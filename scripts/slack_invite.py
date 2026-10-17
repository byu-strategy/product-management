#!/usr/bin/env python3
"""Add enrolled students who are in the Slack workspace to the course channel.

    python3 ~/courses/product-management/scripts/slack_invite.py --dry-run
    python3 ~/courses/product-management/scripts/slack_invite.py
    python3 ~/courses/product-management/scripts/slack_invite.py --strong-only

The channel is private, so it has no join link and nobody can add themselves. This script
closes that gap: it reads slack-members.csv, finds enrolled students who have a Slack account
but are not in the channel, and invites them.

Rerun it after every registration wave and after nudging students to join the workspace. It
skips anyone already in the channel, so running it twice is harmless.

Students with no Slack account at all cannot be added by anything; they have to accept the
workspace invite first. They are listed at the end, and live in no-slack.csv.

--strong-only leaves out students matched to a Slack account by display name alone. A wrong
name match would put a stranger in a private channel with the class, so /student-status runs
with it and lists those students for Scott to confirm instead.

Run slack_roster.py first so the CSV is current.
"""
import csv, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from slack_common import CHANNELS, DATA, call, SlackError

MEMBERS = DATA / "slack-members.csv"
BATCH = 25          # small enough that one bad id does not take a big batch down with it


def main():
    dry = "--dry-run" in sys.argv
    channel = next(iter(CHANNELS))
    name = CHANNELS[channel]
    rows = list(csv.DictReader(MEMBERS.open()))

    targets = [r for r in rows
               if r["net_id"] and r["slack_user_id"] and r["in_channel"] == "no"]
    no_account = [r for r in rows if r["net_id"] and not r["slack_user_id"]]

    print(f"#{name}: {len(targets)} students to invite, {len(no_account)} have no Slack account")
    weak = [r for r in targets if r["match"] == "name"]
    for r in weak:
        print(f"  matched by name, not email: {r['sortable_name']} ({r['slack_handle']})")
    if "--strong-only" in sys.argv and weak:
        targets = [r for r in targets if r["match"] != "name"]
        print(f"  --strong-only: not inviting those {len(weak)}; confirm them and rerun without it")
    if dry:
        for r in targets:
            print(f"  would invite {r['sortable_name']} ({r['slack_handle']})")
        return

    invited, skipped, failed = [], [], []
    for i in range(0, len(targets), BATCH):
        batch = targets[i:i + BATCH]
        try:
            call("conversations.invite", channel=channel,
                 users=",".join(r["slack_user_id"] for r in batch))
            invited.extend(batch)
        except SlackError:
            for r in batch:                      # one bad id fails the batch; retry singly
                try:
                    call("conversations.invite", channel=channel, users=r["slack_user_id"])
                    invited.append(r)
                except SlackError as e:
                    (skipped if "already_in_channel" in str(e) else failed).append((r, e))
                time.sleep(1.2)
        time.sleep(1.2)

    print(f"\ninvited {len(invited)}")
    if skipped:
        print(f"already in the channel: {len(skipped)}")
    for r, e in failed:
        print(f"  FAILED {r['sortable_name']}: {e}")
    print("\nRun slack_roster.py again to refresh the membership CSVs.")
    if no_account:
        print(f"{len(no_account)} students still need to join the workspace (see no-slack.csv)")


if __name__ == "__main__":
    main()
