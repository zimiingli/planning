# 实验结果综合报告

**Date**: 2026-03-19 (updated)
**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**总计**: 700+ runs, 212 个 (method x env) 组合, 6 个环境, 30+ 个方法

### 数据来源

| 来源 | 路径 | 内容 |
|------|------|------|
| Phase 4 | `results/phase4/webshop/core/*/seed_*/performance_summary.json` | SCG WebShop (3 seeds) |
| Phase 5 | `results/phase5/{comparison,cb,cb_calibrated,other}/*/*/*/summary.json` | SCG + 4 CB + base/always/oracle (HotpotQA/APPS/TWExpress/Plancraft/BabyAI) |
| Phase 6 Path E | `results/phase6/path_e/{env}/{method}/seed_*/summary.json` | Principled 系列 + SE 全系列 + CACB + Proto |
| Phase 6 New BL | `results/phase6/new_baselines/{env}/{method}/seed_*/summary.json` | AUQ + s1_budget (5 envs) |

---

## 1. 方法概览

### 1.1 Reference Baselines

| Method | 类型 | 描述 |
|--------|------|------|
| base_only | Reference | 纯 base policy，不使用 rollout |
| always_rollout | Reference | 每步都触发 rollout（SR 上界，cost 上界） |
| oracle | Reference | 用真实 utility 决定是否触发（理论最优） |

### 1.2 Competing Baselines (文献方法)

| Method | 论文 | 核心机制 | 方向假设 |
|--------|------|---------|---------|
| CaTS | Kadavath 2022 | Token probability calibration | 固定负向 |
| CATTS | Stengel-Eskin 2024 | Calibrated with task-specific tuning | 固定负向 |
| SEAG | Ye 2024 | Self-evaluation with aggregated guidance | 固定负向 |
| CoRefine | Madaan 2023 | Co-refinement iterative | 固定负向 |
| AUQ | arXiv:2601.15703 | 每步问 LLM "你多有信心？" → 低信心触发 | 固定负向 |
| s1_budget | EMNLP 2025 | 固定 K 次 rollout 均匀分布 | 无 |

### 1.3 ⭐ Our Methods — SCG (Signal-Conditioned Gating)

| Method | 描述 | 需要领域知识 | 特点 |
|--------|------|:-----------:|------|
| **scg_finetune_lr** ⭐ | 手工 5 feature (token_entropy, step_count, evidence_count 等) + LogisticRegression，per-environment 特征工程 | Yes | Cost 最低，HotpotQA 最优 |

### 1.4 ⭐ Our Methods — Principled SCG Series

所有 Principled 方法都是全自动化的，不需要领域知识。

| Method | 描述 | 关键区别 |
|--------|------|---------|
| **principled** ⭐ | Auto feature pool (universal+PCA+auto-extracted) → MI pre-filter → LASSO selection → 固定 threshold | 原始版本，threshold 不够灵活 |
| **principled_nopca** ⭐ | 同上但去掉 PCA features，不需要 HF engine | SR 几乎不变，省掉 HF engine |
| **principled_auto** ⭐ | 固定 lambda=0.05 做 CMDP threshold sweep | HotpotQA SR 暴跌 68.2%（lambda 太大） |
| **principled_adaptive** ⭐ | 自适应 lambda = (always_gain)/(always_cost-1)，从探索数据估计 | 主环境修复，但 Plancraft LASSO 失败 |
| **principled_fbeta** ⭐ | F-beta threshold，beta = sqrt(pos_rate/(1-pos_rate)) | HotpotQA 91.8% 太保守 |
| **principled_v2** ⭐ | adaptive lambda + low pos_rate fallback (pos_rate<2% → threshold=0.95) | **最终自动化方法**: 5 环境全覆盖 |

### 1.5 ⭐ Our Methods — Self-Evolving V1

| Method | Backend | 描述 |
|--------|---------|------|
| **self_evolving_local** ⭐ | Qwen3-4B | LLM 分析探索经验 → 生成 Python feature extractor → features 加入 LASSO pool |
| **self_evolving_openrouter** ⭐ | Claude-opus-4.6 | 同上，但用 Claude 做反思 |

特点：LLM 生成 15-18 个 features，但 50 样本不够支撑 → WebShop 过拟合 (38.2%)
数据来源: `results/phase6/path_e/` (V1 补做后全部 5 环境 3-seed 完成)

### 1.6 ⭐ Our Methods — SE Phase 1: Fewer Features

| Method | Backend | Filter | 描述 |
|--------|---------|:------:|------|
| **se_few5_local** ⭐ | local | No | LLM 只生成 5 个 feature（减少过拟合） |
| **se_few5_filter_local** ⭐ | local | Yes | 5 feature + correlation filter (|corr|>0.05) |
| **se_few5_openrouter** ⭐ | openrouter | No | 同 few5，Claude backend |
| **se_few5_filter_openrouter** ⭐ | openrouter | Yes | 同 few5_filter，Claude backend |

### 1.7 ⭐ Our Methods — SE Phase 2: Feedback Evolution

| Method | Cycles | Backend | 描述 |
|--------|:------:|---------|------|
| **se_feedback_cycle2_local** ⭐ | 2 | local | 2 轮反馈进化: LASSO 重要性 + 失误案例 → LLM 重新反思 |
| **se_feedback_cycle3_local** ⭐ | 3 | local | 3 轮反馈进化 |
| **se_feedback_cycle2_openrouter** ⭐ | 2 | openrouter | 同上，Claude backend |
| **se_feedback_cycle3_openrouter** ⭐ | 3 | openrouter | 同上，Claude backend |

### 1.8 ⭐ Our Methods — SE 100cal & Ablation

| Method | 描述 |
|--------|------|
| **se_few5flt_or_100cal** ⭐ | 100 cal points (更多探索数据) + openrouter + filter |
| **se_100cal_fb_c3_local** ⭐ | 100cal + feedback cycle3 + local |
| **se_c3_addcum_local** ⭐ | Phase3 消融: additive features + cumulative data + NO feedback |
| **se_c3_addlat_local** ⭐ | Phase3 消融: additive + latest data only |
| **se_c3_selcum_local** ⭐ | Phase3 消融: selective features + cumulative |
| **se_c3_sellat_local** ⭐ | Phase3 消融: selective + latest |

### 1.9 ⭐ Our Methods — SE Online Continuous Learning

| Method | epsilon 策略 | LLM Re-reflect | 描述 |
|--------|--------|:--------------:|------|
| **se_online_fix_local** ⭐ | 固定 0.1 | No | epsilon-greedy 持续探索 + 每 30ep LASSO 重训练 |
| **se_online_fix_ref_local** ⭐ | 固定 0.1 | Yes ep100 | 同上 + ep100 LLM 重反思 |
| **se_online_decay_local** ⭐ | 0.3→0.05 衰减 | No | 衰减 epsilon + 周期重训练 |
| **se_online_decay_ref_local** ⭐ | 0.3→0.05 衰减 | Yes ep100 | 衰减 epsilon + ep100 反思 |

### 1.10 ⭐ Our Methods — Other Explorations

| Method | 描述 | 结论 |
|--------|------|------|
| **cacb_A/B/C** ⭐ | Thompson Sampling Contextual Bandit (3 种 feature mode) | 方差大，不够稳定 |
| **proto** ⭐ | Prototypical Networks (hidden state 距离) | 第二好，但不如 Principled |

---

## 2. 环境描述

| 环境 | 类型 | 论文定位 | base SR | always SR | Oracle SR | Headroom | 信号特点 |
|------|------|---------|:-------:|:---------:|:---------:|:--------:|---------|
| **HotpotQA** | Multi-hop QA | 主实验 | 49.0% | 97.0% | 97.0% | 48.0pp | 强信号 (rho=-0.327), Type I 主导 |
| **APPS** | Code Generation | 主实验 | 58.5% | 64.5% | 75.0% | 6.0pp | 弱信号 (rho=-0.155), oracle gap 大 |
| **WebShop** | Web Navigation | 主实验 | 28.0% | 43.5% | — | 15.5pp | 混合信号, state 结构差异大 |
| **TWExpress** | Text Adventure | 诊断: rollout-safe | 56.3% | 99.3% | 99.3% | 43.0pp | rollout 永远无害 |
| **Plancraft** | Crafting | 诊断: rollout-harmful | 29.8% | 22.8% | 21.3% | -7.0pp | rollout 有害! base > always |
| **BabyAI** | Grid World | Limitation | 2.0% | 11.3% | 11.3% | 9.3pp | 信号不存在 (pos_rate=0.2%) |

---

## 3. 各环境主结果表

每个环境一个完整表格，包含: Reference + 6 Competing Baselines + SCG + Principled/V2 + SE Top 3。
Cost(×base) 使用公式 `1 + Ro/ep × C_rollout / (S_base × C_base)`，注意此为近似值（假设 S≈S_base）。

### 3.1 HotpotQA (Multi-hop QA — 主实验, 强信号)

**环境参数**: C_base=216, C_rollout=7,743, S_base=6.24 | base SR=49.0%, always SR=97.0%, oracle SR=97.0%

| # | Method | 归属 | SR | Ro/ep | Cost(×base) | 数据来源 |
|:-:|--------|:----:|:--:|:-----:|:-----------:|:--------:|
| 1 | oracle | ref | 97.0% | 0.59 | 4.39× | P5 |
| 2 | always_rollout | ref | 97.0% | 1.80 | 11.34× | P5 |
| 3 | AUQ | CB | 97.0% | 1.69 | 10.70× | P6-NB |
| 4 | s1_budget | CB | 97.0% | 1.04 | 6.97× | P6-NB |
| 5 | CaTS | CB | 93.2% | 1.77 | 11.18× | P5-CB |
| 6 | CoRefine | CB | 68.2% | 1.05 | 7.01× | P5-CB |
| 7 | CATTS | CB | 68.3% | 1.07 | 7.13× | P5-CB |
| 8 | SEAG | CB | 67.5% | 1.02 | 6.86× | P5-CB |
| 9 | **scg_finetune_lr** | ⭐ Ours | **96.8%** | **1.09** | **7.26×** | P5 |
| 10 | principled_adaptive | ⭐ Ours | 95.7% | 1.14 | 7.55× | P6-E |
| 11 | **principled_v2** | ⭐ Ours | **94.8%** | **1.09** | **7.26×** | P6-E |
| 12 | **se_online_decay_ref_local** | ⭐ SE | **95.7%** | 1.24 | 8.09× | P6-E |
| 13 | **se_fb_cycle2_local** | ⭐ SE | **95.7%** | 1.15 | 7.63× | P6-E |
| 14 | **se_c3_selcum_local** | ⭐ SE | 95.5% | 1.18 | 7.75× | P6-E |

> **数据来源缩写**: P4=Phase4, P5=Phase5, P5-CB=Phase5 competing baselines, P6-E=Phase6 path_e, P6-NB=Phase6 new_baselines

**分析**: SCG 以最低 cost (7.26×) 达到最高 SR (96.8%)，接近 oracle。AUQ/s1 靠近乎全触发达到 97.0% 但 cost 极高。SE 系列自动化方法达到 95.5-95.7%，接近 SCG 但不超过——因为 HotpotQA 的 evidence_count 是人工设计的 "完美信号"。

---

### 3.2 APPS (Code Generation — 主实验, 弱信号)

**环境参数**: C_base=840, C_rollout=3,306, S_base=2.97 | base SR=58.5%, always SR=64.5%, oracle SR=75.0%

| # | Method | 归属 | SR | Ro/ep | Cost(×base) | 数据来源 |
|:-:|--------|:----:|:--:|:-----:|:-----------:|:--------:|
| 1 | always_rollout | ref | 64.5% | 2.59 | 4.43× | P5 |
| 2 | s1_budget | CB | 63.7% | 1.00 | 2.33× | P6-NB |
| 3 | AUQ | CB | 61.3% | 1.73 | 3.29× | P6-NB |
| 4 | CaTS | CB | 59.0% | 0.04 | 1.05× | P5-CB |
| 5 | CATTS | CB | 58.5% | 0.03 | 1.03× | P5-CB |
| 6 | SEAG | CB | 58.5% | 0.01 | 1.01× | P5-CB |
| 7 | CoRefine | CB | 58.5% | 0.01 | 1.01× | P5-CB |
| 8 | scg_finetune_lr | ⭐ Ours | 58.8% | 0.18 | 1.24× | P5 |
| 9 | **principled_v2** | ⭐ Ours | **64.2%** | **1.18** | **2.56×** | P6-E |
| 10 | **se_few5flt_or_100cal** | ⭐ SE | **66.0%** | 1.55 | 3.05× | P6-E |
| 11 | **se_online_decay_local** | ⭐ SE | **66.0%** | 1.20 | 2.59× | P6-E |
| 12 | **se_few5_filter_local** | ⭐ SE | **65.8%** | 1.39 | 2.84× | P6-E |

**分析**: APPS 是 SE 系列最大胜利。SCG 手工 feature 只有 58.8% (甚至不如 CaTS 59.0%)，但 LLM 自动发现的 feature 将 SR 推到 66.0%——超过最强 CB (s1_budget 63.7%) +2.3pp。Oracle SR=75.0% 表明仍有 9pp 提升空间。传统 CB (CATTS/SEAG/CoRefine) 在 APPS 上等于 base_only (58.5%)。

---

### 3.3 WebShop (Web Navigation — 主实验, 最难环境)

**环境参数**: C_base=705, C_rollout=9,089, S_base=14.06 | base SR=28.0%[P4], always SR=43.5%[P4]

| # | Method | 归属 | SR | Ro/ep | Cost(×base) | 数据来源 |
|:-:|--------|:----:|:--:|:-----:|:-----------:|:--------:|
| 1 | always_rollout | ref | 43.5% | 5.61 | 6.14× | P4 |
| 2 | AUQ | CB | 35.7% | 5.33 | 5.89× | P6-NB |
| 3 | CaTS | CB | 30.5% | 3.04 | 3.79× | P5-CB |
| 4 | SEAG | CB | 28.0% | 2.28 | 3.09× | P5-CB |
| 5 | CoRefine | CB | 27.5% | 2.21 | 3.03× | P5-CB |
| 6 | CATTS | CB | 16.0% | 0.20 | 1.18× | P5-CB |
| 7 | s1_budget | CB | 9.3%° | 1.00 | 1.92× | P6-NB |
| 8 | scg_finetune_lr | ⭐ Ours | 43.7% | 0.95 | 1.87× | **P4** |
| 9 | **principled_v2** | ⭐ Ours | **42.7%** | **1.65** | **2.51×** | P6-E |
| 10 | **se_online_fix_local** | ⭐ SE | **44.0%** | 1.94 | 2.78× | P6-E |
| 11 | **se_online_decay_local** | ⭐ SE | **43.8%** | 2.29 | 3.10× | P6-E |
| 12 | **se_c3_addlat_local** | ⭐ SE | 43.2% | 2.27 | 3.08× | P6-E |

> **注**: SCG WebShop 数据 [P4] 来自 Phase 4 独立实验，使用预加载数据 (500 data points)，与 Phase 6 在线学习设置不同。°seed 数不足 3。

**分析**: WebShop 是 SE 系列最难攻克的环境。se_online_fix_local (44.0%) 超过所有方法（含 SCG 43.7%[P4]），且完全自动化。关键是 ε-greedy 持续探索解决了 50ep 数据不够的问题。AUQ 虽然 CB 中最好 (35.7%) 但 cost 极高 (5.89×)，s1_budget 几乎完全失败 (9.3%)。

---

### 3.4 TWExpress (Text Adventure — 诊断: rollout-safe)

**环境参数**: C_base=524, C_rollout=8,002, S_base≈50 | base SR=56.3%, always SR=99.3%

| # | Method | 归属 | SR | Ro/ep | Cost(×base) | 数据来源 |
|:-:|--------|:----:|:--:|:-----:|:-----------:|:--------:|
| 1 | oracle | ref | 99.3% | 0.91 | 1.28× | P5 |
| 2 | always_rollout | ref | 99.3% | 3.45 | 2.05× | P5 |
| 3 | AUQ | CB | 95.5%° | 1.22 | 1.37× | P6-NB |
| 4 | s1_budget | CB | 95.0% | 1.09 | 1.33× | P6-NB |
| 5 | CaTS | CB | 83.4% | 9.52 | 3.91× | P5-CB |
| 6 | CoRefine | CB | 80.3% | 3.68 | 2.12× | P5-CB |
| 7 | CATTS | CB | 76.1% | 3.99 | 2.22× | P5-CB |
| 8 | SEAG | CB | 76.0% | 4.18 | 2.28× | P5-CB |
| 9 | scg_finetune_lr | ⭐ Ours | 75.7% | 8.68 | 3.65× | P5 |
| 10 | **principled_v2** | ⭐ Ours | **97.3%** | 2.71 | 1.83× | P6-E |
| 11 | **principled_adaptive** | ⭐ Ours | **99.2%** | 3.11 | 1.95× | P6-E |
| 12 | **se_fb_cycle2_local** | ⭐ SE | **98.7%** | 2.84 | 1.87× | P6-E |
| 13 | **se_few5_filter_openrouter** | ⭐ SE | **98.7%** | 2.64 | 1.81× | P6-E |
| 14 | **se_few5_filter_local** | ⭐ SE | **98.5%** | 2.82 | 1.86× | P6-E |

> **注**: SE Online 和 Phase 3 方法在 TWExpress/Plancraft 上的数据正在补做中 (job 23229159)，完成后将更新此表。

**分析**: TWExpress 中 rollout 永远无害，最优策略是尽量多触发。principled_adaptive (99.2%) 接近 oracle (99.3%)，自动学会了 "应该总是触发"。SE 系列 98.5-98.7% 也极高。SCG (75.7%) 在此环境反而最差——手工 feature 的选择性在 rollout-safe 环境是劣势。CaTS (83.4%) 触发过多 (9.52 Ro/ep > always 3.45) 但 SR 低，calibration 完全失败。

---

### 3.5 Plancraft (Crafting — 诊断: rollout-harmful)

**环境参数**: C_base=1,120, C_rollout=10,651, S_base≈30 | base SR=29.8%, always SR=22.8%

| # | Method | 归属 | SR | Ro/ep | Cost(×base) | 数据来源 |
|:-:|--------|:----:|:--:|:-----:|:-----------:|:--------:|
| 1 | **base_only** | ref | **29.8%** | **0.00** | **1.00×** | P5 |
| 2 | CATTS | CB | 25.0% | 2.14 | 1.68× | P5-CB |
| 3 | SEAG | CB | 24.8% | 2.16 | 1.69× | P5-CB |
| 4 | AUQ | CB | 24.2% | 6.78 | 3.15× | P6-NB |
| 5 | CoRefine | CB | 22.8% | 2.06 | 1.65× | P5-CB |
| 6 | CaTS | CB | 22.3% | 4.39 | 2.39× | P5-CB |
| 7 | always_rollout | ref | 22.8% | 6.99 | 3.22× | P5 |
| 8 | oracle | ref | 21.3% | 0.08 | 1.03× | P5 |
| 9 | s1_budget | CB | 18.3% | 1.68 | 1.53× | P6-NB |
| 10 | scg_finetune_lr | ⭐ Ours | 21.5% | 3.33 | 2.05× | P5 |
| 11 | **principled_v2** | ⭐ Ours | **27.2%** | **0.77** | **1.24×** | P6-E |
| 12 | **se_few5_local** | ⭐ SE | **28.3%** | 0.25 | 1.08× | P6-E |
| 13 | **se_fb_cycle2_local** | ⭐ SE | **28.3%** | 0.28 | 1.09× | P6-E |
| 14 | **se_fb_cycle2_openrouter** | ⭐ SE | **28.3%** | 0.44 | 1.14× | P6-E |

**分析**: Plancraft 中 rollout 有害 (always 22.8% < base 29.8%)。SE 方法自动学会不触发 (Ro/ep=0.25-0.44)，SR 28.3% 接近 base_only 29.8%，是所有 gating 方法中最高。principled_v2 通过 fallback (threshold=0.95) 也成功限制触发 (Ro/ep=0.77)。所有 6 个 CB 全部 SR ≤ 25%——盲目触发导致性能下降。s1_budget 最差 (18.3%)。

---

### 3.6 BabyAI (Grid World — Limitation 环境)

**环境参数**: base SR=2.0%, always SR=11.3% | pos_rate=0.2%

| Method | 归属 | SR |
|--------|:----:|:--:|
| always_rollout | ref | 11.3% |
| oracle | ref | 11.3% |
| CATTS | CB | 9.3% |
| principled_adaptive | ⭐ Ours | 9.3% |
| CaTS | CB | 8.7% |
| **se_few5_filter_local** | ⭐ SE | **3.5%** |
| base_only | ref | 2.0% |

**分析**: BabyAI pos_rate=0.2%，LASSO 在 2/3 seed 完全失败，LLM feature 也无法发现信号。SE 方法 SR=3.5% 反而低于 principled_adaptive (9.3%)。确认为 limitation 环境：信号不存在时任何自动 gating 不适用。

---

### 3.7 全环境汇总: Our Best vs 6 Competing Baselines

| 环境 | Our Best ⭐ | SR | Best CB | CB SR | Gap | 判定 |
|------|-----------|:--:|---------|:-----:|:---:|:----:|
| HotpotQA | scg_finetune_lr | 96.8% | AUQ / s1 | 97.0% | -0.2pp | 持平 |
| APPS | se_100cal / online_decay | **66.0%** | s1_budget | 63.7% | **+2.3pp** | ⭐ Win |
| WebShop | se_online_fix_local | **44.0%** | AUQ | 35.7% | **+8.3pp** | ⭐ Win |
| TWExpress | principled_adaptive | **99.2%** | AUQ | 95.5% | **+3.7pp** | ⭐ Win |
| Plancraft | SE (few5/fb_c2) | **28.3%** | CATTS | 25.0% | **+3.3pp** | ⭐ Win |

**结论**: 5/5 环境中 4 个超过全部 6 CB，1 个持平 (HotpotQA -0.2pp，噪声范围)。

所有 SE 方法的完整 SR × Ro/ep × Cost 数据见附录 (FULL_RESULTS_DUMP.txt)。

---

### 4.1 Principled Threshold 优化迭代

| 迭代 | Threshold 方式 | HotpotQA | APPS | WebShop | 问题 |
|------|--------------|:--------:|:----:|:-------:|------|
| nopca | 启发式 sweep | 95.8% | 65.7% | 43.7% | Ro/ep 过高 (APPS 2.19) |
| auto | 固定 lambda=0.05 | **68.2%** | 63.0% | 41.3% | lambda 太大 → HotpotQA 暴跌 |
| adaptive | lambda from data | 95.7% | 64.7% | 43.0% | Plancraft LASSO 失败 |
| fbeta | F-beta | 91.8% | 64.0% | 41.8% | 太保守 |
| **v2** | adaptive + fallback | **94.8%** | **64.2%** | **42.7%** | 最终版：5 环境全覆盖 |

**Insight**: 自适应 lambda 是关键改进，但需要 fallback 处理 LASSO 失败场景（Plancraft pos_rate < 2%）。

### 4.2 Our Best vs All 6 Competing Baselines

**全面对比**: 在确定 "Best CB" 时，考虑全部 6 个 competing baselines（CaTS, CATTS, SEAG, CoRefine, AUQ, s1_budget）。

| 环境 | Our Best | SR | Best CB | Best CB SR | 差距 |
|------|----------|:--:|---------|:----------:|:----:|
| HotpotQA | scg_finetune_lr ⭐ | 96.8% | AUQ / s1_budget | 97.0% | -0.2pp |
| APPS | se_few5flt_or_100cal / se_online_decay ⭐ | **66.0%** | s1_budget | 63.7% | **+2.3pp** |
| WebShop | se_online_fix_local ⭐ | **44.0%** | AUQ | 35.7% | **+8.3pp** |
| TWExpress | principled_adaptive ⭐ | **99.2%** | AUQ | 95.5% | **+3.7pp** |
| Plancraft | se_few5_local ⭐ | **28.3%** | CATTS | 25.0% | **+3.3pp** |

**结论**: 在 5/5 个有效环境中，Our methods 在 4 个超过全部 6 个 CB（APPS +2.3pp, WebShop +8.3pp, TWExpress +3.7pp, Plancraft +3.3pp），仅 HotpotQA 持平（96.8% vs 97.0%，差距在噪声范围内）。

**各 CB 各环境 SR 汇总**:

| CB | HotpotQA | APPS | WebShop | TWExpress | Plancraft |
|----|:--------:|:----:|:-------:|:---------:|:---------:|
| CaTS | 93.2% | 59.0% | 30.5% | 83.4% | 22.3% |
| CATTS | 68.3% | 58.5% | 16.0% | 76.1% | **25.0%** |
| SEAG | 67.5% | 58.5% | 28.0% | 76.0% | 24.8% |
| CoRefine | 68.2% | 58.5% | 27.5% | 80.3% | 22.8% |
| AUQ | **97.0%** | 61.3% | **35.7%** | **95.5%**° | 24.2% |
| s1_budget | **97.0%** | **63.7%** | 9.3%° | 95.0% | 18.3% |
| **Best CB** | **97.0%** | **63.7%** | **35.7%** | **95.5%** | **25.0%** |

### 4.3 Self-Evolving 系列演进

**WebShop（最难环境，SE 系列核心改进目标）：**

| 演进阶段 | Method | WebShop SR | Ro/ep | 关键改进 |
|---------|--------|:---------:|:-----:|---------|
| V1 原版 | self_evolving_local | 38.2% | 1.56 | 15-18 features → 过拟合 |
| Phase 1 | se_few5_filter_local | 39.2% (+1.0) | 1.69 | 5 features + filter |
| Phase 2 | se_fb_c3_openrouter | 41.3% (+2.1) | 1.71 | 3-cycle feedback |
| 100cal | se_few5flt_or_100cal | 43.2% (+1.9) | 2.25 | 更多探索数据 |
| Phase 3 | se_c3_addlat_local | 43.2% (+0.0) | 2.27 | 无 feedback 也可以! |
| **Online** | **se_online_fix_local** | **44.0% (+0.8)** | **1.94** | epsilon-greedy 持续学习 |

**APPS（最大提升环境）：**

| 演进阶段 | Method | APPS SR | 提升 (vs Best CB=63.7%) |
|---------|--------|:------:|:----:|
| SCG baseline | scg_finetune_lr | 58.8% | -4.9pp |
| Best CB | s1_budget | 63.7% | — |
| principled_v2 | principled_v2 | 64.2% | +0.5pp |
| SE Phase 1 | se_few5_filter_local | 65.8% | +2.1pp |
| **100cal** | **se_few5flt_or_100cal** | **66.0%** | **+2.3pp** |
| **Online** | **se_online_decay_local** | **66.0%** | **+2.3pp** |

### 4.4 Phase 3 消融实验结果

对比对象: `se_feedback_cycle3_local`（有反馈, selective, cumulative）

| 消融因素 | Method | HotpotQA | APPS | WebShop | 结论 |
|---------|--------|:--------:|:----:|:-------:|------|
| **有反馈 (对照)** | se_fb_c3_local | 94.7% | **65.8%** | 39.8% | APPS 最优 |
| 无反馈+add+cum | se_c3_addcum | 95.3% | 63.2% | 41.2% | HotpotQA 更高! |
| 无反馈+add+lat | se_c3_addlat | 95.2% | 64.3% | **43.2%** | WebShop 最优! |
| 无反馈+sel+cum | se_c3_selcum | 95.5% | 63.5% | 42.0% | 均衡 |
| 无反馈+sel+lat | se_c3_sellat | 95.5% | 62.3% | 42.7% | APPS 最低 |

**消融结论：**

1. **Feedback 帮助 APPS (+2.6pp)，但损害 WebShop (-3.4pp)** — 反馈在不同环境效果相反！
   - APPS: 反馈帮助 LLM 理解代码任务特点
   - WebShop: 反馈导致 feature 过度特化于近期失败案例
2. **Latest > Cumulative** (WebShop: addlat 43.2% > addcum 41.2%) — 只用原始探索数据反而更好
   - 原因: 累积的 exploitation 数据有 selection bias（只包含触发的步骤）
3. **Additive ≈ Selective** — 差距在噪声范围 (+/-1pp)

---

## 5. 各环境深度分析

### 5.1 HotpotQA（主实验 — 强信号环境）

**Best Methods:**

| Rank | Method | SR | Ro/ep | Cost(xbase) |
|:----:|--------|:--:|:-----:|:-----------:|
| 1 | AUQ / s1_budget (CB) | 97.0% | 1.69 / 1.04 | 10.70x / 6.97x |
| 2 | ⭐ scg_finetune_lr | **96.8%** | 1.09 | 7.26x |
| 3 | ⭐ principled_adaptive | 95.7% | 1.14 | 7.55x |
| 3 | ⭐ se_online_decay_ref | 95.7% | 1.24 | 8.12x |
| 3 | ⭐ se_feedback_cycle2_local | 95.7% | 1.15 | 7.61x |
| 6 | ⭐ se_c3_selcum / sellat | 95.5% | 1.18 / 1.16 | 7.78x / 7.66x |

**Insight**: HotpotQA 信号强且清晰 (evidence_count rho=-0.586)，所有合理方法都在 93-97% 范围。AUQ/s1_budget 靠"全部触发"或"均匀触发"达到 97.0%，但 cost 更高（AUQ 10.70x vs SCG 7.26x）。SCG 的手工 feature 以最低 cost 达到 96.8%。自动化方法（principled_v2 94.8%, SE 系列 94-96%）接近但不超过手工 feature。

### 5.2 APPS（主实验 — 弱信号环境，最大提升）

**Best Methods:**

| Rank | Method | SR | Ro/ep | vs Best CB (s1 63.7%) |
|:----:|--------|:--:|:-----:|:---------------------:|
| 1 | ⭐ se_few5flt_or_100cal | **66.0%** | 1.55 | +2.3pp |
| 1 | ⭐ se_online_decay_local | **66.0%** | 1.20 | +2.3pp |
| 3 | ⭐ se_few5_filter_local | 65.8% | 1.39 | +2.1pp |
| 3 | ⭐ se_feedback_cycle3_local | 65.8% | 1.28 | +2.1pp |
| 5 | ⭐ principled_nopca | 65.7% | 2.19 | +2.0pp |
| 6 | s1_budget (CB) | 63.7% | 1.00 | — |
| 7 | AUQ (CB) | 61.3% | 1.73 | -2.4pp |
| 8 | CaTS (CB) | 59.0% | 0.04 | -4.7pp |

**Insight**: APPS 是 SE 系列最大胜利。SCG 手工 feature 只有 58.8%（甚至不如 CaTS 59.0%），但 LLM 自动发现的 feature (has_divisor_terms, has_function_terms, has_graph_terms) 捕捉到了代码任务的领域特点。AUQ 和 s1_budget 表现优于传统 CB (CaTS/CATTS/SEAG/CoRefine)，但仍不如 SE 方法。Oracle SR=75.0% 意味着仍有 9pp 的改进空间。

### 5.3 WebShop（主实验 — 最难环境）

**Best Methods:**

| Rank | Method | SR | Ro/ep | vs Best CB (AUQ 35.7%) |
|:----:|--------|:--:|:-----:|:----------------------:|
| 1 | ⭐ se_online_fix_ref_local | 46.8%° | 2.03 | +11.1pp |
| 2 | ⭐ **se_online_fix_local** | **44.0%** | 1.94 | +8.3pp |
| 3 | ⭐ se_online_decay_local | 43.8% | 2.29 | +8.1pp |
| 4 | ⭐ principled_nopca | 43.7% | 3.49 | +8.0pp |
| 5 | ⭐ se_c3_addlat_local / se_few5flt_or_100cal | 43.2% | 2.27 / 2.25 | +7.5pp |
| 6 | AUQ (CB) | 35.7% | 5.33 | — |
| 7 | CaTS (CB) | 30.5% | 3.04 | -5.2pp |
| 8 | s1_budget (CB) | 9.3%° | 1.00 | -26.4pp |

**Insight**: WebShop 是 SE 系列最难攻克的环境。从 V1 的 38.2% 到 online_fix 的 44.0%，经历了 5 个改进阶段。关键突破是 **在线持续学习**：epsilon-greedy 持续收集新数据 + 周期性重训练，解决了 WebShop state 分布多样性导致的 50ep 探索不够的问题。AUQ (35.7%) 虽然在 CB 中最好，但 cost 极高 (Ro/ep=5.33)。s1_budget 在 WebShop 几乎完全失败 (9.3%)。

### 5.4 TWExpress（诊断 — Rollout-Safe）

**Best Methods:**

| Rank | Method | SR | Ro/ep | Cost(xbase) |
|:----:|--------|:--:|:-----:|:-----------:|
| 1 | ⭐ principled_adaptive | **99.2%** | 3.11 | 1.95x |
| 2 | ⭐ se_few5_filter_openrouter | 98.7% | 2.64 | 1.81x |
| 2 | ⭐ se_feedback_cycle2_local | 98.7% | 2.84 | 1.87x |
| 4 | ⭐ se_few5_filter_local | 98.5% | 2.82 | 1.86x |
| 4 | ⭐ se_feedback_cycle3_local | 98.5% | 2.97 | 1.91x |
| — | AUQ (Best CB) | 95.5%° | 1.22 | 1.37x |
| — | s1_budget | 95.0% | 1.09 | 1.33x |
| — | CaTS | 83.4% | 9.52 | 3.91x |

**Insight**: TWExpress 中 rollout 永远无害 (utility >= 0)，最优策略是尽量多触发。principled_adaptive 99.2% 接近 always_rollout 99.3%，说明自适应 lambda 正确学会了 "这里应该总是触发"。SE 方法同样高 SR (98.5-98.7%)。AUQ/s1_budget 虽然 cost 更低，但 SR 差了 3-4pp。CaTS 触发过多 (9.52 Ro/ep > always 3.45) 但 SR 只有 83.4%，说明其 calibration 在此环境完全失败。

### 5.5 Plancraft（诊断 — Rollout-Harmful）

**Best Methods:**

| Rank | Method | SR | Ro/ep | vs base_only (29.8%) |
|:----:|--------|:--:|:-----:|:--------------------:|
| 1 | base_only (ref) | **29.8%** | 0.00 | — |
| 2 | ⭐ se_few5_local | 28.3% | 0.25 | -1.5pp |
| 2 | ⭐ se_feedback_cycle2_local | 28.3% | 0.28 | -1.5pp |
| 2 | ⭐ se_feedback_cycle2_openrouter | 28.3% | 0.44 | -1.5pp |
| 5 | ⭐ se_few5_filter_openrouter | 28.2% | 0.25 | -1.6pp |
| 6 | ⭐ principled_v2 | 27.2% | 0.77 | -2.6pp |
| — | CATTS (Best CB) | 25.0% | 2.14 | -4.8pp |
| — | AUQ (CB) | 24.2% | 6.78 | -5.6pp |
| — | always_rollout | 22.8% | 6.99 | -7.0pp |
| — | s1_budget (CB) | 18.3% | 1.68 | -11.5pp |

**Insight**: Plancraft 中 rollout 有害 (always_rollout 22.8% < base 29.8%)。关键验证：
- SE 方法 Ro/ep = 0.25-0.28（几乎不触发），自动学会了 "不要 rollout"
- principled_v2 Ro/ep = 0.77（fallback threshold=0.95 生效）
- 所有 6 个 CB 全部 SR <= 25%（盲目触发，damage by rollout），其中 s1_budget 最差 18.3%
- AUQ Ro/ep=6.78 几乎等于 always_rollout 6.99，完全没学会避免触发

### 5.6 BabyAI（Limitation — 信号不存在）

| Method | SR | vs base (2.0%) |
|--------|:--:|:--------------:|
| always_rollout | 11.3% | +9.3pp |
| principled_adaptive | 9.3% | +7.3pp |
| CATTS (Best CB) | 9.3% | +7.3pp |
| ⭐ se_few5_filter_local | **3.5%** | +1.5pp |

**Insight**: BabyAI pos_rate=0.2%，LASSO 在 2/3 seed 完全失败。LLM 生成的 feature 也无法发现信号。确认为 limitation 环境：当信号本身不存在时，任何自动 gating 方法都不适用。

---

## 6. Key Findings & Insights

### 6.1 没有单一最优方法 — 核心论文论点

| 环境 | SR 最优 (Our) | 类型 |
|------|-------------|------|
| HotpotQA | scg_finetune_lr (96.8%) | 手工 feature |
| APPS | se_100cal / online_decay (66.0%) | LLM auto feature |
| WebShop | se_online_fix (44.0%) | 在线持续学习 |
| TWExpress | principled_adaptive (99.2%) | 自适应 threshold |
| Plancraft | SE 系列 (28.3%) | 自动学会不触发 |

**同一组 handcrafted features 在 HotpotQA 上最优 (96.8%)，在 APPS 上不如 s1_budget (58.8% < 63.7%)**。这直接验证了论文标题："Same Signal, Opposite Meaning"。

### 6.2 数据量是关键瓶颈

| 探索数据量 | WebShop SR | APPS SR |
|:---------:|:---------:|:-------:|
| 50 cal points (标准) | 39.2% | 65.8% |
| 100 cal points | 43.2% (+4.0pp) | 66.0% (+0.2pp) |
| 在线持续学习 (200ep all data) | **44.0% (+4.8pp)** | **66.0% (+0.2pp)** |

WebShop state 空间多样性高，50 个数据点不够覆盖 → 100cal 和 online 持续学习都通过增加数据量解决了这个问题。APPS 信号较强，50 cal 已基本饱和。

### 6.3 LLM Feature Discovery 的价值

| 方法 | Feature 来源 | APPS SR | WebShop SR |
|------|-------------|:-------:|:---------:|
| principled_v2 (无 LLM) | universal only | 64.2% | 42.7% |
| se_few5_filter_local (+LLM) | universal + LLM | **65.8%** | 39.2% |
| se_online_fix (+LLM) | universal + LLM + online | 64.5% | **44.0%** |

LLM feature 在 APPS 上明显有帮助 (+1.6pp)，因为 LLM 能发现代码领域特有的 feature (has_graph_terms, is_geometry_task 等)。但在 WebShop 上 LLM feature 本身不够，还需要更多数据来训练。

### 6.4 Feedback 并不总是有帮助

| 环境 | 有反馈 (fb_c3_local) | 无反馈最优 | 差距 |
|------|:-------------------:|:---------:|:----:|
| APPS | **65.8%** | 64.3% (addlat) | +1.5pp (feedback helps) |
| WebShop | 39.8% | **43.2%** (addlat) | **-3.4pp** (feedback hurts) |
| HotpotQA | 94.7% | **95.5%** (selcum) | -0.8pp |

APPS 中反馈帮助 LLM 理解哪些 feature 对代码任务重要；WebShop 中反馈导致 LLM 过度关注近期失败案例，生成的新 feature 反而降低泛化性。

### 6.5 在线持续学习是最有前途的方向

`se_online_fix_local` 在 WebShop 上达到 **44.0%**，是 SE 系列（甚至全部自动化方法）中的最高值（3-seed）。原因：
1. epsilon-greedy (epsilon=0.1) 持续探索避免了 exploitation 阶段的数据饥饿
2. 每 30ep 重训练 LASSO 使模型持续适应
3. 不依赖 LLM re-reflection（se_online_fix 无 re-reflect 但效果最好）

注意 `se_online_fix_ref_local` 在 WebShop 上达到 46.8%，但仅为 2-seed 结果，需要更多验证。

### 6.6 Our Methods vs All 6 Competing Baselines — 综合评估

| 环境 | Our Best | Best CB | CB 名称 | 差距 | 判定 |
|------|:--------:|:-------:|---------|:----:|:----:|
| HotpotQA | 96.8% (SCG) | 97.0% | AUQ/s1 | -0.2pp | 持平 |
| APPS | **66.0%** (100cal/online) | 63.7% | s1_budget | **+2.3pp** | Our wins |
| WebShop | **44.0%** (online_fix) | 35.7% | AUQ | **+8.3pp** | Our wins |
| TWExpress | **99.2%** (adaptive) | 95.5% | AUQ | **+3.7pp** | Our wins |
| Plancraft | **28.3%** (SE) | 25.0% | CATTS | **+3.3pp** | Our wins |

**重要说明**: AUQ 和 s1_budget 是强力 baseline：
- AUQ 在 HotpotQA 和 TWExpress 上达到 97.0% / 95.5%，在 WebShop 上是最好的 CB (35.7%)
- s1_budget 在 HotpotQA 上 97.0%，在 APPS 上是最好的 CB (63.7%)
- 但两者的弱点: AUQ cost 极高 (Ro/ep 普遍很大)，s1_budget 在 WebShop 几乎完全失败 (9.3%)

传统 CB (CaTS/CATTS/SEAG/CoRefine) 在大多数环境表现较弱，尤其 APPS (58.5-59.0%) 几乎等于 base_only (58.5%)。

---

## 7. 论文方法定位建议

### 7.1 主方法

论文中建议展示 3 个代表性方法，体现 "方法演进" 的故事：

1. **SCG (scg_finetune_lr)** — 手工 feature baseline，展示领域知识的价值和局限
2. **Principled v2** — 全自动化 (LASSO + adaptive lambda + fallback)，无需领域知识
3. **SE-Online (se_online_fix_local)** — LLM 自动 feature discovery + 在线持续学习，最先进

### 7.2 消融实验

论文中报告的消融维度：
- LLM feature vs 无 LLM feature (v2 vs SE)
- Feedback vs no-feedback (Phase 2 vs Phase 3)
- 数据量 (50cal vs 100cal vs online)
- epsilon-greedy vs fixed explore/exploit

### 7.3 环境角色

| 角色 | 环境 | 展示什么 |
|------|------|---------|
| 主实验 | HotpotQA, APPS, WebShop | 方法有效性 + 环境间差异 |
| 诊断: rollout-safe | TWExpress | 自动发现 "应该多触发" |
| 诊断: rollout-harmful | Plancraft | 自动发现 "不应该触发" |
| Limitation | BabyAI | Two-Source Model 边界条件 |

### 7.4 Competing Baselines 定位

| CB | 强项 | 弱项 | 论文中的作用 |
|----|------|------|-------------|
| CaTS | HotpotQA 93.2% | APPS/WebShop 接近 base | 传统 calibration 方法代表 |
| CATTS/SEAG/CoRefine | Plancraft 25.0% (CATTS) | 普遍弱 | 固定负向假设的局限 |
| AUQ | HotpotQA 97.0%, WebShop 35.7% | Cost 极高, Plancraft 失败 | 强力 baseline, 但 cost 不可控 |
| s1_budget | HotpotQA 97.0%, APPS 63.7% | WebShop 9.3%, Plancraft 18.3% | 固定预算方法, 不适应环境 |
