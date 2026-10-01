"""Where each MSB 341 sprint lives in Canvas and how it is scored. Shared by the grading scripts.

Sprint 1 was one 50-point assignment with the plan inside it. From Sprint 2 on, a sprint is two
assignments: the Plan (10 points, completion, due the first Wednesday) and the Review (the other
three categories, due the day the sprint ends). The plan's completion score is computed in code;
graders score only the Review categories.
"""
COURSE_ID = 36977
PLAN_FIELDS = ("Goal", "Why this", "Done looks like", "Predicted difficulty")
PLAN_POINTS = 10

SPRINTS = {
    1: {"plan": None, "review": 1500870, "plan_due": "2026-09-16 23:59"},
    2: {"plan": 1506688, "review": 1506686},
    3: {"plan": 1506689, "review": 1506690},
    4: {"plan": 1506691, "review": 1506692},
    5: {"plan": 1506693, "review": 1506694},
    6: {"plan": 1506695, "review": 1506696},
}

# The categories a grader scores, with their maxima.
GRADED = {n: [("shipped", "Output", 20), ("review", "Review", 10), ("demo", "Demo", 10)]
          for n in range(1, 6)}
GRADED[6] = [("shipped", "Output", 50), ("review", "Review", 20), ("demo", "Demo", 20)]


def categories(sprint):
    """Every category on the assignment being posted. Sprint 1's plan sits inside its one assignment."""
    cats = GRADED[sprint]
    return ([("plan", "Plan", PLAN_POINTS)] + cats) if sprint == 1 else cats


def review_points(sprint):
    return sum(mx for _, _, mx in categories(sprint))
