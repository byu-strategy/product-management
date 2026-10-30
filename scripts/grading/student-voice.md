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

**Help them find the way forward (Scott, 2026-10-20).** Every lost point and every question a
student asks gets a concrete, workable path, not only the reason. Think about their situation and
look for a solution that fits it: what exactly to click, open, commit or show, and how to do it
within their constraints (sensitive data, a teammate's repo, a private video, a pivot). When their
constraint is real, solve around it ("open one note with the names blurred using Loom's blur tool")
instead of restating the rule. Where more than one path works, offer two. Explore what they might
have meant or tried before concluding they did not do it, and ask when the evidence is unclear.
This applies to report feedback, next steps, the sprint coach, and replies to grade questions.

The other rules, unchanged:
- Second person ("you"), plain and specific to the student's own work. Facts, no praise.
- No em dashes. No "not X, but Y" antithesis. No hype.
- Never mention lateness, the setup items, or how the work was read (packet, frames, transcript,
  coder, grader, model, AI, session scan, "it appears", "the video shows").
- Never tie the September survey to difficulty.

Before reports are built, every student-facing sentence is checked against this file (step 3b of
`/grade-sprint`), and `sprint_feedback.py` refuses to build when it finds a stock figure of speech.

## Never "the course can" or "the course cannot"

Scott, 2026-10-29: "the course" does not open, check or see anything. Name who it is shared with, or
not: "not shared with Professor Murff (GitHub `sdmurff`)", "so Professor Murff can open it", "not shared
with aifoundry.byu@gmail.com" for a Google file, "set the Loom to Anyone with the link or share it with
scott.murff@byu.edu". Never "which the course cannot open", "so the course can check it", "work the
course could not check".

## Say "full points", never "full marks"

Scott, 2026-10-29: "I would never say that." Write "Full points: ..." in feedback and "full points" anywhere a
student reads. The build refuses "full marks".
