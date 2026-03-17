# Phase 6.1: Self-Evolving Adaptive Gating — 改进实验计划

**Date**: 2026-03-15
**前置**: Phase 6 Path E/F 完成，principled_v2 为当前最佳方法
**目标**: 通过三个改进方向提升 Self-Evolving 在所有环境上的表现

---

## 0. 背景与动机

### 当前 Self-Evolving (V1) 的问题

| 环境 | SE local SR | adaptive SR | 差距 | 根因 |
|------|:----------:|:----------:|:----:|------|
| HotpotQA | 95.0% | 95.7% | -0.7pp | ≈持平 |
| APPS | 64.2% | 64.7% | -0.5pp | ≈持平 |
| **WebShop** | **38.2%** | **43.0%** | **-4.8pp** | 过拟合 (30+ features, 50 samples) |
| TWExpress | 98.0% | 99.2% | -1.2pp | 数据不足 |
| Plancraft | 26.5% | 22.7% | +3.8pp | fallback 有效 |

**核心问题**: LLM 生成了 15-18 个 feature，但 50 ep 探索数据不够支撑这么多 feature 的 LASSO 学习 → 过拟合。

### 三个改进方向

| # | 改进 | 目标 | 预期效果 |
|---|------|------|---------|
| **1** | 多轮迭代 | 增加训练数据量 | 50→100→150 ep 数据，减少过拟合 |
| **2** | 更少更精 feature | 减少 feature 数量 | 5 个 feature vs 15-18 个，降低过拟合 |
| **3** | 反馈式进化 | 用上一轮结果指导下一轮 | LLM 基于反馈改进 feature extractor |

---

## 1. 改进 1: 多轮迭代 (Multi-Cycle)

### 设计决策

| 决策 | 选择 |
|------|------|
| 轮数 | A: 2 轮 + B: 3 轮（都做） |
| Feature 管理 | B: 保留旧 feature + 新增 + C: 保留选中的 + 替换未选中的（都做） |
| 训练数据 | A: 累积全部 + B: 只用最新 cycle（都做） |

### 实验变体

```
改进 1 共 8 个变体 = 2 (轮数) × 2 (feature 管理) × 2 (数据策略)

命名规则: se_cycle{轮数}_{feature策略}_{数据策略}

  se_cycle2_additive_cumulative    2轮, 保留旧+新增, 累积数据
  se_cycle2_additive_latest        2轮, 保留旧+新增, 只用最新
  se_cycle2_selective_cumulative   2轮, 保留选中+替换, 累积数据
  se_cycle2_selective_latest       2轮, 保留选中+替换, 只用最新
  se_cycle3_additive_cumulative    3轮, 保留旧+新增, 累积数据
  se_cycle3_additive_latest        3轮, 保留旧+新增, 只用最新
  se_cycle3_selective_cumulative   3轮, 保留选中+替换, 累积数据
  se_cycle3_selective_latest       3轮, 保留选中+替换, 只用最新
```

### Episode 分配

```
2 轮方案 (200 ep):
  Cycle 1: Explore 50ep → Reflect → Exploit 50ep     [数据: 50 triggered]
  Cycle 2: Re-Reflect (用 C1 数据) → Exploit 100ep   [数据: 50+exploit_triggered]

3 轮方案 (200 ep):
  Cycle 1: Explore 50ep → Reflect → Exploit 30ep     [数据: 50 triggered]
  Cycle 2: Re-Reflect → Exploit 30ep                 [数据: 50+C1_triggered]
  Cycle 3: Re-Reflect → Exploit 40ep                 [数据: 50+C1+C2_triggered]
```

### Feature 管理策略

```
Additive (B):
  Cycle 1: universal(11) + LLM_1(5) = 16 features
  Cycle 2: universal(11) + LLM_1(5) + LLM_2(5) = 21 features
  Cycle 3: universal(11) + LLM_1(5) + LLM_2(5) + LLM_3(5) = 26 features

Selective (C):
  Cycle 1: universal(11) + LLM_1(5) = 16 → LASSO 选 8
  Cycle 2: selected_8 + LLM_2(5) = 13 → LASSO 选 8
  Cycle 3: selected_8 + LLM_3(5) = 13 → LASSO 选 8
  → feature 总数保持可控
```

### 实验矩阵

```
8 变体 × 5 环境 × 3 seeds = 120 runs
仅用 local backend (Qwen3-4B)
每 run ~15min (HotpotQA/APPS) ~ 2h (WebShop/TWExpress)
预估 GPU 时间: ~60-80h (9 并发 ≈ 8-10h wall time)
```

---

## 2. 改进 2: 更少更精 Feature (Fewer Features)

### 设计决策

| 决策 | 选择 |
|------|------|
| Feature 数量 | 5 个 |
| 假设说明 | 不需要 |
| Feature 预筛选 | 加和不加都尝试 |

### Prompt 修改

```
当前 prompt:
  "Extract 5-15 meaningful features..."

改进 prompt:
  "Extract exactly 5 features that are most likely to predict
   rollout utility. Focus on the most discriminative patterns
   you observed between useful and not-useful rollout cases.
   Quality over quantity — each feature should capture a distinct signal."
```

### Feature 预筛选

```
不加预筛选 (se_few5):
  LLM 生成 5 features → 直接加入 LASSO pool

加预筛选 (se_few5_filter):
  LLM 生成 5 features → 计算每个与 utility 的 |correlation|
  → 只保留 |corr| > 0.05 的 → 加入 LASSO pool
```

### 实验变体

```
改进 2 共 2 个变体:
  se_few5              5 features, 无预筛选
  se_few5_filter       5 features, 有预筛选 (|corr|>0.05)

2 变体 × 5 环境 × 3 seeds = 30 runs
```

---

## 3. 改进 3: 反馈式进化 (Feedback-Guided)

### 设计决策

| 决策 | 选择 |
|------|------|
| 反馈内容 | b (importance) + c (SR/trigger rate) + d (失误案例) + e (成功案例) |
| 代码生成方式 | 重新生成（不给旧代码） |
| 退化防护 | 方案 B: 合并新旧 feature，让 LASSO 选 |

### 反馈 Prompt 模板

```
第二轮 prompt:

"In the previous cycle, you generated features and we trained a gating model.
Here are the results:

## Previous Results
- Success Rate: {sr:.1%} (vs base {base_sr:.1%})
- Trigger Rate: {trigger_rate:.1%}
- Features selected by LASSO (with importance):
  {selected_features_with_coefficients}

## Failure Cases (triggered rollout but utility was 0):
  State: {fail_state_1}
  Action: {fail_action_1}

  State: {fail_state_2}
  Action: {fail_action_2}

## Success Cases (correctly skipped, utility was 0):
  State: {success_state_1}
  Action: {success_action_1}

## Task
Based on this feedback, generate a NEW feature extractor (5 features)
that addresses the failure cases. What patterns did the previous features miss?"
```

### 与改进 1 的组合

改进 3 需要至少 2 轮才有意义（第 1 轮没有反馈）。因此：

```
se_feedback_cycle2:
  Cycle 1: Explore 50ep → Reflect (无反馈) → LASSO → Exploit 50ep
  Cycle 2: Reflect (有反馈: SR, importance, 失误/成功案例)
           → 生成新 feature → 合并旧+新 → LASSO → Exploit 100ep

se_feedback_cycle3:
  Cycle 1: → Reflect (无反馈) → Exploit 30ep
  Cycle 2: → Reflect (有反馈 from C1) → Exploit 30ep
  Cycle 3: → Reflect (有反馈 from C1+C2) → Exploit 40ep
```

### 实验变体

```
改进 3 共 2 个变体:
  se_feedback_cycle2     2轮反馈进化, 累积数据, selective feature
  se_feedback_cycle3     3轮反馈进化, 累积数据, selective feature

2 变体 × 5 环境 × 3 seeds = 30 runs
```

---

## 4. 完整实验矩阵

### 改进 1: 多轮迭代

| 变体 | 轮数 | Feature 策略 | 数据策略 | Jobs |
|------|:----:|:-----------:|:--------:|:----:|
| se_cycle2_additive_cumulative | 2 | 保留+新增 | 累积 | 15 |
| se_cycle2_additive_latest | 2 | 保留+新增 | 最新 | 15 |
| se_cycle2_selective_cumulative | 2 | 选中+替换 | 累积 | 15 |
| se_cycle2_selective_latest | 2 | 选中+替换 | 最新 | 15 |
| se_cycle3_additive_cumulative | 3 | 保留+新增 | 累积 | 15 |
| se_cycle3_additive_latest | 3 | 保留+新增 | 最新 | 15 |
| se_cycle3_selective_cumulative | 3 | 选中+替换 | 累积 | 15 |
| se_cycle3_selective_latest | 3 | 选中+替换 | 最新 | 15 |
| **小计** | | | | **120** |

### 改进 2: 更少 Feature

| 变体 | Feature 数 | 预筛选 | Jobs |
|------|:---------:|:------:|:----:|
| se_few5 | 5 | 无 | 15 |
| se_few5_filter | 5 | |corr|>0.05 | 15 |
| **小计** | | | **30** |

### 改进 3: 反馈进化

| 变体 | 轮数 | 反馈内容 | Jobs |
|------|:----:|---------|:----:|
| se_feedback_cycle2 | 2 | importance + SR + 案例 | 15 |
| se_feedback_cycle3 | 3 | importance + SR + 案例 | 15 |
| **小计** | | | **30** |

### 总计

```
改进 1: 120 runs
改进 2:  30 runs
改进 3:  30 runs
总计:   180 runs

全部用 local backend (Qwen3-4B), 不需要 HF engine
GPU_UTIL=0.75, 每 run 预估 15min-2h
9 并发, 预估 wall time: 15-25h
```

---

## 5. 对比基线

每个变体的结果将与以下基线对比:

| 基线 | 含义 |
|------|------|
| SCG | 手工 feature + LR (当前主方法) |
| adaptive† | 自适应 λ, exploitation-only (当前最佳自动化) |
| v2 | adaptive + fallback (Plancraft 修复) |
| SE V1 local | 当前 self-evolving (单轮, 15-18 features) |

### 评估指标

```
主指标:
  SR (Success Rate)
  Cost (×base)
  CAGC (GapClosed% / Cost)

辅助指标:
  Ro/ep (rollouts per episode)
  Feature selection stability (3 seeds 间选的 feature 一致性)
  LLM feature 使用率 (LASSO 选中了几个 LLM feature / 总生成数)
```

---

## 6. 实施优先级

```
Phase 1 (先做, 最快验证): ✅ 已提交 (job 23192753, 60 runs)
  改进 2: se_few5 / se_few5_filter × local / openrouter → 60 runs
  → 验证 "减少 feature 数量" 是否解决过拟合
  → 初步结果: filter 有效 (+0.7~5.4pp), local ≈ openrouter
  → APPS few5_filter_local 65.8% 超过 v2 (64.2%) 🔥
  → WebShop 仍低于 v2 (39.2% vs 42.7%) ❌

Phase 2 (基于 Phase 1 结果): ✅ 已提交 (job 23192761, 60 runs)
  改进 3: se_feedback_cycle2/3 × local / openrouter → 60 runs
  → 验证反馈进化 + 数据累积是否进一步提升
  → 等待结果中

方案 D (数据量验证): ✅ 已提交 (job 23194924, 15 runs)
  se_few5flt_or_100cal: openrouter + few5 + filter + 100 cal points
  → 验证假设: "数据量是瓶颈 vs feature 质量是瓶颈"
  → 如果 WebShop >41% → 数据量是瓶颈, openrouter 需要更多数据
  → 如果 WebShop <40% → feature 质量问题, 数据量救不了

Phase 3 (全量搜索): ⬜ 待 Phase 1-2 + 方案 D 结果指导
  基于 Phase 1 已确认:
    ✅ filter > 无 filter → 只跑 filter
    ≈ local ≈ openrouter → 待方案 D 验证后决定 backend
  可简化为 2(cycles) × 2(feature策略) × 2(数据策略) × 1(backend) × 5 envs × 3 seeds
  = 60 runs (从原计划 120 减半)
```

---

## 7. 成功标准

```
改进 2 成功标准 (Phase 1):
  WebShop se_few5 SR ≥ 41% (vs SE V1 38.2%) → 过拟合减少
  ⚠️ 当前结果: WebShop few5_filter 39.2% → 未达标但比 V1 好 1pp
  ✅ 当前结果: APPS few5_filter_local 65.8% → 超过 v2!

改进 3 成功标准 (Phase 2):
  至少 1 个环境 SR 比 se_few5 提升 ≥ 1pp → 反馈有帮助
  LLM 在第 2 轮生成了与第 1 轮不同的 feature → 真正在"进化"
  (等待结果)

方案 D 成功标准:
  WebShop 100cal openrouter SR > 41% → 数据量是瓶颈 ✅
  WebShop 100cal openrouter SR < 40% → feature 质量问题 ❌
  openrouter 100cal > local 50cal → Claude 需要更多数据
  (等待结果)

终极目标:
  最优 SE 变体在主环境 (HotpotQA/APPS/WebShop) 上:
    SR ≈ v2 且 cost ≤ v2
  在对比环境 (TWExpress/Plancraft) 上:
    SR ≥ v2 且 cost ≤ v2
```

---

## 8. 代码实现状态

### 已实现

```
✅ frvc/self_evolving_gate.py:
  - max_llm_features 参数 (5/15)
  - feature_filter (correlation |corr|>0.05)
  - 支持 local + openrouter backend

✅ frvc/self_evolving_v2.py:
  - SelfEvolvingGateV2: multi-cycle + feedback
  - on_episode_end(): cycle boundary 检查
  - _build_feedback_text(): LASSO importance + SR + 失误/成功案例
  - selective feature 管理 + cumulative 数据策略

✅ experiments/p6_e_method_upgrade.py:
  - se_few5_local, se_few5_filter_local, se_few5_openrouter, se_few5_filter_openrouter
  - se_feedback_cycle2/3_local/openrouter
  - se_few5flt_or_100cal (方案 D)

✅ scripts/phase6/:
  - run_se_phase1.sbatch (60 jobs)
  - run_se_phase2.sbatch (60 jobs)
  - run_se_100cal.sbatch (15 jobs)
```

### SLURM Jobs

| Job | Name | Tasks | Status |
|-----|------|:-----:|:------:|
| ~~23189559~~ | ~~SE V1~~ | 30 | ✅ done (5 failed: old bug) |
| **23192753** | **Phase 1: fewer features** | **60** | **🔄 ~40 done, ~6 running** |
| **23192761** | **Phase 2: feedback** | **60** | **⬜ Pending** |
| **23194924** | **方案 D: 100cal openrouter** | **15** | **⬜ Pending** |
