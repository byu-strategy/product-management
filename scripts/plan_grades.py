"""Grade a sprint's Plan assignment (Sprint 2 on) for completion, and optionally post it to Canvas.

Run from the courses hub:

    python3 ~/courses/product-management/scripts/plan_grades.py --sprint 2              # build + dry run
    python3 ~/courses/product-management/scripts/plan_grades.py --sprint 2 --test <net_id>
    python3 ~/courses/product-management/scripts/plan_grades.py --sprint 2 --send

Completion is mechanical: a submission with all four fields (Goal, Why this, Done looks like,
Predicted difficulty) earns 10, anything else 0 with the missing fields named. Late submissions
are flagged, not docked; Canvas's own late policy, if one is set, applies on its own.

Every run rebuilds grading/sprint-N/plans/: plans.csv (one row per student), a packet per
student for the optional plan-feedback graders (<net_id>.json: the plan text and the README
context), and plan-review.html. If a grader has written plans/feedback/<net_id>.json
({"feedback": "..."}), that text is posted as the submission comment. Plan feedback never
changes the score.

--send posts every submitted plan not already in plans/posted.csv with the same score, after
switching the assignment to manual posting so nothing is visible until Scott clicks Post.
Nothing here holds student data; the output stays in _data.
"""
import argparse, base64, csv, datetime as dt, html, json, re, subprocess, sys
from pathlib import Path

import requests
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path.home() / ".claude/skills/canvas-lms/scripts"))
sys.path.insert(0, str(Path(__file__).parent))
from canvas_client import CanvasAPI, load_config
from sprint_config import COURSE_ID, PLAN_FIELDS, PLAN_POINTS, SPRINTS

TZ = ZoneInfo("America/Denver")
DATA = Path.home() / "hubs/courses/_data/product-management"
COLS = ["net_id", "name", "preferred_first", "canvas_user_id", "submitted_at", "late",
        "fields_missing", "score", "has_feedback"]
e = html.escape


def plain(body):
    t = re.sub(r"<(br|/p|/li|/div)[^>]*>", "\n", body or "")
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def has_field(text, name):
    return bool(re.search(rf"{re.escape(name)}\s*\**\s*:\s*\**\s*\S", text or "", re.I))


def readme(repo_url):
    if not repo_url:
        return None
    repo = repo_url.replace("https://github.com/", "").strip("/")
    p = subprocess.run(["gh", "api", f"repos/{repo}/readme", "--jq", ".content"],
                       capture_output=True, text=True)
    return base64.b64decode(p.stdout).decode("utf-8", "replace")[:4000] if p.returncode == 0 else None


def page(rows, sprint):
    trs = "".join(
        f"<tr><td>{e(r['name'])}<div class=m>{e(r['net_id'])}</div></td><td>{e(r['submitted_at'] or 'not submitted')}</td>"
        f"<td>{'late' if r['late'] == 'yes' else ''}</td><td>{e(r['fields_missing'])}</td>"
        f"<td class=n>{r['score']}</td><td>{e(r.get('_feedback', ''))}</td></tr>" for r in rows)
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Sprint {sprint} plans</title><style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#1d2330;--m:#5b6475;--l:#e3e6ec}}
@media (prefers-color-scheme:dark){{:root{{--bg:#12151b;--card:#1a1f27;--ink:#e6e9ef;--m:#98a1b3;--l:#2a313c}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}}
header,.bar{{padding:14px 24px 6px}}h1{{font-size:20px;margin:0}}.m{{color:var(--m)}}
input{{font:inherit;padding:6px 10px;border:1px solid var(--l);border-radius:6px;background:var(--card);color:var(--ink)}}
.wrap{{padding:0 24px 40px;overflow-x:auto}}table{{border-collapse:collapse;width:100%;background:var(--card);border:1px solid var(--l)}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--l);text-align:left;vertical-align:top}}
th{{position:sticky;top:0;background:var(--card);cursor:pointer;font-size:12px;text-transform:uppercase;color:var(--m)}}.n{{text-align:right}}
</style></head><body><header><h1>Sprint {sprint} plans</h1><p class=m>Completion: all four fields = {PLAN_POINTS}. Late is flagged, not docked.</p></header>
<div class=bar><input id=q placeholder="Search" size=30> <span id=c class=m></span></div>
<div class=wrap><table><thead><tr><th>Student</th><th>Submitted</th><th>Late</th><th>Missing</th><th class=n>Score</th><th>Feedback</th></tr></thead>
<tbody>{trs}</tbody></table><p id=none class=m hidden>No students match.</p></div>
<script>const q=document.getElementById('q'),rs=[...document.querySelectorAll('tbody tr')];
function f(){{let n=0;rs.forEach(r=>{{const ok=r.textContent.toLowerCase().includes(q.value.toLowerCase());r.hidden=!ok;if(ok)n++}});
document.getElementById('c').textContent=n+' of '+rs.length;document.getElementById('none').hidden=n>0}}q.oninput=f;f();
document.querySelectorAll('th').forEach((th,i)=>{{let d=1;th.onclick=()=>{{d=-d;const b=th.parentNode.parentNode.nextElementSibling;
[...b.rows].sort((x,y)=>{{let a=x.cells[i].textContent,c=y.cells[i].textContent;if(th.classList.contains('n')){{a=+a;c=+c}}return (a>c?1:a<c?-1:0)*d}}).forEach(r=>b.appendChild(r))}}}});</script>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--send", action="store_true")
    g.add_argument("--test", metavar="NET_ID")
    a = ap.parse_args()
    aid = SPRINTS[a.sprint]["plan"]
    if not aid:
        sys.exit(f"Sprint {a.sprint} has no separate Plan assignment; its plan is graded inside the sprint.")

    cfg = load_config()
    api = CanvasAPI(cfg["url"], cfg["token"], COURSE_ID)
    asg = api.get(f"/assignments/{aid}")
    subs = {str(s["user_id"]): s for s in api.get_all(f"/assignments/{aid}/submissions")}
    roster = list(csv.DictReader(open(DATA / "roster-msb341-fall2026.csv")))
    repos = {r["net_id"]: r.get("repo_url", "") for r in csv.DictReader(open(DATA / "github-roster.csv"))}

    base = DATA / f"grading/sprint-{a.sprint}/plans"
    (base / "feedback").mkdir(parents=True, exist_ok=True)
    rows = []
    for s in roster:
        sub = subs.get(str(s["canvas_user_id"]), {})
        text = plain(sub.get("body")) if sub.get("submitted_at") else ""
        missing = [k for k in PLAN_FIELDS if not has_field(text, k)] if text else []
        at = sub.get("submitted_at")
        fb_path = base / "feedback" / f"{s['net_id']}.json"
        fb = json.loads(fb_path.read_text()).get("feedback", "") if fb_path.exists() else ""
        row = {"net_id": s["net_id"], "name": s["name"], "preferred_first": s["preferred_first"],
               "canvas_user_id": s["canvas_user_id"],
               "submitted_at": dt.datetime.fromisoformat(at.replace("Z", "+00:00")).astimezone(TZ)
               .strftime("%a %b %-d %-I:%M %p") if at else "",
               "late": "yes" if sub.get("late") else "", "fields_missing": ", ".join(missing),
               "score": (PLAN_POINTS if not missing else 0) if text else "",
               "has_feedback": "yes" if fb else "", "_feedback": fb}
        rows.append(row)
        if text:
            pk = base / f"{s['net_id']}.json"
            pk.write_text(json.dumps({"net_id": s["net_id"], "preferred_first": s["preferred_first"],
                                      "sprint": a.sprint, "plan_text": text,
                                      "readme": readme(repos.get(s["net_id"]))}, indent=1))
            pk.chmod(0o600)

    with open(base / "plans.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (base / "plan-review.html").write_text(page(rows, a.sprint))
    for f in ("plans.csv", "plan-review.html"):
        (base / f).chmod(0o600)

    sub_rows = [r for r in rows if r["score"] != ""]
    print(f"{asg['name']} ({aid}): {len(sub_rows)} of {len(rows)} submitted, "
          f"{sum(1 for r in sub_rows if r['score'] == PLAN_POINTS)} complete, "
          f"{sum(1 for r in sub_rows if r['late'])} late, "
          f"{sum(1 for r in sub_rows if r['has_feedback'])} with feedback")
    for r in sub_rows:
        if r["fields_missing"]:
            print(f"  incomplete {r['net_id']}: missing {r['fields_missing']}")
    print(f"  {base / 'plan-review.html'}")

    log_path = base / "posted.csv"
    posted = {r["net_id"]: r["score"] for r in csv.DictReader(open(log_path))} if log_path.exists() else {}
    todo = [r for r in sub_rows if (not a.test or r["net_id"] == a.test)
            and posted.get(r["net_id"]) != str(r["score"])]
    print(f"{len(todo)} to post (manual posting {'on' if asg.get('post_manually') else 'OFF'})")
    if not (a.send or a.test):
        print("dry run: nothing posted. Add --test <net_id> or --send.")
        return
    if not todo:
        return
    if not asg.get("post_manually"):
        # REST ignores post_manually; the post policy is set through Canvas's GraphQL API.
        base = cfg["url"].rstrip("/").replace("/api/v1", "")
        requests.post(f"{base}/api/graphql", headers={"Authorization": f"Bearer {cfg['token']}"}, timeout=30,
                      json={"query": 'mutation{setAssignmentPostPolicy(input:{assignmentId:"%s",postManually:true})'
                                     '{postPolicy{postManually}}}' % aid})
        if not api.get(f"/assignments/{aid}").get("post_manually"):
            sys.exit("could not switch the assignment to manual posting; nothing posted")
    new = not log_path.exists()
    with open(log_path, "a", newline="") as fh:
        w = csv.DictWriter(fh, ["net_id", "score", "posted_at"])
        if new:
            w.writeheader()
        for r in todo:
            body = {"submission": {"posted_grade": str(r["score"])}}
            if r["_feedback"]:
                body["comment"] = {"text_comment": r["_feedback"]}
            api.put(f"/assignments/{aid}/submissions/{r['canvas_user_id']}", json=body)
            w.writerow({"net_id": r["net_id"], "score": r["score"],
                        "posted_at": dt.datetime.now().isoformat(timespec="seconds")})
            print(f"  posted {r['net_id']:10} {r['score']}")
    log_path.chmod(0o600)
    print("Hidden until you click Post on the assignment in Canvas.")


if __name__ == "__main__":
    main()
