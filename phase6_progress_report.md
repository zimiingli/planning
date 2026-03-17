# Phase 6 Progress Report

**Date**: 2026-03-15 (Day 4)
**Reporting Period**: 2026-03-12 ~ 2026-03-15
**Plan Version**: v3.5

---

## Executive Summary

Phase 6 路径 B 经历了从"突破"到"发现问题"再到"修复重跑"的完整迭代。

**关键时间线**：
1. B1-B3 全部成功（offline AUC 0.88-1.00, 3/3 GO）
2. B4v1 end-to-end 看似成功（APPS +5.7pp），但后来发现**两层 bug**：(a) threshold=0.05 太低 → 100% 触发；(b) hidden_state 从未被传递到 gate → gate 始终 fallback 为 always_trigger
3. B4v2 尝试 4 种在线 threshold 校准，但同样受 bug(b) 影响且在线数据太少
4. B4v3 第一轮同样受 bug(b) 影响
5. 发现并修复 bug(b)：在 episode runner 中新增 `hf_engine` 参数传递 hidden_state
6. **B4v3 第二轮（job 23166910）是第一次 probe 真正参与 gating 决策的实验**，running 中

路径 A/D 全部完成，路径 C 全 NO-GO。

### 当前状态总结

| 路径 | 状态 | 关键结果 |
|------|:----:|---------|
| **A 数据完善** | ✅ 完成 | TWExpress CB 12/12, APPS rerun 9/9, 全部 token cost |
| **B Probe Gate** | 🔄 **迭代中** | B1-B3 ✅, B4v1-v3r1 无效(hidden_state未传递), **B4v3r2 首次真正 probe gating, running** |
| **C 新环境** | ❌ 全 NO-GO | 16 环境测试，仅 5 GO，论文 4 环境锁定 |
| **D Toy Model** | ✅ 完成 | P1/P2/P3 全部 confirmed, Figure 2+7 已生成 |

---

## 1. 路径 A：完善现有环境数据 — ✅ 全部完成

（无变化）

- **A1 TWExpress**: CB 12/12, 对比案例, C_base=524, C_rollout=8,002
- **A2 APPS**: Rerun 9/9, oracle=75.0%, Hidden State Probe 最强动机环境
- **A3 Cost**: 全部 6 环境 token cost 完成

---

## 2. 路径 B：Hidden State Probe — 迭代探索中

### B1. 多层 Hidden State 收集 — ✅ 完成

Job 23151614: HotpotQA (391, 9, 2560), APPS (518, 9, 2560), WebShop (1261, 9, 2560)

### B2. Offline Probe 训练 — ✅ 完成

| Method | HotpotQA AUC | APPS AUC | WebShop AUC |
|--------|:------------:|:--------:|:-----------:|
| P1 Linear Reg | 0.894 | 0.807 | **1.000** |
| P2 PCA(50)+LR | 0.876 | 0.860 | 0.999 |
| P3 MLP Reg | **0.922** | 0.878 | **1.000** |
| P4 MLP Clf | 0.904 | **0.894** | 1.000 |
| Handcrafted LR | **1.000** | **0.981** | 1.000 |

**关键发现**：Probe AUC 高 (0.88-1.00) 但 handcrafted LR 更高 (0.98-1.00)。这预示了后续 end-to-end 的困难。

### B3. GO/NO-GO — ✅ 3/3 GO

所有环境 R² >> 0.10, AUC >> 0.70。

### B4v1. End-to-End（原始版本）— ❌ 结果无效

| 环境 | Probe SR | Probe Ro/ep | SCG SR | SCG Ro/ep | always SR | always Ro/ep |
|------|:--------:|:-----------:|:------:|:---------:|:---------:|:------------:|
| HotpotQA | 97.0% | **1.80** | 96.8% | 1.09 | 97.0% | 1.80 |
| APPS | 64.5% | **2.58** | 58.8% | 0.18 | 64.5% | 2.58 |
| WebShop | 41.8% | **5.61** | 43.7% | 0.95 | 43.0% | 5.63 |

**⚠️ 结果无效 — 发现两层 bug**：

**Bug 1: threshold=0.05 太低**（最初的诊断）
- Probe Ro/ep ≈ always_trigger Ro/ep → Probe 等同于 always_trigger
- SR 提升来自过度触发，不是精准选择

**Bug 2: hidden_state 从未传递（根本原因，后续发现）**
- `run_gated_episode()` 和 `run_gated_episode_p4()` 函数**不接受也不传递 hidden_state 参数**
- Gate 的 `ctx.get("hidden_state")` 始终返回 None
- Gate fallback: `if hidden_state is None: return True` → **100% 触发**
- **APPS "+5.7pp" 完全是 always_trigger 的结果**，probe 从未参与决策
- Phase 5 comparison 的 `hidden_state_mlp` 结果同样无效（同一 bug）

**修复**（已应用到 B4v3 第二轮）：
- `run_gated_episode()` 新增 `hf_engine` 参数
- 在 gate 调用前用 `hf_engine.encode_state(prompt)` 提取 hidden state
- 传入 `ctx["hidden_state"]` 供 gate 使用

**教训**：
- ⚠️ 之前所有声称的 probe end-to-end 结果（B4v1 全部、B4v2 全部、B4v3 第一轮）都是 always_trigger 的假象
- 只有 B4v3 第二轮（job 23166910）才是 probe 真正参与决策的实验

### B4v2. 4 种 Threshold 校准方法 — ⚠️ 在线校准失败

实现了 4 种 threshold 自适应策略 (`frvc/calibrated_probe_gate.py`)：
- **A. Quantile-adaptive**：匹配 positive_rate 的分位数
- **B. F1-optimal**：最大化 F1 score
- **C. Cost-EV**：最大化 E[utility] - λ·trigger_cost
- **D. Online Bayesian**：F1 warm-start + EMA 在线自适应

#### HotpotQA 结果（4/4 完成）

| Method | Mean SR | Ro/ep | Threshold | 评估 |
|--------|:-------:|:-----:|:---------:|------|
| A Quantile | 54.5% | 0.25 | 1.000 | ❌ 阈值过高 → 几乎不触发 |
| B F1 | 95.8% | 1.75 | 0.990 | ⚠️ SR 好但仍接近 always |
| C Cost-EV | 95.7% | 1.73 | 0.990 | ⚠️ 同 B，λ 惩罚不够 |
| D Online | 56.5% | 0.26 | 1.010 | ❌ 同 A，初始阈值太高 |

#### APPS 部分结果

| Method | Seed | SR | Ro/ep | Threshold |
|--------|:----:|:--:|:-----:|:---------:|
| A Quantile | 123 | 59.0% | 0.25 | 1.000 |

**失败根因分析**：

探索期（50 ep）只收集 ~50-100 步数据，导致：
1. **分布偏移**：探索期的 probe 预测分布与 B1 offline 数据不同（新 episode 生成不同 prompt → 不同 hidden state）
2. **样本量不足**：50 个样本估计分位数/F1 不稳定
3. **二值 utility**：HotpotQA utility 是 0/1，分位数恰好卡在 1.0 → 完全不触发

**模拟验证**：用 B1 offline 全量数据（391-1261 步）模拟同样的校准方法，threshold 分布合理（0.15-0.72），证明方法本身没问题，问题在于在线数据不够。

### B4v3. Offline Threshold + Adaptive RL

基于诊断结果，改用两条并行路径 (`frvc/probe_gate_v2.py`)。

**第一轮 Job 23164633**: ❌ 无效（hidden_state 未传递 bug）
**第二轮 Job 23166910**: 修复后首次真正 probe gating

#### 策略 1: Offline Pre-computed Threshold — ❌ 不可行

用 B1 offline 数据预计算 F1-optimal threshold，gate 跳过探索直接 exploitation。

**HotpotQA 结果 (3 seeds)**:

| Seed | SR | Ro/ep | Threshold |
|:----:|:--:|:-----:|:---------:|
| 42 | 51.5% | 0.00 | 0.362 |
| 123 | 47.0% | 0.00 | 0.362 |
| 456 | 46.5% | 0.00 | 0.362 |
| **Mean** | **48.3%** | **0.00** | — |

**结论：❌ 完全不可行。** Ro/ep=0.00 意味着 probe 一次都没触发，SR≈base_only(49%)。

**根因：Offline vs Online 预测分布严重偏移。** B1 offline 数据是用保存的 state_texts 做 forward pass，而 online 实验是用新生成的 prompt。同一个 probe 对不同 prompt 产生完全不同的预测值分布，导致 offline 校准的 threshold 对 online 完全不适用。

**已取消剩余 offline 实验（APPS/WebShop）。**

#### 策略 2: Adaptive RL-like Threshold — ⚠️ 部分有效

Offline threshold 做 warm-start，epsilon-greedy 持续探索 + 梯度更新 threshold。

**HotpotQA 结果 (3 seeds, 修复后)**:

| Seed | SR | Ro/ep | Init Th | Final Th |
|:----:|:--:|:-----:|:-------:|:--------:|
| 42 | 61.0% | 0.38 | 0.362 | 0.897 |
| 123 | 63.0% | 0.40 | 0.362 | 0.721 |
| 456 | 58.0% | 0.37 | 0.362 | 0.865 |
| **Mean** | **60.7%** | **0.38** | — | **0.828** |

**对比**: SCG=96.8%@1.09ro, always=97.0%@1.80ro, base=49.0%

**分析**:
- Probe 确实在做**选择性 gating**（Ro/ep=0.38，远低于 always 1.80）
- SR=60.7% 显著高于 base(49%) → rollout 有效
- 但 SR **远低于 handcrafted SCG (96.8%)** → probe 的选择精度不如 handcrafted
- Threshold 从 0.362 自适应升到 0.828 → probe 发现初始 threshold 太低，逐渐变保守
- **根因**：online hidden state 预测分布偏移 + 有限探索数据导致 threshold 未收敛到最优

**APPS adaptive**: 🔄 Running (job 23166910, tasks 9-11)
**WebShop adaptive**: 🔄 Pending (tasks 15-17)

### B6. 科学分析 — ✅ 完成

（不受 B4 threshold 问题影响，结果仍然有效）

#### B6.1 Layer-wise Probing

- WebShop 所有层 AUC > 0.99（信号在最浅层已编码）
- HotpotQA/APPS 所有层 AUC 0.79-0.85（信号广泛分布）

#### B6.2 Cross-Env Transfer Matrix — 🔥 核心发现

| Train \ Eval | HotpotQA | APPS | WebShop |
|:------------:|:--------:|:----:|:-------:|
| HotpotQA | **1.000** | 0.548 | 0.174 |
| APPS | 0.650 | **1.000** | 0.269 |
| WebShop | 0.470 | 0.330 | **1.000** |

对角线 ≈ 1.0, 非对角线 0.17-0.65 → **直接验证 Two-Source Model**

#### B6.3 Learning Curve

- WebShop: 50 samples → AUC=0.985
- HotpotQA: 60 samples → AUC > 0.84
- 信号学习所需数据量极低

### Figure 6 — ✅ 已生成

`results/phase6/figures/figure6_probe_analysis.pdf` (三面板: layer-wise + transfer heatmap + learning curve)

---

## 3. 路径 C：新环境候选 — ❌ 全部 NO-GO

（无变化）16 环境测试，5 GO + 11 NO-GO。论文 4 环境锁定。

---

## 4. 路径 D：Toy Model Verification — ✅ 全部完成

（无变化）P1/P2/P3 confirmed, Figure 2+7 已生成。

---

## 5. SLURM Job 汇总

### Day 2 (2026-03-13)

| JobID | Name | Duration | State | Result |
|-------|------|:--------:|:-----:|--------|
| 23145097 | token_cost_twe | 29m | ✅ | C_base=524, C_rollout=8002 |
| 23145100 | token_cost_bai | 37m | ✅ | C_base=336, C_rollout=2173 |
| 23145101 | token_cost_pc | 14m | ✅ | C_base=1120, C_rollout=10651 |
| 23148694 | s0_tb_mir | 11m | ✅ | base=98%, Δ=0% → NO-GO |

### Day 3 (2026-03-14)

| JobID | Name | Duration | State | Result |
|-------|------|:--------:|:-----:|--------|
| 23151614 | B1 multi-layer (×3) | 11s-2m | ✅ | 3 env hidden states |
| — | B2 probe training (CPU) | 75m | ✅ | 4 probes × 3 envs |
| 23166910 | B4v3r2 修复后 (×18) | — | ✅ | HotpotQA 60.7%, APPS 63.7%, WebShop 30.3% |
| 23167005 | Path E 主实验 (×45) | — | ✅ | E3:principled 最佳 |
| 23175320 | Online Ablation (×30) | — | 🔄 | HotpotQA/APPS/WebShop ✅, BabyAI 🔄 |
| 23176360 | TWExpress online/nopca (×6) | — | ⬜ | pending |
| **23176425** | **principled_auto (×18)** | — | **⬜** | **6 envs × 3 seeds, auto threshold** |

---

## 6. 路径 E：Method Upgrade — ✅ 45/45 完成

### E1-E3 方法概述

| 方法 | 核心思路 | 需要 hidden state? |
|------|---------|:------------------:|
| **E1:cacb_A/B/C** | Thompson Sampling + Bayesian LR，自动 explore/exploit | A:否, B/C:是 |
| **E2:proto** | Prototypical Networks，天然 threshold=0 | 是 |
| **E3:principled** | Auto feature pool + LASSO 选特征 + CMDP threshold | 是 |

### Path E 完整结果（Exploitation-Only 公平对比†）

**HotpotQA** (base=49.0%, oracle=97.0%@3.70×)

| Method | SR | Ro/ep | Cost(×base) |
|--------|:--:|:-----:|:-----------:|
| scg_finetune_lr ★ | 96.8% | 1.09 | 6.59× |
| **E3:principled†** | **96.7%** | 1.34 | 8.05× |
| E2:proto† | 94.4% | 1.12 | 6.80× |
| CaTS | 93.2% | 1.77 | 10.60× |
| E1:cacb_A | 74.7% | 0.56 | 3.80× |
| always_trigger | 97.0% | 1.80 | 10.70× |

**APPS** (base=58.5%, oracle=75.0%@1.14×)

| Method | SR | Ro/ep | Cost(×base) |
|--------|:--:|:-----:|:-----------:|
| **E3:principled†** | **66.2%** | 2.09 | 3.58× |
| **E2:proto†** | **65.6%** | 1.93 | 3.37× |
| random_50 | 66.8% | 1.33 | 2.61× |
| always_trigger | 64.5% | 2.58 | 4.25× |
| E1:cacb_C | 60.3% | 0.44 | 1.51× |
| CaTS | 59.0% | 0.04 | 1.02× |
| scg_finetune_lr ★ | 58.8% | 0.18 | 1.20× |

**WebShop** (base=7.2%, oracle=43.3%@1.06×)

| Method | SR | Ro/ep | Cost(×base) |
|--------|:--:|:-----:|:-----------:|
| scg_finetune_lr ★ | 43.7% | 0.95 | 1.27× |
| **E3:principled†** | **42.7%** | 2.26 | 2.46× |
| E2:proto† | 39.8% | 3.54 | 3.69× |
| CaTS | 30.5% | 3.04 | 3.43× |
| E1:cacb_A | 26.7% | 0.98 | 1.57× |
| always_trigger | 43.0% | 5.63 | 5.54× |

† = exploitation-only（去掉 50ep 探索期，与 SCG 预加载 Phase 1 数据对等）

### Pareto Domination 分析

```
E3:principled† vs SCG:
  HotpotQA: SR -0.1pp, Cost +1.46×  → SCG 略优
  APPS:     SR +7.4pp, Cost +2.38×  → Tradeoff (principled SR 更高, SCG cost 更低)
  WebShop:  SR -1.0pp, Cost +1.20×  → SCG 略优

E3:principled† vs CaTS:
  HotpotQA: SR +3.5pp, Cost -2.55×  → ✅ Pareto-dominates
  WebShop:  SR +12.2pp, Cost -0.97× → ✅ Pareto-dominates
  APPS:     SR +7.2pp, Cost +2.56×  → Tradeoff

E3:principled† vs always_trigger:
  APPS:     SR +1.7pp, Cost -0.67×  → ✅ Pareto-dominates
```

### 关键结论

1. **E3:principled† 在 HotpotQA 上 96.7% ≈ SCG 96.8%** — 完全自动化达到手工水平
2. **E3:principled† 在 APPS 上 66.2% >> SCG 58.8% (+7.4pp)** — 弱信号环境大幅超越
3. **E3:principled† 在 WebShop 上 42.7% ≈ SCG 43.7%** — 接近手工水平
4. **Cost 一致偏高** — principled 的 Ro/ep 高于 SCG（LASSO 学到的策略更激进）
5. **E3:principled Pareto-dominates CaTS** on HotpotQA + WebShop
6. **论文叙事**：SCG 和 Principled 互补 — SCG 适合 cost-sensitive，Principled 适合 SR-first + 无领域知识

### LASSO 特征选择分析

| 环境 | Seed | 非PCA特征 | PCA特征 | PCA占比 |
|------|:----:|:---------:|:-------:|:-------:|
| HotpotQA | 42 | 1 | 9 | **90%** |
| HotpotQA | 123 | 3 | 7 | **70%** |
| HotpotQA | 456 | 2 | 4 | **67%** |
| APPS | 42 | 6 | 4 | 40% |
| APPS | 123 | 4 | **0** | **0%** |
| APPS | 456 | 2 | **0** | **0%** |
| WebShop | 42 | 2 | 6 | **75%** |
| WebShop | 123 | 5 | 5 | 50% |
| WebShop | 456 | 2 | 3 | 60% |

**关键发现**：
- HotpotQA 严重依赖 PCA (67-90%)
- APPS 2/3 seeds 完全不用 PCA (0%)! → APPS 好结果不依赖离线数据
- WebShop 中度依赖 PCA (50-75%)
- **公平性问题**：PCA 是从 B1 offline 数据预拟合的，属于隐含的 offline 成本

### Cost 偏高的根因分析

```
Cost = 探索期成本（可优化） + exploitation 触发率（方法本质）

Exploitation 触发率偏高（主要因素）:
  - APPS: principled 2.09 ro/ep vs SCG 0.18 → 接近 always_trigger
  - 根因: CMDP threshold 用启发式公式设定，过于激进
  - AdjSR(λ=0.05) 在 APPS 上 principled(0.522) < base_only(0.585)
  → threshold 自动调优是关键改进方向
```

### Online Ablation 结果（principled_nopca vs principled_online）

完全 online 方案 vs offline PCA 方案对比（exploitation-only†）：

| 环境 | Offline PCA† | Online PCA† | **No PCA†** | SCG |
|------|:----------:|:----------:|:----------:|:---:|
| HotpotQA | 96.7% | 92.2% | **95.8%** | 96.8% |
| APPS | 66.2% | 65.8% | **65.7%** | 58.8% |
| WebShop | 42.7% | 43.2% | **43.7%** | 43.7% |

**关键发现**：
- **No PCA ≈ Offline PCA** — PCA 贡献极小（APPS/WebShop 几乎无差距）
- **Online PCA 反而更差**（HotpotQA 92.2%）— 探索期数据少导致 PCA 不稳定
- **No PCA 是最佳纯 online 方案** — 不需要 HF engine/offline 数据/领域知识
- **WebShop No PCA 43.7% = SCG 43.7%** — 完全匹配手工方法

### Cost-Adjusted SR (AdjSR = SR - 0.05 × (Cost-1))

| 环境 | oracle | SCG | nopca† | CaTS | always | base |
|------|:------:|:---:|:------:|:----:|:------:|:----:|
| HotpotQA | **0.835** | **0.688** | 0.594 | 0.452 | 0.485 | 0.490 |
| APPS | **0.743** | 0.578 | 0.522 | **0.589** | 0.482 | 0.585 |
| WebShop | **0.430** | **0.424** | 0.308 | 0.183 | 0.203 | 0.072 |

**问题**：nopca AdjSR 在 APPS 上 (0.522) < base_only (0.585) — cost 太高抵消了 SR 增益。
**根因**：CMDP threshold 用启发式公式，过于激进 → 触发率接近 always_trigger。

**修复迭代**：
1. **principled_auto** (job 23176425): 固定 λ=0.05 扫描 → HotpotQA SR 暴跌 68.2%（过度惩罚）
2. **principled_adaptive** (job 23179282): 自适应 λ → HotpotQA 恢复 95.7%, TWExpress 99.2% 🔥
   - 但 Plancraft LASSO 2/3 seeds 失败 → 仍过度触发
3. **principled_fbeta** (job 23185268): F-beta threshold, β=sqrt(pos_rate/(1-pos_rate))
   - HotpotQA 91.8% → 比 adaptive 低 4pp（β=0.70 过于保守，不考虑 rollout value）
   - WebShop 39.8% (2/3 seeds) → 也比 adaptive 低
   - 结论：fbeta 在主环境上不如 adaptive，仅保留 TWExpress/Plancraft 实验
   - BabyAI fbeta: 4.0%@1.51ro → 几乎不触发但 SR 也极低（signal 不可预测）
   - **BabyAI 已确认为 limitation 环境**：rollout 有用但不可预测，选择性 gating 不适用
4. **principled_v2** (job 23185483 + 23189295):
   - = adaptive + 当 LASSO 失败且 pos_rate<2% 时 threshold=0.95
   - 发现并修复 bug: LASSO 失败时 `_model=None` → `should_rollout` 直接 return True → 无视 threshold
   - 修复后: `_model=None` + threshold>=0.9 → return False
   - **Plancraft v2 结果: SR=26.2%@0.25ro ✅** — 接近 base_only(29.8%), cost=1.07×
   - 主环境与 adaptive 相同（LASSO 不会失败）
   - BabyAI 已取消（limitation 环境）

---

## 7. 论文环境集与方法定位

### 最终环境矩阵

| 环境 | 论文角色 | SCG SR / Cost | **V2 SR / Cost** | 最佳 CB | V2 Pareto CB |
|------|---------|:-------------:|:----------------:|:-------:|:------------:|
| HotpotQA | ✅ Pareto-dominate | 96.8% / 6.59× | 94.8% / 6.61× | CaTS 93.2% / 10.60× | ✅ 5个 |
| APPS | ⚠️ 弱信号 | 58.8% / 1.20× | **64.2%** / 2.45× | CaTS 59.0% / 1.02× | — |
| WebShop | ✅ Pareto-dominate | 43.7% / 1.27× | 42.7% / 1.93× | CaTS 30.5% / 3.43× | ✅ 3个 |
| TWExpress | ⚠️ Rollout-safe | 97.0% / 1.00× | 97.3% / 1.74× | CATTS 97.5% / 1.57× | ≈持平 |
| BabyAI | ❌ **Limitation** | 8.8% / 1.46× | — (已取消) | signal 不可预测 | — |
| Plancraft | ⚠️ rollout 有害 | 21.5% / 3.31× | **27.2% / 1.49×** 🔥 | base 29.8% | ✅ **6个** |

### 方法定位 — 双方法互补 + 自动 threshold 优化中

```
SCG (handcrafted, 主方法):
  ✅ Cost-efficient: 精准选择性触发，cost 最低
  ✅ Pareto-dominates 所有 CB on HotpotQA + WebShop
  ❌ 弱信号环境 (APPS) 几乎无效 (SR ≈ base_only)
  ❌ 需要领域知识手工设计 feature

principled_v2 (自动化, 补充方法, 当前最佳版本):
  ✅ 完全 online: 无需 offline 数据 / HF engine / 领域知识
  ✅ 弱信号环境 APPS +5.4pp 超越 SCG
  ✅ 强信号环境 HotpotQA (-2.0pp) / WebShop (-1.0pp) 接近 SCG
  ✅ 有害环境 Plancraft: 27.2%@1.49× → 自动学会不触发, Pareto-dominates SCG + 5个 CB
  ✅ Rollout-safe TWExpress: 97.3% ≈ 所有 CB (差距 <0.2pp)
  ✅ 自适应 λ + fallback: 每环境自动不同的 threshold
  ✅ Pareto-dominates 大部分 CB: HotpotQA 5个, WebShop 3个, Plancraft 6个

Self-Evolving (路径 F, 🔄 running):
  → Agent 反思自己的探索经验 → LLM 生成 feature extractor → LASSO 选择
  → 预期发现环境特异 feature (如 TWExpress num_admissible_commands)
  → 两个 backend: local (Qwen3-4B) + openrouter (Claude-opus-4.6)

论文叙事:
  → SCG + v2 互补: cost-sensitive vs SR-first
  → Self-Evolving: agent learns what to look for (meta-reasoning)
  → Method novelty ⭐⭐⭐-⭐⭐⭐⭐ (取决于 self-evolving 效果)
  → NeurIPS 估计: 60-80%
```

---

## 8. 下一步行动计划

### 已完成

| 任务 | Job | 状态 |
|------|:---:|:----:|
| Path E 主实验 (45 jobs) | 23167005 | ✅ 45/45 完成 |
| B4v3r2 adaptive (18 jobs) | 23166910 | ✅ 完成 |
| Path E Online Ablation 主环境 (18/30) | 23175320 | ✅ HotpotQA/APPS/WebShop 完成 |

### Running

| 任务 | Job | 状态 |
|------|:---:|:----:|
| ~~Path E Online Ablation~~ | ~~23175320~~ | ✅ 30/30 完成 |
| ~~TWExpress online/nopca~~ | ~~23176360~~ | ✅ 完成 |
| ~~principled_auto~~ | ~~23176425~~ | ✅ 18/18 完成 (HotpotQA SR 暴跌问题) |
| ~~principled_adaptive~~ | ~~23179282~~ | ✅ 18/18 完成 (最佳版本, CAGC #2) |
| ~~principled_fbeta~~ | ~~23185268~~ | ✅ 完成 (主环境不如 adaptive, BabyAI confirmed limitation) |
| ~~principled_v2~~ | ~~23185483 + 23189295~~ | ✅ **5/5 环境全部完成** |
| ~~Self-Evolving (job 23189478)~~ | ~~23189478~~ | ❌ f-string bug, 已取消 |
| **Self-Evolving (修复后)** | **23189559** | **🔄 Running (2 backends × 5 envs × 3 seeds)** |

### Threshold 优化迭代

| 版本 | Threshold 方法 | 结果 |
|------|---------------|------|
| nopca | 启发式 `λ×0.001/pos_rate` | APPS 触发率过高 (2.19 ro/ep) |
| auto | 固定 λ=0.05 扫描 AdjSR | HotpotQA SR 暴跌 68.2% |
| adaptive | 自适应 λ from data | ✅ HotpotQA 恢复 95.7%, TWExpress 99.2%, 但 Plancraft LASSO 失败 |
| fbeta | F-beta, β=sqrt(pos_rate/(1-pos_rate)) | ⚠️ HotpotQA 91.8% (太保守), 主环境已取消 |
| **v2** 🆕 | adaptive λ + pos_rate<2% fallback | ✅ **Plancraft 26.2%@1.07× (Pareto-dominates 所有 gating)** |

### principled_adaptive 完整结果（6 环境）

| 环境 | adaptive† SR | Ro/ep | Cost† | SCG SR | SCG Cost | vs SCG SR |
|------|:----------:|:-----:|:-----:|:------:|:--------:|:---------:|
| **HotpotQA** | **96.9%** | 1.07 | **6.49×** | 96.8% | 6.59× | **+0.1pp** |
| **APPS** | **65.6%** | 1.04 | 2.33× | 58.8% | 1.20× | **+6.8pp** |
| WebShop | 43.3% | 1.46 | 1.90× | 43.7% | 1.27× | -0.4pp |
| **TWExpress** | **99.1%** | 3.25 | 2.10× | 97.0% | 1.00× | **+2.1pp** |
| BabyAI | 8.4% | 40.26 | 5.08× | 8.8% | 1.46× | -0.4pp |
| Plancraft (adaptive) | 21.8% | 5.41 | 5.08× | 21.5% | 3.31× | +0.3pp |
| **Plancraft (v2)** | **26.2%** | **0.25** | **1.07×** | 21.5% | 3.31× | **+4.8pp** 🔥 |

† = exploitation-only

**v2 Plancraft 是最大改进**: LASSO 失败 → fallback threshold=0.95 → 几乎不触发 (0.25 ro/ep)
→ SR 26.2% 接近 base_only (29.8%), cost=1.07× ≈ base。
Pareto-dominates 所有 gating 方法（SCG 21.5%@3.31×, CATTS 25.0%@2.50×）。

### principled_v2 完整结果（5 环境 SR + Cost + Pareto）

| 环境 | v2 SR | v2 Ro/ep | v2 Cost | SCG SR | SCG Cost | vs SCG SR | Pareto vs CB |
|------|:-----:|:--------:|:-------:|:------:|:--------:|:---------:|:------------:|
| HotpotQA | 94.8% | 1.09 | 6.61× | 96.8% | 6.59× | -2.0pp | ✅ dominates CaTS/CATTS/SEAG/CoRefine/r50 (5) |
| APPS | 64.2% | 1.18 | 2.45× | 58.8% | 1.20× | **+5.4pp** | — (cost 偏高) |
| WebShop | 42.7% | 1.65 | 1.93× | 43.7% | 1.27× | -1.0pp | ✅ dominates CaTS/SEAG/CoRefine (3) |
| TWExpress | 97.3% | 2.71 | 1.74× | 97.0% | 1.00× | +0.3pp | ≈持平 CB (差距 <0.2pp SR, <0.17× cost) |
| **Plancraft** | **27.2%** | **0.77** | **1.49×** | 21.5% | 3.31× | **+5.7pp** | ✅ **dominates SCG/CaTS/CATTS/SEAG/CoRefine/always (6!)** |

**v2 Pareto domination 汇总**:
- HotpotQA: Pareto-dominates **5** 个方法（所有 CB + random_50）
- WebShop: Pareto-dominates **3** 个方法（CaTS/SEAG/CoRefine）
- Plancraft: Pareto-dominates **6** 个方法（包括 SCG！）
- APPS: SR #4 但 cost #8 → tradeoff
- TWExpress: 与 CB 差距极小（SR -0.2pp, cost +0.13-0.17×），实质持平

**TWExpress 详细分析**: 所有方法 SR 在 96.7-97.8% 内，差异不显著。v2 (97.3%@1.74×) vs CATTS (97.5%@1.57×) 仅差 0.2pp SR + 0.17× cost。本环境 rollout 永远无害，所有选择性 gating 方法表现趋同。

### CAGC 排名（GapClosed% / Cost，综合 SR+Cost）

| 排名 | Method | Avg CAGC | 类型 |
|:----:|--------|:--------:|:----:|
| 1 | **SCG** | **44.8%** | **Ours** |
| 2 | **adaptive†/v2** | **~28%** | **Ours** |
| 3 | CoRefine | 25.6% | CB |
| 4 | CaTS | 25.0% | CB |
| 5 | CATTS | 24.2% | CB |
| 6 | SEAG | 23.5% | CB |

**我们的两个方法包揽 CAGC 前两名，超过所有 competing baselines。**

### 剩余问题

### 已解决的问题

- ✅ **Plancraft v2 修复**: 26.2%@1.07× → 接近 base_only, Pareto-dominates 所有 gating
- ✅ **BabyAI 定性为 limitation**: signal 不可预测, 不再优化

### 剩余问题

- **TWExpress**: adaptive 99.2%@2.10× → SR 好但 cost 偏高 (SCG 1.00×)
  - Self-Evolving 可能通过发现 `num_admissible_commands` 等 feature 降低 cost
- **主环境 cost**: adaptive APPS 2.33×, WebShop 1.90× vs SCG 1.20×/1.27×
  - Self-Evolving 可能通过更好的 feature 提高精准度从而降低触发率

### 🆕 Self-Evolving Adaptive Gating (路径 F)

**核心思想**：Agent 反思自己的探索经验，用 LLM 自动发现环境特异的 feature，然后 LASSO 从中选择。

**流程**：
```
Explore (50ep) → LLM Self-Reflect → Generate Feature Extractor Code
  → LASSO(universal + LLM features) → Adaptive λ → Exploit
```

**两个 LLM backend 对比**：
- `self_evolving_local`: Qwen3-4B（同一个模型，truly self-contained）
- `self_evolving_openrouter`: Claude-opus-4.6（更强 reflection，via OpenRouter API）

**Job 23189559** (修复 f-string bug 后重提交): 30 runs = 2 backends × 5 envs × 3 seeds

**论文叙事**：
> "The agent not only learns the task, but reflects on its own experience
>  to discover what signals predict its need for additional computation,
>  then evolves its gating strategy accordingly."

### 待完成

| 任务 | 优先级 |
|------|:------:|
| Self-Evolving 结果分析 (local vs openrouter × 5 envs) | 🔴 |
| principled_v2 Plancraft 修复结果 | 🔴 |
| adaptive vs v2 vs self-evolving 最终对比 | 🔴 |
| 确定最终方法定位 | 🔴 |
| Unified Pareto Figure | 🟠 |
| phase6_final_report.md | 🟠 |
| 开始 LaTeX | 🟡 |

---

## 9. 产出物清单

### 已生成

| 文件 | 路径 |
|------|------|
| B1 Hidden States (3 envs) | `results/phase6/hidden_states_multi/{env}/seed_42/multi_layer_data.npz` |
| B2/B3/B6 Probe Results | `results/phase6/probe_training/b2_probe_results.json` |
| B4v1 Cost Analysis | `results/phase6/cost_analysis/b4_probe_gate_costs.json` |
| **Path E Results (45 runs)** | `results/phase6/path_e/{env}/{method}/seed_*/summary.json` |
| Figure 6 (Probe Analysis) | `results/phase6/figures/figure6_probe_analysis.pdf` |
| D1-D4 Toy Model | `results/phase6/toy_model/*.json` |
| Figure 2 + Figure 7 | `results/phase6/toy_model/*.pdf` |
| Token Costs (6 envs) | `results/phase5/token_costs/{env}_token_costs.json` |

### Running

| 文件 | Job | 备注 |
|------|:---:|------|
| principled_v2 | 23185483 + 23189295 | TWExpress + Plancraft fix running |
| **Self-Evolving** | **23189478** | **local + openrouter × 5 envs × 3 seeds = 30 runs** |

### 新增代码

| 文件 | 用途 |
|------|------|
| `frvc/cacb_gate.py` | E1: Cost-Aware Contextual Bandit Gate |
| `frvc/contrastive_gate.py` | E2: Prototypical Networks Gate |
| `frvc/principled_scg.py` | E3: Principled SCG (auto feature + CMDP) |
| `frvc/calibrated_probe_gate.py` | B4v2: 4 种 threshold 校准策略 |
| `frvc/probe_gate_v2.py` | B4v3: Offline + Adaptive RL gate |
| `experiments/p6_e_method_upgrade.py` | Path E 统一实验 runner |
| `experiments/p6_b1_data_collection.py` | B1 新环境数据收集 |
| `experiments/p6_b2_probe_training.py` | B2 probe 训练 + B6 分析 |
| `experiments/p6_figure6_probe_analysis.py` | Figure 6 绘图 |
| `scripts/phase6/run_path_e.sbatch` | Path E sbatch (45 jobs) |
| `scripts/phase6/run_path_e_online.sbatch` | Path E Online Ablation sbatch (30 jobs) |
| `scripts/phase6/run_path_e_twexpress.sbatch` | TWExpress online/nopca sbatch (6 jobs) |
| `scripts/phase6/run_path_e_auto.sbatch` | principled_auto sbatch (18 jobs) |
| `scripts/phase6/run_path_e_adaptive.sbatch` | principled_adaptive sbatch (18 jobs) |
| `scripts/phase6/run_path_e_fbeta.sbatch` | principled_fbeta sbatch (18 jobs) |
| `frvc/self_evolving_gate.py` | Self-Evolving Gate (LLM reflect + LASSO) |
| `scripts/phase6/run_self_evolving.sbatch` | Self-Evolving sbatch (30 jobs) |
| `scripts/phase6/run_path_e_failed_envs.sbatch` | 失败环境验证 sbatch |
| `scripts/phase6/run_b1_new_envs.sbatch` | B1 新环境数据收集 sbatch |
