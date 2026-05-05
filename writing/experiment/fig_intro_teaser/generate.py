#!/usr/bin/env python3
"""Intro teaser: entropy-gate direction flips across all 6 environments.

Compact single-column horizontal bar chart of Spearman rho(token_entropy, U)
across the 6 agent environments on Qwen3-4B. Sign of rho determines whether
triggering on high-entropy helps or harms; a fixed-direction gate must be
wrong on at least one side.

Data source: ../tab_signal_discovery/data.csv
"""
import matplotlib
matplotlib.use('Agg')

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from style import *
apply_style()

import matplotlib.pyplot as plt

# Bump fonts by one notch for this teaser figure (local override only)
plt.rcParams.update({
    'font.size':       FONT_TICK   + 1,
    'axes.labelsize':  FONT_LABEL  + 1,
    'xtick.labelsize': FONT_TICK   + 1,
    'ytick.labelsize': FONT_TICK   + 1,
    'legend.fontsize': FONT_LEGEND + 1,
})
from pathlib import Path
import csv

HERE = Path(__file__).parent

ENV_LABEL = {
    'HotpotQA':  'HotpotQA',
    'FEVER':     'FEVER',
    'TWExpress': 'TWExpress',
    'WebShop':   'WebShop',
    'APPS':      'APPS',
    'Plancraft': 'Plancraft',
}

WEAK_THRESH = 0.05


def main():
    src = HERE.parent / 'tab_signal_discovery' / 'data.csv'
    with open(src, newline='') as f:
        rows = list(csv.DictReader(f))

    items = [(r['environment'], float(r['entropy_rho'])) for r in rows]
    items.sort(key=lambda t: t[1])

    envs = [ENV_LABEL.get(e, e) for e, _ in items]
    rhos = [r for _, r in items]

    def bar_color(r):
        if abs(r) < WEAK_THRESH:
            return ZERO_COLOR
        return TYPE_I_COLOR if r < 0 else TYPE_D_COLOR

    colors = [bar_color(r) for r in rhos]

    fig, ax = plt.subplots(figsize=(3.3, 2.3))
    y = list(range(len(envs)))

    # Shaded band: prior-work assumption (rho > 0)
    ax.axvspan(0, 0.48, facecolor=TYPE_D_COLOR, alpha=0.08, zorder=0)

    ax.barh(y, rhos, color=colors, edgecolor='white', height=0.68, zorder=3)

    for yi, r in zip(y, rhos):
        offset = 0.012 if r >= 0 else -0.012
        ax.text(r + offset, yi, f'{r:+.2f}',
                va='center',
                ha='left' if r >= 0 else 'right',
                fontsize=FONT_ANNOT + 1, color='#333333')

    ax.axvline(0, color='#555555', linewidth=0.8, zorder=2)

    # Single top annotation over the shaded assumption region (right-aligned)
    ax.text(0.98, 1.03,
            r'prior-work assumption: $\rho > 0$',
            transform=ax.transAxes,
            color=TYPE_D_COLOR, fontsize=FONT_LABEL + 1, fontweight='bold',
            ha='right', va='bottom')

    ax.set_yticks(y)
    ax.set_yticklabels(envs)
    ax.set_xlabel(r'Spearman $\rho$ (token entropy, utility)')
    ax.set_xlim(-0.48, 0.48)
    ax.set_ylim(-0.7, len(envs) - 0.2)

    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.grid(True, alpha=GRID_ALPHA, color=GRID_COLOR,
                  linestyle=GRID_STYLE, zorder=1)
    ax.set_axisbelow(True)

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')


if __name__ == '__main__':
    main()
