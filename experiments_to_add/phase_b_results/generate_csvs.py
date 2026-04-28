#!/usr/bin/env python3
"""
Convert Phase B summary.json files into CSVs for paper / analysis consumption.

Reads from:  results/phase_b_calibration_sweep/n_cal_{N}/{env}/{method}/seed_{S}/summary.json
Writes to:   planning/experiments_to_add/phase_b_results/*.csv

Outputs:
  grid_results.csv            wide: one row per (n_cal, env, method, seed) cell
  monotonicity.csv            wide: one row per (env, method); Spearman ρ(N_cal, SR), Spearman ρ(N_cal, RR)
  manifest.csv                wide: 20 subsample sources (env × N_cal)

Usage:
  python planning/experiments_to_add/phase_b_results/generate_csvs.py
"""

import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


REPO = Path("/home/uuc24002/FRVC")
SRC = REPO / "results/phase_b_calibration_sweep"
DST = REPO / "planning/experiments_to_add/phase_b_results"

N_CALS = [20, 50, 100, 200, 500]
ENVS = ["hotpotqa", "fever", "apps", "webshop"]
METHODS = ["catts", "seag", "corefine", "cats", "auq", "s1_budget"]
SEEDS = [42]   # Wave 1


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  -> {path.relative_to(REPO)} ({len(rows)} rows)")


def safe_get(d, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
        if d is None:
            return default
    return d


# ---------- grid_results.csv ----------

def emit_grid_results():
    header = [
        "n_cal", "env", "method", "seed", "status",
        "success_rate", "avg_reward",
        "rollout_rate", "avg_rollouts_per_ep", "total_rollouts", "total_decisions",
        "n_episodes", "elapsed_seconds",
        "gate_threshold", "gate_signal", "gate_direction", "gate_buffer_size",
        "summary_path",
    ]
    rows = []
    for n in N_CALS:
        for env in ENVS:
            for m in METHODS:
                for s in SEEDS:
                    fp = SRC / f"n_cal_{n}/{env}/{m}/seed_{s}/summary.json"
                    if not fp.exists():
                        rows.append([n, env, m, s, "MISSING"] + [""] * (len(header) - 6) + [str(fp.relative_to(REPO))])
                        continue
                    with open(fp) as f:
                        d = json.load(f)
                    gs = d.get("gate_stats", {})
                    # Different baselines store threshold differently
                    threshold = (
                        gs.get("threshold")
                        or gs.get("entropy_threshold")
                        or gs.get("budget_K")
                        or ""
                    )
                    signal = gs.get("signal_name", "")
                    direction = gs.get("direction", "")
                    rows.append([
                        n, env, m, s, "OK",
                        d.get("success_rate"),
                        d.get("avg_reward"),
                        gs.get("rollout_rate"),
                        d.get("avg_rollouts_per_ep"),
                        d.get("total_rollouts"),
                        gs.get("total_decisions"),
                        d.get("num_episodes"),
                        d.get("elapsed_seconds"),
                        threshold, signal, direction,
                        gs.get("buffer_size"),
                        str(fp.relative_to(REPO)),
                    ])
    write_csv(DST / "grid_results.csv", header, rows)
    return rows


# ---------- monotonicity.csv ----------

def emit_monotonicity(grid_rows):
    """Compute Spearman ρ(N_cal, SR) and ρ(N_cal, RR) per (env, method) over the 5 N_cal points."""
    header = [
        "env", "method", "n_points", "n_missing",
        "sr_n20", "sr_n50", "sr_n100", "sr_n200", "sr_n500",
        "rr_n20", "rr_n50", "rr_n100", "rr_n200", "rr_n500",
        "rho_sr_vs_ncal", "p_sr",
        "rho_rr_vs_ncal", "p_rr",
        "interpretation",
    ]
    out_rows = []

    # Group rows by (env, method)
    by_em = {}
    for r in grid_rows:
        n_cal, env, method, seed, status = r[0], r[1], r[2], r[3], r[4]
        if status != "OK":
            continue
        sr, rr = r[5], r[7]
        by_em.setdefault((env, method), {})[n_cal] = (sr, rr)

    # Type-I (misaligned) vs Type-D (aligned) per Phase A
    misaligned_envs = {"hotpotqa", "fever"}

    for env in ENVS:
        for m in METHODS:
            cells = by_em.get((env, m), {})
            n_present = len(cells)
            n_missing = 5 - n_present

            sr_list = [cells.get(n, (None, None))[0] for n in N_CALS]
            rr_list = [cells.get(n, (None, None))[1] for n in N_CALS]

            valid_idx = [i for i, sr in enumerate(sr_list) if sr is not None]
            if len(valid_idx) >= 3:
                ncal_arr = np.array([N_CALS[i] for i in valid_idx])
                sr_arr   = np.array([sr_list[i] for i in valid_idx])
                rr_arr   = np.array([rr_list[i] for i in valid_idx])
                rho_sr, p_sr = spearmanr(ncal_arr, sr_arr)
                rho_rr, p_rr = spearmanr(ncal_arr, rr_arr)
            else:
                rho_sr = p_sr = rho_rr = p_rr = None

            interp = ""
            if rho_sr is not None and not np.isnan(rho_sr):
                expect_negative = env in misaligned_envs
                if expect_negative:
                    if rho_sr < -0.7:
                        interp = "strong-negative (matches misaligned)"
                    elif rho_sr < -0.3:
                        interp = "weak-negative (matches misaligned)"
                    elif rho_sr > 0.3:
                        interp = "WRONG-DIRECTION (positive on misaligned env)"
                    else:
                        interp = "flat"
                else:
                    if rho_sr > 0.7:
                        interp = "strong-positive (matches aligned)"
                    elif rho_sr > 0.3:
                        interp = "weak-positive (matches aligned)"
                    elif rho_sr < -0.3:
                        interp = "WRONG-DIRECTION (negative on aligned env)"
                    else:
                        interp = "flat"

            out_rows.append([
                env, m, n_present, n_missing,
                *[f"{x:.4f}" if x is not None else "" for x in sr_list],
                *[f"{x:.4f}" if x is not None else "" for x in rr_list],
                f"{rho_sr:.4f}" if rho_sr is not None else "",
                f"{p_sr:.4f}" if p_sr is not None else "",
                f"{rho_rr:.4f}" if rho_rr is not None else "",
                f"{p_rr:.4f}" if p_rr is not None else "",
                interp,
            ])
    write_csv(DST / "monotonicity.csv", header, out_rows)


# ---------- manifest.csv ----------

def emit_manifest():
    """Provenance: which subsample file fed each Phase B cell."""
    header = ["n_cal", "env", "subsample_path", "n_actual", "n_total_in_source", "capped"]
    rows = []
    summary_path = SRC / "subsamples/subsample_summary.json"
    if not summary_path.exists():
        print(f"  [WARN] manifest: subsample_summary.json missing")
        return
    with open(summary_path) as f:
        d = json.load(f)
    for cell in d.get("cells", []):
        rows.append([
            cell["n_cal_requested"],
            cell["env"],
            cell["path"],
            cell["n_cal_actual"],
            cell["n_total"],
            cell["capped"],
        ])
    write_csv(DST / "manifest.csv", header, rows)


def main():
    DST.mkdir(parents=True, exist_ok=True)
    print("Generating Phase B CSVs from summary.json files...")
    grid_rows = emit_grid_results()
    emit_monotonicity(grid_rows)
    emit_manifest()
    print()
    print(f"Total cells: {sum(1 for r in grid_rows if r[4] == 'OK')}/120")
    print(f"Missing:     {sum(1 for r in grid_rows if r[4] != 'OK')}/120")
    print("Done.")


if __name__ == "__main__":
    main()
