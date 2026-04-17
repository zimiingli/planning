# Experiment Data Index

> Last updated: 2026-04-11
> All experiment data for the FRVC paper. Each row maps a paper figure/table to its experiment folder.

## Status Legend
- **D** = data.csv ready
- **T** = .tex file ready
- **P** = output.pdf exists
- **G** = generate.py exists
- **needs-gen** = data exists but needs generate.py to produce figure/table
- **PENDING** = experiment not yet run

---

## Main Text Figures (experiments.tex)

| Paper Ref | Label | Folder | DTPG | Qwen3 | Phi | Llama | Notes |
|-----------|-------|--------|:----:|:-----:|:---:|:-----:|-------|
| Fig 1 | fig:signal-heatmap | `fig1_signal_heatmap/` | DTPG | ✅ | via A4 | via A4 | 3-backbone: `fig_multi_backbone_heatmap/` |
| Fig 2 | fig:pareto | `fig2_pareto/` | D-PG | ✅ | R | R | 8-env version: `fig_full_pareto_8env/` |
| Fig 3 | fig:entropy-bin | `fig_entropy_bin/` | D--- | ✅ | R | R | **NEW** needs-gen |
| Fig 4 | fig:trigger-adapt | `fig_trigger_rate/` | D-PG | ✅ | R | R | |
| Fig 5 | fig:direction-cost | `fig3_bsw_direction/` | D-PG | ✅ | — | — | BSW ablation |
| Fig 6 | fig:temporal-shift | `fig_p1_temporal_shift/` | D-PG | ✅ | R | R | |
| Fig 7 | fig:case-study | `fig_case_study/` | ---- | needs-gen | — | — | **NEW** complex join needed |

## Main Text Tables (experiments.tex)

| Paper Ref | Label | Folder | DTPG | Qwen3 | Phi | Llama | Notes |
|-----------|-------|--------|:----:|:-----:|:---:|:-----:|-------|
| Table 1 | tab:env-setup | `tab_env_setup/` | DT-G | ✅ | — | — | Static env description |
| Table 2 | tab:main | `tab_main_results/` | DTPG | ✅ | via A7 | via A7 | Multi-backbone: `tab_multi_backbone_results/` |
| Table 3 | tab:winloss | `tab_winloss/` | DT-G | ✅ | TODO | TODO | Needs recomputation for Phi/Llama |
| Table 4 | tab:capacity | `tab_gate_capacity/` | DTPG | ✅ | — | — | Gate complexity ablation |

## Method (method.tex)

| Paper Ref | Label | Folder | DTPG | Notes |
|-----------|-------|--------|:----:|-------|
| Fig (pipeline) | fig:dial-pipeline | `fig_method_diagram/` | ---- | Conceptual TikZ diagram |

## Signal Utility Landscape (signal_utility_landscape.tex)

| Paper Ref | Folder | DTPG | Notes |
|-----------|--------|:----:|-------|
| Feature heatmap | `fig4_feature_heatmap/` | DTPG | ✅ |
| LLM ablation | `fig5_llm_ablation/` | DTPG | ✅ |
| FEVER bias | `fig6_fever_bias/` | DTPG | ✅ |
| Matched pair | `fig_matched_pair/` | DTPG | ✅ |

## Appendix Figures (appendix.tex)

| Paper Ref | Label | Folder | DTPG | Qwen3 | Phi | Llama | Notes |
|-----------|-------|--------|:----:|:-----:|:---:|:-----:|-------|
| Fig A1 | pI axis | `fig_pi_axis_diagram/` | D--- | ✅ | — | — | **NEW** needs-gen |
| Fig A2 | Hyperparam | `fig_hyperparam_sensitivity/` | ---- | — | — | — | **PENDING** Exp 4 + threshold |
| Fig A3 | AUC hierarchy | `fig_auc_hierarchy/` | DTPG | ✅ | — | — | |
| **Fig A4** | **Multi-bb heatmap** | `fig_multi_backbone_heatmap/` | D--- | ✅ | ✅ | ✅ | **NEW** needs-gen |
| **Fig A5** | **Cross-bb SR** | `fig_multi_backbone_sr_compare/` | D--- | ✅ | ✅ | ✅ | **NEW** needs-gen |
| Fig A6 | Controlled reversal | `fig_controlled_reversal/` | DTPG | ✅ | — | — | |
| Fig A7 | Full Pareto 8env | `fig_full_pareto_8env/` | D--- | ✅ | ✅ | ~94% | **NEW** needs-gen |
| Fig A8 | Cost breakdown | `fig_cost_breakdown/` | D--- | ✅ | ✅ | ✅ | **NEW** needs-gen |

## Appendix Tables (appendix.tex)

| Paper Ref | Label | Folder | DTPG | Qwen3 | Phi | Llama | Notes |
|-----------|-------|--------|:----:|:-----:|:---:|:-----:|-------|
| Table A0 | AUC | `fig_auc_hierarchy/` | DTPG | ✅ | — | — | |
| Table A1 | Feature LASSO | `fig4_feature_heatmap/` | DTPG | ✅ | — | — | |
| Table A2 | LLM features | `fig5_llm_ablation/` | DTPG | ✅ | — | — | |
| **Table A3** | **Cost components** | `tab_cost_components/` | DT-- | ✅ | ✅ | ✅ | **NEW** |
| Table A4 | P1 temporal | `fig_p1_temporal_shift/` | DTPG | ✅ | R | R | |
| **Table A5** | **P3 signal identity** | `tab_signal_identity/` | DT-- | ✅ | — | — | **NEW** |
| **Table A6** | **Multi-bb signals** | `tab_multi_backbone_signal/` | DT-- | ✅ | ✅ | ✅ | **NEW** 157 rows |
| **Table A7** | **Cross-bb results** | `tab_multi_backbone_results/` | DT-- | — | ✅ | ~94% | **NEW** 156 rows |
| Table A8 | Significance | `tab_significance/` | DTPG | ✅ | TODO | TODO | Needs multi-backbone bootstrap |
| Table A9 | InfoPoor/Rich | `fig_controlled_reversal/` | DTPG | ✅ | — | — | |
| — | Prompt template | `tab_prompt_template/` | ---- | TODO | — | — | Extract from code |

## Other Existing Folders

| Folder | DTPG | Purpose |
|--------|:----:|---------|
| `tab_env_info_structure/` | DTPG | Env info structure table |
| `tab_method_classification/` | DTPG | Method classification table |
| `tab_diagnostic_results/` | DTPG | Diagnostic env results |
| `tab_appendix_results/` | DTPG | Appendix env results |
| `tab_signal_discovery/` | DTPG | Signal discovery summary |
| `fig_bsw_vs_rho/` | D-PG | BSW cost vs rho scatter |
| `fig_coverage_proxy/` | D-PG | Coverage proxy analysis |
| `fig_stratified_reversal/` | D-PG | Stratified reversal analysis |
| `generate_all_csvs.py` | — | CSV generation master script |

---

## Pending Experiments

| ID | Experiment | File | Target Folder | Blocked By |
|----|-----------|------|---------------|------------|
| P1 | Exp 3: Cross-Optimizer | `pending/exp3_cross_optimizer.md` | `tab_multi_backbone_signal/` | Config + SLURM |
| P2 | Exp 4: Budget Sensitivity | `pending/exp4_budget_sensitivity.md` | `fig_hyperparam_sensitivity/` | Config + SLURM |
| P3 | GPT-4o Signal Discovery | `pending/gpt4o_signal_discovery.md` | `tab_multi_backbone_signal/` | OpenAI API key |
| P4 | Llama CB TWExpress | `pending/llama_cb_twexpress.md` | `tab_multi_backbone_results/` | 4 methods x 3 seeds |
| P5 | Gate Threshold Sweep | `pending/gate_threshold_sweep.md` | `fig_hyperparam_sensitivity/` | tau override in code |

---

## Items Needing generate.py (data ready, script missing)

| Folder | What's needed | Priority |
|--------|--------------|:--------:|
| `fig_entropy_bin/` | Grouped bar chart from data.csv | High |
| `fig_pi_axis_diagram/` | TikZ or matplotlib horizontal axis diagram | Medium |
| `fig_multi_backbone_heatmap/` | 3-panel heatmap from data.csv | High |
| `fig_multi_backbone_sr_compare/` | Grouped bar chart from data.csv | High |
| `fig_full_pareto_8env/` | 2x4 Pareto grid from data.csv | High |
| `fig_cost_breakdown/` | Stacked bar chart from data.csv | Medium |
| `fig_case_study/` | Trajectory visualization (complex data join first) | Low |

---

## Multi-Backbone Data Completeness

| Model | Step 0+1 | Bounds | CB | DIAL | Total | % |
|-------|:--------:|:------:|:--:|:----:|:-----:|:-:|
| **Qwen3-4B** | ✅ 8/8 | ✅ | ✅ | ✅ | — | 100% |
| **Phi-3.5-mini** | ✅ 8/8 | ✅ 72/72 | ✅ 144/144 | ✅ 24/24 | 240/240 | **100%** |
| **Llama-3.1-8B** | ✅ 8/8 | ✅ 72/72 | ~130/144 | ✅ 24/24 | ~226/240 | **~94%** |

Missing Llama: TWExpress CB (auq, cats, corefine, s1_budget) x 3 seeds.
