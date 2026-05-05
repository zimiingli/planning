#!/usr/bin/env python3
"""Generate P1 temporal shift grouped bar chart."""

import matplotlib
matplotlib.use('Agg')

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style import *
apply_style()

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "data.csv")

env_order = ["HotpotQA", "APPS", "WebShop", "FEVER", "TWExpress"]
phases = ["early", "late"]
phase_colors = {"early": "#3274a1", "late": "#c44e52"}
phase_labels = {"early": "Early", "late": "Late"}

n_envs = len(env_order)
x = np.arange(n_envs)
width = 0.35

fig, ax = plt.subplots(figsize=(4.0, 2.5))

for i, phase in enumerate(phases):
    sub = df[df["phase"] == phase].set_index("environment").reindex(env_order)
    offset = (i - 0.5) * width
    vals = sub["rho"].values

    bars = ax.bar(x + offset, vals, width,
                  color=phase_colors[phase], label=phase_labels[phase],
                  edgecolor="white", linewidth=0.5)

    # Stagger labels: Early always above zero, Late always below zero.
    # Color matches bar so reader can associate label with bar even when
    # the label is displaced to the opposite side of the axis.
    for bar, v in zip(bars, vals):
        if np.isnan(v):
            continue
        if phase == "early":
            y_pos = max(0.0, v) + 0.04
            va = "bottom"
        else:  # late
            y_pos = min(0.0, v) - 0.04
            va = "top"
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f"{v:+.2f}", ha="center", va=va, fontsize=10,
                fontweight="bold", color=phase_colors[phase])

ax.axhline(y=0, color="black", linewidth=0.7)
ax.set_xticks(x)
ax.set_xticklabels(env_order, fontsize=10)
ax.tick_params(axis="y", labelsize=10)
ax.set_ylabel(r"$\rho$(entropy, U)", fontsize=11)
ax.legend(fontsize=10, frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

add_ygrid(ax)

# Pad y-limits so bold labels don't crowd the top/bottom edges
y_lo, y_hi = ax.get_ylim()
ax.set_ylim(y_lo - 0.05, y_hi + 0.05)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight", dpi=200)
plt.close(fig)
print("Saved", HERE / "output.pdf")
