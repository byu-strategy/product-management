# How everything a student reads is written

Applies to every word that reaches a student's sprint report: grader feedback, reasons shown to
the student, next steps, the coder's `did`, `why` and `what`, the report template's own text, and
the sprint coach. The same rule governs the course book (CLAUDE.md, "Writing in the course books").

**No mannered prose.** Mannered prose substitutes metaphor and flourish for direct statement.
Instead of "a parameter worth varying," the mannered writer produces "a dial worth turning."
Instead of "this point still matters," they write "this point earns its keep." The phrases exist
to display the writer, not to convey the idea, and readers can tell. That is why mannered prose
irritates: it makes the reader work harder so the writer can perform. It is also imprecise.
Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say
what you mean. When a literal phrase is available, use it.

In a report that means: "most commits came on Oct 10", not "the work was bunched"; "the plan says it
is deployed", not "it shows it landing"; "the demo shows the saved job reloading", not "the demo
nails it"; "this is the step that adds the most points", not "this is where the money is". Terms of
art the book teaches (North Star metric, happy path, Mom Test) are literal names, not flourish.

The other rules, unchanged:
- Second person ("you"), plain and specific to the student's own work. Facts, no praise.
- No em dashes. No "not X, but Y" antithesis. No hype.
- Never mention lateness, the setup items, or how the work was read (packet, frames, transcript,
  coder, grader, model, AI, session scan, "it appears", "the video shows").
- Never tie the September survey to difficulty.

Before reports are built, every student-facing sentence is checked against this file (step 3b of
`/grade-sprint`), and `sprint_feedback.py` refuses to build when it finds a stock figure of speech.
