# Phase 6 执行计划：目标 5 个有效环境 + Method Novelty 升级

**版本**：v4.1（2026-03-14）— 路径 A/D ✅ 完成, 路径 C ❌ 全 NO-GO, 路径 B Probe gate ❌ 失败 (hidden_state bug + 分布偏移), **路径 E ✅ 完成: E3:principled 最佳 (HotpotQA -0.1pp, APPS +7.4pp, WebShop -1.0pp vs SCG)**
**前置依赖**：Phase 0-5 完成，当前 2 个确认 Pareto-dominate（HotpotQA + WebShop）
**核心目标**：~~从 2 → 4-5 个有效论文环境~~ 论文 4 环境已锁定 + 提升 Method Novelty（⭐⭐ → ⭐⭐⭐⭐） + ~~完成 Toy Model 实验验证~~ ✅ 已完成
**v4.0 新增**：路径 E — 三个 Method Upgrade 方向（E1 Contextual Bandit / E2 Contrastive Probe / E3 Principled SCG），目标解决两个结构性问题：(1) 没有好的 method, (2) 可行环境太少
**计划周期**：2026-03-12 至 2026-03-26（3 周）
**论文标题**：Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments

---

## 1. 当前状态总结（基于 Phase 5 环境报告 2026-03-12）

### 1.1 7 环境最终定性

| 环境 | Paper 定位 | 数据完整度 | 关键数据 |
|------|-----------|-----------|---------|
| **HotpotQA** | ✅ **主实验** | ✅ 全部完成 | SCG 0.968@6.55× Pareto-dominate CaTS 0.932@10.55× |
| **WebShop** | ✅ **主实验** | ✅ 全部完成 | SCG 0.437@1.27× Pareto-dominate CaTS 0.305@3.44× |
| **APPS** | ⚠️ **弱信号案例** | ✅ 全部完成 (rerun 9/9 done) | SCG 0.588/1.23× vs CaTS 0.590/1.04×, 弱信号(ρ=−0.155), oracle=75.0% |
| **TWExpress** | ⚠️ **对比案例** | ✅ 全部完成 (CB 12/12 done) | rollout 永远无害, SCG 选择性反而是劣势, token cost 已提取 |
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
| **新环境扩展** | 额外多样性 + 可能的第 3 个 Pareto-dominate | 1-2（C1-C4, 并行 Step 0 取最先 GO） |

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
  路径 C：新环境候选 (3-4个)     B5: 消融实验
  ──────────────────────        B6: 科学分析 🆕
  C1: ToolBench G2/G3 (35%)      → B6.1 Layer-wise probing
  C2: ALFWorld (55%) 🆕           → B6.2 Cross-env transfer
  C3: ScienceWorld (45%) 🆕       → B6.3 Data efficiency
  C4: InterCode-SQL (40%) 🆕
═══════════════════════════════════════════════════════════════════════════
```

**优先级排序（v3.2 修订）**：
1. **路径 B（最高，唯一剩余高影响力路径）**：Hidden State Probe 是 NeurIPS 接受概率从 40% → 75% 的关键。路径 A/D 已完成，路径 C 全 NO-GO，B 是唯一杠杆。
2. ~~**路径 D（高，与 B 并行）**~~ → ✅ **已完成**（Day 2 全部完成，P1/P2/P3 confirmed, Figure 2 + Figure 7 已生成）
3. ~~**路径 A（中等，低投入）**~~ → ✅ **已完成**（TWExpress CB 12/12, APPS rerun 9/9, 全部 token cost 已提取）
4. ~~**路径 C（补充，4 候选取 1-2）**~~ → ❌ **全部 NO-GO**（ToolBench G1/MirrorAPI, ALFWorld, ScienceWorld, InterCode 全部 NO-GO）

**依赖关系（简化后）**：
- B4 依赖 B3 GO
- B6 依赖 B1 数据（但 B6.1/B6.2/B6.3 与 B4 可并行）
- A3 (统一 Pareto figure) 等 B4 结果后一起生成

---

## 3. 路径 A：完善现有环境数据（低投入）

### A1. TWExpress — ✅ 全部完成

**结果**：
- CB 12/12 全部完成（SLURM jobs 23089034-23089057）
- Token cost: C_base=524, C_rollout=8,002, C_vote=2,620
- **定位确定：对比案例**（rollout-safe, 所有方法 ~97%, SCG cost 最低但 SR 不 dominate）

**Step A1.1：✅ CB 完成**
- [x] 检查 TWExpress CB running/pending 状态（6 running + 1 pending）
- [x] 等 SEAG×3 + CoRefine×3 + CATTS-456 完成
- [x] 预计数小时至 1-2 天内完成

**Step A1.2：✅ 分析 + 定位完成**
- [x] 提取所有 CB 的 {SR, ro/ep} 数据
- [x] 计算 token cost（需提取 C_base, C_rollout 常数）
- [x] Pareto 分析：SCG cost ≈ CB cost, SR ≈ CB SR → ⚠️ 无优势，定位为 diagnostic 对比案例
- [x] 确定论文定位：**"rollout-safe 对比案例"**

**TWExpress 论文叙事（大概率定位为对比案例）**：
> TWExpress 与 WebShop 形成精确对比：
> - WebShop：过度 rollout 有害（random_50 47.5% > always 43.0%）→ SCG 选择性是优势
> - TWExpress：rollout 永远无害（utility 从不为负）→ SCG 选择性反而限制了 SR
>
> 两个环境共同说明：SCG 确实学会了信号方向，但最优策略取决于环境的 rollout harm profile。

---

### A2. APPS — ✅ 全部完成

**结果**：
- Rerun 9/9 全部完成（random_50×3, bsw×3, oracle×3）
- **重大发现：oracle=75.0%!** >> always(64.5%) >> SCG(58.8%)
- r50(66.8%) > always(64.5%) → 选择性触发有价值
- bsw(58.5%) = base_only → 正确实现后 bsw 触发率=0%

- [x] 等 APPS rerun 9 jobs 完成（random_50×3, bsw×3, oracle×3）
- [x] 更新 APPS 统一结果表
- [x] 确认正确的 oracle SR → **75.0%**（远高于预估的 66.8%）
- [x] APPS 论文叙事确定：弱信号环境，oracle gap=16.2pp 证明 rollout 信号存在但 handcrafted feature 抓不到 → **Hidden State Probe 最强动机环境**

---

### A3. Cost Analysis 统一计算 — ⚠️ 部分完成

- [x] TWExpress token cost 常数提取 → C_base=524, C_rollout=8002, C_vote=2620
- [x] BabyAI token cost 常数提取 → C_base=336, C_rollout=2173, C_vote=1681
- [x] Plancraft token cost 常数提取 → C_base=1120, C_rollout=10651, C_vote=5598
- [x] 全部 6 环境 token cost 完成
- [ ] 所有论文环境统一 Pareto 图生成（等 B4 结果后一起生成）
- [x] 更新 phase5_environment_report.md

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

## 5. 路径 C：新环境候选 GO/NO-GO — ❌ 全部 NO-GO

**背景**：已试 16 个环境（5 GO / 11 NO-GO）。

**v3.2 更新 (2026-03-13)：** 所有 4 个候选环境均已确认 NO-GO。关键发现：ALFWorld、ScienceWorld、InterCode 在 Phase 5 Wave 2 (2026-03-07) 已测试过且全部失败，Phase 6 执行计划 v3.1 编写时未考虑到这些历史数据。ToolBench G1/MirrorAPI 今日确认 NO-GO。**路径 C 终止，论文环境集锁定为 4 个。**

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

### C1. ToolBench G2/G3（多工具链式调用）— ❌ G1 NO-GO, G2/G3 搁置

**来源**：Qin et al., 2023（清华 NLP）/ StableToolBench
**G1 结果**：❌ NO-GO — base SR=94% (无 MirrorAPI), 98% (有 MirrorAPI), Δ=0%
**MirrorAPI 部署**：✅ 已完成但不改变结论（tool selection 本身太简单）
**G2/G3 搁置**：需 G2/G3 instruction 数据且 Qwen3-4B 在多工具任务上可能太弱 (base SR < 10%)，ROI 不足

**G1 vs G2/G3 难度对比**：
| 级别 | 任务类型 | 工具数 | 链长 | 预期 base SR | 难度来源 |
|------|---------|:------:|:----:|:------------:|---------|
| G1 ❌ | 单工具内 API 调用 | 1 | 1-2 | ~98% (已验证) | 仅 tool selection |
| **G2** | 同类别内多工具调用 | 2-3 | 3-5 | 30-60% (预估) | 需选正确工具 + 链式调用 |
| **G3** | 跨类别多工具调用 | 3-5 | 4-8 | 10-40% (预估) | 最难：跨域 reasoning + 长链 |

**已有基础设施**：
- ✅ MirrorAPI 服务器 (`run_mirror.py`) 已部署可用
- ✅ ToolEnv2404 工具数据 (12,304 JSON, 49 类别)
- ✅ MirrorAPI 专用模型 (Qwen2-7B) 已下载
- ✅ ToolBenchEnv adapter 已实现 (支持 /virtual 端点)
- ⚠️ 需下载 G2/G3 instruction 数据 (`solvable_queries/test_instruction/G2_*.json`, `G3_*.json`)

**执行清单**：
- [ ] C1.0: 下载 G2/G3 任务数据 + 更新 config (task_file 切换)
- [ ] C1.1: G2 Step 0 GO/NO-GO: base 50ep + always 50ep (~2-3h, 含 MirrorAPI)
- [ ] C1.2: (如 G2 NO-GO) G3 Step 0 GO/NO-GO
- [ ] C1.3: (如 GO) Step 1 Signal Discovery 200ep
- [ ] C1.4: (如 GO + ρ>0.2) Step 2-3 完整流水线

**风险/机会**：
- 风险：G2/G3 每步需 MirrorAPI LLM 调用 (~5s/step)，速度慢 → 可能 TIMEOUT
- 风险：多工具任务 Qwen3-4B 可能太弱 → base SR < 10%
- 机会：多工具链式调用是 rollout 最有价值的场景（选错工具后回退 → 高 rollout utility）
- 机会：已有完整 MirrorAPI 基础设施，搭建成本几乎为零

### C2. ALFWorld（文本家庭任务）— ❌ NO-GO (Phase 5 已测试)

**来源**：Shridhar et al., 2021（Allen AI）
**Phase 5 Wave 2 测试结果 (2026-03-07)**：base SR=28%, always SR=30%, **Δ=+2%** → NO-GO (Δ < 3% 阈值)
**失败原因**：Rollout 几乎无帮助，base→always 仅提升 2pp，远低于 GO 阈值

~~**执行清单**~~ — 已在 Phase 5 完成，无需重做：
- [x] C2.0: 环境搭建 + BaseEnv adapter → ✅ Phase 5 已完成
- [x] C2.1: Step 0 GO/NO-GO → ❌ **NO-GO** (Δ=2% < 3%)

### C3. ScienceWorld（文本科学实验）— ❌ NO-GO (Phase 5 已测试)

**来源**：Wang et al., 2022（Allen AI）
**Phase 5 Wave 2 测试结果 (2026-03-07)**：base SR=0%, always SR=0%, **Δ=0%** → NO-GO
**失败原因**：Qwen3-4B 完全无法完成任何科学实验任务，base 和 always 均 0%

~~**执行清单**~~ — 已在 Phase 5 完成，无需重做：
- [x] C3.0: 环境搭建 + BaseEnv adapter → ✅ Phase 5 已完成
- [x] C3.1: Step 0 GO/NO-GO → ❌ **NO-GO** (base=0%, model 完全失败)

### C4. InterCode — ❌ NO-GO (Phase 5 已测试 bash 版本)

**来源**：Yang et al., 2024（Princeton）
**Phase 5 Wave 2 测试结果 (2026-03-07, InterCode-bash)**：base SR=100%, always SR=100%, **Δ=0%** → NO-GO (太简单)
**注**：测试的是 bash 版本而非 SQL 版本。但考虑到 bash 已 100% 且 SQL 需 Docker 支持，投入 SQL 版本的 ROI 极低。

~~**执行清单**~~ — bash 版本已在 Phase 5 完成：
- [x] C4.0: InterCode-bash 环境搭建 → ✅ Phase 5 已完成
- [x] C4.1: Step 0 GO/NO-GO → ❌ **NO-GO** (base=100%, 已完美)

### 新环境汇总 — 全部 NO-GO

| 候选 | 测试日期 | Base SR | Always SR | Δ | 结果 |
|------|:--------:|:-------:|:---------:|:-:|:----:|
| C1 ToolBench G1 | 3/13 | 94-98% | 94-98% | 0% | ❌ 太简单 |
| C2 ALFWorld | 3/7 | 28% | 30% | +2% | ❌ Δ不足 |
| C3 ScienceWorld | 3/7 | 0% | 0% | 0% | ❌ 模型太弱 |
| C4 InterCode-bash | 3/7 | 100% | 100% | 0% | ❌ 太简单 |
| ~~AgentBench-KG~~ | — | — | — | — | ❌ 已砍 |
| ~~CrosswordQA~~ | — | — | — | — | ❌ 已砍 |

**结论**：路径 C 终止。16 个已测试环境中仅 5 个 GO，已覆盖主流 agent benchmarks。论文环境集锁定为 4 个（HotpotQA + WebShop + APPS + TWExpress）。

---

## 5.5 路径 E：Method Upgrade — 三个新方法方向 🆕🆕 v4.0 新增

### 背景与动机

**Phase 6 暴露的两个结构性问题**：

1. **没有好的 method**：当前 SCG = 手工 5 feature + LR，这是 baseline 不是 method。Probe (路径 B) offline AUC 高但 end-to-end threshold 校准连续 3 轮失败（B4v1: threshold 太低 → always_trigger；B4v2: 在线校准数据不足；B4v3: running 中但趋势不乐观）
2. **可行环境太少**：仅 2 个 Pareto-dominate（HotpotQA + WebShop），18 个环境 11 个 NO-GO。一个更强的 method 可能让 APPS 从 "弱信号 diagnostic" 升级为 Pareto-dominate

**瓶颈诊断**：
```
✅ Ranking 能力已足够好: Probe AUC 0.88-1.00, Handcrafted AUC 0.98-1.00
❌ Threshold 校准是核心瓶颈: B4v1/v2/v3 连续失败
❌ 方法过于简单: "手工 feature + LR" 无法撑起 NeurIPS method section
❌ 无自动化: 每个环境需要人工挑选 feature，不 scalable
```

**三条路线定位**：

| 路线 | 目标瓶颈 | 核心思路 | Novelty | 推荐度 |
|------|---------|---------|:-------:|:------:|
| **E1: Contextual Bandit** | ❌ Threshold 校准 | Thompson sampling 自动平衡 explore/exploit，无需显式 threshold | ⭐⭐⭐⭐ | 🔴 最推荐 |
| **E2: Contrastive Probe** | ✅ Ranking → 更好的 score 分布 | Contrastive learning 产生 bimodal score，简化 threshold | ⭐⭐⭐ | 🟡 补充 |
| **E3: Principled SCG** | ❌ 方法过简 + 无自动化 | LASSO auto feature selection + CMDP 最优 threshold | ⭐⭐⭐ | 🟠 E1 的补充 |

**数据基础**：路径 E 复用 B1 已收集的 hidden state 数据 + Phase 1-4 所有 signal discovery 数据。无需额外数据收集。

---

### E1. Cost-Aware Contextual Bandit Gate (CACB) — 🔴 最高优先

#### E1.1 问题建模

将 step-level gating 建模为 **contextual bandit with partial feedback**：

```
Contextual Bandit 定义:
  - Context space X: state feature 向量 x ∈ R^d
  - Action space A = {0: skip, 1: trigger rollout}
  - Reward:
      R(x, a=1) = U(x) - λ · C_ratio     (触发: 获得 utility 减去 cost)
      R(x, a=0) = 0                        (不触发: 零收益)
  - 目标: 最大化 cumulative reward Σ_t R(x_t, a_t)

  其中:
    U(x) = rollout utility (只有触发时才能观测)
    λ = cost penalty (CMDP λ* 或 C_rollout/C_base)
    C_ratio = normalized rollout cost

与当前 SCG 的关键区别:
  SCG:     explore 50ep → 一次性拟合 LR → 固定 exploit
  CACB:    每步 Thompson sampling → posterior 持续更新 → 无硬分界
```

#### E1.2 核心算法：Bayesian Logistic Regression + Thompson Sampling

```python
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import cho_factor, cho_solve

class CACBGate:
    """Cost-Aware Contextual Bandit Gate with Thompson Sampling."""

    def __init__(self, d, lambda_cost, prior_var=1.0,
                 warmup_episodes=10, update_freq='episode'):
        """
        Args:
            d: feature 维度
            lambda_cost: CMDP cost ratio (C_rollout / C_base)
            prior_var: 先验方差 σ²_0
            warmup_episodes: 纯探索阶段（全部触发，收集初始数据）
            update_freq: posterior 更新频率 ('step' 或 'episode')
        """
        self.d = d
        self.lambda_cost = lambda_cost
        self.prior_var = prior_var
        self.warmup_episodes = warmup_episodes
        self.update_freq = update_freq

        # Bayesian LR posterior: P(w|D) ≈ N(w_map, Σ)
        self.w_map = np.zeros(d)                    # MAP estimate
        self.Sigma = prior_var * np.eye(d)          # posterior covariance
        self.Sigma_inv = (1/prior_var) * np.eye(d)  # precision matrix

        # 数据缓冲
        self.X_buffer = []      # features
        self.U_buffer = []      # observed utilities (only for triggered steps)
        self.A_buffer = []      # actions taken

        # 统计
        self.episode_count = 0
        self.total_triggers = 0
        self.total_steps = 0

    def extract_features(self, state, hidden_state=None):
        """
        Feature extraction — 三种模式:

        Mode A (handcrafted only): x = [5 handcrafted signals]
            → 直接对比现有 SCG，最快验证 CACB 框架

        Mode B (hidden state PCA): x = PCA(hidden_state, k=50)
            → 自动 feature，对比 Probe gate

        Mode C (hybrid): x = concat([5 handcrafted, PCA(h, k=20)])
            → 最强配置，handcrafted 提供 strong prior + PCA 补充
        """
        # 实现时根据 mode 选择
        pass

    def decide(self, x_t):
        """
        Thompson Sampling 决策:
        1. 从 posterior 采样 w̃ ~ N(w_map, Σ)
        2. 计算 predicted utility: û = w̃ · x_t
        3. 计算 net value: v = û - λ · C_ratio
        4. 触发条件: v > 0  ↔  û > λ · C_ratio
        """
        self.total_steps += 1

        # Warmup: 全部触发（收集无偏 U 数据）
        if self.episode_count < self.warmup_episodes:
            return True, {'phase': 'warmup'}

        # Thompson Sampling
        w_sample = np.random.multivariate_normal(self.w_map, self.Sigma)
        u_pred = w_sample @ x_t                         # predicted utility
        net_value = u_pred - self.lambda_cost            # cost-adjusted
        trigger = (net_value > 0)

        # 也可以用 sigmoid 做 soft decision:
        # p_trigger = sigmoid(w_sample @ x_t - log(lambda_cost))
        # trigger = (np.random.random() < p_trigger)

        return trigger, {
            'phase': 'thompson',
            'u_pred': u_pred,
            'net_value': net_value,
            'w_norm': np.linalg.norm(w_sample),
            'posterior_std': np.sqrt(np.diag(self.Sigma).mean())
        }

    def observe(self, x_t, action, utility=None):
        """
        观测 rollout 结果并更新 posterior。

        关键: 只有 action=1 (triggered) 时才能观测到 utility。
        action=0 时 utility 是 counterfactual，不可观测。

        处理策略:
          - Option A (推荐): 只用 triggered steps 更新 posterior
            → 无偏但数据少
          - Option B: 假设 skip 时 utility=0
            → 有偏但数据多
          - Option C: IPS (Inverse Propensity Scoring) 加权
            → 无偏但方差大
        """
        self.X_buffer.append(x_t)
        self.A_buffer.append(action)

        if action == 1 and utility is not None:
            self.U_buffer.append((x_t, utility))
            self.total_triggers += 1

    def update_posterior(self):
        """
        Laplace Approximation 更新 posterior。

        目标: 拟合 P(U > 0 | x) = σ(w · x)

        Prior:     P(w) = N(0, σ²_0 · I)
        Likelihood: Π_i σ(w·x_i)^{y_i} · (1-σ(w·x_i))^{1-y_i}

        MAP:  w_map = argmax [log likelihood + log prior]
        Σ = (-∇² log P(w|D))^{-1} |_{w=w_map}  (Hessian 的逆)
        """
        if len(self.U_buffer) < 5:  # 数据太少，不更新
            return

        X = np.array([xu[0] for xu in self.U_buffer])  # (N, d)
        U = np.array([xu[1] for xu in self.U_buffer])   # (N,)
        y = (U > 0).astype(float)                        # binary labels

        N = len(y)
        prior_precision = (1/self.prior_var) * np.eye(self.d)

        # Newton's method for MAP
        w = self.w_map.copy()
        for _ in range(20):  # max 20 Newton steps
            p = 1 / (1 + np.exp(-X @ w))           # sigmoid predictions
            p = np.clip(p, 1e-8, 1-1e-8)

            grad = X.T @ (y - p) - prior_precision @ w
            S = p * (1 - p)                          # diagonal of Hessian weight
            H = -(X.T * S) @ X - prior_precision     # Hessian

            try:
                step = np.linalg.solve(H, grad)
                w = w - step
            except np.linalg.LinAlgError:
                break

            if np.linalg.norm(step) < 1e-6:
                break

        self.w_map = w

        # Posterior covariance = inverse of negative Hessian at MAP
        p = 1 / (1 + np.exp(-X @ self.w_map))
        p = np.clip(p, 1e-8, 1-1e-8)
        S = p * (1 - p)
        self.Sigma_inv = (X.T * S) @ X + prior_precision

        try:
            self.Sigma = np.linalg.inv(self.Sigma_inv)
        except np.linalg.LinAlgError:
            self.Sigma = self.prior_var * np.eye(self.d)

    def on_episode_end(self):
        """每个 episode 结束时更新 posterior（如果 update_freq='episode'）"""
        self.episode_count += 1
        if self.update_freq == 'episode':
            self.update_posterior()
```

#### E1.3 与 VOC/CMDP 的理论连接

```
Thompson Sampling ≈ 在线 VOC 估计:

  VOC(T, s) = E[R(with_rollout) | s] - E[R(without_rollout) | s] - Cost(T)
            = E[U | x(s)] - λ

  CACB trigger condition: û_t > λ
  ↔ VOC(T, s_t) > 0 的采样近似（û_t 是从 posterior 采的 U 估计）

  Posterior uncertainty → 自然 exploration:
  - 不确定时 û_t 方差大 → 有时 û_t > λ 有时不是 → 自动探索
  - 确定时 û_t 集中在 E[U|x] 附近 → 稳定 exploit

  Regret bound (标准 Bayesian LR + Thompson Sampling):
    Regret(T) = O(d · √T · log T)
  其中 d = feature 维度, T = total steps
```

#### E1.4 三种 Feature Mode 的实验设计

```
Mode A: Handcrafted Only (d=5)
  x = [token_entropy, step_count, evidence_count/state_category, ...]
  目的: 直接对比现有 SCG-LR, 验证 CACB 框架本身的价值
  预期: 消除 threshold 校准问题 → APPS 可能从 58.8% 提升到 60%+
  GPU 时间: 3 env × 3 seeds × 200ep × ~40min = ~18h

Mode B: Hidden State PCA (d=50)
  x = PCA(hidden_state_last_layer, n_components=50)
  目的: 对比 B4 Probe gate, 验证 CACB 是否解决 threshold 问题
  PCA 从 B1 收集的 offline data 拟合, 部署时固定
  GPU 时间: 同 Mode A

Mode C: Hybrid (d=25 = 5 handcrafted + 20 PCA)
  x = concat([handcrafted_5, PCA(hidden_state, k=20)])
  目的: 最强配置, handcrafted 提供 informed prior + PCA 补充
  预期: 最高 SR + 最合理 trigger rate
  GPU 时间: 同 Mode A
```

#### E1.5 超参数

| 超参数 | 默认值 | 搜索范围 | 说明 |
|--------|--------|---------|------|
| `prior_var` (σ²_0) | 1.0 | {0.1, 1.0, 10.0} | 先验方差，越大 → 探索越多 |
| `warmup_episodes` | 10 | {5, 10, 20} | 纯探索阶段长度 |
| `lambda_cost` | 环境 specific | CMDP λ* | HotpotQA ~6.5, APPS ~1.06, WebShop ~1.27 |
| `update_freq` | 'episode' | {'step', 'episode'} | Posterior 更新频率 |
| Feature mode | C (hybrid) | {A, B, C} | 特征类型 |

#### E1.6 GO/NO-GO 判断标准

```
在 HotpotQA 上 (信号最强, 最容易验证):
  CACB Mode A SR ≥ 95% AND trigger_rate ∈ [30%, 70%]
    → GO, CACB 框架有效
  CACB Mode A SR ≥ SCG-LR(96.8%) AND cost < SCG cost
    → GO+, CACB Pareto-dominates SCG
  CACB Mode A SR < 90% OR trigger_rate > 90% OR trigger_rate < 5%
    → NO-GO, 检查实现

在 APPS 上 (关键: 能否超过 CaTS 59.0%):
  CACB any mode SR > 60% AND cost < CaTS 1.04×
    → 🎉 APPS 升级为 Pareto-dominate
  CACB any mode SR ∈ (58.8%, 60%)
    → 略有改进, 但不够 Pareto-dominate
  CACB any mode SR ≤ 58.8%
    → CACB 在弱信号环境无帮助
```

#### E1.7 论文叙事

```
§4: Method
  §4.1 Problem: Step-level Gating as Contextual Bandit
    "At each decision point, the agent faces a bandit problem:
     trigger the optimizer (paying cost λ) or proceed with the
     base policy (receiving zero additional value). The optimal
     policy triggers when E[U|x] > λ."

  §4.2 Cost-Aware Contextual Bandit Gate
    "We maintain a Bayesian posterior over the mapping from state
     features to optimizer utility. Thompson Sampling naturally
     balances exploration (learning the signal-utility direction)
     with exploitation (triggering when profitable), without
     requiring a separate calibration phase or explicit threshold
     tuning."

  §4.3 Connection to VOC
    "Our trigger condition û > λ is equivalent to the rational
     metareasoning condition VOC(T,s) > 0, where û is a posterior
     sample of the expected utility. The posterior uncertainty
     encodes the agent's epistemic uncertainty about signal
     direction — precisely the assumption that existing methods
     incorrectly treat as known."

贡献:
  (1) Principled exploration-exploitation for direction discovery
  (2) No threshold calibration needed (posterior + cost ratio 自动确定)
  (3) 理论 regret bound: O(d√T log T)
  (4) 统一 VOC/CMDP/Bandit 三个理论视角
```

#### E1.8 执行清单 — ✅ 全部完成

- [x] **E1.0** ✅ 实现 `frvc/cacb_gate.py` — Bayesian LR + Thompson Sampling + 3 feature modes
- [x] **E1.1** ✅ 实现 `experiments/p6_e_method_upgrade.py` — 统一 runner (E1/E2/E3)
- [x] **E1.2** ✅ HotpotQA sanity check → cacb_A SR=74.7% (方差大 50-88%)
- [x] **E1.3** ✅ 全量实验: 3 modes × 3 envs × 3 seeds = 27 runs (job 23167005)

**E1 结果汇总 (exploitation-only†):**

| | HotpotQA | APPS | WebShop |
|--|:--:|:--:|:--:|
| cacb_A (handcrafted) | 74.7%@3.80× | 59.7%@1.23× | 26.7%@1.57× |
| cacb_B (PCA) | 56.0%@1.80× | 59.7%@1.40× | 24.5%@1.90× |
| cacb_C (hybrid) | 53.2%@1.60× | 60.3%@1.51× | 18.2%@1.53× |

**E1 结论**: Thompson Sampling 在 HotpotQA 方差大且 SR 不如 SCG，在 APPS 上 cacb_A 略超 SCG (+0.9pp)。整体不如 E2/E3。

---

### E2. Contrastive Probe Gate — 🟡 补充方向

#### E2.1 核心思路

**目标**：让 probe 的输出 score 分布更 bimodal（"trigger" vs "skip" 两簇明显分开），使 threshold 校准变得 trivial。

**⚠️ 风险评估**：当前 ranking 不是瓶颈（Probe AUC 已 0.88-1.00），但 contrastive learning 可能产生更好校准的 score 分布，间接解决 threshold 问题。

#### E2.2 三种 Contrastive 方案

**方案 A: Supervised Contrastive Learning (SupCon)**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class ContrastiveProbeGate(nn.Module):
    """Supervised Contrastive Learning for Gating."""

    def __init__(self, input_dim=2560, proj_dim=64, temperature=0.07):
        super().__init__()
        # Projection head (训练时用)
        self.projector = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, proj_dim)
        )
        # Scoring head (部署时用)
        self.scorer = nn.Linear(proj_dim, 1)
        self.temperature = temperature

    def forward(self, h):
        z = F.normalize(self.projector(h), dim=-1)  # L2 normalized
        return z

    def score(self, h):
        z = self.forward(h)
        return self.scorer(z).squeeze(-1)

def supcon_loss(features, labels, temperature=0.07):
    """
    Supervised Contrastive Loss.

    features: (N, proj_dim), L2-normalized
    labels: (N,), binary (1=trigger, 0=skip)

    目标: 同类 hidden state 拉近, 异类推远
    → positive (U>0) 的 hidden states 聚成一簇
    → negative (U≤0) 的 hidden states 聚成另一簇
    → 两簇之间有清晰边界 → threshold trivial
    """
    N = features.shape[0]
    similarity = features @ features.T / temperature  # (N, N)

    # Mask: same class = positive pair
    mask_pos = (labels.unsqueeze(0) == labels.unsqueeze(1)).float()
    mask_pos.fill_diagonal_(0)  # 排除自己

    # Log-softmax over negative pairs
    logits_max = similarity.max(dim=1, keepdim=True).values
    logits = similarity - logits_max.detach()

    exp_logits = torch.exp(logits)
    mask_neg = 1 - torch.eye(N, device=features.device)
    log_prob = logits - torch.log((exp_logits * mask_neg).sum(dim=1, keepdim=True))

    # Mean of positive pairs
    pos_count = mask_pos.sum(dim=1).clamp(min=1)
    loss = -(mask_pos * log_prob).sum(dim=1) / pos_count

    return loss.mean()
```

**方案 B: Margin Ranking Loss (最简单)**

```python
class RankingProbeGate(nn.Module):
    """Pairwise Ranking for Gating — 最简实现."""

    def __init__(self, input_dim=2560, hidden_dim=128, margin=1.0):
        super().__init__()
        self.scorer = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 1)
        )
        self.margin = margin

    def forward(self, h):
        return self.scorer(h).squeeze(-1)

    def ranking_loss(self, h_pos, h_neg):
        """
        Margin ranking: s(h_pos) should exceed s(h_neg) by at least margin.

        h_pos: hidden states where U > 0 (rollout 有用)
        h_neg: hidden states where U ≤ 0 (rollout 无用)
        """
        s_pos = self.forward(h_pos)
        s_neg = self.forward(h_neg)
        return F.margin_ranking_loss(
            s_pos, s_neg,
            target=torch.ones_like(s_pos),
            margin=self.margin
        )
```

**方案 C: Prototypical Networks (最适合小样本)**

```python
class PrototypicalGate:
    """Prototypical Networks for few-shot gating adaptation."""

    def __init__(self, input_dim=2560, proj_dim=64):
        # 简单线性投影（不需要深度网络）
        self.projector = nn.Linear(input_dim, proj_dim)
        self.prototype_pos = None  # 正类原型
        self.prototype_neg = None  # 负类原型

    def fit(self, H, U):
        """
        从 exploration 数据拟合 prototypes.

        H: (N, 2560) hidden states
        U: (N,) utilities
        """
        with torch.no_grad():
            Z = self.projector(H)  # (N, proj_dim)
            mask_pos = (U > 0)
            mask_neg = (U <= 0)
            self.prototype_pos = Z[mask_pos].mean(dim=0)  # (proj_dim,)
            self.prototype_neg = Z[mask_neg].mean(dim=0)

    def score(self, h):
        """
        Score = 到正类原型的负距离 - 到负类原型的负距离.
        score > 0 → 更接近 "应该触发" → trigger
        score < 0 → 更接近 "不应触发" → skip

        → 天然 threshold = 0, 无需校准!
        """
        z = self.projector(h)
        d_pos = torch.norm(z - self.prototype_pos, dim=-1)
        d_neg = torch.norm(z - self.prototype_neg, dim=-1)
        return d_neg - d_pos  # 正值 = 更接近 pos = 应该触发

    def decide(self, h):
        return self.score(h) > 0  # threshold = 0, 固定
```

#### E2.3 训练流程

```
Phase 1: Offline Training (B1 数据, CPU/单 GPU, <10min per env)
  1. 加载 B1 hidden states: H (N, 2560), U (N,)
  2. 标签: y = (U > 0).float()
  3. Train/Val split: 80/20, 5-fold CV
  4. 训练三种方案 (A/B/C), 选最优

Phase 2: Offline Evaluation
  指标:
    - AUC-ROC (对比 B2 probe)
    - Score 分布: 画 positive/negative 的 score histogram
      → 关键: 两个分布是否 well-separated?
      → bimodality index (Hartigan's dip test)
    - 最优 threshold 位置: 两分布交叉点
    - Threshold 稳定性: bootstrap 100 次, threshold 的 std

Phase 3: End-to-End Gate (如果 offline 评估 GO)
  - 方案 A/B: 用 scorer output 做 threshold
  - 方案 C: 用 score > 0 (prototype 天然 threshold)
  - 跑 200ep × 3 seeds × 3 envs
```

#### E2.4 GO/NO-GO 标准

```
Offline (Phase 2):
  AUC ≥ 现有 Probe (0.88-1.00) → 继续
  Score bimodality: Hartigan's dip test p < 0.05 → score 分布是 bimodal → GO
  Threshold stability: bootstrap std < 0.1 → threshold 稳定 → GO

  如果 AUC 高但 score 不 bimodal → 方案 C (prototypical) 可能更好
  如果 AUC 低于 Probe → NO-GO for contrastive, 保持原 Probe

End-to-End (Phase 3):
  SR ≥ SCG-LR AND trigger_rate < always_trigger → GO
  SR < SCG-LR → NO-GO
```

#### E2.5 执行清单 — ✅ 全部完成

- [x] **E2.0** ✅ 实现 `frvc/contrastive_gate.py` — Prototypical Networks (天然 threshold=0)
- [x] **E2.1-E2.2** ✅ End-to-End: proto × 3 envs × 3 seeds = 9 runs (job 23167005)

**E2 结果汇总 (exploitation-only†):**

| | HotpotQA | APPS | WebShop |
|--|:--:|:--:|:--:|
| proto† | 94.4%@6.80× | 65.6%@3.37× | 39.8%@3.69× |

**E2 结论**: HotpotQA 接近 SCG (-2.4pp)，APPS 大幅超越 (+6.8pp)，WebShop 偏低 (-3.9pp)。整体第二好。

---

### E3. Principled SCG: Auto Feature Selection + CMDP Integration — 🟠 E1 补充

#### E3.1 核心思路

在不改变 gate 框架的前提下，让 feature selection 自动化，并与 CMDP 最优 threshold 紧密集成。

```
当前 SCG:
  人工选 5 feature → LR → 人工设 threshold(0.5)
  问题: (1) feature 需领域知识, (2) threshold 不最优

Principled SCG:
  自动构建 feature pool → LASSO 选最优子集 → CMDP λ* 最优 threshold
  目标: (1) 自动化, (2) 最优化, (3) 可解释
```

#### E3.2 自动 Feature Pool 构建

```python
def build_feature_pool(state_text, action_text, hidden_state,
                       env_name, history):
    """
    构建候选 feature pool（每个环境 25-50 个候选）.

    三类特征:
      Type U (Universal): 所有环境通用
      Type H (Hidden): hidden state 派生
      Type E (Environment): 环境特异（自动从 state_text 提取）
    """
    features = {}

    # === Type U: Universal Features (10 个) ===
    features['step_count'] = history['step_count']
    features['step_ratio'] = history['step_count'] / history['max_steps']
    features['token_entropy'] = compute_entropy(logits)
    features['response_length'] = len(action_text.split())
    features['action_diversity'] = len(set(history['recent_actions'][-5:])) / 5
    features['cumulative_reward'] = history['cumulative_reward']
    features['token_entropy_delta'] = features['token_entropy'] - history.get('prev_entropy', 0)
    features['perplexity'] = np.exp(features['token_entropy'])
    features['state_length'] = len(state_text.split())
    features['action_repetition'] = count_repeats(history['recent_actions'][-5:])

    # === Type H: Hidden State PCA Features (20 个) ===
    # PCA 从 B1 offline data 拟合, 部署时固定
    h_pca = pca_transform(hidden_state, n_components=20)  # (20,)
    for i in range(20):
        features[f'h_pca_{i}'] = h_pca[i]

    # === Type E: Environment-Specific Auto-Extracted (5-20 个) ===
    # 通过正则表达式从 state_text 自动提取结构化信息
    # 这些不是手工设计的"信号"，而是通用提取规则

    features['num_entities'] = len(re.findall(r'\b[A-Z][a-z]+\b', state_text))
    features['num_numbers'] = len(re.findall(r'\d+\.?\d*', state_text))
    features['has_error'] = int(bool(re.search(r'error|fail|invalid', state_text, re.I)))
    features['num_sections'] = state_text.count('\n\n')
    features['question_marks'] = state_text.count('?')

    # 环境自适应特征（通用 parser，根据 state_text 结构自动生成）
    if 'Observation:' in state_text:  # ReAct-style 环境
        features['observation_length'] = len(state_text.split('Observation:')[-1].split())
        features['num_observations'] = state_text.count('Observation:')
    if 'Action:' in state_text:
        features['num_actions_taken'] = state_text.count('Action:')

    return features  # dict of 35-50 features
```

#### E3.3 LASSO Auto Feature Selection

```python
from sklearn.linear_model import LogisticRegressionCV
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_classif
import numpy as np

class AutoFeatureSelector:
    """自动 feature selection: MI ranking → LASSO → 最终模型."""

    def __init__(self, max_features=10, cv_folds=5):
        self.max_features = max_features
        self.cv_folds = cv_folds
        self.selected_features = None
        self.scaler = StandardScaler()
        self.model = None
        self.feature_importance = None

    def fit(self, X_pool, y, feature_names):
        """
        Two-stage feature selection:

        Stage 1: MI-based pre-filtering (去掉明显无信息的)
          - 计算每个 candidate feature 与 y 的 mutual information
          - 保留 MI > 0.01 的 features (top-30 if > 30)

        Stage 2: LASSO selection (从 pre-filtered 中选最优子集)
          - L1-regularized logistic regression
          - λ_lasso 由 5-fold CV 选择
          - 非零系数的 features = selected features

        输出:
          - selected_features: 选中的 feature 名列表
          - feature_importance: 每个 feature 的 |coefficient|
          - model: 最终 LR 模型 (用选中 features)
        """
        # Stage 1: MI pre-filtering
        mi_scores = mutual_info_classif(X_pool, y, random_state=42)
        mi_ranking = sorted(zip(feature_names, mi_scores),
                           key=lambda x: -x[1])

        # 保留 MI > 0.01 的 top-30
        prefiltered = [(name, mi) for name, mi in mi_ranking
                       if mi > 0.01][:30]
        prefiltered_names = [name for name, _ in prefiltered]
        prefiltered_idx = [feature_names.index(n) for n in prefiltered_names]
        X_pre = X_pool[:, prefiltered_idx]

        # Stage 2: LASSO
        X_scaled = self.scaler.fit_transform(X_pre)

        self.model = LogisticRegressionCV(
            penalty='l1',
            solver='saga',
            Cs=20,                    # 搜索 20 个 C 值
            cv=self.cv_folds,
            scoring='roc_auc',
            max_iter=5000,
            random_state=42
        )
        self.model.fit(X_scaled, y)

        # 提取非零系数 = selected features
        coef = self.model.coef_[0]
        nonzero_mask = np.abs(coef) > 1e-6

        self.selected_features = [prefiltered_names[i]
                                  for i in range(len(prefiltered_names))
                                  if nonzero_mask[i]]
        self.feature_importance = {
            prefiltered_names[i]: abs(coef[i])
            for i in range(len(prefiltered_names))
            if nonzero_mask[i]
        }

        # 按重要性排序
        self.feature_importance = dict(
            sorted(self.feature_importance.items(),
                   key=lambda x: -x[1])
        )

        return self

    def report(self):
        """生成可解释的 feature selection 报告."""
        print(f"Selected {len(self.selected_features)} features "
              f"from pool of {self.max_features}:")
        for name, importance in self.feature_importance.items():
            direction = "positive" if self.model.coef_[0][
                list(self.feature_importance.keys()).index(name)
            ] > 0 else "negative"
            print(f"  {name}: importance={importance:.3f}, "
                  f"direction={direction}")
```

#### E3.4 CMDP-Optimal Threshold Integration

```python
class PrincipledSCG:
    """
    完整的 Principled SCG pipeline:
    Feature Pool → Auto Selection → CMDP Threshold → Gate
    """

    def __init__(self, budget_ratio=0.5):
        """
        budget_ratio: 允许的 compute budget (占 always_trigger 的比例)
          0.5 = 最多用 always_trigger 一半的 cost
        """
        self.budget_ratio = budget_ratio
        self.feature_selector = AutoFeatureSelector()
        self.lambda_star = None  # CMDP optimal multiplier

    def calibrate(self, explore_data):
        """
        从 exploration 数据完成全部校准:
        1. 构建 feature pool
        2. Auto feature selection (LASSO)
        3. CMDP dual ascent 求 λ*
        4. 最优 threshold = λ*/(1+λ*)
        """
        X_pool, y, feature_names = self._build_pool(explore_data)

        # Step 1: Auto feature selection
        self.feature_selector.fit(X_pool, y, feature_names)
        self.feature_selector.report()

        # Step 2: CMDP dual ascent for optimal λ*
        # 在 selected features 上训练最终 LR model
        # 然后找最优 threshold 使得 E[cost] ≤ budget
        X_selected = self._extract_selected(X_pool, feature_names)

        self.lambda_star = self._cmdp_dual_ascent(
            X_selected, y,
            budget=self.budget_ratio
        )

        print(f"CMDP λ* = {self.lambda_star:.4f}")
        print(f"Optimal threshold = {self.lambda_star/(1+self.lambda_star):.4f}")

    def _cmdp_dual_ascent(self, X, y, budget, lr=0.01, max_iter=100):
        """
        CMDP dual ascent:
          max_π E[U · 1{trigger}]
          s.t.  E[1{trigger}] ≤ budget

        Lagrangian:
          L(π, λ) = E[U · 1{trigger}] - λ(E[1{trigger}] - budget)
                   = E[(U - λ) · 1{trigger}] + λ·budget

        Optimal policy: trigger iff E[U|x] > λ
        Dual update: λ ← λ + lr · (E[1{trigger}] - budget)
        """
        lam = 0.1  # 初始 λ

        # 训练 utility predictor (LR on selected features)
        from sklearn.linear_model import LogisticRegression
        lr_model = LogisticRegression(max_iter=1000)
        lr_model.fit(X, y)
        u_pred = lr_model.predict_proba(X)[:, 1]  # P(U > 0)

        for i in range(max_iter):
            # Primal: trigger iff u_pred > λ/(1+λ)
            threshold = lam / (1 + lam)
            triggers = (u_pred > threshold).astype(float)
            trigger_rate = triggers.mean()

            # Dual update
            constraint_violation = trigger_rate - budget
            lam = max(0, lam + lr * constraint_violation)

            if abs(constraint_violation) < 0.01:
                break

        return lam

    def decide(self, features_dict):
        """Gate 决策: 提取 selected features → LR predict → 对比 threshold."""
        x = np.array([features_dict[f] for f in self.feature_selector.selected_features])
        x_scaled = self.feature_selector.scaler.transform(x.reshape(1, -1))
        p = self.feature_selector.model.predict_proba(x_scaled)[0, 1]
        threshold = self.lambda_star / (1 + self.lambda_star)
        return p > threshold
```

#### E3.5 关键可解释性产出

```
论文最有价值的输出: "LASSO 自动发现了什么 feature?"

预期结果（基于已有 signal discovery 数据的合理推测）:

HotpotQA LASSO 选出的 features:
  1. evidence_count (重要度 0.85)     ← 与手工选择完全一致
  2. h_pca_3 (重要度 0.42)            ← 新发现的 hidden state 维度
  3. step_ratio (重要度 0.31)         ← 手工未选但合理
  4. token_entropy (重要度 0.18)      ← 手工已选
  → LASSO 自动重新发现了 evidence_count! 且加入了 hidden state 维度

APPS LASSO 选出的 features:
  1. h_pca_0 (重要度 0.55)            ← hidden state 主成分
  2. step_count (重要度 0.38)         ← 与手工选择一致
  3. h_pca_7 (重要度 0.22)            ← 另一个 hidden state 维度
  → 手工 feature 信号弱 (ρ=0.274)，但 hidden state PCA 可能捕捉到更强信号

WebShop LASSO 选出的 features:
  1. state_category_encoded (重要度 0.91) ← 与手工选择完全一致
  2. num_observations (重要度 0.35)    ← 自动提取的结构化特征
  3. h_pca_1 (重要度 0.28)            ← hidden state 维度

论文叙事:
  "LASSO automatically rediscovered the key features that domain experts
   manually identified (evidence_count in QA, state_category in web
   navigation), while also uncovering hidden-state dimensions that
   carry additional predictive power."
```

#### E3.6 执行清单 — ✅ 全部完成

- [x] **E3.0** ✅ 实现 `frvc/principled_scg.py` — Auto feature pool + LASSO + CMDP
- [x] **E3.1-E3.2** ✅ End-to-End: principled × 3 envs × 3 seeds = 9 runs (job 23167005)

**E3 结果汇总 (exploitation-only†):**

| | HotpotQA | APPS | WebShop |
|--|:--:|:--:|:--:|
| principled† | **96.7%**@8.05× | **66.2%**@3.58× | **42.7%**@2.46× |

**E3 结论 — 🏆 最佳自动化方法:**
- HotpotQA: 96.7% ≈ SCG 96.8% (**-0.1pp**) → 完全自动化达到手工水平
- APPS: 66.2% >> SCG 58.8% (**+7.4pp**) → 弱信号环境大幅超越
- WebShop: 42.7% ≈ SCG 43.7% (**-1.0pp**) → 接近手工水平
- Cost 一致偏高（Ro/ep 高于 SCG），是 SR-cost tradeoff
- Pareto-dominates CaTS on HotpotQA + WebShop

---

### E 综合: 三方向对比 + 最优组合

#### 实验矩阵

```
Phase 1: Offline 验证 (CPU/单 GPU, ~2h total)
  E1: Bayesian LR posterior 在 B1 数据上的 calibration quality
  E2: 3 种 contrastive 方案 offline AUC + score bimodality
  E3: LASSO feature selection + 可解释性报告

Phase 2: Sanity Check (1 env, 1 seed each)
  E1 Mode A: HotpotQA 200ep (~40min)     → SR / trigger_rate
  E2 best:   HotpotQA 200ep (~40min)     → SR / trigger_rate
  E3:        HotpotQA 200ep (~40min)     → SR / trigger_rate

Phase 3: Full Experiment (GO 的方向, 3 env × 3 seeds)
  最多: 27 runs (E1) + 9 runs (E2) + 9 runs (E3) = 45 runs
  最少: 9 runs (仅 E1 best mode)
```

#### 实验结论与方向间对比

```
✅ 实际结果 (45/45 完成):

  E1 CACB: HotpotQA 方差大不稳定, APPS 略超 SCG, WebShop 差
    → 结论: Thompson Sampling 在有限 200ep 下不稳定, 不适合作主方法

  E2 Proto: HotpotQA -2.4pp, APPS +6.8pp, WebShop -3.9pp
    → 结论: 可用但不如 E3

  E3 Principled: HotpotQA -0.1pp, APPS +7.4pp, WebShop -1.0pp ← 🏆 最佳
    → 结论: 全自动化, 三个环境都接近/超过 SCG

→ 保底方案已确认: E3 Principled SCG 作为补充方法
  = 自动选特征 + CMDP threshold, 无需领域知识
  = Method novelty ⭐⭐⭐
  = SCG + Principled 互补: cost-sensitive vs SR-first

已验证的优化:
  ✅ 4. 去掉 PCA → principled_nopca: SR 几乎不变, 省掉 HF engine
  ⚠️ 1a. principled_auto (固定 λ=0.05): HotpotQA SR 暴跌 68.2%
  ✅ 1b. principled_adaptive (自适应 λ): HotpotQA 恢复 95.7%, TWExpress 99.2% 🔥
       但 Plancraft LASSO 2/3 seeds 失败, BabyAI/Plancraft cost 仍高
  🔄 1c. principled_fbeta: F-beta threshold, β=sqrt(pos_rate/(1-pos_rate))
       完全不需要 C_ratio, 纯 online, pos_rate<2% → fallback 不触发

Threshold 优化完整迭代:
  nopca:      启发式 threshold → APPS 过度触发 (Ro/ep=2.19)
  auto:       固定 λ=0.05 sweep → HotpotQA 过度保守 (SR 68.2%)
  adaptive:   自适应 λ from data → ✅ 主环境修复, ⚠️ Plancraft LASSO 失败
  fbeta:      F-beta, β from pos_rate → 🔄 running, 预期修复 Plancraft

后续可优化方向:
  2. 缩短探索期 (50ep→20ep) → 减少探索浪费
  3. 自适应探索期 (explore_rate 随信号强度衰减)
  5. 用 offline 数据预训练 LASSO → 跳过在线探索
  6. E1+E3 组合: LASSO 选特征 + Thompson Sampling 做决策
```

#### GPU 时间预估

| 阶段 | 任务 | GPU 时间 |
|------|------|---------|
| Phase 1 Offline | E1/E2/E3 offline 验证 | ~0h (CPU) |
| Phase 2 Sanity | E1+E2+E3 各 1 seed HotpotQA | ~2h |
| Phase 3 E1 Full | 3 modes × 3 envs × 3 seeds = 27 | ~18h |
| Phase 3 E2 Full | 1 best × 3 envs × 3 seeds = 9 | ~6h |
| Phase 3 E3 Full | 1 config × 3 envs × 3 seeds = 9 | ~6h |
| **总计 (最大)** | | **~32h** |
| **总计 (最可能: E1 full + E3 full)** | | **~24h** |

#### 执行时间线 — ✅ 全部完成

```
═══════════════════════════════════════════════════════════════════
  路径 E 实际执行 (Mar 14)
═══════════════════════════════════════════════════════════════════

  Mar 14 下午: ✅ 实现 + 提交
  ├── [E1.0] ✅ 实现 CACBGate
  ├── [E2.0] ✅ 实现 PrototypicalGate
  ├── [E3.0] ✅ 实现 PrincipledSCG
  ├── [E*]   ✅ 统一 runner + sbatch 编写
  └── [E*]   ✅ 提交 45 jobs (job 23167005)

  Mar 14 晚: ✅ 结果收集
  ├── HotpotQA 15/15 完成 (~15min/job)
  ├── APPS 15/15 完成 (~15min/job)
  └── WebShop 15/15 完成 (~1h/job)

  结果:
  ├── E3:principled 🏆 最佳自动化方法
  ├── E2:proto 第二好
  └── E1:cacb 方差大, 不够稳定

后续计划:
  ├── ✅ Online Ablation (job 23175320): HotpotQA/APPS/WebShop 完成
  │     关键发现: No PCA ≈ Offline PCA → 不需要 HF engine
  ├── 🔄 BabyAI/Plancraft online/nopca (23175320): running
  ├── 🔄 TWExpress online/nopca (job 23176360): pending
  ├── ✅ principled_auto (job 23176425): 18/18 完成, HotpotQA 暴跌
  ├── ✅ principled_adaptive (job 23179282): 18/18 完成, CAGC #2
  └── 🔄 principled_fbeta (job 23185268): F-beta threshold, 18 runs
```

  后续:
  ├── principled_fbeta 全 6 环境结果
  ├── adaptive vs fbeta 最终对比
  ├── 确定最终方法版本
  ├── 论文 §4 Method 结构确定
  └── 开始写 LaTeX
═══════════════════════════════════════════════════════════════════
```

---

## 6. 执行时间线（v4.0 修订）

```
═══════════════════════════════════════════════════════════════════════
  Week 1 (Mar 12-16) — ✅ A/D 完成 + ❌ C 全 NO-GO + B 启动 + B4 发现 threshold 瓶颈
═══════════════════════════════════════════════════════════════════════

  Day 1 (Mar 12): ✅ 已完成
  ├── [A1] ✅ TWExpress CB 12/12 完成, 定位: 对比案例
  ├── [A2] ✅ APPS rerun 9/9 完成, oracle=75.0%
  └── [C1] ✅ ToolBench G1 环境搭建 + MirrorAPI 部署

  Day 2 (Mar 13): ✅ 已完成
  ├── [A3] ✅ Token cost 全部完成 (TWExpress/BabyAI/Plancraft)
  ├── [C1-C4] ❌ 全部 NO-GO (ToolBench/ALFWorld/ScienceWorld/InterCode)
  ├── [D1-D4] ✅ Toy Model 全部完成 (P1/P2/P3 confirmed, Figure 2+7 已生成)
  ├── [B1-B3] ✅ Hidden state 收集 + Probe 训练 + GO 判断 (3/3 GO)
  ├── [B4v1] ⚠️ End-to-end 发现 cost 问题 (probe = always_trigger)
  └── [B6] ✅ 科学分析完成 (layer-wise, transfer matrix, learning curve)

  Day 3 (Mar 14): ✅ 已完成
  ├── [B4v2] ⚠️ 4 种 threshold 校准方法 → 在线校准失败
  ├── [B4v3] 🔄 Offline threshold + Adaptive RL → Running (job 23164633)
  └── [E] 🆕 识别结构性问题 → 启动路径 E Method Upgrade 规划

═══════════════════════════════════════════════════════════════════════
  Week 1.5 (Mar 15-16) — 🆕 路径 E 实现 + Offline 验证 + B4v3 结果
═══════════════════════════════════════════════════════════════════════

  Day 4 (Mar 15): 🔴 路径 E 实现
  ├── [E1.0] 实现 CACBGate (frvc/cacb_gate.py)
  │          - Bayesian LR posterior (Laplace approximation)
  │          - Thompson sampling decision
  │          - 3 feature modes (A/B/C)
  ├── [E2.0] 实现 ContrastiveGate (frvc/contrastive_gate.py)
  │          - SupCon / Margin Ranking / Prototypical 三方案
  ├── [E3.0] 实现 PrincipledSCG (frvc/principled_scg.py)
  │          - Feature pool builder + LASSO selector + CMDP threshold
  ├── [E1-E3] Offline 验证 (CPU, 复用 B1 数据)
  │          - E1: Bayesian posterior calibration quality
  │          - E2: 3 方案 AUC + score bimodality test
  │          - E3: LASSO selection report (选了什么 feature?)
  └── [B4v3] 🔄 分析结果 (如果已完成)

  Day 5 (Mar 16): 🔴 Sanity Check (每方向 1 seed)
  ├── [E1.2] HotpotQA CACB Mode A (1 seed, ~40min) → SR/trigger_rate?
  ├── [E2.2] HotpotQA Contrastive best (1 seed, ~40min) → SR/trigger_rate?
  ├── [E3.2] HotpotQA PrincipledSCG (1 seed, ~40min) → SR/trigger_rate?
  └── 🔴 GO/NO-GO 决策: 哪些方向继续 full experiment?

  ┌──────────────────────────────────────────────────────────────────┐
  │ Week 1.5 检查点 (Mar 16 EOD) — 关键决策                         │
  │                                                                  │
  │ 必须确定:                                                        │
  │ 1. B4v3 结果 → 现有 probe threshold 策略是否可用?                │
  │ 2. E1 CACB sanity → Thompson sampling 有效? trigger_rate 合理?   │
  │ 3. E2 Contrastive → score bimodal? 优于 probe?                  │
  │ 4. E3 Principled → LASSO 选了什么? AUC 提升?                    │
  │                                                                  │
  │ 决策:                                                            │
  │  ≥ 2 个方向 GO → 并行 full experiment (Week 2)                   │
  │  = 1 个方向 GO → 集中资源做好这个                                │
  │  = 0 个方向 GO → 回退: 保持 SCG-LR, 论文走 finding+theory 路线  │
  └──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
  Week 2 (Mar 17-21) — GO 方向 Full Experiment + 科学分析
═══════════════════════════════════════════════════════════════════════

  Day 6-8 (Mar 17-19):
  ├── [E*] GO 方向 full: 3 envs × 3 seeds (9-27 runs per direction)
  │         E1: 最优 mode × 3 envs × 3 seeds = 9 runs
  │         E2: (如果 GO) best 方案 × 3 envs × 3 seeds = 9 runs
  │         E3: (如果 GO) × 3 envs × 3 seeds = 9 runs
  │         并发 9 jobs, 每 job ~40min → ~4-12h
  ├── [B6] Figure 6 最终版 (三面板: layer-wise + transfer + learning curve)
  └── [E*] 中间结果分析: 哪个方向在 APPS 上超过 CaTS?

  Day 9-10 (Mar 20-21):
  ├── [E*] 全方向结果分析: SR / cost / trigger_rate / Pareto
  ├── [E*] 最优组合确定 (E1+E3? E1 only? 等)
  ├── 论文 §4 Method 结构确定
  └── 论文 method 叙事最终确定

  ┌──────────────────────────────────────────────────────────────────┐
  │ Week 2 检查点 (Mar 21)                                          │
  │                                                                  │
  │ 确认:                                                            │
  │ 1. 最优 method 确定 → 论文 §4 写什么?                            │
  │ 2. APPS 最优 method SR > CaTS 59.0%? → APPS 定位升级?           │
  │ 3. 方法对比表: CACB vs Contrastive vs PrincipledSCG vs 原 SCG   │
  │ 4. B6 cross-env transfer 闭环 Two-Source Model ✅                │
  │ 5. 论文 NeurIPS 接受概率重新评估                                 │
  └──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
  Week 3 (Mar 22-26) — 收尾 + 统一分析 + 写作
═══════════════════════════════════════════════════════════════════════

  Day 11-13 (Mar 22-24):
  ├── 消融实验 (最优 method 的 ablation)
  ├── 所有环境 + 所有方法 统一 Pareto 分析
  └── Unified Results Table 定稿

  Day 14-15 (Mar 25-26):
  ├── Pareto figure 统一生成
  ├── phase6_final_report.md 撰写
  └── 开始写 LaTeX（数据齐全）

═══════════════════════════════════════════════════════════════════════
```

---

## 7. 最终环境组合预测（v4.0 — 方法升级后的环境定位）

```
✅ 确定: 4 环境 = HotpotQA(Pareto) + WebShop(Pareto) + APPS(升级中) + TWExpress(对比)

⚠️ B4v1 Probe 的"假成功":
  Probe gate end-to-end (B4v1, threshold=0.05):
    HotpotQA: 97.0% (但 Ro/ep=1.80 ≈ always_trigger 1.80 → 100%触发)
    APPS:     64.5% (但 Ro/ep=2.58 ≈ always_trigger 2.58 → 100%触发)
    WebShop:  41.8% (但 Ro/ep=5.61 ≈ always_trigger 5.63 → 100%触发)
  → SR 提升来自过度触发，不是精准选择。Cost 极高。

路径 E Method Upgrade 后的预期:

  场景 1 (E1 CACB 成功, P=40%):
    HotpotQA: ~96-97% @ 合理 trigger rate (40-60%)  → Pareto-dominate ✅
    APPS:     ~60-62% @ trigger rate ~15-25%         → 可能 Pareto-dominate CaTS 🎉
    WebShop:  ~42-44% @ trigger rate ~15-25%         → Pareto-dominate ✅
    → 3 个 Pareto-dominate + 1 对比
    → Method novelty ⭐⭐⭐⭐ (Bayesian + cost-aware)
    → NeurIPS 70-80%

  场景 2 (E1 部分成功 + E3 补充, P=35%):
    Method: CACB on handcrafted features + LASSO auto discovery
    → 2-3 个 Pareto-dominate
    → Method novelty ⭐⭐⭐½
    → NeurIPS 60-70%

  场景 3 (路径 E 全 NO-GO, P=25%):
    → 保持 SCG-LR + Probe 作为分析工具
    → Method novelty ⭐⭐
    → 论文走 finding + theory 路线
    → NeurIPS 45-55%
```

---

## 8. GO/NO-GO 总判定（v4.0 — 路径 E 加入后更新）

### Mar 16 检查点（Week 1.5 结束）— v4.0 关键决策点

| 条件 | 状态 | 行动 |
|------|:----:|------|
| Probe offline R² > 0.10 | ✅ **已确认** | R²=0.25-0.96, AUC=0.88-1.00, 3/3 GO |
| Probe end-to-end (B4) | ⚠️ **threshold 瓶颈** | B4v1/v2 失败, v3 running |
| P1 ρ_early < ρ_late | ✅ **已确认** | Toy Model P1 confirmed |
| Simpson's Paradox | ✅ **已确认** | 3/4 案例 confirmed |
| TWExpress 定位 | ✅ **已确认** | 对比案例 |
| 新环境 | ✅ **已确认** | 全部 NO-GO → 4 环境锁定 |
| **🆕 E1 CACB sanity** | ⬜ **待测** | HotpotQA 1 seed → SR/trigger_rate? |
| **🆕 E2 Contrastive sanity** | ⬜ **待测** | Score bimodal? |
| **🆕 E3 Principled sanity** | ⬜ **待测** | LASSO 选了什么? |

### Mar 21 检查点（Week 2 结束）— Method 最终确定

```
E1 CACB Pareto-dominates 原 SCG + APPS > CaTS:
  → 🎉 论文方法: CACB-Gate (Contextual Bandit + cost-aware)
  → APPS 升级为 Pareto-dominate (第 3 个)
  → Method novelty ⭐⭐⭐⭐
  → NeurIPS 70-80%

E1 CACB ≈ 原 SCG 但更 principled + E3 LASSO 可解释:
  → ✅ 论文方法: Principled Direction-Aware Gate (E1+E3 组合)
  → Method novelty ⭐⭐⭐½
  → NeurIPS 60-70%

E1/E2/E3 均 ≤ 原 SCG:
  → ⚠️ 保持 SCG-LR + Probe 分析
  → 论文定位 finding + theory paper
  → Method novelty ⭐⭐ (Probe B6 分析作为补充贡献)
  → NeurIPS 45-55%
```

### Mar 26 检查点（Phase 6 结束）

```
4 env + 方法升级成功:   → 🎉 NeurIPS 70-80%, 全面写作
4 env + 方法持平:       → ✅ NeurIPS 55-65%, 可投
4 env + 方法全失败:     → ⚠️ NeurIPS 40-50%, 考虑 ICLR 2027 (加时间改进方法)
```

---

## 9. 完整 Checklist（v3.2 更新 — 2026-03-13）

### 路径 A — 完善现有环境 ✅ 全部完成

- [x] **A1.1** ✅ TWExpress CB 12/12 完成 → 数据已提取
- [x] **A1.2** ✅ TWExpress 定位确定: 对比案例 (rollout-safe, SCG 选择性是劣势)
- [x] **A1.3** ✅ TWExpress token cost: C_base=524, C_rollout=8002, C_vote=2620
- [x] **A2.1** ✅ APPS rerun 9/9 完成 → oracle=75.0%!
- [x] **A2.2** ✅ APPS 统一结果表已更新
- [x] **A3.1** ✅ 全部 6 环境 token cost 完成 (含 BabyAI/Plancraft)
- [ ] **A3.2** 所有论文环境统一 Pareto figure 生成（等 B4 结果后一起）

### 路径 B — Hidden State Probe (13/17 完成 + B4v2 36 jobs running)

- [x] **B1.0** ✅ 检查已有 hidden state 数据 → Phase 5 有 state_texts 可复用
- [x] **B1.1** ✅ HotpotQA 多层 hidden state 收集 → (391, 9, 2560), 19.1 MB (job 23151614_0)
- [x] **B1.2** ✅ APPS 多层 hidden state 收集 → (518, 9, 2560), 25.3 MB (job 23151614_1)
- [x] **B1.3** ✅ WebShop 多层 hidden state 收集 → (1261, 9, 2560), 61.7 MB (job 23151614_2)
- [x] **B2.1** ✅ 4 种 probe 训练脚本实现 → `experiments/p6_b2_probe_training.py`
- [x] **B2.2** ✅ 3 环境 P1-P4 训练 + 评估 → Best: P3 MLP R²=0.48/0.57/0.96, AUC=0.92/0.88/1.00
- [x] **B2.3** ✅ 对比 handcrafted LR 基线 → Handcrafted AUC=1.00/0.98/1.00 略优但 probe 无需领域知识
- [x] **B3** ✅ **3/3 GO** — 所有环境 R² >> 0.10, AUC >> 0.70
- [x] **B2.4** ✅ APPS + WebShop probe offline 评估已含在 B2.2 中
- [x] **B4.1** ✅ HotpotQA probe gate 200ep × 3 seeds → Mean SR=97.0% (≈ handcrafted 96.8%)
- [x] **B4.2** ✅ WebShop probe gate 200ep × 3 seeds → Mean SR=41.8% (vs handcrafted 43.7%)
- [x] **B4.3** ✅ APPS probe gate 200ep × 3 seeds → Mean SR=64.5% (vs handcrafted 58.8%)
- ⚠️ **B4 问题发现**: Probe gate 触发率 ≈ always_trigger（threshold=0.05 太低），cost 极高。SR 提升来自过度触发而非精准选择。
- [ ] **B4v2** 🔄 Calibrated Probe Gate — 4 种 threshold 自适应方法 × 3 env × 3 seeds = 36 runs (job 23164048)
  - **A. Quantile-adaptive**: threshold = 匹配 positive_rate 的分位数
  - **B. F1-optimal**: 最大化 F1(pred>t, actual>0) 的 threshold
  - **C. Cost-EV**: 最大化 E[utility] - λ·trigger_cost（λ = C_rollout/C_base）
  - **D. Online Bayesian**: F1 warm-start + EMA 在线自适应
  - 代码: `frvc/calibrated_probe_gate.py` + `experiments/p6_b4v2_calibrated.py`
- [ ] **B5** 消融实验 (job 23163738 running)
- [x] **B6.1** ✅ Layer-wise probing: 所有层 AUC 0.79-1.00, 信号广泛分布
- [x] **B6.2** ✅ Cross-env transfer: 对角线≈1.0, 非对角线 0.17-0.65 → **验证 Two-Source Model**
- [x] **B6.3** ✅ Learning curve: 50 samples 即 AUC > 0.74-0.99, 快速饱和
- [ ] **B6.4** （可选）Feature attribution

### 路径 C — 新环境 ❌ 全部 NO-GO

- [x] **C1.0** ✅ ToolBench G1 环境搭建 + MirrorAPI 部署
- [x] **C1.1** ❌ ToolBench G1+MirrorAPI Step 0 → **NO-GO** (base=94-98%, Δ=0%)
- [x] ~~C1.2-C1.4~~ — ❌ G1 NO-GO, G2/G3 搁置
- [x] **C2.0** ✅ ALFWorld 环境搭建 (Phase 5 已完成)
- [x] **C2.1** ❌ ALFWorld Step 0 → **NO-GO** (base=28%, always=30%, Δ=2%, Phase 5 3/7)
- [x] ~~C2.2-C2.4~~ — ❌ NO-GO
- [x] **C3.0** ✅ ScienceWorld 环境搭建 (Phase 5 已完成)
- [x] **C3.1** ❌ ScienceWorld Step 0 → **NO-GO** (base=0%, always=0%, Phase 5 3/7)
- [x] ~~C3.2-C3.4~~ — ❌ NO-GO
- [x] **C4.0** ✅ InterCode-bash 环境搭建 (Phase 5 已完成)
- [x] **C4.1** ❌ InterCode-bash Step 0 → **NO-GO** (base=100%, always=100%, Phase 5 3/7)
- [x] ~~AgentBench-KG~~ — ❌ 已砍
- [x] ~~CrosswordQA~~ — ❌ 已砍

### 路径 D — Toy Model Verification ✅ 全部完成

- [x] **D1.1** ✅ Temporal shift 分析脚本编写 → `experiments/p6_toy_model_verification.py`
- [x] **D1.2** ✅ HotpotQA P1: early(ρ=-0.176) vs late(ρ=-0.437), shift=-0.261
- [x] **D1.3** ✅ APPS(shift=-0.245) / MBPP(shift=-0.461) / WebShop(shift=-0.291) P1 验证
- [x] **D1.4** ✅ Figure 7 生成 → `results/phase6/toy_model/figure7_temporal_shift.pdf`
- [x] **D2.1** ✅ HotpotQA Simpson's Paradox: evidence_count≤1(ρ=-0.265) vs >1(ρ=+0.121) → **True**
- [x] **D2.2** ✅ APPS Simpson's Paradox: step_count≤1(ρ=+0.102) vs >1(ρ=-0.144) → **True**
- [x] **D2.3** ✅ Simpson's Paradox 可视化 → `results/phase6/toy_model/simpsons_paradox_scatter.png`
- [x] **D3.1** ✅ P2 divergence 矩阵: HotpotQA vs MBPP 差异最大(0.480)，APPS vs MBPP 最小(0.010)
- [x] **D3.2** ✅ P3 signal identity: HotpotQA=Type I(evidence_count), MBPP/WebShop=Type D
- [x] **D3.3** ⬜ P1/P2/P3 综合为论文 §5.7 段落（写作阶段完成）
- [x] **D4.1** ✅ Figure 2 绘图脚本编写
- [x] **D4.2** ✅ α, β 参数估计
- [x] **D4.3** ✅ Figure 2 生成 → `results/phase6/toy_model/figure2_two_source_model.pdf`

### 路径 E — Method Upgrade 🆕 v4.0

**E1: Cost-Aware Contextual Bandit Gate (CACB)**
- [ ] **E1.0** 实现 `frvc/cacb_gate.py`
  - [ ] Bayesian LR posterior (Laplace approximation)
  - [ ] Thompson sampling decision function
  - [ ] 三种 feature mode (A: handcrafted, B: PCA, C: hybrid)
  - [ ] Warmup 逻辑 + posterior update scheduling
- [ ] **E1.1** 实现 `experiments/p6_e1_cacb_gate.py`
- [ ] **E1.2** HotpotQA Mode A sanity: 1 seed × 200ep
- [ ] **E1.3** Full experiment (GO 后): modes × 3 envs × 3 seeds
- [ ] **E1.4** 结果分析 + posterior convergence 可视化

**E2: Contrastive Probe Gate**
- [ ] **E2.0** 实现 `frvc/contrastive_gate.py`
  - [ ] 方案 A: SupCon loss
  - [ ] 方案 B: Margin ranking
  - [ ] 方案 C: Prototypical networks
- [ ] **E2.1** Offline 训练 + 评估 (3 方案 × 3 envs, CPU)
  - [ ] AUC 对比 + score bimodality test
- [ ] **E2.2** End-to-End (如果 GO): best × 3 envs × 3 seeds
- [ ] **E2.3** 结果分析 + score 分布可视化

**E3: Principled SCG (Auto Feature Selection + CMDP)**
- [ ] **E3.0** 实现 `frvc/principled_scg.py`
  - [ ] Feature pool builder (Universal + Hidden PCA + Auto-extracted)
  - [ ] AutoFeatureSelector (MI ranking + LASSO)
  - [ ] CMDP dual ascent threshold optimizer
- [ ] **E3.1** Offline: LASSO selection + 可解释性报告 (3 envs, CPU)
- [ ] **E3.2** End-to-End: PrincipledSCG × 3 envs × 3 seeds
- [ ] **E3.3** 可解释性分析 (LASSO vs 手工选择 Venn 图)

### 收尾

- [ ] Unified Results Table（所有论文环境 × 所有方法含路径 E）
- [ ] Pareto figure 统一生成（含路径 E 最优方法）
- [x] Figure 2 (Two-Source Model) ✅ + Figure 7 (P1 Verification) ✅ 就绪
- [x] Figure 6 (Probe Analysis) ✅ 数据已有，待最终绘图
- [ ] phase6_final_report.md
- [x] 论文最终环境集确定 → **4 环境锁定** (HotpotQA + WebShop + APPS + TWExpress)

---

## 10. 资源估算（v4.0 — 路径 E 加入）

### GPU 时间

| 任务 | GPU 时间 | 优先级 | 状态 |
|------|---------|:------:|:----:|
| ~~A: Token cost 分析~~ | ~~1h~~ | ~~已完成~~ | ✅ |
| ~~C: 新环境 Step 0~~ | ~~8h~~ | ~~已砍~~ | ❌ |
| ~~D: Toy Model~~ | ~~0h~~ | ~~已完成~~ | ✅ |
| ~~B1-B3: Hidden state + Probe~~ | ~~4h~~ | ~~已完成~~ | ✅ |
| ~~B4v1: End-to-end (threshold=0.05)~~ | ~~6h~~ | ~~已完成~~ | ✅ (发现 cost 问题) |
| B4v2/v3: Threshold 校准 | ~6h | 🟠 | 🔄 running |
| ~~B6: 科学分析~~ | ~~1h~~ | ~~已完成~~ | ✅ |
| **🆕 E1: CACB offline + sanity** | ~1h (sanity) | 🔴 | ⬜ |
| **🆕 E1: CACB full (如果 GO)** | ~18h (27 runs) | 🔴 | ⬜ |
| **🆕 E2: Contrastive offline** | ~0h (CPU) | 🟡 | ⬜ |
| **🆕 E2: Contrastive full (如果 GO)** | ~6h (9 runs) | 🟡 | ⬜ |
| **🆕 E3: Principled offline** | ~0h (CPU) | 🟠 | ⬜ |
| **🆕 E3: Principled full (如果 GO)** | ~6h (9 runs) | 🟠 | ⬜ |
| B5: 消融 | ~4h | 🟡 | ⬜ |
| **路径 E 总计 (最大)** | **~32h** | | |
| **路径 E 总计 (最可能: E1 full + E3 full)** | **~24h** | | |

### SLURM 管理

- 预估新增 jobs：~27-45 个（路径 E 主体）+ ~18 个（B4v3 running）
- 提交顺序：E1/E2/E3 sanity (各 1 job) → GO 方向 full (9-27 jobs 并发)
- 并发策略：9 jobs 并发 (SLURM array), 每 job ~40min

---

## 11. 风险管理（v4.0 — 路径 E 新风险）

| 风险 | 概率 | 影响 | 缓解措施 | 状态 |
|------|:----:|:----:|---------|:----:|
| ~~Hidden State Probe offline NO-GO~~ | ~~30%~~ | ~~高~~ | 3/3 GO (AUC 0.88-1.00) | ✅ **GO** |
| **Probe threshold 校准失败** | 70% | 高 | B4v1/v2 已失败; B4v3 running; **路径 E 是 plan B** | 🔴 **已部分实现** |
| ~~所有新环境 NO-GO~~ | ~~25%~~ | ~~中~~ | 全部 NO-GO → 4 环境锁定 | ✅ **已实现** |
| **🆕 路径 E 全部 NO-GO** | 25% | 高 | 三方向并行降低风险; 回退: finding+theory paper | ⬜ |
| **🆕 E1 CACB counterfactual bias** | 30% | 中 | 不触发时无法观测 U → warmup 收集无偏数据 | ⬜ |
| **🆕 E2 Contrastive 不 bimodal** | 50% | 低 | E2 不是核心方向; 方案 C (prototypical) 天然 threshold=0 | ⬜ |
| **🆕 GPU quota 紧张** | 30% | 中 | 路径 E 最大 ~32h; 优先 E1, 砍 E2 if needed | ⬜ |
| 论文写作时间不足 | 20% | 中 | Week 3 开始写作; Intro/Theory 部分可立即开始 | ⬜ |

---

## 12. 与论文写作的衔接

**Phase 6 → 论文的关键产出**：

| Phase 6 产出 | 论文位置 | 依赖 |
|-------------|---------|------|
| Probe 结果 | §4.4 方法描述 + §5.7b 分析 | B3/B4 | ✅ B4 完成: HotpotQA +0.2pp, APPS +5.7pp, WebShop -1.9pp |
| Layer-wise + Transfer + Learning Curve | §4.5 + Figure 6 (三面板) | B6 | ✅ 数据已有，待绘图 |
| 统一 Pareto 图 | Figure 4 + Table 2 | A3 + B4 | ⬜ 待绘图 |
| ~~新环境数据~~ | ~~§5 环境扩展~~ | ~~C*~~ | ❌ 无新环境 |
| TWExpress 对比分析 | §5.2 Diagnostic Analysis | A1 | ✅ |
| APPS 弱信号分析 | §5.2 或 Appendix | A2 | ✅ |
| P1 Temporal Shift 验证 | §5.7 E4 + Figure 7 | D1 | ✅ |
| Simpson's Paradox 子群 | §3.3 Theoretical grounding | D2 | ✅ |
| P2/P3 Cross-env + Signal Identity | §5.7 E4 | D3 | ✅ |
| Two-Source Model 理论曲线 | §3.3 + Figure 2 | D4 | ✅ |

**论文叙事（v4.0 — 取决于路径 E 结果）**：

```
场景 1: E1 CACB 成功 (最推荐叙事):
  §4.1 Problem: Step-level gating as contextual bandit
  §4.2 Cost-Aware Contextual Bandit Gate (CACB)
    → Thompson sampling discovers direction + threshold online
    → 理论: regret bound O(d√T log T), 连接 VOC/CMDP
  §4.3 (如果 E3 GO) Auto Feature Selection (LASSO)
    → "LASSO rediscovers expert-chosen features + finds new ones"
  §4.4 Hidden State Probes as Scientific Tool (B6 分析)
    → Cross-env transfer failure validates Two-Source Model
  Method novelty ⭐⭐⭐⭐, NeurIPS 70-80%

场景 2: E3 Principled SCG 成功但 E1 部分:
  §4.1 Problem: Direction discovery for adaptive gating
  §4.2 Automatic Feature Discovery (LASSO + MI)
  §4.3 CMDP-Optimal Gate
  §4.4 Hidden State Analysis
  Method novelty ⭐⭐⭐, NeurIPS 60-70%

场景 3: 路径 E 全 NO-GO:
  保持 SCG-LR + Probe 作为 analysis tool
  论文重心: finding + Two-Source Theory (已验证)
  Method novelty ⭐⭐, Theory novelty ⭐⭐⭐⭐
  NeurIPS 45-55% (finding-driven paper)
```

**不变的论文资产（无论路径 E 结果如何）**：
```
✅ Direction Reversal Finding — 核心 selling point
✅ Two-Source Uncertainty Model — 理论贡献 (P1/P2/P3 全部 confirmed)
✅ Simpson's Paradox 实证 — 理论 grounding
✅ B6 Cross-env Transfer Matrix — 验证 Two-Source Model
✅ 4 Competing Baselines × 3 envs — 实验充分度
✅ 4 环境多样性 — QA + Code + Web + Planning
✅ Token Cost + Pareto 分析框架 — 方法论贡献
```
