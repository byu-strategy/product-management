#!/usr/bin/env python3
"""Draw a builder profile (baseline spider chart) for every MSB 341 student who took the survey.

    python3 ~/courses/product-management/scripts/baseline_profiles.py
    python3 ~/courses/product-management/scripts/baseline_profiles.py path/to/responses.xlsx

The drawing belongs to the foundry-baseline-charts skill; this script only runs it for this
roster. It parses the newest "AI Foundry Baseline*.xlsx" in ~/Downloads with the skill's
parse_baseline.py, keeps the students on the MSB 341 roster (the export covers several
courses), stamps each with its net_id, and draws the charts with make_charts.py into the
standard spot:

    ~/hubs/courses/_data/product-management/baseline-charts-fall2026/
        students.json          axis means by net_id; student_status.py reads it
        student-charts/*.png   the handout set, one per student; send_baseline.py emails these
        charts/*.png           with the cohort average as a ghost line, for Scott
        contact-sheet.png

It redraws every chart each run. The scores come only from the survey, so a redrawn chart is
the same picture unless the student re-took the survey. Who has been emailed their chart is
not decided here: that is baseline-sends.csv, written by send_baseline.py.

The same students.json carries net_id so nothing downstream has to re-match names, which is
where students got lost before. Names are matched through the survey's email column first,
then people_match, the same way student_status.py matches survey responses.

Student data goes only to _data and _private, never to git. This file holds no student data.
"""
import csv, json, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import people_match as pm
from student_status import newest_export

SKILL = Path.home() / ".claude/skills/foundry-baseline-charts/scripts"
DATA = Path.home() / "hubs/courses/_data/product-management"
PRIVATE = Path.home() / "courses/product-management/_private"
ROSTER = DATA / "roster-msb341-fall2026.csv"
OUT = DATA / "baseline-charts-fall2026"
SUBTITLE = "MSB 341 / IS 693R builder baseline, Fall 2026"


def name_to_student(export, idx):
    """Survey 'Name' text -> roster student, using the row's email where the name alone fails."""
    import openpyxl
    ws = openpyxl.load_workbook(export, read_only=True).active
    rows = [r for r in ws.iter_rows(values_only=True) if any(r)]
    header = [str(h or "") for h in rows[0]]
    email_col = next(i for i, h in enumerate(header) if "email" in h.lower())
    name_cols = [i for i, h in enumerate(header) if h.strip() == "Name"]
    out = {}
    for r in rows[1:]:
        name = next((str(r[i]).strip() for i in name_cols if r[i] and str(r[i]).strip()), "")
        student, _ = pm.find(idx, email=str(r[email_col] or "").strip(), display=name)
        if name and student:
            out[name] = student
    return out


def main():
    export = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_export()
    students = [s for s in csv.DictReader(ROSTER.open(newline="", encoding="utf-8-sig"))
                if s["enrollment_state"] == "active"]
    who = name_to_student(export, pm.index(students))

    with tempfile.TemporaryDirectory() as tmp:
        parsed = Path(tmp) / "all.json"
        subprocess.run([sys.executable, SKILL / "parse_baseline.py", export, "-o", parsed],
                       check=True, stdout=subprocess.DEVNULL)
        # A student who submitted twice appears twice; the later response wins.
        mine = {}
        for rec in json.loads(parsed.read_text()):
            s = who.get(rec["name"].strip())
            if s:
                mine[s["net_id"]] = {**rec, "net_id": s["net_id"]}

        before = {r["net_id"] for r in json.loads((OUT / "students.json").read_text())
                  if r.get("net_id")} if (OUT / "students.json").exists() else set()
        OUT.mkdir(mode=0o700, exist_ok=True)
        (OUT / "students.json").write_text(json.dumps(list(mine.values()), indent=1))
        subprocess.run([sys.executable, SKILL / "make_charts.py", OUT / "students.json",
                        "-o", OUT, "--subtitle", SUBTITLE], check=True, stdout=subprocess.DEVNULL)

    new = sorted(set(mine) - before)
    print(f"{len(mine)} builder profiles drawn from {export.name} "
          f"({len(new)} new since the last run)")
    for n in new:
        print(f"  + {mine[n]['name']} ({n})")
    print(f"  {OUT}")
    try:
        shutil.copytree(OUT, PRIVATE / OUT.name, dirs_exist_ok=True)
        print(f"  {PRIVATE / OUT.name}")
    except OSError as e:
        print(f"  note: could not back up to _private ({e})")


if __name__ == "__main__":
    main()
