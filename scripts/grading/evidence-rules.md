# Evidence rules (shared by the grader and the concept coder, 2026-11-12)

One set of rules for what counts as evidence, read by both the Output grader (`output-rubric.md`) and
the concept coder (`concept-coder.md`). A piece of work that does not count for the grade does not
count for the builder profile, and the other way round. Where another file disagrees, this file wins.

- **The work itself.** Repo diffs and their dates; commits in the course repo, client repos
  (`ai-foundry-byu` for the Foundry) and any other repo the student shared; files; links that opened;
  Google files fetched; what is on screen in the Loom frames and transcript.
- **Written records of non-code work.** Calls, meetings, interviews, user tests, sales asks and
  outreach leave records, not diffs. A dated record of who (a name or a masked label such as
  "Customer S"), when, what was asked or tested, and what they said or did is full evidence of that
  conversation: a log, a pipeline table, a session note or a findings page, committed or listed in the
  `/sprint-review` report. A recording is not required. A conversation with no dated record anywhere
  is not checkable. For the builder profile, these records are evidence for Discovery and Launch and
  Learn concepts in the same way a commit is evidence for an Architecture concept.
- **Any repo the course can open counts, whoever owns it** (a client's own GitHub organization, a team
  repo, a repo the review calls unshared), as long as the work in it is the student's. Credit follows
  the student's commits and the review's account of who did what (Scott, 2026-11-12).
- **The student's own agent harness is the student.** Work done by an agent system the student set up
  and ran (Claude Code, or a harness built on it) is the student's work. A dated run log (date, what
  changed, the result, one line per job) counts the same as a commit list (Scott, 2026-11-12).
- **The student's own part.** On a team, credit what this student's commits, files, records and demo
  show. A teammate's work is context. Repo authorship can mislead (a teammate may commit under another
  account): rely on the review's account of who did what, checked against the commits.
- **Using a tool is practice; configuring it belongs to whoever did.** When the student's own sessions
  used a skill, subagent, hook, permission mode or MCP server on their own work (the review's
  "Builder tools you used" list), that counts as using the concept, even if a teammate set it up. The
  credit for writing or configuring it goes to whoever committed it.
- **Checkable work only.** Work nobody can open earns nothing. A sentence in the retro or README, or
  prose in the review with no commit, record or Loom moment behind it, is a claim, not evidence.
- **Unshared repos, exactly.** A repo the student did not share counts only through the
  `/sprint-review` report's list of that repo's commits, and only for commits listed one by one with
  their message (or SHA and message). A paraphrase ("built out the dashboard"), a count ("about 70
  more commits"), or a PR number with no message counts for nothing. Work shown running in the Loom
  counts whatever repo it lives in.
- **Confidential work.** Masked, redacted, sample-data or voiced-over material is full evidence.
- **This sprint's work.** Commits and records dated in the sprint window. Course-provided material
  (the course's own skills, templates, the plan and review files) never counts.
