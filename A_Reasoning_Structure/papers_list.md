# Category A: Reasoning Structure Enhancement - 论文清单

> **更新时间**: 2026-02-12
> **论文总数**: 8篇
> **重点**: Chain-of-Thought, Tree of Thoughts, Graph-based推理结构

---

## A1. Chain of Thought (CoT)

### 1. ⭐ Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
**作者**: Wei et al.
**发表**: NeurIPS 2022 (NeurIPS 2023 proceedings)
**引用数**: 1,000+ (Landmark Paper)
**arXiv**: https://arxiv.org/abs/2201.11903
**PDF**: https://arxiv.org/pdf/2201.11903
**会议页面**: https://proceedings.neurips.cc/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract-Conference.html

**关键贡献**:
- 提出CoT prompting,通过生成中间推理步骤解锁LLM的推理能力
- 在GSM8K数学推理基准上超越finetuned GPT-3
- 证明CoT是大模型(540B+参数)的涌现能力
- 在算术、常识和符号推理任务上显著提升性能

**核心发现**:
- 顺序推理结构本身(而非仅知识激活)驱动改进
- 长度泛化能力增强
- 需要足够大的模型规模才能涌现CoT能力

---

### 2. ⭐ Improving Chain-of-Thought Reasoning in LLMs
**作者**: [待查询具体作者]
**发表**: NeurIPS 2024
**引用数**: 20+ (Recent)
**PDF**: https://proceedings.neurips.cc/paper_files/paper/2024/file/00d80722b756de0166523a87805dd00f-Paper-Conference.pdf
**会议页面**: https://neurips.cc/virtual/2024/poster/95956

**关键贡献**:
- 提出**Contrastive Preference Optimization (CPO)**训练方法
- 利用ToT树搜索中的非最优路径作为对比学习信号
- 在7个推理数据集上平均提升4.3%(最高9.7%)
- 无推理时开销增加,消除ToT的50×延迟惩罚

**核心方法**:
- 将中间思考分类为preferred/dispreferred
- 使用对比目标训练模型学习偏好
- 训练时监督,推理时高效

---

## A2. Tree of Thoughts (ToT)

### 3. ⭐ Tree of Thoughts: Deliberate Problem Solving with Large Language Models
**作者**: Yao et al.
**发表**: [NeurIPS 2023推测]
**引用数**: 500+ (Highly Influential)
**关键链接**: Referenced in multiple NeurIPS papers

**关键贡献**:
- 扩展单路径CoT为多路径树搜索
- 建模任务为状态空间树搜索问题
- 两个核心组件:思考生成器 + 状态评估器
- 显著提升推理质量

**局限性**:
- 推理时间开销大(50×+ 相比标准CoT)
- 需要LLM prompting实现生成和评估

---

## A3. Graph of Thoughts (GoT)

### 4. Graph of Thoughts (GoT) - Adaptive Reasoning Structures
**来源**: Search results on graph-based reasoning
**发表年份**: 2023-2024
**类型**: Emerging research direction

**关键特点**:
- 超越树结构,允许任意图结构推理路径
- 支持循环、合并、分支等复杂推理模式
- 更灵活的推理结构表达

**研究方向**:
- 自适应图结构生成
- 图推理路径的高效搜索
- 与外部知识图谱集成

---

## A4. 其他相关方法

### 5. Highlighted Chain-of-Thought (HoT)
**发表**: NeurIPS 2025
**引用数**: Emerging
**会议页面**: https://neurips.cc/virtual/2025/130525

**关键贡献**:
- 显式引用和高亮推理链
- 提高可追溯性,减少幻觉
- 增强推理过程的可解释性

---

### 6. Robustness Studies on CoT
**研究方向**: 噪声和无关推理链的鲁棒性
**发表年份**: 2024
**会议**: ICML 2024 Spotlight Posters
**链接**: https://icml.cc/virtual/2024/events/2024SpotlightPosters

**研究重点**:
- CoT在噪声条件下的性能退化
- 无关rationale对推理质量的影响
- 实际部署中的鲁棒性问题

---

## 📊 论文分布统计

| 子类别 | 论文数 | 代表会议 |
|--------|--------|----------|
| CoT基础 | 2 | NeurIPS 2022, 2024 |
| ToT扩展 | 1 | NeurIPS 2023 |
| GoT图结构 | 1 | 2023-2024 |
| 鲁棒性研究 | 2 | NeurIPS 2025, ICML 2024 |

---

## 🔍 重点阅读建议

**必读(Foundational)**:
1. Wei et al. CoT (NeurIPS 2022) - 奠基性工作
2. Yao et al. ToT - 多路径推理基础
3. CPO (NeurIPS 2024) - 高效训练方法

**前沿(Recent Advances)**:
4. HoT (NeurIPS 2025) - 可解释性增强
5. Robustness Studies - 实际部署考虑

---

## 📥 下载链接汇总

**已验证PDF链接**:
- CoT原论文: https://arxiv.org/pdf/2201.11903
- CPO (NeurIPS 2024): https://proceedings.neurips.cc/paper_files/paper/2024/file/00d80722b756de0166523a87805dd00f-Paper-Conference.pdf
- OpenReview (CoT): https://openreview.net/pdf?id=_VjQlMeSB_J

**会议页面**:
- NeurIPS 2022 CoT: https://proceedings.neurips.cc/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract-Conference.html
- NeurIPS 2024 CPO: https://neurips.cc/virtual/2024/poster/95956
- NeurIPS 2025 HoT: https://neurips.cc/virtual/2025/130525
- ICML 2024: https://icml.cc/virtual/2024/events/2024SpotlightPosters

---

**生成时间**: 2026-02-12
**数据来源**: Perplexity Sonar Reasoning Pro via research-lookup skill
