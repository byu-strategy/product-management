# Six-axis refactor punch list

Working checklist for the outline refactor in `_outline-refactor-map.md`.
Not student-facing. Check items off as they land.

## Phase A. Assemble the 13 new chapters

Old files stay live in `_quarto.yml` until Phase B, so the site stays coherent
throughout. Each chapter is its own commit.

- [ ] Ch 1  Building with AI Agents          (assembly + six-axes intro)
- [ ] Ch 2  Directing the Agent              (assembly, folds spec-driven-dev)
- [ ] Ch 3  What Is Worth Building           (assembly)
- [ ] Ch 4  Finding and Validating the Problem (assembly, oversized, may split)
- [ ] Ch 5  Interface and Flow               (assembly + NEW design fundamentals)
- [ ] Ch 6  Testing the Design               (assembly)
- [ ] Ch 7  Data, Auth, and APIs             (assembly)
- [ ] Ch 8  Version Control, Testing, Tech Debt (assembly)
- [ ] Ch 9  How Models Work                  (publish the orphan, reshape)
- [ ] Ch 10 Models in Your Product           (NEW writing)
- [ ] Ch 11 Going to Market                  (assembly + NEW build half)
- [ ] Ch 12 Measuring What Matters           (assembly)
- [ ] Ch 13 Storytelling and the Final Demo  (assembly)

## Phase B. Flip the book

- [ ] `_quarto.yml`: six axis parts, new chapter order
- [ ] Delete retired files: `00-setup`, `01-vibe-coding`,
      `02-spec-driven-development`, `02-llms-prompt-engineering`, and the
      14 old topic chapters once their content has moved
- [ ] Retire slide decks that reference dead chapters (`01-pm-ai-era-slides`,
      `05-go-to-market-slides`) or repoint them

## Phase C. Realign everything that references chapters

- [ ] `00-schedule.qmd`: 13 classes on the axis order, readings table, drills
- [ ] `00-assessments.qmd`: quiz rows out, midterm and final in, LO tags
- [ ] `index.qmd`: grading table (quizzes to exams), stale description,
      Claude Max vs Pro contradiction, January dates on a Fall course
- [ ] Cross-reference sweep: every `](NN-name.qmd)` in the book
- [ ] `CLAUDE.md`: content structure section, chapter naming convention

## Phase D. Verify

- [ ] Full `quarto render` clean
- [ ] No orphan links, no dead anchors
- [ ] TOC reads as the six axes

## New writing required

- [ ] Ch 5: visual fundamentals, layout, type, component patterns, "client ready"
- [ ] Ch 10: model APIs, structured output, cost and latency, failure modes, evals
- [ ] Ch 11: landing pages, SEO, basic instrumentation
- [ ] Ch 1: the six axes introduced, hexagon baseline
- [ ] Key Concepts sections for chapters missing them

## Deliberately out of scope for this pass

- Grading model change (points model stays; grid is next year)
- Sprint rewrites (role-neutral language, floor/goal taper)
- Exam item banks
- Builder Axes index page
