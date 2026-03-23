#!/usr/bin/env python3
"""Generate Figure 2: Pareto front -- Success Rate vs Cost per environment."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from pathlib import Path

HERE = Path(__file__).parent
DATA_CSV = HERE / "data.csv"
OUTPUT_PDF = HERE / "output.pdf"

# EAAG method names (principled_adaptive is EAAG)
EAAG_METHODS = {'principled_adaptive'}

# Canonical environment order for 2x3 grid
ENV_ORDER = ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft']
ENV_LABELS = {
    'hotpotqa': 'HotpotQA',
    'apps': 'APPS',
    'webshop': 'WebShop',
    'fever': 'FEVER',
    'twexpress': 'TWExpress',
    'plancraft': 'Plancraft',
}


def main():
    # Read data
    rows = []
    with open(DATA_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Group by environment
    env_data = {}
    for row in rows:
        env = row['environment']
        if env not in env_data:
            env_data[env] = []
        env_data[env].append(row)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for idx, env_key in enumerate(ENV_ORDER):
        ax = axes[idx]
        if env_key not in env_data:
            ax.set_title(ENV_LABELS.get(env_key, env_key))
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            continue

        data = env_data[env_key]
        # Split into EAAG and others
        eaag_x, eaag_y = [], []
        other_x, other_y = [], []

        for row in data:
            cost = float(row['avg_rollouts_per_ep'])
            sr = float(row['success_rate']) * 100  # convert to %
            method = row['method']
            if method in EAAG_METHODS:
                eaag_x.append(cost)
                eaag_y.append(sr)
            else:
                other_x.append(cost)
                other_y.append(sr)

        ax.scatter(other_x, other_y, c='steelblue', marker='o', s=30,
                   alpha=0.6, edgecolors='none', label='Other')
        if eaag_x:
            ax.scatter(eaag_x, eaag_y, c='red', marker='*', s=200,
                       zorder=5, edgecolors='darkred', linewidths=0.5, label='EAAG')

        ax.set_title(ENV_LABELS.get(env_key, env_key), fontsize=11, fontweight='bold')
        ax.set_xlabel('Avg Rollouts / Episode', fontsize=9)
        ax.set_ylabel('Success Rate (%)', fontsize=9)
        ax.tick_params(labelsize=8)

    # Add a shared legend
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=2, fontsize=10,
               bbox_to_anchor=(0.5, 1.02))

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
