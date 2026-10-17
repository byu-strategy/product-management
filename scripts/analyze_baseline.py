#!/usr/bin/env python3
"""Curriculum readout from the MSB 341 baseline survey.

    python3 ~/courses/product-management/scripts/analyze_baseline.py [export.xlsx]

Answers the questions a syllabus actually turns on: which specific skills the cohort is
weakest at, how wide the spread is on each axis, whether the two sections need different
treatment, and how many students are already past the level a session would teach.

Item-level is the useful grain. An axis mean of 2.1 tells you to spend time on architecture;
the item means tell you it is schema design and auth, not version control, which is a
different session.

Writes charts to _data/product-management/baseline-analysis/ and prints the numbers.
Student data goes only to _data and _private, never to git.
"""
import csv, json, statistics as st, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude/skills/foundry-baseline-charts/scripts"))
sys.path.insert(0, str(Path(__file__).parent))
import parse_baseline as pb
import people_match as pm

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA = Path.home() / "hubs/courses/_data/product-management"
ROSTER = DATA / "roster-msb341-fall2026.csv"
STATUS = DATA / "student-status.csv"
OUT = DATA / "baseline-analysis"
AXES = pb.AXES
SHORT = {"Discovery": "Discovery", "Design": "Design",
         "Application Architecture": "App Arch", "AI Systems": "AI Systems",
         "Agentic Workflow": "Agentic", "Launch and Learn": "Launch"}
INK, ACCENT, MUTED = "#1a1a1a", "#4340d6", "#b9b8e8"


def newest_export():
    found = sorted(Path.home().glob("Downloads/AI Foundry Baseline*.xlsx"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    return found[0] if found else sys.exit("No baseline export found in ~/Downloads.")


def items_by_student(export, roster):
    """(net_id, axis, item) -> score, for roster students only."""
    rows = pb.load_rows(export)
    hdr, data = rows[0], rows[1:]
    colmap = pb.build_axis_map(hdr)
    name_col = hdr.index("Name")
    email_col = next(i for i, h in enumerate(hdr) if "email" in h.lower())
    idx = pm.index(roster)

    out = defaultdict(dict)
    for r in data:
        if not any((c or "").strip() for c in r):
            continue
        student, _ = pm.find(idx, email=(r[email_col] or "").strip(),
                             display=(r[name_col] or "").strip())
        if not student:
            continue
        for i, cell in enumerate(r):
            mapped = colmap[i] if i < len(colmap) else None
            v = pb.val(cell) if mapped else None
            if v:
                out[student["net_id"]].setdefault((mapped[0], mapped[1]), v)
    return out


def main():
    export = Path(sys.argv[1]) if len(sys.argv) > 1 else newest_export()
    OUT.mkdir(parents=True, exist_ok=True)
    roster = [s for s in csv.DictReader(ROSTER.open(newline="", encoding="utf-8-sig"))
              if s["enrollment_state"] == "active"]
    section = {s["net_id"]: s["section"].split(":")[0] for s in roster}
    per_item = items_by_student(export, roster)

    status = {r["net_id"]: r for r in csv.DictReader(STATUS.open(newline="", encoding="utf-8"))}
    scored = {n: r for n, r in status.items() if r["baseline_mean"]}
    axis_vals = {a: [float(r[a.lower().replace(" ", "_")]) for r in scored.values()]
                 for a in AXES}

    # 1. axis distribution
    fig, ax = plt.subplots(figsize=(11, 5.5))
    data = [axis_vals[a] for a in AXES]
    bp = ax.boxplot(data, patch_artist=True, widths=.55, medianprops=dict(color=INK, lw=2),
                    flierprops=dict(marker="", ms=0))
    for patch in bp["boxes"]:
        patch.set(facecolor=MUTED, edgecolor=ACCENT, alpha=.65)
    for i, vals in enumerate(data, 1):
        ax.scatter(np.random.normal(i, .07, len(vals)), vals, s=14, color=ACCENT, alpha=.45,
                   zorder=3)
    ax.set_xticks(range(1, len(AXES) + 1))
    ax.set_xticklabels([SHORT[a] for a in AXES])
    ax.set_ylim(.8, 5.2); ax.set_ylabel("self-rating, 1 to 5")
    ax.set_title(f"MSB 341 baseline: spread by axis (n={len(scored)})", fontsize=13, color=INK)
    ax.grid(axis="y", alpha=.25); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "axis-spread.png", dpi=150, facecolor="white")
    plt.close(fig)

    # 2. weakest items
    item_scores = defaultdict(list)
    for net_id, items in per_item.items():
        for (axis, item), v in items.items():
            item_scores[(axis, item)].append(v)
    ranked = sorted(((st.mean(v), len(v), a, i) for (a, i), v in item_scores.items() if len(v) >= 20))

    fig, ax = plt.subplots(figsize=(11, 8))
    worst = ranked[:18][::-1]
    labels = [f"{i[:44]}  ({SHORT[a]})" for _, _, a, i in worst]
    ax.barh(range(len(worst)), [m for m, _, _, _ in worst], color=ACCENT, alpha=.8, height=.7)
    ax.set_yticks(range(len(worst))); ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(1, 3.4); ax.set_xlabel("cohort mean, 1 to 5")
    ax.set_title("Weakest items in the cohort", fontsize=13, color=INK)
    for i, (m, n, _, _) in enumerate(worst):
        ax.text(m + .02, i, f"{m:.2f}", va="center", fontsize=8.5, color=INK)
    ax.grid(axis="x", alpha=.25); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "weakest-items.png", dpi=150, facecolor="white")
    plt.close(fig)

    # 3. sections compared
    secs = sorted({section.get(n, "") for n in scored})
    fig, ax = plt.subplots(figsize=(11, 5))
    width = .38
    for k, sec in enumerate(secs):
        vals = [st.mean([float(scored[n][a.lower().replace(" ", "_")])
                         for n in scored if section.get(n) == sec]) for a in AXES]
        ax.bar(np.arange(len(AXES)) + k * width, vals, width,
               label=f"{sec} (n={sum(1 for n in scored if section.get(n) == sec)})",
               color=[ACCENT, MUTED][k], alpha=.9)
    ax.set_xticks(np.arange(len(AXES)) + width / 2)
    ax.set_xticklabels([SHORT[a] for a in AXES])
    ax.set_ylabel("mean self-rating"); ax.set_ylim(0, 4)
    ax.set_title("Baseline by section", fontsize=13, color=INK)
    ax.legend(frameon=False); ax.grid(axis="y", alpha=.25); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "by-section.png", dpi=150, facecolor="white")
    plt.close(fig)

    # 4. readiness bands per axis: how many are already past what a session would teach
    fig, ax = plt.subplots(figsize=(11, 5))
    bands = [("1.0 - 1.9  no exposure", 1, 2), ("2.0 - 2.9  aware", 2, 3),
             ("3.0 - 3.9  can do with help", 3, 4), ("4.0 - 5.0  independent", 4, 5.01)]
    bottom = np.zeros(len(AXES))
    colors = ["#2b2a86", ACCENT, "#8f8de0", "#d8d7f4"]
    for (label, lo, hi), c in zip(bands, colors):
        counts = [sum(1 for v in axis_vals[a] if lo <= v < hi) for a in AXES]
        ax.bar([SHORT[a] for a in AXES], counts, bottom=bottom, label=label, color=c)
        for i, (cnt, b) in enumerate(zip(counts, bottom)):
            if cnt >= 4:
                ax.text(i, b + cnt / 2, str(cnt), ha="center", va="center", fontsize=9,
                        color="white" if c != "#d8d7f4" else INK)
        bottom += counts
    ax.set_ylabel(f"students (n={len(scored)})")
    ax.set_title("Where students already are, by axis", fontsize=13, color=INK)
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(.5, -.08), ncol=4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "readiness-bands.png", dpi=150, facecolor="white")
    plt.close(fig)

    # readout
    print(f"n = {len(scored)} of {len(roster)} enrolled\n")
    print("AXIS MEANS, weakest first")
    for a in sorted(AXES, key=lambda a: st.mean(axis_vals[a])):
        v = axis_vals[a]
        print(f"  {a:<26} {st.mean(v):.2f}   sd {st.pstdev(v):.2f}   "
              f"range {min(v):.1f}-{max(v):.1f}   "
              f"{sum(1 for x in v if x >= 3.5)} at 3.5+   {sum(1 for x in v if x < 2)} under 2")

    print("\nWEAKEST 12 ITEMS")
    for m, n, a, i in ranked[:12]:
        print(f"  {m:.2f}  {i[:52]:<52} ({SHORT[a]}, n={n})")
    print("\nSTRONGEST 6 ITEMS")
    for m, n, a, i in ranked[-6:][::-1]:
        print(f"  {m:.2f}  {i[:52]:<52} ({SHORT[a]}, n={n})")

    print("\nLOWEST AXIS PER STUDENT")
    low = defaultdict(int)
    for r in scored.values():
        low[r["baseline_low_axis"]] += 1
    for a, n in sorted(low.items(), key=lambda kv: -kv[1]):
        print(f"  {n:>3}  {a}")

    print("\nBY SECTION")
    for sec in secs:
        vals = [float(scored[n]["baseline_mean"]) for n in scored if section.get(n) == sec]
        print(f"  {sec:<16} n={len(vals):<3} overall {st.mean(vals):.2f}")

    means = sorted(float(r["baseline_mean"]) for r in scored.values())
    print(f"\nOVERALL  mean {st.mean(means):.2f}  median {st.median(means):.2f}  "
          f"quartiles {np.percentile(means, 25):.2f} / {np.percentile(means, 75):.2f}")
    print(f"  {sum(1 for m in means if m < 2)} students under 2.0, "
          f"{sum(1 for m in means if m >= 3.5)} at 3.5 or above")
    print(f"\ncharts: {OUT}")


if __name__ == "__main__":
    main()
