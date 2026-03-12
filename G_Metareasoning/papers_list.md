# Category G: Rational Metareasoning & Value of Computation - 论文清单

> **更新时间**: 2026-02-27
> **论文总数**: 10篇
> **重点**: VOC理论、CMDP、Anytime Algorithms、LLM Metareasoning、Cost-Aware Inference
> **与本文关系**: Direction-Aware Gate 的 VOC negativity insight 扩展经典 metareasoning 理论；CMDP formalization + Lagrangian dual ascent 提供 principled cost-quality trade-off

---

## G1. Classical Metareasoning

### 1. ⭐⭐⭐ Russell & Wefald (1991): Do the Right Thing
**发表**: MIT Press, 1991
**标题**: "Do the Right Thing: Studies in Limited Rationality"
**作者**: Stuart J. Russell, Eric Wefald

**关键贡献**:
- **VOC (Value of Computation)** 理论基石
- 将"是否值得继续计算"形式化为 metalevel decision problem
- VOC ≥ 0 依赖 agent 可忽略不利计算结果（option to ignore）

**与本文关系**:
- 我们发现在 evaluator-executor identity 下，option to ignore 不可靠
- Aggregate VOC 可系统性为负（Wrong-Direction LR −34.5pp, MLP −51.2pp）
- Direction discovery 是确保 VOC 非负的 practical prerequisite

---

### 2. ⭐⭐ Horvitz (1989): Bounded Optimality
**发表**: AAAI Workshop on Uncertainty in AI, 1989
**标题**: "Reasoning about Beliefs and Actions under Computational Resource Constraints"
**作者**: Eric J. Horvitz

**关键贡献**:
- Bounded optimality 与 flexible computation 的早期形式化
- 计算资源约束下的推理框架

---

## G2. Constrained MDPs for Resource Allocation

### 3. ⭐⭐⭐ Altman (1999): CMDP
**发表**: Chapman and Hall/CRC, 1999
**标题**: "Constrained Markov Decision Processes"
**作者**: Eitan Altman

**关键贡献**:
- CMDP 经典教材
- Lagrangian relaxation 求解方法
- Slater condition 下收敛保证

**与本文关系**:
- 我们将 adaptive triggering 形式化为 CMDP
- Lagrangian dual ascent 自动学习 λ*
- HotpotQA λ* 严格递增验证理论

---

### 4. ⭐⭐ Gladin et al. (2023): CMDP Algorithm
**发表**: ICML 2023
**标题**: "Algorithm for Constrained Markov Decision Process"
**作者**: Egor Gladin et al.

**关键贡献**:
- CMDP 高效求解算法
- 理论收敛性分析

---

## G3. Anytime Algorithms

### 5. ⭐⭐ Zilberstein (1996): Anytime Algorithms
**发表**: AI Magazine, 17(4):73-83, 1996
**标题**: "Using Anytime Algorithms in Intelligent Systems"
**作者**: Shlomo Zilberstein

**关键贡献**:
- Anytime algorithms 综述
- 随时间递增质量的计算
- VOC 用于判断何时停止

---

## G4. LLM Metareasoning

### 6. ⭐⭐⭐ Nair et al. (2024): LLM Metareasoning
**发表**: arXiv, 2024
**arXiv**: https://arxiv.org/abs/2410.05563
**标题**: "Rational Metareasoning for Large Language Models"
**作者**: Nair et al.

**关键贡献**:
- LLM metareasoning 框架
- 用 VOC 分析 LLM 的 test-time compute allocation
- 引入独立 reward model 做 post-hoc evaluation，恢复 VOC ≥ 0

**与本文关系**:
- Nair et al. 通过独立 evaluator 恢复 VOC ≥ 0
- 我们的 direction discovery 是在**不引入独立 evaluator** 条件下的替代方案
- 两种方案各有 trade-off：独立 evaluator 需额外组件，direction discovery 需 probe data

---

### 7. 🆕 Meta-Reasoner (arXiv:2502.19918, 2025)
**发表**: arXiv, February 2025
**arXiv**: https://arxiv.org/abs/2502.19918
**标题**: "Meta-Reasoner: Multi-Strategy Reasoning Coordination"
**威胁等级**: 🟡 MEDIUM

**关键贡献**:
- 元推理器协调多种推理策略
- 根据问题特征选择最优推理路径

**与本文关系**:
- Meta-level strategy selection vs State-level optimizer triggering
- 交叉引用：同时属于 C8 (routing) 和 G4 (LLM metareasoning)

---

### 8. 🆕 Meta-R1 (arXiv:2508.17291, 2025)
**发表**: arXiv, August 2025
**arXiv**: https://arxiv.org/abs/2508.17291
**标题**: "Meta-R1: RL-Trained Meta-Reasoning Router"
**威胁等级**: 🟡 MEDIUM

**关键贡献**:
- RL 训练的 meta-reasoning router
- 学习何时使用何种推理策略

**与本文关系**:
- RL-based meta-reasoning vs Probe-based direction discovery

---

## G5. Cost-Aware Adaptive Inference

### 9. ⭐⭐ FrugalGPT (Chen et al., 2023)
**发表**: ICML Workshop on ES-FoMo, 2023
**标题**: "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance"
**作者**: Lingjiao Chen et al.

**关键贡献**:
- LLM cascade 中的 cost-aware adaptive 计算分配
- 用小模型先回答、大模型按需介入
- Model-level routing（粒度比 state-level 粗）

**与本文关系**:
- FrugalGPT 做 model-level cascade routing
- 我们做 state-level optimizer triggering（更细粒度）
- 共同点：cost-aware adaptive computation

---

### 10. ⭐⭐ SkipNet (Wang et al., ECCV 2018)
**发表**: ECCV 2018
**标题**: "SkipNet: Learning Dynamic Routing in Convolutional Networks"
**作者**: Xin Wang et al.

**关键贡献**:
- Dynamic layer skipping in neural networks
- RL 学路由策略
- Adaptive computation in neural network inference

**与本文关系**:
- SkipNet 做 layer-level routing
- 我们做 state-level optimizer triggering
- 共同点：adaptive computation via learned routing

---

## 📊 论文分布统计

| 子类别 | 论文数 | 时间跨度 | 与本文关系 |
|--------|--------|----------|-----------|
| G1 Classical Metareasoning | 2 | 1989-1991 | VOC 理论基石 |
| G2 CMDP | 2 | 1999-2023 | CMDP formalization |
| G3 Anytime | 1 | 1996 | 理论背景 |
| G4 LLM Metareasoning | 3 | 2024-2025 | 最直接理论对标 |
| G5 Cost-Aware | 2 | 2018-2023 | Routing 粒度对比 |

---

## 🔍 与 Direction-Aware Gate 的核心联系

1. **VOC Negativity Insight**: 经典 VOC ≥ 0 依赖 "option to ignore"，evaluator-executor identity 破坏此前提 → aggregate VOC 可为负
2. **CMDP Formalization**: Adaptive triggering 形式化为 CMDP，Lagrangian dual ascent 自动学 λ*
3. **Direction Discovery as VOC Prerequisite**: Direction discovery 确保 VOC 非负，无需引入独立 evaluator
4. **跨粒度对比**: FrugalGPT (model) → SkipNet (layer) → 本文 (state) — 不同粒度的 adaptive computation

---

**生成时间**: 2026-02-27
**数据来源**: 手动整理 + taxonomy 交叉引用
