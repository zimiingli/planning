#!/usr/bin/env python3
"""Table A.X: Reversal robustness to entropy quantile-normalization.

Reads from `results/phase_a_robustness/table1prime_quantile_norm.json`,
emits `data.csv` (selected columns) and `tab_phase_a_quantile_norm.tex`.

Rerun:  python generate.py
"""
import csv
import json
from pathlib import Path

REPO = Path("/home/uuc24002/FRVC")
SRC = REPO / "results/phase_a_robustness/table1prime_quantile_norm.json"
HERE = Path(__file__).parent

ENV_ORDER = ["HotpotQA", "APPS", "WebShop", "FEVER", "TWExpress", "Plancraft"]
BB_ORDER = ["Qwen3-4B", "Phi-3.5-mini", "Llama-3.1-8B"]
BB_DISPLAY = {"Qwen3-4B": "Qwen3-4B", "Phi-3.5-mini": "Phi-3.5", "Llama-3.1-8B": "Llama-3.1"}


def load():
    return json.loads(SRC.read_text())


def fmt_rho(r, lo, hi, sig=False):
    """Format rho as e.g. $-0.327^*$ [-0.38,-0.28], with significance star if sig=True."""
    if r is None:
        return "--"
    star = "^*" if sig else ""
    sign = "+" if r >= 0 else "-"
    return f"${sign}{abs(r):.3f}{star}$"


def fmt_with_ci(r, lo, hi, sig=False):
    """rho [CI]"""
    if r is None:
        return "--"
    star = "^*" if sig else ""
    sign = "+" if r >= 0 else "-"
    return f"${sign}{abs(r):.3f}{star}$ \\scriptsize{{$[{lo:+.2f},{hi:+.2f}]$}}"


def write_csv(rows):
    header = [
        "backbone", "env", "n", "status",
        "sp_raw_rho", "sp_raw_ci_lo", "sp_raw_ci_hi", "sp_raw_p",
        "pe_raw_rho", "pe_raw_ci_lo", "pe_raw_ci_hi",
        "pe_s1_rho", "pe_s1_ci_lo", "pe_s1_ci_hi",
        "pe_s2_rho", "pe_s2_ci_lo", "pe_s2_ci_hi",
        "pe_s3_rho", "pe_s3_ci_lo", "pe_s3_ci_hi",
        "pe_signstable_s1", "pe_signstable_s2", "pe_signstable_s3",
    ]
    out = []
    for r in rows:
        if r["status"] == "DEAD":
            out.append([r["backbone"], r["env"], r["n"], "DEAD"] + [""] * (len(header) - 4))
            continue
        sp = r["spearman"]; pe = r["pearson"]
        ss = r["pearson_sign_stable"]
        out.append([
            r["backbone"], r["env"], r["n"], "OK",
            sp["raw"]["rho"], sp["raw"]["ci"][0], sp["raw"]["ci"][1], sp["raw"]["p"],
            pe["raw"]["rho"], pe["raw"]["ci"][0], pe["raw"]["ci"][1],
            pe["scheme1"]["rho"], pe["scheme1"]["ci"][0], pe["scheme1"]["ci"][1],
            pe["scheme2"]["rho"], pe["scheme2"]["ci"][0], pe["scheme2"]["ci"][1],
            pe["scheme3"]["rho"], pe["scheme3"]["ci"][0], pe["scheme3"]["ci"][1],
            ss["scheme1_vs_raw"], ss["scheme2_vs_raw"], ss["scheme3_vs_raw"],
        ])
    with open(HERE / "data.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(out)


def write_tex(rows):
    # Build (bb, env) -> row dict
    by_key = {(r["backbone"], r["env"]): r for r in rows}

    def cell_line(bb, env):
        r = by_key.get((bb, env))
        if r is None or r["status"] == "DEAD":
            return f"{BB_DISPLAY.get(bb, bb)} & {env} & -- & -- & -- & -- & -- & -- & -- \\\\"
        sp = r["spearman"]["raw"]
        pe = r["pearson"]
        sig = sp["p"] < 0.05
        sign_star = "^*" if sig else ""
        sign = "+" if sp["rho"] >= 0 else "-"
        sp_raw_str = f"${sign}{abs(sp['rho']):.3f}{sign_star}$"

        def pe_cell(s):
            v = pe[s]["rho"]
            sg = "+" if v >= 0 else "-"
            return f"${sg}{abs(v):.3f}$"

        ss = r["pearson_sign_stable"]
        flags = []
        for k in ["scheme1_vs_raw", "scheme2_vs_raw", "scheme3_vs_raw"]:
            flags.append("\\cmark" if ss[k] else "\\xmark")
        flag_str = "/".join(flags)

        return (
            f"{BB_DISPLAY.get(bb, bb)} & {env} & {r['n']} & "
            f"{sp_raw_str} & {pe_cell('raw')} & {pe_cell('scheme1')} & "
            f"{pe_cell('scheme2')} & {pe_cell('scheme3')} & {flag_str} \\\\"
        )

    body = []
    for bb in BB_ORDER:
        for env in ENV_ORDER:
            body.append(cell_line(bb, env))
        body.append("\\midrule")
    # Remove last midrule
    if body and body[-1] == "\\midrule":
        body.pop()

    tex = r"""\begin{table*}[t]
\centering
\caption{Robustness of cross-backbone reversal to entropy
quantile-normalization. For each (env, backbone) cell, we report
Spearman $\rho(\sigma, U)$ (which is mathematically invariant under
within-cell monotone transforms of $\sigma$, so the value is shared
across raw/S1/S2/S3) and Pearson $\rho$ under raw vs.\ three
quantile-normalization schemes: \textbf{S1} (per-(env, backbone))
ranks within each cell; \textbf{S2} (per-backbone) ranks within
each backbone's pool; \textbf{S3} (per-environment) ranks within
each environment's pool. \cmark/\xmark{} mark whether the Pearson
sign is stable vs.\ raw under each scheme (CI excludes 0 on the
same side). The cross-backbone reversal cells (HotpotQA, APPS,
FEVER) preserve sign across all three schemes on both metrics;
the cells where Pearson sign flips are uniformly weak-signal cells
with raw $|\rho|<0.13$. DEAD: signal variance $\approx 0$ or no
positive utility labels. $^*$: $p<0.05$. 1000-resample bootstrap.}
\label{tab:phase-a-norm}
\footnotesize
\begin{tabular}{l l r c c c c c c}
\toprule
& & & \textbf{Spearman} & \multicolumn{4}{c}{\textbf{Pearson $\rho(\sigma, U)$}} & \textbf{Sign stable} \\
\cmidrule(lr){5-8}
\textbf{Backbone} & \textbf{Env} & \textbf{N} & raw=S1=S2=S3 & raw & S1 & S2 & S3 & S1/S2/S3 \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    (HERE / "tab_phase_a_quantile_norm.tex").write_text(tex)


def main():
    rows = load()
    write_csv(rows)
    write_tex(rows)
    print(f"Wrote: {HERE / 'data.csv'}")
    print(f"Wrote: {HERE / 'tab_phase_a_quantile_norm.tex'}")


if __name__ == "__main__":
    main()
