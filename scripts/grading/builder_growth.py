#!/usr/bin/env python3
"""Builder profile growth from concept codings (breadth and depth).

Reads, for each sprint up to --sprint, the coder's file and its check
  _data/.../grading/sprint-N/concepts/run-A/<net_id>.json   (concept-coder.md)
  _data/.../grading/sprint-N/concepts/run-V/<net_id>.json   (concept-verifier.md: drops and depth corrections)
One coder plus a targeted check replaced two full coders on 2026-10-16 (Scott); a sprint coded the old way
(run-A and run-B, no run-V) still reads as the consensus of both. Writes
  _data/.../grading/sprint-<last>/concepts/growth-<net_id>.json

The spoke (decided 2026-10-14): 0 to 100 per axis, 100 = a full-stack product builder.
- Practice fills up to PRACTICE[axis] points (50; AI Systems 25): 70% breadth, 30% depth (weighting
  D, decided 2026-10-16; was 50/50 with linear levels, which paid three quarters of all growth out
  of depth by Sprint 2 and left little for Sprints 3 to 6).
  - Breadth: share of the axis's practicable concepts (not knowledge_only) shown in the student's
    own work, counted once, after the second check (or, for sprints coded the old way, consensus of
    both coders).
  - Depth: highest level shown on the axis so far (1 Followed to 4 Delivered), the lower of the two
    coders' levels each sprint (now: the coder's level, lowered by the check if it lowered it); points = depth share x LEVEL_SHARE[level] (1: 0, 2: 20%, 3: 50%,
    4: 100%), so following a template earns nothing and real users are the largest step.
- Knowledge fills the rest from the exams (exam rings are added by the exam step, not here).
- Start (Fall 2026 only, decided 2026-10-15): until the midterm measures knowledge, the core is the
  September survey's self-rating mapped onto the knowledge share: (mean - 1) / 4 x (100 - practice
  max), so 1 = 0 and 5 = the full knowledge share. The midterm replaces the core; the practice rings
  keep their thickness. From next term a pre-test form sets the core instead.
- Each sprint's ring is the practice points it added; rings never shrink.
- Exams (Scott, 2026-10-29): the midterm is its own ring, from midterm_ring.py (grading/midterm/ring-<net_id>.json).
  It fills its share (MIDTERM_SHARE, a half) of the knowledge half of the three axes it tests, at the plain share
  of questions right. On those axes the survey core keeps only the part no exam has measured yet, and the full
  self-rating is kept as start.survey_full for the chart's dashed outline. The final fills the rest.
"""
import argparse
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
# PM_DATA points the run at another data folder (used by the API-versus-subagent comparison).
DATA = Path(os.environ.get("PM_DATA") or Path.home() / "hubs/courses/_data/product-management")
GRADING = DATA / "grading"
PRACTICE = {"AI Systems": 25.0}          # every other axis: 50
SURVEY = DATA / "baseline-charts-fall2026" / "students.json"
LEVELS = {1: "Followed", 2: "Directed", 3: "Decided", 4: "Delivered"}
BREADTH_SHARE = 0.7
LEVEL_SHARE = {0: 0.0, 1: 0.0, 2: 0.2, 3: 0.5, 4: 1.0}
MIDTERM = GRADING / "midterm"


def concepts():
    C, axes = {}, {}
    for f in sorted((HERE / "concepts").glob("*.json")):
        d = json.loads(f.read_text())
        axes[d["axis"]] = sum(1 for c in d["concepts"] if not c.get("knowledge_only"))
        for c in d["concepts"]:
            C[c["id"]] = dict(c, axis=d["axis"])
    return C, axes


def practice_max(axis):
    return PRACTICE.get(axis, 50.0)


def concept_points(axis, axes):
    return practice_max(axis) * BREADTH_SHARE / axes[axis]


def depth_points(axis, frm, to):
    return practice_max(axis) * (1 - BREADTH_SHARE) * (LEVEL_SHARE[to] - LEVEL_SHARE[frm])


def survey():
    """net_id -> axis -> 1 to 5 mean self-rating from the September survey."""
    return {x["net_id"]: x["means"] for x in json.loads(SURVEY.read_text())} if SURVEY.exists() else {}


def start_core(means, axes):
    """The survey self-rating as points on the knowledge share of each spoke."""
    if not means:
        return {}
    return {ax: round((min(5, max(1, float(means[ax]))) - 1) / 4 * (100 - practice_max(ax)), 2)
            for ax in axes if means.get(ax) is not None}


def exams(net_id):
    """The exam rings a student has: [{"exam", "taken", "points": {axis: pts}, "share", "axes": {...}}]."""
    p = MIDTERM / f"ring-{net_id}.json"
    if not p.exists():
        return []
    m = json.loads(p.read_text())
    return [{"exam": "midterm", "taken": m.get("taken"), "share": m["share"], "correct": m["correct"], "of": m["of"],
             "points": {ax: v["points"] for ax, v in m["axes"].items()}, "axes": m["axes"]}]


def measured_core(core, rings):
    """The survey core minus the share of each axis's knowledge an exam has measured."""
    out = dict(core)
    for r in rings:
        for ax in r["points"]:
            if ax in out:
                out[ax] = round(out[ax] * (1 - r["share"]), 2)
    return out


def load(sprint, run, net_id):
    f = GRADING / f"sprint-{sprint}" / "concepts" / f"run-{run}" / f"{net_id}.json"
    return json.loads(f.read_text()) if f.exists() else None


def verified(A, V):
    """The coder's file with the check applied: dropped concepts removed, corrected depth levels used
    (never higher than the coder's). Returned in the coder's shape, so it stands in for a second coder."""
    drops = {x["concept"]: x for x in V.get("drop", [])}
    fix = {x["axis"]: x for x in V.get("depth", [])}
    depth = []
    for d in A.get("depth", []):
        f = fix.get(d["axis"])
        if f and int(f["level"]) < int(d["level"]):
            d = dict(d, level=int(f["level"]), why=f.get("why") or d.get("why", ""))
        depth.append(d)
    return {"breadth": [x for x in A.get("breadth", []) if x.get("concept") not in drops], "depth": depth,
            "seen_not_counted": A.get("seen_not_counted", []), "_drops": drops}


def growth(net_id, upto, C, axes, means=None):
    shown, depth_best, rings = set(), {}, []
    new_last, depth_last, disputed, nc_last, earlier = [], [], [], [], []
    for s in range(1, upto + 1):
        A, B, V = load(s, "A", net_id), load(s, "B", net_id), load(s, "V", net_id)
        mode = "two coders" if B else "checked"
        if A and V and not B:
            B = verified(A, V)
        if not A or not B:
            rings.append({"sprint": s, "coded": False, "breadth": {}, "depth": {}, "points": {}})
            continue
        ok = lambda x: x.get("concept") in C and not C[x["concept"]].get("knowledge_only")
        ba = {x["concept"]: x for x in A.get("breadth", []) if ok(x)}
        bb = {x["concept"]: x for x in B.get("breadth", []) if ok(x)}
        both = set(ba) & set(bb)
        new = sorted(both - shown)
        shown |= both
        da = {x["axis"]: x for x in A.get("depth", [])}
        db = {x["axis"]: x for x in B.get("depth", [])}
        ring_b, ring_d, pts = {}, {}, {}
        for k in new:
            ax = C[k]["axis"]
            p = concept_points(ax, axes)
            ring_b.setdefault(ax, []).append(k)
            pts[ax] = pts.get(ax, 0) + p
        for ax in set(da) & set(db):
            lvl = min(int(da[ax]["level"]), int(db[ax]["level"]))
            prev = depth_best.get(ax, 0)
            if lvl > prev:
                gain = depth_points(ax, prev, lvl)
                pts[ax] = pts.get(ax, 0) + gain
                ring_d[ax] = {"from": prev, "to": lvl}
                depth_best[ax] = lvl
        rings.append({"sprint": s, "coded": True, "breadth": ring_b, "depth": ring_d,
                      "points": {k: round(v, 2) for k, v in pts.items()}})
        if s < upto:
            for k in new:
                a_, c = ba[k], C[k]
                earlier.append({"sprint": s, "concept": k, "name": c["name"], "axis": c["axis"],
                                "points": round(concept_points(c["axis"], axes), 2),
                                "when": a_.get("when", ""), "did": a_.get("did", ""),
                                "evidence": a_.get("evidence", ""), "ref": a_.get("ref", "")})
            for ax, g in ring_d.items():
                earlier.append({"sprint": s, "depth": True, "axis": ax, "level": g["to"], "name": LEVELS[g["to"]],
                                "points": round(depth_points(ax, g["from"], g["to"]), 2),
                                "why": (da[ax] if int(da[ax]["level"]) <= int(db[ax]["level"]) else db[ax]).get("why", "")})
        if s == upto:
            for k in new:
                a, c = ba[k], C[k]
                new_last.append({"concept": k, "name": c["name"], "item": c["item"], "axis": c["axis"],
                                 "points": round(concept_points(c["axis"], axes), 2),
                                 "when": a.get("when", ""), "did": a.get("did", ""), "evidence": a.get("evidence", ""),
                                 "ref": a.get("ref", ""), "evidence_b": bb[k].get("evidence", "")})
            for ax in sorted(set(da) | set(db)):
                la, lb = da.get(ax, {}).get("level"), db.get(ax, {}).get("level")
                lvl = min(int(la), int(lb)) if la and lb else None
                use = da[ax] if la and (not lb or int(la) <= int(lb)) else db.get(ax, {})
                depth_last.append({"axis": ax, "level": lvl, "name": LEVELS.get(lvl, ""), "coder_levels": [la, lb],
                                   "why": use.get("why", ""), "evidence": use.get("evidence", []),
                                   "best_so_far": depth_best.get(ax, 0), "gain": ring_d.get(ax)})
            drops = B.get("_drops", {})
            disputed = [{"concept": k, "name": C[k]["name"], "coder": "A" if k in ba else "B",
                         "evidence": (ba.get(k) or bb.get(k)).get("evidence", ""),
                         "why": drops.get(k, {}).get("why", "")} for k in sorted(set(ba) ^ set(bb))]
            nca = {x["concept"]: x for x in A.get("seen_not_counted", [])}
            ncb = {x["concept"]: x for x in B.get("seen_not_counted", [])}
            nc_last = [dict(nca[i], name=C.get(i, {}).get("name", i)) for i in sorted(set(nca) & set(ncb))]
    totals = {}
    for r in rings:
        for ax, v in r["points"].items():
            totals[ax] = round(totals.get(ax, 0) + v, 2)
    core, ex = start_core(means, axes), exams(net_id)
    return {"net_id": net_id, "sprint": upto, "check": mode if upto else "",
            "start": {"source": "survey", "points": measured_core(core, ex), "survey_full": core},
            "exams": ex,
            "rings": rings, "practice_total": totals,
            "practice_max": {ax: practice_max(ax) for ax in axes}, "depth_best": depth_best,
            "concepts_shown": sorted(shown), "new": new_last, "depth": depth_last,
            "disputed": disputed, "not_counted": nc_last, "earlier": earlier}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    C, axes = concepts()
    S = survey()
    out = GRADING / f"sprint-{a.sprint}" / "concepts"
    nets = a.only or sorted(p.stem for p in (out / "run-A").glob("*.json"))
    for n in nets:
        G = growth(n, a.sprint, C, axes, S.get(n))
        (out / f"growth-{n}.json").write_text(json.dumps(G, indent=1))
        print(n, G["practice_total"], f"new {len(G['new'])}, disputed {len(G['disputed'])}")


if __name__ == "__main__":
    main()
