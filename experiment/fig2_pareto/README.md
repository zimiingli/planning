# fig2_pareto

## Paper Location

Section 5.2 Main text, E2 Main Comparison.

## Description

SR vs Total Cost Pareto frontier for 4 main + 2 diagnostic environments, showing all methods. EAAG sits on or near the Pareto frontier in most environments.

## Data Status

Complete. All 6 environments x 10+ methods. Phase 1 amortized cost included for CaTS/SEAG/CoRefine/SCG.

## Data Source

- `results/phase6/path_e/{env}/*/seed_*/summary.json`
- `results/phase5/competing_baselines/{env}/*/seed_*/summary.json`
- `results/phase6/new_baselines/{env}/*/seed_*/summary.json`

## Files in this folder

- `data.csv` -- Processed data for the Pareto plot.
- `fig2_pareto.pdf` -- Generated figure.
