# Rebuttal Preparation: New Benchmark Experiments

> Created: 2026-04-17
> Last updated: 2026-04-21
> Status: **Step 1 done** (signal discovery), **Step 2 + CB FAILED** (OpenRouter credits exhausted). Waiting for top-up to run slim 7-method version.
> Model: openai/gpt-4o-mini (via OpenRouter)

## Goal

Prepare rebuttal data for two potential reviewer concerns:
1. "No large-model experiments" → gpt-4o-mini as a 4th backbone
2. "No popular benchmarks beyond current 6" → ALFWorld + ScienceWorld

Target: 6 → **8 environments**, 3 → **4 backbones**

Deliverables per environment:
- **Signal direction (ρ values)** — Step 1 signal discovery
- **EAAG vs competing baselines** — Step 2 core experiments

## Two New Environments

| Env | Adapter | Qwen3-4B | gpt-4o-mini Step 0 | Decision |
|-----|---------|----------|---------------------|----------|
| ALFWorld | ✅ | NO-GO (base=28%, Δ=2%) | **base=42%, always=36%, Δ=-6%** | **Proceed as Type I env (rollout-harmful, like Plancraft)** |
| ScienceWorld | ✅ | NO-GO (base=0%) | base=2% (too hard) | **Dropped** — tasks require domain knowledge + have instant-fail mechanics that break zero-shot LLM agents |

### SWE-bench Lite — Dropped

Dropped because HPC has no Docker (only Singularity, adaptation cost too high).
Other code-env alternatives checked:
- DS1000: Step 0 GO but Step 2 all SR=0% (bug)
- CRUXEval: only GO on Qwen3, NO-GO on Phi/Llama
- InterCode-Bash: NO-GO (base_sr=100%, too easy)

Two new envs + gpt-4o-mini signal discovery on existing 6 envs is sufficient for rebuttal.

## Pipeline per Environment

```
Step 0: GO/NO-GO precheck
  └─ 50 ep base_only + 50 ep always_trigger
  └─ GO if: base_sr ∈ [10%, 85%] AND Δ > 3pp

Step 1: Signal discovery
  └─ 200 ep always_trigger
  └─ Compute Spearman ρ for each signal × utility
  └─ Output: signal direction table (like Table 1 in paper)

Step 2: Core experiments (SLIM 7-METHOD VERSION)
  └─ 3 seeds × 200 ep per method = 21 total runs
  └─ Output: SR, Cost, Pareto comparison
```

### Slim 7-Method Plan (updated 2026-04-21)

Reduced from 12 methods to **7** after OpenRouter credits exhausted on 18-method run.

| # | Method | Category | Purpose |
|---|--------|----------|---------|
| 1 | `base_only` | bound | Lower bound (no rollout) |
| 2 | `always_trigger` | bound | Upper bound / Δ evidence |
| 3 | `scg_finetune_lr` (EAAG) | ours | Our method (L1 sparse logistic gate) |
| 4 | `cats` | CB | Platt-scaled confidence |
| 5 | `seag` | CB | Mean logprob confidence |
| 6 | `catts` | CB | K=5 vote-entropy + margin |
| 7 | `corefine` | CB | Entropy-triggered |

**Dropped** (already covered in paper or redundant):

| Method | Why dropped |
|--------|-------------|
| `oracle` | Cheap to add but not critical for rebuttal |
| `random_50` | Random baseline, no info beyond base/always |
| `best_sigma_wrong` | BSW ablation already done on Qwen3 |
| `auq` | Per-step extra LLM call, expensive + redundant |
| `s1_budget` | Weak baseline, paper has full results |

**Predictions (Type I / rollout-harmful env):**
- All 4 CBs should perform ≤ base_only (SR ≤ 42%) — fixed-direction failure
- EAAG should learn to suppress triggering, SR ≈ 42% at low cost
- always_trigger confirms rollout harms (SR = 36%)

**Estimated cost & time:**
- 7 methods × 3 seeds = 21 runs
- Per run: 200 ep × ~15-30s/ep = 1-2 hours
- **Total wall time**: 5-7h with concurrent 6 jobs
- **API cost**: $40-80

## Infrastructure

- **SLURM**: `general-gpu` partition, 12h max (general partition hangs — see log)
- **No vLLM needed** — all LLM calls go through OpenRouter API (GPU allocated but unused)
- **API key**: `OPENROUTER_API_KEY` (env var, existing key)
- **Cost estimate**: gpt-4o-mini ~$0.15/1M input, $0.60/1M output
- **Speed**: ~18s/episode (base_only), slower for always_trigger (rollout calls)

## Config Files

- `configs/rebuttal_alfworld_gpt4omini.yaml` ✅
- `configs/rebuttal_scienceworld_gpt4omini.yaml` ✅

## SLURM Scripts

- `scripts/rebuttal/run_rebuttal_step0.sbatch` ✅ (general-gpu, 12h, PYTHONUNBUFFERED=1)
- `scripts/rebuttal/run_rebuttal_step1.sbatch` ✅ (needs partition update before use)
- `scripts/rebuttal/run_rebuttal_step2.sbatch` ✅ (needs partition update before use)
- `scripts/rebuttal/run_rebuttal_cb.sbatch` ✅ (needs partition update before use)
- `scripts/rebuttal/submit_all.sh` ✅

## Results Directory

```
results/rebuttal/
├── alfworld/
│   ├── step0_go_nogo.json       ← pending (job 23948604)
│   ├── step1_signal_discovery/
│   └── step2_core/
└── scienceworld/
    └── ...
```

---

## Experiment Log

### 2026-04-21

**Status review after 4-day run:**

- **Step 1 (signal discovery): SUCCESS** — 200 ep, 7498 steps, all signals computed
  - `token_entropy`: ρ=**0.000**, p=1.0 (zero signal!)
  - `step_count`: ρ=+0.105, p<1e-19 (weak positive, significant)
  - `evidence_count`: ρ=+0.105 (duplicate of step_count)
  - `num_admissible`: ρ=-0.044, p=0.0001 (weak negative)
  - `action_type` (categorical): η²=0.111 (strongest signal)
  - `state_category` / `is_finish_proposed`: no signal
  - **Key finding**: token_entropy completely uninformative on ALFWorld+gpt-4o-mini,
    confirming Type I / weak-signal regime (analogous to Plancraft ρ=-0.016 on Qwen3)

- **Step 2 (core experiments): FAILED** — all 18 runs (6 methods × 3 seeds) produced
  empty directories. Root cause: **OpenRouter credits exhausted** during Step 1,
  all Step 2 API calls returned HTTP 402 Payment Required. Jobs ran to SLURM
  timeout without producing summary files.

- **CB (competing baselines): FAILED** — same cause as Step 2. No results.

**Decision**: Drop to **slim 7-method plan** (see top of this doc) to reduce API
cost by ~40%. Wait for OpenRouter top-up, then resubmit with consolidated sbatch
(7 methods × 3 seeds = 21 runs in a single array).

### 2026-04-17

**~17:00** — Full pipeline submitted for ALFWorld:
- **Step 1** (job 23980874): 200 ep always_trigger → signal discovery (ρ values)
- **Step 2** (job 23980876, depends on 23980874): 6 methods × 3 seeds = 18 runs
  - Methods: base_only, always_trigger, random_50, best_sigma_wrong, scg_finetune_lr (EAAG), oracle
- **CB** (job 23980877, depends on 23980874): 6 CBs × 3 seeds = 18 runs
  - Methods: catts, seag, corefine, cats, auq, s1_budget
- **Hypothesis**: ALFWorld+gpt-4o-mini is Type I (rollout-harmful, like Plancraft).
  Fixed-direction baselines should perform ≤ base_only (SR=42%). EAAG should learn
  to suppress triggering, matching base_only at low cost.

**~16:45** — **Step 0 results received**:
- **ALFWorld**: base=42%, always=36%, Δ=-6% → formal NO-GO but informative (rollout-harmful pattern)
- **ScienceWorld**: base=2%, always=2%, Δ=0% → NO-GO (too hard for gpt-4o-mini zero-shot)

**~16:30** — ScienceWorld adapter improvements (did not help enough):
- Filtered out `connect`/`disconnect` low-level actions (303 → 134 actions)
- Added ScienceWorld environment description + common-action patterns to prompt
- Exposed `get_goal_progress()` sub-goals in prompt
- Result: 5 ep test still got 0% SR (agent hits instant-fail mechanics like wrong `focus on`)
- Diagnosis: ScienceWorld's instant-fail design + required domain knowledge makes it
  fundamentally hard for zero-shot LLM agents (not a prompt-only issue)

**~15:00** — Step 0 submitted: **job 23948604** (array 0-1) — `general-gpu`, 12h
- Switched to `general-gpu` partition: `general` partition compute nodes hang during init
- Added `module load cuda/12.3` to match working phase6 OpenRouter scripts
- Previous OpenRouter experiments (phase6 SE methods) all ran successfully on GPU nodes
- Login node test confirmed pipeline works: 5 ep base_only completed in 1.5 min, **SR=60%**, 1091 API calls all 200 OK

**~14:40** — Login node end-to-end test: **SUCCESS**
- `python -u experiments/p5_new_env_experiments.py --step 0 --env alfworld --episodes 5`
- ALFWorld: init 341 games in <1s, OpenRouter client OK, episodes running normally
- base_only: 5/5 episodes done (18s/ep avg), SR=60%, then always_trigger started
- No dead loops, tqdm progressing normally, 1091 API calls in 10 min all HTTP 200
- Timed out at 10 min (tool limit), but pipeline fully validated

**~14:20** — Jobs 23948027, 23948231 on `general` partition: **HUNG**
- Both envs initialized successfully (ALFWorld 341 games, ScienceWorld 30 tasks)
- OpenRouter client created OK
- But no API calls made — processes hung after init on cn497
- `PYTHONUNBUFFERED=1` confirmed logs were truly frozen, not just buffered
- Network test: `curl https://openrouter.ai` from general node returned HTTP 200
- Conclusion: `general` partition nodes have some env issue; switch to `general-gpu`

**~14:10** — Job 23947898: crashed on `openai.OpenAI` — **FIXED**
- `openai` package broken (no `OpenAI` class), reinstalled v2.32.0
- Also reinstalled `pyyaml` (yaml.safe_load missing)

**~14:00** — Job 23947681: crashed on `import torch` — **FIXED**
- `experiments/p2_gate_learning.py` directly imported `SCG_MLP` → torch crash
- Fixed: wrapped in try/except in p2, p3, p2_5, p2_scg scripts

**~13:40** — Job 23947197: ALFWorld in STUB mode — **FIXED**
- `fast_downward`, `tqdm`, `termcolor` packages broken by Python reinstall
- Fixed: `pip install --force-reinstall alfworld` (restores all deps)

**13:32** — First submission: **job 23946849** — FAILED
- `matplotlib` circular import → `scipy.stats` missing → `PIL` missing
- Root cause: `conda install python=3.10 --force-reinstall` deleted `.py` files from site-packages

**All code fixes applied:**

| File | Fix | Why |
|------|-----|-----|
| `frvc/utils.py` | matplotlib/seaborn → lazy import | Not needed for experiments |
| `frvc/__init__.py` | SCG_MLP, HFInference → try/except | Torch not needed for OpenRouter |
| `experiments/p2_gate_learning.py` | SCG_MLP import → try/except | Same |
| `experiments/p3_core_experiments.py` | SCG_MLP import → try/except | Same |
| `experiments/p2_5_reviewer_supplement.py` | SCG_MLP import → try/except | Same |
| `experiments/p2_scg_gated_agent.py` | SCG_MLP import → try/except | Same |
| `scienceworld_env.py` | Added `_episode_count` for task cycling | Support all 30 tasks |
| conda env | Reinstalled: python, scipy, openai, pyyaml, alfworld, tqdm, termcolor, pillow, typing_extensions | Restore broken packages |

---

## Detailed Status

### 1. ALFWorld (gpt-4o-mini) — ACTIVE

- [x] Adapter: `frvc/envs/alfworld_env.py`
- [x] Config: `configs/rebuttal_alfworld_gpt4omini.yaml`
- [x] **Step 0**: base=42%, always=36%, **Δ=-6%** (rollout-harmful / Type I)
- [x] **Step 1**: Signal discovery complete (200 ep, token_entropy ρ=0.000)
- [ ] **Step 2 (SLIM)**: 7 methods × 3 seeds = 21 runs — **pending OpenRouter top-up**
- [ ] Analysis: ρ table + Pareto plot + comparison to Plancraft (same Type I pattern)

**Framing for paper**: ALFWorld+gpt-4o-mini is a new Type I / rollout-harmful
instance, analogous to Plancraft. Step 1 confirms weak/zero entropy signal.
Predicts: fixed-direction CBs fail (SR ≤ base), EAAG correctly suppresses
triggering (SR ≈ base, low cost).

### 2. ScienceWorld (gpt-4o-mini) — DROPPED

- [x] Step 0: base=2%, always=2%, Δ=0% → NO-GO
- **Reason**: ScienceWorld's instant-fail mechanics (wrong `focus on` → -100 done)
  combined with required domain knowledge and 200-400 action spaces make it
  fundamentally unsuited for zero-shot LLM agents. Adapter improvements did not help.

### 3. gpt-4o-mini Signal Discovery on Existing 6 Envs (future)

Not yet started. Low cost — only need ρ values, no full EAAG pipeline.
Can reuse existing configs with `api_type: "openrouter"` + `model_name: "openai/gpt-4o-mini"`.
Will produce a row in Table 1 (signal-discovery table) for the 4th backbone.

---

## Next Steps

1. **Top up OpenRouter credits** (~$80 should cover slim plan + headroom)

2. **Create slim sbatch** (`scripts/rebuttal/run_rebuttal_slim.sbatch`)
   - 7 methods × 3 seeds = 21-task array (`--array=0-20%6`)
   - Methods: `base_only always_trigger scg_finetune_lr cats seag catts corefine`
   - Array mapping: `method_idx = IDX / 3`, `seed_idx = IDX % 3`
   - Route 4 CB methods through `p5_competing_baselines.py`,
     3 core methods through `p5_new_env_experiments.py`

3. **Submit and monitor**
   ```bash
   sbatch scripts/rebuttal/run_rebuttal_slim.sbatch
   # Monitor
   squeue -u $USER
   ls results/rebuttal/alfworld/alfworld/*/seed_*/summary.json
   ```

4. **Aggregate results** when all 21 runs done
   ```bash
   python -c "... aggregate SR + cost per method ..."
   ```

5. **gpt-4o-mini signal discovery on existing 6 envs** (future, independent)

## Lessons Learned

- `conda install python --force-reinstall` deletes `.py` files from site-packages → cascading import failures
- `general` partition compute nodes can hang during Python init; `general-gpu` nodes work reliably
- Always use `PYTHONUNBUFFERED=1` and `python -u` for SLURM jobs to get real-time logs
- Test full pipeline on login node before submitting SLURM jobs
