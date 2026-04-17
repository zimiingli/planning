# tab_prompt_template

## Paper Location
appendix.tex, line ~927. Appendix E.3 (LLM Reasoning Prompts), no table number.

## Writing Prompt
> **[DATA NEEDED]** Full LLM prompt template used in the Reason step of DIAL.
> Include one complete example showing:
> (1) the prompt given to the LLM with exploration data summary,
> (2) the LLM's full output including environment profile and feature hypotheses,
> (3) which features LASSO subsequently selected.
> Use WebShop as the example (most interesting LLM contribution).
> Important for reproducibility (NeurIPS checklist item).

## Data Status
- Prompt template: TODO (extract from code)
- WebShop example: TODO (extract from experiment logs)

## Raw Data Source
- Prompt template: `experiments/p6_e_method_upgrade.py` or `src/` code (LLM reasoning module)
- WebShop example output: check `results/phase6/webshop/webshop/se_few5_filter_local/` for LLM logs

## Files
- `prompt_template.txt` — TODO (full template)
- `webshop_example.md` — TODO (complete input/output example)
