# fig_p1_temporal_shift

## Paper Location

Section 5.4 Main text, Theory Verification (Prediction P1). Figure fig:temporal-shift.
Also: appendix.tex line ~609, Table A4 (full data).

## Writing Prompt
> **[FIGURE NEEDED: Figure fig:temporal-shift]**
> P1 verification: temporal dynamics of rho.
> Layout: Single panel, grouped bar chart. x = environments, 2 bars per env (early=blue, late=red).
> y = rho(entropy, utility). Annotate delta = rho_late - rho_early above each pair.
> Horizontal dashed at rho=0. Key message: rho consistently shifts more negative from early to late.
>
> **[DATA NEEDED: Table A4]** P1 Temporal Dynamics full data.
> Columns: Environment, rho_early, rho_late, p_early, p_late. All 8 environments.

## Description

Paired bar chart showing early vs late rho(entropy, U) across environments. Tests whether entropy-utility correlation shifts with episode progress.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 11 rows)
- Phi-3.5-mini: TODO — could compute from `results/review/phi35_mini/{env}/{env}/phase1_signal_data.json`
- Llama-3.1-8B: TODO — could compute from `results/review/llama31_8b/{env}/{env}/phase1_signal_data.json`

**Multi-backbone temporal shift would strengthen P1 verification.**

## Raw Data Source

- Qwen3: `results/phase6/toy_model/d1_temporal_shift_results.json` (HotpotQA, APPS, WebShop)
- Qwen3 FEVER: `results/phase6/fever/fever/phase1_signal_data.json`
- Qwen3 TWExpress: `results/phase5/twexpress/twexpress/phase1_signal_data.json`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/phase1_signal_data.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/phase1_signal_data.json`

## Files in this folder

- `data.csv` — Qwen3 temporal shift data
- `fig_p1_temporal_shift.pdf`
- `generate.py`
- `output.pdf`
