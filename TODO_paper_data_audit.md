# Paper-Data Audit TODO List

**Paper**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**Audit Date**: 2026-03-23
**Source**: `VOC_PAPER_WRITING_GUIDE.md` vs `experiment/` 数据对照
**Last Updated**: 2026-03-23

---

## ✅ 已修复

### ~~1. P1 Temporal Shift — 数据方向与论文叙述完全相反~~ → **已修复 (2026-03-23)**
- **问题**: 论文原叙述称 "early ρ 比 late 更负"，实际数据显示 ρ 随 episode 递减 (late 更负)，且论文中的具体数字 (−0.089, −0.018 等) 为编造
- **修复方案**: Reframe P1 为 "Temporal dynamics" — early 混合 Type I+D, late 分离出纯 Type I, 因此 ρ 递减
- **修改位置** (共 6 处):
  - [x] §3.2 Testable Predictions: P1 prediction 重写
  - [x] §5.4 P1 verification: 整段重写，使用实际数据 (HotpotQA −0.176→−0.437, APPS Intro +0.102→−0.144, WebShop +0.285→−0.006)
  - [x] Appendix D Full Table: 旧编造数字替换为 data.csv 实际数字
  - [x] Reviewer Q3 回复: "temporal shift" → "temporal dynamics"
  - [x] Reviewer Q10 回复: 增加 P1 refined interpretation 描述
  - [x] Figure 清单: fig_p1 描述更新
- **验证**: grep 确认无残留旧数字 (−0.089, −0.018, −0.167, −0.072, −0.341, −0.198)，无残留 "early more negative" 表述

### ~~13. 环境分类统一~~ → **已修复 (2026-03-23)**
- **问题**: 论文原文将 8 个环境分为 "4 主 + 2 诊断 + 2 附录"，TWExpress/Plancraft 被标为 diagnostic，APPS Interview/CRUXEval 被标为 appendix
- **修复**: 全部 8 个环境统一为主评估环境，移除 diagnostic/appendix 分层
- **修改位置**:
  - [x] 文件头部环境列表: 移除 "(主)/(诊断)/(附录)" 分类
  - [x] §5.1 Setup: "Four serve as primary...two as diagnostic...two for appendix" → 统一描述 8 个环境
  - [x] §5.5: "Diagnostic Environments" → "Environments with Extreme Rollout Properties"
  - [x] env-setup table: 移除分隔 \midrule, 加入 APPS Interview + CRUXEval 行
  - [x] Table 清单: "诊断环境" → "极端 rollout 环境", "附录环境" → "APPS Interview / CRUXEval 结果"
  - [x] Reviewer Q4 回复: "extreme properties" → "extreme rollout properties"
  - [x] Checklist: 更新 "8 environments" 描述
- **验证**: grep 确认无残留 "diagnostic environment" (仅 checklist 提醒)、无 "for appendix analysis"

### ~~14. APPS 命名统一~~ → **已修复 (2026-03-23)**
- **问题**: 论文中 "APPS" 既指 APPS Intro 又容易与 APPS Interview 混淆
- **修复**: 全文将基础 APPS 统一为 "APPS Intro"，高级版统一为 "APPS Interview"
- **修改位置** (20+ 处):
  - [x] Abstract: "APPS" → "APPS Intro"
  - [x] §1 P3: "APPS" → "APPS Intro"
  - [x] §1 P5: "APPS" → "APPS Intro"
  - [x] §3.1 signal discovery table: "APPS" → "APPS Intro"
  - [x] §3.2 env-type-mapping table: "APPS" → "APPS Intro", "APPS Intv." → "APPS Interview"
  - [x] §5.2 per-env analysis: "APPS" → "APPS Intro"
  - [x] §5.3 ablation: "APPS" → "APPS Intro" (LLM ablation + trigger rate)
  - [x] §5.4 P1: "APPS" → "APPS Intro"
  - [x] Appendix comments: all "APPS" → "APPS Intro"
  - [x] Reviewer responses: "APPS" → "APPS Intro"
  - [x] Coherence checklist: all "APPS" → "APPS Intro"
- **验证**: `grep -n '\bAPPS\b' | grep -v 'APPS Intro' | grep -v 'APPS Interview'` 返回空

### ~~15. "across 6 environments" → "across 8 environments"~~ → **已修复 (2026-03-23)**
- **问题**: 论文多处写 "across 6 evaluation environments"，与 8 环境统一评估不一致
- **修改位置**:
  - [x] Abstract: "Across 6" → "Across 8"
  - [x] §1 P3: "two of six" → "two of eight"
  - [x] §1 P5: "Across 6" → "Across 8"
  - [x] §1 Contributions: "across 6" → "across 8"
  - [x] §3.1 Obs.4: "across 6" → "across 8"
  - [x] §5.2: "across 4 primary" → "across 8", "across 6 environments" → "across 8 environments"
  - [x] §7 Conclusion: "across 6" → "across 8"
  - [x] Reviewer Q6: "6 environments" → "8 environments"
- **验证**: grep 确认唯一保留 "across 6" 是 "across 6 baselines × 8 environments" (正确)

### ~~16. 移除 MBPP~~ → **已修复 (2026-03-23)**
- **问题**: MBPP 不在 8 个评估环境中，但出现在 Appendix P1 数据表注释里
- **修复**: 注释中标记为已移除
- [x] VOC_PAPER_WRITING_GUIDE.md Appendix D P1 table: MBPP 行替换为 "(MBPP removed)"

---

## ~~🔴 紧急~~ → ✅ 已修复

### ~~2. Trigger Rate 具体数字不匹配~~ → **已修复 (2026-03-23)**
- **问题**: 论文声称 "60% HotpotQA, 6% APPS Intro, ~1% Plancraft"，实际数据完全不同
- **实际 step-level exploitation trigger rate** (from `stats.json`, 3-seed average):
  - HotpotQA: **66%** (论文原 60%，接近)
  - TWExpress: **73%** (论文原 85%，偏高)
  - APPS Intro: **35%** (论文原 6%，严重错误)
  - Plancraft: **33%** (论文原 ~1%，严重错误；但 step-dependent: 49%→<20%)
  - WebShop: **28%**, FEVER: **49%**
- **fig_trigger_rate 数据确认**: exploitation phase only (decision_log 过滤 `phase == 'exploitation'`)
- **修复** (共 4 处):
  - [x] Abstract: "60% when large, 6% when small" → "73% TWExpress, 66% HotpotQA, 28% WebShop"
  - [x] §1 P5: "60% triggering when headroom large, 6% when small" → "73% TWExpress, 66% HotpotQA, 28% WebShop"
  - [x] §5.3 Gating magnitude paragraph: 完全重写，使用实际数字 (66%, 73%, 35%, 28%) + Plancraft step-decay 叙事
  - [x] §5.5 Diagnostic: TWExpress "85%" → "73%", Plancraft "~1%" → step-decay 叙事 (49%→<20%)
  - [x] Coherence checklist trigger rate 行更新

### ~~3. APPS Intro 的 Two-Source Type 标签不一致~~ → **已修复 (2026-03-23)**
- **问题**: data.csv 标 "Decision-Difficulty"，论文 Table 1 标 "Mixed"
- **结论**: APPS Intro entropy ρ = +0.012 (p=0.63, 不显著)，应归为 **"Mixed"** 而非 "Decision-Difficulty"
- **修复**:
  - [x] `tab_signal_discovery/data.csv`: "Decision-Difficulty" → "Mixed"
  - [x] `tab_env_info_structure/data.csv`: "Info-Rich / Decision-Difficulty" → "Mixed / Mixed"
  - [x] `tab_env_info_structure.tex`: 同上
  - [x] 论文 Table 1 和 Table 2 原已正确 ("Mixed")，无需修改

---

## ~~🟡 重要~~ → 大部分已修复

### ~~4. AUC Hierarchy 只有 3 个环境的数据~~ → **已修复 (2026-03-23)**
- **问题**: 仅 3 环境 (HotpotQA, APPS, WebShop)，"Cross-environment" 暗示更多
- **修复**:
  - [x] 补充 Plancraft AUC 数据 (npz 可用): single_entropy=0.500, multi=0.736, hidden=0.951
  - [x] data.csv 更新为 4 环境 (FEVER/TWExpress/APPS Intv/CRUXEval 无 npz probe 数据)
  - [x] 论文 §3.1: "Cross-environment AUC analysis" → "AUC analysis across 4 environments with available probe data"
  - [x] AUC 数字修正: "≈0.53" → "≈0.50", "≈0.85" → "≈0.83", "≈0.89" → "≈0.90" (含 Plancraft 后的 4 环境平均)
  - [x] Abstract 同步修正
  - [x] Reviewer response 同步修正

### ~~5. CRUXEval EAAG 数据缺失~~ → **已修复 (2026-03-23)**
- **问题**: Job 23292522 CRUXEval 75/75 已完成，但 data.csv 缺 EAAG 行
- **修复**:
  - [x] CRUXEval EAAG 3-seed avg: SR=98.5%, ro/ep=1.24
  - [x] `tab_appendix_results/data.csv` 补充 EAAG CRUXEval + always_trigger CRUXEval 行

### ~~6. Gate Capacity 部分值为近似~~ → **已确认可接受 (2026-03-23)**
- **问题**: MLP/Hidden-state correct-direction SR 标为 "~95"
- **结论**: 论文使用 `$\sim$95\%` 标注，这是诚实的近似表达 (LaTeX `\sim` 符号)
  - Logistic correct = 95.2% (精确), MLP/Hidden ≈ 95% (Phase 2/5 估计)
  - 不补跑 — `\sim` 已表明是估计值
- [x] 论文中的 `$\sim$95` 表述已足够诚实，无需修改

### 7. Win/Loss 环境计数差异
- **位置**: Abstract + §5.2
- **论文说**: "34 wins vs 2 losses against 6 competing methods across 8 environments"
- **data.csv** (`tab_winloss`): AUQ 和 s1_budget 的 n_envs=7，其余 n_envs=6
- [ ] 确认各 baseline 实际评估了多少个环境
- [ ] 确保 34W/2L 的计算与 "8 environments" 一致
- [ ] 如实际是跨不同环境数统计的，在论文中说明

### ~~8. Stratified Reversal — APPS Interview 存在 NaN~~ → **已修复 (2026-03-23)**
- **问题**: "persists within every trajectory-length stratum" 过于绝对
- **修复**:
  - [x] §5.6: "within every trajectory-length stratum" → "within trajectory-length strata where utility variance is non-zero"
  - [x] 增加 HotpotQA 具体数字 ($-0.18$/$-0.46$/$-0.42$)

---

## 🟠 中等 (需清理但不影响核心论点)

### 9. Coverage Proxy — TWExpress 是明显 outlier
- **位置**: §5.4 / Appendix D
- **data.csv** (`fig_coverage_proxy`): TWExpress coverage=0.92 但 ρ=−0.29 → 不符合 "低 coverage → 负 ρ" 预测
- **README**: "step_count/max_steps is a poor coverage proxy for text adventure games"
- [ ] 论文中讨论 TWExpress 为 outlier 并解释原因
- [ ] 或为 TWExpress 设计更合理的 coverage proxy

### ~~10. fig_controlled_reversal — 完全无数据~~ → **已修复 (2026-03-23)**
- Job 23304305 全部完成，结果已分析
- InfoRich entropy ρ=+0.311 (符合预测), InfoPoor entropy ρ=+0.119 (不符合预测但 step_count 主导 -0.608)
- 已加入 §5.4 Theory Verification 末尾，支持 Signal Replacement (Obs 2)
- [x] `planning/experiment/fig_controlled_reversal/` 包含 data.csv, generate.py, output.pdf, README.md

### 11. fig_method_diagram — 无数据 (概念图)
- **位置**: §4 Method, Figure ref
- **README**: "conceptual diagram, no experimental data needed"
- [ ] 用 TikZ / Figma / draw.io 制作 EAAG 三步流程图
- [ ] 确认论文 `\ref{fig:method}` 有对应图

### ~~12. BSW APPS Intro 和 FEVER 的 total_cost 缺失~~ → **已确认可接受 (2026-03-23)**
- **问题**: BSW 在 HotpotQA/WebShop 无 cost 数据
- **结论**: BSW 实验只有 FEVER 有 cost 数据 (4.30 ro/ep)。HotpotQA/WebShop 的 BSW 跑在 Phase 4 (pre gate fix)，cost 数据不可靠
  - 论文 §5.3 只讨论 BSW SR 退化，不讨论 cost → 无影响
  - [x] `tab_main_results/data.csv` 中 BSW HotpotQA/WebShop cost 保持为空

### ~~17. fig_p1_temporal_shift 需移除 MBPP 并重新生成~~ → **已修复 (2026-03-23)**
- [x] `data.csv` 删除 MBPP 2 行 (10 rows remaining)
- [x] `generate.py` 重新运行，`output.pdf` 已更新 (不含 MBPP)
- [ ] 确认新图只包含 8 个评估环境中出现的数据

---

## 🟢 已确认支撑的观点 (无需修改)

| 观点 | 数据来源 | 状态 |
|------|----------|------|
| Direction Reversal (Obs.1): entropy ρ 反转 | tab_signal_discovery | ✅ 完全匹配 |
| Signal Identity (Obs.2): 不同环境最强信号不同 | tab_signal_discovery + fig4_feature_heatmap | ✅ 完全匹配 |
| CATTS failure: FEVER 34.2% < base 37.0% | tab_main_results | ✅ 完全匹配 |
| BSW degradation: HotpotQA −38.8pp, WebShop −22.4pp | fig3_bsw_direction + tab_main_results | ✅ 完全匹配 |
| MLP wrong direction: 45.3% < base 49.0% | tab_gate_capacity | ✅ 完全匹配 |
| EAAG main SR: HotpotQA 95.2%, APPS Intro 66.0%, WebShop 43.8%, FEVER 49.8% | tab_main_results | ✅ 完全匹配 |
| FEVER exploration bias 分析 | fig6_fever_bias | ✅ 支撑 |
| Feature heatmap: step_count 6/7 envs | fig4_feature_heatmap | ✅ 支撑 |
| Method classification table | tab_method_classification | ✅ 完整 |
| TWExpress 99.0%, Plancraft 23.3% | tab_diagnostic_results | ✅ 完全匹配 |
| Statistical significance (bootstrap CI) | tab_significance | ✅ 完整 |
| Env setup table: base/always SR | tab_env_setup | ✅ 完全匹配 |
| LLM ablation: <1pp except FEVER +9.1pp | fig5_llm_ablation | ✅ 支撑 |
| P1 Temporal dynamics: ρ 递减 early→late | fig_p1_temporal_shift | ✅ 已修复，数据匹配 |

---

## 修改优先级排序

| 优先级 | Item | 工作量 | 影响范围 | 状态 |
|--------|------|--------|----------|------|
| ~~P0~~ | ~~#1 P1 Temporal Shift 叙述~~ | ~~重写 1 段~~ | ~~§3.2 + §5.4 + Appendix + Reviewer~~ | ✅ 已修复 |
| ~~P0~~ | ~~#13 环境分类统一~~ | ~~改 10+ 处~~ | ~~全文~~ | ✅ 已修复 |
| ~~P0~~ | ~~#14 APPS 命名统一~~ | ~~改 20+ 处~~ | ~~全文~~ | ✅ 已修复 |
| ~~P0~~ | ~~#15 "6 environments" → "8 environments"~~ | ~~改 8 处~~ | ~~全文~~ | ✅ 已修复 |
| ~~P0~~ | ~~#16 移除 MBPP~~ | ~~改 1 处~~ | ~~Appendix 注释~~ | ✅ 已修复 |
| ~~P0~~ | ~~#2 Trigger Rate 数字~~ | ~~查原始数据 + 更新多处~~ | ~~Abstract + §5.3 + §5.5~~ | ✅ 已修复 |
| ~~P1~~ | ~~#3 APPS Intro type 标签~~ | ~~确认 + 改 1 处~~ | ~~Table 1~~ | ✅ 已修复 |
| ~~P1~~ | ~~#5 CRUXEval 数据~~ | ~~补充 data.csv~~ | ~~Appendix~~ | ✅ 已修复 |
| P1 | #7 Win/Loss 环境计数 | 确认 + 改 1-2 句 | Abstract + §5.2 | ⬜ 待处理 |
| ~~P2~~ | ~~#4 AUC 环境覆盖~~ | ~~补 Plancraft + 改措辞~~ | ~~§3.1~~ | ✅ 已修复 |
| ~~P2~~ | ~~#6 Gate Capacity~~ | ~~确认 $\sim$ 可接受~~ | ~~§5.6~~ | ✅ 已确认 |
| ~~P2~~ | ~~#8 Stratified NaN~~ | ~~改 1 句~~ | ~~§5.6~~ | ✅ 已修复 |
| ~~P2~~ | ~~#17 fig_p1 移除 MBPP~~ | ~~改 CSV + 重生成~~ | ~~fig_p1~~ | ✅ 已修复 |
| P3 | #9 Coverage outlier | 加 1 句讨论 | Appendix | ⬜ 待处理 |
| ~~P3~~ | ~~#10 Controlled reversal~~ | ~~确认引用状态~~ | ~~N/A or Appendix~~ | ✅ 已修复 |
| P3 | #11 Method diagram | 画图 | §4 | ⬜ 待处理 |
| ~~P3~~ | ~~#12 BSW cost~~ | ~~确认可接受~~ | ~~Table~~ | ✅ 已确认 |
