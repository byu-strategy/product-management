"""Keep a running roster of students' GitHub usernames and builder repos.

Run from the courses hub (so the Canvas token in .env.local is found):

    python3 ~/courses/product-management/scripts/github_roster.py

Each run:
  1. Accepts pending repo invitations from enrolled students, whatever the repo is called:
     the name contains msb341 or builder-template, the repo is the one submitted on Canvas,
     or the owner's GitHub username or profile name resolves to one student on the roster.
     Invitations to repos that no longer exist are declined. Anything else is listed and
     left alone.
  2. Finds every repo Scott collaborates on, created this semester, that was made from
     the builder template, started from its first commit, was submitted on Canvas, or
     belongs to a student on the roster.
  3. Matches repos to students: first by the repo URL they submitted on Canvas, then
     by the NetID in the repo name (<netid>_msb341), then by the GitHub username itself
     (hudsonroney18 -> Hudson Roney) for students who never renamed the repo and never
     submitted on Canvas. That last path exists because an unmatched repo is indistinguishable
     from no repo at all, which sends "you're missing the assignment" to a student who is done.
  4. Writes ~/hubs/courses/_data/product-management/github-roster.csv with one row per
     enrolled student plus any repos it could not match, and copies it to _private as a
     backup. first_seen and notes are kept from the previous run.

Student data goes only to _data and _private, never to git. This file holds no student data.
"""
import csv, json, re, shutil, subprocess, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/canvas-lms/scripts"))
from canvas_client import CanvasAPI, load_config
import people_match as pm

COURSE_ID = 36977
SETUP_ASSIGNMENT_ID = 1500869          # "Required: Set up your builder repo..."
TEMPLATE = "byu-strategy/builder-template"
TEMPLATE_FIRST_COMMIT = "Initial builder template for MSB 341"
# Added to /sprint-plan on 2026-09-14 as "## What shipped means", renamed "## What output means" in
# builder-template 9e6c0a8; either heading means the copy is from after 2026-09-14.
NEW_SKILL_MARKERS = ("## What shipped means", "## What output means")
# /sprint-review is current when its sprint_scan.py carries SCAN_VERSION on or after this date
# (the marker was added 2026-10-16; older copies have no SCAN_VERSION line at all).
REVIEW_SKILL_MIN = "2026-10-16"
SEMESTER_START = "2026-09-01"
# Student data lives in the hub's _data folder: a plain local directory, not a git repo and
# not inside OneDrive. OneDrive's Files On-Demand can stall a read for minutes, which used to
# break this script mid-run. Both files here are regenerable from Canvas and GitHub, so local
# is safe; a best-effort copy still goes to _private (OneDrive) for backup, and a failure
# there does not fail the run.
DATA = Path.home() / "hubs/courses/_data/product-management"
PRIVATE = Path.home() / "courses/product-management/_private"
ROSTER = DATA / "roster-msb341-fall2026.csv"
OUT = DATA / "github-roster.csv"
# Hand-confirmed matches the automatic paths cannot make (a public repo whose invite expired, a
# repo named for nothing on the roster). net_id,repo as owner/name,note. Always wins.
MANUAL = DATA / "github-manual-matches.csv"
COLUMNS = ["sortable_name", "net_id", "section", "github_username", "repo_url", "private",
           "sprint_plan_skill", "plan_pushed", "canvas_submitted", "match", "first_seen", "notes",
           "sprint_review_skill"]  # new columns go at the end, so readers by position keep working


def gh(path, method="GET", paginate=False, raw=False):
    cmd = ["gh", "api", "-X", method, path]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    if raw:
        cmd += ["-H", "Accept: application/vnd.github.raw"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    if raw:
        return r.stdout
    if not r.stdout.strip():
        return {}
    data = json.loads(r.stdout)
    return [x for page in data for x in page] if paginate else data


def is_builder_name(name):
    return bool(re.search(r"msb341|builder-template", name, re.I))


_owners = {}


def owner_student(idx, login):
    """The enrolled student who owns a GitHub account, or None. Uses the username and the
    profile's display name and public email, so "bubbarand" with the name "Rand ..." still
    resolves. people_match returns no match rather than a wrong one when it is ambiguous."""
    if login.lower() not in _owners:
        profile = gh(f"users/{login}") or {}
        student, _ = pm.find(idx, email=profile.get("email") or "", handle=login,
                             display=profile.get("name") or "")
        _owners[login.lower()] = student
    return _owners[login.lower()]


def is_class_repo(idx, submitted, full_name):
    """Students name their repos anything (MSB_341, sprint1, Brain2), so the name alone is
    not enough. A repo counts if its name says so, it or another repo of its owner was
    submitted on Canvas, or its owner is on the roster."""
    owner = full_name.split("/")[0]
    return (is_builder_name(full_name) or full_name.lower() in submitted
            or owner.lower() in {u.split("/")[0] for u in submitted}
            or owner_student(idx, owner) is not None)


def known_students():
    """GitHub usernames already matched to a student on an earlier run."""
    if not OUT.exists():
        return set()
    return {r["github_username"].lower() for r in csv.DictReader(open(OUT)) if r.get("net_id") and r.get("github_username")}


def accept_invites(idx, submitted):
    for inv in gh("user/repository_invitations", paginate=True) or []:
        name = inv["repository"]["full_name"]
        if inv.get("expired"):
            continue
        # A company or team repo belongs to an organization, not the student, so the owner test
        # fails; the invite still counts when the person who sent it is an enrolled student.
        inviter = (inv.get("inviter") or {}).get("login", "")
        if not (is_class_repo(idx, submitted, name) or inviter.lower() in known_students()
                or (inviter and owner_student(idx, inviter) is not None)):
            print(f"skipped  invite  {name}  (neither owner nor sender on the roster; accept by hand if it is a student's)")
            continue
        gh(f"user/repository_invitations/{inv['id']}", method="PATCH")
        if gh(f"repos/{name}") is None:
            gh(f"user/repository_invitations/{inv['id']}", method="DELETE")
            print(f"declined invite  {name}  (repo no longer exists)")
        else:
            print(f"accepted invite  {name}")


def skill_version(full_name):
    text = gh(f"repos/{full_name}/contents/.claude/skills/sprint-plan/SKILL.md", raw=True)
    if text is None:
        return "missing"
    return "new" if any(m in text for m in NEW_SKILL_MARKERS) else "OLD"


def review_skill_version(full_name):
    """new / OLD / missing, like sprint_plan_skill, from SCAN_VERSION in the repo's sprint_scan.py."""
    text = gh(f"repos/{full_name}/contents/.claude/skills/sprint-review/scripts/sprint_scan.py", raw=True)
    if text is None:
        return "missing"
    m = re.search(r'^SCAN_VERSION\s*=\s*["\'](\d{4}-\d{2}-\d{2})', text, re.M)
    return "new" if m and m.group(1) >= REVIEW_SKILL_MIN else "OLD"


def builder_repos(idx, submitted):
    repos = {}
    for r in gh("user/repos?type=all&per_page=100", paginate=True) or []:
        if r["created_at"] < SEMESTER_START or r["owner"]["login"].lower() in ("sdmurff", "byu-strategy"):
            continue
        full = gh(f"repos/{r['full_name']}") or r
        template = (full.get("template_repository") or {}).get("full_name")
        if template != TEMPLATE and not is_builder_name(r["name"]):
            commits = gh(f"repos/{r['full_name']}/commits?per_page=100") or []
            first = commits[-1]["commit"]["message"].split("\n")[0] if commits else ""
            if first != TEMPLATE_FIRST_COMMIT and not is_class_repo(idx, submitted, r["full_name"]):
                continue
        plan = gh(f"repos/{r['full_name']}/contents/sprints/sprint-1-plan.md") is not None
        repos[r["full_name"].lower()] = {
            "github_username": r["owner"]["login"],
            "repo_url": r["html_url"],
            "private": "yes" if r["private"] else "NO",
            "sprint_plan_skill": skill_version(r["full_name"]),
            "sprint_review_skill": review_skill_version(r["full_name"]),
            "plan_pushed": "yes" if plan else "no",
        }
    return repos


def canvas_submissions():
    api = CanvasAPI(*[load_config()[k] for k in ("url", "token")], COURSE_ID)
    by_user = {}
    for s in api.get_all(f"/assignments/{SETUP_ASSIGNMENT_ID}/submissions"):
        if s.get("workflow_state") == "unsubmitted":
            continue
        body = re.sub(r"<link[^>]*>|<script.*?</script>", "", s.get("body") or "", flags=re.S)
        urls = re.findall(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?(?=[\s<\"'/)]|$)", body)
        by_user[str(s["user_id"])] = urls[0].lower() if urls else ""
    return by_user


def main():
    students_all = [s for s in csv.DictReader(open(ROSTER, newline="", encoding="utf-8-sig"))
                    if s["enrollment_state"] in ("active", "invited")]
    idx = pm.index(students_all)
    try:
        subs = canvas_submissions()
    except OSError as ex:
        # The Canvas token lives in OneDrive; under launchd a Files On-Demand stall can make it
        # unreadable ("Resource deadlock avoided"). Invites expire in 7 days, so accept them anyway
        # (that needs only GitHub), then stop rather than rewrite the roster without Canvas data.
        print(f"Canvas unreachable ({ex}); accepting invites only, roster left unchanged")
        accept_invites(idx, set())
        return
    submitted = {u for u in subs.values() if u}
    accept_invites(idx, submitted)
    repos = builder_repos(idx, submitted)
    previous = {}
    if OUT.exists():
        for row in csv.DictReader(open(OUT, newline="", encoding="utf-8")):
            previous[row["net_id"] or row["repo_url"]] = row
    today = dt.date.today().isoformat()

    by_netid = {}
    for full in repos:
        m = re.match(r"(.+?)_msb341$", full.split("/")[1])
        if m:
            by_netid.setdefault(m.group(1), full)

    # Third match path: the repo owner's GitHub account (username, then profile name). Only
    # used when the first two fail, and only when exactly one student fits, so an ambiguous
    # username yields no match rather than a wrong one. A student who shared two repos gets
    # the one with a Sprint 1 plan in it.
    by_username = {}
    for full in sorted(repos, key=lambda f: repos[f]["plan_pushed"] != "yes"):
        owner = full.split("/")[0]
        student = owner_student(idx, owner)
        if student:
            by_username.setdefault(student["net_id"].lower(), (full, owner))

    manual = {}
    if MANUAL.exists():
        for m in csv.DictReader(open(MANUAL)):
            full = m["repo"].strip().lower()
            if full not in repos:  # public, or shared later: read it directly
                r = gh(f"repos/{m['repo'].strip()}")
                if not r:
                    continue
                plan = gh(f"repos/{r['full_name']}/contents/sprints/sprint-1-plan.md") is not None
                repos[full] = {"github_username": r["owner"]["login"], "repo_url": r["html_url"],
                               "private": "yes" if r["private"] else "NO",
                               "sprint_plan_skill": skill_version(r["full_name"]),
                               "sprint_review_skill": review_skill_version(r["full_name"]),
                               "plan_pushed": "yes" if plan else "no"}
            manual[m["net_id"].strip().lower()] = full

    rows, used = [], set()
    for s in csv.DictReader(open(ROSTER, newline="", encoding="utf-8-sig")):
        if s["enrollment_state"] not in ("active", "invited"):
            continue
        netid = s["net_id"].lower()
        submitted = subs.get(s["canvas_user_id"])
        full, match = None, ""
        if netid in manual and manual[netid] in repos:
            full, match = manual[netid], "manual"
        elif submitted and submitted in repos:
            full, match = submitted, "canvas URL"
        elif netid in by_netid:
            full, match = by_netid[netid], "repo name"
        elif netid in by_username and by_username[netid][0] not in used:
            full, match = by_username[netid][0], "username"
        elif submitted and (same_owner := [f for f in repos if f not in used
                                           and f.split("/")[0] == submitted.split("/")[0]]):
            # The submitted repo was deleted or renamed, but the same account shared another.
            full, match = same_owner[0], "canvas owner"
        row = {"sortable_name": s["sortable_name"], "net_id": s["net_id"], "section": s["section"],
               "canvas_submitted": "yes" if submitted is not None else "no", "match": match}
        if submitted and submitted not in repos:
            row["notes"] = f"submitted {submitted}, not shared with sdmurff yet"
        if full:
            used.add(full)
            row.update(repos[full])
        rows.append(row)

    for full, info in repos.items():
        if full in used:
            continue
        owner = owner_student(idx, full.split("/")[0])
        if owner:
            rows.append({**info, "match": f"extra repo of {owner['net_id']}",
                         "notes": "a second repo from a student already matched to another"})
        else:
            rows.append({**info, "match": "UNMATCHED",
                         "notes": "no roster NetID in repo name, no Canvas submission, and the "
                                  "GitHub account does not resolve to one student"})

    for row in rows:
        prev = previous.get(row.get("net_id") or row.get("repo_url"), {})
        row["first_seen"] = prev.get("first_seen") or (today if row.get("repo_url") else "")
        row["notes"] = prev.get("notes") or row.get("notes", "")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    students = [r for r in rows if r.get("net_id")]
    print(f"\n{sum(1 for r in students if r.get('repo_url'))} of {len(students)} students have a repo shared with sdmurff")
    print(f"{sum(1 for r in students if r.get('plan_pushed') == 'yes')} have pushed a Sprint 1 plan")
    for r in rows:
        problems = [p for p, bad in [("UNMATCHED", r.get("match") == "UNMATCHED"),
                                     ("PUBLIC repo", r.get("private") == "NO"),
                                     (f"{r.get('sprint_plan_skill')} /sprint-plan", r.get("sprint_plan_skill") in ("OLD", "missing")),
                                     (f"{r.get('sprint_review_skill')} /sprint-review", r.get("sprint_review_skill") in ("OLD", "missing"))] if bad]
        if problems:
            print(f"check: {r.get('repo_url')}  {', '.join(problems)}")
    print(f"wrote {OUT}")
    try:
        shutil.copyfile(OUT, PRIVATE / OUT.name)
        print(f"backed up to {PRIVATE / OUT.name}")
    except OSError as e:
        print(f"backup to _private skipped ({e}); the local copy is authoritative")


if __name__ == "__main__":
    main()
