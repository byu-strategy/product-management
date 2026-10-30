#!/usr/bin/env python3
"""Locks the sprint report and the review page: builds both copies of the report and the review page
for a fictional student (fixtures/sample-student: Jordan Rivera, ShiftSwap; no real student data) and
checks what Scott approved on 2026-10-16, revised 2026-10-29 (itemized point deductions with Dispute links,
Next steps before Growth, one Evidence drawer per category, clickable tree rings, the "not yet in your
profile" drawer, BYU brand colors). /grade-sprint runs this before building any reports; a
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
DIS = {"token": "TEST_TOKEN_abc", "closes": "Nov 5"}
student = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="", dispute=DIS)
scott = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="", scott=True, fairness=[], dispute=DIS)
plain = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="")  # no dispute link
resolved = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="", dispute=DIS,
                  outcomes={"R1": {"status": "upheld", "points_changed": 1}, "R2": {"status": "denied"}})
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
    for sec in ('id=summary', 'id=score', 'id=grew', 'id=next', 'id=questions', 'id=appendix', 'id=concepts'):
        check(sec in h or sec.replace("=", '="') in h, f"section missing: {sec}")

# Instructor notes only in Scott's copy
check("Instructor notes" in sc and "Instructor notes" not in st, "instructor notes must be in Scott's copy only")

# Coach card: title and button at the top, prompt drawer, no first-step line, no subtext
check("Go over this report with Claude Code" in student, "coach card title")
check('class=ccbtn' in student and "Copy prompt" in student, "Copy prompt button")
check("See the prompt" in student, "prompt drawer")
check("First step for Sprint" not in student, "first-step line was removed from the card")
check("sprint-coach" in student, "prompt names the sprint-coach skill")
check("refresh-skills/refresh.py" in student, "the coach prompt updates the course skills first")

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
check("Where the points come from" in student and "Appendix B: Concept list" in student, "appendix sections")

# Section order: Next steps before Growth (2026-10-29)
for h in (student, scott):
    check(h.find("id=score") < h.find("id=deds") < h.find("id=questions") < h.find("id=next") < h.find("id=grew")
          < h.find("id=appendix") < h.find("id=concepts"),
          "order: Score (deductions, then questions), Next steps, Growth, Appendix A, Appendix B")
check("Appendix A: How grading works" in student and "Methodology</span>" not in student, "Appendix A heading")

# One heading hierarchy (2026-10-29): sections are h2 and all styled alike; their parts are h3.sub, which
# the contents list nests under them. Questions is an h3 under Score, not its own section.
import re as _re2
_h2 = _re2.findall(r'<section id=(\w+) class="sec ([^"]*)"><h2>', student)
check([i for i, _c in _h2] == ["summary", "score", "next", "grew", "appendix", "concepts"], f"student sections are exactly the six: {_h2}")
check(all(c.strip() == "" for _i, c in _h2), "every student section heading has the same style")
check('<div class=qa id=questions><h3 class=sub>' in student, "Questions is an h3 under Score")
check(all(f'id={x}><span>' in student for x in ("a-profile", "a-points", "a-earn", "a-counts")), "Appendix A topics are h3 headings")

# Questions: disputes through the Dispute buttons, everything else as a Canvas comment reply
check("Questions or disputes" in student and "use its Dispute button" in student, "disputes section")
check("How useful is this report?" in student and student.count('name=rating value=') == 5
      and 'name=token value="TEST_TOKEN_abc"' in student and "/api/report-feedback" in student,
      "report feedback form: five ratings, a comment, sent in place with the link token")
check("/api/report-feedback" not in plain, "no feedback form without a token")
check("reply to the comment this report came with" in student and "Course Monitor" not in student, "questions go to a Canvas comment reply")
check("posted to Canvas" in student and "class=qtotal" not in student, "posted score in the Score heading, no total row")

# Point deductions: one row each, rule and fix shown, Dispute links to the Strategy app; reasons only in Scott's copy
check("Point deductions" in student and student.count("class=ded ") == 2, "two itemized deductions")
check(student.count('href="https://strategy.byu.edu/app/dispute/TEST_TOKEN_abc#R') == 2, "a Dispute link per deduction")
check("class=ihours" in scott and "class=ihours" not in student and "about 10 to 14 hours" not in student,
      "hours only in Scott's copy")
check("To earn it next time:" in student and "Rubric: &ldquo;" in student, "rubric quote and fix under each deduction")

# Every rule quote is the published sentence, word for word (links, bold and code marks removed)
import re as _re
from sprint_report import RULE_TEXT, QUOTE_EXEMPT
_site = (Path(__file__).resolve().parents[2] / "00-assessments.qmd").read_text()
_site = _re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", _site).replace("**", "").replace("`", "")
_site = " ".join(_site.split())
for _k, _q in RULE_TEXT.items():
    if _k not in QUOTE_EXEMPT:
        check(" ".join(_q.split()).lower() in _site.lower(), f"rule {_k} quotes the Assessments page word for word")
check("open until Nov 5" in student, "dispute window shown")
check("The retro has answers under three of five prompts" in scott and "The retro has answers under three of five prompts" not in student,
      "grader's reason in Scott's copy only")
check("/app/dispute/" not in plain and "Questions or disputes" not in plain, "no dispute link without a token")
check("Restored 1 point" in resolved and "Kept after review" in resolved and "/app/dispute/" not in resolved.split("id=next")[0].split("id=deds")[1],
      "resolved deductions show their outcome instead of a Dispute link")
check("2 points deducted in 2 items" in student, "summary card names the deductions")
check("Each point deduction above says how to earn" in student, "next steps point to the deductions")

# Evidence: one drawer per category, parts as subheadings
check(student.count('<details class="q ev">') == 2 and "<div class=evi><h4>Commits" in student, "one Evidence drawer per category")

# Tree rings: tagged rings, axis labels, legend buttons, the hover and click script
check(student.count("polygon data-s=") >= 2 and student.count("class=axl") == 6, "rings and axis labels are clickable")
check("class=lg data-s=" in student and "Click a ring, an axis, or a sprint" in student and "const rowFor" in student, "ring routing")

# Not yet in the profile: a closed drawer grouped by what would count; unreadable items only in Scott's notes
check("<details class=ncx id=notyet>" in student and "Work not counted" not in student, "not-yet drawer, closed")
check("To make it count:" in student and "Nothing to do:" in student, "not-yet groups say what would count")
check("could not be read for this review" not in st and "Could not be read" in sc, "unreadable items in Scott's notes only")

# Brand: the Strategy app's navy and royal, IBM Plex Sans, the course bar
check("#002E5D" in student and "#003DA5" in student and "IBM Plex Sans" in student and "#b45f04" not in student, "BYU brand colors")
check("MSB 341 Product Management" in student, "course bar")

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
