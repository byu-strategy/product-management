"""The student's sprint report (the "dossier"): one self-contained HTML page per student.

Called by sprint_feedback.py; not run on its own. One render, two copies: the student copy, and
Scott's copy, which adds a closed yellow "Instructor only" drawer at the top and, inside the score
drawers, the grader's reasons, the demo checks, the Loom stills and the transcript. Everything
else is identical, so what Scott reviews is what the student reads.

Layout (approved 2026-10-14, revised 2026-10-15 and 2026-10-29): a sticky contents list on the left and open
sections: Summary (score, profile total, the Claude Code coach card, the clickable tree-ring chart), Score (four
rows, each with one Evidence drawer, then Point deductions with a Dispute link per item into the Strategy app, then
Questions or disputes), Next steps, Growth (with the closed "Seen this sprint, not yet in your profile" drawer),
Appendix A: How grading works, Appendix B: Concept list. Every section is an h2 styled alike; its parts are h3.sub, nested
under it in the contents list (2026-10-29). Scott's copy adds Instructor notes first. Colors are the Strategy app's BYU tokens. Detail
(evidence, reasons, Loom stills) stays in <details>. Inline CSS and SVG, one small script that
highlights the current section, images embedded; printing hides the contents list.

Student-facing text here follows the course's feedback rules: second person, plain, literal, no
em dashes, and it never mentions lateness or how evidence was gathered. The September survey appears
only as the profile's starting center (chart legend, Methodology), never tied to difficulty.
"""
import base64, html, io, json, math, os, re, datetime as dt
from pathlib import Path

e = html.escape
HERE = Path(__file__).resolve().parent
CONCEPTS = HERE / "grading" / "concepts"

# Flat-top hexagon, same positions as the course's builder profile charts.
AXES = ["Discovery", "Design", "Launch and Learn", "AI Systems", "Application Architecture", "Agentic Workflow"]
ANGLES = [-60, 0, 60, 120, 180, 240]
import sys
sys.path.insert(0, str(HERE / "grading"))
from builder_growth import PRACTICE, BREADTH_SHARE, LEVEL_SHARE, depth_points  # one copy of the weights
LEVELS = {1: "Followed", 2: "Directed", 3: "Decided", 4: "Delivered"}
LEVEL_TEXT = {  # from depth-levels.md, in the student's terms
    1: "work on the axis follows a template, a tutorial, or the agent's defaults",
    2: "you said specifically what to build and checked that it worked",
    3: "you challenged what the agent or the template proposed, weighed the options, and chose one with a stated reason, or found a problem yourself and fixed it with a judgment about the product",
    4: "people outside your team use it, and you changed the work because of what they did or said"}
# BYU navy tints, light at the center to dark at the newest ring; a sprint keeps its color in every report.
# Colors follow the Strategy app's tokens (website/src/app/globals.css): navy #002E5D, royal #003DA5 (2026-10-29).
SPRINT_COLORS = {1: "#A9BFDA", 2: "#7C9CC4", 3: "#5A7FAE", 4: "#3D6596", 5: "#244C7E", 6: "#0F3766"}
CORE_COLOR = "#DCE6F2"  # the starting core: the lightest step of the same navy ramp
# The midterm ring (2026-10-29): outside the sprint rings, in a hue off the navy ramp so it reads as an exam.
EXAM_COLOR = {"midterm": "#C9A54C"}
EXAM_LABEL = {"midterm": "Midterm"}
NAVY, ROYAL = "#002E5D", "#003DA5"
# Where each deduction can be disputed: the Strategy app, no sign-in (grade disputes, 2026-10-29).
DISPUTE_BASE = "https://strategy.byu.edu/app/dispute/"
# Feedback on the report itself (Scott, 2026-10-29): posted from the report to the Strategy app with the same
# secret link as disputes, so no sign-in and no new page. REPORT_API overrides the host for a local test.
FEEDBACK_API = os.environ.get("REPORT_API", "https://strategy.byu.edu") + "/api/report-feedback"
# Disputes from inside the report: a drawer under each deduction posts here (Scott, 2026-10-29). The Dispute link
# to the app's dispute page stays underneath as the fallback when the report's script cannot run.
DISPUTE_API = os.environ.get("REPORT_API", "https://strategy.byu.edu") + "/api/report-dispute"
# Concepts seen but not counted, grouped by what would let them count. `unreadable` is our limit, not the
# student's, so it goes to Scott's notes only.
NOT_YET = {
    "unproven": ("Shown, not proven working",
                 "commit the output of a test run (or turn on CI), or show it working in your demo, so Professor Murff can see it ran."),
    "tool_not_product": ("Built with a tool, not in your product",
                         "put the logic in your own product code, where your code decides what happens."),
    "after_due": ("Done after the due date", None),
    "not_shared": ("Not shared with Professor Murff",
                   "share the repo with sdmurff, or the file with aifoundry.byu@gmail.com, or list it in your README."),
    "described_only": ("Described, with nothing to check",
                       "commit the file, or link it from your README, so Professor Murff can open it."),
    "course_given": ("Supplied by the course or a template",
                     "change it or build on it yourself; what the course gave you does not count on its own."),
    "before_course": ("Dated before the course began",
                      "new work on it during a sprint counts; work that existed before Sep 2 does not."),
}
SCALE = {1: "something you already knew how to do", 2: "mostly known, a few small gaps",
         3: "something new to learn, with a clear path", 4: "a lot to learn, and the path was not clear",
         5: "unclear whether it was possible at all"}
LABELS = {"plan": "Plan", "shipped": "Output", "review": "Report and retro", "demo": "Demo"}
RUBRIC = {
    "plan": "The Plan is scored for completion: a plan with all four fields (Goal, Why this, Done looks "
            "like, Predicted difficulty) earns 10.",
    "shipped": "Output is what you finished this sprint, judged against your plan as it stood at the end of "
               "the sprint and against how hard the work was. It counts when someone can check it: in a "
               "shared repo, at a link, or working in your demo. An ambitious goal that you nearly reach, "
               "and account for in your retro, can earn full marks.",
    "review": "Your /sprint-review report and your retro. Full marks need every retro prompt answered and a "
              "response, in any answer, to something specific the report found. Each prompt left unanswered "
              "costs 1 point, no specific response costs 2, and an empty retro earns at most half.",
    "demo": "Your work, working, with real content, on Loom, as the course's \"What your demo shows\" table describes. Aim for 2 to 3 minutes. {LENGTH}",
}
CHECK_LABELS = {"on_screen": "On screen", "working": "Working", "real_content": "Real content",
                "reachable": "Reachable", "matches_plan": "Matches the plan", "off_demo": "Off the demo",
                "readable": "Readable"}
# The one install recipe, the same text as the builder-template README's "Update your course skills".
SKILLS_PASTE = ("Update my course skills from the class template. Clone https://github.com/byu-strategy/builder-template "
                "(main branch) into a temporary folder outside this repo with `git clone --depth 1`. For each folder in "
                "the template's `.claude/skills`, replace the folder with the same name in this repo's `.claude/skills` "
                "with the template's copy, and add any that are missing. Do not change any other skill or any other file "
                "in this repo. Delete the temporary folder, then commit only `.claude/skills` with the message "
                "\"Update course skills\" and push. Then tell me to start a new Claude Code session so the updated skills load.")
README_PASTE = ("## Where the work lives\n\n- **Repos:** [owner/repo-name], [shared with sdmurff, or not shared]\n"
                "- **Live:** [the URL of the app, page, store listing, or file]\n"
                "- **Docs:** [links to Google Docs, Figma files, decks]")
TURNIN = """<table class=turnin>
<tr><th>Deliverable</th><th>Where it lives</th><th>How you turn it in</th><th>When</th><th>Points</th></tr>
<tr><td><b>Plan</b></td><td><code>sprints/sprint-N-plan.md</code></td><td>Commit it, and paste its GitHub link into <b>Sprint N Plan</b> on Canvas. To change it later, run <code>/sprint-plan</code> again; no resubmitting</td><td>First Wednesday, 11:59 PM</td><td>10</td></tr>
<tr><td><b>Output</b></td><td>What you finished, in any form: in your course repo, another repo, a link, or your demo</td><td>Nothing separate: list every place it lives under <b>Where the work lives</b> in your README</td><td>{DUE}</td><td>{OUT}</td></tr>
<tr><td><b>Review</b></td><td><code>sprints/sprint-N-review.md</code>: the <code>/sprint-review</code> report, with your retro at the bottom</td><td>Commit it, and paste its GitHub link into <b>Sprint N Wrap-up</b> on Canvas</td><td>{DUE}</td><td>{REV}</td></tr>
<tr><td><b>Demo</b></td><td>Loom, {DEMO_LEN}</td><td>Paste the Loom share link into <b>Sprint N Wrap-up</b> on Canvas</td><td>{DUE}</td><td>{DEM}</td></tr>
</table>"""



# "You might consider committing X" becomes "Commit X". Doubled consonants (committ, runn, plann)
# lose a letter; stems that need a silent e get it back; anything not a gerund is left alone.
SILENT_E = {"hav", "writ", "shar", "us", "sav", "mak", "mov", "giv", "tak", "includ", "chang", "stor", "compar",
            "scor", "hid", "rid", "describ", "nam", "updat", "creat", "remov", "replac", "continu", "argu", "valu", "measur",
            "reduc", "produc", "introduc", "prepar", "separat", "automat", "documen", "captur", "receiv",
            "declin", "defin", "combin", "explor", "rewrit", "retir", "merg", "issu", "schedul", "pric", "rais",
            "us", "clos", "notic", "decid", "locat", "translat", "validat", "generat", "estimat", "calculat",
            "choos", "los", "chas", "rul", "typ", "guid", "provid", "requir", "secur", "configur", "compil",
            "manag", "engag", "packag", "leverag", "encourag", "arrang", "challeng", "promot", "quot", "vot",
            "not", "invit", "involv", "solv", "resolv", "serv", "observ", "reserv", "achiev", "believ", "retriev",
            "advertis", "organiz", "summariz", "priorit", "prioritiz", "optimiz", "personaliz", "recogniz",
            "analyz", "authoriz", "emphasiz", "minimiz", "maximiz", "standardiz", "finaliz", "pars", "fus",
            "abus", "excus", "paus", "caus", "rais", "prais", "purchas", "releas", "increas", "decreas", "eras",
            "phras", "bas", "cas", "us", "examin", "determin", "outlin", "pipelin", "timelin", "deadlin"}
NOT_GERUND = {"anything", "nothing", "something", "everything", "morning", "evening", "string", "thing", "ring",
              "king", "spring", "during", "bring", "sing", "wing", "ceiling"}


def imperative(word):
    w = word.lower()
    if w in NOT_GERUND or not w.endswith("ing") or len(w) < 5:
        return word
    stem = w[:-3]
    if stem in SILENT_E:
        return stem + "e"
    if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "lszdf" + "aeiou":
        return stem[:-1]
    return stem

def fmt(x):
    return f"{round(float(x), 1):g}"


def practice_max(axis):
    return PRACTICE.get(axis, 50.0)


PASSAGES = HERE / "grading" / "book-passages.json"  # book_passages.py writes it
BOOK = "https://byu-strategy.github.io/product-management/"


def demo_length(sprint):
    """The published demo length rule for this sprint (00-assessments.qmd, "Demo length", 2026-10-16)."""
    if sprint == 1:
        return "A demo up to about two minutes long lost no points."
    if sprint == 2:
        return "Demo length was not scored this sprint."
    line = "4:30" if sprint == 6 else "3:30"
    return f"A demo up to {line} loses no points; each started 30 seconds past {line} costs 1 point."


def book_refs(cid):
    """The book pages that teach a concept, one per page (the page highlights every passage on it):
    [(chapter label, section title, url)], at most three."""
    global _P
    try:
        _P
    except NameError:
        _P = json.loads(PASSAGES.read_text()) if PASSAGES.exists() else {}
    out, pages = [], set()
    for x in _P.get(cid or "", []):
        if x["page"] in pages or len(pages) == 3:
            continue
        pages.add(x["page"])
        m = re.match(r"0*(\d+)([a-z]?)-", x["page"])
        href = f'{BOOK}{x["page"]}?c={cid}' + (f'#{x["anchor"]}' if x.get("anchor") else "")
        label = f"Ch {m.group(1)}{m.group(2)}" if m and int(m.group(1)) < 90 else "Appendix"
        out.append((label, x.get("section", ""), href))
    return out


def book_chips(cid):
    """Small chapter chips that open the passage; the section title shows on hover."""
    return "".join(f'<a class=bkc href="{e(h)}" target=_blank rel=noopener title="{e(sec)}">{e(ch)}</a>'
                   for ch, sec, h in book_refs(cid))


def book_name(cid, name):
    """The concept's name, linked to its first passage, followed by its chapter chips."""
    refs = book_refs(cid)
    if not refs:
        return e(name)
    return f'<a class=bkn href="{e(refs[0][2])}" target=_blank rel=noopener>{e(name)}</a>{book_chips(cid)}'


def load_concepts():
    """Every concept on every axis, in list order. Tolerates lists without knowledge_only."""
    out = {}
    for f in sorted(CONCEPTS.glob("*.json")):
        d = json.loads(f.read_text())
        out[d["axis"]] = {"items": d.get("items") or {}, "concepts": d.get("concepts") or []}
    return out


# ---------------------------------------------------------------- the sprint coach prompt
# The Summary card copies one prompt per student. It carries the report's facts, so the
# sprint-coach skill in the student's repo can go over the report without the report open.

COURSE_RULES = BOOK + "00-assessments.html#sprints"
TEMPLATE_REPO = "https://github.com/byu-strategy/builder-template"


def plain(h):
    """Report HTML (a next step's title or detail) as plain text."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", h or "")).split())


def first_sentence(t):
    t = " ".join((t or "").split())
    m = re.match(r"(.+?[.!?])(?=\s+[A-Z(]|$)", t)
    return m.group(1) if m else t


# A reason that starts with a name or an acronym keeps its capital after the colon.
PROPER_START = r"(?:Claude|GitHub|Canvas|Loom|Supabase|Vercel|Slack|Google|Resend|Stripe|Granola|Procore|I)\b|[A-Z]{2}"


def coach_gaps(G, k=4):
    """Two to four concepts worth learning next, each with a book passage: first the ones the
    student worked near but that did not count yet, then unshown concepts in the same item as
    something this sprint showed, taken in turn from each item. [(id, name, url, why)]"""
    if not G:
        return []
    CL = load_concepts()
    by_id = {c["id"]: c for d in CL.values() for c in d["concepts"]}
    shown = set(G.get("concepts_shown") or [])
    out, seen = [], set()

    def add(cid, why):
        c = by_id.get(cid) or {}
        refs = book_refs(cid)
        if not cid or cid in seen or cid in shown or not refs:
            return
        seen.add(cid)
        out.append((cid, c.get("name") or cid, refs[0][2], why))

    for x in G.get("not_counted") or []:
        why = str(x.get("why") or "").strip()
        add(x.get("concept"), "Work on this did not count yet" + (f": {why if re.match(PROPER_START, why) else why[:1].lower() + why[1:]}" if why else "."))
    queues, items_seen = [], set()
    for m in sorted(G.get("new") or [], key=lambda m: -float(m.get("points") or 0)):
        ax, item = m.get("axis"), m.get("item")
        if (ax, item) in items_seen or ax not in CL:
            continue
        items_seen.add((ax, item))
        label = CL[ax]["items"].get(item) or ax
        why = f'It sits next to {m.get("concept")} {m.get("name")}, which you showed this sprint, under {label}.'
        queues.append([(c["id"], why) for c in CL[ax]["concepts"] if c.get("item") == item])
    while len(out) < k and any(queues):
        for q in queues:
            while q and len(out) < k:
                before = len(out)
                add(*q.pop(0))
                if len(out) > before:
                    break
    if len(out) < 2:  # little shown this sprint: the next concepts on the axis worked hardest
        pts = (G.get("rings") or [{}])[-1].get("points") or {}
        for ax in sorted(pts, key=lambda a: -float(pts[a] or 0)):
            for c in (CL.get(ax) or {}).get("concepts", []):
                if len(out) >= 2:
                    break
                add(c["id"], f"A next concept on {ax}, where most of this sprint's work was.")
    return out[:k]


def coach_prompt(sprint, total, total_max, score_lines, steps, G):
    """The prompt a student pastes into Claude Code: their voice, plain text, the report's facts."""
    nxt = sprint + 1
    L = [f"Here is my Sprint {sprint} report from MSB 341 (Product Management). Go over it with me "
         f"and help me plan Sprint {nxt}.",
         "",
         "First, update my course skills: if .claude/skills/refresh-skills/refresh.py exists, run it with "
         "python3; if it does not, update them the way the course template's README says "
         f"({TEMPLATE_REPO}#update-your-course-skills). Then read .claude/skills/sprint-coach/SKILL.md from "
         "disk and follow it in this session.",
         "",
         f"SCORE: {fmt(total)} of {total_max}"]
    L += [f"- {name}: {s} of {mx}. {reason}".rstrip() for name, s, mx, reason in score_lines]
    L += ["", "NEXT STEPS, in the report's order"]
    if steps:
        for i, (_k, t, d, code) in enumerate(steps, 1):
            L.append(f"{i}. {plain(t)}" + (f" {plain(d)}" if d else ""))
            if code:
                L += ["   Text the report gives to paste:"] + [f"   | {x}" for x in code.splitlines()]
    else:
        L.append("- None. The repo and README are set.")
    L += ["", "GROWTH THIS SPRINT (depth levels: 1 Followed, 2 Directed, 3 Decided, 4 Delivered)"]
    if G:
        depth = {d["axis"]: d["level"] for d in G.get("depth") or [] if d.get("level")}
        best = G.get("depth_best") or {}
        new = {}
        for m in G.get("new") or []:
            new.setdefault(m["axis"], []).append(f'{m["concept"]} {m.get("name", "")}'.strip())
        nothing = []
        for ax in AXES:
            b = int(best.get(ax) or 0)
            if ax in depth or ax in new:
                lv = depth.get(ax)
                line = f"- {ax}: " + (f"depth level {lv}, {LEVELS[lv]}" if lv else "no depth level this sprint")
                if b and b != lv:
                    line += f" (highest so far: level {b}, {LEVELS[b]})"
                line += ". New concepts: " + ("; ".join(new[ax]) if ax in new else "none") + "."
                L.append(line)
            elif b:
                L.append(f"- {ax}: nothing new this sprint (highest so far: level {b}, {LEVELS[b]}).")
            else:
                nothing.append(ax)
        if nothing:
            L.append("- Nothing yet: " + ", ".join(nothing) + ".")
    else:
        L.append("- My builder profile is still being prepared, so the report shows no growth yet.")
    gaps = coach_gaps(G)
    L += ["", "GAPS WORTH LEARNING (each opens the course book at its passage)"]
    L += [f"- {cid} {name}: {url}  {why}" for cid, name, url, why in gaps] or ["- None listed in this report."]
    L += ["", "POINTERS",
          f"- Course rules for sprints: {COURSE_RULES}",
          f"- My Sprint {sprint} review and retro: sprints/sprint-{sprint}-review.md",
          f"- My Sprint {nxt} plan: sprints/sprint-{nxt}-plan.md"]
    return "\n".join(L)


# The Claude mark used on the course book's Learn buttons (_extensions/learn/learn.js).
CLAUDE_ICON = ('<svg viewBox="0 0 13 7" width="20" height="11" shape-rendering="crispEdges" aria-hidden="true"><g fill="#D97757">'
               '<rect x="2" y="0" width="9" height="1"/><rect x="2" y="1" width="9" height="1"/><rect x="2" y="2" width="1" height="1"/>'
               '<rect x="4" y="2" width="5" height="1"/><rect x="10" y="2" width="1" height="1"/><rect x="0" y="3" width="13" height="1"/>'
               '<rect x="2" y="4" width="9" height="1"/><rect x="2" y="5" width="9" height="1"/><rect x="2" y="6" width="1" height="1"/>'
               '<rect x="4" y="6" width="1" height="1"/><rect x="8" y="6" width="1" height="1"/><rect x="10" y="6" width="1" height="1"/></g>'
               '<rect x="3" y="2" width="1" height="1" fill="#1F1F1F"/><rect x="9" y="2" width="1" height="1" fill="#1F1F1F"/></svg>')

# Copy prompt: the clipboard API, then the older copy command, then the visible box with the text selected.
COACH_JS = """
document.querySelectorAll('form.rfb').forEach(f=>{
  // A rating saves the moment it is picked (Scott, 2026-10-29); the comment goes with the button. Each save sends both,
  // so one answer per report always holds the latest rating and comment.
  const btn=f.querySelector('.rfbsend'),st=f.querySelector('.rfbst');
  const say=(t,c)=>{st.textContent=t;st.className='rfbst'+(c?' '+c:'')};
  let sent=false;
  const send=(what)=>{
    const body=new URLSearchParams(new FormData(f));body.set('js','1');
    if(what==='comment'){btn.disabled=true;btn.textContent='Sending...'}
    say(what==='rating'?'Saving...':'');
    return fetch(f.action,{method:'POST',body,mode:'cors',credentials:'omit'}).then(r=>r.json()).then(j=>{
      btn.disabled=false;btn.textContent=f.text.value.trim()&&what==='comment'||sent?'Update comment':'Send comment';
      if(!j.ok){say(j.error||'It could not be saved. Try again.','bad');return}
      if(what==='comment'&&f.text.value.trim())sent=true;
      say(what==='rating'?'Rating saved. Add a comment if you like.':'Sent. Thank you.','ok');
    }).catch(()=>{btn.disabled=false;btn.textContent='Send comment';
      if(what==='comment'){say('Opening a new tab to send it.');HTMLFormElement.prototype.submit.call(f)}
      else say('The rating could not be saved from here. Use Send comment.','bad')});
  };
  f.querySelectorAll('input[name=rating]').forEach(x=>x.addEventListener('change',()=>send('rating')));
  f.addEventListener('submit',ev=>{if(!f.rating.value)return;ev.preventDefault();send('comment')});
});
document.querySelectorAll('.ccbtn').forEach(b=>{
  const ta=document.getElementById(b.dataset.copy),lab=b.querySelector('.cclabel'),box=ta.closest('details'),note=b.closest('.coach').querySelector('.ccnote');
  const reset=()=>{lab.textContent='Copy prompt';b.classList.remove('ok','bad')};
  const done=()=>{lab.textContent='Copied';b.classList.add('ok');b.classList.remove('bad');note.textContent='';clearTimeout(b._t);b._t=setTimeout(reset,2000)};
  const fail=()=>{box.open=true;ta.focus();ta.select();b.classList.add('bad');
    note.textContent='Copying did not work here. The prompt is selected below: press '+(/Mac|iPhone|iPad/.test(navigator.platform)?'Cmd+C':'Ctrl+C')+' to copy it.'};
  const legacy=()=>{try{const t=document.createElement('textarea');t.value=ta.value;t.setAttribute('readonly','');t.style.position='fixed';t.style.opacity='0';
    document.body.appendChild(t);t.select();const ok=document.execCommand('copy');t.remove();return ok}catch(e){return false}};
  b.addEventListener('click',()=>{
    const p=(navigator.clipboard&&window.isSecureContext)?navigator.clipboard.writeText(ta.value):Promise.reject();
    p.then(done,()=>legacy()?done():fail());
  });
});
"""


# ---------------------------------------------------------------- small helpers

def img_b64(path, w=560):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
    except Exception:
        return None
    im.thumbnail((w, w))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=68)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def short_date(s):
    """'2026-10-08' or an ISO time -> 'Oct 8'; anything else passes through."""
    try:
        d = dt.date.fromisoformat(str(s)[:10])
        return f"{d:%b} {d.day}"
    except ValueError:
        return str(s or "")


def when_key(m):
    """Sort key for a concept's date: ISO dates, or 'Oct 12' / 'Oct 10 to 14' (the last date)."""
    w = str(m.get("when") or "")
    try:
        return dt.date.fromisoformat(w[:10])
    except ValueError:
        pass
    months = {k: i for i, k in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
    last, mon = None, None
    for tok in re.findall(r"[A-Za-z]+|\d+", w):
        if tok[:3].lower() in months:
            mon = months[tok[:3].lower()]
        elif tok.isdigit() and mon and int(tok) <= 31:
            last = dt.date(2026, mon, int(tok))
    return last or dt.date(2000, 1, 1)


def ref_link(repo, ref):
    """A commit sha, a file path, a URL, or a Loom time, as a link where one exists."""
    ref = str(ref or "").strip()
    if re.fullmatch(r"[0-9a-f]{7,40}", ref):
        return f'<a href="https://github.com/{e(repo)}/commit/{e(ref)}">{e(ref[:7])}</a>'
    if ref.startswith("http"):
        return f'<a href="{e(ref)}">{e(re.sub(r"^https?://", "", ref)[:48])}</a>'
    if re.fullmatch(r"(Loom )?\d+:\d\d.*", ref):
        return e(ref if ref.startswith("Loom") else "Loom " + ref)
    if ref and repo:
        return f'<a href="https://github.com/{e(repo)}/blob/HEAD/{e(ref)}">{e(ref)}</a>'
    return e(ref)


def gfm_lists(src):
    """Read lists the way GitHub does (two-space nesting, a list right after a paragraph line)."""
    out, prev, fence = [], "", False
    for line in (src or "").splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence:
            m = re.match(r"^( +)([-*+]|\d+\.)\s", line)
            if m:
                line = " " * (len(m.group(1)) * 2) + line.lstrip()
            is_item = re.match(r"^\s*([-*+]|\d+\.)\s", line)
            prev_item = re.match(r"^\s*([-*+]|\d+\.)\s", prev)
            if is_item and prev.strip() and not prev_item and not prev.lstrip().startswith(("|", "#", ">")):
                out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def md(src, repo):
    """The student's own markdown file, rendered; relative links point at the repo on GitHub."""
    import markdown
    src = gfm_lists(src)
    src = re.sub(r"(?<![(<\"\]`/])\b(https?://[^\s)<>\]`|]+?)([.,;:]?)(?=\s|$|\)|\|)", r"<\1>\2", src or "", flags=re.M)
    h = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists", "nl2br"])
    h = re.sub(r"<script.*?</script>", "", h, flags=re.S | re.I)
    h = re.sub(r'<img[^>]*?src="([^"]+)"[^>]*?(?:alt="([^"]*)")?[^>]*>',
               lambda m: f'<a href="{m.group(1)}">[image{": " + m.group(2) if m.group(2) else ""}]</a>', h)
    return re.sub(r'href="(?!https?:|#|mailto:)([^"]+)"',
                  lambda m: f'href="https://github.com/{repo}/blob/HEAD/{m.group(1).lstrip("./")}"', h)


def parse_report(t):
    """The few numbers the /sprint-review report states about itself."""
    t = t or ""
    g = lambda pat: (re.search(pat, t) or [None, None])[1]
    wl = re.findall(r"\d{4}-\d\d-\d\d", g(r"\*\*Window:\*\*([^\n]*)") or "")
    return {"window": (wl[0], wl[-1]) if len(wl) >= 2 else None,
            "sessions": g(r"\*\*Sessions reviewed:\*\*\s*(\d+)"),
            "not_visible": g(r"\*\*Not visible to this review:\*\*\s*(.+)")}


def readme_replay(p):
    """The README's 'Where the work lives' entries, each place with what happened when it was
    opened, plus places found in the sprint that the README does not list."""
    readme = p.get("readme") or ""
    if isinstance(readme, dict):
        readme = readme.get("text") or ""
    m = re.search(r"## Where the work lives\n(.*?)(?=\n## |\Z)", readme, re.S)
    section = m.group(1) if m else ""
    checks = {l["url"].rstrip("/"): l for l in p.get("link_checks") or []}
    drive = {d.get("file_id"): d for d in p.get("drive_files") or []}
    course = (p.get("repo") or "").replace("https://github.com/", "").strip("/").lower()
    others = {o["repo"].replace("https://github.com/", "").strip("/").lower(): o for o in p.get("other_repos") or []}
    unshared = {u.lower() for u in (p.get("facts") or {}).get("repos_named_but_not_shared") or []}
    user = (p.get("repo") or "").split("/")[3] if (p.get("repo") or "").count("/") >= 3 else ""

    def status(kind, key):
        if kind == "url":
            gm = re.search(r"/d/([\w-]{20,})", key)
            if "google.com" in key and gm:
                d = drive.get(gm.group(1))
                return ("ok", "opened") if d and d.get("ok") else ("bad", "could not open: share it with aifoundry.byu@gmail.com")
            if re.search(r"localhost|127\.0\.0\.1", key):
                return ("na", "runs only on your computer, so it could not be opened")
            c = checks.get(key.rstrip("/"))
            if not c:
                return ("na", "listed")
            return ("ok", "opened") if (c.get("status") or 999) < 400 else ("bad", "did not open")
        r = key.lower()
        if r == course:
            return ("ok", "your course repo")
        if r in others:
            return ("ok", "shared and read")
        if r in unshared:
            return ("bad", "not shared with sdmurff, so it could not be read")
        return ("na", "listed")

    def places(text):
        urls = [u.rstrip(").,") for u in re.findall(r"https?://[^\s)\]>|`]+", text)]
        repos = {u.lower() for u in re.findall(r"github\.com/([\w.-]+/[\w.-]+)", text)}
        if user:
            repos |= {u.lower().rstrip(".") for u in re.findall(rf"(?<![\w/.-])({re.escape(user)}/[\w.-]+)", text, re.I)}
        urls = [u for u in urls if not re.match(r"https?://github\.com/", u)]
        return [("repo", r) for r in sorted(repos)] + [("url", u) for u in dict.fromkeys(urls)]

    listed, seen = [], set()
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith(("-", "|")) or set(line) <= set("|-: "):
            continue
        lm = re.match(r"[-|]\s*\*\*([^*]+?):?\*\*:?\s*(.*)", line) or re.match(r"\|\s*([^|]+?)\s*\|\s*(.*)", line)
        if not lm or lm.group(1).strip().lower() in ("what",):
            continue
        label, rest = lm.group(1).strip(), lm.group(2).strip(" |")
        found = places(rest)
        seen |= {v.lower().rstrip("/") for _, v in found}
        plain = re.sub(r"https?://\S+|\[|\]|\(|\)|`|\*", "", rest).strip(" ,;:|")
        listed.append({"label": label, "places": [(k, v) + status(k, v) for k, v in found],
                       "note": plain if not found else ""})
    extra = []
    for r in sorted(set(others) | unshared):
        if r != course and r not in seen:
            extra.append(("repo", r) + status("repo", r))
    for d in p.get("drive_files") or []:
        if not any((d.get("file_id") or "~") in x for x in seen):
            extra.append(("url", d.get("url") or d.get("file_id")) + status("url", d.get("url") or ""))
    for u in checks:
        if u.lower() not in seen and not re.search(r"localhost|google\.com", u):
            extra.append(("url", u) + status("url", u))
    return {"has_section": bool(m), "listed": listed, "extra": extra}


def show_place(kind, v):
    if kind == "repo":
        return f'<a href="https://github.com/{e(v)}">{e(v)}</a>'
    short = re.sub(r"^https?://", "", v).rstrip("/")
    return f'<a href="{e(v)}">{e(short if len(short) < 60 else short[:57] + "...")}</a>'


# ---------------------------------------------------------------- the pictures

def profile_svg(G):
    """The builder profile: six spokes, 0 to 100 each (100 is a full-stack product builder). Practice rings
    stack outward from the center, one per sprint in that sprint's color. Knowledge rings from the
    exams will stack outside them; none exist yet, so nothing is drawn for them. With no growth
    file, the empty hexagon."""
    CX, CY, R = 270, 200, 135

    def pt(i, v, rr=R):
        a = math.radians(ANGLES[i])
        r = rr * max(0.0, min(v, 100.0)) / 100
        return CX + r * math.cos(a), CY + r * math.sin(a)

    def poly(vals):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, vals[i]) for i in range(6)))

    out = ['<svg viewBox="0 30 540 360" width="100%" role="img" aria-label="Builder profile: six axes, 0 to 100 each">']
    # Soft bands behind the grid, as on the Strategy app's consultant diamond.
    out.append(f'<polygon points="{poly([100] * 6)}" fill="#EEF3F9"/><polygon points="{poly([87.5] * 6)}" fill="#F6F8FB"/>'
               f'<polygon points="{poly([62.5] * 6)}" fill="#fff"/>')
    for lvl in (25, 50, 75, 100):
        out.append(f'<polygon points="{poly([lvl] * 6)}" fill="none" stroke="{"#CCCCCC" if lvl == 100 else "#E5E5E5"}" '
                   f'stroke-width="{1.3 if lvl == 100 else .8}"/>')
    core = ((G or {}).get("start") or {}).get("points") or {}
    totals = [float(core.get(AXES[i], 0)) for i in range(6)]
    core_vals = list(totals)
    layers = []
    for rg in (G or {}).get("rings") or []:
        pts = rg.get("points") or {}
        if not any(pts.values()):
            layers.append((rg["sprint"], None))
            continue
        totals = [totals[i] + float(pts.get(AXES[i], 0)) for i in range(6)]
        layers.append((rg["sprint"], list(totals)))
    exam_layers = []
    for ex in (G or {}).get("exams") or []:
        pts = ex.get("points") or {}
        totals = [totals[i] + float(pts.get(AXES[i], 0)) for i in range(6)]
        exam_layers.append((ex, list(totals)))
    for ex, vals in reversed(exam_layers):
        per = {a: f'{v["correct"]} of {v["of"]} right, +{fmt(round(float(v["points"]), 1))}' for a, v in (ex.get("axes") or {}).items()}
        out.append(f'<polygon class=exam data-exam="{e(ex["exam"])}" data-per="{e(json.dumps(per))}" points="{poly(vals)}" '
                   f'fill="{EXAM_COLOR.get(ex["exam"], ROYAL)}" stroke="#fff" stroke-width=".8" stroke-linejoin="round">'
                   f'<title>{EXAM_LABEL.get(ex["exam"], ex["exam"])}</title></polygon>')
    for s, vals in reversed(layers):  # outermost first, so each inner ring sits on top
        if vals:
            out.append(f'<polygon data-s="{s}" points="{poly(vals)}" fill="{SPRINT_COLORS.get(s, NAVY)}" stroke="#fff" '
                       f'stroke-width=".8" stroke-linejoin="round"><title>Through Sprint {s}</title></polygon>')
    if any(core_vals):  # the survey center sits innermost, on top of the rings
        out.append(f'<polygon class="core" points="{poly(core_vals)}" fill="{CORE_COLOR}" stroke="#fff" stroke-width=".8" '
                   f'stroke-linejoin="round"><title>Your September survey</title></polygon>')
    full = ((G or {}).get("start") or {}).get("survey_full") or {}
    if exam_layers and any(abs(float(full.get(a, 0)) - float(core.get(a, 0))) > .01 for a in AXES):
        # The full September self-rating, where an exam has since measured part of it.
        out.append(f'<polygon class=sept points="{poly([float(full.get(AXES[i], 0)) for i in range(6)])}" fill="none" '
                   f'stroke="{NAVY}" stroke-width="1.1" stroke-dasharray="3 3" opacity=".55"><title>Your September survey, in full</title></polygon>')
    if G and any(totals):  # a dot at every value, so a small value next to a zero still shows
        for i in range(6):
            if totals[i] > 0:
                x, y = pt(i, totals[i])
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{NAVY}" stroke="#fff" stroke-width="1"/>')
    for i, ax in enumerate(AXES):
        x, y = pt(i, 100)
        out.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="#CCCCCC" stroke-width=".7"/>')
        lx, ly = pt(i, 121)
        anchor = "start" if lx > CX + 5 else "end" if lx < CX - 5 else "middle"
        name = ax.replace("Application Architecture", "App Architecture")
        out.append(f'<text class=axl data-axis="{e(name)}" x="{lx:.1f}" y="{ly - 6:.1f}" text-anchor="{anchor}" font-size="12.5" '
                   f'font-weight="600" fill="{NAVY}">{e(name)}</text>')
        if G:
            out.append(f'<text x="{lx:.1f}" y="{ly + 10:.1f}" text-anchor="{anchor}" font-size="12.5" font-weight="700" '
                       f'fill="{ROYAL}">{round(totals[i])}</text>')
    out.append("</svg>")
    return "".join(out), [s for s, v in layers if v] + [ex["exam"] for ex, _v in exam_layers]


def commit_strip(days, by_day):
    """Commits per day across the sprint, one bar per day."""
    if not days:
        return ""
    W = 640
    colw = W / len(days)
    H, top = 60, 16
    mx = max(by_day.values() or [1]) or 1
    out = [f'<svg viewBox="0 0 {W} {top + H + 32}" width="100%" role="img" aria-label="Commits per day">']
    for i, d in enumerate(days):
        n = by_day.get(d.isoformat(), 0)
        cx = colw * i + colw / 2
        out.append(f'<g><title>{d:%a %b} {d.day}: {n} commit{"" if n == 1 else "s"}</title>')
        if n:
            h = max(2, H * n / mx)
            bw = min(16, colw * .6)
            out.append(f'<rect x="{cx - bw / 2:.1f}" y="{top + H - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{ROYAL}"/>'
                       f'<text x="{cx:.1f}" y="{top + H - h - 4:.1f}" text-anchor="middle" class="v">{n}</text>')
        label = f"{d:%b} {d.day}" if i == 0 or d.day == 1 else str(d.day)
        out.append(f'<text x="{cx:.1f}" y="{top + H + 14}" text-anchor="middle" class="ax">{label}</text>'
                   f'<text x="{cx:.1f}" y="{top + H + 27}" text-anchor="middle" class="ax2">{d:%a}</text></g>')
    out.append(f'<line x1="0" x2="{W}" y1="{top + H}" y2="{top + H}" stroke="#CCCCCC"/></svg>')
    return "".join(out)


# ---------------------------------------------------------------- drawers

def row(title, right, body, cls="", chips="", opened=False):
    return (f'<details class="q {cls}"{" open" if opened else ""}><summary><span class=qn>{title}{chips}</span><span class=qr>{right}</span></summary>'
            f'<div class=qb>{body}</div></details>')


def sub(title, right, body):
    return row(title, right, body, "s")


def big(title, right, body, cls=""):
    return (f'<details class="big {cls}"><summary><span class=bt>{title}</span><span class=br>{right}</span></summary>'
            f'<div class=bb>{body}</div></details>')


def evi(title, right, body):
    """One part inside a category's Evidence drawer: a subheading, not another drawer."""
    return f'<div class=evi><h4>{title}{f" <small>{right}</small>" if right else ""}</h4>{body}</div>'


def ev_drawer(parts):
    """A category's evidence, all in one drawer (2026-10-29: drawers inside drawers were hard to read)."""
    body = "".join(x for x in parts if x)
    n = body.count("<div class=evi>")
    return row("Evidence", f'{n} part{"s" * (n != 1)}', body, "ev") if n else ""


def not_yet(items, s_):
    """Concepts the work touched that could not count yet, grouped by what would let them count, closed by
    default (2026-10-29). Items we could not read are our limit, so they are left out here (Scott's notes)."""
    groups = {}
    for x in items:
        k = x.get("kind") or "other"
        if k != "unreadable":
            groups.setdefault(k, []).append(x)
    if not groups:
        return ""
    cap = lambda w: (w[:1].upper() + w[1:]).rstrip(".") + "." if w else ""
    body = ""
    for k in [k for k in NOT_YET if k in groups] + [k for k in groups if k not in NOT_YET]:
        title, fix = NOT_YET.get(k, ("Not counted yet", ""))
        lead = (f'<p class=fix><b>Nothing to do:</b> this counts toward Sprint {s_ + 1}, the sprint it was done in.</p>' if k == "after_due"
                else f'<p class=fix><b>To make it count:</b> {e(fix)}</p>' if fix else "")
        lis = "".join(f'<li><span class=nm>{e(x.get("name") or x.get("concept", ""))}</span>{book_chips(x.get("concept"))}'
                      f'<span class=wh>{e(x.get("what") or "")}</span>'
                      + (f'<span class=why>{e(cap(str(x.get("why") or "").strip()))}</span>' if k not in NOT_YET or k == "other" else "")
                      + '</li>' for x in groups[k])
        n = len(groups[k])
        body += (f'<div class="ncg{" later" if k == "after_due" else ""}"><div class=ngh><span>{title}</span>'
                 f'<small>{n} item{"s" * (n != 1)}</small></div>{lead}<ul>{lis}</ul></div>')
    total = sum(len(v) for v in groups.values())
    return (f'<details class=ncx id=notyet><summary><h3>Seen this sprint, not yet in your profile'
            f'<small>{total} item{"s" * (total != 1)}</small></h3></summary>'
            '<p class=nci>Concepts your work touched that could not be added to your builder profile yet. They do not '
            'affect your grade. Each group says what would let them count.</p>' + body + '</details>')


CAT_OF = {"shipped": "Output", "review": "Report and retro", "demo": "Demo", "plan": "Plan"}


def deductions_block(r, sprint, cats, dispute, outcomes, scott):
    """Every point lost, one row each, with its rule, how to earn it next time, and a Dispute link to the
    Strategy app (grade disputes, 2026-10-29). Scott's copy adds the grader's reason and the passage it rests on."""
    ds = [d for d in r.get("deductions") or [] if float(d.get("points") or 0) > 0]
    if not ds:
        return '<div class=deds id=deds><h3 class=sub><span>Point deductions</span><small>none</small></h3><p>No points deducted.</p></div>'
    published = rule_sources()
    order = {c: i for i, (c, _l, _m) in enumerate(cats)}
    ds.sort(key=lambda d: (order.get(d.get("category"), 9), d.get("id", "")))
    total = sum(float(d["points"]) for d in ds)
    outcomes = outcomes or {}
    rows_ = ""
    for d in ds:
        did = str(d.get("id", ""))
        oc = outcomes.get(did) or {}
        st = oc.get("status")
        if st in ("upheld", "changed"):
            ch = float(oc.get("points_changed") or 0)
            action = (f'<span class="dst ok">{"Restored" if ch > 0 else "Lowered"} {fmt(abs(ch))} point{"s" * (abs(ch) != 1)} on review</span>'
                      if ch else '<span class=dst>Reviewed, no change</span>')
        elif st == "denied":
            action = '<span class=dst>Kept after review</span>'
        elif st == "open":
            action = '<span class=dst>Disputed</span>'
        elif dispute and dispute.get("token"):
            action = (f'<a class=dbtn data-ded="{e(did)}" href="{DISPUTE_BASE}{e(dispute["token"])}#{e(did)}" target=_blank '
                      f'rel="noopener noreferrer" aria-expanded=false>Dispute</a>')
        else:
            action = ""
        src = published.get(d.get("rule_id"), "")
        inst = ""
        if scott:
            inst = (f'<div class=inote><b>Reason</b> <span class=instag>instructor only</span> <code>{e(str(d.get("rule_id", "")))}</code>'
                    f'<p>{e(d.get("reason") or "")}</p>'
                    + (f'<p class=qm>{e(d.get("excerpt_ref") or "")}</p><pre class=dex>{e(d["excerpt"])}</pre>' if d.get("excerpt") else "")
                    + "</div>")
        rows_ += (f'<div class=ded id=ded-{e(did)}><div class=dh><span class=dp>&minus;{fmt(float(d["points"]))}</span>'
                  f'<span class=dt>{e(d.get("what", ""))}<span class=dcat>{CAT_OF.get(d.get("category"), "")}</span></span>{action}</div>'
                  f'<div class=dx><p class=rule>Rubric: &ldquo;{e(RULE_TEXT.get(d.get("rule_id"), ""))}&rdquo;'
                  + (f' <span>({e(src)})</span>' if src else "") + '</p>'
                  + (f'<p class=fix><b>To earn it next time:</b> {e(d["fix"])}</p>' if d.get("fix") else "")
                  + f'</div>{dispute_form(did) if dispute and dispute.get("token") and not scott and not st else ""}{inst}</div>')
    n = len(ds)
    closes = (f' Disputes are open until {e(dispute["closes"])}.' if dispute and dispute.get("closes") else "")
    note = ('<p class=dnote>Think something is wrong? Use the Dispute button to explain. A review can raise or lower the score.'
            f'{closes}</p>' if dispute and dispute.get("token") else "")
    live = f' data-api="{DISPUTE_API}" data-token="{e(dispute["token"])}"' if dispute and dispute.get("token") and not scott else ""
    return (f'<div class=deds id=deds{live}><h3 class=sub><span>Point deductions</span>'
            f'<small>{fmt(total)} point{"s" * (total != 1)}, {n} item{"s" * (n != 1)}</small></h3>{note}{rows_}</div>')


def dispute_form(did):
    """The drawer the Dispute button opens under its deduction: why, then evidence, then Send. Hidden until the
    report's script turns the Dispute link into a toggle; without the script the link opens the dispute page."""
    i = e(did)
    return (f'<form class=dform data-ded="{i}" hidden novalidate>'
            f'<label class=dfl for=dw-{i}>Why are you disputing this?</label>'
            f'<textarea id=dw-{i} name=why rows=4 maxlength=4000 required '
            f'placeholder="For example: my retro answers this in the third paragraph."></textarea>'
            f'<div class=dfl>Evidence <span>optional</span></div>'
            f'<label class=dfs for=dl-{i}>Links, one per line</label>'
            f'<textarea id=dl-{i} name=links rows=2 placeholder="https://"></textarea>'
            f'<label class=dfs for=dn-{i}>Anything else</label>'
            f'<textarea id=dn-{i} name=notes rows=2></textarea>'
            f'<label class=dfs for=df-{i}>Screenshots or PDFs <span>up to 5, 10 MB each</span></label>'
            f'<input id=df-{i} type=file name=files multiple '
            f'accept="image/png,image/jpeg,image/gif,image/webp,application/pdf">'
            f'<input class=rfbhp name=website tabindex=-1 autocomplete=off aria-hidden=true>'
            f'<div class=dff><span class=dfst role=status aria-live=polite></span>'
            f'<button type=button class=dfcancel>Cancel</button><button type=submit class=rfbsend>Send dispute</button></div>'
            f'</form>')


# What a student reads for each rule: the rubric's wording, one sentence (rule IDs: grading/sprint-grader.md).
# Each deduction quotes the published sentence it rests on (Scott, 2026-10-29: a summary dropped
# "or summarized by /sprint-review" and cost a student 4 points). tests/test_report.py checks that
# every quote still appears in 00-assessments.qmd, so a rubric edit stops the build until it matches.
RULE_TEXT = {
    "out-real": "Something real and finished exists now that did not two weeks ago.",
    "out-checkable": "Professor Murff can check it, privately. It is in your course repo, in another repo shared with Professor Murff or summarized by /sprint-review, at a link, or shown working in your demo.",
    "out-ambitious": "An ambitious goal you partly reach and account for in your retro can still earn full marks.",
    "out-needs-yes": "For these goals, Output is graded on the asks you made and can show: who you asked, when, what you asked for, and what they said.",
    "rev-committed": "The review, committed: the /sprint-review report with your answers to its five retro questions at the bottom.",
    "rev-retro": "Each question left unanswered costs 1 point. An empty retro earns at most half.",
    "rev-s1-template": "The Sprint 1 retro answers its template: did you hit the goal, what happened, what changes next sprint.",
    "rev-five-questions": "Report committed, with your retro answering all five questions.",
    "demo-working": "2 to 3 minutes on Loom of your work, working, as described in What your demo shows, with real content.",
    "demo-length": "A demo up to 3:30 loses no points. From Sprint 3, each started 30 seconds past 3:30 costs 1 point (3:31 to 4:00 is minus 1, 4:01 to 4:30 minus 2, 4:31 to 5:00 minus 3).",
    "demo-not-loom": "A demo that is not a Loom scores 0.",
    "demo-unopenable": "A video he cannot open is not graded until it is shared.",
}

# Where each quote is published: Assessments page, section heading.
RULE_SRC = {
    "out-real": "Assessments, What you have to have",
    "out-checkable": "Assessments, What you have to have",
    "out-ambitious": "Assessments, Grading rubric",
    "out-needs-yes": "Assessments, Grading rubric",
    "rev-committed": "Assessments, What you have to have",
    "rev-retro": "Assessments, Grading rubric",
    "rev-s1-template": "Assessments, Sprint 1",
    "rev-five-questions": "Assessments, Grading rubric",
    "demo-working": "Assessments, Grading rubric",
    "demo-length": "Assessments, Grading rubric",
    "demo-not-loom": "Assessments, Grading rubric",
    "demo-unopenable": "Assessments, How every sprint works",
}
QUOTE_EXEMPT = {"rev-s1-template"}   # Sprint 1 only, graded before quotes; no single published sentence


def rule_sources():
    return RULE_SRC


def inst_sub(title, right, body):
    """A drawer only Scott's copy has, marked so it is never mistaken for student text."""
    return row(f'{title} <span class=instag>instructor only</span>', right, body, "s inst")


# ---------------------------------------------------------------- the page

def render(r, p, row_, sprint, cats, final, *, plan_row=None, growth=None, scott=False,
           fairness=(), skills_status="", flags_withheld=(), dispute=None, outcomes=None):
    """One student's report. `final(row, cat)` gives a category's score after overrides.
    `dispute` is {"token": ..., "closes": "Nov 5"} when deductions can be disputed in the Strategy app;
    `outcomes` is {deduction id: {"status", "points_changed"}} once disputes are resolved."""
    net = r["net_id"]
    repo = (p.get("repo") or "").replace("https://github.com/", "").strip("/")
    f = p.get("facts") or {}
    rep = parse_report((p.get("review") or {}).get("text"))
    loom = p.get("loom") or {}
    diff = r.get("difficulty") or {}
    G = growth

    # ---- score
    graded = [(c, label, mx) for c, label, mx in cats if c != "plan" or sprint == 1]
    review_total = sum(final(row_, c) for c, _, _ in graded)
    review_max = sum(mx for _, _, mx in graded)

    def how_scored(c):
        rub = RUBRIC[c].replace('{LENGTH}', demo_length(sprint))
        if sprint == 1:  # Sprint 1 took any video host; Loom became required in Sprint 2
            rub = rub.replace(', on Loom.', ', on any video host.')
        body = f"<p>{e(rub)}</p>"
        if c == "shipped":
            eff = (diff.get("effect_on_shipped") or "none").strip()
            m = re.match(r"raised by (\d+(?:\.\d+)?)", eff)
            if m:
                # When the work was scored easier than the student rated it, the raise came from how much they
                # took on and pushed through; saying "how hard the work was" beside "closer to a 3" contradicts.
                easier = (diff.get("assessed") is not None and diff.get("student_actual") is not None
                          and float(diff["assessed"]) < float(diff["student_actual"]))
                what = "How much you took on and pushed through" if easier else "How hard the work was"
                body += f"<p>{what} raised this score by {m.group(1)} point{'s' * (m.group(1) != '1')}.</p>"
        out = f'<div class=how><b>How it was scored.</b> {body.replace("<p>", "").replace("</p>", " ").strip()}</div>'
        if scott:  # inline, in the instructor color: no drawer for a short note
            out += (f'<div class=inote><b>Reasons</b> <span class=instag>instructor only</span>'
                    f'<p>{e((r.get("reasons") or {}).get(c, ""))}</p>')
            if c == "demo" and r.get("demo_checks"):
                out += "<table class=chk>" + "".join(
                    f"<tr><td class=k>{CHECK_LABELS.get(k, k)}</td><td>{e(str(v))}</td></tr>"
                    for k, v in r["demo_checks"].items()) + "</table>"
            out += "</div>"
        return out

    def output_evidence():
        out = ""
        nr = r.get("not_reviewed") or {}
        if nr.get("detail") or nr.get("summary"):
            out += evi("What could not be reviewed", "", f"<p>{e(nr.get('detail') or nr.get('summary'))}</p>")
        rr = readme_replay(p)
        if rr["has_section"]:
            rows_ = []
            for it in rr["listed"]:
                cells = ("".join(f'<div>{show_place(k, v)} <span class="st {c}">{e(msg)}</span></div>' for k, v, c, msg in it["places"])
                         or f'<div>{e(it["note"][:140])} <span class="st na">listed</span></div>')
                rows_.append(f"<tr><td class=k>{e(it['label'])}</td><td>{cells}</td></tr>")
            body = f"<table class=rm>{''.join(rows_)}</table>"
        else:
            body = '<p>Your README has no "Where the work lives" section.</p>'
        if rr["extra"]:
            body += ('<p class=qm>Found during your sprint, not listed in your README:</p>' +
                     "".join(f'<div>{show_place(k, v)} <span class="st {c}">{e(msg)}</span></div>' for k, v, c, msg in rr["extra"]))
        out += evi("Where your work lives", f'{len(rr["listed"])} listed' if rr["has_section"] else "not listed", body)
        files = [x for x in p.get("shipped_files") or [] if x.get("path")]
        for o in p.get("other_repos") or []:
            files += [dict(x, _repo=o["repo"].replace("https://github.com/", "").strip("/")) for x in o.get("shipped_files") or []]
        if files:
            trs = "".join(
                f'<tr><td><a href="https://github.com/{e(x.get("_repo") or repo)}/blob/{e(x.get("first_commit") or "HEAD")}/{e(x["path"])}">'
                f'{e(x["path"])}</a></td><td class=r>{e(x.get("status") or "")}</td></tr>' for x in files)
            out += evi("Files added or changed", f"{len(files)}", f"<div class=scroll><table class=axt>{trs}</table></div>")
        imgs = []
        for x in p.get("shipped_files") or []:
            src = img_b64(x["image"], 480) if x.get("image") and Path(x["image"]).exists() else None
            if src:
                imgs.append(f'<figure><img src="{src}" alt="{e(x["path"])}"><figcaption>{e(x["path"])}</figcaption></figure>')
        if imgs:
            out += evi("Images from your work", f"{len(imgs)}", f'<div class=frames>{"".join(imgs)}</div>')
        return out

    def review_evidence():
        out = ""
        crow = []
        for rname, cs in [(repo, p.get("commits") or [])] + [
                (o["repo"].replace("https://github.com/", "").strip("/"), o.get("commits") or []) for o in p.get("other_repos") or []]:
            for c in cs:
                if c.get("after_due"):
                    continue
                crow.append(f'<tr><td class=w>{e(short_date(c["when"]))}</td><td><a href="https://github.com/{e(rname)}/commit/{e(c["sha"])}">'
                            f'<code>{e(c["sha"][:7])}</code></a></td><td>{e(c["message"].splitlines()[0] if c.get("message") else "")}</td>'
                            f'<td class=r>{e(rname.split("/")[-1])}</td></tr>')
        if crow:
            out += evi("Commits", f"{len(crow)}", f'<div class=scroll><table class=axt>{"".join(crow)}</table></div>')
        text = (p.get("review") or {}).get("text")
        if text:
            out += evi("Your sprint review, as graded", "full report", f'<div class=doc>{md(text, repo)}</div>')
        return out

    def demo_head():
        lid = re.search(r"loom\.com/(?:share|embed)/([0-9a-f]{20,})", loom.get("url") or "")
        if not lid:
            return ""
        frames = loom.get("frames") or []
        poster = img_b64(frames[0]["path"]) if frames and Path(frames[0]["path"]).exists() else None
        secs = loom.get("seconds")
        length = f", {secs // 60}:{secs % 60:02d}" if secs else ""
        return (f'<div class=video><iframe src="https://www.loom.com/embed/{lid.group(1)}?hide_owner=true&hide_share=true" '
                f'loading=lazy allowfullscreen title="Your Loom demo"></iframe>'
                f'<a class=poster href="{e(loom["url"])}">' + (f'<img src="{poster}" alt="">' if poster else "") +
                f'</a></div><p class=dmeta><a href="{e(loom["url"])}">{e(loom.get("title") or "Your Loom")}</a>{length}. '
                f'If the player does not load here, this link opens it on Loom.</p>')

    def demo_scott():
        if not scott:
            return ""
        out = ""
        figs = []
        notes = r.get("demo_notes") or []
        for i, fr in enumerate(loom.get("frames") or []):
            src = img_b64(fr["path"]) if Path(fr["path"]).exists() else None
            if not src:
                continue
            s = fr.get("at_seconds") or 0
            note = notes[i]["sees"] if i < len(notes) else ""
            figs.append(f'<figure><img src="{src}" alt="Loom at {s // 60}:{s % 60:02d}"><figcaption><b>{s // 60}:{s % 60:02d}</b> {e(note)}</figcaption></figure>')
        if figs:
            out += inst_sub("Moment by moment", f"{len(figs)} stills", f'<div class=frames>{"".join(figs)}</div>')
        if loom.get("transcript"):
            out += inst_sub("Transcript", "", f'<p class=tr>{e(loom["transcript"])}</p>')
        return out

    def cat_body(c):
        fb = (r.get("feedback") or {}).get(c, "")
        if c == "shipped":
            return f"<p>{e(fb)}</p>" + how_scored(c) + "<!--EV:shipped-->" + output_evidence() + "<!--/EV-->"
        if c == "review":
            return f"<p>{e(fb)}</p>" + how_scored(c) + "<!--EV:review-->" + review_evidence() + "<!--/EV-->"
        if c == "demo":
            return demo_head() + f"<p>{e(fb)}</p>" + how_scored(c) + demo_scott()
        return f"<p>{e(fb)}</p>" + how_scored(c)

    # All closed except Demo, so the student's own video is right there (Scott, 2026-10-29); the point
    # deductions under the rows are what a student reads first.
    kids = "".join(row(LABELS.get(c, label), f"{fmt(final(row_, c))}<small>/{mx}</small>", cat_body(c), "kid",
                       opened=(c == "demo"))
                   for c, label, mx in graded)
    days_late = f.get("canvas_days_late", 0) or 0
    # The report shows the score that is posted; Canvas applies its own late deduction on top (Scott, 2026-10-16).
    wrap_canvas = review_total * (1 - min(100, 10 * days_late) / 100) if days_late else review_total
    if sprint == 1:
        total, total_max = review_total, review_max
        score_body = kids.replace('class="q kid"', 'class="q"')
        canvas = f"Posted to Canvas: Sprint 1 {fmt(review_total)}/{review_max}."
    else:
        ps = str((plan_row or {}).get("score", "")).strip()
        plan_pts = float(ps) if ps else 0.0
        total, total_max = plan_pts + review_total, 10 + review_max
        if ps:
            when = (plan_row or {}).get("submitted_at") or ""
            plan_body = (f"<p>{e(RUBRIC['plan'])}</p>" + (f"<p class=qm>Turned in on Canvas {e(when)}.</p>" if when else "")
                         + (f"<p>Missing: {e(plan_row['fields_missing'])}.</p>" if (plan_row or {}).get("fields_missing") else "")
                         + (f"<p>{e(plan_row['note'])}</p>" if (plan_row or {}).get("note") else ""))
            text = (p.get("plan_submission") or {}).get("text")
            if text:
                plan_body += f'<p class=qm>Your plan, as turned in:</p><div class="doc scroll">{md(text, repo)}</div>'
        else:
            plan_body = f"<p>No plan was turned in on Canvas for Sprint {sprint}.</p><p>{e(RUBRIC['plan'])}</p>"
        score_body = (row("Plan" + ("" if ps else " <span class=qown>not submitted</span>"),
                          f"{fmt(plan_pts)}<small>/10</small>", plan_body)
                      + kids.replace('class="q kid"', 'class="q"'))
        canvas = (f"Posted to Canvas: Sprint {sprint} Plan {fmt(plan_pts)}/10 and Sprint {sprint} Wrap-up "
                  f"{fmt(review_total)}/{review_max}.")
    score_body += deductions_block(r, sprint, cats, dispute, outcomes, scott)
    score_body += "<!--ASK-->"
    note = (row_.get("scott_note") or "").strip()
    if note:
        score_body += f'<div class=snote><b>From Professor Murff</b><p>{e(note)}</p></div>'

    # ---- profile
    svg, drawn = profile_svg(G)
    if G:
        core_sw = (f'<span class=sw style="background:{CORE_COLOR}"></span>Your September survey '
                   if any(((G.get("start") or {}).get("points") or {}).values()) else "")
        sw = core_sw + "".join(
            (f'<button type=button class=lg data-s="{s}"><span class=sw style="background:{SPRINT_COLORS.get(s, NAVY)}">'
             f'</span>Sprint {s}</button> ') if isinstance(s, int) else
            (f'<a class=lgx href="#midterm"><span class=sw style="background:{EXAM_COLOR.get(s, ROYAL)}"></span>'
             f'{EXAM_LABEL.get(s, s)}</a> ') for s in drawn)
        cap = f'{sw}<a href="#a-profile" class=capl>How to read this</a>'
    else:
        cap = "Your builder profile is being prepared."

    # ---- how you grew: one table by axis, then this sprint's evidence by axis, then earlier sprints
    def pt(x):
        return str(round(float(x)))

    def pt1(x):
        """Item points to one decimal, so a row's items visibly add up to its total."""
        v = round(float(x), 1)
        return str(int(v)) if v == int(v) else str(v)

    if G:
        rings = [r_ for r_ in G.get("rings") or [] if r_.get("coded")]
        last = (G.get("rings") or [{}])[-1]
        pts_now = last.get("points") or {}
        core = (G.get("start") or {}).get("points") or {}
        cur = G.get("sprint") or sprint
        ctime = {c["sha"][:7]: c["when"] for c in (p.get("commits") or [])}

        def concept_row(m):
            link = ref_link(repo, m.get("ref"))
            return row(e(m.get("name") or m["concept"]),
                       f'<span class=qd>{e(short_date(m.get("when")))}</span><span class=qp>+{pt1(m.get("points", 0))}</span>',
                       f'<p>{e(m.get("did", ""))}</p><p class=qm>{e(m.get("evidence", ""))}{" · " + link if link else ""}</p>',
                       chips=book_chips(m.get("concept")))

        def depth_row(ax, lv, why, gain, best_before):
            right = f'level {lv}, {e(LEVELS.get(lv, ""))}'
            if gain:
                right += f'<span class=qp>+{pt1(depth_points(ax, gain["from"], gain["to"]))}</span>'
            body = f'<p><b>Level {lv}, {e(LEVELS.get(lv, ""))}:</b> {e(LEVEL_TEXT.get(lv, ""))}.</p>'
            if why:
                body += f'<p class=qm>What showed it: {e(why)}</p>'
            if gain:
                body += (f'<p class=qm>Moving from {"level " + str(gain["from"]) if gain["from"] else "no level"} to level {gain["to"]} '
                         f'adds {pt1(depth_points(ax, gain["from"], gain["to"]))} points.</p>')
            elif best_before >= lv:
                body += f'<p class=qm>You reached level {best_before} on this axis before, so this adds no points.</p>'
            if lv < 4:
                body += f'<p class=qm>Next, level {lv + 1}, {e(LEVELS.get(lv + 1, ""))}: {e(LEVEL_TEXT.get(lv + 1, ""))}.</p>'
            return row("Depth", right, body, "dep")

        def view(s_):
            """The growth table as it stood at the end of sprint s_: each axis row opens to that
            sprint's depth and new concepts."""
            upto = [r_ for r_ in rings if r_["sprint"] <= s_]
            ring = next((r_ for r_ in rings if r_["sprint"] == s_), {})
            pts = ring.get("points") or {}
            tot = {ax: float(core.get(ax, 0)) + sum(float((r_.get("points") or {}).get(ax, 0)) for r_ in upto) for ax in AXES}
            reach, before = {}, {}
            for r_ in upto:
                for ax, g in (r_.get("depth") or {}).items():
                    if r_["sprint"] < s_:
                        before[ax] = max(before.get(ax, 0), g["to"])
                    reach[ax] = max(reach.get(ax, 0), g["to"])
            items, deps = {}, {}
            if s_ == cur:
                for m in G.get("new") or []:
                    items.setdefault(m["axis"], []).append(m)
                for d in G.get("depth") or []:
                    if d.get("level"):
                        deps[d["axis"]] = (d["level"], d.get("why", ""), d.get("gain"))
            else:
                for x in G.get("earlier") or []:
                    if x["sprint"] != s_:
                        continue
                    if x.get("depth"):
                        deps[x["axis"]] = (x["level"], x.get("why", ""), (ring.get("depth") or {}).get(x["axis"]))
                    else:
                        items.setdefault(x["axis"], []).append(x)
            order = sorted(AXES, key=lambda a: (-float(pts.get(a, 0)), AXES.index(a)))
            out = ('<div class="gx gxh"><span>Axis</span><span>Depth reached</span><span class=gn>New concepts</span>'
                   f'<span class=gp>Sprint {s_}</span><span class=gt>Total of 100</span></div>')
            any_ = False
            for ax in order:
                lst = sorted(items.get(ax, []), key=lambda m: (when_key(m), ctime.get(str(m.get("ref", ""))[:7], "")), reverse=True)
                lvl, add = reach.get(ax, 0), float(pts.get(ax, 0))
                cells = (f'<span class=gl>{f"{lvl} {LEVELS[lvl]}" if lvl else "<span class=qm>none yet</span>"}</span>'
                         f'<span class=gn>{len(lst) or ""}</span>'
                         f'<span class=gp>{"+" + pt(add) if round(add) else ""}</span>'
                         f'<span class=gt><span class=gbar><i style="width:{min(100, tot[ax]):.0f}%"></i></span>{pt(tot[ax])}</span>')
                name = e(ax.replace("Application Architecture", "App Architecture"))
                if not lst and ax not in deps:
                    out += f'<div class="gx gx0"><span class=qn>{name}</span>{cells}</div>'
                    continue
                any_ = True
                body = ""
                if ax in deps:
                    lv, why, gain = deps[ax]
                    body += depth_row(ax, lv, why, gain, before.get(ax, 0))
                body += "".join(concept_row(m) for m in lst)
                out += (f'<details class="q gx"><summary><span class=qn>{name}</span>{cells}</summary>'
                        f'<div class=qb>{body}</div></details>')
            if not any_:
                out += f"<p>No new concepts or depth were counted in Sprint {s_}.</p>"
            if s_ == cur:
                out += not_yet(G.get("not_counted") or [], s_)
            return out

        shown = sorted({r_["sprint"] for r_ in rings} | {cur})
        grew = ""
        if len(shown) > 1:
            grew += '<div class=gsw role=group aria-label="Show sprint">' + "".join(
                f'<button type=button data-s={s_}{" class=on aria-pressed=true" if s_ == cur else " aria-pressed=false"}>Sprint {s_}</button>'
                for s_ in shown) + '</div>'
        grew += "".join(f'<div class=gview data-s={s_}{"" if s_ == cur else " hidden"}>{view(s_)}</div>' for s_ in shown)
        for ex in G.get("exams") or []:
            def tcell(v, t):
                c = (v.get("by_type") or {}).get(t)
                return f'<td class=num>{c["correct"]} of {c["of"]}</td>' if c else "<td></td>"
            rows_m = "".join(
                f'<tr><td>{e(a)}</td><td class=num><b>{v["correct"]} of {v["of"]}</b></td>'
                + "".join(tcell(v, t) for t in ("know", "use", "predict"))
                + f'<td class=num>+{fmt(round(float(v["points"]), 1))} <small>of {fmt(v["max"])}</small></td></tr>'
                for a, v in (ex.get("axes") or {}).items())
            m_tot = sum(float(v["points"]) for v in (ex.get("axes") or {}).values())
            grew += (f'<div class=mt id=midterm><h3 class=sub><span>{EXAM_LABEL.get(ex["exam"], ex["exam"])}</span>'
                     f'<small>{ex["correct"]} of {ex["of"]} right · +{fmt(round(m_tot, 1))}</small></h3>'
                     f'<p>The midterm measured what you know in three areas. Each question right earns its share of half of the '
                     f'area\'s exam points; the final exam measures the other half and the other three areas.</p>'
                     f'<table class=mtt><tr><th>Area</th><th>Right</th><th>Know it</th><th>Use it</th><th>Predict it</th><th>Points</th></tr>{rows_m}</table></div>')
        g_tot = sum(float(v) for v in pts_now.values())
        n_new = len(G.get("new") or [])
        grew_right = (f'+{pt(g_tot)} this sprint · {n_new} new concept{"s" * (n_new != 1)}' if g_tot else "nothing new counted")
    else:
        grew_right, grew = "being prepared", "<p>Your builder profile is being prepared.</p>"

    # ---- what was reviewed
    rev_bits, rev_body = [], ""
    diff_row = days_row = nv_row = ""
    if diff.get("assessed"):
        rev_bits.append(f'difficulty {diff["assessed"]} of 5')
        note_ = diff.get("note") or ""
        pred = f'You predicted {diff["predicted"]}' if diff.get("predicted") is not None else ""
        rated = f' and rated it {diff["student_actual"]}' if diff.get("student_actual") is not None else ""
        lead = f"<p>{pred}{rated}.</p>" if pred else ""
        if note_ and not note_.startswith("You predicted"):
            lead += f"<p>{e(note_)}</p>"
        elif note_:
            lead = f"<p>{e(note_)}</p>"
        # Students read "the work was closer to a 3" as a deduction (Spencer Layton, Chris Hoerler, Oct 2026), so the
        # row always says what difficulty did to the score.
        eff_ = (diff.get("effect_on_shipped") or "none").strip()
        m_ = re.match(r"(raised|lowered) by (\d+(?:\.\d+)?)", eff_)
        if m_:
            n_ = m_.group(2)
            effect = f"It {m_.group(1)} your Output by {n_} point{'s' * (n_ != '1')}."
        elif eff_.startswith(("raised", "lowered")):
            effect = f"It {eff_.split()[0]} your Output."
        else:
            effect = "It did not change your score."
        diff_row = evi("How hard it was", f'{diff["assessed"]} of 5',
                        lead + f'<p>{effect}</p>'
                        + f'<p class=qm>On the course scale, {diff["assessed"]} is "{SCALE.get(int(diff["assessed"]), "")}".</p>')
    if rep.get("sessions"):
        rev_bits.append(f'{rep["sessions"]} agent sessions')
    by_day = {}
    for rname, cs in [(repo, p.get("commits") or [])] + [(o["repo"], o.get("commits") or []) for o in p.get("other_repos") or []]:
        for c in cs:
            if not c.get("after_due"):
                by_day[c["when"][:10]] = by_day.get(c["when"][:10], 0) + 1
    n_commits = sum(by_day.values())
    rev_bits.append(f"{n_commits} commit{'s' * (n_commits != 1)}")
    start = end = None
    if rep.get("window"):
        start, end = (dt.date.fromisoformat(x) for x in rep["window"])
    elif by_day:
        start, end = min(dt.date.fromisoformat(d) for d in by_day), max(dt.date.fromisoformat(d) for d in by_day)
    due = (p.get("assignment") or {}).get("due")
    if start and due:
        end = max(end, dt.date.fromisoformat(due[:10])) if end else dt.date.fromisoformat(due[:10])
    if start and end and (end - start).days < 40:
        days = [start + dt.timedelta(i) for i in range((end - start).days + 1)]
        days_row = evi("Day by day", f"{n_commits} commits", commit_strip(days, by_day))
    nv = rep.get("not_visible")
    if nv:
        nv = nv.strip().rstrip(".")
        nv_row = evi("What the review could not see", "", f"<p>{e(nv[:1].upper() + nv[1:])}.</p>")
    first_parts = {"shipped": diff_row, "review": days_row + nv_row}
    score_body = re.sub(r"<!--EV:(\w+)-->(.*?)<!--/EV-->",
                        lambda m: ev_drawer([first_parts.get(m.group(1), ""), m.group(2)]), score_body, flags=re.S)

    # ---- next sprint steps: what keeps work from counting, then suggestions, then setup
    steps = []
    rr = readme_replay(p)
    if p.get("repo") and not rr["has_section"]:
        steps.append(("counts", 'Add a "Where the work lives" section to your README.',
                      "Only what is in your course repo, or listed there, can count toward your sprint. Add it below Context, one line per place.",
                      README_PASTE))
    asked = " ".join(q.get("title", "") + " " + q.get("body", "") for q in f.get("share_requests") or []).lower()
    for u in [u for u in f.get("repos_named_but_not_shared") or [] if u.lower() not in asked]:  # a share request covers it
        steps.append(("counts", f"Share {e(u)} with sdmurff, or list it.",
                      "If you administer it, add <code>sdmurff</code> as a collaborator. If it belongs to a company you cannot "
                      "share, list it in your README, and <code>/sprint-review</code> will summarize its commits (dates and messages, never code).", ""))
    # Work kept somewhere private that is not a repo (a local folder, a Google Doc, a private artifact):
    # set per student in the packet's facts after the audit, each with its own wording.
    for req in f.get("share_requests") or []:
        steps.append((req.get("kind", "counts"), e(req["title"]), re.sub(r"`([^`]+)`", r"<code>\1</code>", e(req["body"])), ""))
    bad_docs = [x for x in rr["extra"] + [y for it in rr["listed"] for y in it["places"]] if x[2] == "bad" and "google" in x[1]]
    bad_docs += [d for d in p.get("drive_files") or [] if not d.get("ok")] if not bad_docs else []
    if bad_docs:
        steps.append(("counts", "Share your Google files with aifoundry.byu@gmail.com.",
                      'Some could not be opened. Share each one with aifoundry.byu@gmail.com, or set it to "Anyone with the link can view".', ""))
    if f.get("plan_changed_during_sprint") and not f.get("plan_change_noted"):
        steps.append(("counts", "When your plan changes, run /sprint-plan again.",
                      "It asks what changed and why, adds a dated note to the plan, and commits it.", ""))
    nxt = r.get("next_sprint") or ""
    for sent in [x for x in re.split(r"(?<=\.)\s+(?=You might)", nxt) if x.strip()]:
        s_ = re.sub(r"^You might (also )?consider ", "", sent.strip()).rstrip(".")
        s_ = re.sub(r"^(\w+?ing)\b", lambda m: imperative(m.group(1)).capitalize(), s_)
        # A second verb in the same sentence: "Recording X, and writing down Y" -> "and write down Y".
        # Only before an example: in "such as tapping a band and watching the tip", the gerunds stay.
        m_ex = re.search(r"\b(?:such as|for example|for instance|like)\b", s_)
        head, tail = (s_[:m_ex.start()], s_[m_ex.start():]) if m_ex else (s_, "")
        head = re.sub(r"\b(and|then|or) (\w+ing)\b", lambda m: f"{m.group(1)} {imperative(m.group(2))}", head)
        s_ = head + tail
        steps.append(("try", e(s_[0].upper() + s_[1:] + "."), "", ""))
    fmt_like = re.compile(r"\b(retro|README|review\.md|plan\.md|/sprint-plan|/sprint-review)\b", re.I)
    steps.sort(key=lambda st: {"try": 0 if not fmt_like.search(st[1]) else 2, "counts": 1}.get(st[0], 3))
    if skills_status in ("OLD", "missing"):
        steps.append(("house", "Update your course skills.",
                      "Your repo has an older copy of the course skills (<code>/sprint-plan</code> or <code>/sprint-review</code>). Open Claude Code in your course repo and paste this.", SKILLS_PASTE))
    tag = {"counts": "so all your work counts", "try": "from your review", "house": "setup"}
    lis = ""
    for i, (k, t, d, code) in enumerate(steps, 1):
        body = (f"<p>{d}</p>" if d else "") + (sub("What to paste", "", f"<pre>{e(code)}</pre>") if code else "")
        lis += (f'<li class="ns {k}"><span class=nsn>{i}</span><div><div class=nst>{t} <span class=nsk>{tag[k]}</span></div>'
                f'{body}</div></li>')
    has_ded = any(float(d.get("points") or 0) > 0 for d in r.get("deductions") or [])
    intro = ('<p class=nsi>Each point deduction above says how to earn those points next sprint.'
             f'{" Beyond those:" if lis else ""}</p>' if has_ded else "")
    todo = intro + (f"<ol class=nsl>{lis}</ol>" if lis else "" if has_ded else "<p>Nothing to fix: your repo and README are set.</p>")
    from sprint_config import GRADED
    nn = sprint + 1
    pts = {c: mx for c, _l, mx in GRADED[nn]} if nn in GRADED else {"shipped": 20, "review": 10, "demo": 10}
    turnin = (TURNIN.replace("{OUT}", str(pts["shipped"])).replace("{REV}", str(pts["review"])).replace("{DEM}", str(pts["demo"]))
              .replace("{DUE}", "Thursday, December 10, 11:59 PM" if nn == 6 else "The Monday the sprint ends, 11:59 PM")
              .replace("{DEMO_LEN}", "3 to 4 minutes" if nn == 6 else "2 to 3 minutes"))
    todo += sub("What you turn in, and how", "the four deliverables", turnin)
    next_n = sprint + 1

    # ---- questions
    ask = ((f'<p><b>To dispute a deduction,</b> use its Dispute button under <a href="#deds">Point deductions</a>.</p>' if dispute and dispute.get("token") else "")
           + f'<p><b>For any other question,</b> reply to the comment this report came with, on the Sprint {sprint}'
           f'{" Wrap-up" if sprint > 1 else ""} assignment in Canvas, and say which part of the report you mean. '
           'Professor Murff reads every reply. Questions sent anywhere else may be missed.</p>')

    # Questions sit under Score, right after the deductions they mostly concern (Scott, 2026-10-29).
    q_title = "Questions or disputes" if dispute and dispute.get("token") else "Questions"
    score_body = score_body.replace("<!--ASK-->", f'<div class=qa id=questions><h3 class=sub><span>{q_title}</span></h3>{ask}</div>')

    # ---- appendix
    CL = load_concepts()
    shown_in = {}
    for rg in (G or {}).get("rings") or []:
        for ax, ids in (rg.get("breadth") or {}).items():
            for i in ids:
                shown_in.setdefault(i, rg["sprint"])
    ap_rows, n_all = "", 0
    for ax in [a for a in AXES if a in CL] + [a for a in CL if a not in AXES]:
        cs = CL[ax]["concepts"]
        practicable = [c for c in cs if not c.get("knowledge_only")]
        each = practice_max(ax) * BREADTH_SHARE / len(practicable) if practicable else 0
        ap_rows += ('<tr class=apg><td colspan=2></td></tr>' if ap_rows else '') + (f'<tr class=apx><td colspan=2>{e(ax)} <span>up to {fmt(practice_max(ax))} from sprints · '
                    f'{fmt(each)} per concept</span></td></tr>')
        items = list(CL[ax]["items"]) + sorted({c.get("item") for c in cs} - set(CL[ax]["items"]), key=str)
        for code in items:
            group = [c for c in cs if c.get("item") == code]
            if not group:
                continue
            got = sum(1 for c in group if shown_in.get(c["id"]))
            ap_rows += (f'<tr class=api><td colspan=2>{e(CL[ax]["items"].get(code) or "Other")}'
                        f'<span>{got} of {len(group)} shown</span></td></tr>')
            for c in group:
                n_all += 1
                s_ = shown_in.get(c["id"])
                status = ("measured on the exams" if c.get("knowledge_only") else f"Sprint {s_}" if s_ else "")
                ap_rows += (f'<tr class="{"got" if s_ else ""}{" ko" if c.get("knowledge_only") else ""}"><td><b>{book_name(c["id"], c["name"])}</b>'
                            f'</td><td class=apd>{e(status)}</td></tr>')
    appendix = f"""
<h3 class=sub id=a-profile><span>Your builder profile</span></h3>
<p>The six-sided chart shows the six areas (the axes of the chart) a product builder works in. Each area runs from 0
to 100, and 100 in all six is a full-stack product builder: someone who can find a problem worth solving, design and build
the product, and get it to real users.</p>
<h3 class=sub id=a-points><span>Where the points come from</span></h3>
<p>Up to half of each area comes from your sprint work (a quarter on AI Systems), and
the rest from the exams. The center of the chart is your own rating from the September survey, counted on the part of each
area's exam points no exam has measured yet. Each ring outside it is one sprint, darker for later sprints. The gold ring is the
midterm: it tested three areas (Agentic Workflow, Discovery, Design), and each question you got right earns its share of half of
those areas' exam points, so on those three areas the September rating now counts for the other half only. The dashed outline
shows your full September rating. The final exam measures the rest, in all six areas.</p>
<h3 class=sub id=a-earn><span>How sprint work earns points</span></h3>
<p>Sprint work earns points two ways.</p>
<ul>
<li><b>Concepts:</b> the first time your work shows a concept from the concept list (Appendix B), it earns its points (70% of an area's
sprint points are spread across its concepts). A concept counts once.</li>
<li><b>Depth:</b> the highest level you have worked at in an area (the other 30%). Level 1, Followed, earns nothing; level
2, Directed, 20%; level 3, Decided, 50%; level 4, Delivered, all of it. Each report says what your level means and what
the next one looks like.</li>
</ul>
<h3 class=sub id=a-counts><span>What counts</span></h3>
<p>Work you can point to: a commit or file in a shared repo, a shared Google file, a live link, or a
moment in your Loom. Close calls and the higher depth levels are checked a second time against that evidence. Work
described only in your review or retro, work in a repo that is not shared unless your <code>/sprint-review</code> report lists
its commits, and anything the course gave you do not count;
they appear under "Seen this sprint, not yet in your profile", with what would let them count. A few concepts and depth level 4 rely on lists that the current
<code>/sprint-review</code> writes ("Builder tools you used" and "Users this sprint"); a Sprint 2 review made with an older
version could not show them, so update your course skills before your next review.</p>
<p>Your sprint rings never shrink, and the profile does not affect your grade.</p>
<!--APX-B--><p>Every concept in the course, by area and topic, with a link to where the book teaches it. The
ones your work has shown say which sprint. Ones marked "measured on the exams" count only on the exams.</p>
<table class=apt><tr><th>Concept</th><th>Shown</th></tr>{ap_rows}</table>"""

    # ---- instructor band
    band = ""
    if scott:
        ov = ", ".join(f"{LABELS.get(c, c)} {row_['override_' + c]}" for c, _, _ in cats if str(row_.get("override_" + c, "")).strip())
        parts = [f'<div class=igrid><div><b>Confidence</b> {e(str(r.get("confidence", "")))}</div>'
                 f'<div><b>Watch the Loom</b> {"yes" if r.get("watch_loom") else "no"}</div>'
                 f'<div><b>Approved</b> {e(row_.get("approved") or "not yet")}</div>'
                 f'<div><b>Overrides</b> {e(ov or "none")}</div></div>']
        if diff:
            parts.append(f'<p><b>Difficulty, with the baseline</b> (never shown to students): assessed {e(str(diff.get("assessed")))} on '
                         f'{e(str(diff.get("axis", "")))}, baseline {e(str(diff.get("baseline_on_axis", "")))}; predicted '
                         f'{e(str(diff.get("predicted")))}, student said {e(str(diff.get("student_actual")))}; effect on Output: '
                         f'{e(str(diff.get("effect_on_shipped") or "none"))}. {e(diff.get("why", ""))}</p>')
        h = r.get("hours") or {}
        if h:
            hv = lambda k: fmt(float(h[k])) if h.get(k) is not None else "none"
            parts.append(f'<p class=ihours><b>Hours</b> (never shown to students): student estimate {hv("self")}'
                         + (f' (&ldquo;{e(h["self_text"])}&rdquo;)' if h.get("self_text") else "")
                         + f', active session time {hv("session")}, grader estimate {hv("est")}. {e(h.get("est_why") or "")}</p>')
        if r.get("axes"):
            parts.append(f'<p><b>Axis split</b> {e(", ".join(f"{k} {round(v * 100)}%" for k, v in r["axes"].items()))}. {e(r.get("axes_why", ""))}</p>')
        if days_late:
            parts.append(f"<p><b>Late</b> {days_late} day(s) on Canvas: the Wrap-up shows {fmt(review_total)} here and "
                         f"{fmt(wrap_canvas)} in Canvas after its automatic deduction. The student copy shows the posted score; Canvas shows the deduction.</p>")
        parts.append("<p><b>Raw flags</b></p><ul>" + "".join(f"<li><code>{e(x)}</code></li>" for x in r.get("flags") or []) + "</ul>"
                     if r.get("flags") else "<p><b>Raw flags</b> none</p>")
        parts.append("<p><b>Fairness check</b></p><ul>" + "".join(f"<li>{e(x)}</li>" for x in fairness) + "</ul>"
                     if fairness else "<p><b>Fairness check</b> no findings for this student</p>")
        if G:
            dis = G.get("disputed") or []
            checked = G.get("check") == "checked"
            title = ("Dropped on the second check" if checked else "Disputed concepts") + \
                    (" (not counted; settle to add)" if checked else " (one coder only, not counted; settle to add)")
            parts.append(f"<p><b>{title}</b></p><ul>" +
                         "".join(f'<li>{e(d.get("name", d.get("concept", "")))} ({e(d.get("concept", ""))})'
                                 f'{"" if checked else ", coder " + e(str(d.get("coder", "")))}: {e(str(d.get("evidence", "")))}'
                                 f'{" · dropped because " + e(d["why"]) if d.get("why") else ""}</li>' for d in dis) + "</ul>" if dis else
                         f"<p><b>{title.split(' (')[0]}</b> none</p>")
            dl = G.get("depth") or []
            if dl:
                lv = lambda d, i: e(str((d.get("coder_levels") or [None, None])[i]))
                parts.append(f"<p><b>Depth, {'coder and check' if checked else 'the two coders'}</b></p><ul>" + "".join(
                    (f'<li>{e(d["axis"])}: coded {lv(d, 0)}, after the check {lv(d, 1)}, counted {e(str(d.get("level")))}</li>' if checked else
                     f'<li>{e(d["axis"])}: A {lv(d, 0)}, B {lv(d, 1)}, counted {e(str(d.get("level")))}</li>') for d in dl) + "</ul>")
        else:
            parts.append("<p><b>Builder profile</b> no growth file for this student yet.</p>")
        unread = [x for x in ((G or {}).get("not_counted") or []) if x.get("kind") == "unreadable"]
        if unread:
            parts.append("<p><b>Could not be read</b> (left out of the student copy; fix the packet and recode)</p><ul>" + "".join(
                f'<li>{e(x.get("name") or x.get("concept", ""))}: {e(x.get("what") or "")}. {e(x.get("why") or "")}</li>' for x in unread) + "</ul>")
        parts.append('<p class=ihow>To change a grade: edit <code>grades.csv</code> (override_*, scott_note, approved), then rerun '
                     '<code>sprint_feedback.py</code>.</p>')
        band = "".join(parts)

    names = (p.get("name") or "").split()
    first = p.get("preferred_first") or (names[0] if names else "")
    lastn = names[-1] if len(names) > 1 else ""
    full = f"{first} {lastn}".strip()
    due_txt = ""
    if due:
        d = dt.date.fromisoformat(due[:10])
        due_txt = f"Due {d:%b} {d.day}, {d.year}"
    n_steps = len(steps)
    copy = "Scott's copy" if scott else ""
    # Summary numbers: the profile total and what this sprint added.
    prof_line, added = "", 0
    if G:
        core = (G.get("start") or {}).get("points") or {}
        whole = (sum(float(v) for v in core.values()) + sum(float(v) for v in (G.get("practice_total") or {}).values())
                 + sum(float(v) for ex in G.get("exams") or [] for v in (ex.get("points") or {}).values()))
        added = sum(float(v) for v in ((G.get("rings") or [{}])[-1].get("points") or {}).values())
        prof_line = (f'<div class=sm><span class=sml>Builder profile</span><span class=smv>{round(whole)}<small> / 600</small></span>'
                     f'<span class=sms>+{round(added)} this sprint, {whole / 6:.0f}% towards a full-stack product builder</span></div>')
    # Go over this report with Claude Code: one button copies a prompt that carries the report's facts.
    score_lines = []
    if sprint > 1:
        pr = plan_row or {}
        reason = (pr["note"] if pr.get("note") else
                  "All four fields are there." if ps and not pr.get("fields_missing") else
                  f"Missing: {pr['fields_missing']}." if ps else f"No plan was turned in on Canvas for Sprint {sprint}.")
        score_lines.append(("Plan", fmt(plan_pts), 10, reason))
    score_lines += [(LABELS.get(c, c), fmt(final(row_, c)), mx, first_sentence((r.get("feedback") or {}).get(c, "")))
                    for c, _l, mx in graded]
    prompt_txt = coach_prompt(sprint, total, total_max, score_lines, steps, G)
    next_line = (f'<div class="sm coach"><div class=cchead><span class=cch>Go over this report with Claude Code</span>'
                 f'<button type=button class=ccbtn data-copy=coachp aria-label="Copy the prompt for Claude Code">'
                 f'{CLAUDE_ICON}<span class=cclabel>Copy prompt</span></button></div>'
                 f'<span class=ccnote role=status aria-live=polite></span>'
                 f'<details class=ccbox><summary>See the prompt</summary>'
                 f'<textarea id=coachp readonly spellcheck=false rows=14>{e(prompt_txt)}</textarea></details></div>')
    if dispute and dispute.get("token"):
        next_line += (f'<form class="sm coach rfb" method=post action="{FEEDBACK_API}" target=_blank>'
                      f'<div class=cchead><span class=cch id=rfbq>How useful is this report?</span>'
                      f'<span class=rfbw><span class=rfbs role=radiogroup aria-labelledby=rfbq>'
                      + "".join(f'<label class=rfbn><input type=radio name=rating value={n} required>'
                                f'<span aria-label="{n} of 5">{n}</span></label>' for n in range(1, 6))
                      + '</span><span class=rfbh><span>Not useful</span><span>Very useful</span></span></span></div>'
                      '<textarea name=text rows=2 maxlength=4000 aria-label="Your comments" '
                      'placeholder="What helped, and what should change? (optional)"></textarea>'
                      f'<input type=hidden name=token value="{e(dispute["token"])}">'
                      '<input class=rfbhp name=website tabindex=-1 autocomplete=off aria-hidden=true>'
                      '<div class=rfbf><span class=rfbst role=status aria-live=polite></span>'
                      '<button type=submit class=rfbsend>Send comment</button></div></form>')
    lost = [d for d in r.get("deductions") or [] if float(d.get("points") or 0) > 0]
    lost_pts = sum(float(d["points"]) for d in lost)
    lost_line = (f'<a class="sms lost" href="#deds">{fmt(lost_pts)} point{"s" * (lost_pts != 1)} deducted in {len(lost)} '
                 f'item{"s" * (len(lost) != 1)}{", each open to dispute" if dispute and dispute.get("token") else ""}</a>' if lost else "")
    parts_ = ([f"Plan {fmt(plan_pts)}"] if sprint > 1 else []) + [f"{LABELS.get(c, c)} {fmt(final(row_, c))}" for c, _l, _m in graded]
    summary = (f'<div class=smrow><div class=sm><span class=sml>Sprint {sprint} score</span>'
               f'<span class=smv>{fmt(total)}<small> / {total_max}</small></span><a class=sms href="#score">{" · ".join(parts_)}</a>{lost_line}</div>'
               f'{prof_line}</div>{next_line}'
               f'<figure class=qfig>{svg}<figcaption>{cap}</figcaption>'
               + ('<p class=rhint>Click a ring, an axis, or a sprint to see where you grew</p>' if G and drawn else "")
               + '</figure>')
    secs = []
    if band:
        secs.append(("inst", "Instructor notes", "not in the student copy", band, "inst"))
    secs += [
        ("summary", "Summary", "", summary, ""),
        ("score", "Score", f'{fmt(total)} / {total_max}, posted to Canvas', score_body, ""),
        ("next", "Next steps", f'{n_steps} step{"s" * (n_steps != 1)}' if n_steps else "", todo, ""),
        ("grew", "Growth", grew_right, grew, ""),
        ("appendix", "Appendix A: How grading works", "", appendix.split("<!--APX-B-->")[0], ""),
        ("concepts", "Appendix B: Concept list", f"{n_all} concepts", appendix.split("<!--APX-B-->")[1], ""),
    ]
    short = {"score": f"{fmt(total)}/{total_max}", "grew": f"+{fmt(round(added))}" if G and added else "",
             "next": str(n_steps) if n_steps else ""}
    toc = "".join(f'<a href="#{i}" class="{c}"><span>{e(t)}</span><small>{short.get(i, "")}</small></a>'
                  for i, t, r_, _b, c in secs)
    body = "".join(f'<section id={i} class="sec {c}"><h2><span>{e(t)}</span><small>{r_}</small></h2>{b}</section>'
                   for i, t, r_, b, c in secs)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprint {sprint} Report · {e(full)}{" (" + copy + ")" if copy else ""}</title>{FONTS}<style>{CSS}{TOC_CSS}</style></head><body>
<div class=layout>
<nav class=toc><div class=tocname>Sprint {sprint} Report<br><b>{e(full)}</b><br><span>{e(due_txt)}</span></div>{toc}</nav>
<main>
<header class=qh><span class=qtitle>Sprint {sprint} Report · {e(full)}</span><span>{e(due_txt)}</span></header>
<details class=tocm><summary>Contents</summary>{toc}</details>
<div class=brand><b>MSB 341 Product Management</b><span>BYU Marriott School of Business</span></div>
{body}
</main></div>
<script>
// Contents list, two levels: each section, and inside it the things a reader looks for (score
// categories, axes, next steps, evidence rows, appendix axes). Second levels collapse; the section
// being read opens its own. Clicking an item inside a closed drawer opens the drawer.
(()=>{{
const nav=document.querySelector('nav.toc');
const pick={{score:':scope>details.q,:scope>.deds>h3.sub,:scope>.qa>h3.sub',grew:':scope>.gview:not([hidden])>details.gx,:scope>.gview:not([hidden])>.qax,:scope details.ncx,:scope>#midterm>h3.sub',appendix:':scope>h3.sub',concepts:'tr.apx'}};
const label=el=>{{
  if(el.matches('h3'))return el.querySelector('span').textContent;
  if(el.matches('details.ncx'))return el.querySelector('h3').firstChild.textContent;
  if(el.matches('details')){{const q=el.querySelector('summary .qn').cloneNode(true);q.querySelectorAll('.bkc').forEach(x=>x.remove());return q.textContent}}
  if(el.matches('li.ns'))return el.querySelector('.nst').textContent;
  const f=el.firstChild;return (f&&f.nodeType===3?f.textContent:(el.querySelector('td')||el).childNodes[0].textContent);
}};
let k=0;
nav.querySelectorAll(':scope>a').forEach(a=>{{
  const sec=document.querySelector(a.getAttribute('href'));const sel=pick[sec.id];
  const g=document.createElement('div');g.className='tg';a.before(g);g.append(a);
  if(!sel)return;
  const items=[...sec.querySelectorAll(sel)];if(!items.length)return;
  const sub=document.createElement('div');sub.className='sub';
  const link=(el,cls)=>{{
    if(!el.id)el.id='t'+(k++);
    const s=document.createElement('a');s.href='#'+el.id;if(cls)s.className=cls;
    let t=label(el).trim().replace(/\\s+/g,' ');
    s.textContent=t.length>44?t.slice(0,42)+'...':t;
    // open the item and every drawer around it, so the target is visible
    s.onclick=()=>{{for(let d=el.matches('details')?el:el.closest('details');d;d=d.parentElement.closest('details'))d.open=true;
      el.querySelectorAll('details').forEach(x=>x.open=true)}};
    return s;
  }};
  items.forEach(el=>{{
    const s=link(el);
    const kids=el.matches('details')?[...el.querySelectorAll(':scope>.qb>details.q')]:[];
    if(!kids.length){{sub.append(s);return}}
    const g3=document.createElement('div');g3.className='tg3';
    const b3=document.createElement('button');b3.className='tw3';b3.setAttribute('aria-label','Show or hide');
    b3.onclick=()=>g3.classList.toggle('open');
    const s3=document.createElement('div');s3.className='sub3';
    kids.forEach(kd=>s3.append(link(kd)));
    g3.append(b3,s,s3);sub.append(g3);
  }});
  const b=document.createElement('button');b.className='tw';b.setAttribute('aria-label','Show or hide');
  const all=on=>{{g.classList.toggle('open',on);g.querySelectorAll('.tg3').forEach(x=>x.classList.toggle('open',on))}};
  b.onclick=()=>all(!g.classList.contains('open'));a.addEventListener('click',()=>all(true));g.prepend(b);g.append(sub);g.classList.add('has');
}});
// Growth: one table, switched between sprints; the current sprint shows first.
document.querySelectorAll('.gsw button').forEach(b=>b.onclick=()=>{{const w=b.closest('section')||document;
  w.querySelectorAll('.gsw button').forEach(x=>{{x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)}});
  w.querySelectorAll('.gview').forEach(v=>v.hidden=v.dataset.s!==b.dataset.s)}});
// Opening a drawer opens every drawer inside it, down to the last level.
document.querySelectorAll('main details').forEach(d=>d.addEventListener('toggle',()=>{{if(d.open)d.querySelectorAll('details').forEach(x=>x.open=true)}}));
const groups=[...nav.querySelectorAll('.tg')];
// Expand all / Collapse all: the contents list and every drawer in the page.
const bar=document.createElement('div');bar.className='tocbar';
[['Expand all',true],['Collapse all',false]].forEach(([t,on])=>{{const x=document.createElement('button');x.textContent=t;
  x.onclick=()=>{{nav.querySelectorAll('.tg.has,.tg3').forEach(g=>g.classList.toggle('open',on));
    document.querySelectorAll('main details').forEach(d=>d.open=on)}};bar.append(x)}});
nav.querySelector('.tocname').after(bar);
const io=new IntersectionObserver(es=>{{es.forEach(x=>{{if(!x.isIntersecting)return;
  groups.forEach(g=>{{const on=g.querySelector(':scope>a').getAttribute('href')==='#'+x.target.id;
    g.querySelector(':scope>a').classList.toggle('on',on);if(on)g.classList.add('open')}})}})}},{{rootMargin:'-20% 0px -70% 0px'}});
document.querySelectorAll('section.sec').forEach(s=>io.observe(s));
}})();
{COACH_JS}
{DISPUTE_JS}
{RINGS_JS}</script>
</body></html>"""


# The dispute drawer (Scott, 2026-10-29). On load it asks the app which deductions are already disputed and whether
# the window is open, since the report itself is a fixed file. Send runs the dispute page's own two steps: signed
# uploads straight to private storage when there are files, then the dispute.
DISPUTE_JS = r"""
(()=>{const box=document.querySelector('.deds[data-api]');if(!box)return;
const api=box.dataset.api,token=box.dataset.token;
const post=o=>fetch(api,{method:'POST',body:JSON.stringify(Object.assign({token},o)),mode:'cors',credentials:'omit'}).then(r=>r.json());
const day=s=>new Date(s).toLocaleDateString(undefined,{month:'short',day:'numeric'});
const btnOf=k=>box.querySelector('.dbtn[data-ded="'+k+'"]'),formOf=k=>box.querySelector('form.dform[data-ded="'+k+'"]');
const mark=(k,txt,ok)=>{const b=btnOf(k);if(b){const sp=document.createElement('span');sp.className='dst'+(ok?' ok':'');sp.textContent=txt;b.replaceWith(sp)}
  const f=formOf(k);if(f)f.remove()};
box.querySelectorAll('.dbtn[data-ded]').forEach(b=>b.addEventListener('click',ev=>{const f=formOf(b.dataset.ded);if(!f)return;
  ev.preventDefault();f.hidden=!f.hidden;b.setAttribute('aria-expanded',String(!f.hidden));if(!f.hidden)f.elements.why.focus()}));
box.querySelectorAll('form.dform').forEach(f=>{
  const k=f.dataset.ded,el=f.elements,btn=f.querySelector('.rfbsend'),st=f.querySelector('.dfst');
  const say=(t,bad)=>{st.textContent=t;st.className='dfst'+(bad?' bad':'')};
  f.querySelector('.dfcancel').onclick=()=>{f.hidden=true;const b=btnOf(k);if(b)b.setAttribute('aria-expanded','false')};
  f.addEventListener('submit',async ev=>{ev.preventDefault();if(btn.disabled)return;
    const why=el.why.value.trim();
    if(why.length<10){say('Say why in at least 10 characters.',true);el.why.focus();return}
    const files=[...el.files.files];
    if(files.length>5){say('Up to 5 files.',true);return}
    const big=files.find(x=>x.size>10*1024*1024);if(big){say(big.name+' is over 10 MB.',true);return}
    const input={why,links:el.links.value.split(/\s*\n\s*/).map(x=>x.trim()).filter(Boolean),
      notes:el.notes.value.trim()?[el.notes.value.trim()]:[],files:files.map(x=>({name:x.name,mime:x.type,size:x.size}))};
    const website=el.website.value;
    btn.disabled=true;btn.textContent='Sending...';say('');
    const fail=m=>{btn.disabled=false;btn.textContent='Send dispute';say(m,true)};
    try{
      let disputeId,paths=[];
      if(files.length){
        const p=await post({action:'prepare',dedKey:k,input,website});if(!p.ok)return fail(p.error);disputeId=p.disputeId;
        for(const [i,u] of p.uploads.entries()){say('Uploading '+files[i].name+'...');
          const r=await fetch(u.url,{method:'PUT',body:files[i],headers:{'content-type':files[i].type,'x-upsert':'false',
            apikey:p.anonKey,authorization:'Bearer '+p.anonKey}});
          if(!r.ok)return fail(files[i].name+' did not upload. Try again.');paths.push(u.path)}}
      const r=await post({action:'send',dedKey:k,input,website,disputeId,paths});
      if(!r.ok)return fail(r.error||"That didn't send. Try again.");
      mark(k,'Disputed '+day(r.createdAt));
      const m=document.createElement('p');m.className='dsent';m.setAttribute('role','status');
      m.textContent='Dispute sent. Professor Murff reviews it and replies by email.';document.getElementById('ded-'+k).append(m);
    }catch(e){fail("That didn't send. Check your connection and try again.")}
  });
});
post({action:'status'}).then(j=>{if(!j||!j.ok)return;
  j.deductions.forEach(d=>{if(d.status)mark(d.dedKey,d.status==='open'?'Disputed '+day(d.disputedAt):'Reviewed')});
  if(!j.open)box.querySelectorAll('.dbtn[data-ded]').forEach(b=>mark(b.dataset.ded,'Disputes closed'));
}).catch(()=>{});
})();
"""


# The rings route to Growth (2026-10-29): hover a ring for that sprint's points on the nearest axis, click a
# ring, an axis name, or a sprint in the legend to open that growth. Axis names are found by their text.
RINGS_JS = r"""
(()=>{
const fig=document.querySelector('.qfig'),svg=fig&&fig.querySelector('svg');if(!svg)return;
const tip=document.createElement('div');tip.className='rtip';fig.append(tip);
const CX=270,CY=200;
const axes=[...svg.querySelectorAll('text.axl')].map(t=>{const x=+t.getAttribute('x'),y=+t.getAttribute('y')+6;
  return{t,short:t.dataset.axis,a:Math.atan2(y-CY,x-CX)}});
const nearest=a=>axes.reduce((b,x)=>{const d=Math.abs(Math.atan2(Math.sin(a-x.a),Math.cos(a-x.a)));return d<b.d?{d,x}:b},{d:9}).x;
const svgPt=ev=>{const p=svg.createSVGPoint();p.x=ev.clientX;p.y=ev.clientY;return p.matrixTransform(svg.getScreenCTM().inverse())};
const rowFor=(s,ax)=>[...document.querySelectorAll(`.gview[data-s="${s}"] .gx`)].find(r=>{const q=r.querySelector('.qn');return q&&q.textContent.trim()===ax.short});
const info=(s,ax)=>{const r=rowFor(s,ax);if(!r)return null;const g=r.querySelector('.gp'),n=r.querySelector('.gn');
  return{pts:(g&&g.textContent.trim())||'',n:(n&&n.textContent.trim())||'',open:r.matches('details')}};
const rings=[...svg.querySelectorAll('polygon[data-s]')];if(!rings.length)return;
const latest=Math.max(...rings.map(p=>+p.dataset.s));
const go=(s,ax)=>{document.querySelector(`.gsw button[data-s="${s}"]`)?.click();
  let r=ax&&rowFor(s,ax);if(!r||!r.matches('details'))r=ax?null:document.querySelector(`.gview[data-s="${s}"] details.gx`);
  if(!r){document.getElementById('grew').scrollIntoView({behavior:'smooth'});return}
  r.open=true;r.classList.remove('flash');void r.offsetWidth;r.classList.add('flash');r.scrollIntoView({behavior:'smooth',block:'center'})};
axes.forEach(x=>x.t.addEventListener('click',()=>go(latest,x)));
document.querySelectorAll('.lg').forEach(b=>b.onclick=()=>go(b.dataset.s,null));
svg.querySelectorAll('polygon.exam').forEach(pg=>{
  const per=JSON.parse(pg.dataset.per||'{}'),name=pg.querySelector('title')?.textContent||'Exam';pg.querySelector('title')?.remove();
  pg.addEventListener('mousemove',ev=>{const p=svgPt(ev),ax=nearest(Math.atan2(p.y-CY,p.x-CX));
    const full=Object.keys(per).find(k=>k.replace('Application Architecture','App Architecture')===ax.short);
    svg.classList.add('hov');pg.classList.add('on');
    const fr=fig.getBoundingClientRect();tip.style.left=(ev.clientX-fr.left)+'px';tip.style.top=(ev.clientY-fr.top)+'px';tip.style.opacity=1;
    tip.innerHTML=`${name} &middot; ${ax.short} <b>${full?per[full]:'not tested'}</b><small>click to see your midterm</small>`});
  pg.addEventListener('mouseleave',()=>{svg.classList.remove('hov');pg.classList.remove('on');tip.style.opacity=0});
  pg.addEventListener('click',()=>{const m=document.getElementById('midterm');if(m)m.scrollIntoView({behavior:'smooth',block:'center'})});
});
rings.forEach(pg=>{
  const s=pg.dataset.s;pg.querySelector('title')?.remove();
  pg.addEventListener('mousemove',ev=>{
    const p=svgPt(ev),ax=nearest(Math.atan2(p.y-CY,p.x-CX)),i=info(s,ax);
    svg.classList.add('hov');rings.forEach(x=>x!==pg&&x.classList.remove('on'));pg.classList.add('on');
    const fr=fig.getBoundingClientRect();tip.style.left=(ev.clientX-fr.left)+'px';tip.style.top=(ev.clientY-fr.top)+'px';tip.style.opacity=1;
    tip.innerHTML=`Sprint ${s} &middot; ${ax.short} <b>${i&&i.pts?i.pts:'no growth'}</b>`+
      (i&&i.n?`<small>${i.n} new concept${i.n==='1'?'':'s'} &middot; click to see them</small>`:i&&i.open?'<small>click to see what counted</small>':'<small>nothing counted on this axis</small>');
  });
  pg.addEventListener('mouseleave',()=>{svg.classList.remove('hov');pg.classList.remove('on');tip.style.opacity=0});
  pg.addEventListener('click',ev=>{const p=svgPt(ev);go(s,nearest(Math.atan2(p.y-CY,p.x-CX)))});
});
})();
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">')

TOC_CSS = '''
body{max-width:none;margin:0;padding:0}
.layout{display:grid;grid-template-columns:220px minmax(0,680px);gap:48px;justify-content:center;padding:28px 22px 80px}
nav.toc{position:sticky;top:24px;align-self:start;font-size:13.5px;max-height:calc(100vh - 48px);overflow:auto}
.tocname{font-size:12.5px;color:var(--mute);margin:0 0 14px;line-height:1.5}.tocname b{color:var(--ink);font-size:14px}
nav.toc a,.tocm a{display:flex;justify-content:space-between;gap:8px;padding:6px 10px;border-left:2px solid var(--line);color:#4a5262}
nav.toc a small,.tocm a small{color:var(--mute);font-size:11.5px;white-space:nowrap;font-variant-numeric:tabular-nums}
nav.toc a:hover{color:var(--ink);background:#fafafb}nav.toc a.on{border-left-color:var(--amber);color:var(--ink);font-weight:600}
nav.toc a.inst{color:#7a5a00}
.tg{position:relative}nav.toc .tg>a{padding-left:22px}
/* Tree carets: one chevron drawn as a mask, centered on the first line of its row, pointing right when closed and down when open. */
.tw,.tw3{position:absolute;display:grid;place-items:center;border:0;background:none;cursor:pointer;padding:0;border-radius:4px}
.tw::before,.tw3::before{content:"";width:12px;height:12px;background:var(--mute);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M6 3.5 10.5 8 6 12.5' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M6 3.5 10.5 8 6 12.5' fill='none' stroke='black' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/contain no-repeat;transition:transform .15s}
.tw:hover::before,.tw3:hover::before{background:var(--ink)}.tw:focus-visible,.tw3:focus-visible{outline:2px solid #003DA5}
.tw{left:3px;top:6px;width:18px;height:1.6em}
.tg.open .tw::before,.tg3.open .tw3::before{transform:rotate(90deg)}
.sub{display:none;margin:0 0 6px}.tg.open .sub{display:block}
nav.toc .sub a{font-size:12.5px;padding:3px 10px 3px 30px;color:var(--mute);border-left:2px solid var(--line)}
nav.toc .sub a:hover{color:var(--ink)}
.tocbar{display:flex;gap:6px;margin:0 0 12px}.tocbar button{font:12px inherit;font-family:inherit;color:#4a5262;background:#F5F7FA;border:1px solid var(--line);border-radius:6px;padding:3px 9px;cursor:pointer}.tocbar button:hover{color:var(--ink);border-color:#CCCCCC}
.tg3{position:relative}.tw3{left:14px;top:3px;width:16px;height:1.6em;font-size:12.5px}.tw3::before{width:11px;height:11px}
.sub3{display:none}.tg3.open .sub3{display:block}
nav.toc .sub3 a{font-size:12px;padding:2px 10px 2px 44px}
main .qh{display:none}.tocm{display:none}
section.sec{padding:8px 0 22px;border-bottom:1px solid var(--line);scroll-margin-top:16px}
section.sec>h2{display:flex;justify-content:space-between;align-items:baseline;gap:14px;font-size:19px;margin:18px 0 10px}
section.sec>h2 small{font-size:13.5px;color:var(--mute);font-weight:400;font-variant-numeric:tabular-nums}
section.inst{background:#fff8e1;border:1px solid #e8c766;border-radius:10px;padding:4px 18px 14px;font-size:12.5px}
section.inst>h2{font-size:15px;color:#7a5a00}
.smrow{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.sm{border:1px solid var(--line);border-radius:10px;background:#F7F9FC;padding:12px 16px;display:flex;flex-direction:column;gap:2px;margin-bottom:12px}
.sml{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute);font-weight:600}
.smv{font-size:28px;font-weight:600;line-height:1.2}.smv small{font-size:.55em;color:var(--mute);font-weight:500}
.sms{font-size:12.5px;color:var(--amber)}.smt{font-size:15px;line-height:1.45}
@media (max-width:900px){.layout{display:block}nav.toc{display:none}main .qh{display:flex}
 .tocm{display:block;border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:0 0 12px}.tocm summary{cursor:pointer;font-weight:600}}
@media print{nav.toc,.tocm,script{display:none}.layout{display:block;padding:0}main .qh{display:flex}}
'''

CSS = '''
:root{--ink:#002E5D;--body:#1A1A1A;--mute:#666666;--line:#E5E5E5;--amber:#003DA5;--navy:#002E5D;--royal:#003DA5;--tint:#EEF4FB}
body{font:15px/1.6 "IBM Plex Sans",-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--body);max-width:640px;margin:28px auto 80px;padding:0 22px}
a{color:#003DA5;text-decoration:none}
code{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;background:#EEF1F5;padding:0 3px;border-radius:3px}
.qh{display:flex;justify-content:space-between;align-items:baseline;font-size:14px;color:var(--mute);margin:0 0 14px}
.qtitle{color:var(--ink);font-weight:600;font-size:15px}
.qscore{font-size:26px;font-weight:600;color:var(--ink)}.qscore small,.qr small,.qtotal small{font-size:.65em;color:var(--mute);font-weight:500}
.qlab{font-size:12.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute);font-weight:600;margin:30px 0 2px}
.qfig{margin:8px -20px 0;text-align:center}.qfig svg{max-width:560px}
.qfig figcaption{font-size:12px;color:var(--mute);margin-top:-6px;line-height:1.7}
.sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin:0 3px 0 8px;vertical-align:0}
.bigs{border-top:1px solid var(--line);margin-top:6px}
details.big{border-bottom:1px solid var(--line)}
details.big>summary{list-style:none;display:flex;justify-content:space-between;align-items:baseline;gap:14px;padding:15px 2px;cursor:pointer}
details.big>summary::-webkit-details-marker{display:none}
details.big .bt{font-size:17px;font-weight:600;color:var(--ink)}
details.big .bt::before{content:"";display:inline-block;width:7px;height:7px;border-right:2px solid var(--amber);border-bottom:2px solid var(--amber);transform:rotate(-45deg);margin:0 12px 0 2px;vertical-align:2px;transition:transform .15s}
details.big[open]>summary .bt::before{transform:rotate(45deg)}
details.big .br{font-size:13.5px;color:var(--mute);text-align:right;font-variant-numeric:tabular-nums}
details.big>.bb{padding:0 2px 18px 23px}
details.big.score{border:1px solid var(--line);border-radius:10px;background:#F7F9FC}
details.big.score>summary{padding:16px 18px;align-items:center}details.big.score>.bb{padding:0 18px 16px 41px}
details.big.score .bt{font-size:12.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute)}
details.big.inst{background:#fff8e1;border:1px solid #e8c766;border-radius:10px;margin:0 0 16px;font-size:12.5px}
details.big.inst>summary{padding:10px 16px}details.big.inst .bt{font-size:14px}details.big.inst>.bb{padding:0 16px 12px}
.igrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:4px 0 8px}.inst ul{margin:2px 0 8px;padding-left:18px}.inst p{margin:6px 0}.ihow{color:#7a5a00}
details.q{border-bottom:1px solid var(--line)}details.q>summary{list-style:none;display:flex;justify-content:space-between;gap:12px;padding:9px 0;cursor:pointer}
details.q>summary::-webkit-details-marker{display:none}
details.q>summary .qn::after{content:"";display:inline-block;width:5px;height:5px;border-right:1.5px solid var(--mute);border-bottom:1.5px solid var(--mute);transform:rotate(-45deg);margin-left:8px;vertical-align:2px;transition:transform .15s}
details.q[open]>summary .qn::after{transform:rotate(45deg)}
details.q>summary:focus-visible,details.big>summary:focus-visible{outline:2px solid #003DA5;outline-offset:2px}
.qr{color:var(--mute);font-size:13.5px;white-space:nowrap;font-variant-numeric:tabular-nums}
details.q.muted .qn{color:var(--mute)}
details.q.s{border-bottom:1px solid #f3f4f6}details.q.s>summary{padding:6px 0;font-size:13.5px}details.q.s .qr{font-size:12.5px}
details.q.kid{margin-left:18px;border-bottom:1px solid #f3f4f6}details.q.kid>summary{padding:8px 0 8px 2px;font-size:14.5px}details.q.kid:last-child{border-bottom:0}
details.q.inst>summary .qn{color:#7a5a00}.instag{font-size:10.5px;background:#fff1c2;color:#7a5a00;border-radius:8px;padding:0 6px;margin-left:4px}
.qb{padding:0 0 12px;font-size:14px}.qb p{margin:0 0 6px}.qb .qb{padding-bottom:8px}.qm{font-size:12.5px;color:var(--mute)}
.qax{display:flex;justify-content:space-between;font-size:12px;color:var(--mute);margin:18px 0 2px;text-transform:uppercase;letter-spacing:.05em}.qax span{color:var(--amber);font-weight:600;letter-spacing:0}
.qd{color:var(--mute)}.qp{display:inline-block;min-width:44px;text-align:right;color:var(--amber);font-weight:600}
.qown{font-size:11.5px;color:var(--mute);margin-left:6px}
.how{font-size:13px;color:#4a5262;background:#f7f8fa;border-radius:6px;padding:6px 10px;margin:6px 0 8px}
.inote{background:#fff8e1;border:1px solid #f0d98a;border-radius:6px;padding:6px 10px;margin:0 0 8px;font-size:13px}.inote p{margin:2px 0}
.gbar{display:inline-block;width:70px;height:6px;background:#f1f2f5;border-radius:3px;margin-right:8px;vertical-align:1px;overflow:hidden}.gbar i{display:block;height:100%;background:#003DA5;border-radius:3px}
.gsw{display:inline-flex;border:1px solid var(--line);border-radius:6px;overflow:hidden;margin:2px 0 10px}.gsw button{font:inherit;font-size:12.5px;padding:4px 12px;border:0;background:#fff;color:var(--mute);cursor:pointer}
.gsw button+button{border-left:1px solid var(--line)}.gsw button.on{background:#EEF4FB;color:var(--ink);font-weight:600}.gsw button:focus-visible{outline:2px solid #003DA5;outline-offset:-2px}
.gx{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1.1fr) minmax(0,.8fr) minmax(0,.6fr) minmax(0,1.3fr);align-items:center;gap:8px;font-size:13.5px}
.gx .gn{color:var(--mute);text-align:center}.gx .gp{color:var(--amber);font-weight:600;text-align:right;white-space:nowrap}.gx .gt{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}.gx .gl{color:#4a5262}
.gxh{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);font-weight:600;padding:4px 0;border-bottom:1px solid var(--line)}.gxh .gn,.gxh .gp{color:var(--mute);font-weight:600}
div.gx0{padding:9px 0;border-bottom:1px solid var(--line)}div.gx0 .qn{font-weight:600}
details.q.gx{display:block}details.q.gx>summary{display:grid;grid-template-columns:inherit;gap:8px}details.q.gx>summary .qn{font-weight:600}
details.q.gx>summary{grid-template-columns:minmax(0,1.5fr) minmax(0,1.1fr) minmax(0,.8fr) minmax(0,.6fr) minmax(0,1.3fr)}
details.q.gx>.qb{padding-left:14px}
@media(max-width:560px){.gx .gn{display:none}.gx,details.q.gx>summary{grid-template-columns:minmax(0,1.4fr) minmax(0,1fr) minmax(0,.5fr) minmax(0,1.1fr)}.gbar{width:40px}}
.qsub{display:flex;justify-content:space-between;font-size:13px;font-weight:600;color:var(--ink);margin:14px 0 0}.qsub span{color:var(--amber)}
details.q.dep>summary .qn{font-style:italic;color:#4a5262}
.capl{margin-left:10px;color:var(--mute);text-decoration:underline;text-decoration-color:#CCCCCC}
.qtotal{display:flex;justify-content:space-between;padding:10px 0 2px;font-weight:600}
.snote{background:#EEF1F5;border-radius:8px;padding:8px 12px;margin:8px 0 0;font-size:14px}.snote p{margin:2px 0 0}
ol.nsl{list-style:none;margin:6px 0 10px;padding:0}
li.ns{display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--line)}li.ns:last-child{border-bottom:0}
.nsn{flex:none;width:26px;height:26px;border-radius:50%;background:#EEF4FB;color:var(--amber);font-weight:600;font-size:13.5px;display:flex;align-items:center;justify-content:center;margin-top:1px}
li.ns.counts .nsn{background:var(--amber);color:#fff}li.ns.house .nsn{background:#f1f2f5;color:var(--mute)}
li.ns>div{flex:1;min-width:0}.nst{font-size:15px;line-height:1.45}
.nsk{display:inline-block;font-size:11px;color:var(--mute);border:1px solid var(--line);border-radius:10px;padding:0 7px;margin-left:4px;vertical-align:1px;white-space:nowrap}
li.ns.counts .nsk{color:var(--amber);border-color:#B9D0EA}
li.ns p{font-size:13.5px;color:#4a5262;margin:3px 0 0}li.ns details.q{border:0;margin-top:2px}
.qb pre{font:12px/1.45 ui-monospace,Menlo,monospace;background:#F5F7FA;padding:8px 10px;border-radius:6px;white-space:pre-wrap}
.doc{border:1px solid var(--line);border-radius:8px;padding:4px 14px;font-size:13px;overflow-wrap:anywhere}
.doc h1{font-size:17px;margin:10px 0 6px}.doc h2{font-size:14.5px}.doc h3{font-size:13.5px}.doc table{font-size:12px;border-collapse:collapse}.doc td,.doc th{border:1px solid var(--line);padding:3px 6px}
.qb table{font-size:12.5px;border-collapse:collapse;width:100%}
table.chk td,table.rm td,table.axt td{padding:4px 6px;border-bottom:1px solid #EEF1F5;vertical-align:top}table.chk td.k,table.rm td.k{font-weight:600;white-space:nowrap;width:120px}
table.axt code{white-space:nowrap}table.axt td.r{color:var(--mute);white-space:nowrap;width:1%}table.axt td.w{white-space:nowrap;color:var(--mute)}table.axt a{word-break:break-all}
@media screen{.scroll{max-height:320px;overflow:auto}}
.st{display:inline-block;font-size:11px;border-radius:9px;padding:0 7px;margin-left:4px;white-space:nowrap}
.st.ok{background:#EEF4EC;color:#44693D}.st.bad{background:#fdecea;color:#9E2A2B}.st.na{background:#eef0f3;color:#4a5263}
.frames{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}.frames figure{margin:0}.frames img{width:100%;border-radius:4px;border:1px solid var(--line)}
.frames figcaption{font-size:11px;color:var(--mute);line-height:1.4}
.video{position:relative;aspect-ratio:16/10;border-radius:8px;overflow:hidden;background:#11151c;margin:0 0 6px}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.video .poster{display:none}
.dmeta{font-size:12px;color:var(--mute);margin:0 0 8px}.tr{font-size:13px;line-height:1.55;color:#2a303c}
svg text.v{font:600 10.5px -apple-system,Helvetica,Arial,sans-serif;fill:#002E5D}
svg text.ax{font:11px -apple-system,Helvetica,Arial,sans-serif;fill:#3d4452}svg text.ax2{font:9.5px -apple-system,Helvetica,Arial,sans-serif;fill:#8a93a3}
table.turnin{font-size:12px;margin:4px 0 6px}table.turnin th,table.turnin td{padding:5px 6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.apt{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:10px}.apt th{text-align:left;font-size:11.5px;color:var(--mute);font-weight:600;padding:4px 6px;border-bottom:1px solid var(--line)}
.apt td{padding:4px 6px;border:0;vertical-align:top}
.apt tr.apx td{position:sticky;top:0;z-index:2;font-size:14px;font-weight:700;color:var(--ink);background:#DCE6F2;
  padding:9px 10px;border:0;box-shadow:inset 0 -2px 0 #003DA5}
.apt tr.apg td{height:18px;padding:0;border:0}
.apt tr.apx span{font-size:12.5px;font-weight:400;color:#002E5D;margin-left:8px}
.apt tr.api td{font-size:13.5px;font-weight:600;color:var(--ink);padding:16px 6px 3px}
.apt tr.api span{font-size:12.5px;font-weight:400;color:var(--mute);margin-left:8px}
.apt td:first-child{padding-left:34px}.apt tr.apx td:first-child,.apt tr.api td:first-child{padding-left:10px}
a.bkn{color:inherit;text-decoration:none}a.bkn:hover,a.bkn:focus-visible{text-decoration:underline;text-decoration-color:#003DA5;text-underline-offset:3px}
a.bkc{display:inline-block;margin-left:6px;padding:0 6px;border-radius:999px;background:#F6F9FD;
  font-size:10.5px;font-weight:500;font-style:normal;line-height:16px;color:#003DA5;text-decoration:none;vertical-align:1px;white-space:nowrap}
a.bkc:hover,a.bkc:focus-visible{background:#DCE6F2;color:#002E5D}
.apt b{font-weight:400}.apt tr:not(.got) b{color:#7a8291}.apt tr.got b{color:var(--ink)}.apt tr.got .apd{color:var(--amber);font-weight:600}
.apt tr.ko b,.apt tr.ko .apd{color:var(--mute);font-style:italic}.apd{white-space:nowrap;color:var(--mute);font-size:12.5px;text-align:right}
.rfbs{display:inline-flex;gap:6px}.rfbn{display:inline-grid;place-items:center;width:2.1em;height:2.1em;border:1px solid var(--line);border-radius:8px;
 font-weight:600;color:var(--navy);text-decoration:none;background:#fff;transition:border-color .12s,background .12s}
.rfbn:hover,.rfbn:focus-visible{border-color:#003DA5;background:#F5F7FA;color:#003DA5}
.rfbw{display:inline-flex;flex-direction:column;gap:3px}
.rfbh{display:flex;justify-content:space-between;font-size:11.5px;color:var(--mute);white-space:nowrap}
.rfbn{cursor:pointer;position:relative}.rfbn input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}
.rfbn:has(input:checked){background:#003DA5;border-color:#003DA5;color:#fff}.rfbn:has(input:focus-visible){outline:2px solid #003DA5;outline-offset:2px}
.rfb textarea{display:block;width:100%;box-sizing:border-box;margin-top:10px;font:inherit;font-size:14px;color:var(--ink);padding:8px 10px;
 border:1px solid var(--line);border-radius:8px;background:#fff;resize:vertical;min-height:2.6em}
.rfb textarea:focus{outline:2px solid #003DA5;outline-offset:0;border-color:#003DA5}
.rfbhp{position:absolute;left:-9999px;width:1px;height:1px}
.rfbf{display:flex;align-items:center;justify-content:flex-end;gap:12px;margin-top:8px}
.rfbst{font-size:13px;color:var(--mute)}.rfbst.bad{color:#A3251B}.rfbst.ok{color:#1F6E43}
.rfbsend{font:600 .86rem/1.4 inherit;font-family:inherit;color:#fff;background:#003DA5;border:1px solid #003DA5;border-radius:8px;padding:.4em 1em;cursor:pointer;transition:background .12s,transform .06s}
.rfbsend:hover{background:#002E5D}.rfbsend:active{transform:translateY(1px)}.rfbsend:disabled{opacity:.6;cursor:default}
.coach{background:#fff;gap:2px;padding-top:10px;padding-bottom:10px}.cch{font-size:15px;font-weight:600;line-height:1.35}
.cchead{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.ccnote:empty{display:none}
.ccbtn{display:inline-flex;align-items:center;gap:.4em;padding:.3em .9em .3em .7em;font:600 .86rem/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;
  letter-spacing:.01em;color:#003DA5;background:#EEF4FB;border:1px solid #D3E1F1;border-radius:999px;cursor:pointer;transition:background .15s,border-color .15s}
.ccbtn:hover,.ccbtn:focus-visible{background:#E1ECF8;border-color:#B9D0EA}.ccbtn:focus-visible{outline:2px solid #003DA5;outline-offset:2px}
.ccbtn svg{flex:none;display:block}.ccbtn.ok{color:#2C7A4C;background:#E8F4EC;border-color:#B7DBC3}
.ccbtn.bad{color:#B03A3A;background:#FBEDED;border-color:#EBC5C5}.ccnote{font-size:12.5px;color:#B03A3A}
.ccbox{margin:2px 0 0}.ccbox>summary{cursor:pointer;font-size:12.5px;color:var(--mute);width:max-content}
.ccbox textarea{display:block;box-sizing:border-box;width:100%;max-width:100%;margin:6px 0 0;padding:8px 10px;border:1px solid var(--line);border-radius:8px;
  background:#F7F9FC;font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink);resize:vertical}
@media(prefers-reduced-motion:reduce){.ccbtn{transition:none}}
@media print{
 .ccbtn,.ccbox{display:none}
 details::details-content{content-visibility:visible;display:block}
 details>summary{break-after:avoid}
 .video iframe{display:none}.video{aspect-ratio:auto;background:none}.video .poster{display:block;position:relative}
 .video .poster img{width:100%;border-radius:8px}.scroll{max-height:none}
}
/* BYU brand (Strategy app tokens) and the 2026-10-29 layout: three text levels, point deductions, one Evidence drawer */
h1,h2,h3,h4,.qn,.qtitle,.smv,.cch,.dt,.nst{color:var(--navy)}
code,.qb pre,.dex{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace}
section.sec>h2{font-size:22px;font-weight:600;letter-spacing:-.01em;border-bottom:2px solid var(--navy);padding-bottom:6px}
.sml{color:var(--navy);letter-spacing:.08em}
.sm{border-radius:14px;box-shadow:0 2px 8px rgba(0,46,93,.06)}
.brand{margin:0 0 18px;padding:10px 14px;background:var(--navy);color:#fff;border-radius:10px;display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-size:13px}
.brand b{font-weight:600;letter-spacing:.08em;text-transform:uppercase;font-size:12px}.brand span{color:#B9D0EA}
#score>details.q>summary .qn{font-weight:600}
h3.sub,.ncx h3{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-size:16px;font-weight:600;margin:0 0 6px}
h3.sub small,.ncx h3 small{font-size:13px;font-weight:400;color:var(--mute)}
.deds{margin:22px 0 4px}.dnote{font-size:13px;color:var(--mute);margin:0 0 8px}
.ded{border:1px solid var(--line);border-radius:10px;margin:0 0 8px;padding:12px 14px}
.ded .dh{display:grid;grid-template-columns:38px 1fr auto;gap:10px;align-items:baseline}
.ded .dp{font-weight:700;color:#B3321C;font-variant-numeric:tabular-nums;font-size:15px}
.ded .dt{font-weight:600}.ded .dcat{display:block;font-weight:400;font-size:12.5px;color:var(--mute);margin-top:1px}
.dbtn{font-size:12.5px;border:1px solid #CCCCCC;background:#fff;border-radius:6px;padding:3px 10px;color:var(--navy);white-space:nowrap}
.dbtn:hover,.dbtn:focus-visible{border-color:var(--royal);color:var(--royal)}
.dst{font-size:12px;color:var(--mute);white-space:nowrap}.dst.ok{color:#44693D}
.dbtn[aria-expanded=true]{border-color:var(--royal);color:var(--royal);background:#F5F7FA}
.dform{margin:10px 0 2px 48px;padding:12px 14px;border:1px solid var(--line);border-radius:8px;background:#F5F7FA}
.dform[hidden]{display:none}
.dfl{display:block;font-weight:600;color:var(--navy);font-size:14px;margin:0 0 4px}.dfl span,.dfs span{font-weight:400;color:var(--mute);font-size:12.5px;margin-left:4px}
.dfs{display:block;font-size:13px;color:#4a5262;margin:8px 0 3px}
.dform textarea{display:block;width:100%;box-sizing:border-box;font:inherit;font-size:14px;color:var(--ink);padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;resize:vertical}
.dform textarea:focus{outline:2px solid #003DA5;outline-offset:0;border-color:#003DA5}
.dform textarea[name=why]{margin-bottom:12px}
.dform input[type=file]{font-size:13px}
.dff{display:flex;align-items:center;justify-content:flex-end;gap:10px;margin-top:12px}
.dfst{font-size:13px;color:var(--mute);margin-right:auto}.dfst.bad{color:#A3251B}
.dfcancel{font:inherit;font-size:13px;background:none;border:0;color:#4a5262;cursor:pointer;padding:.4em .6em}.dfcancel:hover{color:var(--ink)}
.dsent{margin:10px 0 2px 48px;font-size:13.5px;color:#44693D}
.ded .dx{margin:3px 0 0 48px;font-size:13.5px}.ded .dx p{margin:2px 0}.ded .rule{color:var(--mute)}.ded .fix b{font-weight:600}
.ded .inote{margin:8px 0 0 48px}.dex{white-space:pre-wrap;font-size:12px;background:#fff;border-radius:6px;padding:6px 8px;margin:4px 0 0}
.nsi{margin:0 0 8px;color:var(--mute);font-size:14px}
.evi{padding:8px 0 10px;border-top:1px solid #EEF1F5}.evi:first-child{border-top:0}
.evi h4{margin:2px 0 6px;font-size:14px;font-weight:600}.evi h4 small{font-weight:400;color:var(--mute);font-size:12.5px;margin-left:4px}
.doc{background:#F7F9FC;border-left:3px solid #E5E9EF}
.doc h1{font-size:14.5px;margin:10px 0 4px}.doc h2{font-size:13.5px;margin:10px 0 3px}.doc h3{font-size:13px}
.ncx{margin:18px 0 4px;border:1px solid var(--line);border-radius:10px;padding:12px 16px 4px;background:#F7F9FC}
.ncx>summary{display:block;list-style:none;cursor:pointer;padding-bottom:8px}.ncx>summary::-webkit-details-marker{display:none}
.ncx h3{margin:0}.ncx h3 small::after{content:" \\203A";display:inline-block;margin-left:6px;transition:transform .15s}
.ncx[open] h3 small::after{transform:rotate(90deg)}
.ncx .nci{margin:0 0 10px;font-size:13.5px;color:var(--mute)}
.ncg{border-top:1px solid var(--line);padding:10px 0 8px}.ncg .ngh{display:flex;justify-content:space-between;gap:12px;font-weight:600;font-size:13.5px;color:var(--navy)}
.ncg .ngh small{font-weight:400;color:var(--mute)}.ncg .fix{margin:2px 0 6px;font-size:13.5px}.ncg .fix b{color:var(--royal);font-weight:600}
.ncg ul{margin:0;padding:0;list-style:none}.ncg li{font-size:13.5px;padding:3px 0;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:baseline}
.ncg li .nm{font-weight:500}.ncg li .wh,.ncg li .why{color:var(--mute)}.ncg.later .ngh,.ncg.later .fix b{color:#44693D}
.mt{margin:18px 0 6px}.mt p{font-size:13.5px;color:#4a5262;margin:2px 0 8px}
.mtt{width:100%;border-collapse:collapse;font-size:13.5px}.mtt th{text-align:left;font-size:11.5px;color:var(--mute);font-weight:600;padding:4px 6px;border-bottom:1px solid var(--line)}
.mtt td{padding:6px;border-bottom:1px solid var(--line)}.mtt .num{font-variant-numeric:tabular-nums;white-space:nowrap}.mtt small{color:var(--mute)}
.lgx{color:inherit;text-decoration:none;cursor:pointer}.lgx:hover{color:var(--royal)}
.qfig svg polygon.exam{cursor:pointer;transition:opacity .15s}.qfig svg.hov polygon.exam:not(.on){opacity:.35}
.qfig{position:relative}.qfig svg polygon[data-s]{cursor:pointer;transition:opacity .15s}
.qfig svg.hov polygon[data-s]:not(.on),.qfig svg.hov polygon.core{opacity:.35}.qfig svg polygon.on{stroke:var(--navy);stroke-width:2}
.qfig svg text.axl{cursor:pointer}.qfig svg text.axl:hover{fill:var(--royal)}
.rtip{position:absolute;pointer-events:none;background:var(--navy);color:#fff;font-size:12.5px;line-height:1.45;padding:7px 10px;border-radius:7px;white-space:nowrap;transform:translate(-50%,-115%);opacity:0;transition:opacity .1s;text-align:left}
.rtip b{color:#F2CD00;font-weight:600}.rtip small{display:block;color:#B9D0EA;font-size:11.5px}
.lg{font:inherit;font-size:12px;color:var(--mute);background:none;border:1px solid transparent;border-radius:5px;padding:1px 6px 1px 0;cursor:pointer}.lg:hover{border-color:#CCCCCC;color:var(--navy)}
.rhint{font-size:12.5px;color:var(--mute);text-align:center;margin:2px 0 0}
details.gx.flash>summary{animation:flash 1.6s ease-out}@keyframes flash{0%,30%{background:#E1ECF8}100%{background:transparent}}
.sms.lost{display:block;margin-top:4px}
@media print{.dbtn,.rhint{display:none}.ncx{display:block}}
'''
