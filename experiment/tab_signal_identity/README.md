# tab_signal_identity

## Paper Location
appendix.tex, line ~618. Appendix D.3 (Signal Identity Alignment, P3), Table A5.

## Writing Prompt
> **[DATA NEEDED: Table A5]** P3 Signal Identity Alignment.
> Columns: Environment, Dominant Type, Strongest Signal, |rho|,
> Signal Interpretation. Shows what each environment's strongest
> signal measures and how it aligns with the predicted type.

## Data Status
- Qwen3-4B: ✅ data exists in step1_signal_discovery.json + existing tab_signal_discovery
- This is an analytical table derived from existing signal discovery data

## Raw Data Source
- `planning/experiment/tab_signal_discovery/data.csv` (strongest signal per env)
- `results/phase6/{env}/{env}/step1_signal_discovery.json` (full correlation data)
- Signal interpretation is analytical (Type I = info sufficiency, Type D = decision complexity)

## Files
- `data.csv` — TODO: environment, dominant_type, strongest_signal, abs_rho, interpretation
- `generate.py` — TODO
- `output.pdf` — TODO
