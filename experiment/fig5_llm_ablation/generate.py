#!/usr/bin/env python3
"""Generate Figure 5: LLM Feature Ablation."""

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

    envs = [row['environment'] for row in rows]
    eaag_sr = [float(row['eaag_sr']) for row in rows]
    v2_sr = [float(row['v2_no_llm_sr']) for row in rows]
    contribution = [float(row['llm_contribution_pp']) for row in rows]

    n = len(envs)
    x = np.arange(n)
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(x - width / 2, eaag_sr, width, color='steelblue',
                   edgecolor='white', label='EAAG (with LLM)')
    bars2 = ax.bar(x + width / 2, v2_sr, width, color='lightcoral',
                   edgecolor='white', label='v2 (no LLM)')

    # Annotate contribution above each group
    for i in range(n):
        top = max(eaag_sr[i], v2_sr[i])
        sign = '+' if contribution[i] >= 0 else ''
        ax.annotate(f'{sign}{contribution[i]:.1f} pp',
                    xy=(x[i], top + 1.0),
                    ha='center', va='bottom', fontsize=8,
                    color='darkgreen' if contribution[i] > 0 else 'red',
                    fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(envs, fontsize=9)
    ax.set_ylabel('Success Rate (%)', fontsize=11)
    ax.set_title('LLM Feature Ablation', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Set y-axis to give room for annotations
    y_max = max(max(eaag_sr), max(v2_sr)) + 8
    ax.set_ylim(0, y_max)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
