#!/usr/bin/env python3
"""Question-by-question class summary of the MSB 341 baseline survey, as one HTML page.

    python3 ~/courses/product-management/scripts/baseline_questions.py [export.xlsx]

Every scored question on the survey, grouped by axis in survey order, with the class average,
the share at 1-2 (needs teaching) and at 4-5 (could run it or teach it), a bar of the whole
1-to-5 distribution, and the average for each section. An average hides whether a class is
uniformly middling or split between beginners and experts; the bar and the two shares show
which. The page ends with the ten least known, ten best known, and five widest-spread questions.

Aggregates only, no student names, but it is still this class's survey, so it lives in
_data/product-management/baseline-analysis/ with a copy in _private, and prints cleanly to PDF
from the browser. /student-status rebuilds it on every run.

Respondents are matched to the roster exactly as analyze_baseline.py does, so the two reports
count the same students.
"""
import csv, html, shutil, statistics as st, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_baseline import pb, items_by_student, newest_export, ROSTER, OUT

PRIVATE = Path.home() / "courses/product-management/_private"
PAGE = OUT / "baseline-questions.html"
TABLE = OUT / "baseline-questions.csv"
LEVELS = ["New to me", "Familiar", "Conversant", "Direct and judge", "Teach it"]


def question_text(export):
    """(axis, item key) -> the question as the survey words it, in survey order."""
    hdr = pb.load_rows(export)[0]
    out = {}
    for h, mapped in zip(hdr, pb.build_axis_map(hdr)):
        if mapped and mapped not in out:
            out[mapped] = pb.HDR_RE.match(h.strip()).group(2).strip()
    return out


def summarize(export, roster):
    """Per-question stats, plus the questions on the form that no student in this class answered
    (the form was rebuilt while live, and one generation of questions went unanswered)."""
    # "MSB 341-002: Product Management" -> "MSB 341"
    section = {s["net_id"]: s["section"].split(":")[0].rsplit("-", 1)[0] for s in roster}
    per_student = items_by_student(export, roster)
    texts = question_text(export)
    rows, unanswered = [], []
    for (axis, key), text in texts.items():
        answers = {n: items[(axis, key)] for n, items in per_student.items() if (axis, key) in items}
        vals = list(answers.values())
        if not vals:
            unanswered.append((axis, text))
            continue
        counts = [sum(1 for v in vals if v == k) for k in range(1, 6)]
        by_sec = {}
        for n, v in answers.items():
            by_sec.setdefault(section.get(n, "?"), []).append(v)
        low, high = (counts[0] + counts[1]) / len(vals), (counts[3] + counts[4]) / len(vals)
        rows.append({"axis": axis, "question": text, "n": len(vals), "mean": st.mean(vals),
                     "low": low, "high": high, "sd": st.pstdev(vals), "counts": counts,
                     "sections": {s: st.mean(v) for s, v in by_sec.items()}})
    return rows, unanswered, len(per_student)


def bar(counts):
    total = sum(counts)
    segs = "".join(f'<span class="l{k + 1}" style="width:{c / total * 100:.2f}%" '
                   f'title="{LEVELS[k]}: {c} ({c / total:.0%})"></span>'
                   for k, c in enumerate(counts) if c)
    return f'<div class="bar">{segs}</div>'


def table(rows, sections, show_axis=False):
    head = "".join(f"<th class=num>{html.escape(s)}</th>" for s in sections)
    out = ['<table><thead><tr><th class=q>Question</th>'
           + ("<th>Area</th>" if show_axis else "")
           + f'<th class=num>Avg</th><th class=num>1-2</th><th class=num>4-5</th>'
             f'<th class=spread>Spread, 1 to 5</th>{head}<th class=num>n</th></tr></thead><tbody>']
    for r in rows:
        secs = "".join(f"<td class=num>{r['sections'][s]:.1f}</td>" if s in r["sections"]
                       else "<td class=num>–</td>" for s in sections)
        out.append(f"<tr><td class=q>{html.escape(r['question'])}</td>"
                   + (f"<td class=area>{html.escape(r['axis'])}</td>" if show_axis else "")
                   + f"<td class=num><b>{r['mean']:.1f}</b></td><td class=num>{r['low']:.0%}</td>"
                     f"<td class=num>{r['high']:.0%}</td><td class=spread>{bar(r['counts'])}</td>"
                     f"{secs}<td class='num dim'>{r['n']}</td></tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def page(rows, unanswered, n_resp, n_roster, export, sections):
    stamp = dt.datetime.fromtimestamp(export.stat().st_mtime)
    legend = "".join(f'<span><i class="l{k + 1}"></i>{k + 1} {LEVELS[k]}</span>' for k in range(5))
    body = []
    for axis in pb.AXES:
        ar = [r for r in rows if r["axis"] == axis]
        if not ar:
            continue
        avg = st.mean(r["mean"] for r in ar)
        body.append(f'<section><h2>{html.escape(axis)} <span class=meta>{len(ar)} questions · '
                    f'area average {avg:.1f}</span></h2>{table(ar, sections)}</section>')
    least = sorted(rows, key=lambda r: -r["low"])[:10]
    best = sorted(rows, key=lambda r: -r["high"])[:10]
    # Standard deviation, not the smaller of the two shares: the 4-5 share is small on every
    # question, so that measure just re-ranked "best known".
    split = sorted(rows, key=lambda r: -r["sd"])[:5]
    glance = (f'<section class=glance><h2>At a glance</h2>'
              f'<h3>Least known <span class=meta>highest share at 1-2, worth teaching in class</span></h3>'
              f'{table(least, sections, True)}'
              f'<h3>Best known <span class=meta>highest share at 4-5, students who could help others</span></h3>'
              f'{table(best, sections, True)}'
              f'<h3>Widest spread <span class=meta>answers furthest apart, so beginners and experts sit in the same room; suited to mixed groups</span></h3>'
              f'{table(split, sections, True)}</section>')
    unanswered_html = ""
    if unanswered:
        items = "".join(f"<li>{html.escape(t)} <span class=dim>({html.escape(a)})</span></li>"
                        for a, t in unanswered)
        unanswered_html = (f'<section><h3>Not in this report <span class=meta>{len(unanswered)} '
                           f'questions on the form that no one in the class answered. The form was '
                           f'rebuilt while it was live; most of these are other wordings of '
                           f'questions above</span></h3><ul class=dim>{items}</ul></section>')
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Baseline by Question</title>
<style>
:root {{
  --bg:#ffffff; --ink:#1a1a1a; --dim:#6b6b76; --rule:#e4e4ea; --head:#f6f6f9;
  --l1:#d9dcf2; --l2:#a9aee6; --l3:#7479d6; --l4:#4340d6; --l5:#231f8f;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#141418; --ink:#ececf1; --dim:#9a9aa6; --rule:#2c2c35; --head:#1c1c22;
  --l1:#2b2d4a; --l2:#43478a; --l3:#6368c9; --l4:#8c8ff0; --l5:#c3c5ff; }} }}
:root[data-theme="dark"] {{
  --bg:#141418; --ink:#ececf1; --dim:#9a9aa6; --rule:#2c2c35; --head:#1c1c22;
  --l1:#2b2d4a; --l2:#43478a; --l3:#6368c9; --l4:#8c8ff0; --l5:#c3c5ff; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink);
  font:14px/1.45 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }}
main {{ max-width:1100px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
h2 {{ font-size:17px; margin:36px 0 8px; padding-bottom:6px; border-bottom:2px solid var(--ink); }}
h3 {{ font-size:14px; margin:22px 0 6px; break-after:avoid; }}
.meta {{ font-weight:400; color:var(--dim); font-size:13px; margin-left:6px; }}
.sub {{ color:var(--dim); margin:0 0 16px; }}
.legend {{ display:flex; flex-wrap:wrap; gap:14px; font-size:12.5px; color:var(--dim); }}
.legend i {{ display:inline-block; width:12px; height:12px; border-radius:2px; margin-right:5px;
  vertical-align:-1px; }}
.key {{ font-size:12.5px; color:var(--dim); margin:8px 0 0; }}
.wrap {{ overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ text-align:left; font-weight:600; font-size:12px; color:var(--dim); background:var(--head);
  padding:6px 8px; border-bottom:1px solid var(--rule); white-space:nowrap; }}
td {{ padding:6px 8px; border-bottom:1px solid var(--rule); vertical-align:middle; }}
td.q {{ min-width:260px; }}
td.area {{ color:var(--dim); white-space:nowrap; font-size:12px; }}
.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.dim {{ color:var(--dim); }}
th.spread, td.spread {{ width:220px; min-width:160px; }}
.bar {{ display:flex; height:14px; border-radius:3px; overflow:hidden; background:var(--rule); }}
.bar span {{ display:block; height:100%; }}
.l1 {{ background:var(--l1); }} .l2 {{ background:var(--l2); }} .l3 {{ background:var(--l3); }}
.l4 {{ background:var(--l4); }} .l5 {{ background:var(--l5); }}
@media print {{
  main {{ max-width:none; padding:0; }} body {{ font-size:11px; }}
  .wrap {{ overflow:visible; }} td.q {{ min-width:0; }} td.area {{ white-space:normal; }}
  th.spread, td.spread {{ width:110px; min-width:0; }} th, td {{ padding:4px 5px; }}
  table {{ font-size:10.5px; }} section {{ break-inside:auto; }} tr {{ break-inside:avoid; }}
  h2 {{ break-after:avoid; }} .glance {{ break-before:page; }}
  .bar span {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
}}
</style></head>
<body><main>
<h1>MSB 341 / IS 693R builder baseline, question by question</h1>
<p class=sub>{n_resp} of {n_roster} enrolled students responded · {len(rows)} questions ·
survey export downloaded {stamp:%Y-%m-%d} · built {dt.date.today():%Y-%m-%d}</p>
<div class=legend>{legend}</div>
<p class=key><b>Avg</b> is the class average from 1 to 5. <b>1-2</b> is the share of the class
that would need it taught; <b>4-5</b> is the share that could run it or teach it. Section columns
are each section's average. <b>n</b> is how many answered that question.</p>
<div class=wrap>
{"".join(body)}
{glance}
</div>
{unanswered_html}
</main></body></html>
"""


def main():
    export = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_export()
    roster = [s for s in csv.DictReader(ROSTER.open(newline="", encoding="utf-8-sig"))
              if s["enrollment_state"] == "active"]
    rows, unanswered, n_resp = summarize(export, roster)
    sections = sorted({s for r in rows for s in r["sections"]})
    OUT.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(page(rows, unanswered, n_resp, len(roster), export, sections), encoding="utf-8")
    with TABLE.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["axis", "question", "n", "mean", "share_1_2", "share_4_5",
                    *[f"count_{k}" for k in range(1, 6)], *[f"mean_{s}" for s in sections]])
        for r in rows:
            w.writerow([r["axis"], r["question"], r["n"], f"{r['mean']:.2f}", f"{r['low']:.2f}",
                        f"{r['high']:.2f}", *r["counts"],
                        *[f"{r['sections'][s]:.2f}" if s in r["sections"] else "" for s in sections]])
    print(f"{len(rows)} questions, {n_resp} respondents, from {export.name}"
          + (f" ({len(unanswered)} more on the form that no one answered)" if unanswered else ""))
    pdf = PAGE.with_suffix(".pdf")
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if chrome.exists():
        import subprocess
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", PAGE.as_uri()], capture_output=True, timeout=120)
    for f in (PAGE, TABLE, pdf):
        if f.exists():
            f.chmod(0o600)
    print(f"  {PAGE}\n  {TABLE}" + (f"\n  {pdf}" if pdf.exists() else ""))
    try:
        (PRIVATE / OUT.name).mkdir(exist_ok=True)
        for p in (PAGE, TABLE, PAGE.with_suffix(".pdf")):
            shutil.copy2(p, PRIVATE / OUT.name / p.name)
        print(f"  {PRIVATE / OUT.name}")
    except OSError as e:
        print(f"  note: could not back up to _private ({e})")


if __name__ == "__main__":
    main()
