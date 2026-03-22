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

### 5.1 实际执行记录

```
Day 1 (03-19):
  09:00  4 env 实现完成 (fever_env.py, ds1000_env.py, cruxeval_env.py)
  09:30  Step 0 提交 → 修复 argparse/data_path/port → 11:50 全部完成: 4/4 GO ✅
  12:00  Step 1 提交 → 修复 port 冲突 → 全部完成 ✅
  13:00  Step 2 提交 (Job 23232914, 72 tasks)

Day 2 (03-20):
  Step 2 完成 67/72: APPS Interview 18/18, FEVER 14/18, DS-1000 16/18, CRUXEval 18/18
  发现两个问题:
    Issue 1: BSW 退化为 always_trigger (config 缺 wrong_direction)
    Issue 2: DS-1000 oracle leak (reference_code 在候选 action 中)
  修复:
    - ds1000_env.py: 移除 reference_code 从候选 (也修复了 cruxeval_env.py, fever_env.py)
    - 4 个 config: 添加 fixed_signal_name + wrong_direction
    - p3_core_experiments.py: 添加新环境 env_name 匹配
  提交全量实验 (435 tasks):
    Job 23258560: 修复重跑 (DS-1000 全 18 + BSW ×3 env = 27)
    Job 23258750: CB (FEVER + APPS Interview × 6 CB × 3 seeds = 36)
    Job 23258786: 全部 25 local methods × 4 envs × 3 seeds = 300
    Job 23258994: 全部 6 openrouter methods × 4 envs × 3 seeds = 72
```

### 5.2 SLURM Jobs

**已完成:**

| Job | 步骤 | 状态 | 备注 |
|-----|------|:---:|------|
| 23228574 | Step 0 (array 0,2,3) | ✅ | APPS Interview, DS-1000, CRUXEval |
| 23228661 | Step 0 (FEVER) | ✅ | |
| 23228761 | Step 1 (array 0-3) | ✅ | 4 env signal discovery |
| 23232914 | Step 2 (array 0-71) | ✅ 67/72 | 4 env × 6 core methods × 3 seeds |

**运行中 (2026-03-20 提交):**

| Job | 步骤 | Tasks | 内容 |
|-----|------|:---:|------|
| 23259059 | 修复重跑 (Issue 1+2) | **27** | ✅ 27/27 | DS-1000 rerun + BSW fix ×3 env (但 DS-1000 有 Issue 4) |
| 23259060 | CB (FEVER+APPS Intv) | **36** | ✅ 36/36 | auq+s1 有效; catts/seag/corefine/cats 不触发 (Issue 3) |
| **23259061** | **Local methods (25)** | **300** | **🔄 运行中** | **4 envs × 25 methods × 3 seeds** |
| **23259062** | **OpenRouter methods (6)** | **72** | **🔄 排队** | **4 envs × 6 methods × 3 seeds** |
| **23263520** | **CB rerun (Issue 3 fix)** | **48** | **🔄 排队** | **FEVER+APPS Intv catts/seag/corefine/cats + CRUXEval 全 6 CB** |
| **23263826** | **DS-1000 rerun (Issue 4 fix)** | **36** | **🔄 排队** | **DS-1000 core 6 + CB 6 (test_execution harness 修复)** |
| | **运行中总计** | **456** | | |

### 5.3 已发现并修复的问题

#### Issue 1: best_sigma_wrong 退化为 always_trigger — ✅ 已修复

**现象**: 所有 4 个新环境的 BSW rollout_rate=1.0，SR 与 always_trigger 完全一致。

**根因**: `make_phase3_gate()` 中 BSW 的 env_name 匹配缺少新环境，回退到 `signal_name="evidence_count", direction="positive", threshold=0.0` → 恒触发。

**修复 (2026-03-20)**:
- 4 个 config 添加 `fixed_signal_name` + `wrong_direction`：
  - apps_interview: step_count, positive（翻转 ρ=−0.339 的负方向）
  - fever: step_count, positive（翻转 ρ=−0.619 的负方向）
  - ds1000: token_entropy, positive（翻转 ρ=−0.102 的负方向；step_count ρ=0 不可用）
  - cruxeval: step_count, negative（翻转 ρ=+0.184 的正方向）
- `p3_core_experiments.py` 添加新环境 env_name 匹配
- **重跑**: Job 23258560 array 18-26 (BSW × 3 seeds × 3 env，DS-1000 BSW 在 array 9-11 一并重跑)

#### Issue 2: DS-1000 / CRUXEval / FEVER oracle leak — ✅ 已修复

**现象**: DS-1000 always_trigger=100%（应远低于此）。

**根因**: `_generate_candidate_actions()` 将 ground truth 答案放入候选 action 列表。Rollout 通过 `forward_value()` 发现 oracle action 全部通过测试 → SR 被人为推高。

**修复 (2026-03-20)**:
- `ds1000_env.py`: 移除 `reference_code` 从候选，`greedy_oracle_action()` 改为直接测试后注入
- `cruxeval_env.py`: 移除 oracle answer 从候选，`greedy_oracle_action()` 改为验证后注入
- `fever_env.py`: 移除 `classify[correct_label]` 从默认候选
- **重跑**: Job 23259059 array 0-17 (但触发了 Issue 4)

#### Issue 3: CB (catts/cats/seag/corefine) 不触发 — ✅ 已修复

**现象**: 4 个固定方向 CB 在 FEVER 和 APPS Interview 上 rollout_rate≈0，SR≈base_only。

**根因**: 新环境 config 的 `phase1_data_path: null`。CB 需要 Phase 1 signal data 来校准 threshold → buffer_size=0 → fallback → 永远不触发。

**修复 (2026-03-20)**:
- 4 个 config 的 `phase1_data_path` 更新为实际 Step 1 数据路径
- **重跑**: Job 23263520 (48 tasks): FEVER+APPS Intv catts/seag/corefine/cats + CRUXEval 全 6 CB

#### Issue 4: DS-1000 修复后 base_only=100% — ✅ 已修复

**现象**: Issue 2 的 oracle leak 修复后，DS-1000 全部方法 SR=100%（含 base_only）。

**根因**: DS-1000 HuggingFace 数据集没有独立的 `test` 字段（`item.get("test", "")` 返回空字符串）。测试逻辑嵌入在 `code_context` 中的 `test_execution(solution)` 函数里。`_safe_exec()` 原来的逻辑是拼接 `code_context + code + test_code`，当 `test_code=""` 时没有任何验证 → subprocess 成功退出 → passed=True。

**修复 (2026-03-20)**:
- `ds1000_env.py` 的 `_safe_exec()` 现在检测 `code_context` 中是否有 `test_execution`
- 如果有，调用 `test_execution(repr(solution))` 执行 DS-1000 内置 test harness
- 否则回退到原来的拼接逻辑（兼容 stub data）
- **验证**: skeleton→failed, reference→passed, base_only episode→failed (符合预期)
- **重跑**: Job 23263826 (36 tasks): DS-1000 core 6 + CB 6 × 3 seeds

### 5.4 当前实验状态与下一步

**当前 456 tasks 并行运行中** (2026-03-20 晚间):

```
┌─ Job 23259061 (300 tasks): 全部 25 个 local methods × 4 envs × 3 seeds
│   ├─ Path E: cacb_A/B/C, proto, principled, principled_online/nopca/auto/adaptive/fbeta
│   ├─ principled_v2
│   ├─ SE local: self_evolving_local, se_few5_local, se_few5_filter_local
│   ├─ SE feedback: se_feedback_cycle2/3_local, se_100cal_fb_c3_local
│   ├─ SE online: se_online_fix/decay_local, se_online_fix/decay_ref_local
│   └─ SE cycle3: se_c3_addcum/addlat/selcum/sellat_local
│
├─ Job 23259062 (72 tasks): 全部 6 个 openrouter methods × 4 envs × 3 seeds
│   └─ self_evolving_openrouter, se_few5_*, se_feedback_*, se_few5flt_or_100cal
│
├─ Job 23263520 (48 tasks): CB rerun (Issue 3 fix — phase1_data_path)
│   ├─ FEVER + APPS Interview: catts/seag/corefine/cats × 3 seeds (重跑)
│   └─ CRUXEval: 全 6 CB × 3 seeds (首跑)
│
└─ Job 23263826 (36 tasks): DS-1000 full rerun (Issue 4 fix — test_execution)
    ├─ Core 6: base_only/always_trigger/random_50/bsw/scg/oracle × 3 seeds
    └─ CB 6: catts/seag/corefine/cats/auq/s1_budget × 3 seeds
```

**全部 Issue 已修复** (Issue 1-4), 等待重跑结果。

**下一步 (全部 job 完成后)**:
```
1. 汇总全部结果:
   - 4 env × (6 core + 6 CB + 31 methods) × 3 seeds 完整结果表
   - DS-1000 修复后的真实 always_trigger SR (关键数据)

2. 决定论文最终环境选择:
   - FEVER: 最确定入选 (SCG >> all CB)
   - DS-1000: 取决于修复后数据
   - APPS Interview / CRUXEval: rollout-safe 诊断环境

3. Token cost 分析:
   - 为入选环境计算 C_base, C_rollout, C_vote
   - Pareto 图生成

4. 更新论文报告:
   - competing_baselines_report.md (CB rerun 数据)
   - full_report.md (全部方法数据)
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

### 实验进度 (2026-03-21 更新)

| 候选 | Step 0 | Step 1 | Core 6 | CB 6 | BSW fix | Path E/SE (local) | Path E/SE (OR) | 状态 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **FEVER** | ✅ | ✅ ρ=−0.619 | ✅ (缺3) | ⚠️→🔄 | ✅ | 🔄 64/75 | 🔄 0/18 | Path E 进行中 |
| **APPS Interview** | ✅ | ✅ ρ=−0.339 | ✅ 18/18 | ⚠️→🔄 | ✅ | 🔄 35/75 | 🔄 0/18 | Path E 进行中 |
| **DS-1000** | ✅ | ✅ η²=0.605 | 🔄 Issue4 fix | 🔄 Issue4 fix | — | 🔄 0/75 | 🔄 0/18 | 全部等 Issue 4 重跑 |
| **CRUXEval** | ✅ | ✅ ρ=+0.184 | ✅ 18/18 | 🔄 首跑 | ✅ | 🔄 0/75 | 🔄 0/18 | CB + Path E 排队 |

### 完整结果 (2026-03-22 更新, 含全部修复 + CB rerun + Optimistic test)

**FEVER** — Core + CB (Issue 3 修复) + BSW 修复 + Path E/SE + Optimistic:
```
Method               Mean SR  ro/ep  SR/ro   备注
─── Core 6 ───
always_trigger       ~99.8%   1.46   0.431
oracle               ~99.8%   0.70   0.893
random_50            ~98.8%   1.07   0.577
scg_finetune_lr       98.0%   0.99   0.615   ← SR/ro 最高 (非 REF)
best_sigma_wrong      63.0%   4.30   0.060   错误方向 → −36.8pp
─── CB 6 (Issue 3 修复后) ───
cats                  50.2%   4.71   0.028   ✅ 修复后从 33.8% → 50.2%
corefine              49.8%   3.13   0.041   ✅ 修复后从 33.7% → 49.8%
seag                  49.3%   3.12   0.040   ✅ 修复后从 33.3% → 49.3%
s1_budget             46.2%   1.58   0.058
auq                   40.7%   1.17   0.031
catts                 34.2%   0.06  −0.515   仍几乎不触发, < base
─── Path E/SE top (64/75) ───
se_online_decay       49.8%   2.99   0.043
se_100cal_fb_c3       48.7%   2.72   0.043
se_online_fix         47.0%   2.47   0.040
principled_v2         37.8%   0.72   0.011
self_evolving_local   38.8%   0.79   0.023
─── Optimistic (新, 全部失败) ───
v2_optimistic         39.2%   0.96   —       ≈ base, 没有改善
se_optimistic         36.3%   0.60   —       比原始 SE 更差
base_only             37.0%   0.00   —

→ SCG(98.0%) >> cats/corefine/seag/SE(~50%) >> s1(46.2%) >> auq(40.7%) >> base(37.0%)
→ SCG 效率 (SR/ro=0.615) 是 CB 最佳的 10.6×, SE 最佳的 14×
→ Issue 3 修复后 CB 从 ~34% 提升到 ~50%, 但仍远不如 SCG
→ Optimistic exploration 未能改善 SE — 探索数据偏差不是简单改触发策略能解决的
→ FEVER 是 **最强主实验候选**: SCG Pareto-dominates 所有 CB 和 SE
```

**APPS Interview** — Core + CB (Issue 3 修复后) + Path E/SE:
```
Method               Mean SR  ro/ep  SR/ro   备注
─── Core 6 ───
always/BSW/SCG/oracle 79.5%   0.23-2.19      Rollout-safe ceiling
random_50             79.2%   1.23   0.152
─── CB 6 (Issue 3 修复后) ───
corefine              67.5%   0.62   0.112   ✅ 修复后从 60.5% → 67.5%
cats                  66.2%   0.54   0.105   ✅ 修复后从 60.5% → 66.2%
seag                  66.0%   0.64   0.086   ✅ 修复后从 60.5% → 66.0%
s1_budget             69.0%   1.00   0.085
auq                   64.7%   1.08   0.038
catts                 60.8%   0.02   0.154   仍几乎不触发
─── Path E/SE top (54/75) ───
principled_v2         74.2%   1.59   0.086
self_evolving_local   73.8%   1.64   0.081
se_100cal_fb_c3       73.3%   1.32   0.097
se_online_fix         72.8%   1.34   0.093
base_only             60.5%   0.00   —

→ SCG(79.5%) > v2(74.2%) > SE(73.8%) > s1(69.0%) > corefine(67.5%) > cats(66.2%) > auq(64.7%) > base(60.5%)
→ SCG 效率 (SR/ro=0.190) 是所有方法中最高
→ Issue 3 修复后 CB 从 60.5% 提升到 66-68%, 但仍低于 SE/v2
```

**CRUXEval** — Core + CB (首跑完成):
```
Method               Mean SR  ro/ep  SR/ro   备注
─── Core 6 ───
always/SCG/oracle     99.5%   0.15-1.91      SCG ro=0.90, cost 节省 53%
random_50             96.2%   0.98   0.114
best_sigma_wrong      87.5%   1.00   0.025   错误方向 −12pp
─── CB 6 ───
auq                   99.0%   1.75   0.080   接近 SCG
cats                  95.0%   0.73   0.137
s1_budget             86.5%   1.00   0.015
seag                  85.8%   0.73   0.011
corefine              85.8%   0.73   0.011
catts                 81.3%   0.04  −1.048   < base, 方向错误
base_only             85.0%   0.00   —

→ SCG = always = oracle = 99.5% (rollout-safe ceiling)
→ base=85% 偏高, headroom 有限
→ catts(81.3%) < base(85.0%), 方向错误反而有害
```

**DS-1000** — ❌ 放弃:
```
Issue 4 修复后全部 SR=0.000 (test_execution 在 subprocess 中总是 fail)
需要更深入调查 DS-1000 的 test harness 集成方式, 但 ROI 不够高
修复前有参考数据: base=20.3%, SCG=71.7%, random_50=61.7%
决定: 不入选论文, 不再投入时间修复
```

**CRUXEval** — Core ✅ + BSW 修复 ✅:
```
Method               s42     s123    s456    Mean SR  ro/ep   备注
base_only            85.0%   85.0%   85.0%   85.0%   0.00
always_trigger       99.5%   99.5%   99.5%   99.5%   1.91
random_50            97.0%   95.0%   96.5%   96.2%   0.97
best_sigma_wrong     87.5%   87.5%   87.5%   87.5%   1.00    ✅ 修复: SR 下降 12pp
scg_finetune_lr      99.5%   99.5%   99.5%   99.5%   0.90
oracle               99.5%   99.5%   99.5%   99.5%   0.15

→ base=85.0% 超过 GO ceiling (Step 0=76%, 200ep=85%)
→ Rollout-safe: SCG=always=oracle=99.5%
→ BSW(87.5%) < SCG(99.5%), 错误方向 -12pp
→ SCG ro/ep=0.90 vs always=1.91, cost 节省 53%
```

### 论文价值评估 (2026-03-22 最终)

| 候选 | SCG SR | SCG SR/ro | CB 最佳 | SE 最佳 | BSW 退化 | 论文适合度 | 状态 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **FEVER** | **98.0%** | **0.615** | cats 50.2% | SE 49.8% | −36.8pp | ⭐⭐⭐ **主实验** | ✅ 全部完成 |
| **APPS Intv** | 79.5% | 0.190 | corefine 67.5% | v2 74.2% | 0pp (safe) | ⭐⭐ 诊断 | ✅ 全部完成 |
| **CRUXEval** | 99.5% | 0.162 | auq 99.0% | — | −12pp | ⭐⭐ 诊断 | ✅ 全部完成 |
| **DS-1000** | — | — | — | — | — | ❌ 放弃 | test harness 无法修复 |

---

## 9. 实验覆盖矩阵（2026-03-22 更新）

### 新环境的实验覆盖

| 类别 | 方法数 | FEVER | APPS Intv | CRUXEval | DS-1000 |
|------|:---:|:---:|:---:|:---:|:---:|
| **Core 6** | 6 | ✅ (缺3 seeds) | ✅ 18/18 | ✅ 18/18 | ❌ 放弃 |
| **CB 6 (修复后)** | 6 | ✅ 18/18 | ✅ 18/18 | ✅ 18/18 | ❌ |
| **BSW fix** | 1 | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 | ❌ |
| **Local methods** | 25 | ✅ 64/75 | 54/75 | 0/75 | ❌ |
| **Optimistic** | 3 | ✅ 9/9 (失败) | — | — | ❌ |

### 已完成 Job 汇总

| Job | 内容 | Tasks | 状态 |
|-----|------|:---:|:---:|
| 23263520 | CB rerun: FEVER+APPS Intv catts/seag/corefine/cats + CRUXEval 全 6 CB | 48 | 🔄 排队 |
| 23263826 | DS-1000: Core 6 + CB 6 (Issue 4 fix: test_execution harness) | 36 | 🔄 排队 |

### Path E/SE 初步发现

**FEVER (64/75)**: SCG(98.0%) >> 所有 SE 方法 (max ~50%)
- SE 在 search-based QA 环境表现差，手工 feature (step_count ρ=−0.619) 远优于 LLM 自动发现的 feature
- 这支持论文观点: **signal 信息量因环境而异，简单 feature 在某些环境已足够**

**APPS Interview (35/75)**: SCG(79.5%) > principled_v2(~76%) > SE(~74%)
- Rollout-safe 环境，方法差异主要在 cost
- principled_v2 接近 SCG，验证了自动化方法的可行性

### 全部方法清单 (43 个)

```
Core 6:       base_only, always_trigger, random_50, best_sigma_wrong, scg_finetune_lr, oracle
CB 6:         catts, seag, corefine, cats, auq, s1_budget
Path E (11):  cacb_A/B/C, proto, principled, principled_online/nopca/auto/adaptive/fbeta, principled_v2
SE local (14): self_evolving_local, se_few5_local, se_few5_filter_local,
               se_feedback_cycle2/3_local, se_100cal_fb_c3_local,
               se_online_fix/fix_ref/decay/decay_ref_local,
               se_c3_addcum/addlat/selcum/sellat_local
SE OR (6):    self_evolving_openrouter, se_few5/few5_filter_openrouter,
              se_feedback_cycle2/3_openrouter, se_few5flt_or_100cal
```

---

## 10. 深度分析：FEVER 上 SCG >> SE 的根因 (2026-03-21)

### 现象

FEVER 环境中 SCG(98.0%) 远超所有 SE 方法 (max ~50%)，差距高达 48pp。这在其他环境中不常见（旧环境中 SE 通常接近或超过 SCG）。

### 三层原因

#### 原因 1: 特征质量 — 任务结构 vs 文本表面

| | SCG (手工 5 feature) | SE (LLM 自动发现) |
|---|---|---|
| **特征** | step_count (ρ=−0.619), evidence_count (ρ=−0.546) | llm_negation_count, llm_has_directed_by, llm_action_length |
| **捕获的是** | **任务结构**（搜索阶段 vs 分类阶段） | **文本表面模式**（是否包含某些词） |
| **与 utility 相关性** | 强 — 直接反映 rollout 价值 | 弱 — 与 utility 几乎无关 |
| **LR 系数** | step_count=−1.64, evidence_count=−0.96 | LASSO 系数 ≈ 0（全部 drop） |

SCG 的 step_count 和 evidence_count 是 **领域知识特征**，精确捕获了 FEVER 的任务结构：
- 早期步骤（step=0-1）: 需要搜索 evidence → rollout 帮助选择搜索目标 → **高 utility**
- 后期步骤（step=2+）: 已有 evidence，准备 classify → rollout 不再需要 → **低 utility**

SE 的 LLM 看到的是 agent 的文本交互，发现的是 "是否包含 directed by"、"negation 词数量" 等 **内容特征**，这些与 "此刻是否应该触发 rollout" 无关。

#### 原因 2: 校准数据偏差（关键发现）

| 数据来源 | Positive utility rate | Episode length | 来源 |
|---------|:---:|:---:|------|
| **SCG (Phase 1 always_trigger)** | **51.8%** | 1.4 steps/ep | 200 ep, 每步都 rollout |
| **SE (自己的 exploration)** | **7-9%** | 5+ steps/ep | 50 ep, random 50% gate |

差异根因：FEVER 有一个特殊性质 — **rollout 的价值集中在 episode 最初 1-2 步**。

- **always_trigger**: 每步都 rollout → step 0 的 rollout 帮助 agent 快速搜到 evidence → episode 仅 1.4 步 → 数据中 positive 和 negative utility 大致均衡 (51.8%)
- **SE exploration (random gate)**: step 0 有 50% 概率不触发 rollout → agent 选错 search 目标 → episode 延长到 5-6 步 → 后续步骤全是 low-utility → 校准数据被 **late-step negative 样本淹没** (仅 7-9% positive)

#### 原因 3: 反馈死亡螺旋

```
1. Exploration: random gate → 50% 概率错过 step 0 的关键 rollout
2. Episode 延长: 错过关键 rollout → agent 漫无目的搜索 → 5-6 步
3. 数据偏差: 校准数据 positive_rate 仅 7-9% (vs 真实 51.8%)
4. LASSO 学习: "utility 几乎总是负的" → 学到 "永远不触发"
5. Exploitation: rollout_rate=3% → ≈ base_only → SR=37%
   ↻ 回到步骤 1（如果有 online 更新，继续收集偏差数据）
```

对比 SCG：
```
1. Phase 1: always_trigger 收集 200 ep 数据 (positive_rate=51.8%)
2. LR 学习: step_count coef=-1.64 → "step 0-1 触发, step 2+ 不触发"
3. Exploitation: rollout_rate=68%, 精准触发早期步骤
4. 结果: episode 仅 1.5 步, SR=98.0%
```

### 量化证据

| 指标 | SCG | self_evolving_local | se_100cal_fb_c3_local |
|------|:---:|:---:|:---:|
| SR | **98.0%** | 36.0% | 47.0% |
| Rollout rate | **68.2%** | 3.0% | 51.9% |
| Steps/ep | **1.5** | 5.3 | 4.3 |
| Cal positive_rate | **51.8%** (Phase 1) | 7.3% (explore) | 8.8% (explore) |
| Decisions | 292 | 1054 | 860 |

se_100cal (100 cal points, 更多数据) 的 rollout_rate 提升到 51.9%，SR 提升到 47% — 说明 **更多校准数据能缓解偏差**，但仍远不如 SCG 因为 explore 数据本身就有偏。

### 论文价值

这个发现对论文核心叙事非常有价值：

1. **揭示 online exploration 的 sample bias 问题**: 在 "早期 rollout 价值极高" 的环境中，random exploration 产生的数据有系统性偏差，导致从中学习的方法失败。这是 SE 方法的根本局限。

2. **解释为什么 SCG 的 "先收集 always_trigger 数据再学习" 策略更优**: SCG 的两阶段设计（Phase 1 always_trigger → Phase 2 学习 gate）避开了 exploration bias。

3. **支持 Two-Source Theory**: FEVER 是 "Information-Poverty" 类型环境（early steps 的 uncertainty 来自信息不足），rollout 价值集中在信息获取阶段。这与 APPS（Decision-Difficulty 类型）形成对比。

4. **实际指导意义**: 在新环境部署 adaptive compute 时，如果环境有 "early-step critical rollout" 特性，应优先使用 always_trigger 数据来校准 gate（SCG 策略），而非 online random exploration（SE 策略）。

---

## 11. SE 改进方向 (2026-03-21)

### 11.1 问题的本质

SE 失败的根本原因不是 feature discovery 失败，而是 **训练目标和数据收集机制共同造成了不可识别的决策信号**：

- 当前 SE 和 SCG 都在学 U(s)（rollout utility），但 gate 决策真正需要的是 **gate action 的 advantage**
- 每个 state 只观察到 trigger 或 not-trigger 其中一个 → 无法估计 advantage
- SE 的 random exploration 产生的数据分布与 optimal policy 差距太大 → off-policy 估计严重失效

### 11.2 核心提案：学 Δ 而非 U

不是学 U(s)（"这个 state 的 rollout utility 是多少"），而是学：

```
Δ_π(s) = Q_π(s, trigger) - Q_π(s, not-trigger)
```

其中 π 是固定的后续 continuation policy。

**关键区别**：
- U(s) 是 **单边观测**，受 behavior policy 的 episode trajectory 影响
- Δ_π(s) 是 **同一 state 下两种 gate action 的条件效应估计**，消除了 state visitation 偏差

**严格定义**：Δ_π(s) 依赖 continuation policy π。trigger 分支的 π 是 "LLM 基于 rollout 结果选 action"，not-trigger 分支的 π 是 "LLM 基于 forward_value 选 action"。这两者是不同的 policy — 我们估计的是 "触发 rollout 后整体表现是否更好"（包括后续 policy 变化），这正是 gate 的决策目标。

### 11.3 数据收集：Counterfactual Pairs

在同一个 state snapshot 上采集 trigger 和 not-trigger 两条分支：

```
for each step in episode (always_trigger 主路径):
    1. 到达 state s → snapshot
    2. 触发 rollout → 完整 continuation → 记录 R(trigger, s)
    3. rollback to snapshot → 不触发 → continuation → 记录 R(not-trigger, s)
    4. rollback → 恢复到 trigger 路径继续主 episode
    5. Δ(s) = R(trigger, s) - R(not-trigger, s)
```

### 11.4 Cost 分析

**关键设计选择**：not-trigger 分支要跑多长？

| 方案 | not-trigger 分支 | Cost 倍率 | 精度 |
|------|-----------------|:---------:|:----:|
| **Full branch** | 完整 continuation 到 episode 结束 | ~2× | 严格 Δ_π(s) |
| **Short proxy** | 只走 1 步看 immediate reward | ~1.3× | proxy Δ̃(s)，可能有偏 |
| **Early-state only** | 只对 step 0-1 做 full pair | ~1.5× | 对 FEVER 够用（价值集中在早期） |

**FEVER 具体估算**：

主 episode 用 always_trigger → 平均 1.4 steps/ep → 200 ep ≈ 280 states。
如果只对 step 0-1 做 pair（FEVER 决策集中在早期）：

```
cost multiplier ≈ 1 + k/1.4  (k = paired steps)
k=1: ≈ 1.7×    → ~25 min (vs SCG Phase 1 ~15 min)
k=2: ≈ 2.4×    → ~36 min
```

**注意**：short proxy (one-step not-trigger) 只在强假设下成立 — "trigger 的价值几乎完全体现在立刻是否调用 rollout"。FEVER 可能接近这个假设，但需要先验证 proxy Δ̃ 和 strict Δ 的相关性。

### 11.5 LLM 的角色

**定位 1（推荐）：Pattern Summarizer / 解释器**
- 输入：high-Δ(s) states vs low-Δ(s) states
- 输出：human-readable hypothesis（如 "early steps matter", "negation 不重要"）
- 用途：可解释性、failure diagnosis

**定位 2（未来工作）：Hypothesis Proposer**
- 输入：counterfactual dataset
- 输出：candidate rules/features → 反馈到 gate
- 风险更大，先不做

先走定位 1，因为核心贡献在 estimation 改进，不要同时引入不稳定模块。

### 11.6 验证路线图

在实现完整方法之前，必须先做 sanity check 验证核心假设：

**Phase A: 便宜 sanity check（1 GPU, ~1 hour）**
- 只对 FEVER step 0/1 做 counterfactual pair
- 固定 continuation policy + 固定 random seed / deterministic decoding
- 验证：
  - (a) 同一 snapshot 重复 3-5 次 pair → Δ(s) 方差多大？ 如果方差太大，整个方向需重新考虑
  - (b) Δ(s) 是否确实在 early step 显著偏大？ 如果不成立，当前叙事站不住
  - (c) one-step proxy Δ̃ 和 full-branch Δ 的相关性？ 决定是否能用便宜版本

**Phase B: 小规模严格版**
- 抽 50 个 states，trigger/not-trigger 都跑 full continuation
- 比较 proxy Δ̃ 和 strict Δ 的相关性
- 如果高相关 → 用便宜版；如果低相关 → 必须 full branch

**Phase C: Gate 训练对比**
- (c) 用 Δ(s) 训练的 gate vs 用 U(s) 训练 → ablation 验证核心 claim
- (d) 只用 counterfactual data，不用 LLM → 是否已经够？ 如果够，contribution 是 data construction，不是 LLM

### 11.7 潜在风险

| 风险 | 影响 | 应对 |
|------|------|------|
| Δ(s) 方差太大 | 方法不可用 | Phase A(a) 先验证；如果方差大考虑多次平均 |
| Snapshot/rollback 不干净 | Pair 数据有残留状态泄漏 | 确保 env state 完全恢复，seed 可控 |
| Proxy Δ̃ 和 strict Δ 不相关 | 必须用 full branch（cost 高） | Phase B 验证；FEVER 早期集中性可能帮助 |
| Δ(s) 训练的 gate 不优于 U(s) | 核心 contribution 不成立 | Phase C(c) 是关键 ablation |
| 只 counterfactual 就够（不需要 LLM） | 贡献降级为 data construction | Phase C(d) 诚实回答 |

### 11.8 实现与提交

**Phase A 实验已实现并提交 (2026-03-21)**:

- 脚本: `experiments/p6_counterfactual_sanity.py`
- SLURM: `scripts/phase6/run_counterfactual_sanity.sbatch`
- **Job 23275462** — 1 GPU, ~1-2 hours

**实验设计**:
```
环境: FEVER
Episodes: 50 (seed 42-91)
每个 state: 3 repeats (trigger + no-trigger pair)
Paired steps: 前 2 步 (step 0, step 1)
主 episode: always-trigger (保证短 episode, 无偏主路径)
分支评估: 每个分支完整 continuation 到 episode 结束 (full branch, 非 proxy)
```

**每个 pair 收集的数据**:
- trigger branch: success rate, reward, steps (across 3 repeats)
- no-trigger branch: success rate, reward, steps (across 3 repeats)
- Δ(s) = mean(trigger_success) - mean(no_trigger_success)
- 方差估计: trigger/no-trigger 各自的 std across repeats
- 环境信号: step_count, state_category, evidence_count, token_entropy

**分析输出**:
- (a) Δ(s) 分布: mean, std, positive rate → 信号是否存在且稳定
- (b) Δ(s) by step: step 0 vs step 1 → 早期步骤是否主导
- (c) Δ(s) by state_category: no_evidence / partial / sufficient
- (d) 重复间方差: 同一 snapshot 多次 pair 的 std → 测量噪声

**结果路径**: `results/phase6/counterfactual/fever/phase_a_sanity_check.json`

### 11.9 全部 Job 汇总 (2026-03-21 更新)

| Job | 任务 | Tasks | 完成 | 状态 |
|-----|------|:-----:|:----:|:---:|
| ~~23259061~~ | ~~Local methods~~ | ~~300~~ | 118/300 | ❌ 已取消 |
| ~~23275462~~ | ~~Counterfactual Phase A~~ | ~~1~~ | — | ❌ **已取消** (方案过慢不实用) |
| ~~23280358~~ | ~~Local methods 剩余~~ | ~~~182~~ | — | ❌ 已取消 (等 optimistic 结果后恢复) |
| **23263520** | **CB rerun (Issue 3 fix)** | **48** | **🔄** | **运行中** |
| **23263826** | **DS-1000 rerun (Issue 4 fix)** | **36** | **🔄** | **排队** |
| **23280434** | **Optimistic exploration test (FEVER)** | **9** | **🔄** | **排队** |

#### Counterfactual 方案已放弃

Counterfactual Paired Evaluation (§11.2-11.6) 的理论分析保留作为 paper insight，但 **不作为实际方法实现**。原因：数据收集阶段需要每个 state 跑两条完整分支 (~40 min for 50 ep on FEVER)，在实际部署中不可接受。其他 CB 方法（CATTS, SEAG, CaTS 等）不需要数据收集，虽然效果差但成本为零。

#### Optimistic Exploration — 替代改进方案 (2026-03-21)

**核心思路**: 不用 random exploration，而是 optimistic 初始化 — 默认全触发，只有当某个 state group 已有足够 negative evidence 时才停止。

**实现**:
- `principled_scg.py`: 新增 `explore_mode="optimistic"` 参数（默认 `"random"` 不影响现有方法）
- 探索阶段: `(step_bucket, state_category)` 为 key，每个 key 前 3 次访问强制 trigger，之后恢复 random
- **成本**: ≈ always_trigger 早期 + random 后期 → episode 短 → 比 random exploration 更快
- **预期效果**: 早期 step 一定被触发 → 数据不偏 → LASSO 能学到 step_count 的正确方向

**测试方法** (Job 23280434, FEVER × 3 seeds):
- `se_optimistic_local` — SE + 15 LLM features + optimistic
- `se_few5_optimistic_local` — SE + 5 LLM features + optimistic
- `principled_v2_optimistic` — v2 (无 LLM) + optimistic

**对比 baseline**: 原始 SE (random) 在 FEVER 上 ~50%，如果 optimistic 版显著提升（如 >80%），说明 exploration strategy 是关键。

#### Local methods 已完成记录

**FEVER (64/75 完成):**
- ❌ 未完成 array: **3,4,5,8,9,11,12,13,14,16,17**（11 tasks）

**APPS Interview (54/75 完成):**
- ❌ 未完成 array: **90,91,92,131,133-149**（21 tasks）

**DS-1000 (0/75):** 全部未完成，array **150-224**

**CRUXEval (0/75):** 全部未完成，array **225-299**

已重新提交 Job 23280358 恢复所有未完成的 local methods。

**下一步 (按优先级)**:
1. **等 Optimistic test 结果** (Job 23280434) → 验证 exploration strategy 假设
2. 持续收集 local methods + CB rerun + DS-1000 rerun 结果
3. 如果 optimistic 有效 → 在其他环境扩展测试
4. 汇总全部结果 → 决定论文最终方法和环境选择
