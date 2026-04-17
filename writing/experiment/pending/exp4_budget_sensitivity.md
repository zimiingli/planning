# Exp 4: Budget Sensitivity (Exploration Budget N_explore)

## What
Test DIAL's robustness to the exploration budget parameter N_explore. Sweep N_explore in {10, 20, 30, 50, 100} on two environments with strong signals, using DIAL (se_few5_filter_local) method only.

## Models
- Phi-3.5-mini-instruct
- Llama-3.1-8B-Instruct

## Environments
- HotpotQA (strong negative rho on Qwen3)
- FEVER (strong negative rho on Qwen3)

## Experiment Matrix
2 envs x 5 budgets x 3 seeds = 30 jobs per model, 60 total.

| N_explore | HotpotQA | FEVER |
|-----------|----------|-------|
| 10 | 3 seeds | 3 seeds |
| 20 | 3 seeds | 3 seeds |
| 30 | 3 seeds | 3 seeds |
| 50 (default) | 3 seeds | 3 seeds |
| 100 | 3 seeds | 3 seeds |

## Status
- [ ] Create budget sensitivity sbatch for Phi: `scripts/review/run_budget_sensitivity_phi35.sbatch`
- [ ] Llama sbatch `run_budget_sensitivity_llama31.sbatch` already exists
- [ ] Submit Phi jobs
- [ ] Submit Llama jobs
- [ ] Collect results: SR vs N_explore curves

## Implementation Note
Override `min_cal_points` via sed-patch on temp config (same pattern as port injection in existing scripts). Array mapping: env_idx = IDX/15, budget_idx = (IDX%15)/3, seed_idx = IDX%3.

## Raw Data Location (when done)
```
results/review/{model}/budget_sensitivity/{env}/N{budget}/seed_{seed}/
└── summary.json
```

## Depends On
- Existing sbatch template: `scripts/review/run_budget_sensitivity_llama31.sbatch`
- DIAL pipeline code: `experiments/p6_e_method_upgrade.py`

## Target experiment/ Folder
Data feeds into: `fig_hyperparam_sensitivity/` (Panel a: exploration budget)
