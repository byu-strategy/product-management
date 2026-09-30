"""Render Scott's grading dossier for a sprint: one local HTML page, every student, all the evidence.

Called by sprint_feedback.py; not run on its own. The page is a roster on the left (search,
filters, sortable columns) and the selected student's dossier on the right: scores with the
grader's reasons, flags, the nine Loom frames with the grader's note under each (click for full
size), the demo checks, exactly what the student will read, and the raw evidence (plan, review,
transcript, commits, files). j and k move between students; the URL hash keeps your place.

The page links frames by relative path, so it must stay in its grading folder. It holds student
data: open it locally, never publish it.
"""
import html, json, statistics
from pathlib import Path

from sprint_config import COURSE_ID, SPRINTS
from post_grades import comment_text

CANVAS = "https://byu.instructure.com"


def _hex(shares, profile=None):
    if not shares:
        return ""
    from sprint_feedback import hexagon, focus_caption
    return f'<div class=hexbox>{hexagon(shares, profile)}<p class=why>{html.escape(focus_caption(shares))}</p></div>'


def _student(base, r, p, row, sprint, cats, final):
    loom = p.get("loom") or {}
    repo = p.get("repo") or ""
    frames = []
    notes = r.get("demo_notes") or []
    for i, fr in enumerate(loom.get("frames") or []):
        rel = Path(fr["path"]).relative_to(base).as_posix()
        s = fr["at_seconds"]
        frames.append({"src": rel, "at": f"{s // 60}:{s % 60:02d}",
                       "note": notes[i]["sees"] if i < len(notes) else ""})
    f = p.get("facts", {})
    review_id = SPRINTS[sprint]["review"]
    return {
        "id": r["net_id"], "name": p.get("name", ""), "first": p.get("preferred_first", ""),
        "confidence": r.get("confidence", ""), "watch": bool(r.get("watch_loom")),
        "approved": row.get("approved", "").strip().lower() == "yes",
        "total": float(row["final_total"]), "grader_total": float(row["grader_total"]),
        "cats": [{"key": c, "label": label, "max": mx, "score": final(row, c),
                  "grader": r["scores"].get(c), "override": bool(str(row.get(f"override_{c}", "")).strip()),
                  "reason": r.get("reasons", {}).get(c, ""), "feedback": r.get("feedback", {}).get(c, "")}
                 for c, label, mx in cats],
        "flags": r.get("flags", []),
        "late_days": f.get("canvas_days_late", 0),
        "next_sprint": r.get("next_sprint"),
        "scott_note": row.get("scott_note", ""),
        "pdf": f"feedback/{r['net_id']}.pdf",
        "comment": comment_text(row, sprint),
        "checks": r.get("demo_checks") or {},
        "difficulty": r.get("difficulty") or {},
        "hexagon": _hex(r.get("axes") or {}, p.get("baseline")), "axes_why": r.get("axes_why", ""),
        "other_repos": [{"repo": o["repo"], "commits": len(o.get("commits", []))} for o in p.get("other_repos", [])],
        "unshared": f.get("repos_named_but_not_shared", []),
        "frames": frames,
        "links": [x for x in [
            {"label": "Repo", "href": repo} if repo else None,
            {"label": "Review file", "href": f"{repo}/blob/HEAD/sprints/sprint-{sprint}-review.md"} if repo else None,
            {"label": "Plan file", "href": f"{repo}/blob/HEAD/sprints/sprint-{sprint}-plan.md"} if repo else None,
            {"label": f"{'Video (not Loom)' if loom.get('host') else 'Loom'}, {loom.get('seconds')}s",
             "href": loom["url"]} if loom.get("url") else None,
            {"label": "Where to see it", "href": f["readme_where_to_see_it"]}
            if (f.get("readme_where_to_see_it") or "").startswith("http") else None,
            {"label": "SpeedGrader", "href": f"{CANVAS}/courses/{COURSE_ID}/gradebook/speed_grader"
                                              f"?assignment_id={review_id}&student_id={p.get('canvas_user_id')}"},
            {"label": "Student PDF", "href": f"feedback/{r['net_id']}.pdf"},
        ] if x],
        "other_links": [l for l in (p.get("canvas") or {}).get("links", []) if "loom.com" not in l],
        "evidence": {
            "Plan as it stands": (p.get("plan") or {}).get("now") or "",
            "Plan as first submitted": (p.get("plan_submission") or {}).get("text") or "",
            "Sprint review report": (p.get("review") or {}).get("text") or "",
            "Loom transcript": loom.get("transcript") or "",
        },
        "commits": p.get("commits", []),
        "link_checks": p.get("link_checks", []),
        "files": [{"path": x["path"], "status": x["status"], "bytes": x.get("bytes")}
                  for x in p.get("shipped_files", [])],
        "artifacts": [{"src": Path(x["image"]).relative_to(base).as_posix(), "path": x["path"]}
                      for x in p.get("shipped_files", []) if x.get("image")],
    }


CSS = r"""
:root{--bg:#f4f2ee;--panel:#fffdf9;--ink:#1f1d1a;--mute:#6b665e;--line:#e4dfd6;--soft:#efebe3;
--acc:#8a3b12;--acc-soft:#f6e7dc;--good:#2f6b3a;--warn:#9a6700;--bad:#a8321f;--bar:#c9b9a3;--sel:#fbf3ea;
--serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;--sans:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15130f;--panel:#1d1b17;--ink:#ece7de;--mute:#a39c90;
--line:#34302a;--soft:#26231e;--acc:#e0915f;--acc-soft:#3a281c;--good:#7fc48b;--warn:#e3b341;--bad:#f0826d;--bar:#5c5243;--sel:#2a241c}}
:root[data-theme=dark]{--bg:#15130f;--panel:#1d1b17;--ink:#ece7de;--mute:#a39c90;--line:#34302a;--soft:#26231e;--acc:#e0915f;
--acc-soft:#3a281c;--good:#7fc48b;--warn:#e3b341;--bad:#f0826d;--bar:#5c5243;--sel:#2a241c}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font:14px/1.5 var(--sans)}
a{color:var(--acc)}
header.top{padding:22px 28px 16px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:18px 40px;align-items:flex-end}
.eyebrow{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--mute)}
h1{font:600 26px/1.15 var(--serif);margin:2px 0 0}
.stats{display:flex;gap:26px;flex-wrap:wrap}
.stat b{display:block;font:600 22px/1.1 var(--serif)}.stat span{font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:.08em}
.hist{display:flex;align-items:flex-end;gap:3px;height:44px}
.hist i{display:block;width:14px;background:var(--bar);border-radius:2px 2px 0 0;position:relative}
.hist i:hover::after{content:attr(data-t);position:absolute;bottom:100%;left:50%;transform:translateX(-50%);white-space:nowrap;
font:11px var(--sans);background:var(--ink);color:var(--panel);padding:2px 6px;border-radius:4px;font-style:normal}
main{display:grid;grid-template-columns:minmax(360px,440px) 1fr;height:calc(100vh - 110px)}
@media (max-width:900px){main{grid-template-columns:1fr;height:auto}.roster{max-height:50vh}}
.roster{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0}
.tools{padding:12px 16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;border-bottom:1px solid var(--line)}
input[type=search],select{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink)}
input[type=search]{flex:1;min-width:160px}
.chk{font-size:12px;color:var(--mute);display:flex;gap:4px;align-items:center}
.count{font-size:12px;color:var(--mute);width:100%}
.tablewrap{overflow:auto;flex:1}
table.list{border-collapse:collapse;width:100%}
.list th{position:sticky;top:0;background:var(--bg);text-align:left;font-size:11px;letter-spacing:.06em;text-transform:uppercase;
color:var(--mute);padding:8px 10px;border-bottom:1px solid var(--line);cursor:pointer;user-select:none;white-space:nowrap}
.list th.num,.list td.num{text-align:right}
.list th[aria-sort=ascending]::after{content:" \2191"}.list th[aria-sort=descending]::after{content:" \2193"}
.list td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
.list tr{cursor:pointer}.list tr:hover td{background:var(--soft)}.list tr.on td{background:var(--sel)}.list tr.on td:first-child{box-shadow:inset 3px 0 0 var(--acc)}
.list .sub{font-size:12px;color:var(--mute)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;vertical-align:middle}
.c-low{background:var(--bad)}.c-medium{background:var(--warn)}.c-high{background:var(--good)}
.empty{padding:40px 16px;text-align:center;color:var(--mute)}
.dossier{overflow:auto;padding:28px 36px 60px;min-height:0}
@media (max-width:900px){.dossier{padding:20px 16px}}
.dhead{display:flex;flex-wrap:wrap;justify-content:space-between;gap:16px;align-items:flex-start;border-bottom:1px solid var(--line);padding-bottom:18px}
.dhead h2{font:600 30px/1.1 var(--serif);margin:0}.dhead .id{color:var(--mute);margin-top:4px}
.big{font:600 44px/1 var(--serif);text-align:right}.big small{font-size:18px;color:var(--mute)}
.badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.badge{font-size:11px;letter-spacing:.04em;padding:3px 9px;border-radius:999px;border:1px solid var(--line);background:var(--panel)}
.badge.warn{border-color:var(--warn);color:var(--warn)}.badge.bad{border-color:var(--bad);color:var(--bad)}.badge.good{border-color:var(--good);color:var(--good)}
.links{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0 4px}
.links a{font-size:12.5px;text-decoration:none;padding:5px 11px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink)}
.links a:hover{border-color:var(--acc);color:var(--acc)}
section{margin-top:28px}
section>h3{font:600 12px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin:0 0 10px}
.cat{display:grid;grid-template-columns:150px 1fr;gap:6px 18px;padding:12px 0;border-top:1px solid var(--line)}
.cat:first-of-type{border-top:0}
.cat .lab{font-weight:600}.cat .pts{font:600 20px var(--serif)}.cat .pts small{font-size:13px;color:var(--mute);font-weight:400}
.meter{height:6px;background:var(--soft);border-radius:3px;overflow:hidden;margin-top:6px}.meter i{display:block;height:100%;background:var(--acc)}
.cat .ov{font-size:11px;color:var(--acc)}
.why{color:var(--ink)}
.flags{margin:0;padding:0;list-style:none}.flags li{padding:6px 10px;border-left:3px solid var(--warn);background:var(--panel);margin-bottom:6px;border-radius:0 4px 4px 0}
.flags li.late{border-left-color:var(--bad)}
.frames{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.frame{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
.frame img{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top;cursor:zoom-in;background:var(--soft)}
.frame .cap{padding:8px 10px;font-size:12.5px}.frame .t{font:600 12px var(--sans);color:var(--acc);margin-right:6px}
dl.checks{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:0}
dl.checks dt{font-weight:600;text-transform:capitalize}dl.checks dd{margin:0}
.hexbox svg{max-width:100%;height:auto;background:#fff;border-radius:8px}
.diffrow{display:flex;gap:28px;flex-wrap:wrap;margin-bottom:8px}.diffrow div b{display:block;font:600 24px var(--serif)}
.diffrow div span{font-size:11px;color:var(--mute);text-transform:uppercase;letter-spacing:.06em}
.pdf{width:100%;max-width:820px;height:1000px;border:1px solid var(--line);border-radius:8px;background:#fff}
.paper{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:18px 22px;max-width:760px}
.paper h4{font:600 13px var(--sans);margin:14px 0 4px}.paper p{margin:0 0 8px}
.paper table{border-collapse:collapse;width:100%}.paper td{padding:8px 6px;border-top:1px solid var(--line);vertical-align:top}
.paper td.p{white-space:nowrap;font-weight:600}
details{background:var(--panel);border:1px solid var(--line);border-radius:8px;margin-bottom:8px}
details>summary{cursor:pointer;padding:10px 14px;font-weight:600}
details pre{margin:0;padding:0 14px 14px;white-space:pre-wrap;font:12.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;max-height:520px;overflow:auto}
.mini{border-collapse:collapse;width:100%;font-size:12.5px}.mini td{padding:5px 8px;border-top:1px solid var(--line)}
.lightbox{position:fixed;inset:0;background:rgba(10,9,8,.88);display:flex;align-items:center;justify-content:center;z-index:9;padding:24px;flex-direction:column;gap:10px}
.lightbox[hidden]{display:none}.lightbox img{max-width:100%;max-height:88vh;border-radius:6px}.lightbox div{color:#eee;max-width:900px;text-align:center}
.keys{font-size:11px;color:var(--mute)}kbd{font:11px ui-monospace,monospace;border:1px solid var(--line);border-radius:3px;padding:0 4px;background:var(--panel)}
"""

JS = r"""
const S=JSON.parse(document.getElementById('data').textContent),meta=JSON.parse(document.getElementById('meta').textContent);
const $=q=>document.querySelector(q),esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=n=>(Math.round(n*10)/10).toString();
let order=S.map((_,i)=>i),sortKey='conf',dir=1,cur=null;
const confRank={low:0,medium:1,high:2};
function key(s,k){if(k==='diff')return s.difficulty.assessed||0;return k==='name'?s.name:k==='total'?s.total:k==='conf'?confRank[s.confidence]*1000+s.total:k==='flags'?s.flags.length:s.cats.find(c=>c.key===k)?.score}
function visible(s){const q=$('#q').value.toLowerCase();
 return (!q||(s.name+' '+s.id+' '+s.flags.join(' ')).toLowerCase().includes(q))&&(!$('#conf').value||s.confidence===$('#conf').value)
 &&(!$('#watch').checked||s.watch)&&(!$('#late').checked||s.late_days>0)&&(!$('#unapp').checked||!s.approved)}
function roster(){order.sort((a,b)=>{const x=key(S[a],sortKey),y=key(S[b],sortKey);return (x>y?1:x<y?-1:0)*dir});
 const rows=order.filter(i=>visible(S[i]));
 $('#tb').innerHTML=rows.map(i=>{const s=S[i];return `<tr data-i="${i}" class="${cur===i?'on':''}"><td><div>${esc(s.name)}</div><div class=sub>${esc(s.id)}</div></td>
 <td><span class="dot c-${esc(s.confidence)}"></span>${esc(s.confidence)}${s.watch?'<div class=sub>watch Loom</div>':''}</td>
 ${meta.cats.map(c=>{const x=s.cats.find(y=>y.key===c.key);return `<td class=num>${fmt(x.score)}${x.override?'*':''}</td>`}).join('')}
 <td class=num title="predicted / assessed">${s.difficulty.assessed?`${s.difficulty.predicted??'?'}→${s.difficulty.assessed}`:''}</td>
 <td class=num><b>${fmt(s.total)}</b></td><td class=num>${s.flags.length||''}</td><td>${s.approved?'yes':''}</td></tr>`}).join('');
 $('#count').textContent=`${rows.length} of ${S.length} students`;$('#none').hidden=rows.length>0;
 document.querySelectorAll('#tb tr').forEach(tr=>tr.onclick=()=>show(+tr.dataset.i));
 document.querySelectorAll('th[data-k]').forEach(th=>th.setAttribute('aria-sort',th.dataset.k===sortKey?(dir>0?'ascending':'descending'):'none'))}
function show(i){cur=i;const s=S[i];history.replaceState(null,'','#'+s.id);
 const cats=s.cats.map(c=>`<div class=cat><div><div class=lab>${esc(c.label)}</div><div class=pts>${fmt(c.score)}<small> / ${c.max}</small></div>
  <div class=meter><i style="width:${100*c.score/c.max}%"></i></div>${c.override?`<div class=ov>override; grader said ${c.grader}</div>`:''}</div>
  <div class=why>${esc(c.reason)}</div></div>`).join('');
 const frames=s.frames.length?`<div class=frames>${s.frames.map(f=>`<figure class=frame><img loading=lazy src="${esc(f.src)}" data-cap="${esc(f.at+'  '+f.note)}" alt="Loom frame at ${esc(f.at)}">
  <div class=cap><span class=t>${esc(f.at)}</span>${esc(f.note)}</div></figure>`).join('')}</div>`:'<p class=sub>No Loom frames. '+(s.other_links.length?'Other links submitted: '+s.other_links.map(l=>`<a href="${esc(l)}" target=_blank>${esc(l)}</a>`).join(', '):'No video submitted.')+'</p>';
 const checks=Object.keys(s.checks).length?`<dl class=checks>${Object.entries(s.checks).map(([k,v])=>`<dt>${esc(k.replace('_',' '))}</dt><dd>${esc(v)}</dd>`).join('')}</dl>`:'';
 const late=s.late_days?`<h4>Late work</h4><p>Submitted ${s.late_days} day(s) late; Canvas deducts ${Math.min(100,10*s.late_days)}%.</p>`:'';
 const paper=`<p class=sub>Canvas comment: <q>${esc(s.comment)}</q>, with this PDF attached.
  <a href="${esc(s.pdf)}" target=_blank>Open the PDF in its own tab</a>.</p>
  <iframe class=pdf src="${esc(s.pdf)}#view=FitH" title="Feedback PDF for ${esc(s.name)}"></iframe>`;
 const d=s.difficulty,diff=d.assessed?`<section><h3>Difficulty</h3><div class=diffrow>
  <div><b>${d.predicted??'–'}</b><span>predicted</span></div><div><b>${d.student_actual??'–'}</b><span>their actual</span></div>
  <div><b style="color:var(--acc)">${d.assessed}</b><span>assessed</span></div><div><b>${d.baseline_on_axis??'–'}</b><span>baseline, ${esc(d.axis||'')}</span></div></div>
  <p class=why>${esc(d.why||'')}</p><p class=sub>Effect on shipped: ${esc(d.effect_on_shipped||'none')}</p></section>`:'';
 const repos=(s.other_repos.length||s.unshared.length)?`<section><h3>Other repos</h3><table class=mini>${s.other_repos.map(o=>`<tr><td><a href="${esc(o.repo)}" target=_blank>${esc(o.repo.replace('https://github.com/',''))}</a></td><td>${o.commits} commits in window</td></tr>`).join('')}
  ${s.unshared.map(u=>`<tr><td>${esc(u)}</td><td>named, not shared</td></tr>`).join('')}</table></section>`:'';
 const lc=s.link_checks.length?`<table class=mini>${s.link_checks.map(l=>`<tr><td><a href="${esc(l.url)}" target=_blank>${esc(l.url)}</a></td>
  <td>${l.status===200?'<b style="color:var(--good)">200</b>':`<b style="color:var(--bad)">${esc(l.status??l.error)}</b>`}</td><td>${esc(l.title??'')}</td></tr>`).join('')}</table>`:'';
 const ev=Object.entries(s.evidence).filter(([,v])=>v).map(([k,v])=>`<details><summary>${esc(k)}</summary><pre>${esc(v)}</pre></details>`).join('')
  +(s.commits.length?`<details><summary>Commits in the window (${s.commits.length})</summary><table class=mini>${s.commits.map(c=>`<tr><td>${esc(c.sha)}</td><td>${esc(c.when.replace('T',' ').slice(0,16))}</td><td>${esc(c.message)}${c.after_due?' <b>(after due)</b>':''}</td></tr>`).join('')}</table></details>`:'')
  +(s.files.length?`<details><summary>Files the sprint added or changed (${s.files.length})</summary><table class=mini>${s.files.map(f=>`<tr><td>${esc(f.path)}</td><td>${esc(f.status)}</td><td>${f.bytes??''}</td></tr>`).join('')}</table></details>`:'');
 $('#dossier').innerHTML=`<div class=dhead><div><div class=eyebrow>Sprint ${meta.sprint} dossier</div><h2>${esc(s.name)}</h2><div class=id>${esc(s.id)}</div>
  <div class=badges><span class="badge ${s.confidence==='low'?'bad':s.confidence==='high'?'good':'warn'}">${esc(s.confidence)} confidence</span>
  ${s.watch?'<span class="badge warn">watch the Loom</span>':''}${s.late_days?`<span class="badge bad">${s.late_days} day(s) late</span>`:''}
  <span class="badge ${s.approved?'good':''}">${s.approved?'approved':'not approved'}</span></div></div>
  <div class=big>${fmt(s.total)}<small> / ${meta.points}</small><div class=keys style="margin-top:8px"><kbd>j</kbd> <kbd>k</kbd> next / previous</div></div></div>
  <div class=links>${s.links.map(l=>`<a href="${esc(l.href)}" target=_blank>${esc(l.label)}</a>`).join('')}</div>
  <section><h3>Scores and why</h3>${cats}</section>
  ${s.hexagon?`<section><h3>Where this sprint landed</h3>${s.hexagon}<p class=sub>${esc(s.axes_why)}</p></section>`:''}
  ${diff}${repos}
  ${s.flags.length?`<section><h3>Flags</h3><ul class=flags>${s.flags.map(f=>`<li class="${/^late/.test(f)?'late':''}">${esc(f)}</li>`).join('')}</ul></section>`:''}
  ${lc?`<section><h3>Links checked when the packet was built</h3>${lc}</section>`:''}
  ${s.artifacts.length?`<section><h3>Images from the work</h3><div class=frames>${s.artifacts.map(a=>`<figure class=frame><img loading=lazy src="${esc(a.src)}" data-cap="${esc(a.path)}" alt="${esc(a.path)}"><div class=cap>${esc(a.path)}</div></figure>`).join('')}</div></section>`:''}
  <section><h3>Demo, frame by frame</h3>${frames}</section>
  ${checks?`<section><h3>Demo checks</h3>${checks}</section>`:''}
  <section><h3>The feedback PDF, exactly as it will be sent</h3>${paper}</section>
  <section><h3>Evidence</h3>${ev||'<p class=sub>None.</p>'}</section>`;
 $('#dossier').scrollTop=0;
 document.querySelectorAll('.frame img').forEach(im=>im.onclick=()=>{$('#lb img').src=im.src;$('#lb div').textContent=im.dataset.cap;$('#lb').hidden=false});
 roster()}
$('#lb').onclick=()=>$('#lb').hidden=true;
['#q','#conf','#watch','#late','#unapp'].forEach(q=>$(q).addEventListener('input',roster));
document.querySelectorAll('th[data-k]').forEach(th=>th.onclick=()=>{dir=sortKey===th.dataset.k?-dir:1;sortKey=th.dataset.k;roster()});
document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT')return;
 if(e.key==='Escape')$('#lb').hidden=true;
 const vis=[...document.querySelectorAll('#tb tr')].map(t=>+t.dataset.i),p=vis.indexOf(cur);
 if(e.key==='j'&&p<vis.length-1)show(vis[p+1]);if(e.key==='k'&&p>0)show(vis[p-1]);});
roster();const h=location.hash.slice(1),start=S.findIndex(s=>s.id===h);
show(start>=0?start:order.filter(i=>visible(S[i]))[0]??0);
"""


def render(base, items, rows, sprint, points, cats, final):
    students = [_student(base, r, p, rows[r["net_id"]], sprint, cats, final) for r, p in items]
    totals = [s["total"] for s in students]
    bins = {}
    for t in totals:
        b = int(t // 5 * 5)
        bins[b] = bins.get(b, 0) + 1
    hi = max(bins.values()) if bins else 1
    hist = "".join(f'<i style="height:{4 + 40 * bins.get(b, 0) / hi}px" data-t="{b} to {b + 4.9:g}: {bins.get(b, 0)}"></i>'
                   for b in range(0, int(points) + 1, 5))
    stats = [("Graded", len(students)),
             ("Median", f"{statistics.median(totals):g}" if totals else "–"),
             ("Lowest", f"{min(totals):g}" if totals else "–"),
             ("Low confidence", sum(s["confidence"] == "low" for s in students)),
             ("Looms to watch", sum(s["watch"] for s in students)),
             ("Late", sum(bool(s["late_days"]) for s in students)),
             ("Approved", sum(s["approved"] for s in students))]
    meta = {"sprint": sprint, "points": points, "cats": [{"key": c} for c, _, _ in cats]}
    data = json.dumps(students).replace("</", "<\\/")
    heads = "".join(f'<th class=num data-k="{c}">{label.split(",")[0].replace("You shipped it", "Shipped").replace("Sprint review", "Review")}</th>'
                    for c, label, _ in cats)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprint {sprint} Dossier</title><style>{CSS}</style></head><body>
<header class=top><div><div class=eyebrow>MSB 341 · Product Management · local, contains student data</div><h1>Sprint {sprint} grading dossier</h1></div>
<div class=stats>{''.join(f'<div class=stat><b>{v}</b><span>{k}</span></div>' for k, v in stats)}</div>
<div><div class=hist title="Totals in bands of 5">{hist}</div><div class=keys>totals, 0 to {points}</div></div></header>
<main><div class=roster><div class=tools><input type=search id=q placeholder="Search name, NetID, flag">
<select id=conf><option value="">All confidence</option><option>low</option><option>medium</option><option>high</option></select>
<label class=chk><input type=checkbox id=watch>Loom to watch</label><label class=chk><input type=checkbox id=late>Late</label>
<label class=chk><input type=checkbox id=unapp>Not approved</label><div class=count id=count></div></div>
<div class=tablewrap><table class=list><thead><tr><th data-k=name>Student</th><th data-k=conf>Confidence</th>{heads}
<th class=num data-k=diff title="predicted to assessed">Diff</th><th class=num data-k=total>Total</th><th class=num data-k=flags>Flags</th><th>OK</th></tr></thead><tbody id=tb></tbody></table>
<div class=empty id=none hidden>No students match these filters.</div></div></div>
<div class=dossier id=dossier></div></main>
<div class=lightbox id=lb hidden><img alt=""><div></div></div>
<script type=application/json id=data>{data}</script><script type=application/json id=meta>{json.dumps(meta)}</script>
<script>{JS}</script></body></html>"""
