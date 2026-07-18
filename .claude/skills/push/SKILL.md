---
name: push
description: Cut a release and publish the course site. Writes student-facing release notes for everything committed since the last release into 00-release-notes.qmd, bumps the version (patch by default) in the page and the footer chip, verifies the book renders cleanly, commits the release, tags it, then pushes main to GitHub (which triggers the GitHub Actions build and deploy to GitHub Pages, i.e. what students see). Use when the user says "push", "publish", "ship it", "cut a release", or "deploy". This is the ONLY sanctioned way to push; the standing rule is commit-don't-push, and invoking this skill is the user's explicit push authorization for this one run.
---

# push: cut a release, then publish the course site

Pushing `main` deploys the live course site students use, so a push always
ships as a *release*: versioned, with student-facing notes on the Release Notes
page and the footer version chip updated to match. Invocation of this skill
counts as the explicit "push now" authorization required by CLAUDE.md; it does
NOT carry over to later turns.

## Version plumbing (keep in sync, always)

The version lives in exactly two places, and they must match:

1. The newest `## vX.Y.Z (yyyy-mm-dd)` heading at the top of
   `00-release-notes.qmd` (the source of truth).
2. The footer chip in `_footer.html`:
   `<a href="00-release-notes.html" class="version-chip" ...>vX.Y.Z</a>`.

## Inputs

- Optional explicit target version in the user's request (e.g. "make this
  1.1.0"). If given, use it. Otherwise bump the **patch** digit of the current
  version. Bump **minor** on your own judgment when the release adds a whole
  new chapter, assignment, or section of the site; say so in the report.

## Procedure

1. **Preflight.**
   - `git status --short`. Only release files may be staged by this skill.
     Uncommitted changes that look like finished work the user just asked
     about: stop and ask whether to commit them first. Unrelated untracked
     files (PDFs, drafts, OneDrive artifacts) stay out.
   - Confirm you are on `main`.
   - `git fetch origin`, then `git log origin/main..HEAD --oneline`: know
     exactly what this push will publish. If there is nothing to push and no
     notes to write, say so and stop.

2. **Collect what shipped.** Find the last commit that touched
   `00-release-notes.qmd` and list everything after it:
   `git log --oneline $(git log -1 --format=%H -- 00-release-notes.qmd)..HEAD`.
   Cross-check against the newest entry on the page and skip anything its
   notes already describe.

3. **Write the release notes.** Add a new `## vX.Y.Z (yyyy-mm-dd)` section at
   the TOP of the entries in `00-release-notes.qmd` (below the intro prose,
   above the previous release):
   - One short lead sentence naming the headline change, then bullets.
   - Student-facing voice: write what a student sees ("Sprint 3 instructions
     expanded", "Guest speaker added to the Mar 5 schedule"), never commit
     subjects or repo internals. Plain factual copy, **no em dashes**.
   - Omit pure-internal work (tooling, CI, CLAUDE.md, refactors); a "Fixes and
     polish" bullet may collect small visible fixes. Do not oversell or invent.

4. **Bump the version chip.** Update the `vX.Y.Z` text inside the
   `.version-chip` link in `_footer.html` to the target version. Grep both
   files to confirm the two version strings match.

5. **Verify the render.** Run `quarto render` and confirm it completes with no
   errors; never push a broken build. Spot-check `_book/00-release-notes.html`
   (new entry present) and that the footer chip shows the new version. For
   pushes that touch navigation, the schedule, or `_quarto.yml`, also
   spot-check the relevant output in `_book/`.

6. **Commit.** Stage ONLY `00-release-notes.qmd` and `_footer.html`. Commit as
   `chore(release): v<version>` with a body listing the headline themes.
   - **GUARD: commit, tag, and push are SEPARATE steps, never chain them in
     one `;`-joined command.** A blocked or failed commit must stop the tag and
     push. Run the commit alone, confirm it created a new HEAD
     (`git log --oneline -1` shows `chore(release): v<version>`), and only then
     tag: `git tag v<version>`.

7. **Push.** `git push origin main --tags`. Confirm success (`git status`
   shows up to date with origin/main). Never force-push.

8. **Report.** Tell the user: the version shipped, the student-visible themes
   in the notes, how many commits were published, and that GitHub Actions is
   now building (the site updates in a few minutes). No em dashes.

## Failure handling

- If `quarto render` fails, fix or report; do not push a broken release.
- If the push is rejected (remote ahead), `git pull --rebase origin main`,
  re-run `quarto render`, and push again. Never force-push.
