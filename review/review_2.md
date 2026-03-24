# NeurIPS 2026 Peer Review

**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Reviewer Profile**: Theoretical ML researcher specializing in learning theory, statistical decision theory, and formal guarantees
**Reviewer Confidence**: 3/5 (Familiar with the theoretical framework and statistical methodology; less familiar with specific agent benchmarks)

---

## Overall Assessment

**Recommendation: Borderline Reject (5/10)**

The paper documents an empirically interesting phenomenon—that the Spearman correlation between uncertainty signals and optimizer utility flips sign across agent environments—and frames it through a "Two-Source Model" invoking Simpson's paradox. While I find the empirical observation valuable, the theoretical apparatus surrounding it is substantially weaker than presented. Proposition 1 is a tautology dressed in formal notation. The Two-Source Model is a parametric curve-fitting exercise with more free parameters (alpha, beta, p_I per environment) than observable constraints (sign of rho), rendering it unfalsifiable in its current form. The connection to Simpson's paradox is invoked but never rigorously instantiated. And the "testable predictions" P1-P3 are better described as post-hoc pattern descriptions than deductions from the model. From a theoretical ML standpoint, the paper promises formal guarantees ("provably incomplete," "necessary condition") but delivers something closer to a verbal argument with mathematical notation. If the authors positioned this purely as an empirical finding paper with a suggestive conceptual model, my assessment would be more favorable. The overclaiming of theoretical rigor is what lowers my score.

---

## Scores

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| **Novelty** | 6 | The empirical observation is novel. The theory and method are not. |
| **Significance** | 6 | Potentially high if the finding generalizes beyond one backbone; currently uncertain. |
| **Technical Soundness** | 4 | Proposition 1 is trivial; Two-Source Model is unfalsifiable; Simpson's paradox connection is informal. |
| **Clarity** | 7 | Well-written narrative, though the clarity is partially illusory—it obscures the thinness of the formal content. |
| **Experimental Design** | 6 | Good breadth (8 environments), but single backbone and lack of statistical rigor in many comparisons. |
| **Reproducibility** | 6 | Setup described in reasonable detail; code/data availability unclear. |

---

## Key Strengths

### S1: The empirical phenomenon is real and practically important
The direction reversal observation—entropy correlates negatively with rollout utility in FEVER (rho = -0.119) but positively in APPS Interview (rho = +0.317)—is well-documented through multiple lenses: raw correlations, stratified analysis controlling for trajectory length, and the BSW ablation providing interventional evidence. The BSW result (wrong-direction gating drops HotpotQA SR by 37pp, with MLP falling below the no-trigger baseline at 45.3% vs. 49.0%) is the strongest evidence in the paper and is genuinely informative. This finding, on its own, has value for the adaptive compute community.

### S2: The ablation hierarchy is informative
The demonstration that direction >> signal count >> gate complexity (Table 5 / gate capacity ablation) is a clean and useful result. The fact that a logistic gate with correct direction matches a hidden-state probe (both ~95% on HotpotQA) while an MLP with wrong direction falls below baseline is a striking illustration that getting the direction right is the primary concern. This is the paper's most convincing bridge from empirical finding to method design.

### S3: Honest treatment of failures
The FEVER limitation (EAAG at 49.8% vs. always-trigger at 99.8%) is discussed transparently. The coverage proxy analysis (r = +0.75 on 6 points, p = 0.086) is presented with appropriate caveats. This intellectual honesty is appreciated.

---

## Major Concerns

### M1: Proposition 1 is a tautology, not a theorem

Proposition 1 states: if two environments have opposite true directions d*(E1) = +1 and d*(E2) = -1, no fixed-direction gate can achieve non-negative VOC in both. The proof is two lines: if d = +1, it fails in E2; if d = -1, it fails in E1. This is the definition of "opposite directions" restated in notation. It is logically equivalent to: "if A and not-A cannot both hold, then no single choice satisfies both"—a propositional tautology.

The paper claims this establishes that "direction discovery is a *necessary condition* for cross-environment non-negative value of computation." But this is only non-trivial if one first proves that opposite-direction environments *exist* (an empirical claim, not a theoretical one) and that the signal-utility relationship is monotonic (which is assumed, not proven). The proposition contributes no insight beyond what the empirical observation already provides.

**What would constitute a real theoretical contribution:**
- A sample complexity bound: "With N exploration episodes, LASSO-based direction learning recovers the correct sign(rho) with probability at least 1 - delta, where N = O(d log(d) / rho^2)."
- A quantitative wrong-direction damage bound: "If the true correlation is rho* and the gate uses direction -sign(rho*), then SR(g, E) <= SR(base, E) - Omega(|rho*| * headroom)."
- A PAC-style guarantee for the full EAAG pipeline: "After N_explore episodes of epsilon-greedy exploration, EAAG's learned gate satisfies SR >= SR(oracle) - epsilon with probability >= 1 - delta."

Any of these would be a substantive theoretical result. The current proposition is not.

### M2: The Two-Source Model is unfalsifiable in its present form

The model posits: U_I(s) ~ -alpha * H(s) + epsilon_I and U_D(s) ~ +beta * H(s) + epsilon_D, with mixing proportion p_I(E). This yields sign(rho) = sign(beta - (alpha + beta) * p_I). There are three free parameters (alpha, beta, p_I) and one observable (sign of rho). For any observed sign, one can choose p_I to match. The model is therefore unfalsifiable: no pattern of observed rho signs across environments could contradict it.

The authors claim the environment-to-type mapping "is not a free parameter of the model—it follows directly from the environment's information structure." But this mapping is constructed *after* observing rho and rationalized through post-hoc narratives (e.g., "FEVER requires finding specific evidence" therefore Type I). A genuine a priori mapping would require an operationalized definition of "information poverty" that can be computed from the environment specification before running any experiments.

The coverage proxy (Section 5.7) is an attempt to address this but is unconvincing: the proxy definitions are ad hoc (evidence_count/3 for HotpotQA, step_count/7 for FEVER—why these denominators?), the correlation is computed on 6 points after excluding an outlier, and the resulting p = 0.086 is not significant at conventional levels. Including all 7 points gives r = +0.27, p = 0.56.

**What would make the model testable:**
- A formal operationalization of p_I that can be computed from environment transition dynamics (e.g., entropy of the state-conditional information gain distribution).
- Quantitative predictions: not just sign(rho) but a predicted magnitude, or a predicted ordering of |rho| across environments, that can be tested.
- A held-out validation: fit (alpha, beta) on a training set of environments, then predict rho direction on held-out environments.

### M3: The Simpson's paradox connection is superficial

The paper claims the direction reversal is "an instance of Simpson's paradox." Simpson's paradox has a precise meaning in causal inference (Pearl, 2014): a statistical association that reverses upon conditioning on a confounding variable, where the confounded and unconfounded associations have different causal interpretations. The proper formalization requires a causal DAG specifying the relationships among the signal H, the latent type Z in {I, D}, and the utility U.

The paper's usage is informal: "aggregating heterogeneous subpopulations with opposing within-group trends reverses the aggregate correlation." This is the definition of a mixture effect, which is related to but not identical with Simpson's paradox. In a proper Simpson's paradox formalization, one would need to show:
1. Within Type I states: Corr(H, U) < 0.
2. Within Type D states: Corr(H, U) > 0.
3. Marginally (aggregating): Corr(H, U) can be either sign depending on the mixture.
4. The causal effect of H on U differs from the marginal association.

The paper establishes (3) empirically but (1) and (2) are *assumed by construction* of the model (the linear conditional models U_I ~ -alpha*H and U_D ~ +beta*H are stipulated, not derived or verified). And (4) is never discussed. Without a causal DAG and proper identification analysis, calling this "Simpson's paradox" rather than "a mixture effect" is imprecise and potentially misleading. The invocation of Pearl (2014) adds false authority to an informal analogy.

### M4: The linear conditional model lacks testable implications beyond sign(rho)

The model assumes U_I ~ -alpha * H + epsilon and U_D ~ +beta * H + epsilon with constant alpha, beta > 0. This implies:
- Within Type I states, utility is a decreasing linear function of entropy.
- Within Type D states, utility is an increasing linear function of entropy.
- The conditional relationships are homogeneous across environments (same alpha, beta).
- Noise terms epsilon_I, epsilon_D are independent of H.

None of these assumptions are tested. The paper only checks whether sign(rho) matches the predicted direction—the weakest possible test of a linear model. Stronger tests would include:
- Plotting U vs. H within identified state types to verify linearity.
- Testing whether the relationship is truly monotonic (nonlinearity would invalidate the model's core mechanism).
- Checking whether alpha and beta are approximately constant across environments (the model assumes universality of the conditional slopes).
- Verifying the independence assumption between noise and signal.

Without these checks, the linear model is an untested assumption, not a verified mechanism.

---

## Minor Concerns

### m1: P1-P3 are post-hoc pattern descriptions, not model-derived predictions

The paper presents three "testable predictions" derived from the Two-Source Model:
- **P1** (temporal dynamics): rho should decrease over the episode.
- **P2** (cross-environment consistency): similar environments should have similar rho.
- **P3** (signal identity alignment): Type I environments should have information-sufficiency signals; Type D should have decision-complexity signals.

However, none of these follow deductively from the formal model (Eq. 2: rho approx beta - (alpha+beta)*p_I). P1 requires an additional, unstated assumption that p_I increases monotonically over the episode—this is a separate claim about temporal dynamics, not a consequence of the mixture model. P2 requires the (tautological) assumption that "similar environments have similar p_I." P3 is about which *signal* is most informative, but the model is only about *entropy*—it says nothing about the relative informativeness of step_count vs. num_available_actions.

These are reasonable empirical hypotheses, but presenting them as "predictions derived from the model" overstates the model's deductive power. They are better described as auxiliary hypotheses consistent with the model's spirit.

### m2: The "necessity" framing conflates logical and practical necessity

The paper repeatedly says direction discovery is a "necessary condition" for cross-environment non-negative VOC. Formally, this means: without direction discovery, non-negative VOC across environments is *impossible*. But Proposition 1 only proves this under the assumption that opposite-direction environments exist and that the gate is a simple thresholding function g(s) = 1[d * sigma(s) > theta]. A more complex gate (e.g., a neural network that can learn arbitrary decision boundaries) could potentially achieve non-negative VOC without explicit "direction discovery" by learning a nonlinear mapping from signals to gating decisions. The necessity claim is contingent on the gate class being restricted to signed thresholding, which is not stated.

### m3: Statistical concerns with rho values

Several of the key rho values are small in magnitude: entropy rho = -0.041 (HotpotQA), -0.019 (WebShop), -0.048 (CRUXEval), -0.016 (Plancraft), +0.012 (APPS Intro). These are weak correlations that explain less than 0.2% of variance. The paper's narrative treats sign(rho) as the central quantity, but for these environments the sign is essentially noise. Only APPS Interview (+0.317), FEVER (-0.119), and TWExpress (-0.290) have correlations large enough to be practically meaningful. The fact that the *strongest* signal (step_count, num_available_actions) has much larger |rho| values (0.3-0.6) suggests that entropy is simply not the right signal to build the theoretical model around.

### m4: The epistemic/aleatoric analogy is strained

The paper maps Type I to epistemic uncertainty and Type D to aleatoric uncertainty, citing Hullermeier & Waegeman (2021). But the standard epistemic/aleatoric distinction is about *model uncertainty* (reducible with more data) vs. *inherent randomness* (irreducible). Type D ("decision difficulty—the agent faces multiple viable paths") is not aleatoric uncertainty in the standard sense; it is closer to a decision-theoretic concept of option value or branching factor. The analogy may confuse readers familiar with the standard ML uncertainty decomposition literature.

---

## Questions for Authors

1. **Can you state Proposition 1 without assuming the existence of opposite-direction environments?** As written, the proposition's hypothesis includes the conclusion. What would a non-trivial version look like—e.g., a bound on how much performance degrades as a function of direction mismatch magnitude |rho_gate - rho_true|?

2. **Can you derive P1 (temporal dynamics) formally from the Two-Source Model?** Specifically, what additional assumptions about the temporal evolution of p_I(t) are needed, and are these assumptions testable independently?

3. **What would falsify the Two-Source Model?** Given that (alpha, beta, p_I) are free parameters and only sign(rho) is predicted, is there any pattern of observations that would be inconsistent with the model? If not, the model is unfalsifiable by construction.

4. **Can you plot U vs. H within identified state subsets to verify the linear conditional model?** The model assumes U_I ~ -alpha*H and U_D ~ +beta*H. Are these relationships actually linear? Monotonic? What do the scatter plots look like?

5. **Have you considered fitting (alpha, beta) on a subset of environments and predicting rho direction on held-out environments?** This would provide a genuine test of the model's predictive power, rather than the current post-hoc consistency check.

6. **Why is the theoretical model built around entropy when entropy is not the most informative signal in 7/8 environments?** Table 1 shows step_count dominates in 6/8 environments and num_available_actions in 1/8. The model's exclusive focus on entropy H seems misaligned with the paper's own empirical findings about signal identity (Observation 2).

7. **For the gate capacity ablation (Table 5), what architecture is the MLP?** How many hidden layers, what width? The claim that "higher capacity makes performance worse with wrong direction" is interesting but needs to be demonstrated across a range of capacities, not just one MLP configuration.

8. **Can you provide confidence intervals for the rho values in Table 1?** Many of the entropy correlations are near zero. Bootstrap CIs on rho would clarify which direction assignments are statistically distinguishable from zero.

---

## Detailed Technical Assessment

### On the formal framework

The paper's mathematical content amounts to: (i) a two-component mixture model with linear conditional means and three free parameters; (ii) a sign condition derived by equating the mixture to zero; (iii) a trivial impossibility result for fixed-direction gates. None of these are technically deep. For a NeurIPS paper claiming theoretical contributions, I would expect at least one of the following:

- **Identifiability results**: Under what conditions can (alpha, beta, p_I) be identified from data? The EM algorithm would be natural here—is there a consistency result for EM applied to this mixture?
- **Sample complexity**: How many exploration episodes N suffice to learn the correct sign(rho) with high probability? This depends on |rho|, the sample size per episode, and the noise distribution. A finite-sample bound would be highly relevant for the 50-episode exploration budget.
- **Convergence guarantees for EAAG**: The LASSO step selects features and learns their signs. Under standard assumptions (sub-Gaussian design, restricted eigenvalue condition), LASSO is consistent. Can you invoke known LASSO theory to guarantee correct sign recovery?
- **Regret bounds**: EAAG uses epsilon-greedy exploration followed by LASSO. The online adaptation retrains every 30 episodes. Can you bound the cumulative regret relative to the oracle gate?

The absence of any such results makes the "theory" contribution feel like a conceptual framework rather than a mathematical one.

### On the Simpson's paradox framing

Pearl (2014) defines Simpson's paradox in terms of causal interventions: do(H = h) vs. conditioning on H = h can yield different associations depending on the causal structure. The paper's usage is purely associational—it observes that a marginal correlation reverses when conditioned on (the latent) type. This is better described as the ecological inference fallacy or mixture-induced marginal reversal. The Simpson's paradox label, while more recognizable, is technically imprecise.

A proper causal analysis would require: (1) a DAG specifying H -> U with Z as a confounder or mediator; (2) identification of the causal effect of H on U via adjustment or instrumental variables; (3) demonstration that the marginal and conditional effects differ in sign. The paper does none of this.

### On the "provably incomplete" language

The paper uses "provably incomplete" to describe fixed-direction methods. In formal logic and learning theory, "provably incomplete" has a specific meaning (related to Godel's theorems or impossibility results in computational learning theory). Here it means "there exist two environments where the method fails"—an existence claim, not an impossibility theorem. The phrasing is inflated.

---

## Summary

The paper's empirical contribution—demonstrating that signal-utility direction reverses across environments and that getting the direction right matters more than gate complexity—is solid and practically relevant. The BSW ablation is particularly compelling as interventional evidence. However, the theoretical framing is substantially weaker than presented: Proposition 1 is trivially true, the Two-Source Model is unfalsifiable with its current parameterization, the Simpson's paradox connection is informal, and the "testable predictions" are post-hoc descriptions rather than model-derived deductions. For a paper that positions itself as "Finding + Theory + Method," the theory component needs significant strengthening to meet the NeurIPS bar for theoretical contributions.

**Final Recommendation: Borderline Reject (5/10)** — The empirical finding is strong enough that I would not strongly argue against acceptance, but the gap between what the paper claims theoretically and what it actually delivers is large enough to warrant concern. Strengthening Proposition 1 with quantitative bounds, providing a falsifiable operationalization of p_I, and adding sample complexity guarantees for EAAG's exploration phase would raise my score to a clear accept.
