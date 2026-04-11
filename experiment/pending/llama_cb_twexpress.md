# Llama-3.1-8B TWExpress Competing Baselines (Remaining)

## What
Complete the missing competing baseline methods for Llama-3.1-8B on TWExpress. Three methods are missing: auq, cats, s1_budget. Other methods (catts, seag, corefine) already completed.

## Missing Methods (verified 2026-04-11)
| Method | Status | Notes |
|--------|--------|-------|
| auq | missing | Should be straightforward |
| cats | missing | Needs Phase 1 calibration data |
| corefine | missing | Only catts+seag completed for CB† |
| s1_budget | missing | Fixed-budget, no calibration needed |

## Current Llama TWExpress Methods
Completed: always_trigger, base_only, catts, oracle, se_few5_filter_local, seag

## Status
- [ ] Check if sharded CB job 23750380 covered these methods
- [ ] If not, create targeted sbatch for auq/cats/s1_budget on TWExpress
- [ ] Submit jobs
- [ ] Verify 3 seeds each completed
- [ ] Merge with existing TWExpress data

## Raw Data Location (when done)
```
results/review/llama31_8b/twexpress/twexpress/
├── auq/seed_{42,123,456}/summary.json
├── cats/seed_{42,123,456}/summary.json
└── s1_budget/seed_{42,123,456}/summary.json
```

## Depends On
- SLURM job 23750380 (CB Llama TWExpress sharded) -- may already include these
- TWExpress environment requires `textworld-express` package in frvc_review env

## Target experiment/ Folder
Data feeds into: `tab_multi_backbone_results/` (completes Llama column)
