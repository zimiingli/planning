# tab_main_results

## Paper Location

Section 5.2 Main text. Main Comparison (core table).

## Description

Main results table: 4 primary environments x all methods (bounds, CB baselines, ablations, EAAG). Shows SR (%) and Total Cost (ro/ep, including Phase 1 amortized cost for CaTS/SEAG/CoRefine/SCG). FEVER EAAG SR is 49.8% (limited by exploration bias, discussed in Section 6.2). Phase 1 cost amortized at 200 ep always_trigger.

## Data Status

Complete.

## Data Source

- EAAG and ablations: `results/phase6/path_e/{env}/*/seed_*/summary.json` (3 seeds averaged).
- CB baselines: `results/phase5/competing_baselines/` and `results/phase6/new_baselines/`.

## Files in this folder

- `data.csv`
