# Phase B Detailed Plan — Calibration-Quality Sweep (#02)

**Created**: 2026-04-27
**Owner**: zmli6 (liziming033@gmail.com)
**Status**: **smoke test submitted (job 24163286, array 0-5%6); awaiting validation before 6-119**
**Depends on**: Phase A complete ✅ (`phase_a_results/`)

## Submission log

| Time | Job ID | Array | Tasks | Status | Note |
|---|---|---|---|---|---|
| 2026-04-27 ~15:30 | 24163286 | 0-5%6 | 6 | running (gpu21/22/35/45) | Smoke test: hotpotqa @ n_cal=20 × all 6 methods |
| 2026-04-27 ~15:34 | 24163304 | 6-119%10 | 114 | queued | Full grid (rest of Wave 1) |

**Total**: 120 tasks committed. Walltime budget: 12h/task × 120 = 1440 GPU-h max; expected ~2-4h/task with %10 concurrency = ~24-48h wall-clock.

---

## Goal

Demonstrate that **better calibration → worse SR on misaligned envs**, transforming the abstract hook from an *inferred* claim (Table 4 wrong-direction ablation) into a *directly demonstrated controlled monotone effect*.

Per Phase B decision criteria in `00_execution_plan.md`:
- Misaligned envs (HotpotQA, FEVER): Spearman ρ(N_cal, SR) should be strongly negative.
- Aligned envs (APPS, WebShop): Spearman ρ(N_cal, SR) should be strongly positive.

---

## Scope

### Baselines (6, per user spec)

| Method | Calibration mechanism | N_cal-sensitive? |
|---|---|---|
| **CaTS** (Huang et al., 2026a) | Platt scaling on (signal, U) labels | YES |
| **SEAG** (Lee et al., 2025) | Confidence threshold via percentile sweep | YES |
| **CoRefine** (Jin et al., 2026) | Entropy threshold via percentile sweep | YES |
| **CATTS** (Lee et al., 2026) | Vote-based, K=5 (no labeled calibration) | weakly |
| **AUQ** (Zhang et al., 2026) | Verbalized uncertainty + threshold | weakly |
| **s1 budget** (Muennighoff et al., 2025) | Fixed token budget K (no calibration) | NO |

The 3 calibrated baselines (CaTS, SEAG, CoRefine) are where the sweep effect should manifest. The other 3 are reported as **flat-baseline anchors** — their N_cal sweep should show no/minimal change, controlling for "any baseline gets better with more data".

### Grid

```
N_cal  ∈ {20, 50, 100, 200, 500}      (5 calibration sizes)
env    ∈ {HotpotQA, FEVER, APPS, WebShop}  (4 envs, all Qwen3-4B)
method ∈ {catts, seag, corefine, cats, auq, s1_budget}  (6 baselines)
seed   ∈ {42}  (Wave 1 — 1 seed for pipeline validation)
       ∈ {42, 123, 456}  (Wave 2 — error bars for paper figure)
```

### Wave 1: Pipeline validation (commit now)

- 5 × 4 × 6 × 1 = **120 tasks**
- Estimated runtime: 2-3h per task on single A100
- With `%10` array concurrency: ~36 hours wall-clock
- Output: per-cell summary.json with SR, Cost ×base, gate-fire-rate

### Wave 2: Multi-seed error bars (commit IF Wave 1 looks clean)

- 5 × 4 × 6 × 3 = **360 tasks**
- Wall-clock with `%10`: ~3-5 days
- Replaces Wave 1 outputs (Wave 1 results retained for sanity comparison)

---

## Implementation

### Subsampling strategy

`phase1_signal_data.json` is per-step (~200-1200 rows per cell). N_cal sweep operates on **calibration-point count** (steps), not episodes:

| N_cal | Notes |
|---|---|
| 20 | very small; tests "does any baseline survive minimal calibration?" |
| 50 | matches default `min_cal_points` in many gates |
| 100 | typical mid-range |
| 200 | comfortable for most baselines |
| 500 | matches `max_points` default in `preload_phase1_data` |

Subsamples are pre-generated per (env, N_cal). Deterministic random sample with `seed=42` so reruns are stable.

**Per-env data ceiling** (steps in raw data, capping max usable N_cal):

| Env | N_total | N_cal_max usable |
|---|---:|---:|
| HotpotQA | 1208 | 500 ✓ |
| APPS | 439 | 400 (cap at 200 for safety, full 500 won't fit) |
| WebShop | 1073 | 500 ✓ |
| FEVER | 282 | 200 (cap; 500 not feasible — only 282 rows) |

**Action**: For FEVER/APPS at N_cal=500, fall back to N_cal=full_data (282 / 439 respectively) and flag the cell. Document in App C as a per-env cap.

### Code path

1. **`experiments/p7_phase_b_subsample.py`** (new)
   - Inputs: 4 envs' canonical phase1_signal_data paths (Phase A manifest).
   - Outputs: `results/phase_b_calibration_sweep/subsamples/n_cal_{N}/{env}.json` (5 × 4 = 20 files).
   - Deterministic shuffle then take first N points.

2. **`experiments/p5_competing_baselines.py`** (modify)
   - Add `--phase1-data-override` CLI flag → overrides config's `phase1_data_path`.
   - Add `--output-dir-override` CLI flag → overrides config's `output.results_dir`.
   - 0 logic changes otherwise; just additive flags.

3. **`configs/phase_b_calibration_sweep.yaml`** (new)
   - 4 env blocks (hotpotqa, fever, apps, webshop) — copy from `phase6_new_baselines.yaml`, add fever.
   - `methods`: all 6.
   - `phase1_data_path`: empty (overridden via CLI).
   - `output.results_dir`: `results/phase_b_calibration_sweep`.

4. **`scripts/run_phase_b_calibration_sweep.sbatch`** (new)
   - Array job: `0-119%10`.
   - Map IDX → (n_cal_idx, env_idx, method_idx).
   - Pass overrides to p5.

### Task index mapping

```
IDX = 0..119
N_CAL_IDX  = IDX / 24                      (0..4) → {20, 50, 100, 200, 500}
ENV_IDX    = (IDX % 24) / 6                (0..3) → {hotpotqa, fever, apps, webshop}
METHOD_IDX = IDX % 6                        (0..5) → {catts, seag, corefine, cats, auq, s1_budget}
```

Examples:
- IDX=0: n_cal=20, env=hotpotqa, method=catts
- IDX=23: n_cal=20, env=webshop, method=s1_budget
- IDX=24: n_cal=50, env=hotpotqa, method=catts
- IDX=119: n_cal=500, env=webshop, method=s1_budget

---

## Output structure

```
results/phase_b_calibration_sweep/
├── subsamples/
│   ├── n_cal_20/{hotpotqa,fever,apps,webshop}.json
│   ├── n_cal_50/...
│   ├── n_cal_100/...
│   ├── n_cal_200/...
│   └── n_cal_500/...
├── n_cal_20/
│   ├── hotpotqa/{catts,seag,corefine,cats,auq,s1_budget}/seed_42/summary.json
│   ├── fever/...
│   ├── apps/...
│   └── webshop/...
├── n_cal_50/
├── n_cal_100/
├── n_cal_200/
└── n_cal_500/
```

---

## Decision criteria (revisited from `00_execution_plan.md`)

| Spearman ρ(N_cal, SR) pattern | Action |
|---|---|
| Misaligned envs: ρ < -0.7; aligned: ρ > +0.7 | Headline claim bulletproofed. Keep abstract hook as-is. |
| Misaligned: ρ ∈ [-0.7, -0.3]; aligned positive | Soften "strictly worsens" → "monotonically degrades". |
| Non-monotone on misaligned | Soften abstract to "better calibration can fail to help". |
| Misaligned shows positive ρ | **Major framing problem.** Escalate before submission. |

**Per-baseline interpretation**:
- For CaTS, SEAG, CoRefine (calibrated): expect monotone behavior matching env type.
- For CATTS, AUQ, s1_budget (non-calibrated): expect ~flat curves (control).
- If non-calibrated baselines show monotone behavior → calibration data is leaking somewhere unexpected; investigate.

---

## Risks (Phase B specific)

| Risk | Likelihood | Mitigation |
|---|---|---|
| FEVER N_cal=500 / APPS N_cal=500 not feasible (data caps) | HIGH | Cap at N_total per cell; document. Already accounted for. |
| Per-task runtime > 6h → exceeds walltime | MED | Set `--time=12:00:00`. If still exceeds, reduce eval episodes from 30 to 20. |
| vLLM crash mid-task | LOW-MED | Per existing template: `set -eo pipefail` + `cleanup` trap. Failed tasks resubmitted manually. |
| All 6 baselines on FEVER produce 0 SR (env too hard) | MED | Verify on Wave 1 with seed=42; if all-zero, drop FEVER and use TWExpress fallback. |
| Output dir collision across N_cal values | LOW | Subdir per N_cal: `{base}/n_cal_{N}/{env}/{method}/seed_{S}/`. |

---

## Wave 1 completion criteria

Before committing to Wave 2:

- [ ] All 120 tasks completed (or failed-and-investigated)
- [ ] Per-(env, method) curves plotted (5 N_cal points each)
- [ ] Sanity check: CaTS/SEAG/CoRefine show non-flat curves; AUQ/s1_budget show flat curves
- [ ] Sanity check: misaligned envs (HotpotQA, FEVER) show negative trend on calibrated baselines
- [ ] Per-cell SR is non-trivially > 0 (not all-fail)
- [ ] Decision: commit to Wave 2 (3 seeds) or skip (single seed sufficient)

---

## Files to create

- `experiments/p7_phase_b_subsample.py`
- `experiments/p5_competing_baselines.py` ← **modify** (2 new flags)
- `configs/phase_b_calibration_sweep.yaml`
- `scripts/run_phase_b_calibration_sweep.sbatch`

## Files generated (Wave 1)

- `results/phase_b_calibration_sweep/subsamples/n_cal_{N}/{env}.json` (20 files)
- `results/phase_b_calibration_sweep/n_cal_{N}/{env}/{method}/seed_42/summary.json` (120 files)
- `logs/p_b_*.{out,err}` (120 × 2 SLURM logs)

---

**Last updated**: 2026-04-27
