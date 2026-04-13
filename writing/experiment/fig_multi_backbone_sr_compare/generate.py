#!/usr/bin/env python3
"""Figure A5: Cross-backbone SR comparison — EAAG vs best fixed baseline.

Spec (appendix.tex L474-495):
- Grouped bar chart. x = 8 environments.
- 2 groups of 3 bars: best-fixed (blue shades), EAAG (red shades)
- Lighter=Qwen3, Medium=Phi-3.5, Darker=Llama
- Annotate delta-SR per backbone
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
ENV_ORDER = ['HotpotQA', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'APPS']
BACKBONES = ['Qwen3-4B', 'Phi-3.5-mini', 'Llama-3.1-8B']
BB_FIXED_COLORS = ['#92c5de', '#4393c3', '#2166ac']  # light to dark blue
BB_EAAG_COLORS = ['#f4a582', '#d6604d', '#b2182b']   # light to dark red

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    # Build lookup: (backbone, env, category) -> sr
    data = {}
    for row in rows:
        key = (row['backbone'], row['environment'], row['category'])
        data[key] = float(row['sr_pct'])

    x = np.arange(len(ENV_ORDER))
    w = 0.10          # single bar width
    gap = 0.08        # gap between blue group and red group
    fig, ax = plt.subplots(figsize=(8, 2.8))

    # 6 bar positions: [-2.5w-gap/2, -1.5w-gap/2, -0.5w-gap/2,
    #                    +0.5w+gap/2, +1.5w+gap/2, +2.5w+gap/2]
    for bidx, bb in enumerate(BACKBONES):
        # Best fixed (left group: positions 0,1,2)
        fixed_srs = [data.get((bb, env, 'best_fixed'), np.nan) for env in ENV_ORDER]
        off_f = -(1.5 - bidx) * w - gap / 2
        ax.bar(x + off_f, fixed_srs, w * 0.92,
               color=BB_FIXED_COLORS[bidx], edgecolor='white', linewidth=0.3)

        # EAAG (right group: positions 3,4,5)
        eaag_srs = [data.get((bb, env, 'EAAG'), np.nan) for env in ENV_ORDER]
        off_e = (0.5 + bidx) * w + gap / 2
        ax.bar(x + off_e, eaag_srs, w * 0.92,
               color=BB_EAAG_COLORS[bidx], edgecolor='white', linewidth=0.3)

    ax.set_xticks(x)
    ax.set_xticklabels(ENV_ORDER, rotation=0, ha='center')
    ax.set_ylabel('SR (%)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Custom legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=BB_FIXED_COLORS[0], label='Best Fixed (Qwen3)'),
        Patch(facecolor=BB_FIXED_COLORS[1], label='Best Fixed (Phi-3.5)'),
        Patch(facecolor=BB_FIXED_COLORS[2], label='Best Fixed (Llama)'),
        Patch(facecolor=BB_EAAG_COLORS[0], label='EAAG (Qwen3)'),
        Patch(facecolor=BB_EAAG_COLORS[1], label='EAAG (Phi-3.5)'),
        Patch(facecolor=BB_EAAG_COLORS[2], label='EAAG (Llama)'),
    ]
    ax.legend(handles=legend_elements, ncol=2, loc='upper right',
              framealpha=0.9, edgecolor='#cccccc')

    add_ygrid(ax)

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
