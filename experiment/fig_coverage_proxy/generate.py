#!/usr/bin/env python3
"""Generate coverage-proxy scatter: coverage vs entropy-rho."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "data.csv")

x = df["mean_coverage"].values
y = df["entropy_rho"].values
sizes = df["n_records"].values
envs = df["environment"].values

# Normalize point sizes: scale to reasonable marker range
size_min, size_max = 80, 400
s_norm = (sizes - sizes.min()) / (sizes.max() - sizes.min() + 1e-9)
s_plot = size_min + s_norm * (size_max - size_min)

# Colors based on rho threshold
colors = []
for rho in y:
    if rho < -0.1:
        colors.append("#3274a1")  # blue
    elif rho > 0.1:
        colors.append("#c44e52")  # red
    else:
        colors.append("#999999")  # gray

fig, ax = plt.subplots(figsize=(8, 5.5))

ax.scatter(x, y, s=s_plot, c=colors, edgecolors="white", linewidths=0.6, alpha=0.85, zorder=5)

# Annotate env names
for xi, yi, env in zip(x, y, envs):
    ax.annotate(env, (xi, yi), textcoords="offset points", xytext=(8, 6),
                fontsize=8, color="#333333")

# Trend line
coeffs = np.polyfit(x, y, 1)
poly = np.poly1d(coeffs)
x_line = np.linspace(x.min() - 0.05, x.max() + 0.05, 100)
ax.plot(x_line, poly(x_line), color="#555555", linestyle="--", linewidth=1.2)

# R-squared
ss_res = np.sum((y - poly(x)) ** 2)
ss_tot = np.sum((y - y.mean()) ** 2)
r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
ax.text(0.05, 0.05, f"$R^2 = {r2:.3f}$\nslope = {coeffs[0]:.3f}",
        transform=ax.transAxes, fontsize=9, verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))

# Legend for colors
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#3274a1",
           markersize=9, label=r"$\rho < -0.1$"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#999999",
           markersize=9, label=r"$-0.1 \leq \rho \leq 0.1$"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#c44e52",
           markersize=9, label=r"$\rho > 0.1$"),
]
ax.legend(handles=legend_elements, fontsize=8, loc="upper right")

ax.set_xlabel("Mean Information Coverage", fontsize=11)
ax.set_ylabel(r"$\rho$(entropy, utility)", fontsize=11)
ax.set_title("Information Coverage Predicts Entropy-Utility Direction",
             fontsize=11, fontweight="bold")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
