# fig3_bsw_direction

## Paper Location

Section 5.3 Main text, Ablation. Figure fig:direction-cost.

## Writing Prompt
> **[FIGURE NEEDED: Figure fig:direction-cost]**
> Cost of wrong direction scales with signal strength (ref: CATTS Figure 3).
> Layout: Single panel scatter. x = |rho| per env, y = BSW degradation (pp SR drop vs DIAL).
> Color by type: blue=Type I, red=Type D, gray=mixed. Dashed trend line with r value.
> Key message: Wrong direction more damaging when signal stronger. |rho|>0.3 => >15pp degradation.

## Description

Scatter plot showing BSW (wrong-direction) degradation vs signal strength. 5 environments with BSW data.

## Data Status

- Qwen3-4B: ✅ complete (data.csv, 6 rows)
- Phi-3.5-mini: could add Phi BSW data if available
- Llama-3.1-8B: could add Llama BSW data if available

**BSW ablation may only be for Qwen3 (main backbone). Check if BSW was run on Phi/Llama.**

## Raw Data Source

- BSW results: hardcoded from main experiment analysis
- Signal strength: from `tab_signal_discovery/data.csv`
- Also: `fig_bsw_vs_rho/` has a related scatter (BSW cost vs rho)

## Files in this folder

- `data.csv` — BSW scatter data
- `fig3_bsw_cost.pdf`
- `generate.py`
- `output.pdf`
