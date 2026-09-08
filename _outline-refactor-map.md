# Outline refactor map: six-axis spine

Status: proposal for redline, Sep 2026. Not student-facing. Underscore prefix keeps
Quarto from rendering it. Nothing here is on the live site.

## The change

The book moves from lifecycle parts (Foundations, Aim, Discover, Build, Grow) to the six
Builder axes, two weeks each, 13 chapters for 13 class sessions. Every existing chapter
splits at its Part 1 / Part 2 seam and the halves refile by axis.

Teaching an axis and using an axis are different. Each axis gets two weeks of instruction;
students keep using all six every week in their sprints. The integration point moves from
the chapter's two halves to the student's own product.

## Axis order

| Weeks | Axis | Rationale |
|---|---|---|
| 1-2 | Agentic Workflow | Claude Code on day one; Sprint 1 is ship-anything |
| 3-4 | Discovery | Now decide what is worth building |
| 5-6 | Design | The surface, once they know what it is for |
| 7-8 | Application Architecture | The guts, after shipping something naive |
| 9-10 | AI Systems | Needs an app to put a model inside |
| 11-12 | Launch and Learn | Get it out, measure it |
| 13 | (wrap) | Final demos |

Ship first with the agent, then learn what you shipped. This dissolves the current bug
where Sprint 1 needs deployment in week 3 but deployment is taught in week 4.

## Chapter map

### Part 1. Agentic Workflow

**Ch 1. Building with AI Agents** (week 1)
- `01-pm-ai-era` P1: History of Product Management, AI Product Management
- `01-pm-ai-era` The Loop (AIRE)
- `01-pm-ai-era` P2: Command Line, VS Code, Claude Code, Code your first app, Code your second app, AI Dev Tools Landscape
- `02-problems-worth-solving` P2: Terminal Practice, Conversational Coding
- `01-vibe-coding`: History, Terminology, Looking ahead  (folded in, file retired)
- NEW: the six axes introduced; hexagon baseline survey

**Ch 2. Directing the Agent** (week 2)
- `02-problems-worth-solving` P2: Claude Code Markdown Files, Deploying a Prototype
- `03-problem-discovery` P2: Slash Commands; git basics (clone/add/commit/push only)
- `03-problem-discovery` P2: Deployment with Vercel / GitHub Pages
- `04-validating-opportunities` P2: Claude Code Agents
- `06-testing-with-users` P2: Claude Code Skills
- `07-platform-strategy` P2: Claude Code Hooks
- `05-building-your-mvp` P1: User Stories, Product Requirements Documents
- `02-spec-driven-development`: SDD Workflow, Major SDD Approaches, CLAUDE.md config, File Structure, Workflow Rules, Why SDD Matters for PMs  (folded in, file retired)

Note: git splits. Basics here because Sprint 1 needs a repo in week 3. Branches and
workflow move to Ch 8.

### Part 2. Discovery

**Ch 3. What Is Worth Building** (week 3)
- `product-strategy`: entire chapter
- `product-morality`: entire chapter
- `02-problems-worth-solving` P1: Why Most Products Fail, Problem vs Solution Thinking

Carries LO3. The Discovery axis definition extends to "what to build, for whom, and
whether you should."

**Ch 4. Finding and Validating the Problem** (week 4)
- `02-problems-worth-solving` P1: Five Discovery Skills, You Are Your Best First Customer, Problem Journaling, Diverge Before You Converge, Evaluating Your Problems, Importance-Satisfaction Framework, From Problems to Opportunities
- `03-problem-discovery` P1: entire (Truth-Seeking, JTBD, Five Kinds of Pain, Mom Test, Conducting Interviews, Interview Synthesis, Personas, Discovery Is Continuous)
- `04-validating-opportunities` P1: entire (Opportunity Evaluation, Scoring, Access Test, Commitment Decision, Avoiding Premature Commitment, Value Proposition)
- `05-building-your-mvp` P1: What is an MVP, Minimum Viable or Minimum Awesome, MVP Scoping, The Cheapest MVP Is a Test, Feature Prioritization

Largest chapter in the book. Split into 4a/4b if it runs long.

### Part 3. Design

**Ch 5. Interface and Flow** (week 5)
- `04-validating-opportunities` P2: Frontend Fundamentals, React Basics, Client-Side State and Forms
- `07-platform-strategy` P1: entire (Platform Decision Framework, Web vs Mobile, Platform Spectrum, PWAs, Capacitor, When to Go Fully Native, Making the Decision)
- `07-platform-strategy` P2: Mobile-Responsive, PWA Setup, Capacitor Setup
- **NEW WRITING**: visual fundamentals, layout, type, component patterns, what "client ready" means

**Ch 6. Testing the Design** (week 6)
- `06-testing-with-users` P1: entire (Curse of Knowledge, Design Canon, Usability Testing, Running a Test, What to Observe, Synthesizing Feedback, Iteration Frameworks, Testing at Scale)

Thinnest axis. Ch 5 needs the most new writing of any chapter.

### Part 4. Application Architecture

**Ch 7. Data and Auth** (week 7)
- `04-validating-opportunities` P2: Supabase Introduction, Authentication with Supabase
- `05-building-your-mvp` P2: Supabase Database Fundamentals, RLS, CRUD, Relations and Queries
- `06-testing-with-users` P2: Supabase Storage, APIs

**Ch 8. Keeping It Healthy** (week 8)
- `03-problem-discovery` P2: Git Fundamentals (deep), Branches
- `11-sustainable-code` P1: Technical Debt, Strategic vs Accidental, Tech Debt Quadrant, When to Pay Down
- `11-sustainable-code` P2: Code Quality, Linting and Formatting, Testing Fundamentals, Refactoring Patterns, Supabase Realtime

### Part 5. AI Systems

**Ch 9. How Models Work** (week 9)
- `02-llms-prompt-engineering`: AI and Machine Learning, Prompting  (published at last, file retired into this)

Carries LO1, which currently nothing assesses.

**Ch 10. Models in Your Product** (week 10)
- **NEW WRITING**: calling model APIs, structured output, cost and latency, failure modes
- **NEW WRITING**: evals

### Part 6. Launch and Learn

**Ch 11. Measuring What Matters** (week 11)
- `08-measuring-what-matters`: entire chapter, P1 and P2
- `11-sustainable-code` P1: Growth and Retention Strategy, Onboarding Optimization  (currently misfiled in the tech debt chapter)

**Ch 12. Going to Market** (week 12)
- `09-go-to-market`: entire chapter, restructured into the standard shape
- `10-business-models`: entire chapter, restructured into the standard shape
- **NEW WRITING**: build half, landing pages and SEO (the schedule already promises this)

**Ch 13. Storytelling and the Final Demo** (week 13)
- `12-final-presentations`: entire chapter

## Files retired

| File | Fate |
|---|---|
| `00-setup.qmd` | delete, stale STRAT 490R content |
| `01-vibe-coding.qmd` | folded into Ch 1 |
| `02-spec-driven-development.qmd` | folded into Ch 2 |
| `02-llms-prompt-engineering.qmd` | becomes Ch 9 |

## New writing required

| Where | What | Size |
|---|---|---|
| Ch 5 | Visual design fundamentals | largest gap |
| Ch 10 | Models in your product, evals | ~half a chapter |
| Ch 12 | GTM build half, landing pages and SEO | ~half a chapter |
| Ch 1 | Six axes introduction | short |
| Ch 3, 4, 12 | Key Concepts sections where missing | short |

Four of six axes are assembly jobs from existing material. Design and AI Systems are
the two that need real authoring.

## Open questions

1. Axis order. Agentic Workflow first vs Discovery first. Recommended: Agentic first,
   because Sprint 1 is Ship and Showcase and "you can ship before you understand" is the
   thesis of the course.
2. Ch 4 is oversized. Split or compress.
3. Does Platform Strategy belong in Design (the surface) or Application Architecture
   (how it ships)? Filed under Design here.
4. Chapter file naming. Proposal: `01-` through `13-` matching reading order, retiring
   the current numbering where `07` renders before `06`.
