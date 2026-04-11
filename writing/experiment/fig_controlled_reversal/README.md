# Controlled InfoPoor/InfoRich Direction Reversal

## Paper Location
§5.4 Theory Verification (optional controlled experiment)

## Description
Controlled experiment manipulating information availability within HotpotQA to test whether signal-utility correlations change with information structure. InfoPoor limits search to first sentence only; InfoRich injects all gold evidence at episode start.

## Data Status
COMPLETE. Job 23304305 finished (8 tasks, all COMPLETED).

Key findings:
- **InfoRich** entropy ρ = +0.311 (vs Original −0.041) — confirmed: info-sufficient → positive ρ ✅
- **InfoPoor** entropy ρ = +0.119 — unexpected: predicted more negative, got weakly positive ❌
- **InfoPoor** step_count ρ = −0.608 (strongest) — info-poor makes step_count dominant ✅
- **InfoRich** step_count ρ = −0.147 (weakened) — info-rich makes step_count irrelevant ✅
- Signal hierarchy shifts (Obs 2 support): dominant signal changes from step_count to entropy as info increases

Interpretation: Results support **Signal Replacement** more than simple Direction Reversal. The experiment shows that information structure determines which signal dominates, not just the direction of a single signal.

## Data Source
- Step 0 + Step 1: `results/phase6/hotpotqa_{infopoor,inforich}/hotpotqa_{infopoor,inforich}/`
  - `step0_go_nogo.json` (base_sr, always_sr)
  - `step1_signal_discovery.json` (correlations)
  - `phase1_signal_data.json` (per-step probe data)
- EAAG: `results/phase6/path_e/hotpotqa_{infopoor,inforich}/se_online_decay_local/seed_{42,123,456}/summary.json`
- Code changes: `frvc/envs/hotpotqa_env.py` (variant parameter)
- Configs: `configs/phase6_hotpotqa_{infopoor,inforich}.yaml`
- Sbatch: `scripts/phase6/run_controlled_reversal.sbatch`
- GPU Job: 23304305 (8 tasks, all COMPLETED 2026-03-23)

## Files in this folder
- `README.md` — this file
- `data.csv` — summary data (3 variants × 7 columns)
- `generate.py` — figure generation script
- `output.pdf` — generated figure
