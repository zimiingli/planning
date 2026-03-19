# Candidate Baselines for SCG/FRVC Paper (2025-2026)

**Date**: 2026-03-18 (updated: implementation details + feasibility assessment + AUQ/s1 实现)
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

- **ArXiv**: 2503.21961 (EACL 2026 Main Conference)
- **Authors**: Xianzhi Li, Ethan Callanan, Abdellah Ghassel, Xiaodan Zhu (Queen's University)
- **核心机制**: 用 token entropy 作为 gating signal，在高不确定性的推理步骤处选择性分支（而非均匀展开），配合 Process Reward Model 剪枝低质量分支。
- **结果**: 比标准推理准确率 +22.6%；比 beam search 快 31-75%（数学/金融推理 benchmark）。
- **方向假设**: **固定**（高 entropy = 多分支）
- **与 SCG 的对比价值**:
  - EGB 使用 token entropy 作为核心信号，且假设固定方向（高 entropy → 需要更多 compute）
  - SCG 的 direction reversal 发现直接挑战此假设：某些环境中高 entropy 可能意味着 rollout 无效，应放弃而非分支
  - **定位**: "fixed-direction entropy gating" baseline

#### ❌ 不纳入实验的原因

EGB 是 **token-level branching + PRM** 范式，与 FRVC 的 **step-level rollout gating** 范式根本不同：
- EGB 在生成过程中高 entropy token 处创建多条分支，用 PRM (7B 模型) 打分选最优
- FRVC 在 agent 每步交互后决定是否触发 rollout（独立计算）
- 如果强行适配，entropy gating 部分退化为 CoRefine（已有 baseline），branching+PRM 机制无法在 FRVC 框架中实现
- 需要额外部署 `Qwen2.5-Math-PRM-7B`，硬件成本不合理
- **结论**：在 Related Work 中讨论，不做实验对比

#### 实现细节

**Entropy 计算**:
```python
# H_t = -sum_{i=1}^{V} p_{i,t} * log2(p_{i,t})
distribution = torch.distributions.Categorical(logits=logits)
entropy = distribution.entropy().item()
```

**算法流程 (Algorithm 1)**:
1. 初始化 beam set B_0 = {问题输入}
2. 每步对每个 beam 计算 token entropy H_t
3. **低 entropy beam** (H_t <= tau): 生成单条续写（不分支）
4. **高 entropy beam** (H_t > tau): 回滚到高 entropy 位置，用 temperature scaling 生成 W 条候选分支
5. 对所有候选用 PRM 打分，保留 top-K
6. 重复直至生成完成；返回最高分 beam

**核心超参数**:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| Beam size K | 4 | 维持的活跃 beam 数 |
| Beam width W | 4 | 每个 uncertain beam 生成的候选数 |
| Entropy threshold tau | 模型相关 | Qwen3: 1.0-2.0; Llama3: 0.8-2.5 |
| Max reasoning steps T | 100 | 最大推理步数 |
| Max tokens per step | 1024 | 每步最大 token 数 |

**Entropy 阈值 tau 敏感性**:
- tau=0 退化为标准 beam search（每步都分支）
- tau=∞ 退化为 self-consistency / best-of-n（不分支）
- 最优 tau 主要是 **model-family 属性**（同一 tau 在 MATH-500 和 CFA-L2 上均有效）
- 推荐在验证集上 sweep: tau ∈ {0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0}
- 性能在 tau ±0.5~1.0 范围内仅波动 1-3pp

**PRM (Process Reward Model)**:
- 主要: `Qwen2.5-Math-PRM-7B`（HuggingFace 最流行的 PRM）
- 备选: `RLHFlow/Llama3.1-8B-PRM-Deepseek-Data`
- 打分方式: 用 `<extra_0>` 分隔符提取逐步 reward，score = P('+' token)

**测试模型**: Qwen3-{1.7B, 4B, 8B}, Llama-3.2-{1B, 3B}, Llama-3.1-8B

**评测 Benchmark**: AIME (90题), MATH-500, GSM8K (1319题), CFA Level I/II

**代码**: https://github.com/JXL884/entropy_gated_branching （标注 "FIXING REPO IN PROGRESS"）
- 核心文件: `confidence_beam_search_vers.py`（EGB 实现）, `run_beam_search.py`（入口，`--confidence-beam-search` 启用 EGB）
- 依赖: PyTorch >=2.5.1, Transformers 4.52.3, Accelerate, bitsandbytes（4-bit 量化）
- 硬件: NVIDIA H100 (80GB), 单卡

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

- **ArXiv**: 2505.17312 (NeurIPS 2025 Spotlight)
- **Authors**: Xiangqi Wang, Yue Huang et al. (Notre Dame MINE Lab / MBZUAI)
- **核心机制**: LLM-agnostic 的 RL 插件，通过 learned policy + factorized action heads，per-query 动态选择推理超参数（temperature, prompt type, step count）。使用 REINFORCE-style policy gradient + pretrained reward model。
- **结果**: 在 6 个 LLM 上比 CoT/Auto-CoT/Best-of-N 提升 5-15%；OOD 鲁棒性强。
- **方向假设**: **学习 per-query, 非 per-env**
- **与 SCG 的对比价值**:
  - AdaReasoner 学习"用什么推理配置"，但 policy 是 query-conditioned，不是 environment-conditioned
  - 不处理 direction reversal（同一信号在不同任务环境中语义反转）
  - **定位**: "instance-level RL adaptation" vs SCG 的 "environment-level gating"

#### ❌ 不纳入实验的原因

AdaReasoner 是 **query-level reasoning 配置选择**，与 FRVC 的 **step-level rollout gating** 范式根本不同：
- AdaReasoner 在问题开始前选择 (temperature, prompt, steps) 配置组合，一次性生成答案
- FRVC 是在 agent 每步交互时做二元决策（rollout/skip）
- AdaReasoner 的 benchmark 是单轮 QA（MMLU, TruthfulQA），FRVC 是多步交互任务
- 如果强行适配为 binary gate，退化为 "BERT encoder + 1-layer MLP → trigger/skip" = SCG_MLP 变体，失去原方法意义
- **结论**：在 Related Work 中讨论，不做实验对比

#### 实现细节

**RL Agent 架构**: `FactorizedAdaptiveContextualMLPAgent`
- **输入**: BERT (`bert-base-uncased`) mean-pooling → 768-d embedding (L2 normalized)
- **共享层**: Linear(768 → 64) + tanh
- **三个并行 action head** (各一层 Linear):
  - Prompt head: Linear(64 → num_prompts) — 选择认知策略模板
  - Temperature head: Linear(64 → 10) — {0.1, 0.2, ..., 1.0}
  - Step head: Linear(64 → num_steps) — {3, 4, 5, 6, 7, 8, 9}
- 权重初始化: `randn() * 0.01`

**Factorized Action Space (3 维)**:
| 维度 | 选项数 | 取值 |
|------|--------|------|
| Temperature a_t | 10 | {0.1, 0.2, ..., 1.0} |
| Reasoning Steps a_s | 7 | {3, 4, 5, 6, 7, 8, 9} |
| Instruction Prompt a_p | 可变 | (base策略, variation修饰) 组合对 |

**训练算法**: REINFORCE-style policy gradient + Boltzmann exploration
1. 对每个训练问题 q_i：
2. 采样 action: `a_t, a_p, a_s ~ Softmax(log π_θ(A|q_i) / τ_explore)`
3. 生成答案: `y = LLM(q_i | a_t, a_p, a_s)`
4. 计算 reward: `r = RewardModel(y, R_i)`
5. 更新: `θ ← θ + η · r · ∇_θ log π_θ(a_j | q_i)` (j ∈ {t, p, s})

**Exploration 退火**: `τ_explore = max(1.0 - 0.0001 * step, 0.1)`

**Reward Model**: `facebook/bart-large-mnli` (zero-shot NLI) — 构造假设 "candidate matches ground truth"，提取 "yes" 置信度作为 reward ∈ [0,1]

**训练超参数**:
| 参数 | 值 |
|------|-----|
| Learning rate | 0.001 (代码) / 0.01 (论文) |
| Hidden dim | 64 |
| Training epochs | 5 |
| Training samples (few-shot) | 100 per dataset |
| Exploration decay | 0.0001 |
| Min exploration temp | 0.1 |
| Top-p (LLM decoding) | 0.1 |
| Max tokens (LLM) | 2,048-5,000 |

**推理流程**:
1. BERT 编码输入问题 → 768-d
2. MLP 前向传播 → 3 个 head 各自 argmax 选择动作
3. 用选定的 (temperature, prompt, step count) 配置 LLM 生成
4. 后处理: hierarchical clustering (threshold 0.8) + 加权投票

**评测 Benchmark**:
- 主要 (100 train / 900 test): MMLU-Math, Metaphor, TruthfulQA, LogiQA
- 知识密集 (100 train / 500 test): GPQA, MMLUChem, MedExQA
- OOD (150 samples, zero-shot): BRIGHTER, StepGame, CRoW

**测试模型**: GPT-4o, LLaMA-3.3-70B, Qwen-2.5-72B, Claude-3.5-Sonnet, DeepSeek-R1, GPT-o3-mini

**代码**: https://github.com/MINE-Lab-ND/AdaReasoner (MIT License)
- 核心文件: `adatrain.py`（训练）, `adatest.py`（推理）, `module/twin_toolbox.py`（RL agent）, `module/Judge_reward.py`（reward model）
- 依赖: PyTorch 2.4.0, transformers 4.44.2, sentence-transformers, openai, anthropic
- 预训练模型: `gpt4oadapt.pkl` 等 pickle 文件

**⚠️ 注意**: 存在同名但不同的论文 "AdaReasoner" (arXiv 2601.18631, ICLR 2026, ssmisya) 关于视觉推理工具编排，勿混淆。

### 4. Certainty-Guided Reasoning (CGR)

- **ArXiv**: 2509.07820 (v2: February 2026)
- **Authors**: Joao Paulo Nogueira, Wentao Sun, Alonso Silva, Laith Zumot
- **核心机制**: Model-agnostic early-exit 策略，每 ~1,000 token 通过追加 "Final Answer" 前缀探测模型 certainty，certainty 超过阈值（0.97-0.99）即终止。
- **结果**: 在 AIME benchmark 上节省数百万 token；准确率在最严格阈值下仅降 1.1%。
- **方向假设**: **固定**（高 certainty = 提前停止）
- **与 SCG 的对比价值**:
  - CGR 使用 certainty 作为固定方向信号（高 certainty = 该停了）
  - SCG 可以展示在某些环境中，早期高 certainty 实际上与更差的最终结果相关（如 overconfident wrong paths）
  - **定位**: "fixed-direction certainty-based early exit" baseline

#### ❌ 不纳入实验的原因

CGR 是 **生成内 early-exit** 策略，与 FRVC 的 **step-level rollout gating** 范式不同：
- CGR 在单次生成过程中每 1000 token 探测 certainty，决定何时停止思考（减少 compute）
- FRVC 是在 action 提出后决定是否投入更多 compute（触发 rollout）
- CGR 需要 mid-generation logit probing（追加 "Final Answer: \boxed{" 前缀），vLLM 架构不支持
- 如果适配为 step-level confidence gate → 本质等同于 CaTS（已有 baseline）
- 仅在 AIME（30 题）上测试，极度窄域
- **结论**：在 Related Work 中讨论，不做实验对比

#### 实现细节

**Certainty 探测机制**:
- 每隔 Δ=1,000 thinking tokens，追加前缀 `"Final Answer: \boxed{"`
- 用 **greedy decoding** (argmax) 解码最多 L=4 个 answer token
- **Certainty 分数**: 所有 answer token 概率的 **最小值**（保守度量）
  ```
  c(a*) = min_{i=1..n} p(t_i* | q, o, t_{<i}*)
  ```
- **需要 logits 访问**: 必须获取每个解码步的 softmax 概率分布

**Early-Exit 算法**:
```
Input: query q, model M, budget B, threshold θ, interval Δ
o ← empty
for t = 1 to B:
    Sample next token x ~ M(.|q,o)
    o ← o || x
    if x == </think>: break
    if t mod Δ == 0:
        c ← CertaintyProbe(M, q, o)  # 追加 "Final Answer: \boxed{" 解码
        if c >= θ: break
Output: DecodeAnswer(M, q, o)
```

**核心超参数**:
| 参数 | 值 | 说明 |
|------|-----|------|
| Certainty threshold θ | {0.96, 0.97, 0.98, **0.99**} | 推荐 0.99 |
| Probe interval Δ | 1,000 tokens | 探测频率 |
| Max answer tokens L | 4 | 足够 AIME 整数答案 [0,999] |
| Budget B | 1,000-32,000 tokens | 最大思考预算 |
| Generation temperature | 0.6 | 主生成温度 |
| Seeds | 64 | 统计鲁棒性 |

**Training-free**: 完全推理时方法，无需训练/微调/架构修改。开销仅为 ~32 次 probe（32K budget 下）。

**关键数值结果 (DeepSeek-R1-Distill-Qwen-14B, 64 seeds)**:
| Threshold θ | Accuracy | Token Savings |
|------------|----------|---------------|
| 0.96 | 44.69% | 3,380,578 |
| 0.97 | 45.26% | 3,081,690 |
| 0.98 | 45.89% | 2,739,761 |
| 0.99 | 46.61% (-1.1pp) | 2,042,389 |
| Baseline | 47.70% | 0 |

**Grade 指标** (penalize wrong answers): CGR 在 p>=0.5 时 Grade **优于** baseline（abstain 优于答错）。

**测试模型**: DeepSeek-R1-Distill-Qwen-14B, DeepSeek-R1-Distill-Llama-70B, Phi-4-reasoning-plus

**评测 Benchmark**: 仅 AIME2025 (30 题)——作者承认这是局限性

**代码**: **无官方代码仓库**。
- 可参考相关实现 **Dynasor** (https://github.com/hao-ai-lab/Dynasor) — vLLM 扩展，实现类似 "probe-in-the-middle" certainty early exit（用 answer consistency 而非 min token prob）
- 核心实现需求: 自定义 logits processor，可在生成中途追加 probe prefix、fork decoding、评估置信度

**相关方法**: Dynasor/Certaindex ("Reasoning Without Self-Doubt", NeurIPS 2025) 机制最接近，但用 answer consistency（连续 K 次相同答案）而非 token probability 作为 certainty 信号。

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

### 6. s1: Simple Test-Time Scaling (Budget Forcing) — ✅ 已实现

- **ArXiv**: 2501.19393 (EMNLP 2025)
- **Authors**: Muennighoff, Yang, Shi, Li et al.
- **核心机制**: 在 1,000 curated samples 上 fine-tune，然后通过 "budget forcing"（追加 "Wait" token 延长推理或强制提前终止）控制 compute。s1-32B (from Qwen2.5-32B) 在数学上超 o1-preview。
- **结果**: MATH/AIME24 上比 o1-preview 提升最高 27%。
- **方向假设**: 固定（more compute = better）
- **与 SCG 的对比价值**:
  - "无 gating" 的下界对比，忽略所有信号，简单增加 compute
  - SCG 应展示 environment-aware allocation 优于 naive budget forcing
  - **定位**: "no gating / always extend" lower-bound baseline

#### ✅ FRVC 适配实现

- **实现**: `S1Budget_Gate` in `frvc/competing_baselines.py` (commit `9e1b86c`)
- **适配方式**: 固定预算均匀分配 — 每 episode 分配 K 次 rollout，均匀分布到各步
- **K 值**: 匹配 SCG 在各环境的 avg ro/ep（HotpotQA: K=2, APPS: K=1, WebShop: K=1, TWExpress: K=2, Plancraft: K=4）
- **论文论点**: 同 cost 下 intelligent allocation (SCG) vs unintelligent uniform allocation (s1)
- **实验**: Job 23210145, 15 runs (5 env × 3 seeds × 200 ep), 🔄 Queued

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

### 11. AUQ: Agentic Uncertainty Quantification — ✅ 已实现

- **ArXiv**: 2601.15703 (January 2026)
- **Authors**: (UCSD / DeepResearch)
- **核心机制**: Dual-process agent uncertainty — System 1 (UAM) 隐式传播 confidence，System 2 (UAR) 在 uncertainty 超阈值时触发 targeted correction/reflection。
- **结果**: WebShop 42.9% (+13.6% over ReAct), ALFWorld 74.3% (+10.7%)
- **方向假设**: **固定负向**（低 confidence → 触发）
- **与 SCG 的对比价值**:
  - AUQ 使用 verbalized confidence 作为固定方向信号（低 → 触发）
  - 新信号类型（verbalized），与现有 4 个 CB 的信号（entropy/logprob/vote/calibrated）都不同
  - 每步多 1 次 LLM 调用 → cost 显著高于零开销 gate
  - SCG 的 direction discovery 在 confidence-utility 反转环境中应优于 AUQ
  - **定位**: "verbalized uncertainty fixed-direction gate" baseline

#### ✅ FRVC 适配实现

- **实现**: `AUQ_Gate` in `frvc/competing_baselines.py` (commit `9e1b86c`)
- **适配方式**: 每步向 LLM 发送 confidence query（含 observation + proposed action），解析 0-1 数值，低于阈值触发 rollout
- **阈值校准**: 从 Phase 1 data 自动校准（与 CaTS 同策略）
- **Cost 追踪**: `auq_total_tokens` 记录额外 LLM 调用开销
- **实验**: Job 23210145, 15 runs (5 env × 3 seeds × 200 ep), 🔄 Queued

---

## 推荐优先级（2026-03-18 更新）

### ✅ 已实现（直接实验对比）

1. **AUQ** — verbalized uncertainty gate，新信号类型，已实现并提交实验
2. **s1 Budget Forcing** — 固定预算均匀分配，同 cost 对比 SCG，已实现并提交实验

### ❌ 不纳入实验（范式不匹配）

3. **AdaReasoner** — query-level reasoning 配置，非 step-level gating（详见 Tier 1 §3 分析）
4. **CGR** — 生成内 early-exit，需 mid-generation probing，退化为 CaTS（详见 Tier 1 §4 分析）
5. **EGB** — token-level branching + PRM，退化为 CoRefine + 需 7B PRM（详见 Tier 1 §1 分析）

### Related Work 讨论（不做实验）

6. **ARS** — training-free certainty suppression
7. **RADAR** — difficulty-aware routing
8. **ODAR**, **SpecReason** — fast/slow 范式
9. **CoD** — reasoning compression
10. **AgentBench TTS** — motivation 支持

---

## 总结对比表

| # | Paper | Year | 方向假设 | 决策粒度 | 训练需求 | SCG 优势 | 实验? |
|---|-------|------|---------|---------|---------|---------|:-----:|
| 1 | EGB | 2025 (EACL 2026) | 固定（高 entropy = 分支） | Step-level | PRM | SCG 学方向 | ❌ 范式不同 |
| 2 | RADAR | 2025 | 学习但 env-agnostic | Problem-level | IRT fitting | SCG env-specific | ❌ |
| 3 | AdaReasoner | 2025 (NeurIPS Spotlight) | 学习 per-query | Problem-level | RL | SCG env-level gating | ❌ 范式不同 |
| 4 | CGR | 2025 | 固定（高 certainty = 停） | Within-generation | 无 | SCG 处理反转 | ❌ 范式不同 |
| 5 | ARS | 2025 | 固定阈值 | Within-generation | 无 | SCG 自适应方向 | ❌ |
| 6 | **s1** | **2025** | **固定（uniform budget）** | **Per-episode** | **无** | **SCG 知道分配到哪** | **✅ 已实现** |
| 7 | ODAR | 2026 | 固定 tier | Problem-level | Active inference | SCG tier 内自适应 | ❌ |
| 8 | CoD | 2025 | 固定（shorter） | Per-step | 无 | 正交 | ❌ |
| 9 | AgentBench TTS | 2026 | N/A (分析) | — | — | Motivation | ❌ |
| 10 | SpecReason | 2025 | 固定 fast/slow | Per-step | 轻量模型 | SCG 学环境拆分 | ❌ |
| 11 | **AUQ** | **2026** | **固定负向（低 confidence）** | **Per-step** | **无** | **SCG 方向自适应** | **✅ 已实现** |

---

## 现有实验 Baseline 全览

论文中的实验 baseline 共 **8 个**（6 个已有 + 2 个新增）：

| Baseline | 信号类型 | 方向假设 | 额外 Cost | 来源 |
|----------|---------|---------|----------|------|
| CATTS | Vote disagreement | 固定正向 | K=5 LLM calls/step | Phase 5 |
| SEAG | Mean logprob | 固定负向 | 0 | Phase 5 |
| CoRefine | Token entropy | 固定正向 | 0 | Phase 5 |
| CaTS | Platt-scaled confidence | 学习(1d) | 0 | Phase 5 |
| **AUQ** 🆕 | **Verbalized confidence** | **固定负向** | **1 LLM call/step** | **Phase 6.1** |
| **s1 Budget** 🆕 | **无（固定预算）** | **无** | **0** | **Phase 6.1** |
| + base_only | — | — | 0 | Core |
| + always_trigger | — | — | 每步 rollout | Core |

**信号类型覆盖完整性**: Token entropy, logprob confidence, calibrated confidence, vote disagreement, verbalized confidence, 无信号 — 覆盖了所有主流 gating 信号。

---

**⚠️ 注意**: 已确认的 arXiv ID: EGB (2503.21961, EACL 2026), AdaReasoner (2505.17312, NeurIPS 2025 Spotlight), CGR (2509.07820), RADAR (2509.25426), ARS (2510.00071), s1 (2501.19393), ODAR (2602.23681), CoD (2502.18600), AgentBench TTS (2602.18998), AUQ (2601.15703)。
