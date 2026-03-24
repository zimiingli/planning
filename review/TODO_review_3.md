# TODO: Action Items from Review 3 (LLM Agent Systems Researcher)

**Review Focus**: Environment diversity, optimizer abstraction, backbone generalization, RL baselines, exploration budget, FEVER failure
**Date**: 2026-03-23

---

## P1: Critical (Must Address Before Submission)

### P1-1: Disentangle optimizer type from environment type (addresses M1)
**Problem**: Per-action evaluation, K-variant sampling, and LLM-Propose-K are confounded with environment category. Direction reversal may be an optimizer-environment interaction, not purely an environment property.

**Actions**:
- [ ] Run per-action evaluation (K=5 candidate scoring) on at least one code environment (APPS Intro or APPS Interview) to test whether direction reversal persists with the same optimizer type as HotpotQA/FEVER
- [ ] Alternatively, run K-variant sampling on HotpotQA (generate K=3 answer candidates, evaluate each) to test whether the same environment shows the same direction with a different optimizer
- [ ] Add a discussion paragraph in Section 3.1 or Section 6 explicitly addressing the optimizer confound and presenting the cross-optimizer experiment
- [ ] If the confound cannot be fully resolved, temper claims: change "direction reversal is a property of the environment's information structure" to "direction reversal is a property of the environment-optimizer pair"

**Effort**: High (requires new experiments)
**Impact**: Resolves the most damaging critique; upgrades the paper from "interesting observation" to "causal finding"

### P1-2: Add at least one alternative backbone experiment (addresses M2)
**Problem**: All experiments use Qwen3-4B. The claim that direction reversal is model-independent is untested.

**Actions**:
- [ ] Run signal-utility correlation analysis (just the rho computation, no full EAAG training needed) on 3-4 core environments (HotpotQA, FEVER, APPS Interview, WebShop) using Llama 3 8B or Qwen3-8B
- [ ] Show rho signs are consistent across backbones (same direction, possibly different magnitude)
- [ ] Add a table in Section 5.6 or Appendix: "Direction reversal across backbones"
- [ ] If rho signs differ across backbones: this is actually a MORE interesting finding -- the direction is a model-environment interaction, not environment-only. Adjust the Two-Source Model claims accordingly.

**Effort**: Medium (reuse existing evaluation pipeline, just swap the model)
**Impact**: Directly addresses the highest-priority concern from both Review 1 and Review 3

---

## P2: Important (Strongly Recommended)

### P2-1: Add AdaptThink or Thinkless as an RL baseline (addresses M3)
**Problem**: RL-based methods implicitly learn direction through policy optimization. They are the most natural comparison for EAAG's explicit direction discovery.

**Actions**:
- [ ] Implement AdaptThink (GRPO-based think/no-think) on 2-3 environments (HotpotQA, WebShop, FEVER) if compute permits
- [ ] If full RL training is too expensive: discuss in Section 2 why RL methods are not directly comparable (per-environment training cost, lack of interpretability, reasoning-setting focus)
- [ ] Add a paragraph in Section 2.1 (RL-based methods) explicitly comparing EAAG vs RL on four dimensions: (a) per-environment training cost, (b) interpretability of learned direction, (c) cross-environment transfer, (d) data efficiency
- [ ] If RL baselines are included and EAAG wins: this is strong evidence. If RL wins: discuss what RL's implicit direction learning captures that explicit direction discovery misses

**Effort**: High if running experiments; Low if discussion-only
**Impact**: Positions EAAG within the broader adaptive compute landscape

### P2-2: Provide exploration budget sensitivity analysis (addresses M4)
**Problem**: N_explore=50 is fixed without justification. FEVER failure may be partially due to insufficient exploration.

**Actions**:
- [ ] Run EAAG with N_explore in {10, 20, 30, 50, 100, 200} on HotpotQA and FEVER
- [ ] Plot SR vs N_explore for both environments -- show convergence curve
- [ ] Specifically test: does N_explore=200 fix the FEVER failure? If yes, the 50-episode budget is too conservative for step-0-critical environments. If no, the exploration strategy (random gating) is the bottleneck, not budget size
- [ ] Add the convergence plot to Appendix E with a summary sentence in Section 6 Limitations
- [ ] Consider adding a practical recommendation: "For environments with suspected early-critical decisions, use N_explore=100 with warm-start always-trigger"

**Effort**: Medium (reuse existing pipeline, just vary N_explore)
**Impact**: Makes the method practically deployable; addresses a concrete reviewer concern

### P2-3: Strengthen or remove Proposition 1 (addresses M1 of Review 1 and review 3 technical assessment)
**Problem**: Proposition 1 is trivially true by construction. It restates the premise rather than proving something non-obvious.

**Actions**:
- [ ] Option A (Strengthen): Replace Proposition 1 with a convergence guarantee: "With N exploration episodes and signal strength |rho| > c, LASSO direction learning recovers the correct sign with probability >= 1 - delta, where delta = f(N, |rho|)." This is provable using standard LASSO consistency results (Zhao & Yu, 2006).
- [ ] Option B (Strengthen): Add a quantitative damage bound: "Wrong-direction gating degrades SR by at least Omega(|rho| * delta_headroom), where delta_headroom is the environment's rollout headroom." Support with the BSW data across environments.
- [ ] Option C (Soften): Keep Proposition 1 but explicitly note it is "a formalization of the intuition, not a deep theoretical result" and shift emphasis to the empirical damage quantification (BSW ablation)
- [ ] Update Section 3.2 accordingly

**Effort**: Medium (Option A requires theoretical work; Option C is editorial)
**Impact**: Addresses a critique that both reviewers raised; strengthens the theoretical contribution

---

## P3: Recommended (Would Improve Paper)

### P3-1: Address the FEVER limitation more honestly (addresses m1)
**Problem**: FEVER captures <1% of available headroom. The paper's framing as "honest limitation" understates the severity.

**Actions**:
- [ ] Add a sentence in Section 5.2 FEVER analysis: "EAAG captures only 20.4% of the available headroom on FEVER (12.8pp of 62.8pp), compared to >90% on HotpotQA. This makes EAAG unsuitable for step-0-critical environments without the curriculum-based exploration proposed in Section 6."
- [ ] Add a practical recommendation paragraph in Section 6: "For environments where practitioners suspect early-critical decisions (a common pattern in search-based QA), we recommend augmenting EAAG's exploration with 10-20 always-trigger episodes at step 0 to ensure coverage of the critical window"
- [ ] Consider testing this "hybrid exploration" fix (random gating + always-trigger at step 0) on FEVER. If it works, add as an extension.

**Effort**: Low (mostly editorial; medium if running the hybrid exploration experiment)
**Impact**: Demonstrates practical awareness and provides actionable deployment guidance

### P3-2: Replace "emergent adaptive behavior" with precise language (addresses m4)
**Problem**: "Emergent" is loaded terminology in the LLM context, and the behavior described is fully explained by logistic regression on different input distributions.

**Actions**:
- [ ] Replace all instances of "emergent adaptive behavior" with "environment-adaptive gating patterns" or "learned adaptive behavior"
- [ ] In Abstract: change "exhibits emergent adaptive behavior" to "exhibits environment-adaptive gating"
- [ ] In Section 5.2: change "EAAG's behavior is qualitatively different... exhibits emergent environment-specific strategies" to "EAAG's gating patterns adapt to each environment's characteristics"
- [ ] In Section 5.3: change "Gating magnitude emerges from direction learning" to "Gating magnitude follows from direction learning" (the word "emerges" is fine here, it's the "emergent" adjective that is problematic)
- [ ] In Conclusion: same replacement

**Effort**: Low (find-and-replace)
**Impact**: Avoids reviewer objections about overclaiming; aligns with Schaeffer et al. (2023) which the paper cites

### P3-3: Add at least one tool-use or software engineering environment (addresses m2)
**Problem**: The 8 environments over-represent code generation (3/8) and miss commercially critical categories (tool use, SWE-bench-style tasks).

**Actions**:
- [ ] Consider adding one of: SWE-bench Lite, ToolBench, or a simple API-calling agent environment
- [ ] If adding a new environment is too expensive: add a discussion paragraph in Section 5.1 explicitly acknowledging the coverage gaps (tool use, software engineering, long-horizon) and arguing why the current selection is sufficient for the Two-Source Model validation
- [ ] Consider replacing CRUXEval (which shows weak signals and adds little to the narrative) with a tool-use environment

**Effort**: High if adding environment; Low if discussion-only
**Impact**: Strengthens the "diverse environments" claim and connects to real-world agent deployments

### P3-4: Fix win/loss counting to include effect sizes (addresses m3)
**Problem**: 34W/2L counts all wins equally regardless of magnitude or significance.

**Actions**:
- [ ] Add a supplementary table showing: Environment x Baseline, delta-SR, 95% CI, significance
- [ ] In the main text, supplement "34W/2L" with: "of which 18 are statistically significant at the 95% level"
- [ ] Consider reporting mean SR improvement (weighted by headroom) as an aggregate metric alongside win count
- [ ] Alternatively, report number of environments where EAAG achieves >X% of oracle SR (a more meaningful practical metric)

**Effort**: Low (data already available in appendix significance table)
**Impact**: Increases statistical rigor; preempts reviewer criticism about inflated win counts

---

## P4: Minor (Nice-to-Have)

### P4-1: Formalize the LLM Reason step
- [ ] Include the exact prompt template in Appendix B
- [ ] Run a sensitivity analysis: 3 different prompt templates, measure SR variance across prompts
- [ ] Since LLM contributes <1pp in 4/6 environments, consider presenting it as "optional enhancement" rather than core component

### P4-2: Add CATTS total cost to results table
- [ ] Add a footnote to Table main: "CATTS cost excludes K=5 per-step voting overhead (~5x forward passes per step)"
- [ ] Or add a "Total Cost" column that includes per-step voting overhead for CATTS

### P4-3: Tighten the coverage proxy section (Section 5.7)
- [ ] r=+0.75 on 6 data points (p=0.086) is not convincing for the main text
- [ ] Move entirely to Appendix D with appropriate caveats about the ad-hoc operationalization
- [ ] Or remove and acknowledge p_I estimation as an open problem (which the paper already does in Section 6 Limitations)

### P4-4: Correct APPS Intro presentation
- [ ] rho=+0.012 with p=0.63 is absence of evidence, not evidence of absence
- [ ] Add a clarifying sentence: "APPS Intro's rho=+0.012 (p=0.63) is statistically indistinguishable from zero, consistent with but not proof of the Two-Source Model's prediction of near-zero signal at the critical threshold p_I*"

---

## Priority Summary

| Priority | Item | Effort | Impact | Addresses |
|----------|------|--------|--------|-----------|
| **P1** | P1-1: Cross-optimizer experiment | High | Critical | M1 (optimizer confound) |
| **P1** | P1-2: Alternative backbone rho analysis | Medium | Critical | M2 (single backbone) |
| **P2** | P2-1: RL baseline or discussion | High/Low | High | M3 (missing RL comparison) |
| **P2** | P2-2: Exploration budget sensitivity | Medium | High | M4 (50-episode budget) |
| **P2** | P2-3: Strengthen Proposition 1 | Medium | Medium | Theoretical soundness |
| **P3** | P3-1: FEVER honest assessment | Low | Medium | m1 |
| **P3** | P3-2: Replace "emergent" | Low | Medium | m4 |
| **P3** | P3-3: Environment diversity | High/Low | Medium | m2 |
| **P3** | P3-4: Effect sizes in win/loss | Low | Medium | m3 |
| **P4** | P4-1 to P4-4: Minor fixes | Low | Low | Various |

**Bottom line**: P1-1 (cross-optimizer) and P1-2 (alternative backbone) are the two experiments that would most substantially strengthen the paper. Together they would resolve the primary confounds and move the recommendation from borderline accept to clear accept.
