# fig_trigger_rate

## Paper Location

Section 5.3 Main text, Ablation / Gate Behavior.

## Description

2x3 grid showing per-step trigger probability for EAAG (exploitation phase) across 6 environments. Each subplot shows how the gate adapts its triggering behavior to the environment.

## Data Status

Complete. Decision logs from 3 seeds x 6 environments. Step-count reconstructed from episodes.json.

Key findings:
- HotpotQA: early-high / late-low
- WebShop: step0=0.01, step1=0.83
- TWExpress: consistently high (0.73-0.90)
- Plancraft: decreasing (0.49 to 0.20)

## Data Source

- Decision logs: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/scg_se_online_decay_local_decision_log.json`
- Episodes: same path, `episodes.json`

## Files in this folder

- `data.csv`
- `fig_trigger_rate_by_step.pdf`
