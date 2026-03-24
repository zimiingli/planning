# TODO: Meta-Review Action Items (Review 6)

**Priority Framework**: Items are ranked by estimated acceptance probability impact. Total estimated swing: +30-40% if all Tier 1 items completed.

---

## Tier 1: MUST-DO (Acceptance probability: +20-25%)

### T1.1 Multi-Backbone Direction Reversal Verification [CRITICAL]
- **Impact**: +15-20% acceptance probability alone
- **Effort**: 2-5 GPU-days depending on model size
- **Status**: NOT STARTED
- [ ] Select 2 additional backbones (e.g., Llama 3 8B + Qwen3-14B or Qwen3-32B)
- [ ] Run signal-utility correlation analysis on 4 core environments: HotpotQA, FEVER, APPS Interview, WebShop
- [ ] For each backbone x environment: compute Spearman rho(entropy, U), p-value, sign
- [ ] Compute strongest signal identity per environment per backbone
- [ ] Create Table: backbone x environment matrix showing rho signs and values
- [ ] **Success criterion**: Sign of rho consistent across 3 backbones for >= 3/4 environments
- [ ] Add results to Section 5.6 (Robustness) as new paragraph "Cross-backbone consistency"
- [ ] Update Abstract, Intro P3, and Conclusion to say "across N backbones" if results confirm
- [ ] Update Limitations to remove "single backbone" caveat (or weaken it)
- **Note**: Even a single additional backbone with consistent signs is valuable. Prioritize the smallest additional backbone (fastest to run) first.

### T1.2 Reframe Two-Source Model as Explanatory Framework
- **Impact**: +3-5% (removes a reason to reject; does not add a reason to accept)
- **Effort**: 1-2 hours of rewriting
- **Status**: NOT STARTED
- [ ] Section 3.2 title: Keep "Two-Source Model" but add subtitle "An Explanatory Framework"
- [ ] Add explicit caveat after Eq. 2: "The model's value is explanatory (why direction reverses) and prescriptive (what gates must learn), not predictive of exact rho values. p_I is a latent construct that organizes observations, not a measurable quantity."
- [ ] Remove any language that implies the model "predicts" rho values -- reframe as "the model is *consistent with* observed patterns"
- [ ] Keep P1-P3 predictions but frame them as "consistency checks" rather than "confirmations"
- [ ] In the environment mapping table caption, change "Predicted rho direction" to "Model-consistent rho direction"

### T1.3 Qualify the 34W/2L Metric
- **Impact**: +2-3% (preempts statistical criticism)
- **Effort**: 30 minutes
- **Status**: NOT STARTED
- [ ] Abstract: Change "34 wins vs. 2 losses" to "34 wins (18 statistically significant) vs. 2 losses"
- [ ] Section 5.2 first paragraph: Add "(18 significant at 95% bootstrap CI)" after "34 wins"
- [ ] Add sentence: "Mean SR improvement across all wins is X.X pp (median: Y.Y pp)."
- [ ] Conclusion: Same qualification
- [ ] Verify the 18/30 significance count is correct from bootstrap data

### T1.4 Remove "Emergent" Terminology
- **Impact**: +1-2% (removes a distraction / criticism vector)
- **Effort**: 15 minutes (search-and-replace)
- **Status**: NOT STARTED
- [ ] Global replace "emergent adaptive behavior" -> "environment-adaptive gating patterns"
- [ ] Global replace "emergent" -> "learned" or "adaptive" where referring to EAAG behavior
- [ ] Specifically fix: Abstract, Section 5.2 "story of the results" paragraph, Section 5.3 "Gating magnitude emerges" paragraph, Conclusion
- [ ] Keep the word "emergent" ONLY when citing Schaeffer et al. (emergent abilities) as a reference point

---

## Tier 2: SHOULD-DO (Acceptance probability: +5-10%)

### T2.1 Strengthen Proposition 1 (Pick ONE Option)
- **Impact**: +3-5%
- **Effort**: 4-8 hours depending on option
- **Status**: NOT STARTED

**Option A: Quantitative damage bound**
- [ ] Prove: delta_SR >= f(|rho|, trigger_rate) when direction is wrong
- [ ] Use BSW data (4 environments) to fit and verify the bound
- [ ] Present as Corollary 1 after Proposition 1

**Option B: Exploration sample complexity**
- [ ] Prove: With N >= C/epsilon^2 exploration episodes, LASSO recovers correct direction sign with probability >= 1 - delta
- [ ] Derive C as a function of signal SNR
- [ ] Verify empirically: plot direction recovery probability vs. N_explore for 2-3 environments

### T2.2 A Priori Direction Prediction Test
- **Impact**: +3-5% (transforms model from post-hoc to predictive)
- **Effort**: 1-3 GPU-days for new environment + analysis
- **Status**: NOT STARTED
- [ ] Select 1-2 held-out environments not in the paper (candidates: ALFWorld, ScienceWorld, TextCraft, BabyAI, InterCode SQL)
- [ ] Write down predicted direction based on task description + Two-Source Model BEFORE running any experiments
- [ ] Document prediction with reasoning: "This environment involves X, so we expect Type [I/D], therefore rho should be [+/-]"
- [ ] Run signal-utility analysis
- [ ] Report match/mismatch
- [ ] Add as new subsection in Section 5.4 or Appendix D

### T2.3 Clean Up Coverage Proxy (Section 5.7)
- **Impact**: +1-2%
- **Effort**: 1-2 hours
- **Status**: NOT STARTED
- [ ] **Decision**: Move entirely to Appendix D (recommended) OR make rigorous
- [ ] If keeping in appendix: acknowledge limitations clearly ("r=0.75 on 6 points is suggestive but not definitive")
- [ ] Remove from main text flow -- currently it weakens the theory section
- [ ] If making rigorous: justify denominators with principled criteria, include all 7+ environments, report confidence interval for r

### T2.4 N_explore Sensitivity Analysis
- **Impact**: +1-2%
- **Effort**: 1-2 GPU-days
- **Status**: NOT STARTED
- [ ] Run EAAG with N_explore in {10, 20, 30, 50, 100} on 2-3 environments (HotpotQA, WebShop, APPS Intro)
- [ ] Plot SR vs. N_explore curve
- [ ] Identify minimum viable N_explore (where direction recovery stabilizes)
- [ ] Add to Appendix E with reference from Section 4 Step 1

---

## Tier 3: NICE-TO-HAVE (Acceptance probability: +2-5%)

### T3.1 CATTS Cost Footnote
- [ ] Add footnote to Table main results: "CATTS cost excludes K=5 per-step voting overhead (Section 2.1). True per-step cost is K times higher than shown."
- **Effort**: 5 minutes

### T3.2 Formalize LLM Reason Step
- [ ] Include exact prompt template in Appendix B
- [ ] Run 3-5 prompt variants, report SR variance
- [ ] If variance is <1pp, add: "The LLM reasoning step is robust to prompt variation (variance < 1pp across 5 prompt variants)"
- [ ] If variance is >3pp, add prompt selection to the method
- **Effort**: 4-8 hours

### T3.3 Add Reading Guide Paragraph
- [ ] Add at end of Section 1 (after contributions list): "Readers interested primarily in the empirical finding may focus on Sections 3.1 and 5.6; those interested in the theoretical explanation on Section 3.2; those interested in the method and its evaluation on Sections 4-5."
- **Effort**: 5 minutes

### T3.4 LLM Ablation Clarification (Plancraft Issue)
- [ ] Address why removing LLM *improves* SR on Plancraft (+3.9pp without LLM)
- [ ] Add explicit discussion: "In rollout-harmful environments, LLM-generated features can introduce noise that worsens an already-adverse gating problem"
- [ ] Consider: is this a case where the LLM generates features that are *anti-predictive*?
- **Effort**: 30 minutes analysis + 15 minutes writing

---

## Page Budget Management

**Current estimate**: 10.25 pages. **Target**: 9.0 pages. **Need to cut**: ~1.25 pages.

### Cuts (in priority order):
- [ ] Move HotpotQA + APPS Intro per-environment analysis to appendix (-0.3p)
- [ ] Condense Related Work: merge signal-based + vote-based into single paragraph (-0.2p)
- [ ] Merge Observations 2 and 3 into single observation (-0.2p)
- [ ] Condense "Why Simplicity" paragraph to 3 sentences (-0.15p)
- [ ] Move "multi-agent coordination" future direction to appendix (-0.15p)
- [ ] Tighten Broader Impact to 2 sentences (-0.1p)
- [ ] Condense §2.2 Orthogonal Work (-0.1p)
- **Total**: -1.2 pages (within budget)

### Additions (if multi-backbone results are obtained):
- [ ] Cross-backbone consistency paragraph in Section 5.6: +0.2p
- [ ] Multi-backbone table: +0.1p
- **Net with additions**: -0.9 pages (within budget)

---

## Execution Order

**Week 1 (Highest priority)**:
1. T1.1 - Start multi-backbone experiments immediately (this is compute-bound and takes the longest)
2. T1.2 - Reframe Two-Source Model (can be done while waiting for T1.1)
3. T1.3 - Qualify 34W/2L metric
4. T1.4 - Remove "emergent" terminology

**Week 2 (While multi-backbone runs)**:
5. T2.4 - N_explore sensitivity (can share compute with T1.1)
6. T2.3 - Clean up coverage proxy
7. T3.1 - CATTS cost footnote
8. T3.3 - Add reading guide
9. T3.4 - LLM ablation clarification
10. Page budget cuts

**Week 3 (After multi-backbone results return)**:
11. Integrate T1.1 results into paper
12. T2.1 - Strengthen Proposition 1 (choose option based on T1.1 results)
13. T2.2 - A priori prediction test (if time permits)
14. T3.2 - Formalize LLM Reason step (if time permits)
15. Final page budget reconciliation

---

## Decision Gates

**After T1.1 completes**:
- If direction reversal confirmed across backbones: proceed with all Tier 2 items, submit with high confidence
- If direction reversal NOT confirmed: major pivot required -- scope claims to single-model regime, reframe contribution, consider different venue
- If results are mixed: carefully scope claims to confirmed environments, strengthen other contributions to compensate

**After page cuts**:
- If under 9 pages with multi-backbone results: proceed
- If over 9 pages: cut coverage proxy entirely, move more per-environment analysis to appendix, consider merging Sections 5.5 and 5.6
