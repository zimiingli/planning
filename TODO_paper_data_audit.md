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

## 🔴 紧急 (数据与论文矛盾，必须修改)

### 2. Trigger Rate 具体数字不匹配
- **位置**: Abstract, §5.3 Ablation, §5.5 等多处
- **论文声称**: "60% when headroom large (HotpotQA), 6% when small (APPS Intro), ~1% (Plancraft)"
- **实际数据** (`experiment/fig_trigger_rate/data.csv`):
  - HotpotQA: 各 step trigger rate 0.16~0.95，非恒定 60%
  - APPS Intro: step 0=0.40, step 1=0.25, step 2=0.12, step 3=0.37, step 4=0.54 → 整体 episode-level RR 待确认
  - Plancraft: step 0=0.49 逐步降到 0.03~0.16，非 ~1%
- [ ] 从原始实验 log 或 EAAG deployment 数据中提取 episode-level 平均 trigger rate (RR)
- [ ] 确认 fig_trigger_rate 里的数据是 exploration phase 还是 exploitation phase
- [ ] 用正确的 RR 数字更新 Abstract、§5.3、§5.5

### 3. APPS Intro 的 Two-Source Type 标签不一致
- **位置**: §3.1 Table 1 (tab_signal_discovery) vs §3.2 Table 2 (tab_env_info_structure)
- **论文 Table 1**: APPS Intro 的 Type = "Mixed"
- **data.csv** (`tab_signal_discovery`): APPS Intro 的 two_source_type = "Decision-Difficulty"
- [ ] 确认 APPS Intro 到底应归为 Mixed 还是 Decision-Difficulty
- [ ] 统一论文 Table 1 和 data.csv 的分类标签

---

## 🟡 重要 (数据不完整，影响论文可信度)

### 4. AUC Hierarchy 只有 3 个环境的数据
- **位置**: §3.1 Observation 3
- **论文说**: "Cross-environment AUC analysis" — 暗示多环境汇总
- **实际数据** (`experiment/fig_auc_hierarchy/data.csv`): 仅 HotpotQA, APPS Intro, WebShop (缺 FEVER, TWExpress, Plancraft 等)
- [ ] 如果有其他环境的 AUC 数据，补充到 data.csv
- [ ] 如果没有，论文中改为 "across 3 environments" 而非暗示全覆盖
- [ ] 验证 "single entropy ≈ 0.53" — 实际平均 ≈ 0.52 (HotpotQA=0.502, APPS Intro=0.557, WebShop=0.502)

### 5. CRUXEval EAAG 数据缺失
- **位置**: 主结果或附录
- **实际数据** (`experiment/tab_appendix_results/data.csv`): 无 EAAG CRUXEval 行
- **README**: "CRUXEval EAAG data pending (Job 23292522)"
- [ ] 检查 Job 23292522 是否已完成
- [ ] 补充 CRUXEval EAAG 的 SR 和 cost 数据
- [ ] 如未完成，论文中标注 pending 或移除 CRUXEval 相关声称

### 6. Gate Capacity 部分值为近似
- **位置**: §5.6, Table (tab_gate_capacity)
- **data.csv**: MLP Correct = "~95", Hidden state LR Correct = "~95"
- **README**: "Precise values would require additional GPU runs"
- [ ] 补跑 MLP correct-direction 和 Hidden state LR correct-direction 实验
- [ ] 用精确值替换 "~95"
- [ ] 或在论文中明确标注为 estimated (e.g., "≈95%")

### 7. Win/Loss 环境计数差异
- **位置**: Abstract + §5.2
- **论文说**: "34 wins vs 2 losses against 6 competing methods across 8 environments"
- **data.csv** (`tab_winloss`): AUQ 和 s1_budget 的 n_envs=7，其余 n_envs=6
- [ ] 确认各 baseline 实际评估了多少个环境
- [ ] 确保 34W/2L 的计算与 "8 environments" 一致
- [ ] 如实际是跨不同环境数统计的，在论文中说明

### 8. Stratified Reversal — APPS Interview 存在 NaN
- **位置**: §5.6, stratified analysis
- **data.csv** (`fig_stratified_reversal`): APPS Interview Mid/Late strata 的 rho=NaN (utility 为常数)
- **论文说**: "direction reversal persists within every trajectory-length stratum"
- [ ] 论文叙述改为排除 APPS Interview 的 NaN strata，或加注 "where utility variance is non-zero"

---

## 🟠 中等 (需清理但不影响核心论点)

### 9. Coverage Proxy — TWExpress 是明显 outlier
- **位置**: §5.4 / Appendix D
- **data.csv** (`fig_coverage_proxy`): TWExpress coverage=0.92 但 ρ=−0.29 → 不符合 "低 coverage → 负 ρ" 预测
- **README**: "step_count/max_steps is a poor coverage proxy for text adventure games"
- [ ] 论文中讨论 TWExpress 为 outlier 并解释原因
- [ ] 或为 TWExpress 设计更合理的 coverage proxy

### 10. fig_controlled_reversal — 完全无数据
- **位置**: 未在主文中引用 (planned causal experiment)
- **README**: "NOT STARTED. Requires ~1,600 episode GPU runs"
- [ ] 确认论文是否引用了此图
- [ ] 如引用了，要么补跑实验，要么从论文中移除引用
- [ ] 如仅作 future work，保持现状即可

### 11. fig_method_diagram — 无数据 (概念图)
- **位置**: §4 Method, Figure ref
- **README**: "conceptual diagram, no experimental data needed"
- [ ] 用 TikZ / Figma / draw.io 制作 EAAG 三步流程图
- [ ] 确认论文 `\ref{fig:method}` 有对应图

### 12. BSW APPS Intro 和 FEVER 的 total_cost 缺失
- **位置**: §5.2, tab_main_results
- **data.csv**: BSW 在 HotpotQA 和 WebShop 的 total_cost_ro_per_ep 为空
- [ ] 补充 BSW 的 cost 数据，或在论文中只讨论 SR 不讨论 cost

### 17. fig_p1_temporal_shift 需移除 MBPP 并重新生成
- **位置**: `experiment/fig_p1_temporal_shift/`
- **问题**: `data.csv` 包含 MBPP 数据行 (MBPP 不在 8 个评估环境中)，`fig_p1_temporal_shift.pdf` 基于含 MBPP 的数据生成
- [ ] 从 `data.csv` 删除 MBPP 的 2 行 (early + late)
- [ ] 重新运行 `generate.py` 生成不含 MBPP 的新 PDF
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
| P0 | #2 Trigger Rate 数字 | 查原始数据 + 更新多处 | Abstract + §5.3 + §5.5 | ⬜ 待处理 |
| P1 | #3 APPS Intro type 标签 | 确认 + 改 1 处 | Table 1 | ⬜ 待处理 |
| P1 | #5 CRUXEval 数据 | 等 GPU job 或移除 | 主结果 or Appendix | ⬜ 待处理 |
| P1 | #7 Win/Loss 环境计数 | 确认 + 改 1-2 句 | Abstract + §5.2 | ⬜ 待处理 |
| P2 | #4 AUC 环境覆盖 | 补数据或改措辞 | §3.1 | ⬜ 待处理 |
| P2 | #6 Gate Capacity 精确值 | 补跑实验 | §5.6 Table | ⬜ 待处理 |
| P2 | #8 Stratified NaN | 改 1 句 | §5.6 | ⬜ 待处理 |
| P2 | #17 fig_p1 移除 MBPP 重新生成 | 改 CSV + 跑脚本 | fig_p1_temporal_shift | ⬜ 待处理 |
| P3 | #9 Coverage outlier | 加 1 句讨论 | Appendix | ⬜ 待处理 |
| P3 | #10 Controlled reversal | 确认引用状态 | N/A or Appendix | ⬜ 待处理 |
| P3 | #11 Method diagram | 画图 | §4 | ⬜ 待处理 |
| P3 | #12 BSW cost 缺失 | 补数据 | Table | ⬜ 待处理 |
