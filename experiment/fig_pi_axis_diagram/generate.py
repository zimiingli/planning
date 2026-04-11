#!/usr/bin/env python3
"""Figure A1: pI axis diagram — visual summary of the Two-Source Model.

Spec (appendix.tex L362-394):
- Single horizontal axis from pI=0 (Pure Type D) to pI=1 (Pure Type I)
- Vertical dashed line at reversal threshold pI*
- Left = green (positive rho), Right = red (negative rho)
- Each environment = labeled dot, size proportional to |rho|
- Color: green for rho>0, red for rho<0, gray for weak
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

    fig, ax = plt.subplots(figsize=(14, 4))

    # Background shading
    ax.axvspan(0, 0.5, alpha=0.06, color='#2ca02c', zorder=0)  # Type D side (green)
    ax.axvspan(0.5, 1.0, alpha=0.06, color='#d62728', zorder=0)  # Type I side (red)

    # Reversal threshold
    ax.axvline(x=0.5, color='#444444', linestyle='--', linewidth=1.5, alpha=0.7, zorder=1)
    ax.text(0.5, 1.15, r'Reversal threshold $p_I^*$', ha='center', va='bottom',
            fontsize=9, color='#444444', transform=ax.get_xaxis_transform())

    # Plot environments
    for row in rows:
        pi = float(row['pI_estimate'])
        rho = float(row['rho_entropy'])
        abs_rho = float(row['abs_rho'])
        env = row['environment']

        # Color by rho sign
        if abs_rho < 0.03:
            color = '#888888'
        elif rho > 0:
            color = '#2ca02c'
        else:
            color = '#d62728'

        # Size proportional to |rho|
        size = max(80, abs_rho * 600)

        ax.scatter(pi, 0, s=size, c=color, edgecolors='white', linewidths=1.2,
                   zorder=5, alpha=0.85)

        # Label
        y_offset = 0.35 if (pi > 0.4 and pi < 0.6) else 0.3
        # Stagger labels to avoid overlap
        if env in ['Plancraft', 'CRUXEval']:
            y_offset = -0.35
        ax.annotate(f'{env}\n$\\rho$={rho:+.2f}', (pi, 0),
                    textcoords='offset points',
                    xytext=(0, 25 if y_offset > 0 else -30),
                    ha='center', va='bottom' if y_offset > 0 else 'top',
                    fontsize=8, fontweight='bold', color=color)

    # Axis labels
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.6, 0.6)
    ax.set_xlabel(r'Fraction of Type I states $p_I$', fontsize=11)
    ax.set_yticks([])

    # Bracket labels
    ax.text(0.15, -0.5, 'Type D dominant\n(trigger on high entropy)',
            ha='center', fontsize=8, color='#2ca02c', fontstyle='italic')
    ax.text(0.85, -0.5, 'Type I dominant\n(avoid high entropy)',
            ha='center', fontsize=8, color='#d62728', fontstyle='italic')
    ax.text(0.5, -0.5, 'Mixed',
            ha='center', fontsize=8, color='#888888', fontstyle='italic')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    fig.suptitle('Environment Positions on the Two-Source Model $p_I$ Axis',
                 fontsize=13, fontweight='bold')

    plt.tight_layout()
    fig.savefig(HERE / 'output.pdf', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'Saved {HERE / "output.pdf"}')

if __name__ == '__main__':
    main()
