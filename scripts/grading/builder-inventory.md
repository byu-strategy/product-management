# Builder inventory (draft v1.2, 2026-10-14)

One list of 37 items (six per axis, seven in Launch and Learn), used two ways: the baseline
survey asks students to place themselves on each item, and sprint evidence moves items up.
Supersedes the milestone list in `builder-milestones.md` (v0, the pilot) and the 50 items of the
first baseline survey.

v1.2 rewrote levels 4 and 5 from 25 coded Sprint 2 packets (`_data/.../builder-pilot/inventory-fit/`):
what students actually did, and what a coder could and could not confirm from the packet.

**The standard.** A profile with every item at 5 describes someone ready to be hired into
LinkedIn's Associate Product Builder program, Google's APM program, or a builder role at a top
technology company. LinkedIn's application is a 60-second demo of a product people use, with no
resume, and it weighs judgment over tools; Google's APM loop tests product sense and technical
reasoning at whiteboard level. Few students should reach 5 on an axis during the course; a strong
student ends near 3, with 4 on the axes their product required most.

## The ladder (the same five levels for every item)

| Level | Meaning | Who can award it |
|---|---|---|
| 1 | New to me | the survey |
| 2 | I know what it is and what it is for | the survey |
| 3 | I can reason about it out loud: when to use it, what breaks | the survey; confirmed by a `/learn` check or an exam |
| 4 | I have built it in my own product | sprint evidence |
| 5 | I built it for real users and chose it on purpose | sprint evidence |

- An item moves only up. Self-rated levels 2 and 3 stay as given until a check confirms or
  recalibrates them.
- An axis is the mean of its items. One level on one item moves the axis by 1/6 (1/7 in Launch and
  Learn), and every point on a report names the item that earned it.
- Practices, never tools: any database counts for "Data and schema".

Levels 1 and 2 read the same for every item and are not repeated below.

## Evidence rules (for levels 4 and 5)

- **Checkable.** Evidence is something a reader can open: a commit or file in a shared repo, a
  Google file, a live link, or a moment in the Loom. A sentence in the retro or README, or work
  described only in the `/sprint-review` report, does not count by itself.
- **This sprint.** The work is in this sprint's commits or Loom. A level reached earlier is kept,
  never credited again.
- **Real users.** People who do not build the product, using it for its purpose, shown by a dated
  record: a feedback or test note, a usage count from the database, a support message, a payment,
  or their data on screen in the Loom.
  - The team is the people who build it. A business partner, coworker, co-founder or client who
    uses it and does not build it is a real user.
  - Family members count for watching someone use it (G6), and for other items only when the
    product is for households.
  - When the builder is the only user, the item stops at 4.
- **Chose it on purpose.** A file in `decisions/` (or a spec section) that names at least two
  options and the reason for the one chosen, committed no later than the work it decides. A record
  committed in the same commit as the work counts for level 4 only.
- **Both halves.** When a level-5 statement has two parts, both must be shown. A coder names the
  missing half, so the student sees what is left.
- **Before.** "Before the code" means an earlier commit, not an earlier time in the same commit.
- **Defending a choice** out loud is level 3: a `/learn` check, an exam question, or a Loom moment
  where the student names the alternative and why they did not choose it.

## Discovery

**D1 User interviews.** Learning from real people without leading them.
- 3: can explain why "would you use this?" is a bad question, and what to ask instead.
- 4: interviewed people about the problem and wrote up what they said. Interviews that only collect
  the product's content do not count.
- 5: the product's direction changed or held because of the interviews, and a decision record cites them.
- Old survey: User interviews.
- Chapters: Ch 4: Problem Interviews; Conducting Effective Interviews; Interview Synthesis.

**D2 Problem and who it is for.** The problem, separate from the fix, and the people who have it.
- 3: can state a problem without naming a solution, and who it is not for.
- 4: wrote a problem statement or persona that cites what users said.
- 5: real users describe the problem in their own words in the record, and it says who was left out and why.
- Old survey: Problem vs solution; Personas and segments.
- Chapters: Ch 3: Problem vs. Solution Thinking. Ch 4: Jobs-to-be-Done; Who It Is For, and Not For; Building Personas.

**D3 Assumption tests.** Finding the riskiest belief and checking it.
- 3: can name a product's riskiest assumption and a test that could prove it wrong.
- 4: named a belief the product depends on, ran a check that could prove it wrong (an interview,
  a prototype, a survey, a comparison with a real result), and recorded the result.
- 5: the result decided something, and a decision record cites it.
- Old survey: none.
- Chapters: Ch 4: The Evidence Ladder; The Four Risks and the Riskiest Assumption; The Smallest Test.

**D4 Competitive landscape.** What else people use for the problem, and what is missing from it.
- 3: can explain why users would choose the product over what they use now, including doing nothing.
- 4: wrote a comparison of the alternatives users actually use, including what they do today.
- 5: the product's position comes from that comparison, in a decision record.
- Old survey: Competitive landscape.
- Chapters: Ch 4: The Real Competitor Is the Current Habit. Ch 3: The five forces; Blue oceans; Moats; Disruption.

**D5 Prioritization.** Ranking by value, effort and risk.
- 3: can explain why a team should build one thing before another.
- 4: ranked options in writing with the criteria shown.
- 5: built what ranked first for real users, and the ranking cites what was learned.
- Old survey: Prioritization.
- Chapters: Ch 4: The Commitment Decision; MVP Scoping; Feature Prioritization.

**D6 What to build.** Choosing this product or idea over others: who it is for and why it can win.
- 3: can say what a product will not do, and test an idea for desirability, feasibility and viability.
- 4: wrote down why this product or idea over at least one other, including who it is for and why it can win.
- 5: built the chosen idea for real users, and a later decision record says whether the choice held.
- Old survey: none.
- Chapters: Ch 3: Vision before strategy; Strategy is choosing what not to do; Where to play, and how to win; Creating value, and capturing it; DHM.

## Design

**G1 User flows and states.** What the user does, step by step, including off the happy path.
- 3: can walk through a flow, say where users will drop off, and list the empty, loading and error states it needs.
- 4: built the empty, loading and error states for a flow, and wrote the flow down (steps, or a list of states).
- 5: changed a flow or state because of what a person outside the team did, and recorded why.
- Old survey: User flows.
- Chapters: Ch 5: Flows Before Screens; Off the Happy Path.

**G2 Visual fundamentals.** Hierarchy, spacing, contrast, accessibility.
- 3: can say why one screen reads more clearly than another.
- 4: wrote down design rules (a type scale, color rules, a contrast check, keyboard access) and the product follows them.
- 5: people outside the team use it without help, and the rules changed because of what they did.
- Old survey: Usability fundamentals.
- Chapters: Ch 5: Attention and Hierarchy; Words Are Interface; Accessible by Default. Ch 5b: Visual Design Fundamentals; Norman's Principles; How People Perceive a Screen.

**G3 Design system.** Define a component once and reuse it.
- 3: can explain what a design system saves and what it costs.
- 4: built shared components or design tokens used on three or more screens.
- 5: chose the system over alternatives in a decision record, in a product real users use.
- Old survey: Design systems.
- Chapters: Ch 5: Decide Once: Design Systems and Familiar Patterns.

**G4 Specs.** A description clear enough to build from.
- 3: can explain what makes a spec testable.
- 4: wrote a spec with acceptance criteria, committed before the code it describes.
- 5: shipped to real users against the spec, and recorded what changed in it and why.
- Old survey: Spec writing.
- Chapters: Ch 6b: User Stories; PRDs; The SDD Workflow; Stories and acceptance criteria.

**G5 Critique and direction.** Saying specifically what is wrong and what to change.
- 3: can name specific problems in a generated screen and the change that fixes each.
- 4: directed design changes in writing (to an agent or a teammate), and they shipped.
- 5: a written design direction, revised after people outside the team used the product, says what changed and why.
- Old survey: UI critique; Design direction.
- Chapters: Ch 5: Directing an Agent on Design. Ch 5b: Nielsen's Ten Usability Heuristics.

**G6 Usability testing.** Watching a real person use it, then changing it.
- 3: can explain what a usability test can and cannot show.
- 4: watched a person outside the team use it and wrote down what they did, one note per session.
- 5: changed the product because of it, and the change is recorded.
- Old survey: Prototype testing.
- Chapters: Ch 6: Running a Usability Test; What to Observe; Synthesizing Feedback.

## Launch and Learn

**L1 Shipping to real people.** People who do not build it use it.
- 3: can explain the difference between launched and used.
- 4: people outside the team used it, with a dated record.
- 5: two or more people used it on two or more separate days, on their own.
- Old survey: none.
- Chapters: Ch 12: Who It Is For: The Beachhead; Your First Users, by Hand; Launch in rings.

**L2 Metrics and instrumentation.** One number that shows whether the product works, and the events behind it.
- 3: can explain why signups are not adoption, what to log before launch, and what an A/B test can and cannot prove.
- 4: named one number that shows whether the product works for its users, and built the logging
  that counts it. Analytics shown to users does not count.
- 5: chose the number over others in a decision record, and real users' data answered a question asked in advance.
- Old survey: Instrumentation; Metric selection; Activation and retention.
- Chapters: Ch 14: Decide What Working Means First; Instrument the Core Action; Signups Are Not Adoption; Retention. Ch 12: Instrument it before you launch.

**L3 Experiments.** A designed test of the product, its copy or its price.
- 3: can explain what makes a test fair, and what a before-and-after comparison cannot show.
- 4: ran a test with a prediction stated before it started, and recorded the result.
- 5: the result changed what was built or how it is offered, recorded.
- Old survey: Experiments.
- Chapters: Ch 14: Cause Versus Coincidence. Ch 12: When to change your GTM.

**L4 Positioning, pricing and business model.** Why someone chooses it, what it is worth, and whether the numbers work.
- 3: can state who it is for, what it replaces, and a reasoned price.
- 4: wrote positioning, a price, or a business model with unit economics.
- 5: tested a price or position with real people and recorded what happened.
- Old survey: Positioning and pricing.
- Chapters: Ch 12: Positioning & Messaging; Pricing and AI Margins. Ch 13: Revenue Models; Unit Economics and Break-Even.

**L5 Acting on usage.** Deciding what to change, cut or stop from what users did.
- 3: can explain how to decide what to build next from usage.
- 4: analyzed what users did with a feature or the product, and wrote down what it showed.
- 5: changed, cut, or stopped a feature or the product because of it, with the record.
- Old survey: Usage analysis; Feature retirement.
- Chapters: Ch 14: Keep, Change, or Kill; Asking How People Feel.

**L6 Telling the product's story.** A demo and a story that make people believe it.
- 3: can explain what a story does that a feature list does not.
- 4: recorded a demo of 90 seconds or less that shows one task done in the live product, from the
  user's first action to the result. A tour of screens, or features described and not shown, does not count.
- 5: the demo shows real users' use of the product, and someone acted on it (a user signed up, a sponsor approved, a client paid).
- Old survey: none.
- Chapters: Ch 15: A story has a job; The Final Demo.

**L7 Reaching users.** Getting the product in front of the people it is for.
- 3: can explain where the first users will come from and how to reach them.
- 4: ran outreach through a channel (direct messages, posts, a listing, ads, flyers, in person) and
  recorded who was reached and what happened.
- 5: chose a channel from recorded results, and users came from it.
- Old survey: none.
- Chapters: Ch 12: Who It Is For: The Beachhead; Your First Users, by Hand; Choosing Your Channel Strategy.

## Application Architecture

**A1 Client, server and deploy.** What runs where, and how it goes live.
- 3: can explain what runs in the browser, what runs on a server, and how a build becomes a live app.
- 4: deployed this sprint's work at an address others can open, and it runs there. A fix to the
  live app from its errors or logs also counts.
- 5: chose the stack and host in a decision record that names the alternatives, and people outside the team reach it.
- Old survey: Client vs server; Deploy, builds and logs; Stack selection.
- Chapters: Ch 7: Three Places Code Runs; How a Request Crosses the Internet; Tech Stacks. Ch 2: Deploying a Prototype. Ch 9: Environments; Logs and Error Reports.

**A2 Data and schema.** Data that outlives a session, in a defined shape.
- 3: can explain tables, keys and relationships, and when a schema change breaks things.
- 4: defined tables in a migration or schema file, and the product reads and writes them. Importing
  existing data into them (a spreadsheet, an old system, with duplicates removed) also counts.
- 5: real users' data lives there, and the schema choices are in a decision record.
- Old survey: Database schema design.
- Chapters: Ch 8: The Data Model Is the Skeleton; Asking the Database a Question.

**A3 Sign-in and access.** Who you are, and what you may see.
- 3: can explain authentication versus authorization.
- 4: built sign-in (a password, a provider, or a magic link) and at least one rule that stops one
  user from reading another user's data.
- 5: real users sign in, and the access rules are recorded and tested.
- Old survey: Auth vs authorization.
- Chapters: Ch 7: Who You Are, What You May Do. Ch 8: Row Level Security.

**A4 APIs and integrations.** Calling other systems, including models, or offering an API.
- 3: can explain a request and response, and why calls fail.
- 4: the product calls an API (a model counts) and handles a failed call.
- 5: chose the integration in a decision record, and it works for real users.
- Old survey: APIs.
- Chapters: Ch 8: Requests Are Contracts That Fail. Ch 11: Where the Call Lives.

**A5 Secrets, privacy and security.** Keys out of the code, people's data protected.
- 3: can explain why a committed key is an incident and what never goes in a prompt.
- 4: keys are in environment variables or a secret store, and no key, database file, log or
  personal data is in the repo.
- 5: handles real people's data with the protections written down and applied (consent, redaction,
  access limits). Passing a platform review (an app store, a sign-in provider's verification) counts.
- Old survey: Environments and secrets; Data privacy; Security basics.
- Chapters: Ch 8: Secrets and Sensitive Data.

**A6 Version control, checks and tech debt.** History, review, what runs on every change, and what was deferred.
- 3: can explain branches, pull requests, continuous integration, and when debt is worth taking on.
- 4: works in branches or pull requests, or has automated tests or checks that run.
- 5: checks run on a product real users depend on, and a record says what they catch.
- Old survey: Version control; Pull requests; CI.
- Chapters: Ch 9: Git; Pull Requests; Automated Checks; Rolling Back. Ch 9b: Tests; Technical Debt.

## Agentic Workflow

Putting AI to work: directing coding agents, and building AI into the product.

**W1 Directing coding agents.** Context files, plans, and specs fed to the agent.
- 3: can explain what a context file is for and when to plan before building.
- 4: wrote project instructions or specs that the agent works from, committed.
- 5: changed the instructions because of what the agent got wrong, and recorded what the change fixed.
- Old survey: Project instructions; The agent loop; Memory.
- Chapters: Ch 1: What Makes an Agent an Agent. Ch 2: It Knows Only What It Can See; Project Overview; Development Notes.

**W2 Agent tooling.** Skills, hooks, subagents, and tool connections such as MCP.
- 3: can explain when to package a workflow, and when parallel agents help or cost.
- 4: built a skill, hook, subagent or tool connection that runs. A skill or agent that is itself the product counts here.
- 5: people outside the team use it, or it runs in the product's development every sprint, and its design is recorded.
- Old survey: Skills; Hooks; Subagents; MCP; Multi-agent orchestration.
- Chapters: Ch 2: Slash Commands; Skills; Rules; Advice Versus Enforcement; Delegation and Parallel Work; MCP.

**W3 Checking agent output.** Reviewing, testing and limiting what agents do.
- 3: can explain what to check in agent-written code, and what an agent may run unattended.
- 4: caught and fixed an agent's error with the record, checked agent work in the running product
  and recorded the check, or set permissions on purpose.
- 5: the same recorded check runs on agent work throughout the sprint, in a product real users use.
- Old survey: Code review of agent output; Testing AI-written code; Agent permissions.
- Chapters: Ch 2: Blast Radius; Done Means You Saw It Work.

**W4 Prompts in the product.** Features driven by prompts the student wrote.
- 3: can explain instructions, examples and structured output.
- 4: built a feature driven by a prompt they wrote, with the prompt in the repo.
- 5: real users use the feature, and prompt versions are kept with why each changed.
- Old survey: Prompt engineering.
- Chapters: Ch 11: Prompts Are Product Code; Getting Structured Output. Ch 10: Prompting.

**W5 Tool use and agent loops in the product.** The model calls tools and takes steps on its own.
- 3: can explain tool calling, stopping conditions and retries.
- 4: built a feature where the model takes more than one step, or calls a tool, without a person in between.
- 5: real users rely on it, and the loop's limits are written down.
- Old survey: Tool use and function calling; Loop design.
- Chapters: Ch 11: Tools and Agent Loops.

**W6 Evals and accuracy checks.** Knowing whether output, from a model or from the student's own logic, is right.
- 3: can explain what an eval set is and why one example proves little.
- 4: built test cases, a scorer, or a check against a known answer (a real invoice, a past result), ran it, and saved the results.
- 5: a prompt, model or logic decision was made from the saved results, recorded.
- Old survey: Evals.
- Chapters: Ch 11: Evals: Knowing Whether It Works.

## AI Systems

Understanding how models work and why they behave as they do. Level 4 here means the
understanding shaped something the student built, and the record says how. Most students will
show this axis at level 3, through `/learn` and the exams.

**S1 Tokens and the context window.** What fills it, and what happens when it overflows.
- 3: can explain tokens, the context window, and what overflow does.
- 4: designed around the limit in the product (trimming, summarizing, chunking), noted in a spec or the code.
- 5: the design is backed by numbers from the product, recorded.
- Old survey: Context window.
- Chapters: Ch 10: Step 1 (tokens); The context window is working memory. Ch 11: The API Remembers Nothing.

**S2 Cost and latency.** What makes a model call slow or expensive.
- 3: can estimate a call's cost and explain what drives latency.
- 4: measured cost or latency in the product and saved the numbers. A claimed saving with no measurement does not count.
- 5: changed the product because of the numbers, recorded.
- Old survey: Tokens, latency and cost.
- Chapters: Ch 11: What It Costs. Ch 12: Every AI call is a cost.

**S3 How models are made.** Pretraining, fine-tuning, and training from feedback.
- 3: can explain how a model is trained and what that means for what it knows.
- 4: recorded a product decision that depends on how models are trained (what the model cannot know, its cutoff, why it follows instructions).
- 5: that decision was tested in the product, with saved results.
- Old survey: none.
- Chapters: Ch 10: Steps 2 to 6 (embeddings, attention, prediction, pretraining, fine-tuning).

**S4 Retrieval and embeddings.** Giving a model the right material, and where retrieval fails.
- 3: can explain embeddings, chunking and where retrieval fails.
- 4: built retrieval into the product.
- 5: measured retrieval quality and changed it because of the result.
- Old survey: RAG.
- Chapters: Ch 10: Step 2 (embeddings). Ch 11: Grounding Answers in Your Data.

**S5 Hallucination and verification.** Why models make things up, and what must be checked.
- 3: can explain why models hallucinate and what to verify.
- 4: built a check on model output into the product (a validation rule, required sources, a second
  independent pass, a person approving), or traced a wrong output to its cause and fixed it.
- 5: the check runs for real users, and what it catches is recorded.
- Old survey: Hallucination and verification.
- Chapters: Ch 10: Plausible is not true; The jagged frontier. Ch 11: Where It Breaks.

**S6 Choosing a model or technique.** Prompting, retrieval, fine-tuning, model size.
- 3: can explain when each technique fits.
- 4: chose a model or technique in a decision record that names an alternative.
- 5: the choice is backed by a comparison run in the product, with saved results.
- Old survey: none.
- Chapters: Ch 11: one paragraph on choosing a model (no section yet).

## Open

- Calibrate level 3 checks: one `/learn` or exam question per item, in the form "Your app needs X.
  What would you choose, and why?"
- Map each current student's 50 first-survey answers onto these items, where the old survey has a
  match, as a provisional starting point until the December re-run uses this inventory.
- Items the old survey has no match for (D3, D6, L1, L6, L7, S3, S6) start at the student's axis mean.
- The packet cannot yet show usage counts, who wrote a record (student or agent), or Loom
  timestamps. A "Users this sprint" table in the `/sprint-review` template would give "real users"
  a dated record to point to.
