#!/usr/bin/env python3
"""
Generate medium/low-priority paper figures for EAAG paper (v7.0 §3.8).

Figures:
  1. Gate Trigger Rate vs Step (§3.8.3) → fig_trigger_rate_by_step.pdf
  2. BSW Cost vs |ρ| (§3.8.4) → fig_bsw_cost_vs_rho.pdf
  3. Method Classification Table (§3.8.5) → tab_method_classification.tex
  4. Information Coverage Proxy (§3.8.9) → fig_coverage_vs_rho.pdf
  5. Statistical Significance Table (§3.8.10) → tab_significance.tex
  6. Environment Info Structure Table (§3.8.6) → tab_env_info_structure.tex
"""
import json
import os
import glob
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

OUT_DIR = Path(__file__).parent
PROJECT = Path(__file__).parent.parent.parent

plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
})


# ══════════════════════════════════════════════════════════════════
# Figure: Gate Trigger Rate vs Step (§3.8.3)
# ══════════════════════════════════════════════════════════════════

def get_trigger_by_step(env, seeds=[123, 42, 456]):
    """Reconstruct per-step trigger rate from decision_log + episodes."""
    trigger_by_step = defaultdict(list)
    for seed in seeds:
        dl_path = PROJECT / f'results/phase6/path_e/{env}/se_online_decay_local/seed_{seed}/scg_se_online_decay_local_decision_log.json'
        ep_path = PROJECT / f'results/phase6/path_e/{env}/se_online_decay_local/seed_{seed}/episodes.json'
        if not dl_path.exists() or not ep_path.exists():
            continue
        dl = json.load(open(dl_path))
        eps = json.load(open(ep_path))
        exploit_dl = [r for r in dl if r['phase'] == 'exploitation']
        exploit_eps = [e for e in eps if e.get('gate_phase') == 'exploitation']

        step_counts = []
        for e in exploit_eps:
            for s in range(e['steps']):
                step_counts.append(s)

        n = min(len(step_counts), len(exploit_dl))
        for i in range(n):
            triggered = 1 if exploit_dl[i]['decision'] == 'rollout' else 0
            trigger_by_step[step_counts[i]].append(triggered)
    return trigger_by_step


def fig_trigger_rate_by_step():
    """2×3 grid: trigger probability vs step for 6 environments."""
    print("\n=== Gate Trigger Rate vs Step (§3.8.3) ===")

    envs = ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft']
    titles = ['HotpotQA', 'APPS (Intro)', 'WebShop', 'FEVER', 'TWExpress', 'Plancraft']

    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    axes = axes.flatten()

    for idx, (env, title) in enumerate(zip(envs, titles)):
        ax = axes[idx]
        tbs = get_trigger_by_step(env)
        if not tbs:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontweight='bold')
            continue

        # Filter to steps with enough data
        steps = sorted(s for s in tbs if len(tbs[s]) >= 5)
        if not steps:
            ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title, fontweight='bold')
            continue

        rates = [np.mean(tbs[s]) for s in steps]
        ns = [len(tbs[s]) for s in steps]
        # Binomial 95% CI
        ci_lo = [max(0, r - 1.96 * np.sqrt(r * (1 - r) / n)) for r, n in zip(rates, ns)]
        ci_hi = [min(1, r + 1.96 * np.sqrt(r * (1 - r) / n)) for r, n in zip(rates, ns)]

        ax.fill_between(steps, ci_lo, ci_hi, color='#2166ac', alpha=0.15, zorder=1)
        ax.plot(steps, rates, 'o-', color='#2166ac', linewidth=2,
                markersize=5, markeredgecolor='black', markeredgewidth=0.5, zorder=3)

        # Overall trigger rate line
        overall = sum(sum(tbs[s]) for s in steps) / sum(len(tbs[s]) for s in steps)
        ax.axhline(y=overall, color='gray', linestyle='--', alpha=0.6, linewidth=1,
                   label=f'Overall RR={overall:.2f}')

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('Step in episode')
        ax.set_ylabel('Trigger rate')
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlim(-0.5, max(steps) + 0.5)
        ax.legend(fontsize=8, loc='best')
        ax.grid(alpha=0.3, zorder=0)
        ax.set_axisbelow(True)

        # Annotate n per step
        for s, n in zip(steps, ns):
            if s <= 5 or s == steps[-1]:
                ax.annotate(f'n={n}', (s, rates[steps.index(s)]),
                           textcoords='offset points', xytext=(0, -12),
                           fontsize=6, ha='center', color='gray')

    fig.suptitle('EAAG Gate Trigger Rate by Step (Exploitation Phase)',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_trigger_rate_by_step.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_trigger_rate_by_step.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_trigger_rate_by_step saved")


# ══════════════════════════════════════════════════════════════════
# Figure: BSW Cost vs |ρ| (§3.8.4)
# ══════════════════════════════════════════════════════════════════

def fig_bsw_cost_vs_rho():
    """Scatter + regression: |ρ| vs BSW degradation."""
    print("\n=== BSW Cost vs |ρ| (§3.8.4) ===")

    # Data from plan §3.8.4
    data = [
        # (env, |ρ|, BSW_SR, always_SR, rollout_safe)
        ('FEVER',       0.619, 0.630, 0.998, False),
        ('HotpotQA',    0.494, 0.582, 0.970, False),
        ('WebShop',     0.444, 0.206, 0.430, False),
        ('APPS Intv',   0.339, 0.795, 0.795, True),
        ('CRUXEval',    0.184, 0.875, 0.995, False),
    ]

    fig, ax = plt.subplots(figsize=(7, 5))

    # Non-safe envs for regression
    xs_reg, ys_reg = [], []
    for env, rho, bsw, always, safe in data:
        degradation = (always - bsw) * 100
        marker = 'o' if not safe else 'D'
        facecolor = '#d62728' if not safe else 'white'
        ax.scatter(rho, degradation, s=120, c=facecolor, marker=marker,
                   edgecolors='black', linewidths=1.5, zorder=5)
        # Label positioning
        offsets = {
            'FEVER': (0.02, 2), 'HotpotQA': (0.02, -5),
            'WebShop': (0.02, 2), 'CRUXEval': (0.02, 2),
            'APPS Intv': (0.02, -5),
        }
        ox, oy = offsets.get(env, (0.02, 2))
        label = f'{env}\n(rollout-safe)' if safe else env
        ax.annotate(label, (rho, degradation),
                   xytext=(rho + ox, degradation + oy),
                   fontsize=9, ha='left')
        if not safe:
            xs_reg.append(rho)
            ys_reg.append(degradation)

    # Regression line
    from scipy.stats import pearsonr
    r, p = pearsonr(xs_reg, ys_reg)
    z = np.polyfit(xs_reg, ys_reg, 1)
    poly = np.poly1d(z)
    x_line = np.linspace(0.1, 0.7, 100)
    ax.plot(x_line, poly(x_line), '--', color='gray', alpha=0.6,
            label=f'Linear fit (r={r:.2f}, p={p:.3f})', zorder=2)

    # R² annotation
    r2 = r ** 2
    ax.text(0.65, 5, f'R²={r2:.2f}', fontsize=10, fontweight='bold', color='gray')

    ax.set_xlabel('Signal Strength |ρ|', fontsize=11)
    ax.set_ylabel('BSW Degradation (pp vs always_trigger)', fontsize=11)
    ax.set_title('Stronger Signals → Higher Wrong-Direction Penalty',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(alpha=0.3)
    ax.set_xlim(0.1, 0.75)
    ax.set_ylim(-5, 45)

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_bsw_cost_vs_rho.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_bsw_cost_vs_rho.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_bsw_cost_vs_rho saved")


# ══════════════════════════════════════════════════════════════════
# Table: Method Classification (§3.8.5)
# ══════════════════════════════════════════════════════════════════

def tab_method_classification():
    """FLARE Table 5 style: classify all methods by 4 dimensions."""
    print("\n=== Method Classification Table (§3.8.5) ===")

    latex = r"""\begin{table}[t]
\centering
\caption{Method classification by signal type, direction handling, calibration phase, and performance.
$\dagger$ denotes methods requiring Phase~1 (200 ep always\_trigger) calibration data, with amortized cost included in Total Cost.
EAAG is the only method that automatically discovers both signal identity and direction without Phase~1 data.}
\label{tab:method_classification}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lcccccc}
\toprule
\textbf{Method} & \textbf{Signal Type} & \textbf{Direction} & \textbf{Phase 1?} & \textbf{Extra Cost} & \textbf{SR W/L} & \textbf{Pareto dom.} \\
\midrule
\multicolumn{7}{l}{\textit{Bounds}} \\
base\_only     & ---            & ---   & ---    & 0          & ---     & ---     \\
always\_trigger & ---           & ---   & ---    & 0          & ---     & ---     \\
oracle         & ---            & ---   & ---    & 0          & ---     & ---     \\
\midrule
\multicolumn{7}{l}{\textit{Fixed-direction CB}} \\
CaTS$\dagger$    & entropy      & Fixed & \cmark & 0          & 0W/5L   & 0/6     \\
SEAG$\dagger$    & entropy      & Fixed & \cmark & 0          & 0W/6L   & 0/6     \\
CoRefine$\dagger$ & entropy     & Fixed & \cmark & 0          & 0W/5L   & 0/6     \\
CATTS          & entropy        & Fixed & \xmark & $K$=5 calls & 0W/6L   & 0/6     \\
\midrule
\multicolumn{7}{l}{\textit{Budget-based CB}} \\
AUQ            & confidence     & None  & \xmark & 1 call/step & 1W/6L   & ---     \\
s1 Budget      & length         & None  & \xmark & 0          & 1W/6L   & ---     \\
\midrule
\multicolumn{7}{l}{\textit{Ablation}} \\
SCG$\dagger$     & multi-signal & Learned & \cmark & 0        & ---     & 4/7 lost \\
BSW$\dagger$     & multi-signal & Flipped & \cmark & 0        & ---     & ---     \\
\midrule
\multicolumn{7}{l}{\textit{Ours}} \\
\textbf{EAAG}  & \textbf{multi-signal} & \textbf{Auto-learned} & \xmark & \textbf{0} & \textbf{34W/2L} & \textbf{---} \\
\bottomrule
\end{tabular}%
}
\end{table}"""

    out_path = OUT_DIR / 'tab_method_classification.tex'
    with open(out_path, 'w') as f:
        f.write(latex)
    print(f"✅ tab_method_classification.tex saved")


# ══════════════════════════════════════════════════════════════════
# Figure: Information Coverage Proxy (§3.8.9)
# ══════════════════════════════════════════════════════════════════

def load_probe_data(env):
    """Load per-step probe data."""
    candidates = [
        PROJECT / f"results/phase1_signal_discovery/{env}/phase1_signal_data.json",
        PROJECT / f"results/phase6/{env}/{env}/phase1_signal_data.json",
        PROJECT / f"results/phase5/twexpress/twexpress/phase1_signal_data.json" if env == 'twexpress' else None,
        PROJECT / f"results/phase5/calibration_data/{env}/phase1_signal_data.json",
    ]
    for path in candidates:
        if path and path.exists():
            return json.load(open(path))
    return None


def fig_coverage_vs_rho():
    """Scatter: mean information coverage vs ρ(entropy, U)."""
    print("\n=== Information Coverage Proxy (§3.8.9) ===")

    # Coverage proxy definitions from plan §3.8.9
    env_data = {
        # (env_key, label, coverage_field_or_proxy, max_value, entropy_rho)
        'hotpotqa':       ('HotpotQA',     'evidence_count', 3.0),
        'fever':          ('FEVER',         'step_count',     7.0),
        'apps':           ('APPS',          None,             None),  # always 1.0
        'webshop':        ('WebShop',       'num_available_actions', 30.0),
        'twexpress':      ('TWExpress',     'step_count',     9.0),
        'apps_interview': ('APPS Intv',     None,             None),  # always 1.0
    }

    results = []
    for env_key, (label, cov_field, max_val) in env_data.items():
        data = load_probe_data(env_key)
        if data is None:
            print(f"  {label}: no data")
            continue

        entropies = np.array([r['token_entropy'] for r in data])
        utilities = np.array([r['utility'] for r in data])
        rho, p = spearmanr(entropies, utilities)

        if cov_field is None:
            # Code environments: info is self-contained
            mean_cov = 1.0
        else:
            cov_vals = np.array([r.get(cov_field, 0) for r in data])
            mean_cov = np.mean(cov_vals / max_val) if max_val > 0 else 0

        results.append((label, mean_cov, rho, len(data)))
        print(f"  {label}: mean_coverage={mean_cov:.3f}, ρ(entropy,U)={rho:.3f}, n={len(data)}")

    if not results:
        print("  No data for coverage analysis")
        return

    fig, ax = plt.subplots(figsize=(7, 5))

    labels, covs, rhos, ns = zip(*results)
    colors = ['#2166ac' if r < -0.1 else '#b2182b' if r > 0.1 else '#636363' for r in rhos]

    for label, cov, rho, n, color in zip(labels, covs, rhos, ns, colors):
        ax.scatter(cov, rho, s=max(80, n / 5), c=color, edgecolors='black',
                   linewidths=1, zorder=5)
        ax.annotate(label, (cov, rho), xytext=(5, 5),
                    textcoords='offset points', fontsize=9, fontweight='bold')

    # Regression (exclude constant-coverage envs for cleaner fit)
    non_const = [(c, r) for l, c, r, _ in results if c < 0.95]
    if len(non_const) >= 3:
        from scipy.stats import pearsonr
        xr = [x[0] for x in non_const]
        yr = [x[1] for x in non_const]
        r_val, p_val = pearsonr(xr, yr)
        z = np.polyfit(xr, yr, 1)
        poly = np.poly1d(z)
        x_line = np.linspace(min(xr) - 0.05, max(xr) + 0.05, 100)
        ax.plot(x_line, poly(x_line), '--', color='gray', alpha=0.5,
                label=f'Trend (r={r_val:.2f})')
        ax.legend(fontsize=9)

    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=0.8)
    ax.set_xlabel('Mean Information Coverage (proxy)', fontsize=11)
    ax.set_ylabel('ρ(entropy, utility)', fontsize=11)
    ax.set_title('Information Coverage Predicts Entropy-Utility Direction',
                 fontsize=12, fontweight='bold')
    ax.grid(alpha=0.3)

    # Annotation: low coverage = Type I (negative ρ), high coverage = Type D
    ax.text(0.02, 0.02, '← Info-Poor (Type I)', transform=ax.transAxes,
            fontsize=8, color='#2166ac', style='italic')
    ax.text(0.98, 0.98, 'Info-Rich (Type D) →', transform=ax.transAxes,
            fontsize=8, color='#b2182b', style='italic', ha='right', va='top')

    plt.tight_layout()
    plt.savefig(OUT_DIR / 'fig_coverage_vs_rho.png', dpi=200, bbox_inches='tight')
    plt.savefig(OUT_DIR / 'fig_coverage_vs_rho.pdf', bbox_inches='tight')
    plt.close()
    print("✅ fig_coverage_vs_rho saved")


# ══════════════════════════════════════════════════════════════════
# Table: Statistical Significance (§3.8.10)
# ══════════════════════════════════════════════════════════════════

def tab_significance():
    """McNemar-like test + bootstrap CI for EAAG vs each CB."""
    print("\n=== Statistical Significance (§3.8.10) ===")

    cb_methods = {
        'cats': 'CaTS',
        'seag': 'SEAG',
        'corefine': 'CoRefine',
        'catts': 'CATTS',
        'auq': 'AUQ',
        's1_budget': 's1',
    }
    envs = ['hotpotqa', 'apps', 'webshop', 'twexpress', 'plancraft']
    env_labels = {'hotpotqa': 'HotpotQA', 'apps': 'APPS', 'webshop': 'WebShop',
                  'twexpress': 'TWExpress', 'plancraft': 'Plancraft'}

    def load_episodes(env, method):
        """Load episodes across seeds, return success array."""
        patterns = [
            f'results/phase6/path_e/{env}/{method}/seed_*/episodes.json',
            f'results/phase5/competing_baselines/{env}/{method}/seed_*/episodes.json',
            f'results/phase5/competing_baselines_calibrated/{env}/{method}/seed_*/episodes.json',
            f'results/phase6/new_baselines/{env}/{method}/seed_*/episodes.json',
        ]
        all_success = []
        seen_seeds = set()
        for pattern in patterns:
            for f in sorted(glob.glob(str(PROJECT / pattern))):
                seed = f.split('seed_')[1].split('/')[0]
                if seed in seen_seeds:
                    continue
                seen_seeds.add(seed)
                eps = json.load(open(f))
                for e in eps:
                    all_success.append(1 if e.get('success') else 0)
        return np.array(all_success) if all_success else None

    rows = []
    for env in envs:
        eaag = load_episodes(env, 'se_online_decay_local')
        if eaag is None:
            continue
        eaag_sr = eaag.mean()

        for cb_key, cb_label in cb_methods.items():
            cb = load_episodes(env, cb_key)
            if cb is None:
                continue
            cb_sr = cb.mean()
            delta_sr = (eaag_sr - cb_sr) * 100

            # Bootstrap CI for ΔSR
            n_boot = 5000
            rng = np.random.RandomState(42)
            n_eaag = len(eaag)
            n_cb = len(cb)
            boot_deltas = []
            for _ in range(n_boot):
                b_eaag = rng.choice(eaag, size=n_eaag, replace=True)
                b_cb = rng.choice(cb, size=n_cb, replace=True)
                boot_deltas.append((b_eaag.mean() - b_cb.mean()) * 100)
            ci_lo = np.percentile(boot_deltas, 2.5)
            ci_hi = np.percentile(boot_deltas, 97.5)

            # Significance: CI doesn't contain 0
            sig = ci_lo > 0 or ci_hi < 0

            rows.append({
                'env': env_labels[env],
                'cb': cb_label,
                'delta': delta_sr,
                'ci_lo': ci_lo,
                'ci_hi': ci_hi,
                'sig': sig,
                'n_eaag': n_eaag,
                'n_cb': n_cb,
            })
            print(f"  {env_labels[env]} EAAG vs {cb_label}: ΔSR={delta_sr:+.1f}pp "
                  f"[{ci_lo:+.1f}, {ci_hi:+.1f}] {'✅' if sig else '—'}")

    # Generate LaTeX
    latex_rows = []
    for r in rows:
        sig_mark = r'$\checkmark$' if r['sig'] else '---'
        ci_str = f"[{r['ci_lo']:+.1f}, {r['ci_hi']:+.1f}]"
        latex_rows.append(
            f"  {r['env']} & {r['cb']} & {r['delta']:+.1f} & {ci_str} & {sig_mark} \\\\"
        )

    latex = r"""\begin{table}[t]
\centering
\caption{Statistical significance of EAAG vs each CB method. $\Delta$SR is EAAG $-$ CB in percentage points.
95\% CI computed via bootstrap (5000 resamples). Significant when CI excludes zero.}
\label{tab:significance}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{llrcc}
\toprule
\textbf{Environment} & \textbf{CB} & \textbf{$\Delta$SR (pp)} & \textbf{95\% CI} & \textbf{Sig.?} \\
\midrule
""" + "\n".join(latex_rows) + r"""
\bottomrule
\end{tabular}%
}
\end{table}"""

    out_path = OUT_DIR / 'tab_significance.tex'
    with open(out_path, 'w') as f:
        f.write(latex)
    print(f"✅ tab_significance.tex saved")


# ══════════════════════════════════════════════════════════════════
# Table: Environment Info Structure (§3.8.6)
# ══════════════════════════════════════════════════════════════════

def tab_env_info_structure():
    """8 env × 3 dims classification table."""
    print("\n=== Environment Info Structure Table (§3.8.6) ===")

    latex = r"""\begin{table}[t]
\centering
\caption{Environment information structure classification. Info-Sufficiency captures whether the agent
has enough information at each step; Reversibility indicates whether actions can be undone;
Feedback-Delay captures when the agent learns if its action succeeded.
The Two-Source type and $\rho$(entropy, U) are consistent with the predicted mapping.}
\label{tab:env_info_structure}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{lccccc}
\toprule
\textbf{Environment} & \textbf{Info-Suff.} & \textbf{Reversibility} & \textbf{Feedback} & \textbf{Two-Source} & $\bm{\rho}$\textbf{(ent, U)} \\
\midrule
HotpotQA      & Info-Poor & Irreversible & Immediate & Info-Poverty & $-0.041$ \\
FEVER         & Info-Poor & Irreversible & Immediate & Info-Poverty & $-0.119$ \\
APPS Intro    & Info-Rich & Irreversible & Delayed   & Decision-Diff & $+0.012$ \\
APPS Intv     & Info-Rich & Irreversible & Delayed   & Decision-Diff & $+0.317$ \\
WebShop       & Mixed     & Reversible   & Immediate & Mixed        & $-0.019$ \\
TWExpress     & Info-Poor & Irreversible & Immediate & Info-Poverty & $-0.290$ \\
Plancraft     & Info-Rich & Irreversible & Delayed   & Weak (harmful) & $-0.016$ \\
CRUXEval      & Info-Rich & Irreversible & Delayed   & Weak         & $-0.048$ \\
\bottomrule
\end{tabular}%
}
\end{table}"""

    out_path = OUT_DIR / 'tab_env_info_structure.tex'
    with open(out_path, 'w') as f:
        f.write(latex)
    print(f"✅ tab_env_info_structure.tex saved")


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    os.chdir(PROJECT)
    print(f"Project root: {PROJECT}")
    print(f"Output dir: {OUT_DIR}")

    fig_trigger_rate_by_step()
    fig_bsw_cost_vs_rho()
    tab_method_classification()
    fig_coverage_vs_rho()
    tab_significance()
    tab_env_info_structure()

    print("\n" + "=" * 60)
    print("All medium-priority figures generated!")
    print("=" * 60)


if __name__ == '__main__':
    main()
