# NeurIPS 2026 Peer Review

**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Reviewer Confidence**: 4/5 (I have deep familiarity with LLM agents, test-time compute, and adaptive inference)

---

## Overall Assessment

**Recommendation: Weak Accept (6/10)**

This paper makes a genuinely interesting empirical observation — that the direction of signal-utility correlation reverses across agent environments — and provides a reasonable theoretical explanation via a Two-Source Model. The finding is well-supported by data across 8 environments and could influence how the community designs adaptive compute methods. However, several issues temper my enthusiasm: the method (EAAG) is technically thin, the theoretical model is post-hoc and difficult to falsify, and the single-backbone evaluation limits generalizability claims.

---

## Scores

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| **Novelty** | 7 | Direction reversal finding is novel and surprising. Method is incremental. |
| **Significance** | 7 | Could change how the community designs adaptive compute. |
| **Technical Soundness** | 6 | Core finding is solid, but Two-Source Model is unfalsifiable; Proposition 1 is trivially true. |
| **Clarity** | 8 | Well-written, clear narrative arc, good use of concrete numbers. |
| **Experimental Design** | 6 | 8 environments is good breadth but single backbone; no statistical significance on many comparisons. |
| **Reproducibility** | 7 | Detailed setup described, but code/data availability unclear. |

---

## Key Strengths

### S1: The core finding is compelling and well-evidenced
The direction reversal observation is the paper's strongest contribution. The contrast between FEVER (rho=-0.119) and APPS Interview (rho=+0.317) is concrete and striking. The authors demonstrate this isn't a fluke — it holds across 8 environments, persists within trajectory-length strata (Section 5.6), and the BSW ablation (wrong direction: -37pp on HotpotQA) provides interventional evidence that direction is causal, not merely correlational. This is NeurIPS-quality empirical work.

### S2: The narrative structure is excellent
The paper follows a clean "assumption -> falsification -> explanation -> fix -> validation" arc that is easy to follow and persuasive. The framing as an instance of Simpson's paradox is elegant. The design notes show careful study of NeurIPS best paper patterns, and it shows — the paper reads well.

### S3: Comprehensive baseline comparison
Comparing against 6 contemporaneous methods (CaTS, SEAG, CoRefine, CATTS, AUQ, s1_budget) across 8 environments is thorough. The 34W/2L record and Pareto-dominance analysis are convincing. The cost fairness discussion (deployment-only vs Phase 1 overhead) is honest.

### S4: Honest limitation discussion
The FEVER failure (49.8% vs always 99.8%) is discussed transparently with a plausible explanation (exploration bias at step-0). This is refreshing — many papers would hide or minimize such a result.

---

## Major Concerns

### M1: The Two-Source Model is post-hoc and difficult to falsify
The model proposes two uncertainty types (Info-Poverty and Decision-Difficulty) and maps each environment to one type. But this mapping is done *after observing the results*. Any environment with negative rho is labeled "Type I" and any with positive rho is labeled "Type D." The model then "predicts" the sign of rho — which is circular.

**What would make this stronger:**
- A priori prediction: Given a *new* environment's task description (without running experiments), can the model predict the rho direction? This would be a true test of the theory.
- Quantitative predictions: The model predicts sign(rho) = sign(beta - (alpha+beta)*p_I), but p_I is unobservable and alpha/beta are free parameters. The model can explain any direction by adjusting p_I.

The controlled reversal experiment (InfoPoor/InfoRich) partially addresses this, but even there, the InfoPoor result (entropy rho=+0.119, weakly positive) doesn't fully match the Type I prediction of negative rho — the authors acknowledge this but the caveat is buried.

**Severity: Medium-High.** The finding stands regardless of the model, but the theoretical contribution is weaker than presented.

### M2: Proposition 1 is trivially true
The proposition states: if two environments have opposite true directions, no fixed-direction gate can satisfy both. This is true by construction — it's essentially restating the assumption. A more useful theoretical result would characterize *how much* performance degrades as a function of direction mismatch magnitude, or prove that direction learning with N exploration episodes converges to the correct direction with high probability.

**Severity: Medium.** The proposition is correct but contributes little beyond the empirical observation.

### M3: Single backbone (Qwen3-4B) limits generalizability
The core claim is that direction reversal is a property of the *environment*, not the model. But this is only tested with one backbone. It's entirely possible that a larger model (e.g., 70B) with better calibration would show different signal-utility relationships — perhaps even eliminating the reversal. The authors acknowledge this in limitations but it's a significant gap.

**What would help:** Even 2-3 experiments with a different backbone (e.g., Llama 3 8B) on the 4 core environments showing the same reversal pattern would substantially strengthen the claim.

**Severity: Medium-High.** This is the most actionable improvement the authors could make.

### M4: EAAG as a method is technically thin
EAAG is logistic regression with LASSO feature selection on top of LLM-generated features. The authors explicitly argue that simplicity is a feature (citing Michael Black's "Novelty in Science"), and the ablation showing direction >> complexity supports this. However:

- The "Reason" step (LLM analyzes exploration data) is described qualitatively but not formalized. What prompt is used? How robust is this to prompt variation? The ablation shows removing the LLM changes SR by <1pp in most environments, which raises the question: why include it at all?
- The 50-episode exploration budget is fixed and unjustified. Why 50? What's the sensitivity?
- The method is essentially "do logistic regression on the right features with the right signs" — which, while effective, may not meet the novelty bar for a methods contribution at NeurIPS.

**Severity: Medium.** Mitigated by the paper's positioning as Finding > Theory > Method.

---

## Minor Concerns

### m1: CATTS cost comparison is misleading
CATTS shows extremely low cost in Table 1 (e.g., 0.06 ro/ep on FEVER) because the cost metric only counts optimizer triggers. But CATTS runs K=5 forward passes at *every step* for vote computation. This per-step overhead is not reflected in the cost column, making CATTS appear much cheaper than it actually is. The authors mention this in Related Work but should note it in the results table footnote.

### m2: Win/loss counting is coarse
The 34W/2L metric counts SR improvements regardless of magnitude. A 0.1pp improvement counts the same as a 30pp improvement. More informative: report mean SR improvement and statistical significance. The significance table (Appendix) shows only 18/30 comparisons are statistically significant — meaning ~40% of the "wins" may not be meaningful.

### m3: APPS Intro entropy rho = +0.012 (p=0.63) is used as evidence
The paper uses APPS Intro as an example of "near-zero signal," but p=0.63 means the correlation is not statistically distinguishable from zero. This supports the narrative but should be presented more carefully — it's absence of evidence for a correlation, not evidence of absence.

### m4: Coverage proxy (Section 5.7) is weak
The correlation r=+0.75 is based on only 6 data points (excluding TWExpress outlier), yielding p=0.086 — not significant at conventional levels. The coverage operationalization is ad hoc (evidence_count/3 for HotpotQA, step_count/7 for FEVER) with no justification for the denominators. This section should be moved entirely to the appendix or removed — in its current form it weakens rather than strengthens the theory.

### m5: "Emergent adaptive behavior" overclaims
The paper describes EAAG's varying trigger rates (73% TWExpress, 28% WebShop) as "emergent." This is simply the logistic regression responding to different feature distributions — there's nothing emergent about it. The term "emergent" in the LLM context carries specific connotations (cf. Schaeffer et al.) and should not be used loosely.

### m6: LLM ablation incomplete
The paper says removing the LLM changes SR by <1pp "in 4 of 6 environments," but Plancraft shows -3.9pp. While acknowledged in the revised text, the claim that the LLM provides "robustness, not accuracy" is undermined by Plancraft where removing the LLM actually *improves* performance. This suggests the LLM can introduce harmful features in some environments.

---

## Questions for Authors

1. **Generalization test**: Have you tested direction reversal with any other backbone? Even a single alternative model on 2-3 environments would significantly strengthen the core claim.

2. **A priori prediction**: Given a text description of a new environment (e.g., "SQL query generation with execution feedback"), can you predict whether it will be Type I or Type D *before* running experiments?

3. **Exploration efficiency**: You use 50 episodes. What happens with 10? 20? 100? The sensitivity to this hyperparameter matters for practical deployment.

4. **RL baselines**: AdaptThink and Thinkless learn direction implicitly through RL. How does EAAG compare to these methods? They're mentioned in Related Work but not included as baselines.

5. **CATTS cost**: Would you consider adding a "Total Cost" column that includes CATTS's K=5 voting overhead for fair comparison?

6. **The 2 losses**: What are the specific environments/baselines for the 2 losses? Are they within noise?

---

## Detailed Assessment Against NeurIPS Criteria

### Novelty (7/10)
The *finding* (direction reversal) is genuinely novel — I'm not aware of prior work documenting this phenomenon in the agent setting. The *theory* (Two-Source Model) is a reasonable but unfalsifiable explanation. The *method* (EAAG) is incremental — logistic regression + LASSO is not novel, and the LLM reasoning step is poorly formalized.

**For NeurIPS**: The finding alone justifies publication, even with a simple method. Analogous to "Are Emergent Abilities a Mirage?" where the finding (metric choice drives apparent emergence) was the contribution, not the method.

### Significance (7/10)
If the direction reversal finding is robust across models (untested), it has high significance — it would change how the entire adaptive compute community designs gating mechanisms. The prescriptive framework ("characterize information structure before designing gates") is valuable. However, if the finding is backbone-specific, significance drops substantially.

### Experimental Design (6/10)
**Strengths**: 8 environments spanning QA, code, web, text games, manufacturing. Stratified analysis (Section 5.6) and controlled reversal (Section 5.4) go beyond basic correlation.

**Weaknesses**: Single backbone. 3-seed evaluation with bootstrap CIs, but many comparisons not significant. FEVER result (49.8%) undermines the "wins everywhere" narrative. The Phase 1 cost distinction is honest but complicates fair comparison.

### Clarity (8/10)
The paper is exceptionally well-structured. The design notes show careful study of successful NeurIPS papers and the narrative arc (assumption → falsification → theory → method → validation) is compelling. The use of concrete numbers throughout (specific rho values, specific SR percentages) makes claims verifiable.

---

## Suggestions for Improvement

1. **Multi-backbone validation** (highest priority): Run at least one alternative backbone on 4 core environments. If direction reversal persists, the paper becomes much stronger.

2. **Strengthen Proposition 1**: Either prove a quantitative bound on wrong-direction degradation, or prove convergence of direction learning with finite exploration.

3. **Formalize the LLM Reason step**: Provide the exact prompt template. Run a sensitivity analysis to prompt variation. If the LLM contribution is truly <1pp, consider presenting it as optional.

4. **Reframe "emergent"**: Replace "emergent adaptive behavior" with "environment-adaptive gating patterns" or similar.

5. **Add CATTS cost footnote**: Note the K=5 per-step overhead in the results table.

6. **Move coverage proxy to appendix**: The r=+0.75 on 6 points is not convincing enough for the main text.

---

## Summary

This paper presents a valuable empirical finding (signal-utility direction reversal) with a reasonable theoretical framework and a simple but effective method. The finding is the primary contribution and is well-supported. The main weaknesses are: (1) the theoretical model is post-hoc and unfalsifiable, (2) single-backbone evaluation limits generalizability claims, and (3) the method is technically thin. Despite these concerns, the paper makes a contribution that the NeurIPS community would benefit from — the direction reversal phenomenon is real, important, and not previously documented. With multi-backbone validation, this would be a clear accept.

**Final Recommendation: Weak Accept (6/10)** — The finding is strong enough to carry the paper, but the theoretical and methodological contributions need strengthening to be confident it clears the NeurIPS bar.
