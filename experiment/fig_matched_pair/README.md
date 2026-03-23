# fig_matched_pair

## Paper Location

Section 5.6 Main text, Robustness -- title-level evidence for "Same Signal, Opposite Meaning".

## Description

2x2 subplot showing Delta-U = U(high_entropy) - U(low_entropy) within difficulty-matched states. Blue bars (Delta-U < 0) = Type I environments, Red bars (Delta-U > 0) = Type D environments.

## Data Status

Complete with caveats. HotpotQA shows strong negative Delta-U (-0.08 to -0.43). TWExpress shows sign flip between strata. APPS Intv weakly positive (+0.026 at Easy only, utility too sparse at later steps). APPS near zero as expected.

## Data Source

Same probe data as fig_stratified_reversal:

- `results/phase1_signal_discovery/hotpotqa/phase1_signal_data.json` (1208 records)
- `results/phase5/calibration_data/{apps,webshop}/phase1_signal_data.json`
- `results/phase5/twexpress/twexpress/phase1_signal_data.json`
- `results/phase6/apps_interview/apps_interview/phase1_signal_data.json`

## Files in this folder

- `data.csv`
- `fig_matched_pair_opposite_meaning.pdf`
