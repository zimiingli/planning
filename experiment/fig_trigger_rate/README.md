# fig_trigger_rate

## Paper Location

Section 5.3 Main text, Ablation / Gate Behavior. Figure fig:trigger-adapt.

## Writing Prompt
> **[FIGURE NEEDED: Figure fig:trigger-adapt]**
> Environment-adaptive trigger behavior (ref: CATTS Figure 2).
> Layout: 2x3 grid, 6 environments. Each subplot: x = step index, y = trigger rate (%).
> Solid blue line with shaded 95% CI band. Horizontal dashed gray at 50%.
> Annotate overall RR in corner. Order by delta (rollout headroom).
> Key message: Trigger rate varies from 73% (TWExpress) to <20% late-step (Plancraft).

## Description

2x3 grid showing per-step trigger probability for EAAG (exploitation phase) across 6 environments.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 119 rows)
- Phi-3.5-mini: TODO — raw data exists in `results/review/phi35_mini/`
- Llama-3.1-8B: TODO — raw data exists in `results/review/llama31_8b/`

**Multi-backbone trigger rate comparison would strengthen the ablation story.**

## Raw Data Source

- Qwen3 decision logs: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/scg_se_online_decay_local_decision_log.json`
- Qwen3 episodes: same path, `episodes.json`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/se_few5_filter_local/seed_*/scg_*_decision_log.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/se_few5_filter_local/seed_*/scg_*_decision_log.json`

## Files in this folder

- `data.csv` — Qwen3 trigger rate data
- `fig_trigger_rate_by_step.pdf`
- `generate.py`
- `output.pdf`
