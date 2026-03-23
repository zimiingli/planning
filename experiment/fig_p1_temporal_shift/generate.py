#!/usr/bin/env python3
"""Generate P1 temporal shift grouped bar chart."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "data.csv")

env_order = df["environment"].unique()
phases = ["early", "late"]
phase_colors = {"early": "#3274a1", "late": "#c44e52"}
phase_labels = {"early": "Early", "late": "Late"}

n_envs = len(env_order)
x = np.arange(n_envs)
width = 0.32

fig, ax = plt.subplots(figsize=(10, 5))

for i, phase in enumerate(phases):
    sub = df[df["phase"] == phase].set_index("environment").reindex(env_order)
    offset = (i - 0.5) * width
    vals = sub["rho"].values

    # Error bars from CI if available
    ci_lo = sub["ci_lo"].values
    ci_hi = sub["ci_hi"].values
    yerr_lo = np.where(np.isnan(ci_lo), 0, vals - ci_lo)
    yerr_hi = np.where(np.isnan(ci_hi), 0, ci_hi - vals)
    yerr = np.array([yerr_lo, yerr_hi])

    bars = ax.bar(x + offset, vals, width,
                  color=phase_colors[phase], label=phase_labels[phase],
                  edgecolor="white", linewidth=0.5,
                  yerr=yerr, capsize=3, error_kw={"linewidth": 0.8})

# Annotate delta-rho between early and late
for j, env in enumerate(env_order):
    row_e = df[(df["environment"] == env) & (df["phase"] == "early")]
    row_l = df[(df["environment"] == env) & (df["phase"] == "late")]
    if len(row_e) and len(row_l):
        rho_e = row_e["rho"].values[0]
        rho_l = row_l["rho"].values[0]
        delta = rho_l - rho_e
        y_pos = max(rho_e, rho_l) + 0.06 if max(rho_e, rho_l) > 0 else min(rho_e, rho_l) - 0.08
        ax.text(j, y_pos, f"\u0394={delta:+.2f}", ha="center", va="bottom", fontsize=7,
                fontstyle="italic", color="#444444")

ax.axhline(y=0, color="black", linewidth=0.7)
ax.set_xticks(x)
ax.set_xticklabels(env_order, fontsize=9, rotation=15, ha="right")
ax.set_ylabel(r"$\rho$(entropy, U)", fontsize=11)
ax.set_title(r"P1: Entropy-Utility Correlation Shifts with Episode Progress",
             fontsize=11, fontweight="bold")
ax.legend(fontsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
fig.savefig(HERE / "output.pdf", bbox_inches="tight")
plt.close(fig)
print("Saved", HERE / "output.pdf")
