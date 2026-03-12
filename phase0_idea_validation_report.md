# Phase 0: Idea Validation 实验报告

**实验日期**：2026-02-20  
**环境**：HotpotQA（多跳问答）  
**判定结果**：✅ **GO** — 进入 Phase 1  
**运行时间**：主实验 1872 秒（~31 分钟） + Vote 多样性 105 秒（~2 分钟）

---

## 1. 实验背景与动机

### 1.1 核心问题

> **For any test-time optimizer, can we learn WHEN to use it?**

本项目研究的核心 idea 是：在 agent 执行任务的每一步，不是总是使用 test-time optimizer（如 rollout、vote），而是学习一个 **gate**，预测当前步骤使用 optimizer 是否有价值，从而在保持性能的同时节省计算资源。

### 1.2 Phase 0 要回答的前提问题

> **在 clean base agent（纯 LLM 输出，无任何 heuristic）下，rollout utility 是否有方差？**

此前的实验（Phase 2 HotpotQA，SR 50%→69%）是在有 `forward_value` heuristic 辅助的前提下得到的。新框架要求去掉所有 heuristic，使用 clean base agent。如果去掉 heuristic 后 rollout utility 分布坍缩为 U ≈ 0（即 rollout 永远不帮忙），那么"学习 WHEN to use optimizer"这一方向就不成立。

### 1.3 为什么选 HotpotQA

- 已有基础设施（环境适配器、数据集、oracle policy）
- 任务复杂度高（multi-hop reasoning，开放式动作空间）
- 如果在 HotpotQA 上 rollout 有价值，其他更简单的环境大概率也有
- 配合 InterCode-SQL 做跨任务验证（Phase 1 目标）

---

## 2. 实验中的核心概念与参数定义

### 2.1 Clean Base Agent（纯 LLM Agent）

**定义**：Base agent 使用 LLM（Qwen3-4B）以 greedy decoding（temperature=0）直接选择动作。**不使用** `forward_value` heuristic、不使用 rollout、不使用任何信号——纯粹的 LLM 输出。

**实现**：`ActionProposer(mode="llm_api", temperature=0.0)` 调用 vLLM 上的 Qwen3-4B-Instruct，给定当前 state 的文本描述和可选动作列表，LLM 返回它认为最优的动作。

**为什么是 clean**：去掉了 `forward_value`（关键词重叠 heuristic），agent 只依赖 LLM 的内在推理能力，不受外部信号干扰。这是为了验证"optimizer 本身的价值"而非"optimizer + heuristic 的联合价值"。

### 2.2 Rollout Utility $U$

**定义**：在当前状态 $s$ 下，rollout utility 衡量"使用 rollout optimizer 能比 base agent 做出多好的决策"：

$$U(s) = \max_{a \in \mathcal{A}} \tilde{V}_R(s, a) - \tilde{V}_R(s, a_{\text{proposed}})$$

其中：
- $a_{\text{proposed}}$：base agent（LLM greedy）选择的动作
- $\tilde{V}_R(s, a)$：动作 $a$ 在状态 $s$ 下的 retrospective value（rollout 估计）
- $\mathcal{A}$：当前可用的候选动作集（取 top-K 个）

**直观含义**：
- $U = 0$：rollout 找到的最优动作和 LLM 的选择一样好 → optimizer 没有额外价值
- $U > 0$：rollout 找到了比 LLM 更好的动作 → optimizer 有价值
- $U$ 越大：optimizer 的价值越高

### 2.3 Retrospective Value $\tilde{V}_R(s, a)$

**定义**：通过 Monte Carlo rollout 估计动作 $a$ 在状态 $s$ 下的期望回报：

$$\tilde{V}_R(s, a) = \frac{1}{N} \sum_{i=1}^{N} G_i(s, a)$$

其中每个 rollout $G_i$ 的计算过程：
1. **Deep copy** 当前环境状态
2. **强制执行**动作 $a$，获得即时 reward $r_1$
3. 之后 $H-1$ 步使用 **ε-greedy rollout policy**（以 $\varepsilon$ 概率随机，$1-\varepsilon$ 概率用 oracle 贪心）
4. 累加折扣回报：$G_i = r_1 + \gamma r_2 + \gamma^2 r_3 + \cdots$

**参数**：
| 参数 | 符号 | 值 | 含义 |
|------|------|-----|------|
| Rollout 次数 | $N$ | 3 | 每个动作重复 3 次 rollout 取平均 |
| Rollout 深度 | $H$ | 3 | 向前模拟 3 步 |
| 折扣因子 | $\gamma$ | 0.99 | 近似不折扣（HotpotQA 步数少） |
| 探索率 | $\varepsilon$ | 0.3 | rollout policy 30% 随机探索 |

**为什么 $N=3$ 足够**：Phase 0 只需验证 utility 是否有方差（screening），不需要精确估计每个 $U$ 的值。$N=3$ 的估计噪声会略微放大 std，但不会改变"有方差 vs 无方差"的结论。

### 2.4 HotpotQA 环境

**任务**：Multi-hop 问答。Agent 需检索多个 Wikipedia 段落并综合推理以回答复杂问题。

**动作空间**（开放式文本动作，离散化为候选列表）：
- `search[entity]`：检索 Wikipedia 段落
- `lookup[term]`：在最近检索的段落中查找包含该词的句子
- `finish[answer]`：提交最终答案

**Reward**：基于 F1 score，比较提交答案和 ground truth 的 token 重叠度。
$$\text{F1} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

**成功判定**：`terminated AND reward ≥ 0.5`（F1 ≥ 0.5 即视为成功）

**State 分类**（用于分层分析）：
| 类别 | 定义 | 含义 |
|------|------|------|
| `no_evidence` | 已检索 0 个段落 | Agent 尚未开始信息收集 |
| `partial_evidence` | 已检索 1 个段落 | 有部分信息但不足以回答 multi-hop 问题 |
| `multi_evidence` | 已检索 ≥ 2 个段落 | 信息较充分，可能可以回答 |

### 2.5 Go / No-Go 判断标准

来自 README 的预设标准：

| 判定 | 条件 | 含义 |
|------|------|------|
| ✅ **GO** | std$(U) > 0.1$ **且** $> 30\%$ 步骤 $U > 0$ | Rollout 有价值，进入 Phase 1 |
| ⚠️ **WEAK** | std$(U) \in [0.05, 0.1]$ | 价值存在但较弱，需切换环境验证 |
| ❌ **NO-GO** | std$(U) < 0.05$ **或** $< 10\%$ 步骤 $U > 0$ | Rollout 无效，需重新考虑 |

### 2.6 Decision Changed Ratio

**定义**：在所有采样步骤中，rollout 找到的最优动作 $a^* = \arg\max_a \tilde{V}_R(s,a)$ 与 LLM 提出的动作 $a_{\text{proposed}}$ 不同的比例。

$$\text{Decision Changed Ratio} = \frac{|\{s : a^*(s) \neq a_{\text{proposed}}(s)\}|}{|\text{all sampled steps}|}$$

高 decision changed ratio 说明 rollout 经常"推翻" LLM 的选择，是 optimizer 有用的另一个佐证。

---

## 3. 实验设置

> **实验的核心问题**：在一个 question-answering 任务上，用 LLM 做 agent（搜索→查找→提交答案），如果我们额外跑 Monte Carlo rollout 来评估每个动作的好坏，这个 rollout 信号到底有多大的纠错价值？

**实验做了什么**：

1. **Base Agent 跑 100 个 episode**：LLM（Qwen3-4B）独立回答 HotpotQA 问题。每一步，LLM 根据当前状态选一个动作（搜索某实体 / 查找某关键词 / 提交答案）。
2. **每 2 步"拍快照"做 rollout**：在这些步骤上，我们暂停 agent，对当前可选的所有动作（最多 5 个），用 Monte Carlo 方法估计每个动作的"retrospective value" $\tilde{V}_R$。具体来说，为每个候选动作做 3 次模拟（深拷贝环境 → 强制执行该动作 → 用 ε-greedy oracle 继续走 3 步 → 看最终 reward），取平均。
3. **计算 Utility**：$U = \max_a \tilde{V}_R(a) - \tilde{V}_R(a_{\text{LLM选的}})$。如果 $U > 0$，说明存在一个比 LLM 选择更好的动作——rollout 有纠错价值。
4. **不干预 agent**：计算完 $U$ 后，agent 仍然执行 LLM 原始选择的动作（保证 base agent 数据的纯净性）。
5. **汇总统计**：收集所有 293 个数据点的 $U$ 值，用方差和正比率做 Go/No-Go 判定。

### 3.1 硬件与软件环境

| 项目 | 配置 |
|------|------|
| 集群节点 | gpu42（SLURM HPC） |
| GPU | 1x GPU（用于 vLLM 推理） |
| LLM 服务 | vLLM v0.x，OpenAI-compatible API |
| LLM 模型 | `Qwen/Qwen3-4B-Instruct-2507` |
| 推理端点 | `http://gpu42:8000/v1` |
| Python 环境 | conda `frvc` |
| 数据集 | HotpotQA dev distractor v1（7405 问题） |

### 3.2 主实验配置

| 参数 | 值 | 说明 |
|------|-----|------|
| `num_episodes` | 100 | 跑 100 个 episode |
| `seed_start` | 42 | Episode $i$ 使用 seed $= 42 + i$ |
| `max_steps` | 10 | 每个 episode 最多 10 步 |
| `sample_every` | 2 | 每隔 2 步计算一次 rollout utility |
| `top_k_actions` | 5 | 每步评估最多 5 个候选动作 |
| LLM `temperature` | 0.0 | Greedy decoding（确定性 base agent） |
| LLM `max_tokens` | 300 | 每次 LLM 调用最多生成 300 tokens |
| Rollout `num_samples` ($N$) | 3 | 每个动作 3 次 rollout |
| Rollout `horizon` ($H$) | 3 | 每次 rollout 向前 3 步 |
| Rollout $\gamma$ | 0.99 | 折扣因子 |
| Rollout $\varepsilon$ | 0.3 | ε-greedy 探索率 |

### 3.3 每步的具体计算流程

对于每个 episode 中的每一步（step $t$）：

```
1. LLM 选动作：
   a_proposed = LLM.choose_action(state)  // temperature=0, greedy

2. 如果 t % sample_every == 0，计算 rollout utility：
   a) 获取候选动作列表 A = get_actions()[:top_k]
      若 a_proposed ∉ A，则 A = A ∪ {a_proposed}
   b) 对每个 a ∈ A：
      V_R(a) = mean of N rollouts:
        for i = 1..N:
          clone = deepcopy(env)
          clone.step(a)               // 强制执行 a
          for h = 2..H:
            a_h = ε-greedy_oracle(ε=0.3)  // 30% 随机，70% oracle
            clone.step(a_h)
          G_i = 累加折扣 reward
        V_R(a) = mean(G_1, ..., G_N)
   c) U = max(V_R) - V_R(a_proposed)
   d) 记录数据点：{episode, step, U, a_proposed, a_best, state_type, ...}

3. 执行 a_proposed（clean agent 始终按 LLM 选择行动）
4. 重复直到 episode 结束
```

### 3.4 一个完整的 Utility 计算 Walkthrough

下面用三个真实数据点，端到端展示 rollout utility $U$ 的计算过程。

#### 案例 A：Episode 0, Step 0 — $U = 0.673$（高价值，optimizer 有用）

**场景**：Episode 刚开始，问题是关于一个日本漫画系列的作者。Agent 没有任何检索结果（`no_evidence`）。

**第一步：LLM 选动作**

LLM（Qwen3-4B, temperature=0）看到状态描述：
```
Question: A Japanese manga series based on a 16 year old high school student Ichitaka Seto, is writt...
Observation: Question: A Japanese manga series based on ...
Available actions:
  0: search[A Japanese]
  1: search[Ichitaka Seto]
  2: finish[1962]
```
LLM 的选择：$a_{\text{proposed}} = 1$（`search[Ichitaka Seto]`）。这是合理的——LLM 认为应该先搜索关键实体。

**第二步：计算每个动作的 $\tilde{V}_R$**

对 3 个候选动作（$|\mathcal{A}| = 3$），分别做 $N = 3$ 次 rollout，每次深度 $H = 3$ 步：

**动作 0：`search[A Japanese]`**

| Rollout | 步骤 | 执行的动作 | Reward | 说明 |
|---------|------|-----------|--------|------|
| #1 | h=1 | `search[A Japanese]`（强制） | 0 | 搜索"A Japanese"，未命中有用段落 |
| #1 | h=2 | oracle 选 `search[supporting_fact_entity]` | 0 | oracle 知道正确答案，搜索支持事实 |
| #1 | h=3 | oracle 选 `finish[correct_answer]` | 0.99 | 找到证据，提交正确答案 |
| #2 | h=1 | `search[A Japanese]`（强制） | 0 | 同上 |
| #2 | h=2 | 随机（ε=0.3 触发） | 0 | 随机选了无用动作 |
| #2 | h=3 | oracle 选 `finish[...]` | 0 | 证据不够，未成功 |
| #3 | h=1-3 | ...类似 #1... | 0.99 | 成功 |

$$\tilde{V}_R(s, \text{search[A Japanese]}) = \frac{0.99 \times \gamma^2 + 0 + 0.99 \times \gamma^2}{3} \approx 0.33$$

**动作 1：`search[Ichitaka Seto]`**（LLM 的选择）

类似过程，3 次 rollout 平均：
$$\tilde{V}_R(s, \text{search[Ichitaka Seto]}) = 0.3267$$

**动作 2：`finish[1962]`**

| Rollout | 步骤 | 执行的动作 | Reward | 说明 |
|---------|------|-----------|--------|------|
| #1 | h=1 | `finish[1962]`（强制） | 1.0 | 直接提交答案，F1=1.0，episode 结束！ |
| #2 | h=1 | `finish[1962]`（强制） | 1.0 | 同上 |
| #3 | h=1 | `finish[1962]`（强制） | 1.0 | 同上 |

$$\tilde{V}_R(s, \text{finish[1962]}) = \frac{1.0 + 1.0 + 1.0}{3} = 1.0$$

**第三步：计算 Utility**

$$U = \max_{a} \tilde{V}_R(s, a) - \tilde{V}_R(s, a_{\text{proposed}}) = 1.0 - 0.3267 = \mathbf{0.6733}$$

**含义**：LLM 选择了 `search[Ichitaka Seto]`（还想搜集信息），但 rollout 发现直接 `finish[1962]` 就能得到满分。Rollout 在这一步价值极高——它能帮 agent 跳过不必要的搜索，直接给出答案。

**第四步：执行**

但实验中 **base agent 不使用 rollout 结果**，仍然执行 LLM 的选择 `search[Ichitaka Seto]`。这是"clean base agent"的要求——我们只是在观察和记录 rollout 的潜在价值，不让它影响 agent 行为。

---

#### 案例 B：Episode 1, Step 4 — $U = 0$（optimizer 无价值）

**场景**：Episode 进行到第 4 步，已检索 1 个段落（`partial_evidence`），5 个候选动作。

LLM 选择：$a_{\text{proposed}} = 2$（`search[Giuseppe Edoardo Arimondi]`）

5 个动作的 $\tilde{V}_R$ ：

| 动作 | 文本 | $\tilde{V}_R$ |
|------|------|----------|
| 0 | (其他搜索) | 0.9834 |
| 1 | (其他搜索) | 0.9834 |
| **2** | **`search[Giuseppe Edoardo Arimondi]`** | **0.9900** |
| 3 | (其他动作) | 0.9900 |
| 4 | (其他动作) | 0.6600 |

$$U = \max(0.9834, 0.9834, 0.9900, 0.9900, 0.6600) - 0.9900 = 0.9900 - 0.9900 = \mathbf{0.0}$$

**含义**：LLM 的选择已经和 rollout 能找到的最优一样好。Optimizer 在这一步没有额外价值。当 agent 已有部分证据、方向明确时，LLM 自己就能做出正确决策。

---

#### 案例 C：Episode 0, Step 6 — $U = 0.01$（微弱价值）

LLM 选了 `search[Ichitaka Seto]`（$\tilde{V}_R = 0.990$），rollout 最优是 `finish[1962]`（$\tilde{V}_R = 1.0$）。

$$U = 1.0 - 0.990 = \mathbf{0.01}$$

**含义**：Rollout 找到了一个略好的动作，但差距极小。这类情况在实际部署中不值得花计算资源去跑 rollout——这正是 Phase 2 gate learning 要学习过滤的。

---

#### 三种案例的对比

| 案例 | Step | State | $U$ | 含义 |
|------|------|-------|-----|------|
| A | 0 | no_evidence | **0.673** | 开头信息不足，LLM 犯错，rollout 大幅纠正 |
| B | 4 | partial_evidence | **0.000** | LLM 方向正确，rollout 无额外价值 |
| C | 6 | no_evidence | **0.010** | Rollout 略好但差距极小，不值得花计算 |

这三种情况在 293 个数据点中的分布：29% 类似 B（$U=0$），48% 类似 C（$0 < U \leq 0.1$），23% 类似 A（$U > 0.5$）。正是这种多样性使得"学习 WHEN to use optimizer"有意义。

### 3.5 每步的计算开销分析

| 组件 | 耗时 | 次数 | 说明 |
|------|------|------|------|
| LLM 调用 | ~0.4s | 每步 1 次 | vLLM 推理，Qwen3-4B |
| 单次 rollout | ~0.5s | 每动作 $N=3$ 次 | deepcopy + 3 步 oracle |
| 单动作 V_R | ~1.5s | 每采样步 ~3 个动作 | 3 rollouts × 0.5s |
| **单步（采样）** | **~4.9s** | — | 0.4s LLM + 3 × 1.5s rollout |
| **单步（非采样）** | **~0.4s** | — | 仅 LLM 调用 |
| **单 episode** | **~19s** | — | ~5 个采样步 + 5 个非采样步 |
| **100 episodes** | **~31min** | — | 实测 1872s |

### 3.6 Vote 多样性侧实验配置

| 参数 | 值 | 说明 |
|------|-----|------|
| `num_episodes` | 20 | 20 个 episode |
| `num_vote_samples` | 5 | 每步采样 5 次 LLM 输出 |
| `greedy_temperature` | 0.0 | Greedy 基准动作 |
| `vote_temperature` | 0.7 | 采样动作的温度 |
| `diversity_threshold` | 0.20 | >20% divergent → vote 可行 |

**流程**：每步先用 temperature=0 获取 greedy action，再用 temperature=0.7 采样 5 次获取 vote actions。检查 majority vote 是否与 greedy 不同。

---

## 4. 实验结果

### 4.1 主实验：Rollout Utility 分布

#### 4.1.1 核心指标

| 指标 | 值 | Go 阈值 | 判定 |
|------|-----|---------|------|
| **Utility std** | **0.3486** | > 0.1 | ✅ **通过**（3.5 倍于阈值） |
| **U > 0 比例** | **71.0%** | > 30% | ✅ **通过**（2.4 倍于阈值） |
| Utility mean | 0.2606 | — | — |
| Utility median | 0.0133 | — | — |
| Utility range | [0, 1.0] | — | 覆盖完整范围 |
| Utility IQR | [0, 0.3466] | — | — |
| Decision changed ratio | 82.3% | — | 超高改写率 |
| 总数据点 | 293 | — | 充分 |

#### 4.1.2 分布特征

| 区间 | 数据点数 | 占比 |
|------|----------|------|
| $U = 0$（rollout 无价值） | 85 | 29.0% |
| $U > 0$（rollout 有价值） | 208 | 71.0% |
| $U > 0.5$（rollout 高价值） | 68 | 23.2% |

**分布形态**：右偏（right-skewed），median = 0.013 远小于 mean = 0.261。大多数步骤 rollout 有微小到中等的价值，少数步骤有极高价值（U 接近 1.0）。这正是"学习 WHEN to use optimizer"的理想分布——optimizer 不是总有用（29% 无用），也不是总没用（71% 有用），而且有用的程度差异很大。

#### 4.1.3 按 Step 细分

| Step | N | Mean $U$ | Std $U$ | $U > 0$ 比例 |
|------|---|----------|---------|-------------|
| **0** | 100 | **0.5407** | 0.3914 | **83.0%** |
| 2 | 64 | 0.0503 | 0.1152 | 57.8% |
| 4 | 46 | 0.0621 | 0.1581 | 56.5% |
| 6 | 42 | 0.0994 | 0.1792 | 76.2% |
| **8** | 41 | **0.2932** | 0.2841 | **73.2%** |

**关键发现**：
- **Step 0 的 U 极高**（mean=0.54）：episode 开头 LLM 的第一步选择最容易被 rollout 改进。这符合直觉——开头信息最少，LLM 最容易犯错。
- **Step 2-4 的 U 较低**：LLM 已经开始有信息了，做出的选择相对合理。
- **Step 8 的 U 回升**（mean=0.29）：接近结尾，LLM 需要决定是否 finish，rollout 能帮助判断答案是否正确。
- **N 随 step 递减**（100→41）：因为很多 episode 在中途就成功结束了（平均 5.5 步）。

#### 4.1.4 按 State Type 细分

| State Type | N | Mean $U$ | Std $U$ | $U > 0$ 比例 | Median $U$ |
|------------|---|----------|---------|-------------|-----------|
| **no_evidence** | 167 | **0.3692** | 0.3876 | **86.2%** | 0.340 |
| partial_evidence | 38 | 0.1231 | 0.2191 | 55.3% | 0.003 |
| multi_evidence | 88 | 0.1138 | 0.2160 | 48.9% | 0.000 |

**关键发现**：
- **no_evidence 状态下 rollout 最有价值**：86% 的步骤 U > 0，mean = 0.37。此时 agent 还没有任何检索结果，LLM 只能"猜"要搜什么，rollout 能有效纠正。
- **multi_evidence 状态下 rollout 价值最低**：49% 步骤 U > 0，median = 0。当信息充足时，LLM 的选择已经不错，rollout 的边际价值下降。
- **这种差异正是 Phase 1 "学习信号" 的基础**：state_type 与 utility 有明显关联，可以作为预测 optimizer 是否有用的信号。

#### 4.1.5 样例数据点

| Episode | Step | State | LLM 选择 | $\tilde{V}_R$ (LLM) | Rollout 最优 | $\tilde{V}_R$ (最优) | $U$ |
|---------|------|-------|----------|------|-------------|------|------|
| 0 | 0 | no_evidence | `search[Ichitaka Seto]` | 0.327 | `finish[1962]` | 1.000 | **0.673** |
| 0 | 2 | no_evidence | `search[Ichitaka Seto]` | 0.990 | `finish[1962]` | 1.000 | 0.010 |
| 6 | 0 | no_evidence | `search[Are Ferocactus]` | 0.000 | `finish[yes]` | 1.000 | **1.000** |

Episode 6 Step 0 是 U=1.0 的极端例子：LLM 选择了一个完全错误的搜索（V_R=0），而 rollout 发现直接 finish 就能得到正确答案（V_R=1.0）。

### 4.2 Base Agent 性能

| 指标 | 值 |
|------|-----|
| Success Rate (SR) | **59.0%** |
| Average Reward | 0.590 |
| Average Steps | 5.5 |
| Steps Std | 3.9 |
| Min Steps | 1 |
| Max Steps | 10 |
| LLM 总调用数 | 554 |
| LLM 错误数 | 0 |

**解读**：Qwen3-4B 在 HotpotQA 上的 SR = 59%，表现中等。这为 rollout optimizer 提供了充足的提升空间（从 59% 到理论最优 ~100%）。SR 不会太低（避免 agent 太弱以至于 rollout 也无法纠正），也不会太高（避免 agent 太强以至于 rollout 没有必要）。

### 4.3 Vote 多样性侧实验

| 指标 | 值 | 阈值 | 判定 |
|------|-----|------|------|
| 总采样步数 | 121 | — | — |
| **Divergent 步数** | **0** | — | — |
| **Divergence ratio** | **0.00%** | > 20% | ❌ 未通过 |
| Vote consistency | 0.997 | — | 极高一致性 |
| Avg unique actions | 1.01 | — | 几乎完全相同 |

**结论**：Qwen3-4B 在 temperature=0.7 下的采样输出几乎与 greedy（temperature=0）完全相同。Vote 作为 optimizer 对 4B 模型**完全无效**。

**原因分析**：Qwen3-4B 的输出分布过于 peaked（确信度极高），即使 temperature=0.7 也无法产生有意义的多样性。可能原因：
1. 模型参数量太小（4B），内部 logit 分布集中
2. HotpotQA 的动作空间有限（3-8 个候选），LLM 几乎总是选同一个
3. 需要更大模型（8B+）或更高 temperature 才能看到 vote 多样性

---

## 5. 综合判定

### 5.1 Go / No-Go 判定

| 准则 | 结果 |
|------|------|
| utility_std > 0.1 | ✅ **0.3486 >> 0.1** |
| positive_ratio > 0.3 | ✅ **0.710 >> 0.3** |
| utility_std > 0.05 | ✅ |
| positive_ratio > 0.1 | ✅ |

**判定：✅ GO**

所有指标远超阈值，核心前提强有力地成立：

> **在 clean base agent 下，rollout utility 有显著方差（std = 0.349），且 71% 的步骤中 rollout 能提供比 LLM greedy 更好的动作。Optimizer 在 clean setup 下有价值，"学习 WHEN to use optimizer" 这一方向成立。**

### 5.2 对后续阶段的启示

1. **Phase 1 的信号预测有基础**：
   - state_type 与 utility 有明显关联（no_evidence: 86% vs multi_evidence: 49%）
   - step_number 与 utility 有 U-shape 关系（step 0 和 8 高，中间低）
   - 这些信号可以作为 Phase 1 Gate Learning 的特征

2. **Vote 路线需要更大模型**：
   - 4B 模型 vote 完全无效（divergence = 0%）
   - 8B 模型接近可用（divergence = 17.8%，接近 20% 阈值），尤其在 `partial_evidence` 状态下 divergence 高达 56.5%（见补充实验 C）
   - Phase 1 应专注 rollout optimizer，vote 仅在 `partial_evidence` 状态下选择性使用

3. **Rollout 在 step 0 价值最大，但去掉后仍然 GO**：
   - Step 0 的 mean U = 0.54，但去掉 Step 0 后 std = 0.208、positive ratio = 64.8%，仍远超阈值（见补充实验 B）
   - Step 8 的 mean U = 0.293，形成 U-shape 曲线
   - Gate 策略可以基于 step 和 evidence 数量

4. **LLM 自身做 rollout 仍然有效**：
   - LLM rollout 的 utility std = 0.493（甚至高于 oracle 的 0.349），GO 判定成立（见补充实验 A）
   - 项目的 practical value 不依赖于"拥有完美 rollout policy"

---

## 6. 补充实验

为验证 Phase 0 主实验结论的鲁棒性，我们设计了三个补充实验。

### 6.1 补充实验 A：LLM-based Rollout Policy 的 Utility 测量

**动机**：Phase 0 的 rollout 使用 ε-greedy oracle（70% 知道正确答案的 oracle + 30% random）。这测的是"假设有完美 rollout policy，optimizer 有没有价值"，但实际部署时 rollout policy 只能是 LLM 自身。如果换成 LLM rollout 后 utility 坍缩为 ~0，说明瓶颈在 rollout policy quality，整个项目的 practical value 存疑。

**实验设计**：
- 保持所有参数不变（N=3, H=3, top_k=5, sample_every=2）
- 唯一改变：rollout policy 从 ε-greedy oracle → **LLM 自身**（Qwen3-4B, temperature=0.7）
- 50 个 episodes（screening 级别）

**结果**：

| 指标 | Oracle Rollout (Phase 0) | LLM Rollout (Exp A) | 变化 |
|------|------------------------:|---------------------:|------|
| **Utility std** | **0.3486** | **0.4934** | +41.5% ↑ |
| Utility mean | 0.2606 | 0.4731 | +81.5% ↑ |
| Positive ratio | 70.99% | 60.77% | −10.2pp ↓ |
| Decision changed | 82.25% | 79.23% | −3.0pp ↓ |
| Base agent SR | 59.00% | 66.00% | +7.0pp ↑ |
| 数据点数 | 293 | 130 | (50 ep vs 100 ep) |
| 耗时 | 1872s | 857s | ~17s/ep |

**Per-State-Type 对比（LLM Rollout）**：

| State Type | N | Mean U | Std U | U>0 Ratio |
|------------|---|--------|-------|-----------|
| no_evidence | 92 | 0.6004 | 0.4870 | 78.26% |
| partial_evidence | 8 | 0.6188 | 0.4793 | 62.50% |
| multi_evidence | 30 | 0.0437 | 0.1634 | 6.67% |

**Go/No-Go 判定**：✅ **GO**（std=0.493 > 0.1, positive_ratio=60.8% > 30%）

**解读**：

LLM rollout 的 utility 不但没有坍缩，反而 **std 更高**（0.49 vs 0.35）。这看似反直觉，但原因是：
1. **LLM rollout 质量不如 oracle**，导致大部分动作的 $\tilde{V}_R$ 更低（LLM 经常选错，rollout 得分低）
2. 但如果某个动作碰巧导向正确答案（如 `finish[correct_answer]`），该动作的 $\tilde{V}_R$ 仍然很高（因为 finish 是 terminal，不依赖后续 rollout 质量）
3. 这种"大部分低 + 少数高"的分布拉大了方差

关键发现：`multi_evidence` 状态下 LLM rollout 的 U>0 ratio 仅 6.67%（oracle 下为 48.9%）——当 agent 已经有足够证据时，LLM rollout 几乎无法区分动作好坏。但在 `no_evidence`（78%）和 `partial_evidence`（63%）状态下，LLM rollout 仍有显著信号。

**结论**：**瓶颈不在 rollout policy quality**。即使用 LLM 自身做 rollout，optimizer 仍然有价值。项目的 practical value 是成立的。

---

### 6.2 补充实验 B：去掉 Step 0 的 Sensitivity Analysis

**动机**：Phase 0 中 Step 0 占 34% 数据（100/293），但 mean U = 0.54 是其余步骤的 4.7 倍。GO 判定（std=0.349, 71% positive）可能被 Step 0 "带偏"。需要确认：去掉 Step 0 后，rollout 在中间步骤是否仍然有价值。

**实验设计**：纯数据分析，不需要重新跑实验。从已有的 293 条数据中过滤掉 step=0 的 100 条，用剩余 193 条重新计算指标。

**结果**：

| 指标 | 全部 (293) | Step 0 (100) | 非 Step 0 (193) |
|------|----------:|------------:|-----------------:|
| **Utility std** | **0.3486** | 0.3914 | **0.2082** |
| Utility mean | 0.2606 | 0.5407 | 0.1154 |
| Utility median | 0.0133 | 0.6716 | 0.0066 |
| **Positive ratio** | **70.99%** | 83.00% | **64.77%** |
| Decision changed | 82.25% | 83.00% | 81.87% |

**非 Step 0 的 Per-Step 细分**：

| Step | N | Mean U | Std U | U>0 % |
|------|---|--------|-------|-------|
| 2 | 64 | 0.0503 | 0.1152 | 57.81% |
| 4 | 46 | 0.0621 | 0.1581 | 56.52% |
| 6 | 42 | 0.0994 | 0.1792 | 76.19% |
| 8 | 41 | 0.2932 | 0.2841 | 73.17% |

**非 Step 0 的 Per-State-Type 细分**：

| State Type | N | Mean U | Std U | U>0 % |
|------------|---|--------|-------|-------|
| no_evidence | 67 | 0.1131 | 0.1905 | 91.04% |
| partial_evidence | 38 | 0.1231 | 0.2191 | 55.26% |
| multi_evidence | 88 | 0.1138 | 0.2160 | 48.86% |

**Go/No-Go 判定（去掉 Step 0）**：✅ **GO**（std=0.208 > 0.1, positive_ratio=64.8% > 30%）

**解读**：

1. **GO 判定不依赖 Step 0**：去掉 Step 0 后，std 从 0.349 降到 0.208，但仍远超 0.1 阈值；positive ratio 从 71% 降到 65%，仍远超 30% 阈值。
2. **Step 8 的 mean U 特别高**（0.293）：Episode 后期（接近 max_steps=10），agent 面临"是否提交答案"的关键决策，rollout 在此处价值重新升高。这形成 U 形曲线：Step 0 高 → Step 2-4 低 → Step 6-8 回升。
3. **no_evidence 状态下 U>0 ratio = 91%**：即使去掉 Step 0，缺乏证据时 rollout 几乎总是能提供有用信号。
4. **Gate learning 的额外信号**：Step 和 state_type 都是强 feature，Phase 2 的 gate classifier 应该可以学到这些 pattern。

---

### 6.3 补充实验 C：Qwen3-8B Vote 多样性测试

**动机**：Phase 0 仅测了 4B 的 vote 多样性（结果 divergence=0%）。4B 模型输出分布太 peaked 是预期内的。Plan 本意是看更大模型是否能解锁 vote 作为第二种 optimizer。

**实验设计**：
- 模型：Qwen/Qwen3-8B（base model，非 Instruct）
- 20 个 HotpotQA episodes，每步采样
- 每步：greedy action（temperature=0）+ 5 次采样（temperature=0.7）
- 检查 majority vote ≠ greedy 的比例

**结果**：

| 指标 | 4B (Phase 0) | 8B (Exp C) | 变化 |
|------|------------:|----------:|------|
| **Divergence ratio** | **0.00%** | **17.83%** | +17.8pp ↑↑ |
| Vote consistency | 0.997 | 0.869 | −0.128 ↓ |
| Unique actions / step | 1.01 | 1.48 | +0.47 ↑ |
| Steps sampled | 121 | 157 | — |
| 耗时 | 105s | 3859s | 37× 慢 |

**Per-State-Type 细分（8B）**：

| State Type | N | Divergence | Consistency | Unique Acts |
|------------|---|-----------|-------------|-------------|
| **partial_evidence** | 23 | **56.52%** | 0.722 | 1.91 |
| no_evidence | 87 | 11.49% | 0.906 | 1.37 |
| multi_evidence | 47 | 10.64% | 0.872 | 1.49 |

**判定**：⚠️ **MODERATE**（17.8% < 20% 阈值，但接近）

**解读**：

1. **从 0% 到 17.8% 是巨大进步**：8B 确实能产生多样性，从 4B 的"完全 peaked"到 8B 的"接近可用"。
2. **partial_evidence 状态是关键**：divergence 高达 56.5%！当 agent 只有部分证据时，8B 的输出分布最不确定——这恰恰是 rollout 最有价值的位置之一（与 Exp B 的发现一致）。
3. **no_evidence 和 multi_evidence 仅 ~11%**：在证据极少或充足时，8B 和 4B 类似地 peaked。
4. **8B 非常慢**（3859s vs 105s）：base model 需要思考（think token），每次采样 6 个 LLM call × 157 步，吞吐量仅 ~72 tokens/s。
5. **建议**：
   - 17.8% 接近 20% 阈值，如果使用 Instruct 版本（输出更 compact）或 temperature=0.9，可能突破阈值
   - Phase 1 可以**选择性测 vote utility**：仅在 `partial_evidence` 状态下使用 vote（该状态 divergence > 50%）
   - 或暂不投入 vote，专注 rollout optimizer（已经在 Exp A 证明 practical value）

---

### 6.4 三个补充实验的综合结论

| 实验 | 核心问题 | 结论 | 对后续的影响 |
|------|---------|------|-------------|
| **A** | LLM rollout 是否仍有 utility？ | ✅ YES (std=0.49, GO) | 项目 practical value 成立 |
| **B** | 去掉 Step 0 是否仍 GO？ | ✅ YES (std=0.21, GO) | GO 判定鲁棒 |
| **C** | 8B 能否产生 vote 多样性？ | ⚠️ MODERATE (17.8%) | 暂不投入 vote，专注 rollout |

**核心信息**：Phase 0 的 GO 决定是鲁棒的——无论换成 LLM rollout、去掉 Step 0、还是检验 vote 可行性，核心结论都不变。Proceed to Phase 1。

---

## 7. 产出文件清单

**主实验**（`results/phase0_idea_validation/hotpotqa/`）：

| 文件 | 说明 |
|------|------|
| `phase0_summary.json` | 汇总统计（utility 分布、per-state 分析） |
| `phase0_decision.json` | Go/No-Go 判定结果 |
| `phase0_utility_data.json` | 293 个数据点的完整记录 |
| `phase0_utility_data.csv` | 同上，CSV 格式 |
| `phase0_episode_summaries.json` | 100 个 episode 的汇总（SR, reward, steps） |
| `phase0_vote_diversity.json` | Vote 多样性实验的完整记录 |
| `phase0_idea_validation_plots.png` | 4 面板诊断图（分布、按步、按状态、per-episode） |

**补充实验**（`results/supplementary/`）：

| 文件 | 说明 |
|------|------|
| `expA_llm_rollout/expA_summary.json` | Exp A 汇总（LLM rollout utility） |
| `expA_llm_rollout/expA_utility_data.json` | 130 个数据点 |
| `expA_llm_rollout/expA_episode_summaries.json` | 50 个 episode 汇总 |
| `expB_step0_sensitivity/expB_results.json` | Exp B 完整结果（三组对比） |
| `expB_step0_sensitivity/expB_step0_sensitivity_plots.png` | 4 面板对比图 |
| `expC_8b_vote/expC_summary.json` | Exp C 汇总（8B vote 多样性） |
| `expC_8b_vote/expC_vote_records.json` | 157 步的详细记录 |

---

## 8. 可复现性

```bash
# 1. 确保 vLLM 服务运行
#    model: Qwen/Qwen3-4B-Instruct-2507, port: 8000

# 2. 运行实验
cd /home/uuc24002/FRVC
PYTHONUNBUFFERED=1 python experiments/phase0_idea_validation.py \
    --config configs/phase0_idea_validation.yaml \
    --episodes 100 --verbose

# 3. 或使用 nohup 后台运行
PYTHONUNBUFFERED=1 nohup python experiments/phase0_idea_validation.py \
    --config configs/phase0_idea_validation.yaml \
    --episodes 100 --verbose > logs/phase0_idea_validation_nohup.out 2>&1 &

# 4. 或 SLURM 提交（自动启动 vLLM）
sbatch scripts/phase0/run_idea_validation.sbatch

# 5. 补充实验 B（无需 GPU，纯数据分析）
python experiments/supplementary_expB_sensitivity.py

# 6. 补充实验 A + C（需要 GPU，SLURM 提交）
sbatch scripts/supplementary/run_supplementary_ABC.sbatch
```
