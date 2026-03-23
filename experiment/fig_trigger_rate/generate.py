#!/usr/bin/env python3
"""Generate trigger rate per-environment grid of line plots."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "data.csv")

envs = df["environment"].unique()
n_envs = len(envs)

# Layout: 2 rows x 3 cols (6 slots for up to 6 envs; last cell blank if odd)
nrows, ncols = 2, 3
fig, axes = plt.subplots(nrows, ncols, figsize=(14, 7), sharex=False, sharey=True)
axes_flat = axes.flatten()

for idx, env in enumerate(envs):
    ax = axes_flat[idx]
    sub = df[df["environment"] == env].sort_values("step")
    steps = sub["step"].values
    rates = sub["trigger_rate"].values
    ns = sub["n"].values

    # 95% binomial CI: rate +/- 1.96 * sqrt(rate*(1-rate)/n)
    se = 1.96 * np.sqrt(rates * (1 - rates) / ns)
    ci_lo = np.clip(rates - se, 0, 1)
    ci_hi = np.clip(rates + se, 0, 1)

    ax.plot(steps, rates, color="#3274a1", linewidth=1.5, marker="o", markersize=3)
    ax.fill_between(steps, ci_lo, ci_hi, color="#3274a1", alpha=0.15)

    # Overall weighted trigger rate
    overall = np.average(rates, weights=ns)
    ax.axhline(y=overall, color="#c44e52", linestyle="--", linewidth=0.9, alpha=0.7)

    ax.set_title(f"{env}  RR={overall:.2f}", fontsize=10, fontweight="bold")
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Step", fontsize=8)
    if idx % ncols == 0:
        ax.set_ylabel("Trigger Rate", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# Hide unused subplots
for idx in range(n_envs, nrows * ncols):
    axes_flat[idx].set_visible(False)

fig.suptitle("Trigger Rate by Step per Environment", fontsize=12, fontweight="bold", y=1.01)
plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
