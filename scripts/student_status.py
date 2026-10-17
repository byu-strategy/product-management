#!/usr/bin/env python3
"""One row per MSB 341 student: baseline survey, GitHub repo, Slack channel.

    python3 ~/courses/product-management/scripts/student_status.py
    python3 ~/courses/product-management/scripts/student_status.py path/to/responses.xlsx

Joins what the other scripts produce into a single view, so "who has done what" is one file
instead of four. Run canvas_roster.py, github_roster.py and slack_roster.py first; this script
only joins, it never fetches.

The survey export defaults to the newest "AI Foundry Baseline*.xlsx" in ~/Downloads, because
that file is re-exported by hand and lands there with a new (n) suffix each time. The export
covers several courses, so responses that do not match this roster are counted and ignored.

Matching is by BYU email, then through people_match for students who answered from another
address. Every row records how each of the three was matched, so a blank is a real gap rather
than a matching failure.

Student data goes only to _data and _private, never to git. This file holds no student data.
"""
import csv, shutil, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import people_match as pm

DATA = Path.home() / "hubs/courses/_data/product-management"
PRIVATE = Path.home() / "courses/product-management/_private"
ROSTER = DATA / "roster-msb341-fall2026.csv"
GITHUB = DATA / "github-roster.csv"
SLACK = DATA / "slack-members.csv"
OUT = DATA / "student-status.csv"
BASELINE = DATA / "baseline-charts-fall2026" / "students.json"   # per-axis means, by net_id
SENDS = DATA / "baseline-sends.csv"          # who was emailed their chart, from send_baseline.py
# Who agreed to be a go-to person (deputy). Hand-kept by Scott as replies arrive, so it is not
# regenerable and lives only in _private, never copied to _data. send_deputy.py records who was
# asked; this table is the only record of who said yes.
DEPUTIES = PRIVATE / "deputies.md"

AXES = ["Discovery", "Design", "Application Architecture",
        "AI Systems", "Agentic Workflow", "Launch and Learn"]
AXIS_COL = {a: a.lower().replace(" ", "_") for a in AXES}

COLUMNS = ["sortable_name", "net_id", "email", "section",
           "survey", "survey_at", "profile", "profile_sent",
           *AXIS_COL.values(), "baseline_mean", "baseline_low_axis",
           "github", "repo_url", "plan_pushed", "sprint_plan_skill", "canvas_submitted",
           "slack", "slack_joined_at", "slack_handle",
           "deputy", "deputy_area", "deputy_note", "deputy_as_of",
           "done_count", "missing", "sprint_review_skill"]


def newest_export():
    downloads = sorted(Path.home().glob("Downloads/AI Foundry Baseline*.xlsx"),
                       key=lambda p: p.stat().st_mtime, reverse=True)
    if not downloads:
        sys.exit("No 'AI Foundry Baseline*.xlsx' in ~/Downloads. Pass the path as an argument.")
    return downloads[0]


def survey_rows(path, students):
    """net_id -> timestamp, for roster students who answered. Others are counted and dropped."""
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True).active
    rows = [r for r in ws.iter_rows(values_only=True) if any(r)]
    header = [str(h or "") for h in rows[0]]
    ts_col = header.index("Timestamp")
    email_col = next(i for i, h in enumerate(header) if "email" in h.lower())
    name_col = header.index("Name") if "Name" in header else 1

    idx = pm.index(students)
    found, other = {}, 0
    for r in rows[1:]:
        email = str(r[email_col] or "").strip()
        student, _ = pm.find(idx, email=email, display=str(r[name_col] or ""))
        if not student:
            other += 1
            continue
        stamp = r[ts_col]
        found.setdefault(student["net_id"],
                         stamp.strftime("%Y-%m-%d") if hasattr(stamp, "strftime") else str(stamp))
    return found, other, len(rows) - 1


def deputies():
    """net_id -> {deputy, deputy_area, deputy_note, deputy_as_of}, from the Status table in
    deputies.md. Status cells read like "**agreed** — design only; declined ..." or
    "asked, no reply yet"; the word before the dash becomes `deputy`, the rest `deputy_note`.

    The file is in OneDrive, whose Files On-Demand can stall a read for minutes. The read runs
    in a thread with a timeout, and a stall leaves the columns blank rather than hanging the run.
    """
    import re, threading
    box = {}
    t = threading.Thread(target=lambda: box.update(text=DEPUTIES.read_text(encoding="utf-8")),
                         daemon=True)
    t.start()
    t.join(20)
    if "text" not in box:
        return None
    out = {}
    for line in box["text"].split("## Status", 1)[-1].splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or not re.fullmatch(r"[a-z0-9]+", cells[1]):
            continue
        _, net_id, area, status, as_of = cells
        status = status.replace("**", "")
        word, _, note = status.partition("—")
        word = word.strip().rstrip(",")
        kind = ("agreed" if word.startswith("agreed") else
                "declined" if word.startswith("declined") else "asked")
        out[net_id] = {"deputy": kind, "deputy_area": area, "deputy_as_of": as_of,
                       "deputy_note": note.strip() or ("" if kind != "asked" else word)}
    return out


def read(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return {r["net_id"]: r for r in csv.DictReader(f) if r.get("net_id")}


def main():
    export = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_export()
    students = [s for s in csv.DictReader(ROSTER.open(newline="", encoding="utf-8-sig"))
                if s["enrollment_state"] == "active"]
    github, slack = read(GITHUB), read(SLACK)
    # Axis means come from the same students.json the charts were drawn from, so a number in
    # this file and a number on a student's chart can never disagree.
    import json
    scores = {r["net_id"]: r["means"] for r in json.loads(BASELINE.read_text())
              if r.get("net_id")} if BASELINE.exists() else {}
    survey, other, total = survey_rows(export, students)
    deps = deputies() if DEPUTIES.exists() else {}
    sends = {}
    if SENDS.exists():
        for r in csv.DictReader(SENDS.open(newline="", encoding="utf-8")):
            sends.setdefault(r["net_id"], r["sent_at"][:10])

    rows = []
    for s in students:
        g = github.get(s["net_id"], {})
        k = slack.get(s["net_id"], {})
        means = scores.get(s["net_id"], {})
        axis_cells = {AXIS_COL[a]: (f"{means[a]:.2f}" if a in means else "") for a in AXES}
        overall = f"{sum(means.values()) / len(means):.2f}" if means else ""
        low = min(means, key=means.get) if means else ""

        has = {"survey": s["net_id"] in survey,
               "github": bool(g.get("repo_url")),
               "slack": k.get("in_channel") == "yes"}
        rows.append({
            "sortable_name": s["sortable_name"], "net_id": s["net_id"], "email": s["email"],
            "section": s["section"].split(":")[0],
            "survey": "yes" if has["survey"] else "no",
            "survey_at": survey.get(s["net_id"], ""),
            "profile": "yes" if means else "no",
            "profile_sent": sends.get(s["net_id"], ""),
            **axis_cells, "baseline_mean": overall, "baseline_low_axis": low,
            "github": "yes" if has["github"] else "no",
            "repo_url": g.get("repo_url", ""),
            "plan_pushed": g.get("plan_pushed", ""),
            "sprint_plan_skill": g.get("sprint_plan_skill", ""),
            "sprint_review_skill": g.get("sprint_review_skill", ""),
            "canvas_submitted": g.get("canvas_submitted", ""),
            "slack": "yes" if has["slack"] else "no",
            "slack_joined_at": k.get("joined_at", ""),
            "slack_handle": k.get("slack_handle", ""),
            **(deps or {}).get(s["net_id"], {}),
            "done_count": sum(has.values()),
            "missing": " ".join(name for name, ok in has.items() if not ok),
        })

    rows.sort(key=lambda r: (r["done_count"], r["sortable_name"]))
    # Read the last run before overwriting it, so the report can say what moved.
    before = read(OUT) if OUT.exists() else {}
    before_at = (dt.datetime.fromtimestamp(OUT.stat().st_mtime)
                 .strftime("%Y-%m-%d %H:%M") if OUT.exists() else "")
    scored = [r for r in rows if r["baseline_mean"]]
    if scored:
        print(f"{len(scored)} students have baseline scores merged in "
              f"(mean {sum(float(r['baseline_mean']) for r in scored) / len(scored):.2f} of 5)")
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, restval="")
        w.writeheader()
        w.writerows(rows)
    OUT.chmod(0o600)

    n = len(rows)
    for key, label in (("survey", "completed the baseline survey"),
                       ("github", "shared a GitHub repo"),
                       ("slack", "joined the Slack channel")):
        print(f"{sum(1 for r in rows if r[key] == 'yes'):>3} of {n}  {label}")
    drawn = [r for r in rows if r["profile"] == "yes"]
    waiting = [r for r in drawn if not r["profile_sent"]]
    print(f"{len(drawn):>3} of {n}  have a builder profile, "
          f"{len(drawn) - len(waiting)} emailed, {len(waiting)} not yet emailed")
    for r in waiting:
        print(f"       not yet emailed: {r['sortable_name']}")
    if deps is None:
        print(f"       deputies: {DEPUTIES.name} did not open within 20s (OneDrive); columns left blank")
    elif deps:
        by = {k: [r for r in rows if r.get("deputy") == k] for k in ("agreed", "asked", "declined")}
        print(f"{len(deps):>3} asked to be deputies: {len(by['agreed'])} agreed, "
              f"{len(by['asked'])} no reply yet" + (f", {len(by['declined'])} declined" if by["declined"] else ""))
        for r in by["agreed"]:
            print(f"       agreed: {r['sortable_name']} ({r['deputy_area']}"
                  + (f"; {r['deputy_note']}" if r["deputy_note"] else "") + ")")
        missing = set(deps) - {r["net_id"] for r in rows}
        if missing:
            print(f"       not on the active roster: {', '.join(sorted(missing))}")
    unscored = [r for r in rows if r["survey"] == "yes" and r["profile"] == "no"]
    if unscored:
        print(f"       {len(unscored)} took the survey but have no profile; run baseline_profiles.py")
    from collections import Counter
    print()
    for count, k in sorted(Counter(r["done_count"] for r in rows).items(), reverse=True):
        print(f"{k:>3} students have {count} of 3")
    if before:
        print(f"\nsince the last run ({before_at}):")
        for key in ("survey", "github", "slack"):
            gained = sum(1 for r in rows if r[key] == "yes" and before.get(r["net_id"], {}).get(key) == "no")
            lost = sum(1 for r in rows if r[key] == "no" and before.get(r["net_id"], {}).get(key) == "yes")
            print(f"  {key:<7} +{gained}" + (f"  -{lost}" if lost else ""))
        new = sum(1 for r in rows if r["net_id"] not in before)
        gone = sum(1 for n in before if n not in {r["net_id"] for r in rows})
        if new or gone:
            print(f"  roster  {new} new, {gone} no longer active")
    stamp = dt.datetime.fromtimestamp(export.stat().st_mtime)
    print(f"\nsurvey export: {export.name}, downloaded {stamp:%Y-%m-%d %H:%M} ({total} responses, {other} from outside this roster)")
    print(f"  {OUT}")
    try:
        shutil.copy2(OUT, PRIVATE / OUT.name)
        print(f"  {PRIVATE / OUT.name}")
    except Exception as e:
        print(f"  note: could not back up to _private ({e})")


if __name__ == "__main__":
    main()
