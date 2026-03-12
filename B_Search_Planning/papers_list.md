# Category B: Search & Planning - 论文清单

> **更新时间**: 2026-02-12
> **论文总数**: 12篇
> **重点**: MCTS, Beam Search, FLARE, Hierarchical Planning

---

## B1. Monte Carlo Tree Search (MCTS) for LLM Planning

### 1. ⭐ MCTS for Table-Based Question Answering (SemEval 2025)
**来源**: ACL Anthology SemEval 2025
**链接**: https://aclanthology.org/2025.semeval-1.256/
**类型**: 神经符号方法

**关键贡献**:
- 将LLM解码建模为Markov Decision Process
- 使用MCTS作为代码生成的前瞻规划算法
- 在表格QA任务上实现**2.38×准确率提升**

**核心方法**:
- 翻译自然语言查询为可执行Python代码
- 使用合成测试和真实数据集作为奖励信号
- 探索多条代码生成路径并迭代优化

---

### 2. ⭐ LGMCTS: Language-Guided Monte Carlo Tree Search for Robot Planning
**发表**: IROS 2024
**PDF**: http://rl.cs.rutgers.edu/publications/HaonanIROS2024C.pdf
**应用**: 语言引导机器人任务与运动规划

**关键贡献**:
- 结合LLM与MCTS实现语义物体重排
- 在ELGR基准(1,600+语言查询)上验证
- 相比Code as Policies和Progprompt显著提升可行性和语义一致性

**核心方法**:
- 使用LLM解析自然语言为空间分布规范
- MCTS高效探索生成可执行TAMP解决方案
- 结合语言理解与动作规划

---

### 3. ⭐ CodePilot: Automated Program Repair with MCTS
**arXiv**: https://www.arxiv.org/pdf/2602.00129
**模型**: Qwen3 + MCTS
**应用**: GitHub issue自动解决

**关键贡献**:
- 将补丁生成建模为决策树搜索
- 利用执行反馈指导模型生成有效解决方案
- 集成层级错误定位和置信度校准

**核心方法**:
- 每个节点代表部分补丁状态
- 探索多样化解决方案轨迹
- 测试通过或达到最大迭代时终止

---

### 4. ⭐ MCTS-AHD: Automatic Heuristic Design with MCTS
**发表**: ICML 2025
**链接**: https://icml.cc/virtual/2025/poster/45984
**应用**: 启发式优化

**关键贡献**:
- 将LLM生成的启发式组织为树结构(而非固定种群)
- 更好发展临时表现不佳的启发式
- 避免局部最优收敛

**核心任务**:
- 路线规划
- 任务分配
- 复杂优化任务

---

### 5. ⭐ GIF-MCTS: Generate, Improve and Fix with MCTS
**发表**: NeurIPS 2024
**OpenReview**: https://openreview.net/forum?id=9SpWvX9ykp&noteId=kH2xomkeeu
**会议页面**: https://neurips.cc/virtual/2024/poster/96309

**关键贡献**:
- 全面的代码生成策略解决复杂程序合成
- 引入Code World Models Benchmark (CWMB): 18个RL环境
- 使用单元测试和环境轨迹反馈进行自我调试

**核心挑战**:
- 理解复杂指令
- 生成精确的非平凡逻辑代码
- 使用反馈调试长程序

---

### 6. Awesome MCTS Papers (资源汇总)
**GitHub**: https://github.com/benedekrozemberczki/awesome-monte-carlo-tree-search-papers
**类型**: 论文汇总资源

---

## B2. Beam Search & Best-First Search

### 7. ⭐ Best-First Beam Search
**发表**: TACL 2020
**DOI**: https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00346/96473/Best-First-Beam-Search
**ACL**: https://aclanthology.org/2020.tacl-1.51/
**arXiv**: https://arxiv.org/abs/2007.03909

**关键贡献**:
- 提出内存减少的beam search变体
- A*风格优先级排序的agenda-based算法
- 实践中实现**10×加速**,保持相同输出质量

**性能**:
- 神经机器翻译: ~30%加速
- Beam width 500: ~10×加速
- 证明某些优先级方案允许安全剪枝

**理论发现**:
- Beam search常**优于精确推理**(由于有益的搜索偏差)
- 假设单调评分函数(长度单调)
- 为非单调评分提供有效近似

---

### 8. Adaptive Beam Search Variants (2024-2026)
**来源**: Emergent Mind, Computational Creativity Conference
**链接**: https://www.emergentmind.com/topics/beam-search-techniques

**现代变体**:
- **Relative Threshold Pruning**: 基于分数比率的动态候选过滤
- **Bidirectional Beam Search**: 结合左右双向模型
- **Creative Beam Search**: 使用LLM判断步骤提升多样性
- **Adaptive Beam Search**: 位置感知对齐,贝叶斯方法消除固定先验

**改进**:
- 速度、准确率和响应多样性提升
- 跨多个基准验证

---

## B3. FLARE (Lookahead Retrieval)

### 9. FLARE相关研究 (待补充)
**搜索结果说明**:
- 当前搜索结果未包含FLARE原论文
- 需要额外定向搜索"FLARE lookahead retrieval augmented generation"
- 建议搜索关键词: "Forward-Looking Active Retrieval" + "LLM"

**FLARE核心概念**(基于已知):
- Forward-Looking Active Retrieval augmented generation
- 前瞻式检索增强生成
- 动态检索机制结合生成

---

## B4. Hierarchical Planning

### 10. ⭐ HiPlan: Adaptive Global-Local Guidance
**arXiv**: https://arxiv.org/abs/2508.19076
**类型**: 层级规划框架

**关键贡献**:
- 自适应全局-局部指导提升LLM智能体决策能力
- 里程碑库构建(offline) + 动态适应(online)
- 显著优于强基线

**两阶段设计**:
- **Offline阶段**: 从专家演示构建里程碑库
- **Execution阶段**: 动态适应轨迹片段生成step-wise提示

**核心创新**:
- Milestone action guides (宏观方向)
- Step-wise hints (详细动作)
- 语义检索类似任务和里程碑

---

### 11. ⭐ H-AIM: Hierarchical Multi-Robot Planning
**arXiv**: https://arxiv.org/html/2601.11063v1
**类型**: 多机器人系统

**关键贡献**:
- 三阶段级联架构: LLM + PDDL + Behavior Trees
- 端到端闭环: 从高层指令解析到低层执行
- 宏任务并行 + 微动作鲁棒性

**三阶段架构**:
1. **PDDL File Generator (PFG)**: LLM解析自然语言生成PDDL
2. **Hybrid Planner (HP)**: LLM语义推理 + 经典规划器搜索
3. **Behavior Tree Compiler (BTC)**: 编译为行为树实现反应式控制

**多机器人协调**:
- 自动同步节点插入
- 共享黑板机制
- 异构机器人团队协作

---

### 12. ⭐ HLA: Hierarchical Language Agents
**来源**: ACM Digital Library
**DOI**: https://dl.acm.org/doi/10.5555/3635637.3662979
**应用**: 人机协作

**关键贡献**:
- 强推理能力与实时执行能力平衡
- 人机协调场景动态响应
- 交互式性能与复杂规划结合

---

## 📊 论文分布统计

| 子类别 | 论文数 | 代表会议/期刊 |
|--------|--------|---------------|
| MCTS应用 | 6 | NeurIPS, ICML, IROS, SemEval |
| Beam Search | 2 | TACL 2020 |
| FLARE | 1 | (待补充) |
| Hierarchical Planning | 3 | arXiv 2024-2025 |

---

## 🔍 重点阅读建议

**MCTS基础与应用(必读)**:
1. LGMCTS (IROS 2024) - 机器人规划
2. GIF-MCTS (NeurIPS 2024) - 代码生成
3. MCTS-AHD (ICML 2025) - 启发式优化

**Beam Search优化**:
4. Best-First Beam Search (TACL 2020) - 算法优化基础
5. Adaptive variants (2024-2026) - 最新变体

**Hierarchical Planning(前沿)**:
6. HiPlan - 里程碑库方法
7. H-AIM - 多机器人协作
8. HLA - 人机协调

---

## 📥 下载链接汇总

**已验证PDF/arXiv链接**:
- LGMCTS: http://rl.cs.rutgers.edu/publications/HaonanIROS2024C.pdf
- CodePilot: https://www.arxiv.org/pdf/2602.00129
- Best-First Beam Search: https://arxiv.org/abs/2007.03909
- HiPlan: https://arxiv.org/abs/2508.19076
- H-AIM: https://arxiv.org/html/2601.11063v1

**会议页面**:
- GIF-MCTS (NeurIPS 2024): https://neurips.cc/virtual/2024/poster/96309
- MCTS-AHD (ICML 2025): https://icml.cc/virtual/2025/poster/45984
- SemEval MCTS: https://aclanthology.org/2025.semeval-1.256/

**OpenReview**:
- GIF-MCTS: https://openreview.net/forum?id=9SpWvX9ykp&noteId=kH2xomkeeu

**资源汇总**:
- Awesome MCTS Papers: https://github.com/benedekrozemberczki/awesome-monte-carlo-tree-search-papers

---

## ⚠️ 待补充方向

1. **FLARE原论文**: Forward-Looking Active Retrieval Augmented Generation
2. **RAP (Reasoning via Planning)**: 需要单独搜索
3. **LATS (Language Agent Tree Search)**: 需要单独搜索
4. **ReST-MCTS**: Reinforced Self-Training with MCTS

建议后续搜索查询:
- "RAP reasoning via planning LLM"
- "LATS language agent tree search"
- "ReST-MCTS reinforced self-training"
- "FLARE active retrieval generation"

---

**生成时间**: 2026-02-12
**数据来源**: Perplexity Sonar Pro/Reasoning Pro via research-lookup skill
