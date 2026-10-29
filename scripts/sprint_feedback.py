"""Turn a sprint's grader results into Scott's review page, grades.csv, and a report per student.

Run from the courses hub after the graders have written results:

    python3 ~/courses/product-management/scripts/sprint_feedback.py --sprint 2

Reads   ~/hubs/courses/_data/product-management/grading/sprint-N/results/<net_id>.json
        (one grader result each), the packets beside them, plans/plans.csv (the Plan score, Sprint 2
        on), fairness.md, and the builder profile growth in concepts/growth-<net_id>.json when it
        exists (builder_growth.py writes it; --growth-dir reads it from somewhere else).
Writes  grading/sprint-N/review.html        every student in a rail, each one's instructor report beside it
        grading/sprint-N/grades.csv         the gradebook /publish-grades reads
        grading/sprint-N/feedback/<net_id>.html        the student's report (sprint_report.py)
        grading/sprint-N/feedback/<net_id>-scott.html  the same report with the instructor drawer
        grading/sprint-N/feedback/<net_id>.pdf         the student copy printed, drawers open;
                                                       /publish-grades attaches it (--no-pdf skips)

grades.csv is the one place to change a grade. Its override_* columns, `approved`, and
`scott_note` are kept across reruns; everything else is rebuilt from the results. The final
score for a category is its override when one is set, the grader's score otherwise.

Nothing here touches Canvas. Student data stays in _data. This file holds none.
"""
import argparse, csv, html, json, os, re, secrets, subprocess, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sprint_config import categories, review_points

# PM_DATA points the run at another data folder (used by the API-versus-subagent comparison).
DATA = Path(os.environ.get("PM_DATA") or Path.home() / "hubs/courses/_data/product-management")
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
        return ("Your plan could not be reviewed: your course repo was not shared with Professor Murff."
                if not p.get("repo") else "No plan was found in your repo.")
    if f.get("plan_fields_missing"):
        return f"Your plan, committed {when}, is missing {', '.join(f['plan_fields_missing'])}."
    late = f.get("plan_days_late", 0)
    if late:
        days = f"{late} day{'s' * (late > 1)} after the plan deadline"
        if late >= 10:
            return (f"You committed your plan {when} with Goal, Why this, Done looks like, and Predicted difficulty filled in. That was {days}; "
                    f"under the late work policy, work 10 or more days late earns no credit.")
        return (f"You committed your plan {when} with Goal, Why this, Done looks like, and Predicted difficulty filled in. That was {days}, "
                f"so {10 * late}% came off under the late work policy.")
    return f"You committed your plan {when} with Goal, Why this, Done looks like, and Predicted difficulty filled in. Full credit."


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
            mx = dict((c, m) for c, _l, m in categories(sprint))["demo"]
            r["deductions"] = [d for d in r.get("deductions") or [] if d.get("category") != "demo"] + [{
                "id": "D1", "category": "demo", "points": mx, "rule_id": "demo-not-loom",
                "what": "No Loom demo" if not other else "The demo is not a Loom share link",
                "fix": "Record the demo in Loom and paste its share link into the Wrap-up on Canvas.",
                "reason": r["reasons"]["demo"], "excerpt": None, "excerpt_ref": None}]
        # Adding the TA as a collaborator was dropped as a requirement (2026-09-30).
        r["flags"] = [x for x in r.get("flags", []) if not re.search(r"\bTA\b|nmccaul|collaborator", x)]
        days = p.get("facts", {}).get("canvas_days_late", 0)
        if days:
            r.setdefault("flags", []).insert(0, f"late: Canvas submission {days} day(s) late, "
                                                f"Canvas deducts {min(100, 10 * days)}% automatically")
        out.append((r, p))
    return base, out


NOT_YET_KINDS = {"unproven", "tool_not_product", "after_due", "not_shared", "described_only", "course_given", "before_course"}


def growth_text(G):
    """Every sentence in a growth file that the student reads."""
    if not G:
        return ""
    out = []
    for m in G.get("new") or []:
        out += [m.get("did", ""), m.get("evidence", "")]
    for d in G.get("depth") or []:
        out.append(d.get("why", ""))
    for x in G.get("not_counted") or []:  # what the report shows: no unreadable items, and `why` only for an unknown kind
        if x.get("kind") == "unreadable":
            continue
        out += [x.get("what", "")] + ([] if x.get("kind") in NOT_YET_KINDS else [x.get("why", "")])
    for x in G.get("earlier") or []:
        out += [x.get("did", ""), x.get("evidence", ""), x.get("why", "")]
    return " ".join(str(x) for x in out if x)


def published_rules(sprint):
    """Rule IDs that can cost points in this sprint, from the table in grading/sprint-grader.md."""
    ok = set()
    for line in (Path(__file__).parent / "grading/sprint-grader.md").read_text().splitlines():
        m = re.match(r"\| `([\w-]+)` \|.*\| Sprint (\d+)( only)? \|\s*$", line)
        if m and (sprint == int(m.group(2)) if m.group(3) else sprint >= int(m.group(2))):
            ok.add(m.group(1))
    return ok - {"late", "plan-complete"}  # Canvas and code apply these, never a grader


def check_deductions(r, sprint):
    """Every lost point is one itemized deduction under a published rule (grade disputes, 2026-10-29)."""
    out, n = [], r.get("net_id", "?")
    rules = published_rules(sprint)
    ds = r.get("deductions")
    if ds is None:
        return [f"{n}: no deductions list"]
    ids = [d.get("id") for d in ds]
    if len(ids) != len(set(ids)):
        out.append(f"{n}: repeated deduction ids {ids}")
    for c, _l, mx in CATS:
        if c == "plan":
            continue
        lost = mx - float((r.get("scores") or {}).get(c, 0))
        got = sum(float(d.get("points") or 0) for d in ds if d.get("category") == c)
        if abs(lost - got) > 1e-6:
            out.append(f"{n}: {c} lost {lost:g} but its deductions add up to {got:g}")
    for d in ds:
        if d.get("rule_id") not in rules:
            out.append(f"{n}: deduction {d.get('id')} rests on {d.get('rule_id')!r}, not a published rule for Sprint {sprint}")
        if not d.get("what") or not d.get("fix"):
            out.append(f"{n}: deduction {d.get('id')} needs both what and fix")
    return out


def validate(base, items, growth=None, sprint=0):
    """Stop before building anything a student would read if a result is malformed."""
    growth = growth or {}
    problems = []
    packets = {f.stem for f in base.glob("*.json") if not f.name.startswith(("_", "dispute-"))}  # not the dispute state files
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
                         *((r.get("not_reviewed") or {}).get(k) or "" for k in ("summary", "detail")),
                         r.get("next_sprint") or "",
                         *(f'{d.get("what", "")} {d.get("fix", "")}' for d in r.get("deductions") or []),
                         growth_text(growth.get(n))])
        import re as _re
        # Quoted text is the student's own words or their app's output, so it is not checked.
        plain_text = _re.sub(r"(?<!\w)'.*?'(?!\w)|\"[^\"]*\"|\u2018.*?\u2019(?!\w)|\u201c[^\u201d]*\u201d", " ", text)
        # File paths and the student's own terms ("campaign packet" is a carrier filing) are not our words.
        check_text = _re.sub(r"\S*/\S+|\S+\.(?:md|json|js|ts|py|csv|html)\b|\b(?:(?:10DLC )?campaign|teach) packets?\b|What I am (?:working on|building)|How I will know if it works", " ", plain_text, flags=_re.I)
        # Words a reviewer confirmed name the student's own product (an eval "baseline", a "release
        # packet" builder, an iframe "frame"), listed per student in the result's "voice_ok".
        for w in r.get("voice_ok") or []:
            check_text = _re.sub(rf"\b{_re.escape(w)}s?\b", " ", check_text, flags=_re.I)
        plain_ok = plain_text
        for w in r.get("voice_ok") or []:
            plain_ok = _re.sub(rf"\b{_re.escape(w)}s?\b", " ", plain_ok, flags=_re.I)
        machine = _re.findall(r"\b(frames?|grader|artificial intelligence|it appears (?:that|to)|appears to be|the video shows|"
                              r"session scan|coders?|packet)\b",
                              check_text, _re.I)
        machine += _re.findall(r"(?<!Type )\bI\b(?!-)|\bI'(?:m|ve|d|ll)\b", check_text)  # no first person
        # The baseline survey informs difficulty, but saying so invites students to underrate themselves.
        machine += _re.findall(r"\b(baseline|starting point|where you started|self-rating|self-rated|"
                               r"starting at \d|at \d\.\d+ on|starting where you)\b", plain_ok, _re.I)
        # Mannered prose (grading/student-voice.md): stock figures of speech a literal phrase replaces.
        # A backstop only; the step 3b read catches the rest.
        machine += [f"mannered: {m}" for m in _re.findall(
            r"\b(earns? (?:its|their) keep|moves? the needle|low-hanging fruit|heavy lifting|deep dive|game[- ]changer|"
            r"nail(?:s|ed)? (?:it|the)|shines?|rabbit hole|bread and butter|double-edged|at the end of the day|"
            r"front and center|in the weeds|sweet spot|silver bullet|home run|slam dunk|secret sauce|superpower|"
            r"the real test|tip of the iceberg|hit the ground running|"
            r"dial worth turning|pulls? (?:its|their) weight|carries? the day|lands? (?:well|cleanly|the))\b", check_text, _re.I)]
        if machine:
            problems.append(f"{n}: student feedback reads as machine-written ({', '.join(sorted(set(m.lower() for m in machine)))})")
        # Words that are usually about the student's own project, but worth a look.
        soft = sorted(set(w.lower() for w in _re.findall(
            r"\b(screenshots?|captions?|stills|transcripts?|packets?|the model|the ai|my|me|shipped|shipping)\b",
            plain_text, _re.I)))
        if soft:
            r.setdefault("flags", []).append("voice check: feedback mentions " + ", ".join(soft) +
                                             "; confirm it refers to the student's own work")
        if sprint >= 3:  # itemized deductions start with Sprint 3
            problems += check_deductions(r, sprint)
        if "\u2014" in text:
            problems.append(f"{n}: em dash in student feedback")
        # Scott, 2026-10-29: never "the course can/cannot open"; name who it is (not) shared with (student-voice.md).
        req = " ".join(q.get("title", "") + " " + q.get("body", "") for q in (p.get("facts") or {}).get("share_requests") or [])
        if _re.search(r"\bthe course (?:can|cannot|could|can't|couldn't)\b|\b(?:with|to) the course\b", text + " " + req, _re.I):
            problems.append(f"{n}: says 'the course can/cannot'; name who it is shared with (Professor Murff, GitHub sdmurff)")
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


def review_page(base, items, rows, sprint, points, plans, growth, fairness):
    """Scott's review page: a rail of every student, and each one's instructor report beside it."""
    import sprint_review_shell
    out = base / "review.html"
    out.write_text(sprint_review_shell.render(items, rows, sprint, plans, growth, fairness, points))
    out.chmod(0o600)


def load_growth(sprint, net_ids, growth_dir=None):
    """Builder profile growth per student, or nothing when builder_growth.py has not run for them."""
    d = Path(growth_dir) if growth_dir else DATA / f"grading/sprint-{sprint}/concepts"
    out = {}
    for n in net_ids:
        f = d / f"growth-{n}.json"
        if f.exists():
            G = json.loads(f.read_text())
            if "rings" in G and "new" in G:  # the 0-to-100 shape; an older pilot file is ignored
                out[n] = G
    return out


def side_inputs(base):
    """The Plan scores, each student's course-skill status, and the fairness findings."""
    plans = base / "plans/plans.csv"
    plans = {r["net_id"]: r for r in csv.DictReader(open(plans))} if plans.exists() else {}
    roster = DATA / "github-roster.csv"
    # "OLD" or "missing" when either course skill is out of date (sprint-review gained a version
    # marker on 2026-10-16), so the report's update step fires for either.
    worst = lambda r: next((v for v in ("missing", "OLD") if v in (r.get("sprint_plan_skill", ""), r.get("sprint_review_skill", ""))), "new")
    skills = ({r["net_id"]: worst(r) for r in csv.DictReader(open(roster))}
              if roster.exists() else {})
    fair = base / "fairness.md"
    fairness = {}
    if fair.exists():
        for line in fair.read_text().splitlines():
            m = re.match(r"- (\w+) \| (.*)", line)
            if m:
                fairness.setdefault(m.group(1), []).append(m.group(2))
    return plans, skills, fairness


def dispute_inputs(base, sprint, net_ids):
    """Each student's dispute link token (kept across rebuilds, so a posted report's link keeps working),
    the window's close date, and the outcomes /resolve-dispute has recorded. Sprint 3 on."""
    if sprint < 3:
        return {}, None, {}
    f = base / "dispute-tokens.json"
    tokens = json.loads(f.read_text()) if f.exists() else {}
    new = [n for n in net_ids if n not in tokens]
    for n in new:
        tokens[n] = secrets.token_urlsafe(32)
    if new or not f.exists():
        f.write_text(json.dumps(tokens, indent=1))
    f.chmod(0o600)
    w = base / "dispute-window.json"
    closes = None
    if w.exists():
        c = json.loads(w.read_text()).get("closes")
        if c:
            d = dt.datetime.fromisoformat(c)
            closes = f"{d:%b} {d.day}"
    o = base / "dispute-outcomes.json"
    return tokens, closes, (json.loads(o.read_text()) if o.exists() else {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--no-pdf", action="store_true", help="skip the PDFs /publish-grades attaches")
    ap.add_argument("--growth-dir", help="read growth-<net_id>.json from here instead of sprint-N/concepts")
    a = ap.parse_args()
    global CATS
    CATS = categories(a.sprint)
    base, items = load(a.sprint)
    if not items:
        sys.exit(f"no results in {base / 'results'}")
    points = review_points(a.sprint)
    growth = load_growth(a.sprint, [r["net_id"] for r, _ in items], a.growth_dir)
    validate(base, items, growth, a.sprint)
    rows = write_csv(base, items)
    plans, skills, fairness = side_inputs(base)
    tokens, closes, outcomes = dispute_inputs(base, a.sprint, [r["net_id"] for r, _ in items])
    from sprint_report import render
    fb = base / "feedback"
    fb.mkdir(exist_ok=True)
    for r, p in items:
        n = r["net_id"]
        kw = dict(plan_row=plans.get(n), growth=growth.get(n), skills_status=skills.get(n, ""),
                  dispute={"token": tokens[n], "closes": closes} if n in tokens else None, outcomes=outcomes.get(n))
        page = fb / f"{n}.html"
        page.write_text(render(r, p, rows[n], a.sprint, CATS, final, **kw))
        mine = fb / f"{n}-scott.html"
        mine.write_text(render(r, p, rows[n], a.sprint, CATS, final, scott=True, fairness=fairness.get(n, []), **kw))
        for x in (page, mine):
            x.chmod(0o600)
        if not a.no_pdf:
            pdf = page.with_suffix(".pdf")
            subprocess.run(["weasyprint", "-q", str(page), str(pdf)], check=True)
            pdf.chmod(0o600)
    review_page(base, items, rows, a.sprint, points, plans, growth, fairness)
    low = sum(1 for r, _ in items if r.get("confidence") == "low")
    watch = sum(1 for r, _ in items if r.get("watch_loom"))
    print(f"{len(items)} graded, {low} low confidence, {watch} Looms to watch, "
          f"{len(growth)} with a builder profile")
    print(f"  {base / 'review.html'}\n  {base / 'grades.csv'}\n  {fb}/  (<net_id>.html student, <net_id>-scott.html yours)")


if __name__ == "__main__":
    main()
