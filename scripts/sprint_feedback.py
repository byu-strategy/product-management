"""Turn a sprint's grader results into Scott's review page, grades.csv, and a feedback page per student.

Run from the courses hub after the graders have written results:

    python3 ~/courses/product-management/scripts/sprint_feedback.py --sprint 1

Reads   ~/hubs/courses/_data/product-management/grading/sprint-N/results/<net_id>.json
        (one grader result each) and the packets beside them.
Writes  grading/sprint-N/review.html        every student, sortable, with evidence and frames
        grading/sprint-N/grades.csv         the gradebook /publish-grades reads
        grading/sprint-N/feedback/<net_id>.html and .pdf   what the student receives

grades.csv is the one place to change a grade. Its override_* columns, `approved`, and
`scott_note` are kept across reruns; everything else is rebuilt from the results. The final
score for a category is its override when one is set, the grader's score otherwise.

Nothing here touches Canvas. Student data stays in _data. This file holds none.
"""
import argparse, csv, html, json, subprocess, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sprint_config import categories, review_points

DATA = Path.home() / "hubs/courses/_data/product-management"
CATS = []  # set in main() from sprint_config: Sprint 1 includes the plan, later sprints do not
KEEP = ["override_plan", "override_shipped", "override_review", "override_demo",
        "approved", "scott_note"]
COLS = (["net_id", "name", "preferred_first", "canvas_user_id", "confidence", "watch_loom",
         "plan", "shipped", "review", "demo", "grader_total"] + KEEP +
        ["final_total", "flags", "loom", "repo"])
e = html.escape


def final(row, cat):
    o = str(row.get(f"override_{cat}", "")).strip()
    return float(o) if o else float(row[cat])


def fmt(x):
    return f"{x:g}"


def plan_line(p):
    """Sprint 1's plan category, from the completion facts the packet computed."""
    f, sub = p.get("facts", {}), p.get("plan_submission") or {}
    when = sub.get("submitted_at")
    when = dt.datetime.fromisoformat(when).strftime("%b %-d at %-I:%M %p") if when else None
    if not f.get("plan_submitted"):
        return "No plan was found."
    if f.get("plan_fields_missing"):
        return f"Your plan, committed {when}, is missing: {', '.join(f['plan_fields_missing'])}."
    late = f.get("plan_days_late", 0)
    if late:
        return (f"Committed {when} with all four fields filled in, {late} day{'s' * (late > 1)} after "
                f"the plan deadline, so {late} point{'s' * (late > 1)} came off under the late work policy.")
    return f"Committed {when} with all four fields filled in. Graded for completion."


def load(sprint):
    base = DATA / f"grading/sprint-{sprint}"
    out = []
    for f in sorted((base / "results").glob("*.json")):
        r = json.loads(f.read_text())
        pk = base / f"{r['net_id']}.json"
        p = json.loads(pk.read_text()) if pk.exists() else {}
        if sprint == 1:  # the plan is inside Sprint 1's one assignment; its score is computed, not graded
            r["scores"]["plan"] = p.get("facts", {}).get("plan_score", 0)
            r["reasons"]["plan"] = r["feedback"]["plan"] = plan_line(p)
            if p.get("facts", {}).get("plan_submitted") and not p["facts"].get("plan_on_time"):
                r.setdefault("flags", []).insert(0, "late: plan committed after Sep 16, 11:59 PM")
        # Loom only, from Sprint 2 on: any other demo scores 0, set here so no grader can soften it.
        if sprint >= 2 and not p.get("facts", {}).get("demo_is_loom"):
            other = p.get("facts", {}).get("non_loom_video")
            r["scores"]["demo"] = 0
            r["feedback"]["demo"] = (
                "Your demo was not a Loom share link, so Demo is 0. The demo must be on Loom."
                if other else "No Loom demo was submitted, so Demo is 0.")
            r["reasons"]["demo"] = "Not a Loom link (" + (", ".join(other) or "no video") + "): 0 by rule."
        days = p.get("facts", {}).get("canvas_days_late", 0)
        if days:
            r.setdefault("flags", []).insert(0, f"late: Canvas submission {days} day(s) late, "
                                                f"Canvas deducts {min(100, 10 * days)}% automatically")
        out.append((r, p))
    return base, out


def validate(base, items):
    """Stop before building anything a student would read if a result is malformed."""
    problems = []
    packets = {f.stem for f in base.glob("*.json")}
    for r, p in items:
        n = r.get("net_id", "?")
        for c, _, mx in CATS:
            s = (r.get("scores") or {}).get(c)
            if not isinstance(s, (int, float)) or not 0 <= s <= mx:
                problems.append(f"{n}: {c} score {s!r} outside 0-{mx}")
            if not (r.get("feedback") or {}).get(c):
                problems.append(f"{n}: no student feedback for {c}")
        graded = {c for c, _, _ in CATS if c != "plan"}  # the plan line is written by this script
        text = " ".join([*(v for k, v in (r.get("feedback") or {}).items() if k in graded),
                         r.get("review_missed") or "",
                         r.get("next_sprint") or ""])
        import re as _re
        machine = _re.findall(r"\b(frames?|screenshots?|stills|transcripts?|captions?|packets?|grader|"
                              r"the model|artificial intelligence|the ai|it appears|the video shows)\b",
                              text, _re.I)
        if machine:
            problems.append(f"{n}: student feedback reads as machine-written ({', '.join(sorted(set(m.lower() for m in machine)))})")
        if "\u2014" in text:
            problems.append(f"{n}: em dash in student feedback")
        if any(w in text.lower() for w in (" late", "after the deadline", "after due", "seconds after")):
            problems.append(f"{n}: student feedback mentions lateness")
    missing = packets - {r["net_id"] for r, _ in items}
    if missing:
        print(f"{len(missing)} packets have no result yet: {', '.join(sorted(missing))}")
    if problems:
        sys.exit("fix these results first:\n  " + "\n  ".join(problems))


def write_csv(base, items):
    path, old = base / "grades.csv", {}
    if path.exists():
        old = {r["net_id"]: r for r in csv.DictReader(open(path))}
    rows = []
    for r, p in items:
        row = {"net_id": r["net_id"], "name": p.get("name", ""),
               "preferred_first": p.get("preferred_first", ""),
               "canvas_user_id": p.get("canvas_user_id", ""),
               "confidence": r.get("confidence", ""), "watch_loom": r.get("watch_loom", False),
               **{c: r["scores"][c] for c, _, _ in CATS}, "grader_total": sum(r["scores"].values()),
               **{k: old.get(r["net_id"], {}).get(k, "") for k in KEEP},
               "flags": " | ".join(r.get("flags", [])),
               "loom": (p.get("loom") or {}).get("url", ""), "repo": p.get("repo") or ""}
        row["final_total"] = fmt(sum(final(row, c) for c, _, _ in CATS))
        rows.append(row)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)
    path.chmod(0o600)
    return {r["net_id"]: r for r in rows}


STUDENT_CSS = """
body{font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1d2330;max-width:720px;margin:32px auto;padding:0 20px}
h1{font-size:22px;margin:0 0 4px}.sub{color:#5b6475;margin:0 0 24px}
table{border-collapse:collapse;width:100%;margin:8px 0 24px}
th,td{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid #e3e6ec}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#5b6475}
td.pts{white-space:nowrap;font-weight:600;width:70px}
h2{font-size:15px;margin:22px 0 6px}p{margin:0 0 10px}
.total{font-size:28px;font-weight:700}
"""


def student_page(r, p, row, sprint, points):
    total = sum(final(row, c) for c, _, _ in CATS)
    trs = "".join(
        f"<tr><td>{label}</td><td class=pts>{fmt(final(row, c))}/{mx}</td>"
        f"<td>{e(r['feedback'][c])}</td></tr>" for c, label, mx in CATS)
    extra = ""
    if r.get("review_missed"):
        extra += f"<h2>What your sprint review found that your retro did not mention</h2><p>{e(r['review_missed'])}</p>"
    if r.get("next_sprint"):
        extra += f"<h2>For next sprint</h2><p>{e(r['next_sprint'])}</p>"
    days = p.get("facts", {}).get("canvas_days_late", 0)
    if days:
        pct = min(100, 10 * days)
        extra = (f"<h2>Late work</h2><p>This was submitted {days} day{'s' * (days > 1)} late. Canvas "
                 f"applies the late work policy on top of the score above: minus {pct}%, so your "
                 f"Canvas grade is {fmt(round(total * (1 - pct / 100), 1))} / {points}.</p>") + extra
    f = p.get("facts", {})
    if sprint == 1 and not f.get("demo_is_loom") and f.get("non_loom_video"):
        extra += ("<h2>Use Loom from Sprint 2 on</h2><p>Your demo was not a Loom share link. That cost "
                  "nothing in Sprint 1. From Sprint 2 on, the demo must be a Loom share link, and a demo "
                  "anywhere else, or none, scores 0.</p>")
    if sprint == 1 and p.get("repo"):
        open_items = []
        if f.get("readme_context_filled") is False:
            open_items.append("fill in the context declaration in your README (your role, what you "
                              "are working on, who it is for, and who uses your work)")
        if f.get("ta_is_collaborator") is False:
            open_items.append("add Nate (nmccaul) as a collaborator on your repo")
        if open_items:
            extra += ("<h2>Sprint 1 setup, still open</h2><p>Please " + " and ".join(open_items) +
                      " before Sprint 2 is due. No points were taken for this.</p>")
    note = row.get("scott_note", "").strip()
    if note:
        extra += f"<h2>From Professor Murff</h2><p>{e(note)}</p>"
    return f"""<!doctype html><html><head><meta charset=utf-8><title>Sprint {sprint} feedback</title>
<style>{STUDENT_CSS}</style></head><body>
<h1>Sprint {sprint} feedback, {e(p.get('preferred_first') or p.get('name', ''))}</h1>
<p class=sub>MSB 341 Product Management</p>
<p class=total>{fmt(total)} / {points}</p>
<table><tr><th>Category</th><th>Score</th><th>What it was based on</th></tr>{trs}</table>
{extra}</body></html>"""


def review_page(base, items, rows, sprint, points):
    """Scott's grading dossier: every student, their scores, and the evidence behind them."""
    from sprint_dossier import render
    (base / "review.html").write_text(render(base, items, rows, sprint, points, CATS, final))
    (base / "review.html").chmod(0o600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    global CATS
    CATS = categories(a.sprint)
    base, items = load(a.sprint)
    if not items:
        sys.exit(f"no results in {base / 'results'}")
    points = review_points(a.sprint)
    validate(base, items)
    rows = write_csv(base, items)
    fb = base / "feedback"
    fb.mkdir(exist_ok=True)
    for r, p in items:
        page = fb / f"{r['net_id']}.html"
        page.write_text(student_page(r, p, rows[r["net_id"]], a.sprint, points))
        page.chmod(0o600)
        if not a.no_pdf:
            pdf = page.with_suffix(".pdf")
            subprocess.run(["weasyprint", "-q", str(page), str(pdf)], check=True)
            pdf.chmod(0o600)
    review_page(base, items, rows, a.sprint, points)
    low = sum(1 for r, _ in items if r.get("confidence") == "low")
    watch = sum(1 for r, _ in items if r.get("watch_loom"))
    print(f"{len(items)} graded, {low} low confidence, {watch} Looms to watch")
    print(f"  {base / 'review.html'}\n  {base / 'grades.csv'}\n  {fb}/")


if __name__ == "__main__":
    main()
