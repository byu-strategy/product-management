"""Shared Slack helpers for the MSB 341 course channel.

Auth, in priority order:
  1. SLACK_BOT_TOKEN in the environment (set it by sourcing ~/hubs/courses/.env.local).
     This is the path that works under cron.
  2. The Slack CLI, which fetches the bot token itself from the installed app. Works
     interactively on this machine only, and depends on `slack login` staying valid.

This file holds no student data.
"""
import json, os, subprocess, time, urllib.parse, urllib.request
from pathlib import Path

APP_ID = "A0C2TDWPL4U"                 # Course Monitor, workspace byustrategyprogram
TEAM = "byustrategyprogram"
CHANNELS = {"C0C1XC407J5": "msb341-is693r"}   # add per-team channels here as they appear
PROJECT = Path.home() / "hubs/courses/slack-monitor"

DATA = Path.home() / "hubs/courses/_data/product-management"
PRIVATE = Path.home() / "courses/product-management/_private"


class SlackError(RuntimeError):
    pass


def _via_http(method, params, token):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=data,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _via_cli(method, params):
    # -s skips the CLI's update check, which has no time limit and once hung a call for over
    # five minutes. The timeout turns any other hang into an error rather than a stalled run.
    args = ["slack", "api", method, "--app", APP_ID, "--no-color", "-s"]
    args += [f"{k}={v}" for k, v in params.items()]
    p = subprocess.run(args, capture_output=True, text=True, cwd=PROJECT, timeout=60,
                       stdin=subprocess.DEVNULL,
                       env={**os.environ, "PATH": f"{Path.home()}/.local/bin:" + os.environ["PATH"]})
    if p.returncode != 0:
        raise SlackError(f"slack CLI failed for {method}: {p.stderr.strip()[:300]}")
    return json.loads(p.stdout)


def call(method, **params):
    """One Slack API call, with retry on rate limiting."""
    token = os.environ.get("SLACK_BOT_TOKEN")
    for attempt in range(5):
        d = _via_http(method, params, token) if token else _via_cli(method, params)
        if d.get("ok"):
            return d
        if d.get("error") == "ratelimited":
            time.sleep(int(d.get("retry_after", 5)))
            continue
        raise SlackError(f"{method} failed: {d.get('error')}")
    raise SlackError(f"{method} rate limited after 5 attempts")


def paged(method, key, **params):
    """Every page of a cursor-paginated method, as one flat list."""
    out, cursor = [], ""
    while True:
        d = call(method, cursor=cursor, **params) if cursor else call(method, **params)
        out.extend(d.get(key, []))
        cursor = d.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            return out
        time.sleep(1.2)          # Slack's free-plan methods are tier 2/3; stay well under


def backup_to_private(path, private=PRIVATE):
    """Best-effort copy to OneDrive. A failure here never fails the run."""
    import shutil
    try:
        private.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, private / Path(path).name)
        return True
    except Exception as e:
        print(f"  note: could not back up {Path(path).name} to _private ({e})")
        return False
