# Outline refactor map: six-axis spine

Status: proposal for redline, Sep 2026. Not student-facing. Underscore prefix keeps
Quarto from rendering it. Nothing here is on the live site.

## The change

The book moves from lifecycle parts (Foundations, Aim, Discover, Build, Grow) to the six
Builder axes, two weeks each, 14 chapters across 13 class sessions, week 8 carrying two. Every existing chapter
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
- `02-spec-driven-development` lines 179-688: SDD Workflow, Major SDD Approaches, Why SDD
  Matters for PMs, Getting Started, PRD Building Blocks, CLAUDE.md config, Tips and Gotchas,
  When to Use SDD vs Vibe Coding  (the full-stack primer at lines 37-178 goes to Ch 7 instead)

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

**Ch 7. Anatomy of an Application** (week 7)
- `02-spec-driven-development` lines 37-178: Frontend (The User Interface), Backend (The
  Business Logic), Database (The Memory), API (The Messenger), How They Work Together:
  The Full Stack, Why This Matters, Don't Panic
- **NEW WRITING**: tech stacks and languages. Scott has an image for this.
- `04-validating-opportunities` P2: Supabase Introduction, Authentication with Supabase

This is the conceptual foundation for the axis and it has been sitting orphaned inside the
spec-driven-development file. Note the deliberate lateness: under "ship first with the agent,
then learn what you shipped," students do not need to know what a backend is in week 1
because Claude Code handles it. Week 7 is where they learn what they have been shipping.

**Ch 8. Data and APIs** (week 8)
- `05-building-your-mvp` P2: Supabase Database Fundamentals, RLS, CRUD, Relations and Queries
- `06-testing-with-users` P2: Supabase Storage, APIs

**Ch 9. Version Control, Testing, and Tech Debt** (week 8, paired with Ch 8)
- `03-problem-discovery` P2: Git Fundamentals (deep), Branches
- `11-sustainable-code` P1: Technical Debt, Strategic vs Accidental, Tech Debt Quadrant, When to Pay Down
- `11-sustainable-code` P2: Code Quality, Linting and Formatting, Testing Fundamentals, Refactoring Patterns, Supabase Realtime

### Part 5. AI Systems

**Ch 10. How Models Work** (week 9)
- `02-llms-prompt-engineering`: AI and Machine Learning, Prompting  (published at last, file retired into this)

Carries LO1, which currently nothing assesses.

**Ch 11. Models in Your Product** (week 10)
- **NEW WRITING**: calling model APIs, structured output, cost and latency, failure modes
- **NEW WRITING**: evals

### Part 6. Launch and Learn

**Ch 12. Going to Market** (week 11)
- `09-go-to-market`: entire chapter, restructured into the standard shape
- `10-business-models`: entire chapter, restructured into the standard shape
- `11-sustainable-code` P1: Growth and Retention Strategy, Onboarding Optimization  (currently misfiled in the tech debt chapter)
- **NEW WRITING**: build half, landing pages and SEO (the schedule already promises this)
- **NEW WRITING**: basic instrumentation. A landing page needs analytics on it the day it
  ships, so event tracking setup moves here from Ch 13. Ch 13 then teaches what the numbers
  mean rather than how to collect them.

**Ch 13. Measuring What Matters** (week 12)
- `08-measuring-what-matters`: entire chapter, P1 and P2 (less the setup mechanics moved to Ch 12)

**Ch 14. Storytelling and the Final Demo** (week 13)
- `12-final-presentations`: entire chapter

## Files retired

| File | Fate |
|---|---|
| `00-setup.qmd` | delete, stale STRAT 490R content |
| `01-vibe-coding.qmd` | folded into Ch 1 |
| `02-spec-driven-development.qmd` | splits: primer to Ch 7, SDD workflow to Ch 2 |
| `02-llms-prompt-engineering.qmd` | becomes Ch 9 |

## New writing required

| Where | What | Size |
|---|---|---|
| Ch 5 | Visual design fundamentals | largest gap |
| Ch 7 | Tech stacks and languages (Scott has an image) | short |
| Ch 11 | Models in your product, evals | ~half a chapter |
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
2a. Application Architecture now needs three chapters (7, 8, 9) in its two weeks, because
   the full-stack primer earned its own. Week 8 carries two short chapters, which the
   current schedule already does elsewhere. Alternative is giving the axis three weeks and
   taking one from Discovery.
3. Launch before measure, settled. The axis is Launch and Learn, in that order, and a
   student whose final product is due in week 13 needs acquisition runway more than
   perfect instrumentation order. Basic event tracking rides along with the landing page
   in Ch 11 so nothing ships un-instrumented.
4. Does Platform Strategy belong in Design (the surface) or Application Architecture
   (how it ships)? Filed under Design here.
5. Chapter file naming. Proposal: `01-` through `13-` matching reading order, retiring
   the current numbering where `07` renders before `06`.
