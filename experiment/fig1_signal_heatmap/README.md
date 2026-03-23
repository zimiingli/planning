# fig1_signal_heatmap

## Paper Location

Section 3.1 Main text, Observation 1 (Direction Reversal).

## Description

8 env x N signals heatmap showing Spearman rho between signals and utility. Core evidence that the same signal (e.g., entropy) correlates in opposite directions across environments.

## Data Status

Complete. 8 environments covered. Data from step1_signal_discovery.json files.

## Data Source

- `results/phase6/{env}/{env}/step1_signal_discovery.json`
- Probe data from `results/phase1_signal_discovery/`
- Calibration data from `results/phase5/calibration_data/`

## Files in this folder

- `data.csv` -- Processed data for the heatmap.
- `fig1_signal_heatmap.pdf` -- Generated figure.
- Generation code: `planning/paper_figures/generate_all_figures.py::fig1_signal_heatmap()`
