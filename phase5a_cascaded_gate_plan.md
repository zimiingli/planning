# Phase 5A 实验方案：Cascaded Multi-Fidelity Gate

**版本**：v1.0（2026-03-01）
**核心问题**：能否用多级 cascade 结构，让大多数 step 用廉价信号快速决策，仅在模糊情况下 escalate 到更昂贵的判断？
**前置依赖**：Phase 0-4 全部完成，3 个有效环境（HotpotQA + APPS + WebShop）
**代码位置**：UConn HPC `frvc/` 目录下新增模块

---

## 核心动机

当前 SCG-FineTune(LR) 在每一步都提取手工 feature → 跑 LR 分类。问题：
1. **Feature 是手工的**：每个环境需要人工定义信号（evidence_count, state_category 等）
2. **Model 太简单**：LR 的 methodology contribution 弱
3. **成本一刀切**：每步 gate 决策的"精度需求"不同，但用的是同一个模型

Cascaded Gate 的思路：**不是所有 step 都需要同等精度的决策**。

```
大多数 step（~60-70%）→ 廉价信号即可判断 → Level 0（几乎零开销）
部分 step（~20-30%）  → 需要 LLM 内部信息 → Level 1（hidden state probe）
少数 step（~5-10%）   → 信号不足，直接试 → Level 2（short trial rollout）
```

---

## 缩写补充

| 缩写 | 全称 | 含义 |
|------|------|------|
| **L0** | Level 0 | 廉价信号 gate（entropy, step_count 等已有信号 + uncertainty 输出）|
| **L1** | Level 1 | Hidden-state VOC probe（LLM 最后一层 hidden state → MLP → VOC 估计）|
| **L2** | Level 2 | Trial rollout（实际执行 1-2 步 rollout 直接观测 VOC）|
| **VOC** | Value of Computation | 触发 optimizer 的预期价值 = E[U(T, s)] |
| **esc%** | Escalation Rate | 从当前 level escalate 到下一级的比例 |
| **conf** | Confidence | 模型对当前预测的确定度，由预测 variance 决定 |

---

## 状态速览

| 阶段 | 状态 | 目标 |
|------|------|------|
| **5A.0：Hidden State 基础设施** | ⏳ 待开始 | 在现有 pipeline 中保存 LLM hidden states |
| **5A.1：Level 0 实现与验证** | ⏳ 待开始 | 廉价信号 gate + uncertainty 估计 |
| **5A.2：Level 1 实现与验证** | ⏳ 待开始 | Hidden-state VOC probe |
| **5A.3：Cascade 集成** | ⏳ 待开始 | L0 + L1 + L2 联合训练/调参 |
| **5A.4：Full Evaluation** | ⏳ 待开始 | 3 环境 × 3 seeds 完整实验 |
| **5A.5：Analysis** | ⏳ 待开始 | Escalation profile + ablation + 对比 |

---

## Phase 5A.0：Hidden State 基础设施

### 做什么

在现有 experiment pipeline 中添加 hidden state 提取和保存功能。**这是 Plan A 和 Plan B 的共享前置步骤**。

### 实现细节

**修改文件**：`frvc/envs/` 下所有环境文件 + vLLM 推理接口

**方案**：在 LLM generate action 时，同时保存最后一层 hidden state。

```python
# 修改 LLM 推理接口（vLLM 方案）
# vLLM 默认不返回 hidden states，需要改用 HuggingFace 接口提取

# 方案 1（推荐）：用 HuggingFace 接口单独提取 hidden state
# 只在需要 hidden state 的 step 调用，不影响 vLLM 主推理

def extract_hidden_state(model, tokenizer, state_text, device="cuda"):
    """
    从 Qwen3-4B 提取最后一层 hidden state。

    输入：state_text (str) — 当前环境状态的文本表示
    输出：h (np.ndarray, shape=(d_model,)) — 最后一层 mean-pooled hidden state

    d_model = 2560 for Qwen3-4B
    """
    inputs = tokenizer(state_text, return_tensors="pt",
                       truncation=True, max_length=2048).to(device)
    with torch.no_grad():
        outputs = model(
            **inputs,
            output_hidden_states=True,
            return_dict=True
        )
    # 最后一层 hidden state, mean pooling over token dimension
    last_hidden = outputs.hidden_states[-1]  # (1, seq_len, d_model)
    h = last_hidden.mean(dim=1).squeeze(0).cpu().numpy()  # (d_model,)
    return h

# 方案 2（备选）：用 vLLM 的 prompt logprobs 接口提取 logit-level 特征
# 开销更低但信息量不如完整 hidden state
```

**保存格式**：

```python
# 扩展 CalibrationPoint
CalibrationPointV2 = namedtuple('CalibrationPointV2', [
    'signals',        # Dict: 原有手工信号
    'hidden_state',   # np.ndarray: shape (d_model,), d_model=2560 for Qwen3-4B
    'action',         # str
    'utility',        # float
    'reward',         # float
    'timestamp',      # int
])

# 保存到 .npz 文件（hidden states 太大不适合 JSON）
np.savez_compressed(
    f"results/phase5a_{env}/hidden_states_{seed}.npz",
    hidden_states=np.stack(all_hidden_states),  # (N_steps, d_model)
    utilities=np.array(all_utilities),           # (N_steps,)
    signals=signal_array,                        # (N_steps, n_signals)
    metadata=metadata_dict
)
```

**数据量估算**：

| 环境 | Episodes | Steps/Ep | 总 Steps | Hidden State Size | 总存储 |
|------|---------|----------|----------|-------------------|--------|
| HotpotQA | 200 | ~5 | ~1,000 | 2560 × 4B = 10KB | ~10MB |
| APPS | 200 | ~5 | ~1,000 | 2560 × 4B = 10KB | ~10MB |
| WebShop | 200 | ~10 | ~2,000 | 2560 × 4B = 10KB | ~20MB |
| **总计** | — | — | ~4,000 | — | **~40MB** |

存储开销极低，完全可行。

### 判断标准

```
✅ GO：hidden state 成功提取且保存，维度正确 (d_model=2560)
❌ BLOCK：vLLM 不支持 hidden state 输出 → 切换到方案 1（HuggingFace 额外推理）
```

### 时间估算

- 代码修改：1-2 天
- 数据收集（3 环境 × 200 ep）：复用已有 episode 轨迹，只需重放 state → 提取 hidden state。约 2-4 GPU 小时
- 总计：**2-3 天**

---

## Phase 5A.1：Level 0 — 廉价信号 Gate with Uncertainty

### 做什么

基于现有手工信号（token_entropy, step_count, evidence_count 等），训练一个能输出 **VOC 估计 + uncertainty** 的轻量模型。

### 核心创新点

当前 LR 只输出 P(trigger)——一个 binary 决策。Level 0 输出的是 **(VOC_mean, VOC_var)**——连续的 VOC 估计 + 不确定性。这让它能判断 "我不确定" 然后 escalate。

### 实现

**方案 A（推荐）：Bayesian Logistic Regression on signals**

```python
# 使用 sklearn 的 BayesianRidge 做 VOC regression（不是分类！）
from sklearn.linear_model import BayesianRidge

class Level0Gate:
    """
    Level 0: 在廉价手工信号上做 Bayesian VOC regression。
    输出 VOC 预测值 + 不确定性（posterior variance）。
    """
    def __init__(self, confidence_threshold=0.8):
        self.model = BayesianRidge(
            alpha_1=1e-6, alpha_2=1e-6,
            lambda_1=1e-6, lambda_2=1e-6
        )
        self.confidence_threshold = confidence_threshold
        self.is_fitted = False

    def fit(self, X_signals, U_utilities):
        """
        X_signals: (N, n_features) — 手工信号特征矩阵
        U_utilities: (N,) — utility 值（连续，非 binary）
        """
        self.model.fit(X_signals, U_utilities)
        self.is_fitted = True

    def predict(self, x_signal):
        """
        返回 (voc_mean, voc_std, confident)
        """
        voc_mean, voc_std = self.model.predict(
            x_signal.reshape(1, -1), return_std=True
        )
        # 判断是否 confident：
        # 如果 VOC 的均值距离 λ* 足够远（相对于 std），就是 confident
        # 使用 z-score: |voc_mean - lambda_star| / voc_std > z_threshold
        z_score = abs(voc_mean[0] - self.lambda_star) / (voc_std[0] + 1e-8)
        confident = z_score > 1.5  # ≈ 87% confidence

        return voc_mean[0], voc_std[0], confident

    def decide(self, x_signal, lambda_star):
        """
        返回 (decision, confident, voc_mean)
        decision: True=trigger, False=skip, None=escalate
        """
        voc_mean, voc_std, confident = self.predict(x_signal)

        if confident:
            return (voc_mean > lambda_star), True, voc_mean
        else:
            return None, False, voc_mean  # escalate to Level 1
```

**方案 B（备选）：Ensemble of small models**

```python
# 训练 M=10 个 LR（bootstrap sampling），用预测方差作为 uncertainty
class Level0Ensemble:
    def __init__(self, n_models=10):
        self.models = [LogisticRegression() for _ in range(n_models)]

    def fit(self, X, U):
        for i, model in enumerate(self.models):
            # Bootstrap sample
            idx = np.random.choice(len(X), len(X), replace=True)
            model.fit(X[idx], (U[idx] > 0).astype(int))

    def predict(self, x):
        probs = [m.predict_proba(x.reshape(1,-1))[0, 1] for m in self.models]
        return np.mean(probs), np.std(probs)
```

### 验证实验

在 Phase 1-3 已有数据上（不需要新 episode）：

| 实验 | 目的 | 数据 |
|------|------|------|
| L0 VOC accuracy | VOC 预测的 MSE / R² | 各环境 calibration data |
| L0 confidence calibration | 模型说 "confident" 时准确率多少 | 各环境，看 confident=True 时的 gate accuracy |
| L0 escalation rate | 多少比例的 step 被判为 "不确定" | 各环境 |
| L0 vs 当前 LR | 在 confident 子集上，L0 gate accuracy 是否 ≥ LR | 各环境 |

### 判断标准

```
✅ GO：
  - L0 confident 子集 gate accuracy ≥ 当前 LR 的全集 accuracy
  - L0 escalation rate 在 20-40%（太低说明不需要 L1，太高说明 L0 没用）

⚠️ MODERATE：
  - escalation rate > 50% → L0 信号太弱，cascade 主要靠 L1
  → 仍可继续，但 cascade 的成本优势减弱

❌ NO-GO：
  - L0 confident 子集 accuracy < LR 全集 accuracy
  → L0 的 uncertainty 估计不可靠，回退到 flat L1
```

### 时间估算

- 实现：1 天（Bayesian Ridge + confidence 判断逻辑）
- 验证（在已有数据上）：0.5 天
- 总计：**1.5 天**

---

## Phase 5A.2：Level 1 — Hidden-State VOC Probe

### 做什么

用 LLM hidden state 训练一个 VOC probe，作为 Level 0 escalate 后的更精确判断。

### 实现

```python
class Level1VOCProbe(nn.Module):
    """
    Level 1: 2-layer MLP on frozen LLM hidden states → VOC estimate。

    关键设计决策：
    - 预测 VOC（连续值），不是 P(trigger)（binary）
    - 输出 (mean, logvar) 用于 uncertainty 估计
    - 在 calibration data 上训练，<10 秒
    """
    def __init__(self, d_model=2560, d_hidden=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_hidden),
            nn.LayerNorm(d_hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_hidden, d_hidden // 2),
            nn.ReLU(),
            nn.Linear(d_hidden // 2, 2)  # [voc_mean, voc_logvar]
        )

    def forward(self, h):
        """
        h: (batch, d_model) — LLM hidden states
        Returns: voc_mean (batch,), voc_logvar (batch,)
        """
        out = self.net(h)
        return out[:, 0], out[:, 1]

    def predict_with_uncertainty(self, h, lambda_star):
        voc_mean, voc_logvar = self.forward(h)
        voc_std = torch.exp(0.5 * voc_logvar)

        # P(VOC > λ*) under Gaussian assumption
        z = (lambda_star - voc_mean) / (voc_std + 1e-8)
        prob_helpful = 1 - torch.distributions.Normal(0, 1).cdf(z)

        return voc_mean, voc_std, prob_helpful

# 训练
def train_level1(hidden_states, utilities, epochs=100, lr=1e-3):
    """
    hidden_states: (N, d_model) — 从 Phase 5A.0 收集的数据
    utilities: (N,) — 对应的 U 值
    """
    dataset = TensorDataset(
        torch.tensor(hidden_states, dtype=torch.float32),
        torch.tensor(utilities, dtype=torch.float32)
    )
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    model = Level1VOCProbe(d_model=hidden_states.shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    for epoch in range(epochs):
        for h_batch, u_batch in loader:
            voc_mean, voc_logvar = model(h_batch)

            # Gaussian NLL loss: 同时学 mean 和 variance
            loss = 0.5 * (voc_logvar + (u_batch - voc_mean)**2 / torch.exp(voc_logvar))
            loss = loss.mean()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    return model
```

**参数量**：2560 × 256 + 256 × 128 + 128 × 2 ≈ **690K 参数**。训练 < 10 秒。

### 验证实验

| 实验 | 目的 | 预期 |
|------|------|------|
| L1 VOC regression 质量 | R² on held-out data | R² > 0.3（VOC 可预测） |
| L1 vs LR-HandCraft (gate accuracy) | hidden state 是否比手工信号更好 | L1 ≥ LR（hidden state 信息量更大） |
| L1 vs LR-HandCraft (SR/CS) | 端到端性能 | L1 SR ≥ LR SR，且 CS 相当 |
| L1 uncertainty calibration | 预测的 variance 是否准确 | ECE < 0.1 |
| L1 跨环境：相同架构不同权重 | 架构通用性 | 3 环境都能训练成功 |

### 判断标准

```
✅ GO：
  - L1 gate accuracy ≥ LR-HandCraft 在至少 2/3 环境
  - 或 L1 ≈ LR 但不需要手工 feature（自动化优势）

⚠️ MODERATE：
  - L1 < LR 在 1-2 个环境
  → 可能 hidden state 需要更好的 pooling（CLS token vs mean vs last token）
  → 尝试不同 pooling 策略

❌ NO-GO：
  - L1 << LR 在所有环境
  → hidden state 不编码 VOC 信息，放弃 hidden state 路线
  → 回退到手工信号 + 更好的 uncertainty（仅 L0 + L2，跳过 L1）
```

### 关键消融

| 消融 | 变量 | 预期结果 |
|------|------|---------|
| Pooling 策略 | mean / last_token / CLS | 预期 last_token 或 mean 最好 |
| Hidden layer 选择 | last / second-to-last / average | 预期 last 最好 |
| 模型大小 | d_hidden ∈ {64, 128, 256, 512} | 预期 128-256 足够 |
| 训练数据量 | N ∈ {50, 100, 200, 500} | 预期 200+ 就饱和 |

### 时间估算

- 实现：1-2 天
- 训练 + 验证（3 环境）：1 天
- 消融实验：1 天
- 总计：**3-4 天**

---

## Phase 5A.3：Cascade 集成

### 做什么

将 L0 + L1 + L2 组合为完整的 Cascaded Gate，实现联合决策逻辑。

### 实现

```python
class CascadedGate(SCGBase):
    """
    三级 cascade gate：
    L0 (cheap signals) → L1 (hidden state probe) → L2 (trial rollout)

    每级输出 (VOC_mean, VOC_std)。
    如果 confident（|VOC - λ*| / std > z_threshold），在该级决策。
    否则 escalate 到下一级。
    """

    def __init__(self, env_name, lambda_star,
                 z_threshold_l0=1.5, z_threshold_l1=1.0,
                 trial_rollout_steps=1):
        super().__init__(env_name)
        self.lambda_star = lambda_star
        self.z_threshold_l0 = z_threshold_l0
        self.z_threshold_l1 = z_threshold_l1
        self.trial_rollout_steps = trial_rollout_steps

        self.level0 = Level0Gate(confidence_threshold=z_threshold_l0)
        self.level1 = Level1VOCProbe(d_model=2560)
        # Level 2 不需要训练，直接执行 trial rollout

        # 统计
        self.level_counts = {0: 0, 1: 0, 2: 0}

    def train(self, signals_data, hidden_states, utilities):
        """
        用 calibration data 训练 L0 和 L1。

        signals_data: (N, n_signals) — 手工信号
        hidden_states: (N, d_model) — LLM hidden states
        utilities: (N,) — utility 值
        """
        # L0: Bayesian Ridge on signals → VOC
        self.level0.fit(signals_data, utilities)
        self.level0.lambda_star = self.lambda_star

        # L1: MLP on hidden states → VOC
        self.level1 = train_level1(hidden_states, utilities)

    def decide(self, signals, hidden_state, env=None, proposer=None):
        """
        Cascaded decision：L0 → L1 → L2。

        Returns: (trigger: bool, level_used: int, voc_estimate: float)
        """
        # === Level 0: Cheap signals ===
        x_signal = self.build_features(signals)
        decision_l0, confident_l0, voc_l0 = self.level0.decide(
            x_signal, self.lambda_star
        )

        if confident_l0:
            self.level_counts[0] += 1
            return decision_l0, 0, voc_l0

        # === Level 1: Hidden state probe ===
        h = torch.tensor(hidden_state, dtype=torch.float32).unsqueeze(0)
        voc_mean, voc_std, prob_helpful = self.level1.predict_with_uncertainty(
            h, self.lambda_star
        )

        z_score_l1 = abs(voc_mean.item() - self.lambda_star) / (voc_std.item() + 1e-8)

        if z_score_l1 > self.z_threshold_l1:
            self.level_counts[1] += 1
            return (voc_mean.item() > self.lambda_star), 1, voc_mean.item()

        # === Level 2: Trial rollout ===
        self.level_counts[2] += 1
        if env is not None and proposer is not None:
            # 执行 short trial rollout (1-2 步)
            trial_voc = self._trial_rollout(env, proposer,
                                             n_steps=self.trial_rollout_steps)
            return (trial_voc > self.lambda_star), 2, trial_voc
        else:
            # fallback: 用 L1 的 mean 做决策（不确定但没有 env access）
            return (voc_mean.item() > self.lambda_star), 2, voc_mean.item()

    def _trial_rollout(self, env, proposer, n_steps=1):
        """执行 short trial rollout 直接观测 VOC"""
        # 简化版 rollout：只跑 1 步，K=2 candidate actions
        state = env.get_current_state()
        candidates = proposer.propose_candidates(state, K=2)

        best_value = -float('inf')
        for action in candidates:
            env_copy = env.deepcopy()  # 需要 env 支持 deepcopy
            obs, reward, done, info = env_copy.step(action)
            best_value = max(best_value, reward)

        base_reward = env.get_expected_reward()  # 当前 base action 的预期 reward
        return best_value - base_reward

    def get_escalation_profile(self):
        """返回各级处理比例"""
        total = sum(self.level_counts.values())
        if total == 0:
            return {0: 0, 1: 0, 2: 0}
        return {k: v / total for k, v in self.level_counts.items()}
```

### Cascade 参数调优

| 参数 | 搜索范围 | 调优方式 |
|------|---------|---------|
| z_threshold_l0 | {1.0, 1.5, 2.0, 2.5} | Grid search on val set |
| z_threshold_l1 | {0.5, 1.0, 1.5, 2.0} | Grid search on val set |
| lambda_star | 来自 CMDP（已有） | 固定，不搜索 |
| trial_rollout_steps | {1, 2} | 固定 1（成本考虑） |

**调优目标**：最大化 TES（SR-CS 平衡），同时 L2 使用率 < 15%。

### 判断标准

```
✅ GO（强）：
  - Cascade SR ≥ LR-HandCraft SR 在 2/3 环境
  - Cascade 总计算成本 < LR-HandCraft（通过 L0 快速决策节省开销）
  - 或 Cascade SR > LR 且提供新的 analysis 维度（escalation profile）

✅ GO（弱）：
  - Cascade ≈ LR-HandCraft 在 SR 上
  - 但 Cascade 不需要手工 feature（自动化优势）
  - 且 escalation profile 提供了新 insight

❌ NO-GO：
  - Cascade SR << LR-HandCraft
  - 或 escalation 退化为 "几乎全部 L2"（cascade 形同虚设）
```

### 时间估算

- 实现 Cascade 集成：2 天
- 参数调优（grid search）：1 天
- 总计：**3 天**

---

## Phase 5A.4：Full Evaluation

### 做什么

在 3 个有效环境上，完整对比 CascadedGate 与所有 baseline。

### 实验矩阵

| 方法 | 描述 | 新/旧 |
|------|------|-------|
| base_only | 不触发 optimizer | ✅ 已有 |
| always_trigger | 每步触发 | ✅ 已有 |
| random_50 | 50% 随机触发 | ✅ 已有 |
| oracle | 只在 U>0 时触发 | ✅ 已有 |
| **SCG-LR (hand-craft)** | 当前最佳方法 | ✅ 已有 |
| **L1-only (hidden state probe)** | 只用 L1，无 cascade | 🆕 新增 |
| **Cascade (L0+L1)** | L0 + L1，无 trial rollout | 🆕 新增 |
| **Cascade (L0+L1+L2)** | 完整 cascade | 🆕 新增 |

**每种方法 × 3 环境 × 3 seeds = 新增 4 × 3 × 3 = 36 runs**

加上已有数据中可复用的 baseline，总计不需要重跑 base/always/random/oracle。

### 评价指标

| 指标 | 公式 | 含义 |
|------|------|------|
| SR | 成功率 | 主指标 |
| CS | 1 - gated_rollouts / always_rollouts | 成本节省 |
| TES | 2 × eff × eff / (eff + eff) | 效率综合 |
| **esc_profile** | (L0%, L1%, L2%) | 🆕 各级处理比例 |
| **avg_gate_cost** | Σ level_cost × level_freq | 🆕 加权平均 gate 决策成本 |
| VOC_R² | R² of VOC prediction | 🆕 VOC 预测质量 |

### Gate 决策成本定义

| Level | 每次成本 | 说明 |
|-------|---------|------|
| L0 | 1× | 基准（几个浮点运算） |
| L1 | 5× | hidden state 提取 + MLP forward |
| L2 | 100-500× | 实际 rollout（取决于 K 和 H） |

### 资源估算

| 环境 | Episodes/Run | Runs | GPU 时间/Run | 总 GPU 时间 |
|------|-------------|------|-------------|-------------|
| HotpotQA | 200 | 12 | ~1h | ~12h |
| APPS | 200 | 12 | ~2h | ~24h |
| WebShop | 200 | 12 | ~2h | ~24h |
| **总计** | — | 36 | — | **~60 GPU-hours** |

### 时间估算

- 实验跑完：3-5 天（并行跑 3 环境 × 4 方法）
- 结果分析：1-2 天
- 总计：**4-7 天**

---

## Phase 5A.5：Analysis

### 核心分析项

**1. Escalation Profile 跨环境对比（C2 新证据）**

```
预期发现：
  HotpotQA（强信号 ρ=−0.586）：L0 解决 ~70%, L1 ~25%, L2 ~5%
  APPS（弱信号 ρ=−0.274）：L0 解决 ~40%, L1 ~40%, L2 ~20%
  WebShop（分类信号 η²=0.598）：L0 解决 ~60%, L1 ~30%, L2 ~10%

解读：escalation profile 的差异反映了环境的 "gating difficulty"
  → 强信号环境廉价信号即可判断大多数 step
  → 弱信号环境需要更多 escalation
  → 这是 C2（信号环境依赖性）的新维度证据
```

**2. "Automatic vs Hand-Crafted" Ablation（关键 ablation）**

| 对比 | 含义 |
|------|------|
| SCG-LR (hand-craft) vs L1-only (hidden state) | 手工特征 vs 自动特征 |
| Cascade (L0+L1) vs L1-only | 多级有用吗？ |
| Cascade (L0+L1+L2) vs Cascade (L0+L1) | Trial rollout 有用吗？ |

**3. VOC 预测质量分析**

- L0 VOC R² vs L1 VOC R²：hidden state 能预测多少额外的 VOC variance
- VOC prediction error 与 gate accuracy 的关系

**4. 成本分析**

| 方法 | 每步平均成本 | SR | CS | TES |
|------|------------|-----|-----|-----|
| SCG-LR | 1× | [已有] | [已有] | [已有] |
| L1-only | 5× | [新] | [新] | [新] |
| Cascade | (1×·L0% + 5×·L1% + 300×·L2%) | [新] | [新] | [新] |

如果 Cascade 的加权成本 < L1-only 的成本（因为大部分 step 在 L0 解决），cascade 就有明确的 cost 优势。

### 可视化设计

| 图 | 内容 | 用于论文 |
|-----|------|---------|
| Fig A1 | Escalation profile bar chart (3 环境 × 3 levels) | Section 5 main result |
| Fig A2 | SR-CS Pareto front（加入 cascade 方法） | Section 5 main result |
| Fig A3 | VOC prediction scatter (predicted vs actual, L0 vs L1) | Section 5 ablation |
| Fig A4 | Gate cost breakdown (stacked bar: L0/L1/L2 contribution) | Section 5 或 appendix |
| Fig A5 | Confidence threshold sensitivity (z_threshold vs esc%) | Appendix |

### 时间估算

- 分析 + 可视化：2-3 天
- 总计：**2-3 天**

---

## 总体时间线

| 阶段 | 预计时间 | 累计 |
|------|---------|------|
| 5A.0 Hidden State 基础设施 | 2-3 天 | 2-3 天 |
| 5A.1 Level 0 | 1.5 天 | 3.5-4.5 天 |
| 5A.2 Level 1 | 3-4 天 | 6.5-8.5 天 |
| 5A.3 Cascade 集成 | 3 天 | 9.5-11.5 天 |
| 5A.4 Full Evaluation | 4-7 天 | 13.5-18.5 天 |
| 5A.5 Analysis | 2-3 天 | **15.5-21.5 天** |

**总计：约 3-4 周**

### 早期 Kill Switch

```
Phase 5A.2 结束后（~8 天）做 GO/NO-GO 判断：
  如果 L1 (hidden state probe) << LR-HandCraft → 整个 cascade 路线 NO-GO
  因为 cascade 的价值前提是 L1 至少不输 LR

Phase 5A.1 结束后（~4 天）做快速判断：
  如果 L0 escalation rate > 80% → L0 几乎没用，cascade 退化为 L1-only
  → 仍可继续（L1-only 本身也是有价值的），但 cascade 创新点弱化
```

---

## 风险评估

| 风险 | 严重性 | 应对 |
|------|--------|------|
| Hidden state 不编码 VOC 信息 | 🔴 高 | Phase 5A.2 early kill。回退到手工信号 + Bayesian uncertainty |
| L0 escalation rate 太高（>80%） | 🟡 中 | L0 信号弱不影响 L1 独立价值。cascade 退化为 L1-only |
| L2 trial rollout 成本过高 | 🟡 中 | 限制 L2 使用率 < 10%。或完全去掉 L2（只用 L0+L1） |
| Cascade 不优于单层 L1 | 🟡 中 | cascade 的额外价值是 cost（L0 更便宜），不一定是 accuracy |
| vLLM 不支持 hidden state 提取 | 🟢 低 | 用 HuggingFace 接口单独提取（多一次 forward pass） |
| WebShop env.deepcopy 不支持 L2 | 🟢 低 | WebShop 已验证支持 deepcopy。APPS 不需要（代码执行即可） |

---

## 论文中的定位

**如果 Phase 5A 成功**，论文 Method Section 的结构：

```
4.1 Problem: VOC estimation for adaptive triggering
4.2 Level 0: Cheap-signal Bayesian gate (existing signals, but with uncertainty)
4.3 Level 1: Hidden-state VOC probe (automatic features, no hand-crafting)
4.4 Cascade integration (multi-fidelity decision with escalation)
4.5 λ* from CMDP (已有理论基础)
```

**核心 selling point**：
1. **不需要手工 feature**：L1 用 hidden state，完全自动
2. **成本可控**：cascade 让大多数决策在 L0 快速完成
3. **VOC estimation + CMDP threshold**：比 binary classification 更 principled
4. **Escalation profile**：新的分析维度，提供 C2 的额外证据

**如果 Phase 5A 部分成功**（L1 work，cascade 不优于 L1-only）：

```
退化方案：只用 L1 (Hidden-State VOC Probe) + CMDP threshold
仍然有：自动 feature + VOC regression + 理论 threshold
缺少：cascade 的 cost 优势
→ 可接受的论文，但 methodology contribution 弱一级
```
