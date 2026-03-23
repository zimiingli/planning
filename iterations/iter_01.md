# Iteration 1: Abstract + Introduction Improvement

**日期**: 2026-03-22
**Focus**: 添加 Abstract, 改进 §1 Introduction (P1, P3), 补全 baseline citations

---

## 1. Research Findings Summary

### Sub-agent 1: NeurIPS Best Paper Abstract 结构分析

分析了 3 篇 NeurIPS 2023-2024 获奖论文的 abstract 结构：

| 论文 | 奖项 | Abstract 模式 | 关键句法 |
|------|------|---------------|----------|
| **Not All Tokens Are What You Need** (Lin et al., NeurIPS 2024) | Best Paper Runner-Up | 2句背景→"Challenging this norm, we posit..."→方法(SLM)→结果(+30%/MATH) | 第3句直接亮发现，不做长铺垫 |
| **Are Emergent Abilities a Mirage?** (Schaeffer et al., NeurIPS 2023) | Outstanding Paper | 1句claim→"we present an alternative explanation"→3种验证→结论 | 颠覆假设型: 先精确描述 claim 再拆解 |
| **Visual Autoregressive Modeling** (Tian et al., NeurIPS 2024) | Best Paper | 1句新范式定义→"diverging from the standard"→量化结果(FID 18.65→1.73)→scaling law | 新范式型: 第1句就定义新方法 |

**提取的共同模式**:
1. Abstract 前 2-3 句必须包含核心发现/颠覆, 不超过 2 句纯背景
2. 用具体数字 (ρ, %, pp) 在 abstract 阶段就说服 reviewer
3. 结尾用 "emergent" / "scaling" / "Pareto" 等强结论词

### Sub-agent 2: NeurIPS Introduction 开头模式

从获奖论文中提取的 P1 (背景段) 设计模式:

- **"Not All Tokens" P1 策略**: "Previous methods have uniformly applied X" → 一句定义 status quo, 强调 "uniformly" (暗示盲区)
- **"Emergent Abilities" P1 策略**: "Recent work claims that..." → 先精确描述 community belief, 设好拆解靶点
- **"VAR" P1 策略**: "We present VAR..." → 跳过背景直接亮方法, 但这适合 pure method paper, 不适合 finding paper

**对我们 P1 的改进**:
- 原版 3 句平铺 → 改为 3 句递进: overhead → selective triggering → "每个方法在自己的环境里有效" (为 P2 的 "但跨环境不行" 做锚点)
- 增加了 mechanism 枚举 (vote entropy, calibrated confidence, token entropy, RL), 让 reviewer 看到我们覆盖了所有主流方向

### Sub-agent 3: Baseline Citations 补全

| 方法 | arXiv/Venue | 作者 | 核心机制 | 状态 |
|------|-------------|------|----------|:----:|
| **CATTS** | arXiv:2602.12276 | Lee, Erdogan, John, Krishnapillai, Mahoney, Keutzer, Gholami | Vote entropy + margin, web agents | verified |
| **SEAG** | arXiv:2501.05752, ACL 2025 | Lee, Park, Kim, Ok | Mean token confidence gating | verified |
| **CaTS** | arXiv:2503.00031 | Huang et al. | Platt-scaled confidence, Best-of-N early stopping | verified |
| **CoRefine** | arXiv:2602.08948 | Anonymous | Conv1D confidence controller, halt/re-examine | verified |
| **AdaptThink** | arXiv:2505.13417, EMNLP 2025 | Zhang, Lin, Hou, Feng, Li (THU-KEG) | RL think/no-think policy | verified |
| **Thinkless** | arXiv:2505.13379, NeurIPS 2025 | Fang, Ma, Wang (NUS) | DeGRPO hybrid reasoning | verified |
| **DiffAdapt** | arXiv:2510.19669 | Anonymous | U-shaped entropy, hidden-state probe | verified |
| **Think Just Enough** | arXiv:2510.08146 | Sharma, Chopra | Sequence-level entropy early stopping | verified |
| **ARPO** | arXiv:2507.19849, ICLR 2026 | Du et al. | Entropy-based adaptive rollout at tool-calls | verified |
| **s1** | arXiv:2501.19393, EMNLP 2025 | Muennighoff, Yang et al. | Budget forcing | verified |

### Sub-agent 4: 理论基础 — Simpson's Paradox & Uncertainty Decomposition

**Simpson's Paradox in ML**:
- KDD 2023: "Learning to Discover Various Simpson's Paradoxes" — ML-based auto-detection, 但仅处理 tabular data
- Pearl 2014: 经典理论框架已在关键引用中
- **Gap**: 尚无论文将 Simpson's paradox 应用于 LLM agent 的 signal-utility space → 我们是第一个

**Epistemic/Aleatoric Decomposition**:
- Charpentier et al. (arXiv:2206.01558): RL 中的 epistemic vs aleatoric 解耦, 定义了 4 个 desiderata
- Hullermeier & Waegeman (ML 2021): 已在关键引用中
- **我们的创新**: 将 epistemic/aleatoric distinction 适配到 meta-decision (何时调用 optimizer) 而非 policy learning 层面 → Type I (information poverty ≈ epistemic) vs Type D (decision difficulty ≈ aleatoric)

---

## 2. Changes Made to VOC_PAPER_WRITING_GUIDE.md

### 2.1 新增 Abstract (~250 words)
- 位置: Storyline 和 §1 Introduction 之间
- 结构: [背景2句] → [发现3句, 含3组 ρ 数据] → [理论2句: two-source model + necessity proof] → [方法2句: EAAG 三步] → [结果2句: 34W/2L + emergent adaptive behavior]
- 附带 "Abstract 设计笔记" 解释每句为何如此设计

### 2.2 改进 P1 (Introduction 背景段)
- 增加了 "P1 设计笔记" 分析 3 篇 best paper 的开头模式
- 文本调整: "A growing body of work proposes" → "A growing body of work addresses this inefficiency through" (更 active)
- 增加 mechanism 枚举行 (vote entropy, calibrated confidence, token-level entropy, RL)
- 将 "demonstrated effectiveness within their respective evaluation environments" 作为 P2 颠覆的锚点

### 2.3 改进 P3 (核心发现段)
- 增加了 "P3 设计笔记" 分析 finding-driven paper 的 3 层递进结构
- 新增 AUC 数据: "single-signal entropy achieves AUC≈0.53 (barely above chance) while multi-signal gates reach AUC≈0.85"
- 修正 wrong-direction 数据: 统一使用 38.8 pp (HotpotQA), 45.3% MLP vs 49.0% base
- 保留 signature insight: "When the direction is wrong, more precise calibration makes performance worse, not better."

### 2.4 补全 Baseline 引用
- 10 个 baseline 方法的完整 BibTeX (CATTS, SEAG, CaTS, CoRefine, AdaptThink, Thinkless, DiffAdapt, Think Just Enough, ARPO, s1)
- 新增理论参考: Charpentier et al. 2022 (epistemic/aleatoric in RL)
- 新增 NeurIPS best paper 参考: 4 篇获奖论文 BibTeX (供 abstract/intro 结构参考)
- 新增 KDD 2023 Simpson's paradox detection paper

---

## 3. Next Iteration Suggestions

1. **§2 Related Work**: 现在有了完整 baseline citations, 可以重构 Related Work 的叙事线 — 按 "signal-based → vote-based → RL-based → ours" 递进, 每类用一个代表性 citation
2. **§3.1 Observation Table**: 考虑增加 p-value 列, 强化统计严谨性
3. **§4 Method Figure**: EAAG pipeline 示意图 (fig_method) 仍为 ⏳ 状态
4. **P2 (隐含假设段)**: 可进一步 tighten — 当前列举了太多 mechanism, 考虑用一句话概括然后 footnote 详列
5. **Abstract 长度**: 当前约 260 words, 略长于理想的 250 words, 可能需要在提交前 trim

---

## 4. Verified Sources

所有 citation 均通过 WebSearch 验证, 具体来源:
- CATTS: https://arxiv.org/abs/2602.12276
- SEAG: https://arxiv.org/abs/2501.05752, https://aclanthology.org/2025.acl-long.29/
- CaTS: https://openreview.net/forum?id=jrSc4RJXy1, arXiv:2503.00031
- CoRefine: https://arxiv.org/abs/2602.08948
- AdaptThink: https://arxiv.org/abs/2505.13417, https://aclanthology.org/2025.emnlp-main.184/
- Thinkless: https://arxiv.org/abs/2505.13379, https://github.com/VainF/Thinkless (NeurIPS 2025 confirmed)
- DiffAdapt: https://arxiv.org/abs/2510.19669
- Think Just Enough: https://arxiv.org/abs/2510.08146
- ARPO: https://arxiv.org/abs/2507.19849, ICLR 2026 confirmed via OpenReview
- s1: https://arxiv.org/abs/2501.19393, https://aclanthology.org/2025.emnlp-main.1025/
- Charpentier et al.: https://arxiv.org/abs/2206.01558
- NeurIPS best paper list: https://blog.neurips.cc/2024/12/10/announcing-the-neurips-2024-best-paper-awards/
