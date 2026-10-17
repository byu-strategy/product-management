#!/usr/bin/env python3
"""Match Slack channel members to the MSB 341 Canvas roster.

    python3 ~/courses/product-management/scripts/slack_roster.py

Writes to ~/hubs/courses/_data/product-management/:
  slack-members.csv   one row per enrolled student: in the channel or not, join date,
                      Slack handle. Plus any channel member not on the roster.
  no-slack.csv        enrolled students who have not joined, for nudging.

Matching is by BYU email first, which is exact. Students who signed up with a personal or
law-school address fall back to their handle and display name, which resolves cases like
lauren.warner@law.byu.edu, and those rows are flagged match=handle so you can eyeball them. An
ambiguous handle produces no match rather than a wrong one, and nobody is matched on a display
name that does not contain a real name, because students set those to things like "jt".

Join dates come from channel_join events in slack-messages.jsonl, so run slack_sync.py first
and keep running it: on the free plan those events age out after 90 days, and the archive is
then the only place they exist.

Student data goes only to _data and _private, never to git.
"""
import csv, json, sys, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from slack_common import CHANNELS, DATA, call, paged, backup_to_private
import people_match as pm

ROSTER = DATA / "roster-msb341-fall2026.csv"
ARCHIVE = DATA / "slack-messages.jsonl"
OUT = DATA / "slack-members.csv"
MISSING = DATA / "no-slack.csv"
COLUMNS = ["sortable_name", "net_id", "email", "section", "in_channel", "joined_at",
           "slack_handle", "slack_user_id", "match"]


def slack_users():
    """Every human workspace user, and a lookup by BYU email."""
    users = [u for u in paged("users.list", "members", limit=200)
             if not (u.get("deleted") or u.get("is_bot") or u["id"] == "USLACKBOT")]
    by_email = {}
    for u in users:
        email = (u.get("profile", {}).get("email") or "").lower()
        if email:
            by_email[email] = u
    return users, by_email, {u["id"]: u for u in users}


def join_dates(channel):
    """user id -> date they joined, from archived channel_join events."""
    out = {}
    if not ARCHIVE.exists():
        return out
    for line in ARCHIVE.read_text().splitlines():
        if not line.strip():
            continue
        m = json.loads(line)
        if m.get("channel") == channel and m.get("subtype") == "channel_join":
            ts = dt.datetime.fromtimestamp(float(m["ts"])).strftime("%Y-%m-%d")
            out.setdefault(m["user"], ts)      # earliest wins if they left and rejoined
    return out


def main():
    channel = next(iter(CHANNELS))
    name = CHANNELS[channel]
    members = set(paged("conversations.members", "members", channel=channel, limit=200))
    users, by_email, by_id = slack_users()
    joined = join_dates(channel)

    rows, unmatched_ids = [], set(members)
    with ROSTER.open() as f:
        students = [s for s in csv.DictReader(f) if s["enrollment_state"] == "active"]

    # One student at a time against the Slack directory: exact BYU email first, then handle
    # and display name via the shared matcher.
    idx = pm.index(students)
    claimed = {}
    for u in users:
        profile = u.get("profile", {})
        student, how = pm.find(idx, email=profile.get("email", ""),
                               handle=u.get("name", ""),
                               display=profile.get("real_name", ""))
        if student:
            claimed.setdefault(student["net_id"], (u, how))

    for s in students:
        email = s["email"].lower()
        u, match = by_email.get(email), "email"
        if not u:
            u, match = claimed.get(s["net_id"], (None, "none"))
        uid = u["id"] if u else ""
        unmatched_ids.discard(uid)
        rows.append({
            "sortable_name": s["sortable_name"], "net_id": s["net_id"], "email": s["email"],
            "section": s["section"].split(":")[0],
            "in_channel": "yes" if uid in members else "no",
            "joined_at": joined.get(uid, ""),
            "slack_handle": u["profile"].get("display_name") or u.get("name", "") if u else "",
            "slack_user_id": uid, "match": match if u else "none",
        })

    for uid in sorted(unmatched_ids):           # in the channel, not on the roster
        u = by_id.get(uid)
        if not u:
            continue
        rows.append({
            "sortable_name": f"(not on roster) {u['profile'].get('real_name', '')}",
            "net_id": "", "email": u["profile"].get("email", ""), "section": "",
            "in_channel": "yes", "joined_at": joined.get(uid, ""),
            "slack_handle": u["profile"].get("display_name") or u.get("name", ""),
            "slack_user_id": uid, "match": "not_on_roster",
        })

    rows.sort(key=lambda r: r["sortable_name"])
    for path, subset in ((OUT, rows),
                         (MISSING, [r for r in rows if r["in_channel"] == "no"])):
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(subset)
        path.chmod(0o600)

    enrolled = [r for r in rows if r["net_id"]]
    joined_n = sum(1 for r in enrolled if r["in_channel"] == "yes")
    weak = sum(1 for r in enrolled if r["match"] == "name")
    extra = sum(1 for r in rows if r["match"] == "not_on_roster")
    print(f"#{name}: {joined_n} of {len(enrolled)} enrolled students are in the channel")
    if weak:
        print(f"  {weak} matched by name only, check match=name rows")
    if extra:
        print(f"  {extra} channel members are not on the roster")
    print(f"  {OUT}\n  {MISSING}")
    backup_to_private(OUT)
    backup_to_private(MISSING)


if __name__ == "__main__":
    main()
