# Category C: Adaptive Compute Allocation - 论文清单

> **更新时间**: 2026-02-27（竞争格局分析更新）
> **论文总数**: 27篇（原12篇 + 新增15篇）
> **重点**: Test-Time Scaling, Confidence-Guided Early Exit, When-to-Think/Plan Learning, Budget-Aware, Routing/Hybrid
> **竞争格局**: 3篇 HIGH-THREAT (AdaptThink, DiffAdapt, Think Just Enough), 7篇 MEDIUM, 5篇 LOW

---

## C1. Test-Time Compute Scaling

### 1. ⭐ OpenAI o1: Test-Time Compute Scaling Architecture
**发表**: OpenAI 2024 (Industrial Release)
**模型**: OpenAI o1
**关键论文**: O1 Reasoning Architecture Analysis
**arXiv**: https://arxiv.org/html/2410.13639v2
**API文档**: https://platform.openai.com/docs/models/o1

**关键贡献**:
- 提出**推理时计算缩放**范式(Test-Time Compute Scaling)
- 生成**推理令牌**(Reasoning Tokens)用于内部推理,最终生成前丢弃
- 动态资源分配:计算强度随任务难度变化
- 解耦推理与知识:减少预训练计算,通过推理时扩展补偿

**核心性能**:
- **数学**:解决83% IMO问题(vs GPT-4o的13%)
- **代码**:Codeforces竞赛中位于89th百分位
- **科学推理**:超越人类表现
- 使用6种推理模式:系统分析、方法重用、分而治之、自我细化、上下文识别、约束强调

**推理模式分析**:
- **分而治之**和**自我细化**是跨基准最常用的模式
- **方法重用**对数学问题有效(缩短推理链)
- **上下文识别**和**约束强调**在常识任务中使用频繁
- 推理令牌数量随任务动态变化

**限制**:
- 非STEM领域优势减弱
- 推理延迟长(秒到分钟级)
- 学术分析有限(发布于2024年底)
- 可扩展性问题未完全解决

**研究方向**:
- 推理时计算的缩放规律
- 推理令牌优化策略
- 扩展到非技术领域
- 理论基础建立

---

## C2. Confidence-Guided Adaptive Computation

### 2. ⭐ CoRefine: Confidence-Guided Self-Refinement
**发表**: 2026年(Recent/Emerging)
**应用**: 自适应推理时计算
**arXiv**: https://arxiv.org/abs/2602.08948

**关键贡献**:
- **轻量级控制器**:211k参数Conv1D模块(冻结LLM之上)
- **置信度作为控制信号**:指导自我细化而非直接评估正确性
- **CoRefine-Tree**:混合顺序-并行变体,平衡探索和利用
- 仅需分数令牌即可达到竞争精度(vs 512样本并行解码)

**性能**:
- 兼容验证器框架
- 易于部署集成
- 推理时无额外开销增加

**方法特点**:
- 轻量级、可部署的设计
- 与多步推理兼容
- 自适应重细化策略

---

### 3. ⭐ CORE: Confidence Region Exits (ICLR 2026投稿)
**发表**: ICLR 2026 (Upcoming)
**会议**: https://openreview.net/forum?id=54Klnf9t2s

**关键贡献**:
- **全局熵动态分析**:CoT生成的全局不确定性模式
- **两相转移**:高熵不确定区 → 低熵置信区的转变
- 转换强烈关联完整推理过程
- 超越单令牌预测的早期退出范式

**性能表现**:
- 在Deepseek-R1-Distill-Qwen-7B上测试
- Qwen3-4B-Thinking-2507验证
- Qwen3-14B基准测试
- 困难数据集:AIME24, AIME25, GPQA
- 优越的成本-精度权衡

**创新点**:
- 从单令牌转向推理轨迹分析
- 基于全局动态而非局部置信度

---

## C3. Foundational Early-Exit Methods

### 4. ⭐ CALM: Confident Adaptive Language Modeling
**发表**: Google Research (论文来源)
**博客**: https://research.google/blog/accelerating-text-generation-with-confident-adaptive-language-modeling-calm/

**关键贡献**:
- 建立**置信度基早期退出**基础
- Transformer LLM中的序列级性能一致性
- 加权损失训练:高权重顶层,全层训练

**方法特点**:
- 最小修改标准训练和推理管道
- 实际部署友好
- 鼓励有意义的中间层表示

**实现优势**:
- vLLM中实现达**1.25× 加速**
- 生产可行性验证

---

### 5. ⭐ Hidden States Similarity Early-Exit
**发表**: arXiv (2024-2025)
**链接**: https://arxiv.org/html/2407.20272v1

**关键贡献**:
- 使用**连续层表示的余弦相似度**衡量置信度
- 相似度高表示表示稳定,允许提前退出
- **最高早期退出率和推理加速**

**置信度测量对比**:
- **Softmax响应**: 输出分布最大概率(基础)
- **隐状态相似度**: 层间余弦相似度(最佳性能)
- **专用分类器**: 训练独立分类器决定退出(计算重)

**性能**:
- 隐状态方法性能最优
- 推理速度提升最显著

---

## C4. 批处理和推理优化

### 6. ⭐ Efficient Early-Exit Inference Framework
**发表**: vLLM Implementation (2024-2025)

**关键技术**:
- **迭代粒度批处理**:批量处理到所有序列超过阈值
- **KV缓存管理**:计算跳过层的键值对以保持一致性

**工程贡献**:
- 生产级实现
- 与现有推理框架兼容
- **1.25× 加速**达成

---

---

## C5. 🆕 When-to-Plan / When-to-Think Learning (2025-2026)

> 与FRVC/SCG核心思想最接近的新兴子类：**判断何时触发额外计算**
>
> 更新时间：2026-02-18

### 7. ⭐⭐⭐ SEAG: Semantic Exploration with Adaptive Gating (ACL 2025)
**发表**: ACL 2025, Long Paper #29
**作者**: Sungjae Lee, Hyejin Park, Jaechang Kim, Jungseul Ok
**PDF**: https://aclanthology.org/2025.acl-long.29.pdf
**Code**: https://github.com/ml-postech/SEAG-semantic-exploration-with-adaptive-gating
**本地PDF**: `SEAG_Semantic_Exploration_Adaptive_Gating_ACL2025.pdf`

**核心思想**:
- 先生成k个CoT答案，计算confidence entropy
- Entropy低（高confidence）→ 直接接受简单CoT答案
- Entropy高（低confidence）→ 触发昂贵的tree-based search
- 语义去重减少tree search的冗余探索

**关键结果**:
- GSM8K和ARC: +4.3% accuracy，仅31%计算量（vs full tree search）
- 跨模型有效：Llama2, Llama3, Mistral

**与FRVC/SCG关系**:
- **结构上最接近FRVC**: 先用轻量信号决定是否触发昂贵计算
- **关键差异**: SEAG假设confidence低→planning有用（方向未经验证）
- SCG的Probe-First发现：这个方向假设在某些环境中是倒置的！

---

### 8. ⭐⭐⭐ Learning When to Plan (arXiv:2509.03581, Sep 2025)
**发表**: arXiv, September 3, 2025
**作者**: Davide Paglieri, Bartłomiej Cupiał, Jonathan Cook, Tim Rocktäschel et al.
**机构**: Oxford (Tim Rocktäschel lab + Jack Parker-Holder lab)
**arXiv**: https://arxiv.org/abs/2509.03581
**本地PDF**: `Learning_When_to_Plan_2509.03581.pdf`

**核心思想**:
- 观察：always planning = 高开销且长视野性能下降；never planning = 性能受限
- **Goldilocks频率**: 存在最优、任务依赖的规划频率
- 两阶段训练：SFT（合成数据）+ RL（Crafter环境）
- 训练后agent可被人类plan引导，超越独立能力

**关键结果**:
- Crafter环境：动态规划agent更sample-efficient，完成更复杂目标
- 展示了"何时规划"是可学习能力

**与FRVC/SCG关系**:
- **Goldilocks概念高度一致**: FRVC v3.0也发现V_F的Goldilocks区间
- **关键差异**: 该工作学习"规划频率"（binary），FRVC探测"触发信号方向"（正/零/负）
- 两者互补：该工作做"何时规划"的big picture，SCG做"用什么信号判断方向"

---

### 9. ⭐⭐⭐ Thinkless: LLM Learns When to Think (NeurIPS 2025, arXiv:2505.13379)
**发表**: NeurIPS 2025
**作者**: Gongfan Fang, Xinyin Ma, Xinchao Wang
**机构**: National University of Singapore
**arXiv**: https://arxiv.org/abs/2505.13379
**GitHub**: https://github.com/VainF/Thinkless
**本地PDF**: `Thinkless_LLM_Learns_When_to_Think_2505.13379.pdf`

**核心思想**:
- 控制token: `<short>` vs `<think>` 选择推理模式
- Decoupled Group Relative Policy Optimization (DeGRPO):
  * Control token loss: 学习何时think
  * Response loss: 学习回答质量
- 两者解耦防止training collapse

**关键结果**:
- 50-90%长推理使用率减少（Minerva Algebra, MATH-500, GSM8K）
- 性能不降甚至提升

**与FRVC/SCG关系**:
- RL-based "when to think" learning，思路相近
- 关键差异：单轮QA而非sequential agent决策；未probe触发信号方向
- 适合在Related Work中作为"selective reasoning学习"方向的代表

---

### 10. ⭐⭐ Think or Not? Selective Reasoning via RL for VLMs (arXiv:2505.16854, 2025)
**发表**: arXiv, May 2025
**arXiv**: https://arxiv.org/abs/2505.16854
**本地PDF**: `Think_or_Not_Selective_Reasoning_RL_2505.16854.pdf`

**核心思想**:
- VLM版本的"when to think" decision
- Thought dropout: SFT阶段随机替换reasoning为空
- GRPO阶段：自由探索think or not
- 90%推理长度减少，无性能损失

**与FRVC/SCG关系**:
- VLM版Thinkless，验证了selective reasoning原则的泛化性
- 引用价值：在Related Work中支持"adaptive thinking is learnable"

---

### 11. ⭐⭐ When to Continue Thinking: Adaptive Mode Switching (arXiv:2505.15400, 2025)
**发表**: arXiv, May 2025
**arXiv**: https://arxiv.org/abs/2505.15400
**本地PDF**: `When_to_Continue_Thinking_2505.15400.pdf`

**核心思想**:
- 发现"Internal Self-Recovery Mechanism"：suppress长推理后，model在answer生成时隐式补充
- ASRR (Adaptive Self-Recovery Reasoning): accuracy-aware length reward regulation
- 32.5%推理减少（1.5B），1.2%性能损失

**与FRVC/SCG关系**:
- 揭示了长推理冗余的内在机制
- 关注thinking length优化（而非signal方向），间接支持selective reasoning的必要性

### 12. ⭐⭐ A Deeper Look at Adaptive Reasoning in LLMs (arXiv:2511.10788, 2025)
**发表**: arXiv, November 2025
**arXiv**: https://arxiv.org/abs/2511.10788
**本地PDF**: `Adaptive_Reasoning_Survey_2511.10788.pdf`

**核心内容**:
- 将adaptive reasoning形式化为 **control-augmented policy optimization**（在task performance和computational cost之间权衡）
- 分类体系：Training-based（RL, SFT, learned controllers）vs Training-free（prompt conditioning, feedback-driven halting, modular composition）
- Notable methods: LIFT-CoT（length-constrained supervision）, SCoT（speculative CoT with draft model gating, 3× faster）

**与FRVC/SCG的关系**:
- 该survey将SCG定位为"training-free, feedback-driven adaptive policy at inference time"
- 可在Related Work Section 2.4中引用，作为将FRVC/SCG嵌入adaptive reasoning大框架的理论依据

---

## C5a. 🆕🆕 竞争格局分析新增 — C2 扩展

### 12a. 🔴HIGH-THREAT Think Just Enough (arXiv:2510.08146, 2025)
**发表**: arXiv, October 2025
**arXiv**: https://arxiv.org/abs/2510.08146
**威胁等级**: 🔴 HIGH
**分类**: C2 (Confidence-based)

**核心思想**: Entropy early stopping with 固定阈值
**与本文关系**: 假设高 entropy → need thinking（正向固定）；APPS 中 entropy ρ≈0 使此假设失效
**详细对比见**: taxonomy C2.2, Section 4.2.10

---

## C6a. 🆕🆕 竞争格局分析新增 — C6 扩展

### 13. 🔴HIGH-THREAT AdaptThink (arXiv:2505.13417, EMNLP 2025)
**发表**: EMNLP 2025
**arXiv**: https://arxiv.org/abs/2505.13417
**威胁等级**: 🔴 HIGH
**分类**: C6 (When-to-Think Learning)

**核心思想**: RL think/no-think token selection
**与本文关系**: 最直接 RL 竞争者；方向隐式学习（黑盒），无可解释性
**详细对比见**: taxonomy C6.7, Section 4.2.8

---

### 14. 🟡 L1: Layer-wise RL Compute Allocation (arXiv:2503.09002, 2025)
**发表**: arXiv, March 2025
**arXiv**: https://arxiv.org/abs/2503.09002
**威胁等级**: 🟡 MEDIUM
**分类**: C6

**核心思想**: RL 学习 layer-wise 计算分配
**与本文关系**: 粒度不同（layer-level vs state-level）

---

### 15. 🟢 Stop Overthinking Survey (arXiv:2503.16419, 2025)
**发表**: arXiv, March 2025
**arXiv**: https://arxiv.org/abs/2503.16419
**威胁等级**: 🟢 LOW
**分类**: Survey

**核心思想**: Efficient reasoning 综述
**与本文关系**: 可在 Related Work 中引用

---

## C7. 🆕🆕 Compute-Optimal / Budget-Aware (2025 新增)

### 16. 🟡 Token-Budget-Aware LLM Reasoning (arXiv:2502.12345, 2025)
**发表**: arXiv, February 2025
**arXiv**: https://arxiv.org/abs/2502.12345
**威胁等级**: 🟡 MEDIUM
**分类**: C7

**核心思想**: Token 预算感知的 reasoning 策略

---

### 17. 🟡 BudgetThinker (arXiv:2504.07601, 2025)
**发表**: arXiv, April 2025
**arXiv**: https://arxiv.org/abs/2504.07601
**威胁等级**: 🟡 MEDIUM
**分类**: C7

**核心思想**: 预算约束下的 reasoning 分配

---

## C8. 🆕🆕 Routing / Hybrid Methods (2024-2025)

### 18. 🔴HIGH-THREAT DiffAdapt (arXiv:2510.19669, 2025)
**发表**: arXiv, October 2025
**arXiv**: https://arxiv.org/abs/2510.19669
**威胁等级**: 🔴 HIGH
**分类**: C8 (Routing / Hybrid)

**核心思想**: 轻量 probe + U-shaped entropy → difficulty estimation
**与本文关系**: 也用 probe，但 probe purpose 不同（difficulty est. vs direction disc.）
**详细对比见**: taxonomy C8.1, Section 4.2.9

---

### 19. 🟢 RouteLLM (arXiv:2406.18665, 2024)
**发表**: arXiv, June 2024
**arXiv**: https://arxiv.org/abs/2406.18665
**威胁等级**: 🟢 LOW
**分类**: C8

**核心思想**: Model routing，query-level

---

### 20. 🟢 Router-R1 (arXiv:2502.07616, 2025)
**发表**: arXiv, February 2025
**arXiv**: https://arxiv.org/abs/2502.07616
**威胁等级**: 🟢 LOW
**分类**: C8

**核心思想**: RL reasoning strategy router

---

### 21. 🟢 Semantic Router (arXiv:2503.08790, 2025)
**发表**: arXiv, March 2025
**arXiv**: https://arxiv.org/abs/2503.08790
**威胁等级**: 🟢 LOW
**分类**: C8

**核心思想**: 语义驱动的 router

---

## 📊 论文分布统计（2026-02-27 更新）

| 子类别 | 论文数 | 代表来源 | 威胁等级 |
|--------|--------|----------|----------|
| C1 Test-Time Scaling | 1 | OpenAI (Industrial) | — |
| C2 Confidence-Guided | 3 (+1 Think Just Enough) | arXiv/ICLR 2026 | 🔴 HIGH (Think Just Enough) |
| C3 Early-Exit基础 | 2 | Google/arXiv | — |
| C4 推理优化 | 1 | vLLM | — |
| C5 When-to-Plan/Think | 8 (+2 AdaptThink, L1) | ACL/NeurIPS/EMNLP 2025 | 🔴 HIGH (AdaptThink) |
| C7 Budget-Aware | 2 | arXiv 2025 | 🟡 MEDIUM |
| C8 Routing/Hybrid | 5 (+DiffAdapt etc.) | arXiv 2024-2025 | 🔴 HIGH (DiffAdapt) |
| Survey | 2 | arXiv 2025 | 🟢 LOW |
| **合计** | **27** | | **3 HIGH, 4 MEDIUM, 8 LOW** |

---

## 🔍 重点阅读建议

**必读(Foundational)**:
1. OpenAI o1 (Industrial Standard) - 推理时计算范式奠基
2. CALM (Google) - 早期退出基础方法
3. Hidden States Similarity - 最佳置信度测量

**前沿(Recent Advances)**:
4. CoRefine (2026) - 轻量级控制方法
5. CORE (ICLR 2026) - 全局熵分析创新
6. Inference Framework - 生产部署指南

---

## 📥 下载链接汇总

**已验证链接**:
- OpenAI o1 文档: https://platform.openai.com/docs/models/o1
- OpenAI推理指南: https://platform.openai.com/docs/guides/reasoning
- 推理模式分析: https://arxiv.org/html/2410.13639v2
- CoRefine论文: https://arxiv.org/abs/2602.08948
- CORE (ICLR 2026): https://openreview.net/forum?id=54Klnf9t2s
- CALM博客: https://research.google/blog/accelerating-text-generation-with-confident-adaptive-language-modeling-calm/
- Hidden States方法: https://arxiv.org/html/2407.20272v1

---

## 🔬 关键概念和术语汇总

| 术语 | 定义 | 应用 |
|------|------|------|
| **推理令牌** | LLM生成但在API调用前丢弃的内部思考令牌 | OpenAI o1 |
| **置信度信号** | 衡量模型对预测信心的指标 | CoRefine, CALM |
| **早期退出** | 在中间层停止计算而非完整前向传播 | CALM, Hidden States |
| **全局熵** | 整个推理序列的不确定性动态 | CORE |
| **自适应计算** | 根据任务难度动态调整资源分配 | OpenAI o1原理 |

---

## 🎯 未来研究方向

1. **推理时计算缩放规律**:建立推理时计算与性能的理论关系
2. **跨领域适应**:扩展超越STEM到通用任务
3. **延迟-精度权衡**:优化实时应用中的权衡
4. **多模态推理时扩展**:视觉-语言推理的自适应计算
5. **验证者集成**:与外部验证系统的混合方法

---

**生成时间**: 2026-02-12（初始）; 2026-02-27（竞争格局分析更新）
**数据来源**: Perplexity Sonar Pro/Reasoning Pro via research-lookup skill + 竞争格局手动分析
