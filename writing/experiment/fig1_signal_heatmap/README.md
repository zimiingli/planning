# fig1_signal_heatmap

## Paper Location

Section 3.1 Main text, Observation 1 (Direction Reversal).

## Writing Prompt
Part of the signal discovery analysis. Main-text heatmap shows Qwen3 only.
Multi-backbone version: see `fig_multi_backbone_heatmap/` (Figure A4 in appendix).

## Description

8 env x N signals heatmap showing Spearman rho between signals and utility. Core evidence that the same signal (e.g., entropy) correlates in opposite directions across environments.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 43 rows)
- Phi-3.5-mini: ✅ data exists — see `tab_multi_backbone_signal/` for multi-backbone data
- Llama-3.1-8B: ✅ data exists — see `tab_multi_backbone_signal/` for multi-backbone data

**Main-text figure shows Qwen3 only. Appendix Figure A4 (`fig_multi_backbone_heatmap/`) shows all 3 backbones.**

## Raw Data Source

- Qwen3: `results/phase6/{env}/{env}/step1_signal_discovery.json`
- Probe data: `results/phase1_signal_discovery/`
- Calibration data: `results/phase5/calibration_data/`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/step1_signal_discovery.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/step1_signal_discovery.json`

## Files in this folder

- `data.csv` — Qwen3 signal heatmap data
- `fig1_signal_heatmap.pdf` — Generated figure
- `generate.py`
- `output.pdf`
