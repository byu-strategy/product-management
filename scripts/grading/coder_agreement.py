#!/usr/bin/env python3
"""How well two independent concept coders agree (the gate before profiles reach students).

Reads sprint-N/concepts/run-A and run-B (shape in concept-coder.md) for students coded by both and
prints, and writes to sprint-N/concepts/agreement.md:
- Breadth: positive agreement (2 x both / (A + B)), which ignores the many concepts neither coder
  saw, and Cohen's kappa over every (student, practicable concept) pair; overall and per axis; and
  the concepts that disagree most.
- Depth: per (student, axis) either coder rated, exact agreement, within one level, and the share of
  axes only one coder rated.
Targets (2026-10-14): breadth positive agreement 0.80+; depth same or one apart on 80%+ of axes.

Usage: python3 coder_agreement.py --sprint 2
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADING = Path.home() / "hubs/courses/_data/product-management/grading"


def kappa(a, b, both, n):
    """Cohen's kappa for two yes/no raters over n items, given the yes counts and the both-yes count."""
    if n == 0:
        return float("nan")
    po = (both + (n - a - b + both)) / n
    pe = (a / n) * (b / n) + ((n - a) / n) * ((n - b) / n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    s = ap.parse_args().sprint
    C, practicable = {}, defaultdict(set)
    for f in (HERE / "concepts").glob("*.json"):
        d = json.loads(f.read_text())
        for c in d["concepts"]:
            C[c["id"]] = (d["axis"], c["name"])
            if not c.get("knowledge_only"):
                practicable[d["axis"]].add(c["id"])
    base = GRADING / f"sprint-{s}" / "concepts"
    nets = sorted(p.stem for p in (base / "run-A").glob("*.json") if (base / "run-B" / p.name).exists())
    per_axis = defaultdict(lambda: Counter())
    per_concept = defaultdict(lambda: Counter())
    depth = []
    for n in nets:
        A = json.loads((base / "run-A" / f"{n}.json").read_text())
        B = json.loads((base / "run-B" / f"{n}.json").read_text())
        sa = {x["concept"] for x in A.get("breadth", []) if x.get("concept") in C}
        sb = {x["concept"] for x in B.get("breadth", []) if x.get("concept") in C}
        for ax, ids in practicable.items():
            a, b = sa & ids, sb & ids
            per_axis[ax].update(a=len(a), b=len(b), both=len(a & b), n=len(ids))
        for k in sa | sb:
            per_concept[k].update(a=k in sa, b=k in sb, both=(k in sa and k in sb))
        da = {x["axis"]: int(x["level"]) for x in A.get("depth", []) if x.get("level")}
        db = {x["axis"]: int(x["level"]) for x in B.get("depth", []) if x.get("level")}
        for ax in set(da) | set(db):
            depth.append((n, ax, da.get(ax), db.get(ax)))
    lines = [f"# Coder agreement, Sprint {s} ({len(nets)} students coded by both)", ""]
    tot = Counter()
    for c in per_axis.values():
        tot.update(c)
    pa = 2 * tot["both"] / max(1, tot["a"] + tot["b"])
    lines += ["## Breadth", "",
              f"Overall: positive agreement **{pa:.2f}** (target 0.80), kappa {kappa(tot['a'], tot['b'], tot['both'], tot['n']):.2f}; "
              f"coder A {tot['a']} credits, coder B {tot['b']}, both {tot['both']}.", "",
              "| Axis | A | B | Both | Positive agreement | Kappa |", "|---|--:|--:|--:|--:|--:|"]
    for ax, c in sorted(per_axis.items()):
        lines.append(f"| {ax} | {c['a']} | {c['b']} | {c['both']} | {2 * c['both'] / max(1, c['a'] + c['b']):.2f} | "
                     f"{kappa(c['a'], c['b'], c['both'], c['n']):.2f} |")
    worst = sorted(per_concept.items(), key=lambda kv: (kv[1]["both"] / max(1, kv[1]["a"] + kv[1]["b"] - kv[1]["both"]), -(kv[1]["a"] + kv[1]["b"])))
    lines += ["", "Concepts with the most disagreement (credited by one coder only):", ""]
    for k, c in worst[:15]:
        if c["a"] + c["b"] - 2 * c["both"] > 0:
            lines.append(f"- {k} {C[k][1]} ({C[k][0]}): A {c['a']}, B {c['b']}, both {c['both']}")
    both_rated = [(a, b) for _, _, a, b in depth if a and b]
    exact = sum(a == b for a, b in both_rated)
    within = sum(abs(a - b) <= 1 for a, b in both_rated)
    lines += ["", "## Depth", "",
              f"Axes rated by both: {len(both_rated)}; exact **{exact / max(1, len(both_rated)):.0%}**, "
              f"within one level **{within / max(1, len(both_rated)):.0%}** (target 80%). "
              f"Axes rated by only one coder: {sum(1 for _, _, a, b in depth if bool(a) != bool(b))}.", "",
              "| Student | Axis | A | B |", "|---|---|--:|--:|"]
    for n, ax, a, b in sorted(depth):
        lines.append(f"| {n} | {ax} | {a or ''} | {b or ''} |")
    out = "\n".join(lines) + "\n"
    (base / "agreement.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
