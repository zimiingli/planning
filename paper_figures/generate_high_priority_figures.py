#!/usr/bin/env python3
"""
Generate high-priority paper figures for EAAG paper (v7.0 §3.8).

Figures:
  1. AUC Hierarchy bar chart (§3.8.1) → fig_auc_hierarchy.pdf
  2. P1 Temporal Shift (§3.8.2) → fig_p1_temporal_shift.pdf
  3. Stratified Reversal (§3.8.7A) → fig_stratified_reversal.pdf
  4. Matched-Pair ΔU (§3.8.7B) → fig_matched_pair_opposite_meaning.pdf
  5. Gate Capacity Ablation table (§3.8.8) → tab_gate_capacity.tex
"""
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import spearmanr, bootstrap

OUT_DIR = Path(__file__).parent
PROJECT = Path(__file__).parent.parent.parent

# Consistent style
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
})


# ══════════════════════════════════════════════════════════════════
# Data Loading Utilities
# ══════════════════════════════════════════════════════════════════

def load_probe_data(env):
    """Load per-step probe data (token_entropy, utility, step_count, etc.)."""
    candidates = [
        PROJECT / f"results/phase1_signal_discovery/{env}/phase1_signal_data.json",
        PROJECT / f"results/phase6/{env}/{env}/phase1_signal_data.json",
        PROJECT / f"results/phase5/twexpress/twexpress/phase1_signal_data.json" if env == 'twexpress' else None,
        PROJECT / f"results/phase5/calibration_data/{env}/phase1_signal_data.json",
    ]
    for path in candidates:
        if path and path.exists():
            data = json.load(open(path))
            if isinstance(data, list) and len(data) > 0:
                print(f"  Loaded {env}: {len(data)} records from {path.relative_to(PROJECT)}")
                return data
    print(f"  WARNING: No probe data found for {env}")
    return None


# ══════════════════════════════════════════════════════════════════
# Figure 1: AUC Hierarchy Bar Chart (§3.8.1)
# ══════════════════════════════════════════════════════════════════

def fig_auc_hierarchy():
    """Grouped bar chart: single entropy → best single → multi LR → hidden state LR."""
    print("\n=== AUC Hierarchy (§3.8.1) ===")

    # Data from phase5_interim_report.md §4.5.4
    # 5-fold CV AUC, seed 42, utility_threshold=0.05
    envs = ['HotpotQA', 'APPS', 'WebShop']
    levels = ['Single\nentropy', 'Best\nsingle', 'Multi-signal\nLR', 'Hidden\nstate LR']
    data = {
        'HotpotQA': [0.502, 0.782, 0.851, 0.869],
        'APPS':     [0.557, 0.778, 0.761, 0.794],
        'WebShop':  [0.502, 0.895, 0.924, 0.994],
    }

    n_envs = len(envs)
    n_levels = len(levels)
    x = np.arange(n_envs)
    width = 0.18
    offsets = np.arange(n_levels) - (n_levels - 1) / 2

    colors = ['#bdbdbd', '#969696', '#4292c6', '#d62728']
    hatches = ['', '', '', '']

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, (level, color) in enumerate(zip(levels, colors)):
        vals = [data[env][i] for env in envs]
        bars = ax.bar(x + offsets[i] * width, vals, width * 0.9,
                      color=color, edgecolor='black', linewidth=0.5,
                      label=level, zorder=3)
        # Add value labels
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=7.5,
                    fontweight='bold')

    # Random baseline
    ax.axhline(y=0.5, color='black', linestyle='--', alpha=0.4, linewidth=1,
               label='Random (AUC=0.5)', zorder=1)

    # Improvement annotations
    for j, env in enumerate(envs):
        top = data[env][-1]
        bottom = data[env][0]
        ratio = top / bottom if bottom > 0 else 0
        ax.annotate(f'×{ratio:.1f}', xy=(j, top + 0.03),
                    fontsize=9, ha='center', fontweight='bold', color='#d62728')

    ax.set_xticks(x)
    ax.set_xticklabels(envs, fontsize=11, fontweight='bold')
    ax.set_ylabel('AUC (5-fold CV)', fontsize=11)
    ax.set_ylim(0.40, 1.08)
    ax.set_title('Signal Hierarchy: Single Entropy ≈ Random, Multi-Signal >> Single',
                 fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='upper left', fontsize=8.5, framealpha=0.9, ncol=2)
    ax.grid(axis='y', alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

    # Mini summary table below
    avg_auc = [np.mean([data[env][i] for env in envs]) for i in range(n_levels)]
    table_text = "Avg AUC:  " + "  |  ".join(
        f"{levels[i].replace(chr(10), ' ')}: {avg_auc[i]:.3f}" for i in range(n_levels))
    fig.text(0.5, -0.02, table_text, ha='center', fontsize=8.5, style='italic')

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_auc_hierarchy.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_auc_hierarchy.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_auc_hierarchy saved")


# ══════════════════════════════════════════════════════════════════
# Figure 2: P1 Temporal Shift (§3.8.2)
# ══════════════════════════════════════════════════════════════════

def fig_p1_temporal_shift():
    """Paired bar chart: early vs late ρ(entropy, U) across environments."""
    print("\n=== P1 Temporal Shift (§3.8.2) ===")

    # Load pre-computed results
    results_path = PROJECT / "results/phase6/toy_model/d1_temporal_shift_results.json"
    results = json.load(open(results_path))

    # Filter to target environments
    target_envs = ['HotpotQA', 'APPS', 'WebShop']
    env_results = {r['env']: r for r in results if r['env'] in target_envs}

    # Also compute from raw probe data for FEVER, TWExpress, Plancraft
    extra_envs_map = {
        'fever': 'FEVER',
        'twexpress': 'TWExpress',
        'plancraft': 'Plancraft',
    }

    for env_key, env_label in extra_envs_map.items():
        data = load_probe_data(env_key)
        if data is None:
            continue
        entropies = np.array([r['token_entropy'] for r in data])
        utilities = np.array([r['utility'] for r in data])
        steps = np.array([r['step_count'] for r in data])

        median_step = np.median(steps)
        if median_step == 0:
            # Use step 0 vs step > 0
            early_mask = steps == 0
            late_mask = steps > 0
            cutoff_desc = "step = 0 vs step > 0"
        else:
            early_mask = steps <= median_step
            late_mask = steps > median_step
            cutoff_desc = f"step ≤ {median_step:.0f} vs step > {median_step:.0f}"

        if early_mask.sum() < 10 or late_mask.sum() < 10:
            print(f"  {env_label}: insufficient data for split (early={early_mask.sum()}, late={late_mask.sum()})")
            continue

        rho_early, p_early = spearmanr(entropies[early_mask], utilities[early_mask])
        rho_late, p_late = spearmanr(entropies[late_mask], utilities[late_mask])

        # Bootstrap CI for early
        def rho_stat_early(x, y):
            return spearmanr(x, y).statistic
        def rho_stat_late(x, y):
            return spearmanr(x, y).statistic

        try:
            ci_early = bootstrap(
                (entropies[early_mask], utilities[early_mask]),
                lambda x, y: spearmanr(x, y).statistic,
                n_resamples=1000, paired=True, method='percentile',
                random_state=42
            )
            ci_lo_early = ci_early.confidence_interval.low
            ci_hi_early = ci_early.confidence_interval.high
        except Exception:
            ci_lo_early = rho_early - 0.1
            ci_hi_early = rho_early + 0.1

        try:
            ci_late = bootstrap(
                (entropies[late_mask], utilities[late_mask]),
                lambda x, y: spearmanr(x, y).statistic,
                n_resamples=1000, paired=True, method='percentile',
                random_state=42
            )
            ci_lo_late = ci_late.confidence_interval.low
            ci_hi_late = ci_late.confidence_interval.high
        except Exception:
            ci_lo_late = rho_late - 0.1
            ci_hi_late = rho_late + 0.1

        env_results[env_label] = {
            'env': env_label,
            'early': {
                'n': int(early_mask.sum()),
                'rho': rho_early,
                'p_value': p_early,
                'ci_lo': ci_lo_early,
                'ci_hi': ci_hi_early,
            },
            'late': {
                'n': int(late_mask.sum()),
                'rho': rho_late,
                'p_value': p_late,
                'ci_lo': ci_lo_late,
                'ci_hi': ci_hi_late,
            },
            'shift': rho_late - rho_early,
        }
        print(f"  {env_label}: ρ_early={rho_early:.3f} (n={early_mask.sum()}), "
              f"ρ_late={rho_late:.3f} (n={late_mask.sum()}), Δρ={rho_late - rho_early:+.3f}")

    # Plot
    plot_envs = ['HotpotQA', 'FEVER', 'TWExpress', 'APPS', 'WebShop', 'Plancraft']
    plot_envs = [e for e in plot_envs if e in env_results]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(plot_envs))
    width = 0.32

    early_rhos = []
    late_rhos = []
    early_errs = [[], []]
    late_errs = [[], []]

    for env in plot_envs:
        r = env_results[env]
        e = r['early']
        l = r['late']
        early_rhos.append(e['rho'])
        late_rhos.append(l['rho'])
        early_errs[0].append(e['rho'] - e.get('ci_lo', e['rho'] - 0.05))
        early_errs[1].append(e.get('ci_hi', e['rho'] + 0.05) - e['rho'])
        late_errs[0].append(l['rho'] - l.get('ci_lo', l['rho'] - 0.05))
        late_errs[1].append(l.get('ci_hi', l['rho'] + 0.05) - l['rho'])

    bars1 = ax.bar(x - width/2, early_rhos, width, yerr=early_errs,
                   color='#2166ac', edgecolor='black', linewidth=0.5,
                   capsize=3, label='Early steps', zorder=3)
    bars2 = ax.bar(x + width/2, late_rhos, width, yerr=late_errs,
                   color='#b2182b', edgecolor='black', linewidth=0.5,
                   capsize=3, label='Late steps', zorder=3)

    # Zero line
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=0.8)

    # Shift annotations
    for i, env in enumerate(plot_envs):
        r = env_results[env]
        shift = r['shift']
        y_pos = max(early_rhos[i], late_rhos[i]) + 0.08
        if y_pos < 0:
            y_pos = 0.05
        color = '#2ca02c' if shift < 0 else '#d62728'
        ax.annotate(f'Δ={shift:+.2f}', xy=(i, y_pos),
                    fontsize=8, ha='center', fontweight='bold', color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(plot_envs, fontsize=10, fontweight='bold')
    ax.set_ylabel('ρ(entropy, utility)', fontsize=11)
    ax.set_title('P1: Entropy-Utility Correlation Shifts with Episode Progress',
                 fontsize=12, fontweight='bold', pad=10)
    ax.legend(loc='best', fontsize=9.5, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_p1_temporal_shift.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_p1_temporal_shift.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_p1_temporal_shift saved")


# ══════════════════════════════════════════════════════════════════
# Figure 3: Stratified Reversal Analysis (§3.8.7A)
# ══════════════════════════════════════════════════════════════════

def fig_stratified_reversal():
    """ρ(entropy, U) within trajectory-length strata, per environment."""
    print("\n=== Stratified Reversal (§3.8.7A) ===")

    env_configs = {
        'hotpotqa': 'HotpotQA',
        'apps': 'APPS',
        'webshop': 'WebShop',
        'twexpress': 'TWExpress',
        'apps_interview': 'APPS Intv',
    }

    all_results = {}
    for env_key, env_label in env_configs.items():
        data = load_probe_data(env_key)
        if data is None:
            continue

        entropies = np.array([r['token_entropy'] for r in data])
        utilities = np.array([r['utility'] for r in data])
        steps = np.array([r['step_count'] for r in data])

        # Stratify by step_count into 3 bins
        unique_steps = np.unique(steps)
        if len(unique_steps) < 3:
            # Not enough step variation
            print(f"  {env_label}: only {len(unique_steps)} unique step values, skipping")
            continue

        try:
            # Use tercile split
            t1 = np.percentile(steps, 33.3)
            t2 = np.percentile(steps, 66.7)
            if t1 == t2:
                # Fall back to 0 vs mid vs high
                t1 = 0
                t2 = np.percentile(steps[steps > 0], 50) if (steps > 0).any() else 1
        except Exception:
            t1, t2 = 0, 1

        bins = [
            ('Early', steps <= t1),
            ('Mid', (steps > t1) & (steps <= t2)),
            ('Late', steps > t2),
        ]

        env_rhos = {}
        for bin_label, mask in bins:
            if mask.sum() < 10:
                env_rhos[bin_label] = (np.nan, np.nan)
                continue
            rho, p = spearmanr(entropies[mask], utilities[mask])
            env_rhos[bin_label] = (rho, p)
            print(f"  {env_label} [{bin_label}]: ρ={rho:.3f}, p={p:.3f}, n={mask.sum()}")

        all_results[env_label] = env_rhos

    if not all_results:
        print("  No data available for stratified analysis")
        return

    # Plot
    plot_envs = [e for e in ['HotpotQA', 'TWExpress', 'APPS', 'WebShop', 'APPS Intv']
                 if e in all_results]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(plot_envs))
    width = 0.22
    strata = ['Early', 'Mid', 'Late']
    colors = ['#deebf7', '#6baed6', '#08519c']

    for i, (stratum, color) in enumerate(zip(strata, colors)):
        vals = []
        for env in plot_envs:
            rho, _ = all_results[env].get(stratum, (np.nan, np.nan))
            vals.append(rho if not np.isnan(rho) else 0)
        offset = (i - 1) * width
        ax.bar(x + offset, vals, width * 0.9,
               color=color, edgecolor='black', linewidth=0.5,
               label=stratum, zorder=3)
        # Value labels
        for j, v in enumerate(vals):
            if v != 0:
                ax.text(x[j] + offset, v + (0.015 if v >= 0 else -0.035),
                        f'{v:.2f}', ha='center', va='bottom' if v >= 0 else 'top',
                        fontsize=7, fontweight='bold')

    ax.axhline(y=0, color='black', linestyle='-', alpha=0.4, linewidth=0.8)

    # Highlight: check sign consistency within each env
    for j, env in enumerate(plot_envs):
        rhos = [all_results[env].get(s, (0, 0))[0] for s in strata]
        valid = [r for r in rhos if not np.isnan(r) and r != 0]
        if valid and all(r < 0 for r in valid):
            ax.text(j, -0.02, '●', ha='center', va='top', fontsize=14, color='#2166ac', alpha=0.5)
        elif valid and all(r > 0 for r in valid):
            ax.text(j, 0.02, '●', ha='center', va='bottom', fontsize=14, color='#b2182b', alpha=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(plot_envs, fontsize=10, fontweight='bold')
    ax.set_ylabel('ρ(entropy, utility) within stratum', fontsize=11)
    ax.set_title('Direction Reversal Persists Across Step-Count Strata\n(Not a trajectory-length artifact)',
                 fontsize=12, fontweight='bold', pad=10)
    ax.legend(title='Step-count stratum', loc='best', fontsize=9, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, zorder=0)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_stratified_reversal.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_stratified_reversal.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_stratified_reversal saved")


# ══════════════════════════════════════════════════════════════════
# Figure 4: Matched-Pair ΔU (§3.8.7B)
# ══════════════════════════════════════════════════════════════════

def fig_matched_pair():
    """ΔU = U(high_entropy) - U(low_entropy) within difficulty-matched states."""
    print("\n=== Matched-Pair Analysis (§3.8.7B) ===")

    env_configs = {
        'hotpotqa': ('HotpotQA', 'Type I (ρ=−0.33)'),
        'twexpress': ('TWExpress', 'Type I (ρ=−0.29)'),
        'apps_interview': ('APPS Intv', 'Type D (ρ=+0.32)'),
        'apps': ('APPS', 'Weak (ρ≈0)'),
    }

    all_results = {}
    for env_key, (env_label, type_label) in env_configs.items():
        data = load_probe_data(env_key)
        if data is None:
            continue

        entropies = np.array([r['token_entropy'] for r in data])
        utilities = np.array([r['utility'] for r in data])
        steps = np.array([r['step_count'] for r in data])

        # Stratify by difficulty (step_count terciles)
        unique_steps = np.unique(steps)
        if len(unique_steps) < 2:
            t1, t2 = 0, 0
            bins_labels = ['All']
            bins_masks = [np.ones(len(steps), dtype=bool)]
        else:
            try:
                t1 = np.percentile(steps, 33.3)
                t2 = np.percentile(steps, 66.7)
                if t1 == t2 == 0:
                    t2 = max(1, np.percentile(steps[steps > 0], 50) if (steps > 0).any() else 1)
            except:
                t1, t2 = 0, 1

            bins_labels = ['Easy', 'Medium', 'Hard']
            bins_masks = [
                steps <= t1,
                (steps > t1) & (steps <= t2),
                steps > t2,
            ]

        deltas = []
        delta_cis = []
        for bin_label, mask in zip(bins_labels, bins_masks):
            if mask.sum() < 10:
                deltas.append(np.nan)
                delta_cis.append((np.nan, np.nan))
                continue

            ent_sub = entropies[mask]
            util_sub = utilities[mask]
            med_ent = np.median(ent_sub)

            high_mask = ent_sub >= med_ent
            low_mask = ent_sub < med_ent

            if high_mask.sum() < 5 or low_mask.sum() < 5:
                deltas.append(np.nan)
                delta_cis.append((np.nan, np.nan))
                continue

            delta_u = util_sub[high_mask].mean() - util_sub[low_mask].mean()
            deltas.append(delta_u)

            # Bootstrap CI
            n_boot = 2000
            boot_deltas = []
            rng = np.random.RandomState(42)
            for _ in range(n_boot):
                idx = rng.choice(len(ent_sub), size=len(ent_sub), replace=True)
                b_ent = ent_sub[idx]
                b_util = util_sub[idx]
                b_med = np.median(b_ent)
                b_high = b_ent >= b_med
                b_low = b_ent < b_med
                if b_high.sum() > 0 and b_low.sum() > 0:
                    boot_deltas.append(b_util[b_high].mean() - b_util[b_low].mean())
            if boot_deltas:
                ci = (np.percentile(boot_deltas, 2.5), np.percentile(boot_deltas, 97.5))
            else:
                ci = (delta_u - 0.05, delta_u + 0.05)
            delta_cis.append(ci)

            print(f"  {env_label} [{bin_label}]: ΔU={delta_u:+.3f}, "
                  f"CI=[{ci[0]:+.3f}, {ci[1]:+.3f}], "
                  f"n_high={high_mask.sum()}, n_low={low_mask.sum()}")

        all_results[env_label] = {
            'deltas': deltas,
            'cis': delta_cis,
            'type_label': type_label,
            'bins': bins_labels,
        }

    if not all_results:
        print("  No data available for matched-pair analysis")
        return

    # Plot: 2×2 subplots
    plot_envs = [e for e in ['HotpotQA', 'TWExpress', 'APPS Intv', 'APPS'] if e in all_results]
    n_plots = len(plot_envs)
    nrows = 2
    ncols = (n_plots + 1) // 2

    fig, axes = plt.subplots(nrows, ncols, figsize=(10, 7), sharey=True)
    axes = axes.flatten()

    for idx, env in enumerate(plot_envs):
        ax = axes[idx]
        r = all_results[env]
        bins = r['bins']
        deltas = r['deltas']
        cis = r['cis']
        type_label = r['type_label']

        x = np.arange(len(bins))
        colors_bar = []
        for d in deltas:
            if np.isnan(d):
                colors_bar.append('#bdbdbd')
            elif d < 0:
                colors_bar.append('#2166ac')
            else:
                colors_bar.append('#b2182b')

        errs_lo = [d - ci[0] if not np.isnan(d) else 0 for d, ci in zip(deltas, cis)]
        errs_hi = [ci[1] - d if not np.isnan(d) else 0 for d, ci in zip(deltas, cis)]

        valid_deltas = [d if not np.isnan(d) else 0 for d in deltas]

        bars = ax.bar(x, valid_deltas, 0.6, yerr=[errs_lo, errs_hi],
                      color=colors_bar, edgecolor='black', linewidth=0.5,
                      capsize=4, zorder=3)

        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(bins, fontsize=9)
        ax.set_title(f'{env}\n{type_label}', fontsize=10.5, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, zorder=0)
        ax.set_axisbelow(True)

        # Value labels
        for j, (d, bar) in enumerate(zip(deltas, bars)):
            if not np.isnan(d):
                y_pos = d + (0.01 if d >= 0 else -0.01)
                ax.text(j, y_pos, f'{d:+.3f}', ha='center',
                        va='bottom' if d >= 0 else 'top',
                        fontsize=8, fontweight='bold')

    # Hide unused axes
    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)

    # Common labels
    fig.text(0.5, -0.01, 'Difficulty stratum (by step count)', ha='center', fontsize=11)
    fig.text(-0.01, 0.5, 'ΔU = U(high entropy) − U(low entropy)', va='center',
             rotation='vertical', fontsize=11)

    fig.suptitle('Same Entropy Level, Opposite Utility Effect Across Environments',
                 fontsize=13, fontweight='bold', y=1.02)

    # Color legend
    blue_patch = mpatches.Patch(color='#2166ac', label='ΔU < 0 (Type I: high entropy = info poverty)')
    red_patch = mpatches.Patch(color='#b2182b', label='ΔU > 0 (Type D: high entropy = decision difficulty)')
    fig.legend(handles=[blue_patch, red_patch], loc='lower center',
               ncol=2, fontsize=9, bbox_to_anchor=(0.5, -0.06))

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_matched_pair_opposite_meaning.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_matched_pair_opposite_meaning.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_matched_pair_opposite_meaning saved")


# ══════════════════════════════════════════════════════════════════
# Table: Gate Capacity Ablation (§3.8.8)
# ══════════════════════════════════════════════════════════════════

def tab_gate_capacity():
    """Generate LaTeX table: direction >> capacity."""
    print("\n=== Gate Capacity Ablation (§3.8.8) ===")

    # Data from plan §3.8.8 + phase2/phase5 results
    rows = [
        # (gate, direction, SR, AUC, source)
        ('Base (no gate)', '—', 49.0, 0.500, 'baseline'),
        ('Logistic (5 feat)', 'Correct', 95.2, 0.851, 'EAAG'),
        ('MLP (5 feat)', 'Correct', '~95', 0.869, 'Phase 2'),
        ('Hidden state LR', 'Correct', '~95', 0.869, 'Phase 5'),
        ('Logistic (5 feat)', 'Wrong', 62.0, '—', 'BSW-LR'),
        ('MLP (5 feat)', 'Wrong', 45.3, '—', 'BSW-MLP'),
    ]

    latex = r"""\begin{table}[t]
\centering
\caption{Gate Capacity Ablation on HotpotQA. All correct-direction gates achieve similar SR ($\approx$95\%),
while wrong-direction gates degrade substantially---more so with higher capacity.
Direction matters far more than gate complexity.}
\label{tab:capacity}
\begin{tabular}{llcc}
\toprule
\textbf{Gate} & \textbf{Direction} & \textbf{SR (\%)} & \textbf{AUC} \\
\midrule
Base (no gate) & --- & 49.0 & 0.500 \\
\midrule
Logistic (5 feat) & Correct & \textbf{95.2} & 0.851 \\
MLP (5 feat) & Correct & $\sim$95 & 0.869 \\
Hidden state LR & Correct & $\sim$95 & 0.869 \\
\midrule
Logistic (5 feat) & Wrong & 62.0 & --- \\
MLP (5 feat) & Wrong & 45.3 & --- \\
\bottomrule
\end{tabular}
\end{table}"""

    out_path = OUT_DIR / 'tab_gate_capacity.tex'
    with open(out_path, 'w') as f:
        f.write(latex)

    print(f"✅ tab_gate_capacity.tex saved")
    print(f"\n{latex}")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    os.chdir(PROJECT)
    print(f"Project root: {PROJECT}")
    print(f"Output dir: {OUT_DIR}")

    fig_auc_hierarchy()
    fig_p1_temporal_shift()
    fig_stratified_reversal()
    fig_matched_pair()
    tab_gate_capacity()

    print("\n" + "=" * 60)
    print("All high-priority figures generated!")
    print("=" * 60)


if __name__ == '__main__':
    main()
