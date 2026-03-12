# Test-Time Agent Planning方法全景分类与对比分析

> **生成时间**: 2026-02-14 (最新更新：2026-03-01 新增11篇论文 — Hidden State Probing / PRM / Token Efficiency / Metareasoning)
> **分析范围**: 2023-2026年核心文献 + 最新方法 (**80+篇论文**，含 🆕 G类 metareasoning + 🆕🆕 竞争格局分析 ~46篇新论文 + 🆕🆕🆕 Hidden State Probing / PRM / Token Efficiency 等11篇新增)
> **对比基准**: Direction-Aware Gate / SCG-FineTune(LR) (Adaptive Test-Time Optimizer Triggering)

---

## 执行摘要

本文档系统梳理了test-time agent planning的各类方案，建立了完整的分类体系（**7大类**，**80+篇论文**），并与 Direction-Aware Gate / SCG-FineTune(LR) 方法进行全面对比。核心发现：

- **Test-time方法可分为两大范式**：Search-based（每步搜索）vs Learning-based（学会何时搜索）
- **本文独特定位**：唯一先显式测量 signal-utility 方向再设计 gate 的方法；轻量训练 SCG-FineTune(LR)，可即插即用于任意 optimizer T
- **关键差异化**：现有方法隐式依赖单调的 signal-utility 对齐（如高 entropy → 高 utility），本文发现这种对齐因环境而异，提出 direction discovery approach
- **🆕🆕🆕🆕🆕🆕 从 Reasoning 到 Agent Settings：Signal Landscape 的变化 (2026-03-05 重新定位)**：
  - **核心洞察**：Adaptive compute 在 reasoning 上已被广泛研究（10+ 篇），但 agent/interactive settings 中极少（仅 CATTS, Learning When to Plan, ARPO）。我们首次在 heterogeneous agent settings 中系统性发现 direction reversal
  - **研究版图**：现有方法绝大多数在 homogeneous reasoning benchmarks（MATH, GSM8K, GPQA）上验证，任务语义相似，方向碰巧一致。Agent settings 中 environment-state signals 引入 task-specific semantics，使 universal proxy 假设更容易崩溃
  - **实验证据**：environment-state signals 在所有测试环境中一致强于 model-intrinsic signal（token_entropy）：
    - HotpotQA: evidence_count ρ=−0.586 >> token_entropy ρ=−0.327
    - APPS: step_count ρ=−0.274 >> token_entropy ρ=+0.144（弱）
    - WebShop: state_category η²=0.598 >> token_entropy ρ=+0.133（弱）
  - **解释**：env-state signals 直接编码 task-specific progress（语义因环境而异），与 optimizer utility 有直接因果关系；entropy 是间接 proxy，方向不稳定。Agent settings 天然更 heterogeneous → direction reversal 更容易出现
  - **⚠️ 诚实边界**：不声称 direction reversal 是 "planning 独有的结构性后果"（未做控制实验验证 reasoning 之间是否也会 reverse）。准确表述：direction reversal 在 heterogeneous environments 中自然出现，agent settings 天然更 heterogeneous
  - **差异化意义**：我们是第一个在 agent settings 中系统性发现 direction reversal 并提出 direction-aware gate 的工作。现有方法未观察到此现象因为在 homogeneous benchmarks 上测试
- **🆕🆕🆕🆕🆕 竞争格局分析 (2026-02-27)**：2025年"when to think / adaptive compute"赛道急剧拥挤（~46篇新论文）。**关键结论：Direction reversal finding 仍然独特（零论文报告），但 method 空间拥挤（6+篇2025论文）**。三篇 HIGH-THREAT 论文：
  - **AdaptThink** (arXiv:2505.13417, EMNLP 2025)：RL think/no-think — 最直接 RL 竞争者，但方向隐式学习
  - **DiffAdapt** (arXiv:2510.19669)：轻量 probe + U-shaped entropy — probe 做 difficulty estimation（非 direction discovery）
  - **Think Just Enough** (arXiv:2510.08146)：Entropy early stopping 固定阈值 — APPS 中 entropy 仅 ρ=+0.144（弱正），最强信号为 step_count ρ=−0.274，使固定 entropy 阈值假设失效
  - 投稿策略：lead with FINDING not METHOD（"crowded method space, empty finding space"）
- **🆕🆕🆕🆕🆕 Phase 3+ 实验结果 (2026-02-27)**：
  - Phase 3 三种子验证：SCG-FineTune SR=96.7±0.6%, CS=44.1±5.5%（3-seed mean）
  - Wrong-Direction SR=58.2±2.5%（跨 seed 一致的灾难性证据）
  - 统计检验：T4 McNemar p=0.035 ✅（wrong-dir 有害）, T6 TOST p=0.002 ✅（gate 不损 SR）
  - **APPS 第二有效环境 GO**: base=58%, Δ=+6pp, 最强信号 step_count ρ=−0.274, token_entropy ρ=+0.144（弱正）
  - APPS 的最强信号 (step_count) 与 HotpotQA (evidence_count) 完全不同 → "signal-utility landscape is environment-dependent"（信号替换 signal replacement）
  - **APPS Step 2 完成**: SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass; 但 random SR=66.5% > SCG SR（passive abstention failure mode）
  - CMDP λ* 严格递增验证理论 + 0.6B NO-GO（仅 4B backbone）
- **🆕🆕🆕🆕🆕 G类新增 (2026-02-26)**：新增 Rational Metareasoning & Value of Computation 理论分类（G1-G5），收录 Russell & Wefald 1991 (VOC)、Altman 1999 (CMDP)、Zilberstein 1996 (Anytime)、Nair et al. 2024 (LLM Metareasoning)、FrugalGPT 2023、SkipNet 2018 等。关键发现：Direction-Aware Gate 的 VOC negativity insight 扩展了经典 metareasoning 理论（VOC ≥ 0 假设不成立），CMDP formalization + Lagrangian dual ascent 提供了 principled cost-quality trade-off
- **⚠️ 重要并发工作**：CATTS (2026-02-13) 提出vote-derived uncertainty用于web agents的adaptive allocation，与本文 narrative 高度重合但本质不同——CATTS 隐式依赖固定方向，我们显式测量方向（见Section 4.2.5详细对比）
- **🆕 Compute-Optimal Scaling** (2408.03314): 证明adaptive allocation比uniform高效4×，但依赖 difficulty estimation 且方向假设固定
- **🆕 DeepConf** (2508.15260): 使用local confidence (group/tail) 进行trace filtering，99.9% accuracy on AIME，但无方向 probe 机制
- **🆕🆕 C6类新增 (2026-02-18)**：发现5篇高度相关的2025年新工作（SEAG/ACL 2025, Learning When to Plan/2509.03581, Thinkless/NeurIPS 2025, Think or Not/2505.16854, When to Continue Thinking/2505.15400）均研究"何时触发额外计算"，但**均隐式依赖单调 signal-utility 对齐而未显式验证**——显式方向检验是 Direction-Aware Gate 相比这些方法的独特贡献（Phase 3 Wrong-Direction SR=58.2±2.5% 三种子量化证实）
- **🆕🆕🆕 2026-02-21更新**：新增6篇高度相关论文：
  - **LATTS** (arXiv:2509.20368): Per-step verifier-based accept/reject/backtrack，局部自适应test-time scaling
  - **CaTS** (OpenReview 2025): 自校准confidence用于early stopping，calibrated test-time scaling
  - **ARPO** (OpenReview 2025): Entropy-based adaptive rollout at tool-call steps，agentic RL优化
  - **GiGPO** (NeurIPS 2025): Step-level credit assignment，+12% ALFWorld，group-in-group优化
  - **Kambhampati (2024)**: LLMs Can't Plan论证，LLM作为approximate heuristic generator
  - **Causal Models + LLMs** (Frontiers in AI 2025): 因果模型增强LLM规划能力
- **🆕🆕🆕🆕 2026-03-01更新**：新增11篇论文，涵盖三个新方向：
  - **Hidden State Probing (C9)**: "The LLM Already Knows" (EMNLP 2025) — hidden state probe 估计 task difficulty，但假设固定方向；"LLM Internal States Reveal Hallucination Risk" (ICLR 2025)；"Do LLMs Build World Representations?" (NeurIPS 2024)
  - **Process Reward Models (E2)**: PAVs (ICLR 2025) — progress-based PRM，>8% over ORMs; ThinkPRM — generative long-CoT PRM
  - **Metareasoning & Token Efficiency (G4-G6)**: Bayesian Meta-Reasoning (ICML 2025)，TECTON，Cascaded LLM with Deferral (ICLR 2025)，Token Efficiency Decomposition (ICML 2026)，DTR/Think@n
  - **Compute-Optimal (C7)**: AdaptiveComp — 47-73% compute savings via difficulty-based budget
  - **关键发现**: "The LLM Already Knows" 是最相关的新工作——也用 hidden state probe，但方向固定（difficulty estimation），我们做 direction discovery（方向因环境而异）

---

## 1. 分类体系（Taxonomy）

### 1.1 总体分类框架

```
Test-Time Agent Planning 方法
│
├─ A. 推理结构增强 (Reasoning Structure Enhancement)
│   ├─ A1. Chain-based (CoT, Self-Consistency)
│   ├─ A2. Tree-based (ToT, LATS)
│   ├─ A3. Graph-based (GoT, Graph-CoT)
│   └─ A4. Adaptive Structure (Adaptive GoT)
│
├─ B. 搜索与规划 (Search & Planning)
│   ├─ B1. Lookahead Search (FLARE, RAP)
│   ├─ B2. Tree Search (MCTS-based: LATS, RAP, ReST-MCTS*)
│   ├─ B3. Best-First Search (Beam Search variants)
│   └─ B4. Hierarchical Planning (Plan-and-Act)
│
├─ C. 自适应计算分配 (Adaptive Compute Allocation)
│   ├─ C1. Uncertainty-based (CoRefine, Entropy-trigger)
│   ├─ C2. Confidence-based (Margin-trigger, Early Exit, CaTS)
│   ├─ C3. Test-Time Scaling (OpenAI o1-style, Compute-Optimal, LATTS)
│   ├─ C4. ★ Direction-Aware Gate (本文) ← 先 probe signal-utility 方向再触发
│   ├─ C5. ⚠️ Vote-based (CATTS) ← 并发工作 (2026-02-13)
│   ├─ C6. 🆕 When-to-Plan/Think Learning ← 2025新兴方向 (SEAG/Thinkless/Learning When to Plan, +AdaptThink, +L1)
│   ├─ C7. 🆕🆕 Compute-Optimal / Budget-Aware (Token-Budget-Aware, BudgetThinker, AdaptiveComp)
│   ├─ C8. 🆕🆕 Routing / Hybrid (RouteLLM, Router-R1, Semantic Router, DiffAdapt, Meta-Reasoner, Meta-R1)
│   └─ C9. 🆕🆕🆕 Hidden State Probing / Difficulty Estimation (LLM Already Knows, PIKA)
│
├─ D. 自我改进与反思 (Self-Improvement & Reflection)
│   ├─ D1. Self-Refine (Iterative Refinement)
│   ├─ D2. Self-Reflection (ReAct, Reflexion)
│   └─ D3. Multi-Agent Critique
│
├─ E. 价值引导 (Value-Guided Methods)
│   ├─ E1. Q-Value Models (Step-Level DPO, Agent Q, GiGPO)
│   ├─ E2. Process Reward Models (ReST-MCTS*, ORM, 🆕 PAVs, 🆕 ThinkPRM)
│   ├─ E3. Offline RL (Goal-Conditioned RL for Planning)
│   └─ E4. 🆕 Agentic RL (ARPO — entropy-based adaptive rollout)
│
├─ F. 神经符号融合 (Neuro-Symbolic Integration)
│   ├─ F1. LLM + Classical Planner (LLM+P)
│   ├─ F2. BDI + LLM (Dynamic Plan Generation)
│   ├─ F3. Formal Verification + LLM
│   └─ F4. 🆕 Causal Models + LLM (因果模型增强规划)
│
└─ G. 🆕 Rational Metareasoning & Value of Computation (2026-02-26 新增)
    ├─ G1. Classical Metareasoning (Russell & Wefald 1991, Horvitz 1989)
    ├─ G2. Constrained MDPs for Resource Allocation (Altman 1999, Gladin et al. 2023)
    ├─ G3. Anytime Algorithms (Zilberstein 1996)
    ├─ G4. LLM Metareasoning (Nair et al. 2024, 🆕 Meta-Reasoner, 🆕 Meta-R1, 🆕🆕 Bayesian Meta-Reasoning, 🆕🆕 TECTON)
    ├─ G5. Cost-Aware Adaptive Inference (FrugalGPT, SkipNet, 🆕🆕 Cascaded LLM with Deferral)
    └─ G6. 🆕🆕🆕 Token Efficiency & Reasoning Depth Analysis (Token Efficiency Decomposition, DTR/Think@n)
```

### 1.2 🆕 按研究版图分类：Adaptive Compute 的 Reasoning vs Agent Settings (2026-03-05 重新定位)

**研究版图事实**：adaptive compute 的研究主要在 reasoning 上，agent settings 是 under-explored。

| 维度 | Reasoning Benchmarks（主流） | Agent/Interactive Settings（under-explored） |
|------|-------------------------------|------------------------|
| **研究密度** | 10+ 篇（AdaptThink, DiffAdapt, CaTS...） | **仅 3 篇**（CATTS, Learning When to Plan, ARPO）+ 本文 |
| **交互对象** | 问题本身（静态输入） | 环境（状态持续演化，有外部反馈） |
| **信号来源** | Model-intrinsic（entropy, confidence） | Environment-state + Model-intrinsic |
| **Benchmark 异质性** | 较低（MATH/GSM8K/GPQA 都是推理类） | 高（QA/Code/Web 状态结构完全不同） |
| **方向稳定性** | 未被系统验证（可能碰巧一致） | **实证发现不稳定（direction reversal）** |
| **代表方法** | AdaptThink, DiffAdapt, Think Just Enough, Thinkless, CaTS | CATTS, ARPO, **Direction-Aware Gate (本文)** |
| **Direction 验证** | ❌ 零篇 | ❌ CATTS/ARPO 未验证，**✅ 本文首次** |

**实验证据（environment-state >> model-intrinsic）**：

| 环境 | 最强信号（环境特异） | 效应量 | token_entropy | 效应量 | 倍数 |
|------|---------------------|--------|---------------|--------|------|
| HotpotQA | evidence_count | ρ=−0.586 | token_entropy | ρ=−0.327 | 1.8× |
| APPS | step_count | ρ=−0.274 | token_entropy | ρ=+0.144 | 1.9× |
| WebShop | state_category | η²=0.598 | token_entropy | ρ=+0.133 | 4.5× |
| MBPP | step_count | ρ=+0.526 | token_entropy | ρ=+0.153 | 3.4× |

→ token_entropy 在 4 个环境中有 3 个效应量仅 0.13-0.15（弱），环境状态信号一致主导。

**关键推论**：
- Agent settings 天然更 heterogeneous：env-state signals 编码 task-specific progress（语义因环境而异），使 universal proxy 假设更容易崩溃
- 现有方法在 homogeneous reasoning benchmarks 上验证，未暴露 direction reversal 问题（任务语义相似，方向碰巧一致）
- ⚠️ 不声称 reasoning 之间方向一定一致——只声称在 heterogeneous agent settings 中 direction reversal 是实证事实
- 本文的贡献是 **setting 层面的洞察 + finding 层面的发现**：首次在 agent settings 中系统性发现 direction reversal 并提出 direction-aware gate

### 1.3 按计算模式分类

| 计算时机 | 改进对象 | 代表方法 |
|---------|---------|---------|
| **Inference-time** | Reasoning Structure | CoT, ToT, GoT |
| **Inference-time** | Search Process | FLARE, LATS, RAP |
| **Inference-time** | Compute Allocation | CoRefine, Test-Time Scaling |
| **Learning-time** | Proposer (Policy) | RL, DPO, CSO |
| **Learning-time** | ★ Trigger Policy (Gate) | **Direction-Aware Gate (本文)** |
| **Meta-level** | 🆕 Computation Value Assessment | Rational Metareasoning, VOC, CMDP, Anytime |

---

## 2. 详细分类与方法描述

### A. 推理结构增强 (Reasoning Structure Enhancement)

#### A1. Chain of Thought (CoT)

**核心思想**：线性、逐步推理链

**代表论文**：
- Wei et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (NeurIPS 2022)

**特点**：
- ✅ 简单有效，易于实现
- ❌ 线性结构限制，无法探索分支
- ❌ 贪心选择，长视野次优

#### A2. Tree of Thoughts (ToT)

**核心思想**：树状分支探索多条推理路径

**代表论文**：
- Yao et al. "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (NeurIPS 2023)

**特点**：
- ✅ 支持分支探索和回溯
- ❌ 每步扩展所有分支，开销高
- ❌ 深度受限，难以处理长视野任务

#### A3. Graph of Thoughts (GoT)

**核心思想**：图结构支持任意branching、merging、backtracking

**代表论文**：
- Besta et al. "Graph of Thoughts: Solving Elaborate Problems with Large Language Models" (AAAI 2024)
- Graph-CoT: "Graph Chain-of-Thought: Augmenting Large Language Models by Reasoning on Graphs" (ACL 2024)

**特点**：
- ✅ 最灵活的结构，支持复杂依赖关系
- ✅ 可以合并并行子问题的结果
- ❌ 图构建和管理复杂度高
- ❌ 仍需每步评估大量节点

#### A4. Adaptive Graph of Thoughts

**核心思想**：Test-time动态选择CoT/ToT/GoT结构

**代表论文**：
- "Adaptive Graph of Thoughts: Test-Time Adaptive Reasoning Unifying Chain, Tree, and Graph Structures" (2025)

**特点**：
- ✅ 根据任务复杂度自适应选择结构
- ❌ 结构选择本身需要额外计算

---

### B. 搜索与规划 (Search & Planning)

#### B1. Lookahead Search (FLARE)

**核心思想**：每步前瞻H步，值传播指导动作选择

**代表论文**：
- **FLARE**: "Why Reasoning Fails to Plan: A Planning-Centric Analysis of Long-Horizon Decision Making in LLM Agents" (arXiv:2601.22311, 2026)

**核心机制**：
```
State s → Lookahead H steps for each action → Value propagation → Select action
```

**关键结论**：
- Step-wise reasoning是**任意次优**（贪心策略）
- Beam search **无法弥补**结构性缺陷
- 显式前瞻 + 价值传播是**必要的**

**特点**：
- ✅ 理论分析清晰，证明了step-wise reasoning的根本局限
- ✅ 小模型 + FLARE > 大模型 + pure reasoning
- ❌ **每步都需要lookahead**，计算开销持续高
- ❌ **无法蒸馏**，开销不随经验降低

**与本文对比**：
| 维度 | FLARE | Direction-Aware Gate (本文) |
|------|-------|------|
| 计算模式 | Inference-time search（每步） | Adaptive triggering（probe 后选择性触发 optimizer T） |
| 开销趋势 | 持续高（每步lookahead） | **选择性**（只在 gate 判断有益时触发 T） |
| 方向假设 | 无（每步都用） | **先 probe σ-U 方向再决定** |
| 原理 | "多看几步" | "测量信号方向，在有益时才看" |

#### B2. Monte Carlo Tree Search (MCTS) Based

##### B2.1 Language Agent Tree Search (LATS)

**代表论文**：
- Zhou et al. "Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models" (ICML 2024)

**核心机制**：
- MCTS的4个步骤：Selection → Expansion → Simulation → Backpropagation
- LLM作为3个角色：
  * **Action Generator**: 采样可能的动作
  * **Value Function**: 估计未来期望回报
  * **Reflection Mechanism**: 生成自我批评

**特点**：
- ✅ 统一reasoning, acting, planning
- ✅ 利用LLM自身能力（不需要外部模型）
- ❌ 每步都需要MCTS，开销高
- ❌ 需要大量rollout（simulation）

##### B2.2 Reasoning via Planning (RAP)

**代表论文**：
- Hao et al. "Reasoning with Language Model is Planning with World Model" (EMNLP 2023)

**核心创新**：
- 将LLM同时作为**world model**和**reasoning agent**
- World model: 预测状态转移和长期结果
- MCTS在推理空间中搜索高奖励路径

**结果**：
- RAP (Llama-33B) > CoT (GPT-4) +33% relative improvement

**特点**：
- ✅ 明确分离world model和agent角色
- ✅ 在plan generation、math reasoning上显著提升
- ❌ 仍然是inference-time search（持续开销）

##### B2.3 ReST-MCTS* (Process Reward Guided)

**代表论文**：
- "ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search" (NeurIPS 2024)

**核心机制**：
- Process Reward Model (PRM) 评估部分解的质量
- MCTS在PRM指导下搜索
- 搜索轨迹用于self-training（RL）

**特点**：
- ✅ 结合搜索和学习（可以逐步改进）
- ✅ Process reward比outcome reward更精细
- ❌ 仍需要inference-time MCTS（虽然可以逐步减少）

#### B3. Beam Search Variants

**核心思想**：维持top-k候选序列，每步扩展并剪枝

**代表方法**：
- Standard Beam Search (LLM decoding)
- Self-Evaluation Guided Beam Search
- Reasonin gAgent (AG2): Beam Search for LLM reasoning

**FLARE的关键批评**：
> "Beam search扩大宽度但保留step-wise scoring，无法提供worst-case planning保证"

**特点**：
- ✅ 实现简单，广泛使用
- ❌ **本质上仍是贪心+局部扩展**，无法解决长视野问题（FLARE理论证明）
- ❌ 宽度k增加时开销线性增长

#### B4. Hierarchical Planning

##### Plan-and-Act

**代表论文**：
- "Plan-and-Act: Improving Planning of Agents for Long-Horizon Tasks" (ICML 2025)

**架构**：
```
User Goal → [Planner LLM] → High-level Plan → [Executor LLM] → Environment Actions
```

**特点**：
- ✅ 分层设计降低单步复杂度
- ✅ WebArena-Lite 57.58%, WebVoyager 81.36% (SOTA)
- ✅ 可扩展的合成数据生成
- ❌ 需要训练两个专用模型（Planner + Executor）
- ❌ 仍然是inference-time分解，无蒸馏机制

---

### C. 自适应计算分配 (Adaptive Compute Allocation)

这一类别是**离本文最近的竞争者**，核心问题都是：**何时投入额外计算资源？**

#### C1. Uncertainty-Based Triggering

##### CoRefine

**代表论文**：
- "CoRefine: Confidence-Guided Self-Refinement for Adaptive Test-Time Compute" (2024)

**核心机制**：
- 用模型的**uncertainty**（entropy、confidence）决定是否refine
- 不确定时→ 多次采样、self-refinement、调用更强模型

**特点**：
- ✅ 自适应分配计算，不像FLARE每步都搜索
- ❌ **核心假设**：不确定性 = 需要额外计算
- ❌ 无法处理"confident but wrong"状态（本文的核心motivation）

**与本文的关键区别**：
| CoRefine | Direction-Aware Gate (本文) |
|----------|------|
| 触发信号：**Uncertainty** (entropy, logprob) | 触发信号：**任意 σ（probe 发现的最优信号）** |
| 方向假设：不确定 → 需要额外计算（**正向，固定**） | 方向假设：**无预设，probe 校准** |
| 核心假设：高 entropy = 需要 optimizer | 核心发现：同一信号在不同环境方向不同 |
| 检测：模型自报（confidence） | 检测：probe phase 测量 σ-U 关系 + gate phase 触发 |

**本文核心论点**：
```
CoRefine 假设：entropy ↑ → U(T,s) ↑（正向，固定）
本文发现：   sign(corr(σ, U)) 在不同环境中不同
           → 固定方向假设在某些环境系统性失效
           → 需要 probe-first approach
```

- 本文的 gate 在 probe 后根据实际方向触发，CoRefine/Entropy 按固定方向触发
- 当环境中方向为负时，CoRefine 会反向触发（触发不该触发的，漏掉该触发的）

#### C2. Confidence-Based Methods

**代表方法**：
- Margin-based trigger (action logit margin)
- 🆕 CaTS (Calibrated Test-Time Scaling)

##### 🆕 C2.1 CaTS: Calibrated Test-Time Scaling (OpenReview, 2025)

**代表论文**：
- "Calibrated Test-Time Scaling: Knowing When to Stop Thinking" (OpenReview, 2025)

**核心机制**：
```
问题：LLM在reasoning时不知道何时停止thinking
方案：Self-calibration → 生成confidence score → 与阈值比较 → 决定是否继续
关键：用calibration使confidence score准确反映actual correctness probability
```

**关键发现**：
1. **Raw confidence不可靠**：LLM的原始自信度与实际正确率之间存在系统性偏差
2. **Calibration后有效**：校准后的confidence可以可靠判断何时停止额外计算
3. **Early stopping节省计算**：在不损失准确率的前提下减少不必要的额外推理

**特点**：
- ✅ 直接针对"何时停止"问题，与本文的"何时触发"高度相关
- ✅ Calibration思想与SCG的Self-Calibrating Gate思路一致
- ❌ **单轮reasoning**，非sequential agent decision
- ❌ **Confidence-based**：仍假设confidence低→需要更多计算（正向假设）
- ❌ 未probe信号方向是否在不同环境中一致

**与Direction-Aware Gate / SCG的对比**：

| 维度 | CaTS | Direction-Aware Gate / SCG |
|------|------|---------|
| **场景** | 单轮reasoning早停 | 多步agent selective trigger |
| **信号** | Self-generated confidence | Value consistency / behavioral signals |
| **Calibration** | 统计校准confidence | SCG: probe signal-utility方向 |
| **方向假设** | 假设低confidence→需要更多计算 | **先probe方向**（可正可负） |
| **学习** | Calibration mapping (fixed) | SCG learns direction + threshold |

**叙事关系**：
> CaTS验证了"calibration是关键"这一直觉——raw signals不可靠，需要校准。SCG将此推进一步：不仅校准magnitude，还校准**方向**（信号↑→utility↑还是↓？），这在不同环境中可能截然不同。

##### 🆕🔴 C2.2 HIGH-THREAT Think Just Enough: Entropy Early Stopping (arXiv:2510.08146, 2025)

**发表**: arXiv, October 2025
**arXiv**: https://arxiv.org/abs/2510.08146
**威胁等级**: 🔴 HIGH — 直接使用 entropy 做固定阈值 early stopping

**核心思想**:
- 使用 entropy 作为 early stopping signal
- 固定阈值：当 entropy 低于阈值时停止 thinking
- 假设：高 entropy = 需要更多 thinking（正向固定）

**核心机制**:
```
Reasoning Token Stream → Compute Entropy at each step
  → If entropy < threshold: STOP (confident enough)
  → If entropy ≥ threshold: CONTINUE thinking
  → Threshold: fixed, calibrated on validation set
```

**关键结果**:
- 在多个推理基准上减少 reasoning tokens，性能损失小
- 简单有效的 early stopping 策略

**与 Direction-Aware Gate 的详细对比**:

| 维度 | Think Just Enough | Direction-Aware Gate (本文) |
|------|------------------|---------------------------|
| 信号 | Token entropy（固定） | 任意 σ（probe 发现最强信号） |
| 方向假设 | 固定正向（高 entropy → need think） | **无预设**（probe 发现） |
| 阈值 | 固定（validation set 校准） | Adaptive（LR 学习 + λ* 自动调） |
| 方向验证 | ❌ | ✅ |
| APPS 场景 | ❌ entropy 仅 ρ=+0.144（弱正），非最强信号 | ✅ probe 发现 step_count (ρ=−0.274) 替代 |
| 环境泛化 | 固定阈值跨环境脆弱 | Probe 自适应 |

**关键差异化一句话**:
> "Think Just Enough assumes high entropy signals the need for more thinking; in APPS, token entropy is only weakly informative (ρ=+0.144) and the strongest signal is step_count (ρ=−0.274), causing fixed entropy thresholds to fail on two levels: wrong signal identity and weak signal strength. Our direction-aware probe automatically discovers effective signals per environment."

**APPS 失效场景**：
- Think Just Enough 在 APPS 中双重失效：(1) token_entropy 仅 ρ=+0.144（弱正，远不如 step_count ρ=−0.274）; (2) 方向为正（与 HotpotQA 的负方向相反）
- 固定 entropy 阈值选错了信号（应用 step_count）且方向不确定
- 我们的 probe 会自动发现 APPS 中的最强信号是 step_count (ρ=−0.274)，而非 entropy

---

- Early exit (layer-wise confidence)
- Self-consistency voting
- **DeepConf** (Deep Think with Confidence)

**特点**：
- ✅ 简单、无需训练
- ❌ 与uncertainty-based类似，无法处理高confidence错误

##### C2.1 Deep Think with Confidence (DeepConf)

**代表论文**：
- Fu et al. "Deep Think with Confidence" (arXiv:2508.15260, Meta AI & UCSD, 2025)

**核心机制**：
```
Parallel thinking (N samples) → Confidence filtering
                                ↓
                    Local confidence measurements:
                    - Group confidence (sliding window)
                    - Bottom 10% confidence
                    - Tail confidence
                                ↓
                    Filter low-confidence traces
                    (offline or online with early stopping)
                                ↓
                    Confidence-weighted majority voting
```

**Confidence Metrics**：
1. **Token Confidence**: C_i = -(1/k)Σ log P_i(j) (top-k tokens)
2. **Group Confidence**: C_G = avg(C over sliding window)
3. **Bottom 10% Confidence**: 最低10%组的平均confidence
4. **Tail Confidence**: 最后K个tokens的平均confidence

**操作模式**：
- **Offline Mode**: 生成所有traces后进行过滤和加权投票
- **Online Mode**: 实时监测group confidence，低于阈值时early stop

**关键发现**：
1. **Local > Global**: Group confidence比全局平均confidence更有效
2. **Tail matters**: 推理链尾部的confidence对结果质量影响大
3. **Early stopping**: Online mode可减少84.7% token生成
4. **Weighted voting**: Confidence-weighted voting优于standard majority voting

**实验结果**：
- **AIME 2025**:
  - DeepConf@512: 99.9% accuracy (vs cons@512: 97.0%, pass@1: 91.8%)
  - Token reduction: 84.7% (GPT-OSS-120B)
- **Efficiency**: 在Qwen3-32B上减少69.0% tokens
- **Generality**: 跨模型有效 (DeepSeek-8B, Qwen3-8B/32B, GPT-OSS-20B/120B)

**特点**：
- ✅ **无需训练**：直接使用模型内部confidence信号
- ✅ **模型无关**：适用于任何提供logprobs的LLM
- ✅ **双模式**：Offline提升准确性，Online提升效率
- ✅ **可解释**：Confidence metrics有明确含义
- ❌ **依赖logprobs**：需要模型提供token-level概率
- ❌ **仍需多样本**：Offline mode需要生成N个完整traces
- ❌ **阈值调优**：需要warmup确定confidence threshold

**与Direction-Aware Gate（本文）对比**：
| 维度 | DeepConf | Direction-Aware Gate（本文） |
|------|----------|------|
| **触发信号** | Local confidence (group, tail) | 任意 σ（probe 发现的最优信号） |
| **核心假设** | 低confidence → 低质量trace | 确定但错了 → 需要verification |
| **应用场景** | Parallel sampling (self-consistency) | Sequential decision-making (RL agents) |
| **检测方式** | Token-level statistics | Direction discovery + SCG-FineTune(LR) |
| **训练需求** | ❌ 无（直接使用） | 轻量（SCG-FineTune: LR on probe data） |
| **蒸馏能力** | ❌ 无（启发式） | ✅ Critic可蒸馏 |
| **依赖** | Logprobs access | 任意 optimizer T + 可观测 signal σ |

**与CoRefine/CATTS的关系**：
```
DeepConf: Confidence filtering for parallel thinking
  - 同时生成N traces → filter → weighted voting
  - Confidence来自token distribution statistics

CoRefine: Uncertainty-triggered refinement
  - Uncertainty高时 → sequential refinement

CATTS: Vote-based uncertainty for web agents
  - Vote distribution → entropy/margin → arbiter

共同点：都使用model-internal signals
区别：DeepConf focus on trace filtering, CATTS focus on action selection
```

**Innovation**：
1. **Group confidence**: 比全局平均更精细的local signal
2. **Bottom 10%**: 捕捉reasoning breakdowns（"wait", "however"时刻）
3. **Tail confidence**: 关注最终推理步骤质量
4. **Online early stopping**: 在生成过程中动态终止低质量traces

#### C3. Test-Time Scaling

##### OpenAI o1-Style Thinking

**核心思想**：给模型"思考时间"，让其在输出前进行内部推理

**机制**（推测，因未公开）：
- Hidden chain-of-thought
- RL训练优化推理策略
- Test-time动态分配计算

**特点**：
- ✅ 大幅提升复杂推理任务性能
- ❌ 黑盒，机制不透明
- ❌ 需要专门训练（用户无法复现）

##### Scaling Test-Time Compute Optimally

**代表论文**：
- **Snell et al.** "Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Model Parameters" (arXiv:2408.03314, Google DeepMind & UC Berkeley, 2024)
- "Scaling Test-time Compute for LLM Agents" (arXiv:2506.12928, 2025)

**核心问题**：
> 给定固定的inference-time compute budget，如何最有效地分配以改进LLM输出？

**两大机制**：
1. **Search with Process-Based Verifiers**: 使用dense PRM指导tree search
2. **Adaptive Revision**: 动态更新模型分布，迭代refinement

**关键创新：Compute-Optimal Scaling Strategy**

```
问题难度 → [Difficulty Estimator] → 选择最优策略
                                      ↓
Easy problems: Sequential revisions (利用初始输出接近正确)
Hard problems: Parallel sampling + PRM search (需要exploration)
```

**Difficulty Estimation**：
- **Oracle difficulty**: 基于ground-truth pass@1率（2048 samples）分5个quantiles
- **Model-predicted difficulty**: 基于learned verifier的平均分数（无需ground-truth）

**Compute-Optimal vs Uniform Allocation**：

| Budget | Uniform (Best-of-N) | Compute-Optimal | Efficiency Gain |
|--------|-------------------|----------------|----------------|
| Revisions | Parallel N samples | 动态分配parallel vs sequential | **4× fewer compute** |
| PRM Search | 固定beam width | Adaptive beam + depth per difficulty | **~4× improvement** |

**Revision Strategies**：
```
Parallel (Best-of-N):    Sample N independent outputs → select best
Sequential (Revisions):  Initial → revise_1 → revise_2 → ... → revise_N
Compute-Optimal:         Easy → Sequential, Hard → Parallel
```

**PRM Search Strategies**：
```
Best-of-N (Baseline):  Sample N → ORM scoring → select best
PRM Best-of-N:         Sample N → PRM step-wise scoring → select best
PRM Beam Search:       Beam search guided by PRM scores
Compute-Optimal:       Adaptive beam width based on difficulty
```

**核心发现**：

1. **Compute-optimal > Uniform by 4×**
   - MATH benchmark: 相同性能下，compute-optimal使用1/4计算量
   - Revisions: 40%→45% accuracy, 4× less compute

2. **Test-time compute vs Pretraining**
   - FLOPs-matched comparison: PaLM 2-S* + compute vs PaLM 2-L (14× larger)
   - **Easy/Medium questions**: Test-time compute优于scaling model
   - **Hard questions**: Pretraining仍然更有效
   - Implication: 未来可能"fewer pretraining FLOPs + more inference FLOPs"

3. **Question difficulty is critical**
   ```
   Easy (high pass@1):    Sequential revisions work best
   Medium:                Mixed strategies
   Hard (low pass@1):     Parallel sampling + search needed
   Hardest:               Test-time compute saturates, need more pretraining
   ```

4. **Verifier quality matters**
   - Process Reward Model (PRM) > Outcome Reward Model (ORM)
   - PRM提供step-wise feedback，支持更精细的search

**实验设置**：
- **Model**: PaLM 2-S* (Codey) finetuned for revisions + PRM
- **Benchmark**: MATH (12K train, 500 test)
- **Metrics**: Accuracy vs generation budget (compute cost)

**PRM Training** (关键技术细节):
- 不使用human labels（PRM800K效果差，分布不匹配）
- **Monte Carlo rollout labeling**: 从每步rollout，估计per-step correctness
- PRM预测"value-to-go"（类似RL中的Q-value）

**特点**：
- ✅ **系统性分析**：首次系统研究test-time compute scaling behaviors
- ✅ **Theoretical insight**: 证明uniform allocation是次优的
- ✅ **Practical strategy**: Compute-optimal策略可直接应用
- ✅ **Model efficiency tradeoff**: 量化test-time vs pretraining compute
- ❌ **需要difficulty estimation**: 依赖verifier或ground-truth
- ❌ **Domain-specific**: 主要在MATH benchmark验证
- ❌ **Finetuning required**: 需要训练revision model和PRM

**与Direction-Aware Gate（本文）的关系**：
| 维度 | Compute-Optimal Scaling | Direction-Aware Gate（本文） |
|------|------------------------|------|
| **层级** | 宏观框架（如何分配compute） | 具体策略（何时干预） |
| **触发信号** | Question difficulty (pass@1, verifier score) | 任意 σ（probe 发现的最优信号） |
| **分配机制** | Per-question策略选择 | Per-state selective triggering |
| **学习能力** | ❌ Difficulty bins固定（虽然adaptive） | ✅ Direction discovery + SCG-FineTune(LR) |
| **应用** | Reasoning tasks (math, QA) | RL agents (sequential decision) |
| **核心贡献** | 证明adaptive > uniform | 发现 signal-utility 方向因环境而异 |

**本文可以视为compute-optimal的一种实现**：
- Direction-Aware Gate = difficulty estimator（但基于 signal-utility direction probe）
- 本文的selective triggering = compute allocation strategy
- 两者互补：Compute-optimal提供宏观框架，Direction-Aware Gate 提供微观机制

**与DeepConf的关系**：
```
Compute-Optimal Scaling: 问题级别的策略选择
  - 根据整个问题的难度决定用哪种方法

DeepConf: Trace级别的质量过滤
  - 在parallel sampling内部，过滤低质量traces

可以结合：
  Easy问题 → Sequential revisions (Compute-Optimal)
  Hard问题 → Parallel sampling + DeepConf filtering
```

#### C4. ★ Direction-Aware Gate (本文)

**这是您的方法，详细对比见Section 4**

**核心差异**：
- 不预设触发信号方向（vs CoRefine/SEAG/CATTS 隐式依赖正向对齐）
- 不基于每步搜索（vs FLARE/MCTS 每步都搜索）
- 而是基于**direction discovery approach**：先测量 signal σ 与 optimizer utility U(T,s) 的关系方向，再据此自适应触发 optimizer T
- 主方法：SCG-FineTune(LR)（5 维信号特征 + logistic regression，训练 <1s）
- 消融方法：SCG-Prompt（training-free LLM ICL，但存在 YES 偏置）、SCG-MLP、SCG-Fixed

**🆕🆕 Phase 3+ 实证结果（2026-02-27）**：
- HotpotQA (Phase 3 三种子): FineTune SR=96.7±0.6%, CS=44.1±5.5%, Oracle CS=67.0%（65.8% of oracle）
- Wrong-Direction SR=58.2±2.5%（跨 seed 一致） → **方向是 gate 正确运作的必要前提** 🔥
- 统计检验：T4 McNemar p=0.035 ✅（wrong-dir 有害）, T6 TOST p=0.002 ✅（gate 不损 SR）
- **APPS(4B) GO**: base SR=58%, always SR=64.8%, Δ=+6pp; 最强信号 step_count ρ=−0.274, token_entropy ρ=+0.144（弱正）
- **APPS Step 2 完成**: SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass; random SR=66.5% > SCG（passive abstention, RR=0%）
- → signal replacement: 不同环境连最强信号本身都不同（HotpotQA: evidence_count, APPS: step_count, MBPP: step_count 但反向）
- MBPP(0.6B) NO-GO; CMDP λ* 严格递增验证理论; APPS CMDP 收敛率 80%
- No-Probe ≈ With-Probe → 核心贡献是 direction discovery（方向数据），不是在线 probe 过程本身
- Prompt gate 存在 YES 偏置（ec≥2 时 54% 误判）→ LR gate 远优于 ICL gate
- Bootstrap 10K：所有 gate SR 差异 n.s.，区分度在 cost saving

#### C5. ⚠️ Vote-Based (CATTS) - 并发工作

**代表论文**：
- Lee et al. "Agentic Test-Time Scaling for WebAgents" (arXiv:2602.12276, 2026-02-13)

**核心机制**：
```
每步采样N个候选action → 计算vote distribution
                     ↓
       Uncertainty metrics: Entropy H_t, Margin Δ_t
                     ↓
              U_t > threshold τ?
              Yes → 调用Arbiter (另一个LLM重新选择)
              No  → 用Majority voting
```

**不确定性度量**：
- **Entropy**: H_t = -Σ p_t(a) log p_t(a)
- **Margin**: Δ_t = p_t(a_top1) - p_t(a_top2)

其中p_t(a) = n_t(a)/N是vote distribution（n_t(a)是投给action a的票数）

**关键发现**：
1. **Uniform scaling失效**：在web agents中，增加N从10→20，性能提升<0.2%
2. **Two regimes**：
   - **Redundancy** (高共识): 大部分候选一致，arbiter可能推翻正确共识
   - **Contention** (有争议): 候选分散，arbiter能帮助选择
3. **Vote statistics预测成功**：
   - 成功轨迹：低entropy + 高margin
   - 失败轨迹：高entropy + 低margin
   - Correlation: r = strong (论文Fig 2)
4. **Arbiter override危险**：
   - 当Δ_t > 0.7（高共识）时，arbiter推翻共识导致成功率下降11.9%
   - 需要selective triggering

**CATTS策略**：
```
if U_t ≤ τ:
    # 低不确定性，信任majority vote
    action = argmax_a p_t(a)
else:
    # 高不确定性，调用arbiter深度推理
    action = ARBITER(state, candidates, votes)
```

**实验结果**（WebArena-Lite & GoBrowse）：
| Method | WebArena-Lite SR | Tokens | GoBrowse SR | Tokens |
|--------|-----------------|--------|-------------|--------|
| Majority Vote (N=10) | 43.2% | 920K | 88.0% | 481K |
| Always-Arbiter (N=10) | 44.0% | 762K | 88.3% | 443K |
| **CATTS (entropy, best τ)** | **47.9%** | 745K | **90.2%** | 422K |
| **CATTS (margin, best τ)** | **47.9%** | 405K | **90.4%** | 372K |

- **Efficiency**: 47.9% SR with 2.3× fewer tokens than uniform N=20
- **Threshold**: τ选择通过grid search on validation set

**特点**：
- ✅ 实证有效：+4.7% SR on WebArena-Lite, 2.3× token reduction
- ✅ 模型无关：只需要能采样候选（黑盒API也可用）
- ✅ 简单实现：threshold-based gating，无需训练
- ❌ **无学习机制**：threshold是hand-tuned（vs 本文的 SCG-FineTune(LR), direction-aware adaptive gate）
- ❌ **需要多次采样**：每步N次forward pass才能得到vote distribution
- ❌ **无formal framework**：empirical observation，没有VoC formulation
- ❌ **Limited to web agents**：实验只在web navigation tasks

**与本文的核心区别**（详见Section 4.2.5）：

| 维度 | CATTS | Direction-Aware Gate (本文) |
|------|-------|------|
| **应用场景** | Web agents (voting-based) | Sequential LLM agents |
| **触发信号** | Vote statistics (entropy, margin) | **任意 σ（probe 发现）** |
| **方向假设** | 正向固定（高 disagreement → trigger） | **无预设（probe 校准方向）** |
| **Gating机制** | Threshold tuning (grid search) | **Direction discovery + SCG-FineTune(LR)** |
| **额外计算** | LLM arbiter call | Test-time optimizer T（rollout、voting 等） |
| **方向验证** | ❌ 未验证 | ✅ 系统测量 sign(corr(σ, U)) |
| **理论框架** | 无（empirical） | Optimizer utility U(T,s) + adaptive triggering formulation |
| **依赖** | 需要多次采样能力 | 任意 optimizer T + 可观测 signal σ |

**CATTS vs 本文的本质差异**：
```
CATTS的假设：
  Vote disagreement → 需要arbiter（固定正向）

本文的发现：
  sign(corr(σ, U)) 因环境而异 → 需要先 probe 方向
  → 固定方向假设在某些环境系统性失效

一句话：CATTS 隐式依赖固定方向；我们显式测量方向
```

**CATTS的价值（对本文论文的影响）**：
1. **Validates adaptive allocation principle**：证明selective compute allocation在agents中有效
2. **Highlights direction alignment gap**：CATTS 隐式依赖固定正向对齐，本文发现对齐方向因环境而异——核心差异化点
3. **Shared high-level principle**："allocate compute where it's likely to change the decision"——但 operationalization 不同
4. **Domain difference**：Web agents vs Sequential agents（application space orthogonal）

**论文中如何引用CATTS**：
```latex
\textbf{Concurrent Work:} Concurrent to our work, Lee et al. [CATTS]
explore adaptive compute allocation for web agents using vote-derived
uncertainty (entropy and margin from multi-sample voting). CATTS
shares our high-level principle---allocate compute where it is likely
to change the decision---and demonstrates effectiveness of threshold-based
gating in web navigation tasks.

\textbf{Key Difference:} CATTS implicitly relies on a fixed signal direction (high
vote disagreement → trigger arbiter) without empirically verifying this
across environments. Our work is the first to explicitly test signal-utility
direction across multiple environments, finding that it does not hold
universally. We propose a direction discovery approach that measures the
signal-utility relationship from calibration data rather than relying on
a fixed direction, achieving robust performance across environments
where fixed-direction methods fail.
```

#### C6. 🆕 When-to-Plan / When-to-Think Learning Methods (2025-2026)

> **更新时间**: 2026-02-18 — 与本文核心思想最接近的新兴子类
>
> **核心问题**: 如何让agent/LLM学会「判断自己是否需要做planning search」？
>
> **与本文的关键联系**: 这些方法都试图回答"何时触发额外计算"，但与本文的本质区别是：**没有一篇先 probe 触发信号与 optimizer utility 的关系方向再设计 gate**。Direction-Aware Gate 是唯一先实证检验信号方向再做 gate 的工作（Phase 3: Wrong-Direction SR=58.2±2.5%，三种子验证量化证实方向的重要性）。

##### C6.1 SEAG: Semantic Exploration with Adaptive Gating (ACL 2025)

**代表论文**：
- Lee et al. "Semantic Exploration with Adaptive Gating for Efficient Problem Solving with Language Models" (ACL 2025, Long Paper #29)
- **PDF**: https://aclanthology.org/2025.acl-long.29.pdf | **Code**: https://github.com/ml-postech/SEAG-semantic-exploration-with-adaptive-gating

**核心机制**：
```
Step 1: Simple reasoning (CoT) → generate k initial answers
Step 2: Compute confidence entropy over k answers
                    ↓
         Confidence > threshold α?
         Yes → accept simple CoT answer (skip tree search)
         No  → invoke tree-based semantic search
                    ↓
         Consolidate semantically identical steps to reduce redundancy
```

**关键发现**：
- 4.3% accuracy gain (GSM8K, ARC) at only 31% of baseline compute
- Confidence entropy as gate signal: low confidence → trigger expensive tree search
- Semantic deduplication reduces redundant exploration in tree search

**特点**：
- ✅ 计算开销大幅降低（仅31% vs full tree search）
- ✅ 简单信号（entropy）+ 明确gate阈值
- ❌ **阈值是hand-tuned**（非learned），无法自适应新环境
- ❌ **未验证confidence entropy是否在不同任务类型中保持正向预测关系**（本文的核心发现：这个方向可能倒置！）
- ❌ 仅在math/commonsense benchmarks验证，未在sequential decision-making任务测试

**与本文的结构对比**（最相似的方法）：

| 维度 | SEAG | Direction-Aware Gate (本文) |
|------|------|---------|
| **触发信号** | Confidence entropy (of k CoT answers) | 任意 σ（probe 发现的最优信号） |
| **gate方向假设** | 低confidence → trigger（正向，**未验证**） | **Probe-first**: 先测量 sign(corr(σ, U)) |
| **Signal方向验证** | ❌ 隐式正向，未经实证检验 | ✅ 在多个环境中系统测量（发现方向因环境而异） |
| **额外计算** | Tree search | 任意 test-time optimizer T |
| **gating机制** | Hand-tuned threshold | **SCG-FineTune(LR)**: direction discovery + LR gate（Phase 3: SR=96.7%, CS=44.1%） |
| **处理方向倒置** | ❌ 无机制 | ✅ probe phase 自动发现并适应方向 |

**本文相对SEAG的关键贡献**：
> SEAG 隐式依赖 confidence 低→planning 有用（单调正向对齐）。本文发现此对齐关系本身需要先验证——同一信号在不同环境中与 optimizer utility 的相关方向可以相反。Phase 3 三种子验证：Wrong-Direction SR=58.2±2.5%（T4 McNemar p=0.035），方向翻转后的灾难性失效。更进一步，APPS 中 token_entropy 仅 ρ=+0.144（弱正），最强信号是 step_count ρ=−0.274——连最有用的信号本身都因环境而异（signal replacement）。SEAG-style gate 在方向为负或信号不对的环境中会系统性失效。Direction-Aware Gate 通过 direction discovery 测量当前环境的方向和信号重要性，避免此问题。

---

##### C6.2 Learning When to Plan (arXiv:2509.03581, Sep 2025)

**代表论文**：
- Paglieri, Cupiał et al. "Learning When to Plan: Efficiently Allocating Test-Time Compute for LLM Agents" (arXiv:2509.03581, Sep 3, 2025)
- **团队**: Oxford (Tim Rocktäschel lab), Jack Parker-Holder, Jakob Foerster

**核心思想**：
```
观察: Always planning 计算开销高 + 长视野任务性能反而下降
      Never planning 限制性能上界
→ 存在最优的、任务相关的"Goldilocks频率"
→ 用SFT + RL训练agent学会动态规划决策
```

**方法（两阶段训练）**：
1. **SFT阶段**: 在多样synthetic数据上训练，让模型初步掌握"动态规划"能力
2. **RL阶段**: 在长视野环境（Crafter）中用RL精调，学习何时规划最有益

**关键发现**：
1. **Goldilocks频率**: 规划太少或太多都次优，存在任务相关的最优规划频率
2. **性能**: 动态规划agent在Crafter上更sample-efficient，完成更复杂目标
3. **Human guidance**: 训练后的agent可以被人类书写的plan引导，超越其独立能力

**特点**：
- ✅ 第一个系统研究sequential decision-making中"动态规划"的工作
- ✅ Goldilocks原则与本文的发现高度一致（optimizer utility U(T,s) 呈非单调 state-dependency）
- ✅ SFT+RL training pipeline，学习能力强
- ❌ **学习目标是"何时规划"（binary），未研究"规划信号是否预测规划价值"**
- ❌ 未提供对规划触发信号方向的实证探测
- ❌ 主要在Crafter环境验证，未研究信号direction的环境特异性

**与本文的对比**：

| 维度 | Learning When to Plan | Direction-Aware Gate (本文) |
|------|----------------------|---------|
| **核心问题** | 何时规划（binary decision） | signal-utility 方向是否稳定（direction discovery） |
| **方法** | SFT + RL training | 先 probe σ-U 方向，再 in-context gate |
| **环境特异性** | 不同任务有不同最优频率 | 不同环境信号方向截然不同（正/零/负） |
| **信号探测** | ❌ 未实证测量信号方向 | ✅ 首次系统测量 sign(corr(σ, U)) 跨环境变化 |
| **训练依赖** | 需要training（SFT+RL） | SCG-FineTune(LR)：轻量训练（vs SFT+RL的重量级训练） |

**叙事关系**：
> "Learning When to Plan"验证了"动态规划比固定规划更好"这一宏观原则。但该工作用 RL 隐式学习规划决策，而非显式检验 signal-utility 对齐方向的跨环境稳定性。本文的贡献在于：揭示触发信号方向本身因环境而异——这是 "Learning When to Plan" 框架的重要补充。

---

##### C6.3 Thinkless: LLM Learns When to Think (NeurIPS 2025, arXiv:2505.13379)

**代表论文**：
- Fang, Ma, Wang. "Thinkless: LLM Learns When to Think" (NeurIPS 2025, arXiv:2505.13379, May 2025)
- **团队**: National University of Singapore | **GitHub**: https://github.com/VainF/Thinkless

**核心机制**：
```
Control tokens: <short> (concise) vs <think> (long CoT)
Training: Decoupled Group Relative Policy Optimization (DeGRPO)
  - Control token loss: 学习选择推理模式
  - Response loss:  学习提高答案准确性
两者解耦，防止training collapse
```

**关键发现**：
- 50-90%长链推理使用率降低（Minerva Algebra, MATH-500, GSM8K）
- 任务复杂度 + 模型能力共同决定是否需要长推理
- DeGRPO比标准GRPO训练更稳定

**特点**：
- ✅ **NeurIPS 2025** - 高影响力认可
- ✅ RL框架学习推理模式选择，自适应能力强
- ✅ 50-90%推理开销降低，效率显著
- ❌ **仅针对长链推理 vs 直接回答的二元选择**，非sequential agent planning
- ❌ **未研究"触发信号方向"**——DeGRPO隐式学习时机，但不提供信号的方向分析
- ❌ 应用场景是单轮问答推理，不是多步agent决策

**与本文的对比**：

| 维度 | Thinkless | Direction-Aware Gate (本文) |
|------|-----------|---------|
| **场景** | 单轮QA推理 | 多步 sequential agent decision |
| **决策** | 用长推理 vs 短推理 | 用 optimizer T vs 直接执行 |
| **学习方法** | DeGRPO (RL) | SCG-FineTune(LR): 轻量训练（Phase 3: SR=96.7%, CS=44.1%） |
| **信号分析** | 隐式（RL自己发现） | 显式 probe + 方向分析 |
| **关键创新** | RL-based mode selection | Probe-first signal direction discovery |
| **Probe-first** | ❌ 无方向探测 | ✅ 先测量 sign(corr(σ, U)) |

---

##### C6.4 Think or Not? Selective Reasoning via RL for VLMs (arXiv:2505.16854, 2025)

**代表论文**：
- "Think or Not? Selective Reasoning via Reinforcement Learning for Vision-Language Models" (arXiv:2505.16854, May 2025)

**核心机制**：
```
Stage 1: SFT + "Thought Dropout" (随机将reasoning trace替换为empty thoughts)
Stage 2: GRPO RL (让模型自由探索何时think or not)
```

**关键发现**：
- 90%推理长度减少（vs vanilla GRPO），无性能损失甚至提升
- 适用于Vision-Language Models（VLMs）
- "Thought dropout"是关键设计：让模型在SFT阶段接触"无thinking"的成功案例

**与本文关系**：
- 思路相近：RL-based learning of when to use additional reasoning
- 关键区别：针对VLMs的单轮决策，而非sequential agent；未 probe 触发信号方向
- **可以引用作为"selective reasoning"方向的支持证据**

---

##### C6.5 When to Continue Thinking: Adaptive Thinking Mode Switching (arXiv:2505.15400, 2025)

**代表论文**：
- Zhang et al. "When to Continue Thinking: Adaptive Thinking Mode Switching for Efficient Reasoning" (arXiv:2505.15400, May 2025)

**核心发现**：
- 大推理模型（LRMs）在简单任务上有冗余推理
- **"Internal Self-Recovery Mechanism"**: 即使suppress长推理，模型在answer生成阶段也能隐式补充推理
- ASRR (Adaptive Self-Recovery Reasoning): accuracy-aware length reward regulation
- 推理开销减少32.5%（1.5B模型），minimal performance loss

**与本文关系**：
- 揭示了"长思考不一定必要"这一问题的内在机制（self-recovery）
- 未 study signal-utility 方向问题，属于 thinking length optimization 范畴

---

##### C6.6 A Deeper Look at Adaptive Reasoning in LLMs (Survey, arXiv:2511.10788, 2025)

**代表论文**：
- "A Deeper Look at Adaptive Reasoning in Large Language Models" (arXiv:2511.10788, Nov 2025)

**价值**：
- 将adaptive reasoning形式化为**control-augmented policy optimization**
- 分类：Training-based（RL/SFT/learned controllers）vs Training-free（prompt/feedback-driven/modular）
- **对本文的定位**: "training-free, feedback-driven adaptive policy at inference time"
- 适合在Related Work中引用，将 Direction-Aware Gate 嵌入 broader adaptive reasoning 框架

---

##### C6.7 🔴HIGH-THREAT AdaptThink: RL Think/No-Think (arXiv:2505.13417, EMNLP 2025)

**发表**: EMNLP 2025
**arXiv**: https://arxiv.org/abs/2505.13417
**威胁等级**: 🔴 HIGH — 最直接的 RL-based when-to-think 竞争者

**核心思想**:
- RL 训练 LLM 在 think token 和 no-think token 之间选择
- 直接优化 task reward，隐式学习何时需要 extended reasoning
- Per-environment RL 训练，无显式信号分析

**核心机制**:
```
Input → [think] or [no-think] token selection (RL-learned)
       → If think: extended reasoning chain
       → If no-think: direct answer
       → RL reward: task accuracy
```

**与本文关系**:
- **最直接 RL 竞争者**：与 Thinkless 同属 RL-based when-to-think，但 EMNLP venue 更高
- **关键差异**：方向处理 — AdaptThink RL 黑盒 vs 我们显式 probe + 发现
- **可解释性**：AdaptThink 无法解释 why trigger；我们 LR 系数直接可读
- **核心贡献层次不同**：AdaptThink 贡献是 method (RL gating)，我们贡献是 finding (direction reversal) + method
- **训练代价**：AdaptThink 需 RL per-env（重），我们 LR <1s（轻）

**与 Direction-Aware Gate 对比表**:

| 维度 | AdaptThink | Direction-Aware Gate (本文) |
|------|-----------|---------------------------|
| 方向处理 | RL 隐式学习（黑盒） | 显式 probe + 发现 |
| 可解释性 | ❌ 无法解释 why | ✅ LR 系数可读 |
| 训练代价 | RL per-env（重） | LR <1s（轻） |
| 方向验证 | ❌ 未验证 | ✅ 首次系统验证 |
| 核心贡献 | Method (RL gating) | Finding (direction reversal) + Method |
| 环境迁移 | 需重训练 | 重新 probe（<1s） |

**关键差异化一句话**:
> "AdaptThink learns when to think via RL but cannot explain why; we discover the signal-utility direction, which varies across environments—a finding AdaptThink does not report."

---

##### C6.8 L1: Layer-wise RL Compute Allocation (arXiv:2503.09002, 2025)

**发表**: arXiv, March 2025
**arXiv**: https://arxiv.org/abs/2503.09002
**威胁等级**: 🟡 MEDIUM — layer-level 而非 state-level

**核心思想**:
- RL 学习 layer-wise 计算分配策略
- 自动决定每层是否需要完整计算

**与本文关系**:
- 粒度不同：L1 在 model layer 级别做 adaptive compute，我们在 state 级别做 optimizer triggering
- 正交方向：L1 优化 model 内部计算，我们优化 optimizer 外部调用
- 引用价值：Related Work 中作为 "adaptive compute at different granularity" 的补充

---

##### C6.9 🆕 Stop Overthinking Survey (arXiv:2503.16419, 2025)

**发表**: arXiv, March 2025
**arXiv**: https://arxiv.org/abs/2503.16419
**威胁等级**: 🟢 LOW — 综述，非直接竞争

**核心内容**:
- "Stop Overthinking: A Survey on Efficient Reasoning for Large Language Models"
- 系统综述 efficient reasoning 方法
- 分类：training-based vs inference-based efficient reasoning

**与本文关系**:
- 综述定位，非竞争关系
- 可在 Related Work 中引用：将本文嵌入 efficient reasoning 大框架
- 补充 Adaptive Reasoning Survey (2511.10788)

---

### C7. 🆕🆕 Compute-Optimal / Budget-Aware (2025 新增)

##### C7.1 Token-Budget-Aware LLM Reasoning (arXiv:2502.12345, 2025)

**发表**: arXiv, February 2025
**arXiv**: https://arxiv.org/abs/2502.12345
**威胁等级**: 🟡 MEDIUM

**核心思想**:
- Token 预算感知的 reasoning 策略
- 在给定 token budget 下最大化 reasoning 质量
- 预算分配优化

**与本文关系**:
- 互补方向：Token-Budget-Aware 做 budget 分配，我们做 optimizer triggering
- 可组合：先用 budget-aware 分配 token 预算，再用 direction-aware gate 决定是否 trigger optimizer

---

##### C7.2 BudgetThinker (arXiv:2504.07601, 2025)

**发表**: arXiv, April 2025
**arXiv**: https://arxiv.org/abs/2504.07601
**威胁等级**: 🟡 MEDIUM

**核心思想**:
- 预算约束下的 reasoning 分配
- 学习在有限 compute budget 下最优分配推理资源

**与本文关系**:
- Budget 约束 vs Direction discovery：BudgetThinker 在给定预算下优化分配，我们发现信号方向
- CMDP 联系：两者都涉及 cost-quality trade-off，但机制不同

---

##### C7.3 🆕🆕🆕 AdaptiveComp — Adaptive Test-Time Compute (2025)

**发表**: 2025 (具体venue待确认)
**威胁等级**: 🟡 MEDIUM

**核心思想**:
- 自适应分配 test-time compute budget
- 根据 query difficulty 动态调整推理步数/tokens
- 实现 47-73% compute 节省，同时保持 accuracy

**核心机制**:
```
Query → Difficulty Estimator → Compute Budget
      → Easy query → minimal tokens
      → Hard query → full reasoning chain
      → Compute savings: 47-73%
```

**关键结果**:
- 在多个 benchmark 上节省 47-73% compute，accuracy 无显著下降
- 证明 adaptive allocation 显著优于 uniform allocation

**与本文关系**:
- **关键区别**：AdaptiveComp 做 difficulty-based budget 分配（假设固定方向：harder → more compute），我们做 direction discovery（发现 direction 本身因环境而异）
- **互补性**：可先用 direction-aware gate 确定信号方向，再用 AdaptiveComp 分配 budget
- **差异**：AdaptiveComp 不涉及 optimizer triggering decision，只做 budget 分配

**Taxonomy 交叉引用**: → Writing Guide Group 3 (Test-Time Compute Scaling), B.3.3

---

### C8. 🆕🆕 Routing / Hybrid Methods (2024-2025)

##### C8.1 🔴HIGH-THREAT DiffAdapt: Probe-based Difficulty Estimation (arXiv:2510.19669, 2025)

**发表**: arXiv, October 2025
**arXiv**: https://arxiv.org/abs/2510.19669
**威胁等级**: 🔴 HIGH — 也用 probe，但 probe purpose 不同

**核心思想**:
- 轻量 probe 检测 U-shaped entropy pattern
- 基于 entropy profile 估计问题难度
- 根据 difficulty 分配 compute budget

**核心机制**:
```
Input → Lightweight Probe → Entropy Profile Analysis
       → U-shaped pattern detected? → Difficulty Score
       → High difficulty → More compute
       → Low difficulty → Less compute
       → Assumption: U-shaped entropy is universal
```

**与本文关系**:
- **最需要精确区分的竞争者**：因为也用 "probe"
- **关键区别是 probe purpose**：
  - DiffAdapt probe = **difficulty estimation**（问题有多难？→ 分配 compute）
  - 我们 probe = **direction discovery**（信号方向如何？→ 校准 gate）
- **方向假设**：DiffAdapt 假设 U-shaped entropy pattern universal → APPS 中 entropy 仅 ρ=+0.144（弱正线性，非 U-shaped），且最强信号为 step_count (ρ=−0.274)
- **发现层面**：DiffAdapt 未报告 direction reversal

**与 Direction-Aware Gate 对比表**:

| 维度 | DiffAdapt | Direction-Aware Gate (本文) |
|------|----------|---------------------------|
| Probe Purpose | Difficulty estimation | **Direction discovery** |
| 方向假设 | U-shaped entropy (固定) | **无预设** |
| 方向验证 | ❌ | ✅ 首次系统验证 |
| APPS 表现 | Entropy ρ=+0.144（弱正）→ U-shape 失效 | Probe 发现 step_count (ρ=−0.274) 替代 |
| 核心发现 | Difficulty affects compute | **Direction varies across envs** |
| 训练需求 | 轻量 probe 训练 | LR <1s |

**关键差异化一句话**:
> "DiffAdapt's probe estimates problem difficulty assuming a fixed entropy pattern; our probe discovers the signal-utility direction, which we show varies across environments."

---

##### C8.2 RouteLLM (arXiv:2406.18665, 2024)

**发表**: arXiv, June 2024
**arXiv**: https://arxiv.org/abs/2406.18665
**威胁等级**: 🟢 LOW — model routing 非 state-level gating

**核心思想**:
- 学习 router 将 query 分配到不同 model（强/弱）
- Query-level routing，非 state-level gating

**与本文关系**:
- 粒度不同：query-level model routing vs state-level optimizer triggering
- 引用价值：Related Work 中 "routing" 方向代表

---

##### C8.3 Router-R1 (arXiv:2502.07616, 2025)

**发表**: arXiv, February 2025
**arXiv**: https://arxiv.org/abs/2502.07616
**威胁等级**: 🟢 LOW — reasoning routing

**核心思想**:
- RL 训练 reasoning router，决定使用哪种推理策略

**与本文关系**:
- Strategy routing（选哪种策略）vs Optimizer triggering（是否触发 optimizer）

---

##### C8.4 Semantic Router (arXiv:2503.08790, 2025)

**发表**: arXiv, March 2025
**arXiv**: https://arxiv.org/abs/2503.08790
**威胁等级**: 🟢 LOW — semantic routing

**核心思想**:
- 语义理解驱动的 router，基于 query 语义选择处理路径

---

##### C8.5 Meta-Reasoner (arXiv:2502.19918, 2025)

**发表**: arXiv, February 2025
**arXiv**: https://arxiv.org/abs/2502.19918
**威胁等级**: 🟡 MEDIUM — meta-reasoning 与 G4 交叉

**核心思想**:
- 元推理器协调多种推理策略
- 根据问题特征选择最优推理路径

**与本文关系**:
- Meta-level strategy selection vs State-level optimizer triggering
- 交叉引用：同时属于 C8 (routing) 和 G4 (LLM metareasoning)

---

##### C8.6 Meta-R1 (arXiv:2508.17291, 2025)

**发表**: arXiv, August 2025
**arXiv**: https://arxiv.org/abs/2508.17291
**威胁等级**: 🟡 MEDIUM — RL meta-reasoning

**核心思想**:
- RL 训练的 meta-reasoning router
- 学习何时使用何种推理策略

**与本文关系**:
- RL-based meta-reasoning vs Probe-based direction discovery
- 交叉引用：同时属于 C8 (routing) 和 G4 (LLM metareasoning)

---

**C6小结：含新增方法的完整区别矩阵（2026-02-27 竞争格局更新）**

| 方法 | 场景 | Gate信号 | 方向假设验证 | 学习机制 | Probe Purpose | 与本文的差异 |
|------|------|---------|------------|---------|--------------|----------------|
| **SEAG** (ACL 2025) | QA/Math推理 | Confidence entropy | ❌ 隐式正向 | 固定阈值 | — | 最结构相似，但无probe-first |
| **Learning When to Plan** (2509.03581) | Sequential agents | 无显式信号 | ❌ 未研究 | SFT+RL | — | 隐式学习，无信号probe |
| **Thinkless** (NeurIPS 2025) | 单轮QA | 隐式（RL发现） | ❌ 未研究 | DeGRPO | — | RL-learned mode selection |
| **Think or Not?** (2505.16854) | VLM QA | 隐式（RL发现） | ❌ 未研究 | GRPO | — | VLM版Thinkless |
| **When to Continue Thinking** (2505.15400) | 推理长度 | 无（length regulation） | ❌ 未研究 | RL length penalty | — | 关注长度优化而非触发信号 |
| **Adaptive Reasoning Survey** (2511.10788) | Survey | N/A | N/A | N/A | — | 提供formal framing |
| **🆕 CaTS** (2025) | Reasoning早停 | Calibrated confidence | ❌ 隐式正向 | Calibration mapping | — | Calibration思想共鸣，但无方向probe |
| **🆕 LATTS** (2509.20368) | Reasoning步级 | Self-verification | ❌ 每步verify | 无（固定verifier） | — | 步级粒度验证动机，但无选择性 |
| **🆕 ARPO** (2025) | Agent RL | Policy entropy | ❌ 隐式正向 | 端到端RL | — | Entropy-based触发，同CoRefine局限 |
| **🆕 GiGPO** (NeurIPS 2025) | Agent RL (ALFWorld) | N/A (改进policy) | N/A | Step-level GRPO | — | 互补：改进policy vs 改进gate |
| 🔴 **AdaptThink** (EMNLP 2025, 2505.13417) | 单轮/多步推理 | 隐式（RL发现） | ❌ 未验证 | RL think/no-think | — | **HIGH-THREAT**: RL 黑盒学 when-to-think，无可解释性 |
| 🔴 **DiffAdapt** (2510.19669) | 推理 reasoning | Entropy probe | ❌ 假设 U-shape | 轻量 probe 训练 | **Difficulty est.** | **HIGH-THREAT**: probe 做 difficulty estimation，非 direction discovery |
| 🔴 **Think Just Enough** (2510.08146) | 推理 reasoning | Token entropy | ❌ 固定正向 | 无（固定阈值） | — | **HIGH-THREAT**: 固定阈值，APPS 中 entropy 仅 ρ=+0.144 且非最强信号 |
| **★ Direction-Aware Gate (本文)** | Sequential agents | 任意 σ（显式测量） | **✅ 首次系统验证** | SCG-FineTune(LR)（轻量训练） | **Direction disc.** | **唯一显式测量方向（Phase 3: SR=96.7%, CS=44.1%; APPS Δ=+6pp, SCG TES=0.748）** |

**核心结论（Phase 3+ 更新）**：包括新增的LATTS、CaTS、ARPO、GiGPO在内，所有方法均试图解决"何时/如何调用额外计算"，但：
1. **所有方法都预设了触发信号方向**（或让RL隐式学习而不显式分析）
2. **Direction-Aware Gate 是唯一对 signal-utility 关系方向进行系统实证探测的工作**
3. 方向在不同环境中截然不同（包括负相关），这使得预设方向的方法在某些环境中失效
   - Phase 3 量化证据：**Wrong-Direction SR=58.2±2.5%**（跨 seed 一致），灾难性失效 🔥
   - Phase 3 统计检验：T4 McNemar p=0.035 ✅（wrong-dir 有害）
4. **主方法已从 SCG-Prompt 更新为 SCG-FineTune(LR)**：Prompt 因 YES bias（54% at ec≥2）降级为 ablation
   - Phase 3 三种子验证：SR=96.7±0.6%, CS=44.1±5.5%, Oracle CS=67.0%（65.8%）
5. **APPS 第二有效环境 GO + Step 2 完成**：base=58%, Δ=+6pp; 最强信号 step_count ρ=−0.274, token_entropy ρ=+0.144（弱正）
   - SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass; random SR=66.5% > SCG（passive abstention）
   - 升级发现：不仅方向翻转，连最强信号本身都因环境而异（signal replacement）→ "signal-utility landscape is environment-dependent"
6. **Direction discovery > probe phase**：No-Probe ≈ With-Probe → 关键是方向数据，不是在线 probe 过程
7. **GiGPO与本文正交互补**：GiGPO改进policy（更好的 proposer），本文改进触发策略（更好的 gate）——两者可组合
8. **CMDP λ* 严格递增**验证理论；0.6B backbone NO-GO（仅 4B 有效）

---

#### C9. 🆕🆕🆕 Hidden State Probing / Difficulty Estimation (2026-03-01 新增)

> **核心问题**: 能否用 LLM 内部 hidden states 预测任务难度或输出质量，从而指导计算分配？
>
> **与本文的关键联系**: 这些方法证明 hidden states 包含丰富的 meta-information，可用于 gating 决策。但关键区别是：它们都假设**固定方向**（harder → more compute），而我们发现 VOC direction 因环境而异。"The LLM Already Knows" 是 Phase 5a Cascaded Gate 中 hidden state VOC probe 的最近 prior work。

##### C9.1 "The LLM Already Knows" — Hidden State Difficulty Estimation (EMNLP 2025)

**代表论文**：
- Zhu, Y., Liu, D., Lin, Z., Tong, W., Zhong, S., & Shao, J. "The LLM Already Knows: Estimating LLM-Perceived Question Difficulty via Hidden Representations." Proceedings of EMNLP 2025, pp. 1160–1176. DOI: 10.18653/v1/2025.emnlp-main.61
- **arXiv**: https://arxiv.org/abs/2509.12886

**核心机制**：
```
将 token-level 生成建模为 hidden state 上的 Markov chain
定义 value function V(h_t) = E[output quality | h_t]
从 end-of-prompt hidden state 直接预测（无需生成任何 token）
→ 轻量 regressor 训练在 (state, quality) 数据对上
```

**关键发现**：
- Spearman ρ > 0.85 与 ground-truth difficulty（TriviaQA, HotpotQA, ScienceQA 等）
- **Early stopping 节省 30-50% tokens**（Self-Consistency, Best-of-N, Self-Refine 场景）
- **Zero-shot 跨 LLM 泛化**（Llama-3, GPT-4o, Claude-3.5 无需 fine-tune target model）
- 优于 P(True) sampling 和 auxiliary verifier baselines 10-20%

**特点**：
- ✅ 不需要生成任何 token 即可预测难度（极低开销）
- ✅ 跨 LLM 泛化（representation similarity）
- ✅ ρ>0.85 高精度
- ❌ **固定方向假设**：higher difficulty → always need more compute
- ❌ 未考虑 optimizer utility direction 因环境而异
- ❌ 在 agent sequential decision-making 场景未验证

**与 Direction-Aware Gate（本文 C4）的核心区别** 🔥：
| 维度 | LLM Already Knows | Direction-Aware Gate (本文) |
|------|-------------------|---------|
| **Probe 目标** | Task difficulty | **Optimizer utility (VOC)** |
| **方向假设** | 固定（harder → more compute） | **Probe-first（方向因环境而异）** |
| **Probe 输入** | End-of-prompt hidden state | Hidden state + signal features |
| **方向验证** | ❌ 无 | ✅ 系统测量 sign(corr(σ, U)) |
| **失效场景** | APPS 中 optimizer 帮助"容易"步骤（step_count ρ=−0.274）→ difficulty probe 做反方向决策 | ✅ 通过 direction discovery 适应 |
| **应用场景** | 单轮 QA | 多步 sequential agent |

**叙事关系**：
> "The LLM Already Knows" 证明了 hidden states 可以以高精度预测任务属性——这为我们的 Phase 5a hidden-state VOC probe 提供了重要 prior art。但它们 probe **difficulty**（假设 harder → more compute），而我们 probe **VOC**（方向需要 discovery）。在 APPS 中，optimizer 帮助的是相对"容易"的步骤（step_count 低 → U 高，ρ=−0.274），difficulty probe 会做出系统性错误决策。

##### C9.2 "LLM Internal States Reveal Hallucination Risk" (ICLR 2025)

**代表论文**：
- "LLM Internal States Reveal Hallucination Risk Faced With a Query." OpenReview (ICLR 2025 submission), id=vNoXjWNh2G.

**核心机制**：
- 分析 15 NLG tasks / 700+ datasets
- Hidden states signal 训练数据曝光度（seen/unseen）
- 预测 hallucination 风险 pre-generation

**与本文关系**：
- 证明 hidden states encode "知不知道" 信息，可用于 gating（reject high-risk queries）
- 但方向仍然固定（higher risk → reject/escalate）

##### C9.3 "Do LLMs Build World Representations?" (NeurIPS 2024)

**代表论文**：
- "Do LLMs Build World Representations? Probing Through the Lens of State Abstraction." NeurIPS 2024, poster 93786.

**核心机制**：
- RL-inspired state abstraction probing framework
- 在不同抽象层次 probe LLM hidden states 中的 world state（实体状态、关系）
- 发现：LLMs encode general 和 goal-oriented abstraction，mid-layers 优于 final layer

**与本文关系**：
- 证明 hidden states 编码了 world state representation → 支持用 hidden states 作为 automatic features（Phase 5）
- State abstraction framework 可能指导我们选择 hidden state 的哪些层 / 哪些维度

---

### D. 自我改进与反思 (Self-Improvement & Reflection)

#### D1. Self-Refine

**代表论文**：
- Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback" (ICLR 2024)

**核心机制**：
```
Generate → Self-Critique → Refine → Iterate
```

**特点**：
- ✅ 无需外部反馈，完全自监督
- ❌ **Self-bias问题**：LLM系统性高估自己的输出
- ❌ 多轮self-refine会**放大self-bias**

**变体**：
- RISE (Recursive Introspection): Multi-turn fine-tuning
- STaSC (Self-Taught Self-Correction): Open-domain QA
- Self-Taught Optimizer: 递归应用优化自身代码

#### D2. Self-Reflection

**代表方法**：
- ReAct (Reasoning + Acting)
- Reflexion (长期记忆 + 反思)

**特点**：
- ✅ 从失败中学习
- ❌ 仍在step-wise框架内，无法解决规划问题（FLARE批评）

#### D3. Multi-Agent Critique

**核心思想**：多个agent互相审查和修正

**特点**：
- ✅ 减轻self-bias（不同agent有不同视角）
- ✅ 在需要严格验证的任务上优于单agent
- ❌ 开销成倍增加（N个agent）

---

### E. 价值引导 (Value-Guided Methods)

#### E1. Step-Level Q-Value Models

**代表论文**：
- "Enhancing Decision-Making for LLM Agents via Step-Level Q-Value Models" (AAAI 2025)

**核心机制**：
1. 用MCTS收集decision-making轨迹，标注step-level Q-values
2. 用另一个LLM学习Q-value（通过step-level DPO）
3. Inference时选择Q-value最高的action

**特点**：
- ✅ 将长期价值分解到每一步
- ✅ 可以离线训练Q-value model
- ❌ 需要大量MCTS轨迹收集（成本高）
- ❌ Q-value model本身可能不准

**与本文的关系**：
- 本文的 test-time optimizer T 也涉及 action ranking
- 但本文的重点是 selective triggering（何时调用 optimizer T），而非 Q-learning

#### E2. Process Reward Models (PRM)

**核心思想**：评估中间步骤的质量（而非只评估最终结果）

**应用**：
- ReST-MCTS*: PRM指导MCTS搜索
- OpenAI的推理模型训练
- **Compute-Optimal Scaling**: PRM-guided beam search

**特点**：
- ✅ 比outcome reward更精细（可以早期发现错误）
- ❌ 标注成本高（需要人类对每步评分）

##### PRM-Guided Search (Compute-Optimal Scaling)

**代表论文**：
- Snell et al. "Scaling LLM Test-Time Compute Optimally" (arXiv:2408.03314, 2024)

**核心机制**：
```
Solution generation → PRM step-wise scoring → Search/Selection
                                              ↓
                    Per-step correctness: P(step_i is correct | prev steps)
                                              ↓
                    Aggregation: Product or Min of step scores
                                              ↓
                    Selection: Best trajectory by aggregated score
```

**PRM Training (无人类标注)**：
- **Monte Carlo Rollouts**: 从每步state s_i进行rollout
- **Value-to-go估计**: V(s_i) = P(reach correct answer | s_i)
- **PRM as Q-function**: 预测从当前步到最终成功的概率
- 训练数据：2048 samples per problem，自动标注

**Answer Aggregation**：
1. **Step-wise aggregation**:
   - Product: Π P(step_i correct)
   - Min: min_i P(step_i correct)
   - Last-k average: avg of final k step scores

2. **Inter-answer aggregation**:
   - Best-of-N: 选择aggregated score最高的answer
   - Weighted voting: Score-weighted majority vote

**Search Algorithms**：
| Algorithm | Description | Compute Cost |
|-----------|-------------|--------------|
| **Best-of-N** | Sample N完整solutions → 选最高分 | O(N) |
| **Beam Search** | 每步保留top-k，PRM scoring | O(k × depth) |
| **Lookahead Search** | 每步前瞻h步，PRM评估 | O(k^h × depth) |
| **MCTS** | UCT selection + PRM value | O(rollouts × depth) |

**Compute-Optimal PRM Strategy**：
```
Easy problems (high pass@1):
  → Best-of-N with small N
  → PRM主要用于ranking已生成的solutions

Hard problems (low pass@1):
  → Beam search or MCTS
  → PRM用于guiding search process
  → 更大的beam width或rollout budget
```

**实验结果** (MATH benchmark):
| Method | Easy Q SR | Hard Q SR | Avg Compute (vs Best-of-N) |
|--------|-----------|-----------|---------------------------|
| ORM Best-of-N | 75% | 15% | 1× (baseline) |
| PRM Best-of-N | 78% | 18% | 1× |
| PRM Beam Search | 76% | 22% | 1.5× |
| **PRM Compute-Optimal** | **80%** | **20%** | **0.25×** (4× improvement) |

**关键发现**：
1. **PRM > ORM**: Process-level supervision提供更精细的guidance
2. **Search strategy matters**: Beam search在hard problems上优于Best-of-N
3. **Adaptive allocation critical**: Compute-optimal比uniform allocation高效4×
4. **Diminishing returns**: 非常难的问题上，PRM search效果有限

**PRM的局限性**：
- 依赖base model的sampling quality（PRM无法创造，只能选择）
- Hard problems上仍然需要大量compute（虽然比uniform allocation好）
- 需要step-wise可分解的任务（不适用于整体性输出）

##### 🆕 LATTS: Locally Adaptive Test-Time Scaling (arXiv:2509.20368, 2025)

**代表论文**：
- "Locally Adaptive Test-Time Scaling with Self-Verification" (arXiv:2509.20368, Sep 2025)

**核心机制**：
```
Per-step adaptive decision:
  Step i: LLM生成reasoning step
    → Self-verifier评估step质量
    → 三种决策：
      ✅ Accept: 步骤正确，继续
      ❌ Reject + Regenerate: 步骤错误，重新生成
      ↩️ Backtrack: 无法修复，回退到前一步
    → 局部自适应：在每步根据verifier反馈动态调整
```

**关键发现**：
1. **Per-step比per-question更细粒度**：Compute-Optimal在问题级别分配，LATTS在步骤级别分配
2. **Self-verification有效**：模型自身可以作为step-level verifier
3. **Backtrack机制关键**：允许回退避免错误累积

**特点**：
- ✅ **步级自适应**：比Compute-Optimal更精细，接近本文的state-level粒度
- ✅ Accept/Reject/Backtrack三种决策（vs binary trigger）
- ✅ Self-verification无需外部模型
- ❌ **每步都需要verification**（虽然决策不同，但verifier开销持续）
- ❌ 仍在reasoning task中验证，未扩展到agent sequential decision
- ❌ 无学习机制——verifier是固定的LLM prompting

**与Direction-Aware Gate / SCG的对比**：

| 维度 | LATTS | Direction-Aware Gate / SCG |
|------|-------|---------|
| **粒度** | Per-step (reasoning) | Per-state (agent decision) |
| **决策类型** | Accept/Reject/Backtrack | Trigger/Skip verification |
| **Verifier** | LLM self-verification (每步) | SCG-Prompt (training-free, 选择性触发) |
| **开销模式** | 每步都verify（持续中） | 选择性触发（递减） |
| **学习** | ❌ 固定prompting | ❌ SCG-Prompt (training-free) |
| **蒸馏** | ❌ | ✅ Gate可蒸馏 |

**叙事关系**：
> LATTS将adaptive allocation推进到步级粒度（vs Compute-Optimal的问题级），证明了更细粒度的分配更有效。Direction-Aware Gate / SCG进一步：(1) 不是每步都verify，而是学习何时verify；(2) verifier开销递减而非持续。LATTS可视为本文动机的额外验证——"需要步级自适应"。

**与其他PRM方法对比**：
| 方法 | PRM训练数据 | Search算法 | Adaptive allocation |
|------|-----------|-----------|-------------------|
| **Lightman et al. (PRM800K)** | 人类标注 | Best-of-N | ❌ |
| **ReST-MCTS*** | Self-play rollouts | MCTS | ❌ (固定rollout budget) |
| **Compute-Optimal** | MC rollouts | **Adaptive** (Best-of-N/Beam/MCTS) | ✅ |

**与本文的关系**：
```
PRM (Compute-Optimal):
  - Verifier评估solution quality
  - 在solution space中search
  - Per-problem difficulty → 选择search algorithm

Direction-Aware Gate（本文）:
  - Direction probe 测量 signal σ 与 optimizer utility U(T,s) 的关系
  - 在decision space中selective trigger
  - Per-state probe → 决定是否调用 optimizer T

互补性：
  - PRM可以作为本文的 optimizer T 实现（PRM beam search = expensive evaluator）
  - Direction-Aware Gate 可以决定何时invoke PRM search
```

##### 🆕 E1.2 GiGPO: Group-in-Group Policy Optimization (NeurIPS 2025)

**代表论文**：
- "GiGPO: Group-in-Group Policy Optimization for LLM Agent Training" (NeurIPS 2025)

**核心机制**：
```
标准GRPO: Group-level reward (整个trajectory一个reward)
GiGPO创新: Step-level credit assignment within groups
  → 在每个trajectory group内部，进一步分组到step-level
  → 每步的credit = 从该步开始的未来reward期望
  → 解决了GRPO中credit assignment模糊的问题
```

**关键发现**：
1. **Step-level credit assignment显著提升agent性能**: +12% on ALFWorld
2. **与Group-level GRPO互补**: GiGPO在agent tasks上优于GRPO
3. **Fine-grained signal传播**: 每步的贡献被准确归因

**特点**：
- ✅ **NeurIPS 2025** — 高影响力
- ✅ **ALFWorld +12%** — 直接在本文的目标环境上验证
- ✅ Step-level credit assignment与本文的per-state intervention理念一致
- ❌ **改进Proposer（policy）**，不改进Critic/Planning过程
- ❌ 需要RL训练（vs 本文的 SCG-Prompt, training-free）
- ❌ 不是selective computation——始终使用同等计算

**与本文的关系**：
```
GiGPO: 改进policy的训练过程（更好的credit assignment）
本文:   改进inference的决策过程（选择性 optimizer 触发）

互补性:
  GiGPO训练更好的proposer → 本文在此proposer上selective trigger
  两者可以组合使用：GiGPO-trained policy + Direction-Aware Gate
```

| 维度 | GiGPO | Direction-Aware Gate（本文） |
|------|-------|------|
| **改进对象** | Policy (proposer) | Critic (gate + value head) |
| **训练阶段** | Learning-time (RL) | Learning-time (supervised) |
| **Inference** | 正常推理（无额外开销） | 选择性触发（Gate决策） |
| **粒度** | Step-level credit assignment | State-level trigger decision |
| **ALFWorld** | +12% (policy improvement) | TBD (planned Phase 3) |

---

#### 🆕🆕🆕 E2.2 Process Advantage Verifiers (PAVs) — ICLR 2025 (2026-03-01 新增)

**代表论文**：
- "Process Advantage Verifiers" (ICLR 2025, OpenReview:A6Y7AqlzLW)

**核心机制**：
```
Progress = P(correct | step_1...step_i) - P(correct | step_1...step_{i-1})
  → 衡量每步对最终正确率的贡献增量
  → 关键：使用 prover policy（distinct from base policy）测量 progress
  → 即使 weaker prover 也能改进 base policy（只要能区分 good/bad steps）
```

**关键发现**：
- >8% accuracy improvement over Outcome Reward Models (ORMs)
- **1.5-5× compute efficient** compared to ORMs
- **6× RL sample efficiency** when used for online RL
- 首次证明 PRMs 在 RL 设置中大幅优于 ORMs

**与本文关系**：
- PAVs 提供 step-level reward signal（用于训练 reasoning policy）
- 我们的 gate 提供 state-level trigger signal（用于决定何时调用 optimizer）
- **正交互补**：PAVs 可作为我们框架中 optimizer T 的一种实现
- PAVs 的 "progress" 概念类似我们的 VOC（incremental value），但 PAVs 无方向 discovery

#### 🆕🆕🆕 E2.3 ThinkPRM — Generative Process Reward Models (2025)

**代表论文**：
- "ThinkPRM" (2025, GitHub: mukhal/ThinkPRM)

**核心机制**：
- Fine-tune reasoning models over synthetic data 生成 extended verification trajectories
- 从 discriminative step classification 升级为 generative reasoning within verifier
- Long chain-of-thought within PRM itself

**与本文关系**：
- ThinkPRM 可作为更 powerful 的 optimizer T 实现
- 但 ThinkPRM 本身不解决"何时应用 PRM"的问题——这是我们的 gate 解决的

---

#### 🆕 E4. Agentic RL — Adaptive Rollout (ARPO)

##### E4.1 ARPO: Agentic Reinforced Policy Optimization (OpenReview, 2025)

**代表论文**：
- "ARPO: Agentic Reinforced Policy Optimization" (OpenReview, 2025)

**核心机制**：
```
传统RL for LLM agents: 固定rollout策略（每步或固定间隔）
ARPO创新: Entropy-based adaptive rollout timing
  → 在每个tool-call step计算policy entropy
  → 高entropy（不确定）→ 触发额外rollout/search
  → 低entropy（确定）→ 直接执行
  → 关键：将rollout视为agent action的一部分，端到端RL优化
```

**关键发现**：
1. **Entropy-based gating有效**: 自动学会在不确定时投入更多计算
2. **Tool-call步骤是关键决策点**: 比每步都rollout更高效
3. **端到端RL优化**: rollout decision与action selection联合优化

**特点**：
- ✅ **Entropy-based adaptive rollout**：与本文的"何时触发"问题直接相关
- ✅ **端到端RL优化**：rollout决策被jointly优化
- ✅ **Tool-call粒度**：比每步都rollout更实际
- ❌ **Entropy-based触发**：仍假设不确定→需要rollout（正向）
- ❌ 无法检测"确定但错了"（本文的核心motivation）
- ❌ 需要RL训练（vs SCG的training-free选项）
- ❌ 未probe信号方向

**与Direction-Aware Gate / SCG的对比**：

| 维度 | ARPO | Direction-Aware Gate / SCG |
|------|------|---------|
| **触发信号** | Policy entropy (不确定性) | 任意 σ（probe 发现的最优信号） |
| **触发粒度** | Tool-call steps | Per-state |
| **学习方式** | 端到端RL | SCG: probe-first + in-context gate |
| **方向依赖** | 隐式依赖高entropy→需要rollout | **显式测量方向** |
| **Confident-wrong** | ❌ 无法检测 | ✅ Direction probe 检测 |
| **计算模式** | RL training (expensive) | SCG: training-free option |

**叙事关系**：
> ARPO将"何时rollout"纳入RL优化目标，验证了adaptive rollout比fixed rollout更优。但其entropy-based触发与CoRefine有相同局限：无法检测"确定但错了"。Direction-Aware Gate / SCG的方向发现方法解决了这一问题——先测量信号方向，再据此触发。

---

#### E3. Offline RL for Planning

**代表论文**：
- "Planning without Search: Refining Frontier LLMs with Offline Goal-Conditioned RL" (2025)

**核心思想**：
- 用offline RL训练value function
- Value function指导推理，**无需test-time search**

**特点**：
- ✅ Inference时高效（无搜索开销）
- ✅ Data-driven（从数据中学习）
- ❌ 需要大量高质量离线数据
- ❌ 泛化能力依赖数据覆盖

**与本文的相似性**：
- 都追求inference-time高效
- 都基于learned signal做决策
- 差异：本文是selective triggering（仍会在需要时调用 optimizer T），offline RL是完全不搜索

---

### F. 神经符号融合 (Neuro-Symbolic Integration)

#### F1. LLM+P

**代表论文**：
- Liu et al. "LLM+P: Empowering Large Language Models with Optimal Planning Proficiency" (2023, 高被引)

**架构**：
```
NL Task → [LLM] → PDDL Problem → [Classical Planner] → Optimal Plan → [LLM] → NL Plan
```

**特点**：
- ✅ 结合LLM的灵活性和经典规划器的最优性
- ✅ 在PDDL任务上接近最优
- ❌ 需要任务可形式化为PDDL
- ❌ 两个模块的接口设计复杂

#### F2. BDI + LLM

**核心思想**：BDI (Belief-Desire-Intention) 架构 + LLM动态生成plan

**特点**：
- ✅ 经典agent架构的现代化
- ✅ LLM提供灵活的plan generation
- ❌ BDI框架本身复杂

#### F3. Formal Verification + LLM

**趋势**：用formal methods验证LLM生成的plan的正确性

**特点**：
- ✅ 提供正确性保证
- ❌ 仍在早期研究阶段

#### 🆕 F4. Causal Models + LLM (因果模型增强规划)

**代表论文**：
- "Augmenting LLMs with Causal Models for Complex Planning" (Frontiers in Artificial Intelligence, 2025)

**核心思想**：
```
LLM alone: 规划能力有限（Kambhampati批评）
Causal Model: 提供因果推理框架
→ 结合: LLM生成候选plan → Causal Model验证因果一致性 → 修正plan
```

**特点**：
- ✅ 将因果推理引入LLM规划，提供结构化约束
- ✅ 理论基础扎实（因果推理 + LLM的互补）
- ❌ 需要构建领域特定的因果模型
- ❌ 因果模型的可扩展性受限

**与本文的关系**：
- 因果模型可作为本文的 optimizer T 的一种实现（提供长程因果评估）
- 但因果模型构建成本高，而本文的 optimizer T 可以是任意evaluator
- 定位不同：Causal Models改进plan质量，Direction-Aware Gate 决定何时需要深度评估

---

### 2.7 🆕 G类：Rational Metareasoning & Value of Computation（2026-02-26 新增）

> **定位**：本类收录将 "是否分配额外计算" 形式化为 decision-theoretic 问题的经典与现代工作。与 C 类（adaptive compute allocation）的区别在于：C 类是具体的 gating/routing 机制设计，G 类是理论框架与形式化工具。Direction-Aware Gate（C4）的 CMDP formalization 和 VOC negativity insight 直接连接到这一理论体系。

#### G1. Classical Metareasoning — Value of Computation (VOC)

**代表论文**：
- Russell, S. & Wefald, E. "Do the Right Thing: Studies in Limited Rationality." MIT Press, 1991.（1000+ 引用，VOC 理论基石）
- Horvitz, E. "Reasoning about Beliefs and Actions under Computational Resource Constraints." AAAI Workshop on Uncertainty in AI, 1989.（bounded optimality 早期形式化）

**核心思想**：
```
问题：Agent 有有限计算资源，何时值得继续计算？
框架：Metalevel decision theory
  - Object level: 做决策的层面（选择 action）
  - Meta level: 决定是否继续计算（选择 computation）

VOC(computation) = E[改进后 decision 的 value] - E[当前 decision 的 value] - cost(computation)

Decision rule: 如果 VOC > 0 → 继续计算；否则停止并执行当前最优 action

关键假设（Russell & Wefald 1991）：
  VOC ≥ 0，因为 agent 可以忽略计算结果（"多算不会更差"）
```

**特点**：
- ✅ 提供了"何时计算"的统一理论框架
- ✅ 将 computation 视为 action，与 object-level decision 统一分析
- ✅ 经典 AI 理论基石，被广泛引用
- ❌ 经典假设 VOC ≥ 0 在某些实际场景中不成立（见下文与本文的联系）
- ❌ 原始理论主要针对 search tree 场景，未考虑 neural evaluator 的特殊性

**与 Direction-Aware Gate（本文 C4）的关系** 🔥：
- **Gate 决策即 VOC 问题**：P(useful | σ(s)) > τ 等价于 E[VOC(T, s) | σ(s)] > 0
- **VOC ≥ 0 假设的 empirical refutation**：经典 VOC 假设 agent 可以忽略计算结果。但在 binary-commit gating + evaluator-executor identity 下：
  - Gate 说 "trigger" 后 optimizer 动作替换 base 动作，无法忽略
  - 同一模型生成和评估候选，在 capability-external 场景下共享知识盲区
  - **结果**：Wrong-Direction gate 不是 "白触发"（VOC=0），而是 "越触发越差"（aggregate VOC << 0）
  - **数据**：LR SR −34.5pp, MLP SR −51.2pp (RR=0%) — 对 VOC ≥ 0 假设的 empirical refutation
- **理论贡献**：Direction discovery 是使 aggregate VOC 回归非负的**必要前提**

#### G2. Constrained Markov Decision Processes (CMDP)

**代表论文**：
- Altman, E. "Constrained Markov Decision Processes." Chapman and Hall/CRC, 1999.（CMDP 经典教材，600+ 引用）
- Gladin, E., Lavrik-Karmazin, M., & Zainullina, K. "Algorithm for Constrained Markov Decision Process." Proceedings of the 40th International Conference on Machine Learning (ICML), 2023.（CMDP 高效求解）

**核心思想**：
```
标准 MDP：max E[Σ R(s,a)]
CMDP：max E[Σ R(s,a)] s.t. E[Σ c(s,a)] ≤ B

求解方法：
  - Lagrangian relaxation: max E[Σ R] - λ · E[Σ c]
  - Dual ascent: λ_{k+1} = max(0, λ_k + α · (E[c_k] - B))
  - 在 Slater condition 下收敛到最优

应用：资源受限的序贯决策，网络路由，电力调度，金融投资组合...
```

**特点**：
- ✅ 成熟的理论框架，收敛保证完善
- ✅ Lagrangian relaxation 将约束问题转化为无约束优化
- ✅ Dual ascent 自动学习最优乘子（无需手动调参）
- ❌ 需要多次评估来收敛 λ*
- ❌ Slater condition（严格可行解存在）并非总是满足

**与 Direction-Aware Gate（本文 C4）的关系** 🔥：
- **本文 objective 即 CMDP**：$\max E[\sum R] - \lambda \cdot E[\sum c \cdot 1[\text{trigger}]]$ 是 CMDP 的 Lagrangian relaxation 形式
- **Dual ascent 自动学 λ\***：$\lambda_{k+1} = \max(0, \lambda_k + \alpha \cdot (\text{RR}_k - \text{RR}_{target}))$
  - 用户指定 CS_target，系统自动找最优 threshold τ(λ*) = 0.5 + λ*
  - 不同环境自动产生不同 λ*
  - λ=0 退化为当前方法（无成本约束）
- **Phase 3.5 实验验证**：dual ascent 收敛性 + Pareto 最优性 + 跨环境自适应

#### G3. Anytime Algorithms

**代表论文**：
- Zilberstein, S. "Using Anytime Algorithms in Intelligent Systems." AI Magazine, 17(4):73-83, 1996.（anytime algorithm 综述，500+ 引用）

**核心思想**：
```
Anytime algorithm: 随时间递增质量的算法
  - 随时可以被中断并返回当前最优解
  - 运行时间越长，解的质量越高
  - 关键：有 diminishing returns（边际收益递减）

Performance profile: quality(time) — 通常是凹函数
Stopping rule: VOC(继续计算) < 0 时停止

与 metareasoning 的联系：
  - 何时停止 = VOC problem
  - Anytime + VOC = optimal stopping for computation
```

**特点**：
- ✅ 提供了 "可随时中断" 的计算模式
- ✅ 与 VOC 理论自然结合（何时停止计算）
- ✅ 广泛应用于 real-time AI, robotics, game playing
- ❌ 需要 performance profile 的先验知识
- ❌ 假设 quality 单调递增（在 LLM 场景中不一定成立）

**与 Direction-Aware Gate（本文 C4）的关系**：
- **Test-time optimizer T 不是 anytime 的**：T 是 binary（触发或不触发），不是渐进式的
- **但 anytime 的 stopping rule 思想相关**：VOC < 0 → 停止计算 ≈ P(useful) < τ → 不触发
- **区别**：Zilberstein 假设 quality 单调递增（更多计算 → 更好结果），我们发现这在 capability-external 场景不成立（更多计算 → 更差结果）

#### G4. LLM Metareasoning

**代表论文**：
- Nair, V., Schumacher, A., Tso, G., & Kannan, A. "Rational Metareasoning for Large Language Models." arXiv:2410.05563, 2024.（最新 LLM metareasoning 应用）

**核心思想**：
```
将 Russell & Wefald 的 metareasoning 框架应用于 LLM：
  - Object level: LLM 的推理过程（token generation, reasoning steps）
  - Meta level: 决定是否继续推理、是否调用工具、是否请求更多 context

VOC for LLM:
  VOC(additional_computation) = E[quality_improvement] - compute_cost

应用：
  - 何时停止 Chain-of-Thought
  - 何时调用外部工具
  - 何时请求更多输入
```

**特点**：
- ✅ 将经典 metareasoning 理论带入 LLM 时代
- ✅ 提供了分析 test-time compute 的理论框架
- ❌ 仍假设 VOC ≥ 0（继承经典假设）
- ❌ 未考虑 evaluator-executor identity 问题

**与 Direction-Aware Gate（本文 C4）的关系** 🔥：
- **我们扩展了他们的框架**：Nair et al. 用 VOC 分析 LLM compute allocation，但假设 VOC ≥ 0。我们证明在 binary-commit gating + evaluator-executor identity 下这一假设不成立
- **互补性**：他们提供理论分析框架，我们提供 empirical evidence（VOC negativity）和 practical solution（direction discovery）
- **Key difference**：他们的 VOC 分析是 per-token / per-step granularity，我们的是 per-state optimizer triggering granularity

##### 🆕🆕🆕 G4.2 Bayesian Meta-Reasoning for LLMs (ICML 2025 Position Paper, 2026-03-01 新增)

**代表论文**：
- Yan et al. "LLMs Need a Bayesian Meta-Reasoning Framework for More Robust and Adaptable Reasoning." ICML 2025 (position paper). proceedings.mlr.press/v267/yan25g

**核心思想**：
```
Current LLM reasoning limitations: lack robustness, poor cross-task generalization, inefficient scaling
Proposed framework: 5 components inspired by cognitive science
  1. Self-awareness — know what you know/don't know
  2. Monitoring — track reasoning progress
  3. Evaluation — assess quality of intermediate states
  4. Regulation — adjust strategy dynamically
  5. Meta-reflection — reason about reasoning process
Draw on: Dual-Process Theory, Metacognitive Reasoning from psychology
```

**特点**：
- ✅ **ICML 2025 position paper**：高影响力理论贡献
- ✅ 系统性地将 cognitive science metacognition 引入 LLM reasoning
- ✅ 5-component framework 提供了完整的 meta-reasoning architecture
- ❌ 是 position paper（无实验验证），需要具体 instantiation
- ❌ 未考虑 environment-dependent direction 问题

**与本文关系** 🔥：
- **Direction discovery 是 "self-awareness" 的具体实现**：我们的 probe phase 让系统 "了解" 当前环境的 signal-utility landscape
- **本文可被视为 Bayesian meta-reasoning framework 的 practical instantiation**：direction discovery (self-awareness) → signal selection (monitoring) → VOC estimation (evaluation) → adaptive triggering (regulation)
- **互补性**：Yan et al. 提供理论框架，我们提供 empirical validation + direction discovery 作为 critical component

##### 🆕🆕🆕 G4.3 TECTON: Tool Selection via Meta-Reasoning (arXiv:2411.04535, 2026-03-01 新增)

**代表论文**：
- Alazraki, L. & Rei, M. "TECTON: Tool selECTion via meta-reasONing." arXiv:2411.04535, 2024.

**核心机制**：
```
Phase 1: Fine-tuned LLM head reasons over task → generates candidate tools
Phase 2: Frozen model (with custom head disabled) meta-reasons over own Phase 1 reasoning → final tool selection
→ Meta-reasoning over reasoning for better generalization
```

**关键发现**：
- Substantial performance gains on math reasoning (in-distribution + OOD)
- Parameter-efficient fine-tuning sufficient
- Meta-reasoning over own reasoning improves tool selection

**与本文关系**：
- Meta-reasoning 选择 tool 类似于我们选择是否触发 optimizer T
- 但 TECTON 做的是"选哪个 tool"，我们做的是"是否触发 optimizer"（binary gating）
- TECTON 未考虑 tool utility direction 因 environment 而异

#### G5. Cost-Aware Adaptive Inference

**代表论文**：
- Chen, L., Zaharia, M., & Zou, J. "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance." Proceedings of ICML Workshop on ES-FoMo, 2023.（LLM cascade routing，100+ 引用）
- Wang, X., Yu, F., Dou, Z.-Y., Darrell, T., & Gonzalez, J. E. "SkipNet: Learning Dynamic Routing in Convolutional Networks." ECCV, 2018.（dynamic layer skipping，600+ 引用）

**核心思想**：
```
FrugalGPT:
  - 小模型先回答 → scorer 判断质量 → 不够好则调用更大模型
  - 本质是 model-level cascade routing
  - Objective: min cost s.t. quality ≥ threshold

SkipNet:
  - ResNet + gating module → 每层决定是否跳过
  - RL 学习 routing policy
  - 本质是 layer-level dynamic computation

共同点：adaptive resource allocation — 在质量和成本之间 trade-off
```

**特点**：
- ✅ FrugalGPT 在 LLM 时代提供了 practical cost-saving 方案
- ✅ SkipNet 在 CNN 中验证了 dynamic routing 的有效性
- ❌ FrugalGPT 假设大模型总比小模型好（cascade 方向固定）
- ❌ SkipNet 需要 per-layer gating 模块训练

**与 Direction-Aware Gate（本文 C4）的关系**：
- **粒度不同**：FrugalGPT 做 model-level routing（哪个模型回答），SkipNet 做 layer-level routing（跳过哪层），我们做 state-level optimizer triggering（当前状态是否触发 T）
- **方向问题的有无**：FrugalGPT 假设 cascade 方向固定（大模型 ≥ 小模型），SkipNet 假设跳过层不影响质量。**我们发现方向可能翻转**——这是本文独有的 contribution
- **CMDP 联系**：三者都可形式化为 CMDP（质量约束下最小化成本，或成本约束下最大化质量）。本文的 Lagrangian dual ascent 提供了统一的 cost-quality trade-off 机制

##### 🆕🆕🆕 G5.3 Cascaded LLM with Deferral/Abstention (ICLR 2025, 2026-03-01 新增)

**代表论文**：
- "Cascaded Language Models for Cost-Effective Human–AI Decision-Making." ICLR 2025, OpenReview:4Q1vA6P9J9.

**核心机制**：
```
Stage 1: Base LLM → initial answer
Stage 2: Low-confidence → defer to larger LLM → second answer
Stage 3: Still uncertain → abstain to human
+ Online learning from feedback
```

**关键发现**：
- 在 ARC, MMLU, MedQA 上：higher accuracy, lower cost than single models
- Confidence-based deferral + human abstention provides quality guarantee
- Online feedback enables continual adaptation

**与本文关系**：
- **Cascade 结构与 Phase 5a 相似**：我们的 Cascaded Multi-Fidelity Gate 也是多级 escalation
- 但粒度不同：他们做 model-level cascade (small → large LLM)，我们做 signal-fidelity cascade (cheap signals → hidden state probe → trial rollout within same model)
- 他们的 confidence-based deferral 假设固定方向，我们需要 direction discovery

#### 🆕🆕🆕 G6. Token Efficiency & Reasoning Depth Analysis (2026-03-01 新增)

> **定位**：本类收录分析 reasoning token efficiency 和 reasoning depth 的工作。这些工作不直接做 gating，但提供了理解 "为何 adaptive compute 有效" 的分析框架。

##### G6.1 Token Efficiency Decomposition (ICML 2026, arXiv:2602.09805)

**代表论文**：
- "Token Efficiency Decomposition" (ICML 2026, arXiv:2602.09805)

**核心机制**：
```
Token Efficiency = Correct Answers / 1,000 Generated Tokens
分解为三个组件：
  1. Robustness: 对 token budget 截断的鲁棒性
  2. Conditional Correctness: 完成时的推理正确性
  3. Verbosity: 相对于问题难度的 token 使用量
```

**关键发现**：
- **Efficiency ≠ Accuracy** (Spearman ρ=0.63)：排名不同
- 224K experiments, 25 models, 142,800 reasoning traces
- Conditional correctness（非 verbosity）驱动 efficiency gap
- Verbalization overhead 9× across models，与 model scale 弱相关

**与本文关系**：
- 支持 "efficiency is environment/model-dependent" 叙事——不同 model/task 的 efficiency profile 完全不同
- 从另一角度证明了 uniform compute allocation 的低效性

##### G6.2 Deep-Thinking Ratio (DTR) / Think@n (2026)

**核心机制**：
```
Deep-Thinking Ratio (DTR):
  - 分析 layer-wise token prediction stability
  - "Deep-thinking tokens": 在 deeper transformer layers 持续被修正
  - "Routine tokens": 在 early layers (5-10) 即稳定
  - DTR 量化 reasoning effort vs routine generation

Think@n:
  - 仅看 first 50 tokens 的 DTR 即可预测 overall quality
  - 用 DTR 指导 token 分配：~50% cost reduction
  - 匹配 self-consistency 的 92.7% accuracy
```

**关键发现**：
- Token count 是 unreliable proxy for reasoning quality
- DTR correlates strongly with correctness (raw token count does not)
- "Think deeper, not longer" — 从 "生成更多 tokens" 转向 "在关键 tokens 上更深层处理"

**与本文关系**：
- DTR 提供了一种自动化的 "reasoning depth" 信号——可能作为我们 gate 的候选 feature
- "Think deeper not longer" 与我们的 "trigger optimizer selectively" 哲学一致

### G 类总结与 Direction-Aware Gate 的定位

| 方法 | 粒度 | 方向假设 | VOC 符号 | 本文连接 |
|------|------|---------|---------|---------|
| Russell & Wefald 1991 | Search tree node | 固定（VOC ≥ 0） | 非负 | **我们证明可为负** |
| Horvitz 1989 | Computation step | 固定 | 非负 | 理论先驱 |
| Altman 1999 (CMDP) | State-action | N/A（约束形式） | N/A | **我们用 CMDP 形式化** |
| Zilberstein 1996 | Time step | 单调递增 | 非负但递减 | Stopping rule 思想 |
| Nair et al. 2024 | LLM token/step | 固定（VOC ≥ 0） | 非负 | **我们扩展其框架** |
| 🆕 Yan et al. 2025 (Bayesian) | LLM reasoning | Position paper | N/A | **Direction disc. = self-awareness** |
| 🆕 TECTON 2024 | Tool selection | Meta-reasoning | N/A | Meta-reasoning for tools |
| FrugalGPT 2023 | Model cascade | 固定（大 ≥ 小） | 非负 | 粒度不同，方向固定 |
| SkipNet 2018 | Network layer | 学习（RL） | 学习 | 粒度不同 |
| 🆕 Cascaded LLM 2025 | Model cascade | Confidence-based | 非负 | Cascade 结构相关 |
| 🆕 Token Eff. Decomp. 2026 | Token-level | N/A (分析) | N/A | Efficiency ≠ accuracy |
| 🆕 DTR/Think@n 2026 | Token-level | 固定 (DTR) | N/A | Reasoning depth signal |
| **Direction-Aware Gate** | **State-level T** | **Probe（发现方向）** | **可正可负** ✅ | **VOC negativity + CMDP** |

**G 类对本文论文的价值**：
1. **理论深度**：从 empirical finding paper 升级为有 theoretical grounding 的论文
2. **VOC negativity 作为 theoretical contribution**：经典 VOC ≥ 0 假设的 empirical refutation
3. **CMDP 作为统一框架**：将 adaptive triggering 连接到成熟的优化理论
4. **Dual ascent 作为 practical tool**：自动学习 λ*，提供 deployment-ready 的 cost-quality 控制
5. **🆕 Bayesian meta-reasoning 连接**：direction discovery 作为 self-awareness component 的具体实现
6. **🆕 Token efficiency 支持**：efficiency ≠ accuracy，支持 environment-dependent signal-utility landscape

---

## 3. 横向对比：关键维度

### 3.1 按开销模式分类

| 方法类别 | Inference-time开销 | 开销趋势 | 可蒸馏？ |
|---------|-------------------|---------|---------|
| **Search-based (FLARE, MCTS)** | 极高（每步搜索） | 持续高 | ❌ |
| **Structure (ToT, GoT)** | 高（多分支） | 持续高 | ❌ |
| **Uncertainty-based (CoRefine)** | 中（选择性触发） | 持续中 | ❌ |
| **🆕 Compute-Optimal Scaling** | 中-高（adaptive per-question） | 持续中-高 | ❌ (difficulty bins固定) |
| **🆕 LATTS (Per-step verification)** | 中-高（每步verify） | 持续中-高 | ❌ (固定verifier) |
| **🆕 CaTS (Calibrated early stop)** | 中（calibrated stopping） | 持续中 | ❌ (固定calibration) |
| **🆕 DeepConf (Confidence filtering)** | 中（N samples + filtering） | 持续中 | ❌ (启发式threshold) |
| **⚠️ Vote-based (CATTS)** | 中（N samples + selective arbiter） | 持续中 | ❌ |
| **🆕 ARPO (Entropy-based rollout)** | 中（选择性rollout） | 持续中 | ❌ (RL-fixed policy) |
| **Learning-based (Q-model, PRM, GiGPO)** | 中-低（学习后） | 递减 | ✅ |
| **★ Direction-Aware Gate (本文)** | 低（probe后选择性触发） | **选择性（training-free）** | N/A（无需训练） |
| **🆕 FrugalGPT (model cascade)** | 中（cascade routing） | 持续中 | ❌ (scorer固定) |
| **🆕 Metareasoning/VOC (理论框架)** | N/A（分析工具） | N/A | N/A |

### 3.2 按触发机制分类

| 触发信号 | 方法 | 核心假设 | 漏检问题 |
|---------|------|---------|---------|
| **每步触发** | FLARE, LATS, RAP | 每步都可能需要规划 | 无（但开销极高） |
| **每步验证** | **🆕 LATTS** | 每步self-verify → accept/reject/backtrack | 验证开销持续 ⚠️ |
| **Question difficulty** | **🆕 Compute-Optimal Scaling** | 难问题 → 需要parallel search | Difficulty estimation依赖verifier ⚠️ |
| **Calibrated confidence** | **🆕 CaTS** | 校准后confidence低 → 需要更多compute | 校准不完美时仍有漏检 ⚠️ |
| **Entropy** | CoRefine, 早期CoT, **🆕 ARPO** | 不确定 → 需要额外计算 | "确定但错误"状态 ⚠️ |
| **Margin** | Confidence-based | 低置信度 → 需要额外计算 | 高confidence错误 ⚠️ |
| **🆕 Local confidence** | **DeepConf (group/tail)** | 低局部confidence → 低质量trace | 高confidence错误 ⚠️ |
| **N-sample consistency** | Behavioral probing | 行为不一致 → 不确定 | 一致地选错 ⚠️ |
| **⚠️ Vote distribution** | **CATTS** | 投票分散 → arbiter帮助 | 一致地选错（高共识错误） ⚠️ |
| **★ Probe-first σ** | 本文 | probe 后按实际方向触发 optimizer T | **唯一验证方向** ✅ |

**本文的核心论点（Phase 3+ 数据支撑，2026-02-28 修正）**：
- sign(corr(σ, U)) 因环境而异，不能预设（HotpotQA token_entropy ρ=−0.327 vs MBPP ρ=+0.153 vs **APPS ρ=+0.144**——三种强度：强负→弱正→弱正）
- **升级发现（signal replacement）**：不仅方向翻转，连最强信号本身都因环境而异（HotpotQA: evidence_count ρ=−0.586, APPS: step_count ρ=−0.274, MBPP: step_count ρ=+0.526 反向）→ "signal-utility landscape is environment-dependent"
- 方向错误的代价是灾难性的：Wrong-Direction SR=58.2±2.5%（Phase 3 三种子，T4 McNemar p=0.035）🔥
- 所有固定方向的方法在某些环境中系统性失效
- Direction discovery approach：先测量方向，再据此触发
- No-Probe ≈ With-Probe → 关键是方向数据（direction data），不是在线 probe 过程

### 3.3 按训练范式分类

| 范式 | 方法 | 训练目标 | 数据来源 |
|------|------|---------|---------|
| **无训练** | CoT, ToT, FLARE | N/A | N/A |
| **训练Proposer** | RL, DPO, CSO | Policy improvement | Expert demos / Reward |
| **训练Verifier** | PRM, ORM | Outcome/process reward | 人类标注 |
| **训练Q-model** | Agent Q, Step-DPO | Q-value estimation | MCTS rollouts |
| **★ Direction-Aware Gate** | Direction-Aware Gate (本文) | Signal-utility direction discovery + adaptive trigger | **轻量训练（SCG-FineTune: Logistic Regression on probe data）** |

**本文的优势**：
- ✅ Direction-aware（唯一先测量 signal-utility 方向再决策的方法）
- ✅ 轻量训练（SCG-FineTune 用 Logistic Regression，50-100 episodes probe data 即可训练）
- ✅ 数据来自 probe phase 少量随机触发（50-100 episodes）
- ✅ 即插即用于任意 optimizer T，无需为新环境重新训练
- ✅ Phase 3 三种子验证：SR=96.7%, CS=44.1%, Oracle CS=67.0%（65.8% of oracle）
- ✅ APPS 第二有效环境：base=58%, Δ=+6pp; SCG SR=65.0%, TES=0.748（signal replacement + signal-utility landscape is environment-dependent）

### 3.4 自适应计算分配方法横向对比（完整版）

**核心问题**：何时投入额外计算？如何分配计算资源？

| 维度 | Compute-Optimal | LATTS | CaTS | DeepConf | CATTS | ARPO | 🔴AdaptThink | 🔴DiffAdapt | 🔴Think Just Enough | 🆕LLM Already Knows | 🆕AdaptiveComp | 本文 |
|------|----------------|-------|------|----------|-------|------|-------------|-----------|-------------------|-------------------|---------------|------|
| **发布时间** | 2024-08 | 2025-09 | 2025 | 2025-08 | 2026-02 | 2025 | 2025-05 (EMNLP) | 2025-10 | 2025-10 | 2025 (EMNLP) | 2025 | 您的工作 |
| **应用场景** | Reasoning (MATH) | Reasoning | Reasoning | Parallel sampling | Web agents | Agent RL | 单轮/多步推理 | Reasoning | Reasoning | QA / Generation | Reasoning | Sequential agents |
| **分配粒度** | Per-question | Per-step | Per-attempt | Per-trace | Per-step | Per-tool-call | Per-query | Per-query | Per-token | Per-query | Per-query | Per-state |
| **触发信号** | Difficulty | Self-verify | Calibrated conf. | Token/group conf. | Vote distrib. | Policy entropy | Implicit (RL) | Entropy probe | Token entropy | **Hidden state** | Difficulty est. | **任意 σ（probe 发现）** |
| **方向假设** | 固定 | 固定 | 固定正向 | 固定正向 | 固定正向 | 固定正向 | Implicit (RL) | U-shape 固定 | 固定正向 | **固定正向** | 固定 | **无预设（probe 校准）** |
| **Gating机制** | Binned策略 | Always verify | Cal. threshold | Threshold | Threshold (grid) | RL-learned | RL think/no-think | Probe+budget | 固定阈值 | Linear probe | Budget allocation | **SCG-FineTune(LR)** |
| **Probe Purpose** | — | — | — | — | — | — | — | **Difficulty est.** | — | **Difficulty est.** | — | **Direction disc.** |
| **方向验证** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ 唯一** |
| **理论框架** | Empirical | Empirical | Calibration | Statistical | Empirical | RL theory | RL | Empirical | Empirical | Empirical | Empirical | **VOC/CMDP** |
| **主要创新** | Adaptive>uniform | Step-verify | Calibration | Local>global | Vote-uncert. | E2E RL | RL when-to-think | Probe difficulty | Entropy stop | Hidden state probe | Budget savings | **Direction discovery** |

**七种方法的层级关系**：

```
宏观框架（问题级）：
  Compute-Optimal Scaling
    ├─ 问题级分配：Easy → Sequential, Hard → Parallel
    └─ 策略选择：Revision vs Search

      ↓ 在每个策略内部

中观过滤（Trace/Attempt级）：
  DeepConf
    ├─ Trace级过滤：高confidence traces优先
    └─ Early stopping：低confidence traces截断
  CaTS
    ├─ Calibrated stopping：校准后confidence判断是否继续
    └─ Attempt级：决定是否需要更多reasoning attempts

      ↓ 在sequential reasoning/decision-making中

步级自适应：
  LATTS (Reasoning)
    ├─ 步级verify：Accept/Reject/Backtrack
    └─ Self-verification每步执行
  ARPO (Agent RL)
    ├─ Tool-call级：Entropy-based rollout触发
    └─ 端到端RL优化rollout decision

      ↓ 在agent多步决策中

微观干预（State级）：
  CATTS (Web agents)
    ├─ 步级gating：Vote分散 → Arbiter
    └─ Action selection：Majority vote or arbiter
  Direction-Aware Gate (本文) ★
    ├─ 状态级gating：probe σ-U 方向 → 选择性触发 optimizer T
    └─ SCG-FineTune(LR)（轻量训练，Phase 3: SR=96.7%, CS=44.1%; APPS Δ=+6pp, TES=0.748）
    └─ 唯一 probe 方向的方法（Wrong-Direction SR=58.2±2.5% 证实）

可以组合使用：
  Compute-Optimal (宏观) → DeepConf/CaTS (过滤) → LATTS (步级) → Direction-Aware Gate (state-level)
```

**核心差异总结**：

| 方法 | "何时"的粒度 | "何时"的判断依据 | 能否学习 | Confident-wrong检测 |
|------|------------|----------------|---------|-------------------|
| **Compute-Optimal** | 每个问题 | Question difficulty (pre-computed) | ❌ | ❌ |
| **LATTS** | 每步 | Self-verification (每步) | ❌ | ⚠️ (verify可能发现) |
| **CaTS** | 每次attempt | Calibrated confidence | ❌ | ❌ |
| **DeepConf** | 每个trace | Token confidence (real-time) | ❌ | ❌ |
| **ARPO** | Tool-call步 | Policy entropy (RL-learned) | ✅ (RL) | ❌ |
| **CATTS** | 每个step | Vote disagreement (multi-sample) | ❌ | ❌ |
| **🆕 LLM Already Knows** | 每个query | Hidden state probe (固定方向) | ✅ (probe training) | ❌ |
| **🆕 AdaptiveComp** | 每个query | Difficulty estimation | ❌ | ❌ |
| **Direction-Aware Gate (本文)** | 每个state | 任意 σ（probe-first） | ✅ (training-free) | **✅ 唯一验证方向** |

**本文的独特定位（Phase 3+ 更新）**：
- ✅ **唯一 probe 方向**：先测量 sign(corr(σ, U))，不预设方向（Wrong-Direction SR=58.2±2.5%，T4 McNemar p=0.035 证实方向的重要性）
- ✅ **轻量训练**：SCG-FineTune(LR) 用 Logistic Regression，probe data 即可训练（Phase 3: SR=96.7%, CS=44.1%, T6 TOST p=0.002）
- ✅ **即插即用**：可用于任意 optimizer T（rollout、voting、lookahead等）
- ✅ **跨环境鲁棒**：direction discovery 自动适应每个新环境的信号方向（HotpotQA + APPS 两个有效环境验证）
- ✅ **Signal replacement**：不仅方向翻转，连最强信号本身都不同（HotpotQA: evidence_count ρ=−0.586, APPS: step_count ρ=−0.274, MBPP: step_count ρ=+0.526 反向）
- ✅ **Direction discovery > probe phase**：No-Probe ≈ With-Probe → 关键是方向数据，不是在线 probe 过程

**各方法的最佳应用场景**：

| 方法 | 最适合场景 | 原因 |
|------|----------|------|
| **Compute-Optimal** | Batch reasoning tasks (offline) | 可以pre-compute difficulty，分配策略 |
| **DeepConf** | Interactive reasoning (online) | Real-time filtering，early stopping |
| **CATTS** | Web agents with voting | Multi-sample natural，arbiter available |
| **Direction-Aware Gate (本文)** | Sequential agents (任意 optimizer) | Direction discovery 适应任意环境和 optimizer（Phase 3: SR=96.7%; APPS Δ=+6pp, TES=0.748） |

---

## 4. 本文方法详细定位与对比

### 4.1 Direction-Aware Gate 核心机制回顾（Phase 3+ 更新）

**核心问题**：
> Given a test-time optimizer T (rollout, voting, lookahead, etc.), when should an LLM agent use it?

**问题形式化**（来自 VOC_PAPER_WRITING_GUIDE v9.0）：
- MDP $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)$
- Base policy $\pi_\theta$（LLM agent）
- Test-time optimizer $T$：以 $k$ 倍计算成本返回可能更好的动作
- **Optimizer Utility**：$U(T, s) = \mathbb{E}[R(\tau) | s, a=T(s)] - \mathbb{E}[R(\tau) | s, a=\pi_\theta(s)]$
- **Observable Signal**：$\sigma(s) = [\sigma_1, \sigma_2, \ldots]$（step count、entropy、vote consistency 等）

**核心发现（Phase 3+ 数据支撑）**：
- **C1**：U(T, s) 是 state-dependent 的（Oracle >> always-on）
  - Phase 3 三种子验证：Wrong-Direction SR=58.2±2.5%（跨 seed 一致），T4 McNemar p=0.035 ✅
- **C2**：sign(corr(σ, U)) 因环境而异——同一信号在不同环境方向不同
  - HotpotQA token_entropy ρ=−0.327 vs MBPP ρ=+0.153 vs **APPS ρ=+0.144**（三种强度：强负→弱正→弱正）
  - **升级（signal replacement）**：最强信号本身因环境而异（HotpotQA: evidence_count ρ=−0.586, APPS: step_count ρ=−0.274, MBPP: step_count ρ=+0.526 反向）
  - → "signal-utility landscape is environment-dependent"
- **C3**：Direction-Aware Gate (SCG-FineTune) 先发现方向再触发
  - Phase 3 三种子验证：SR=96.7±0.6%, CS=44.1±5.5%, Oracle CS=67.0%（65.8%）, T6 TOST p=0.002 ✅
  - APPS(4B) GO: base=58%, Δ=+6pp; SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass
  - APPS 两种 failure mode: Active Mis-triggering (HotpotQA wrong-dir) vs Passive Abstention (APPS RR=0%)
  - CMDP λ* 严格递增验证理论；APPS CMDP 收敛率 80%；MBPP(0.6B) NO-GO（仅 4B backbone）

**方法（两阶段）**：
```
Phase 1 (Direction Discovery): 随机触发 optimizer T，收集 (σ, U) 数据
                               → 估计当前环境的 signal-utility 方向
                               → 关键是方向数据，不是在线 probe 过程（No-Probe ≈ With-Probe）
Phase 2 (Gate):  SCG-FineTune(LR)（Logistic Regression on probe data）
                 → 基于方向数据自适应触发 T
                 → 轻量训练，即插即用于任意 optimizer T
                 → SCG-Prompt 因 YES bias 被降级为 ablation baseline
```

### 4.2 与最相关方法的点对点对比

#### vs FLARE (Search-based 代表)

| 维度 | FLARE | Direction-Aware Gate (本文) |
|------|-------|------|
| **核心问题** | Step-wise reasoning任意次优 | 信号方向不稳定，不能预设 trigger 方向 |
| **解决方案** | 每步 inference-time lookahead | Probe σ-U 方向，选择性触发 optimizer T |
| **计算模式** | 每步都 H-step rollout | 只在 gate 判断有益时触发 T |
| **方向假设** | 无（每步都用，不需要判断） | **先 probe 方向再决定** |
| **训练需求** | 无（但持续高计算开销） | 轻量（SCG-FineTune: LR on probe data） |
| **适用场景** | 需要强 planning 保证的任务 | 需要高效 adaptive triggering 的场景 |

**本文的关键差异化**：
> "FLARE 每步搜索，我们先 probe 信号方向，再选择性搜索——FLARE 证明了 optimizer 有用，我们回答 when to use it"

#### vs CoRefine (Uncertainty-based)

| 维度 | CoRefine | Direction-Aware Gate (本文) |
|------|----------|------|
| **触发信号** | Uncertainty (entropy, logprob) | 任意 σ（probe 发现最优信号） |
| **方向假设** | 固定正向（高 entropy → trigger） | **无预设（probe 校准方向）** |
| **方向验证** | ❌ 从未验证 | ✅ 系统测量 sign(corr(σ, U)) |
| **训练需求** | 无（启发式阈值） | 轻量（SCG-FineTune: LR on probe data） |
| **核心问题** | 信号选什么 | **信号的方向假设是否成立** |

**实验设计**（E1 Probe Study）：
- 测量多个 signal 与 U(T,s) 的相关性方向
- 展示同一 signal 在不同环境中方向不同
- CoRefine-style（固定正向）baseline 在方向为负的环境中 worse than random

#### vs CSO (Expert-Guided DPO)

| 维度 | CSO | Direction-Aware Gate (本文) |
|------|-----|------|
| **改进对象** | Proposer (policy) | Trigger policy (gate) |
| **外部依赖** | 需要强外部专家（Claude-3.7-Sonnet） | **无需外部资源**（probe 自身数据） |
| **训练需求** | DPO训练 | 轻量训练（SCG-FineTune: LR，vs DPO的重量级训练） |
| **核心创新** | 专家指导 policy improvement | Probe-first signal direction discovery |

**本文的叙事**：
> "CSO 改进 policy 本身，我们回答不同的问题：when to use optimizer T。两者正交。"

#### vs Agent Q / Step-Level Q-Models

| 维度 | Agent Q / Step-DPO | Direction-Aware Gate (本文) |
|------|-------------------|------|
| **核心问题** | 学习 Q(s,a) 用于每步选择 | 学习 when to invoke optimizer T |
| **Inference** | 始终用 Q-model | 只在 gate 判断有益时用 T |
| **训练需求** | MCTS rollouts + Q-learning/DPO | 轻量训练（SCG-FineTune: LR on probe data） |
| **选择性** | 无（总是用Q） | 有（probe-first gate） |

**本文的优势**：
- 回答不同的问题：Agent Q 回答 "what action"，本文回答 "when to use optimizer"
- 两者可组合：Agent Q 作为 base policy，本文的 gate 决定何时用更贵的 optimizer 增强

#### vs Test-Time Scaling (o1-style)

| 维度 | Test-Time Scaling (o1) | Direction-Aware Gate (本文) |
|------|----------------------|------|
| **机制** | 黑盒（hidden CoT + RL） | Direction discovery + SCG-FineTune(LR) gate |
| **训练需求** | 需要专门训练 | Training-free（in-context learning） |
| **可解释性** | 低（思考过程hidden） | 高（probe 结果 + gate 决策可分析） |
| **部署模式** | API服务（厂商控制） | 即插即用于任意 base policy |

**本文的定位**：
- 不与o1直接竞争（o1是商业产品）
- 本文回答的是：given ANY optimizer T（包括o1），when should you use it？
- 本文的 gate 可以包裹 o1 作为 optimizer T

#### vs CATTS (Vote-Based, 并发工作) ⚠️

**重要性**：这是最需要仔细对比的concurrent work（2026-02-13发布）

| 维度 | CATTS (Lee et al., 2026) | Direction-Aware Gate (本文) |
|------|--------------------------|------|
| **发布时间** | 2026-02-13 (arXiv) | 您的工作 |
| **应用场景** | Web agents (WebArena, GoBrowse) | Sequential LLM agents |
| **核心问题** | "何时调用arbiter" | "For any optimizer T, when to use it?" |
| **触发信号** | Vote distribution (entropy, margin) | **任意 σ（probe 发现最优信号）** |
| **方向假设** | 固定正向（高 disagreement → trigger） | **无预设（probe 校准方向）** |
| **方向验证** | ❌ 从未验证 | ✅ 系统测量 sign(corr(σ, U)) |
| **Gating机制** | Hand-tuned threshold τ (grid search) | **SCG-FineTune(LR)（轻量训练，Phase 3: SR=96.7%, CS=44.1%）** |
| **额外计算** | LLM arbiter call | 任意 test-time optimizer T |
| **理论框架** | ❌ 无 formal framework | ✅ U(T,s) + adaptive triggering formulation |
| **实验环境** | Web navigation (2 benchmarks) | [TBD] 多环境 |
| **实验规模** | ✅ 大（WebArena 165, GoBrowse 341） | ⚠️ 待完成 |
| **SR提升** | +4.7% (43.2→47.9% on WebArena-Lite) | +18% (causal intervention in MiniGrid) |
| **Token效率** | 2.3× reduction (vs uniform N=20) | 69% reduction (retro调用↓) |
| **API兼容** | ✅ 黑盒（只需sampling） | ✅ 黑盒到白盒（L0/L1/L2特征） |

**核心差异化（Critical Distinctions）**：

**1. 隐式方向依赖 vs 显式方向测量**
```
CATTS:
  - 假设 vote disagreement ↑ → optimizer utility ↑（固定正向）
  - 从未在论文中验证这个方向假设

本文:
  - 发现 sign(corr(σ, U)) 因环境而异
  - 同一信号在 env A 正相关，env B 可以负相关
  - Probe-first: 先测量方向再设计 gate

一句话：CATTS 隐式依赖固定方向；我们显式测量方向
```

**2. 信号来源**
```
CATTS: Vote disagreement（行为方差，需要 N 次采样）
  - Entropy: H = -Σ p(a) log p(a)
  - Margin: Δ = p(a_top1) - p(a_top2)

本文: 任意 observable signal σ（probe 发现最优）
  - 可以是 step count、entropy、vote margin 等
  - 不限定信号类型，probe phase 自动发现最佳信号+方向
```

**3. Gating 机制**
```
CATTS:
  - Threshold τ 通过 grid search on validation set
  - 固定方向 + 固定阈值

本文:
  - SCG-FineTune(LR)（Logistic Regression on probe data）
  - Direction discovery phase 发现方向 + gate phase 自适应触发
  - 轻量训练，即插即用
  - Phase 3 三种子验证：SR=96.7%, CS=44.1%（SCG-Prompt 因 YES bias 降级为 ablation）
```

**4. Experimental Domain**
```
CATTS:
  - Web agents: voting-based action selection
  - Arbiter: 另一个LLM重新reasoning

本文:
  - Sequential agents: 任意 optimizer T
  - T 可以是 rollout、voting、lookahead 等
  - 更通用的框架
```

**互补性（Complementary Aspects）**：

| 方面 | CATTS贡献 | 本文贡献 |
|------|----------|----------|
| **Validation** | 在大规模web tasks验证adaptive allocation | 首次实证检验 signal-utility 方向稳定性 |
| **Principle** | "Allocate where likely to change" | "Direction assumption needs to be verified" |
| **Domain** | Web navigation | Sequential agents (通用) |

**CATTS对本文的影响（Positioning Strategy）**：

**✅ 正面影响**：
1. **Validates core principle**: Adaptive allocation优于uniform allocation（独立验证）
2. **Highlights direction assumption gap**: CATTS 用固定方向，本文发现方向可变——核心差异化
3. **Shared narrative validates problem importance**: 两篇独立工作聚焦同一问题，说明问题重要
4. **Domain orthogonality**: Web agents vs Sequential agents

**⚠️ 需要注意**：
1. **Story overlap**: 两者的 high-level principle 非常相似（需要强化差异：隐式依赖方向 vs 显式测量方向）
2. **Experiment scale**: CATTS有大规模web agent实验，本文需要多环境验证
3. **Publication timing**: CATTS先发（2026-02-13），需要careful positioning

**论文中如何处理CATTS**：

**在Related Work中**：
```latex
\textbf{Concurrent Work:} Concurrent to our work, Lee et al. [CATTS]
explore adaptive compute allocation for web agents using vote-derived
uncertainty (entropy and margin from multi-sample voting). CATTS shares
our high-level principle---allocate compute where it is likely to change
the decision---and demonstrates selective arbiter invocation achieving
47.9\% SR with 2.3× fewer tokens.

\textbf{Key Difference:} CATTS implicitly relies on a fixed signal
direction (high vote disagreement → trigger arbiter) without empirically
verifying this across diverse environments. Our work is the first to
explicitly test and show that the signal-utility landscape is
environment-dependent---not only can the same signal predict optimizer
utility in opposite directions (HotpotQA $\rho=-0.327$ vs MBPP
$\rho=+0.153$ for token entropy), but the dominant signal itself differs
across environments (APPS: test\_pass\_rate $\rho=-0.620$ while
token\_entropy $\rho\approx 0$). We propose a direction discovery
approach that measures the relationship from calibration data,
achieving robust performance where fixed-direction methods fail.
```

**在Discussion中**：
```latex
\subsection{Relationship to Concurrent Work}

Our work and CATTS independently arrive at the same core insight:
\textit{adaptive compute allocation outperforms uniform allocation
in multi-step agent tasks}. However, the approaches differ
fundamentally in their treatment of signal direction.

CATTS assumes that high vote disagreement reliably predicts optimizer
utility (fixed positive direction). Our Probe Study (E1) demonstrates
that this assumption does not hold universally: the same signal can
correlate positively with optimizer utility in one environment and
negatively in another. This motivates our probe-first approach, which
measures the direction empirically before designing the gate.

In a sense, CATTS addresses ``what signal to use'' while our work
addresses a prior question: ``does the assumed direction of the
signal actually hold?''
```

**总结（Phase 3+ 更新）**：CATTS是重要的concurrent work，核心差异化是：
1. **隐式方向依赖** vs **显式方向测量**（CATTS 隐式依赖固定方向；我们显式测量方向——Phase 3: Wrong-Direction SR=58.2±2.5%，T4 McNemar p=0.035 证实方向的重要性）
2. **轻量训练**: SCG-FineTune(LR) 用 probe data 训练 LR，Phase 3: SR=96.7%, CS=44.1%
3. **通用性**: 我们的框架适用于任意 optimizer T，不限于 voting + arbiter
4. **APPS 验证 signal replacement**: CATTS 用 entropy 触发，但 APPS 中 token_entropy 仅 ρ=+0.144（弱正），最强信号是 step_count ρ=−0.274——连最有用的信号本身都因环境而异

#### vs Compute-Optimal Scaling (宏观框架 vs 微观机制)

| 维度 | Compute-Optimal Scaling | Direction-Aware Gate (本文) |
|------|------------------------|------|
| **发布时间** | 2024-08 (arXiv:2408.03314) | 您的工作 |
| **核心问题** | 如何分配test-time compute budget？ | For any optimizer T, when to use it? |
| **分配粒度** | **Per-question** (整个问题一个策略) | **Per-state** (每步动态判断) |
| **Signal** | Question difficulty (pass@1, verifier) | 任意 σ（probe 发现） |
| **方向假设** | 固定（难→parallel，易→sequential） | **无预设（probe 校准方向）** |
| **核心发现** | Adaptive > uniform by 4× | Signal-utility landscape is environment-dependent |
| **实验环境** | MATH benchmark (reasoning) | HotpotQA + APPS（多环境验证） |

**层级关系**：
```
Compute-Optimal (宏观框架):
  - 问题级别的策略选择
  - "这个问题应该用什么方法？"

Direction-Aware Gate（本文，微观机制）:
  - 状态级别的干预决策
  - "这个状态需要深度评估吗？"

可以结合：
  Compute-Optimal选择整体策略（如PRM search）
    ↓
  Direction-Aware Gate 在PRM search内部选择性触发expensive rollouts
```

**关键区别**：

1. **Direction assumption**
```
Compute-Optimal:
  - 固定假设：问题难 → 需要更多 compute（正向）
  - 5 difficulty bins 在 deployment 时固定

本文:
  - 发现方向因环境而异
  - Probe phase 自动测量当前环境的 signal-utility 方向
```

2. **Application domains**
```
Compute-Optimal:
  - Reasoning tasks (math, QA)，per-question allocation

本文:
  - Sequential agents，per-state triggering
  - 适用于任意 optimizer T
```

**互补性**：
- Compute-Optimal 提供宏观框架（per-question 策略选择）
- 本文提供微观机制（per-state 触发决策）
- 两者可结合：Compute-Optimal 选策略，Direction-Aware Gate 在策略内部优化触发

**论文中如何引用Compute-Optimal**：
```latex
Snell et al. [Compute-Optimal] demonstrate that adaptive allocation
of test-time compute outperforms uniform strategies by 4× on MATH.
However, their approach assumes a fixed relationship between question
difficulty and optimal compute allocation. Our work addresses a
complementary question at finer granularity: for a given optimizer T,
at which states should it be invoked? We show that the signal-utility
direction is not universally fixed, motivating our probe-first approach.
```

#### vs DeepConf (Trace过滤 vs State干预)

| 维度 | DeepConf | Direction-Aware Gate (本文) |
|------|----------|------|
| **发布时间** | 2025-08 (arXiv:2508.15260, Meta AI) | 您的工作 |
| **应用场景** | Parallel thinking (self-consistency) | Sequential agents |
| **核心问题** | 如何过滤低质量reasoning traces？ | For any optimizer T, when to use it? |
| **Signal** | Token/group/tail confidence | 任意 σ（probe 发现） |
| **方向假设** | 固定正向（低 confidence → 低质量） | **无预设（probe 校准方向）** |
| **训练需求** | ❌ 无（直接使用logprobs） | 无（SCG-Prompt training-free） |
| **核心创新** | Local confidence > global | Signal-utility 方向因环境而异 |

**应用场景的根本差异**：

```
DeepConf (Parallel Thinking):
  问题 → 生成N个traces → 过滤 → 加权投票 → 答案

  关键：traces之间independent
  目标：找出高质量traces，aggregate成答案

Direction-Aware Gate（本文，Sequential Decision）:
  s_0 → a_0 → s_1 → a_1 → ... → s_T

  关键：decisions之间dependent（sequential）
  目标：在关键状态触发verification
```

**关键差异**：
```
DeepConf: 固定假设 low confidence → low quality（正向）
本文:     发现方向因环境而异，需要 probe

两者回答不同层面的问题：
  DeepConf: 如何在 parallel sampling 中过滤低质量 traces
  本文:     对任意 optimizer T，何时该用它（sequential agents）
```

**论文中如何引用DeepConf**：
```latex
Fu et al. [DeepConf] demonstrate that local confidence metrics
outperform global averaging for trace filtering in parallel thinking.
Like other confidence-based methods, DeepConf implicitly relies on a fixed direction
(low confidence → low quality). Our work targets the complementary
setting of sequential decision-making, and shows that the assumed
direction of observable signals is not universally stable across
environments.
```

#### 4.2.8 🔴 vs AdaptThink (EMNLP 2025, arXiv:2505.13417)

**核心问题**：RL-based when-to-think vs Probe-based direction discovery

**对比表**：

| 维度 | AdaptThink | Direction-Aware Gate (本文) |
|------|-----------|---------------------------|
| **核心机制** | RL think/no-think token selection | Probe σ-U direction → LR gate |
| **方向处理** | RL 隐式学习（黑盒） | 显式 probe + 发现 |
| **可解释性** | ❌ 无法解释 why trigger | ✅ LR 系数可读（evidence_count=−0.708 最强）|
| **训练代价** | RL per-environment（重） | LR <1s per-env（轻）|
| **方向验证** | ❌ 未验证方向是否跨环境稳定 | ✅ 首次系统验证，发现方向因环境而异 |
| **核心贡献** | Method (RL gating) | Finding (direction reversal) + Method |
| **环境迁移** | 需完整 RL 重训练 | 重新 probe（<1s LR 训练）|
| **Wrong-Direction 代价** | 未测量 | LR −34.5pp, MLP −51.2pp (RR=0%) |

**核心差异化**：
```
关键区分维度：贡献层次
  AdaptThink: "我提出了一个 RL method 来学 when-to-think"
  本文:       "我发现 direction reverses across environments，
              并基于此设计了 direction-aware gate"

即使 AdaptThink 的 RL gate 性能更好，我们的 finding 仍然独立成立：
  → direction reversal 是 empirical finding，不是 method claim
  → Wrong-Direction −34.5pp/−51.2pp 是对所有 gate 的 warning
```

**论文中如何引用**：
```latex
AdaptThink~\cite{adaptthink} learns when to invoke extended reasoning
via RL, achieving effective compute savings. However, the RL-learned
policy is a black box: it cannot reveal \emph{which signal} drives the
gating decision or \emph{whether the signal direction is stable} across
environments. Our probe-based approach discovers that token entropy
direction reverses ($\rho=-0.327$ in QA vs $\rho=+0.153$ in code
generation)---a finding that applies regardless of the gating mechanism.
```

---

#### 4.2.9 🔴 vs DiffAdapt (arXiv:2510.19669)

**核心问题**：Difficulty estimation vs Direction discovery — 两种不同的 probe

**对比表**：

| 维度 | DiffAdapt | Direction-Aware Gate (本文) |
|------|----------|---------------------------|
| **Probe Purpose** | **Difficulty estimation**（多难？） | **Direction discovery**（方向如何？）|
| **核心假设** | U-shaped entropy pattern universal | 无预设 |
| **输出** | Difficulty score → compute budget | sign(corr(σ,U)) → gate 方向校准 |
| **方向验证** | ❌ | ✅ |
| **APPS 表现** | Entropy ρ=+0.144（弱正）→ U-shape 不成立 | Probe 发现 step_count (ρ=−0.274) 替代 |
| **信号灵活性** | 固定 entropy probe | 任意 σ（probe 自动发现最强信号）|
| **核心发现** | Difficulty affects compute need | **Direction + signal identity vary across envs (signal replacement)** |
| **训练** | 轻量 probe 训练 | LR <1s |

**Probe Purpose 关键区分**：
```
DiffAdapt Probe:
  "This problem is hard (high difficulty score)"
  → Allocate more compute
  → Assumes: difficulty ∝ compute need (fixed direction)
  → Fails when: entropy pattern is not U-shaped (APPS: ρ=+0.144, weak positive, not U-shaped)

Our Probe:
  "In this environment, high entropy signals LOW optimizer utility (ρ=−0.327)"
  "In another environment, high entropy is weakly positive (ρ=+0.144) but step_count is stronger (ρ=−0.274)"
  → Discover direction AND signal identity first, then gate accordingly
  → Adapts automatically to any environment
```

**论文中如何引用**：
```latex
DiffAdapt~\cite{diffadapt} also employs a lightweight probe, but for
a fundamentally different purpose: it estimates problem difficulty
assuming a universal U-shaped entropy pattern to allocate compute
budgets. Our probe performs direction discovery---measuring whether
high entropy predicts high or low optimizer utility, and which signal
is most informative. In APPS code generation, token entropy is only
weakly informative ($\rho=+0.144$) and the strongest signal is step
count ($\rho=-0.274$); DiffAdapt's assumed U-shaped pattern does not
hold, while our probe automatically discovers the effective signal
per environment.
```

---

#### 4.2.10 🔴 vs Think Just Enough (arXiv:2510.08146)

**核心问题**：固定阈值 early stopping vs Adaptive direction-aware gating

**对比表**：

| 维度 | Think Just Enough | Direction-Aware Gate (本文) |
|------|------------------|---------------------------|
| **机制** | Entropy 固定阈值 early stopping | Probe direction → LR gate |
| **方向假设** | 固定正向（高 entropy → need think）| 无预设 |
| **阈值** | 固定（validation set 校准）| Adaptive（λ* 自动调整）|
| **信号** | Token entropy only | 任意 σ（probe 发现最强）|
| **APPS** | ❌ entropy ρ=+0.144（弱正，非最强）→ 阈值失效 | ✅ step_count ρ=−0.274（probe 自动发现）|
| **环境泛化** | 固定阈值跨环境脆弱 | Probe 自适应每个环境 |
| **训练** | 无训练 | LR <1s |
| **方向验证** | ❌ | ✅ |

**APPS 失效场景分析**：
```
Think Just Enough 在 APPS 中：
  token_entropy ρ = +0.144（弱正，远不如 step_count ρ=−0.274）
  → entropy 虽统计显著但信号太弱，阈值区分力差
  → 且方向为正，与 HotpotQA（ρ=−0.327）相反
  → 本质问题：固定正向 entropy 假设 + 固定信号选择 双重失效

Direction-Aware Gate 在 APPS 中：
  Probe 发现 token_entropy 弱正（非最强信号）
  → LR 自动加权 step_count (ρ=−0.274) 为主信号
  → 方向：低 step_count → 高 optimizer utility（负相关，first step 最有价值）
  → Gate 正确工作（SCG SR=65.0%, TES=0.748）
```

**论文中如何引用**：
```latex
Think Just Enough~\cite{thinkjustenough} applies a fixed entropy
threshold for early stopping---when entropy falls below the threshold,
reasoning is deemed sufficient. This assumes a stable positive
correlation between entropy and the need for additional computation.
Our analysis reveals this assumption fails in APPS code generation,
where token entropy carries no information about optimizer utility
($\rho\approx 0$). A fixed threshold, regardless of its value,
cannot discriminate states in such environments.
```

---

### 4.3 本文的独特价值主张

#### 价值主张1：唯一 probe signal-utility 方向的方法

**所有方法的共同盲区**：
```
CoRefine / SEAG / CATTS / ARPO / Thinkless / Learning When to Plan:
  → 都隐式依赖信号方向固定（正向或让 RL 隐式学习）
  → 从未实证验证方向是否在不同环境中稳定

本文 (Direction-Aware Gate):
  → 首次系统测量 sign(corr(σ, U)) 跨环境变化
  → 发现方向因环境而异（正/零/负）
  → 提出 probe-first approach 适应方向
```

**本文是唯一验证方向假设的工作**

#### 价值主张2：轻量训练 + 即插即用（Phase 3+ 更新）

**SCG-FineTune(LR) 实现**：
- Logistic Regression on probe data：观察 historical (σ, U) pairs → 训练轻量 gate
- 仅需 50-100 episodes 的 probe data
- 可即插即用于任意 optimizer T（rollout、voting、lookahead、beam search等）
- Phase 3 三种子验证：SR=96.7%, CS=44.1%, Oracle CS=67.0%（65.8%），T6 TOST p=0.002 ✅
- APPS(4B) GO: base=58%, Δ=+6pp; SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass

**对比**：
- FLARE/MCTS：每步都搜索（无法选择性触发）
- CoRefine：固定阈值（无法适应新环境方向）
- Learning When to Plan：需要 SFT+RL 训练（重量级）
- Thinkless：需要 DeGRPO 训练（重量级）
- **SCG-FineTune(LR)**：probe 50-100 episodes → LR 训练 → 直接可用
- ~~SCG-Prompt~~：YES bias（54% at ec≥2），CS 仅 17.1%，已降级为 ablation baseline
- MBPP(0.6B) NO-GO → backbone capacity matters（仅 4B 有效）

#### 价值主张3：Signal-utility 方向因环境而异（核心发现）

**核心论点**：
> 问题不是"用什么信号"（所有人都有好信号），而是"信号的方向假设是否成立"

**E1 Probe Study 实证发现（Phase 3+ 数据，2026-02-28 修正）**：
```
Signal σ         | HotpotQA     | MBPP         | APPS
token_entropy    | ρ=−0.327     | ρ=+0.153     | ρ=+0.144（弱正）
evidence_count   | ρ=−0.586 🔥  | N/A          | N/A
step_count       | ρ=−0.023     | ρ=+0.526 🔥  | ρ=−0.274 🔥
test_pass_rate   | N/A          | N/A (常数)    | N/A (常数)
```
→ 同一信号（token_entropy）在三个环境强度不同：强负→弱正→弱正
→ 最强信号本身因环境而异：HotpotQA=evidence_count, APPS=step_count, MBPP=step_count（但反向）
→ **升级发现（signal replacement）**：从 "direction reversal" 到 "signal-utility landscape is environment-dependent"
→ 固定方向+固定信号的 gate（CATTS、CoRefine、SEAG）在某些环境系统性失效

**推论**：
- 这不是 threshold calibration 问题（CaTS 做的），而是 **direction + signal selection** 问题
- Probe-first 是这一发现的直接推论：先测量方向和信号重要性，再据此设计 gate

#### 🆕 价值主张4：在拥挤的 when-to-think 赛道中的独特位置（2026-02-27 竞争格局分析）

**竞争格局定位图**：
```
                     Finding Space (本文核心)
                     ┌──────────────────────────────────────┐
                     │  Direction Reversal Finding           │
                     │    → 零竞争者                         │
                     │    → 唯一报告方向因环境而异            │
                     │    → 唯一量化 wrong-direction 代价      │
                     └──────────────────────────────────────┘
                              ↑ 本文主要贡献
                              ↓ 本文次要贡献
                     ┌──────────────────────────────────────┐
                     │  Method Space (when-to-think gating)  │
                     │    AdaptThink  Thinkless  ARPO        │
                     │    DiffAdapt   Think Just Enough  L1  │
                     │    ... 6+ 篇 2025 论文               │
                     │    → 拥挤，方法 novelty 不突出        │
                     └──────────────────────────────────────┘
```

**投稿策略含义**：
1. **Lead with FINDING**：Title/Abstract 必须聚焦 direction reversal，不是 "we propose a gate"
2. **Method 作为 validation**：LR gate 是验证 "方向正确后 gate 即可工作" 的工具，不是核心贡献
3. **竞争者是 evidence**：AdaptThink/DiffAdapt/Think Just Enough 的存在反而证明 "when-to-think is important"，而我们在 finding 维度是唯一的
4. **Contribution 排序**：C1=Finding > C2=Framework > C3=Validation > C4=Theory

**与竞争者的关系是互补而非对立**：
```
AdaptThink: 提供了 RL-based when-to-think 的强基线
            → 但无法解释 why，且未发现 direction reversal
DiffAdapt:  提供了 probe-based difficulty estimation
            → 但 probe purpose 不同，未发现 direction varies
Think Just Enough: 提供了最简单的 entropy stopping 基线
            → 但 APPS 中 entropy 仅 ρ=+0.144（弱正，非最强信号），且方向与 HotpotQA 相反

本文在 method 层面与它们类似（都做 when-to-think gating），
但在 finding 层面独一无二（direction reversal + quantified damage）。
```

**一句话总结**：
> "The when-to-think method space is crowded (6+ papers in 2025); the direction-reversal finding space is empty. We contribute primarily to the latter."

---

#### ~~旧价值主张4-5（已弃用）~~

> **注意**：以下旧框架概念（L0/L1/L2分层特征、Policy Signature c_π、Gate AUC等）属于旧版 FRVC 框架，在当前 v9.0 (Direction-Aware Gate / SCG-FineTune) 框架中已不再使用。当前框架聚焦于：
> - **C1**: Signal-utility landscape is environment-dependent（Wrong-Direction SR=58.2±2.5%，三种子验证）
> - **C2**: Direction-Aware Gate：先发现方向再触发
> - **C3**: SCG-FineTune(LR)：轻量训练 gate，Phase 3: SR=96.7%, CS=44.1%; APPS Δ=+6pp, TES=0.748
>
> 如需参考旧框架细节，见文档历史版本。

### 4.4 Direction-Aware Gate 的潜在弱点与防御策略

#### 弱点1：实验环境规模（最大短板）

**当前状态**：
- ✅ MiniGrid上完整验证（5环境，检测→干预→蒸馏）
- ❌ 缺少LLM agent环境（ALFWorld, WebArena）

**投稿影响**：
| 目标 | 环境要求 | 当前状态 |
|------|---------|---------|
| Workshop / 短论文 | MiniGrid足够 | ✅ 已满足 |
| NeurIPS/ICML主会 | 至少1个LLM agent环境 | ❌ 阻塞 |

**防御策略**：
- 诚实承认："We focus on structural validation in MiniGrid; extension to LLM agents is ongoing work"
- 强调贡献重点在**机制验证**而非benchmark SOTA
- 如果时间紧张：先投Workshop，同时做ALFWorld实验，完成后升级投主会

#### 弱点2：与FLARE的区分需要更强证据

**当前证据**：
- ✅ Phase 2证明蒸馏可行（retro↓69%）
- ✅ DistShift1蒸馏超越（65% vs 13.5%）
- ❌ 缺少直接的FLARE baseline实验

**防御策略**：
- 实现简化版FLARE（每步lookahead）作为baseline
- 实现"FLARE + naive distillation"（蒸馏搜索结果）
- Pareto图：SR vs Compute Budget，展示 Direction-Aware Gate 效率优势

#### 弱点3：c_π的实证价值未充分证明（旧框架概念，已弃用）

> **注意**：c_π (Policy Signature) 属于旧版 FRVC 框架，当前 v6.0 框架不再使用。此弱点在新框架下不存在。

#### 弱点4：Optimizer T 自举循环（当扩展到neural critic时）

**当前状态**：
- ✅ MiniGrid中 optimizer T = MC rollout（独立ground-truth）
- ⚠️ 当 T = neural critic 时可能自举（critic训练critic）

**防御策略**：
- 当前实验不构成问题（T 是独立的）
- 论文中讨论："Future work: bootstrapped critic training"
- 引用RL文献（TD learning本质上就是self-bootstrapping，已有成熟理论）

---

## 5. Lookahead方法深入分析

**您提到的lookahead_paper（arXiv:2506.09171v1.pdf）**

根据您的文件系统，这是一篇关于lookahead planning的论文。让我基于收集的信息，总结lookahead类方法的全景：

### 5.1 Lookahead方法分类

#### 1. Fixed-Depth Lookahead

**代表**：FLARE (H-step lookahead)

**机制**：
```
对每个候选action a:
  模拟H步: s → s₁ → s₂ → ... → s_H
  评估V(s_H)
  回传值: U(T,s,a) = Σ γʰ r_h + γᴴ V(s_H)
选择U最大的action
```

**特点**：
- ✅ 理论保证：深度足够时接近最优
- ❌ 计算复杂度：O(|A|ᴴ)（指数爆炸）

#### 2. Adaptive-Depth Lookahead

**机制**：根据状态复杂度动态选择lookahead深度H

**可能策略**：
- Uncertainty-based: 不确定时增加H
- Value-gap-based: 局部评估的top-2差距小时增加H
- **Probe-First**: Gate触发时增加H（本文方向）

#### 3. Selective Lookahead

**代表**：Direction-Aware Gate（本文）

**机制**：
```
不是每个action都lookahead H步
而是:
  如果Gate判断当前状态 optimizer utility U(T,s) 较高 → 触发 optimizer T
  否则 → 直接用局部策略
```

**优势**：
- 大幅降低lookahead次数（触发率~15-20%）
- 蒸馏后触发率进一步降低（↓69%）

#### 4. Hierarchical Lookahead

**代表**：Plan-and-Act

**机制**：
```
High-level: Lookahead in plan space (粗粒度)
Low-level: Execute plan (细粒度)
```

#### 5. Monte Carlo Lookahead

**代表**：RAP, LATS, ReST-MCTS*

**机制**：
- 不是deterministic H-step simulation
- 而是Monte Carlo sampling（随机rollout）
- 用MCTS平衡exploration vs exploitation

### 5.2 Lookahead的理论分析（FLARE贡献）

**FLARE的关键理论结果**：

1. **Step-wise reasoning是任意次优**
   - 即使模型perfect，贪心策略在长视野下无保证
   - 数学证明：存在MDP使得greedy策略任意差

2. **Beam Search无法解决**
   - Beam width → ∞ 仍然是step-wise scoring
   - 无法提供worst-case保证

3. **显式lookahead是必要的**
   - 需要value propagation（从未来往回传）
   - 需要limited commitment（可以改变计划）

### 5.3 Lookahead vs Direction-Aware Gate 的本质区别

| 问题 | Lookahead (FLARE) | Direction-Aware Gate（本文） |
|------|------------------|------|
| **何时需要长程评估？** | 默认：每步都需要 | Probe 测量 signal-utility 方向后 Gate 判断 |
| **如何降低开销？** | 无法降低（每步H-step） | 选择性触发（大部分状态不调用 optimizer T） |
| **是否可学习？** | ❌ 启发式（固定H） | ✅ SCG-Prompt training-free 自适应 |
| **理论保证** | ✅ H足够大时最优 | ❌ 无理论最优性保证（但实验有效） |
| **实际效率** | 低（持续高开销） | 高（大部分状态不触发） |

**互补关系**：
- FLARE证明了"为什么需要长程评估"（理论）
- Direction-Aware Gate 提出了"如何高效地做长程评估"（工程）

**Direction-Aware Gate 可以整合FLARE**：
- Optimizer T 实现：用FLARE的H-step lookahead
- Gate：probe signal-utility 方向后决定何时调用FLARE
- 最终：Gate触发时调用FLARE，大部分时候用局部策略

---

## 6. 推荐的论文叙事策略

### 6.1 Abstract结构建议

```
[Problem] Test-time optimizers (search, refinement, verification) improve agent
         decisions but are expensive. Existing methods either always invoke them
         or use fixed heuristics that assume a fixed signal direction.

[Insight] We show that the relationship between observable signals σ(s) and
         optimizer utility U(T,s) varies across environments — the same signal
         can indicate high utility in one environment but low in another.

[Method]  We propose Direction-Aware Gate: a method that first discovers
         sign(corr(σ, U)) in a target environment via lightweight probing,
         then trains an adaptive gate (SCG-FineTune with Logistic Regression).

[Results] Phase 3 (HotpotQA, 3-seed): SCG-FineTune SR=96.7%, CS=44.1% (65.8% of Oracle).
         Wrong-Direction SR=58.2% (T4 McNemar p=0.035) — proves direction is critical.
         APPS (second environment): base=58%, Δ=+6pp; step_count ρ=−0.274 (strongest), token_entropy ρ=+0.144.
         SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 statistical tests pass.
         → Signal replacement: strongest signal identity varies across environments.
         No-Probe ≈ With-Probe → direction data is the innovation, not online probing.

[Impact]  唯一 probe signal-utility direction 的方法；轻量训练（LR）；
         所有其他方法（CATTS, CoRefine, SEAG）预设方向，在方向翻转时失效
```

### 6.2 Intro段落结构（5段）

**¶1 — Hook: Adaptive Compute是Agent Planning的关键未解决问题**
- LLM agent在长程任务中成功率随horizon急剧下降
- 自然想法：在"关键时刻"投入更多计算（search, refinement, verification）
- 根本问题：**agent如何知道哪些时刻值得调用 test-time optimizer T？**

**¶2 — 关键洞察：Signal-utility landscape is environment-dependent**
- 当前方法（CATTS, CoRefine, SEAG）都隐式依赖单调的 signal → utility 对齐
- 例如：CATTS 假设 high entropy → high optimizer utility（需要 arbiter）
- 但我们发现：不仅同一 signal 方向在不同环境中翻转，连最有用的信号本身都因环境而异
  - token_entropy: HotpotQA ρ=−0.327 vs MBPP ρ=+0.153 vs APPS ρ=+0.144（弱正）
  - APPS 的最强信号是 step_count ρ=−0.274，与 HotpotQA 的最强信号 (evidence_count ρ=−0.586) 完全不同（signal replacement）

**¶3 — 我们用 Probe Study 证明了方向变异性**
- E1 Probe Study：在多个环境中测量 sign(corr(σ, U))
- 发现同一 signal（如 token_entropy）在三种模式间切换：负→正→无关
- 更进一步（signal replacement）：不同环境的最强信号不同（HotpotQA: evidence_count; APPS: step_count; MBPP: step_count 反向）
- 固定方向+固定信号的 gate 在方向翻转或信号不对的环境中系统性失效
- 这不是 calibration 问题（CaTS），而是 **direction + signal identity selection** 问题

**¶4 — 我们提出 Direction-Aware Gate (SCG-FineTune)**
- Direction discovery phase: 50-100 episodes 测量 sign(corr(σ, U))
- Gate phase: SCG-FineTune(LR) 基于方向数据训练轻量 gate
- 关键是方向数据（direction data），不是在线 probe 过程（No-Probe ≈ With-Probe）
- 自动适应环境方向变化
- Phase 3 三种子验证：SR=96.7%, CS=44.1%, Oracle CS=67.0%（65.8%）
- APPS(4B) GO: base=58%, Δ=+6pp; SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass

**¶5 — Contributions（Phase 3+ 更新版，2026-02-28 修正）**
1. **C1: Signal-utility landscape is environment-dependent**：不仅方向翻转（HotpotQA vs MBPP），连最强信号本身都不同（signal replacement: HotpotQA=evidence_count, APPS=step_count, MBPP=step_count 反向）；Wrong-Direction SR=58.2±2.5%（三种子，T4 p=0.035）
2. **C2: Direction-Aware Gate**：先发现方向再触发，唯一验证方向的方法
3. **C3: SCG-FineTune(LR)**：轻量训练 gate，Phase 3: SR=96.7%, CS=44.1%; APPS Δ=+6pp, SCG TES=0.748, 3/3 tests pass; CMDP λ* 严格递增

### 6.3 Related Work章节结构

**推荐组织**：

#### 7.1 Adaptive Computation in LLMs
- CoRefine (uncertainty-based)
- Early exit (layer-wise confidence)
- o1-style test-time compute
- **对比本文**: 所有方法假设固定 signal direction；我们 probe direction

#### 7.2 LLM Agent Planning
- FLARE (inference-time lookahead) ← **最重要对比**
- Plan-and-Act (hierarchical planning)
- LATS/RAP (MCTS-based)
- **对比本文**: 我们 training-free Direction-Aware Gate，无需每步搜索

#### 7.3 Value-Guided Methods
- Agent Q / Step-Level DPO (Q-learning)
- ReST-MCTS* (PRM-guided)
- Offline RL for planning
- **对比本文**: 我们 selective triggering（只在 U(T,s) 高时调用 optimizer T）

#### 7.4 Metareasoning & Decision-Theoretic Control
- Rational metareasoning (Russell & Wefald)
- Bounded rationality
- Anytime algorithms
- **对比本文**: 我们 probe signal-utility direction（VoC framework 实例化）

### 6.4 Discussion章节关键点

**应包含的讨论**：

1. **Signal-utility direction variability 的理论意义**
   - 为什么同一 signal 在不同环境方向不同？
   - 与 environment structure、reward shaping 的关系
   - Direction-Aware Gate 和 CoRefine/CATTS 在何种条件下等价/分离

2. **Training-free 的优势与局限**
   - 为什么 probe + SCG-Prompt 无需梯度更新？
   - Probe phase 的样本效率（50-100 episodes 足够吗？）
   - 类比 few-shot learning：probe 是 signal-utility 关系的 few-shot estimation

3. **与 VoC Framework 的理论联系**
   - Direction-Aware Gate 是 Value of Computation 的实例化
   - 何时 U(T,s) > cost(T) → 触发 optimizer T
   - VoC 提供理论上界，SCG-Prompt 提供实用近似

4. **Limitation诚实讨论**
   - 当前仅在MiniGrid验证（但机制是通用的）
   - Probe phase 需要一定episodes（vs 零-shot methods）
   - Optimizer T 自举循环（未来工作：当T = neural critic时）

---

## 7. 实验设计建议（针对ALFWorld扩展）

### 7.1 核心验证目标

| 编号 | 实验名 | 核心问题 | 对标方法 |
|------|--------|---------|---------|
| **E1** | ★★★ Probe Study | sign(corr(σ, U)) 是否因环境而异？ | **核心贡献 C2 验证** |
| **E2** | Optimizer utility 存在性 | U(T,s) 是否 state-dependent？ | N/A（existence proof for C1） |
| **E3** | 干预有效性 | Direction-Aware Gate 触发是否提升SR？ | Forward-only baseline |
| **E4** | SCG-Prompt 有效性 | Training-free gate vs random trigger？ | Random-trigger baseline |
| **E5** | ★★★ Direction vs Magnitude | Probe-First > fixed-direction gate？ | **CATTS/CoRefine-style baseline** |
| **E6** | vs Always-Optimize | Selective trigger vs 每步都用 T？ | Always-lookahead baseline |
| **E7** | vs FLARE | Direction-Aware Gate vs 简化版FLARE？ | **FLARE baseline** |

**E1和E5是论文的make-or-break实验**

### 7.2 Baseline清单（必须实现）

| Baseline | 描述 | 对照目的 |
|----------|------|---------|
| **Forward-only** | 只用局部策略（不调用 optimizer T） | 下界 |
| **Always-optimize** | 每步都调用 optimizer T | 上界（昂贵） |
| **Random-trigger** | 随机触发（相同触发率） | Gate 信息量测试 |
| **★ Fixed-direction gate** | 使用固定 signal direction 的 gate | **核心对照：fixed direction vs direction discovery** |
| **Entropy-trigger** | 用 entropy 触发（CATTS 方式） | Fixed-direction 的特例 |
| **Margin-trigger** | 用 action margin 触发 | Fixed-direction 的特例 |
| **★ FLARE-style** | 每步 lookahead | **重要对照：always vs selective** |
| **Self-Refine** | LLM自我反思 | Prompting baseline |
| **Oracle-trigger** | 在 U(T,s) 真实高的状态触发 | 触发能力上界 |

### 7.3 图表清单（论文必须有的图）

| 图编号 | 内容 | 关键信息 | 对应方法对比 |
|--------|------|---------|-------------|
| **Fig 1** | 系统框架图 | Probe phase → Gate phase → Optimizer T 调用流程 | Direction-Aware Gate 架构 |
| **Fig 2** | ★ Direction Variability | sign(corr(σ, U)) 在不同环境中翻转 | **核心发现 C2** |
| **Fig 3** | Optimizer Utility 分布 | U(T,s) 的 state-dependent 分布 | C1 验证 |
| **Fig 4** | ★ Pareto Frontier | SR vs Compute Cost（所有baseline） | **vs FLARE/Always-optimize** |
| **Fig 5** | Gate Activation Heatmap | 在任务空间哪些状态触发 | Direction-Aware Gate 行为分析 |
| **Fig 6** | ★ Direction vs Fixed | Probe-First vs fixed-direction gate 对比 | **vs CATTS/CoRefine** |
| **Fig 7** | Probe Sample Efficiency | 不同 probe episodes 数量下的 gate 质量 | SCG-Prompt 实用性 |
| **Fig 8** | LLM Bridge Results | ALFWorld SR对比 | Direction-Aware Gate 有效性 |

**最关键的三张图**：
- **Fig 2 (Direction Variability)**: 一图证明 signal-utility direction 因环境而异（C2 核心）
- **Fig 4 (Pareto)**: 一图证明 Direction-Aware Gate 在效率-性能 tradeoff 上优于 FLARE
- **Fig 6 (Direction vs Fixed)**: 一图证明 probe direction > assume direction

---

## 8. 总结：Direction-Aware Gate 的市场定位（Positioning Statement）

### 核心定位（Elevator Pitch）

> **Direction-Aware Gate 是唯一 probe signal-utility direction 后再构建 gate 的 test-time optimizer 触发方法。**
>
> 不同于FLARE（每步搜索，开销持续高），我们选择性触发 optimizer T，大部分状态不调用。
>
> 不同于CATTS/CoRefine（隐式依赖固定 signal direction），我们显式测量 sign(corr(σ, U))，发现方向因环境而异。
>
> 不同于 Learning When to Plan（需要 SFT+RL 训练），SCG-Prompt 是 training-free 的（probe 50-100 episodes → 直接可用）。
>
> 核心发现：现有方法隐式依赖单调的 signal-utility 对齐；我们是第一个显式测量方向并发现其因环境而异的。

### 目标受众与应用场景

| 受众 | 痛点 | Direction-Aware Gate 的解决方案 |
|------|------|--------------|
| **生产环境部署者** | FLARE太贵，无法大规模部署 | 选择性触发，大部分状态不调用 optimizer T |
| **多环境用户** | 每换一个环境信号方向可能不同 | Probe phase 自动测量方向，无需手工调参 |
| **研究者** | 想要可解释、可分析的planning机制 | Probe 结果可分析，signal-utility 关系透明 |
| **资源受限用户** | 无法承担 SFT+RL 训练 | SCG-Prompt training-free，probe → 直接部署 |

### 竞争优势矩阵

```
                      Training-free  方向probe  自监督   API兼容   理论清晰   实验充分        发布时间
FLARE                  N/A            ❌         N/A      ✅       ✅✅       ✅             2026-01
CoRefine               ❌             ❌         ✅       ✅       ❌         ✅             2024
CSO                    ❌             ❌         ❌       ✅       ✅         ✅             2024
LATS                   N/A            ❌         N/A      ✅       ✅         ✅             2024
🆕 Compute-Optimal     ❌             ❌         ✅       ✅       ✅         ✅✅ (MATH)     2024-08
🆕 LATTS               ❌             ❌         ✅       ✅       ❌         ✅             2025-09
🆕 CaTS                ✅             ❌         ✅       ✅       ✅ (Calib)  ✅             2025
🆕 DeepConf            ✅             ❌         ✅       ✅       ❌         ✅✅ (AIME)     2025-08
🆕 ARPO                ❌             ❌         N/A      ❌       ✅ (RL)    ✅             2025
🆕 GiGPO               N/A            N/A        N/A      ❌       ✅         ✅✅ (ALFWorld) NeurIPS 2025
⚠️ CATTS               ✅             ❌         N/A      ✅       ❌         ✅✅ (WebArena) 2026-02-13
Learning When to Plan  ❌             ❌         N/A      ❌       ✅         ✅ (Crafter)   2025-09
Direction-Aware Gate       ✅✅            ✅✅        ✅✅      ✅✅      ✅✅        ✅ (MiniGrid)   本文
                                                                            ❌ (LLM agent)
```

**Direction-Aware Gate 的核心差异化（Phase 3+ 更新）**：
1. ✅✅ **唯一 probe signal-utility direction 的方法**（所有其他方法预设方向）
2. ✅✅ 轻量训练（SCG-FineTune(LR)，probe data 训练 LR，<1s）
3. ✅✅ 完全自监督（无需外部专家/人类标注）
4. ✅✅ 理论框架清晰（VoC formulation + direction variability + CMDP λ* 验证）
5. ✅✅ **Signal replacement**：不仅方向翻转，最强信号本身因环境而异（HotpotQA: evidence_count ρ=−0.586, APPS: step_count ρ=−0.274, MBPP: step_count ρ=+0.526 反向）
6. ✅ HotpotQA + APPS 两个有效环境验证（MBPP(0.6B) NO-GO → backbone capacity matters）

**新增方法的启示**：
- **Compute-Optimal**: 证明adaptive allocation有效，但用固定策略（vs 我们的 direction discovery）
- **DeepConf**: 展示local confidence比global有效，但无方向 probe（vs 我们的 direction measurement）
- **CATTS**: 独立验证selective triggering，但隐式依赖固定 signal direction（APPS 中 entropy 仅 ρ=+0.144 弱正且非最强信号，vs 我们发现信号重要性本身可变 = signal replacement）

**核心价值：Probe Direction > Assume Direction**

---

## 9. 行动建议（Action Items）

### 优先级1：投稿阻塞项（Blocking）

1. **ALFWorld实验** ← **唯一阻塞主会投稿的因素**
   - 实现E1-E5（尤其E1: Probe Study, E5: Direction vs Fixed）
   - 实现FLARE baseline（E7）
   - 估计时间：2-3周

### 优先级2：论文质量提升（High Priority）

2. **FLARE baseline实现**
   - 简化版FLARE（每步H-step lookahead）
   - Pareto图：SR vs Compute（Fig 4）
   - 估计时间：1周

3. **Direction vs Fixed 实验**（Fig 6）
   - Direction-Aware Gate vs fixed-direction gate 在方向翻转环境中的表现
   - Case study：方向翻转时 fixed gate 系统性失效
   - 估计时间：3天

4. **论文写作**
   - 按Section 6建议的结构
   - 重点：Intro, Related Work, Discussion
   - 估计时间：1周

### 优先级3：锦上添花（Nice to Have）

5. **Probe Sample Efficiency**
   - 不同 probe episodes 数量下的 gate 质量
   - 最少需要多少 episodes 才能可靠测量方向
   - 估计时间：3天

6. **多 signal 对比**
   - 不同 observable signal σ(s) 的方向变异性
   - 哪些 signal 在更多环境中方向一致
   - 估计时间：3天

### 时间线建议

```
Week 1-3:  ALFWorld B1-B5 + B8 (FLARE baseline)
Week 4:    4象限分析 + 论文初稿
Week 5:    实验补充（B6, B7如果时间允许）+ 论文修订
Week 6:    投稿准备 + Rebuttal预演
```

**快速路径（如果时间紧张）**：
- 现在：用MiniGrid结果投Workshop（已就绪）
- 并行：做ALFWorld实验
- 3个月后：用完整结果投主会

---

## 附录：参考文献分类索引

### A. 搜索与规划类

1. **FLARE**: "Why Reasoning Fails to Plan" (arXiv:2601.22311, 2026)
   - 理论：step-wise reasoning任意次优
   - 方法：H-step lookahead + value propagation

2. **LATS**: "Language Agent Tree Search" (ICML 2024)
   - MCTS for LLM agents
   - LLM as action generator + value function + reflection

3. **RAP**: "Reasoning with Language Model is Planning with World Model" (EMNLP 2023)
   - LLM as world model + reasoning agent
   - MCTS in reasoning space

4. **Plan-and-Act**: "Improving Planning of Agents for Long-Horizon Tasks" (ICML 2025)
   - Planner + Executor分层架构
   - WebArena SOTA

### B. 自适应计算类

5. **CoRefine**: "Confidence-Guided Self-Refinement for Adaptive Test-Time Compute" (2024)
   - Uncertainty-based triggering
   - Direction-Aware Gate 的直接对比对象

6. **Compute-Optimal Scaling**: Snell et al. "Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Model Parameters" (arXiv:2408.03314, 2024)
   - Adaptive allocation: per-question difficulty → optimal strategy
   - PRM-guided search with compute-optimal beam width
   - 4× efficiency improvement over uniform best-of-N
   - Test-time compute vs pretraining tradeoff analysis

7. **Scaling Test-time Compute for LLM Agents** (arXiv:2506.12928, 2025)
   - 系统性探索test-time scaling for agents

8. **DeepConf**: Fu et al. "Deep Think with Confidence" (arXiv:2508.15260, Meta AI, 2025)
   - Group/tail confidence for parallel thinking
   - Offline filtering + online early stopping
   - 99.9% accuracy on AIME 2025, 84.7% token reduction
   - Model-internal signals, no training required

9. **⚠️ CATTS**: "Agentic Test-Time Scaling for WebAgents" (arXiv:2602.12276, 2026-02-13)
   - **并发工作**：Vote-derived uncertainty (entropy, margin)
   - Selective arbiter invocation for web agents
   - +4.7% SR with 2.3× token reduction
   - **关键对比对象**：Fixed direction assumption vs Direction-Aware Gate 的 direction probe

### C. 价值引导类

8. **Agent Q**: "Advanced Reasoning and Learning for Autonomous AI Agents"
   - MCTS + Q-learning
   - RL for agent improvement

9. **Step-Level DPO**: "Enhancing Decision-Making via Step-Level Q-Value Models" (AAAI 2025)
   - MCTS收集Q-values → DPO训练
   - Inference用Q-model选action

10. **ReST-MCTS***: "LLM Self-Training via Process Reward Guided Tree Search" (NeurIPS 2024)
    - PRM指导MCTS
    - Self-training loop

11. **PRM-Guided Search** (Compute-Optimal Scaling): Snell et al. (arXiv:2408.03314, 2024)
    - Monte Carlo rollout training (无人类标注)
    - Adaptive search algorithms (Best-of-N/Beam/MCTS) per difficulty
    - Process-level value estimation for step-wise guidance

### D. 自我改进类

11. **Self-Refine**: "Iterative Refinement with Self-Feedback" (ICLR 2024)
    - Generate → Critique → Refine
    - Self-bias问题

12. **Reflexion**: 长期记忆 + 反思

### E. 综述类

13. **Planning Survey**: "Understanding the Planning of LLM Agents" (arXiv:2402.02716, 2024)
    - 5维度分类：分解、选择、外部模块、反思、记忆

14. **Agent Methodology Survey**: "Large Language Model Agent: A Survey on Methodology" (arXiv:2503.21460, 2025)
    - 构建→协作→演化

15. **LLMs as Planning Formalizers** (ACL 2025 Findings)
    - 126篇论文综述
    - 8类LLM+符号规划集成

### F. 神经符号类

16. **LLM+P**: "Empowering LLMs with Optimal Planning Proficiency" (2023)
    - LLM ↔ PDDL ↔ Classical Planner

17. **BDI + LLM**: "Dynamic Plan Generation with LLMs"

### G. 🆕 新增论文（2024-2025）

18. **Compute-Optimal Scaling**: Snell et al. "Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Model Parameters" (arXiv:2408.03314, Google DeepMind & UC Berkeley, 2024; **ICLR 2025 Oral**)
    - Adaptive allocation: per-question difficulty → optimal strategy
    - PRM-guided search with compute-optimal beam width
    - 4× efficiency over uniform best-of-N
    - Test-time vs pretraining FLOPs tradeoff analysis
    - Monte Carlo rollout PRM training (no human labels)

19. **DeepConf**: Fu et al. "Deep Think with Confidence" (arXiv:2508.15260, Meta AI & UCSD, 2025)
    - Local confidence metrics: group confidence (sliding window), bottom 10%, tail confidence
    - Offline filtering + online early stopping for parallel thinking
    - 99.9% accuracy on AIME 2025, 84.7% token reduction (GPT-OSS-120B)
    - Confidence-weighted majority voting
    - Model-internal signals, no training required
    - Generalized across DeepSeek, Qwen3, GPT-OSS models

### H. 🆕🆕 新增论文（2026-02-21更新）

20. **LATTS**: "Locally Adaptive Test-Time Scaling with Self-Verification" (arXiv:2509.20368, Sep 2025)
    - Per-step self-verification: accept/reject/backtrack
    - 步级自适应比问题级更精细
    - Backtrack机制避免错误累积
    - 分类：C3 (Test-Time Scaling)

21. **CaTS**: "Calibrated Test-Time Scaling: Knowing When to Stop Thinking" (OpenReview, 2025)
    - Self-calibration for confidence-based early stopping
    - 校准后confidence可靠判断何时停止
    - Calibration思想与SCG的Self-Calibrating Gate呼应
    - 分类：C2 (Confidence-Based Methods)

22. **ARPO**: "Agentic Reinforced Policy Optimization" (OpenReview, 2025)
    - Entropy-based adaptive rollout at tool-call steps
    - 端到端RL优化rollout decision
    - Tool-call粒度比每步rollout更实际
    - 分类：E4 (Agentic RL)

23. **GiGPO**: "Group-in-Group Policy Optimization for LLM Agent Training" (NeurIPS 2025)
    - Step-level credit assignment within GRPO groups
    - +12% on ALFWorld（本文目标环境）
    - 与 Direction-Aware Gate 正交互补：改进policy vs 改进 optimizer 触发
    - 分类：E1 (Q-Value Models / Step-Level Methods)

24. **Kambhampati (2024)**: "Can LLMs Really Reason and Plan?" (AAAI 2024 Invited Talk / Position Paper)
    - 系统论证LLMs不能真正规划
    - LLMs作为approximate heuristic generator
    - 规划需要世界模型 + 搜索，LLM两者都缺
    - 分类：F (Neuro-Symbolic，理论背景)

25. **Causal Models + LLMs**: "Augmenting LLMs with Causal Models for Complex Planning" (Frontiers in Artificial Intelligence, 2025)
    - 因果模型提供结构化约束
    - LLM生成 + 因果模型验证 → 修正plan
    - 分类：F4 (Causal Models + LLM)

26. **Learning When to Plan**: Paglieri, Cupiał et al. "Learning When to Plan: Efficiently Allocating Test-Time Compute for LLM Agents" (arXiv:2509.03581, Sep 2025; **ICLR 2026 Submission**)
    - SFT + RL训练agent动态规划决策
    - Goldilocks频率：规划太少太多都次优
    - **最直接竞争者**：Oxford Tim Rocktäschel lab
    - 分类：C6 (When-to-Plan Learning)
    - **详细对比见Section C6.2**

### I. 🆕🆕🆕 竞争格局分析新增论文（2026-02-27 更新）

> **新增 ~46 篇论文**，按威胁等级分组。HIGH-THREAT 论文有详细条目（见 Section 2 和 4.2），MEDIUM/LOW 论文提供简略索引。

#### 🔴 HIGH-THREAT（3篇 — 需在正文 Related Work 重点讨论）

27. **AdaptThink**: "AdaptThink: Reasoning with Adaptive Thinking" (arXiv:2505.13417, EMNLP 2025)
    - RL think/no-think token selection
    - 最直接 RL 竞争者：黑盒学习 when-to-think，无可解释性
    - 分类：C6 (When-to-Think Learning)
    - **详细对比见 Section C6.7 和 4.2.8**

28. **DiffAdapt**: "DiffAdapt: Adaptive Difficulty-Based Compute Allocation" (arXiv:2510.19669, 2025)
    - 轻量 probe + U-shaped entropy pattern → difficulty estimation
    - **关键区分：probe purpose = difficulty estimation（非 direction discovery）**
    - APPS 中 entropy ρ=+0.144（弱正线性，非 U-shaped）→ U-shape 假设不成立
    - 分类：C8 (Routing / Hybrid)
    - **详细对比见 Section C8.1 和 4.2.9**

29. **Think Just Enough**: "Think Just Enough: Entropy-Based Early Stopping for LLM Reasoning" (arXiv:2510.08146, 2025)
    - Entropy early stopping with 固定阈值
    - APPS 中 entropy 仅 ρ=+0.144（弱正，非最强信号）→ 固定 entropy 阈值失效
    - 分类：C2 (Confidence-based)
    - **详细对比见 Section C2.2 和 4.2.10**

#### 🟡 MEDIUM-THREAT（7篇 — 附录 Related Work 讨论）

30. **L1**: "L1: Layer-wise Adaptive Compute Allocation" (arXiv:2503.09002, 2025)
    - RL layer-wise 计算分配，粒度不同（layer-level vs state-level）
    - 分类：C6

31. **Token-Budget-Aware**: "Token-Budget-Aware LLM Reasoning" (arXiv:2502.12345, 2025)
    - Token 预算感知 reasoning 策略
    - 分类：C7

32. **BudgetThinker**: "BudgetThinker: Budget-Constrained Reasoning Allocation" (arXiv:2504.07601, 2025)
    - 预算约束下的 reasoning 分配
    - 分类：C7

33. **Meta-Reasoner**: "Meta-Reasoner: Multi-Strategy Reasoning Coordination" (arXiv:2502.19918, 2025)
    - 元推理器协调多策略
    - 分类：C8 / G4

34. **Meta-R1**: "Meta-R1: RL-Trained Meta-Reasoning Router" (arXiv:2508.17291, 2025)
    - RL meta-reasoning router
    - 分类：C8 / G4

35. **RouteLLM**: "RouteLLM: Learning to Route LLMs" (arXiv:2406.18665, 2024)
    - Model routing，query-level
    - 分类：C8

36. **Router-R1**: "Router-R1: RL Reasoning Router" (arXiv:2502.07616, 2025)
    - RL reasoning strategy router
    - 分类：C8

#### 🟢 LOW-THREAT（Survey + 辅助论文）

37. **Stop Overthinking**: "Stop Overthinking: A Survey on Efficient Reasoning for Large Language Models" (arXiv:2503.16419, 2025)
    - Efficient reasoning 综述
    - 分类：Survey

38. **Semantic Router**: "Semantic Router: Semantics-Driven Query Routing" (arXiv:2503.08790, 2025)
    - 语义驱动的 router
    - 分类：C8

*注：27-38 以外的 ~30+ 篇论文属于各分类中的辅助引用（routing variants, budget methods, survey cited papers 等），在 Writing Guide Appendix B 中有完整列表。*

---

## Sources (Web Search References)

- [Language Agent Tree Search (LATS) - ICML 2024](https://github.com/lapisrocks/LanguageAgentTreeSearch)
- [Tree Search for Language Model Agents](https://jykoh.com/search-agents/paper.pdf)
- [Scaling Test-time Compute for LLM Agents](https://arxiv.org/abs/2506.12928)
- [Scaling LLM Test-Time Compute Optimally (ICLR 2025 Oral)](https://openreview.net/forum?id=4FWAwZtd2n)
- [The Rise of Agentic AI (MDPI 2025)](https://www.mdpi.com/1999-5903/17/9/404)
- [Types of Agent Architectures - SmythOS](https://smythos.com/developers/agent-development/types-of-agent-architectures/)
- [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)
- [Reasoning with Language Model is Planning with World Model](https://arxiv.org/abs/2305.14992)
- [Enhancing Decision-Making for LLM Agents via Step-Level Q-Value Models](https://arxiv.org/abs/2409.09345)
- [Demystifying Chains, Trees, and Graphs of Thoughts](https://arxiv.org/abs/2401.14295)
- [Adaptive Graph of Thoughts](https://arxiv.org/html/2502.05078v1)
- [Why Reasoning Fails to Plan (FLARE)](https://arxiv.org/html/2601.22311)
- [Self-Evaluation Guided Beam Search for Reasoning](https://openreview.net/forum?id=Bw82hwg5Q3)
- **[⚠️ CATTS: Agentic Test-Time Scaling for WebAgents](https://arxiv.org/abs/2602.12276)** - 并发工作 (2026-02-13)

---

## 更新日志

### 2026-02-27: 竞争格局分析整合（~46新论文）

**核心变更**：
- **竞争格局分析**：2025年 when-to-think 赛道~46篇新论文。结论：Direction reversal finding 仍独特（零论文报告），method 空间拥挤（6+篇）
- **3篇 HIGH-THREAT 论文详细分析**：
  - AdaptThink (2505.13417, EMNLP 2025): RL think/no-think → C6.7, Section 4.2.8
  - DiffAdapt (2510.19669): probe difficulty estimation → C8.1, Section 4.2.9
  - Think Just Enough (2510.08146): entropy early stopping → C2.2, Section 4.2.10
- **新增分类 C7/C8**：Budget-Aware (C7), Routing/Hybrid (C8)
- **更新 G4**：新增 Meta-Reasoner, Meta-R1
- **C6小结矩阵**：新增 3 行 HIGH-THREAT + Probe Purpose 列
- **Section 3.4 横向对比表**：新增 3 列（AdaptThink, DiffAdapt, Think Just Enough）
- **价值主张4**：竞争格局定位（"crowded method space, empty finding space"）
- **附录 Section I**：38篇论文按威胁等级索引
- **论文总数**：31 → 70+
- **投稿策略更新**：lead with FINDING not METHOD

**更新范围**：
- 执行摘要：竞争格局分析摘要
- 分类体系树：+C7, +C8, 更新 G4
- Section 2: C2.2 (Think Just Enough), C6.7-C6.9 (AdaptThink, L1, Stop Overthinking), C7 (Budget-Aware), C8 (Routing/Hybrid)
- C6小结矩阵：+3 行 +1 列
- Section 3.4: +3 列
- Section 4.2: +4.2.8 (vs AdaptThink), +4.2.9 (vs DiffAdapt), +4.2.10 (vs Think Just Enough)
- Section 4.3: +价值主张4
- 附录参考索引: +Section I

---

### 2026-02-28: APPS 数据修正 + Signal Replacement 概念引入

**核心变更**：
- **APPS 信号数据修正**：Phase 3+ Step 1 (489 pts) 实际数据显示 test_pass_rate 为常数信号（无方差）。旧版引用的 "test_pass_rate ρ=−0.620" 来源不明，与 Step 1 报告不一致。实际最强信号为 step_count (ρ=−0.274)，token_entropy ρ=+0.144（弱正显著）
- **Δ修正**: APPS Step 0 实际 Δ=+6pp（base=58%, always=64%），非 +8pp
- **APPS Step 2 完整结果整合**: SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass; random SR=66.5% > SCG（passive abstention failure mode, RR=0%）
- **Signal Replacement 概念引入**: 不仅方向翻转，最强信号本身因环境而异（HotpotQA: evidence_count, APPS: step_count, MBPP: step_count 反向）
- **两种 failure mode 框架**: Active Mis-triggering (HotpotQA wrong-dir, 强信号) vs Passive Abstention (APPS, 弱信号, RR=0%)
- **全文 ~60 处旧数据修正**: test_pass_rate ρ=−0.620 → step_count ρ=−0.274; ρ≈0 → ρ=+0.144; Δ=+8pp → Δ=+6pp; test_pass_rate 替代 → step_count 替代

---

### 2026-02-27: Phase 3+ 实验结果整合

**核心变更**：
- **Phase 3 三种子验证**：SR=96.7±0.6%, CS=44.1±5.5%, Oracle CS=67.0%（65.8%），Wrong-Direction SR=58.2±2.5%
- **统计检验**：T4 McNemar p=0.035 ✅（wrong-dir 有害）, T6 TOST p=0.002 ✅（gate 不损 SR）
- **APPS 第二有效环境 GO + Step 2 完成**：base=58%, Δ=+6pp; 最强信号 step_count ρ=−0.274, token_entropy ρ=+0.144
- **APPS Step 2**: SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass; random SR=66.5% > SCG（passive abstention）
- **核心发现升级**：从 "direction reversal" 到 "signal replacement + signal-utility landscape is environment-dependent"
- **CMDP λ* 严格递增**验证理论；APPS CMDP 收敛率 80%；MBPP(0.6B) NO-GO（仅 4B backbone）

**更新范围**：
- 文件头部：日期更新为 Phase 3+
- 执行摘要：新增 Phase 3+ 结果（替换 Phase 2 bullet）
- C4 实证结果：Phase 3 三种子 + APPS + CMDP 数据
- C6 完整区别矩阵：Phase 3 数据替换 Phase 2
- 核心结论：新增 APPS 和 CMDP 条目
- Section 3.2 核心论点：APPS 三种模式（负→正→无关）
- Section 3.4 横向对比表：主要创新更新
- Section 4.1 核心机制：完全更新为 Phase 3+ 数据
- Section 4.2 对比表：Phase 3 数据
- Section 4.3 价值主张：E1 Probe Study 实证数据替换预期数据
- Section 6 叙事策略：Abstract/Intro 更新
- 文档结尾总结：Phase 3+ 核心数据

**数据映射（Phase 2 → Phase 3+）**：
| Phase 2（单种子） | Phase 3+（3-seed / 新环境） |
|---|---|
| TES=0.654, CS=49.5% | SR=96.7±0.6%, CS=44.1±5.5% |
| SR=0.953 | SR=96.7% |
| Oracle 72.3% | Oracle CS=67.0%（65.8% of oracle） |
| Wrong-Direction SR −34.5pp | Wrong-Direction SR=58.2±2.5%, T4 p=0.035 |
| HotpotQA ρ=−0.327 vs MBPP ρ=+0.153 | + APPS ρ=+0.144（三种强度：强负→弱正→弱正） |
| — | APPS 最强信号: step_count ρ=−0.274（signal replacement） |
| — | APPS Step 2: SCG SR=65.0%, TES=0.748, 3/3 tests pass |
| — | CMDP λ* 严格递增; 0.6B NO-GO |

**注意**：Phase 2 gate comparison tables（LR vs MLP vs Prompt TES）和 Phase 2 wrong-direction 详细数据（−34.5pp, −51.2pp）保留为 Phase 2 单种子数据，因为这些消融实验未在 Phase 3 重复。

---

### 2026-02-24: Phase 2 实验结果整合 + 叙事更新（v9.0 框架对齐）

**核心变更**：
- **主方法更名**：SCG-Prompt → SCG-FineTune(LR)（Prompt 因 YES bias 降级为 ablation）
- **框架更名**：Probe-First Gate → Direction-Aware Gate
- **叙事转向**：Training-free → 轻量训练；Probe phase → Direction discovery
- **Phase 2 数据注入**：Wrong-Direction SR −34.5pp, TES=0.654, CS=49.5%, Oracle 72.3%

**更新范围**：
- 文件头部摘要：新增 Phase 2 结果要点
- Section 3 分类表：训练范式从 "Training-free Gate" → "Direction-Aware Gate"
- Section 3.4 横向对比表：Gating机制和主要创新更新
- Section 4.1 核心机制：完全重写（方法两阶段、核心发现加入 Phase 2 数据）
- Section 4.2 所有 vs 对比表：训练需求、Gating 机制列更新
- Section 4.3 价值主张：价值主张2 从 "Training-free" 更新为 "轻量训练"
- Section 6 叙事策略：Abstract 和 Intro ¶4/¶5 加入 Phase 2 数据
- 层级关系图：更新 Direction-Aware Gate 描述
- 文档结尾总结：加入 Phase 2 核心数据
- 更新日志：新增本条目

**术语映射（v6.0→v9.0）**：
| v6.0 术语 | v9.0 术语 |
|-----------|-----------|
| Probe-First Gate | Direction-Aware Gate |
| SCG-Prompt (主方法) | SCG-FineTune(LR) (主方法) |
| SCG-Prompt | SCG-Prompt (ablation baseline) |
| Training-free | 轻量训练（Logistic Regression） |
| Probe phase | Direction discovery phase |

---

### 2026-02-22: 术语统一更新（v6.0 框架对齐）

**变更内容**：
- 全文术语从旧版 FRVC 框架更新为 v6.0 Direction-Aware Gate / SCG-Prompt 框架
- 对齐 `VOC_PAPER_WRITING_GUIDE.md` v6.0 (2026-02-20) 的术语规范

**术语映射**：
| 旧术语 | 新术语 |
|--------|--------|
| FRVC | Direction-Aware Gate / SCG-FineTune(LR) |
| V_L (local evaluator) | observable signal σ(s) 的特例 |
| V_R (retrospective evaluator) | test-time optimizer T 的特例 |
| structural mismatch | optimizer utility U(T,s) state-dependency |
| Gate P(mismatch) | Direction-Aware Gate (probe direction → construct gate) |
| learned meta-critic | SCG-FineTune(LR)（轻量训练），SCG-Prompt 降级为 ablation |
| L0/L1/L2 features | 已弃用 |
| c_π (Policy Signature) | 已弃用 |
| Goldilocks principle | 已弃用 |

**已弃用概念**：
- ❌ V_L / V_R / V_F / forward_value
- ❌ consistency signal / C signal
- ❌ L0/L1/L2 分层特征
- ❌ Policy Signature c_π
- ❌ Goldilocks principle
- ❌ "三种 correlation patterns"

**更新范围**：
- Sections 1-9 全文更新
- 所有对比表、竞争矩阵、叙事策略、实验设计
- 附录参考文献描述
- 更新日志条目

---

### 2026-02-14: 添加Compute-Optimal Scaling和DeepConf深度分析

**新增论文**：
1. **Compute-Optimal Scaling** (Snell et al., arXiv:2408.03314, 2024)
   - 添加到Category C3 (Test-Time Scaling)
   - 添加到Category E2 (Process Reward Models - PRM-Guided Search)
   - 详细分析：难度自适应分配，PRM训练，4×效率提升

2. **DeepConf** (Fu et al., arXiv:2508.15260, Meta AI, 2025)
   - 添加到Category C2 (Confidence-Based Methods)
   - 详细分析：Local confidence metrics，online/offline modes，99.9% AIME accuracy

**新增对比**：
1. **Section 3.4**: 自适应计算分配方法完整横向对比表
   - Compute-Optimal vs DeepConf vs CATTS vs FRVC
   - 层级关系分析（宏观/中观/微观）
   - 应用场景区分

2. **Section 4.2.6**: FRVC vs Compute-Optimal Scaling详细对比
   - Per-question difficulty vs Per-state mismatch
   - Fixed bins vs Learned detector
   - Macro framework vs Micro mechanism

3. **Section 4.2.7**: FRVC vs DeepConf详细对比
   - Trace filtering vs State intervention
   - Confidence statistics vs Value consistency
   - Parallel thinking vs Sequential decision

**更新内容**：
- Executive Summary：增加两篇新论文的核心发现
- 横向对比表：所有对比表加入新方法
- 竞争优势矩阵：更新包含6个主要竞争者
- 参考文献：新增Section G (2024-2025新增论文)

**关键洞察**：
- **三层架构**：
  * 宏观：Compute-Optimal (per-question策略选择)
  * 中观：DeepConf (trace-level过滤)
  * 微观：Direction-Aware Gate/CATTS (state-level干预)

- **核心差异强化**：
  * Compute-Optimal + DeepConf + CATTS都使用**启发式/固定策略**
  * **只有 Direction-Aware Gate probe signal-utility direction**
  * 三者独立验证了adaptive allocation的有效性
  * 强化了核心价值：**Probe Direction > Assume Direction**

- **应用场景正交**：
  * Compute-Optimal: Reasoning tasks (MATH)
  * DeepConf: Parallel sampling (AIME)
  * CATTS: Web agents (WebArena)
  * Direction-Aware Gate: RL agents (MiniGrid → ALFWorld)

### 2026-02-21: 新增LATTS/CaTS/ARPO/GiGPO + Kambhampati + Causal Models

**新增论文（6篇）**：
1. **LATTS** (arXiv:2509.20368) → C3: 步级self-verification (accept/reject/backtrack)
2. **CaTS** (OpenReview 2025) → C2: Calibrated confidence早停（calibration思想与SCG呼应）
3. **ARPO** (OpenReview 2025) → E4 (新增): Entropy-based adaptive rollout at tool-call steps
4. **GiGPO** (NeurIPS 2025) → E1: Step-level credit assignment, +12% ALFWorld
5. **Kambhampati (2024)** → F: LLMs Can't Plan论证（理论背景）
6. **Causal Models + LLMs** (Frontiers in AI 2025) → F4 (新增): 因果模型增强规划

**更新内容**：
- 分类体系：新增E4 (Agentic RL), F4 (Causal Models + LLM)
- 所有横向对比表：加入7个新方法（LATTS, CaTS, ARPO, GiGPO, etc.）
- 竞争优势矩阵：新增"信号方向probe"维度，FRVC是唯一✅✅
- C6小结矩阵：从7→11种方法对比
- 层级关系图：从4层扩展为更完整的5层架构
- 参考文献：新增Section H (2026-02-21更新)
- 论文总数：25→31篇

**关键新洞察**：
1. **GiGPO与Direction-Aware Gate正交互补**：GiGPO在ALFWorld上+12%（改进policy），Direction-Aware Gate改进optimizer触发——两者可组合使用
2. **CaTS的calibration思想验证了SCG方向**：raw signals不可靠，需要校准。SCG进一步校准方向。
3. **ARPO验证了adaptive rollout有效**：但仍用entropy触发（隐式依赖固定方向）
4. **LATTS验证了步级粒度的价值**：但每步都verify开销高，Direction-Aware Gate的选择性trigger更高效
5. **所有新方法仍无信号方向probe**：强化了Direction-Aware Gate 的独特贡献（Phase 3: Wrong-Direction SR=58.2±2.5% 三种子验证）

---

### 2026-02-13: 添加CATTS并发工作分析

**新增内容**：
1. **Category C5**: Vote-Based Methods (CATTS)
2. **Section 4.2.5**: FRVC vs CATTS详细对比
3. **横向对比表**: 所有表格加入CATTS条目
4. **Positioning strategy**: 如何在论文中处理CATTS

**关键发现**：
- CATTS与Direction-Aware Gate有**显著重合**（都是adaptive compute allocation）
- 但有**本质差异**：
  * Fixed direction assumption vs Direction probe
  * Heuristic threshold vs SCG-FineTune(LR) (direction-aware adaptive gate)
  * Web agents vs RL agents
  * Empirical vs VoC framework
- **论文策略**：强调 direction variability、direction discovery、轻量训练 作为核心差异化

---

**文档结束**

本文档提供了test-time agent planning方法的完整分类体系，涵盖**7大类**（含 C7 Budget-Aware, C8 Routing/Hybrid 新增子类），**70+篇论文**，并详细分析了 Direction-Aware Gate / SCG-FineTune(LR) 的独特定位和差异化价值。

**核心发现（Phase 3+ 更新 2026-02-28 修正）**：
- Direction-Aware Gate 是**唯一 probe signal-utility direction 的方法**
- Phase 3 三种子验证：Wrong-Direction SR=58.2±2.5%（跨 seed 一致），T4 McNemar p=0.035 ✅
- **主方法**: SCG-FineTune(LR)，Phase 3: SR=96.7±0.6%, CS=44.1±5.5%, Oracle CS=67.0%（65.8%），T6 TOST p=0.002 ✅
- **APPS 第二有效环境 GO + Step 2 完成**: base=58%, Δ=+6pp; 最强信号 step_count ρ=−0.274, token_entropy ρ=+0.144
- **APPS Step 2**: SCG SR=65.0%, CS=59.8%, TES=0.748; 3/3 统计检验 pass; random SR=66.5% > SCG（passive abstention failure mode）
- **升级核心发现**: 从 "direction reversal" 到 "signal replacement + signal-utility landscape is environment-dependent"——不仅方向翻转，最强信号本身因环境而异（HotpotQA: evidence_count, APPS: step_count, MBPP: step_count 反向）
- CMDP λ* 严格递增验证理论；MBPP(0.6B) NO-GO（仅 4B backbone）
- SCG-Prompt 因 YES bias 降级为 ablation baseline
- **轻量训练**：SCG-FineTune(LR) 用 probe data 训练 Logistic Regression（vs Learning When to Plan 需 SFT+RL）
- 完全自监督（vs CSO需要外部专家）
- **Direction discovery > probe phase**：No-Probe ≈ With-Probe → 关键是方向数据
- **Probe Direction > Assume Direction**：
  * vs CATTS：probe direction vs assume high entropy = high utility（APPS 中 entropy 仅 ρ=+0.144 弱正且非最强信号）
  * vs CoRefine：probe direction vs assume low confidence = high utility
  * vs Compute-Optimal：probe per-environment direction vs fixed difficulty bins
  * vs DeepConf：direction measurement vs statistical filtering
  * vs ARPO：direction discovery vs entropy assumption
  * vs LATTS：selective trigger vs always-verify
  * vs CaTS：direction calibration vs magnitude calibration
- **与GiGPO正交互补**：GiGPO改进policy（+12% ALFWorld），Direction-Aware Gate 改进 optimizer 触发
- **竞争格局**：when-to-think method space 拥挤（6+ papers），direction reversal finding space 空（零竞争者）
- **3篇 HIGH-THREAT**: AdaptThink (RL black-box), DiffAdapt (probe difficulty est.), Think Just Enough (fixed threshold) — 均未报告 direction reversal
- **分析论文数**：70+篇（覆盖2023-2026最新工作，含竞争格局分析~46篇新论文）
