#!/usr/bin/env python3
"""Generate AUC hierarchy grouped bar chart."""

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

# Pivot: rows = environment, columns = signal_level
signal_order = ["single_entropy", "best_single", "multi_signal_lr", "hidden_state_lr"]
env_order = df["environment"].unique()

pivot = df.pivot(index="environment", columns="signal_level", values="auc")
pivot = pivot.reindex(index=env_order, columns=signal_order)

# Plot settings
colors = ["#b0b0b0", "#707070", "#3274a1", "#c44e52"]
labels = ["Single Entropy", "Best Single", "Multi-Signal LR", "Hidden-State LR"]
n_envs = len(env_order)
n_bars = len(signal_order)
x = np.arange(n_envs)
width = 0.18

fig, ax = plt.subplots(figsize=(3.5, 2.5))

for i, (sig, color, label) in enumerate(zip(signal_order, colors, labels)):
    offset = (i - (n_bars - 1) / 2) * width
    vals = pivot[sig].values
    bars = ax.bar(x + offset, vals, width, color=color, label=label, edgecolor="white", linewidth=0.5)
    # Value labels
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                f"{v:.3f}", ha="center", va="bottom", fontsize=7)

# Dashed line at AUC = 0.5
ax.axhline(y=0.5, color="black", linestyle="--", linewidth=0.8, alpha=0.6, label="Random (AUC=0.5)")

ax.set_ylim(0.4, 1.0)
ax.set_xticks(x)
ax.set_xticklabels(env_order)
ax.set_ylabel("AUC")
ax.legend(loc="upper left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

add_ygrid(ax)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
