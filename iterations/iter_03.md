# Iteration 3: Experiments Section

## Targeted Section
- `sections/experiments.tex`

## Changes Made

### Setup
1. **Added Phase 1 requirements paragraph** (guide lines 860-867): Explains that CaTS/SEAG/CoRefine/SCG require 200 episodes of Phase 1 calibration data, while DIAL requires none. Clarifies the dagger notation and cost column scope.
2. **Enhanced env-setup table** (guide lines 877-891): Added % symbols to SR columns, expanded "APPS Intv." to "APPS Interview", expanded "$K$-variant" to "$K$-variant sampling" for clarity.

### Main Results  
3. **Added interpretation sentence to APPS Intro analysis** (guide lines 971-974): "This demonstrates that direction-aware gating naturally adapts to environment headroom."

### Extreme Environments
4. **Added concluding sentence** (guide lines 1150-1153): "These results confirm that DIAL adapts not only direction but *magnitude* of gating..."

### Theory Verification
5. **Expanded P1 with FEVER and TWExpress data** (guide lines 1070-1081): Added temporal dynamics data for FEVER (weak/non-significant) and TWExpress (significant early, vanishing late). Added the refined interpretation about $p_I$ reflecting residual gap between gathered info and task requirements.
6. **Expanded P2 with richer explanation** (guide line 1093): Added "FEVER has more early-step information poverty than HotpotQA."
7. **Expanded controlled information paragraph** (guide lines 1118-1128): Added sample size caveat, nuanced explanation for unexpected positive entropy sign in InfoPoor, and Observation 2 support reference.

### Robustness
8. **Expanded robustness intro** (guide lines 1166-1169): Added multi-backbone verification cross-reference showing direction depends on environment × model interaction.

## Rationale
The experiments section is the paper's strongest empirical evidence. These changes add crucial details for reviewer scrutiny: Phase 1 requirements clarify fair comparison, temporal dynamics for all environments strengthen P1 verification, and nuanced caveats for controlled experiments show intellectual honesty without undermining claims.
