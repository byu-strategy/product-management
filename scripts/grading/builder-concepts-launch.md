# Launch and Learn concepts (draft, generated from concepts/launch.json)

The named concepts under the Launch and Learn items. Getting the product to the people it is for, measuring what they do, deciding from it, and making the case for it.

Each concept is measured in up to two ways:

- **Know it** (every concept): the exams. Midterm and final questions on the concept come in three
  types (know it, use it, predict it). The September survey self-rating stands in until the midterm.
- **Practice** (every concept not marked knowledge only): the student's own work shows it, counted
  once. The **Practice** column says what counts as evidence: the `/sprint-review` session scan's
  "Builder tools you used" list, or a file in a shared repo. This is the breadth half of the profile's
  practice score; depth (`depth-levels.md`) is assigned per axis, not per concept.

A concept marked **knowledge only** has no practice check: it is measured by the exams alone.
Evidence rules are in `concept-coder.md` and `depth-levels.md`.

## L1 Shipping to real people

| Concept | Practice | Chapter |
|---|---|---|
| **LL01 Real users and launched versus used.** A launch puts the product where people can reach it; use is people who do not build it doing its main task on their own. A real user is shown by a dated record (a usage count, a feedback note, a payment), and repeat use on separate days matters more than a first try. | A committed, dated usage record (a metrics file, test note or usage count) that names people outside the team who used the product. | Ch 12: Your First Users, by Hand; Launch & Iterate. Ch 14: Outcomes, not output |
| **LL02 Launch in rings and deploy versus release.** Launch to widening groups: a private beta of people invited by hand, a public beta for the beachhead, then a wider launch. A merge deploys code; a release flag, checked on the server, decides who sees it, so each ring is reached by changing the flag with no new deploy. | A committed release flag (a table or config naming who has a feature) checked in server code, or a committed record of which group got the product first and which group next. | Ch 12: Launch in rings |

## L2 Metrics and instrumentation

| Concept | Practice | Chapter |
|---|---|---|
| **LL03 North Star metric.** The one number that best shows the value customers get, It measures an outcome (whether users are better off); how much the team built is output. Test: could it go up while the product got worse? If so, it counts activity. Input metrics are the drivers that move it. | One number named in a committed spec, README or metrics file as the measure of whether the product works, with why it shows value. | Ch 14: Outcomes, not output; The North Star and the metrics under it |
| **LL04 Success definition and guardrails.** Written before launch: the value metric, a threshold, guardrail metrics that must not get worse (such as AI cost per active user or error rate), and a judgment date. Without the threshold and date any result can be read as a success. | A committed success definition (the metric, a threshold, and a date) in an earlier commit than the launch or test it judges. | Ch 14: The North Star and the metrics under it; Write a success definition. Ch 12: Instrument it before you launch |
| **LL05 Vanity, leading and lagging metrics.** A vanity metric (total signups, page views, time in app) feels good and changes no decision; an actionable one can change what you do next week. Leading indicators move early and predict an outcome; lagging indicators (revenue, churn) report it after the fact. | knowledge only (exams) | Ch 14: Vanity, leading, and lagging |
| **LL06 Events and instrumenting the core action.** An event is one row: who, what, when, and details. Log the four to six events that trace the core task from start to finish, tied to the user, before launch, and check that real rows arrive. Signed-in users may insert only their own events and nobody reads them from the browser; signed-out visitors go through an analytics service or a server route. | An events table and logging calls, or analytics capture calls, committed for the product's core task. Analytics shown to users does not count. | Ch 14: Instrument the Core Action. Ch 12: Instrument it before you launch |
| **LL07 The funnel and activation.** Follow people from arrival to first value to coming back (AARRR: acquisition, activation, retention, revenue, referral). Each rate is a share of the step before it. Activation is the first moment a user gets the promised value; with high acquisition and low activation (a leaky bucket), fix activation, usually onboarding, before buying more traffic. | A funnel or activation rate computed from the product's events, committed as a query, a script, or a metrics file with the numbers. | Ch 14: Signups Are Not Adoption; The funnel; Onboarding is the activation step |
| **LL08 Cohort retention, churn and stickiness.** Group users by start week and track the share still active N periods later. Totals can rise from new signups while every cohort keeps less. Curve shape points to the cause: a steep first drop to the first experience, steady decline to the core value, flattening to a group that stays. Churn and DAU/MAU count distinct people, never events. | A cohort retention table computed from the product's data, committed. | Ch 14: Retention Shows Whether It Works; Cohorts; Why totals mislead; Engagement measures count people |

## L3 Experiments

| Concept | Practice | Chapter |
|---|---|---|
| **LL09 Cause versus coincidence.** A before-and-after change can come from the calendar, a campaign, or noise, and the data alone cannot tell them apart from the change you made. | knowledge only (exams) | Ch 14: Cause Versus Coincidence; Three ways a before-and-after comparison misleads you |
| **LL10 Randomized test (A/B test).** Assign users to A or B at random in the same weeks, so the change is the only systematic difference and a gap larger than chance is its effect. It proves an effect on the metric measured, for those users in that period; it says nothing about other metrics, later outcomes, or why. State the prediction before it starts. | A committed test plan with a prediction, in an earlier commit than the result, for a test that assigned users to versions at random, and the result recorded. | Ch 14: Why random assignment works |
| **LL11 Learning with small numbers.** With about 20 users, look only for big effects, hold out a random group in the same weeks, watch people use it, and say "can't tell yet" when the data cannot decide. Run a test to the size planned in advance; stopping when one version looks ahead finds differences that are chance. | A committed record of a holdout or small test with its planned size and the result, including a result of cannot tell yet. | Ch 14: What to do with 20 users |

## L4 Positioning, pricing and business model

| Concept | Practice | Chapter |
|---|---|---|
| **LL12 Positioning and the competitive alternative.** Why a specific person picks you over what they do today (usually a spreadsheet, a group text, or nothing), said in their words. Start from that competitive alternative, then unique attributes, value, who cares most, and the category. A positioning statement is the internal reference for all messaging, and every sentence of it should pass the "So what?" test. A model's opinion of copy is a guess from its training text; only real people's replies, clicks and signups show which message works. | A committed positioning statement or messaging file that names the customer and the alternative the product replaces. | Ch 12: Positioning & Messaging; The positioning statement; Messages that convert; What AI can and cannot do for your messaging |
| **LL13 Value-based pricing: ceiling, reference, floor.** Price between what the problem is worth to the customer (the ceiling, from what it costs them today, never from asking what they would pay) and your cost to serve (the floor), with what they pay for alternatives as the reference. The value estimate rests on assumptions about how the customer uses what is saved. | A committed price decision with the ceiling, reference and floor and the source of each. | Ch 12: Pricing and AI Margins |
| **LL14 AI cost to serve and gross margin.** Cost per user is cost per AI action times actions per month. Gross margin is price minus cost to serve, divided by price. On a flat price, a heavy user of an AI product can cost more than they pay, so check the distribution of usage as well as the average. | A committed estimate of the AI cost to serve one user, including the heaviest realistic user. | Ch 12: Every AI call is a cost |
| **LL15 Revenue models and free tiers.** The rule that turns use into money: subscription, usage-based, freemium, one-time, advertising, or commission. Each works only if something specific holds about the customer and costs. A flat price is simple and carries the heavy-user risk; usage pricing tracks cost; a free tier needs a usage cap. | A committed decision record that chooses a revenue model and names another model. | Ch 13: How Money Comes In: Revenue Models. Ch 12: Should you offer a free tier? |
| **LL16 Business Model Canvas.** A one-page model in ten blocks (customer segments, jobs-to-be-done, value proposition, channels, relationships, revenue, resources, activities, partners, costs). The blocks constrain each other, and every block is a hypothesis to mark as evidence or guess. A model can draft every block, and fills gaps with plausible guesses. | A committed Business Model Canvas for the product with all ten blocks filled in. | Ch 13: What a Business Model Is; Drafting Your Canvas with Claude |
| **LL17 Unit economics and break-even.** Look at one customer. Contribution margin is price minus variable cost (model calls, payment fees). Break-even is fixed costs divided by contribution margin. If each customer costs more than they bring in, more customers make it worse. | A committed break-even or financial model with the variable costs per user stated. | Ch 13: Unit Economics and Break-Even; Turn the canvas into a model and a slide |
| **LL18 Lifetime value and acquisition cost.** Margin-based LTV is contribution margin per month times the months a customer stays; using revenue overstates it, by a lot for an AI product. CAC is what you spend in money and time to win one paying customer. If CAC exceeds LTV, each new customer loses money; a common rule of thumb is LTV at least three times CAC. | A committed CAC per channel or LTV calculation from recorded spend and retention. | Ch 13: Unit Economics and Break-Even. Ch 14: Money Metrics |

## L5 Acting on usage

| Concept | Practice | Chapter |
|---|---|---|
| **LL19 Keep, change, or kill.** Every feature carries upkeep. Retire one that few use, that costs upkeep, and that does not serve the core task, after logging it long enough to judge; tell the people who rely on it and give them a path. The same reasoning applies to stopping a product. | A committed analysis of how people outside the team used a feature or the product (counts, events, or notes from watching them), ending in a decision to keep, change or remove something, with the reason. | Ch 14: Keep, Change, or Kill |
| **LL20 When to change the go-to-market plan.** Change the plan when people sign up but do not reach value, a channel given a fair test brings almost no one, customers describe the product in other words, or a customer costs more to acquire than they bring in. Then interview again, rewrite messaging in their words, narrow the customer, or try the next channel. | A committed decision record that changes the customer, message or channel and cites the evidence for the change. | Ch 12: When to change your GTM |
| **LL21 Reading what people say: NPS, comments and AI themes.** Combine the numbers with what interviews, sessions and comments show (data-informed), unless the data came from a clean test with enough people. At student scale one NPS answer moves the score five points or more, so read the comments. A model can group feedback into themes with the quotes behind each; it cannot tell you why a number moved. | A committed synthesis of user feedback (comments, survey or NPS responses) with counts and quotes. | Ch 14: What to do with 20 users; Asking How People Feel. Ch 12: Using AI on launch data |

## L6 Telling the product's story

| Concept | Practice | Chapter |
|---|---|---|
| **LL22 Decide what the story is for.** Aim (what to communicate, and to whom), approach (which story serves it), act (tell it and watch how the audience responds). A story shows a change, a before and an after; without one it is a report. Setting, method, audience and purpose are chosen on purpose. | knowledge only (exams) | Ch 15: Decide what the story is for |
| **LL23 Story database.** A running list of at least 20 personal stories, each with its five-second moment, kept ready for interviews, demos and pitches. | A committed story database file with the student's own stories. | Ch 15: Build a story database |
| **LL24 What makes a story persuasive and memorable.** Facts persuade deliberate reasoning (the rider); stakes, specifics and feeling move emotion and intuition (the elephant). SUCCESs names six traits of ideas people remember: simple, unexpected, concrete, credible, emotional, stories. Duarte's structure moves between what is and what could be and ends on a call to action. | knowledge only (exams) | Ch 15: Techniques that make a story persuasive and memorable; Make It Stick; Storytelling in day-to-day product work |
| **LL25 The demo as an argument.** One claim (this product does a real job for a real person), supported in order by the person and the problem, the moment it works on the deployed product, the evidence, and what was learned. Small real numbers are strong evidence; projected or inflated ones are not. Rehearse out loud, timed, on camera. | A Loom moment that shows one task done in the product people use, from the user's first action to the result. | Ch 15: The Final Demo; Rehearse |
| **LL26 Innovation capital and impression amplifiers.** Support comes from human capital (skills, passion), social capital (who vouches for you) and reputation capital (what you have done). Materialize, compare, story and commit amplify a true claim; used to make something false look true, they become deception. | knowledge only (exams) | Ch 15: Winning Support: Your Innovation Capital; Amplify: Make Them Believe |

## L7 Reaching users

| Concept | Practice | Chapter |
|---|---|---|
| **LL27 Beachhead and ideal customer profile.** The ideal customer profile names who gets the most value and is easiest to reach: their situation, current habit, where they gather, and what they pay for today. The beachhead is the narrowest group with the pain that you can reach by hand and win completely before widening. | An ideal customer profile or beachhead named in a committed GTM file or README, with where those people gather. | Ch 12: Who It Is For: The Beachhead |
| **LL28 First users by hand.** Recruit the first users one at a time, by name, to learn what makes people say yes (a sprint target: 20 named people contacted, 5 using it). Predict replies and tries before sending, then compare. The six principles of persuasion (social proof, authority, scarcity, reciprocity, commitment and consistency, liking) amplify a true offer; pushing a product that does not deliver turns them into manipulation. | A committed outreach log: who was contacted, through what channel, and what happened. | Ch 12: Your First Users, by Hand; Where the first twenty come from; The pitch conversation; Six principles of persuasion |
| **LL29 Channel strategy.** A channel is a repeatable path by which strangers become users. Pick one or two where the customer already is and give each a fair test, comparing channels by the share of signups that activate and pay and by cost per customer. Buyers now also ask models, which cite community and reference sites, so being useful in public where buyers gather reaches both. | A committed record of a channel test (a listing, posts, ads or flyers) with who was reached and the result. | Ch 12: Choosing Your Channel Strategy; A second audience: the models |
| **LL30 Product-led versus sales-led growth.** Product-led growth lets people sign up and reach value alone; sales-led growth needs a person to reach out, demo and set up, which fits a complex product, a long setup, or a large deal. | A committed decision record or GTM file that chooses product-led or sales-led growth for the product and gives the reason. | Ch 12: Choosing Your Channel Strategy |

## Book gaps

- Real users: the book never defines a real user (someone who does not build it, using it for its purpose) or asks for a dated usage record. A short section in Ch 12 Launch & Iterate, or Ch 14 Instrument the Core Action, should say what counts and how to keep a weekly users table.
- Stopping a test early and planned sample size (the retired LL-F-11): Ch 14 What to do with 20 users teaches big effects and holdouts but not deciding the test size in advance or why peeking finds chance differences. One paragraph in Ch 14 Why random assignment works.
- Writing the prediction before a test: Ch 12 asks for a prediction before outreach and Ch 14 before a cohort curve, but no section says a test plan is committed before the test starts. Ch 14 Cause Versus Coincidence should add a test-plan template (question, prediction, metric, size, date).
- Stopping a product or idea from evidence: Keep, Change, or Kill covers features. Students shelved whole ideas after channel tests; Ch 14 Keep, Change, or Kill should add a paragraph on stopping the product.
- Distribution through listings and app stores (an App Store listing, a directory, a marketplace): Ch 12 Choosing Your Channel Strategy names communities and Product Hunt only.
- Choosing a launch market or pilot location: no section; Ch 12 Who It Is For could treat it as a beachhead choice.
- Several concepts have no exam question: success definition and guardrails, revenue models and free tiers, the Business Model Canvas, reading feedback (NPS, AI themes), all of Ch 15 except the demo. The bank also has no Launch midterm items, which matches the course order.

## Evidence a packet or the session scan cannot see yet

- Real users (L1, and depth level 4 on every axis): the packet used to have usage only as sentences in plans and reviews. The review's "Users this sprint" list is now the record depth level 4 accepts; a read-only count from the product's database (distinct users by day) would make it checkable.
- Instrumentation (L2): the packet shows an events migration or capture calls but not whether real rows arrived, or whether the analytics are shown to users. A count of event rows by name and date in the packet would show it.
- Experiments (L3): the prediction must be committed before the test. Commit order in the packet shows this only when the plan and the result are in separate commits; it should flag a test file first committed with its result.
- Outreach and channels (L7): outreach often lives in email, Slack, ads managers or private repos. The packet sees it only when a log is committed; ad spend and clicks need a screenshot or export in the repo.
- Pricing tested with real people (L4): a Stripe link or checkout in code does not show anyone paid. A payment count (excluding the founder's own test purchase) would need a recorded export.
- Demo (L6): the coder judges from Loom frames and the transcript. The packet does not tell a live app from localhost or a prototype, nor a fresh run from a result made earlier; Loom timestamps are estimates. A link check on the URL shown would help.
- Practice for most Launch concepts is not visible in the session scan: launch work happens in browsers, email and analytics tools. Only SQL or analytics queries and outreach drafting in sessions show up.
