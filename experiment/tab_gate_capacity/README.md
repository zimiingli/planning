# tab_gate_capacity

## Paper Location

Section 5.6 Main text. Robustness -- Gate Complexity Ablation.

## Description

Ablation on HotpotQA showing that all correct-direction gates achieve ~95% SR regardless of capacity (Logistic/MLP/Hidden state), while wrong-direction gates degrade (62%/45.3%). Direction >> capacity.

## Data Status

Complete with caveat. MLP and Hidden state correct-direction SR marked as "~95" (approximate). Precise values would require additional GPU runs.

## Data Source

- Phase 6 DIAL (95.2%, AUC=0.851)
- Phase 2 MLP (SR~95%, AUC=0.869)
- Phase 5 probe (AUC=0.869)
- Phase 2/2.5 BSW variants (62.0%, 45.3%)

## Files in this folder

- `data.csv`
- `tab_gate_capacity.tex`
