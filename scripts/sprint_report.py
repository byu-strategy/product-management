"""The student's sprint report (the "dossier"): one self-contained HTML page per student.

Called by sprint_feedback.py; not run on its own. One render, two copies: the student copy, and
Scott's copy, which adds a closed yellow "Instructor only" drawer at the top and, inside the score
drawers, the grader's reasons, the demo checks, the Loom stills and the transcript. Everything
else is identical, so what Scott reviews is what the student reads.

Layout (approved 2026-10-14, revised 2026-10-15): a sticky contents list on the left and open
sections: Summary (score, profile total, first next step, the hexagon), Score, Growth, Next steps,
Evidence reviewed, Questions, Methodology; Scott's copy adds Instructor notes first. Detail
(evidence, reasons, Loom stills) stays in <details>. Inline CSS and SVG, one small script that
highlights the current section, images embedded; printing hides the contents list.

Student-facing text here follows the course's feedback rules: second person, plain, literal, no
em dashes, and it never mentions lateness, how evidence was gathered, or the baseline survey.
"""
import base64, html, io, json, math, re, datetime as dt
from pathlib import Path

e = html.escape
HERE = Path(__file__).resolve().parent
CONCEPTS = HERE / "grading" / "concepts"
ASK_LINK = "https://slack.com/app_redirect?app=A0C2TDWPL4U&team=T097CK3UKB7"  # a DM with Course Monitor

# Flat-top hexagon, same positions as the course's builder profile charts.
AXES = ["Discovery", "Design", "Launch and Learn", "AI Systems", "Application Architecture", "Agentic Workflow"]
ANGLES = [-60, 0, 60, 120, 180, 240]
PRACTICE = {"AI Systems": 25.0}  # every other axis: 50 (builder_growth.py holds the same rule)
LEVELS = {1: "Followed", 2: "Directed", 3: "Decided", 4: "Delivered"}
LEVEL_TEXT = {  # from depth-levels.md, in the student's terms
    1: "work on the axis follows a template, a tutorial, or the agent's defaults",
    2: "you said specifically what to build and checked that it worked",
    3: "you challenged what the agent or the template proposed, weighed the options, and owned the trade-off, or found a problem yourself and fixed it with a judgment about the product",
    4: "people outside your team use it, and you changed the work because of what they did or said"}
# One amber ramp, light at the center to dark at the newest ring; a sprint keeps its color in every report.
SPRINT_COLORS = {1: "#f7d39c", 2: "#efb365", 3: "#e2933a", 4: "#c9761d", 5: "#a65d10", 6: "#80460a"}
CORE_COLOR = "#fcebd0"  # the starting core: the lightest step of the same amber ramp
SCALE = {1: "something you already knew how to do", 2: "mostly known, a few small gaps",
         3: "something new to learn, with a clear path", 4: "a lot to learn, and the path was not clear",
         5: "unclear whether it was possible at all"}
LABELS = {"plan": "Plan", "shipped": "Output", "review": "Report and retro", "demo": "Demo"}
RUBRIC = {
    "plan": "The Plan is scored for completion: a plan with all four fields (Goal, Why this, Done looks "
            "like, Predicted difficulty) earns 10.",
    "shipped": "Output is what you finished this sprint, judged against your plan as it stood at the end of "
               "the sprint and against how hard the work was. It counts when someone can check it: in a "
               "shared repo, at a link, or working in your demo. Great work on an ambitious goal earns full "
               "marks even when it falls a little short.",
    "review": "Your /sprint-review report and your retro. Full marks need every retro prompt answered and a "
              "response to something specific the report found. An empty retro earns at most half.",
    "demo": "The real thing, working, with real content, on Loom. Up to about two minutes costs nothing.",
}
CHECK_LABELS = {"on_screen": "On screen", "working": "Working", "real_content": "Real content",
                "reachable": "Reachable", "matches_plan": "Matches the plan", "off_demo": "Off the demo",
                "readable": "Readable"}
SKILLS_PASTE = ("Update my course skills from the class template. Download the latest "
                ".claude/skills/sprint-plan and .claude/skills/sprint-review folders from "
                "https://github.com/byu-strategy/builder-template (main branch) and replace mine with them. "
                "Do not change anything else. Then commit with the message \"Refresh course skills\" and push.")
README_PASTE = ("## Where the work lives\n\n- **Repos:** [owner/repo-name], [shared with sdmurff, or not shared]\n"
                "- **Live:** [the URL of the app, page, store listing, or file]\n"
                "- **Docs:** [links to Google Docs, Figma files, decks]")
TURNIN = """<table class=turnin>
<tr><th>Deliverable</th><th>Where it lives</th><th>How you turn it in</th><th>When</th><th>Points</th></tr>
<tr><td><b>Plan</b></td><td><code>sprints/sprint-N-plan.md</code></td><td>Commit it, and paste its GitHub link into <b>Sprint N Plan</b> on Canvas. To change it later, run <code>/sprint-plan</code> again; no resubmitting</td><td>First Wednesday, 11:59 PM</td><td>10</td></tr>
<tr><td><b>Output</b></td><td>What you finished, in any form: in your course repo, another repo, a link, or your demo</td><td>Nothing separate: list every place it lives under <b>Where the work lives</b> in your README</td><td>The Monday the sprint ends, 11:59 PM</td><td>20</td></tr>
<tr><td><b>Review</b></td><td><code>sprints/sprint-N-review.md</code>: the <code>/sprint-review</code> report, with your retro at the bottom</td><td>Commit it, and paste its GitHub link into <b>Sprint N Wrap-up</b> on Canvas</td><td>The Monday the sprint ends, 11:59 PM</td><td>10</td></tr>
<tr><td><b>Demo</b></td><td>Loom, 60 to 90 seconds</td><td>Paste the Loom share link into <b>Sprint N Wrap-up</b> on Canvas</td><td>The Monday the sprint ends, 11:59 PM</td><td>10</td></tr>
</table>"""


def fmt(x):
    return f"{round(float(x), 1):g}"


def practice_max(axis):
    return PRACTICE.get(axis, 50.0)


def load_concepts():
    """Every concept on every axis, in list order. Tolerates lists without knowledge_only."""
    out = {}
    for f in sorted(CONCEPTS.glob("*.json")):
        d = json.loads(f.read_text())
        out[d["axis"]] = {"items": d.get("items") or {}, "concepts": d.get("concepts") or []}
    return out


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
    for lvl in (25, 50, 75, 100):
        out.append(f'<polygon points="{poly([lvl] * 6)}" fill="none" stroke="{"#d5d9e0" if lvl == 100 else "#eceef2"}" '
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
    for s, vals in reversed(layers):  # outermost first, so each inner ring sits on top
        if vals:
            out.append(f'<polygon points="{poly(vals)}" fill="{SPRINT_COLORS.get(s, "#d97706")}" stroke="#fff" '
                       f'stroke-width=".8" stroke-linejoin="round"><title>Through Sprint {s}</title></polygon>')
    if any(core_vals):  # the survey center sits innermost, on top of the rings
        out.append(f'<polygon points="{poly(core_vals)}" fill="{CORE_COLOR}" stroke="#fff" stroke-width=".8" '
                   f'stroke-linejoin="round"><title>Your September survey</title></polygon>')
    if G and any(totals):  # a dot at every value, so a small value next to a zero still shows
        for i in range(6):
            if totals[i] > 0:
                x, y = pt(i, totals[i])
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#8a4a03" stroke="#fff" stroke-width="1"/>')
    for i, ax in enumerate(AXES):
        x, y = pt(i, 100)
        out.append(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="#d5d9e0" stroke-width=".7"/>')
        lx, ly = pt(i, 121)
        anchor = "start" if lx > CX + 5 else "end" if lx < CX - 5 else "middle"
        name = ax.replace("Application Architecture", "App Architecture")
        out.append(f'<text x="{lx:.1f}" y="{ly - 6:.1f}" text-anchor="{anchor}" font-size="12.5" fill="#1d2330">{e(name)}</text>')
        if G:
            out.append(f'<text x="{lx:.1f}" y="{ly + 10:.1f}" text-anchor="{anchor}" font-size="12.5" font-weight="700" '
                       f'fill="#b45f04">{round(totals[i])}</text>')
    out.append("</svg>")
    return "".join(out), [s for s, v in layers if v]


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
            out.append(f'<rect x="{cx - bw / 2:.1f}" y="{top + H - h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="#d97706"/>'
                       f'<text x="{cx:.1f}" y="{top + H - h - 4:.1f}" text-anchor="middle" class="v">{n}</text>')
        label = f"{d:%b} {d.day}" if i == 0 or d.day == 1 else str(d.day)
        out.append(f'<text x="{cx:.1f}" y="{top + H + 14}" text-anchor="middle" class="ax">{label}</text>'
                   f'<text x="{cx:.1f}" y="{top + H + 27}" text-anchor="middle" class="ax2">{d:%a}</text></g>')
    out.append(f'<line x1="0" x2="{W}" y1="{top + H}" y2="{top + H}" stroke="#d5d9e0"/></svg>')
    return "".join(out)


# ---------------------------------------------------------------- drawers

def row(title, right, body, cls=""):
    return (f'<details class="q {cls}"><summary><span class=qn>{title}</span><span class=qr>{right}</span></summary>'
            f'<div class=qb>{body}</div></details>')


def sub(title, right, body):
    return row(title, right, body, "s")


def big(title, right, body, cls=""):
    return (f'<details class="big {cls}"><summary><span class=bt>{title}</span><span class=br>{right}</span></summary>'
            f'<div class=bb>{body}</div></details>')


def inst_sub(title, right, body):
    """A drawer only Scott's copy has, marked so it is never mistaken for student text."""
    return row(f'{title} <span class=instag>instructor only</span>', right, body, "s inst")


# ---------------------------------------------------------------- the page

def render(r, p, row_, sprint, cats, final, *, plan_row=None, growth=None, scott=False,
           fairness=(), skills_status="", flags_withheld=()):
    """One student's report. `final(row, cat)` gives a category's score after overrides."""
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
        body = f"<p>{e(RUBRIC[c])}</p>"
        if c == "shipped":
            eff = (diff.get("effect_on_shipped") or "none").strip()
            m = re.match(r"raised by (\d+(?:\.\d+)?)", eff)
            if m:
                body += f"<p>How hard the work was raised this score by {m.group(1)} point{'s' * (m.group(1) != '1')}.</p>"
            elif eff.startswith("capped"):
                body += "<p>How hard the work was capped this score at 75% of the points.</p>"
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
            out += sub("What could not be reviewed", "", f"<p>{e(nr.get('detail') or nr.get('summary'))}</p>")
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
        out += sub("Where your work lives", f'{len(rr["listed"])} listed' if rr["has_section"] else "not listed", body)
        files = [x for x in p.get("shipped_files") or [] if x.get("path")]
        for o in p.get("other_repos") or []:
            files += [dict(x, _repo=o["repo"].replace("https://github.com/", "").strip("/")) for x in o.get("shipped_files") or []]
        if files:
            trs = "".join(
                f'<tr><td><a href="https://github.com/{e(x.get("_repo") or repo)}/blob/{e(x.get("first_commit") or "HEAD")}/{e(x["path"])}">'
                f'{e(x["path"])}</a></td><td class=r>{e(x.get("status") or "")}</td></tr>' for x in files)
            out += sub("Files added or changed", f"{len(files)}", f"<div class=scroll><table class=axt>{trs}</table></div>")
        imgs = []
        for x in p.get("shipped_files") or []:
            src = img_b64(x["image"], 480) if x.get("image") and Path(x["image"]).exists() else None
            if src:
                imgs.append(f'<figure><img src="{src}" alt="{e(x["path"])}"><figcaption>{e(x["path"])}</figcaption></figure>')
        if imgs:
            out += sub("Images from your work", f"{len(imgs)}", f'<div class=frames>{"".join(imgs)}</div>')
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
            out += sub("Commits", f"{len(crow)}", f'<div class=scroll><table class=axt>{"".join(crow)}</table></div>')
        text = (p.get("review") or {}).get("text")
        if text:
            out += sub("Your sprint review, as graded", "full report", f'<div class=doc>{md(text, repo)}</div>')
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
            return f"<p>{e(fb)}</p>" + how_scored(c) + "<!--DIFF-->" + output_evidence()
        if c == "review":
            return f"<p>{e(fb)}</p>" + how_scored(c) + "<!--DAYS-->" + review_evidence()
        if c == "demo":
            return demo_head() + f"<p>{e(fb)}</p>" + how_scored(c) + demo_scott()
        return f"<p>{e(fb)}</p>" + how_scored(c)

    kids = "".join(row(LABELS.get(c, label), f"{fmt(final(row_, c))}<small>/{mx}</small>", cat_body(c), "kid")
                   for c, label, mx in graded)
    days_late = f.get("canvas_days_late", 0) or 0
    wrap_canvas = review_total * (1 - min(100, 10 * days_late) / 100) if days_late else review_total
    if sprint == 1:
        total, total_max = review_total, review_max
        score_body = kids.replace('class="q kid"', 'class="q"')
        canvas = f"In Canvas: Sprint 1 {fmt(wrap_canvas)}/{review_max}."
    else:
        ps = str((plan_row or {}).get("score", "")).strip()
        plan_pts = float(ps) if ps else 0.0
        total, total_max = plan_pts + review_total, 10 + review_max
        if ps:
            when = (plan_row or {}).get("submitted_at") or ""
            plan_body = (f"<p>{e(RUBRIC['plan'])}</p>" + (f"<p class=qm>Turned in on Canvas {e(when)}.</p>" if when else "")
                         + (f"<p>Missing: {e(plan_row['fields_missing'])}.</p>" if (plan_row or {}).get("fields_missing") else ""))
            text = (p.get("plan_submission") or {}).get("text")
            if text:
                plan_body += f'<p class=qm>Your plan, as turned in:</p><div class="doc scroll">{md(text, repo)}</div>'
        else:
            plan_body = f"<p>No plan was turned in on Canvas for Sprint {sprint}.</p><p>{e(RUBRIC['plan'])}</p>"
        score_body = (row("Plan" + ("" if ps else " <span class=qown>not submitted</span>"),
                          f"{fmt(plan_pts)}<small>/10</small>", plan_body)
                      + kids.replace('class="q kid"', 'class="q"'))
        canvas = (f"In Canvas: Sprint {sprint} Plan {fmt(plan_pts)}/10 and Sprint {sprint} Wrap-up "
                  f"{fmt(wrap_canvas)}/{review_max}.")
    score_body += (f'<div class=qtotal><span>Sprint {sprint}</span><span>{fmt(total)}<small>/{total_max}</small></span></div>'
                   f'<p class=qm>{e(canvas)}</p>')
    note = (row_.get("scott_note") or "").strip()
    if note:
        score_body += f'<div class=snote><b>From Professor Murff</b><p>{e(note)}</p></div>'

    # ---- profile
    svg, drawn = profile_svg(G)
    if G:
        core_sw = (f'<span class=sw style="background:{CORE_COLOR}"></span>Your September survey '
                   if any(((G.get("start") or {}).get("points") or {}).values()) else "")
        sw = core_sw + "".join(f'<span class=sw style="background:{SPRINT_COLORS.get(s, "#d97706")}"></span>Sprint {s} ' for s in drawn)
        cap = f'{sw}<a href="#appendix" class=capl>How to read this</a>'
    else:
        cap = "Your builder profile is being prepared."

    # ---- how you grew: one table by axis, then this sprint's evidence by axis, then earlier sprints
    def pt(x):
        return str(round(float(x)))

    if G:
        last = (G.get("rings") or [{}])[-1]
        pts_now = last.get("points") or {}
        core = (G.get("start") or {}).get("points") or {}
        ptot = G.get("practice_total") or {}
        depth = {d["axis"]: d for d in G.get("depth") or [] if d.get("level")}
        best = G.get("depth_best") or {}
        by_axis = {}
        for m in G.get("new") or []:
            by_axis.setdefault(m["axis"], []).append(m)
        ctime = {c["sha"][:7]: c["when"] for c in (p.get("commits") or [])}
        order = sorted(AXES, key=lambda a: (-float(pts_now.get(a, 0)), AXES.index(a)))
        trs = ""
        for ax in order:
            tot = float(core.get(ax, 0)) + float(ptot.get(ax, 0))
            add = float(pts_now.get(ax, 0))
            lvl = best.get(ax, 0)
            trs += (f'<tr><td class=ga>{e(ax.replace("Application Architecture", "App Architecture"))}</td>'
                    f'<td class=gl>{f"{lvl} {LEVELS[lvl]}" if lvl else "<span class=qm>none yet</span>"}</td>'
                    f'<td class=gn>{len(by_axis.get(ax, [])) or ""}</td>'
                    f'<td class=gp>{"+" + pt(add) if round(add) else ""}</td>'
                    f'<td class=gt><span class=gbar><i style="width:{min(100, tot):.0f}%"></i></span>{pt(tot)}</td></tr>')
        grew = ('<table class=gtab><tr><th>Axis</th><th>Depth reached</th><th>New concepts</th><th>This sprint</th>'
                f'<th>Total of 100</th></tr>{trs}</table>')
        grew += '<div class=qax>This sprint</div>'
        any_now = False
        for ax in order:
            lst = sorted(by_axis.get(ax, []), key=lambda m: (when_key(m), ctime.get(str(m.get("ref", ""))[:7], "")), reverse=True)
            d = depth.get(ax)
            if not lst and not d:
                continue
            any_now = True
            grew += f'<div class=qsub>{e(ax)} <span>+{pt(pts_now.get(ax, 0))}</span></div>'
            if d:
                gain = d.get("gain")
                right = f'level {d["level"]}, {e(d.get("name") or LEVELS.get(d["level"], ""))}'
                if gain:
                    right += f'<span class=qp>+{pt(practice_max(ax) / 2 * (gain["to"] - gain["from"]) / 4)}</span>'
                body = f'<p>{e(d.get("why", ""))}</p><p class=qm>Level {d["level"]} means {LEVEL_TEXT.get(d["level"], "")}.</p>'
                if not gain and d.get("best_so_far", 0) >= d["level"]:
                    body += f'<p class=qm>You reached level {d["best_so_far"]} on this axis before, so this adds no points.</p>'
                grew += row("Depth", right, body, "dep")
            for m in lst:
                link = ref_link(repo, m.get("ref"))
                grew += row(e(m.get("name") or m["concept"]), f'<span class=qd>{e(short_date(m.get("when")))}</span>',
                            f'<p>{e(m.get("did", ""))}</p><p class=qm>{e(m.get("evidence", ""))}{" · " + link if link else ""}</p>')
        if not any_now:
            grew += "<p>No new concepts or depth were counted this sprint.</p>"
        earlier = G.get("earlier") or []
        for s_ in sorted({x["sprint"] for x in earlier}, reverse=True):
            xs = [x for x in earlier if x["sprint"] == s_]
            grew += f'<div class=qax>Sprint {s_} <span>+{pt(sum(float(x.get("points", 0)) for x in xs))}</span></div>'
            for ax in AXES:
                ax_x = [x for x in xs if x["axis"] == ax]
                if not ax_x:
                    continue
                grew += f'<div class=qsub>{e(ax)} <span>+{pt(sum(float(x.get("points", 0)) for x in ax_x))}</span></div>'
                for x in sorted(ax_x, key=lambda x: not x.get("depth")):
                    if x.get("depth"):
                        grew += row("Depth", f'level {x["level"]}, {e(x["name"])}<span class=qp>+{pt(x.get("points", 0))}</span>',
                                    f'<p>{e(x.get("why", ""))}</p>', "dep")
                    else:
                        link = ref_link(repo, x.get("ref"))
                        grew += row(e(x["name"]), f'<span class=qd>{e(short_date(x.get("when")))}</span>',
                                    f'<p>{e(x.get("did", ""))}</p><p class=qm>{e(x.get("evidence", ""))}{" · " + link if link else ""}</p>')
        nc = G.get("not_counted") or []
        if nc:
            grew += '<div class=qax>Work not counted</div>' + "".join(
                row(e(x.get("name") or x.get("concept", "")), "not counted",
                    (f'<p>{e(x["what"])}</p>' if x.get("what") else "") + f'<p class=qm>{e(str(x.get("why", "")).capitalize())}.</p>'.replace("..", "."),
                    "muted") for x in nc)
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
        diff_row = row("How hard it was", f'{diff["assessed"]} of 5',
                        lead + f'<p class=qm>On the course scale, {diff["assessed"]} is "{SCALE.get(int(diff["assessed"]), "")}".</p>')
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
        days_row = row("Day by day", f"{n_commits} commits", commit_strip(days, by_day))
    nv = rep.get("not_visible")
    if nv:
        nv = nv.strip().rstrip(".")
        nv_row = row("What the review could not see", "", f"<p>{e(nv[:1].upper() + nv[1:])}.</p>")
    score_body = score_body.replace("<!--DIFF-->", diff_row).replace("<!--DAYS-->", days_row + nv_row)

    # ---- next sprint steps: what keeps work from counting, then suggestions, then setup
    steps = []
    rr = readme_replay(p)
    if p.get("repo") and not rr["has_section"]:
        steps.append(("counts", 'Add a "Where the work lives" section to your README.',
                      "Only what is in your course repo, or listed there, can count toward your sprint. Add it below Context, one line per place.",
                      README_PASTE))
    for u in f.get("repos_named_but_not_shared") or []:
        steps.append(("counts", f"Share {e(u)} with sdmurff, or list it.",
                      "If you administer it, add <code>sdmurff</code> as a collaborator. If it belongs to a company you cannot "
                      "share, list it in your README, and <code>/sprint-review</code> will summarize its commits (dates and messages, never code).", ""))
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
        s_ = re.sub(r"^(\w+?)ing\b", lambda m: {"lett": "Let", "runn": "Run", "hav": "Have", "writ": "Write",
                                                 "shar": "Share", "us": "Use", "sav": "Save", "mak": "Make",
                                                 "mov": "Move", "giv": "Give", "tak": "Take", "includ": "Include",
                                                 "chang": "Change", "stor": "Store", "compar": "Compare",
                                                 "scor": "Score", "spreading": "Spread"}.get(m.group(1), m.group(1).capitalize()), s_)
        steps.append(("try", e(s_[0].upper() + s_[1:] + "."), "", ""))
    fmt_like = re.compile(r"\b(retro|README|review\.md|plan\.md|/sprint-plan|/sprint-review)\b", re.I)
    steps.sort(key=lambda st: {"try": 0 if not fmt_like.search(st[1]) else 2, "counts": 1}.get(st[0], 3))
    if skills_status in ("OLD", "missing"):
        steps.append(("house", "Update your course skills.",
                      "Your repo has an older <code>/sprint-plan</code>. Open Claude Code in your course repo and paste this.", SKILLS_PASTE))
    tag = {"counts": "so all your work counts", "try": "from your review", "house": "setup"}
    lis = ""
    for i, (k, t, d, code) in enumerate(steps, 1):
        body = (f"<p>{d}</p>" if d else "") + (sub("What to paste", "", f"<pre>{e(code)}</pre>") if code else "")
        lis += (f'<li class="ns {k}"><span class=nsn>{i}</span><div><div class=nst>{t} <span class=nsk>{tag[k]}</span></div>'
                f'{body}</div></li>')
    todo = (f"<ol class=nsl>{lis}</ol>" if lis else "<p>Nothing to fix: your repo and README are set.</p>")
    todo += sub("What you turn in, and how", "the four deliverables", TURNIN)
    next_n = sprint + 1

    # ---- questions
    ask = (f'<p>Message <a href="{ASK_LINK}">Course Monitor</a> in the course Slack. Say which part of this report you mean, '
           'and what you think it missed or got wrong.</p>'
           '<p>If the link does not open it, open Slack, search for <b>Course Monitor</b> (it is listed under Apps), and send it '
           'a message from its Messages tab. Please do not @mention it in the class channel, where everyone can see your '
           'question. Professor Murff reads every message sent there. Send grading questions only to Course Monitor: questions '
           'sent by email or anywhere else may be missed.</p>')

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
        each = practice_max(ax) / 2 / len(practicable) if practicable else 0
        ap_rows += (f'<tr class=apx><td colspan=2>{e(ax)} <span>practice up to {fmt(practice_max(ax))}; '
                    f'each concept {fmt(each)}</span></td></tr>')
        for c in cs:
            n_all += 1
            s_ = shown_in.get(c["id"])
            status = ("measured on the exams" if c.get("knowledge_only") else f"shown, Sprint {s_}" if s_ else "")
            item = CL[ax]["items"].get(c.get("item"), "")
            ap_rows += (f'<tr class="{"got" if s_ else ""}{" ko" if c.get("knowledge_only") else ""}"><td><b>{e(c["name"])}</b>'
                        f'{"<br><span class=qm>" + e(item) + "</span>" if item else ""}</td><td class=apd>{e(status)}</td></tr>')
    appendix = f"""
<p><b>What a spoke means.</b> Each of the six spokes runs from 0 to 100. 100 on every spoke is a full-stack product
builder. A spoke fills from two sources: practice, from your sprints, and knowledge, from the exams.</p>
<p><b>Reading the chart.</b> The lightest center is what you reported in the September survey; each ring outside it is one
sprint's practice, darker for later sprints. The midterm replaces the survey center with what you show on the exam.</p>
<p><b>Practice</b> fills up to 50 points on each spoke (25 on AI Systems, where the exams carry more of the weight). Half of
that is breadth and half is depth.</p>
<ul>
<li><b>Breadth</b> is the share of the axis's concepts, listed below, that your own work has shown. Each concept counts once:
showing it again in a later sprint adds nothing.</li>
<li><b>Depth</b> is the highest level you have worked at on the axis: 1 Followed ({LEVEL_TEXT[1]}), 2 Directed
({LEVEL_TEXT[2]}), 3 Decided ({LEVEL_TEXT[3]}), 4 Delivered ({LEVEL_TEXT[4]}). Each level is a quarter of the depth half,
and the highest level you have reached stays.</li>
</ul>
<p><b>Knowledge</b> fills the rest of each spoke from the exams. Concepts marked "measured on the exams" below count only there.</p>
<p><b>How a sprint is counted.</b> Each sprint, your work is checked twice, independently, against the concepts below. A
concept counts only when both checks find it in work you can point to: a commit or file in a shared repo, a shared Google
file, a live link, or a moment in your Loom. Depth uses the lower of the two levels. Work described only in your sprint
review or retro, work in a repo that is not shared, and anything the course gave you do not count; they appear under
"Work not counted" with the reason.</p>
<p><b>Your profile never goes down,</b> it is not graded, and it does not change your score.</p>
<table class=apt><tr><th>Concept</th><th>You</th></tr>{ap_rows}</table>"""

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
        if r.get("axes"):
            parts.append(f'<p><b>Axis split</b> {e(", ".join(f"{k} {round(v * 100)}%" for k, v in r["axes"].items()))}. {e(r.get("axes_why", ""))}</p>')
        if days_late:
            parts.append(f"<p><b>Late</b> {days_late} day(s) on Canvas: the Wrap-up shows {fmt(review_total)} here and "
                         f"{fmt(wrap_canvas)} in Canvas after its automatic deduction. The student copy shows only the Canvas number.</p>")
        parts.append("<p><b>Raw flags</b></p><ul>" + "".join(f"<li><code>{e(x)}</code></li>" for x in r.get("flags") or []) + "</ul>"
                     if r.get("flags") else "<p><b>Raw flags</b> none</p>")
        parts.append("<p><b>Fairness check</b></p><ul>" + "".join(f"<li>{e(x)}</li>" for x in fairness) + "</ul>"
                     if fairness else "<p><b>Fairness check</b> no findings for this student</p>")
        if G:
            dis = G.get("disputed") or []
            parts.append("<p><b>Disputed concepts</b> (one coder only, not counted; settle to add)</p><ul>" +
                         "".join(f'<li>{e(d.get("name", d.get("concept", "")))} ({e(d.get("concept", ""))}), coder {e(str(d.get("coder", "")))}: '
                                 f'{e(str(d.get("evidence", "")))}</li>' for d in dis) + "</ul>" if dis else
                         "<p><b>Disputed concepts</b> none</p>")
            dl = G.get("depth") or []
            if dl:
                parts.append("<p><b>Depth, the two coders</b></p><ul>" + "".join(
                    f'<li>{e(d["axis"])}: A {e(str((d.get("coder_levels") or [None, None])[0]))}, '
                    f'B {e(str((d.get("coder_levels") or [None, None])[1]))}, counted {e(str(d.get("level")))}</li>' for d in dl) + "</ul>")
        else:
            parts.append("<p><b>Builder profile</b> no growth file for this student yet.</p>")
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
        whole = sum(float(v) for v in core.values()) + sum(float(v) for v in (G.get("practice_total") or {}).values())
        added = sum(float(v) for v in ((G.get("rings") or [{}])[-1].get("points") or {}).values())
        prof_line = (f'<div class=sm><span class=sml>Builder profile</span><span class=smv>{round(whole)}<small> / 600</small></span>'
                     f'<span class=sms>+{round(added)} this sprint, {whole / 6:.0f}% of a full-stack product builder</span></div>')
    next_line = (f'<div class=sm><span class=sml>First step for Sprint {next_n}</span><span class=smt>{steps[0][1]}</span>'
                 f'<a class=sms href="#next">all {n_steps}</a></div>') if steps else ""
    parts_ = ([f"Plan {fmt(plan_pts)}"] if sprint > 1 else []) + [f"{LABELS.get(c, c)} {fmt(final(row_, c))}" for c, _l, _m in graded]
    summary = (f'<div class=smrow><div class=sm><span class=sml>Sprint {sprint} score</span>'
               f'<span class=smv>{fmt(total)}<small> / {total_max}</small></span><a class=sms href="#score">{" · ".join(parts_)}</a></div>'
               f'{prof_line}</div>{next_line}'
               f'<figure class=qfig>{svg}<figcaption>{cap}</figcaption></figure>')
    secs = []
    if band:
        secs.append(("inst", "Instructor notes", "not in the student copy", band, "inst"))
    secs += [
        ("summary", "Summary", "", summary, ""),
        ("score", "Score", f'{fmt(total)} / {total_max}', score_body, ""),
        ("grew", "Growth", grew_right, grew, ""),
        ("next", "Next steps", f'{n_steps} step{"s" * (n_steps != 1)}' if n_steps else "", todo, ""),
        ("questions", "Questions", "message Course Monitor", ask, ""),
        ("appendix", "Methodology", f"{n_all} concepts", appendix, "apxd"),
    ]
    short = {"score": f"{fmt(total)}/{total_max}", "grew": f"+{fmt(round(added))}" if G and added else "",
             "next": str(n_steps) if n_steps else ""}
    toc = "".join(f'<a href="#{i}" class="{c}"><span>{e(t)}</span><small>{short.get(i, "")}</small></a>'
                  for i, t, r_, _b, c in secs)
    body = "".join(f'<section id={i} class="sec {c}"><h2><span>{e(t)}</span><small>{r_}</small></h2>{b}</section>'
                   for i, t, r_, b, c in secs)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprint {sprint} Report · {e(full)}{" (" + copy + ")" if copy else ""}</title><style>{CSS}{TOC_CSS}</style></head><body>
<div class=layout>
<nav class=toc><div class=tocname>Sprint {sprint} Report<br><b>{e(full)}</b><br><span>{e(due_txt)}</span></div>{toc}</nav>
<main>
<header class=qh><span class=qtitle>Sprint {sprint} Report · {e(full)}</span><span>{e(due_txt)}</span></header>
<details class=tocm><summary>Contents</summary>{toc}</details>
{body}
</main></div>
<script>
// Contents list, two levels: each section, and inside it the things a reader looks for (score
// categories, axes, next steps, evidence rows, appendix axes). Second levels collapse; the section
// being read opens its own. Clicking an item inside a closed drawer opens the drawer.
(()=>{{
const nav=document.querySelector('nav.toc');
const pick={{score:':scope>details.q',grew:':scope>.qax',next:':scope>ol.nsl>li.ns',appendix:'tr.apx'}};
const label=el=>{{
  if(el.matches('details'))return el.querySelector('summary .qn').textContent;
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
    let t=label(el).trim().replace(/\s+/g,' ');const v=el.querySelector('.video');if(v&&v.closest('details')===el)t+=' (video)';
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
</script>
</body></html>"""


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
.tw{position:absolute;left:4px;top:6px;width:16px;height:20px;border:0;background:none;cursor:pointer;padding:0}
.tw::before{content:"";display:block;width:5px;height:5px;border-right:1.5px solid var(--mute);border-bottom:1.5px solid var(--mute);transform:rotate(-45deg);margin:6px 0 0 4px;transition:transform .15s}
.tg.open .tw::before{transform:rotate(45deg)}
.sub{display:none;margin:0 0 6px}.tg.open .sub{display:block}
nav.toc .sub a{font-size:12.5px;padding:3px 10px 3px 30px;color:var(--mute);border-left:2px solid var(--line)}
nav.toc .sub a:hover{color:var(--ink)}
.tocbar{display:flex;gap:6px;margin:0 0 12px}.tocbar button{font:12px inherit;font-family:inherit;color:#4a5262;background:#f5f6f8;border:1px solid var(--line);border-radius:6px;padding:3px 9px;cursor:pointer}.tocbar button:hover{color:var(--ink);border-color:#d5d9e0}
.tg3{position:relative}.tw3{position:absolute;left:16px;top:3px;width:14px;height:18px;border:0;background:none;cursor:pointer;padding:0}
.tw3::before{content:"";display:block;width:4px;height:4px;border-right:1.5px solid var(--mute);border-bottom:1.5px solid var(--mute);transform:rotate(-45deg);margin:6px 0 0 4px;transition:transform .15s}
.tg3.open .tw3::before{transform:rotate(45deg)}
.sub3{display:none}.tg3.open .sub3{display:block}
nav.toc .sub3 a{font-size:12px;padding:2px 10px 2px 44px}
main .qh{display:none}.tocm{display:none}
section.sec{padding:8px 0 22px;border-bottom:1px solid var(--line);scroll-margin-top:16px}
section.sec>h2{display:flex;justify-content:space-between;align-items:baseline;gap:14px;font-size:19px;margin:18px 0 10px}
section.sec>h2 small{font-size:13.5px;color:var(--mute);font-weight:400;font-variant-numeric:tabular-nums}
section.inst{background:#fff8e1;border:1px solid #e8c766;border-radius:10px;padding:4px 18px 14px;font-size:12.5px}
section.inst>h2{font-size:15px;color:#7a5a00}
section.apxd>h2{font-size:16px;color:#4a5262}
.smrow{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.sm{border:1px solid var(--line);border-radius:10px;background:#fbfbfc;padding:12px 16px;display:flex;flex-direction:column;gap:2px;margin-bottom:12px}
.sml{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute);font-weight:600}
.smv{font-size:28px;font-weight:600;line-height:1.2}.smv small{font-size:.55em;color:var(--mute);font-weight:500}
.sms{font-size:12.5px;color:var(--amber)}.smt{font-size:15px;line-height:1.45}
@media (max-width:900px){.layout{display:block}nav.toc{display:none}main .qh{display:flex}
 .tocm{display:block;border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:0 0 12px}.tocm summary{cursor:pointer;font-weight:600}}
@media print{nav.toc,.tocm,script{display:none}.layout{display:block;padding:0}main .qh{display:flex}}
'''

CSS = '''
:root{--ink:#1d2330;--mute:#7a8394;--line:#eceef2;--amber:#b45f04}
body{font:15px/1.6 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--ink);max-width:640px;margin:28px auto 80px;padding:0 22px}
a{color:#2f5bd3;text-decoration:none}
code{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;background:#f3f4f7;padding:0 3px;border-radius:3px}
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
details.big.score{border:1px solid var(--line);border-radius:10px;background:#fbfbfc}
details.big.score>summary{padding:16px 18px;align-items:center}details.big.score>.bb{padding:0 18px 16px 41px}
details.big.score .bt{font-size:12.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute)}
details.big.inst{background:#fff8e1;border:1px solid #e8c766;border-radius:10px;margin:0 0 16px;font-size:12.5px}
details.big.inst>summary{padding:10px 16px}details.big.inst .bt{font-size:14px}details.big.inst>.bb{padding:0 16px 12px}
.igrid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:4px 0 8px}.inst ul{margin:2px 0 8px;padding-left:18px}.inst p{margin:6px 0}.ihow{color:#7a5a00}
details.big.apxd .bt{font-size:15px;color:#4a5262}
details.q{border-bottom:1px solid var(--line)}details.q>summary{list-style:none;display:flex;justify-content:space-between;gap:12px;padding:9px 0;cursor:pointer}
details.q>summary::-webkit-details-marker{display:none}
details.q>summary .qn::after{content:"";display:inline-block;width:5px;height:5px;border-right:1.5px solid var(--mute);border-bottom:1.5px solid var(--mute);transform:rotate(-45deg);margin-left:8px;vertical-align:2px;transition:transform .15s}
details.q[open]>summary .qn::after{transform:rotate(45deg)}
details.q>summary:focus-visible,details.big>summary:focus-visible{outline:2px solid #2f5bd3;outline-offset:2px}
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
.gtab{width:100%;border-collapse:collapse;font-size:13.5px;margin:4px 0 6px}.gtab th{text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute);font-weight:600;padding:4px 6px;border-bottom:1px solid var(--line)}
.gtab td{padding:7px 6px;border-bottom:1px solid #f3f4f6}.gtab .ga{font-weight:600}.gtab .gl{color:#4a5262}.gtab .gn{color:var(--mute);text-align:center}
.gtab .gp{color:var(--amber);font-weight:600;text-align:right;white-space:nowrap}.gtab .gt{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.gbar{display:inline-block;width:70px;height:6px;background:#f1f2f5;border-radius:3px;margin-right:8px;vertical-align:1px;overflow:hidden}.gbar i{display:block;height:100%;background:#e2933a;border-radius:3px}
.qsub{display:flex;justify-content:space-between;font-size:13px;font-weight:600;color:var(--ink);margin:14px 0 0}.qsub span{color:var(--amber)}
details.q.dep>summary .qn{font-style:italic;color:#4a5262}
.capl{margin-left:10px;color:var(--mute);text-decoration:underline;text-decoration-color:#d5d9e0}
.qtotal{display:flex;justify-content:space-between;padding:10px 0 2px;font-weight:600}
.snote{background:#f3f4f7;border-radius:8px;padding:8px 12px;margin:8px 0 0;font-size:14px}.snote p{margin:2px 0 0}
ol.nsl{list-style:none;margin:6px 0 10px;padding:0}
li.ns{display:flex;gap:14px;padding:12px 0;border-bottom:1px solid var(--line)}li.ns:last-child{border-bottom:0}
.nsn{flex:none;width:26px;height:26px;border-radius:50%;background:#fdf1e2;color:var(--amber);font-weight:600;font-size:13.5px;display:flex;align-items:center;justify-content:center;margin-top:1px}
li.ns.counts .nsn{background:var(--amber);color:#fff}li.ns.house .nsn{background:#f1f2f5;color:var(--mute)}
li.ns>div{flex:1;min-width:0}.nst{font-size:15px;line-height:1.45}
.nsk{display:inline-block;font-size:11px;color:var(--mute);border:1px solid var(--line);border-radius:10px;padding:0 7px;margin-left:4px;vertical-align:1px;white-space:nowrap}
li.ns.counts .nsk{color:var(--amber);border-color:#f3d3a8}
li.ns p{font-size:13.5px;color:#4a5262;margin:3px 0 0}li.ns details.q{border:0;margin-top:2px}
.qb pre{font:12px/1.45 ui-monospace,Menlo,monospace;background:#f5f6f8;padding:8px 10px;border-radius:6px;white-space:pre-wrap}
.doc{border:1px solid var(--line);border-radius:8px;padding:4px 14px;font-size:13px;overflow-wrap:anywhere}
.doc h1{font-size:17px;margin:10px 0 6px}.doc h2{font-size:14.5px}.doc h3{font-size:13.5px}.doc table{font-size:12px;border-collapse:collapse}.doc td,.doc th{border:1px solid var(--line);padding:3px 6px}
.qb table{font-size:12.5px;border-collapse:collapse;width:100%}
table.chk td,table.rm td,table.axt td{padding:4px 6px;border-bottom:1px solid #f0f2f5;vertical-align:top}table.chk td.k,table.rm td.k{font-weight:600;white-space:nowrap;width:120px}
table.axt code{white-space:nowrap}table.axt td.r{color:var(--mute);white-space:nowrap;width:1%}table.axt td.w{white-space:nowrap;color:var(--mute)}table.axt a{word-break:break-all}
@media screen{.scroll{max-height:320px;overflow:auto}}
.st{display:inline-block;font-size:11px;border-radius:9px;padding:0 7px;margin-left:4px;white-space:nowrap}
.st.ok{background:#e6f4ea;color:#1e6b34}.st.bad{background:#fdecea;color:#a1271b}.st.na{background:#eef0f3;color:#4a5263}
.frames{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}.frames figure{margin:0}.frames img{width:100%;border-radius:4px;border:1px solid var(--line)}
.frames figcaption{font-size:11px;color:var(--mute);line-height:1.4}
.video{position:relative;aspect-ratio:16/10;border-radius:8px;overflow:hidden;background:#11151c;margin:0 0 6px}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}.video .poster{display:none}
.dmeta{font-size:12px;color:var(--mute);margin:0 0 8px}.tr{font-size:13px;line-height:1.55;color:#2a303c}
svg text.v{font:600 10.5px -apple-system,Helvetica,Arial,sans-serif;fill:#1d2330}
svg text.ax{font:11px -apple-system,Helvetica,Arial,sans-serif;fill:#3d4452}svg text.ax2{font:9.5px -apple-system,Helvetica,Arial,sans-serif;fill:#8a93a3}
table.turnin{font-size:12px;margin:4px 0 6px}table.turnin th,table.turnin td{padding:5px 6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.apt{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:10px}.apt th{text-align:left;font-size:11.5px;color:var(--mute);font-weight:600;padding:4px 6px;border-bottom:1px solid var(--line)}
.apt td{padding:6px 6px;border-bottom:1px solid #f3f4f6;vertical-align:top}.apt tr.apx td{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);font-weight:600;padding-top:16px}
.apt tr.apx span{text-transform:none;letter-spacing:0;font-weight:400;margin-left:6px}
.apt tr:not(.got) b{font-weight:500;color:#4a5262}.apt tr.got b{color:var(--ink)}.apt tr.got .apd{color:var(--amber);font-weight:600}
.apt tr.ko b{color:var(--mute)}.apd{white-space:nowrap;color:var(--mute);font-size:12.5px;text-align:right}
@media print{
 details::details-content{content-visibility:visible;display:block}
 details>summary{break-after:avoid}
 .video iframe{display:none}.video{aspect-ratio:auto;background:none}.video .poster{display:block;position:relative}
 .video .poster img{width:100%;border-radius:8px}.scroll{max-height:none}
}
'''
