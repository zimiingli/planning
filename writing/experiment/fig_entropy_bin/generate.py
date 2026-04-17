#!/usr/bin/env python3
"""Figure: SR by entropy bin (ref: SEAG Figure 4).

Spec (experiments.tex L143-177):
- 1x3 panels: (a) Type I (HotpotQA), (b) Mixed (APPS), (c) Type D (APPS Intv)
  Note: using available data — HotpotQA, FEVER, APPS Intv
- Grouped bar chart: methods per entropy bin
- Annotate proportion of steps at top
- DIAL = red/crimson, baselines = blue/green/gray
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

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    envs = []
    for r in rows:
        if r['environment'] not in envs:
            envs.append(r['environment'])

    type_labels = {'HotpotQA': '(a) Type I: HotpotQA',
                   'FEVER': '(a) Type I: FEVER',
                   'APPS': '(c) Type D: APPS'}
    # Use whatever envs are in data
    n_envs = len(envs)
    fig, axes = plt.subplots(1, n_envs, figsize=(7, 3), sharey=True)
    if n_envs == 1:
        axes = [axes]

    colors = {'Q1 (low)': '#4393c3', 'Q2': '#92c5de', 'Q3': '#f4a582', 'Q4 (high)': '#d6604d'}

    for idx, env in enumerate(envs):
        ax = axes[idx]
        env_rows = [r for r in rows if r['environment'] == env]

        bins = [r['entropy_bin'] for r in env_rows]
        utilities = [float(r['mean_utility']) for r in env_rows]
        proportions = [float(r['proportion']) for r in env_rows]
        n_steps = [int(r['n_steps']) for r in env_rows]

        bar_colors = [colors.get(b, '#888888') for b in bins]
        x = np.arange(len(bins))

        bars = ax.bar(x, utilities, color=bar_colors, edgecolor='white', width=0.7)

        # Annotate proportion on top
        for i, (bar, prop, n) in enumerate(zip(bars, proportions, n_steps)):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{prop:.0%}\n(n={n})', ha='center', va='bottom', fontsize=7,
                    color='#444444')

        # Annotate utility value inside bar
        for i, (bar, u) in enumerate(zip(bars, utilities)):
            if u > 0.05:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                        f'{u:.2f}', ha='center', va='center', fontsize=7,
                        color='white', fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels(bins)
        ax.set_xlabel('Entropy Bin')
        title = type_labels.get(env, env)
        ax.set_title(title, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        add_ygrid(ax)

    axes[0].set_ylabel('Mean Utility')

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
