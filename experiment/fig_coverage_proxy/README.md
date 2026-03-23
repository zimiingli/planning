# fig_coverage_proxy

## Paper Location

Section 5.4 / Appendix D, Two-Source Model Empirical Grounding.

## Description

Scatter plot of mean information coverage (observable proxy for latent p_I) vs rho(entropy, U). Tests whether info-poor environments have more negative rho.

## Data Status

Complete with caveat. Trend r=-0.62. TWExpress is an outlier (high coverage=0.92 but negative rho=-0.29) because step_count/max_steps is a poor coverage proxy for text adventure games.

## Data Source

Coverage computed from probe data fields:

- HotpotQA: evidence_count / 3
- FEVER: step_count / 7
- WebShop: num_available_actions / 30
- TWExpress: step_count / 9
- APPS / APPS Intv: constant 1.0

## Files in this folder

- `data.csv`
- `fig_coverage_vs_rho.pdf`
