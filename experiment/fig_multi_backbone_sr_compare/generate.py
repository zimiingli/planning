#!/usr/bin/env python3
"""Figure: Cross-backbone SR comparison — DIAL vs best fixed baseline.
Per-environment subplots with auto y-axis range."""
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
from matplotlib.patches import Patch

HERE = Path(__file__).parent
ENV_ORDER = ['HotpotQA', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'APPS']
BACKBONES = ['Qwen3-4B', 'Phi-3.5-mini', 'Llama-3.1-8B']
BB_LABELS = ['Qwen3', 'Phi-3.5', 'Llama']
BB_FIXED_COLORS = ['#92c5de', '#4393c3', '#2166ac']
BB_DIAL_COLORS = ['#f4a582', '#d6604d', '#b2182b']

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    data = {}
    for row in rows:
        key = (row['backbone'], row['environment'], row['category'])
        data[key] = float(row['sr_pct'])

    fig, axes = plt.subplots(2, 3, figsize=(7, 4))
    axes = axes.flatten()

    x = np.arange(len(BACKBONES))
    w = 0.35

    for idx, env in enumerate(ENV_ORDER):
        ax = axes[idx]

        fixed_srs = [data.get((bb, env, 'best_fixed'), np.nan) for bb in BACKBONES]
        dial_srs = [data.get((bb, env, 'DIAL'), np.nan) for bb in BACKBONES]

        ax.bar(x - w/2, fixed_srs, w, color='#4393c3', edgecolor='white',
               linewidth=0.5, label='Best Fixed')
        ax.bar(x + w/2, dial_srs, w, color='#d6604d', edgecolor='white',
               linewidth=0.5, label='DIAL')

        # Auto y-axis zoom
        all_vals = [v for v in fixed_srs + dial_srs if not np.isnan(v)]
        if all_vals:
            v_min = min(all_vals)
            v_max = max(all_vals)
            pad = max((v_max - v_min) * 0.2, 3.0)
            ax.set_ylim(max(0, v_min - pad), min(100, v_max + pad))

        # Value labels on bars
        for xi, (fv, ev) in enumerate(zip(fixed_srs, dial_srs)):
            if not np.isnan(fv):
                ax.text(xi - w/2, fv + 0.5, f'{fv:.0f}', ha='center', va='bottom',
                        fontsize=6, color='#333333')
            if not np.isnan(ev):
                ax.text(xi + w/2, ev + 0.5, f'{ev:.0f}', ha='center', va='bottom',
                        fontsize=6, color='#333333')

        ax.set_xticks(x)
        ax.set_xticklabels(BB_LABELS, fontsize=7)
        ax.set_title(env, fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if idx % 3 == 0:
            ax.set_ylabel('SR (%)', fontsize=8)
        add_ygrid(ax)

    # Shared legend
    legend_elements = [
        Patch(facecolor='#4393c3', label='Best Fixed'),
        Patch(facecolor='#d6604d', label='DIAL'),
    ]
    fig.legend(handles=legend_elements, loc='upper center', ncol=2,
               fontsize=9, bbox_to_anchor=(0.5, 1.02), frameon=False)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
