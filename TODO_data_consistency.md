# TODO: 实验数据与论文观点一致性修复清单

**生成日期**: 2026-03-23
**二轮核查**: 2026-03-23
**基于**: `VOC_PAPER_WRITING_GUIDE.md` vs `experiment/` 文件夹逐项核对

---

## ~~P0~~ — 全部已修复（数据层面）

### ~~1.~~ [x] fig1_signal_heatmap vs tab_signal_discovery: HotpotQA 数值矛盾 → **已修复 (2026-03-23)**

**根因**: `csv_fig1()` 用 Source A (phase1, 1208 records, seed 42), 论文用 Source B (phase5, 1117 records, 3 seeds)。

**修复**: fig1 和 fig_coverage_proxy 已统一为 Source B 值。二轮验证:
- fig1: HotpotQA entropy=-0.0407, step_count=-0.4944 ✅
- fig_coverage_proxy: entropy_rho=-0.0407, n_records=1117 ✅
- tab_signal_discovery: entropy_rho=-0.041, step_count=-0.494 ✅

---

### ~~2.~~ [x] P1 temporal 对 TWExpress 的描述与数据矛盾 → **已修复 (2026-03-23)**

**修复**: §5.4 line 1006-1011 现在分开讨论 FEVER（不显著 p>0.4）和 TWExpress（early 显著 ρ=+0.161, p=0.001, late 消失 p=0.877）。二轮验证与 fig_p1_temporal_shift 数据一致 ✅

---

### ~~3.~~ [x] "APPS Intro: RR=6%" 与 trigger rate 数据矛盾 → **部分修复 (2026-03-23)**

**修复状态**: §5.3 (line 963) 已改为 RR=35% ✅, 但 **§5.2 (line 912) 仍写 RR=6%** ❌ → 见新增 P1-A

---

### ~~4.~~ [x] "Pareto-dominates CaTS in 6/6 environments" → **已修复 (2026-03-23)**

**修复**: §5.2 (line 863) 改为 "5/6" ✅, 但 **Abstract 和 §1 P5 仍写 "Pareto-dominates all"** → 见新增 P1-D

---

## P1 — 需修复（二轮核查发现的文本残留 + 新问题）

### A. [ ] §5.2 APPS Intro 仍写 RR=6%（原 P0-3 未完全修复）

**位置**: VOC_PAPER_WRITING_GUIDE.md line 912

**现状**:
```latex
% line 912 (§5.2):
conservative gating (RR=6\%), achieving 66.0\% at 1.20 ro/ep.
```
```latex
% line 963 (§5.3, 已修复):
moderate in mixed environments (APPS Intro: RR=35\%, WebShop: RR=28\%),
```

同一文档内 §5.2 说 6%, §5.3 说 35%, 自相矛盾。fig_trigger_rate 加权平均验证为 ~35%。

**行动项**:
- [ ] Line 912: `RR=6\%` → `RR=35\%`
- [ ] 同时检查该 bullet 的叙述: "conservative gating" 在 RR=35% 时是否仍合适（35% 属于中等，非 conservative）

---

### B. [ ] §1 P3、§4、§5.6 仍用 38.8pp（BSW 基准不统一）

**位置**: lines 143, 676, 1120

**现状**: §5.3 (line 935-937) 已修复为 EAAG 基准 (−37.0pp, −23.2pp) ✅

但其他 3 处仍使用 always_trigger 基准 38.8pp:

| 位置 | Line | 当前文本 |
|---|---|---|
| §1 P3 | 143 | `direction causes SR to drop by 38.8\,pp on HotpotQA` |
| §4 Design | 676 | `the wrong direction degrades SR by 38.8\,pp` |
| §5.6 Robustness | 1120 | `$-$38.8\,pp on HotpotQA` |

**行动项**:
- [ ] 决定统一基准: EAAG (37.0pp) 或 always_trigger (38.8pp)
  - 建议: §5.3 的 EAAG 基准更合理 (BSW = EAAG with flipped direction)
- [ ] 若统一为 EAAG 基准:
  - Line 143: 38.8 → 37.0, 并补充 "vs. EAAG's 95.2%"
  - Line 676: 38.8 → 37.0
  - Line 1120: 38.8 → 37.0, 22.4 → 23.2
- [ ] 或: 保留 38.8pp 但统一标注 "(vs. always\_trigger)" 以消除歧义

---

### C. [ ] tab:capacity 表标题算术错误

**位置**: VOC_PAPER_WRITING_GUIDE.md line 1135

**现状**:
```latex
\caption{... a logistic gate with correct direction outperforms an MLP with wrong direction by 51.5\,pp.}
```

**实际**: Logistic correct (95.2%) − MLP wrong (45.3%) = **49.9pp**, 不是 51.5pp

tab_gate_capacity 数据: Logistic Correct SR=95.2, MLP Wrong SR=45.3, 差值=49.9

**行动项**:
- [ ] Line 1135: `51.5\,pp` → `49.9\,pp`

---

### D. [ ] Abstract 和 §1 P5 仍写 "Pareto-dominates all"

**位置**: lines 57, 184

**现状**: §5.2 (line 863) 已修正为 "5/6" ✅, 但:
- Line 57 (Abstract): `EAAG Pareto-dominates all fixed-direction baselines (34 wins vs.\ 2 losses...`
- Line 184 (§1 P5): `Pareto-dominates all calibrated baselines: 34 wins vs.\ 2 losses...`

FEVER 上 CaTS SR=50.2% > EAAG SR=49.8%, 严格不构成 Pareto dominance。

**行动项**:
- [ ] 方案 A (推荐): 将 "Pareto-dominates" 与 "34W/2L" 分开陈述，例如:
  `EAAG achieves 34 wins vs. 2 losses in head-to-head SR comparisons against 6 competing methods, and Pareto-dominates in 5/6 shared environments (exception: FEVER, within 0.4pp at half the cost).`
- [ ] 方案 B (最小改动): `Pareto-dominates all` → `Pareto-dominates nearly all` 并在括号中注明
- [ ] 同步检查 line 211 (Contribution #3) 和 line 1341 (Conclusion) 中的 Pareto 声明

---

### E. [ ] fig_controlled_reversal: n_probe=1208 与 Source B 不一致

**位置**: experiment/fig_controlled_reversal/data.csv

**现状**:
```csv
Original,49.0,97.0,-0.041,-0.494,95.2,1208
```
- entropy_rho=-0.041 和 step_count_rho=-0.494 已对齐到 Source B ✅
- 但 n_probe=**1208** 是 Source A 的样本量, Source B 应为 **1117**

**行动项**:
- [ ] 确认 controlled reversal 实验是否独立于 Source A/B（有自己的数据收集）
  - 若独立: 1208 是正确的, 无需修改, 但 rho 值应该从这 1208 条数据计算而非引用 Source B
  - 若引用 Source B: n_probe 应改为 1117
- [ ] 建议: 在 README.md 中注明数据来源

---

### F. [ ] §5.6 McNemar/TOST p-values 无数据支撑

**位置**: VOC_PAPER_WRITING_GUIDE.md lines 1163-1165

**现状**:
```latex
We report McNemar's test for paired SR comparisons (BSW vs.\ correct
direction: $p{=}0.035$) and TOST equivalence testing for EAAG
vs.\ oracle (non-inferiority: $p{=}0.002$, $\delta{=}3\%$).
```

tab_significance 使用 **bootstrap CI** (5000 resamples), 不包含 McNemar 或 TOST 结果。p=0.035 和 p=0.002 在数据中无出处。

**行动项**:
- [ ] 方案 A: 实际计算 McNemar 和 TOST 并录入数据
- [ ] 方案 B: 改为引用现有 bootstrap CI 结果, 例如:
  `We report bootstrap confidence intervals (5000 resamples) for all head-to-head comparisons (Table~\ref{tab:significance}). EAAG vs. BSW: ΔSR = +37.0pp, 95% CI [...]. Pareto-dominance claims use a conservative criterion (SR ≥ and Cost ≤ with at least one strict inequality).`

---

## P2 — 待完成项

### 9. [ ] fig_method_diagram 缺少实际内容

**位置**: §4 Method Overview

**问题**: 文件夹仅含 README.md, 无数据/图片。论文 §4 引用 `Figure~\ref{fig:method}`。

**行动项**:
- [ ] 制作 EAAG 三步流程图 (Explore → Reason → Learn & Deploy)
- [ ] 导出为 PDF 放入 fig_method_diagram/

---

## P3 — 完整性检查（非阻塞）

### ~~11.~~ [x] tab_significance 覆盖范围确认

- [x] 30 行数据覆盖 5 envs × 6 CB methods
- 注意: FEVER 环境无 CB 对比数据 (EAAG 和 CB 都在 ~50%, 无对比意义)

### 12. [ ] fig_matched_pair 在论文中的引用完整性

- [ ] 确认 §5.6 是否完整引用了 matched-pair 分析结果
- [ ] 数据: 4 环境 (HotpotQA, TWExpress, APPS Intv, APPS) × 3 difficulty bins
- [ ] HotpotQA delta_u 全部为负 (−0.08/−0.43/−0.39) — 支持 "高 entropy → 低 utility" 的 Type I 模式
- [ ] TWExpress Easy 为正 (+0.33) 但 Mid/Hard 为负 — 说明 early-step Type D 混合

### ~~13.~~ [x] fig_bsw_vs_rho 的 R² > 0.5 声明 → R²=0.803 已验证 ✅

### 14. [ ] APPS Intv 在 fig4_feature_heatmap 中只选中 3 个 features

- [ ] APPS Intv: 仅 has_error=1, step_count=1, step_ratio=1 被选中（token_entropy=0）
- [ ] 但 tab_signal_discovery 中 APPS Intv entropy_rho=+0.317 (最强正相关)
- [ ] 可能解释: step_count 和 step_ratio 与 entropy 共线性高, LASSO 选择了更稀疏的表示
- [ ] 建议: 若论文讨论了此现象可忽略; 若未讨论, 在 Appendix 中加一句解释

---

## 已关闭项汇总

| # | 问题 | 修复日期 | 状态 |
|---|---|---|---|
| 1 | fig1 vs tab HotpotQA 数据矛盾 | 2026-03-23 | ✅ Source B 统一 |
| 2 | TWExpress P1 描述错误 | 2026-03-23 | ✅ 分开讨论 |
| 3 | APPS Intro RR=6% (数据层) | 2026-03-23 | ✅ 确认 35%, §5.3 已改 |
| 4 | Pareto CaTS 6/6 (§5.2) | 2026-03-23 | ✅ 改为 5/6 |
| 5 | AUC ≈ 值范围 | 2026-03-23 | ✅ 近似可接受 |
| 6 | BSW 38.8pp 基准 (§5.3) | 2026-03-23 | ✅ 改为 EAAG 基准 37.0pp |
| 7 | Appendix APPS Intv 注释值 | 2026-03-23 | ✅ 改为 60.5/79.5 |
| 8 | fig_coverage_proxy 文本 | 2026-03-23 | ✅ §5.4 已有文本 |
| 10 | Trigger rate 加权平均 | 2026-03-23 | ✅ 66/35/28/49/73/33 |
| 11 | tab_significance 覆盖 | 2026-03-23 | ✅ 30 行 5env×6CB |
| 13 | R² > 0.5 | 2026-03-23 | ✅ R²=0.803 |

---

## 快速参考: 文件 → 论文位置映射

| 实验文件夹 | 论文位置 | 状态 |
|---|---|---|
| fig1_signal_heatmap | §3.1 | ✅ 已修复 (Source B) |
| fig2_pareto | §5.2 | ✅ |
| fig3_bsw_direction | §5.3 | ✅ 已修复 (EAAG 基准) |
| fig4_feature_heatmap | §3.1 Obs 2 | ✅ |
| fig5_llm_ablation | §5.3 | ✅ |
| fig6_fever_bias | §6 | ✅ |
| fig_auc_hierarchy | §3.1 Obs 3 | ✅ ≈ 值可接受 |
| fig_bsw_vs_rho | §5.3/附录 | ✅ R²=0.80 |
| fig_controlled_reversal | §5.4 | ⚠️ n_probe=1208 待确认 |
| fig_coverage_proxy | §5.4/App D | ✅ 已修复 (Source B) |
| fig_matched_pair | §5.6 | ✅ 数据存在, 引用待查 |
| fig_method_diagram | §4 | ⏳ 无内容 |
| fig_p1_temporal_shift | §5.4 | ✅ 已修复 TWExpress |
| fig_stratified_reversal | §5.6 | ✅ |
| fig_trigger_rate | §5.3 | ✅ 加权平均已验证 |
| tab_signal_discovery | §3.1 | ✅ |
| tab_env_info_structure | §3.2 | ✅ |
| tab_env_setup | §5.1 | ✅ |
| tab_main_results | §5.2 | ⚠️ Pareto "all" 待修文本 |
| tab_method_classification | §3.3 | ✅ |
| tab_gate_capacity | §5.6 | ❌ 表标题 51.5→49.9 |
| tab_winloss | §5.2 | ✅ 34W/2L 精确 |
| tab_diagnostic_results | §5.5 | ✅ |
| tab_appendix_results | 附录 B | ✅ |
| tab_significance | 附录 E | ⚠️ McNemar/TOST 无数据 |

---

**当前开放项统计**: P1 × 6 (A-F) + P2 × 1 (#9) + P3 × 2 (#12, #14) = **9 项**
**其中需立即修复**: A (RR 6%→35%) 和 C (51.5→49.9) 为明确数据错误
