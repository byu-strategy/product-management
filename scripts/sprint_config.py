"""Where each course's sprints live in Canvas and how they are scored. Shared by the grading scripts.

One set of scripts grades every course that runs the sprint model (builder-template
.claude/sprint-model.md): MSB 341 (the default) and AI Foundry. Pick the course with
`--course ai-foundry` on any grading script, or SPRINT_COURSE=ai-foundry in the environment.
The flag is read here, at import, and taken out of sys.argv, so each script's own argument
parser never sees it. Everything that differs by course is in COURSES below; a script that
needs a course fact reads it from C, never from a constant of its own.

MSB 341: Sprint 1 was one 50-point assignment with the plan inside it. From Sprint 2 on, a sprint
is two assignments: the Plan (10 points, completion, due the first Wednesday) and the Review (the
other three categories, due the day the sprint ends).

AI Foundry: every sprint is two assignments, Plan (10) and Wrap-up (110: Output 60, Review 25,
Demo 25), on the published Sprints page (ai-foundry students/11-sprints.qmd).
"""
import os
import sys
from pathlib import Path

HUB = Path.home() / "hubs/courses"


def _course_from_argv():
    a = sys.argv
    for i, x in enumerate(a):
        if x == "--course" and i + 1 < len(a):
            c = a[i + 1]
            del a[i:i + 2]
            return c
        if x.startswith("--course="):
            del a[i]
            return x.split("=", 1)[1]
    return None


COURSE = _course_from_argv() or os.environ.get("SPRINT_COURSE") or "msb341"
COURSE = {"msb": "msb341", "pm": "msb341", "foundry": "ai-foundry"}.get(COURSE, COURSE)
os.environ["SPRINT_COURSE"] = COURSE  # child processes (tests, helpers) grade the same course

COURSES = {
    "msb341": {
        "label": "MSB 341 Product Management",
        "short": "MSB 341 (Product Management)",
        "school": "BYU Marriott School of Business",
        "canvas": 36977,
        "data": "product-management",
        "roster": "roster-msb341-fall2026.csv",
        "plan_fields": ("Goal", "Why this", "Done looks like", "Predicted difficulty"),
        "sprints": {
            1: {"plan": None, "review": 1500870, "plan_due": "2026-09-16 23:59"},
            2: {"plan": 1506688, "review": 1506686},
            3: {"plan": 1506689, "review": 1506690},
            4: {"plan": 1506691, "review": 1506692},
            5: {"plan": 1506693, "review": 1506694},
            6: {"plan": 1506695, "review": 1506696},
        },
        "graded": {**{n: [("shipped", "Output", 20), ("review", "Review", 10), ("demo", "Demo", 10)] for n in range(1, 6)},
                   6: [("shipped", "Output", 50), ("review", "Review", 20), ("demo", "Demo", 20)]},
        "plan_inside_review": {1},
        "grader_overlay": None,
        "rules_file": None,
        "site": "https://byu-strategy.github.io/product-management/",
        "rules_url": "https://byu-strategy.github.io/product-management/00-assessments.html#sprints",
        "where_heading": "Where the work lives",
        "plan_due_text": "First Wednesday, 11:59 PM",
        "wrapup_due_text": "The Monday the sprint ends, 11:59 PM",
        "baseline": "baseline-charts-fall2026/students.json",
        "midterm": True,
        "dispute_course": "msb341",
        "not_graded": None,
    },
    "ai-foundry": {
        "label": "AI Foundry",
        "short": "AI Foundry",
        "school": "BYU Marriott School of Business",
        "canvas": 37925,
        "data": "ai-foundry",
        "roster": "roster-foundry-fall2026.csv",
        "plan_fields": ("Menu", "Teammates", "Goal", "My part", "Who will see it", "Why this",
                        "What done looks like", "Predicted difficulty"),
        "sprints": {
            1: {"plan": 1515512, "review": 1515513},
            2: {"plan": 1515514, "review": 1515515},
            3: {"plan": 1515516, "review": 1515517},
        },
        "graded": {n: [("shipped", "Output", 60), ("review", "Review", 25), ("demo", "Demo", 25)] for n in range(1, 4)},
        "plan_inside_review": set(),
        "grader_overlay": "sprint-grader-foundry.md",
        "rules_file": "foundry_rules.json",
        "site": "https://byu-strategy.github.io/ai-foundry/",
        "rules_url": "https://byu-strategy.github.io/ai-foundry/students/11-sprints.html#grading-rubric",
        "where_heading": "Work files and links",
        "plan_due_text": "The Monday after the sprint starts, 11:59 PM",
        "wrapup_due_text": "The Friday the sprint ends, 8:00 AM",
        "baseline": "baseline-charts-fall2026/students.json",
        "midterm": False,
        "dispute_course": "ai-foundry",
        # Auditors are on the Canvas roster but are not graded: one net_id per line (the app's roster
        # status "auditing", checked 2026-11-09).
        "not_graded": "not-graded.txt",
    },
}
if COURSE not in COURSES:
    raise SystemExit(f"unknown course {COURSE!r}; one of {', '.join(COURSES)}")

C = COURSES[COURSE]
DATA = Path(os.environ.get("PM_DATA") or HUB / "_data" / C["data"])
COURSE_ID = C["canvas"]
PLAN_FIELDS = C["plan_fields"]
PLAN_POINTS = 10
SPRINTS = C["sprints"]
GRADED = C["graded"]


def roster():
    """The Canvas roster rows that are graded (auditors left out)."""
    import csv
    rows = list(csv.DictReader(open(DATA / C["roster"])))
    skip = set()
    if C["not_graded"] and (DATA / C["not_graded"]).exists():
        skip = {l.split("#")[0].strip() for l in (DATA / C["not_graded"]).read_text().splitlines()} - {""}
    return [r for r in rows if r["net_id"] not in skip]


def categories(sprint):
    """Every category on the assignment being posted. MSB 341 Sprint 1's plan sits inside its one assignment."""
    cats = GRADED[sprint]
    return ([("plan", "Plan", PLAN_POINTS)] + cats) if sprint in C["plan_inside_review"] else cats


def review_points(sprint):
    return sum(mx for _, _, mx in categories(sprint))
