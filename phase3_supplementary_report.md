# Phase 3 第二次补充实验报告 (基于当前 README)

## 1. 实验设置 (Experimental Settings)

根据当前 `README.md` 的规划，本次实验旨在完成 Phase 3 的补充分析（S0）以及在新的有效环境（MBPP, HumanEval）上的验证（S2），并进行 CMDP 实验（S3）。

- **模型 (Model)**: `Qwen/Qwen3-4B-Instruct-2507` (注：根据实际运行脚本，未使用 0.6B 模型，而是继续使用了 4B 模型)
- **环境 (Environments)**: HotpotQA, MBPP, HumanEval
- **评估指标 (Metrics)**:
  - **SR (Success Rate)**: 任务成功率
  - **RR (Rollout Rate)**: 触发 Rollout 的比例
  - **CS (Cost Saving)**: 相比于 `always_trigger` 节省的成本 ($1 - RR_{method} / RR_{always}$)
  - **TES (Task-Efficiency Score)**: 综合有效性 (Effectiveness) 和效率 (Efficiency) 的调和平均数
- **对比方法 (Methods)**:
  - `base_only`: 不使用任何 Rollout
  - `always_trigger`: 每步都触发 Rollout
  - `random_50`: 50% 概率随机触发
  - `best_sigma_wrong`: 使用错误的信号方向触发
  - `scg_finetune_lr`: 核心方法 (基于逻辑回归的门控网络)
  - `oracle`: 理想情况下的最优触发

## 2. 实验详细结果 (Detailed Results)

### 2.1 S0 & S2: 核心指标分析 (SR / RR / CS / TES)

以下结果为 3 个随机种子 (seeds) 的均值和标准差 (mean±std)。

#### Environment: HotpotQA
| Method | SR (%) | RR (%) | CS (%) | TES |
|---|---|---|---|---|
| base_only | 49.0 ± 1.9 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.000 ± 0.000 |
| always_trigger | 97.0 ± 0.4 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.000 ± 0.000 |
| random_50 | 89.0 ± 0.8 | 51.4 ± 2.3 | 48.6 ± 2.3 | 0.614 ± 0.021 |
| best_sigma_wrong | 58.2 ± 2.5 | 49.9 ± 1.2 | 50.1 ± 1.2 | 0.277 ± 0.022 |
| **scg_finetune_lr** | **96.7 ± 0.6** | **55.9 ± 5.5** | **44.1 ± 5.5** | **0.609 ± 0.053** |
| oracle | 97.0 ± 0.4 | 33.0 ± 2.3 | 67.0 ± 2.3 | 0.802 ± 0.017 |

**分析**: 在 HotpotQA 上，`scg_finetune_lr` 成功保持了接近 `always_trigger` 的高成功率 (96.7%)，同时实现了 **44.1%** 的成本节省 (CS > 20% 的预期目标)，TES 达到 0.609 (满足 > 0.50 的 STRONG GO 判定标准)。

#### Environment: MBPP
| Method | SR (%) | RR (%) | CS (%) | TES |
|---|---|---|---|---|
| base_only | 92.7 ± 1.4 | 0.0 ± 0.0 | 100.0 ± 0.0 | 1.000 ± 0.000 |
| always_trigger | 92.7 ± 1.4 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.000 ± 0.000 |
| best_sigma_wrong | 92.7 ± 1.4 | 74.8 ± 3.5 | 25.2 ± 3.5 | 0.401 ± 0.045 |
| **scg_finetune_lr** | **92.7 ± 1.4** | **22.1 ± 3.3** | **77.9 ± 3.3** | **0.875 ± 0.021** |
| oracle | 92.7 ± 1.4 | 24.6 ± 4.5 | 75.4 ± 4.5 | 0.859 ± 0.029 |

#### Environment: HumanEval
| Method | SR (%) | RR (%) | CS (%) | TES |
|---|---|---|---|---|
| base_only | 92.1 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 0.667 ± 0.471 |
| always_trigger | 92.3 ± 0.3 | 100.0 ± 0.0 | 0.0 ± 0.0 | 0.000 ± 0.000 |
| random_50 | 92.3 ± 0.3 | 53.0 ± 5.1 | 47.0 ± 5.1 | 0.429 ± 0.307 |
| best_sigma_wrong | 92.3 ± 0.3 | 75.9 ± 0.5 | 24.1 ± 0.5 | 0.257 ± 0.182 |
| **scg_finetune_lr** | **92.7 ± 0.8** | **13.3 ± 7.4** | **86.7 ± 7.4** | **0.661 ± 0.399** |
| oracle | 92.5 ± 0.3 | 10.8 ± 0.8 | 89.2 ± 0.8 | 0.943 ± 0.004 |

**代码环境 (MBPP & HumanEval) 分析**: 
在这两个代码环境中，模型表现出了明显的 **天花板效应 (Ceiling Effect)**。`base_only` 的 SR 已经高达 92% 以上，导致 `always_trigger` 几乎无法带来额外的性能提升。
尽管如此，`scg_finetune_lr` 依然能够准确识别出绝大多数步骤不需要 Rollout，从而在保持高 SR 的同时，实现了极高的成本节省（MBPP CS=77.9%, HumanEval CS=86.7%）。

### 2.2 S3: CMDP 跨环境对比 (Lagrangian Dual Ascent)

针对不同的目标成本节省率 (CS Target)，使用 Lagrangian Dual Ascent 算法求解最优的拉格朗日乘子 $\lambda^*$。

| CS Target | HotpotQA $\lambda^*$ | HumanEval $\lambda^*$ | MBPP $\lambda^*$ |
|---|---|---|---|
| 30% (0.3) | 0.000 | 0.000 | 0.000 |
| 40% (0.4) | 0.000 | 0.000 | 0.000 |
| 50% (0.5) | 0.056 | 0.000 | 0.000 |
| 60% (0.6) | 0.140 | 0.000 | 0.000 |
| 70% (0.7) | 0.144 | 0.000 | 0.000 |

**分析**:
- 在 **HotpotQA** 中，随着 CS Target 的提高（要求节省更多成本），$\lambda^*$ 逐渐增大（从 0.0 增加到 0.144），这表明系统需要施加更大的惩罚来抑制 Rollout 的触发，符合 CMDP 的理论预期。
- 在 **HumanEval 和 MBPP** 中，$\lambda^*$ 始终为 0.0。这是因为在这两个环境中，模型本身的自然 Rollout 率（RR）已经非常低（例如 MBPP 的 RR 仅为 22.1%，即 CS 已经达到了 77.9%）。因此，即使 CS Target 设定为 70%，系统也无需施加额外的惩罚（$\lambda^*=0$）即可满足约束条件。

## 3. 结论与下一步建议

1. **HotpotQA 结果达标**: `scg_finetune_lr` 在 HotpotQA 上表现优异，CS > 20% 且 TES > 0.50，满足了 Phase 3 的 STRONG GO 条件。
2. **代码环境的天花板效应**: MBPP 和 HumanEval 的 `base_only` SR 过高（>85%），触发了 README 中 S2-A0 的 NO-GO 条件。虽然门控网络在这些环境中成功实现了极高的 CS，但由于缺乏性能提升空间，无法充分展示 Rollout 的有效性。
3. **下一步行动**: 根据 README 的决策树，由于 MBPP 和 HumanEval 的 base SR ≥ 85%，建议 **转方案 B (APPS) 或方案 D (GSM8K)**，以寻找具有更大操作空间（base SR 较低）的有效环境进行后续验证。
