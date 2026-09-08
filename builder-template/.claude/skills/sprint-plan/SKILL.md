---
name: sprint-plan
description: Start a sprint by defining its goal. Interviews the builder about what they will accomplish in the next two weeks, pushes back on vague or unambitious goals, and writes sprints/sprint-N-plan.md ready to commit. Use at the start of every sprint, or when the user says "start my sprint", "plan my sprint", or "/sprint-plan".
---

# Sprint Plan

Write the plan file that opens a two-week sprint. The commit timestamp is the record, so this
runs on day one and the file gets committed the same day.

## Steps

### 1. Work out which sprint this is

Look in `sprints/`. The next number is one higher than the highest `sprint-N-plan.md` present.
If the directory does not exist, this is Sprint 1; create it.

### 2. Read the context

- `README.md` in the repo root for the context declaration: what they are building, who it is
  for, their role, and their user.
- The previous sprint's plan file, if there is one. Pay attention to its **Retro** and to
  **What changes next sprint**, which is what they said they would do differently.
- The previous sprint's review report in `sprints/sprint-<N-1>-review.md`, if present. Note
  which axis it tagged.

If earlier reviews exist, count the axis tags across all of them and tell the user which of
the six axes they have not touched yet. They need five of six by the end.

### 3. Interview

Ask about the goal first, in the user's own terms. Then work through the rest. Ask one thing
at a time; do not present a form.

- **Goal.** What will be true in two weeks that is not true now?
- **Why this.** Why is this the right next thing for what they are building?
- **Done looks like.** How will they know the goal was met? Specific enough that someone else
  could check.
- **Predicted difficulty.** 1 to 5 on the scale below.

### 4. Push back before you write

Do this once, briefly, and then accept their answer. You are not negotiating.

- **Vague goal.** "Improve the app" or "work on the frontend" is not a goal. Ask what
  specifically will be different.
- **Unmeasurable.** If "done looks like" cannot be checked by another person, ask again.
- **Too small.** If it reads like an afternoon of work, say so and ask what else belongs in
  the two weeks.
- **Too large.** If it reads like a semester, say so and ask what the two-week slice is.
- **Ignores the last retro.** If the previous retro said something would change and this plan
  ignores it, point that out once.

Do not push back on difficulty. It is self-reported and not graded.

### 5. Write the file

Write `sprints/sprint-N-plan.md` exactly in this shape, filled in with their answers:

```markdown
# Sprint N Plan

**Goal:** ...

**Why this:** ...

**Done looks like:** ...

**Predicted difficulty:** N
```

Leave the end-of-sprint fields out. `/sprint-review` adds them later.

### 6. Tell them to commit

Print the exact command and say the timestamp is what gets graded:

```bash
git add sprints/sprint-N-plan.md && git commit -m "Sprint N plan" && git push
```

## The difficulty scale

| | |
|---|---|
| 1 | I already knew how to do this before I started |
| 3 | I had to learn something new, but the path was clear |
| 5 | I did not know whether this was possible when I set the goal |

## Rules

- Write the file only after the interview. Do not draft a plan and ask them to approve it.
- Their words, not yours. Tighten wording; do not replace their thinking with your own.
- Never fill in a field they did not answer.
