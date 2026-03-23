#!/usr/bin/env python3
"""Generate controlled direction reversal figure."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from pathlib import Path
import numpy as np

# Read data
data_path = Path(__file__).parent / "data.csv"
with open(data_path) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

variants = [r["variant"] for r in rows]
entropy_rho = [float(r["entropy_rho"]) for r in rows]
step_count_rho = [float(r["step_count_rho"]) for r in rows]
base_sr = [float(r["base_sr"]) for r in rows]
always_sr = [float(r["always_sr"]) for r in rows]
eaag_sr = [float(r["eaag_sr"]) for r in rows]

x = np.arange(len(variants))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Left subplot: Signal Correlations
bars1 = ax1.bar(x - width / 2, entropy_rho, width, label="entropy_rho", color="tab:blue")
bars2 = ax1.bar(x + width / 2, step_count_rho, width, label="step_count_rho", color="tab:orange")
ax1.axhline(0, color="black", linewidth=0.8)
ax1.set_xticks(x)
ax1.set_xticklabels(variants)
ax1.set_ylabel("ρ")
ax1.set_title("Signal Correlations by Information Availability")
ax1.legend()

# Value labels
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, h,
             f"{h:+.3f}", ha="center", va="bottom" if h >= 0 else "top", fontsize=8)
for bar in bars2:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, h,
             f"{h:+.3f}", ha="center", va="bottom" if h >= 0 else "top", fontsize=8)

# Right subplot: Task Performance
bars3 = ax2.bar(x - width / 2, base_sr, width, label="base_sr", color="tab:blue")
bars4 = ax2.bar(x + width / 2, always_sr, width, label="always_sr", color="tab:orange")
ax2.scatter(x, eaag_sr, color="red", marker="D", zorder=5, s=60, label="eaag_sr")
ax2.set_xticks(x)
ax2.set_xticklabels(variants)
ax2.set_ylabel("SR (%)")
ax2.set_title("Task Performance")
ax2.legend()

fig.suptitle("Controlled Direction Reversal: Same Task, Different Information Structure",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])

output_path = Path(__file__).parent / "output.pdf"
fig.savefig(output_path)
plt.close(fig)
print(f"Saved {output_path}")
