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
import argparse, csv, html, json, re, subprocess, sys, datetime as dt
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


# Same axis order, orientation, and colors as the builder profile charts students received.
AXES = ["Discovery", "Design", "Application Architecture", "AI Systems", "Agentic Workflow", "Launch and Learn"]
SHORT = [["Discovery"], ["Design"], ["Application", "Architecture"], ["AI Systems"], ["Agentic", "Workflow"],
         ["Launch", "and Learn"]]
ACCENT, GRID, INK, MUTED = "#4f46e5", "#d5d5df", "#1f1f24", "#6b6b76"


EFFORT = "#d97706"  # amber: validated against the profile indigo for colorblind separation


def hexagon(shares, profile=None):
    """The student's builder profile (their baseline self-rating, 1 to 5) as a line, with each
    axis's wedge shaded by the share of this sprint's effort that went there. Distance from the
    center means only skill; effort is the shading, so the two never share a scale."""
    import math
    cx, cy, R = 260, 170, 112
    ang = [math.pi / 2 - i * 2 * math.pi / 6 for i in range(6)]
    pt = lambda r, a: (cx + r * math.cos(a), cy - r * math.sin(a))
    vals = [max(0.0, min(1.0, float(shares.get(ax, 0)))) for ax in AXES]
    wedges = ""
    verts = [pt(R, a) for a in ang]
    for i, v in enumerate(vals):
        if v > 0:  # the axis's slice of the hexagon: center, half-edge, vertex, half-edge
            prev, nxt, vx = verts[i - 1], verts[(i + 1) % 6], verts[i]
            m1 = ((prev[0] + vx[0]) / 2, (prev[1] + vx[1]) / 2)
            m2 = ((nxt[0] + vx[0]) / 2, (nxt[1] + vx[1]) / 2)
            wedges += (f'<polygon points="{cx},{cy} {m1[0]:.1f},{m1[1]:.1f} {vx[0]:.1f},{vx[1]:.1f} '
                       f'{m2[0]:.1f},{m2[1]:.1f}" fill="{EFFORT}" fill-opacity="{0.10 + 0.55 * v:.2f}"/>')
    grid = "".join(
        f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(R * k / 5, a) for a in ang))}" '
        f'fill="none" stroke="{GRID}" stroke-width="{1.2 if k == 5 else 0.8}"/>' for k in range(1, 6))
    spokes = "".join(f'<line x1="{cx}" y1="{cy}" x2="{pt(R, a)[0]:.1f}" y2="{pt(R, a)[1]:.1f}" '
                     f'stroke="{GRID}" stroke-width="0.8"/>' for a in ang)
    line = ""
    if profile:
        pv = [max(0.0, min(5.0, float(profile.get(ax, 0)))) for ax in AXES]
        pts = [pt(R * v / 5, a) for v, a in zip(pv, ang)]
        line = (f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{ACCENT}" '
                f'fill-opacity="0.08" stroke="{ACCENT}" stroke-width="2" stroke-linejoin="round"/>'
                + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{ACCENT}"/>' for x, y in pts))
    labels = ""
    for ax, lines, v, a in zip(AXES, SHORT, vals, ang):
        x, y = pt(R + 22, a)
        anchor = "middle" if abs(math.cos(a)) < 0.2 else ("start" if math.cos(a) > 0 else "end")
        y0 = y - (len(lines) - 1) * 7 + (4 if math.sin(a) < -0.2 else (-6 if math.sin(a) > 0.9 else 0))
        tsp = "".join(f'<tspan x="{x:.1f}" dy="{0 if i == 0 else 14}">{html.escape(l)}</tspan>' for i, l in enumerate(lines))
        sub = []
        if profile and ax in profile:
            sub.append(f"profile {float(profile[ax]):.1f}")
        if v > 0:
            sub.append(f"{round(v * 100)}% of sprint")
        labels += (f'<text x="{x:.1f}" y="{y0:.1f}" text-anchor="{anchor}" font-size="11.5" '
                   f'font-weight="{600 if v > 0 else 400}" fill="{INK if v > 0 else MUTED}">{tsp}'
                   f'<tspan x="{x:.1f}" dy="14" font-size="10.5" fill="{MUTED}" font-weight="400">'
                   f'{" &#183; ".join(sub)}</tspan></text>')
    legend = (f'<g font-size="10.5" fill="{MUTED}"><rect x="90" y="352" width="14" height="10" fill="{EFFORT}" '
              f'fill-opacity="0.45"/><text x="110" y="361">Where this sprint\'s effort went</text>'
              + (f'<line x1="280" y1="357" x2="296" y2="357" stroke="{ACCENT}" stroke-width="2"/>'
                 f'<text x="302" y="361">Your builder profile, 1 to 5</text>' if profile else "") + "</g>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 372" width="520" height="372" role="img" '
            f'aria-label="Builder profile with this sprint\'s effort shaded by axis">{wedges}{grid}{spokes}{line}'
            f'{labels}{legend}</svg>')


def focus_caption(shares):
    ranked = sorted(((s, a) for a, s in shares.items() if a in AXES and s > 0), reverse=True)
    if not ranked:
        return ""
    lead = f"This sprint's effort went mostly to {ranked[0][1]} ({round(ranked[0][0] * 100)}%)"
    rest = [f"{a} ({round(s * 100)}%)" for s, a in ranked[1:]]
    if rest:
        lead += ", with " + (rest[0] if len(rest) == 1 else ", ".join(rest[:-1]) + " and " + rest[-1])
    lead += "."
    return lead


def plan_line(p):
    """Sprint 1's plan category, from the completion facts the packet computed."""
    f, sub = p.get("facts", {}), p.get("plan_submission") or {}
    when = sub.get("submitted_at")
    when = dt.datetime.fromisoformat(when).strftime("%b %-d at %-I:%M %p") if when else None
    if not f.get("plan_submitted"):
        return "No plan was found in your repo."
    if f.get("plan_fields_missing"):
        return f"Your plan, committed {when}, is missing {', '.join(f['plan_fields_missing'])}."
    late = f.get("plan_days_late", 0)
    if late:
        return (f"You committed your plan {when} with all four fields filled in. That was {late} "
                f"day{'s' * (late > 1)} after the plan deadline, so {late} point{'s' * (late > 1)} "
                f"came off under the late work policy.")
    return f"You committed your plan {when} with all four fields filled in. Full credit."


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
                "Your demo was not a Loom share link. The demo has to be on Loom, so Demo is 0."
                if other else "No Loom demo was submitted, so Demo is 0.")
            r["reasons"]["demo"] = "Not a Loom link (" + (", ".join(other) or "no video") + "): 0 by rule."
        # Adding the TA as a collaborator was dropped as a requirement (2026-09-30).
        r["flags"] = [x for x in r.get("flags", []) if not re.search(r"\bTA\b|nmccaul|collaborator", x)]
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
                         (r.get("difficulty") or {}).get("note") or "",
                         r.get("next_sprint") or ""])
        import re as _re
        # Quoted text is the student's own words or their app's output, so it is not checked.
        plain_text = _re.sub(r"'[^']*'|\"[^\"]*\"|\u2018[^\u2019]*\u2019|\u201c[^\u201d]*\u201d", " ", text)
        machine = _re.findall(r"\b(frames?|grader|artificial intelligence|it appears|the video shows)\b",
                              plain_text, _re.I)
        machine += _re.findall(r"(?<!Type )\bI\b(?!-)|\bI'(?:m|ve|d|ll)\b", plain_text)  # no first person
        if machine:
            problems.append(f"{n}: student feedback reads as machine-written ({', '.join(sorted(set(m.lower() for m in machine)))})")
        # Words that are usually about the student's own project, but worth a look.
        soft = sorted(set(w.lower() for w in _re.findall(
            r"\b(screenshots?|captions?|stills|transcripts?|packets?|the model|the ai|my|me)\b", plain_text, _re.I)))
        if soft:
            r.setdefault("flags", []).append("voice check: feedback mentions " + ", ".join(soft) +
                                             "; confirm it refers to the student's own work")
        if "\u2014" in text:
            problems.append(f"{n}: em dash in student feedback")
        if _re.search(r"\b(submitted|committed|turned in|pushed)\b[^.]{0,40}\blate\b|\blate (submission|penalty|work)\b|"
                      r"\bafter the (deadline|due date)\b|\bpast the deadline\b|\bseconds after\b|\bafter due\b",
                      plain_text, _re.I):
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
.disclaimer{margin-top:28px;padding-top:10px;border-top:1px solid #e3e6ec;font-size:12px;color:#5b6475}
.hex{text-align:center;margin:4px 0 6px}.hex svg{max-width:100%;height:auto}
h2{font-size:15px;margin:22px 0 6px}p{margin:0 0 10px}
.total{font-size:28px;font-weight:700}
"""


def student_page(r, p, row, sprint, points):
    total = sum(final(row, c) for c, _, _ in CATS)
    trs = "".join(
        f"<tr><td>{label}</td><td class=pts>{fmt(final(row, c))}/{mx}</td>"
        f"<td>{e(r['feedback'][c])}</td></tr>" for c, label, mx in CATS)
    extra = ""
    shares = r.get("axes") or {}
    if shares:
        profile = p.get("baseline")
        note = (" The line is your builder profile from the September baseline survey, your own 1 to 5 "
                "rating on each axis.") if profile else ""
        extra = (f"<h2>Where this sprint landed</h2><div class=hex>{hexagon(shares, profile)}</div>"
                 f"<p>{e(focus_caption(shares))}{e(note)}</p>") + extra
    if (r.get("difficulty") or {}).get("note"):
        extra += f"<h2>How hard it was</h2><p>{e(r['difficulty']['note'])}</p>"
    if r.get("next_sprint"):
        extra += f"<h2>Something to consider for next sprint</h2><p>{e(r['next_sprint'])}</p>"
    days = p.get("facts", {}).get("canvas_days_late", 0)
    if days:
        pct = min(100, 10 * days)
        extra = (f"<h2>Late work</h2><p>You submitted this {days} day{'s' * (days > 1)} late. Under the "
                 f"late work policy Canvas takes {pct}% off the score above, so your Canvas grade is "
                 f"{fmt(round(total * (1 - pct / 100), 1))} / {points}.</p>") + extra
    f = p.get("facts", {})
    if sprint == 1 and not f.get("demo_is_loom") and f.get("non_loom_video"):
        extra += ("<h2>Use Loom from Sprint 2 on</h2><p>Your demo was not on Loom. That cost nothing "
                  "in Sprint 1. From Sprint 2 on, the demo has to be a Loom share "
                  "link, and a demo anywhere else, or none, scores 0.</p>")
    if sprint == 1 and p.get("repo"):
        open_items = []
        if f.get("readme_context_filled") is False:
            open_items.append("fill in the context declaration in your README (your role, what you "
                              "are working on, who it is for, and who uses your work)")
        if open_items:
            extra += ("<h2>Sprint 1 setup, still open</h2><p>Please " + " and ".join(open_items) +
                      " before Sprint 2 is due. No points were taken off for this.</p>")
    note = row.get("scott_note", "").strip()
    if note:
        extra += f"<h2>From Professor Murff</h2><p>{e(note)}</p>"
    return f"""<!doctype html><html><head><meta charset=utf-8><title>Sprint {sprint} feedback</title>
<style>{STUDENT_CSS}</style></head><body>
<h1>Sprint {sprint} feedback, {e(p.get('preferred_first') or p.get('name', ''))}</h1>
<p class=sub>MSB 341 Product Management</p>
<p class=total>{fmt(total)} / {points}</p>
<table><tr><th>Category</th><th>Score</th><th>What it was based on</th></tr>{trs}</table>
{extra}
<p class=disclaimer>This sprint feedback was generated with the assistance of Claude Code by reviewing
everything you turned in. If you believe something is incorrect or does not accurately represent
your work, please let Nate, the TA, know.</p></body></html>"""


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
