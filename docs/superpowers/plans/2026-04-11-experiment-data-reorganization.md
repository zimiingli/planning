# Experiment Data Reorganization Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate all experiment data (Qwen3 baseline + Phi-3.5 + Llama-3.1 multi-backbone) into `planning/experiment/`, with clear mapping to writing prompts, raw data sources, and pending experiments.

**Architecture:** Extend existing `experiment/{fig,tab}_*/` folder convention. Each folder gets an updated README.md with writing prompt, multi-backbone data status, and raw source paths. New folders created for missing fig/tab. Pending experiments tracked in `experiment/pending/`. Global `INDEX.md` provides one-line status for every item.

**Tech Stack:** Markdown, CSV, Python (generate_all_csvs.py update)

---

## Full Inventory: Writing Prompts → Experiment Folders

### Main Text (experiments.tex)

| # | Label | Type | Writing Prompt | Existing Folder | Data Status |
|---|-------|------|---------------|-----------------|-------------|
| M1 | tab:main | DATA | L80: Main results table, methods × 8 envs | `tab_main_results/` | Qwen3 ✅, needs Phi/Llama |
| M2 | tab:winloss | DATA | L90: Win/loss summary | `tab_winloss/` | Qwen3 ✅, needs Phi/Llama |
| M3 | fig:pareto | FIGURE | L94: Pareto frontier 2×3 grid | `fig2_pareto/` | Qwen3 ✅, needs Phi/Llama |
| M4 | fig:entropy-bin | FIGURE | L143: SR by entropy bin 1×3 panels | **MISSING** | TODO |
| M5 | fig:trigger-adapt | FIGURE | L208: Trigger rate by step 2×3 grid | `fig_trigger_rate/` | Qwen3 ✅, needs Phi/Llama |
| M6 | fig:direction-cost | FIGURE | L248: BSW cost vs signal strength scatter | `fig3_bsw_direction/` | Qwen3 ✅ |
| M7 | fig:temporal-shift | FIGURE | L305: P1 temporal ρ shift bars | `fig_p1_temporal_shift/` | Qwen3 ✅ |
| M8 | fig:case-study | FIGURE | L442: Trajectory gate visualization | **MISSING** | TODO |

### Method (method.tex)

| # | Label | Type | Writing Prompt | Existing Folder | Data Status |
|---|-------|------|---------------|-----------------|-------------|
| T1 | fig:eaag-pipeline | FIGURE | L46: EAAG pipeline diagram | `fig_method_diagram/` | Diagram only (no data) |

### Appendix (appendix.tex)

| # | Label | Type | Writing Prompt | Existing Folder | Data Status |
|---|-------|------|---------------|-----------------|-------------|
| A0 | Table A0 | DATA | L577: AUC table | `fig_auc_hierarchy/` | Qwen3 ✅ |
| A1 | Table A1 | DATA | L535: Env × Feature LASSO matrix | `fig4_feature_heatmap/` | Qwen3 ✅ |
| A2 | Table A2 | DATA | L546: LLM-generated features | `fig5_llm_ablation/` | Qwen3 ✅ |
| A3 | Table A3 | DATA | L809: Method × Cost components | **MISSING** | TODO |
| A4 | Table A4 | DATA | L609: P1 Temporal Dynamics full | `fig_p1_temporal_shift/` | Qwen3 ✅ |
| A5 | Table A5 | DATA | L618: P3 Signal Identity | **MISSING** | TODO (data exists in signal_discovery) |
| A6 | Table A6 | DATA | L429: Multi-backbone full signals | **MISSING** | Phi/Llama step1 ✅ |
| A7 | Table A7 | DATA | L440: Cross-backbone baselines | **MISSING** | Phi ✅, Llama ~94% |
| A8 | Table A8 | DATA | L920: Full significance table | `tab_significance/` | Qwen3 ✅, needs Phi/Llama |
| A9 | Table A9 | DATA | L644: InfoPoor vs InfoRich | `fig_controlled_reversal/` | Qwen3 ✅ |
| AF1 | Figure A1 | FIGURE | L362: pI axis diagram | **MISSING** | Conceptual diagram |
| AF2 | Figure A2 | FIGURE | L870: Hyperparameter sensitivity | **MISSING** | Pending (Exp 4 + threshold) |
| AF3 | Figure A3 | FIGURE | L582: AUC hierarchy bar chart | `fig_auc_hierarchy/` | Qwen3 ✅ |
| AF4 | Figure A4 | FIGURE | L445: Multi-backbone heatmap | **MISSING** | Phi/Llama step1 ✅ |
| AF5 | Figure A5 | FIGURE | L474: Cross-backbone SR compare | **MISSING** | Phi ✅, Llama ~94% |
| AF6 | Figure A6 | FIGURE | L648: Controlled reversal shift | `fig_controlled_reversal/` | Qwen3 ✅ |
| AF7 | Figure A7 | FIGURE | L815: Full Pareto (8 envs) | **MISSING** | Partial |
| AF8 | Figure A8 | FIGURE | L832: Cost breakdown | **MISSING** | TODO |
| -- | LLM Prompt | DATA | L927: Full prompt template | **MISSING** | TODO (extract from code) |

### Existing Folders NOT in Writing Prompts (keep as-is)

| Folder | Purpose | Status |
|--------|---------|--------|
| `tab_env_setup/` | Table 1: env setup | ✅ |
| `tab_env_info_structure/` | Env info structure | ✅ |
| `tab_gate_capacity/` | Table: gate complexity ablation | ✅ |
| `tab_method_classification/` | Method classification | ✅ |
| `tab_diagnostic_results/` | Diagnostic env results | ✅ |
| `tab_appendix_results/` | Appendix results | ✅ |
| `fig6_fever_bias/` | FEVER bias analysis | ✅ |
| `fig_bsw_vs_rho/` | BSW vs ρ scatter | ✅ |
| `fig_coverage_proxy/` | Coverage proxy | ✅ |
| `fig_matched_pair/` | Matched pair visualization | ✅ |
| `fig_stratified_reversal/` | Stratified reversal | ✅ |

### Pending Experiments

| ID | Experiment | What's Missing | Target Folders |
|----|-----------|---------------|----------------|
| P1 | Exp 3: Cross-Optimizer | Phi+Llama, 2 envs × 2 optimizers | `tab_multi_backbone_signal/` |
| P2 | Exp 4: Budget Sensitivity | Phi+Llama, 2 envs × 5 budgets × 3 seeds | `fig_hyperparam_sensitivity/` |
| P3 | GPT-4o Signal Discovery | 8 envs, Step 0+1 only | `tab_multi_backbone_signal/` |
| P4 | Llama CB TWExpress | auq, cats, s1_budget missing | `tab_multi_backbone_results/` |
| P5 | Gate threshold τ sweep | τ ∈ {0.3–0.7} | `fig_hyperparam_sensitivity/` |

---

## Task 1: Create `pending/` Directory with 5 Tracking Files

**Files:**
- Create: `planning/experiment/pending/exp3_cross_optimizer.md`
- Create: `planning/experiment/pending/exp4_budget_sensitivity.md`
- Create: `planning/experiment/pending/gpt4o_signal_discovery.md`
- Create: `planning/experiment/pending/llama_cb_twexpress.md`
- Create: `planning/experiment/pending/gate_threshold_sweep.md`

- [ ] Step 1: Create pending directory and all 5 files

---

## Task 2: Create New Experiment Folders for Missing Items

**Files to create (each gets README.md):**
- Create: `planning/experiment/fig_entropy_bin/README.md`
- Create: `planning/experiment/fig_case_study/README.md`
- Create: `planning/experiment/fig_pi_axis_diagram/README.md`
- Create: `planning/experiment/fig_hyperparam_sensitivity/README.md`
- Create: `planning/experiment/fig_full_pareto_8env/README.md`
- Create: `planning/experiment/fig_cost_breakdown/README.md`
- Create: `planning/experiment/fig_multi_backbone_heatmap/README.md`
- Create: `planning/experiment/fig_multi_backbone_sr_compare/README.md`
- Create: `planning/experiment/tab_multi_backbone_signal/README.md`
- Create: `planning/experiment/tab_multi_backbone_results/README.md`
- Create: `planning/experiment/tab_cost_components/README.md`
- Create: `planning/experiment/tab_signal_identity/README.md`
- Create: `planning/experiment/tab_prompt_template/README.md`

- [ ] Step 1: Create all directories
- [ ] Step 2: Write README.md for each, with writing prompt, data status, raw source

---

## Task 3: Update Existing Folders with Multi-Backbone Info

Folders that need README updates to include Phi/Llama data status and raw sources:

- Modify: `tab_main_results/README.md`
- Modify: `tab_winloss/README.md`
- Modify: `fig2_pareto/README.md`
- Modify: `fig_trigger_rate/README.md`
- Modify: `fig1_signal_heatmap/README.md`
- Modify: `tab_signal_discovery/README.md`
- Modify: `tab_significance/README.md`
- Modify: `fig3_bsw_direction/README.md`
- Modify: `fig_p1_temporal_shift/README.md`

- [ ] Step 1: Update each README with multi-backbone section

---

## Task 4: Extract Multi-Backbone Data to CSV Files

For folders where Phi/Llama data already exists in `results/review/`:

- Create: `tab_multi_backbone_signal/data.csv` (from step1_signal_discovery.json × 3 backbones)
- Create: `tab_multi_backbone_results/data.csv` (from summary.json × 3 backbones × all methods)
- Update: `tab_main_results/data_phi35.csv` and `data_llama31.csv`

- [ ] Step 1: Write extraction logic and generate CSVs

---

## Task 5: Create INDEX.md

- Create: `planning/experiment/INDEX.md`

- [ ] Step 1: Write global index mapping every fig/tab to folder, status, and paper location
