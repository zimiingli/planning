# fig_p1_temporal_shift

## Paper Location

Section 5.4 Main text, Theory Verification (Prediction P1).

## Description

Paired bar chart showing early vs late rho(entropy, U) across 5 environments. Tests whether entropy-utility correlation shifts with episode progress.

## Data Status

Complete with caveat. Pre-computed results for HotpotQA/APPS/WebShop from d1_temporal_shift_results.json. FEVER and TWExpress computed from raw probe data. Plancraft excluded (no suitable probe data). NOTE: Actual results show rho becomes MORE negative at late steps (opposite to original prediction). Paper narrative needs adjustment.

## Data Source

- `results/phase6/toy_model/d1_temporal_shift_results.json` (HotpotQA, APPS, WebShop)
- `results/phase6/fever/fever/phase1_signal_data.json` (282 records)
- `results/phase5/twexpress/twexpress/phase1_signal_data.json` (798 records)

## Files in this folder

- `data.csv`
- `fig_p1_temporal_shift.pdf`
