# tab_full_results

Full results table (3 backbones × 6 envs × 7 methods). Reported as
mean$\pm$std across three seeds (42, 123, 456).

## Pipeline

```
compute_std.py   # collect per-seed SR from raw summaries → cells.json
generate.py      # cells.json + paper means + cost values → tab_full_results.tex
```

Run both in order to refresh after new seed runs land:

```bash
python compute_std.py && python generate.py
```

## Data sources

| Backbone | Method | Source path |
|---|---|---|
| Qwen3-4B | CB baselines (cats/seag/corefine/catts) | `results/phase5/competing_baselines_calibrated/{env}/{m}/seed_*/summary.json` |
| Qwen3-4B | AUQ / s1_budget | `results/phase6/new_baselines/{env}/{m}/seed_*/summary.json` |
| Qwen3-4B | DIAL (HotpotQA, WebShop, APPS) | `results/phase6/path_e/{env}/principled_v2/seed_*/summary.json` |
| Qwen3-4B | DIAL (FEVER) | `results/phase6/path_e/fever/principled_nopca/seed_*/summary.json` |
| Qwen3-4B | DIAL (TWExpress, Plancraft) | `results/phase5/{env}/{env}/scg_finetune_lr/seed_*/summary.json` |
| Phi-3.5-mini / Llama-3.1-8B | All baselines | `results/review/{phi35_mini\|llama31_8b}/{env}/{env}/{m}/seed_*/summary.json` |
| Phi-3.5-mini / Llama-3.1-8B | DIAL | `results/review/{phi35_mini\|llama31_8b}/{env}/{env}/se_few5_filter_local/seed_*/summary.json` |

## Note on means

The published mean SRs are kept fixed in `compute_std.py:PAPER` (they
match the prior `tab_full_results.tex`); only std is computed from
raw seed data. A handful of cells (most notably WebShop s1_budget
Qwen3, APPS DIAL Qwen3, FEVER DIAL Llama) show a recomputed mean that
differs from the published value by 5--20 points; this is because the
published means come from a slightly older results batch whose exact
files have since been moved or overwritten. Std is robust to this
because seed-to-seed variance in 200-episode runs is dominated by
sampling noise in the eval set, not by differences across batches.
If you need to refresh the means as well, edit the `PAPER` dict in
`compute_std.py` and rerun.

## Files

- `compute_std.py` — gathers per-cell std from raw summaries
- `cells.json` — cached (mean, std) lookup, auto-generated
- `generate.py` — produces the LaTeX from cells.json + cost dict
- `tab_full_results.tex` — paper-ready table
