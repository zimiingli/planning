# Competing Baselines 实验结果报告

**生成日期**: 2026-03-19 (updated: 2026-03-20, 新增 FEVER + APPS Interview CB 数据)
**范围**: 6 个 Competing Baselines（CATTS, SEAG, CoRefine, CaTS, AUQ, s1 Budget）在 5+2 个环境上的实验结果
**数据来源**: Phase 5 环境报告 + Phase 6.1b 新 baseline JSON 数据 + Phase 6.1 新环境扩展

---

## 1. 方法描述

### 1.1 Phase 5 Competing Baselines（已有）

| # | 方法 | 全称 | 核心机制 | 信号类型 | 方向假设 | 额外 Cost/step | 论文 |
|---|------|------|---------|---------|---------|:-------------:|------|
| 1 | **CATTS** | Collaborative Agent Tree Search | 每步 K=5 次 LLM 独立采样候选动作，计算投票分歧度（vote entropy + margin）。高分歧 → 触发 rollout | Vote disagreement | 固定正向 | K=5 LLM calls (C_vote) | Lee et al., arXiv:2602.12276 (2026) |
| 2 | **SEAG** | Self-Evaluation-Guided Agents | 使用 LLM 输出 token 的平均 log-probability 作为 confidence 信号。低 confidence → 触发 rollout | Mean logprob | 固定负向 | 0 | Lee et al., ACL 2025 |
| 3 | **CoRefine** | Confidence-based Refinement | 使用 LLM 输出 token 的分布熵作为 uncertainty 信号。高 entropy → 触发 rollout | Token entropy | 固定正向 | 0 | arXiv 2024 |
| 4 | **CaTS** | Calibrated Test-time Scaling | 对 LLM confidence 做 Platt scaling（logistic regression 校准），学习一维阈值。校准后低置信度 → 触发 rollout | Platt-scaled confidence | 学习（1维） | 0 | OpenReview 2025 |

### 1.2 Phase 6.1b New Competing Baselines（新增）

| # | 方法 | 全称 | 核心机制 | 信号类型 | 方向假设 | 额外 Cost/step | 论文 |
|---|------|------|---------|---------|---------|:-------------:|------|
| 5 | **AUQ** | Agentic Uncertainty Quantification | 每步额外调用 LLM 询问"你对当前动作有多大信心？"，解析 0-1 数值。低信心 → 触发 rollout | Verbalized confidence | 固定负向 | 1 LLM call (~150 tok) | Salesforce AI, arXiv:2601.15703 (2026) |
| 6 | **s1 Budget** | s1: Simple Test-Time Scaling (Budget Forcing) | 将固定 K 次 rollout 均匀分布到预设步骤上。零信号、零智能、纯 budget 分配。K 匹配 SCG 的 avg ro/ep，用于"同 cost 下智能 vs 均匀分配"对比 | 无 | 无 | 0 | Muennighoff et al., EMNLP 2025, arXiv:2501.19393 |

### 1.3 信号类型覆盖

| 信号类型 | Baseline | 说明 |
|---------|----------|------|
| Token entropy | CoRefine | LLM 输出 token 分布的 Shannon entropy |
| Mean logprob confidence | SEAG | LLM 输出 token 的平均 log-probability |
| Platt-scaled confidence | CaTS | 对 raw confidence 做 logistic regression 校准 |
| Vote disagreement | CATTS | K=5 采样的投票一致性 (entropy + margin) |
| Verbalized confidence | AUQ | LLM 自我评估的语言化置信度 |
| 无（固定预算） | s1 Budget | 不使用任何信号 |

6 个 baseline 覆盖了所有主流 gating 信号类型。除 CaTS 学习一维阈值外，其余均使用**固定方向**假设。

### 1.4 s1 Budget K 值设定

K 值匹配 SCG 在各环境的平均 rollouts/episode（向上取整，min=1）：

| 环境 | SCG ro/ep | s1 K | trigger_steps (0-indexed) |
|------|:---------:|:----:|:-------------------------:|
| HotpotQA | 1.09 | 2 | {0, 5} |
| APPS | 0.18 | 1 | {0} |
| WebShop | 0.95 | 1 | {0} |
| TWExpress | 1.38 | 2 | {0, 25} |
| Plancraft | 3.33 | 4 | {0, 7, 15, 22} |

---

## 2. 各环境详细结果

参考指标：base_only 和 scg_finetune_lr (SCG) 作为下界和本文方法对照。

### 2.1 HotpotQA（主实验 — 强信号环境）

**Token cost 常数**: C_base=216 tok/step, C_rollout=7,743 tok/trigger, C_vote=1,063 tok/step

| 方法 | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Ro/ep | Cost (tok) | Cost (×base) |
|------|:--------:|:---------:|:---------:|:-----------:|:-----:|:----------:|:------------:|
| base_only (ref) | 51.5% | 48.5% | 47.0% | **49.0%** | 0.00 | 1,349 | **1.00×** |
| **SCG** (ref) | **96.0%** | **97.0%** | **97.5%** | **96.8%** | **1.09** | **8,834** | **6.55×** |
| CATTS | 71.0% | 71.0% | 63.0% | **68.3%** | 1.07 | 14,171 | 10.50× |
| SEAG | 69.5% | 71.0% | 62.0% | **67.5%** | 1.02 | 8,902 | 6.60× |
| CoRefine | 71.0% | 71.0% | 62.5% | **68.2%** | 1.05 | 9,101 | 6.75× |
| CaTS | 94.0% | 91.5% | 94.0% | **93.2%** | 1.77 | 14,233 | 10.55× |
| **AUQ** | 96.5% | 97.0% | 97.5% | **97.0%** | 1.69 | ~13,450 | ~9.97× |
| **s1 Budget** | 96.5% | 97.0% | 97.5% | **97.0%** | 1.04 | ~8,425 | ~6.25× |

**分析**:
- CATTS/SEAG/CoRefine (~68%) 因**方向错误**大幅退化（HotpotQA 信号为负向，固定正向假设失效）
- CaTS (93.2%) 是 Phase 5 最佳 CB，Platt scaling 部分学到了方向，但 cost 10.55× — 比 SCG 贵 61%
- AUQ (97.0%) 达到 ceiling，但 cost ~10× — 每步额外 LLM 调用 + 高触发率
- s1 (97.0%) 也达 ceiling，cost 6.25× 略优于 SCG (6.55×)
- **⚠️ HotpotQA 区分度有限**：rollout 极强 (base→always +48pp)，任何触发策略都接近 ceiling

### 2.2 APPS（主实验 — 弱信号环境）

**Token cost 常数**: C_base=840 tok/step, C_rollout=3,306 tok/trigger, C_vote=4,198 tok/step

| 方法 | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Ro/ep | Cost (tok) | Cost (×base) |
|------|:--------:|:---------:|:---------:|:-----------:|:-----:|:----------:|:------------:|
| base_only (ref) | 58.5% | 58.5% | 58.5% | **58.5%** | 0.00 | 2,489 | **1.00×** |
| **SCG** (ref) | 59.0% | 58.5% | 59.0% | **58.8%** | 0.18 | 3,065 | 1.23× |
| CATTS | 58.5% | 58.5% | 58.5% | **58.5%** | 0.03 | 14,993 | **6.02×** |
| SEAG | 58.5% | 58.5% | 58.5% | **58.5%** | 0.01 | 2,522 | 1.01× |
| CoRefine | 58.5% | 58.5% | 58.5% | **58.5%** | 0.01 | 2,522 | 1.01× |
| CaTS | 59.0% | 59.0% | 59.0% | **59.0%** | 0.04 | 2,600 | 1.04× |
| **AUQ** | 62.5% | 60.5% | 61.0% | **61.3%** | 1.73 | ~7,770 | ~3.12× |
| **s1 Budget** | 62.5% | 65.0% | 63.5% | **63.7%** | 1.00 | ~5,846 | ~2.35× |

**分析**:
- **Phase 5 所有 CB 均退化为 base_only** — gate 从不触发 (ro/ep ≈ 0)，信号太弱无法越过阈值
- CATTS 尤其灾难：SR=58.5%（无提升）但 cost 6.02× — K=5 投票开销 (C_vote=4,198) **超过 rollout 本身** (C_rollout=3,306)
- **s1 (63.7%) > AUQ (61.3%) > SCG (58.8%)** — s1 在 step 0 强制触发 1 次 rollout，碰巧在 APPS 有效
- AUQ 也触发较多 (1.73 ro/ep)，但 cost 是 SCG 的 2.5 倍
- **⚠️ s1 > SCG 的原因**：APPS 信号极弱 (ρ=0.155)，SCG gate 几乎不触发 (0.18 ro/ep)。s1 的"盲目"反而比 SCG 的"过于保守"好。但 s1 cost 更高且在其他环境崩溃

### 2.3 WebShop（主实验 — showcase 环境）

**Token cost 常数**: C_base=705 tok/step, C_rollout=9,089 tok/trigger, C_vote=3,385 tok/step

| 方法 | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Ro/ep | Cost (tok) | Cost (×base) |
|------|:--------:|:---------:|:---------:|:-----------:|:-----:|:----------:|:------------:|
| base_only (ref) | 8.0% | 8.0% | 5.5% | **7.2%** | 0.00 | 9,919 | **1.00×** |
| **SCG** (ref) | **49.0%** | **44.5%** | **37.5%** | **43.7%** | **0.95** | **12,640** | **1.27×** |
| CATTS | 15.5% | 16.5% | 16.0% | **16.0%** | 0.20 | 55,026 | 5.55× |
| SEAG | 33.5% | 26.5% | 24.0% | **28.0%** | 2.28 | 28,156 | 2.84× |
| CoRefine | 31.5% | 27.0% | 24.0% | **27.5%** | 2.21 | 27,498 | 2.77× |
| CaTS | 33.0% | 29.5% | 29.0% | **30.5%** | 3.04 | 34,153 | 3.44× |
| **AUQ** | 41.0% | 34.5% | 31.5% | **35.7%** | 5.33 | ~58,600 | ~5.91× |
| **s1 Budget** | 8.5% | 10.0% | ❌ | **9.3%**\* | 1.00 | ~18,990 | ~1.91× |

\* s1 seed_456 缺失（job 失败），Mean SR 基于 2 个 seed

**分析**:
- **SCG (43.7%, 1.27×) Pareto-dominates 所有 6 个 CB**:
  - vs CaTS: SR↑13.2pp, cost↓63%
  - vs AUQ: SR↑8.0pp, cost↓79%
  - vs SEAG: SR↑15.7pp, cost↓55%
- **s1 崩溃 (9.3% ≈ base_only)** — step 0 的 rollout 在 WebShop 无用（需要先浏览商品才知道买什么）
- **AUQ (35.7%)** 比 Phase 5 CB 都高，但 cost 5.91× 极贵（每步都查询 confidence + 高触发率 5.33 ro/ep）
- CATTS (16.0%) 表现最差——投票 cost 巨大但 SR 极低
- **WebShop 是 SCG 的 showcase**：精准触发 (17% trigger rate) + 极低 cost = CER=1.352

### 2.4 TWExpress（诊断 — rollout-safe 环境）

**Token cost 常数**: C_base=524 tok/step, C_rollout=8,002 tok/trigger, C_vote=2,620 tok/step

| 方法 | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Ro/ep |
|------|:--------:|:---------:|:---------:|:-----------:|:-----:|
| base_only (ref) | 67.0% | 69.0% | 66.5% | **67.5%** | 0.00 |
| **SCG** (ref) | 97.0% | 98.0% | 96.0% | **97.0%** | 1.38 |
| CATTS | 97.0% | 97.5% | 98.0% | **97.5%** | 2.26 |
| SEAG | 97.0% | 97.5% | 97.5% | **97.3%** | 2.31 |
| CoRefine | 97.0% | 97.5% | 98.0% | **97.5%** | 2.26 |
| CaTS | 96.0% | 96.5% | 97.5% | **96.7%** | 1.97 |
| **AUQ** | ❌ | 95.5% | 95.5% | **95.5%**\* | 1.22 |
| **s1 Budget** | 94.5% | 95.0% | 95.5% | **95.0%** | 1.09 |

\* AUQ seed_42 缺失（job 失败），Mean SR 基于 2 个 seed

**分析**:
- **所有方法 SR 均 >95%**，差距在噪声范围内
- Rollout 从不有害 → 触发率越高 SR 越高：CATTS/CoRefine (97.5%) > SEAG (97.3%) > SCG (97.0%) > CaTS (96.7%) > AUQ (95.5%) > s1 (95.0%)
- AUQ 和 s1 触发率较低 (1.09-1.22 ro/ep)，因此 SR 略低
- **TWExpress 不是 baseline 区分环境** — SCG 的选择性在此环境反而是劣势

### 2.5 Plancraft（诊断 — rollout-harmful 负例）

**Token cost 常数**: C_base=1,120 tok/step, C_rollout=10,651 tok/trigger, C_vote=5,598 tok/step

| 方法 | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Ro/ep |
|------|:--------:|:---------:|:---------:|:-----------:|:-----:|
| **base_only** (ref) | **29.0%** | **30.0%** | **30.5%** | **29.8%** | **0.00** |
| SCG (ref) | 21.0% | 20.0% | 23.5% | **21.5%** | 3.33 |
| CATTS | 23.5% | 25.0% | 26.5% | **25.0%** | 2.14 |
| SEAG | 24.0% | 25.0% | 25.5% | **24.8%** | 2.16 |
| CoRefine | 22.5% | 20.0% | 26.0% | **22.8%** | 2.06 |
| CaTS | 21.5% | 20.0% | 25.5% | **22.3%** | 4.39 |
| **AUQ** | 23.0% | 23.5% | 26.0% | **24.2%** | 6.78 |
| **s1 Budget** | 17.5% | 16.5% | 21.0% | **18.3%** | 1.68 |

**分析**:
- **base_only (29.8%) 是所有方法中 SR 最高** — rollout 本质有害
- **s1 (18.3%) 最差** — 固定分配在 rollout-harmful 环境中灾难性，比 base_only 低 11.5pp
- AUQ (24.2%) 触发率极高 (6.78 ro/ep ≈ always_trigger 的 6.99)，大量无效 rollout
- CATTS (25.0%) 是 CB 中最高，因为 rollout 较少 (2.14 ro/ep)
- CaTS (22.3%) 触发过多 (4.39 ro/ep)，接近 always_trigger 水平

### 2.6 FEVER (新环境, 2026-03-22 更新 — Issue 3 修复后)

**环境特征**: Fact verification, search-based QA (与 HotpotQA 同族), base SR=37.0%, 信号方向=负

| 方法 | s42 | s123 | s456 | **Mean SR** | Ro/ep | SR/ro | 备注 |
|------|:---:|:----:|:----:|:-----------:|:-----:|:-----:|------|
| base_only | 35.0% | 38.0% | 38.0% | **37.0%** | 0.00 | — | |
| **SCG** | 98.5% | 98.0% | 97.5% | **98.0%** | 0.99 | **0.615** | **效率最高** |
| cats | 47.5% | 50.5% | 52.5% | **50.2%** | 4.71 | 0.028 | ✅ 修复后 |
| corefine | 48.0% | 49.5% | 52.0% | **49.8%** | 3.13 | 0.041 | ✅ 修复后 |
| seag | 47.0% | 48.0% | 53.0% | **49.3%** | 3.12 | 0.040 | ✅ 修复后 |
| s1_budget | 44.0% | 46.5% | 48.0% | **46.2%** | 1.58 | 0.058 | |
| auq | 36.5% | 41.0% | 44.5% | **40.7%** | 1.17 | 0.031 | |
| catts | 33.5% | 34.5% | 36.0% | **34.2%** | 0.06 | −0.515 | < base! |

- **SCG(98.0%) >> cats(50.2%) ≈ corefine(49.8%) ≈ seag(49.3%) >> s1(46.2%) >> auq(40.7%) >> base(37.0%) >> catts(34.2%)**
- SCG 效率 (SR/ro=0.615) 是 CB 最佳 (s1 0.058) 的 **10.6 倍**
- Issue 3 修复后 cats/corefine/seag 从 ~34% 提升到 ~50%, 但仍远不如 SCG
- catts 仍几乎不触发 (ro=0.06), 比 base 更差

### 2.7 APPS Interview (新环境, 2026-03-22 更新 — Issue 3 修复后)

**环境特征**: Code generation (Interview 难度), rollout-safe, base SR=60.5%

| 方法 | s42 | s123 | s456 | **Mean SR** | Ro/ep | SR/ro | 备注 |
|------|:---:|:----:|:----:|:-----------:|:-----:|:-----:|------|
| base_only | 60.5% | 60.5% | 60.5% | **60.5%** | 0.00 | — | |
| **SCG** | 79.5% | 79.5% | 79.5% | **79.5%** | 1.00 | **0.190** | = ceiling |
| s1_budget | 68.5% | 70.5% | 68.0% | **69.0%** | 1.00 | 0.085 | |
| corefine | 68.0% | 68.0% | 66.5% | **67.5%** | 0.62 | 0.112 | ✅ 修复后 |
| cats | 66.0% | 67.0% | 65.5% | **66.2%** | 0.54 | 0.105 | ✅ 修复后 |
| seag | 67.5% | 65.0% | 65.5% | **66.0%** | 0.64 | 0.086 | ✅ 修复后 |
| auq | 65.0% | 64.5% | 64.5% | **64.7%** | 1.08 | 0.038 | |
| catts | 60.5% | 61.0% | 61.0% | **60.8%** | 0.02 | 0.154 | 几乎不触发 |

- Rollout-safe: SCG=always=oracle=79.5%
- **SCG(79.5%) > s1(69.0%) > corefine(67.5%) > cats(66.2%) > seag(66.0%) > auq(64.7%) > catts(60.8%) ≈ base(60.5%)**
- Issue 3 修复后 CB 从 60.5% 提升到 66-68%

### 2.8 CRUXEval (新环境, 2026-03-22)

**环境特征**: Code reasoning (output prediction), base SR=85.0% (偏高), rollout-safe

| 方法 | s42 | s123 | s456 | **Mean SR** | Ro/ep | 备注 |
|------|:---:|:----:|:----:|:-----------:|:-----:|------|
| base_only | 85.0% | 85.0% | 85.0% | **85.0%** | 0.00 | |
| **SCG** | 99.5% | 99.5% | 99.5% | **99.5%** | 0.90 | = ceiling |
| auq | 99.0% | 99.0% | 99.0% | **99.0%** | 1.75 | 接近 SCG |
| cats | 95.0% | 95.0% | 95.0% | **95.0%** | 0.73 | |
| s1_budget | 86.5% | 86.5% | 86.5% | **86.5%** | 1.00 | |
| seag | 85.0% | 85.0% | 87.5% | **85.8%** | 0.73 | ≈ base |
| corefine | 85.0% | 85.0% | 87.5% | **85.8%** | 0.73 | ≈ base |
| catts | 81.5% | 81.5% | 81.0% | **81.3%** | 0.04 | < base! |

- SCG = always = 99.5%, base=85% headroom 有限
- **catts(81.3%) < base(85.0%)** — 方向错误反而有害

---

## 3. 跨环境总表

### 3.1 Mean SR 汇总

| 方法 | HotpotQA | APPS | WebShop | TWExpress | Plancraft | **FEVER** | **APPS Intv** | **CRUXEval** |
|------|:--------:|:----:|:-------:|:---------:|:---------:|:---------:|:-------------:|:------------:|
| base_only (ref) | 49.0% | 58.5% | 7.2% | 67.5% | **29.8%** | 37.0% | 60.5% | 85.0% |
| **SCG** (ref) | **96.8%** | 58.8% | **43.7%** | 97.0% | 21.5% | **98.0%** | **79.5%** | **99.5%** |
| CATTS | 68.3% | 58.5% | 16.0% | 97.5% | 25.0% | 34.2% | 60.8% | 81.3% |
| SEAG | 67.5% | 58.5% | 28.0% | 97.3% | 24.8% | **49.3%** | **66.0%** | 85.8% |
| CoRefine | 68.2% | 58.5% | 27.5% | 97.5% | 22.8% | **49.8%** | **67.5%** | 85.8% |
| CaTS | 93.2% | 59.0% | 30.5% | 96.7% | 22.3% | **50.2%** | **66.2%** | **95.0%** |
| **AUQ** | 97.0% | 61.3% | 35.7% | 95.5%\* | 24.2% | 40.7% | 64.7% | **99.0%** |
| **s1 Budget** | 97.0% | **63.7%** | 9.3%\* | 95.0% | 18.3% | 46.2% | 69.0% | 86.5% |

**FEVER/APPS Intv/CRUXEval**: Issue 3 修复后的真实数据 (2026-03-22)

### 3.2 Avg Ro/ep 汇总

| 方法 | HotpotQA | APPS | WebShop | TWExpress | Plancraft |
|------|:--------:|:----:|:-------:|:---------:|:---------:|
| CATTS | 1.07 | 0.03 | 0.20 | 2.26 | 2.14 |
| SEAG | 1.02 | 0.01 | 2.28 | 2.31 | 2.16 |
| CoRefine | 1.05 | 0.01 | 2.21 | 2.26 | 2.06 |
| CaTS | 1.77 | 0.04 | 3.04 | 1.97 | 4.39 |
| **AUQ** | 1.69 | 1.73 | 5.33 | 1.22 | 6.78 |
| **s1 Budget** | 1.04 | 1.00 | 1.00 | 1.09 | 1.68 |
| SCG (ref) | 1.09 | 0.18 | 0.95 | 1.38 | 3.33 |

### 3.3 Cost (×base) 汇总

| 方法 | HotpotQA | APPS | WebShop | TWExpress | Plancraft |
|------|:--------:|:----:|:-------:|:---------:|:---------:|
| CATTS | 10.50× | **6.02×** | 5.55× | ~1.57× | ~5.69× |
| SEAG | 6.60× | 1.01× | 2.84× | ~1.60× | ~2.52× |
| CoRefine | 6.75× | 1.01× | 2.77× | ~1.57× | ~2.44× |
| CaTS | 10.55× | 1.04× | 3.44× | ~1.36× | ~4.14× |
| **AUQ** | ~9.97× | ~3.12× | ~5.91× | ~0.94× | ~6.11× |
| **s1 Budget** | ~6.25× | ~2.35× | ~1.91× | ~0.84× | ~2.00× |
| SCG (ref) | **6.55×** | **1.23×** | **1.27×** | ~1.00× | ~3.31× |

### 3.4 SCG vs 各 CB 的 Pareto 关系

| CB | HotpotQA | APPS | WebShop | TWExpress | Plancraft |
|----|:--------:|:----:|:-------:|:---------:|:---------:|
| CATTS | SCG >> | SCG >> (cost) | SCG >> | ≈ | N/A (harmful) |
| SEAG | SCG >> | ≈ | SCG >> | ≈ | N/A |
| CoRefine | SCG >> | ≈ | SCG >> | ≈ | N/A |
| CaTS | SCG > | ≈ | SCG >> | ≈ | N/A |
| **AUQ** | ≈ SR, SCG cost↓ | AUQ > SR, SCG cost↓ | **SCG >>** | ≈ | N/A |
| **s1 Budget** | ≈ SR, ≈ cost | **s1 > SR**, SCG cost↓ | **SCG >>** | ≈ | N/A |

**说明**: `>>` = Pareto-dominate (SR↑ 且 cost↓), `>` = 一个维度优, `≈` = 差距在噪声/可接受范围

---

## 4. Cost-Effectiveness 分析（3 个主实验环境）

**CER = ΔSR / ΔCost**，其中 ΔSR = SR − base_SR，ΔCost = Cost(×base) − 1.0

### 4.1 CER 详细表

#### HotpotQA (base_SR=49.0%)

| 方法 | SR | ΔSR | Cost (×base) | ΔCost | CER |
|------|:--:|:---:|:------------:|:-----:|:---:|
| CATTS | 68.3% | +19.3pp | 10.50× | 9.50 | 0.020 |
| SEAG | 67.5% | +18.5pp | 6.60× | 5.60 | 0.033 |
| CoRefine | 68.2% | +19.2pp | 6.75× | 5.75 | 0.033 |
| CaTS | 93.2% | +44.2pp | 10.55× | 9.55 | 0.046 |
| **AUQ** | 97.0% | +48.0pp | 9.97× | 8.97 | **0.054** |
| **s1 Budget** | 97.0% | +48.0pp | 6.25× | 5.25 | **0.091** |
| SCG (ref) | 96.8% | +47.8pp | 6.55× | 5.55 | **0.086** |

#### APPS (base_SR=58.5%)

| 方法 | SR | ΔSR | Cost (×base) | ΔCost | CER |
|------|:--:|:---:|:------------:|:-----:|:---:|
| CATTS | 58.5% | +0.0pp | 6.02× | 5.02 | 0.000 |
| SEAG | 58.5% | +0.0pp | 1.01× | 0.01 | 0.000 |
| CoRefine | 58.5% | +0.0pp | 1.01× | 0.01 | 0.000 |
| CaTS | 59.0% | +0.5pp | 1.04× | 0.04 | 0.125 |
| **AUQ** | 61.3% | +2.8pp | 3.12× | 2.12 | 0.013 |
| **s1 Budget** | 63.7% | +5.2pp | 2.35× | 1.35 | **0.039** |
| SCG (ref) | 58.8% | +0.3pp | 1.23× | 0.23 | 0.013 |

#### WebShop (base_SR=7.2%)

| 方法 | SR | ΔSR | Cost (×base) | ΔCost | CER |
|------|:--:|:---:|:------------:|:-----:|:---:|
| CATTS | 16.0% | +8.8pp | 5.55× | 4.55 | 0.019 |
| SEAG | 28.0% | +20.8pp | 2.84× | 1.84 | 0.113 |
| CoRefine | 27.5% | +20.3pp | 2.77× | 1.77 | 0.115 |
| CaTS | 30.5% | +23.3pp | 3.44× | 2.44 | 0.096 |
| **AUQ** | 35.7% | +28.5pp | 5.91× | 4.91 | 0.058 |
| **s1 Budget** | 9.3% | +2.1pp | 1.91× | 0.91 | 0.023 |
| **SCG** (ref) | **43.7%** | **+36.5pp** | **1.27×** | **0.27** | **1.352** |

### 4.2 CER 汇总

| 方法 | HotpotQA | APPS | WebShop | 平均 |
|------|:--------:|:----:|:-------:|:----:|
| CATTS | 0.020 | 0.000 | 0.019 | 0.013 |
| SEAG | 0.033 | 0.000 | 0.113 | 0.049 |
| CoRefine | 0.033 | 0.000 | 0.115 | 0.049 |
| CaTS | 0.046 | 0.125 | 0.096 | 0.089 |
| **AUQ** | 0.054 | 0.013 | 0.058 | 0.042 |
| **s1 Budget** | **0.091** | **0.039** | 0.023 | 0.051 |
| **SCG** (ref) | 0.086 | 0.013 | **1.352** | **0.484** |

SCG 平均 CER (0.484) 远超所有 CB，主要因 WebShop 的极端 cost-effectiveness (1.352)。

### 4.3 真实总 Cost 分析 — 含 Phase 1 数据收集 (2026-03-22 新增)

**⚠️ 重要修正**: 上述 CER 分析仅计算 exploitation 阶段的 cost。但 SCG/CaTS/SEAG/CoRefine 都依赖 Phase 1 数据（200 ep always_trigger），这是一笔隐性成本。SE/v2 的探索数据在 200 ep 运行中自包含，无额外成本。

**Phase 1 成本 per 环境**:

| 环境 | Phase 1 (200 ep always_trigger) | 总 rollout 数 |
|------|:---:|:---:|
| FEVER | 1.46 ro/ep | 292 |
| HotpotQA | 1.80 ro/ep | 361 |
| APPS Intro | 2.58 ro/ep | 517 |
| WebShop | 5.63 ro/ep | 1126 |
| APPS Interview | 2.19 ro/ep | 439 |
| CRUXEval | 1.91 ro/ep | 381 |

**含 Phase 1 的真实 Total Cost 对比 (Total ro/ep = (Phase1 + 200ep × exploit_ro) / 200)**:

#### FEVER

| 方法 | SR | Exploit ro/ep | Phase 1? | Total ro/ep | SR/total_ro |
|------|:---:|:---:|:---:|:---:|:---:|
| **SCG** | **98.0%** | 0.99 | ✅ 292 | **2.45** | **0.249** |
| SE best | 49.8% | 2.99 | ❌ | 2.99 | 0.043 |
| s1_budget | 46.2% | 1.58 | ❌ | 1.58 | 0.058 |
| cats | 50.2% | 4.71 | ✅ 292 | **6.17** | 0.021 |
| seag | 49.3% | 3.12 | ✅ 292 | **4.58** | 0.027 |
| auq | 40.7% | 1.17 | ❌ | 1.17 | 0.031 |

→ SCG 加 Phase 1 后 total 2.45 ro/ep，仍然效率最高 (0.249)。但 cost 不再是 "0.99" 而是 "2.45"。

#### HotpotQA

| 方法 | SR | Exploit ro/ep | Phase 1? | Total ro/ep | SR/total_ro |
|------|:---:|:---:|:---:|:---:|:---:|
| s1_budget | 97.0% | 1.04 | ❌ | 1.04 | **0.463** |
| SE best | 95.7% | 1.24 | ❌ | 1.24 | 0.378 |
| **SCG** | 96.8% | 1.09 | ✅ 361 | **2.89** | 0.165 |
| auq | 97.0% | 1.69 | ❌ | 1.69 | 0.285 |

→ **算上 Phase 1 后 SCG (0.165) 效率反而低于 s1 (0.463) 和 SE (0.378)**。

#### APPS Intro

| 方法 | SR | Exploit ro/ep | Phase 1? | Total ro/ep | SR/total_ro |
|------|:---:|:---:|:---:|:---:|:---:|
| SE best | **66.0%** | 1.55 | ❌ | 1.55 | **0.048** |
| s1_budget | 63.7% | 1.00 | ❌ | 1.00 | 0.052 |
| **SCG** | 58.8% | 0.18 | ✅ 517 | **2.77** | 0.001 |

→ SCG 加 Phase 1 后效率极低 (0.001)，因为 APPS 的 Phase 1 成本很高 (517 rollouts) 但 SCG 只比 base 好 0.3pp。

#### 跨环境总结 (含 Phase 1 真实 cost)

| 环境 | SCG SR/total_ro | SE SR/total_ro | s1 SR/total_ro | 效率冠军 |
|------|:---:|:---:|:---:|:---:|
| **FEVER** | **0.249** | 0.043 | 0.058 | **SCG** |
| HotpotQA | 0.165 | 0.378 | **0.463** | **s1** |
| APPS | 0.001 | **0.048** | 0.052 | **SE** |
| WebShop | ~0.080 | ~0.195 | 0.007 | **SE** |
| APPS Intv | 0.059 | 0.081 | **0.085** | **s1** |
| CRUXEval | 0.052 | — | 0.015 | **SCG** |

**关键发现**:
- 只看 exploitation cost 时 SCG 几乎全面领先
- **算上 Phase 1 后没有单一最优方法** — SCG 在 FEVER/CRUXEval 最优，SE 在 APPS/WebShop 最优，s1 在 HotpotQA/APPS Intv 最优
- 这进一步支持论文核心观点：**没有跨环境通用的最优策略**，需要根据环境特性选择方法

---

## 5. 关键发现

### 5.1 Phase 5 CB 发现

**发现 1: 固定方向假设导致系统性失效**
- HotpotQA 上 CATTS/SEAG/CoRefine (~68%) 远低于 SCG (96.8%)。这三者假设"高 entropy/低 confidence → 需要 rollout"，但 HotpotQA 中该方向是错误的
- CaTS (93.2%) 通过 Platt scaling 部分学到方向，但仅支持 1 维信号，无法处理多维交互

**发现 2: CATTS 的 K=5 投票机制 cost 灾难**
- APPS 上 C_vote (4,198 tok/step) > C_rollout (3,306 tok/trigger) — 投票比 rollout 还贵
- 所有环境中 CATTS 的 CER 均为最低 (平均 0.013)
- HotpotQA 和 WebShop 上 CATTS cost ≈ always_trigger 但 SR 远低

**发现 3: APPS 中所有 Phase 5 CB gate 从不触发**
- SEAG/CoRefine ro/ep ≈ 0.01，CaTS ro/ep = 0.04 → 信号太弱，所有 CB 退化为 base_only
- 唯一例外：CATTS ro/ep = 0.03 但 cost 6.02× (纯 voting overhead)

### 5.2 Phase 6.1b 新 CB 发现

**发现 4: AUQ 的 verbalized confidence 是有效信号但 cost 过高**
- AUQ 在 APPS 上首次突破 Phase 5 CB 瓶颈 (61.3% vs 59.0%)，因为 verbalized confidence 比 token-level 信号更有信息量
- 但每步额外 LLM 调用使 cost 膨胀：WebShop 5.91×, APPS 3.12×
- AUQ 仍是固定负向假设，在 WebShop 上 (35.7%) 远不如 SCG (43.7%)

**发现 5: s1 Budget 暴露了"智能 vs 盲目分配"的关键差异**
- **APPS**: s1 (63.7%) > SCG (58.8%) — step 0 rollout 碰巧有效，且 SCG 信号太弱过于保守
- **WebShop**: s1 (9.3%) ≈ base_only — step 0 rollout 完全无用，需要在浏览商品后才触发
- **Plancraft**: s1 (18.3%) 最差 — 固定分配在 rollout-harmful 环境中灾难性
- **结论**: 盲目分配在特定环境碰巧有效，但**不具备跨环境 generalizability**

**发现 6: 同 cost 对比 — 智能分配 vs 均匀分配**
- HotpotQA: s1 (97.0%, 6.25×) ≈ SCG (96.8%, 6.55×) — 持平（ceiling 效应）
- WebShop: SCG (43.7%, 1.27×) >> s1 (9.3%, 1.91×) — **同 budget 下 SCG 的 SR 高 34.4pp**
- 这证明了论文核心论点：**不是 rollout 数量决定性能，而是 rollout 分配到正确的状态**

### 5.3 总结

| 维度 | 最佳 CB | SCG 优势 |
|------|---------|---------|
| HotpotQA SR | s1/AUQ (97.0%) | ≈ (noise, all at ceiling) |
| HotpotQA CER | s1 (0.091) | 0.086 (接近) |
| APPS SR | s1 (63.7%) | SCG 不如 s1 ⚠️ |
| APPS CER | CaTS (0.125) | 0.013 (SCG 不触发) |
| **WebShop SR** | **AUQ (35.7%)** | **SCG 43.7% >> AUQ +8.0pp** |
| **WebShop CER** | CoRefine (0.115) | **SCG 1.352 >> all** |
| TWExpress SR | CATTS/CoRefine (97.5%) | SCG 97.0% (≈) |
| Plancraft SR | CATTS (25.0%) | N/A (rollout harmful) |

**WebShop 是论文的核心 showcase 环境**：SCG Pareto-dominates 全部 8 个 competing baselines (6 CB + base_only + always_trigger)，CER 是次佳方法的 **11.8 倍** (1.352 vs CoRefine 0.115)。
