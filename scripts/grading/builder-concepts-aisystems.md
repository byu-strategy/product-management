# AI Systems concepts (draft, generated from concepts/aisystems.json)

The named concepts under the AI Systems items. Understanding how language models work and why they behave as they do; building AI into the product is Agentic Workflow.

Each concept is measured in up to two ways:

- **Know it** (every concept): the exams. Midterm and final questions on the concept come in three
  types (know it, use it, predict it). The September survey self-rating stands in until the midterm.
- **Practice** (every concept not marked knowledge only): the student's own work shows it, counted
  once. The **Practice** column says what counts as evidence: the `/sprint-review` session scan's
  "Builder tools you used" list, or a file in a shared repo. This is the breadth half of the profile's
  practice score; depth (`depth-levels.md`) is assigned per axis, not per concept.

A concept marked **knowledge only** has no practice check: it is measured by the exams alone.
Evidence rules are in `concept-coder.md` and `depth-levels.md`.

## S1 Tokens and the context window

| Concept | Practice | Chapter |
|---|---|---|
| **AS01 Tokens.** The model reads and writes tokens, pieces of text with ID numbers from a fixed vocabulary, about three quarters of an English word. Tokens are the unit of cost, speed and every limit, and code and other languages use more tokens per word. | knowledge only (exams) | Ch 10: Step 1: Text becomes tokens |
| **AS02 The context window.** The most tokens the model can take in at once: instructions, documents, the conversation so far, and its answer. When it fills, something is dropped or summarized, and what was dropped is gone. | knowledge only (exams) | Ch 10: The context window is working memory |
| **AS03 The stateless model.** Each call starts from zero, and the model's weights do not change from use. A conversation exists only because the app resends the history, and a correction given in one chat does not reach the next. | Committed code that stores a conversation or facts about a user in the product's database and sends them with later model calls. | Ch 10: The context window is working memory; Ch 11: The API Remembers Nothing |
| **AS04 The output limit.** A separate cap, in tokens, on how much the model writes in one call (max_tokens). An answer that reaches it stops mid-sentence. | Committed code that handles a model response cut off at the output limit (checks the stop reason, or splits the job into parts), with the limit named in a spec or the code. | Ch 10: Step 4: The model predicts the next token (one sentence) |
| **AS05 Keeping a long context in bounds.** Trimming, summarizing or chunking what is sent so the important tokens stay in the window. /compact and /clear do this for a Claude Code session; a product needs its own rule. | Committed code that trims, summarizes or splits what is sent to a model, with the limit it designs around named in a spec or the code. | Ch 10: The context window is working memory; Ch 11: The API Remembers Nothing |

## S2 Cost and latency

| Concept | Practice | Chapter |
|---|---|---|
| **AS06 Per-token pricing.** Model APIs bill per input token and per output token, and output costs about five times input on Anthropic's current models. A long conversation costs more each turn because every turn resends everything. | knowledge only (exams) | Ch 10: Step 1: Text becomes tokens; Ch 11: What It Costs. Ch 11: The API Remembers Nothing. Ch 10: The context window is working memory |
| **AS07 Estimating a feature's cost.** Tokens per call (in and out) times calls per user per day times users times price per token, done before shipping. A cost that is small in a demo can be large at a thousand users a day. | A cost estimate for an AI feature in a committed spec or decision record, with tokens per call, calls per user, users, and price per token each stated. | Ch 11: What It Costs; Ch 12: Every AI call is a cost |
| **AS08 Caching.** Prompt caching keeps a repeated opening of the prompt (a long system prompt or reference document) ready so repeated calls pay a fraction for it. Storing a model's answer and reusing it avoids the call altogether when the input has not changed. | Committed code that sets cache_control on a repeated prompt prefix, or stores a model result and reuses it in place of a new call. | Ch 11: What It Costs |
| **AS09 Measuring usage.** Every response reports its input and output tokens (usage), and a call's input can be counted before it is sent. Measured numbers replace guesses about cost and latency. | Committed code that logs input and output tokens or latency for each model call, with the numbers saved in the repo. | Ch 11: What It Costs |
| **AS10 What drives latency.** The model writes one token at a time, so long outputs are slow; attention runs over the whole context, so long inputs are slower too; larger models are slower than small ones. A call can take one second or ten. | A measured latency of a named model call in the product, saved in the repo. | Ch 10: Step 3: Attention mixes in context; Step 4: The model predicts the next token; Ch 11: What It Costs; Where It Breaks. Ch 11: Streaming |

## S3 How models are made

| Concept | Practice | Chapter |
|---|---|---|
| **AS12 Machine learning and training.** A model learns from examples of inputs paired with outputs: a loss measures its error and gradient descent adjusts every parameter a small step to lower it. A language model is a large neural network trained this way on text. | knowledge only (exams) | Ch 10: AI and Machine Learning; Under the Hood: The Math |
| **AS13 Attention and the transformer.** Attention lets each token draw on every earlier token, so its numbers reflect its context; a transformer repeats attention in stacked blocks. It runs over the whole context, which is why longer prompts cost more and take longer. | knowledge only (exams) | Ch 10: Step 3: Attention mixes in context |
| **AS14 Next-token prediction.** The model scores every token in its vocabulary, turns the scores into probabilities, picks one, appends it, and runs again until a stop token or the output limit. The model generates an answer token by token; it does not look one up. | knowledge only (exams) | Ch 10: Step 4: The model predicts the next token |
| **AS15 Sampling and temperature.** The next token is drawn from the probabilities, so the same input can give different output; temperature sets how random the draw is. Even temperature 0 is not fully deterministic, and newer models do not allow changing it. | A temperature setting on a model call in committed code, with the reason for the value in a comment, spec or decision record. | Ch 10: Step 4: The model predicts the next token |
| **AS16 Pretraining and the base model.** Self-supervised training on huge amounts of text, where each next token is its own label, sets the weights. The result is a base model that continues text and can follow examples in the prompt (few-shot) but is not yet an assistant. | knowledge only (exams) | Ch 10: Step 5: Pretraining on huge text |
| **AS17 Knowledge cutoff.** Pretraining text stops at a date, and nothing after it is in the weights. The model does not know today's date, recent changes or new library versions unless the prompt supplies them. | Committed code or a record that supplies current facts to a model (today's date, live data, or retrieved documents) and says the model would not know them otherwise. | Ch 10: Step 5: Pretraining on huge text |
| **AS18 Instruction tuning and human feedback.** Later training on example conversations and on people's preferences between answers (RLHF) turns a text completer into an assistant. It changes behavior far more than knowledge. | knowledge only (exams) | Ch 10: Step 6: Fine-tuning and human feedback shape behavior |
| **AS19 Sycophancy.** Because people rate agreement a little higher than correction, the model learns to agree and may drop a correct answer when pushed. Ask for the case against, and judge disagreement on the evidence. | knowledge only (exams) | Ch 10: Step 6: Fine-tuning and human feedback shape behavior |

## S4 Retrieval and embeddings

| Concept | Practice | Chapter |
|---|---|---|
| **AS20 Embeddings.** A list of numbers that places a token, sentence or document on a map of meaning, so similar meanings sit close together. Search by embedding matches meaning, and it can miss exact strings such as part numbers or IDs. | Committed code that calls an embedding model and stores the vectors in the product. | Ch 10: Step 2: Tokens become embeddings; Ch 11: Grounding Answers in Your Data |
| **AS21 Retrieval-augmented generation (RAG).** Find the pieces of your own documents nearest in meaning to the question and put them in the prompt, so the model answers from them. It supplies text at question time and does not change the model; it addresses the cutoff and private data, and moves the risk to retrieval. | Retrieval in committed code: stored chunks, the nearest ones fetched for a question, and those chunks sent to the model with the question. | Ch 11: Grounding Answers in Your Data |
| **AS22 Chunking and the vector store.** Documents are split into passages of a few hundred tokens, the unit that gets retrieved, and each passage is stored next to its embedding (in Supabase, a pgvector column). Documents and questions must be embedded with the same model. | Committed chunking code with a stated chunk size, and a vector column or table that stores the chunks. | Ch 11: Grounding Answers in Your Data |
| **AS23 Where retrieval fails.** A document never loaded, the wrong chunks fetched, or an answer given anyway: each still produces a fluent, cited answer. Test retrieval on its own by checking, for each test question, whether the right chunk came back. | A committed retrieval test: questions with the chunk each should return, and the results of a run. | Ch 11: Grounding Answers in Your Data |

## S5 Hallucination and verification

| Concept | Practice | Chapter |
|---|---|---|
| **AS24 Hallucination.** Fluent, confident output that is false. The model produces the most plausible continuation and nothing inside it checks whether plausible is true, so its confidence says nothing about accuracy. | A committed analysis that checks a model's claims against sources and records which claims were correct, partly correct, and invented. | Ch 10: Plausible is not true; Ch 11: Where It Breaks |
| **AS25 Checking model output against a source.** Anything that matters is checked against something trusted: required quotes or sources, a validation rule, a second independent pass, or a person approving before it is used. Where a wrong answer is expensive, the check sits in the path. | Committed code that checks the product's model output before it is used (a validation rule, required sources, a second independent pass, or a person approving), or a commit that traces a wrong product output to its cause and fixes it. Checks on the coding agent's output are AW17. | Ch 10: Plausible is not true; Ch 11: Where It Breaks |
| **AS26 The jagged frontier.** Models are strong at some tasks and fail at nearby tasks that look no harder, such as exact counting or long arithmetic, and the edge moves with each release. Test your own task; reputation will not tell you. | The product's core AI task run on realistic inputs that include an edge case, with a prediction for each input and the results, committed. | Ch 10: The jagged frontier |

## S6 Choosing a model or technique

| Concept | Practice | Chapter |
|---|---|---|
| **AS27 When not to use a model.** Anything that must be exact or stable (an ID, a price, a sum, a permission check) comes from code. Use the model for the part that needs language and judgment. | A committed decision record that names a model option and a non-model option for one feature and the reason for the choice. | Ch 11: Where It Breaks; Ch 10: The jagged frontier |
| **AS28 Model tiers: capability, cost and speed.** Larger models are more capable and cost more per token and run slower; the smallest fit simple, high-volume, latency-sensitive work. Start with the most capable and move down only when measurement shows the smaller one is good enough. | A committed decision record that chooses a model, names an alternative model, and gives the reason. | Ch 11: What It Costs (one paragraph, On choosing a model) |
| **AS29 Prompting, retrieval or fine-tuning.** Prompting (instructions and examples) changes one call; retrieval supplies facts at question time; fine-tuning retrains the model and changes its behavior; it is a poor way to add facts that change. Try them in that order of cost. | A committed decision record that chooses prompting, retrieval or fine-tuning for a feature and names an alternative technique. | not taught yet as a comparison (Ch 10: Prompting; Step 6; Ch 11: Grounding Answers in Your Data each cover one technique) |

## Book gaps

- Choosing a technique (prompting, retrieval, fine-tuning) has no section. Add one to Ch 11 after Grounding Answers in Your Data, with when each fits and what fine-tuning cannot do (add facts that change).
- Choosing a model tier is one paragraph inside Ch 11: What It Costs. A short section on capability, cost and speed tradeoffs would give S6 a home; measurement stays with Agentic Workflow's evals.
- Embedding search missing exact strings (part numbers, IDs, names) and keyword or hybrid search are not taught, though AS-F-02 tests it. Add a paragraph to Ch 11: Grounding Answers in Your Data.
- The output limit (max_tokens, stop reason, an answer cut off mid-sentence) gets one sentence in Ch 10 Step 4. Add a paragraph to Ch 11: The API Remembers Nothing or What It Costs.
- Latency drivers are spread across Ch 10 Steps 3 and 4 and Ch 11 Where It Breaks. Ch 11: What It Costs could add a short list: output length, input length, model size, and time to first token with streaming.
- Keeping a long context in bounds in a product (trim, summarize, chunk) is named in Ch 11: The API Remembers Nothing but not shown. A worked example with a rule (keep the last N turns plus a summary) would support S1 level 4.
- Logging usage per call (response.usage) is shown as one line; how to save the numbers so they count as evidence for S2 level 4 is not said.
- Cost to serve and margin per user is owned by Launch and Learn (LL14); AI Systems keeps the per-call cost concepts.

## Evidence a packet or the session scan cannot see yet

- The session scan counts slash commands, so /context, /compact and /clear are visible for AS02 and AS05. It cannot see token counts or cost per session; adding the session's token totals to the scan would make AS06 checkable as practice.
- Product token usage, latency and cost live in the product's logs or provider dashboard, which the packet does not see. Only numbers saved in the repo (a usage log, a measured table in a spec) count as S2 practice evidence.
- Database or page latency is not model latency. A coder needs the S2 practice sentence to say model or service calls, and the record to say which call was timed.
- Many S4 and S5 builds sit in code that calls a model inside the product. A private repo the coder cannot open hides them; the packet should list which repos were shared.
- S3 concepts (pretraining, attention, RLHF, the cutoff) rarely show in a build, so the exams measure most of them. Depth level 3 (Decided) from S3 needs a recorded decision that names the training fact it depends on, which students seldom write. A prompt in the decision template (what can the model not know here?) would surface it.
- A cost estimate (AS07) and a margin calculation (AS11) are often in the sprint plan or a pricing doc rather than code. The packet should include the plan and any pricing file so they can be checked.
- A check on model output (AS25) and a check on the coding agent's output (W3) look the same in a commit. The coder needs to know whether the checked output is produced by the product for its users or by the agent building it.
