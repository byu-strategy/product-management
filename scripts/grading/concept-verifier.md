# Concept check: a second look at the close calls

One coder has coded the sprint (`concepts/run-A/<net_id>.json`, rules in `concept-coder.md`). You
re-check only the credits most likely to be wrong, against the evidence they cite. You are not
recoding the sprint: do not add credits, and do not re-read the whole packet.

## Read first
`concept-coder.md` (all of it: the window, whose decision it is, what counts), `depth-levels.md`,
and the practice sentence of each concept you check (`concepts-for-coders.json`).

## What you check
1. Every breadth credit with a non-empty `borderline`.
2. Every depth level of 3 or 4.
3. Every depth level that rests on a decision record (whose decision it is).

For each, open the packet only where the `ref` or `evidence` points (the commit, the file in
`shipped_files`, the plan or review section, the Loom transcript). Confirm it if the evidence matches
the practice sentence or the level as written. Otherwise drop the credit, or lower the level to the
one the evidence supports. When the evidence is genuinely balanced, confirm: you are catching
errors, not raising the bar.

## Output (exactly this JSON) to `concepts/run-V/<net_id>.json`

```json
{"net_id": "", "sprint": 2, "checked": 9,
 "drop": [{"concept": "AA03", "why": "the commit changes only markup; no state changes what renders"}],
 "depth": [{"axis": "Design", "level": 2, "why": "the record was written by the agent and approved; no reason of the student's"}]}
```

`checked` is how many items you looked at. List only what you change; everything else stands.
`why` is read by Scott, not the student: plain and specific, no em dashes.
