"""Correct Canvas due dates for this course, across the DST boundary.

The canvas-lms skill's parse_due_date applies a fixed CANVAS_TZ_OFFSET. Utah is
UTC-6 on daylight time and UTC-7 on standard time, and this semester straddles the
change (Nov 1, 2026), so any fixed offset is wrong for part of the term. Use this
instead; zoneinfo knows the rules.

    from canvas_due import due
    api.put(f"/assignments/{aid}", json={"assignment": {"due_at": due("2026-11-23 15:00")}})
"""
import datetime as dt
from zoneinfo import ZoneInfo

COURSE_TZ = ZoneInfo("America/Denver")   # matches the Canvas course and account setting


def due(local: str) -> str:
    """'YYYY-MM-DD HH:MM' in course-local time -> the UTC instant Canvas wants.

    A bare date means 11:59 PM local, matching the usual end-of-day deadline.
    """
    local = local.strip()
    fmt = "%Y-%m-%d %H:%M" if " " in local else "%Y-%m-%d"
    naive = dt.datetime.strptime(local, fmt)
    if " " not in local:
        naive = naive.replace(hour=23, minute=59)
    aware = naive.replace(tzinfo=COURSE_TZ)
    return aware.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local(utc_iso: str) -> str:
    """Canvas UTC timestamp -> a readable course-local string, for verification."""
    u = dt.datetime.fromisoformat(utc_iso.replace("Z", "+00:00"))
    return u.astimezone(COURSE_TZ).strftime("%a %b %d, %Y at %-I:%M %p %Z")


if __name__ == "__main__":
    for s in ["2026-09-14 15:00", "2026-09-28", "2026-11-23 15:00", "2026-12-10", "2026-12-14 08:00"]:
        u = due(s)
        print(f"{s:<18} -> {u}  ({local(u)})")
