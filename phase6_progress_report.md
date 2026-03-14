# Phase 6 Progress Report

**Date**: 2026-03-14 (Day 3, v3)
**Reporting Period**: 2026-03-12 ~ 2026-03-14
**Plan Version**: v3.4

---

## Executive Summary

Phase 6 路径 B 经历了从"突破"到"发现问题"再到"修复重跑"的完整迭代。

**关键时间线**：
1. B1-B3 全部成功（offline AUC 0.88-1.00, 3/3 GO）
2. B4v1 end-to-end 看似成功（APPS +5.7pp），但发现 probe 实际上等同于 always_trigger（threshold=0.05 太低 → 100% 触发率 → cost 极高）
3. B4v2 尝试 4 种在线 threshold 校准方法（A/B/C/D），但因探索期数据太少+分布偏移导致 threshold 估计不准
4. B4v3 改用 offline 预计算 threshold + adaptive RL 两条路并行重跑中

路径 A/D 全部完成，路径 C 全 NO-GO。

### 当前状态总结

| 路径 | 状态 | 关键结果 |
|------|:----:|---------|
| **A 数据完善** | ✅ 完成 | TWExpress CB 12/12, APPS rerun 9/9, 全部 token cost |
| **B Probe Gate** | 🔄 **迭代中** | B1-B3 ✅, B4v1 发现 cost 问题, B4v2 threshold 不准, B4v3 running |
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

### B4v1. End-to-End（原始版本）— ⚠️ 发现严重 cost 问题

| 环境 | Probe SR | Probe Ro/ep | SCG SR | SCG Ro/ep | always Ro/ep |
|------|:--------:|:-----------:|:------:|:---------:|:------------:|
| HotpotQA | 97.0% | **1.80** | 96.8% | 1.09 | 1.80 |
| APPS | 64.5% | **2.58** | 58.8% | 0.18 | 2.58 |
| WebShop | 41.8% | **5.61** | 43.7% | 0.95 | 5.63 |

**问题诊断**：
- Probe Ro/ep ≈ always_trigger Ro/ep → **Probe 等同于 always_trigger**
- SR 提升（特别是 APPS +5.7pp）来自过度触发，不是精准选择
- Cost 极高：HotpotQA 10.87×, APPS 4.29×, WebShop 13.89×
- **根因**：`utility_threshold=0.05` 太低，几乎所有 state 的 predicted utility > 0.05

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

### B4v3. Offline Threshold + Adaptive RL — 🔄 Running

基于诊断结果，改用两条并行路径 (`frvc/probe_gate_v2.py`)：

**策略 1: Offline Pre-computed Threshold**
- 用 B1 全量 offline 数据预计算 F1-optimal threshold
- Gate 直接进入 exploitation（跳过 50 ep 探索）
- 零额外 cost，最大化 probe 的 ranking 能力

**策略 2: Adaptive RL-like Threshold**
- Offline threshold 做 warm-start
- Epsilon-greedy 持续探索（15% → 衰减到 2%）
- 每次 rollout 后梯度更新 threshold：有用 → 降；无用 → 升
- Cost-aware 正则化：threshold 有轻微上升趋势

**Offline 预计算的 threshold（F1-optimal on B1 data）**：

| 环境 | Threshold | Trigger Rate | Precision |
|------|:---------:|:------------:|:---------:|
| HotpotQA | **0.362** | 41.7% | 73.0% |
| APPS | **0.298** | 11.6% | 80.0% |
| WebShop | **0.315** | 10.2% | 97.7% |

**SLURM Job 23164633**: 18 runs (2 strategies × 3 envs × 3 seeds), 9 并发

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
| 23161692 | B4v1 WebShop (×3) | ~2h each | ✅ | SR=47.0/42.0/36.5% |
| 23164048 | B4v2 calibrated (×36) | — | ❌ FAILED→部分 | 代码 bug 修复后部分完成 |
| 23164139 | B4v2 resubmit (×36) | — | ⚠️ 部分 | HotpotQA 4/4 done, APPS 进行中 |
| **23164633** | **B4v3 offline+adaptive (×18)** | — | **🔄 Running** | **2 strategies × 3 envs × 3 seeds** |

---

## 6. 路径 B 迭代总结与教训

### 迭代路径

```
B4v1: 直接用 probe (threshold=0.05)
  → 发现: probe = always_trigger, cost 极高
  → 教训: 固定低 threshold 在 sparse utility 分布上不可用

B4v2: 4 种在线 threshold 校准 (A/B/C/D)
  → 发现: 在线数据太少 + 分布偏移 → threshold 估计不准
  → 教训: 探索期 50-100 步不够稳定估计，需要 offline 数据

B4v3: Offline threshold + Adaptive RL (当前)
  → 预期: offline threshold 合理 (0.30-0.36)，precision 73-98%
  → 等待结果中...
```

### 核心洞察

1. **Probe 的 ranking 能力很强**（offline AUC 0.88-1.00），但 threshold 校准是成败关键
2. **在线校准不可靠**：探索期数据太少 + 新 episode 产生分布偏移
3. **Offline 预计算 threshold 最稳定**：用 B1 全量数据（391-1261 步）确保估计准确
4. **Handcrafted features 的 AUC 更高**（0.98-1.00 vs probe 0.88-1.00），说明手工特征在分类任务上仍有优势
5. **Probe 的真正价值可能在科学分析**（B6）而非方法提升：cross-env transfer 失败是验证 Two-Source Model 的最强证据

---

## 7. 论文环境集与方法定位

### 最终环境矩阵

| 环境 | 论文角色 | Handcrafted SCG | 最佳 CB | 状态 |
|------|---------|:---------------:|:-------:|:----:|
| HotpotQA | ✅ Pareto-dominate | 96.8% @ 6.55× | CaTS 93.2% @ 10.55× | ✅ |
| WebShop | ✅ Pareto-dominate | 43.7% @ 1.27× | CaTS 30.5% @ 3.44× | ✅ |
| APPS | ⚠️ 弱信号 diagnostic | 58.8% @ 1.23× | CaTS 59.0% @ 1.04× | ✅ |
| TWExpress | ⚠️ Rollout-safe 对比 | 97.0% | CATTS 97.5% | ✅ |

### 方法定位（取决于 B4v3 结果）

```
场景 1: B4v3 probe gate SR ≈ SCG 且 cost < SCG
  → Probe 作为方法升级（自动化 feature 发现）
  → Method novelty ⭐⭐⭐⭐

场景 2: B4v3 probe gate SR ≈ SCG 但 cost ≈ SCG
  → Probe 作为可选方法（自动化但无 cost 优势）
  → Method novelty ⭐⭐⭐

场景 3: B4v3 probe gate SR < SCG 或 cost >> SCG
  → Probe 降为科学分析工具（B6 cross-env transfer 仍是核心发现）
  → Handcrafted SCG 保持主方法
  → Method novelty ⭐⭐, 但 theory novelty ⭐⭐⭐⭐（Two-Source Model 验证）
```

---

## 8. 下一步行动计划

### 立即

| 任务 | 状态 |
|------|:----:|
| B4v3 offline + adaptive (18 jobs) | 🔄 Running (job 23164633) |
| B4v2 剩余 APPS/WebShop 结果 | 🔄 部分 running |

### B4v3 完成后

| 任务 | 优先级 |
|------|:------:|
| B4v3 结果分析（SR, Ro/ep, cost 对比） | 🔴 |
| 确定方法定位（场景 1/2/3） | 🔴 |
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
| B4v1 Results (3 envs × 3 seeds) | `results/phase5/comparison/{env}/hidden_state_mlp/seed_*/summary.json` |
| B4v1 Cost Analysis | `results/phase6/cost_analysis/b4_probe_gate_costs.json` |
| B4v2 Results (partial) | `results/phase6/b4v2/{env}/probe_cal_{A,B,C,D}/seed_*/summary.json` |
| Figure 6 (Probe Analysis) | `results/phase6/figures/figure6_probe_analysis.pdf` |
| D1-D4 Toy Model | `results/phase6/toy_model/*.json` |
| Figure 2 + Figure 7 | `results/phase6/toy_model/*.pdf` |
| Token Costs (6 envs) | `results/phase5/token_costs/{env}_token_costs.json` |

### Running

| 文件 | Job |
|------|:---:|
| B4v3 Results (2 strategies × 3 envs × 3 seeds) | 23164633 |

### 新增代码

| 文件 | 用途 |
|------|------|
| `frvc/calibrated_probe_gate.py` | B4v2: 4 种 threshold 校准策略 |
| `frvc/probe_gate_v2.py` | B4v3: Offline + Adaptive RL gate |
| `experiments/p6_b4v2_calibrated.py` | B4v2 实验 runner |
| `experiments/p6_b4v3_probe_gate.py` | B4v3 实验 runner |
| `experiments/p6_figure6_probe_analysis.py` | Figure 6 绘图 |
| `scripts/phase6/run_b4v2_calibrated.sbatch` | B4v2 sbatch (36 jobs) |
| `scripts/phase6/run_b4v3_probe_gate.sbatch` | B4v3 sbatch (18 jobs) |
