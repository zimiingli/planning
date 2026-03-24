# TODO: Action Items from Review 2 (Theoretical ML Reviewer)

**Review Score**: 5/10 (Borderline Reject)
**Reviewer Profile**: Theoretical ML, learning theory, statistical decision theory
**Key Diagnosis**: Theory is overclaimed relative to actual formal content. Proposition 1 is trivial, Two-Source Model is unfalsifiable, Simpson's paradox connection is informal.

---

## P1: Strengthen Proposition 1 with quantitative bounds [HIGH PRIORITY]

**Estimated score impact**: +1.0 to +1.5 (5 -> 6-6.5)
**Difficulty**: Medium-Hard
**Files**: `VOC_PAPER_WRITING_GUIDE.md` (Section 3.2, Appendix C)

The reviewer's core complaint is that Proposition 1 is a tautology: "if directions are opposite, no fixed direction works in both" is true by definition. This must be upgraded to a substantive result.

### Option A: Sample complexity bound for direction recovery (Recommended)
- [ ] **A1.** Formalize direction recovery as a hypothesis testing problem: H0: rho >= 0 vs. H1: rho < 0 based on N exploration episodes.
- [ ] **A2.** Derive a finite-sample bound: N >= C * d * log(d) / rho^2 suffices for correct sign recovery with probability >= 1 - delta, where d is the feature dimension and rho is the true Spearman correlation. Leverage known results on sign-consistency of LASSO (Wainwright 2009, "Sharp thresholds for high-dimensional and noisy sparsity recovery").
- [ ] **A3.** Validate empirically: plot sign recovery accuracy vs. N_explore in {10, 20, 30, 50, 100} across 4 core environments.
- [ ] **A4.** Add as Proposition 2 or upgrade Proposition 1 to include the bound.
- [ ] **A5.** Update Section 4 (Step 1: Explore) to cite the bound when justifying N_explore = 50.
- [ ] **A6.** Add the full proof to Appendix C.

### Option B: Quantitative wrong-direction damage bound
- [ ] **B1.** Prove: SR(g_wrong, E) <= SR(base, E) - Omega(|rho| * Delta) where Delta is the rollout headroom.
- [ ] **B2.** Verify empirically: the BSW ablation data (Table in Appendix C, lines 1570-1582) already shows |rho| vs. |Delta_SR| with R^2 > 0.5. Formalize this as a theorem.
- [ ] **B3.** This converts the current hand-wavy "damage magnitude scales with signal strength" into a rigorous bound.

### Minimal fix (if time-constrained):
- [ ] **C1.** At minimum, add a Remark after Proposition 1 explicitly acknowledging its logical simplicity and explaining that its value is *making the implicit assumption explicit* and *quantifying the empirical cost of violating it*.
- [ ] **C2.** Add confidence intervals on the BSW damage values so the reviewer sees this as a measured quantity, not just a point estimate.

---

## P2: Make Two-Source Model falsifiable [HIGH PRIORITY]

**Estimated score impact**: +0.5 to +1.0 (cumulative: 5.5-7.5)
**Difficulty**: Medium
**Files**: `VOC_PAPER_WRITING_GUIDE.md` (Section 3.2, Section 5.7, Appendix D)

The reviewer identifies that (alpha, beta, p_I) have 3 free parameters and only 1 observable (sign of rho), making the model unfalsifiable. Need to add testable constraints.

### Action items:
- [ ] **2a.** Formalize the model to produce a *quantitative* prediction: not just sign(rho) but an ordering |rho(FEVER)| > |rho(HotpotQA)| > |rho(APPS Intro)| based on the p_I ranking. This ordering is already present in the data and follows from the model (environments farther from p_I* have larger |rho|). Write this as a corollary.
- [ ] **2b.** Perform a train/test split of environments: fit alpha, beta on 4 environments (HotpotQA, FEVER, APPS Interview, WebShop), predict rho sign and ordering on held-out 4 (APPS Intro, TWExpress, CRUXEval, Plancraft). Report whether predictions match.
- [ ] **2c.** Replace or supplement the ad-hoc coverage proxy (evidence_count/3, step_count/7) with a principled operationalization. Candidate: compute the mutual information I(observation_t; task_answer | history_{<t}) as a measure of information sufficiency, or use the agent's own confidence trajectory as a proxy.
- [ ] **2d.** Plot U vs. H within stratified state subsets (early/late, high/low coverage) to verify the linear conditional model visually. Show scatter plots with fitted regression lines. This directly addresses Question 4 from the reviewer.
- [ ] **2e.** Add a paragraph in Section 3.2 explicitly stating what would falsify the model: "The Two-Source Model would be falsified if: (i) rho did not vary monotonically with a reasonable proxy for p_I across environments, (ii) within-environment temporal dynamics (P1) showed rho increasing rather than decreasing, or (iii) the conditional U-H relationship within identified state types were non-monotonic."
- [ ] **2f.** Update Section 5.7 to use the improved coverage proxy and report confidence intervals.

---

## P3: Fix the Simpson's paradox framing [MEDIUM PRIORITY]

**Estimated score impact**: +0.3 to +0.5 (cumulative: 5.8-8.0)
**Difficulty**: Easy-Medium
**Files**: `VOC_PAPER_WRITING_GUIDE.md` (Section 3.2 "Theoretical grounding" paragraph)

The reviewer correctly notes that the paper invokes Simpson's paradox informally without a proper causal DAG or identification analysis.

### Action items:
- [ ] **3a.** Add a causal DAG (Figure, or in-text description): Z (latent type) -> H (entropy), Z -> U (utility), with H -> U conditional on Z. The marginal H-U association reverses because Z is an unobserved confounder.
- [ ] **3b.** Explicitly formalize: "Within Type I: E[U | H=h, Z=I] is decreasing in h. Within Type D: E[U | H=h, Z=D] is increasing in h. The marginal E[U | H=h] = p_I * E[U|H=h,Z=I] + (1-p_I) * E[U|H=h,Z=D] can be either increasing or decreasing depending on p_I."
- [ ] **3c.** Clarify terminology: either commit to "Simpson's paradox" with a proper causal justification (citing Pearl 2014 correctly), or soften to "Simpson's paradox-like reversal" / "ecological fallacy" / "marginal reversal due to latent heterogeneity."
- [ ] **3d.** Optionally: cite Blyth (1972, "On Simpson's Paradox and the Sure-Thing Principle") for the probabilistic formulation, which is closer to what the paper actually demonstrates.

---

## P4: Reposition P1-P3 predictions honestly [MEDIUM PRIORITY]

**Estimated score impact**: +0.2 to +0.3 (cumulative: 6.0-8.3)
**Difficulty**: Easy
**Files**: `VOC_PAPER_WRITING_GUIDE.md` (Section 3.2 "Testable Predictions", Section 5.4)

The reviewer argues P1-P3 are post-hoc pattern descriptions, not deductions from the model.

### Action items:
- [ ] **4a.** For P1 (temporal dynamics): explicitly state the additional assumption required—"p_I(t) is non-decreasing over the episode because information accumulates monotonically"—and note that this is a testable auxiliary hypothesis.
- [ ] **4b.** For P2 (cross-environment consistency): acknowledge this is a consistency check ("environments with similar task structure should have similar information structure, hence similar p_I, hence similar rho sign") rather than a prediction, since "similar task structure" is not formally defined.
- [ ] **4c.** For P3 (signal identity alignment): clarify that this prediction is about the *full framework* (Two-Source Model + the signal identity hypothesis), not the mixture model alone (which only concerns entropy H). The model by itself says nothing about which signal dominates.
- [ ] **4d.** Rephrase the section header from "Testable Predictions" to "Empirically Testable Hypotheses" or "Model-Consistent Patterns" to avoid overclaiming deductive power.
- [ ] **4e.** In Section 5.4, add a sentence acknowledging: "We note that P1 and P3 require auxiliary assumptions beyond the Two-Source Model itself; the verifications below test the joint hypothesis of the model plus these auxiliary assumptions."

---

## P5: Miscellaneous fixes [LOW PRIORITY]

**Estimated score impact**: +0.2 combined
**Difficulty**: Easy
**Files**: Various sections

- [ ] **5a.** Remove or soften "provably incomplete" language (Section 3.3 and elsewhere). Replace with "demonstrably insufficient" or "necessarily incomplete under the monotonic-gate assumption."
- [ ] **5b.** Fix the epistemic/aleatoric analogy (Section 3.2): add a clarifying sentence that Type D is closer to "option value" in decision theory than to aleatoric uncertainty in the standard ML sense.
- [ ] **5c.** Add bootstrap confidence intervals for all rho values in Table 1 (tab_signal_discovery). This addresses reviewer m3 and Question 8.
- [ ] **5d.** In Section 3.2 "Environment mapping" paragraph, soften the claim that the mapping "is not a free parameter" — it is determined by task structure analysis, but this analysis is qualitative and post-hoc. A more honest framing: "The mapping is informed by the environment's task structure rather than fit to the observed rho values, though we acknowledge the analysis is qualitative."
- [ ] **5e.** Clarify in Proposition 1 that the necessity holds for the class of threshold gates g(s) = 1[d * sigma(s) > theta], not for arbitrary gate functions. A neural network gate could in principle learn correct behavior without explicit "direction discovery." This addresses reviewer concern m2.
- [ ] **5f.** Address reviewer Question 6: add a remark explaining that the theoretical model uses entropy H as the canonical signal for parsimony, but the framework extends to any scalar signal sigma(s). The model predicts reversal for *any* signal correlated with the latent type—step_count dominates because it happens to be a stronger proxy for the latent type than entropy.

---

## Priority Summary

| Priority | Item | Score Impact | Effort | Key Benefit |
|----------|------|:---:|:---:|------|
| **P1** | Strengthen Proposition 1 | +1.0 to +1.5 | Medium-Hard | Transforms tautology into real theorem |
| **P2** | Make model falsifiable | +0.5 to +1.0 | Medium | Removes "post-hoc" criticism |
| **P3** | Fix Simpson's paradox | +0.3 to +0.5 | Easy-Medium | Improves technical precision |
| **P4** | Reposition P1-P3 | +0.2 to +0.3 | Easy | Removes overclaiming |
| **P5** | Misc fixes | +0.2 | Easy | Polish and precision |

**Total estimated improvement**: +2.2 to +3.5 points (from 5/10 to 7-8.5/10 range)

**Critical path**: P1 alone could flip the decision from reject to accept. P1 + P2 together would likely satisfy a theoretical reviewer. P3-P5 are polish.

---

## Cross-reference with Review 1

Review 1 (score 6/10) shares several concerns with Review 2 but weights them differently:

| Concern | Review 1 | Review 2 | Consensus |
|---------|----------|----------|-----------|
| Proposition 1 trivial | M2 (Medium) | M1 (High) | **Both agree** — must fix |
| Two-Source Model post-hoc | M1 (Medium-High) | M2 (High) | **Both agree** — must fix |
| Single backbone | M3 (Medium-High) | Not major concern | Review 1 priority |
| Method technically thin | M4 (Medium) | Not major concern | Review 1 priority |
| Simpson's paradox informal | Not raised | M3 (Medium) | Review 2 priority |
| P1-P3 post-hoc | Not raised | m1 | Review 2 priority |
| Coverage proxy weak | m4 | Part of M2 | **Both agree** — fix or remove |

**Shared top priority**: Strengthen Proposition 1 and make Two-Source Model falsifiable. These address the top concerns of both reviewers simultaneously.
