# fig5_llm_ablation

## Paper Location

Section 5.3 Ablation / Appendix.

## Description

Bar chart comparing DIAL (with LLM features) vs principled_v2 (without LLM features). LLM contribution is marginal (<1pp) in most envs, except FEVER (+9.1pp).

## Data Status

Complete. 5 environments compared. LLM value is in zero-shot feature generation, not SR improvement.

## Data Source

- `results/phase6/path_e/{env}/se_online_decay_local/` -- DIAL (with LLM features)
- `results/phase6/path_e/{env}/principled_v2/` -- Without LLM features
- Comparison via `summary.json` in each.

## Files in this folder

- `data.csv` -- Processed data for the LLM ablation bar chart.
- `fig5_llm_ablation.pdf` -- Generated figure.
