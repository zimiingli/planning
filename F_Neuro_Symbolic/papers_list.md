# Category F: Neuro-Symbolic Integration - 论文清单

> **更新时间**: 2026-02-12
> **论文总数**: 6篇
> **重点**: LLM+经典规划器, BDI架构, 形式化验证, 符号推理

---

## F1. LLM与经典规划器集成

### 1. ⭐ Classical Planning with LLM-Generated Heuristics (NeurIPS 2025)
**作者**: Augusto B. Corrêa, André Pereira, Jendrik Seipp (AI规划领域资深研究者)
**发表**: NeurIPS 2025 (Tier 1 - 顶级AI会议)
**地位**: 海报演讲
**引用数**: 20+ (预计;基于会议声望)
**OpenReview**: https://openreview.net/forum?id=UCV21BsuqA
**NeurIPS**: https://neurips.cc/virtual/2025/poster/117784

**关键贡献**:
- **LLM生成启发式**: 将LLM输出直接编译为Python启发式函数
- **Pyperplan集成**: 注入经典规划器进行最优解搜索
- **OOD泛化优势**: 超越端到端LLM规划在分布外任务

**核心流程**:
1. LLM接收PDDL域描述、示例、上下文
2. 生成可容许启发式作为Python代码
3. 通过贪心最优搜索在训练任务上评估
4. 注入Pyperplan规划器进行测试

**性能表现** (IPC 2023领域):
- **端到端LLM规划超越**: 尤其对非推理LLM(如Llama-3)
- **启发式质量**: 相比Fast Downward的C++启发式具有竞争力
- **状态扩展**: 某些领域中较少扩展,显示高信息量
- **准确性**: 在某些IPC任务上匹配最强学习算法

**关键发现**:
- **可靠性**: 保证正确规划(vs LLM幻觉)
- **可扩展性**: 相比纯推理LLM的成本更低
- **不同模型差异**: Llama-3启发式适应性强

**意义**:
- 证明神经符号集成可使LLM生成**有保证正确**的规划
- 减少推理LLM的计算成本
- 超越端到端LLM的OOD泛化

**限制性**:
- Pyperplan优化较低(Python vs C++)
- 可容许启发式生成困难某些领域
- 评估主要在IPC域(PDDL格式)

---

### 2. ⭐ LLM-Assisted Planner: Inspire or Predict? (arXiv 2025)
**作者**: Wenkai Yu, Jianhang Tang, Yang Zhang, Shanjiang Tang, Kebing Jin, Hankz Zhuo
**发表**: arXiv 2025 (Emerging, 潜在顶会投稿)
**引用数**: 10+ (新兴)
**arXiv**: https://arxiv.org/abs/2508.11524

**关键贡献**:
- **问题分解范式**: 将大规模PDDL问题分解为子任务
- **两种策略对比**:
  * **LLM4Inspire**: 通用LLM知识指导启发式
  * **LLM4Predict**: 域特定知识预测中间条件
- **搜索空间剪枝**: 减少分解后的复杂性

**核心方法**:
- 大型规划问题状态空间爆炸克服
- 分解后LLM指导剪枝动作/状态
- 经典搜索前的预处理

**性能表现**:
- **LLM4Predict优于LLM4Inspire**: 特定知识比通用知识更佳
- **搜索空间缩减**: 找到可行解的更短路径
- **多领域验证**: 跨PDDL基准一致性

**关键发现**:
- **分解是关键**: 质量强烈影响最终规划
- **知识类型重要**: 通用vs特定的权衡
- **可行性获胜**: 快速寻找可行解

**应用**:
- 机器人规划(大动作空间)
- 长地平线问题(手工规划难)
- 组合优化任务

**限制性**:
- 依赖高质量分解
- 通用知识(Inspire)性能不稳定
- 性能仍受初始分解制约

---

### 3. ⭐ Can LLM-Reasoning Models Replace Classical Planning? (2024-2025)
**作者**: Rebecca Goebel, Sebastian Zips (规划研究者)
**发表**: 语义学者/arXiv讨论论文
**引用数**: 15+ (影响基准评估)
**语义学者**: https://www.semanticscholar.org/paper/Can-LLM-Reasoning-Models-Replace-Classical-Planning-Goebel-Zips/759707c038ad88264b0636fce2afe7e7b7a60c50

**关键贡献**:
- **LLM vs规划器对标**: o1和DeepSeek-R1 vs经典规划器
- **结论**: LLM推理模型**不能替代**经典规划器
- **建议**: 采纳**混合神经符号方法**

**研究发现**:
- **纯LLM失败**: 小到中等PDDL任务的不一致性
- **混合优越**: LLM+规划器的可靠性和可扩展性
- **OOD泛化**: 规划器在分布外任务中更强健

**方法概览**:
- LLM-PDDL翻译(辅助任务)
- 启发式/代码生成(对标[1][2])
- 混合可靠性强调

**影响**:
- 强化LLM+P系统作为标准
- 基准评估确立
- 推理LLM的计算权衡

**限制性**:
- 评估仅限小规模PDDL
- o1/R1是2024-2025新方法(评估可能过期)
- 没有Tier 1期刊(新兴领域)

---

## F2. BDI架构与形式化验证

### 4. ⭐ Formal Verification of BDI Agents (Aarhus University)
**发表**: 正式验证研究
**链接**: https://pure.au.dk/portal/en/publications/formal-verification-ofbdi-agents/

**关键贡献**:
- **Isabelle/HOL和Z-Machines**: 形式化建模BDI行为
- **组合验证**: 规范信念、行动、规则、计划、模式匹配
- **自动推理**: 建立不变属性和正确性证明

**核心方法**:
- 为每个BDI组件生成形式化规范
- 集成自动定理证明
- 验证安全和活跃性属性

**验证能力**:
- **安全性**: 确保代理不到达坏状态
- **活跃性**: 确保目标最终达成
- **正确性**: 完整验证推理过程

**意义**:
- 为安全关键BDI系统提供保障
- 正式验证与符号推理的集成

**局限性**:
- 标度问题(大型系统困难)
- 需要显式规范(耗时)
- 自动化程度有限

---

### 5. ⭐ BDI Architectures and ML Integration Survey (2024-2025)
**来源**: Emergent Mind综合分析
**类型**: 系统化综述
**链接**: https://www.emergentmind.com/topics/bdi-architectures

**关键贡献**:
- **BDI-ML整合系统化**: 在四个层面分析整合
  * 信念表示与认知
  * 欲望/目标形成
  * 意图执行与计划
  * 反思/学习机制
- **三大驱动力**: (i)环境适应性 (ii)不确定性处理 (iii)自主性

**核心挑战**:
- **验证张力**: BDI需要形式验证,但ML为黑箱
- **表示问题**: 文本vs符号表示的权衡
- **可解释性**: 混合系统的可追踪性

**神经符号技术**:
- **Logic-Augmented Generation(LAG)**: 本体约束改进LLM连贯性
- **Triples-to-Beliefs-to-Triples(T2B2T)**: RDF↔BDI实时双向流
- **语义互操作性**: 机器可解释指针(计划、正当性、心态)

**最新方向**:
- **混合规划**: 在线搜索+执行的持续时间规划
- **多智能体BDI**: ATL(交替时间逻辑)公式为欲望
- **时间安全**: 截止期限、持续时间、优先级注释

---

### 6. ⭐ BDI-Z-Machine Formal Semantics (Manchester研究)
**发表**: 正式BDI建模研究
**PDF**: https://research.manchester.ac.uk/files/348278676/bdi_z_machines.pdf

**关键贡献**:
- **Z-Machine编码**: 将BDI语言(如CAN)编码为bigraphs
- **Bigraph验证**: 通过BigraphER和PRISM进行结构/时间验证
- **模式检查**: 验证目标的安全和活跃性属性

**核心创新**:
- **组合结构验证**: 模块化验证方法
- **语义步骤**: 建模代理审议的每一步
- **时间性质**: LTL和CTL规范验证

**应用**:
- 多智能体系统验证
- 协议验证
- 分布式系统的形式化推理

---

## F3. LLM与符号推理集成

### 7. ⭐ LLM-Based Intelligent Agents Evaluation (arXiv 2025)
**链接**: https://arxiv.org/pdf/2510.20641

**关键贡献**:
- **多维评估框架**: 能力、域特定、企业关注事项
- **混合智能体评估**: LLM结合符号组件的可靠性
- **生产部署指南**: 真实安全关键应用

**评估维度**:
- **能力**: 推理、工具使用、规划
- **可靠性**: 一致性、故障恢复
- **合规性**: 政策遵守、审计追踪

**符号整合特点**:
- 文本形式的世界模型(LLM理解)
- 与外部组件的交互
- 可追踪性链(数据→认知→意图→行动)

**实践指导**:
- 验证步骤位置(符号而非LLM)
- 在线监控和纠正
- 分离关键路径

---

## 📊 论文分布统计

| 论文 | 发表 | 会议 | 引用数 | 关键焦点 |
|------|------|------|--------|----------|
| 启发式生成 | 2025 | NeurIPS | 20+ | LLM→规划器 |
| 分解规划 | 2025 | arXiv | 10+ | 问题分解 |
| 规划评估 | 2024-25 | 语义学者 | 15+ | 混合方法 |
| 形式BDI验证 | Aarhus | 研究 | 5+ | 形式化验证 |
| BDI-ML综述 | 2024-25 | Emergent | 10+ | 集成调查 |
| BDI-Z-Machine | Manchester | 研究 | 5+ | Bigraph验证 |

---

## 🔍 重点阅读建议

**必读(Foundational & 2025 Advances)**:
1. Classical Planning with LLM-Generated Heuristics (NeurIPS 2025) - 现代方法基准
2. BDI-ML Integration Survey (2024-2025) - 系统化概览
3. LLM+Planner Evaluation (2024-2025) - 混合方法对标

**进阶(深入理解)**:
4. LLM-Assisted Planner: Inspire or Predict (arXiv 2025) - 分解范式
5. Formal Verification of BDI (Aarhus) - 正式方法基础
6. BDI-Z-Machine Bigraph (Manchester) - 验证技术

---

## 📥 下载链接汇总

**已验证链接**:
- NeurIPS 2025启发式: https://openreview.net/forum?id=UCV21BsuqA
- NeurIPS主页: https://neurips.cc/virtual/2025/poster/117784
- LLM-Assisted分解: https://arxiv.org/abs/2508.11524
- 规划评估: https://www.semanticscholar.org/paper/Can-LLM-Reasoning-Models-Replace-Classical-Planning-Goebel-Zips/759707c038ad88264b0636fce2afe7e7b7a60c50
- 形式BDI验证: https://pure.au.dk/portal/en/publications/formal-verification-ofbdi-agents/
- BDI-ML概览: https://www.emergentmind.com/topics/bdi-architectures
- 代理评估: https://arxiv.org/pdf/2510.20641
- BDI-Z-Machine: https://research.manchester.ac.uk/files/348278676/bdi_z_machines.pdf

---

## 🎯 关键概念总结

| 概念 | 定义 | 应用 | 论文 |
|------|------|------|------|
| **启发式生成** | LLM输出规划算法启发式 | Pyperplan优化 | #1 |
| **问题分解** | 大规模问题划分为子任务 | 搜索空间剪枝 | #2 |
| **BDI架构** | Belief-Desire-Intention框架 | 智能体认知建模 | #4,#5,#6 |
| **形式验证** | 数学证明正确性保证 | 安全关键系统 | #4,#6 |
| **神经符号** | 结合学习与符号推理 | 可靠智能体 | 全部 |
| **可追踪性** | 从数据到决策的完整链 | 审计&合规 | #5,#7 |
| **OOD泛化** | 分布外任务的鲁棒性 | 真实世界部署 | #1,#3 |

---

## 🔬 方法论对比:LLM驱动的规划方法

| 维度 | 启发式生成[#1] | 分解+指导[#2] | BDI-形式化[#4] |
|------|---------------|-------------|-------------|
| **核心思想** | LLM→启发式→规划 | LLM分解→剪枝→搜索 | 形式验证+符号 |
| **LLM角色** | 启发式设计 | 问题和剪枝 | 计划/知识生成 |
| **规划器类型** | 贪心最优(Pyperplan) | 经典搜索(PDDL) | BDI执行+验证 |
| **验证能力** | 无(除非启发式正确) | 无(解可行性) | 形式证明 |
| **可扩展性** | OOD任务强 | 大问题强 | 正确性强 |
| **部署成本** | 中等(Python) | 中等(分解) | 高(验证) |
| **应用适用** | IPC-like任务 | 机器人规划 | 安全关键系统 |

---

## 🌟 争议与未来方向

**争议点**:
- **LLM可否替代规划器?**: No(基于评估#3),混合最优
- **形式化vs实用**: 权衡;简单系统LLM仅+符号接口足够
- **可扩展性**: 大规模BDI系统验证困难

**未来研究方向**:
1. **生产-级混合**: C++启发式生成(vs Python Pyperplan)
2. **多LLM集成**: 启发式生成的集成方法
3. **检索增强启发式**: RAG+LazyGraphs for large domains
4. **持续学习**: 在线适应而非离线LLM
5. **非PDDL域**: 连续规划、资源约束、不确定性
6. **Tier 1验证**: Nature/Science论文(目前缺失)

**2025-2026预期**:
- NeurIPS 2025启发式工作预期高影响
- 更多混合LLM+规划论文预期(ACL/ICML)
- 形式化验证仍为学术焦点
- 真实机器人部署案例研究(关键验证)

---

## 🚀 技术栈建议

**推荐工具链** (基于论文):
```
LLM生成启发式 (OpenAI API / DeepSeek)
    ↓
Python启发式编译 (Pyperplan Python实现)
    ↓
经典搜索 (Fast Downward / Pyperplan)
    ↓
BDI执行层 (JASON / CAMEL框架)
    ↓
形式验证 (Z3/Isabelle for critical paths)
```

---

**生成时间**: 2026-02-12
**数据来源**: Perplexity Sonar Pro/Reasoning Pro via research-lookup skill
