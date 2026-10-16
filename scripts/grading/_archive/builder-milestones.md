# Builder milestones (draft v0, 2026-10-14)

How a sprint's work grows a student's builder profile. The profile starts at the student's own
self-assessment (the core). Each sprint adds growth for milestones the work shows for the first
time. Never graded: it does not touch a sprint's score.

Axis definitions are the ones in `sprint-grader.md` (Oct 8 split): Agentic Workflow is putting
AI to work, both directing coding agents and building AI into the product (prompts, tool use,
agent loops, evals). Application Architecture includes wiring a model in (API calls, retrieval,
cost and latency). AI Systems is understanding how models work and why they behave as they do,
not wiring them.

## How to credit a milestone

A milestone is a **concept**, never a tool. Match the concept, name the tool in the evidence.
Supabase, Firebase, Postgres, SQLite, Rails models and a defined Airtable base all show
"Keeps data on purpose". The examples under each concept are examples, not limits. When unsure,
credit nothing and list it under `uncertain` for Scott; settled cases become examples here.

**Depth**, on the same 1 to 5 scale words as the self-assessment:

| Depth | What the work shows |
|---|---|
| Used it | the concept is present and working in what they made |
| Built it | they created or changed it this sprint |
| Decided it | they chose between options and recorded why (a decision record, a spec section) |
| Taught it | they explained it to others (a deputy answer, a post, a walkthrough for the class) |
| Explained it | a `/learn` log on a section that teaches the concept, with the check passed |

**Evidence must be checkable** in the packet: a file or commit in a shared repo, a Google file
that opened, a live link that opened, or a moment in the Loom. Work described only in the
`/sprint-review` report, or in a repo that is not shared, goes under `seen_not_counted` with why.

**Credit only this sprint's work**: commits in the window, files changed in it, the Loom, and
learning logs dated in the window.

## Growth (computed in code, not by the coder)

- A credit is new the first time a student shows that concept at that depth. Showing it again
  at the same depth adds nothing; reaching a deeper depth on the same concept is new.
- Each new credit adds 0.25 to its axis. At most 0.5 per axis per sprint. An axis never passes 5.
- Growth only adds.

## The milestones

### Discovery
- **D1 Talked to real users.** Interviews, observation or calls with real people, written up.
- **D2 Defined who and what.** A persona, problem statement or job to be done drawn from what users said.
- **D3 Tested an assumption.** A riskiest-assumption test, landing-page or smoke test, or survey, with the result.
- **D4 Chose from evidence.** A ranking or decision record that cites what was learned.

### Design
- **G1 Mapped a flow.** A user flow or journey before or alongside screens.
- **G2 Designed screens on purpose.** Mockups, a design system, or the empty, loading and error states.
- **G3 Tested the design with people.** Usability notes, and what changed because of them.
- **G4 Specified before building.** A spec with acceptance criteria written before the work it describes.

### Launch and Learn
- **L1 Put it in front of real people.** Shipped to people other than the builder: signups, users, a pilot.
- **L2 Measured something.** A metric defined and its data collected.
- **L3 Ran a go-to-market test.** A channel, copy or outreach experiment, with the result.
- **L4 Priced or modeled it.** A price, a pricing test, or a business model with numbers.
- **L5 Changed something because of what users did.** Feedback or data that led to a recorded change.

### Application Architecture
- **A1 Runs somewhere others can reach.** Any host, store, or published page; local-only does not count.
- **A2 Keeps data on purpose.** Data that outlives a session, in a shape that was defined (any database or store).
- **A3 Knows who you are.** Sign-in and access rules, in any provider.
- **A4 Talks to other systems.** Calls an API, including a model's, or offers one.
- **A5 Keeps secrets out of the code.** Keys in environment variables or a secret store, not committed.
- **A6 Guards against breakage.** Automated tests or checks that run.

### Agentic Workflow
- **W1 Directed coding agents on purpose.** Context files (CLAUDE.md, AGENTS.md), specs fed to the agent, plan-first work.
- **W2 Built agent tooling.** A custom skill, subagent, hook, or MCP server.
- **W3 Built AI into the product.** A feature driven by prompts the student wrote.
- **W4 Measured AI output.** An eval set, a scorer, or prompt versions compared against results.
- **W5 Put an agent loop in the product.** Tool use or multi-step model actions inside the product.

### AI Systems
- **S1 Explained how models work.** Tokens, context windows, pretraining, fine-tuning, embeddings, in the student's own words.
- **S2 Diagnosed model behavior by its mechanism.** A hallucination, drift or limit traced to its cause, with the fix that follows.
- **S3 Chose a model or technique for a reason.** Prompting versus fine-tuning, retrieval, model size, cost or latency, with the reasoning.

## Coder output, per student per sprint

```json
{"net_id": "", "sprint": 2,
 "credits": [{"id": "A4", "depth": "Built it", "when": "Oct 12",
              "did": "one sentence, second person, what they did",
              "evidence": "short description", "ref": "commit sha, file path, URL, or Loom m:ss"}],
 "seen_not_counted": [{"id": "D1", "what": "", "when": "", "why": ""}],
 "uncertain": [{"id": "", "what": "", "question": "for Scott"}]}
```
