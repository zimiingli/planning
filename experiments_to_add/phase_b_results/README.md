# Phase B Results: Calibration-Quality Sweep (#02)

**Date last updated**: 2026-04-28 (Wave 2 final: 235/360 cells, then cancelled)
**Owner**: zmli6 (liziming033@gmail.com)
**Plan**: [`../phase_b_plan.md`](../phase_b_plan.md)
**Spec**: [`../02_calibration_quality_sweep.md`](../02_calibration_quality_sweep.md)
**Status**: 🔴 **DEFERRED FROM PAPER (Path B chosen)** — see [Final verdict](#final-verdict-2026-04-28-post-wave-2) below.
**Why**: Wave 2 final data (with N_cal=500 added) reveals the apparent strong-monotone "calibration worsens SR on misaligned envs" result was a partial-data artifact. SR variation across N_cal ∈ [20, 500] is within statistical noise (~3pp) on every (env, method) cell. **Phase B does not provide evidence for the abstract hook**.
- **Wave 1 complete** (2026-04-27): 120/120 cells, 1 seed × 30 episodes — pipeline validation only.
- **Wave 2 cancelled** (2026-04-28): 235/360 cells run before cancellation; remaining 125 tasks cancelled to save compute (no recoverable signal expected).
**Harness**: `experiments/p5_competing_baselines.py` (with `--phase1-data-override` flag) + `experiments/p7_phase_b_subsample.py` (subsample generator) + `scripts/run_phase_b_calibration_sweep{,_wave2}.sbatch` (SLURM arrays)

---

## Final verdict (2026-04-28, post Wave 2)

**Decision: Path B — drop Phase B from the paper entirely.**

### What changed

Wave 2 partial (186/360 cells, missing most N_cal=500) appeared to show two clean strong-monotone-negative cells:
- HotpotQA / SEAG: ρ(N_cal, SR) = **-0.949**
- FEVER / CoRefine: ρ = **-0.738**

Wave 2 final (235/360 cells, with N_cal=500 populated to 47/72) **reverses both**:

| Cell | Wave 2 partial ρ | Wave 2 final ρ | What changed |
|---|---:|---:|---|
| HotpotQA / SEAG | -0.949 | **-0.359** | SR @ N_cal=500 reverts up to 0.70 |
| FEVER / CoRefine | -0.738 | **+0.154** | SR @ N_cal=500 also reverts up |

The mean-SR trajectories show why:

```
HotpotQA seag:  N_cal=20 → 50 → 100 → 200 → 500
                  0.71    0.70   0.69   0.69   0.70   ← N=500 reverts
                                                ↑
                                    range = 2pp (within ~3pp seed noise)

FEVER corefine: 0.49    0.49   0.47   0.48   0.49   ← N=500 reverts
                                                ↑
                                    range = 2pp (within ~3pp seed noise)
```

**The "strong-negative" finding was a 4-point artifact**: with only N_cal ∈ {20, 50, 100, 200} sampled, the small downward drift looks monotonic. Adding the 5th point (N_cal=500) fully within the noise band reveals there is no real trend.

### Why no monotone effect appears

| Reason | Detail |
|---|---|
| Effect size << noise floor | SE on SR with 100 ep × 3 seeds ≈ 3pp; observed range across N_cal is 1-3pp on every cell. |
| N_cal sweep is a *gentle* intervention | Compare with Table 4's wrong-direction ablation, which inverts the gate's predicted direction outright (23-37pp drop). N_cal grows the calibration set but doesn't reverse it; the gate's threshold converges quickly. |
| Threshold convergence | SEAG / CoRefine percentile-fit thresholds stabilize by N_cal ≈ 50; further data doesn't change the gate's decisions much. |
| Base agent dominance | On APPS (base SR ≈ 0.62), gates rarely fire (RR < 0.10), so SR is pinned to base regardless of N_cal. |
| WebShop SR-definition issue | Bimodal 0%/100% pattern; not interpretable for calibration sweep. |

### Verdict for paper integration

| Claim source | Status |
|---|---|
| Phase A (cross-backbone reversal robustness) | ✅ Integrated (§3.1, §3.2, App G.X, App G.Y). Done. |
| **Phase B (calibration-quality sweep)** | ❌ **Drop entirely from paper**. No evidence of monotone effect. |
| Abstract hook ("better calibration can worsen") | Stays. Supported by Table 4 wrong-direction ablation (23-37pp drop) — a stronger and cleaner intervention than the calibration data-size sweep. |

**Action**: Phase B compute artifacts (`results/phase_b_calibration_sweep{,_wave2}/`) and this `phase_b_results/` folder are retained for transparency / future revisits, but **none of it goes into the paper**.

### Lessons for future #02-style experiments

1. **Estimate effect size before designing the sweep**. If the predicted effect is < 2× the noise floor, the sweep can't detect it without massive episode counts.
2. **The wrong-direction ablation (Table 4) is the right tool for this hypothesis**. Inverting the gate is a much larger intervention than varying calibration data size.
3. **Partial data is dangerous**: 4-of-5 sweep points showed an artifactual monotone trend. Always analyze with the full grid before drawing conclusions.

---

## What's in this folder

| File | Format | Rows | Description |
|---|---|---:|---|
| `README.md` | markdown | – | This file: methodology + analysis + decision |
| `manifest.csv` | wide | 20 | Subsample provenance: which (env × N_cal) file fed each run |
| `grid_results.csv` | wide | 120 | Main: one row per (n_cal, env, method, seed) cell; SR, RR, gate params |
| `monotonicity.csv` | wide | 24 | One row per (env, method); Spearman ρ(N_cal, SR) and ρ(N_cal, RR) over the 5 N_cal points |
| `generate_csvs.py` | python | – | Reproducibility: regenerates the 3 CSVs from `results/phase_b_calibration_sweep/**/summary.json` |

---

## Research question

Does monotonically improving a baseline gate's calibration quality (via more training data, $N_{\text{cal}}$) cause monotone SR change in the **predicted direction** based on environment type?

- **Misaligned envs (Type-I)**: HotpotQA, FEVER on Qwen3-4B (Spearman ρ(σ, U) < 0 from Phase A). Gate fires on high entropy = WRONG direction. **Predicted**: SR monotonically *decreases* as $N_{\text{cal}}$ grows.
- **Aligned envs (Type-D)**: APPS, WebShop on Qwen3-4B (ρ(σ, U) > 0). Gate fires on high entropy = RIGHT direction. **Predicted**: SR monotonically *increases* as $N_{\text{cal}}$ grows.

If both predictions hold → abstract hook ("better calibration worsens performance on misaligned envs") is bulletproofed.

---

## What was run

### Grid

```
N_cal  ∈ {20, 50, 100, 200, 500}    (5 calibration sizes; APPS/FEVER capped at 282/439)
env    ∈ {hotpotqa, fever, apps, webshop}
method ∈ {catts, seag, corefine, cats, auq, s1_budget}    (6 baselines)
seed   ∈ {42}                        (Wave 1 — single seed)
eval episodes = 30 per cell
```

5 × 4 × 6 × 1 = **120 cells**.

### Baselines

Per the user spec, all 6 from the literature:

| Method | Reference | Calibration mechanism | N_cal-sensitive? |
|---|---|---|---|
| **CaTS** | Huang et al., 2026a | Platt scaling on (signal, U) labels | YES |
| **SEAG** | Lee et al., 2025 | Confidence threshold via percentile sweep | YES |
| **CoRefine** | Jin et al., 2026 | Entropy threshold via percentile sweep | YES |
| **CATTS** | Lee et al., 2026 | Vote-based, K=5 (no labeled calibration) | weakly |
| **AUQ** | Zhang et al., 2026 | Verbalized uncertainty + threshold | weakly |
| **s1 budget** | Muennighoff et al., 2025 | Fixed token budget K (no calibration) | NO |

CaTS/SEAG/CoRefine are the methods where $N_{\text{cal}}$ should produce a clear gradient. CATTS/AUQ/s1_budget serve as flat-baseline anchors.

---

## How it was run

### Step 1 — Phase A artifact: subsample generator

`experiments/p7_phase_b_subsample.py` reads each env's canonical `phase1_signal_data.json` (paths from Phase A manifest), shuffles deterministically with `seed=42`, and writes 5 nested subsamples per env to:

```
results/phase_b_calibration_sweep/subsamples/n_cal_{N}/{env}.json
```

Per-env caps (data exhausted before $N_{\text{cal}}=500$):

| Env | N_total | Caps at |
|---|---:|---:|
| HotpotQA | 1208 | – |
| WebShop | 1073 | – |
| **APPS** | **439** | **N_cal=500 → 439** |
| **FEVER** | **282** | **N_cal=200 → 282; N_cal=500 → 282** |

For FEVER, $N_{\text{cal}}\in\{200, 500\}$ collapse to the same dataset. This is a real limitation noted in Phase B plan and reflected in `manifest.csv:capped`.

### Step 2 — Runner extension

Added two CLI flags to `experiments/p5_competing_baselines.py`:
- `--phase1-data-override <path>` — overrides config's `phase1_data_path`
- `--output-dir-override <path>` — overrides config's `output.results_dir`

Both are zero-impact when unset. This lets the SLURM array vary calibration data per task without writing 5 separate configs.

### Step 3 — Config

`configs/phase_b_calibration_sweep.yaml` defines 4 envs (hotpotqa, fever, apps, webshop) with no `phase1_data_path` (overridden via CLI) and the 6-method list. `episodes: 30`, `probe_episodes: 0`.

### Step 4 — SLURM array

`scripts/run_phase_b_calibration_sweep.sbatch` maps each `SLURM_ARRAY_TASK_ID` ∈ [0, 119] to a unique (n_cal, env, method) triplet:

```
N_CAL_IDX  = IDX / 24       (0..4)  → {20, 50, 100, 200, 500}
ENV_IDX    = (IDX % 24) / 6 (0..3)  → {hotpotqa, fever, apps, webshop}
METHOD_IDX = IDX % 6        (0..5)  → {catts, seag, corefine, cats, auq, s1_budget}
```

`--gres=gpu:1`, `--mem=48G`, `--time=12:00:00`, `--array=0-119%10`. Per-task: spin up vLLM on a unique port, sed-patch the config to use that port, run p5 with overrides, teardown vLLM in EXIT trap.

### Step 5 — Issues encountered (and fixed)

1. **`frvc` env corruption** (initial failure of all 120 tasks): The `frvc` conda env had a partial vllm install — `vllm/version.py` and ~972 other .py files missing. Switched sbatch to use `frvc_review` (working backup env). Later rebuilt `frvc` from scratch via subagent (see `frvc.broken_20260427` backup); future runs can use either env.
2. **GPU memory contention** (second failure wave): With `--gpu-memory-utilization 0.85`, vLLM startup hit OOM on shared GPUs. Reduced to `0.30`. Most failures after this were on a specific node (`gpu54`) where another job was hogging memory.
3. **17 task failures** all on `gpu54` and `gpu48`: Resubmitted with `--exclude=gpu54,gpu48` (job 24171656). All 17 succeeded on retry.

### Wall-clock

- Job 24163286, 24163304: failed (frvc env broken). Wasted ~20 GPU-h.
- Job 24167902: failed (mem util too high).
- Job 24167911 (smoke test): 4 of 6 succeeded (2 stuck on gpu54).
- Job 24167919 (full grid 6-119): 97 of 114 succeeded; 17 failed on gpu54/48.
- Job 24171656 (retry of 17): all succeeded.

End-to-end: ~3 hours wall-clock from first submit to 120/120 (mostly waiting on QOS-limited concurrency).

---

## Analysis

### TL;DR (post Wave 2 partial, 2026-04-28) — ⚠️ **SUPERSEDED, see "Final verdict" above**

> **NOTE**: This section was written when Wave 2 was 52% complete (186/360 cells, N_cal=500 nearly empty). The strong-monotone "findings" reported below **did not survive when N_cal=500 data was added** (Wave 2 235/360). Both ρ values reverted toward zero; the apparent monotone trend was a 4-point partial-data artifact. Kept here as part of the analysis trail; the operative conclusion is Path B (drop Phase B from paper).

**Multi-seed averaging changed the picture.** Wave 1 looked mixed; Wave 2 (3 seeds × 100 ep, 52% complete) reveals two clean strong-monotone-negative cells on the misaligned envs:

- ⭐ **HotpotQA / SEAG**: ρ(N_cal, SR) = **-0.949** (Wave 1 had reported -0.258 = "flat"; multi-seed averaging unmasked the trend) — **superseded: -0.359 with full N_cal=500 data**
- ⭐ **FEVER / CoRefine**: ρ = **-0.738** (consistent with Wave 1's -0.707) — **superseded: +0.154 with full N_cal=500 data**

These are the lead cells for §5.2.1. — **superseded; no §5.2.1 will be written**

The **practical lesson** is that #02's effect size is real but small enough that a single seed × 30 episodes is insufficient to see it cleanly — exactly the noise floor we feared. — **superseded: with 100 ep × 3 seeds the effect is still within noise, suggesting the effect may not be there at all rather than just hidden by noise.**

### Wave 2 partial verdict (mean over available seeds)

| Env | Method | mean SR @ N_cal=20,50,100,200 | ρ | Verdict |
|---|---|---|---:|---|
| **hotpotqa** | **seag** | 0.71, 0.70, 0.69, 0.69 | **-0.949** | **✓ strong-neg ⭐ (matches misaligned)** |
| hotpotqa | corefine | 0.70, 0.71, 0.67, 0.68 | -0.600 | weak-neg (matches misaligned) |
| hotpotqa | catts | 0.53, –, 0.53, 0.60 | +0.600 | ✗ wrong-direction |
| hotpotqa | cats | 0.69, 0.55, 0.95, 0.92 | +0.600 | ✗ Platt degeneracy → always-fire |
| hotpotqa | auq | 0.97, 0.98, 0.98, 0.98 | +0.775 | ✗ already always-fire |
| hotpotqa | s1_budget | 0.97, 0.98, 0.97, 0.98 | +0.447 | ✗ (irrelevant — fixed budget) |
| **fever** | **corefine** | 0.49, 0.49, 0.47, 0.48 | **-0.738** | **✓ strong-neg ⭐** |
| fever | auq | 0.47, 0.46, 0.48, 0.46 | -0.400 | weak-neg |
| fever | catts | 0.34, 0.35, 0.34, 0.35 | +0.211 | flat |
| fever | seag | 0.49, 0.44, 0.45, 0.49 | +0.400 | ✗ wrong-direction (only 3 valid points; noisy) |
| fever | cats | 0.33, 0.34, 0.51, 0.47 | +0.800 | ✗ Platt degeneracy |
| fever | s1_budget | 0.45, 0.43, 0.48, 0.49 | +0.800 | ✗ (irrelevant) |
| apps | catts/seag/corefine/cats/auq/s1_budget | all ~0.61–0.65 flat | ≈0 | gates inert; SR pinned to base agent's 70%-ish |
| webshop | catts/seag/corefine/s1_budget | 0% | flat | SR-definition issue (binary thresholding) |
| webshop | cats/auq | 100% | flat | same issue |

(Cells marked "–" indicate missing seeds in the partial Wave 2 data. N_cal=500 is largely empty pending the rest of Wave 2.)

### Wave 1 vs Wave 2 comparison on misaligned envs

| Cell | Wave 1 ρ (1 seed × 30 ep) | Wave 2 ρ (≤3 seeds × 100 ep) | Δ |
|---|---:|---:|---|
| HotpotQA seag | -0.258 (flat) | **-0.949** | **dramatic** — multi-seed unmasked trend |
| HotpotQA corefine | -0.158 (flat) | -0.600 | improved (still weak-neg) |
| FEVER seag | -0.775 (strong-neg) | +0.400 (wrong) | flipped — Wave 1's "support" was a single-seed fluke |
| FEVER corefine | -0.707 (strong-neg) | -0.738 | consistent ✓ |
| HotpotQA cats | +0.783 (wrong) | +0.600 | persistent wrong-direction (Platt degeneracy) |
| FEVER cats | +0.894 (wrong) | +0.800 | same |

### Key narrative finding

Different gate **calibration mechanisms** behave differently on misaligned envs:

| Calibration class | Methods | N_cal=20→200 behavior on misaligned envs | What this implies |
|---|---|---|---|
| **Threshold from labeled data** (single threshold percentile-fit on (signal, U) pairs) | SEAG, CoRefine | **Monotone SR degradation** as N_cal grows | Predicted by σ-insufficiency hypothesis ✓ |
| **Platt scaling on labels** | CaTS | Degenerates to always-fire (RR→1) on imbalanced labels; SR appears to "rise" | Latent bug in Platt-scaling baselines, not a refutation; report honestly in App C |
| **Verbalized / vote-based / fixed-budget** | AUQ, CATTS, s1_budget | Mostly flat (or degenerate from start) | Don't actually use N_cal; serve as control showing "more data" alone doesn't move SR |

This is a **cleaner and more discriminating story** than "all baselines fail equally". It's actually paper-positive: we can name a specific mechanism (labeled-threshold gates) that exhibits the predicted failure mode, and explain why other classes don't.

### Path A vs Path B vs the actual third option

The Wave 1 README proposed:
- **A**: Run Wave 2 → if all baselines show predicted patterns, full sweep claim.
- **B**: Skip Wave 2, soften claim to "FEVER seag/corefine only".

Wave 2 partial data points to a **third option (recommended)**:

> **C. Mechanism-stratified claim**: Lead with the SEAG-on-HotpotQA + CoRefine-on-FEVER pair as the σ-insufficiency demonstration. Group the 6 baselines by calibration mechanism (labeled-threshold vs Platt vs other), and report that **only the labeled-threshold class** exhibits the predicted monotone degradation. CaTS's Platt-degeneracy gets a paragraph in App C as an honest second finding.

Draft §5.2.1 lead sentence:

> "On misaligned environments, baselines that explicitly fit a calibrated threshold from labeled $(\sigma, U)$ data exhibit monotone SR degradation as the calibration set $N_{\text{cal}}$ grows — exactly the predicted artifact of σ-insufficiency. SEAG on HotpotQA shows $\rho(N_{\text{cal}}, \text{SR})\!=\!-0.95$; CoRefine on FEVER shows $\rho\!=\!-0.74$ (Fig. X, App C). Methods that bypass labeled calibration (CATTS voting, AUQ verbalization, s1 budget) show no monotone pattern, and Platt-scaled CaTS degenerates to always-fire on imbalanced labels (App C.Y)."

This claim is **stronger than B** (HotpotQA actually delivers under multi-seed) and **more nuanced/defensible than A** (we don't claim all 6 baselines fail; we claim a specific mechanism does, and we explain the others).

---

### Original Wave 1 single-seed analysis (kept for comparison)

| Env | Method | ρ(N_cal, SR) | Interpretation |
|---|---|---:|---|
| **fever** | **seag** | **-0.775** | **strong-negative (matches misaligned)** ✓ |
| **fever** | **corefine** | **-0.707** | **strong-negative (matches misaligned)** ✓ |
| hotpotqa | seag | -0.258 | flat |
| hotpotqa | corefine | -0.158 | flat |
| hotpotqa | cats | +0.783 | **WRONG-DIRECTION** (positive on misaligned) |
| fever | cats | +0.894 | **WRONG-DIRECTION** (positive on misaligned) |
| apps | s1_budget | -0.866 | **WRONG-DIRECTION** (negative on aligned) |
| (others — auq, catts, s1_budget on most cells) | | nan / 0.000 | flat (constant SR across N_cal) |

(Full table in `monotonicity.csv`. The above shows entries where |ρ| > 0.3.)

### What we got right

The cleanest finding: **SEAG and CoRefine on FEVER show the predicted monotonic-negative relationship**, with ρ = -0.775 and -0.707. This is exactly what #02 was designed to demonstrate — better calibration → worse SR on a misaligned env.

These two methods are the right ones for this test: both fit a single threshold on (signal, U) labels, so they directly use $N_{\text{cal}}$ to "improve" calibration. With more (signal, U) data on a *misaligned* env, the threshold gets pushed to fire more aggressively in the wrong direction → SR drops.

### What we got wrong (or didn't see)

1. **HotpotQA SEAG/CoRefine flat**: ρ ≈ -0.16 to -0.26. Same methods, same env type as FEVER, but no clear gradient. Possibly:
   - Single seed + 30 episodes → SR noise floor of ±5-10%, swamps the effect.
   - HotpotQA's signal magnitude (-0.327) is stronger than FEVER's (-0.119), but FEVER's worse base SR makes the gate's wrong-direction triggering more visible.

2. **CaTS shows WRONG-DIRECTION on both misaligned envs (HotpotQA ρ=+0.78, FEVER ρ=+0.89)**: At higher $N_{\text{cal}}$, CaTS's Platt regression converges to "always fire" on misaligned data (RR jumps to ~1.0). This is a known degeneracy of Platt scaling on imbalanced labels — not a refutation of the calibration hypothesis, but a complication. CaTS is "calibrating away" toward always-trigger, which on these envs accidentally improves SR (because the base agent is bad and any extra rollout helps).

3. **CATTS / AUQ / s1_budget mostly flat**: As expected — they don't really use $N_{\text{cal}}$. CATTS's threshold is computed on entropy distribution; AUQ uses verbalized confidence on the fly; s1_budget uses a fixed K. The flat curves are a control showing "data quantity isn't itself driving SR change".

4. **APPS all flat at 70.0% across most methods**: The base agent's SR on APPS is 70%, and most methods at small $N_{\text{cal}}$ have RR < 0.10 — they barely trigger. The gate is effectively inert, and we see base SR. To get a real $N_{\text{cal}}$ gradient on APPS, we likely need either more episodes (lower noise) or a method that triggers more readily.

5. **WebShop anomalous**: SR is either 0% (most methods, all $N_{\text{cal}}$) or 100% (auq across all $N_{\text{cal}}$, with avg_reward=0.8). The 0%/100% bimodality suggests a `success_rate` definition issue specific to WebShop (likely thresholded at reward ≥ some-value; at low reward, threshold not met, so SR=0). We need to reconcile this with `avg_reward` to get the actual gradient. **Action**: do not include WebShop in the §5.2.1 figure as currently produced; investigate first.

### Verdict relative to Phase B decision criteria

Per `00_execution_plan.md`:

| Pattern (Spearman ρ over N_cal) | Action |
|---|---|
| Misaligned: ρ < -0.7 ; aligned: ρ > +0.7 | Headline claim bulletproofed. |
| Misaligned: ρ ∈ [-0.7, -0.3] ; aligned positive | Soften to "monotonically degrades". |
| Non-monotone on misaligned | Soften abstract to "can fail to help". |
| Misaligned shows positive ρ | Major framing problem. |

Wave 1 result is **mixed**:
- ✓ Two cells (FEVER seag/corefine) hit the strong-negative target.
- ✗ HotpotQA seag/corefine fell into "flat" (|ρ| < 0.3).
- ✗ CaTS shows wrong-direction on misaligned envs (degenerate Platt scaling).
- ✗ APPS flat (gates inert at 30 episodes).
- ✗ WebShop anomalous.

Honest call: Wave 1 alone is **not sufficient** to defend the headline claim with high confidence. → **Wave 2 was launched and is now revealing the trends Wave 1 missed (see Wave 2 verdict above).**

### Why Wave 1 wasn't enough (and what Wave 2 fixed)

| Issue | Source | Wave 2 fix | Result so far |
|---|---|---|---|
| 30 episodes/cell → high SR noise | Compute budget choice | 100 episodes/cell | ✓ Wave 2 noise visibly lower |
| 1 seed → no error bars | Pipeline validation only | 3 seeds (42, 123, 456) | ✓ Mean over seeds unmasked HotpotQA seag from -0.26 to -0.95 |
| WebShop SR definition unclear | Env/eval pipeline | Not fixed in Wave 2 | ✗ Still 0%/100% bimodal — must reconcile or drop |
| APPS gates inert | Base SR too high | Not fixed | ✗ APPS still flat at ~0.62 across all methods/N_cal |
| CaTS degenerates to always-fire | Platt scaling on imbalanced labels | Not fixed (intrinsic) | ✗ Persists in Wave 2; report as App C finding |

### Recommendation (post Wave 2 partial)

Adopt **Path C — Mechanism-stratified claim** (see "Wave 2 partial verdict" above). Concrete steps:

1. **Lead figure** for §5.2.1: 2-panel SR vs N_cal showing
   - Panel A (misaligned): HotpotQA SEAG curve + FEVER CoRefine curve (both monotone-down).
   - Panel B (control): same methods on aligned env or non-calibrated baselines (flat).
2. **App C "calibration ablation" subsection**:
   - Full table with all 6 baselines × 4 envs × 5 N_cal (Wave 2 final).
   - One paragraph on CaTS Platt-degeneracy on imbalanced labels.
   - One paragraph on WebShop SR-definition caveat (or drop WebShop entirely if cannot resolve).
   - One paragraph on APPS gate-inertness (gates rarely fire when base agent is competent enough).
3. **Don't overclaim**: §5.2.1 lead sentence (drafted above) explicitly names the mechanism (labeled-threshold gates) that fails, doesn't claim all baselines fail.

**Pending Wave 2 completion** (currently 186/360, N_cal=500 mostly empty): trends may sharpen further, especially for the larger N_cal points where the σ-insufficiency effect should be strongest. Re-evaluate when complete.

---

## Files & paths

```
/home/uuc24002/FRVC/
├── experiments/
│   ├── p5_competing_baselines.py            (modified: --phase1-data-override, --output-dir-override)
│   └── p7_phase_b_subsample.py              (new: subsample generator)
├── configs/
│   └── phase_b_calibration_sweep.yaml       (new: 4 envs × 6 methods)
├── scripts/
│   └── run_phase_b_calibration_sweep.sbatch (new: 120-task array; uses frvc_review env, gpu_mem_util=0.30)
├── results/phase_b_calibration_sweep/
│   ├── subsamples/n_cal_{20,50,100,200,500}/{env}.json   (20 files)
│   └── n_cal_{N}/{env}/{method}/seed_42/summary.json     (120 files)
└── planning/experiments_to_add/phase_b_results/
    ├── README.md                             (this file)
    ├── grid_results.csv                      (120 rows)
    ├── monotonicity.csv                       (24 rows)
    ├── manifest.csv                          (20 rows)
    └── generate_csvs.py                      (regenerates the 3 CSVs)
```

## Reproducibility

```bash
# 1. Regenerate subsamples (deterministic with seed=42)
python experiments/p7_phase_b_subsample.py

# 2. Submit array job (or array=<list> for retries)
sbatch scripts/run_phase_b_calibration_sweep.sbatch

# 3. After all tasks complete: regenerate CSVs from disk
python planning/experiments_to_add/phase_b_results/generate_csvs.py
```

---

**Last updated**: 2026-04-28 (post-Wave 2 partial 186/360; recommended Path C — mechanism-stratified claim)

## Update log

- 2026-04-27 ~late evening: Wave 1 complete (120/120). Initial analysis: 2 cells matched, others mixed. Recommended Wave 2.
- 2026-04-27 ~midnight: Wave 2 launched (job 24171804, 360 tasks).
- 2026-04-28 ~early morning: Wave 2 retry submitted (job 24178742, 102 tasks on bad-node failures: gpu47 added to exclude list).
- 2026-04-28 morning: Wave 2 at 52% (186/360). HotpotQA SEAG: ρ flipped from -0.26 (W1) to -0.95 (W2 partial) — multi-seed unmasking. Recommended Path C mechanism-stratified claim. README updated with Wave 2 verdict and revised §5.2.1 lead sentence.
- 2026-04-28 afternoon: Wave 2 at 65% (235/360, N_cal=500 column populated). **Reversal**: HotpotQA SEAG ρ goes -0.95 → **-0.36**, FEVER CoRefine ρ goes -0.74 → **+0.15**. Earlier "strong-monotone" was a 4-point partial-data artifact. Decision: **Path B — drop Phase B from paper**. Wave 2 cancelled (job 24171804 + 24178742). Phase A integration unaffected.
