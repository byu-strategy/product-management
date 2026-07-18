# CLAUDE.md — Company Brain

This file is loaded by Claude Code at the start of every session. Keep it current:
it should let a brand-new session act like a chief of staff who already knows the company.
Update it whenever strategy, customers, or conventions change.

## The company

- **What we do:** [one sentence]
- **Who we serve:** [specific customer segment — see discovery/personas.md]
- **Why they pay / will pay:** [the problem, in the customer's words]
- **Business model:** [pricing, current thinking — link the decision record]

## Current state

- **Sprint goal right now:** [update each sprint]
- **Live URL:** [deploy]
- **Biggest open risk:** [the thing most likely to kill the company]

## How this repo works

- The repo is the whole company. Non-code work (interviews, pipeline, experiments)
  is committed as files just like code.
- Specs go in `specs/` and are written before building. When asked to build a feature,
  check for its spec first; if none exists, draft one and confirm it before writing code.
- Meaningful choices get a numbered record in `decisions/`. When we make one in a
  session, write the record.
- Weekly numbers live in `metrics/weekly.md`.
- Never put real customer names, emails, or phone numbers anywhere in this repo.

## Product conventions

- **Stack:** [fill in]
- **Deploy:** [how a push becomes live]
- **Style/testing conventions:** [fill in as they emerge]

## Voice

- Customer-facing copy sounds like: [2–3 adjectives + an example line]
