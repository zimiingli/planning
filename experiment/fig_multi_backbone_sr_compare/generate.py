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
import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path

HERE = Path(__file__).parent
ENV_ORDER = ['HotpotQA', 'APPS', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'APPS Intv', 'CRUXEval']
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
    width = 0.12
    fig, ax = plt.subplots(figsize=(16, 6))

    for bidx, bb in enumerate(BACKBONES):
        # Best fixed
        fixed_srs = [data.get((bb, env, 'best_fixed'), np.nan) for env in ENV_ORDER]
        offset_f = -1.5 * width + bidx * width
        ax.bar(x + offset_f, fixed_srs, width * 0.9,
               color=BB_FIXED_COLORS[bidx], edgecolor='white', linewidth=0.3,
               label=f'Best Fixed ({bb.split("-")[0]})' if bidx == 0 else None)

        # EAAG
        eaag_srs = [data.get((bb, env, 'EAAG'), np.nan) for env in ENV_ORDER]
        offset_e = 1.5 * width + bidx * width
        ax.bar(x + offset_e, eaag_srs, width * 0.9,
               color=BB_EAAG_COLORS[bidx], edgecolor='white', linewidth=0.3,
               label=f'EAAG ({bb.split("-")[0]})' if bidx == 0 else None)

    ax.set_xticks(x)
    ax.set_xticklabels(ENV_ORDER, fontsize=10, rotation=15, ha='right')
    ax.set_ylabel('SR (%)', fontsize=12)
    ax.set_title('Cross-Backbone: EAAG vs Best Fixed-Direction Baseline', fontsize=13, fontweight='bold')
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
    ax.legend(handles=legend_elements, fontsize=8, ncol=2, loc='upper right',
              framealpha=0.9, edgecolor='#cccccc')

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
