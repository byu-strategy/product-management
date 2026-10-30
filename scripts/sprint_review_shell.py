"""Scott's review page for a sprint: a rail of every student on the left, that student's instructor
report on the right. The reports are the same files the students get (feedback/<net_id>-scott.html,
with the instructor notes), so what Scott reviews is exactly what goes out.

Order: the students who most need a look come first (low confidence, a Loom to watch, fairness
findings, concepts the check dropped), then the rest by total, lowest first. Approving still happens in
grades.csv ("approve all", "approve everyone but X"); the rail shows the result after a rebuild.
"""
import html
import json


def e(x):
    return html.escape(str(x if x is not None else ""))


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def fmt(x):
    return str(int(x)) if float(x) == int(x) else f"{x:.1f}"


def render(items, rows, sprint, plans, growth, fairness, review_max):
    people = []
    for r, p in items:
        n = r["net_id"]
        row = rows.get(n, {})
        plan = num((plans.get(n) or {}).get("score")) if sprint > 1 else 0
        wrap = num(row.get("final_total"))
        total, total_max = plan + wrap, (10 if sprint > 1 else 0) + review_max
        G = growth.get(n) or {}
        conf = r.get("confidence") or ""
        needs = []
        if conf == "low":
            needs.append("low confidence")
        if r.get("watch_loom"):
            needs.append("watch the Loom")
        if [x for x in fairness.get(n) or [] if not x.lower().startswith("no findings")]:
            needs.append("fairness")
        if G.get("disputed"):
            needs.append(f"{len(G['disputed'])} concept{'s' * (len(G['disputed']) != 1)} dropped")
        people.append({
            "id": n, "name": p.get("name") or row.get("name") or n,
            "total": fmt(total), "max": total_max, "pct": total / total_max if total_max else 0,
            "conf": conf, "needs": needs, "look": bool([x for x in needs if not x.endswith(("dropped", "disputed"))]) or conf == "medium",
            "approved": (row.get("approved") or "").strip().lower() == "yes",
            "grew": round(sum(num(v) for v in ((G.get("rings") or [{}])[-1].get("points") or {}).values())) if G else None,
        })
    rank = {"low": 0, "medium": 1, "high": 2}
    people.sort(key=lambda x: (not x["look"], rank.get(x["conf"], 1), x["pct"], x["name"]))
    data = json.dumps(people).replace("</", "<\\/")
    n_look = sum(1 for x in people if x["look"])
    n_ok = sum(1 for x in people if x["approved"])
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprint {sprint} review</title>
<style>
:root{{--ink:#1f2430;--mute:#6b7280;--line:#e5e7eb;--amber:#b06a12;--soft:#fafafb;--sel:#fdf3e6}}
*{{box-sizing:border-box}}html,body{{height:100%;margin:0}}
body{{font:14px/1.5 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--ink);background:#fff;display:grid;grid-template-columns:300px 1fr;height:100vh}}
aside{{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0}}
.top{{padding:14px 14px 8px;border-bottom:1px solid var(--line)}}
.top h1{{font-size:15px;margin:0 0 2px}}.top .sub{{font-size:12px;color:var(--mute);margin:0 0 10px}}
.top input{{width:100%;font:inherit;font-size:13px;padding:6px 9px;border:1px solid var(--line);border-radius:6px}}
.top input:focus-visible{{outline:2px solid #2f5bd3;outline-offset:-1px}}
.seg{{display:flex;margin:8px 0 0;border:1px solid var(--line);border-radius:6px;overflow:hidden}}
.seg button{{flex:1;font:inherit;font-size:12px;padding:4px 6px;border:0;background:#fff;color:var(--mute);cursor:pointer}}
.seg button+button{{border-left:1px solid var(--line)}}.seg button.on{{background:var(--sel);color:var(--ink);font-weight:600}}
.seg button:focus-visible{{outline:2px solid #2f5bd3;outline-offset:-2px}}
.view{{display:flex;gap:6px;align-items:center;margin:8px 0 0;font-size:12px;color:var(--mute)}}
.view label{{display:flex;gap:5px;align-items:center;cursor:pointer;white-space:nowrap}}.view input{{margin:0}}
ol{{list-style:none;margin:0;padding:4px 0;overflow:auto;flex:1}}
li a{{display:grid;grid-template-columns:1fr auto;gap:2px 8px;padding:8px 14px;color:var(--ink);text-decoration:none;border-left:3px solid transparent}}
li a:hover{{background:var(--soft)}}li a.on{{background:var(--sel);border-left-color:var(--amber)}}
li a:focus-visible{{outline:2px solid #2f5bd3;outline-offset:-2px}}
.nm{{font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.sc{{font-variant-numeric:tabular-nums;font-weight:600}}.sc small{{color:var(--mute);font-weight:400}}
.meta{{grid-column:1/-1;font-size:11.5px;color:var(--mute);display:flex;gap:6px;flex-wrap:wrap}}
.tag{{padding:0 6px;border-radius:999px;background:#f1f2f5}}.tag.need{{background:#fcebd0;color:#80460a}}.tag.ok{{background:#e8f4ec;color:#2c7a4c}}
.empty{{padding:20px 14px;color:var(--mute);font-size:13px}}
.foot{{border-top:1px solid var(--line);padding:8px 14px;font-size:11.5px;color:var(--mute)}}
main{{min-width:0;display:flex;flex-direction:column}}
.bar{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:8px 16px;border-bottom:1px solid var(--line);font-size:13px}}
.bar b{{font-weight:600}}.bar .nav button{{font:inherit;font-size:12.5px;padding:3px 10px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer}}
.bar .nav button:disabled{{opacity:.4;cursor:default}}.bar a{{color:#2f5bd3;font-size:12.5px}}
iframe{{border:0;flex:1;width:100%}}
@media(max-width:760px){{body{{grid-template-columns:1fr;grid-template-rows:45vh 1fr}}aside{{border-right:0;border-bottom:1px solid var(--line)}}}}
</style></head><body>
<aside>
 <div class=top><h1>Sprint {sprint} review</h1>
  <p class=sub>{len(people)} students · {n_look} to look at · {n_ok} approved</p>
  <input type=search id=q placeholder="Search by name" aria-label="Search students">
  <div class=seg role=group aria-label=Show>
   <button type=button data-f=all class=on aria-pressed=true>All</button>
   <button type=button data-f=look aria-pressed=false>To look at</button>
   <button type=button data-f=open aria-pressed=false>Not approved</button></div>
  <div class=view><label><input type=checkbox id=stu> Student copy</label></div>
 </div>
 <ol id=list></ol>
 <div class=foot><span id=count></span> · j and k move between students</div>
</aside>
<main>
 <div class=bar><span id=who></span><span class=nav><button type=button id=prev aria-label="Previous student">Previous</button>
  <button type=button id=next aria-label="Next student">Next</button> <a id=open target=_blank rel=noopener>Open on its own</a></span></div>
 <iframe id=frame title="Student report"></iframe>
</main>
<script>
const P={data};
let filter='all',cur=null;
const list=document.getElementById('list'),frame=document.getElementById('frame'),q=document.getElementById('q'),stu=document.getElementById('stu');
const store={{get:k=>{{try{{return localStorage.getItem(k)}}catch(_){{return null}}}},set:(k,v)=>{{try{{localStorage.setItem(k,v)}}catch(_){{}}}}}};
const shown=()=>P.filter(p=>(filter==='all'||(filter==='look'&&p.look)||(filter==='open'&&!p.approved))&&p.name.toLowerCase().includes(q.value.trim().toLowerCase()));
function draw(){{
  const xs=shown();list.innerHTML='';
  if(!xs.length){{list.innerHTML='<li class=empty>No students match.</li>'}}
  xs.forEach(p=>{{const li=document.createElement('li'),a=document.createElement('a');a.href='#'+p.id;a.dataset.id=p.id;if(p.id===cur)a.className='on';
    const tags=p.needs.map(t=>`<span class="tag need">${{t}}</span>`).join('')+(p.conf&&p.conf!=='low'?`<span class=tag>${{p.conf}}</span>`:'')
      +(p.grew!==null?`<span class=tag>+${{p.grew}} growth</span>`:'')+(p.approved?'<span class="tag ok">approved</span>':'');
    a.innerHTML=`<span class=nm></span><span class=sc>${{p.total}}<small>/${{p.max}}</small></span><span class=meta>${{tags}}</span>`;
    a.querySelector('.nm').textContent=p.name;
    a.onclick=ev=>{{ev.preventDefault();pick(p.id)}};li.append(a);list.append(li)}});
  document.getElementById('count').textContent=`${{xs.length}} shown`;
  nav();
}}
function pick(id){{
  const p=P.find(x=>x.id===id);if(!p)return;cur=id;store.set('rv{sprint}',id);history.replaceState(null,'','#'+id);
  const src=`feedback/${{id}}${{stu.checked?'':'-scott'}}.html`;frame.src=src;document.getElementById('open').href=src;
  document.getElementById('who').innerHTML='';const b=document.createElement('b');b.textContent=p.name;
  document.getElementById('who').append(b,` · ${{p.total}}/${{p.max}}${{stu.checked?' · student copy':''}}`);
  list.querySelectorAll('a').forEach(a=>a.classList.toggle('on',a.dataset.id===id));
  const on=list.querySelector('a.on');on&&on.scrollIntoView({{block:'nearest'}});nav();
}}
function step(d){{const xs=shown(),i=xs.findIndex(p=>p.id===cur);const n=xs[i+d];if(n)pick(n.id)}}
function nav(){{const xs=shown(),i=xs.findIndex(p=>p.id===cur);document.getElementById('prev').disabled=i<=0;document.getElementById('next').disabled=i<0||i>=xs.length-1}}
document.getElementById('prev').onclick=()=>step(-1);document.getElementById('next').onclick=()=>step(1);
document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{{filter=b.dataset.f;
  document.querySelectorAll('.seg button').forEach(x=>{{x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)}});draw()}});
q.oninput=draw;stu.onchange=()=>cur&&pick(cur);
const keys=ev=>{{if(ev.target.matches&&ev.target.matches('input'))return;if(ev.key==='j'||ev.key==='ArrowDown'){{ev.preventDefault();step(1)}}if(ev.key==='k'||ev.key==='ArrowUp'){{ev.preventDefault();step(-1)}}}};
document.addEventListener('keydown',keys);
frame.addEventListener('load',()=>{{try{{frame.contentDocument.addEventListener('keydown',keys)}}catch(_){{}}}});
draw();
const start=location.hash.slice(1)||store.get('rv{sprint}');pick(P.some(p=>p.id===start)?start:(P[0]||{{}}).id);
</script></body></html>"""
