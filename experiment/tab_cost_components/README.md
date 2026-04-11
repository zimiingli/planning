# tab_cost_components

## Paper Location
appendix.tex, line ~809. Appendix E (Computational Analysis), Table A3.

## Writing Prompt
> **[DATA NEEDED: Table A3]** Method x Cost component.
> Columns: Method, Phase-1 Episodes, Phase-1 Compute (GPU-hrs),
> Per-Step Overhead (ms), Gate Training Time, Total Cost for 500 Episodes.
> Shows EAAG's cost advantage: 50 exploration episodes, ~2 GPU-hrs,
> 0ms gate overhead, <1s training.

## Data Status
- Qwen3-4B: TODO (compute from runtime logs)
- Phi-3.5-mini: TODO
- Llama-3.1-8B: TODO

## Cost Model (from multi_backbone_experiment_plan.md)
| Method | Base proposer | Gate overhead/step | Rollout | Phase 1 |
|--------|:---:|:---:|:---:|:---:|
| base | 1/step | 0 | 0 | — |
| AT | 1/step | 0 | max | — |
| CATTS | 1/step | +K=5 | gated | optional |
| SEAG† | 1/step | 0 (reads logprob) | gated | required |
| CoRefine† | 1/step | 0 (reads entropy) | gated | required |
| CaTS† | 1/step | 0 (reads confidence) | gated | required |
| AUQ | 1/step | +1 (confidence query) | gated | optional |
| **EAAG** | 1/step | **0** | gated | 50 eps exploration |

## Raw Data Source
- Deployment rollouts: `results/{phase6,review}/{model}/{env}/*/seed_*/summary.json`
- Phase 1 runtime: SLURM job logs for Step 1 jobs
- Gate training: EAAG training logs (negligible)

## Files
- `data.csv` — TODO
- `generate.py` — TODO
- `output.pdf` — TODO
