# tab_winloss

## Paper Location

Section 5.2 Main text, alongside main results.

## Writing Prompt
> **[DATA NEEDED: Table tab:winloss]** Win/loss summary
> over all baseline-environment pairs. Rows = baselines, columns = number
> of environments where DIAL wins/ties/loses on SR and on Cost.

## Description

DIAL vs 6 CB methods win/loss summary. Qwen3 result: 34 wins, 2 losses across 38 comparisons. Only losses are HotpotQA vs AUQ and s1 (-1.8pp each, not statistically significant).

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 7 rows)
- Phi-3.5-mini: TODO — recompute from `tab_multi_backbone_results/` data
- Llama-3.1-8B: TODO — recompute after TWExpress CB complete

**Multi-backbone win/loss needs recomputation once full results available.**

## Raw Data Source

- Qwen3: Computed from `tab_main_results/data.csv`
- Phi/Llama: Compute from `tab_multi_backbone_results/data.csv`

## Files in this folder

- `data.csv` — Qwen3 win/loss (cb_method, dial_wins, dial_losses, n_envs)
- `generate.py`
- `output.pdf`
