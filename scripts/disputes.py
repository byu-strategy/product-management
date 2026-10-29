#!/usr/bin/env python3
"""Grade disputes: the course side of the Strategy app's dispute page (decided with Scott 2026-10-29).

Students dispute an itemized deduction from their sprint report at strategy.byu.edu/app/dispute/<token>,
with no sign-in. The app stores the dispute and shows it to Scott at /app/admin/disputes, where he copies
a /resolve-dispute command. Everything that changes a grade or contacts a student happens here, each step
after Scott says yes, and nothing here writes to Canvas (that is /publish-grades).

    python3 disputes.py --sprint 3 sync [--only net_id ...]     push each student's link and deductions
    python3 disputes.py --sprint 3 window 2026-11-05            set when disputes close (release + 7 days)
    python3 disputes.py --sprint 3 list                         open disputes
    python3 disputes.py pull <ticket>                           one dispute, with its evidence downloaded
    python3 disputes.py resolve <ticket> restore 1|change -1|keep [--note "..."]
    python3 disputes.py reply <ticket> --body-file reply.md [--send]   draft by default; --send sends

Run from ~/hubs/courses. Reads the Strategy app's Supabase URL and service key from the app's .env.local
(never copied anywhere) and Resend settings from the courses .env.local. Tables: the app's migration
073_grade_disputes.sql. Writes sprint-N/dispute-window.json, dispute-outcomes.json and grades.csv overrides,
then rebuild with sprint_feedback.py. Student data stays in _data.
"""
import argparse, csv, hashlib, json, re, sys, datetime as dt
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from canvas_due import due  # America/Denver, DST-aware
from sprint_config import categories

DATA = Path.home() / "hubs/courses/_data/product-management"
APP_ENV = Path.home() / "Documents/strategy-program/website/.env.local"
COURSES_ENV = Path.home() / "hubs/courses/.env.local"
COURSE = "msb341"
BUCKET = "grade-dispute-evidence"
FROM = '"Professor Murff" <grading@strategy.byu.edu>'
CAT_KEY = {"Output": "shipped", "Report and retro": "review", "Demo": "demo", "Plan": "plan"}
LABEL = {"shipped": "Output", "review": "Report and retro", "demo": "Demo", "plan": "Plan"}


def env(path):
    out = {}
    for line in path.read_text().splitlines():
        m = re.match(r"\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


class DB:
    """The few REST calls this needs, as the service role (server-side only, like the app's own writes)."""

    def __init__(self):
        e = env(APP_ENV)
        self.url, key = e["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/"), e["SUPABASE_SERVICE_KEY"]
        self.h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def _ok(self, r):
        if r.status_code >= 300:
            sys.exit(f"Supabase {r.status_code}: {r.text[:400]}")
        return r.json() if r.text else None

    def get(self, table, **q):
        return self._ok(requests.get(f"{self.url}/rest/v1/{table}", headers=self.h, params=q, timeout=30))

    def upsert(self, table, rows, on):
        h = dict(self.h, Prefer="resolution=merge-duplicates,return=representation")
        return self._ok(requests.post(f"{self.url}/rest/v1/{table}", headers=h, params={"on_conflict": on},
                                      data=json.dumps(rows), timeout=30))

    def patch(self, table, values, **q):
        h = dict(self.h, Prefer="return=representation")
        return self._ok(requests.patch(f"{self.url}/rest/v1/{table}", headers=h, params=q,
                                       data=json.dumps(values), timeout=30))

    def delete(self, table, **q):
        return self._ok(requests.delete(f"{self.url}/rest/v1/{table}", headers=self.h, params=q, timeout=30))

    def download(self, path):
        r = requests.get(f"{self.url}/storage/v1/object/{BUCKET}/{path}", headers=self.h, timeout=60)
        if r.status_code >= 300:
            sys.exit(f"Storage {r.status_code} for {path}: {r.text[:200]}")
        return r.content


def base(sprint):
    return DATA / f"grading/sprint-{sprint}"


def roster():
    return {r["net_id"]: r for r in csv.DictReader(open(DATA / "roster-msb341-fall2026.csv"))}


def grades(sprint):
    p = base(sprint) / "grades.csv"
    return {r["net_id"]: r for r in csv.DictReader(open(p))} if p.exists() else {}


def final(row, cat):
    o = str(row.get(f"override_{cat}", "")).strip()
    return float(o) if o else float(row[cat])


# ---------------------------------------------------------------- sync

def cmd_sync(a):
    b = base(a.sprint)
    tokens = json.loads((b / "dispute-tokens.json").read_text())
    ros, gr = roster(), grades(a.sprint)
    cats = [(c, m) for c, _l, m in categories(a.sprint) if c != "plan"]
    review_max = sum(m for _c, m in cats)
    w = b / "dispute-window.json"
    closes = json.loads(w.read_text()).get("closes") if w.exists() else None
    db, n_links, n_ded = DB(), 0, 0
    for f in sorted((b / "results").glob("*.json")):
        r = json.loads(f.read_text())
        n = r["net_id"]
        if a.only and n not in a.only:
            continue
        ds = [d for d in r.get("deductions") or [] if float(d.get("points") or 0) > 0]
        if n not in tokens or n not in ros:
            print(f"  skip {n}: {'no token (run sprint_feedback.py first)' if n not in tokens else 'not on the roster'}")
            continue
        p = json.loads((b / f"{n}.json").read_text()) if (b / f"{n}.json").exists() else {}
        ro, row = ros[n], gr.get(n)
        score = sum(final(row, c) for c, _m in cats) if row else None
        link = db.upsert("grade_dispute_links", [{
            "token_hash": hashlib.sha256(tokens[n].encode()).hexdigest(), "course": COURSE, "sprint": a.sprint,
            "net_id": n, "student_name": p.get("name") or ro["name"], "first_name": ro.get("preferred_first") or ro["name"].split()[0],
            "email": ro["email"], "review_score": score, "review_max": review_max, "closes_at": closes,
            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat()}], "course,sprint,net_id")[0]
        n_links += 1
        # A deduction someone already disputed is never replaced; the rest follow the current result.
        have = db.get("grade_deductions", link_id=f"eq.{link['id']}", select="id,ded_key,grade_disputes(id)")
        locked = {x["ded_key"] for x in have if x.get("grade_disputes")}
        keep = {d["id"] for d in ds}
        for x in have:
            if x["ded_key"] not in keep and x["ded_key"] not in locked:
                db.delete("grade_deductions", id=f"eq.{x['id']}")
        rows = [{"link_id": link["id"], "ded_key": d["id"], "category": LABEL.get(d.get("category"), d.get("category")),
                 "points": float(d["points"]), "what": d.get("what", ""), "rule": rule_text(d.get("rule_id")),
                 "rule_source": rule_source(d.get("rule_id")), "fix": d.get("fix"), "reason": d.get("reason"),
                 "confidence": r.get("confidence"), "excerpt": d.get("excerpt"), "excerpt_ref": d.get("excerpt_ref")}
                for d in ds if d["id"] not in locked]
        if rows:
            db.upsert("grade_deductions", rows, "link_id,ded_key")
        n_ded += len(rows)
    print(f"synced {n_links} students, {n_ded} deductions (Sprint {a.sprint})")


def rule_text(rid):
    from sprint_report import RULE_TEXT
    return RULE_TEXT.get(rid, "")


def rule_source(rid):
    from sprint_report import RULE_SRC
    return RULE_SRC.get(rid, "")


def cmd_window(a):
    """Disputes close a week after release (Scott, 2026-10-29): 11:59 PM course time on the given date."""
    closes = due(a.date)
    (base(a.sprint) / "dispute-window.json").write_text(json.dumps({"closes": closes}))
    DB().patch("grade_dispute_links", {"closes_at": closes}, course=f"eq.{COURSE}", sprint=f"eq.{a.sprint}")
    local = dt.datetime.fromisoformat(closes.replace("Z", "+00:00")).astimezone(__import__("zoneinfo").ZoneInfo("America/Denver"))
    print(f"Sprint {a.sprint} disputes close {local:%a %b %-d, %-I:%M %p} (course time). Rebuild the reports to show it.")


# ---------------------------------------------------------------- read

SEL = ("id,ticket,why,evidence,status,points_changed,resolution_note,resolved_at,reply_sent_at,created_at,"
       "grade_deductions(ded_key,category,points,what,rule,fix,reason,excerpt,excerpt_ref),"
       "grade_dispute_links(sprint,net_id,student_name,first_name,email,review_score,review_max)")


def one(ticket):
    rows = DB().get("grade_disputes", ticket=f"eq.{ticket.lower()}", select=SEL)
    if not rows:
        sys.exit(f"no dispute {ticket}")
    return rows[0]


def cmd_list(a):
    rows = DB().get("grade_disputes", status="eq.open", select=SEL, order="created_at")
    rows = [x for x in rows if not a.sprint or x["grade_dispute_links"]["sprint"] == a.sprint]
    for x in rows:
        d, l = x["grade_deductions"], x["grade_dispute_links"]
        print(f"{x['ticket']}  Sprint {l['sprint']}  {l['net_id']:<10} {d['ded_key']} -{d['points']:g} {d['category']}: {d['what']}")
    print(f"{len(rows)} open")


def cmd_pull(a):
    x = one(a.ticket)
    l = x["grade_dispute_links"]
    folder = base(l["sprint"]) / "disputes" / x["ticket"]
    folder.mkdir(parents=True, exist_ok=True)
    db = DB()
    for ev in x.get("evidence") or []:
        if ev.get("kind") == "file" and ev.get("path"):
            out = folder / re.sub(r"[^\w.-]+", "-", ev.get("name") or Path(ev["path"]).name)
            out.write_bytes(db.download(ev["path"]))
            out.chmod(0o600)
            ev["local"] = str(out)
    row = grades(l["sprint"]).get(l["net_id"], {})
    x["current_scores"] = {c: (final(row, c) if row else None) for c, _l, _m in categories(l["sprint"]) if c != "plan"}
    (folder / "dispute.json").write_text(json.dumps(x, indent=1, ensure_ascii=False))
    (folder / "dispute.json").chmod(0o600)
    print(json.dumps(x, indent=1, ensure_ascii=False))
    print(f"\nsaved in {folder}")


# ---------------------------------------------------------------- change

def cmd_resolve(a):
    """Record Scott's decision: the override in grades.csv, the outcome the report shows, the status in the app."""
    x = one(a.ticket)
    d, l = x["grade_deductions"], x["grade_dispute_links"]
    sprint, n, cat = l["sprint"], l["net_id"], CAT_KEY[d["category"]]
    change = {"restore": float(a.points if a.points is not None else d["points"]), "keep": 0.0}.get(a.decision)
    if a.decision == "change":
        change = float(a.points)
    status = "denied" if a.decision == "keep" else "upheld" if a.decision == "restore" else "changed"
    path = base(sprint) / "grades.csv"
    rows = list(csv.DictReader(open(path)))
    cols = list(rows[0].keys())
    mx = dict((c, m) for c, _l, m in categories(sprint))[cat]
    for row in rows:
        if row["net_id"] == n and change:
            new = min(mx, max(0.0, final(row, cat) + change))
            print(f"{n} {LABEL[cat]}: {final(row, cat):g} -> {new:g} (override_{cat})")
            row[f"override_{cat}"] = f"{new:g}"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(rows)
    path.chmod(0o600)
    op = base(sprint) / "dispute-outcomes.json"
    oc = json.loads(op.read_text()) if op.exists() else {}
    oc.setdefault(n, {})[d["ded_key"]] = {"status": status, "points_changed": change, "ticket": x["ticket"]}
    op.write_text(json.dumps(oc, indent=1))
    op.chmod(0o600)
    DB().patch("grade_disputes", {"status": status, "points_changed": change, "resolution_note": a.note,
                                  "resolved_at": dt.datetime.now(dt.timezone.utc).isoformat()}, id=f"eq.{x['id']}")
    print(f"{x['ticket']} marked {status} in the app. Next: sprint_feedback.py --sprint {sprint} --no-pdf, then "
          f"post_grades.py --sprint {sprint} --test {n} --replace (dry run first, through /publish-grades; on every decision).")


def cmd_reply(a):
    """Send Scott's reply from grading@strategy.byu.edu to the roster address only. Draft unless --send."""
    x = one(a.ticket)
    l = x["grade_dispute_links"]
    body = Path(a.body_file).read_text().strip()
    if "—" in body:
        sys.exit("the reply has an em dash; rewrite it first")
    subject = f"Your Sprint {l['sprint']} dispute: {x['grade_deductions']['what']}"
    print(f"From: {FROM}\nTo: {l['email']}\nSubject: {subject}\n\n{body}\n")
    if not a.send:
        print("(draft only; add --send to send)")
        return
    e = env(COURSES_ENV)
    payload = {"from": FROM, "to": [l["email"]], "subject": subject, "text": body}
    if e.get("REPLY_TO"):
        payload["reply_to"] = e["REPLY_TO"]
    r = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {e['RESEND_API_KEY']}"},
                      json=payload, timeout=30)
    if r.status_code >= 300:
        sys.exit(f"Resend {r.status_code}: {r.text[:300]}")
    DB().patch("grade_disputes", {"reply_sent_at": dt.datetime.now(dt.timezone.utc).isoformat()}, id=f"eq.{x['id']}")
    print(f"sent to {l['email']} (Resend id {r.json().get('id', '?')})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sprint", type=int)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("sync"); s.add_argument("--only", nargs="*")
    s = sp.add_parser("window"); s.add_argument("date", help="YYYY-MM-DD, course time; closes at 11:59 PM")
    sp.add_parser("list")
    s = sp.add_parser("pull"); s.add_argument("ticket")
    s = sp.add_parser("resolve"); s.add_argument("ticket"); s.add_argument("decision", choices=["restore", "change", "keep"])
    s.add_argument("points", nargs="?", type=float, help="restore: points to restore (default all); change: signed points")
    s.add_argument("--note", default="")
    s = sp.add_parser("reply"); s.add_argument("ticket"); s.add_argument("--body-file", required=True)
    s.add_argument("--send", action="store_true")
    a = ap.parse_args()
    if a.cmd in ("sync", "window") and not a.sprint:
        sys.exit("--sprint is required")
    if a.cmd == "resolve" and a.decision == "change" and a.points is None:
        sys.exit("change needs signed points, e.g. change -1")
    {"sync": cmd_sync, "window": cmd_window, "list": cmd_list, "pull": cmd_pull,
     "resolve": cmd_resolve, "reply": cmd_reply}[a.cmd](a)


if __name__ == "__main__":
    main()
