#!/usr/bin/env python3
"""Build the builder concept lists from concepts/<axis>.json.

For each axis, writes:
  builder-concepts-<key>.md in this folder: the concept list, its practice checks and knowledge-only
  concepts (no exam content), and
  concepts-<key>.html in the private exam folder: the same list with the exam questions on each
  concept, which ones are seated on the final, and the gaps.
Run with no arguments for every axis, or name axis keys: python3 builder_concepts.py agentic design
"""
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAM = Path.home() / "Library/CloudStorage/OneDrive-BrighamYoungUniversity/3. Teaching/_materials/product-management/builder-exam"
CHECKS = """Each concept is measured in up to two ways:

- **Know it** (every concept): the exams. Midterm and final questions on the concept come in three
  types (know it, use it, predict it). The September survey self-rating stands in until the midterm.
- **Practice** (every concept not marked knowledge only): the student's own work shows it, counted
  once. The **Practice** column says what counts as evidence: the `/sprint-review` session scan's
  "Builder tools you used" list, or a file in a shared repo. This is the breadth half of the profile's
  practice score; depth (`depth-levels.md`) is assigned per axis, not per concept.

A concept marked **knowledge only** has no practice check: it is measured by the exams alone.
Evidence rules are in `concept-coder.md` and `depth-levels.md`."""


def exam_items():
    out = {}
    for f in (EXAM / "items/draft").glob("*.json"):
        d = json.loads(f.read_text())
        for x in d.get("items", []):
            out[x["id"]] = x
    return out


def practice(c):
    return "knowledge only (exams)" if c.get("knowledge_only") else (c.get("practice") or "n/a")


def build(key, items):
    d = json.loads((HERE / "concepts" / f"{key}.json").read_text())
    C = d["concepts"]
    lines = [f"# {d['axis']} concepts (draft, generated from concepts/{key}.json)", "",
             f"The named concepts under the {d['axis']} items. {d.get('intro', '')}".strip(), "",
             CHECKS, ""]
    for code, name in d["items"].items():
        lines += [f"## {code} {name}", "", "| Concept | Practice | Chapter |", "|---|---|---|"]
        for c in [c for c in C if c["item"] == code]:
            lines.append(f"| **{c['id']} {c['name']}.** {c['what']} | {practice(c)} | {c['chapter']} |")
        lines.append("")
    for title, field in (("Book gaps", "book_gaps"), ("Evidence a packet or the session scan cannot see yet", "evidence_notes")):
        if d.get(field):
            lines += [f"## {title}", ""] + [f"- {x}" for x in d[field]] + [""]
    (HERE / f"builder-concepts-{key}.md").write_text("\n".join(lines))

    e = html.escape
    def q(i):
        x = items.get(i, {})
        return f'<span class="q {x.get("exam", "missing")} {x.get("role", "")}" title="{e(x.get("topic", "not in the bank"))}">{i}</span>'
    def seated(ids):
        return sum(1 for i in ids if items.get(i, {}).get("exam") == "final" and items[i].get("role") == "seated")
    rows = ""
    for code, name in d["items"].items():
        rows += f'<tr class=grp><td colspan=4>{code} {e(name)}</td></tr>'
        for c in [c for c in C if c["item"] == code]:
            fs = seated(c["exam"])
            know = (" ".join(q(i) for i in c["exam"]) or '<span class=gap>no question</span>') + \
                (f'<div class=fs>{fs} seated on the final</div>' if fs else ('<div class="fs gap">none seated on the final</div>' if c["exam"] else ""))
            prac = '<span class=na>knowledge only</span>' if c.get("knowledge_only") else e(c.get("practice") or "")
            rows += (f'<tr><td><b>{e(c["id"])} {e(c["name"])}</b><div class=m>{e(c["what"])}</div></td><td class=k>{know}</td>'
                     f'<td>{prac}</td><td class=m>{e(c["chapter"])}</td></tr>')
    checks = sum(1 + (not c.get("knowledge_only") and bool(c.get("practice"))) for c in C)
    noq = [c["name"] for c in C if not c["exam"]]
    nofinal = [c["name"] for c in C if c["exam"] and not seated(c["exam"])]
    mapped = {i for c in C for i in c["exam"]} | {x["id"] for x in d.get("exam_elsewhere", [])}
    axis_final = [i for i, x in items.items() if x.get("axis") == d["axis"] and x.get("exam") == "final" and x.get("role") != "retired"]
    unmapped = sorted(i for i in axis_final if i not in mapped)
    missing = sorted(i for c in C for i in c["exam"] if i not in items)
    page = f"""<!doctype html><meta charset=utf-8><title>{e(d['axis'])} concepts</title><style>
body{{font:14px/1.5 -apple-system,Helvetica,Arial,sans-serif;color:#1d2330;max-width:1180px;margin:28px auto;padding:0 20px}}
h1{{font-size:22px;margin:0 0 4px}}.sub{{color:#6b7385;margin:0 0 18px}}
.cards{{display:flex;gap:12px;margin:0 0 18px;flex-wrap:wrap}}.card{{border:1px solid #e6e8ee;border-radius:8px;padding:10px 14px;min-width:150px}}.card b{{font-size:20px;display:block}}
table{{border-collapse:collapse;width:100%}}th{{position:sticky;top:0;background:#fff;text-align:left;font-size:12px;color:#6b7385;border-bottom:2px solid #e6e8ee;padding:6px 8px}}
td{{border-bottom:1px solid #f0f1f4;padding:8px;vertical-align:top}}tr.grp td{{background:#f6f7f9;font-weight:600;font-size:12.5px;letter-spacing:.03em}}
.m{{color:#6b7385;font-size:12.5px}}.na{{color:#c3c7cf}}.gap{{color:#b45f04;font-weight:600}}.fs{{font-size:12px;color:#6b7385;margin-top:3px}}
.q{{display:inline-block;font:11.5px ui-monospace,Menlo,monospace;border-radius:4px;padding:1px 5px;margin:1px;background:#eef2ff;color:#3346a8}}
.q.midterm{{background:#f3f4f6;color:#4a5262}}.q.retired{{text-decoration:line-through;opacity:.6}}.q.spare{{opacity:.8;border:1px dashed #9aa3b5}}.q.missing{{background:#fde8e8;color:#9b1c1c}}
.key{{font-size:12.5px;color:#6b7385;margin:6px 0 14px}}td.k{{width:190px}}ul{{margin:4px 0 0 18px;padding:0}}</style>
<h1>{e(d['axis'])}: concepts, checks, and the exam</h1>
<p class=sub>Generated from concepts/{key}.json. Know it (the exams) and Practice (the student's own work, counted once; knowledge-only concepts have none). Hover a question id for its topic.</p>
<div class=cards><div class=card><b>{len(C)}</b>concepts under {len(d['items'])} items</div><div class=card><b>{checks}</b>checks in all</div>
<div class=card><b>{len(noq)}</b>concepts with no exam question</div><div class=card><b>{len(nofinal)}</b>with questions, none seated on the final</div>
<div class=card><b>{len(unmapped)}</b>final questions on this axis mapped to no concept</div></div>
<p class=key><span class="q final seated">final, seated</span> <span class="q final spare">spare</span> <span class="q midterm seated">midterm</span> <span class="q final retired">retired</span></p>
<table><tr><th>Concept</th><th>Know it (exam questions)</th><th>Practice</th><th>Chapter</th></tr>{rows}</table>
<h3>Gaps</h3><ul><li><b>No question at all:</b> {e(", ".join(noq)) or "none"}</li>
<li><b>Questions exist, none seated on the final:</b> {e(", ".join(nofinal)) or "none"}</li>
<li><b>Final questions on this axis that map to no concept:</b> {" ".join(q(i) for i in unmapped) or "none"}</li>
<li><b>Questions on this axis that belong elsewhere:</b> {e("; ".join(f"{x['id']}: {x['belongs']}" for x in d.get("exam_elsewhere", []))) or "none"}</li>
{f'<li class=gap>Ids not in the bank: {e(", ".join(missing))}</li>' if missing else ""}</ul>"""
    (EXAM / f"concepts-{key}.html").write_text(page)
    SUMMARY.append((d["axis"], key, len(C), checks, len(noq), len(nofinal), len(unmapped), len(d.get("book_gaps", []))))
    print(f"{d['axis']}: {len(C)} concepts, {checks} checks, no question {len(noq)}, none seated on final {len(nofinal)}, "
          f"unmapped final {len(unmapped)}" + (f", MISSING IDS {missing}" if missing else ""))


SUMMARY = []


def overview():
    e = html.escape
    rows = "".join(f'<tr><td><a href="concepts-{k}.html">{e(a)}</a></td><td>{n}</td><td>{c}</td><td>{q}</td><td>{f}</td><td>{u}</td><td>{g}</td></tr>'
                   for a, k, n, c, q, f, u, g in SUMMARY)
    t = [sum(x[i] for x in SUMMARY) for i in range(2, 8)]
    (EXAM / "concepts-index.html").write_text(f"""<!doctype html><meta charset=utf-8><title>Builder concepts</title><style>
body{{font:14px/1.5 -apple-system,Helvetica,Arial,sans-serif;color:#1d2330;max-width:900px;margin:28px auto;padding:0 20px}}
table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #eceef2}}th{{font-size:12px;color:#6b7385}}
td:not(:first-child),th:not(:first-child){{text-align:right}}tr.t td{{font-weight:600}}a{{color:#2f5bd3}}</style>
<h1>Builder concepts: all six axes</h1><p>The spine of the builder system. Each axis page lists its concepts, their checks, and the exam questions on each.</p>
<table><tr><th>Axis</th><th>Concepts</th><th>Checks</th><th>No question</th><th>None seated on final</th><th>Final questions mapped to no concept</th><th>Book gaps</th></tr>
{rows}<tr class=t><td>Total</td>{"".join(f"<td>{x}</td>" for x in t)}</tr></table>""")


def coder_list():
    """concepts-for-coders.json: only what a concept coder uses (id, name, topic, what it is, the practice
    check, knowledge-only), about half the size of the full lists, which every coder reads at every step."""
    out = []
    for f in sorted((HERE / "concepts").glob("*.json")):
        d = json.loads(f.read_text())
        out.append({"axis": d["axis"], "items": d["items"], "evidence_notes": d.get("evidence_notes", ""),
                    "concepts": [{k: c[k] for k in ("id", "name", "item", "what", "practice", "knowledge_only") if k in c}
                                 for c in d["concepts"]]})
    (HERE / "concepts-for-coders.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    keys = sys.argv[1:] or sorted(p.stem for p in (HERE / "concepts").glob("*.json"))
    items = exam_items()
    for k in keys:
        build(k, items)
    if not sys.argv[1:]:
        overview()
    coder_list()
