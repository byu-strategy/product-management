#!/usr/bin/env python3
"""Archive the course Slack channels so the record outlives Slack's retention window.

    python3 ~/courses/product-management/scripts/slack_sync.py [--full]

The workspace is on Slack's free plan, which hides messages older than 90 days. Every run
appends new messages and thread replies to slack-messages.jsonl, which is the permanent
record; Slack is only the source. Run it at least monthly or the gap becomes unrecoverable.

Each run re-reads the last 3 days on top of anything new, so edits and late thread replies
are picked up. Records are keyed by (channel, ts); the newest copy of a message wins.

--full ignores the cursor and pulls everything Slack still has.

Each course keeps its own archive in its own _data folder (see ARCHIVES), so one course's
messages never land in another's file. A failure on one course does not stop the others.

Student data goes only to _data and _private, never to git.
"""
import json, sys, time, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from slack_common import CHANNELS, DATA, PRIVATE, call, paged, backup_to_private

OVERLAP_DAYS = 3

# (channels, _data folder, _private folder) per course
ARCHIVES = [
    (CHANNELS, DATA, PRIVATE),
    ({"C0C2RN6N2R1": "ai-foundry"},
     Path.home() / "hubs/courses/_data/ai-foundry",
     Path.home() / "courses/ai-foundry/_private"),
]


def load_archive(archive):
    """Existing records, keyed by (channel, ts)."""
    records = {}
    if archive.exists():
        for line in archive.read_text().splitlines():
            if line.strip():
                m = json.loads(line)
                records[(m["channel"], m["ts"])] = m
    return records


def fetch(channel, oldest):
    """Top-level messages plus every thread reply, since oldest (0 means everything)."""
    window = {"oldest": f"{oldest:.6f}", "inclusive": "true"} if oldest > 0 else {}
    msgs = paged("conversations.history", "messages", channel=channel, limit=200, **window)
    out = list(msgs)
    threads = [m["ts"] for m in msgs if m.get("reply_count")]
    for ts in threads:
        time.sleep(1.2)
        replies = paged("conversations.replies", "messages", channel=channel, ts=ts, limit=200)
        out.extend(r for r in replies if r["ts"] != ts)   # parent already captured
    return out


def sync(channels, data, private, full):
    archive = data / "slack-messages.jsonl"
    cursor = data / "slack-cursor.json"
    data.mkdir(parents=True, exist_ok=True)
    records = load_archive(archive)
    cursors = json.loads(cursor.read_text()) if cursor.exists() else {}
    added = updated = 0

    for channel, name in channels.items():
        last = 0.0 if full else float(cursors.get(channel, 0))
        oldest = max(0.0, last - OVERLAP_DAYS * 86400)
        msgs = fetch(channel, oldest)
        newest = last
        for m in msgs:
            m["channel"] = channel
            m["channel_name"] = name
            m["fetched_at"] = dt.datetime.now().isoformat(timespec="seconds")
            key = (channel, m["ts"])
            if key not in records:
                added += 1
            elif records[key].get("text") != m.get("text"):
                updated += 1
            records[key] = m
            newest = max(newest, float(m["ts"]))
        cursors[channel] = newest
        posts = sum(1 for m in msgs if not m.get("subtype"))
        print(f"#{name}: {len(msgs)} messages in window ({posts} real posts)")

    with archive.open("w") as f:
        for key in sorted(records, key=lambda k: (k[0], float(k[1]))):
            f.write(json.dumps(records[key], ensure_ascii=False) + "\n")
    cursor.write_text(json.dumps(cursors, indent=2) + "\n")
    archive.chmod(0o600)
    cursor.chmod(0o600)

    print(f"archive: {len(records)} messages total, {added} new, {updated} edited")
    print(f"  {archive}")
    backup_to_private(archive, private)


def main():
    full = "--full" in sys.argv
    failed = []
    for channels, data, private in ARCHIVES:
        try:
            sync(channels, data, private, full)
        except Exception as e:
            print(f"FAILED {', '.join(channels.values())}: {e}")
            failed.append(data)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
