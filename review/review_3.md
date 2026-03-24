# NeurIPS 2026 Peer Review

**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Reviewer**: Reviewer 3
**Reviewer Expertise**: LLM agent systems, ReAct/LATS/tree search, multi-step agent evaluation, test-time compute scaling, agent benchmarks
**Reviewer Confidence**: 4/5 (I have published on agent evaluation benchmarks, test-time compute allocation, and tree search methods at NeurIPS/ICML)

---

## Overall Assessment

**Recommendation: Borderline Accept (6/10)**

This paper identifies a real and practically important phenomenon: the direction of the correlation between uncertainty signals and optimizer utility reverses across agent environments. The empirical evidence for this reversal across 8 environments is convincing, and the interventional BSW ablation elevates it beyond mere correlation. The paper is well-written with a strong narrative arc.

However, I have substantive concerns about three axes: (1) the "optimizer T" abstraction papers over critical mechanistic differences between per-action evaluation, K-variant sampling, and LLM-Propose-K, making it unclear whether direction reversal is an environment property or an optimizer-environment interaction; (2) the single-backbone evaluation (Qwen3-4B) is a serious gap given that larger models with better in-context learning could fundamentally change the signal-utility landscape; and (3) the paper does not engage with RL-based adaptive compute methods (AdaptThink, Thinkless) as baselines, despite these methods implicitly learning direction through policy optimization -- a direct comparison would clarify EAAG's contribution relative to the most natural alternative.

The finding is valuable enough to merit publication, but the paper as submitted leaves too many confounds uncontrolled to support its strongest claims.

---

## Scores

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| **Novelty** | 7 | Direction reversal finding is novel and actionable. Method is standard. |
| **Significance** | 7 | Could reshape adaptive compute design if the finding generalizes beyond Qwen3-4B. |
| **Technical Soundness** | 5 | Core finding is solid, but optimizer heterogeneity is uncontrolled; Proposition 1 is trivial; Two-Source Model is post-hoc with unidentifiable parameters. |
| **Clarity** | 8 | Excellent writing. Strong narrative structure. Concrete numbers throughout. |
| **Experimental Design** | 5 | 8 environments provide breadth, but single backbone, heterogeneous optimizers, and missing RL baselines weaken causal claims. |
| **Reproducibility** | 6 | Setup described but code/data availability unclear. LLM reasoning step underspecified. |

---

## Key Strengths

### S1: The direction reversal finding is empirically robust and practically important

The core observation -- that entropy correlates negatively with rollout utility in FEVER (rho=-0.119) but positively in APPS Interview (rho=+0.317) -- is not a marginal effect. It is corroborated by three layers of evidence: (a) raw Spearman correlations across 8 environments, (b) stratified analysis controlling for trajectory length showing the reversal persists within strata, and (c) the BSW ablation providing interventional evidence (wrong direction causes -37.0pp on HotpotQA, with MLP falling below the no-trigger baseline at 45.3% < 49.0%). This is stronger evidence than most papers in this space provide. The practical implication is clear: any practitioner deploying adaptive compute must characterize signal semantics per environment, or risk active harm.

### S2: The information hierarchy insight (direction >> signal count >> gate complexity) is the paper's most actionable contribution

The gate capacity ablation (Table tab:capacity) is elegant: logistic regression with correct direction achieves ~95% SR on HotpotQA; MLP with wrong direction achieves 45.3%. This inverts the conventional wisdom that more powerful gating functions are better. For practitioners, this is immediately useful -- it says "spend your budget on understanding the environment, not on building a fancier gate." This insight extends beyond EAAG to any adaptive compute system.

### S3: The 34W/2L record across 6 baselines and 8 environments demonstrates broad applicability

While individual wins may be noisy, the aggregate pattern is hard to dismiss. EAAG achieves this without Phase 1 calibration data (unlike CaTS, SEAG, CoRefine, SCG which require 200 always-trigger episodes), making its wins more impressive when accounting for total data efficiency. The Pareto-dominance in 5/6 shared environments with CaTS is a strong result.

---

## Major Concerns

### M1: The "optimizer T" abstraction is too coarse and conflates environment effects with optimizer effects

This is my most significant concern. The paper treats "optimizer T" as a black box and attributes direction reversal entirely to the environment's information structure. But the 8 environments use three fundamentally different optimizer types:

- **Per-action evaluation** (HotpotQA, FEVER, TWExpress, Plancraft): generates K=5 candidate actions, scores each with a reward model, selects best. This is essentially Best-of-N at the action level.
- **K-variant sampling** (APPS Intro, APPS Interview, CRUXEval): generates K=3 complete code solutions, tests each against test cases, selects passing one. This is solution-level resampling with execution feedback.
- **LLM-Propose-K** (WebShop): LLM proposes K=3 action sequences, simulates each, selects highest reward. This is a form of planning/rollout.

These optimizers have very different mechanisms for improving action quality. Per-action evaluation benefits from diversity in the candidate set (favoring high-entropy states). K-variant sampling benefits from the existence of a correct solution in the resampling distribution (which may or may not correlate with entropy). LLM-Propose-K benefits from the LLM's ability to plan ahead (which depends on state predictability, not entropy).

The paper's central claim is that direction reversal is an environment property (Type I vs Type D information structure). But an alternative explanation is that direction reversal is an **optimizer-environment interaction**: per-action evaluation naturally benefits from decision-difficulty states (Type D), while K-variant sampling may benefit differently depending on whether the problem has a narrow solution space (code) vs. broad (web shopping). The paper cannot distinguish these explanations because optimizer type is perfectly confounded with environment category.

**What would resolve this**: Run the same optimizer (e.g., per-action evaluation) across 3-4 environments from different categories. If direction still reverses, the environment explanation holds. If not, the optimizer type is the primary driver.

**Severity: High.** This confound undermines the paper's strongest theoretical claim.

### M2: Single backbone (Qwen3-4B) is inadequate for the generality of the claims

The paper claims direction reversal is a property of the environment's information structure, independent of the model. But Qwen3-4B is a relatively small model with known calibration limitations. Larger models (e.g., 32B, 70B) with better in-context learning could exhibit fundamentally different signal-utility landscapes:

1. **Better calibration**: A well-calibrated model's entropy would more accurately reflect true uncertainty, potentially eliminating the "information poverty" failure mode where entropy is high but rollouts are useless. If a 70B model's entropy correctly distinguishes "I lack information" from "I face a hard choice," the direction reversal phenomenon might weaken or disappear.

2. **Better base performance**: A stronger model has higher base SR and lower headroom for optimizer improvement. In environments where Qwen3-4B achieves 49% base SR (HotpotQA), a 70B model might achieve 85%, fundamentally changing the utility landscape.

3. **Different uncertainty structure**: In-context learning quality affects whether uncertainty is epistemic (reducible by more computation) or aleatoric (irreducible). A model with stronger ICL would shift the Type I/Type D balance within each environment.

The paper cites Tao et al. (2025) as independent evidence that uncertainty semantics vary across tasks for diverse models. But Tao et al. study calibration quality, not signal-utility direction -- these are different phenomena. The claim that direction reversal is model-independent requires direct evidence with at least one alternative backbone.

**Severity: High.** Without multi-backbone evidence, the paper's generalization claims rest entirely on theoretical arguments that have not been empirically validated.

### M3: RL-based methods (AdaptThink, Thinkless) are the most natural comparison and are missing from the baselines

The paper mentions AdaptThink and Thinkless in Related Work but does not include them as baselines. This is a significant omission because these methods **implicitly learn direction through reinforcement learning** -- exactly the capability that the paper argues is necessary. They represent the strongest alternative to EAAG's explicit direction discovery:

- **AdaptThink** learns a think/no-think policy via RL (GRPO), which implicitly learns when extra computation is beneficial. If the optimal policy in a Type I environment is "don't think," AdaptThink should learn this through reward signal, effectively discovering direction without explicit signal-utility analysis.
- **Thinkless** uses DeGRPO to learn hybrid short/long-form reasoning, with the RL reward implicitly capturing when extended reasoning helps vs. hurts.

The paper argues these methods "require per-environment training and provide no interpretable direction signal." But EAAG also requires per-environment exploration (50 episodes). The key question is: **does explicit direction discovery (EAAG) outperform implicit direction learning (RL)**? This is the central methodological comparison the paper should make.

Without this comparison, EAAG's practical contribution is unclear. If AdaptThink/Thinkless achieve comparable performance while also learning direction implicitly, EAAG's explicit three-step pipeline adds complexity without benefit. If they fail in cross-environment settings (which the paper's theory predicts), that would be powerful evidence for the paper's thesis.

**Severity: Medium-High.** The absence of RL baselines leaves the paper's methodological contribution poorly positioned.

### M4: The 50-episode exploration budget is unjustified and its practicality is questionable

The paper fixes N_explore = 50 with no sensitivity analysis in the main text (Appendix E mentions it is "stable for N >= 30" but provides no data). Several concerns:

1. **Cost in real deployments**: 50 episodes with epsilon=0.5 random gating means approximately 25 episodes where the optimizer fires unnecessarily and 25 where it does not fire when it should. In real-world deployments (e.g., customer-facing web agents), these 50 "exploration episodes" represent degraded service. The paper does not discuss this practical constraint.

2. **Sufficiency for direction discovery**: The claim that 50 episodes reliably discover direction is not theoretically grounded. In environments with high variance (WebShop: base 7.2% SR) or sparse signal (CRUXEval, Plancraft), 50 episodes may produce noisy estimates of rho. The FEVER failure (49.8% vs 99.8%) is partially attributed to exploration bias -- would 100 or 200 episodes fix FEVER? If so, the 50-episode budget is too low. If not, the exploration strategy itself is flawed.

3. **Comparison fairness**: CaTS, SEAG, CoRefine, and SCG require 200 always-trigger episodes for Phase 1 calibration. The paper argues EAAG is more data-efficient (50 vs 200). But the baselines' 200 episodes are always-trigger, providing maximal signal about optimizer utility. EAAG's 50 episodes are random-gated, providing noisier signal. The effective information content may be comparable.

4. **No convergence analysis**: A useful contribution would be proving or demonstrating that direction learning converges to the correct direction with probability 1-delta after N episodes, as a function of signal strength |rho|.

**Severity: Medium.** The fixed budget is a practical limitation that should be analyzed, not just stated.

---

## Minor Concerns

### m1: The FEVER failure (49.8% vs always-trigger 99.8%) is more severe than the paper acknowledges

The paper frames FEVER as an "honest limitation" and notes that EAAG matches fixed-direction baselines (~50%). But this framing obscures the magnitude of the problem:

- The gap is 50pp -- EAAG captures less than 1% of the available headroom (delta = +62.8pp, EAAG captures +12.8pp).
- SCG achieves 98.0% with Phase 1 data. If a practitioner has to choose between spending 50 episodes on EAAG exploration vs 200 episodes on SCG calibration, SCG is clearly preferable in FEVER-like environments.
- The theoretical explanation (step-0 concentration) suggests the failure is structural, not fixable by more exploration episodes. This means EAAG has a fundamental blind spot for environments with early-critical decision windows -- a common pattern in search-based tasks.

The paper should more clearly delineate when EAAG is appropriate vs when practitioners should fall back to Phase 1-based methods.

### m2: The 8 environments are not as diverse as claimed for evaluating real agent deployments

While the environments span several categories, they share important properties that limit representativeness:

- **All are single-turn or short-horizon**: Episode lengths range from a few steps (CRUXEval) to ~15 steps (HotpotQA, WebShop). Real agent deployments often involve 50-100+ steps (e.g., SWE-bench, complex web automation).
- **No tool-use environments**: Modern agent deployments heavily involve tool calling (code execution, API calls, database queries). None of the 8 environments test tool-use patterns.
- **No partially observable environments**: All environments provide the agent with relatively complete state observation. Real deployments often involve partial observability (e.g., unknown system state in DevOps agents).
- **No multi-turn dialogue**: Conversational agents with user interaction are a major deployment category, absent here.
- **Missing SWE-bench and similar**: Software engineering tasks are the most commercially relevant agent deployment and are not represented.

The paper claims environments are "selected to cover the full range of the Two-Source Model." This is theory-driven selection, which is fine for validating the model but does not establish broad practical applicability.

### m3: Win/loss counting without effect size or significance masks the quality of wins

The 34W/2L metric treats a 0.3pp win on CRUXEval the same as a 13.3pp win on WebShop. The significance table in the appendix shows only 18/30 comparisons are statistically significant, meaning 12 of the 34 "wins" may be within noise. A more informative metric would be:

- Mean SR improvement across environments (weighted by headroom)
- Number of wins that are statistically significant (18/30)
- Number of environments where EAAG achieves >90% of oracle SR

The aggregate 34W/2L number, while impressive-sounding, may be inflating EAAG's practical advantage.

### m4: The "emergent adaptive behavior" framing is misleading

The paper describes EAAG's varying trigger rates (73% in TWExpress, 28% in WebShop) as "emergent adaptive behavior." This is logistic regression producing different output probabilities when given different input distributions. Calling this "emergent" invokes connotations from the emergent abilities literature (Schaeffer et al., 2023 -- a paper the authors explicitly cite and model their narrative structure after) that are inappropriate here. The behavior is fully explained by the learned LASSO coefficients and the input feature distributions -- there is nothing surprising or "emergent" about a linear model producing different predictions on different inputs. This framing should be replaced with "environment-adaptive gating patterns" or similar.

---

## Questions for Authors

1. **Optimizer confound**: Have you considered running the same optimizer type (e.g., per-action evaluation with K=5) across environments from different categories (e.g., HotpotQA + APPS Interview + WebShop) to disentangle the environment effect from the optimizer effect? If not, can you provide theoretical arguments for why the optimizer type should not affect direction?

2. **RL baseline comparison**: What is the specific reason AdaptThink and Thinkless are excluded as baselines? Is it infrastructure/compute constraints, or a principled argument that they are not comparable? Given that both methods implicitly learn direction through RL, they seem like the most relevant comparison points for EAAG's explicit direction discovery.

3. **Backbone sensitivity**: You state in limitations that "we would expect the same reversal pattern with different backbones." Have you tested this expectation at all, even informally? A single experiment on HotpotQA with Llama 3 8B showing the same negative rho would substantially strengthen the paper. Without it, this is an untested assumption underlying the entire theoretical framework.

4. **Exploration budget sensitivity**: You mention in Appendix E that EAAG is "stable for N_explore >= 30." Can you provide the actual SR values for N_explore in {10, 20, 30, 50, 100} on at least 2 environments? Specifically: does increasing N_explore to 100 or 200 fix the FEVER failure? If not, the exploration strategy itself needs redesign, not just more budget.

5. **Type prediction**: Given a natural-language description of a new environment (e.g., "An agent that debugs production code by reading logs, querying databases, and suggesting fixes"), can you predict whether it will be Type I or Type D before running experiments? If the Two-Source Model has predictive power, this should be possible. If not, the model's practical utility is limited to post-hoc explanation.

6. **Comparison to simple alternatives**: How does EAAG compare to a much simpler baseline: "run 50 exploration episodes, compute rho(entropy, U), if rho > 0 use high-entropy-triggers, if rho < 0 use low-entropy-triggers"? This captures the direction discovery insight without the LLM reasoning step or LASSO feature selection. If this simple baseline works nearly as well, the EAAG pipeline may be overengineered.

---

## Detailed Technical Assessment

### On Proposition 1 (Necessity of Direction Discovery)

The proposition states that no fixed-direction gate can achieve non-negative VOC in two environments with opposite true directions. This is true by construction and adds no information beyond the empirical observation. The proof amounts to: "if the correct action in E1 is X and in E2 is not-X, no fixed action satisfies both." This is a restatement of the premise, not a theoretical contribution.

A substantively useful proposition would be one of:
- A **convergence guarantee**: With N exploration episodes, EAAG discovers the correct direction with probability >= 1 - delta, where delta = f(N, |rho|).
- A **regret bound**: The cost of exploration is bounded by O(f(N, |rho|)) relative to the oracle.
- A **quantitative damage bound**: Wrong-direction gating degrades SR by at least delta(|rho|), where the relationship is characterized.

The empirical evidence for the damage of wrong direction (BSW ablation) is strong and does not need theoretical packaging to be convincing. The proposition as stated adds a veneer of formalism without adding substance.

### On the Two-Source Model

The model has three free parameters (alpha, beta, p_I) and one observable (sign(rho)). It is therefore underdetermined: any observed rho can be explained by choosing p_I appropriately. The three "testable predictions" (P1-P3) are qualitative (direction of effects, not magnitudes) and are consistent with many alternative models. For example, a simple "trajectory progress" model -- where rho decreases as the agent progresses because late-step entropy reflects accumulating errors -- would predict P1 equally well without requiring the Type I/Type D distinction.

The controlled reversal experiment (InfoPoor/InfoRich) is the strongest evidence for the model, but the InfoPoor result (entropy rho=+0.119, weakly positive) contradicts the Type I prediction of negative rho. The authors acknowledge this but the discrepancy undermines the model's most direct test.

### On the Environment Selection

The 8 environments cover useful territory but have notable gaps for evaluating real agent deployments:

| Category | Environments | Gap |
|----------|-------------|-----|
| Multi-hop QA | HotpotQA | Adequate |
| Fact verification | FEVER | Adequate |
| Code generation | APPS Intro, APPS Interview, CRUXEval | Over-represented (3/8) |
| Web navigation | WebShop | Only 1 environment |
| Text games | TWExpress | Niche domain |
| Manufacturing | Plancraft | Niche domain |
| Tool use | None | Major gap |
| Software engineering | None | Major gap |
| Dialogue agents | None | Notable gap |
| Long-horizon planning | None | Notable gap |

Code generation is over-represented (3 environments), while commercially critical categories (tool use, software engineering, dialogue) are entirely absent. The paper would benefit from replacing one APPS/CRUXEval environment with a tool-use or software engineering task.

---

## Summary

This paper presents a valuable empirical finding (signal-utility direction reversal) with practical implications for adaptive compute deployment. The BSW ablation and stratified analysis provide strong evidence that the phenomenon is real. The paper is well-written and the narrative is compelling.

The main weaknesses are: (1) the optimizer-environment confound means direction reversal might be an optimizer property, not purely an environment property; (2) single-backbone evaluation cannot support environment-level generalization claims; (3) missing RL baselines leave the methodological contribution poorly contextualized; and (4) the theoretical components (Proposition 1, Two-Source Model) are weaker than they appear.

The finding is the paper's core contribution and is strong enough to be worth publishing. But the gap between the paper's claims (environment-level property, theory-driven method) and its evidence (single model, confounded optimizers) needs to be closed or the claims need to be tempered.

**Final Recommendation: Borderline Accept (6/10)** -- The finding is novel and important, but the experimental design has uncontrolled confounds that prevent the paper from fully supporting its theoretical claims. A revision addressing the optimizer confound and adding one alternative backbone would move this to a clear accept.
