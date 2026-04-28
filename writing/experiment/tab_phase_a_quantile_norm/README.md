# tab_phase_a_quantile_norm

## Paper Location
`appendix.tex`, App G new subsection `\subsection{Robustness of Reversal to Entropy Quantile-Normalization}` (label `app:reversal-norm`). Inserted right after `\subsection{Multi-Backbone Verification}`.

## Writing Prompt
Per-cell Spearman + Pearson $\rho(\sigma, U)$ under raw vs.\ three quantile-normalization schemes (S1 per-cell, S2 per-backbone, S3 per-environment). Defends cross-backbone reversal in Table 1 against the "scale artifact" attack.

## Data Status
- ✅ Source JSON: `results/phase_a_robustness/table1prime_quantile_norm.json` (Phase A harness output, 2026-04-27)
- ✅ Filtered CSV: `data.csv` (18 cells)
- ✅ Generated table: `tab_phase_a_quantile_norm.tex`

## Key Results (from data.csv)

- 15 / 18 cells analyzable (3 DEAD: TWExpress on \{Phi-3.5, Llama-3.1\}, Plancraft on Phi-3.5)
- Spearman $\rho$ identical across schemes by rank-invariance (mathematically required)
- Pearson sign-stable on 11/15 (S1), 11/15 (S2), 10/15 (S3) cells
- All 3 cross-backbone reversal envs (HotpotQA, APPS, FEVER) preserve Pearson sign on the strong cells under all 3 schemes ⭐

## Raw Data Source
- `results/phase_a_robustness/table1prime_quantile_norm.json` (raw output)
- `planning/experiments_to_add/phase_a_results/table1prime_quantile_norm.csv` (presentation copy)
- Harness: `experiments/p7_robustness_harness.py` (run with `--n-boot 1000`)

## Files
- `data.csv` — backbone, env, n, status, sp_raw_*, pe_raw_*, pe_s1_*, pe_s2_*, pe_s3_*, pe_signstable_*
- `generate.py` — regenerates data.csv + .tex from source JSON
- `tab_phase_a_quantile_norm.tex` — LaTeX `\begin{table*}` for paper inclusion

## Reproducibility
```bash
python planning/writing/experiment/tab_phase_a_quantile_norm/generate.py
```
