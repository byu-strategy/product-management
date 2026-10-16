# Design concepts (draft, generated from concepts/design.json)

The named concepts under the Design items. Deciding what the user sees and does, writing it down clearly enough to build, and watching real people use it.

Each concept is measured in up to two ways:

- **Know it** (every concept): the exams. Midterm and final questions on the concept come in three
  types (know it, use it, predict it). The September survey self-rating stands in until the midterm.
- **Practice** (every concept not marked knowledge only): the student's own work shows it, counted
  once. The **Practice** column says what counts as evidence: the `/sprint-review` session scan's
  "Builder tools you used" list, or a file in a shared repo. This is the breadth half of the profile's
  practice score; depth (`depth-levels.md`) is assigned per axis, not per concept.

A concept marked **knowledge only** has no practice check: it is measured by the exams alone.
Evidence rules are in `concept-coder.md` and `depth-levels.md`.

## G1 User flows and states

| Concept | Practice | Chapter |
|---|---|---|
| **DE01 Flows before screens.** A flow is the steps a user takes to finish one task: a goal, an entry point, steps, decisions, and exits. Map it and count the steps before designing or prompting for screens. | A flow written as steps or a list of states in a committed spec or design file. | Ch 5: Flows Before Screens |
| **DE02 States off the happy path.** The happy path is the run where everything goes right. Empty, loading, error and partial states each say what is true now and what the user can do next; a button that changes data shows a loading state and disables itself until the request finishes. | Committed code that shows an empty, loading or error state for a flow, or a Loom moment that shows one. | Ch 5: Off the Happy Path |
| **DE03 UI, UX and product design (the UX iceberg).** UI is the screens; UX is the whole experience of getting a task done, including what happens off the screen; product design also decides what the product is. Visual polish sits on top of interaction design, information architecture and the conceptual layer, where usable and unusable products differ. | knowledge only (exams) | Ch 5b: UI, UX, and Product Design; Ch 5: Why This Matters |
| **DE04 Information architecture.** How content is organized, labeled, navigated and searched, in the user's terms. Navigation patterns (tab bar, sidebar, top navigation, hub and spoke, breadcrumbs) fit different products. A card sort shows how people group things; a tree test checks whether they can find things in a proposed structure. | A committed navigation map or site structure, or card sort or tree test results. | Ch 5b: Information Architecture; Two methods: card sorting and tree testing |
| **DE05 Designing for an uncertain AI.** When a model's output can be wrong, the screen sets expectations, shows the evidence behind the answer, presents output as an editable draft, makes dismiss and undo one step, and asks a person to confirm costly actions. | Committed code in an AI feature that shows at least one of: what to expect about accuracy, the evidence behind an answer, output as an editable draft, undo, or a confirmation before acting. | Ch 5: Designing for an Uncertain AI |

## G2 Visual fundamentals

| Concept | Practice | Chapter |
|---|---|---|
| **DE06 Visual hierarchy and one primary action.** Size, weight, contrast, spacing and position rank what is on the screen. Each screen gets one primary action and the rest are de-emphasized. The squint test: blur the screen; what still stands out should be the primary action. | A committed design rule about hierarchy or the primary action (for example one primary action per screen), and screens in the Loom that follow it. | Ch 5: Attention and Hierarchy |
| **DE07 Gestalt grouping.** People see items as a group when they are close together, look alike, or share a boundary. Space inside a group should be smaller than the space between groups, or a label reads as belonging to the wrong field. | knowledge only (exams) | Ch 5b: How People Perceive a Screen; Gestalt grouping |
| **DE08 Fitts's law, Hick's law and cognitive load.** Fitts: a target is faster to hit when it is larger and closer. Hick: more options take longer to choose among, for a choice among unfamiliar options. Cognitive load: show what the user needs at the step where they need it, so they recognize it instead of recalling it. | knowledge only (exams) | Ch 5b: Fitts's law; Hick's law; Cognitive load and Jakob's law; Ch 5: Attention and Hierarchy |
| **DE09 Norman's principles and the conceptual model.** An affordance is an action a thing makes possible; a signifier is the visible cue that it is there. Mapping, constraints and feedback close the gulfs of execution and evaluation. The user's model of how the product works is built only from the system image, so a change that alters what users think the product is for needs testing first. | knowledge only (exams) | Ch 5b: Norman's Principles of Interaction; Ch 6: The Design Canon Behind This |
| **DE10 Typography, layout grid and color.** A short type scale, a spacing scale and a grid, and color used by meaning with one accent. Limiting the choices up front means each one is made once. | Committed rules or tokens for a type scale, a spacing scale or color use, which the product's code uses. | Ch 5b: Visual Design Fundamentals; Typography; Layout and grid; Color |
| **DE11 Words are interface.** Labels, buttons and messages are instructions. Buttons are verb plus object, errors say what happened and how to fix it, names use the user's words, and confirmations say what changed. | A committed copy rule in a spec or design rules file, or a commit whose message says it rewrites labels, buttons or error messages in the user's terms. | Ch 5: Words Are Interface |
| **DE12 Accessibility baseline (WCAG).** Text contrast at least 4.5:1 (3:1 for large text), every action works by keyboard with visible focus, touch targets large enough, a label on every input, and real HTML elements so screen readers can read them. | A committed accessibility rule or check result (contrast numbers, a keyboard pass note), with fixes that follow it. | Ch 5: Accessible by Default |
| **DE13 Web, mobile, or both; mobile-first layout.** Most student products start as a responsive web app; a PWA, Capacitor, or native app is chosen for use away from a desk, device hardware, or store distribution. Mobile-first means the phone layout is the default and wider screens add columns at set breakpoints, with touch targets sized for a thumb. | A committed spec section or decision record about phone and desktop use (a mobile layout, a PWA, or a native app), or a commit whose message says it makes a screen work at phone width. | Ch 5: Web, Mobile, or Both; Making Your App Mobile-Responsive |

## G3 Design system

| Concept | Practice | Chapter |
|---|---|---|
| **DE14 Design system: tokens, components, patterns.** A design system makes each decision once. Tokens hold the raw choices (colors, type sizes, spacing, radius); components are built from tokens with defined variants and states; patterns combine components to solve a recurring problem. A component library the agent already knows (shadcn/ui) keeps sessions consistent. | Shared components or design tokens, committed, used on more than one screen or page section. | Ch 5: Decide Once: Design Systems and Familiar Patterns; Ch 5b: From decisions to tokens |
| **DE15 Design rules written for the agent.** An agent has no memory between sessions and will restyle each new screen. A short design rules section in CLAUDE.md or the spec (which components, one primary button, spacing scale, empty states, icon set) turns one-time decisions into standing instructions. | A design rules section the student wrote in CLAUDE.md, AGENTS.md or a spec, committed. | Ch 5: Decide Once: Design Systems and Familiar Patterns (Why this matters more with an agent) |
| **DE16 Jakob's law and familiar patterns.** Users spend most of their time in other products and expect yours to work the same way. Each invented convention is something users must learn; platform guidelines record the conventions. | knowledge only (exams) | Ch 5: Decide Once: Design Systems and Familiar Patterns; Ch 5b: Cognitive load and Jakob's law |

## G4 Specs

| Concept | Practice | Chapter |
|---|---|---|
| **DE17 User stories.** As a [type of user], I want [goal] so that [benefit]. A story names a user and an outcome; "build login" or "make it faster" does not. | User stories in the form As a [user], I want [goal] so that [benefit], in a committed spec outside the sprint plan. | Ch 6b: User Stories |
| **DE18 Acceptance criteria.** The conditions that must be true for a story to be done, and the check held against the agent's work. Each criterion states one observable result, names the user and screen, and names the check that confirms it (walk, unit, or structure); a criterion about who can see something gets its opposite as a separate criterion. EARS phrases a requirement as WHEN ... THE SYSTEM SHALL. | A committed spec, outside the sprint plan, with numbered or checkable acceptance criteria for a feature. | Ch 6b: Acceptance Criteria; Kiro's three files and EARS; The Agent Team Kit's spec and build-spec Skills |
| **DE19 Product requirements document (PRD).** A document that says what is being built, why, for whom, and how success is measured: overview, objectives, stories with criteria, functional and non-functional requirements, success metrics, and out of scope. | A committed PRD or spec that includes success metrics and an out-of-scope list. | Ch 6b: Product Requirements Documents (PRDs) |
| **DE20 Spec-driven development.** Write the spec before code you intend to keep: requirements, design, then tasks, built one checkable task at a time. Explore with throwaway code to learn, then spec what you keep. Kiro's three files, GitHub Spec Kit (with a constitution of non-negotiable principles), and a plan saved to files package the same workflow. | Spec files committed in an earlier commit than the code they describe. | Ch 6b: Build first, then spec what you keep; Why SDD Matters; When to Use SDD vs. Pure Vibe Coding; The SDD Workflow; Major SDD Approaches |
| **DE21 Decisions already made, considered and rejected.** A spec records what was settled while exploring (wording, empty and error states, names) and each option turned down with the reason, so the next session does not reopen the question or propose the rejected option again. | A committed spec with a decisions-made section and a considered-and-rejected section. | Ch 6b: The Agent Team Kit's spec and build-spec Skills |
| **DE22 Punch list and check sheet.** The spec's build steps as an ordered checklist, each naming the files it touches and the criteria it closes, so a fresh session can resume. Browser-checked criteria go into a check sheet of Go, Do, Expect lines worked by hand. | A committed punch list with items checked off, or a check sheet with results. | Ch 6b: The Agent Team Kit's spec and build-spec Skills |

## G5 Critique and direction

| Concept | Practice | Chapter |
|---|---|---|
| **DE23 Precise design direction.** A design instruction says where, what is wrong, why (the principle), what to change, and a reference such as a screenshot or a named component. For a redesign, ask first for a list of what the new design removes (a subtraction audit). Taste is naming specific problems against stated principles. | A written design direction in a spec, issue or change note that names the element, the problem and the change, and a later commit that makes the change. | Ch 5: Directing an Agent on Design; Taste is a skill |
| **DE24 Double Diamond: diverge, then converge, twice.** Design widens and narrows twice: explore the problem, define it, then generate several solutions before choosing one. Builders using an agent most often skip the second widening and build the first solution. | A committed comparison of two or more design options with the reason for the one chosen. | Ch 5b: The Design Process: Diverge, Then Converge, Twice |
| **DE25 Nielsen's ten usability heuristics.** Ten rules of thumb (visibility of system status, match with the real world, user control, consistency, error prevention, recognition over recall, and others) for reviewing a screen. A heuristic review, by a person or an agent, finds likely problems; it does not replace watching users. | A committed heuristic review of the product that names the heuristics, the problems found, and the fixes. | Ch 5b: Nielsen's Ten Usability Heuristics; Running a quick heuristic review with an agent |

## G6 Usability testing

| Concept | Practice | Chapter |
|---|---|---|
| **DE26 Curse of knowledge: watch, do not ask.** The builder cannot see the product as a newcomer does. Watching what people do shows problems that asking their opinion hides; a task completed is not the same as a task understood. | knowledge only (exams) | Ch 6: The Curse of Knowledge; What to Observe |
| **DE27 Running a usability test.** About five people from the target group per round, three to five tasks written as goals (never as click instructions), a think-aloud script, and a moderator who stays quiet and does not help. Watching a few people comes before counting many with analytics or A/B tests. | A committed note for each session in which a person outside the team used the product, with the tasks and what the person did. | Ch 6: What is Usability Testing?; Running a Usability Test; Testing at Scale |
| **DE28 Affinity mapping and severity scoring.** Group observations into themes, then rank problems as critical, major, minor or cosmetic. Fix what blocks the core task first. | A committed synthesis of usability test notes with the problems grouped and ranked by severity. | Ch 6: Synthesizing Feedback; The Affinity Mapping Process; Severity Scoring |
| **DE29 Fix the top issue and retest.** Fix the one or two most severe problems, run the same tasks with new people, and check the problem is gone and nothing new broke. Keep what works; weigh feedback by frequency, severity and source instead of acting on single opinions. Repeated failure to show value across rounds is a reason to consider a pivot. | A commit that changes the product and cites a usability test finding. | Ch 6: Fix the top issue and retest; Iteration Frameworks; Responding to Feedback Without Overreacting |
| **DE30 Fidelity: the cheapest artifact for the question.** Sketch, wireframe, mockup and prototype differ in how finished they look and how much they do; fidelity and effort are separate. Name the question first, then make the cheapest artifact that answers it. Polish invites comments on polish. | A committed sketch, wireframe, mockup or prototype, in an earlier commit than the feature it shows. | Ch 5b: Fidelity: Sketch, Wireframe, Mockup, Prototype; Design Tools: Paper, Figma, Claude, and Code |

## Book gaps

- Writing a flow down (G1 level 4): Ch 5 teaches mapping a flow but gives no file convention. Add a short 'Write the flow in the spec' block to Ch 5: Flows Before Screens, and a Flow and states section to the spec template in Ch 6b.
- Session notes (G6 level 4): Ch 6 says to take notes but gives no note format or where to commit it. Add a one-page session note template to Ch 6: Running a Usability Test.
- Changing a spec after shipping (G4 level 5): Ch 6b does not teach recording what changed in a spec and why. Add a 'When the spec changes' subsection after The Agent Team Kit's spec and build-spec Skills.
- Choosing a design system on purpose (G3 level 5): Ch 5 recommends shadcn/ui but does not show a decision record comparing options. Add an example to Decide Once.
- Recruiting test participants and consent: one line in Ch 6 (Before the Session). Thin for a step most students find hardest.
- Dark patterns and design ethics (deceptive defaults, confirm-shaming, hidden cancellation): not taught. A short section would fit after Words Are Interface in Ch 5.
- Onboarding and first-run design beyond the empty state: thin. Could extend Ch 5: Off the Happy Path.

## Evidence a packet or the session scan cannot see yet

- States (DE02): a packet sees code and nine Loom frames, which usually show the happy path. An empty, loading or error state is confirmed only if the spec lists the states or the Loom shows one. Asking for a Flow and states list in the spec would make it visible.
- Flow written down (DE01): several Sprint 2 flows exist only in code (a Steps component, a route list). The coder cannot tell a route list from a flow. A named spec section would settle it.
- Design rules (DE10, DE12, DE15): rules sometimes live only in commit messages or code comments, and contrast and keyboard checks leave no record unless output is saved. A committed check result (contrast numbers, a keyboard-pass note) would make them checkable.
- Design system reuse (DE14): counting the screens that use a shared component needs a code search the packet does not include. Adding import counts per shared component to the packet would make 'three or more screens' checkable.
- Spec text (DE18 to DE22): packets often drop spec texts under the text budget, so acceptance criteria and decisions sections cannot be read. Commit order still settles 'before the code'. Giving spec files priority in the packet would fix it.
- Design direction (DE23): directions to an agent are in the user's prompts, which the session scan reads but does not classify. Directions to a teammate or another tool (Cursor) are not visible. A scan count of prompts with a screenshot attached, or naming an element and a principle, would help.
- Usability testing (DE27 to DE29): one record may be evidence for concepts under both G5 and G6; it counts for each concept only when it meets that concept's practice sentence on its own. Session note texts are often absent from the packet.
