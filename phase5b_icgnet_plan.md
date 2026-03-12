# Phase 5B 实验方案：In-Context Gating Network (ICGNet)

**版本**：v1.0（2026-03-01）
**核心问题**：能否训练一个网络，让它从 calibration data 中"学会如何 gate"——换环境时只换 context 不换权重？
**前置依赖**：Phase 0-4 全部完成，3 个有效环境（HotpotQA + APPS + WebShop）
**代码位置**：UConn HPC `frvc/` 目录下新增模块

---

## 核心动机

当前方法的根本局限：

```
当前 SCG-LR 在新环境中的 pipeline：
  1. 人工定义信号（需要 domain knowledge）  ← 不可扩展
  2. 跑 calibration episodes 收集数据         ← OK
  3. 训练 LR                                ← 太简单
  4. 部署 gate                               ← OK

理想的 pipeline：
  1. 跑 calibration episodes 收集数据         ← OK
  2. 将 calibration data 作为 "context" 输入给 gate
  3. Gate 自动发现 what signals matter + which direction
  4. 直接做 gate 决策                         ← 零人工干预
```

**ICGNet 的核心 idea**：Gate 不是一个训练好的固定函数 f(x; θ)，而是一个**条件函数** f(x; calibration_data)。

```
传统 gate:   calibration_data → [训练阶段] → 固定权重 θ → f(x; θ) → decision
ICGNet:      f(x, calibration_data) → decision（一次 forward pass 完成"学习"+决策）
```

这相当于让网络**在 forward pass 中完成 "learning from calibration data"**——本质是 in-context learning，但用的不是 LLM，而是一个专门为 gating 设计的小型 attention 网络。

---

## 缩写补充

| 缩写 | 全称 | 含义 |
|------|------|------|
| **ICGNet** | In-Context Gating Network | 从 calibration context 中学习 gate 策略的网络 |
| **calib set** | Calibration Set | (hidden_state, utility) 对的集合，作为 ICGNet 的 context 输入 |
| **query** | Query Point | 当前需要做 gate 决策的 state |
| **LOO** | Leave-One-Out | 训练时留出一个环境，用于测试跨环境泛化 |
| **N_c** | Calibration Set Size | calib set 中的样本数（关键超参） |
| **d_proj** | Projection Dimension | hidden state 投影到的低维空间 |

---

## 状态速览

| 阶段 | 状态 | 目标 |
|------|------|------|
| **5B.0：Hidden State 基础设施** | ⏳ 待开始 | 与 Plan A 共享：保存 LLM hidden states |
| **5B.1：ICGNet 架构实现** | ⏳ 待开始 | 实现 ICGNet 核心架构 + 训练 pipeline |
| **5B.2：Per-Environment 验证** | ⏳ 待开始 | 在每个环境内，ICGNet 是否 ≥ LR |
| **5B.3：Cross-Environment Meta-Training** | ⏳ 待开始 | 跨环境 meta-training + LOO 评估 |
| **5B.4：Full Evaluation** | ⏳ 待开始 | 3 环境 × 3 seeds 完整实验 |
| **5B.5：Analysis** | ⏳ 待开始 | Attention 可视化 + calibration size ablation + 对比 |

---

## Phase 5B.0：Hidden State 基础设施（与 Plan A 共享）

与 Phase 5A.0 完全相同。保存每个 step 的 LLM hidden state。

**详见 `phase5a_cascaded_gate_plan.md` Phase 5A.0**

**输出**：每个环境一个 `.npz` 文件，包含 hidden_states (N, d_model=2560) + utilities (N,) + signals (N, n_signals)

**时间估算**：2-3 天

---

## Phase 5B.1：ICGNet 架构实现

### 核心架构

```python
import torch
import torch.nn as nn

class InContextGatingNet(nn.Module):
    """
    In-Context Gating Network:
    从 calibration data 中学习如何做 gate 决策。

    输入：
    - calibration set: {(h_1, U_1), ..., (h_N, U_N)}
    - query: h_query

    输出：
    - VOC estimate for query
    - uncertainty estimate

    核心机制：
    1. 将 calibration (h, U) 编码为 context tokens
    2. Self-attention over context → 发现 calibration 中的 pattern（方向、信号重要性）
    3. Cross-attention: query attends to context → 利用发现的 pattern 做预测

    关键特性：
    - 权重在 meta-training 后固定
    - 换环境 = 换 calibration set（不需要重新训练）
    - Attention weights 可解释（看 query 在参考哪些 calibration examples）
    """

    def __init__(self, d_model=2560, d_proj=128, n_heads=4, n_layers=2,
                 dropout=0.1):
        super().__init__()

        self.d_proj = d_proj

        # === Module 1: State Projector ===
        # 将 high-dim hidden state 投影到 low-dim 空间
        # d_model (2560) → d_proj (128)
        self.state_proj = nn.Sequential(
            nn.Linear(d_model, d_proj * 2),
            nn.LayerNorm(d_proj * 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_proj * 2, d_proj)
        )

        # === Module 2: Utility Encoder ===
        # 将 scalar utility 编码为 d_proj 维向量
        # 这让模型能"看到"每个 calibration 点的 utility 值
        self.utility_encoder = nn.Sequential(
            nn.Linear(1, d_proj // 2),
            nn.ReLU(),
            nn.Linear(d_proj // 2, d_proj)
        )

        # === Module 3: Calibration Context Encoder ===
        # Self-attention over calibration set
        # 目的：发现 calibration 中的 pattern
        # - 哪些 state 特征与高 utility 共现？
        # - 方向是正还是负？
        # - 哪些信号最重要？
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_proj,
            nhead=n_heads,
            dim_feedforward=d_proj * 4,
            dropout=dropout,
            batch_first=True,
            norm_first=True  # Pre-LN for training stability
        )
        self.context_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=n_layers
        )

        # === Module 4: Query-Context Cross-Attention ===
        # Query attends to encoded context
        # 目的：基于 context 中的 pattern 预测 query 的 VOC
        self.cross_attn = nn.MultiheadAttention(
            embed_dim=d_proj,
            num_heads=n_heads,
            dropout=dropout,
            batch_first=True
        )
        self.cross_norm = nn.LayerNorm(d_proj)

        # === Module 5: Decision Head ===
        # 融合 query 自身信息 + cross-attention 输出
        self.decision_head = nn.Sequential(
            nn.Linear(d_proj * 2, d_proj),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_proj, 2)  # [VOC_mean, VOC_logvar]
        )

        # Parameter count
        self._count_params()

    def _count_params(self):
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"ICGNet: {total:,} total params, {trainable:,} trainable")
        # 预估: ~500K - 1M params (取决于 d_proj 和 n_layers)

    def encode_calibration(self, h_calib, u_calib):
        """
        编码 calibration set。

        h_calib: (B, N_c, d_model) — N_c 个 calibration states 的 hidden states
        u_calib: (B, N_c, 1)       — 对应的 utility 值

        Returns: (B, N_c, d_proj) — encoded calibration context
        """
        # 投影 state
        state_emb = self.state_proj(h_calib)       # (B, N_c, d_proj)

        # 编码 utility
        util_emb = self.utility_encoder(u_calib)    # (B, N_c, d_proj)

        # 融合：state + utility
        # 用加法融合（让模型同时看到"这个 state 长什么样"和"它的 utility 是多少"）
        calib_emb = state_emb + util_emb            # (B, N_c, d_proj)

        # Self-attention over calibration set
        # → 发现 calibration 内部的 pattern
        context = self.context_encoder(calib_emb)   # (B, N_c, d_proj)

        return context

    def forward(self, h_query, h_calib, u_calib):
        """
        完整 forward pass。

        h_query: (B, 1, d_model) — 当前 query state
        h_calib: (B, N_c, d_model) — calibration states
        u_calib: (B, N_c, 1) — calibration utilities

        Returns:
        - voc_mean: (B,) — VOC 预测值
        - voc_logvar: (B,) — VOC 预测不确定性
        - attn_weights: (B, 1, N_c) — cross-attention weights（可解释）
        """
        # 1. Encode calibration set
        context = self.encode_calibration(h_calib, u_calib)  # (B, N_c, d_proj)

        # 2. Project query
        query_emb = self.state_proj(h_query)                  # (B, 1, d_proj)

        # 3. Cross-attention: query attends to context
        attended, attn_weights = self.cross_attn(
            query=query_emb,
            key=context,
            value=context
        )  # attended: (B, 1, d_proj), attn_weights: (B, 1, N_c)

        # Residual + LayerNorm
        attended = self.cross_norm(query_emb + attended)      # (B, 1, d_proj)

        # 4. Decision: concat query + attended → predict VOC
        combined = torch.cat([
            query_emb.squeeze(1),     # (B, d_proj) — query 自身信息
            attended.squeeze(1)       # (B, d_proj) — context 提供的信息
        ], dim=-1)                    # (B, d_proj * 2)

        out = self.decision_head(combined)  # (B, 2)

        voc_mean = out[:, 0]       # (B,)
        voc_logvar = out[:, 1]     # (B,)

        return voc_mean, voc_logvar, attn_weights

    def decide(self, h_query, h_calib, u_calib, lambda_star):
        """
        Gate 决策接口。

        Returns: (trigger: bool, voc: float, confidence: float)
        """
        voc_mean, voc_logvar, attn = self.forward(
            h_query.unsqueeze(0).unsqueeze(0),  # (1, 1, d_model)
            h_calib.unsqueeze(0),                # (1, N_c, d_model)
            u_calib.unsqueeze(0).unsqueeze(-1)   # (1, N_c, 1)
        )

        voc = voc_mean.item()
        voc_std = torch.exp(0.5 * voc_logvar).item()

        trigger = voc > lambda_star
        confidence = abs(voc - lambda_star) / (voc_std + 1e-8)

        return trigger, voc, confidence, attn.squeeze(0)
```

### 参数量估算

| d_proj | n_layers | n_heads | 总参数量 | 训练时间预估 |
|--------|----------|---------|---------|------------|
| 64 | 1 | 4 | ~400K | ~30s |
| **128** | **2** | **4** | **~900K** | **~2min** |
| 256 | 3 | 8 | ~3M | ~10min |

**推荐配置**：d_proj=128, n_layers=2, n_heads=4（~900K 参数，训练 < 5 分钟）

### 时间估算

- 架构实现 + 单元测试：2-3 天
- 总计：**2-3 天**

---

## Phase 5B.2：Per-Environment 验证

### 做什么

在每个环境内部，验证 ICGNet 是否能从 calibration data 中有效学习 gate。**这一步不做跨环境**，只做 within-environment 的 train/test split。

### 训练方式（per-env）

```python
def train_icgnet_per_env(hidden_states, utilities, n_calib=50, n_epochs=200):
    """
    Per-environment training:
    从同一环境的数据中，随机分 calibration set + query set。

    hidden_states: (N_total, d_model) — 某环境的所有数据
    utilities: (N_total,) — 对应 utility
    n_calib: calibration set 大小

    训练方式：episodic training
    每个 training episode:
      1. 随机抽 n_calib 个点作为 calibration set
      2. 随机抽 batch_size 个点作为 query
      3. ICGNet(query, calib_set) → 预测 query 的 VOC
      4. Loss = Gaussian NLL
    """
    model = InContextGatingNet(d_model=hidden_states.shape[1])
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)

    all_h = torch.tensor(hidden_states, dtype=torch.float32)
    all_u = torch.tensor(utilities, dtype=torch.float32)

    for epoch in range(n_epochs):
        # Episodic sampling
        for _ in range(20):  # 20 episodes per epoch
            # Random split: calibration + query
            perm = torch.randperm(len(all_h))
            calib_idx = perm[:n_calib]
            query_idx = perm[n_calib:n_calib + 32]  # batch of 32 queries

            h_calib = all_h[calib_idx].unsqueeze(0)      # (1, N_c, d_model)
            u_calib = all_u[calib_idx].unsqueeze(0).unsqueeze(-1)  # (1, N_c, 1)
            h_query = all_h[query_idx].unsqueeze(0)       # (1, 32, d_model)
            u_query = all_u[query_idx]                     # (32,)

            # Forward（对每个 query 独立做 cross-attention）
            # Reshape: 把 query batch 展开
            B_q = h_query.shape[1]
            h_q_flat = h_query.squeeze(0)  # (32, d_model)

            voc_preds = []
            voc_logvars = []
            for i in range(B_q):
                h_q_i = h_q_flat[i:i+1].unsqueeze(0)  # (1, 1, d_model)
                vm, vl, _ = model(h_q_i, h_calib, u_calib)
                voc_preds.append(vm)
                voc_logvars.append(vl)

            voc_mean = torch.cat(voc_preds)    # (32,)
            voc_logvar = torch.cat(voc_logvars)  # (32,)

            # Gaussian NLL Loss
            loss = 0.5 * (voc_logvar + (u_query - voc_mean)**2 / torch.exp(voc_logvar))
            loss = loss.mean()

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        scheduler.step()

    return model
```

### 评估方式

```
Hold-out evaluation:
  1. 数据按 episode 分：80% train, 20% test（确保无 episode 泄露）
  2. 训练时：从 train 中抽 calibration + query
  3. 测试时：从 train 中抽 calibration，从 test 中抽 query
  4. 指标：VOC prediction R², gate accuracy, gate SR (在 held-out episodes 上)
```

### 验证实验矩阵

| 实验 | 环境 | 目的 | 预期 |
|------|------|------|------|
| ICGNet per-env R² | 各 ×3 | VOC 预测质量 | R² > 0.2 |
| ICGNet per-env gate acc | 各 ×3 | 二值 gate 准确率 | acc > LR-HandCraft |
| ICGNet vs LR-HandCraft | 各 ×3 | 方法对比 | ICGNet ≥ LR |
| ICGNet vs L1-Probe (5A.2) | 各 ×3 | 架构对比 | ICGNet ≥ L1（ICGNet 看了 context） |
| N_c sensitivity | HotpotQA | calibration size 影响 | N_c=50 足够 |

### 判断标准

```
✅ GO：
  - ICGNet per-env gate accuracy ≥ LR-HandCraft 在至少 2/3 环境
  - ICGNet R² > 0.15 在所有环境
  → 证明 ICGNet 架构有效，可继续做 meta-training

⚠️ MODERATE：
  - ICGNet ≈ LR 在 gate accuracy 上
  → ICGNet 不输 LR，但没有优势
  → 仍可继续，因为跨环境泛化是 ICGNet 的主要优势
  → 但需要 Phase 5B.3 证明跨环境优势

❌ NO-GO：
  - ICGNet << LR-HandCraft 在多数环境
  → 架构不适合这个问题
  → 尝试调参（d_proj, n_layers），如果仍然不行 → 放弃 ICGNet 路线
```

**Early Kill 机制**：如果在 HotpotQA（最强信号环境）上 ICGNet 都不如 LR → 直接 kill，不继续。

### 时间估算

- Per-env 训练（3 环境）：1 天
- 评估 + 对比：1 天
- N_c sensitivity 实验：0.5 天
- 总计：**2.5 天**

---

## Phase 5B.3：Cross-Environment Meta-Training

### 做什么

**这是 ICGNet 的核心创新实验**。在多个环境的数据上联合 meta-train，让 ICGNet 学会 "how to gate from calibration data"——而不只是学会某一个环境的 gating pattern。

### Meta-Training 策略

```python
def meta_train_icgnet(env_data_dict, n_calib=50, n_epochs=500):
    """
    Meta-training across environments.

    env_data_dict: {
        'hotpotqa': (hidden_states_hq, utilities_hq),
        'apps': (hidden_states_apps, utilities_apps),
        'webshop': (hidden_states_ws, utilities_ws),
    }

    每个 meta-training episode:
      1. 随机选一个环境
      2. 从该环境中抽 calibration set + query set
      3. ICGNet(query, calib_set) → 预测 VOC
      4. Loss = Gaussian NLL

    关键：ICGNet 需要学会从 calibration 中发现方向和信号重要性，
    而不是记住某个环境的固定 pattern。因为不同环境方向不同（C2 finding），
    模型必须真正学会 "how to discover direction from data"。
    """
    model = InContextGatingNet(d_model=2560)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)

    env_names = list(env_data_dict.keys())

    for epoch in range(n_epochs):
        epoch_loss = 0
        n_episodes = 0

        for _ in range(30):  # 30 episodes per epoch
            # 随机选环境
            env = random.choice(env_names)
            all_h, all_u = env_data_dict[env]

            # 随机抽 calibration + query
            perm = torch.randperm(len(all_h))
            calib_idx = perm[:n_calib]
            query_idx = perm[n_calib:n_calib + 16]

            h_calib = all_h[calib_idx].unsqueeze(0)
            u_calib = all_u[calib_idx].unsqueeze(0).unsqueeze(-1)
            h_query = all_h[query_idx]
            u_query = all_u[query_idx]

            # Forward + Loss (per query point)
            loss = compute_episode_loss(model, h_query, h_calib, u_calib, u_query)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            epoch_loss += loss.item()
            n_episodes += 1

        scheduler.step()

        if epoch % 50 == 0:
            print(f"Epoch {epoch}: avg_loss = {epoch_loss / n_episodes:.4f}")

    return model
```

### 数据增强策略

由于只有 3 个环境，meta-training 数据有限。需要数据增强：

| 增强策略 | 做法 | 目的 |
|---------|------|------|
| **Calibration set 随机子采样** | 每次从 N_total 中随机抽 N_c 个 | 同一环境产生不同的 calibration context |
| **Utility perturbation** | U' = U + ε, ε ~ N(0, 0.05) | 防止过拟合 utility 的精确值 |
| **Hidden state dropout** | 随机 mask hidden state 的 10% 维度 | 防止依赖特定维度 |
| **Calibration size variation** | N_c ~ Uniform(20, 100) | 让模型适应不同大小的 calibration set |
| **Utility direction flip** | 50% 概率翻转 U 的符号 | **关键**：迫使模型从数据中发现方向，而不是记住方向 |

**⚠️ Utility direction flip 是最重要的增强**：

```python
# 随机翻转 utility 方向
if random.random() < 0.5:
    u_calib = -u_calib
    u_query = -u_query
    # 这迫使模型必须从 calibration 数据中推断方向
    # 否则它会记住 "HotpotQA 的方向是负的"
    # flip 后模型必须看 calibration 中 (state, utility) 的关系才能判断
```

### Leave-One-Out (LOO) 评估

**最关键的实验**：模型在 2 个环境上训练，在第 3 个环境上测试。

| 训练环境 | 测试环境 | 这测试什么 |
|---------|---------|-----------|
| APPS + WebShop | **HotpotQA** | 最强信号环境，方向是负的 |
| HotpotQA + WebShop | **APPS** | 弱信号环境，方向混合 |
| HotpotQA + APPS | **WebShop** | 分类信号为主，方向正 |

**LOO 评估方式**：

```
对于测试环境 E_test:
  1. Meta-train on E_1, E_2（不包含 E_test 的任何数据）
  2. 在 E_test 中抽 calibration set（50-100 个点）
  3. 用 ICGNet(query, calib_from_E_test) 做 gate
  4. 评估 gate accuracy, SR, CS

这模拟了"遇到全新环境"的场景：
  - 模型从未见过 E_test 的数据
  - 只通过 calibration set 了解 E_test
  - 如果仍能有效 gate → 泛化性验证通过
```

### 对比实验

| 方法 | 描述 | 需要训练？ | 需要手工 feature？ |
|------|------|-----------|------------------|
| SCG-LR (hand-craft) | 当前最佳 | 每环境独立训 | ✅ 需要 |
| L1-Probe (from 5A.2) | MLP on hidden state | 每环境独立训 | ❌ 不需要 |
| **ICGNet per-env** | 每环境独立训 | 每环境独立训 | ❌ 不需要 |
| **ICGNet meta-all** | 3 环境联合训 | 一次 | ❌ 不需要 |
| **ICGNet LOO** | 2 环境训，1 环境测 | 一次 | ❌ 不需要 |

### 判断标准

```
✅ GO（强）：
  - ICGNet LOO gate accuracy > LR-HandCraft 在 2/3 测试环境
  → 跨环境泛化成功 + 超过手工方法
  → 论文最强 claim："zero-shot gating in new environments"

✅ GO（中）：
  - ICGNet LOO ≈ LR-HandCraft（±5% accuracy）
  → 泛化到新环境且不输手工方法
  → claim："matches hand-crafted gates without domain knowledge"

✅ GO（弱）：
  - ICGNet per-env > LR-HandCraft，但 LOO < LR
  → 架构有效但跨环境泛化不足
  → 需要更多训练环境（limitation）
  → 仍可发表，但 claim 降级

❌ NO-GO：
  - ICGNet per-env 和 LOO 都 < LR
  → 架构对这个问题不适合
  → 放弃 ICGNet 路线
```

### 时间估算

- Meta-training 实现 + 调试：2-3 天
- Meta-training 运行（~500 epochs，3 环境）：0.5 天
- LOO 评估（3 个 LOO split）：1 天
- 对比实验分析：1 天
- 总计：**4.5-5.5 天**

---

## Phase 5B.4：Full Evaluation

### 做什么

选择表现最好的 ICGNet 变体，在 3 环境 × 3 seeds 上跑完整的 online gating 实验。

### 实验矩阵

| 方法 | 描述 | 新/旧 |
|------|------|-------|
| base_only | 不触发 | ✅ 已有 |
| always_trigger | 每步触发 | ✅ 已有 |
| random_50 | 50% 随机 | ✅ 已有 |
| oracle | 完美 gate | ✅ 已有 |
| **SCG-LR (hand-craft)** | 当前最佳 | ✅ 已有 |
| **ICGNet per-env** | 每环境独立训 | 🆕 |
| **ICGNet meta-all** | 3 环境联合训 | 🆕 |
| **ICGNet LOO** | 2 训 1 测 | 🆕 |

**新增：3 × 3 × 3 = 27 runs**

### Online Gating 实现

```python
class ICGNetOnlineGate(SCGBase):
    """
    ICGNet 的在线部署版本。

    Phase 1 (Probe): 前 N_probe 步随机触发，收集 (h, U) 对
    Phase 2 (Exploit): 用收集的 calibration set 做 ICGNet gate 决策
    """

    def __init__(self, icgnet_model, lambda_star,
                 n_probe_steps=100, n_calib=50):
        self.model = icgnet_model  # 已训练好的 ICGNet
        self.lambda_star = lambda_star
        self.n_probe_steps = n_probe_steps
        self.n_calib = n_calib

        self.calibration_buffer = []  # [(h, U)]
        self.step_count = 0
        self.phase = 'probe'

    def step(self, state_text, hidden_state, env, proposer):
        self.step_count += 1

        if self.phase == 'probe':
            # Probe phase: 50% 随机触发，收集数据
            trigger = random.random() < 0.5
            if trigger:
                utility = self._execute_optimizer(env, proposer)
            else:
                utility = 0.0
            self.calibration_buffer.append((hidden_state, utility))

            if self.step_count >= self.n_probe_steps:
                self.phase = 'exploit'
                self._prepare_calib_set()

            return trigger

        else:
            # Exploit phase: 用 ICGNet gate
            trigger, voc, conf, attn = self.model.decide(
                h_query=torch.tensor(hidden_state, dtype=torch.float32),
                h_calib=self.calib_h,
                u_calib=self.calib_u,
                lambda_star=self.lambda_star
            )
            return trigger

    def _prepare_calib_set(self):
        """从 buffer 中抽取 calibration set"""
        h_all = np.stack([x[0] for x in self.calibration_buffer])
        u_all = np.array([x[1] for x in self.calibration_buffer])

        # 抽 N_c 个（如果 buffer < N_c，全用）
        n = min(self.n_calib, len(h_all))
        idx = np.random.choice(len(h_all), n, replace=False)
        self.calib_h = torch.tensor(h_all[idx], dtype=torch.float32)
        self.calib_u = torch.tensor(u_all[idx], dtype=torch.float32)
```

### 资源估算

ICGNet forward pass 比 LR 慢但仍然很快（~1ms per step）。
主要时间在 environment rollout（与现有实验相同）。

| 环境 | Episodes/Run | Runs | GPU 时间/Run | 总 GPU 时间 |
|------|-------------|------|-------------|-------------|
| HotpotQA | 200 | 9 | ~1h | ~9h |
| APPS | 200 | 9 | ~2h | ~18h |
| WebShop | 200 | 9 | ~2h | ~18h |
| **总计** | — | 27 | — | **~45 GPU-hours** |

### 时间估算

- 实验跑完：3-5 天
- 结果分析：1 天
- 总计：**4-6 天**

---

## Phase 5B.5：Analysis

### 核心分析项

**1. Attention Pattern 可视化（关键 novelty）**

```
ICGNet 的 cross-attention weights 揭示：
  query 在做 gate 决策时，参考了 calibration set 中的哪些 examples

预期发现：
  - 在 HotpotQA 中：query 主要 attend 到 utility < 0 的 high-entropy examples
    → 学到了 "高 entropy = 不需要 optimizer"（负方向）
  - 在 APPS 中：query 主要 attend 到 utility > 0 的 low-step examples
    → 学到了 "低 step = 需要 optimizer"（不同信号 + 不同方向）

这直接可视化了 "direction discovery in action"
→ C2 finding 的最直观证据
```

可视化方式：
```
Attention heatmap:
  行 = query states (按 utility 排序)
  列 = calibration examples (按 utility 排序)
  颜色 = attention weight

预期：对角/反对角 pattern（取决于方向）
```

**2. Calibration Set Size Ablation**

| N_c | 预期 gate accuracy | 说明 |
|-----|-------------------|------|
| 10 | 较低 | calibration 信息不足 |
| 20 | 中等 | 最小可用 |
| 50 | 接近最优 | 推荐值 |
| 100 | 最优 | 边际收益递减 |
| 200 | ≈ 100 | 饱和 |

**关键问题**：N_c 最少需要多少？如果 N_c=20 就够 → 实用价值高。

**3. LOO 跨环境 Gate Accuracy 对比**

| 测试环境 | LR-HandCraft | ICGNet LOO | Δ | 说明 |
|---------|-------------|-----------|---|------|
| HotpotQA | [已有] | [新] | | 强信号，最容易 |
| APPS | [已有] | [新] | | 弱信号，最难 |
| WebShop | [已有] | [新] | | 分类信号 |

**4. "What Did ICGNet Learn?" Probing Study**

```
实验：在 meta-trained ICGNet 中，probe context encoder 学到了什么。

方法：
  1. 给 ICGNet 人工构造的 calibration set（U 与某个 state 维度正相关）
  2. 看 ICGNet 能否正确利用这个关系做 gate
  3. 翻转方向（U 与该维度负相关），看 ICGNet 能否适应

如果 ICGNet 正确适应方向翻转 → 它确实学会了 "direction discovery"
如果不能 → 它只是记忆了训练环境的 pattern
```

### 可视化设计

| 图 | 内容 | 用于论文 |
|-----|------|---------|
| Fig B1 | Attention heatmap (3 环境，展示方向差异) | Section 5 核心 figure |
| Fig B2 | Calibration size ablation (N_c vs accuracy) | Section 5 ablation |
| Fig B3 | LOO 跨环境对比 bar chart | Section 5 main result |
| Fig B4 | Direction flip probing study | Section 5 或 appendix |
| Fig B5 | VOC prediction scatter (per env) | Appendix |
| Fig B6 | Training loss curve (meta-train vs per-env) | Appendix |

### 时间估算

- 分析 + 可视化：3-4 天
- 总计：**3-4 天**

---

## 总体时间线

| 阶段 | 预计时间 | 累计 |
|------|---------|------|
| 5B.0 Hidden State 基础设施（共享） | 2-3 天 | 2-3 天 |
| 5B.1 ICGNet 架构实现 | 2-3 天 | 4-6 天 |
| 5B.2 Per-Environment 验证 | 2.5 天 | 6.5-8.5 天 |
| 5B.3 Cross-Environment Meta-Training | 4.5-5.5 天 | 11-14 天 |
| 5B.4 Full Evaluation | 4-6 天 | 15-20 天 |
| 5B.5 Analysis | 3-4 天 | **18-24 天** |

**总计：约 3-4 周**

### 早期 Kill Switch

```
Phase 5B.2 结束后（~8 天）做 GO/NO-GO 判断：
  如果 ICGNet per-env << LR-HandCraft 在 HotpotQA → 直接 kill
  原因：如果连 per-env 都不行，meta-training 不可能救回来

Phase 5B.3 中期（~12 天）做快速判断：
  如果 meta-train loss 不收敛 → 检查 data augmentation
  如果 LOO accuracy 极低 → 可能 3 环境不够 meta-train
  → 降级为 per-env ICGNet（放弃跨环境 claim）
```

---

## 风险评估

| 风险 | 严重性 | 应对 |
|------|--------|------|
| **3 环境不够 meta-train** | 🔴 高 | 数据增强（direction flip 最关键）。worst case 降级为 per-env ICGNet |
| ICGNet 过拟合少量环境 | 🔴 高 | Direction flip augmentation + dropout + weight decay。LOO 评估 |
| Hidden state 不编码 VOC 信息 | 🔴 高 | 与 5A 共享此风险。Phase 5B.2 early kill |
| Cross-attention 退化为均匀 attention | 🟡 中 | Entropy regularization。检查 attention 是否 peaked |
| 训练不稳定 | 🟡 中 | Pre-LN transformer, gradient clipping, warmup |
| ICGNet ≈ L1-Probe（attention 没帮忙） | 🟡 中 | Ablation: ICGNet vs L1-Probe。如果 attention 没帮助 → cascade 可能更值得 |
| LOO 只在部分环境 work | 🟢 低 | 3 个 LOO split，至少 2 个成功就可以 claim |

---

## 与 Plan A 的关系

### 共享组件

| 组件 | Plan A | Plan B | 共享？ |
|------|--------|--------|--------|
| Hidden state 基础设施 | 5A.0 | 5B.0 | ✅ 完全共享 |
| L1 VOC Probe | 5A.2 核心 | 5B.2 对比 baseline | ✅ 可复用 |
| LR-HandCraft baseline | 5A.4 对比 | 5B.4 对比 | ✅ 已有 |
| Lambda* from CMDP | 5A.3 使用 | 5B.4 使用 | ✅ 已有 |

### 互补关系

```
如果 Plan A 成功 + Plan B 成功：
  → 论文同时报告两个 model，cascade 为主（practical），ICGNet 为 analysis tool（interpretability）
  → Contribution: finding (C1) + cascaded gate (C2) + ICGNet direction discovery (C3) + validation (C4)

如果 Plan A 成功 + Plan B 失败：
  → 论文用 Cascade，ICGNet 在 appendix 作为 negative result
  → 说明：简单 cascade 比复杂 meta-learning 更实用

如果 Plan A 失败 + Plan B 成功：
  → 论文用 ICGNet，展示 attention-based direction discovery
  → L1 作为 ICGNet 的 ablation

如果 Plan A 失败 + Plan B 失败：
  → 回退到原方案（LR + 手工特征）
  → 但在 writing guide 中强化 finding + 加入自动 feature screening（低成本补充）
  → hidden state 实验作为 negative result 在 appendix
```

### 并行执行建议

```
Week 1:  5A.0 / 5B.0（共享）→ hidden state 收集
Week 1:  5A.1（L0 Bayesian gate）| 5B.1（ICGNet 架构）
Week 2:  5A.2（L1 probe）| 5B.2（per-env 验证）
         → Week 2 末：两路 GO/NO-GO 判断
Week 3:  5A.3-5A.4 | 5B.3-5B.4（如果两路都 GO）
Week 4:  5A.5 | 5B.5（analysis）
         → Week 4 末：选定最终方案，开始 paper writing
```

---

## 论文中的定位

**如果 Phase 5B 成功**，论文 Method Section 的结构：

```
4.1 Problem: VOC estimation for adaptive triggering
4.2 Self-Probing: VOC from LLM hidden representations
4.3 In-Context Gating: learning to gate from calibration data
    4.3.1 Architecture (state projection + utility encoding + cross-attention)
    4.3.2 Meta-training across environments
    4.3.3 Deployment: probe phase + exploit phase
4.4 λ* from CMDP (decision threshold)
```

**核心 selling point**：
1. **Zero domain knowledge**：不需要手工 feature，hidden state + calibration data 足够
2. **Direction discovery is implicit**：ICGNet 通过 attention 从 calibration 中发现方向（不需要显式计算 ρ）
3. **Cross-environment generalization**：同一模型权重适配不同环境（LOO 证据）
4. **Interpretable**：attention weights 直接可视化 direction discovery 过程

**如果 Phase 5B 部分成功**（per-env 好，LOO 一般）：

```
退化方案：ICGNet per-env（每环境独立训练，但不需要手工 feature）
claim 降级："ICGNet automates feature discovery and direction calibration within each environment"
缺少：跨环境泛化的 claim
→ 可接受，但影响力减半
```
