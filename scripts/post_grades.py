"""Post approved sprint grades to Canvas (the Review assignment; Sprint 1's single assignment), each with the student's feedback PDF attached.

Run from the courses hub, after Scott has reviewed review.html and marked rows approved:

    python3 ~/courses/product-management/scripts/post_grades.py --sprint 1              # dry run
    python3 ~/courses/product-management/scripts/post_grades.py --sprint 1 --test <net_id>
    python3 ~/courses/product-management/scripts/post_grades.py --sprint 1 --send

Dry run (the default) prints exactly what would be posted and touches nothing.
--test <net_id> posts one student only, so Scott can check it in SpeedGrader.
--send posts every row with approved = yes in grades.csv.

Before any write it switches the assignment to manual posting, so grades and comments stay
hidden from students until Scott clicks Post in Canvas; if that switch fails, nothing is
posted. Each post uploads the feedback PDF as a submission comment file, sets the grade, and
appends to posted.csv. A student already in posted.csv with the same score is skipped, so a
rerun never posts a second comment; a changed score is posted again with a new comment.
"""
import argparse, csv, datetime as dt, sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path.home() / ".claude/skills/canvas-lms/scripts"))
from canvas_client import CanvasAPI, load_config
sys.path.insert(0, str(Path(__file__).parent))
from sprint_config import COURSE_ID, SPRINTS
DATA = Path.home() / "hubs/courses/_data/product-management"
LOG_COLS = ["net_id", "canvas_user_id", "score", "posted_at", "comment_file_id"]


def comment_text(row, sprint):
    return (f"{row['preferred_first'] or row['name']}, your Sprint {sprint} score is "
            f"{row['final_total']}. The attached PDF covers each category and one thing to change "
            f"for next sprint.")


def upload(cfg, aid, uid, pdf):
    """Canvas three-step upload of a submission comment file; returns the file id."""
    base = cfg["url"].rstrip("/")
    base = base if base.endswith("/api/v1") else base + "/api/v1"
    h = {"Authorization": f"Bearer {cfg['token']}"}
    r = requests.post(f"{base}/courses/{COURSE_ID}/assignments/{aid}/submissions/{uid}/comments/files",
                      headers=h, data={"name": pdf.name, "size": pdf.stat().st_size,
                                       "content_type": "application/pdf"}, timeout=60)
    r.raise_for_status()
    slot = r.json()
    with open(pdf, "rb") as fh:
        up = requests.post(slot["upload_url"], data=slot["upload_params"],
                           files={"file": (pdf.name, fh, "application/pdf")},
                           allow_redirects=False, timeout=120)
    if up.status_code in (301, 302, 303):
        up = requests.get(up.headers["Location"], headers=h, timeout=60)
    up.raise_for_status()
    return up.json()["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--send", action="store_true")
    g.add_argument("--test", metavar="NET_ID")
    a = ap.parse_args()

    base = DATA / f"grading/sprint-{a.sprint}"
    rows = list(csv.DictReader(open(base / "grades.csv")))
    log_path = base / "posted.csv"
    posted = {}
    if log_path.exists():
        for r in csv.DictReader(open(log_path)):
            posted[r["net_id"]] = r["score"]

    todo, skipped = [], []
    for r in rows:
        if a.test and r["net_id"] != a.test:
            continue
        if not a.test and r.get("approved", "").strip().lower() != "yes":
            skipped.append((r["net_id"], "not approved"))
            continue
        if posted.get(r["net_id"]) == r["final_total"]:
            skipped.append((r["net_id"], f"already posted {r['final_total']}"))
            continue
        pdf = base / "feedback" / f"{r['net_id']}.pdf"
        if not pdf.exists():
            skipped.append((r["net_id"], "no feedback PDF"))
            continue
        todo.append((r, pdf))

    aid = SPRINTS[a.sprint]["review"]
    cfg = load_config()
    api = CanvasAPI(cfg["url"], cfg["token"], COURSE_ID)
    asg = api.get(f"/assignments/{aid}")
    print(f"{asg['name']} ({aid}), {asg['points_possible']:g} points, "
          f"manual posting {'on' if asg.get('post_manually') else 'OFF'}")
    for r, pdf in todo:
        print(f"  {r['net_id']:10} {r['final_total']:>5}  {pdf.name}  \"{comment_text(r, a.sprint)}\"")
    print(f"{len(todo)} to post, {len(skipped)} skipped"
          + "".join(f"\n  skip {n}: {why}" for n, why in skipped if why != "not approved")
          + (f"\n  {sum(1 for _, w in skipped if w == 'not approved')} not approved yet" if skipped else ""))

    if not (a.send or a.test):
        print("dry run: nothing posted. Add --test <net_id> or --send.")
        return
    if not todo:
        return

    if not asg.get("post_manually"):
        api.put(f"/assignments/{aid}", json={"assignment": {"post_manually": True}})
        if not api.get(f"/assignments/{aid}").get("post_manually"):
            sys.exit("could not switch the assignment to manual posting; nothing posted")
        print("switched to manual posting: grades stay hidden until you Post them in Canvas")

    new = not log_path.exists()
    with open(log_path, "a", newline="") as fh:
        w = csv.DictWriter(fh, LOG_COLS)
        if new:
            w.writeheader()
        for r, pdf in todo:
            uid = r["canvas_user_id"]
            fid = upload(cfg, aid, uid, pdf)
            api.put(f"/assignments/{aid}/submissions/{uid}", json={
                "submission": {"posted_grade": r["final_total"]},
                "comment": {"text_comment": comment_text(r, a.sprint), "file_ids": [fid]}})
            got = api.get(f"/assignments/{aid}/submissions/{uid}")
            ok = str(got.get("score")) in (r["final_total"], f"{float(r['final_total']):.1f}")
            w.writerow({"net_id": r["net_id"], "canvas_user_id": uid, "score": r["final_total"],
                        "posted_at": dt.datetime.now().isoformat(timespec="seconds"),
                        "comment_file_id": fid})
            fh.flush()
            print(f"  posted {r['net_id']:10} {r['final_total']:>5}  canvas reads {got.get('score')}"
                  f"{'' if ok else '  MISMATCH'}")
    log_path.chmod(0o600)
    print("Grades are hidden until you click Post in Canvas (Gradebook, the assignment's menu).")


if __name__ == "__main__":
    main()
