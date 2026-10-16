# Application Architecture concepts (draft, generated from concepts/architecture.json)

The named concepts under the Application Architecture items in `builder-inventory.md`. What runs where, what the app remembers, who may see what, and how a change goes live safely.

Each concept has up to four checks, each counted once:

- **Know it**: says what it is and applies it on paper. Evidence: final exam questions on the concept,
  all three types (know it, use it, predict it), and `/learn` checks. Self-rated in the survey until
  the exam. (The exam's "use it" questions are scenarios on paper; the profile's "Used it" is real work.)
- **Used it**: used it in their own work. Evidence: the `/sprint-review` session scan, or the repo.
- **Built it**: built their own. Evidence: a file they wrote, committed in a shared repo.
- **Shipped it**: made it for real users and chose it on purpose (the inventory's level 5 rules).

A blank cell means the check does not apply to that concept. Evidence rules from
`builder-inventory.md` apply.

## A1 Client, server and deploy

| Concept | Used it | Built it | Shipped it | Chapter |
|---|---|---|---|---|
| **AA01 Three places code runs, and the trust rule.** The browser belongs to the user, who can read and change anything there. The server runs your code and holds the secret keys. The database stores each record. A check that runs only in the browser can be skipped. | n/a | n/a | n/a | Ch 7: Three Places Code Runs and Data Lives; Requests Connect the Places |
| **AA02 Server and client code in a project.** File names and folders say what runs where: in Next.js, page.tsx is a screen, route.ts is an endpoint, and a file marked "use client" is downloaded to the browser with everything it imports. node_modules, build output and .env.local stay out of git. | sessions place a check or a call in a named server file | a server route or endpoint the student added, committed | n/a | Ch 7: The Files in a Next.js Project |
| **AA03 State, render and events.** The screen is a function of state. A handler changes state through its setter, and the framework draws the screen again; a handler that edits a copy of the data leaves the screen unchanged. | n/a | n/a | n/a | Ch 7: How the Code Works; The loop: state, render, event, state |
| **AA04 Choosing a stack.** The set of tools for each layer: frontend, backend, database, hosting, sign-in. Pick the well-known option, and weigh who will maintain it after handoff. | n/a | a decision record that names at least two stacks and the reason for the one chosen | the chosen stack runs a product people outside the team reach | Ch 7: Tech Stacks and Languages |
| **AA05 Deploys, builds and hosts.** A host builds the code from the repository and serves it at an address; pushing to the main branch redeploys. A production build can fail where the development server worked. Hosts differ by what they run (Vercel for Next.js, Streamlit Community Cloud, GitHub Pages for static sites). | deploy and build commands, or build errors fixed, in sessions | this sprint's work live at an address others can open, or a fix to the live app from its build or runtime log | people outside the team reach it, and the host choice is in a decision record | Ch 2: Deploying a Prototype; Deployment with Vercel / GitHub Pages. Ch 9: Development server vs. production build |
| **AA06 Environments and development data.** Each running copy of the app (laptop, preview, production) reads its own settings, and the settings decide which database it touches. Once real people use the app, develop against a separate database filled with seed data. | n/a | a separate development or staging database, or seed data, committed | real users' data kept out of development, recorded | Ch 9: Environments: Where Your Code Runs and Which Data It Touches; Which database? The settings decide. Ch 8: Develop against a disposable copy |
| **AA07 Staging and feature flags.** Staging is a copy of production for trying a change before users see it. A feature flag lets deployed code reach some users before others. A change that takes effect for everyone at once, such as a migration, cannot hide behind a flag. | n/a | a staging environment or a feature flag in the code | a feature released to real users through a flag or staging, recorded | Ch 9: Staging; Feature flags; Staging or a flag? |
| **AA08 Logs, error reports and developer tools.** The browser console and network panel, the host's runtime logs, the database logs, and an error reporter show what users hit. A useful log line says what happened, where, and an id. | logs or developer tools read in sessions to find a fault | a fix made from a log or error report, or an error reporter set up | errors from real users caught and fixed from the reports | Ch 9: See What Is Happening: Logs and Error Reports. Ch 9c: Developer Tools |

## A2 Data and schema

| Concept | Used it | Built it | Shipped it | Chapter |
|---|---|---|---|---|
| **AA09 Tables, keys and relationships.** A table is a noun of the product, a row one instance, a column one fact with a type. A primary key identifies a row; a foreign key on the many side links two tables. Facts are stored once. Only a file or database outlives the session; page memory and local storage do not. | n/a | tables with keys defined in a migration, ORM schema or schema file, which the product reads and writes | real users' data lives there, and the schema choices are in a decision record | Ch 8: Design the Data Model First. Ch 9c: Where an App Keeps Data |
| **AA10 Migrations and schema changes.** A migration is a file that makes one schema change, applied in order and kept in git. Changing a table that holds real rows means migrating them, and a rollback does not undo data, so add before you remove. | migrations created or applied in sessions | a migration or schema file committed this sprint, including one that imports existing data | a schema change applied to a database real users rely on without losing data | Ch 8: Design the Data Model First (Migration). Ch 9: Rolling Back a Bad Deploy |
| **AA11 Queries and joins.** SELECT, WHERE, ORDER BY, LIMIT and JOIN. A join drops rows with no match unless it is a LEFT JOIN; an update or delete with no WHERE changes every row; a query that matches nothing returns an empty list. An index makes reads on a column fast. | SQL read or run in sessions | n/a | n/a | Ch 8: Asking the Database a Question |

## A3 Sign-in and access

| Concept | Used it | Built it | Shipped it | Chapter |
|---|---|---|---|---|
| **AA12 Authentication versus authorization.** Authentication proves who a user is. Authorization decides what that user may do to each row, and it holds only where the user cannot reach: the server or the database, never a hidden button. Permissions never come from model output. | n/a | n/a | n/a | Ch 7: Who You Are, What You May Do |
| **AA13 Sign-in and sessions.** Sign-in by password, a provider (OAuth) or a magic link gives the browser a signed token that every later request carries. The token expires and must never go in logs, chats or prompts. | n/a | sign-in built in the product | real users sign in | Ch 7: Who You Are, What You May Do |
| **AA14 Row-level security.** Policies in the database that decide which rows each request may touch, as if a WHERE were added to every query. With security on and no policies, every read returns an empty list, not an error. | n/a | a policy that stops one user from reading or changing another user's rows, committed | real users' rows protected by the policies, and the rules recorded | Ch 8: Row Level Security: Enforce Access Where the Data Lives |
| **AA15 Permission tests.** A test that signs in as one user, with the publishable key, and asks for data that user must not see. It keeps the access rules true as an agent changes the code. | permission tests run in sessions | a permission test committed, with a record that it ran | the tests run on a product real users sign in to | Ch 9b: Kinds of tests (permission tests). Ch 8: Row Level Security |

## A4 APIs and integrations

| Concept | Used it | Built it | Shipped it | Chapter |
|---|---|---|---|---|
| **AA16 Requests, responses and status codes.** A URL names the computer and the endpoint; DNS turns the name into an address. A request has a method, an address, headers and a body; a response has a status code (2xx worked, 4xx the request was the problem, 5xx the server was) and usually a JSON body. | n/a | n/a | n/a | Ch 7: How a Request Crosses the Internet; Requests Connect the Places. Ch 8: Requests Are Contracts That Fail |
| **AA17 The API contract.** An API is the set of requests a system agrees to answer, stated in its documentation. A change to the contract (a renamed field, a removed endpoint, a new required input) breaks the caller; other changes do not. | n/a | n/a | n/a | Ch 7: Requests Connect the Places (API documentation). Ch 8: Requests Are Contracts That Fail |
| **AA18 Handling failed calls.** Calls fail from the network, timeouts, sign-in, permission, rate limits and bad input. Code checks the response, retries where it is safe, and tells the user what happened without losing what they typed. | n/a | the product calls another system's API and handles a failed call in code | the integration works for real users, chosen in a decision record | Ch 8: Requests Are Contracts That Fail |
| **AA19 Calling a model API from the server.** A model call is a server-side request made with the provider's SDK from a route handler, with the key read from the environment. It costs money and time on every call. | n/a | a server route that calls a model API, committed | real users use the feature, and the provider is chosen in a decision record | Ch 11: Where the Call Lives |
| **AA20 Integrations with other services.** Connecting to another company's system for payments, email, calendars or data: an OAuth connection on the user's behalf, a webhook the other system calls, or an API the product offers. | n/a | an OAuth connection, webhook handler or offered endpoint in the product | real users' accounts connected through it | not taught yet (Ch 8: Requests Are Contracts That Fail names Stripe, Resend and Twilio only) |

## A5 Secrets, privacy and security

| Concept | Used it | Built it | Shipped it | Chapter |
|---|---|---|---|---|
| **AA21 Environment variables.** Settings kept outside the code, in .env.local and the host's settings, set separately for each environment. In Next.js only names starting with NEXT_PUBLIC_ reach the browser, so a secret never gets that prefix. | n/a | secret keys read from environment variables, with an .env.example and .env files ignored by git | n/a | Ch 8: Secrets and Sensitive Data. Ch 7: The Files in a Next.js Project. Ch 11: Where the Call Lives |
| **AA22 Publishable key, token and secret key.** The publishable key is public and can reach only what row-level security allows; a token identifies one signed-in user and expires; the secret key bypasses the rules and stays on the server. | n/a | n/a | n/a | Ch 7: Three credentials: publishable key, token, secret key; Supabase Introduction |
| **AA23 A leaked secret.** A key committed to a public repository is published. Deleting it from the code does not help, because history keeps it: create a new key, revoke the old one, then fix .gitignore. | n/a | no secret key, database file, log or personal data in the repo | n/a | Ch 8: Secrets and Sensitive Data (Rotate a leaked key). Ch 7: The Files in a Next.js Project (Not in git) |
| **AA24 Sensitive data and where it may go.** Personal, student and client data may go only where its rules allow. Sending it to a model, a log or an analytics event copies it to that company's servers, so send the least the task needs. | n/a | protections written down and applied to data about people (consent, redaction, access limits) | data about people outside the team handled under those protections, or a platform review passed | Ch 8: Secrets and Sensitive Data |
| **AA25 Common web attacks.** Injected SQL, scripts injected into a page (cross-site scripting), forged requests from another site, and open endpoints with no sign-in. Each has a standard defense: parameterized queries, escaped output, checks on the server. | n/a | a defense against one of them in the code, such as a content security policy | n/a | not taught yet |

## A6 Version control, checks and tech debt

| Concept | Used it | Built it | Shipped it | Chapter |
|---|---|---|---|---|
| **AA26 Commits, branches and pull requests.** A commit is a snapshot with a message. A branch builds a change without touching main; a pull request runs the checks, builds a preview and gets a review of the diff before the merge. Main stays releasable: branches are short and merge within a day or two, and unfinished work merges behind a flag. | branches and pull requests opened in sessions | branches or pull requests that contain code | n/a | Ch 9: Git: A Time Machine Plus Parallel Copies; Pull Requests: The Review Gate; Trunk-Based Development: Small Branches, Merged Often |
| **AA27 Continuous integration.** Tests, type check, lint and build run automatically on every pull request, on a fresh machine, and mark it pass or fail. | n/a | a CI workflow file that runs, with a run record | checks run on a product real users depend on, and a record says what they catch | Ch 9: Automated Checks: Tests, Types, and Lint |
| **AA28 Automated tests.** Code that runs the app's code with a chosen input and checks the answer: unit, integration, end-to-end, regression. A passing suite means only that the checks someone wrote did not fail; for a bug, write a test that fails first. | tests run in sessions | tests committed, with a record this sprint that they ran | tests guard a product real users depend on | Ch 9b: Tests: Code That Checks Your Code |
| **AA29 Rolling back a bad deploy.** When the live site breaks, point it back at the last good deployment first, then fix. A rollback does not undo data changes. | n/a | a recorded rollback or revert of a bad deploy | n/a | Ch 9: Rolling Back a Bad Deploy |
| **AA30 Technical debt.** Extra work later from a quick solution now, which makes every later change slower. Debt can be strategic (chosen, with a plan to repay) or accidental; pay it down when the code is about to be changed again. | n/a | a recorded list of debt taken on, with a plan, or a commit that pays one down | n/a | Ch 9b: What is Technical Debt?; Strategic vs. Accidental Debt; The Tech Debt Quadrant; When to Pay Down Tech Debt |

## Book gaps

- Deploying is taught in Ch 2 (Deploying a Prototype; Deployment with Vercel / GitHub Pages), both marked MOVE. Move them to Ch 7 after Tech Stacks, and add how to pick a host for a Python app (Streamlit, Render, PythonAnywhere) and what a build log is.
- Integrations with other services (OAuth connections on a user's behalf, webhooks, offering an API) are not taught. Ch 8 after Requests Are Contracts That Fail.
- Common web attacks (SQL injection, cross-site scripting, forged requests, endpoints with no sign-in) are not taught. Ch 8, a section after Secrets and Sensitive Data.
- Protections for data about people (consent, redaction, pseudonymizing interview or research data) are taught only as 'where data may go'. Ch 8: Secrets and Sensitive Data needs a part on consent and redaction, since A5 level 5 asks for them.
- Importing existing data (a spreadsheet or old system into tables, with duplicates removed) is not taught, though A2 level 4 counts it. Ch 8 after Design the Data Model First.
- Data and schema assume Supabase. Many products store data in SQLite, an ORM schema or a platform's own store. Ch 8 should say what counts as a defined schema in those stacks.
- Where an app keeps data (page memory, local storage, database) is only in the Ch 9c appendix. Ch 8 should open with it.

## Evidence a packet or the session scan cannot see yet

- A link check of 200 shows the address answers, not that this sprint's commit is what is deployed. A deployment id or commit SHA from the host (or a /version endpoint) would show it.
- Environment variables set on the host are not visible, so a feature that needs a key may not run in production. A smoke test of the live feature, saved, would show it.
- Migration, schema and row-level security texts are often absent from the packet; only file names are listed. Include the text of migrations and schema files changed this sprint.
- Test and CI runs leave no record unless the student commits output. The GitHub Actions run history for the repo would show runs and results.
- Pull requests are listed without saying whether the branch holds code or only plans, or whether they were merged by the due date. The packet should list each PR's changed files and merge date.
- A secret removed from the latest commit is still in history. A secret scan over the full history (for example gitleaks) would cover it.
- Whether real users sign in (A3 level 5) needs a count of sign-ins from the auth table, dated. The packet cannot see it today.
- Private code repos and non-web distribution (an App Store release) are not visible to the link check or the repo scan.
- The session scan can show Used it for this axis from commands: build and deploy commands, git branch and gh pr, migration commands, test runs, and log reads.
