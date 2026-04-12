# tab_signal_discovery

## Paper Location

Section 3.1 Main text, alongside fig1 signal heatmap.

## Writing Prompt
Part of the signal discovery narrative. Main-text Table 1 shows Qwen3 summary.
Multi-backbone extension: see `tab_multi_backbone_signal/` (Table A6 in appendix).

## Description

Summary table of signal discovery results across 8 environments: strongest signal, Spearman rho, entropy direction, entropy rho, and Two-Source type classification.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 9 rows)
- Phi-3.5-mini: ✅ step1 data exists for all 8 envs
- Llama-3.1-8B: ✅ step1 data exists for all 8 envs

**Multi-backbone signal data in `tab_multi_backbone_signal/`.**

## Multi-Backbone Key Finding
Signal direction depends on **environment x model interaction**, not environment alone:
- 3/5 envs with significant signals on both models: consistent sign (APPS, WebShop, APPS Intv)
- 2/5 inconsistent: HotpotQA (Llama -, Phi +), FEVER (Llama +, Phi -)

## Raw Data Source

- Qwen3: `results/phase6/{env}/{env}/step1_signal_discovery.json`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/step1_signal_discovery.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/step1_signal_discovery.json`

## Files in this folder

- `data.csv` — Qwen3 summary (environment, strongest_signal, rho, entropy_direction, entropy_rho, two_source_type)
- `generate.py`
- `output.pdf`
