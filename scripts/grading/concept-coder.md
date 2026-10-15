# Concept coder: breadth and depth from one sprint's work (instructions for every coder)

You read one student's sprint packet and record two things: which builder concepts show up in the
student's own work this sprint (breadth), and how the student worked on each axis the sprint
touched (depth). You are not grading: nothing you record changes a score. Two coders do this
independently for every student; a concept counts only when both of you record it, and depth
uses the lower of your two levels. Record only what the packet lets a reader verify.

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
- **This sprint only:** commits in the window (on or before the due date) and this sprint's Loom.
  Work copied in from before the course does not count. In a shared repo, credit follows the commit
  author.
- **Course-provided material never counts:** the course's skills (sprint-plan, sprint-review, learn,
  eli5), template files, and the sprint plan and review files themselves.
- **One piece of work may show several concepts** only when it matches each concept's sentence on its
  own.
- A claim made only in the retro or the review report does not count.

## Depth
For each axis the sprint's work touched, assign one level from `depth-levels.md`, judged from all
the evidence together. Give the one or two pieces of evidence that decided it, and if you hesitated
between two levels, name the lower one as your level and say what would have settled it.

## Writing
`did` and `why` are written to the student: second person, plain, literal, specific to their work,
no figures of speech, no em dashes ("You added a migration that creates a jobs table, and the app
saves new jobs to it.").

## Output (exactly this JSON, one file per student per sprint)

```json
{"net_id": "", "sprint": 2, "coder": "A",
 "breadth": [{"concept": "AA10", "when": "2026-10-08", "did": "...",
              "evidence": "short description a reader can check",
              "ref": "commit sha (7 characters), file path, URL, or Loom m:ss"}],
 "depth": [{"axis": "Application Architecture", "level": 2, "why": "...",
            "evidence": ["commit 4f1e2ab: migration and test", "Loom 0:42: saves a job"],
            "unsure": "what would have settled a higher level, or empty"}],
 "seen_not_counted": [{"concept": "DI01", "what": "", "why": "e.g. described only in the retro"}]}
```

`when` is the date of the commit or Loom that shows it. Use a commit sha for anything in a repo.
