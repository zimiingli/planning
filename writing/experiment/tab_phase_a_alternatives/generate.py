#!/usr/bin/env python3
"""Table A.Y: Reversal robustness to monotone reward and entropy transforms.

Reads from `results/phase_a_robustness/{table_a2_reward_bias, table_a4_temperature}.json`,
emits `data.csv` and `tab_phase_a_alternatives.tex`.

Rerun:  python generate.py
"""
import csv
import json
from pathlib import Path

REPO = Path("/home/uuc24002/FRVC")
SRC_REWARD = REPO / "results/phase_a_robustness/table_a2_reward_bias.json"
SRC_TEMP   = REPO / "results/phase_a_robustness/table_a4_temperature.json"
HERE = Path(__file__).parent

ENV_ORDER = ["HotpotQA", "APPS", "WebShop", "FEVER", "TWExpress", "Plancraft"]
BB_ORDER  = ["Qwen3-4B", "Phi-3.5-mini", "Llama-3.1-8B"]
BB_DISPLAY = {"Qwen3-4B": "Qwen3-4B", "Phi-3.5-mini": "Phi-3.5", "Llama-3.1-8B": "Llama-3.1"}


def load_data():
    reward = {(r["backbone"], r["env"]): r for r in json.loads(SRC_REWARD.read_text())}
    temp   = {(r["backbone"], r["env"]): r for r in json.loads(SRC_TEMP.read_text())}
    return reward, temp


def write_csv(reward, temp):
    header = [
        "backbone", "env", "status",
        "sp_raw", "sp_alpha_neg1", "sp_alpha_pos2",
        "sp_pow_alpha05", "sp_pow_alpha2", "sp_log",
        "pe_pow_alpha05", "pe_pow_alpha1", "pe_pow_alpha2", "pe_log",
    ]
    rows = []
    for bb in BB_ORDER:
        for env in ENV_ORDER:
            r_rw = reward.get((bb, env)); r_tp = temp.get((bb, env))
            if not r_rw or r_rw["status"] == "DEAD":
                rows.append([bb, env, "DEAD"] + [""] * (len(header) - 3))
                continue
            scale = {s["alpha"]: s["spearman_rho"] for s in r_rw["scale_results"]}
            powr  = {p["alpha"]: p for p in r_tp["power_results"]}
            log_  = r_tp["log_result"]
            rows.append([
                bb, env, "OK",
                # Spearman raw is α=1 case
                scale.get(1.0),
                scale.get(-1.0),
                scale.get(2.0),
                # Spearman under power transforms (should = raw)
                powr.get(0.5, {}).get("spearman_rho"),
                powr.get(2.0, {}).get("spearman_rho"),
                log_["spearman_rho"],
                # Pearson under power transforms (varies)
                powr.get(0.5, {}).get("pearson_rho"),
                powr.get(1.0, {}).get("pearson_rho"),
                powr.get(2.0, {}).get("pearson_rho"),
                log_["pearson_rho"],
            ])
    with open(HERE / "data.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def fmt(v, dec=3):
    if v is None or v == "":
        return "--"
    sign = "+" if v >= 0 else "-"
    return f"${sign}{abs(v):.{dec}f}$"


def write_tex(reward, temp):
    body_rows = []
    for bb in BB_ORDER:
        for env in ENV_ORDER:
            r_rw = reward.get((bb, env)); r_tp = temp.get((bb, env))
            if not r_rw or r_rw["status"] == "DEAD":
                body_rows.append(
                    f"{BB_DISPLAY.get(bb, bb)} & {env} & -- & -- & -- & -- & -- & -- & -- & -- \\\\"
                )
                continue
            scale = {s["alpha"]: s["spearman_rho"] for s in r_rw["scale_results"]}
            powr  = {p["alpha"]: p for p in r_tp["power_results"]}
            log_  = r_tp["log_result"]
            body_rows.append(
                f"{BB_DISPLAY.get(bb, bb)} & {env} & "
                f"{fmt(scale.get(1.0))} & {fmt(scale.get(-1.0))} & "
                f"{fmt(powr.get(0.5,{}).get('spearman_rho'))} & "
                f"{fmt(powr.get(2.0,{}).get('spearman_rho'))} & "
                f"{fmt(log_['spearman_rho'])} & "
                f"{fmt(powr.get(0.5,{}).get('pearson_rho'))} & "
                f"{fmt(powr.get(2.0,{}).get('pearson_rho'))} & "
                f"{fmt(log_['pearson_rho'])} \\\\"
            )
        body_rows.append(r"\midrule")
    if body_rows and body_rows[-1] == r"\midrule":
        body_rows.pop()

    tex = r"""\begin{table*}[t]
\centering
\caption{Robustness of $\rho(\sigma, U)$ to monotone reward and
entropy transforms. Spearman $\rho$ is rank-invariant under
positive monotone transforms of either variable, so the
$\sigma\!\to\!\sigma^{0.5}$, $\sigma^{2}$, and $\log\sigma$
columns must agree with the raw column up to numerical noise --
this is reported transparently as a sanity check ruling out
upstream entropy-pipeline bugs. For $U\!\to\!\alpha U$ with
$\alpha < 0$, Spearman flips sign as expected (rank order
reversed). Pearson $\rho$ varies under non-linear $\sigma$
transforms (informative); the only cell where Pearson sign
flips is Phi-3.5 / APPS under $\log\sigma$, where Spearman
remains stable at $-0.129$. DEAD: signal variance $\approx 0$
or no positive utility labels.}
\label{tab:phase-a-alternatives}
\footnotesize
\begin{tabular}{l l c c c c c c c c}
\toprule
& & \multicolumn{5}{c}{\textbf{Spearman $\rho$}} & \multicolumn{3}{c}{\textbf{Pearson $\rho$}} \\
\cmidrule(lr){3-7} \cmidrule(lr){8-10}
& & raw & $\alpha U$, $\alpha\!=\!-1$ & $\sigma^{0.5}$ & $\sigma^{2}$ & $\log\sigma$ & $\sigma^{0.5}$ & $\sigma^{2}$ & $\log\sigma$ \\
\textbf{Backbone} & \textbf{Env} & & & & & & & & \\
\midrule
""" + "\n".join(body_rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    (HERE / "tab_phase_a_alternatives.tex").write_text(tex)


def main():
    reward, temp = load_data()
    write_csv(reward, temp)
    write_tex(reward, temp)
    print(f"Wrote: {HERE / 'data.csv'}")
    print(f"Wrote: {HERE / 'tab_phase_a_alternatives.tex'}")


if __name__ == "__main__":
    main()
