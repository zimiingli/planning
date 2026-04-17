# fig4_feature_heatmap

## Paper Location

Section 3.1 Main text, Observation 2 (Signal Replacement).

## Description

Binary heatmap showing which features LASSO selected in each environment. step_count is selected in 6/7 envs (most universal), while LLM features dominate in WebShop and TWExpress.

## Data Status

Complete. 7 environments with selected features from DIAL gate_pattern.

## Data Source

Hardcoded from DIAL LASSO results (Section 3.1 in implementation plan).

## Files in this folder

- `data.csv` -- Processed data for the feature heatmap.
- `fig4_feature_heatmap.pdf` -- Generated figure.
