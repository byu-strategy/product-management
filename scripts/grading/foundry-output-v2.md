# AI Foundry Output: Amount and Quality (draft v2.1, 2026-11-11)

DRAFT for Scott's review. Not used by any grader yet. When approved, it replaces "Output" in
`sprint-grader-foundry.md`, and the Sprints page gets the published sentences at the end.

v2.1 (after the first calibration test, 4 students, 2 blind runs): lower bands raised so one
finished, working piece lands near 75% of the Wrap-up and a certificate or drafts alone near 60 to
65%; the unshared-repo evidence rule made exact (it caused the one disagreement between runs);
worked examples replaced with invented ones (the first set described tested students and anchored
the graders).

## What Output is

Output is 60 points in two parts, each 0 to 30:

- **Amount**: how much real, finished work exists now that did not two weeks ago.
- **Quality**: how hard the work was for this student, and how well it was done.

The plan is context, not the yardstick. It tells you what the student was aiming at, who the work
is for, and which part is theirs. A pivot costs nothing: judge the work that was done, before and
after the change. Never score against "Done looks like" as a checklist.

## What to judge from

- **The work itself.** Repo diffs and their dates, commits in `ai-foundry-byu` client repos and
  any other shared repo, files, links that opened, Google files fetched, and what the Loom frames
  and transcript show on screen.
- **The student's own part.** On a team, credit what this student's commits, files and demo show.
  A teammate's work is context. Repo authorship can mislead (a teammate may commit under another
  account): rely on the review's account of who did what, checked against the commits.
- **Checkable work only.** Work nobody can open earns nothing in either part. Say in
  `not_reviewed` what would make it checkable.
- **Unshared repos, exactly.** A repo the student did not share counts only through the
  `/sprint-review` report's list of that repo's commits, and only for commits listed one by one
  with their message (or SHA and message). A paraphrase ("built out the dashboard"), a count ("about
  70 more commits"), or a PR number with no message counts for nothing. Work shown running in the
  Loom counts whatever repo it lives in.
- **Confidential work.** Masked, redacted, sample-data, or voiced-over demos are full evidence of
  the work. Never mark them down.
- **A late start.** When the plan's first commit or the enrollment date shows the student had less
  than the full two weeks, judge Amount against the time they had and flag it for Scott.

## Amount (0 to 30)

How much real, finished work for two weeks, judged against what a capable student produces in
two weeks of steady work in this course. Not against the plan, and not against classmates.

| Score | Anchor |
|---|---|
| 27 to 30 | A large amount: several substantial pieces finished, well beyond a solid sprint |
| 21 to 26 | A solid sprint: at least one substantial piece finished, with smaller pieces around it |
| 15 to 20 | One finished, working piece of real size, and little else: thin for two weeks |
| 8 to 14 | Something finished but small (a certificate, a short write-up, one page), or real work left mostly as drafts or setup |
| 1 to 7 | A first step only: setup, a template filled in, an outline |
| 0 | Nothing new and checkable |

What a solid sprint (21 to 26) looks like, by kind of work:

| Kind | A solid sprint |
|---|---|
| Feature or app | A feature built through from data to screen, running or deployed, with its main error and empty cases handled |
| Agent or automation | It runs start to finish on real inputs, with its instructions, and checks or tests that it does the right thing |
| Go-to-market | A page or campaign live, and the first results measured (visits, sign-ups, replies) |
| Sales and outreach | A targeted list, a dozen or more asks sent and recorded (who, when, what was asked, the answer), follow-ups, a pipeline |
| Research or discovery | Several interviews or a full analysis, written up, with conclusions and what they change |
| Client deliverable | A complete deliverable the client can act on, with the decision it asks for |
| Learn | A Claude course with its certificate, and the thing it teaches built and used in real work. A Learn-only sprint covers two weeks: several courses, or chapters with /learn logs and the practice exam |

Worked examples (invented, for calibration only):
- **About 28:** a booking app for a tutoring business moved from sign-up to paid booking, deployed,
  with reminders by text and an admin view; plus a pricing page tested with two prices.
- **About 23:** an intake agent for a clinic that reads a referral form and drafts a routing
  decision, running on 40 real forms with an evaluation set; nothing else.
- **About 17:** one finished, working calculator page that turns a client's spreadsheet into a
  form; no other work finished.
- **About 11:** one course certificate and notes, with the thing it teaches started but not
  working.
- **About 4:** a repo set up from the template and a plan.

## Quality (0 to 30)

How hard the work was for this student, and how well it was done. Judge difficulty against the
student's builder profile (`baseline` and earlier rings): the same work is harder for a beginner
than for a strong builder. The student's own difficulty rating is context, never the answer. With
no baseline, judge difficulty from the work and the review's account, and say so in `reason`.

| Score | Anchor |
|---|---|
| 27 to 30 | Hard for this student and done well: real choices made and recorded with reasons, real problems found and fixed, holds up with real content. Usually shown in use: a client, a user, a teammate, or the student on real work |
| 21 to 26 | Decided: at least one real choice between options with a stated reason, or a problem found and fixed with a judgment about the product. Works with real content. New ground for this student |
| 15 to 20 | Directed: the student said specifically what to build and checked that it works, mostly within what they already knew, or with rough edges left |
| 8 to 14 | Followed, and it works: a template, a tutorial, or the agent's defaults, with little shaping by the student |
| 1 to 7 | It does not hold up: breaks on screen, placeholder content, or did not run |

These match `depth-levels.md` (Followed, Directed, Decided, Delivered) so the score and the
builder profile describe the same work. "In use" is evidence for the top band, never a requirement:
a sprint whose work is not used yet (infrastructure, early discovery, mid-course Learn) can still
reach 21 to 26.

By kind of work, what raises Quality: for outreach, asks aimed at the right people with a reason,
and replies acted on; for research, conclusions that change what gets built, recorded as a
decision; for go-to-market, a choice of channel or message tested against an alternative; for
Learn, the thing built and used on real work, or a concept explained with the student's own work.

## Where scores land (with Review 25 and Demo 25 earned)

| Sprint | Output | Wrap-up of 110 |
|---|---|---|
| Large and hard, done well | 54 to 60 | 104 to 110 (95%+) |
| Solid sprint, real decisions | 42 to 52 | 92 to 102 (84 to 93%) |
| One finished working piece, directed | 30 to 40 | 80 to 90 (73 to 82%) |
| A certificate or drafts | 16 to 28 | 66 to 78 (60 to 71%) |
| Nothing checkable | 0 | 50 or less |

## Effort and hours: a cross-check, never a score

Rate `effort_review` as before (effort and progress, 1 to 5) and fill `hours`. Compare them with
Amount. Flag a mismatch for Scott in `flags` (for example, 50 hours reported with little checkable
work, or a large amount of work in one short session). Never move a score for hours alone, and
never mention hours or effort to the student.

## Output in the result

- `scores.shipped` = Amount + Quality.
- `output_parts`: `{"amount": {"score", "reason", "raise"}, "quality": {"score", "reason", "raise"}}`.
  `reason` is one sentence the student reads on what the score rests on; `raise` is one concrete
  thing that would raise that part next sprint. Same voice rules as `feedback`.
- `deductions` for Output: at most two items, one per part, `O1` for Amount (`rule_id`
  `f-out-amount`) and `O2` for Quality (`f-out-quality`), each with `points` = 30 minus the
  part's score, `what` = the part's `reason`, `fix` = its `raise`. A full part has no item. This
  keeps one Dispute button per part.

## Published sentences (Sprints page, "Grading rubric", Output row)

> **Output (60): Amount (30) and Quality (30).** Amount is how much real, finished work you made
> this sprint. Quality is how hard the work was for you and how well it was done: decisions you made
> and recorded, problems you found and fixed, and work that holds up with real content or is in use.
> Your plan says what you are aiming at; changing it when you learn something costs nothing.
