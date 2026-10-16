# Agentic Workflow concepts (draft, generated from concepts/agentic.json)

The named concepts under the Agentic Workflow items. Putting AI to work: directing coding agents, and building AI into the product.

Each concept is measured in up to two ways:

- **Know it** (every concept): the exams. Midterm and final questions on the concept come in three
  types (know it, use it, predict it). The September survey self-rating stands in until the midterm.
- **Practice** (every concept not marked knowledge only): the student's own work shows it, counted
  once. The **Practice** column says what counts as evidence: the `/sprint-review` session scan's
  "Builder tools you used" list, or a file in a shared repo. This is the breadth half of the profile's
  practice score; depth (`depth-levels.md`) is assigned per axis, not per concept.

A concept marked **knowledge only** has no practice check: it is measured by the exams alone.
Evidence rules are in `concept-coder.md` and `depth-levels.md`.

## W1 Directing coding agents

| Concept | Practice | Chapter |
|---|---|---|
| **AW01 The agent loop and the harness.** A model in a loop with tools: it gathers context, acts, and checks. The model writes; the harness carries out the actions. | knowledge only (exams) | Ch 1: What Makes an Agent an Agent |
| **AW02 Command line and packages.** Running commands, files and folders, package managers. | A committed change to package.json or a lockfile that adds or removes a package the product uses. | Ch 1: The Command Line |
| **AW03 Launching and surfaces.** Starting the agent in the right folder; the same engine in the terminal, desktop, IDE and web; following a session from the Claude mobile app (Remote Control); speaking prompts (/voice); non-interactive runs. | /remote-control, /voice or a non-interactive run listed in the session scan's "Builder tools you used" list in the review report, or a committed script that runs the agent without a person. | Ch 1: One engine, many surfaces; Ch 2: Claude Code: Slash Commands |
| **AW04 Project instructions (CLAUDE.md, AGENTS.md).** A file the agent reads at the start of every session: decisions, constraints, traps. Advisory, not enforced. | Text the student wrote in CLAUDE.md or AGENTS.md beyond the template's text, committed. | Ch 2: It Knows Only What It Can See; CLAUDE.md: your project's memory; Where CLAUDE.md files live |
| **AW05 Memory and context.** What persists between sessions (auto memory, CLAUDE.md) and what does not; /clear and /compact. | /clear, /compact or /memory listed in the session scan's "Builder tools you used" list in the review report, or a memory entry or rule the student added to CLAUDE.md or a memory file, committed. | Ch 2: It Knows Only What It Can See; What fills the window; The controls; CLAUDE.md and auto memory |
| **AW06 Plan mode.** Claude reads, explores and writes a plan without editing your files until you approve it. Writing the spec it builds from is Design's spec-driven development (DE20). | Plan mode listed in the session scan's "Builder tools you used" list in the review report. | Ch 6b: Claude Code's plan mode; Ch 2: The controls, from tightest to loosest |
| **AW07 Settings and their scope.** Project settings versus global settings, and which wins. | A .claude/settings.json the student added or changed beyond the template's copy, committed. | Ch 2: Permission rules; Claude Code hooks. Ch A3: The same engine |

## W2 Agent tooling

| Concept | Practice | Chapter |
|---|---|---|
| **AW08 Slash commands.** Commands run by name inside a session; text after the command is its argument. Must know by name: /context, /compact, /clear, /rewind, /resume, /rename, /list-agents (/peers), /btw, /exit, /remote-control (/rc), /voice, /init, /memory, /config, /model, /effort, /status, /usage, /add-dir, /plan, /permissions, /hooks, /sandbox, /skills, /mcp, /plugin, /diff, /help. | A built-in slash command listed in the session scan's "Builder tools you used" list in the review report (the course's own skills, such as /sprint-plan, /sprint-review and /learn, do not count), or a custom command the student wrote, committed. | Ch 2: Claude Code: Slash Commands |
| **AW09 Skills.** A saved procedure the agent runs by name, shared in the repo or kept personal. | A skill the student wrote in .claude/skills/<name>/SKILL.md, committed, or a skill that is not one of the course's skills listed in the session scan's "Builder tools you used" list in the review report. | Ch 2: Claude Code: Skills |
| **AW10 Hooks.** A command that runs every time an event happens: guaranteed, unlike an instruction. | A hook the student added to .claude/settings.json, committed, or a hook run listed in the session scan's "Builder tools you used" list in the review report. | Ch 2: Advice Versus Enforcement |
| **AW11 Advice versus enforcement.** Instructions advise; hooks and permission rules enforce. Knowing which to use for a rule. | knowledge only (exams) | Ch 2: Advice Versus Enforcement |
| **AW12 Subagents.** A separate agent with its own context, used to protect the main one or to work in parallel. | Subagents listed in the session scan's "Builder tools you used" list in the review report, or a subagent file the student wrote in .claude/agents/, committed. | Ch 2: Delegation and Parallel Work |
| **AW13 Reaching outside the repo: CLI tools, MCP servers, API calls.** Three routes to a system outside the repo: a CLI tool the agent runs (gh, supabase), an MCP server that adds the system's actions as tools (in the Claude app, a connector), or a direct API call the agent writes with a key. Choosing the route for a case. | A CLI tool, MCP server or API call listed in the session scan's "Builder tools you used" list in the review report, or an MCP server the student added to .mcp.json, or a committed script or skill the student wrote that wraps a CLI tool or an API. | Ch 2: Reach Beyond the Repo: CLI Tools, MCP, and APIs |
| **AW26 Plugins.** A package of skills, slash commands, subagents, hooks and MCP servers installed together with /plugin. A way to share building blocks, not a route to outside data; an enabled plugin costs context every session. | A plugin listed in the session scan's "Builder tools you used" list in the review report (its skills appear as plugin:skill), or a plugin the student wrote (.claude-plugin/plugin.json), committed. | Ch 2: Plugins: a package, not a route |
| **AW14 Parallel sessions, worktrees and messaging.** Several agents at once, each in its own working copy, and messages between them: /list-agents shows who Claude can reach; a message is plain text with no authority (it cannot approve a prompt or change settings). | Worktrees or messages to another session listed in the session scan's "Builder tools you used" list in the review report. | Ch 2: Parallel work needs separate copies of the files; Messaging your other sessions |

## W3 Checking agent output

| Concept | Practice | Chapter |
|---|---|---|
| **AW15 Permission modes.** Manual, Accept edits, Plan, Auto (a second model reviews each action), Don't ask (pre-approved tools only, for scripts), and Bypass permissions (--dangerously-skip-permissions: no prompts and no safety checks, for containers only). What each lets run without asking, and when to use it. | Accept edits, Auto or Don't ask mode listed in the session scan's "Builder tools you used" list in the review report. | Ch 2: The controls, from tightest to loosest |
| **AW27 Permission rules.** Allow, ask and deny rules in a settings file: ask and deny hold in every mode, including auto and bypass; a boundary said only in chat does not. | Allow, ask or deny rules the student added to a committed settings file, or a rule that prompted or blocked an action listed in the session scan's "Builder tools you used" list in the review report. | Ch 2: Permission rules; The controls, from tightest to loosest |
| **AW16 Blast radius and undo.** What an action can damage and what can be undone (/rewind, git); some actions are permanent. | /rewind listed in the session scan's "Builder tools you used" list in the review report, or a revert commit the student made. | Ch 2: Blast Radius |
| **AW17 Verifying agent work.** Done means you saw it work; a fresh-context review of agent-written code. | A committed record that the student checked agent-written work (a review note, saved test output, or a note of a check on the live site) that names what was checked and the result. | Ch 2: Done Means You Saw It Work |

## W4 Prompts in the product

| Concept | Practice | Chapter |
|---|---|---|
| **AW18 Prompts as product code.** Prompts in the product are versioned, tested and changed with reasons; examples for boundary cases. | A prompt, in a prompt file or in the code, that the product sends to a model, added or changed by the student and committed. | Ch 11: Prompts Are Product Code |
| **AW19 Structured output.** Asking the model for output in a fixed shape the code can rely on. | Committed code that asks a model for output in a fixed shape (a JSON schema, a tool definition, or a structured output setting) and parses it before the product uses it. | Ch 11: Getting Structured Output |
| **AW20 Streaming and the AI surface.** Showing output as it arrives, and the states an AI feature passes through. | Committed code that shows a model's response on screen as it arrives, or a Loom moment that shows a streamed response in the product. | Ch 11: Streaming |
| **AW21 Untrusted model input.** Text the model reads can carry instructions (prompt injection); privileged actions need a guard. | Committed code that guards an action the product takes from model output (a confirmation step, an allow list, or a check before the action runs), with a comment or record that names prompt injection or untrusted input as the reason. | Ch 11: Where It Breaks |
| **AW22 Non-determinism.** The same input can give different output; a feature must work across runs. | knowledge only (exams) | Ch 11: Where It Breaks |

## W5 Tool use and agent loops in the product

| Concept | Practice | Chapter |
|---|---|---|
| **AW23 Tool calling and agent loops in the product.** The model chooses the next step or calls a tool; stopping rules and a point where a person decides. | Committed code in which the model picks among two or more tools the product defines, the code runs the chosen tool and returns the result to the model, and a stopping rule (a step limit or an end condition) ends the loop. Sending a request to one provider or another does not count. | Ch 11: Tools and Agent Loops |

## W6 Evals and accuracy checks

| Concept | Practice | Chapter |
|---|---|---|
| **AW24 Evals.** A set of cases with known answers, a baseline, noise, and graders (code for exact answers, a model as judge). | A committed set of test cases with known answers, or a scorer, for model or product output, with saved results from a run. | Ch 11: Evals: Knowing Whether It Works |
| **AW25 Choosing a model by measurement.** Picking a model by running the same cases on each, not by reputation. | A committed comparison that runs the same cases on two or more models and saves the results for each. | Ch 11: What It Costs; Evals: Knowing Whether It Works |
