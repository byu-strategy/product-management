# Evidence rules (shared by the grader and the concept coder, 2026-11-12)

One set of rules for what counts as evidence, read by both the Output grader (`output-rubric.md`) and
the concept coder (`concept-coder.md`). A piece of work that does not count for the grade does not
count for the builder profile, and the other way round. Where another file disagrees, this file wins.

- **The work itself.** Repo diffs and their dates; commits in the course repo, client repos
  (`ai-foundry-byu` for the Foundry) and any other repo the student shared; files; links that opened;
  Google files fetched; what is on screen in the Loom frames and transcript. A dated record shown legibly in
  the Loom counts as on record, and a document shown in the Loom counts as of the Loom's recording date.
- **A run is not output.** The session scan shows that something ran. A run whose results are not kept
  (committed, saved, or shown on screen) earns no Amount; the scan is evidence of practice for the builder
  profile only.
- **Written records of non-code work.** Calls, meetings, interviews, user tests, sales asks and
  outreach leave records, not diffs. A short dated note of when, with whom (a name or a label such as
  "Customer S"), and what came of it is full evidence of that conversation; one line per conversation is
  enough: a log, a pipeline row, a session note or a findings page, committed, listed in the
  `/sprint-review` report, or shown legibly in the Loom. A recording is not required. A conversation with no dated record anywhere
  is not checkable. A file name alone (a meeting transcript listed in a folder) is not a record: it
  does not say what came of the conversation. For the builder profile, these records are evidence for Discovery and Launch and
  Learn concepts in the same way a commit is evidence for an Architecture concept.
- **Any repo the course can open counts, whoever owns it** (a client's own GitHub organization, a team
  repo, a repo the review calls unshared), as long as the work in it is the student's. Credit follows
  the student's commits and the review's account of who did what (Scott, 2026-11-12).
- **The student's own agent harness is the student.** Work done by an agent system the student set up
  and ran (Claude Code, or a harness built on it) is the student's work. A dated run log (date, what
  changed, the result, one line per job) counts the same as a commit list (Scott, 2026-11-12). This holds in
  an unshared repo too: a dated run log from the student's own harness counts there, where a bare list of
  commit counts or paraphrases does not.
- **The student's own part.** On a team, credit what this student's commits, files, records and demo
  show. A teammate's work is context. Commits count as the student's when the student authored them, or
  when the review shows the student's own sessions producing them; a commit under a teammate's account
  counts when the review says it is the student's and the sessions back it up. Commits by the student's
  own agent or agent harness are the student's; by a teammate's agent, the teammate's. Repo authorship
  alone can mislead; neither the account name nor the review's word alone settles it.
- **Using a tool is practice; configuring it belongs to whoever did.** When the student's own sessions
  used a skill, subagent, hook, permission mode or MCP server on their own work (the review's
  "Builder tools you used" list), that counts as using the concept, even if a teammate set it up. The
  credit for writing or configuring it goes to whoever committed it.
- **Checkable work only.** Work nobody can open earns nothing. A sentence in the retro or README, or
  prose in the review with no commit, record or Loom moment behind it, is a claim, not evidence.
- **Unshared repos, exactly.** A repo the student did not share counts only through the
  `/sprint-review` report's list of that repo's commits, and only for commits listed one by one with
  their message (or SHA and message). A pull request listed with its number and its title or a one-line description of what it did counts like a commit listed with its message (Scott, 2026-11-12). A paraphrase ("built out the dashboard"), a paraphrase of several PRs, a range ("#13 to #37"), a count ("about 70 more commits"), or a bare number counts for nothing. Work shown running in the Loom
  counts whatever repo it lives in.
- **Confidential work.** Masked, redacted, sample-data or voiced-over material is full evidence.
- **This sprint's work.** Commits and records dated in the sprint window. The window starts on the
  sprint's first day (Foundry Sprint 1: Oct 23), not at the plan commit, and ends at the due date, or at
  the Canvas submission when that came later (Canvas applies the late penalty; graders never do). Course-provided material
  (the course's own skills, templates, the plan and review files) never counts.
