# tab_multi_backbone_signal

## Paper Location
appendix.tex, line ~429. Appendix C (Multi-Backbone Verification), Table A6.

## Writing Prompt
> **[DATA NEEDED: Table A6]** Full multi-backbone results.
> 8 environments x 3 backbones x multiple signals.
> Extends Table 1 in main text with all signal types, not just entropy.
> Shows that step_count direction is stable while entropy flips.

## Data Status
- Qwen3-4B: ✅ step1_signal_discovery.json for all 8 envs
- Phi-3.5-mini: ✅ step1_signal_discovery.json for all 8 envs
- Llama-3.1-8B: ✅ step1_signal_discovery.json for all 8 envs

**All raw data exists. CSV extraction needed.**

## Key Results (from multi_backbone_experiment_plan.md)

| Environment | Llama-3.1-8B | Phi-3.5-mini | Qwen3-4B |
|-------------|:---:|:---:|:---:|
| HotpotQA | -0.346* | +0.184* | -0.041 |
| APPS | -0.242* | -0.129* | +0.012 |
| APPS Interview | -0.249* | -0.024 (ns) | +0.317* |
| FEVER | +0.428* | -0.156* | -0.119* |
| WebShop | +0.287* | +0.335* | -0.019 |
| Plancraft | -0.176* | 0.000 (ns) | -0.016 |
| TWExpress | 0.000 | 0.000 | -0.290* |
| CRUXEval | -0.045 (ns) | -0.065 (ns) | -0.048 |

## Raw Data Source
- Qwen3: `results/phase6/{env}/{env}/step1_signal_discovery.json`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/step1_signal_discovery.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/step1_signal_discovery.json`

## Files
- `data.csv` — TODO: backbone, environment, signal, rho, p_value, significant
- `generate.py` — TODO
- `output.pdf` — TODO
