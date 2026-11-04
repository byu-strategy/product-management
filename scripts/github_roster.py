"""Keep a running roster of students' GitHub usernames and builder repos.

Run from the courses hub (so the Canvas token in .env.local is found):

    python3 ~/courses/product-management/scripts/github_roster.py                       # MSB 341
    python3 ~/courses/product-management/scripts/github_roster.py --course ai-foundry   # AI Foundry

The course settings are in COURSES below. AI Foundry needs its Canvas roster first:
`canvas_roster.py --course ai-foundry`. launchd com.murff.github-roster runs both courses.

Each run:
  1. Accepts pending repo invitations from students enrolled in ANY course in COURSES, whatever
     the repo is called: the name says it is a course repo (msb341, builder-template, _foundry),
     the repo is the one submitted on Canvas, or the owner's (or sender's) GitHub username or
     profile name resolves to one student on a roster. Invitations are one list for the whole
     account, so every run checks them against every roster; which course runs first does not
     matter. Invitations to repos that no longer exist are declined. Anything else is listed
     and left alone. Expired invitations cannot be accepted; a student whose submitted repo has
     one is listed under "check:" as needing to invite sdmurff again.
  2. Finds every repo Scott collaborates on, created this semester, that was made from
     the builder template, started from its first commit, was submitted on Canvas, or
     belongs to a student on the roster.
  3. Matches repos to students: first by the repo URL they submitted on Canvas, then
     by the NetID in the repo name (<netid>_msb341), then by the GitHub username itself
     (hudsonroney18 -> Hudson Roney) for students who never renamed the repo and never
     submitted on Canvas. That last path exists because an unmatched repo is indistinguishable
     from no repo at all, which sends "you're missing the assignment" to a student who is done.
  4. Writes ~/hubs/courses/_data/<course>/github-roster.csv with one row per
     enrolled student plus any repos it could not match, and copies it to _private as a
     backup. first_seen and notes are kept from the previous run.

A student enrolled in both courses keeps a separate repo for each (sprints are numbered per
course, so one repo would overwrite the other's plan files). A repo named for the other course
(msb341 in a Foundry run, _foundry in an MSB 341 run) is left out of this course's roster unless
it was submitted on this course's Canvas, and then it is flagged.

Student data goes only to _data and _private, never to git. This file holds no student data.
"""
import argparse, csv, json, re, shutil, subprocess, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/canvas-lms/scripts"))
from canvas_client import CanvasAPI, load_config
import people_match as pm

HUB_DATA = Path.home() / "hubs/courses/_data"
# One entry per course whose students share builder repos with sdmurff. `names` marks a repo as
# this course's by name; `marker` is the part no other course uses (so a run can leave out the
# other course's repos); `submit` are the Canvas assignments whose text holds a repo link, later
# ones winning; `template_test` also counts any repo made from the template (true only for
# MSB 341, the template's original course: every Foundry repo is made from it too).
COURSES = {
    "product-management": {
        "canvas": 36977, "submit": [1500869],  # "Required: Set up your builder repo..."
        "names": r"msb341|builder-template", "marker": r"msb341", "netid_suffix": "_msb341",
        "template_test": True, "check_course_json": False,
        "roster": "roster-msb341-fall2026.csv",
        "private": Path.home() / "courses/product-management/_private",
    },
    "ai-foundry": {
        "canvas": 37925, "submit": [1515512, 1515514, 1515516],  # Sprint 1, 2, 3 Plan: a link to the plan in the repo
        "names": r"_foundry", "marker": r"_foundry", "netid_suffix": "_foundry",
        "template_test": False, "check_course_json": True,
        "roster": "roster-foundry-fall2026.csv",
        "private": Path.home() / "courses/ai-foundry/_private",
    },
}
ALL_NAMES = "|".join(c["names"] for c in COURSES.values())


def configure(course):
    """Point the module-level settings at one course."""
    global COURSE, COURSE_ID, SUBMIT_IDS, NAMES, OTHER_MARKERS, DATA, PRIVATE, ROSTER, OUT, MANUAL
    c = COURSES[course]
    COURSE, COURSE_ID, SUBMIT_IDS, NAMES = course, c["canvas"], c["submit"], c["names"]
    OTHER_MARKERS = "|".join(o["marker"] for k, o in COURSES.items() if k != course)
    DATA = HUB_DATA / course
    PRIVATE = c["private"]
    ROSTER = DATA / c["roster"]
    OUT = DATA / "github-roster.csv"
    MANUAL = DATA / "github-manual-matches.csv"


TEMPLATE = "byu-strategy/builder-template"
TEMPLATE_FIRST_COMMIT = "Initial builder template for MSB 341"
# Added to /sprint-plan on 2026-09-14 as "## What shipped means", renamed "## What output means" in
# builder-template 9e6c0a8; either heading means the copy is from after 2026-09-14.
NEW_SKILL_MARKERS = ("## What shipped means", "## What output means")
# /sprint-review is current when its sprint_scan.py carries SCAN_VERSION on or after this date
# (the marker was added 2026-10-16; older copies have no SCAN_VERSION line at all).
REVIEW_SKILL_MIN = "2026-10-16"
SEMESTER_START = "2026-09-01"
# Student data lives in the hub's _data/<course> folder (set by configure()): a plain local
# directory, not a git repo and not inside OneDrive. OneDrive's Files On-Demand can stall a read
# for minutes, which used to break this script mid-run. Both files there are regenerable from
# Canvas and GitHub, so local is safe; a best-effort copy still goes to _private (OneDrive) for
# backup, and a failure there does not fail the run. MANUAL holds hand-confirmed matches the
# automatic paths cannot make (a public repo whose invite expired, a repo named for nothing on
# the roster): net_id,repo as owner/name,note. Always wins.
configure("product-management")
# self_updating: the repo has refresh-skills (builder-template 76377ec, 2026-10-29), so every course
# skill updates itself from the template. A copy made before then needs the README's one-time prompt.
# course_json: the "course" value in course.json at the repo root; Foundry repos must say ai-foundry.
COLUMNS = ["sortable_name", "net_id", "section", "github_username", "repo_url", "private",
           "sprint_plan_skill", "plan_pushed", "canvas_submitted", "match", "first_seen", "notes",
           "sprint_review_skill", "self_updating", "course_json"]  # new columns go at the end, so readers by position keep working


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


def is_builder_name(name, names=None):
    return bool(re.search(names or NAMES, name, re.I))


_owners = {}


def owner_student(idx, login):
    """The enrolled student who owns a GitHub account, or None. Uses the username and the
    profile's display name and public email, so "bubbarand" with the name "Rand ..." still
    resolves. people_match returns no match rather than a wrong one when it is ambiguous.
    Cached per roster index: the all-courses index used for invitations must not answer for
    one course's roster."""
    key = (id(idx), login.lower())
    if key not in _owners:
        profile = gh(f"users/{login}") or {}
        student, _ = pm.find(idx, email=profile.get("email") or "", handle=login,
                             display=profile.get("name") or "")
        _owners[key] = student
    return _owners[key]


def is_class_repo(idx, submitted, full_name, names=None):
    """Students name their repos anything (MSB_341, sprint1, Brain2), so the name alone is
    not enough. A repo counts if its name says so, it or another repo of its owner was
    submitted on Canvas, or its owner is on the roster."""
    owner = full_name.split("/")[0]
    return (is_builder_name(full_name, names) or full_name.lower() in submitted
            or owner.lower() in {u.split("/")[0] for u in submitted}
            or owner_student(idx, owner) is not None)


def read_roster(path):
    return [s for s in csv.DictReader(open(path, newline="", encoding="utf-8-sig"))
            if s["enrollment_state"] in ("active", "invited")]


def all_students():
    """Every enrolled student in every course with a roster file, once each. A student in two
    courses appears in both rosters; listing them twice would make people_match call their own
    name ambiguous and match nobody."""
    seen = {}
    for course, c in COURSES.items():
        path = HUB_DATA / course / c["roster"]
        if path.exists():
            for s in read_roster(path):
                seen.setdefault(s["net_id"].lower(), s)
    return list(seen.values())


def known_students():
    """GitHub usernames already matched to a student on an earlier run, in any course."""
    known = set()
    for course in COURSES:
        out = HUB_DATA / course / "github-roster.csv"
        if out.exists():
            known |= {r["github_username"].lower() for r in csv.DictReader(open(out))
                      if r.get("net_id") and r.get("github_username")}
    return known


def accept_invites(idx, submitted):
    """Accept invitations from students in any course. Returns the repos whose invitation
    expired (lowercased owner/name): GitHub keeps them listed, but only the student can send a
    new one."""
    expired = set()
    known = known_students()
    for inv in gh("user/repository_invitations", paginate=True) or []:
        name = inv["repository"]["full_name"]
        if inv.get("expired"):
            expired.add(name.lower())
            continue
        # A company or team repo belongs to an organization, not the student, so the owner test
        # fails; the invite still counts when the person who sent it is an enrolled student.
        inviter = (inv.get("inviter") or {}).get("login", "")
        if not (is_class_repo(idx, submitted, name, ALL_NAMES) or inviter.lower() in known
                or (inviter and owner_student(idx, inviter) is not None)):
            print(f"skipped  invite  {name}  (neither owner nor sender on a course roster; accept by hand if it is a student's)")
            continue
        gh(f"user/repository_invitations/{inv['id']}", method="PATCH")
        if gh(f"repos/{name}") is None:
            gh(f"user/repository_invitations/{inv['id']}", method="DELETE")
            print(f"declined invite  {name}  (repo no longer exists)")
        else:
            print(f"accepted invite  {name}")
    return expired


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


def self_updating(full_name):
    return "yes" if gh(f"repos/{full_name}/contents/.claude/skills/refresh-skills/refresh.py") is not None else "no"


def course_json(full_name):
    """The course named in course.json at the repo root, "missing", or "unreadable"."""
    text = gh(f"repos/{full_name}/contents/course.json", raw=True)
    if text is None:
        return "missing"
    try:
        return json.loads(text).get("course") or "unreadable"
    except (ValueError, AttributeError):
        return "unreadable"


def repo_info(r):
    """One roster entry for a repo, from its GitHub API record."""
    plan = gh(f"repos/{r['full_name']}/contents/sprints/sprint-1-plan.md") is not None
    return {
        "github_username": r["owner"]["login"],
        "repo_url": r["html_url"],
        "private": "yes" if r["private"] else "NO",
        "sprint_plan_skill": skill_version(r["full_name"]),
        "sprint_review_skill": review_skill_version(r["full_name"]),
        "plan_pushed": "yes" if plan else "no",
        "self_updating": self_updating(r["full_name"]),
        "course_json": course_json(r["full_name"]) if COURSES[COURSE]["check_course_json"] else "",
    }


def builder_repos(idx, submitted):
    repos = {}
    for r in gh("user/repos?type=all&per_page=100", paginate=True) or []:
        if r["created_at"] < SEMESTER_START or r["owner"]["login"].lower() in ("sdmurff", "byu-strategy"):
            continue
        # The other course's repo (a student in both keeps one per course) stays out of this
        # roster unless this course's Canvas was given it.
        if (OTHER_MARKERS and re.search(OTHER_MARKERS, r["name"], re.I)
                and r["full_name"].lower() not in submitted):
            continue
        if not is_builder_name(r["name"]):
            if COURSES[COURSE]["template_test"]:
                full = gh(f"repos/{r['full_name']}") or r
                template = (full.get("template_repository") or {}).get("full_name")
                if template != TEMPLATE:
                    commits = gh(f"repos/{r['full_name']}/commits?per_page=100") or []
                    first = commits[-1]["commit"]["message"].split("\n")[0] if commits else ""
                    if first != TEMPLATE_FIRST_COMMIT and not is_class_repo(idx, submitted, r["full_name"]):
                        continue
            elif not is_class_repo(idx, submitted, r["full_name"]):
                continue
        repos[r["full_name"].lower()] = repo_info(r)
    return repos


def canvas_submissions():
    """canvas_user_id -> the repo (owner/name, lowercased) in their latest submission with a
    GitHub link, across this course's SUBMIT_IDS in order."""
    api = CanvasAPI(*[load_config()[k] for k in ("url", "token")], COURSE_ID)
    by_user = {}
    for aid in SUBMIT_IDS:
        for s in api.get_all(f"/assignments/{aid}/submissions"):
            if s.get("workflow_state") == "unsubmitted":
                continue
            body = re.sub(r"<link[^>]*>|<script.*?</script>", "", s.get("body") or "", flags=re.S)
            body += " " + (s.get("url") or "")
            urls = re.findall(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?(?=[\s<\"'/)]|$)", body)
            uid = str(s["user_id"])
            if urls or uid not in by_user:
                by_user[uid] = urls[0].lower() if urls else ""
    return by_user


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--course", choices=sorted(COURSES), default="product-management")
    configure(ap.parse_args().course)
    print(f"== {COURSE}  {dt.datetime.now():%Y-%m-%d %H:%M}")
    if not ROSTER.exists():
        sys.exit(f"no roster at {ROSTER}; run canvas_roster.py --course {COURSE} first")
    students_all = read_roster(ROSTER)
    idx = pm.index(students_all)
    idx_any = pm.index(all_students())   # invitations: a student in any course
    try:
        subs = canvas_submissions()
    except OSError as ex:
        # The Canvas token lives in OneDrive; under launchd a Files On-Demand stall can make it
        # unreadable ("Resource deadlock avoided"). Invites expire in 7 days, so accept them anyway
        # (that needs only GitHub), then stop rather than rewrite the roster without Canvas data.
        print(f"Canvas unreachable ({ex}); accepting invites only, roster left unchanged")
        accept_invites(idx_any, set())
        return
    submitted = {u for u in subs.values() if u}
    expired = accept_invites(idx_any, submitted)
    repos = builder_repos(idx, submitted)
    previous = {}
    if OUT.exists():
        for row in csv.DictReader(open(OUT, newline="", encoding="utf-8")):
            previous[row["net_id"] or row["repo_url"]] = row
    today = dt.date.today().isoformat()

    by_netid = {}
    suffix = re.escape(COURSES[COURSE]["netid_suffix"])
    for full in repos:
        m = re.match(rf"(.+?){suffix}$", full.split("/")[1])
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
                repos[full] = repo_info(r)
            manual[m["net_id"].strip().lower()] = full

    rows, used, unshared = [], set(), {}
    for s in students_all:
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
            if not full:
                unshared[s["net_id"]] = submitted
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

    DATA.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    OUT.chmod(0o600)

    foundry_checks = COURSES[COURSE]["check_course_json"]
    students = [r for r in rows if r.get("net_id")]
    print(f"\n{sum(1 for r in students if r.get('repo_url'))} of {len(students)} students have a repo shared with sdmurff")
    print(f"{sum(1 for r in students if r.get('plan_pushed') == 'yes')} have pushed a Sprint 1 plan")
    for r in rows:
        checks = [("UNMATCHED", r.get("match") == "UNMATCHED"),
                  ("PUBLIC repo", r.get("private") == "NO"),
                  (f"{r.get('sprint_plan_skill')} /sprint-plan", r.get("sprint_plan_skill") in ("OLD", "missing")),
                  (f"{r.get('sprint_review_skill')} /sprint-review", r.get("sprint_review_skill") in ("OLD", "missing"))]
        if foundry_checks and r.get("repo_url"):
            checks += [(f"course.json {r.get('course_json')}", r.get("course_json") != "ai-foundry"),
                       ("skills not self-updating (README one-time prompt)", r.get("self_updating") == "no"),
                       ("named for another course", bool(OTHER_MARKERS and re.search(OTHER_MARKERS, r.get("repo_url", ""), re.I)))]
        problems = [p for p, bad in checks if bad]
        if problems:
            print(f"check: {r.get('repo_url')}  {', '.join(problems)}")
    for net_id, repo in sorted(unshared.items()):
        why = "invitation EXPIRED: the student must invite sdmurff again" if repo in expired else "no invitation seen"
        print(f"check: {net_id} submitted github.com/{repo}, not shared with sdmurff ({why})")
    print(f"wrote {OUT}")
    try:
        shutil.copyfile(OUT, PRIVATE / OUT.name)
        print(f"backed up to {PRIVATE / OUT.name}")
    except OSError as e:
        print(f"backup to _private skipped ({e}); the local copy is authoritative")


if __name__ == "__main__":
    main()
