# Candidate Baselines for SCG/FRVC Paper (2025-2026)

**Date**: 2026-03-17
**Purpose**: 补充现有 baseline 列表，寻找 2025/2026 年会议或 arXiv 上可作为新增 baseline 的论文

---

## 现有 Baselines（已在论文中）

- CaTS (2025) — Calibrated Test-time Scaling
- CATTS (2026) — concurrent work
- CoRefine
- SEAG (ACL 2025) — Search-Efficient Graph Augmentation
- Snell et al. (ICLR 2025) — Scaling LLM Test-Time Compute Optimally
- AdaptThink (EMNLP 2025)
- DiffAdapt (2025)
- Think Just Enough (2025)
- Thinkless (2025)
- PonderTTT (2025)
- L1, LATTS, DeepConf, ARPO, Learning When to Plan, Compute-Optimal

---

## Tier 1：高度相关（可直接对比 SCG）

### 1. Entropy-Gated Branching (EGB)

- **Venue**: arXiv 2025
- **核心机制**: 用 token entropy 作为 gating signal，在高不确定性的推理步骤处选择性分支（而非均匀展开），配合 Process Reward Model 剪枝低质量分支。
- **结果**: 比标准推理准确率 +22.6%；比 beam search 快 31-75%（数学/金融推理 benchmark）。
- **方向假设**: **固定**（高 entropy = 多分支）
- **与 SCG 的对比价值**:
  - EGB 使用 token entropy 作为核心信号，且假设固定方向（高 entropy → 需要更多 compute）
  - SCG 的 direction reversal 发现直接挑战此假设：某些环境中高 entropy 可能意味着 rollout 无效，应放弃而非分支
  - **定位**: "fixed-direction entropy gating" baseline

### 2. RADAR: Reasoning-Ability and Difficulty-Aware Routing

- **ArXiv**: 2509.25426 (2025)
- **Authors**: Fernandez, Kveton et al.
- **核心机制**: 借鉴心理测量学的 Item Response Theory (IRT)，联合估计 query 难度和 model-configuration 能力，将 query 路由到最优的 {model, reasoning budget} 组合。路由延迟 ~7ms。
- **结果**: 在 8 个推理 benchmark 上实现更优的 Pareto-optimal 性能-成本权衡；OOD 泛化能力强。
- **方向假设**: **学习但 env-agnostic**（假设难度与 compute 需求单调关系）
- **与 SCG 的对比价值**:
  - RADAR 学习 difficulty-aware routing，但不考虑信号-性能相关性方向可能在不同环境中反转
  - SCG 捕捉 env-specific direction reversal，RADAR 的 IRT 模型无法做到
  - **定位**: "learned but environment-agnostic routing" baseline

### 3. AdaReasoner

- **ArXiv**: 2505.17312 (NeurIPS 2025)
- **Authors**: Tan et al. (Notre Dame / MBZUAI)
- **核心机制**: LLM-agnostic 的 RL 插件，通过 learned policy + factorized action heads，per-query 动态选择推理超参数（temperature, prompt type, step count）。使用 REINFORCE++ + pretrained reward model。
- **结果**: 在 6 个 LLM 上比 CoT/Auto-CoT/Best-of-N 提升 5-15%；OOD 鲁棒性强。
- **方向假设**: **学习 per-query, 非 per-env**
- **与 SCG 的对比价值**:
  - AdaReasoner 学习"用什么推理配置"，但 policy 是 query-conditioned，不是 environment-conditioned
  - 不处理 direction reversal（同一信号在不同任务环境中语义反转）
  - **定位**: "instance-level RL adaptation" vs SCG 的 "environment-level gating"

### 4. Certainty-Guided Reasoning (CGR)

- **ArXiv**: 2509.07820 (2025)
- **核心机制**: Model-agnostic early-exit 策略，每 ~1,000 token 通过追加 "Final Answer" 前缀探测模型 certainty，certainty 超过阈值（0.97-0.99）即终止。
- **结果**: 在 AIME benchmark 上节省数百万 token；准确率在最严格阈值下仅降 1.1%。
- **方向假设**: **固定**（高 certainty = 提前停止）
- **与 SCG 的对比价值**:
  - CGR 使用 certainty 作为固定方向信号（高 certainty = 该停了）
  - SCG 可以展示在某些环境中，早期高 certainty 实际上与更差的最终结果相关（如 overconfident wrong paths）
  - **定位**: "fixed-direction certainty-based early exit" baseline

### 5. Adaptive Reasoning Suppression (ARS)

- **ArXiv**: 2510.00071 (October 2025)
- **Authors**: Dongqi Zheng
- **核心机制**: Training-free 方法，通过 multi-checkpoint certainty 估计 + 渐进抑制阈值，动态抑制冗余推理步骤。无需 fine-tuning。
- **结果**: GSM8K/MATH 上 token 减少 53%、延迟降低 46.1%、能耗降低 57.9%，准确率不降。
- **方向假设**: **固定阈值**（高 certainty = 抑制进一步思考）
- **与 SCG 的对比价值**:
  - ARS 是 training-free certainty-based suppression，使用固定方向假设
  - SCG 的 learned gating 在 certainty-utility 关系反转的环境中优势明显
  - **定位**: "training-free fixed-threshold suppression" baseline

---

## Tier 2：补充对比

### 6. s1: Simple Test-Time Scaling (Budget Forcing)

- **ArXiv**: 2501.19393 (EMNLP 2025)
- **Authors**: Muennighoff, Yang, Shi, Li et al.
- **核心机制**: 在 1,000 curated samples 上 fine-tune，然后通过 "budget forcing"（追加 "Wait" token 延长推理或强制提前终止）控制 compute。s1-32B (from Qwen2.5-32B) 在数学上超 o1-preview。
- **结果**: MATH/AIME24 上比 o1-preview 提升最高 27%。
- **方向假设**: 固定（more compute = better）
- **与 SCG 的对比价值**:
  - "无 gating" 的下界对比，忽略所有信号，简单增加 compute
  - SCG 应展示 environment-aware allocation 优于 naive budget forcing
  - **定位**: "no gating / always extend" lower-bound baseline

### 7. ODAR: Principled Adaptive Routing via Active Inference

- **ArXiv**: 2602.23681 (February 2026)
- **核心机制**: 将 difficulty-aware routing 与 fast/slow agent 专门化结合，使用双阈值创建 3 条推理路径（simple: 仅 fast; medium: fast + slow 验证; hard: fast + 5 个 slow 候选 + FEP-based selection）。
- **方向假设**: 固定 tier 分配
- **与 SCG 的对比价值**:
  - ODAR 使用固定难度 tier + 预定 compute 分配
  - SCG 展示 tier 内最优分配方向随环境变化
  - **定位**: "fixed-tier adaptive routing" baseline

### 8. Chain of Draft (CoD)

- **ArXiv**: 2502.18600 (March 2025)
- **Authors**: Xu et al. (Zoom Communications)
- **核心机制**: Prompting 策略，生成简约的 ~5 词推理步骤而非冗长 CoT，token 减少 80% 且保持准确率。
- **结果**: GPT-4o/GSM8K 上仅用 7.6% token 匹配 CoT 准确率；延迟降低 48-76%。
- **方向假设**: 固定（shorter always better）
- **与 SCG 的对比价值**:
  - 正交方法（压缩推理 per-step vs 选择性分配 compute budget）
  - **定位**: "reasoning compression" complementary baseline

### 9. Benchmark Test-Time Scaling of General LLM Agents

- **ArXiv**: 2602.18998 (February 2026, CMU)
- **核心机制**: 非方法论文，而是 benchmark 分析——揭示 "context ceiling"（超过 ~100K token 性能下降）和 "verification gap"（agent 无法从并行样本中可靠选出最佳 trajectory，即使用 GPT-5 做 verifier）。
- **与 SCG 的关联**:
  - 为 compute 与环境的关系提供实证支持，motivation 角度有用
  - Verification gap 支持 direction reversal 论点：更多 compute 不总是有帮助
  - **定位**: motivation / related work 引用

### 10. SpecReason: Speculative Reasoning for Fast LRM Inference

- **Venue**: NeurIPS 2025
- **核心机制**: 用轻量模型 speculative 执行中间 CoT 步骤，大模型只做验证/修正。利用推理 token 的 semantic tolerance。
- **结果**: 1.4-3.0x 加速；跨领域 benchmark 上准确率提升 0.4-9.0%。
- **方向假设**: 固定 fast/slow 分配规则
- **与 SCG 的对比价值**:
  - SpecReason 在 fast speculator 和 slow verifier 之间分配 compute，但使用固定分配
  - SCG 展示最优 fast/slow 拆分因环境而异
  - **定位**: "fixed fast/slow allocation" baseline

---

## 推荐优先级

### 必须加入（直接可对比实验）

1. **AdaReasoner** — RL-based per-query 自适应，最接近 SCG 的学习范式但缺少 env-level direction awareness
2. **CGR** — certainty-based early exit，代表固定方向 gating 的 SOTA
3. **EGB** — entropy-based gating，与 SCG 使用相同核心信号但方向固定

### 强烈推荐（丰富对比维度）

4. **ARS** — training-free baseline，展示 SCG 学习的必要性
5. **RADAR** — difficulty-aware routing，展示 env-agnostic 路由的局限性
6. **s1** — "no gating" 下界

### 可选（Related Work 讨论）

7. **ODAR**, **SpecReason** — fast/slow 范式对比
8. **CoD** — 正交方法
9. **AgentBench TTS** — motivation 支持

---

## 总结对比表

| # | Paper | Year | 方向假设 | 决策粒度 | 训练需求 | SCG 优势 |
|---|-------|------|---------|---------|---------|---------|
| 1 | EGB | 2025 | 固定（高 entropy = 分支） | Step-level | PRM | SCG 学方向 |
| 2 | RADAR | 2025 | 学习但 env-agnostic | Problem-level | IRT fitting | SCG env-specific |
| 3 | AdaReasoner | 2025 | 学习 per-query | Problem-level | RL | SCG env-level gating |
| 4 | CGR | 2025 | 固定（高 certainty = 停） | Within-generation | 无 | SCG 处理反转 |
| 5 | ARS | 2025 | 固定阈值 | Within-generation | 无 | SCG 自适应方向 |
| 6 | s1 | 2025 | 固定（more = better） | Problem-level | Fine-tune | SCG 知道何时更多无用 |
| 7 | ODAR | 2026 | 固定 tier | Problem-level | Active inference | SCG tier 内自适应 |
| 8 | CoD | 2025 | 固定（shorter） | Per-step | 无 | 正交 |
| 9 | AgentBench TTS | 2026 | N/A (分析) | — | — | Motivation |
| 10 | SpecReason | 2025 | 固定 fast/slow | Per-step | 轻量模型 | SCG 学环境拆分 |

---

**⚠️ 注意**: 部分 arXiv ID（尤其 EGB）未完全确认，引用前请在 arxiv.org 或 Semantic Scholar 二次验证。已确认的 ID: RADAR (2509.25426), AdaReasoner (2505.17312), CGR (2509.07820), ARS (2510.00071), s1 (2501.19393), ODAR (2602.23681), CoD (2502.18600), AgentBench TTS (2602.18998)。
