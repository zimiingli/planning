# fig6_fever_bias

## Paper Location

Section 6.2 Main text, Discussion (FEVER Case Study).

## Description

Analysis of why EAAG achieves only ~50% on FEVER despite oracle being 99.8%. Online exploration's random 50% skip at step 0 creates biased training data.

## Data Status

Complete. Compares SCG (Phase 1 data) vs EAAG (explore data) calibration statistics.

## Data Source

Hardcoded from Section 3.6 exploration bias analysis in implementation plan. Original data from FEVER probe runs.

## Files in this folder

- `data.csv` -- Processed data for the FEVER bias analysis.
- `fig6_fever_bias.pdf` -- Generated figure (PDF).
- `fig6_fever_bias.png` -- Generated figure (PNG).
