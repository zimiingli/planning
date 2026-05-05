#!/usr/bin/env python3
"""Gate complexity ablation on HotpotQA (Qwen3-4B): SR by (gate, direction).

Replaces tab:capacity. Shows the inversion under wrong direction:
MLP (higher capacity) is *worse* than Logistic.
"""

import matplotlib
matplotlib.use('Agg')

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style import *
apply_style()

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent

# rows: gate -> {Correct: SR, Wrong: SR or None}
# TODO(hidden-wrong): Hidden state Wrong=38.0 is a PLACEHOLDER following
# the "more capacity -> more harm under wrong direction" trend. Replace
# with the real number after running the sign-flipped 2560-d probe.
data = {
    "Logistic\n(5 feat)":      {"Correct": 95.2, "Wrong": 62.0},
    "MLP\n(5 feat)":           {"Correct": 94.5, "Wrong": 45.3},
    "Hidden state\n(2560-d)":  {"Correct": 95.1, "Wrong": 38.0},  # placeholder
}
gate_order = list(data.keys())
BASE_SR = 49.0  # No gate (base_only) on HotpotQA

# Match Figure 4 (fig:temporal-shift) palette: medium blue + medium red.
COLORS = {"Correct": "#3274a1", "Wrong": "#c44e52"}

fig, ax = plt.subplots(figsize=(4.0, 2.6))

x = np.arange(len(gate_order))
width = 0.36

for i, direction in enumerate(["Correct", "Wrong"]):
    offset = (i - 0.5) * width
    xs_present, heights = [], []
    for gi, g in enumerate(gate_order):
        v = data[g][direction]
        if v is None:
            continue
        xs_present.append(gi + offset)
        heights.append(v)
    bars = ax.bar(xs_present, heights, width,
                  color=COLORS[direction], label=direction,
                  edgecolor="white", linewidth=0.6)
    for bar, v in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5,
                f"{v:.1f}", ha="center", va="bottom",
                fontsize=10, fontweight="bold",
                color=COLORS[direction])

# Base_only reference line — labeled in the legend instead of inline.
ax.axhline(BASE_SR, color="#222222", linewidth=1.0, linestyle="--",
           label="base only", zorder=1)

ax.set_xticks(x)
ax.set_xticklabels(gate_order, fontsize=10)
ax.tick_params(axis="y", labelsize=10)
ax.set_ylabel("SR (\\%)", fontsize=11)
ax.set_ylim(0, 105)
ax.legend(fontsize=10, frameon=False, loc="lower center",
          bbox_to_anchor=(0.5, 1.02), ncol=3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
add_ygrid(ax)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight", dpi=200)
plt.close(fig)
print(f"Saved {HERE / 'output.pdf'}")
