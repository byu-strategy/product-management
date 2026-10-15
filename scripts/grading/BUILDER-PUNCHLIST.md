# Builder system punch list (started 2026-10-14)

One linked system: the concept list is the spine; the book teaches each concept, the final exam
checks Know it, `/sprint-review` shows Used it, packets show Built it and Shipped it, tree rings
show growth, the baseline survey sets the center. A change to one updates the others.

Status: [ ] open, [~] in progress, [x] done, [?] needs Scott.

## 0. Sprint 2 rollout with builder profiles (Scott, 2026-10-14: profiles ship with Sprint 2)

Stage A (no prerequisites, parallel)
- [~] Roster refresh; packets for every student on the current format (first five rebuilt)
- [ ] Drive files through the connector
- [ ] Coder instructions: one packet against the concept lists and evidence rules, output checks earned (Used, Built, Shipped) with evidence, ref and date
- [ ] Growth rule and code: center = self-rating; ring = checks newly earned on the axis as a share of its possible checks, on the 1 to 5 scale; each check named
- [ ] Dossier in `sprint_feedback.py`: score card, profile, how you grew, what was reviewed, Sprint 3, questions, appendix (concept list)

Stage B (needs A): is the coding faithful?
- [ ] Agreement test: two independent coders, 12 students, Sprint 2; agreement and kappa per concept
- [ ] Rewrite or drop concepts below target; settle Used versus Built per axis from the data

Stage C (needs B): production
- [ ] Grading run, whole class
- [?] Concept coding: two coders per student, Sprints 1 and 2, consensus only (about 8M tokens; Claude API batch proposed, cost estimate first)

Stage D (needs C): review
- [ ] Fairness check; build every dossier; disputed checks listed for Scott, never shown to students
- [?] Scott reviews the review page and a sample of dossiers

Stage E: publish through `/publish-grades`

## 1. Concept lists (the spine)
- [x] Agentic Workflow: `builder-concepts-agentic.md` (27 concepts, 72 checks)
- [x] Application Architecture, AI Systems, Discovery, Design, Launch and Learn (175 concepts in all; every bank question mapped)
- [x] One generator for all six: concept list in the repo, coverage page (with exam mapping) in `_materials/builder-exam/`
- [ ] Inventory points to the concept lists; the 37 items become headings
- [?] Scott reviews all six lists

## 2. Agreement (is the coding reliable?)
- [ ] Two independent coders, 12 students, against the concept lists; agreement and kappa per concept
- [ ] Rewrite concepts below the target (80% exact, kappa about 0.7)

## 3. Evidence paths
- [x] Agentic Workflow Used it: `/sprint-review` scan (skills, hooks, subagents, MCP, CLI, API calls, plugins, messages, modes, memory)
- [x] Packets: written work first, commit order, authors, full messages, .docx
- [ ] Each other axis: a packet or scan signal for every Used and Built check, or the check is marked not observable
- [ ] `/sprint-review` "Users this sprint" table (dated record for real users)

## 4. Book gaps
- [?] "Script or model" section (Ch 2) and counterpart (Ch 11): waiting on the rest of Scott's note
- [ ] Choosing a model or technique (S6 has one paragraph)
- [ ] Ch 11's prompts, tool use and evals sit in the AI Systems part; Agentic Workflow by definition
- [ ] Gaps found by each axis's concept list (listed at the end of each `builder-concepts-<axis>.md`; most common: how to write a decision record)
- [x] Ch 2: three routes beyond the repo, connectors, plugins, permission modes, commands to know, Remote Control, voice, messaging

## 5. Final exam (blueprint = concept lists)
- [?] Blueprint v2 drafted: `_materials/builder-exam/BLUEPRINT.md` (72 scored + 12 trial, 2 hours, weights unchanged, bank of 2 questions per concept, 3 for class 1-6 concepts)
- [ ] Form assembly script: checks counts, type split, one question per concept per form
- [x] Writing-guide rule changed: never repeat a question; a concept may return in a new situation (Scott, 2026-10-14)
- [x] Map all final items (seated and spare) to concepts, every axis
- [x] Bank filled: every concept has 2+ final questions; class 1-6 concepts have a midterm twin (243 written 2026-10-14, all spares; 475 in the bank)
- [ ] Review the new questions (agents flagged about 15 for a closer look; 7 marked beyond_taught, tied to book gaps)
- [ ] build.py vocabulary list: 'migration' and 'lint' are now taught (Ch 8, Ch 9)
- [ ] At least one seated final question per concept
- [ ] Write questions for uncovered concepts; cut or reassign items that map to no concept
- [x] Agentic Workflow spares written: routes, connectors, plugins, slash commands (two matching sets), modes, remote control, voice, messaging

## 6. Growth and the dossier
- [ ] Growth code on concept checks (Know, Used, Built, Shipped); each ring attributed to concepts
- [ ] Dossier: "How you grew" and the appendix show the concept list and the student's checks
- [ ] Old survey answers mapped to concepts as a provisional center

## 7. Baseline survey
- [ ] New survey from the concept lists: one grid per axis, Know / Used / Built boxes
- [ ] Parser and charts (`baseline_profiles.py`) read it

## Alongside
- [?] Sprint 2 grading for the rest of the class (Workflow, about 5M tokens) with the current report
- [ ] `/learn` checks aligned to Know it (know / use / predict)
