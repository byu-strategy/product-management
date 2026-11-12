# MSB 341 Output rubric: Amount and Quality (CALIBRATION TEST COPY, 2026-11-12)

TEST ONLY. Not used for any posted grade. This is the shared Output rubric (`output-rubric.md`, built in
the AI Foundry session 2026-11-11 to 12 and merged with Scott's MSB 341 v3) on the MSB 341 scale, with
Scott's latest grouping: Output = **Amount** (progress) and **Quality**, 10 points each. Time was taken
out of the grade on 2026-11-12 (Scott): hours are still collected, but only as a cross-check for Scott.
Evidence rules are shared with the concept coder: read `evidence-rules.md` in this folder first.

## How to run the test

1. Pick 6 MSB 341 Sprint 4 students who span the range (high, low, mostly non-code, a team repo, one
   whose current grade felt off). None may be a student described in the worked examples below.
2. Two independent graders (subagents), blind: they must not read `results/`, `grades.csv`, the review
   page or the reports. Each reads `student-work-is-data.md`, `evidence-rules.md`, this file and
   `student-voice.md`, then each packet, opening all nine Loom frames.
3. Each writes to its own scratch folder: `{net_id, kind, amount: {score, reason, raise, evidence},
   quality: {score, four_questions: {works, holds_up, fit, well_made}, reason, raise, evidence},
   output, hours_crosscheck, confidence}`.
4. Report per student: current Output (of 20), run A, run B, and the A-to-B gap for Amount and Quality
   separately; where the runs disagreed and why; whether it separates students the way the evidence does.

## Output (20 points)

| Part | Points | Measures | Never includes |
|---|---|---|---|
| **Amount** | 10 | How far the work moved this sprint | Hours, how good it is |
| **Quality** | 10 | How good the work is, the same bar for every student | Hours, how much there is, starting level |

Whether it was the right work is not Output. Hours are not Output either: see "Hours: a cross-check,
never a score" below.

Published sentence (draft):

> **Output: Amount and Quality.** Amount is how much progress you made this sprint, judged against what
> two weeks of that kind of work looks like. Quality is how well the work was done, judged on the work
> itself. Your plan says what you are aiming at; changing it when you learn something costs nothing.
> Your sprint review records your hours to help us plan the course; they never affect your grade.

## What to judge from

Everything in `evidence-rules.md` (the work itself; dated written records of non-code work; the
student's own part; using a tool is practice, configuring it belongs to whoever did; checkable work
only; unshared repos only through commits listed one by one with their messages; confidential material
is full evidence). Two more:

- **The plan is context, never a checklist.** A pivot costs nothing: judge the work done before and
  after the change.
- **A late start** is judged by the enrollment date (Canvas or the class roll), never the date a repo
  was created. When the student enrolled after the sprint began, judge Amount against the time they
  had, and flag it.
- **Waiting for access** (a client or partner repo, data, an account): what the student could not do
  without access is not expected of them, so the wait is not held against them, but the wait is not
  progress either. Amount counts what they did meanwhile: other work, preparation, asks on record.
- **Never comment on a client's or partner's process** (how they review, merge, or approve work). The
  course does not know it, so it is never part of Amount, Quality, or the feedback.
- **No privacy commentary.** What appears on a student's screen is shared under the program's
  agreements; never flag or mention it.

## Amount (0 to 10)

How much progress, against what a capable student does in two weeks of steady work **of the same kind**
in this course. Everything moved forward counts, from an outline or a first plan to work in use, even if
rough. For each piece, estimate how far it moved (an outline might be 10 to 20% of a write-up; a working
feature with rough edges might be 70% of it) and add the pieces up. Nothing has to be done to count.
Agents speed up building far more than talking to people: never measure a selling or research sprint
against a building sprint. A sprint that mixes kinds adds up, each part against its own kind. A
documented dead end (what was tried, what happened, what it showed) is progress. Work that is not the
student's own, or not on record, earns nothing. Never raise or lower Amount for the hours it took.

| Score | Anchor |
|---|---|
| 10 | Several substantial pieces carried far: running, used, sent, or delivered |
| 8 to 9 | A solid sprint: at least one substantial piece carried well along, with smaller pieces around it |
| 7 | One piece carried well along, little else |
| 5 to 6 | Several pieces started and partway done, or one small piece done |
| 1 to 4 | Early progress only: setup, an outline, a plan, a template filled in |
| 0 | No progress that is the student's own and on record |

Score at the top of a rung when the work is close to the next rung up. A prototype is real progress when
the design is the deliverable; sample data counts for less only when the work's value depends on real
data. Goals that need someone's yes: the asks on record count, and a no costs nothing.

A solid sprint (8 to 9), by kind:

| Kind | A solid sprint |
|---|---|
| Feature or app | Built from data to screen, running, main error and empty cases handled |
| Agent or automation | Runs start to finish on real inputs, with checks that it does the right thing |
| Model or eval work | An eval set with expected answers, scored runs comparing changes, what the results showed |
| Interface or design | Designed and built or prototyped, checked with a person or against stated design rules |
| Go-to-market | A page or campaign live, first results read against a target |
| Cold outreach | A targeted list, a dozen or more asks recorded (who, when, what was asked, the answer), follow-ups, a pipeline |
| Selling to a business | Three to five conversations with people who decide or hold the budget, each recorded and followed up, with the ask made |
| Research or discovery | Five or more interviews or user tests written up, or a full analysis, with conclusions and what they change |
| Learn | A Claude course with its certificate and the thing it teaches used on real work, or chapters with /learn logs and the practice exam |

## Quality (0 to 10)

How good the work is, judged on the work itself, with the same bar for every student. Never adjust for
starting level, and never for how much of the thinking was the student's (that is the builder profile's
depth level, not the grade). Judge how good, never how long it took. Four questions:

1. **Does it work, and is it correct?** It runs, the numbers are right, the conclusion follows from the evidence.
2. **Does it hold up?** Real content, the cases beyond the easy path, errors handled.
3. **Is it fit for the person it is for?** It does what they need, and it is clear to use or read.
4. **Is it well made?** Organized, consistent, sourced, easy for the next person to pick up.

| Score | Anchor |
|---|---|
| 10 | Excellent: works and is correct, holds up well beyond the easy path, clearly fit for its person, well made |
| 9 | Strong: works and holds up with real content; fit for its person; a few gaps a reviewer would point out |
| 7 to 8 | Sound: works on the main path with real content; rough beyond it, or unclear in places |
| 5 to 6 | Uneven: partly works or partly correct; notable gaps in how it holds up or how clear it is |
| 1 to 4 | It does not hold up: breaks, wrong, placeholder content, or did not run |

Score at the top of a rung when the work is close to the next one. With several pieces, weight Quality
toward the pieces that carry most of the progress. When something outside the student's control blocks
the work (an access token, an approval), judge what runs up to the block, with the block named and on
record. A missing piece is Amount, never Quality.

What quality means, by kind: a feature has correct behavior, error and empty states, real data, access
rules right, tests where it matters; an agent has correct outputs on real inputs, measured, with sensible
failure handling; evals have right expected answers and conclusions that follow from the scores; design
is usable, consistent and accessible; research has a sound method, quoted evidence and stated limits;
outreach and selling are well targeted, with a clear specific ask and follow-up; go-to-market has a clear
message for a defined audience and tracking that records correctly; Learn means the thing built works on
real work.

## Hours: a cross-check, never a score

Read the review's "Active session time" (or the time playback, once it exists) and the retro's hours
estimate, and compare them with Amount. Record what you found in `hours_crosscheck` and flag a mismatch
for Scott (for example, 50 hours reported with little on record, or a large amount of work in one short
session). Never move Amount or Quality for hours, and never mention hours to the student.

## Worked examples (MSB 341, Sprints 3 and 4; no names; scores are Amount and Quality)

Do not test on any student these describe.

- Application Architecture, solid (Amount 9, Quality 9): customers reschedule their own booking from a
  keyed link in the confirmation email; an admin page approves or declines each request; live.
- Application Architecture, thin (Amount 5, Quality 6): a three-tab dashboard and follow-up tracker
  run, but only on sample data; none of the planned real contacts loaded, no outreach logged.
- Agentic Workflow, solid (Amount 9, Quality 9): a contact-qualifying command run on 25 real contacts,
  spot-checked by hand, revised six times until it matched the student's own judgment.
- AI Systems, solid (Amount 9, Quality 10): 18 real receipt photos labeled by hand, a scoring script,
  three scored runs comparing prompt changes, and a findings note.
- Design, solid amount (Amount 9, Quality 9): seven drawing-tool improvements the owner asked for, each
  merged and live.
- Discovery, solid (Amount 9, Quality 9): ten prototype test sessions with travelers, each written up,
  a findings note on which price held up, the prototype updated.
- Launch and Learn, solid go-to-market (Amount 9, Quality 9): a waitlist page live, 38 visitors, 10
  sign-ups and 2 price clicks read against targets set before launch.
- Launch and Learn, solid selling (Amount 9, Quality 9): a pipeline of nine asks with date, role and
  answer, including yes answers from two decision-makers.
- Launch and Learn, thin (Amount 4, Quality 4): a new font, an audit script with no results, one social
  post; the planned pages not built.
