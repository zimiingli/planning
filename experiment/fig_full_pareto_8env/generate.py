#!/usr/bin/env python3
"""Figure A7: Full Pareto frontier (all 8 environments, 3 backbones).

Spec (appendix.tex L815-830):
- 2x4 grid (all 8 environments)
- Same format as main-text Pareto (fig2_pareto)
- One backbone at a time (Qwen3 for now; extend to 3-backbone panels later)
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

ENV_ORDER = ['HotpotQA', 'APPS', 'APPS Intv', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'CRUXEval']
# Use display names from data
ENV_ALIASES = {'APPS Intro': 'APPS', 'APPS': 'APPS'}

EAAG = {'EAAG', 'se_few5_filter_local'}
BOUNDS = {'base_only', 'always_trigger', 'oracle'}
FIXED_CB = {'CaTS', 'SEAG', 'CoRefine', 'CATTS', 'AUQ', 's1_budget',
            'cats', 'seag', 'corefine', 'catts', 'auq'}
CB_COLORS = {'CaTS': '#1f77b4', 'SEAG': '#ff7f0e', 'CoRefine': '#2ca02c',
             'CATTS': '#9467bd', 'AUQ': '#8c564b', 's1_budget': '#e377c2'}

def categorize(m):
    if m in EAAG: return 'eaag'
    if m in BOUNDS: return 'bounds'
    if m in FIXED_CB: return 'cb'
    return 'other'

def pareto_front(pts):
    if len(pts) == 0: return []
    order = pts[:, 0].argsort()
    ps = pts[order]
    front, mx = [0], ps[0, 1]
    for i in range(1, len(ps)):
        if ps[i, 1] >= mx:
            front.append(i); mx = ps[i, 1]
    return order[front]

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    # Group by (backbone, environment)
    env_data = {}
    for row in rows:
        env = row['environment']
        bb = row['backbone']
        key = (bb, env)
        if key not in env_data:
            env_data[key] = []
        env_data[key].append(row)

    # Plot Qwen3 only for the full 8-env view
    backbone = 'Qwen3-4B'
    fig, axes = plt.subplots(2, 4, figsize=(7, 4))
    axes = axes.flatten()

    for idx, env in enumerate(ENV_ORDER):
        ax = axes[idx]
        key = (backbone, env)
        # Try alternate name
        if key not in env_data:
            for alt in ['APPS Intro', 'APPS Intv']:
                if (backbone, alt) in env_data and alt == env:
                    key = (backbone, alt)
                    break
        if key not in env_data:
            ax.set_title(env, fontsize=10, fontweight='bold')
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            continue

        data = env_data[key]
        points = []
        for row in data:
            m = row['method']
            cat = categorize(m)
            if cat == 'other':
                continue
            cost = float(row['cost_ro_per_ep']) if row['cost_ro_per_ep'] else 0
            sr = float(row['sr_pct'])
            points.append((cost, sr, cat, m))

        for cost, sr, cat, m in points:
            if cat == 'bounds':
                ax.scatter(cost, sr, c='#888888', marker='o', s=40, alpha=0.8,
                           edgecolors='#555555', linewidths=0.4, zorder=3)
            elif cat == 'cb':
                color = CB_COLORS.get(m, '#17becf')
                ax.scatter(cost, sr, c=color, marker='^', s=45, alpha=0.85, zorder=4)
            elif cat == 'eaag':
                ax.scatter(cost, sr, c='crimson', marker='*', s=220,
                           edgecolors='darkred', linewidths=0.5, zorder=10)

        # Pareto frontier
        pp = np.array([(c, s) for c, s, _, _ in points])
        if len(pp) >= 2:
            fi = pareto_front(pp)
            fp = pp[fi][pp[fi][:, 0].argsort()]
            ax.plot(fp[:, 0], fp[:, 1], '--', color='#333', linewidth=0.8, alpha=0.5)
            ax.fill_between(fp[:, 0], 0, fp[:, 1], alpha=0.03, color='#333')

        ax.set_title(env, fontsize=10, fontweight='bold')
        ax.set_xlabel('Cost', fontsize=8)
        if idx % 4 == 0:
            ax.set_ylabel('SR (%)', fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=7)

    fig.suptitle(f'Pareto Frontier — All 8 Environments ({backbone})',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
