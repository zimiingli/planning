# tab_phase_a_alternatives

## Paper Location
`appendix.tex`, App G new subsection `\subsection{Ruling Out Alternative Explanations: Reward and Entropy Calibration}` (label `app:reversal-alternatives`). Inserted right after `\subsection{Robustness of Reversal to Entropy Quantile-Normalization}`.

## Writing Prompt
Per-cell Spearman / Pearson $\rho(\sigma, U)$ under monotone reward transforms ($U \to \alpha U$) and non-linear entropy transforms ($\sigma \to \sigma^\alpha$, $\sigma \to \log\sigma$). Demonstrates that the cross-backbone reversal is not explained by reward parameterization or entropy estimator calibration.

## Data Status
- ✅ Source JSON: `results/phase_a_robustness/table_a2_reward_bias.json` (Exp 04.2 output)
- ✅ Source JSON: `results/phase_a_robustness/table_a4_temperature.json` (Exp 04.4 output)
- ✅ Filtered CSV: `data.csv`
- ✅ Generated table: `tab_phase_a_alternatives.tex`

## Key Results (from data.csv)

- Spearman $\rho$ exactly preserved across all positive-monotone $\sigma$ transforms ($\sigma^{0.5}$, $\sigma^2$, $\log\sigma$) on every cell — confirms no entropy-pipeline bug.
- Spearman $\rho$ flips sign for $\alpha = -1$ (negating $U$ reverses rank order) — expected.
- Pearson $\rho$ varies under non-linear $\sigma$ transforms (informative). Only **one** cell (Phi-3.5 / APPS under $\log\sigma$) shows a Pearson sign flip; Spearman remains stable at $-0.129$ on that cell, so the structural reversal claim is unaffected.

## Raw Data Source
- `results/phase_a_robustness/table_a2_reward_bias.json`
- `results/phase_a_robustness/table_a4_temperature.json`
- Harness: `experiments/p7_robustness_harness.py`

## Files
- `data.csv` — backbone, env, status, Spearman under raw / $\alpha U$ ($\alpha=-1$) / $\sigma^{0.5}$ / $\sigma^2$ / $\log\sigma$, Pearson under power transforms + log
- `generate.py` — regenerates data.csv + .tex from source JSONs
- `tab_phase_a_alternatives.tex` — LaTeX `\begin{table*}` for paper inclusion

## Reproducibility
```bash
python planning/writing/experiment/tab_phase_a_alternatives/generate.py
```
