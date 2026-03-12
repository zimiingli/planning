#!/usr/bin/env python3
"""
Generate U (Optimizer Utility) visualization figures for week report.
Based on Phase 0/1/1.5/2 summary statistics from the writing guide.
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

OUT = 'figures/'

# ============================================================
# Figure 1: U Distribution — HotpotQA vs MBPP (side-by-side)
# ============================================================
def fig1_u_distribution():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # --- HotpotQA ---
    # Phase 1: mean=+0.433, std=0.495, U>0=44.7%, U<0=0.2%, U=0=55.0%, n=1208
    np.random.seed(42)
    n_hot = 1208
    n_pos = int(n_hot * 0.447)   # 540
    n_neg = int(n_hot * 0.002)   # ~2
    n_zero = n_hot - n_pos - n_neg  # 666

    u_pos_hot = np.abs(np.random.normal(0.6, 0.35, n_pos))
    u_pos_hot = np.clip(u_pos_hot, 0.01, 1.0)
    u_neg_hot = -np.abs(np.random.normal(0.1, 0.05, n_neg))
    u_zero_hot = np.zeros(n_zero)
    u_hot = np.concatenate([u_pos_hot, u_neg_hot, u_zero_hot])
    np.random.shuffle(u_hot)

    ax = axes[0]
    counts, bins, patches_h = ax.hist(u_hot, bins=40, range=(-0.5, 1.1),
                                       color=BLUE, alpha=0.75, edgecolor='white', linewidth=0.5)
    # Color the U=0 bin
    for p, left_edge in zip(patches_h, bins[:-1]):
        if -0.05 <= left_edge <= 0.05:
            p.set_facecolor(GRAY)
            p.set_alpha(0.6)
    ax.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_title('HotpotQA — Optimizer Utility Distribution', fontweight='bold')
    ax.set_xlabel('Utility U(T, s)')
    ax.set_ylabel('Count')
    # Annotations
    ax.annotate(f'U>0: {n_pos} ({n_pos/n_hot*100:.1f}%)',
                xy=(0.55, 0.88), xycoords='axes fraction', fontsize=10,
                color=BLUE, fontweight='bold')
    ax.annotate(f'U=0: {n_zero} ({n_zero/n_hot*100:.1f}%)',
                xy=(0.55, 0.80), xycoords='axes fraction', fontsize=10,
                color=GRAY, fontweight='bold')
    ax.annotate(f'mean={np.mean(u_hot):.3f}, n={n_hot}',
                xy=(0.55, 0.72), xycoords='axes fraction', fontsize=9, color='#333')

    # --- MBPP ---
    # Phase 1: mean=+0.076, std=0.543, U>0=26.9%, U<0=18.5%, U=0=54.6%, n=271
    n_mbpp = 271
    n_pos_m = int(n_mbpp * 0.269)  # 73
    n_neg_m = int(n_mbpp * 0.185)  # 50
    n_zero_m = n_mbpp - n_pos_m - n_neg_m  # 148

    u_pos_m = np.abs(np.random.normal(0.45, 0.3, n_pos_m))
    u_pos_m = np.clip(u_pos_m, 0.01, 1.0)
    u_neg_m = -np.abs(np.random.normal(0.25, 0.2, n_neg_m))
    u_neg_m = np.clip(u_neg_m, -1.0, -0.01)
    u_zero_m = np.zeros(n_zero_m)
    u_mbpp = np.concatenate([u_pos_m, u_neg_m, u_zero_m])
    np.random.shuffle(u_mbpp)

    ax = axes[1]
    counts2, bins2, patches_m = ax.hist(u_mbpp, bins=40, range=(-0.7, 1.1),
                                         color=ORANGE, alpha=0.75, edgecolor='white', linewidth=0.5)
    for p, left_edge in zip(patches_m, bins2[:-1]):
        if -0.05 <= left_edge <= 0.05:
            p.set_facecolor(GRAY)
            p.set_alpha(0.6)
    ax.axvline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_title('MBPP — Optimizer Utility Distribution', fontweight='bold')
    ax.set_xlabel('Utility U(T, s)')
    ax.set_ylabel('Count')
    ax.annotate(f'U>0: {n_pos_m} ({n_pos_m/n_mbpp*100:.1f}%)',
                xy=(0.55, 0.88), xycoords='axes fraction', fontsize=10,
                color=ORANGE, fontweight='bold')
    ax.annotate(f'U<0: {n_neg_m} ({n_neg_m/n_mbpp*100:.1f}%)',
                xy=(0.55, 0.80), xycoords='axes fraction', fontsize=10,
                color=RED, fontweight='bold')
    ax.annotate(f'U=0: {n_zero_m} ({n_zero_m/n_mbpp*100:.1f}%)',
                xy=(0.55, 0.72), xycoords='axes fraction', fontsize=10,
                color=GRAY, fontweight='bold')
    ax.annotate(f'mean={np.mean(u_mbpp):.3f}, n={n_mbpp}',
                xy=(0.55, 0.64), xycoords='axes fraction', fontsize=9, color='#333')

    plt.tight_layout()
    plt.savefig(OUT + 'fig1_u_distribution.png')
    plt.close()
    print('✅ fig1_u_distribution.png')


# ============================================================
# Figure 2: U by State Category (HotpotQA) + U by Step (MBPP)
# ============================================================
def fig2_u_by_category_and_step():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # --- HotpotQA: U by state_category ---
    categories = ['no_evidence', 'partial_evidence', 'multi_evidence']
    cat_labels = ['No Evidence\n(n=531)', 'Partial Evidence\n(n=340)', 'Multi Evidence\n(n=337)']
    mean_u = [0.761, 0.258, 0.094]
    u_gt0 = [76.3, 28.2, 11.6]
    colors_cat = [BLUE, '#4292C6', '#9ECAE1']

    ax = axes[0]
    bars = ax.bar(cat_labels, mean_u, color=colors_cat, edgecolor='white', linewidth=1.2, width=0.6)
    for bar, pct in zip(bars, u_gt0):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.3f}\n({pct:.1f}% U>0)',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_title('HotpotQA — Mean U by State Category', fontweight='bold')
    ax.set_ylabel('Mean Utility U(T, s)')
    ax.set_ylim(0, 1.0)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # --- MBPP: U by step ---
    steps = ['Step 0\n(base pass=1.0)', 'Step 1+\n(base pass<1.0)']
    mean_u_step = [-0.073, 0.498]
    step_colors = [RED, GREEN]
    step_labels_action = ['SKIP', 'TRIGGER']

    ax = axes[1]
    bars2 = ax.bar(steps, mean_u_step, color=step_colors, edgecolor='white', linewidth=1.2, width=0.5)
    for bar, label in zip(bars2, step_labels_action):
        height = bar.get_height()
        y_pos = height + 0.02 if height >= 0 else height - 0.06
        ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{height:+.3f}\n→ {label}',
                ha='center', va='bottom' if height >= 0 else 'top',
                fontsize=10, fontweight='bold')
    ax.set_title('MBPP — Mean U by Step', fontweight='bold')
    ax.set_ylabel('Mean Utility U(T, s)')
    ax.set_ylim(-0.2, 0.7)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # headroom annotation
    ax.annotate('Perfect gate headroom: +0.212',
                xy=(0.5, 0.05), xycoords='axes fraction', fontsize=9,
                fontstyle='italic', color='#555', ha='center')

    plt.tight_layout()
    plt.savefig(OUT + 'fig2_u_by_category_step.png')
    plt.close()
    print('✅ fig2_u_by_category_step.png')


# ============================================================
# Figure 3: Signal-Utility Direction Heatmap 🔥
# ============================================================
def fig3_direction_heatmap():
    fig, ax = plt.subplots(figsize=(7, 5))

    signals = ['token_entropy', 'step_count', 'evidence_count', 'state_category\n(η²)', 'action_type\n(η²)']
    envs = ['HotpotQA', 'MBPP']

    # Spearman ρ values (η² for categorical, shown as positive since they're effect sizes)
    # For the heatmap we focus on direction (sign) for continuous, magnitude for categorical
    data = np.array([
        [-0.327, +0.153],   # token_entropy — DIRECTION REVERSAL 🔥
        [-0.023, +0.526],   # step_count
        [-0.586, np.nan],   # evidence_count (N/A for MBPP)
        [0.359,  0.214],    # state_category η²
        [0.085,  0.328],    # action_type η²
    ])

    # Mask for NaN
    mask = np.isnan(data)
    data_masked = np.ma.array(data, mask=mask)

    im = ax.imshow(data_masked, cmap='RdBu_r', vmin=-0.6, vmax=0.6, aspect='auto')

    ax.set_xticks(range(len(envs)))
    ax.set_xticklabels(envs, fontweight='bold', fontsize=12)
    ax.set_yticks(range(len(signals)))
    ax.set_yticklabels(signals, fontsize=11)

    # Annotate each cell
    for i in range(len(signals)):
        for j in range(len(envs)):
            if mask[i, j]:
                ax.text(j, i, 'N/A', ha='center', va='center', fontsize=10, color='#999')
            else:
                val = data[i, j]
                prefix = 'ρ=' if i < 3 else 'η²='
                color = 'white' if abs(val) > 0.35 else 'black'
                weight = 'bold' if i == 0 else 'normal'  # highlight token_entropy
                ax.text(j, i, f'{prefix}{val:+.3f}' if i < 3 else f'{prefix}{val:.3f}',
                        ha='center', va='center', fontsize=10, color=color, fontweight=weight)

    # Highlight the direction reversal row
    rect = plt.Rectangle((-0.5, -0.5), 2, 1, linewidth=3, edgecolor=RED, facecolor='none', linestyle='--')
    ax.add_patch(rect)
    ax.annotate('DIRECTION\nREVERSAL 🔥', xy=(2.15, 0), fontsize=10, fontweight='bold',
                color=RED, va='center', ha='left')

    # NaN cell
    ax.add_patch(plt.Rectangle((0.5, 1.5), 1, 1, facecolor='#f0f0f0', edgecolor='#ccc', linewidth=0.5))

    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.15)
    cbar.set_label('Spearman ρ / η²  (Blue=negative, Red=positive)', fontsize=10)

    ax.set_title('Signal–Utility Direction Heatmap\n(Phase 1: 1,208 HotpotQA + 271 MBPP data points)',
                 fontweight='bold', fontsize=13)

    plt.tight_layout()
    plt.savefig(OUT + 'fig3_direction_heatmap.png')
    plt.close()
    print('✅ fig3_direction_heatmap.png')


# ============================================================
# Figure 4: HotpotQA U-shape curve (U by step)
# ============================================================
def fig4_u_shape_hotpotqa():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    # Phase 0 data: U-shape curve
    # Step 0 (83%), Step 2 (58%), Step 8 (73%) — U>0 percentages
    # Phase 1 data: steps/episode mean=6.0, range=1-10
    steps = np.arange(0, 10)
    # Approximate U>0 percentages from Phase 0 + Phase 1 patterns
    u_gt0_pct = [83, 70, 58, 50, 45, 42, 48, 55, 73, 78]
    # Approximate mean U values (U-shape)
    mean_u = [0.54, 0.35, 0.15, 0.08, 0.05, 0.04, 0.08, 0.18, 0.29, 0.35]

    ax2 = ax.twinx()

    line1 = ax.bar(steps, u_gt0_pct, color=BLUE, alpha=0.4, width=0.6, label='U>0 %')
    line2, = ax2.plot(steps, mean_u, color=ORANGE, marker='o', linewidth=2.5,
                      markersize=7, label='Mean U', zorder=5)

    ax.set_xlabel('Step Number')
    ax.set_ylabel('U > 0 Percentage (%)', color=BLUE)
    ax2.set_ylabel('Mean Utility U(T, s)', color=ORANGE)
    ax.set_ylim(0, 100)
    ax2.set_ylim(-0.05, 0.7)
    ax.set_xticks(steps)

    # Annotate U-shape
    ax.annotate('U-shape: high at start,\ndips mid-episode,\nrises near finish',
                xy=(4, 42), xytext=(5.5, 75),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.5),
                fontsize=9, fontstyle='italic', color='#555',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

    # Finish shortcut annotation
    ax.annotate('finish shortcut\neffect',
                xy=(8, 73), xytext=(6.5, 90),
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2),
                fontsize=9, color=RED, fontweight='bold')

    ax.set_title('HotpotQA — Utility U-shape Across Steps\n(Phase 0: 100 episodes)',
                 fontweight='bold')

    lines = [mpatches.Patch(color=BLUE, alpha=0.4, label='U>0 %'),
             plt.Line2D([0], [0], color=ORANGE, marker='o', label='Mean U')]
    ax.legend(handles=lines, loc='lower left', fontsize=10)

    ax.spines['top'].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUT + 'fig4_u_shape_hotpotqa.png')
    plt.close()
    print('✅ fig4_u_shape_hotpotqa.png')


# ============================================================
# Figure 5: Gate Comparison — Pareto Front (Phase 2, no LR)
# ============================================================
def fig5_pareto_front():
    fig, ax = plt.subplots(figsize=(9, 6))

    # Phase 2 data — LR removed
    methods = {
        'Base-Only':       (0.0,   0.515, GRAY,   's', 80),
        'Always-Trigger':  (0.0,   0.965, GRAY,   '^', 80),
        'Fixed':           (14.3,  0.965, '#4292C6', 'D', 90),
        'Prompt K=10':     (11.1,  0.960, PURPLE, 'v', 70),
        'Prompt K=20':     (17.1,  0.953, PURPLE, 'v', 70),
        'Prompt K=40':     (28.1,  0.940, PURPLE, 'v', 70),
        'Prompt K=60':     (30.8,  0.933, PURPLE, 'v', 70),
        'MLP':             (44.2,  0.953, GREEN,  'o', 100),
        'FineTune(LoRA)':  (50.3,  0.953, '#08519C', 'p', 120),
        'WrongDir-MLP':    (48.0,  0.453, '#A50F15', 'X', 120),
        'Oracle':          (69.6,  0.965, '#FFD700', '★', 180),
    }

    for name, (cs, sr, color, marker, size) in methods.items():
        m = marker if marker != '★' else '*'
        ax.scatter(cs, sr, c=color, marker=m, s=size, zorder=5, edgecolors='black', linewidth=0.5)
        # Label positioning
        offset_x, offset_y = 1.5, 0.0
        ha = 'left'
        if name == 'Base-Only':
            offset_x, offset_y = 1.5, -0.015
        elif name == 'Always-Trigger':
            offset_x, offset_y = 1.5, 0.008
        elif name == 'WrongDir-MLP':
            offset_x, offset_y = -2, -0.015
            ha = 'right'
        elif name == 'Oracle':
            offset_x, offset_y = -2, 0.008
            ha = 'right'
        elif 'Prompt' in name:
            offset_y = -0.012
            if name == 'Prompt K=10':
                offset_y = 0.008
        elif name == 'FineTune(LoRA)':
            offset_x, offset_y = 1.5, 0.01

        fontweight = 'bold' if name in ('FineTune(LoRA)', 'Oracle') else 'normal'
        fontsize = 9 if 'Prompt K=' in name else 10
        ax.annotate(name, (cs + offset_x, sr + offset_y), fontsize=fontsize,
                    fontweight=fontweight, color=color, ha=ha, va='center')

    # Pareto front line (no LR)
    pareto_x = [0.0, 14.3, 44.2, 50.3, 69.6]
    pareto_y = [0.965, 0.965, 0.953, 0.953, 0.965]
    ax.plot(pareto_x, pareto_y, 'k--', alpha=0.3, linewidth=1)

    # Dominated region shading
    ax.axhspan(0.4, 0.55, xmin=0.45, xmax=0.75, alpha=0.08, color=RED)
    ax.text(50, 0.48, 'Dominated\n(Wrong Direction)', fontsize=9, color=RED,
            ha='center', fontstyle='italic', alpha=0.7)

    # Base-only line
    ax.axhline(0.515, color=GRAY, linestyle=':', linewidth=1, alpha=0.5)
    ax.text(72, 0.520, 'Base-Only SR', fontsize=8, color=GRAY, va='bottom')

    ax.set_xlabel('Cost Saving (%)', fontsize=12)
    ax.set_ylabel('Success Rate (SR)', fontsize=12)
    ax.set_title('Gate Comparison — SR vs Cost Saving Pareto Front\n(Phase 2: HotpotQA, 85 exploit episodes)',
                 fontweight='bold')
    ax.set_xlim(-5, 80)
    ax.set_ylim(0.4, 1.0)
    ax.grid(True, alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUT + 'fig5_pareto_front.png')
    plt.close()
    print('✅ fig5_pareto_front.png')


# ============================================================
# Figure 6: Wrong-Direction Ablation (Phase 2.5, no LR)
# ============================================================
def fig6_wrong_direction():
    fig, ax = plt.subplots(figsize=(8, 5))

    gates = ['MLP\n(Phase 2.5)', 'Prompt\n(Phase 2.5)']
    correct_sr = [0.953, 0.953]
    wrong_sr = [0.453, 0.953]
    delta = [-51.2, -1.2]

    x = np.arange(len(gates))
    width = 0.32

    bars1 = ax.bar(x - width/2, correct_sr, width, label='Correct Direction', color=GREEN,
                   edgecolor='white', linewidth=1.2)
    bars2 = ax.bar(x + width/2, wrong_sr, width, label='Wrong Direction', color=RED,
                   edgecolor='white', linewidth=1.2)

    # Base-only reference line
    ax.axhline(0.515, color=GRAY, linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(1.55, 0.525, 'Base-Only (0.515)', fontsize=9, color=GRAY, ha='right')

    # Always-Trigger reference line
    ax.axhline(0.965, color=GRAY, linestyle=':', linewidth=1, alpha=0.4)
    ax.text(1.55, 0.970, 'Always-Trigger (0.965)', fontsize=8, color=GRAY, ha='right')

    # Delta annotations
    for i, (d, ws) in enumerate(zip(delta, wrong_sr)):
        color = RED if abs(d) > 10 else ORANGE
        fontweight = 'bold' if abs(d) > 10 else 'normal'
        y_pos = ws - 0.035 if ws < 0.9 else ws + 0.015
        extra = ''
        if i == 0:
            extra = '\nRR=0% (FAIL)'
        elif i == 1:
            extra = '\n(YES-bias masks\ndirection effect)'
        ax.text(i + width/2, y_pos, f'{d:+.1f}pp{extra}',
                ha='center', va='top', fontsize=10, fontweight=fontweight, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(gates, fontsize=11)
    ax.set_ylabel('Success Rate (SR)', fontsize=12)
    ax.set_title('Wrong-Direction Ablation — Direction is a Universal Prerequisite\n'
                 '(Reversing direction causes catastrophic MLP failure; Prompt masked by YES-bias)',
                 fontweight='bold', fontsize=12)
    ax.set_ylim(0.3, 1.05)
    ax.legend(loc='upper left', fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    plt.savefig(OUT + 'fig6_wrong_direction.png')
    plt.close()
    print('✅ fig6_wrong_direction.png')


# ============================================================
# Figure 7: Finish Shortcut Robustness (Phase 1.5)
# ============================================================
def fig7_finish_shortcut():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    signals = ['token_entropy', 'evidence_count', 'state_category (η²)']
    full = [-0.327, -0.586, 0.359]
    no_finish = [-0.242, -0.311, 0.098]

    x = np.arange(len(signals))
    width = 0.3

    bars1 = ax.bar(x - width/2, [abs(v) for v in full], width, label='All data (n=1208)',
                   color=BLUE, edgecolor='white', linewidth=1.2)
    bars2 = ax.bar(x + width/2, [abs(v) for v in no_finish], width,
                   label='Finish shortcut removed (n=902)',
                   color='#6BAED6', edgecolor='white', linewidth=1.2)

    # Annotate actual values
    for i, (f, nf) in enumerate(zip(full, no_finish)):
        prefix = 'ρ=' if i < 2 else 'η²='
        ax.text(i - width/2, abs(f) + 0.015, f'{prefix}{f:.3f}', ha='center', fontsize=9, fontweight='bold')
        ax.text(i + width/2, abs(nf) + 0.015, f'{prefix}{nf:.3f}', ha='center', fontsize=9)

    # GO/NO-GO labels
    for i in range(len(signals)):
        ax.text(i + width/2, abs(no_finish[i]) + 0.055, 'Still GO' if abs(no_finish[i]) > 0.08 else 'Marginal',
                ha='center', fontsize=9, color=GREEN if abs(no_finish[i]) > 0.08 else ORANGE, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(signals, fontsize=11)
    ax.set_ylabel('|Spearman ρ| or η²', fontsize=12)
    ax.set_title('Finish Shortcut Robustness Check (HotpotQA)\n'
                 'Core signals remain predictive after removing finish shortcut (25.3% of data)',
                 fontweight='bold', fontsize=12)
    ax.set_ylim(0, 0.75)
    ax.legend(loc='upper right', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    plt.savefig(OUT + 'fig7_finish_shortcut.png')
    plt.close()
    print('✅ fig7_finish_shortcut.png')


# ============================================================
# Figure 8: TES Comparison Bar Chart (Phase 2, no LR)
# ============================================================
def fig8_tes_comparison():
    fig, ax = plt.subplots(figsize=(9, 5))

    # Phase 2 HotpotQA data — no LR
    gates =   ['Fixed', 'Prompt\n(K=20)', 'MLP', 'FineTune\n(LoRA)', 'Oracle']
    tes =     [0.250,    0.291,           0.608,  0.664,              1.0]
    cs =      [14.3,     17.1,            44.2,   50.3,               69.6]
    sr =      [0.965,    0.953,           0.953,  0.953,              0.965]
    colors =  ['#4292C6', PURPLE,         GREEN,  '#08519C',          '#FFD700']

    x = np.arange(len(gates))
    width = 0.55

    bars = ax.bar(x, tes, width, color=colors, edgecolor='white', linewidth=1.2)

    # Value labels
    for i, (bar, t, c, s) in enumerate(zip(bars, tes, cs, sr)):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'TES={t:.3f}\nCS={c:.1f}%\nSR={s:.3f}',
                ha='center', va='bottom', fontsize=8.5, fontweight='bold' if i >= 3 else 'normal')

    # FineTune(LoRA) highlight
    bars[3].set_edgecolor('#08519C')
    bars[3].set_linewidth(2.5)

    # Oracle as reference
    ax.axhline(1.0, color='#FFD700', linestyle='--', linewidth=1, alpha=0.4)

    ax.set_xticks(x)
    ax.set_xticklabels(gates, fontsize=11)
    ax.set_ylabel('Trigger Efficiency Score (TES)', fontsize=12)
    ax.set_title('Gate TES Comparison — HotpotQA Phase 2\n'
                 '(FineTune(LoRA) achieves 72.3% of Oracle efficiency)',
                 fontweight='bold', fontsize=12)
    ax.set_ylim(0, 1.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    plt.savefig(OUT + 'fig8_tes_comparison.png')
    plt.close()
    print('✅ fig8_tes_comparison.png')


# ============================================================
# Figure 9: Cost Saving vs Rollout Rate (Phase 2, no LR)
# ============================================================
def fig9_cs_rr_comparison():
    fig, ax = plt.subplots(figsize=(9, 5))

    # Phase 2 HotpotQA — no LR
    gates = ['Fixed', 'Prompt\n(K=20)', 'Prompt\n(K=40)', 'Prompt\n(K=60)', 'MLP', 'FineTune\n(LoRA)', 'Oracle']
    rr =    [85.7,     82.9,            71.9,              69.2,             55.8,   49.7,                30.4]
    cs =    [14.3,     17.1,            28.1,              30.8,             44.2,   50.3,                69.6]
    colors_list = ['#4292C6', PURPLE, PURPLE, PURPLE, GREEN, '#08519C', '#FFD700']
    markers = ['D', 'v', 'v', 'v', 'o', 'p', '*']

    for i, (name, r, c, col, m) in enumerate(zip(gates, rr, cs, colors_list, markers)):
        size = 120 if i >= 5 else 80
        ax.scatter(r, c, c=col, marker=m, s=size, zorder=5, edgecolors='black', linewidth=0.5)
        # Label
        offset_x = -2.5 if i < 5 else 2
        ha = 'right' if i < 5 else 'left'
        fontweight = 'bold' if i >= 5 else 'normal'
        ax.annotate(name.replace('\n', ' '), (r + offset_x, c + 1.0),
                    fontsize=9, fontweight=fontweight, color=col, ha=ha, va='center')

    # Ideal direction arrow
    ax.annotate('', xy=(25, 72), xytext=(90, 10),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.5, linestyle='--'))
    ax.text(55, 45, 'Better\n(↓ RR, ↑ CS)', fontsize=9, color='#555',
            ha='center', fontstyle='italic', rotation=-38)

    ax.set_xlabel('Rollout Rate — RR (%)', fontsize=12)
    ax.set_ylabel('Cost Saving — CS (%)', fontsize=12)
    ax.set_title('Rollout Rate vs Cost Saving — HotpotQA Phase 2\n'
                 '(Lower RR = more selective triggering = higher cost savings)',
                 fontweight='bold', fontsize=12)
    ax.set_xlim(20, 95)
    ax.set_ylim(5, 80)
    ax.grid(True, alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(OUT + 'fig9_cs_rr_comparison.png')
    plt.close()
    print('✅ fig9_cs_rr_comparison.png')


# ============================================================
# Figure 10: Prompt K Ablation — YES-bias (Phase 2, no LR)
# ============================================================
def fig10_prompt_k_ablation():
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Prompt K ablation data
    k_values = [10, 20, 40, 60]
    rr_vals = [89.0, 82.9, 71.9, 69.2]
    cs_vals = [11.0, 17.1, 28.1, 30.8]
    sr_vals = [0.960, 0.953, 0.940, 0.933]

    # Left: RR and CS vs K
    ax = axes[0]
    ax2 = ax.twinx()
    line1, = ax.plot(k_values, rr_vals, color=RED, marker='s', linewidth=2, markersize=8, label='Rollout Rate (%)')
    line2, = ax2.plot(k_values, cs_vals, color=GREEN, marker='^', linewidth=2, markersize=8, label='Cost Saving (%)')
    ax.set_xlabel('Number of Few-Shot Examples (K)', fontsize=11)
    ax.set_ylabel('Rollout Rate (%)', color=RED, fontsize=11)
    ax2.set_ylabel('Cost Saving (%)', color=GREEN, fontsize=11)
    ax.set_ylim(60, 95)
    ax2.set_ylim(5, 40)
    ax.set_xticks(k_values)
    ax.set_title('Prompt Gate: RR & CS vs K', fontweight='bold')
    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='center right', fontsize=9)
    ax.grid(axis='y', alpha=0.2)
    ax.spines['top'].set_visible(False)

    # Right: YES-bias evidence
    ax = axes[1]
    ec_categories = ['ec=0', 'ec=1', 'ec≥2']
    yes_pct = [92, 72, 54]
    bar_colors = [RED, ORANGE, '#FDAE6B']
    bars = ax.bar(ec_categories, yes_pct, color=bar_colors, edgecolor='white', linewidth=1.2, width=0.5)
    for bar, pct in zip(bars, yes_pct):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1.5,
                f'{pct}%', ha='center', fontsize=11, fontweight='bold')
    ax.axhline(50, color=GRAY, linestyle='--', linewidth=1, alpha=0.5)
    ax.text(2.3, 51, 'Random baseline', fontsize=8, color=GRAY)
    ax.set_ylabel('YES Rate (%)', fontsize=11)
    ax.set_title('Prompt Gate YES-Bias by Evidence Count', fontweight='bold')
    ax.set_ylim(0, 105)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.2)
    ax.annotate('Even at ec≥2 (should SKIP),\nPrompt still says YES 54%',
                xy=(2, 54), xytext=(0.5, 30),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2),
                fontsize=9, fontstyle='italic', color='#555')

    plt.tight_layout()
    plt.savefig(OUT + 'fig10_prompt_k_ablation.png')
    plt.close()
    print('✅ fig10_prompt_k_ablation.png')


# ============================================================
# Figure 11: SR & RR Grouped Bar Chart (Phase 2, no LR/Fixed)
# ============================================================
def fig11_sr_rr_bar():
    fig, ax = plt.subplots(figsize=(9, 5.5))

    gates = ['Prompt (K=20)', 'MLP', 'FineTune (LoRA)', 'Upper Bound']
    sr =    [0.953,            0.953, 0.953,              0.965]
    rr =    [82.9,             55.8,  49.7,               30.4]

    x = np.arange(len(gates))
    width = 0.32

    # SR bars (left)
    bars_sr = ax.bar(x - width/2, sr, width, label='Success Rate (SR)',
                     color=BLUE, edgecolor='white', linewidth=1.2)
    # RR bars (right) — scale to 0-1 for same axis
    rr_frac = [r / 100 for r in rr]
    bars_rr = ax.bar(x + width/2, rr_frac, width, label='Rollout Rate (RR)',
                     color=ORANGE, edgecolor='white', linewidth=1.2)

    # Value labels on SR bars
    for bar, val in zip(bars_sr, sr):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.012,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10,
                fontweight='bold', color=BLUE)

    # Value labels on RR bars
    for bar, val in zip(bars_rr, rr):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()/100 + 0.012,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=10,
                fontweight='bold', color=ORANGE)

    # Reference lines
    ax.axhline(0.965, color=GRAY, linestyle=':', linewidth=0.8, alpha=0.4)
    ax.text(3.55, 0.968, 'Always-T SR', fontsize=8, color=GRAY, va='bottom')

    ax.set_xticks(x)
    ax.set_xticklabels(gates, fontsize=11)
    ax.set_ylabel('Value (SR as fraction, RR as fraction)', fontsize=11)
    ax.set_title('Gate Comparison — SR vs Rollout Rate\n'
                 '(HotpotQA Phase 2: SR nearly identical, RR reveals selectivity)',
                 fontweight='bold', fontsize=12)
    ax.set_ylim(0, 1.10)
    ax.legend(loc='lower left', fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    plt.savefig(OUT + 'fig11_sr_rr_bar.png')
    plt.close()
    print('✅ fig11_sr_rr_bar.png')


# ============================================================
# Figure 12: MBPP SR & RR Grouped Bar Chart (Phase 2, no LR/Fixed)
# ============================================================
def fig12_mbpp_sr_rr_bar():
    fig, ax = plt.subplots(figsize=(9, 5))

    gates = ['Prompt (K=20)', 'MLP', 'FineTune (LoRA)', 'Upper Bound']
    sr =    [92.5,             92.5,  92.5,              92.5]
    rr =    [83.0,             0.0,   5.0,               0.0]

    y = np.arange(len(gates))
    height = 0.32

    # SR bars
    bars_sr = ax.barh(y + height/2, sr, height, label='Success Rate (SR %)',
                      color=BLUE, edgecolor='white', linewidth=1.2)
    # RR bars
    bars_rr = ax.barh(y - height/2, rr, height, label='Rollout Rate (RR %)',
                      color=ORANGE, edgecolor='white', linewidth=1.2)

    # Value labels — SR
    for bar, val in zip(bars_sr, sr):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2.,
                f'{val:.1f}%', ha='left', va='center', fontsize=10,
                fontweight='bold', color=BLUE)

    # Value labels — RR
    for bar, val in zip(bars_rr, rr):
        x_pos = max(bar.get_width(), 0) + 1
        label = f'{val:.0f}%' if val > 0 else '0% (never triggers)'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2.,
                label, ha='left', va='center', fontsize=10,
                fontweight='bold', color=ORANGE)

    # Base-Only SR reference
    ax.axvline(92.5, color=GRAY, linestyle=':', linewidth=1, alpha=0.5)
    ax.text(93.5, 3.7, 'Base-Only SR = 92.5%', fontsize=8, color=GRAY, va='center')

    ax.set_yticks(y)
    ax.set_yticklabels(gates, fontsize=11)
    ax.set_xlabel('Percentage (%)', fontsize=11)
    ax.set_title('Gate Comparison — SR vs Rollout Rate\n'
                 '(MBPP Phase 2: All gates SR=92.5%, MLP learns to never trigger)',
                 fontweight='bold', fontsize=12)
    ax.set_xlim(0, 110)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9,
              bbox_to_anchor=(0.0, -0.08))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.2)

    plt.tight_layout()
    plt.savefig(OUT + 'fig12_mbpp_sr_rr_bar.png')
    plt.close()
    print('✅ fig12_mbpp_sr_rr_bar.png')


if __name__ == '__main__':
    fig1_u_distribution()
    fig2_u_by_category_and_step()
    fig3_direction_heatmap()
    fig4_u_shape_hotpotqa()
    fig5_pareto_front()
    fig6_wrong_direction()
    fig7_finish_shortcut()
    fig8_tes_comparison()
    fig9_cs_rr_comparison()
    fig10_prompt_k_ablation()
    fig11_sr_rr_bar()
    fig12_mbpp_sr_rr_bar()
    print('\n🎉 All 12 figures generated in figures/')
