# Phase 6.1: 新环境扩展计划

**Date**: 2026-03-19 (updated: Step 0 全部 GO, FEVER Step 1 完成, 其余 Step 1 运行中)
**前置**: Phase 5 完成 (6 环境: 3主+2诊断+1限制), Phase 6 Path C 全部 NO-GO, Phase 6.1b AUQ+s1 baselines 27/30 完成
**目标**: 新增 1-2 个有效环境，补充 code (harder) / fact-verification 类型
**候选**: APPS Interview, FEVER, DS-1000, CRUXEval
**GO 条件**: base SR ∈ [5%, 85%] AND always_trigger SR > base SR + 3pp

### Step 0 结果：4/4 全部 GO ✅

| 环境 | base SR | always SR | Δ | GO? | Job |
|------|:-------:|:---------:|:---:|:---:|-----|
| **APPS Interview** | 56% | 82% | +26pp | ✅ GO | 23228574_0 |
| **FEVER** | 32% | 100% | +68pp | ✅ GO | 23228661 |
| **DS-1000** | 20% | 100% | +80pp | ✅ GO | 23228574_2 |
| **CRUXEval** | 76% | 100% | +24pp | ✅ GO | 23228574_3 |

**注意**: FEVER/DS-1000/CRUXEval 的 always_sr=100% 可能因 generic rollout 使用了 oracle action，实际 Step 2 中 SR 会低一些。

### Step 1 结果：FEVER 完成，其余运行中 (Job 23228761)

**FEVER Signal Discovery (N=282 steps, 200 episodes)**:

| Rank | Signal | Spearman ρ | p-value | 方向 |
|:---:|--------|:---:|:---:|:---:|
| 1 | **step_count** | **−0.619** | 2.9e-31 *** | 负 |
| 2 | **is_finish_proposed** | **−0.555** | 3.8e-24 *** | 负 |
| 3 | **evidence_count** | **−0.546** | 2.6e-23 *** | 负 |
| 4 | claim_length | −0.198 | 8.3e-4 ** | 负 |
| 5 | token_entropy | −0.119 | 0.045 * | 负 |
| (cat) | action_type | η²=0.314 | — | classify/search/lookup |
| (cat) | state_category | η²=0.303 | — | no/partial/sufficient evidence |

- **Utility stats**: mean=0.515, positive_rate=51.8% (rollout 约一半时间有效)
- **Token entropy 方向**: 负（与 HotpotQA 一致）
- **关键发现**: FEVER 信号方向与 HotpotQA 完全一致（同为 search-based QA），但信号更强 (ρ=−0.619 vs HotpotQA ρ=−0.494)。验证了 "同一 agent 框架下方向一致" 假设。

---

## 0. 动机

### 当前环境矩阵

| 环境 | 类型 | 定位 | Rollout 策略 | 关键特征 | SCG vs 最佳新BL |
|------|------|------|-------------|---------|:-----------:|
| HotpotQA | QA/推理 | 主实验 | per-action exhaustive (K=5, H=3) | 信号强 (ρ=−0.494) | ≈ (noise) |
| APPS (Intro) | 代码生成 | 主实验 | K-variant generation (K=5) | 弱信号 (ρ=0.155) | s1 > SCG ⚠️ |
| WebShop | Web 交互 | 主实验 | per-action exhaustive (K=5, H=3) | 方向反转 (ρ=+0.444) | **SCG >> all** 🔥 |
| TWExpress | 文本游戏 | 诊断 (rollout-safe) | per-action exhaustive (K=2, H=3) | rollout 永不有害 | SCG > AUQ/s1 |
| Plancraft | 制造规划 | 诊断 (rollout-harmful) | per-action exhaustive (K=2, H=3) | rollout 本质有害 | 全 < base |
| BabyAI | 导航 | Limitation | per-action exhaustive (K=2, H=3) | 信号不存在 | — |

### 新增 Competing Baselines（2026-03-18 实现，实验 27/30 完成）

Phase 6.1b 新增了两个 competing baselines（AUQ + s1 Budget Forcing），已在 5 个现有环境上跑完 27/30 runs（3 个因 vLLM 启动超时失败，已提交 rerun Job 23228573）。

**新 Baseline 结果 vs 现有方法**:

```
┌──────────────┬──────────────────────────────────────────────────────────────────┐
│              │  base_only    SCG       CaTS(最佳CB)  AUQ 🆕      s1 Budget 🆕  │
│ Environment  │  SR   Cost   SR  Cost   SR   Cost    SR   Cost    SR   Cost     │
├──────────────┼──────────────────────────────────────────────────────────────────┤
│ HotpotQA     │ 49.0% 1.0×  96.8% 6.6×  93.2% 10.6×  97.0% 10.2×  97.0% 6.3× │
│ APPS         │ 58.5% 1.0×  58.8% 1.2×  59.0%  1.0×  61.3%  3.1×  63.7% 2.0× │
│ WebShop      │  7.2% 1.0×  43.7% 1.3×  30.5%  3.4×  35.7%  5.9×   9.3% 1.9× │
│ TWExpress    │ 67.5% 1.0×  97.0% 1.0×  96.7%  1.4×  95.5%  —     95.0% —     │
│ Plancraft    │ 29.8% 1.0×  21.5% 3.3×  22.3%  4.1×  24.2%  —     18.3% —     │
└──────────────┴──────────────────────────────────────────────────────────────────┘
```

**关键发现**:
1. **HotpotQA**: AUQ/s1 均达 97.0% ≈ always_trigger，与 SCG (96.8%) 差距为噪声。但 HotpotQA rollout 极强（base→always +48pp），任何策略都接近 ceiling
2. **APPS**: s1 (63.7%) > AUQ (61.3%) > CaTS (59.0%) > SCG (58.8%) — s1 仅 1 次 rollout 在 step 0 碰巧有效，但 cost 是 SCG 的 1.7 倍
3. **WebShop**: SCG (43.7%) >> AUQ (35.7%) >> s1 (9.3%) — **showcase 环境**，s1 崩溃证明 "盲目在 step 0 rollout" 在 WebShop 无用，SCG 的 intelligent allocation 远超所有 baseline
4. **TWExpress**: 所有方法 ~95-97%，rollout-safe 环境差异不大
5. **Plancraft**: 所有 rollout 方法 < base_only (29.8%)，rollout-harmful 确认

**⚠️ APPS s1 > SCG 的解释**: s1 在 step 0 强制触发 rollout，而 APPS 的 SCG gate 几乎不触发（ro/ep=0.18，信号太弱）。s1 的"盲目"策略在 APPS 碰巧比 SCG 的"过于保守"更好。但 s1 cost 更高 (2.0× vs 1.2×)，且在 WebShop 上崩溃 — 不是 generalizable 的优势。

**对新环境扩展的启示**:
- 新环境应能区分 intelligent gating (SCG) 和 naive allocation (s1)
- 理想新环境：s1 (blind step-0 rollout) 失效，SCG 的 direction discovery 有明确优势
- APPS Interview 可能展示与 APPS Intro 不同的信号强度（更难 → 更强信号？）

### 缺失的类型
- **数学推理**: 无（Game of 24 / GSM8K 因 single-turn 问题被搁置）
- **更难的代码生成**: APPS Intro 已有，但 Interview 级别可展示同环境不同难度下的信号变化
- **事实验证 / 知识推理**: 无（与 HotpotQA 互补但任务本质不同）
- **Data Science 代码**: 无（与算法题不同的代码生成子类型）

### 为什么还需要新环境

1. **Reviewer 预期**: NeurIPS 论文通常要求 4-6 个有效环境，当前 3 主 + 2 诊断勉强够，但如果再多 1-2 个主实验环境说服力更强
2. **Direction reversal story**: 更多环境 = 更强的 "信号语义因环境而异" 论证
3. **Code 领域深度**: APPS Intro + APPS Interview 可展示 "同一环境、不同难度、信号可能不同" — 这是 Two-Source Theory 的直接验证

---

## 1. APPS Interview（代码生成 — 更高难度）

### 1.1 概述

| 项目 | 说明 |
|------|------|
| **任务类型** | 代码生成（面试级别编程题） |
| **数据来源** | APPS dataset, `difficulty="interview"` 子集 (~5000 题) |
| **交互模式** | generate code → run tests → see failures → revise → ... |
| **成功指标** | 所有 test case 通过 (pass@1) |
| **预估 base SR** | 15-35%（Interview 比 Introductory 难，Intro 为 58.5%） |
| **实现成本** | **零** — `APPSEnv` 已支持，只需 `difficulty: "interview"` |

### 1.2 Rollout 策略

与 APPS Introductory 完全相同：**K-variant generation**。

```
Rollout type:     K-variant code generation
K (num_variants): 5
Temperature:      0.7 (采样多样性)
Evaluator:        Unit test (外部 oracle)
Utility:          max(variant_pass_rate) - base_pass_rate
```

**设计理由**:
- 代码生成任务的 rollout 不是 "向前搜索"（没有 sequential action），而是 "并行采样多个候选"
- 温度 0.7 产生多样性候选，unit test 客观评价 → utility 衡量 rollout 是否找到更好的代码
- 与 HotpotQA/WebShop 的 per-action exhaustive search 形成对比

### 1.3 信号设计

复用 APPS Introductory 的 5 个信号：

| 信号 | 计算方式 | APPS Intro 中的 ρ | Interview 预期 |
|------|---------|:--:|:--:|
| step_count | 当前步数 | −0.155 | 可能更强（多步修正空间更大） |
| token_entropy | LLM 输出的 token 分布熵 | +0.012 (无效) | 可能仍无效（代码语法约束） |
| test_pass_rate | 当前代码的 test 通过率 | −0.620 (最强) | 预期仍强 |
| state_category | first_attempt / partial_pass / all_fail | categorical | 预期有效 |
| action_type | submit / revise | categorical | 预期有效 |

**核心假设**: Interview 比 Intro 更难，base 模型 pass rate 更低 → rollout 提升空间更大 → 信号可能更强。如果 token_entropy 在 Interview 上仍然无效，进一步验证 "代码任务中 token entropy 缺乏信息量" 的理论。

### 1.4 配置

```yaml
# configs/phase6_apps_interview.yaml
apps_interview:
  environment:
    name: "apps_interview"
    type: "apps"
    max_steps: 5
    difficulty: "interview"           # ← 唯一变化
    max_problems: null
    num_candidates: 5
    timeout_per_test: 10

  proposer:
    mode: "llm_api"
    llm_config:
      api_type: "vllm"
      endpoint: "http://localhost:8900/v1"
      model_name: "Qwen/Qwen3-4B-Instruct-2507"
      temperature: 0.0
      max_tokens: 1024                # Interview 题目更复杂，保持 1024
      max_retries: 2
      top_logprobs: 5
      disable_thinking: true

  rollout:
    num_variants: 5
    temperature: 0.7

  gate:
    explore_rate: 0.5
    min_cal_points: 50
    window_size: 500
    utility_threshold: 0.05
    finetune_features:
      - step_count
      - token_entropy
      - state_category
      - action_type
      - test_pass_rate

  phase1_data_path: null
```

### 1.5 Step 0 结果 ✅ GO

```
base_sr  = 56%  (预期 15-35%，实际更高 — Qwen3-4B 在 Interview 上比预想的强)
always_sr = 82%  (Δ = +26pp，headroom 充足)
GO = true
```

比 APPS Intro (base=58.5%) 略低，说明 Interview 确实更难但幅度有限。Δ=+26pp 远超 APPS Intro 的 Δ=+6pp，rollout 提升空间大得多。

### 1.6 Step 1 — 🔄 运行中 (Job 23228761_0)

### 1.7 论文价值

- base SR (56%) vs APPS Intro (58.5%) 差距不大，但 **Δ 差异巨大** (26pp vs 6pp) — 说明 Interview 题的 rollout 价值远高于 Intro
- **与 APPS Intro 的 pair 对比**是独特的实验设计，其他论文没做过
- 如果信号方向与 Intro 一致 → "direction 是 environment property 而非 difficulty artifact"
- 如果信号方向不同 → "even within the same environment, difficulty shift changes signal semantics"

---

## 2. FEVER（事实验证）

### 2.1 概述

| 项目 | 说明 |
|------|------|
| **任务类型** | 事实验证（Fact Verification） |
| **数据来源** | FEVER dataset (Thorne et al., NAACL 2018), HuggingFace `fever/fever` |
| **规模** | ~145K train / ~20K dev (paper 验证集) |
| **交互模式** | search[entity] → lookup[term] → classify[Supported/Refuted/NEI] |
| **成功指标** | 正确分类 claim 为 SUPPORTS / REFUTES / NOT ENOUGH INFO |
| **预估 base SR** | 30-60%（三分类，需要 evidence retrieval） |
| **实现成本** | **中** — 复用 HotpotQA 的 search/lookup 框架，新增 classify action |

### 2.2 Rollout 策略

与 HotpotQA 相同模式：**per-action exhaustive evaluation**。

```
Rollout type:     Per-action exhaustive evaluation
K (num_chains):   5
Horizon:          3 steps
Top-k actions:    5
Temperature:      0.7 (rollout policy)
Evaluator:        LLM self-eval (与 HotpotQA 相同)
Utility:          R(with_rollout) - R(without_rollout)
```

**设计理由**:
- FEVER 的 agent loop 与 HotpotQA 结构一致：search evidence → reason → classify
- Per-action exhaustive evaluation 在每步枚举候选 action 并前瞻评估
- Self-eval evaluator（与 HotpotQA 相同） → 预期 entropy 方向也为负（高 entropy = 模型困惑 = rollout 有效）
- **但 FEVER 是分类而非生成答案**，信号方向可能有差异

### 2.3 环境设计

#### 动作空间

```
search[entity]       — 在 Wikipedia evidence 中搜索实体
lookup[term]         — 在最近检索的段落中查找关键词
classify[label]      — 提交分类: SUPPORTS / REFUTES / NOT ENOUGH INFO
```

#### Episode 流程

```
Step 0: Agent 看到 claim (e.g., "The Colosseum is in Rome.")
Step 1: Agent 搜索 evidence: search[Colosseum]
         → Obs: "The Colosseum is an amphitheatre in the centre of Rome, Italy."
Step 2: Agent 分类: classify[SUPPORTS]
         → Reward: 1.0 (correct) / 0.0 (incorrect)
```

#### 数据格式

```python
# FEVER dataset 结构
{
    "id": 12345,
    "claim": "The Colosseum is in Rome.",
    "label": "SUPPORTS",                    # ground truth
    "evidence": [                            # evidence sentences
        ["Colosseum", 0, "sentence text", 0]  # [title, sent_id, text, ...]
    ]
}
```

#### 与 HotpotQA 的关键差异

| 维度 | HotpotQA | FEVER |
|------|----------|-------|
| **任务** | 生成答案（开放式） | 三分类（SUPPORTS/REFUTES/NEI） |
| **答案空间** | 无限（自由文本） | 3 个离散标签 |
| **Evidence 需求** | 2+ 段落（多跳） | 通常 1 段落（单跳为主） |
| **评估** | F1 score | Exact match (label accuracy) |
| **预期 entropy 行为** | 负方向 (ρ=−0.041) | 可能不同（分类决策 vs 生成） |

### 2.4 信号设计

| 信号 | 计算方式 | 预期行为 |
|------|---------|---------|
| step_count | 当前步数 | 负方向（早期 search 最有价值） |
| token_entropy | LLM output token entropy | 可能负方向（同 HotpotQA），但分类任务 entropy 含义不同 |
| evidence_count | 已检索的 evidence 段落数 | 负方向（越多 evidence → 越接近 classify → rollout 价值降低） |
| is_classify_proposed | 当前候选中是否有 classify action | 负方向（准备 classify = 接近结束） |
| claim_type | 按 claim 特征分类 (entity/relation/numerical) | categorical |

### 2.5 实现计划

**需要新增的代码**:

1. `frvc/envs/fever_env.py` (~200 行)
   - 继承 `BaseEnv`
   - 复用 HotpotQA 的 search/lookup 模式
   - 新增 `classify[label]` action
   - 数据加载: HuggingFace `fever/fever` dataset
   - Evidence 存储: 与 HotpotQA 相同的 context 结构

2. `configs/phase6_fever.yaml`
   - 环境 + proposer + rollout + gate 配置

3. Registry 注册: `registry.py` 新增 `"fever"` 条目

**复用的代码**:
- `p5_new_env_experiments.py` (Step 0/1/2 pipeline 无需修改)
- `p5_competing_baselines.py` (Phase B baselines 无需修改)
- HotpotQA 的 `_do_search()`, `_do_lookup()` 逻辑

### 2.6 配置

```yaml
# configs/phase6_fever.yaml
fever:
  environment:
    name: "fever"
    type: "fever"
    max_steps: 8                      # FEVER 通常 2-4 步就够
    data_path: null                    # 使用 HuggingFace 加载
    split: "labelled_dev"             # paper 验证集
    max_problems: null

  proposer:
    mode: "llm_api"
    llm_config:
      api_type: "vllm"
      endpoint: "http://localhost:8900/v1"
      model_name: "Qwen/Qwen3-4B-Instruct-2507"
      temperature: 0.0
      max_tokens: 300
      max_retries: 2
      top_logprobs: 5
      disable_thinking: true

  rollout:
    temperature: 0.7
    num_chains: 5
    horizon: 3
    top_k_actions: 5
    disable_thinking: true

  gate:
    explore_rate: 0.5
    min_cal_points: 50
    window_size: 500
    utility_threshold: 0.05
    finetune_features:
      - step_count
      - token_entropy
      - evidence_count
      - is_classify_proposed
      - claim_type

  phase1_data_path: null
```

### 2.7 Step 0 结果 ✅ GO

```
base_sr  = 32%  (三分类 + evidence retrieval 需求，难度适中)
always_sr = 100% (rollout 极为有效，可能因 generic rollout 使用了 oracle)
GO = true (Δ = +68pp)
```

### 2.8 Step 1 结果 ✅ 完成 — 信号极强

| Rank | Signal | Spearman ρ | p-value |
|:---:|--------|:---:|:---:|
| 1 | **step_count** | **−0.619** | 2.9e-31 *** |
| 2 | **is_finish_proposed** | **−0.555** | 3.8e-24 *** |
| 3 | **evidence_count** | **−0.546** | 2.6e-23 *** |
| 4 | claim_length | −0.198 | 8.3e-4 ** |
| 5 | token_entropy | −0.119 | 0.045 * |
| (cat) | action_type | η²=0.314 | — |
| (cat) | state_category | η²=0.303 | — |

- **N=282 steps, 200 episodes**, utility positive_rate=51.8%
- **Token entropy 方向: 负** (与 HotpotQA 一致)
- **step_count ρ=−0.619** — 比 HotpotQA (ρ=−0.494) 更强
- 数据路径: `results/phase6/fever/fever/step1_signal_discovery.json`

### 2.9 论文价值（已确认）

- ✅ **方向与 HotpotQA 一致** (都是负方向) → "同一 agent 架构 (search→reason→classify) 下方向一致，验证 direction 是 task-structure property"
- 信号比 HotpotQA 更强，可能因为 FEVER 的 search→classify 路径更短 (avg 1.4 steps)，信号更 concentrated
- **与 HotpotQA 的对比**: 同为 search-based QA，FEVER 是分类 (3-class) 而 HotpotQA 是生成 (open-ended) — 任务不同但信号方向一致

---

## 3. DS-1000（Data Science 代码生成）

### 3.1 概述

| 项目 | 说明 |
|------|------|
| **任务类型** | Data Science 代码生成（Numpy, Pandas, Sklearn, Matplotlib, ...） |
| **数据来源** | DS-1000 (Lai et al., ICML 2023), HuggingFace `xlangai/DS-1000` |
| **规模** | 1,000 个 data science 问题 |
| **交互模式** | generate code → run tests → see failures → revise → ... |
| **成功指标** | Unit test 通过 (pass@1) |
| **预估 base SR** | 20-50%（取决于 Qwen3-4B 的 data science 能力） |
| **实现成本** | **中高** — 需处理库依赖，复用 APPS 的 generate→test→revise 框架 |

### 3.2 Rollout 策略

与 APPS 相同：**K-variant generation**。

```
Rollout type:     K-variant code generation
K (num_variants): 5
Temperature:      0.7
Evaluator:        Unit test (外部 oracle)
Utility:          max(variant_pass_rate) - base_pass_rate
```

**设计理由**:
- 代码生成任务统一使用 K-variant generation + unit test evaluation
- DS-1000 的 test 代码已内置，直接执行即可
- 与 APPS 的区别在于：DS-1000 需要 numpy/pandas/sklearn 等库，且问题是 "填空" 式（给定上下文，补全代码片段）

### 3.3 环境设计

#### 与 APPS 的关键差异

| 维度 | APPS | DS-1000 |
|------|------|---------|
| **问题格式** | 完整题目描述 + 从头生成 | 给定上下文代码 + 填空/补全 |
| **测试方式** | stdin/stdout IO 或 assert | 自定义 test function (比较输出 array/dataframe) |
| **依赖** | 标准库为主 | numpy, pandas, sklearn, matplotlib, scipy, tensorflow, pytorch |
| **代码长度** | 较长（完整程序） | 较短（通常 1-10 行） |
| **难度来源** | 算法设计 | API 知识 + 数据操作正确性 |

#### DS-1000 数据格式

```python
# DS-1000 每题结构
{
    "prompt": "import numpy as np\n...\n# <solution>\n",   # 待补全的代码上下文
    "reference_code": "result = np.argsort(arr)[::-1][:k]", # 参考答案
    "metadata": {
        "library": "Numpy",          # Numpy/Pandas/Sklearn/...
        "perturbation_type": "Origin" # Origin / Semantic / Difficult-Rewrite
    },
    "code_context": "...",            # test harness code
    "test": "def test(candidate):\n    ..."  # 验证函数
}
```

#### Episode 流程

```
Step 0: Agent 看到上下文 + prompt
Step 1: Agent 生成补全代码
         → 执行 test function → 观察结果
Step 2 (如果失败): Agent 看到错误信息 → 修正代码
         → 再次执行 → ...
```

### 3.4 信号设计

| 信号 | 计算方式 | 预期行为 |
|------|---------|---------|
| step_count | 当前步数 | 负方向（首次尝试最关键） |
| token_entropy | LLM 输出 token entropy | 可能无效（同 APPS：代码语法约束） |
| test_pass_rate | 当前代码 test 通过率 | 可能有效（DS-1000 通常只有 1 个 test） |
| library_type | 问题所属库 (numpy/pandas/...) | categorical（不同库的模型能力不同） |
| code_length | 生成代码行数 | 可能正方向（更长 = 更复杂 = rollout 可能找到更好方案） |

### 3.5 实现计划

**需要新增的代码**:

1. `frvc/envs/ds1000_env.py` (~250 行)
   - 继承 `BaseEnv`
   - 复用 APPS 的 generate→test→revise 流程
   - 数据加载: HuggingFace `xlangai/DS-1000`
   - 测试执行: 在 subprocess 中运行 DS-1000 的 test function
   - **需要处理**: numpy/pandas/sklearn 等库在 sandbox 中可用

2. `configs/phase6_ds1000.yaml`

3. Registry 注册

**依赖要求**:
```bash
# frvc conda 环境中需要额外安装
pip install numpy pandas scikit-learn matplotlib scipy
# 大部分应该已经安装
```

### 3.6 配置

```yaml
# configs/phase6_ds1000.yaml
ds1000:
  environment:
    name: "ds1000"
    type: "ds1000"
    max_steps: 5
    library: null                     # null = 所有库; 或 "Numpy" / "Pandas" / ...
    max_problems: null
    timeout_per_test: 15              # DS-1000 有些 test 需要更长时间

  proposer:
    mode: "llm_api"
    llm_config:
      api_type: "vllm"
      endpoint: "http://localhost:8900/v1"
      model_name: "Qwen/Qwen3-4B-Instruct-2507"
      temperature: 0.0
      max_tokens: 512
      max_retries: 2
      top_logprobs: 5
      disable_thinking: true

  rollout:
    num_variants: 5
    temperature: 0.7

  gate:
    explore_rate: 0.5
    min_cal_points: 50
    window_size: 500
    utility_threshold: 0.05
    finetune_features:
      - step_count
      - token_entropy
      - state_category
      - library_type
      - code_length

  phase1_data_path: null
```

### 3.7 Step 0 结果 ✅ GO

```
base_sr  = 20%  (Data science 对 Qwen3-4B 较难，符合预期)
always_sr = 100% (rollout 极为有效，可能因 generic rollout oracle)
GO = true (Δ = +80pp)
```

base SR=20% 在理想区间，headroom 巨大。

### 3.8 Step 1 — 🔄 运行中 (Job 23228761_2)

### 3.9 论文价值

- **与 APPS 的互补**: 算法题 vs data science 题 — 不同的代码生成子类型
- **库特异性信号**: 如果不同 library 的信号方向不同，可以在一个环境内展示 direction reversal
- base SR=20% 是目前所有代码环境中最低的，rollout 空间最大

---

## 4. CRUXEval（代码执行推理）

### 4.1 概述

| 项目 | 说明 |
|------|------|
| **任务类型** | 代码执行推理（预测输出 / 推断输入） |
| **数据来源** | CRUXEval (Gu et al., ICML 2024), HuggingFace `cruxeval/cruxeval` |
| **规模** | 800 个 Python 函数 × 2 子任务 = 1,600 题 |
| **子任务** | CRUXEval-I (input prediction), CRUXEval-O (output prediction) |
| **交互模式** | 需要包装 — 原始是 single-turn |
| **成功指标** | Exact match (预测值 == 真实值) |
| **预估 base SR** | 30-60%（取决于函数复杂度） |
| **实现成本** | **中** — 需要包装为多步交互 |

### 4.2 Rollout 策略

**K-variant generation**（与 APPS 类似，但产生的是 prediction 而非 code）。

```
Rollout type:     K-variant prediction
K (num_variants): 5
Temperature:      0.7
Evaluator:        Exact match (执行代码验证)
Utility:          max(variant correctness) - base correctness
```

**设计理由**:
- CRUXEval 原始是 single-turn，需要包装为多步
- 包装方式：predict → execute to verify → revise prediction → ...
- Evaluator 可以是 **真实执行**（在 subprocess 中运行代码得到 ground truth）
- 这使得 CRUXEval 拥有 **外部 oracle evaluator**（类似 APPS），但任务是 **推理而非生成**

### 4.3 环境设计 — 多步包装

#### 原始 CRUXEval (single-turn)

```
Input:  函数代码 + (input or output)
Output: 预测 (output or input)
```

#### 包装为多步交互

```
Step 0: Agent 看到函数代码 + 输入 (CRUXEval-O) 或 函数代码 + 输出 (CRUXEval-I)
Step 1: Agent 提交初始预测
         → 系统执行代码验证 → 反馈 "正确" 或 "错误: expected X, got Y"
Step 2 (如果错误): Agent 修正预测
         → 再次验证 → ...
Max steps: 3-5 (推理任务不需要太多轮)
```

#### 与 APPS 的关键差异

| 维度 | APPS | CRUXEval |
|------|------|----------|
| **任务** | 生成代码 | 预测执行结果 |
| **Agent 输出** | Python 代码 | 值（字符串/数字/列表/...） |
| **验证方式** | 运行代码 + 比较输出 | 运行给定代码 + 比较预测 |
| **多步自然度** | 高（test 反馈 → 修 bug） | 中（错误反馈 → 重新推理） |
| **代码角色** | Agent 生成 | 环境提供 |

### 4.4 信号设计

| 信号 | 计算方式 | 预期行为 |
|------|---------|---------|
| step_count | 当前步数 | 负方向 |
| token_entropy | LLM 预测时的 entropy | 可能有效（预测值的不确定性） |
| function_complexity | 函数的行数/嵌套深度 | 可能正方向（更复杂 = rollout 更有价值） |
| subtask_type | CRUXEval-I vs CRUXEval-O | categorical |
| has_loops | 函数是否包含循环 | categorical（循环 = 更难推理） |

### 4.5 配置

```yaml
# configs/phase6_cruxeval.yaml
cruxeval:
  environment:
    name: "cruxeval"
    type: "cruxeval"
    max_steps: 3                      # 推理任务，不需要太多步
    subtask: "output"                 # "output" (CRUXEval-O) 或 "input" (CRUXEval-I)
    max_problems: null

  proposer:
    mode: "llm_api"
    llm_config:
      api_type: "vllm"
      endpoint: "http://localhost:8900/v1"
      model_name: "Qwen/Qwen3-4B-Instruct-2507"
      temperature: 0.0
      max_tokens: 256                 # 预测值通常较短
      max_retries: 2
      top_logprobs: 5
      disable_thinking: true

  rollout:
    num_variants: 5
    temperature: 0.7

  gate:
    explore_rate: 0.5
    min_cal_points: 50
    window_size: 500
    utility_threshold: 0.05
    finetune_features:
      - step_count
      - token_entropy
      - function_complexity
      - subtask_type
      - has_loops

  phase1_data_path: null
```

### 4.6 Step 0 结果 ✅ GO

```
base_sr  = 76%  (偏高但在 [5%, 85%] 范围内)
always_sr = 100% (rollout 有效，可能因 generic rollout oracle)
GO = true (Δ = +24pp)
```

base SR=76% 偏高，rollout 空间有限 (24pp)。可能因为很多 CRUXEval 函数较简单，Qwen3-4B 直接能预测正确输出。

### 4.7 Step 1 — 🔄 运行中 (Job 23228761_3)

### 4.8 论文价值

- **独特定位**: 代码推理（理解 + 预测）vs 代码生成（创造） — 唯一的 "code understanding" 环境
- **Token entropy 可能有效**: 不同于代码生成（受语法约束），预测值的 entropy 可能真正反映不确定性
- **风险**: base=76% 偏高，headroom 有限；多步包装有些 artificial

---

## 5. 执行计划

### 5.1 实际执行记录 (2026-03-19)

```
Day 1 (03-19):
  09:00  4 个 env 实现完成 (fever_env.py 873行, ds1000_env.py 694行, cruxeval_env.py 879行)
         registry.py 更新, signal extraction 更新, configs 创建, SLURM 脚本创建

  09:30  Step 0 提交 (Job 23217235) — 失败: argparse choices 未包含新环境名
  10:00  修复 argparse, 重提交 (Job 23228574)
  10:30  FEVER Step 0 修复 data_path=None bug, 单独重跑 (Job 23228596)
         FEVER 端口冲突 (config=8900, vLLM=8910), 再次修复重跑 (Job 23228661)
  11:50  Step 0 全部完成: 4/4 GO ✅

  12:00  Step 1 提交 (Job 23228680) — 失败: 固定 port 8900 导致同 node 冲突
  12:10  修复: 每个 array task 独立端口 + sed 动态替换 config
         重提交 (Job 23228761)
  12:20  Step 1 正常运行, FEVER 最先完成 (15 min), 其余 ~30-60 min
```

### 5.2 SLURM Jobs

| Job | 步骤 | 状态 | 备注 |
|-----|------|:---:|------|
| 23228574 | Step 0 (array 0,2,3) | ✅ 完成 | APPS Interview, DS-1000, CRUXEval |
| 23228661 | Step 0 (FEVER 单独) | ✅ 完成 | 修复 data_path + port 后 |
| **23228761** | **Step 1 (array 0-3)** | **🔄 运行中** | **4 env 并行 signal discovery** |

### 5.3 下一步

Step 1 完成后:
- Step 2: Core 6-method experiments (6 methods × 3 seeds × 200 ep per env)
- Step 3: Competing baselines (8 CB × 3 seeds × 200 ep per env)
- 选择最终入选论文的环境（基于信号质量 + SCG 表现）

### 5.3 SLURM 资源需求

每个 Step 0 job:
- GPU: 1 × A100/H100 (vLLM serving)
- Memory: 48G
- Time: 4h
- 包含: vLLM 启动 + base_only 50ep + always_trigger 50ep

### 5.4 GO/NO-GO 决策矩阵

```
           base SR ∈ [5%, 85%]?
                  │
            ┌─────┴─────┐
            yes         no → NO-GO (停止)
            │
     Δ(always - base) > 3pp?
            │
      ┌─────┴─────┐
      yes         no → NO-GO (停止)
      │
   继续 Step 1 (Signal Discovery)
      │
   最强信号 |ρ| > 0.10?
      │
   ┌──┴──┐
   yes   no → 弱信号环境 (类似 APPS Intro)
   │         仍可用于 paper (诊断案例)
   │
   继续 Step 2 (Core 6-Method Experiments)
```

---

## 6. 跨环境对比框架

### 6.1 现有 + 新增环境的 Rollout 策略分类

| Rollout 策略类型 | 环境 | 特征 |
|-----------------|------|------|
| **Per-action exhaustive** | HotpotQA, FEVER, WebShop, TWExpress, Plancraft | 每步枚举 K 条 action chain, horizon H 步前瞻 |
| **K-variant generation** | APPS (Intro+Interview), DS-1000, CRUXEval | 一次性采样 K 个候选，外部 test 评价 |

### 6.2 Evaluator 类型分类

| Evaluator | 环境 | 预期 entropy 方向 |
|-----------|------|:---:|
| **Self-eval (LLM)** | HotpotQA, FEVER, WebShop, TWExpress | 负方向（高 entropy = 困惑 = 需要 rollout） |
| **External oracle (test)** | APPS (Intro+Interview), DS-1000, CRUXEval | 方向不确定（取决于信号信息量） |

### 6.3 论文叙事中的新环境角色

如果所有 4 个候选都 GO（最乐观情况）：

| 环境 | 论文角色 | Story 贡献 |
|------|---------|-----------|
| APPS Interview | **同环境不同难度** | Two-Source Theory 验证 |
| FEVER | **同框架不同任务** | search-based QA 内的方向对比 |
| DS-1000 | **不同代码子类型** | 算法 vs data science 信号差异 |
| CRUXEval | **推理 vs 生成** | Code understanding vs generation |

实际预期 GO 数: **1-2 个**（基于历史 NO-GO 率 ~60%）。

---

## 7. 引用信息

### FEVER

**Thorne, J., Vlachos, A., Christodoulopoulos, C., & Mittal, A. (2018).**
*FEVER: a Large-scale Dataset for Fact Extraction and VERification.*
**NAACL 2018**, pages 809-819.
arXiv: [1803.05355](https://arxiv.org/abs/1803.05355)
- 引用数: 2,000+
- ReAct 论文中包含 FEVER 评测

### DS-1000

**Lai, Y., Li, C., Wang, Y., Zhang, T., Zhong, R., Zettlemoyer, L., Yih, W., Fried, D., Wang, S., & Yu, T. (2023).**
*DS-1000: A Natural and Reliable Benchmark for Data Science Code Generation.*
**ICML 2023**.
arXiv: [2211.11501](https://arxiv.org/abs/2211.11501)
- 引用数: 300+
- 7 个 Python 库: Numpy, Pandas, Scipy, Sklearn, Matplotlib, TensorFlow, PyTorch

### CRUXEval

**Gu, A., Rozière, B., Leather, H., Solar-Lezama, A., Synnaeve, G., & Wise, S. (2024).**
*CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution.*
**ICML 2024**.
arXiv: [2401.03065](https://arxiv.org/abs/2401.03065)
- 引用数: 100+
- 800 Python 函数 × 2 子任务

### APPS (已有，补充 Interview 级别信息)

**Hendrycks, D. et al. (2021).** *Measuring Coding Challenge Competence With APPS.*
- Interview 子集: ~5,000 题 (来自 Codewars, Kattis 等的面试级别题目)
- 难度: Introductory < **Interview** < Competition

---

## 8. 总结

### 实验进度

| 候选 | Step 0 | Step 1 | Step 2 | 状态 |
|------|:---:|:---:|:---:|:---:|
| **APPS Interview** | ✅ GO (56%→82%, Δ=+26pp) | 🔄 运行中 | — | Signal discovery |
| **FEVER** | ✅ GO (32%→100%, Δ=+68pp) | ✅ 完成 (ρ=−0.619) | — | 信号强，ready for Step 2 |
| **DS-1000** | ✅ GO (20%→100%, Δ=+80pp) | 🔄 运行中 | — | Signal discovery |
| **CRUXEval** | ✅ GO (76%→100%, Δ=+24pp) | 🔄 运行中 | — | Signal discovery |

### 论文价值评估

| 候选 | Step 0 结果 | 信号强度 | 论文角色 |
|------|:---:|:---:|------|
| **APPS Interview** | base=56%, Δ=+26pp | 待确认 | 同环境不同难度，Two-Source Theory 验证 |
| **FEVER** | base=32%, Δ=+68pp | **极强** (ρ=−0.619) | 新任务类型，方向与 HotpotQA 一致 |
| **DS-1000** | base=20%, Δ=+80pp | 待确认 | 新代码子类型 (data science) |
| **CRUXEval** | base=76%, Δ=+24pp | 待确认 | Code reasoning vs generation |

**实际成果**: 4/4 全部 GO（远超预期的 1-2 个），论文可从 "3主+2诊断+1限制" 提升到最多 "7主+2诊断+1限制"。但需根据 Step 1 信号质量和 Step 2 SCG 表现筛选最终入选环境。

---

## 9. Competing Baselines 状态（2026-03-19 更新）

### 已实现的 Competing Baselines（共 8 个）

| Baseline | 信号 | 方向 | 额外 Cost | Phase | 状态 |
|----------|------|------|----------|-------|:----:|
| CATTS | Vote disagreement | 固定正向 | K=5 calls/step | P5 | ✅ 全5环境 |
| SEAG | Mean logprob | 固定负向 | 0 | P5 | ✅ 全5环境 |
| CoRefine | Token entropy | 固定正向 | 0 | P5 | ✅ 全5环境 |
| CaTS | Platt-scaled conf | 学习(1d) | 0 | P5 | ✅ 全5环境 |
| **AUQ** 🆕 | Verbalized conf | 固定负向 | 1 call/step | P6.1b | ✅ 27/30 (rerun 2) |
| **s1 Budget** 🆕 | 无 | 无 | 0 | P6.1b | ✅ 27/30 (rerun 2) |
| base_only | — | — | 0 | Core | ✅ |
| always_trigger | — | — | 每步 rollout | Core | ✅ |

### 新环境需同步跑的 Baselines

任何新 GO 的环境需要跑：
- **Core 6**: base_only, always_trigger, random_50, best_sigma_wrong, scg_finetune_lr, oracle
- **CB 8**: CATTS, SEAG, CoRefine, CaTS, AUQ, s1 Budget
- **Our methods**: principled_v2, SE variants
- 总计: ~18 methods × 3 seeds × 200 ep per env
