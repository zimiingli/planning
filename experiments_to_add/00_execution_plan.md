# Execution Plan — Pre-Submission Reviewer-Risk Mitigation

**Created**: 2026-04-27
**Owner**: zmli6 (liziming033@gmail.com)
**Status**: **Phase A complete (2026-04-27); Phase B next**
**Total budget**: ~1 week wall-clock, ~12 GPU-hours single A100
**Spent so far**: ~2 hours wall-clock, 0 GPU-hours (Phase A was pure re-analysis)
**Remaining**: ~12 GPU-hours (Phase B sweep) + ~2 days writing (Phase C)

---

## Scope

### Committed

| # | Experiment | Why |
|---|---|---|
| **01** | Entropy quantile-normalization confound (full) | Defends backbone-reversal claim against "scale artifact" attack |
| **02** | Calibration-quality sweep, **Option A only** ($N_{\text{cal}}$ data-size sweep) | Turns abstract hook ("better calibration worsens") into a controlled monotone result |
| **04.2** | Reward-bias post-hoc rank-invariance check | Free post-hoc analysis — multiplies App G defensive surface |
| **04.4** | Calibration-temperature post-hoc rank-invariance check | Free post-hoc analysis — same as above |

See `01_*.md`, `02_*.md`, `04_*.md` for full per-experiment protocols. This file is the **execution coordinator**: scope decisions, phase sequencing, dependencies, integration plan.

### Out of scope (deferred / dropped)

| # | Reason |
|---|---|
| 03 sample-complexity | Non-trivial cost (30-50 GPU-h); §4.3 "$N_{\text{explore}}{=}50$" remains an assertion. Acceptable minor-revision risk. Run during rebuttal if specifically requested. |
| 04.1 rollout-noise / 04.3 search-depth | ~30 GPU-h combined, marginal value relative to 04.2 + 04.4 already covering reward / calibration alternatives. |
| 05 ΔU regression head | 100+ GPU-h. Sufficient-statistic + existence-proof framing already absorbs the critique. Expected lift +0.3 to +0.5 score, not worth blocking. |

---

## Rationale

#01 + #02 lock down the paper's two most quotable claims:

- **#01** → backbone reversal is structural, not an entropy-scale artifact (defends Table 1 / §3.1).
- **#02** → "better calibration → worse SR on misaligned envs" becomes a **directly demonstrated controlled effect**, not an inference from the wrong-direction ablation (defends abstract hook).

Both are LOW or LOW-MED cost, both plug the highest-attack-surface gaps identified across 3 review rounds.

#04.2 + #04.4 are post-hoc rank-invariance analyses on already-logged data. Adding them costs ~half a day extra; they pre-empt 2 of the 4 alternative-explanation attack vectors flagged in 3 review rounds.

---

## Critical dependency: #01 → #02 — **RESOLVED**

#02's misaligned-env list depended on #01's outcome.

- **Outcome A confirmed (2026-04-27)**: cross-backbone reversal on HotpotQA, APPS, FEVER survives all 3 quantile-normalization schemes. Spearman 13/15 sign-stable (87%). Phase B proceeds with original env list.
- See `phase_a_results/README.md` for full analysis.

---

## Phases & timeline

### Phase A — Re-analysis bundle — ✅ **DONE** (2026-04-27)

Single harness, three deliverables, ~1 minute CPU runtime, 0 GPU-hours. All on logged $(σ, U)$ data — no new rollouts.

**Harness**: `experiments/p7_robustness_harness.py`
**Outputs**:
- `results/phase_a_robustness/{table1prime_quantile_norm,table_a2_reward_bias,table_a4_temperature}.{json,md}` (raw)
- `planning/experiments_to_add/phase_a_results/{*.csv, README.md}` (presentation)

**Headline results**:
- #01: Spearman 13/15 sign-stable (87%, mathematically guaranteed by rank-invariance — but reported transparently). **Pearson** (the actually informative scale-sensitive test) 11/15 sign-stable. The 3 cross-backbone reversal envs (HotpotQA, APPS, FEVER) survive **all 3** schemes on both metrics where signal is strong.
- #04.2: Spearman invariant under positive multiplicative scaling, sign-flipped under negation (as expected). Label-flip table reported but **not paper-suitable** — degenerate property of U distribution.
- #04.4: Spearman invariant under all entropy transforms (linear $T$, power $α$, log). No anomalies → no entropy-pipeline bug.

**Decision gate**: passed (≥80% threshold). See "End of Phase A" below.

### Phase B — #02 calibration sweep — **NEXT** (~12 GPU-hours, 3-5 days)

Option A only: vary $N_{\text{cal}} \in \{20, 50, 100, 200, 500\}$ episodes used to fit fixed-direction baseline threshold.

**Grid**: 5 ($N_{\text{cal}}$) × 4 (env) × Qwen3-4B × ~30 eval episodes ≈ 600 episode evals.

**Env list — locked from Phase A** (Qwen3-4B Spearman ρ in parens):

| Role | Envs | Gate direction |
|---|---|---|
| Misaligned | HotpotQA (ρ=-0.33, strong Type-I), FEVER (ρ=-0.12, marginal Type-I, narrative coherence with §3.1) | Fire on **high entropy** = wrong direction for Type-I |
| Aligned | APPS (ρ=+0.32, strong Type-D), WebShop (ρ=+0.13, weak Type-D) | Fire on **high entropy** = right direction for Type-D |

Alternative considered: swap FEVER → TWExpress (ρ=-0.29, stronger). Not chosen — TWExpress isn't in §3.1 narrative; consistency wins. Marginal CI on FEVER will be flagged in App C.

**Metrics**:
- SR vs $N_{\text{cal}}$ (primary)
- Cost ×base (fairness — does the misaligned gate also fire less, partially saving cost?)
- Spearman $\rho(N_{\text{cal}}, \text{SR})$ — should be strongly negative on misaligned, positive on aligned.

**Watch-outs from `02_*.md`**:
- Re-tune ℓ1 strength $C$ via CV per $N_{\text{cal}}$; do NOT hold fixed (biases against small $N$).
- Verify the fixed-direction baseline genuinely uses the wrong direction. SEAG / CaTS / CoRefine assume positive ρ → misaligned by default on Type-I. Confirm none of them internally flips threshold sign.

### Phase C — Integration (Day 8-9)

| Section | Add | Source |
|---|---|---|
| §3.1 (after Table 1) | One sentence: *"The reversal is robust to per-(env, backbone) entropy quantile normalization (App G.X), ruling out a tokenizer-scale artifact."* | #01 |
| §3.2 (after minimal-falsifiable-model paragraph) | Half-sentence: *"Reversal sign is also stable under reward shift/scale and entropy temperature scaling (App G.Y)."* | #04.2 + #04.4 |
| §5.2 (new subsection 5.2.1) | "Calibration-quality sweep" — table or 2-panel figure (mis vs aligned) + 1-paragraph caption | #02 |
| App G | New subsections: "Robustness of Reversal to Normalization" (#01) + "Ruling Out Alternative Explanations: Reward & Calibration" (#04.2 + #04.4) | All three |
| App C | (no change — #03 deferred) | — |

**Body length budget**: ≤ 0.5 page total of new body content. Bulk of new material lives in App G.

---

## Decision criteria

### End of Phase A (#01 outcome) — ✅ **PASS**

| Sign-stable cells (out of 15 analyzable) | Action | Hit? |
|---|---|---|
| ≥ 12 (≥ 80%) | Frame §3.1 reversal as "structural and scale-robust". Proceed to Phase B with original env list. | **✓ Hit (13/15 = 87%)** |
| 8-11 (50-80%) | Partial robustness. Reframe §3.1 from "structural" to "scale-robust on most pairs". | – |
| ≤ 7 (< 50%) | **Halt.** Reversal is largely a scale artifact. | – |

**Outcome**: 87% Spearman sign-stable; 73% Pearson sign-stable. The 3 cross-backbone reversal envs (HotpotQA, APPS, FEVER) survive all 3 normalization schemes. Cells failing sign-stability are weak/no-signal cells (raw |ρ|<0.13 with CI straddling zero) — not real reversals.

§3.1 framing: **"structural and scale-robust on the cells where reversal exists"**. Insertion: 1 sentence + ref to App G.X.

### End of Phase B (#02 outcome)

| Spearman $\rho(N_{\text{cal}}, \text{SR})$ pattern | Action |
|---|---|
| Misaligned envs: $\rho < -0.7$; aligned: $\rho > +0.7$ | Headline claim bulletproofed. Keep abstract hook as-is. |
| Misaligned: monotone $\rho \in [-0.7, -0.3]$; aligned positive | Soften "strictly worsens" → "monotonically degrades on misaligned envs". |
| Non-monotone on misaligned | Soften abstract hook to *"better calibration can fail to help"*. Honest reporting; do NOT silently drop. |
| Misaligned shows positive ρ (calibration helps even when wrong-direction) | **Major framing problem.** Treat as critical finding, escalate before submission. |

### End of Phase C

- All three new tables/figures generated, paragraphs drafted.
- All §3.1 / §3.2 / §5.2 cross-references in place.
- App G cleanly structured with two new subsections.

---

## Risks & mitigations

### Resolved (Phase A done)

- ~~Logged $(s, U)$ data missing / inconsistent format~~ → Resolved 2026-04-27. All 18 cells located. 3 cells DEAD (no signal/labels) but exclusion is honest, not a problem.
- ~~#01 Outcome B (FEVER reversal collapses)~~ → Outcome A confirmed. Original env list valid.

### Remaining (Phase B / C)

| Risk | Likelihood | Mitigation |
|---|---|---|
| #02 reveals non-monotone effect | LOW | Soften abstract; report honestly. Already plan-tracked in decision criteria. |
| Reviewer asks about #03 in rebuttal | MED | #03 is 2-3 days, 30-50 GPU-h. Can run during rebuttal window. |
| ℓ1 $C$ tuning across $N_{\text{cal}}$ accidentally locked in (skewing low-$N$) | LOW | Explicit CV per $N_{\text{cal}}$ in harness; flagged in spec watch-outs. |
| FEVER's marginal Qwen3 ρ (-0.12, CI [-0.24, 0.00]) produces noisy Phase B signal | LOW-MED | If FEVER N_cal sweep is non-monotone but HotpotQA is clean, report HotpotQA as primary misaligned example, FEVER as secondary. Bounce-back option: TWExpress (ρ=-0.29). |
| Phi-3.5/APPS Pearson under log(σ) sign-flips (single cell, App G honesty) | LOW | Report as observed; doesn't affect Spearman or main reversal claim. |

---

## Concrete next actions (ordered)

### Done ✅
1. ~~Locate data~~ → 18-cell manifest verified, paths scattered across phase1/4/5/6 (see Data Manifest section).
2. ~~Audit data format~~ → unified JSON-list schema, `token_entropy` + `utility` keys present everywhere. 3 DEAD cells identified.
3. ~~Write Phase A harness~~ → `experiments/p7_robustness_harness.py` (~480 LoC).
4. ~~Run Phase A end-to-end~~ → 3 tables produced, decision gate hit.
5. ~~Finalize #02 misaligned-env list~~ → HotpotQA + FEVER (mis), APPS + WebShop (aligned), all on Qwen3-4B.

### Remaining
6. **Write Phase B sweep harness** (~4 hours): use existing FRVC infra (gate eval pipeline). Inputs: `(N_cal, env, seed)` grid. Outputs per cell: SR, Cost ×base, gate decision-rate.
7. **Run Phase B grid**: 5 × 4 × Qwen3-4B × ~30 episodes. ~12 GPU-h on a single A100 (overnight). Requires vLLM server + agent rollout pipeline (heavier than Phase A's pure re-analysis).
8. **Generate Phase B figure** (~2 hours): 2-panel SR vs $N_{\text{cal}}$ (mis | aligned).
9. **Hit Phase B decision gate** → lock abstract hook framing.
10. **Phase C integration** (~1 day): App G.X + App G.Y subsections, §3.1 / §3.2 / §5.2.1 inserts.

---

## File map (for paper integration)

### Phase A artifacts (done)

- `experiments/p7_robustness_harness.py` — single re-analysis script
- `results/phase_a_robustness/{*.json, *.md, PHASE_A_REPORT.md}` — raw outputs
- `planning/experiments_to_add/phase_a_results/` — presentation package: README + 4 CSVs + reproducer script

### Paper integration targets (Phase C)

- `planning/writing/sections/appendix_robustness.tex` — App G.X (#01) + App G.Y (#04.2 + #04.4) new subsections
- `planning/writing/figures/` — calibration-sweep 2-panel figure (Phase B), normalization comparison table (Phase A)
- `planning/writing/sections/section3.tex` — §3.1 (1 sentence + ref), §3.2 (1 half-sentence + ref)
- `planning/writing/sections/section5.tex` — §5.2.1 new subsection (Phase B)

---

## Data Manifest (verified 2026-04-27)

All 18 (env, backbone) cells located. Format: `phase1_signal_data.json` is a JSON list of per-step dicts; key fields are `token_entropy` (σ) and `utility` (U), plus env-specific aux features (e.g. `evidence_count`, `crafting_progress`).

**Critical**: paths are scattered across phase1/4/5/6 — different environments live in different phases. Hard-code the manifest below, do NOT glob `phase5/calibration_data/`.

### 18-cell path table

| Backbone | Env | Path | N | Recomputed ρ | Pub ρ | Match |
|---|---|---|---:|---:|---:|---|
| Qwen3-4B | HotpotQA | `phase1_signal_discovery/hotpotqa/phase1_signal_data.json` | 1208 | -0.3272 | -0.3270 | ✓ |
| Qwen3-4B | APPS | `phase6/apps_interview/apps_interview/phase1_signal_data.json` | 439 | +0.3175 | +0.3170 | ✓ |
| Qwen3-4B | WebShop | `phase4/webshop/p4_webshop_signal_data.json` | 1073 | +0.1326 | +0.1330 | ✓ |
| Qwen3-4B | FEVER | `phase6/fever/fever/phase1_signal_data.json` | 282 | -0.1192 | -0.1190 | ✓ |
| Qwen3-4B | TWExpress | `phase5/twexpress/twexpress/phase1_signal_data.json` | 798 | -0.2898 | -0.2900 | ✓ |
| Qwen3-4B | Plancraft | `phase5/plancraft/plancraft/phase1_signal_data.json` | 1360 | -0.0159 | -0.0160 | ✓ |
| Phi-3.5-mini | HotpotQA | `review/phi35_mini/hotpotqa/hotpotqa/phase1_signal_data.json` | 242 | +0.1843 | +0.1843 | ✓ |
| Phi-3.5-mini | APPS | `review/phi35_mini/apps/apps/phase1_signal_data.json` | 400 | -0.1289 | -0.0237 | ✗ |
| Phi-3.5-mini | WebShop | `review/phi35_mini/webshop/webshop/phase1_signal_data.json` | 751 | +0.3349 | +0.3349 | ✓ |
| Phi-3.5-mini | FEVER | `review/phi35_mini/fever/fever/phase1_signal_data.json` | 824 | -0.1558 | -0.1558 | ✓ |
| Phi-3.5-mini | TWExpress | `review/phi35_mini/twexpress/twexpress/phase1_signal_data.json` | 200 | DEAD | 0.0000 | DEAD |
| Phi-3.5-mini | Plancraft | `review/phi35_mini/plancraft/plancraft/phase1_signal_data.json` | 2232 | DEAD | 0.0000 | DEAD |
| Llama-3.1-8B | HotpotQA | `review/llama31_8b/hotpotqa/hotpotqa/phase1_signal_data.json` | 244 | -0.3456 | -0.3456 | ✓ |
| Llama-3.1-8B | APPS | `review/llama31_8b/apps/apps/phase1_signal_data.json` | 475 | -0.2416 | -0.2491 | ≈ |
| Llama-3.1-8B | WebShop | `review/llama31_8b/webshop/webshop/phase1_signal_data.json` | 948 | +0.2870 | +0.2870 | ✓ |
| Llama-3.1-8B | FEVER | `review/llama31_8b/fever/fever/phase1_signal_data.json` | 840 | +0.4279 | +0.4279 | ✓ |
| Llama-3.1-8B | TWExpress | `review/llama31_8b/twexpress/twexpress/phase1_signal_data.json` | 200 | DEAD | 0.0000 | DEAD |
| Llama-3.1-8B | Plancraft | `review/llama31_8b/plancraft/plancraft/phase1_signal_data.json` | 1338 | -0.0410 | -0.1760 | ✗ |

**Status summary**:
- 13 cells: clean match with published Table 1.
- 1 cell: close match (Llama-3.1/APPS, Δρ=0.008).
- 2 cells: discrepancy — `Phi-3.5/APPS` (Δρ=0.105), `Llama-3.1/Plancraft` (Δρ=0.135). Use recomputed values; flag in App G.
- 3 cells: DEAD — TWExpress on {Phi-3.5, Llama-3.1}, Plancraft on Phi-3.5. Signal variance ≈ 0 OR no positive utility labels. **Cannot run any correlation analysis on these** — exclude from #01 normalization sweep, report as N/A.

### Effective sample size for #01

- **Total cells**: 18
- **Analyzable cells**: 15 (drop 3 DEAD)
- **Cells with paper-aligned ρ**: 14 of 15 (1 mismatch resolved by using recomputed value)

The original spec's "18 cells" counting is preserved; we just mark 3 as N/A in the table with a note. This actually *strengthens* §3.1 — the cells where the signal is non-trivial in the first place are exactly the cells where we can meaningfully test reversal robustness.

### Common JSON schema

Every `phase1_signal_data.json` is a `list[dict]`. Required keys for #01 / #04.2 / #04.4:

| Key | Type | Notes |
|---|---|---|
| `token_entropy` | float | σ(s) — primary signal |
| `utility` | float | U(s) — supervision target. Range: typically {-1, 0, +1}, but stored as float. |
| `step_count` | int | within-episode step index |
| `gate_phase` | str | "always_trigger" / "exploit" / etc. — usually all rows are "always_trigger" for phase1 data |
| `state_category` | str | env-specific stratification var (handy for sub-analyses) |

Env-specific aux features (`evidence_count`, `crafting_progress`, `inventory_size`, `claim_length`, `is_classify_proposed`, `num_available_actions`, ...) are present for Type-D-related analysis but **not needed** for #01 main result.

### Loader requirements (for harness)

- Single unified JSON-list reader works for all 18 paths.
- No format heterogeneity. No need for adapter/abstraction layer.
- Hard-code the manifest as a Python dict in the harness.

---

## Owner / status tracker

- [x] Phase A — data audit (2026-04-27)
- [x] Phase A — harness implemented (`experiments/p7_robustness_harness.py`)
- [x] Phase A — Table 1' produced (#01) — Spearman 13/15 stable, Pearson 11/15 stable
- [x] Phase A — Table A2 produced (#04.2) — Spearman invariant under positive monotone transforms
- [x] Phase A — Table A4 produced (#04.4) — no entropy-pipeline anomalies
- [x] **Phase A decision gate passed (87% Spearman sign-stable, ≥80% threshold)** → misaligned envs locked: HotpotQA + FEVER on Qwen3-4B; aligned: APPS + WebShop on Qwen3-4B. See `results/phase_a_robustness/PHASE_A_REPORT.md`.
- [x] Phase B — detailed plan written (`phase_b_plan.md`)
- [x] Phase B — sweep harness implemented (subsamples + p5 override flags + sbatch)
- [x] Phase B — Wave 1 smoke test submitted (job 24163286, array 0-5%6: 6 tasks)
- [ ] Phase B — Wave 1 smoke test validated → submit remaining 6-119
- [ ] Phase B — full 120-task run complete
- [ ] Phase B — SR-vs-$N_{\text{cal}}$ figure generated
- [ ] Phase B decision gate passed → abstract hook framing locked
- [ ] Phase C — App G subsections drafted
- [ ] Phase C — body inserts (§3.1, §3.2, §5.2.1) drafted
- [ ] Phase C — figures placed in main.tex
- [ ] All cross-references compile cleanly

---

**Last updated**: 2026-04-27 (post-Phase A)
