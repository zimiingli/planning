#!/usr/bin/env python3
"""Generate Figure 1: Signal-Utility Direction Heatmap."""

import matplotlib
matplotlib.use('Agg')

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style import *
apply_style()

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

    # Extract unique environments and signals in order of appearance
    env_order = []
    signal_order = []
    for row in rows:
        env = row['environment']
        sig = row['signal']
        if env not in env_order:
            env_order.append(env)
        if sig not in signal_order:
            signal_order.append(sig)

    # Build matrix (environments x signals), NaN for missing
    matrix = np.full((len(env_order), len(signal_order)), np.nan)
    for row in rows:
        i = env_order.index(row['environment'])
        j = signal_order.index(row['signal'])
        matrix[i, j] = float(row['spearman_rho'])

    # Create figure
    fig, ax = plt.subplots(figsize=(7, 3))

    # Plot heatmap
    import matplotlib.colors as mcolors
    cmap = plt.cm.get_cmap('RdBu_r')
    cmap.set_bad(color='#f0f0f0')  # light gray for missing values
    im = ax.imshow(matrix, cmap=cmap, vmin=-0.7, vmax=0.7, aspect='auto')

    # Set ticks
    ax.set_xticks(np.arange(len(signal_order)))
    ax.set_yticks(np.arange(len(env_order)))
    ax.set_xticklabels(signal_order, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(env_order, fontsize=9)

    # Add text annotations
    for i in range(len(env_order)):
        for j in range(len(signal_order)):
            val = matrix[i, j]
            if not np.isnan(val):
                color = 'white' if abs(val) > 0.4 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                        fontsize=7, color=color)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('Spearman $\\rho$')

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
