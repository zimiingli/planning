# Exp 3: Cross-Optimizer Verification

## What
Verify that signal direction is consistent across different optimizer types within the same environment. Run HotpotQA with K-variant rollout (instead of per-action) and APPS Interview with per-action rollout (instead of K-variant). If direction is robust, it should not depend on the optimizer choice.

## Models
- Phi-3.5-mini-instruct
- Llama-3.1-8B-Instruct

## Environments & Optimizer Swap
| Environment | Default Optimizer | Swapped Optimizer |
|-------------|------------------|-------------------|
| HotpotQA | Per-action eval | K-variant (num_variants=5) |
| APPS Interview | K-variant sampling | Per-action eval (num_chains=5) |

## Status
- [ ] Create config: `configs/review/phi35_mini_hotpotqa_kvariant.yaml`
- [ ] Create config: `configs/review/phi35_mini_apps_interview_peraction.yaml`
- [ ] Llama config `llama31_8b_hotpotqa_kvariant.yaml` already exists
- [ ] Create sbatch script for Phi cross-optimizer
- [ ] Llama sbatch `run_cross_optimizer_llama31.sbatch` already exists
- [ ] Submit Phi jobs (Step 0 + Step 1 only)
- [ ] Submit Llama jobs (Step 0 + Step 1 only)
- [ ] Collect results: compare rho direction with default optimizer

## Raw Data Location (when done)
```
results/review/{model}/cross_optimizer/
├── hotpotqa_kvariant/
│   ├── step0_go_nogo.json
│   ├── step1_signal_discovery.json
│   └── phase1_signal_data.json
└── apps_intv_peraction/
    ├── step0_go_nogo.json
    ├── step1_signal_discovery.json
    └── phase1_signal_data.json
```

## Depends On
- Existing configs as templates: `configs/review/phi35_mini_hotpotqa.yaml`, `configs/review/llama31_8b_hotpotqa_kvariant.yaml`
- vLLM server availability on HPC

## Target experiment/ Folder
Data feeds into: `tab_multi_backbone_signal/` (extends signal direction table with optimizer-variant rows)
