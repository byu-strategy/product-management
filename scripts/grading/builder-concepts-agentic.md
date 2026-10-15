# Agentic Workflow concepts (draft, 2026-10-14)

The named concepts under the six Agentic Workflow items in `builder-inventory.md`. Each concept has
up to four checks, each counted once:

- **Know it**: says what it is and when to use it. Evidence: final exam questions on the concept
  (and `/learn` checks). Self-rated in the survey until the exam.
- **Used it**: used it in their own work. Evidence: the `/sprint-review` session scan, or the repo.
- **Made it**: built one. Evidence: a file they wrote, committed in a shared repo.
- **Shipped it**: made it for real users and chose it on purpose (the inventory's level 5 rules).

A blank cell means the check does not apply to that concept. Evidence rules from the inventory apply.

## W1 Directing coding agents

| Concept | Used it | Made it | Shipped it | Chapter |
|---|---|---|---|---|
| **AW01 The agent loop and the harness.** A model in a loop with tools: it gathers context, acts, and checks. The model writes; the harness carries out the actions. | n/a | n/a | n/a | Ch 1: What Makes an Agent an Agent |
| **AW02 Command line and packages.** Running commands, files and folders, package managers. | commands run in sessions | n/a | n/a | Ch 1: The Command Line |
| **AW03 Launching and surfaces.** Starting the agent in the right folder; the same engine in the terminal, desktop, IDE and web; following a session from the Claude mobile app (Remote Control); speaking prompts (/voice); non-interactive runs. | sessions started in the course repo; /remote-control or /voice used in sessions | a script that runs the agent without a person (non-interactive) | n/a | Ch 1: One engine, many surfaces; Ch 2: Your phone and your voice |
| **AW04 Project instructions (CLAUDE.md, AGENTS.md).** A file the agent reads at the start of every session: decisions, constraints, traps. Advisory, not enforced. | the file loads in sessions | wrote its content (beyond the template), committed | n/a | Ch 2: It Knows Only What It Can See; Project Overview |
| **AW05 Memory and context.** What persists between sessions (auto memory, CLAUDE.md) and what does not; /clear and /compact. | memory written or /clear, /compact used in sessions | wrote a memory entry or rule on purpose, committed | n/a | Ch 2: Development Notes |
| **AW06 Plan mode and spec first.** Exploring and planning before editing; handing the agent a spec. | sessions in plan mode | a spec the agent built from (counts as G4) | n/a | Ch 2; Ch 6b: The SDD Workflow |
| **AW07 Settings and their scope.** Project settings versus global settings, and which wins. | n/a | committed .claude/settings.json | n/a | Ch 2: Rules |

## W2 Agent tooling

| Concept | Used it | Made it | Shipped it | Chapter |
|---|---|---|---|---|
| **AW08 Slash commands.** Commands run by name inside a session; text after the command is its argument. Must know by name: /context, /compact, /clear, /rewind, /resume, /rename, /btw, /exit, /remote-control (/rc), /voice, /init, /memory, /config, /model, /effort, /status, /usage, /add-dir, /plan, /permissions, /hooks, /sandbox, /skills, /mcp, /plugin, /diff, /help. | slash commands used in sessions (the scan lists them) | wrote a custom command or skill run by name | n/a | Ch 2: Claude Code: Slash Commands |
| **AW09 Skills.** A saved procedure the agent runs by name, shared in the repo or kept personal. | a skill invoked in sessions | wrote .claude/skills/<own>/SKILL.md | others use it (a classmate, a team, users) | Ch 2: Claude Code: Skills |
| **AW10 Hooks.** A command that runs every time an event happens: guaranteed, unlike an instruction. | a hook ran in sessions | a hook committed in .claude/settings.json | n/a | Ch 2: Advice Versus Enforcement |
| **AW11 Advice versus enforcement.** Instructions advise; hooks and permission rules enforce. Knowing which to use for a rule. | n/a | n/a | n/a | Ch 2: Advice Versus Enforcement |
| **AW12 Subagents.** A separate agent with its own context, used to protect the main one or to work in parallel. | subagents launched in sessions | wrote .claude/agents/<name>.md | n/a | Ch 2: Delegation and Parallel Work |
| **AW13 Reaching outside the repo: CLI tools, MCP servers, API calls.** Three routes to a system outside the repo: a CLI tool the agent runs (gh, supabase), an MCP server that adds the system's actions as tools (in the Claude app, a connector), or a direct API call the agent writes with a key. Choosing the route for a case. | any of the three in sessions (the scan lists each) | added an MCP server to .mcp.json, or wrote a script or skill that wraps a CLI tool or an API | n/a | Ch 2: Reach Beyond the Repo: CLI Tools, MCP, and APIs |
| **AW26 Plugins.** A package of skills, slash commands, subagents, hooks and MCP servers installed together with /plugin. A way to share building blocks, not a route to outside data; an enabled plugin costs context every session. | a plugin installed and used (its skills appear as plugin:skill) | wrote a plugin (.claude-plugin/plugin.json) | others install it | Ch 2: Plugins: a package, not a route |
| **AW14 Parallel sessions and worktrees.** Several agents at once, each in its own working copy. | parallel sessions or worktrees in sessions | n/a | n/a | Ch 2: Delegation and Parallel Work |

## W3 Checking agent output

| Concept | Used it | Made it | Shipped it | Chapter |
|---|---|---|---|---|
| **AW15 Permission modes.** Manual, Accept edits, Plan, Auto (a second model reviews each action), Don't ask (pre-approved tools only, for scripts), and Bypass permissions (--dangerously-skip-permissions: no prompts and no safety checks, for containers only). What each lets run without asking, and when to use it. | the modes used in sessions (the scan counts turns in each) | n/a | n/a | Ch 2: The controls, from tightest to loosest |
| **AW27 Permission rules.** Allow, ask and deny rules in a settings file: ask and deny hold in every mode, including auto and bypass; a boundary said only in chat does not. | a rule prompted or blocked in sessions | committed allow, ask or deny rules | n/a | Ch 2: Rules; The controls, from tightest to loosest |
| **AW16 Blast radius and undo.** What an action can damage and what can be undone (/rewind, git); some actions are permanent. | /rewind or a revert in sessions | n/a | n/a | Ch 2: Blast Radius |
| **AW17 Verifying agent work.** Done means you saw it work; a fresh-context review of agent-written code. | n/a | a recorded check of agent work (a review note, a test run, a check on the live site) | n/a | Ch 2: Done Means You Saw It Work |

## W4 Prompts in the product

| Concept | Used it | Made it | Shipped it | Chapter |
|---|---|---|---|---|
| **AW18 Prompts as product code.** Prompts in the product are versioned, tested and changed with reasons; examples for boundary cases. | n/a | a prompt file in the repo that the product uses | real users use the feature; versions kept with reasons | Ch 11: Prompts Are Product Code |
| **AW19 Structured output.** Asking the model for output in a fixed shape the code can rely on. | n/a | a schema the product enforces on model output | real users use the feature | Ch 11: Getting Structured Output |
| **AW20 Streaming and the AI surface.** Showing output as it arrives, and the states an AI feature passes through. | n/a | a streamed response in the product | real users use the feature | Ch 11: Streaming |
| **AW21 Untrusted model input.** Text the model reads can carry instructions (prompt injection); privileged actions need a guard. | n/a | a guard on privileged actions in the product | real users use the guarded feature | Ch 11: Where It Breaks |
| **AW22 Non-determinism.** The same input can give different output; a feature must work across runs. | n/a | n/a | n/a | Ch 11: Where It Breaks |

## W5 Tool use and agent loops in the product

| Concept | Used it | Made it | Shipped it | Chapter |
|---|---|---|---|---|
| **AW23 Tool calling and agent loops in the product.** The model chooses the next step or calls a tool; stopping rules and a point where a person decides. | n/a | a loop or tool call in the product, with a stopping rule | real users rely on it; limits written down | Ch 11: Tools and Agent Loops |

## W6 Evals and accuracy checks

| Concept | Used it | Made it | Shipped it | Chapter |
|---|---|---|---|---|
| **AW24 Evals.** A set of cases with known answers, a baseline, noise, and graders (code for exact answers, a model as judge). | evals run, results saved | an eval set or scorer in the repo | a product decision made from saved results | Ch 11: Evals: Knowing Whether It Works |
| **AW25 Choosing a model by measurement.** Picking a model by running the same cases on each, not by reputation. | n/a | a recorded comparison of models on the product's own cases | the product runs the chosen model for real users | Ch 11: one paragraph |
