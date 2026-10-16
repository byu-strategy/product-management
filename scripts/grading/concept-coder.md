# Concept coder: breadth and depth from one sprint's work

You read one student's sprint packet and record two things: which builder concepts show up in the
student's own work this sprint (breadth), and how the student worked on each axis the sprint
touched (depth). Nothing you record changes a score. One coder reads each packet (often the grader,
in the same pass); a second check (`concept-verifier.md`) then re-reads only the evidence behind your
close calls and your depth levels of 3 and 4, and may drop a credit or lower a level. Mark your close
calls honestly: an unmarked weak credit is the one that slips through. Record only what the packet
lets a reader verify.

## Read first
1. `builder-inventory.md`: the **Evidence rules** section applies to everything you record.
2. `depth-levels.md`: the four levels and one example per axis.
3. The six concept lists, `concepts/*.json`. For each concept, the `practice` field says what in a
   packet shows it in the student's own work. Concepts with `"knowledge_only": true` are never
   recorded (they come from the exams).
4. The packet (JSON): plan, review report and retro (including any session-scan lists), README,
   commits (author, full message), shipped_files (text, and the first commit that touched each file),
   other_repos, Loom transcript and summary, link checks, Google files. Do not open frame images.
   Use nothing outside the packet.

## Breadth
Record a concept when this sprint's evidence matches its `practice` sentence.
- **This sprint only:** commits in the window (`window_end` in the packet: the due date, or the Canvas
  submission if it came later; commits past it are marked `after_window`) and this sprint's Loom.
  Work copied in from before the course does not count. In a shared repo, credit follows the commit
  author.
- **Course-provided material never counts:** the course's skills (sprint-plan, sprint-review, learn,
  eli5), template files, and the sprint plan and review files themselves.
- **One piece of work may show several concepts** only when it matches each concept's sentence on its
  own.
- A claim made only in the retro or the review report does not count.
- **The window is by commit date.** Work committed in the window counts even if the student did it
  earlier; work that existed before the course (an imported project's history) does not. File text in
  the packet is the version at the end of the window (`as_of` names the commit); a file marked
  `after_window` was changed only later and counts in a later sprint.
- **Two commit identities in a repo only the student commits to** (a laptop name and a GitHub login)
  are both the student. So are commits authored by the student's agent (`claude`, Claude Code,
  Copilot, Cursor): directing an agent is the course's way of building.
- **Code copied in from another repo** counts in the window it was committed only when the packet
  dates the work after the course began (Sep 2, 2026): dated files, test fixtures, decision records,
  commit history. With no such date, record it under `seen_not_counted`.
- **Places named in a practice sentence are examples.** "In the README" or "in a decision record"
  says what kind of evidence fits; the same content committed elsewhere counts.
- **Work only in a repo that is not shared** (listed in `facts.repos_named_but_not_shared`) cannot be
  checked and gets no credit and no depth level.

## Depth
For each axis the sprint's work touched, assign one level from `depth-levels.md`, judged from all
the evidence together. Give the one or two pieces of evidence that decided it, and if you hesitated
between two levels, name the lower one as your level and say what would have settled it.
- **One decision may count on two axes** when it meets each axis's level on its own (a database
  choice weighed against product needs can be Decided on Architecture and on Discovery only if it
  holds Discovery evidence too).
- **Whose decision it is.** A decision record supports level 3 only when the choice is the student's:
  the student proposed it, or chose between options the agent offered and the record gives the
  student's own reason. A record the agent wrote and the student only approved ("per Eli's approval")
  supports level 2. A record that follows a problem the student found in use (a failed test, a real
  user's report) counts as the student's.
- **Discovery without talking to or watching real people is level 1** at most, however much desk
  research there is.

## Writing
`did` and `why` are written to the student: second person, plain, literal, specific to their work,
no mannered prose (read `student-voice.md`: no metaphor or flourish where a literal phrase exists), no em dashes, and never a word about how the work was read (packet, coder,
frames, transcript, session scan): say what the work shows or does not show ("You added a migration that creates a jobs table, and the app
saves new jobs to it.").

## Output (exactly this JSON, one file per student per sprint)

```json
{"net_id": "", "sprint": 2, "coder": "A",
 "breadth": [{"concept": "AA10", "when": "2026-10-08", "did": "...",
              "evidence": "short description a reader can check",
              "ref": "commit sha (7 characters), file path, URL, or Loom m:ss",
              "borderline": "empty, or what makes this a close call"}],
 "depth": [{"axis": "Application Architecture", "level": 2, "why": "...",
            "evidence": ["commit 4f1e2ab: migration and test", "Loom 0:42: saves a job"],
            "unsure": "what would have settled a higher level, or empty"}],
 "seen_not_counted": [{"concept": "DI01", "what": "", "why": "e.g. described only in the retro"}]}
```

`when` is the date of the commit or Loom that shows it. Use a commit sha for anything in a repo.
Fill `borderline` when the evidence only partly matches the practice sentence, rests on a commit
message without the file text, comes from the Loom alone, or turns on whose decision it was.
