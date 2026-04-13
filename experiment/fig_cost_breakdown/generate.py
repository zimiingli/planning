#!/usr/bin/env python3
"""Figure A8: Computational cost breakdown — grouped bar chart showing ×base.

Shows total normalized cost per method, decomposed into:
- Base proposer cost (steps × C_base)
- Gate overhead cost (CATTS K=5 voting, AUQ confidence query)
- Rollout cost (triggers × C_rollout)
All normalized by base_only cost per episode.
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
COST_CSV = HERE.parent / "tab_cost_components" / "cost_xbase_per_env.csv"
CONSTANTS_CSV = HERE.parent / "tab_cost_components" / "token_cost_constants.csv"
MAIN_CSV = HERE.parent / "tab_main_results" / "data.csv"

def main():
    # Read ×base per env
    xbase = {}
    with open(COST_CSV, newline='') as f:
        for row in csv.DictReader(f):
            method = row['method']
            vals = []
            for env in ['HotpotQA', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft', 'APPS']:
                v = row.get(env, '')
                if v:
                    vals.append(float(v))
            if vals:
                xbase[method] = np.mean(vals)

    # Methods to show (exclude base_only and always_trigger)
    methods = ['s1_budget', 'SEAG', 'CoRefine', 'EAAG', 'CaTS', 'AUQ', 'CATTS']
    methods = [m for m in methods if m in xbase]

    # Sort by total cost
    methods.sort(key=lambda m: xbase[m])

    # Gate overhead type
    gate_type = {'CATTS': 'K=5 voting', 'AUQ': '+1 query'}
    phase1 = {'SEAG': 200, 'CoRefine': 200, 'CaTS': 200, 'EAAG': 50}

    vals = [xbase[m] for m in methods]
    colors = []
    for m in methods:
        if m == 'EAAG':
            colors.append('#d62728')
        elif m in gate_type:
            colors.append('#9467bd')  # purple for gate-overhead methods
        elif m in phase1 and phase1[m] > 0:
            colors.append('#1f77b4')  # blue for calibration methods
        else:
            colors.append('#7f7f7f')

    fig, ax = plt.subplots(figsize=(4, 3))
    x = np.arange(len(methods))
    bars = ax.barh(x, vals, color=colors, edgecolor='white', linewidth=0.5, height=0.6)

    # Highlight EAAG with thicker border
    for i, m in enumerate(methods):
        if m == 'EAAG':
            bars[i].set_edgecolor('darkred')
            bars[i].set_linewidth(2)

    # Annotate ×base on bars
    for i, v in enumerate(vals):
        label = f'{v:.1f}×'
        if methods[i] in gate_type:
            label += f' ({gate_type[methods[i]]})'
        ax.text(v + 0.15, i, label, va='center', fontsize=8)

    # Phase 1 annotation
    for i, m in enumerate(methods):
        if m in phase1 and phase1[m] > 0:
            ax.text(0.15, i, f'P1={phase1[m]}ep', va='center', fontsize=7,
                    color='white', fontweight='bold')

    ax.set_yticks(x)
    ax.set_yticklabels(methods)
    ax.set_xlabel('Average Cost (×base)')
    ax.set_xlim(0, max(vals) * 1.35)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()
    add_ygrid(ax)

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
