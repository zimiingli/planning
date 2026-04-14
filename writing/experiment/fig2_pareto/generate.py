#!/usr/bin/env python3
"""Generate Figure 2: Pareto frontier -- SR vs Cost, with category markers.

Visual spec (experiments.tex L94-124):
- 2x3 grid: HotpotQA, APPS, WebShop, FEVER, Plancraft, APPS Intv
- Marker shapes: circle=bounds, triangle=fixed-direction, star=EAAG
- Colors: bounds=gray, fixed-direction=tab10, EAAG=crimson
- Pareto frontier dashed line + light shading below
- Shared legend
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
DATA_CSV = HERE / "data.csv"
MAIN_CSV = HERE.parent / "tab_main_results" / "data.csv"
OUTPUT_PDF = HERE / "output.pdf"

# Environment order for 2x3 grid
ENV_ORDER = ['hotpotqa', 'webshop', 'fever', 'twexpress', 'plancraft', 'apps_interview']
ENV_LABELS = {
    'hotpotqa': 'HotpotQA', 'webshop': 'WebShop',
    'fever': 'FEVER', 'plancraft': 'Plancraft', 'apps_interview': 'APPS',
    'twexpress': 'TWExpress',
    # tab_main_results uses display names
    'HotpotQA': 'HotpotQA', 'WebShop': 'WebShop',
    'FEVER': 'FEVER', 'Plancraft': 'Plancraft', 'APPS': 'APPS',
    'TWExpress': 'TWExpress',
}

# Map raw method names to display names and categories
EAAG_METHODS = {'se_few5_filter_local', 'principled_adaptive', 'EAAG'}
BOUNDS = {'base_only', 'always_trigger', 'oracle'}
FIXED_CB = {'cats', 'seag', 'corefine', 'catts', 'auq', 's1_budget',
            'CaTS', 'SEAG', 'CoRefine', 'CATTS', 'AUQ'}
CB_COLORS = {
    'CaTS': '#1f77b4', 'cats': '#1f77b4',
    'SEAG': '#ff7f0e', 'seag': '#ff7f0e',
    'CoRefine': '#2ca02c', 'corefine': '#2ca02c',
    'CATTS': '#9467bd', 'catts': '#9467bd',
    'AUQ': '#8c564b', 'auq': '#8c564b',
    's1_budget': '#e377c2',
}
CB_MARKERS = {
    'CaTS': '^', 'cats': '^',
    'SEAG': 'v', 'seag': 'v',
    'CoRefine': 's', 'corefine': 's',
    'CATTS': 'D', 'catts': 'D',
    'AUQ': 'o', 'auq': 'o',
    's1_budget': 'P',
}
CB_LABELS = {
    'cats': 'CaTS', 'seag': 'SEAG', 'corefine': 'CoRefine',
    'catts': 'CATTS', 'auq': 'AUQ', 's1_budget': 's1_budget',
    'CaTS': 'CaTS', 'SEAG': 'SEAG', 'CoRefine': 'CoRefine',
    'CATTS': 'CATTS', 'AUQ': 'AUQ',
}


def categorize(method):
    if method in EAAG_METHODS:
        return 'eaag'
    if method in BOUNDS:
        return 'bounds'
    if method in FIXED_CB:
        return 'cb'
    return 'other'


def pareto_front(points):
    """Return indices of Pareto-optimal points (max SR, min cost)."""
    pts = np.array(points)
    if len(pts) == 0:
        return []
    # Sort by cost ascending
    order = pts[:, 0].argsort()
    pts_sorted = pts[order]
    front = [0]
    max_sr = pts_sorted[0, 1]
    for i in range(1, len(pts_sorted)):
        if pts_sorted[i, 1] >= max_sr:
            front.append(i)
            max_sr = pts_sorted[i, 1]
    return order[front]


def main():
    # Primary source: tab_main_results (clean, paper-reported methods)
    rows = []
    if MAIN_CSV.exists():
        env_remap = {
            'HotpotQA': 'hotpotqa', 'WebShop': 'webshop',
            'FEVER': 'fever', 'TWExpress': 'twexpress', 'Plancraft': 'plancraft',
            'APPS': 'apps_interview',
        }
        with open(MAIN_CSV, newline='') as f:
            for row in csv.DictReader(f):
                cost = row.get('cost_xbase', '')
                if cost == '' or cost == '---':
                    continue
                env_key = env_remap.get(row['environment'], row['environment'])
                rows.append({
                    'environment': env_key,
                    'method': row['method'],
                    'success_rate': str(float(row['sr_pct']) / 100),
                    'cost_xbase': cost,
                })

    # No longer loading data.csv (it has too many dev variants).
    # All paper methods come from tab_main_results.

    # Group by environment
    env_data = {}
    for row in rows:
        env = row['environment']
        if env not in env_data:
            env_data[env] = []
        env_data[env].append(row)

    fig, axes = plt.subplots(2, 3, figsize=(7, 4.5))
    axes = axes.flatten()

    # Track handles for shared legend
    legend_handles = {}

    for idx, env_key in enumerate(ENV_ORDER):
        ax = axes[idx]
        if env_key not in env_data:
            ax.set_title(ENV_LABELS.get(env_key, env_key), fontweight='bold')
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            continue

        data = env_data[env_key]
        all_points = []  # (cost, sr) for Pareto front

        # Collect by category
        for row in data:
            method = row['method']
            cost_str = row.get('cost_xbase', '0')
            if cost_str == '' or cost_str == '---':
                continue
            cost = float(cost_str)
            sr = float(row['success_rate'])
            if sr <= 1.0:
                sr *= 100
            cat = categorize(method)
            all_points.append((cost, sr, cat, method))

        # Separate bounds and methods
        paper_points = [(c, s, cat, m) for c, s, cat, m in all_points
                        if cat in ('cb', 'eaag')]
        bounds_pts = {m: (c, s) for c, s, cat, m in all_points if cat == 'bounds'}

        # Plot methods with jitter for overlapping points
        marker_size = 60
        # Detect overlaps: group by (cost, sr) proximity
        pts_for_jitter = [(c, s, cat, m) for c, s, cat, m in paper_points]
        cost_range = max(c for c, s, _, _ in pts_for_jitter) - min(c for c, s, _, _ in pts_for_jitter) if len(pts_for_jitter) > 1 else 1
        sr_range = max(s for _, s, _, _ in pts_for_jitter) - min(s for _, s, _, _ in pts_for_jitter) if len(pts_for_jitter) > 1 else 1
        cost_thresh = max(cost_range * 0.05, 0.3)
        sr_thresh = max(sr_range * 0.05, 1.0)

        # Assign jitter offsets to overlapping points
        jitter_offsets = {}
        used = []
        for i, (c1, s1, cat1, m1) in enumerate(pts_for_jitter):
            cluster = [i]
            for j, (c2, s2, cat2, m2) in enumerate(pts_for_jitter):
                if i != j and abs(c1 - c2) < cost_thresh and abs(s1 - s2) < sr_thresh:
                    cluster.append(j)
            cluster = sorted(set(cluster))
            if len(cluster) > 1 and tuple(cluster) not in used:
                used.append(tuple(cluster))
                for k, idx in enumerate(cluster):
                    angle = 2 * np.pi * k / len(cluster)
                    jitter_offsets[idx] = (
                        np.cos(angle) * cost_thresh * 0.4,
                        np.sin(angle) * sr_thresh * 0.4
                    )

        for i, (cost, sr, cat, method) in enumerate(paper_points):
            dc, ds = jitter_offsets.get(i, (0, 0))
            if cat == 'cb':
                color = CB_COLORS.get(method, '#17becf')
                marker = CB_MARKERS.get(method, '^')
                label = CB_LABELS.get(method, method)
                h = ax.scatter(cost + dc, sr + ds, c=color, marker=marker,
                               s=marker_size, alpha=0.85, edgecolors='white',
                               linewidths=0.5, zorder=4)
                if label not in legend_handles:
                    legend_handles[label] = h
            elif cat == 'eaag':
                h = ax.scatter(cost + dc, sr + ds, c='crimson', marker='*',
                               s=marker_size * 2, edgecolors='darkred',
                               linewidths=0.5, zorder=10)
                legend_handles['EAAG'] = h

        # Set x-axis with padding
        all_costs = [c for c, s, cat, m in paper_points]
        if all_costs:
            x_min = max(0, min(all_costs) - 0.5)
            x_max = max(all_costs) + 1.0
            ax.set_xlim(x_min, x_max)

        # Set y-axis to zoom into the data range with padding
        all_srs = [s for _, s, _, _ in paper_points]
        if all_srs:
            sr_min = min(all_srs)
            sr_max = max(all_srs)
            sr_pad = max((sr_max - sr_min) * 0.15, 2.0)
            ax.set_ylim(max(0, sr_min - sr_pad), min(100, sr_max + sr_pad))

        # EAAG-dominated region (use original positions, not jittered)
        eaag_pts = [(c, s) for c, s, cat, m in paper_points if cat == 'eaag']
        if eaag_pts:
            eaag_cost, eaag_sr = eaag_pts[0]
            ax.fill_between([eaag_cost, x_max + 5], ax.get_ylim()[0], eaag_sr,
                            color='crimson', alpha=0.06, zorder=0)
            ax.axvline(eaag_cost, color='crimson', linestyle=':', linewidth=0.5,
                       alpha=0.3, ymax=(eaag_sr - ax.get_ylim()[0]) /
                       (ax.get_ylim()[1] - ax.get_ylim()[0]) if ax.get_ylim()[1] != ax.get_ylim()[0] else 0.5,
                       zorder=0)
            ax.axhline(eaag_sr, color='crimson', linestyle=':', linewidth=0.5,
                       alpha=0.3, xmin=(eaag_cost - ax.get_xlim()[0]) /
                       (ax.get_xlim()[1] - ax.get_xlim()[0]) if ax.get_xlim()[1] != ax.get_xlim()[0] else 0.5,
                       zorder=0)

        ax.set_title(ENV_LABELS.get(env_key, env_key))
        ax.set_xlabel('Cost ($\\times$base)', fontsize=9)
        ax.set_ylabel('SR (%)', fontsize=9)
        ax.tick_params(labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        add_ygrid(ax)

    # Shared legend — ordered: CBs, EAAG
    desired_order = ['CaTS', 'SEAG', 'CoRefine', 'CATTS', 'AUQ', 's1_budget', 'EAAG']
    handles = []
    labels = []
    for name in desired_order:
        if name in legend_handles:
            handles.append(legend_handles[name])
            labels.append(name)
    fig.legend(handles, labels, loc='upper center', ncol=len(labels),
               fontsize=9, bbox_to_anchor=(0.5, 1.01), frameon=False)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
