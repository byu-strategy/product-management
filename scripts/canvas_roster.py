#!/usr/bin/env python3
"""Refresh the MSB 341 roster from Canvas.

    python3 ~/courses/product-management/scripts/canvas_roster.py

Writes ~/hubs/courses/_data/product-management/roster-msb341-fall2026.csv, the spine every
other script joins against: github_roster.py, slack_roster.py, slack_invite.py, nudge.py.
Run it after any registration wave, and before a nudge send, so a student who added or
dropped this week is treated correctly.

Canvas course 36977 is the cross-listed shell, so this covers MSB 341-002, IS 693R-008 and
C S 498R-005 in one pull.

preferred_first is the first word of Canvas's short_name, which BYU fills from the name the
student chose ("Daniel Wait II" for Wait II, Scott Daniel; "Toby Zheng" for Zheng, Yitong).
Every email greets students with it, through first_name() in ~/hubs/courses/scripts/send_nudge.py.
Taking the first given name from sortable_name instead is what sent "Hi Scott" to Daniel.

Student data goes only to _data and _private, never to git. This file holds no student data.
"""
import csv, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/canvas-lms/scripts"))
from canvas_client import CanvasAPI, load_config

COURSE_ID = 36977
DATA = Path.home() / "hubs/courses/_data/product-management"
PRIVATE = Path.home() / "courses/product-management/_private"
OUT = DATA / "roster-msb341-fall2026.csv"
COLUMNS = ["sortable_name", "name", "preferred_first", "email", "net_id", "canvas_user_id", "sis_user_id",
           "section", "enrollment_state"]


def main():
    api = CanvasAPI(*[load_config()[k] for k in ("url", "token")], COURSE_ID)
    sections = {s["id"]: s["name"] for s in api.get_all("/sections")}

    rows, seen = [], set()
    for e in api.get_all("/enrollments", params={"type[]": "StudentEnrollment",
                                                 "state[]": ["active", "invited"]}):
        u = e.get("user", {})
        if u.get("id") in seen:          # a cross-listed student can appear twice
            continue
        seen.add(u.get("id"))
        login = u.get("login_id", "") or ""
        rows.append({
            "sortable_name": u.get("sortable_name", ""),
            "name": u.get("name", ""),
            "preferred_first": (u.get("short_name") or "").split(" ")[0],
            "email": u.get("login_id", "") if "@" in login else f"{login}@byu.edu",
            "net_id": login.split("@")[0],
            "canvas_user_id": u.get("id", ""),
            "sis_user_id": u.get("sis_user_id", "") or e.get("sis_user_id", "") or "",
            "section": sections.get(e.get("course_section_id"), ""),
            "enrollment_state": e.get("enrollment_state", ""),
        })

    rows.sort(key=lambda r: r["sortable_name"])
    previous = set()
    if OUT.exists():
        previous = {r["net_id"] for r in csv.DictReader(OUT.open())}

    DATA.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    OUT.chmod(0o600)

    now = {r["net_id"] for r in rows}
    active = sum(1 for r in rows if r["enrollment_state"] == "active")
    print(f"{len(rows)} students ({active} active) in Canvas course {COURSE_ID}")
    from collections import Counter
    for sec, n in Counter(r["section"] for r in rows).most_common():
        print(f"  {n:>3}  {sec}")
    if previous:
        added, gone = now - previous, previous - now
        print(f"since the last file: {len(added)} added, {len(gone)} no longer listed")
        for net_id in sorted(added):
            r = next(r for r in rows if r["net_id"] == net_id)
            print(f"  + {r['sortable_name']} ({net_id})")
        for net_id in sorted(gone):
            print(f"  - {net_id}")
    print(f"  {OUT}")
    try:
        shutil.copy2(OUT, PRIVATE / OUT.name)
    except Exception as e:
        print(f"  note: could not back up to _private ({e})")


if __name__ == "__main__":
    main()
