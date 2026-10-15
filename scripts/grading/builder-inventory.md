# Builder inventory (draft v1, 2026-10-14)

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

**D2 Problem and who it is for.** The problem, separate from the fix, and the people who have it.
- 3: can state a problem without naming a solution, and who it is not for.
- 4: wrote a problem statement or persona drawn from what users said.
- 5: real users recognize the problem in their own words, and the record says who was left out and why.
- Old survey: Problem vs solution; Personas and segments.

**D3 Assumption tests.** Finding the riskiest belief and testing it cheaply.
- 3: can name a product's riskiest assumption and a test that could prove it wrong.
- 4: ran a test (smoke test, landing page, survey, prototype) and recorded the result.
- 5: the result decided something, and the decision record cites it.
- Old survey: none.

**D4 Competitive landscape.** What else people use for the problem, and what is missing from it.
- 3: can explain why users would choose the product over what they use now, including doing nothing.
- 4: wrote a comparison of the alternatives users actually use.
- 5: the product's position comes from that comparison, and the student can defend it.
- Old survey: Competitive landscape.

**D5 Prioritization.** Ranking by value, effort and risk.
- 3: can explain why a team should build one thing before another.
- 4: ranked options in writing with the criteria shown.
- 5: built what ranked first for real users, and the ranking cites what was learned.
- Old survey: Prioritization.

**D6 Specs.** A description clear enough to build from.
- 3: can explain what makes a spec testable.
- 4: wrote a spec with acceptance criteria before building it.
- 5: shipped to real users against the spec, and recorded what changed in it and why.
- Old survey: Spec writing.

## Design

**G1 User flows.** What the user does, step by step.
- 3: can walk through a flow and say where users will drop off.
- 4: mapped a flow before or alongside the screens.
- 5: changed the flow because of what real users did, and recorded why.
- Old survey: User flows.

**G2 Visual fundamentals.** Hierarchy, spacing, contrast, accessibility.
- 3: can say why one screen reads more clearly than another.
- 4: applied them on purpose (a type scale, contrast checks, keyboard access).
- 5: real users use it without help, and the design choices are written down.
- Old survey: Usability fundamentals.

**G3 Design system.** Define a component once and reuse it.
- 3: can explain what a design system saves and what it costs.
- 4: built shared components or tokens used across the product.
- 5: chose the system over alternatives for a stated reason, in a product real users use.
- Old survey: Design systems.

**G4 States.** Empty, loading, error and success.
- 3: can list the states a screen needs and what goes wrong without them.
- 4: built the states for the product's main flow.
- 5: a state was added or changed because of what real users ran into.
- Old survey: none.

**G5 Critique and direction.** Saying specifically what is wrong and what to change.
- 3: can name specific problems in a generated screen and the change that fixes each.
- 4: directed design changes in writing (to an agent or a teammate) and they shipped.
- 5: can defend the product's design direction to someone who disagrees, with the record of why.
- Old survey: UI critique; Design direction.

**G6 Usability testing.** Watching a real person use it, then changing it.
- 3: can explain what a usability test can and cannot show.
- 4: ran a test with a real person and wrote down what happened.
- 5: changed the product because of it, and the change is recorded.
- Old survey: Prototype testing.

## Launch and Learn

**L1 Shipping to real people.** People other than the builder use it.
- 3: can explain the difference between launched and used.
- 4: put it in front of people outside the team.
- 5: people use it more than once, on their own.
- Old survey: none.

**L2 Instrumentation.** Logging what matters before launch.
- 3: can say what to log before launch and why.
- 4: built event logging or analytics into the product.
- 5: the data from real users answered a question the student asked in advance.
- Old survey: Instrumentation.

**L3 Metric selection.** One number that moves if the product works.
- 3: can explain why signups are not adoption.
- 4: defined a metric and collected it.
- 5: chose the metric over others for a stated reason, and it moved (or did not) with real users.
- Old survey: Metric selection; Activation and retention.

**L4 Experiments.** Tests of channel, copy, price or feature, with a result.
- 3: can explain what an A/B test can and cannot prove.
- 4: ran an experiment and recorded the result.
- 5: the result changed what was built or how it is offered.
- Old survey: Experiments.

**L5 Positioning and pricing.** Why someone chooses it, and what it is worth.
- 3: can state who it is for, what it replaces, and a reasoned price.
- 4: wrote positioning or a pricing model with numbers.
- 5: tested a price or position with real people and recorded what happened.
- Old survey: Positioning and pricing.

**L6 Acting on usage.** Deciding what to change, or stop, from what users did.
- 3: can explain how to decide what to build next from usage.
- 4: analyzed usage and wrote down what it showed.
- 5: changed or removed something because of it, with the record of why.
- Old survey: Usage analysis; Feature retirement.

## Application Architecture

**A1 Client, server and deploy.** What runs where, and how it goes live.
- 3: can explain what runs in the browser, what runs on a server, and how a build becomes a live app.
- 4: deployed it where others can reach it, and can read its logs.
- 5: chose the stack and host over alternatives for a stated reason, and real users reach it.
- Old survey: Client vs server; Deploy, builds and logs; Stack selection.

**A2 Data and schema.** Data that outlives a session, in a defined shape.
- 3: can explain tables, keys and relationships, and when a schema change breaks things.
- 4: defined a schema and the product stores data in it.
- 5: real users' data lives there, and the schema choices are written down.
- Old survey: Database schema design.

**A3 Sign-in and access.** Who you are, and what you may see.
- 3: can explain authentication versus authorization.
- 4: built sign-in and at least one access rule.
- 5: real users sign in, and the access rules are recorded and tested.
- Old survey: Auth vs authorization.

**A4 APIs and integrations.** Calling other systems, including models, or offering an API.
- 3: can explain a request and response, and why calls fail.
- 4: the product calls an API (a model counts) and handles its failures.
- 5: chose the integration for a stated reason, and it works for real users.
- Old survey: APIs.

**A5 Secrets, privacy and security.** Keys out of the code, personal data protected.
- 3: can explain why a committed key is an incident and what never goes in a prompt.
- 4: keys live in environment variables or a secret store, never in the repo.
- 5: handles real users' data with the protections written down.
- Old survey: Environments and secrets; Data privacy; Security basics.

**A6 Version control and checks.** History, review, and what runs on every change.
- 3: can explain branches, pull requests and continuous integration.
- 4: works in branches or pull requests, or has automated tests or checks that run.
- 5: checks run on a product real users depend on, and the student can say what they catch.
- Old survey: Version control; Pull requests; CI.

## Agentic Workflow

Putting AI to work: directing coding agents, and building AI into the product.

**W1 Directing coding agents.** Context files, plans, and specs fed to the agent.
- 3: can explain what a context file is for and when to plan before building.
- 4: wrote project instructions or specs that the agent works from.
- 5: can show how the instructions changed the agent's output, and why they are written that way.
- Old survey: Project instructions; The agent loop; Memory.

**W2 Agent tooling.** Skills, hooks, subagents, and tool connections such as MCP.
- 3: can explain when to package a workflow, and when parallel agents help or cost.
- 4: built a skill, hook, subagent or tool connection that runs.
- 5: it does real work in the product's development, and the student can defend the design.
- Old survey: Skills; Hooks; Subagents; MCP; Multi-agent orchestration.

**W3 Checking agent output.** Reviewing, testing and limiting what agents do.
- 3: can explain what to check in agent-written code, and what an agent may run unattended.
- 4: caught and fixed an agent's error, with the record, or set permissions on purpose.
- 5: checks agent work the same way every time, in a product real users use.
- Old survey: Code review of agent output; Testing AI-written code; Agent permissions.

**W4 Prompts in the product.** Features driven by prompts the student wrote.
- 3: can explain instructions, examples and structured output.
- 4: built a feature driven by a prompt they wrote.
- 5: real users use the feature, and prompt versions are kept with why each changed.
- Old survey: Prompt engineering.

**W5 Tool use and agent loops in the product.** The model calls tools and takes steps on its own.
- 3: can explain tool calling, stopping conditions and retries.
- 4: built tool use or a multi-step model action into the product.
- 5: real users rely on it, with the loop's limits written down.
- Old survey: Tool use and function calling; Loop design.

**W6 Evals.** Knowing whether AI output got better or just different.
- 3: can explain what an eval set is and why one example proves little.
- 4: built an eval set or scorer and ran it.
- 5: a prompt or model decision was made from eval results, recorded.
- Old survey: Evals.

## AI Systems

Understanding how models work and why they behave as they do. Level 4 here means the
understanding shaped something the student built.

**S1 Tokens and the context window.** What fills it, and what happens when it overflows.
- 3: can explain tokens, the context window, and what overflow does.
- 4: designed around the limit in their product (trimming, summarizing, chunking).
- 5: can defend the design with numbers from their own product.
- Old survey: Context window.

**S2 Cost and latency.** What makes a model call slow or expensive.
- 3: can estimate a call's cost and explain what drives latency.
- 4: measured cost or latency in their product.
- 5: changed the product because of the numbers, recorded.
- Old survey: Tokens, latency and cost.

**S3 How models are made.** Pretraining, fine-tuning, and training from feedback.
- 3: can explain how a model is trained and what that means for what it knows.
- 4: a product decision depends on it (for example, what the model cannot know), recorded.
- 5: can defend that decision in an interview, citing their own product.
- Old survey: none.

**S4 Retrieval and embeddings.** Giving a model the right material, and where retrieval fails.
- 3: can explain embeddings, chunking and where retrieval fails.
- 4: built retrieval into the product.
- 5: measured retrieval quality and changed it because of the result.
- Old survey: RAG.

**S5 Hallucination and verification.** Why models make things up, and what must be checked.
- 3: can explain why models hallucinate and what to verify.
- 4: traced a wrong output in their product to its cause and fixed it.
- 5: verification is built into a product real users use.
- Old survey: Hallucination and verification.

**S6 Choosing a model or technique.** Prompting, retrieval, fine-tuning, model size.
- 3: can explain when each technique fits.
- 4: chose a model or technique in their product, with the reason.
- 5: the choice is backed by a comparison from their own product.
- Old survey: none.

## Open

- Calibrate level 3 checks: one `/learn` or exam question per item, in the form "Your app needs X.
  What would you choose, and why?"
- Map each current student's 50 first-survey answers onto these items, where the old survey has a
  match, as a provisional starting point until the December re-run uses this inventory.
- Items the old survey has no match for (D3, G4, L1, S3, S6) start at the student's axis mean.
