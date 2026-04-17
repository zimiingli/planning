# Rebuttal Preparation: New Benchmark Experiments

> Created: 2026-04-17
> Last updated: 2026-04-17 15:00 EDT
> Status: **Step 0 running** (job 23948604, `general-gpu`, 12h)
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

| Env | Adapter | Previous GO/NO-GO (Qwen3-4B) | gpt-4o-mini preliminary | Status |
|-----|---------|------------------------------|------------------------|--------|
| ALFWorld | ✅ exists | NO-GO (base=28%, Δ=2%) | **base_sr=60% (5ep test)** | Step 0 running |
| ScienceWorld | ✅ exists | NO-GO (base=0%, always=0%) | TBD | Step 0 running |

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

Step 1: Signal discovery (only if GO)
  └─ 200 ep always_trigger
  └─ Compute Spearman ρ for each signal × utility
  └─ Output: signal direction table (like Table 1 in paper)

Step 2: Core experiments (only if GO)
  └─ Methods: base_only, always_trigger, random_50, best_sigma_wrong,
              scg_finetune_lr, oracle, + competing baselines (CaTS, SEAG,
              CoRefine, CATTS, AUQ, s1_budget)
  └─ 3 seeds × 200 ep per method
  └─ Output: SR, Cost, Pareto comparison
```

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

### 2026-04-17

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

### 1. ALFWorld (gpt-4o-mini)

- [x] Adapter: `frvc/envs/alfworld_env.py`
- [x] Registry: registered as "alfworld"
- [x] Config: `configs/rebuttal_alfworld_gpt4omini.yaml`
- [x] Login node test: base_sr=60% (5ep), pipeline works
- [ ] **Step 0: GO/NO-GO** — running (job 23948604_0, general-gpu)
- [ ] Step 1: Signal discovery
- [ ] Step 2: Core experiments (6 methods × 3 seeds × 200 ep)
- [ ] Step 2b: Competing baselines (6 CB × 3 seeds × 200 ep)
- [ ] Analysis: ρ table + Pareto plot

Previous Qwen3-4B: base_sr=28%, always_sr=30%, Δ=2% → NO-GO
gpt-4o-mini test: **base_sr=60%** (5 ep) → very likely GO

### 2. ScienceWorld (gpt-4o-mini)

- [x] Adapter: `frvc/envs/scienceworld_env.py` (updated: task cycling)
- [x] Registry: registered as "scienceworld"
- [x] Config: `configs/rebuttal_scienceworld_gpt4omini.yaml`
- [ ] **Step 0: GO/NO-GO** — running (job 23948604_1, general-gpu)
- [ ] Step 1: Signal discovery
- [ ] Step 2: Core experiments (6 methods × 3 seeds × 200 ep)
- [ ] Step 2b: Competing baselines (6 CB × 3 seeds × 200 ep)
- [ ] Analysis: ρ table + Pareto plot

Previous Qwen3-4B: base_sr=0%, always_sr=0% → NO-GO (model too weak)
Config: `task_name: null` — cycles all 30 tasks across episodes

### 3. gpt-4o-mini Signal Discovery on Existing 6 Envs (future)

Not yet started. Low cost — only need ρ values, no full EAAG pipeline.
Can reuse existing configs with `api_type: "openrouter"` + `model_name: "openai/gpt-4o-mini"`.
Will produce a row in Table 1 (signal-discovery table) for the 4th backbone.

---

## Next Steps

1. **Wait for Step 0 results** (job 23948604, est. 1-3 hours)
   ```bash
   squeue -u $USER
   cat results/rebuttal/alfworld/alfworld/step0_go_nogo.json
   cat results/rebuttal/scienceworld/scienceworld/step0_go_nogo.json
   ```

2. **If GO**: update Step 1/2/CB scripts to `general-gpu` partition, then submit
   ```bash
   JOB1=$(sbatch --parsable scripts/rebuttal/run_rebuttal_step1.sbatch)
   sbatch --dependency=afterok:${JOB1} scripts/rebuttal/run_rebuttal_step2.sbatch
   sbatch --dependency=afterok:${JOB1} scripts/rebuttal/run_rebuttal_cb.sbatch
   ```

3. **If NO-GO for ScienceWorld**: investigate task selection, try easier subset

## Lessons Learned

- `conda install python --force-reinstall` deletes `.py` files from site-packages → cascading import failures
- `general` partition compute nodes can hang during Python init; `general-gpu` nodes work reliably
- Always use `PYTHONUNBUFFERED=1` and `python -u` for SLURM jobs to get real-time logs
- Test full pipeline on login node before submitting SLURM jobs
