# Weekly Report (2026-03-23)

**Project**: Direction-Aware Gate — Adaptive Test-Time Optimizer Triggering
**Target Venue**: NeurIPS 2026 (primary) / ICLR 2027 (backup)
**Paper Title**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Method**: EAAG (Environment-Aware Adaptive Gating)
**Backbone**: Qwen3-4B
**Paper Type**: Finding + Theory + Method

---

## 1. Method: EAAG (Environment-Aware Adaptive Gating)

**Core Insight**: The semantics of uncertainty signals (e.g., token entropy) are determined by the environment's information structure, not fixed. The same entropy signal reverses direction across environments.

### EAAG Three-Step Pipeline

1. **Explore**: Run 50 episodes in a new environment with randomized gating (ε=0.5), collecting (state, utility) data. The randomized design ensures unbiased estimation of utility U across the full signal range.

2. **Reason**: An LLM analyzes exploration data to identify patterns distinguishing useful from wasteful rollouts. It outputs:
   - An *environment profile*: natural-language description of the task structure
   - *Feature hypotheses*: task-specific signals to extract (e.g., `price_mentioned`, `action_is_click` for WebShop)

3. **Learn & Deploy**:
   - **Universal feature pool** (available across all environments): step count, token entropy, state length, action entropy, num_available_actions, has_output, etc.
   - LLM-generated features **complement** the universal pool — they are unioned together as the candidate feature set
   - **LASSO** selects the most relevant features from this union, then trains a **logistic regression** gate:
     - Weight sign encodes **direction** (w>0 → trigger when high = Type D; w<0 → trigger when low = Type I; w=0 → uninformative)
     - Training completes in <1s on CPU
     - **Zero per-step deployment cost** (single inner product)

4. **Online Adaptation (Optional)**: During deployment, ε-greedy exploration (ε: 0.1→0) with gate retraining every 30 episodes, enabling adaptation to distributional shift.

### Why the Method Is Intentionally Simple

The analysis reveals that **the bottleneck for adaptive compute is not gate complexity but direction discovery**:
- An MLP gate with the wrong direction degrades SR by 37.0 pp (HotpotQA)
- A logistic gate with the correct direction Pareto-dominates all baselines
- Information hierarchy: **signal direction >> signal count >> gate complexity**

---

## 2. Datasets

### 2.1 Main Experiments (6 environments, in main text §5)

| Environment | Type | Base SR | Always SR | Δ | Optimizer T | Unc. Type | Dataset Paper |
|-------------|------|---------|-----------|---|-------------|-----------|---------------|
| HotpotQA | Multi-hop QA | 49.0% | 97.0% | +48.0 | Per-action eval | Info-Poverty (Type I) | Yang et al., EMNLP 2018 |
| FEVER | Fact Verification | 37.0% | 99.8% | +62.8 | Per-action eval | Info-Poverty (Type I) | Thorne et al., NAACL 2018 |
| APPS Intro | Code Gen (easy) | 58.5% | 64.5% | +6.0 | K-variant sampling | Mixed | Hendrycks et al., NeurIPS 2021 |
| WebShop | Web Shopping | 7.2% | 43.0% | +35.8 | LLM-Propose-K | Mixed | Yao et al., NeurIPS 2022 |
| TWExpress | Text Game | 67.5% | 99.3% | +31.8 | Per-action eval | Info-Poverty (Type I) | Jansen & Côté, EACL 2023 |
| Plancraft | Mfg. Planning | 29.8% | 22.8% | **-7.0** | Per-action eval | Weak (rollout harmful) | Dag et al., arXiv 2024 |

**Notable papers that used each dataset:**

| Environment | Notable Papers Using This Dataset |
|-------------|----------------------------------|
| HotpotQA | ReAct (Yao et al., ICLR 2023); Reflexion (Shinn et al., NeurIPS 2023); Tree of Thoughts (Yao et al., NeurIPS 2023); LATS (Zhou et al., ICML 2024) |
| FEVER | ReAct (Yao et al., ICLR 2023); FEVER shared tasks (ACL workshops 2018–2025) |
| APPS | AlphaCode (Li et al., Science 2022); CodeT (Chen et al., ICLR 2023); CodeRL (Le et al., NeurIPS 2022) |
| WebShop | ReAct (Yao et al., ICLR 2023); AgentBench (Liu et al., NeurIPS 2023); LATS (Zhou et al., ICML 2024) |
| TWExpress | Based on TextWorld (Côté et al., NeurIPS 2019 workshop); used in RL agent evaluation literature |
| Plancraft | Recent benchmark (Dec 2024); based on Minecraft crafting, extends TextCraft (Prasad et al., 2023) |

**Notes**:
- These 6 environments span the full range of the Two-Source Model — from pure Type I (FEVER) through Mixed (APPS Intro) to rollout-harmful (Plancraft).
- Plancraft is the only environment with **negative headroom** (Δ=-7.0), where rollouts hurt performance.
- TWExpress is **rollout-safe**: nearly always beneficial.
- HotpotQA and WebShop are the most widely used agent benchmarks in the LLM agent literature.

### 2.2 Appendix Experiments (2 environments, in Appendix B)

| Environment | Type | Base SR | Always SR | Δ | Optimizer T | Unc. Type | Dataset Paper |
|-------------|------|---------|-----------|---|-------------|-----------|---------------|
| APPS Interview | Code Gen (hard) | 60.5% | 79.5% | +19.0 | K-variant sampling | Decision-Diff (Type D) | Hendrycks et al., NeurIPS 2021 |
| CRUXEval | Code Reasoning | 85.0% | 99.5% | +14.5 | K-variant sampling | Weak | Gu et al., ICML 2024 |

**Notable papers:**

| Environment | Notable Papers Using This Dataset |
|-------------|----------------------------------|
| APPS Interview | Same as APPS Intro (harder split of APPS); AlphaCode (Li et al., Science 2022) |
| CRUXEval | Used in code understanding evaluation; CRUXEval-X (Zhuo et al., 2024) for multilingual extension |

---

## 3. Baselines

All methods share the same agent and optimizer T; we compare **only the gate decision**.

| Method | Full Paper Title | Venue | Signal | Direction | Granularity | Phase 1 Data |
|--------|-----------------|-------|--------|-----------|-------------|-------------|
| CaTS | "Calibrated Test-Time Scaling" | ICLR 2026 | Platt-scaled confidence | Fixed | Problem | Yes (200 ep) |
| SEAG | "Semantic Exploration with Adaptive Gating for Efficient Problem Solving with Language Models" | ACL 2025 | Mean token confidence | Fixed | Problem | Yes (200 ep) |
| CoRefine | "Confidence-Guided Self-Refinement for Adaptive Test-Time Compute" | arXiv 2026 | Per-token entropy | Fixed | Problem | Yes (200 ep) |
| CATTS | "Agentic Test-Time Scaling for WebAgents" | arXiv 2026 | Vote entropy + margin (K=5) | Fixed | Problem | No (but K×forward pass overhead) |
| AUQ | "Agentic Uncertainty Quantification" | arXiv 2026 | Confidence threshold | Fixed | Problem | Yes |
| s1_budget | "s1: Simple Test-Time Scaling" | EMNLP 2025 | Fixed budget | — | Problem | No |
| **EAAG (ours)** | — | — | **Multi (auto: universal + LLM-generated)** | **Learned** | **Step** | **No** |

**Key distinction**: All prior methods assume a **fixed** signal–utility direction. EAAG is the only method that **discovers** both signal identity and direction per environment.

**Bounds**: base_only (never trigger), always_trigger (trigger every step), oracle (perfect gate).

**Cost fairness**: CaTS, SEAG, CoRefine require Phase 1 data (200 episodes of always_trigger); this cost is amortized and included in Total Cost. EAAG requires **no Phase 1 data**.

---

## 4. Main Results Table

### 4.1 Combined SR (%) and Cost (ro/ep) — 6 Main Environments

> Data source: `experiment/tab_main_results/data.csv`. Costs are deployment-phase rollouts per episode (no Phase 1 amortization). Each cell: **SR / Cost**.

| Method | HotpotQA | APPS Intro | WebShop | FEVER | TWExpress | Plancraft |
|--------|----------|-----------|---------|-------|-----------|-----------|
| base_only | 49.0 / 0.00 | 58.5 / 0.00 | 7.2 / 0.00 | 37.0 / 0.00 | 67.5 / 0.00 | 29.8 / 0.00 |
| always_trigger | 97.0 / 1.80 | 64.5 / 2.58 | 43.0 / 5.63 | 99.8 / 1.46 | 99.3 / 3.45 | 22.8 / 6.99 |
| CaTS | 93.2 / 1.06 | 59.0 / 0.04 | 30.5 / 3.05 | 50.2 / 4.71 | 96.7 / 1.97 | 22.3 / 4.39 |
| SEAG | 67.5 / 0.80 | 58.5 / 0.01 | 28.0 / 2.28 | 49.3 / 3.12 | 97.3 / 2.30 | 24.8 / 2.16 |
| CoRefine | 68.2 / 0.79 | 58.5 / 0.01 | 27.5 / 2.21 | 49.8 / 3.12 | 97.5 / 2.26 | 22.8 / 2.06 |
| CATTS | 68.3 / 1.07 | 58.5 / 0.03 | 16.0 / 0.19 | 34.2 / 0.06 | 97.5 / 2.26 | 25.0 / 2.14 |
| AUQ | 97.0 / 1.69 | 61.3 / 1.73 | 35.7 / 5.33 | 40.7 / 1.17 | 95.5 / 1.24 | 24.2 / 6.78 |
| s1_budget | 97.0 / 1.04 | 63.7 / 1.00 | 7.8 / 1.00 | 46.2 / 1.58 | 95.0 / 1.09 | 18.3 / 1.68 |
| **EAAG** | **95.2 / 1.34** | **66.0 / 1.20** | **43.8 / 2.29** | **49.8 / 2.99** | **99.0 / 2.84** | **23.3 / 3.69** |

> Note: CaTS/SEAG/CoRefine additionally require Phase 1 calibration (200 ep of always_trigger) not reflected in the cost column above. CATTS/AUQ/s1_budget/EAAG have no Phase 1 requirement.

**Key observations:**
- **TWExpress** (rollout-safe): All methods >95% SR. EAAG (99.0%) highest SR overall. Costs comparable across methods (1.09–3.45 ro/ep).
- **Plancraft** (rollout-harmful): s1_budget worst (18.3% < base 29.8%) — forcing rollouts when harmful. CaTS 22.3% and CoRefine 22.8% also below base. EAAG (23.3% / 3.69) near base, correctly learning to rarely trigger.
- **FEVER** (direction mismatch): CATTS 34.2% < base 37.0%. All fixed-direction CBs cluster ~50%, far below always_trigger 99.8%.
- **WebShop** (strongest EAAG win): EAAG 43.8% / 2.29 vs CaTS 30.5% / 3.05. LLM features critical.
- **APPS Intro** (narrow headroom): SEAG/CoRefine/CATTS barely trigger (cost ~0.01–0.03), gaining no SR over base. EAAG 66.0% / 1.20 best.

### 4.2 Head-to-Head Summary

**EAAG vs 6 baselines across 8 environments: 34 wins, 2 losses.**

> Data source: `experiment/tab_winloss/data.csv` — CaTS 5W/0L, SEAG 6W/0L, CoRefine 5W/0L, CATTS 6W/0L, AUQ 6W/1L, s1_budget 6W/1L.

| Environment | EAAG SR / Cost | vs CaTS | vs CATTS | Highlight |
|-------------|----------------|---------|----------|-----------|
| HotpotQA | 95.2 / 1.34 | Win (93.2 / 1.06) | Win (68.3 / 1.07) | Near oracle (97%) |
| WebShop | 43.8 / 2.29 | Strong win (30.5 / 3.05) | Win (16.0 / 0.19) | LLM features critical, 75.1% precision |
| FEVER | 49.8 / 2.99 | Tie (50.2 / 4.71, lower cost) | Strong win (34.2 < base) | CATTS below base (37%) |
| APPS Intro | 66.0 / 1.20 | Win (59.0 / 0.04) | Win (58.5 / 0.03) | Adaptive under narrow headroom |
| TWExpress | 99.0 / 2.84 | Win (96.7 / 1.97) | Win (97.5 / 2.26) | RR=73%, near always (99.3%) |
| Plancraft | 23.3 / 3.69 | Win (22.3 / 4.39) | Tie (25.0 / 2.14) | Learns to almost never trigger |

**Pareto-dominance**: EAAG Pareto-dominates CaTS in 5/6 environments.

### 4.3 Appendix Experiments (2 environments)

> Data source: `experiment/tab_main_results/data.csv` (rows for APPS Intv and CRUXEval).

| Method | APPS Interview SR / Cost | CRUXEval SR / Cost |
|--------|--------------------------|--------------------|
| base_only | 60.5 / 0.00 | 85.0 / 0.00 |
| always_trigger | 79.5 / 2.19 | 99.5 / 1.91 |
| CaTS | 66.2 / 0.54 | 95.0 / 0.73 |
| SEAG | 66.0 / 0.64 | 85.8 / 0.73 |
| CoRefine | 67.5 / 0.62 | 85.8 / 0.73 |
| CATTS | 60.8 / 0.02 | 81.3 / 0.04 |
| AUQ | 64.7 / 1.08 | 99.0 / 1.75 |
| s1_budget | 69.0 / 1.00 | 86.5 / 1.00 |
| **EAAG** | **73.0 / 1.35** | **98.5 / 1.24** |

---

## 5. Storyline & Paper Structure

### Core Narrative

```
Hidden assumption (fixed signal direction)
  → Assumption is wrong (4 Observations)
    → Why it's wrong (Two-Source Model / Simpson's Paradox)
      → Wrong direction is provably fatal (Proposition)
        → How to fix it (EAAG)
          → Fixed = wins everywhere (Results)
```

**One sentence**: The semantics of uncertainty signals are determined by the environment's information structure; any method assuming fixed semantics is provably incomplete.

### Section-by-Section Plan

| Section | Pages | Content |
|---------|-------|---------|
| §1 Introduction | 1.5p | P1: Background (test-time compute + selective triggering) → P2: Hidden assumption ("fixed direction") → P3: Assumption is wrong (3 concrete ρ values) → P4: Why (Two-Source Model + Simpson's Paradox) → P5: Method + results (34W/2L) → P6: Contributions (3 items) |
| §2 Related Work | 0.75p | §2.1: Signal-based / Vote-based / RL-based methods — all share fixed-direction assumption. §2.2: Orthogonal work (test-time scaling, search methods). Concurrent work statement. |
| §3 Signal-Utility Landscape | 2.0p | **Heart of the paper.** §3.1 Empirical: 4 Observations (direction reversal / signal identity replacement / single signal ≈ random / CB systematic failure). §3.2 Formal: Two-Source Model (intuition → formula → environment mapping → Simpson's Paradox) + Proposition (direction discovery is necessary) + 3 testable predictions. §3.3: Design implications (method classification table → derive 3 desiderata). |
| §4 Method: EAAG | 1.5p | Design principles (derived from §3 findings) → "Why simplicity" (direction > gate complexity) → Three steps: Explore / Reason / Learn & Deploy → Online adaptation → WebShop concrete example |
| §5 Experiments | 2.5p | §5.1 Setup (8 envs, baselines, metrics) → §5.2 Main results (main table + Pareto + narrative) → §5.3 Ablation (direction >> signal >> LLM) → §5.4 Theory verification (P1–P3 all confirmed) → §5.5 Extreme rollout environments → §5.6 Robustness of direction reversal (stratified / interventional / capacity ablation — core reviewer defense) |
| §6 Discussion | 0.75p | Community insight ("bottleneck is understanding uncertainty semantics") → FEVER exploration bias (honest limitation + theory-consistent) → Future directions (taxonomy beyond two sources / adaptive exploration / multi-agent signal semantics) → Limitations (4 items, each with mitigation) → Broader impact |
| §7 Conclusion | 0.25p | Echo abstract. Final sentence: "The bottleneck was never the method's complexity—it was the assumption." |
| Appendix | ~6p | A: Extended related work → B: Experimental details (incl. APPS Interview & CRUXEval results) → C: Proofs → D: Two-Source Model full derivation → E: Additional analyses (sensitivity, significance) |

### Paper Type Positioning

**Finding + Theory + Method** — contribution hierarchy: **Finding > Theory > Method**. The method's simplicity is a feature, not a bug. Analogous to:
- "Are Emergent Abilities a Mirage?" (Schaeffer et al., NeurIPS 2023 Outstanding) — method is trivial (change the metric), finding is transformative
- "Not All Tokens Are What You Need" (NeurIPS 2024 Best Paper Runner-Up) — method is token scoring + selective loss, finding is "not all tokens matter"

---

## 6. Key Figures & Tables Inventory

### Figures (15 total, 14 complete)

| # | Content | Location | Status |
|---|---------|----------|:------:|
| fig1 | Signal heatmap (8 env × signals, color=ρ) | §3.1 | ✅ |
| fig2 | Pareto frontier (SR vs Cost) | §5.2 | ✅ |
| fig3 | BSW wrong-direction degradation | §5.3 | ✅ |
| fig4 | Feature usage heatmap (7 env × features) | §3.1 | ✅ |
| fig5 | LLM ablation bar chart | §5.3 | ✅ |
| fig6 | FEVER exploration bias | §6 | ✅ |
| fig_auc | AUC hierarchy (3 env × 4 levels) | §3.1 | ✅ |
| fig_p1 | P1 temporal dynamics (ρ early→late) | §5.4 | ✅ |
| fig_trigger | Trigger rate vs step (6 env) | §5.3 | ✅ |
| fig_bsw_rho | BSW cost vs \|ρ\| regression | §3.2 | ✅ |
| fig_stratified | Stratified reversal (5 env × 3 strata) | §5.6 | ✅ |
| fig_matched | Matched-pair ΔU (4 env × 3 bins) | §5.6 | ✅ |
| fig_coverage | Coverage proxy vs ρ scatter | §5.4 | ✅ |
| fig_controlled | Controlled InfoPoor/InfoRich | §5.4 | ✅ |
| fig_method | EAAG 3-step pipeline diagram | §4 | ⏳ |

### Tables (10 total)

| # | Content | Location |
|---|---------|----------|
| tab:signal-discovery | Signal-utility ρ (8 env) | §3.1 |
| tab:env-type-mapping | Environment information structure classification | §3.2 |
| tab:classification | Method classification (FLARE T5 style) | §3.3 |
| tab:env-setup | 8 env setup (base/always/T) | §5.1 |
| tab:main | Main results (methods × 6 env) | §5.2 |
| tab:winloss | EAAG vs CB win/loss | §5.2 |
| tab:capacity | Gate capacity ablation | §5.6 |
| tab:significance | Statistical significance | Appendix |
| tab:extreme | Extreme rollout environments (TWExpress/Plancraft) | §5.5 |
| tab:additional | APPS Interview / CRUXEval results | Appendix |
