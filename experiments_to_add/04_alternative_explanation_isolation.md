# Experiment 04: Alternative-Explanation Isolation

**Priority**: 🟡 **MEDIUM-HIGH — addresses the most persistent reviewer concern across all 3 review rounds**
**Cost**: MEDIUM
**Time estimate**: 5–10 days
**Addresses**: Rounds 1, 2, **and** 3 reviewer concern: *"the two-source model is plausible but you haven't ruled out alternative explanations for the reversal — rollout noise, reward bias, search depth, calibration error, etc."*

---

## Motivation

The two-source model (§3.2) is currently supported by:
- The mixture equation $\rho \approx \beta - (\alpha+\beta)p_I$ matches observed sign patterns.
- P1, P2, P3 predictions verified on held-out data.

But the verification is **predictive**, not **causal**. The two-source decomposition is *consistent* with the data; it has not been shown to be the *unique* explanation. Plausible alternatives:

| Alternative | Mechanism | How it would explain reversal |
|---|---|---|
| **A1: Rollout noise** | $T$'s outputs are noisy; high-entropy states amplify noise. | Reversal reflects rollout estimator variance, not state-type structure. |
| **A2: Reward bias** | $R$ is itself noisy / partially observable; some envs have positively biased rewards, others negatively. | Reversal reflects reward-distribution asymmetry. |
| **A3: Search-depth effect** | Optimizers with different effective depth interact with state structure differently. | Reversal is a function of $T$'s internal hyperparameters, not state types. |
| **A4: Calibration error** | $\sigma$ is miscalibrated by the LLM in env-specific ways. | Reversal is an artifact of upstream calibration, not VOC structure. |

**This is the single most-cited weakness in 3 rounds of internal review. Address it.**

---

## Research question

**Q**: For each of A1–A4, can we manipulate that variable in isolation and confirm that the two-source mixture prediction (not the alternative) explains observed reversal?

---

## Sub-experiments

### 4.1 Rollout noise (A1)

**Manipulation**: Vary the rollout estimator's variance by changing $K$ (number of rollouts averaged).
- $K \in \{1, 3, 5, 10\}$.
- Rerun DIAL gate fitting and evaluation on a subset of envs (FEVER, HotpotQA, APPS).

**Prediction (two-source)**: Sign of $\rho(\sigma, U)$ is **invariant** to $K$ (only the magnitude of noise changes, not the structural sign).

**Falsification**: If sign flips with $K$, then noise — not state structure — explains reversal.

### 4.2 Reward bias (A2)

**Manipulation**: Apply additive shift to reward $R \to R + c$ and multiplicative scaling $R \to \alpha R$, both with $c \in \{-0.5, 0, +0.5\}$ and $\alpha \in \{0.5, 1, 2\}$.
- These are post-hoc transformations on the logged data, no new rollouts needed.

**Prediction (two-source)**: Sign of $\rho(\sigma, U)$ is invariant to monotone reward transformations (Spearman is rank-based; affine reward transforms preserve rank).

**Falsification**: If reversal disappears under reward transformations, the issue was reward parameterization, not state structure.

**Note**: This is partly automatic given Spearman's rank-invariance. The real question is whether the *sign* of $U$ (which determines DIAL's training labels via $U > 0$) is robust under reward shifts. If shifting $c$ flips the median of $U$ across zero on some envs, the apparent reversal could be a labeling artifact.

### 4.3 Search-depth effect (A3)

**Manipulation**: Vary $T$'s internal search depth on environments where $T$ is rollout-based.
- For rollout-based optimizers: vary trajectory horizon $H \in \{1, 3, 5, 10\}$ or branching $B$.
- Rerun on 2 envs.

**Prediction (two-source)**: Sign of $\rho(\sigma, U)$ is invariant to $T$'s depth (the structural state-type distinction is independent of how long $T$ explores).

**Falsification**: If sign depends on $H$, then optimizer hyperparameters are confounded with the apparent reversal.

### 4.4 Calibration error (A4)

**Manipulation**: Apply temperature scaling to entropy: $\sigma_T(s) = \sigma(s) / T$ for $T \in \{0.5, 1, 2, 5\}$.
- This changes the *sharpness* of the entropy distribution but not its rank.

**Prediction (two-source)**: Sign of Spearman $\rho$ unchanged under temperature scaling (rank-invariant).
**Stronger prediction**: Sign of Pearson $\rho$ also stable for moderate $T$.

**Falsification**: If even Spearman flips with $T$, something is wrong with the entropy estimator or the data pipeline (this would actually be a useful diagnostic finding).

---

## Integration plan

### New appendix subsection
Add `\subsection{Ruling Out Alternative Explanations}` to App G (Robustness), as the closing subsection.

Content:
- Brief description of A1–A4.
- One small table or figure per sub-experiment, summarizing whether reversal sign is preserved under the manipulation.
- Closing paragraph: *"Across all four manipulations, reversal sign is preserved. This rules out rollout noise, reward parameterization, search depth, and calibration error as primary causes, supporting the two-source mixture interpretation as the operative mechanism."*

### Body change
- §3.2: After the *"minimal falsifiable model"* sentence, add: *"Robustness checks in App G.Z further rule out rollout noise, reward bias, search depth, and calibration scaling as alternative explanations."*

### If results contradict
- If any sub-experiment falsifies the two-source prediction:
  - Do not silently drop. Report it honestly in App G.
  - Add a paragraph to §6 (Limitations) acknowledging the alternative mechanism.
  - Re-frame §3.2 as a *partial* explanation.

---

## Compute cost

- **4.1 (rollout noise)**: 4 ($K$) × 3 (env) × 1 (backbone) × ~30 episodes × $K$ rollouts each. Total ~360 episodes worth of compute. ~10–20 GPU-hours.
- **4.2 (reward bias)**: ~0 GPU-hours (post-hoc analysis).
- **4.3 (search depth)**: 4 ($H$) × 2 (env) × ~30 episodes. ~10 GPU-hours.
- **4.4 (calibration)**: ~0 GPU-hours (re-analysis).

**Total**: ~20–40 GPU-hours single A100.

**Engineering**: 1–2 days for the harness across 4 sub-experiments.

---

## Owner / status

- [ ] Owner: TBD
- [ ] Status: not started
- [ ] Estimated completion: 5–10 days after start

---

## Watch-outs

- 4.2 (reward bias) is the trickiest. The two-source model claims structural invariance under monotone transforms, but the gate's *training labels* ($U > 0$ vs $U \leq 0$) are sensitive to where the threshold falls relative to the reward distribution. Be careful to distinguish "reversal of $\rho(\sigma, U)$" (rank-based) from "reversal of gate decisions" (threshold-based).
- 4.4 (calibration) may inadvertently confirm a different concern: if temperature scaling does change the sign of Pearson $\rho$ even though Spearman is preserved, this is a *finding in itself* — it would mean fixed-direction methods using Pearson-style calibration are even more brittle than we currently claim.
