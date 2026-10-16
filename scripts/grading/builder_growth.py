#!/usr/bin/env python3
"""Builder profile growth from two independent concept codings (breadth and depth).

Reads, for each sprint up to --sprint, the two coders' files
  _data/.../grading/sprint-N/concepts/run-A/<net_id>.json and run-B/<net_id>.json
(shape in concept-coder.md) and writes
  _data/.../grading/sprint-<last>/concepts/growth-<net_id>.json

The spoke (decided 2026-10-14): 0 to 100 per axis, 100 = a full-stack product builder.
- Practice fills up to PRACTICE[axis] points (50; AI Systems 25), half breadth, half depth.
  - Breadth: share of the axis's practicable concepts (not knowledge_only) shown in the student's
    own work, counted once, consensus of both coders.
  - Depth: highest level shown on the axis so far (1 Followed to 4 Delivered), the lower of the two
    coders' levels each sprint; points = half of practice x level / 4.
- Knowledge fills the rest from the exams (exam rings are added by the exam step, not here).
- Start (Fall 2026 only, decided 2026-10-15): until the midterm measures knowledge, the core is the
  September survey's self-rating mapped onto the knowledge share: (mean - 1) / 4 x (100 - practice
  max), so 1 = 0 and 5 = the full knowledge share. The midterm replaces the core; the practice rings
  keep their thickness. From next term a pre-test form sets the core instead.
- Each sprint's ring is the practice points it added; rings never shrink.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = Path.home() / "hubs/courses/_data/product-management"
GRADING = DATA / "grading"
PRACTICE = {"AI Systems": 25.0}          # every other axis: 50
SURVEY = DATA / "baseline-charts-fall2026" / "students.json"
LEVELS = {1: "Followed", 2: "Directed", 3: "Decided", 4: "Delivered"}


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


def survey():
    """net_id -> axis -> 1 to 5 mean self-rating from the September survey."""
    return {x["net_id"]: x["means"] for x in json.loads(SURVEY.read_text())} if SURVEY.exists() else {}


def start_core(means, axes):
    """The survey self-rating as points on the knowledge share of each spoke."""
    if not means:
        return {}
    return {ax: round((min(5, max(1, float(means[ax]))) - 1) / 4 * (100 - practice_max(ax)), 2)
            for ax in axes if means.get(ax) is not None}


def load(sprint, run, net_id):
    f = GRADING / f"sprint-{sprint}" / "concepts" / f"run-{run}" / f"{net_id}.json"
    return json.loads(f.read_text()) if f.exists() else None


def growth(net_id, upto, C, axes, means=None):
    shown, depth_best, rings = set(), {}, []
    new_last, depth_last, disputed, nc_last, earlier = [], [], [], [], []
    for s in range(1, upto + 1):
        A, B = load(s, "A", net_id), load(s, "B", net_id)
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
            p = (practice_max(ax) / 2) / axes[ax]
            ring_b.setdefault(ax, []).append(k)
            pts[ax] = pts.get(ax, 0) + p
        for ax in set(da) & set(db):
            lvl = min(int(da[ax]["level"]), int(db[ax]["level"]))
            prev = depth_best.get(ax, 0)
            if lvl > prev:
                gain = (practice_max(ax) / 2) * (lvl - prev) / 4
                pts[ax] = pts.get(ax, 0) + gain
                ring_d[ax] = {"from": prev, "to": lvl}
                depth_best[ax] = lvl
        rings.append({"sprint": s, "coded": True, "breadth": ring_b, "depth": ring_d,
                      "points": {k: round(v, 2) for k, v in pts.items()}})
        if s < upto:
            for k in new:
                a_, c = ba[k], C[k]
                earlier.append({"sprint": s, "concept": k, "name": c["name"], "axis": c["axis"],
                                "points": round((practice_max(c["axis"]) / 2) / axes[c["axis"]], 2),
                                "when": a_.get("when", ""), "did": a_.get("did", ""),
                                "evidence": a_.get("evidence", ""), "ref": a_.get("ref", "")})
            for ax, g in ring_d.items():
                earlier.append({"sprint": s, "depth": True, "axis": ax, "level": g["to"], "name": LEVELS[g["to"]],
                                "points": round((practice_max(ax) / 2) * (g["to"] - g["from"]) / 4, 2),
                                "why": (da[ax] if int(da[ax]["level"]) <= int(db[ax]["level"]) else db[ax]).get("why", "")})
        if s == upto:
            for k in new:
                a, c = ba[k], C[k]
                new_last.append({"concept": k, "name": c["name"], "item": c["item"], "axis": c["axis"],
                                 "points": round((practice_max(c["axis"]) / 2) / axes[c["axis"]], 2),
                                 "when": a.get("when", ""), "did": a.get("did", ""), "evidence": a.get("evidence", ""),
                                 "ref": a.get("ref", ""), "evidence_b": bb[k].get("evidence", "")})
            for ax in sorted(set(da) | set(db)):
                la, lb = da.get(ax, {}).get("level"), db.get(ax, {}).get("level")
                lvl = min(int(la), int(lb)) if la and lb else None
                use = da[ax] if la and (not lb or int(la) <= int(lb)) else db.get(ax, {})
                depth_last.append({"axis": ax, "level": lvl, "name": LEVELS.get(lvl, ""), "coder_levels": [la, lb],
                                   "why": use.get("why", ""), "evidence": use.get("evidence", []),
                                   "best_so_far": depth_best.get(ax, 0), "gain": ring_d.get(ax)})
            disputed = [{"concept": k, "name": C[k]["name"], "coder": "A" if k in ba else "B",
                         "evidence": (ba.get(k) or bb.get(k)).get("evidence", "")} for k in sorted(set(ba) ^ set(bb))]
            nca = {x["concept"]: x for x in A.get("seen_not_counted", [])}
            ncb = {x["concept"]: x for x in B.get("seen_not_counted", [])}
            nc_last = [dict(nca[i], name=C.get(i, {}).get("name", i)) for i in sorted(set(nca) & set(ncb))]
    totals = {}
    for r in rings:
        for ax, v in r["points"].items():
            totals[ax] = round(totals.get(ax, 0) + v, 2)
    return {"net_id": net_id, "sprint": upto, "start": {"source": "survey", "points": start_core(means, axes)},
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
