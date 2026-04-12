# fig_multi_backbone_heatmap

## Paper Location
appendix.tex, line ~445. Appendix C (Multi-Backbone Verification), Figure A4.

## Writing Prompt
> **[FIGURE NEEDED: Figure A4]**
> Multi-backbone signal direction heatmap.
> Layout: 3 panels side by side (one per backbone: Qwen3-4B, Phi-3.5, Llama-3.1-8B).
> Each panel: rows = 8 environments, columns = key signals (step_count, token_entropy, etc.).
> Cell color = Spearman rho (red-white-blue diverging colormap).
> Same color scale across all 3 panels. Annotate rho values inside cells.
> Bold border on cells where sign flips across backbones.
> Key message: Entropy direction flips across backbones in 4/5 envs. Structural signals stable.

## Data Status
- Qwen3-4B: ✅ from `results/phase6/{env}/{env}/step1_signal_discovery.json`
- Phi-3.5-mini: ✅ from `results/review/phi35_mini/{env}/{env}/step1_signal_discovery.json`
- Llama-3.1-8B: ✅ from `results/review/llama31_8b/{env}/{env}/step1_signal_discovery.json`

## Raw Data Source
- Qwen3: `results/phase6/{env}/{env}/step1_signal_discovery.json`
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/step1_signal_discovery.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/step1_signal_discovery.json`
- Also: `planning/experiment/tab_multi_backbone_signal/data.csv` (once generated)

## Relation to fig1_signal_heatmap
`fig1_signal_heatmap/` shows Qwen3 only (main text). This is the 3-backbone appendix version.

## Files
- `data.csv` — TODO (from tab_multi_backbone_signal/data.csv)
- `generate.py` — TODO
- `output.pdf` — TODO
