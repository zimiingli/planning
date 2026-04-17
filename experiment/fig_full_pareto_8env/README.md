# fig_full_pareto_8env

## Paper Location
appendix.tex, line ~815. Appendix E (Computational Analysis), Figure A7.

## Writing Prompt
> **[FIGURE NEEDED: Figure A7]**
> Full Pareto frontier plot (all 8 environments).
> Layout: 2x4 grid. Same format as main-text fig:pareto but including APPS Interview and CRUXEval.
> Star for DIAL, triangle for baselines, circle for bounds, Pareto frontier dashed line.
> Key message: Pareto dominance holds across all 8 environments.

## Data Status
- Qwen3-4B: ✅ complete (extends fig2_pareto data)
- Phi-3.5-mini: ✅ raw data complete in results/review/
- Llama-3.1-8B: ✅ raw data mostly complete (TWExpress CB partial)

## Raw Data Source
- Qwen3: `results/phase6/path_e/{env}/*/seed_*/summary.json` + `results/phase5/competing_baselines/`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/*/seed_*/summary.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/*/seed_*/summary.json`

## Relation to fig2_pareto
This is the full 8-env version. `fig2_pareto/` shows 6 representative envs for main text.
Both share the same data pipeline; this one adds APPS Interview + CRUXEval panels.

## Files
- `data.csv` — TODO (extend fig2_pareto/data.csv with all 8 envs × 3 backbones)
- `generate.py` — TODO
- `output.pdf` — TODO
