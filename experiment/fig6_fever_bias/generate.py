#!/usr/bin/env python3
"""Generate Figure 6: FEVER Exploration Bias -- SCG vs EAAG Data."""

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

    metrics = [row['metric'] for row in rows]
    scg_vals = [float(row['scg_phase1']) for row in rows]
    eaag_vals = [float(row['eaag_explore']) for row in rows]

    n = len(metrics)
    x = np.arange(n)
    width = 0.35

    fig, ax = plt.subplots(figsize=(3.5, 2.8))

    bars1 = ax.bar(x - width / 2, scg_vals, width, color='#e07b54',
                   edgecolor='white', label='SCG Phase-1')
    bars2 = ax.bar(x + width / 2, eaag_vals, width, color='#5b9bd5',
                   edgecolor='white', label='EAAG Explore')

    # Add value labels on each bar
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                f'{h:g}', ha='center', va='bottom', fontsize=8)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                f'{h:g}', ha='center', va='bottom', fontsize=8)

    # Format metric labels for readability
    display_labels = [m.replace('_', ' ').title() for m in metrics]
    ax.set_xticks(x)
    ax.set_xticklabels(display_labels, fontsize=9, rotation=20, ha='right')
    ax.set_ylabel('Value', fontsize=11)
    ax.set_title('FEVER Exploration Bias: SCG vs EAAG Data', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
