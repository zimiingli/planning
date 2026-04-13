#!/usr/bin/env python3
"""Generate Figure 5: Cost of wrong direction vs signal strength.

Visual spec (experiments.tex L248-279):
- Single panel scatter plot
- x = |rho| per env, y = BSW degradation (pp)
- Color by Two-Source type: blue=Type I, red=Type D, gray=mixed/weak
- Dashed trend line with r value
- Large, clear font for environment labels
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
try:
    from scipy import stats
except ImportError:
    stats = None

HERE = Path(__file__).parent
DATA_CSV = HERE / "data.csv"
OUTPUT_PDF = HERE / "output.pdf"

# Two-Source type classification
ENV_TYPE = {
    'FEVER': 'Type I',
    'HotpotQA': 'Type I',
    'TWExpress': 'Type I',
    'WebShop': 'Mixed',
    'APPS': 'Type D',
    'Plancraft': 'Weak',
}

TYPE_COLORS = {
    'Type I': '#2166ac',    # blue
    'Type D': '#b2182b',    # red
    'Mixed': '#888888',     # gray
    'Weak': '#aaaaaa',      # light gray
}

TYPE_MARKERS = {
    'Type I': 'o',
    'Type D': 's',
    'Mixed': 'D',
    'Weak': 'D',
}


def main():
    rows = []
    with open(DATA_CSV, newline='') as f:
        for row in csv.DictReader(f):
            rows.append(row)

    fig, ax = plt.subplots(figsize=(3.5, 3))

    xs, ys, labels, types = [], [], [], []
    for row in rows:
        x = float(row['abs_rho'])
        y = float(row['degradation_pp'])
        env = row['environment']
        env_type = ENV_TYPE.get(env, 'Weak')

        xs.append(x)
        ys.append(y)
        labels.append(env)
        types.append(env_type)

        color = TYPE_COLORS[env_type]
        marker = TYPE_MARKERS[env_type]
        ax.scatter(x, y, c=color, marker=marker, s=100,
                   edgecolors='white', linewidths=0.8, zorder=5)

    # Annotate environment names
    for x, y, label, t in zip(xs, ys, labels, types):
        color = TYPE_COLORS[t]
        # Offset to avoid overlap
        offset_x, offset_y = 8, 6
        if label == 'FEVER':
            offset_x, offset_y = -10, 8
        elif label == 'HotpotQA':
            offset_y = 8
        elif label == 'APPS':
            offset_y = -12
        ax.annotate(label, (x, y), textcoords='offset points',
                    xytext=(offset_x, offset_y), color=color,
                    fontweight='bold')

    # Trend line over all points with r value
    xs_arr = np.array(xs)
    ys_arr = np.array(ys)
    if len(xs_arr) >= 2 and stats is not None:
        slope, intercept, r_value, p_value, std_err = stats.linregress(xs_arr, ys_arr)
    elif len(xs_arr) >= 2:
        # Fallback: numpy polyfit + manual r
        coeffs = np.polyfit(xs_arr, ys_arr, 1)
        slope, intercept = coeffs
        ss_res = np.sum((ys_arr - (slope * xs_arr + intercept)) ** 2)
        ss_tot = np.sum((ys_arr - ys_arr.mean()) ** 2)
        r_value = np.sqrt(1 - ss_res / ss_tot) if ss_tot > 0 else 0
    if len(xs_arr) >= 2:
        x_range = np.linspace(min(xs_arr) - 0.05, max(xs_arr) + 0.05, 100)
        ax.plot(x_range, slope * x_range + intercept, '--', color='#666666',
                linewidth=1.2, alpha=0.7)
        # r value annotation
        ax.text(0.03, 0.97, f'$r = {r_value:.2f}$', transform=ax.transAxes,
                ha='left', va='top', color='#444444',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          alpha=0.8, edgecolor='#cccccc'))

    ax.set_xlabel(r'Signal Strength $|\rho|$')
    ax.set_ylabel('BSW Degradation (pp)')
    ax.tick_params()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.2)

    # Legend for types
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2166ac',
               markersize=10, label='Type I (Info-Poverty)'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#b2182b',
               markersize=10, label='Type D (Decision-Diff)'),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='#888888',
               markersize=9, label='Mixed / Weak'),
    ]
    ax.legend(handles=legend_elements, fontsize=9, loc='lower right',
              framealpha=0.9, edgecolor='#cccccc')

    add_ygrid(ax)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f"Saved {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
