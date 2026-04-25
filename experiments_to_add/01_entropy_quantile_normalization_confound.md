# Experiment 01: Entropy Quantile-Normalization Confound Control

**Priority**: 🔴 **HIGHEST — closes the single biggest attack vector**
**Cost**: LOW (no new training, only re-analysis of existing $(s, U)$ data)
**Time estimate**: 1–2 days
**Addresses**: Round-1 reviewer concern (raised in 3 internal review rounds, unanswered)

---

## Motivation

The paper's most striking finding is that signal–utility direction reverses **across model backbones with the task held fixed** — most extreme on FEVER ($\rho{=}{-}0.156$ on Phi-3.5 vs $\rho{=}{+}0.428$ on Llama-3.1).

A reviewer will ask:

> "Different backbones produce entropy values on different scales (different tokenizers, different temperature implicit in fine-tuning). Maybe the 'reversal' is just an artifact of comparing entropy values across incomparable scales — the *rank* of high-entropy states might be consistent across backbones, and the sign flip an artifact of mixing backbones into the same correlation."

If true, this would weaken the central claim significantly. **We have not ruled this out.**

---

## Research question

**Q**: Does the (environment, backbone) direction reversal in Table 1 of the paper persist after entropy values are normalized to a backbone-agnostic scale?

---

## Hypothesis

**H1 (predicted)**: Reversal persists. Quantile-normalized entropy still shows opposite signs across backbones on FEVER, HotpotQA, and APPS. → Paper claim is bulletproofed.

**H0 (null)**: Reversal disappears or significantly attenuates. Most or all sign flips collapse. → Paper claim is at risk and framing must be revised.

---

## Protocol

### Data
- Reuse the same $(s, U)$ exploration datasets already collected for the main results (6 envs × 3 backbones × ~50 episodes each).
- No new rollouts needed.

### Procedure
1. **Per-(env, backbone) quantile rank**: For each (environment, backbone) pair, replace each state's raw entropy $\sigma(s)$ with its empirical quantile rank $Q(s) \in [0, 1]$ within the exploration dataset for that pair.
   ```
   Q(s_i) = rank(σ(s_i)) / N
   ```
2. **Per-backbone quantile rank** (alternative comparison): For each backbone, pool all states across environments, compute quantile rank within that pool. This gives a backbone-internal but cross-environment rank.
3. **Per-environment quantile rank**: For each environment, pool all backbones, compute quantile rank. This gives an environment-internal cross-backbone rank — the most aggressive normalization.
4. For each normalization scheme, recompute Spearman $\rho(Q, U)$ and compare against the raw-entropy table.

### Analysis
- Build a 3-way comparison table: raw-entropy $\rho$ vs three quantile-normalized $\rho$ values, per (env, backbone) pair.
- Mark cells where sign **changes** under normalization.
- Report counts: how many of the original 18 (env, backbone) pairs show sign-stable correlation?
- Specific spotlight: do the FEVER and APPS sign flips persist?

### Statistical test
- Bootstrap confidence interval (1000 resamples) on each normalized $\rho$.
- A reversal is "robust" if both raw and normalized $\rho$ have CIs that exclude zero on the same side.

---

## Expected outcome

- **Most likely**: Reversal is **partially robust** — some (env, backbone) pairs collapse to non-significant under aggressive normalization, but the FEVER cross-backbone reversal persists in some form. This is fine and we report it honestly.
- **If H1 fully holds**: Add a sentence to §3.1: *"The reversal is not an artifact of cross-backbone entropy scale: per-backbone quantile-normalized entropy reproduces the same sign-flip pattern (App. G.X)."*
- **If H0 partially holds**: Acknowledge that some "sign flips" are scale artifacts, but the within-backbone cross-environment reversals (which don't depend on cross-backbone comparison) are unchanged. Re-emphasize cross-environment reversal in §3.1; downgrade backbone-reversal claim from "structural" to "scale-dependent".

---

## Integration plan

### New appendix subsection
Add `\subsection{Robustness of Reversal to Entropy Normalization}` at the end of `appendix.tex` Section G (Robustness), right after `\subsection{Multi-Backbone Verification}`.

Content:
- 3-column comparison table (raw / per-(env, bb) Q / per-backbone Q).
- Bootstrap CI columns.
- One-paragraph interpretation.
- Summary sentence pointing back to §3.1.

### Body changes
- §3.1: After Table 1 description, add: *"The reversal is robust to per-(environment, backbone) entropy quantile normalization (Appendix G.Y), ruling out a tokenizer-scale artifact."*
- §3.2 backbone-reversal-as-prediction paragraph: add citation to G.Y.

### Stop conditions
- If quantile normalization eliminates the cross-backbone FEVER reversal entirely, **do not** silently drop the result. Either:
  (a) Reframe the paper around cross-environment reversal alone (still valid, just narrower claim), or
  (b) Switch the multi-backbone narrative from "direction flips" to "magnitude collapses to zero" (a weaker but still valid claim).

---

## Compute cost

- **Compute**: ~0 GPU-hours (analysis on logged data).
- **Engineering**: 4–8 hours of code (read existing logs → quantile-rank → recompute Spearman + bootstrap → format table).
- **Risk**: minimal — we have the data, this is a re-analysis.

---

## Owner / status

- [ ] Owner: TBD
- [ ] Status: not started
- [ ] Estimated completion: 1–2 days after start
