# Iteration 3 (FINAL): §4 Method + §6 Discussion + Appendix + Reviewer FAQ + Coherence

**日期**: 2026-03-22
**Focus**: §4 Method (principled design, simplicity argument), §6 Discussion (future directions, broader impact), Appendix (finalized structure), Reviewer FAQ, 全文 coherence check

---

## 1. Research Findings Summary

### Sub-agent 1: Simple Method as Strength — NeurIPS Best Paper Patterns

分析了多篇以 "simple method + strong finding" 获奖的论文:

| 论文 | Venue | 方法复杂度 | 贡献类型 | 简单性的呈现策略 |
|------|-------|-----------|----------|----------------|
| **"Are Emergent Abilities a Mirage?"** (Schaeffer et al.) | NeurIPS 2023 Outstanding | 极简 (change the metric) | Finding > Theory > Method | "我们不需要复杂方法, 因为问题在 metric 选择" |
| **"Not All Tokens Are What You Need"** (Lin et al.) | NeurIPS 2024 Best Paper Runner-Up | Token scoring + selective loss | Finding + Method | "selective loss 是 finding 的 natural consequence" |
| **ReAct** (Yao et al.) | ICLR 2023 | Prompting (few-shot) | Finding (reasoning+acting synergy) | "the synergy is the contribution, prompting is the implementation" |
| **Reflexion** (Shinn et al.) | NeurIPS 2023 | Verbal feedback + episodic memory | Finding (verbal RL works) | 34% absolute gain from simple verbal reflection |

**提取的方法呈现策略**:
1. **Design Principles paragraph**: 从 findings 推导出方法必须满足的 constraints — 让 method 看起来是 *derived*, not *proposed*
2. **Explicit simplicity argument**: "The complexity budget should go to discovery, not the gate" — 正面论证简单性是正确的工程决策
3. **Michael Black "Novelty in Science" 准则**: "The simplicity of an idea is often confused with a lack of novelty when exactly the opposite is often true." 可引用此准则来 preemptively address reviewer concerns

**NeurIPS 2025 Reviewer Guidelines 关键引文**: "Originality does not necessarily require introducing an entirely new method. A work that provides novel insights by evaluating existing methods is also equally valuable."

### Sub-agent 2: Discussion Section — Future Work & Broader Impact

**NeurIPS 2025 broader impact 要求**:
- 不再强制要求独立的 "Broader Impact" section, 但 checklist 仍然问 "Have you discussed potential negative societal impacts?"
- 可以放在 conclusion, discussion, 或 supplementary 中, 不超过 page limit
- 重点: positive + negative outcomes, uncertainties, potential misuse

**Discussion 结构 best practices**:
1. Community-level insight (zoom out from your method)
2. Honest limitations with mitigation strategies
3. Compelling future directions (concrete, feasible, independently interesting)
4. Broader impact (when applicable)

**Future Directions 设计原则**:
- 每个 future direction 应该是一个 concrete research question, 不是 generic "use bigger models"
- 应从 findings 自然衍生 — "our Two-Source Model suggests X, but Y remains open"
- 理想的 future direction 读者看了会想 "I want to work on this"

### Sub-agent 3: Appendix Structure & NeurIPS Format

**NeurIPS 2025 submission format** (2026 尚未公布, 预计类似):
- Main text: **9 content pages** (excluding references, appendix, checklist)
- No page limit for technical appendices
- Appendices in same PDF, after references
- Supplementary material (code, data) as separate ZIP, max 100MB
- NeurIPS paper checklist required after appendix

**Top paper appendix 组织模式**:
- **A**: Extended related work / method comparison tables
- **B**: Experimental details (environments, hyperparameters, compute)
- **C**: Proofs (complete versions of main-text proof sketches)
- **D**: Theory details (derivations, additional analysis)
- **E**: Additional experiments (sensitivity, ablations, statistical tests)

**Best practice**: Appendix should make the paper self-contained for reproducibility; main text must be self-contained for understanding. Reviewers read appendix at their discretion.

### Sub-agent 4: Preemptive Reviewer Defense

**常见 rejection patterns (finding papers with simple methods)**:

| 批评 | 频率 | 防御策略 |
|------|------|---------|
| "Method is just X" (logistic regression) | Very high | Reframe: contribution is finding + theory, method is consequence |
| "Limited to specific environments" | High | Show principled coverage of environment types |
| "Single backbone" | High | Distinguish env-level finding from model-level implementation |
| "Simplified theoretical model" | Medium | Defend explanatory + prescriptive value |
| "Performance on specific env (FEVER)" | Medium | Reframe as honest limitation that validates theory |
| "No neural gate comparison" | Medium | Show MLP wrong-direction is worse |
| "Exploration cost" | Low | Quantify: 8× cheaper than Phase 1 baselines |

**Rebuttal 策略 from "How We Write Rebuttals" (Devi Parikh et al.)**:
1. Clarify → reframe → add results → acknowledge edge cases
2. Prioritize: address common concerns first
3. Always reference specific paper sections

**Michael Black 准则 (directly applicable)**:
- "Replacing a complex algorithm with a simple one provides insight."
- "The novelty must be evaluated before the idea existed."
- "The inventive insight is to realize that a small change could have a big effect."

---

## 2. Changes Made to VOC_PAPER_WRITING_GUIDE.md

### 2.1 §4 Method — 三项重大改进

**改进 A: 新增 "Design Principles" paragraph**
- 三条 design principles, 每条从 §3 的 specific finding/proposition 推导
- Principle 1 (Explore before commit) ← Obs.1 (env-dependent semantics)
- Principle 2 (Discover direction) ← Prop.1 (necessity)
- Principle 3 (Multi-signal, sparse) ← Obs.2-3 (signal replacement + poverty)
- 让 reviewer 看到 method 是 *derived from analysis*, not ad hoc

**改进 B: 新增 "Why the method is intentionally simple" paragraph**
- Core argument: "bottleneck is direction discovery, not gate complexity"
- Supporting evidence: MLP wrong-direction (45.3% < base 49.0%)
- Engineering argument: "complexity budget should go to discovery, not the gate"
- Closing: "Training completes in <1s on CPU precisely because the gate need not compensate for missing direction information"

**改进 C: Step 1 增加 randomization rationale**
- 解释为什么用 random exploration 而非 targeted: "targeted exploration conditions on the signal whose semantics are unknown"

**改进 D: Step 3 增加 weight sign interpretation**
- 新增一句: "The sign of each w_i directly implements direction discovery: w_i > 0 means Type D, w_i < 0 means Type I, w_i = 0 means uninformative"
- 将 LASSO 的数学特性直接映射到 Two-Source Model 的语义

**改进 E: LLM paragraph 改为 "concrete example" format**
- 从 generic description 改为 WebShop 的具体例子
- 展示 LLM reasoning chain: observation → hypothesis → features
- 包含 LLM 的实际推理文本 (quoted)
- 解释为什么这个 case 不能用 universal features 解决

**改进 F: 新增 §4 设计笔记 (method presentation strategy)**
- 分析 NeurIPS best papers 的方法呈现模式
- 引用 Michael Black "Novelty in Science"
- 引用 NeurIPS 2025 reviewer guidelines on novelty
- 明确本论文的贡献层次: Finding > Theory > Method

### 2.2 §6 Discussion — 四项重大改进

**改进 A: 新增 §6 设计笔记**
- Discussion section best practices from NeurIPS best papers
- Limitations 策略: honest but not self-defeating
- Future directions 设计原则

**改进 B: 新增 "Future Directions" subsection (3 paragraphs)**
1. "Beyond two sources: a taxonomy of uncertainty types" — 从 Type I/D 扩展到更 fine-grained types (execution, compositional, temporal uncertainty)
2. "Adaptive exploration for step-0 critical environments" — 从 FEVER 限制引出 curriculum-based exploration + meta-learning warm-start
3. "Signal semantics as a foundation for multi-agent coordination" — 扩展到 multi-agent 设置

**改进 C: Limitations 重写为 numbered list with mitigations**
- 每个 limitation 附带 "why it doesn't undermine the core contribution" 或 "concrete path to address"
- (1) Single backbone → env-level vs model-level distinction
- (2) Linear model → explanatory + prescriptive value defense
- (3) p_I estimation → EAAG sidesteps via end-to-end learning
- (4) Exploration cost → amortized, one-time per environment

**改进 D: 新增 "Broader Impact" subsection**
- Positive: computational efficiency, reduced energy/cost
- Prescriptive: helps avoid deploying harmful fixed-direction methods
- Negative: none beyond LLM agents themselves

**改进 E: FEVER exploration bias paragraph 增加 theory connection**
- 新增: "this failure mode is itself predicted by the Two-Source Model: FEVER is the most extreme Type I environment"

### 2.3 §7 Conclusion — 改进

- 扩展为完整的 findings-theory-method-results arc
- 保留 signature closing line
- Capitalized "Two-Source" for consistency

### 2.4 Appendix — 完全重写为详细内容大纲

**Appendix A: Extended Related Work (1.5 页)**
- A.1: Complete landscape table (15+ methods)
- A.2: Per-method detailed analysis paragraphs
- A.3: Extended concurrent work statement with timeline

**Appendix B: Experimental Details (2 页)**
- B.1: Environment specifications (action space, state, reward, optimizer T)
- B.2: Hyperparameter configuration (EAAG + all baselines)
- B.3: Appendix environment results (APPS Interview, CRUXEval)
- B.4: Feature selection details (LASSO coefficients + LLM prompts)
- B.5: Computational cost breakdown table

**Appendix C: Proofs (1 页)**
- C.1: Full proof of Proposition 1 (not sketch) with Lemma + 2 cases
- C.2: Wrong-direction damage quantification (full data + correlation)
- C.3: VOC non-negativity scope (Russell & Wefald → evaluator-executor identity)

**Appendix D: Two-Source Model Details (1 页)**
- D.1: Full derivation (state assignment → conditional models → marginal ρ → reversal)
- D.2: Environment mapping on p_I axis (1D figure)
- D.3: Prediction verification full data (P1, P2, P3 complete tables)

**Appendix E: Additional Analyses (0.5 页)**
- E.1: Hyperparameter sensitivity (N_explore, τ, LASSO α)
- E.2: Trigger rate adaptation analysis (full table)
- E.3: Statistical significance (bootstrap CIs, permutation tests, Holm-Bonferroni)

### 2.5 新增 Reviewer FAQ (8 questions + prepared responses)

| Q# | 预期批评 | 核心防御策略 |
|----|---------|------------|
| Q1 | "Method is just logistic regression" | Contribution is finding + theory; simplicity is feature not bug |
| Q2 | "Single backbone (Qwen3-4B)" | Finding is env-level, not model-level |
| Q3 | "Two-Source Model too simplified" | Explanatory + prescriptive, not predictive of exact ρ |
| Q4 | "Limited environments" | 8 envs cover 6 task categories + full Two-Source spectrum |
| Q5 | "FEVER performance (49.8%)" | Honest limitation that validates the theory |
| Q6 | "Pareto-dominance claim" | Clarify definition + 34W/2L record |
| Q7 | "Why not neural network gate?" | MLP wrong-direction is worse; AUC hierarchy shows diminishing returns |
| Q8 | "Exploration cost (50 episodes)" | 8× cheaper than Phase 1 baselines; amortized |

每个 Q 包含: response template, paper section references, reframe strategy.

### 2.6 新增 Coherence Checklist

- **ONE STORY** checklist (9 items): Abstract → Conclusion arc consistency
- **NUMBER CONSISTENCY** (13 items): all ρ values, pp values, SR numbers
- **TERMINOLOGY CONSISTENCY** (8 items): direction reversal, Two-Source Model, Type I/D, etc.
- **NeurIPS FORMAT COMPLIANCE** (7 items): page count, trim candidates, template

### 2.7 Page Count Estimate Update

- Previous: ~9.75p → now: ~10.25p (additions in §4 and §6)
- Trim plan: 7 specific candidates with estimated savings, totaling ~1.25p

---

## 3. Structural Completeness Map (Final State)

```
§1 Intro (1.5p)
  ├─ P1: Background + mechanisms          ✅ (iter_01)
  ├─ P2: Hidden assumption                ✅ (original)
  ├─ P3: Assumption is wrong 🔥          ✅ (iter_01)
  ├─ P4: Why + Simpson's paradox          ✅ (original)
  ├─ P5: Method + results                 ✅ (original)
  └─ P6: Contributions                    ✅ (original)

§2 Related Work (0.75p)
  ├─ §2.1: Signal/Vote/RL methods         ✅ (original + iter_01 citations)
  ├─ §2.2: Orthogonal work                ✅ (iter_02: Snell + Tao + Heo)
  └─ Concurrent work statement            ✅ (original)

§3 Signal-Utility Landscape (2.0p)         — 论文心脏
  ├─ §3.1: 4 Observations + tables        ✅ (original + iter_02 transition)
  ├─ §3.2: Two-Source Model               ✅ (iter_02: intuition + mapping + proof)
  │    ├─ Intuition paragraph             ✅ (iter_02)
  │    ├─ Model + equation                ✅ (original)
  │    ├─ Environment mapping table       ✅ (iter_02)
  │    ├─ Theoretical grounding           ✅ (iter_02: +4 grounding points)
  │    └─ Proposition + proof sketch      ✅ (iter_02: 2-case structure)
  └─ §3.3: Design Implications + table    ✅ (original + iter_02 transition)

§4 Method: EAAG (1.75p)                   ← iter_03 重点
  ├─ Design Principles paragraph          🆕 (iter_03)
  ├─ Why Simplicity paragraph             🆕 (iter_03)
  ├─ Overview                             ✅ (original)
  ├─ Step 1: Explore + rationale          ✅ (improved iter_03)
  ├─ Step 2: Reason                       ✅ (original)
  ├─ Step 3: Learn + sign interpretation  ✅ (improved iter_03)
  ├─ Online Adaptation                    ✅ (original)
  └─ LLM concrete example (WebShop)      🆕 (iter_03, replaces generic)

§5 Experiments (2.5p)
  ├─ §5.1: Setup + 3-axis framing        ✅ (iter_02)
  ├─ §5.2: Main Results + story narrative ✅ (iter_02)
  ├─ §5.3: Ablation + hierarchy           ✅ (iter_02)
  ├─ §5.4: Theory Verification (P→T→R→V)  ✅ (iter_02)
  └─ §5.5: Diagnostic environments        ✅ (original)

§6 Discussion (1.0p)                       ← iter_03 重点
  ├─ Insight for community                ✅ (original)
  ├─ FEVER exploration bias + theory      ✅ (improved iter_03)
  ├─ Future Directions                    🆕 (iter_03)
  │    ├─ Beyond two sources              🆕
  │    ├─ Adaptive exploration            🆕
  │    └─ Multi-agent coordination        🆕
  ├─ Limitations (numbered + mitigations) 🆕 (iter_03, replaces brief list)
  └─ Broader Impact                       🆕 (iter_03)

§7 Conclusion (0.25p)                      ← improved iter_03
  └─ Full arc + signature closing line    ✅ (improved iter_03)

Appendix A-E: Detailed outlines            🆕 (iter_03)
Reviewer FAQ (Q1-Q8)                       🆕 (iter_03)
Coherence Checklist                        🆕 (iter_03)
```

---

## 4. Quality Assessment (Final)

### What is now NeurIPS-ready:
- **§1-§3**: Full narrative arc from assumption → violation → theory (iter_01 + iter_02)
- **§3.2**: Follows Schaeffer/Snell pattern with intuition → model → mapping → proof → predictions (iter_02)
- **§4**: Method is now *derived* from findings, not presented as standalone contribution (iter_03)
- **§4 simplicity argument**: Explicitly addresses the "just logistic regression" concern before reviewers raise it (iter_03)
- **§5**: Story-first results with theory connections in every paragraph (iter_02)
- **§6**: Compelling future directions + honest-but-strong limitations (iter_03)
- **§7**: Memorable conclusion with signature closing line
- **Appendix**: Complete structure ready for content filling
- **Reviewer FAQ**: Preemptive defense for 8 likely reviewer concerns
- **All transitions**: Every §→§ has explicit bridge

### What needs attention during actual writing:
1. **Page count**: ~10.25p estimated, need ~1.25p trim (trim plan provided)
2. **FEVER exact numbers**: some numbers may need confirmation from experiments
3. **APPS Interview / CRUXEval full data**: appendix placeholder
4. **Figures**: fig_auc, fig_p1, fig_trigger, fig_method still ⏳
5. **Tab:main**: Full LaTeX table not yet written (only narrative)
6. **Statistical significance**: bootstrap CIs and p-values in Appendix E

### Contribution type classification:
- **Primary**: Empirical finding (direction reversal) + theoretical explanation (Two-Source Model)
- **Secondary**: Method (EAAG) as principled consequence of analysis
- **Supporting**: Necessity proof, 34W/2L evaluation, emergent adaptive behavior
- **NeurIPS category**: Bridge paper (connecting uncertainty theory to adaptive compute) + Critical analysis (challenging fixed-direction assumption)

---

## 5. Verified Sources

所有 research findings 来源:
- Michael Black "Novelty in Science": https://medium.com/@black_51980/novelty-in-science-8f1fd1a0a143
- NeurIPS 2025 Reviewer Guidelines: https://neurips.cc/Conferences/2025/ReviewerGuidelines
- NeurIPS 2025 Call for Papers: https://neurips.cc/Conferences/2025/CallForPapers
- NeurIPS 2025 Best Paper Awards: https://blog.neurips.cc/2025/11/26/announcing-the-neurips-2025-best-paper-awards/
- NeurIPS 2026 Dates: https://neurips.cc/Conferences/2026/Dates
- Devi Parikh "How We Write Rebuttals": https://deviparikh.medium.com/how-we-write-rebuttals-dc84742fece1
- "Are Emergent Abilities a Mirage?" (Schaeffer et al.): https://arxiv.org/abs/2304.15004
- "Not All Tokens Are What You Need" (Lin et al.): https://proceedings.neurips.cc/paper_files/paper/2024/hash/3322a9a72a1707de14badd5e552ff466-Abstract-Conference.html
- ReAct (Yao et al.): https://arxiv.org/abs/2210.03629
- Reflexion (Shinn et al.): https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html
- NeurIPS Paper Checklist: https://neurips.cc/public/guides/PaperChecklist
- NeurIPS 2025 FAQ for Authors: https://neurips.cc/Conferences/2025/PaperInformation/NeurIPS-FAQ
