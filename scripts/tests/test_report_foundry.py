"""The AI Foundry report: the same approved layout as MSB 341 (test_report.py), with the Foundry's own
points, rules and wording. Renders the fictional sample student under --course ai-foundry.

    python3 ~/courses/product-management/scripts/tests/test_report_foundry.py

Run it, and test_report.py, before building either course's reports.
"""
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

sys.argv += ["--course", "ai-foundry"]  # read by sprint_config at import
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "grading"))

from sprint_config import C, COURSE, categories  # noqa: E402
from sprint_feedback import final, published_rules  # noqa: E402
from sprint_report import RULE_TEXT, render  # noqa: E402

assert COURSE == "ai-foundry", COURSE
FX = HERE / "fixtures" / "sample-student"
L = lambda n: json.loads((FX / n).read_text())
r, p, G, row_, plan_row = L("result.json"), L("packet.json"), L("growth.json"), L("grades_row.json"), L("plan_row.json")

# The sample student, scored on the Foundry's scale: Output 55 of 60, Review 22 of 25, Demo 25 of 25.
r = copy.deepcopy(r)
r["scores"] = {"shipped": 55, "review": 22, "demo": 25}
r["deductions"] = [
    {"id": "O1", "category": "shipped", "points": 5, "rule_id": "f-out-checkable",
     "what": "Interview notes are not in a repo Professor Murff can open",
     "fix": "Commit the notes to the Foundry repo, or list where they live under Work files and links.",
     "reason": "fixture", "excerpt": None, "excerpt_ref": None},
    {"id": "R1", "category": "review", "points": 3, "rule_id": "f-rev-retro",
     "what": "No answer to “What did the client or your users say or do about the work?”",
     "fix": "Say what the client contact did with the work.", "reason": "fixture", "excerpt": None, "excerpt_ref": None},
]
row_ = dict(row_, shipped="55", review="22", demo="25", grader_total="102", final_total="102")
CATS = categories(2)
DIS = {"token": "TEST_TOKEN_abc", "closes": {"opens": "Mon, Nov 16", "closes": "Mon, Nov 23"}}
student = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="", dispute=DIS)
scott = render(r, p, row_, 2, CATS, final, plan_row=plan_row, growth=G, skills_status="", scott=True, fairness=[], dispute=DIS)

fails = []


def check(ok, what):
    if not ok:
        fails.append(what)


text = lambda h: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style|textarea)[^>]*>.*?</\1>", " ", h, flags=re.S)))
st = text(student)

check(CATS == [("shipped", "Output", 60), ("review", "Review", 25), ("demo", "Demo", 25)], f"Foundry categories: {CATS}")
check("<b>AI Foundry</b>" in student and "MSB 341" not in st, "brand and course name are the Foundry's")
check("ai-foundry/students/11-sprints.html" in student, "the coach prompt points at the Foundry's Sprints page")
check("from AI Foundry." in student, "the coach prompt names the course")
check("Work files and links" in student, "the deliverables table uses the Foundry README heading")
check("The Monday after the sprint starts, 11:59 PM" in student and "8:00 AM" in student, "Foundry due times")
check("/60" in student and "/25" in student, "Foundry maxima shown")
check("Instructor notes" in text(scott) and "Instructor notes" not in st, "instructor notes in Scott's copy only")
for sec in ('id=summary', 'id=score', 'id=grew', 'id=next', 'id=questions', 'id=appendix', 'id=concepts'):
    check(sec in student, f"section missing: {sec}")
check("Rubric: &ldquo;" in student and "To earn it next time:" in student, "rubric quote and fix under each deduction")
check({"f-out-checkable", "f-rev-committed", "f-demo-working"} <= published_rules(1), "Foundry rules are published from Sprint 1")
check("f-rev-retro" not in published_rules(1) and "f-rev-retro" in published_rules(2), "retro amounts from Sprint 2 only")
check("f-demo-length" not in published_rules(1) and "f-demo-length" in published_rules(2), "demo length from Sprint 2 only")

# Every Foundry rule quote is the published sentence, word for word, as of Sprint 1's start (commit 9d4d7ba).
site = subprocess.run(["git", "-C", str(Path.home() / "courses/ai-foundry"), "show", "9d4d7ba:students/11-sprints.qmd"],
                      capture_output=True, text=True).stdout
site = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", site).replace("**", "").replace("`", "")
for k, q in RULE_TEXT.items():
    check(" ".join(q.split()).lower() in " ".join(site.split()).lower(), f"rule {k} quotes the Sprints page word for word")

if fails:
    print("FOUNDRY REPORT CHECKS FAILED:\n- " + "\n- ".join(fails))
    sys.exit(1)
print("foundry report: all checks pass")
