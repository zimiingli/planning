# Category E: Value-Guided Methods - 论文清单

> **更新时间**: 2026-02-12
> **论文总数**: 8篇
> **重点**: Process Reward Models, Q-Value Methods, Offline RL, RLHF对齐

---

## E1. 过程奖励模型 (PRM) 和步级评估

### 1. ⭐ THINKPRM: Process Reward Models That Think (ICLR 2025)
**发表**: ICLR 2025 投稿(Tier 2)
**引用数**: 50+ (Emerging)
**OpenReview**: https://openreview.net/forum?id=V727xqBYIW

**关键贡献**:
- **生成式PRM**: 通过明确CoT痕迹验证步级推理
- **降低监督成本**: 相比ORMs减少密集步级标签需求
- **推理时缩放友好**: 与智能体Q-值集成用于累积步级评估

**核心创新**:
- 生成**验证基础**(而非仅分数)
- 步级口头化奖励
- 优于结果奖励模型(ORM)的推理基准

**方法特点**:
- 避免奖励黑客(ORM通病)
- 步级监管更有效
- 与验证器框架兼容

**限制性**:
- 痕迹生成开销
- 性能仍依赖训练数据质量

---

### 2. ⭐ RewardBench: Evaluating Reward Models (2024)
**发表**: 标准化基准(Tier 2影响力)
**引用数**: 100+ (Standard Benchmark)

**关键贡献**:
- **标准化RM评估**: ORM/PRM跨基准
- **文档化超参数**: SFT策略初始化、学习率等
- **性能差距定量化**: DPO vs RLHF对标

**核心发现**:
- DPO vs RLHF性能差距显著(对推理任务)
- 初始化策略影响重大
- PRM与ORM权衡(准确性vs解释性)

**研究价值**:
- 建立评估标准
- 方法间可比性
- 推动字段标准化

---

## E2. Q-值模型和价值评估

### 3. ⭐ Bayesian Reward Models for LLM Alignment (ICLR 2026)
**发表**: ICLR 2026 (Tier 2)
**引用数**: 30+ (Emerging)
**链接**: https://iclr.cc/virtual/2024/23797

**关键贡献**:
- **不确定性感知**: Laplace-LoRA估计RM后验
- **OOD鲁棒性**: 信号训练分布外的不确定性
- **过优化缓解**: 改进Best-of-N采样中的奖励黑客

**核心方法**:
- Laplace近似RM后验
- 频率主义RM超越
- 最好的N采样改进

**应用**:
- PRM/ORM差异缓解
- 智能体提示中的奖励不确定性
- 智能体Q-值评估

**限制性**:
- 计算密集
- 需要特殊训练流程

---

### 4. ⭐ GRPO in Deep Reasoning Verification (2025)
**应用**: DeepSeek-R1风格管道
**引用数**: 200+ (通过模型发布)

**关键贡献**:
- **消除RM/评论家**: 使用可验证奖励的步级DPO(组相对策略优化)
- **格式-感知奖励**: 如<think><answer>标签
- **CoT验证**: 链推理验证而非独立RM

**性能特点**:
- 简化RLHF管道
- 避免RM幻觉
- 与推理令牌兼容

**发现的偏差**:
- 长度/难度偏差(冗长错误倾向)
- <think><answer>标签调整提升智能体性能

**限制性**:
- 依赖可验证奖励存在(不总是可用)
- 长度偏见影响某些任务

---

## E3. 主动奖励建模

### 5. ⭐ Active Reward Modeling: Adaptive Preference Labeling (ICML 2025)
**作者**: Yunyi Shen, Hao Sun, Jean-Francois Ton (对齐实验室资深作者)
**发表**: ICML 2025 (Tier 2)
**引用数**: 20+ (Emerging)
**OpenReview**: https://openreview.net/forum?id=GSyX4amBFR

**关键贡献**:
- **Fisher信息选择**: 选择信息提示对(平衡探索和中等奖励差)
- **标注效率提升**: 减少50%标注成本
- **步级DPO适用**: 用于智能体训练的步级数据

**核心方法**:
- 最后层Fisher用于主动学习
- 应用于步级数据PRM训练
- RLHF/DPO管道增强

**性能**:
- 50%标注成本降低
- 保持竞争精度

**限制性**:
- 假设初始RM可用
- 计算开销(Fisher计算)

---

## E4. 离线强化学习方法

### 6. ⭐ Conservative Q-Learning (CQL) (NeurIPS 2020)
**作者**: Aviral Kumar 等 (UC Berkeley/Google Brain)
**发表**: NeurIPS 2020 (Tier 2, Landmark)
**引用数**: 1000+ (Foundation)

**关键贡献**:
- **保守主义Q-函数**: 惩罚未见动作
- **分布转移解决**: KL散度正则化
- **目标条件规划**: 从目标状态向后传播Q-值

**核心创新**:
- CQL惩罚项: Q(s,a)学习加KL正则化
- 子轨迹缝合(Hindsight relabeling)
- 安全离线RL使能

**性能**:
- D4RL基准SOTA
- 运动和操纵任务领先
- 超越BEAR、AWR等先前方法

**限制性**:
- 数据集质量敏感
- 稀疏奖励中长期规划困难
- 超参数敏感

---

### 7. ⭐ HsO-VP: Hierarchical Skills for Autonomous Driving (arXiv 2023)
**发表**: arXiv 2023 (Tier 2等价)
**引用数**: 50+ (Emerging)

**关键贡献**:
- **分层技能VAE**: 双分支(离散选项+连续变体)
- **长地平线规划**: 处理稀疏延迟奖励
- **可解释子目标**: 如"向左变道"

**核心方法**:
- 离线RL于技能(CQL/IQL)
- VAE缓解后验崩溃
- 高级策略而非低级行为

**性能** (CARLA模拟器):
- +4-6%驾驶分数 vs IRIS/OPAL
- 碰撞率和奖励改进
- 超越行为克隆

**应用**:
- 自主驾驶(安全关键)
- 长地平线目标导向任务

---

### 8. ⭐ CUORL: Curriculum Offline RL (NeurIPS 2022)
**发表**: NeurIPS 2022 (Tier 2)
**引用数**: 50+ (Influential)
**ACM DL**: https://dl.acm.org/doi/10.5555/3545946.3598767

**关键贡献**:
- **数据课程**: 按政策相似性序列化样本选择
- **噪声过滤**: 避免糟糕政策污染
- **灵活规划**: 跨初始条件的值传播

**核心创新**:
- 选择可能由当前策略生成的样本
- 扩展D4RL SOTA
- 零奖励数据转移

**性能**:
- D4RL运动/操纵SOTA
- 与CQL配合时最优
- 目标导向任务泛化

**限制性**:
- 假设政策进度对齐
- 多模态目标限制

---

## E5. 基础RLHF框架

### 9. ⭐ RLHF Pipeline Foundations (2020)
**发表**: 标准RLHF工作流程
**论文**: Fine-Tuning Language Models from Human Preferences

**核心组件**:
1. **SFT**: 监督微调
2. **RM训练**: 偏好排名(多个响应/提示)
3. **PPO优化**: 政策、RM、评论家(Q-值)、参考模型

**方法特点**:
- 明确价值估计(评论家)
- KL惩罚减少政策漂移
- 人类值编码

**影响**:
- RLHF标准范例
- ChatGPT/GPT-4基础
- 比DPO更复杂但更有效

---

## 📊 论文分布统计

| 方法 | 发表年 | 会议 | 引用数 | 关键焦点 |
|------|--------|------|--------|----------|
| THINKPRM | 2025 | ICLR | 50+ | 生成PRM |
| RewardBench | 2024 | Benchmark | 100+ | RM评估 |
| Bayesian RM | 2026 | ICLR | 30+ | 不确定性 |
| GRPO | 2025 | arXiv | 200+ | 可验证奖励 |
| Active RM | 2025 | ICML | 20+ | 标注效率 |
| CQL | 2020 | NeurIPS | 1000+ | 保守Q-学习 |
| HsO-VP | 2023 | arXiv | 50+ | 分层驾驶 |
| CUORL | 2022 | NeurIPS | 50+ | 课程离线RL |

---

## 🔍 重点阅读建议

**必读(Foundational)**:
1. RLHF Pipeline (2020) - 奖励模型基础
2. CQL (NeurIPS 2020) - 离线RL基础
3. RewardBench (2024) - RM评估标准

**前沿(2025-2026 Advances)**:
4. THINKPRM (ICLR 2025) - 生成式PRM
5. Bayesian RM (ICLR 2026) - 不确定性感知
6. GRPO (2025) - 可验证奖励集成

**应用(Practical Methods)**:
7. Active RM (ICML 2025) - 标注效率
8. HsO-VP (2023) - 分层自主智能体

---

## 📥 下载链接汇总

**已验证链接**:
- THINKPRM: https://openreview.net/forum?id=V727xqBYIW
- Bayesian RM: https://iclr.cc/virtual/2024/23797
- Active RM: https://openreview.net/forum?id=GSyX4amBFR
- CQL论文: 见标准RLHF流程文献
- HsO-VP: https://arxiv.org/html/2309.13614v1
- CUORL: https://dl.acm.org/doi/10.5555/3545946.3598767

**资源库**:
- Awesome Reward Models: https://github.com/JLZhong23/awesome-reward-models
- Microsoft Offline RL: https://www.microsoft.com/en-us/research/project/offlinerl/
- 离线RL综合: https://github.com/hanjuku-kaso/awesome-offline-rl

---

## 🎯 关键概念总结

| 概念 | 定义 | 应用 |
|------|------|------|
| **过程奖励模型(PRM)** | 步级评估推理(vs最终结果ORM) | THINKPRM, 推理验证 |
| **结果奖励模型(ORM)** | 单个标量评分最终输出 | 标准RLHF |
| **Q-值/评论家** | 估计累积奖励(价值函数) | PPO稳定性, CQL |
| **保守主义Q-学习** | 惩罚分布外动作的Q函数 | CQL, 离线RL |
| **分布转移** | 离线数据vs在线政策的差异 | CQL解决 |
| **课程学习** | 按难度递增序列化任务 | CUORL数据选择 |
| **可验证奖励** | 格式/结构检查而非学习评估 | GRPO实现 |

---

## 🔬 方法论对比:PRM vs ORM vs Q-值

| 维度 | PRM(THINKPRM) | ORM(标准) | Q-值(评论家) |
|------|---------------|----------|-------------|
| **评估粒度** | 步级 | 输出级 | 状态动作级 |
| **目标** | 推理验证 | 政策优化 | 价值估计 |
| **监督成本** | 中等(步级标签) | 低(只输出) | 无(隐含) |
| **奖励黑客抵抗** | 高(步级监督) | 低(易被骗) | 中(KL正则化) |
| **应用任务** | 推理密集 | 通用 | RLHF PPO |
| **解释性** | 高(基础) | 中(黑箱) | 低(抽象) |

---

## 🌟 争议与未来方向

**争议点**:
- **RLHF vs DPO**: RLHF因PRM/Q-值更强(推理);DPO更简单但性能差(Step-Level DPO缩小差距)
- **奖励黑客**: PRMs比ORMs更好,但Bayesian变体计算成本更高
- **数据质量**: CQL对数据集质量敏感;CUORL假设政策进度(限制多模态目标)

**未来研究方向**:
1. **自我对弈DPO**: 可扩展智能体对齐(ICLR 2025方向)
2. **混合ORM/PRM+Q-值**: 长地平线智能体的长期规划
3. **因果奖励**: 超越黑客/表面线索
4. **多任务RM**: 跨域泛化(vs任务特定)
5. **Tier 1验证**: 机器人期刊的真实世界部署(超越模拟)

---

**生成时间**: 2026-02-12
**数据来源**: Perplexity Sonar Pro/Reasoning Pro via research-lookup skill
