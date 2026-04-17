# Gate Threshold Sensitivity Sweep

## What
Test DIAL's robustness to the gate threshold parameter tau. Sweep tau in {0.3, 0.4, 0.5, 0.6, 0.7} on representative environments. This is Panel (b) of Figure A2 in the appendix.

## Models
- Qwen3-4B (primary, matches main paper)
- Optionally Phi-3.5 / Llama-3.1

## Environments
4 representative: HotpotQA, APPS Intro, FEVER, WebShop

## Experiment Matrix
4 envs x 5 thresholds x 3 seeds = 60 jobs (Qwen3 only)

## Status
- [ ] Determine how to override tau (CLI arg, env var, or config patch)
- [ ] Create sbatch script for threshold sweep
- [ ] Submit jobs
- [ ] Collect SR vs tau curves

## Implementation Note
The gate threshold is set in the DIAL method config. Need to either add `--gate-threshold` CLI arg to `p6_e_method_upgrade.py` or sed-patch the config file per job.

## Raw Data Location (when done)
```
results/review/qwen3_4b/threshold_sensitivity/{env}/tau_{threshold}/seed_{seed}/
└── summary.json
```

## Depends On
- `experiments/p6_e_method_upgrade.py` with threshold override support
- Existing Qwen3 configs as base

## Target experiment/ Folder
Data feeds into: `fig_hyperparam_sensitivity/` (Panel b: gate threshold)
