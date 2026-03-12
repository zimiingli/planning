# Phase 5：三路并行实验方案

**版本**：v3.0（2026-03-06）
**前置依赖**：Phase 0-4 全部完成，3 个有效环境（HotpotQA + APPS + WebShop）
**核心目标**：扩展环境 + 恢复自动 feature extraction + 完善论文数据
**论文标题**：Think at the Right Moment: Trajectory-Aware Compute Gating for LLM Agents
**核心叙事**：Step-level trajectory-aware gating + Adaptive Behavior Story

---

## 核心决策

1. **APPS P0 已解决** ✅
   - Phase 3 SR=65.0% 是虚高：gate 退化为 always_trigger（LR 系数全正 → 对所有状态预测 "should rollout"，RR=100%）
   - Phase 5 SR=0.588 是正确数据（gate 正常工作，RR=6%）
   - **论文使用 Phase 5 数据**，APPS narrative: gate 在低 headroom (+6%) 时正确保守

2. **P2-P4 Token Cost Analysis 已完成** ✅
   - Token cost constants 实测完成（C_base, C_rollout, C_vote × 3 envs）
   - 完整 SR vs Cost 表 + Pareto 分析 + CER + 5 个图表已生成
   - 核心发现：FRVC Pareto-dominates on HotpotQA + WebShop; CATTS vote cost > rollout cost on APPS

3. **Track 1 恢复：自动 Feature Extraction**
   - 目的：从手工 5-feature LR 升级为自动特征发现，提升 method novelty
   - 策略：回到之前的 hidden state probe 路线，已有 AUC=0.88 上界数据
   - 已暂停的 APPS hidden_state_mlp/lr：让其继续或重跑

4. **Track 2 新目标：5 个多步 Agentic 候选环境**
   - ScienceWorld + AppWorld 已终结（Both NO-GO: base_sr=0, always_sr=0）
   - Game of 24 / GSM8K 弃选（单轮推理，非 multi-step agentic，与论文 step-level gating 叙事不符）
   - 新候选：ALFWorld / InterCode-Bash / BabyAI / Jericho / WebArena-Lite
   - 目标：从 5 个候选中通过 GO/NO-GO 筛选 2-3 个，最终论文 5-6 个有效环境

## 优先级排序

| # | 任务 | 产出 | 阻塞什么 | 状态 |
|---|------|------|---------|------|
| **N1** | **扩展环境：5 候选 GO/NO-GO (ALFWorld/InterCode/BabyAI/Jericho/WebArena)** | 2-3 个新环境 | 论文环境多样性 | **NEXT — 最高优先** |
| **N2** | **恢复 Track 1：自动 feature extraction** | Method novelty 升级 | Method 贡献 | **NEXT — 第二优先** |
| **N3** | 论文写作（使用 v3.0 narrative） | 论文初稿 | 投稿 | 与 N1/N2 并行 |

## Token Cost 计算方法

每个方法的 total token cost per episode:
```
Token_cost = steps * C_base + steps * RR * C_rollout + steps * C_vote (CATTS only)
```

需要从 log 中提取的 3 个环境常数:
| 常数 | 含义 | 提取来源 |
|------|------|---------|
| C_base | 每步 base action 平均 token 数 | 任意 run 的 log |
| C_rollout | 每次 rollout 平均 token 数 | always_trigger run 的 log |
| C_vote | CATTS 每步 K=5 采样 token 数 | CATTS run 的 log |

Normalized Token Cost = method_tokens / base_only_tokens (base_only = 1.0x)

## Controlled Comparison 段落

```latex
\paragraph{Controlled Comparison.}
All adaptive triggering methods share the same base agent, optimizer $T$,
and rollout policy. The \emph{only} variable across methods is the gate
function $g(\cdot)$ that decides whether to invoke $T$ at each step.
This design isolates gating quality from optimizer quality.
We include two reference policies: \textsc{Always-Trigger} (upper bound
on SR when gating is removed) and \textsc{Oracle} (upper bound on gating
quality). Compute cost is measured in total tokens generated per episode,
normalized to the base agent cost (no triggering).
```

---

## Track 1：Automatic Feature Discovery — RESUMED

自动 feature extraction 作为 method novelty 的核心升级。

当前 NeurIPS 评估仅 30-40%，主要弱点是 method novelty (LR on 5 handcrafted features)。
自动 feature discovery 可将 method 贡献从 ⭐⭐ 升级到 ⭐⭐⭐⭐。
已有数据：hidden state AUC=0.88 (vs handcraft LR AUC=0.85)，但 gate 实际效果待验证。

**Track 1 优先级**：
1. Hidden state probe → gate 实际 SR 对比（已有 AUC 数据，需验证 end-to-end）
2. 如果 hidden state gate 有效 → 成为论文方法的升级路线
3. auto_feature_lr 已 NO-GO，不再尝试

### 动机

Phase 0-4 的 method novelty 评估：手工 5-feature + LR -> 2/5 stars.
三个弱点：(1) 环境特异 (2) 需 domain knowledge (3) 信号类型受限。
Track 1 目标：**自动发现 feature，替代手工 feature engineering**。

### Phase 5.0：共享基础设施 — HF Transformers Data Collection

**做什么**：替换 vLLM 为 HF Transformers，一次推理获取 text + logprobs + hidden_state。

**关键决策**：vLLM 无法获取 hidden states → HF Transformers 直接推理。
代价：比 vLLM 慢 ~3×（42min vs 14min per env），实验阶段完全可接受。

**输出**：每个环境一个 `.npz` 文件：
- `hidden_states`: (N_steps, 2560) — Qwen3-4B 最后一层 mean-pooled
- `state_texts`: list of str — 当前 state 文本
- `utilities`: (N_steps,) — U 值
- `signals`: (N_steps, n_signals) — 手工信号（保留用于对比）
- `token_entropies`: (N_steps,) — token entropy

**数据收集范围**：
- HotpotQA 200 ep × 3 seeds
- APPS 200 ep × 3 seeds
- WebShop 200 ep × 3 seeds
- （新 env 后续追加）

### Phase 5.1A：Hidden State Probe

**做什么**：用 LLM hidden state (d=2560) 训练 MLP → VOC estimate。

**架构**：2560 → 256 → 128 → 2（VOC_mean, VOC_logvar），~690K 参数。

**消融**：
| 变量 | 搜索范围 |
|------|---------|
| Pooling | mean / last_token / weighted_mean |
| Hidden layer | last / second-to-last / avg(last 4) |
| d_hidden | {64, 128, 256, 512} |
| 训练数据量 | {50, 100, 200, 500, 1000} |

**风险**：实验证据显示 env-state signals 一致强于 model-intrinsic signals。Hidden state 作为 model-intrinsic representation 的极端形式，可能无法有效提取环境特异信号。

**GO/NO-GO**：
- ✅ GO：VOC R² > 0.15 in ≥ 2/3 env
- ⚠️ MODERATE：R² ∈ (0.05, 0.15) → 有弱信号
- ❌ NO-GO：R² < 0.05 → hidden state 不编码 VOC

### Phase 5.1B：Text Embedding Probe

**做什么**：用 sentence-transformer 编码 state_text → MLP → VOC。

**模型候选**：
| 模型 | 维度 | 大小 | 速度 |
|------|------|------|------|
| all-MiniLM-L6-v2 | 384 | 22M | ~5ms |
| all-mpnet-base-v2 | 768 | 110M | ~15ms |

**优势**：不需要访问 LLM 内部（vLLM 兼容），轻量快速。

**GO/NO-GO**：
- ✅ GO：VOC R² > 0.10 in ≥ 2/3 env
- ❌ NO-GO：R² < 0.05

### Phase 5.1C：LLM Feature Design + Online Learning Gate

**做什么**：全自动 gate 构建 pipeline。核心设计理念：**关注点分离**。
- **LLM 负责语义理解**：读环境描述 + 格式样本 → 生成 `extract_features()` 代码
- **统计学习负责模式发现**：online learning 收集数据 → 自动发现 direction → 训练 LR gate

**全流程**：

```
Step 0: 采集格式样本（1 episode, 2-3 步, 零 LLM 调用）
  ↓
Step 1: LLM 生成 extract_features()（1 次 LLM 调用 per env）
  ↓
Step 2: 代码验证 + 修复循环（0-3 次额外 LLM 调用）
  ↓
Step 3: Online Explore（30 episodes, 随机 50% trigger, 收集 (features, U)）
  ↓
Step 4: Direction Discovery + Gate Training（Spearman ρ → LR, < 1s）
  ↓
Step 5: Online Deploy（170 episodes, LR gate + 每 10 ep retrain）
  ↓
Step 6: 评估（Deploy SR / CS / TES，排除 explore 阶段）
```

**GO/NO-GO**：
- ✅ GO：可执行 extract_features() + deploy SR ≥ 手工 LR in ≥ 2/3 env
- ⚠️ MODERATE：deploy SR 在手工 LR ±3pp 内
- ❌ NO-GO：无法生成可执行代码 / gate accuracy < 0.55

### Phase 5.2：三路对比实验

**实验矩阵**：

| Feature 来源 | Gate Model | 描述 |
|-------------|-----------|------|
| 手工 5 feature | LR | 当前最佳 (SCG-FineTune-LR) [已有] |
| 手工 5 feature | MLP | 手工 feature + 非线性 [新] |
| Hidden state (d=2560) | MLP | Track A [新] |
| Hidden state (d=2560) | LR (PCA→50d) | Track A 线性版 [新] |
| Text embedding (d=384/768) | MLP | Track B [新] |
| Text embedding (d=384/768) | LR | Track B 线性版 [新] |
| LLM-designed features | Online LR | Track C [新] |

**评估指标**：VOC R², Gate accuracy, SR, CS, TES（Track C 用 deploy phase SR）

### Phase 5.3：Winner Selection + 深度分析

**Winner 选择逻辑**：

```
IF any track SR ≥ hand-craft LR in ≥ 2/3 env:
    Winner → 论文主方法升级
ELIF any track ≈ hand-craft LR (±3pp):
    Winner → "matches without domain knowledge"
ELSE:
    回退 → 手工 feature + 三路作为 appendix analysis
```

**分析内容**：
- Feature source ablation table（论文 Section 5）
- Direction discovery 验证
- Track C 可解释性分析（生成代码审查 + 信号覆盖验证）
- 计算成本对比
- 学习曲线

### Track 1 Early Kill Switch

```
5.1A 结束后：
  hidden state R² < 0.05 in 所有 env → Track A NO-GO（Track B/C 继续）

5.1C 结束后：
  LLM 无法生成可执行代码 → Track C NO-GO（仅看 Track A/B）

5.2 offline 评估后：
  三路 offline gate accuracy 都 << 手工 LR → 三路 NO-GO，回退
```

---

## Track 2：New Environment Expansion

ScienceWorld + AppWorld 已终结 (Both NO-GO: base_sr=0, always_sr=0)。
Game of 24 / GSM8K 弃选（单轮推理，非 multi-step agentic，与论文 step-level gating 叙事不符）。
经调研，选定 5 个真正多步 agentic 候选环境。目标：从 5 候选中筛选 2-3 个 GO，最终论文 5-6 env。

### 5 个候选环境

| # | 候选 | 类型 | 步数/ep | 动作空间 | Reward | 社区使用度 | GO 概率 |
|---|------|------|--------|---------|--------|-----------|---------|
| 1 | **ALFWorld** | 文本化家务 (embodied) | 5-30 | 模板化 NL | Binary | AgentBench/AgentBoard/TALES/ReAct/Reflexion | 高 |
| 2 | **InterCode-Bash** | 交互式终端操作 | 5-15 | Bash 命令 | 执行匹配 | AgentBench/IPR (EMNLP'24) | 中高 |
| 3 | **BabyAI** | 网格导航 + NL 指令 | 10-50 | 7 离散动作 | Binary | AgentBoard | 高 |
| 4 | **Jericho (Zork1)** | 文本冒险游戏 | 50-200 | 自由 NL 命令 | Score | AgentBoard/TALES | 中低 |
| 5 | **WebArena-Lite** | 真实网页导航 | 8-12 | Web 动作 | Binary | CATTS 论文直接使用 | 中 |

### 各候选详情

**1. ALFWorld**（首推）
- 论文：Shridhar et al., ICLR 2021
- 任务：6 类家务（pick, clean, heat, cool, examine, put two），134 测试 task
- 动作示例："go to shelf 1", "take mug 1 from shelf 1", "put mug 1 in/on sinkbasin 1"
- 安装：`pip install alfworld`，纯文本模式，无需额外 GPU/Docker
- Rollout：文本模拟器，支持 env.step() 循环，可 save/load
- 小模型数据：7B ReAct ~30-60% SR，Qwen3-4B 预估 20-40%
- **为什么首推**：使用率最高的 multi-step agent benchmark 之一，与现有 3 env 零重叠（embodied household）

**2. InterCode-Bash**
- 论文：Yang et al., NeurIPS 2023
- 任务：在 Docker 容器内用 Bash 命令完成文件系统任务
- 动作：自由 Bash 命令，每步有 execution feedback (stdout/stderr)
- 安装：`pip install intercode-bench`，需 Docker
- 与 APPS 差异：APPS = 写完整程序一次提交；InterCode = 逐步在终端中操作、观察输出、调整策略（POMDP）
- **为什么选**：AgentBench 标配，展示 interactive coding vs one-shot coding 的差异

**3. BabyAI**
- 论文：Chevalier-Boisvert et al., ICLR 2019
- 任务：网格世界中跟随 NL 指令导航（"go to the red ball", "pick up the blue key and open the door"）
- 动作：7 个离散动作（turn left/right, forward, pickup, drop, toggle, done）
- 难度：19 个 level，可选择合适难度确保 base SR 在合理区间
- **为什么选**：空间推理 + 指令理解，完全不同于现有环境；难度可控 → GO 概率高

**4. Jericho (Zork1)**
- 论文：Hausknecht et al., 2020 (Microsoft)
- 任务：经典文本冒险游戏，自由文本命令交互
- 动作示例："open mailbox", "go north", "attack troll with sword"
- 特点：超长 horizon、部分可观测、组合爆炸动作空间
- **风险**：很难，GPT-4 都 struggle，Qwen3-4B 大概率 base SR 很低
- **为什么仍列入**：经典 benchmark (AgentBoard/TALES)，如果 GO 则是超长 horizon 极端测试

**5. WebArena-Lite**
- 论文：Zhou et al., ICLR 2024（165 tasks 精简版）
- 任务：在真实网站上完成操作（电商下单、论坛发帖、代码管理等）
- 动作：Web 动作（click, type, scroll 等）
- 特点：CATTS 论文 (arXiv:2602.12276) 的评估环境，可做 head-to-head 对比
- **风险**：需要 self-host 4 个 Docker 网站实例，搭建复杂；Qwen3-4B 可能 SR 极低

### GO/NO-GO 决策标准

每个候选跑 base_only + always_trigger 的预检（50 ep × 1 seed），确认：
1. base SR ∈ [10%, 85%]
2. Δ(always - base) > 3-5pp（有 rollout headroom）
3. 环境与现有 3 env 有足够差异化

### 建议执行顺序（按 GO 概率从高到低）

1. **ALFWorld** → 最可能 GO，搭建最快（pip install，纯文本）
2. **BabyAI** → 很可能 GO，难度可调
3. **InterCode-Bash** → 可能 GO，需 Docker
4. **WebArena-Lite** → 中等概率，搭建较重
5. **Jericho** → 概率最低，极端测试

每个 GO/NO-GO 预计 1-2 小时。

### 预期结果矩阵

```
乐观 (3-4 GO): ALFWorld + BabyAI + InterCode + WebArena → 6-7 env
现实 (2-3 GO): ALFWorld + BabyAI + InterCode            → 5-6 env
保守 (1-2 GO): ALFWorld + BabyAI                         → 5 env
最差 (0-1 GO): 仅 ALFWorld 或全部 NO-GO                   → 3-4 env
```

### 扩展后环境多样性矩阵（目标 5-6 env）

| 维度 | HotpotQA | APPS | WebShop | ALFWorld | InterCode-Bash | BabyAI |
|------|----------|------|---------|----------|---------------|--------|
| 领域 | 知识 QA | 算法编程 | 网购导航 | 家务操作 | 终端操作 | 网格导航 |
| 动作空间 | 小离散 | 代码生成 | 中等 NL | 模板化 NL | Bash 命令 | 7 离散 |
| 步数 | 2-8 | 1-5 | 3-15 | 5-30 | 5-15 | 10-50 |
| Reward | Binary (F1) | Binary (test) | Scalar (0-1) | Binary | 执行匹配 | Binary |
| 交互类型 | 搜索+推理 | 一次生成 | 浏览+选择 | 导航+操作物体 | 逐步执行+反馈 | 空间推理+指令 |

### 执行流水线

每个新环境遵循标准四步流水线：

#### Step 0：GO/NO-GO 预检（~1 hr per env, 50 ep × 1 seed）

```
├── 搭建环境（pip install + agent loop 适配）
├── 实现 Optimizer T
├── 跑 base_only 50 ep → 记录 base SR
├── 跑 always_trigger 50 ep → 记录 AT SR
└── 判断: base SR ∈ [10%, 85%] 且 Δ > 3-5pp → GO | 否则 NO-GO
```

#### Step 1：Signal Discovery（~2 hr per env, 200 ep × 1 seed）

```
├── 收集 200 ep × all steps 的 (σ, U) 数据
├── 计算 5 信号的 Spearman ρ, MI, η²
├── ⭐ 关键验证: token_entropy 方向是正还是负？→ C2 evidence
├── 确定最强信号 + 方向
└── 判断: ≥1 信号 MI > 0.05 或 |ρ| > 0.2 → GO | 否则信号太弱
```

#### Step 2：Full Experiments（~4-8 hr per env, 6+ methods × 3 seeds × 200 ep）

```
├── base_only, always_trigger, random_50, best_sigma_wrong
├── scg_finetune_lr（主方法）
├── oracle
└── 统计检验 + SR-CS Pareto 分析
```

#### Step 3：Competing Baselines 补跑

```
└── CATTS/SEAG/CoRefine/CaTS × 3 seeds = 12 runs per new env
```

### Signal 设计（通用模板）

每个新环境需设计 5 个 signals：
```python
signals = {
    'token_entropy':   # model-intrinsic（所有环境共用）
    'step_count':      # env-state (continuous)，所有环境共用
    'signal_3':        # env-specific (环境特有信号)
    'signal_4':        # env-specific
    'signal_5':        # env-specific
}
```

各环境特有信号候选：
- **ALFWorld**: room_type (categorical), inventory_count (continuous), task_progress (continuous)
- **InterCode-Bash**: error_count (continuous), command_type (categorical), output_length (continuous)
- **BabyAI**: distance_to_goal (continuous), carrying_object (binary), rooms_visited (continuous)
- **Jericho**: game_score (continuous), inventory_size (continuous), location_id (categorical)
- **WebArena-Lite**: page_type (categorical), num_actions_taken (continuous), dom_elements (continuous)

---

## Track 3：Competing Baselines — ✅ COMPLETE

Phase A (36 runs: 3 env × 4 baselines × 3 seeds) + P0 Calibrated (24 runs) 全部完成。
Token cost 数据提取完成，已转为 accuracy + token cost 报告框架。

### 4 个 Baseline 设计

所有 baselines 共享核心特征：**固定方向假设**（高 uncertainty/entropy/disagreement → trigger）。
统一控制变量：相同 optimizer T + 相同 agent + 相同 rollout policy，**唯一变量是 gate 逻辑**。

| Baseline | 来源 | 核心机制 | 方向假设 | 额外成本 |
|----------|------|---------|---------|---------|
| CATTS | arXiv:2602.12276 (2026) | K=5 vote entropy + margin | 高 disagreement → trigger | K=5 fwd/step |
| SEAG | ACL 2025 | token-level confidence | 低 confidence → trigger | ~0 |
| CoRefine | 2024 | output entropy | 高 entropy → trigger | ~0 |
| CaTS | OpenReview 2025 | Platt scaling calibrated confidence | 学 θ 但方向固定 | ~0 |

### 核心论点

1. 所有固定方向 baselines 在 HotpotQA（entropy 负方向）上系统性失败
2. CaTS（最强 calibrated baseline）跨环境不稳定
3. CATTS 额外 5× 推理成本，但方向假设限制性能
4. **只有 SCG 在所有环境上稳定**——因为它 **学** 方向而非 **假设** 方向
5. 新环境的 direction pattern 进一步验证 C2

---

## 时间线

```
=====================================================================
  Phase 5 v3.0 计划
  P0-P4 全部 DONE，聚焦扩展环境 + 自动特征
=====================================================================

--- 已完成 ---
  [P0] ✅ APPS P0 已解决: Phase 3 SR=0.650 是假阳性 (gate 退化为 always_trigger)
       Phase 5 SR=0.588 是正确数据
  [P1] ✅ WebShop scg Phase5 验证完成 (SR=0.437, RR=16.9%)
  [P2] ✅ Token cost 数据提取完成 (3 env 全部)
  [P3] ✅ Table 2 + Normalized Cost 完整填充
  [P4] ✅ Pareto figure + CER analysis 完成

--- 进行中 ---

[N1] 新环境扩展 (优先级最高)
  目标: 从 3 env 扩展到 5-6 env (5 个候选，预期 2-3 GO)
  候选 (按执行顺序):
    1. ALFWorld (embodied household, pip install, GO 概率高)
    2. BabyAI (grid navigation, 难度可调, GO 概率高)
    3. InterCode-Bash (interactive terminal, 需 Docker, GO 概率中高)
    4. WebArena-Lite (web navigation, 需 self-host, GO 概率中)
    5. Jericho/Zork1 (text adventure, 极端测试, GO 概率中低)
  步骤 (每个候选):
    0. 环境搭建 + agent loop 适配
    1. GO/NO-GO: base_only + always_trigger 50ep
    2. Signal Discovery: 200ep 收集 + Spearman/MI
    3. Full Experiments: SCG-LR + 6 methods × 3 seeds × 200ep
    4. Baselines 补跑 (CATTS/CaTS/SEAG/CoRefine)
    5. Token cost + Pareto 更新

[N2] 自动特征提取 (Track 1 恢复)
  目标: 用 hidden state / text embedding 自动提取 gate feature
  状态: 已有 probe 数据 (R2 up to 0.873)
  下一步:
    1. 设计 feature extractor pipeline
    2. 验证 auto feature 能否达到手工 feature 的 SR
    3. 如成功: 论文新增 "Auto Feature" 章节 (方法贡献)

[N3] 论文写作
  在 N1 完成后进入正式写作
  使用 VOC_PAPER_WRITING_GUIDE.md v3.0 框架
  核心叙事: step-level online gating + adaptive behavior
=====================================================================
```

---

## 最终产出

### 已完成核心产出 (✅ DONE)
- **Table 2**: SR + Normalized Token Cost, 3 env × all methods (HotpotQA / APPS / WebShop)
- **Figure (Pareto)**: SR vs Token Cost, 3 panels, Pareto frontier 标注
- **CER 分析**: Cost-Effectiveness Ratio 对比
- **Token Cost 数据**: 3 env 全部提取完成 (C_base, C_rollout, C_vote, avg_steps)
- **Main Claim 验证**: FRVC Pareto-dominates on HotpotQA + WebShop ✅

### 新增目标产出
- **扩展 Table 2**: 5-6 env × all methods (新增 ALFWorld / InterCode / BabyAI 等)
- **Adaptive Behavior 图**: RR vs Headroom 散点/柱状图 (5-6 env 数据点)
- **Auto Feature 章节**: 自动特征提取方法 + 对比手工特征的消融实验
- **Step-level vs Problem-level 对比表**: 与现有 ~46 篇 adaptive compute 论文的系统性差异

### 辅助产出 (已完成)
- 三层失败模型分析 (threshold mismatch / signal poverty / direction assumption)
- Cross-env AUC analysis (single signal 0.53 vs multi-signal 0.85 vs hidden state 0.88)
- CATTS K=5 hidden cost 暴露
- Calibrated vs uncalibrated baseline comparison

### Appendix 素材 (Track 1 数据)
- Hidden state probe results (R2 up to 0.873)
- Text embedding probe results (R2 up to 0.854)
- Feature source comparison (Phase 5.2 partial data)
- auto_feature_lr failure analysis

---

## 风险与回退

| 风险 | 影响 | 应对 | 状态 |
|------|------|------|------|
| scg 在 APPS 上不如 CaTS | APPS narrative | 诚实 limitation: signal poverty, ceiling gap only 6pp; adaptive behavior story 支撑 | **已接受** |
| **Qwen3-4B 在新 env 上 base SR 太低 (<10%)** | **环境扩展** | 5 个候选中只需 2-3 GO；ALFWorld/BabyAI GO 概率高 | **N1 风险** |
| **新 env 搭建复杂 (WebArena Docker)** | **时间成本** | 按 GO 概率排序执行，复杂环境排后 | **N1 风险** |
| **Auto feature 仍不如手工 feature** | **方法贡献** | 回退: 手工 feature + 分析为何 auto 失败 | **N2 风险** |
| **3 env 不够 NeurIPS** | **投稿** | 5 候选中预期 2-3 GO → 5-6 env; 最差仍可 4 env + 强 story | **核心风险** |

---

## Checklist

### 已完成任务 — ✅

- [x] **[P0] APPS scg_finetune_lr 不一致调查** → 已解决: Phase 3 是假阳性 (gate 退化为 always_trigger, RR=100%)
- [x] **[P1] WebShop scg_finetune_lr Phase5 验证** → 完成 (SR=0.437, RR=16.9%)
- [x] **[P2] Token cost 数据提取** → 3 env 全部完成
- [x] **[P3] Table 2 完整填充** → SR + Normalized Cost 表格完成
- [x] **[P4] Pareto Figure + CER** → 5 张图已生成
- [x] **[P4] Main claim 验证** → FRVC Pareto-dominates on HotpotQA + WebShop ✅

### Track 1: Feature Discovery — RESUMED
- [x] 5.0: HF Transformers 推理接口实现
- [x] 5.0: 3 env x 3 seeds 数据收集
- [x] 5.1A: Hidden State Probe 训练 + 消融 + GO/NO-GO -> GO (R2 up to 0.873)
- [x] 5.1B: Text Embedding Probe -> done (R2 up to 0.854)
- [x] 5.1C: LLM Feature Design -> NO-GO (auto_feature_lr SR=0.583 on HotpotQA)
- [x] 5.2 HotpotQA: 30/30 complete (all methods ~0.970 except auto_feature)
- [ ] **设计 auto feature extractor pipeline**
- [ ] **验证 auto feature vs 手工 feature 的 SR 对比**

### Track 2: New Environments (5 候选)
- [x] ScienceWorld: NO-GO (base_sr=0, always_sr=0)
- [x] AppWorld: NO-GO (base_sr=0, always_sr=0, 4h TIMEOUT)
- [x] Game of 24: 弃选 (单轮推理，非 multi-step agentic)
- [x] GSM8K: 弃选 (单轮推理，非 multi-step agentic)
- [ ] **ALFWorld GO/NO-GO** (优先级 1)
- [ ] **BabyAI GO/NO-GO** (优先级 2)
- [ ] **InterCode-Bash GO/NO-GO** (优先级 3)
- [ ] **WebArena-Lite GO/NO-GO** (优先级 4)
- [ ] **Jericho (Zork1) GO/NO-GO** (优先级 5)
- [ ] 通过环境的完整实验 (SCG + baselines + 3 seeds)

### Track 3: Competing Baselines — ✅ COMPLETE
- [x] CATTS/SEAG/CoRefine/CaTS gate 实现
- [x] Phase A: 36 runs (3 env x 4 baselines x 3 seeds) -> all complete
- [x] P0 Calibrated: 24 runs -> all complete
- [x] Token cost 数据提取 -> 3 env 完成

### 新优先级任务
- [ ] **[N1] 新环境扩展** (最高优先, 5 候选)
  - [ ] ALFWorld: 环境搭建 + GO/NO-GO (优先级 1)
  - [ ] BabyAI: 环境搭建 + GO/NO-GO (优先级 2)
  - [ ] InterCode-Bash: 环境搭建 + GO/NO-GO (优先级 3)
  - [ ] WebArena-Lite: 环境搭建 + GO/NO-GO (优先级 4)
  - [ ] Jericho (Zork1): 环境搭建 + GO/NO-GO (优先级 5)
  - [ ] 通过的环境: Signal Discovery + SCG-LR 部署 + 3 seeds
  - [ ] 通过的环境: Baselines 补跑
  - [ ] 更新 Table 2 + Pareto figure
  - [ ] 更新 adaptive behavior story (新增数据点)
- [ ] **[N2] 自动特征提取** (Track 1 恢复)
  - [ ] 设计 feature extractor pipeline
  - [ ] 验证 auto feature 能否达到手工 feature 的 SR
  - [ ] 如成功: 写入论文方法章节
- [ ] **[N3] 论文写作**
  - [x] VOC_PAPER_WRITING_GUIDE.md v3.0 → ✅ 已更新
  - [ ] 正式 LaTeX 初稿
  - [ ] Peer review + revision

### 已完成论文素材
- [x] Table 2: SR + Cost(xbase) 完整表格 (3 env x all methods)
- [x] Figure: SR vs Token Cost Pareto (5 张图)
- [x] CER 分析 + adaptive behavior 数据
- [x] 更新 VOC_PAPER_WRITING_GUIDE.md v3.0
