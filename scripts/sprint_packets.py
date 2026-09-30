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
TA = "nmccaul"
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


def frames(vid, dest_dir, net_id, n=9, width=1568):
    """n full-resolution frames from the Loom, evenly spaced, one JPEG each.

    The transcript says what the student said; the frames show what was on screen. Each frame
    is 1568 px wide, the largest a model reads without shrinking it, so terminal and document
    text stays legible (about 2k tokens a frame). The video goes to a temp file and is deleted;
    only the frames are kept, next to the packet."""
    r = requests.post(f"https://www.loom.com/api/campaigns/sessions/{vid}/transcoded-url",
                      json={}, timeout=30)
    if not r.ok or "url" not in r.json():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    for old in dest_dir.glob(f"{net_id}-*.jpg"):
        old.unlink()
    out = []
    with tempfile.NamedTemporaryFile(suffix=".mp4") as mp4:
        mp4.write(requests.get(r.json()["url"], timeout=300).content)
        mp4.flush()
        secs = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", mp4.name], capture_output=True, text=True).stdout or 90)
        for i in range(n):
            at = secs * (i + 0.5) / n
            dest = dest_dir / f"{net_id}-{i + 1}.jpg"
            if subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{at:.2f}", "-i", mp4.name,
                               "-frames:v", "1", "-vf", f"scale='min({width},iw)':-2", "-q:v", "2",
                               str(dest)]).returncode == 0 and dest.exists():
                dest.chmod(0o600)
                out.append({"at_seconds": round(at), "path": str(dest)})
    return out or None


def shipped(repo, commits):
    """Files added or changed by the sprint's commits, with capped text for the grader."""
    files, budget = {}, SHIPPED_CHARS
    for c in commits:
        for f in (gh(f"repos/{repo}/commits/{c['sha']}") or {}).get("files", []):
            if f["status"] != "removed" and not SKIP.search(f["filename"]):
                files[f["filename"]] = f["status"]
    out = []
    for name, status in files.items():
        # One API call per file is slow on big repos, so fetch only files whose text fits the budget.
        meta = gh(f"repos/{repo}/contents/{name}") or {} if TEXT.search(name) and budget > 0 else {}
        item = {"path": name, "status": status, "bytes": meta.get("size")}
        if meta.get("content"):
            text = base64.b64decode(meta["content"]).decode("utf-8", "replace")
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
        collabs = gh(f"repos/{repo}/collaborators", ".[].login") or ""
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
        p["shipped_files"] = shipped(repo, commits)

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
        f["ta_is_collaborator"] = TA in collabs.split()
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
    for s in roster:
        if a.only and s["net_id"] not in a.only:
            continue
        s = s | {"repo_url": repos.get(s["net_id"], {}).get("repo_url", "")}
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
