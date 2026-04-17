#!/usr/bin/env python3
"""
Generate CSV data files for all experiment folders.
Run: conda activate frvc && python planning/experiment/generate_all_csvs.py
"""
import csv
import json
import os
import glob
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr

PROJECT = Path(__file__).parent.parent.parent
EXP = PROJECT / "planning" / "experiment"
os.chdir(PROJECT)


def write_csv(folder, filename, headers, rows):
    path = EXP / folder / filename
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  {folder}/{filename}: {len(rows)} rows")


def load_probe(env):
    candidates = [
        f"results/phase1_signal_discovery/{env}/phase1_signal_data.json",
        f"results/phase6/{env}/{env}/phase1_signal_data.json",
        f"results/phase5/twexpress/twexpress/phase1_signal_data.json" if env == "twexpress" else None,
        f"results/phase5/calibration_data/{env}/phase1_signal_data.json",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return json.load(open(c))
    return None


# ── 1. fig1_signal_heatmap ──
def csv_fig1():
    envs = ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft', 'apps_interview', 'cruxeval']
    env_labels = {'hotpotqa': 'HotpotQA', 'apps': 'APPS', 'webshop': 'WebShop', 'fever': 'FEVER',
                  'twexpress': 'TWExpress', 'plancraft': 'Plancraft', 'apps_interview': 'APPS Intv', 'cruxeval': 'CRUXEval'}
    rows = []
    for env in envs:
        for pat in [f"results/phase6/{env}/{env}/step1_signal_discovery.json"]:
            if os.path.exists(pat):
                d = json.load(open(pat))
                corrs = d.get("correlations", {})
                for sig, info in corrs.items():
                    if isinstance(info, dict) and "spearman_rho" in info:
                        rows.append([env_labels.get(env, env), sig, f"{info['spearman_rho']:.4f}"])
        # Also from probe data
        data = load_probe(env)
        if data and not any(r[0] == env_labels.get(env, env) for r in rows):
            ent = np.array([r['token_entropy'] for r in data])
            util = np.array([r['utility'] for r in data])
            sc = np.array([r['step_count'] for r in data])
            rho_ent, _ = spearmanr(ent, util)
            rho_sc, _ = spearmanr(sc, util)
            rows.append([env_labels.get(env, env), "token_entropy", f"{rho_ent:.4f}"])
            rows.append([env_labels.get(env, env), "step_count", f"{rho_sc:.4f}"])
    write_csv("fig1_signal_heatmap", "data.csv", ["environment", "signal", "spearman_rho"], rows)


# ── 2. fig2_pareto ──
def csv_fig2():
    rows = []
    patterns = [
        "results/phase6/path_e/{env}/*/seed_*/summary.json",
        "results/phase5/competing_baselines/{env}/*/seed_*/summary.json",
        "results/phase5/competing_baselines_calibrated/{env}/*/seed_*/summary.json",
        "results/phase6/new_baselines/{env}/*/seed_*/summary.json",
    ]
    for env in ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft']:
        method_data = defaultdict(list)
        for pat in patterns:
            for f in glob.glob(pat.format(env=env)):
                try:
                    d = json.load(open(f))
                    method = f.split("/")[-3]
                    sr = d.get("success_rate", d.get("overall_stats", {}).get("success_rate"))
                    ro = d.get("avg_rollouts_per_ep", d.get("overall_stats", {}).get("avg_rollouts_per_ep", 0))
                    if sr is not None:
                        method_data[method].append((float(sr), float(ro) if ro else 0.0))
                except Exception:
                    pass
        for method, vals in method_data.items():
            avg_sr = np.mean([v[0] for v in vals])
            avg_ro = np.mean([v[1] for v in vals])
            rows.append([env, method, f"{avg_sr:.4f}", f"{avg_ro:.4f}"])
    write_csv("fig2_pareto", "data.csv", ["environment", "method", "success_rate", "avg_rollouts_per_ep"], rows)


# ── 3. fig3_bsw_direction ──
def csv_fig3():
    data = [
        ["FEVER", 0.619, 0.630, 0.998, "No"],
        ["HotpotQA", 0.494, 0.582, 0.970, "No"],
        ["WebShop", 0.444, 0.206, 0.430, "No"],
        ["APPS Intv", 0.339, 0.795, 0.795, "Yes"],
        ["CRUXEval", 0.184, 0.875, 0.995, "No"],
    ]
    rows = [[d[0], d[1], d[2], d[3], (d[3] - d[2]) * 100, d[4]] for d in data]
    write_csv("fig3_bsw_direction", "data.csv",
              ["environment", "abs_rho", "bsw_sr", "always_sr", "degradation_pp", "rollout_safe"], rows)


# ── 4. fig4_feature_heatmap ──
def csv_fig4():
    env_features = {
        'HotpotQA': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                     'evidence_count', 'is_finish', 'state_length', 'num_numbers', 'llm_query_length'],
        'APPS': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                 'state_length', 'num_numbers', 'has_error', 'h_pca_9', 'llm_action_type'],
        'WebShop': ['num_available_actions', 'num_numbers', 'state_length', 'step_x_entropy',
                    'token_entropy', 'is_finish', 'llm_price_mentioned', 'llm_action_is_click',
                    'llm_step_early', 'llm_instruction_keyword_count'],
        'FEVER': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                  'state_length', 'h_pca_1', 'h_pca_9', 'llm_text_length_normalized', 'llm_has_claim'],
        'TWExpress': ['step_count', 'step_ratio', 'token_entropy', 'entropy_sq', 'state_length',
                      'num_numbers', 'llm_text_length', 'llm_closed_ratio', 'llm_action_look_around', 'llm_already_open'],
        'Plancraft': ['step_count', 'step_ratio', 'step_x_entropy', 'token_entropy', 'entropy_sq',
                      'state_length', 'num_numbers', 'num_available_actions', 'h_pca_0', 'h_pca_10'],
        'APPS Intv': ['step_count', 'step_ratio', 'has_error'],
    }
    all_feats = sorted(set(f for feats in env_features.values() for f in feats))
    rows = []
    for env, feats in env_features.items():
        for f in all_feats:
            rows.append([env, f, 1 if f in feats else 0])
    write_csv("fig4_feature_heatmap", "data.csv", ["environment", "feature", "selected"], rows)


# ── 5. fig5_llm_ablation ──
def csv_fig5():
    data = [
        ["WebShop", 43.8, 43.7], ["TWExpress", 99.0, 99.2], ["APPS", 66.0, 65.8],
        ["HotpotQA", 95.2, 95.8], ["FEVER", 49.8, 40.7],
    ]
    rows = [[d[0], d[1], d[2], d[1] - d[2]] for d in data]
    write_csv("fig5_llm_ablation", "data.csv",
              ["environment", "dial_sr", "v2_no_llm_sr", "llm_contribution_pp"], rows)


# ── 6. fig6_fever_bias ──
def csv_fig6():
    rows = [
        ["positive_rate", 51.8, 7.5],
        ["episode_length_steps", 1.4, 5.0],
        ["steps_observed", 282, 1054],
        ["rollout_rate_exploit", 68.2, 3.0],
    ]
    write_csv("fig6_fever_bias", "data.csv", ["metric", "scg_phase1", "dial_explore"], rows)


# ── 7. fig_auc_hierarchy ──
def csv_fig_auc():
    rows = [
        ["HotpotQA", "single_entropy", 0.502],
        ["HotpotQA", "best_single", 0.782],
        ["HotpotQA", "multi_signal_lr", 0.851],
        ["HotpotQA", "hidden_state_lr", 0.869],
        ["APPS", "single_entropy", 0.557],
        ["APPS", "best_single", 0.778],
        ["APPS", "multi_signal_lr", 0.761],
        ["APPS", "hidden_state_lr", 0.794],
        ["WebShop", "single_entropy", 0.502],
        ["WebShop", "best_single", 0.895],
        ["WebShop", "multi_signal_lr", 0.924],
        ["WebShop", "hidden_state_lr", 0.994],
    ]
    write_csv("fig_auc_hierarchy", "data.csv", ["environment", "signal_level", "auc"], rows)


# ── 8. fig_p1_temporal_shift ──
def csv_fig_p1():
    rows = []
    # Pre-computed
    ts = json.load(open("results/phase6/toy_model/d1_temporal_shift_results.json"))
    for r in ts:
        rows.append([r["env"], "early", f"{r['early']['rho']:.4f}",
                     f"{r['early'].get('ci_lo', '')}", f"{r['early'].get('ci_hi', '')}",
                     r["early"]["n"], f"{r['early']['p_value']:.6f}"])
        rows.append([r["env"], "late", f"{r['late']['rho']:.4f}",
                     f"{r['late'].get('ci_lo', '')}", f"{r['late'].get('ci_hi', '')}",
                     r["late"]["n"], f"{r['late']['p_value']:.6f}"])
    # Extra envs from probe
    for env_key, env_label in [("fever", "FEVER"), ("twexpress", "TWExpress")]:
        data = load_probe(env_key)
        if not data:
            continue
        ent = np.array([r['token_entropy'] for r in data])
        util = np.array([r['utility'] for r in data])
        steps = np.array([r['step_count'] for r in data])
        med = np.median(steps)
        if med == 0:
            early_m, late_m = steps == 0, steps > 0
        else:
            early_m, late_m = steps <= med, steps > med
        if early_m.sum() >= 10 and late_m.sum() >= 10:
            re, pe = spearmanr(ent[early_m], util[early_m])
            rl, pl = spearmanr(ent[late_m], util[late_m])
            rows.append([env_label, "early", f"{re:.4f}", "", "", int(early_m.sum()), f"{pe:.6f}"])
            rows.append([env_label, "late", f"{rl:.4f}", "", "", int(late_m.sum()), f"{pl:.6f}"])
    write_csv("fig_p1_temporal_shift", "data.csv",
              ["environment", "phase", "rho", "ci_lo", "ci_hi", "n", "p_value"], rows)


# ── 9. fig_trigger_rate ──
def csv_fig_trigger():
    rows = []
    for env in ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft']:
        trigger_by_step = defaultdict(list)
        for seed in [123, 42, 456]:
            dl_p = f"results/phase6/path_e/{env}/se_online_decay_local/seed_{seed}/scg_se_online_decay_local_decision_log.json"
            ep_p = f"results/phase6/path_e/{env}/se_online_decay_local/seed_{seed}/episodes.json"
            if not os.path.exists(dl_p) or not os.path.exists(ep_p):
                continue
            dl = json.load(open(dl_p))
            eps = json.load(open(ep_p))
            exploit_dl = [r for r in dl if r['phase'] == 'exploitation']
            exploit_eps = [e for e in eps if e.get('gate_phase') == 'exploitation']
            sc = []
            for e in exploit_eps:
                for s in range(e['steps']):
                    sc.append(s)
            n = min(len(sc), len(exploit_dl))
            for i in range(n):
                trigger_by_step[sc[i]].append(1 if exploit_dl[i]['decision'] == 'rollout' else 0)
        for s in sorted(trigger_by_step.keys()):
            vals = trigger_by_step[s]
            if len(vals) >= 5:
                rows.append([env, s, f"{np.mean(vals):.4f}", len(vals)])
    write_csv("fig_trigger_rate", "data.csv", ["environment", "step", "trigger_rate", "n"], rows)


# ── 10. fig_bsw_vs_rho ──
def csv_fig_bsw_rho():
    # Same data as fig3 but different focus
    data = [
        ["FEVER", 0.619, 36.8, "No"],
        ["HotpotQA", 0.494, 38.8, "No"],
        ["WebShop", 0.444, 22.4, "No"],
        ["APPS Intv", 0.339, 0.0, "Yes"],
        ["CRUXEval", 0.184, 12.0, "No"],
    ]
    write_csv("fig_bsw_vs_rho", "data.csv",
              ["environment", "abs_rho", "degradation_pp", "rollout_safe"], data)


# ── 11. fig_stratified_reversal ──
def csv_fig_stratified():
    rows = []
    for env_key, env_label in [('hotpotqa', 'HotpotQA'), ('apps', 'APPS'), ('webshop', 'WebShop'),
                                ('twexpress', 'TWExpress'), ('apps_interview', 'APPS Intv')]:
        data = load_probe(env_key)
        if not data:
            continue
        ent = np.array([r['token_entropy'] for r in data])
        util = np.array([r['utility'] for r in data])
        steps = np.array([r['step_count'] for r in data])
        t1 = np.percentile(steps, 33.3)
        t2 = np.percentile(steps, 66.7)
        if t1 == t2:
            t1 = 0
            t2 = max(1, np.percentile(steps[steps > 0], 50) if (steps > 0).any() else 1)
        for label, mask in [("Early", steps <= t1), ("Mid", (steps > t1) & (steps <= t2)), ("Late", steps > t2)]:
            if mask.sum() >= 10:
                try:
                    rho, p = spearmanr(ent[mask], util[mask])
                    rows.append([env_label, label, f"{rho:.4f}", f"{p:.6f}", int(mask.sum())])
                except Exception:
                    pass
    write_csv("fig_stratified_reversal", "data.csv",
              ["environment", "stratum", "rho", "p_value", "n"], rows)


# ── 12. fig_matched_pair ──
def csv_fig_matched():
    rows = []
    for env_key, env_label in [('hotpotqa', 'HotpotQA'), ('twexpress', 'TWExpress'),
                                ('apps_interview', 'APPS Intv'), ('apps', 'APPS')]:
        data = load_probe(env_key)
        if not data:
            continue
        ent = np.array([r['token_entropy'] for r in data])
        util = np.array([r['utility'] for r in data])
        steps = np.array([r['step_count'] for r in data])
        t1 = np.percentile(steps, 33.3)
        t2 = np.percentile(steps, 66.7)
        if t1 == t2 == 0:
            t2 = max(1, np.percentile(steps[steps > 0], 50) if (steps > 0).any() else 1)
        for label, mask in [("Easy", steps <= t1), ("Medium", (steps > t1) & (steps <= t2)), ("Hard", steps > t2)]:
            if mask.sum() < 10:
                continue
            e_sub, u_sub = ent[mask], util[mask]
            med = np.median(e_sub)
            high, low = e_sub >= med, e_sub < med
            if high.sum() > 0 and low.sum() > 0:
                delta = u_sub[high].mean() - u_sub[low].mean()
                rows.append([env_label, label, f"{delta:.4f}", int(high.sum()), int(low.sum())])
    write_csv("fig_matched_pair", "data.csv",
              ["environment", "difficulty_bin", "delta_u", "n_high_entropy", "n_low_entropy"], rows)


# ── 13. fig_coverage_proxy ──
def csv_fig_coverage():
    env_cfg = {
        'hotpotqa': ('HotpotQA', 'evidence_count', 3.0),
        'fever': ('FEVER', 'step_count', 7.0),
        'apps': ('APPS', None, None),
        'webshop': ('WebShop', 'num_available_actions', 30.0),
        'twexpress': ('TWExpress', 'step_count', 9.0),
        'apps_interview': ('APPS Intv', None, None),
    }
    rows = []
    for env_key, (label, field, maxv) in env_cfg.items():
        data = load_probe(env_key)
        if not data:
            continue
        ent = np.array([r['token_entropy'] for r in data])
        util = np.array([r['utility'] for r in data])
        rho, _ = spearmanr(ent, util)
        if field is None:
            cov = 1.0
        else:
            vals = np.array([r.get(field, 0) for r in data])
            cov = float(np.mean(vals / maxv))
        rows.append([label, f"{cov:.4f}", f"{rho:.4f}", len(data)])
    write_csv("fig_coverage_proxy", "data.csv",
              ["environment", "mean_coverage", "entropy_rho", "n_records"], rows)


# ── 16. tab_signal_discovery ──
def csv_tab_signal():
    data = [
        ["HotpotQA", "step_count", -0.494, "negative", -0.041, "Information-Poverty"],
        ["FEVER", "step_count", -0.619, "negative", -0.119, "Information-Poverty"],
        ["APPS Intro", "step_count", -0.155, "~0", 0.012, "Decision-Difficulty"],
        ["APPS Intv", "step_count", -0.339, "positive", 0.317, "Decision-Difficulty"],
        ["WebShop", "num_available_actions", 0.444, "negative", -0.019, "Mixed"],
        ["TWExpress", "step_count", -0.477, "negative", -0.290, "Information-Poverty"],
        ["CRUXEval", "step_count", 0.184, "negative", -0.048, "Weak"],
        ["Plancraft", "has_output", 0.162, "negative", -0.016, "Weak (harmful)"],
    ]
    write_csv("tab_signal_discovery", "data.csv",
              ["environment", "strongest_signal", "rho", "entropy_direction", "entropy_rho", "two_source_type"], data)


# ── 17. tab_env_setup ──
def csv_tab_env_setup():
    data = [
        ["HotpotQA", "QA", 49.0, 97.0, "Main"],
        ["APPS Intro", "Code", 58.5, 64.5, "Main (weak signal)"],
        ["WebShop", "Web", 7.2, 43.0, "Main"],
        ["FEVER", "Fact", 37.0, 99.8, "Main"],
        ["TWExpress", "Game", 67.5, 99.3, "Diagnostic (safe)"],
        ["Plancraft", "Planning", 29.8, 22.8, "Diagnostic (harmful)"],
        ["APPS Intv", "Code", 60.5, 79.5, "Appendix"],
        ["CRUXEval", "Code", 85.0, 99.5, "Appendix"],
    ]
    write_csv("tab_env_setup", "data.csv",
              ["environment", "type", "base_sr_pct", "always_sr_pct", "paper_role"], data)


# ── 18. tab_main_results ──
def csv_tab_main():
    data = [
        ["base_only", "HotpotQA", 49.0, 0.00], ["base_only", "APPS", 58.5, 0.00],
        ["base_only", "WebShop", 7.2, 0.00], ["base_only", "FEVER", 37.0, 0.00],
        ["always_trigger", "HotpotQA", 97.0, 1.80], ["always_trigger", "APPS", 64.5, 2.58],
        ["always_trigger", "WebShop", 43.0, 5.63], ["always_trigger", "FEVER", 99.8, 1.46],
        ["CaTS", "HotpotQA", 93.2, 2.86], ["CaTS", "APPS", 59.0, 2.62],
        ["CaTS", "WebShop", 30.5, 8.68], ["CaTS", "FEVER", 50.2, 6.17],
        ["AUQ", "HotpotQA", 97.0, 1.69], ["AUQ", "APPS", 61.3, 1.73],
        ["AUQ", "WebShop", 35.7, 5.33], ["AUQ", "FEVER", 40.7, 1.17],
        ["s1_budget", "HotpotQA", 97.0, 1.04], ["s1_budget", "APPS", 63.7, 1.00],
        ["s1_budget", "WebShop", 7.8, 1.00], ["s1_budget", "FEVER", 46.2, 1.58],
        ["SEAG", "HotpotQA", 67.5, 2.60], ["SEAG", "APPS", 58.5, 2.59],
        ["SEAG", "WebShop", 28.0, 7.91], ["SEAG", "FEVER", 49.3, 4.58],
        ["CoRefine", "HotpotQA", 68.2, 2.59], ["CoRefine", "APPS", 58.5, 2.59],
        ["CoRefine", "WebShop", 27.5, 7.84], ["CoRefine", "FEVER", 49.8, 4.58],
        ["CATTS", "HotpotQA", 68.3, 1.07], ["CATTS", "APPS", 58.5, 0.03],
        ["CATTS", "WebShop", 16.0, 0.19], ["CATTS", "FEVER", 34.2, 0.06],
        ["SCG", "HotpotQA", 96.8, 2.89], ["SCG", "APPS", 58.8, 2.77],
        ["SCG", "WebShop", 43.0, 7.10], ["SCG", "FEVER", 98.0, 2.45],
        ["BSW", "HotpotQA", 58.2, None], ["BSW", "WebShop", 20.6, None],
        ["BSW", "FEVER", 63.0, 5.76],
        ["DIAL", "HotpotQA", 95.2, 1.34], ["DIAL", "APPS", 66.0, 1.20],
        ["DIAL", "WebShop", 43.8, 2.29], ["DIAL", "FEVER", 49.8, 2.99],
    ]
    write_csv("tab_main_results", "data.csv",
              ["method", "environment", "sr_pct", "total_cost_ro_per_ep"], data)


# ── 19. tab_method_classification ──
def csv_tab_method_class():
    data = [
        ["CaTS", "entropy", "Fixed", "Yes", "0", "0W/5L"],
        ["SEAG", "entropy", "Fixed", "Yes", "0", "0W/6L"],
        ["CoRefine", "entropy", "Fixed", "Yes", "0", "0W/5L"],
        ["CATTS", "entropy", "Fixed", "No", "K=5 calls", "0W/6L"],
        ["AUQ", "confidence", "None", "No", "1 call/step", "1W/6L"],
        ["s1_budget", "length", "None", "No", "0", "1W/6L"],
        ["SCG", "multi-signal", "Learned", "Yes", "0", "-"],
        ["BSW", "multi-signal", "Flipped", "Yes", "0", "-"],
        ["DIAL", "multi-signal", "Auto-learned", "No", "0", "34W/2L"],
    ]
    write_csv("tab_method_classification", "data.csv",
              ["method", "signal_type", "direction", "needs_phase1", "extra_cost", "sr_win_loss"], data)


# ── 20. tab_gate_capacity ──
def csv_tab_capacity():
    data = [
        ["Base (no gate)", "-", 49.0, 0.500],
        ["Logistic (5 feat)", "Correct", 95.2, 0.851],
        ["MLP (5 feat)", "Correct", "~95", 0.869],
        ["Hidden state LR", "Correct", "~95", 0.869],
        ["Logistic (5 feat)", "Wrong", 62.0, "-"],
        ["MLP (5 feat)", "Wrong", 45.3, "-"],
    ]
    write_csv("tab_gate_capacity", "data.csv", ["gate", "direction", "sr_pct", "auc"], data)


# ── 21. tab_env_info_structure ──
def csv_tab_env_info():
    data = [
        ["HotpotQA", "Info-Poor", "Irreversible", "Immediate", "Info-Poverty", -0.041],
        ["FEVER", "Info-Poor", "Irreversible", "Immediate", "Info-Poverty", -0.119],
        ["APPS Intro", "Info-Rich", "Irreversible", "Delayed", "Decision-Difficulty", 0.012],
        ["APPS Intv", "Info-Rich", "Irreversible", "Delayed", "Decision-Difficulty", 0.317],
        ["WebShop", "Mixed", "Reversible", "Immediate", "Mixed", -0.019],
        ["TWExpress", "Info-Poor", "Irreversible", "Immediate", "Info-Poverty", -0.290],
        ["Plancraft", "Info-Rich", "Irreversible", "Delayed", "Weak (harmful)", -0.016],
        ["CRUXEval", "Info-Rich", "Irreversible", "Delayed", "Weak", -0.048],
    ]
    write_csv("tab_env_info_structure", "data.csv",
              ["environment", "info_sufficiency", "reversibility", "feedback_delay", "two_source_type", "entropy_rho"], data)


# ── 22. tab_winloss ──
def csv_tab_winloss():
    data = [
        ["CaTS", 5, 0, 6], ["SEAG", 6, 0, 6], ["CoRefine", 5, 0, 6],
        ["CATTS", 6, 0, 6], ["AUQ", 6, 1, 7], ["s1_budget", 6, 1, 7],
    ]
    write_csv("tab_winloss", "data.csv", ["cb_method", "dial_wins", "dial_losses", "n_envs"], data)


# ── 23. tab_significance ──
def csv_tab_sig():
    rows = []
    cb_methods = {'cats': 'CaTS', 'seag': 'SEAG', 'corefine': 'CoRefine',
                  'catts': 'CATTS', 'auq': 'AUQ', 's1_budget': 's1'}
    envs = ['hotpotqa', 'apps', 'webshop', 'twexpress', 'plancraft']
    env_labels = {'hotpotqa': 'HotpotQA', 'apps': 'APPS', 'webshop': 'WebShop',
                  'twexpress': 'TWExpress', 'plancraft': 'Plancraft'}
    def load_ep(env, method):
        pats = [f"results/phase6/path_e/{env}/{method}/seed_*/episodes.json",
                f"results/phase5/competing_baselines/{env}/{method}/seed_*/episodes.json",
                f"results/phase5/competing_baselines_calibrated/{env}/{method}/seed_*/episodes.json",
                f"results/phase6/new_baselines/{env}/{method}/seed_*/episodes.json"]
        succ = []
        seen = set()
        for p in pats:
            for f in sorted(glob.glob(p)):
                sd = f.split("seed_")[1].split("/")[0]
                if sd in seen:
                    continue
                seen.add(sd)
                for e in json.load(open(f)):
                    succ.append(1 if e.get("success") else 0)
        return np.array(succ) if succ else None
    rng = np.random.RandomState(42)
    for env in envs:
        dial = load_ep(env, "se_online_decay_local")
        if dial is None:
            continue
        for cb_k, cb_l in cb_methods.items():
            cb = load_ep(env, cb_k)
            if cb is None:
                continue
            delta = (dial.mean() - cb.mean()) * 100
            boots = []
            for _ in range(5000):
                boots.append((rng.choice(dial, len(dial), True).mean() - rng.choice(cb, len(cb), True).mean()) * 100)
            ci_lo, ci_hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5)
            sig = "Yes" if (ci_lo > 0 or ci_hi < 0) else "No"
            rows.append([env_labels[env], cb_l, f"{delta:.1f}", f"{ci_lo:.1f}", f"{ci_hi:.1f}", sig])
    write_csv("tab_significance", "data.csv",
              ["environment", "cb_method", "delta_sr_pp", "ci_lo", "ci_hi", "significant"], rows)


# ── 24. tab_diagnostic_results ──
def csv_tab_diag():
    data = [
        ["base_only", "TWExpress", 67.5, 0.00], ["base_only", "Plancraft", 29.8, 0.00],
        ["always_trigger", "TWExpress", 99.3, 3.45], ["always_trigger", "Plancraft", 22.8, 6.99],
        ["DIAL", "TWExpress", 99.0, 2.84], ["DIAL", "Plancraft", 23.3, 3.69],
        ["SCG", "TWExpress", 97.0, 4.83], ["SCG", "Plancraft", 21.5, 10.32],
    ]
    write_csv("tab_diagnostic_results", "data.csv",
              ["method", "environment", "sr_pct", "total_cost_ro_per_ep"], data)


# ── 25. tab_appendix_results ──
def csv_tab_appendix():
    data = [
        ["base_only", "APPS Intv", 60.5, 0.00], ["base_only", "CRUXEval", 85.0, 0.00],
        ["DIAL", "APPS Intv", 73.0, 1.35],
        ["SCG", "APPS Intv", 79.5, 3.19], ["SCG", "CRUXEval", 99.5, 2.80],
        ["AUQ", "APPS Intv", 64.7, 1.08], ["AUQ", "CRUXEval", 99.0, 1.75],
    ]
    write_csv("tab_appendix_results", "data.csv",
              ["method", "environment", "sr_pct", "total_cost_ro_per_ep"], data)


def main():
    print("Generating all CSVs...")
    csv_fig1()
    csv_fig2()
    csv_fig3()
    csv_fig4()
    csv_fig5()
    csv_fig6()
    csv_fig_auc()
    csv_fig_p1()
    csv_fig_trigger()
    csv_fig_bsw_rho()
    csv_fig_stratified()
    csv_fig_matched()
    csv_fig_coverage()
    csv_tab_signal()
    csv_tab_env_setup()
    csv_tab_main()
    csv_tab_method_class()
    csv_tab_capacity()
    csv_tab_env_info()
    csv_tab_winloss()
    csv_tab_sig()
    csv_tab_diag()
    csv_tab_appendix()
    print("\nAll CSVs generated!")


if __name__ == "__main__":
    main()
