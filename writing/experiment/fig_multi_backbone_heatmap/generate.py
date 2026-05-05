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
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import csv
from pathlib import Path

# Diverging palette aligned with Table 2 highlights:
#   negative end -> tab10 blue (#1f77b4)  | mid -> white
#   positive end -> DIAL crimson (#DC143C)
# At |rho| ~0.35 the gradient sits near Table 2's
# #E5EDF7 (light blue) / #FBE7EB (light crimson) tints.
FIG2_CMAP = LinearSegmentedColormap.from_list(
    'fig2_diverging',
    ['#1f77b4', '#FFFFFF', '#DC143C'],
)

HERE = Path(__file__).parent

ENV_ORDER = ['HotpotQA', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'APPS']
BACKBONES = ['Qwen3-4B', 'Phi-3.5-mini', 'Llama-3.1-8B']
BB_TITLES = ['Qwen3-4B', 'Phi-3.5-mini', 'Llama-3.1-8B']
# Focus on key signals only
KEY_SIGNALS = ['token_entropy', 'step_count']

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    # Pre-compute sign-flip cells: (env_idx, signal_idx) where significant
    # rho changes sign across backbones.
    flip_cells = set()
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
                if len(set(signs)) > 1:
                    flip_cells.add((i, j))

    fig, axes = plt.subplots(1, 3, figsize=(7, 3.2), sharey=True,
                              gridspec_kw={'wspace': 0.15, 'right': 0.88})

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

        im = ax.imshow(matrix, cmap=FIG2_CMAP, vmin=-0.7, vmax=0.7, aspect='auto')

        ax.set_xticks(range(len(KEY_SIGNALS)))
        ax.set_xticklabels(KEY_SIGNALS, rotation=0, ha='center', fontsize=7)
        if bidx == 0:
            ax.set_yticks(range(len(ENV_ORDER)))
            ax.set_yticklabels(ENV_ORDER, fontsize=7)
        ax.set_title(title, fontsize=9)

        # Annotate values; sign-flip cells get an extra ⇄ marker.
        for i in range(len(ENV_ORDER)):
            for j in range(len(KEY_SIGNALS)):
                val = matrix[i, j]
                if np.isnan(val):
                    continue
                color = 'white' if abs(val) > 0.45 else 'black'
                star = '*' if pvals[i, j] < 0.05 else ''
                flip_mark = r' $\rightleftarrows$' if (i, j) in flip_cells else ''
                ax.text(j, i, f'{val:+.2f}{star}{flip_mark}',
                        ha='center', va='center',
                        fontsize=7, color=color)

    cbar_ax = fig.add_axes([0.90, 0.15, 0.015, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label(r'Spearman $\rho$', fontsize=7)
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
