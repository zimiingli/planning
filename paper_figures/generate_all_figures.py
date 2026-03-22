#!/usr/bin/env python3
"""
Generate all paper figures for EAAG paper.
Output to: planning/paper_figures/
"""
import json
import glob
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT_DIR = Path(__file__).parent
PROJECT = Path(__file__).parent.parent.parent

# ── Data collection ────────────────────────────────────────────

def collect_results():
    """Collect all results across environments."""
    all_envs = ['hotpotqa', 'apps', 'webshop', 'twexpress', 'plancraft',
                'fever', 'apps_interview', 'cruxeval']
    env_data = {}

    for env in all_envs:
        results = defaultdict(list)
        patterns = [
            f"results/phase6/{env}/{env}/*/seed_*/summary.json",
            f"results/phase6/path_e/{env}/*/seed_*/summary.json",
            f"results/phase5/comparison/{env}/*/seed_*/summary.json",
            f"results/phase5/competing_baselines_calibrated/{env}/*/seed_*/summary.json",
            f"results/phase6/new_baselines/{env}/*/seed_*/summary.json",
            f"results/phase5/{env}/{env}/*/seed_*/summary.json",
            f"results/phase4/{env}/core/*/seed_*/performance_summary.json",
        ]
        for pattern in patterns:
            for f in sorted(glob.glob(str(PROJECT / pattern))):
                try:
                    d = json.load(open(f))
                    method = f.split("/")[-3]
                    sr = d.get("success_rate", d.get("overall_stats", {}).get("success_rate", None))
                    ro = d.get("avg_rollouts_per_ep", d.get("overall_stats", {}).get("avg_rollouts_per_ep", None))
                    if sr is not None:
                        results[method].append((float(sr), float(ro) if ro else 0.0))
                except:
                    pass
        env_data[env] = results
    return env_data

def ms(env_data, env, m):
    if m not in env_data[env]:
        return None, None
    vals = env_data[env][m]
    return sum(v[0] for v in vals)/len(vals), sum(v[1] for v in vals)/len(vals)


# ══════════════════════════════════════════════════════════════════
# Figure 1: Direction Reversal Signal Heatmap
# ══════════════════════════════════════════════════════════════════

def fig1_signal_heatmap():
    """8 env × N signals heatmap of Spearman ρ."""
    envs = ['hotpotqa', 'apps', 'webshop', 'twexpress', 'plancraft',
            'fever', 'apps_interview', 'cruxeval']
    env_labels = ['HotpotQA', 'APPS', 'WebShop', 'TWExpress', 'Plancraft',
                  'FEVER', 'APPS Intv', 'CRUXEval']

    signals = ['step_count', 'token_entropy', 'evidence_count',
               'is_finish_proposed', 'claim_length']
    signal_labels = ['step_count', 'token_entropy', 'evidence_count',
                     'is_finish', 'claim_length']

    # Load Step 1 data
    rho_matrix = np.full((len(envs), len(signals)), np.nan)

    for i, env in enumerate(envs):
        for pattern in [f"results/phase6/{env}/{env}/step1_signal_discovery.json",
                       f"results/phase5/calibration_data/{env}/phase1_signal_data.json"]:
            p = PROJECT / pattern
            if not p.exists():
                continue
            if 'step1' in str(p):
                try:
                    d = json.load(open(p))
                    corrs = d.get('correlations', {})
                    for j, sig in enumerate(signals):
                        if sig in corrs:
                            info = corrs[sig]
                            if isinstance(info, dict) and 'spearman_rho' in info:
                                rho_matrix[i, j] = info['spearman_rho']
                    break
                except:
                    pass

    fig, ax = plt.subplots(figsize=(8, 5))

    # Mask NaN
    masked = np.ma.masked_invalid(rho_matrix)

    im = ax.imshow(masked, cmap='RdBu_r', vmin=-0.7, vmax=0.7, aspect='auto')

    ax.set_xticks(range(len(signals)))
    ax.set_xticklabels(signal_labels, rotation=45, ha='right', fontsize=10)
    ax.set_yticks(range(len(envs)))
    ax.set_yticklabels(env_labels, fontsize=10)

    # Add text annotations
    for i in range(len(envs)):
        for j in range(len(signals)):
            val = rho_matrix[i, j]
            if not np.isnan(val):
                color = 'white' if abs(val) > 0.35 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                       color=color, fontsize=8, fontweight='bold')

    plt.colorbar(im, ax=ax, label='Spearman ρ', shrink=0.8)
    ax.set_title('Signal-Utility Direction Varies Across Environments', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig1_signal_heatmap.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig1_signal_heatmap.pdf', bbox_inches='tight')
    plt.close()
    print("✅ Figure 1: Signal heatmap saved")


# ══════════════════════════════════════════════════════════════════
# Figure 2: Pareto Frontier (SR vs Total Cost)
# ══════════════════════════════════════════════════════════════════

def fig2_pareto():
    """SR vs Total Cost Pareto plot for 4 main + 2 diagnostic environments."""
    env_data = collect_results()

    main_envs = ['hotpotqa', 'apps', 'webshop', 'fever']
    diag_envs = ['twexpress', 'plancraft']
    all_plot_envs = main_envs + diag_envs
    env_titles = {
        'hotpotqa': 'HotpotQA', 'apps': 'APPS (Intro)',
        'webshop': 'WebShop', 'fever': 'FEVER',
        'twexpress': 'TWExpress', 'plancraft': 'Plancraft'
    }

    needs_p1 = {"scg_finetune_lr", "cats", "seag", "corefine"}

    methods_config = [
        ("base_only", "Base", "gray", "s", 60),
        ("always_trigger", "Always", "gray", "^", 60),
        ("scg_finetune_lr", "SCG†", "silver", "D", 70),
        ("cats", "CaTS†", "#1f77b4", "o", 50),
        ("seag", "SEAG†", "#2ca02c", "o", 50),
        ("corefine", "CoRefine†", "#9467bd", "o", 50),
        ("catts", "CATTS", "#8c564b", "o", 50),
        ("auq", "AUQ", "#ff7f0e", "v", 60),
        ("s1_budget", "s1", "#e377c2", "v", 60),
        ("se_online_decay_local", "EAAG (Ours)", "red", "*", 150),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for idx, env in enumerate(all_plot_envs):
        ax = axes[idx]
        _, always_ro = ms(env_data, env, "always_trigger")
        if always_ro is None:
            always_ro = 0

        for method, label, color, marker, size in methods_config:
            sr, ro = ms(env_data, env, method)
            if sr is None:
                continue
            total = ro + always_ro if method in needs_p1 else ro
            ax.scatter(total, sr * 100, c=color, marker=marker, s=size,
                      label=label, zorder=5 if 'EAAG' in label else 3,
                      edgecolors='black' if 'EAAG' in label else 'none',
                      linewidths=1.5 if 'EAAG' in label else 0)

        base_sr, _ = ms(env_data, env, "base_only")
        if base_sr:
            ax.axhline(y=base_sr * 100, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)

        ax.set_title(env_titles.get(env, env), fontsize=11, fontweight='bold')
        ax.set_xlabel('Total Cost (ro/ep)', fontsize=9)
        ax.set_ylabel('SR (%)', fontsize=9)
        ax.grid(True, alpha=0.3)

    # Legend on last unused space or outside
    handles, labels = axes[0].get_legend_handles_labels()
    # Remove duplicates
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(),
              loc='lower center', ncol=5, fontsize=8,
              bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('SR vs Total Cost (incl. Phase 1 amortized)', fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig2_pareto.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig2_pareto.pdf', bbox_inches='tight')
    plt.close()
    print("✅ Figure 2: Pareto frontier saved")


# ══════════════════════════════════════════════════════════════════
# Figure 3: BSW Wrong Direction Cost vs |ρ|
# ══════════════════════════════════════════════════════════════════

def fig3_bsw_cost():
    """Scatter: |ρ| vs BSW degradation."""
    data = [
        # (env, |ρ|, BSW_SR, always_SR, label)
        ("FEVER", 0.619, 0.630, 0.998, "FEVER"),
        ("HotpotQA", 0.494, 0.582, 0.970, "HotpotQA"),
        ("CRUXEval", 0.184, 0.875, 0.995, "CRUXEval"),
        ("TWExpress", 0.477, 0.990, 0.993, "TWExpress"),
        ("APPS Intv", 0.339, 0.795, 0.795, "APPS Intv\n(rollout-safe)"),
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    for env, rho, bsw, always, label in data:
        degradation = (always - bsw) * 100  # in pp
        color = 'red' if degradation > 5 else 'blue'
        ax.scatter(rho, degradation, s=100, c=color, zorder=5, edgecolors='black')
        offset = (0.02, 2) if degradation > 5 else (0.02, -4)
        ax.annotate(label, (rho, degradation),
                   xytext=(rho + offset[0], degradation + offset[1]),
                   fontsize=9, ha='left')

    # Trend line (excluding rollout-safe)
    xs = [0.619, 0.494, 0.184, 0.477]
    ys = [(0.998-0.630)*100, (0.970-0.582)*100, (0.995-0.875)*100, (0.993-0.990)*100]
    z = np.polyfit(xs, ys, 1)
    p = np.poly1d(z)
    x_line = np.linspace(0.1, 0.7, 100)
    ax.plot(x_line, p(x_line), '--', color='gray', alpha=0.5, label=f'trend (r={np.corrcoef(xs,ys)[0,1]:.2f})')

    ax.set_xlabel('Signal Strength |ρ|', fontsize=11)
    ax.set_ylabel('BSW Degradation (pp vs always_trigger)', fontsize=11)
    ax.set_title('Cost of Wrong Direction: Stronger Signal = Higher Penalty', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.05, 0.75)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig3_bsw_cost.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig3_bsw_cost.pdf', bbox_inches='tight')
    plt.close()
    print("✅ Figure 3: BSW cost scatter saved")


# ══════════════════════════════════════════════════════════════════
# Figure 4: Feature Usage Heatmap
# ══════════════════════════════════════════════════════════════════

def fig4_feature_heatmap():
    """Binary heatmap: which features selected in which env."""
    envs = ['hotpotqa', 'apps', 'webshop', 'twexpress', 'plancraft', 'fever', 'apps_interview']
    env_labels = ['HotpotQA', 'APPS', 'WebShop', 'TWExpress', 'Plancraft', 'FEVER', 'APPS Intv']

    # Collected from results
    env_features = {
        'hotpotqa': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                     'evidence_count', 'is_finish', 'state_length', 'num_numbers', 'llm_query_length'],
        'apps': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                 'state_length', 'num_numbers', 'has_error', 'h_pca_9', 'llm_action_type'],
        'webshop': ['num_available_actions', 'num_numbers', 'state_length', 'step_x_entropy',
                    'token_entropy', 'is_finish', 'llm_price_mentioned', 'llm_action_is_click',
                    'llm_step_early', 'llm_instruction_keyword_count'],
        'twexpress': ['step_count', 'step_ratio', 'token_entropy', 'entropy_sq', 'state_length',
                      'num_numbers', 'llm_text_length', 'llm_closed_ratio', 'llm_action_look_around', 'llm_already_open'],
        'plancraft': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                      'state_length', 'num_numbers', 'num_available_actions', 'h_pca_0', 'h_pca_10'],
        'fever': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                  'state_length', 'h_pca_1', 'h_pca_9', 'llm_text_length_normalized', 'llm_has_claim'],
        'apps_interview': ['step_count', 'step_ratio', 'has_error'],
    }

    # Get all unique features, separate universal vs LLM
    all_features = set()
    for feats in env_features.values():
        all_features.update(feats)

    universal = sorted([f for f in all_features if not f.startswith('llm_') and not f.startswith('h_pca')])
    llm_feats = sorted([f for f in all_features if f.startswith('llm_')])
    pca_feats = sorted([f for f in all_features if f.startswith('h_pca')])
    ordered_features = universal + pca_feats + llm_feats

    # Build matrix
    matrix = np.zeros((len(envs), len(ordered_features)))
    for i, env in enumerate(envs):
        for f in env_features.get(env, []):
            if f in ordered_features:
                j = ordered_features.index(f)
                matrix[i, j] = 1

    fig, ax = plt.subplots(figsize=(14, 5))

    # Color: universal=blue, LLM=orange, PCA=green
    colors = np.zeros_like(matrix)
    for j, f in enumerate(ordered_features):
        if f.startswith('llm_'):
            colors[:, j] = 2  # orange
        elif f.startswith('h_pca'):
            colors[:, j] = 3  # green
        else:
            colors[:, j] = 1  # blue

    display = matrix * colors
    cmap = matplotlib.colors.ListedColormap(['white', '#4C72B0', '#DD8452', '#55A868'])

    ax.imshow(display, cmap=cmap, aspect='auto', vmin=0, vmax=3)

    ax.set_xticks(range(len(ordered_features)))
    ax.set_xticklabels(ordered_features, rotation=60, ha='right', fontsize=7)
    ax.set_yticks(range(len(envs)))
    ax.set_yticklabels(env_labels, fontsize=10)

    # Divider lines
    n_uni = len(universal)
    n_pca = len(pca_feats)
    ax.axvline(x=n_uni - 0.5, color='gray', linewidth=1, linestyle='--')
    ax.axvline(x=n_uni + n_pca - 0.5, color='gray', linewidth=1, linestyle='--')

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#4C72B0', label='Universal'),
        mpatches.Patch(facecolor='#55A868', label='PCA (hidden state)'),
        mpatches.Patch(facecolor='#DD8452', label='LLM-discovered'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    ax.set_title('EAAG Feature Selection Across Environments', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig4_feature_heatmap.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig4_feature_heatmap.pdf', bbox_inches='tight')
    plt.close()
    print("✅ Figure 4: Feature usage heatmap saved")


# ══════════════════════════════════════════════════════════════════
# Figure 5: LLM Ablation (EAAG vs v2)
# ══════════════════════════════════════════════════════════════════

def fig5_llm_ablation():
    """Bar chart: EAAG (with LLM) vs principled_v2 (without LLM)."""
    env_data = collect_results()

    envs = ['hotpotqa', 'apps', 'webshop', 'twexpress', 'plancraft', 'fever', 'apps_interview']
    labels = ['HotpotQA', 'APPS', 'WebShop', 'TWExpress', 'Plancraft', 'FEVER', 'APPS Intv']

    eaag_name = 'se_online_decay_local'
    v2_name = 'principled_v2'

    eaag_srs = []
    v2_srs = []

    for env in envs:
        sr_e, _ = ms(env_data, env, eaag_name)
        # Find best v2
        v2_methods = [m for m in env_data[env] if m.startswith('principled') and 'optimistic' not in m]
        if v2_methods:
            best_v2 = max(v2_methods, key=lambda m: ms(env_data, env, m)[0] or 0)
            sr_v, _ = ms(env_data, env, best_v2)
        else:
            sr_v = None

        eaag_srs.append(sr_e * 100 if sr_e else 0)
        v2_srs.append(sr_v * 100 if sr_v else 0)

    x = np.arange(len(envs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    bars1 = ax.bar(x - width/2, eaag_srs, width, label='EAAG (with LLM)', color='#E74C3C', alpha=0.85)
    bars2 = ax.bar(x + width/2, v2_srs, width, label='Principled v2 (no LLM)', color='#3498DB', alpha=0.85)

    # Add value labels
    for bar in bars1:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.5, f'{h:.1f}',
                   ha='center', va='bottom', fontsize=7)
    for bar in bars2:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2., h + 0.5, f'{h:.1f}',
                   ha='center', va='bottom', fontsize=7)

    ax.set_xlabel('Environment', fontsize=11)
    ax.set_ylabel('SR (%)', fontsize=11)
    ax.set_title('LLM Ablation: EAAG vs Principled v2 (no LLM reflection)', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig5_llm_ablation.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig5_llm_ablation.pdf', bbox_inches='tight')
    plt.close()
    print("✅ Figure 5: LLM ablation saved")


# ══════════════════════════════════════════════════════════════════
# Figure 6: FEVER Exploration Bias Analysis
# ══════════════════════════════════════════════════════════════════

def fig6_fever_bias():
    """Bar chart comparing SCG Phase 1 data vs SE exploration data."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Data
    methods = ['SCG\n(Phase 1)', 'EAAG\n(explore)']

    # Panel 1: Positive utility rate
    ax = axes[0]
    vals = [51.8, 7.3]
    colors = ['#2ECC71', '#E74C3C']
    ax.bar(methods, vals, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax.set_ylabel('Positive Utility Rate (%)', fontsize=10)
    ax.set_title('Calibration Data Quality', fontsize=11, fontweight='bold')
    for i, v in enumerate(vals):
        ax.text(i, v + 1, f'{v:.1f}%', ha='center', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 65)
    ax.grid(True, axis='y', alpha=0.3)

    # Panel 2: Episode length
    ax = axes[1]
    vals = [1.4, 5.3]
    ax.bar(methods, vals, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax.set_ylabel('Avg Steps/Episode', fontsize=10)
    ax.set_title('Episode Length', fontsize=11, fontweight='bold')
    for i, v in enumerate(vals):
        ax.text(i, v + 0.1, f'{v:.1f}', ha='center', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 7)
    ax.grid(True, axis='y', alpha=0.3)

    # Panel 3: Final SR
    ax = axes[2]
    vals = [98.0, 49.8]
    ax.bar(methods, vals, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
    ax.set_ylabel('SR (%)', fontsize=10)
    ax.set_title('Final Performance', fontsize=11, fontweight='bold')
    for i, v in enumerate(vals):
        ax.text(i, v + 1, f'{v:.1f}%', ha='center', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.grid(True, axis='y', alpha=0.3)

    fig.suptitle('FEVER: Exploration Bias Analysis — Why EAAG Underperforms SCG',
                fontsize=13, fontweight='bold', y=1.03)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig6_fever_bias.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig6_fever_bias.pdf', bbox_inches='tight')
    plt.close()
    print("✅ Figure 6: FEVER exploration bias saved")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Output directory: {OUT_DIR}")
    print(f"Project root: {PROJECT}")
    print()

    fig1_signal_heatmap()
    fig2_pareto()
    fig3_bsw_cost()
    fig4_feature_heatmap()
    fig5_llm_ablation()
    fig6_fever_bias()

    print()
    print(f"All figures saved to {OUT_DIR}/")
    print("Files: fig1_signal_heatmap, fig2_pareto, fig3_bsw_cost,")
    print("       fig4_feature_heatmap, fig5_llm_ablation, fig6_fever_bias")
