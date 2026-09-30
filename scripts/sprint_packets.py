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
SHIPPED_CHARS = 20_000      # cap on artifact text per packet, about 5k tokens
PER_FILE_CHARS = 6_000
SKIP = re.compile(r"^(sprints/|\.claude/|\.gitignore$|README\.md$|CLAUDE\.md$)|000-.*template")
TEXT = re.compile(r"\.(md|txt|py|js|jsx|ts|tsx|html|css|json|csv|yml|yaml|toml|sql|qmd)$", re.I)


def local(iso):
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ)


def gh(path, jq=None):
    cmd = ["gh", "api", path] + (["--jq", jq] if jq else [])
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        return None
    return p.stdout if jq else json.loads(p.stdout)


def file_at(repo, path, ref=None):
    q = f"repos/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
    c = gh(q, ".content")
    return base64.b64decode(c).decode("utf-8", "replace") if c else None


def history(repo, path):
    """Commits touching path, oldest first: [(sha, local datetime)]."""
    log = gh(f"repos/{repo}/commits?path={path}&per_page=100") or []
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
    if not r.ok or "url" not in r.json():
        return None
    with tempfile.NamedTemporaryFile(suffix=".mp4") as mp4:
        mp4.write(requests.get(r.json()["url"], timeout=300).content)
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


def raw(repo, path):
    """A file's bytes, any size up to GitHub's 100 MB, private repos included."""
    p = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github.raw",
                        f"repos/{repo}/contents/{path}"], capture_output=True)
    return p.stdout if p.returncode == 0 else None


def doc_text(name, data):
    """Readable text from a Word, PowerPoint, PDF, or Excel file, so a deck or a model is judged
    on what it says, not skipped as a binary."""
    import io, zipfile
    ext = name.lower().rsplit(".", 1)[-1]
    try:
        if ext == "docx":
            import docx
            d = docx.Document(io.BytesIO(data))
            parts = [p.text for p in d.paragraphs if p.text.strip()]
            for tb in d.tables:
                parts += [" | ".join(c.text.strip() for c in row.cells) for row in tb.rows]
            return "\n".join(parts)
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


def shipped(repo, commits, budget=SHIPPED_CHARS, image_dir=None, net_id=None, max_images=3):
    """Files added or changed by the sprint's commits, with capped text for the grader. Text files,
    Word, PowerPoint, PDF, and Excel are read; up to three images (mockups, charts, screenshots
    of the work) are saved for the grader to look at."""
    files = {}
    for c in commits:
        for f in (gh(f"repos/{repo}/commits/{c['sha']}") or {}).get("files", []):
            if f["status"] != "removed" and not SKIP.search(f["filename"]):
                files[f["filename"]] = f["status"]
    out, images = [], 0
    for name, status in files.items():
        item = {"path": name, "status": status}
        text = None
        if TEXT.search(name) and budget > 0:
            # One API call per file is slow on big repos, so fetch only files whose text fits the budget.
            meta = gh(f"repos/{repo}/contents/{name}") or {}
            item["bytes"] = meta.get("size")
            if meta.get("content"):
                text = base64.b64decode(meta["content"]).decode("utf-8", "replace")
        elif DOCS.search(name) and budget > 0:
            data = raw(repo, name)
            if data:
                item["bytes"] = len(data)
                text = doc_text(name, data)
        elif IMAGES.search(name) and image_dir and images < max_images:
            data = raw(repo, name)
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
            take = min(PER_FILE_CHARS, budget)
            item["text"] = text[:take] + ("\n[... truncated]" if len(text) > take else "")
            budget -= len(item["text"])
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

    if repo_url:
        repo = repo_url.replace("https://github.com/", "").strip("/")
        n = cfg["sprint"]
        plan_path, review_path = f"sprints/sprint-{n}-plan.md", f"sprints/sprint-{n}-review.md"
        ph, rh = history(repo, plan_path), history(repo, review_path)
        plan_first = file_at(repo, plan_path, ph[0][0]) if ph else None
        plan_now = file_at(repo, plan_path)
        review = file_at(repo, review_path)
        readme = file_at(repo, "README.md") or ""
        p["plan"] = {"first_commit": ph[0][1].isoformat() if ph else None, "commits": len(ph),
                     "as_committed_day_one": plan_first, "now": plan_now}
        p["review"] = {"first_commit": rh[0][1].isoformat() if rh else None, "commits": len(rh),
                       "text": review}
        p["readme"] = readme[:4000]
        start = ph[0][1] if ph else due - dt.timedelta(days=14)
        log = gh(f"repos/{repo}/commits?since={start.astimezone(dt.timezone.utc).isoformat()}&per_page=100") or []
        commits = [{"sha": c["sha"], "when": local(c["commit"]["author"]["date"]).isoformat(),
                    "after_due": local(c["commit"]["author"]["date"]) > due,
                    "message": c["commit"]["message"].split("\n")[0]} for c in reversed(log)]
        p["commits"] = [{k: v for k, v in c.items() if k != "sha"} | {"sha": c["sha"][:7]} for c in commits]
        p["shipped_files"] = shipped(repo, commits, image_dir=cfg["out"] / "frames", net_id=net_id)

        f["plan_committed"] = bool(ph)
        f["plan_changed_during_sprint"] = bool(ph) and any(
            field(plan_first, k) != field(plan_now, k) for k in ("Goal", "Done looks like"))
        f["plan_change_noted"] = has_field(plan_now, "Changes")
        m = re.search(r"\*\*Where to see it:\*\*\s*(.+)", readme)
        f["readme_where_to_see_it"] = m.group(1).strip() if m and "[URL" not in m.group(1) else None
        f["retro_filled"] = all(field(plan_now, k) for k in ("Actual difficulty", "Why it differed", "Retro"))
        f["review_committed"] = bool(rh)
        f["review_on_time"] = bool(rh) and rh[0][1] <= due
        f["review_edited_after_first_commit"] = len(rh) > 1
        m = re.search(r"\*\*Window:\*\*\s*\S+\s+to\s+(\S+)", review or "")
        f["review_window_end"] = m.group(1) if m else None
        f["readme_context_filled"] = "[Your product" not in readme and "[the hats you wear" not in readme
        f["commits_after_due"] = sum(c["after_due"] for c in commits)
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
        plan_text = plain(plan_sub.get("body"))
        at = plan_sub.get("submitted_at")
        p["plan_submission"] = {"source": "Canvas", "submitted_at": at and local(at).isoformat(),
                                "text": plan_text or None}
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
    named = {re.sub(r"\.git$", "", u.lower()) for u in
             re.findall(r"github\.com/([\w.-]+/[\w.-]+)", where + " " + " ".join(links))}
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
        log = gh(f"repos/{r}/commits?since={start.astimezone(dt.timezone.utc).isoformat()}&per_page=100") or []
        cs = [{"sha": c["sha"], "when": local(c["commit"]["author"]["date"]).isoformat(),
               "after_due": local(c["commit"]["author"]["date"]) > due,
               "message": c["commit"]["message"].split("\n")[0]} for c in reversed(log)]
        p["other_repos"].append({"repo": f"https://github.com/{r}",
                                 "commits": [{k: v for k, v in c.items() if k != "sha"} | {"sha": c["sha"][:7]} for c in cs],
                                 "files": shipped(r, cs, budget=8_000) if cs else []})
    unshared = sorted(named - shared_lower - {course} - {o.lower() for o in others})
    f["repos_named_but_not_shared"] = unshared
    targets += [u.rstrip(").,") for u in re.findall(r"https?://\S+", where) if "github.com" not in u]
    p["link_checks"] = [check_link(u) for u in dict.fromkeys(targets)]
    p["baseline"] = cfg["baseline"].get(net_id)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    cfg = SPRINTS[a.sprint] | {"sprint": a.sprint}

    api = CanvasAPI(*[load_config()[k] for k in ("url", "token")], COURSE_ID)
    assignment = api.get(f"/assignments/{cfg['review']}")
    due = local(assignment["due_at"])
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
        p = build(s, subs.get(str(s["canvas_user_id"]), {}),
                  plan_subs.get(str(s["canvas_user_id"]), {}), cfg, due)
        p["assignment"] = {"id": cfg["review"], "name": assignment["name"],
                           "points": assignment["points_possible"], "due": due.isoformat()}
        (out / f"{s['net_id']}.json").write_text(json.dumps(p, indent=1))
        (out / f"{s['net_id']}.json").chmod(0o600)
        print(f"{s['net_id']:10} {len(json.dumps(p)) // 4:>6} tokens  "
              f"loom={p['facts'].get('loom_seconds')}s  review={p['facts'].get('review_committed')}")


if __name__ == "__main__":
    main()
