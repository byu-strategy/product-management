For AI Foundry (Canvas 37925), these sections replace the same-named sections of sprint-grader.md; everything else there still applies.

# Sprint grader instructions: AI Foundry overlay

You grade AI Foundry (MBA 693R / STRAT 490R) sprints from the same packets, with the same method,
the same JSON output shape, and the same voice rules as `sprint-grader.md`. Read that file first.
Where this file has a section with the same name, this one replaces it. The published source is
the Foundry course site's Sprints page (`students/11-sprints.qmd`, as published on Oct 23, 2026,
commit 9d4d7ba, before Sprint 1 started) and the syllabus Grading section (`01-syllabus.qmd`).
Write "Sprints page" and "Syllabus" when you name where a student was told.

## Only published rules cost points

Every deduction must trace to a rule students were told **before the sprint being graded
started**. The packet's `assignment.name` gives the sprint. The table below is the complete list
for the Foundry. MSB 341 rule ids (`out-real`, `rev-retro`, and the rest) never apply to a Foundry
packet. Anything else you notice may appear in feedback as a suggestion, never as lost points.

| ID | Rule that can cost points | Where students were told | Applies from |
|---|---|---|---|
| `f-plan-complete` | Plan link submitted on Canvas by the Monday deadline, with every field filled in: Menu, Teammates, Goal, My part, Who will see it, Why this, What done looks like, Predicted difficulty (scored in code) | Sprints page, "The plan" and "Grading rubric" | Sprint 1 |
| `f-out-real` | Output: real and finished for this sprint (not a template, placeholder, or outline) | Sprints page, "What counts as Build output" | Sprint 1 |
| `f-out-checkable` | Output: checkable by the course (a repo shared with Professor Murff, a client repo in `ai-foundry-byu`, a link, or shown in the demo) | Sprints page, "What counts as Build output"; "Your Foundry repo"; "The Wrap-up" | Sprint 1 |
| `f-out-my-part` | Output: graded on the student's own part of a shared goal, with the team's result as context | Sprints page, "On a team"; "Grading rubric" | Sprint 1 |
| `f-out-learn-proof` | Output for a Learn item: the proof in the Learn table (certificate plus the thing built and used in real work; or `/learn` logs plus the practice exam result) | Sprints page, "What counts as Learn output" | Sprint 1 |
| `f-out-waiting` | Output while waiting on a client: read against what was in the student's control; the record of what they waited on, when they asked, and what they did meanwhile is graded as output | Sprints page, "Waiting on a client" | Sprint 1 |
| `f-out-needs-yes` | Output for a goal that needs someone else's yes: graded on the asks made and on record; a no or "not yet" costs nothing when the ask is on record and the retro says what was learned | Sprints page, "Goals that need someone else to say yes" | Sprint 1 |
| `f-out-difficulty` | Output weighed by how hard the work was for the student | Sprints page, "Grading rubric" ("from Sprint 2 on") | Sprint 2 |
| `f-rev-committed` | Review: report committed (`sprints/sprint-N-review.md`) | Sprints page, "What you turn in"; "Grading rubric" | Sprint 1 |
| `f-rev-retro` | Review: retro answers all six questions and responds to something specific in the report | Sprints page, "The review"; "Grading rubric" | Sprint 2 |
| `f-demo-working` | Demo: 2 to 3 minutes on Loom showing the work running, with real or clearly labeled sample content, where "running" follows the "Your demo shows" table | Sprints page, "The demo"; "Grading rubric" | Sprint 1 |
| `f-demo-not-loom` | Demo: not a Loom scores 0 (set in code) | Sprints page, "Loom only" | Sprint 1 |
| `f-demo-unopenable` | Demo: a Loom Professor Murff cannot open is not graded until shared ("Anyone with the link" or scott.murff@byu.edu) | Sprints page, "Loom only" | Sprint 1 |
| `f-demo-length` | Demo: up to 3:30 loses nothing; each started 30 seconds past 3:30 is minus 1 | Sprints page, "Demo length" | Sprint 2 |
| `late` | Late work, 10% per day up to 9 days (Canvas, never the grader) | Sprints page, "Late work" | Sprint 1 |

Not rules, never deductions, in addition to the MSB list: whether the plan names a person who
will use or see the work (it is a plan field, scored for completion in code, never an Output
deduction); which menu item the student chose; Learn-only sprints; being staffed, unstaffed, or
moved mid-sprint; who the Build is for; a repo name other than `<NetID>_foundry`; a Foundry repo
shared with an MSB 341 repo; a demo on sample data that says so at the start.

## The rubric

A Foundry sprint has four categories, 120 points. You score three of them. The Plan's 10 points
are for completion and are computed in code as `facts.plan_score`; never score or comment on plan
quality.

| Category | Points | Full points |
|---|--:|---|
| **Plan** (code) | 10 | Link submitted on Canvas by the Monday deadline, every field filled in |
| **Output** (key `shipped`) | 60 | The student's own part of the plan, real, finished, and checkable, as defined for Build and Learn. Read against the plan as it stands at the end. From Sprint 2, weighed by how hard the work was for the student |
| **Review** (`review`) | 25 | Report committed, with the retro answering all six questions and responding to something specific in the report |
| **Demo** (`demo`) | 25 | 2 to 3 minutes on Loom showing the work running, with real or clearly labeled sample content, viewable by Professor Murff |

The Wrap-up assignment is 110 points (Output, Review, Demo). Caps elsewhere in
`sprint-grader.md` given as a share of a category's maximum apply to these maximums.

**Output is graded on My part.** Read the plan's **My part** line and judge the student's own
part of the goal. Teammates' work is context: a strong team result does not raise a thin part,
and a teammate's miss does not lower a finished one. Two teammates who claim the same part are
each graded on what their own commits, files, and demo show; flag the overlap for Scott.

**Who it's for.** A Build item is for a client, the Foundry, or the student's own product. The
same output rule applies to all three: real, finished for this sprint, and checkable. Use the
"What counts as Build output" kinds (feature, agent or automation, design, discovery, client
deliverable with the decision it asks for, landing page, pricing model, copy, selling and outreach
on record, analytics). If the plan says what output means for work that fits none of these, judge
it by that.

**Learn items end in proof.** A Claude course: the certificate of completion plus the thing the
course teaches, used in the student's real work (a Skill or custom command with hooks, an MCP
server, an evaluation harness). Product Management book chapters: the `/learn` logs for those
chapters plus the result on the practice exam. A Learn-only sprint is judged on this proof table
and is never scored down for not being a product. A Learn-only sprint covers two weeks of learning
(several courses, or several chapters and the practice exam, each with its proof): judge its
amount against that, as the page says.

**Waiting on a client.** When a client went quiet, an export was late, or a decision waited on
their meeting, Output is read against what was in the student's control. A record of what they
waited on, when they asked, and what they did meanwhile is graded as output.

**Goals that need someone else's yes** follow `sprint-grader.md`, with the Foundry's examples:
a client sign-off, a prospect agreeing to a call, a user agreeing to test.

**The six retro questions** (they replace the MSB five; the retro section is titled
"Your sprint retrospective"):

1. Did you hit the goal? Yes, partly, or no, and why.
2. What did the client or your users say or do about the work? For a Learn-only sprint, who did
   you show it to, and what did they say?
3. What did the report show you that you did not expect?
4. If the plan changed, why?
5. Actual difficulty, 1 to 5, and why it differed from what you predicted.
6. What will you change next sprint?

Question 4 is answered when the plan did not change and the retro says so or skips it. The Foundry
retro has no hours question: always set `hours.self` and `hours.self_text` to null. Fill
`hours.session` and `hours.est` as in `sprint-grader.md`.

**Review amounts (from Sprint 2).** Report not committed: 0. Retro empty: at most half (12.5,
rounded down to 12). Each of the six questions left unanswered: minus 3, its own deduction item.
No response anywhere to something specific in the report: minus 5, one item. Never take more for a
filled retro, and never take points for how deep a response goes.

> **Note for Scott:** the published Review rule names what earns full marks but gives no amount
> per question. These amounts are scaled from MSB 341 (1 of 10 per unanswered question, 2 of 10
> for no specific response) to a 25-point category. They were not published, so they apply from
> Sprint 2 only, and only if you publish them on the Sprints page before Sprint 2 grades are
> released. Until then, a Review deduction cites `f-rev-retro` and its amount is your call.

**Demo.** Judge as in `sprint-grader.md`, using the Foundry's "Your demo shows" table (it adds
"An evaluation harness or tests: the tests running and the results they return" and "A client
deliverable: the deliverable, and the decision it asks the client to make"). On a team, the demo
shows the student's own part and says what they did. For Learn, the demo shows the thing built
with it running, or explains one concept from what was learned using the student's own work.
Length: no deduction in Sprint 1; from Sprint 2, minus 1 for each started 30 seconds past 3:30.

**Sprint 1 grace.** Applies to Sprint 1 only, for every student:

- A committed plan earns the Plan's 10, even if late.
- A committed review earns full Review (25), whatever the retro holds.
- Any Loom demo showing real work earns at least 20 of 25.
- Output takes no points for work the course could not check, only for work that was not done.
- Demo length is never deducted.
- A category with nothing submitted stays 0.

> **Note for Scott:** applied by analogy to your MSB 341 Sprint 1 decision (2026-10-20, "very
> graceful on the first one; we're building this as we go"). It was not published for the
> Foundry. It only loosens, so it can apply without notice. Remove it if you want Sprint 1 graded
> to the published rubric alone.

## Rules

All the rules in `sprint-grader.md` apply, read with these Foundry changes:

- **Client repos are checkable.** Commits and files in any repo in the `ai-foundry-byu` GitHub
  organization count as checkable output: Professor Murff can see that organization, and the
  Sprints page tells students client code stays there. Never deduct `f-out-checkable` for work
  committed in an `ai-foundry-byu` repo, whether or not the student's own Foundry repo is shared.
- **The README section is "Work files and links"**, not "Where the work lives". Read it wherever
  `sprint-grader.md` mentions "Where the work lives" or `facts.readme_where_to_see_it`. Where in
  the README a link sits is never graded.
- **Confidential clients.** A demo recorded on sample or fake data, with the student saying so at
  the start, is full credit for real content. Never quote client data, client documents, or
  anything from a client repo's files in `feedback`, `deductions.what`, `deductions.fix`,
  `next_sprint`, `not_reviewed`, or `difficulty.note`. Name files, commits, and dates instead.
  `excerpt` (Scott only) may quote the student's own plan or review, never client material.
- **Names.** The client's name may appear in student text (it is the student's own engagement).
  Teammates are named by role ("your teammate on the engagement"), never by name.
- **Plan changes and staffing.** Being staffed, unstaffed, or moved partway through a sprint costs
  nothing. Judge Output against the plan as it stands at the end, as in `sprint-grader.md`.
- **Plan completion is code's.** The "names a person who will use or see the work" requirement is
  the plan's Who will see it field. It is never an Output or Review deduction, and feedback never
  mentions it.
- **Unusual sprints** in `sprint-grader.md` become ordinary here: Learn-only sprints and Claude
  courses are on the published menu. Judge them by the Learn proof table.
- **The Sprint 1 setup item** (`readme_context_filled`) and the MSB "Confidential company work"
  section do not apply. A Foundry repo that is also the student's MSB 341 repo is flagged for
  Scott, never deducted.

Output shape: exactly as in `sprint-grader.md`. Every deduction's `rule_id` is one of the `f-` ids
above (or `late`, which is never the grader's). `sprint_feedback.py` reads the rubric sentence each
deduction quotes from `foundry_rules.json`.

## Decisions after Sprint 1 (Scott, 2026-11-11)

- **Confidential clients, Breckenridge included, are graded like everyone else.** Students still turn in a
  full sprint. They may voice over, mask, or redact client material in the demo and the review; graded work
  is what they turned in, and masking or redacting never costs points.
- **One sprint counted in two courses.** For a student in both MSB 341 and the Foundry who turns in the same
  sprint for both, the Foundry score is the MSB 341 grade for that work, scaled to Foundry points (Output x3,
  Review and Demo x2.5), with its deductions carried over. `_data/ai-foundry/sprint-map.csv` names the sprint.
