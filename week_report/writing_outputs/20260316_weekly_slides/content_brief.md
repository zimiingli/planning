# Slides Content Brief — Weekly Update 2026-03-16

## Section 1: Theoretical Breakthrough

### Problem Recap: Direction Reversal
- token_entropy: HotpotQA ρ=-0.327 (negative) vs MBPP ρ=+0.153 (positive)
- step_count: MBPP ρ=+0.526 vs APPS ρ=-0.274 (sign flips)
- All fixed-direction methods fail systematically: Wrong-Direction LR -34.5pp, MLP -51.2pp

### Two-Source Uncertainty Model (NEW)
- High entropy has TWO semantic sources:
  - Type I (Information Poverty): agent lacks info → rollout cannot help → U low
  - Type D (Decision Difficulty): agent faces complex choice → rollout explores → U high
- Different environments have different Type I/D composition p_I(env):
  - HotpotQA (search, p_I high) → negative correlation
  - MBPP (coding, p_I low) → positive correlation
  - APPS (mixed, p_I mid) → near-zero correlation

### Three Testable Predictions — All Confirmed
- P1 (Temporal Shift): Early steps more negative ρ than late steps
  - HotpotQA: early ρ=-0.42 vs late ρ=-0.15 ✅
- P2 (Cross-Env Divergence): Greater task difference → greater ρ difference
  - |ρ_HotpotQA - ρ_MBPP| = 0.480 >> |ρ_APPS - ρ_MBPP| = 0.009 ✅
- P3 (Signal Identity): Type I envs' strongest signal = "information sufficiency"
  - HotpotQA → evidence_count (ρ=-0.586) ✅

### Cross-Env Transfer Matrix (Probe验证)
- Train\Eval | HotpotQA | APPS | WebShop
- HotpotQA   | 1.000    | 0.548| 0.174
- APPS        | 0.650    | 1.000| 0.269
- WebShop     | 0.470    | 0.330| 1.000
- Diagonal ≈ 1.0, off-diagonal 0.17-0.65 → validates theory

### Storyline Impact: v4.0 → v5.0
- v4.0: Finding paper (direction reversal is empirical observation)
- v5.0: Finding + Theory paper (direction reversal is explained by Two-Source Model)
- Paper type upgrade: observation → explanation

## Section 2: Experimental Results Overview

### Environment Matrix (4 Locked)
| Env | Domain | Base SR | Oracle SR | Headroom | Paper Role |
| HotpotQA | Multi-hop QA | 49.0% | 97.0% | +48pp | Pareto-dominate |
| WebShop | Web Shopping | 7.2% | 43.3% | +36pp | Pareto-dominate |
| APPS | Code Gen | 58.5% | 75.0% | +16.5pp | Weak-signal case |
| TWExpress | Text Adventure | 64.0% | 98.0% | +34pp | Rollout-safe case |

### Full Results (Main 3 Envs, Key Methods)
HotpotQA:
- SCG: 96.8% / 6.59×
- Principled Adaptive†: 96.9% / 6.49×
- CaTS: 93.2% / 10.60×
- always: 97.0% / 10.64×

APPS:
- Principled Adaptive†: 65.6% / 2.33×
- random_50: 66.8% / 2.65×
- CaTS: 59.0% / 1.02×
- SCG: 58.8% / 1.20×
- always: 64.5% / 4.30×

WebShop:
- SCG: 43.7% / 1.27×
- Principled Adaptive†: 43.3% / 1.90×
- CaTS: 30.5% / 3.44×
- always: 43.0% / 5.56×

### CAGC Ranking
1. SCG: 44.8% (Ours)
2. Principled Adaptive†: 28.6% (Ours)
3. CoRefine: 25.6%
4. CaTS: 25.0%
5. CATTS: 24.2%
6. SEAG: 23.5%

## Section 3: Principled-Adaptive Method

### Motivation
- SCG = handcrafted 5 features + LR + manual threshold
  - Needs domain knowledge
  - Weak-signal envs (APPS): SR ≈ base_only
- Need: automated feature selection + optimal threshold

### Architecture
1. Auto Feature Pool (15-30 candidates):
   - Type U (Universal, 10): step_count, token_entropy, response_length, etc.
   - Type E (Environment-specific, 5-20): auto-extracted from state_text
2. LASSO Feature Selection:
   - MI ranking → L1-regularized LR → top 5-10 features
3. Adaptive Threshold (key innovation):
   - Adaptive λ from data → CMDP-optimal threshold
   - pos_rate drives threshold: low pos_rate → high threshold → conservative

### Threshold Optimization Journey
| Version | Method | HotpotQA SR | APPS SR | Issue |
| nopca | Heuristic | 95.8% | 65.7% | APPS cost too high |
| auto | Fixed λ=0.05 | 68.2% | — | SR crash |
| adaptive | Adaptive λ | 96.9% | 65.6% | Best version |
| fbeta | F-beta | pending | pending | — |

### Results: Principled Adaptive vs SCG
| Env | SCG SR | SCG Cost | Adaptive SR | Adaptive Cost | ΔSR |
| HotpotQA | 96.8% | 6.59× | 96.9% | 6.49× | +0.1pp |
| APPS | 58.8% | 1.20× | 65.6% | 2.33× | +6.8pp |
| WebShop | 43.7% | 1.27× | 43.3% | 1.90× | -0.4pp |
| TWExpress | 97.0% | ~1.0× | 99.1% | 2.10× | +2.1pp |

### Dual-Method Narrative
- SCG: cost-efficient, best for strong-signal environments
- Principled: SR-first, best for weak-signal / no domain knowledge
- Complementary, not competing
