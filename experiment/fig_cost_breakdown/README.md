# fig_cost_breakdown

## Paper Location
appendix.tex, line ~832. Appendix E (Computational Analysis), Figure A8.

## Writing Prompt
> **[FIGURE NEEDED: Figure A8]**
> Computational cost breakdown (ref: CoRefine Table 2 token efficiency).
> Layout: Stacked bar chart. x = methods (EAAG, CaTS, SEAG, CoRefine, CATTS, AUQ, s1).
> y = total compute (GPU-hours for 500 episodes).
> Stacked components: dark = calibration/exploration overhead, light = deployment rollouts.
> EAAG highlighted with red border. Sort by total cost ascending.
> Key message: EAAG's 50-episode exploration overhead <= calibration overhead of other methods.

## Data Status
- Qwen3-4B: TODO (compute from summary.json run times + Phase 1 overhead)
- Phi-3.5-mini: TODO
- Llama-3.1-8B: TODO

## Raw Data Source
- Per-method deployment cost: `results/{phase6,review}/{model}/{env}/*/seed_*/summary.json` → rollouts_per_ep field
- Phase 1 overhead: 200 episodes × AT runtime (from Step 1 jobs)
- Gate training time: negligible (<1s, from EAAG training logs)
- Per-step overhead: CATTS K=5 calls, AUQ 1 call, others 0

## Relation to tab_cost_components
This figure visualizes the data from `tab_cost_components/`. Generate the table first.

## Files
- `data.csv` — TODO
- `generate.py` — TODO
- `output.pdf` — TODO
