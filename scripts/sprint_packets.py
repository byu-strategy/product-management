"""Build one grading packet per student for a sprint.

Run from the courses hub (so the Canvas token in .env.local is found):

    python3 ~/courses/product-management/scripts/sprint_packets.py --sprint 1 [--only netid ...]

A packet is everything a grader needs to score one student's sprint, gathered without a model:
the Canvas submission, the plan as committed on day one and as it stands now, the
/sprint-review report, the README, the sprint's commits and what they added, and the Loom's
length, summary, and transcript. Facts that code can check exactly (timestamps, whether the
retro is filled in, whether the demo is a Loom) are computed here and handed to the grader as
facts, so the model judges quality and never has to work out a date.

Writes ~/hubs/courses/_data/product-management/grading/sprint-N/<net_id>.json. Student data
goes only to _data, never to git. This file holds no student data.
"""
import argparse, base64, csv, html, json, re, subprocess, sys, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import requests, tempfile

sys.path.insert(0, str(Path.home() / ".claude/skills/canvas-lms/scripts"))
from canvas_client import CanvasAPI, load_config
from sprint_config import COURSE_ID, PLAN_FIELDS, PLAN_POINTS, SPRINTS

TZ = ZoneInfo("America/Denver")
DATA = Path.home() / "hubs/courses/_data/product-management"
SHIPPED_CHARS = 40_000      # code text per packet, about 10k tokens (written work has its own budget)
PER_FILE_CHARS = 10_000     # written work (specs, decisions, discovery, evals, docs): long enough for acceptance criteria
CODE_FILE_CHARS = 6_000     # code: enough to see what it does (3,000 cut off tool loops and error handling)
# Course-provided skills and the sprint plan and review files (read separately) are skipped; a skill
# the student wrote is their work (W2), and so is anything else they put in sprints/.
SKIP = re.compile(r"^(sprints/sprint-\d+-(plan|review)\.md$|\.claude/skills/(eli5|learn|sprint-plan|sprint-review)/|README\.md$)|000-.*template"
                  r"|(^|/)(node_modules|dist|build|\.next|out|coverage|\.vercel)/"
                  r"|(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|bun\.lockb)$|\.(min\.js|min\.css|map)$")
# Written work is read first, so a large code change cannot use up the budget before the specs,
# decision records, discovery notes and evals the student wrote.
WRITTEN = re.compile(r"\.(md|qmd|txt)$|(^|/)(specs|decisions|discovery|evals|prompts|docs|research|gtm|learning)/", re.I)
WRITTEN_CHARS = 100_000     # written work and code have separate budgets, so neither crowds out the other
# Small files that say a lot about how the app is built (schema, row-level security, secrets kept out
# of the repo, hooks and agent settings, tests, deploy config). Read before other code, on their own
# budget, so a large feature cannot crowd them out (agreement test, 2026-10-15).
SIGNAL = re.compile(r"(^|/)(migrations|supabase|prisma|tests?|__tests__|\.claude/(hooks|agents|commands))/|\.sql$|"
                    r"(^|/)(\.gitignore|\.env\.example|\.env\.sample|\.mcp\.json|CLAUDE\.md|vercel\.json|"
                    r"middleware\.[jt]s|schema\.prisma|\.claude/settings(\.local)?\.json)$|\.(test|spec)\.[jt]sx?$", re.I)
SIGNAL_CHARS = 20_000
CORE = re.compile(r"(^|/)(llm|agents?|tools?|prompts?|models?|claude|openai|anthropic|chat|ai|api|routes?|server|handlers?|actions?|lib)(?=[\w-]*(/|\.[jt]sx?$|\.py$))", re.I)
SIGNAL_FILE_CHARS = 3_000
TEXT = re.compile(r"\.(md|txt|py|js|jsx|ts|tsx|html|css|json|csv|yml|yaml|toml|sql|qmd|prisma)$|(^|/)\.(gitignore|env\.example|env\.sample)$", re.I)



def path_or_branch(r, text):
    """True when an owner/name match is really a folder path or a git branch, not a repo."""
    esc = re.escape(r)
    as_path = re.search(rf"(?i)(?<!github\.com/)(?<![\w.-]){esc}/[\w.-]", text) or \
        re.search(rf"(?i)(?<!github\.com)/{esc}\b", text)
    as_branch = re.search(rf"(?i)(?:branch|PR\s*#?\d+)\W{{1,4}}`?{esc}\b|\b{esc}`?\)?\s+branch", text) or \
        re.search(rf"(?i)\b(?:on|from|into|merged?)\s+`?{esc}`?[^.\n]{{0,25}}\b(?:main|master)\b", text)
    return bool(as_path or as_branch or r.split("/")[0] in {"discovery", "interviews", "supabase", "agents", "claude",
                                                             "social", "codex", "cursor", "copilot", "chore", "wip"})


def private_bare_repos(text):
    """Repo names given without an owner and called private: "`elders-quorum-web`, private GitHub repo"."""
    pat = (r"`([\w.-]+)`\s*[,(]?\s*(?:a\s+)?private(?: GitHub| company)? repo"
           r"|private(?: GitHub| company)? repo(?:sitory)?,?\s+`([\w.-]+)`")
    return sorted({(a or b).lower() for a, b in re.findall(pat, text, re.I)
                   if "/" not in (a or b) and "." not in (a or b)[-5:]})

def local(iso):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ)


def wait_for_rate_limit(stderr):
    """GitHub allows 5,000 API calls an hour. Hitting the limit used to return None, which reads as a
    missing file; now the build waits for the reset and the caller retries."""
    if "rate limit" not in (stderr or "").lower():
        return False
    import time
    reset = subprocess.run(["gh", "api", "rate_limit", "--jq", ".resources.core.reset"], capture_output=True, text=True).stdout.strip()
    wait = max(30, int(reset or 0) - int(time.time()) + 5) if reset.isdigit() else 300
    print(f"GitHub rate limit reached; waiting {wait // 60} min", flush=True)
    time.sleep(wait)
    return True


def gh(path, jq=None):
    cmd = ["gh", "api", path] + (["--jq", jq] if jq else [])
    p = subprocess.run(cmd, capture_output=True, text=True)
    while p.returncode and wait_for_rate_limit(p.stderr):
        p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        return None
    return p.stdout if jq else json.loads(p.stdout)


def gh_list(path):
    """Every item of a paginated list endpoint, not just the first 100."""
    cmd = ["gh", "api", "--paginate", path, "--jq", ".[] | tojson"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    while p.returncode and wait_for_rate_limit(p.stderr):
        p = subprocess.run(cmd, capture_output=True, text=True)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()] if p.returncode == 0 else []


def file_at(repo, path, ref=None):
    q = f"repos/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
    c = gh(q, ".content")
    return base64.b64decode(c).decode("utf-8", "replace") if c else None


def history(repo, path):
    """Commits touching path, oldest first: [(sha, local datetime)]."""
    log = gh_list(f"repos/{repo}/commits?path={path}&per_page=100")
    return [(c["sha"], local(c["commit"]["author"]["date"])) for c in reversed(log)]


def has_field(text, name):
    """A plan field with something after it, bold or not ("**Goal:** x" or "Goal: x")."""
    return bool(re.search(rf"{re.escape(name)}\s*\**\s*:\s*\**\s*\S", text or "", re.I))


def plain(html_text):
    t = re.sub(r"<(br|/p|/li|/div)[^>]*>", "\n", html_text or "")
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def field(text, name):
    m = re.search(rf"\*\*{name}:\*\*\s*(.*?)(?=\n\s*\n\*\*|\n\*\*|\Z)", text or "", re.S)
    return m.group(1).strip() if m else ""


def loom(url):
    m = re.search(r"loom\.com/(?:share|embed)/([0-9a-f]{32})", url or "")
    if not m:
        return None
    vid = m.group(1)
    out = {"url": f"https://www.loom.com/share/{vid}"}
    o = requests.get("https://www.loom.com/v1/oembed", params={"url": out["url"]}, timeout=30)
    if o.ok:
        d = o.json()
        out |= {"title": d.get("title"), "seconds": round(d.get("duration") or 0),
                "loom_summary": d.get("description")}
    page = requests.get(out["url"], headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text
    # oEmbed reports the raw recording; a trimmed Loom plays shorter. Viewers see playable_duration.
    pd = re.search(r'"playable_duration":([\d.]+)', page)
    if pd:
        out["seconds"] = round(float(pd.group(1)))
    ch = re.search(r'"chapters":"((?:[^"\\]|\\.)*)"', page)
    out["chapters"] = json.loads(f'"{ch.group(1)}"') if ch else None
    cap = re.search(r'"captions_source_url":"([^"]+)"', page)
    if cap:
        vtt = requests.get(json.loads(f'"{cap.group(1)}"'), timeout=30).text
        lines = [re.sub(r"</?v[^>]*>", "", l) for l in vtt.splitlines()
                 if l.strip() and l != "WEBVTT" and "-->" not in l and not l.strip().isdigit()]
        out["transcript"] = " ".join(lines)
    else:
        st = re.search(r'"transcription_status":"(\w+)"', page)
        out["transcript"] = None
        out["transcript_status"] = st.group(1) if st else "unknown"
    return out


def grab_frames(video, dest_dir, net_id, n=9, width=1568):
    """n full-resolution frames from a local video file, evenly spaced, one JPEG each.

    The transcript says what the student said; the frames show what was on screen. Each frame
    is 1568 px wide, the largest a model reads without shrinking it, so terminal and document
    text stays legible (about 2k tokens a frame). Only the frames are kept, next to the packet."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    for old in dest_dir.glob(f"{net_id}-[0-9]*.jpg"):  # video frames only, not artifact images
        old.unlink()
    out = []
    secs = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout or 90)
    for i in range(n):
        at = secs * (i + 0.5) / n
        dest = dest_dir / f"{net_id}-{i + 1}.jpg"
        if subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{at:.2f}", "-i", str(video),
                           "-frames:v", "1", "-vf", f"scale='min({width},iw)':-2", "-q:v", "2",
                           str(dest)]).returncode == 0 and dest.exists():
            dest.chmod(0o600)
            out.append({"at_seconds": round(at), "path": str(dest)})
    return out or None


def frames(vid, dest_dir, net_id):
    """Frames from a Loom, by its id. The video goes to a temp file and is deleted."""
    r = requests.post(f"https://www.loom.com/api/campaigns/sessions/{vid}/transcoded-url",
                      json={}, timeout=30)
    try:
        url = r.json().get("url") if r.ok else None
    except ValueError:  # Loom sometimes answers with an HTML page (rate limit, removed video)
        url = None
    if not url:
        return None
    with tempfile.NamedTemporaryFile(suffix=".mp4") as mp4:
        mp4.write(requests.get(url, timeout=300).content)
        mp4.flush()
        return grab_frames(mp4.name, dest_dir, net_id)


def other_video(url, dest_dir, net_id):
    """Sprint 1 allowed any video host. Pull frames and captions the same way through yt-dlp
    (YouTube, public Drive files, direct video links). Anything private or behind a login
    (most SharePoint links) fails and is reported as such, for Scott to watch."""
    out = {"url": url}
    with tempfile.TemporaryDirectory() as tmp:
        p = subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", "mp4/bestvideo[height<=1080]+bestaudio/best",
                            "--merge-output-format", "mp4", "--write-auto-subs", "--write-subs",
                            "--sub-langs", "en.*", "--sub-format", "vtt", "--print", "after_move:%(duration)s",
                            "-o", f"{tmp}/v.%(ext)s", url], capture_output=True, text=True, timeout=600)
        vids = [f for f in Path(tmp).glob("v.*") if f.suffix in (".mp4", ".webm", ".mkv", ".mov")]
        if not vids:
            out["error"] = (p.stderr.strip().splitlines() or ["could not download"])[-1][:200]
            return out
        try:
            out["seconds"] = round(float(p.stdout.strip().splitlines()[-1]))
        except (ValueError, IndexError):
            pass
        subs = sorted(Path(tmp).glob("v*.vtt"))
        if subs:
            lines, seen = [], set()
            for l in subs[0].read_text(errors="replace").splitlines():
                l = re.sub(r"<[^>]+>", "", l).strip()
                if l and l != "WEBVTT" and "-->" not in l and not l.isdigit() and l not in seen \
                        and not l.startswith(("Kind:", "Language:")):
                    seen.add(l)
                    lines.append(l)
            out["transcript"] = " ".join(lines)
        out["frames"] = grab_frames(vids[0], dest_dir, net_id)
    return out


def canvas_video(file_id, dest_dir, net_id):
    """A video uploaded straight into the Canvas submission (an embedded recording or an attached
    file), not a link. Missed until 2026-10-20: one Sprint 1 demo, uploaded on time, scored 0
    because only links were read. Frames as for any video; the transcript comes from Whisper,
    since Canvas uploads have no captions. The video goes to a temp file and is deleted."""
    cfg = load_config()
    base = cfg["url"].rstrip("/").replace("/api/v1", "")
    H = {"Authorization": f"Bearer {cfg['token']}"}
    meta = requests.get(f"{base}/api/v1/files/{file_id}", headers=H, timeout=30)
    if not meta.ok:
        return {"url": f"{base}/files/{file_id}", "error": f"Canvas file {file_id}: HTTP {meta.status_code}"}
    m = meta.json()
    out = {"url": f"{base}/courses/{COURSE_ID}/files/{file_id}", "title": m.get("display_name"),
           "uploaded_at": m.get("created_at")}
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp) / "v.mp4"
        v.write_bytes(requests.get(m["url"], headers=H, timeout=600).content)
        try:
            out["seconds"] = round(float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                capture_output=True, text=True).stdout))
        except ValueError:
            out["error"] = "not a readable video"
            return out
        out["frames"] = grab_frames(v, dest_dir, net_id)
        w = subprocess.run(["whisper", str(v), "--model", "small", "--language", "en", "--output_format", "txt",
                            "--output_dir", tmp], capture_output=True, text=True, timeout=1800)
        t = Path(tmp) / "v.txt"
        out["transcript"] = t.read_text().strip() if t.exists() else None
        if not t.exists():
            out["transcript_status"] = (w.stderr.strip().splitlines() or ["whisper failed"])[-1][:200]
    return out


def check_link(url):
    """Does a shipped link load? Status, final URL, and page title; no judgment."""
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
        m = re.search(r"<title[^>]*>(.*?)</title>", r.text[:20000], re.S | re.I)
        return {"url": url, "status": r.status_code, "final_url": r.url,
                "title": html.unescape(m.group(1).strip())[:120] if m else None}
    except requests.RequestException as ex:
        return {"url": url, "status": None, "error": type(ex).__name__}


DOCS = re.compile(r"\.(docx|pptx|pdf|xlsx)$", re.I)
IMAGES = re.compile(r"\.(png|jpe?g|webp|gif)$", re.I)


def raw(repo, path, ref=None):
    """A file's bytes, any size up to GitHub's 100 MB, private repos included."""
    cmd = ["gh", "api", "-H", "Accept: application/vnd.github.raw",
           f"repos/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")]
    p = subprocess.run(cmd, capture_output=True)
    while p.returncode and wait_for_rate_limit(p.stderr.decode("utf-8", "replace")):
        p = subprocess.run(cmd, capture_output=True)
    return p.stdout if p.returncode == 0 else None


def doc_text(name, data):
    """Readable text from a Word, PowerPoint, PDF, or Excel file, so a deck or a model is judged
    on what it says, not skipped as a binary."""
    import io, zipfile
    ext = name.lower().rsplit(".", 1)[-1]
    try:
        if ext == "docx":
            # Read the XML directly: no dependency (an unrelated "docx" package shadows python-docx here).
            xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8", "replace")
            paras = ["".join(html.unescape(t) for t in re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", para))
                     for para in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)]
            return "\n".join(x for x in paras if x.strip())
        if ext == "pptx":
            z = zipfile.ZipFile(io.BytesIO(data))
            slides = sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                            key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[1]).group(1)))
            return "\n".join(f"[slide {k}] " + " ".join(html.unescape(x) for x in
                             re.findall(r"<a:t>([^<]*)</a:t>", z.read(s).decode("utf-8", "replace")))
                             for k, s in enumerate(slides, 1))
        if ext == "pdf":
            import fitz
            doc = fitz.open(stream=data, filetype="pdf")
            return f"[{doc.page_count} pages]\n" + "\n".join(pg.get_text() for pg in doc)
        if ext == "xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True, read_only=True)
            out = []
            for ws in wb.worksheets:
                out.append(f"[sheet {ws.title}]")
                for row in ws.iter_rows(max_row=40, values_only=True):
                    if any(v is not None for v in row):
                        out.append(" | ".join("" if v is None else str(v) for v in row[:15]))
            return "\n".join(out)
    except Exception as ex:
        return f"[could not read {ext}: {type(ex).__name__}]"
    return ""


def shipped(repo, commits, budget=SHIPPED_CHARS, image_dir=None, net_id=None, max_images=3, cutoff=None):
    """Files added or changed by the sprint's commits, with capped text for the grader. Text files,
    Word, PowerPoint, PDF, and Excel are read; up to three images (mockups, charts, screenshots
    of the work) are saved for the grader to look at.

    Each file is read as of the last commit at or before `cutoff` that touched it (`as_of`), so work
    done after the sprint never shows up as this sprint's. A file touched only after the cutoff is
    listed with `after_window` and no text."""
    files, first, last = {}, {}, {}
    for c in commits:
        inside = cutoff is None or dt.datetime.fromisoformat(c["when"]) <= cutoff
        for f in (gh(f"repos/{repo}/commits/{c['sha']}") or {}).get("files", []):
            name = f["filename"]
            if SKIP.search(name):
                continue
            if f["status"] == "removed":
                if inside:
                    files.pop(name, None)
                    last.pop(name, None)
                continue
            files[name] = f["status"]
            # The first commit in the window that touched the file, so a spec can be checked
            # as written before the code it describes (commit order, not file dates).
            first.setdefault(name, (c["sha"][:7], c["when"]))
            if inside:
                last[name] = c["sha"]
    out, images = [], 0
    budgets = {"written": WRITTEN_CHARS * budget // SHIPPED_CHARS, "signal": SIGNAL_CHARS, "code": budget}
    caps = {"written": PER_FILE_CHARS, "signal": SIGNAL_FILE_CHARS, "code": CODE_FILE_CHARS}
    kind = lambda n: "written" if WRITTEN.search(n) or DOCS.search(n) else "signal" if SIGNAL.search(n) else "code"
    rank = {"written": 0, "signal": 1, "code": 2}
    # Within code, the files that hold the product's logic come before UI and boilerplate.
    core = lambda n: 0 if CORE.search(n) else 1
    order = sorted(files, key=lambda n: (rank[kind(n)], core(n), first[n][1]))
    for name in order:
        status, k = files[name], kind(name)
        item = {"path": name, "status": status, "first_commit": first[name][0], "first_when": first[name][1]}
        ref = last.get(name)
        if not ref:
            item["after_window"] = True
            out.append(item)
            continue
        item["as_of"] = ref[:7]
        text = None
        if TEXT.search(name) and budgets[k] > 0:
            # One API call per file is slow on big repos, so fetch only files whose text fits the budget.
            meta = gh(f"repos/{repo}/contents/{name}?ref={ref}") or {}
            item["bytes"] = meta.get("size")
            if meta.get("content"):
                text = base64.b64decode(meta["content"]).decode("utf-8", "replace")
        elif DOCS.search(name) and budgets[k] > 0:
            data = raw(repo, name, ref)
            if data:
                item["bytes"] = len(data)
                text = doc_text(name, data)
        elif IMAGES.search(name) and image_dir and images < max_images:
            data = raw(repo, name, ref)
            if data:
                image_dir.mkdir(parents=True, exist_ok=True)
                src = image_dir / f"{net_id}-art-{images + 1}{Path(name).suffix.lower()}"
                dest = src.with_suffix(".jpg")
                src.write_bytes(data)
                ok = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-vf",
                                     "scale='min(1568,iw)':-2", "-q:v", "3", str(dest)]).returncode == 0
                if src != dest:
                    src.unlink(missing_ok=True)
                if ok:
                    dest.chmod(0o600)
                    item["image"] = str(dest)
                    images += 1
        if text:
            take = min(caps[k], budgets[k])
            item["text"] = text[:take] + ("\n[... truncated]" if len(text) > take else "")
            budgets[k] -= len(item["text"])
        out.append(item)
    return out


def build(student, sub, plan_sub, cfg, due):
    net_id, repo_url = student["net_id"], student.get("repo_url", "")
    body = sub.get("body") or ""
    links = [h for h in re.findall(r'href="([^"]+)"', body) + re.findall(r"https?://[^\s<\"]+", body)
             if "instructure" not in h]
    links = list(dict.fromkeys(links))
    loom_links = [l for l in links if "loom.com" in l]
    p = {"net_id": net_id, "name": student["name"], "preferred_first": student["preferred_first"],
         "canvas_user_id": student["canvas_user_id"],
         "canvas": {"submitted_at": sub.get("submitted_at") and local(sub["submitted_at"]).isoformat(),
                    "late": sub.get("late"), "seconds_late": sub.get("seconds_late") or 0,
                    "links": links},
         "repo": repo_url or None, "facts": {}}
    f = p["facts"]
    f["canvas_submitted"] = bool(sub.get("submitted_at"))
    f["canvas_late"] = bool(sub.get("late"))
    f["demo_is_loom"] = bool(loom_links)
    f["non_loom_video"] = [l for l in links if re.search(r"drive\.google|youtu|sharepoint|clickup|vimeo", l)]
    f["canvas_video"] = list(dict.fromkeys(
        re.findall(r"media_attachments_iframe/(\d+)", body)
        + [str(a["id"]) for a in sub.get("attachments") or []
           if str(a.get("content-type") or "").startswith("video") or a.get("mime_class") == "video"]))

    if repo_url:
        repo = repo_url.replace("https://github.com/", "").strip("/")
        n = cfg["sprint"]
        plan_path, review_path = f"sprints/sprint-{n}-plan.md", f"sprints/sprint-{n}-review.md"
        ph, rh = history(repo, plan_path), history(repo, review_path)
        # A student who keeps the sprint in a second repo links its plan or review on Canvas
        # (dspring1 and jr115534 in Sprint 2). When the course repo has no review, read that repo's.
        review_repo = repo
        if not rh:
            for r in dict.fromkeys(re.findall(r"github\.com/([\w.-]+/[\w.-]+)/blob/", " ".join(links))):
                r = r.removesuffix(".git")
                if r.lower() == repo.lower():
                    continue
                r_rh = history(r, review_path)
                if r_rh:
                    review_repo, rh = r, r_rh
                    r_ph = history(r, plan_path)
                    if r_ph and not ph:  # the whole sprint lives there: plan, README and commits too
                        repo, ph = r, r_ph
                    p["sprint_repo"] = f"https://github.com/{r}"
                    break
        # The window closes at the due date, or at the Canvas submission when that came later (the late
        # policy is applied separately). Plan, review, README and every file are read as of then.
        at = sub.get("submitted_at")
        cutoff = max(due, local(at)) if at else due

        def as_of(path, hist=None, in_repo=None):
            in_repo = in_repo or repo
            hist = history(in_repo, path) if hist is None else hist
            inside = [sha for sha, t in hist if t <= cutoff]
            return file_at(in_repo, path, inside[-1]) if inside else (file_at(in_repo, path) if not hist else None)

        plan_first = file_at(repo, plan_path, ph[0][0]) if ph else None
        plan_now = as_of(plan_path, ph)
        review = as_of(review_path, rh, review_repo)
        readme = as_of("README.md") or ""
        f["edited_after_window"] = [x for x, h in (("plan", ph), ("review", rh)) if any(t > cutoff for _, t in h)]
        at_due = [sha for sha, t in ph if t <= due]
        p["plan"] = {"first_commit": ph[0][1].isoformat() if ph else None, "commits": len(ph),
                     "as_committed_day_one": plan_first, "now": plan_now,
                     # Only when it was edited after the due date; otherwise it equals "now".
                     "at_due_date": file_at(repo, plan_path, at_due[-1]) if at_due and any(t > due for _, t in ph) else None}
        p["review"] = {"first_commit": rh[0][1].isoformat() if rh else None, "commits": len(rh),
                       "text": review}
        # Commits run to today, so a late submitter's packet can hold the next sprint's work too.
        # The next sprint's plan lets the grader credit only work that serves this sprint's plan.
        next_plan = file_at(repo, f"sprints/sprint-{n + 1}-plan.md")
        p["next_sprint_plan"] = next_plan[:4000] if next_plan else None
        p["readme"] = readme[:4000]
        start = ph[0][1] if ph else due - dt.timedelta(days=14)
        log = gh_list(f"repos/{repo}/commits?since={start.astimezone(dt.timezone.utc).isoformat()}&per_page=100")
        commits = [{"sha": c["sha"], "when": local(c["commit"]["author"]["date"]).isoformat(),
                    "after_due": local(c["commit"]["author"]["date"]) > due,
                    "author": (c.get("author") or {}).get("login") or c["commit"]["author"]["name"],
                    "message": c["commit"]["message"].strip()[:1500]} for c in reversed(log)]
        p["commits"] = [{k: v for k, v in c.items() if k != "sha"} | {"sha": c["sha"][:7]} for c in commits]
        p["window_end"] = cutoff.isoformat()
        for c in p["commits"]:
            c["after_window"] = dt.datetime.fromisoformat(c["when"]) > cutoff
        p["shipped_files"] = shipped(repo, commits, image_dir=cfg["out"] / "frames", net_id=net_id, cutoff=cutoff)

        f["plan_committed"] = bool(ph)
        # A change is an edited Goal or Done line, or a section added during the sprint that updates
        # the plan ("## Scope update (Oct 6)", "## October 12 amendment", "**Amended done looks like:**").
        change_head = re.compile(r"^\s*(?:#+\s*|\*\*)[^\n]*\b(chang|amend|updat|revis|scope)\w*", re.I | re.M)
        added = {x.group(0).strip() for x in change_head.finditer(plan_now or "")} - \
                {x.group(0).strip() for x in change_head.finditer(plan_first or "")}
        added = {a for a in added if "Only if the plan changes" not in a}
        f["plan_changed_during_sprint"] = bool(ph) and (bool(added) or any(
            field(plan_first, k) != field(plan_now, k) for k in ("Goal", "Done looks like")))
        # "**Changes:**" from /sprint-plan, or a hand-written "**Change (Oct 6):**" with a reason.
        # The template's own placeholder line does not count.
        f["plan_change_noted"] = bool(ph) and bool(added) or any(
            "Only if the plan changes" not in m.group(0) for m in
            re.finditer(r"^\s*(?:#+\s*|\*\*)Changes?\b[^\n]*?:?\**\s*\S[^\n]*", plan_now or "", re.I | re.M))
        m = re.search(r"\*\*Where to see it:\*\*\s*(.+)", readme)
        f["readme_where_to_see_it"] = m.group(1).strip() if m and "[URL" not in m.group(1) else None
        # Sprint 1 put the retro at the end of the plan file. From Sprint 2 it is the "Your retro"
        # section at the bottom of the review file, five prompts the student answers.
        old_style = all(field(plan_now, k) for k in ("Actual difficulty", "Why it differed", "Retro"))
        m = re.search(r"##\s*Your retro\s*(.*)", review or "", re.S)
        answered = ""
        if m:
            answered = re.sub(r"\*Written by you.*?\*|\*\*[^*]+\?\*\*|\*\*Actual difficulty:\*\*|"
                              r"Yes, partly, or no, and one sentence on why\.|One or two things from the report above"
                              r" that you didn't expect\s+or would not have noticed yourself\.|Skip if it didn't\.|"
                              r"1 to 5, and one sentence on why it differed from the difficulty you\s+predicted\.|"
                              r"One specific thing\.", "", m.group(1), flags=re.S)
        f["retro_location"] = "review file" if m else "plan file" if old_style else None
        f["retro_filled"] = old_style or len(re.sub(r"\s+", " ", answered).strip()) > 120
        f["review_committed"] = bool(rh)
        f["review_on_time"] = bool(rh) and rh[0][1] <= due
        f["review_edited_after_first_commit"] = len(rh) > 1
        m = re.search(r"\*\*Window:\*\*\s*\S+\s+to\s+(\S+)", review or "")
        f["review_window_end"] = m.group(1) if m else None
        m = re.search(r"## Context\n(.*?)(?=\n## |\Z)", readme, re.S)
        f["readme_context_filled"] = bool(m) and not re.search(r"\[(the hats you wear|your product, or your part|the customer or segment|the specific person)", m.group(1), re.I)
        f["commits_after_due"] = sum(c["after_due"] for c in commits)
        f["plan_edited_after_due"] = any(t > due for _, t in ph)
    else:
        f["repo_found"] = False

    # The plan's 10 points: completion, computed here. Sprint 1's plan was the first commit of the
    # plan file; from Sprint 2 on it is the Plan assignment's Canvas submission.
    if cfg["plan"] is None:
        plan_text = (p.get("plan") or {}).get("as_committed_day_one")
        first = (p.get("plan") or {}).get("first_commit")
        p["plan_submission"] = {"source": "repo, first commit", "submitted_at": first, "text": plan_text}
        plan_due = dt.datetime.fromisoformat(cfg["plan_due"]).replace(second=59, tzinfo=TZ)
        on_time = bool(first) and dt.datetime.fromisoformat(first) <= plan_due
        # Syllabus late policy, 10% of the category per day or part of a day. From Sprint 2 on,
        # Canvas applies it to the Plan assignment itself; Sprint 1's plan was a commit, so here.
        late_s = (dt.datetime.fromisoformat(first) - plan_due).total_seconds() if first else 0
        f["plan_days_late"] = max(0, -(-int(late_s) // 86400))
    else:
        from plan_grades import plan_from_submission
        plan_text, how = plan_from_submission(plan_sub.get("body"), cfg["sprint"], plan_sub.get("submitted_at")) if plan_sub.get("submitted_at") else ("", "")
        at = plan_sub.get("submitted_at")
        p["plan_submission"] = {"source": f"Canvas ({how})" if how else "Canvas",
                                "submitted_at": at and local(at).isoformat(), "text": plan_text or None}
        on_time = bool(at) and not plan_sub.get("late")
    missing = [k for k in PLAN_FIELDS if not has_field(plan_text, k)] if plan_text else list(PLAN_FIELDS)
    f["plan_submitted"] = bool(plan_text)
    f["plan_on_time"] = on_time
    f["plan_fields_missing"] = missing
    f["plan_score"] = PLAN_POINTS if plan_text and not missing else 0
    if cfg["plan"] is None and f["plan_score"]:
        f["plan_score"] = max(0, PLAN_POINTS - f.get("plan_days_late", 0))
    f["canvas_days_late"] = -(-int(p["canvas"]["seconds_late"]) // 86400) if sub.get("late") else 0

    p["loom"] = loom(loom_links[0]) if loom_links else None
    if p["loom"]:
        f["loom_seconds"] = p["loom"].get("seconds")
        vid = p["loom"]["url"].rsplit("/", 1)[1]
        p["loom"]["frames"] = frames(vid, cfg["out"] / "frames", net_id)
    elif f["canvas_video"] and cfg["sprint"] == 1:
        v = canvas_video(f["canvas_video"][0], cfg["out"] / "frames", net_id)
        p["loom"] = v | {"host": "not Loom"}
        f["loom_seconds"] = v.get("seconds")
        f["other_video_readable"] = bool(v.get("frames"))
    elif f["non_loom_video"] and cfg["sprint"] == 1:
        v = other_video(f["non_loom_video"][0], cfg["out"] / "frames", net_id)
        p["loom"] = v | {"host": "not Loom"}
        f["loom_seconds"] = v.get("seconds")
        f["other_video_readable"] = bool(v.get("frames"))

    # Links a grader would otherwise have to take on faith: everything on Canvas that is not the
    # demo or a GitHub page, and the README's "Where to see it".
    targets = [l for l in links if "loom.com" not in l and "github.com" not in l
               and l not in f["non_loom_video"] and "localhost" not in l]
    if f.get("readme_where_to_see_it", "") and str(f["readme_where_to_see_it"]).startswith("http"):
        targets.append(f["readme_where_to_see_it"].split()[0].strip("<>()"))
    # Work often lives outside the course repo: a company repo, a second project. Read every
    # other repo the student has shared with sdmurff (they own it, or listed or linked it), and
    # check every live link in the README's "Where the work lives" section.
    readme_text = p.get("readme") or ""
    m = re.search(r"## Where the work lives\n(.*?)(?=\n## |\Z)", readme_text, re.S)
    where = m.group(1) if m else ""
    text = (where + " " + " ".join(links) + " " + ((p.get("plan") or {}).get("now") or "") + " " +
            ((p.get("review") or {}).get("text") or ""))
    named = {re.sub(r"\.git$", "", u.lower().rstrip(".")) for u in re.findall(r"github\.com/([\w.-]+/[\w.-]+)", text)}
    # The review report names repos bare ("Spencer24601/RememberMe"); take those under the student's own account.
    if student.get("github_username"):
        named |= {u.lower().rstrip(".") for u in
                  re.findall(rf"(?<![\w/.-])({re.escape(student['github_username'])}/[\w.-]+)", text, re.I)}
    # Repos named bare under any owner ("`Sisk-Labs/echo`", "private repo Sisk-Labs/echo"); kept only
    # if the owner is a real GitHub account and the name is not a file path.
    # Model names (`openai/gpt-oss-120b`) and branches (`prod/main`, `origin/feature-x`) look the same,
    # so known model publishers, git remotes and branch prefixes are skipped.
    not_repo = re.compile(r"^(openai|anthropic|meta-llama|mistralai|google|qwen|deepseek-ai|groq|x-ai|xai|cohere|"
                          r"huggingface|nvidia|microsoft|moonshotai|origin|upstream|prod|production|staging|dev|"
                          r"feature|feat|fix|hotfix|release|refs|heads)/|/(main|master|develop|dev|head)$", re.I)
    bare = {r for r in set(re.findall(r"`([\w-]+/[\w.-]+)`", text)) |
            set(re.findall(r"\brepo(?:sitory)?\W{1,4}`?([\w-]+/[\w.-]+)", text, re.I)) if not not_repo.search(r)}
    for r in bare:
        r = r.lower().rstrip(".")
        if r in named or "." in r.split("/")[1][-6:] or r.split("/")[0] in {"src", "app", "docs", "specs", "sprints", "product", "lib",
                                                                          "api", "public", "decisions", "design", "test", "tests"}:
            continue
        if gh(f"users/{r.split('/')[0]}"):
            named.add(r)
    course = (repo_url or "").replace("https://github.com/", "").strip("/").lower()
    mine = {r for r, owner in cfg["shared"].items() if owner.lower() == (student.get("github_username") or "#").lower()}
    others = [r for r in cfg["shared"] if r.lower() != course and (r in mine or r.lower() in named)]
    # A repo the student names that is not shared with sdmurff may still be public: read it if so.
    shared_lower = {r.lower() for r in cfg["shared"]}
    for r in sorted(named - shared_lower - {course}):
        info = gh(f"repos/{r}")
        if info and not info.get("private"):
            others.append(info["full_name"])
    start = dt.datetime.fromisoformat(p["plan"]["first_commit"]) if (p.get("plan") or {}).get("first_commit") \
        else due - dt.timedelta(days=14)
    p["other_repos"] = []
    for r in others[:4]:
        log = gh_list(f"repos/{r}/commits?since={start.astimezone(dt.timezone.utc).isoformat()}&per_page=100")
        cs = [{"sha": c["sha"], "when": local(c["commit"]["author"]["date"]).isoformat(),
               "after_due": local(c["commit"]["author"]["date"]) > due,
               "author": (c.get("author") or {}).get("login") or c["commit"]["author"]["name"],
               "message": c["commit"]["message"].strip()[:1500]} for c in reversed(log)]
        p["other_repos"].append({"repo": f"https://github.com/{r}",
                                 "commits": [{k: v for k, v in c.items() if k != "sha"} | {"sha": c["sha"][:7]} for c in cs],
                                 "files": shipped(r, cs, budget=20_000, cutoff=p.get("window_end") and
                                                  dt.datetime.fromisoformat(p["window_end"])) if cs else []})
    unshared = sorted(r for r in named - shared_lower - {course} - {o.lower() for o in others} if not path_or_branch(r, text))
    # A private repo named without its owner ("`elders-quorum-web`, private GitHub repo") still needs a share line.
    for b in private_bare_repos(text):
        if not any(b == u.split("/")[-1] for u in set(unshared) | shared_lower | {o.lower() for o in others} | {course}):
            unshared.append(b)
    f["repos_named_but_not_shared"] = unshared
    # Every live link anywhere in the README, not only the "Where the work lives" section: students
    # put them under Live:, Where to see it, or in prose, and an unchecked link is our gap, not theirs.
    targets += [u.rstrip(").,>]*_'\"") for u in re.findall(r"https?://[^\s)\]>\"'`]+", readme_text)
                if "github.com" not in u and "loom.com" not in u and "shields.io" not in u]
    p["link_checks"] = [check_link(u) for u in dict.fromkeys(targets)]
    p["baseline"] = cfg["baseline"].get(net_id)

    # Google Docs, Sheets, Slides, and Drive files can't be read from here: they are fetched through
    # the Drive connector (signed in as aifoundry.byu@gmail.com) by drive_fill.py before grading.
    sources = " ".join(links) + " " + where + " " + ((p.get("review") or {}).get("text") or "") + " " + \
        ((p.get("plan") or {}).get("now") or "")
    google = {}
    for u in re.findall(r"https?://(?:docs|drive)\.google\.com/[^\s)\"'<>\]]+", sources):
        m = re.search(r"/d/([\w-]{20,})|[?&]id=([\w-]{20,})", u)
        if m:
            google.setdefault(m.group(1) or m.group(2), u)
    p["google_links"] = [{"file_id": k, "url": v} for k, v in google.items()]
    return trim_after_window(p)


def trim_after_window(p):
    """Work after the window is set aside by every reader, so the packet keeps only what it takes to say
    so (a count, the dates, a few commit subjects, the paths) instead of every commit and file. Cut the
    largest packets by more than half (mckayw23 carried 370 commits after his window)."""
    end = p.get("window_end")
    if not end:
        return p
    cut = dt.datetime.fromisoformat(end)

    def split(commits, files):
        late = [c for c in commits if dt.datetime.fromisoformat(c["when"]) > cut]
        keep = [c for c in commits if dt.datetime.fromisoformat(c["when"]) <= cut]
        late_files = [f["path"] for f in files if f.get("after_window")]
        summary = None
        if late or late_files:
            summary = {"commits": len(late), "first": late[0]["when"][:10] if late else None,
                       "last": late[-1]["when"][:10] if late else None,
                       "subjects": [c["message"].split("\n")[0][:100] for c in late[:15]],
                       "files": len(late_files), "paths": late_files[:25]}
        return keep, [f for f in files if not f.get("after_window")], summary

    p["commits"], p["shipped_files"], p["after_window"] = split(p.get("commits") or [], p.get("shipped_files") or [])
    for o in p.get("other_repos") or []:
        o["commits"], o["files"], o["after_window"] = split(o.get("commits") or [], o.get("files") or [])
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    cfg = SPRINTS[a.sprint] | {"sprint": a.sprint}

    api = CanvasAPI(*[load_config()[k] for k in ("url", "token")], COURSE_ID)
    # The class due date, not one bent by an extension: with overrides present, Canvas otherwise
    # reports an override's date (a single extension moved Sprint 1's to Oct 7 for everyone).
    assignment = api.get(f"/assignments/{cfg['review']}", params={"override_assignment_dates": "false"})
    class_due = local(assignment["due_at"])
    # Extensions: a student's own due date, which also bounds what counts as late work for them.
    extended = {}
    for o in api.get_all(f"/assignments/{cfg['review']}/overrides"):
        if o.get("due_at") and o.get("student_ids"):
            extended.update({str(sid): local(o["due_at"]) for sid in o["student_ids"]})
        elif o.get("course_section_id"):
            print(f"warning: section override '{o.get('title')}' is not applied; due dates use the class date")
    subs = {str(s["user_id"]): s for s in
            api.get_all(f"/assignments/{cfg['review']}/submissions")}
    plan_subs = {str(s["user_id"]): s for s in
                 api.get_all(f"/assignments/{cfg['plan']}/submissions")} if cfg["plan"] else {}
    roster = list(csv.DictReader(open(DATA / "roster-msb341-fall2026.csv")))
    repos = {r["net_id"]: r for r in csv.DictReader(open(DATA / "github-roster.csv"))}

    out = DATA / f"grading/sprint-{a.sprint}"
    out.mkdir(parents=True, exist_ok=True)
    cfg["out"] = out
    # Every repo shared with sdmurff, owner by name, and each student's baseline axis scores.
    listing = subprocess.run(["gh", "api", "user/repos?affiliation=collaborator&per_page=100", "--paginate",
                              "--jq", ".[] | [.full_name, .owner.login] | @tsv"], capture_output=True, text=True).stdout
    cfg["shared"] = dict(l.split("\t") for l in listing.splitlines() if "\t" in l)
    bl = DATA / "baseline-charts-fall2026/students.json"
    cfg["baseline"] = {s["net_id"]: s["means"] for s in json.loads(bl.read_text())} if bl.exists() else {}
    for s in roster:
        if a.only and s["net_id"] not in a.only:
            continue
        s = s | {"repo_url": repos.get(s["net_id"], {}).get("repo_url", ""),
                 "github_username": repos.get(s["net_id"], {}).get("github_username", "")}
        due = extended.get(str(s["canvas_user_id"]), class_due)
        p = build(s, subs.get(str(s["canvas_user_id"]), {}),
                  plan_subs.get(str(s["canvas_user_id"]), {}), cfg, due)
        p["assignment"] = {"id": cfg["review"], "name": assignment["name"],
                           "points": assignment["points_possible"], "due": due.isoformat(),
                           "extended": due != class_due}
        (out / f"{s['net_id']}.json").write_text(json.dumps(p, indent=1))
        (out / f"{s['net_id']}.json").chmod(0o600)
        print(f"{s['net_id']:10} {len(json.dumps(p)) // 4:>6} tokens  "
              f"loom={p['facts'].get('loom_seconds')}s  review={p['facts'].get('review_committed')}")


if __name__ == "__main__":
    main()
