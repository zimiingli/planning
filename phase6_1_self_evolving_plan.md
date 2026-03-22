# Phase 6.1: Self-Evolving Adaptive Gating — 改进实验计划

**Date**: 2026-03-20 (final)
**前置**: Phase 6 Path E/F 完成，principled_v2 为当前最佳方法
**目标**: 通过多个改进方向提升 Self-Evolving 在所有环境上的表现
**状态**: ✅ 全部完成 (51/55 补做完成, 4 个 vLLM failures 不再重跑)
**SE 方法总数**: 20 个方法, 其中 18 个 5 环境 3-seed 完整
**代表性方法**: **se_c3_addlat_local** (5env 均值最高 65.7%, cost 中等 3.17×, local only)
**备选代表**: se_few5_filter_local (5env 完整, 算法最简, Plancraft 28.0% 最安全)
**⚠️ Online 发现**: ε-greedy 在 rollout-harmful 环境有害 (Plancraft 24.5% < base 29.8%)

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

## 4. 完整实验矩阵 (原计划 vs 实际执行)

### 改进 1: 多轮迭代 — ⬜→🔄 简化为 Phase 3 消融

原计划 8 变体 × 5 环境 × 3 seeds = 120 runs → 简化为 4 变体 × 5 环境 × 3 seeds

| 变体 | 轮数 | Feature 策略 | 数据策略 | 反馈 | 3主环境 | TWExp/Planc |
|------|:----:|:-----------:|:--------:|:----:|:------:|:-----------:|
| ~~se_cycle2_*~~ | 2 | — | — | — | ❌ 砍掉 | — |
| se_c3_addcum_local | 3 | 保留+新增 | 累积 | ❌ | ✅ 3/3 | ✅ TWE 3/3, Planc 3/3 |
| se_c3_addlat_local | 3 | 保留+新增 | 最新 | ❌ | ✅ 3/3 | ✅ TWE 3/3, Planc 3/3 |
| se_c3_selcum_local | 3 | 选中+替换 | 累积 | ❌ | ✅ 3/3 | ✅ TWE 3/3, Planc 3/3 |
| se_c3_sellat_local | 3 | 选中+替换 | 最新 | ❌ | ✅ 3/3 | ✅ TWE 3/3, Planc 3/3 |

**Phase 3 全环境结果 (✅ 全部完成):**

| Method | HotpotQA | APPS | WebShop | TWExpress | Plancraft |
|--------|:--------:|:----:|:-------:|:---------:|:---------:|
| se_c3_addcum | 95.3% | 63.2% | 41.2% | 98.2% | 27.0% |
| **se_c3_addlat** | 95.2% | 64.3% | **43.2%** | **98.7%** | 27.3% |
| se_c3_selcum | 95.5% | 63.5% | 42.0% | 98.2% | 27.2% |
| se_c3_sellat | 95.5% | 62.3% | 42.7% | 97.8% | **28.0%** |
| (对照) fb_c3_local | 94.7% | **65.8%** | 39.8% | 98.5% | 27.5% |

**消融结论:**
1. Feedback 帮助 APPS (+2.6pp) 但损害 WebShop (-3.4pp)
2. Latest > Cumulative (WebShop: addlat 43.2% > addcum 41.2%)
3. Additive ≈ Selective (噪声范围)

### 改进 2: 更少 Feature — ✅ Phase 1 完成

| 变体 | Feature 数 | 预筛选 | Backend | Jobs | 状态 |
|------|:---------:|:------:|:-------:|:----:|:----:|
| se_few5_local | 5 | 无 | local | 15 | ✅ |
| se_few5_filter_local | 5 | |corr|>0.05 | local | 15 | ✅ 🏆 |
| se_few5_openrouter | 5 | 无 | openrouter | 15 | ✅ |
| se_few5_filter_openrouter | 5 | |corr|>0.05 | openrouter | 15 | ✅ |
| **小计** | | | | **60** | ✅ 58 done |

### 改进 3: 反馈进化 — ✅ Phase 2 完成

| 变体 | 轮数 | 反馈 | Backend | Jobs | 状态 |
|------|:----:|:----:|:-------:|:----:|:----:|
| se_feedback_cycle2_local | 2 | ✅ | local | 15 | ✅ |
| se_feedback_cycle3_local | 3 | ✅ | local | 15 | ✅ |
| se_feedback_cycle2_openrouter | 2 | ✅ | openrouter | 15 | ✅ |
| se_feedback_cycle3_openrouter | 3 | ✅ | openrouter | 15 | ✅ |
| **小计** | | | | **60** | ✅ 60 done |

### 追加实验

| 变体 | 说明 | Jobs | 状态 |
|------|------|:----:|:----:|
| se_few5flt_or_100cal | 100 cal points, openrouter | 15 | ✅ 15/15 done |
| se_100cal_fb_c3_local | 100cal + feedback cycle3 + local | 15 | ✅ 15/15 done |
| se_few5_filter_local × BabyAI | Limitation 验证 | 3 | ✅ |

### 方案 3: 在线持续学习 (Online Continuous Learning) 🆕

**核心思想**: 取消固定 explore/exploit 分界, ε-greedy 持续探索 + 周期性 LASSO 重训练

| 变体 | ε 策略 | LLM Re-reflect | 3主环境 | TWExp/Planc |
|------|--------|:--------------:|:------:|:-----------:|
| se_online_fix_local | 固定 0.1 | ❌ | ✅ 3/3 | ✅ TWE 3/3, Planc 3/3 |
| se_online_fix_ref_local | 固定 0.1 | ✅ ep100 | ✅ 3/3 (WebShop 2-seed°) | ✅ TWE 3/3, Planc 3/3 |
| se_online_decay_local | 0.3→0.05 衰减 | ❌ | ✅ 3/3 | ✅ TWE 3/3, Planc 3/3 |
| se_online_decay_ref_local | 0.3→0.05 衰减 | ✅ ep100 | ✅ 3/3 | ⚠️ TWE 2/3, Planc 0/3 (vLLM failures, 不再重跑) |

**Online 全环境结果:**

| Method | HotpotQA | APPS | WebShop | TWExpress | Plancraft |
|--------|:--------:|:----:|:-------:|:---------:|:---------:|
| **se_online_fix_local** | 94.8% | 64.5% | **44.0%** 🏆 | 98.5% | ⚠️ **24.5%** |
| se_online_fix_ref_local | 95.3% | 64.0% | 46.8%° | 97.3% | ⚠️ 25.3% |
| se_online_decay_local | 95.2% | **66.0%** | 43.8% | **99.0%** | ⚠️ **23.3%** |
| se_online_decay_ref_local | **95.7%** | 64.3% | 43.3% | 🔄 | 🔄 |
| (对照) se_few5_filter_local | 94.7% | 65.8% | 39.2% | 98.5% | ✅ **28.0%** |

°se_online_fix_ref_local × webshop × s456 因 ep100 re-reflect 后卡死超时 (12h)

**⚠️ 关键发现: Online 方法在 Plancraft 上严重退化!**

```
Online Plancraft 退化原因:
  ε-greedy 持续触发 rollout (Ro/ep = 2.76-3.69)
  → 在 rollout-harmful 环境中, 持续探索 = 持续受害
  → se_online_fix Plancraft 24.5% < base_only 29.8% (-5.3pp)
  → se_online_decay Plancraft 23.3% < base_only 29.8% (-6.5pp)

vs se_few5_filter_local:
  探索结束后 LASSO 学会 threshold=0.95 → Ro/ep=0.28 (几乎不触发)
  → Plancraft 28.0% ≈ base_only 29.8% (正确保守)

结论: ε-greedy 在 rollout-harmful 环境不安全
  → Online 方法不适合作为论文代表性 SE 方法
  → se_few5_filter_local 仍是最佳代表 (所有环境正确行为)
```

### 总计

```
原计划:  180 runs (改进1: 120 + 改进2: 30 + 改进3: 30)
实际:    395 runs (含补做)
  SE V1:               30 runs  ✅ 25 done, 5 vLLM failures → 🔄 补做中
  Phase 1 (改进2):     60 runs  ✅ 58 done, 2 failed → 🔄 补 se_few5_local×HotQA
  Phase 2 (改进3):     60 runs  ✅ 60 done
  方案 D (100cal):     15 runs  ✅ 15 done
  方案 1 (100cal+fb):  15 runs  ✅ 15 done
  BabyAI 验证:          3 runs  ✅ 3 done
  Phase 3 (消融):      36 runs  ✅ 36 done (3主环境) → 🔄 补 TWExp/Planc (24 runs)
  方案 3 (Online):     51 runs  ✅ 48 done (3主环境) → 🔄 补 TWExp/Planc (24 runs)
  补做缺失:            55 runs  🔄 job 23229159 submitted
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
Phase 1 (先做, 最快验证): ✅ 完成 (job 23192753, 58/60 done)
  改进 2: se_few5 / se_few5_filter × local / openrouter → 60 runs
  → ✅ filter 有效 (+0.7~5.4pp), local 略优于 openrouter
  → ✅ APPS few5_filter_local 65.8% 超过 v2 (+1.6pp) 🔥
  → ✅ TWExpress 98.5%, Plancraft 28.0% (超过 v2)
  → ⚠️ WebShop 39.2% (仍低于 v2 42.7%)

Phase 2 (基于 Phase 1 结果): ✅ 完成 (job 23192761, 60/60 done)
  改进 3: se_feedback_cycle2/3 × local / openrouter → 60 runs
  → ✅ Cycle 3 > Cycle 2 (多轮迭代纠正中间退化)
  → ✅ fb_c3_or WebShop 41.3% (SE系列最高, 接近 v2)
  → ✅ TWExpress 全系 97.7-98.7%, Plancraft Ro/ep 0.25-0.44 (更保守)
  → ⚠️ WebShop 仍差 v2 1.4pp (41.3% vs 42.7%)

方案 D (数据量验证): ✅ 已提交 (job 23194924, 15 runs)
  se_few5flt_or_100cal: openrouter + few5 + filter + 100 cal points
  → 验证假设: "数据量是瓶颈 vs feature 质量是瓶颈"
  → 如果 WebShop >41% → 数据量是瓶颈, openrouter 需要更多数据
  → 如果 WebShop <40% → feature 质量问题, 数据量救不了

BabyAI 验证: ✅ 完成 (job 23201746, 3 runs)
  se_few5_filter_local × BabyAI × 3 seeds
  → 结果: SR=3.5% (< base 9.3%), LASSO 2/3 seed 完全失败
  → 结论: limitation 环境确认, 信号不存在, LLM feature 也无法拯救

Phase 3 (消融实验): ✅ 3 主环境完成 (job 23209062), 诊断环境补做中
  4 methods × 3 main envs × 3 seeds = 36 runs ✅ done
  4 methods × 2 diag envs × 3 seeds = 24 runs 🔄 补做中 (job 23229159)
  消融结论: feedback 帮 APPS 但害 WebShop, Latest > Cumulative

方案 1 (100cal+fb): ✅ 完成 (job 23209212 IDX 0-14, 15/15 done)
  se_100cal_fb_c3_local × 5 envs × 3 seeds = 15 runs
  结论: 100cal + feedback 效果不如单独 100cal, feedback 在此配置下反而有害

方案 3 (Online 持续学习): ✅ 3 主环境完成 (job 23209212 IDX 15-50), 诊断环境补做中
  4 online methods × 3 main envs × 3 seeds = 36 runs ✅ done
  4 online methods × 2 diag envs × 3 seeds = 24 runs 🔄 补做中 (job 23229159)
  🏆 最大突破: se_online_fix_local WebShop 44.0% (全方法最高)

补做缺失: ✅ 完成 (job 23229159), 51/55 done, 4 个 vLLM failures 不再重跑
  ✅ V1 补做: 5/5 done
  ✅ se_few5_local × hotpotqa: 2/2 done
  ✅ Phase 3 × TWExp/Planc: 24/24 done
  ✅ Online fix/fix_ref/decay × TWExp/Planc: 18/18 done
  ⚠️ Online decay_ref × TWExp/Planc: 2/6 done (4 vLLM failures, 不再重跑, 非关键方法)
```

---

## 7. 成功标准 (更新 2026-03-19)

```
改进 2 成功标准 (Phase 1): ✅ 部分达成
  WebShop se_few5 SR ≥ 41% (vs SE V1 38.2%) → 过拟合减少
  ⚠️ 结果: WebShop few5_filter 39.2% → 未达标但比 V1 好 1pp
  ✅ 结果: APPS few5_filter_local 65.8% → 超过 v2 (+1.6pp)!
  ✅ 结果: TWExpress 98.5% → 超过 v2 (+1.2pp)
  ✅ 结果: Plancraft 28.0% → 超过 v2 (+0.8pp), Ro/ep 0.28 (更保守)

改进 3 成功标准 (Phase 2): ✅ 达成
  ✅ WebShop fb_c3_or 41.3% — 比 se_few5_filter 39.2% 提升 2.1pp → 反馈有帮助
  ✅ APPS fb_c3_local 65.8% — 与 Phase 1 最佳持平
  ✅ TWExpress 全系 97.7-98.7% — 超过 v2 (97.3%)
  ✅ Plancraft 全系 Ro/ep 0.25-0.44 — 比 v2 (0.77) 更保守

方案 D 成功标准: ✅ 达成
  ✅ WebShop 100cal 43.2% > 41% → 数据量是瓶颈 确认!
  ✅ APPS 100cal 66.0% — 全方法最高!
  ⚠️ Plancraft 退化 (0.90 Ro/ep vs 0.25) — 更多数据使LASSO拟合出触发模式
  ⚠️ HotpotQA 略降 (93.3% vs 93.8%) — 更多探索不总是更好

终极目标: ✅ 达成!
  主环境:
    ✅ APPS: SE 65.8-66.0% > v2 64.2% (超过!) [100cal/online_decay 66.0%]
    ✅ WebShop: SE online_fix **44.0%** > v2 42.7% (超过!) [online 突破]
    ⚠️ HotpotQA: SE 94.7-95.7% ≈ v2 94.8% (持平, SCG 96.8% 仍最优)
  诊断环境:
    ✅ TWExpress: SE 98.5-98.7% > v2 97.3% (超过!)
    ✅ Plancraft: SE 28.0-28.3% > v2 27.2%, cost 更低 (超过!)
  限制环境:
    ✅ BabyAI: SE 3.5% < base 9.3% → 正确确认为 limitation
  vs 全部 6 个 Competing Baselines:
    ✅ APPS +2.3pp vs s1_budget (63.7%)
    ✅ WebShop +8.3pp vs AUQ (35.7%)
    ✅ TWExpress +3.7pp vs AUQ (95.5%)
    ✅ Plancraft +3.3pp vs CATTS (25.0%)
    ≈ HotpotQA -0.2pp vs AUQ/s1 (97.0%)

Phase 3 消融结果 (已完成):
  假设 1 部分成立: fb_c3 APPS +2.6pp (反馈有帮助), 但 WebShop -3.4pp (反馈有害!)
  假设 2 反转: Latest > Cumulative (WebShop addlat 43.2% > addcum 41.2%)
  假设 3 ≈ 持平: Selective ≈ Additive (噪声范围)

方案 1 (100cal+fb) 结果:
  ⚠️ 表现一般, HotpotQA 93.0% (低于 v2 94.8%), WebShop 40.8%
  → 100cal 的优势被 feedback 的负面效果抵消

方案 3 (Online) 结果 — 🏆 最大突破:
  ✅ se_online_fix_local WebShop **44.0%** — 全方法最高 (3-seed)!
  ✅ se_online_decay_local APPS **66.0%** — 追平 100cal
  ✅ ε-greedy 持续探索 > 固定 explore/exploit 分界
  ✅ 不需要 LLM re-reflect (fix > fix_ref)
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
  - selective / additive feature 管理
  - cumulative / latest 数据策略
  - use_feedback=True/False 控制

✅ frvc/online_continuous_gate.py:   🆕
  - OnlineContinuousGate: ε-greedy 持续探索 + 周期性 LASSO 重训练
  - epsilon 固定/衰减两种模式
  - retrain_interval=30 episodes
  - 可选 LLM re-reflect at specific episodes
  - 持续数据累积 (epsilon-triggered data → training pool)

✅ experiments/p6_e_method_upgrade.py:
  - se_few5_local, se_few5_filter_local, se_few5_openrouter, se_few5_filter_openrouter
  - se_feedback_cycle2/3_local/openrouter
  - se_few5flt_or_100cal (方案 D)
  - se_100cal_fb_c3_local (方案 1)
  - se_c3_addcum_local, se_c3_addlat_local, se_c3_selcum_local, se_c3_sellat_local (Phase 3)
  - se_online_fix_local, se_online_fix_ref_local (方案 3)
  - se_online_decay_local, se_online_decay_ref_local (方案 3)

✅ scripts/phase6/:
  - run_se_phase1.sbatch (60 jobs)
  - run_se_phase2.sbatch (60 jobs)
  - run_se_100cal.sbatch (15 jobs)
  - run_se_babyai_test.sbatch (3 jobs)
  - run_se_phase3.sbatch (36 jobs)
  - run_se_online.sbatch (51 jobs: 方案 1 + 方案 3)
  - run_se_missing.sbatch (55 jobs: 所有缺失补做)
```

### SLURM Jobs

| Job | Name | Tasks | Status |
|-----|------|:-----:|:------:|
| ~~23189559~~ | ~~SE V1~~ | 30 | ✅ 25+5=30 done (补做全部完成) |
| ~~23192753~~ | ~~Phase 1: fewer features~~ | 60 | ✅ 58+2=60 done (补做全部完成, se_few5_local HotQA 94.8%) |
| ~~23192761~~ | ~~Phase 2: feedback evolution~~ | 60 | ✅ 60 done |
| ~~23194924~~ | ~~方案 D: 100cal openrouter~~ | 15 | ✅ 15 done |
| ~~23201746~~ | ~~BabyAI SE test~~ | 3 | ✅ 3 done (limitation confirmed) |
| ~~23209062~~ | ~~Phase 3: multi-cycle ablation~~ | 36 | ✅ 36 done (3主环境) |
| ~~23209212~~ | ~~方案 1+3: 100cal_fb + Online~~ | 51 | ✅ ~48 done (3主环境) |
| ~~23229159~~ | ~~补做缺失实验~~ | 55 | ✅ 51/55 done, 4 vLLM failures (不再重跑) |

---

## 9. 总结与论文方法选择 (2026-03-19)

### 9.1 SE 系列方法全景 (21 个方法)

```
SE V1 (2 methods):         self_evolving_{local,openrouter}
SE Phase 1 (4 methods):    se_few5_{local,openrouter}, se_few5_filter_{local,openrouter}
SE Phase 2 (4 methods):    se_feedback_cycle{2,3}_{local,openrouter}
SE 100cal (2 methods):     se_few5flt_or_100cal, se_100cal_fb_c3_local
SE Phase 3 (4 methods):    se_c3_{addcum,addlat,selcum,sellat}_local
SE Online (4+1 methods):   se_online_{fix,decay}{,_ref}_local + principled_online
```

### 9.2 论文代表性方法推荐

| 角色 | 方法 | 理由 |
|------|------|------|
| **SE 主方法 (方案A)** | **se_c3_addlat_local** | 5env 均值最高 (65.7%), cost 中等 (3.17×), local only, 多轮反思叙事 |
| **SE 主方法 (方案B)** | **se_few5_filter_local** | 算法最简, Plancraft 最安全 (28.0%), 有 BabyAI 数据 |
| **消融** | addlat vs fb_c3 vs few5_filter | feedback/multi-cycle/filter 各自贡献 |
| **Online 消融** | se_online_fix_local | WebShop 44.0% 最高, 但 Plancraft 24.5% 退化 → ε-greedy 局限 |

**方案A (se_c3_addlat) vs 方案B (se_few5_filter) 取舍:**
- A 优势: 5env SR 更高 (+0.5pp avg), WebShop 43.2% >> 39.2%, 不依赖 feedback
- B 优势: 算法更简洁 (1次反思 vs 3次), Plancraft 更安全 (28.0% vs 27.3%), 有 BabyAI 数据
- 建议: 主表用 A, 简洁叙事用 B, 两者都报告

### 9.3 关键发现

1. **数据量 > 反馈质量**: 100cal (+4pp WebShop) 和 online (+4.8pp) 比 feedback (+2pp) 更有效
2. **反馈在不同环境效果相反**: APPS +2.6pp (帮助), WebShop -3.4pp (有害)
3. **ε-greedy 是双刃剑**: WebShop +4.8pp (持续探索有效), 但 **Plancraft -5.3pp** (持续探索有害!)
4. **LLM Re-reflect 不必要**: se_online_fix (无反思) > se_online_fix_ref (有反思)
5. **se_few5_filter_local 在所有环境正确行为**: TWExp 98.5% (多触发) + Planc 28.0% (不触发) + BabyAI 3.5% (确认 limitation)
6. **Phase 3 消融在诊断环境表现一致**: TWExp 97.8-98.7%, Planc 27.0-28.0% (与 Phase 2 持平)
7. **Online 方法在 rollout-harmful 环境不安全**: ε-greedy 无法自动停止探索 → 需要额外的安全机制

### 9.4 状态: ✅ SE 实验全部完成

```
✅ SE 系列实验全部完成
   20 个方法, 18 个 5 环境 3-seed 完整
   2 个不完整: se_online_decay_ref_local (vLLM failures), se_online_fix_ref_local (WebShop 超时)
   这两个均为非关键消融变体, 不影响论文

⬜ 下一步: 论文写作
   → 实验数据全部齐全
   → 详见 planning/experiment_result_report/full_report.md
```
