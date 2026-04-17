# tab_main_results

## Paper Location

Section 5.2 Main text. Main Comparison (core table).

## Writing Prompt
> **[DATA NEEDED: Table tab:main]** Main results table.
> Full method x environment grid. Rows = methods (base_only, always_trigger, oracle, CaTS, SEAG, CoRefine, CATTS, AUQ, s1_budget, BSW, DIAL).
> Columns = 8 environments, each with SR(%) and Cost (ro/ep). Bold best SR per env.
> Include +/- std if available. Add delta column showing SR improvement over base.

## Description

Main results table: 8 environments x all methods (bounds, CB baselines, ablations, DIAL). Shows SR (%) and Total Cost (ro/ep, including Phase 1 amortized cost for CaTS/SEAG/CoRefine/SCG). Phase 1 cost amortized at 200 ep always_trigger.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 89 rows)
- Phi-3.5-mini: ✅ raw data complete — see `tab_multi_backbone_results/` for full table
- Llama-3.1-8B: ~94% — TWExpress CB auq/cats/s1_budget missing

**Current data.csv contains Qwen3 only. Multi-backbone data in `tab_multi_backbone_results/`.**

## Raw Data Source

- Qwen3 DIAL/ablations: `results/phase6/path_e/{env}/*/seed_*/summary.json` (3 seeds averaged)
- Qwen3 CB baselines: `results/phase5/competing_baselines/` and `results/phase6/new_baselines/`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/*/seed_*/summary.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/*/seed_*/summary.json`

## Files in this folder

- `data.csv` — Qwen3-4B results (method, environment, sr_pct, cost_ro_per_ep)
- `generate.py` — generation script
- `output.pdf` — rendered table
