# Output rubric: Amount and Quality (shared, v8.3, 2026-11-12)

DRAFT. One Output rubric for every course on the sprint model (MSB 341 and AI Foundry). Evidence rules
are shared with the concept coder: read `evidence-rules.md` in this folder first.

v7 (Scott, 2026-11-12): Time is out of the grade. Output is Amount and Quality only. Hours are still
collected (the `/sprint-review` time playback, the retro estimate, `sprint_records`), but only as a
cross-check for Scott, never a score and never mentioned to the student. Reasons: time could rarely be
measured (in an MSB 341 test, 1 of 6 students had session time), it scored efficient agent work below
logged hours, it invites inflated self-reports, and it split the "whose work is this" call from progress.
Slow kinds of work are protected by "judged against two weeks of the same kind" and "asks on record
count; a no costs nothing". The MSB 341 copy, `output-rubric-msb341-test.md`, uses the same wording.

v8 (merged with the MSB 341 session, strat-d8, 2026-11-12): one scale for both courses (Foundry = MSB 341
x 3, each MSB point owning three Foundry points), MSB 341 Sprint 6, course-specific lines for Judgment and
privacy, rule ids per course, a published records line, authorship in `evidence-rules.md`, and worked
examples per course.

## Points by course

| Category | MSB 341 | MSB 341 Sprint 6 | AI Foundry |
|---|---|---|---|
| Plan | 10 | 10 | 10 |
| Output: Amount + Quality | 20 (10 + 10) | 50 (25 + 25) | 60 (30 + 30) |
| Review | 10 | 20 | 25 |
| Demo | 10 | 20 | 25 |

MSB 341 Sprint 6 doubles the sprint; its Output bands are the 0-10 bands x 2.5, rounded to whole points.

**Plan.** Completion only: the GitHub link on Canvas by the deadline, every field filled in. In the
Foundry, "My part" is not required for solo work.

## Output

| Part | MSB 341 | Foundry | Measures | Never includes |
|---|---|---|---|---|
| **Amount** | 10 | 30 | How far the work moved this sprint | Hours, how good it is |
| **Quality** | 10 | 30 | How good the work is, the same bar for every student | Hours, how much there is, starting level |

Whether it was the right work is not Output (in the Foundry it is Judgment, on the Consultant side; MSB 341 does not grade it). Hours are not
Output either: see "Hours: a cross-check, never a score" below.

Published sentence:

> **Output: Amount and Quality.** Amount is how much progress you made this sprint, judged against what
> two weeks of that kind of work looks like. Quality is how well the work was done, judged on the work
> itself. Your plan says what you are aiming at; changing it when you learn something costs nothing.
> Your sprint review records your hours to help us plan the course; they never affect your grade.

Published with it, on both Sprints pages:

> **Keep a short record.** For each call, interview, test with a user, or ask, note the date, who (a name
> or a label such as Customer A), and what came of it. One line is enough, in your repo or your sprint
> review. A conversation with no record cannot be counted.

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
  When the wait is on record (the ask and its date), judge Amount against the time access existed, the
  same way as a late start.
- **Never comment on a client's or partner's process** (how they review, merge, or approve work). The
  course does not know it, so it is never part of Amount, Quality, or the feedback.
- **No privacy commentary.** Students own the records on their screens and may show them as they are or
  redact them; never flag or mention it, and it never affects a score.

## Amount (MSB 341 0 to 10, Foundry 0 to 30)

How much progress, against what a capable student does in two weeks of steady work **of the same kind**
in this course. Everything moved forward counts, from an outline or a first plan to work in use, even if
rough. For each piece, estimate how far it moved (an outline might be 10 to 20% of a write-up; a working
feature with rough edges might be 70% of it) and add the pieces up. Nothing has to be done to count.
Agents speed up building far more than talking to people: never measure a selling or research sprint
against a building sprint. A sprint that mixes kinds adds up, each part against its own kind. A
documented dead end (what was tried, what happened, what it showed) is progress. Work that is not the
student's own, or not on record, earns nothing. Never raise or lower Amount for the hours it took.

| MSB 341 | Foundry | Anchor |
|---|---|---|
| 10 | 29 to 30 | Several substantial pieces carried far: running, used, sent, or delivered |
| 8 to 9 | 23 to 28 | A solid sprint: at least one substantial piece carried well along, with smaller pieces around it |
| 7 | 20 to 22 | One piece carried well along, little else |
| 5 to 6 | 14 to 19 | Several pieces started and partway done, or one small piece done |
| 1 to 4 | 2 to 13 | Early progress only: setup, an outline, a plan, a template filled in |
| 0 | 0 to 1 | No progress that is the student's own and on record |

One scale for both courses: the Foundry is MSB 341 x 3, each MSB point owning three Foundry points (10 is
29 to 30, 9 is 26 to 28, 8 is 23 to 25, 7 is 20 to 22, 6 is 17 to 19, 5 is 14 to 16, 4 is 11 to 13, 3 is
8 to 10, 2 is 5 to 7, 1 is 2 to 4, 0 is 0 to 1).

"Running" includes a staging or test site. For Learn, a course's completion screen counts as its
certificate when the course gives none.

Score at the top of a rung when the work is close to the next rung up. A prototype is real progress when
the design is the deliverable; sample data counts for less only when the work's value depends on real
data. Goals that need someone's yes: the asks on record count, and a no costs nothing. Waiting on a
client (Foundry): the record of what was waited on, when it was asked for, and what was done meanwhile
is progress.

A solid sprint, by kind:

| Kind | A solid sprint |
|---|---|
| Feature or app | Built from data to screen, running, main error and empty cases handled |
| Agent or automation | Runs start to finish on real inputs, with checks that it does the right thing |
| Model or eval work | An eval set with expected answers, scored runs comparing changes, what the results showed |
| Interface or design | Designed and built or prototyped, checked with a person or against stated design rules |
| Go-to-market | A page or campaign live, first results read against a target |
| Cold outreach | A targeted list, a dozen or more asks on record (date, who, the answer), follow-ups, a pipeline |
| Selling to a business | Three to five conversations with people who decide or hold the budget, each recorded and followed up, with the ask made |
| Research or discovery | Five or more interviews or user tests written up, or a full analysis, with conclusions and what they change |
| Client deliverable (Foundry) | A deliverable the client can act on, with the decision it asks for |
| Learn | A Claude course with its certificate and the thing it teaches used on real work, or chapters with /learn logs and the practice exam |

## Quality (MSB 341 0 to 10, Foundry 0 to 30)

How good the work is, judged on the work itself, with the same bar for every student. Never adjust for
starting level, and never for how much of the thinking was the student's (that is the builder profile's
depth level, not the grade). Judge how good, never how long it took. Four questions:

1. **Does it work, and is it correct?** It runs, the numbers are right, the conclusion follows from the evidence.
2. **Does it hold up?** Real content, the cases beyond the easy path, errors handled.
3. **Is it fit for the person it is for?** It does what they need, and it is clear to use or read.
4. **Is it well made?** Organized, consistent, sourced, easy for the next person to pick up.

| MSB 341 | Foundry | Anchor |
|---|---|---|
| 10 | 29 to 30 | Excellent: works and is correct, holds up well beyond the easy path, clearly fit for its person, well made |
| 9 | 26 to 28 | Strong: works and holds up with real content; fit for its person; a few gaps a reviewer would point out |
| 7 to 8 | 20 to 25 | Sound: works on the main path with real content; rough beyond it, or unclear in places |
| 5 to 6 | 14 to 19 | Uneven: partly works or partly correct; notable gaps in how it holds up or how clear it is |
| 1 to 4 | 2 to 13 | It does not hold up: breaks, wrong, placeholder content, or did not run |

Score at the top of a rung when the work is close to the next one. With several pieces, weight Quality
toward the pieces that carry most of the progress. When something outside the student's control blocks
the work (an access token, an approval), judge what runs up to the block, with the block named and on
record. A missing piece is Amount, never Quality.

What quality means, by kind: a feature has correct behavior, error and empty states, real data, access
rules right, tests where it matters; an agent has correct outputs on real inputs, measured, with sensible
failure handling; evals have right expected answers and conclusions that follow from the scores; design
is usable, consistent and accessible; research has a sound method, quoted evidence and stated limits;
outreach and selling are well targeted, with a clear specific ask and follow-up; go-to-market has a clear
message for a defined audience and tracking that records correctly; a client deliverable answers the
client's actual question, clearly, backed by evidence; Learn means the thing built works on real work.

## Never counted against a student (Scott's rulings, 2026-11-11 to 12)

Neither Amount nor Quality, nor any reason, raise, or deduction, may rest on:

- **The plan's items as a checklist.** Never tally done items against the plan; judge the work done.
- **Work on a project the student was moved off,** or a pivot. Judge the work they did.
- **Teaching or onboarding a teammate away from the repo.** It counts neither way.
- **A client's or partner's process** (reviews, pull requests, merges, approvals, tickets).
- **A wait for access or a client,** beyond the waiting rule above.
- **Privacy.**
- **In Quality:** a missing or planned piece, work not yet used by anyone, work not yet shared or
  checkable, or how much there is. Those are Amount questions (or no question at all). Quality judges
  only the work that is there: does it work, hold up, fit its person, and is it well made.

## Hours: a cross-check, never a score

Read the review's "Active session time" (or the time playback, once it exists) and the retro's hours
estimate, and compare them with Amount. Record what you found in `hours_crosscheck` and flag a mismatch
for Scott (for example, 50 hours reported with little on record, or a large amount of work in one short
session). Never move Amount or Quality for hours, and never mention hours to the student.

## What the student sees, and the result fields

The Output total; Amount and Quality each with one sentence on what the score rests on and one concrete
thing that would raise it; one Dispute button per part.

In the result: `scores.shipped` = Amount + Quality; `output_parts` = {`amount`, `quality`}, each
{`score`, `reason`, `raise`}; one `deductions` item per part below its maximum (`O1` Amount,
`O2` Quality; rule ids `out-amount` and `out-quality` in MSB 341, `f-out-amount` and `f-out-quality` in
the Foundry), `points` = the shortfall, `what` = its `reason`, `fix` =
its `raise`. There is no Time item.

## Where a Foundry Wrap-up lands (Review and Demo earned)

Derived from the v8 bands (Output = Amount + Quality, each 0 to 30; Wrap-up = Output + 50).

| Sprint | Amount | Quality | Output of 60 | Wrap-up of 110 |
|---|---|---|---|---|
| Excellent | 29 to 30 | 29 to 30 | 58 to 60 | 98 to 100% |
| Solid, strong work | 23 to 28 | 26 to 28 | 49 to 56 | 90 to 96% |
| Solid, sound work | 23 to 28 | 20 to 25 | 43 to 53 | 85 to 94% |
| One piece carried well along, sound | 20 to 22 | 20 to 25 | 40 to 47 | 82 to 88% |
| Partway, uneven | 14 to 19 | 14 to 19 | 28 to 38 | 71 to 80% |
| Early progress only | 2 to 13 | 2 to 19 | 4 to 32 | 49 to 75% |

## Worked examples

Each course tests only on students not described in its own list.

### MSB 341 (Sprints 3 and 4; Amount and Quality on 10)

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

### AI Foundry (Amount and Quality on 30; invented, for calibration)

- Client deliverable, solid (Amount 26, Quality 27): a pricing analysis for a regional clinic group, built
  on two years of their visit data, with three options costed and the decision it asks the owner to make;
  presented to the owner and sent with the data appendix.
- Client feature, waiting on the client (Amount 20, Quality 23): an intake form and its routing rules
  built and tested on 40 sample forms; the client's API key, requested in writing on day 3 and again on
  day 8, never came, so live routing could not run; meanwhile a test plan and a fallback for scanned forms.
- Agent harness, solid (Amount 27, Quality 22): an agent harness the student set up ran 14 dated jobs on
  their own product (each logged with what changed and the result), 11 landed in production; three
  stuck jobs are written up with why.
- Learn, solid (Amount 23, Quality 23): two Claude courses with certificates, and an MCP server from the
  second used on the team's client repo for a week, with the queries it answered.
- Learn, thin (Amount 8, Quality 8): one course certificate; the skill it teaches was written but never
  committed or run.
- Selling for the Foundry, solid (Amount 24, Quality 26): nine asks to prospective clients, each with
  date, role and answer; two agreed to scoping calls, held and written up.

