#!/usr/bin/env python3
"""A fully working Sprint 3 report for a fictional student, for demos in class (Scott, 2026-11-02).

Jordan Rivera and ShiftSwap are the test fixture (tests/fixtures/sample-student), moved forward to
Sprint 3: dates +14 days (same weekdays), sprint numbers +1, a small Sprint 1 ring added, and three
deductions (one Output, two Report and retro) so there is something to dispute. The report is built by
the real template (sprint_report.render), so it is the report students got, feature for feature.

Its Dispute buttons and "How useful is this report?" form work against the live Strategy app. The demo
link lives under course "msb341-demo", net_id "demo-jrivera", so it never mixes with MSB 341's records
(sprint_records, `disputes.py window`), though its disputes do show on Grade disputes (/app/admin/disputes),
which lets the triage side be shown too. Replies go to scott.murff@byu.edu.

    python3 demo_report.py build       build the report and sync the demo link and deductions
    python3 demo_report.py status      what the demo link holds now: disputes and feedback
    python3 demo_report.py resolve R1 restore|keep [--note "..."]   decide one dispute, rebuild the report
    python3 demo_report.py reset       delete demo disputes, evidence and feedback; rebuild clean

The token and the built report stay in ~/hubs/courses/_data/product-management/grading/demo/, not in git.
"""
import argparse, copy, datetime as dt, hashlib, json, re, secrets, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "grading"))
from canvas_due import due  # noqa: E402
from sprint_config import categories  # noqa: E402

FX = HERE / "tests/fixtures/sample-student"
OUT = Path.home() / "hubs/courses/_data/product-management/grading/demo"
SPRINT, COURSE, NET = 3, "msb341-demo", "demo-jrivera"
EMAIL = "scott.murff@byu.edu"
# Shown in the report as the real Sprint 3 window; the database keeps the demo open through the semester.
SHOWN = {"opens": "Fri, Oct 30", "closes": "Fri, Nov 6"}
OPEN_UNTIL = "2026-12-18"
CATS = categories(SPRINT)
LABEL = {"shipped": "Output", "review": "Report and retro", "demo": "Demo", "plan": "Plan"}
CAT_KEY = {v: k for k, v in LABEL.items()}

# ---------------------------------------------------------------- fixture -> Sprint 3

MON = {"Sep": 9, "Oct": 10, "Nov": 11}
MNAME = {9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
SHIFT = dt.timedelta(days=14)


def shift_text(s):
    def iso(m):
        d = dt.date(2026, int(m.group(1)), int(m.group(2))) + SHIFT
        return f"2026-{d:%m}-{d:%d}"

    def compact(m):
        d = dt.date(2026, int(m.group(1)), int(m.group(2))) + SHIFT
        return f"2026{d:%m}{d:%d}"

    def short(m):
        d = dt.date(2026, MON[m.group(1)], int(m.group(2))) + SHIFT
        return f"{MNAME[d.month]} {d.day}"

    s = re.sub(r"2026-(\d\d)-(\d\d)", iso, s)
    s = re.sub(r"2026(\d\d)(\d\d)(?=\d{6})", compact, s)
    s = re.sub(r"\b(Sep|Oct|Nov) (\d{1,2})\b", short, s)
    return re.sub(r"\b([Ss]print[-_ ]?)([1-5])\b", lambda m: f"{m.group(1)}{int(m.group(2)) + 1}", s)


def walk(x, skip=()):
    if isinstance(x, str):
        return shift_text(x)
    if isinstance(x, list):
        return [walk(v, skip) for v in x]
    if isinstance(x, dict):
        return {k: (v if k in skip else walk(v, skip)) for k, v in x.items()}
    return x


def load_fixture():
    L = lambda n: json.loads((FX / n).read_text())
    r, p, G, row, plan = L("result.json"), L("packet.json"), L("growth.json"), L("grades_row.json"), L("plan_row.json")
    r, p, row, plan = walk(r), walk(p), walk(row), walk(plan)
    G = walk(G, skip=("exams",))  # the midterm was Fri 10/23, inside Sprint 3 already
    for x in (r, p, G, row, plan):
        x["net_id"] = NET
    p["window_end"] = "2026-10-26T23:59:59-06:00"
    p["after_window"] = None

    # ---- growth: renumber the rings, add a small Sprint 1 ring before them
    G["sprint"] = SPRINT
    for ring in G["rings"]:
        ring["sprint"] += 1
    for x in G.get("earlier") or []:
        x["sprint"] += 1
    s1 = [("DI01", "Problem interviews (the Mom Test)", "2026-09-22",
           "You interviewed three library desk workers about the last time a shift fell through, and wrote down what each one did next.",
           "sprints/interviews.md: three interviews dated Sep 21 and 22", "3c1d9a7"),
          ("DI04", "Problem statement and the stranger test", "2026-09-24",
           "Your problem statement names student desk workers, a shift they cannot cover, and the group text that goes unanswered, with no product in it.",
           "README Problem section", "7be2f10")]
    G["earlier"] = [{"sprint": 1, "concept": c, "name": n, "axis": "Discovery", "points": 1.3, "when": w,
                     "did": d, "evidence": ev, "ref": ref} for c, n, w, d, ev, ref in s1] + \
        [{"sprint": 1, "depth": True, "axis": "Discovery", "level": 1, "name": "Followed", "points": 0.0,
          "why": "You ran the interviews from the book's question list and summarized them, before choosing what to build."}] + \
        (G.get("earlier") or [])
    G["rings"].insert(0, {"sprint": 1, "coded": True, "breadth": {"Discovery": ["DI01", "DI04"]},
                          "depth": {"Discovery": {"from": 0, "to": 1}}, "points": {"Discovery": 2.6}})
    for ring in G["rings"][1:]:
        if "Discovery" in (ring.get("depth") or {}):
            ring["depth"]["Discovery"]["from"] = max(1, ring["depth"]["Discovery"]["from"])
    G["practice_total"]["Discovery"] = round(G["practice_total"].get("Discovery", 0) + 2.6, 2)
    G["concepts_shown"] = sorted(set(G["concepts_shown"]) | {"DI01", "DI04"})

    # ---- scores and deductions: Output 18, Retro 8, Demo 10 = 36 of 40
    r["scores"] = {"shipped": 18, "review": 8, "demo": 10}
    r["feedback"]["shipped"] = (
        "Your plan's items are there: post, pick-up and approval working on the live app, the photo reader returning an "
        "editable draft with undo in c94d1b0, and the rebuilt UI with its empty and error states. The seven interviews, five "
        "briefs and ranking are named in commits b47c0d2 and f7e3c19, but the notes themselves are not in your repo.")
    r["deductions"] = [
        {"id": "O1", "category": "shipped", "points": 2, "rule_id": "out-checkable",
         "what": "Interview notes, briefs and ranking are not in the repo",
         "fix": "Commit the notes to sprints/discovery/, or share the document with Professor Murff (GitHub sdmurff) and link it from your plan.",
         "reason": "Commits b47c0d2 and f7e3c19 name seven interviews, five briefs and a ranking; sprints/discovery/ holds no text for them.",
         "excerpt": None, "excerpt_ref": None},
    ] + [d for d in r["deductions"] if d["category"] == "review"]
    for c in ("shipped", "review", "demo"):
        row[c] = str(r["scores"][c])
        row[f"override_{c}"] = ""
    row["grader_total"] = row["final_total"] = str(sum(r["scores"].values()))
    return r, p, G, row, plan


# ---------------------------------------------------------------- state

def token():
    OUT.mkdir(parents=True, exist_ok=True)
    OUT.chmod(0o700)
    f = OUT / "token.txt"
    if not f.exists():
        f.write_text(secrets.token_urlsafe(32))
        f.chmod(0o600)
    return f.read_text().strip()


def outcomes():
    f = OUT / "outcomes.json"
    return json.loads(f.read_text()) if f.exists() else {}


def db():
    from disputes import DB
    return DB()


def link_row(d):
    rows = d.get("grade_dispute_links", course=f"eq.{COURSE}", sprint=f"eq.{SPRINT}", net_id=f"eq.{NET}",
                 select="id,feedback_rating,feedback_text,feedback_at")
    return rows[0] if rows else None


# ---------------------------------------------------------------- commands

def build(sync=True):
    from sprint_feedback import final
    from sprint_report import render, RULE_TEXT, RULE_SRC
    r, p, G, row, plan = load_fixture()
    oc = outcomes()
    for key, o in oc.items():  # a decided dispute changes the score the way /resolve-dispute's override does
        d = next(x for x in r["deductions"] if x["id"] == key)
        if o.get("points_changed"):
            c = d["category"]
            mx = dict((k, m) for k, _l, m in CATS)[c]
            row[f"override_{c}"] = f"{min(mx, max(0.0, final(row, c) + o['points_changed'])):g}"
    tok = token()
    dispute = {"token": tok, "closes": SHOWN}
    html = render(r, p, row, SPRINT, CATS, final, plan_row=plan, growth=G, skills_status="",
                  dispute=dispute, outcomes=oc or None)
    out = OUT / "sprint-3-report-demo.html"
    out.write_text(html)
    score = sum(final(row, c) for c, _l, _m in CATS)
    print(f"built {out}  ({score:g} of 40)")
    if not sync:
        return
    d = db()
    link = d.upsert("grade_dispute_links", [{
        "token_hash": hashlib.sha256(tok.encode()).hexdigest(), "course": COURSE, "sprint": SPRINT, "net_id": NET,
        "student_name": p["name"], "first_name": p.get("preferred_first") or "Jordan", "email": EMAIL,
        "review_score": score, "review_max": 40, "closes_at": due(OPEN_UNTIL),
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat()}], "course,sprint,net_id")[0]
    have = d.get("grade_deductions", link_id=f"eq.{link['id']}", select="id,ded_key,grade_disputes(id)")
    locked = {x["ded_key"] for x in have if x.get("grade_disputes")}
    rows = [{"link_id": link["id"], "ded_key": x["id"], "category": LABEL[x["category"]], "points": float(x["points"]),
             "what": x["what"], "rule": RULE_TEXT.get(x["rule_id"], ""), "rule_source": RULE_SRC.get(x["rule_id"], ""),
             "fix": x.get("fix"), "reason": x.get("reason"), "confidence": r.get("confidence"),
             "excerpt": x.get("excerpt"), "excerpt_ref": x.get("excerpt_ref")}
            for x in r["deductions"] if x["id"] not in locked]
    if rows:
        d.upsert("grade_deductions", rows, "link_id,ded_key")
    print(f"synced demo link ({COURSE}/{NET}), {len(rows)} deductions, open until {OPEN_UNTIL}")


def status(_a=None):
    d = db()
    link = link_row(d)
    if not link:
        sys.exit("no demo link yet; run build")
    ds = d.get("grade_disputes", link_id=f"eq.{link['id']}",
               select="ticket,status,why,evidence,created_at,grade_deductions(ded_key,what)", order="created_at")
    for x in ds:
        ev = ", ".join(e.get("kind") for e in x.get("evidence") or []) or "no evidence"
        print(f"{x['ticket']}  {x['grade_deductions']['ded_key']}  {x['status']:<8} {x['grade_deductions']['what']}\n"
              f"          why: {x['why'][:200]}  ({ev})")
    print(f"{len(ds)} dispute(s)")
    if link.get("feedback_rating"):
        print(f"feedback: {link['feedback_rating']} of 5, {link['feedback_text'] or '(no comment)'} at {link['feedback_at']}")
    else:
        print("feedback: none")


def resolve(a):
    d = db()
    link = link_row(d)
    ded = d.get("grade_deductions", link_id=f"eq.{link['id']}", ded_key=f"eq.{a.ded}", select="id,points,grade_disputes(id)")
    if not ded or not ded[0].get("grade_disputes"):
        sys.exit(f"{a.ded} has no dispute to resolve")
    change = float(ded[0]["points"]) if a.decision == "restore" else 0.0
    st = "upheld" if change else "denied"
    d.patch("grade_disputes", {"status": st, "points_changed": change, "resolution_note": a.note,
                               "resolved_at": dt.datetime.now(dt.timezone.utc).isoformat()},
            id=f"eq.{ded[0]['grade_disputes'][0]['id'] if isinstance(ded[0]['grade_disputes'], list) else ded[0]['grade_disputes']['id']}")
    oc = outcomes()
    oc[a.ded] = {"status": st, "points_changed": change}
    (OUT / "outcomes.json").write_text(json.dumps(oc, indent=1))
    print(f"{a.ded} marked {st}")
    build()


def reset(_a=None):
    d = db()
    link = link_row(d)
    if link:
        ds = d.get("grade_disputes", link_id=f"eq.{link['id']}", select="id,evidence")
        paths = [e["path"] for x in ds for e in x.get("evidence") or [] if e.get("kind") == "file" and e.get("path")]
        if paths:
            import requests
            from disputes import BUCKET
            requests.delete(f"{d.url}/storage/v1/object/{BUCKET}", headers=d.h, data=json.dumps({"prefixes": paths}), timeout=30)
        if ds:
            d.delete("grade_disputes", link_id=f"eq.{link['id']}")
        d.patch("grade_dispute_links", {"feedback_rating": None, "feedback_text": None, "feedback_at": None,
                                        "feedback_saves": 0}, id=f"eq.{link['id']}")
        print(f"deleted {len(ds)} dispute(s), {len(paths)} file(s), and the feedback")
    (OUT / "outcomes.json").unlink(missing_ok=True)
    build()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("build"); s.add_argument("--no-sync", action="store_true")
    sp.add_parser("status")
    s = sp.add_parser("resolve"); s.add_argument("ded"); s.add_argument("decision", choices=["restore", "keep"])
    s.add_argument("--note", default="")
    sp.add_parser("reset")
    a = ap.parse_args()
    if a.cmd == "build":
        build(sync=not a.no_sync)
    else:
        {"status": status, "resolve": resolve, "reset": reset}[a.cmd](a)


if __name__ == "__main__":
    main()
