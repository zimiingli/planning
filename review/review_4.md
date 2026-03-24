# NeurIPS 2026 Peer Review

**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Reviewer**: Skeptical Empiricist
**Reviewer Confidence**: 4/5 (Strong familiarity with adaptive inference, test-time compute, LLM agents, and experimental methodology in ML)

---

## Overall Assessment

**Recommendation: Borderline Reject (4/10)**

The paper presents an interesting empirical observation -- that the Spearman correlation between uncertainty signals and optimizer utility can flip sign across agent environments -- and proposes a simple method (EAAG) to discover environment-specific gating directions. The core observation has merit and could influence how the community thinks about adaptive compute. However, the paper's empirical claims are substantially overclaimed relative to the evidence. The headline "34 wins vs. 2 losses" obscures the fact that only 18/30 (60%) of those comparisons are statistically significant. The Spearman correlations that drive the entire narrative are often tiny in magnitude (several |rho| < 0.05) with no confidence intervals reported in the main text. The 3-seed, 200-episode evaluation protocol is underpowered for the precision the claims require. The environment selection appears designed to demonstrate the phenomenon rather than to test it. The cost metric systematically favors EAAG by excluding exploration overhead. Collectively, these issues mean the paper's strongest claims are not adequately supported by the evidence presented.

---

## Scores

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| **Novelty** | 6 | Direction reversal observation is interesting but the theoretical explanation is post-hoc. |
| **Significance** | 6 | Could matter if the finding is real, but evidence is insufficient to be sure. |
| **Technical Soundness** | 4 | Systematic overclaiming, underpowered evaluation, misleading headline statistics. |
| **Clarity** | 7 | Well-written narrative, but the clarity makes overclaims more persuasive than they should be. |
| **Experimental Design** | 4 | Underpowered seeds, no CIs in main text, deployment-only cost metric, cherry-picked environments. |
| **Reproducibility** | 5 | Single backbone, no code/data release mentioned, LLM reasoning step not formalized. |

---

## Key Strengths

### S1: The direction-reversal observation is genuinely interesting
The contrast between FEVER (rho_entropy = -0.119) and APPS Interview (rho_entropy = +0.317) is a real and non-obvious phenomenon. If robustly established, this would be a useful finding for the adaptive compute community. The framing via Simpson's paradox is elegant.

### S2: The BSW ablation provides the strongest evidence
The wrong-direction ablation (BSW) is the most convincing piece of evidence in the paper. Deliberately reversing gate direction causes catastrophic degradation (-37.0pp on HotpotQA, -23.2pp on WebShop) and even drops performance below the no-trigger baseline (MLP wrong-direction: 45.3% < base 49.0%). This is interventional, not merely correlational, and it is the single best argument that direction matters.

### S3: Honest FEVER limitation
The authors transparently discuss EAAG's poor FEVER performance (49.8% vs. always-trigger 99.8%), trace it to exploration bias at step-0, and even note that this failure is predicted by their theoretical model. This intellectual honesty is commendable.

### S4: Comprehensive baseline coverage
Comparing against 6 contemporary methods across 8 environments represents substantial experimental effort. The method classification table (Table 3) clearly positions the contribution in the landscape.

---

## Major Concerns

### M1: The "34 wins vs. 2 losses" headline is misleading (Critical)

The paper's most prominent empirical claim -- repeated in the abstract, introduction, results, and conclusion -- is "34 wins vs. 2 losses against 6 competing methods." This metric is seriously misleading for several reasons:

**Only 18 of 30 comparisons (60%) are statistically significant.** The authors' own significance data (tab_significance/data.csv) reveals that 12 of the 34 "wins" have 95% bootstrap confidence intervals that include zero. Concretely:

- **HotpotQA**: EAAG vs. CaTS delta = +2.0pp, CI = [-0.5, 4.7] -- NOT significant. EAAG vs. AUQ delta = -1.8pp, CI = [-4.0, 0.3] -- NOT significant. EAAG vs. s1 delta = -1.8pp, CI = [-4.2, 0.3] -- NOT significant. Two of these are actually losses that are counted as environment-level wins elsewhere.
- **TWExpress**: EAAG vs. CoRefine delta = +1.5pp, CI = [0.0, 3.0] -- NOT significant. EAAG vs. CATTS delta = +1.5pp, CI = [0.0, 3.0] -- NOT significant.
- **Plancraft**: ALL 6 comparisons are non-significant except vs. s1. EAAG vs. SEAG = -1.5pp, EAAG vs. CATTS = -1.7pp -- these are numerically losses.

The paper should report: "Of 30 pairwise comparisons, EAAG achieves 18 statistically significant wins and 0 statistically significant losses, with 12 comparisons indistinguishable from the baseline." This is still a positive result, but the current framing inflates the apparent evidence.

**The win/loss table (tab_winloss/data.csv) uses a different counting method than the significance table.** The win/loss table counts 6 environments each for AUQ and s1_budget but only 6 for others. Cross-referencing with tab_significance (which only covers 6 environments: HotpotQA, APPS, WebShop, TWExpress, Plancraft, and -- missing -- FEVER, APPS Intv, CRUXEval), I find that the significance table covers only 6 of 8 environments. The remaining 2 environments' significance is unreported, meaning the 34W/2L claim is not fully testable from the data provided.

**Severity: High.** This is the paper's marquee claim and it is materially overstated.

### M2: Spearman correlations are weak and lack confidence intervals (Critical)

The entire theoretical narrative rests on the sign and magnitude of Spearman rho values, yet these values are often tiny and reported without confidence intervals:

**Weak correlations presented as meaningful:**
- HotpotQA entropy rho = -0.041 (n=1117). This is negligibly small. A 95% CI would be approximately [-0.10, +0.02]. The sign could easily be positive.
- APPS Intro entropy rho = +0.012 (n=1567, p=0.63). The authors use this as a key example of "near-zero signal" but with p=0.63, this is indistinguishable from zero.
- WebShop entropy rho = -0.019 (n=3899). At n=3899, even tiny correlations can be "significant" but this is substantively meaningless.
- CRUXEval entropy rho = -0.048. Weak.
- Plancraft entropy rho = -0.016 (n=1548). Indistinguishable from zero.

**Stronger correlations deserve scrutiny too:**
- APPS Interview entropy rho = +0.317 (n=439). This is the strongest positive signal but the sample size is among the smallest.
- FEVER entropy rho = -0.119 (n=282). With n=282, the 95% CI is approximately [-0.23, -0.01], so the sign is likely real but the magnitude is uncertain.

The paper builds its "direction reversal" story primarily on the FEVER-vs-APPS-Interview contrast, but 5 of 8 environments have |entropy rho| < 0.05 -- effectively zero. The honest characterization is: "entropy carries a measurably non-zero signal in exactly 3 of 8 environments (FEVER, APPS Interview, TWExpress), is negligible in the remaining 5, and the sign differs between FEVER/TWExpress (negative) and APPS Interview (positive)." This is a much weaker finding than "direction reverses across 8 environments."

**The strongest non-entropy signals (step_count rho = -0.494 to -0.619) are more consistently directional,** suggesting the real story may be simpler: step_count is the universally dominant signal (selected in 6/7 environments), and its direction is consistently negative except in CRUXEval (+0.184). The "direction reversal" narrative is primarily about entropy, which is a weak signal in most environments.

**No confidence intervals are reported for any rho value in the main text.** For a paper whose entire argument rests on the sign and relative magnitude of correlations, this is a serious omission.

**Severity: High.** The core finding may be real but is substantially overclaimed.

### M3: 3-seed evaluation with 200 episodes is underpowered (Major)

Each method-environment pair is evaluated with 3 seeds of 200 episodes each (600 total episodes). For binary success/failure outcomes, the standard error of a success rate estimate at p=0.50 is sqrt(0.25/600) = 2.04%. A 95% CI is approximately +/-4pp.

This means that for comparisons where the delta is less than ~4pp, the result is expected to be non-significant under this protocol. From the data:

- HotpotQA: EAAG 95.2% vs. CaTS 93.2% = +2.0pp. Below detection threshold.
- TWExpress: EAAG 99.0% vs. SEAG 97.3% = +1.7pp. Below detection threshold.
- Plancraft: EAAG 23.3% vs. CATTS 25.0% = -1.7pp. Below detection threshold. This is actually a loss.
- APPS Intv: EAAG 73.0% vs. CaTS 66.2% = +6.8pp. Detectable but borderline.

The protocol is adequate for large effects (WebShop: +13.3pp vs. CaTS) but insufficient for the precision needed to declare wins in environments where performance differences are small. This is particularly problematic because the paper claims wins in ALL environments -- if it limited claims to environments with large, significant effects (WebShop, APPS Intro vs. some baselines, TWExpress vs. some), the argument would be more credible.

**Recommendation:** Either (a) increase to 5+ seeds with more episodes, (b) restrict win/loss claims to statistically significant comparisons, or (c) use a more conservative claim like "EAAG is competitive or superior in all environments and significantly superior in X of Y."

**Severity: Major.** Insufficient power for the precision of claims made.

### M4: Environment selection appears designed to fit the theory (Major)

The writing guide states that environments were "selected to cover the full range of the Two-Source Model -- from pure Type I (FEVER) through mixed (APPS Intro) to Type D (APPS Interview), including extreme rollout properties (TWExpress: rollout-safe; Plancraft: rollout-harmful)."

This is selection bias. The environments were chosen because they exhibit the phenomenon the paper wants to demonstrate, not as an unbiased test of whether the phenomenon exists. The table tab_env_setup/data.csv explicitly labels environments with their "paper_role" -- "Main", "Main (weak signal)", "Diagnostic (safe)", "Diagnostic (harmful)", "Appendix" -- revealing that the environments serve a rhetorical function, not an experimental one.

**Specific concerns:**

1. The 8 environments were chosen to span the Two-Source Model's spectrum. But how many environments were screened to find these 8? If the authors tried 20 environments and picked 8 that showed the clearest reversal, this is cherry-picking.

2. Of the 8 environments, only 3 (FEVER, APPS Interview, TWExpress) show entropy rho with |value| > 0.05. The remaining 5 have near-zero entropy correlations. The "direction reversal" story critically depends on FEVER vs. APPS Interview -- removing either would substantially weaken the narrative.

3. The paper uses non-entropy signals (step_count, num_available_actions) as evidence of "signal replacement" (Observation 2), but these signals are confounded with trajectory position and environment structure. Step_count having a strong negative correlation with utility is predictable -- later steps tend to be in harder states.

**What would strengthen the paper:** A pre-registered environment selection protocol, or a held-out environment prediction test where the Two-Source Model predicts rho direction before any experiments are run.

**Severity: Major.** The evidence base is potentially cherry-picked.

### M5: Cost metric systematically favors EAAG (Major)

The paper defines cost as "deployment rollout budget" and explicitly states: "Cost measures only the deployment rollout budget -- calibration or exploration overhead is excluded for all methods, ensuring a fair comparison of runtime efficiency" (Section 5.1).

This is not fair. It systematically advantages EAAG over baselines:

1. **EAAG's exploration cost is hidden.** EAAG requires 50 exploration episodes with epsilon=0.5 random gating, plus LLM reasoning. None of this is counted.

2. **Phase 1 costs for baselines are hidden.** CaTS, SEAG, CoRefine, and SCG require 200 episodes of always-trigger for calibration. This is noted with a dagger symbol but not reflected in cost.

3. **The asymmetry is real.** EAAG's exploration costs ~25 equivalent always-trigger episodes (50 episodes at 50% trigger rate). Baselines cost 200 episodes. If setup costs were included, EAAG would look even better against baselines. Conversely, comparing against methods with NO setup cost (CATTS, AUQ, s1_budget), EAAG's hidden 50-episode cost is a real disadvantage.

4. **CATTS per-step cost is hidden in a different way.** CATTS runs K=5 forward passes per step for voting but this overhead is not in the "Cost" column. The paper mentions this in Related Work but not in the results table, making CATTS appear artificially cheap (0.06 ro/ep on FEVER).

The paper should present total lifecycle cost (setup + deployment) as the primary metric, or at minimum present both metrics side by side.

**Severity: Major.** Readers comparing Cost columns across methods will draw incorrect conclusions.

---

## Detailed Concern: Are the Ablation Conclusions Robust?

### M6: "Direction >> signals >> complexity" hierarchy is overclaimed

The paper argues a clean hierarchy: direction learning matters most, then multi-signal features, then gate complexity. Let me examine each claim against the data:

**Direction matters most (BSW ablation):** The BSW data shows catastrophic degradation in HotpotQA (-37.0pp), WebShop (-23.2pp), and FEVER (-36.8pp). But in APPS Interview, BSW achieves 79.5% = always_trigger 79.5%, meaning direction reversal has zero effect. In CRUXEval, BSW = 87.5% vs. always = 99.5% -- a 12.0pp gap, but this is smaller than the other environments. The degradation correlates with |rho| of the strongest signal, which is reasonable, but the result is dominated by 3 environments.

**Multi-signal > single-signal (AUC hierarchy):** The data shows single entropy AUC ~ 0.50-0.56, best single signal AUC = 0.74-0.90, multi-signal LR AUC = 0.74-0.92. However:
- In APPS, multi_signal_lr (0.761) < best_single (0.778). More features are worse.
- In Plancraft, multi_signal_lr (0.736) = best_single (0.736). No improvement.
- The claim "AUC ~ 0.83" for multi-signal is accurate only for HotpotQA (0.851). The average across 4 environments is (0.851 + 0.761 + 0.924 + 0.736)/4 = 0.818, and the paper rounds this up to ~0.83.

**LLM contributes almost nothing:** The fig5_llm_ablation data shows that removing the LLM changes SR by: WebShop +0.1pp, TWExpress -0.2pp, APPS +0.2pp, HotpotQA -0.6pp, FEVER +9.1pp, Plancraft -3.9pp. In 4/6 environments, the effect is < 1pp. In Plancraft, removing the LLM IMPROVES performance by 3.9pp. Only FEVER shows a substantial positive LLM contribution (+9.1pp). Yet the paper argues the LLM provides "robustness, not accuracy" -- this is a creative reframing of "the LLM barely helps and sometimes hurts."

The hierarchy is partially supported but the evidence is weaker and more nuanced than presented. A fairer summary: "Direction is the dominant factor in environments with strong signals; multi-signal features help in some but not all environments; the LLM is negligible in most environments and harmful in one."

**Severity: Medium-High.** The conclusions are directionally correct but overclaimed.

---

## Minor Concerns

### m1: "Emergent adaptive behavior" is misleading terminology
The paper repeatedly describes EAAG's varying trigger rates as "emergent." Trigger rates vary because the logistic regression weights differ across environments, which is exactly what supervised learning does -- it fits different parameters to different data. There is nothing emergent about it. Using "emergent" in a paper that cites Schaeffer et al. (2023) -- a paper whose entire point is that "emergent abilities" may be measurement artifacts -- is ironic and should be reconsidered.

### m2: The Two-Source Model environment mapping is circular
Table 5 maps environments to their "dominant uncertainty type" and predicts rho direction. But the mapping is derived from the observed rho, making the "prediction" circular. The InfoPoor/InfoRich manipulation (controlled reversal) partially addresses this but the InfoPoor result (entropy rho = +0.119, weakly positive) contradicts the Type I prediction of negative rho. The authors acknowledge this but attribute it to "small sample and mixed early-step Type D component" -- which is an ad hoc rescue.

### m3: Proposition 1 is trivially true by construction
If environment E1 has d* = +1 and E2 has d* = -1, then no fixed d can satisfy both. This is a restatement of the definition, not a theorem. A more informative result would bound the sample complexity of direction discovery or characterize conditions under which EAAG's exploration phase correctly identifies the direction.

### m4: Coverage proxy is too weak for publication
The information coverage proxy achieves r = +0.75 on 6 data points (p = 0.086) only after excluding an outlier (TWExpress). Including all 7 points gives r = +0.27 (p = 0.56) -- completely non-significant. The operationalizations are ad hoc (evidence_count/3 for HotpotQA, step_count/7 for FEVER) with no justification for the denominators. This analysis should be removed or significantly strengthened.

### m5: Missing multiple comparison correction
The significance table reports 30 pairwise comparisons. At alpha = 0.05 without correction, 1.5 false positives are expected by chance. With Holm-Bonferroni correction, several of the borderline-significant results (e.g., TWExpress vs. CaTS, delta = 2.3pp, p < 0.05 uncorrected) would likely become non-significant. The writing guide mentions Holm-Bonferroni but the data file does not indicate it was applied.

### m6: Stratified reversal analysis has inconsistencies
The stratified reversal data (fig_stratified_reversal/data.csv) shows some patterns that do not match the main text claims:
- APPS: Early rho = -0.0006 (p=0.99), Mid rho = -0.1814 (p < 0.001), Late rho = -0.0331 (p=0.50). The reversal from early to late is non-monotonic and the late stratum is non-significant.
- WebShop: Early rho = +0.076 (p=0.001), Mid rho = -0.031 (p=0.35), Late rho = +0.046 (p=0.11). No clear directional pattern -- early and late are both weakly positive.
- FEVER: ALL strata non-significant (p > 0.44). Yet the paper claims FEVER is the strongest Type I environment.
- APPS Intv: Mid and Late strata have rho = NaN (insufficient data).

These inconsistencies undermine the claim that "direction reversal persists within trajectory-length strata."

### m7: No held-out environment test
The Two-Source Model is proposed and verified on the same 8 environments. A convincing test would be to predict rho direction for a 9th environment based solely on its task description (before running experiments). Without this, the model remains unfalsifiable.

### m8: Trigger rate data contradicts claims
The paper claims Plancraft trigger rate "starts at 49% but decays to <20% at later steps." The actual data shows: step 0: 0.489, step 5: 0.279, step 10: 0.271, step 15: 0.132, step 20: 0.250, step 25: 0.091, step 28: 0.355, step 29: 0.323. The decay is non-monotonic and the trigger rate actually increases at later steps (steps 28-29). The description oversimplifies the data.

---

## Questions for Authors

1. How many environments were considered before selecting these 8? Was there a principled stopping criterion, or were environments added/removed based on initial results?

2. Can you report 95% bootstrap CIs for all Spearman rho values in Table 2? Several values (rho = -0.041, -0.019, -0.016) are likely to have CIs that include zero.

3. The significance table covers only 6 of 8 environments. Why are FEVER, APPS Interview, and CRUXEval missing from the significance analysis? (Or is the "APPS" row covering APPS Intro only?)

4. Would you accept a revision where the 34W/2L claim is replaced with "18 statistically significant wins, 0 significant losses, 12 indeterminate" or equivalent?

5. Have you run any experiments with a second backbone? Even preliminary results on 2-3 environments would substantially strengthen the generalizability claim.

6. Total lifecycle cost (exploration/calibration + deployment): can you add a table showing this for all methods? This would clarify the cost comparison.

---

## Recommendation

The core observation -- that entropy-utility correlations can have different signs in different environments -- is interesting and potentially important. The BSW ablation provides genuine causal evidence that direction matters. However, the paper wraps this finding in a layer of overclaiming that makes it difficult to assess the true contribution:

- The 34W/2L headline is misleading (40% of wins are non-significant).
- The rho values driving the narrative are mostly negligible in magnitude.
- The evaluation is underpowered for the precision of claims.
- The environment selection appears post-hoc.
- The cost metric is not apples-to-apples.

I would reconsider my score if the authors: (1) replace the 34W/2L claim with significance-adjusted counts, (2) add CIs for all rho values and restrict "direction reversal" claims to environments where the CI excludes zero, (3) add a second backbone even on a subset of environments, and (4) present total lifecycle cost.

**Current recommendation: Borderline Reject (4/10).**
