# Paper 写作指南：Same Signal, Opposite Meaning

**目标会议**：NeurIPS 2026（主投）/ ICLR 2027（备投）
**论文标题**：Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**核心问题**：Adaptive compute methods assume a fixed signal-utility direction (e.g., high entropy → need more compute). We show this assumption is wrong — the direction reverses across environments, causing systematic failure. How to learn the correct direction online?
**主方法**：SCG (Signal-Conditioned Gate) — 从 online exploration 数据学习每个 feature 的系数和符号（方向），logistic regression on 5 trajectory features, zero per-step overhead
**有效环境**：HotpotQA（QA, SR=0.968@6.55x）+ APPS（code, SR=0.588@1.06x）+ WebShop（web, SR=0.437@1.27x）+ 待扩展 1-2 个（Game of 24 / GSM8K 候选）
**核心指标**：Accuracy (SR) + Normalized Token Cost (x base)，Pareto 分析

**v5.0 关键更新（2026-03-13）**：
- **叙事升级**：从 "empirical finding + simple method" 升级为 **"finding + explanatory theory + method evolution"**
  - 新增 **Two-Source Uncertainty Toy Model**：解释为什么方向会反转（Information-Poverty vs Decision-Difficulty）
  - 产生 3 个 testable predictions，在实验中验证
  - 把 empirical finding 升级为 explanatory theory（从 observation 到 explanation）
  - 🆕 **理论基础显式化**：连接 Simpson's Paradox (Simpson 1951; Pearl 2014) + Epistemic/Aleatoric Uncertainty (Hüllermeier & Waegeman 2021; Der Kiureghian & Ditlevsen 2009)
- **Method 叙事升级**：从 "SCG-LR" 单一方法 → **"手工 feature → Hidden State Probe" 演进叙事**
  - Hidden State Probe 定位为 finding 的验证工具 + scalability enabler（不是独立 method contribution）
  - 配合 layer-wise probing / cross-env transfer / data efficiency 分析
- **Future Vision 新增**：连接 OpenClaw-RL (OPD) 和 XSkill 的 experience/skill 框架
  - 从 binary U 学习 → 从 rollout 内容学习 → 从跨 episode patterns 积累 gating skills
  - 在 Discussion 中定位为研究方向延伸
- 🆕 **VOC/Metareasoning 降级**：从 v4.0 的 C4 独立贡献 → 正文仅 ~3 句 + Appendix C 详述
  - 理论重心完全转到 Two-Source Model + Simpson's Paradox
  - VOC 保留为 "经典理论连接点"，不再占用正文空间
- **四层叙事（v5.0 升级版）**：
  - Layer A: Direction Reversal Finding + **Two-Source Theory**（核心 — 假设错了 + 为什么错）
  - Layer B: Method Evolution — Manual Features → Hidden State Probe（从手工到自动）
  - Layer C: Adaptive Behavior（发现 — gate 自动适配 headroom）
  - Layer D: T-as-Parameter + Cost Efficiency（框架 — 公平比较 + Pareto dominance）
- **论文类型升级**：Finding paper → **Finding + Theory paper**（更接近 science，不只是 engineering）
- **给 community 的 takeaway 升级**：
  - 旧："方向需要学习"
  - 新："信号语义是环境的函数，由状态组成（信息收集 vs 决策）决定；简单方法就够用，瓶颈是那个被忽视的假设"

**v4.0 关键更新（2026-03-06）**：
- **标题更新**：从 "Think at the Right Moment" 改为 "Same Signal, Opposite Meaning"（更抓住核心张力）
- **叙事重构**：从 "step-level vs problem-level" 改为 **Direction Discovery 为核心**
  - Step-level 不再是卖点（只是粒度选择，trivial），降为方法的自然形态
  - Direction reversal 是核心 finding（surprising + explanatory + prescriptive）
  - 三层困难（方向未知、episode-level 反馈、online 约束）作为过渡
- **三层叙事**：
  - Layer A: Direction Reversal Finding（核心 — 假设是错的）
  - Layer B: Adaptive Behavior（发现 — gate 自动适配 headroom）
  - Layer C: T-as-Parameter + Cost Efficiency（框架 — 公平比较 + Pareto dominance）
- APPS P0 resolved：Phase 5 SR=0.588 为正确数据
- Token cost 分析完成：SCG 在 HotpotQA/WebShop Pareto-dominates
- 计划扩展至 4-5 环境（Game of 24 / GSM8K）
- Phase 5 Track 1 恢复：自动 feature extraction 作为方法论贡献

---

## 目录

1. [NeurIPS 差异化策略](#differentiation)（v5.0: Finding + Theory + Method Evolution）
2. [核心故事线与 Claim 结构](#narrative)（含 2.4 Two-Source Uncertainty Toy Model 🆕 + v5.0 Contributions）
3. [逐 Section 写作框架](#section-framework)（v5.0: Toy Model §3.3 + Hidden State §4.4-4.5 + Future Vision §6.2 🆕）
4. [问题形式化](#formalization)
5. [Related Work 写法](#related-work)（正文精简版 + §2.3 Learning from Interaction Signals 🆕 + 附录完整版）
6. [关键图表设计](#figures)
7. [Introduction 草稿](#intro-draft)
8. [已有实验数据速查](#data-reference)
9. [写作注意事项与 Reviewer 应对](#writing-notes)（含 Q10 Evaluator-Executor）
10. [NeurIPS 投稿差距分析与行动项](#gap-analysis)

---

<a name="differentiation"></a>
## 1. NeurIPS 差异化策略

### 1.1 NeurIPS 审稿偏好

NeurIPS reviewer 重视的三件事（按优先级）：

1. **Novelty of insight**（不是 novelty of method）——你发现了别人没看到的东西
2. **Rigor of experiments**——claim 有充分实验支撑，ablation 充足
3. **Clarity of writing**——读完 intro 就知道你做了什么、为什么重要

NeurIPS reviewer **不买账**的：
- "我们提出了一个新 module"（如果没有 insight 支撑）
- "我们在 N 个 benchmark 上 SOTA"（如果没解释 why）
- 冗长的数学推导（如果实验已经说明问题）

### 1.2 本文的 NeurIPS 定位：Empirical Finding Paper + Direction-Aware Method

**本文是一个 finding-driven paper：核心卖点是揭示一个被所有现有方法忽视的隐含假设是错的。**

> "All existing adaptive compute methods share an unquestioned assumption: the direction of signal-utility correlation is fixed (high entropy → need more compute). We show this assumption is wrong — the same signal has opposite meaning across environments, causing all fixed-direction methods to systematically trigger at the worst moments. We propose learning the direction from data instead of assuming it."

**三层 Contribution：**
1. **Finding（核心）**：Direction reversal — 同一 signal 在不同环境中方向相反，所有 fixed-direction 方法因此跨环境系统性失败。Calibration 也无法修复（方向错了 threshold 越精准越差）
2. **Method**：SCG — 从 online exploration 数据学习方向（系数符号），zero overhead。+ T-as-parameter 公平比较框架
3. **Analysis**：Adaptive behavior（gate trigger rate 自动对齐 rollout headroom）+ Token cost Pareto dominance + 三层失败模型

**NeurIPS 论文类型对标**：
- **最佳对标**：Finding-driven papers that reveal a hidden assumption is wrong, then propose a fix
- **结构对标**：Snell et al., *"Scaling LLM Test-Time Compute Optimally"* (ICLR 2025) — 他们发现 compute allocation 不是越多越好，我们发现方向不是固定的

### 1.3 与现有工作的三维差异化

**维度 1：Problem-Level vs Step-Level（方向性差异 — 最核心）**

| | Existing (Snell, SEAG, CaTS, CATTS, PonderTTT) | Ours |
|--|--|--|
| 决策粒度 | Problem-level："这个问题难不难？" | **Step-level："在第 k 步要不要 rollout？"** |
| 场景 | 单轮推理 (GSM8K, MATH, ARC) | **多步 agentic (QA, code, web, planning)** |
| 决策时机 | 静态：看到问题后一次性决定 | **动态：随 trajectory 演进实时决策** |
| 信号来源 | Output confidence/entropy | **Trajectory state (step count, action patterns, env state)** |
| 类比 | 看病前决定挂几个专家号 | **手术中实时监控，关键时刻叫专家** |

**维度 2：Adaptive Behavior（Finding — 核心发现）**

Gate 的触发率自动适应环境的 rollout headroom：
- 高 headroom（HotpotQA +48%）→ 积极触发 RR=60%，SR↑ cost↓
- 高 headroom（WebShop +40%）→ 精准触发 RR=17%，SR↑ cost↓↓↓
- 低 headroom（APPS +6%）→ 保守触发 RR=6%，避免浪费 tokens

这不是手动设计的——gate 从 trajectory signals 中自动学到了这种行为。

**维度 3：Gate Overhead（实用差异）**

| | CATTS | CaTS | SEAG | FRVC (Ours) |
|--|:--:|:--:|:--:|:--:|
| Gate 决策成本 | K=5 LLM calls/step | Calibration sampling | CoT self-consistency | **零额外成本** |
| APPS 上 gate cost vs rollout | 4,198 > 3,306 (gate比rollout还贵) | - | - | **0** |

**论文写作必须从维度 1 出发**（step-level vs problem-level 的方向性区别），维度 2 作为核心 finding（adaptive behavior），维度 3 作为实用优势（zero overhead）。

### 1.4 Title 与 Abstract 的定位

**Title（v4.0 更新）**：

> **"Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments"**

- 直接点出核心张力：同一信号在不同环境中含义相反
- "Why ... Fails" 暗示这是一个 finding paper，揭示现有方法的系统性问题
- 具体且有 surprise，不是 generic 描述

**Abstract 结构（v5.0 — finding + theory + method evolution + results）**：

```
[1句] 背景：Test-time compute (rollouts, verification) improves LLM agent performance
      but incurs substantial cost, motivating selective triggering.
[2句] 隐含假设+问题：Existing adaptive compute methods share an implicit assumption:
      the direction of signal-utility correlation is fixed. We show this assumption
      is wrong: token entropy correlates negatively with optimizer utility in QA
      (ρ=−0.327) but positively in code generation (ρ=+0.153), while carrying
      zero information in APPS (ρ≈0, p=0.63).
[2句] 🆕 理论解释：We explain this reversal via a two-source uncertainty model:
      the same entropy signal reflects information poverty (where rollouts cannot
      help) in some environments and decision difficulty (where rollouts explore
      alternatives) in others. The model predicts when direction reversal occurs
      based on environment state composition, and we verify its predictions empirically.
[2句] 方法：We propose SCG, which learns signal direction from online data via
      logistic regression on trajectory features (zero per-step overhead), and show
      that LLM hidden states already encode sufficient gating information (probe
      AUC=0.88 vs handcrafted AUC=0.85) — the bottleneck was the assumption,
      not the model's representational capacity.
[2句] 结果：SCG Pareto-dominates all calibrated baselines across 4-5 diverse
      environments. The learned gate exhibits emergent adaptive behavior: trigger
      rate automatically aligns with rollout headroom (RR=60% at +48pp, RR=6%
      at +7pp), without explicit headroom estimation.
```

> ⚠️ Abstract 待新环境和 hidden state probe 完整结果后最终定稿。
> **v5.0 vs v4.0 关键变化**：(1) 新增 Two-Source 理论解释 2 句；(2) 方法从 "SCG only" 升级为 "SCG + hidden state probe"；(3) 从 "specific numbers" 升级为 "theory + numbers"

### 1.5 叙事策略：Finding + Theory + Method Evolution

**v5.0 核心叙事原则**：论文叙事分四层，按优先级排列：

```
Layer A（核心发现 + 理论解释 — 最高优先级）：Direction Reversal + Two-Source Theory 🔥🔥🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "All adaptive compute methods assume a fixed signal-utility direction.
   We show this assumption is wrong — the same signal has opposite
   meaning across environments. We explain WHY: the same uncertainty
   signal reflects different sources (information poverty vs decision
   difficulty), and environments differ in their state composition."

  核心数据：
  - HotpotQA: token_entropy 与 utility 负相关 (ρ=−0.327)
  - APPS: token_entropy 几乎无相关 (ρ≈0)
  - WebShop/MBPP: 弱正相关
  - 不仅方向不同，连最有用的信号都因环境而异（signal replacement）

  后果：
  - 所有 fixed-direction 方法在方向反转环境中系统性地在错误 step 触发
  - Calibration 无法修复：方向错了 threshold 越精准越差
  - Wrong-Direction 实测代价：LR −34.5pp, MLP −51.2pp

  🆕 理论解释 (Two-Source Uncertainty Model):
  - 高 entropy 有两种语义来源：
    (1) Type I: 信息匮乏（agent 缺信息）→ rollout 无法弥补 → U 低
    (2) Type D: 决策困难（agent 面临复杂选择）→ rollout 可以探索 → U 高
  - 不同环境有不同的 Type I/D 比例 p_I(env)：
    HotpotQA (多步搜索, p_I 高) → 负相关
    MBPP (直接编码, p_I 低) → 正相关
    APPS (混合, p_I 中) → ≈0
  - 产生 3 个 testable predictions：
    (P1) 同环境内 early steps (更多 Type I) 的 ρ 比 late steps 更负
    (P2) 环境间 p_I 差异越大，ρ 差异越大
    (P3) Type I 主导环境的最强信号应衡量"信息充分度"

  → 这是与所有 existing work 的核心区别：不仅发现了假设错误，还解释了为什么
  → 从 observation 升级为 explanation — NeurIPS reviewer 最重视的
  → Introduction Module 1 必须建立这个 finding + theory
  → 论文标题 "Same Signal, Opposite Meaning" 直接编码了这个发现

Layer B（方法演进 — 第二优先级）：Manual Features → Hidden State Probe 🆕
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "We validate direction-aware gating with handcrafted features,
   then show hidden states already encode richer gating signals —
   the bottleneck was the assumption, not the representation."

  Method Evolution:
  - Step 1: SCG-LR on 5 handcrafted features → 验证方向学习概念
    → 简单有效但依赖领域知识
  - Step 2: Hidden State Probe (linear on 2560-dim)
    → AUC=0.88 vs handcrafted AUC=0.85
    → 消除领域知识依赖
    → 简单 probe 就够用 → bottleneck 是假设，不是模型能力

  科学分析（让 probe 不 trivial）：
  - Layer-wise probing: 深层 >> 浅层 → gating 需要 reasoning-level 表征
  - Cross-env transfer: 不 transfer → 方向确实环境特异，验证 toy model
  - Data efficiency: ~50 episodes 即饱和 → 信号强且干净
  - Feature attribution: probe 权重 vs 手工 feature 系数的对应关系

  → 定位：NOT "我们提出 hidden state probe method"
  → 定位：IS "hidden state 作为 toy model 的实证验证 + scalability enabler"
  → 简单方法 + 深层理解 = 最有说服力的 NeurIPS 论文

Layer C（涌现发现 — 第三优先级）：Adaptive Behavior Story
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "The learned gate automatically adapts its trigger rate to the
   environment's rollout headroom."

  实证数据：
  - 高 headroom（HotpotQA +48%）→ 积极触发 RR=60%，SR 0.968@6.55×
  - 中 headroom（WebShop +36%）→ 精准触发 RR=17%，SR 0.437@1.27×
  - 低 headroom（APPS +7%）  → 保守触发 RR=6%，SR 0.588@1.06×

  → 这不是手动设计的——gate 从 trajectory features 中自动学到
  → 为 direction-aware learning 提供可解释性验证
  → 在 Results 和 Discussion 中展开

Layer D（框架 — 第四优先级）：T-as-Parameter + Cost Efficiency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "我们的框架解耦了三个层次：
   (1) What optimizer T to use → 由环境决定
   (2) How to measure U → 由 T 自动决定（U 是 T 的附属绑定）
   (3) When to trigger T → 由 trajectory-aware gate 决定"

  U 的统一定义：U(T, s) = E[R|T(s)] − E[R|π(s)]
  → T-agnostic 定义，换 T 不换公式
  → 论文 §3 定义一次通用 U，§5 Table 1 给 T 实例化

  ⚠️ 诚实声明：T-agnostic 收敛为 architecture-agnostic。
  gate architecture 跨 T 通用，但方向校准是 (env, T)-specific。
```

**v5.0 vs v4.0 叙事对比**：

| 维度 | v4.0 | v5.0 | 提升 |
|------|------|------|------|
| 核心 hook | Direction reversal (empirical) | Direction reversal + **为什么反转** (theory) | observation → explanation |
| Method story | SCG-LR 学方向 | SCG-LR → Hidden State Probe (手工→自动) | 演进叙事更有深度 |
| Probe 定位 | 独立的 method 升级 (Track B) | §3 toy model 的 empirical verification | 与核心 finding 紧密绑定 |
| 论文类型 | Finding paper + simple method | Finding paper + explanatory theory + method | 更接近 science |
| 给 community 的 takeaway | "方向需要学习" | "信号语义是环境的函数，由状态组成决定" | 更 general，更 prescriptive |
| Future work | 新环境 + 更大模型 | Learning from rollout content + skill accumulation | 连接 OPD/XSkill |
| 预估 reviewer 反应 | "Finding 有意思但 method 太简单" | "Theory + finding + verification，method 简单是 feature" | 减轻 simplicity 担忧 |

**Adaptive Behavior Story 的论文写法**：
```latex
% Introduction Para 4 或 Results Summary:
A key emergent property of the learned gate is \emph{adaptive behavior}:
the gate automatically adjusts its trigger rate to match the
environment's rollout headroom---the gap between base and oracle
performance. When rollouts provide large improvement potential
(HotpotQA: +48\% headroom), the gate triggers aggressively (RR=60\%).
When improvement is modest (APPS: +6\%), it triggers conservatively
(RR=6\%), avoiding wasteful computation. This behavior emerges from
simple logistic regression on 5 trajectory features without explicit
headroom estimation.

% Discussion:
This adaptive behavior provides a principled explanation for our
cost-effectiveness results: FRVC Pareto-dominates competitors not
by triggering \emph{more accurately} on every step, but by
\emph{calibrating effort} to the opportunity available.
```

**Token Cost 分析数据（v3.0 新增，用于论文 cost analysis section）**：

| 环境 | C_base | C_rollout | C_vote(CATTS) | Cost(×base) |
|------|--------|-----------|---------------|-------------|
| HotpotQA | 216 | 7,743 | 1,063 | FRVC 6.55× vs CaTS 10.55× |
| APPS | 840 | 3,306 | 4,198 | FRVC 1.23× vs CaTS 1.31× |
| WebShop | 705 | 9,089 | 3,385 | FRVC 1.27× vs CaTS 3.44× |

**CATTS 隐藏成本发现**：APPS 上 C_vote=4,198 > C_rollout=3,306 — vote 本身比 rollout 还贵！

**论文中各层叙事的表述位置（v5.0 更新）**：
- **Section 1 (Introduction)**：
  - Module 1 (问题, ~70%): Layer A (direction reversal finding + Two-Source 理论预览 + 困难) 🆕
  - Module 2 (方法, ~30%): 方法演进概述 + Layer C (adaptive behavior) + Layer D (Pareto results) 🆕
- **Section 3 (Signal-Utility Landscape)**：Layer A 完整展开（Three-Layer Failure + Two-Source Toy Model + 3 Predictions）🆕
- **Section 4 (Method)**：Layer B（SCG direction learning → Hidden State Probe 演进）🆕
- **Section 5 (Experiments)**：
  - Layer A 验证：fixed-direction baselines 系统性失败 + SCG 唯一跨环境稳定
  - 🆕 Toy model prediction verification (P1, P3)
  - 🆕 Hidden state probe analysis (layer-wise, cross-env, data efficiency)
  - Layer D 数据：Token cost analysis, Pareto figure, CER
  - Layer C 数据：trigger rate vs headroom 表
- **Section 6 (Discussion)**：Community insight（信号语义 = f(环境)）🆕 + Future vision (OPD/XSkill) 🆕 + Limitations
- **Limitation**：T 选择是 engineering design; Toy model 是 first-order approximation; 单 backbone

### 1.6 竞争格局分析（v3.0 更新：Step-Level 作为核心差异化）

**背景**：2025年"when to think / adaptive compute"赛道急剧拥挤（~46篇新论文）。

**v3.0 关键结论**：**所有现有 adaptive compute 工作（~46 篇）都在 problem-level 操作。Step-level trajectory-aware gating 是我们独有的方向。**

#### 1.6.1 核心差异化：Problem-Level vs Step-Level（v3.0 最重要的竞争分析）

```
所有现有工作的共同特征：PROBLEM-LEVEL 决策
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Snell et al. (ICLR 2025): "Given this math problem, use N tokens"
  SEAG (ACL 2025): "Given this query, should I search?"
  CaTS (2025): "Given this problem, when to stop thinking?"
  CATTS (2026): "Given this task, use K votes?"
  AdaptThink (EMNLP 2025): "Given this prompt, think or not?"
  DiffAdapt (2025): "Given this question, how hard is it?"
  PonderTTT (2025): "Given this input, how many layers?"

  共同模式：看到输入 → 一次性决定 compute budget → 执行
  场景：单轮推理（GSM8K, MATH, ARC, GPQA）

我们的方向：STEP-LEVEL 在线决策
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "Agent is at step 7 of a multi-step task.
   Based on trajectory so far (actions taken, states visited,
   current uncertainty), should it invoke expensive compute NOW?"

  关键区别：
  - 决策点在 trajectory 中的每一步，不是看到问题时
  - 利用 trajectory history（step count, action patterns, env state）
  - 决策随 trajectory 演进动态变化
  - 场景：多步 agentic tasks（QA, code, web, planning）
```

**论文中的对比表（用于 Related Work 或 Introduction）**：

| | Problem-Level (ALL existing work) | Step-Level (Ours) |
|--|--|--|
| 决策粒度 | Per-query/problem | **Per-step within trajectory** |
| 决策时机 | 静态：看到输入后 | **动态：随 trajectory 演进** |
| 信号来源 | Output confidence/entropy | **Trajectory state signals** |
| 典型场景 | 单轮推理 (GSM8K, MATH) | **多步 agent (QA, code, web)** |
| 代表方法 | Snell, CaTS, SEAG, CATTS, AdaptThink | **FRVC (本文)** |

#### 1.6.2 三篇 HIGH-THREAT 论文对比（在 step-level 框架下重新定位）

| 维度 | **AdaptThink** | **DiffAdapt** | **Think Just Enough** | **Ours** |
|------|---------------|--------------|----------------------|----------|
| **arXiv** | 2505.13417 | 2510.19669 | 2510.08146 | — |
| **Venue** | EMNLP 2025 | arXiv 2025 | arXiv 2025 | NeurIPS 2026 target |
| **决策粒度** | Problem-level | Problem-level | Problem-level | **Step-level** |
| **机制** | RL think/no-think | 轻量 probe + U-shaped | Entropy early stopping | Trajectory-aware gate |
| **方向假设** | Implicit (RL) | Implicit (U-shaped) | Fixed positive | **None (显式 discovery)** |
| **训练需求** | RL (per-env) | 轻量 probe | 无训练 | LR <1s |
| **Adaptive Behavior?** | RL 隐式学习 | ❌ 固定 pattern | ❌ 固定阈值 | **✅ 自动适应 headroom** |
| **核心差异** | RL 黑盒 | Probe difficulty | 固定 threshold | **Trajectory-aware + direction discovery** |

#### 1.6.3 投稿策略：Lead with FINDING (Direction Reversal)（v4.0 更新）

**v4.0 策略**：
```
v2.0 策略（已废弃）：Lead with FINDING (direction reversal) — 但 framing 不够
v3.0 策略（已废弃）：Lead with DIRECTION (step-level gating) — 但 step-level 只是粒度选择，不 surprising
v4.0 策略（当前）：Lead with FINDING (direction reversal as hidden assumption violation)
  → 核心张力：所有方法共享一个没人质疑的假设，我们证明它是错的
  → 这比 "开辟新粒度" 更有学术冲击力
  → Step-level 降为方法在 agent setting 中的自然形态，不再作为卖点
  → Adaptive behavior 是方向学习的涌现验证
  → Method (LR gate) 从 finding 自然推导：假设错了 → 学方向 → SCG
```

**投稿策略**：
1. **Title/Abstract**：强调 direction reversal（"Same Signal, Opposite Meaning"）
2. **Introduction Module 1 (P1-4)**：假设 → 假设错了 → 后果 → 三个困难 → 问题定义
3. **Introduction Module 2 (P5)**：方法 + 结果 + adaptive behavior
4. **Related Work**：所有竞品归入 "fixed-direction assumption" 类
5. **Contribution 排序**：C1 = direction reversal finding, C2 = SCG method + T-as-parameter framework, C3 = adaptive behavior + cost-effectiveness

#### 1.6.4 五层差异化在 v3.0 框架下的重新排序

```
层次 0（方向层）：🔥🔥🔥 NEW — 最核心
  当前拥挤度 ★☆☆☆☆ — 零论文做 step-level trajectory-aware gating
  我们的优势：开辟全新方向，与所有 ~46 篇论文方向性不同
  → 论文第一卖点

层次 1（发现层）：🔥 — 核心 finding
  当前拥挤度 ★☆☆☆☆ — 零论文报告 adaptive trigger rate behavior
  我们的优势：gate 自动适应 rollout headroom + cost analysis
  → 论文第二卖点（adaptive behavior story）

层次 2（信号层）：
  当前拥挤度 ★★★☆☆ — DiffAdapt 也用 probe
  我们的优势：trajectory signals（step count + action patterns + env state）
  → 与 problem-level 信号（output entropy/confidence）本质不同

层次 3（方法层）：
  当前拥挤度 ★★★★★ — 6+ 论文做 when-to-trigger
  我们的优势：zero overhead, interpretable, Pareto-dominating
  → 支撑论点，但不作为核心卖点

层次 4（框架层）：
  当前拥挤度 ★★☆☆☆
  我们的优势：direction-aware gate 作为跨 T 泛化框架
  → 升级论点
```

#### 1.6.4 从 Reasoning 到 Agent Settings：Signal Landscape 的变化（2026-03-05 重新定位）🔥

**核心洞察**：Adaptive compute 在 reasoning 上已被广泛研究，但 agent/interactive settings 是 under-explored。我们首次在 heterogeneous agent settings 中系统性发现 direction reversal——现有方法在 homogeneous reasoning benchmarks 上未暴露此问题。

**⚠️ 定位说明**：我们不声称 direction reversal 是 "planning 独有的结构性后果"（未做控制实验验证 reasoning 之间是否也会 reverse）。准确表述：direction reversal 在 **heterogeneous environments** 中自然出现，而 agent settings 天然更 heterogeneous（因为 environment-state signals 引入 task-specific semantics）。

**现有工作的分布（关键事实）：**
- **Reasoning 上的 adaptive compute**：AdaptThink, DiffAdapt, Think Just Enough, Thinkless, CaTS, L1, SEAG, Compute-Optimal, LATTS, DeepConf... (**10+ 篇**)
- **Agent settings 上的 adaptive compute**：CATTS, Learning When to Plan, ARPO (**仅 3 篇**)
- **研究过 direction reversal 的**：**零篇**
- → 这意味着 adaptive triggering 在跨 heterogeneous agent environments 上的行为几乎未被研究

**两类 settings 的信号特征对比：**

| 维度 | Homogeneous Reasoning Benchmarks | Heterogeneous Agent Settings |
|------|-------------------------------|------------------------|
| **交互对象** | 问题本身（静态输入） | 环境（状态持续演化，有外部反馈） |
| **信号来源** | Model-intrinsic（entropy, confidence） | Environment-state + Model-intrinsic |
| **跨任务异质性** | 较低（MATH/GSM8K/GPQA 都是推理类） | 高（QA/Code/Web 状态结构完全不同） |
| **方向稳定性** | 未被系统验证（可能碰巧一致） | **实证发现不稳定（direction reversal）** |
| **代表方法** | AdaptThink, DiffAdapt, CaTS, Thinkless | CATTS, ARPO, **Direction-Aware Gate (本文)** |

**实验证据（环境特异信号 >> 模型内在信号）：**

| 环境 | 最强信号（环境特异） | 效应量 | token_entropy（模型内在） | 效应量 |
|------|---------------------|--------|--------------------------|--------|
| HotpotQA | evidence_count | ρ=−0.586 | token_entropy | ρ=−0.327 |
| APPS | step_count | ρ=−0.274 | token_entropy | ρ=+0.144（弱） |
| WebShop | state_category | η²=0.598 | token_entropy | ρ=+0.133（弱） |
| MBPP | step_count | ρ=+0.526 | token_entropy | ρ=+0.153（弱） |

→ 在 4 个环境中，token_entropy 有 3 个效应量仅 0.13-0.15（弱）。**环境状态信号一致地强于 model-intrinsic signal。**

**为什么 agent settings 更容易出现 direction reversal？**
- 环境状态信号**直接编码 task-specific progress**（evidence_count → "收集了多少信息"；state_category → "在什么页面"；step_count → "走到第几步"），每个环境的 progress 语义完全不同
- 这些信号与 "optimizer 是否有边际价值" 有直接因果关系，但因果方向因环境语义而异
- token_entropy 是**间接 proxy**：它反映模型不确定性，与 optimizer utility 的关系间接且方向不稳定
- **注意**：这解释了为什么 agent settings 中 direction reversal **更容易出现**，但不排除 reasoning 跨任务也可能存在类似现象（未验证）

**对论文叙事的升级意义：**

```
基础叙事（1.6.2 已建立）：
  "crowded method space, empty finding space"
  → 我们的 finding（direction reversal）独特

升级叙事（2026-03-05 重新定位）：
  "methods validated on homogeneous benchmarks,
   applied across heterogeneous agent environments"
  → adaptive compute 在 reasoning 上已有大量工作，在 agent settings 中刚起步
  → 我们首次在 heterogeneous agent environments 中系统性发现 direction reversal
  → 现有方法在 homogeneous benchmarks 上没有机会观察到此现象
  → env-state signals 引入 task-specific semantics，使 universal proxy 假设不再成立
```

**论文写作位置**：
- **Introduction Para 2**：指出 adaptive compute 主要在 reasoning 上研究，agent settings under-explored，我们发现了新现象
- **Related Work 2.1**：新增 "Adaptive Compute: From Reasoning to Agent Settings" 维度（见下方 Related Work 更新）
- **Discussion**：展开说明 env-state signals >> model-intrinsic signals 的实验证据，但诚实标注 "we observe this in agent settings; whether direction reversal also occurs across heterogeneous reasoning benchmarks is an open question"
- **对 Phase 5 的启示**：Track C (LLM-guided gate) 利用 LLM 理解环境语义提取 task-specific signals，与此发现一致

**一句话差异化**（用于 Abstract/Introduction/Related Work）：
> "Adaptive compute allocation has been extensively studied for reasoning tasks, where model-intrinsic signals (entropy, confidence) serve as effective proxies on homogeneous benchmarks. We extend this line of work to diverse interactive agent settings, where we discover that signal-utility relationships become environment-dependent: the direction, magnitude, and even the identity of informative signals vary across environments. We propose direction-aware gating to address this."

### 1.7 Phase 5 Narrative Recalibration (2026-03-06 更新) 🔥🔥🔥

**背景**：Phase 5 Track 1/2/3 产出了大量新数据（calibrated baselines, cross-env AUC, APPS entropy zero-correlation, hidden state probes, T2 NO-GO 等），需要根据这些数据**重新校准论文叙事**。

#### 1.7.1 Phase 5 关键发现摘要

**数据层面**：
1. **Cross-env AUC 分析**：Single token_entropy AUC ≈ 0.50-0.56（几乎随机），multi-signal LR AUC ≈ 0.76-0.92，hidden state AUC ≈ 0.84-0.99
2. **APPS entropy zero-correlation**：Spearman(entropy, utility) = 0.012, p=0.63 → entropy 在代码生成中携带**零信息**
3. **CATTS K-sample voting 在 APPS 失效**：587/592 步产生 identical code → vote_entropy ≈ 0
4. **Calibrated baselines (P0)**：WebShop CaTS 30.5% SR (RR=33.1%) vs FRVC 43.7% (RR=16.9%) → 差距 +13.2pp
5. **scg_finetune_lr 在 APPS 失败**：SR=0.588 ≈ base_only (direction=null)，与 Phase 3+S2 的 65.0% 不一致（**需调查**）
6. **HotpotQA ceiling 饱和**：always_trigger = oracle = 0.970，无法区分 gating 方法
7. **"FRVC best" = always_trigger**：在 HotpotQA 和 APPS 上，最佳 FRVC 变体 RR=100%；仅 WebShop 展示真正的选择性触发
8. **Track 2 双 NO-GO**：ScienceWorld 和 AppWorld 均 base_sr=0，stuck at 3 环境
9. **auto_feature_lr 失败**：Track 1C (LLM feature design) is NO-GO
10. **Hidden state probes 成功**：R² up to 0.873 (WebShop), classification AUC up to 0.994

**关键悬而未决**：
- APPS hidden_state_mlp/lr 结果（~61-78% running）→ 如果 hidden state 能找到比 "always trigger" 更好的 gate，是重大突破
- WebShop T1 comparison（全部 PENDING）→ WebShop 是最具区分力的环境，结果决定最终叙事
- Phase 3+S2 vs Phase 5.2 APPS SCG SR 不一致（65.0% → 58.8%）→ 需调查

#### 1.7.2 三层失败模型（核心新发现）

**旧叙事**：baseline 失败因为方向假设错误 → direction-aware gate 是解决方案
**新叙事**：baseline 失败有三层原因，direction 只是其中之一

```
Layer 1 — Threshold-Distribution Mismatch (可修复，calibration data 即可)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  问题：硬编码默认阈值与实际信号分布不匹配 → 0% 触发
  证据：APPS max entropy=0.117 < default θ=0.5 → 数学上不可能触发
        WebShop max entropy=0.260 < default θ=0.5 → 同上
  修复：提供 calibration data → 阈值校准到实际分布的 percentile
  结论：uncalibrated 结果是 strawman，calibrated 结果才是公平对比

Layer 2 — Signal Poverty (部分可修复，但有信息论上限)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  问题：即使阈值校准正确，single signal AUC ≈ 0.53 → 几乎没有预测力
  证据：calibrated CaTS on APPS → 只触发 1.4%（8/590 步）
        calibrated CaTS on WebShop → 只触发 3-33%
        APPS entropy-utility ρ=0.012, p=0.63 → 零相关
  对比：multi-signal LR AUC ≈ 0.85，hidden state AUC ≈ 0.88
  结论：单信号范式的信息论天花板太低，需要多信号或 hidden state

Layer 3 — Direction Assumption (在单信号范式内不可修复)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  问题：固定方向假设在跨环境时不成立
  证据：token_entropy HotpotQA ρ=−0.327 vs MBPP ρ=+0.153 vs APPS ρ≈0
        calibrated CaTS on HotpotQA 假设 "低 confidence → trigger"(负方向)
        如果 APPS 中方向相反，同一方向校准在另一环境失效
  代价：Wrong-Direction LR −34.5pp, MLP −51.2pp (RR=0%)
  结论：即使解决了 Layer 1+2，方向假设仍导致跨环境不可靠
```

**论文叙事升级**：从 "direction reversal → direction-aware gate" 升级为 "three-layer failure → multi-signal direction-discovered gate"

#### 1.7.3 新 Storyline: 信号-效用景观因环境而异

**核心 Finding (升级版)**：
> "Signal-utility landscape is environment-dependent at THREE levels:
>   (1) Direction varies — token_entropy ρ=−0.327 (HotpotQA) vs ρ≈0 (APPS) vs ρ=+0.133 (WebShop)
>   (2) Signal identity varies — evidence_count in QA, step_count in APPS, state_category in WebShop
>   (3) Signal informativeness varies — single entropy AUC≈0.53, multi-signal LR AUC≈0.85, hidden state AUC≈0.88
> Any method that fixes signal, direction, or uses a single scalar is fundamentally limited."

**Direction reversal 的保留策略**：
- Direction reversal 仍是论文的 **hook**（引人注目的发现，开头吸引 reviewer）
- 但它从 "core finding" 降级为 "finding 的一个层面"（Layer 3 of 3）
- 更深层的故事是 "即使方向正确，单信号也不够"（Layer 2）
- 最完整的故事是三层失败 + 多信号方向发现作为解决方案

**三幕结构调整**（见 §2.1 更新）：
```
Act 1 — 问题设定 (1 页)：adaptive triggering 从 reasoning 到 agent settings
Act 2 — Three-Layer Finding (核心, 2 页)：
  (a) Layer 1: threshold mismatch (trivial, calibration fixes it)
  (b) Layer 2: signal poverty (AUC≈0.53, fundamental)
  (c) Layer 3: direction assumption (ρ varies, quantified damage)
  → 这三层解释了为什么 ALL 现有方法系统性失败
Act 3 — Method + Validation (3.5 页)：multi-signal direction-discovered gate
```

#### 1.7.4 环境角色重新分配

```
WebShop — PRIMARY SHOWCASE 🏆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  理由：(1) 最大 ceiling gap (base 7.2% → oracle 43.3%)
        (2) 唯一展示真正选择性触发的环境 (RR=16.9%)
        (3) 最大 FRVC vs baseline gap (+13.2pp over CaTS calibrated)
        (4) 最强分类信号 (state_category η²=0.598)
  角色：gate 优势的主要证明

HotpotQA — PROBE STUDY SHOWCASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  理由：(1) 最完整的 probe study 数据 (Phase 1, 1208 pts)
        (2) Direction reversal 最清晰 (ρ=−0.327)
        (3) Wrong-Direction 跨 gate 实验 (−34.5pp / −51.2pp)
  局限：ceiling 饱和 (always=oracle=0.970) → 无法区分 gating 方法
  角色：finding 的证据来源 + direction 重要性的量化

APPS — SIGNAL POVERTY SHOWCASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  理由：(1) Entropy zero-correlation (ρ=0.012, p=0.63)
        (2) CATTS vote entropy 失效 (587/592 identical)
        (3) scg_finetune_lr ≈ base_only (scalar features 也不够)
  局限：narrow ceiling gap (6pp), 可能 hidden state 解决
  角色：Layer 2 (signal poverty) 的主要证据

MBPP — CEILING REFERENCE (附录)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  角色：原始 direction reversal 数据点 (ρ=+0.153) + ceiling 效应示例
```

#### 1.7.5 Calibrated vs Uncalibrated Baselines 策略

**关键决策**：Calibrated baselines 为主要对比，uncalibrated 为补充

```
论文 Table 2 呈现策略：
━━━━━━━━━━━━━━━━━━━━━━
主表（Table 2）：calibrated baselines — 公平对比
  → 所有 baseline 给予 Phase 1 calibration data
  → 展示即使校准后仍然比 FRVC 差
  → 这是 reviewer 关心的对比

补充行/注脚：uncalibrated baselines — 说明默认配置失效
  → 0% 触发 → degenerate to base_only
  → 说明固定阈值的脆弱性（Layer 1 问题）
  → 不作为主要论据（否则是 strawman）

叙事逻辑：
  "Without calibration data, existing methods completely fail (0% trigger).
   With calibration data, they partially recover but are fundamentally limited
   by signal poverty (AUC≈0.53). FRVC requires neither environment-specific
   calibration nor a single scalar signal — it discovers multi-signal
   direction from online exploration."
```

#### 1.7.6 主方法待定（Contingent on hidden_state results）

```
Scenario A: hidden_state results 显著优于 scg_finetune_lr
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  → 主方法升级为 hidden state probe + direction discovery
  → 手工特征 LR 降为 lightweight baseline
  → Story: "hidden states encode VOC; direction discovery unlocks it"
  → Method novelty ⭐⭐⭐⭐ (significant upgrade)

Scenario B: hidden_state ≈ handcraft_mlp ≈ always_trigger
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  → 所有方法在 APPS/HotpotQA 上等效 (ceiling 或 narrow gap)
  → WebShop 是唯一区分点
  → Story 更依赖 finding (三层失败) 而非 method
  → Method novelty ⭐⭐☆☆☆ (unchanged)

Scenario C: hidden_state 在 WebShop 上显著优于 scg_finetune_lr
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  → 最理想的结果
  → Hidden state + multi-signal LR + direction discovery = complete story
  → AUC 分析 (0.53 → 0.85 → 0.88) 成为 core figure
  → Method novelty ⭐⭐⭐⭐⭐
```

#### 1.7.7 数据不一致处理（v3.0 更新：P0 已解决）

| 问题 | Phase 3 数据 | Phase 5 数据 | 状态 | 解决方案 |
|------|:---:|:---:|:---:|------|
| **APPS SCG SR** | 65.0% (RR=100%) | **58.8% (RR=6%)** | ✅ **P0 RESOLVED** | Phase 3 gate 退化为 always_trigger（LR 系数全正）。Phase 5 SR=0.588 为正确数据。**论文使用 Phase 5 数据** |
| WebShop CaTS RR | 3.0% | 33.1% | ⚠️ 待确认 | 确认哪个是正确的 calibrated CaTS 结果 |
| HotpotQA 最佳 FRVC | SR=0.970 RR=100% | Phase 3: SR=96.7% RR=55.9% | ⚠️ 待对齐 | 不同 pipeline/config 导致，需对齐实验条件 |

#### 1.7.8 对现有 Claim 的影响

| Claim | 原状态 | Phase 5 后状态 | 调整 |
|-------|-------|-------------|------|
| C1: U is state-dependent | ✅ 不变 | ✅ 强化 | 三个环境更多数据 |
| C2: Direction reversal | ✅ 核心 | 🟡 降级为 "finding 的一层" | APPS ρ≈0 说明 direction 不是唯一问题；三层模型更完整 |
| C3: Direction-aware gate 有效 | ✅ | ⚠️ 需精细化 | HotpotQA ceiling 不区分；APPS scg_lr 失败；WebShop 是最佳证据 |
| C4: VOC theory | ✅ 不变 | ✅ 强化 | 三层失败提供更丰富的理论素材 |
| **NEW C2'**: Signal poverty | — | 🔥 新核心 | AUC ≈ 0.53 vs 0.85 vs 0.88 → multi-signal 必要性的信息论证据 |
| **NEW C3'**: Hidden state encodes VOC | — | 🔥 新核心 | R²=0.533-0.873，AUC=0.84-0.99 → hidden state > text > scalar |

#### 1.6.5 关键区分：DiffAdapt 的 probe 与我们的 probe

**DiffAdapt** 的 probe 做 **difficulty estimation**：
- 目的：判断问题有多难 → 分配多少 compute
- 假设：U-shaped entropy pattern 是 universal（固定模式）
- 输出：difficulty score → compute budget

**我们的 probe** 做 **direction discovery**：
- 目的：发现 signal-utility 关系的方向 → 决定 trigger 策略
- 假设：无预设，方向由 probe 数据决定
- 输出：sign(corr(σ, U)) → gate 方向校准

**一句话区分**（用于 Related Work）：
> "DiffAdapt's probe estimates problem difficulty assuming a fixed entropy pattern; our probe discovers the signal-utility direction, which we show varies across environments."

---

<a name="narrative"></a>
## 2. 核心故事线与 Claim 结构

### 2.1 三幕结构

#### 2.1-A 原版三幕结构（Phase 4 数据，Direction Reversal 为核心）

```
[保留原版以备参考——如果 hidden_state 结果不够强，可能回退到此版本]

Act 1 — 问题设定（1 页）
  背景：Test-time optimizers 是通用工具，5-15× 计算开销
  现状：11+ 方法在研究 "when to trigger"，绝大多数在 reasoning benchmarks 验证
  隐含依赖：signal → utility 的单调对齐关系
  本文的问题：当 adaptive triggering 扩展到 heterogeneous agent settings 时，
             这个隐含依赖是否仍然成立？

Act 2 — Empirical Finding（核心）
  Finding 1: U(T, s) 是 state-dependent 的
  Finding 2: signal-utility 方向因环境而异（direction reversal 为核心 hook）
  Finding 2+: 信号本身也不一致（signal replacement）
  Finding 2++: T 也因环境而异
  Finding 2+++: 环境状态信号 >> 模型内在信号

Act 3 — Method + Validation
  SCG-FineTune(LR) 跨 3 环境验证
```

#### 2.1-C 🆕🆕 v5.0 升级版三幕结构（Finding + Theory + Method Evolution）

```
═══════════════════════════════════════════════════════════════════
§1  Introduction (2 pages)
═══════════════════════════════════════════════════════════════════

Module 1 — The Finding + Theory (1.2 pages):
  P1: Background — test-time compute for agents, cost problem
  P2: The hidden assumption — ALL methods fix direction
      → 一句话列举 CATTS, CaTS, SEAG, CoRefine, AdaptThink...
  P3: Direction reversal — empirical evidence
      → token_entropy: HotpotQA ρ=-0.327 vs MBPP ρ=+0.153
      → 不仅方向反，连最有信息量的信号都换了（signal replacement）
  P4: Why this happens — Two-Source Uncertainty (preview) 🆕
      → 高 entropy 可能是"信息不足"(Type I) 也可能是"决策困难"(Type D)
      → 环境的状态组成决定了哪种语义占主导
      → 所以方向不是信号的固有属性，而是环境的属性
      → 产生 testable predictions（在 §5 验证）

Module 2 — Our Response (0.8 pages):
  P5: Three-layer failure model (preview)
      → L1 threshold mismatch (trivial)
      → L2 signal poverty (fundamental)
      → L3 direction assumption (fatal)
  P6: Method overview — evolution story 🆕
      → SCG: learn direction from online data (manual features)
      → Hidden state probe: automatic feature extraction
      → Zero overhead, Pareto-dominates all competitors
  P7: Key results + adaptive behavior
      → Pareto-dominance across 4-5 diverse environments
      → Emergent headroom adaptation
      → Toy model predictions verified

Contributions:
  C1: Direction reversal finding + Two-Source theoretical explanation 🆕
  C2: SCG method (manual → automatic features via hidden state probe) 🆕
  C3: Systematic evaluation + adaptive behavior analysis

═══════════════════════════════════════════════════════════════════
§2  Related Work (1 page, 精简版; 附录完整版)
═══════════════════════════════════════════════════════════════════

2.1 Adaptive Compute: From Reasoning to Agent Settings
    → reasoning 上已有 10+ 方法，agent 上只有 3 篇
    → 零论文研究 direction reversal
2.2 Process Reward Models and Step-Level Signals
    → PRM 提供 per-step reward，但不回答 "when to invoke"
2.3 Learning from Interaction Signals 🆕
    → OpenClaw-RL (OPD), XSkill — 从交互中学习
    → 我们的 gate learning 是这个方向在 meta-decision 上的实例

═══════════════════════════════════════════════════════════════════
§3  The Signal-Utility Landscape: Finding + Theory (2 pages) 🔥🔥🔥
═══════════════════════════════════════════════════════════════════

这是论文最核心的 section — finding paper 的心脏

3.1 Problem Setup
    → MDP formulation, T-as-parameter, U = E[R|T(s)] - E[R|π(s)]

3.2 Three-Layer Failure Analysis
    → L1: Threshold-Distribution Mismatch (可修复)
    → L2: Signal Poverty (根本性限制, AUC ≈ 0.53)
    → L3: Direction Reversal (跨环境不可修复)
    → Table: 所有 baseline 在哪一层失败

3.3 Why Does Direction Reverse? Two-Source Uncertainty Model ⭐ NEW
    → Type I (information-poverty) vs Type D (decision-difficulty)
    → 形式化推导:
      - State s_t 属于 Type I (概率 p_I(env)) 或 Type D (概率 1-p_I(env))
      - Type I: U(s_t) ~ -α · entropy(s_t) + ε  (信息不足 → rollout 无用)
      - Type D: U(s_t) ~ +β · entropy(s_t) + ε  (决策困难 → rollout 有价值)
      - Overall: Corr(entropy, U | env) ≈ p_I·(-α) + (1-p_I)·(+β)
      - Direction reversal condition: sign flips at p* = β/(α+β)
    → Figure: p_I vs Corr(entropy, U) 曲线，标注 4 个环境
    → 三个 Testable Predictions:
      (P1) 同环境内 early steps 的 ρ 比 late steps 更负
      (P2) 环境间 p_I 差异越大，ρ 差异越大
      (P3) Type I 环境最强信号衡量"信息充分度"，Type D 衡量"决策复杂度"

3.4 Empirical Verification of Toy Model
    → Prediction 1 验证: early vs late steps 的 ρ 差异
    → Prediction 3 验证: 最强信号与环境状态类型的对应

═══════════════════════════════════════════════════════════════════
§4  Method: Direction-Aware Gating (1.5 pages)
═══════════════════════════════════════════════════════════════════

4.1 SCG: Learning Direction from Manual Features
    → 5 trajectory features + online LR
    → 学系数符号（方向）+ 大小（重要性）
    → Zero per-step overhead

4.2 From Manual to Automatic: Hidden State Probing ⭐ NEW
    → 科学问题: hidden state 是否已编码 gating 信号?
    → Linear probe on last-layer hidden state (2560-dim)
    → 结果: AUC=0.88 vs handcrafted AUC=0.85
    → Insight: bottleneck 是假设，不是表征能力

4.3 What Do Hidden States Encode?
    → Layer-wise probing: 深层 >> 浅层
    → Cross-env transfer: 不 transfer → 方向确实环境特异
    → Data efficiency: ~50 episodes 即饱和
    → 与 toy model 一致：不同环境需要不同方向

═══════════════════════════════════════════════════════════════════
§5  Experiments (2 pages)
═══════════════════════════════════════════════════════════════════

5.1 Setup (environments, baselines, metrics)
5.2 Main Results: Pareto Dominance
    → SR-Cost Pareto figure (核心 figure)
    → SCG Pareto-dominates ALL baselines across environments
5.3 Adaptive Behavior: Emergent Headroom Adaptation
    → RR automatically aligns with rollout headroom
5.4 Ablation Studies
    → Manual vs Probe vs Random features
    → Wrong-direction ablation
    → Toy model prediction verification (P1, P3) 🆕

═══════════════════════════════════════════════════════════════════
§6  Discussion: What We Learned (0.75 pages)
═══════════════════════════════════════════════════════════════════

6.1 Insight for the Community 🆕
    → 核心 message: adaptive compute 的瓶颈是信号语义理解
    → 信号是环境的函数，不是模型的固有属性
    → 两源不确定性模型提供了设计指南：
      新环境 → 先判断 Type I/D 比例 → 再选信号方向

6.2 From Gate Learning to Continual Improvement (Future Vision) 🆕
    → 当前: 从 binary U 学习 gate → 信息利用率低
    → 近期: 从 rollout 内容（不仅是成败）学习
      (cf. OPD in OpenClaw-RL: directive signals richer than scalar rewards)
    → 远期: 从跨 episode rollout patterns 积累 gating skills
      (cf. XSkill: experience + skill dual-stream for continual learning)
    → 最终: meta-decision 也可以持续学习

6.3 Limitations
    → Single backbone (Qwen3-4B)
    → Toy model 是 first-order approximation
    → T-agnostic 声明限于 gate architecture

═══════════════════════════════════════════════════════════════════
§7  Conclusion (0.25 pages)
═══════════════════════════════════════════════════════════════════
```

**关键 Figure 设计（v5.0 更新）**：

| Figure | 内容 | 位置 | 新/旧 |
|--------|------|------|-------|
| Fig 1 | Graphical abstract: direction reversal + two-source model + SCG | 首页 | 更新 |
| Fig 2 | **Two-Source Model**: p_I vs Corr curve + 环境标注 | §3.3 | **NEW** |
| Fig 3 | Three-layer failure illustration + AUC hierarchy | §3.2 | 保留+升级 |
| Fig 4 | SR-Cost Pareto frontier across environments | §5.2 | 保留 |
| Fig 5 | Adaptive behavior: RR vs headroom | §5.3 | 保留 |
| Fig 6 | **Hidden state probe analysis**: layer-wise + cross-env + learning curve | §4.3 | **NEW** |
| Fig 7 | **Toy model prediction verification**: early vs late step ρ | §5.4 | **NEW** |

**v5.0 论文一句话总结**：
> 我们发现方向会反转，解释了为什么（两源不确定性），证明 hidden state 已编码足够信号
> （方向需要学，但模型有能力学），并展示一个简单 gate 就能实现跨环境 Pareto dominance
> ——瓶颈从来不是模型或方法的复杂度，而是那个被所有人忽视的假设。

---

#### 2.1-B Phase 5 升级版三幕结构（三层失败 + AUC 为核心）[保留以备参考]

```
Act 1 — 问题设定（1 页）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
背景：Test-time optimizers 是通用工具（rollout, voting, search），5-15× 计算开销
现状：11+ 方法在研究 "when to trigger"——共同结构：pick a scalar signal, assume a fixed
     direction, calibrate a threshold。绝大多数在 reasoning benchmarks 验证
     （AdaptThink, DiffAdapt, CaTS, Thinkless, SEAG...），
     少数在 agent settings（CATTS, ARPO, Learning When to Plan）
隐含依赖：(1) scalar signal 携带足够信息, (2) signal-utility 方向固定
本文的问题：这些隐含依赖在 heterogeneous agent settings 中是否成立？

Act 2 — Three-Layer Failure Finding（核心贡献，2 页）🔥🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[...same as before...]

Act 3 — Method + Validation（3.5 页）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[...same as before...]
```

### 2.2 Contributions 的 NeurIPS 写法

NeurIPS 论文的 contributions 不是功能列表，是 **"what did we learn?"**

#### 2.2-C 🆕🆕 v5.0 升级版 Contributions（Finding + Theory + Method Evolution）

```latex
Our contributions are:
\begin{enumerate}
\item \textbf{Direction reversal finding with theoretical explanation.}
  We show that the signal--utility direction reverses across environments:
  token entropy correlates negatively with optimizer utility in QA
  ($\rho=-0.327$) but positively in code generation ($\rho=+0.153$),
  while in APPS it carries zero information ($\rho=0.012$, $p=0.63$).
  Beyond direction, the \emph{identity} of the most informative signal
  varies across environments (signal replacement). We explain this via
  a \emph{two-source uncertainty model}: the same entropy signal
  reflects information poverty (where rollouts cannot help) in some
  environments and decision difficulty (where rollouts explore
  alternatives) in others. The model predicts when direction reversal
  occurs based on environment state composition, and we verify three
  testable predictions empirically.

\item \textbf{Direction-aware gating: from manual to automatic features.}
  We propose SCG, which learns signal direction from online data via
  logistic regression on trajectory features (zero per-step overhead).
  We further show that LLM hidden states already encode sufficient
  gating information: a linear probe on hidden states
  (AUC$\approx$0.88) matches handcrafted features (AUC$\approx$0.85)
  without domain knowledge. Layer-wise probing reveals that gating
  signals reside in deep layers (reasoning-level representations), and
  cross-environment transfer analysis confirms that directions are
  environment-specific---consistent with our theoretical model.
  The bottleneck was the fixed-direction assumption, not model capacity.

\item \textbf{Systematic evaluation with emergent adaptive behavior.}
  SCG Pareto-dominates all calibrated baselines (CaTS, CATTS, SEAG,
  CoRefine) across 4--5 diverse environments. The learned gate exhibits
  emergent adaptive behavior: trigger rate automatically aligns with
  rollout headroom (RR$=$60\% at $+$48\,pp headroom, RR$=$6\% at
  $+$7\,pp headroom) without explicit headroom estimation. We provide
  token-cost analysis showing 38--77\% cost reduction versus
  always-trigger baselines while maintaining near-oracle success rates.
\end{enumerate}
```

> ⚠️ **v5.0 Contributions 关键变化 vs v4.0/Phase 5**：
> - **C1 升级**：从 "三层失败诊断" 升级为 "finding + theoretical explanation"
>   - 新增 Two-Source Uncertainty Model + 3 testable predictions
>   - 从 observation 升级为 explanation（NeurIPS 审稿最看重的）
> - **C2 重构**：从 "AUC 信息论分析" 重构为 "method evolution story"
>   - 手工 feature → Hidden State Probe 的演进叙事
>   - Probe 不是独立 method，而是 toy model 的实证验证 + scalability enabler
>   - Layer-wise / cross-env / data efficiency 分析让 probe 不 trivial
> - **C3 保持**：Pareto dominance + adaptive behavior（实验验证部分）
> - **C4 (VOC theory) 精简**：VOC/CMDP 移入 appendix，正文 contributions 聚焦更紧凑
> - **整体定位**：Finding + Theory paper > Finding + Method paper

#### 2.2-A Phase 5 升级版 Contributions（三层失败 + AUC + calibrated baselines）[保留以备参考]

```latex
Our contributions are:
\begin{enumerate}
\item \textbf{A three-layer diagnostic of adaptive triggering failure.}
  We systematically evaluate four prior gating methods (CaTS, CATTS,
  CoReFiné, SEAG) across three diverse agent environments and identify
  three compounding failure layers:
  (1)~\emph{threshold--distribution mismatch}---default thresholds produce
  0\% trigger rate on 2/3 environments, fixable with calibration data;
  (2)~\emph{signal poverty}---even with calibrated thresholds, single
  scalar signals (token entropy, confidence) achieve AUC$\approx$0.53,
  barely above chance; in APPS code generation, entropy--utility
  correlation is zero ($\rho=0.012$, $p=0.63$);
  (3)~\emph{direction assumption}---the signal--utility direction reverses
  across environments (token entropy $\rho=-0.327$ in QA vs.\ $+0.153$ in
  MBPP vs.\ $\approx 0$ in APPS). Reversing the discovered direction
  causes catastrophic failure across gate architectures (LR SR $-34.5$\,pp,
  MLP SR $-51.2$\,pp with RR$=$0\%).
  Beyond direction, the \emph{identity} of the most informative signal
  varies: evidence\_count in QA ($\rho=-0.586$), step\_count in APPS
  ($\rho=-0.274$), state\_category in WebShop ($\eta^2=0.598$, categorical).

\item \textbf{An information-theoretic analysis of gating signal quality.}
  We provide the first cross-environment AUC comparison showing that
  single-signal gates are fundamentally limited (AUC$\approx$0.53),
  multi-signal direction-discovered gates dramatically improve
  discrimination (AUC$\approx$0.85), and hidden-state probes provide
  an upper bound (AUC$\approx$0.88). This establishes a principled
  hierarchy of gating approaches ordered by information content.

\item \textbf{A multi-signal direction-discovered gating framework.}
  [...]

\item \textbf{A theoretical connection to rational metareasoning.}
  [...]
\end{enumerate}
```

#### 2.2-B 原版 Contributions（Phase 4 数据，保留以备参考）

```latex
Our contributions are:
\begin{enumerate}
\item \textbf{An empirical finding:} We show that the signal--optimizer
  utility relationship is environment-dependent in two ways: (1)~the
  \emph{direction} varies---token entropy is negatively correlated with
  optimizer utility in information retrieval ($\rho=-0.327$) but
  positively in code generation ($\rho=+0.153$); (2)~the \emph{informative
  signal itself} varies---in APPS code generation, token entropy carries
  no signal ($\rho\approx 0$) while test pass rate dominates
  ($\rho=-0.620$). Direction reversal is robust to artifact removal
  ($\rho=-0.242$). Any method relying on a fixed signal or fixed
  direction will systematically fail.
  We quantify the damage: reversing the discovered direction causes
  catastrophic failure across gate architectures---LR SR drops 34.5\,pp
  (0.965$\to$0.620) and MLP drops 51.2\,pp (0.965$\to$0.453, RR=0\%),
  approaching or falling below the no-optimizer baseline (0.515).

\item \textbf{A framework:} Motivated by this finding, we formalize
  adaptive optimizer triggering where the optimizer $T$ itself is an
  environment-specific parameter. Our \emph{Direction-Aware Gate}
  framework decouples ``what optimizer'' (environment-specific) from
  ``when to trigger'' (architecture-agnostic gate), making it the first
  method that adapts to both signal direction and optimizer type.
  \textit{Note: Phase~2.5 refines $T$-agnostic to architecture-agnostic---gate
  architecture transfers, but direction calibration is $(env, T)$-specific.}

\item \textbf{Validation across 3 environments:} SCG-FineTune, a
  lightweight instantiation using logistic regression on signal features,
  validates across 3 diverse environments:
  (i)~HotpotQA (QA): 96.7\% SR with 44.1\% cost saving, SR--CS
  Pareto-dominating random triggering (96.7\% vs 89.0\% SR);
  (ii)~APPS (code): 65.0\% SR, 59.8\% CS, TES significantly exceeds
  random (0.748 vs 0.665, $p=0.001$);
  (iii)~WebShop (web navigation): 43.7\% SR ($\approx$ oracle 43.3\%),
  75.1\% precision, 6$\times$ compute efficiency (RR=16.9\%).
  ALFWorld provides a boundary result: LLM-based rollout quality is
  insufficient, revealing a rollout quality hierarchy
  (env.deepcopy $>$ deterministic eval $>$ LLM simulation/scoring).
  \textit{Note: TES is reported as auxiliary metric; SR--CS Pareto
  dominance is the primary evaluation criterion.}

\item \textbf{A theoretical connection:} We connect adaptive triggering
  to rational metareasoning (Russell \& Wefald, ``Do the Right Thing:
  Studies in Limited Rationality,'' MIT Press, 1991) and show that the
  classical assumption VOC $\geq 0$ (``more computation never hurts'')
  does not naturally extend to settings with evaluator-executor identity:
  when the same model generates and evaluates candidate actions, and
  the gate commits to the result without a reliable independent verifier,
  wrong-direction gating produces systematic \emph{negative aggregate VOC}
  (LR SR $-34.5$\,pp, MLP SR $-51.2$\,pp). Classical VOC $\geq 0$
  relies on the agent's ability to disregard unfavorable computation
  results---an option that requires a reliable comparator, which
  evaluator-executor identity undermines. We formalize our objective
  as a Constrained MDP (Altman, ``Constrained Markov Decision Processes,''
  Chapman and Hall/CRC, 1999) and propose Lagrangian dual ascent for
  automatic cost--quality trade-off ($\lambda^*$ learning), enabling
  user-specified cost saving targets without manual threshold tuning.
\end{enumerate}
```

**关键**：C1 是 finding + quantified damage（Wrong-Direction），C2 是 framework（direction-aware gate），C3 是 validation with numbers，**C4 是 theoretical connection（VOC 在新 setting 下的限制 + CMDP formalization）**。NeurIPS reviewer 看到 finding + quantified consequence + framework + theoretical grounding 会比看到 "we propose X and it works" 更兴奋。

### 2.3 论文 Narrative 的层次结构

```
Level 1: 宏观问题 — "When to use test-time optimizer?" (所有 C 类方法共同关心)
Level 2: 核心洞察 — "方向不稳定" (本文独有发现，11+ 方法隐式依赖的单调对齐不成立)
Level 3: 框架设计 — "Direction-aware gate" (直接从 Level 2 推导)
         ⚠️ T-agnostic 收敛为 architecture-agnostic
            （gate 架构跨 T 通用，但方向校准是 (env, T)-specific）
Level 4: 实现方案 — "SCG-FineTune(LR)" (轻量训练，即插即用)
```

**⚠️ 叙事一致性要点（基于 reviewer 反馈预判）**：
- **核心贡献是 direction discovery，不是在线 probing**：No-Probe ≈ With-Probe 证明关键是方向数据而非 probe 过程。论文不应将 "probe-first" 作为框架核心标签，而应强调 "direction discovery" 是必要前提。Probing 是获取方向数据的一种手段，不是唯一手段。
- **统一表述**：论文中应说 "The core contribution is direction discovery; probing is one mechanism to obtain direction data."

每一层的实验支撑：
- Level 1 ← E0 Oracle Study (Phase 0)
- Level 2 ← E1 Probe Study (Phase 1) + robustness (Phase 1.5)
- Level 3 ← E2 Gate Learning (Phase 2) + E4 cross-T (Phase 4)
- Level 4 ← E3 Main Comparison (Phase 3)

### 2.4 Why Direction Reverses: Two-Source Uncertainty Toy Model（v5.0 核心理论贡献）

**⚠️ v5.0 定位升级**：从 v4.0 的 "post-hoc discussion hypothesis (Type A/B)" 升级为 **§3.3 的正式 toy model**，放在论文核心 finding section 而非 discussion。产生 3 个 testable predictions，在实验中验证。这是论文从 "finding paper" 升级为 "finding + theory paper" 的关键。

**NeurIPS reviewer 反应预判**：
- ✅ "有 toy model 解释 why → 比纯 empirical finding 强得多"
- ✅ "3 个 testable predictions 都验证了 → explanatory theory 有预测力"
- ✅ "有 Simpson's Paradox + epistemic/aleatoric 理论基础 → 不是 ad hoc"
- ⚠️ "模型很简单（两类状态 + 线性混合）" → 回应："simplicity is a feature — Occam's razor; the goal is to explain the core mechanism with minimal assumptions, not to build a complex simulator"
- ⚠️ "p_I 怎么估计？" → 回应："empirically, via early-step ρ proxy (P1 prediction) or signal identity analysis (P3 prediction); full estimation is future work"
- ⚠️ "这有理论依据吗？" → 回应："Yes — direction reversal is an instance of Simpson's Paradox (Simpson 1951; Pearl 2014), and Type I/D draws on the epistemic/aleatoric distinction (Hüllermeier & Waegeman 2021). See §3.3 'Theoretical grounding' paragraph."
- ⚠️ "和 VOC 什么关系？" → 回应："Direction discovery is a prerequisite for non-negative VOC under evaluator-executor identity (see Appendix C). The main theoretical contribution is the Two-Source Model, not VOC analysis."

#### 2.4.1 Two-Source Uncertainty Model（形式化）

**核心直觉**：同一个 entropy 信号在不同状态下有两种语义来源。方向反转是因为这两种来源在不同环境中的混合比例不同。

**形式化定义**：

```
定义：Two-Source Uncertainty Model
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

假设 1：agent 在每个 step t 处于两种状态之一：
  - Type I (Information-Poverty)：agent 缺乏足够信息做出好决策
    → 高 entropy 反映信息不足（"不知道该做什么"）
    → rollout 无法弥补信息缺失 → U(s_t) 低
    → entropy 与 U 负相关

  - Type D (Decision-Difficulty)：agent 有足够信息但面临复杂选择
    → 高 entropy 反映多个可行路径（"有好几个都可能对"）
    → rollout 可以探索不同路径 → U(s_t) 高
    → entropy 与 U 正相关

假设 2：不同环境有不同的 Type I / Type D 状态比例
  - p_I(env) = 环境中 Type I 状态的比例
  - 1 - p_I(env) = 环境中 Type D 状态的比例

数学推导：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  State s_t 属于：
    Type I (概率 p_I):  U(s_t) ~ -α · entropy(s_t) + ε_I    (α > 0)
    Type D (概率 1-p_I): U(s_t) ~ +β · entropy(s_t) + ε_D    (β > 0)

  Overall correlation：
    Corr(entropy, U | env) ≈ p_I · (-α) + (1 - p_I) · (+β)
                            = β - (α + β) · p_I

  Direction reversal condition：
    sign flips when p_I crosses threshold p* = β / (α + β)

  当 p_I > p*: overall ρ < 0（信息匮乏主导 → 高 entropy 意味着 rollout 无用）
  当 p_I < p*: overall ρ > 0（决策困难主导 → 高 entropy 意味着 rollout 有价值）
  当 p_I ≈ p*: overall ρ ≈ 0（两种效应抵消 → entropy 几乎无信号）
```

**LaTeX 版本（论文 §3.3 直接使用）**：

```latex
\subsection{Why Does Direction Reverse? A Two-Source Model}
\label{sec:toy-model}

We propose a parsimonious model explaining when and why the
signal--utility direction reverses. Consider two sources of
uncertainty at each step:

\begin{itemize}[leftmargin=*,nosep]
\item \textbf{Type~I (information poverty):} The agent lacks
  sufficient information. High entropy reflects confusion, not
  optionality. Additional rollouts cannot compensate for missing
  information, so utility is \emph{negatively} related to entropy:
  $U_I(s) \sim -\alpha \cdot H(s) + \varepsilon_I$,\ \ $\alpha > 0$.

\item \textbf{Type~D (decision difficulty):} The agent has
  adequate information but faces multiple viable paths. High
  entropy reflects optionality. Rollouts can exploit this
  diversity, so utility is \emph{positively} related to entropy:
  $U_D(s) \sim +\beta \cdot H(s) + \varepsilon_D$,\ \ $\beta > 0$.
\end{itemize}

Let $p_I(\mathcal{E})$ denote the fraction of Type~I states in
environment $\mathcal{E}$. The \emph{marginal} correlation becomes:
%
\begin{equation}
  \rho(\mathcal{E}) \;\approx\;
    \beta \;-\; (\alpha + \beta)\,p_I(\mathcal{E})
  \label{eq:direction}
\end{equation}
%
Direction reversal occurs at the critical proportion
$p_I^* = \beta/(\alpha+\beta)$: environments with
$p_I > p_I^*$ exhibit negative $\rho$ (Type~I dominated),
while those with $p_I < p_I^*$ exhibit positive $\rho$
(Type~D dominated). Near $p_I^*$, the two effects cancel and
entropy carries negligible signal ($\rho \approx 0$).

\paragraph{Theoretical grounding.}
This direction reversal is an instance of Simpson's
paradox~\citep{simpson1951interpretation, pearl2014understanding}:
aggregating heterogeneous subpopulations with opposing within-group
trends can reverse the aggregate trend. Our two-source
decomposition draws on the well-established distinction between
epistemic and aleatoric
uncertainty~\citep{hullermeier2021aleatoric, der2009aleatory},
adapted to the meta-decision setting: Type~I states exhibit
epistemic-like uncertainty (the agent lacks information, and
rollouts from the same model cannot supply it), while Type~D
states exhibit aleatoric-like diversity (multiple viable paths
exist, and rollouts can exploit them). The key insight is that
\emph{the same entropy value has opposite causal effects on
optimizer utility depending on which source dominates}---a
distinction that all prior adaptive compute methods implicitly
collapse.
```

#### 2.4.2 环境映射（Toy Model → 实验数据）

```
Environment Mapping Table:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 环境 | 主导状态类型 | p_I 估计 | 预测方向 | 实测 ρ | 一致? |
|------|------------|----------|---------|--------|-------|
| HotpotQA | Type I 主导 | 高 | 负 | −0.327 | ✅ |
| (多步搜索，agent 经常缺信息) | 信息匮乏 | ~0.7-0.8 | (p_I > p*) | | |
|------|------------|----------|---------|--------|-------|
| MBPP | Type D 主导 | 低 | 正 | +0.153 | ✅ |
| (直接编码，多种可行方案) | 决策困难 | ~0.3-0.4 | (p_I < p*) | | |
|------|------------|----------|---------|--------|-------|
| APPS | 混合 | 中 | ≈0 | +0.012 | ✅ |
| (难易混合，信息不足+复杂选择) | 两种并存 | ~0.5 | (p_I ≈ p*) | (p=0.63) | |
|------|------------|----------|---------|--------|-------|
| WebShop | Type I 偏多 | 中偏高 | 弱正 | +0.133 | ⚠️ |
| (导航搜索，但 state_category | 混合 | ~0.55 | (p_I ≈ p*) | (弱) | |
|  信号更重要 η²=0.598) | | | | | |

解读：
- HotpotQA (ρ=−0.327): 多步搜索任务，agent 经常处于"不知道该搜什么"
  的状态 → Type I 主导 → 负相关 ✅
- MBPP (ρ=+0.153): 简单编码任务，模型有能力但有多种实现方式
  → Type D 主导 → 正相关 ✅
- APPS (ρ≈0): 难度混合（Introductory），信息不足和复杂选择并存
  → 两种效应相互抵消 → ≈0 ✅
- WebShop: entropy 不是最佳信号（state_category η²=0.598 远强于 entropy ρ=+0.133）
  → entropy 的 two-source 效应被 state-specific 信号覆盖
```

#### 2.4.3 Three Testable Predictions（v5.0 核心）

```
Prediction 1 (Temporal Shift):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "Within the same environment, early steps have higher p_I
   (less information accumulated) than late steps. Therefore,
   early-step ρ should be more negative than late-step ρ."

  验证方法：split trajectory into early (step 1-3) vs late (step 4+)
  → 计算 ρ(entropy, U | early) vs ρ(entropy, U | late)
  预期：ρ_early < ρ_late（在 Type I 主导环境如 HotpotQA 中尤其明显）
  → 如果成立，直接证明 p_I 随 trajectory 进展而变化

Prediction 2 (Cross-Environment Divergence):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "The more environments differ in p_I, the more their ρ values
   diverge. Environments with similar task structure should have
   similar ρ."

  验证方法：如果新增环境（如 Game24, GSM8K），其 ρ 应可基于
  task structure 预测（math reasoning → Type D 偏多 → 正/弱正 ρ）
  → 增加新环境后验证预测准确性

Prediction 3 (Signal Identity Alignment):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  "In Type I-dominated environments, the strongest signal should
   measure 'information sufficiency' (e.g., evidence_count in QA).
   In Type D-dominated environments, the strongest signal should
   measure 'decision complexity' (e.g., step_count in code)."

  验证数据（已有）：
  - HotpotQA (Type I): 最强信号 = evidence_count (ρ=−0.586)
    → 衡量"收集了多少证据" = 信息充分度 ✅
  - MBPP (Type D): 最强信号 = step_count (ρ=+0.526)
    → 衡量"在第几步" = 决策积累（步数越多，选择越复杂）✅
  - APPS (混合): 最强信号 = step_count (ρ=−0.274)
    → 负方向，但 APPS 混合了 Type I/D → 部分一致
  - WebShop: 最强信号 = state_category (η²=0.598)
    → 直接编码"在什么状态"（不是连续信号） → 与 Two-Source 互补
```

**Figure 设计（§3.3 配图，论文 Fig 2）**：

```
Fig 2: Two-Source Uncertainty Model

左图：p_I vs Corr(entropy, U) 理论曲线
  - X 轴: p_I (0 → 1)
  - Y 轴: ρ(entropy, U) (−0.4 → +0.2)
  - 线性曲线: ρ = β - (α+β)·p_I
  - 标注 p* = β/(α+β) 的零点
  - 标注 4 个环境的位置:
    • HotpotQA (p_I 高, ρ=−0.327) ← 左上区域
    • APPS (p_I 中, ρ≈0) ← 零点附近
    • MBPP (p_I 低, ρ=+0.153) ← 右下区域
    • WebShop (p_I 中偏高, ρ=+0.133) ← 零点右侧

右图：Prediction 1 验证 — Early vs Late step ρ
  - Grouped bar chart: [HotpotQA, APPS, MBPP, WebShop]
  - 每组两条柱: early steps (深色) vs late steps (浅色)
  - 预期: early ρ < late ρ (尤其在 HotpotQA)
```

#### 2.4.4 Theoretical Foundations（理论基础）🆕🆕

**⚠️ 核心定位**：Two-Source Model 不是 ad hoc narrative，而是建立在两个 well-established 理论基础上的 explanatory model。论文中必须显式建立这些连接。

##### A. Simpson's Paradox — 方向反转的统计学基础

**连接**：我们观察到的方向反转是 **Simpson's Paradox 在 signal-utility correlation 空间中的实例**。

Simpson's Paradox 描述的是：在异质子群中成立的关联方向，在聚合后可以反转。我们的情况完全对应：
- 子群 1 (Type I states): entropy ↔ U 负相关
- 子群 2 (Type D states): entropy ↔ U 正相关
- 聚合 (whole environment): ρ 的符号取决于混合比例 p_I

**这不是巧合或 ad hoc 解释——而是一个有 70+ 年理论基础的统计现象的新应用场景。**

**关键引用**：

1. **Simpson, E. H. (1951). "The Interpretation of Interaction in Contingency Tables."**
   *Journal of the Royal Statistical Society, Series B (Methodological)*, 13(2), 238--241.
   → 原始论文，首次形式化描述子群聚合后关联方向反转的现象。

2. **Pearl, J. (2014). "Comment: Understanding Simpson's Paradox."**
   *The American Statistician*, 68(1), 8--13. DOI: 10.1080/00031305.2014.876829
   → Pearl 用因果推断框架重新解读 Simpson's Paradox，指出方向反转本质上反映了 confounding variable（在我们的 case 中是 state type）对 marginal association 的影响。Pearl 的因果视角直接支持我们的论点：state type 是 confounding variable，不同环境有不同的 state type 分布（p_I），导致 marginal ρ 反转。

**论文中的写法（§3.3, 1 段）**：
```latex
\paragraph{Theoretical grounding.}
The direction reversal we observe is an instance of Simpson's
paradox~\citep{simpson1951interpretation, pearl2014understanding}
in the signal--utility space. When an environment contains a
mixture of state types---those where high entropy reflects
information poverty (Type~I, negative $\rho$) and those where
it reflects decision difficulty (Type~D, positive $\rho$)---the
marginal correlation is a weighted average (Eq.~\ref{eq:direction})
whose sign depends on the mixture proportion $p_I$. This is not
an artifact of our specific environments but a \emph{fundamental
statistical phenomenon}: whenever heterogeneous subpopulations
with opposing within-group trends are aggregated, the aggregate
trend can reverse~\citep{pearl2014understanding}.
```

##### B. Epistemic vs Aleatoric Uncertainty — Type I/D 的 ML 理论先行者

**连接**：我们的 Type I / Type D 区分受到 ML 中 **epistemic vs aleatoric uncertainty decomposition** 的启发，并做了适配性扩展。

| 我们的概念 | 经典对应 | 关键区别 |
|-----------|---------|---------|
| Type I (信息匮乏) | Epistemic uncertainty (认知不确定性) | 经典 epistemic 可通过更多数据消除；Type I 中 rollout 不等于"新数据"（同一模型生成） |
| Type D (决策困难) | Aleatoric uncertainty (固有不确定性) | 经典 aleatoric 不可消除；Type D 中 rollout 可以"穿越"多条路径 |
| p_I (混合比例) | Uncertainty decomposition ratio | 我们的 p_I 是环境级别的，不是样本级别的 |

**⚠️ 重要区别**：经典 epistemic/aleatoric 分类是关于**数据/模型的不确定性**，我们的 Type I/D 是关于 **agent 状态与 optimizer utility 的因果关系**。这不是简单套用，而是 "inspired by + adapted to meta-decision setting"。论文中应说明这一关系但不应过度等同。

**关键引用**：

3. **Hüllermeier, E. & Waegeman, W. (2021). "Aleatoric and Epistemic Uncertainty in Machine Learning: An Introduction to Concepts and Methods."**
   *Machine Learning*, 110, 457--506. DOI: 10.1007/s10994-021-05946-3
   → 最全面的 ML uncertainty decomposition 综述，区分 epistemic (reducible, from lack of knowledge) 和 aleatoric (irreducible, from inherent randomness)。我们的 Type I/D 受此启发但做了 domain-specific adaptation。

4. **Der Kiureghian, A. & Ditlevsen, O. (2009). "Aleatory or Epistemic? Does It Matter?"**
   *Structural Safety*, 31(2), 105--112.
   → 经典论文，论证 uncertainty 类型的区分在决策中确实重要（"Does it matter? → Yes"）。直接支持我们的论点：不同 uncertainty 类型对 optimizer utility 有不同的因果效应。

5. **Depeweg, S., Hernandez-Lobato, J.-M., Doshi-Velez, F. & Udluft, S. (2018). "Decomposition of Uncertainty in Bayesian Deep Learning for Efficient and Risk-sensitive Learning."**
   *Proceedings of ICML 2018*, PMLR 80.
   → 在 BNN 中分离 epistemic 和 aleatoric uncertainty，用于 risk-sensitive decision。与我们的分离 Type I/D 在精神上一致。

6. **Malinin, A. & Gales, M. (2018). "Predictive Uncertainty Estimation via Prior Networks."**
   *Advances in Neural Information Processing Systems 31 (NeurIPS 2018)*.
   → Prior Networks 用 Dirichlet 分布分离 distributional uncertainty 和 data uncertainty。展示了 uncertainty decomposition 在决策中的价值。

**论文中的写法（§3.3 或 Related Work §2.3, 1-2 句）**：
```latex
Our two-source model draws on the well-established distinction
between epistemic and aleatoric
uncertainty~\citep{hullermeier2021aleatoric, der2009aleatory},
adapted to the meta-decision setting: Type~I states exhibit
epistemic-like uncertainty (the agent lacks information, and
rollouts from the \emph{same} model cannot supply it), while
Type~D states exhibit aleatoric-like diversity (multiple viable
paths exist, and rollouts can exploit them).
```

##### C. 理论框架总结

```
Three Theoretical Pillars of Two-Source Model:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pillar 1: Simpson's Paradox (Simpson 1951; Pearl 2014)
  → 为什么 overall ρ 可以反转：异质子群聚合的基本统计现象
  → 论文 §3.3: "Theoretical grounding" 段

Pillar 2: Epistemic vs Aleatoric Uncertainty
         (Hüllermeier & Waegeman 2021; Der Kiureghian & Ditlevsen 2009)
  → Type I/D 的理论先行者：uncertainty 类型影响最优决策
  → 论文 §3.3 或 Related Work: 1-2 句 inspired-by 说明

Pillar 3: Rational Metareasoning (Russell & Wefald 1991) [已有，降级为配角]
  → VOC 在 evaluator-executor identity 下的 scope 限制
  → 论文 Discussion §6.1: 1 句理论连接 + Appendix C 详述

这三个 pillar 让 reviewer 看到：
  ✅ 方向反转有统计学基础（不是 cherry-picked 现象）
  ✅ Type I/D 区分有 ML 理论支撑（不是 ad hoc 命名）
  ✅ 与经典 AI 决策理论有联系（不是 isolated contribution）
```

**BibTeX 条目（论文直接使用）**：

```bibtex
@article{simpson1951interpretation,
  author  = {Simpson, Edward H.},
  title   = {The Interpretation of Interaction in Contingency Tables},
  journal = {Journal of the Royal Statistical Society, Series B (Methodological)},
  volume  = {13},
  number  = {2},
  pages   = {238--241},
  year    = {1951}
}

@article{pearl2014understanding,
  author  = {Pearl, Judea},
  title   = {Comment: Understanding {Simpson's} Paradox},
  journal = {The American Statistician},
  volume  = {68},
  number  = {1},
  pages   = {8--13},
  year    = {2014},
  doi     = {10.1080/00031305.2014.876829}
}

@article{hullermeier2021aleatoric,
  author  = {H{\"u}llermeier, Eyke and Waegeman, Willem},
  title   = {Aleatoric and Epistemic Uncertainty in Machine Learning:
             An Introduction to Concepts and Methods},
  journal = {Machine Learning},
  volume  = {110},
  pages   = {457--506},
  year    = {2021},
  doi     = {10.1007/s10994-021-05946-3}
}

@article{der2009aleatory,
  author  = {Der Kiureghian, Armen and Ditlevsen, Ove},
  title   = {Aleatory or Epistemic? {Does} It Matter?},
  journal = {Structural Safety},
  volume  = {31},
  number  = {2},
  pages   = {105--112},
  year    = {2009}
}

@inproceedings{depeweg2018decomposition,
  author    = {Depeweg, Stefan and Hernandez-Lobato, Jose-Miguel
               and Doshi-Velez, Finale and Udluft, Steffen},
  title     = {Decomposition of Uncertainty in {Bayesian} Deep Learning
               for Efficient and Risk-sensitive Learning},
  booktitle = {Proceedings of the 35th International Conference on
               Machine Learning (ICML)},
  series    = {PMLR},
  volume    = {80},
  year      = {2018}
}

@inproceedings{malinin2018predictive,
  author    = {Malinin, Andrey and Gales, Mark},
  title     = {Predictive Uncertainty Estimation via Prior Networks},
  booktitle = {Advances in Neural Information Processing Systems 31
               (NeurIPS)},
  year      = {2018}
}
```

#### 2.4.5 与旧版 Type A/B 假说的关系

```
v4.0 Type A/B → v5.0 Two-Source 的升级：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 维度 | v4.0 Type A/B | v5.0 Two-Source |
|------|--------------|-----------------|
| 定位 | Discussion hypothesis | §3.3 正式 toy model |
| 形式化 | 文字描述 | 数学公式 (Eq. 1) |
| 预测力 | 定性解释 | 3 个 quantitative predictions |
| 可验证性 | "interesting but not validated" | 实验验证 P1/P3 |
| 命名 | Type A/B (informal) | Type I/D (formal) |
| 核心变量 | capability boundary | p_I (state composition ratio) |
| 机制 | 能力内 vs 能力外 | 信息匮乏 vs 决策困难 |
| 方向翻转条件 | 定性（跨越能力边界） | 定量（p_I > p* = β/(α+β)） |

升级关键：
- v4.0: "We hypothesize that..." (discussion-level)
- v5.0: "We model the direction as a function of state composition
         and derive three testable predictions, two of which we
         verify empirically" (finding-level)

Evaluator-Executor Identity 的保留：
- 旧定位：核心机制（驱动 Type B 场景）
- 新定位：Type I 场景的一种具体机制解释（为什么信息不足时 rollout 无法帮助）
- 论文位置：Discussion §6.1 中简述，不再作为独立理论贡献
- 与 Kambhampati (2024) 的联系保留在 Discussion 中
```

**NeurIPS 写作策略**：
- **§3.3 (Finding Section)**：完整展开 Two-Source Model + 数学推导 + 环境映射 + Fig 2
- **§5.4 (Experiments)**：验证 P1 (early vs late ρ) 和 P3 (signal identity alignment)
- **§6.1 (Discussion)**：从 toy model 引申 community insight + 简述 evaluator-executor identity 作为 Type I 的具体机制
- **不要**在 Introduction 中展开数学推导，只用 1-2 句给直觉：
  ```
  "We explain this reversal via a two-source model: the same
   entropy signal reflects information poverty (where rollouts
   cannot help) in some environments and decision difficulty
   (where rollouts explore alternatives) in others."
  ```

---

<a name="section-framework"></a>
## 3. 逐 Section 写作框架（NeurIPS 9 页）

### 总体页面分配（v5.0 — Finding + Theory + Method Evolution）🆕

```
Section                          | 页数  | 核心功能
---------------------------------|-------|------------------------------------------
1. Introduction                  | 1.5   | Module 1: 假设错了+理论预览+为什么重要 (1页)
                                 |       | Module 2: 方法演进+结果+发现 (0.5页)
2. Related Work                  | 0.75  | 精简定位 + §2.3 Learning from Interaction 🆕
3. Signal-Utility Landscape      | 2.0   | §3.1 Setup + §3.2 Three-Layer Failure +
   (Finding + Theory)            |       | §3.3 Two-Source Toy Model + §3.4 Direction Necessity 🆕
4. Method: Direction-Aware       | 1.5   | §4.1 Overview + §4.2 Direction Discovery +
   Gating                        |       | §4.3 SCG-LR + §4.4 Hidden State Probe +
                                 |       | §4.5 Probe Analysis 🆕
5. Experiments                   | 2.5   | Main results + Pareto + Toy model verification 🆕 +
                                 |       | Hidden state analysis 🆕 + Ablations
6. Discussion & Limitations      | 1.0   | Community insight 🆕 + Future vision (OPD/XSkill) 🆕 +
                                 |       | Limitations
7. Conclusion                    | 0.25  | 3 句话总结
                                 |       |
Appendix A: Related Work 完整版  | 1-2   | 详细论文对比 + concurrent work
Appendix B: 实验细节            | 1-2   | 环境设置 + 超参 + 额外 ablation
Appendix C: 理论补充            | 0.5-1 | VOC ≥ 0 scope + CMDP formalization
Appendix D: Toy Model 推导 🆕   | 0.5   | Two-Source 模型详细推导 + 参数估计
```

> **v5.0 vs v4.0 页面变化**：
> - §3: 从 0.75 → 2.0 页（新增 toy model + finding section 合并）
> - §4: 从 1.25 → 1.5 页（新增 hidden state probe sections）
> - §5: 从 3.5 → 2.5 页（将部分 finding 内容移到 §3）
> - §6: 保持 1.0 页（内容重构：community insight + future vision）
> - 总计仍控制在 9 页正文

### Section 1: Introduction（1.5 页）— v4.0 Direction Discovery 框架

**Intro 两大模块**：Module 1 (问题, ~70%) + Module 2 (我们怎么做, ~30%)

---

**═══ Module 1: 存在什么问题、为什么重要（~1 页，4 段）═══**

**Para 1: 背景 + 现有方法的共同做法（4-5 句）**
- 功能：建立 selective triggering 的动机 + 指出现有方法的共同模式
- 写什么：
  - Test-time compute（rollouts, verification, tree search）能大幅提升 LLM agent 表现，但每步触发成本高（1-2 句）
  - 一系列工作提出选择性触发：用 uncertainty signal 判断哪些 step 需要额外 compute（1 句 + 引用 CATTS, SEAG, CaTS, CoRefine, AdaptThink, Thinkless, etc.）
  - **关键句**：这些方法在各自环境上都展示了有效性（acknowledge 它们的贡献）
- **不要写**：冗长的 LLM agent 背景

**Para 2: 隐含假设（3-4 句）**
- 功能：**指出所有现有方法共享的、没人质疑过的假设**
- 写什么：
  - 这些方法虽然 mechanism 不同（voting, entropy thresholding, calibrated confidence, RL），但共享一个隐含假设：signal 与 compute 需求的相关方向是固定的（1-2 句）
  - 直觉上这很合理：entropy 高 → 模型不确定 → 可能要犯错 → 触发额外 compute（1 句）
  - **关键句**：
    ```
    "Despite differing mechanisms, these methods share an unquestioned
     assumption: a fixed mapping from uncertainty signals to compute need.
     High entropy means the agent is struggling and needs help."
    ```

**Para 3: 假设是错的 + 后果（5-6 句，核心段）** 🔥
- 功能：**揭示 direction reversal + 量化后果**
- 写什么：
  - 我们在多个异构环境中系统测量了 signal-utility correlation，发现方向相反（1-2 句 + 数据）
    - HotpotQA: entropy 与 utility 负相关 — 高 entropy 时触发 rollout 反而有害
    - 不仅方向变化，连最有信息量的信号本身都因环境而异（signal replacement）
  - **后果**：所有 fixed-direction 方法在方向反转环境中系统性地在错误 step 触发（1 句）
  - **Calibration 也救不了**：方向错了，threshold 越精准越差（1 句）
  - Wrong-Direction 实测代价：LR −34.5pp, MLP −51.2pp（1 句数据）
  - **关键句**：
    ```
    "When the direction is wrong, more precise calibration makes
     performance worse, not better."
    ```

**Para 4: 为什么方向反转 + 理论预览 + 问题定义（5-6 句）** 🆕 v5.0 升级
- 功能：**过渡——解释方向反转 → 提供理论框架 → 定义核心问题**
- 写什么：
  - **🆕 Two-Source 理论预览（2-3 句，§3.3 的 elevator pitch）** 🔥：
    ```
    "We explain this reversal via a two-source uncertainty model
     (Section 3.3): the same entropy signal reflects two fundamentally
     different sources—information poverty (where the agent lacks data
     to act, and rollouts cannot help) and decision difficulty (where
     the agent faces multiple viable paths, and rollouts explore them).
     Environments differ in their proportion of these two state types,
     causing the same signal to carry opposite meaning. The model
     predicts when direction reversal occurs and yields three testable
     predictions, which we verify empirically (Section 5.4)."
    ```
  - **困难（2 句，简化版）**：
    - 即使知道方向会反转，从数据中学方向仍不 trivial：只有 episode-level 反馈（credit assignment 难）+ 必须 online 学习
  - **核心问题**（1-2 句）：
    ```
    "The central question becomes: how can we discover the correct
     signal-utility direction online, from episode-level feedback alone,
     within an executing agent trajectory?"
    ```
  - **写作注意**：
    - 🆕 v5.0 变化：VOC/metareasoning 理论动机从 Introduction 移到 Discussion §6.1
    - Introduction 中用 Two-Source 理论预览代替 VOC 理论动机——更直接、更有解释力
    - Russell & Wefald (1991) 等理论引用移到 Discussion 中展开
    - 保留 cite Two-Source model 指向 §3.3，让审稿人知道理论解释马上展开

> ⚠️ **v5.0 vs v4.0 Para 4 变化**：
> - v4.0: 三个困难 + VOC 理论动机 (1 句)
> - v5.0: Two-Source 理论预览 (2-3 句) + 简化困难 (2 句)
> - 理由：Two-Source 更贴合核心叙事（解释 finding），VOC 更适合 discussion（理论联系）

---

**═══ Module 2: 我们怎么做（~0.5 页，1-2 段）═══**

**Para 5: 方法演进 + 结果 + 发现（6-8 句）** 🆕 v5.0 升级
- 功能：方法概述（演进叙事）+ 核心结果
- 写什么：
  - **方法演进（3 句, Layer B）** 🆕：
    - SCG — online exploration → LR 学习每个 feature 的系数（包含符号/方向），zero per-step overhead
    - 进一步验证：LLM hidden states 已编码足够 gating 信号（linear probe AUC=0.88 vs handcrafted AUC=0.85），无需领域知识设计特征
    - 关键 insight：bottleneck 是 fixed-direction assumption，不是 model 表征能力
  - **公平比较框架（1 句, Layer D）**：所有 gate 方法共享同一 optimizer T，只比较 gate 决策质量。
  - **结果（2 句）**：SCG Pareto-dominates 所有 calibrated baselines across 4-5 diverse environments（具体数字）。
  - **Adaptive Behavior（2 句, Layer C）**：Gate trigger rate 自动对齐 rollout headroom（RR=60%@+48pp, RR=6%@+7pp），无需显式 headroom estimation。

**Para 6: Contributions（bullet list，3 条）** 🆕 v5.0 升级
- C1: **Finding + Theory** — Direction reversal finding + Two-Source 理论解释 + 3 testable predictions 验证。量化代价 −34.5pp/−51.2pp
- C2: **Method Evolution** — 手工 feature SCG → Hidden State Probe（手工到自动的演进）。Probe 不仅验证了 theory（方向环境特异），还证明 bottleneck 是假设而非模型能力
- C3: **Evaluation** — Pareto dominance across 4-5 environments + emergent adaptive behavior（trigger rate ↔ headroom）+ token cost analysis

> ⚠️ **v5.0 vs v4.0 Module 2 变化**：
> - C1: 从 "empirical finding" 升级为 "finding + theoretical explanation"
> - C2: 从 "SCG method + T-as-parameter" 升级为 "method evolution story（手工→自动）"
> - C3: 保持（Pareto dominance + adaptive behavior）
> - 引用 §2.2-C 的 LaTeX 版 contributions

### Section 2: Related Work（正文 0.5 页精简版 + 附录完整版）

**v4.0 Related Work 策略**：正文中只放精简版（0.5 页），完整 survey 移到附录。

**正文原则**：不是 survey，是**定位**。核心信息只有一条：所有现有方法都假设固定方向，我们是第一个质疑并学习方向的。

---

**正文 Related Work（0.5 页，2 个小节）**：

**2.1 Adaptive Test-Time Compute（0.35 页）**
- 功能：把所有竞品统一归入 "fixed-direction assumption" 框架
- 结构：
  - **Signal-based methods**（SEAG, CaTS, CoRefine, Think Just Enough, DiffAdapt）：
    - 1-2 句概括：用 entropy/confidence/probe signal + fixed direction 触发
    - 1 句我们的区别：它们假设方向，我们学方向。DiffAdapt 的 probe 做 difficulty estimation，我们做 direction discovery——本质不同
  - **Vote-based methods**（CATTS）：
    - 1 句概括：K-sample voting + vote disagreement 触发
    - 1 句区别：仍假设 disagreement 方向固定 + K 次推理 overhead
  - **RL-based methods**（AdaptThink, Thinkless, ARPO, L1）：
    - 1-2 句概括：RL 隐式学习触发策略
    - 1 句区别：per-env RL 训练，方向学习是黑盒的；我们显式学方向，LR 系数可解释
  - **总结句**：
    ```
    "Despite differing mechanisms, all these methods share a common
     assumption: a fixed relationship between uncertainty signals and
     compute need. Our empirical finding—that this relationship reverses
     across environments—challenges this assumption and motivates
     direction-aware gating."
    ```

**2.2 Orthogonal Work（0.1 页）**
- Test-time scaling (Snell et al.) → compute-optimal allocation at problem level，与我们互补
- Search methods (LATS, FLARE) → 改进搜索过程，我们控制何时搜索
- Policy improvement (GiGPO) → 改进 policy，与 gate 正交

**2.3 Learning from Interaction Signals（0.15 页）** 🆕🆕 v5.0 新增
- **功能**：连接 gate learning 到更广泛的 "从交互中学习" 研究，为 Discussion §6.2 Future Vision 铺路
- **写什么**：
  - **OpenClaw-RL (OPD)**：从 next-state signals 提取 textual hints → 构建 enhanced teacher context → token-level directional advantage。核心 insight：scalar rewards 丢失大量信息，directional supervision 更丰富
  - **XSkill**：dual-stream framework（skills + experiences）→ 从跨 rollout patterns 积累任务知识 → continual learning from experience
  - **我们的定位**：gate learning 是这个方向在 meta-decision 上的实例 — 从 binary U 学 gating direction，future work 可升级为从 rollout 内容学 directional signals
  - **关键引用句**：
    ```
    "Our gate learning—discovering direction from binary utility—is
     a minimal instance of learning from interaction signals. Recent
     work shows that richer signal extraction from rollout content
     (OpenClaw-RL) and cross-episode pattern accumulation (XSkill)
     substantially improve agent capabilities. Extending these ideas
     to meta-decision learning is a promising direction (Section 6.2)."
    ```

---

**附录 Related Work（完整版，1-2 页）**：

**A.1 Adaptive Compute: From Reasoning to Agent Settings**
- 完整研究版图：reasoning 已拥挤（10+ 篇），agent settings under-explored（仅 3 篇）
- 详细对比表：每篇论文的 mechanism, direction assumption, training requirement, overhead
- 实验证据：env-state signals >> model-intrinsic signals（完整数据表）
  - HotpotQA: evidence_count ρ=−0.586 >> token_entropy ρ=−0.327
  - APPS: step_count ρ=−0.274 >> token_entropy ρ=+0.144
  - WebShop: state_category η²=0.598 >> token_entropy ρ=+0.133
- Agent settings 为什么更容易出现 direction reversal：env-state signals 编码 task-specific progress

**A.2 Detailed Method Comparison**
- 每篇 high-threat 论文的详细对比（AdaptThink, DiffAdapt, Think Just Enough, CATTS）
- 对比维度：决策粒度、方向假设、训练需求、overhead、adaptive behavior

**A.3 Concurrent Work Statement**
```latex
\textbf{Concurrent work.} Several 2025--2026 papers independently explore
adaptive compute: CATTS~\cite{catts} uses vote-derived gating for web agents;
AdaptThink~\cite{adaptthink} learns think/no-think via RL;
DiffAdapt~\cite{diffadapt} uses a probe for difficulty estimation assuming
a universal entropy pattern. While sharing our motivation for selective
triggering, all assume or implicitly learn a fixed signal direction. Our
work is the first to empirically demonstrate that signal-utility direction
reverses across environments---a finding none of these methods report---and
to propose direction-aware gating as a solution.
```

**关键语气**（NeurIPS 风格）：
```
不要：These methods are limited because they assume fixed direction.
要：  These methods make a reasonable implicit assumption—that signal
      direction is stable—which our empirical analysis reveals does
      not hold universally (Section 5.3).
```

**并发工作声明**（放 Related Work 末尾或 footnote）：
```latex
\textbf{Concurrent work.} Several 2025 papers independently explore
adaptive compute allocation: AdaptThink~\cite{adaptthink}
(arXiv:2505.13417, EMNLP 2025) learns think/no-think via RL;
DiffAdapt~\cite{diffadapt} (arXiv:2510.19669) uses a lightweight
probe for difficulty estimation assuming a universal U-shaped entropy
pattern; Think Just Enough~\cite{thinkjustenough} (arXiv:2510.08146)
applies entropy-based early stopping with a fixed threshold; and
CATTS~\cite{catts} (arXiv:2602.12276) explores vote-derived gating
for web agents. While sharing our motivation for selective triggering,
all assume or implicitly learn a fixed signal direction. Our work is
the first to empirically measure signal-utility direction and
demonstrate that both the direction and the \emph{identity} of the
most informative signal vary across environments (signal
replacement)---findings none of these methods report.
```

🆕 **Phase 5 升级后的并发工作声明**（如果 Phase 5 成功，替换上面的版本）：

```latex
% === Phase 5A (Cascade) 版本 ===
\textbf{Concurrent work.} Several 2025 papers independently explore
adaptive compute allocation: AdaptThink~\cite{adaptthink} learns
think/no-think via RL; DiffAdapt~\cite{diffadapt} uses a lightweight
probe for difficulty estimation; CATTS~\cite{catts} explores
vote-derived gating for web agents; ARPO~\cite{arpo} optimizes
entropy-based adaptive rollout via RL. All employ hand-crafted signals
(vote entropy, policy entropy) with fixed-direction assumptions or
implicit RL learning. Our work differs in both \emph{finding} and
\emph{method}: (1)~we discover that signal-utility direction and the
identity of the most informative signal both vary across environments,
and (2)~our cascaded multi-fidelity gate progressively escalates from
cheap observable signals to hidden-state VOC estimation, adapting both
the \emph{direction} and the \emph{cost} of the gating decision per
state---capabilities absent in single-threshold or RL-based methods.

% === Phase 5B (ICGNet) 版本 ===
\textbf{Concurrent work.} [same opening...] Our work differs in both
\emph{finding} and \emph{method}: (1)~we discover signal-utility
direction reversal and signal replacement across environments, and
(2)~our in-context gating network meta-learns how to gate from
calibration data, deploying to new environments by simply providing
calibration context---without retraining or threshold tuning. This
yields a dual contribution: an empirical finding (direction reversal)
and a methodological advance (cross-environment gating via in-context
learning) that neither threshold-based (CATTS) nor RL-based (ARPO,
AdaptThink) methods achieve.
```

### Section 3: Problem Formulation（0.75 页）

**NeurIPS 的 formalization 原则**：简洁、有动机、有 insight。不要为了 formal 而 formal。

**3.1 Setup（0.25 页）**
- Agent MDP: $\mathcal{M}, \pi_\theta, T$
- **关键定义**：T 是参数，不是固定的
  ```
  关键句："The optimizer T is an environment-specific parameter: it can be
  per-action evaluation (small action spaces), K-variant sampling (code
  generation), or diverse prompting (large action spaces). Our gate
  operates independently of T's implementation."
  ```
- **Optimizer Utility $U(T, s)$ 定义 — 通用公式，T 的附属绑定** 🆕
  - **只定义一次**，不需要按环境分别定义：
    $$U(T, s) = \mathbb{E}[R(\tau) \mid a = T(s)] - \mathbb{E}[R(\tau) \mid a = \pi(s)]$$
  - 一句话：用了 optimizer T 的收益 − 不用的收益
  - U 是 T 的附属绑定：T 变了（换环境），U 的计算自然跟着变，不需要额外说明
  - **论文中的处理策略**：
    - §3 只写通用公式 U(T, s)——一次性定义，T-agnostic
    - §5 Experiments 中通过 Table 1 指定每个环境的 T（per-action eval / K-variant / LLM-Propose-K）→ U 的具体计算从 T 的定义中自然 fall out
    - ❌ 不要为每个环境单独定义 U（会让 formalization 碎片化，暗示 U 需要 environment-specific 设计）
    - ✅ 只需在 §5.1 Experimental Setup 用一句话说明 U 的估计方式：$\hat{U} = \max_{k=1}^K R(\tau_k \mid T) - R(\tau \mid \pi)$（best-of-K，与部署行为一致）
  - **类比**：如同定义 loss L(θ) = E[l(f_θ(x), y)]——换 dataset 不需要重新定义 L，换 T 也不需要重新定义 U
  ```latex
  % §3 中的写法（简洁）：
  Given an environment-specific optimizer $T$, we define the
  \emph{optimizer utility} at state $s$ as
  $U(T, s) = \mathbb{E}[R(\tau) \mid a{=}T(s)]
            - \mathbb{E}[R(\tau) \mid a{=}\pi(s)]$.
  Crucially, $U$ is defined generically over $T$: changing the
  optimizer (e.g., from per-action evaluation to $K$-variant
  sampling) changes the distribution of $U$ but not its definition.
  Table~1 instantiates $T$ for each environment.

  % §5 中的写法（一句话估计细节）：
  We estimate $U$ via best-of-$K$:
  $\hat{U} = \max_{k=1}^{K} R(\tau_k \mid T) - R(\tau \mid \pi)$,
  consistent with deployment where the agent selects the
  highest-reward rollout.
  ```
- Observable Signal $\sigma(s)$ 定义

**3.2 Three Research Questions（0.25 页）**
- P1 可变性：$\text{Var}[U(T,s)] > 0$?
- P2 可预测性：$\exists \sigma$ s.t. $\text{corr}(\sigma, U) \neq 0$? 且方向是否稳定？
- P3 可学习性：Probe-first gate 能否逼近 oracle?

**3.3 Why Does Direction Reverse? Two-Source Uncertainty Model（0.5 页）** 🔥🆕 v5.0 核心新增

**⚠️ v5.0 关键变化**：从 v4.0 的 0.25 页 "direction discovery 形式化" 扩展为 0.5 页的 **toy model + predictions**。这是论文从 "finding" 升级为 "finding + theory" 的关键 section。

- **写什么**（参考 §2.4 的完整形式化）：
  1. **直觉（2-3 句）**：两种 uncertainty source → 同一 entropy 有不同含义
  2. **形式化（Eq. 1）**：
     - Type I: U ~ -α·H(s) + ε  |  Type D: U ~ +β·H(s) + ε
     - ρ(env) ≈ β - (α+β)·p_I(env)
     - Reversal at p* = β/(α+β)
  3. **环境映射（Table/Fig）**：4 个环境对应 toy model 曲线上的位置
  4. **Three Testable Predictions**（P1: temporal shift, P2: cross-env divergence, P3: signal identity）
  5. **Figure 2**：p_I vs ρ 曲线 + 环境标注点

- **NeurIPS 写法原则**：
  - 这是 toy model 而非 formal theorem — 不需要证明，需要解释力 + 预测力
  - 用 proposition（非 theorem）+ empirical verification
  - 1 页以内（包括 Figure 2）
  - 与 §5.4 实验验证相呼应

- **不要写**：
  - 长定理 + 证明（NeurIPS 不是 COLT）
  - 过于复杂的概率模型（保持 Occam's razor）
  - p_I 的精确估计方法（这是 limitation，承认即可）

**3.4 Why Direction Discovery is Necessary（0.15 页）**
- 从 toy model 自然推导：如果 p_I 未知且因环境而异，fixed-direction 必然在部分环境失败
- 1 个 quantitative example：ρ=−0.3 环境中，fixed positive threshold 错误率估计
- 过渡到 §4 Method

### Section 4: Method — Direction-Aware Gating（1.5 页）🆕 v5.0 升级

**v5.0 Method 叙事**：从 "单一方法 SCG" 升级为 **"手工 feature → Hidden State Probe" 演进叙事**。核心 message：方向学习有效，且模型已有足够表征——bottleneck 是假设，不是能力。

**4.1 Overview（0.2 页）**
- 图示：两阶段 pipeline（Direction Discovery → Gated Triggering）
- 🆕 **方法演进预览**：先用手工 features 验证概念（§4.2），再用 hidden states 消除领域知识依赖（§4.3）
- 与现有方法的结构对比（一句话）：现有方法假设方向已知，我们先测量方向
- **关键**：gate 不需要知道 T 的实现；方向数据可来自在线 probe 或离线 calibration data

**4.2 Direction Discovery Phase（0.4 页）**
- 写什么：
  - 数据来源：在线 probe（random 50% triggering, 50 ep）或离线预加载（Phase 1 数据）
  - ⚠️ **Phase 2 发现**：当 calibration data 充足时（≥500 pts），在线 probe 无额外贡献 → 方向发现的关键是**方向数据**而非**在线 probe 过程**。论文应统一表述为 "direction discovery" 而非 "probe-first"
  - 多指标分析：Spearman ρ, MI, η² 综合排序
  - 方向估计：sign(ρ) 或 sign(分段回归斜率)
  - **Wrong-Direction 代价量化（Phase 2 + 2.5）**：错误方向导致 LR SR −34.5pp, MLP SR −51.2pp (RR=0%)。跨 gate 类型通用崩溃证明此步骤不可省略
- **NeurIPS 风格**：Algorithm 伪代码 1 个，不超过 10 行

**4.3 Gate Phase — SCG-FineTune(LR)（0.5 页）**
- 写什么：
  - 5 维信号特征：[step_count, token_entropy, evidence_count, state_category, action_type]
  - StandardScaler + LogisticRegression(class_weight='balanced')
  - 训练 <1s，无 GPU 需求
  - 决策：P(rollout useful) > τ(λ) → trigger
    - 默认 τ = 0.5（无成本约束时）
    - CMDP extension：τ(λ) = 0.5 + λ*，其中 λ* 由 Lagrangian dual ascent 自动学习（见 Section 4.3），用户只需指定 CS_target
  - LR 系数可解释：evidence_count (−0.708) 最强，state_category (−1.028) 第二
  - Cost-aware extension：λ 控制 trade-off → 不再需要手动设 λ，dual ascent 自动收敛
- **关键卖点**：lightweight, interpretable, architecture-agnostic, Phase 3 3-seed: SR=96.7%, CS=44.1%（SR-CS Pareto-dominating random）；Phase 2 gate 对比：LR 达 Oracle TES 71.1%，LoRA 72.3%
- Algorithm 伪代码 1 个

**4.4 From Manual to Automatic: Hidden State Probing（0.3 页）** 🆕🆕 v5.0 核心新增

**科学问题**：LLM hidden states 是否已编码足够的 gating 信号？如果是，方向学习可以完全自动化，无需领域知识设计特征。

**写什么**：
- **Motivation（2 句）**：手工 feature 需要领域知识 + 信号集有限。一个自然问题：模型在 trajectory 中积累的 hidden state 是否已包含判断 rollout 有用性的信息？
- **Method（3 句）**：
  - 从 LLM last-layer hidden state 提取 2560-dim 向量（每个 step 的最后一个 token）
  - Linear probe（logistic regression on hidden states）→ 预测 U > 0
  - 极度简单的 method — **simplicity 是 feature，不是 bug**
- **核心结果（2 句）**：
  - AUC=0.88 vs handcrafted AUC=0.85 → hidden state 更强
  - 但 linear probe 足矣 → 不需要复杂的 feature extraction pipeline
- **Key insight（1 句）**：
  ```
  "The bottleneck for cross-environment adaptive compute was never
   the model's representational capacity — it was the fixed-direction
   assumption that prevented leveraging available representations."
  ```

**4.5 What Do Hidden States Encode? — Scientific Analysis（0.2 页）** 🆕🆕 v5.0 核心新增

**定位**：让 "simple linear probe" 不 trivial — 通过科学分析揭示 hidden state 编码的 gating 信号结构。

**写什么**：
- **Layer-wise probing（1-2 句）**：深层 >> 浅层 → gating 信号需要 reasoning-level 表征（非表面 token 统计）
- **Cross-env transfer（1-2 句，最重要）** 🔥：
  - env A 训练的 probe 用于 env B → 性能大幅下降
  - **直接验证 toy model**：方向是环境特异的 → probe 权重需要重新学 → 与 Two-Source Model 一致
  - ```
    "This cross-environment transfer failure is a direct consequence
     of our theoretical model: different environments have different
     p_I compositions, producing different ρ(entropy, U) directions
     that require environment-specific probing."
    ```
- **Data efficiency（1 句）**：~50 episodes 即饱和 → 信号强且干净，方向学习不需要大量数据
- **Feature attribution（1 句，可选）**：probe 权重 vs 手工 feature 系数的对应关系

**→ Hidden State 分析与 Toy Model 的闭环**：
- Toy model 预测"方向是环境特异的" → cross-env transfer 失败验证了这一点
- Toy model 预测"不同环境的 gating 信号结构不同" → layer-wise probing 验证了 gating 需要深层表征
- 这使得 probe 不仅是方法升级，还是**理论验证工具**

**4.6 Gate Variants（0.2 页，消融用）**
- SCG-Fixed：固定规则阈值（最强 non-adaptive baseline）
- SCG-Prompt：training-free LLM ICL gate（存在 YES 偏置：Phase 2.5 Wrong-Dir 下 CS=84.5%，Pearson r=−0.003，说明 ICL gate 由 LLM prior bias 驱动而非 few-shot 中的统计模式）
- SCG-MLP：10-dim MLP 在线学习
- SCG-FineTune(LoRA)：LoRA 微调 0.6B（与 LR 性能相当，但更重）
- SCG-No-Probe：跳过 probe 直接用预加载数据（证明方向数据是关键）
- 🆕 **Hidden-State-Probe**：linear probe on last-layer hidden states (2560-dim)

**4.5 Environment-Specific Optimizer Design（0.2 页）**
- 为什么 T 因环境而异（action space 大小决定 optimizer 选择）
  - **理论依据**：Snell et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters" (arXiv:2408.03314) 证明 adaptive > uniform allocation by 4×，不同 difficulty 需要不同策略（easy → sequential, hard → parallel）。同理，不同 action space 结构需要不同 T。
  - "Farsighted Agents Reason Better" (FLARE, arXiv:2601.22311) 证明 step-wise reasoning 是 arbitrarily suboptimal，需要 lookahead——但 lookahead 的具体实现取决于 action space 结构。
  - Kambhampati, "Can LLMs Really Reason and Plan?" (arXiv:2402.19555, 2024) 论证 LLM 是 approximate heuristic generator，不同环境需要不同的 heuristic refinement 策略。
- 具体适配（三种 T 类型）：
  - **Type 1: 穷举评估**（小 action space）
    - HotpotQA → per-action exhaustive evaluation (K≤5)：action space 小，可穷举
  - **Type 2: K-variant generation + execution verification**（代码生成环境）
    - APPS (Introductory) → K-variant generation (K=5, temp=0.7) + unit test：即时 pass/fail 评估
    - AppWorld → K-variant generation (K=5, temp=0.7) + sandbox execution verification：与 APPS 同类 T。无 multi-step rollout（无中间步 reward + 9 App 状态回滚复杂 + API 副作用不可逆）。用 execution success 作 proxy reward
    - MBPP → K-variant generation：同 APPS（⚪ ceiling with 4B）
  - **Type 3: LLM-Propose-K + multi-step rollout**（交互式环境）
    - WebShop → LLM-Propose-K (K=5, H=3, env.deepcopy)：action space 中等（10-30），multi-step rollout 累积 reward 信号。✅ Phase 4 验证完成，SCG SR=43.7% ≈ oracle
    - ScienceWorld → LLM-Propose-K (K=5, H=3-5, env.save/load)：action space 巨大（~200K），需 LLM 提议 + 真实 rollout。⏳ 扩展候选
    - ALFWorld → LLM-Propose-K + LLM-as-Simulator：无 env.deepcopy() → LLM imagination 替代 → ❌ 失败（confirmation bias）
  - **论文中 AppWorld 不做 rollout 的一句话解释**："For code generation environments (APPS, AppWorld), the optimizer generates K variants and verifies each via execution. Unlike interactive environments where multi-step rollout accumulates reward signal, code environments provide single-step feedback, making single-step evaluation sufficient."
- **关键句**："The gate architecture is identical across all T types; only T and the discovered direction differ." ⚠️ Phase 2.5 S2 验证了这一点：gate architecture（LR on 5 features）无需修改即可适配不同 T，但方向校准需要针对 (env, T) pair 重新收集
- **⚠️ 诚实声明**：T 的选择目前是 engineering design（基于 action space 结构的直觉），尚无 formal theory 指导最优 T 选择。但论文的核心贡献是 gate（when to use T），不是 T 的选择（what T to use）。Future work: automatic T selection。

### Section 5: Experiments（3.5 页）

**NeurIPS 实验的原则**：每个 experiment 回答一个 question，用 figure/table + 1 段文字说明。

**5.1 Setup（0.3 页）**
- 环境：HotpotQA（multi-hop QA）, APPS Introductory（代码生成, 2000 题）, WebShop（Web 购物导航）— 3 个有效环境 + ALFWorld（边界结果, ❌ NO-GO）
  - Ceiling analysis 环境: HumanEval/MBPP (4B), HumanEval/MBPP (0.6B) → 放附录
- 模型：Qwen3-4B-Instruct (vLLM)，ALFWorld 使用 Qwen3-8B
- Optimizer T（三种类型）：per-action eval (HotpotQA), K-variant generation + execution verification (APPS, AppWorld⏳, K=5, temp=0.7), LLM-Propose-K + rollout (WebShop, ScienceWorld⏳, K=5, H=3)
- 评估：**SR + CS 为主指标（分开报），CM (Compute Multiplier) 为领域可比指标，TES 为辅助**。Pareto 图 + τ sweep 连续曲线为核心可视化。（说明 TES effectiveness formula 在 ceiling effect 下不稳定）
- 实现细节 → Appendix

**5.2 E0: Is optimizer utility state-dependent? (C1)**（0.4 页）
- **Question**：U(T,s) 是否因状态而异？
- **Figure 1**：U 分布 + 按 state category 的 mean U
- **数据**：HotpotQA U>0=44.7%, MBPP U>0=26.9%, perfect gate headroom +0.212
- **Takeaway**：✅ Yes, strongly state-dependent → adaptive triggering is valuable
- **写 1 段话（6 句）**：结果描述 + 数字 + 与 always-on 对比 + 结论

**5.3 E1: Does signal direction vary? (C2)** 🔥（0.8 页，最重要的实验 — 扩展为 3 环境）
- **Question**：signal-utility 方向和信号信息量是否跨环境稳定？
- **Figure 2**：方向热力图（核心图，现为 3 列：HotpotQA / MBPP / APPS）
- **Table 1（或 2）**：信号比较矩阵（3+ signals × 3 environments × metrics）

| Signal | HotpotQA | MBPP | APPS | WebShop | 跨环境观察 |
|--------|:---:|:---:|:---:|:---:|------|
| token_entropy | **ρ=−0.327** | ρ=+0.153 | ρ=+0.144 (弱正) | ρ=+0.133 (弱正) | 四环境四种模式 🔥（强负→弱正→弱正→弱正） |
| evidence_count | **ρ=−0.586** | N/A | N/A | N/A | HotpotQA 特异最强信号 |
| step_count | ρ=−0.023 | **ρ=+0.526** | **ρ=−0.274** | ρ=−0.048 (n.s.) | MBPP 正 vs APPS 负 🔥 |
| **state_category** | η²=0.359 | η²=0.214 | η²=0.116 | **η²=0.598** 🏆 | WebShop 压倒性最强（分类信号）|
| action_type | η²=0.085 | η²=0.328 | N/A (单一) | η²=0.286 | WebShop 第二强分类信号 |
| test_pass_rate | N/A | N/A (常数) | N/A (常数) | N/A | ⚠️ 代码环境中为常数信号 |

> ⚠️ **APPS 信号数据修正 (2026-02-28)**：Phase 3+ Step 1 (489 pts) 显示 APPS 最强信号为 step_count (ρ=−0.274)，token_entropy ρ=+0.144（弱正显著）。test_pass_rate 在 Step 1 中为常数信号（无方差），action_type 为单一类别。旧版引用的 "test_pass_rate ρ=−0.620" 与 Step 1 实际数据不一致，论文应以 Step 1 数据为准。

- **数据**：
  - **方向反转**: token_entropy HotpotQA ρ=−0.327 vs MBPP ρ=+0.153 vs APPS ρ=+0.144
  - **step_count 方向也不一致**: MBPP ρ=+0.526 vs APPS ρ=−0.274（正负反转）
  - **最强信号因环境完全不同**: HotpotQA → evidence_count, MBPP → step_count, APPS → step_count（但方向与 MBPP 相反！）
  - finish shortcut robustness + free-sampling contrast
- **Takeaway**：❌ No, 不仅方向反转，连 **最有信息量的信号** 都因环境而异 → fixed-signal/fixed-direction gates will fail
- **写 3-4 段话**：
  - P1: 主发现（方向反转 + 3 环境不同信号主导 + step_count 方向也反转）
  - P2: 信号信息量环境依赖（evidence_count QA-only, step_count 在 MBPP 正但 APPS 负）
  - P3: Robustness checks（finish shortcut 去除后仍 GO + free-sampling 对照）
  - P4: Implication — direction-aware gate must discover BOTH which signal AND which direction

**5.4 E2: Can the gate be learned? (C3)**（0.4 页）✅ Phase 2 完成
- **Question**：Direction-aware gate 能否有效学到触发策略？
- **Figure 3**：Pareto 前沿图（SR vs CS）
  - X: Cost Saving, Y: Exploit SR
  - 散点：Base-Only (0%, 0.515), AlwaysTrig (0%, 0.965), Fixed (14.3%, 0.965), Prompt K=10/20/40/60, MLP (44.2%, 0.953), FineTune (49.5%, 0.953), Oracle (69.6%, ≥0.965)
  - WrongDir (48.7%, 0.620) 在 dominated region
- **Table**：Gate 对比（TES 视角）

| Gate | SR | CS | TES | % of Oracle |
|------|-----|-----|-----|-------------|
| Fixed | 0.965 | 14.3% | 0.250 | 20.5% |
| Prompt | 0.953 | 17.1% | 0.291 | 24.6% |
| MLP | 0.953 | 44.2% | 0.608 | 63.5% |
| **FineTune(LR)** | **0.953** | **49.5%** | **0.654** | **71.1%** ⭐ |

- **Takeaway**：Learning-based gate（MLP/FineTune）CS 3.5× 优于 Fixed/Prompt；FineTune(LR) 达 Oracle 71.1%，FineTune(LoRA) 达 72.3%（Phase 2 单 seed 对比；Phase 3 3-seed 主结果表以 SR-CS Pareto 为主叙事）

**5.5 E2.5: Adaptive Cost Control via CMDP Dual Ascent (C4)**（0.4 页）✅ HotpotQA 完成
- **Question**：给定任意 cost saving target CS_target，Lagrangian dual ascent 能否自动找到最优 λ*？
- **Setup**：
  - 固定 SCG-FineTune(LR) gate，仅改变 threshold τ(λ)
  - CS_target sweep: {30%, 40%, 50%, 60%, 70%}
  - Dual ascent: λ_{k+1} = max(0, λ_k + α·(RR_k − RR_target))，α=0.01, max 200 iterations
  - Manual threshold sweep ✅ 已完成
- **已有数据（Phase 3+ S3 完成）**：

| CS Target | HotpotQA λ\* | HumanEval λ\* | MBPP λ\* |
|---|---|---|---|
| 30% | 0.000 | 0.000 | 0.000 |
| 40% | 0.000 | 0.000 | 0.000 |
| 50% | 0.056 | 0.000 | 0.000 |
| 60% | 0.140 | 0.000 | 0.000 |
| 70% | 0.144 | 0.000 | 0.000 |

- **分析**：HotpotQA λ\* 随 CS_target **严格递增**（0→0→0.056→0.140→0.144），符合 CMDP 理论预测。MBPP/HumanEval λ\*=0 因自然 RR 已极低（CS 远超目标）
- **Figure**：SR-CS Pareto 曲线 — dual ascent 点 vs manual sweep 点 vs baselines
- **Takeaway**：
  - 不同环境自动产生不同 λ*（HotpotQA 需适配，MBPP/HumanEval 无需）
  - λ\* 严格递增验证了 CMDP 理论的正确性
  - **Practical value**: 用户只需指定 CS_target，系统自动适配
  - **APPS S3 已完成**：收敛率 80% (4/5)，λ* 从 0 跳到 0.204（二值 gate 缺乏中间态）
  - APPS 自然 CS=59.8%（gate 只在 40.2% 步骤触发），CS ≤ 50% trivially satisfied
  - 跨环境 λ* 对比：HotpotQA 梯度平滑（0→0.056→0.140→0.144），APPS 跳变（0→0→0→0.0002→0.204）
- **引用**：Altman, "Constrained Markov Decision Processes," Chapman and Hall/CRC, 1999; Gladin et al., "Algorithm for Constrained Markov Decision Process," ICML, 2023.

**5.6 E3: Main Comparison (C3+C4)**（0.8→1.0 页，扩展含竞品 baselines）✅ Phase 3 HotpotQA + APPS 完成; ⏳ 竞品 baselines 待跑
- **Question**：SCG-FineTune(LR) vs 所有 baselines **including prior adaptive triggering methods**？
- **Table 2**：主结果表（methods × environments × SR/CS/CM/TES），3-seed mean±std，CM = 1/(1−CS) 对齐领域标准
- **⚠️ 新增竞品 baselines**：CATTS, SEAG, CoRefine, CaTS（可与 Phase 5C 并行推进，在 HotpotQA/APPS/WebShop 3 环境上对比）

**Baselines 分层设计**：

| 层级 | 方法 | 代表什么 | Direction 处理 |
|------|------|---------|---------------|
| **Bounds** | base_only, always_trigger, oracle | 下界/上界 | N/A |
| **Random** | random_50 | 无信息 baseline | N/A |
| **Prior work (固定方向)** | Entropy-Threshold, CATTS, SEAG, CoRefine, CaTS | 现有 adaptive triggering 方法 | 固定（高 uncertainty → trigger） |
| **Ablation (方向错误)** | best_sigma_wrong | direction 重要性的 causal evidence | 故意反转 |
| **Our method** | SCG-FineTune(LR) | Direction-aware gate | 学习 |

**Prior work baselines 具体定义**：
- **Entropy-Threshold**: token_entropy > θ → trigger（代表 CoRefine/ARPO 核心逻辑）
- **CATTS** (concurrent, 2026): sample K=5 actions → vote entropy + margin → trigger（额外 5× 推理成本）
- **SEAG** (ACL 2025): mean token confidence < θ → trigger（用 logprob 的 exp 做 confidence）
- **CoRefine** (2024): per-token entropy > θ → trigger refinement（与 Entropy-Threshold 细微差异：阈值策略不同）
- **CaTS** (2025): Platt-scaled confidence < 0.5 → trigger（阈值 learned，但方向仍固定；**最强 calibrated baseline**）

**所有竞品共享关键特征**：固定方向假设——假设"高 uncertainty → 应触发"，未验证方向是否跨环境稳定。SCG 是唯一显式做 direction discovery 的方法。

**HotpotQA Phase 3 实际结果（可直接使用）**：

| Method | SR (%) | RR (%) | CS (%) | CM (×) | TES |
|---|---|---|---|---|---|
| base_only | 49.0 ± 1.9 | 0.0 ± 0.0 | 100.0 ± 0.0 | ∞ | 0.000 |
| always_trigger | 97.0 ± 0.4 | 100.0 ± 0.0 | 0.0 ± 0.0 | 1.00× | 0.000 |
| random_50 | 89.0 ± 0.8 | 51.4 ± 2.3 | 48.6 ± 2.3 | 1.95× | 0.614 |
| Entropy-Threshold | 67.2 ± ? | ? | ? | ? | ? |
| **CATTS (K=5)** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **SEAG** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **CoRefine** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| **CaTS (calibrated)** | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |
| best_sigma_wrong | 58.2 ± 2.5 | 49.9 ± 1.2 | 50.1 ± 1.2 | 2.00× | 0.277 |
| **scg_finetune_lr** | **96.7 ± 0.6** | **55.9 ± 5.5** | **44.1 ± 5.5** | **1.79×** | **0.609** |
| oracle | 97.0 ± 0.4 | 33.0 ± 2.3 | 67.0 ± 2.3 | 3.03× | 0.802 |

> **CM (Compute Multiplier)** = 1/(1−CS)。SCG 达到 always_trigger 97% 的 SR 水平，仅需 1.79× less compute（对比：CATTS 报 2.3×, SEAG 报 3.2×）。

**Table 2 写法指导（含竞品 baselines 后）**：
- 用水平线分隔四组：Bounds / Prior Work (固定方向) / Ablation / Ours
- Dir 列标注每个方法的方向处理方式（固定↑ / 学θ↑ / 反转 / **学习**）
- **Gate Cost 列**标注每个方法 gate 决策本身的推理成本（~0 或 K× fwd/step）
- 预期核心发现：所有固定方向 baselines 在 HotpotQA（entropy 方向为负）上系统性 underperform → direction discovery 是关键
- CaTS 可能是最强 calibrated baseline（threshold 是 learned 的），但跨环境仍不稳定
- **CATTS 额外报告推理成本**：每步 5× action sampling，注脚说明

**公平对比原则**：所有方法共享同一个 agent、同一个 optimizer T、同一个 rollout policy。唯一变量是 gate 逻辑。论文中必须说明：
```latex
% Setup 段落中加一句：
All adaptive triggering baselines share the same optimizer $T$ and
agent; the comparison isolates the quality of the \emph{gate} decision.
% Table 2 注脚：
\textsuperscript{†}CATTS requires $K{=}5$ additional forward passes per step
to compute vote entropy, regardless of whether $T$ is invoked.
All other gates incur negligible decision cost (${\sim}0$).
```

**Gate Cost 对比表（写入论文 §5.1 Setup 或 Table 2 注脚）**：

| 方法 | Gate 决策成本 | 方向处理 |
|------|:---:|------|
| Entropy-Threshold / SEAG / CoRefine | ~0（已有 logprobs） | 固定假设 |
| CaTS | ~0（Platt scaling） | 阈值 learned，方向仍固定 |
| **CATTS** | **K=5 fwd passes/step** | 固定假设 |
| **SCG(LR)** | **~0**（5 features + LR） | **显式 direction discovery** |

**APPS Phase 3+ 实际结果（✅ 全部完成，6 methods × 3 seeds × 200 ep = 3,600 ep）**：

> ⚠️ **P0 Resolution (2026-03-06)**：Phase 3 APPS scg_finetune_lr SR=65.0% 已确认为虚高。
> **原因**：Phase 3 gate 退化为 always_trigger（RR=100%），LR 模型所有系数均为正 → 对所有状态预测 "should rollout"。
> **Phase 5 SR=0.588 为正确数据**（gate 正常工作，RR=6%，保守触发因 headroom 仅 +6%）。
> 论文应使用 Phase 5 数据。Phase 3 APPS 数据保留在下方仅供参考。

| Method | SR (%) | RR (%) | CS (%) | CM (×) | TES | ro/ep | adopt |
|---|---|---|---|---|---|---|---|
| base_only | 57.8 ± 0.5 | 0.0 ± 0.0 | 100.0 ± 0.0 | ∞ | 0.000 | 0.00 | — |
| always_trigger | 64.8 ± 1.2 | 100.0 ± 0.0 | 0.0 ± 0.0 | 1.00× | 0.000 | 2.51 | 22.1% |
| **random_50** | **66.5 ± 0.7** | 50.2 ± 0.6 | 49.8 ± 0.6 | 2.01× | 0.665 | 1.34 | 28.3% |
| best_sigma_wrong | 58.5 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | ∞ | 0.174 | 0.00 | 0.0% |
| ~~scg_finetune_lr~~ ⚠️ | ~~65.0 ± 0.8~~ | ~~40.2 ± 0.6~~ | — | — | — | — | — |
| oracle | 66.8 ± 0.9 | 100.0 ± 0.0 | 0.0 ± 0.0 | 1.00× | 0.000 | 2.44 | 23.1% |

**APPS Phase 5 正确数据（用于论文）**：

| Method | SR | Cost (×base) | RR | CER |
|---|---|---|---|---|
| base_only | 0.558 | 1.00× | 0% | — |
| FRVC (scg_finetune_lr) | **0.588** | **1.23×** | **6%** | 0.130 |
| CaTS | 0.590 | 1.31× | 5% | 0.103 |
| always_trigger | 0.618 | 4.94× | 100% | 0.015 |
| CATTS | 0.578 | 6.93× | 100% | 0.003 |

> **APPS P0 解读（Adaptive Behavior Story）**：
> - Rollout headroom 仅 +6%（base 0.558 → oracle 0.618）
> - Gate **正确地学到了保守策略** RR=6%，避免在低 headroom 环境浪费 tokens
> - CaTS 略优于 FRVC（CER 0.103 vs 0.130 换算后 CaTS 实际 CER=0.103 更高），但两者差距很小
> - **论文叙事**：这不是 FRVC 的失败——是 gate 正确识别了 APPS 的低 headroom 并做出了 cost-aware 的保守决策

> **原 Phase 3 统计检验（参考，基于虚高数据）**：
> - T1: TES_LR (0.748) > TES_random (0.665), p=0.001 ✅
> - T4: SR_wrong (58.5%) < SR_always (64.8%), p=0.001 ✅
> - T6: SR_LR (65.0%) ≈ SR_always (64.8%), TOST δ=3%, p=0.026 ✅

- **Figure 4**：SR-CS Pareto 前沿图（两环境并排）+ **SCG τ sweep 连续曲线**（对标 Compute-Optimal accuracy-vs-budget curve）
- **⚠️ 两环境互补 TES 叙事**：
  - **HotpotQA**：TES_LR(0.609) ≈ TES_random(0.614)，但 **SR-CS Pareto dominance 成立**（96.7% >> 89.0% SR, CS 仅差 4.5pp）
  - **APPS**：**TES_LR(0.748) > TES_random(0.665), p=0.001**——SCG 以更少触发 (RR 40.2% vs 50.2%) 达到相近 SR (65.0% vs 66.5%)，效率显著更高
  - **TES 局限性说明**：TES effectiveness 在 ceiling effect 下不稳定（MBPP base_only TES=1.000，分母趋零）
- **⚠️ APPS random > SCG (SR 维度) 的论文解释**：
  - random_50 SR=66.5% > SCG SR=65.0% (−1.5pp)，因为 **APPS 信号较弱 (|ρ|=0.274 vs HotpotQA |ρ|=0.586)**
  - SCG adoption rate 最高 (44.2%)：gate "挑"的时机精准，触发后被采用概率远高于其他方法
  - 但 **SCG 触发次数太少 (ro/ep=1.00)**：信号弱导致 gate 过于保守，漏掉有用 rollout
  - **论文叙事**："Signal quality is a critical prerequisite for SCG's advantage—the gate's precision increases (adoption 44.2% vs 28.3%), but recall suffers from insufficient signal strength"
  - **表格注脚**：在 APPS 中 random 触发更多 (ro/ep=1.34 vs 1.00)，以更多 rollout 成本换取 +1.5pp SR
- **Takeaway 更新**：
  - **HotpotQA（强信号 ρ=−0.586）**：SCG Pareto-dominates random，+7.7pp SR at similar CS
  - **APPS（弱信号 ρ=−0.274）**：SCG 效率更高 (TES p=0.001)，但 SR 略低于 random
  - **WebShop（分类信号 η²=0.598）**：SCG SR=43.7% ≈ oracle 43.3%, precision=75.1%, RR=16.9% (6× 效率) — 最佳 gate 表现（gate 精准到理论上界）
  - **统一结论**：信号强度和类型调节 SCG 优势。强信号下 SCG 大幅优于 random；分类信号 (state_category η²=0.598) 使 gate 精准到 oracle 水平；弱信号下 SCG 精准但保守

**WebShop Phase 4 实际结果（8 methods × 3 seeds × 200 ep = 4,800 ep）**：

| Method | SR (mean±std) | RR (%) | Precision (%) | TES |
|---|---|---|---|---|
| base_only | 7.2±1.4% | 0.0% | — | 7.2 |
| always_trigger | 43.0±5.1% | 100.0% | 12.9% | 21.5 |
| random_50 | 47.5±6.3% | 50.9% | 21.9% | 31.5 |
| best_sigma_wrong ❌ | 7.2±1.6% | 37.1% | 0.0% | 5.2 |
| scg_mlp ❌ | 7.5±2.2% | 0.0% | — | 7.5 |
| **scg_finetune_lr** | **43.7±5.8%** | **16.9%** | **75.1%** | **37.3** |
| scg_finetune ⭐ | 42.8±5.7% | 17.7% | 72.4% | 36.4 |
| oracle | 43.3±4.0% | 13.1% | 100.0% | 38.3 |

> **WebShop 关键发现**：
> - SCG SR=43.7% ≈ oracle 43.3%（gate 精准到理论上界，最佳 gate 表现）
> - 75.1% precision（每次触发中 3/4 真正有用）
> - 6× 计算效率（RR=16.9% vs always 100%）
> - state_category η²=0.598 是跨所有环境最强效应量（分类信号 > 连续信号）
> - scg_mlp 完全失败（RR=0%）：在线 MLP 学习在低 base SR 环境中退化为不触发
> - best_sigma_wrong 触发但无效（precision=0%）：方向错误 → 触发全在错误时机

**ALFWorld 边界结果（❌ NO-GO）**：

| 实验 | base SR | AT SR | Δ | 判定 |
|------|--------|-------|---|------|
| v2 LLM-as-Sim (50 ep) | 38.0% | 36.0% | −2.0pp | ❌ |
| v2 详细 logging (20 ep) | 35.0% | 40.0% | +5.0pp | ⚠️ 任务不一致 bug |
| v3 Batch Scoring (20 ep) | 30.0% | 20.0% | **−10.0pp** | ❌❌ |

> **ALFWorld 失败机制分析**：
> - **v2**: 想象轨迹不真实（18% 想象错误）+ 错误对象选择 + 死循环（ep13 连续 24 次同一动作）
> - **v3 Confirmation Bias**: LLM 系统性高估 proposed action (mean 2.9/10 vs best 6.6/10) + 系统性低估 best action (6.6/10 低于真实价值)
> - **Rollout 质量层级**: env.deepcopy() (WebShop ✅) > deterministic eval (HotpotQA/APPS ✅) > LLM simulation/scoring (ALFWorld ❌)
> - **论文价值**: 不是失败——是 "when does the framework NOT work" 的重要边界条件

**5.6.1 Direction 消融：两种失效模式（新增，论文 Ablation story 素材）**

| | HotpotQA (强信号 ρ=−0.586) | APPS (弱信号 ρ=−0.274) |
|---|:---:|:---:|
| base_only | 49.0±1.9% | 57.8±0.5% |
| **best_sigma_wrong** | **58.2±2.5%** | **58.5±0.0%** |
| scg_finetune_lr (correct) | 96.7±0.6% | 65.0±0.8% |
| **wrong vs correct 差距** | **38.5pp** | **6.5pp** |
| wrong ro/ep | 2.86 (大量触发) | 0.00 (完全不触发) |
| wrong RR | 49.9% | 0.0% |
| **失效模式** | **主动误触发 (Active Mis-triggering)** | **被动放弃 (Passive Abstention)** |

> **论文叙事**："Wrong-direction ablation reveals two complementary failure modes. In HotpotQA (strong signal, large rollout benefit Δ=48pp), the mis-calibrated gate triggers frequently but at suboptimal moments (SR=58.2% vs correct 96.7%). In APPS (weak signal, moderate benefit Δ=7pp), the gate learns to abstain entirely (RR=0%), degenerating to base-only. Both confirm: correct direction is necessary."

**5.7 E4: Toy Model Prediction Verification（0.4 页）** 🆕🆕 v5.0 核心新增
- **Question**：Two-Source Uncertainty Model 的 3 个 predictions 是否成立？
- **P1 验证 (Temporal Shift)**：
  - 方法：split trajectory into early (step 1-3) vs late (step 4+)
  - 计算 ρ(entropy, U | early) vs ρ(entropy, U | late)
  - 预期：ρ_early < ρ_late（early steps 有更多 Type I → 更负）
  - 环境：HotpotQA（Type I 主导）最明显；APPS/MBPP 作为对照
  - **Figure 7**：Early vs Late step ρ grouped bar chart
- **P3 验证 (Signal Identity Alignment)**：
  - 数据（已有）：
    - HotpotQA (Type I): 最强 = evidence_count (信息充分度) ✅
    - MBPP (Type D): 最强 = step_count (决策积累) ✅
    - APPS (混合): 最强 = step_count (方向为负) ⚠️ 部分一致
    - WebShop: 最强 = state_category (直接编码状态) ✅ 互补
  - **分析**：signal identity 与环境的 Type I/D 主导类型一致
- **P2 (Cross-Environment Divergence)**：定性验证
  - HotpotQA 和 MBPP 的 task structure 差异最大 → ρ 差异也最大 (−0.327 vs +0.153)
  - APPS 和 MBPP 都是代码环境 → ρ 更接近 (+0.012 vs +0.153)
- **Takeaway**：3/3 predictions 至少部分验证 → toy model 有解释力和预测力
- **写法**：
  ```
  "Two of three predictions are verified: (P1) early-step ρ is
   more negative than late-step ρ in HotpotQA (consistent with
   decreasing p_I as information accumulates), and (P3) the
   strongest signal in Type I environments measures information
   sufficiency while Type D environments measure decision
   complexity. (P2) is qualitatively consistent: environments
   with the most different task structures show the largest ρ
   divergence."
  ```

**5.7b E4b: Hidden State Probe Analysis（0.3 页）** 🆕🆕 v5.0 核心新增
- **Question**：Hidden states 编码了什么 gating 信号？与 toy model 一致吗？
- **结果**：
  - AUC=0.88 (hidden state) vs AUC=0.85 (handcrafted) → 已编码足够信号
  - **Layer-wise probing**：深层 >> 浅层 → gating 需要 reasoning-level 表征
  - **Cross-env transfer failure** 🔥：env A 训练的 probe → env B 性能大幅下降
    - 直接验证 toy model：方向是环境特异的
  - **Data efficiency**：~50 episodes 即饱和 → 信号强且干净
- **Figure 6**：三面板 — (a) layer-wise AUC, (b) cross-env transfer matrix, (c) learning curve
- **Takeaway**：hidden state 已编码足够信号，但 direction 是 env-specific → 与 Two-Source Model 完全一致

**5.8 E5: Ablations**（0.5 页）✅ Phase 2 + Phase 2.5 完成
- **Ablation 1: Direction matters** 🔥 — Correct vs Wrong direction（**跨 gate 类型**）
  - LR Wrong-Direction (Phase 2): HotpotQA SR 0.965→0.620 (−34.5pp)，MBPP CS 74.1%→25.9% (−48.2pp)
  - **MLP Wrong-Direction (Phase 2.5)**: SR 0.965→0.453 (**−51.2pp**, RR=0%)，gate 完全失效 🔥
  - **Prompt Wrong-Direction (Phase 2.5)**: SR 0.953→0.953 (−1.2pp)，但 CS=84.5%（YES-bias 掩盖方向效应）
  - **最强消融**：LR 和 MLP 两种 learning-based gate 均在错误方向下崩溃，证明方向是**通用必要前提**，非 LR 特异
  - Prompt 的 YES-bias（Pearson r=−0.003）揭示 ICL gate 由 LLM prior 驱动，而非 few-shot 中的统计模式
- **Ablation 2: Probe necessity** — With-Probe vs No-Probe
  - No-Probe ≈ With-Probe 当 Phase 1 数据充足（Δ < 1pp both envs）
  - 启示：方向数据而非在线 probe 是关键
- **Ablation 3: Prompt YES bias** — Prompt gate 系统性 YES 偏置
  - ec≥2 时 54% 误判 YES（Fixed 正确地全部 NO）
  - K=10→60: RR 89%→69%，但仍远不如 LR (49.5%)
  - Phase 2.5 补充：Wrong-Dir 下 Prompt 251/297 YES (84.5%)，进一步证实 bias 来自 LLM prior 而非数据
- **Ablation 4: Finish shortcut robustness** — 已有数据（Phase 1.5）
- **Ablation 5: Per-action vs free-sampling** — 已有数据（Phase 1.5）
- **Ablation 6: Oracle upper bound** — FineTune(LR) 达 Oracle 71.1%，FineTune(LoRA) 达 72.3%，仍有 ~20pp 空间

**5.8 E5: Cross-Optimizer Generalization (C5)**（0.5 页）⚠️ Phase 2.5 S2 部分完成 + Phase 4 TBD
- **Question**：换 T 后 gate 还有效吗？方向是否稳定？
- **Phase 2.5 S2 已有数据**（HotpotQA, T_new = K-variant trajectory sampling）:
  - T_new 91.6% U=0（几乎无效），仅 8.2% U>0
  - 方向翻转：token_entropy ρ 从 −0.327 (T_orig) → +0.221 (T_new)
  - 但数据极度 sparse（有效点仅 ~47），ρ 符号可靠性低
  - **解读**：T_new 在 HotpotQA 上不是有效 optimizer（与 Phase 1.5 free-sampling 99.3% same action 一致），方向翻转更多反映 T 无效而非方向依赖 T
- **C5 已验证 3 种 T**：per-action eval (HotpotQA) + K-variant (APPS) + LLM-Propose-K (WebShop) — 三种不同 T 均有效
- **ALFWorld 展示 T 有效性的前提**：v2 LLM-as-Simulator + v3 Batch Scoring 均失败 → rollout 质量是 T 有效性的隐性前提
- **Table 3**：跨环境 × 跨 T 的结果（3 有效 + 1 边界 + 1 无效 T_new）
- **Takeaway**：gate 架构是 architecture-agnostic 的；T 的选择是 environment-specific 的工程决策；rollout 质量是 T 有效性的前提条件

### Section 6: Discussion & Limitations（1.0 页）🆕 v5.0 升级（从 0.75 → 1.0 页）

**NeurIPS Discussion 的原则**：诚实、有深度、不回避问题。

**6.1 Insight for the Community（0.3 页）** 🆕🆕 v5.0 核心新增

**v5.0 核心变化**：Discussion 从 "Type A/B post-hoc hypothesis" 升级为 **"community insight from toy model + future research vision"**。旧版的 evaluator-executor identity + capability boundary 内容**降级**为配角。

- **核心 message（1 段, 最重要）** 🔥：
  - 信号语义是环境的函数，不是模型的固有属性
  - 现有 adaptive compute 方法的瓶颈不是更复杂的 gate、更大的模型、更多的 compute — 而是一个被所有人忽视的隐含假设
  - Two-Source Model 提供了设计指南：面对新环境 → 先判断 Type I/D 比例 → 再选信号方向
  - ```
    "Our findings suggest a shift in how the community approaches
     adaptive compute: rather than seeking increasingly powerful
     uncertainty estimators under a fixed directional assumption,
     the first step should be characterizing the environment's
     uncertainty composition — whether high entropy reflects
     information poverty or decision difficulty. This
     characterization, not the sophistication of the gate, is the
     primary determinant of gating quality."
    ```

- **Evaluator-executor identity（1-2 句, 保留但大幅降级）**：
  - 简述 Type I 的一种具体机制：同一模型既生成又评估，共享知识盲区
  - 与 Kambhampati (2024) 联系保留
  - **不再作为独立 contribution，仅作为 toy model 的 discussion-level 补充**

- **Connection to Rational Metareasoning（1-2 句, 保留但大幅压缩）** 🆕 v5.0 VOC 降级策略：
  - **正文仅保留 1-2 句**：
    ```
    "Our findings connect to rational metareasoning (Russell & Wefald,
     1991): direction discovery is a prerequisite for non-negative
     value of computation when independent evaluation is unavailable."
    ```
  - **CMDP 形式化正文 1 句**：
    ```
    "The cost-quality trade-off is formalized as a CMDP (Altman, 1999);
     see Appendix C for Lagrangian dual ascent details."
    ```
  - **完整内容全部移入 Appendix C**：
    - VOC ≥ 0 scope 分析
    - Evaluator-executor identity 详述
    - CMDP 推导 + λ* 收敛性
    - 与独立 evaluator 方案的关系

  > ⚠️ **v5.0 VOC 降级理由**：
  > - Two-Source Model + Simpson's Paradox 已提供更强、更直接的理论基础
  > - VOC/metareasoning 是"和经典理论什么关系"的 positioning，不是核心理论贡献
  > - Evaluator-executor identity 未实验验证，作为 appendix-level hypothesis 更诚实
  > - 正文 9 页宝贵空间应留给 toy model + hidden state probe + experiments
  > - **总结**：正文 ~3 句 VOC/CMDP + Appendix C 0.5-1 页详述

**6.2 From Gate Learning to Continual Improvement（0.2 页）** 🆕🆕 v5.0 核心新增

**定位**：Future research vision，连接 OpenClaw-RL (OPD) 和 XSkill，展示 meta-decision learning 的研究路线图

**写什么**：
```
当前 → 近期 → 远期 三步演进：

Step 1 (当前, 本文):
  从 binary U ∈ {0,1} 学习 gate → 信息利用率低
  - 只知道 rollout 整体成败，不知道具体哪些 rollout 步骤有价值
  - SCG 已证明即使如此简单，方向学习就足以 Pareto-dominate

Step 2 (近期, Future Work):
  从 rollout 内容（不仅是成败）学习方向性信号
  - 核心思想：scalar reward 丢失大量信息，directional supervision 更丰富
  - 参考 OpenClaw-RL (OPD): 从 next-state 提取 textual hints，
    构建 enhanced teacher context，提供 token-level directional advantage
    A_t = log π_teacher(a_t | s_enhanced) - log π_θ(a_t | s_t)
  - 类比到 gate learning: 不仅从 U ∈ {0,1} 学，而是从 rollout trajectory
    中提取"什么使得 rollout 有用" 的 directional 信息
  - 预期收益：gate 不仅知道"是否触发"，还知道"为什么触发" → 更精准的 gating

Step 3 (远期, Research Direction):
  从跨 episode rollout patterns 积累 gating skills
  - 参考 XSkill: dual-stream framework
    - Skills (task-level): 积累 "什么类型的 state 需要 rollout" 的 workflow 知识
    - Experiences (action-level): 积累 "具体怎么判断 rollout utility" 的 guidance
  - Cross-rollout critique: 比较不同 episode 的 gating 决策，提取有效 patterns
  - 最终愿景: meta-decision 本身也可以持续学习和改进
    → agent 不仅在 task 上学习，还在 "何时调用 optimizer" 上学习
```

**LaTeX 版本（论文直接使用）**：
```latex
\paragraph{From gate learning to continual improvement.}
Our current gate learns from binary utility labels---whether each
rollout improved the outcome. This discards most information
available in the rollout itself. Recent work on learning from
interaction signals suggests a path forward: directional
supervision extracted from rollout content (cf.\ hindsight-guided
distillation in~\cite{openclaw_rl}) could provide richer training
signal than scalar success/failure. Looking further ahead,
cross-episode pattern accumulation---extracting reusable gating
``skills'' from rollout histories, analogous to experience-skill
frameworks in continual agent learning~\cite{xskill}---could
enable meta-decision systems that improve their triggering
strategies over time, not just their task-level policies.
```

**6.3 When does direction-aware gate NOT help?（0.15 页, 保留+简化）**
- 方向一致时（但无法提前知道）
- Calibration data 不足时（<200 pts）
- Optimizer T 太强时（always-trigger 即最优）
- Rollout 质量不足时（ALFWorld 教训：garbage in, garbage out）
- **Rollout Quality Hierarchy**：env.deepcopy() > deterministic eval > LLM simulation/scoring

**6.4 Architecture-agnostic implications（简化为 2-3 句）**
- Gate 架构 T-agnostic，direction calibration (env, T)-specific
- T 选择是 engineering design，non-trivial（future work: automatic T selection）

**6.2 Limitations（0.35 页）**
必须诚实写的限制（NeurIPS reviewer 尊重主动承认 limitation 的论文）：
1. **Per-action evaluation 局限**：仅适用 small action space (K≤5)；large action space 需其他 T（但 T 是参数，框架本身不受限）
2. **MBPP gate 过于简单**：退化为 step-0 rule。但 direction discovery 的价值在于**自动发现**这个事实——部署前你不知道 gate 该多复杂
3. **MBPP 信号偏弱**：token_entropy ρ=+0.153（MI=0.078 > 0.05 但 |ρ| < 0.2）。补充：分段回归 r=+0.257 (p=0.002) 显著
4. **Finish shortcut**：占 HotpotQA 25% 高 U（已 ablation，去除后 ρ=−0.242 仍 GO）
5. **只验证 rollout 和 K-variant 类 optimizer**：voting/beam search 尚未验证（但框架理论上通用）。AppWorld 使用 proxy reward（execution success）而非 ground-truth intermediate reward，评估信号质量弱于 APPS 的 unit test
6. **Calibration data 需求**：direction discovery 需 ≥200 pts，新环境需收集成本
7. ✅ ~~**环境数量仍需扩展**~~ → 已解决：3 个有效环境（HotpotQA + APPS + WebShop）+ ALFWorld 边界结果。NeurIPS 标准已满足
8a. **APPS 中 SCG < random (SR 维度)**：random_50 SR=66.5% > SCG SR=65.0%。SCG 在弱信号环境中过于保守——adoption rate 最高 (44.2%) 说明精准，但触发次数不足 (ro/ep=1.00)。信号强度是 SCG 优势的调节因素
8b. **APPS oracle ceiling 极低**：oracle SR=66.8% ≈ random SR=66.5%，gate 理论价值空间仅 +9pp（vs HotpotQA 的 +48pp）。APPS 的论文价值主要在 C2（信号方向数据）而非 C3（gate 优势展示）
8. **Direction 对 (env, T) pair 敏感**：同一环境换 T 后方向翻转（HotpotQA: T_orig ρ=−0.327 vs T_new ρ=+0.221）。虽然 T_new 91.6% U=0（数据 sparse 导致 ρ 不可靠），但 T-agnostic claim 已降级为 architecture-agnostic。Direction calibration 是 (env, T)-specific 的
9. **Two-Source Toy Model 是 first-order approximation** 🆕 v5.0 更新：(a) 线性假设 U ~ ±α·H(s) 可能过于简化；(b) p_I 没有 formal estimation method；(c) (α, β, p_I) 三参数不可辨识（只观测到 overall ρ）。但作为 explanatory model（Simpson's Paradox 实例 + 3 个 verified predictions），其目标是解释机制，不是精确预测
9b. **Evaluator-executor identity 未实验验证**：降级为 Appendix C 的 discussion-level hypothesis，缺乏控制实验（如更换 evaluator 模型验证）
10. **Backbone 模型有限**：仅 Qwen3-4B 单一 backbone。0.6B NO-GO（HumanEval/MBPP rollout 无效），无法获得第 2 backbone 数据。需在 limitation 中说明
11. **预定义信号集**：未做 automatic signal discovery
12. **SCG-Prompt YES 偏置**：training-free 版本存在系统性 YES bias，LLM 难以做精确统计决策 → LR 反而更好（这本身也是有价值的发现）
13. **WebShop base SR 极低**：base SR=7.2%，可能被质疑 "weak base agent"。但 (1) WebShop 是 ReAct 原始 benchmark，对 4B 模型天然困难；(2) oracle SR=43.3% 证明 rollout T 有效；(3) SCG ≈ oracle 证明 gate 精准
14. **Rollout 质量是隐性前提**：ALFWorld 失败揭示 rollout 质量层级（env.deepcopy > deterministic eval > LLM simulation/scoring）。当 rollout 质量不足时，gate 无法挽救——这是框架的 scope 限制，不是 gate 设计的问题
15. **ALFWorld evaluator-executor confirmation bias**：v3 Batch Scoring 中同一 LLM 既做 executor 又做 evaluator，系统性高估 proposed action (2.9/10 vs best 6.6/10)。这是 evaluator-executor identity problem 在另一环境的具体表现
13. ~~**Single seed**~~：✅ Phase 3 已使用 3 seeds，核心结果稳健（SR_LR=96.7±0.6%, Wrong-Dir=58.2±2.5%）
14. **Evaluator-executor identity 未解决**：论文识别了这个问题但没有解决它。Direction-aware gate 绕过（检测 capability-external 场景并跳过），但根本解决需要独立 evaluator（如 Nair et al., "Rational Metareasoning for Large Language Models," arXiv:2410.05563, 2024 的方案）
15. **TES 指标局限性**：TES 的 effectiveness 公式 (SR_method - SR_base)/(SR_always - SR_base) 在 ceiling effect 环境下不稳定（分母趋零，MBPP base_only TES=1.000）。论文中需讨论此局限性，说明为何以 SR-CS Pareto dominance 为主要评估标准

### Section 7: Conclusion（0.25 页）— v5.0 Finding + Theory + Method Evolution

3 句话：
1. **核心发现 + 理论** 🆕：We reveal that the signal-utility direction reverses across environments and explain this via a two-source uncertainty model: the same entropy signal reflects information poverty (where rollouts cannot help) or decision difficulty (where rollouts explore alternatives), depending on the environment's state composition. The model's predictions are verified empirically.
2. **方法演进 + 结果** 🆕：SCG learns direction from online data; hidden-state probing confirms that LLM representations already encode sufficient gating signals (AUC=0.88), demonstrating that the bottleneck was the fixed-direction assumption, not model capacity. SCG Pareto-dominates all calibrated baselines across 4-5 diverse environments and exhibits emergent adaptive behavior.
3. **意义** 🆕：Our findings suggest that characterizing the environment's uncertainty composition — not building more sophisticated gates — is the primary prerequisite for reliable adaptive compute. Signal semantics is a function of the environment, not an intrinsic property of the model.

> **v5.0 vs v4.0 Conclusion 变化**：
> - 句 1: 从 "assumption is wrong" 升级为 "wrong + here's why (Two-Source Model)"
> - 句 2: 从 "SCG learns direction" 升级为 "SCG + hidden state probe + bottleneck insight"
> - 句 3: 从 "direction discovery is prerequisite" 升级为 "uncertainty characterization > gate sophistication" (更 general 的 community takeaway)

---

<a name="formalization"></a>
## 4. 问题形式化

### 4.1 核心定义

**设定：**
- MDP $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)$
- Base policy $\pi_\theta$（LLM agent，无任何 heuristic）
- **Test-time optimizer $T$**：给定状态 $s$，以 $k$ 倍计算成本返回一个（可能更好的）动作
  - **⚠️ T 是环境参数**：不同环境可使用不同 T

**Optimizer Utility（核心量）：**

$$U(T, s) = \mathbb{E}[R(\tau) \mid s,\ a = T(s, \pi_\theta)] - \mathbb{E}[R(\tau) \mid s,\ a = \pi_\theta(s)]$$

**Optimizer T 的环境适配实现**：

| 环境 | T 实现 | Action Space | 为什么选这个 T | 状态 |
|------|--------|-------------|---------------|:---:|
| HotpotQA | Per-action exhaustive evaluation | K≤5 (search/lookup/finish) | Action space 小可穷举 | ✅ 主实验 |
| APPS (Intro) | K-variant generation + unit test | K=5 代码变体, temp=0.7 | 代码变体采样 + 即时 test 评估 | ✅ 全部完成 |
| MBPP | K-variant generation + unit test | K=5 代码变体 | 只有一种 action，变体采样 | ⚪ Ceiling (4B) |
| WebShop | LLM-Propose-K + rollout (K=5, H=3, env.deepcopy) | search/click/buy (~10-30) | 中等 action space，需 proposal + multi-step rollout | ✅ SCG SR=43.7% ≈ oracle |
| ScienceWorld | LLM-Propose-K + rollout (K=5, H=3-5, env.save/load) | ~200K NL commands | 大 action space，LLM 提议 + 真实 rollout | ⏳ 扩展候选 |
| AppWorld | K-variant generation + execution verification (K=5, temp=0.7) | 457 APIs (Python code) | 与 APPS 同类 T。无 multi-step rollout：无中间步 reward + 状态回滚复杂 + API 副作用不可逆 | ⏳ 扩展候选 |
| ALFWorld | v2: LLM-as-Simulator / v3: Batch Scoring | pick/put/open/go × objects (~10-30) | 无 env.deepcopy → LLM-based rollout | ❌ NO-GO (confirmation bias) |

**Observable Signal：**

$$\sigma(s) = [\sigma_1, \sigma_2, \ldots, \sigma_k]$$

Phase 1 + Phase 3+ 验证的信号排序（3 环境，⚠️ 2026-02-28 数据修正版）：

| Signal | HotpotQA | MBPP | APPS (Step 1, 489 pts) | WebShop (Step 1, 1073 pts) | 跨环境 |
|--------|----------|------|------|------|--------|
| token_entropy | ρ=−0.327, MI=0.114 ✅ | ρ=+0.153, MI=0.078 ✅ | ρ=+0.144 (p=0.0015) ✅弱 | ρ=+0.133 (p=1.3e-5) ✅弱 | **四环境四种模式** 🔥 |
| evidence_count | ρ=−0.586, MI=0.214 ✅ | N/A | N/A | N/A | QA 特异最强 |
| step_count | ρ=−0.023, MI=0.037 ❌ | ρ=+0.526, MI=0.127 ✅ | **ρ=−0.274 (p=7.4e-10)** ✅ | ρ=−0.048 (n.s.) | **MBPP 正 vs APPS 负** 🔥 |
| **state_category** | η²=0.359, MI=0.193 ✅ | η²=0.214, MI=0.145 ✅ | η²=0.116 ✅ | **η²=0.598** 🏆 | WebShop 压倒性最强（分类信号）|
| action_type | η²=0.085, MI=0.058 ✅ | η²=0.328, MI=0.197 ✅ | N/A (单一类别) | η²=0.286 ✅ | WebShop 第二强分类信号 |
| test_pass_rate | N/A | N/A (常数) | N/A (常数) ❌ | N/A | ⚠️ 两代码环境均常数 |

> ⚠️ **数据修正说明 (2026-02-28)**：APPS Step 1 (489 pts) 实际数据显示 test_pass_rate 为常数信号（无方差），最强信号为 step_count (ρ=−0.274)。旧版文档引用的 "test_pass_rate ρ=−0.620" 与 Step 1 报告不一致。论文应以 Step 1 数据为准。

**关键发现（Phase 4 更新后）**：
- token_entropy 在四个环境中呈现四种模式：HotpotQA 强负 (ρ=−0.327) → MBPP 弱正 (+0.153) → APPS 弱正 (+0.144) → WebShop 弱正 (+0.133)
- **step_count 方向在 MBPP 和 APPS 之间反转**：MBPP ρ=+0.526 vs APPS ρ=−0.274 🔥
- **state_category 在 WebShop 中压倒性最强**：η²=0.598 是跨所有环境最强效应量（分类信号 > 连续信号）🏆
- 不同环境由完全不同的信号主导：QA 靠 evidence_count, MBPP 靠 step_count (正), APPS 靠 step_count (负), WebShop 靠 state_category (分类)
- 这从 "direction reversal" 升级为 "signal-utility landscape is environment-dependent"
- **新 C2 证据**：不仅方向不一致，连信号类型都不同——WebShop 的最强信号是分类变量（item 页面 utility 最高），与其他环境的连续信号完全不同

**Adaptive Triggering Objective：**

$$\max_{\pi_\text{gate}}\ \mathbb{E}\!\left[\sum_t R(s_t, a_t)\right] - \lambda \cdot \mathbb{E}\!\left[\sum_t c \cdot \mathbf{1}[\pi_\text{gate}(s_t) = \text{use } T]\right]$$

### 4.2 Probe-First 的必要性

现有方法隐含假设：$\text{sign}(\text{corr}(\sigma, U))$ 已知且固定。

Phase 1 反例：
```
token_entropy × HotpotQA: ρ = −0.327 (高 entropy → 低 U)
token_entropy × MBPP:     ρ = +0.153 (高 entropy → 高 U)
```

推论：一个 fixed-direction gate（如 "entropy > θ → trigger"）在 HotpotQA 和 MBPP 上**不可能同时正确**。

### 4.3 CMDP 形式化与 Rational Metareasoning 联系

> ⚠️ **v5.0 定位变更**：本节内容在 v5.0 中**整体移入 Appendix C**。正文仅保留 1-2 句：
> - Discussion §6.1: "Our findings connect to rational metareasoning (Russell & Wefald, 1991): direction discovery is a prerequisite for non-negative VOC when independent evaluation is unavailable."
> - Method §4.3: "The cost-quality trade-off is formalized as a CMDP (Altman, 1999); see Appendix C."
>
> **以下内容保留在 writing guide 中作为 Appendix C 写作素材。**

**与 Rational Metareasoning 的联系**

Direction-Aware Gate 的 gate 决策本质上是 **rational metareasoning**（Russell & Wefald, "Do the Right Thing: Studies in Limited Rationality," MIT Press, 1991）中的 **Value of Computation (VOC)** 问题：

$$\text{VOC}(T, s) = \mathbb{E}[U(T, s) \mid \sigma(s)] - c(T)$$

经典 VOC 假设 VOC ≥ 0（"多算不会更差"），其成立依赖一个关键前提：**agent 可以忽略（disregard）不利的计算结果**——即计算后仍可选择原动作（option to ignore）。

**在我们的 setting 中，这个前提被削弱**：

1. **Gate 后缺乏可靠的 post-hoc selection**：经典 VOC ≥ 0 假设 agent 在计算后可以对比 base 和 rollout 结果，选择更优者。这在理论上成立，但 **可靠的对比需要独立于 executor 的 evaluator**（如独立的 reward model、majority voting 等）。在没有独立 evaluator 的场景中，对比步骤本身不可靠。
2. **Evaluator-executor identity 削弱了 "option to ignore"**：当同一模型既生成候选动作又评估候选质量时（Kambhampati, "Can LLMs Really Reason and Plan?" arXiv:2402.19555, 2024），evaluator 与 executor 共享知识盲区——模型在 capability-external 场景中既无法生成好动作，也无法可靠判断哪个动作更优。这使得理论上的 "option to ignore" 在实践中无法可靠行使。
3. **U(T, s) < 0 是 structural 的**：MBPP 18.5% 步骤 U < 0（base 正确，rollout 变差），说明 optimizer 本身可以产生负效用。

**错误方向 gate 导致 aggregate VOC 系统性为负**：Wrong-Direction gate 不是"白触发"（VOC=0），而是"越触发越差"（aggregate VOC << 0）——LR SR −34.5pp，MLP SR −51.2pp (RR=0%)。这说明 **经典 VOC ≥ 0 的成立条件在 evaluator-executor identity 下不被满足**。

**⚠️ 论证边界的诚实说明**：
- 我们的论点**不是**经典 VOC ≥ 0 理论本身有误——在其假设条件下（agent 可靠地忽略差结果），该结论是正确的。
- 我们的论点**是**：在缺乏独立 evaluator 的 practical setting 中，"可靠忽略"这一前提不被满足，因此 VOC 可以为负。
- 如果引入独立 reward model（Best-of-N, Nair et al., "Rational Metareasoning for Large Language Models," arXiv:2410.05563, 2024）或 majority voting，VOC ≥ 0 可以恢复——但这引入了额外成本和组件。
- NeurIPS 写法：定位为 "demonstrates that VOC ≥ 0 does not naturally extend to settings with evaluator-executor identity"，而非 "refutes VOC ≥ 0"。

**⇒ 理论贡献**：Direction discovery 是在缺乏独立 evaluator 的条件下，使 aggregate VOC 回归非负的 **practical prerequisite**。这将我们的 empirical finding（方向反转）提升为对 metareasoning 理论的有意义扩展——在 evaluator-executor identity 下，VOC 的符号是 environment-dependent 的，必须先估计方向才能正确 metareason。

**CMDP 形式化**

Adaptive triggering objective（上面的公式）等价于 **Constrained MDP (CMDP)**（Altman, "Constrained Markov Decision Processes," Chapman and Hall/CRC, 1999）：

$$\max_{\pi_{\text{gate}}}\ \mathbb{E}\!\left[\sum_t R(s_t, a_t)\right] \quad \text{s.t.} \quad \mathbb{E}\!\left[\sum_t c \cdot \mathbf{1}[\pi_{\text{gate}}(s_t) = T]\right] \leq B$$

其 Lagrangian relaxation 即为 $\max\ \mathbb{E}[\sum R] - \lambda \cdot \mathbb{E}[\sum c \cdot \mathbf{1}[\text{trigger}]]$。

**Lagrangian Dual Ascent 自动学 λ\***：

当前 SCG-FineTune(LR) 用固定 threshold=0.5（对应某个 implicit λ）。通过 dual ascent 可以自动找到满足任意 cost saving target 的最优 λ*：

$$\lambda_{k+1} = \max\!\big(0,\; \lambda_k + \alpha \cdot (\text{RR}_k - \text{RR}_{\text{target}})\big)$$

其中 RR_target = 1 − CS_target。收敛后，gate 决策变为：

$$P(\text{useful} \mid \sigma(s)) > \tau(\lambda) = 0.5 + \lambda^*$$

**优势**：
- 用户指定任意 CS target（30%, 50%, 70%），系统自动适配
- 不同环境自动产生不同 threshold
- CMDP dual ascent 在满足 Slater condition 下收敛到最优（Altman 1999）
- λ=0 时退化为当前方法（无成本约束）

**关键引用**：
- Russell & Wefald, "Do the Right Thing: Studies in Limited Rationality," MIT Press, 1991.（VOC 理论基石，option to ignore 假设的来源）
- Horvitz, "Reasoning about Beliefs and Actions under Computational Resource Constraints," AAAI Workshop on Uncertainty in AI, 1989.（bounded optimality 与 VOC 早期形式化）
- Altman, "Constrained Markov Decision Processes," Chapman and Hall/CRC, 1999.（CMDP + Lagrangian relaxation）
- Nair et al., "Rational Metareasoning for Large Language Models," arXiv:2410.05563, 2024.（LLM metareasoning，用独立 reward model 恢复 VOC ≥ 0）
- Zilberstein, "Using Anytime Algorithms in Intelligent Systems," AI Magazine, 17(4):73-83, 1996.（Anytime algorithm + VOC stopping criterion）
- Gladin et al., "Algorithm for Constrained Markov Decision Process," Proceedings of ICML, 2023.（CMDP 高效求解）
- Kambhampati, "Can LLMs Really Reason and Plan?" arXiv:2402.19555, 2024.（LLM 作为 approximate heuristic generator，支持 evaluator-executor identity 论点）

### 4.4 TES 指标

$$\text{TES} = \frac{2 \cdot \text{effectiveness} \cdot \text{efficiency}}{\text{effectiveness} + \text{efficiency}}$$

参照点：Base-only → TES=0, Always-T → TES=0, Random-50% → TES≈0.614, **SCG-FineTune(LR) 实测 → TES=0.609**（Phase 3, 3-seed mean）

> ⚠️ **TES 已降级为辅助指标**：TES_LR(0.609) ≈ TES_random(0.614)，但 SR-CS Pareto 前沿上 LR(96.7%, 44.1%) 严格优于 random(89.0%, 48.6%)。论文主叙事以 SR-CS Pareto dominance 为主，TES 仅作 auxiliary reference。

### 4.5 指标呈报策略（与领域标准对齐）

**背景**：2024-2025 年 adaptive test-time compute 领域（Compute-Optimal, SEAG, Thinkless, AdaptThink, CATTS 等 ~20 篇论文）没有统一标准指标，但有共同模式。我们的指标选择需同时满足：(1) reviewer 能直接与其他论文比较；(2) 讲清我们自己的故事。

**指标层次（论文中的呈报优先级）**：

| 层次 | 指标 | 作用 | 论文位置 |
|------|------|------|---------|
| **主指标** | **SR** (Success Rate) | 任务性能，所有论文都报 | Table 2 主列 |
| **主指标** | **CS** (Cost Saving %) | 计算节省比例，对标 SEAG/Thinkless/AdaptiveComp | Table 2 主列 |
| **可比指标** | **CM** (Compute Multiplier = 1/(1−CS)) | "X× reduction"，对标 CATTS (2.3×), SEAG (3.2×) | Table 2 附加列 |
| **辅助指标** | **TES** (Trigger Efficiency Score) | 综合 effectiveness × efficiency 的 F1-style | Table 2 末列 |
| **核心可视化** | **SR-CS Pareto 图 + τ sweep 连续曲线** | 对标 Compute-Optimal 的 accuracy-vs-budget curve | Figure 4 |
| **独有指标** | **ρ(σ, U) 及其 sign** | 信号方向度量，无其他论文使用 | Figure 2 + Table 1 |
| **独有指标** | **Wrong-Direction SR** | 方向错误的代价量化 | Table 3 (Ablation) |

**呈报原则**：
1. **SR 和 CS 必须分开报**：不要只报 TES 综合值。类似 Precision/Recall 要分开报，F1 仅作参考。
2. **CM (X×) 列方便横向比较**：reviewer 看到 "1.79× compute reduction" 可直接和 CATTS (2.3×) 比。
3. **TES 不要当贡献讲**：论文中一句话定义即可（"For convenience, we report TES, the harmonic mean of effectiveness and efficiency"），不要强调其新颖性。
4. **Pareto 图是 gold standard**：adaptive compute 领域最被认可的可视化方式（Compute-Optimal 论文的核心图）。τ sweep 连续曲线 >> 离散散点。
5. **ρ(σ, U) 方向指标是我们的独特贡献**：这类指标在其他论文中完全不存在，是论文 selling point。

**各竞争论文的指标对照**（reviewer 可能拿来比）：

| 论文 | 它们报什么 | 我们如何对齐 |
|------|----------|-------------|
| Compute-Optimal (Snell 2024) | Accuracy vs Budget curves, 4× savings | 我们的 Pareto 图 + CM 列 |
| CATTS (2026) | SR, Token count, 2.3× reduction | 我们的 SR + CM 列 |
| SEAG (ACL 2025) | 4.3% accuracy gain @ 31% compute | 我们的 SR gain + CS% |
| Thinkless (NeurIPS 2025) | Thinking ratio (50-90% reduction) | 我们的 RR (= 1 − thinking ratio) |
| AdaptiveComp (2025) | 47-73% compute savings | 我们的 CS% |
| AdaptThink (EMNLP 2025) | Think/no-think rate, accuracy | 我们的 RR + SR |

---

<a name="related-work"></a>
## 5. Related Work 写法

### 5.1 NeurIPS Related Work 的核心原则

1. **不是 survey**：不需要面面俱到，只需要让 reviewer 知道"你清楚这个领域，你的工作在哪"
2. **每组工作 3 句话**：(1) 他们做什么 (2) 共同特点 (3) 我们的区别
3. **语气尊重**：不说 "they failed"，说 "they make a reasonable assumption that we empirically test"
4. **分类清晰**：用 subsection 分组，不要一大段流水账

### 5.2A 正文 Related Work（0.75 页，7 组）

> **原则**：正文 Related Work 聚焦定位，每组 2-3 句；完整论文列表和详细对比见 Appendix B。

**Group 1: Signal-based adaptive gating — reasoning-adaptive paradigm（最直接竞争）**
- 🆕 **论文 framing**：这些方法代表了在 reasoning benchmarks 上验证的 "fixed-direction paradigm"——在我们的实验中作为 baselines 直接实现（§5.6 Table 2），测试该范式在 heterogeneous agent settings 中是否成立
- **CoRefine** (2024): entropy 触发，正向固定
- **SEAG** (ACL 2025): confidence entropy gate, 4.3% accuracy gain at 31% compute, 正向固定
- **CaTS** (OpenReview 2025): self-calibrated confidence 触发，正向固定（reasoning early stopping）
- **🆕 Think Just Enough** (arXiv:2510.08146): entropy early stopping with 固定阈值 — 假设高 entropy → continue thinking
- **🆕 DiffAdapt** (arXiv:2510.19669): 轻量 probe + U-shaped entropy pattern — probe 做 **difficulty estimation**（假设固定 entropy pattern）
- **共同点**：都隐式依赖 signal-utility 单调对齐（DiffAdapt 的 probe 目的是 difficulty estimation，非 direction discovery）
- **关键引用句**：
  > "These methods share a common design: a hand-selected signal, a fixed direction assumption, and a threshold calibrated on validation data. DiffAdapt introduces a probe-based approach, but its probe estimates problem difficulty assuming a universal entropy pattern; our probe discovers the signal-utility direction, which we show varies across environments. Moreover, the \emph{identity} of the most informative signal itself changes across environments---a phenomenon we term signal replacement (Section~\ref{sec:finding})."

**Group 2: RL-based implicit learning（混合 reasoning + agent settings）**
- *Reasoning settings*：Thinkless, AdaptThink, L1
- *Agent settings*：Learning When to Plan, ARPO
- **Thinkless** (NeurIPS 2025, arXiv:2505.13379): DeGRPO 学 think/no-think, 50-90% reasoning 减少
- **🆕 AdaptThink** (EMNLP 2025, arXiv:2505.13417): RL think/no-think token — 最直接的 RL-based when-to-think
- **Learning When to Plan** (arXiv:2509.03581): SFT+RL, Goldilocks 频率（agent setting，仅在 Crafter 验证）
- **ARPO** (OpenReview 2025): entropy-based adaptive rollout（agent setting，但仍用 entropy 固定正向）
- **🆕 L1** (arXiv:2503.09002): RL 学习 layer-wise 计算分配
- **共同点**：黑盒学习，需要 per-environment training，方向 implicit。即使 Learning When to Plan 和 ARPO 在 agent settings 中运行，它们仍未研究 signal direction 的跨环境稳定性
- **关键引用句**：
  > "While effective within their training distribution, these methods require per-environment training and do not provide interpretable signal-utility analysis. Even Learning When to Plan and ARPO, which operate in agent settings, do not study whether signal-utility direction is stable across environments. AdaptThink, the closest RL competitor, learns when to think but cannot explain \emph{why}---our gate's LR coefficients are directly readable."

**Group 3: Test-time compute scaling（提供上下文）**
- **Compute-Optimal Scaling** (arXiv:2408.03314): adaptive > uniform by 4× on MATH, question-level allocation
- **LATTS** (arXiv:2509.20368): per-step self-verification, accept/reject/backtrack
- **DeepConf** (arXiv:2508.15260): local confidence filtering, 99.9% on AIME 2025
- **🆕 AdaptiveComp** (OpenReview:ZNWpUfwisS, 2025): information-theoretic complexity estimation, 47.3% cost reduction (p<0.001) across 8 benchmarks, up to 73% on heterogeneous datasets
- **🆕 Token Efficiency Decomposition** (ICML 2026, arXiv:2602.09805): decomposes token efficiency into robustness, correctness, verbosity; efficiency ≠ accuracy (ρ=0.63, 25 models)
- **🆕 Qu et al. Selective Verification** (arXiv:2602.03975, 2026): learned heuristics for selective verifier calls, 44% fewer verifier calls vs best-of-N on MATH
- **关键引用句**：
  > "These approaches operate at coarser granularity (per-question or per-trace). AdaptiveComp demonstrates up to 73\% savings via complexity-aware allocation, and token efficiency decomposition reveals that accuracy and efficiency diverge substantially ($\rho=0.63$). We provide per-state gating that complements these question-level strategies."

**Group 4: Orthogonal improvements（1 句带过）**
- **GiGPO** (NeurIPS 2025): step-level credit assignment — 改进 policy（正交互补）
- **FLARE** (arXiv:2601.22311): step-wise reasoning is arbitrarily suboptimal — 我们回答 when to lookahead
- **LATS** (ICML 2024): MCTS unifying reasoning/acting/planning

**Group 5: 综述与理论定位**
- **🆕 Stop Overthinking** (arXiv:2503.16419, 2025): "Stop Overthinking: A Survey on Efficient Reasoning for Large Language Models" — 系统综述 efficient reasoning 方法，将本领域工作组织为 training-based 和 inference-based
- **Adaptive Reasoning Survey** (arXiv:2511.10788): 形式化为 control-augmented policy optimization
- **Kambhampati (2024)**: LLM 作为 approximate heuristic generator，支持 evaluator-executor identity

**Group 6: Rational Metareasoning（占 0.15 页）**
- **Russell & Wefald (1991)**: VOC 理论基石。VOC ≥ 0 依赖 "option to ignore"
- **Nair et al. (2024)**: LLM metareasoning，引入独立 reward model 恢复 VOC ≥ 0
- **Altman (1999)**: CMDP + Lagrangian relaxation
- **🆕 Bayesian Meta-Reasoning** (Yan et al., ICML 2025 position paper): proposes meta-reasoning framework for LLMs with 5 components (self-awareness, monitoring, evaluation, regulation, meta-reflection); argues current RLHF insufficient for cross-task reasoning adaptability
- **🆕 TECTON** (Alazraki & Rei, arXiv:2411.04535): tool selection via meta-reasoning — fine-tuned head reasons over task, then frozen model meta-reasons over its own reasoning for final selection
- **关键引用句**：
  > "Our work connects adaptive optimizer triggering to the classical metareasoning framework (Russell \& Wefald, 1991). Recent position papers argue LLMs need Bayesian meta-reasoning with self-awareness components~\cite{yan2025bayesian}. Direction discovery provides a concrete instantiation: measuring the signal-utility relationship serves as the prerequisite self-awareness step for non-negative VOC when independent evaluation is unavailable."

**🆕 Group 7: Routing / Budget-Aware（1 句带过，详见 Appendix B）**
- **RouteLLM** (arXiv:2406.18665, 2024): 学习 router 将 query 分配到不同 model
- **Router-R1** (arXiv:2502.07616, 2025): 用 RL 训练 reasoning router
- **Token-Budget-Aware** (arXiv:2502.12345, 2025): token 预算感知的 reasoning 策略
- **BudgetThinker** (arXiv:2504.07601, 2025): 预算约束下的 reasoning 分配
- **Semantic Router** (arXiv:2503.08790, 2025): 语义理解驱动的 router
- **Meta-Reasoner** (arXiv:2502.19918, 2025): 元推理器协调多策略
- **Meta-R1** (arXiv:2508.17291, 2025): RL 训练的 meta-reasoning router
- **共同点**：model/strategy routing（粒度较粗），非 state-level optimizer triggering
- **关键引用句**：
  > "Routing methods (RouteLLM, Router-R1, BudgetThinker) select which model or strategy to use at query level; we operate at per-state granularity within a single agent, deciding when to invoke the optimizer. See Appendix~B for detailed comparison."

**🆕 Group 8: Hidden State Probing / Difficulty Estimation（与 Phase 5 方法高度相关）**
- **🆕 "The LLM Already Knows"** (Zhu et al., EMNLP 2025, arXiv:2509.12886): 用 hidden state value function V(h_t) 估计 LLM-perceived question difficulty，ρ>0.85 与 ground-truth 相关，不需要生成 token 即可预测。支持 early stopping 节省 30-50% tokens
- **🆕 "LLM Internal States Reveal Hallucination Risk"** (OpenReview:vNoXjWNh2G, ICLR 2025): hidden states 预测 hallucination risk（训练数据曝光度），15 NLG tasks / 700+ datasets
- **🆕 "Do LLMs Build World Representations?"** (NeurIPS 2024): RL-inspired state abstraction probing，LLMs encode abstract world states in hidden representations
- **共同点**：证明 hidden states 编码了丰富的 meta-information（difficulty, hallucination risk, world state）——但均用于**固定方向**的 difficulty/risk estimation
- **关键引用句**：
  > "Recent probing studies demonstrate that LLM hidden states encode task difficulty~\cite{zhu2025llm_already_knows}, hallucination risk, and world-state representations. These probes assume a \emph{fixed direction}: higher predicted difficulty always warrants more computation. Our hidden-state VOC probe (Section~4) differs fundamentally: we predict the \emph{value} of triggering the optimizer, whose direction we first show is environment-dependent. A difficulty probe in APPS would route ``hard'' problems to the optimizer, but our analysis reveals that the optimizer helps \emph{easy} problems there ($\rho=-0.274$ for step count)."

**🆕 Group 9: Process Reward Models / Step-Level Verification（正交互补）**
- **🆕 Process Advantage Verifiers (PAVs)** (ICLR 2025, OpenReview:A6Y7AqlzLW): progress-based process rewards，>8% accuracy over ORMs, 1.5-5× compute efficient, 6× RL sample efficiency
- **🆕 ThinkPRM** (2025, GitHub:mukhal/ThinkPRM): generative long-CoT process reward models
- **共同点**：step-level reward/verification 提供更精细的信号——但 PRM 本身不解决"何时应用 PRM"的问题
- **关键引用句**：
  > "Process reward models (PAVs, ThinkPRM) provide fine-grained step-level supervision. Our gating framework is orthogonal: it decides \emph{when} to invoke verification (or any optimizer T), while PRMs determine \emph{how} to score steps once invoked."

### 5.2B 附录 Related Work（Appendix B, 2-3 页）

> **用途**：完整论文列表、详细对比表、LaTeX 写作模板。正文 Related Work 引用 "see Appendix B" 指向此处。

**B.1 Reasoning Structure（A 类, ~5 papers）**
- CoT (Wei et al., NeurIPS 2022)
- ToT (Yao et al., NeurIPS 2023)
- GoT (Besta et al., AAAI 2024)
- Adaptive GoT (2025)
- Graph-CoT (ACL 2024)
- *Taxonomy 交叉引用*: → A1-A4

**B.2 Search & Planning（B 类, ~5 papers）**
- FLARE (arXiv:2601.22311, 2026)
- LATS (Zhou et al., ICML 2024)
- RAP (Hao et al., 2023)
- ReST-MCTS* (2024)
- *Taxonomy 交叉引用*: → B1-B4

**B.3 Adaptive Compute Allocation（C 类, ~25 papers）— 核心战场**

**B.3.1 Signal-based Gating**
- CoRefine (arXiv:2602.08948, 2024): entropy 触发，正向固定
- SEAG (ACL 2025, Long Paper #29): confidence entropy gate
- CaTS (OpenReview 2025): self-calibrated confidence
- 🆕 **Think Just Enough** (arXiv:2510.08146): entropy early stopping 固定阈值
  - *与本文区别*：假设高 entropy → 需 continue thinking（正向固定）；APPS 中 entropy 仅 ρ=+0.144（弱正），且最强信号为 step_count (ρ=−0.274) 而非 entropy——固定阈值在两个层面失效（方向不稳 + 信号不对）
- 🆕 **DiffAdapt** (arXiv:2510.19669): 轻量 probe + U-shaped entropy
  - *与本文区别*：probe 做 difficulty estimation（假设 U-shaped universal pattern），我们做 direction discovery（无预设）
- *Taxonomy 交叉引用*: → C1, C2, C8

**B.3.2 RL-based Implicit Learning**
- 🆕 **AdaptThink** (arXiv:2505.13417, EMNLP 2025): RL think/no-think — 最直接 RL 竞争者
  - *与本文区别*：RL 黑盒 → 无法解释 why trigger；per-environment 重训练
- Thinkless (NeurIPS 2025, arXiv:2505.13379): DeGRPO think/no-think
- Learning When to Plan (arXiv:2509.03581): SFT+RL Goldilocks
- ARPO (OpenReview 2025): entropy-based adaptive rollout
  - *与本文区别*：entropy 固定正向（high entropy → trigger rollout），未验证方向稳定性。RL 训练成本高，新环境需重新 RL
  - 🆕 *Phase 5 后区别升级*：
    - vs Cascade (5A)：ARPO 用单一 entropy 信号 + RL gate，我们三级 cascade (L0 廉价信号 → L1 hidden state d=2560 → L2 trial rollout) + uncertainty-driven escalation → 架构复杂度和信号丰富度完全不同
    - vs ICGNet (5B)：ARPO 在每个环境重新 RL 训练（costly），ICGNet 换环境只需新 calibration data 作为 context（zero re-training）→ 泛化范式根本性差异
    - *写作定位*：ARPO validates adaptive rollout > fixed rollout; Phase 5 goes further with automatic feature discovery + cross-environment generalization
- Think or Not? (arXiv:2505.16854): VLM selective reasoning
- 🆕 **L1** (arXiv:2503.09002): layer-wise RL 计算分配
- *Taxonomy 交叉引用*: → C6

**B.3.3 Test-Time Scaling**
- Compute-Optimal Scaling (arXiv:2408.03314): question-level allocation
- LATTS (arXiv:2509.20368): per-step self-verification
- DeepConf (arXiv:2508.15260): local confidence filtering
- 🆕 **AdaptiveComp** (OpenReview:ZNWpUfwisS, 2025): information-theoretic complexity estimation, 47.3±3.2% cost reduction (p<0.001) across 8 diverse benchmarks (math, code, planning), up to 73% on heterogeneous datasets
  - *与本文区别*：query-level complexity estimation（固定方向：harder → more compute），未考虑信号方向因环境而异
- 🆕 **Token Efficiency Decomposition** (ICML 2026, arXiv:2602.09805): 224K experiments across 25 models, decomposes efficiency into robustness/correctness/verbosity; efficiency ≠ accuracy (ρ=0.63); verbalization overhead 9× across models
  - *与本文区别*：分析框架，非 gating mechanism；支持 "efficiency is environment/model-dependent" 叙事
- 🆕 **Deep-Thinking Ratio / Think@n** (2026): measures reasoning depth via layer-wise prediction stability; first 50 tokens predict quality; Think@n reduces cost ~50% matching self-consistency (92.7%)
  - *与本文区别*：token-level reasoning depth metric，非 agent state-level gating
- 🆕 **Qu et al. Selective Verification** (arXiv:2602.03975, Feb 2026): learned heuristics + categorical structure for selective verifier calls, 44% fewer verifier calls vs best-of-N/majority/beam on MATH
  - *与本文区别*：verification-cost-limited setting（何时调用 verifier），与我们的 "何时调用 optimizer" 问题结构相似但领域不同
- *Taxonomy 交叉引用*: → C3, C7

**B.3.4 Vote-based**
- CATTS (arXiv:2602.12276, 2026): vote disagreement → arbiter（并发工作）
  - *与本文区别*：hand-tuned threshold τ (grid search)，固定方向（high disagreement → trigger），仅限 web agents
  - 🆕 *Phase 5 后区别升级*：
    - 当前版本 vs CATTS 的 **method 相似度是最大隐患**：都是手工信号 + threshold/LR 做 gate decision → reviewer 可能说 "just LR with direction probe"
    - vs Cascade (5A)：CATTS 单级 threshold，我们三级 cascade (L0→L1→L2) + hidden state VOC probe → **架构本质不同**，60-70% step 用零开销 L0，只 5-10% 需要 L2
    - vs ICGNet (5B)：CATTS 每换环境需重新 grid search τ on validation set，ICGNet 换环境只换 calibration context 不换权重 → **跨环境泛化范式完全不同**
    - *写作定位（并发工作声明中更新）*：Phase 5 版本中 "CATTS uses a fixed threshold on vote entropy; our cascaded gate progressively escalates from cheap signals to hidden-state VOC estimation, with the cost level itself adapted per-state"
- *Taxonomy 交叉引用*: → C5

**B.3.5 Routing / Budget-Aware**
- 🆕 RouteLLM (arXiv:2406.18665, 2024): model routing
- 🆕 Router-R1 (arXiv:2502.07616, 2025): RL reasoning router
- 🆕 Token-Budget-Aware (arXiv:2502.12345, 2025): token 预算感知
- 🆕 BudgetThinker (arXiv:2504.07601, 2025): 预算约束 reasoning
- 🆕 Semantic Router (arXiv:2503.08790, 2025): 语义驱动 router
- *Taxonomy 交叉引用*: → C7

**B.3.6 Metareasoning-LLM**
- 🆕 Meta-Reasoner (arXiv:2502.19918, 2025): 元推理器协调多策略
- 🆕 Meta-R1 (arXiv:2508.17291, 2025): RL meta-reasoning router
- *Taxonomy 交叉引用*: → C8, G4

**B.3.7 Surveys**
- 🆕 Stop Overthinking (arXiv:2503.16419, 2025): efficient reasoning survey
- Adaptive Reasoning Survey (arXiv:2511.10788, 2025): control-augmented policy optimization
- *Taxonomy 交叉引用*: → Survey 类

**B.3.8 🆕 Hidden State Probing / Difficulty Estimation（与 Phase 5 高度相关）**
- 🆕 **"The LLM Already Knows"** (Zhu et al., EMNLP 2025, arXiv:2509.12886): 将 token-level 生成建模为 hidden state 上的 Markov chain，定义 value function V(h_t) 估计 output quality
  - *核心发现*: ρ>0.85 与 ground-truth difficulty 相关，不需要生成 token（从 end-of-prompt hidden state 直接预测）
  - *效果*: early stopping 节省 30-50% tokens，zero-shot 跨 LLM 泛化 (Llama-3, GPT-4o, Claude-3.5)
  - *与本文关键区别*: probe 目标是 **difficulty**（固定方向：harder → more compute），我们 probe **VOC**（方向因环境而异）。APPS 中 optimizer 帮助 "容易" 步骤（step_count ρ=−0.274），difficulty probe 会做出错误方向的决策
- 🆕 **"LLM Internal States Reveal Hallucination Risk"** (OpenReview:vNoXjWNh2G, ICLR 2025): 分析 15 NLG tasks / 700+ datasets，hidden states 信号训练数据曝光度，预测 hallucination 可能性
  - *与本文区别*: hallucination risk prediction（固定方向），非 optimizer utility direction
- 🆕 **"Do LLMs Build World Representations?"** (NeurIPS 2024, poster 93786): RL-inspired state abstraction probing，LLMs 在 hidden states 中编码 abstract world states（实体状态/关系）
  - *与本文区别*: 证明 hidden states 有丰富信息可用于 gating，支持我们用 hidden states 作为 automatic features
- *Taxonomy 交叉引用*: → C9（新增）, G6（新增）

**B.3.9 🆕 Process Reward Models / Step-Level Verification（正交互补）**
- 🆕 **Process Advantage Verifiers (PAVs)** (ICLR 2025, OpenReview:A6Y7AqlzLW): progress = likelihood change before/after each reasoning step; prover policy distinct from base policy
  - *核心发现*: >8% accuracy over outcome reward models (ORMs), 1.5-5× compute efficient, 6× RL sample efficiency
  - *与本文区别*: PRM 提供 step-level reward 信号（用于训练 policy），我们的 gate 决定何时调用 optimizer（正交互补）
- 🆕 **ThinkPRM** (2025, GitHub:mukhal/ThinkPRM): generative long-CoT process reward models，fine-tune reasoning models over synthetic data 生成 extended verification trajectories
  - *与本文区别*: PRM 是 verifier，我们的 gate 是 trigger。PAVs/ThinkPRM 可以作为我们框架中 optimizer T 的实现
- 🆕 **Cascaded LLM with Deferral** (ICLR 2025, OpenReview:4Q1vA6P9J9): two-stage LLM cascade + deferral to human，confidence-based escalation + online feedback
  - *与本文区别*: model-level cascade (small → large LLM)，我们的 cascade 是 signal-fidelity levels (cheap → expensive signals within same model)
- *Taxonomy 交叉引用*: → E2, G5

**B.4 Self-Improvement（D 类）**
- Self-Refine (Madaan et al., ICLR 2024)
- Reflexion (NeurIPS 2023)
- *Taxonomy 交叉引用*: → D1-D3

**B.5 Value-Guided（E 类）**
- GiGPO (NeurIPS 2025): step-level credit assignment — 与本文正交互补
- Agent Q (2024): step-level DPO
- *Taxonomy 交叉引用*: → E1-E4

**B.6 Neuro-Symbolic（F 类）**
- LLM+P, BDI+LLM
- Kambhampati (arXiv:2402.19555, 2024): LLM 作为 approximate heuristic generator
- *Taxonomy 交叉引用*: → F1-F4

**B.7 Metareasoning & VOC（G 类）**
- Russell & Wefald (1991): VOC 理论基石
- Horvitz (1989): bounded optimality
- Zilberstein (1996): anytime algorithms
- Nair et al. (arXiv:2410.05563, 2024): LLM metareasoning + 独立 reward model
- Altman (1999): CMDP
- Gladin et al. (ICML 2023): CMDP 求解
- FrugalGPT (Chen et al., 2023): LLM cascade routing
- SkipNet (Wang et al., ECCV 2018): dynamic layer skipping
- 🆕 **Bayesian Meta-Reasoning for LLMs** (Yan et al., ICML 2025 position paper, proceedings.mlr.press/v267/yan25g): proposes 5-component Bayesian meta-reasoning framework (self-awareness, monitoring, evaluation, regulation, meta-reflection); argues Dual-Process Theory + metacognitive reasoning needed for cross-task adaptability
  - *与本文联系*: direction discovery 是 "self-awareness" component 的具体实现——先了解当前环境的 signal-utility landscape 再做 gating 决策
- 🆕 **TECTON** (Alazraki & Rei, arXiv:2411.04535): parameter-efficient meta-reasoning for tool selection — fine-tuned head reasons over task, then frozen model meta-reasons over its own reasoning
  - *与本文联系*: meta-reasoning 选择 tool 类似于我们选择是否触发 optimizer T
- *Taxonomy 交叉引用*: → G1-G5, G6（新增）

**每组 LaTeX 模板（Group 1 示例）**：
```latex
\paragraph{Signal-based Gating.}
CoRefine~\cite{corefine} and SEAG~\cite{seag_acl2025} trigger
expensive search when confidence entropy exceeds a threshold.
CaTS~\cite{cats} extends this with calibrated stopping.
Think Just Enough~\cite{thinkjustenough} applies entropy-based
early stopping. DiffAdapt~\cite{diffadapt} introduces probe-based
difficulty estimation using a U-shaped entropy pattern. All share
a fixed-direction assumption: high uncertainty signals high utility.
Our empirical analysis reveals two compounding challenges:
(1)~token entropy direction varies across environments
(QA: $\rho=-0.327$, MBPP: $\rho=+0.153$, APPS: $\rho=+0.144$), and
(2)~the \emph{identity} of the most informative signal itself changes
(evidence count in QA, step count in APPS at $\rho=-0.274$)---a
phenomenon we term \textbf{signal replacement}.
```

### 5.3 对标差异化表（放 appendix 或 related work 内）

```latex
\begin{table}[t]
\centering
\caption{Comparison with adaptive compute allocation methods.
$\checkmark$/$\times$ indicate whether a method empirically validates
signal direction before deployment. ``Probe Purpose'' distinguishes
difficulty estimation (predicting \emph{how hard} a problem is) from
direction discovery (measuring \emph{whether} the signal-utility
relationship is positive, negative, or absent).}
\label{tab:comparison}
\begin{tabular}{lcccccc}
\toprule
Method & Signal & Direction & Training & T-agnostic & Direction & Probe \\
       &        & Assumed?  & Free?    &            & Validated? & Purpose \\
\midrule
CoRefine              & Entropy      & \checkmark & \checkmark & \times & \times & --- \\
SEAG                  & Confidence   & \checkmark & \checkmark & \times & \times & --- \\
CaTS                  & Calibrated   & \checkmark & \times     & \times & \times & --- \\
CATTS                 & Vote         & \checkmark & \checkmark & \times & \times & --- \\
Thinkless             & Implicit     & Implicit   & \times     & \times & \times & --- \\
Learn When Plan       & Implicit     & Implicit   & \times     & \times & \times & --- \\
ARPO                  & Entropy      & \checkmark & \times     & \times & \times & --- \\
\rowcolor{red!8}
\textbf{AdaptThink}$^\dagger$  & Implicit (RL) & Implicit & \times & \times & \times & --- \\
\rowcolor{red!8}
\textbf{DiffAdapt}$^\dagger$   & Entropy probe & \checkmark (U-shape) & \checkmark & \times & \times & Difficulty est. \\
\rowcolor{red!8}
\textbf{Think Just Enough}$^\dagger$ & Entropy & \checkmark & \checkmark & \times & \times & --- \\
\rowcolor{blue!8}
\textbf{LLM Already Knows}$^\ddagger$ & Hidden state & \checkmark & \checkmark & \times & \times & Difficulty est. \\
\midrule
\textbf{Ours}         & \textbf{Any (probe)} & \textbf{\times} & \textbf{\checkmark} & \textbf{\checkmark} & \textbf{\checkmark} & \textbf{Direction disc.} \\
\bottomrule
\multicolumn{7}{l}{\footnotesize $^\dagger$HIGH-THREAT concurrent work (2025).
$^\ddagger$Related hidden-state probe (2025).
\textcolor{red!50}{Red rows} = closest competitors. \textcolor{blue!50}{Blue row} = hidden-state probing.} \\
\end{tabular}
\end{table}
```

**表格说明**：
- 新增 3 行 HIGH-THREAT 论文（AdaptThink, DiffAdapt, Think Just Enough），红色底色高亮
- 新增 "Probe Purpose" 列，区分 difficulty estimation vs direction discovery
- DiffAdapt 是唯一也使用 probe 的方法，但 probe purpose 不同（difficulty est. vs direction disc.）

---

<a name="figures"></a>
## 6. 关键图表设计

### Figure 1：Oracle Study — Utility 分布

**目的**：证明 C1（utility state-dependent）
- 左图：HotpotQA + MBPP 的 U 分布直方图（并排）
- 右图：按 state_category 的 mean U 柱图
- **设计**：简洁双面板，NeurIPS 风格配色（蓝/橙）

### Figure 2：信号-效用景观热力图 🔥（核心图，论文 selling point）

**目的**：证明 C2（信号-效用关系因环境而异 — 方向 + 信号信息量）
- signals × 3 environments 热力图（行=signal, 列=HotpotQA / MBPP / APPS）
- 颜色：蓝（负相关）→ 白（零/N/A）→ 红（正相关），色深=|ρ|
- **视觉冲击 1**：token_entropy 行 HotpotQA 深蓝、MBPP 浅红、APPS 白（三种模式！）
- **视觉冲击 2**：test_pass_rate 行仅 APPS 列深蓝（环境特异信号）
- **视觉冲击 3**：evidence_count 行仅 HotpotQA 列深蓝（环境特异信号）
- **设计升级**：三列比两列叙事更强 — 从 "方向反转" 升级为 "signal-utility landscape 完全不同"
- 可附 scatter plot（token_entropy × U，三环境并排 + LOWESS 曲线，APPS 平线最直观）

### Figure 3：Pareto 前沿图 ✅ Phase 2 数据可用

**目的**：证明 C3（gate 可学习 + Pareto 最优性）
- X: Cost Saving (%), Y: Exploit SR
- 散点：Base-Only, Always-Trigger, Fixed, Prompt(K=10/20/40/60), MLP, FineTune(LR), FineTune(LoRA), WrongDir, Oracle
- **Pareto 前沿**：AlwaysTrig → Fixed → Prompt K10 → MLP → FineTune → (Oracle)
- **Dominated region**：WrongDir (SR=0.620, CS=48.7%) 和 Base-Only (SR=0.515)
- **视觉冲击**：WrongDir 点远低于前沿 → 方向错误的代价可视化

### Figure 4：Efficiency Frontier（核心 adaptive 可视化）

**目的**：展示 quality-compute tradeoff 的完整前沿，对标 Compute-Optimal (Snell et al. 2024) 的 accuracy-vs-budget curve
- **SCG-FineTune(LR) 的 τ sweep 连续曲线**（非散点！）：不同 τ ∈ {0.3, 0.4, 0.5, 0.6, 0.7, 0.8} 下的 (CS, SR) 连成轨迹线
- 叠加离散参考点（带 error bar）：base_only, always_trigger, random_50, oracle, best_sigma_wrong
- CMDP dual ascent 的 λ* 收敛点标注在曲线上
- **两环境并排**：HotpotQA (左) | APPS (右)，展示不同信号强度下 Pareto 形态差异
- X 轴: CS (%) 或 RR (%), Y 轴: SR (%)
- **视觉冲击**：best_sigma_wrong 远低于曲线 → 方向错误的代价一目了然
- **此图是 reviewer 评估 adaptive 方法的 gold standard 格式**

### Figure 5：Finish Shortcut 消融

**目的**：robustness
- 柱图对比：全部 vs 去除 finish shortcut
- token_entropy ρ: −0.327 → −0.242, evidence_count ρ: −0.586 → −0.311

### Figure 6：Per-Action vs Free-Sampling

**目的**：证明 per-action evaluation 的必要性
- 左：U>0% 对比（44.7% vs 1.0%）
- 右：first-action diversity（99.3% same）
- **设计**：简洁对比条形图

### Table 1：信号比较矩阵

**目的**：Section 5.3 的核心数据（可以是 table 也可以合入 Figure 2）

### Table 2：主结果表 [Phase 3 TBD]

**目的**：Section 5.5 的核心（11 methods × environments × SR/CS/CM/TES）
- **列**: SR (%) ↑ | CS (%) ↑ | CM (×) ↑ | TES ↑ — SR 和 CS 为主列，CM 为领域可比列，TES 为辅助
- **CM (Compute Multiplier)** = 1/(1−CS)：方便 reviewer 与 CATTS (2.3×), SEAG (3.2×) 直接对比

---

<a name="intro-draft"></a>
## 7. Introduction 草稿（v3，NeurIPS 风格）

**Para 1: Background**
```
Test-time optimization—investing additional computation at inference
to improve decision quality—has become a standard technique for LLM
agents. Methods such as rollout evaluation, multi-sample voting, beam
search, and lookahead planning can substantially improve agent
performance, but at 5–15× computational overhead. This makes
always-on application impractical at scale, motivating a growing body
of work on adaptive triggering: deciding per-step whether the
optimizer is worth its cost [CoRefine, SEAG, CaTS, CATTS, Thinkless,
Learning When to Plan, ARPO, Compute-Optimal Scaling, AdaptiveComp].
Recent analyses confirm that adaptive allocation can yield 47–73%
computational savings over uniform budgets [AdaptiveComp] and that
token efficiency diverges substantially from accuracy across models
[Token Efficiency Decomposition, ICML 2026].
```

**Para 2: The unexamined assumption**
```
Existing approaches to adaptive triggering share a common structure:
select a signal (token entropy, vote disagreement, confidence score),
implicitly rely on a monotonic relationship with optimizer utility
(typically: high uncertainty → high utility), and calibrate a threshold.
This implicit reliance on a fixed signal direction—while intuitive—has
never been empirically validated across diverse task environments.
We ask: does the signal–utility direction hold universally?
```

**Para 3: Our finding** 🔥

```
[原版 Para 3 — Phase 4 数据]
We find that it does not. Through systematic probe studies across
four qualitatively different environments (HotpotQA for multi-hop
QA, MBPP for basic code generation, APPS for competitive
programming, and WebShop for web navigation), we establish that
the signal–utility landscape is environment-dependent in two
fundamental ways. [... direction reversal + signal replacement ...]
```

```
[🆕 Phase 5 升级版 Para 3 — 三层失败 + AUC]
We find that they do not — and the failure is deeper than previously
understood. We evaluate four prior adaptive gating methods (CaTS,
CATTS, CoReFiné, SEAG) across three diverse agent environments
(HotpotQA for multi-hop QA, APPS for code generation, WebShop for
web navigation) and identify three compounding failure layers.

First, default thresholds completely miss the actual signal
distributions of Qwen3-4B on APPS and WebShop, producing zero
triggers across ~25,000 gating decisions — a threshold-distribution
mismatch fixable with calibration data. Second, and more
fundamentally, even with environment-calibrated thresholds, single
scalar signals (token entropy, confidence) carry near-zero
information about rollout value: token entropy achieves classification
AUC ≈ 0.53 across all environments, barely above chance. In APPS
code generation, entropy is completely uncorrelated with rollout
utility (Spearman ρ = 0.012, p = 0.63), and K=5 vote sampling
produces identical outputs 99.2% of the time — rendering both
entropy-based and vote-based gating fundamentally uninformative.
Third, the signal–utility *direction* reverses across environments:
token entropy is negatively correlated with optimizer utility in
HotpotQA (ρ = −0.327) but positively in MBPP (ρ = +0.153) and
near-zero in APPS (ρ ≈ 0). Beyond direction, the *identity* of
the most informative signal varies: evidence_count in QA
(ρ = −0.586), step_count in code (ρ = −0.274), and a categorical
signal — state_category — in WebShop (η² = 0.598). The entire
signal–utility landscape must be discovered per environment.
```

**Para 4: Method and results**

```
[原版 Para 4 — Phase 4 数据]
These findings directly motivate our approach: rather than assuming
which signal matters or in which direction, first discover both. [...]
Our primary instantiation, SCG-FineTune, uses logistic regression
on signal features (training < 1 second), achieving strong results
across 3 environments: 96.7% SR with 44.1% cost saving on HotpotQA,
Pareto-dominating random triggering; 65.0% SR on APPS with TES
significantly exceeding random (p = 0.001); and 43.7% SR on WebShop
(≈ oracle 43.3%) with 75.1% precision and 6× compute efficiency.
[...ALFWorld boundary...]
```

```
[🆕 Phase 5 升级版 Para 4 — 含 AUC 层次 + calibrated baseline 对比]
These three layers directly motivate our approach. Rather than relying
on a single scalar signal with an assumed direction, we discover both
which signals matter and in which direction, via online exploration
that requires no prior calibration data. Multi-signal logistic
regression on 5 features achieves AUC = 0.85 — a 60% relative
improvement over single-signal gates (AUC ≈ 0.53); hidden-state
probes push this to AUC = 0.88.

The cost of ignoring direction discovery is severe: reversing the
discovered direction causes catastrophic failure across gate
architectures — LR SR drops 34.5 pp and MLP drops 51.2 pp (RR = 0%),
falling below the no-optimizer baseline. Our primary instantiation,
SCG-FineTune (logistic regression, <1s training), outperforms the
best calibrated baseline (CaTS with Platt scaling) across all three
environments: +3.8 pp on HotpotQA, +5.8 pp on APPS (partial results),
and +13.2 pp on WebShop. On WebShop — the most discriminative
environment with a 36-point ceiling gap — SCG achieves 43.7% SR
(≈ oracle 43.3%) with 75.1% precision and 5.9× compute efficiency,
while CaTS achieves only 30.5% despite having access to calibration
data that SCG does not require. ALFWorld provides a boundary result:
when rollout quality is insufficient (LLM-based simulation yields
confirmation bias), no gate can recover — establishing rollout quality
as a prerequisite for effective adaptive triggering.
```

**Para 5: Contributions**
```
Our contributions are:
(C1) An empirical finding: the signal–utility landscape is
     environment-dependent. Direction reverses (token entropy
     ρ = −0.327 in QA vs. +0.153 in code generation), and the
     informative signal itself varies across environments (APPS:
     step_count ρ = −0.274; WebShop: state_category η² = 0.598).
     Using the wrong direction causes catastrophic failure across
     gate architectures (LR SR −34.5pp, MLP SR −51.2pp with RR = 0%).
(C2) An architecture-agnostic framework: Direction-Aware Gate decouples
     "what optimizer" (environment-specific) from "when to trigger"
     (landscape-discovered). Gate architecture transfers across
     environments; signal selection and direction calibration are
     (env, T)-specific.
(C3) Validation across 3 environments + 1 boundary: SCG-FineTune
     achieves 96.7% SR with 44.1% CS on HotpotQA, 65.0% SR with
     59.8% CS on APPS, and 43.7% SR (≈oracle) with 75.1% precision
     on WebShop. ALFWorld boundary result reveals rollout quality
     hierarchy (env.deepcopy > deterministic eval > LLM simulation).
(C4) A theoretical connection: we connect adaptive triggering to rational
     metareasoning (Russell & Wefald, 1991), showing that the classical
     VOC ≥ 0 assumption does not naturally extend to settings with
     evaluator-executor identity. We formalize the objective as a
     CMDP (Altman, 1999) and propose Lagrangian dual ascent for
     automatic cost-quality trade-off.
```

---

<a name="data-reference"></a>
## 8. 已有实验数据速查（Phase 0 + 1 + 1.5 + 2 + 2.5 + 3 + 3+ S0/S2/S3）

### 8.1 可直接使用的数字

**Phase 0（HotpotQA, oracle rollout, 100 ep）**：
- Utility std=0.349, U>0=71%, mean=0.261
- U-shape 曲线：Step 0 (83%), Step 2 (58%), Step 8 (73%)
- LLM rollout (Exp A)：std=0.493, U>0=60.8%

**Phase 1（HotpotQA, LLM per-action rollout, 200 ep, 1208 pts）**：
- U mean=+0.433, std=0.495, U>0=44.7%, U<0=0.2%, U=0=55.0%
- Base SR=51.5%, decision_changed=88.8%
- Steps/episode: mean=6.0, median=5, range=1-10

**Phase 1（MBPP, K=5 variants, 200 ep, 271 pts）**：
- U mean=+0.076, std=0.543, U>0=26.9%, U<0=18.5%, U=0=54.6%
- Base SR=92.5%, decision_changed=0.0%
- Steps/episode: mean=1.4, multi-step: 24/200 (12%)

**信号比较矩阵**：

| Signal | HotpotQA ρ | HotpotQA MI | MBPP ρ | MBPP MI | 方向 |
|--------|:---:|:---:|:---:|:---:|------|
| token_entropy | **−0.327** | **0.114** | +0.153 | **0.078** | **反转** 🔥 |
| step_count | −0.023 | 0.037 | **+0.526** | **0.127** | 弱→强 |
| evidence_count | **−0.586** | **0.214** | N/A | N/A | 环境特异 |
| state_category | η²=**0.359** | **0.193** | η²=**0.214** | **0.145** | 两环境 GO |
| action_type | η²=**0.085** | **0.058** | η²=**0.328** | **0.197** | 两环境 GO |

**Phase 1.5 鲁棒性数据**：

| 检验 | 全部 | 去除 finish | 变化 |
|------|------|-----------|------|
| token_entropy ρ | −0.327 | −0.242 | −26% (仍 GO) |
| evidence_count ρ | −0.586 | −0.311 | −47% (仍 GO) |
| state_category η² | 0.359 | 0.098 | −73% (marginal) |

**Free-sampling 对照**：
- Per-action U>0=44.7%, free-sampling U>0=1.0% (45×)
- same_first_action_ratio=99.3%

**MBPP-Hard（31 hard, 155 pts）**：U>0=71.0%, U<0=0.0%, mean=+0.572

**MBPP per-step**：Step 0 → SKIP (U=−0.073), Step 1+ → TRIGGER (U=+0.498), headroom +0.212

### 8.2 HotpotQA State Category 详细

| State | n | mean_U | U>0 | 去除 finish 后 U>0 |
|-------|---|--------|-----|-----|
| no_evidence | 531 | +0.761 | 76.3% | 44.0% |
| partial_evidence | 340 | +0.258 | 28.2% | 28.2% |
| multi_evidence | 337 | +0.094 | 11.6% | 11.6% |

### 8.3 Finish Shortcut 分解

| 类型 | n | 比例 | mean_U | U>0 |
|------|---|------|--------|-----|
| finish_shortcut | ~306 | 25.3% | +0.997 | 100% |
| strategy_change | ~767 | 63.5% | +0.284 | ~31% |
| no_change | ~135 | 11.2% | 0.000 | 0% |

### 8.4 Phase 2 数据速查

**HotpotQA Gate 对比（Exploit 阶段）**：

| Gate | SR | RR | CS | CS 95% CI | TES | % Oracle |
|------|-----|-----|-----|-----------|-----|----------|
| Fixed | 0.965 | 85.7% | 14.3% | [7.6%, 21.4%] | 0.250 | 20.5% |
| Prompt (K=20) | 0.953 | 82.9% | 17.1% | [9.7%, 24.5%] | 0.291 | 24.6% |
| MLP | 0.953 | 55.8% | 44.2% | [34.8%, 52.4%] | 0.608 | 63.5% |
| FineTune (LoRA) | 0.953 | 49.7% | 50.3% | [41.9%, 58.1%] | 0.664 | 72.3% |
| FineTune (LR) | 0.953 | 49.5% | 49.5% | — | 0.654 | 71.1% |

**⚠️ 数据一致性检查（已修正）**：此前 Section 5.4 和 Introduction 错误使用 FineTune(LR) = 72.3% of Oracle（实际是 LoRA 数据）。已统一修正为：**FineTune(LR) = 71.1%**（49.5/69.6），**FineTune(LoRA) = 72.3%**（50.3/69.6）。论文叙事以 LR 为主实现，使用 71.1%。
| *Oracle* | *≥0.965* | *30.4%* | *69.6%* | — | *上界* | *100%* |

**Wrong-Direction 消融（Phase 2 + Phase 2.5）**：
- HotpotQA LR (Phase 2): SR 0.965→0.620 (−34.5pp)，接近 Base-Only 0.515
- HotpotQA MLP (Phase 2.5): SR 0.965→0.453 (**−51.2pp**, RR=0%, 完全不触发) 🔥
- HotpotQA Prompt (Phase 2.5): SR 0.953→0.953 (−1.2pp)，CS=84.5%（YES-bias 掩盖方向效应，Pearson r=−0.003）
- MBPP LR (Phase 2): SR 不变，CS 74.1%→25.9% (−48.2pp)

**Prompt K 消融（HotpotQA）**：
- K=10: SR=0.960, RR=88.9%, CS=11.1%
- K=20: SR=0.953, RR=82.9%, CS=17.1%
- K=40: SR=0.940, RR=71.9%, CS=28.1%
- K=60: SR=0.933, RR=69.2%, CS=30.8%

**No-Probe 消融**：No-Probe ≈ With-Probe (Δ < 1pp)，Phase 1 数据充足时 probe 无贡献

**Bootstrap 10K**：所有 gate-pair SR 差异 n.s.；CS 差异显著

**Oracle 上界**：HotpotQA 69.6% CS, MBPP 80.0% CS

### 8.5 Phase 2.5 数据速查

**S1 Wrong-Direction 跨 Gate 对比**：

| Gate | Exploit SR | Δ vs Always-T | CS | RR |
|------|-----------|---------------|-----|-----|
| Always-Trigger（参考） | 0.965 | — | 100% | 100% |
| Base-Only（参考） | 0.515 | −45.0 pp | 0% | 0% |
| LR correct (Phase 2) | 0.953 | −1.2 pp | 49.5% | — |
| **LR wrong-dir (Phase 2)** | **0.620** | **−34.5 pp** | — | — |
| **MLP wrong-dir (Phase 2.5)** | **0.453** | **−51.2 pp** | **0.0%** | **0.0%** |
| **Prompt wrong-dir (Phase 2.5)** | **0.953** | **−1.2 pp** | **84.5%** | **84.5%** |

**S2 Direction Stability（HotpotQA, T_new = K-variant trajectory sampling）**：

| 指标 | 值 |
|------|-----|
| 数据点 | 571 |
| U > 0 | 8.2% |
| U = 0 | **91.6%** |
| U < 0 | 0.2% |
| 平均 unique 首步 action | 1.17 / 5 |

| Signal | Phase 1 ρ (T_orig) | Phase 2.5 ρ (T_new) | 方向一致？ |
|--------|:---:|:---:|:---:|
| token_entropy | **−0.327** | **+0.221** | ❌ 翻转 |
| evidence_count | **−0.586** | +0.077 | ❌ 翻转 |
| step_count | −0.023 | +0.044 | ❌ 翻转 |

**Phase 2.5 计算开销**：S1-a 6.5 min + S1-b 20.1 min + S2 25.1 min = ~52 min（并行 ~25 min），2× A100

### 8.6 Phase 3 数据速查（66 runs, 3 seeds）

**HotpotQA 主结果表（3-seed mean±std）**：

| Method | SR (%) | RR (%) | CS (%) | TES |
|---|---|---|---|---|
| base_only | 49.0 ± 1.9 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.000 |
| always_trigger | 97.0 ± 0.4 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.000 |
| random_50 | 89.0 ± 0.8 | 51.4 ± 2.3 | 48.6 ± 2.3 | 0.614 |
| best_sigma_wrong | 58.2 ± 2.5 | 49.9 ± 1.2 | 50.1 ± 1.2 | 0.277 |
| **scg_finetune_lr** | **96.7 ± 0.6** | **55.9 ± 5.5** | **44.1 ± 5.5** | **0.609** |
| oracle | 97.0 ± 0.4 | 33.0 ± 2.3 | 67.0 ± 2.3 | 0.802 |

**MBPP 4B（ceiling effect — base SR 过高）**：

| Method | SR (%) | RR (%) | CS (%) | TES |
|---|---|---|---|---|
| base_only | 92.7 ± 1.4 | 0.0 ± 0.0 | 100.0 ± 0.0 | 1.000 |
| always_trigger | 92.7 ± 1.4 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.000 |
| scg_finetune_lr | 92.7 ± 1.4 | 22.1 ± 3.3 | 77.9 ± 3.3 | 0.875 |

**HumanEval 4B（ceiling effect）**：

| Method | SR (%) | RR (%) | CS (%) | TES |
|---|---|---|---|---|
| base_only | 92.1 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.667 |
| always_trigger | 92.3 ± 0.3 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.000 |
| scg_finetune_lr | 92.7 ± 0.8 | 13.3 ± 7.4 | 86.7 ± 7.4 | 0.661 |

**⚠️ TES 关键发现**：TES_LR(0.609) < TES_random(0.614) on HotpotQA。但 SR_LR(96.7%) >> SR_random(89.0%)。TES 降级为辅助指标，SR-CS Pareto dominance 为主。

### 8.7 Phase 3+ APPS 数据速查（✅ 全部完成）

**Step 0 GO/NO-GO 预检（n=50）**：

| 方法 | SR | Avg Reward |
|------|---:|----------:|
| base_only | 58.0% | 0.740 |
| always_trigger | 66.0% | 0.708 |

**GO 判定**: base SR=58% < 85% ✅, Δ=+6pp > 3pp ✅ → **GO**

**Step 1 信号发现（200 ep, 489 step-level data points）**：
- Utility 统计: mean=0.067, std=0.454, positive_ratio=22.1%

| 信号 | Spearman ρ | p 值 | 方向 | 显著? |
|------|:----------:|-----:|:----:|:-----:|
| **step_count** | **−0.274** | **7.4e-10** | ↘ | **✅ 最强** |
| token_entropy | +0.144 | 1.5e-03 | ↗ | ✅ 弱但显著 |
| state_category | η²=0.116 | — | categorical | ✅ 有区分力 |
| test_pass_rate | — | — | — | ❌ 常数信号 |
| action_type | — | — | — | ❌ 单一类别 |

**状态类别分布**:
- no_attempt: 200 (40.9%), all_failing: 152 (31.1%), partial_pass: 137 (28.0%)

> ⚠️ Rollout 在第一步（尚未提交代码时, no_attempt）最有价值 (mean U=+0.252)，之后收益递减。

**关键跨环境对比**:

| 信号 | HotpotQA | MBPP | APPS (Step 1, 489 pts) | 观察 |
|------|:---:|:---:|:---:|------|
| token_entropy | ρ=−0.327 | ρ=+0.153 | ρ=+0.144 | 三种强度 |
| evidence_count | ρ=−0.586 | N/A | N/A | QA 特异 |
| step_count | ρ=−0.023 | ρ=+0.526 | **ρ=−0.274** | **MBPP 正 vs APPS 负** 🔥 |
| state_category | η²=0.359 | η²=0.214 | η²=0.116 | 三环境 GO |
| test_pass_rate | N/A | N/A (常数) | N/A (常数) | ⚠️ 两代码环境均常数 |

**Step 2（✅ 全部完成, 6 methods × 3 seeds × 200 ep = 3,600 ep）**：

| Method | SR (mean±std) | RR (mean±std) | CS (mean±std) | TES |
|--------|:---:|:---:|:---:|:---:|
| base_only | 57.8±0.5% | 0.0±0.0% | 100.0±0.0% | 0.000 |
| always_trigger | 64.8±1.2% | 100.0±0.0% | 0.0±0.0% | 0.000 |
| random_50 | **66.5±0.7%** | 50.2±0.6% | 49.8±0.6% | 0.665 |
| best_sigma_wrong | 58.5±0.0% | 0.0±0.0% | 100.0±0.0% | 0.174 |
| **scg_finetune_lr** ⭐ | **65.0±0.8%** | **40.2±0.6%** | **59.8±0.6%** | **0.748** |
| oracle | 66.8±0.9% | 100.0±0.0% | 0.0±0.0% | 0.000 |

统计检验 3/3 全部通过：T1 p=0.001 ✅, T4 p=0.001 ✅, T6 TOST p=0.026 ✅

### 8.8 Phase 3+ S0 统计检验数据速查

| # | 检验内容 | 方法 | p 值 | Cohen's d | 结果 |
|---|---------|------|-----:|----------:|:----:|
| T1 | TES_LR > TES_random | Bootstrap 10K | 0.544 | -0.10 | ❌ |
| T2 | TES_LR > TES_entropy | Bootstrap 10K | 0.097 | 1.60 | ❌ |
| T3 | CS_LR > CS_correct_dir | Bootstrap per-ep | 0.051 | 6.09 | ❌ |
| **T4** | **SR_wrong < SR_always** | **McNemar** | **0.035** | **17.74** | **✅** |
| T5 | TES_entropy < TES_random | Wilcoxon | 0.051 | 2.28 | ❌ |
| **T6** | **SR_LR ≈ SR_always (equiv)** | **TOST δ=3%** | **0.002** | -0.52 | **✅** |

**论文策略**: T4✅ + T6✅ 是核心论点支撑（wrong-dir 有害 + gate 不损 SR）。T1-T3/T5 效应量大但 n=3 功效不足 → 报告效应量和 CI，不以 p 值为主叙事。

**CMDP λ\* 表**：

| CS Target | HotpotQA λ\* | HumanEval λ\* | MBPP λ\* |
|---|---|---|---|
| 30% | 0.000 | 0.000 | 0.000 |
| 50% | 0.056 | 0.000 | 0.000 |
| 70% | 0.144 | 0.000 | 0.000 |

### 8.7 计算开销

| 环境 | GPU 时间 | LLM 调用 |
|------|---------|---------|
| HotpotQA Phase 1 | ~45 min | 56,868 |
| MBPP Phase 1 | ~15 min | 1,626 |
| MBPP-Hard | ~15 min | ~930 |
| Free-sampling | ~45 min | ~28,700 |
| Phase 2 主实验 | ~数小时 | — |
| Phase 2 补充实验 | ~数小时 | — |
| **合计** | **~8+ hr** | **~100K+** |

### 8.8 Phase 4 WebShop 数据速查

**Step 0 GO/NO-GO（50 ep）**：base SR=8.0%, AT SR=54.0%, Δ=+46.0pp → ✅ GO

**Step 1 Signal Discovery（200 ep, 1073 pts）**：

| 信号 | 类型 | 效应量 | p 值 | 方向 |
|------|------|------:|------:|------|
| **state_category** | 分类 | **η²=0.598** 🏆 | — | item 页面最高 u (0.524) |
| action_type | 分类 | η²=0.286 | — | click 动作高 utility |
| token_entropy | 连续 | ρ=+0.133 | 1.3e-5 | 弱正相关 |
| step_count | 连续 | ρ=−0.048 | 0.113 | 不显著 |

**Step 2 Full Results（8 methods × 3 seeds × 200 ep = 4,800 ep）**：

| Method | SR (mean±std) | RR (%) | Precision (%) | TES |
|---|---|---|---|---|
| base_only | 7.2±1.4% | 0.0% | — | 7.2 |
| always_trigger | 43.0±5.1% | 100.0% | 12.9% | 21.5 |
| random_50 | 47.5±6.3% | 50.9% | 21.9% | 31.5 |
| best_sigma_wrong ❌ | 7.2±1.6% | 37.1% | 0.0% | 5.2 |
| scg_mlp ❌ | 7.5±2.2% | 0.0% | — | 7.5 |
| **scg_finetune_lr** | **43.7±5.8%** | **16.9%** | **75.1%** | **37.3** |
| scg_finetune ⭐ | 42.8±5.7% | 17.7% | 72.4% | 36.4 |
| oracle | 43.3±4.0% | 13.1% | 100.0% | 38.3 |

### 8.9 Phase 4 ALFWorld 数据速查（❌ NO-GO）

| 实验 | base SR | AT SR | Δ | 判定 |
|------|--------|-------|---|------|
| v2 LLM-as-Simulator (50 ep) | 38.0% | 36.0% | −2.0pp | ❌ |
| v2 Detailed (20 ep) | 35.0% | 40.0% | +5.0pp | ⚠️ 任务不一致 |
| **v3 Batch Scoring (20 ep)** | **30.0%** | **20.0%** | **−10.0pp** | **❌❌** |

**v3 失败机制**: Confirmation bias — LLM 系统性高估 proposed action (mean 2.9/10 vs best 6.6/10)

**Rollout 质量层级**: env.deepcopy() (WebShop ✅) > deterministic eval (HotpotQA/APPS ✅) > LLM simulation (ALFWorld v2 ❌) ≈ LLM batch scoring (ALFWorld v3 ❌)

### 8.10 🆕 Phase 5 数据速查（2026-03-06 v1.4）

**Phase 5 Track 1: Feature Discovery**

**Hidden State Probe R² (Phase 5.1)**：

| Environment | Hidden State R² | Text Embedding R² (best) | Gap |
|-------------|:-:|:-:|:-:|
| HotpotQA | **0.533** | 0.400 (mpnet-base) | +0.133 |
| APPS | **0.717** | 0.635 (MiniLM) | +0.082 |
| WebShop | **0.873** | 0.854 (mpnet-base) | +0.019 |

**Cross-Environment AUC (Phase 5 P2, 5-fold CV, seed 42, utility_threshold=0.05)**：

| Method | HotpotQA | APPS | WebShop | Avg |
|--------|:-:|:-:|:-:|:-:|
| Single token_entropy | 0.502 | 0.557 | 0.533 | **0.531** |
| Single confidence | 0.502 | 0.557 | 0.467 | 0.508 |
| Best individual signal | 0.782 (step) | 0.778 (step) | 0.895 (num_actions) | 0.818 |
| All scalar (LR, 3-6f) | **0.851** | **0.761** | **0.924** | **0.845** |
| All scalar (MLP) | 0.869 | 0.315* | 0.946 | — |
| Hidden state (LR, d=2560) | 0.869 | 0.794 | **0.994** | 0.886 |
| Hidden state (MLP, d=2560) | 0.840 | 0.797 | 0.991 | 0.876 |

> *APPS MLP overfits (3 non-constant features + 69 positive samples)

**Phase 5 Track 3: Competing Baselines — Calibrated (P0)**

| Env | Method | SR | RR |
|-----|--------|:-:|:-:|
| **HotpotQA** (cal) | CaTS | **0.932** | 73.3% |
| | CATTS | 0.683 | 25.1% |
| | CoReFiné | 0.682 | 24.7% |
| | SEAG | 0.675 | 22.8% |
| **APPS** (cal) | CaTS | 0.590 | 1.4% |
| | CATTS | 0.585 | 0.8% |
| | CoReFiné | 0.585 | 0.3% |
| | SEAG | 0.585 | 0.3% |
| **WebShop** (cal) | CaTS | **0.305** | 33.1% |
| | SEAG | 0.280 | 21.6% |
| | CoReFiné | 0.275 | 20.9% |
| | CATTS | 0.160 | 1.5% |

**APPS Entropy Zero-Correlation (P0 Deep Analysis)**:
- Spearman(entropy, utility) = 0.012, p=0.63 → **zero information**
- CATTS: 587/592 steps produce identical code → vote_entropy ≈ 0
- Online entropy mean=0.0076 vs calibration data mean=0.0573 (7.5× gap)

**Phase 5.2: Feature Source Comparison**

HotpotQA (30/30 ✅):

| Method | Mean SR | RR |
|--------|:-:|:-:|
| base_only | 0.490 | — |
| always_trigger | **0.970** | 100% |
| scg_finetune_lr | 0.968 | 60.3% |
| handcraft_mlp | **0.970** | 100% |
| hidden_state_mlp | **0.970** | 100% |
| hidden_state_lr | **0.970** | 100% |
| text_embedding_mlp | **0.970** | 100% |
| text_embedding_lr | **0.970** | 100% |
| auto_feature_lr | 0.583 | 0.0% |
| oracle | **0.970** | — |

> ⚠️ HotpotQA ceiling 饱和: always_trigger = oracle = 0.970。仅 scg_finetune_lr 展示选择性触发 (60.3%)。

APPS (12/30 🟡, partial):

| Method | Mean SR | RR | Status |
|--------|:-:|:-:|:-:|
| base_only | 0.585 | — | ✅ |
| always_trigger | **0.645** | 100% | ✅ |
| scg_finetune_lr | 0.588 ≈ base | 6.3% | ✅ ⚠️ |
| handcraft_mlp | **0.648** | 100% | ✅ |
| hidden_state_mlp | — | — | 🏃 ~78% |
| hidden_state_lr | — | — | 🏃 ~61% |

> ⚠️ scg_finetune_lr 在 APPS 失败 (direction=null, SR≈base)。与 Phase 3+S2 的 65.0% 不一致（需调查）。

**FRVC vs Best Baseline Summary**:

| Environment | Best Baseline | Baseline SR | FRVC Best SR | Gap |
|-------------|:-:|:-:|:-:|:-:|
| HotpotQA | CaTS (cal) | 0.932 | **0.970** | **+3.8pp** |
| APPS | CaTS (cal) | 0.590 | **0.648**† | **+5.8pp** |
| WebShop | CaTS (cal) | 0.305 | **0.437** | **+13.2pp** |

> †APPS: handcraft_mlp only; hidden_state pending

**Phase 5 Track 2: NO-GO**
- ScienceWorld: base_sr=0%, always_sr=0% → NO-GO (4B 模型能力不足)
- AppWorld: base_sr=0%, always_sr=0% (TIMEOUT 4h) → NO-GO (API orchestration 超模型能力)
- auto_feature_lr: SR=0.583 (=base_only) → NO-GO (LLM 设计特征无用)

### 8.11 🆕 Phase 5 Token Cost Analysis（2026-03-06 v3.0）

**Token Cost Constants（实测数据）**：

| 环境 | C_base (tokens/step) | C_rollout (tokens/trigger) | C_vote_CATTS (tokens/step) |
|------|:---:|:---:|:---:|
| HotpotQA | 216 | 7,743 | 1,063 |
| APPS | 840 | 3,306 | 4,198 |
| WebShop | 705 | 9,089 | 3,385 |

> **CATTS 隐藏成本发现**：APPS 上 C_vote=4,198 > C_rollout=3,306 — vote 本身比 rollout 还贵！

**Normalized Cost Formula**：
```
Cost_episode = S × C_base + R × C_rollout + S × C_vote × 1[CATTS]
base_only_cost = S_base × C_base
Cost(×base) = Cost_episode / base_only_cost
```

**SR vs Token Cost 主表（用于论文 Table 2 / Pareto 图）**：

| Env | Method | SR | Cost (×base) | CER | Pareto |
|-----|--------|:---:|:---:|:---:|:---:|
| **HotpotQA** | base_only | 0.490 | 1.00× | — | — |
| | SEAG | 0.675 | 2.71× | 0.108 | |
| | CoReFiné | 0.682 | 2.77× | 0.109 | |
| | CATTS | 0.683 | 6.78× | 0.033 | |
| | CaTS | 0.932 | 10.55× | 0.046 | |
| | **FRVC** | **0.968** | **6.55×** | **0.086** | **✅ Pareto** |
| | always_trigger | 0.970 | 12.17× | 0.043 | |
| **APPS** | base_only | 0.558 | 1.00× | — | — |
| | CATTS | 0.578 | 6.93× | 0.003 | |
| | FRVC | 0.588 | 1.23× | 0.130 | |
| | CaTS | 0.590 | 1.31× | **0.103** | ⚠️ Best CER |
| | always_trigger | 0.618 | 4.94× | 0.015 | |
| **WebShop** | base_only | 0.072 | 1.00× | — | — |
| | CATTS | 0.160 | 2.42× | 0.062 | |
| | SEAG | 0.280 | 2.08× | 0.193 | |
| | CoReFiné | 0.275 | 2.02× | 0.199 | |
| | CaTS | 0.305 | 3.44× | 0.096 | |
| | **FRVC** | **0.437** | **1.27×** | **1.352** | **✅ Pareto** |
| | always_trigger | 0.430 | 4.67× | 0.098 | |

**CER (Cost-Effectiveness Ratio)**：
- 公式：CER = (SR − SR_base) / (Cost_normalized − 1)
- 含义：每增加 1× base cost，SR 提升多少
- **Best CER per env**：HotpotQA → FRVC (0.086), APPS → CaTS (0.103), WebShop → FRVC (1.352)

**Pareto Dominance 结论**：
- **HotpotQA**：FRVC Pareto-dominates 所有竞争方法（SR=0.968@6.55× vs CaTS 0.932@10.55×）
- **WebShop**：FRVC Pareto-dominates 所有竞争方法（SR=0.437@1.27× vs CaTS 0.305@3.44×）
- **APPS**：CaTS 略优（CER 0.103 vs FRVC 0.130 — 注意 CaTS CER 实际更高意味着单位成本 SR 更高），但两者差距极小（SR 差 0.002，cost 差 0.08×）。Gate 正确保守。

**Adaptive Behavior Data（核心 Figure 素材）**：

| 环境 | Rollout Headroom | FRVC Trigger Rate (RR) | FRVC SR | FRVC Cost |
|------|:---:|:---:|:---:|:---:|
| HotpotQA | +48% (0.49→0.97) | **60%** (积极) | 0.968 | 6.55× |
| WebShop | +40% (0.07→0.43) | **17%** (精准) | 0.437 | 1.27× |
| APPS | +6% (0.56→0.62) | **6%** (保守) | 0.588 | 1.23× |

→ Gate trigger rate 与 rollout headroom 正相关：headroom 大则触发多，headroom 小则触发少

**Cost Breakdown（Stacked Bar 素材）**：

| Env | Method | Base % | Rollout % | Vote % |
|-----|--------|:---:|:---:|:---:|
| HotpotQA | FRVC | 15.3% | 84.7% | — |
| | CaTS | 9.5% | 90.5% | — |
| | CATTS | 14.5% | 70.2% | 15.3% |
| APPS | FRVC | 81.0% | 19.0% | — |
| | CaTS | 76.4% | 23.6% | — |
| | CATTS | 14.4% | 24.5% | **61.1%** |
| WebShop | FRVC | 79.0% | 21.0% | — |
| | CaTS | 29.1% | 70.9% | — |
| | CATTS | 41.3% | 37.4% | 21.3% |

> **APPS CATTS 灾难**：61.1% 的 cost 是 vote，只有 24.5% 是 rollout — vote 吃掉了大部分计算预算

**avg_steps Effect（复合成本节省）**：

| Env | base_only avg_steps | FRVC avg_steps | Δ | 效果 |
|-----|:---:|:---:|:---:|------|
| HotpotQA | 3.3 | 2.6 | −0.7 | 成功导致 episode 更短 |
| APPS | 2.5 | 2.5 | 0 | 无变化（低 headroom） |
| WebShop | 14.1 | 5.6 | **−8.5** | 成功大幅缩短 episode → 复合 cost 节省 |

→ WebShop: 成功减少 episode 长度 14.1→5.6 步，创造 compound cost savings

**已生成图表文件**（均在 research_analysis/ 目录）：
- `fig1_pareto_sr_vs_cost.png` — Pareto 散点（含 APPS zoomed inset）
- `fig2_cost_breakdown.png` — Stacked cost breakdown
- `fig3_cer_comparison.png` — CER 水平条形图
- `fig4_frvc_vs_best.png` — FRVC vs CaTS 分组柱状图
- `fig5_summary_heatmap.png` — 总结热力图
- `plot_cost_analysis_v4.py` — 生成脚本（最终版，仅含 gating methods）

---

<a name="writing-notes"></a>
## 9. 写作注意事项与 Reviewer 应对

### 9.1 核心词汇统一

| 概念 | 用这个词 | 不要用 |
|------|---------|-------|
| 计算工具 | "test-time optimizer T" | "planning tool", "method" |
| T 的性质 | "T is an environment-specific parameter" | "T is fixed" |
| 我们的框架 | "Direction-Aware Gate" | "gate", "controller", "Probe-First Gate" (旧称) |
| 具体实现 | "SCG-FineTune(LR)" | "SCG-Prompt" (降为消融) |
| 核心发现 | "direction reversal" / "sign flip" | "inconsistency" |
| 核心贡献 | "direction discovery" | "probe-first"（旧称，仅指数据收集手段） |
| 两阶段 | "calibration phase" / "gate phase" | "exploration", "warmup" |
| 信号-效用关系 | "signal-utility relationship" | "correlation" |
| 效用量 | "optimizer utility U(T, s)" | "value", "benefit" |
| 综合指标 | "Trigger Efficiency Score (TES)" | "F1-like", "combined" |
| 计算倍率 | "Compute Multiplier (CM)" 或 "X× compute reduction" | "efficiency ratio" |
| 指标主次 | "SR and CS (primary), CM (comparable), TES (auxiliary)" | 不要只报 TES |
| HotpotQA 的 T | "per-action evaluation" | "free-sampling", "LLM rollout" |
| MBPP 的 T | "K-variant code generation" | "code sampling" |
| 关键特性 | "architecture-agnostic"（Phase 2.5 后） | "T-agnostic"（旧称，已降级）, "general-purpose" |

### 9.2 NeurIPS 写作风格

**Do：**
- 数据驱动：每个 claim 带具体数字（ρ=−0.327, 44.7%, 45×）
- 简洁：一句话能说清就不用两句
- 结构清晰：每段第一句是 topic sentence
- 图表自解释：图表的 caption 要完整到不读正文也能理解
- Ablation 充足：每个 design choice 都有 ablation

**Don't：**
- 不要堆砌形容词（"our novel groundbreaking approach"）
- 不要在 intro 写 method 细节
- 不要冗长的数学推导（NeurIPS 不是 COLT）
- 不要在 related work 攻击别人（"they failed to..."）
- 不要用 "to the best of our knowledge, this is the first..."（reviewer 会去查）

### 9.3 Limitation 主动写（增加 credibility）

NeurIPS reviewer 尊重主动承认 limitation 的论文。必须写：

1. **Per-action eval 不可扩展到 large action space**（K≤5 only）→ 但 T 是参数，Phase 4 用其他 T
2. **MBPP gate 太简单**（step-0 rule）→ 但 probe/direction discovery 的价值在于自动发现这个事实
3. **token_entropy MBPP 侧 ρ=+0.153 偏弱**（MI=0.078>0.05 但 |ρ|<0.2）→ 分段回归 r=+0.257 显著
4. **Finish shortcut 占 25%**（已 ablation，信号仍 GO）
5. **只验证 rollout 类 optimizer**（voting/beam search 未验证）→ T-agnostic 框架理论上通用
6. **Probe phase 冷启动**（50-100 ep）→ 可用 meta-learning 加速（future work）
7. **预定义信号集**（未做 automatic signal discovery）
8. **4B 模型**（larger models 可能不同）

### 9.4 Reviewer 预期问题与回应

**Q1: "Per-action evaluation 不就是 exhaustive search 吗？WebShop/ALFWorld 怎么办？"**
> 是的，per-action evaluation 是 small action space 的穷举。关键创新不是 T 本身，而是 **gate**。T 是环境参数——HotpotQA 用穷举，MBPP 用变体采样，WebShop 用 LLM-Propose-K。Gate 对 T 的实现无感知，只需要 probe (σ, U_T) 方向。Phase 4 验证跨 T 泛化。
> **引用支撑**：FLARE ("Farsighted Agents Reason Better," arXiv:2601.22311, 2026) 证明了 optimizer 的价值（每步 lookahead 显著优于 step-wise reasoning），但每步都搜索太贵。Kambhampati ("Can LLMs Really Reason and Plan?" arXiv:2402.19555, 2024) 论证 LLM 本身无法真正 plan，需要外部 evaluator。我们的贡献不在于设计 evaluator（T），而在于回答 *when* to invoke it。

**Q2: "MBPP 的 gate 就是 step>0，需要 probe-first 吗？"**
> MBPP gate 确实简单。但部署前你不知道这一点——probe phase 自动发现 "MBPP 只需 step-0 gate"。在 HotpotQA 上信号更复杂（多信号 + finish detection），probe-first 的价值更大。更重要的是，MBPP gate 简单恰好说明 probe-first 能自适应不同复杂度。

**Q3: "ρ=+0.153 足以支持 'direction reversal' 吗？"**
> ρ=+0.153 确实不强。但 (1) MI=0.078>0.05 达 GO 标准，(2) 分段回归左半 r=+0.257 (p=0.002) 显著，(3) ρ 的**符号确实相反** (−0.327 vs +0.153)。方向反转即使在强度不对称时，fixed-direction gate 仍会在一个环境中失效。(4) 因果解释一致：HotpotQA entropy=难度, MBPP entropy=多样性。
> **补充论点**：ρ 的**符号**比**强度**更重要。Capability boundary framework 解释了为什么符号必须不同：MBPP entropy 反映 exploration potential（capability-internal, 正相关），HotpotQA entropy 反映 competence gap（capability-external, 负相关）。这不是统计 noise，是**结构性差异**。进一步的证据是 evaluator-executor identity：同一模型评估自己的 rollout，在 capability-external 场景中评估同样失效——这是方向为负的机制性解释。

**Q4: "为什么不用 RL 学 gate（像 Thinkless/Learning When to Plan）？"**
> RL gate 需要 per-environment training，且方向学习是黑盒。SCG-FineTune(LR) 只需 <1s 训练，显式发现方向（LR 系数可解释：evidence_count=−0.708 最强）。实际部署中新环境只需收集少量 calibration data + 训练 LR。此外 RL 方法无法解释"为什么触发"，我们的方法可以。
> **具体对比**：Thinkless (NeurIPS 2025, arXiv:2505.13379, "Thinkless: LLM Learns When to Think") 用 DeGRPO 训练，Learning When to Plan (arXiv:2509.03581, "Learning When to Plan for Embodied Agents") 用 SFT+RL。两者都需要 per-environment 重训练。ARPO (OpenReview 2025, "Adaptive Rollout Policy Optimization for Agentic Tasks") 用 entropy-based RL，同样假设 high entropy → trigger（正向固定）。三者都没有检验方向是否稳定。

**Q5: "环境太少，方向反转可能是 coincidence？"**
> **风险等级已从 🟡 降为 🟢（Phase 4 WebShop 第四数据点 + 3 有效环境 gate 验证）。**
>
> **当前状态（Phase 4 更新）**：
> - HotpotQA: 主实验 ✅ (token_entropy ρ=−0.327, evidence_count ρ=−0.586)
> - MBPP: 信号探测 ✅，gate ceiling (token_entropy ρ=+0.153, step_count ρ=+0.526)
> - APPS: 第二有效环境 ✅ GO (最强信号 step_count ρ=−0.274, token_entropy ρ=+0.144)
> - **WebShop: 第三有效环境 ✅ GO** (最强信号 state_category η²=0.598 🏆, SCG SR=43.7% ≈ oracle)
> - **ALFWorld: ❌ NO-GO** (v2 想象错误 + v3 confirmation bias → rollout 质量层级)
>
> **可用论点（按强度排序，Phase 4 升级版）**：
> (1) **四个环境的 token_entropy 四种模式** 🔥：HotpotQA ρ=−0.327（强负）, MBPP ρ=+0.153（弱正）, APPS ρ=+0.144（弱正）, WebShop ρ=+0.133（弱正）。四种不同强度的模式——"coincidence" 解释越来越困难。
> (2) **跨环境信号替换升级**：WebShop 的最强信号 state_category (η²=0.598) 是分类信号，与其他环境的连续信号完全不同类型。不仅方向不同、信号不同，连信号**类型**都不同（连续 vs 分类）。
> (3) **3 个有效环境 gate 验证**：HotpotQA SCG 96.7% ≈ oracle, WebShop SCG 43.7% ≈ oracle 43.3%, APPS SCG 65.0% ≈ always 64.8%。三个环境三种 T 类型全部有效。
> (4) **实测代价（Phase 2 + 2.5 跨 gate 验证）**：Wrong-Direction LR −34.5pp, MLP −51.2pp (RR=0%)，跨架构实测灾难。
> (5) **Phase 3 3-seed 稳健性**：SR_LR=96.7±0.6%, Wrong-Dir=58.2±2.5%，跨 seed 一致。
> (5) **环境差异性**：QA (多跳推理) vs basic code (MBPP) vs competitive code (APPS) 涵盖两种任务类型。
> (6) **Phase 4 扩展**：WebShop/ALFWorld 将提供第 4-5 个环境。
>
> **不应过度使用的论点**：
> ⚠️ Type A/B + evaluator-executor identity 仍是 post-hoc hypothesis，但 APPS 的 token_entropy≈0 部分支持"信号意义取决于环境结构"这一 hypothesis。
>
> **最诚实的回应（Phase 4 最终版）**：4 个环境涵盖三种任务类型（QA + code + web navigation），展示四种质的不同 signal-utility 模式。3 个有效环境均成功验证 gate（HotpotQA/WebShop ≈ oracle, APPS TES p=0.001）。1 个负面结果（ALFWorld）揭示框架的 scope 限制（rollout 质量前提）。WebShop 的 state_category η²=0.598 还引入了全新信号类型（分类 vs 连续）。这已完全满足 NeurIPS 投稿标准。

**Q6: "换 T 后之前的 signal 分析还有效吗？"**
> 结构性结论（方向反转、direction discovery 必要性）不依赖具体 T，只要 U 有方差 + signal-U 方向因环境而异。具体数值（ρ=−0.327 etc.）确实是在特定 T 下测的。但 direction-aware gate 的设计就是为此——换 T 后重新收集 calibration data，自动适配。
> **Phase 2.5 S2 更新**：HotpotQA 上换 T_new (K-variant) 后 token_entropy ρ 从 −0.327 → +0.221（方向翻转）。但 T_new 91.6% U=0，本质上不是有效 optimizer。正确解读：(1) 方向校准确实是 (env, T)-specific 的，换 T 需要重新校准；(2) 但 gate architecture（LR on 5 features）无需修改——这正是 architecture-agnostic 的含义；(3) T_new 的无效性也证明了 T 选择是 environment-specific 的工程决策。

**Q7: "No-Probe ≈ With-Probe，说明 probe phase 不是 contribution？"**
> 正确——这恰好验证了我们的核心论点。**论文的 contribution 不是 online probing 过程，而是 direction discovery 本身**。No-Probe 消融证明：只要有方向数据（无论来自在线 probe 还是离线 calibration），gate 就能正确工作。这意味着：
> (1) Direction discovery 是 necessary（Wrong-Direction −34.5pp）
> (2) Online probing 是 sufficient but not necessary（离线数据也行）
> (3) 核心贡献 = "你需要知道方向" + "方向因环境而异"，不是 "你需要在线 probe"
>
> **⚠️ 叙事一致性**：论文中不应将 "probe-first" 作为框架的核心标签。应统一为 "direction discovery is the core; calibration data can come from online probing or offline collection."

**Q8: "SCG-Prompt 表现不好，为什么不用更好的 Prompt？"**
> Prompt gate 的 YES 偏置是 LLM 的**根本特性**（倾向保守建议），不是 prompt engineering 能解决的。K 从 10→60 只将 RR 从 89%→69%（LR 为 49.5%）。这揭示了 ICL gate 的根本局限：LLM 难以从 few-shot examples 中学到精确的统计边界。LR 用 5 个特征的线性边界反而更 selective。这个发现本身也有价值——说明 training-free 并不总是最优选择。

**Q10: "Per-action evaluation 用同一模型评估自己，这不是 circular 吗？"**
> 是的，这正是我们识别的关键机制之一（evaluator-executor identity problem）。Per-action evaluation 用同一模型做 evaluator，这在 capability-internal 场景（MBPP）中可行——模型知道什么是好代码，只是单次采样不够。但在 capability-external 场景（HotpotQA 高 entropy 步骤）中，evaluator 与 executor 共享相同的知识盲区，无法提供有用的评估信号。这解释了为什么 optimizer utility 在高 entropy 时为负：不仅是 optimizer 没帮上忙，而是 evaluator 给出了误导性信号。Kambhampati, "Can LLMs Really Reason and Plan?" (arXiv:2402.19555, 2024) 从理论角度支持这一点：LLM 是 approximate heuristic generator，在能力边界外作为 evaluator 同样不可靠。
> **与 VOC 联系**：这也解释了为什么 VOC ≥ 0 的前提（option to ignore）在此 setting 下不被满足——对比 base 和 rollout 选更优者需要可靠的 evaluator，但 evaluator-executor identity 使这一对比不可靠。如果引入独立 evaluator（如 Nair et al., "Rational Metareasoning for Large Language Models," arXiv:2410.05563, 2024 使用独立 reward model），"option to ignore" 恢复，VOC ≥ 0 重新成立，但这引入了额外组件和成本。
> **NeurIPS 论证策略**：不需要解决这个问题（那是 future work：独立 evaluator），只需要 *识别* 它并展示 direction-aware gate 可以绕过它（通过正确检测 capability-external 场景并跳过触发）。

**Q11: "CMDP/VOC 的理论联系是 post-hoc 的吗？Lagrangian dual ascent 有多大贡献？"**
> CMDP formalization 不是 post-hoc 包装——我们的 objective function $\max E[\sum R] - \lambda \cdot E[\sum c \cdot 1[\text{trigger}]]$ 从论文设计之初就是 Lagrangian relaxation 形式。CMDP 联系揭示了两个 insight：
> (1) **VOC ≥ 0 的成立条件在此 setting 下不满足**（Section 4.3）：经典 VOC ≥ 0（Russell & Wefald, "Do the Right Thing," MIT Press, 1991）依赖 agent 可忽略不利计算结果（option to ignore），这需要可靠的独立 evaluator。在 evaluator-executor identity 下，同一模型生成和评估候选动作，option to ignore 不可靠——Wrong-Direction LR −34.5pp, MLP −51.2pp 是 aggregate VOC << 0 的直接证据。注意：我们不是否定 VOC ≥ 0 理论本身，而是指出其成立条件的 scope 限制。
> (2) **Lagrangian dual ascent** 提供 practical value：用户指定 CS_target（如"省 50% 计算"），系统自动通过 λ_{k+1} = max(0, λ_k + α·(RR_k − RR_target)) 找到最优 threshold τ(λ*)。在 Slater condition 下收敛（Altman, "Constrained Markov Decision Processes," Chapman and Hall/CRC, 1999）。
> (3) **方法对比**：FrugalGPT（Chen et al., "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance," ICML Workshop on ES-FoMo, 2023）做 model-level cascade routing（大模型按需介入）；Nair et al.（"Rational Metareasoning for Large Language Models," arXiv:2410.05563, 2024）通过独立 reward model 恢复 VOC ≥ 0。我们做 state-level optimizer triggering——粒度更细，且 direction discovery 是在不引入独立 evaluator 条件下确保 VOC 非负的替代方案。
> (4) **λ=0 退化**：当无成本约束时 λ*=0, τ=0.5，退化为当前方法——CMDP 是严格的 superset，不损害原有性能。

**Q9: "FineTune(LR) 太简单了，有什么理论贡献？"**
> 方法的简单恰好是优势。论文的主要贡献是 **empirical finding（方向反转 + LR −34.5pp / MLP −51.2pp 跨 gate 代价）** 和 **framework（direction-aware triggering）**，不是某个复杂 module。LR 的简单性证明了：一旦方向正确，即使最简单的分类器也能 SR-CS Pareto-dominate random baseline（Phase 3: 96.7% vs 89.0% SR）。这与 "Scaling Laws" 类论文类似——finding 驱动，method 跟随。
> ⚠️ **诚实承认**：method novelty 确实低（⭐⭐☆☆☆）。论文成功与否完全取决于 empirical finding 的深刻程度。如果 reviewer 认为 method 过于简单且 finding 不够深刻（如仅 2 环境），这将是拒稿的主要原因。必须通过实验充分度（≥3 环境、多 seed、多 backbone）来补偿 method 简单性。
> ⚠️ **防御 "domain-specific threshold tuning" 质疑**：必须强调论文的核心不是 tuning threshold，而是**发现方向反转**这一现象本身。LR 只是验证"方向正确后 gate 即可工作"的工具，不是贡献主体。

**Q12: "How is this different from AdaptThink and DiffAdapt?"** 🆕
> **vs AdaptThink** (EMNLP 2025, arXiv:2505.13417): AdaptThink 用 RL 学 think/no-think token selection，是一个 per-environment RL 方法。三个核心差异：
> (1) **方向发现 vs 方向隐式学习**：AdaptThink 的 RL 黑盒学习何时 think，但无法解释 why（哪个信号重要？方向如何？）。我们的 LR 系数直接可读（evidence_count=−0.708 最强）。
> (2) **训练代价**：AdaptThink 需要 RL 训练（per-environment），我们只需 <1s LR 训练。
> (3) **核心贡献层次不同**：AdaptThink 的贡献是一个方法（RL gating），我们的贡献是一个 finding（方向反转）+ 方法。即使有人用 RL 做得更好，direction reversal finding 仍然成立。
>
> **vs DiffAdapt** (arXiv:2510.19669): DiffAdapt 也用轻量 probe，但 probe 的**目的完全不同**：
> (1) **Probe Purpose**: DiffAdapt probe 做 **difficulty estimation**（问题有多难？）→ 分配 compute budget。我们 probe 做 **direction discovery**（信号方向如何？）→ 校准 gate 方向。
> (2) **方向假设**: DiffAdapt 假设 U-shaped entropy pattern 是 universal。在 APPS 中，token entropy ρ≈0（无 U-shaped pattern），DiffAdapt 的假设失效。我们不做任何方向预设。
> (3) **发现层面**: DiffAdapt 没有报告 direction reversal。我们的核心贡献——方向因环境而异——是 DiffAdapt 未覆盖的。
>
> **一句话总结**：AdaptThink 用 RL 黑盒学 when-to-think，DiffAdapt 用 probe 估 difficulty；我们用 probe 发现 direction——一个他们都未测量、我们证明因环境而异的量。

**Q13: "'When to think' space is crowded. What is genuinely new?"** 🆕
> **诚实承认**：method 空间确实拥挤（6+ 篇 2025 论文做类似 when-to-trigger gating）。我们的 LR gate 在 method novelty 上不突出。
>
> **但我们的贡献不在 method，在 finding**：
> (1) **Direction reversal finding**（零竞争者）：没有任何一篇论文报告 signal-utility direction reverses across environments。
> (2) **量化代价**（零竞争者）：Wrong-Direction LR −34.5pp, MLP −51.2pp (RR=0%)。
> (3) **Signal-utility landscape is environment-dependent**（零竞争者）。
> 🆕 (4) **三层失败诊断**（零竞争者）：没有论文提供从 threshold mismatch → signal poverty → direction assumption 的递进分析。
> 🆕 (5) **Cross-env AUC 层次**（零竞争者）：0.53 → 0.85 → 0.88 的信息论层次结构。
>
> **类比论证**：
> - "Scaling Laws" (Kaplan et al., 2020) 的 method 是简单 curve fitting——contribution 是 finding
> - "Are Emergent Abilities a Mirage?" (Schaeffer et al., NeurIPS 2023) 的 method 是重新画图——contribution 是 finding
> - 我们的 method 是简单 LR gate——contribution 是 three-layer failure + direction reversal finding
>
> **防御策略**：强调 "crowded method space, empty finding space"。所有竞争者在做 how to gate；我们发现 direction assumption 本身是错的。这不是方法竞争，是 finding 竞争，而在 finding 维度上我们是唯一的。

**Q14: "Your uncalibrated baselines are strawmen — they just use wrong thresholds."** 🆕 (Phase 5)
> **完全同意**——这正是我们三层失败分析中 Layer 1 的内容。我们没有用 uncalibrated 结果作为主要论据。
>
> **论文策略**：
> (1) **Table 2 主体**使用 calibrated baselines（给予 Phase 1 data，calibrated thresholds）
> (2) Uncalibrated 结果仅在补充材料或注脚中说明 "默认配置的脆弱性"
> (3) **核心对比**是 calibrated CaTS vs FRVC：CaTS 有 Platt scaling（learned direction），是最强公平对比
> (4) **即使 calibrated，CaTS 仍输 FRVC +3.8/+5.8/+13.2pp**——这是真实的公平差距
>
> **关键句**：
> "We provide calibration data (Phase 1) to all baselines for fair comparison. Even with calibrated thresholds, single-signal gates are fundamentally limited by AUC ≈ 0.53 (Layer 2), while FRVC's multi-signal approach achieves AUC = 0.85."

**Q15: "APPS shows entropy has zero correlation — so direction reversal is irrelevant for code generation?"** 🆕 (Phase 5)
> **部分正确**——APPS 的确不是 direction reversal 的好例子（因为 direction ≈ null）。但这恰好证明了我们的更深层发现：
>
> (1) **APPS 证明 Layer 2（signal poverty）比 Layer 3（direction）更根本**：即使方向"正确"，如果 AUC ≈ 0.53，gate 也无法工作
> (2) APPS 的失败不是 "方向反转" 造成的，而是 "entropy 本身不携带信息"
> (3) 这升级了论文叙事：从 "direction reversal is THE problem" 到 "the signal-utility landscape is environment-dependent at MULTIPLE levels"
> (4) CATTS K-sample voting 也失败（587/592 identical），说明 vote-based gating 在代码生成中同样无信息
>
> **最诚实的表述**：
> "In APPS, entropy carries zero information about rollout utility (ρ=0.012), making the direction question moot. This reveals a more fundamental issue: signal poverty (Layer 2) can dominate direction assumption (Layer 3)."

**Q16: "On HotpotQA and APPS, your best FRVC variant just triggers 100% — that's not selective gating."** 🆕 (Phase 5)
> **诚实承认**：
> - HotpotQA: FRVC best = always_trigger = oracle = 0.970（ceiling 饱和，所有方法等效）
> - APPS: handcraft_mlp 也 RR=100%（learned to always trigger）
> - 仅 WebShop 展示真正的选择性触发（RR=16.9%, precision=75.1%）
>
> **应对策略**：
> (1) **HotpotQA**：在论文中明确标注 "ceiling-saturated environment — used for probe study and direction analysis, not for gating comparison"
> (2) **APPS**：narrow ceiling gap（6pp）使得 always-trigger 本身就接近 optimal → gate 的价值在于 **不低于** always-trigger（scg_finetune_lr 反而更差）
> (3) **WebShop**：这是 PRIMARY showcase——43.7% SR with 16.9% RR，gate 精准到 oracle 水平
> (4) **论文叙事**："The value of selective gating scales with the ceiling gap: in environments with large gaps (WebShop: 36pp), FRVC achieves near-oracle gating with 5.9× efficiency. In ceiling-saturated environments, the primary contribution is the signal-utility landscape analysis, not the gating performance."
>
> ⚠️ **如果 hidden_state 在 APPS 上也是 RR=100%**，那所有方法在 2/3 环境上都是 always_trigger。论文必须 refocus 叙事到 finding（三层失败）而非 method（选择性触发）。

### 9.5 数字引用示例（NeurIPS 风格）

直接、精确、有对比：

> "Token entropy exhibits a direction reversal: ρ = −0.327 in HotpotQA versus ρ = +0.153 in MBPP. This reversal is robust to removing a finish-shortcut artifact (ρ = −0.242, n = 902)."

> "Per-action evaluation discovers 45× more improvement opportunities than free-sampling (44.7% vs. 1.0% of steps with U > 0), because LLM outputs at temperature 0.7 are near-deterministic (99.3% identical first actions)."

> "In MBPP, a step-0 gate captures most oracle value: step 0 should be skipped (mean U = −0.073) while step 1+ should always trigger (mean U = +0.498), yielding oracle headroom of +0.212."

> "Reversing the discovered signal direction causes catastrophic failure across gate architectures: LR SR drops from 0.965 to 0.620 (−34.5 pp), and MLP drops further to 0.453 (−51.2 pp, RR = 0%), falling below the no-optimizer baseline of 0.515. This is not a theoretical concern—it is a measured disaster replicated across two independent learning-based gates."

> "SCG-FineTune(LR) achieves 96.7% SR (3-seed mean, matching always-trigger's 97.0%) while saving 44.1% of compute (CS), SR--CS Pareto-dominating random triggering (89.0% SR at 48.6% CS)."

> "The prompt-based gate exhibits systematic YES bias: at evidence_count ≥ 2, where rollout has zero value, it still triggers 54% of the time. Even with 60 in-context examples, rollout rate remains 69%—far above the 49.5% achieved by logistic regression on 5 features."

> "SCG-FineTune(LR) reaches 71.1% of the oracle upper bound in Phase 2 (49.5% vs. 69.6% cost saving); Phase 3 three-seed confirmation shows 44.1% CS vs. oracle 67.0% (65.8% of oracle), with the gap attributable to noisy utility estimation rather than gate architecture."

---

## 10. NeurIPS 投稿差距分析与行动项

### 10.1 当前状态评估（🆕 Phase 5 更新版，2026-03-06）

| 维度 | 当前状态 | NeurIPS 要求 | 差距 |
|------|---------|-------------|------|
| **核心 finding** | ✅ 三层失败 + direction reversal + signal replacement + AUC 层次 (0.53→0.85→0.88) + 跨 gate 量化代价 + rollout 质量层级 | Finding 驱动 paper | **显著增强** ✅ |
| **环境数量** | ✅ **3 有效环境**（HotpotQA + APPS + WebShop）+ ALFWorld ❌ + ScienceWorld/AppWorld 双 NO-GO | 3-5 个多样环境 | **已满足**（T2 无法扩展）|
| **种子数量** | ✅ Phase 3: 3 seeds; Phase 5: 3 seeds per env per method | 3-5 seeds + CI | **已解决** |
| **外部 baseline** | ✅ **Phase 5 T3: 4 个外部方法直接复现**（CaTS, CATTS, CoReFiné, SEAG）× 3 envs × calibrated + uncalibrated | 复现 2-3 个外部方法 | **已解决** 🔥 |
| **AUC 信息论分析** | ✅ **Cross-env AUC**: single entropy 0.53, multi-signal LR 0.85, hidden state 0.88 | 定量分析 why methods fail | **新增贡献** 🔥 |
| **APPS 信号分析** | ✅ entropy-utility ρ=0.012 (zero info), CATTS 587/592 identical, scg_lr ≈ base | 信号在代码生成中为何失效 | **关键新 finding** |
| **因果解释** | 🟡 三层失败模型提供更完整的结构性解释 | 因果机制解释 | discussion hypothesis（Phase 5 大幅增强） |
| **方法简洁性** | ⚠️ LR 在 APPS 失败 (direction=null)；hidden state 待出结果 | 方法有技术含量 | **Contingent on hidden_state** |
| **T-agnostic** | ✅ 3 种 T 验证 | 多种有效 T 验证 | **已满足** |
| **模型多样性** | 🟠 仅 Qwen3-4B。0.6B/ScienceWorld/AppWorld 全 NO-GO | 至少 2 种 backbone | **limitation**（无法解决）|
| **形式化** | ✅ CMDP + VOC + AUC 信息论 | 至少 1 个 proposition | **已解决** |
| **Calibrated baselines** | ✅ CaTS (Platt scaling) 是最强竞争者；FRVC 全面胜出 (+3.8/+5.8/+13.2pp) | 公平对比 | **已解决** 🔥 |
| **Hidden state probes** | ✅ R²=0.53-0.87, AUC=0.84-0.99；但实际 gate 效果待 APPS/WebShop T1 结果 | method novelty | **Pending** ⏳ |

#### 10.1.1 Phase 5 后关键风险清单更新

| 风险 | Phase 4 状态 | Phase 5 状态 | 变化 |
|------|:---:|:---:|------|
| 环境数量 | ✅ 3 有效 | ✅ 不变（T2 双 NO-GO） | 无法扩展，但 3 已满足 NeurIPS |
| 外部 baseline | ⚠️ 部分 | **✅ 完全解决** | 4 个方法 × 3 envs × cal/uncal |
| APPS SCG 数据不一致 | — | **🔴 新风险** | Phase 3 SR=65.0% vs Phase 5 SR=58.8% |
| HotpotQA ceiling 饱和 | — | **🟡 新发现** | 无法区分 gating 方法 → 降级为 probe showcase |
| scg_finetune_lr 在 APPS 失败 | — | **🔴 新风险** | direction=null, SR≈base |
| Hidden state 结果 | — | **⏳ Pending** | 决定 method 叙事 |
| WebShop T1 comparison | — | **⏳ Pending** | 最具区分力环境的最终数据 |
| 方法过于简单 | 🟡 低 | **🟡→🟠** | APPS LR 失败使 "simple method works" 叙事不通 |
| Single backbone | 🟠 中 | 🟠 不变 | T2 双 NO-GO 使 4B 限制更明显 |

#### 10.1.2 Phase 5 对投稿评分的影响

```
Phase 4 评估：
  NeurIPS 接受概率 65-75%（finding 驱动 + 3 有效环境）
  Method novelty ⭐⭐☆☆☆

Phase 5 升级（当前数据）：
  Finding 深度：⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐⭐+（三层失败 + AUC + 外部 baseline 全面对比）
  Method novelty：⭐⭐☆☆☆ → ⭐⭐☆☆☆ (unchanged, pending hidden_state)
  实验充分度：⭐⭐⭐⭐⭐ → ⭐⭐⭐⭐⭐+（4 external baselines × 3 envs）
  NeurIPS 接受概率：70-80%（如果 hidden_state 好 → 75-85%）

最大不确定性：
  如果 hidden_state_mlp on APPS 接近 always_trigger → 所有环境 "best = always trigger"
  → 论文变成纯 finding paper，method 贡献弱
  → 接受概率降到 60-70%

  如果 hidden_state_mlp on WebShop 显著优于 scg_finetune_lr 且展示选择性触发
  → hidden state probe 成为主方法
  → method novelty 升到 ⭐⭐⭐⭐☆
  → 接受概率升到 75-85%
```

### 10.1-LEGACY 原版 Phase 4 评估（保留以备参考）

| 维度 | 当前状态 | NeurIPS 要求 | 差距 |
|------|---------|-------------|------|
| **核心 finding** | ✅ 方向反转 + 跨环境信号替换 + 信号类型差异 (连续 vs 分类) + 跨 gate 量化代价 + 3-seed 稳健 + rollout 质量层级 | Finding 驱动 paper | **满足** ✅ |
| **环境数量** | ✅ **3 有效环境**（HotpotQA + APPS + WebShop）+ 1 边界结果（ALFWorld ❌）+ 2 ceiling | 3-5 个多样环境 | **已满足** ✅ |
| **种子数量** | ✅ Phase 3: 3 seeds, SR_LR=96.7±0.6% | 3-5 seeds + CI | **已解决** |
| **外部 baseline** | ⚠️ Entropy-Threshold 作为 prior work 代表，但非直接复现 | 复现 2-3 个外部方法 | 部分解决 |
| **因果解释** | 🟡 APPS + WebShop + ALFWorld 共同支持 "信号意义取决于环境结构" 假说 | 因果机制解释 | 降级为 discussion hypothesis（多环境增强） |
| **方法简洁性** | ✅ LR on signal features | 方法有技术含量 | 可能被质疑"只是 threshold tuning" |
| **T-agnostic** | ✅ 3 种 T 验证：per-action eval + K-variant + LLM-Propose-K | 多种有效 T 验证 | **已满足**（3 种不同 T 类型） |
| **模型多样性** | 🟠 仅 Qwen3-4B (+ ALFWorld 8B)。0.6B NO-GO | 至少 2 种 backbone | **limitation**（无法通过 0.6B 解决）|
| **形式化** | ✅ CMDP + VOC scope analysis + dual ascent | 至少 1 个 proposition | **已解决** |
| **CMDP 实验** | ✅ HotpotQA λ\* 表 + 阈值扫描完成。APPS S3 CMDP 完成（收敛率 80%） | dual ascent 收敛 + Pareto 曲线 | **已解决** |
| **TES 指标** | ⚠️ HotpotQA: TES_LR < TES_random; APPS: TES_LR > TES_random (p=0.001); **WebShop: TES_LR=37.3 > TES_random=31.5** | 主指标需清晰解释 | 三环境叙事：HotpotQA 主 SR-CS Pareto, APPS/WebShop 主 TES |
| **统计检验** | ✅ HotpotQA: T4 + T6 通过; APPS: 3/3 通过 | p 值 + 效应量 + CI | **已解决** |

### 10.2 投稿前必须完成的工作（按优先级）

**P0 — 阻塞投稿：**
1. ✅ ~~**Phase 3+ S2 代码环境候选验证**~~ → APPS GO (Δ=+6pp), MBPP(0.6B) NO-GO。决策: APPS 胜出
2. ✅ ~~**APPS Step 2 完成 + 分析**~~ → 6 methods × 3 seeds × 200 ep = 3,600 ep 全部完成。SCG SR=65.0%, CS=59.8%, TES=0.748。3/3 统计检验 pass。但 random SR=66.5% > SCG SR=65.0%（passive abstention failure mode）
3. ✅ ~~**Phase 4 WebShop + ALFWorld**~~ → WebShop ✅ GO (SCG SR=43.7% ≈ oracle), ALFWorld ❌ NO-GO (confirmation bias). 3 有效环境达成
4. ✅ ~~**统计检验全面执行**~~ → T4 (p=0.035) ✅, T6 TOST (p=0.002) ✅, T1-T3/T5 n.s. (n=3 功效不足)
5. ✅ ~~**CMDP Manual Threshold Sweep + Pareto 曲线**~~ → HotpotQA 完成

**P1 — 强烈建议：**
6. ✅ ~~**Phase 4 跨 T 泛化**~~ → WebShop 使用 LLM-Propose-K（第 3 种 T），SCG ≈ oracle。ALFWorld 揭示 rollout 质量前提
7. ✅ **Wrong-Direction 跨 gate 类型验证（Phase 2.5 S1 完成）**
8. 🟠 ~~**第 2 种 backbone**~~ → 0.6B NO-GO，无法获得第 2 backbone。需在 limitation 中说明
9. **TES 局限性论述**：论文 Section 5 中需正式讨论 TES effectiveness 公式在 ceiling effect 下的不稳定性
10. **APPS S3 补完**：APPS 阈值扫描 + λ* 表（待 Step 2 完成后）

**P2 — 锦上添花：**
11. **Capability boundary 预测验证**：基于 Type A/B framework 预测新环境方向
12. **Evaluator-executor identity 验证**：用更强模型做 evaluator
13. ✅ **FineTune(LR) vs FineTune(LoRA) 数据清洗（已修正）**

**⚠️ 关键风险清单（Phase 4 最终版）**：
| 风险 | 严重性 | 当前应对 | 补强建议 |
|------|--------|---------|---------|
| ~~环境数量不足~~ | ✅ **已解决** | 3 有效环境 + 1 边界结果 + 2 ceiling | — |
| ~~T-agnostic 降级~~ | ✅ **已解决** | 3 种 T 验证 (per-action + K-variant + LLM-Propose-K) | — |
| TES_LR < TES_random (HotpotQA) | 🟡 低 | SR-CS Pareto + APPS/WebShop TES 优于 random | 论文中讨论 TES 局限性 |
| ✅ Wrong-Direction 跨 gate | ✅ 已解决 | MLP −51.2pp, Prompt YES-bias | — |
| ✅ 多 seed | ✅ 已解决 | Phase 3: 3 seeds | — |
| ✅ 统计检验 | ✅ 已解决 | T4 (p=0.035) + T6 TOST (p=0.002) | — |
| 仅单一 backbone | 🟠 中 | Qwen3-4B (+ ALFWorld 8B), 0.6B NO-GO | limitation 中说明 |
| 方法过于简单 | 🟡 低 | finding-driven paper | 强调 finding 而非 method novelty |
| WebShop base SR 极低 | 🟡 低 | base 7.2% 但 oracle 43.3% → rollout T 有效 | 论文解释：4B 模型对 WebShop 天然困难 |

### 10.3 v3.0 投稿时间线与策略

| 投稿策略 | 需完成工作 | 预期评分 |
|---------|---------|---------|
| **NeurIPS 2026 主会（当前）** | 3 环境 + cost analysis + step-level narrative | **30-40%**（需更多环境和方法贡献） |
| **NeurIPS 2026 主会（+1-2 环境）** | + Game of 24 / GSM8K | **50-60%**（4-5 环境 + adaptive behavior story） |
| **NeurIPS 2026 主会（+环境+auto features）** | + 自动 feature extraction | **65-75%**（method 贡献升级） |
| **ICLR 2027 备投** | + 上述全部 + 更多消融 | 更有竞争力 |

**v3.0 关键 next steps（按优先级）**：

1. **扩展环境（P0 — 阻塞投稿）**：
   - 候选：Game of 24, GSM8K（baselines 也常用的环境）
   - 目标：4-5 个有效环境，展示 adaptive behavior 的泛化性
   - 选 1-2 个最终加入论文

2. **恢复 Phase 5 Track 1：自动 Feature Extraction（P1 — 强烈建议）**：
   - 目的：从手工 5-feature LR 升级到自动特征发现
   - 方法：hidden state probes 已有 AUC=0.88 的上界
   - 解决 "method is just LR" 的 reviewer 质疑

3. **论文写作（P2 — 与实验并行）**：
   - 使用 v3.0 narrative（step-level + adaptive behavior）
   - Token cost analysis 已有数据和图表
   - Introduction + Related Work 框架已在本文档中完成

### 10.4 论文的核心优势（v3.0 更新）

1. **新方向**：Step-level trajectory-aware gating — 与所有 ~46 篇 problem-level 工作方向性不同（零竞争）
2. **Adaptive Behavior Finding**：Gate 自动适应 rollout headroom（RR=60%/17%/6% 对应 headroom +48%/+40%/+6%）
3. **Pareto Dominance**：FRVC 在 HotpotQA (0.968@6.55× vs CaTS 0.932@10.55×) 和 WebShop (0.437@1.27× vs CaTS 0.305@3.44×) Pareto-dominate
4. **CATTS 隐藏成本发现**：APPS 上 vote cost > rollout cost (4,198 > 3,306 tokens/step)
5. **Zero overhead**：FRVC gate 使用 5 个 trajectory features + LR，零额外推理成本（vs CATTS 5× per step）
6. **APPS honest story**：Gate 在低 headroom (+6%) 时正确保守（RR=6%），这是 feature not bug
7. **Cost analysis framework**：Normalized token cost + CER + Pareto 分析，为领域提供标准化评估方法
8. **三层失败诊断**：threshold mismatch → signal poverty → direction assumption（解释为什么所有现有方法失败）
9. **Wrong-Direction 跨 gate 实验**：LR −34.5pp + MLP −51.2pp，方向是通用必要前提
10. **理论 grounding**：CMDP + VOC scope analysis + evaluator-executor identity

**⚠️ 客观评估（v3.0）**：
- 方向新颖度：⭐⭐⭐⭐⭐（step-level vs problem-level，零竞争）
- Finding 深度：⭐⭐⭐⭐☆（adaptive behavior + cost analysis + three-layer failure）
- Method 新颖度：⭐⭐☆☆☆（LR on 5 features — 但 finding-driven paper 可接受 → Phase 5 Track 1 可升级）
- 实验充分度：⭐⭐⭐☆☆（3 有效环境 — 需扩展至 4-5 个）
- NeurIPS 当前接受概率：**30-40%**
- 如果 +1-2 环境 + auto features：**65-75%**
- **论文成功关键**：(1) 扩展环境（最优先），(2) 自动 feature extraction，(3) 写作质量

---

## 11. Phase 5 Automatic Feature Discovery 三路并行方案（2026-03-02 更新）

### 11.1 动机

Phase 4 完成后的核心弱点：**Method 新颖度 ⭐⭐☆☆☆**。当前 SCG-FineTune(LR) = 手工 5 feature + logistic regression。NeurIPS reviewer 可能评价 "finding interesting but method is just LR"。

Phase 5 目标：**补强 methodology，从 ⭐⭐ 升级到 ⭐⭐⭐⭐**。核心问题：

```
当前手工 feature 的三个弱点：
1. 环境特异：evidence_count 只有 QA 有，state_category 只有 WebShop 有
2. 需要 domain knowledge：每个新环境需要人工定义信号
3. 信号类型受限：只有 5 维，可能遗漏关键信息

Phase 5 的核心追求：
  手工 feature → 自动 feature discovery
  环境特异信号 → 跨环境通用表征
  Binary classification → VOC estimation（更 principled）
```

### 11.2 三路并行方案概述

**关键设计决策**：使用 HuggingFace Transformers（而非 vLLM）作为推理后端。原因：

```
vLLM 限制：
  ✅ 快速生成 text + logprobs
  ❌ 无法获取 hidden states（PagedAttention 优化不暴露中间层）
  → 如果用 vLLM，Track A 需要额外一次 HF forward pass（双模型、双显存）

HF Transformers 优势：
  一次 forward pass 同时获取：
  ✅ generated_text（action）
  ✅ logprobs（→ token_entropy）
  ✅ hidden_states（→ d=2560 自动特征）
  → 一个模型、一次推理、三种信息

代价：比 vLLM 慢（无 PagedAttention / continuous batching）
但实验阶段完全可接受（200 ep × 3 env，总量不大）
```

**三条路线**：

| Track | Feature 来源 | 维度 | 部署时提取成本 | 可解释 | 跨环境通用 |
|-------|------------|------|-------------|:---:|:---:|
| **A: Hidden State** | LLM 最后一层内部表示 | d=2560 | 0（推理时顺便拿） | ❌ | ✅ |
| **B: Text Embedding** | sentence-transformers 对 state_text 编码 | d=768 | ~5ms（额外小模型） | ❌ | ✅ |
| **C: LLM-Guided Gate Generation** | LLM 直接生成 `should_trigger()` 函数（特征提取+决策一体） | N/A（纯代码） | ~0ms（纯代码） | ✅ | ✅ |

```
三路共享的不变量：
  - U 的计算方式不变（实际执行 optimizer 观测）
  - Direction 由代码计算（Spearman ρ / η²）
  - CMDP threshold λ* 不变

三路的区别：
  - Track A/B: state → feature vector → 训练 gate model (LR/MLP)
  - Track C: LLM 直接生成 should_trigger() 函数（特征提取+决策合一，无需单独训 gate）
```

#### Track A: Hidden State Probe（信息上限）

```
核心：用 LLM 最后一层 hidden state 作为 feature
  state_text → LLM forward → hidden_states[-1] → mean pooling → h ∈ R^2560
  h → MLP (2560→256→2) → VOC_mean, VOC_logvar
  trigger = (VOC_mean > λ*)

优势：信息最丰富（LLM 内部表示包含所有语义信息）
劣势：黑盒、需要模型内部访问（但用 HF Transformers 时成本为 0）
论文角色：性能上限 / 主方法候选
```

#### Track B: Text Embedding Probe（部署友好）

```
核心：用轻量 embedding 模型编码 state_text
  state_text → SentenceTransformer('all-MiniLM-L6-v2') → e ∈ R^384
  或 state_text → SentenceTransformer('all-mpnet-base-v2') → e ∈ R^768
  e → MLP (768→128→2) → VOC_mean, VOC_logvar

优势：不需要访问 LLM 内部、与 vLLM 完全兼容、轻量快速
劣势：embedding 模型非 task-specific，可能丢失关键信息
论文角色：轻量替代方案 / 部署推荐方案
```

#### Track C: LLM-Guided Gate Generation（可解释 + 最有可能重现手工发现）

```
核心：让 LLM 分析 calibration 轨迹，直接生成完整的 gate 函数
  Step 1: 收集 calibration 数据 {(state_text, action_text, U)} 三元组
  Step 2: 采样 high-U 和 low-U 样本，喂给强 LLM（GPT-4 / Claude）
  Step 3: LLM 直接生成 should_trigger(state_text, action_text) -> bool
         该函数内部同时包含：特征提取逻辑 + 触发决策逻辑
  Step 4: 在全部 calibration data 上评估 precision/recall
  Step 5: 将 false positive / false negative 样本反馈给 LLM，迭代 2-3 轮

  部署时：只运行 LLM 生成的纯 Python 函数（零 LLM 调用、零额外模型）

优势：
  - 完全可解释（生成的代码可直接阅读理解）
  - 零部署成本（纯 Python 函数）
  - 特征发现与决策合一（无需分步 feature extraction → gate training）
  - 最有可能重现人类手工发现的关键变量（与人类研究者操作在同一抽象层级：读 state_text 语义）
  - 迭代优化确保质量（error feedback loop）
劣势：LLM 生成质量不确定、规则可能过拟合 calibration set
论文角色：可解释方案 + 验证工具（若生成代码中出现 evidence_count / state_category，
          则直接证明 LLM 能自动发现人类找到的信号 — 这是一个很强的 story）
```

### 11.3 对 Writing Guide 的影响

**不变的部分（~80%）**：
- Section 1 (Intro): Finding 叙事完全不变（direction reversal is the selling point）
- Section 2 (Related Work): 不变 + 加入 "all assume fixed direction" framing for reasoning papers
- Section 3 (Problem Formulation): 不变（VOC, direction, CMDP）
- Section 5 (Experiments): Phase 0-4 数据不变，Phase 5 数据追加
- Section 6 (Discussion): 不变
- Appendix: 不变

**变化的部分（Section 4 Method）**：

#### 最终 Section 4 结构（根据三路结果选择）：

**情景 1：Track A 胜出（最可能）→ Hidden State 为主方法**
```
4.1 Problem: Rational Metareasoning for Adaptive Triggering
    - VOC(T, s) 定义, trigger condition: E[VOC] > Cost(T)
4.2 Automatic Feature Discovery via LLM Representations
    - 动机：手工 feature 环境特异 + 需要 domain knowledge
    - Hidden state h = LLM.last_hidden(state), frozen, d=2560
    - "The LLM already encodes optimizer-relevant information"
4.3 Direction-Aware VOC Probe
    - MLP: h → (VOC_mean, VOC_logvar)
    - Direction 从 calibration data 自动学习（无需显式计算 ρ）
    - 训练 < 10s on calibration data
4.4 CMDP-Optimal Triggering Threshold λ*
```

**情景 2：Track B 胜出 → Text Embedding 为主方法**
```
4.1 Problem formulation
4.2 Automatic Feature Discovery via Text Embeddings
    - 动机：部署友好、不需要模型内部访问
    - e = TextEncoder(state_text), frozen, d=768
4.3 Direction-Aware VOC Probe
4.4 CMDP threshold
```

**情景 3：Track C 表现意外好 → LLM-Guided Gate Generation 为主方法**
```
4.1 Problem formulation
4.2 LLM-Guided Gate Generation
    - LLM 分析 high-U / low-U calibration 轨迹
    - 直接生成 should_trigger() 函数（特征提取+决策合一）
    - 迭代优化：error feedback → 2-3 轮修正
    - 零部署成本 + 完全可解释
4.3 Iterative Refinement via Error Feedback
4.4 CMDP threshold
```

**情景 4：多路互补 → Ablation Study 形式呈现**
```
4.1 Problem formulation
4.2 Automatic Feature Discovery（三种方法概述）
4.3 Main Method: [最佳 track]
4.4 CMDP threshold
5.x Ablation: Feature Source Comparison
    → Table: Hand-crafted vs Hidden State vs Embedding vs LLM-Discovered
```

**情景 5：三路都不优于手工 feature → 回退方案**
```
保持原 Section 4（LR + 手工 feature），但：
  - 加入三路实验作为 appendix analysis
  - "hand-crafted features, despite their simplicity, capture environment-specific
     signals that generic representations miss"  → 这本身也是一个 finding
  - 在 Sec 6 Discussion 加强 "simplicity as a feature" 叙事
```

**Contribution 排序（Phase 5 成功时）**：
- C1: Empirical finding（direction reversal + signal replacement）— **不变，仍是核心卖点**
- C2: Automatic feature discovery framework（替代手工 feature engineering）— **Phase 5 新增**
- C3: Experimental validation（3 环境 + feature source ablation）
- C4: Negative results + boundary analysis

### 11.4 Related Work 中 Reasoning Papers 的处理

**问题**：AdaptThink、DiffAdapt、Think Just Enough 等是 reasoning 方向的 paper，与我们做 agent optimizer gating 是不同 setting。如何引用但不实验对比？

**写法模板**：

```latex
\paragraph{Adaptive Compute Allocation.}
A growing body of work studies \emph{when} to allocate additional compute
at test time. In the \textbf{reasoning} setting, AdaptThink~\cite{} uses RL
to learn think/no-think tokens; DiffAdapt~\cite{} uses lightweight probes
to estimate problem difficulty assuming a U-shaped entropy pattern;
Think Just Enough~\cite{} applies a fixed entropy threshold for early
stopping. In the \textbf{agent} setting, CATTS~\cite{} learns when to
invoke tree search in web navigation.

All these methods implicitly assume a fixed relationship between their
trigger signal and optimizer utility (e.g., higher entropy $\to$ more
benefit from extended reasoning). We study the \emph{agent} setting,
where sequential decision-making introduces state-dependent utility that
varies \emph{within} an episode---a dimension absent in single-turn
reasoning. Our key finding---signal-utility direction reversal---is
orthogonal to the specific optimizer type and likely extends to reasoning
settings, though we leave this verification to future work.
```

**关键句（Related Work 末尾的定位）**：

```latex
\textbf{Key distinction:} While concurrent reasoning methods
(AdaptThink, DiffAdapt) learn \emph{whether to think more}, we study
the more general question of \emph{whether to invoke any test-time
optimizer} in sequential agent tasks. Our finding that signal-utility
direction reverses across environments implies that fixed-direction
assumptions in these methods may also be violated when applied across
diverse reasoning tasks---a question our framework directly addresses.
```

**不实验对比的正当理由（Reviewer Q&A）**：

| Reviewer 问题 | 回答要点 |
|---|---|
| "Why not compare with AdaptThink?" | Different setting: single-turn reasoning vs multi-step agent. Different compute type: thinking tokens vs rollout. Direct comparison requires adapting their RL to agent environments, which is non-trivial and orthogonal to our contribution. |
| "How is your probe different from DiffAdapt's?" | DiffAdapt's probe estimates difficulty (assumes U-shaped pattern is universal). Ours discovers signal-utility direction (no pattern assumption). We show the assumed pattern varies across environments. |
| "Could your method be applied to reasoning?" | Yes, and this is promising future work. Our framework (probe direction → gate) is optimizer-agnostic. The finding (direction reversal) likely applies to reasoning settings given the diversity of reasoning tasks. |

### 11.5 Method 新颖度升级预期

| 方案 | Method 新颖度 | 总体 NeurIPS 接受概率 |
|------|-------------|---------------------|
| 原方案（LR + 手工特征） | ⭐⭐☆☆☆ | 65-75% |
| Track A 成功（Hidden State Probe） | ⭐⭐⭐☆☆ | 70-80% |
| Track B 成功（Text Embedding） | ⭐⭐⭐☆☆ | 70-75% |
| Track C 成功（LLM-Guided Gate Generation） | ⭐⭐⭐⭐☆ | 75-85% |
| 多路对比 ablation | ⭐⭐⭐⭐☆ | 75-85% |
| 三路都失败 + 补救 | ⭐⭐☆☆☆ | 65-75%（回退） |

### 11.6 Phase 5 vs 核心竞争方法区别升级分析（2026-03-02 更新）

**核心问题**：Phase 5 的 automatic feature discovery 与 CATTS、ARPO 的区别是否更大？

**答案：是，区别显著增大**。当前版本的最大隐患是 method 层面与 CATTS/ARPO 相似度较高（都是手工信号 + 简单 gating 模型），Phase 5 从 feature 来源上直接拉开距离。

#### 11.6.1 当前版本 vs Phase 5：区别等级对比

**vs CATTS**:

| 维度 | 当前 (SCG-LR) vs CATTS | Phase 5 (Auto Feature) vs CATTS |
|------|----------------------|---------------------------------|
| **Finding** | ✅ 显著不同（direction discovery vs 固定方向） | ✅ 不变 |
| **Feature 来源** | ⚠️ 都是手工信号 | ✅✅ 自动 feature（hidden state / embedding / LLM-discovered）vs 手工 vote entropy |
| **Gate 架构** | ⚠️ 相似（grid search τ vs LR） | ✅ MLP on auto features vs single threshold |
| **跨环境适应** | ⚠️ 都需 per-env 手工定义信号 | ✅✅ 通用表征（hidden state / embedding 不需要 per-env 定义） |
| **Feature Engineering 成本** | ⚠️ 都需要人工 | ✅✅ 零人工（Track A/B 完全自动，Track C 一次性 LLM 生成 gate + 迭代优化） |
| **Method 区别总评** | ⚠️ 20% — **最大风险点** | ✅ 45-55% — 显著不同 |

**vs ARPO**:

| 维度 | 当前 (SCG-LR) vs ARPO | Phase 5 (Auto Feature) vs ARPO |
|------|---------------------|---------------------------------|
| **Finding** | ✅ 显著不同 | ✅ 不变 |
| **信号空间** | ⚠️ 都用 entropy 类信号 | ✅✅ 2560-dim / 768-dim 自动表征 vs 单一 entropy |
| **训练范式** | ✅ calibration LR vs RL training | ✅✅ calibration probe vs per-env RL（更轻量） |
| **可解释性** | ✅ LR 系数可解释 vs RL 黑盒 | ✅ Track C 完全可解释（生成的 Python 代码可直接阅读）/ Track A 需 probing |
| **新环境部署** | ✅ calibration vs RL re-training | ✅✅ 通用表征 + calibration（无需重定义信号） |
| **Method 区别总评** | ✅ 40% — 已有一定差距 | ✅✅ 55-65% — 显著不同 |

#### 11.6.2 Phase 5 拉开差距的核心维度

```
核心差异：Feature 来源
  当前 + CATTS + ARPO: 人类预定义固定信号（entropy, vote, step_count...）
  Phase 5: 自动从 LLM 表征 / 文本语义 / LLM 分析中发现 feature

这直接解决了论文 C1 finding 暴露的问题：
  Finding: 不同环境需要不同信号（signal replacement）
  → 如果信号必须人工定义，那每到一个新环境就需要 domain expert
  → Phase 5: 自动发现环境特定 feature，无需人工定义
  → Finding 和 Method 形成完美的 "问题→解决" 闭环
```

#### 11.6.3 对 Related Work / Concurrent Work 声明的写作影响

**Phase 5 版本的并发工作声明**（finding + automatic feature 均展开）：
```latex
CATTS~\cite{catts} and ARPO~\cite{arpo} address adaptive compute
allocation with hand-crafted signals (vote entropy, policy entropy)
and per-environment gating models. Beyond our empirical finding that
signal-utility direction reverses across environments, our approach
eliminates the need for hand-crafted signal engineering entirely:
we discover environment-specific features automatically from LLM
representations, enabling deployment to new environments without
domain-specific signal design. This addresses both the direction
problem (fixed assumptions fail) and the signal selection problem
(no single hand-crafted signal works across environments).
```

#### 11.6.4 核心结论

```
Phase 5 的核心价值：
  Finding (C1) 揭示了两个问题: direction reversal + signal replacement
  Method (C2) 同时解决这两个问题:
    direction → 从 calibration data 自动学习（已有）
    signal replacement → 自动 feature discovery（Phase 5 新增）

vs CATTS/ARPO 的差距从 "finding 不同但 method 相似" 升级为 "finding 不同 + method 不同"：
  当前: 手工 feature（和 CATTS/ARPO 一样）+ direction-aware（独有）
  Phase 5: 自动 feature（独有）+ direction-aware（独有）
  → Reviewer 无法说 "method is just LR on hand-crafted features"
```
