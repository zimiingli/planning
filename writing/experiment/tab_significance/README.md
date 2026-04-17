# tab_significance

## Paper Location

Appendix F. Statistical Significance. Table A8.

## Writing Prompt
> **[DATA NEEDED: Table A8]** Full statistical significance table.
> For each method x environment pair: delta-SR, 95% bootstrap CI,
> significant (Y/N). 48 cells total (6 baselines x 8 environments).

## Description

Bootstrap delta-SR 95% CI for DIAL vs each CB method. Qwen3: 18/30 significant across 5 environments. Bootstrap with 5000 resamples, seed=42.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 31 rows). FEVER excluded (no CB comparison data).
- Phi-3.5-mini: TODO — recompute with Phi DIAL vs Phi CB data
- Llama-3.1-8B: TODO — recompute after TWExpress CB complete

**Full Table A8 needs all 3 backbones x 8 envs x 6 baselines = 144 comparisons.**

## Raw Data Source

- Qwen3 DIAL episodes: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/episodes.json`
- Qwen3 CB baselines: `results/phase5/competing_baselines/` and `results/phase6/new_baselines/`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/*/seed_*/episodes.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/*/seed_*/episodes.json`

## Files in this folder

- `data.csv` — Qwen3 significance data
- `tab_significance.tex`
- `generate.py`
- `output.pdf`
