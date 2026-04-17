# fig2_pareto

## Paper Location

Section 5.2 Main text, E2 Main Comparison. Figure fig:pareto.

## Writing Prompt
> **[FIGURE NEEDED: Figure fig:pareto]**
> Pareto frontier plot (ref: CATTS Figure 5).
> Layout: 2x3 grid (6 representative environments: HotpotQA, APPS Intro, WebShop, FEVER, Plancraft, APPS Interview).
> x-axis = Cost (rollouts/episode), y-axis = SR(%).
> Marker shapes by category: circle=bounds, triangle=fixed-direction, star=DIAL.
> Draw Pareto frontier as dashed line. DIAL in red/crimson with star marker.
> Key message: DIAL on or near Pareto frontier in every env.

## Description

SR vs Total Cost Pareto frontier for 6 main environments, showing all methods. DIAL sits on or near the Pareto frontier in most environments.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 203 rows). Phase 1 amortized cost included.
- Phi-3.5-mini: ✅ raw data complete — needs processing into Pareto format
- Llama-3.1-8B: ~94% — TWExpress CB partial

**See also `fig_full_pareto_8env/` for full 8-env appendix version.**

## Raw Data Source

- Qwen3: `results/phase6/path_e/{env}/*/seed_*/summary.json` + `results/phase5/competing_baselines/` + `results/phase6/new_baselines/`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/*/seed_*/summary.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/*/seed_*/summary.json`

## Files in this folder

- `data.csv` — Qwen3 Pareto data (environment, method, success_rate, avg_rollouts_per_ep)
- `fig2_pareto.pdf` — Generated figure
- `generate.py`
- `output.pdf`
