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

    # Label each bar with its rho value
    for bar, v in zip(bars, vals):
        if np.isnan(v):
            continue
        if v >= 0:
            y_pos = v + 0.01
            va = "bottom"
        else:
            y_pos = v - 0.01
            va = "top"
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f"{v:+.2f}", ha="center", va=va, fontsize=5.5,
                color="#444444")

ax.axhline(y=0, color="black", linewidth=0.7)
ax.set_xticks(x)
ax.set_xticklabels(env_order, fontsize=8)
ax.set_ylabel(r"$\rho$(entropy, U)", fontsize=9)
ax.legend(fontsize=8, frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

add_ygrid(ax)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight", dpi=200)
plt.close(fig)
print("Saved", HERE / "output.pdf")
