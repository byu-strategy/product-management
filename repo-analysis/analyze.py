#!/usr/bin/env python3
"""Team stat sheet for MSB 341 student company repos.

Reads roster.csv (name,track,repo), clones/pulls each repo into work/,
and writes stat-sheet.md with per-student cadence and category balance.

Usage:
    python3 analyze.py            # last 7 days spotlight, full-semester totals
    python3 analyze.py --days 14

Requires: git (uses your existing GitHub auth — students must add you as
a collaborator on private repos, or use `gh auth setup-git`).
"""

import argparse
import csv
import subprocess
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE / "work"

# Top-level folder -> category (mirrors the practice-plan categories)
CATEGORIES = {
    "product": "Building",
    "specs": "Building",
    "discovery": "Discovery",
    "gtm": "GTM",
    "decisions": "Judgment",
    "metrics": "Metrics",
    "practice-log": "Practice log",
}


def run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def sync_repo(url: str, dest: Path) -> str | None:
    """Clone or pull. Returns error message or None."""
    if dest.exists():
        code, _, err = run(["git", "-C", str(dest), "pull", "--ff-only", "-q"])
    else:
        code, _, err = run(["git", "clone", "-q", url, str(dest)])
    return err if code != 0 else None


def commit_stats(repo: Path, since_days: int):
    """Return dict of stats from git log."""
    code, out, err = run(
        ["git", "-C", str(repo), "log", "--pretty=%H|%ad", "--date=short",
         "--name-only", "--no-merges"])
    if code != 0:
        return None

    cutoff = (date.today() - timedelta(days=since_days)).isoformat()
    stats = {
        "total_commits": 0, "recent_commits": 0,
        "active_days": set(), "recent_days": set(),
        "last_commit": None,
        "cat_total": Counter(), "cat_recent": Counter(),
        "interviews": 0, "specs": 0, "logs": 0, "experiments": 0,
    }
    current_date = None
    for line in out.splitlines():
        if "|" in line and len(line.split("|")[0]) == 40:
            current_date = line.split("|")[1]
            stats["total_commits"] += 1
            stats["active_days"].add(current_date)
            if stats["last_commit"] is None:
                stats["last_commit"] = current_date
            if current_date >= cutoff:
                stats["recent_commits"] += 1
                stats["recent_days"].add(current_date)
        elif line.strip() and current_date:
            top = line.split("/")[0]
            cat = CATEGORIES.get(top, "Other")
            stats["cat_total"][cat] += 1
            if current_date >= cutoff:
                stats["cat_recent"][cat] += 1

    # Artifact counts from the working tree (substance lives in files, not commits)
    stats["interviews"] = count_files(repo / "discovery" / "interviews")
    stats["specs"] = count_files(repo / "specs")
    stats["logs"] = count_files(repo / "practice-log")
    stats["experiments"] = count_files(repo / "gtm" / "experiments")
    return stats


def count_files(d: Path) -> int:
    if not d.is_dir():
        return 0
    return sum(1 for f in d.rglob("*.md") if not f.name.startswith("000-"))


def cat_bar(counter: Counter) -> str:
    total = sum(counter.values())
    if not total:
        return "—"
    parts = [f"{cat} {100 * n // total}%" for cat, n in counter.most_common()]
    return ", ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7, help="spotlight window (default 7)")
    args = ap.parse_args()

    roster_path = HERE / "roster.csv"
    if not roster_path.exists():
        sys.exit("roster.csv not found next to analyze.py")
    WORK.mkdir(exist_ok=True)

    rows, errors = [], []
    with open(roster_path) as f:
        roster = [r for r in csv.DictReader(f) if r.get("repo", "").strip()]

    for entry in roster:
        name, track, url = entry["name"], entry.get("track", ""), entry["repo"].strip()
        slug = url.rstrip("/").split("/")[-1].removesuffix(".git")
        dest = WORK / slug
        print(f"Syncing {name} ({slug})...", file=sys.stderr)
        err = sync_repo(url, dest)
        if err:
            errors.append((name, err))
            continue
        s = commit_stats(dest, args.days)
        if s is None:
            errors.append((name, "git log failed"))
            continue
        rows.append((name, track, s))

    rows.sort(key=lambda r: r[2]["recent_commits"])  # least active first: coaching order

    d = args.days
    lines = [
        f"# Team Stat Sheet — generated {date.today().isoformat()}",
        "",
        f"Spotlight window: last {d} days. Sorted least-active first (coaching order).",
        "",
        f"| Student | Track | Commits ({d}d) | Active days ({d}d) | Last commit | "
        "Balance (semester) | Interviews | Specs | Experiments | Practice logs |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, track, s in rows:
        lines.append(
            f"| {name} | {track} | {s['recent_commits']} | {len(s['recent_days'])} | "
            f"{s['last_commit'] or '—'} | {cat_bar(s['cat_total'])} | "
            f"{s['interviews']} | {s['specs']} | {s['experiments']} | {s['logs']} |")

    if errors:
        lines += ["", "## Sync errors", ""]
        lines += [f"- **{n}**: {e}" for n, e in errors]

    lines += [
        "", "## Reading the sheet", "",
        "- **Balance** shows which folders their commits touch. A sandbox student at "
        ">90% Building with 0 Discovery commits needs a coaching conversation.",
        "- Artifact counts exclude `000-` template files.",
        "- Never grade commit counts directly — use this sheet to pick coaching "
        "conversations and film-session material, then read the artifacts.",
    ]

    out = HERE / "stat-sheet.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
