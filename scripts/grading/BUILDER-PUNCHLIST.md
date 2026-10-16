# Builder system punch list (started 2026-10-14)

One linked system: the concept list is the spine; the book teaches each concept, the final exam
checks Know it, `/sprint-review` shows Used it, packets show Built it and Shipped it, tree rings
show growth, the baseline survey sets the center. A change to one updates the others.

Status: [ ] open, [~] in progress, [x] done, [?] needs Scott.

## 0. Sprint 2 rollout with builder profiles (Scott, 2026-10-14: profiles ship with Sprint 2)

**Design, as of 2026-10-16.** Each axis runs 0 to 100; 100 is a full-stack product builder. Sprint
work fills up to 50 (AI Systems 25): 70% breadth (share of the axis's practicable concepts shown),
30% depth (highest level: Followed earns 0, Directed 20%, Decided 50%, Delivered 100%). Exams fill the
rest; the midterm replaces the September self-rating center on the three axes it tests (up or down),
the September rating stays as a dashed outline, and sprint rings never shrink. One coder per student
(in the grading pass) plus a targeted check of close calls and depth 3-4 (`concept-verifier.md`)
replaced two full coders on 2026-10-16. The report and review page are locked by
`scripts/tests/test_report.py`. Coherence audit: `_materials/product-management/coherence-audit-2026-10-16.md`.

Step 1. Inputs (parallel)
- [x] Roster refresh
- [~] Sprint 2 packets for every student, current format (first five rebuilt)
- [ ] Sprint 1 packets checked: present for all, rebuilt on the current format if needed
- [ ] Drive files through the connector, both sprints

Step 2. Measures
- [x] Concept lists: one breadth check per practicable concept; knowledge-only concepts marked (29 of 175)
- [x] Depth levels: four written levels per axis with one worked example each (`depth-levels.md`)
- [x] Coder instructions rewritten for breadth and depth (`concept-coder.md`)
- [x] Growth code: breadth and depth, per-axis split, rings by source, consensus (`builder_growth.py`, tested on synthetic codings)

Step 3. Agreement test (Scott sees the numbers)
- [ ] Two independent coders, 12 students, Sprint 2
- [ ] Breadth agreement 80%+ ; depth same or one apart on 80%+ of axes
- [ ] Rewrite or drop what falls short; rerun if needed

Step 4. Dossier in the pipeline
- [~] `sprint_feedback.py` builds the dossier: score card (Plan first, /50), builder profile, how you
      grew, what was reviewed, Sprint 3, questions, appendix (concept list); Scott's copy adds the
      instructor band and the disputed calls

Step 5. Production runs (after step 3 passes)
- [?] Cost estimate for coding (Claude API batch proposed) and grading; Scott approves
- [ ] Grading run, whole class (regrade the first five on current packets)
- [ ] Coding run: two coders per student, Sprints 1 and 2; consensus only; depth takes the lower level
- [ ] Growth computed for every student

Step 6. Review
- [ ] Fairness check on grades
- [ ] Build every dossier and the review page
- [?] Scott reviews the review page and a sample of dossiers

Step 7. Publish
- [?] `/publish-grades` (dossier attached on Canvas) after Scott approves

Step 8. Skills catch up
- [ ] `/grade-sprint`: coding, growth, dossier, token budget, linked-system rule
- [ ] `/publish-grades`: attach the dossier HTML
- [ ] `/sprint-review`: "Decisions this sprint" (choices from sessions, student names key ones) and
      "Users this sprint" table; push to builder-template with Scott's OK

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
