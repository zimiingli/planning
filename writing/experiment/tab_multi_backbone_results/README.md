# tab_multi_backbone_results

## Paper Location
appendix.tex, line ~440. Appendix C (Multi-Backbone Verification), Table A7.

## Writing Prompt
> **[DATA NEEDED: Table A7]** Cross-backbone baseline results.
> Methods x environments for Phi-3.5 and Llama-3.1 backbones.
> Shows that the same baselines that work on Qwen3 fail on other backbones,
> while DIAL adapts successfully.

## Data Status
- Qwen3-4B: ✅ from existing tab_main_results
- Phi-3.5-mini: ✅ 240/240 jobs complete
- Llama-3.1-8B: ~94% (226/240, missing auq/cats/s1_budget on TWExpress)

**See `pending/llama_cb_twexpress.md` for remaining Llama jobs.**

## Key Results (from multi_backbone_experiment_plan.md)

### Phi-3.5-mini Complete
| Env | base | AT | CATTS | SEAG† | CoRef† | CaTS† | AUQ | s1Bgt | **DIAL** |
|-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| HotpotQA | 28.3% | 98.8% | 42.0% | 88.3% | 87.7% | 68.3% | 31.2% | 94.2% | **92.3%** |
| APPS | 59.0% | 75.0% | 28.0% | 30.0% | 30.3% | 35.8% | 27.3% | 36.2% | 37.2% |
| WebShop | 3.5% | 53.5% | 28.7% | 36.5% | 35.8% | 41.7% | 7.0% | 3.0% | **57.3%** |
| FEVER | 7.2% | 61.0% | 12.7% | 13.5% | 13.7% | 19.8% | 8.5% | 23.0% | 16.5% |
| TWExpress | 66.7% | 97.8% | 86.7% | 94.5% | 94.7% | 68.2% | 94.5% | 95.7% | **96.7%** |
| Plancraft | 13.7% | 14.5% | 13.5% | 14.7% | 15.2% | 13.5% | 12.7% | 13.7% | 13.8% |
| APPS Intv | 27.0% | 79.5% | 27.7% | 27.8% | 28.5% | 30.5% | 27.2% | 34.5% | **36.8%** |
| CRUXEval | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% |

### Llama-3.1-8B DIAL
| Env | base | AT | **DIAL** | delta |
|-----|:---:|:---:|:---:|:---:|
| HotpotQA | 46.3% | 99.5% | **95.5%** | +49.2pp |
| APPS | 53.3% | 75.0% | 55.0% | +1.7pp |
| WebShop | 1.2% | 42.8% | **41.7%** | +40.5pp |
| FEVER | 13.2% | 62.8% | 34.7% | +21.5pp |
| TWExpress | 36.5% | — | **94.8%** | +58.3pp |
| Plancraft | 31.7% | 18.7% | 27.0% | -4.7pp |
| APPS Intv | 60.2% | 79.5% | 59.7% | -0.5pp |
| CRUXEval | 99.0% | 99.5% | 99.3% | +0.3pp |

## Raw Data Source
- Qwen3: `results/phase6/path_e/{env}/*/seed_*/summary.json` + `results/phase5/competing_baselines/`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/*/seed_*/summary.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/*/seed_*/summary.json`

## Files
- `data.csv` — TODO: backbone, environment, method, sr_pct, cost_ro_per_ep
- `generate.py` — TODO
- `output.pdf` — TODO
