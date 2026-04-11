#!/usr/bin/env python3
"""Figure A8: Computational cost breakdown — stacked bar chart.

Spec (appendix.tex L832-859):
- Stacked bar chart. x = methods, y = total compute
- Dark = calibration/exploration overhead, Light = deployment rollouts
- EAAG highlighted with red border
- Sort by total cost ascending
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import csv
from pathlib import Path

HERE = Path(__file__).parent

def main():
    with open(HERE / 'data.csv', newline='') as f:
        rows = list(csv.DictReader(f))

    # Parse data
    methods = []
    phase1_eps = []
    deploy_costs = []

    for row in rows:
        m = row['method']
        if m in ('base_only', 'always_trigger'):
            continue  # bounds, not gating methods
        methods.append(m)
        p1 = int(row['phase1_episodes'])
        phase1_eps.append(p1)
        deploy = float(row['deploy_rollouts_per_ep'])
        deploy_costs.append(deploy)

    # Normalize: phase1 overhead = episodes (scaled), deployment = rollouts/ep * 500
    # Use simple metric: phase1_eps as calibration cost, deploy * 500 as deployment
    overhead = np.array(phase1_eps, dtype=float)
    deployment = np.array(deploy_costs) * 500  # 500 deployment episodes
    total = overhead + deployment

    # Sort by total ascending
    order = np.argsort(total)
    methods = [methods[i] for i in order]
    overhead = overhead[order]
    deployment = deployment[order]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(methods))

    bars1 = ax.bar(x, overhead, color='#4393c3', edgecolor='white', linewidth=0.5,
                   label='Calibration / Exploration')
    bars2 = ax.bar(x, deployment, bottom=overhead, color='#f4a582', edgecolor='white',
                   linewidth=0.5, label='Deployment Rollouts (500 ep)')

    # Highlight EAAG with red border
    for i, m in enumerate(methods):
        if m == 'EAAG':
            for b1, b2 in [(bars1[i], bars2[i])]:
                b1.set_edgecolor('crimson')
                b1.set_linewidth(2)
                b2.set_edgecolor('crimson')
                b2.set_linewidth(2)

    # Annotate total on top
    for i in range(len(methods)):
        t = overhead[i] + deployment[i]
        ax.text(i, t + 10, f'{t:.0f}', ha='center', va='bottom', fontsize=8,
                fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=9, rotation=30, ha='right')
    ax.set_ylabel('Total Cost (episodes equivalent)', fontsize=11)
    ax.set_title('Computational Cost Breakdown by Method', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
