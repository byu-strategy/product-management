"""Turn a sprint's grader results into Scott's review page, grades.csv, and a feedback page per student.

Run from the courses hub after the graders have written results:

    python3 ~/courses/product-management/scripts/sprint_feedback.py --sprint 1

Reads   ~/hubs/courses/_data/product-management/grading/sprint-N/results/<net_id>.json
        (one grader result each) and the packets beside them.
Writes  grading/sprint-N/review.html        every student, sortable, with evidence and frames
        grading/sprint-N/grades.csv         the gradebook /publish-grades reads
        grading/sprint-N/feedback/<net_id>.html and .pdf   what the student receives

grades.csv is the one place to change a grade. Its override_* columns, `approved`, and
`scott_note` are kept across reruns; everything else is rebuilt from the results. The final
score for a category is its override when one is set, the grader's score otherwise.

Nothing here touches Canvas. Student data stays in _data. This file holds none.
"""
import argparse, csv, html, json, subprocess, sys
from pathlib import Path

DATA = Path.home() / "hubs/courses/_data/product-management"
CATS = [("plan", "Plan, on time", 10), ("shipped", "You shipped it", 20),
        ("review", "Sprint review", 10), ("demo", "Demo", 10)]
KEEP = ["override_plan", "override_shipped", "override_review", "override_demo",
        "approved", "scott_note"]
COLS = (["net_id", "name", "preferred_first", "canvas_user_id", "confidence", "watch_loom",
         "plan", "shipped", "review", "demo", "grader_total"] + KEEP +
        ["final_total", "flags", "loom", "repo"])
e = html.escape


def final(row, cat):
    o = str(row.get(f"override_{cat}", "")).strip()
    return float(o) if o else float(row[cat])


def fmt(x):
    return f"{x:g}"


def load(sprint):
    base = DATA / f"grading/sprint-{sprint}"
    out = []
    for f in sorted((base / "results").glob("*.json")):
        r = json.loads(f.read_text())
        pk = base / f"{r['net_id']}.json"
        out.append((r, json.loads(pk.read_text()) if pk.exists() else {}))
    return base, out


def validate(base, items):
    """Stop before building anything a student would read if a result is malformed."""
    problems = []
    packets = {f.stem for f in base.glob("*.json")}
    for r, p in items:
        n = r.get("net_id", "?")
        for c, _, mx in CATS:
            s = (r.get("scores") or {}).get(c)
            if not isinstance(s, (int, float)) or not 0 <= s <= mx:
                problems.append(f"{n}: {c} score {s!r} outside 0-{mx}")
            if not (r.get("feedback") or {}).get(c):
                problems.append(f"{n}: no student feedback for {c}")
        text = " ".join([*(r.get("feedback") or {}).values(), r.get("review_missed") or "",
                         r.get("next_sprint") or ""])
        if "\u2014" in text:
            problems.append(f"{n}: em dash in student feedback")
        if any(w in text.lower() for w in (" late", "after the deadline", "after due", "seconds after")):
            problems.append(f"{n}: student feedback mentions lateness")
    missing = packets - {r["net_id"] for r, _ in items}
    if missing:
        print(f"{len(missing)} packets have no result yet: {', '.join(sorted(missing))}")
    if problems:
        sys.exit("fix these results first:\n  " + "\n  ".join(problems))


def write_csv(base, items):
    path, old = base / "grades.csv", {}
    if path.exists():
        old = {r["net_id"]: r for r in csv.DictReader(open(path))}
    rows = []
    for r, p in items:
        row = {"net_id": r["net_id"], "name": p.get("name", ""),
               "preferred_first": p.get("preferred_first", ""),
               "canvas_user_id": p.get("canvas_user_id", ""),
               "confidence": r.get("confidence", ""), "watch_loom": r.get("watch_loom", False),
               **{c: r["scores"][c] for c, _, _ in CATS}, "grader_total": sum(r["scores"].values()),
               **{k: old.get(r["net_id"], {}).get(k, "") for k in KEEP},
               "flags": " | ".join(r.get("flags", [])),
               "loom": (p.get("loom") or {}).get("url", ""), "repo": p.get("repo") or ""}
        row["final_total"] = fmt(sum(final(row, c) for c, _, _ in CATS))
        rows.append(row)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)
    path.chmod(0o600)
    return {r["net_id"]: r for r in rows}


STUDENT_CSS = """
body{font:15px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#1d2330;max-width:720px;margin:32px auto;padding:0 20px}
h1{font-size:22px;margin:0 0 4px}.sub{color:#5b6475;margin:0 0 24px}
table{border-collapse:collapse;width:100%;margin:8px 0 24px}
th,td{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid #e3e6ec}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#5b6475}
td.pts{white-space:nowrap;font-weight:600;width:70px}
h2{font-size:15px;margin:22px 0 6px}p{margin:0 0 10px}
.total{font-size:28px;font-weight:700}
"""


def student_page(r, p, row, sprint, points):
    total = sum(final(row, c) for c, _, _ in CATS)
    trs = "".join(
        f"<tr><td>{label}</td><td class=pts>{fmt(final(row, c))}/{mx}</td>"
        f"<td>{e(r['feedback'][c])}</td></tr>" for c, label, mx in CATS)
    extra = ""
    if r.get("review_missed"):
        extra += f"<h2>What your sprint review found that your retro did not mention</h2><p>{e(r['review_missed'])}</p>"
    if r.get("next_sprint"):
        extra += f"<h2>For next sprint</h2><p>{e(r['next_sprint'])}</p>"
    note = row.get("scott_note", "").strip()
    if note:
        extra += f"<h2>From Professor Murff</h2><p>{e(note)}</p>"
    return f"""<!doctype html><html><head><meta charset=utf-8><title>Sprint {sprint} feedback</title>
<style>{STUDENT_CSS}</style></head><body>
<h1>Sprint {sprint} feedback, {e(p.get('preferred_first') or p.get('name', ''))}</h1>
<p class=sub>MSB 341 Product Management</p>
<p class=total>{fmt(total)} / {points}</p>
<table><tr><th>Category</th><th>Score</th><th>What it was based on</th></tr>{trs}</table>
{extra}</body></html>"""


REVIEW_CSS = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#1d2330;--mute:#5b6475;--line:#e3e6ec;--hi:#fff7e0;--bad:#b42318;--ok:#067647;--acc:#2f5bd3}
@media (prefers-color-scheme:dark){:root{--bg:#12151b;--card:#1a1f27;--ink:#e6e9ef;--mute:#98a1b3;--line:#2a313c;--hi:#2c2610;--bad:#f97066;--ok:#47cd89;--acc:#7c9cf0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
header{padding:20px 24px 8px}h1{font-size:20px;margin:0}.mute{color:var(--mute)}
.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;padding:8px 24px 12px}
input,select{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.wrap{padding:0 24px 40px;overflow-x:auto}
table{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--line)}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{position:sticky;top:0;background:var(--card);cursor:pointer;user-select:none;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--mute);white-space:nowrap}
th.num,td.num{text-align:right}tr.row{cursor:pointer}tr.row:hover{background:var(--hi)}
.ov{color:var(--acc);font-weight:600}.low{color:var(--bad);font-weight:600}.high{color:var(--ok)}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;border:1px solid var(--line);font-size:12px;margin:1px 2px 1px 0}
tr.detail>td{background:var(--bg);padding:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.card h3{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--mute)}
.frames{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
.frames figure{margin:0}.frames img{width:100%;border:1px solid var(--line);border-radius:4px}
.frames figcaption{font-size:12px;color:var(--mute)}
dl{margin:0}dt{font-weight:600;margin-top:6px}dd{margin:0 0 4px}
.empty{padding:30px;text-align:center;color:var(--mute)}
"""

REVIEW_JS = """
const q=document.getElementById('q'),conf=document.getElementById('conf'),watch=document.getElementById('watch'),count=document.getElementById('count');
const body=document.querySelector('tbody');
function apply(){let n=0;const t=q.value.toLowerCase();
 document.querySelectorAll('tr.row').forEach(r=>{const ok=(!t||r.dataset.s.includes(t))&&(!conf.value||r.dataset.c===conf.value)&&(!watch.checked||r.dataset.w==='1');
  r.hidden=!ok;const d=r.nextElementSibling;if(!ok)d.hidden=true;if(ok)n++;});
 count.textContent=n+' of '+document.querySelectorAll('tr.row').length+' students';document.getElementById('none').hidden=n>0;}
[q,conf,watch].forEach(x=>x.addEventListener('input',apply));
document.querySelectorAll('tr.row').forEach(r=>r.addEventListener('click',()=>{const d=r.nextElementSibling;d.hidden=!d.hidden;}));
let dir={};document.querySelectorAll('th[data-k]').forEach((th,i)=>th.addEventListener('click',()=>{const k=th.dataset.k,num=th.classList.contains('num');dir[k]=!dir[k];
 const pairs=[...document.querySelectorAll('tr.row')].map(r=>[r,r.nextElementSibling]);
 pairs.sort((a,b)=>{let x=a[0].dataset[k],y=b[0].dataset[k];if(num){x=+x;y=+y}return (x>y?1:x<y?-1:0)*(dir[k]?1:-1)});
 pairs.forEach(([r,d])=>{body.appendChild(r);body.appendChild(d)});}));
apply();
"""


def review_page(base, items, rows, sprint, points):
    order = {"low": 0, "medium": 1, "high": 2}
    items = sorted(items, key=lambda it: (order.get(it[0].get("confidence"), 0),
                                          float(rows[it[0]["net_id"]]["final_total"])))
    trs = []
    for r, p in items:
        row = rows[r["net_id"]]
        cells = ""
        for c, _, mx in CATS:
            v, ov = final(row, c), str(row.get(f"override_{c}", "")).strip()
            cells += (f"<td class='num{' ov' if ov else ''}' title='grader {r['scores'][c]}'>"
                      f"{fmt(v)}</td>")
        confc = {"low": "low", "high": "high"}.get(r.get("confidence"), "")
        loom = p.get("loom") or {}
        frames = "".join(
            f"<figure><a href='{e(Path(fr['path']).relative_to(base).as_posix())}' target=_blank>"
            f"<img loading=lazy src='{e(Path(fr['path']).relative_to(base).as_posix())}'></a>"
            f"<figcaption>{fr['at_seconds'] // 60}:{fr['at_seconds'] % 60:02d}</figcaption></figure>"
            for fr in (loom.get("frames") or []))
        notes = "".join(f"<dt>{e(n['at'])}</dt><dd>{e(n['sees'])}</dd>" for n in r.get("demo_notes", []))
        checks = "".join(f"<dt>{e(k.replace('_', ' '))}</dt><dd>{e(v)}</dd>"
                         for k, v in (r.get("demo_checks") or {}).items())
        reasons = "".join(f"<dt>{label} ({fmt(final(row, c))}/{mx}, grader {r['scores'][c]})</dt>"
                          f"<dd>{e(r['reasons'][c])}</dd>" for c, label, mx in CATS)
        flags = "".join(f"<li>{e(f)}</li>" for f in r.get("flags", []))
        search = " ".join([r["net_id"], p.get("name", ""), " ".join(r.get("flags", []))]).lower()
        links = " · ".join(x for x in [
            f"<a href='{e(p['repo'])}' target=_blank>repo</a>" if p.get("repo") else "",
            f"<a href='{e(loom['url'])}' target=_blank>Loom ({loom.get('seconds')}s)</a>" if loom else "",
            f"<a href='feedback/{e(r['net_id'])}.html' target=_blank>student feedback page</a>"] if x)
        trs.append(
            f"<tr class=row data-s='{e(search)}' data-c='{e(r.get('confidence', ''))}' "
            f"data-w='{1 if r.get('watch_loom') else 0}' data-name='{e(p.get('name', ''))}' "
            f"data-total='{row['final_total']}' data-conf='{order.get(r.get('confidence'), 0)}' "
            f"data-flags='{len(r.get('flags', []))}'>"
            f"<td>{e(p.get('name', ''))}<div class=mute>{e(r['net_id'])}</div></td>"
            f"<td class={confc}>{e(r.get('confidence', ''))}{' · watch' if r.get('watch_loom') else ''}</td>"
            f"{cells}<td class=num><b>{row['final_total']}</b></td>"
            f"<td class=num>{len(r.get('flags', []))}</td>"
            f"<td>{'yes' if row.get('approved', '').strip().lower() == 'yes' else ''}</td></tr>"
            f"<tr class=detail hidden><td colspan=10><p>{links}</p><div class=grid>"
            f"<div class=card><h3>Why these scores</h3><dl>{reasons}</dl></div>"
            f"<div class=card><h3>Flags</h3><ul>{flags or '<li>none</li>'}</ul>"
            f"<h3>Demo checks</h3><dl>{checks or '<dd>no video</dd>'}</dl></div>"
            f"<div class=card><h3>What the student will read</h3><dl>"
            + "".join(f"<dt>{label}</dt><dd>{e(r['feedback'][c])}</dd>" for c, label, _ in CATS)
            + (f"<dt>Review found, retro missed</dt><dd>{e(r['review_missed'])}</dd>" if r.get("review_missed") else "")
            + (f"<dt>For next sprint</dt><dd>{e(r['next_sprint'])}</dd>" if r.get("next_sprint") else "")
            + f"</dl></div></div>"
            + (f"<div class=card style='margin-top:16px'><h3>Loom frames</h3><div class=frames>{frames}</div>"
               f"<h3 style='margin-top:12px'>Frame notes</h3><dl>{notes}</dl></div>" if frames else "")
            + "</td></tr>")
    approved = sum(1 for r in rows.values() if r.get("approved", "").strip().lower() == "yes")
    page = f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprint {sprint} grades</title><style>{REVIEW_CSS}</style></head><body>
<header><h1>Sprint {sprint} grades</h1><p class=mute>{len(items)} graded · {approved} approved ·
lowest confidence first · click a row for evidence · change a grade in grades.csv or tell Claude</p></header>
<div class=bar><input id=q placeholder="Search name, NetID, flag" size=30>
<select id=conf><option value="">All confidence</option><option>low</option><option>medium</option><option>high</option></select>
<label><input type=checkbox id=watch> Loom to watch</label><span id=count class=mute></span></div>
<div class=wrap><table><thead><tr><th data-k=name>Student</th><th data-k=conf>Confidence</th>
{''.join(f"<th class=num>{label.split(',')[0]} /{mx}</th>" for _, label, mx in CATS)}
<th class=num data-k=total>Total /{points}</th><th class=num data-k=flags>Flags</th><th>Approved</th></tr></thead>
<tbody>{''.join(trs)}</tbody></table><div id=none class=empty hidden>No students match.</div></div>
<script>{REVIEW_JS}</script></body></html>"""
    (base / "review.html").write_text(page)
    (base / "review.html").chmod(0o600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    base, items = load(a.sprint)
    if not items:
        sys.exit(f"no results in {base / 'results'}")
    points = sum(mx for _, _, mx in CATS) * (2 if a.sprint == 6 else 1)
    validate(base, items)
    rows = write_csv(base, items)
    fb = base / "feedback"
    fb.mkdir(exist_ok=True)
    for r, p in items:
        page = fb / f"{r['net_id']}.html"
        page.write_text(student_page(r, p, rows[r["net_id"]], a.sprint, points))
        page.chmod(0o600)
        if not a.no_pdf:
            pdf = page.with_suffix(".pdf")
            subprocess.run(["weasyprint", "-q", str(page), str(pdf)], check=True)
            pdf.chmod(0o600)
    review_page(base, items, rows, a.sprint, points)
    low = sum(1 for r, _ in items if r.get("confidence") == "low")
    watch = sum(1 for r, _ in items if r.get("watch_loom"))
    print(f"{len(items)} graded, {low} low confidence, {watch} Looms to watch")
    print(f"  {base / 'review.html'}\n  {base / 'grades.csv'}\n  {fb}/")


if __name__ == "__main__":
    main()
