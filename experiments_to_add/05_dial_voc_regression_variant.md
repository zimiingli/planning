# Experiment 05: DIAL with $\Delta U$ Regression Head (Optional)

**Priority**: 🟢 **OPTIONAL — high cost, only if deadline allows; lifts method-side novelty**
**Cost**: HIGH (re-train + re-evaluate all 6 envs × 3 backbones)
**Time estimate**: 7–14 days
**Addresses**: Repeated reviewer concern across Round 2 and Round 3: *"DIAL is just ℓ1 logistic regression — where is the algorithmic contribution?"*

---

## Motivation

DIAL currently uses **binary classification** (ℓ1 logistic) to predict $\mathbf{1}[U > 0]$. This is the simplest possible operationalization, and we've reframed this as a deliberate "existence proof" in the writing.

But the reviewer's underlying concern is real: in classical metareasoning (Russell & Wefald 1991), the value of computation $\Delta U(s) = \mathbb{E}[U \mid \text{trigger}] - \mathbb{E}[U \mid \text{no trigger}]$ is a **continuous quantity**, and the optimal gate is a function of this estimate, not its sign.

If we make DIAL estimate $\hat{\Delta U}(s)$ as a continuous quantity, the method moves from:
- "binary classifier of utility sign"

to:
- "value-of-computation estimator with sufficiency-recovery features"

This is a **substantively** stronger framing — and aligns the paper with the metareasoning literature, not just the calibration / adaptive-compute literature.

**Caveat**: This is only worth doing if the regression variant **also performs at least as well as the binary classifier**. If it underperforms, drop it quietly.

---

## Research question

**Q1**: Does estimating $\Delta U$ as a continuous quantity (rather than $\mathbf{1}[U > 0]$) yield equal or better SR/Cost across the 6 envs × 3 backbones grid?

**Q2**: Does the continuous estimate enable better thresholding strategies (e.g., expected-cost-aware threshold, instead of fixed $\tau = 0.5$)?

---

## Hypothesis

**H1 (predicted, optimistic)**: Regression matches binary classification on aligned envs and *outperforms* it on weak-signal envs (Plancraft, TWExpress) where the binary thresholding loses information.

**H1.5 (predicted, realistic)**: Regression matches binary classification within 1–2 pp on most envs; doesn't beat it. Then we adopt regression as the default for **framing** reasons, not performance reasons.

**H0**: Regression underperforms. → Drop and stick with binary version.

---

## Protocol

### Algorithmic change

Replace the ℓ1-logistic gate with an ℓ1-ridge regressor predicting **expected $U$** as a continuous quantity:

```
ŵ, b̂ = argmin_{w,b} Σ (y_i - (w^T φ(s_i) + b))²  +  λ ||w||_1
where y_i = U_i ∈ {-1, 0, +1} (or normalized continuous if available)
```

Then the deployed gate is:
```
g(s) = 𝟙[ŵ^T φ(s) + b̂ > τ]
```

with $\tau$ chosen by **cost-aware optimization**:
```
τ* = argmin_τ E_s[ |U(s) - g_τ(s) · U(s)| · cost(g_τ(s)) ]
```

If logged $U$ values are only binary (no continuous reward signal), use ordinal labels {-1, 0, +1} based on whether the rollout was harmful, neutral, or beneficial.

### Sweep

- 6 envs × 3 backbones × 3 seeds = 54 cells.
- Compare new regression DIAL vs current binary DIAL on SR and Cost.

### Analysis

- Per-cell SR difference: $\Delta\text{SR} = \text{SR}_\text{reg} - \text{SR}_\text{bin}$.
- Pareto front: does regression DIAL dominate binary DIAL on the SR–Cost frontier?
- Sample-efficiency: re-run the experiment 03 sample-complexity sweep with regression. Does regression need fewer or more samples?

---

## Expected outcome

- **Most likely (H1.5)**: Regression matches binary within 1–2 pp on most envs, slightly better on weak-signal Plancraft. We adopt it as DIAL default for the **framing** benefit — the paper's method now estimates VOC, not just classifies.
- **If H1 holds**: 2–5 pp gain on weak-signal envs. Adopt unambiguously, expand the §4 method discussion to a full VOC-estimation framing, and possibly retitle the method.
- **If H0 holds**: Drop the variant. Keep binary version. Note in App C: *"We tested a $\Delta U$ regression variant; performance was equivalent within seed variance, but binary classification was retained for simplicity."*

---

## Integration plan

If H1 or H1.5 holds:

### §4 method changes
- Rewrite §4.3 (`Learn: Sparse Linear Gate`) as `Learn: Sparse Linear VOC Estimator`.
- Equation 3 (logistic) becomes regression.
- Update the DIAL pipeline figure caption.
- Add one sentence: *"The continuous estimate makes DIAL a value-of-computation estimator (Russell \& Wefald 1991) rather than a classifier of utility sign, aligning the method with the classical metareasoning framework."*

### Abstract change
- Replace "a sparse linear gate" with "a sparse linear value-of-computation estimator".

### Conclusion change
- Update the existence-proof claim: *"DIAL recovers per-(env, backbone) VOC through a sparse linear estimator..."*

### New comparison table in App F
- Side-by-side: binary DIAL vs regression DIAL across all 6×3 cells.

If H0 holds:
- Add a one-paragraph subsection to App C noting the negative result and decision.

---

## Compute cost

- **Compute**: 54 cells × full DIAL training pipeline. With existing $(s, U)$ data, only the gate fitting needs to be redone (cheap), but evaluation requires a full re-run of agent episodes per cell.
  - Optimistic: 50–100 GPU-hours (single A100), assuming logged datasets are reused.
  - Pessimistic: 200+ GPU-hours if rollouts are re-sampled.
- **Engineering**: 2–3 days (regression refit + cost-aware threshold tuning + integration).

---

## Owner / status

- [ ] Owner: TBD
- [ ] Status: not started
- [ ] Estimated completion: 7–14 days after start, depending on whether logged data can be reused.

---

## Decision criteria (run-or-skip)

Do this experiment **only if**:
- ≥ 3 weeks until submission deadline, **AND**
- Experiments 01–03 (high-priority) are already complete, **AND**
- Compute budget allows 100+ GPU-hours of additional runs.

Otherwise: skip. The sufficient-statistic + existence-proof framing already deflects most of this critique. The regression variant is a +0.3 to +0.5 score uplift in expectation; not worth blocking on.

---

## Watch-outs

- **Label noise on continuous $U$**: If the logged $U$ is only $\{0, 1\}$ (success / fail), regression has limited information beyond binary classification. Check whether richer reward signals are available before committing.
- **Threshold tuning**: Cost-aware threshold optimization is not free; it requires a held-out cost-vs-SR validation set. Don't accidentally tune on test.
- **Comparability**: Make sure $N_\text{explore}$, feature pool, and CV protocol are identical between binary and regression variants. The contribution is the *output head*, not the rest of the pipeline.
