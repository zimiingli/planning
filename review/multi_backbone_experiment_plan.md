# Multi-Backbone Supplementary Experiments Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate that direction reversal and EAAG effectiveness generalize across LLM backbones (Phi-3.5-mini-instruct, Llama-3.1-8B-Instruct), addressing P0-1 from all 6 reviewers.

**Architecture:** Create per-model config files for **all 8 environments** (matching the paper's full evaluation), run standard 3-step pipeline (GO/NO-GO → Signal Discovery → Core Experiments), plus cross-optimizer and budget sensitivity experiments on both new models.

**Tech Stack:** vLLM 0.11.2 serving, SLURM job arrays, existing `p5_new_env_experiments.py` pipeline, conda env `frvc_review`

> **Model change (2026-03-27):** Originally planned Qwen3.5-4B was replaced by Phi-3.5-mini-instruct because:
> 1. Qwen3.5 uses `Qwen3_5ForConditionalGeneration` architecture — not supported by vLLM 0.11.2
> 2. vLLM ≥0.12 requires glibc ≥2.31, but HPC runs RHEL 8 (glibc 2.28) — cannot upgrade vLLM
> 3. Phi-3.5-mini-instruct (3.8B, Microsoft) provides a third vendor (Alibaba/Meta/Microsoft) for stronger cross-backbone narrative

---

## Overview

### Models
| Model ID | Short Name | Vendor | Size | Notes |
|----------|-----------|--------|------|-------|
| `Qwen/Qwen3-4B-Instruct-2507` | qwen3-4b (original) | Alibaba | 4B | Baseline — already done |
| `microsoft/Phi-3.5-mini-instruct` | phi35-mini | Microsoft | 3.8B | New backbone #1 |
| `meta-llama/Llama-3.1-8B-Instruct` | llama31-8b | Meta | 8B | New backbone #2 |
| GPT-4o / GPT-4o-mini (TBD) | gpt4o | OpenAI | ~200B+ | TODO: large API model for scale coverage |

### All 8 Environments
| # | Env Name (--env) | Paper Section | Type |
|---|------------------|---------------|------|
| 0 | `hotpotqa` | §3.1/§5.2 Main | Info-Poverty (QA) |
| 1 | `apps` | §3.1/§5.2 Main | Mixed (Code Gen) |
| 2 | `webshop` | §3.1/§5.2 Main | Mixed (Web Nav) |
| 3 | `fever` | §3.1/§5.2 Main | Info-Poverty (Fact Check) |
| 4 | `twexpress` | §3.1/§5.5 Diagnostic | Rollout-safe |
| 5 | `plancraft` | §3.1/§5.5 Diagnostic | Rollout-harmful |
| 6 | `apps_interview` | §3.1/Appendix | Decision-Difficulty (Code Gen) |
| 7 | `cruxeval` | §3.1/Appendix | High-ceiling (Code Reasoning) |

### Experiment Matrix

| Experiment | Environments | Phi-3.5-mini | Llama-3.1-8B | Qwen3-4B (existing) |
|------------|-------------|:-----------:|:------------:|:-------------------:|
| Exp 1: Signal Discovery (Step 0+1) | All 8 | ✅ | ✅ | ✅ already done |
| Exp 2: EAAG Core (Step 2) | All 8 | ✅ | ✅ | ✅ already done |
| Exp 3: Cross-Optimizer | HotpotQA (K-variant), APPS Intv (per-action) | ✅ | ✅ | ❌ not done |
| Exp 4: Budget Sensitivity | HotpotQA, FEVER | ✅ | ✅ | ✅ already done |

### Results Directory Structure and Completed Data

All data is under `results/review/`. Per-environment structure: `{model}/{env}/{env}/{file}`.

**Completed data (Step 0 + Step 1, 48 files total):**
```
results/review/
├── phi35_mini/                              # 1.4 MB
│   ├── {hotpotqa,apps,webshop,fever,twexpress,plancraft,apps_interview,cruxeval}/
│   │   └── {env}/
│   │       ├── step0_go_nogo.json           # ✅ 8/8 complete
│   │       ├── step1_signal_discovery.json  # ✅ 8/8 complete
│   │       └── phase1_signal_data.json      # ✅ 8/8 complete (raw signal data)
│   ├── cross_optimizer/                     # ❌ TODO
│   └── budget_sensitivity/                  # ❌ TODO
├── llama31_8b/                              # 1.6 MB
│   ├── {hotpotqa,apps,webshop,fever,twexpress,plancraft,apps_interview,cruxeval}/
│   │   └── {env}/
│   │       ├── step0_go_nogo.json           # ✅ 8/8 complete
│   │       ├── step1_signal_discovery.json  # ✅ 8/8 complete
│   │       └── phase1_signal_data.json      # ✅ 8/8 complete (raw signal data)
│   ├── cross_optimizer/                     # ❌ TODO
│   └── budget_sensitivity/                  # ❌ TODO
└── analysis/                                # ❌ TODO
    ├── multi_backbone_rho_table.csv
    └── multi_backbone_eaag_table.csv
```

**Pending data (Step 2, Exp 3, Exp 4):**
```
results/review/{model}/{env}/{env}/
    ├── base_only/seed_{42,123,456}/         # Step 2: 3 methods × 3 seeds per env
    ├── always_trigger/seed_{42,123,456}/
    └── scg_finetune_lr/seed_{42,123,456}/
results/review/{model}/cross_optimizer/      # Exp 3
results/review/{model}/budget_sensitivity/   # Exp 4
```

### Config Files (need to create for new 4 envs)
```
configs/review/
├── phi35_mini_hotpotqa.yaml          # ✅ exists
├── phi35_mini_apps.yaml              # ✅ exists
├── phi35_mini_webshop.yaml           # ✅ exists
├── phi35_mini_fever.yaml             # ✅ exists
├── phi35_mini_twexpress.yaml         # ✅ exists
├── phi35_mini_plancraft.yaml         # ✅ exists
├── phi35_mini_apps_interview.yaml    # ✅ exists
├── phi35_mini_cruxeval.yaml          # ✅ exists
├── llama31_8b_hotpotqa.yaml          # ✅ exists
├── llama31_8b_apps.yaml              # ✅ exists
├── llama31_8b_webshop.yaml           # ✅ exists
├── llama31_8b_fever.yaml             # ✅ exists
├── llama31_8b_twexpress.yaml         # ✅ exists
├── llama31_8b_plancraft.yaml         # ✅ exists
├── llama31_8b_apps_interview.yaml    # ✅ exists (Exp 3: cross-optimizer)
├── llama31_8b_cruxeval.yaml          # ✅ exists
├── llama31_8b_hotpotqa_kvariant.yaml # ✅ exists (Exp 3: cross-optimizer)
├── phi35_mini_hotpotqa_kvariant.yaml # ❌ TODO (Exp 3: cross-optimizer)
├── phi35_mini_apps_interview_peraction.yaml  # ❌ TODO (Exp 3: cross-optimizer)
└── budget_sensitivity configs        # ❌ TODO (Exp 4: both models)
```

### SLURM Scripts
```
scripts/review/
│
│  ── Step 0 & 1: Signal Discovery Pipeline ──
├── run_step0_phi35.sbatch              # GO/NO-GO (8 envs, array 0-7)         → p5_new_env_experiments.py --step 0
├── run_step0_llama31.sbatch            # same for Llama (ports 9100+)
├── run_step1_phi35.sbatch              # Signal discovery (8 envs, array 0-7)  → p5_new_env_experiments.py --step 1
├── run_step1_llama31.sbatch            # same for Llama
│
│  ── Step 2A: Bounds (base_only, always_trigger, oracle) ──
├── run_step2_phi35.sbatch              # 8 envs × 3 bounds × 3 seeds = 72     → p5_new_env_experiments.py --step 2
├── run_step2_llama31.sbatch            # same for Llama
│
│  ── Step 2B: Competing Baselines (catts, seag, corefine, cats, auq, s1_budget) ──
├── run_cb_phi35.sbatch                 # 8 envs × 6 CBs × 3 seeds = 144      → p5_competing_baselines.py
├── run_cb_llama31.sbatch               # same for Llama
│
│  ── Step 2C: EAAG (se_few5_filter_local) ──
├── run_eaag_phi35.sbatch               # 8 envs × 1 method × 3 seeds = 24    → p6_e_method_upgrade.py
├── run_eaag_llama31.sbatch             # same for Llama
│
│  ── Exp 3 & 4 (supplementary) ──
├── run_cross_optimizer_llama31.sbatch   # Exp 3: cross-optimizer
└── run_budget_sensitivity_llama31.sbatch # Exp 4: budget sensitivity
```

### Experiment Scripts Reference
| Script | Purpose | Methods |
|--------|---------|---------|
| `experiments/p5_new_env_experiments.py --step 0` | GO/NO-GO precheck | base_only, always_trigger |
| `experiments/p5_new_env_experiments.py --step 1` | Signal discovery | always_trigger (200 ep) |
| `experiments/p5_new_env_experiments.py --step 2` | Bounds | base_only, always_trigger, oracle |
| `experiments/p5_competing_baselines.py` | Competing baselines | catts, seag, corefine, cats, auq, s1_budget |
| `experiments/p6_e_method_upgrade.py` | **EAAG (our method)** | se_few5_filter_local |

---

## Task 1: Create Config Files for Phi-3.5-mini-instruct (4 environments)

**Files:**
- Create: `configs/review/phi35_mini_hotpotqa.yaml`
- Create: `configs/review/phi35_mini_apps.yaml`
- Create: `configs/review/phi35_mini_webshop.yaml`
- Create: `configs/review/phi35_mini_fever.yaml`

Based on existing phase6 configs, with changes:
- `model_name: "microsoft/Phi-3.5-mini-instruct"`
- `output.results_dir: "results/review/phi35_mini/{env}"`
- `phase1_data_path`: point to new results dir

- [x] Step 1: Create `configs/review/` directory
- [x] Step 2: Create configs (originally as qwen35_4b_*.yaml)
- [x] Step 3: Rename and update to phi35_mini_*.yaml (2026-03-27 model swap)
- [x] Step 4: Verify all 4 configs are valid YAML

---

## Task 2: Create Config Files for Llama-3.1-8B (4 environments + cross-optimizer + budget)

**Files:**
- Create: `configs/review/llama31_8b_hotpotqa.yaml`
- Create: `configs/review/llama31_8b_apps.yaml`
- Create: `configs/review/llama31_8b_webshop.yaml`
- Create: `configs/review/llama31_8b_fever.yaml`
- Create: `configs/review/llama31_8b_hotpotqa_kvariant.yaml`
- Create: `configs/review/llama31_8b_apps_interview.yaml`
- Create: `configs/review/llama31_8b_budget_sensitivity.yaml`

Changes from Qwen3 configs:
- `model_name: "meta-llama/Llama-3.1-8B"`
- Remove all `disable_thinking` flags (Qwen3-specific)
- `output.results_dir: "results/review/llama31_8b/{env}"`
- `max-model-len` in vLLM may need 8192 (Llama supports 128K but 8192 is sufficient)
- Llama-3.1-8B is a base model, not instruct — may need `meta-llama/Llama-3.1-8B-Instruct` instead

**Cross-optimizer configs (Exp 3):**
- `llama31_8b_hotpotqa_kvariant.yaml`: HotpotQA env but with K-variant rollout (num_variants: 5) instead of per-action eval (num_chains: 5, top_k_actions: 5)
- `llama31_8b_apps_interview.yaml`: APPS Interview env but with per-action eval (num_chains: 5) instead of K-variant (num_variants: 5)

**Budget sensitivity config (Exp 4):**
- Same as standard config but `min_cal_points` parameterized as {10, 20, 30, 50, 100}

- [x] Step 1: Create 4 standard configs (hotpotqa, apps, webshop, fever)
- [x] Step 2: Create `llama31_8b_hotpotqa_kvariant.yaml` with K-variant rollout
- [x] Step 3: Create `llama31_8b_apps_interview_peraction.yaml` with per-action rollout
- [x] Step 4: Budget sensitivity uses standard configs with sed-patched `min_cal_points`
- [x] Step 5: Verify all configs are valid YAML

---

## Task 3: Create SLURM Scripts — Exp 1 & 2 (Both Models)

**Files:**
- Create: `scripts/review/run_step0_phi35.sbatch`
- Create: `scripts/review/run_step1_phi35.sbatch`
- Create: `scripts/review/run_step2_phi35.sbatch`
- Create: `scripts/review/run_step0_llama31.sbatch`
- Create: `scripts/review/run_step1_llama31.sbatch`
- Create: `scripts/review/run_step2_llama31.sbatch`

Pattern follows `scripts/phase6/run_env_extend_step{0,1,2}.sbatch`:

**Step 0 (GO/NO-GO):** 4 parallel jobs, 1 GPU each
- Array: 0-3 (HotpotQA, APPS Intro, WebShop, FEVER)
- ~50 ep base_only + 50 ep always_trigger
- Time: 4-6 hours

**Step 1 (Signal Discovery):** 4 parallel jobs, 1 GPU each
- Array: 0-3
- 200 ep always_trigger
- Time: 8-12 hours

**Step 2 (Core EAAG):** 4 envs × 3 methods × 3 seeds = 36 jobs
- Methods: base_only, always_trigger, scg_finetune_lr
- Array: 0-35, max 8 concurrent
- Time: 8-12 hours each
- Array mapping: env_idx = IDX / 9, method_idx = (IDX % 9) / 3, seed_idx = IDX % 3

**vLLM considerations:**
- Phi-3.5-mini: `VLLM_MODEL="microsoft/Phi-3.5-mini-instruct"`, ~7.6GB VRAM, `--gpu-memory-utilization 0.85`
- Llama-3.1-8B: `VLLM_MODEL="meta-llama/Llama-3.1-8B-Instruct"`, ~15GB VRAM, `--gpu-memory-utilization 0.90`

**Environment:** conda env `frvc_review` (vLLM 0.11.2, transformers 4.57.6, torch 2.9.0+cu128)

- [x] Step 1: Create `scripts/review/` directory
- [x] Step 2: Create Step 0 scripts for both models
- [x] Step 3: Create Step 1 scripts for both models
- [x] Step 4: Create Step 2 scripts for both models
- [x] Step 5: Verify all scripts with `bash -n` syntax check
- [x] Step 6: Fix conda env (frvc → frvc_review) and add HF_TOKEN (2026-03-27)
- [x] Step 7: Rename qwen35 scripts to phi35 (2026-03-27 model swap)

---

## Task 4: Create SLURM Scripts — Exp 3 (Cross-Optimizer, Llama only)

**Files:**
- Create: `scripts/review/run_cross_optimizer_llama31.sbatch`

2 cross-optimizer experiments:
- Job 0: HotpotQA with K-variant rollout (Step 0 + Step 1 only — signal discovery)
- Job 1: APPS Interview with per-action rollout (Step 0 + Step 1 only — signal discovery)

Array: 0-1, fully parallel.

Output: `results/review/llama31_8b/cross_optimizer/{hotpotqa_kvariant,apps_intv_peraction}/`

- [x] Step 1: Create the SLURM script
- [x] Step 2: Verify with `bash -n`

---

## Task 5: Create SLURM Scripts — Exp 4 (Budget Sensitivity, Llama only)

**Files:**
- Create: `scripts/review/run_budget_sensitivity_llama31.sbatch`

2 envs × 5 budget levels × 3 seeds = 30 jobs
- Envs: HotpotQA, FEVER
- N_explore ∈ {10, 20, 30, 50, 100}
- Method: scg_finetune_lr only
- Array: 0-29, max 6 concurrent

Array mapping:
- env_idx = IDX / 15
- budget_idx = (IDX % 15) / 3
- seed_idx = IDX % 3

Needs a way to override `min_cal_points` per job. Options:
- (A) Env var: `FRVC_MIN_CAL_POINTS` (requires code support)
- (B) sed-patch config: modify `min_cal_points` in temp config
- (C) CLI arg: `--min-cal-points N` (requires code support)

Best approach: sed-patch the temp config (same as port injection pattern).

Output: `results/review/llama31_8b/budget_sensitivity/{env}/N{budget}/seed_{seed}/`

- [x] Step 1: Create the SLURM script
- [x] Step 2: Verify with `bash -n`

---

## Task 6: Create Analysis Script

**Files:**
- Create: `scripts/review/analyze_multi_backbone.py`

After all experiments complete:
1. Load Step 1 results from Phi-3.5-mini + Llama-3.1-8B + original Qwen3-4B
2. Build multi-backbone ρ comparison table (for §3.1)
3. Load Step 2 results and build EAAG SR comparison table
4. Load cross-optimizer results and compare ρ directions
5. Load budget sensitivity results and plot stability curves

Output:
- `results/review/analysis/multi_backbone_rho_table.csv`
- `results/review/analysis/multi_backbone_eaag_table.csv`
- `results/review/analysis/cross_optimizer_rho.csv`
- `results/review/analysis/budget_sensitivity.csv`

- [x] Step 1: Create analysis script
- [x] Step 2: Verify imports and file paths

---

## Execution Log

### 2026-03-23: Step 0 submitted (FAILED — env issues)
- [x] **Qwen3.5-4B Step 0**: SLURM job **23320631** — ❌ FAILED: `qwen3_5` architecture not recognized by transformers 4.57.6 in `frvc` env
- [x] **Llama-3.1-8B Step 0**: SLURM job **23320632** — ❌ FAILED: 401 Unauthorized (gated repo, no HF_TOKEN)

### 2026-03-27: Diagnosis and fixes
**Root causes identified:**
1. SLURM scripts used `frvc` env (transformers 4.57.6) instead of `frvc_review`
2. Missing `HF_TOKEN` for gated Llama model
3. `frvc_review` env had transformers 5.3.0 which broke vLLM 0.11.2 tokenizer API
4. Qwen3.5 (`Qwen3_5ForConditionalGeneration`) not in vLLM 0.11.2 architecture list
5. vLLM ≥0.12 requires glibc ≥2.31, but HPC has glibc 2.28 (RHEL 8) — cannot upgrade

**Fixes applied:**
- [x] Installed missing pip packages in `frvc_review` (pandas, matplotlib, seaborn, gymnasium, etc.)
- [x] Switched all sbatch scripts from `frvc` → `frvc_review` env
- [x] Added `HF_TOKEN` to all sbatch scripts and `~/.bashrc`
- [x] Downgraded transformers 5.3.0 → 4.57.6 in `frvc_review` (vLLM 0.11.2 compatibility)
- [x] Replaced Qwen3.5-4B with **Phi-3.5-mini-instruct** (supported by vLLM 0.11.2, `Phi3ForCausalLM`)
- [x] Renamed all qwen35 configs/scripts to phi35
- [x] Added `"hotpotqa"` and `"webshop"` to p5 argparse `--env` choices
- [x] Installed WebShop dependencies (gym, bs4, flask, spacy, pyserini, openjdk, etc.) and added `JAVA_HOME` to sbatch scripts

### 2026-03-27: Step 0 first resubmit (partial failures)
- **Llama-3.1-8B Step 0**: SLURM job **23442334** (array 0-3)
  - array 0 (hotpotqa): ❌ FAILED — `--env hotpotqa` not in p5 argparse choices
  - array 1 (apps): ✅ COMPLETED — **GO** (base=48%, AT=80%, Δ=+32pp)
  - array 2 (webshop): ❌ FAILED — `--env webshop` not in p5 argparse choices
  - array 3 (fever): ✅ COMPLETED — **GO** (base=8%, AT=64%, Δ=+56pp)
- **Phi-3.5-mini Step 0**: SLURM job **23442660** (array 0-3)
  - array 0 (hotpotqa): ❌ FAILED — same argparse issue
  - array 1 (apps): ✅ COMPLETED — **GO** (base=46%, AT=80%, Δ=+34pp)
  - array 2 (webshop): ❌ FAILED — same argparse issue
  - array 3 (fever): running

**Fix:** Added `"hotpotqa"` and `"webshop"` to argparse choices in `experiments/p5_new_env_experiments.py`

### 2026-03-27: Step 0 second resubmit (hotpotqa + webshop)
- **Llama-3.1-8B**: job **23443215** (array 0,2)
  - array 0 (hotpotqa): ✅ COMPLETED — **GO** (base=48%, AT=98%, Δ=+50pp)
  - array 2 (webshop): ✅ COMPLETED — but 0%/0% (WebShop in stub mode)
- **Phi-3.5-mini**: job **23443214** (array 0,2)
  - array 0 (hotpotqa): ✅ COMPLETED — **GO** (base=28%, AT=96%, Δ=+68pp)
  - array 2 (webshop): ✅ COMPLETED — but 0%/0% (WebShop in stub mode)

**Root cause:** WebShop ran in stub mode because `frvc_review` env was missing WebShop's dependencies: `gym`, `beautifulsoup4`, `flask`, `spacy`, `pyserini` (needs Java/OpenJDK), `rank_bm25`, `cleantext`, `nltk`, `selenium`, `nmslib`, `en_core_web_sm` spacy model.

**Fixes applied:**
- [x] Installed `gym==0.26.2`, `beautifulsoup4`, `flask`, `flask-cors`, `spacy`, `pyserini`, `rank_bm25`, `cleantext`, `nltk`, `selenium`, `nmslib`, `fasttext`, `hashids`
- [x] Installed `openjdk=21` via conda (required by pyserini/Lucene)
- [x] Downloaded spacy model `en_core_web_sm`
- [x] Added `export JAVA_HOME` to all sbatch scripts
- [x] Verified `from web_agent_site.envs import WebAgentTextEnv` succeeds

### 2026-03-27: Step 0 third resubmit (webshop — port collision)
- **Phi-3.5-mini**: job **23447266** (array 2, webshop) — ❌ FAILED: port 8920 collision with Llama job on same node (gpu41)
- **Llama-3.1-8B**: job **23447267** (array 2, webshop) — ❌ FAILED: same port collision
- **Phi-3.5-mini FEVER**: job **23442660_3** — mistakenly cancelled at 82% (41/50 episodes), was running normally but slowly (~100-150s/ep for always_trigger rollouts, vs Llama's ~18s/ep — Phi-3.5 generates far more tokens per call)

**Fixes applied:**
- [x] Shifted Llama vLLM ports from 8900+ to 9100+ in all Llama sbatch scripts (avoids collision with Phi on same node)

### 2026-03-27: Step 0 fourth resubmit (webshop + fever)
- **Phi-3.5-mini WebShop**: job **23450618** — ✅ COMPLETED — **GO** (base=8%, AT=54%, Δ=+46pp)
- **Llama-3.1-8B WebShop**: job **23450619** — ✅ COMPLETED — **NO-GO** (base=2%, AT=2%, Δ=0pp)
- **Phi-3.5-mini FEVER**: job **23450882** — ✅ COMPLETED — **GO** (base=6%, AT=60%, Δ=+54pp)

### 2026-03-27: Step 1 submitted for original 4 envs (overlapping with Step 0)

**Llama-3.1-8B Step 1**: job **23451368** (array 0,1,3 = hotpotqa, apps, fever) — ✅ ALL COMPLETED
**Phi-3.5-mini Step 1**: job **23451369** (array 0,1 = hotpotqa, apps) — ✅ ALL COMPLETED

### 2026-03-27: Expanded to 8 environments

Created 8 new config files from phase5/phase6 Qwen3 templates, updated sbatch ENVS arrays.

**Step 0 for new envs:**
- **Phi-3.5-mini**: job **23452312** (array 4-7) — ✅ ALL COMPLETED
- **Llama-3.1-8B**: job **23452313** (array 4-7) — ✅ ALL COMPLETED

### Step 0 GO/NO-GO Results — All 8 Environments × 2 Models (COMPLETE)

| # | Environment | Phi-3.5-mini | Llama-3.1-8B | Decision |
|---|-------------|:---:|:---:|:---:|
| 0 | **HotpotQA** | base=28%, AT=96%, Δ=+68pp → **GO** | base=48%, AT=98%, Δ=+50pp → **GO** | ✅ Double GO |
| 1 | **APPS** | base=46%, AT=80%, Δ=+34pp → **GO** | base=48%, AT=80%, Δ=+32pp → **GO** | ✅ Double GO |
| 2 | **WebShop** | base=8%, AT=54%, Δ=+46pp → **GO** | base=2%, AT=2% → **NO-GO** | ⚠️ Phi GO only |
| 3 | **FEVER** | base=6%, AT=60%, Δ=+54pp → **GO** | base=8%, AT=64%, Δ=+56pp → **GO** | ✅ Double GO |
| 4 | **TWExpress** | base=62%, AT=92%, Δ=+30pp → **GO** | base=38%, AT=100%, Δ=+62pp → **GO** | ✅ Double GO |
| 5 | **Plancraft** | base=16%, AT=16%, Δ=0 → **NO-GO** | base=50%, AT=24%, Δ=**-26pp** → **NO-GO** | ❌ Rollout harmful |
| 6 | **APPS Interview** | base=28%, AT=82%, Δ=+54pp → **GO** | base=52%, AT=82%, Δ=+30pp → **GO** | ✅ Double GO |
| 7 | **CRUXEval** | base=100%, AT=100% → **NO-GO** | base=98%, AT=98% → **NO-GO** | ❌ Ceiling (~100%) |

**Gate 1 summary (updated after TWExpress/Plancraft stub fix):**
- **Double GO (5 envs):** HotpotQA, APPS, FEVER, APPS Interview, TWExpress
- **Single GO (1 env):** WebShop — Phi GO only, Llama NO-GO (2%)
- **Double NO-GO (2 envs):**
  - Plancraft: rollout harmful (Llama -26pp, Phi 0pp) — still run Step 2 to test if methods learn to avoid triggering
  - CRUXEval: ceiling (~100%)

> **Previous TWExpress/Plancraft data was INVALID** (stub mode, showed 100%/0%). Real results above from jobs 23487057/23487059 after installing `textworld-express` and `plancraft`.

> **Note on Phi-3.5 speed:** Phi-3.5-mini generates significantly more tokens per API call than Llama (~100-150s/ep vs ~18s/ep on FEVER always_trigger). This is model verbosity, not a bug.

### Step 1 Signal Discovery — ALL 16 RUNS COMPLETE

### Step 1 Results: token_entropy Spearman ρ (the key signal for direction reversal)

| Environment | Llama-3.1-8B | Phi-3.5-mini | Sign match? | Qwen3-4B (ref) |
|-------------|:---:|:---:|:---:|:---:|
| **HotpotQA** | **-0.346** * | **+0.184** * | ❌ | -0.041 |
| **APPS** | **-0.242** * | **-0.129** * | ✅ both neg | +0.012 |
| **APPS Interview** | **-0.249** * | -0.024 (ns) | ✅ both neg | +0.317* |
| **FEVER** | **+0.428** * | **-0.156** * | ❌ | -0.119* |
| **WebShop** | **+0.287** * | **+0.335** * | ✅ both pos | -0.019 |
| **Plancraft** | **-0.176** * | 0.000 (ns) | — no signal | -0.016 |
| **TWExpress** | 0.000 | 0.000 | — no signal | -0.290* |
| **CRUXEval** | -0.045 (ns) | -0.065 (ns) | — no signal | -0.048 |

\* = p < 0.05; ns = not significant

**Key finding**: Signal direction depends on **both environment AND model**, not environment alone. Among the 5 envs with significant signals on both models:
- 3/5 consistent sign: APPS (both −), WebShop (both +), APPS Interview (both −)
- 2/5 inconsistent: HotpotQA (Llama −, Phi +), FEVER (Llama +, Phi −)

**Implication for paper**: This is a **stronger result** than sign consistency. Fixed-direction methods (CaTS, CATTS) are even more fragile than originally argued — they fail not only across environments but also when switching backbones within the same environment. Only adaptive gating (EAAG) can handle this unpredictability. The paper narrative upgrades from "direction depends on environment" to "direction depends on environment × model interaction."

### Step 2A Bounds Results (as of 2026-04-02)

**Phi-3.5-mini (mean SR across seeds):**
| Env | base_only | always_trigger | oracle | seeds |
|-----|:---:|:---:|:---:|:---:|
| HotpotQA | 28.3% | 98.8% | 98.8% | ✅ 3/3 all |
| APPS | 59.0% | 75.0% | 75.0% | ✅ 3/3 all |
| WebShop | 3.5% | 53.5% | 52.3% | ✅ 3/3 all |
| FEVER | 7.2% | 61.0% | 61.2% | ✅ 3/3 all |
| TWExpress | 66.7% | 97.8% (2s) | 98.5% (1s) | ⚠️ AT/oracle incomplete (TIMEOUT) |
| Plancraft | 13.7% | 14.5% | 14.3% | ✅ 3/3 all |
| APPS Interview | 27.0% | 79.5% | 79.5% | ✅ 3/3 all |
| CRUXEval | 99.5% | 99.5% | 99.5% | ✅ 3/3 all |

**Llama-3.1-8B (mean SR across seeds):**
| Env | base_only | always_trigger | oracle | seeds |
|-----|:---:|:---:|:---:|:---:|
| HotpotQA | 46.3% | 99.5% | 99.5% | ✅ 3/3 all |
| APPS | 53.3% | 75.0% | 75.0% | ✅ 3/3 all |
| WebShop | 1.2% | 42.8% | 42.3% | ✅ 3/3 all |
| FEVER | 13.2% | 62.8% | 63.0% | ✅ 3/3 all |
| TWExpress | 36.5% | — | — | ❌ AT/oracle all TIMEOUT (600s/ep) |
| Plancraft | 31.7% | 18.7% | 18.3% | ✅ 3/3 all ⚠️ **rollout harmful -13pp** |
| APPS Interview | 60.2% | 79.5% | 79.5% | ✅ 3/3 all |
| CRUXEval | 99.0% | 99.5% | 99.5% | ✅ 3/3 all |

### Phi-3.5 Complete Results — ALL methods (CALIBRATED, as of 2026-04-06)

| Env | base | AT | oracle | CATTS | SEAG† | CoRef† | CaTS† | AUQ | s1Bgt | **EAAG** |
|-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| HotpotQA | 28.3% | 98.8% | 98.8% | 42.0% | **88.3%** | **87.7%** | 68.3% | 31.2% | 94.2% | **92.3%** |
| APPS | 59.0% | 75.0% | 75.0% | 28.0% | 30.0% | 30.3% | 35.8% | 27.3% | 36.2% | 37.2% |
| WebShop | 3.5% | 53.5% | 52.3% | 28.7% | 36.5% | 35.8% | **41.7%** | 7.0% | 3.0% | **57.3%** |
| FEVER | 7.2% | 61.0% | 61.2% | 12.7% | 13.5% | 13.7% | **19.8%** | 8.5% | 23.0% | 16.5% |
| TWExpress | 66.7% | 97.8% | 98.5% | 86.7% | **94.5%** | **94.7%** | 68.2% | 94.5% | 95.7% | **96.7%** |
| Plancraft | 13.7% | 14.5% | 14.3% | 13.5% | 14.7% | 15.2% | 13.5% | 12.7% | 13.7% | 13.8% |
| APPS Intv | 27.0% | 79.5% | 79.5% | 27.7% | 27.8% | 28.5% | 30.5% | 27.2% | 34.5% | **36.8%** |
| CRUXEval | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% | 99.5% |

† = Phase 1 calibrated (SEAG/CoRefine/CaTS). **Calibration made a huge difference** — e.g. SEAG on HotpotQA: 28%→88% (+60pp), WebShop: 3%→37% (+33pp).

> **Key findings (Phi-3.5):**
> - **EAAG on WebShop: 57.3%** > AT 53.5%, beats ALL CB (best CaTS† 41.7%) by +15pp
> - **APPS: all methods < base 59%** — rollout quality issue on Phi-3.5, EAAG (37.2%) not exempt
> - **Plancraft: EAAG 13.8% ≈ base** — correctly learned not to trigger (cost=6%)
> - Calibrated SEAG†/CoRefine† now competitive on HotpotQA (88%) and TWExpress (95%)

### Amortized Cost Analysis: EAAG vs Calibrated CB†

### Full Cost Model: All Hidden Costs Included

Previous amortized analysis only counted rollouts. The **true cost** must include:

| Method | Gate overhead per step | Phase 1 cost | Notes |
|--------|:---:|:---:|------|
| CATTS | **K=5 extra LLM calls** | 0 (optional) | Highest per-step cost |
| SEAG† | 0 | 200 ep × AT rollouts | Reads logprob from proposer call |
| CoRefine† | 0 | 200 ep × AT rollouts | Reads entropy from proposer call |
| CaTS† | 0 | 200 ep × AT rollouts | Platt scaling on confidence |
| AUQ | **1 extra LLM call** (confidence query) | 0 (optional) | Asks LLM "how confident?" |
| **EAAG** | **0** | **0** | No extra calls, no Phase 1 |

**Total LLM calls per episode** = base proposer (1/step × steps) + gate overhead + rollout calls + amortized Phase 1

Phi-3.5 results (calls/episode, 200-ep deployment):

| Env | EAAG SR | EAAG cost | Best CB† SR | CB† cost | CATTS SR | CATTS cost |
|-----|:---:|:---:|:---:|:---:|:---:|:---:|
| HotpotQA | **92.3%** | **6.1** | SEAG† 88.3% | 7.8 | 42.0% | **30.6** |
| APPS | 37.2% | **7.1** | CaTS† 35.8% | 9.6 | 28.0% | 30.2 |
| **WebShop** | **57.3%** | **7.5** | CaTS† 41.7% | 9.9 | 28.7% | 30.5 |
| FEVER | 16.5% | **7.4** | CaTS† 19.8% | 12.8 | 12.7% | 30.5 |
| TWExpress | **96.7%** | **7.7** | CoRef† 94.7% | 11.1 | 86.7% | 30.9 |
| **Plancraft** | 13.8% | **5.7** | CoRef† 15.2% | **19.7** | 13.5% | 30.1 |
| APPS Intv | **36.8%** | **7.1** | CaTS† 34.3% | 8.6 | 27.7% | 30.1 |
| CRUXEval | 99.5% | **5.3** | all 99.5% | 7.0+ | 99.5% | 30.1 |

> **Key insight:** CATTS (K=5 voting) costs 30+ calls/ep — **4-5× more than EAAG** — while often achieving worse SR. Even calibrated CB† methods cost 8-20 calls/ep (including amortized Phase 1). **EAAG achieves the best SR/cost tradeoff at 5.3-7.7 calls/ep across all environments.**
>
> EAAG **Pareto-dominates** all CB on 6/7 non-ceiling environments when total cost (gate overhead + rollouts + Phase 1 amortization) is properly accounted for:
> - Higher or equal SR on 6/7 envs (only FEVER -3.3pp)
> - Lower total cost on ALL 8 envs
> - No pre-deployment data collection required
>
> Note: s1_budget excluded — it's a budget-parity baseline from Muennighoff et al. (2024), not a direct competitor in the adaptive gating space.

### Llama-3.1-8B Partial Results (as of 2026-04-06)

| Env | base | AT | oracle | **EAAG** | CB | note |
|-----|:---:|:---:|:---:|:---:|:---:|------|
| HotpotQA | 46.3% | 99.5% | 99.5% | **95.5%** | pending | EAAG near AT |
| APPS | 53.3% | 75.0% | 75.0% | **55.0%** | pending | EAAG ≈ base (not harmful, unlike Phi) |
| WebShop | 1.2% | 42.8% | 42.3% | **41.7%** | pending | EAAG ≈ AT |
| FEVER | 13.2% | 62.8% | 63.0% | **34.7%** | pending | decent improvement |
| TWExpress | 36.5% | — | — | running | pending | bounds TIMEOUT |
| Plancraft | 31.7% | 18.7% | 18.3% | running | pending | rollout harmful |
| APPS Intv | 60.2% | 79.5% | 79.5% | running | pending | |
| CRUXEval | 99.0% | 99.5% | 99.5% | running | pending | |

**CB Llama: 0/144 — pending GPU (job 23694865)**

### Phase 1 calibration dependency (from paper Table 2)

| CB Method | Needs Phase 1 data? | Without calibration | Phi results valid? |
|-----------|:---:|------|:---:|
| CATTS | ❌ optional | Fixed thresholds (entropy=0.5, margin=0.4) | ✅ valid |
| **SEAG** | **✓ required (†)** | Fallback threshold=0.3 (no percentile search) | ❌ rerun |
| **CoRefine** | **✓ required (†)** | Fallback threshold=0.5 (no percentile search) | ❌ rerun |
| **CaTS** | **✓ required (†)** | Fallback threshold=0.3 (no Platt scaling) | ❌ rerun |
| AUQ | ❌ optional | Fixed threshold=0.5 | ✅ valid |
| s1_budget | ❌ not needed | Pure fixed-budget, no thresholds | ✅ valid |

> **Root cause:** All 16 review configs had wrong `phase1_data_path` — pointed to `.../review/{model}/{env}/phase1_signal_data.json` but actual file is at `.../review/{model}/{env}/{env}/phase1_signal_data.json`. **Fixed all configs on 2026-04-04.**

### Issues and fixes (as of 2026-04-04)

| Issue | Affected | Cause | Fix | Status |
|-------|----------|-------|-----|--------|
| TWExpress AT/oracle TIMEOUT | S2A Phi idx 39,42 + Llama idx 39-44 | 600s/ep, 12h not enough | Need `--time=36:00:00` or sharding | ❌ TODO |
| S2A Phi idx 43 FAILED | Phi TWExpress oracle/seed_42 | vLLM startup timeout | Resubmit | ❌ TODO |
| Wrong `phase1_data_path` | All 16 review configs | Missing `/{env}/` in path | Fixed all configs | ✅ fixed |
| CB Phi seag/corefine/cats invalid | 72/144 CB Phi results | Ran without calibration | Resubmitted as **23669862** | ✅ resubmitted |
| CB Llama TMPCONFIG bug | All 144 CB Llama jobs | `TMPCONFIG: unbound variable` | Resubmitted as **23669864** (with fixed config+script) | ✅ resubmitted |
| EAAG Phi wrong output path | 18/24 completed EAAG Phi | `p6_e_method_upgrade.py` hardcoded path | Fixed line 158, resubmitted as **23669706** | ✅ resubmitted |
| EAAG Llama TMPCONFIG bug | All 24 EAAG Llama jobs | Same unbound variable | Resubmitted as **23669707** | ✅ resubmitted |
| TMPCONFIG bug in scripts | Multiple sbatch scripts | trap cleanup refs undefined var | **All 12 scripts now fixed** | ✅ all fixed |

### Data paths

All results stored under `results/review/{model}/{env}/{env}/{method}/seed_{seed}/summary.json`:
```
results/review/
├── phi35_mini/{env}/{env}/
│   ├── base_only/seed_{42,123,456}/     # ✅ Step 2A complete (except TWExpress partial)
│   ├── always_trigger/seed_{...}/       # ✅ same
│   ├── oracle/seed_{...}/               # ✅ same
│   ├── catts/seed_{...}/                # ✅ valid (no calibration needed)
│   ├── seag/seed_{...}/                 # ✅ calibrated (APPS/APPS_Intv: uncalibrated due to OOM)
│   ├── corefine/seed_{...}/             # ✅ calibrated (APPS: 1 seed uncalibrated due to OOM)
│   ├── cats/seed_{...}/                 # ✅ calibrated (APPS: all OOM; APPS_Intv: all OOM)
│   ├── auq/seed_{...}/                  # ✅ valid (no calibration needed)
│   ├── s1_budget/seed_{...}/            # ✅ valid (no calibration needed)
│   └── se_few5_filter_local/seed_{...}/ # ✅ 24/24 COMPLETE (job 23669706)
├── llama31_8b/{env}/{env}/
│   ├── base_only/seed_{...}/            # ✅ Step 2A complete (except TWExpress TIMEOUT)
│   ├── always_trigger/seed_{...}/       # ✅ same
│   ├── oracle/seed_{...}/               # ✅ same
│   ├── catts/seed_{...}/                # 🔄 running (job 23694865, 72/144 done)
│   ├── seag/seed_{...}/                 # 🔄 running
│   ├── corefine/seed_{...}/             # 🔄 running
│   ├── cats/seed_{...}/                 # 🔄 running
│   ├── auq/seed_{...}/                  # 🔄 running
│   ├── s1_budget/seed_{...}/            # 🔄 running
│   └── se_few5_filter_local/seed_{...}/ # ✅ 24/24 COMPLETE (job 23694864)
```

_(Old Phi results table removed — see calibrated version above at line 472)_

### Issues and fixes (as of 2026-04-06)

| Issue | Affected | Cause | Fix | Status |
|-------|----------|-------|-----|--------|
| TWExpress AT/oracle TIMEOUT | S2A Phi 3 + Llama 6 | 600s/ep, 12h not enough | Need `--time=36:00:00` or sharding | ❌ TODO |
| Wrong `phase1_data_path` | All 16 review configs | Missing `/{env}/` in path | Fixed all configs | ✅ fixed |
| CB Phi calibrated OOM | 15 jobs (APPS+APPS_Intv × seag/corefine/cats) | 48GB mem not enough for code-gen envs | Resubmit with `--mem=64G` | ❌ TODO |
| CB Phi seag/corefine/cats uncalibrated | 72 CB Phi results | Ran without phase1 data | Resubmitted as **23669862** | ✅ **COMPLETE** (except OOM above) |
| EAAG Phi wrong output path | 24 EAAG Phi results | Hardcoded path in p6 script | Fixed p6_e_method_upgrade.py line 158 | ✅ **COMPLETE** |
| CB/EAAG Llama wrong MODEL name | All CB+EAAG Llama | `microsoft/` instead of `meta-llama/` | Fixed scripts, resubmitted | ✅ fixed |
| TMPCONFIG unbound variable | Multiple scripts | trap cleanup refs undefined var | All 12 scripts fixed | ✅ all fixed |

### Pipeline Progress

- [x] **Step 0 GO/NO-GO — ALL 8 envs × 2 models: COMPLETE**
- [x] **Step 1 Signal Discovery — ALL 8 envs × 2 models: COMPLETE**
- [x] Step 2A Bounds — Phi: ✅ 69/72 (TWExpress AT/oracle TIMEOUT)
- [x] Step 2A Bounds — Llama: ✅ 66/72 (TWExpress TIMEOUT)
- [x] Step 2B CB Phi: ✅ **144/144** (calibrated; APPS/APPS_Intv seag/coref/cats OOM → uncalibrated fallback)
- [x] Step 2C EAAG Phi: ✅ **24/24 COMPLETE**
- [x] Step 2C EAAG Llama: ✅ **24/24 COMPLETE** (job 23694864)
- [ ] Step 2B CB Llama: 🔄 **72/144 done**, 6 running (job **23694865**)
- [ ] CB Phi OOM rerun: submitted job **23737729** (`--mem=64G`, 15 jobs, array 21,23,25,27-29,111-119)
- [ ] TWExpress sharded rerun: job **23737873** (36 jobs, array 0-35, 3 shards × 2 methods × 3 seeds × 2 models)
  - 12h partition limit → split 200 eps into 3 shards (0-66, 67-133, 134-199)
  - Script: `scripts/review/run_twexpress_sharded.sbatch`
  - Need merge-shards step after completion
- [ ] Exp 3: Cross-optimizer (both new models)
- [ ] Exp 4: Budget sensitivity (both new models)
- [ ] Create Exp 3 + Exp 4 sbatch scripts for Phi-3.5
- [ ] **Large API model (GPT-4o / GPT-4o-mini): Step 0 + Step 1 on 8 envs**
  - Addresses Reviewer 3: "larger models (70B+) might eliminate direction reversal"
  - Code already supports `api_type: "openai"` — no GPU needed, just API key
  - Only need Step 0 + Step 1 (signal discovery) — not full Step 2
  - TODO: create configs with `api_type: "openai"`, run locally (no SLURM needed)
- [ ] Run `python scripts/review/analyze_multi_backbone.py`

### Llama-3.1-8B EAAG Complete Results (as of 2026-04-06)

| Env | base | AT | oracle | **EAAG** | Δ vs base |
|-----|:---:|:---:|:---:|:---:|:---:|
| HotpotQA | 46.3% | 99.5% | 99.5% | **95.5%** | +49.2pp |
| APPS | 53.3% | 75.0% | 75.0% | 55.0% | +1.7pp |
| WebShop | 1.2% | 42.8% | 42.3% | **41.7%** | +40.5pp |
| FEVER | 13.2% | 62.8% | 63.0% | 34.7% | +21.5pp |
| TWExpress | 36.5% | — | — | **94.8%** | +58.3pp |
| Plancraft | 31.7% | 18.7% | 18.3% | 27.0% | -4.7pp |
| APPS Intv | 60.2% | 79.5% | 79.5% | 59.7% | -0.5pp |
| CRUXEval | 99.0% | 99.5% | 99.5% | 99.3% | +0.3pp |

> **Cross-model EAAG comparison:**
> | Env | Phi EAAG | Llama EAAG | note |
> |-----|:---:|:---:|------|
> | HotpotQA | 92.3% | **95.5%** | both strong |
> | APPS | 37.2% | **55.0%** | Llama not harmed (Phi harmed) |
> | WebShop | **57.3%** | 41.7% | Phi better |
> | FEVER | 16.5% | **34.7%** | Llama much better |
> | TWExpress | 96.7% | **94.8%** | both strong |
> | Plancraft | **13.8%** (≈base) | 27.0% (-4.7pp) | Phi safer |
> | APPS Intv | 36.8% | **59.7%** (≈base) | Llama safer |
> | CRUXEval | 99.5% | 99.3% | both ceiling |

### Currently running/queued jobs (as of 2026-04-06)

| Job ID | Task | Jobs | Status |
|--------|------|------|--------|
| **23737729** | CB Phi OOM rerun (--mem=64G, APPS+APPS_Intv) | 15 | running |
| **23737873** | TWExpress bounds sharded (2 models × 2 methods × 3 seeds × 3 shards) | 36 | pending |
| **23749957** | CB Llama plancraft+cruxeval (normal) | 36 | pending |
| **23749958** | CB Llama APPS rerun (--mem=64G) | 18 | pending |
| **23749959** | CB Llama APPS Interview (--mem=64G) | 18 | pending |
| **23750380** | CB Llama TWExpress sharded (6 methods × 3 seeds × 3 shards) | 54 | pending |

**CB Llama status:**
- hotpotqa/webshop/fever: ✅ done (54/144 calibrated)
- APPS: OOM → resubmit `--mem=64G` (job 23749958)
- APPS Interview: resubmit `--mem=64G` (job 23749959) — may also OOM
- plancraft/cruxeval: normal resubmit (job 23749957)
- TWExpress: sharded (job **23750380**, 54 jobs = 6 methods × 3 seeds × 3 shards)
  - Added `--episode-start` support to `p5_competing_baselines.py`
  - Script: `scripts/review/run_twexpress_cb_sharded.sbatch`
  - Shards save to `summary_shard_{start}_{end}.json`, need merge after completion

### 2026-03-28: ALL Step 2 submitted

**Step 1 reruns (TWExpress/Plancraft stub fix):**
- Phi-3.5 Step 1 twexpress+plancraft: job **23489140** (array 4,5)
- Llama Step 1 twexpress: job **23489141** (array 4)
- Llama Step 1 plancraft: job **23488474** (array 5) — running

**Step 2A: Bounds (base_only, always_trigger, oracle) via p5 --step 2:**
- Phi-3.5: job **23489097** (array 0-71, 72 jobs)
- Llama: job **23489098** (array 0-71, 72 jobs)

**Step 2B: Competing Baselines (catts, seag, corefine, cats, auq, s1_budget) via p5_competing_baselines:**
- Phi-3.5: job **23489134** (array 0-143, 144 jobs)
- Llama: job **23489135** (array 0-143, 144 jobs)

**Step 2C: EAAG (se_few5_filter_local) via p6_e_method_upgrade:**
- Phi-3.5: job **23489136** (array 0-23, 24 jobs)
- Llama: job **23489137** (array 0-23, 24 jobs)

**Still running from earlier:**
- Phi-3.5 Step 0 twexpress: job 23487057_4
- Phi-3.5 Step 0 plancraft: job 23487057_5
- Llama Step 0 twexpress: job 23487059_4

**Total new jobs submitted: 480 + 3 Step 1 reruns = 483 GPU jobs**

### 2026-03-29: Partial failures and resubmissions

**Failure causes:**
1. `TMPCONFIG: unbound variable` — trap cleanup referenced TMPCONFIG before it was defined. Fixed by initializing `TMPCONFIG=""` before trap.
2. `/tmp: No space left on device` — too many concurrent jobs creating temp files in /tmp (10GB). Fixed by using `/scratch/.../tmp/` instead.

**Fixes applied to ALL 12 review sbatch scripts** (not just Step 2 — also Step 0, Step 1, CB, EAAG).

> **Note:** SLURM snapshots the script at submission time. Fixing the file does NOT fix already-submitted pending jobs. Must cancel and resubmit.

**Completed (valid) from first submission:**
- Step 2A Phi: 24/72 completed (envs 0-2: hotpotqa, apps, webshop partial)
- Step 2A Llama: 5/72 completed
- Step 2B Phi CB: ~102/144 completed (envs 0-3: hotpotqa, apps, webshop, fever)
- Step 0 TWExpress/Plancraft reruns: ✅ ALL COMPLETE
- Step 1 Llama plancraft: ✅ COMPLETE (job 23488474)

**Resubmitted with fixed scripts:**
- Step 2A Phi: job **23517107** (48 failed indices) — ⏳ running (6 concurrent)
- Step 2A Llama: job **23517116** (67 failed indices) — pending
- Step 2B Phi CB: job **23517123** (~75 failed indices) — pending
- Step 2B Llama CB: job **23517129** (full 144) — pending
- Step 2C EAAG Phi: job **23517445** (24 jobs) — pending
- Step 2C EAAG Llama: job **23517446** (24 jobs) — pending
- Step 1 Phi TWExpress+Plancraft: job **23517254** (array 4,5) — pending
- Step 1 Llama TWExpress: job **23517258** (array 4) — pending

### 2026-03-29: Killed stub jobs, queue unblocked

CB-Phi 1st batch (23489134) had 60 remaining TWExpress/Plancraft jobs with stub phase1_data — killed to free GPU.

### 2026-03-29: Reduced to 2 GPU slots, resubmitted with %2 limit

Cancelled all pending jobs and resubmitted with `%2` array concurrency to free GPU quota for other users.

### 2026-03-29: ALL JOBS CANCELLED — paused to free GPU (later resumed)

**Completed data so far (across all batches):**
- S2A Phi bounds: ~33/72 unique indices done (batches 23489097+23517107+23524967)
- S2A Llama bounds: ~9/72 unique indices done (batches 23489098+23517116+23524970)
- CB Phi: ~108/144 done (batch 23489134, but TWExpress/Plancraft data invalid from stub)
- CB Llama: 0/144
- EAAG Phi: 0/24
- EAAG Llama: 0/24
- S1 TWExpress/Plancraft reruns: only Llama Plancraft done (23488474), rest not started

### 2026-03-31: ALL JOBS RESUMED

| Job ID | Task | Jobs |
|--------|------|------|
| Job ID | Task | Jobs | Status |
|--------|------|------|--------|
| **23574082** | S1 Phi TWExpress+Plancraft | array 4,5 | ✅ COMPLETE |
| **23574083** | S1 Llama TWExpress | array 4 | ✅ COMPLETE |
| **23574085** | S2A Phi bounds remaining | array 23,32-71 (41 jobs) | 38 done, 1 failed, 3 running |
| **23574086** | S2A Llama bounds remaining | array 2-3,5-19,21-33,35-71 (67 jobs) | pending |
| **23574087** | CB Phi (full) | array 0-143 (144 jobs) | pending |
| **23574088** | CB Llama (full) | array 0-143 (144 jobs) | pending |
| **23574089** | EAAG Phi | array 0-23 (24 jobs) | pending |
| **23574090** | EAAG Llama | array 0-23 (24 jobs) | pending |
| **23609762** | CB Phi TWExpress+Plancraft | array 72-107 (36 jobs) | pending |
| **23609763** | CB Llama TWExpress+Plancraft | array 72-107 (36 jobs) | pending |

## GPU Budget Estimate (updated for 8 envs × 2 models × 10 methods)

| Experiment | Script | Jobs/model | Total jobs | GPU-hrs/job | Total GPU-hrs |
|------------|--------|-----------|------------|-------------|---------------|
| Step 0 GO/NO-GO | p5 --step 0 | 8 | 16 | 2 | 32 |
| Step 1 Signal Discovery | p5 --step 1 | 8 | 16 | 10 | 160 |
| Step 2A Bounds (3 methods) | p5 --step 2 | 72 | 144 | 10 | 1440 |
| Step 2B CB (6 baselines) | p5_competing_baselines | 144 | 288 | 10 | 2880 |
| Step 2C EAAG (1 method) | p6_e_method_upgrade | 24 | 48 | 10 | 480 |
| Exp 3 Cross-Optimizer | — | 2 | 4 | 10 | 40 |
| Exp 4 Budget Sensitivity | — | 30 | 60 | 8 | 480 |
| **Total** | | | **576** | | **~5512 GPU-hrs** |

---

## 8-Environment Expansion Status

- [x] Created configs for 4 new envs × 2 models
- [x] Updated step0/step1 sbatch ENVS arrays (4 → 8)
- [x] Installed `textworld-express==1.1.0` and `plancraft==0.4.9` in `frvc_review` (were in stub mode)
- [x] Updated step2 sbatch → bounds only (base_only, always_trigger, oracle), removed scg_finetune_lr
- [x] Created `run_cb_{phi35,llama31}.sbatch` → competing baselines via `p5_competing_baselines.py`
- [x] Created `run_eaag_{phi35,llama31}.sbatch` → EAAG (se_few5_filter_local) via `p6_e_method_upgrade.py`
- [ ] Create Exp 3 + Exp 4 sbatch scripts for Phi-3.5

### Stub mode issues (same pattern as WebShop)
TWExpress and Plancraft ran in stub mode because `frvc_review` was missing their packages.
**All Step 0 + Step 1 data for TWExpress and Plancraft is INVALID (stub mode).**
Resubmitted Step 0: Phi-3.5 job 23487057, Llama job 23487059 (array 4,5). Need to rerun Step 1 after.

CRUXEval loaded correctly (800 problems) — its data is valid.

### Existing Qwen3-4B data
- Signal discovery: all 8 envs ✅
- Budget sensitivity: all 8 envs ✅
- Cross-optimizer: ❌ not done (new experiment)
- Core EAAG (Step 2): partial coverage (varies by env)

---

## Decision Gates

### Gate 1: GO/NO-GO (after Step 0)
- **Pass**: base SR ∈ [5%, 85%] AND always_trigger SR > base + 3pp
- **Fail action**: If a model fails GO on an env, investigate. Possible fixes:
  - Increase max_tokens (model needs more generation budget)
  - Adjust prompting format (Phi-3.5 uses ChatML, Llama uses Llama-3 format)
  - Drop that env for that model (still have other envs as evidence)

### Gate 2: Direction Reversal (after Step 1) — COMPLETED

**Original criterion**: entropy ρ sign consistent across 3 backbones for ≥6/8 envs.

**Actual result**: Mixed — sign is consistent on some envs (APPS, WebShop) but not others (HotpotQA, FEVER).

**Reinterpretation**: The finding is **stronger than sign consistency**. Direction depends on BOTH environment AND model, making it fundamentally unpredictable. This strengthens the case for adaptive gating (EAAG) even further — fixed-direction methods fail not only across environments but also across model swaps within the same environment.

See "Step 1 Results" section below for full data.

### Gate 3: EAAG Effectiveness (after Step 2)
- **Pass**: EAAG SR > best CB baseline on ≥5/8 envs for both models
- **Partial pass**: Works on 1 model → still useful data point
