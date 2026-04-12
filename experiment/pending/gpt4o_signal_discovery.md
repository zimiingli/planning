# GPT-4o / GPT-4o-mini Signal Discovery

## What
Run Step 0 (GO/NO-GO) and Step 1 (Signal Discovery) on a large API model to address Reviewer 3's concern that "larger models (70B+) might eliminate direction reversal." Only signal discovery needed -- no full Step 2.

## Models
- GPT-4o (or GPT-4o-mini as cost-effective alternative)

## Environments
All 8: hotpotqa, apps, webshop, fever, twexpress, plancraft, apps_interview, cruxeval

## Status
- [ ] Create config files with `api_type: "openai"` for all 8 envs
- [ ] Set up OpenAI API key
- [ ] Run Step 0 GO/NO-GO (can run locally, no GPU needed)
- [ ] Run Step 1 Signal Discovery (200 episodes per env)
- [ ] Collect rho values and compare with 3 existing backbones

## Implementation Note
Code already supports `api_type: "openai"` -- no GPU or SLURM needed. Can run locally. Main concern is API cost (~200 episodes x 8 envs x ~$0.01-0.05/episode = $16-80 estimated).

## Raw Data Location (when done)
```
results/review/gpt4o/{env}/{env}/
├── step0_go_nogo.json
├── step1_signal_discovery.json
└── phase1_signal_data.json
```

## Depends On
- OpenAI API key with sufficient credits
- `experiments/p5_new_env_experiments.py` with `--api-type openai` support

## Target experiment/ Folder
Data feeds into: `tab_multi_backbone_signal/` (adds 4th backbone column)
