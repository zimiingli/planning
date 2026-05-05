#!/usr/bin/env python3
"""Generate trigger rate per-environment grid of line plots.

Visual spec (experiments.tex L208-237):
- 2x3 grid, 6 environments
- Order by Delta (rollout headroom): TWExpress first, Plancraft last
- Solid blue line with shaded 95% CI band
- Horizontal dashed GRAY line at 50% for reference
- Annotate overall RR in each panel corner
- Title case environment names
"""

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

# Order by Delta (rollout headroom): high to low
# TWExpress(+31.8), WebShop(+35.8), HotpotQA(+48.0), FEVER(+62.8), APPS(-), Plancraft(-7.0)
ENV_ORDER = ['TWExpress', 'HotpotQA', 'FEVER', 'WebShop', 'APPS', 'Plancraft']
ENV_DISPLAY = {
    'twexpress': 'TWExpress', 'hotpotqa': 'HotpotQA', 'fever': 'FEVER',
    'webshop': 'WebShop', 'apps': 'APPS', 'plancraft': 'Plancraft',
    'TWExpress': 'TWExpress', 'HotpotQA': 'HotpotQA', 'FEVER': 'FEVER',
    'WebShop': 'WebShop', 'APPS': 'APPS', 'Plancraft': 'Plancraft',
}

# Map data environment names to canonical order
env_col = df["environment"].values
all_envs = df["environment"].unique()

# Build canonical map
env_map = {}
for e in all_envs:
    for canon in ENV_ORDER:
        if e.lower().replace(' ', '') == canon.lower().replace(' ', ''):
            env_map[e] = canon
            break
    if e not in env_map:
        env_map[e] = e

df["env_canon"] = df["environment"].map(env_map)

nrows, ncols = 2, 3
fig, axes = plt.subplots(nrows, ncols, figsize=(7, 3.8), sharey=True)
axes_flat = axes.flatten()

for idx, env_canon in enumerate(ENV_ORDER):
    ax = axes_flat[idx]
    sub = df[df["env_canon"] == env_canon].sort_values("step")

    if len(sub) == 0:
        ax.set_title(ENV_DISPLAY.get(env_canon, env_canon))
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
        continue

    steps = sub["step"].values
    rates = sub["trigger_rate"].values
    ns = sub["n"].values

    # 95% binomial CI
    se = 1.96 * np.sqrt(rates * (1 - rates) / np.maximum(ns, 1))
    ci_lo = np.clip(rates - se, 0, 1)
    ci_hi = np.clip(rates + se, 0, 1)

    ax.plot(steps, rates, color="#3274a1", linewidth=1.5, marker="o", markersize=3)
    ax.fill_between(steps, ci_lo, ci_hi, color="#3274a1", alpha=0.15)

    # 50% reference line (gray dashed, per spec)
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)

    # Overall weighted trigger rate
    overall = np.average(rates, weights=ns)

    # Annotate RR in corner (not title)
    display_name = ENV_DISPLAY.get(env_canon, env_canon)
    ax.set_title(display_name)
    ax.text(0.97, 0.95, f"RR={overall:.0%}", transform=ax.transAxes,
            ha='right', va='top', fontsize=9, color='#c44e52', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='none'))

    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("Step", fontsize=8)
    if idx % ncols == 0:
        ax.set_ylabel("Trigger Rate", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    add_ygrid(ax)

# Hide unused subplots
n_envs = len(ENV_ORDER)
for idx in range(n_envs, nrows * ncols):
    axes_flat[idx].set_visible(False)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight", dpi=200)
plt.close(fig)
print("Saved", HERE / "output.pdf")
