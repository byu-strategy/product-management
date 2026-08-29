# Grading Architecture (scratch, off the site)

Status: working draft for stress-testing, July 2026. Not student-facing. Not in
`_quarto.yml` (the leading underscore keeps Quarto from rendering it). Nothing
here is on the live site or in Canvas yet. When it settles, it feeds a rewrite
of `00-assessments.qmd` and `93-why-this-class-works.qmd`.

## The problem this solves

Past classes compressed at the top: most students earned A's, so the grade
rewarded neither effort nor expertise fairly. AI makes this worse right now.
When every student has Claude Max, the floor of output quality rises and
everyone can produce a decent-looking spec, PRD, and prototype. The tool
compresses the bottom upward. The goal is an honest distribution that fairly
rewards both harder work and more skill.

## Governing principle

Grade the scarce thing, measure the honest thing, hold the bar with anchors.

- A grade certifies **demonstrated competence against defined, absolute
  criteria** (criterion-referenced). Not rank against peers (a curve), and not
  improvement over a starting point (growth).
- **Setting the grade and measuring learning are different jobs.** Growth is the
  wrong basis for a grade because it punishes the student who arrives already
  sharp, but it is the right basis for measurement. Keep them in separate boxes.
- **No forced curve.** It would poison a collaborative practice room. Use a
  private design-target distribution (roughly 25 to 30% A, 45% B, the rest C or
  below) only as a check on whether the rubrics have real headroom, never
  imposed on students.

A defensible grade is valid (measures PM competence, not compliance), reliable
(same work, same grade, because it is anchored to exemplars), aligned (the thing
graded is the thing taught and the thing the job needs), and defensible (you can
put artifact and criterion side by side and explain it to a student who came to
argue).

## The grid: effort floors, expertise ceilings

Two explicit dimensions. Do not add them into one number. Read the letter off
the grid. Expertise drives the letter; effort (reps) sets the floor and gates
the very top.

|              | Excellent | Proficient | Developing | Weak  |
|--------------|-----------|------------|------------|-------|
| Full reps    | A         | B+         | B          | B-    |
| Partial reps | A-        | B          | C+         | C     |
| Minimal reps | B+        | C+         | C          | D / F |

Two rules generate the whole grid:

- **Ceiling rule (expertise):** an A requires Excellent work **and** full reps.
  Raw excellence without the reps steps down A to A- to B+ as reps drop. No
  volume of effort alone reaches an A.
- **Floor rule (effort):** full reps guarantee no worse than B-. Work hard and
  you pass comfortably and are never in danger.

Decided edge values: full-effort floor is **B-**, raw-excellence cap is **B+**.
(Scott briefly considered a B floor for a character/diligence reward, then moved
back to B- for a wider, more honest spread. The character signal is recovered by
making "full reps" a genuinely strict bar and the floor genuinely unfailable.)

The below-B world exists only in the Partial and Minimal rows. That is why the
effort bar has to be strict: if nearly all 70 students clear "full reps," the
distribution collapses into just B and A again. **The strictness of "full reps"
is the single load-bearing decision in the whole system.**

## Expertise axis (judged, holistic, anchored)

Expertise is a **judgment** problem, not a measurement problem. Read the whole
repo (product, specs, discovery, decisions, metrics) plus the sprint video, and
place it against published anchor exemplars. Score the **human layer AI cannot
hand them**, not the presence or polish of artifacts (which is now free).

- **Excellent.** One coherent product thesis the whole repo serves. Decisions in
  `decisions/` are justified by real discovery (talked to actual users, real
  data), not asserted. Tradeoffs named and defended. The MVP actually works and
  solves the stated problem. Visible evidence they changed their mind at least
  once when discovery pushed back. In the video they reason well about a "what
  breaks if your assumption is wrong" prompt rather than reciting. Shows taste
  beyond what the tool gives.
- **Proficient.** Complete and coherent. Product makes sense, specs are clear,
  MVP runs, discovery happened. But decisions are more asserted than defended,
  discovery is thinner, little sign of real iteration or mind-changing. This is
  "strong student who used the tool well." An honest B-range, and where most
  diligent students will land. That is correct, not a failure.
- **Developing.** Incomplete or incoherent in places. Artifacts exist but
  disconnected: the spec does not match what got built, discovery is not
  reflected in the decisions. Product works partially or solves a fuzzy problem.
  Reasoning reads generic, like unedited model output.
- **Weak.** Missing, broken, or generic. MVP does not work or is not there.
  Discovery absent or fabricated. Decisions unexplained. Reads as AI filler with
  no human judgment behind it.

The axis of discrimination is **coherence and defended judgment**, exactly the
thing a student cannot get from Claude for free.

**Where expertise is read (to survive 70 students):** judge expertise on two
decisive deliverables, the mid-season sprint (Sprint 3) and the final demo
(Sprint 5). The other sprints get formative feedback and feed the reps axis by
completion, not a careful expertise read each.

## Reps axis (measured, off the repo-analysis stat sheet)

Reps is a **measurement** problem. Use `repo-analysis/analyze.py` signals in
three bands. Never raw commit count; use cadence spread, category coverage,
artifact substance, and sprint completion. The stat sheet already emits:
`active_days`, per-category commit balance (Building, Discovery, GTM, Judgment,
Metrics, Practice log), and artifact counts (interviews, specs, experiments,
practice logs, excluding `000-` templates).

Proposed thresholds (tune these; they are the strictness dial):

- **Full reps.** All 5 sprints delivered, on time. Committed in most weeks of
  the term (cadence spread, not bunched at deadlines), e.g. active in >= 10 of
  ~14 weeks. Category balance touches at least 5 of the 7 folders with none
  trivially empty (Discovery, Building, Judgment, Metrics, and Practice log at a
  minimum). Practice-log kept regularly (e.g. >= 10 log files). Real artifact
  substance (e.g. >= 3 interviews, >= 2 specs, >= 1 GTM experiment). Positive
  peer contribution. Completed >= 8 of 10 quizzes. Took both the pre and post
  exam.
- **Partial reps.** Most deliverables in (>= 4 of 5 sprints), some late or
  missing. Bursty cadence (active in fewer distinct weeks). Some categories thin
  or empty. Practice-log sporadic. Did the work, not consistently.
- **Minimal reps.** Many deliverables missing (<= 3 sprints). Sparse or
  last-minute commits. Whole categories absent. Practice-log neglected.

Set one explicit threshold per band and publish it. This is the character and
diligence bar, and per the note above it must be strict enough that not everyone
clears Full.

## The instruments (Scott's simplified set)

Everything in the course is one of these. Peer code review, peer product
testing, and the process clip are **folded into sprints**, not separate buckets.

| Instrument | The one job | Feeds |
|---|---|---|
| **5 Sprints** (build artifacts + recorded video defense; peer review, peer testing, and the process clip fold in; Sprint 5 is the final demo) | The whole game. Expertise (ceiling) and reps (floor) | The letter |
| **10 Quizzes** | Retrieval practice, the "remember" layer, low-stakes | Reps floor (completion + good-faith attempt) |
| **Pre / Post exam** (identical or parallel form) | Measurement: learning delta + Scott's teaching mirror | Reps floor only (small baseline/effort credit); the delta is measurement, never a grade |
| **Reflect self-scout report** (optional) | Formative self-coaching on prompting | Nothing (coaching only) |
| **Claude Code Architect cert** (optional) | External credential | Nothing (optional extra credit / resume line) |

Note what this means: **neither quizzes nor the exam get an additive point
bucket that sums to a letter.** They feed the reps floor by completion and do
their real jobs (retrieval, measurement). The letter comes off the grid. That is
the anti-compression move made concrete.

### The 5 sprints

Sprints 1 to 4 build the company across the term; Sprint 5 is the final demo.
Each sprint deliverable includes:

- The build itself (artifacts committed to the company repo).
- A **recorded video** in which they demo the working thing and narrate real
  decisions, answering a specific reasoning prompt that varies by sprint ("what
  breaks if your core assumption is wrong, and what would you do"). Not a pitch,
  a defense of decisions over the working artifact.
- A **curated process clip**: one self-selected, annotated Claude Code exchange
  (their best reasoning, or where they caught the model being wrong), with a
  short note on what made it good and what they would ask differently now.
- Where relevant, a **peer activity** (review a peer's codebase, or be a test
  user for a peer's app) as a sprint task rather than its own assessment type.

Live spot-checks keep the videos honest at 70: pull a random 10 to 15 students
into a short synchronous "film review" per major deliverable. Nobody defends all
70 live, but everyone knows they might be.

### Process clip rubric (question quality, the AI-age meta-skill)

Same judgment axis as the expertise bands, made visible in process:
decomposition (breaks a fuzzy goal into tractable asks), context (gives the
model what it needs), skepticism (verifies and corrects wrong output),
iteration (steers across turns toward a goal), judgment about the tool (knows
when to trust, override, or stop).

### Pre / post exam

- **Job:** the cleanest possible learning measurement (a direct gain score) and
  a rare honest mirror on Scott's own teaching (cohort-over-cohort average
  gain). This is the strongest reason to run it.
- **Day one, "combine" framing:** "this is your season starting line, not where
  you are judged." Effort-based credit so students actually try. The pretesting
  effect is a real bonus: guessing wrong in August makes the answer stick in
  December.
- **Do not grade the delta.** Growth is self-referenced and unsound for
  certification; it would punish the student who arrived already sharp. The
  delta is measurement only.
- **Security:** the pre-test is the post-test's answer key. Use a **parallel
  form** at the end (same blueprint and difficulty, different items), or collect
  the pre and return only scores. Parallel form is the recommended trade.
- **Read the average gain as a year-over-year trend, not an absolute teaching
  score** (ceiling effects and regression to the mean distort raw deltas). And a
  fixed, mostly-recall exam only measures the knowledge layer; the expertise
  that actually spreads people still lives in the sprints and the defense.
- **Open decision:** how much, if any, does the post-exam weigh? Recommendation:
  keep it as baseline/effort credit inside the reps floor, and leave the
  letter-driving weight on the sprints.

## Transcript privacy: curation, not surveillance

Do **not** harvest student Claude Code transcripts for grades, even
project-scoped. Reasons: privacy and sensitive content, the observer effect
(grading every prompt degrades the free tool use the course depends on), and
volume. Only student-**curated** submissions (the process clip) reach Scott for
grading. Git history is fair game (Scott is a disclosed collaborator who already
analyzes it via the stat sheet); raw JSONL transcripts are not. If a formative
signal on prompting is ever wanted, it runs client-side (student runs the
analysis, only the derived report leaves their machine) and stays formative,
never a direct grade input (Goodhart, and the student can edit the output).

## Mapping the grid into Canvas (points-based LMS)

Canvas is points-based; the grid is criterion-referenced and conjunctive (not a
weighted sum), so do not try to reproduce it by summing points. Recommended:
**specifications grading plus a manual letter overlay.**

- Use Canvas assignments only for **low-stakes completion tracking**: each quiz
  (small attempt-based points), each sprint submission (complete / incomplete
  against a spec), pre and post exam (completion credit). These record the reps
  signals; they do not compute the letter.
- Track the two bands (reps: Full/Partial/Minimal; expertise:
  Excellent/Proficient/Developing/Weak) in a rubric or a separate gradebook
  column or a spreadsheet overlay fed by the stat sheet plus the two decisive
  expertise reads.
- Assign the final course letter from the grid via Canvas's manual grade
  override / grading scheme.

The `canvas-lms` skill can wire this once the bands and thresholds are locked.

## Worked examples (a student falling out of the grid)

1. **The star.** All sprints on time, cadence across the term, all folders
   touched, real discovery, decisions defended, MVP works, reasons well on the
   spot. Full reps x Excellent = **A**.
2. **The diligent grinder.** Does every rep, keeps the practice log, iterates
   honestly, but the product is coherent-not-exceptional and decisions are
   asserted more than defended. Full reps x Developing/Proficient = **B to B+**.
   Protected floor, honest about skill. This is the character reward working.
3. **The polished coaster.** Slick-looking repo, but skips practice: bunched
   last-minute commits, thin discovery, practice-log neglected, only 3 sprints
   truly delivered. Even if the artifact reads Proficient, Minimal reps x
   Proficient = **C+**. If it genuinely reaches Excellent, the cap still holds at
   **B+**. The gifted athlete does not get the MVP award for skipping practice.
4. **The disengaged.** Missing deliverables, sparse commits, no discovery, MVP
   broken. Minimal reps x Weak = **D / F**.

## The backstop

None of this holds unless Scott holds the bar: actually gives B's and C's and
defends them to students who have always gotten A's. The instruments are maybe
20% of the fix; willingness to hold the line is 80%. The published anchor
exemplars plus a one or two sentence written rationale per expertise grade
("placed at Proficient: coherent and complete, but decisions asserted rather
than evidenced, see the anchor") defuse almost every appeal in 30 seconds.

## Open decisions to stress-test

1. **"Full reps" thresholds** (the strictness dial, and the single point of
   failure). The proposed numbers above are a starting point; tune against real
   stat-sheet output once there is a roster.
2. **Post-exam weight** (recommendation: baseline/effort credit only).
3. **Canvas implementation** (specifications grading + manual overlay vs. any
   points approximation).
4. **Private target distribution** numbers (the ~25/45/rest split) to validate
   rubric headroom.
5. **Peer contribution measurement** (how peer review/testing quality is scored
   inside sprints, and whether it feeds reps, expertise, or both).
