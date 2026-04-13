#!/usr/bin/env python3
"""Generate BSW degradation vs |rho| scatter with regression."""

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

x = df["abs_rho"].values
y = df["degradation_pp"].values
safe = df["rollout_safe"].values
envs = df["environment"].values

fig, ax = plt.subplots(figsize=(3.5, 3))

# Scatter: red filled circle for non-safe, white diamond for safe
for xi, yi, s, env in zip(x, y, safe, envs):
    if s == "Yes":
        ax.scatter(xi, yi, marker="D", s=90, facecolors="white", edgecolors="#3274a1",
                   linewidths=1.5, zorder=5)
    else:
        ax.scatter(xi, yi, marker="o", s=90, facecolors="#c44e52", edgecolors="#8b0000",
                   linewidths=0.8, zorder=5)

# Annotate environment names
for xi, yi, env in zip(x, y, envs):
    ax.annotate(env, (xi, yi), textcoords="offset points", xytext=(8, 5),
                fontsize=8, color="#333333")

# Regression / trend line
coeffs = np.polyfit(x, y, 1)
poly = np.poly1d(coeffs)
x_line = np.linspace(x.min() - 0.05, x.max() + 0.05, 100)
ax.plot(x_line, poly(x_line), color="#555555", linestyle="--", linewidth=1.2)

# R-squared
ss_res = np.sum((y - poly(x)) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
ax.text(0.05, 0.95, f"$R^2 = {r2:.3f}$\nslope = {coeffs[0]:.1f} pp per unit |ρ|",
        transform=ax.transAxes, fontsize=9, verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))

# Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#c44e52",
           markeredgecolor="#8b0000", markersize=9, label="Not rollout-safe"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor="white",
           markeredgecolor="#3274a1", markersize=9, label="Rollout-safe"),
]
ax.legend(handles=legend_elements, fontsize=9, loc="lower right")

ax.set_xlabel(r"|$\rho$|  (entropy-utility correlation strength)")
ax.set_ylabel("Degradation (pp)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
