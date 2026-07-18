---
name: push
description: Publish the course site. Verifies the book renders cleanly, reviews exactly what will go live, then pushes main to GitHub (which triggers the GitHub Actions build and deploy to GitHub Pages, i.e. what students see). Use when the user says "push", "publish", "ship it", or "deploy". This is the ONLY sanctioned way to push; the standing rule is commit-don't-push, and invoking this skill is the user's explicit push authorization for this one run.
---

# push: verify, then publish the course site

Pushing `main` deploys the live course site students use. A push should never
publish a broken render or content the user hasn't seen described. Invocation of
this skill counts as the explicit "push now" authorization required by
CLAUDE.md; it does NOT carry over to later turns.

## Procedure

1. **Preflight.**
   - `git status --short`. Uncommitted changes that look like finished work the
     user just asked about: stop and ask whether to commit them first. Unrelated
     untracked files (PDFs, drafts, OneDrive artifacts) stay out.
   - Confirm you are on `main`.
   - `git fetch origin`, then `git log origin/main..HEAD --oneline`: know
     exactly what this push will publish. If there is nothing to push, say so
     and stop.

2. **Verify the render.** Run `quarto render` and confirm it completes with no
   errors. If it fails, fix or report; never push a broken build. For pushes
   that touch navigation, the schedule, or `_quarto.yml`, spot-check the
   relevant output in `_book/` (chapter present, links resolve).

3. **Push.** `git push origin main`. Confirm success (`git status` shows up to
   date with origin/main). Never force-push.

4. **Report.** Summarize in plain language what just went live: the commits
   published and the student-visible changes (new content, schedule updates,
   fixes). Note that GitHub Actions is now building and the site updates in a
   few minutes. No em dashes.

## Failure handling

- If the push is rejected (remote ahead), `git pull --rebase origin main`,
  re-run `quarto render`, and push again. Never force-push.
