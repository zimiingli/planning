#!/usr/bin/env python3
"""
Generate figures for week report 2026-03-02.
Covers: direction reversal, signal replacement, wrong-direction damage,
        full method comparison across 3 environments.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})

BLUE = '#2171B5'
ORANGE = '#E6550D'
GREEN = '#31A354'
RED = '#DE2D26'
GRAY = '#999999'
PURPLE = '#756BB1'
TEAL = '#1B9E77'
GOLD = '#D95F02'

OUT = 'figures/'


# ============================================================
# Fig 13: token_entropy Direction Reversal Across 4 Environments
# ============================================================
def fig13_direction_reversal():
    fig, ax = plt.subplots(figsize=(8, 5))

    envs = ['HotpotQA', 'MBPP', 'APPS', 'WebShop']
    rhos = [-0.327, +0.153, +0.144, +0.133]
    colors = [RED, BLUE, BLUE, BLUE]

    bars = ax.bar(envs, rhos, color=colors, width=0.6, edgecolor='white', linewidth=1.5)

    # Zero line
    ax.axhline(y=0, color='black', linewidth=1.0, linestyle='-')

    # Annotations
    for bar, rho, env in zip(bars, rhos, envs):
        y = bar.get_height()
        offset = -0.03 if y < 0 else 0.015
        va = 'top' if y < 0 else 'bottom'
        ax.text(bar.get_x() + bar.get_width()/2, y + offset,
                f'ρ = {rho:+.3f}', ha='center', va=va,
                fontsize=12, fontweight='bold')

    # Direction arrows & labels
    ax.annotate('Negative\n(high entropy → low utility)',
                xy=(0, -0.327), xytext=(-0.3, -0.45),
                fontsize=9, color=RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))
    ax.annotate('Positive\n(high entropy → high utility)',
                xy=(1.5, 0.153), xytext=(2.5, 0.30),
                fontsize=9, color=BLUE, ha='center',
                arrowprops=dict(arrowstyle='->', color=BLUE, lw=1.5))

    ax.set_ylabel('Spearman ρ (token_entropy vs Utility)', fontsize=12)
    ax.set_title('Direction Reversal: Same Signal, Opposite Directions', fontsize=14, fontweight='bold')
    ax.set_ylim(-0.55, 0.40)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Legend
    neg_patch = mpatches.Patch(color=RED, label='Negative correlation')
    pos_patch = mpatches.Patch(color=BLUE, label='Positive correlation')
    ax.legend(handles=[neg_patch, pos_patch], loc='lower right', framealpha=0.9)

    plt.tight_layout()
    plt.savefig(f'{OUT}fig13_direction_reversal.png')
    plt.close()
    print('✅ Fig 13: Direction Reversal saved')


# ============================================================
# Fig 14: Signal-Utility Heatmap (4 environments × 5 signals)
# ============================================================
def fig14_signal_heatmap():
    fig, ax = plt.subplots(figsize=(10, 6))

    signals = ['token_entropy', 'step_count', 'evidence_count', 'state_category', 'action_type']
    envs = ['HotpotQA', 'MBPP', 'APPS', 'WebShop']

    # Data matrix (ρ or η², NaN for N/A)
    # Using absolute effect size for color, sign for annotation
    data = np.array([
        [-0.327, +0.153, +0.144, +0.133],   # token_entropy
        [-0.023, +0.526, -0.274, -0.048],    # step_count
        [-0.586,  np.nan, np.nan, np.nan],   # evidence_count
        [ 0.359,  0.214,  0.116,  0.598],    # state_category (η²)
        [ 0.085,  0.328,  np.nan, 0.286],    # action_type (η²)
    ])

    # For display: mask NaN
    masked = np.ma.masked_invalid(data)

    # Custom diverging colormap for signed values
    cmap = plt.cm.RdBu_r
    im = ax.imshow(masked, cmap=cmap, aspect='auto', vmin=-0.6, vmax=0.6,
                   interpolation='nearest')

    # Labels
    ax.set_xticks(range(len(envs)))
    ax.set_xticklabels(envs, fontsize=12)
    ax.set_yticks(range(len(signals)))
    ax.set_yticklabels(signals, fontsize=11)

    # Annotate each cell
    for i in range(len(signals)):
        for j in range(len(envs)):
            val = data[i, j]
            if np.isnan(val):
                ax.text(j, i, 'N/A', ha='center', va='center',
                        fontsize=10, color=GRAY, style='italic')
            else:
                # Mark strongest signal per env
                col = data[:, j]
                col_abs = np.abs(np.nan_to_num(col, nan=0))
                is_strongest = (col_abs[i] == col_abs.max()) and col_abs[i] > 0.1

                prefix = 'η²=' if signals[i] in ['state_category', 'action_type'] else 'ρ='
                text = f'{prefix}{val:+.3f}' if signals[i] not in ['state_category', 'action_type'] else f'{prefix}{val:.3f}'

                fontw = 'bold' if is_strongest else 'normal'
                fontc = 'white' if abs(val) > 0.35 else 'black'
                ax.text(j, i, text, ha='center', va='center',
                        fontsize=10, fontweight=fontw, color=fontc)

                if is_strongest:
                    rect = plt.Rectangle((j-0.48, i-0.48), 0.96, 0.96,
                                         linewidth=2.5, edgecolor=GOLD, facecolor='none')
                    ax.add_patch(rect)

    # NaN cells background
    for i in range(len(signals)):
        for j in range(len(envs)):
            if np.isnan(data[i, j]):
                rect = plt.Rectangle((j-0.5, i-0.5), 1, 1,
                                     facecolor='#f0f0f0', zorder=0)
                ax.add_patch(rect)

    ax.set_title('Signal-Utility Landscape: Effect Sizes Across Environments\n'
                 '(Gold box = strongest signal per environment)',
                 fontsize=13, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('Effect Size (ρ or η²)', fontsize=11)

    plt.tight_layout()
    plt.savefig(f'{OUT}fig14_signal_heatmap.png')
    plt.close()
    print('✅ Fig 14: Signal Heatmap saved')


# ============================================================
# Fig 15: Wrong-Direction Damage (grouped bar, 3 environments)
# ============================================================
def fig15_wrong_direction():
    fig, ax = plt.subplots(figsize=(10, 5.5))

    envs = ['HotpotQA\n(LR)', 'HotpotQA\n(MLP)', 'APPS\n(LR)', 'WebShop\n(LR)']
    correct_sr = [96.7, 96.7, 65.0, 43.7]
    wrong_sr   = [62.0, 45.3, 58.5, 7.2]
    base_sr    = [49.0, 49.0, 57.8, 7.2]
    delta      = [-34.7, -51.4, -6.5, -36.5]

    x = np.arange(len(envs))
    w = 0.3

    bars_c = ax.bar(x - w/2, correct_sr, w, label='Correct Direction', color=GREEN, edgecolor='white', linewidth=1.2)
    bars_w = ax.bar(x + w/2, wrong_sr, w, label='Wrong Direction', color=RED, edgecolor='white', linewidth=1.2)

    # Base SR reference lines
    for i, b in enumerate(base_sr):
        ax.plot([i - 0.4, i + 0.4], [b, b], '--', color=GRAY, linewidth=1.2, zorder=5)

    # Delta annotations
    for i, (c, w_val, d) in enumerate(zip(correct_sr, wrong_sr, delta)):
        mid = (c + w_val) / 2
        ax.annotate(f'{d:+.1f}pp',
                    xy=(i, mid), fontsize=11, fontweight='bold',
                    color=RED, ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=RED, alpha=0.9))

    # Special annotation for MLP RR=0%
    ax.text(1 + w/2, wrong_sr[1] + 2, 'RR=0%\n(zero trigger)', ha='center', va='bottom',
            fontsize=9, color=RED, style='italic')

    ax.set_ylabel('Success Rate (%)', fontsize=12)
    ax.set_title('Wrong-Direction Damage: Catastrophic Across Environments & Gates',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(envs, fontsize=11)
    ax.set_ylim(0, 110)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='upper right', framealpha=0.9)

    # Base SR legend
    ax.plot([], [], '--', color=GRAY, label='Base-Only SR')
    ax.legend(loc='upper right', framealpha=0.9)

    plt.tight_layout()
    plt.savefig(f'{OUT}fig15_wrong_direction.png')
    plt.close()
    print('✅ Fig 15: Wrong Direction Damage saved')


# ============================================================
# Fig 16: Method Comparison — SR vs CS Pareto (3 environments)
# ============================================================
def fig16_pareto_3env():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # --- HotpotQA ---
    ax = axes[0]
    methods_h = {
        'base_only':     (49.0, 100.0),
        'always':        (97.0, 0.0),
        'random_50':     (89.0, 48.6),
        'entropy_thr':   (67.2, 78.5),
        'wrong_dir':     (58.2, 50.1),
        'scg_prompt':    (95.7, 17.9),
        'scg_mlp':       (96.7, 36.3),
        'SCG-LR':        (96.7, 44.1),
        'oracle':        (97.0, 67.0),
    }
    colors_h = [GRAY, GRAY, ORANGE, PURPLE, RED, PURPLE, BLUE, GREEN, TEAL]
    markers_h = ['s', 's', 'o', 'D', 'X', 'D', '^', '*', 'P']
    sizes_h = [40, 40, 50, 50, 70, 50, 60, 200, 80]

    for (name, (sr, cs)), c, m, s in zip(methods_h.items(), colors_h, markers_h, sizes_h):
        ax.scatter(cs, sr, c=c, marker=m, s=s, zorder=5, edgecolors='black', linewidth=0.5)
        offset_x, offset_y = 1.5, -1.5
        if name == 'SCG-LR': offset_x, offset_y = -8, -3
        if name == 'oracle': offset_x, offset_y = 2, -2
        if name == 'wrong_dir': offset_x, offset_y = -12, 2
        if name == 'base_only': offset_x, offset_y = -5, 2
        ax.annotate(name, (cs, sr), textcoords='offset points',
                    xytext=(offset_x, offset_y), fontsize=7.5)

    ax.set_xlabel('Cost Saving (%)')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('HotpotQA', fontweight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(40, 102)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # --- APPS ---
    ax = axes[1]
    methods_a = {
        'base_only':  (57.8, 100.0),
        'always':     (64.8, 0.0),
        'random_50':  (66.5, 49.8),
        'wrong_dir':  (58.5, 100.0),
        'SCG-LR':     (65.0, 59.8),
        'oracle':     (66.8, 0.0),
    }
    colors_a = [GRAY, GRAY, ORANGE, RED, GREEN, TEAL]
    markers_a = ['s', 's', 'o', 'X', '*', 'P']
    sizes_a = [40, 40, 50, 70, 200, 80]

    for (name, (sr, cs)), c, m, s in zip(methods_a.items(), colors_a, markers_a, sizes_a):
        ax.scatter(cs, sr, c=c, marker=m, s=s, zorder=5, edgecolors='black', linewidth=0.5)
        offset_x, offset_y = 2, -2
        if name == 'SCG-LR': offset_x, offset_y = -8, -3
        if name == 'wrong_dir': offset_x, offset_y = -12, 2
        ax.annotate(name, (cs, sr), textcoords='offset points',
                    xytext=(offset_x, offset_y), fontsize=7.5)

    ax.set_xlabel('Cost Saving (%)')
    ax.set_title('APPS (Introductory)', fontweight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(53, 70)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # --- WebShop ---
    ax = axes[2]
    methods_w = {
        'base_only':  (7.2, 100.0),
        'always':     (43.0, 0.0),
        'random_50':  (47.5, 49.1),
        'wrong_dir':  (7.2, 62.9),
        'scg_mlp':    (7.5, 100.0),
        'SCG-LR':     (43.7, 83.1),
        'SCG-LoRA':   (42.8, 82.3),
        'oracle':     (43.3, 86.9),
    }
    colors_w = [GRAY, GRAY, ORANGE, RED, RED, GREEN, BLUE, TEAL]
    markers_w = ['s', 's', 'o', 'X', 'X', '*', '^', 'P']
    sizes_w = [40, 40, 50, 70, 50, 200, 60, 80]

    for (name, (sr, cs)), c, m, s in zip(methods_w.items(), colors_w, markers_w, sizes_w):
        ax.scatter(cs, sr, c=c, marker=m, s=s, zorder=5, edgecolors='black', linewidth=0.5)
        offset_x, offset_y = 2, -2
        if name == 'SCG-LR': offset_x, offset_y = -8, -3
        if name == 'oracle': offset_x, offset_y = 2, -2
        if name == 'wrong_dir': offset_x, offset_y = 2, 2
        if name == 'scg_mlp': offset_x, offset_y = -12, 2
        ax.annotate(name, (cs, sr), textcoords='offset points',
                    xytext=(offset_x, offset_y), fontsize=7.5)

    ax.set_xlabel('Cost Saving (%)')
    ax.set_title('WebShop', fontweight='bold')
    ax.set_xlim(-5, 105)
    ax.set_ylim(0, 55)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.suptitle('SR vs CS Pareto Front Across 3 Environments\n'
                 '(★ SCG-LR achieves near-oracle performance in all)',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{OUT}fig16_pareto_3env.png')
    plt.close()
    print('✅ Fig 16: Pareto 3-Env saved')


# ============================================================
# Fig 17: Strongest Signal Per Environment (bar chart)
# ============================================================
def fig17_strongest_signal():
    fig, ax = plt.subplots(figsize=(9, 5))

    envs = ['HotpotQA', 'APPS', 'WebShop']
    signals = ['evidence_count\n(ρ = −0.586)', 'step_count\n(ρ = −0.274)', 'state_category\n(η² = 0.598)']
    values = [0.586, 0.274, 0.598]
    sig_types = ['Continuous\n(retrieval count)', 'Continuous\n(code step)', 'Categorical\n(page state)']
    colors = [BLUE, ORANGE, GREEN]

    bars = ax.barh(envs, values, color=colors, height=0.5, edgecolor='white', linewidth=1.5)

    # Annotate signal name + type
    for i, (bar, sig, st) in enumerate(zip(bars, signals, sig_types)):
        w = bar.get_width()
        ax.text(w + 0.01, bar.get_y() + bar.get_height()/2,
                f'{sig}\n{st}', va='center', ha='left', fontsize=10)

    ax.set_xlabel('Effect Size (|ρ| or η²)', fontsize=12)
    ax.set_title('Strongest Signal is Environment-Specific\n'
                 '(Different signal, different type, different direction)',
                 fontsize=13, fontweight='bold')
    ax.set_xlim(0, 0.85)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUT}fig17_strongest_signal.png')
    plt.close()
    print('✅ Fig 17: Strongest Signal saved')


# ============================================================
# Fig 18: step_count Direction Also Reverses (MBPP vs APPS)
# ============================================================
def fig18_step_count_reversal():
    fig, ax = plt.subplots(figsize=(7, 4.5))

    envs = ['HotpotQA', 'MBPP', 'APPS', 'WebShop']
    rhos = [-0.023, +0.526, -0.274, -0.048]
    colors = [GRAY, BLUE, RED, GRAY]
    alphas = [0.4, 1.0, 1.0, 0.4]

    bars = ax.bar(envs, rhos, color=colors, width=0.55, edgecolor='white', linewidth=1.5)
    for bar, a in zip(bars, alphas):
        bar.set_alpha(a)

    ax.axhline(y=0, color='black', linewidth=1.0)

    for bar, rho in zip(bars, rhos):
        y = bar.get_height()
        offset = -0.03 if y < 0 else 0.02
        va = 'top' if y < 0 else 'bottom'
        ax.text(bar.get_x() + bar.get_width()/2, y + offset,
                f'ρ = {rho:+.3f}', ha='center', va=va,
                fontsize=11, fontweight='bold')

    # Highlight the reversal
    ax.annotate('', xy=(1, 0.526), xytext=(2, -0.274),
                arrowprops=dict(arrowstyle='<->', color=GOLD, lw=2.5, connectionstyle='arc3,rad=0.3'))
    ax.text(1.5, 0.15, 'Direction\nReversal!', ha='center', va='center',
            fontsize=11, fontweight='bold', color=GOLD,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff8e1', edgecolor=GOLD))

    ax.set_ylabel('Spearman ρ (step_count vs Utility)', fontsize=12)
    ax.set_title('step_count Also Reverses: MBPP (+0.526) vs APPS (−0.274)',
                 fontsize=13, fontweight='bold')
    ax.set_ylim(-0.45, 0.65)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(f'{OUT}fig18_step_count_reversal.png')
    plt.close()
    print('✅ Fig 18: step_count Reversal saved')


# ============================================================
# Fig 19: Full SR Comparison Bar (3 valid environments)
# ============================================================
def fig19_sr_comparison():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # HotpotQA
    ax = axes[0]
    methods = ['base', 'always', 'random', 'entropy\n_thr', 'wrong\n_dir', 'SCG-LR', 'oracle']
    srs = [49.0, 97.0, 89.0, 67.2, 58.2, 96.7, 97.0]
    cs_vals = [100.0, 0.0, 48.6, 78.5, 50.1, 44.1, 67.0]
    colors = [GRAY, GRAY, ORANGE, PURPLE, RED, GREEN, TEAL]

    x = np.arange(len(methods))
    bars = ax.bar(x, srs, color=colors, width=0.65, edgecolor='white', linewidth=1)
    for bar, sr in zip(bars, srs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{sr:.1f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=8)
    ax.set_ylabel('SR (%)')
    ax.set_title('HotpotQA', fontweight='bold')
    ax.set_ylim(0, 110)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # APPS
    ax = axes[1]
    methods = ['base', 'always', 'random', 'wrong\n_dir', 'SCG-LR', 'oracle']
    srs = [57.8, 64.8, 66.5, 58.5, 65.0, 66.8]
    colors = [GRAY, GRAY, ORANGE, RED, GREEN, TEAL]

    x = np.arange(len(methods))
    bars = ax.bar(x, srs, color=colors, width=0.65, edgecolor='white', linewidth=1)
    for bar, sr in zip(bars, srs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{sr:.1f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=8)
    ax.set_title('APPS (Intro)', fontweight='bold')
    ax.set_ylim(50, 72)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # WebShop
    ax = axes[2]
    methods = ['base', 'always', 'random', 'wrong\n_dir', 'scg_mlp', 'SCG-LR', 'oracle']
    srs = [7.2, 43.0, 47.5, 7.2, 7.5, 43.7, 43.3]
    colors = [GRAY, GRAY, ORANGE, RED, RED, GREEN, TEAL]

    x = np.arange(len(methods))
    bars = ax.bar(x, srs, color=colors, width=0.65, edgecolor='white', linewidth=1)
    for bar, sr in zip(bars, srs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{sr:.1f}', ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=8)
    ax.set_title('WebShop', fontweight='bold')
    ax.set_ylim(0, 55)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.suptitle('Success Rate Comparison Across 3 Valid Environments',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{OUT}fig19_sr_comparison.png')
    plt.close()
    print('✅ Fig 19: SR Comparison saved')


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    import os
    os.makedirs(OUT, exist_ok=True)
    fig13_direction_reversal()
    fig14_signal_heatmap()
    fig15_wrong_direction()
    fig16_pareto_3env()
    fig17_strongest_signal()
    fig18_step_count_reversal()
    fig19_sr_comparison()
    print('\n✅ All 7 figures generated in figures/')
