# TODO: 实验数据与论文观点一致性修复清单

**生成日期**: 2026-03-23
**基于**: `VOC_PAPER_WRITING_GUIDE.md` vs `experiment/` 文件夹逐项核对

---

## P0 — 重大不一致（阻塞性，必须在提交前修复）

### 1. [ ] fig1_signal_heatmap vs tab_signal_discovery: HotpotQA 数值矛盾

**位置**: §3.1 Observation 1, Abstract, §1 P3

**问题**: 两个数据文件对 HotpotQA 给出完全不同的 Spearman ρ 值，其余 7 个环境一致。

| 指标 | fig1_signal_heatmap (计算值) | tab_signal_discovery (硬编码) | 论文使用 |
|---|---|---|---|
| HotpotQA token_entropy | **-0.3272** | -0.041 | -0.041 |
| HotpotQA step_count | **-0.0234** | -0.494 | -0.494 |

`fig_coverage_proxy` 中 HotpotQA entropy_rho=-0.3272 也与 fig1 一致，说明两份独立计算都指向 -0.327。

**影响范围**:
- Abstract: "step_count dominates in HotpotQA (ρ=−0.494)"
- §3.1 tab:signal-discovery 表格整行
- §3.1 Observation 1 叙述
- §3.2 Environment mapping 表格 (HotpotQA observed ρ)
- §5.4 P2 cross-environment consistency 论证

**行动项**:
- [ ] 检查 `generate_all_csvs.py` 中 `csv_fig1()` 的数据来源路径
- [ ] 检查 `csv_tab_signal()` 中 HotpotQA 硬编码值的原始来源
- [ ] 确认哪个是正确值（大概率需要回溯到原始 probe JSON）
- [ ] 统一两个文件的 HotpotQA 数据
- [ ] 若 fig1 的计算值正确 (entropy=-0.327, step_count=-0.023)，则需要：
  - 重写 Abstract 中 HotpotQA 相关数字
  - 更新 tab:signal-discovery 表格
  - 重新评估 "step_count dominates in HotpotQA" 这个论据是否成立
  - 更新 Environment mapping 表格
- [ ] 若 tab_signal_discovery 的硬编码值正确，则需要修复 fig1 和 fig_coverage_proxy 的计算逻辑

---

### 2. [ ] P1 temporal 对 TWExpress 的描述与数据矛盾

**位置**: §5.4 P1 verification 段落

**问题**: 论文写 "FEVER and TWExpress show weak, non-significant effects in both phases (p>0.4)"

fig_p1_temporal_shift 实际数据:

| 环境 | Phase | ρ | p-value | 显著? |
|---|---|---|---|---|
| FEVER | early | +0.054 | 0.446 | No ✅ |
| FEVER | late | +0.078 | 0.486 | No ✅ |
| TWExpress | early | **+0.161** | **0.001** | **Yes ❌** |
| TWExpress | late | +0.008 | 0.877 | No ✅ |

TWExpress early phase p=0.001，**高度显著**，不是 "p>0.4"。

**行动项**:
- [ ] 修改 §5.4 P1 段落，将 FEVER 和 TWExpress 分开讨论
- [ ] 对 TWExpress early ρ=+0.161 (p=0.001) 给出解释（可能与 early-step 的 Type D 成分有关）
- [ ] 建议改为: "FEVER shows weak, non-significant effects in both phases (p>0.4). TWExpress shows a significant positive early-phase effect (ρ=+0.161, p=0.001) that vanishes in the late phase (p=0.877), consistent with early-step Type D mixing."

---

### 3. [ ] "APPS Intro: RR=6%" 与 trigger rate 数据矛盾

**位置**: §5.2 per-environment analysis (APPS Intro bullet)

**问题**: 论文写 "EAAG correctly learns conservative gating (RR=6%)"

fig_trigger_rate 中 apps 的 per-step trigger rates:
- step 0: 40.5% (n=489)
- step 1: 25.1% (n=255)
- step 2: 12.1% (n=182)
- step 3: 37.1% (n=175)
- step 4: 54.1% (n=170)

加权平均 ≈ 33%，远高于 6%。

**行动项**:
- [ ] 排查 "6%" 数字的来源（可能来自旧版本实验、不同 seed、或不同度量方式）
- [ ] 若 6% 指的是 "episodes where at least one trigger occurred" 的比率，需明确标注
- [ ] 若无法追溯来源，用 trigger_rate CSV 重新计算加权平均并替换
- [ ] 同步更新 Abstract 中 trigger rate 相关表述（如果有引用此数值）

---

### 4. [ ] "Pareto-dominates CaTS in 6/6 environments" 无法验证

**位置**: §5.2 Main Results 开头

**问题**:
- tab_main_results 中 CaTS 只有 **4 个环境** 的数据 (HotpotQA, APPS, WebShop, FEVER)
- tab_diagnostic_results 和 tab_appendix_results 中 **没有 CaTS** 数据
- FEVER: EAAG SR=49.8% **<** CaTS SR=50.2%（EAAG cost 更低但 SR 更低），不构成 Pareto dominance

**行动项**:
- [ ] 确认 CaTS 是否有 6 个环境的实验数据（如有，补入 CSV）
- [ ] 若只有 4 个环境数据，改为 "Pareto-dominates CaTS in X/4 environments"
- [ ] 处理 FEVER 的 Pareto 判定: EAAG SR(49.8) < CaTS SR(50.2)，虽然 cost 更低
  - 选项 A: 明确写 "Pareto-dominates in 3/4, ties on FEVER within noise"
  - 选项 B: 补充 FEVER 的 confidence interval 论证差异不显著
- [ ] 同步修改 "SCG in 4/7 environments" 的声明，确保有数据支撑

---

## P1 — 中度问题（建议在提交前修正）

### 5. [ ] AUC hierarchy "≈" 描述掩盖了环境间差异

**位置**: §3.1 Observation 3

**问题**: 论文写 "single entropy AUC≈0.50, multi-signal AUC≈0.83, hidden-state AUC≈0.90"

实际范围 (fig_auc_hierarchy):

| Level | Min | Max | Mean | 论文 |
|---|---|---|---|---|
| single_entropy | 0.500 | **0.557** | 0.515 | ≈0.50 |
| multi_signal_lr | **0.736** | 0.924 | 0.818 | ≈0.83 |
| hidden_state_lr | **0.794** | 0.994 | 0.902 | ≈0.90 |

APPS 的 single_entropy=0.557、Plancraft 的 multi_signal=0.736、APPS 的 hidden_state=0.794 都显著偏离 "≈" 值。

**行动项**:
- [ ] 改为报告范围: "single entropy achieves AUC 0.50–0.56 (mean 0.52), multi-signal logistic regression 0.74–0.92 (mean 0.82), hidden-state probes 0.79–0.99 (mean 0.90)"
- [ ] 或者保留 "≈" 但加脚注说明环境间变异

---

### 6. [ ] BSW degradation "38.8pp" 对比基准不清

**位置**: §5.3 BSW ablation 段落

**问题**: "SR drops by 38.8pp on HotpotQA" — 38.8pp = always_trigger(97.0) - BSW(58.2)，但上下文说的是 "reversing the learned direction"，暗示比较对象是 EAAG(95.2)，差值实为 37.0pp。

fig3_bsw_direction: `degradation_pp` 列使用 `always_sr - bsw_sr`。

**行动项**:
- [ ] 明确对比基准: "BSW achieves 58.2% vs. EAAG's 95.2% (−37.0 pp) and always_trigger's 97.0% (−38.8 pp)"
- [ ] 或统一使用 EAAG 作为基准（改为 37.0pp），因为 BSW 就是 "EAAG with flipped direction"
- [ ] 同步更新 fig3_bsw_direction 的 degradation 计算方式（如果决定改基准）

---

### 7. [ ] Appendix 注释中 APPS Interview 数值与数据不匹配

**位置**: Appendix B (commented LaTeX)

**问题**: 论文注释写 "base 55.0%, always 81.0%"

实际数据:
- tab_env_setup: APPS Intv base=**60.5%**, always=**79.5%**

**行动项**:
- [ ] 更新注释中的数值为 base=60.5%, always=79.5%
- [ ] 检查 Appendix B 其他注释中的数值是否也有过时问题

---

## P2 — 待完成项

### 8. [ ] fig_coverage_proxy 对应的论文文本仍为 TODO

**位置**: §5.7 Observable Proxy

**问题**: 数据已有 (5 环境的 mean_coverage 和 entropy_rho)，但论文文本仍是 `% TODO` 模板。

数据摘要:

| 环境 | mean_coverage | entropy_rho |
|---|---|---|
| HotpotQA | 0.455 | -0.327 |
| FEVER | 0.059 | -0.119 |
| APPS | 1.000 | +0.012 |
| WebShop | 0.319 | -0.019 |
| TWExpress | 0.921 | -0.290 |
| APPS Intv | 1.000 | +0.318 |

**行动项**:
- [ ] 撰写 coverage proxy 分析段落
- [ ] 注意: 此处 HotpotQA entropy_rho=-0.327 与 fig1 一致但与 tab_signal_discovery(-0.041) 矛盾 → 需先解决 P0 #1
- [ ] 绘制 scatter plot: x=mean_coverage, y=entropy_rho

---

### 9. [ ] fig_method_diagram 缺少实际内容

**位置**: §4 Method Overview

**问题**: 文件夹仅含 README.md，无数据/图片。论文 §4 引用 `Figure~\ref{fig:method}`。

**行动项**:
- [ ] 制作 EAAG 三步流程图 (Explore → Reason → Learn & Deploy)
- [ ] 导出为 PDF 放入 fig_method_diagram/

---

### 10. [ ] Trigger rate 百分比需要加权计算验证

**位置**: §5.3, §5.2, Abstract

**涉及声明**:
- "73% in rollout-safe TWExpress"
- "66% in high-headroom HotpotQA"
- "28% in WebShop"
- "35% in APPS Intro"

**问题**: fig_trigger_rate 提供 per-step 粒度数据。论文中的百分比应为加权平均 `Σ(trigger_rate × n) / Σ(n)`，但未包含在 CSV 中。

**行动项**:
- [ ] 编写脚本从 fig_trigger_rate/data.csv 计算各环境加权平均 trigger rate
- [ ] 对比计算结果与论文声明
- [ ] 若偏差 > 3pp，更新论文数值
- [ ] 将加权平均值写入一个汇总 CSV 或添加到 README

---

## P3 — 完整性检查（非阻塞，提交前完成即可）

### 11. [ ] tab_significance 覆盖范围确认

- [ ] 确认 20 行数据是否覆盖了所有需要声明显著性的比较
- [ ] §5.6 提到的 McNemar's test (BSW vs correct, p=0.035) 和 TOST (p=0.002, δ=3%) 是否在数据中有记录

### 12. [ ] fig_matched_pair 在论文中的引用完整性

- [ ] 确认 §5.6 是否完整引用了 matched-pair 分析结果
- [ ] 4 个环境 × 3 个 difficulty bin 的数据是否都被讨论

### 13. [ ] fig_bsw_vs_rho 的 R² > 0.5 声明

**位置**: §5.3 "magnitude of degradation correlates with signal strength (|ρ| vs |ΔSR|, R² > 0.5)"

- [ ] 从 fig_bsw_vs_rho/data.csv (5 个点) 计算 R²，确认 > 0.5
- [ ] 5 个数据点的 R² 统计效力较弱，考虑是否需要降低声明强度

### 14. [ ] APPS Intv 在 fig4_feature_heatmap 中只选中 3 个 features

- [ ] APPS Intv: 仅 has_error=1, step_count=1, step_ratio=1 被选中（token_entropy=0）
- [ ] 论文 Observation 2 说 "step_count selected in 6/7" — APPS Intv 确实选了，一致
- [ ] 但 APPS Intv token_entropy 未被选中，这与 tab_signal_discovery 中 APPS Intv entropy_rho=+0.317 (strongest positive) 看似矛盾，需确认 LASSO 为何没选 entropy

---

## 快速参考: 文件 → 论文位置映射

| 实验文件夹 | 论文位置 | 状态 |
|---|---|---|
| fig1_signal_heatmap | §3.1 | ❌ HotpotQA 矛盾 |
| fig2_pareto | §5.2 | ✅ |
| fig3_bsw_direction | §5.3 | ⚠️ 基准模糊 |
| fig4_feature_heatmap | §3.1 Obs 2 | ✅ |
| fig5_llm_ablation | §5.3 | ✅ |
| fig6_fever_bias | §6 | ✅ |
| fig_auc_hierarchy | §3.1 Obs 3 | ⚠️ 范围模糊 |
| fig_bsw_vs_rho | §5.3/附录 | 待验证 R² |
| fig_controlled_reversal | §5.4 | ✅ |
| fig_coverage_proxy | §5.7 | 文本待写 |
| fig_matched_pair | §5.6 | ✅ |
| fig_method_diagram | §4 | ⏳ 无内容 |
| fig_p1_temporal_shift | §5.4 | ❌ TWExpress 描述错 |
| fig_stratified_reversal | §5.6 | ✅ |
| fig_trigger_rate | §5.3 | ⚠️ 需验证加权平均 |
| tab_signal_discovery | §3.1 | ❌ HotpotQA 矛盾 |
| tab_env_info_structure | §3.2 | ✅ |
| tab_env_setup | §5.1 | ✅ |
| tab_main_results | §5.2 | ❌ Pareto 6/6 不成立 |
| tab_method_classification | §3.3 | ✅ |
| tab_gate_capacity | §5.6 | ✅ |
| tab_winloss | §5.2 | ✅ |
| tab_diagnostic_results | §5.5 | ✅ |
| tab_appendix_results | 附录 B | ⚠️ 注释值不匹配 |
| tab_significance | 附录 E | 待确认覆盖范围 |
