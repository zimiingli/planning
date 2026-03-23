#!/usr/bin/env python3
"""Generate matched-pair opposite-meaning bar charts (2x2 grid)."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "data.csv")

env_order = ["HotpotQA", "TWExpress", "APPS Intv", "APPS"]
difficulty_order = ["Easy", "Medium", "Hard"]

fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=True)
axes_flat = axes.flatten()

for idx, env in enumerate(env_order):
    ax = axes_flat[idx]
    sub = df[df["environment"] == env].set_index("difficulty_bin").reindex(difficulty_order)
    deltas = sub["delta_u"].values.astype(float)

    colors = ["#3274a1" if d < 0 else "#c44e52" if d > 0 else "#888888" for d in deltas]

    bars = ax.bar(difficulty_order, deltas, color=colors, edgecolor="white", width=0.55)

    # Value labels
    for bar, v in zip(bars, deltas):
        y_off = 0.008 if v >= 0 else -0.008
        va = "bottom" if v >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + y_off,
                f"{v:+.3f}", ha="center", va=va, fontsize=8)

    ax.axhline(y=0, color="black", linewidth=0.7)
    ax.set_title(env, fontsize=10, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if idx >= 2:
        ax.set_xlabel("Difficulty Bin", fontsize=9)
    if idx % 2 == 0:
        ax.set_ylabel(r"$\Delta U$ (high - low entropy)", fontsize=9)

fig.suptitle("Same Entropy Level, Opposite Utility Effect", fontsize=12, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
