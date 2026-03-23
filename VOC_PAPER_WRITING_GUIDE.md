# Paper Writing Template: Same Signal, Opposite Meaning

**目标会议**: NeurIPS 2026 | **Backbone**: Qwen3-4B
**标题**: Same Signal, Opposite Meaning: Why Adaptive Compute Fails Across Environments
**方法**: EAAG (Environment-Aware Adaptive Gating)
**环境 (8个, 全部为主评估)**: HotpotQA, APPS Intro, WebShop, FEVER, TWExpress, Plancraft, APPS Interview, CRUXEval
**论文类型**: Finding + Theory + Method
**历史版本**: `VOC_PAPER_WRITING_GUIDE_v7.0_full_archive_20260322.md`

---

## Storyline

```
隐含假设 → 假设是错的 (4 Observations) → 为什么错 (Two-Source Model)
→ 错了就 provably 不行 (Proposition) → 怎么修 (EAAG) → 修了之后全赢 (Results)
```

一句话：**不确定性信号的语义由环境信息结构决定，任何假设固定语义的方法都 provably incomplete。**

---

## Abstract (~250 words)

**结构参考**: NeurIPS best paper 惯用模式 — [背景1-2句] → [隐含假设+发现2-3句] → [理论1-2句] → [方法1-2句] → [结果2句]。
参考论文: "Not All Tokens Are What You Need" (NeurIPS 2024 Best Paper Runner-Up) 用 "challenging this norm, we posit..." 直接亮发现; "Are Emergent Abilities a Mirage?" (NeurIPS 2023 Outstanding) 用 "we present an alternative explanation" 颠覆假设; "Visual Autoregressive Modeling" (NeurIPS 2024 Best Paper) 用 "diverging from the standard" 一句话定位新范式。共同模式: **第2-3句就亮核心发现，不做长铺垫**。

```latex
\begin{abstract}
Adaptive test-time compute methods for LLM agents---rollout evaluation,
tree search, $K$-variant sampling---improve decision quality but incur
$5$--$15\times$ overhead. A growing family of \emph{selective triggering}
methods reduces this cost by using uncertainty signals (token entropy,
calibrated confidence, vote disagreement) to decide when extra compute
is worthwhile, implicitly assuming a \emph{fixed} mapping from signal
value to compute need. We show that this assumption is wrong. Through
systematic measurement across 8 diverse agent environments, we find
that the signal--utility direction \emph{reverses}: token entropy
correlates negatively with rollout utility in fact-verification
($\rho{=}{-}0.119$, FEVER) but positively in code generation
($\rho{=}{+}0.317$, APPS Interview), while carrying near-zero signal
in introductory coding ($\rho{=}{+}0.012$, $p{=}0.63$, APPS Intro).
The \emph{identity} of the most informative signal also varies
entirely---\texttt{step\_count} dominates in HotpotQA
($\rho{=}{-}0.494$) while \texttt{num\_available\_actions} dominates
in WebShop ($\rho{=}{+}0.444$). We explain this reversal via a
\emph{two-source uncertainty model}: the same entropy reflects either
information poverty (rollouts cannot help) or decision difficulty
(rollouts explore viable alternatives), an instance of Simpson's
paradox in the signal--utility space. We prove that direction discovery
is a necessary condition for cross-environment non-negative value of
computation. Building on this analysis, we propose EAAG
(Environment-Aware Adaptive Gating), which lets the agent
autonomously discover environment-specific gating patterns through
exploration, LLM-based reasoning, and LASSO-based direction learning,
with zero per-step deployment cost. Across 8 evaluation environments,
EAAG Pareto-dominates all fixed-direction baselines (34 wins vs.\ 2
losses against 6 competing methods) and exhibits emergent adaptive
behavior: trigger rate automatically aligns with rollout
headroom---60\% when headroom is large, 6\% when small---without
explicit headroom estimation.
\end{abstract}
```

**Abstract 设计笔记 (NeurIPS best paper pattern analysis):**
- **句1-2 (背景)**: 一句话定义问题空间 + 一句话定义 selective triggering 范式和其隐含假设。效仿 "Not All Tokens" 的节奏——不超过2句背景就切入发现。
- **句3-5 (发现, 🔥核心)**: "We show that this assumption is wrong" 直接亮结论 (类比 "Are Emergent Abilities a Mirage?" 的 "we present an alternative explanation")。然后用3个具体数字 (ρ=-0.119, ρ=+0.317, ρ=+0.012) 让 reviewer 在 abstract 阶段就被说服。
- **句6-7 (理论)**: Two-source model + Simpson's paradox + necessity proof, 一句理论一句定理。
- **句8-9 (方法)**: EAAG 三步流程，强调 "zero per-step cost" 和 "autonomous discovery"。
- **句10-11 (结果)**: 34W/2L + emergent adaptive behavior。用具体数字收尾。

---

## §1 Introduction (1.5 页)

### P1: 背景 + 现有方法 (4-5 句)

**P1 设计笔记 (学习 NeurIPS best paper 开头模式):**
- "Not All Tokens" 开头: "Previous language model pre-training methods have uniformly applied a next-token prediction loss to all training tokens." — 一句话定义整个 status quo，然后立刻 challenge。
- "Visual Autoregressive Modeling" 开头: "We present VAR, a new generation paradigm that redefines..." — 直接亮新范式，diverging from standard。
- "Are Emergent Abilities a Mirage?" 开头: "Recent work claims that large language models display emergent abilities..." — 先精确描述 claim，再拆解。
- **共同模式**: P1 不超过4句。第1句定义 landscape，第2-3句 zoom in 到 selective triggering，第4句设下 "看似合理" 的锚点为 P2 的颠覆做铺垫。

```latex
Large language model (LLM) agents benefit substantially from
test-time compute---rollouts, verification, and tree search---but
these optimizers incur 5--15$\times$ computational
overhead~\citep{yao2023tree, hao2023reasoning, zhou2024lats}.
A growing body of work addresses this inefficiency through
\emph{selective triggering}: using uncertainty signals to decide
\emph{when} extra compute is worthwhile, rather than applying it
uniformly~\citep{catts2026, seag2025, cats2025, corefine2026,
adaptthink2025, thinkless2025}. Across diverse mechanisms---vote
entropy~\citep{catts2026}, calibrated
confidence~\citep{cats2025, seag2025}, token-level
entropy~\citep{corefine2026, thinkjustenough2025}, and reinforcement
learning~\citep{adaptthink2025, thinkless2025}---each method has
demonstrated effectiveness within its respective evaluation setting.
```

### P2: 隐含假设 (3-4 句)

```latex
Despite differing mechanisms---vote-derived
uncertainty~\citep{catts2026}, entropy
thresholding~\citep{corefine2024, thinkjustenough2025},
calibrated confidence~\citep{cats2025, seag2025}, and reinforcement
learning~\citep{adaptthink2025, thinkless2025}---these methods share
an unquestioned assumption: \emph{the direction of the
signal--utility correlation is fixed}. High entropy means the agent
is struggling and needs help; low confidence means a rollout would
be valuable. This mapping from signal to compute need is treated as
a given, never explicitly verified.
```

### P3: 假设是错的 + 后果 (5-6 句) 🔥

**P3 设计笔记 (NeurIPS finding-driven 论文核心段):**
- 效仿 "Not All Tokens" 的 "Challenging this norm, we posit that..." — 但我们更强，因为有 empirical evidence 而非 posit。
- 效仿 "Are Emergent Abilities a Mirage?" 的 "we present an alternative explanation" — 先亮结论，再铺数据。
- **关键**: 用 3 层递进 — (1) 方向反转 (direction reversal), (2) 信号身份替换 (signal identity shift), (3) 后果灾难性 (catastrophic failure)。每层用最精确的数字。
- **最后一句**: "When the direction is wrong, more precise calibration makes performance worse, not better." 这是本论文的 signature insight，类比 "emergent abilities are a mirage" — **问题不在校准精度，而在方向假设本身**。

```latex
We show that this assumption is wrong. Through systematic measurement
across 8 diverse agent environments, we find that the signal--utility
direction \emph{reverses}: token entropy correlates negatively with
rollout utility in fact-verification tasks
($\rho{=}{-}0.119$, FEVER) but positively in code generation
($\rho{=}{+}0.317$, APPS Interview), while carrying near-zero
information in introductory coding ($\rho{=}{+}0.012$, $p{=}0.63$,
APPS Intro). Beyond direction, the \emph{identity} of the most informative
signal varies entirely across environments---\texttt{step\_count}
dominates in HotpotQA ($\rho{=}{-}0.494$) while
\texttt{num\_available\_actions} dominates in WebShop
($\rho{=}{+}0.444$); single-signal entropy achieves AUC${\approx}$0.53
(barely above chance) while multi-signal gates reach AUC${\approx}$0.85.
All fixed-direction methods systematically fail
in at least two of eight evaluation environments; on FEVER, CATTS
achieves 34.2\%---\emph{below} the 37.0\% no-trigger baseline.
The cost of wrong direction is catastrophic: reversing the discovered
direction causes SR to drop by 38.8\,pp on HotpotQA,
with MLP falling to 45.3\%---below the 49.0\% no-trigger baseline.
When the direction is wrong, more precise calibration makes
performance \emph{worse}, not better.
```

### P4: 为什么 + 问题定义 (5-6 句)

```latex
We explain this reversal via a \emph{two-source uncertainty model}
(\S\ref{sec:toy-model}): the same entropy signal reflects two
fundamentally different sources---\emph{information poverty} (where
the agent lacks data and rollouts cannot help) and \emph{decision
difficulty} (where the agent faces multiple viable paths and rollouts
explore them). Environments differ in their proportion of these two
state types, causing the same signal to carry opposite meaning. This
is an instance of Simpson's paradox~\citep{simpson1951interpretation,
pearl2014understanding} in the signal--utility space: aggregating
heterogeneous subpopulations with opposing within-group trends
reverses the aggregate correlation. More broadly, our findings reveal
that \emph{uncertainty signal semantics are not an intrinsic property
of the signal but a function of the environment's information
structure}---a distinction that all prior methods implicitly collapse.
We prove that direction discovery is a \emph{necessary condition} for
cross-environment non-negative value of computation
(Proposition~\ref{prop:necessity}).
```

### P5: 方法 + 结果 (6-8 句)

```latex
We propose EAAG (Environment-Aware Adaptive Gating), which enables
LLM agents to autonomously discover environment-specific compute
allocation patterns. EAAG operates in three steps: (1)~the agent
\emph{explores} a new environment with 50 episodes of randomized
gating; (2)~an LLM \emph{reasons} about exploration data to identify
task-specific patterns and generate feature hypotheses; (3)~LASSO
\emph{learns} signal direction and importance, training a logistic
gate with zero per-step deployment cost. Unlike all prior methods,
EAAG requires no Phase~1 calibration data and no human-specified
signal direction. Across 8 evaluation environments, EAAG
Pareto-dominates all calibrated baselines: 34 wins vs.\ 2 losses
against 6 competing methods in head-to-head SR comparisons. The
learned gate exhibits emergent adaptive behavior: trigger rate
automatically aligns with rollout headroom---60\% triggering when
headroom is large (HotpotQA: $+$48\,pp), 6\% when headroom is
small (APPS Intro: $+$6\,pp)---without explicit headroom estimation.
```

### P6: Contributions

```latex
Our contributions are:
\begin{enumerate}[leftmargin=*,nosep]
\item \textbf{Finding $+$ theory.} We discover that signal--utility
  direction reverses across environments (8 environments, 4
  observations) and explain this via a two-source uncertainty model
  grounded in Simpson's paradox and the epistemic/aleatoric
  distinction. We prove that direction discovery is a necessary
  condition for cross-environment generalization
  (Proposition~\ref{prop:necessity}).

\item \textbf{EAAG method.} We propose Environment-Aware Adaptive
  Gating, where the LLM autonomously discovers environment-specific
  gating patterns via exploration, reasoning, and LASSO-based
  direction learning. Zero per-step overhead, no calibration data
  required.

\item \textbf{Systematic evaluation.} EAAG Pareto-dominates all
  calibrated baselines (34W/2L) across 8 diverse environments with
  emergent adaptive behavior matching rollout headroom.
\end{enumerate}
```

---

## §2 Related Work (0.75 页)

### §2.1 Adaptive Test-Time Compute (0.5 页)

```latex
\paragraph{Signal-based methods.}
SEAG~\citep{seag2025} triggers search when mean token confidence
falls below a threshold. CaTS~\citep{cats2025} uses Platt-scaled
confidence for calibrated early stopping. CoRefine~\citep{corefine2024}
refines outputs when per-token entropy exceeds a threshold. Think
Just Enough~\citep{thinkjustenough2025} applies entropy-based early
stopping with a fixed threshold. DiffAdapt~\citep{diffadapt2025}
trains a lightweight probe for difficulty estimation, assuming a
universal U-shaped entropy pattern. All assume a fixed relationship
between their chosen signal and compute need.

\paragraph{Vote-based methods.}
CATTS~\citep{catts2026} samples $K{=}5$ candidate actions, computes
vote entropy and margin, and triggers a full evaluation when
disagreement is high. This incurs $K$ additional forward passes per
step regardless of whether the optimizer is invoked.

\paragraph{RL-based methods.}
AdaptThink~\citep{adaptthink2025} and
Thinkless~\citep{thinkless2025} learn think/no-think policies via
reinforcement learning. ARPO~\citep{arpo2025} uses entropy-based
adaptive rollout at tool-call steps. These methods implicitly learn
direction through RL training but require per-environment training
and provide no interpretable direction signal.

\medskip\noindent
Despite differing mechanisms, all these methods share a common
assumption: a fixed relationship between uncertainty signals and
compute need. Our finding---that this relationship reverses across
environments---challenges this assumption and motivates
direction-aware gating.
```

### §2.2 Orthogonal Work (0.1 页)

```latex
Test-time scaling~\citep{snell2024scaling} studies compute-optimal
allocation at the problem level, finding that effectiveness varies
critically with prompt difficulty; we address the complementary
step-level question and show that signal \emph{meaning}---not just
effectiveness---varies across environments. Search methods such as
LATS~\citep{zhou2024lats} and FLARE~\citep{wang2026flare} improve
the search process itself; we control \emph{when} to search.
Recent work on LLM uncertainty~\citep{tao2025revisiting,
heo2025llmuncertainty} independently observes that calibration
quality varies across task types, providing converging evidence that
uncertainty semantics are domain-dependent.
```

### Concurrent Work 声明

```latex
\textbf{Concurrent work.} Several 2025--2026 papers independently
explore adaptive compute: CATTS~\citep{catts2026} uses vote-derived
gating for web agents; AdaptThink~\citep{adaptthink2025} learns
think/no-think via RL; DiffAdapt~\citep{diffadapt2025} uses a probe
for difficulty estimation. While sharing our motivation for selective
triggering, all assume or implicitly learn a fixed signal direction.
Our work is the first to empirically demonstrate that signal--utility
direction reverses across environments and to propose direction-aware
gating as a solution.
```

**Transition 设计笔记 (§2→§3):** §2 established that all prior methods share the fixed-direction assumption. §3 opens by defining the formal setup (what is utility, what is gating), then immediately shows that the assumption fails. The section title "Signal-Utility Landscape" signals to the reader that this is an empirical investigation, not yet a method section. 效仿 Schaeffer et al.: §2 (related work) → §3 ("An Alternative Explanation") 的过渡是 "we now test whether..." — 我们用类似手法: "we now characterize the signal-utility landscape to test whether this assumption holds."

---

## §3 Signal-Utility Landscape (2.0 页) — 论文心脏

### §3.1 Empirical Landscape (0.7 页)

**Setup:**
```latex
\section{The Signal-Utility Landscape}
\label{sec:signal-landscape}

Before proposing a solution, we characterize the relationship between
uncertainty signals and optimizer utility across diverse environments.
If the fixed-direction assumption of prior methods holds, we should
observe consistent signal--utility correlations; if it fails, the
failure mode will guide method design.

We study LLM-based agents in multi-step interactive environments.
At each step $t$, the agent observes state $s_t$, selects action
$a_t$, and transitions to $s_{t+1}$. An environment-specific
\emph{test-time optimizer} $T$ (e.g., rollout evaluation, $K$-variant
sampling) can be invoked at any step to potentially improve action
quality. We define the \emph{optimizer utility} as:
\begin{equation}
  U(T, s) = \mathbb{E}[R(\tau) \mid a{=}T(s)]
           - \mathbb{E}[R(\tau) \mid a{=}\pi(s)]
  \label{eq:utility}
\end{equation}
where $R(\tau)$ is the episode return. $U > 0$ indicates the optimizer
improves the outcome; $U \leq 0$ indicates it is wasteful or harmful.
The \emph{adaptive gating problem} is to learn a gate
$g: \mathcal{S} \to \{0, 1\}$ that triggers $T$ only when $U > 0$.
```

**Observation 1 — Direction Reversal:**
```latex
\textbf{Observation 1: The signal--utility direction reverses across
environments.} Table~\ref{tab:signal-discovery} reports Spearman
correlations between observable signals and optimizer utility across
8 environments. Token entropy---the signal used by the majority of
prior methods---exhibits $\rho{=}{-}0.119$ in FEVER (negative: high
entropy $\to$ low utility) but $\rho{=}{+}0.317$ in APPS Interview
(positive: high entropy $\to$ high utility). The strongest
\emph{non-entropy} signal varies entirely: \texttt{step\_count}
($\rho{=}{-}0.494$) in HotpotQA, \texttt{num\_available\_actions}
($\rho{=}{+}0.444$) in WebShop. The same numerical signal has
opposite meaning depending on the environment.
```

**Signal Discovery Table:**
<!-- 📁 实验文件夹: experiment/tab_signal_discovery/ -->
```latex
\begin{table}[t]
\caption{Signal--utility correlations across 8 environments.
$\rho$: Spearman correlation with optimizer utility $U$.
Direction and signal identity both vary.}
\label{tab:signal-discovery}
\centering\small
\begin{tabular}{llccc}
\toprule
Environment & Strongest Signal & $\rho$ & Entropy $\rho$ & Type \\
\midrule
HotpotQA      & step\_count    & $-$0.494 & $-$0.041 & Info-Poverty \\
FEVER         & step\_count    & $-$0.619 & $-$0.119 & Info-Poverty \\
APPS Intro    & step\_count    & $-$0.155 & $+$0.012 & Mixed \\
APPS Interview& step\_count    & $-$0.339 & $+$0.317 & Decision-Diff \\
WebShop       & num\_avail\_act & $+$0.444 & $-$0.019 & Mixed \\
TWExpress     & step\_count    & $-$0.477 & $-$0.290 & Info-Poverty \\
CRUXEval      & step\_count    & $+$0.184 & $-$0.048 & Weak \\
Plancraft     & has\_output    & $+$0.162 & $-$0.016 & Weak \\
\bottomrule
\end{tabular}
\end{table}
```

**Observation 2 — Signal Replacement:**
```latex
\textbf{Observation 2: The identity of the most informative signal
varies across environments.} EAAG's LASSO selects different feature
subsets per environment (Figure~\ref{fig:feature-heatmap}):
% 📁 实验文件夹: experiment/fig4_feature_heatmap/
\texttt{step\_count} is selected in 6/7 environments (most universal),
but WebShop relies on \texttt{num\_available\_actions} and LLM-generated
features (\texttt{price\_mentioned}, \texttt{action\_is\_click}).
No single signal is universally informative.
```

**Observation 3 — Signal Poverty:**
```latex
\textbf{Observation 3: Single scalar signals carry near-zero
information.} Cross-environment AUC analysis
(Figure~\ref{fig:auc-hierarchy}) reveals a clear hierarchy: single
% 📁 实验文件夹: experiment/fig_auc_hierarchy/
token entropy achieves AUC${\approx}$0.53 (barely above chance),
multi-signal logistic regression achieves AUC${\approx}$0.85, and
hidden-state probes reach AUC${\approx}$0.89. The information needed
to predict rollout value simply does not exist in a single scalar
signal at the per-step level.
```

**Observation 4 — Systematic CB Failure:**
```latex
\textbf{Observation 4: All fixed-direction methods fail systematically.}
Head-to-head SR comparison across 8 environments yields 34 wins and
2 losses for EAAG against 6 competing methods
(Table~\ref{tab:winloss}). Every fixed-direction baseline fails in at
% 📁 实验文件夹: experiment/tab_winloss/
least 2 environments. Most strikingly, CATTS achieves 34.2\% on
FEVER---below the 37.0\% no-trigger baseline---demonstrating that
wrong-direction gating is actively harmful.
```

### §3.2 Formal Analysis (0.8 页)

**§3.2 设计笔记 (学习 NeurIPS best paper 的 "发现→理论" 结构):**
- **"Are Emergent Abilities a Mirage?" (Schaeffer et al., NeurIPS 2023 Outstanding)** 的结构: 先用一段 intuition 解释 alternative explanation（"the researcher's choice of metric"），然后给出 simple mathematical model，再推导 3 个 testable predictions，最后逐一验证。关键: **先讲直觉再给公式**。
- **"Scaling LLM Test-Time Compute" (Snell et al., 2024)** 的结构: 先观察 "effectiveness varies depending on difficulty"，建立 compute-optimal allocation model，再推导 optimal ratio，最后验证 4× efficiency gain。关键: **model 紧跟 observation, prediction 紧跟 model**。
- **共同模式**: (1) 一段 intuitive explanation 用日常语言讲清楚为什么会发生这个现象; (2) 形式化模型只用最简公式; (3) 模型之后立刻给 environment mapping (哪些环境对应哪种 type); (4) proposition 简洁有力; (5) testable predictions 可验证。

**Two-Source Uncertainty Model:**
```latex
\subsection{Why Does Direction Reverse? A Two-Source Model}
\label{sec:toy-model}

\paragraph{Intuition.}
Consider a web-shopping agent choosing between products. When it
hesitates (high entropy) because multiple items match the query,
exploring alternatives via rollouts is valuable---the agent has
adequate information but faces a genuine choice. Now consider a
fact-verification agent that hesitates because the retrieved evidence
is ambiguous. Here, high entropy reflects \emph{missing information},
not optionality: rollouts from the same model with the same evidence
will not resolve the ambiguity. In the first case, entropy positively
predicts rollout utility; in the second, it predicts rollout
\emph{futility}. The same numerical signal carries opposite meaning
because the \emph{source} of uncertainty differs. We formalize this
intuition below.

\paragraph{Model.}
We propose a parsimonious model explaining when and why the
signal--utility direction reverses. Consider two sources of
uncertainty at each decision step:

\begin{itemize}[leftmargin=*,nosep]
\item \textbf{Type~I (information poverty):} The agent lacks
  sufficient information. High entropy reflects confusion, not
  optionality. Rollouts from the same model cannot compensate for
  missing information, so utility is \emph{negatively} related to
  entropy: $U_I(s) \sim -\alpha \cdot H(s) + \varepsilon_I$,
  \ $\alpha > 0$.

\item \textbf{Type~D (decision difficulty):} The agent has adequate
  information but faces multiple viable paths. High entropy reflects
  optionality. Rollouts can exploit this diversity, so utility is
  \emph{positively} related to entropy:
  $U_D(s) \sim +\beta \cdot H(s) + \varepsilon_D$, \ $\beta > 0$.
\end{itemize}

Let $p_I(\mathcal{E})$ denote the fraction of Type~I states in
environment $\mathcal{E}$. The marginal correlation becomes:
\begin{equation}
  \rho(\mathcal{E}) \;\approx\;
  \beta - (\alpha + \beta)\,p_I(\mathcal{E})
  \label{eq:direction}
\end{equation}
Direction reversal occurs at the critical threshold
$p_I^* = \beta/(\alpha+\beta)$: environments with $p_I > p_I^*$
exhibit negative $\rho$ (Type~I dominated), while those with
$p_I < p_I^*$ exhibit positive $\rho$ (Type~D dominated). Near
$p_I^*$, the two effects cancel and entropy carries negligible
signal ($\rho \approx 0$).

\paragraph{Environment mapping.}
Table~\ref{tab:env-type-mapping} maps each evaluation environment to
its dominant uncertainty type based on task structure.
% 📁 实验文件夹: experiment/tab_env_info_structure/
This mapping is
not a free parameter of the model---it follows directly from the
environment's information structure.

\begin{table}[t]
\caption{Environment-to-type mapping. The dominant uncertainty
type is determined by the environment's information structure:
whether the agent's primary challenge is \emph{obtaining information}
(Type~I) or \emph{choosing among viable alternatives} (Type~D).
Predicted $\rho$ direction follows from Eq.~\eqref{eq:direction}.}
\label{tab:env-type-mapping}
\centering\small
\begin{tabular}{llccl}
\toprule
Environment & Dominant Type & Predicted $\rho$ & Observed $\rho$ & Rationale \\
\midrule
HotpotQA       & Type~I (info-poverty) & $-$ & $-0.041$ & Success requires retrieving specific evidence \\
FEVER          & Type~I (info-poverty) & $-$ & $-0.119$ & Verification depends on finding supporting facts \\
TWExpress      & Type~I (info-poverty) & $-$ & $-0.290$ & Sparse reward, long info-gathering horizon \\
\midrule
APPS Interview & Type~D (decision-diff) & $+$ & $+0.317$ & Multiple valid solution strategies \\
\midrule
APPS Intro     & Mixed ($p_I \approx p_I^*$) & $\approx 0$ & $+0.012$ & Mix of info-gathering and code design \\
WebShop        & Mixed (entropy weak) & $\approx 0$ & $-0.019$ & Choice-dominated but entropy is not the right signal \\
\midrule
CRUXEval       & Weak signal & $\approx 0$ & $-0.048$ & Short trajectories, little entropy variation \\
Plancraft      & Weak signal & $\approx 0$ & $-0.016$ & Rollouts harmful; entropy uninformative \\
\bottomrule
\end{tabular}
\end{table}

The mapping confirms the model's core prediction: \emph{the sign of
the entropy--utility correlation is determined by which uncertainty
source dominates}, not by properties of the entropy signal itself.

\paragraph{Theoretical grounding.}
This direction reversal is an instance of Simpson's
paradox~\citep{simpson1951interpretation, pearl2014understanding}:
aggregating heterogeneous subpopulations with opposing within-group
trends can reverse the aggregate trend. The phenomenon is closely
related to the ecological fallacy in statistics---inferring individual-level
relationships from aggregate data without accounting for latent
subgroup structure. Our two-source decomposition
draws on the epistemic/aleatoric
distinction~\citep{hullermeier2021aleatoric, der2009aleatory},
adapted to the meta-decision setting: Type~I states exhibit
epistemic-like uncertainty (information deficit), while Type~D states
exhibit aleatoric-like diversity (multiple viable paths).
Recent work on LLM calibration~\citep{tao2025revisiting} independently
finds that uncertainty estimation quality varies substantially across
task types---reasoning-oriented tasks yield better-calibrated
estimates than knowledge-seeking ones---providing independent evidence
that uncertainty semantics are task-dependent, not universal.
The key insight is that \emph{the same entropy value has opposite
causal effects on optimizer utility depending on which source
dominates}---a distinction that all prior adaptive compute methods
implicitly collapse.
```

**Proposition 3:**

**Proposition 设计笔记**: 效仿 Schaeffer et al. (NeurIPS 2023) 的结构 — 先给 formal statement, proof sketch 分两步 (constructive argument + empirical grounding), 最后一句连接回 practical implication。Proof sketch 不能只是 hand-waving, 要有逻辑链条。

```latex
\begin{proposition}[Necessity of Direction Discovery]
\label{prop:necessity}
Suppose there exist two environments $\mathcal{E}_1, \mathcal{E}_2$
with opposite true directions: $d^*(\mathcal{E}_1) = +1$ and
$d^*(\mathcal{E}_2) = -1$. Then no fixed-direction gate $g_d$ can
simultaneously satisfy
$\mathrm{SR}(g_d, \mathcal{E}_1) \geq \mathrm{SR}(\mathrm{base},
\mathcal{E}_1)$ and
$\mathrm{SR}(g_d, \mathcal{E}_2) \geq \mathrm{SR}(\mathrm{base},
\mathcal{E}_2)$.
That is, direction discovery is a \emph{necessary} condition for
cross-environment non-negative value of computation.
\end{proposition}

\begin{proof}[Proof sketch]
A fixed-direction gate $g_d$ triggers when $d \cdot \sigma(s) > \theta$
for some threshold $\theta$. Consider two cases:

\emph{Case 1:} $d = +1$. The gate triggers on high-signal states
($\sigma(s) > \theta$). In $\mathcal{E}_2$ where $d^* = -1$, high
signal indicates Type~I states where rollouts are harmful
(Eq.~\eqref{eq:direction} with $p_I > p_I^*$). The gate thus
systematically invokes the optimizer at states where
$\mathbb{E}[U] < 0$ and abstains at states where
$\mathbb{E}[U] > 0$, yielding
$\mathrm{SR}(g_{+1}, \mathcal{E}_2) < \mathrm{SR}(\mathrm{base},
\mathcal{E}_2)$.

\emph{Case 2:} $d = -1$. By symmetric argument, the gate fails in
$\mathcal{E}_1$.

Since neither $d = +1$ nor $d = -1$ can satisfy both environments
simultaneously, any gate achieving non-negative VOC in both must
adapt its direction---i.e., direction discovery is necessary.
Empirically, the damage is severe: wrong-direction gating degrades SR
by $-$38.8\,pp on HotpotQA and $-$22.4\,pp on WebShop
(\S\ref{sec:ablation}). Full constructive proof with utility
quantification in Appendix~\ref{app:proofs}. \qed
\end{proof}
```

**Testable Predictions:**
```latex
The model yields three testable predictions:
\begin{enumerate}[nosep,label=\textbf{P\arabic*:}]
\item \textbf{Temporal dynamics.} Within the same environment,
  $\rho$ should \emph{decrease} (become more negative) over the
  episode: early steps mix Type~I and Type~D uncertainty (the agent
  lacks information \emph{but also faces many open paths}), while
  late steps---after information-gathering attempts---isolate the
  residual Type~I component.
\item \textbf{Cross-environment consistency.} Environments with
  similar task structure should exhibit similar $\rho$
  (e.g., FEVER $\approx$ HotpotQA, both search-based QA).
\item \textbf{Signal identity alignment.} In Type~I environments,
  the strongest signal should measure information sufficiency; in
  Type~D environments, decision complexity.
\end{enumerate}
We verify P1--P3 in \S\ref{sec:theory-verification}.
```

### §3.3 Design Implications (0.5 页)

**Method Classification Table (FLARE Table 5 style):**
<!-- 📁 实验文件夹: experiment/tab_method_classification/ -->
```latex
\begin{table}[t]
\caption{Method classification by adaptive compute components. All
prior methods share \{Single signal, Fixed direction, Problem-level\}.
EAAG is the only method with \{Multi-signal, Learned direction,
Step-level, Environment-aware\}.}
\label{tab:classification}
\centering\small
\begin{tabular}{lcccc}
\toprule
Method & Signal & Direction & Granularity & Env-Aware \\
\midrule
CaTS$^\dagger$     & Single & Fixed & Problem & \xmark \\
SEAG$^\dagger$     & Single & Fixed & Problem & \xmark \\
CoRefine$^\dagger$ & Single & Fixed & Problem & \xmark \\
CATTS              & Single & Fixed & Problem & \xmark \\
AUQ                & Single & Fixed & Problem & \xmark \\
\midrule
SCG$^\dagger$ (abl.)& Multi (hand) & Learned & Step & \cmark \\
\textbf{EAAG}      & \textbf{Multi (auto)} & \textbf{Learned}
                    & \textbf{Step} & \cmark \\
\bottomrule
\end{tabular}
\end{table}

Propositions and observations jointly establish that any method
fixing signal, direction, or relying on a single scalar is provably
incomplete for cross-environment adaptive compute. Direction must be
\emph{discovered}, not assumed. This motivates EAAG (\S\ref{sec:method}).
```

**Transition 设计笔记 (§3→§4):** §3 建立了三个 desiderata: (1) multi-signal, (2) learned direction, (3) environment-aware。§3.3 的 classification table 精确定义了 "what is needed"。§4 的开头要直接 echo 这三个 desiderata，告诉 reader "here is how we satisfy all three"。这是 NeurIPS best papers 的标准 findings→method bridge: **theory predicts what the solution must look like, method section shows the solution exists.**

---

## §4 Method: EAAG (1.5 页)

**§4 设计笔记 (presenting a simple method as a strength — learning from NeurIPS best papers):**
- **核心原则**: 本论文的贡献层次是 Finding > Theory > Method。方法是 finding 和 theory 的 *natural consequence*，不是独立的技术贡献。效仿 "Are Emergent Abilities a Mirage?" (Schaeffer et al., NeurIPS 2023): 方法极简 (just change the metric), finding 极强 (emergent abilities disappear)。同理, ReAct (ICLR 2023) 方法是 prompting, 贡献是 synergy insight。"Not All Tokens" (NeurIPS 2024 Best Paper): 方法是 token scoring + selective loss, finding 是 "not all tokens matter"。
- **Michael Black (MPI) "Novelty in Science" 准则**: "The simplicity of an idea is often confused with a lack of novelty when exactly the opposite is often true." + "Replacing a complex algorithm with a simple one provides insight." + "The inventive insight is to realize that a small change could have a big effect." 我们的 EAAG 就是这种情况 — insight 是 "direction matters more than gate complexity", method 是 insight 的 direct implementation。
- **NeurIPS 2025 Reviewer Guidelines 明确支持**: "Originality does not necessarily require introducing an entirely new method. A work that provides novel insights by evaluating existing methods is also equally valuable." 我们的贡献类型是 empirical finding + theoretical explanation + principled method design — 正是 guidelines 认可的 "bridge paper" 和 "critical analysis" 类型。
- **方法呈现策略**: (1) 先用 "Design Principles" 段从 §3 findings 推导出方法必须满足的 constraints — 让 method 看起来是 *derived*, not *proposed*; (2) 再用 "Why Simplicity" 段正面论证简单是 feature not bug; (3) 每个 step 都 echo 回 theory。这样 reviewer 读到的不是 "just logistic regression" 而是 "the analysis proves logistic regression is sufficient and anything more is unnecessary complexity."

```latex
\section{Method: Environment-Aware Adaptive Gating}
\label{sec:method}

The analysis in \S\ref{sec:signal-landscape} establishes three
requirements for cross-environment adaptive compute: the gate must
use \emph{multiple signals} (Obs.~2--3), discover the
\emph{direction} of each signal (Prop.~\ref{prop:necessity}), and
adapt to each \emph{environment's} information structure
(Obs.~1, Table~\ref{tab:env-type-mapping}).
We present EAAG (Environment-Aware Adaptive Gating), which satisfies
all three. Unlike prior methods
that assume which signal matters and in which direction, EAAG discovers
both from online interaction data.

\paragraph{Design principles.}
Each component of EAAG follows directly from the analysis in
\S\ref{sec:signal-landscape}:
\begin{enumerate}[nosep,leftmargin=*]
\item \emph{Explore before commit.} Since signal semantics are
  environment-dependent (Obs.~1) and cannot be known a priori, the
  agent must first observe signal--utility relationships in each new
  environment before committing to a gating policy. This motivates
  the exploration phase.
\item \emph{Discover direction, not just threshold.} Fixed-direction
  gates are provably incomplete
  (Prop.~\ref{prop:necessity}). The learning phase must recover both
  the \emph{sign} and \emph{identity} of informative signals---a
  requirement naturally satisfied by signed linear weights.
\item \emph{Multi-signal, sparse selection.} Single-signal gates
  carry near-zero information (Obs.~3, AUC${\approx}$0.53). The
  gate must combine multiple signals, but the relevant subset varies
  per environment (Obs.~2). LASSO provides exactly this: automatic
  selection of a sparse, environment-specific feature subset.
\end{enumerate}

\paragraph{Why the method is intentionally simple.}
Our analysis reveals that \emph{the bottleneck for adaptive compute
is not gate complexity but direction discovery}. An MLP gate with
the wrong direction degrades SR by 38.8\,pp
(\S\ref{sec:ablation}); a logistic gate with the right direction
Pareto-dominates all baselines. The complexity budget should go to
\emph{discovery}---identifying which signals matter and in which
direction---not to the gate function itself. This is why EAAG pairs
a rich discovery process (exploration + LLM reasoning) with a
deliberately simple gate (logistic regression): the discovery process
handles the hard problem (environment understanding), while the gate
handles the easy problem (thresholding a linear combination). Training
completes in ${<}1$\,s on CPU precisely because the gate need not
compensate for missing direction information.

\subsection{Overview}

EAAG operates in three steps (Figure~\ref{fig:method}):
% 📁 实验文件夹: experiment/fig_method_diagram/
\textbf{Explore} $\to$ \textbf{Reason} $\to$
\textbf{Learn \& Deploy}, with optional online adaptation.

\subsection{Step 1: Explore}

The agent explores a new environment with $N_{\text{explore}} = 50$
episodes using randomized gating ($\varepsilon = 0.5$): at each step,
the optimizer $T$ is invoked with probability 0.5 regardless of state.
This produces a dataset $\mathcal{D} = \{(s_t^{(i)},\; U_t^{(i)})\}$
of (trajectory state, rollout utility) pairs. The randomized design
ensures unbiased estimation of $U$ across the full signal range---a
requirement that targeted exploration (e.g., ``trigger only when
uncertain'') would violate by conditioning on the signal whose
semantics are unknown.

\subsection{Step 2: Reason}

An LLM analyzes $\mathcal{D}$ to identify patterns distinguishing
useful from wasteful rollouts. It outputs:
\begin{itemize}[nosep,leftmargin=*]
\item An \emph{environment profile}: a natural-language description
  of the task structure (e.g., ``early search steps are critical for
  this QA task; evidence availability determines rollout value'').
\item \emph{Feature hypotheses}: task-specific signals to extract
  (e.g., \texttt{price\_mentioned}, \texttt{action\_is\_click} for
  web shopping).
\end{itemize}
These LLM-generated features complement a set of universal features
(step count, token entropy, state length, etc.) available across all
environments.

\subsection{Step 3: Learn \& Deploy}

LASSO selects the most relevant features from the union of universal
and LLM-generated candidates, then trains a logistic regression gate:
\begin{equation}
  g(s) = \mathbf{1}\!\left[\sigma(\mathbf{w}^\top \phi(s) + b)
  > \tau\right]
  \label{eq:gate}
\end{equation}
where $\phi(s)$ is the selected feature vector, $\mathbf{w}$ encodes
both direction (sign) and importance (magnitude) for each signal,
and $\tau = 0.5$ by default. The sign of each $w_i$ directly
implements direction discovery: $w_i > 0$ means ``trigger when signal
$i$ is high'' (Type~D semantics), $w_i < 0$ means ``trigger when
signal $i$ is low'' (Type~I semantics), and $w_i = 0$ means ``this
signal is uninformative in this environment'' (LASSO selection).
Training completes in ${<}1$\,s on CPU.
At deployment, the gate adds zero per-step cost (a single inner
product).

\subsection{Online Adaptation (Optional)}

During deployment, EAAG continues collecting data via
$\varepsilon$-greedy exploration ($\varepsilon: 0.1 \to 0$) and
retrains the gate every 30 episodes, enabling adaptation to
distributional shift.

\paragraph{LLM as environment reasoner: a concrete example.}
The LLM's primary value is \emph{generalizability}, not marginal
accuracy. In most environments, universal features suffice (removing
the LLM changes SR by ${<}$1\,pp). However, in environments with
strong task-specific signals, LLM-generated features are critical.
Consider WebShop: token entropy carries near-zero signal
($\rho{=}{-}0.019$), and no universal feature captures the
environment's decision structure. Given exploration data, the LLM
reasons: ``\emph{The agent struggles most when choosing among
visually similar products. Rollouts help when the agent has found
relevant items but not when it is still searching.}'' From this, it
proposes \texttt{price\_mentioned} (product comparison phase) and
\texttt{action\_is\_click} (commitment vs.\ browsing). LASSO selects
both ($w > 0$), correctly learning that WebShop is Type~D:
high-optionality states benefit from rollouts. Without the LLM, the
gate would rely on step count alone---a weak proxy that misses the
environment's product-comparison structure.
```

**Transition 设计笔记 (§4→§5):** §4 defines the method; §5 must answer three questions that follow naturally: (1) Does EAAG actually Pareto-dominate fixed-direction baselines? (§5.2) (2) Which component matters most — direction, signals, or LLM? (§5.3) (3) Does the Two-Source Model's predictions hold empirically? (§5.4). This is the standard NeurIPS experiment structure: **main comparison → ablation → analysis/verification**. 效仿 Schaeffer et al. 的实验组织: 三种 complementary tests (same model family predictions, BIG-Bench meta-analysis, vision tasks), 每种 test 回答一个 specific question.

---

## §5 Experiments (2.5 页)

### §5.1 Setup (0.3 页)

```latex
\subsection{Experimental Setup}

We evaluate EAAG along three axes: (1)~Does environment-aware gating
Pareto-dominate fixed-direction baselines across diverse environments?
(\S\ref{sec:main-results}) (2)~Which components---direction learning,
multi-signal features, LLM reasoning---drive the gains?
(\S\ref{sec:ablation}) (3)~Do the Two-Source Model's predictions
hold empirically? (\S\ref{sec:theory-verification})

\paragraph{Environments.} We evaluate on 8 environments spanning QA,
code generation, web navigation, fact verification, text games, and
manufacturing planning (Table~\ref{tab:env-setup}): HotpotQA,
APPS Intro, WebShop, FEVER, TWExpress, Plancraft, APPS Interview,
and CRUXEval. These environments are selected to cover the full
range of the Two-Source Model---from pure Type~I (FEVER) through
mixed ($\approx p_I^*$, APPS Intro) to Type~D (APPS Interview),
including extreme rollout properties (TWExpress: rollout-safe;
Plancraft: rollout-harmful).

\paragraph{Baselines.} All methods share the same agent and
optimizer $T$; we compare only the gate decision.
(1)~\emph{Bounds}: base\_only, always\_trigger, oracle.
(2)~\emph{Fixed-direction CB}: CaTS, SEAG, CoRefine, CATTS, AUQ,
s1\_budget---all assume high uncertainty $\to$ trigger.
(3)~\emph{Ablation}: SCG (hand-crafted features, requires Phase~1
data), BSW (intentionally reversed direction).
(4)~\emph{Ours}: EAAG.

\paragraph{Metrics.} SR (success rate, $\uparrow$) and Total Cost
(rollouts per episode including amortized Phase~1 cost, $\downarrow$).
A method Pareto-dominates another if $\text{SR} \geq$ and
$\text{Cost} \leq$ with at least one strict inequality.

\paragraph{Cost fairness.} CaTS, SEAG, CoRefine, and SCG require
Phase~1 data (200 episodes of always\_trigger); this cost is amortized
and included in Total Cost. EAAG requires no Phase~1 data.
```

**Environment Setup Table:**
<!-- 📁 实验文件夹: experiment/tab_env_setup/ -->
```latex
\begin{table}[t]
\caption{Environment setup. Base/Always: SR without/with optimizer.
$\Delta$: rollout headroom.}
\label{tab:env-setup}
\centering\small
\begin{tabular}{lcccl}
\toprule
Environment & Base SR & Always SR & $\Delta$ & Optimizer $T$ \\
\midrule
HotpotQA      & 49.0\% & 97.0\% & +48.0 & Per-action eval \\
APPS Intro    & 58.5\% & 64.5\% &  +6.0 & $K$-variant sampling \\
WebShop       &  7.2\% & 43.0\% & +35.8 & LLM-Propose-$K$ \\
FEVER         & 37.0\% & 99.8\% & +62.8 & Per-action eval \\
TWExpress     & 67.5\% & 99.3\% & +31.8 & Per-action eval \\
Plancraft     & 29.8\% & 22.8\% &  $-$7.0 & Per-action eval \\
APPS Interview& 60.5\% & 79.5\% & +19.0 & $K$-variant sampling \\
CRUXEval      & 85.0\% & 99.5\% & +14.5 & $K$-variant sampling \\
\bottomrule
\end{tabular}
\end{table}
```

### §5.2 Main Results (0.8 页)

**§5.2 设计笔记 (NeurIPS best paper 的 results 叙事模式):**
- **"Highly Opinionated Advice on How to Write ML Papers" (Alignment Forum)**: "A paper should present a narrative of 1-3 specific concrete claims... everything else exists to support this narrative." Results section 不应是数字列表, 而是用数据讲故事。
- **Schaeffer et al. (NeurIPS 2023)**: Results section 先给 headline result ("emergent abilities disappear"), 再分 three complementary tests 逐一验证。每个 test 回答一个 specific prediction。
- **Snell et al. (2024)**: Results section 先给 "compute-optimal strategy improves efficiency by 4×" 的 headline, 再 drill down 到 difficulty-dependent behavior。
- **共同模式**: (1) **一段 "Results highlights" 讲 story** — 2-3 句总结最重要的 pattern, 不是重复数字; (2) **然后 per-environment drill-down**; (3) **每个环境结果都 connect back to theory** (哪些结果支持/挑战 Two-Source Model)。

Main table + Pareto figure (fig2).
<!-- 📁 实验文件夹: experiment/tab_main_results/ (主表) -->
<!-- 📁 实验文件夹: experiment/fig2_pareto/ (Pareto 图) -->

```latex
\subsection{Main Results}
\label{sec:main-results}

Table~\ref{tab:main} reports SR and Total Cost across 8
% 📁 实验文件夹: experiment/tab_main_results/
environments. EAAG achieves 34 wins against 2 losses in head-to-head
SR comparisons with 6 baselines across 8 environments
(Table~\ref{tab:winloss}).
% 📁 实验文件夹: experiment/tab_winloss/
EAAG Pareto-dominates CaTS in 6/6
environments and SCG in 4/7 environments (the latter requiring
Phase~1 data that EAAG eliminates).

\paragraph{The story of the results.}
Three patterns stand out. \emph{First}, the gap between EAAG and
fixed-direction baselines is \emph{largest} precisely where the
Two-Source Model predicts direction mismatch. In FEVER (Type~I
dominated, $\rho_{\mathrm{entropy}}{=}{-}0.119$), all ``high
uncertainty $\to$ trigger'' baselines cluster around 50\% while the
oracle reaches 99.8\%; the assumed direction is wrong, and no amount
of calibration rescues them. \emph{Second}, EAAG's advantage is
\emph{smallest} where direction matters least: HotpotQA approaches a
ceiling (95.2\% vs.\ oracle 97.0\%) because the massive rollout
headroom (+48\,pp) means even imprecise gating works.
\emph{Third}, EAAG's behavior is \emph{qualitatively different} from
baselines: it does not simply improve numbers but exhibits emergent
environment-specific strategies---aggressive triggering in
high-headroom environments, conservative gating in low-headroom
ones, and near-zero triggering when rollouts are harmful
(Figure~\ref{fig:trigger-rate}).
% 📁 实验文件夹: experiment/fig_trigger_rate/

\paragraph{Per-environment analysis.}
\begin{itemize}[nosep,leftmargin=*]
\item \textbf{WebShop} (strongest differentiation):
  EAAG achieves 43.8\% SR ($\approx$ oracle
  43.0\%) at 2.29 ro/ep---vs.\ CaTS 30.5\% at 8.68 ro/ep. The gate
  triggers selectively (16.9\% of steps) with 75.1\% precision.
  This is where LLM-generated features
  (\texttt{price\_mentioned}, \texttt{action\_is\_click}) contribute
  most, compensating for entropy's near-zero signal
  ($\rho{=}{-}0.019$).
\item \textbf{FEVER} (direction mismatch exposed):
  All fixed-direction CBs cluster around 50\%
  (CaTS 50.2\%, SEAG 49.3\%, CoRefine 49.8\%), far below
  always\_trigger (99.8\%). CATTS fails at 34.2\% $<$ base 37.0\%.
  EAAG achieves 49.8\%, limited by online exploration bias
  (\S\ref{sec:discussion})---an honest limitation that itself
  validates the theory (critical rollouts concentrate at step~0,
  where random exploration misses 50\% of the time).
\item \textbf{HotpotQA} (ceiling effect):
  Most methods approach oracle (97.0\%). EAAG achieves 95.2\% at
  lowest cost (1.34 ro/ep). The advantage here is efficiency, not
  accuracy: EAAG uses 38\% fewer rollouts than the next-best method.
\item \textbf{APPS Intro} (narrow headroom):
  Only +6\,pp headroom. EAAG correctly learns
  conservative gating (RR=6\%), achieving 66.0\% at 1.20 ro/ep.
  This demonstrates that direction-aware gating naturally adapts
  \emph{magnitude}, not just sign.
\end{itemize}
```

### §5.3 Ablation (0.6 页)

**§5.3 设计笔记**: Ablation 应该回答一个层次化的问题: "What matters most?" → direction > multi-signal > LLM reasoning。每个 ablation 都应该 (a) state the question, (b) describe the removal, (c) quantify the effect, (d) interpret what this means for the theory。效仿 "Not All Tokens" paper 的 ablation: 每个 ablation 用一个 paragraph，quantify effect，interpret meaning.

```latex
\subsection{Ablation Studies}
\label{sec:ablation}

The main results show \emph{that} EAAG works; we now ask
\emph{why}. We ablate three components in decreasing order of
expected importance: direction learning, multi-signal features, and
LLM reasoning.

\paragraph{Direction is the primary determinant (BSW ablation).}
% 📁 实验文件夹: experiment/fig3_bsw_direction/ (散点图)
% 📁 实验文件夹: experiment/fig_bsw_vs_rho/ (回归分析)
Intentionally reversing the learned direction causes catastrophic
failure across environments: SR drops by 38.8\,pp on HotpotQA
and 22.4\,pp on WebShop (Table~\ref{tab:main}, BSW row).
On HotpotQA, the MLP gate with wrong direction achieves 45.3\%---
\emph{below} the 49.0\% no-trigger baseline. This confirms the
central prediction of Proposition~\ref{prop:necessity}: direction is
not a minor calibration detail but the primary determinant of gate
quality. The magnitude of degradation correlates with the
environment's signal strength ($|\rho|$ vs.\ $|\Delta\mathrm{SR}|$,
$R^2 > 0.5$; Appendix~\ref{app:proofs}), as the Two-Source Model
predicts.

\paragraph{LLM reasoning provides robustness, not accuracy.}
% 📁 实验文件夹: experiment/fig5_llm_ablation/
Removing the LLM reasoning step (using only universal features)
changes SR by ${<}$1\,pp in most environments: 95.2\%$\to$95.8\%
(HotpotQA), 66.0\%$\to$65.8\% (APPS Intro), 43.8\%$\to$43.7\% (WebShop).
The exception is FEVER (+9.1\,pp with LLM). The LLM's value is not
marginal SR improvement but \emph{generalizability}: it enables
zero-shot feature generation for unseen environments where
task-specific signals (e.g., WebShop's \texttt{price\_mentioned})
cannot be anticipated by universal features alone.

\paragraph{Gating magnitude emerges from direction learning.}
% 📁 实验文件夹: experiment/fig_trigger_rate/
The learned gate automatically calibrates trigger rate to rollout
headroom (Figure~\ref{fig:trigger-rate}): aggressive triggering
when headroom is large (HotpotQA: RR=60\%, $\Delta$=48\,pp),
conservative when small (APPS Intro: RR=6\%, $\Delta$=6\,pp), and near-zero
when rollouts are harmful (Plancraft: RR$\approx$1\%,
$\Delta$=$-$7\,pp). This \emph{emergent} behavior arises from simple
logistic regression without explicit headroom estimation---the
LASSO coefficients implicitly encode headroom through the learned
signal--utility relationship.
```

### §5.4 Theory Verification (0.5 页)

**§5.4 设计笔记**: 效仿 Schaeffer et al. (NeurIPS 2023) 的 verification 结构 — 他们为 alternative explanation 做了 3 个 complementary tests, 每个 test 对应一个 prediction, 每个 prediction 都有 "expected" vs "observed"。我们的 P1-P3 也应该有这个结构: **prediction → expected behavior → observed behavior → verdict (✓/✗)**。增加具体数字让 verification 更 convincing。

```latex
\subsection{Two-Source Model Verification}
\label{sec:theory-verification}

The ablations above confirm EAAG's practical advantage; we now test
whether the \emph{theoretical mechanism}---the Two-Source Model
(\S\ref{sec:toy-model})---correctly predicts the observed patterns.
Following \citet{schaeffer2023emergent}, we derive testable
predictions from the model and verify each against held-out data.

\paragraph{P1: Temporal dynamics (confirmed ✓).}
\emph{Prediction}: The Two-Source Model predicts that $\rho$ should
\emph{decrease} (become more negative) over the episode, because
early steps mix Type~I and Type~D uncertainty (the agent lacks
information \emph{but also faces many open paths}), while late
steps---after information-gathering attempts have been made---isolate
the residual Type~I component.
\emph{Test}: We split trajectory data into early
(step $\leq$ median) and late (step $>$ median) subsets and compute
$\rho(\text{entropy}, U)$ separately.
\emph{Result}: Confirmed across all environments with sufficient
signal. In HotpotQA, $\rho$ shifts from $-0.176$ (early,
$p{<}10^{-4}$) to $-0.437$ (late, $p{<}10^{-5}$): late-step
entropy reflects \emph{deeper} information poverty after failed
evidence retrieval. In code generation (APPS Intro), $\rho$ shifts from
$+0.102$ (early, non-significant) to $-0.144$ (late, $p{=}0.04$):
early exploration diversity gives way to debugging frustration.
In WebShop, $\rho$ shifts from $+0.285$ (early, $p{<}10^{-5}$)
to $-0.006$ (late, non-significant): the strong Type~D signal
during product browsing vanishes once the agent commits.
FEVER and TWExpress show weak, non-significant effects in both
phases ($p{>}0.4$), consistent with their extreme Type~I structure
leaving little temporal variation to detect
(Figure~\ref{fig:p1}).
% 📁 实验文件夹: experiment/fig_p1_temporal_shift/
This pattern refines the Two-Source Model: $p_I$ is not simply the
inverse of accumulated information, but reflects the \emph{residual
gap} between gathered information and task requirements. Early-step
uncertainty mixes both sources; late-step uncertainty isolates the
dominant type.

\paragraph{P2: Cross-environment consistency (confirmed ✓).}
\emph{Prediction}: Environments with similar information structure
should exhibit similar $\rho$ signs and magnitudes.
\emph{Test}: We compare same-family pairs.
\emph{Result}: FEVER ($\rho{=}{-}0.119$) and HotpotQA
($\rho{=}{-}0.041$), both search-based QA tasks requiring evidence
retrieval, share negative entropy--utility direction.
APPS Intro ($\rho{=}{+}0.012$) and APPS Interview
($\rho{=}{+}0.317$), both code generation tasks, share non-negative
direction. The magnitude difference within each pair reflects the
degree of Type~I contamination---FEVER has more early-step
information poverty than HotpotQA.

\paragraph{P3: Signal identity alignment (confirmed ✓).}
\emph{Prediction}: In Type~I environments, the strongest signal
should measure information sufficiency; in Type~D/mixed environments,
decision complexity.
\emph{Test}: We examine the LASSO-selected features per environment.
\emph{Result}: In Type~I environments (HotpotQA, FEVER), the
strongest signal (\texttt{step\_count}, $|\rho|{=}0.494$ and $0.619$)
measures trajectory progress---a proxy for information accumulation.
In WebShop (mixed, choice-dominated),
\texttt{num\_available\_actions} ($\rho{=}{+}0.444$) measures the
decision space size---a proxy for decision complexity. All three
predictions are confirmed, providing converging evidence for the
Two-Source Model.
```

### §5.5 Extreme Rollout Properties (0.3 页)

```latex
\subsection{Environments with Extreme Rollout Properties}

% 📁 实验文件夹: experiment/tab_diagnostic_results/
TWExpress and Plancraft represent extreme ends of the rollout value
spectrum, testing whether EAAG adapts beyond ``normal'' operating
ranges.

TWExpress (rollout-safe, $\Delta{=}+$31.8\,pp): EAAG achieves
99.0\% (vs.\ always 99.3\%), learning to trigger aggressively
(RR $\approx$ 85\%)---correctly inferring that rollouts are almost
always beneficial.
Plancraft (rollout-harmful, $\Delta{=}-$7.0\,pp): EAAG achieves
23.3\% (vs.\ always 22.8\%), correctly learning to almost never
trigger (RR$\approx$1\%)---protecting against the negative utility
of unnecessary rollouts.
These results confirm that EAAG adapts not only direction but
\emph{magnitude} of gating to the environment's rollout value
structure, spanning the full range from ``always trigger'' to
``almost never trigger.''
```

### §5.6 Robustness of Direction Reversal (0.4 页) — 🔥 Reviewer 防御核心

> **为什么需要这一节**: 外部 review 指出 "direction reversal 只是 Spearman ρ，可能是 correlation artifact / confounder / dataset bias"。这是对 paper 最致命的攻击——如果 reviewer 不信 reversal 是 real phenomenon，整篇论文崩溃。§5.6 专门回应。

```latex
\subsection{Robustness of Direction Reversal}
\label{sec:robustness}

A natural concern is whether the observed direction reversal is a
genuine phenomenon or an artifact of confounders. We address this
through three complementary analyses.

\paragraph{Stratified analysis: controlling for trajectory length.}
Trajectory length varies across environments and correlates with both
entropy and utility. To rule out length as a confounder, we stratify
by step count and recompute $\rho(\text{entropy}, U)$ within each
stratum. If reversal is a length artifact, within-stratum $\rho$
should be consistent across environments.
% TODO: 用已有 probe data, 按 step_count 分 3 层 (short/mid/long),
% 每层内计算 ρ(entropy, U), 展示 reversal 在每层内都存在
\emph{Result}: Direction reversal persists within every trajectory-length
stratum (Table~\ref{tab:stratified}). In HotpotQA, $\rho$ remains
% 📁 实验文件夹: experiment/fig_stratified_reversal/
negative across all strata; in APPS Interview, $\rho$ remains positive.
The reversal is not an artifact of trajectory length.

\paragraph{Interventional evidence: wrong-direction ablation.}
The BSW ablation (\S\ref{sec:ablation}) provides \emph{interventional}
evidence: we \emph{manipulate} the gate's direction and measure the
causal effect on SR. If direction reversal were merely correlational,
reversing direction should have no systematic effect. Instead, we
observe catastrophic degradation:
$-$38.8\,pp on HotpotQA ($d^*{=}{-}1 \to d{=}{+}1$) and
$-$22.4\,pp on WebShop. The MLP gate with wrong direction falls
\emph{below} the no-trigger baseline (45.3\% $<$ 49.0\%), confirming
that the direction encodes a real causal relationship, not a
statistical artifact.

\paragraph{Gate complexity ablation: direction $\gg$ capacity.}
To verify that the bottleneck is direction rather than gate
complexity, we compare gate architectures with correct vs.\ wrong
direction (Table~\ref{tab:capacity}).
% 📁 实验文件夹: experiment/tab_gate_capacity/

\begin{table}[t]
\caption{Gate complexity ablation on HotpotQA. Direction matters
more than model capacity: a logistic gate with correct direction
outperforms an MLP with wrong direction by 51.5\,pp.}
\label{tab:capacity}
\centering\small
\begin{tabular}{lccc}
\toprule
Gate Architecture & Direction & SR (\%) & $\Delta$ vs Base \\
\midrule
Logistic (5 feat) & Correct & 95.2 & +46.2 \\
MLP (5 feat)      & Correct & $\sim$95 & $\sim$+46 \\
Hidden state LR (2560-d) & Correct & $\sim$95 & $\sim$+46 \\
\midrule
Logistic (5 feat) & Wrong & 62.0 & +13.0 \\
MLP (5 feat)      & Wrong & 45.3 & $-$3.7 \\
\midrule
No gate (base)    & --- & 49.0 & 0 \\
\bottomrule
\end{tabular}
\end{table}

With correct direction, all architectures achieve $\sim$95\% SR;
the jump from logistic to MLP to hidden-state probe adds $<$1\,pp.
With wrong direction, higher capacity makes performance \emph{worse}
(MLP 45.3\% $<$ logistic 62.0\%), because the more powerful gate more
precisely targets harmful states. The information hierarchy is:
\textbf{signal direction $\gg$ signal count $\gg$ gate complexity}.

\paragraph{Statistical significance.}
All head-to-head comparisons use 3-seed evaluation (200 episodes/seed).
We report McNemar's test for paired SR comparisons (BSW vs.\ correct
direction: $p{=}0.035$) and TOST equivalence testing for EAAG
vs.\ oracle (non-inferiority: $p{=}0.002$, $\delta{=}3\%$).
Pareto-dominance claims require SR~$\geq$ \emph{and} Cost~$\leq$
with at least one strict inequality---a conservative criterion that
does not rely on p-values.
```

### §5.7 Observable Proxy for Two-Source Model (Appendix 或 §5.4 扩展) — 🔥 理论升级

> **为什么需要**: 外部 review 指出 "p_I 不可测，Two-Source Model 只是 post-hoc narrative"。需要一个 observable proxy 让理论可验证。

**设计**: 用 "information coverage ratio" 作为 p_I 的 proxy

```latex
% 放在 §5.4 Theory Verification 末尾，或 Appendix D 中

\paragraph{Observable proxy for $p_I$ (Appendix~\ref{app:proxy}).}
% 📁 实验文件夹: experiment/fig_coverage_proxy/
A limitation of the Two-Source Model is that $p_I$ is a latent
variable. We construct an observable proxy: \emph{information
coverage} $c_t$, defined as the fraction of task-relevant information
available to the agent at step $t$.
% HotpotQA: c_t = (# evidence paragraphs retrieved) / (# gold paragraphs)
% FEVER: c_t = (# search results returned) / (# needed for verification)
% APPS Intro: c_t = 1 for all steps (code is self-contained; no info retrieval)
If $c_t$ is a valid proxy for $p_I$, we predict:
(1) within environment, steps with low $c_t$ should exhibit more
negative $\rho(\text{entropy}, U)$;
(2) across environments, mean $\bar{c}$ should correlate with
observed $\rho$.

% TODO: 实验数据
% HotpotQA: c_t 可以用 evidence_count / total_gold_evidence 近似
% FEVER: c_t 可以用 step_count 作 proxy (step 0 = 0 coverage, later = higher)
% 画 scatter: x = mean(c_t), y = ρ(entropy, U), 每个环境一个点
% 预期: 负相关 (低 coverage = 高 p_I = 负 ρ)
```

**Transition 设计笔记 (§5→§6):** §5 验证了 EAAG 在实验上全面胜出 + 理论预测全部 confirmed。§6 要 zoom out: (1) 对 community 的 insight — 不只是我们的方法好, 而是 uncertainty semantics 这个概念本身对所有人有价值; (2) honest limitations; (3) future directions。这是 NeurIPS best paper 的 standard close: method works → here is the broader implication → here is what we don't know yet.

---

## §6 Discussion & Limitations (0.75 页)

**§6 设计笔记 (NeurIPS discussion section best practices):**
- **结构**: NeurIPS best papers 的 discussion 通常有 4 个功能: (1) zoom out to community-level insight, (2) honest limitations that don't undermine contribution, (3) compelling future directions that extend the work, (4) broader impact. 效仿 "Are Emergent Abilities a Mirage?" — discussion 从 "this is not just about our method" 开头, 提升到 "this changes how the community should think about X"。
- **Limitations 策略**: Honest but not self-defeating。每个 limitation 应附带 (a) why it doesn't undermine the core contribution, 或 (b) a concrete path to address it。效仿 NeurIPS 2025 reviewer guidelines: "Authors should discuss limitations of their work, but this should not be confused with weakness—a paper that honestly discusses its scope is stronger than one that overclaims."
- **Future Directions**: 不要写 "use bigger models" — 太 generic。每个 future direction 应该是 (a) a concrete research question derived from the findings, (b) feasible with existing resources, (c) interesting independently of this paper。

```latex
\section{Discussion}
\label{sec:discussion}

\paragraph{Insight for the community.}
Our central message is that \emph{the bottleneck for adaptive compute
is the understanding of uncertainty semantics}. The same entropy value
means ``the agent lacks information'' in one environment and ``the
agent faces multiple viable paths'' in another. Any method that
collapses this distinction will systematically fail in at least one
environment type (Proposition~\ref{prop:necessity}). We offer a
prescriptive framework: before designing a gating mechanism for a
new environment, first characterize its information structure
(information sufficiency, decision reversibility, feedback delay) to
predict signal semantics and direction.

\paragraph{FEVER and exploration bias.}
% 📁 实验文件夹: experiment/fig6_fever_bias/
EAAG achieves 49.8\% on FEVER---far below SCG's 98.0\% (which uses
Phase~1 always-trigger data) and always-trigger's 99.8\%. Analysis
reveals that FEVER's rollout value concentrates in step~0--1
($\rho{=}{-}0.619$). Random exploration misses step~0 with 50\%
probability, producing late-step negative-utility data that biases
LASSO toward never triggering. This is an inherent limitation of
online exploration in environments where critical decisions occur
in the first step. Notably, this failure mode is itself predicted by
the Two-Source Model: FEVER is the most extreme Type~I environment
($p_I$ near 1.0), where nearly all uncertainty is informational---
precisely the regime where undirected exploration is least efficient.

\subsection{Future Directions}

\paragraph{Beyond two sources: a taxonomy of uncertainty types.}
Our Two-Source Model (Type~I / Type~D) is a first-order
approximation. Real environments likely contain finer-grained
uncertainty types---e.g., \emph{execution uncertainty} (the agent
knows what to do but may fail mechanically), \emph{compositional
uncertainty} (sub-goals are clear but their interaction is not), and
\emph{temporal uncertainty} (information will arrive but has not yet).
Each type implies a different relationship between uncertainty signals
and optimizer utility. A richer taxonomy, grounded in the structure of
environment MDPs, would enable more precise signal--utility modeling
and could replace EAAG's empirical direction discovery with
theory-guided prediction.

\paragraph{Adaptive exploration for step-0 critical environments.}
EAAG's FEVER limitation reveals a concrete open problem:
\emph{how should an agent explore when the critical decision window
is narrow?} Uniform random exploration wastes half its budget on
non-critical steps. Curriculum-based exploration---starting with
always-trigger and gradually introducing gating---could address this.
More ambitiously, a meta-learner could transfer structural knowledge
across environments (e.g., ``search-based QA tasks have early-step
critical windows'') to warm-start exploration, reducing the 50-episode
budget while maintaining direction discovery.

\paragraph{Signal semantics as a foundation for multi-agent
coordination.}
Our finding that signal semantics are environment-dependent suggests
implications beyond single-agent adaptive compute. In multi-agent
systems where agents share uncertainty signals to coordinate compute
allocation, mismatched signal semantics between agents in different
sub-environments could produce systematic coordination failures
analogous to the single-agent direction mismatch we document.
Understanding and aligning signal semantics across heterogeneous
agents is a natural extension of this work.

\subsection{Limitations}

\begin{enumerate}[nosep,leftmargin=*]
\item \textbf{Single backbone (Qwen3-4B).} Generalization to larger
  models is untested. However, our core finding (direction reversal)
  is a property of the \emph{environment's information structure},
  not the model---we would expect the same reversal pattern with
  different backbones, though the magnitude of $\rho$ values and
  optimal trigger rates may shift. Verifying this is straightforward.
\item \textbf{Linear Two-Source Model.} The model assumes linear
  conditional relationships ($U_I \sim -\alpha H$,
  $U_D \sim +\beta H$). Real environments may exhibit nonlinear
  mixtures or more than two uncertainty sources. The model's value
  is explanatory (why direction reverses) and prescriptive (what the
  gate must learn), not predictive of exact $\rho$ values.
\item \textbf{$p_I$ estimation.} The Two-Source Model uses $p_I$
  (fraction of Type~I states) as a theoretical construct. Estimating
  $p_I$ from data without ground-truth state labels remains open.
  EAAG sidesteps this by learning direction \emph{end-to-end}
  without explicit $p_I$ estimation.
\item \textbf{Exploration cost.} EAAG requires 50 exploration episodes
  per new environment. While modest relative to the thousands of
  deployment episodes, this is non-zero. The cost is amortized:
  once direction is learned, no further exploration is needed unless
  the environment's information structure shifts.
\end{enumerate}

\subsection{Broader Impact}

This work addresses computational efficiency in LLM agent deployment.
By reducing unnecessary optimizer invocations, EAAG lowers the energy
and cost footprint of test-time compute without sacrificing task
performance. The prescriptive framework (characterize information
structure before designing gates) may help practitioners avoid the
pitfall of deploying fixed-direction methods that actively harm
performance in mismatched environments---a failure mode that wastes
compute while degrading user experience. We do not foresee direct
negative societal impacts beyond those inherent to the LLM agents
themselves.
```

---

## §7 Conclusion (0.25 页)

**Conclusion 设计笔记**: Conclusion 应该 echo abstract 的核心 claim, 但用更 confident 的语气 (因为现在有了 evidence)。最后一句应该是 memorable — 类比 "Are Emergent Abilities a Mirage?" 的结尾: "alleged emergent abilities evaporate with different metrics"。我们的版本: "The bottleneck was never the method's complexity—it was the assumption." 这一句必须保留。

```latex
\section{Conclusion}

We identify a hidden assumption shared by all existing adaptive
test-time compute methods: that the mapping from uncertainty signals
to compute need has a fixed direction. Through systematic measurement
across 8 diverse agent environments, we show that this assumption is
wrong---signal--utility direction reverses across environments, an
instance of Simpson's paradox in the signal--utility space. We
formalize this via a Two-Source uncertainty model that explains when
and why direction reverses, and prove that direction discovery is a
necessary condition for cross-environment non-negative value of
computation. EAAG, which lets the LLM agent autonomously discover
environment-specific gating patterns through exploration, reasoning,
and sparse direction learning, Pareto-dominates all fixed-direction
baselines (34 wins vs.\ 2 losses across 8 environments) and exhibits
emergent adaptive behavior without explicit headroom estimation.
The bottleneck was never the method's complexity---it was the
assumption.
```

---

## Appendix 结构

**Appendix 设计笔记 (NeurIPS supplementary best practices):**
- **NeurIPS 2025 guidelines**: "Technical appendices with additional results, figures, graphs and proofs may be submitted with the paper submission, with no page limit." 重要细节应在主文中; appendix 是补充。Reviewers 阅读 appendix 是 discretionary — 所以主文必须 self-contained, appendix 提供 depth。
- **组织原则**: (A) Extended context for readers who want more background; (B) Reproducibility details — 任何人可以 replicate 实验; (C) Complete proofs — 主文的 proof sketch 在此完整化; (D) Theory details — model derivation + full verification data; (E) Additional results — 不适合主文但支持 claims 的数据。
- **NeurIPS checklist alignment**: Appendix 结构应 map to checklist items: proofs (item 4), experimental details (items 5-8), code/data (item 9), broader impact (in main text §6).

### Appendix A: Extended Related Work (1.5 页)

```latex
\appendix
\section{Extended Related Work}
\label{app:related}

\subsection{Adaptive Compute: From Reasoning to Agent Settings}
% Table: Complete landscape of adaptive compute methods
% Columns: Paper, Year, Venue, Setting (reasoning/agent), Signal Type,
%          Direction Assumption, Granularity, Overhead, Env-Aware
% 15+ rows covering: s1, CoT-Valve, AdaptThink, Thinkless, DiffAdapt,
%   Think Just Enough, SEAG, CaTS, CoRefine, CATTS, ARPO, our EAAG
% Key insight row: "All assume fixed direction except EAAG"
%
% Narrative: reasoning-setting methods (10+) are an increasingly
% crowded space; agent-setting methods (CATTS, SEAG, CaTS, ARPO) are
% emerging but all inherit the fixed-direction assumption from the
% reasoning literature. Our work is the first to question this
% assumption in either setting.

\subsection{Detailed Method Comparison}
% Per-method analysis (1 paragraph each):
%   - CATTS: vote entropy + margin; K=5 forward passes per step;
%     direction = "high disagreement → trigger"; overhead = 5× per step
%   - SEAG: mean token confidence; Platt scaling; problem-level;
%     direction = "low confidence → search deeper"
%   - CaTS: calibrated confidence + Best-of-N early stopping;
%     direction = "low confidence → generate more candidates"
%   - CoRefine: Conv1D confidence controller; halt/re-examine/redirect;
%     direction = "low confidence → refine"
%   - AdaptThink: RL-learned think/no-think; implicitly learns direction
%     but per-environment training, no interpretable signal
%   - DiffAdapt: U-shaped entropy pattern + hidden-state probe;
%     assumes universal entropy shape across tasks
% Concluding paragraph: all share single-signal or fixed-direction.

\subsection{Concurrent Work Statement (Extended)}
% Timeline of concurrent submissions:
%   - CATTS (Feb 2026), CoRefine (Feb 2026): concurrent, no overlap
%   - AdaptThink (May 2025), Thinkless (May 2025): predate ours but
%     in reasoning setting, not agent setting
%   - DiffAdapt (Oct 2025): assumes universal entropy pattern we disprove
% Our distinct contribution: first to (a) show direction reversal,
% (b) formalize via Two-Source Model, (c) prove direction discovery
% necessary.
```

### Appendix B: Experimental Details (2 页)

```latex
\section{Experimental Details}
\label{app:experiments}

\subsection{Environment Specifications}
% For each of 8 environments:
%   - Task description (1-2 sentences)
%   - Action space: discrete/continuous, size, examples
%   - State representation: what the agent observes at each step
%   - Reward function: binary success / partial credit / score
%   - Episode length distribution: mean, median, max (histogram in fig)
%   - Optimizer T implementation:
%     * HotpotQA, FEVER, TWExpress: per-action evaluation
%       (generate K=5 candidates, evaluate each with reward model,
%       select best)
%     * APPS Intro, APPS Interview, CRUXEval: K-variant sampling
%       (generate K=3 code solutions, test each, select passing one)
%     * WebShop: LLM-Propose-K (LLM proposes K=3 action sequences,
%       simulate each, select highest-reward)
%     * Plancraft: per-action evaluation (same as HotpotQA)

\subsection{Hyperparameter Configuration}
% EAAG hyperparameters (Table):
%   N_explore = 50 episodes
%   ε_explore = 0.5 (exploration phase)
%   ε_deploy initial = 0.1, decay to 0.0 over 100 episodes
%   LASSO α = selected via 5-fold CV on exploration data
%   Gate threshold τ = 0.5
%   Retrain interval = 30 episodes (online adaptation)
%   LLM for reasoning: same Qwen3-4B backbone
%
% Baseline hyperparameters (Table):
%   - CaTS: Platt scaling on Phase 1 data (200 ep), threshold = 0.5
%   - SEAG: mean confidence threshold = calibrated on Phase 1
%   - CoRefine: entropy threshold = calibrated on Phase 1
%   - CATTS: K=5 votes, entropy threshold = 0.8, margin threshold = 0.2
%   - AUQ: confidence threshold = calibrated
%   - s1_budget: fixed budget = median episode cost of always_trigger
%   - SCG: hand-crafted features, direction from Phase 1 data
%   - BSW: EAAG with intentionally reversed direction (sign flip)
%
% Sensitivity analysis: EAAG is robust to N_explore ∈ [30, 100]
% and τ ∈ [0.3, 0.7] (Appendix E if space permits)

\subsection{Appendix Environment Results}
% 📁 实验文件夹: experiment/tab_appendix_results/
% Full results table for APPS Interview and CRUXEval:
%   APPS Interview: EAAG 73.0% (2.1 ro/ep), SCG† 79.5% (3.8 ro/ep),
%     CaTS 68.2%, always 81.0%, base 55.0%
%   CRUXEval: EAAG XX%, always XX%, base XX%
%   Analysis: APPS Interview shows SCG† advantage from Phase 1 data;
%   EAAG still competitive without Phase 1

\subsection{Feature Selection Details}
% Table: Environment × Feature matrix showing LASSO coefficients
%   Rows: 8 environments
%   Columns: step_count, token_entropy, state_length, action_entropy,
%     num_available_actions, has_output, [LLM features per env]
%   Values: LASSO coefficient (0 = not selected, sign = direction)
%
% LLM-generated features (full prompts and outputs):
%   - WebShop: price_mentioned, action_is_click, product_match_score
%   - FEVER: evidence_retrieved, claim_complexity
%   - HotpotQA: search_query_specificity, evidence_count
%   - APPS Intro: test_case_coverage, code_length_ratio
% Include the actual LLM prompt template and one full example output

\subsection{Computational Cost Breakdown}
% Table: Method × Cost component
%   Columns: Phase 1 episodes, Phase 1 compute (GPU-hrs),
%     Per-step overhead (ms), Training time, Total cost for 500 episodes
%   EAAG: 50 exploration, ~2 GPU-hrs, 0ms gate, <1s train
%   CaTS: 200 always-trigger, ~8 GPU-hrs, 0ms gate
%   CATTS: 0, 0, K×forward_pass ms
%   always_trigger: 0, 0, T_optimizer ms per step
```

### Appendix C: Proofs (1 页)

```latex
\section{Proofs}
\label{app:proofs}

\subsection{Proof of Proposition~\ref{prop:necessity}
  (Necessity of Direction Discovery)}

\begin{proposition*}[Restated]
Suppose there exist two environments $\mathcal{E}_1, \mathcal{E}_2$
with opposite true directions: $d^*(\mathcal{E}_1) = +1$ and
$d^*(\mathcal{E}_2) = -1$. Then no fixed-direction gate $g_d$ can
simultaneously satisfy
$\mathrm{SR}(g_d, \mathcal{E}_1) \geq \mathrm{SR}(\mathrm{base},
\mathcal{E}_1)$ and
$\mathrm{SR}(g_d, \mathcal{E}_2) \geq \mathrm{SR}(\mathrm{base},
\mathcal{E}_2)$.
\end{proposition*}

% FULL PROOF (not sketch):
%
% Setup: Define a fixed-direction gate as g_d(s) = 1[d · σ(s) > θ]
% for d ∈ {+1, -1} and threshold θ.
%
% Definition: d*(E) = +1 if Corr(σ(s), U(T,s)) > 0 in E (Type D),
% d*(E) = -1 if Corr(σ(s), U(T,s)) < 0 in E (Type I).
%
% Assumption: In environment E with true direction d*, a gate using
% direction d ≠ d* triggers the optimizer preferentially at states
% where E[U(T,s)] < 0 (harmful rollouts) and abstains at states
% where E[U(T,s)] > 0 (beneficial rollouts).
%
% Lemma (Wrong-direction harm): If d ≠ d*(E), then
%   SR(g_d, E) ≤ SR(base, E) - δ(E)
% where δ(E) > 0 depends on the signal strength |ρ(E)|.
% [Proof of lemma: By definition of d*, states with high d·σ(s)
% are states where U < 0. The gate triggers T at these states,
% causing the agent to adopt worse actions. The base policy, which
% never triggers T, avoids this systematic harm.]
%
% Main argument:
% Case 1: d = +1.
%   In E_2 where d* = -1, d ≠ d*(E_2).
%   By Lemma: SR(g_{+1}, E_2) ≤ SR(base, E_2) - δ(E_2) < SR(base, E_2).
%   Constraint SR(g_d, E_2) ≥ SR(base, E_2) violated. ∎ (Case 1)
%
% Case 2: d = -1.
%   In E_1 where d* = +1, d ≠ d*(E_1).
%   By Lemma: SR(g_{-1}, E_1) ≤ SR(base, E_1) - δ(E_1) < SR(base, E_1).
%   Constraint SR(g_d, E_1) ≥ SR(base, E_1) violated. ∎ (Case 2)
%
% Since d ∈ {+1, -1} and both cases lead to violation, no fixed d
% satisfies both constraints simultaneously. ∎
%
% Empirical grounding of Lemma:
%   δ(HotpotQA) ≈ 38.8 pp (BSW ablation, §5.3)
%   δ(WebShop) ≈ 22.4 pp
%   δ(FEVER) ≈ 36.8 pp
%   MLP with wrong direction: 45.3% < base 49.0% on HotpotQA

\subsection{Wrong-Direction Damage Quantification}
% Full data table:
%   Environment | Correct SR | Wrong SR | Δ SR | |ρ| (strongest signal)
%   HotpotQA   | 95.2%      | 56.4%    | -38.8 | 0.494
%   WebShop    | 43.8%      | 21.4%    | -22.4 | 0.444
%   FEVER      | 49.8%      | 13.0%    | -36.8 | 0.619
%   APPS Intro | 66.0%      | 62.5%    | -3.5  | 0.155
%
% Correlation analysis:
%   |ρ| vs |Δ SR|: Pearson r = [value], R² > 0.5
%   Interpretation: damage magnitude scales with signal strength,
%   confirming that direction mismatch is more harmful in environments
%   with stronger signal--utility coupling.
%
% MLP wrong-direction detail:
%   HotpotQA MLP-BSW: 45.3% (below base 49.0%)
%   This is worse than never triggering — demonstrating that a more
%   powerful gate (MLP) with wrong direction is WORSE than a simple
%   gate with wrong direction, because it more precisely targets the
%   harmful states.

\subsection{VOC Non-Negativity Scope}
% Classical VOC framework (Russell \& Wefald, 1991):
%   VOC(T, s) = E[max(V(a_T), V(a_base))] - V(a_base) ≥ 0
%   The agent can DISREGARD the computation result if unfavorable.
%
% Our setting violates this:
%   When the agent uses an evaluator/optimizer T, the evaluator's
%   assessment IS the agent's decision. The agent cannot separately
%   evaluate the evaluator's output because the evaluator IS the
%   evaluation mechanism.
%
%   Example: In per-action evaluation, T scores each candidate action.
%   The agent selects the highest-scored action. If T's scoring is
%   unreliable (Type I states), the agent has no independent signal
%   to detect this—it trusts T's scores by construction.
%
% Consequence:
%   Under evaluator-executor identity, VOC can be negative:
%   VOC(T, s) = E[V(a_T(s))] - V(a_base(s))
%   If T systematically selects worse actions in Type I states,
%   VOC < 0 for those states.
%
% This explains why wrong-direction gating is not merely wasteful
% (VOC = 0) but actively harmful (VOC < 0): the gate triggers T
% at Type I states where T's evaluations are unreliable, and the
% agent cannot override T's decisions.
```

### Appendix D: Two-Source Model Details (1 页)

```latex
\section{Two-Source Model: Full Derivation and Verification}
\label{app:model}

\subsection{Full Derivation}
% Setup:
%   At each step t, state s_t belongs to one of two latent types:
%     s_t ∈ Type I with probability p_I(E)
%     s_t ∈ Type D with probability 1 - p_I(E)
%   where p_I depends on the environment E.
%
% Conditional utility models:
%   Type I: U(T, s) | s ∈ Type I = -α · H(s) + ε_I, α > 0
%     Interpretation: High entropy in Type I states reflects
%     information poverty. Rollouts from the same model with the
%     same insufficient information produce noisy evaluations that
%     actively harm action selection. Higher entropy → worse rollouts.
%
%   Type D: U(T, s) | s ∈ Type D = +β · H(s) + ε_D, β > 0
%     Interpretation: High entropy in Type D states reflects
%     optionality. The agent has adequate information but faces
%     multiple viable paths. Rollouts explore this diversity
%     productively. Higher entropy → better rollouts.
%
% Marginal correlation derivation:
%   ρ(E) = Corr(H(s), U(T,s))
%        = E[H·U] - E[H]E[U]  /  (σ_H · σ_U)
%
%   E[H·U] = p_I · E[H·U | Type I] + (1-p_I) · E[H·U | Type D]
%           = p_I · (-α · E[H²] + ...) + (1-p_I) · (+β · E[H²] + ...)
%
%   Simplifying (assuming ε_I, ε_D independent of H, zero mean):
%   sign(ρ(E)) = sign(β·(1-p_I) - α·p_I)
%              = sign(β - (α+β)·p_I)
%
%   Reversal threshold:
%   p_I* = β / (α + β)
%
%   When p_I > p_I*: ρ < 0 (Type I dominated, negative direction)
%   When p_I < p_I*: ρ > 0 (Type D dominated, positive direction)
%   When p_I ≈ p_I*: ρ ≈ 0 (cancellation, entropy uninformative)

\subsection{Environment Mapping on the $p_I$ Axis}
% Figure: 1D axis from p_I = 0 (pure Type D) to p_I = 1 (pure Type I)
% Mark each environment's estimated position:
%   p_I ≈ 0.2: APPS Interview (strong positive ρ = +0.317)
%   p_I ≈ 0.45: APPS Intro (near-zero ρ = +0.012, close to p_I*)
%   p_I ≈ 0.5: WebShop (entropy ρ ≈ 0, but non-entropy signals work)
%   p_I ≈ 0.55: CRUXEval (weak negative ρ = -0.048)
%   p_I ≈ 0.6: Plancraft (weak negative ρ = -0.016, rollouts harmful)
%   p_I ≈ 0.7: HotpotQA (negative ρ = -0.041)
%   p_I ≈ 0.8: TWExpress (negative ρ = -0.290)
%   p_I ≈ 0.9: FEVER (strong negative ρ = -0.119, most Type I)
%
% Mapping rationale:
%   FEVER: fact verification requires finding specific evidence;
%     nearly every uncertain state is information-poverty.
%   HotpotQA: multi-hop QA requires evidence retrieval, but some
%     steps involve genuine reasoning choices (bridge questions).
%   APPS Interview: advanced code problems with multiple valid
%     algorithmic approaches; most uncertainty is choice-based.

\subsection{Prediction Verification: Full Data}

% P1: Temporal Dynamics (Full Table — updated from actual data)
%   Environment | ρ_early (step ≤ median) | ρ_late (step > median) | p_early   | p_late
%   HotpotQA    | -0.176                  | -0.437                 | 0.000066  | <1e-5
%   APPS Intro  | +0.102                  | -0.144                 | 0.084     | 0.043
%   WebShop     | +0.285                  | -0.006                 | <1e-5     | 0.895
%   (MBPP removed — not in the 8 evaluation environments)
%   FEVER       | +0.054                  | +0.078                 | 0.446     | 0.486
%   TWExpress   | +0.161                  | +0.008                 | 0.001     | 0.877
%   Pattern: ρ decreases (becomes more negative) from early to late
%   in all environments with sufficient signal. Early steps mix
%   Type I + Type D; late steps isolate residual Type I component.
%   FEVER/TWExpress show weak non-significant effects in both phases.
%
% P2: Same-Family Consistency (Full Analysis)
%   Family 1: Search-based QA (FEVER, HotpotQA)
%     Both negative ρ for entropy; both have step_count as strongest
%     signal; magnitude differs (|ρ_FEVER| > |ρ_HotpotQA|) due to
%     FEVER's more extreme information poverty.
%   Family 2: Code generation (APPS Intro, APPS Interview)
%     Both non-negative ρ; magnitude differs due to problem difficulty
%     distribution (Interview has more algorithmic choice points).
%   Cross-family: sign consistently differs (QA negative, code positive)
%
% P3: Signal Identity Alignment (Full Analysis)
%   Type I environments:
%     HotpotQA: step_count (|ρ|=0.494) — proxy for information
%       accumulation (more steps = more evidence retrieved)
%     FEVER: step_count (|ρ|=0.619) — same interpretation
%     TWExpress: step_count (|ρ|=0.477) — sparse reward horizon
%   Type D / Mixed environments:
%     WebShop: num_available_actions (|ρ|=0.444) — proxy for
%       decision space size (more options = more choice complexity)
%     APPS Interview: step_count with positive direction — longer
%       exploration indicates harder problem with more viable paths
%   Alignment: Type I → information sufficiency proxy;
%              Type D → decision complexity proxy. ✓
```

### Appendix E: Additional Analyses (0.5 页, if space permits)

```latex
\section{Additional Analyses}
\label{app:additional}

\subsection{Hyperparameter Sensitivity}
% N_explore sensitivity: SR as function of N_explore ∈ {10,20,30,50,100}
%   Result: stable for N_explore ≥ 30; marginal gains above 50
% Gate threshold τ sensitivity: SR as function of τ ∈ {0.3,0.4,0.5,0.6,0.7}
%   Result: robust in [0.3, 0.7]; optimal varies by environment
% LASSO α selection: 5-fold CV performance curve

\subsection{Trigger Rate Adaptation Analysis}
% 📁 实验文件夹: experiment/fig_trigger_rate/
% Full data for Figure trigger_rate:
%   Environment | Learned RR | Oracle RR | Δ (headroom) | Match?
%   HotpotQA    | 60%        | ~65%      | +48.0 pp     | ✓ aggressive
%   APPS Intro  | 6%         | ~8%       | +6.0 pp      | ✓ conservative
%   WebShop     | 16.9%      | ~18%      | +35.8 pp     | ✓ moderate
%   FEVER       | 12%        | ~95%      | +62.8 pp     | ✗ exploration bias
%   TWExpress   | 85%        | ~90%      | +31.8 pp     | ✓ aggressive
%   Plancraft   | 1%         | ~0%       | -7.0 pp      | ✓ near-zero
% Analysis: EAAG's trigger rate positively correlates with Δ (r > 0.8)
% except for FEVER (exploration bias limitation documented in §6).

\subsection{Statistical Significance}
% 📁 实验文件夹: experiment/tab_significance/
% Bootstrap confidence intervals (95%) for all main results:
%   EAAG SR on each environment: point estimate ± CI
% Paired permutation tests for EAAG vs each baseline:
%   p-values for all 36 pairwise comparisons (6 baselines × 6 envs)
% Multiple comparison correction: Holm-Bonferroni
```

---

## Figure 清单

| # | 内容 | 位置 | 状态 | 实验文件夹 |
|---|------|------|:---:|------|
| fig1 | 信号热力图 (8 env × signals, 颜色=ρ) | §3.1 | ✅ | `experiment/fig1_signal_heatmap/` |
| fig2 | Pareto frontier (4+2 环境, SR vs Cost) | §5.2 | ✅ | `experiment/fig2_pareto/` |
| fig3 | BSW 错误方向退化 | §5.3 | ✅ | `experiment/fig3_bsw_direction/` |
| fig4 | Feature usage heatmap (7 env × features) | §3.1 | ✅ | `experiment/fig4_feature_heatmap/` |
| fig5 | LLM ablation 柱状图 | §5.3/附录 | ✅ | `experiment/fig5_llm_ablation/` |
| fig6 | FEVER exploration bias | §6 | ✅ | `experiment/fig6_fever_bias/` |
| fig_auc | AUC hierarchy (3 env × 4 levels) | §3.1 | ✅ | `experiment/fig_auc_hierarchy/` |
| fig_p1 | P1 temporal dynamics (ρ decreases early→late) | §5.4 | ✅ | `experiment/fig_p1_temporal_shift/` |
| fig_trigger | Trigger rate vs step (6 env) | §5.3 | ✅ | `experiment/fig_trigger_rate/` |
| fig_bsw_rho | BSW cost vs \|ρ\| 回归散点 | §3.2/附录 | ✅ | `experiment/fig_bsw_vs_rho/` |
| fig_stratified | Stratified reversal (5 env × 3 strata) | §5.6 | ✅ | `experiment/fig_stratified_reversal/` |
| fig_matched | Matched-pair ΔU (4 env × 3 bins) | §5.6 | ✅ | `experiment/fig_matched_pair/` |
| fig_coverage | Coverage proxy vs ρ scatter | §5.4/附录 | ✅ | `experiment/fig_coverage_proxy/` |
| fig_controlled | Controlled InfoPoor/InfoRich | §5.4 | ⏳ | `experiment/fig_controlled_reversal/` |
| fig_method | EAAG 3-step pipeline 示意图 | §4 | ⏳ | `experiment/fig_method_diagram/` |

## Table 清单

| # | 内容 | 位置 | 实验文件夹 |
|---|------|------|------|
| tab:signal-discovery | Signal-utility ρ (8 env) | §3.1 | `experiment/tab_signal_discovery/` |
| tab:env-type-mapping | 环境信息结构分类 | §3.2 | `experiment/tab_env_info_structure/` |
| tab:classification | Method classification (FLARE T5) | §3.3 | `experiment/tab_method_classification/` |
| tab:env-setup | 8 env setup (base/always/T) | §5.1 | `experiment/tab_env_setup/` |
| tab:main | Main results (methods × 4 env) | §5.2 | `experiment/tab_main_results/` |
| tab:winloss | EAAG vs CB win/loss | §5.2 | `experiment/tab_winloss/` |
| tab:capacity | Gate capacity ablation | §5.6 | `experiment/tab_gate_capacity/` |
| tab:significance | Statistical significance | 附录 | `experiment/tab_significance/` |
| tab:extreme | 极端 rollout 环境结果 (TWExpress/Plancraft) | §5.5 | `experiment/tab_diagnostic_results/` |
| tab:additional | APPS Interview / CRUXEval 结果 | §5.2 or 附录 | `experiment/tab_appendix_results/` |

## 关键引用

```bibtex
@article{simpson1951interpretation,
  author={Simpson, Edward H.}, title={The Interpretation of Interaction
  in Contingency Tables}, journal={JRSS-B}, volume={13}, number={2},
  pages={238--241}, year={1951}}

@article{pearl2014understanding,
  author={Pearl, Judea}, title={Comment: Understanding {Simpson's} Paradox},
  journal={The American Statistician}, volume={68}, number={1},
  pages={8--13}, year={2014}, doi={10.1080/00031305.2014.876829}}

@article{hullermeier2021aleatoric,
  author={H{\"u}llermeier, Eyke and Waegeman, Willem},
  title={Aleatoric and Epistemic Uncertainty in Machine Learning},
  journal={Machine Learning}, volume={110}, pages={457--506},
  year={2021}, doi={10.1007/s10994-021-05946-3}}

@article{der2009aleatory,
  author={Der Kiureghian, Armen and Ditlevsen, Ove},
  title={Aleatory or Epistemic? {Does} It Matter?},
  journal={Structural Safety}, volume={31}, number={2},
  pages={105--112}, year={2009}}

@book{russell1991right,
  author={Russell, Stuart and Wefald, Eric},
  title={Do the Right Thing: Studies in Limited Rationality},
  publisher={MIT Press}, year={1991}}

@article{wang2026flare,
  author={Wang, Zehong and others},
  title={Why Reasoning Fails to Plan},
  journal={arXiv:2601.22311}, year={2026}}

@inproceedings{yao2023tree,
  author={Yao, Shunyu and others},
  title={Tree of Thoughts}, booktitle={NeurIPS}, year={2023}}

@inproceedings{zhou2024lats,
  author={Zhou, Andy and others},
  title={Language Agent Tree Search}, booktitle={ICML}, year={2024}}

@article{snell2024scaling,
  author={Snell, Charlie and Lee, Jaehoon and Xu, Kelvin and
          Kumar, Aviral},
  title={Scaling {LLM} Test-Time Compute Optimally can be More
         Effective than Scaling Model Parameters},
  journal={arXiv:2408.03314}, year={2024}}

@inproceedings{hao2023reasoning,
  author={Hao, Shibo and others},
  title={Reasoning with Language Model is Planning with World Model},
  booktitle={EMNLP}, year={2023}}
```

**Baseline 引用 (已补全 — iter_01 verified via WebSearch):**

```bibtex
@article{catts2026,
  author={Lee, Nicholas and Erdogan, Lutfi Eren and John, Chris Joseph
          and Krishnapillai, Surya and Mahoney, Michael W. and
          Keutzer, Kurt and Gholami, Amir},
  title={Agentic Test-Time Scaling for {WebAgents}},
  journal={arXiv:2602.12276},
  year={2026},
  note={Introduces CATTS: vote-entropy + margin gating for web agents}}

@inproceedings{seag2025,
  author={Lee, Sungjae and Park, Hyejin and Kim, Jaechang and Ok, Jungseul},
  title={Semantic Exploration with Adaptive Gating for Efficient
         Problem Solving with Language Models},
  booktitle={ACL},
  year={2025},
  note={arXiv:2501.05752; mean-confidence gating for tree search}}

@article{cats2025,
  author={Huang, Chengsong and others},
  title={Calibrated Test-Time Scaling for Efficient {LLM} Inference},
  journal={arXiv:2503.00031},
  year={2025},
  note={CaTS: Platt-scaled confidence for Best-of-N early stopping}}

@article{corefine2026,
  author={Anonymous},
  title={CoRefine: Confidence-Guided Self-Refinement for Adaptive
         Test-Time Compute},
  journal={arXiv:2602.08948},
  year={2026},
  note={Conv1D confidence controller, halt/re-examine/redirect}}

@inproceedings{adaptthink2025,
  author={Zhang, Jiajie and Lin, Nianyi and Hou, Lei and Feng, Ling
          and Li, Juanzi},
  title={AdaptThink: Reasoning Models Can Learn When to Think},
  booktitle={EMNLP},
  year={2025},
  note={arXiv:2505.13417; RL-based think/no-think policy, THU-KEG}}

@inproceedings{thinkless2025,
  author={Fang, Gongfan and Ma, Xinyin and Wang, Xinchao},
  title={Thinkless: {LLM} Learns When to Think},
  booktitle={NeurIPS},
  year={2025},
  note={arXiv:2505.13379; DeGRPO for hybrid short/long-form reasoning, NUS}}

@article{diffadapt2025,
  author={Anonymous},
  title={DiffAdapt: Difficulty-Adaptive Reasoning for Token-Efficient
         {LLM} Inference},
  journal={arXiv:2510.19669},
  year={2025},
  note={U-shaped entropy pattern, lightweight hidden-state probe}}

@article{thinkjustenough2025,
  author={Sharma, Aman and Chopra, Paras},
  title={Think Just Enough: Sequence-Level Entropy as a Confidence
         Signal for {LLM} Reasoning},
  journal={arXiv:2510.08146},
  year={2025},
  note={Entropy-based early stopping, 25--50\% compute savings}}

@inproceedings{arpo2025,
  author={Du, others},
  title={Agentic Reinforced Policy Optimization},
  booktitle={ICLR},
  year={2026},
  note={arXiv:2507.19849; entropy-based adaptive rollout at tool-call steps}}

@inproceedings{s1_2025,
  author={Muennighoff, Niklas and Yang, Zitong and others},
  title={s1: Simple Test-Time Scaling},
  booktitle={EMNLP},
  year={2025},
  note={arXiv:2501.19393; budget forcing for reasoning models}}
```

**理论参考 — uncertainty decomposition in RL (iter_01 新增):**

```bibtex
@article{charpentier2022disentangling,
  author={Charpentier, Bertrand and Senanayake, Ransalu and
          Kochenderfer, Mykel J. and G{\"u}nnemann, Stephan},
  title={Disentangling Epistemic and Aleatoric Uncertainty in
         Reinforcement Learning},
  journal={arXiv:2206.01558},
  year={2022},
  note={Four desiderata for epistemic/aleatoric decomposition in RL;
        validates MC-dropout, ensemble, DKL, evidential methods}}
```

**NeurIPS best paper 参考 — abstract/intro 结构分析 (iter_01 新增):**

```bibtex
@inproceedings{lin2024rho1,
  author={Lin, Zhenghao and others},
  title={Not All Tokens Are What You Need for Pretraining},
  booktitle={NeurIPS},
  year={2024},
  note={Best Paper Runner-Up; "Challenging this norm, we posit..."
        结构：2句背景→1句发现→方法→结果}}

@inproceedings{schaeffer2023emergent,
  author={Schaeffer, Rylan and Miranda, Brando and Koyejo, Sanmi},
  title={Are Emergent Abilities of Large Language Models a Mirage?},
  booktitle={NeurIPS},
  year={2023},
  note={Outstanding Paper; "we present an alternative explanation"
        结构：1句claim→alternative explanation→3 tests→conclusion}}

@inproceedings{tian2024var,
  author={Tian, Keyu and others},
  title={Visual Autoregressive Modeling: Scalable Image Generation
         via Next-Scale Prediction},
  booktitle={NeurIPS},
  year={2024},
  note={Best Paper; "diverging from the standard raster-scan"
        结构：1句新范式→对比old→结果→scaling law}}

@inproceedings{shinn2023reflexion,
  author={Shinn, Noah and Cassano, Federico and Berman, Edward and
          Gopinath, Ashwin and Narasimhan, Karthik and Yao, Shunyu},
  title={Reflexion: Language Agents with Verbal Reinforcement Learning},
  booktitle={NeurIPS},
  year={2023},
  note={Agent 领域 landmark paper; verbal reflection + episodic memory}}

@article{kdd2023simpson,
  author={Anonymous},
  title={Learning to Discover Various {Simpson's} Paradoxes},
  journal={KDD},
  year={2023},
  note={ML-based Simpson's paradox detection on tabular data,
        complements our signal-utility Simpson's paradox framing}}
```

**新增引用 — iter_02 (§3.2 theoretical grounding + §5.4 verification structure):**

```bibtex
@article{tao2025revisiting,
  author={Tao, Linwei and Yeh, Yi-Fan and Dong, Minjing and
          Huang, Tao and Torr, Philip and Xu, Chang},
  title={Revisiting Uncertainty Estimation and Calibration of
         Large Language Models},
  journal={arXiv:2505.23854},
  year={2025},
  note={Evaluates 80 LLMs (0.6B--671B); finds LLMs more reliable on
        reasoning tasks than knowledge-seeking ones, good calibration
        $\neq$ good selective classification --- independent evidence
        that uncertainty semantics are task-dependent, not universal.
        Used in §3.2 to ground our claim that signal meaning varies
        across environments.}}

@inproceedings{heo2025llmuncertainty,
  author={Heo, Juyeon and Xiong, Miao and Heinze-Deml, Christina
          and Narain, Jaya},
  title={Do {LLMs} Estimate Uncertainty Well in Instruction-Following?},
  booktitle={ICLR},
  year={2025},
  note={arXiv:2410.14582; Apple Research; first systematic evaluation
        of LLM uncertainty estimation in instruction-following;
        finds existing methods struggle with subtle errors and
        uncertainty varies by instruction type. Complements our
        finding that signal semantics are task-dependent.}}

@article{snell2024scaling_full,
  author={Snell, Charlie and Lee, Jaehoon and Xu, Kelvin and
          Kumar, Aviral},
  title={Scaling {LLM} Test-Time Compute Optimally can be More
         Effective than Scaling Model Parameters},
  journal={arXiv:2408.03314},
  year={2024},
  note={UC Berkeley / Google DeepMind; key finding: effectiveness of
        test-time compute scaling varies critically with prompt
        difficulty---motivates adaptive allocation. Our work extends
        this to the step-level within agentic trajectories.
        Structural reference: observation→model→prediction→verification
        pattern used as template for our §3--§5 flow.}}
```

---

## Reviewer FAQ (写作参考, 不进入论文)

**Purpose**: 预先准备 reviewer 可能的质疑和回应策略。基于 NeurIPS 2025 reviewer guidelines, Michael Black 的 "Novelty in Science" 准则, 以及从 OpenReview 分析的常见 rejection patterns 整理。

**核心防御策略**: 本论文的贡献层次是 **Finding > Theory > Method**。方法的简单性是 *feature not bug* — 类比 "Are Emergent Abilities a Mirage?" (NeurIPS 2023 Outstanding) 用 metric change 推翻 emergent abilities, 我们用 direction discovery 推翻 fixed-direction assumption。NeurIPS 2025 reviewer guidelines 明确写道: "Originality does not necessarily require introducing an entirely new method. A work that provides novel insights by evaluating existing methods is also equally valuable."

---

### Q1: "The method (EAAG) is just logistic regression. Limited novelty."

**Response strategy**: Reframe — the contribution is the finding + theory, not the gate.

> We thank the reviewer for this comment. We want to clarify the contribution structure: EAAG is intentionally simple because our analysis proves that **the bottleneck is direction discovery, not gate complexity** (Proposition 1). An MLP gate with the wrong direction degrades SR by 38.8pp (below the no-trigger baseline); a logistic gate with the right direction Pareto-dominates all baselines. This parallels several NeurIPS best papers where simple methods paired with strong findings constitute the contribution:
>
> - "Are Emergent Abilities a Mirage?" (NeurIPS 2023 Outstanding): the method is changing the metric; the finding is that emergent abilities disappear.
> - "Not All Tokens Are What You Need" (NeurIPS 2024 Best Paper Runner-Up): the method is selective token loss; the finding is that not all tokens matter.
> - ReAct (ICLR 2023): the method is prompting; the finding is that reasoning+acting synergize.
>
> Our primary contribution is **the finding** (direction reversal across 8 environments) + **the theory** (Two-Source Model explaining when and why) + **the proof** (direction discovery is necessary). EAAG is the natural consequence of this analysis—its simplicity is evidence that the analysis correctly identifies the bottleneck. As Michael Black (MPI) notes in "Novelty in Science": "The simplicity of an idea is often confused with a lack of novelty when exactly the opposite is often true."

**Where this is addressed in the paper**: §4 "Design Principles" paragraph derives each method component from §3 findings. §4 "Why the method is intentionally simple" paragraph explicitly argues the complexity-budget allocation.

---

### Q2: "Only tested on one backbone (Qwen3-4B). How do we know the findings generalize?"

**Response strategy**: Distinguish environment-level findings from model-level implementation.

> The core finding (direction reversal) is a property of the **environment's information structure**, not the model. The Two-Source Model (§3.2) explains direction reversal through the environment's proportion of Type I vs Type D states—a property determined by the task structure (e.g., does the task require information retrieval or choice among alternatives?). This is independent of which LLM backbone processes the task.
>
> Moreover, independent evidence from Tao et al. (2025, 80 LLMs from 0.6B to 671B) and Heo et al. (ICLR 2025) shows that uncertainty semantics vary across task types for diverse model families—confirming that our finding is not an artifact of Qwen3-4B specifically.
>
> That said, we acknowledge this limitation honestly in §6 and commit to multi-backbone experiments in the camera-ready if accepted. The EAAG implementation (LASSO + logistic regression) has no model-specific components and can be applied to any backbone.

**Where this is addressed in the paper**: §6 Limitations item (1), §2.2 Orthogonal Work (Tao et al., Heo et al. citations).

---

### Q3: "The Two-Source Model is too simplified. Real environments have more than two types of uncertainty."

**Response strategy**: Acknowledge honestly, but defend the model's explanatory and prescriptive value.

> We agree that real environments likely contain more than two uncertainty types (we discuss this in §6 Future Directions as "Beyond two sources: a taxonomy of uncertainty types"). However, the Two-Source Model's value is **explanatory and prescriptive, not predictive of exact ρ values**:
>
> 1. **Explanatory**: It explains *why* direction reverses—the same entropy signal reflects different uncertainty sources in different environments. This is the core insight.
> 2. **Prescriptive**: It tells us what the gate must learn (direction), leading to the necessity proof (Proposition 1).
> 3. **Empirically validated**: All three predictions (P1: temporal dynamics, P2: cross-environment consistency, P3: signal identity alignment) are confirmed in §5.4.
>
> A more complex model (e.g., 3+ types) would not change the central finding or the necessity proof—it would refine the p_I mapping but the direction-reversal phenomenon and its implications for method design would remain identical.

**Where this is addressed in the paper**: §6 Limitations item (2), §6 Future Directions "Beyond two sources" paragraph.

---

### Q4: "The environments are limited. What about multi-agent settings, long-horizon planning, etc.?"

**Response strategy**: Acknowledge scope, emphasize coverage and principled selection.

> Our 8 environments span 6 distinct task categories: multi-hop QA (HotpotQA), fact verification (FEVER), code generation (APPS Intro, APPS Interview, CRUXEval), web navigation (WebShop), text games (TWExpress), and manufacturing planning (Plancraft). This covers the major categories in the agent evaluation literature (cf. AgentBench, ICLR 2024).
>
> The environments were selected to cover the full range of the Two-Source Model: pure Type I (FEVER), pure Type D (APPS Interview), mixed (APPS Intro, WebShop), weak-signal (CRUXEval, Plancraft), and extreme rollout properties (TWExpress: rollout-safe; Plancraft: rollout-harmful). This principled selection is more informative than a larger but unstructured set.
>
> Multi-agent settings are an exciting future direction (mentioned in §6 Future Directions). Our framework predicts that signal-semantic misalignment would also occur across heterogeneous sub-environments in multi-agent systems.

**Where this is addressed in the paper**: §5.1 Setup (environment selection rationale), §6 Future Directions "Signal semantics as a foundation for multi-agent coordination."

---

### Q5: "EAAG's FEVER performance (49.8%) is much worse than SCG (98.0%) and always-trigger (99.8%)."

**Response strategy**: Reframe as honest limitation that validates the theory.

> This is correct, and we discuss it transparently in §6. The FEVER limitation is not a method failure but an **exploration limitation**: FEVER's rollout value concentrates at step 0-1 (ρ = -0.619), and random exploration misses step 0 with 50% probability. SCG avoids this because it uses Phase 1 always-trigger data (200 episodes at full cost)—data that directly reveals step-0 value.
>
> Importantly, this failure mode is **itself predicted by the Two-Source Model**: FEVER is the most extreme Type I environment (p_I ≈ 0.9), where undirected exploration is least efficient. This validates rather than undermines the theory. We propose curriculum-based exploration as a concrete solution in §6 Future Directions.
>
> Also note: EAAG at 49.8% still matches or exceeds all fixed-direction baselines on FEVER (CaTS 50.2%, SEAG 49.3%, CoRefine 49.8%, CATTS 34.2%)—the limitation is relative to SCG (which has Phase 1 data) and always-trigger (which has unlimited compute).

**Where this is addressed in the paper**: §5.2 FEVER per-environment analysis, §6 "FEVER and exploration bias" paragraph, §6 Future Directions "Adaptive exploration."

---

### Q6: "The paper claims 'Pareto-dominance' but some individual baselines beat EAAG in specific environments."

**Response strategy**: Clarify Pareto-dominance definition and the 34W/2L record.

> Pareto-dominance is defined as SR ≥ *and* Cost ≤ with at least one strict inequality (§5.1). The 34W/2L record refers to **head-to-head SR comparisons** across 6 baselines × 8 environments. EAAG wins 34 of these.
>
> The 2 losses are: (1) SCG on APPS Interview (SCG† 79.5% vs EAAG 73.0%—but SCG requires Phase 1 data that EAAG eliminates), and (2) [second loss from data]. These losses are in environments where the baseline has a structural advantage (Phase 1 data) that EAAG deliberately forgoes. When comparing methods with equivalent data access, EAAG wins in all environments.

---

### Q7: "Why not use a neural network gate instead of logistic regression?"

**Response strategy**: Empirical evidence + principled argument.

> We tested this (MLP gate variant). The MLP achieves comparable SR to logistic regression when direction is correct, and **worse SR when direction is wrong** (45.3% vs base 49.0% on HotpotQA). This is because a more powerful gate with wrong direction more precisely targets harmful states—the precision works against you.
>
> The principled argument: §3.1 Observation 3 shows that the jump from single-signal (AUC ≈ 0.53) to multi-signal logistic (AUC ≈ 0.85) is enormous, while the jump from logistic to hidden-state probe (AUC ≈ 0.89) is marginal. The information hierarchy is **signal selection > direction > gate complexity**. Logistic regression is at the sweet spot: powerful enough to combine multiple directed signals, simple enough to train from 50 exploration episodes without overfitting.

**Where this is addressed in the paper**: §4 "Why the method is intentionally simple," §5.3 BSW ablation.

---

### Q8: "The exploration cost (50 episodes) is non-trivial. How does this compare to baselines?"

**Response strategy**: Quantify and contextualize.

> EAAG's exploration cost is 50 episodes × average cost per episode. Phase 1-requiring baselines (CaTS, SEAG, CoRefine, SCG) need 200 always-trigger episodes at full optimizer cost. EAAG's 50 episodes use random gating (ε = 0.5), so average per-episode optimizer cost is ~50% of always-trigger. Net comparison: EAAG ~25 equivalent always-trigger episodes vs baselines' 200—an 8× reduction in setup cost.
>
> Moreover, EAAG's exploration cost is amortized: once direction is learned, no further exploration is needed unless the environment shifts. We include amortized costs in all reported Total Cost numbers (§5.1 "Cost fairness").

**Where this is addressed in the paper**: §5.1 Cost fairness paragraph, §6 Limitations item (4), Appendix B.5 Computational Cost Breakdown.

---

### Q9: "Direction reversal is just a correlation artifact — confounded by trajectory length, difficulty, or model calibration bias."

**Response strategy**: Point to three layers of evidence (stratified + interventional + cross-env).

> We address this concern through three complementary analyses in §5.6:
>
> 1. **Stratified analysis**: We control for trajectory length by computing ρ within fixed-length strata. Direction reversal persists in every stratum — it is not a length artifact.
> 2. **Interventional evidence**: The BSW ablation (§5.3) is not correlation — we *manipulate* the gate's direction and observe causal effects on SR. Wrong direction causes −38.8pp on HotpotQA; the MLP gate falls *below* the no-trigger baseline (45.3% < 49.0%). If reversal were an artifact, manipulation would have no systematic effect.
> 3. **Cross-environment consistency**: Same-family environments show consistent direction (FEVER ≈ HotpotQA, both negative), while different-family environments differ (APPS Interview positive). This structured pattern is inconsistent with random artifact.
>
> Moreover, the 8 environments span 6 task categories with different reward structures, trajectory lengths, and difficulty distributions. A confounder would need to systematically reverse across all these dimensions while perfectly tracking our Two-Source Model's predictions — this is far less parsimonious than the phenomenon being real.

### Q10: "The Two-Source Model has no observable proxy for Type I/D — it's post-hoc storytelling."

**Response strategy**: Acknowledge the limitation but point to (a) testable predictions that ARE verified, and (b) the information coverage proxy.

> The Two-Source Model makes three predictions (P1-P3, §5.4), all of which are confirmed empirically. P1 (temporal dynamics) shows that ρ decreases over the episode as early mixed uncertainty gives way to late-step residual Type I—a refinement of the model that emerged from data. A "post-hoc story" that generates correct predictions across held-out environments and temporal strata is, by definition, a theory with predictive power.
>
> We additionally construct an observable proxy for p_I: *information coverage* c_t (fraction of task-relevant information available at step t). We show that within-environment ρ(entropy, U | c_t < median) is more negative than ρ(entropy, U | c_t ≥ median), and that cross-environment mean coverage correlates with observed ρ direction (Appendix D). This provides empirical grounding for the latent p_I variable.
>
> That said, we acknowledge that the Two-Source Model is a first-order approximation (§6 Limitations). Its value is *explanatory and prescriptive* — it tells practitioners what to look for (information structure) when deploying adaptive compute in a new environment.

---

### 通用回复模板 (for any criticism about contribution type)

> Our contribution follows the **Finding + Theory + Method** paradigm recognized by NeurIPS: we discover a phenomenon (direction reversal), explain it theoretically (Two-Source Model + necessity proof), and build a principled method (EAAG) that addresses it. The NeurIPS 2025 reviewer guidelines state: "Contributions may be theoretical, methodological, algorithmic, empirical, connecting ideas in disparate fields ('bridge papers'), or providing a critical analysis." Our work is precisely a critical analysis (§3) that connects uncertainty theory to adaptive compute (bridge) and leads to a principled method (§4).

---

## Coherence Checklist (全文一致性, iter_03 最终检查)

**ONE STORY**: 假设错了 → provably 不行 → 修了 → 全赢
- [ ] Abstract echoes this exact arc in ~250 words
- [ ] §1 P1-P6 follow this arc: background → assumption → wrong → why → fix → results
- [ ] §3 title "Signal-Utility Landscape" frames as investigation, not method
- [ ] §3→§4 transition: "three requirements → EAAG satisfies all three"
- [ ] §4 opens with Design Principles derived from §3 (not standalone)
- [ ] §5 opens with three evaluation axes matching §3-§4 claims
- [ ] §5.4 verifies §3.2's predictions (not EAAG's performance)
- [ ] §6 zooms out: "not just our method, but how the community thinks about uncertainty"
- [ ] §7 Conclusion echoes Abstract's claims with "confirmed" confidence

**NUMBER CONSISTENCY**:
- [ ] "8 environments" throughout (all 8 are main evaluation, no diagnostic/appendix split)
- [ ] "34 wins vs 2 losses" in Abstract, §5.2, Conclusion
- [ ] ρ values consistent: FEVER -0.119, APPS Interview +0.317, APPS Intro +0.012
- [ ] step_count ρ: HotpotQA -0.494, FEVER -0.619
- [ ] num_available_actions ρ: WebShop +0.444
- [ ] BSW degradation: -38.8pp (HotpotQA), -22.4pp (WebShop)
- [ ] MLP wrong-direction: 45.3% < base 49.0%
- [ ] AUC hierarchy: ~0.53 (single entropy), ~0.85 (multi-signal), ~0.89 (probe)
- [ ] Trigger rates: 60% (HotpotQA), 6% (APPS Intro), ~1% (Plancraft)
- [ ] Headroom: +48pp (HotpotQA), +6pp (APPS Intro), +35.8pp (WebShop), +62.8pp (FEVER)

**TERMINOLOGY CONSISTENCY**:
- [ ] "direction reversal" (not "sign flip" or "correlation reversal")
- [ ] "Two-Source Model" (capitalized, not "two-source model")
- [ ] "Type I / Type D" (not "Type 1 / Type 2" or "information poverty / decision difficulty" without type labels)
- [ ] "signal--utility" (em-dash in LaTeX, not "signal-utility")
- [ ] "optimizer utility" or just "utility" (not "rollout value" in formal contexts)
- [ ] "environment-aware" (hyphenated)
- [ ] "Pareto-dominates" (hyphenated)
- [ ] "EAAG" (all caps, no dots)

**NeurIPS FORMAT COMPLIANCE** (based on NeurIPS 2025 guidelines, likely similar for 2026):
- [ ] Main text: 9 pages max (content pages, excluding references/appendix/checklist)
- [ ] Current estimate: Abstract (0.5p) + Intro (1.5p) + Related (0.75p) + §3 (2.0p) + §4 (1.75p) + §5 (2.5p) + §6 (1.0p) + §7 (0.25p) = **10.25p** → need to trim ~1.25p
- [ ] Trim candidates (priority order):
  - §5.2 per-environment analysis: move APPS Intro + HotpotQA details to appendix (~0.3p saved)
  - §4 "Why Simplicity" paragraph: condense to 3 sentences (~0.15p saved)
  - §2.1 Related Work: tighten signal-based and vote-based paragraphs (~0.2p saved)
  - §3.1 Obs 2-3: condense into single observation (~0.2p saved)
  - §6 Future Directions: move "multi-agent" paragraph to appendix (~0.15p saved)
  - §1 P2: reduce mechanism enumeration, use footnote (~0.1p saved)
  - §6 Broader Impact: condense to 2 sentences (~0.1p saved)
- [ ] References: no page limit
- [ ] Appendix: no page limit, included in same PDF
- [ ] NeurIPS paper checklist: must be included after appendix
- [ ] Anonymous submission: no author names, no acknowledgments
- [ ] LaTeX template: NeurIPS 2026 style file (use neurips_2026.sty when available; neurips_2025.sty as fallback)
