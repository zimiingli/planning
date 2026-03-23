#!/usr/bin/env python3
"""Generate Figure 3: Cost of Wrong BSW Direction."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path

HERE = Path(__file__).parent
DATA_CSV = HERE / "data.csv"
OUTPUT_PDF = HERE / "output.pdf"


def main():
    # Read data
    rows = []
    with open(DATA_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Separate safe and non-safe points
    safe_x, safe_y, safe_labels = [], [], []
    nonsafe_x, nonsafe_y, nonsafe_labels = [], [], []

    for row in rows:
        x = float(row['abs_rho'])
        y = float(row['degradation_pp'])
        env = row['environment']
        is_safe = row['rollout_safe'].strip().lower() == 'yes'

        if is_safe:
            safe_x.append(x)
            safe_y.append(y)
            safe_labels.append(env)
        else:
            nonsafe_x.append(x)
            nonsafe_y.append(y)
            nonsafe_labels.append(env)

    fig, ax = plt.subplots(figsize=(7, 5))

    # Non-safe: red filled circles
    ax.scatter(nonsafe_x, nonsafe_y, c='red', marker='o', s=80,
               edgecolors='darkred', linewidths=0.8, zorder=5, label='Not Rollout-Safe')

    # Safe: white diamonds with black edge
    ax.scatter(safe_x, safe_y, c='white', marker='D', s=80,
               edgecolors='black', linewidths=1.2, zorder=5, label='Rollout-Safe')

    # Annotate environment names
    offset = 0.012
    for x, y, label in zip(nonsafe_x, nonsafe_y, nonsafe_labels):
        ax.annotate(label, (x, y), textcoords='offset points',
                    xytext=(8, 5), fontsize=8, color='red')
    for x, y, label in zip(safe_x, safe_y, safe_labels):
        ax.annotate(label, (x, y), textcoords='offset points',
                    xytext=(8, 5), fontsize=8, color='black')

    # Linear trend line for non-safe points
    if len(nonsafe_x) >= 2:
        ns_x = np.array(nonsafe_x)
        ns_y = np.array(nonsafe_y)
        coeffs = np.polyfit(ns_x, ns_y, 1)
        poly = np.poly1d(coeffs)
        x_range = np.linspace(min(ns_x) - 0.05, max(ns_x) + 0.05, 100)
        ax.plot(x_range, poly(x_range), '--', color='gray', linewidth=1, alpha=0.7,
                label=f'Trend (non-safe): y={coeffs[0]:.1f}x{coeffs[1]:+.1f}')

    ax.set_xlabel('|Spearman $\\rho$| (Signal Strength)', fontsize=11)
    ax.set_ylabel('Degradation (pp)', fontsize=11)
    ax.set_title('Cost of Wrong Direction', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
