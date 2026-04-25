# Experiment 03: Sample-Complexity Sweep ($N_\text{explore}$)

**Priority**: 🟡 **MEDIUM-HIGH — required to defend deployment story**
**Cost**: LOW
**Time estimate**: 2–3 days
**Addresses**: Reviewer concern (raised in Round 3 implicitly, also a generic deployment-feasibility concern). Diagnostic-for-practitioners section says "a few hundred $(s, U)$ pairs"; method section says $N_\text{explore}{=}50$; nothing in the paper currently shows what happens at smaller or larger $N_\text{explore}$.

---

## Motivation

The paper makes two practical claims about deployment cost:

1. **§4.3 cost accounting**: "$N_\text{explore}{=}50$ episodes per (env, backbone) pair, amortized over all subsequent deployment".
2. **§3.1 diagnostic for practitioners**: "collecting a few hundred signal-agnostic $(s, U)$ pairs is sufficient to decide".

These are claims about the deployment economics of DIAL. A reviewer will ask:

> "Did you actually measure how SR scales with $N_\text{explore}$? Why 50? Is 30 enough? Is 200 needed for harder environments? Without this curve, the cost story is just an assertion."

**This is a cheap experiment that closes a real gap.**

---

## Research question

**Q**: How does DIAL's deployment SR depend on the size of the exploration dataset $N_\text{explore}$?

---

## Hypothesis

**H1 (predicted)**: SR plateaus by $N_\text{explore} \in [30, 50]$ on most environments, with FEVER (Type~I extreme) requiring more (~100–200).

**H0**: SR keeps climbing past $N_\text{explore}{=}50$ on multiple environments. → Revise the "minimal" framing or report a per-env recommendation.

---

## Protocol

### Sweep grid
- $N_\text{explore} \in \{10, 25, 50, 100, 200\}$
- All 6 environments
- 3 backbones (Qwen3-4B is mandatory; others if time)
- 3 random seeds per cell

### Procedure
1. For each $(N_\text{explore}, \text{env}, \text{backbone}, \text{seed})$:
   - Run signal-agnostic exploration with $N_\text{explore}$ episodes.
   - Fit DIAL gate on the resulting $(s, U)$ dataset.
   - Evaluate gate on the test split.
2. Record SR, Cost ($\times$base), and the number of non-zero weights selected by ℓ1.
3. Plot SR vs $N_\text{explore}$ per environment.

### Analysis
- Identify the per-env $N_\text{explore}^*$ at which SR is within 1 pp of the asymptotic value.
- Check: does $N_\text{explore}^*$ correlate with $p_I$? (Two-source model would predict higher $N_\text{explore}^*$ for high-$p_I$ envs because the rare Type~D states are needed to fit the direction.)
- Variance check: at $N_\text{explore}{=}50$, what is the std of SR across the 3 seeds? If high (>2 pp), report it honestly.

---

## Expected outcome

- **Most likely**: SR climbs sharply from $N_\text{explore}{=}10$ to ~25–50, then plateaus on 5/6 envs. FEVER plateaus later or never (consistent with the §6 limitation).
- **If H1 holds**: Add a per-env recommendation table to App C (DIAL Implementation Details). Cite from §4.3 cost accounting.
- **If H0 holds**: Either (a) increase the default $N_\text{explore}$ recommendation in the paper, or (b) report per-env recommendations and acknowledge the simple "50 episodes" claim is over-simplified.

---

## Integration plan

### New appendix subsection
Add `\subsection{Sample Complexity}` to App C (`\section{DIAL Implementation Details}`) right after the hyperparameters section.

Content:
- Plot or table of SR vs $N_\text{explore}$ for all 6 envs (Qwen3, with Phi-3.5 / Llama-3.1 in supplementary if available).
- Per-env $N_\text{explore}^*$ recommendation.
- One-paragraph commentary on FEVER (and any other Type~I extreme) requiring more samples.

### Body changes
- **§4.3 cost accounting**: change "$N_\text{explore}{=}50$" to "$N_\text{explore}{=}50$ (sufficient for 5 of 6 environments; FEVER benefits from $N_\text{explore}{=}X$, see App C.Y)".
- **§6 Limitations**: add half-sentence: "FEVER's high-$p_I$ structure also makes it the most sample-hungry environment for DIAL (App C.Y)".
- **§3.1 diagnostic for practitioners**: optionally update "few hundred" to a more specific number (e.g., "30–200 depending on $p_I$").

---

## Compute cost

- **Compute**: 5 ($N_\text{explore}$) × 6 (env) × 3 (seed) × 1 (backbone, Qwen3 only) = 90 DIAL training runs + evaluations. Each is fast (< 30 min including exploration). Estimate: 30–50 GPU-hours single A100.
- If extending to all 3 backbones: 3× more, ~100–150 GPU-hours.
- **Engineering**: 4 hours (sweep harness + plotting).

---

## Owner / status

- [ ] Owner: TBD
- [ ] Status: not started
- [ ] Estimated completion: 2–3 days after start

---

## Watch-outs

- Different envs have different episode lengths, so $N_\text{explore}{=}50$ episodes ≠ 50 (s, U) data points. Report **both** $N_\text{explore}$ (episodes) **and** $|\mathcal{D}|$ (data points) to make the comparison fair.
- Make sure the test split is held out **before** the sweep, not re-drawn per $N_\text{explore}$.
- The ℓ1 regularization strength $C$ should be re-tuned per $N_\text{explore}$ via CV; don't hold it fixed across sweep points (would bias against small-$N$).
