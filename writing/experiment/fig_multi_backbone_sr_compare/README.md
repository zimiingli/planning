# fig_multi_backbone_sr_compare

## Paper Location
appendix.tex, line ~474. Appendix C (Multi-Backbone Verification), Figure A5.

## Writing Prompt
> **[FIGURE NEEDED: Figure A5]**
> Cross-backbone SR comparison: DIAL vs. best fixed baseline.
> Layout: Grouped bar chart. x = 8 environments.
> 2 groups of 3 bars each:
> Group 1 (blue): best fixed-direction baseline SR on Qwen3/Phi-3.5/Llama-3.1.
> Group 2 (red): DIAL SR on Qwen3/Phi-3.5/Llama-3.1.
> Lighter shade = Qwen3, Medium = Phi-3.5, Darker = Llama.
> Annotate delta-SR between DIAL and fixed baseline per backbone.
> Sort by cross-backbone variation magnitude.
> Key message: Fixed baselines brittle across backbones; DIAL robust.

## Data Status
- Qwen3-4B: ✅ from existing tab_main_results
- Phi-3.5-mini: ✅ from results/review/ (all methods complete)
- Llama-3.1-8B: ~94% (TWExpress CB auq/cats/s1_budget missing)

## Raw Data Source
- Qwen3: `planning/experiment/tab_main_results/data.csv`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/*/seed_*/summary.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/*/seed_*/summary.json`
- Also: `planning/experiment/tab_multi_backbone_results/data.csv` (once generated)

## Files
- `data.csv` — TODO (from tab_multi_backbone_results)
- `generate.py` — TODO
- `output.pdf` — TODO
