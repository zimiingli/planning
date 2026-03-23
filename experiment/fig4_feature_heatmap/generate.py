#!/usr/bin/env python3
"""Generate Figure 4: EAAG Feature Selection Heatmap."""

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

    # Extract unique environments and features in order of appearance
    env_order = []
    feature_order = []
    for row in rows:
        env = row['environment']
        feat = row['feature']
        if env not in env_order:
            env_order.append(env)
        if feat not in feature_order:
            feature_order.append(feat)

    # Build binary matrix (environments x features)
    matrix = np.zeros((len(env_order), len(feature_order)), dtype=int)
    for row in rows:
        i = env_order.index(row['environment'])
        j = feature_order.index(row['feature'])
        matrix[i, j] = int(row['selected'])

    # Create figure
    fig, ax = plt.subplots(figsize=(max(10, len(feature_order) * 0.5),
                                     max(3, len(env_order) * 0.6)))

    # Binary heatmap: dark = selected (1), light = not selected (0)
    cmap = plt.cm.get_cmap('Greys')
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect='auto')

    # Set ticks
    ax.set_xticks(np.arange(len(feature_order)))
    ax.set_yticks(np.arange(len(env_order)))
    ax.set_xticklabels(feature_order, rotation=60, ha='right', fontsize=7)
    ax.set_yticklabels(env_order, fontsize=9)

    # Add grid lines to separate cells
    ax.set_xticks(np.arange(-0.5, len(feature_order), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(env_order), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.5)
    ax.tick_params(which='minor', size=0)

    ax.set_title("EAAG Feature Selection Across Environments", fontsize=12, pad=10)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02, ticks=[0, 1])
    cbar.ax.set_yticklabels(['Not Selected', 'Selected'], fontsize=8)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
