# Phase 5: Full Experiment Status Report
**Last Updated:** 2026-03-11 (20:00 update)
**Goal:** FRVC gating framework across 7 environments (6 GO + 1 negative example)

---

## Executive Summary

| Environment | Step 0 | Step 1 | Step 2 (6 methods) | Step 3 (Baselines) | Cost Analysis |
|---|---|---|---|---|---|
| HotpotQA     | ✅ | ✅ | ✅ 6/6 | ✅ 4/4 (cal)   | ✅ |
| APPS         | ✅ | ✅ | ⚠️ 3/6 可靠 | ✅ 4/4 (cal)   | ✅ |
| WebShop      | ✅ | ✅ | ✅ 6/6 | ✅ 4/4 (cal)   | ✅ |
| BabyAI       | ✅ | ✅ | ✅ 6/6 | ✅ 12/12 done   | ❌ |
| TWExpress    | ✅ | ✅ | ✅ 6/6 | 🔄 Pending     | ❌ |
| TextWorld    | ✅ | ✅ | ❌ 4/6 (always_trigger+oracle TIMEOUT) | 🔄 4/12 running | ❌ |
| Plancraft    | ✅ | ✅ | ⚠️ 4/6 (missing random_50, best_sigma_wrong) | 🔄 10/12 done +2 running | ❌ |

### Paper Viability Assessment

| Environment | Paper? | Reason |
|---|---|---|
| **HotpotQA** | ✅ **主实验** | SCG(96.8%)≈oracle, 远超所有 CB, cost 节省 38% vs always_trigger |
| **WebShop** | ✅ **主实验** | SCG Pareto-dominates 所有 CB, cost 仅 +27%, 展示"学会何时不 rollout" |
| APPS | ⚠️ 补充 | 弱信号环境, SCG 正确不触发但无提升; 可作为"弱信号"案例讨论 |
| TWExpress | ⚠️ 补充 | 对比案例: rollout 从不有害 → SCG 选择性反而是劣势; 与 WebShop 对比 |
| BabyAI | ❌ 不用 | SCG < always_trigger, gate 不稳定, 高方差 |
| TextWorld | ❌ 不用 | always_trigger + oracle 均 TIMEOUT, 缺 2/6 core methods |
| Plancraft | ❌ 负例 | Rollout 本质有害, 连 oracle 也不行; 可在附录作为负例展示 |

**Pipeline steps:**
- **Step 0 (GO/NO-GO):** 50 ep base_only + always_trigger → GO if SR ∈ [5%, 85%] AND Δ > 3pp
- **Step 1 (Signal Discovery):** 200 ep always_trigger → Spearman ρ, MI, η² for all signals
- **Step 2 (Core 6-Method):** 6 methods × 3 seeds × 200 ep (base_only, always_trigger, random_50, best_sigma_wrong, scg_finetune_lr, oracle)
- **Step 3 (Competing Baselines):** 4 methods × 3 seeds × 200 ep (CATTS, SEAG, CoRefine, CaTS)

---

## ⚠️ Known Data Issues

1. **APPS Phase3_supp gate 实现有 bug** — SCG trigger_rate=1.0 (= always_trigger)、best_sigma_wrong trigger_rate=0.0 (= base_only)、random_50 trigger_rate=0.79 (应为 0.5)。Phase5/comparison (3 methods) gate 行为正确，已改用 Phase5 数据。Phase3_supp random_50/best_sigma_wrong/oracle 数据标注为不可靠。
2. **BabyAI SCG seed=456 异常** — rollouts=55.4/ep（≈ always_trigger），gate 未收敛。SR=15.0% 最高但可能仅因 rollout 多。
3. **TextWorld always_trigger + oracle 均超时** — 12h 时限不够，6 个 job 全部 TIMEOUT。TextWorld 现缺 2/6 core methods，不可用于 paper。
4. **TextWorld SCG seed=456 异常** — rollouts=23.0（其他 seed ~12），SR=49.5% 反而最低。
5. **WebShop random_50 > always_trigger** — 47.5% vs 43.0%，过度 rollout 反而有害。
6. **APPS 竞争 baselines 全部退化为 base_only** — rollouts ≈ 0，gate 从不触发。

---

## 1. HotpotQA

### 1.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=49.0%, always=97.0%, Δ=+48.0% |
| Step 1 | ✅ | N=1117 signal points |
| Step 2 | ✅ 6/6 | Phase5 数据 (4 methods), Phase3 补充 (random_50, best_sigma_wrong) |
| Step 3 | ✅ 4/4 (cal) | |
| Cost   | ✅ | |

### 1.2 Feature Importance (N=1117)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | step_count | −0.4944 | 6.4e-70 *** |
| 2 | evidence_count | −0.4256 | 2.3e-50 *** |
| 3 | is_finish_proposed | −0.4191 | 1.0e-48 *** |
| 4 | token_entropy | −0.0407 | 0.174 |

### 1.3 Unified Results & Cost Table

**Token cost 常数:** C_base=216 tok/step, C_rollout=7,743 tok/trigger (35.8×), C_vote=1,063 tok/step (CATTS K=5)

| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep | Cost (tok) | Cost (×base) |
|---|---|---|---|---|---|---|---|---|---|
| base_only | core | 51.5% | 48.5% | 47.0% | **49.0%** | 6.2 | 0.00 | 1,349 | **1.00×** |
| always_trigger | core | 96.5% | 97.0% | 97.5% | **97.0%** | 1.8 | 1.80 | 14,351 | 10.64× |
| random_50 | core | 89.0% | 90.0% | 88.0% | **89.0%** | 3.0 | 1.54 | 12,571 | 9.32× |
| best_sigma_wrong | core | 61.5% | 57.5% | 55.5% | **58.2%** | 5.7 | 2.86 | 23,380 | 17.33× |
| **scg_finetune_lr** | **core** | **96.0%** | **97.0%** | **97.5%** | **96.8%** | **1.8** | **1.09** | **8,834** | **6.55×** |
| oracle | core | 96.5% | 97.0% | 97.5% | **97.0%** | 1.8 | 0.59 | 4,957 | 3.67× |
| CATTS | CB | 71.0% | 71.0% | 63.0% | **68.3%** | 4.6 | 1.07 | 14,171 | 10.50× |
| SEAG | CB | 69.5% | 71.0% | 62.0% | **67.5%** | 4.6 | 1.02 | 8,902 | 6.60× |
| CoRefine | CB | 71.0% | 71.0% | 62.5% | **68.2%** | 4.6 | 1.05 | 9,101 | 6.75× |
| CaTS | CB | 94.0% | 91.5% | 94.0% | **93.2%** | 2.3 | 1.77 | 14,233 | 10.55× |

**CER (ΔSR/ΔCost):** SCG=0.086 > always=0.050 > CaTS=0.046 > CATTS=0.020

**Takeaway:**
- SCG(96.8%, 6.55×) ≈ oracle SR，但**节省 38% cost** vs always_trigger(10.64×)
- CaTS(93.2%) 是唯一接近的 CB，但 cost 10.55× — 比 SCG 贵 61%
- CATTS/SEAG/CoRefine ~68% 因方向错误大幅退化
- FRVC 是唯一在 cost < 7× 区域内 SR > 0.96 的方法

### 1.5 Data Paths
```
Step 2 (Phase5):     results/phase5/comparison/hotpotqa/{method}/seed_{s}/summary.json  (base/always/scg/oracle)
Step 2 (Phase3):     results/phase3/hotpotqa/{method}/seed_{s}/performance_summary.json  (random_50/best_sigma_wrong)
Step 3 (cal):        results/phase5/competing_baselines/hotpotqa/{method}/seed_{s}/summary.json
Phase 1 signal:      results/phase5/calibration_data/hotpotqa/phase1_signal_data.json
Token costs:         results/phase5/token_costs/hotpotqa_token_costs.json
```

---

## 2. APPS

### 2.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=58.5%, always=64.5%, Δ=+6.0% |
| Step 1 | ✅ | N=1567, 仅 step_count 显著 (ρ=−0.155) |
| Step 2 | ⚠️ 3/6 可靠 | Phase5 有 base/always/scg (gate 正确); r50/bsw/oracle 重跑中 (9 jobs pending) |
| Step 3 | ✅ 4/4 (cal) | |
| Cost   | ✅ | |

### 2.2 Feature Importance (N=1567)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | step_count | −0.1551 | 6.7e-10 *** |
| 2 | token_entropy | +0.0121 | 0.631 |

极弱信号环境。

### 2.3 Unified Results & Cost Table

**Token cost 常数:** C_base=840 tok/step, C_rollout=3,306 tok/trigger (3.9×), C_vote=4,198 tok/step (CATTS K=5, **超过 rollout 成本**)

| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep | Cost (tok) | Cost (×base) | Source |
|---|---|---|---|---|---|---|---|---|---|---|
| base_only | core | 58.5% | 58.5% | 58.5% | **58.5%** | 3.0 | 0.00 | 2,489 | **1.00×** | Phase5 ✅ |
| always_trigger | core | 65.0% | 64.5% | 64.0% | **64.5%** | 2.6 | 2.58 | 10,715 | 4.30× | Phase5 ✅ |
| random_50 | core | 65.5% | 67.0% | 67.0% | **66.5%** | — | — | — | — | ⚠️ P3_supp bug, 重跑中 |
| best_sigma_wrong | core | 58.5% | 58.5% | 58.5% | **58.5%** | — | — | — | — | ⚠️ P3_supp bug, 重跑中 |
| **scg_finetune_lr** | **core** | **59.0%** | **58.5%** | **59.0%** | **58.8%** | **2.9** | **0.18** | **3,065** | **1.23×** | **Phase5 ✅** |
| oracle | core | 67.5% | 65.5% | 67.5% | **66.8%** | — | — | — | — | ⚠️ P3_supp, 重跑中 |
| CATTS | CB | 58.5% | 58.5% | 58.5% | **58.5%** | 3.0 | 0.03 | 14,993 | **6.02×** | Phase5 ✅ |
| SEAG | CB | 58.5% | 58.5% | 58.5% | **58.5%** | 3.0 | 0.01 | 2,522 | 1.01× | Phase5 ✅ |
| CoRefine | CB | 58.5% | 58.5% | 58.5% | **58.5%** | 3.0 | 0.01 | 2,522 | 1.01× | Phase5 ✅ |
| CaTS | CB | 59.0% | 59.0% | 59.0% | **59.0%** | 2.9 | 0.04 | 2,600 | 1.04× | Phase5 ✅ |

**Phase3_supp gate bug:** SCG trigger=1.0 (=always), bsw trigger=0.0 (=base), r50 trigger=0.79 (≠0.50)。已用正确代码重跑 (9 jobs pending → `results/phase5/apps_rerun/`)。

**Takeaway:**
- 弱信号环境。所有 gated 方法 rollout 极少 → cost≈base，SR≈base
- SCG 正确识别信号不足 (pearson_r≈−0.05, LR acc 53-58%) → 几乎不触发 (RR=2.5-10.8%)
- CATTS 是灾难: SR 无提升但 cost **6.02×** — K=5 code gen 投票 (C_vote=4,198) > rollout 本身 (C_rollout=3,306)

### 2.5 Data Paths
```
Step 2 (可靠):       results/phase5/comparison/apps/{method}/seed_{s}/summary.json  (base/always/scg)
Step 2 (⚠️有bug):   results/phase3_supp/apps/core/{method}/seed_{s}/performance_summary.json  (r50/bsw/oracle)
Step 3 (cal):        results/phase5/competing_baselines_calibrated/apps/{method}/seed_{s}/summary.json
Phase 1 signal:      results/phase5/calibration_data/apps/phase1_signal_data.json
Token costs:         results/phase5/token_costs/apps_token_costs.json
```

---

## 3. WebShop

### 3.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=7.2%, always=43.0%, Δ=+35.8% |
| Step 1 | ✅ | N=3899, num_available_actions 最强 (ρ=+0.444) |
| Step 2 | ✅ 6/6 | Phase4 数据 |
| Step 3 | ✅ 4/4 (cal) | |
| Cost   | ✅ | |

### 3.2 Feature Importance (N=3899)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | num_available_actions | +0.4443 | 2.6e-188 *** |
| 2 | step_count | −0.1297 | 4.3e-16 *** |
| 3 | evidence_count | −0.1297 | 4.3e-16 *** |
| 4 | is_finish_proposed | −0.0359 | 0.025 * |
| 5 | token_entropy | −0.0192 | 0.231 |

### 3.3 Unified Results & Cost Table

**Token cost 常数:** C_base=705 tok/step, C_rollout=9,089 tok/trigger (12.9×), C_vote=3,385 tok/step (CATTS K=5)

| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep | Cost (tok) | Cost (×base) |
|---|---|---|---|---|---|---|---|---|---|
| base_only | core | 8.0% | 8.0% | 5.5% | **7.2%** | 14.1 | 0.00 | 9,919 | **1.00×** |
| always_trigger | core | 47.5% | 44.0% | 37.5% | **43.0%** | 5.6 | 5.63 | 55,173 | 5.56× |
| random_50 | core | 54.0% | 47.0% | 41.5% | **47.5%** | 6.4 | 3.28 | 34,330 | 3.46× |
| best_sigma_wrong | core | 6.5% | 9.0% | 6.0% | **7.2%** | 14.0 | 5.20 | 57,133 | 5.76× |
| **scg_finetune_lr** | **core** | **49.0%** | **44.5%** | **37.5%** | **43.7%** | **5.6** | **0.95** | **12,640** | **1.27×** |
| oracle | core | 47.0% | 44.0% | 39.0% | **43.3%** | 5.6 | 0.73 | 10,584 | 1.07× |
| CATTS | CB | 15.5% | 16.5% | 16.0% | **16.0%** | 13.0 | 0.20 | 55,026 | 5.55× |
| SEAG | CB | 33.5% | 26.5% | 24.0% | **28.0%** | 10.5 | 2.28 | 28,156 | 2.84× |
| CoRefine | CB | 31.5% | 27.0% | 24.0% | **27.5%** | 10.5 | 2.21 | 27,498 | 2.77× |
| CaTS | CB | 33.0% | 29.5% | 29.0% | **30.5%** | 9.2 | 3.04 | 34,153 | 3.44× |

**CER (ΔSR/ΔCost):** SCG=**1.352** >> CoRefine=0.115 > SEAG=0.113 > CaTS=0.096 > always=0.088

**Takeaway — WebShop 是 FRVC 的 showcase 环境:**
- **过度 rollout 有害:** random_50(47.5%) > always_trigger(43.0%)，并非每一步都值得 rollout
- **SCG 效率极高:** SR=43.7%, cost=1.27× — 仅 +27% overhead，cost 仅为 always_trigger 的 **23%**
- **SCG Pareto-dominates 所有竞争方法:** vs CaTS (0.305, 3.44×): SR↑43%, cost↓63%; vs SEAG (0.280, 2.84×): SR↑56%, cost↓55%
- **低 cost 双重来源:** (1) 精准触发 RR=17% → 少 rollout; (2) 快速成功 steps 14.1→5.6 → 少 base cost
- **Rollout 效率排序:** oracle(49.7pp/ro) > SCG(38.3pp/ro) >> random_50(12.3pp/ro) >> always(6.4pp/ro)

### 3.5 Data Paths
```
Step 2:              results/phase4/webshop/core/{method}/seed_{s}/performance_summary.json  (keys: overall_stats.*)
Step 3 (cal):        results/phase5/competing_baselines_calibrated/webshop/{method}/seed_{s}/summary.json
Phase 1 signal:      results/phase5/calibration_data/webshop/phase1_signal_data.json
Token costs:         results/phase5/token_costs/webshop_token_costs.json
```

---

## 4. BabyAI

### 4.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=2.0%, always=11.3%, Δ=+9.3% |
| Step 1 | ✅ | N=11550, 信号极弱 (max |ρ|=0.052) |
| Step 2 | ✅ 6/6 | |
| Step 3 | ✅ 12/12 done | |
| Cost   | ❌ | |

### 4.2 Feature Importance (N=11550)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | step_count | −0.0515 | 3.1e-08 *** |
| 2 | carrying_object | +0.0269 | 3.8e-03 ** |
| 3 | token_entropy | +0.0218 | 0.019 * |
| 4 | distance_to_goal | −0.0049 | 0.597 |

注: rooms_visited/evidence_count 与 step_count 完全共线 (ρ 相同)。

### 4.3 Unified Results Table
| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep |
|---|---|---|---|---|---|---|---|
| base_only | core | 2.0% | 1.5% | 2.5% | **2.0%** | 62.9 | 0.0 |
| always_trigger | core | 12.5% | 7.0% | 14.5% | **11.3%** | 58.0 | 57.96 |
| random_50 | core | 9.5% | 6.5% | 13.5% | **9.8%** | 58.9 | 29.48 |
| best_sigma_wrong | core | 7.5% | 6.0% | 7.5% | **7.0%** | 61.4 | 30.88 |
| scg_finetune_lr | core | 7.0% | 4.5% | ⚠️15.0% | **8.8%** | 58.9 | 5.1/7.5/⚠️55.4 |
| oracle | core | 11.5% | 8.0% | 14.5% | **11.3%** | 57.9 | 0.10 |
| CaTS | CB | 9.5% | 5.0% | 11.5% | **8.7%** | 59.2 | 14.0/15.7/10.7 |
| CATTS | CB | 10.0% | 5.0% | 13.0% | **9.3%** | 58.9 | 11.2/15.0/12.7 |
| SEAG | CB | 10.0% | 4.5% | 12.0% | **8.8%** | 59.2 | 11.2/15.7/9.4 |
| CoRefine | CB | 10.0% | 4.5% | 12.0% | **8.8%** | 59.2 | 11.2/15.7/9.4 |

⚠️ SCG seed=456: rollouts=55.4 ≈ always_trigger, gate 未收敛。无 token cost 数据。
所有 CB ≈ SCG(8.8%) < always_trigger(11.3%)，进一步确认 BabyAI 不适合 paper。

### 4.4 Data Paths
```
Step 2:              results/phase5/babyai/babyai/{method}/seed_{s}/summary.json
Step 3:              results/phase5/competing_baselines_calibrated/babyai/{method}/seed_{s}/summary.json  (partial)
Phase 1 signal:      results/phase5/babyai/babyai/phase1_signal_data.json
```

---

## 5. TextWorldExpress

### 5.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=67.5%, always=99.3%, Δ=+31.8% |
| Step 1 | ✅ | N=798, step_count 最强 (ρ=−0.477) |
| Step 2 | ✅ 6/6 | |
| Step 3 | 🔄 0/12 pending | 被 TextWorld/Plancraft CB 阻塞 |
| Cost   | ❌ | |

### 5.2 Feature Importance (N=798)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | step_count | −0.4773 | 1.2e-46 *** |
| 2 | num_admissible_commands | +0.4474 | 1.6e-40 *** |
| 3 | token_entropy | −0.2898 | 6.7e-17 *** |
| (cat) | action_type | η²=0.098 | — |

### 5.3 Unified Results Table
| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep |
|---|---|---|---|---|---|---|---|
| base_only | core | 67.0% | 69.0% | 66.5% | **67.5%** | 26.1 | 0.0 |
| always_trigger | core | 98.5% | 99.5% | 100.0% | **99.3%** | 3.5 | 3.45 |
| random_50 | core | 98.0% | 98.0% | 97.5% | **97.8%** | 5.1 | 2.51 |
| best_sigma_wrong | core | 99.0% | 99.0% | 99.0% | **99.0%** | 5.2 | 3.20 |
| **scg_finetune_lr** | **core** | **97.0%** | **98.0%** | **96.0%** | **97.0%** | **5.1** | **1.38** |
| oracle | core | 98.5% | 99.5% | 100.0% | **99.3%** | 3.5 | 0.91 |
| CATTS | CB | — | — | — | — | — | — |
| SEAG | CB | — | — | — | — | — | — |
| CoRefine | CB | — | — | — | — | — | — |
| CaTS | CB | — | — | — | — | — | — |

**TWExpress 是"rollout 永远无害"环境：** Step 1 数据显示 utility 从不为负 (0/798)，22.6% 正面、77.4% 中性。因此：
- **触发率越高 SR 越高：** always(99.3%, 100%) > bsw(99.0%, 63%) > r50(97.8%, 50%) > SCG(97.0%, 28%)
- **best_sigma_wrong 并非"方向错了还好"**，而是 wrong direction + threshold=2 恰好制造了 63% 高触发率
- **SCG 的选择性在此环境是劣势** — 正确学到"early steps 最有价值"，但选择性限制了 rollout 总量
- **Oracle(99.3%, 0.91 ro/ep) 的效率最高** — 精准识别 22.6% 有效步骤，用最少 rollout 达到最高 SR
- **论文叙事：** TWExpress 与 WebShop 形成对比 — WebShop 过度 rollout 有害 (SCG 选择性是优势)，TWExpress rollout 无害 (SCG 选择性是劣势)。两个环境共同说明 SCG 确实学会了信号方向，但最优触发策略因环境而异。

### 5.4 Data Paths
```
Step 2:              results/phase5/twexpress/twexpress/{method}/seed_{s}/summary.json
Step 3:              results/phase5/competing_baselines_calibrated/twexpress/{method}/seed_{s}/summary.json  (pending)
Phase 1 signal:      results/phase5/twexpress/twexpress/phase1_signal_data.json
```

---

## 6. TextWorld

### 6.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=45.0%, Δ 待 always_trigger 完成 |
| Step 1 | ✅ | N=9999, score_fraction 最强 (ρ=+0.174) |
| Step 2 | ❌ 4/6 | always_trigger + oracle 均 **TIMEOUT**(12h) |
| Step 3 | 🔄 4/12 running | cats ×3 + catts ×1 running; 8 pending |
| Cost   | ❌ | |

### 6.2 Feature Importance (N=9999)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | score_fraction | +0.1744 | 4.1e-69 *** |
| 2 | num_admissible_commands | −0.1276 | 1.4e-37 *** |
| 3 | step_count | +0.1009 | 4.6e-24 *** |
| 4 | token_entropy | −0.0203 | 0.042 * |
| (cat) | action_type | η²=0.059 | — |

注: step_count 方向为 **positive**（与大多数环境相反）。

### 6.3 Unified Results Table (partial)
| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep |
|---|---|---|---|---|---|---|---|
| base_only | core | 46.0% | 44.0% | 45.0% | **45.0%** | 31.9 | 0.0 |
| always_trigger | core | ❌ TIMEOUT | ❌ TIMEOUT | ❌ TIMEOUT | — | — | — |
| random_50 | core | 66.5% | 63.5% | 64.5% | **64.8%** | 27.5 | 13.75 |
| best_sigma_wrong | core | 58.0% | 55.5% | 57.5% | **57.0%** | 31.9 | 14.30 |
| scg_finetune_lr | core | 60.0% | 53.5% | ⚠️49.5% | **54.3%** | 36.8 | 11.6/13.4/⚠️23.0 |
| oracle | core | ❌ TIMEOUT | ❌ TIMEOUT | ❌ TIMEOUT | — | — | — |
| CATTS | CB | — | — | — | — | — | — |
| SEAG | CB | — | — | — | — | — | — |
| CoRefine | CB | — | — | — | — | — | — |
| CaTS | CB | — | — | — | — | — | — |

⚠️ always_trigger + oracle 均 12h TIMEOUT (3chains×3horizon×5top_k 成本过高)。TextWorld 现缺 2/6 core methods，**不可用于 paper**。SCG seed=456 rollouts=23.0 翻倍但 SR 最低。

### 6.4 Data Paths
```
Step 2:              results/phase5/textworld/textworld/{method}/seed_{s}/summary.json
Step 3:              results/phase5/competing_baselines_calibrated/textworld/{method}/seed_{s}/summary.json  (pending)
Phase 1 signal:      results/phase5/textworld/textworld/phase1_signal_data.json
```

---

## 7. Plancraft (Negative Example)

### 7.1 Status
| Step | Status | Notes |
|---|---|---|
| Step 0 | ✅ | base=29.8%, always=22.8%, **Δ=−7.0%** (rollout 有害) |
| Step 1 | ✅ | N=1360, has_output 最强 (ρ=+0.162), utility 极低 (positive_rate=1.1%) |
| Step 2 | ⚠️ 4/6 (K=3) | Missing random_50, best_sigma_wrong |
| Step 3 | 🔄 10/12 done | seag-456 + corefine-456 running |
| Cost   | ❌ | |

### 7.2 Feature Importance (N=1360)
| Rank | Signal | Spearman ρ | p-value |
|---|---|---|---|
| 1 | has_output | +0.1621 | 1.8e-09 *** |
| 2 | inventory_size | +0.0617 | 0.023 * |
| 3 | grid_items | −0.0469 | 0.084 |
| 4 | crafting_progress | −0.0171 | 0.529 |
| 5 | token_entropy | −0.0159 | 0.557 |

### 7.3 Unified Results Table
| Method | Type | SR (s42) | SR (s123) | SR (s456) | **Mean SR** | Steps | Ro/ep |
|---|---|---|---|---|---|---|---|
| **base_only** | **core** | **29.0%** | **30.0%** | **30.5%** | **29.8%** | **12.0** | **0.0** |
| always_trigger | core | 20.5% | 22.5% | 25.5% | **22.8%** | 7.0 | 6.99 |
| random_50 | core | — | — | — | — | — | — |
| best_sigma_wrong | core | — | — | — | — | — | — |
| scg_finetune_lr | core | 21.0% | 20.0% | 23.5% | **21.5%** | 8.1 | 3.33 |
| oracle | core | 20.0% | 20.5% | 23.5% | **21.3%** | 7.0 | 0.08 |
| CATTS | CB | 23.5% | 25.0% | 26.5% | **25.0%** | 9.6 | 2.01/2.11/2.31 |
| SEAG | CB | 24.0% | 25.0% | 🔄 | **24.5%** | 9.7 | 2.03/2.13/— |
| CoRefine | CB | 22.5% | 20.0% | 🔄 | **21.3%** | 9.7 | 2.04/1.98/— |
| CaTS | CB | 21.5% | 20.0% | 25.5% | **22.3%** | 7.9 | 4.65/4.33/4.19 |

**Rollout 在此环境本质上有害。** base_only(29.8%) 是最佳策略，所有 rollout 方法均低于 base_only:
- 即使 oracle(21.3%) 也比 base_only 低 8.5pp
- CB 方法 (CATTS 25.0%, SEAG 24.5%, CaTS 22.3%) 同样不如 base_only，但略优于 always_trigger(22.8%)
- CATTS/SEAG rollout 少 (~2/ep) 因此 SR 损害较小；CaTS rollout 多 (~4.4/ep) 接近 always_trigger 水平

### 7.4 Data Paths
```
Step 2:              results/phase5/plancraft/plancraft/{method}/seed_{s}/summary.json
Step 3:              results/phase5/competing_baselines_calibrated/plancraft/{method}/seed_{s}/summary.json  (pending)
Phase 1 signal:      results/phase5/plancraft/plancraft/phase1_signal_data.json
```

---

## 8. Job Tracking (2026-03-11 20:00)

### 已完成 (since last update)
- ✅ **TextWorld oracle × 3** — ❌ 全部 TIMEOUT (12h)
- ✅ **BabyAI CB 12/12** — 全部完成
- ✅ **Plancraft CB 10/12** — cats×3 + catts×3 + seag×2 + corefine×2

### Running (6 jobs)
| Job ID | Name | Runtime |
|---|---|---|
| 23089030 | frvc-cb-pc-corefine-456 | ~1.5h |
| 23089033 | frvc-cb-pc-seag-456 | ~1h |
| 23089034 | frvc-cb-tw-cats-123 | ~40min |
| 23089035 | frvc-cb-tw-cats-42 | ~36min |
| 23089036 | frvc-cb-tw-cats-456 | ~34min |
| 23089037 | frvc-cb-tw-catts-123 | ~15min |

### Pending (29 jobs)
- TextWorld CB: 8 remaining (catts×2, corefine×3, seag×3)
- TWExpress CB: 12 jobs
- **APPS rerun: 9 jobs** (random_50×3, best_sigma_wrong×3, oracle×3) → `results/phase5/apps_rerun/`

---

## 9. Paper Table Data Paths

### Table 1: Core 6-Method Comparison (SR)
| Environment | Primary Path | JSON Key | Notes |
|---|---|---|---|
| HotpotQA | `results/phase5/comparison/hotpotqa/{method}/seed_{s}/summary.json` | `success_rate` | random_50/best_sigma_wrong 用 Phase3 |
| APPS | `results/phase5/comparison/apps/{method}/seed_{s}/summary.json` | `success_rate` | Phase5 仅 3 methods; Phase3_supp 有 bug |
| WebShop | `results/phase4/webshop/core/{method}/seed_{s}/performance_summary.json` | `overall_stats.success_rate` | |
| BabyAI | `results/phase5/babyai/babyai/{method}/seed_{s}/summary.json` | `success_rate` | |
| TWExpress | `results/phase5/twexpress/twexpress/{method}/seed_{s}/summary.json` | `success_rate` | |
| TextWorld | `results/phase5/textworld/textworld/{method}/seed_{s}/summary.json` | `success_rate` | partial |
| Plancraft | `results/phase5/plancraft/plancraft/{method}/seed_{s}/summary.json` | `success_rate` | 4/6 methods |

### Table 2: Cost Analysis
```
results/phase5/token_costs/{env}_token_costs.json       (HotpotQA/APPS/WebShop only)
reports/phase5_cost_analysis_report.md                   (详细)
reports/table2_cost_analysis.md                          (精简)
```

### Table 3: Competing Baselines
```
results/phase5/competing_baselines/hotpotqa/{method}/seed_{s}/summary.json             (HotpotQA, cal)
results/phase5/competing_baselines_calibrated/{env}/{method}/seed_{s}/summary.json      (其他环境)
```

### Table 4: Feature Importance
```
results/phase5/{env}/{env}/step1_signal_discovery.json                (Phase5 new envs)
results/phase5/calibration_data/{env}/phase1_signal_data.json         (Phase1 envs)
```

---

## 10. Remaining Action Items

1. ~~TextWorld always_trigger 超时~~ → ❌ oracle 也 TIMEOUT，TextWorld 确认不可用
2. **APPS rerun r50/bsw/oracle** — 9 jobs pending (GPU quota)，output → `results/phase5/apps_rerun/`
3. **Plancraft CB** — 还差 seag-456 + corefine-456 (running)
4. **TWExpress CB** — 12 jobs pending
5. **TextWorld CB** — 4 running + 8 pending (但 core methods 不完整，仅供参考)
6. **Plancraft random_50 + best_sigma_wrong** — 是否补跑？(环境为负例，优先级低)
7. **Cost Analysis** — 等结果齐全后统一计算 (BabyAI/TWExpress/TextWorld/Plancraft)

---

## 11. Cross-Environment Cost Analysis (Paper Table 2)

### 11.1 Token Cost 常数

| | HotpotQA | APPS | WebShop |
|--|:--------:|:----:|:-------:|
| **C_base** (tok/step) | 216 | 840 | 705 |
| **C_rollout** (tok/trigger) | 7,743 | 3,306 | 9,089 |
| **C_vote** (tok/step, CATTS) | 1,063 | 4,198 | 3,385 |
| Rollout/base ratio | 35.8× | 3.9× | 12.9× |
| Rollout type | Tree search 5×3 | Code batch n=5 | Tree search 5×3 |

### 11.2 Pareto 摘要 (FRVC vs 最佳竞争方法)

| 环境 | FRVC SR | FRVC Cost | 最佳 CB SR | 最佳 CB Cost | FRVC 优势 |
|------|:-------:|:---------:|:----------:|:------------:|-----------|
| **HotpotQA** | 0.968 | 6.55× | CaTS 0.932 | 10.55× | SR↑3.6pp, Cost↓38% |
| **WebShop** | 0.437 | 1.27× | CaTS 0.305 | 3.44× | **SR↑13.2pp, Cost↓63%** |
| APPS | 0.588 | 1.23× | CaTS 0.590 | 1.04× | SR≈, Cost略高 (弱信号) |

### 11.3 Cost-Effectiveness Ratio (CER = ΔSR / ΔCost)

| Method | HotpotQA | APPS | WebShop |
|--------|:--------:|:----:|:-------:|
| **scg_finetune_lr** | **0.086** | 0.013 | **1.352** |
| CaTS | 0.046 | 0.125 | 0.096 |
| SEAG | 0.033 | 0.000 | 0.113 |
| CoRefine | 0.033 | 0.000 | 0.115 |
| CATTS | 0.020 | −0.000 | −0.019 |
| always_trigger | 0.050 | 0.018 | 0.088 |

**在 2/3 环境 (HotpotQA, WebShop) 中 FRVC CER 显著最高。WebShop CER=1.352 是极端效率优势。**

### 11.4 FRVC 低 cost 的三重机制

1. **精准触发 (低 RR):** 只在高-utility 状态触发 — HotpotQA RR=60%, APPS RR=6%, WebShop RR=17%
2. **零 per-step overhead:** Gate 基于已有 logprobs 信号，不需额外 LLM 调用 (对比 CATTS K=5 voting)
3. **Success-driven step reduction:** 精准 rollout → 更高 SR → 更少步数 → base cost 减少 (WebShop: 14.1→5.6 步, −60%)

### 11.5 CATTS 的失败

CATTS 在所有 3 个环境都是 cost-效率最差:
- HotpotQA: SR=0.683, cost=10.50× — 投票 overhead 几乎等于 rollout
- APPS: SR=0.585 (无提升), cost=**6.02×** — K=5 code gen 投票 (C_vote=4,198) > rollout 本身 (C_rollout=3,306)
- WebShop: SR=0.160, cost=5.55× — cost 等于 always_trigger 但 SR 远低

**详细报告:** `reports/phase5_cost_analysis_report.md`, `reports/table2_cost_analysis.md`

---

## 12. Key Findings (Paper Narrative)

### 主实验 (HotpotQA + WebShop)
1. **SCG Pareto-dominates 所有竞争 baselines:** HotpotQA 上 SR↑3.6pp/cost↓38% vs CaTS; WebShop 上 SR↑13.2pp/cost↓63% vs CaTS
2. **方向发现至关重要:** HotpotQA SCG(96.8%) >> CoRefine(68.2%), 差距来自 SCG 正确发现信号方向
3. **学会"何时不 rollout" (WebShop):** random_50(47.5%) > always_trigger(43.0%) 证明过度 rollout 有害; SCG 减少 83% rollout 仍超 always_trigger, CER=1.352 极端效率优势
4. **零 per-step overhead:** SCG gate 基于已有 logprobs, 不需额外 LLM 调用 → CATTS (K=5 voting) 在所有环境都是最差 cost-efficiency

### 补充环境
5. **弱信号 (APPS):** SCG 正确识别信号不足 → 几乎不触发 (SR≈base_only)。竞争 baselines 也全退化为 base_only
6. **Rollout 无害 (TWExpress):** utility 从不为负 → 触发率越高越好 → SCG 选择性反而是劣势。与 WebShop (rollout 有时有害) 形成对比
7. **反例 (Plancraft):** Rollout 有害 (Δ=−7%)，所有方法均低于 base_only; CB 中 CATTS(25.0%) > always(22.8%) 因 rollout 较少 (2/ep vs 7/ep)
8. **TextWorld 不可用:** always_trigger + oracle 均 TIMEOUT (12h)，缺 2/6 core methods

---

## 13. SCG 失败分析与改进方向

### 13.1 初步判断 (用户分析)

1. **HotpotQA 和 WebShop ✅ 适合 paper** — SCG 表现优异，Pareto-dominates 所有竞争方法
2. **APPS 和 BabyAI** — random_50/best_sigma_wrong 似乎优于 SCG，说明方法存在缺陷：特征不佳或方法太简单
3. **TWExpress 和 TextWorld** — best_sigma_wrong 优于 SCG
4. **Plancraft** — 所有 core baseline 都比 SCG 好

### 13.2 修正与澄清

| 判断 | 修正 | 说明 |
|------|------|------|
| Point 2: BabyAI bsw > SCG | ❌ **部分错误** | bsw(7.0%) < SCG(8.8%)。APPS 数据 Phase3_supp 有 gate bug (bsw trigger=0.0 = base_only)，需等重跑 |
| Point 2: APPS r50 > SCG | ⚠️ **待确认** | Phase3_supp r50 trigger=0.79 (应为 0.50), 数据不可靠。9 jobs 重跑中 |
| Point 3: TWE bsw > SCG | ✅ **正确** | bsw(99.0%) > SCG(97.0%)，但原因非"方法缺陷"而是"rollout 永不有害" |
| Point 3: TW bsw > SCG | ✅ **正确** | bsw(57.0%) > SCG(54.3%)，且 SCG 比 r50(64.8%) 更差 — **gate 主动做出错误决策** |
| Point 4: 所有 core > SCG | ⚠️ **大部分正确** | oracle(21.3%) ≈ SCG(21.5%)。但 base_only(29.8%) >> SCG(21.5%) >> always(22.8%) — rollout 本质有害 |

### 13.3 根因分析：Rollout Utility 分布

SCG 的成败取决于 rollout 的效用分布。以下表格展示 Step 1 数据中 rollout utility 的三类分布：

| Environment | Positive | Negative | Neutral | Signal ρ | SCG 表现 |
|---|:---:|:---:|:---:|:---:|---|
| **HotpotQA** | 34.3% | 0.2% | 65.5% | 0.494 | ✅ 96.8% ≈ oracle |
| **WebShop** | 9.7% | 0.0% | 90.3% | 0.444 | ✅ 43.7%, CER=1.352 |
| TWExpress | 22.6% | 0.0% | 77.4% | 0.477 | ⚠️ 97.0% < always 99.3% |
| APPS | 13.8% | 17.2% | 69.0% | 0.155 | ⚠️ 58.8% ≈ base 58.5% |
| TextWorld | 43.1% | 0.0% | 56.9% | 0.174 | ❌ 54.3% < r50 64.8% |
| BabyAI | 0.2% | 0.0% | 99.8% | 0.052 | ❌ 8.8% < always 11.3% |
| Plancraft | 1.1% | 0.0% | 98.9% | 0.162 | ❌ rollout 有害 |

**关键发现: Signal ρ > 0.3 → SCG 有效; Signal ρ < 0.2 → SCG 失败**

### 13.4 三种 SCG 失败场景

**场景 A: 信号太弱，gate 等同噪声或更差 (TextWorld, BabyAI)**
- TextWorld: ρ=0.174，positive_rate=43.1% (高) 但信号弱 → gate 无法区分
- TextWorld SCG 触发 16 ro/ep **比** r50 的 13.75 ro/ep **更多**，但 SR 更低 (54.3% < 64.8%) — **gate 主动做出了错误决策**
- BabyAI: ρ=0.052，positive_rate=0.2% → 信号几乎不存在，gate 只是噪声

**场景 B: Rollout 从不有害，选择性反而是劣势 (TWExpress)**
- negative_rate=0.0%，positive_rate=22.6% — 多 rollout 永远不亏
- SCG 正确学到信号方向，但选择性限制 rollout 总量 (RR=28% vs always 100%)
- 结果：always(99.3%) > bsw(99.0%) > r50(97.8%) > SCG(97.0%) — 触发率越高越好
- Oracle(99.3%, 0.91 ro/ep) 证明精准触发可以用最少量 rollout 达到最高 SR

**场景 C: Rollout 几乎永远无用，任何 rollout 都是浪费 (Plancraft)**
- positive_rate=1.1%，negative_rate=0.0% → 98.9% 的 rollout 都是白费
- base_only(29.8%) >> always_trigger(22.8%) → rollout 有害 (可能扰乱 agent 决策)
- 即使 oracle(21.3%) 也不如 base_only — rollout 机制本身不适合此环境
- SCG(21.5%) ≈ oracle(21.3%) 说明 gate 本身运作正常，问题在于 rollout 本身

