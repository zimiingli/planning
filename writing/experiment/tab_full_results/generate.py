#!/usr/bin/env python3
"""
Regenerate tab_full_results.tex with mean ± std SR cells.

Input:  cells.json  (produced by compute_std.py)
Output: tab_full_results.tex
"""
import json
from pathlib import Path

DIR = Path(__file__).parent

# Cost values are not changed (kept as in the previous table). Pulled from the
# original LaTeX so we don't need to re-read summaries for cost.
COSTS = {
    "qwen3": {
        "hotpotqa":  {"cats":"10.54","seag":"9.34","corefine":"9.28","catts":"10.53","auq":"10.29","s1_budget":"8.27","DIAL":"8.02"},
        "webshop":   {"cats":"3.45","seag":"2.84","corefine":"2.78","catts":"5.55","auq":"5.83","s1_budget":"2.91","DIAL":"2.50"},
        "fever":     {"cats":"25.48","seag":"17.19","corefine":"17.19","catts":"16.46","auq":"18.04","s1_budget":"19.21","DIAL":"16.51"},
        "twexpress": {"cats":"3.37","seag":"2.60","corefine":"2.57","catts":"2.83","auq":"1.95","s1_budget":"2.02","DIAL":"1.81"},
        "plancraft": {"cats":"4.14","seag":"3.52","corefine":"3.44","catts":"6.53","auq":"6.64","s1_budget":"3.02","DIAL":"3.63"},
        "apps":      {"cats":"2.61","seag":"2.75","corefine":"2.70","catts":"6.00","auq":"3.28","s1_budget":"2.65","DIAL":"2.61"},
    },
    "phi35": {
        "hotpotqa":  {"cats":"5.86","seag":"7.82","corefine":"7.83","catts":"7.98","auq":"5.47","s1_budget":"5.26","DIAL":"5.38"},
        "webshop":   {"cats":"2.52","seag":"2.43","corefine":"2.44","catts":"4.86","auq":"3.11","s1_budget":"3.89","DIAL":"2.56"},
        "fever":     {"cats":"14.51","seag":"5.61","corefine":"5.73","catts":"7.65","auq":"3.18","s1_budget":"8.45","DIAL":"7.44"},
        "twexpress": {"cats":"1.00","seag":"2.58","corefine":"2.56","catts":"4.00","auq":"1.82","s1_budget":"2.05","DIAL":"1.83"},
        "plancraft": {"cats":"1.44","seag":"2.29","corefine":"2.24","catts":"5.96","auq":"2.24","s1_budget":"1.73","DIAL":"1.33"},
        "apps":      {"cats":"3.55","seag":"2.59","corefine":"2.60","catts":"6.10","auq":"2.03","s1_budget":"2.93","DIAL":"2.87"},
    },
    "llama31": {
        "hotpotqa":  {"cats":"7.21","seag":"9.82","corefine":"9.42","catts":"11.11","auq":"10.54","s1_budget":"8.08","DIAL":"7.07"},
        "webshop":   {"cats":"2.51","seag":"1.86","corefine":"1.82","catts":"4.74","auq":"4.54","s1_budget":"1.87","DIAL":"1.68"},
        "fever":     {"cats":"14.82","seag":"12.57","corefine":"12.64","catts":"17.00","auq":"25.08","s1_budget":"8.56","DIAL":"18.69"},
        "twexpress": {"cats":"3.00","seag":"3.85","corefine":"3.56","catts":"4.11","auq":"3.58","s1_budget":"3.05","DIAL":"2.55"},
        "plancraft": {"cats":"3.42","seag":"2.70","corefine":"2.69","catts":"7.31","auq":"8.21","s1_budget":"2.53","DIAL":"2.49"},
        "apps":      {"cats":"4.81","seag":"4.41","corefine":"4.37","catts":"6.70","auq":"6.11","s1_budget":"2.33","DIAL":"4.29"},
    },
}

LABEL = {
    "cats": r"CaTS$^\dagger$",
    "seag": r"SEAG$^\dagger$",
    "corefine": r"CoRefine$^\dagger$",
    "catts": "CATTS",
    "auq": "AUQ",
    "s1_budget": r"s1\_budget",
    "DIAL": r"\textbf{DIAL}",
}
BACKBONES = [
    ("qwen3",   "Qwen3-4B-Instruct"),
    ("phi35",   "Phi-3.5-mini-Instruct"),
    ("llama31", "Llama-3.1-8B-Instruct"),
]
ENV_ORDER = ["hotpotqa", "webshop", "fever", "twexpress", "plancraft", "apps"]
METHOD_ORDER = ["cats", "seag", "corefine", "catts", "auq", "s1_budget", "DIAL"]


def fmt_sr(mean, std, color=None, bold=False):
    """Format a single SR cell with optional cellcolor + bold."""
    if std is None:
        core = f"{mean}"
    elif bold:
        core = f"\\mathbf{{{mean}}}{{\\scriptstyle\\,\\pm\\,{std:.1f}}}"
    else:
        core = f"{mean}{{\\scriptstyle\\,\\pm\\,{std:.1f}}}"
    body = f"${core}$"
    if color == "red":
        return f"\\cellcolor{{red!15}}{body}"
    if color == "blue":
        return f"\\cellcolor{{blue!10}}{body}"
    return body


def best_and_second(values, prefer_for_tie="DIAL"):
    """values: dict method -> mean. Return (best_method, second_method).
    On a tie for first, prefer the method named in `prefer_for_tie`."""
    top_val = max(values.values())
    tied = [m for m, v in values.items() if v >= top_val - 1e-6]
    if prefer_for_tie in tied:
        best = prefer_for_tie
    else:
        best = tied[0]
    second = None
    second_val = -float("inf")
    for m, v in values.items():
        if m == best:
            continue
        if v > second_val:
            second_val = v
            second = m
    if second_val >= top_val - 1e-6:
        # Second was tied with best (a third method); leave second uncolored
        # to avoid double red, mark it blue.
        pass
    return best, second


def main():
    cells = json.load(open(DIR / "cells.json"))

    # Lookup cells[key]["mean"], cells[key]["std"]
    def get(bb, env, m):
        return cells[f"{bb}|{env}|{m}"]

    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Full results across 6 environments and 3 backbones. SR (\%) and Cost ($\times$base, total deployment tokens normalized by base\_only).",
        r"SR is mean$\pm$std across three seeds (\{42, 123, 456\}).",
        r"\colorbox{red!15}{\strut Best} and \colorbox{blue!10}{\strut second-best} mean SR per environment.",
        r"$\dagger$: methods requiring calibration data.",
        r"Cost includes all LLM calls: base proposer, gate overhead (CATTS $K{=}5$ voting, AUQ confidence query), and rollout calls.}",
        r"\label{tab:full-results}",
        r"\renewcommand{\arraystretch}{0.9}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{l *{6}{rc} }",
        r"\toprule",
        r"& \multicolumn{2}{c}{\textbf{HotpotQA}} & \multicolumn{2}{c}{\textbf{WebShop}} & \multicolumn{2}{c}{\textbf{FEVER}}",
        r"& \multicolumn{2}{c}{\textbf{TWExpress}} & \multicolumn{2}{c}{\textbf{Plancraft}} & \multicolumn{2}{c}{\textbf{APPS}} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}",
        r"\cmidrule(lr){8-9}\cmidrule(lr){10-11}\cmidrule(lr){12-13}",
        r"\textbf{Method} & SR$\uparrow$ & Cost$\downarrow$ & SR$\uparrow$ & Cost$\downarrow$ & SR$\uparrow$ & Cost$\downarrow$ & SR$\uparrow$ & Cost$\downarrow$ & SR$\uparrow$ & Cost$\downarrow$ & SR$\uparrow$ & Cost$\downarrow$ \\",
        r"\midrule",
    ]

    for bb_key, bb_label in BACKBONES:
        lines.append(rf"\multicolumn{{13}}{{c}}{{\textit{{{bb_label}}}}} \\")
        lines.append(r"\midrule")
        # Compute per-env best/second
        best_per_env = {}
        for env in ENV_ORDER:
            means = {m: get(bb_key, env, m)["mean"] for m in METHOD_ORDER}
            best_per_env[env] = best_and_second(means)
        for m in METHOD_ORDER:
            row = [LABEL[m]]
            for env in ENV_ORDER:
                cell = get(bb_key, env, m)
                mean = cell["mean"]; std = cell["std"]
                cost = COSTS[bb_key][env][m]
                best, second = best_per_env[env]
                color = "red" if m == best else ("blue" if m == second else None)
                bold = (m == "DIAL") or (m == best)
                row.append(fmt_sr(mean, std, color=color, bold=bold))
                row.append(cost)
            lines.append(" & ".join(row) + r" \\")
        if bb_key != BACKBONES[-1][0]:
            lines.append(r"\midrule")

    lines += [
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table*}",
    ]

    out = "\n".join(lines) + "\n"
    out_path = DIR / "tab_full_results.tex"
    out_path.write_text(out)
    print(f"Wrote {out_path} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
