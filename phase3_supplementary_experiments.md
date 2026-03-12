# Phase 3 补充实验完整清单

> **日期**: 2026-02-26
> **背景**: Phase 3 核心 66 runs 已完成，但存在关键数据缺失和战略性缺陷
> **目标**: 补全 Phase 3 缺失指标 + 解决 "仅 1 个有效环境" 的致命弱点

---

## 问题总览

| # | 问题 | 严重性 | 对应补充实验 |
|---|------|--------|-------------|
| 1 | TES/CS 未计算，Phase 3 判断标准无法评估 | 🔴 阻塞 | S0 |
| 2 | 6 项统计检验未执行 | 🔴 阻塞 | S0 |
| 3 | Phase 2 vs Phase 3 seed=42 数据不一致 (SR 0.953 vs 0.960) | 🟠 需确认 | S0 |
| 4 | Avg Steps 暗示 CS≈0%，与 Phase 2 的 CS=49.5% 矛盾 | 🔴 可能阻塞 | S1 |
| 5 | MBPP/HumanEval 均 ceiling effect，仅 HotpotQA 1 个有效环境 | 🔴 阻塞投稿 | S2 |
| 6 | Phase 3.5 CMDP 实验待执行 | 🟠 P1 | S3 |

---

## S0：分析补全（无需新实验，纯计算）

**预计耗时**: 2-3 小时
**前置条件**: 无
**阻塞性**: 🔴 是——不完成 S0 无法判断 Phase 3 是 GO 还是 CONCERN

### S0-1：计算全部方法的 Cost 指标

**做什么**: 从已有 Phase 3 结果数据中提取每步 rollout 触发记录，计算 RR 和 CS。

**怎么做**:

```python
# 对每个 (method, env, seed) 组合:
# 从 results/phase3/{env}/{method}/seed_{seed}/ 中加载 episode 数据

# 1. Rollout Rate (RR) — 每步触发概率
RR = total_rollout_calls / total_steps_across_all_episodes

# 2. Cost Saving (CS) — 相对 always_trigger 的节省
CS = 1.0 - (RR_method / RR_always_trigger)
# 等价于:
CS = (rollouts_always - rollouts_method) / rollouts_always

# 3. 每 episode 平均 rollout 次数
avg_rollouts_per_episode = total_rollout_calls / num_episodes
```

**需要输出的指标**:

| 指标 | 公式 | 含义 |
|------|------|------|
| **RR** (Rollout Rate) | `Σ rollout_calls / Σ total_steps` | 每步触发概率 |
| **CS** (Cost Saving) | `1 - RR_method / RR_always` | 相对 always-trigger 的成本节省 |
| **Avg Rollouts/ep** | `Σ rollout_calls / N_episodes` | 每 episode 平均 rollout 次数 |

**输出格式**（每个环境一张表）:

```
HotpotQA:
Method              | SR (mean±std) | RR (mean±std)  | CS (mean±std)  | Avg Rollouts/ep |
--------------------|---------------|----------------|----------------|-----------------|
base_only           | 0.490±0.023   | 0.000±0.000    | 100.0%±0.0%    | 0.00            |
always_trigger      | 0.970±0.005   | 1.000±0.000    | 0.0%±0.0%      | X.XX            |
random_50           | 0.890±0.010   | ~0.50±?        | ~50%±?         | X.XX            |
entropy_threshold   | 0.672±0.040   | ?              | ?              | X.XX            |
best_sigma_wrong    | 0.582±0.031   | ?              | ?              | X.XX            |
best_sigma_correct  | 0.970±0.005   | ?              | ?              | X.XX            |
scg_mlp             | 0.967±0.008   | ?              | ?              | X.XX            |
scg_prompt          | 0.957±0.006   | ?              | ?              | X.XX            |
scg_finetune_lr ⭐  | 0.967±0.008   | ?              | ?              | X.XX            |
oracle              | 0.970±0.005   | ?              | ?              | X.XX            |
```

### S0-2：计算 TES

**做什么**: 在 S0-1 的基础上计算 TES。

**公式**:

```python
def compute_tes(sr_method, sr_base, sr_always, cost_method, cost_always, cost_base=0.0):
    """
    sr_method:    方法的 Success Rate
    sr_base:      base_only 的 SR (下界)
    sr_always:    always_trigger 的 SR (上界参考)
    cost_method:  方法的 rollout 总次数 (或 RR)
    cost_always:  always_trigger 的 rollout 总次数 (或 RR)
    cost_base:    base_only 的 rollout 总次数 = 0
    """
    # Effectiveness: SR 提升占 always-trigger 提升的比例
    if sr_always == sr_base:
        effectiveness = 1.0 if sr_method >= sr_always else 0.0
    else:
        effectiveness = (sr_method - sr_base) / (sr_always - sr_base)
    effectiveness = max(0.0, min(1.0, effectiveness))

    # Efficiency: 成本节省占 always-trigger 成本的比例
    if cost_always == cost_base:
        efficiency = 1.0
    else:
        efficiency = (cost_always - cost_method) / (cost_always - cost_base)
    efficiency = max(0.0, min(1.0, efficiency))

    # TES: F1-style 调和平均
    if effectiveness + efficiency == 0:
        tes = 0.0
    else:
        tes = 2.0 * effectiveness * efficiency / (effectiveness + efficiency)

    return tes, effectiveness, efficiency
```

**计算时的参照点**（每个 seed 独立计算，然后取 mean±std）:

```
对 seed s ∈ {42, 123, 456}:
    SR_base[s]   = base_only 在 seed s 的 SR
    SR_always[s] = always_trigger 在 seed s 的 SR
    Cost_always[s] = always_trigger 在 seed s 的总 rollout 次数 (或 RR)
    Cost_base[s] = 0

    对每个 method:
        effectiveness[s] = (SR_method[s] - SR_base[s]) / (SR_always[s] - SR_base[s])
        efficiency[s]    = (Cost_always[s] - Cost_method[s]) / (Cost_always[s] - 0)
        TES[s]           = 2 * effectiveness[s] * efficiency[s] / (effectiveness[s] + efficiency[s])

TES_mean = mean(TES[42], TES[123], TES[456])
TES_std  = std(TES[42], TES[123], TES[456])
```

**输出格式**:

```
HotpotQA TES 完整表:
Method              | Effectiveness | Efficiency | TES (mean±std) |
--------------------|---------------|------------|----------------|
base_only           | 0.000         | 1.000      | 0.000          |
always_trigger      | 1.000         | 0.000      | 0.000          |
random_50           | ~0.83         | ~0.50      | ~0.63          |
scg_finetune_lr ⭐  | ~0.99         | ?          | ?              |
...
```

**关键检查点**:
- `scg_finetune_lr TES > 0.50`? → Phase 3 STRONG GO 标准 #1
- `scg_finetune_lr TES > random_50 TES`? → STRONG GO 标准 #1
- `scg_finetune_lr TES > entropy_threshold TES`? → STRONG GO 标准 #2
- `entropy_threshold TES < random_50 TES`? → STRONG GO 标准 #4

### S0-3：执行 6 项统计检验

**做什么**: 运行 `experiments/p3_analysis.py` 或手动实现以下检验。

**6 项检验及其公式**:

#### 检验 1: SCG-FineTune(LR) TES > Random-50% TES

```python
# 方法: Paired permutation test (3 seeds 太少用 t-test, 用 bootstrap)
# Bootstrap 10K:
#   1. 聚合 3 seeds × exploitation episodes (e.g., 150 ep/seed = 450 ep)
#   2. 对 450 ep 做 10000 次 bootstrap resample
#   3. 每次计算 TES_finetune - TES_random
#   4. p-value = 比例(diff < 0)
#
# 或: Wilcoxon signed-rank test on per-episode binary outcomes
from scipy.stats import wilcoxon
# 对 3 seeds 的 TES 配对: [TES_ft_s1, TES_ft_s2, TES_ft_s3] vs [TES_rand_s1, ...]
stat, p = wilcoxon(tes_finetune_per_seed, tes_random_per_seed, alternative='greater')

# 效应量: Cohen's d
d = (mean(tes_finetune) - mean(tes_random)) / pooled_std
```

#### 检验 2: SCG-FineTune(LR) TES > Entropy-Threshold TES

```python
# 同检验 1 方法
# 这是最核心对比: direction-aware vs fixed-direction
stat, p = wilcoxon(tes_finetune_per_seed, tes_entropy_per_seed, alternative='greater')
```

#### 检验 3: SCG-FineTune(LR) CS > Best-σ-correct-dir CS

```python
# Bootstrap on per-episode rollout decisions
# 验证 learning 优于 fixed rule (即使方向正确)
# 聚合 3 seeds 的 per-episode CS, bootstrap 10K
bootstrap_diff = []
for _ in range(10000):
    idx = np.random.choice(N, N, replace=True)
    cs_ft = compute_cs(finetune_episodes[idx])
    cs_fixed = compute_cs(fixed_correct_episodes[idx])
    bootstrap_diff.append(cs_ft - cs_fixed)
p_value = np.mean(np.array(bootstrap_diff) < 0)
ci_95 = np.percentile(bootstrap_diff, [2.5, 97.5])
```

#### 检验 4: Best-σ-wrong-dir SR < Always-T SR

```python
# McNemar's test: 配对的 episode-level success/fail
# 对每个 episode: (wrong_success, always_success) → 2×2 contingency table
from statsmodels.stats.contingency_tables import mcnemar
# b = wrong fails but always succeeds
# c = wrong succeeds but always fails
result = mcnemar([[a, b], [c, d]], exact=True)
p_value = result.pvalue

# 效应量
delta_sr = sr_always - sr_wrong  # 预期 ~0.388 (0.970 - 0.582)
```

#### 检验 5: Entropy-Threshold TES < Random-50% TES

```python
# 同检验 1 方法, alternative='less'
stat, p = wilcoxon(tes_entropy_per_seed, tes_random_per_seed, alternative='less')
# 验证 fixed positive direction 在负相关环境系统性失败
```

#### 检验 6: SCG-FineTune(LR) SR ≈ Always-T SR (n.s.)

```python
# 等价性检验 (TOST: Two One-Sided Tests)
# H0: |SR_ft - SR_always| > δ (δ = 0.03, 即 3pp 等价界限)
# 如果两个单侧检验都显著 → 等价成立
from scipy.stats import ttest_rel
delta = 0.03  # 等价界限
diff = sr_finetune_per_seed - sr_always_per_seed

# 上侧: mean(diff) < δ
t1, p1 = ttest_rel(sr_finetune_per_seed, sr_always_per_seed - delta)
# 下侧: mean(diff) > -δ
t2, p2 = ttest_rel(sr_finetune_per_seed, sr_always_per_seed + delta)
p_tost = max(p1/2, p2/2)  # TOST p-value
```

**效应量报告** (NeurIPS 要求):

```python
# Cohen's d for SR 差异
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

# 所有关键对比的 Cohen's d:
# finetune vs random_50, finetune vs entropy, wrong vs always, etc.
```

### S0-4：Phase 2 vs Phase 3 数据一致性检查

**做什么**: 确认 seed=42 数据来源。

**怎么做**:

```bash
# 1. 检查 Phase 2 和 Phase 3 的 seed=42 结果文件是否相同
diff results/phase2/hotpotqa/scg_finetune_lr/seed_42/performance_summary.json \
     results/phase3/hotpotqa/scg_finetune_lr/seed_42/performance_summary.json

# 2. 如果不同, 记录差异:
#    - Phase 2: SR=0.953, CS=49.5%, TES=0.654
#    - Phase 3: SR=0.960, CS=?, TES=?
#    - 差异来源? 重跑 or 复用?

# 3. 检查 patch 脚本做了什么
cat scripts/phase3/run_phase3_patch_seed42.sbatch
```

**输出**: 一致性报告，明确说明 seed=42 数据是复用还是重跑，以及差异原因。

---

## S1：诊断 CS 退化（条件性——仅当 S0 发现 CS 异常时执行）

**触发条件**: S0-1 计算出 `scg_finetune_lr CS < 20%`（Phase 2 为 49.5%）
**预计耗时**: 2-4 小时
**前置条件**: S0 完成

### S1-1：Per-Step Rollout 行为分析

**做什么**: 对比 Phase 2 和 Phase 3 中 scg_finetune_lr 的逐步触发模式。

**怎么做**:

```python
# 从 Phase 3 episode 数据中提取:
for episode in episodes:
    for step in episode.steps:
        record = {
            "episode_id": episode.id,
            "step": step.index,
            "gate_decision": step.trigger,  # True/False
            "gate_probability": step.gate_prob,  # P(trigger | features)
            "features": step.features,  # [token_entropy, evidence_count, ...]
            "utility": step.utility if available else None,
        }
```

**需要测试的指标**:

| 指标 | 公式 | 预期 (Phase 2) | 如果异常说明什么 |
|------|------|----------------|----------------|
| **Step-0 trigger rate** | `Σ trigger_at_step0 / N_episodes` | ~80-90% | Step 0 U 最高, 应该 trigger |
| **Step-1+ trigger rate** | `Σ trigger_at_step>0 / Σ steps>0` | ~30-40% | 非首步应选择性 trigger |
| **Gate probability 分布** | `histogram(P(trigger \| σ))` | 双峰 (0.2 附近 + 0.8 附近) | 单峰(>0.8)=always trigger |
| **Threshold τ** | Gate 的决策阈值 | 0.5 (default) | 如果 preload 改变了 τ |

### S1-2：Phase 1 数据预加载影响分析

**做什么**: 检查 Phase 3 的 Phase 1 数据预加载是否改变了 gate 行为。

**怎么做**:

```python
# Phase 3 的关键代码路径:
# preloaded = preload_phase1_data(gate, phase1_data_path)
# if preloaded >= gate.min_cal_points:
#     gate._on_transition()
#     gate.phase = "exploitation"

# 检查:
# 1. Phase 1 预加载了多少数据点?
print(f"Preloaded: {preloaded} points")
# 2. Gate 训练后的权重是什么?
print(f"LR weights: {gate.model.coef_}")
print(f"LR intercept: {gate.model.intercept_}")
# 3. 与 Phase 2 在 200 ep probe 后训练的权重对比
```

**关键假设**: Phase 2 中 gate 在 50 ep probe + 150 ep exploit 模式下训练；Phase 3 用 Phase 1 的 500+ 数据点直接训练。训练数据不同可能导致不同的决策边界。

### S1-3：控制实验（如果 S1-1/S1-2 确认问题）

**做什么**: 用 Phase 2 完全相同的配置（不预加载 Phase 1 数据，probe 50 ep + exploit 150 ep）重跑 scg_finetune_lr。

**怎么做**:

```yaml
# 修改 configs/phase3_core_experiments.yaml:
hotpotqa:
  phase1_data_path: null  # 不预加载, 改为 probe 模式
  gate:
    min_cal_points: 50     # 与 Phase 2 一致
    explore_episodes: 50   # probe 50 ep

# 仅跑 scg_finetune_lr × 3 seeds × 200 ep
# 3 runs, ~1.5 小时
```

**需要测试的指标**:

| 指标 | 公式 | 预期 |
|------|------|------|
| CS (no-preload) | 同 S0-1 | ~49.5% (与 Phase 2 一致) |
| TES (no-preload) | 同 S0-2 | ~0.654 (与 Phase 2 一致) |
| SR (no-preload) | episode success / total | ~0.953 (与 Phase 2 一致) |

**判断**:
- 如果 no-preload CS ≈ 49.5% → **确认是预加载导致的行为变化**，论文中需要讨论
- 如果 no-preload CS 仍然 ≈ 0% → 问题不在预加载，需进一步排查

---

## S2：第 2/3 个有效环境（解决 "仅 1 个有效环境" 致命弱点）

**预计耗时**: 1.5-2 天
**前置条件**: S0 完成
**阻塞性**: 🔴 是——NeurIPS 投稿需要 ≥2 个 gate 有效差异化的环境

### 核心问题

当前 MBPP (base SR=92.7%) 和 HumanEval (base SR=92.1%) 均 ceiling effect。**需要一个 base SR 在 50-80% 的环境，使 rollout optimizer 有提升空间，gate 有差异化空间。**

### 方案对比

| 方案 | 新环境 | 预期 base SR | 搭建成本 | 额外收益 | 推荐度 |
|------|--------|------------|---------|---------|--------|
| **A: 小模型** | MBPP+HumanEval on Qwen3-1.5B | 60-75% | ⭐ 极低 | 同时回应 "单一 backbone" 质疑 | ⭐⭐⭐⭐⭐ |
| **B: 难 benchmark** | APPS Introductory on Qwen3-4B | 30-60% | ⭐⭐ 中等 | 不同难度的代码环境 | ⭐⭐⭐ |
| **C: 不同任务类型** | WebArena (Phase 4 提前) on Qwen3-4B | <50% | ⭐⭐⭐ 高 | 新任务类型(web 导航) | ⭐⭐ |
| **D: 数学推理** | GSM8K on Qwen3-4B | 50-70% | ⭐⭐ 中等 | 第三种任务类型 | ⭐⭐⭐ |

### 方案 A（强烈推荐）：Qwen3-0.6B 跑 MBPP + HumanEval

**理由**:
1. **零搭建成本**: 环境代码完全复用 `frvc/envs/mbpp_env.py` 和 `frvc/envs/humaneval_env.py`
2. **双重收益**: 同时解决 "仅 1 个有效环境" + "仅单一 backbone 模型" 两个 reviewer 攻击点
3. **时间最短**: 仅需改配置中的 model name，不需要新代码
4. **科学价值**: 验证 signal-utility 方向在不同模型能力下是否稳定

#### A-0: GO/NO-GO 预检（2 runs, ~30 min）

**做什么**: 确认 Qwen3-0.6B 在 MBPP/HumanEval 上 base SR 足够低。

```yaml
model: Qwen/Qwen3-0.6B
method: base_only
episodes: 50  # 快速预检
seeds: [42]
environments: [mbpp, humaneval]
```

**需要测试的指标**:

| 指标 | 公式 | GO 阈值 | NO-GO 阈值 |
|------|------|---------|-----------|
| **Base SR (MBPP)** | `成功 episodes / 50` | < 85% | ≥ 85% |
| **Base SR (HumanEval)** | `成功 episodes / 50` | < 85% | ≥ 85% |
| **Always-trigger SR** | 同上，method=always_trigger | > Base SR + 3pp | = Base SR |

**判断**:
- 两个环境 base SR < 85% **且** always > base → ✅ GO，执行 A-1
- 一个环境 base SR < 85% → ✅ GO 该环境
- 两个都 ≥ 85% → ❌ 转方案 B

#### A-1: Phase 1 Signal Discovery (Qwen/Qwen3-0.6B)

**做什么**: 在 Qwen/Qwen3-0.6B 下重新测量 signal-utility 关系，获得 Phase 1 数据。

```yaml
model: Qwen/Qwen3-0.6B
environments: [mbpp, humaneval]  # 仅 GO 的环境
episodes: 200
seeds: [42]
rollout: { temperature: 0.7, K: 5 }
sample_every: 1
```

**需要测试的指标**:

| 指标 | 公式 | 含义 | 关键检查 |
|------|------|------|---------|
| **Utility mean** | `mean(U)` | 平均 rollout 收益 | > 0 |
| **Utility std** | `std(U)` | U 的方差 | > 0.1 |
| **U > 0 比例** | `sum(U > 0) / N` | 正 utility 比例 | > 20% |
| **ρ(token_entropy, U)** | Spearman 秩相关 | entropy-utility 方向 | 与 4B 同/异？|
| **ρ(step_count, U)** | Spearman 秩相关 | step-utility 方向 | — |
| **ρ(test_pass_rate, U)** | Spearman 秩相关 | pass_rate-utility 方向 | — |
| **MI(token_entropy, U)** | 互信息 (nats) | 非线性关系强度 | > 0.03 |

```python
# Spearman rho
from scipy.stats import spearmanr
rho, p_value = spearmanr(signal_values, utility_values)

# Mutual Information (binned estimator)
from sklearn.metrics import mutual_info_score
# 将连续值离散化为 10-20 bins
signal_binned = pd.qcut(signal_values, q=10, labels=False, duplicates='drop')
utility_binned = pd.qcut(utility_values, q=10, labels=False, duplicates='drop')
mi = mutual_info_score(signal_binned, utility_binned) / np.log(2)  # 转 bits → nats: * ln2
```

**关键输出**: Signal 方向矩阵

```
Qwen3-1.5B Signal Direction:
                  MBPP ρ    HumanEval ρ   HotpotQA ρ (4B)   MBPP ρ (4B)
token_entropy     ???       ???            −0.327 (neg)      +0.153 (pos)
step_count        ???       ???            ...               ...
```

**C2 的关键验证**: token_entropy 方向在 1.5B 下是否与 4B 一致？如果 1.5B 也出现方向差异（或与 4B 不同），这是更强的 C2 证据。

#### A-2: Phase 3 Core Experiments (Qwen3-1.5B)

**做什么**: 在有效环境上跑核心方法对比。

**方法矩阵**（精简版，6 方法）:

| # | Method | 类别 | 说明 |
|---|--------|------|------|
| 1 | `base_only` | 下界 | 不使用 optimizer |
| 2 | `always_trigger` | 上界参考 | 每步触发 |
| 3 | `random_50` | baseline | 50% 随机触发 |
| 4 | `best_sigma_wrong` | ablation | 错误方向（C2/C3 证据）|
| 5 | `scg_finetune_lr` ⭐ | 主方法 | Direction-aware LR gate |
| 6 | `oracle` | 上界 | 逐步最优 |

**配置**:

```yaml
model: Qwen/Qwen3-0.6B
seeds: [42, 123, 456]
episodes_per_seed: 200  # MBPP; HumanEval 用 164
methods: [base_only, always_trigger, random_50, best_sigma_wrong, scg_finetune_lr, oracle]
total_runs: 6 methods × 3 seeds × N_envs(1-2) = 18-36 runs
```

**需要测试的指标** (每个方法 × 每个 seed):

| 指标 | 公式 | 怎么计算 |
|------|------|---------|
| **SR** | `成功 episodes / 总 episodes` | 逐 episode 判断 |
| **RR** | `总 rollout 调用 / 总 steps` | 逐 step 统计 |
| **CS** | `1 - RR_method / RR_always` | 需要 always_trigger 的 RR 作参照 |
| **Effectiveness** | `(SR_method - SR_base) / (SR_always - SR_base)` | 需要 base 和 always 的 SR |
| **Efficiency** | `(Cost_always - Cost_method) / (Cost_always - 0)` | Cost = 总 rollout 次数 |
| **TES** | `2 × Eff × Effc / (Eff + Effc)` | 调和平均 |

**关键检查点**:
- `scg_finetune_lr SR > base_only SR` (显著)? → Gate 有效
- `scg_finetune_lr TES > random_50 TES`? → 学习优于随机
- `best_sigma_wrong SR < always_trigger SR` (显著)? → 方向重要
- `scg_finetune_lr CS > 20%`? → 有实际成本节省

**总计算量**:
- A-0: 2 runs (~30 min)
- A-1: 2 runs (~2 hr, 因为 1.5B 推理更快)
- A-2: 18-36 runs (~4-8 hr with GPU parallelism)
- **总计 ~0.5-1 天**

### 方案 B（备选）：APPS Introductory on Qwen3-4B

仅当方案 A 的 GO/NO-GO 失败（1.5B 在两个环境都 ceiling）时执行。

**搭建工作**:

```python
# 1. 新建 frvc/envs/apps_env.py
#    - 使用 HuggingFace datasets: load_dataset("codeparrot/apps", split="test")
#    - 筛选 difficulty="introductory" (~1000 题)
#    - 执行: Python subprocess with timeout
#    - Reward: test case pass rate (0-1)

# 2. 配置
model: Qwen/Qwen3-4B-Instruct-2507
episodes: 200
seeds: [42, 123, 456]
methods: [base_only, always_trigger, random_50, best_sigma_wrong, scg_finetune_lr, oracle]
```

---

## S3：Phase 3.5 CMDP 实验

**预计耗时**: 1-2 天
**前置条件**: S0 完成（需要 HotpotQA 的 CS/RR 数据）
**阻塞性**: 🟠 P1——强烈建议但不阻塞

### S3-1: Lagrangian Dual Ascent 收敛验证

**做什么**: 验证 CMDP dual ascent 能自动找到满足任意 CS target 的最优阈值 τ(λ*)。

**怎么做**:

```python
def lagrangian_dual_ascent(gate_model, eval_episodes, cs_target, alpha=0.01, max_iter=200):
    rr_target = 1.0 - cs_target
    lambda_k = 0.0

    history = []
    for k in range(max_iter):
        tau_k = 0.5 + lambda_k
        sr_k, rr_k, cs_k = evaluate_gate(gate_model, eval_episodes, threshold=tau_k)
        lambda_k = max(0, lambda_k + alpha * (rr_k - rr_target))
        history.append({"iter": k, "lambda": lambda_k, "tau": tau_k,
                        "sr": sr_k, "rr": rr_k, "cs": cs_k})
        if abs(rr_k - rr_target) < 0.01:
            break
    return lambda_k, tau_k, sr_k, cs_k, history
```

**CS target sweep**:

| CS_target | RR_target | 含义 |
|-----------|-----------|------|
| 30% | 70% | 轻度节省 |
| 40% | 60% | 中度节省 |
| 50% | 50% | 平衡点 |
| 60% | 40% | 重度节省 |
| 70% | 30% | 极度节省 |

**需要测试的指标**:

| 指标 | 公式 | GO 标准 |
|------|------|---------|
| **收敛率** | `收敛的 CS_target 数 / 5` | ≥ 80% (4/5) |
| **收敛速度** | `达到 |RR - RR_target| < 1pp 的迭代数` | < 100 iter |
| **λ* 值** | Dual ascent 最终的 λ | 记录即可 |
| **τ(λ*) 值** | `0.5 + λ*` | 记录即可 |
| **达标 CS** | `实际 CS 与 target 的偏差` | |CS_actual - CS_target| < 3pp |
| **SR 损失** | `SR(λ*) vs SR(λ=0)` | SR 损失 < 5pp |

### S3-2: Manual Threshold Sweep (Baseline)

**做什么**: 手动扫描 τ 构建 Pareto 前沿，与 dual ascent 对比。

```python
manual_thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

for tau in manual_thresholds:
    sr, rr, cs = evaluate_gate(gate_model, eval_episodes, threshold=tau)
    # 记录 (CS, SR) 点
```

**需要测试的指标**:

| 指标 | 公式 | 含义 |
|------|------|------|
| **Pareto 最优性** | Dual ascent 点到 manual Pareto 前沿的距离 | < 2pp |
| **Pareto 前沿** | 非被支配的 (CS, SR) 点集 | 可视化 |

### S3-3: 跨环境 λ* 对比

**做什么**: 在 HotpotQA 和 MBPP（如果 gate 有效）上比较相同 CS target 产生的 λ*。

**需要测试的指标**:

| 指标 | 公式 | 预期 |
|------|------|------|
| **λ* 差异** | `λ*_hotpotqa - λ*_mbpp` (同 CS target 下) | ≠ 0 (环境需要不同 λ) |
| **τ* 差异** | `τ*_hotpotqa - τ*_mbpp` | ≠ 0 |

**总运行数**: 5 CS_targets × 2 envs × 3 seeds + 6 thresholds × 2 envs × 3 seeds = 30 + 36 = **66 evaluation runs**（无需重新训练，仅评估，~2-3 小时）。

---

## 执行优先级与时间线

```
Day 0 (立即, ~3 hr):
├── S0-1: 计算 RR/CS ← 从已有数据提取
├── S0-2: 计算 TES ← 依赖 S0-1
├── S0-3: 6 项统计检验 ← 依赖 S0-2
└── S0-4: 数据一致性检查

Day 0 晚 (决策点):
├── IF scg_finetune_lr TES > 0.50 → Phase 3 = GO
│   ├── IF CS > 20% → S1 跳过, 进入 S2
│   └── IF CS < 20% → 执行 S1 诊断 (Day 1)
└── IF scg_finetune_lr TES < 0.50 → Phase 3 = CONCERN
    └── 必须执行 S1 + 诊断 (Day 1)

Day 1 (~6 hr):
├── S2/A-0: GO/NO-GO 预检 (Qwen3-1.5B, 30 min)
├── S2/A-1: Phase 1 Signal Discovery (2 hr, 与 S1 并行)
├── [条件] S1: CS 退化诊断 (如果触发)
└── S2/A-2 Day1: 关键方法 (scg_finetune_lr, wrong_dir, base, always × 3 seeds)

Day 2 (~6 hr):
├── S2/A-2 Day2: 补充方法 (random_50, oracle × 3 seeds)
├── S2 统计分析: TES/CS + 检验
└── S3-1: CMDP Dual Ascent (HotpotQA, 2 hr)

Day 3 (~4 hr):
├── S3-2: Manual threshold sweep
├── S3-3: 跨环境 λ* 对比
├── 全部可视化: Pareto 图 + 收敛曲线
└── 更新 Phase 3 报告 + Writing Guide
```

---

## 指标速查表

### 核心指标公式汇总

| 指标 | 公式 | 范围 | 越大越好？ |
|------|------|------|-----------|
| **SR** (Success Rate) | `成功 ep / 总 ep` | [0, 1] | ✅ |
| **RR** (Rollout Rate) | `总 rollout 调用 / 总 steps` | [0, 1] | ❌ (越低越省) |
| **CS** (Cost Saving) | `1 - RR_method / RR_always` | [0, 1] | ✅ |
| **Effectiveness** | `(SR_m - SR_base) / (SR_always - SR_base)` | [0, 1] | ✅ |
| **Efficiency** | `(Cost_always - Cost_m) / (Cost_always - 0)` | [0, 1] | ✅ |
| **TES** | `2 × Effectiveness × Efficiency / (Eff + Effc)` | [0, 1] | ✅ |
| **Spearman ρ** | `scipy.stats.spearmanr(signal, utility)` | [-1, 1] | 方向性 |
| **MI** | `mutual_info_score(binned_signal, binned_utility)` | [0, ∞) | ✅ |
| **Cohen's d** | `(μ₁ - μ₂) / σ_pooled` | (-∞, ∞) | 绝对值越大效应越大 |

### 判断标准速查

| 判断 | 条件 |
|------|------|
| **Phase 3 STRONG GO** | TES_LR > 0.50 且 > TES_random (p<0.05) 且 TES_LR > TES_entropy (p<0.05) 且 SR_wrong < 0.70 且 TES_entropy < TES_random |
| **Phase 3 GO** | TES_LR > 0.50 且 SR_wrong < 0.75 |
| **Phase 3 WEAK** | TES_LR 的 std > 0.10 或 SR_wrong 某 seed > 0.80 |
| **Phase 3 CONCERN** | TES_LR < TES_random |
| **S2 环境 GO** | base SR < 85% 且 always SR > base SR + 3pp |
| **S3 CMDP GO** | ≥ 80% CS targets 收敛，dual ascent 在 Pareto 前沿 ±2pp |

---

## 产出清单

完成全部补充实验后，论文将拥有:

| 产出 | 来源 | 论文位置 |
|------|------|---------|
| HotpotQA 完整 Table (10 方法 × SR/CS/TES) | S0 | Table 2 主表 |
| 6 项统计检验 + 效应量 | S0 | Table 2 脚注 |
| Qwen3-1.5B 环境结果 (6 方法 × SR/CS/TES) | S2 | Table 2 新列 |
| Signal 方向矩阵 (2 模型 × 3 环境) | S2/A-1 | Table 1 扩展 |
| CMDP Pareto 曲线 | S3 | Figure 5 |
| Dual ascent 收敛曲线 | S3 | Appendix |
| 跨环境 λ* 对比 | S3 | Section 4.3 |

**论文 Claims 预期改善**:

| Claim | 当前支持 | 补充后支持 |
|-------|---------|-----------|
| C1: Gate learning 有效 | ⚠️ SR 层面 | ✅ SR + TES + 多环境 |
| C2: 方向因环境而异 | 🔴 仅 1 有效环境 | ✅ 2-3 有效环境 + 2 backbone |
| C3: 方向发现重要 | ✅ 强 | ✅ 更强 (跨模型验证) |
| C5: Architecture-agnostic | ⚠️ 仅 1 backbone | ✅ 2 backbones |
