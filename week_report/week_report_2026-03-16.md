# Weekly Report (2026-03-16)

**Project**: Direction-Aware Gate — Adaptive Test-Time Optimizer Triggering
**Target Venue**: NeurIPS 2026 (primary) / ICLR 2027 (backup)
**Paper Title**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Current Status**: Phase 6 Day 4 — Method Upgrade (Path E) complete, Threshold optimization iterating

### Terminology

| Abbrev. | Full Name | Meaning |
|---------|-----------|---------|
| **SR** | Success Rate | Task success rate |
| **RR** | Rollout Rate | Per-step rollout trigger probability |
| **CER** | Cost-Effectiveness Ratio | (SR - SR_base) / (Cost_normalized - 1) |
| **CAGC** | Cost-Adjusted Gap Closed | GapClosed% / Cost, comprehensive SR+Cost metric |
| **SCG** | Signal-Conditioned Gate | Our main method (handcrafted 5 features + LR) |
| **CACB** | Cost-Aware Contextual Bandit | Path E1 method (Thompson Sampling) |
| **Principled** | Principled SCG | Path E3 method (auto feature pool + LASSO + CMDP threshold) |
| **AdjSR** | Adjusted SR | SR - λ × (Cost - 1), penalizing excessive cost |

---

## 1. Executive Summary

This week marks the transition from **data collection + environment expansion** (Phase 5) to **method innovation + theory development** (Phase 6). Three major threads were executed in parallel:

1. **Theory Development (Path D)**: Two-Source Uncertainty Toy Model validated — all 3 testable predictions confirmed empirically. This upgrades the paper from "Finding paper" to "Finding + Theory paper".
2. **Method Upgrade (Path E)**: Three new method directions explored (CACB, Prototypical, Principled). **E3:Principled** emerged as the best — fully automated, no domain knowledge, APPS SR +7.4pp over handcrafted SCG.
3. **Hidden State Probe (Path B)**: Offline analysis successful (AUC 0.88-1.00), but end-to-end gate failed due to distribution shift. **Critical bug discovered and fixed** (hidden_state never passed to gate). Scientific analyses (cross-env transfer, layer-wise probing) completed and directly validate the Two-Source Model.

**Bottom Line**: Paper narrative upgraded to v5.0 (Finding + Theory + Method Evolution). Our two methods (SCG + Principled Adaptive) rank #1 and #2 in CAGC across all methods tested. NeurIPS acceptance estimate: 55-75%.

---

## 2. Paper Narrative Upgrade: v4.0 → v5.0

### 2.1 Core Change: From "Finding Paper" to "Finding + Theory Paper"

| Dimension | v4.0 (Last Week) | v5.0 (This Week) |
|-----------|------------------|-------------------|
| **Core hook** | Direction reversal (empirical) | Direction reversal + **why it reverses** (theory) |
| **Theory** | None | **Two-Source Uncertainty Model** |
| **Method story** | SCG-LR learns direction | SCG-LR → Principled SCG (handcrafted → automated) |
| **Probe positioning** | Independent method upgrade | Toy model empirical verification + scalability enabler |
| **Paper type** | Finding paper + simple method | Finding + Theory + Method Evolution |
| **Community takeaway** | "Direction needs to be learned" | "Signal semantics is a function of environment state composition" |
| **Environment count** | 3 validated + expansion ongoing | **4 locked** (HotpotQA, APPS, WebShop, TWExpress) |

### 2.2 Four-Layer Narrative (v5.0)

```
Layer A (Core — Highest Priority): Direction Reversal + Two-Source Theory
  "The same signal has opposite meaning across environments because high
   entropy reflects either information poverty (rollout cannot help) or
   decision difficulty (rollout explores alternatives)."

Layer B (Method — Second Priority): Manual Features → Principled Auto
  SCG-LR (handcrafted, cost-efficient) → Principled SCG (automated, SR-first)
  Two methods are complementary, not competing.

Layer C (Emergent Finding — Third Priority): Adaptive Behavior
  Gate trigger rate automatically aligns with rollout headroom.
  Not programmed — emerges from logistic regression on trajectory features.

Layer D (Framework — Fourth Priority): T-as-Parameter + Cost Efficiency
  Decouple: what optimizer (env-specific) / how to measure U / when to trigger.
```

---

## 3. Phase 6 Path Results

### 3.1 Path A: Data Completion — ✅ Done

| Task | Result |
|------|--------|
| TWExpress CB 12/12 | All competing baselines complete; positioned as "rollout-safe contrast case" |
| APPS Rerun 9/9 | **oracle=75.0%** (major finding: 16.2pp gap over SCG proves rollout signal exists but handcrafted features miss it) |
| Token Cost (6 envs) | All extracted: HotpotQA C_rollout=7,743; APPS C_rollout=3,306; WebShop C_rollout=9,089 |

### 3.2 Path B: Hidden State Probe — Offline ✅, End-to-End ❌

#### B1-B3: Offline Success

| Probe | HotpotQA AUC | APPS AUC | WebShop AUC |
|-------|:------------:|:--------:|:-----------:|
| P1 Linear Reg | 0.894 | 0.807 | 1.000 |
| P3 MLP Reg | **0.922** | 0.878 | 1.000 |
| Handcrafted LR | 1.000 | 0.981 | 1.000 |

All 3 envs GO (AUC >> 0.70).

#### B4: End-to-End Failure Chain

**Critical Bug Discovered**: `run_gated_episode()` never passed `hidden_state` to the gate. Gate fallback: `if hidden_state is None: return True` → 100% trigger. All prior "probe gate" results (B4v1, B4v2, B4v3r1) were actually `always_trigger` in disguise.

**After Bug Fix** (B4v3r2, first true probe gating):

| Env | Probe Adaptive SR | SCG SR | always SR |
|-----|:-----------------:|:------:|:---------:|
| HotpotQA | 60.7% | 96.8% | 97.0% |
| APPS | 63.7% | 58.8% | 64.5% |
| WebShop | 30.3% | 43.7% | 43.0% |

**Root cause**: Online hidden state prediction distribution shifts severely from offline training data. Threshold calibrated offline becomes useless online. Probe selects correctly on relative ranking but absolute threshold mismatches.

**Conclusion**: Hidden state probe as end-to-end gate is not viable. Repositioned for scientific analysis only.

#### B6: Scientific Analysis — ✅ Completed (Paper §4.5)

**B6.1 Layer-wise Probing**: WebShop AUC > 0.99 at all layers; HotpotQA/APPS AUC 0.79-0.85 across layers.

**B6.2 Cross-Env Transfer Matrix** — 🔥 Core Finding:

| Train \ Eval | HotpotQA | APPS | WebShop |
|:------------:|:--------:|:----:|:-------:|
| HotpotQA | **1.000** | 0.548 | 0.174 |
| APPS | 0.650 | **1.000** | 0.269 |
| WebShop | 0.470 | 0.330 | **1.000** |

Diagonal ≈ 1.0, off-diagonal 0.17-0.65 → **Directly validates Two-Source Model**: signal direction is environment-specific, probe weights don't transfer.

**B6.3 Learning Curve**: WebShop saturates at ~50 samples (AUC=0.985). Direction learning requires minimal data.

### 3.3 Path C: New Environment Candidates — ❌ All NO-GO

| Candidate | Test Date | Base SR | Always SR | Δ | Verdict |
|-----------|:---------:|:-------:|:---------:|:-:|:------:|
| ToolBench G1 | 3/13 | 94-98% | 94-98% | 0% | ❌ Too easy |
| ALFWorld | 3/7 | 28% | 30% | +2% | ❌ Δ insufficient |
| ScienceWorld | 3/7 | 0% | 0% | 0% | ❌ Model too weak |
| InterCode-bash | 3/7 | 100% | 100% | 0% | ❌ Already perfect |

**Cumulative**: 18 environments tested, 7 GO / 11 NO-GO. Paper environment set **locked at 4**.

### 3.4 Path D: Toy Model Verification — ✅ All Confirmed

**Two-Source Uncertainty Model**: High entropy has two semantic sources:
- **Type I (Information Poverty)**: Agent lacks information → rollout cannot help → U low
- **Type D (Decision Difficulty)**: Agent faces complex choice → rollout explores alternatives → U high

| Prediction | Status | Evidence |
|------------|:------:|---------|
| **P1**: Early steps (more Type I) have more negative ρ than late steps | ✅ Confirmed | HotpotQA early ρ=-0.42 vs late ρ=-0.15 |
| **P2**: Greater env task structure difference → greater ρ difference | ✅ Confirmed | \|ρ_HotpotQA - ρ_MBPP\| = 0.480 >> \|ρ_APPS - ρ_MBPP\| = 0.009 |
| **P3**: Type I-dominant envs' strongest signal measures "information sufficiency" | ✅ Confirmed | HotpotQA → evidence_count (ρ=-0.586) |

**Figures Generated**: Figure 2 (theoretical p_I vs ρ curve) + Figure 7 (early vs late ρ grouped bar chart).

### 3.5 Path E: Method Upgrade — ✅ Best Result: Principled SCG

Three new method directions tested (45 runs total):

#### Full Results (Exploitation-Only†, Fair Comparison)

**HotpotQA** (base=49.0%, oracle=97.0%)

| Method | SR | Cost (×base) |
|--------|:--:|:-----------:|
| **SCG (ours)** | **96.8%** | **6.59×** |
| E3:principled† | 96.7% | 8.05× |
| E2:proto† | 94.4% | 6.80× |
| CaTS | 93.2% | 10.60× |
| E1:cacb_A | 74.7% | 3.80× |

**APPS** (base=58.5%, oracle=75.0%)

| Method | SR | Cost (×base) |
|--------|:--:|:-----------:|
| **E3:principled†** | **66.2%** | 3.58× |
| E2:proto† | 65.6% | 3.37× |
| always_trigger | 64.5% | 4.25× |
| CaTS | 59.0% | 1.02× |
| SCG (ours) | 58.8% | 1.20× |

**WebShop** (base=7.2%, oracle=43.3%)

| Method | SR | Cost (×base) |
|--------|:--:|:-----------:|
| **SCG (ours)** | **43.7%** | **1.27×** |
| E3:principled† | 42.7% | 2.46× |
| E2:proto† | 39.8% | 3.69× |
| CaTS | 30.5% | 3.43× |
| E1:cacb_A | 26.7% | 1.57× |

† = exploitation-only (50ep exploration removed for fair comparison with SCG)

#### Key Findings

1. **E3:Principled is the best new method** — matches SCG on strong-signal envs (HotpotQA -0.1pp, WebShop -1.0pp), massively outperforms on weak-signal envs (APPS +7.4pp)
2. **E1:CACB (Thompson Sampling) disappointing** — high variance in HotpotQA, only marginal gain in APPS
3. **E2:Prototypical second-best** — natural threshold=0, strong in APPS (+6.8pp) but weaker in WebShop (-3.9pp)
4. **LASSO feature selection insight**: HotpotQA relies heavily on PCA features (67-90%), APPS 2/3 seeds use zero PCA → handcrafted features suffice for code environments

### 3.6 Threshold Optimization Iterations

The core bottleneck shifted from **ranking** (already excellent) to **threshold calibration**:

| Version | Threshold Method | Result |
|---------|-----------------|--------|
| nopca | Heuristic `λ×0.001/pos_rate` | APPS over-triggers (2.19 ro/ep) |
| auto | Fixed λ=0.05 sweep | HotpotQA SR crashes to 68.2% |
| **adaptive** | **Adaptive λ from data** | **✅ Best: HotpotQA 96.9%, APPS 65.6%, TWExpress 99.2%** |
| fbeta 🆕 | F-beta, β=sqrt(pos_rate/(1-pos_rate)) | ⬜ Pending (job 23185268) |

#### Principled Adaptive Complete Results (6 Environments)

| Environment | adaptive† SR | Cost† | SCG SR | SCG Cost | vs SCG |
|-------------|:----------:|:-----:|:------:|:--------:|:------:|
| **HotpotQA** | **96.9%** | **6.49×** | 96.8% | 6.59× | **+0.1pp** |
| **APPS** | **65.6%** | 2.33× | 58.8% | 1.20× | **+6.8pp** |
| WebShop | 43.3% | 1.90× | 43.7% | 1.27× | -0.4pp |
| **TWExpress** | **99.1%** | 2.10× | 97.0% | 1.00× | **+2.1pp** |
| BabyAI | 8.4% | 5.08× | 8.8% | 1.46× | -0.4pp |
| Plancraft | 21.8% | 5.08× | 21.5% | 3.31× | +0.3pp |

---

## 4. CAGC Ranking: Our Methods Take #1 and #2

| Rank | Method | Avg CAGC | Type |
|:----:|--------|:--------:|:----:|
| 1 | **SCG** | **44.8%** | **Ours** |
| 2 | **Principled Adaptive†** | **28.6%** | **Ours** |
| 3 | CoRefine | 25.6% | Competing Baseline |
| 4 | CaTS | 25.0% | Competing Baseline |
| 5 | CATTS | 24.2% | Competing Baseline |
| 6 | SEAG | 23.5% | Competing Baseline |

**Our two methods dominate ALL competing baselines on the comprehensive CAGC metric.**

---

## 5. Paper Environment Matrix (Locked)

| Environment | Paper Role | SCG | Principled Adaptive† | Best CB |
|-------------|-----------|:---:|:-------------------:|:-------:|
| **HotpotQA** | ✅ Pareto-dominate | 96.8% / 6.59× | 96.9% / 6.49× | CaTS 93.2% / 10.60× |
| **WebShop** | ✅ Pareto-dominate | 43.7% / 1.27× | 43.3% / 1.90× | CaTS 30.5% / 3.43× |
| **APPS** | ⚠️ Weak-signal diagnostic | 58.8% / 1.20× | **65.6%** / 2.33× | CaTS 59.0% / 1.02× |
| **TWExpress** | ⚠️ Rollout-safe contrast | 97.0% / ~1.0× | 99.1% / 2.10× | CATTS 97.5% |

**Dual-method narrative**: SCG = cost-efficient (best when signals are strong), Principled = SR-first (best when signals are weak or domain knowledge unavailable).

---

## 6. Deliverables Produced This Week

### Code

| File | Purpose |
|------|---------|
| `frvc/cacb_gate.py` | E1: Cost-Aware Contextual Bandit Gate |
| `frvc/contrastive_gate.py` | E2: Prototypical Networks Gate |
| `frvc/principled_scg.py` | E3: Principled SCG (auto feature + LASSO + CMDP) |
| `frvc/calibrated_probe_gate.py` | B4v2: 4 threshold calibration strategies |
| `frvc/probe_gate_v2.py` | B4v3: Offline + Adaptive RL gate |
| `experiments/p6_e_method_upgrade.py` | Path E unified experiment runner |
| `experiments/p6_b2_probe_training.py` | B2 probe training + B6 analysis |
| 7 sbatch scripts | Path E experiment orchestration |

### Figures & Data

| File | Content |
|------|---------|
| `results/phase6/figures/figure6_probe_analysis.pdf` | Three-panel: layer-wise + transfer heatmap + learning curve |
| `results/phase6/toy_model/figure2_*.pdf` | Two-Source Model theoretical curve |
| `results/phase6/toy_model/figure7_*.pdf` | Early vs late ρ grouped bar chart |
| `results/phase6/path_e/` | 45 run results (E1/E2/E3 × 3 envs × 3 seeds) |
| `results/phase6/hidden_states_multi/` | Multi-layer hidden states for 3 environments |

### SLURM Jobs Summary

| Job | Name | Tasks | Status |
|-----|------|:-----:|:------:|
| 23145097-101 | Token cost extraction (3 envs) | 3 | ✅ |
| 23148694 | ToolBench G1 Step 0 | 1 | ✅ NO-GO |
| 23151614 | B1 multi-layer hidden states | 3 | ✅ |
| 23166910 | B4v3r2 probe gate (bug-fixed) | 18 | ✅ |
| 23167005 | Path E main experiments | 45 | ✅ |
| 23175320 | Online ablation | 30 | ✅ |
| 23176360 | TWExpress online/nopca | 6 | ✅ |
| 23176425 | principled_auto | 18 | ✅ (SR crash issue) |
| 23179282 | principled_adaptive | 18 | ✅ (best version) |
| **23185268** | **principled_fbeta** | **18** | **⬜ Pending** |

---

## 7. Next Week Plan

### Priority Tasks

| Priority | Task | Expected Duration |
|:--------:|------|:-----------------:|
| **P0** | Analyze principled_fbeta results (job 23185268) | 1 day |
| **P0** | Finalize method positioning: SCG vs Principled Adaptive vs fbeta | 1 day |
| **P0** | Generate unified Pareto figure (all methods, 4 environments) | 1 day |
| **P1** | Begin LaTeX paper writing: §1 Introduction + §3 Two-Source Theory | 2-3 days |
| **P1** | Write §4 Method (dual method: SCG + Principled evolution) | 2 days |
| **P2** | Write §5 Experiments (Tables 1-2, Pareto figures, ablation) | 2-3 days |
| **P2** | Generate all paper figures (graphical abstract + 5-7 figures) | 2 days |
| **P3** | Phase 6 final report | 1 day |

### Key Milestones

- **By Tuesday (03-17)**: principled_fbeta analyzed, final method chosen
- **By Thursday (03-19)**: Paper §1 (Intro) + §3 (Theory) first draft
- **By Saturday (03-21)**: Paper §4 (Method) + §5 (Experiments) first draft

### Risk Items

| Risk | Impact | Mitigation |
|------|--------|-----------|
| principled_fbeta still over-triggers on Plancraft/BabyAI | Low (appendix envs) | Fallback: use adaptive version, note limitation |
| LaTeX compilation issues with complex figures | Medium | Pre-test figure integration early |
| NeurIPS deadline pressure (May 2026) | High | Start paper skeleton this week, iterate on sections |

### Open Questions for Paper

1. **Dual method vs single method**: Present SCG and Principled as two instantiations of the same framework, or as separate contributions?
2. **APPS positioning**: With Principled SR=65.6%, does APPS upgrade from "diagnostic case" to "partial Pareto-dominate"?
3. **Threshold story**: How much space to devote to threshold optimization journey (nopca → auto → adaptive → fbeta)?

---

## Appendix: Lessons Learned This Week

### A. Hidden State Bug (B4 Saga)

The most impactful debugging discovery this week: `run_gated_episode()` lacked `hf_engine` parameter, causing `hidden_state` to always be `None`, making the probe gate default to always-trigger. This invalidated **all prior probe end-to-end results** (B4v1, B4v2, B4v3r1, and even Phase 5's `hidden_state_mlp` comparison).

**Takeaway**: When a "new method" matches `always_trigger` exactly, always verify the method is actually being invoked.

### B. Offline-Online Distribution Shift

Even after fixing the bug, probe gate performs poorly (HotpotQA 60.7% vs SCG 96.8%) because:
- Offline probe is trained on saved `state_texts` with batch forward pass
- Online probe sees newly generated prompts with different token distributions
- Threshold calibrated offline becomes meaningless online

**Takeaway**: For hidden state methods, offline AUC is a necessary but far from sufficient condition for end-to-end success.

### C. Environment Expansion Saturation

18 environments tested, only 7 GO. The GO conditions (base SR 10-85%, Δ ≥ 3pp, reliable rollout) are harder to satisfy than expected. Most environments fail on model capacity floor (Qwen3-4B too weak) or ceiling effect (already perfect).

**Takeaway**: 4 diverse environments with different signal profiles is sufficient for the paper's claims. More environments would not strengthen the narrative.
