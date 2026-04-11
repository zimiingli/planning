#!/usr/bin/env python3
"""Generate controlled reversal figure: InfoPoor vs InfoRich.

Visual spec (appendix.tex L648-678):
- Panel (a): x = signals, paired bars InfoPoor(dark blue) vs InfoRich(light green)
  y = Spearman rho. Highlight winning signal per condition.
- Panel (b): SR performance by condition (base, always, EAAG)

Data: from data.csv (variant, rho values, SR values) + step1_signal_discovery.json
"""

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
    rows = {}
    with open(DATA_CSV, newline='') as f:
        for row in csv.DictReader(f):
            rows[row['variant']] = row

    # -- Panel (a): Signal rho comparison by signal --
    signals = ['step_count', 'token_entropy']
    signal_labels = ['step_count', 'token_entropy']

    rho_infopoor = [float(rows['InfoPoor']['step_count_rho']),
                    float(rows['InfoPoor']['entropy_rho'])]
    rho_inforich = [float(rows['InfoRich']['step_count_rho']),
                    float(rows['InfoRich']['entropy_rho'])]
    rho_original = [float(rows['Original']['step_count_rho']),
                    float(rows['Original']['entropy_rho'])]

    # -- Panel (b): SR comparison --
    conditions = ['Original', 'InfoPoor', 'InfoRich']
    base_srs = [float(rows[c]['base_sr']) for c in conditions]
    always_srs = [float(rows[c]['always_sr']) for c in conditions]
    eaag_srs = [float(rows[c]['eaag_sr']) for c in conditions]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))

    # === Panel (a): Signal rho by condition ===
    x = np.arange(len(signals))
    width = 0.25

    bars_orig = ax1.bar(x - width, rho_original, width, label='Original',
                        color='#999999', edgecolor='white', linewidth=0.5)
    bars_poor = ax1.bar(x, rho_infopoor, width, label='InfoPoor',
                        color='#2166ac', edgecolor='white', linewidth=0.5)
    bars_rich = ax1.bar(x + width, rho_inforich, width, label='InfoRich',
                        color='#4dac26', edgecolor='white', linewidth=0.5)

    # Value labels
    for bars in [bars_orig, bars_poor, bars_rich]:
        for bar in bars:
            h = bar.get_height()
            va = 'bottom' if h >= 0 else 'top'
            y_off = 0.01 if h >= 0 else -0.01
            ax1.text(bar.get_x() + bar.get_width() / 2, h + y_off,
                     f'{h:+.3f}', ha='center', va=va, fontsize=8, fontweight='bold')

    # Highlight dominant signal per condition
    # InfoPoor: step_count dominates (|rho|=0.608 > 0.119)
    # InfoRich: entropy dominates (|rho|=0.311 > 0.147)
    ax1.annotate('dominant', xy=(0, rho_infopoor[0]), xytext=(0, rho_infopoor[0] - 0.12),
                 fontsize=7, color='#2166ac', ha='center', fontstyle='italic')
    ax1.annotate('dominant', xy=(1 + width, rho_inforich[1]), xytext=(1 + width, rho_inforich[1] + 0.05),
                 fontsize=7, color='#4dac26', ha='center', fontstyle='italic')

    ax1.axhline(y=0, color='black', linewidth=0.7)
    ax1.set_xticks(x)
    ax1.set_xticklabels(signal_labels, fontsize=10)
    ax1.set_ylabel(r'Spearman $\rho$', fontsize=11)
    ax1.set_title('(a) Signal Correlations', fontsize=11, fontweight='bold')
    ax1.legend(fontsize=9, loc='lower left')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # === Panel (b): SR comparison ===
    x2 = np.arange(len(conditions))
    width2 = 0.25

    ax2.bar(x2 - width2, base_srs, width2, label='Base', color='#92c5de', edgecolor='white')
    ax2.bar(x2, always_srs, width2, label='Always Trigger', color='#f4a582', edgecolor='white')
    ax2.scatter(x2 + width2, eaag_srs, color='crimson', marker='*', s=200,
                zorder=5, edgecolors='darkred', linewidths=0.5, label='EAAG')

    # Value labels for EAAG
    for i, (c, sr) in enumerate(zip(conditions, eaag_srs)):
        ax2.text(x2[i] + width2, sr + 1.5, f'{sr:.1f}%', ha='center', va='bottom',
                 fontsize=9, color='crimson', fontweight='bold')

    ax2.set_xticks(x2)
    ax2.set_xticklabels(conditions, fontsize=10)
    ax2.set_ylabel('SR (%)', fontsize=11)
    ax2.set_title('(b) Task Performance', fontsize=11, fontweight='bold')
    ax2.legend(fontsize=9, loc='upper left')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.set_ylim(0, 108)

    fig.suptitle('Controlled Information Manipulation: Signal Hierarchy Shift',
                 fontsize=13, fontweight='bold', y=1.02)

    add_ygrid(ax1)
    add_ygrid(ax2)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
