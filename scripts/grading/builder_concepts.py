#!/usr/bin/env python3
"""Build the builder concept lists from concepts/<axis>.json.

For each axis, writes:
  builder-concepts-<key>.md in this folder: the concept list and its checks (no exam content), and
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
CHECKS = """Each concept has up to four checks, each counted once:

- **Know it**: says what it is and when to use it. Evidence: final exam questions on the concept
  (and `/learn` checks). Self-rated in the survey until the exam.
- **Used it**: used it in their own work. Evidence: the `/sprint-review` session scan, or the repo.
- **Made it**: built one. Evidence: a file they wrote, committed in a shared repo.
- **Shipped it**: made it for real users and chose it on purpose (the inventory's level 5 rules).

A blank cell means the check does not apply to that concept. Evidence rules from
`builder-inventory.md` apply."""


def exam_items():
    out = {}
    for f in (EXAM / "items/draft").glob("*.json"):
        d = json.loads(f.read_text())
        for x in d.get("items", []):
            out[x["id"]] = x
    return out


def build(key, items):
    d = json.loads((HERE / "concepts" / f"{key}.json").read_text())
    C = d["concepts"]
    lines = [f"# {d['axis']} concepts (draft, generated from concepts/{key}.json)", "",
             f"The named concepts under the {d['axis']} items in `builder-inventory.md`. {d.get('intro', '')}".strip(), "",
             CHECKS, ""]
    for code, name in d["items"].items():
        lines += [f"## {code} {name}", "", "| Concept | Used it | Made it | Shipped it | Chapter |", "|---|---|---|---|---|"]
        for c in [c for c in C if c["item"] == code]:
            lines.append(f"| **{c['id']} {c['name']}.** {c['what']} | {c['used'] or 'n/a'} | {c['made'] or 'n/a'} | "
                         f"{c['shipped'] or 'n/a'} | {c['chapter']} |")
        lines.append("")
    (HERE / f"builder-concepts-{key}.md").write_text("\n".join(lines))

    e = html.escape
    def q(i):
        x = items.get(i, {})
        return f'<span class="q {x.get("exam", "missing")} {x.get("role", "")}" title="{e(x.get("topic", "not in the bank"))}">{i}</span>'
    def seated(ids):
        return sum(1 for i in ids if items.get(i, {}).get("exam") == "final" and items[i].get("role") == "seated")
    rows = ""
    for code, name in d["items"].items():
        rows += f'<tr class=grp><td colspan=6>{code} {e(name)}</td></tr>'
        for c in [c for c in C if c["item"] == code]:
            fs = seated(c["exam"])
            know = (" ".join(q(i) for i in c["exam"]) or '<span class=gap>no question</span>') + \
                (f'<div class=fs>{fs} seated on the final</div>' if fs else ('<div class="fs gap">none seated on the final</div>' if c["exam"] else ""))
            na = "<span class=na>n/a</span>"
            rows += (f'<tr><td><b>{e(c["name"])}</b><div class=m>{e(c["what"])}</div></td><td class=k>{know}</td>'
                     f'<td>{e(c["used"]) or na}</td><td>{e(c["made"]) or na}</td><td>{e(c["shipped"]) or na}</td>'
                     f'<td class=m>{e(c["chapter"])}</td></tr>')
    checks = sum(1 + bool(c["used"]) + bool(c["made"]) + bool(c["shipped"]) for c in C)
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
<p class=sub>Generated from concepts/{key}.json. Know it (the final exam), Used it (the session scan or the repo), Made it (a committed file), Shipped it (for real users, chosen on purpose). Hover a question id for its topic.</p>
<div class=cards><div class=card><b>{len(C)}</b>concepts under {len(d['items'])} items</div><div class=card><b>{checks}</b>checks in all</div>
<div class=card><b>{len(noq)}</b>concepts with no exam question</div><div class=card><b>{len(nofinal)}</b>with questions, none seated on the final</div>
<div class=card><b>{len(unmapped)}</b>final questions on this axis mapped to no concept</div></div>
<p class=key><span class="q final seated">final, seated</span> <span class="q final spare">spare</span> <span class="q midterm seated">midterm</span> <span class="q final retired">retired</span></p>
<table><tr><th>Concept</th><th>Know it (exam questions)</th><th>Used it</th><th>Made it</th><th>Shipped it</th><th>Chapter</th></tr>{rows}</table>
<h3>Gaps</h3><ul><li><b>No question at all:</b> {e(", ".join(noq)) or "none"}</li>
<li><b>Questions exist, none seated on the final:</b> {e(", ".join(nofinal)) or "none"}</li>
<li><b>Final questions on this axis that map to no concept:</b> {" ".join(q(i) for i in unmapped) or "none"}</li>
<li><b>Questions on this axis that belong elsewhere:</b> {e("; ".join(f"{x['id']}: {x['belongs']}" for x in d.get("exam_elsewhere", []))) or "none"}</li>
{f'<li class=gap>Ids not in the bank: {e(", ".join(missing))}</li>' if missing else ""}</ul>"""
    (EXAM / f"concepts-{key}.html").write_text(page)
    print(f"{d['axis']}: {len(C)} concepts, {checks} checks, no question {len(noq)}, none seated on final {len(nofinal)}, "
          f"unmapped final {len(unmapped)}" + (f", MISSING IDS {missing}" if missing else ""))


if __name__ == "__main__":
    keys = sys.argv[1:] or sorted(p.stem for p in (HERE / "concepts").glob("*.json"))
    items = exam_items()
    for k in keys:
        build(k, items)
