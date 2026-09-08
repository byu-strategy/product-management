# Six-axis refactor punch list

Working checklist for the outline refactor in `_outline-refactor-map.md`.
Not student-facing. Check items off as they land.

## Phase A. Assemble the 13 new chapters

Old files stay live in `_quarto.yml` until Phase B, so the site stays coherent
throughout. Each chapter is its own commit.

- [x] Ch 1  Building with AI Agents          (assembly + six-axes intro)
- [x] Ch 2  Directing the Agent              (assembly, folds spec-driven-dev)
- [x] Ch 3  What Is Worth Building           (assembly)
- [x] Ch 4  Finding and Validating the Problem (assembly, oversized, may split)
- [x] Ch 5  Interface and Flow               (assembly + NEW design fundamentals)
- [x] Ch 6  Testing the Design               (assembly)
- [x] Ch 7  Anatomy of an Application        (assembly + NEW tech stacks)
- [x] Ch 8  Data and APIs                    (assembly)
- [x] Ch 9  Version Control, Testing, Tech Debt (assembly)
- [x] Ch 10 How Models Work                  (publish the orphan, reshape)
- [x] Ch 11 Models in Your Product           (NEW writing)
- [x] Ch 12 Going to Market                  (assembly + NEW build half)
- [x] Ch 13 Measuring What Matters           (assembly)
- [x] Ch 14 Storytelling and the Final Demo  (assembly)

## Phase B. Flip the book

- [x] `_quarto.yml`: six axis parts, new chapter order
- [x] Delete retired files: `00-setup`, `01-vibe-coding`,
      `02-spec-driven-development`, `02-llms-prompt-engineering`, and the
      14 old topic chapters once their content has moved
- [ ] Retire slide decks that reference dead chapters (`01-pm-ai-era-slides`,
      `05-go-to-market-slides`) or repoint them

## Phase C. Realign everything that references chapters

- [x] `00-schedule.qmd`: 13 classes on the axis order, readings table, drills
- [x] `00-assessments.qmd`: quiz rows out, midterm and final in, LO tags
- [x] `index.qmd`: grading table (quizzes to exams), stale description,
      Claude Max vs Pro contradiction, January dates on a Fall course
- [x] Cross-reference sweep: every `](NN-name.qmd)` in the book
- [x] `CLAUDE.md`: content structure section, chapter naming convention

## Phase D. Verify

- [x] Full `quarto render` clean
- [x] No orphan links, no dead anchors
- [x] TOC reads as the six axes

## New writing required

- [x] Ch 7: tech stacks and languages (Scott has an image)
- [x] Ch 5: visual fundamentals, layout, type, component patterns, "client ready"
- [x] Ch 10: model APIs, structured output, cost and latency, failure modes, evals
- [x] Ch 11: landing pages, SEO, basic instrumentation
- [x] Ch 1: the six axes introduced, hexagon baseline
- [ ] Key Concepts sections for chapters missing them

## Deliberately out of scope for this pass

- Grading model change (points model stays; grid is next year)
- Sprint rewrites (role-neutral language, floor/goal taper)
- Exam item banks
- Builder Axes index page

## Still open after the first pass

- [ ] Ch 5 Interface and Flow: the visual design writing (layout, type, component
      patterns, what "client ready" means). Thinnest chapter at ~2,000 words.
- [ ] Ch 12 Going to Market: the build half, landing pages and SEO.
- [ ] Ch 4 is 5,800 words and 27 sections. Split or compress.
- [ ] Retire or repoint the two slide decks that reference dead chapters
      (`01-pm-ai-era-slides.qmd`, `05-go-to-market-slides.qmd`).
- [ ] Sprint rewrites: role-neutral language, the floor/goal taper, the
      confidentiality clause for sandbox students.
- [ ] Exam item banks: 40 midterm, 60 final.
- [ ] `company-template` as a real GitHub template; rename `practice-log`.
- [ ] Builder Axes index page (upgrade of `97-builder-resources.qmd`).
