# Experiment 02: Calibration-Quality Sweep on Misaligned Environments

**Priority**: 🔴 **HIGH — turns the headline claim into a controlled experiment**
**Cost**: LOW–MEDIUM (one new variant, existing infrastructure)
**Time estimate**: 3–5 days
**Addresses**: Round-3 reviewer observation — *"better calibration worsens performance"* is the paper's most quotable claim, but we currently only **infer** it from the wrong-direction ablation. A reviewer can argue this is post-hoc.

---

## Motivation

The paper now uses *"better-calibrated uncertainty signals can make adaptive test-time compute strictly worse than no gating at all"* as the abstract hook. This is genuinely reviewer-attractive — but the supporting evidence is currently:

- Table 4 (wrong-direction ablation): reversing the gate's learned weights drops SR by 23–37 pp.
- This **implies** "more accurate calibration → more harm in misaligned envs" but doesn't directly **demonstrate** it as a controlled monotone relationship.

A reviewer may say:

> "Reversing weights is a binary intervention. Show me that as calibration *quality* increases monotonically (e.g., more training data, lower temperature), SR on misaligned envs *monotonically* drops. Otherwise the headline claim is overstated."

We need to make this an experimentally controlled claim, not an inferred one.

---

## Research question

**Q**: On environments where the assumed direction is wrong, does monotonically improving the gate's calibration quality (via more training data, lower regularization, or temperature scaling) cause monotonic SR degradation?

---

## Hypothesis

**H1 (predicted)**: On Type~I-dominated envs (FEVER, HotpotQA on Qwen3) gated by a fixed-direction baseline (e.g., SEAG with $d{=}{+}1$), increasing calibration quality strictly decreases SR.

**H1 contrast**: On Type~D-dominated envs (APPS, WebShop) the same calibration improvement strictly *increases* SR.

**H0**: SR is non-monotone or insensitive to calibration quality. → Soften abstract hook.

---

## Protocol

### Calibration-quality knobs

We need to vary calibration quality in a *controllable* way. Three options, in increasing order of complexity:

**Option A (recommended, simplest)**: Vary the amount of training data used to fit a gate's calibration parameters.
- Take a fixed-direction baseline (SEAG, threshold-based). Its "calibration" is the threshold $\theta$.
- Vary the size of held-out data used to tune $\theta$: $N_\text{cal} \in \{20, 50, 100, 200, 500\}$ episodes.
- Larger $N_\text{cal}$ → more accurate $\theta$ → better calibration.

**Option B**: Vary the temperature applied to the gate's score before thresholding.
- Higher temperature → flatter distribution → less precise gate.
- Lower temperature → sharper distribution → more precise gate.
- Range: temperature $\in \{0.1, 0.5, 1.0, 2.0, 5.0\}$.

**Option C** (most direct, more work): Replace the gate's classifier with calibrators of varying capacity:
- random gate (no calibration)
- 1-feature linear (univariate logistic on entropy alone)
- multi-feature linear (full universal feature pool)
- nonlinear (RF / MLP on full pool)
- "oracle" gate (trained on test labels — upper bound on calibration)

Each rung is monotonically better-calibrated.

**Recommendation**: Start with Option A (cheapest), add Option C only if Option A is non-monotone.

### Environments

Pick 4 envs covering the spectrum:
- **2 misaligned** (paper's main claim): FEVER (Type~I, Qwen3), HotpotQA (Type~I, Qwen3) — gate set to fire on **high entropy** (the "wrong" direction).
- **2 aligned** (control / contrast): APPS (Type~D, Qwen3), WebShop (Type~D, Qwen3) — gate set to fire on **high entropy** (the "right" direction).

### Backbones

Qwen3-4B for the main sweep. If results are clean, repeat on Phi-3.5 to show the same pattern at a different scale (1 day extra).

### Metric

- SR vs $N_\text{cal}$ (or temperature, depending on Option).
- Cost ($\times$base) for completeness.
- Spearman test of monotonicity: $\rho_{\text{Spearman}}(N_\text{cal}, \text{SR})$ should be **negative** on misaligned envs and **positive** on aligned envs.

---

## Expected outcome

- **Most likely**: Clear monotone effect. On FEVER, going from $N_\text{cal}{=}20$ to $N_\text{cal}{=}500$ drops SR by 5–15 pp; on APPS, the same change *increases* SR.
- **If H1 holds**: Add a 2-panel figure to §5.2 (one panel per env type), captioned: *"As calibration quality improves, SR moves in opposite directions on aligned vs misaligned environments — the headline cost of σ-insufficiency."*
- **If H0 holds**: Soften abstract hook to *"better calibration can fail to help"* instead of *"better calibration worsens"*. Honest, but loses the punch.

---

## Integration plan

### New paragraph in §5.2
After the wrong-direction ablation (Table 4), add a new ablation **5.2.1: Calibration-quality sweep**:

```
\textbf{Better calibration directly worsens SR on misaligned environments.}
[1-paragraph description of protocol + result]
[Table or figure: SR vs N_cal for 4 envs]
[Closing: "This is the controlled-experiment statement of the headline
claim: improving calibration quality causes monotone SR degradation
when σ has the wrong sign."]
```

### Possible new figure
Two-panel SR-vs-$N_\text{cal}$ plot (left: misaligned, right: aligned). Place in §5.2 if space allows; otherwise in appendix with body reference.

### Abstract cross-reference
None needed — the abstract hook is already in place. This experiment makes it bulletproof, not load-bearing for the abstract itself.

---

## Compute cost

- **Compute**: 5 (env) × 5 ($N_\text{cal}$) × ~30 episodes (eval) = ~750 episode evals on Qwen3-4B. Estimate: 6–12 GPU-hours on a single A100.
- **Engineering**: 4–8 hours (sweep harness + plotting).

---

## Owner / status

- [ ] Owner: TBD
- [ ] Status: not started
- [ ] Estimated completion: 3–5 days after start

---

## Watch-outs

- Make sure the misaligned-env baseline genuinely uses the wrong direction. SEAG / CaTS / CoRefine all assume positive $\rho$, so they are misaligned by default on Type~I envs. Don't accidentally use a method that flips its threshold sign internally.
- Cost should be reported alongside SR — if better calibration also reduces cost on misaligned envs (because the gate fires less), the story changes (still bad SR, but maybe acceptable cost). Report both.
