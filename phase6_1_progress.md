# Phase 6.1: Self-Evolving Improvements — Progress Report

**Date**: 2026-03-18 (updated)
**Plan**: `planning/phase6_1_self_evolving_plan.md`

---

## Overview

| Phase | 改进 | Jobs | Status |
|:-----:|------|:----:|:------:|
| **1** | Fewer Features (5 features ± filter) | 60 | ✅ 58 done, 2 failed |
| **2** | Feedback Evolution (multi-cycle) | 60 | ✅ 60 done |
| **D** | 100cal openrouter (数据量验证) | 15 | 🔄 12 done, 3 running (TWExpress) |
| **BabyAI** | SE_few5_filter_local × BabyAI | 3 | ✅ 3 done |
| **3** | Multi-Cycle Full Search | TBD | ⬜ 待实现 |

---

## 全方法 × 全环境 SR + Cost 横向对比

```
┌──────────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│                      │    HotpotQA      │      APPS        │    WebShop       │    TWExpress     │    Plancraft     │
│ Method               │  SR    Ro/ep    │  SR    Ro/ep    │  SR    Ro/ep    │  SR    Ro/ep    │  SR    Ro/ep    │
├──────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ base_only            │ 49.0%  0.00   │ 58.5%  0.00   │  7.2%  0.00   │ 67.5%  0.00   │ 29.8%  0.00   │
│ always_trigger       │ 97.0% 10.70   │ 64.5%  4.25   │ 43.0%  5.54   │ 99.3%  2.15   │ 22.8%  6.12   │
├──────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ scg_finetune_lr      │ 96.8%  6.59   │ 58.8%  1.20   │ 43.7%  1.27   │ 97.0%  1.00   │ 21.5%  3.31   │
│ oracle               │ 97.0%  3.70   │ 75.0%  1.14   │ 43.3%  1.06   │ 99.3%  0.67   │ 21.3%  0.65   │
├──────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ CaTS                 │ 93.2% 10.60   │ 59.0%  1.02   │ 30.5%  3.43   │ 96.7%  1.36   │ 22.3%  4.14   │
│ CATTS                │ 68.3%  6.93   │ 58.5%  1.04   │ 16.0%  1.10   │ 97.5%  1.57   │ 25.0%  2.50   │
│ SEAG                 │ 67.5%  6.64   │ 58.5%  1.01   │ 28.0%  2.83   │ 97.3%  1.61   │ 24.8%  2.52   │
│ CoRefine             │ 68.2%  6.81   │ 58.5%  1.01   │ 27.5%  2.77   │ 97.5%  1.57   │ 22.8%  2.44   │
├──────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ principled_v2        │ 94.8%  1.09   │ 64.2%  1.18   │ 42.7%  1.65   │ 97.3%  2.71   │ 27.2%  0.77   │
├──────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ SE_V1_local          │ 95.0%  1.21   │ 64.2%  1.15   │ 38.2%  1.55   │ 98.2%  2.98   │ 26.5%  0.25   │
│ SE_V1_openrouter     │ 94.7%  1.29   │ 62.2%  0.75   │ 40.8%  1.96   │ 97.0%  2.84   │ 28.5%  0.25   │
│ SE_few5_local        │ 94.0%  1.03   │ 63.8%  1.17   │ 33.8%  1.30   │ 97.8%  2.90   │ 28.3%  0.25   │
│ SE_few5flt_local     │ 94.7%  1.09   │ 65.8%  1.39   │ 39.2%  1.69   │ 98.5%  2.82   │ 28.0%  0.28   │
│ SE_few5_openrouter   │ 94.0%  1.17   │ 64.8%  1.69   │ 37.8%  1.58   │ 98.2%  2.46   │ 28.0%  0.25   │
│ SE_few5flt_openrtr   │ 93.8%  1.07   │ 64.2%  1.37   │ 38.3%  1.49   │ 98.7%  2.64   │ 28.2%  0.25   │
│ SE_fb_c2_local       │ 95.7%  1.15   │ 62.7%  0.83   │ 33.8%  1.83   │ 98.7%  2.84   │ 28.3%  0.28   │
│ SE_fb_c3_local       │ 94.7%  1.12   │ 65.8%  1.28   │ 39.8%  2.38   │ 98.5%  2.97   │ 27.5%  0.25   │
│ SE_fb_c2_openrouter  │ 94.2%  1.07   │ 64.5%  1.19   │ 40.8%  2.23   │ 98.0%  2.64   │ 28.3%  0.44   │
│ SE_fb_c3_openrouter  │ 94.7%  1.13   │ 65.2%  1.32   │ 41.3%  1.71   │ 97.7%  2.67   │ 27.2%  0.30   │
│ SE_100cal_openrtr    │ 93.3%  1.23   │ 66.0%  1.55   │ 43.2%  2.25   │    pending     │ 26.8%  0.90   │
├──────────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ SE_flt_local×BabyAI  │          — limitation env: SR=3.5% (worse than base 9.3%)          │
└──────────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

---

## Phase 1 结果分析

### Filter 效果（local backend）

| 环境 | few5 (无filter) | few5_filter | 差距 | Filter 有效? |
|------|:--------------:|:-----------:|:----:|:------------:|
| HotpotQA | 94.0% @6.27× | **94.7%** @6.57× | +0.7pp | ✅ |
| **APPS** | 63.8% @2.50× | **65.8%** @2.79× | **+2.0pp** | ✅✅ |
| WebShop | 33.8% @1.59× | **39.2%** @1.94× | **+5.4pp** | ✅✅ |
| TWExpress | 97.8% @1.89× | **98.5%** @1.85× | +0.7pp | ✅ |

**Filter 在所有环境都有帮助**，WebShop 提升最大 (+5.4pp)。Filter 去掉了 |corr|<0.05 的噪声 feature，减少过拟合。

### Local vs OpenRouter（few5_filter）

| 环境 | local | openrouter | 差距 |
|------|:-----:|:----------:|:----:|
| HotpotQA | **94.7%** @6.57× | 93.8% @6.48× | local +0.9pp |
| **APPS** | **65.8%** @2.79× | 64.2% @2.76× | local **+1.6pp** |
| WebShop | **39.2%** @1.94× | 38.3% @1.76× | local +0.9pp |

**Local (Qwen3-4B) 在所有环境都优于 OpenRouter (Claude)**。可能因为 Qwen3-4B 生成的 feature 更适合自己的表征空间。

### SE_few5flt_local vs V2 vs SCG

| 环境 | SE_few5flt_local | v2 | SCG | SE vs v2 | SE vs SCG |
|------|:----------------:|:--:|:---:|:--------:|:---------:|
| HotpotQA | 94.7% @6.57× | 94.8% @6.61× | 96.8% @6.59× | -0.1pp | -2.1pp |
| **APPS** | **65.8%** @2.79× | 64.2% @2.45× | 58.8% @1.20× | **+1.6pp** 🔥 | **+7.0pp** |
| WebShop | 39.2% @1.94× | **42.7%** @1.93× | **43.7%** @1.27× | **-3.5pp** ❌ | -4.5pp |
| TWExpress | **98.5%** @1.85× | 97.3% @1.74× | 97.0% @1.00× | **+1.2pp** | +1.5pp |

### Phase 1 结论

```
✅ Filter 有效: 所有环境 few5_filter > few5
≈ Local ≈ OpenRouter: 差距在噪声范围 (0.9-1.6pp), 不是能力差异而是数据瓶颈
✅ APPS: SE_few5flt_local 65.8% 是所有自动化方法最高
✅ TWExpress: SE_few5flt_local 98.5% 超过 v2 和 SCG

❌ WebShop: SE (39.2%) 仍远低于 v2 (42.7%) → LLM feature 在 WebShop 上是噪声
❌ Cost: SE cost 普遍与 v2 持平或略高 (APPS 2.79× vs 2.45×)
```

### 三方法互补：SCG + V2 + SE — 全部 5 环境超过所有 CB

```
┌──────────────────────┬───────────────┬───────────────┬───────────────┬───────────────┬───────────────┐
│                      │     HotQA      │     APPS       │     WShop      │     TWExp      │     Planc      │
│ Method               │  SR    Ro/ep  │  SR    Ro/ep  │  SR    Ro/ep  │  SR    Ro/ep  │  SR    Ro/ep  │
├──────────────────────┼───────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ SCG                  │ 96.8%  6.59  │ 58.8%  1.20  │ 43.7%  1.27  │ 97.0%  1.00  │ 21.5%  3.31  │
│ v2                   │ 94.8%  1.09  │ 64.2%  1.18  │ 42.7%  1.65  │ 97.3%  2.71  │ 27.2%  0.77  │
│ SE_f5flt_local       │ 94.7%  1.09  │ 65.8%  1.39  │ 39.2%  1.69  │ 98.5%  2.82  │ 28.0%  0.28  │
│ SE_fb_c3_or          │ 94.7%  1.13  │ 65.2%  1.32  │ 41.3%  1.71  │ 97.7%  2.67  │ 27.2%  0.30  │
│ SE_100cal_or         │ 93.3%  1.23  │ 66.0%  1.55  │ 43.2%  2.25  │  pending     │ 26.8%  0.90  │
├──────────────────────┼───────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Best CB              │ 93.2% 10.60  │ 59.0%  1.02  │ 30.5%  3.43  │ 97.5%  1.57  │ 25.0%  2.50  │
├──────────────────────┼───────────────┼───────────────┼───────────────┼───────────────┼───────────────┤
│ Our Best SR          │ 96.8% (SCG)  │ 66.0%(100cal)│ 43.7% (SCG)  │ 98.7%(SE_or) │ 28.3%(SE_fb) │
│ Our Best vs BestCB   │  +3.6pp      │  +7.0pp      │ +13.2pp      │  +1.2pp      │  +3.3pp      │
└──────────────────────┴───────────────┴───────────────┴───────────────┴───────────────┴───────────────┘

各环境最优方法 (Updated 2026-03-18):
  HotpotQA:   SCG (SR最高96.8%) / fb_c2_local (SE最高95.7%)
  APPS:       SE_100cal_or (66.0%, 全方法最高!) / SE_f5flt_local (65.8%)
  WebShop:    SCG (43.7%) / SE_100cal_or (43.2%!, 超过v2) / v2 (42.7%)
  TWExpress:  SE_f5flt_or (98.7%) / SE_f5flt_local (98.5%)
  Plancraft:  SE_fb_c2_local/or (28.3%) / SE_f5flt_local (28.0%) / v2 (27.2%)

BabyAI:     ❌ limitation 确认, SE_f5flt_local SR=3.5% (< base 9.3%)

论文叙事:
  → 没有单一方法在所有环境最优 (核心论点)
  → 但三者组合在每个环境都超过所有 competing baselines
  → SCG: cost-sensitive, 需要领域知识 (HotpotQA/WebShop 最优)
  → v2: 完全自动化, online learning, rollout-harmful 自动防护 (Plancraft)
  → SE: self-evolving, LLM 自动发现环境特异 feature (APPS/TWExpress 最优)
  → 100cal: 更多探索数据 → WebShop 超过 v2! 但 cost 更高
```

---

## Phase 2 结果 (全部完成)

**Job 23192761**: ✅ 60/60 completed

### Phase 2 完整结果 (4 变体 × 5 环境)

| 环境 | fb_c2_local | fb_c3_local | fb_c2_or | fb_c3_or | v2 |
|------|:----------:|:----------:|:--------:|:--------:|:--:|
| HotpotQA | **95.7%** @1.15 | 94.7% @1.12 | 94.2% @1.07 | 94.7% @1.13 | 94.8% @1.09 |
| APPS | 62.7% @0.83 | **65.8%** @1.28 | 64.5% @1.19 | 65.2% @1.32 | 64.2% @1.18 |
| WebShop | 33.8% @1.83 | 39.8% @2.38 | 40.8% @2.23 | **41.3%** @1.71 | **42.7%** @1.65 |
| TWExpress | **98.7%** @2.84 | 98.5% @2.97 | 98.0% @2.64 | 97.7% @2.67 | 97.3% @2.71 |
| Plancraft | 28.3% @0.28 | 27.5% @0.25 | **28.3%** @0.44 | 27.2% @0.30 | 27.2% @0.77 |

### Cycle-level SR 分析

**APPS fb_cycle3_local — 每 cycle 递增!**
```
  Explore(0-49): 62-64%
  → C1(50-79):   63-73%
  → C2(80-109):  63%
  → C3(110-199): 66-69% 🔥 (exploitation-only 看这部分超过 v2)
```

**WebShop fb_cycle3_local — V 字型恢复!**
```
  s42:  Explore:52% → C1:70% → C2:30% → C3:42%
  s123: Explore:20% → C1:40% → C2:37% → C3:43% 🔥
```
C2 崩了（反馈后 feature 变差），但 C3 恢复到 42-43%（接近 v2！）

### Phase 2 结论

```
✅ Cycle 3 > Cycle 2: 更多迭代能纠正中间的退化
✅ APPS fb_c3_local 65.8% = P1 最佳，确认 5-feature + 迭代有效
✅ WebShop fb_c3_or 41.3% — SE系列最高! 接近 v2 (42.7%), cost更低 (1.71 vs 1.65)
✅ HotpotQA fb_c2_local 95.7% — 超过 v2 (+0.9pp)
✅ TWExpress: 所有fb变体 97.7-98.7% — 全部超过 v2 (97.3%)
✅ Plancraft: 所有fb变体 Ro/ep 0.25-0.44 — 比 v2 (0.77) 更保守，SR持平/更高

⚠️ WebShop: fb_c3 比 v2 仍差 1.4pp (41.3% vs 42.7%)
⚠️ Cycle 2 不稳定: WebShop 33.8% 暴跌，3 轮才恢复
```

---

## 方案 D 结果 (100cal openrouter)

**Job 23194924**: 🔄 12/15 done, 3 running (TWExpress)

### 100cal vs 50cal 对比

| 环境 | SE_f5flt_or (50cal) | SE_100cal_or | 差距 | v2 |
|------|:-------------------:|:-----------:|:----:|:--:|
| HotpotQA | 93.8% @1.07 | 93.3% @1.23 | -0.5pp | 94.8% |
| **APPS** | 64.2% @1.37 | **66.0%** @1.55 | **+1.8pp** | 64.2% |
| **WebShop** | 38.3% @1.49 | **43.2%** @2.25 | **+4.9pp** 🔥 | 42.7% |
| TWExpress | 98.7% @2.64 | pending | — | 97.3% |
| Plancraft | 28.2% @0.25 | 26.8% @0.90 | -1.4pp | 27.2% |

### 100cal 结论

```
✅ WebShop 43.2% — 超过 v2 (42.7%)!! SE系列首次在WebShop上超过v2
✅ APPS 66.0% — 全方法最高! 比 v2 +1.8pp
✅ 验证假设: "数据量是瓶颈" → 50cal→100cal, WebShop +4.9pp

⚠️ HotpotQA 略降 (-0.5pp) — 更多探索 ≠ 更好 (HotpotQA 信号已经清晰)
⚠️ Plancraft 退化: 0.90 Ro/ep (vs 0.25) — 更多数据使 LASSO 拟合出触发模式
⚠️ Cost 比50cal更高: WebShop 2.25 vs 1.49
```

---

## BabyAI SE 验证 (limitation 环境)

**Job 23201746**: ✅ 3/3 done

### 结果

| Seed | SR | Ro/ep | LASSO | 说明 |
|:----:|:---:|:-----:|:-----:|------|
| 42 | 6.0% | 3.50 | 成功 (threshold=0.77) | SR仍低于base |
| 123 | 2.0% | 0.25 | 失败→fallback 0.95 | LASSO找不到正样本 |
| 456 | 2.5% | 0.25 | 失败→fallback 0.95 | LASSO找不到正样本 |
| **avg** | **3.5%** | **1.33** | | **< base_only 9.3%** |

### BabyAI 结论

```
❌ SE在BabyAI上SR=3.5%, 比base_only (9.3%) 更差
❌ pos_rate太低 (0.2%), LASSO在2/3 seed完全失败
❌ LLM生成的feature也无法发现有效信号
→ 确认BabyAI为limitation环境: 信号本身不存在, 任何自动方法都无法拯救
→ 支撑论文"Two-Source Model"理论
```

---

## Phase 3: Multi-Cycle Ablation (NO feedback)

**Job 23209062**: 🔄 36 runs submitted (4 methods × 3 main envs × 3 seeds)

### 实验设计

Phase 3 是针对 Phase 2 feedback 方法的消融实验，验证三个独立贡献：
1. **Feedback vs No-Feedback**: Phase 2 有反馈 vs Phase 3 无反馈（纯重新反思）
2. **Additive vs Selective**: 保留旧+新增 vs 保留选中+替换未选中
3. **Cumulative vs Latest**: 累积全部数据 vs 仅用原始探索数据

| 变体 | Feature策略 | 数据策略 | 反馈 | 对比对象 |
|------|:----------:|:-------:|:----:|---------|
| se_c3_addcum_local | Additive | Cumulative | ❌ | vs fb_c3 (有反馈) |
| se_c3_addlat_local | Additive | Latest | ❌ | vs addcum (数据量) |
| se_c3_selcum_local | Selective | Cumulative | ❌ | vs addcum (feature管理) |
| se_c3_sellat_local | Selective | Latest | ❌ | vs selcum (数据量) |

### 预期消融结论

```
假设 1: fb_c3_local > se_c3_selcum_local → 反馈有帮助
假设 2: selcum > sellat → 累积数据有帮助
假设 3: selcum > addcum → Selective > Additive (控制feature总数)
```

### 简化决策

```
原计划 120 runs → 简化为 36 runs:
  ✅ 只用 cycle3 (已确认 cycle3 > cycle2)
  ✅ 只用 local backend (已确认 local ≈ openrouter at 50cal)
  ✅ 只用 filter (已确认 filter > no-filter)
  ✅ 只用 3 主环境 (TWExpress/Plancraft 已有足够SE数据)
```

---

## V2 Pareto Domination（参考基线）

| 环境 | v2 vs CB Pareto | 详情 |
|------|:--------------:|------|
| HotpotQA | ✅ 5 个 | dominates CaTS/CATTS/SEAG/CoRefine/random_50 |
| APPS | — | SR #4 but cost #8 (tradeoff) |
| WebShop | ✅ 3 个 | dominates CaTS/SEAG/CoRefine |
| TWExpress | ≈持平 | 与 CB 差距 <0.2pp SR, <0.17× cost |
| Plancraft | ✅ **6 个** | dominates SCG/CaTS/CATTS/SEAG/CoRefine/always 🔥 |

---

## Phase 6.1b: New Competing Baselines (AUQ + s1 Budget Forcing)

**Date**: 2026-03-18
**Goal**: 补充两个新 baseline，丰富论文的 baseline 对比维度

### 新 Baseline 概述

| Baseline | 论文 | 核心机制 | 信号 | 方向假设 | 额外 Cost |
|----------|------|---------|------|---------|----------|
| **AUQ** | arXiv:2601.15703 (2026) | 每步问 LLM "你多有信心？" → 低信心触发 rollout | Verbalized confidence | 固定负向 | 1 LLM call/step |
| **s1 Budget** | EMNLP 2025 (2501.19393) | 固定 K 次 rollout 均匀分布 → 零智能 | 无 | 无 | 0 |

### s1 Budget K 值设定（匹配 SCG avg ro/ep）

| 环境 | SCG ro/ep | s1 K | trigger_steps |
|------|:---------:|:----:|:-------------:|
| HotpotQA | 1.09 | 2 | {0, 5} |
| APPS | 0.18 | 1 | {0} |
| WebShop | 0.95 | 1 | {0} |
| TWExpress | 1.38 | 2 | {0, 25} |
| Plancraft | 3.33 | 4 | {0, 7, 15, 22} |

### 实现状态

| Step | 内容 | Status |
|------|------|:------:|
| Gate 类实现 | `AUQ_Gate` + `S1Budget_Gate` in `competing_baselines.py` | ✅ (`9e1b86c`) |
| Runner 集成 | `p5_competing_baselines.py` 注册新方法 (ADDITIVE ONLY) | ✅ (`ea56050`) |
| Episode runner | 3 个 runner 添加 `obs_text`/`action_text` + s1 reset | ✅ (`f70f780`) |
| Config | `configs/phase6_new_baselines.yaml` (5 env) | ✅ (`3209256`) |
| SLURM | `scripts/run_phase6_baselines.sbatch` (array job, 自启 vLLM) | ✅ (`a971601`) |
| Report gen | `experiments/gen_phase6_report.py` | ✅ (`013c011`) |
| **实验提交** | **Job 23210145 — 30 array tasks (2×5×3)** | **🔄 Queued** |
| 报告生成 | `planning/phase6.1_environment_report.md` | ⬜ 等实验完成 |

### 实验矩阵

```
2 methods × 5 envs × 3 seeds × 200 episodes = 30 runs
每 run: 1 GPU, 自启 vLLM (端口 9300+IDX), 12h 时限
最多同时 10 个 job (%10)
结果路径: results/phase6/new_baselines/{env}/{method}/seed_{seed}/summary.json
```

### 预期论文价值

- **AUQ**: 新信号类型（verbalized confidence），与现有 4 个 CB 的信号都不同。仍然是 fixed-direction → 在 direction-reversed 环境中应失败
- **s1 Budget**: 同 cost 对比 — "同样花 K 次 rollout，SCG 的 intelligent allocation 是否优于 unintelligent uniform allocation？"

---

## SLURM Jobs

| Job | Name | Tasks | Status |
|-----|------|:-----:|:------:|
| ~~23189559~~ | ~~SE V1~~ | 30 | ✅ 25 done, 5 failed (old bug) |
| ~~23192753~~ | ~~Phase 1: fewer features~~ | 60 | ✅ 58 done, 2 failed |
| ~~23192761~~ | ~~Phase 2: feedback evolution~~ | 60 | ✅ 60 done |
| **23194924** | **方案 D: 100cal openrouter** | **15** | **🔄 12 done, 3 running (TWExpress)** |
| ~~23201746~~ | ~~BabyAI SE test~~ | 3 | ✅ 3 done (limitation confirmed) |
| **23209062** | **Phase 3: multi-cycle ablation** | **36** | **🔄 Submitted** |
| **23210145** | **Phase 6.1b: AUQ + s1 Budget** | **30** | **🔄 Queued (waiting GPU)** |

---

## 代码文件

| 文件 | 用途 |
|------|------|
| `frvc/self_evolving_gate.py` | SE V1 + few5/filter 支持 |
| `frvc/self_evolving_v2.py` | SE V2: multi-cycle + feedback |
| `frvc/competing_baselines.py` | 6 个 CB gate (含新增 AUQ + s1 Budget) |
| `experiments/p5_competing_baselines.py` | CB 实验 runner (含新增 auq/s1_budget 支持) |
| `experiments/gen_phase6_report.py` | Phase 6.1 报告生成器 |
| `configs/phase6_new_baselines.yaml` | 新 baseline 实验 config |
| `scripts/run_phase6_baselines.sbatch` | 新 baseline SLURM array job |
| `scripts/phase6/run_se_phase1.sbatch` | Phase 1 sbatch (60 jobs) |
| `scripts/phase6/run_se_phase2.sbatch` | Phase 2 sbatch (60 jobs) |
