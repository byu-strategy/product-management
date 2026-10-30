#!/usr/bin/env python3
"""The midterm ring of each student's builder profile (Scott, 2026-10-29).

The midterm tests three axes (Agentic Workflow, Discovery, Design), 12 questions each, and fills part of
the knowledge half of those axes: MIDTERM_SHARE of it, with the final filling the rest. Points are the
plain share of questions right, with no curve (Scott: "take their actual score without the scaling,
because that's what they actually knew"): points = MIDTERM_SHARE x knowledge max x correct / 12. On those
three axes the September self-rating keeps only the part the exams have not measured yet
(builder_growth.py), and it stays on the chart as a dashed outline.

Sources, both read-only:
  - the Testing Center exports of the paper exam (~/Downloads/Student Results - * - Midterm.csv): one row
    per student, the key letter in each question's header, the student's letter in each cell;
  - the Canvas make-up quiz (assignment MAKEUP_ASSIGNMENT, a classic quiz): per-question right or wrong
    from each submission's history, matched to the item bank by question text.
Question order and each question's concept and type (know, use, predict) come from the item bank
(_materials/builder-exam/items/draft, role "seated"), in the order build_midterm_print.py printed them; the
script refuses to run if the export's answer key does not match that order.

Writes, student data, never git:
  _data/product-management/grading/midterm/ring-<net_id>.json   per student
  _data/product-management/grading/midterm/midterm.csv          one row per student, for Scott
  _data/product-management/grading/midterm/raw/                 copies of the exports read
No question text, options or answers are written: the exam is reused.

    python3 midterm_ring.py            # from ~/hubs/courses (reads .env.local for Canvas)
"""
import csv
import glob
import html
import json
import os
import re
import shutil
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("PM_DATA") or Path.home() / "hubs/courses/_data/product-management")
OUT = DATA / "grading" / "midterm"
BANK = HERE.parents[1] / "_materials" / "builder-exam"
EXPORTS = sorted(glob.glob(str(Path.home() / "Downloads" / "Student Results - * - Midterm.csv")))
COURSE, MAKEUP_ASSIGNMENT = 36977, 1515811
AXES = ("Agentic Workflow", "Discovery", "Design")
MIDTERM_SHARE = 0.5   # of each tested axis's knowledge half; the final fills the rest
PRACTICE = {"AI Systems": 25.0}


def knowledge_max(axis):
    return 100 - PRACTICE.get(axis, 50.0)


def item_order():
    sys.path.insert(0, str(BANK / "tools"))
    import build  # noqa: E402  the item bank's own loader and print order
    items, _c, _e = build.load()
    seated = [i for i in items if i["exam"] == "midterm" and i.get("role") == "seated"]
    order = []
    for axis in AXES:
        order += sorted([i for i in seated if i["axis"] == axis], key=build.sort_key)
    if len(order) != 36:
        sys.exit(f"expected 36 seated midterm items, found {len(order)}")
    return order


def paper(order):
    """{net_id: (rights[36], taken)} from the Testing Center exports. A blank answer is wrong."""
    out = {}
    for f in EXPORTS:
        rows = list(csv.reader(open(f, encoding="utf-8-sig")))
        hdr = rows[0]
        qcols = [i for i, h in enumerate(hdr) if re.match(r"Q\d+ \(", h)]
        key = [re.search(r"\((\w)\)", hdr[i]).group(1) for i in qcols]
        if key != [it["answer"] for it in order]:
            sys.exit(f"{Path(f).name}: the answer key does not match the item bank's order")
        ni, ti = hdr.index("Net ID"), hdr.index("Entry Time")
        for r in rows[1:]:
            if len(r) <= max(qcols) or not r[ni].strip():
                continue
            out[r[ni].strip().lower()] = ([r[i].strip().upper() == k for i, k in zip(qcols, key)], r[ti].strip(), "paper")
    return out


def canvas_get(path):
    env = dict(line.strip().split("=", 1) for line in open(Path.home() / "hubs/courses/.env.local")
               if "=" in line and not line.startswith("#"))
    tok, base = env["CANVAS_API_TOKEN"].strip('"'), env["CANVAS_API_URL"].strip('"').rstrip("/")
    base += "" if base.endswith("/api/v1") else "/api/v1"
    out, url = [], base + path
    while url:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + tok}))
        body = json.load(r)
        out += body if isinstance(body, list) else [body]
        m = re.search(r'<([^>]+)>; rel="next"', r.headers.get("Link") or "")
        url = m.group(1) if m else None
    return out


def makeup(order):
    """{canvas_user_id: (rights[36], taken)} from the make-up quiz, matched to the item bank by question text."""
    norm = lambda t: re.sub(r"\W+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip().lower()
    a = canvas_get(f"/courses/{COURSE}/assignments/{MAKEUP_ASSIGNMENT}")[0]
    qs = canvas_get(f"/courses/{COURSE}/quizzes/{a['quiz_id']}/questions?per_page=100")
    pos = {}
    for q in qs:
        t = norm(q["question_text"])
        hit = [n for n, it in enumerate(order) if norm(it["stem"])[:60] in t]
        if len(hit) != 1:
            sys.exit(f"make-up question {q['id']} matches {len(hit)} items")
        pos[q["id"]] = hit[0]
    out = {}
    for s in canvas_get(f"/courses/{COURSE}/assignments/{MAKEUP_ASSIGNMENT}/submissions?per_page=100&include[]=submission_history"):
        hist = [h for h in s.get("submission_history") or [] if h.get("submission_data")]
        if not hist:
            continue
        last = hist[-1]
        rights = [False] * 36
        for d in last["submission_data"]:
            if d.get("question_id") in pos:
                rights[pos[d["question_id"]]] = bool(d.get("correct") is True or d.get("correct") == "true")
        out[str(s["user_id"])] = (rights, (last.get("submitted_at") or "")[:10], "make-up")
    return out


def ring(net_id, rights, taken, source, order):
    axes = {}
    for axis in AXES:
        idx = [n for n, it in enumerate(order) if it["axis"] == axis]
        right = sum(rights[n] for n in idx)
        by_type = {}
        for n in idx:
            t = order[n].get("type") or "other"
            c, o = by_type.get(t, (0, 0))
            by_type[t] = (c + rights[n], o + 1)
        mx = MIDTERM_SHARE * knowledge_max(axis)
        axes[axis] = {"correct": right, "of": len(idx), "pct": round(right / len(idx), 4),
                      "points": round(mx * right / len(idx), 2), "max": mx,
                      "by_type": {t: {"correct": c, "of": o} for t, (c, o) in by_type.items()}}
    concepts = {}
    for n, it in enumerate(order):
        c, o = concepts.get(it["concept"], (0, 0))
        concepts[it["concept"]] = (c + rights[n], o + 1)
    return {"net_id": net_id, "exam": "midterm", "source": source, "taken": taken,
            "correct": sum(rights), "of": 36, "share": MIDTERM_SHARE, "axes": axes,
            "concepts": {k: {"correct": c, "of": o} for k, (c, o) in sorted(concepts.items())}}


def main():
    order = item_order()
    roster = list(csv.DictReader(open(DATA / "roster-msb341-fall2026.csv")))
    by_paper = paper(order)
    by_canvas = makeup(order)
    OUT.mkdir(parents=True, exist_ok=True)
    os.chmod(OUT, 0o700)
    (OUT / "raw").mkdir(exist_ok=True)
    for f in EXPORTS:
        shutil.copy2(f, OUT / "raw" / Path(f).name)
        os.chmod(OUT / "raw" / Path(f).name, 0o600)
    rows, none = [], []
    for r in roster:
        n = r["net_id"].lower()
        got = by_paper.get(n) or by_canvas.get(str(r.get("canvas_user_id")))
        if not got:
            none.append(n)
            continue
        g = ring(n, *got, order)
        p = OUT / f"ring-{n}.json"
        p.write_text(json.dumps(g, indent=1))
        os.chmod(p, 0o600)
        rows.append({"net_id": n, "source": g["source"], "taken": g["taken"], "correct": g["correct"],
                     **{f"{a} correct": g["axes"][a]["correct"] for a in AXES},
                     **{f"{a} points": g["axes"][a]["points"] for a in AXES}})
    with open(OUT / "midterm.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    os.chmod(OUT / "midterm.csv", 0o600)
    src = {s: sum(1 for x in rows if x["source"] == s) for s in ("paper", "make-up")}
    print(f"{len(rows)} rings ({src['paper']} paper, {src['make-up']} make-up); no midterm yet: {len(none)} {' '.join(none)}")
    print(f"  {OUT}")


if __name__ == "__main__":
    main()
