# tab_significance

## Paper Location

Appendix E. Statistical Significance.

## Description

Bootstrap delta-SR 95% CI for EAAG vs each CB method across 5 environments (30 comparisons). 18/30 significant. WebShop all significant (+8~+37pp). Plancraft mostly not significant.

## Data Status

Complete. Bootstrap with 5000 resamples, seed=42. FEVER excluded (no CB comparison data).

## Data Source

- EAAG episodes: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/episodes.json`
- CB baselines: `results/phase5/competing_baselines/` and `results/phase6/new_baselines/`

## Files in this folder

- `data.csv`
- `tab_significance.tex`
