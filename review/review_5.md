# NeurIPS 2026 Peer Review

**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Reviewer Persona**: Applied ML researcher working on efficient inference and test-time compute
**Reviewer Confidence**: 4/5 (I work directly on adaptive inference methods and have deployed selective compute allocation in production agent systems)

---

## Overall Assessment

**Recommendation: Accept (7/10)**

This paper identifies a practically important failure mode in adaptive test-time compute: the direction of signal-utility correlation reverses across environments, meaning that methods calibrated on one environment can actively harm performance in another. The finding is clean, empirically grounded, and immediately actionable. The proposed fix (EAAG) is simple enough that I could implement it in an afternoon, which I consider a strength rather than a weakness. The paper follows the "Are Emergent Abilities a Mirage?" archetype -- a sharp empirical finding that reframes how the community should think about a problem -- and largely succeeds in this ambition.

My positive assessment is driven by three factors: (1) the finding genuinely changes how I would design adaptive compute for a new deployment, (2) the paper is honest about its limitations (especially the FEVER failure), and (3) the prescriptive framework ("characterize information structure first") fills a gap that the current literature does not address. The weaknesses -- single backbone, simplified theory, thin method -- are real but do not undermine the core value proposition.

---

## Scores

| Criterion | Score (1-10) | Notes |
|-----------|:---:|-------|
| **Novelty** | 7 | Direction reversal is a genuine discovery. Not technically novel as a method, but the reframing is valuable. |
| **Significance** | 8 | High practical impact. Every practitioner deploying adaptive compute across environments should know this. |
| **Technical Soundness** | 7 | Finding is robust (stratified analysis, interventional BSW ablation, cross-env consistency). Theory is a useful simplification. |
| **Clarity** | 8 | Clean narrative arc, well-chosen concrete numbers, good figure design. |
| **Experimental Design** | 7 | 8 environments across 6 task categories is strong breadth. Single backbone is a limitation but the environment diversity compensates. |
| **Reproducibility** | 7 | Setup is detailed. Hyperparameters are specified. Code availability unclear. |

---

## Key Strengths

### S1: The direction reversal finding is genuinely useful for practitioners

I work on deploying test-time compute optimizers across diverse agent tasks. The single most common failure mode I encounter is exactly what this paper describes: a gating strategy that works beautifully on a development environment (say, QA with retrieval) fails or actively hurts on a production environment (say, code generation). This paper gives me a name for the problem (direction reversal), an explanation for why it happens (Two-Source Model), and a diagnostic I can run before deployment (measure signal-utility correlations in a small exploration phase).

The concrete numbers make this actionable. When the paper shows that CATTS achieves 34.2% on FEVER -- below the 37.0% no-trigger baseline -- that is not an academic curiosity. That is the kind of silent regression that ships to production and degrades user experience. The fact that this happens to a well-designed method (CATTS uses vote entropy, a reasonable signal) because of a structural mismatch (FEVER is Type I dominated) makes the warning credible and urgent.

### S2: The paper is well-positioned as a "finding paper" at NeurIPS

The paper explicitly follows the archetype of "Are Emergent Abilities a Mirage?" (Schaeffer et al., NeurIPS 2023 Outstanding) and "Not All Tokens Are What You Need" (Lin et al., NeurIPS 2024 Best Paper Runner-Up). The contribution hierarchy is clear: Finding > Theory > Method. This is the right positioning.

The key structural parallel: Schaeffer et al. showed that emergent abilities disappear when you change the metric (simple fix, big insight). This paper shows that fixed-direction gating fails when you change the environment (simple fix: learn the direction, big insight: direction is determined by information structure). In both cases, the finding reframes how the community should think about a problem, and the method is deliberately simple because the insight, not the machinery, is the bottleneck.

The paper's design notes show awareness of this positioning (citing Michael Black's "Novelty in Science" on simplicity), and the writing delivers on it. The narrative arc -- assumption, falsification, explanation, fix, validation -- is tight and persuasive.

### S3: EAAG's simplicity is a genuine adoption advantage

I have watched multiple RL-based adaptive compute methods (AdaptThink, Thinkless) go through the publication cycle. They work well on their training environments, but the per-environment training cost (thousands of episodes of RL fine-tuning) makes them impractical for the "deploy an agent on a new task next week" use case that is increasingly common.

EAAG's pipeline -- 50 episodes of random exploration, one LLM reasoning call, one LASSO fit in <1 second -- is practical in a way that matters. The zero per-step deployment cost (a single inner product) means it does not add latency. The LASSO coefficients are interpretable: I can look at the signs and understand what the gate learned (negative weight on step_count in HotpotQA means "trigger early, not late"). This interpretability is not just academic -- it builds trust with engineering teams who need to understand why the system makes the decisions it does.

The ablation data supports this: the jump from single-signal entropy (AUC approximately 0.50, chance level) to multi-signal logistic regression (AUC approximately 0.83) captures the vast majority of available information. Going further to hidden-state probes (AUC approximately 0.90) adds marginal value at substantial complexity cost. EAAG sits at the practical sweet spot.

### S4: The prescriptive framework is the most underrated contribution

The paper's Discussion section offers a prescriptive framework: "before designing a gating mechanism for a new environment, first characterize its information structure (information sufficiency, decision reversibility, feedback delay) to predict signal semantics and direction." This is exactly the kind of practical guidance that is missing from the adaptive compute literature.

Currently, practitioners pick a signal (usually entropy or confidence), pick a direction (usually "high uncertainty means trigger"), and hope. This paper says: stop. First ask whether the environment is information-poverty-dominated or decision-difficulty-dominated. The answer determines whether your signal should trigger on high or low values. This is a simple diagnostic that could save significant debugging time.

The environment-type mapping table (Table 2) is actionable: if my new environment looks like search-based QA (external retrieval required, evidence may be missing), I should expect negative entropy-utility direction. If it looks like code generation (multiple valid strategies, information is self-contained), I should expect positive direction. This is useful even without running EAAG.

---

## Concerns

### C1 (Medium): Single backbone limits confidence in generality claims

The paper argues that direction reversal is a property of the environment's information structure, not the model. This is a reasonable theoretical argument, but it is tested with only Qwen3-4B. A larger model with better calibration might show different (perhaps weaker) reversal patterns. The independent evidence from Tao et al. (2025) and Heo et al. (ICLR 2025) helps, but these papers measure calibration quality, not signal-utility direction specifically.

**Why I do not make this a major issue**: The core finding (direction reversal exists) only needs to hold for at least one practical backbone to be valuable. Even if a 70B model showed weaker reversal, the 4B-class models that are increasingly common in agent deployment (due to latency and cost constraints) would still need direction-aware gating. The practical relevance is clear.

**Recommended action**: Add 2-3 experiments with a second backbone on the environments showing the strongest reversal (FEVER, APPS Interview, HotpotQA). Even showing that the sign of rho is preserved (regardless of magnitude) would substantially strengthen the paper.

### C2 (Medium-Low): The Two-Source Model is a useful simplification, not a theory

The Two-Source Model decomposes uncertainty into "information poverty" (Type I) and "decision difficulty" (Type D). This is an appealing intuition, but calling it a "model" overstates its formality. The key parameter p_I (fraction of Type I states) is unobservable, and the mapping from environments to types is determined post-hoc by observing the rho values.

However, unlike a purely post-hoc narrative, the model generates three testable predictions (P1: temporal dynamics, P2: cross-environment consistency, P3: signal identity alignment), and all three are confirmed in Section 5.4. The temporal dynamics prediction (rho decreases from early to late steps as information accumulates and residual Type I dominates) is particularly convincing because it is a within-environment prediction that could easily have failed.

**Why I do not downgrade heavily**: The model's practical value is prescriptive, not predictive. It tells practitioners what to look for (is this environment information-poverty-dominated or decision-difficulty-dominated?) and what to expect (which direction should the gate learn?). A more complex theory would not change this practical guidance. The connection to Simpson's paradox and the epistemic/aleatoric distinction in uncertainty quantification is intellectually satisfying even if the formalism is lightweight.

**Recommended action**: Strengthen the controlled reversal experiment (InfoPoor/InfoRich). The current result (InfoPoor shows weakly positive entropy rho = +0.119, contradicting the Type I prediction of negative rho) needs a clearer explanation. If the Two-Source Model does not correctly predict the direction in a controlled setting, that is a meaningful limitation of the theory.

### C3 (Minor): The 34W/2L metric is coarse-grained

The headline result (34 wins vs. 2 losses across 6 baselines and 8 environments) counts any SR improvement as a "win" regardless of magnitude. The appendix shows that only 18 of 30 comparisons reach statistical significance (95% CI excludes zero). This means approximately 40% of the "wins" could be noise.

A more informative summary would be: "EAAG achieves statistically significant improvements in 18/30 head-to-head comparisons, with no statistically significant losses." This is still a strong result, and more defensible.

### C4 (Minor): The "emergent adaptive behavior" framing is overclaimed

The paper describes EAAG's varying trigger rates (73% in TWExpress, 28% in WebShop) as "emergent." This is simply logistic regression producing different outputs on different input distributions. The term "emergent" carries specific connotations in the LLM literature (per Schaeffer et al., the very paper this work cites as inspiration) and should be used more carefully. "Environment-adaptive gating patterns" would be more accurate.

### C5 (Minor): FEVER result deserves more structural analysis

EAAG achieves 49.8% on FEVER versus SCG's 98.0% and always-trigger's 99.8%. The paper explains this as exploration bias (random gating misses step-0 rollouts 50% of the time), which is plausible. But this is a large gap -- nearly 50 percentage points below the oracle. The paper could strengthen this section by showing that a curriculum-based exploration (always-trigger for first 10 episodes, then random) closes the gap. This would both validate the exploration-bias explanation and provide a practical fix. If the experiment is infeasible for this submission, framing this as a concrete limitation and future direction (which the paper already partially does) is acceptable.

---

## Questions for Authors

1. **Cross-backbone prediction**: If I deploy EAAG with Llama 3 8B on HotpotQA, do you predict the same sign of rho for step_count (negative) and similar LASSO feature selection? What is the theoretical basis for this prediction?

2. **Exploration budget sensitivity**: The 50-episode exploration budget is presented as a hyperparameter. Is there a principled way to determine when sufficient exploration data has been collected (e.g., monitoring convergence of LASSO coefficient signs)? This would make EAAG more practical for deployment.

3. **Online adaptation**: The paper mentions optional online adaptation (epsilon-greedy exploration, retrain every 30 episodes). Do you have evidence that this helps in practice? Specifically, does the learned direction ever change during deployment, or is it stable after the initial exploration phase?

4. **Negative VOC scope**: The appendix discusses environments where the evaluator-executor identity means VOC can be negative (Plancraft: always-trigger 22.8% < base 29.8%). This is an interesting theoretical point. How common do you estimate this is in real-world agent deployments? Does EAAG reliably detect and avoid triggering in such environments?

---

## Detailed Assessment Against Review Criteria

### Is the direction reversal finding genuinely useful for practitioners?

**Yes, strongly.** The finding passes the "Monday morning" test: if I read this paper on Friday, would I change how I work on Monday? The answer is yes. Specifically:

- I would add a signal-utility correlation diagnostic to any new environment before deploying a gating strategy.
- I would stop assuming that "high entropy means trigger" and instead learn the direction from data.
- I would use EAAG's exploration-reason-learn pipeline (or something similar) as the default approach for new deployments.
- I would use the Two-Source Model's taxonomy (Type I vs Type D) as a mental model for anticipating failure modes.

The fact that CATTS actively hurts performance on FEVER (34.2% < baseline 37.0%) is the kind of result that changes practice. Practitioners deploying adaptive compute across diverse environments will encounter this failure mode. This paper tells them why it happens and how to prevent it.

### Is the paper well-positioned relative to the NeurIPS "finding paper" precedent?

**Yes, with one caveat.** The paper successfully follows the Schaeffer et al. archetype: sharp finding, clean falsification, elegant explanation, simple fix. The writing quality is high, the narrative arc is tight, and the design notes show deliberate study of best paper patterns.

The caveat: Schaeffer et al.'s finding (emergent abilities are a mirage) was stronger because it required zero new experiments -- only re-analysis of existing data with different metrics. This paper requires new experiments (8 environments, exploration data collection, EAAG training). The finding is therefore more "here is a phenomenon we discovered" rather than "here is a reinterpretation of existing data." Both are valid, but the latter is more surprising. The paper is not quite at the "Are Emergent Abilities" level of conceptual impact, but it is solidly within the NeurIPS "finding paper" quality band.

### Does EAAG's simplicity help adoption?

**Yes, decisively.** The deployment pipeline (50 episodes random exploration, LLM reasoning call, LASSO fit in <1 second, logistic gate with zero per-step cost) has a total engineering budget of roughly one day. Compare this to:

- RL-based methods (AdaptThink, Thinkless): require per-environment RL training with thousands of episodes, reward shaping, and hyperparameter tuning. Days to weeks of engineering.
- Phase-1-calibration methods (CaTS, SEAG, CoRefine, SCG): require 200 always-trigger episodes (4x EAAG's exploration budget at higher per-episode cost) plus separate calibration fitting.
- CATTS: no training required, but K=5 forward passes per step adds latency that is unacceptable in many production settings.

EAAG wins on setup cost, deployment cost, and interpretability simultaneously. The LASSO coefficients provide a human-readable summary of what the gate learned. In my experience, this interpretability is essential for production deployment: when performance drops, the team needs to understand why the gate made its decisions.

The ablation data further supports the adoption case: removing the LLM reasoning step changes SR by <1pp in 4/6 environments, meaning a "EAAG-lite" version (just LASSO on universal features, no LLM call needed) captures most of the value. This is even simpler to deploy.

### Is the prescriptive framework actionable?

**Partially.** The framework ("characterize information structure first") is directionally useful but needs more operationalization. Currently, the guidance is:

1. Ask: is the environment dominated by information poverty (agent lacks data, rollouts cannot help) or decision difficulty (agent faces multiple viable paths, rollouts explore them)?
2. If Type I: expect negative entropy-utility direction; step_count is likely the strongest signal.
3. If Type D: expect positive entropy-utility direction; decision-space features may dominate.
4. If unsure: run EAAG's 50-episode exploration phase and let the data tell you.

Steps 1-3 are useful as mental models but hard to formalize. The paper acknowledges that p_I is unobservable. Step 4 is the practical fallback and is well-specified. The framework would be stronger with a concrete decision tree or checklist that maps environment properties (e.g., "does the task require external information retrieval?" / "are there multiple valid solution strategies?") to predicted signal semantics.

### What is the paper's lasting impact on the adaptive compute community?

**Moderate-to-high.** I see two lasting contributions:

1. **The direction reversal finding as a cautionary result.** Future adaptive compute papers will need to evaluate across environments with different information structures and demonstrate that their method does not assume a fixed signal direction. This raises the evaluation bar for the field, which is valuable.

2. **The "characterize information structure first" principle.** Even if EAAG is superseded by better methods, the principle that signal semantics depend on environment information structure will remain. This is the paper's most durable insight. It connects to the broader epistemic/aleatoric uncertainty decomposition literature and suggests that adaptive compute is fundamentally a meta-reasoning problem, not just a calibration problem.

The method (EAAG) itself may not persist in its current form -- logistic regression will likely be replaced by more sophisticated direction-learning approaches -- but the direction-aware design principle it embodies will. This is the hallmark of a good "finding paper": the finding outlasts the method.

---

## Minor Notes

- Table 1 should footnote CATTS's per-step overhead (K=5 forward passes), which is not reflected in the cost column.
- The controlled reversal experiment (InfoPoor/InfoRich) partially contradicts the Two-Source Model (InfoPoor entropy rho = +0.119, expected negative). The caveat ("small sample and mixed early-step Type D component") is buried in the text and should be more prominently acknowledged.
- Section 5.7 (observable proxy for p_I, r = +0.75 on 6 points, p = 0.086) is too weak for the main text. Move to appendix or remove. It currently weakens the theory rather than strengthening it.
- The paper is estimated at approximately 10.25 pages, exceeding the 9-page NeurIPS limit. Trimming approximately 1.25 pages is needed. Recommended cuts: condense per-environment analysis in Section 5.2 (move HotpotQA and APPS Intro details to appendix), tighten Related Work, and move the multi-agent future direction to appendix.

---

## Summary

This paper makes a clear, useful, and well-evidenced contribution to the adaptive test-time compute literature. The direction reversal finding is practically important, the Two-Source Model provides useful (if simplified) explanatory power, and EAAG's simplicity is a feature that enables real-world adoption. The paper is well-written, follows the NeurIPS "finding paper" archetype effectively, and is honest about its limitations. The single-backbone evaluation and simplified theory are real weaknesses but do not undermine the core contribution. I recommend acceptance.
