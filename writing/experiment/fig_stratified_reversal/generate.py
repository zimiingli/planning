#!/usr/bin/env python3
"""Generate stratified reversal grouped bar chart."""

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

env_order = df["environment"].unique()
strata = ["Early", "Mid", "Late"]
stratum_colors = {"Early": "#a6c8e0", "Mid": "#3274a1", "Late": "#14425a"}

n_envs = len(env_order)
n_strata = len(strata)
x = np.arange(n_envs)
width = 0.22

fig, ax = plt.subplots(figsize=(3.5, 3))

for i, stratum in enumerate(strata):
    sub = df[df["stratum"] == stratum].set_index("environment").reindex(env_order)
    offset = (i - 1) * width
    vals = sub["rho"].values.astype(float)
    # Replace nan with 0 for plotting, mark them
    is_nan = np.isnan(vals)
    vals_plot = np.where(is_nan, 0, vals)

    bars = ax.bar(x + offset, vals_plot, width,
                  color=stratum_colors[stratum], label=stratum,
                  edgecolor="white", linewidth=0.5)

    # Value labels
    for j, (bar, v, nan_flag) in enumerate(zip(bars, vals, is_nan)):
        if nan_flag:
            label_text = "n/a"
        else:
            label_text = f"{v:.3f}"
        y_offset = 0.012 if v >= 0 else -0.012
        va = "bottom" if v >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + y_offset if v >= 0 else bar.get_height() - 0.012,
                label_text, ha="center", va=va, fontsize=6.5)

ax.axhline(y=0, color="black", linewidth=0.7)
ax.set_xticks(x)
ax.set_xticklabels(env_order, fontsize=9, rotation=15, ha="right")
ax.set_ylabel(r"$\rho$ within stratum")
ax.legend(fontsize=9, title="Stratum")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
