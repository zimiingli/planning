#!/usr/bin/env python3
"""Figure A4: Multi-backbone signal direction heatmap.

Spec (appendix.tex L445-472):
- 3 panels side by side (Qwen3-4B, Phi-3.5, Llama-3.1-8B)
- Rows = 8 environments, Columns = key signals
- Cell color = Spearman rho (RdBu diverging)
- Same color scale across all panels
- Annotate rho values inside cells
- Bold border on cells where sign flips across backbones
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

ENV_ORDER = ['HotpotQA', 'APPS', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'APPS Intv', 'CRUXEval']
BACKBONES = ['Qwen3-4B', 'Phi-3.5-mini', 'Llama-3.1-8B']
BB_TITLES = ['Qwen3-4B', 'Phi-3.5-mini', 'Llama-3.1-8B']
# Focus on key signals only
KEY_SIGNALS = ['token_entropy', 'step_count']

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    fig, axes = plt.subplots(1, 3, figsize=(7, 3.2), sharey=True)

    for bidx, (bb, title) in enumerate(zip(BACKBONES, BB_TITLES)):
        ax = axes[bidx]
        matrix = np.full((len(ENV_ORDER), len(KEY_SIGNALS)), np.nan)
        pvals = np.full((len(ENV_ORDER), len(KEY_SIGNALS)), 1.0)

        for row in rows:
            if row['backbone'] != bb:
                continue
            if row['signal'] not in KEY_SIGNALS:
                continue
            try:
                ei = ENV_ORDER.index(row['environment'])
                si = KEY_SIGNALS.index(row['signal'])
            except ValueError:
                continue
            matrix[ei, si] = float(row['rho'])
            pvals[ei, si] = float(row['p_value'])

        im = ax.imshow(matrix, cmap='RdBu_r', vmin=-0.7, vmax=0.7, aspect='auto')

        ax.set_xticks(range(len(KEY_SIGNALS)))
        ax.set_xticklabels(KEY_SIGNALS, rotation=45, ha='right', fontsize=9)
        if bidx == 0:
            ax.set_yticks(range(len(ENV_ORDER)))
            ax.set_yticklabels(ENV_ORDER, fontsize=9)
        ax.set_title(title, fontsize=11, fontweight='bold')

        # Annotate values
        for i in range(len(ENV_ORDER)):
            for j in range(len(KEY_SIGNALS)):
                val = matrix[i, j]
                if np.isnan(val):
                    continue
                color = 'white' if abs(val) > 0.35 else 'black'
                star = '*' if pvals[i, j] < 0.05 else ''
                ax.text(j, i, f'{val:+.2f}{star}', ha='center', va='center',
                        fontsize=8, color=color, fontweight='bold')

    # Check sign flips and mark them
    for i in range(len(ENV_ORDER)):
        for j in range(len(KEY_SIGNALS)):
            vals = []
            for bb in BACKBONES:
                for row in rows:
                    if (row['backbone'] == bb and row['signal'] == KEY_SIGNALS[j]
                            and row['environment'] == ENV_ORDER[i]):
                        v = float(row['rho'])
                        p = float(row['p_value'])
                        if p < 0.05:
                            vals.append(v)
            if len(vals) >= 2:
                signs = [np.sign(v) for v in vals if v != 0]
                if len(set(signs)) > 1:  # sign flip
                    for bidx in range(3):
                        rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                             linewidth=2.5, edgecolor='gold',
                                             facecolor='none', zorder=10)
                        axes[bidx].add_patch(rect)

    cbar = fig.colorbar(im, ax=axes, shrink=0.7, pad=0.02)
    cbar.set_label(r'Spearman $\rho$', fontsize=10)

    fig.suptitle('Signal Direction Across Three Backbones', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
