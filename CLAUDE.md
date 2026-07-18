# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Quarto book project for **MSB 341 - Product Management**, a BYU course taught by Scott Murff. The project generates a static website containing course materials, schedules, assessments, and chapter content.

The course was previously numbered STRAT 490R ("Creating Digital Products with AI"); it reverted to a standard number for Fall 2026. It is cross-listed under three numbers that all meet together as one class: MSB 341 (sec 002), IS 693R (sec 008), and C S 498R (sec 005). The class meets Mondays 3:30 to 4:45 PM in 2439 TNRB and uses Canvas as the LMS.

### Location and deployment

- **Canonical repo:** `~/Documents/courses/product-management` (a fork of the older `strategy-prototyping` repo, moved off OneDrive). Full git history is preserved.
- **GitHub:** `byu-strategy/product-management`. **Live site:** https://byu-strategy.github.io/product-management/
- The old `strategy-prototyping` repo (on OneDrive, GitHub `byu-strategy/strategy-prototyping`) is the archived STRAT 490R version. Do not commit new course work there.

### Teaching model (the practice model)

Class is run like an athletic practice: Scott is the coach, students are full-stack product builder athletes, and Claude Code is the tool of instruction (every student has a Claude Max plan). Each Monday session is a "practice" with an emphasis, a daily scripture and quote, whistle segments (film review, chalk talk) for full attention, and live drill time building with Claude Code. Supporting artifacts in the repo:

- `practice-plan-template.md`: the minute-by-minute daily plan template. Season benchmarks (sprints, quizzes, peer work) are published in `00-schedule.qmd`; individual practice plans are written the week of and published after class.
- `company-template/`: scaffold for each student's one-person company repo (the repo is the whole company: product, specs, discovery, gtm, decisions, metrics, practice-log). Intended to become a GitHub template. Students add Scott as a collaborator.
- `repo-analysis/`: `analyze.py` reads a roster and produces a team stat sheet (commit cadence, folder-category balance, artifact counts) for coaching and film selection. Never grade raw commit counts; use the sheet to pick coaching conversations, then read the artifacts.

**Jargon rule:** use athletic language (practice, film, drill, scrimmage, reps, emphasis, huddle) for the in-room cadence and culture. Use industry terms (sprint, PRD, MVP, discovery, code review, retro) for anything assessed, documented, or resume-transferable. Schedule and assessments stay in industry terms; the practice plans and room framing use the athletic terms. Drop the metaphor whenever precision matters.

## Architecture

### Content Structure
- **Course Information**: `index.qmd`, `00-schedule.qmd`, `00-assessments.qmd` - Core course logistics and grading
- **Topic Chapters**: Numbered `.qmd` files (01-14) covering course topics from AI/PM basics to final presentations
- **Resources**: `97-resources.qmd`, `98-tools.qmd`, `99-prompts.qmd` - Supplementary materials
- **Configuration**: `_quarto.yml` defines the book structure, chapters order, and output settings

### Build System
- **Primary tool**: Quarto (installed at `/usr/local/bin/quarto`)
- **Output**: Static HTML website generated to `_book/` directory (configured in `_quarto.yml`)
- **Assets**: Images stored in `images/` directory, copied to output during build
- **Python Engine**: Project uses Jupyter for python code execution (Python 3.12+)
- **Deployment**: Automated via GitHub Actions to GitHub Pages on push to main branch

## Common Commands

### Build and Preview
```bash
# Build the entire book
quarto render

# Preview with live reload during development
quarto preview

# Build and serve locally
quarto serve
```

### Chapter Management
- All chapters are defined in `_quarto.yml` under the `book.chapters` section with three parts: "Course Information", "Topics", and "Resources"
- Chapter files follow naming convention: `##-topic-name.qmd`
- When adding new chapters, update both the file and the YAML configuration
- Two versions exist for some files since two different course sections are taught (e.g., `00-schedule-sandbox.qmd`). APM stands for Associate Product Manager and Sandbox refers to students building their own companies. 

### Creating Presentation Slides
- The project supports RevealJS slide decks from chapter content
- Slide files use naming convention: `##-topic-name-slides.qmd`
- Slide format configuration includes:
  ```yaml
  format:
    revealjs:
      theme: [default, custom.scss]
      slide-number: true
      chalkboard: true
  ```
- Custom slide styling defined in `custom.scss` with BYU branding (navy #002E5D, royal blue #0057B8)
- Render slides with: `quarto render ##-topic-name-slides.qmd`

### File References
- Internal links between chapters use relative paths: `[Link Text](file.qmd)`
- Cross-references to assessments use anchors: `[Link](00-assessments.qmd#section-id)`
- All file references in content must match exactly with actual filenames

## Important Notes

- The project uses Quarto's book format with HTML output
- Bibliography references use `references.bib` with `informs.csl` style
- Custom CSS styling in `styles.css` for book pages
- Custom SCSS styling in `custom.scss` for RevealJS slides (BYU color scheme)
- Header/footer includes via `_header.html` and `_footer.html`
- Python code execution disabled by default (`execute: eval: false` in config)
- When renaming chapter files, update all references in `_quarto.yml`, schedule, assessments, and cross-links
- GitHub Actions workflow (`.github/workflows/publish.yml`) automatically builds and deploys to GitHub Pages on push to main

## Commit and push regime

This course site is a product. A push to `main` publishes it live to students via GitHub Pages, so committing and pushing are two different acts with two different owners.

- **Commit straight to `main`, no feature branches.** Solo-maintainer workflow. Recovery is `git reset` while unpushed, `git revert` once pushed. Never rewrite pushed history.
- **Commit often, without asking.** Committing is pre-authorized and always reversible. Commit after each unit of work; do not end a task with "want me to commit?".
- **Conventional prefixes, one concern per commit.** `feat:` / `fix:` / `content:` / `chore:` / `docs:`. A schedule change and a new chapter section are two commits, not one.
- **Stage explicit paths only.** Never `git add -A`, `git add .`, or `git commit -am`. The working tree often holds unrelated files (OneDrive artifacts, drafts, PDFs); never sweep them into a commit.
- **Do NOT push.** Pushing publishes to students, so it is the human's deliberate act. When work is committed, say it is ready and stop. The `/push` skill is the only sanctioned push path; invoking it is push authorization for that one run only.

## Working discipline (definition of done)

- **Render before calling it ready.** Any change to `.qmd` content, `_quarto.yml`, or styling must pass `quarto render` cleanly before commit. A broken render pushed to main is a broken deploy.
- **Check cross-references when files move or sections change.** Renames and anchor edits must be chased through `_quarto.yml`, the schedule, assessments, and cross-links; broken internal links are the top regression here.
- **Verify proportional to risk.** A typo or copy tweak needs only a clean render. Navigation changes, schedule restructures, and styling changes earn a look at the rendered output (`quarto preview`) before commit.
- **Never reformat or rewrite content you weren't asked to touch.** Keep diffs scoped to the task so review stays cheap.

## Copy voice

- **No em dashes, anywhere.** Not in course content, commit messages, code comments, or replies to Scott. Use a comma, colon, period, or "and" instead.
- **Plain and factual.** Direct, not flowery or salesy. Scott adds the flourishes himself. This applies to all student-facing copy: syllabus text, assignment instructions, announcements.
- **No emoji as UI or content decoration** unless explicitly asked.

## Mockups and design iteration

When asked for a design, layout, or "show me what X could look like" (site styling, slide themes, page layouts), build a high-fidelity, self-contained HTML mockup in `.mockups/` at the repo root (gitignored). Real fonts, spacing, and representative content. Finish by printing the clickable absolute `file://` path. Mockups are throwaway: once built into the site, they are done. Desktop only unless asked.