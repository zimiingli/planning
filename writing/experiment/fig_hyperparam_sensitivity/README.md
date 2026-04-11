# fig_hyperparam_sensitivity

## Paper Location
appendix.tex, line ~870. Appendix F (Additional Analyses), Figure A2.

## Writing Prompt
> **[FIGURE NEEDED: Figure A2]**
> Hyperparameter sensitivity plots. Layout: 1x2 panels.
> Panel (a): Exploration budget sensitivity. x = N_explore in {10,20,30,50,100}, y = SR(%).
> 4 lines (HotpotQA, APPS Intro, FEVER, WebShop). Shaded stable zone for N>=30.
> Panel (b): Gate threshold sensitivity. x = tau in {0.3,0.4,0.5,0.6,0.7}, y = SR(%).
> Same 4 environments. Vertical dashed at defaults (N=50, tau=0.5).
> Key message: EAAG robust to both N_explore (stable for >=30) and tau (stable across 0.3-0.7).

## Data Status
- Panel (a) N_explore: **PENDING** — see `pending/exp4_budget_sensitivity.md`
- Panel (b) tau sweep: **PENDING** — see `pending/gate_threshold_sweep.md`
- Qwen3-4B budget sensitivity: already done (check results/phase6/)
- Phi/Llama budget sensitivity: not done

## Raw Data Source
- Panel (a): `results/review/{model}/budget_sensitivity/{env}/N{budget}/seed_{seed}/summary.json`
- Panel (b): `results/review/qwen3_4b/threshold_sensitivity/{env}/tau_{threshold}/seed_{seed}/summary.json`
- Qwen3 existing: `results/phase6/` (if budget sweep was done)

## Files
- `data.csv` — TODO
- `generate.py` — TODO
- `output.pdf` — TODO
