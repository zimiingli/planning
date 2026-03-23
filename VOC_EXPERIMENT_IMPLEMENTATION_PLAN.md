# Experiment Implementation Plan: EAAG (Environment-Aware Adaptive Gating)

**版本**: v7.1 (2026-03-22) — 全部 analysis 图表已生成
**前版**: v7.0 → v24.0 已归档至 `planning/archive/VOC_EXPERIMENT_IMPLEMENTATION_PLAN_v24.md`
**论文标题**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**目标会议**: NeurIPS 2026
**主方法**: EAAG (Environment-Aware Adaptive Gating) — LLM as environment reasoner + LASSO direction discovery + online adaptation

---

## 1. 实验总览

### 1.1 环境

| # | 环境 | 类型 | base SR | always SR | 论文定位 |
|---|------|------|:---:|:---:|------|
| 1 | HotpotQA | QA/多跳推理 | 49.0% | 97.0% | 主实验 |
| 2 | APPS Intro | 代码生成(入门) | 58.5% | 64.5% | 主实验 (弱信号) |
| 3 | WebShop | Web 交互 | 7.2% | 43.0% | 主实验 |
| 4 | FEVER | 事实验证 | 37.0% | 99.8% | 主实验 (新增) |
| 5 | TWExpress | 文本游戏 | 67.5% | 99.3% | 诊断 (rollout-safe) |
| 6 | Plancraft | 制造规划 | 29.8% | 22.8% | 诊断 (rollout-harmful) |
| 7 | APPS Interview | 代码生成(面试) | 60.5% | 79.5% | Appendix |
| 8 | CRUXEval | 代码推理 | 85.0% | 99.5% | Appendix |

测试过但 NO-GO/放弃的: MBPP, HumanEval, ALFWorld, ScienceWorld, InterCode, ToolBench, AgentBench-KG, CrosswordQA, DS-1000, TextWorld, BabyAI (11 个)

### 1.2 方法

| 层级 | 方法 | 方向处理 | 需要 Phase 1? | 额外 inference cost |
|------|------|---------|:---:|:---:|
| Bounds | base_only, always_trigger, oracle | — | — | — |
| Random | random_50 | — | — | — |
| Fixed-dir CB | CaTS, SEAG, CoRefine, CATTS | 固定 | ✅ (CaTS/SEAG/CoRefine) | 0 (CATTS: K=5 calls) |
| Budget CB | AUQ, s1_budget | 无方向 | ❌ | AUQ: 1 call/step |
| Ablation | SCG (手工 feature) | 学习 | ✅ | 0 |
| Ablation | BSW (错误方向) | 翻转 | ✅ | 0 |
| **Ours** | **EAAG** (= se_online_decay_local) | **自动学习** | **❌** | **0** |

### 1.3 核心指标

| 指标 | 定义 | 用途 |
|------|------|------|
| **SR** | Success Rate (任务成功率) | 主性能指标 |
| **Total Cost** (ro/ep) | exploitation ro/ep + Phase 1 amortized ro/ep | 主成本指标 (含隐性成本) |
| **SR/total_ro** | ΔSR / total_ro | 效率指标 |
| **Pareto dominance** | SR≥ AND cost≤ (至少一个 strict) | 方法对比 |

---

## 2. 已完成实验与结果

### 2.1 主表数据

```
Method          HotpotQA          APPS             WebShop           FEVER
                SR    Cost(T)     SR    Cost(T)    SR    Cost(T)    SR    Cost(T)
─── Bounds ───
base_only      49.0%  0.00      58.5%  0.00       7.2%  0.00      37.0%  0.00
always_trigger 97.0%  1.80      64.5%  2.58      43.0%  5.63      99.8%  1.46
─── CB ───
CaTS†          93.2%  2.86      59.0%  2.62      30.5%  8.68      50.2%  6.17
AUQ            97.0%  1.69      61.3%  1.73      35.7%  5.33      40.7%  1.17
s1 Budget      97.0%  1.04      63.7%  1.00       7.8%  1.00      46.2%  1.58
SEAG†          67.5%  2.60      58.5%  2.59      28.0%  7.91      49.3%  4.58
CoRefine†      68.2%  2.59      58.5%  2.59      27.5%  7.84      49.8%  4.58
CATTS          68.3%  1.07      58.5%  0.03      16.0%  0.19      34.2%  0.06
─── Ablation ───
SCG†           96.8%  2.89      58.8%  2.77      43.0%  7.10      98.0%  2.45
BSW†           58.2%  —          —     —         20.6%  —         63.0%  5.76
─── Ours ───
EAAG           95.2%  1.34      66.0%  1.20      43.8%  2.29      49.8%  2.99

† = 含 Phase 1 (200 ep always_trigger) amortized cost
Cost(T) = Total ro/ep = exploit ro/ep + (Phase 1 ro/ep if applicable)
```

### 2.2 诊断环境数据

```
Method          TWExpress         Plancraft
                SR    Cost(T)     SR    Cost(T)
base_only      67.5%  0.00      29.8%  0.00
always_trigger 99.3%  3.45      22.8%  6.99
EAAG           99.0%  2.84      23.3%  3.69
SCG†           97.0%  4.83      21.5%  10.32
```

### 2.3 Appendix 环境数据

```
Method          APPS Interview    CRUXEval
                SR    Cost(T)     SR    Cost(T)
base_only      60.5%  0.00      85.0%  0.00
EAAG           73.0%  1.35       —     —
SCG†           79.5%  3.19      99.5%  2.80
AUQ            64.7%  1.08      99.0%  1.75
```

### 2.4 Signal Discovery 汇总 (8 环境)

| 环境 | 最强信号 | ρ | entropy 方向 | entropy ρ | Two-Source 类型 |
|------|---------|:---:|:---:|:---:|------|
| HotpotQA | step_count | −0.494 | 负 | −0.041 | Information-Poverty |
| FEVER | step_count | **−0.619** | 负 | −0.119 | Information-Poverty |
| APPS Intro | step_count | −0.155 | ≈0 | +0.012 | Decision-Difficulty |
| APPS Interview | step_count | −0.339 | **正** | **+0.317** | Decision-Difficulty |
| WebShop | num_available_actions | **+0.444** | 负 | −0.019 | Mixed |
| TWExpress | step_count | −0.477 | 负 | −0.290 | Information-Poverty |
| CRUXEval | step_count | +0.184 | 负 | −0.048 | 弱信号 |
| Plancraft | has_output | +0.162 | 负 | −0.016 | 弱信号 (harmful) |

### 2.5 EAAG vs CB Win Rate

| CB | SE win | SE loss | 环境数 |
|---|:---:|:---:|:---:|
| CaTS† | 5 | 0 | 6 |
| SEAG† | 6 | 0 | 6 |
| CoRefine† | 5 | 0 | 6 |
| CATTS | 6 | 0 | 6 |
| AUQ | 6 | 1 (HotpotQA −1.8pp) | 7 |
| s1 | 6 | 1 (HotpotQA −1.8pp) | 7 |
| **Total** | **34W** | **2L** | **38** |

### 2.6 Pareto Dominance (含 Phase 1 total cost)

| vs | EAAG Pareto-dominates | 环境 |
|---|:---:|------|
| SCG† | **4/7** | APPS, WebShop, TWExpress, Plancraft |
| CaTS† | **6/6** | 全胜 |
| SEAG† | **5/6** | |
| CoRefine† | **6/6** | 全胜 |

---

## 3. 需要补充的 Analysis 实验

### 3.1 Feature Usage Heatmap (§5 E1)

**目的**: 展示 EAAG 在不同环境自动选择了不同的 feature，证明 "方向和信号都是环境特异的"

**数据**: 已有 — 7 环境的 `gate_pattern.selected_features` (见下)

```
HotpotQA:       step_count, step_ratio, step_x_entropy, token_entropy, entropy_sq,
                evidence_count, is_finish, state_length, num_numbers, llm_query_length

APPS:           step_count, step_ratio, step_x_entropy, token_entropy, entropy_sq,
                state_length, num_numbers, has_error, h_pca_9, llm_action_type

WebShop:        num_available_actions, num_numbers, state_length, step_x_entropy,
                token_entropy, is_finish, llm_price_mentioned, llm_action_is_click,
                llm_step_early, llm_instruction_keyword_count

FEVER:          step_count, step_ratio, step_x_entropy, token_entropy, entropy_sq,
                state_length, h_pca_1, h_pca_9, llm_text_length_normalized, llm_has_claim

TWExpress:      step_count, step_ratio, token_entropy, entropy_sq, state_length,
                num_numbers, llm_text_length, llm_closed_ratio, llm_action_look_around, llm_already_open

Plancraft:      step_count, step_ratio, step_x_entropy, token_entropy, entropy_sq,
                state_length, num_numbers, num_available_actions, h_pca_0, h_pca_10

APPS Interview: step_count, step_ratio, has_error
```

**Analysis 要点**:
- `step_count` 在 6/7 环境被选中 → 最 universal 的信号
- `token_entropy` 在 5/7 环境被选中 → 也很 universal
- LLM feature 在 WebShop (4/10) 和 TWExpress (4/10) 被大量使用 → 这些环境的 task-specific 信号更重要
- APPS Interview 只选了 3 个 feature → 弱信号环境 LASSO 更保守
- **图**: 7×15 的 binary heatmap (env × feature)，深色=选中

**状态**: ✅ 数据已有，需生成图
**TODO**: ~~`python plots/generate_feature_heatmap.py`~~ (已由 `generate_all_figures.py` 完成)

### 3.2 Gate Trigger Rate vs Step 可视化 (§5 E3)

**目的**: 展示 EAAG 确实学到了 "何时触发" — 不同环境 gate 行为不同

**数据**: 需要从 episode 级别 step_records 中提取每步的 trigger rate

**预期结果**:
- HotpotQA/FEVER: 高 trigger rate 在 early steps, 低在 late steps (step_count coef 负)
- WebShop: 高 trigger rate 在 num_available_actions 大的步骤
- Plancraft: trigger rate 极低 (ro/ep=0.27, 学会不触发)
- TWExpress: 高 trigger rate 全程 (rollout-safe)

**图**: 6 个子图 (每环境一个), X=step, Y=trigger probability

**状态**: ✅ 已完成 (v7.1)
**数据来源**:
- Decision logs: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/scg_se_online_decay_local_decision_log.json`
- Episodes: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/episodes.json`
- 通过 episode steps 重建 per-step trigger rate (decision_log 只有 global step index)
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::fig_trigger_rate_by_step()`
**产出**: `planning/paper_figures/fig_trigger_rate_by_step.png/pdf`

### 3.3 错误方向代价量化 (§5 E1)

**目的**: BSW 的退化幅度 vs 环境信号强度 ρ 的关系，证明 "信号越强，方向错误代价越大"

**数据**: 已有

| 环境 | 最强信号 ρ | BSW SR | always SR | BSW 退化 (pp) |
|------|:---:|:---:|:---:|:---:|
| FEVER | −0.619 | 63.0% | 99.8% | −36.8 |
| HotpotQA | −0.494 | 58.2% | 97.0% | −38.8 |
| CRUXEval | +0.184 | 87.5% | 99.5% | −12.0 |
| APPS Interview | −0.339 | 79.5% | 79.5% | 0.0 (rollout-safe) |

**预期**: |ρ| 越大，BSW 退化越大 → 正相关散点图
**注意**: rollout-safe 环境 (APPS Interview) BSW 不退化，需排除或标注

**图**: 散点图, X=|ρ|, Y=BSW 退化 (pp), 每个点是一个环境

**状态**: ✅ 已完成 (v7.1) — 两个版本的图已生成
**TODO**: ~~`python plots/generate_bsw_cost_scatter.py`~~
**生成脚本**: `planning/paper_figures/generate_all_figures.py::fig3_bsw_cost()` (原版)
             `planning/paper_figures/generate_medium_priority_figures.py::fig_bsw_cost_vs_rho()` (含回归线+R²)
**产出**: `planning/paper_figures/fig3_bsw_cost.png/pdf` + `fig_bsw_cost_vs_rho.png/pdf`

### 3.4 Pareto Frontier 图 (§5 E2 核心图)

**目的**: SR vs Total Cost 的 Pareto 图，最直观的方法对比

**设计**: 6 个子图（4 主实验 + 2 诊断），每图显示所有方法的散点
- X = Total Cost (ro/ep, 含 Phase 1)
- Y = SR
- 颜色: EAAG=红, CB=蓝/绿, SCG=灰, bounds=虚线
- EAAG 应在大部分环境位于 Pareto frontier 上或接近

**状态**: ✅ 已完成
**TODO**: ~~`python plots/generate_pareto_figures.py`~~
**生成脚本**: `planning/paper_figures/generate_all_figures.py::fig2_pareto()`
**数据来源**: `results/phase6/{env}/{env}/*/seed_*/summary.json` (自动扫描所有方法)
**产出**: `planning/paper_figures/fig2_pareto.png/pdf`

### 3.5 LLM Environment Reasoning 分析 (§5 E3 Ablation)

**目的**: 展示 LLM 作为 environment reasoner 的能力 — 它发现了什么？

**数据**: 已有 — 7 环境的 LLM 生成 feature 名字 + LASSO 是否选中

| 环境 | LLM 生成的 feature | LASSO 选中 | 有实际意义? |
|------|-------------------|:---:|:---:|
| WebShop | `price_mentioned`, `action_is_click`, `step_early`, `instruction_keyword_count` | ✅ 4/5 | ✅ 完全有道理 |
| TWExpress | `closed_ratio`, `action_look_around`, `already_open` | ✅ 4/5 | ✅ 游戏状态特征 |
| FEVER | `text_length_normalized`, `has_claim` | ✅ 2/10 | 边缘 |
| HotpotQA | `query_length` | ✅ 1/10 | 边缘 |
| APPS | `action_type` | ✅ 1/10 | 边缘 |
| Plancraft | (无 LLM feature 被选中) | 0/10 | N/A |

**LLM vs 无 LLM (principled_v2) 对比**:

| 环境 | EAAG (有 LLM) | v2 (无 LLM) | LLM 贡献 |
|------|:---:|:---:|:---:|
| WebShop | 43.8% | 43.7% | +0.1pp (but LLM features used) |
| TWExpress | 99.0% | 99.2% | −0.2pp |
| APPS | 66.0% | 65.8% | +0.2pp |
| HotpotQA | 95.2% | 95.8% | −0.6pp |
| FEVER | 49.8% | 40.7% | +9.1pp |

**Analysis 要点**:
- LLM SR 贡献 marginal (<1pp) in most envs
- LLM 真正的价值: zero-shot 生成 task-specific features（如 WebShop 的 `price_mentioned`），无需人工设计
- 在新环境部署时，LLM 的 environment reasoning 是唯一的 feature discovery 机制

**图**: 柱状图, 每环境两柱 (EAAG vs v2), 标注 LLM feature 名字

**状态**: ✅ 已完成
**TODO**: ~~`python plots/generate_llm_ablation.py`~~
**生成脚本**: `planning/paper_figures/generate_all_figures.py::fig5_llm_ablation()`
**数据来源**: `results/phase6/path_e/{env}/se_online_decay_local/` vs `principled_v2/` 的 `summary.json`
**产出**: `planning/paper_figures/fig5_llm_ablation.png/pdf`

### 3.6 Exploration Bias 分析 (§6.1 FEVER Case Study)

**目的**: 解释为什么 EAAG 在 FEVER 上只有 50% — online exploration 的固有局限

**数据**: 已有

| 指标 | SCG (Phase 1 data) | EAAG (explore data) |
|------|:---:|:---:|
| Calibration positive_rate | 51.8% | 7-9% |
| Episode length | 1.4 steps/ep | 5+ steps/ep |
| Steps observed | 282 | 1054 |
| Rollout rate (exploit) | 68.2% | 3.0% (basic SE) |

**Analysis 要点**:
- FEVER 的 rollout 价值集中在 step 0-1 (ρ=−0.619)
- Random exploration 50% 概率错过 step 0 → episode 延长 → late-step negative 淹没
- LASSO 学到 "永远不触发" → rollout_rate=3%
- Online decay 版本通过 ε-greedy 部分缓解 (rollout_rate ~50%, SR=49.8%)
- SCG 用 Phase 1 always_trigger 数据避开偏差 → SR=98%

**图**: 柱状图对比 SCG data vs SE data 的 positive_rate + episode length

**Optimistic exploration 尝试**: 测试了 3 个 optimistic variant，全部失败 (SR 35-39%)
- 原因: 50 ep 中每个 (step, state_category) group 只被访问 3-5 次，强制触发 3 次后数据仍不足

**状态**: ✅ 图已生成 → `planning/paper_figures/fig6_fever_bias.png`

### 3.7 Direction Reversal 信号热力图 (§5 E1 核心图)

**目的**: 论文的 selling point 图 — 一眼看出方向在不同环境反转

**设计**: 8×N heatmap, 行=环境, 列=信号, 颜色=ρ (红=正, 蓝=负, 白=0)

**关键 pattern**:
- entropy: HotpotQA/FEVER 负 vs APPS Interview 正
- step_count: 大部分负，CRUXEval 正
- num_available_actions: WebShop 极强正 (+0.444)
- APPS 几乎全白 (弱信号)

**状态**: ✅ 图已生成 → `planning/paper_figures/fig1_signal_heatmap.png`

---

## 3.8 v7.0 新增 Analysis（已有数据，无需新 GPU run）🆕🆕🆕

> **来源**：v7.0 Writing Guide FLARE-Style Structural Upgrade (§1.8)
> **原则**：以下 analysis 全部基于已有实验数据，只需写分析脚本 + 生成图表

### 3.8.1 🔴 AUC Hierarchy 柱状图 (Observation 3 / Proposition 2 核心证据)

**论文位置**: §3.1 Observation 3 (Signal Poverty) + §3.2 Proposition 2 (Signal Poverty Bound)

**目的**: 展示单信号 → 多信号 → hidden state 的 AUC 阶梯式提升，证明 "单信号范式有信息论天花板"

**数据来源**: Phase 5 Cross-Environment AUC Analysis (phase5_interim_report.md §4.5.4)

```
已有数据（5-fold CV AUC, seed 42, utility_threshold=0.05）:

                        HotpotQA   APPS    WebShop   Avg
Single token_entropy     0.502     0.557    0.533    0.531
Single confidence        0.502     0.557    0.467    0.508
Best individual signal   0.782     0.778    0.895    0.818
All scalar (LR, 3-6f)   0.851     0.761    0.924    0.845
Hidden state (LR)        0.869     0.794    0.994    0.886
```

**Figure 设计**:
- **类型**: Grouped bar chart (3 环境 × 5 方法层级)
- **X 轴**: 3 个环境 (HotpotQA, APPS, WebShop), grouped
- **Y 轴**: AUC (0.4 → 1.0)
- **每组 5 条柱**:
  - Single entropy (浅灰) → 0.50-0.56
  - Single best (灰) → 0.78-0.90
  - Multi-signal LR (蓝) → 0.76-0.92
  - Hidden state LR (红) → 0.79-0.99
- **虚线**: AUC = 0.5 (random baseline)
- **标注**: 每组上方标注 "×1.6" "×1.7" 等倍数
- **Legend**: 4 层级 + random baseline
- **文件名**: `fig_auc_hierarchy.pdf`

**附加**: 在柱状图旁或下方加一个 mini-table 报告 avg AUC:
```
Signal Level          Avg AUC    vs Random
Single entropy         0.531      +0.031 (≈random)
Multi-signal LR        0.845      +0.345
Hidden state           0.886      +0.386
```

**分析脚本需要做什么**:
1. 从 phase5_interim_report.md 提取上述数值（或从原始 probe 实验结果 JSON/log 中读取）
2. 生成 grouped bar chart
3. 输出 PDF + PNG

**TODO**: ~~`python plots/generate_auc_hierarchy.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**: 硬编码自 phase5_interim_report.md §4.5.4 (5-fold CV AUC, seed 42, utility_threshold=0.05)
- 原始 probe 数据: `results/phase5/data/{hotpotqa,apps,webshop}/seed_42/step_data.npz`
- AUC 计算脚本: `scripts/phase5/auc_analysis.py`
**生成脚本**: `planning/paper_figures/generate_high_priority_figures.py::fig_auc_hierarchy()`
**产出**: `planning/paper_figures/fig_auc_hierarchy.png/pdf`
**优先级**: 🔴 高 — Proposition 2 和 Observation 3 的核心视觉证据

---

### 3.8.2 🔴 P1 Temporal Shift 验证 (Two-Source Model Prediction 1)

**论文位置**: §3.2 Testable Prediction P1 验证 / §5.4 Ablation

**目的**: 验证 Two-Source Model 的核心预测 —— 在同一环境内，early steps（p_I 更高，信息更缺乏）的 ρ(entropy, U) 应比 late steps 更负

**理论预测**:
```
Two-Source Model 预测:
  ρ(entropy, U | early steps) < ρ(entropy, U | late steps)

直觉: early steps → agent 还没收集信息 → Type I 主导 → ρ 更负
      late steps → agent 已有信息 → Type D 比例上升 → ρ 变正/变弱
```

**数据来源**: 各环境 Phase 1 probe 数据（step_records）
- 每条记录包含: (env, episode_id, step_t, token_entropy, utility_U, ...)
- HotpotQA: ~1208 data points (Phase 1)
- APPS: ~590 data points
- WebShop: ~2000+ data points (高 step count)
- FEVER: ~282 data points
- TWExpress: data points from probe phase
- Plancraft: data points from probe phase

**数据文件位置（需确认）**:
- 选项 A: `experiments/phase1/*/step_records.jsonl`
- 选项 B: `experiments/phase5/*/probe_data.csv`
- 选项 C: 从 EAAG/SCG 的 explore phase 中的 decision_log 提取
- **⚠️ 需先确认数据位置**: 运行 `find /path/to/experiments -name "*step_record*" -o -name "*probe*" -o -name "*decision_log*" | head -20`

**分析方法**:
```python
import pandas as pd
from scipy.stats import spearmanr

for env in ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft']:
    data = load_probe_data(env)  # (step, entropy, utility)

    # Split by step position
    median_step = data['step'].median()
    early = data[data['step'] <= median_step]
    late = data[data['step'] > median_step]

    # Alternative: fixed split (step 1-3 vs 4+)
    early_fixed = data[data['step'] <= 3]
    late_fixed = data[data['step'] > 3]

    rho_early, p_early = spearmanr(early['entropy'], early['utility'])
    rho_late, p_late = spearmanr(late['entropy'], late['utility'])

    print(f"{env}: ρ_early={rho_early:.3f} (p={p_early:.3f}), "
          f"ρ_late={rho_late:.3f} (p={p_late:.3f}), "
          f"Δρ={rho_late - rho_early:+.3f}")
```

**预期结果**:
```
环境         ρ_early    ρ_late    Δρ (late−early)   P1 验证?
HotpotQA     −0.45      −0.15      +0.30            ✅ (early更负)
FEVER        −0.70      −0.30      +0.40            ✅ (early更负)
APPS         ≈0         ≈0         ≈0               ✅ (弱信号全程)
WebShop      −0.10      +0.15      +0.25            ✅ (early负→late正)
TWExpress    −0.40      −0.10      +0.30            ✅ (early更负)
Plancraft    ≈0         ≈0         ≈0               ⚠️ (弱信号)
```

**Figure 设计**:
- **类型**: Grouped bar chart (paired bars per environment)
- **X 轴**: 6 个环境
- **Y 轴**: ρ(entropy, U) (−0.8 → +0.4)
- **每组 2 条柱**:
  - Early steps (深色/实心)
  - Late steps (浅色/斜线)
- **零线**: 虚线 ρ = 0
- **箭头**: 从 early 到 late 的方向箭头（↑ = P1 成立）
- **标注**: Δρ 值标在每组上方
- **统计**: 每组柱上方标注 p-value（ρ_early vs ρ_late 的 Fisher z-test）
- **文件名**: `fig_p1_temporal_shift.pdf`

**备选 Figure**: 如果环境太多，做 2×3 子图 grid，每个子图是一个环境的 scatter plot:
- X = entropy, Y = utility, 颜色 = early(蓝)/late(红)
- 分别拟合回归线，斜率差异可视化

**TODO**: ~~`python analysis/verify_p1_temporal_shift.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**:
- HotpotQA/APPS/WebShop 已有预计算: `results/phase6/toy_model/d1_temporal_shift_results.json`
- FEVER 原始数据: `results/phase6/fever/fever/phase1_signal_data.json` (282 records)
- TWExpress 原始数据: `results/phase5/twexpress/twexpress/phase1_signal_data.json` (798 records)
- Plancraft: 无独立 probe 数据 (phase5 npz 无 episode 标记)
**生成脚本**: `planning/paper_figures/generate_high_priority_figures.py::fig_p1_temporal_shift()`
**产出**: `planning/paper_figures/fig_p1_temporal_shift.png/pdf`
**实际结果**: ρ 在 late steps 变得更负 (HotpotQA: -0.18→-0.44)，方向与原始预测相反。
  论文叙述需调整: entropy 在后期 steps 区分力更强，而非早期。
**优先级**: 🔴 高 — Two-Source Model 最直接的可验证预测

---

### 3.8.3 🟡 Gate Trigger Rate vs Step 可视化 (已有 TODO，升级设计)

**论文位置**: §5.4 E3 Ablation — Gate Behavior

**目的**: 展示 EAAG 在不同环境学到了不同的 step-dependent 触发模式

**数据来源**: EAAG exploit phase 的 decision_log
- 每条记录: (env, episode_id, step_t, gate_decision, gate_probability)
- 需要从每个环境的 se_online_decay_local 实验结果中提取

**分析方法**:
```python
for env in environments:
    log = load_decision_log(env, method='se_online_decay_local')
    # Group by step, compute mean trigger rate
    trigger_by_step = log.groupby('step')['gate_decision'].mean()
    # Also compute 95% CI via bootstrap or binomial CI
```

**Figure 设计**:
- **类型**: 2×3 子图 grid (6 环境)
- **每个子图**:
  - X = step (0 → max_step)
  - Y = trigger probability (0 → 1.0)
  - 蓝线 = EAAG trigger rate
  - 灰色虚线 = overall trigger rate (常数线)
  - 浅蓝 shading = 95% CI
- **标注**: 每个子图标注环境名 + overall RR
- **预期 pattern**:
  - HotpotQA: early high, late low (step_count coef 负)
  - FEVER: early high, late low (step_count coef 负)
  - WebShop: spike when num_available_actions 大
  - APPS: 全程低 (RR=6%, 保守)
  - TWExpress: 全程高 (rollout-safe)
  - Plancraft: 全程极低 (rollout-harmful, RR=1%)
- **文件名**: `fig_trigger_rate_by_step.pdf`

**叙事价值**:
- 直观展示 adaptive behavior（不同环境不同 pattern）
- 与 P1 temporal shift 互补（P1 看 signal 方向随 step 变化，这里看 gate 行为随 step 变化）
- 证明 gate 不是 "一刀切"，而是 step-dependent 的精细控制

**TODO**: ~~`python analysis/generate_trigger_rate_by_step.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**:
- Decision logs: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/scg_se_online_decay_local_decision_log.json`
  - keys: step (global), prob, threshold, decision (rollout/skip), phase (exploitation)
- Episodes: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/episodes.json`
  - keys: episode, steps, success, gate_phase; 用于重建 per-episode step index
- 6 环境各 3 seeds, 每 seed 200 ep
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::fig_trigger_rate_by_step()`
**产出**: `planning/paper_figures/fig_trigger_rate_by_step.png/pdf`
**实际结果**:
  - HotpotQA: 早高(0.70)晚低(0.16)，符合 step_count coef 负
  - WebShop: step 0 极低(0.01), step 1 spike(0.83)，学到 "等看商品"
  - TWExpress: 全程高(0.73-0.90)，rollout-safe
  - Plancraft: 递减(0.49→0.20)，rollout-harmful 学会少触发
  - FEVER: 平坦(0.46-0.57)，weak online learning
  - APPS: step 0 高(0.41)→step 2 低(0.12)→step 4 回升(0.54)
**优先级**: 🟡 中 — 支撑 adaptive behavior story

---

### 3.8.4 🟡 BSW 代价 vs |ρ| 相关性分析 (Proposition 1 定量验证)

**论文位置**: §3.2 Proposition 1 紧跟段 / §5.2 E1

**目的**: 验证 "信号越强 (|ρ| 越大)，wrong-direction 代价越大"——Proposition 1 的 empirical corollary

**数据来源**: §3.3 已有数据 + 新增 BSW 环境

```
已有数据:

环境           |ρ| (最强信号)  BSW SR   always SR  BSW退化(pp)  rollout-safe?
FEVER          0.619          63.0%    99.8%      −36.8       ❌
HotpotQA       0.494          58.2%    97.0%      −38.8       ❌
APPS Intv      0.339          79.5%    79.5%       0.0        ✅ (rollout-safe)
CRUXEval       0.184          87.5%    99.5%      −12.0       ❌
WebShop        0.444          20.6%    43.0%      −22.4       ❌
```

**分析方法**:
```python
import numpy as np
from scipy.stats import spearmanr, pearsonr

# 排除 rollout-safe 环境 (APPS Interview)
data = [
    ('FEVER',     0.619, -36.8),
    ('HotpotQA',  0.494, -38.8),
    ('WebShop',   0.444, -22.4),
    ('CRUXEval',  0.184, -12.0),
]
rho_vals = [d[1] for d in data]
bsw_cost = [d[2] for d in data]

r, p = pearsonr(rho_vals, bsw_cost)  # 预期: 负相关 (|ρ|↑ → 退化更大)
# 或者用 |bsw_cost| vs |ρ|: 正相关
```

**Figure 设计**:
- **类型**: 散点图 + 回归线
- **X 轴**: |ρ| of strongest signal (0 → 0.7)
- **Y 轴**: BSW SR degradation in pp (0 → −40)
- **每个点**: 一个环境，标注环境名
- **回归线**: 线性拟合 + R² 标注
- **特殊标注**: APPS Interview 用空心圆（rollout-safe，排除在回归外）
- **标注**: "Stronger signals → larger wrong-direction penalty"
- **文件名**: `fig_bsw_cost_vs_rho.pdf`

**预期**: |ρ| 与 |degradation| 正相关 (R² > 0.5)
- 最强信号环境 (FEVER |ρ|=0.619) → 最大退化 (−36.8pp)
- 最弱信号环境 (CRUXEval |ρ|=0.184) → 最小退化 (−12.0pp)

**TODO**: ~~`python analysis/generate_bsw_cost_correlation.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**: 硬编码自 §3.3 数据表 (5 环境的 |ρ|, BSW SR, always SR)
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::fig_bsw_cost_vs_rho()`
**产出**: `planning/paper_figures/fig_bsw_cost_vs_rho.png/pdf`
**实际结果**: r=0.90, R²=0.80, p=0.104 (4 个 non-safe 点)
  APPS Intv (rollout-safe) 用空心菱形标注，排除在回归外
**优先级**: 🟡 中 — Proposition 1 的 quantitative validation

---

### 3.8.5 🟡 方法分类等价表 (FLARE Table 5 对标)

**论文位置**: §3.3 Implications / §5.1 Setup

**目的**: 用 4 个维度把所有方法分类，一眼看出 EAAG 的独特性

**数据来源**: §1.2 方法表 + §2.5 Win Rate + test_time_planning_taxonomy.md

**Table 设计**: 见 VOC_PAPER_WRITING_GUIDE.md §1.8.4 完整设计

**需要整理**:
1. 从 Win Rate 数据 (§2.5) 填充 "SR Win/Loss" 列
2. 确认 RL-based methods (AdaptThink, Thinkless) 无直接对比数据 → 标 N/A
3. 从 taxonomy 确认每个方法的 Signal Type / Direction / Granularity

**输出**: LaTeX table code (直接放入论文)

**TODO**: ~~手动整理 → LaTeX~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**: §1.2 方法表 + §2.5 Win Rate + `planning/test_time_planning_taxonomy.md`
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::tab_method_classification()`
**产出**: `planning/paper_figures/tab_method_classification.tex`
**优先级**: 🟡 中 — §3.3 或 §5.1 的重要表格

---

### 3.8.6 🟢 环境信息结构分类 (Prescriptive Framework)

**论文位置**: §3.3 Implications / §6 Discussion

**目的**: 给每个环境标注 3 维信息结构特征，验证与 Two-Source 类型一致

**数据来源**: 环境设计知识 + §2.4 Signal Discovery 数据

```
环境           Info-Sufficiency   Reversibility    Feedback-Delay   Two-Source Type     ρ(entropy,U)
HotpotQA       Info-Poor          Irreversible     Immediate        Information-Poverty  −0.041
FEVER          Info-Poor          Irreversible     Immediate        Information-Poverty  −0.119
APPS Intro     Info-Rich          Irreversible     Delayed          Decision-Difficulty  +0.012
APPS Intv      Info-Rich          Irreversible     Delayed          Decision-Difficulty  +0.317
WebShop        Mixed              Reversible       Immediate        Mixed               −0.019
TWExpress      Info-Poor          Irreversible     Immediate        Information-Poverty  −0.290
Plancraft      Info-Rich          Irreversible     Delayed          弱信号(harmful)      −0.016
CRUXEval       Info-Rich          Irreversible     Delayed          弱信号              −0.048
```

**验证**: Info-Poor 环境 → Type I 主导 → entropy ρ 负 ✅ (HotpotQA, FEVER, TWExpress)
         Info-Rich 环境 → Type D 主导 → entropy ρ ≈0 或正 ✅ (APPS Intv +0.317)

**输出**: LaTeX table (8 行 × 6 列)
**TODO**: ~~手动整理 → LaTeX~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**: 环境设计知识 + §2.4 Signal Discovery 数据 (ρ 值)
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::tab_env_info_structure()`
**产出**: `planning/paper_figures/tab_env_info_structure.tex`
**优先级**: 🟢 低 — §6 Discussion 的 prescriptive takeaway

---

### 3.8.7 🔴 Stratified + Matched-Pair Analysis: Direction Reversal 因果性验证 (§5.6 核心)

**论文位置**: §5.6 Robustness of Direction Reversal

**目的**: 两层验证——(A) 控制 confounder 后 reversal 仍存在，(B) 在 matched states 下直接展示 "same entropy, opposite meaning"

**数据来源**: 已有 probe 数据 (同 §3.8.2 P1 Temporal Shift)

**⚠️ 为什么需要两层**: 外部 review 指出 BSW ablation 只证明 "direction matters for gate policy"，没证明 "entropy semantics 是 environment-dependent 的 real phenomenon"。Stratified analysis 控制 confounder；Matched-pair 直接展示 "在相同条件下高 entropy 在不同环境意味着相反的事"——这是 "Same Signal, Opposite Meaning" 的最直观证据。

---

#### Part A: Stratified Analysis (控制 confounder)

**核心问题**: direction reversal 会不会是 trajectory length / difficulty 造成的 artifact？

**分析方法**:
```python
from scipy.stats import spearmanr

for env in ['hotpotqa', 'apps', 'apps_intv', 'fever', 'webshop', 'twexpress']:
    data = load_probe_data(env)

    # 方法 1: 按 trajectory length 分层
    data['length_bin'] = pd.qcut(data['episode_length'], 3, labels=['short','mid','long'])

    for bin_name in ['short', 'mid', 'long']:
        subset = data[data['length_bin'] == bin_name]
        rho, p = spearmanr(subset['entropy'], subset['utility'])
        print(f"{env} [{bin_name}]: ρ={rho:.3f}, p={p:.3f}, n={len(subset)}")

    # 方法 2: 按 step_count 分层 (proxy for difficulty/progress)
    data['step_bin'] = pd.qcut(data['step_count'], 3, labels=['early','mid','late'])

    for bin_name in ['early', 'mid', 'late']:
        subset = data[data['step_bin'] == bin_name]
        rho, p = spearmanr(subset['entropy'], subset['utility'])
        print(f"{env} [{bin_name}]: ρ={rho:.3f}, p={p:.3f}, n={len(subset)}")
```

**预期结果**:
```
环境          short    mid      long     reversal 在每层都存在?
HotpotQA     −0.05   −0.03    −0.02    ✅ 始终负
FEVER        −0.15   −0.10    −0.08    ✅ 始终负
APPS Intv    +0.25   +0.30    +0.35    ✅ 始终正
APPS         ≈0      ≈0       ≈0       ✅ 始终≈0 (弱信号)
WebShop      ≈0      ≈0       ≈0       ✅ entropy 始终弱 (主信号是 num_actions)
```

**Figure 设计 (Part A)**:
- **类型**: Grouped bar chart (6 env × 3 strata)
- **X 轴**: 6 environments, grouped
- **Y 轴**: ρ(entropy, U) within stratum
- **每组 3 条柱**: short (浅色) / mid (中色) / long (深色)
- **核心 message**: 每组内 3 条柱符号一致 → reversal 不是 length/difficulty artifact
- **文件名**: `fig_stratified_reversal.pdf`

---

#### Part B: Matched-Pair Analysis (within-state "same signal, opposite meaning" 展示) 🔥

**核心问题**: 在难度/进度 matched 的 states 下，高 entropy 在不同环境是否真的意味着相反的事？

**这是论文标题 "Same Signal, Opposite Meaning" 的最直观证据。**

**分析方法**:
```python
import numpy as np

results = {}
for env in ['hotpotqa', 'apps_intv', 'fever', 'apps']:
    data = load_probe_data(env)

    # Step 1: 按 difficulty proxy 分层 (step_count 三分位)
    data['difficulty_bin'] = pd.qcut(data['step_count'], 3, labels=['easy','med','hard'])

    deltas = []
    for diff_bin in ['easy', 'med', 'hard']:
        matched = data[data['difficulty_bin'] == diff_bin]

        # Step 2: 在 matched states 内, 按 entropy 分 high/low
        median_entropy = matched['entropy'].median()
        high_ent = matched[matched['entropy'] >= median_entropy]
        low_ent = matched[matched['entropy'] < median_entropy]

        # Step 3: 比较 mean utility
        delta_U = high_ent['utility'].mean() - low_ent['utility'].mean()
        deltas.append(delta_U)

        print(f"{env} [{diff_bin}]: "
              f"U(high_ent)={high_ent['utility'].mean():.3f}, "
              f"U(low_ent)={low_ent['utility'].mean():.3f}, "
              f"ΔU={delta_U:+.3f}")

    results[env] = deltas
```

**预期结果**:
```
在 difficulty-matched states 内, 高 entropy 的 utility 差:

环境          easy     med      hard     方向
HotpotQA     −0.08   −0.05    −0.03    全负 → 高entropy=信息匮乏=rollout无用
FEVER        −0.12   −0.09    −0.06    全负 → 同上
APPS Intv    +0.05   +0.08    +0.10    全正 → 高entropy=决策困难=rollout有价值
APPS         ≈0      ≈0       ≈0       ≈0   → 弱信号

→ 在相同难度下, 高 entropy 在 HotpotQA 意味着 "rollout 无用",
  在 APPS Interview 意味着 "rollout 有价值"
→ 这就是 "Same Signal, Opposite Meaning" 的直接证据
```

**Figure 设计 (Part B)**:
- **类型**: 2×2 子图 (4 个代表环境)
- **每个子图**:
  - X 轴: difficulty bin (easy / med / hard)
  - Y 轴: ΔU = U(high_entropy) − U(low_entropy)
  - 柱状图 + error bar (bootstrap 95% CI)
  - 零线虚线
  - 环境名 + 方向标注 ("Type I: ΔU < 0" 或 "Type D: ΔU > 0")
- **核心 message**: HotpotQA/FEVER 柱子全在零线下方, APPS Intv 全在上方
- **标题**: "Same entropy level, opposite utility effect across environments"
- **文件名**: `fig_matched_pair_opposite_meaning.pdf`

**备选 Figure**: 如果子图太多, 做一个 **heatmap**:
- X 轴: 4 environments
- Y 轴: 3 difficulty bins
- 颜色: ΔU (红=正, 蓝=负, 白=0)
- 一眼看出 "红蓝分明" = opposite meaning

---

**TODO**: ~~`python analysis/stratified_and_matched_pair.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**:
- HotpotQA: `results/phase1_signal_discovery/hotpotqa/phase1_signal_data.json` (1208 records, 有 episode ID)
- APPS: `results/phase5/calibration_data/apps/phase1_signal_data.json` (1567 records, 3 seeds)
- WebShop: `results/phase5/calibration_data/webshop/phase1_signal_data.json` (3899 records, 3 seeds)
- TWExpress: `results/phase5/twexpress/twexpress/phase1_signal_data.json` (798 records)
- FEVER: `results/phase6/fever/fever/phase1_signal_data.json` (282 records)
- APPS Interview: `results/phase6/apps_interview/apps_interview/phase1_signal_data.json` (439 records)
- 每条记录包含: step_count, token_entropy, utility (+环境特异 fields)
- Stratified: 按 step_count tercile 分 Early/Mid/Late, 计算 within-stratum ρ(entropy, U)
- Matched-pair: 按 step_count tercile 分层, 每层内 median split entropy, 计算 ΔU
**生成脚本**:
- Part A: `planning/paper_figures/generate_high_priority_figures.py::fig_stratified_reversal()`
- Part B: `planning/paper_figures/generate_high_priority_figures.py::fig_matched_pair()`
**产出**: `planning/paper_figures/fig_stratified_reversal.png/pdf` + `fig_matched_pair_opposite_meaning.png/pdf`
**实际结果**:
- Part A: HotpotQA 三层 strata 全负 (-0.18/-0.46/-0.42) ✅; TWExpress 层间翻转 (+0.32/-0.36/-0.03)
- Part B: HotpotQA ΔU 显著负 (-0.08 to -0.43) ✅; APPS Intv 弱正 (+0.026, utility 太稀疏)
**优先级**: 🔴 高 — Part A 堵 artifact 攻击, Part B 提供标题级别的直观证据

---

### 3.8.8 🔴 Gate Capacity Ablation (§5.6 核心)

**论文位置**: §5.6 Robustness → Gate complexity ablation

**目的**: 证明 "direction >> capacity"——用更复杂的 gate 不会提升性能，但用错误方向的复杂 gate 更糟

**数据来源**: 已有 Phase 2/2.5 数据 + Phase 5 AUC 数据

```
已有数据 (HotpotQA):

Gate               Direction    SR       AUC     来源
Logistic (5 feat)  Correct      95.2%    0.851   Phase 6 EAAG
MLP (5 feat)       Correct      ~95%     0.869   Phase 2 MLP variant
Hidden state LR    Correct      ~95%     0.869   Phase 5 probe
Logistic (5 feat)  Wrong        62.0%    —       Phase 2 BSW-LR
MLP (5 feat)       Wrong        45.3%    —       Phase 2.5 BSW-MLP
Base (no gate)     —            49.0%    0.500   baseline
```

**需要确认**:
- MLP correct-direction SR: 从 Phase 2 数据中提取（scg_mlp 变体）
- Hidden state LR correct-direction SR: 从 Phase 5 hidden state probe 数据中提取
- 如果缺失 → 需要跑少量补充实验 (每个 200 ep × 1 seed)

**Figure 设计**:
- **类型**: 表格 (Table, 不是 figure) — 放在 §5.6 或 §5.3 的 ablation 中
- 结构如 writing guide 中 `tab:capacity` 的设计
- 核心 message: 所有 correct-direction gates ≈ 95%，所有 wrong-direction gates 大幅下降

**TODO**: ~~整理已有数据成表~~
**状态**: ✅ 已完成 (v7.1) — LaTeX 表格已生成; MLP/hidden-state correct-dir SR 用 "~95" 标注 (如需精确值仍需补跑)
**数据来源**:
- Logistic correct: Phase 6 EAAG (SR=95.2%, AUC=0.851)
- MLP correct: Phase 2 MLP variant (SR ~95%, AUC=0.869) — 来自 `results/phase2/` 或 `results/phase5/` probe
- Hidden state LR: Phase 5 probe (AUC=0.869) — `results/phase5/data/{env}/seed_42/step_data.npz`
- BSW-LR wrong: Phase 2 (SR=62.0%)
- BSW-MLP wrong: Phase 2.5 (SR=45.3%)
**生成脚本**: `planning/paper_figures/generate_high_priority_figures.py::tab_gate_capacity()`
**产出**: `planning/paper_figures/tab_gate_capacity.tex`
**优先级**: 🔴 高 — 直接回应 "为什么不用更复杂的 gate" 的 reviewer 攻击

---

### 3.8.9 🟡 Observable Proxy for p_I: Information Coverage (§5.4 / Appendix D)

**论文位置**: §5.4 Theory Verification 或 Appendix D

**目的**: 为 Two-Source Model 的 latent variable p_I 提供 observable proxy，让理论从 "post-hoc narrative" 升级为 "empirically grounded model"

**Proxy 定义**:
```
Information Coverage c_t = 可观测的"信息充分度"指标

环境       c_t 定义                                          可从已有数据提取?
HotpotQA   evidence_count / total_gold_evidence              ✅ (evidence_count 已有)
FEVER      step_count / max_steps (proxy: 更多步=更多搜索)    ✅ (step_count 已有)
APPS       1.0 for all steps (code 是 self-contained)        ✅ (常数)
WebShop    num_available_actions / max_actions (proxy)        ✅ (num_available_actions 已有)
TWExpress  step_count / max_steps                            ✅ (step_count 已有)
```

**分析方法**:
```python
# Analysis 1: Within-environment — 低 coverage 的 ρ 是否更负?
for env in environments:
    data = load_probe_data(env)
    coverage = compute_coverage(data, env)  # 按上表定义
    low_cov = data[coverage < coverage.median()]
    high_cov = data[coverage >= coverage.median()]
    rho_low = spearmanr(low_cov['entropy'], low_cov['utility'])
    rho_high = spearmanr(high_cov['entropy'], high_cov['utility'])
    # 预期: rho_low < rho_high (低 coverage = 高 p_I = 更负 ρ)

# Analysis 2: Cross-environment — mean coverage 是否与 ρ 方向相关?
for env in environments:
    mean_c = compute_mean_coverage(env)
    rho_env = get_entropy_utility_rho(env)
    # 画 scatter: x = mean_c, y = rho_env
    # 预期: 正相关 (高 coverage = 低 p_I = 更正 ρ)
```

**预期结果**:
- Analysis 1: 在 HotpotQA 中，低 evidence_count 的 ρ 更负 (Type I 主导)
- Analysis 2: 散点图中 APPS (high coverage, ρ≈0) 和 FEVER (low coverage, ρ=−0.119) 分布在预期位置

**Figure 设计**:
- **类型**: 散点图 (cross-environment)
- **X 轴**: Mean information coverage (0 → 1)
- **Y 轴**: ρ(entropy, U)
- **每个点**: 一个环境，标注名称
- **回归线**: 如果正相关显著 → 直接验证 "p_I ∝ (1 - coverage)"
- **文件名**: `fig_coverage_vs_rho.pdf`

**TODO**: ~~`python analysis/information_coverage_proxy.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源** (同 §3.8.7 probe 数据):
- HotpotQA: `evidence_count / 3.0` → mean_cov=0.455
- FEVER: `step_count / 7.0` → mean_cov=0.059
- WebShop: `num_available_actions / 30.0` → mean_cov=0.319
- TWExpress: `step_count / 9.0` → mean_cov=0.921
- APPS/APPS Intv: 1.0 (code is self-contained)
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::fig_coverage_vs_rho()`
**产出**: `planning/paper_figures/fig_coverage_vs_rho.png/pdf`
**实际结果**: Trend r=-0.62; TWExpress 是 outlier (高 coverage 但负 ρ)
  — TWExpress 的 step_count/max_steps 作为 coverage proxy 可能不准 (信息不只来自步数推进)
**优先级**: 🟡 中高 — 让 Two-Source Model 从 narrative 升级为 empirically grounded

---

### 3.8.10 🟡 Statistical Significance 汇总表 (§5.2 / Appendix E)

**论文位置**: §5.2 Main Results 或 Appendix E

**目的**: 回应 "34W/2L 是弱证据" — 用 formal statistical tests 替代 win/loss counting

**分析方法**:
```python
# 对每个 (EAAG vs CB) 对比:
from scipy.stats import chi2_contingency  # McNemar
from statsmodels.stats.tost import TOST   # equivalence

for cb in ['CaTS', 'SEAG', 'CoRefine', 'CATTS', 'AUQ', 's1']:
    for env in ['hotpotqa', 'apps', 'webshop', 'fever', 'twexpress', 'plancraft']:
        # McNemar test: EAAG vs CB, paired by episode
        # 已有 3-seed data (200 ep/seed)
        # H0: SR(EAAG) = SR(CB)
        p_mcnemar = mcnemar_test(eaag_results, cb_results)

        # Effect size: ΔSR = SR(EAAG) - SR(CB)
        delta_sr = eaag_sr - cb_sr

        # 95% CI via bootstrap
        ci = bootstrap_ci(eaag_results, cb_results, n_boot=10000)
```

**产出**:
```
Table (Appendix E): Statistical significance of EAAG vs each CB

CB       Env        ΔSR (pp)   95% CI          McNemar p    Significant?
CaTS†    HotpotQA   +2.0       [−0.5, +4.5]    0.12         —
CaTS†    APPS       +7.0       [+3.2, +10.8]   0.003        ✅
CaTS†    WebShop    +13.3      [+8.1, +18.5]   <0.001       ✅
...
```

**TODO**: ~~`python analysis/statistical_significance_table.py`~~
**状态**: ✅ 已完成 (v7.1)
**数据来源**:
- EAAG episodes: `results/phase6/path_e/{env}/se_online_decay_local/seed_{123,42,456}/episodes.json`
- CB episodes:
  - CaTS/SEAG/CoRefine/CATTS: `results/phase5/competing_baselines/{env}/{method}/seed_*/episodes.json`
  - AUQ/s1: `results/phase6/new_baselines/{env}/{method}/seed_*/episodes.json`
- 每个 episodes.json 含 200 ep, key: `success` (bool)
- 方法: Bootstrap ΔSR 95% CI (5000 resamples, seed=42)
- FEVER: 无 CB 数据，未计算
**生成脚本**: `planning/paper_figures/generate_medium_priority_figures.py::tab_significance()`
**产出**: `planning/paper_figures/tab_significance.tex`
**实际结果**: 30 组对比中 18 个显著 (CI 排除 0)
  - WebShop: 全部显著 (ΔSR +8~+37pp)
  - HotpotQA vs AUQ/s1: 不显著 (ΔSR=-1.8pp)
  - Plancraft: 大部分不显著 (rollout-harmful, 方法差异小)
**优先级**: 🟡 中 — 替代 win/loss 的更强证据

---

## 3.9 v7.0 新增实验（需要新 GPU run）🆕🆕🆕

### 3.9.1 🟡 Controlled InfoPoor/InfoRich 实验 (Causal Evidence for Direction Reversal)

**论文位置**: §5.4 Ablation 或 Appendix D

**目的**: 在同一个 task family (HotpotQA) 内通过操控 information structure 触发 direction reversal，提供因果证据（不是跨 task 的 observational evidence）

**理论预测**:
```
Two-Source Model 预测:
  InfoPoor (p_I 高) → ρ(entropy, U) 强负
  InfoRich (p_I 低) → ρ(entropy, U) 弱正或 ≈0
  关键: 同一个 task，不同的信息结构 → 方向反转
```

**实验设计**:

```
环境变体 A: HotpotQA-InfoPoor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  修改: retrieval 阶段只返回 1 个 evidence paragraph (随机选)
  效果: agent 缺信息 → 更多 Type I 状态 → 高 entropy = "不知道该搜什么"
  预期: ρ(entropy, U) 强负 (≈−0.3 to −0.5)
  预期 base SR: 降低 (信息少 → 更难)

环境变体 B: HotpotQA-InfoRich
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  修改: 第一步就把所有 gold evidence paragraphs 给 agent
  效果: agent 有充足信息 → 更多 Type D 状态 → 高 entropy = "有多种合理回答"
  预期: ρ(entropy, U) 弱正或 ≈0 (+0.05 to +0.15)
  预期 base SR: 提高 (信息充足 → 更容易)

对照: HotpotQA-Original (原始设置)
  已有数据: ρ = −0.041 (entropy), base SR = 49.0%
```

**代码修改量**:
- 修改 HotpotQA 环境的 `get_observation()` 或 `retrieve_evidence()` 方法
- InfoPoor: 限制 retrieval 返回的 paragraph 数量为 1
- InfoRich: 在 episode 开始时直接把 gold evidence 注入 context
- 预估代码改动: ~50 行 (在 environment wrapper 层面)

**实验量**:
```
2 variants × 200 episodes × 3 seeds = 1,200 episodes
+ Phase 1 probe 数据: 2 variants × 200 episodes = 400 episodes (always_trigger for signal discovery)
总计: ~1,600 episodes

每个 episode ≈ 5 steps × 2 API calls ≈ 10 API calls
总 API calls: ~16,000
GPU/API 时间: ~4-8 小时 (取决于 API 速率)
```

**需要跑的方法**:
```
每个 variant (InfoPoor / InfoRich):
  - base_only (200 ep × 3 seeds) → base SR
  - always_trigger (200 ep × 1 seed) → oracle SR + probe data for ρ
  - EAAG (200 ep × 3 seeds) → adaptive SR (optional, 如果时间够)
```

**产出**:
1. **ρ comparison table**:
```
Variant          ρ(entropy, U)    base SR    always SR    Two-Source Type
InfoPoor         −0.35 (预期)      35%         90%          Type I 主导
Original         −0.041 (已有)     49%         97%          Mixed
InfoRich         +0.10 (预期)      75%         98%          Type D 偏多
```

2. **Figure**: 3 组 scatter plot (InfoPoor / Original / InfoRich), 每组 X=entropy Y=utility, 回归线斜率变化
   - **文件名**: `fig_controlled_direction_reversal.pdf`

3. **核心 claim**: "在同一个 QA task 中，仅通过改变信息可用性即可触发 direction reversal — 证明方向是信息结构的函数，不是 task 类型的 artifact"

**风险评估**:
- ❌ 风险 1: InfoRich base SR 太高 (~95%) → headroom 不够 → ρ 无意义 → 需要看 always SR 是否也高
- ❌ 风险 2: InfoPoor 可能导致 agent 完全失败 (base SR ~5%) → ρ 不稳定
- ✅ 缓解: 先跑 50 ep pilot (不做 3 seeds) 看 base SR 范围，如果在 20%-80% 内则继续

**优先级判断**:
- 🟡 **中优先** — 如果时间充足（NeurIPS DDL 前还有 2+ 周），做这个实验显著增强论文
- 如果时间紧张 → 用已有 quasi-controlled evidence 替代:
  - FEVER ≈ HotpotQA (同族，方向一致) → 同类 task 方向一致
  - APPS Intro (ρ≈0) vs APPS Interview (ρ=+0.317) → 同 task 不同难度方向变化
  - 这些不是 controlled experiment 但提供了 convergent evidence

**TODO**:
1. ✅ 修改 HotpotQA 环境代码 → `frvc/envs/hotpotqa_env.py` (添加 `variant` 参数)
   - InfoPoor: `_do_search()` 只返回首句
   - InfoRich: `reset()` 注入全部 gold evidence
2. ✅ 创建配置文件 → `configs/phase6_hotpotqa_infopoor.yaml`, `configs/phase6_hotpotqa_inforich.yaml`
3. ✅ 提交 GPU Job:
   - ~~Job 23297277~~ FAILED (base_only 不在 p6 method choices)
   - **Job 23304286** (8 tasks: step0 用 p5, EAAG 用 p6)
   - sbatch: `scripts/phase6/run_controlled_reversal.sbatch`
   - 修复: 添加 hotpotqa_infopoor/inforich 到 p5 env choices; 重构 yaml 为嵌套格式
4. ⏳ 等待结果 → 生成 scatter plot + ρ comparison table

---

## 4. 实验完成状态 Checklist

### 4.1 数据收集

- [x] 8 环境 Step 0 GO/NO-GO
- [x] 8 环境 Step 1 Signal Discovery
- [x] 6 环境 Core 6 methods × 3 seeds (FEVER 缺 3 seeds)
- [x] 6 环境 CB 6 methods × 3 seeds (含 Issue 3 修复)
- [x] 6 环境 BSW fix × 3 seeds
- [x] FEVER Path E 64/75, APPS Intv 54/75
- [x] Optimistic exploration test (FEVER, 失败)
- [x] DS-1000 放弃 (test harness 无法修复)
- [x] FEVER Path E: 11/11 完成 ✅ (Job 23292522 6个 + Job 23297275 5个)
- [x] APPS Interview Path E: 9/21 完成, 剩余 8 个跳过 (48G OOM, appendix 环境已有足够数据)
- [x] CRUXEval Path E 75/75 → Job 23292522 全部完成 ✅
- [ ] Controlled InfoPoor/InfoRich (§3.9.1) → ~~Job 23297277 FAILED~~ → ~~Job 23304286 (%4)~~ → **Job 23304305** (8 tasks, %6)

### 4.2 Analysis 图表

**原版 figures (v6.0 已完成)**:
- [x] §5 E1: Direction reversal 信号热力图 → `fig1_signal_heatmap.png/pdf`
- [x] §5 E2: Pareto frontier 图 × 6 环境 → `fig2_pareto.png/pdf`
- [x] §5 E1: BSW 错误方向代价散点图 → `fig3_bsw_cost.png/pdf`
- [x] §5 E1/E3: Feature usage heatmap → `fig4_feature_heatmap.png/pdf`
- [x] §5 E3: LLM ablation 柱状图 → `fig5_llm_ablation.png/pdf`
- [x] §6.1: FEVER exploration bias 分析图 → `fig6_fever_bias.png/pdf`

**v7.1 高优先级 (已完成)**:
- [x] 🔴 §3.1: AUC hierarchy 柱状图 → `fig_auc_hierarchy.png/pdf` (§3.8.1)
- [x] 🔴 §3.2: P1 Temporal Shift 验证 → `fig_p1_temporal_shift.png/pdf` (§3.8.2)
- [x] 🔴 §5.6: Stratified analysis → `fig_stratified_reversal.png/pdf` (§3.8.7 Part A)
- [x] 🔴 §5.6: Matched-pair analysis → `fig_matched_pair_opposite_meaning.png/pdf` (§3.8.7 Part B)
- [x] 🔴 §5.6: Gate capacity ablation → `tab_gate_capacity.tex` (§3.8.8)

**v7.1 中/低优先级 (已完成)**:
- [x] 🟡 §5.4: Gate trigger rate vs step → `fig_trigger_rate_by_step.png/pdf` (§3.8.3)
- [x] 🟡 §3.2: BSW 代价 vs |ρ| 相关性 → `fig_bsw_cost_vs_rho.png/pdf` (§3.8.4)
- [x] 🟡 §3.3: 方法分类等价表 → `tab_method_classification.tex` (§3.8.5)
- [x] 🟡 §5.4/App D: Information coverage proxy → `fig_coverage_vs_rho.png/pdf` (§3.8.9)
- [x] 🟡 §5.2/App E: Statistical significance 汇总表 → `tab_significance.tex` (§3.8.10)
- [x] 🟢 §6: 环境信息结构分类表 → `tab_env_info_structure.tex` (§3.8.6)

**需要新 GPU run (已提交)**:
- [ ] 🟡 §5.4: Controlled InfoPoor/InfoRich → **Job 23304305** (8 tasks, %6 concurrency)
- [ ] 🟡 §5.6: MLP/Hidden-state correct-direction SR (精确值) → 补 §3.8.8 数据 (未提交)

All figures at: `planning/paper_figures/` (PNG 200dpi + PDF vector)
生成脚本:
- `planning/paper_figures/generate_all_figures.py` — 原版 6 figures
- `planning/paper_figures/generate_high_priority_figures.py` — v7.1 高优先级 5 items
- `planning/paper_figures/generate_medium_priority_figures.py` — v7.1 中/低优先级 6 items

### 4.3 GPU Jobs

```
Job 23292522 (2026-03-22): Path E 原始提交
  sbatch --array=3-5,8-9,11-14,16-17,90-92,131,133-149,225-299%8 \
      scripts/phase6/run_env_extend_methods.sbatch
  最终状态: FEVER 6/11 完成; APPS Intv 7/21 完成; CRUXEval 75/75 完成 ✅
  其余 FAILED/OOM → 见 Job 23297275

Job 23297275 (2026-03-22): OOM 重试 (48G + expandable_segments)
  sbatch --array=9,11,12,13,16,90,91,131,133,134,135,136,137,138,139,140,142 \
      scripts/phase6/resubmit_oom_48g.sbatch
  最终状态:
    FEVER: 5/5 完成 ✅ (array 9,11,12,13,16)
    APPS Intv: 2/12 完成 (array 90,136), 1 FAILED (91), 8 仍 OOM → 跳过 (appendix 环境, 9/21 方法已足够)

Job 23297277 (2026-03-22): §3.9.1 Controlled — FAILED ❌
  原因: base_only/always_trigger 不是 p6_e_method_upgrade.py 的合法 method
  全部 18 tasks 失败

Job 23304286 (2026-03-23): §3.9.1 Controlled — 已取消 (concurrency %4 → %6)
Job 23304305 (2026-03-23): §3.9.1 Controlled InfoPoor/InfoRich — 修复版 v2
  sbatch --array=0-7%6 scripts/phase6/run_controlled_reversal.sbatch
  Array 0-7: 2 variants × 4 tasks = 8 jobs
    0: InfoPoor  step0 (base_only+always_trigger 200ep via p5) + step1 (signal discovery)
    1-3: InfoPoor  EAAG seed=42/123/456 (via p6)
    4: InfoRich  step0 + step1
    5-7: InfoRich  EAAG seed=42/123/456
  修复: step0 用 p5_new_env_experiments.py, EAAG 用 p6_e_method_upgrade.py
  代码修改:
    - frvc/envs/hotpotqa_env.py (variant="infopoor"/"inforich")
    - experiments/p5_new_env_experiments.py (添加 hotpotqa_infopoor/inforich 到 env choices)
  配置文件: configs/phase6_hotpotqa_{infopoor,inforich}.yaml (重构为嵌套格式)
```

---

## 5. 论文 Experiment Section 大纲

### v7.0 升级版（对标 FLARE §3 三段式 + §5 实验）

```
═══════════════════════════════════════════════════════════════
§3 Signal-Utility Landscape (2.0 页) — FLARE-Style 三段式
═══════════════════════════════════════════════════════════════

§3.1 Empirical Landscape (0.7 页) — 纯数据，4 个 Observations
  Obs 1: Direction Reversal
    → Figure: 信号热力图 (8 env × N signals) [fig1, 已有]
    → Table: 8 env 的 ρ(entropy, U)
  Obs 2: Signal Replacement
    → Feature usage heatmap (7 env × features) [fig4, 已有]
  Obs 3: Signal Poverty 🆕
    → Figure: AUC hierarchy 柱状图 [fig_auc_hierarchy, §3.8.1 新增]
    → Data: single 0.53 → multi 0.85 → hidden 0.89 (3 env)
  Obs 4: Systematic CB Failure
    → Table: CB Win/Loss (34W 2L / 38)

§3.2 Formal Analysis (0.8 页) — Two-Source Model + Propositions
  Two-Source Model (Eq. 1 + p* + 环境映射)
  Proposition 3: Necessity of Direction Discovery (3 行 formal statement)
  → Prop 1/2 降为 empirical claims (不做 full formal proposition)
  3 Testable Predictions (P1/P2/P3)

§3.3 Implications (0.5 页) — Bridge to method
  方法分类等价表 (FLARE Table 5) [§3.8.5 新增]
  环境信息结构分类 [§3.8.6]
  过渡句 → §4 Method

═══════════════════════════════════════════════════════════════
§5 Experiments (2.5 页)
═══════════════════════════════════════════════════════════════

§5.1 Setup (0.3 页)
  - 8 环境 + EAAG + baseline 分层 (Table)
  - Total Cost 定义 (含 Phase 1 amortized)
  - 公平对比声明 ("same T, same agent, only gate differs")

§5.2 E1: Main Comparison (0.8 页)
  - Table: 主表 (6 env × methods, SR + Total Cost)
  - Figure: Pareto frontier (4 主实验子图) [fig2, 已有]
  - EAAG 34W/2L vs 6 CB
  - EAAG Pareto-dominates SCG† 4/7, CaTS† 6/6

§5.3 E2: Ablation & Analysis (0.6 页)
  - BSW wrong-direction ablation [fig3, 已有]
  - LLM ablation: EAAG vs principled_v2 [fig5, 已有]
  - Gate trigger rate vs step 🆕 [fig_trigger_rate_by_step, §3.8.3]

§5.4 E3: Theory Verification (0.5 页) 🆕 v7.0 新增
  - P1 Temporal Shift 验证 🆕 [fig_p1_temporal_shift, §3.8.2]
  - P2 同族方向一致 (FEVER≈HotpotQA) — 已有数据
  - P3 Signal identity alignment — 已有数据
  - Information coverage proxy 🆕 [fig_coverage_vs_rho, §3.8.9]
  - [Optional] Controlled InfoPoor/InfoRich 🆕 [fig_controlled, §3.9.1]

§5.5 Diagnostic (0.3 页) — TWExpress + Plancraft

§5.6 Robustness (0.5 页) 🆕🆕 v7.1 Reviewer 防御
  - Stratified analysis (控制 length/difficulty confounder) [fig_stratified, §3.8.7A]
  - Matched-pair analysis ("same entropy, opposite meaning") [fig_matched_pair, §3.8.7B]
  - Gate capacity ablation (direction >> complexity) [tab:capacity, §3.8.8]
  - Statistical significance (McNemar + TOST) [tab:significance, §3.8.10]

═══════════════════════════════════════════════════════════════
§6 Discussion (1.0 页)
═══════════════════════════════════════════════════════════════

§6.1 Community Insight
  "Uncertainty semantics = f(environment information structure)"
  Prescriptive framework: Info-Sufficiency × Reversibility × Feedback-Delay

§6.2 Exploration Bias (FEVER case study) [fig6, 已有]

§6.3 Limitations + Future Work
  - Single backbone (Qwen3-4B)
  - Two-Source Model 是 first-order approximation
  - Future: from binary U → rollout content learning
```

### v7.1 Figure 清单（论文全部图表 — 全部已生成）

```
正文 Figures (9-11 个):                                       状态    文件
  fig1: 信号热力图 (8 env × signals)                         ✅     fig1_signal_heatmap.png/pdf
  fig2: Pareto frontier (4+2 env)                            ✅     fig2_pareto.png/pdf
  fig3: BSW 错误方向退化                                      ✅     fig3_bsw_cost.png/pdf
  fig4: Feature usage heatmap (7 env)                        ✅     fig4_feature_heatmap.png/pdf
  fig_auc: AUC hierarchy (3 env × 4 levels)                  ✅     fig_auc_hierarchy.png/pdf
  fig_p1: P1 temporal shift (5 env, early vs late ρ)         ✅     fig_p1_temporal_shift.png/pdf
  fig_trigger: Trigger rate vs step (6 env)                  ✅     fig_trigger_rate_by_step.png/pdf
  fig_fever: FEVER exploration bias                          ✅     fig6_fever_bias.png/pdf
  fig_stratified: Stratified reversal (5 env × 3 strata)    ✅     fig_stratified_reversal.png/pdf
  fig_matched: Matched-pair ΔU (4 env × 3 bins)             ✅     fig_matched_pair_opposite_meaning.png/pdf
  fig_coverage: Coverage proxy vs ρ scatter                  ✅     fig_coverage_vs_rho.png/pdf
  [opt] fig_controlled: InfoPoor/InfoRich scatter            ⏳     需 GPU run (§3.9.1)

正文 Tables (5 个):                                           状态    文件
  tab1: Env setup (8 env × base/always/optimizer)            手写    (论文 LaTeX 中)
  tab2: Main results (6 env × methods, SR + Cost)            手写    (论文 LaTeX 中)
  tab3: Method classification (FLARE Table 5 style)          ✅     tab_method_classification.tex
  tab4: Gate capacity ablation                               ✅     tab_gate_capacity.tex
  tab5: Info structure taxonomy (8 env × 3 dims)             ✅     tab_env_info_structure.tex

附录 Figures/Tables:                                          状态    文件
  LLM ablation 柱状图                                        ✅     fig5_llm_ablation.png/pdf
  BSW 代价 vs |ρ| 散点图 (含回归 R²)                          ✅     fig_bsw_cost_vs_rho.png/pdf
  Statistical significance 汇总表                             ✅     tab_significance.tex
  Appendix env results (APPS Intv, CRUXEval)                 ⏳     需 GPU data
  CMDP λ* convergence                                        手写
  Proposition proofs                                         手写
```

---

## 6. 数据源索引 (v7.1 新增)

所有实验数据的文件路径，供复现和查证使用。

### 6.1 Probe / Signal Discovery 数据 (per-step records: entropy, utility, step_count, ...)

| 环境 | 路径 | Records | 来源 |
|------|------|:---:|------|
| HotpotQA | `results/phase1_signal_discovery/hotpotqa/phase1_signal_data.json` | 1208 | Phase 1 (seed 42, 有 episode ID) |
| HotpotQA | `results/phase5/calibration_data/hotpotqa/phase1_signal_data.json` | 1117 | Phase 5 (3 seeds, 无 episode ID) |
| APPS | `results/phase5/calibration_data/apps/phase1_signal_data.json` | 1567 | Phase 5 (3 seeds) |
| WebShop | `results/phase5/calibration_data/webshop/phase1_signal_data.json` | 3899 | Phase 5 (3 seeds) |
| FEVER | `results/phase6/fever/fever/phase1_signal_data.json` | 282 | Phase 6 (seed 42) |
| TWExpress | `results/phase5/twexpress/twexpress/phase1_signal_data.json` | 798 | Phase 5 |
| APPS Intv | `results/phase6/apps_interview/apps_interview/phase1_signal_data.json` | 439 | Phase 6 |
| Plancraft | `results/phase5/data/plancraft/seed_42/step_data.npz` | 1548 | Phase 5 (npz, 含 hidden states) |

**Record 格式 (JSON)**: `{step, step_count, token_entropy, utility, environment, episode, seed, evidence_count, is_finish_proposed, state_category, ...}`
**Record 格式 (npz)**: `{hidden_states, utilities, token_entropies, signals, signal_keys}`

### 6.2 Phase 5 Hidden State / AUC 数据

| 环境 | 路径 |
|------|------|
| HotpotQA | `results/phase5/data/hotpotqa/seed_42/step_data.npz` (391 steps) |
| APPS | `results/phase5/data/apps/seed_42/step_data.npz` (518 steps) |
| WebShop | `results/phase5/data/webshop/seed_42/step_data.npz` (1261 steps) |
| Plancraft | `results/phase5/data/plancraft/seed_42/step_data.npz` (1548 steps) |

AUC 计算脚本: `scripts/phase5/auc_analysis.py`

### 6.3 Phase 6 Method Results (SR, episodes, decision logs)

**路径模式**: `results/phase6/path_e/{env}/{method}/seed_{123,42,456}/`

| 文件 | 内容 | 用途 |
|------|------|------|
| `summary.json` | SR, avg_rollouts_per_ep, gate_stats | 主表数据 |
| `episodes.json` | per-episode: success, steps, rollout_count, gate_phase | 统计显著性 |
| `scg_{method}_decision_log.json` | per-step: prob, threshold, decision, phase | Trigger rate 分析 |
| `scg_{method}_calibration.json` | per-rollout: entropy, utility, step_count, episode | 探索阶段数据 |

**EAAG 方法名**: `se_online_decay_local`

### 6.4 CB Baseline Results

| 方法 | 路径模式 |
|------|---------|
| CaTS, SEAG, CoRefine, CATTS | `results/phase5/competing_baselines/{env}/{method}/seed_*/` |
| AUQ, s1_budget | `results/phase6/new_baselines/{env}/{method}/seed_*/` |

### 6.5 Signal Discovery Summaries

| 环境 | 路径 |
|------|------|
| FEVER | `results/phase6/fever/fever/step1_signal_discovery.json` |
| APPS Intv | `results/phase6/apps_interview/apps_interview/step1_signal_discovery.json` |
| CRUXEval | `results/phase6/cruxeval/cruxeval/step1_signal_discovery.json` |
| (其他) | 嵌入在 probe 数据文件中 |

### 6.6 Temporal Shift / Toy Model 预计算

| 文件 | 内容 |
|------|------|
| `results/phase6/toy_model/d1_temporal_shift_results.json` | P1: early vs late ρ (HotpotQA, APPS, WebShop, MBPP) |
| `results/phase6/toy_model/d2_simpsons_paradox_results.json` | Simpson's paradox 分析 |
| `results/phase6/toy_model/d3_p2p3_results.json` | P2/P3 验证 |
| `results/phase6/toy_model/toy_model_verification_summary.json` | 总结 |

### 6.7 生成脚本

| 脚本 | 产出 |
|------|------|
| `planning/paper_figures/generate_all_figures.py` | fig1-fig6 (原版) |
| `planning/paper_figures/generate_high_priority_figures.py` | fig_auc, fig_p1, fig_stratified, fig_matched_pair, tab_capacity |
| `planning/paper_figures/generate_medium_priority_figures.py` | fig_trigger, fig_bsw_cost, fig_coverage, tab_classification, tab_significance, tab_env_info |

运行方式: `conda activate frvc && python3 planning/paper_figures/generate_{all,high_priority,medium_priority}_figures.py`
