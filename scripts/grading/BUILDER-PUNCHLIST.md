# Builder system punch list (started 2026-10-14)

One linked system: the concept list is the spine; the book teaches each concept, the final exam
checks Know it, `/sprint-review` shows Used it, packets show Made it and Shipped it, tree rings
show growth, the baseline survey sets the center. A change to one updates the others.

Status: [ ] open, [~] in progress, [x] done, [?] needs Scott.

## 1. Concept lists (the spine)
- [x] Agentic Workflow: `builder-concepts-agentic.md` (27 concepts, 72 checks)
- [~] Application Architecture
- [~] AI Systems
- [~] Discovery
- [~] Design
- [~] Launch and Learn
- [ ] One generator for all six: concept list in the repo, coverage page (with exam mapping) in `_materials/builder-exam/`
- [ ] Inventory points to the concept lists; the 37 items become headings
- [?] Scott reviews all six lists

## 2. Agreement (is the coding reliable?)
- [ ] Two independent coders, 12 students, against the concept lists; agreement and kappa per concept
- [ ] Rewrite concepts below the target (80% exact, kappa about 0.7)

## 3. Evidence paths
- [x] Agentic Workflow Used it: `/sprint-review` scan (skills, hooks, subagents, MCP, CLI, API calls, plugins, messages, modes, memory)
- [x] Packets: written work first, commit order, authors, full messages, .docx
- [ ] Each other axis: a packet or scan signal for every Used and Made check, or the check is marked not observable
- [ ] `/sprint-review` "Users this sprint" table (dated record for real users)

## 4. Book gaps
- [?] "Script or model" section (Ch 2) and counterpart (Ch 11): waiting on the rest of Scott's note
- [ ] Choosing a model or technique (S6 has one paragraph)
- [ ] Ch 11's prompts, tool use and evals sit in the AI Systems part; Agentic Workflow by definition
- [ ] Gaps found by each axis's concept list
- [x] Ch 2: three routes beyond the repo, connectors, plugins, permission modes, commands to know, Remote Control, voice, messaging

## 5. Final exam (blueprint = concept lists)
- [?] Change the writing-guide rule "do not repeat the same tested concept between midterm and final" to "never repeat a question; a concept may return in a new situation"
- [ ] Map all final items (seated and spare) to concepts, every axis
- [ ] At least one seated final question per concept
- [ ] Write questions for uncovered concepts; cut or reassign items that map to no concept
- [x] Agentic Workflow spares written: routes, connectors, plugins, slash commands (two matching sets), modes, remote control, voice, messaging

## 6. Growth and the dossier
- [ ] Growth code on concept checks (Know, Used, Made, Shipped); each ring attributed to concepts
- [ ] Dossier: "How you grew" and the appendix show the concept list and the student's checks
- [ ] Old survey answers mapped to concepts as a provisional center

## 7. Baseline survey
- [ ] New survey from the concept lists: one grid per axis, Know / Used / Made boxes
- [ ] Parser and charts (`baseline_profiles.py`) read it

## Alongside
- [?] Sprint 2 grading for the rest of the class (Workflow, about 5M tokens) with the current report
- [ ] `/learn` checks aligned to Know it (know / use / predict)
