#!/usr/bin/env python3
"""Locks the sprint report and the review page: builds both copies of the report and the review page
for a fictional student (fixtures/sample-student: Jordan Rivera, ShiftSwap; no real student data) and
checks what Scott approved on 2026-10-16. /grade-sprint runs this before building any reports; a
failure means a change broke something students or Scott rely on.

    /opt/anaconda3/bin/python3 scripts/tests/test_report.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "grading"))

from sprint_config import categories  # noqa: E402
from sprint_feedback import final, growth_text  # noqa: E402
from sprint_report import render  # noqa: E402
import sprint_review_shell  # noqa: E402

FX = HERE / "fixtures" / "sample-student"
L = lambda n: json.loads((FX / n).read_text())
r, p, G, row_, plan_row = L("result.json"), L("packet.json"), L("growth.json"), L("grades_row.json"), L("plan_row.json")
CATS = categories(2)
student = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="")
scott = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="", scott=True, fairness=[])
review = sprint_review_shell.render([(r, p)], {p["net_id"]: row_}, 2, {p["net_id"]: plan_row},
                                   {p["net_id"]: G}, {}, 40)

fails = []


def check(ok, what):
    if not ok:
        fails.append(what)


def text(h):
    h = re.sub(r"<(script|style|textarea)[^>]*>.*?</\1>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))


st, sc = text(student), text(scott)

# Both copies: sections and order
for h in (student, scott):
    for sec in ('id=summary', 'id=score', 'id=grew', 'id=next', 'id=questions', 'id=appendix'):
        check(sec in h or sec.replace("=", '="') in h, f"section missing: {sec}")

# Instructor notes only in Scott's copy
check("Instructor notes" in sc and "Instructor notes" not in st, "instructor notes must be in Scott's copy only")

# Coach card: title and button at the top, prompt drawer, no first-step line, no subtext
check("Go over this report with Claude Code" in student, "coach card title")
check('class=ccbtn' in student and "Copy prompt" in student, "Copy prompt button")
check("See the prompt" in student, "prompt drawer")
check("First step for Sprint" not in student, "first-step line was removed from the card")
check("sprint-coach" in student, "prompt names the sprint-coach skill")

# Growth: one table with a sprint switch, rows that open, item points that add up
check('class=gsw' in student and 'data-s=1' in student and 'data-s=2' in student, "growth sprint switch")
check(student.count('class=gview') >= 2, "one growth view per sprint")
check('details class="q gx"' in student, "growth axis rows open in place")
check("Sprint 1 <span>+" not in student, "no repeated earlier-sprint list under the table")
cur = re.search(r'<div class=gview data-s=2>(.*?)</div><div class=gview|<div class=gview data-s=2>(.*)', student, re.S)
blk = (cur.group(1) or cur.group(2)) if cur else ""
for row in re.findall(r'<details class="q gx">(.*?)</details></div></details>', blk, re.S):
    head = re.search(r'<span class=gp>\+(\d+)</span>', row)
    items = [float(x) for x in re.findall(r'class=qp>\+([\d.]+)', row)]
    if head and items:
        check(abs(sum(items) - int(head.group(1))) <= 0.6, f"growth items add up to the row (+{head.group(1)} vs {sum(items)})")

# Methodology in plain words
for w in ("spoke", "knowledge fills", "Practice</b>"):
    check(w not in student, f"old Methodology wording: {w}")
check("Where the points come from" in student and "The concept list" in student, "Methodology sections")

# Questions go to Canvas; the posted score is shown, Canvas carries any late deduction
check("Reply to the comment" in student and "Course Monitor" not in student, "questions go to a Canvas comment reply")
check("Posted to Canvas:" in student and "In Canvas:" not in student, "posted score line")

# Student voice: no em dashes, nothing about how evidence was gathered, lateness, or the survey and difficulty
check("—" not in st, "em dash in the student copy")
for w in (r"\bpacket\b", r"\bcoders?\b", r"\bgrader\b", r"session scan", r"\blate\b", r"\bframes?\b"):
    check(not re.search(w, st, re.I), f"student copy mentions: {w}")
check(not re.search(r"\bpacket\b|\bcoders?\b", growth_text(G), re.I), "growth text names how the work was read")

# Review page: rail, filters, frame, keyboard
for x in ("Sprint 2 review", "To look at", "Not approved", "Student copy", "id=frame", "j and k", "feedback/${id}"):
    check(x in review, f"review page: {x}")

if fails:
    print(f"FAILED {len(fails)}:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("report and review page: all checks pass")
