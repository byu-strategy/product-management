# Depth levels: how a student works on an axis (practice, one level per axis per sprint)

Depth is 30% of the practice score on each spoke (up to 15 of the 50 practice points; on AI
Systems, up to 7.5 of 25). Level 1 earns no points, level 2 earns 20% of the depth points, level 3
earns 50%, and level 4 earns all of them (weighting D, decided 2026-10-16). A coder reads all of one sprint's evidence together (repo and commit
history, the review report and its session-scan lists, the Loom, the plan, the retro) and assigns
each axis the sprint's work touched one level. An axis the sprint did not touch gets no level.

The levels describe how the student worked, not how much. Each level includes the ones below it.
Assign the highest level the evidence clearly shows; when torn between two, assign the lower and
say what would have settled it.

| Level | Name | What the evidence shows |
|---|---|---|
| 1 | **Followed** | Work on the axis exists, but it follows the template, a tutorial, or the agent's defaults. Little sign of the student's own choices: no spec, generic prompts, no sign they checked the result. |
| 2 | **Directed** | The student said specifically what to build and checked that it worked: a spec or acceptance criteria, specific instructions, a Loom or test showing the result works as intended. |
| 3 | **Decided** | The student challenged what the agent or the template proposed, weighed the options, and owned the trade-off, or caught and fixed what the agent got wrong. Evidence: a decision record, a session where the student rejected or overruled the agent's proposal with a reason, a choice between named options in the session scan or the review report, a retro that explains why in their own words, a fix commit after they found a problem. A fix counts only when the student found the problem (in testing, review, or use, not the agent repairing its own error in the same session) and the fix took a judgment about the product: data, access, hosting, cost, or behavior. Build errors, typos, dependency and config repairs stay at the level the rest of the work shows. |
| 4 | **Delivered** | People outside the team use it, and the student changed the work because of what those people did or said. Evidence must come from the student's own sessions (the review report's "Users this sprint" list: reading production rows or logs about real users, handling a user's report) tied to a commit that changed the work. Shipping to production alone is not level 4, and users named only in the retro or the review's prose do not count. |

Rules: the evidence rules in `builder-inventory.md` apply (checkable evidence; this sprint only;
course-provided material never counts; credit follows the commit author in a shared repo). A
claim made only in the retro does not reach level 2 or above by itself; the retro can explain
evidence that is there. Depth on the profile is sticky: the highest level shown in any sprint stays.

## One example per axis (composite, not real students)

**Agentic Workflow.** Level 1: the student used the course skills as given and accepted the
agent's output. Level 2: they wrote a CLAUDE.md with project rules and a spec for the feature, and
the Loom shows the feature working. Level 3: the session scan shows they added a hook after the
agent kept editing a protected file, and the retro explains why a hook and not another CLAUDE.md
line. Level 4: classmates installed the skill they wrote and the student changed it after two of
them reported a failure.

**Application Architecture.** Level 1: the template's database and deploy, unchanged. Level 2: a
migration adding a table the app reads and writes, with a test or Loom showing it work. Level 3: a
decision record choosing a host over two named alternatives, or a commit fixing a row-level
security rule the student found was too open. Not level 3: fixing a failed deploy, a missing environment variable, or a type error, even when the student noticed it. Level 4: outside users sign in and store data, and
the student changed an access rule after a user reported seeing the wrong data.

**AI Systems.** Level 1: a model call copied from an example. Level 2: the student measured token
cost or latency for their feature and saved the numbers. Level 3: they chose retrieval over a
longer prompt (or a smaller model over a larger one) with the reason and the numbers recorded.
Level 4: real users use the feature, and the student changed the model or technique because of
measured results from that use.

**Discovery.** Level 1: a persona or problem statement the agent drafted with no interviews behind
it. Level 2: interview notes from real conversations and a problem statement that cites them.
Level 3: a ranking or commitment decision that cites what was learned and names what was set
aside. Level 4: the direction the evidence chose is in front of real users, and the student
revisited the decision because of what they did.

**Design.** Level 1: generated screens accepted as they came. Level 2: a flow written down with its
empty and error states built, matching a spec with acceptance criteria. Level 3: a usability test
with a real person and a recorded change made because of it, or a design rule chosen over an
alternative with the reason. Level 4: people outside the team use the flow, and the student
changed it because of what they did.

**Launch and Learn.** Level 1: a landing page or pricing line with no measurement. Level 2: one
named metric with the logging that counts it, or a dated outreach log. Level 3: a channel, price, or
metric chosen from recorded results over a named alternative. Level 4: real users came through
the chosen channel or used the product on more than one day, and the student changed something
because of the numbers.
