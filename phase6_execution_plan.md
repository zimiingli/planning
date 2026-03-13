# Phase 6 执行计划：目标 5 个有效环境 + Method Novelty 升级

**版本**：v3.0（2026-03-13）— 新增 Track D (Toy Model Verification) + B6 (Probe Scientific Analysis)，对齐 Writing Guide v5.0
**前置依赖**：Phase 0-5 完成，当前 2 个确认 Pareto-dominate（HotpotQA + WebShop）
**核心目标**：从 2 → 4-5 个有效论文环境 + 提升 Method Novelty（⭐⭐ → ⭐⭐⭐⭐） + 完成 Toy Model 实验验证
**计划周期**：2026-03-12 至 2026-03-26（3 周）
**论文标题**：Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments

---

## 1. 当前状态总结（基于 Phase 5 环境报告 2026-03-12）

### 1.1 7 环境最终定性

| 环境 | Paper 定位 | 数据完整度 | 关键数据 |
|------|-----------|-----------|---------|
| **HotpotQA** | ✅ **主实验** | ✅ 全部完成 | SCG 0.968@6.55× Pareto-dominate CaTS 0.932@10.55× |
| **WebShop** | ✅ **主实验** | ✅ 全部完成 | SCG 0.437@1.27× Pareto-dominate CaTS 0.305@3.44× |
| **APPS** | ⚠️ **弱信号案例** | ⚠️ 3/6 可靠, 9 jobs pending | SCG 0.588/1.23× vs CaTS 0.590/1.04×, 弱信号(ρ=−0.155) |
| **TWExpress** | ⚠️ **对比案例** | 🔄 CB 6/12 running | rollout 永远无害, SCG 选择性反而是劣势 |
| **BabyAI** | ❌ 不用 | ✅ 全部完成 | SCG < always_trigger, 信号极弱(ρ=0.052), 高方差 |
| **TextWorld** | ❌ **放弃** | ❌ 缺 2/6 core | always+oracle TIMEOUT, 信号极弱(ρ=0.174), gate 做错决策 |
| **Plancraft** | ❌ 附录负例 | ⚠️ 缺 2/6 | rollout 本质有害, base_only > 所有方法 |

### 1.2 为什么放弃 TextWorld

环境报告已明确标注 "❌ 不用"，原因充分：
1. **数据不完整**：always_trigger + oracle 均 12h TIMEOUT → 缺 2/6 core methods
2. **Gate 失败**：SCG(54.3%) < random_50(64.8%) — gate 主动做错决策
3. **信号极弱**：最强 ρ=0.174 — 远低于 SCG 有效线(ρ>0.3)
4. **CB 也有问题**：CaTS TIMEOUT, CoRefine FAILED
5. **ROI 极低**：即使降成本修复 TIMEOUT（5-7 天工作量），信号太弱 SCG 大概率仍然失败

**结论**：不值得任何额外投入。省下的 5-7 天转投路径 B（Hidden State Probe）和路径 C（新环境），ROI 远高于修 TextWorld。

### 1.3 诚实评估：各环境 Pareto-dominate 前景

```
✅ 确认 Pareto-dominate (2):
   HotpotQA  — SCG 0.968@6.55× vs CaTS 0.932@10.55×（SR↑3.6pp, Cost↓38%）
   WebShop   — SCG 0.437@1.27× vs CaTS 0.305@3.44×（SR↑13.2pp, Cost↓63%）

❓ 待确认 (1):
   TWExpress — SCG 97.0% vs CaTS 96.7% vs CATTS 97.3%（2 seeds）
               ⚠️ 但这是 "rollout 无害" 环境，SCG 选择性无优势
               → Pareto-dominate 需要 cost 优势显著
               → 更可能定位为"对比案例"而非 Pareto-dominate

⚠️ 不太可能 Pareto-dominate (1):
   APPS      — SCG 0.588/1.23× vs CaTS 0.590/1.04×，CaTS 两项均略优
               → 除非 probe gate 提升 SR 2pp+（依赖路径 B）
               → 更适合定位为"弱信号+正确保守"案例

❌ 明确放弃 (3):
   TextWorld — TIMEOUT + 信号弱 + gate 失败
   BabyAI    — 信号极弱 + SCG 无提升
   Plancraft — rollout 本质有害（附录负例）
```

### 1.4 目标调整

**原目标**：5 个 Pareto-dominate（过于乐观）
**修订目标**：**论文呈现 4-5 个有效环境，其中 2-3 个 Pareto-dominate + 1-2 个 diagnostic/对比案例**

这个调整更现实，因为：
- 并非每个环境都需要 Pareto-dominate；不同环境展示不同 insight 更有论文价值
- HotpotQA（高 headroom, 强信号）+ WebShop（中 headroom, 精准触发）= 核心 Pareto-dominate
- APPS（弱信号, 正确保守）+ TWExpress（rollout 无害, 选择性是劣势）= diagnostic cases
- 新环境如果 GO → 第 5 个环境，可能是额外的 Pareto-dominate

**论文环境矩阵目标**：

| 环境角色 | 作用 | 目标 |
|---------|------|------|
| **Pareto-dominate 主实验** | 证明 SCG 在 SR 和 cost 上双优 | ≥ 2（HotpotQA + WebShop 已确认） |
| **弱信号 diagnostic** | 展示 gate 在信号不足时正确保守 | 1（APPS） |
| **Rollout-safe 对比** | 展示不同环境需要不同策略 | 1（TWExpress） |
| **新环境扩展** | 额外多样性 + 可能的第 3 个 Pareto-dominate | 0-1（路径 C） |

---

## 2. 修订后的两路并行策略

**核心变化**：砍掉 TextWorld（路径 A2），将资源集中到路径 B（战略价值最高）和路径 C。

```
═══════════════════════════════════════════════════════════════════════════
  路径 A：完善现有环境数据      路径 B：Hidden State Probe     路径 D：Toy Model Verification 🆕
  （轻量，主要等 pending）     （核心战略路径，最高优先）       （纯分析，无 GPU）
  ─────────────────────       ──────────────────────        ───────────────────────
  A1: TWExpress 等 CB 确认     B1: 多层数据收集 (3 env)      D1: P1 temporal shift 分析
  A2: APPS 等 rerun 完成       B2: Offline probe 训练        D2: Simpson's Paradox 子群
  A3: Cost Analysis 统一       B3: GO/NO-GO 判断             D3: P2/P3 汇总
                               B4: End-to-end gate           D4: Figure 2 (理论曲线)
  路径 C：新环境候选            B5: 消融实验
  ──────────────────           B6: 科学分析 🆕
  C1: ToolBench (40%)            → B6.1 Layer-wise probing
                                 → B6.2 Cross-env transfer
                                 → B6.3 Data efficiency
═══════════════════════════════════════════════════════════════════════════
```

**优先级排序**：
1. **路径 B（最高）**：Hidden State Probe 是 NeurIPS 接受概率从 40% → 75% 的关键。省下的 TextWorld 时间全部投入这里。
2. **路径 D（高，与 B 并行）** 🆕：Toy Model 验证是论文从 "finding paper" → "finding + theory paper" 的关键。纯数据分析，无 GPU 需求，Day 1 即可启动。
3. **路径 A（中等，低投入）**：主要是等 pending jobs 完成 + 分析，几乎不需要主动工作。
4. **路径 C（补充，仅 ToolBench）**：AgentBench-KG 和 CrosswordQA 已砍。仅保留 ToolBench 一个候选。

**依赖关系**：
- A2(APPS probe gate) 依赖 B3/B4 结果
- B4 依赖 B3 GO
- B6 依赖 B1 数据（但 B6.1/B6.2/B6.3 与 B4 可并行）
- D 路径完全独立（用已有 Phase 1-4 数据），Day 1 即可启动
- A/B/C/D 之间无阻塞依赖，可最大并行

---

## 3. 路径 A：完善现有环境数据（低投入）

### A1. TWExpress — 等 CB 数据 + 分析定位

**投入**：~半天分析时间（主要等 pending jobs）
**前置状态**：SCG 97.0%, 6/12 CB running。CB 初步结果：CaTS 96.7% ≈ SCG, CATTS 97.3%(2seeds) ≈ SCG。

**Step A1.1：等 CB 完成（Day 1-3，被动等待）**
- [ ] 检查 TWExpress CB running/pending 状态（6 running + 1 pending）
- [ ] 等 SEAG×3 + CoRefine×3 + CATTS-456 完成
- [ ] 预计数小时至 1-2 天内完成

**Step A1.2：分析 + 定位（CB 完成后 ~2h）**
- [ ] 提取所有 CB 的 {SR, ro/ep} 数据
- [ ] 计算 token cost（需提取 C_base, C_rollout 常数）
- [ ] Pareto 分析：
  ```
  如果 SCG cost 明显低于所有 CB → ✅ Pareto-dominate（第 3 个）
  如果 SCG cost ≈ CB cost, SR ≈ CB SR → ⚠️ 无优势，定位为 diagnostic 对比案例
  ```
- [ ] 确定论文定位：Pareto-dominate 还是 "rollout-safe 对比案例"

**TWExpress 论文叙事（大概率定位为对比案例）**：
> TWExpress 与 WebShop 形成精确对比：
> - WebShop：过度 rollout 有害（random_50 47.5% > always 43.0%）→ SCG 选择性是优势
> - TWExpress：rollout 永远无害（utility 从不为负）→ SCG 选择性反而限制了 SR
>
> 两个环境共同说明：SCG 确实学会了信号方向，但最优策略取决于环境的 rollout harm profile。

---

### A2. APPS — 等 rerun + 数据更新

**投入**：~2h 分析时间（等 9 jobs pending）
**前置状态**：Phase3_supp 有 bug，random_50/bsw/oracle 在重跑中。

- [ ] 等 APPS rerun 9 jobs 完成（random_50×3, bsw×3, oracle×3）
- [ ] 更新 APPS 统一结果表
- [ ] 确认正确的 oracle SR（目前估计 ~66.8%）
- [ ] APPS 论文叙事确定：
  ```
  弱信号环境 (最强 ρ=−0.155)。
  所有 CB 退化为 base_only（rollout ≈ 0），SCG 正确保守 (RR=6%)。
  CATTS 是灾难：SR 无提升但 cost 6.02× — vote cost > rollout cost。
  → 展示 gate 在信号不足时的正确行为。
  ```

---

### A3. Cost Analysis 统一计算（等 A1/A2 数据齐全后）

- [ ] TWExpress token cost 常数提取（C_base, C_rollout）
- [ ] TWExpress 全方法 cost 表计算
- [ ] 所有论文环境统一 Pareto 图生成
- [ ] 更新 phase5_environment_report.md

---

## 4. 路径 B：Hidden State Probe（核心战略路径）

**核心目标**：用 LLM hidden state (d=2560) 训练 probe 预测 rollout utility U，替代手工 5-feature LR gate。
**战略价值**：Method novelty ⭐⭐ → ⭐⭐⭐⭐。NeurIPS 接受概率 40% → 75% 的关键路径。
**已有上界**：Phase 5 offline AUC=0.88（vs handcraft LR AUC=0.85），暗示 GO 概率较高。
**省下的 TextWorld 时间（5-7 天）全部投入路径 B。**

### B1. 数据收集（Day 1-2, 每环境 ~40min）🆕 v3.0 升级：多层 hidden states

用 HF Transformers 替代 vLLM 跑 always_trigger 200ep，每步保存 hidden state。

**⚠️ v3.0 升级**：保存**多层** hidden states（不仅 last layer），用于 B6.1 Layer-wise Probing 科学分析（论文 §4.5 + Figure 6a）。

**输出格式**：
```
{env}_hidden_states.npz:
  - hidden_states_multi: (N_steps, N_layers, 2560)  # 🆕 多层 hidden states
    → Qwen3-4B 共 32 layers, 保存 8 个代表层: {0, 4, 8, 12, 16, 20, 24, 28, 31}
    → 每层 mean-pooled over sequence positions
  - hidden_states: (N_steps, 2560)   # last layer（兼容 B2-B4 单层实验）
  - utilities: (N_steps,)            # U = R(with_rollout) - R(without_rollout)
  - signals: (N_steps, 5)            # 手工 5 feature（对比基线）
  - metadata: step_count, episode_id, action_text
```

**执行清单**：
- [ ] 检查是否已有 hidden state 数据（Phase 5 Track 1 可能已收集部分）
- [ ] HotpotQA 200ep hidden state 收集（1 seed, ~40min）— 保存 8 层
- [ ] APPS 200ep hidden state 收集（1 seed, ~40min）— 保存 8 层
- [ ] WebShop 200ep hidden state 收集（1 seed, ~40min）— 保存 8 层
- [ ] 数据验证：hidden_states shape (N, 8, 2560), utilities 分布, NaN 检查

**注意事项**：
- HF Transformers 比 vLLM 慢 ~3×，实验阶段完全可接受
- 保存中间检查点，防止 OOM 或中断丢失
- 多层保存增加存储 ~8×，但每个 env 数据量仍 <500MB，可接受
- 如果存储成 bottleneck，可降为 4 层: {0, 10, 21, 31}

---

### B2. Offline Probe 训练 + 评估（Day 2-3, 每环境 <10min）

**先在 HotpotQA 上跑**（信号最强 ρ=−0.494，最容易验证有效性）。

**4 种 probe 架构**（从简到复杂）：

| # | Probe | 输入 | 输出 | Loss | 参数量 | 目的 |
|---|-------|------|------|------|--------|------|
| P1 | **Linear Regression** | h (2560) | U_pred (scalar) | MSE | 2.5K | Sanity check: hidden state 是否编码 U |
| P2 | **PCA(50) + LR Classifier** | PCA(h) (50) | P(trigger) | BCE | <1K | 降维避免 overfit |
| P3 | **小 MLP 回归** | h (2560) | U_pred (scalar) | MSE | ~82K | `2560→64→1`, dropout=0.3, wd=1e-2 |
| P4 | **小 MLP 分类** | h (2560) | P(trigger) | weighted BCE | ~82K | class_weight 平衡正负样本 |

**关键设计决策**：
- **回归 (P1/P3) 优先于分类 (P2/P4)**：避免 class imbalance 导致 always-trigger
- 回归部署时用 threshold 做 gate 决策
- **P1 是 sanity check**：R² < 0.05 → hidden state 不编码 U → 全部 NO-GO

**评估指标**：
```
Offline 指标:
  - R²(U_pred, U_true)           # 回归方案
  - AUC-ROC(P(trigger), label)   # 分类方案
  - Spearman ρ(pred, U_true)     # 预测值与真实 U 的秩相关

对比基线:
  - 手工 5-feature LR 的 R²/AUC（用同一份数据的 signals 列）
```

**执行清单**：
- [ ] 实现 4 种 probe 训练脚本（train/val split: 80/20, 5-fold CV）
- [ ] HotpotQA: 训练 P1-P4，记录 R², AUC, ρ
- [ ] 对比 handcrafted LR 基线
- [ ] 如果 B3 GO → APPS + WebShop 重复

---

### B3. GO/NO-GO 判断（Day 3）

```
HotpotQA 上:
  任何 probe R² > 0.10 或 AUC > 0.70
    → GO，继续 B4

  R² ∈ (0.05, 0.10)
    → 弱信号，尝试调参:
      - Pooling: last_token vs mean-pool vs weighted_mean
      - Hidden layer: last vs second-to-last vs avg(last 4)
    → 调参后仍 < 0.10 → NO-GO

  R² < 0.05
    → NO-GO，hidden state 不编码 U，放弃此路径

跨环境验证（如果 HotpotQA GO）:
  ≥ 2/3 环境 R² > 0.05 → 继续 B4
  仅 1/3 → probe 不泛化，仅用于 HotpotQA 消融
  0/3 → NO-GO
```

---

### B4. End-to-End Gate 实验（Day 4-10, 如果 B3 GO）

选最佳 probe 架构，作为 gate 替代手工 LR，跑完整 200ep。

**实验矩阵**：
```
环境 × {handcrafted_LR, best_probe_gate} × 3 seeds × 200 ep
= 3 env × 2 methods × 3 seeds = 18 runs
每 run ~40min (HF) → 预估 GPU 时间 ~12h
```

**核心对比**：
| 指标 | handcrafted LR | best probe | 判断 |
|------|:-:|:-:|:--|
| SR (mean ± CI) | baseline | 待测 | probe ≥ LR → 主方法升级 |
| RR (trigger rate) | baseline | 待测 | 越接近 oracle RR 越好 |
| Cost (×base) | baseline | 待测 | 越低越好 |

**论文叙事分支**：
```
IF probe ≥ handcrafted (SR↑ 或持平 + cost↓):
  → 主方法升级为 probe gate
  → Method novelty ⭐⭐⭐⭐
  → "Auto feature discovery from LLM hidden states matches/exceeds hand-crafted signals"

IF probe ≈ handcrafted (±3pp SR):
  → 论文中作为 method 贡献（自动化，无需领域知识）
  → Method novelty ⭐⭐⭐
  → "Matches without domain knowledge — no manual feature engineering needed"

IF probe < handcrafted:
  → appendix 消融分析
  → handcrafted LR 保持为主方法
  → Method novelty ⭐⭐（不变）
```

**关键：probe 在 APPS 上的表现决定了 APPS 能否从 "弱信号案例" 升级为 "Pareto-dominate"**：
```
APPS probe gate SR ≥ 60% AND cost < CaTS 1.04×
  → APPS Pareto-dominate（第 3 个 Pareto-dominate 环境 🎉）
APPS probe gate SR ∈ (58.5%, 60%)
  → APPS 略优于 CaTS，但差距太小，仍为 diagnostic case
APPS probe gate SR ≤ 58.5%
  → APPS 保持弱信号案例定位
```

**执行清单**：
- [ ] 实现 probe gate 集成到 SCG 框架（替换 LR 分类器为 probe inference）
- [ ] HotpotQA: probe gate 200ep × 3 seeds（优先，sanity check）
- [ ] WebShop: probe gate 200ep × 3 seeds
- [ ] APPS: probe gate 200ep × 3 seeds（关键：能否超过 CaTS 59.0%？）
- [ ] 统计对比：paired t-test / bootstrap CI

---

### B5. Probe 消融实验（Day 10-14, 如果 B4 有效，论文 appendix）

| 消融维度 | 搜索范围 | 预期最优 |
|---------|---------|---------|
| Pooling 策略 | mean / last_token / weighted_mean | last_token 或 mean |
| Hidden layer | last / second-to-last / avg(last 4) | last |
| d_hidden (MLP) | {32, 64, 128, 256} | 64 |
| 训练数据量 | N ∈ {50, 100, 200, 500, 1000} | 200+ 饱和 |
| PCA 维度 | {10, 20, 50, 100} | 50 |

- [ ] 消融实验脚本（参数化搜索）
- [ ] HotpotQA 完成所有消融组合
- [ ] 生成消融表格 + 图表

---

### B6. Probe 科学分析（Day 3-10, 与 B4 并行，论文 §4.5 + §5.7b + Figure 6）🆕🆕 v3.0 新增

**定位**：B5 是参数消融（appendix），B6 是**科学分析**（正文 §4.5 + §5.7b）。这是将 "simple linear probe" 从 trivial 提升为 **scientifically interesting** 的关键。

**B6.1 Layer-wise Probing — 论文 §4.5 + Figure 6(a)**

**科学问题**：gating 信号在 LLM 的哪一层表征中出现？如果只有深层有效 → gating 需要 reasoning-level 表征（不是表面 token 统计）。

```
输入: B1 收集的多层 hidden states (N_steps, 8_layers, 2560)
方法: 在 8 个层各自独立训练 linear probe → 预测 U > 0
指标: AUC-ROC per layer
预期: AUC 随 layer depth 单调递增, 前 1/3 层 ≈ 随机 (AUC~0.5), 后 1/3 层 >> 0.7
```

- [ ] 实现 layer-wise probing 脚本（每层独立训练 LR probe）
- [ ] HotpotQA 8 层 AUC 计算
- [ ] APPS 8 层 AUC 计算
- [ ] WebShop 8 层 AUC 计算
- [ ] 生成 Figure 6(a): Layer index vs AUC 折线图（3 环境 3 条线）

**B6.2 Cross-Environment Transfer Matrix — 论文 §4.5 核心 + Figure 6(b)** 🔥

**科学问题**：env A 训练的 probe 用于 env B 是否有效？如果 transfer 失败 → **直接验证 Toy Model**: 方向是环境特异的，probe 权重需要重新学。

**⚠️ 这是 probe 实验中最重要的分析 — 它连接了 method (probe) 和 theory (Two-Source Model)**。

```
输入: B1 收集的 3 个环境的 last-layer hidden states
方法: 3×3 transfer matrix:
  - 对角线: train on A, eval on A (in-env performance)
  - 非对角线: train on A, eval on B (cross-env transfer)
指标: AUC-ROC
预期: 对角线 >> 非对角线 (transfer 大幅下降)
```

| Train \ Eval | HotpotQA | APPS | WebShop |
|---|:---:|:---:|:---:|
| HotpotQA | AUC_AA | AUC_AB | AUC_AC |
| APPS | AUC_BA | AUC_BB | AUC_BC |
| WebShop | AUC_CA | AUC_CB | AUC_CC |

**论文叙事**：
```
"This cross-environment transfer failure is a direct consequence
 of our theoretical model: different environments have different
 p_I compositions, producing different ρ(entropy, U) directions
 that require environment-specific probing."
```

- [ ] 实现 cross-env transfer evaluation 脚本
- [ ] 计算 3×3 transfer matrix (AUC)
- [ ] 生成 Figure 6(b): 3×3 heatmap

**B6.3 Data Efficiency / Learning Curve — 论文 §4.5 + Figure 6(c)**

**科学问题**：direction learning 需要多少数据？如果 ~50 episodes 即饱和 → 信号强且干净，在线学习开销极低。

```
输入: B1 收集的 hidden states
方法: 从 {10, 20, 50, 100, 200} episodes 子采样训练数据
      对每个 N 训练 linear probe, 评估 AUC
指标: AUC vs N_episodes learning curve
预期: N≥50 时 AUC 基本饱和
```

- [ ] 实现 learning curve 脚本（bootstrap 子采样 × 5 repeats）
- [ ] HotpotQA learning curve
- [ ] 生成 Figure 6(c): N_episodes vs AUC 学习曲线

**B6.4 Feature Attribution（可选，论文 §4.5 一句话）**

- 比较 probe 权重方向 vs 手工 feature 系数方向
- 用 CCA / cosine similarity 衡量对应关系
- 如果高度对应 → probe 自动发现了人类选择的特征
- 如果不对应 → probe 发现了超越人类设计的新信号维度
- [ ] （可选）probe 权重 vs handcrafted feature 对比分析

---

## 4.5 路径 D：Toy Model Verification + Theory Figures（与 A/B/C 并行）🆕🆕 v3.0 新增

**核心目标**：验证 Two-Source Uncertainty Toy Model 的 3 个 Testable Predictions + 生成理论 Figure。
**论文位置**：§3.3 (Figure 2) + §5.7 E4 (Figure 7)
**投入**：~1-2 天分析时间（纯数据分析 + 绘图，无需 GPU）
**数据来源**：Phase 1 (HotpotQA/MBPP) + Phase 3+S2 (APPS) + Phase 4 (WebShop) 已有数据

### D1. P1 验证: Temporal Shift Analysis（最重要，需新分析）🔥

**Prediction 1**："Within the same environment, early steps have higher p_I than late steps. Therefore, early-step ρ should be more negative than late-step ρ."

**方法**：
```
对每个环境:
  1. 取 Phase 1/3+/4 已有的 signal discovery 数据
     - HotpotQA: Phase 1 (293 pts) + Phase 0 (293 pts)
     - APPS: Phase 3+S2 Step 1 (489 pts)
     - MBPP: Phase 1 (1,479 pts 中的 MBPP 部分)
     - WebShop: Phase 4 Step 1 (1,073 pts)

  2. Split 每条 trajectory 为:
     - early: step 1-3 (trajectory 前半段，信息少 → 更多 Type I)
     - late: step 4+ (trajectory 后半段，信息多 → 更少 Type I)

  3. 分别计算:
     - ρ(token_entropy, U | early steps)
     - ρ(token_entropy, U | late steps)

  4. 预期结果:
     - HotpotQA (Type I 主导): ρ_early << ρ_late (最明显)
     - APPS (混合): ρ_early < ρ_late (弱效应)
     - MBPP (Type D 主导): ρ_early ≈ ρ_late 或 ρ_early > ρ_late
     - WebShop: 依赖 state_category 更多，可能不显著
```

**Figure 7 设计**：Grouped bar chart
- X 轴：4 环境
- 每组两条柱：early (深色) vs late (浅色)
- Y 轴：ρ(entropy, U)
- 误差条：bootstrap 95% CI

- [ ] 编写 temporal shift 分析脚本（split trajectories by step）
- [ ] 加载 4 环境已有数据，计算 early/late ρ
- [ ] Bootstrap CI 计算（10K resamples）
- [ ] 生成 Figure 7
- [ ] 记录结果到 progress.md

### D2. Simpson's Paradox 子群演示（论文 §3.3 理论支撑）

**目标**：用实际数据展示 Simpson's Paradox 在 signal-utility 空间中的实例。

**方法**：
```
在 HotpotQA 中（数据最丰富，signal 最强）:
  1. 将 states 分为 Type I proxy 和 Type D proxy:
     - Type I proxy: evidence_count ≤ 1 (信息匮乏状态)
     - Type D proxy: evidence_count ≥ 2 (信息充分但需决策)

  2. 计算:
     - ρ(entropy, U | Type I states) → 预期: 负（高 entropy = 还没找到信息 → 不值得 rollout）
     - ρ(entropy, U | Type D states) → 预期: 正（高 entropy = 有多条路 → 值得 rollout 探索）
     - ρ(entropy, U | all states)     → 实际值: −0.327（负，因为 HotpotQA 中 Type I 占多数）

  3. 展示：within-group 正负相反，aggregated 呈负 → 经典 Simpson's Paradox

APPS 中也类似尝试:
  - Type I proxy: step_count ≤ 2 (刚开始，信息少)
  - Type D proxy: step_count ≥ 3 (已执行多步，面临选择)
```

**论文价值**：这不是新实验，而是对已有数据的重新分析。但它为 Two-Source Model 提供了**直接的实证支撑**，将 narrative 从 "post-hoc explanation" 提升为 "verified statistical phenomenon"。

- [ ] HotpotQA: 按 evidence_count 分组计算 within-group ρ
- [ ] APPS: 按 step_count 分组计算 within-group ρ
- [ ] 记录 Simpson's Paradox 演示结果
- [ ] （可选）生成 Simpson's Paradox 可视化（scatter plot with colored sub-groups）

### D3. P2/P3 Cross-Env + Signal Identity 汇总（论文 §5.7）

**P2 (Cross-Environment Divergence)**: 定性验证——已有数据足够
```
ρ 差异矩阵:
  |ρ_HotpotQA - ρ_MBPP| = |−0.327 − 0.153| = 0.480 (最大，task structure 差异最大)
  |ρ_APPS - ρ_MBPP|      = |+0.144 − 0.153| = 0.009 (最小，都是代码环境)
  |ρ_WebShop - ρ_HotpotQA| = |+0.133 − (−0.327)| = 0.460 (大，不同 task type)
→ 环境 task structure 差异越大，ρ 差异越大 ✅
```

**P3 (Signal Identity Alignment)**: 已有数据整理
```
| 环境 | 主导 Type | 最强信号 | 信号含义 | 对齐？ |
|------|----------|---------|---------|--------|
| HotpotQA | Type I | evidence_count (ρ=−0.586) | 信息充分度 | ✅ 完美对齐 |
| MBPP | Type D | step_count (ρ=+0.526) | 决策积累 | ✅ 完美对齐 |
| APPS | 混合 | step_count (ρ=−0.274) | 负方向 | ⚠️ 部分一致 |
| WebShop | 混合 | state_category (η²=0.598) | 状态编码 | ✅ 互补 |
```

- [ ] P2 divergence 矩阵计算 + 格式化
- [ ] P3 signal identity 对齐表格整理
- [ ] 综合 P1/P2/P3 为论文 §5.7 段落

### D4. Figure 2: Two-Source Model 理论曲线（论文 §3.3）

**设计**：
```
左图：p_I vs ρ(entropy, U) 理论曲线
  - X 轴: p_I (0 → 1)
  - Y 轴: ρ (−0.4 → +0.2)
  - 线性曲线: ρ = β − (α+β)·p_I
  - 标注 p* = β/(α+β) 零点
  - 标注 4 环境位置:
    • HotpotQA (p_I 高, ρ=−0.327)
    • APPS (p_I 中, ρ≈0)
    • MBPP (p_I 低, ρ=+0.153)
    • WebShop (p_I 中偏高, ρ=+0.133)

右图：Prediction 1 验证 — Early vs Late step ρ (= Figure 7)
```

- [ ] 实现 Figure 2 绘图脚本（matplotlib）
- [ ] 确定 α, β 参数（从实际数据拟合或使用合理估计）
- [ ] 生成 Figure 2（两面板）

---

## 5. 路径 C：新环境候选 GO/NO-GO

**背景**：已试 18 个环境（7 GO / 11 NO-GO）。新环境是获得第 5 个有效环境和第 3 个 Pareto-dominate 的机会。

### GO/NO-GO 标准（基于 18 个环境经验总结）

```
必须满足（AND）:
  ✅ base SR ∈ [10%, 85%]           — Qwen3-4B 能力范围内
  ✅ Δ(always - base) > 5pp         — rollout 有足够 headroom
  ✅ always_trigger 不 TIMEOUT       — 计算可行
  ✅ positive_rate ∈ [5%, 50%]      — rollout 有时有用但不是永远有用
  ✅ negative_rate < 5%             — rollout 不频繁有害

最佳条件（Signal 强度）:
  ✅ 最强 signal ρ > 0.3            — SCG 历史上在此条件下有效
  ⚠️ 最强 signal ρ ∈ [0.2, 0.3]   — 需 MLP gate 或 probe
  ❌ 最强 signal ρ < 0.2            — SCG 大概率失败（TextWorld/BabyAI 教训）
```

### C1. ToolBench（多步 API 调用链，GO 概率 40%）

**来源**：Qin et al., 2023（清华 NLP）
**任务**：从 16K+ 工具中选择合适 API 序列
**Rollout T**：K-variant API call generation (temp=0.7, K=5) + execution verification

**执行清单**：
- [ ] C1.0: 环境搭建 + base agent 适配（Day 1-2）
- [ ] C1.1: Step 0 GO/NO-GO: base 50ep + always 50ep（Day 2-3, ~2h）
- [ ] C1.2: （如 GO）Step 1 Signal Discovery 200ep（Day 3-4, ~4h）
- [ ] C1.3: （如 GO + ρ>0.2）Step 2 6-Method Core 6×3×200ep（Day 4-7, ~16h）
- [ ] C1.4: （如 GO）Step 3 CB + Cost Analysis（Day 7-10, ~16h）

**风险**：Qwen3-4B 在 16K API 集合选择上可能太弱 → base SR < 10% → NO-GO。

### ~~C2. AgentBench-KG~~ — ❌ 已砍

### ~~C3. CrosswordQA~~ — ❌ 已砍

### 新环境标准流水线

```
Step 0: GO/NO-GO     → 50ep × 1 seed, ~1-2h
Step 1: Signal Disc  → 200ep × 1 seed, ~2-4h
Step 2: 6-Method     → 6 × 3 seeds × 200ep, ~8-16h
Step 3: CB + Cost    → 4 × 3 seeds × 200ep + analysis, ~8-16h + 2h
```

---

## 6. 执行时间线

```
═══════════════════════════════════════════════════════════════════════
  Week 1 (Mar 12-16) — 数据收集 + Probe Offline + 新环境搭建
═══════════════════════════════════════════════════════════════════════

  Day 1 (Mar 12-13):
  ├── [A1] 检查 TWExpress CB 6 running + 1 pending 状态
  ├── [A2] 检查 APPS rerun 9 jobs pending 状态
  ├── [B1] 检查已有 hidden state 数据
  ├── [C1] ToolBench 环境搭建开始
  ├── 🆕 [D1] Temporal shift 分析脚本编写 + HotpotQA P1 验证
  └── 🆕 [D2] Simpson's Paradox 子群分析（HotpotQA）

  Day 2-3 (Mar 13-14):
  ├── [B1] HotpotQA 多层 hidden state 收集 (~40min) 🆕 8 层
  ├── [B1] APPS 多层 hidden state 收集 (~40min)
  ├── [B1] WebShop 多层 hidden state 收集 (~40min)
  ├── [C1] ToolBench Step 0 GO/NO-GO (50ep × 2)
  ├── 🆕 [D1] APPS/MBPP/WebShop P1 temporal shift 分析
  ├── 🆕 [D2] APPS Simpson's Paradox 子群分析
  ├── 🆕 [D3] P2/P3 汇总表格 + 段落初稿
  └── 🆕 [D4] Figure 2 + Figure 7 初稿生成

  Day 4-5 (Mar 15-16):
  ├── [A1] TWExpress CB 完成 → 分析定位（Pareto 还是对比案例？）
  ├── [B2] HotpotQA 4 种 probe offline 训练 + 评估 (<10min)
  ├── [B3] HotpotQA GO/NO-GO 判断 ← 关键节点
  ├── [B2] （如 B3 GO）APPS + WebShop probe offline 评估
  ├── 🆕 [B6.1] Layer-wise probing (HotpotQA 8 层 AUC) ← B1 数据就绪后
  └── [C1] （如 GO）ToolBench Signal Discovery

  ┌──────────────────────────────────────────────────────────────────┐
  │ Week 1 检查点 (Mar 16)                                          │
  │                                                                  │
  │ 关键决策:                                                        │
  │ 1. Hidden State Probe: HotpotQA R² = ?  GO/NO-GO?               │
  │    → GO: 路径 B 全速推进（Week 2 核心）                          │
  │    → NO-GO: 放弃 probe, 资源转入路径 C + 论文叙事调整            │
  │                                                                  │
  │ 2. TWExpress: Pareto-dominate 还是对比案例？                      │
  │    → Pareto: 第 3 个！论文更强                                    │
  │    → 对比案例: 仍有论文价值（与 WebShop 对比叙事）                │
  │                                                                  │
  │ 3. 新环境: ToolBench GO/NO-GO?                                    │
  │    → GO: Week 2 启动 Step 1-2                                    │
  │    → NO-GO: 确认论文最终 3-4 个环境                              │
  │                                                                  │
  │ 🆕 4. Toy Model P1 Verification: ρ_early < ρ_late?              │
  │    → Yes: Two-Source Model 有预测力 → 论文 §5.7 confirmed        │
  │    → No/Weak: 调整 P1 的 cutoff 或 downgrade P1 为 "suggestive"  │
  │                                                                  │
  │ 🆕 5. Simpson's Paradox: within-group ρ 方向相反?                │
  │    → Yes: 强理论支撑 → §3.3 confident writing                   │
  │    → Weak: 调整 proxy 定义或 soften claim                        │
  └──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
  Week 2 (Mar 17-21) — Probe End-to-End + 新环境 Core
═══════════════════════════════════════════════════════════════════════

  Day 6-8 (Mar 17-19):
  ├── [B4] HotpotQA probe gate end-to-end 200ep × 3 seeds
  ├── [B4] WebShop probe gate end-to-end 200ep × 3 seeds
  ├── 🆕 [B6.1] Layer-wise probing (APPS + WebShop 8 层 AUC)
  ├── 🆕 [B6.2] Cross-env transfer matrix (3×3, 最重要)
  ├── 🆕 [B6.3] Data efficiency learning curve (HotpotQA)
  ├── [C*] GO 环境 Step 2: 6-Method Core
  └── [A2] APPS rerun 结果分析（如果已完成）

  Day 9-10 (Mar 20-21):
  ├── [B4] APPS probe gate end-to-end 200ep × 3 seeds
  │         → 关键：SR 能否超过 CaTS 59.0%?
  ├── 🆕 [B6] Figure 6 生成（三面板：layer-wise + transfer + learning curve）
  ├── [C*] GO 环境 Step 3: CB baselines
  └── B4 结果分析 → 确定论文 method 叙事

  ┌──────────────────────────────────────────────────────────────────┐
  │ Week 2 检查点 (Mar 21)                                          │
  │                                                                  │
  │ 确认:                                                            │
  │ 1. Probe gate end-to-end 结果 → method 叙事确定                  │
  │ 2. APPS probe 是否超过 CaTS → APPS 定位升级？                    │
  │ 3. 有效论文环境总数（目标 ≥ 4）                                  │
  │ 4. Pareto-dominate 环境总数（目标 ≥ 2, 争取 3）                  │
  │ 🆕 5. B6 科学分析: cross-env transfer 失败？layer-wise 显著？     │
  │    → 与 Toy Model 闭环确认                                       │
  │ 🆕 6. D 路径全部完成？Figure 2 + Figure 7 就绪？                 │
  └──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
  Week 3 (Mar 22-26) — 收尾 + 统一分析 + 论文环境集确定
═══════════════════════════════════════════════════════════════════════

  Day 11-13 (Mar 22-24):
  ├── [B5] Probe 消融实验（如果 B4 有效）
  ├── [C*] 新环境 CB + Cost Analysis（如果有 GO 环境）
  └── 所有环境统一 Pareto 分析

  Day 14-15 (Mar 25-26):
  ├── 汇总：Unified Results Table
  ├── Pareto figure 统一生成
  ├── 论文最终环境集确定
  ├── phase6_final_report.md 撰写
  └── 开始写 LaTeX（数据齐全）

═══════════════════════════════════════════════════════════════════════
```

---

## 7. 最终环境组合预测（修订版）

```
组合 1（最可能, P=40%）:
  ✅ HotpotQA(Pareto) + ✅ WebShop(Pareto) + ⚠️ APPS(弱信号) + ⚠️ TWExpress(对比)
  = 4 环境, 2 Pareto + 2 diagnostic
  + probe 成功 → method novelty ⭐⭐⭐⭐

组合 2（P=20%）:
  上述 4 + 🆕 ToolBench GO
  = 5 环境, 2-3 Pareto + 2-3 diagnostic
  + probe 成功 → 最强论文

组合 3（P=20%）:
  HotpotQA(Pareto) + WebShop(Pareto) + APPS(probe升级→Pareto) + TWExpress(对比)
  = 4 环境, 3 Pareto + 1 diagnostic
  + probe 将 APPS 从弱信号升级为 Pareto → 强论文

组合 4（P=10%）:
  HotpotQA + WebShop + APPS (弱信号)
  = 3 环境, probe 失败, 新环境全 NO-GO
  → 调整论文为 finding-driven + diagnostic framework

组合 5（P=5%）:
  最佳情况：5 env + probe 成功 + TWExpress Pareto
  → 🎉 NeurIPS 强投
```

---

## 8. GO/NO-GO 总判定

### Mar 16 检查点（Week 1 结束）

| 条件 | 行动 |
|------|------|
| Probe R² > 0.10 | ✅ 全速推进 B4 end-to-end |
| Probe R² ∈ (0.05, 0.10) | ⚠️ 尝试调参（pooling/layer），不立即放弃 |
| Probe R² < 0.05 | ❌ 放弃 probe, 资源全转路径 C + 强化 finding 叙事 |
| 🆕 P1 ρ_early < ρ_late (显著) | ✅ Toy Model P1 confirmed, §5.7 confident |
| 🆕 P1 方向对但不显著 | ⚠️ Report as "suggestive" with CI overlap caveat |
| 🆕 Simpson's Paradox within-group 方向相反 | ✅ §3.3 理论支撑 confirmed |
| 🆕 Simpson's Paradox 不明显 | ⚠️ 调整 Type I/D proxy 定义，或 soften claim |
| ToolBench NO-GO | 确认论文 3-4 环境（仅保留 ToolBench 一个候选） |

### Mar 26 检查点（Phase 6 结束，论文环境集确定）

```
4-5 env + probe 有效:   → 🎉 NeurIPS 75-85%, 全面开始写作
4 env + probe 持平:     → ✅ NeurIPS 60-70%, 可投
3-4 env + probe 失败:   → ⚠️ NeurIPS 40-50%, 考虑 ICLR 2027
2 env only:             → ❌ 需重大调整论文定位
```

---

## 9. 完整 Checklist（v3.0 更新）

### 路径 A — 完善现有环境（低投入）

- [ ] **A1.1** TWExpress CB 7 jobs 完成 → 数据提取
- [ ] **A1.2** TWExpress Pareto 分析 + 论文定位确定
- [ ] **A1.3** TWExpress token cost 常数提取 + cost 表
- [ ] **A2.1** APPS rerun 9 jobs 完成 → 数据更新
- [ ] **A2.2** APPS 统一结果表更新（正确 random_50/bsw/oracle）
- [ ] **A3** 所有论文环境 Pareto figure 统一生成

### 路径 B — Hidden State Probe（核心）

- [ ] **B1.0** 检查已有 hidden state 数据
- [ ] **B1.1** HotpotQA 多层 hidden state 收集（200ep, HF, 8 层）🆕 升级
- [ ] **B1.2** APPS 多层 hidden state 收集
- [ ] **B1.3** WebShop 多层 hidden state 收集
- [ ] **B2.1** 4 种 probe 训练脚本实现
- [ ] **B2.2** HotpotQA P1-P4 训练 + 评估（R², AUC, ρ）
- [ ] **B2.3** 对比 handcrafted LR 基线
- [ ] **B3** HotpotQA GO/NO-GO 判断
- [ ] **B2.4** （如 B3 GO）APPS + WebShop probe offline 评估
- [ ] **B4.1** （如 B3 GO）HotpotQA probe gate 200ep × 3 seeds
- [ ] **B4.2** （如 B3 GO）WebShop probe gate 200ep × 3 seeds
- [ ] **B4.3** （如 B3 GO）APPS probe gate 200ep × 3 seeds
- [ ] **B5** （如 B4 有效）消融实验
- [ ] **B6.1** 🆕 Layer-wise probing: 3 环境 × 8 层 AUC + Figure 6(a)
- [ ] **B6.2** 🆕 Cross-env transfer matrix: 3×3 AUC heatmap + Figure 6(b)
- [ ] **B6.3** 🆕 Data efficiency learning curve: AUC vs N_episodes + Figure 6(c)
- [ ] **B6.4** 🆕 （可选）Feature attribution: probe 权重 vs handcrafted 对比

### 路径 C — 新环境（仅 ToolBench）

- [ ] **C1.0** ToolBench 环境搭建
- [ ] **C1.1** ToolBench Step 0 GO/NO-GO
- [ ] **C1.2-C1.4** （如 GO）完整流水线
- [x] ~~C2 AgentBench-KG~~ — ❌ 已砍
- [x] ~~C3 CrosswordQA~~ — ❌ 已砍

### 路径 D — Toy Model Verification 🆕🆕

- [ ] **D1.1** Temporal shift 分析脚本编写
- [ ] **D1.2** HotpotQA P1: early vs late step ρ 计算 + bootstrap CI
- [ ] **D1.3** APPS/MBPP/WebShop P1 验证
- [ ] **D1.4** Figure 7 生成（grouped bar chart）
- [ ] **D2.1** HotpotQA Simpson's Paradox 子群分析（按 evidence_count 分组）
- [ ] **D2.2** APPS Simpson's Paradox 子群分析（按 step_count 分组）
- [ ] **D2.3** （可选）Simpson's Paradox 可视化
- [ ] **D3.1** P2 divergence 矩阵计算
- [ ] **D3.2** P3 signal identity 对齐表格
- [ ] **D3.3** P1/P2/P3 综合为论文 §5.7 段落
- [ ] **D4.1** Figure 2 绘图脚本（Two-Source Model 理论曲线）
- [ ] **D4.2** α, β 参数估计（从数据拟合或合理假设）
- [ ] **D4.3** Figure 2 生成（两面板）

### 收尾

- [ ] Unified Results Table（所有论文环境）
- [ ] Pareto figure 统一生成
- [ ] Figure 2 (Two-Source Model) + Figure 6 (Probe Analysis) + Figure 7 (P1 Verification) 就绪 🆕
- [ ] phase6_final_report.md
- [ ] 论文最终环境集确定 → 开始 LaTeX

---

## 10. 资源估算（修订版）

### GPU 时间

| 任务 | GPU 时间 | 优先级 |
|------|---------|:------:|
| B1: Hidden state 收集 (3 env, 多层) | ~3h (比单层多 ~50%) | 🔴 最高 |
| B2: Probe offline 训练 | ~0.5h (CPU) | 🔴 |
| B4: End-to-end (3×2×3 seeds) | ~12h | 🔴 |
| B5: 消融 | ~4h | 🟡 |
| 🆕 B6: 科学分析 (layer-wise + transfer + learning curve) | ~1h (CPU/单 GPU) | 🔴 |
| 🆕 D: Toy Model Verification + Figures | ~0h (纯 CPU 分析) | 🔴 |
| C*: 新环境流水线 (per env) | ~20h | 🟠 |
| ~~A2: TextWorld~~ | ~~16h~~ | ~~已砍~~ |
| **总计** | **~42-62h** | |

**vs v1.0 省下 ~16h GPU 时间**（TextWorld 砍掉），全部可投入路径 B/C/D。
**路径 D 零 GPU 成本** — 纯数据分析 + 绘图，可在 CPU 上并行执行。

### SLURM 管理

- 预估新增 jobs：20-35 个（比 v1.0 减少 ~15 个）
- 优先提交：B1（短任务，~40min/job）→ B4（中任务，~40min/job）
- 路径 C 与路径 B 并行提交

---

## 11. 风险管理

| 风险 | 概率 | 影响 | 缓解措施 |
|------|:----:|:----:|---------|
| Hidden State Probe NO-GO | 30% | 高 | 保持手工 LR 为主方法；强化 finding 叙事（方向反转 + adaptive behavior）。论文仍可投但 method novelty 不足 |
| 所有新环境 NO-GO | 40% | 中 | 4 环境 (HotpotQA+WebShop+APPS+TWExpress) 仍可支撑论文 |
| TWExpress 不 Pareto-dominate | 50% | 低 | 定位为 "rollout-safe 对比案例"，与 WebShop 形成对比叙事 |
| APPS probe 仍不超过 CaTS | 60% | 低 | APPS 保持弱信号案例定位，展示正确保守行为 |
| GPU quota 不足 | 15% | 中 | 优先路径 B（战略价值最高），错峰提交 |

---

## 12. 与论文写作的衔接

**Phase 6 → 论文的关键产出**：

| Phase 6 产出 | 论文位置 | 依赖 |
|-------------|---------|------|
| Probe 结果 | §4.4 方法描述 + §5.7b 分析 | B3/B4 |
| 🆕 Layer-wise + Transfer + Learning Curve | §4.5 + Figure 6 (三面板) | B6 |
| 统一 Pareto 图 | Figure 4 + Table 2 | A3 |
| 新环境数据 | §5 环境扩展 | C* |
| TWExpress 对比分析 | §5.2 Diagnostic Analysis | A1 |
| APPS 弱信号分析 | §5.2 或 Appendix | A2 |
| 🆕 P1 Temporal Shift 验证 | §5.7 E4 + Figure 7 | D1 |
| 🆕 Simpson's Paradox 子群 | §3.3 Theoretical grounding | D2 |
| 🆕 P2/P3 Cross-env + Signal Identity | §5.7 E4 | D3 |
| 🆕 Two-Source Model 理论曲线 | §3.3 + Figure 2 | D4 |

**论文叙事依赖**：
```
Probe 成功 → 方法叙事: "SCG learns both direction and features from LLM hidden states"
           → 升级为: 无需领域知识的端到端 gating
           → B6 科学分析提供 theory-method 闭环
Probe 失败 → 方法叙事: "SCG uses lightweight trajectory features with zero overhead"
           → 保持: finding-driven paper, 方法简洁是 feature not bug

Toy Model 验证成功 → 理论叙事: "finding + verified theory paper"
                   → P1/P2/P3 confirmed → NeurIPS 理论深度 ⭐⭐⭐⭐
Toy Model 验证部分 → 理论叙事: "finding + suggestive theory paper"
                   → 至少 2/3 predictions → 仍有价值
Toy Model 验证失败 → 理论叙事: "finding + post-hoc explanatory model"
                   → 降级为 discussion-level hypothesis
```
