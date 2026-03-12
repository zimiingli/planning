# 实验补充 & 待验证想法

> **创建日期**: 2026-02-27
> **最后更新**: 2026-02-27（Phase 3+ APPS 结果整合）
> **用途**: 记录自发产生的担忧、需要纠正的地方、reviewer 可能攻击的点、以及对应的补充实验方案

---

## 目录

1. [Direction Reversal 归因 Confound](#1-direction-reversal-归因-confound)
2. [跨环境信号不一致性（比方向反转更深）](#2-跨环境信号不一致性)

---

## 1. Direction Reversal 归因 Confound

**提出日期**: 2026-02-27
**严重性**: 🟠 中（APPS 数据部分缓解，但未完全消除）
**状态**: 🟡 部分回答（APPS 数据提供新证据，假说需修订）

### 1.1 担忧

当前论文核心 claim C2 是 "signal-utility direction varies across environments"。但 HotpotQA 和 MBPP 的 rollout 设计存在一个未分离的 confound：

| | HotpotQA | MBPP | **APPS** (新增) |
|--|----------|------|------|
| **Optimizer T** | Per-action exhaustive eval | K-variant generation | K-variant generation |
| **Evaluator** | **LLM 自身**（self-eval） | **Unit test**（外部 oracle） | **Unit test**（外部 oracle） |
| **候选来源** | 穷举 action space (K≤5) | 温度采样 K=5 变体 | 温度采样 K=5 变体 |
| **token_entropy ρ** | **−0.327** | **+0.153** | **≈0 (−0.001)** |
| **最强信号** | evidence_count (ρ=−0.586) | step_count (ρ=+0.526) | test_pass_rate (ρ=−0.620) |

原始假说：方向反转可能不是 environment 的性质，而是 **evaluator 是否独立** 的性质。

### 1.2 APPS 数据对假说的冲击 🆕

**APPS 结果部分否定了"evaluator 独立性 → 正方向"的简单假说：**

| 环境 | Evaluator 类型 | token_entropy ρ | 按原假说预期 | 实际 |
|------|---------------|:-:|:-:|:-:|
| HotpotQA | self-eval | −0.327 | 负 ✅ | 负 ✅ |
| MBPP | unit test (外部 oracle) | +0.153 | 正 ✅ | 正 ✅ |
| **APPS** | **unit test (外部 oracle)** | **≈0** | **正 ❌** | **≈0** |

APPS 和 MBPP **都使用 unit test 作为外部 oracle evaluator**，但 token_entropy 的表现截然不同：
- MBPP: ρ=+0.153（正相关，符合"外部 oracle → 正方向"假说）
- APPS: ρ≈0（完全无效，**违反**"外部 oracle → 正方向"假说）

**结论**：evaluator 独立性不是方向的**充分**决定因素。APPS 有外部 oracle 但 token_entropy 仍然无效——说明还有其他因素在起作用。

### 1.3 修订后的假说

**原假说（过度简化）**：
> "evaluator 独立性决定方向。self-eval → 负，external oracle → 正"

**修订假说（基于 APPS 数据）**：
> "方向取决于 **(signal 的信息量, environment 的任务结构, evaluator 类型)** 的交互。token_entropy 在代码生成任务中**固有地**缺乏信息量（代码语法结构使 token 分布高度确定），无论 evaluator 是否独立。"

**为什么 token_entropy 在 APPS 中无效**：
1. 代码生成的 token 分布受语法结构约束（关键字、缩进、括号），entropy 更多反映语言结构而非"不确定性"
2. APPS 的真正不确定性体现在**代码逻辑**层面（算法选择、边界处理），而非**token**层面
3. 因此 APPS 的最强信号是 **test_pass_rate**（ρ=−0.620）——直接测量代码质量，与 token 无关

**更精确的归因模型**：
```
方向 = f(signal 信息量 × environment 任务结构 × evaluator 类型)

信号维度：
  - token_entropy: 在自然语言任务 (HotpotQA) 中有信息量，在代码任务 (APPS/MBPP) 中信息量有限
  - test_pass_rate: 仅在代码任务中存在且极强 (ρ=−0.620)
  - evidence_count: 仅在 QA 任务中存在且强 (ρ=−0.586)

环境维度：
  - 任务结构决定哪些信号有信息量
  - 模型能力边界决定信号的语义（多样性 vs 困惑）

Evaluator 维度：
  - 仍然是一个因素，但不是唯一因素
  - APPS 证明即使有外部 oracle，如果信号本身无信息量，方向也不会是正的
```

### 1.4 已有的相关证据（更新版）

**支持"方向由多因素决定"的证据：**

1. **APPS token_entropy ≈ 0 (新增)**：有外部 oracle 但 entropy 无效，证明 evaluator 独立性不充分
2. **APPS test_pass_rate ρ=−0.620 (新增)**：域特异信号极强，说明信号选择比方向更关键
3. **Phase 2.5 S2 方向翻转**：HotpotQA 上换 T（per-action → K-variant），token_entropy ρ 从 −0.327 翻转为 +0.221（但 T_new 91.6% U=0，数据 sparse）
4. **多信号一致性**：HotpotQA 上 state_category（η²=0.359）、evidence_count（ρ=−0.586）都呈负向——系统性环境级特征
5. **Finish shortcut 去除后方向仍负**：ρ=−0.327 → ρ=−0.242

**支持"evaluator 仍是部分因素"的证据：**

1. **HotpotQA 是唯一使用 self-eval 且方向为负的环境**——self-eval 可能是负方向的必要条件之一（但非充分条件）
2. **MBPP evaluator 完全独立**：lottery effect 天然产生正相关
3. **逻辑反事实仍成立**：如果在 HotpotQA 用 GPT-4o 做 evaluator，方向可能改变

### 1.5 对论文 C2 claim 的影响

**Phase 3+ APPS 结果实际上让 C2 更强，而非更弱：**

原来 C2 只是说"token_entropy 方向反转"（HotpotQA 负 vs MBPP 正）。现在 APPS 数据揭示了更深的现象：**不同环境需要完全不同的信号集**。

| 环境 | 最强信号 | token_entropy 有效？ |
|------|---------|:---:|
| HotpotQA | evidence_count (ρ=−0.586) | ✅ (ρ=−0.327) |
| MBPP | step_count (ρ=+0.526) | ⚠️ (ρ=+0.153, 弱) |
| APPS | test_pass_rate (ρ=−0.620) | ❌ (ρ≈0) |

这意味着 C2 可以从"方向反转"升级为"信号-效用关系的全面环境依赖性"：
- 方向可以反转（HotpotQA 负 vs MBPP 正）
- 信号可以完全失效（APPS 中 token_entropy ≈ 0）
- 最强信号因环境而完全不同（evidence_count / step_count / test_pass_rate）

**论文叙事升级**：从 "direction varies" 到 "the entire signal-utility landscape is environment-dependent"。

### 1.6 修订后的补充实验建议

#### 实验 A: HotpotQA Evaluator 对照（优先级 🟡 降低）

**原优先级**：🔴 推荐
**修订优先级**：🟡 如果时间允许

**理由**：APPS 数据已部分回答了"evaluator 是否是唯一因素"——答案是"不是唯一因素"。实验 A 仍有价值（可以精确量化 evaluator 的贡献），但不再是 C2 claim 的生死攸关实验。

**思路不变**：固定环境（HotpotQA）、固定 T（per-action eval），只改变 evaluator：

| 条件 | Evaluator | 预期方向 |
|------|-----------|---------|
| 条件 1（现有） | LLM self-eval | ρ < 0（已有数据） |
| 条件 2（新增） | Ground-truth F1 | ρ ??? |

**实施成本**：低。复用 Phase 1 已收集的 rollout 数据（1208 个 decision points），只需改 utility 计算方式。

#### 实验 B: MBPP Self-Eval 对照（优先级 ⚪ 可选）

**原优先级**：🟠 中等
**修订优先级**：⚪ 可选（MBPP 已是 ceiling effect 环境，实验价值降低）

#### 实验 C: 利用 Phase 4 WebShop 做交叉验证（优先级 🟢 保持）

**思路**：WebShop 有外部 reward（任务完成度分数）+ 用 diverse sampling 作为 T + 非代码任务。

- 如果 WebShop token_entropy ρ > 0 → evaluator 独立性在非代码环境中可能确实重要
- 如果 WebShop token_entropy ρ ≈ 0 或 < 0 → 进一步否定 evaluator 简单假说
- 无论结果如何，都会提供新的信号-方向数据点

**实施成本**：零（Phase 4 本来就要做）。只需在 Signal Discovery 时关注方向。

#### 实验 D: APPS 信号迁移检验（新增，优先级 🟡）🆕

**思路**：验证 APPS 中 test_pass_rate 的方向是否在 MBPP 上一致。

| 环境 | test_pass_rate 存在？ | 预期 ρ |
|------|:---:|:---:|
| APPS | ✅ (ρ=−0.620) | 已知：强负 |
| MBPP | ✅ (可计算) | ??? |

- 如果 MBPP test_pass_rate 也是负方向 → 代码环境内部信号方向一致性
- 如果 MBPP test_pass_rate 方向不同 → 即使同类任务，信号方向也可变

**实施成本**：零。MBPP 已有 Phase 1 数据，可直接计算。

### 1.7 修订后的论文叙事建议

**当前叙事**（write_guide）：
> "Signal-utility direction varies across environments."

**建议调整为（基于 APPS 数据的更精确版本）**：
> "The signal-utility relationship is fundamentally environment-dependent: not only can the direction of a given signal reverse across environments (token_entropy: ρ=−0.327 in HotpotQA vs ρ=+0.153 in MBPP), but the most informative signal itself varies (evidence_count for QA, test_pass_rate for code generation, with token_entropy being uninformative in APPS despite ρ≈0). Any method that assumes a fixed signal or fixed direction will fail when deployed to a new environment."

**具体调整位置**：
- **Introduction Para 3**：扩展发现——不只是方向反转，还有信号有效性的环境依赖
- **Section 3.3**：将 "direction varies across environments" 升级为 "signal-utility landscape varies across environments"
- **Section 5.3 (E1)**：APPS 信号数据作为第三个数据点，展示跨环境信号不一致性表
- **Discussion 6.1**：讨论 evaluator independence 作为**部分**驱动因素（APPS 数据约束了这个假说的 scope）
- **Limitation**：诚实写明 "evaluator type, environment structure, and signal informativeness are confounded across our environments; controlled ablations are needed to fully disentangle these factors"

### 1.8 无论归因如何，direction discovery 的价值不变（加强版）

APPS 数据让这个论点**更强**：

1. **部署时你不一定有外部 oracle**——很多任务没有 unit test
2. **方向确实会变**——无论原因是 env、T 还是 evaluator
3. **你甚至不知道该看哪个信号**——HotpotQA 用 entropy，APPS 用 test_pass_rate，MBPP 用 step_count。预设任何单一信号都不对
4. **Wrong-direction 代价是实测的**：LR −34.5pp, MLP −51.2pp (RR=0%)
5. **Direction discovery 同时发现"看什么"和"怎么看"**——不仅发现方向，还发现最有效的信号

所以 APPS 数据实际上让 direction discovery 的价值论证更完整——**你需要 discovery 的不只是方向，还有信号本身**。

---

## 2. 跨环境信号不一致性（比方向反转更深）🆕

**提出日期**: 2026-02-27
**严重性**: 🟢 正面发现（强化论文核心 claim）
**状态**: ✅ 已有数据支撑

### 2.1 发现

Phase 3+ APPS Step 1 的信号发现揭示了一个比"方向反转"更深层的现象：**不同环境需要完全不同的信号集合**。

**跨环境信号-Utility 关系完整矩阵**：

| 信号 | HotpotQA ρ | MBPP ρ | APPS ρ | 跨环境一致？ |
|------|:----------:|:------:|:------:|:---:|
| token_entropy | −0.327 ↘ | +0.153 ↗ | −0.001 ≈0 | ❌ 三环境三种表现 |
| step_count | −0.023 ≈0 | +0.526 ↗ | +0.080 ↗ (边缘) | ❌ HotpotQA 无效 |
| evidence_count | −0.586 ↘ | N/A | N/A | (域特异) |
| test_pass_rate | N/A | N/A¹ | −0.620 ↘ | (域特异) |
| state_category | η²=0.359 | η²=0.214 | — | ⚠️ 部分一致 |

> ¹ MBPP 也有 test pass rate，但 Phase 1 未计算该信号的 ρ。建议补算（见实验 D）。

### 2.2 论文意义

这个发现可以在论文中以三个递进层次呈现：

**层次 1（Finding）**：同一信号在不同环境方向不同（token_entropy: −0.327 vs +0.153 vs ≈0）
**层次 2（Deeper Finding）**：最强信号因环境而完全不同（evidence_count / step_count / test_pass_rate）
**层次 3（Implication）**：**任何固定信号 + 固定方向的方法都无法跨环境工作**——不仅因为方向会变，还因为信号本身会失效

### 2.3 对 Figure 2（方向热力图）的设计启发

原设计：5 × 2 热力图（行=signal, 列=HotpotQA/MBPP）
修订设计：**5+ × 3 热力图（行=signal, 列=HotpotQA/MBPP/APPS）**

新增行：test_pass_rate（APPS 特有，在 HotpotQA/MBPP 列显示 N/A 或灰色）
视觉冲击：token_entropy 行从 蓝→红→灰（三环境三种状态），比原来的 蓝→红 更有说服力。

### 2.4 这个发现对 related work 定位的价值

现有方法（CoRefine, SEAG, CaTS, CATTS 等）**都预设了信号**（entropy, confidence, vote disagreement）。APPS 数据证明：即使选对了方向，如果选错了信号（如在 APPS 中用 token_entropy），gate 也会完全失效。

这让我们的 direction discovery framework 的价值从"发现方向"扩展到"发现最有效的信号+方向组合"——更全面的自动适配。

---

*（后续新想法和需要纠正的地方继续在此文件追加）*
