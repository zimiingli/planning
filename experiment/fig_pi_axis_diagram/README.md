# fig_pi_axis_diagram

## Paper Location
appendix.tex, line ~362. Appendix B.4 (Position on the pI Axis), Figure A1.

## Writing Prompt
> **[FIGURE NEEDED: Figure A1]**
> pI axis diagram: visual summary of the Two-Source Model.
> Layout: Single horizontal axis from pI=0 (Pure Type D) to pI=1 (Pure Type I).
> Vertical dashed line at reversal threshold pI*. Left region green (positive rho), right region red (negative rho).
> Each environment = labeled dot at estimated pI, size proportional to |rho|, color by rho sign.
> Style: TikZ, clean publication-quality number-line diagram.

## Data Status
- Qwen3-4B: data exists (from tab_signal_discovery and tab_env_info_structure)
- This is a conceptual/analytical diagram, not a data-heavy figure

## Raw Data Source
- `planning/experiment/tab_signal_discovery/data.csv` (rho values)
- `planning/experiment/tab_env_info_structure/data.csv` (pI estimates)

## Files
- `data.csv` — TODO (env, pI_estimate, rho, type)
- `generate.py` — TODO (TikZ or matplotlib)
- `output.pdf` — TODO
