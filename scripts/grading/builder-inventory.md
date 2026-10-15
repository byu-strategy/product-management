# Builder inventory (draft v1.1, 2026-10-14)

One list of 36 items, six per axis, used two ways: the baseline survey asks students to place
themselves on each item, and sprint evidence moves items up. Supersedes the milestone list in
`builder-milestones.md` (v0, the pilot) and the 50 items of the first baseline survey.

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
| 5 | I built it for real users, chose it on purpose, and can defend the choice | sprint evidence |

- An item moves only up. Self-rated levels 2 and 3 stay as given until a check confirms or
  recalibrates them; levels 4 and 5 need evidence a reader can open (a commit or file in a shared
  repo, a Google file, a live link, a moment in the Loom).
- "Real users" means people other than the builder, teammates and classmates, using it for its
  purpose. "Chose it on purpose" means a decision record or spec section that names the options and
  why this one.
- An axis is the mean of its six items. One level on one item moves the axis by 1/6 (about 0.17),
  and every point on a report names the item that earned it.
- Practices, never tools: any database counts for "Data and schema".

Levels 1 and 2 read the same for every item and are not repeated below.

## Discovery

**D1 User interviews.** Learning from real people without leading them.
- 3: can explain why "would you use this?" is a bad question, and what to ask instead.
- 4: interviewed people about the problem and wrote up what they said.
- 5: the product's direction changed or held because of interviews, and the write-up shows it.
- Old survey: User interviews.
- Chapters: Ch 4: Problem Interviews; Conducting Effective Interviews; Interview Synthesis.

**D2 Problem and who it is for.** The problem, separate from the fix, and the people who have it.
- 3: can state a problem without naming a solution, and who it is not for.
- 4: wrote a problem statement or persona drawn from what users said.
- 5: real users recognize the problem in their own words, and the record says who was left out and why.
- Old survey: Problem vs solution; Personas and segments.
- Chapters: Ch 3: Problem vs. Solution Thinking. Ch 4: Jobs-to-be-Done; Who It Is For, and Not For; Building Personas.

**D3 Assumption tests.** Finding the riskiest belief and testing it cheaply.
- 3: can name a product's riskiest assumption and a test that could prove it wrong.
- 4: ran a test (smoke test, landing page, survey, prototype) and recorded the result.
- 5: the result decided something, and the decision record cites it.
- Old survey: none.
- Chapters: Ch 4: The Evidence Ladder; The Four Risks and the Riskiest Assumption; The Smallest Test.

**D4 Competitive landscape.** What else people use for the problem, and what is missing from it.
- 3: can explain why users would choose the product over what they use now, including doing nothing.
- 4: wrote a comparison of the alternatives users actually use.
- 5: the product's position comes from that comparison, and the student can defend it.
- Old survey: Competitive landscape.
- Chapters: Ch 4: The Real Competitor Is the Current Habit. Ch 3: The five forces; Blue oceans; Moats; Disruption.

**D5 Prioritization.** Ranking by value, effort and risk.
- 3: can explain why a team should build one thing before another.
- 4: ranked options in writing with the criteria shown.
- 5: built what ranked first for real users, and the ranking cites what was learned.
- Old survey: Prioritization.
- Chapters: Ch 4: The Commitment Decision; MVP Scoping; Feature Prioritization.

**D6 What is worth building.** Where to play, how to win, and whether the value can be captured.
- 3: can say what a product will not do, and test an idea for desirability, feasibility and viability.
- 4: wrote down where the product plays and why it can win.
- 5: built for real users the choice that analysis supported, and can defend it against the alternatives.
- Old survey: none.
## Design
- Chapters: Ch 3: Vision before strategy; Strategy is choosing what not to do; Where to play, and how to win; Creating value, and capturing it; DHM.

**G1 User flows and states.** What the user does, step by step, including off the happy path.
- 3: can walk through a flow, say where users will drop off, and list the empty, loading and error states it needs.
- 4: mapped a flow and built its states.
- 5: changed the flow or a state because of what real users did, and recorded why.
- Old survey: User flows.
- Chapters: Ch 5: Flows Before Screens; Off the Happy Path.
**G2 Visual fundamentals.** Hierarchy, spacing, contrast, accessibility.
- 3: can say why one screen reads more clearly than another.
- 4: applied them on purpose (a type scale, contrast checks, keyboard access).
- 5: real users use it without help, and the design choices are written down.
- Old survey: Usability fundamentals.
- Chapters: Ch 5: Flows Before Screens; Off the Happy Path.

**G3 Design system.** Define a component once and reuse it.
- 3: can explain what a design system saves and what it costs.
- 4: built shared components or tokens used across the product.
- 5: chose the system over alternatives for a stated reason, in a product real users use.
- Old survey: Design systems.
- Chapters: Ch 5: Decide Once: Design Systems and Familiar Patterns.

**G4 Specs.** A description clear enough to build from.
- 3: can explain what makes a spec testable.
- 4: wrote a spec with acceptance criteria before building it.
- 5: shipped to real users against the spec, and recorded what changed in it and why.
- Old survey: Spec writing.
- Chapters: Ch 6b: User Stories; PRDs; The SDD Workflow; Stories and acceptance criteria.

**G5 Critique and direction.** Saying specifically what is wrong and what to change.
- 3: can name specific problems in a generated screen and the change that fixes each.
- 4: directed design changes in writing (to an agent or a teammate) and they shipped.
- 5: can defend the product's design direction to someone who disagrees, with the record of why.
- Old survey: UI critique; Design direction.
- Chapters: Ch 5: Directing an Agent on Design. Ch 5b: Nielsen's Ten Usability Heuristics.

**G6 Usability testing.** Watching a real person use it, then changing it.
- 3: can explain what a usability test can and cannot show.
- 4: ran a test with a real person and wrote down what happened.
- 5: changed the product because of it, and the change is recorded.
- Old survey: Prototype testing.
- Chapters: Ch 6: Running a Usability Test; What to Observe; Synthesizing Feedback.

## Launch and Learn

**L1 Shipping to real people.** People other than the builder use it.
- 3: can explain the difference between launched and used.
- 4: put it in front of people outside the team.
- 5: people use it more than once, on their own.
- Old survey: none.
- Chapters: Ch 12: Who It Is For: The Beachhead; Your First Users, by Hand; Launch in rings.

**L2 Metrics and instrumentation.** One number that moves if the product works, and the events behind it.
- 3: can explain why signups are not adoption, and what to log before launch.
- 4: defined a metric and built the logging that collects it.
- 5: chose the metric over others for a stated reason, and real users' data answered a question asked in advance.
- Old survey: Instrumentation; Metric selection; Activation and retention.
- Chapters: Ch 14: Decide What Working Means First; Instrument the Core Action; Signups Are Not Adoption; Retention. Ch 12: Instrument it before you launch.

**L3 Experiments.** Tests of channel, copy, price or feature, with a result.
- 3: can explain what an A/B test can and cannot prove.
- 4: ran an experiment and recorded the result.
- 5: the result changed what was built or how it is offered.
- Old survey: Experiments.
- Chapters: Ch 14: Cause Versus Coincidence. Ch 12: When to change your GTM.

**L4 Positioning, pricing and business model.** Why someone chooses it, what it is worth, and whether the numbers work.
- 3: can state who it is for, what it replaces, and a reasoned price.
- 4: wrote positioning, a price, or a business model with unit economics.
- 5: tested a price or position with real people and recorded what happened.
- Old survey: Positioning and pricing.
- Chapters: Ch 12: Positioning & Messaging; Pricing and AI Margins. Ch 13: Revenue Models; Unit Economics and Break-Even.

**L5 Acting on usage.** Deciding what to change, or stop, from what users did.
- 3: can explain how to decide what to build next from usage.
- 4: analyzed usage and wrote down what it showed.
- 5: changed or removed something because of it, with the record of why.
- Old survey: Usage analysis; Feature retirement.
- Chapters: Ch 14: Keep, Change, or Kill; Asking How People Feel.

**L6 Telling the product's story.** A demo and a story that make people believe it.
- 3: can explain what a story does that a feature list does not.
- 4: recorded a demo that shows the product working, start to finish.
- 5: the story persuaded real people (users, a sponsor, an interviewer), and the demo shows the product in use.
- Old survey: none.
- Chapters: Ch 15: A story has a job; The Final Demo.

## Application Architecture

**A1 Client, server and deploy.** What runs where, and how it goes live.
- 3: can explain what runs in the browser, what runs on a server, and how a build becomes a live app.
- 4: deployed it where others can reach it, and can read its logs.
- 5: chose the stack and host over alternatives for a stated reason, and real users reach it.
- Old survey: Client vs server; Deploy, builds and logs; Stack selection.
- Chapters: Ch 7: Three Places Code Runs; How a Request Crosses the Internet; Tech Stacks. Ch 2: Deploying a Prototype. Ch 9: Environments; Logs and Error Reports.

**A2 Data and schema.** Data that outlives a session, in a defined shape.
- 3: can explain tables, keys and relationships, and when a schema change breaks things.
- 4: defined a schema and the product stores data in it.
- 5: real users' data lives there, and the schema choices are written down.
- Old survey: Database schema design.
- Chapters: Ch 8: The Data Model Is the Skeleton; Asking the Database a Question.

**A3 Sign-in and access.** Who you are, and what you may see.
- 3: can explain authentication versus authorization.
- 4: built sign-in and at least one access rule.
- 5: real users sign in, and the access rules are recorded and tested.
- Old survey: Auth vs authorization.
- Chapters: Ch 7: Who You Are, What You May Do. Ch 8: Row Level Security.

**A4 APIs and integrations.** Calling other systems, including models, or offering an API.
- 3: can explain a request and response, and why calls fail.
- 4: the product calls an API (a model counts) and handles its failures.
- 5: chose the integration for a stated reason, and it works for real users.
- Old survey: APIs.
- Chapters: Ch 8: Requests Are Contracts That Fail. Ch 11: Where the Call Lives.

**A5 Secrets, privacy and security.** Keys out of the code, personal data protected.
- 3: can explain why a committed key is an incident and what never goes in a prompt.
- 4: keys live in environment variables or a secret store, never in the repo.
- 5: handles real users' data with the protections written down.
- Old survey: Environments and secrets; Data privacy; Security basics.
- Chapters: Ch 8: Secrets and Sensitive Data.

**A6 Version control, checks and tech debt.** History, review, what runs on every change, and what was deferred.
- 3: can explain branches, pull requests, continuous integration, and when debt is worth taking on.
- 4: works in branches or pull requests, or has automated tests or checks that run.
- 5: checks run on a product real users depend on, and the student can say what they catch.
- Old survey: Version control; Pull requests; CI.
- Chapters: Ch 9: Git; Pull Requests; Automated Checks; Rolling Back. Ch 9b: Tests; Technical Debt.

## Agentic Workflow

Putting AI to work: directing coding agents, and building AI into the product.

**W1 Directing coding agents.** Context files, plans, and specs fed to the agent.
- 3: can explain what a context file is for and when to plan before building.
- 4: wrote project instructions or specs that the agent works from.
- 5: can show how the instructions changed the agent's output, and why they are written that way.
- Old survey: Project instructions; The agent loop; Memory.
- Chapters: Ch 1: What Makes an Agent an Agent. Ch 2: It Knows Only What It Can See; Project Overview; Development Notes.

**W2 Agent tooling.** Skills, hooks, subagents, and tool connections such as MCP.
- 3: can explain when to package a workflow, and when parallel agents help or cost.
- 4: built a skill, hook, subagent or tool connection that runs.
- 5: it does real work in the product's development, and the student can defend the design.
- Old survey: Skills; Hooks; Subagents; MCP; Multi-agent orchestration.
- Chapters: Ch 2: Slash Commands; Skills; Rules; Advice Versus Enforcement; Delegation and Parallel Work; MCP.

**W3 Checking agent output.** Reviewing, testing and limiting what agents do.
- 3: can explain what to check in agent-written code, and what an agent may run unattended.
- 4: caught and fixed an agent's error, with the record, or set permissions on purpose.
- 5: checks agent work the same way every time, in a product real users use.
- Old survey: Code review of agent output; Testing AI-written code; Agent permissions.
- Chapters: Ch 2: Blast Radius; Done Means You Saw It Work.

**W4 Prompts in the product.** Features driven by prompts the student wrote.
- 3: can explain instructions, examples and structured output.
- 4: built a feature driven by a prompt they wrote.
- 5: real users use the feature, and prompt versions are kept with why each changed.
- Old survey: Prompt engineering.
- Chapters: Ch 11: Prompts Are Product Code; Getting Structured Output. Ch 10: Prompting.

**W5 Tool use and agent loops in the product.** The model calls tools and takes steps on its own.
- 3: can explain tool calling, stopping conditions and retries.
- 4: built tool use or a multi-step model action into the product.
- 5: real users rely on it, with the loop's limits written down.
- Old survey: Tool use and function calling; Loop design.
- Chapters: Ch 11: Tools and Agent Loops.

**W6 Evals.** Knowing whether AI output got better or just different.
- 3: can explain what an eval set is and why one example proves little.
- 4: built an eval set or scorer and ran it.
- 5: a prompt or model decision was made from eval results, recorded.
- Old survey: Evals.
- Chapters: Ch 11: Evals: Knowing Whether It Works.

## AI Systems

Understanding how models work and why they behave as they do. Level 4 here means the
understanding shaped something the student built.

**S1 Tokens and the context window.** What fills it, and what happens when it overflows.
- 3: can explain tokens, the context window, and what overflow does.
- 4: designed around the limit in their product (trimming, summarizing, chunking).
- 5: can defend the design with numbers from their own product.
- Old survey: Context window.
- Chapters: Ch 10: Step 1 (tokens); The context window is working memory. Ch 11: The API Remembers Nothing.

**S2 Cost and latency.** What makes a model call slow or expensive.
- 3: can estimate a call's cost and explain what drives latency.
- 4: measured cost or latency in their product.
- 5: changed the product because of the numbers, recorded.
- Old survey: Tokens, latency and cost.
- Chapters: Ch 11: What It Costs. Ch 12: Every AI call is a cost.

**S3 How models are made.** Pretraining, fine-tuning, and training from feedback.
- 3: can explain how a model is trained and what that means for what it knows.
- 4: a product decision depends on it (for example, what the model cannot know), recorded.
- 5: can defend that decision in an interview, citing their own product.
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
- 4: traced a wrong output in their product to its cause and fixed it.
- 5: verification is built into a product real users use.
- Old survey: Hallucination and verification.
- Chapters: Ch 10: Plausible is not true; The jagged frontier. Ch 11: Where It Breaks.

**S6 Choosing a model or technique.** Prompting, retrieval, fine-tuning, model size.
- 3: can explain when each technique fits.
- 4: chose a model or technique in their product, with the reason.
- 5: the choice is backed by a comparison from their own product.
- Old survey: none.
- Chapters: Ch 11: one paragraph on choosing a model (no section yet).

## Open

- Calibrate level 3 checks: one `/learn` or exam question per item, in the form "Your app needs X.
  What would you choose, and why?"
- Map each current student's 50 first-survey answers onto these items, where the old survey has a
  match, as a provisional starting point until the December re-run uses this inventory.
- Items the old survey has no match for (D3, D6, L1, L6, S3, S6) start at the student's axis mean.
