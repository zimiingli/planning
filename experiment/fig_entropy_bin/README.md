# fig_entropy_bin

## Paper Location
experiments.tex, line ~143. Section 5.2 Main Results, cross-environment patterns.

## Writing Prompt
> **[FIGURE NEEDED: Figure fig:entropy-bin]**
> SR by entropy bin (ref: SEAG Figure 4 + CATTS Figure 4).
> Layout: 1x3 panels: (a) Type I (FEVER or HotpotQA), (b) Mixed (APPS Intro), (c) Type D (APPS Interview).
> Data: Bin steps by entropy into 4-5 bins, compute SR of EAAG/best-fixed/AT/base per bin.
> Grouped bar chart, annotate proportion of steps per bin.
> Key message: In Type I, EAAG maintains SR at high entropy while baselines degrade; in Type D, both improve but EAAG is more selective.

## Data Status
- Qwen3-4B: TODO (data exists in exploration logs, needs processing)
- Phi-3.5-mini: TODO
- Llama-3.1-8B: TODO

## Raw Data Source
- Qwen3: `results/phase6/path_e/{env}/se_few5_filter_local/seed_*/episodes.json` (per-step entropy + utility)
- Phi-3.5: `results/review/phi35_mini/{env}/{env}/se_few5_filter_local/seed_*/episodes.json`
- Llama-3.1: `results/review/llama31_8b/{env}/{env}/se_few5_filter_local/seed_*/episodes.json`
- Also need decision logs: `*_decision_log.json` for gate decisions

## Files
- `data.csv` — TODO
- `generate.py` — TODO
- `output.pdf` — TODO
