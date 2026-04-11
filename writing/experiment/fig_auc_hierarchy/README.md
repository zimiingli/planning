# fig_auc_hierarchy

## Paper Location

Section 3.1 Main text, Observation 3 (Signal Poverty).

## Description

Grouped bar chart showing AUC hierarchy: single entropy (approximately 0.50, random) to best single signal to multi-signal LR (0.85) to hidden state LR (0.89). Proves single-signal methods have an information-theoretic ceiling.

## Data Status

Complete. Data from phase5 probe experiments. Hardcoded from phase5_interim_report.md Section 4.5.4.

## Data Source

- Original probe data at `results/phase5/data/{hotpotqa,apps,webshop}/seed_42/step_data.npz`
- AUC computation via `scripts/phase5/auc_analysis.py`

## Files in this folder

- `data.csv`
- `fig_auc_hierarchy.pdf`
