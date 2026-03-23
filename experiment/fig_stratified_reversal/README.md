# fig_stratified_reversal

## Paper Location

Section 5.6 Main text, Robustness of Direction Reversal.

## Description

Grouped bar chart showing rho(entropy, U) within step-count strata (Early/Mid/Late) across 5 environments. Proves direction reversal is not a trajectory-length artifact.

## Data Status

Complete. HotpotQA shows strongest evidence (all 3 strata negative: -0.18/-0.46/-0.42). TWExpress flips between strata. APPS Intv has NaN in Mid/Late (constant utility).

## Data Source

- `results/phase1_signal_discovery/hotpotqa/phase1_signal_data.json` (1208 records)
- `results/phase5/calibration_data/{apps,webshop}/phase1_signal_data.json`
- `results/phase5/twexpress/twexpress/phase1_signal_data.json`
- `results/phase6/apps_interview/apps_interview/phase1_signal_data.json`

## Files in this folder

- `data.csv`
- `fig_stratified_reversal.pdf`
