#!/usr/bin/env python3
"""
Convert Phase A JSON outputs into CSVs for paper / analysis consumption.

Run from repo root:
  python planning/experiments_to_add/phase_a_results/generate_csvs.py

Reads from:  results/phase_a_robustness/*.json
Writes to:   planning/experiments_to_add/phase_a_results/*.csv
"""

import csv
import json
from pathlib import Path

REPO = Path("/home/uuc24002/FRVC")
SRC = REPO / "results/phase_a_robustness"
DST = REPO / "planning/experiments_to_add/phase_a_results"


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  -> {path.relative_to(REPO)} ({len(rows)} rows)")


# ---------- Table 1' ----------
def emit_table1prime():
    src = json.loads((SRC / "table1prime_quantile_norm.json").read_text())
    header = [
        "backbone", "env", "n", "status",
        # Spearman: 4 schemes × 3 fields (rho, ci_lo, ci_hi) + 3 sign-stable flags
        "sp_raw_rho", "sp_raw_ci_lo", "sp_raw_ci_hi", "sp_raw_p",
        "sp_s1_rho", "sp_s1_ci_lo", "sp_s1_ci_hi",
        "sp_s2_rho", "sp_s2_ci_lo", "sp_s2_ci_hi",
        "sp_s3_rho", "sp_s3_ci_lo", "sp_s3_ci_hi",
        "sp_s1_signstable", "sp_s2_signstable", "sp_s3_signstable",
        # Pearson: same shape
        "pe_raw_rho", "pe_raw_ci_lo", "pe_raw_ci_hi", "pe_raw_p",
        "pe_s1_rho", "pe_s1_ci_lo", "pe_s1_ci_hi",
        "pe_s2_rho", "pe_s2_ci_lo", "pe_s2_ci_hi",
        "pe_s3_rho", "pe_s3_ci_lo", "pe_s3_ci_hi",
        "pe_s1_signstable", "pe_s2_signstable", "pe_s3_signstable",
    ]
    rows = []
    for r in src:
        if r["status"] == "DEAD":
            rows.append([r["backbone"], r["env"], r["n"], "DEAD"] + [""] * (len(header) - 4))
            continue
        sp, pe = r["spearman"], r["pearson"]
        sps, pes = r["spearman_sign_stable"], r["pearson_sign_stable"]
        row = [r["backbone"], r["env"], r["n"], "OK",
               sp["raw"]["rho"], sp["raw"]["ci"][0], sp["raw"]["ci"][1], sp["raw"]["p"],
               sp["scheme1"]["rho"], sp["scheme1"]["ci"][0], sp["scheme1"]["ci"][1],
               sp["scheme2"]["rho"], sp["scheme2"]["ci"][0], sp["scheme2"]["ci"][1],
               sp["scheme3"]["rho"], sp["scheme3"]["ci"][0], sp["scheme3"]["ci"][1],
               sps["scheme1_vs_raw"], sps["scheme2_vs_raw"], sps["scheme3_vs_raw"],
               pe["raw"]["rho"], pe["raw"]["ci"][0], pe["raw"]["ci"][1], pe["raw"]["p"],
               pe["scheme1"]["rho"], pe["scheme1"]["ci"][0], pe["scheme1"]["ci"][1],
               pe["scheme2"]["rho"], pe["scheme2"]["ci"][0], pe["scheme2"]["ci"][1],
               pe["scheme3"]["rho"], pe["scheme3"]["ci"][0], pe["scheme3"]["ci"][1],
               pes["scheme1_vs_raw"], pes["scheme2_vs_raw"], pes["scheme3_vs_raw"]]
        rows.append(row)
    write_csv(DST / "table1prime_quantile_norm.csv", header, rows)


# ---------- Table A2 (long format) ----------
def emit_table_a2():
    src = json.loads((SRC / "table_a2_reward_bias.json").read_text())

    # Long format: one row per (cell, perturbation_type, value)
    header_long = ["backbone", "env", "n", "status", "perturbation_type", "param_value",
                   "pos_frac", "label_flip_rate", "majority_class", "majority_flipped",
                   "spearman_rho"]
    rows_long = []
    for r in src:
        if r["status"] == "DEAD":
            rows_long.append([r["backbone"], r["env"], r["n"], "DEAD",
                              "", "", "", "", "", "", ""])
            continue
        # Shift rows
        for s in r["shift_results"]:
            rows_long.append([r["backbone"], r["env"], r["n"], "OK",
                              "shift", s["c"], s["pos_frac"], s["label_flip_rate"],
                              s["majority_class"], s["majority_flipped"],
                              s["spearman_rho"]])
        # Scale rows (only Spearman ρ is meaningful)
        for s in r["scale_results"]:
            rows_long.append([r["backbone"], r["env"], r["n"], "OK",
                              "scale", s["alpha"], "", "", "", "",
                              s["spearman_rho"]])
    write_csv(DST / "table_a2_reward_bias.csv", header_long, rows_long)


# ---------- Table A4 (long format) ----------
def emit_table_a4():
    src = json.loads((SRC / "table_a4_temperature.json").read_text())

    # Long format: one row per (cell, transform_type, param)
    header = ["backbone", "env", "n", "status", "transform_type", "param_value",
              "spearman_rho", "pearson_rho"]
    rows = []
    for r in src:
        if r["status"] == "DEAD":
            rows.append([r["backbone"], r["env"], r["n"], "DEAD", "", "", "", ""])
            continue
        for t in r["temperature_results"]:
            rows.append([r["backbone"], r["env"], r["n"], "OK",
                         "linear_T", t["T"], t["spearman_rho"], t["pearson_rho"]])
        for p in r["power_results"]:
            rows.append([r["backbone"], r["env"], r["n"], "OK",
                         "power_alpha", p["alpha"], p["spearman_rho"], p["pearson_rho"]])
        rows.append([r["backbone"], r["env"], r["n"], "OK",
                     "log", "log", r["log_result"]["spearman_rho"], r["log_result"]["pearson_rho"]])
    write_csv(DST / "table_a4_entropy_transforms.csv", header, rows)


# ---------- Manifest CSV ----------
def emit_manifest():
    """Reproducibility: where each cell's data came from."""
    cells = [
        ("Qwen3-4B",     "HotpotQA",  "results/phase1_signal_discovery/hotpotqa/phase1_signal_data.json", 1208),
        ("Qwen3-4B",     "APPS",      "results/phase6/apps_interview/apps_interview/phase1_signal_data.json", 439),
        ("Qwen3-4B",     "WebShop",   "results/phase4/webshop/p4_webshop_signal_data.json", 1073),
        ("Qwen3-4B",     "FEVER",     "results/phase6/fever/fever/phase1_signal_data.json", 282),
        ("Qwen3-4B",     "TWExpress", "results/phase5/twexpress/twexpress/phase1_signal_data.json", 798),
        ("Qwen3-4B",     "Plancraft", "results/phase5/plancraft/plancraft/phase1_signal_data.json", 1360),
        ("Phi-3.5-mini", "HotpotQA",  "results/review/phi35_mini/hotpotqa/hotpotqa/phase1_signal_data.json", 242),
        ("Phi-3.5-mini", "APPS",      "results/review/phi35_mini/apps/apps/phase1_signal_data.json", 400),
        ("Phi-3.5-mini", "WebShop",   "results/review/phi35_mini/webshop/webshop/phase1_signal_data.json", 751),
        ("Phi-3.5-mini", "FEVER",     "results/review/phi35_mini/fever/fever/phase1_signal_data.json", 824),
        ("Phi-3.5-mini", "TWExpress", "results/review/phi35_mini/twexpress/twexpress/phase1_signal_data.json", 200),
        ("Phi-3.5-mini", "Plancraft", "results/review/phi35_mini/plancraft/plancraft/phase1_signal_data.json", 2232),
        ("Llama-3.1-8B", "HotpotQA",  "results/review/llama31_8b/hotpotqa/hotpotqa/phase1_signal_data.json", 244),
        ("Llama-3.1-8B", "APPS",      "results/review/llama31_8b/apps/apps/phase1_signal_data.json", 475),
        ("Llama-3.1-8B", "WebShop",   "results/review/llama31_8b/webshop/webshop/phase1_signal_data.json", 948),
        ("Llama-3.1-8B", "FEVER",     "results/review/llama31_8b/fever/fever/phase1_signal_data.json", 840),
        ("Llama-3.1-8B", "TWExpress", "results/review/llama31_8b/twexpress/twexpress/phase1_signal_data.json", 200),
        ("Llama-3.1-8B", "Plancraft", "results/review/llama31_8b/plancraft/plancraft/phase1_signal_data.json", 1338),
    ]
    dead = {("Phi-3.5-mini", "TWExpress"), ("Phi-3.5-mini", "Plancraft"), ("Llama-3.1-8B", "TWExpress")}
    header = ["backbone", "env", "data_path_relative_to_repo", "n_steps", "status"]
    rows = [[bb, env, p, n, "DEAD" if (bb, env) in dead else "OK"] for bb, env, p, n in cells]
    write_csv(DST / "manifest.csv", header, rows)


def main():
    DST.mkdir(parents=True, exist_ok=True)
    print("Generating CSVs from Phase A JSON outputs...")
    emit_manifest()
    emit_table1prime()
    emit_table_a2()
    emit_table_a4()
    print("Done.")


if __name__ == "__main__":
    main()
