# Figure Drawing Prompts

## Figure 1: Intro Teaser Figure — "Same Signal, Opposite Meaning"

### 设计概要
一个三部分的 teaser figure，展示论文核心发现。参考 CATTS Figure 1 的干净方框风格。

### 画图 Prompt (TikZ / Python matplotlib)

**整体布局：** 横向三栏，宽度比例约 3.5 : 4 : 2.5，总宽度 = \textwidth。

---

#### (a) 左栏：概念图 — 两种 uncertainty 类型

**Prompt for TikZ:**

```
Draw a conceptual diagram showing two types of uncertainty leading to
opposite outcomes when test-time compute is applied.

TOP HALF — "Type I: Information Poverty (e.g., FEVER)"
- Show a small agent icon on the left
- Arrow pointing right labeled "High Entropy"
- A red X labeled "Rollout" with annotation "Agent lacks info → rollout
  from same model cannot help"
- Result: red downward arrow labeled "SR ↓"
- Background: light red/pink shading

BOTTOM HALF — "Type D: Decision Difficulty (e.g., APPS Interview)"
- Same agent icon
- Arrow pointing right labeled "High Entropy"
- A green checkmark labeled "Rollout" with annotation "Multiple viable
  paths → rollout explores alternatives"
- Result: green upward arrow labeled "SR ↑"
- Background: light green shading

BETWEEN THE TWO:
- A prominent double-headed vertical arrow labeled
  "Same Signal, Opposite Meaning"
- Use a wavy or zigzag style to emphasize the reversal

STYLE:
- Rounded rectangles for boxes
- Clean sans-serif font (Helvetica or similar)
- Color scheme: red family for Type I, green/teal family for Type D
- Minimal text, icon-driven
- Similar visual weight to CATTS Figure 1 left panel
```

---

#### (b) 中栏：真实数据 — 方向反转的 empirical evidence

**Prompt for matplotlib:**

```python
"""
Figure 1(b): Two scatter plots showing opposite entropy-utility direction.

Layout: 2 rows × 1 column, sharing x-axis label "Token Entropy"

TOP PANEL: FEVER (Type I, ρ = -0.62)
- Scatter plot: x = token_entropy, y = utility U (binary 0/1, jittered)
  or y = rollout_gain (continuous)
- Overlay: regression line with NEGATIVE slope (blue, thick)
- Shading: light blue confidence band
- Annotation: "ρ = -0.62" in corner, "High entropy → HARM" with red arrow
- Color: blue dots

BOTTOM PANEL: APPS Interview (Type D, ρ = +0.32)
- Same axes as above
- Overlay: regression line with POSITIVE slope (red/orange, thick)
- Annotation: "ρ = +0.32" in corner, "High entropy → HELP" with green arrow
- Color: red/orange dots

ALTERNATIVE (if scatter too noisy):
Use the matched-pair bar chart style from fig_matched_pair_opposite_meaning.png
but only show 2 environments (FEVER + APPS Intv), 3 difficulty bins each.
Blue bars = ΔU < 0 (Type I), Red bars = ΔU > 0 (Type D).

DATA SOURCE:
- From exploration data D: per-step (entropy, U) pairs
- Files: fig_matched_pair/ or fig1_signal_heatmap/ CSV files
- Alternatively: use signal_discovery correlation values directly

STYLE:
- Matplotlib with seaborn styling
- Font size: 10pt axis labels, 12pt titles
- Tight layout, no wasted whitespace
- Match color scheme with panel (a): blue = Type I, red = Type D
"""
```

---

#### (c) 右栏：EAAG 的效果 mini-summary

**Prompt for matplotlib:**

```python
"""
Figure 1(c): Compact win/loss summary showing EAAG vs baselines.

OPTION A — Stacked horizontal bar (preferred):
- One bar per baseline (CaTS, SEAG, CoRefine, CATTS, AUQ, s1)
- Each bar split into: green (EAAG wins), gray (tie), red (EAAG loses)
- x-axis: number of environments (0-8)
- Sorted by total wins descending
- Annotation: "EAAG wins X/8" title

OPTION B — Compact radar/spider chart:
- 8 axes = 8 environments
- EAAG line (red, filled) vs best baseline (gray, dashed)
- Show EAAG encompassing baselines

DATA SOURCE:
- From tab_winloss/ CSV files
- Count wins/ties/losses across 8 environments for each baseline

STYLE:
- Very compact (fit in ~2.5cm width)
- Large clear numbers
- Green/gray/red color coding
"""
```

---

### 组合方式

```latex
\begin{figure*}[t]
\centering
% (a) Conceptual diagram — TikZ or imported PDF
\begin{subfigure}[t]{0.35\textwidth}
  \centering
  \includegraphics[width=\textwidth]{figures/fig1a_concept.pdf}
  \caption{Two uncertainty types lead to opposite outcomes under
  the same high-entropy signal.}
\end{subfigure}
\hfill
% (b) Empirical evidence — matplotlib
\begin{subfigure}[t]{0.38\textwidth}
  \centering
  \includegraphics[width=\textwidth]{figures/fig1b_reversal_data.pdf}
  \caption{Real data: entropy--utility direction reverses
  between FEVER ($\rho{=}{-}0.62$) and APPS Intv ($\rho{=}{+}0.32$).}
\end{subfigure}
\hfill
% (c) EAAG summary — matplotlib
\begin{subfigure}[t]{0.24\textwidth}
  \centering
  \includegraphics[width=\textwidth]{figures/fig1c_winloss.pdf}
  \caption{EAAG Pareto-dominates all fixed-direction baselines.}
\end{subfigure}
\caption{\textbf{Same Signal, Opposite Meaning.}
(a)~High entropy reflects information poverty (Type~I) or decision
difficulty (Type~D); the same signal predicts opposite value of
computation.
(b)~This reversal is empirically confirmed: entropy--utility
correlation flips sign across environments.
(c)~EAAG, which learns direction per environment, dominates all
fixed-direction baselines across 8 environments.}
\label{fig:teaser}
\end{figure*}
```

---

## Figure 4: EAAG Method Pipeline Diagram

### 设计概要
展示 EAAG 的三阶段 pipeline 及其与 Section 3 requirements 的映射关系。
参考 CATTS Figure 1 的干净方框风格 + CoRefine Figure 3 的 pipeline 对比。

### 画图 Prompt (TikZ)

```
Draw a method pipeline diagram for EAAG with the following structure:

=== TOP ROW: Requirements from Section 3 ===
Three small rounded boxes in a row, with light gray background:
- Box 1: "Req (iii)" subtitle: "Signal-agnostic collection"
  Icon: dice or question mark
- Box 2: "Req (ii)" subtitle: "Multi-signal features"
  Icon: grid or multiple arrows
- Box 3: "Req (i)" subtitle: "Direction must be learned"
  Icon: bidirectional arrow (↕)

Each box has a downward arrow (dashed, gray) pointing to the
corresponding pipeline stage below.

=== MIDDLE ROW: Three-stage pipeline ===
Three large rounded boxes connected by thick arrows (→):

BOX 1 — EXPLORE (Blue: #4472C4)
  Header: "EXPLORE" (bold, white text on blue banner)
  Body (white background):
  - "ε-random gating"
  - "ε = 0.5, N = 50 episodes"
  - "Output: D = {(φ(s), U)}"
  Small icon: shuffle/random symbol

  → (thick arrow)

BOX 2 — REASON (Orange: #ED7D31, dashed border to show optional)
  Header: "REASON (optional)" (bold)
  Body:
  - "LLM analyzes D"
  - "Proposes task-specific features"
  - "Output: φ_cand = φ_univ ∪ φ_LLM"
  Small icon: lightbulb or brain

  → (thick arrow)

BOX 3 — LEARN (Green: #70AD47)
  Header: "LEARN" (bold, white text on green banner)
  Body:
  - "LASSO logistic regression"
  - "Signed weights → direction"
  - "Output: gate g(s)"
  Small icon: target/crosshair

  → (thick arrow, to the right)

BOX 4 — DEPLOY (Gray: #A5A5A5, smaller box)
  "Deploy"
  "Zero per-step overhead"
  Small icon: rocket

=== BOTTOM ROW: Signed weight examples ===
Below BOX 3 (LEARN), add two small annotation boxes:

LEFT example box (light blue border):
  "HotpotQA (Type I)"
  "w_entropy = -0.34"
  "High entropy → DON'T trigger"
  Small arrow: ↓ (blue, pointing down)

RIGHT example box (light red border):
  "APPS Intv (Type D)"
  "w_entropy = +0.32"
  "High entropy → trigger"
  Small arrow: ↑ (red, pointing up)

Between them: "Same feature, learned opposite direction"

=== OVERALL STYLE ===
- Width: full \textwidth (two-column figure)
- Clean, modern corporate style (think McKinsey/BCG diagram)
- Rounded corners on all boxes (radius ~5pt)
- Drop shadow on main pipeline boxes (subtle)
- Font: sans-serif, 8-9pt body, 10pt headers
- White background, plenty of whitespace
- Color palette: Blue → Orange → Green → Gray (left to right)
- Arrows: thick (1.5pt), with arrowhead
- Dashed elements: requirement arrows, REASON box border
```

### TikZ 代码框架

```latex
\begin{figure*}[t]
\centering
\resizebox{\textwidth}{!}{%
\begin{tikzpicture}[
  reqbox/.style={draw=gray!50, fill=gray!5, rounded corners=3pt,
    minimum width=2.8cm, minimum height=1.2cm, align=center,
    font=\small},
  pipebox/.style={draw=#1!70, fill=#1!5, rounded corners=5pt,
    minimum width=3.5cm, minimum height=2.8cm, align=center,
    font=\small, line width=1pt},
  header/.style={fill=#1!80, text=white, font=\small\bfseries,
    minimum width=3.5cm, rounded corners=3pt, inner sep=3pt},
  exbox/.style={draw=#1!50, fill=#1!5, rounded corners=3pt,
    minimum width=2.8cm, align=center, font=\scriptsize},
  arrow/.style={->, >=stealth, line width=1.5pt, #1},
  dasharrow/.style={->, >=stealth, dashed, gray, line width=0.8pt},
]

% === Requirements (top row) ===
\node[reqbox] (req3) at (0, 4) {Req (iii)\\[-2pt]
  \scriptsize Signal-agnostic\\[-2pt]\scriptsize collection};
\node[reqbox] (req2) at (4.5, 4) {Req (ii)\\[-2pt]
  \scriptsize Multi-signal\\[-2pt]\scriptsize features};
\node[reqbox] (req1) at (9, 4) {Req (i)\\[-2pt]
  \scriptsize Direction must\\[-2pt]\scriptsize be learned};

% === Pipeline boxes (middle row) ===
% EXPLORE
\node[pipebox=blue] (explore) at (0, 1.5) {};
\node[header=blue] at (0, 2.6) {EXPLORE};
\node[align=center, font=\scriptsize] at (0, 1.3) {
  $\varepsilon$-random gating\\
  $\varepsilon{=}0.5$, $N{=}50$ eps\\[2pt]
  $\mathcal{D} = \{(\phi(s), U)\}$};

% REASON
\node[pipebox=orange, dashed] (reason) at (4.5, 1.5) {};
\node[header=orange] at (4.5, 2.6) {REASON \scriptsize(optional)};
\node[align=center, font=\scriptsize] at (4.5, 1.3) {
  LLM analyzes $\mathcal{D}$\\
  Proposes features\\[2pt]
  $\phi_{\text{cand}} = \phi_{\text{univ}} \cup \phi_{\text{LLM}}$};

% LEARN
\node[pipebox=green!60!black] (learn) at (9, 1.5) {};
\node[header=green!60!black] at (9, 2.6) {LEARN};
\node[align=center, font=\scriptsize] at (9, 1.3) {
  LASSO logistic reg.\\
  Signed weights $\to$ direction\\[2pt]
  Gate $g(s) = \mathbf{1}[\sigma(\mathbf{w}^\top\phi) > \tau]$};

% DEPLOY
\node[pipebox=gray, minimum width=2.2cm, minimum height=1.8cm]
  (deploy) at (12.5, 1.5) {};
\node[header=gray] at (12.5, 2.2) {DEPLOY};
\node[align=center, font=\scriptsize] at (12.5, 1.3) {
  Zero overhead\\per step};

% === Arrows ===
\draw[arrow=blue!70] (explore) -- (reason);
\draw[arrow=orange!70] (reason) -- (learn);
\draw[arrow=green!60!black] (learn) -- (deploy);
\draw[dasharrow] (req3) -- (explore);
\draw[dasharrow] (req2) -- (reason);
\draw[dasharrow] (req1) -- (learn);

% === Signed weight examples (bottom row) ===
\node[exbox=blue] (ex1) at (7, -1) {
  \textbf{HotpotQA} (Type I)\\
  $w_{\text{entropy}} = -0.34$\\
  High entropy $\to$ \textcolor{blue}{\textbf{don't}} trigger};
\node[exbox=red] (ex2) at (11, -1) {
  \textbf{APPS Intv} (Type D)\\
  $w_{\text{entropy}} = +0.32$\\
  High entropy $\to$ \textcolor{red}{\textbf{do}} trigger};

\draw[dasharrow] (learn.south) -- ++(0, -0.5) -| (ex1.north);
\draw[dasharrow] (learn.south) -- ++(0, -0.5) -| (ex2.north);

\node[font=\scriptsize\itshape, gray] at (9, -2.3) {
  Same feature, learned opposite direction};

\end{tikzpicture}
}
\caption{\textbf{EAAG pipeline.} Each stage addresses a requirement
from \S\ref{sec:signal-landscape}:
\textsc{Explore} collects signal-agnostic data (Req~iii),
\textsc{Reason} builds a multi-signal feature pool (Req~ii),
and \textsc{Learn} recovers per-environment direction via LASSO (Req~i).
The signed weights reveal whether each signal follows a
Type~I or Type~D pattern (bottom).}
\label{fig:eaag-pipeline}
\end{figure*}
```

---

## Pareto Plot (改进版)

### Prompt for matplotlib

```python
"""
Improved Pareto frontier plot (参考 CATTS Figure 5).

Layout: 2×3 grid, 6 environments
(HotpotQA, APPS Intro, WebShop, FEVER, TWExpress, Plancraft)

For each subplot:
- x-axis: Cost (rollouts per episode)
- y-axis: SR (%)
- Each method = one point

Marker scheme:
- Bounds: gray, marker='o', size=40
  - base_only, always_trigger, oracle
- Fixed-direction baselines: tab10 colormap, marker='^', size=60
  - CaTS, SEAG, CoRefine, CATTS, AUQ, s1_budget
- BSW ablation: marker='x', black, size=50
- EAAG: red/crimson, marker='*', size=200 (prominent!)

Pareto frontier:
- Identify non-dominated points
- Connect with dashed black line
- Light gray shading below frontier

Per-subplot annotations:
- Environment name as subplot title
- Type label: "(Type I)", "(Mixed)", "(Type D)" in gray
- Δ value in corner

Shared legend at bottom (one row, horizontal)

Style:
- figsize=(12, 8)
- seaborn whitegrid style
- Font: 10pt
- Tight layout

Data source: tab_main_results/ CSV files
"""
```

---

## Entropy-Bin Analysis Figure (新增)

### Prompt for matplotlib

```python
"""
SR by entropy bin, showing EAAG's adaptive advantage.
参考 SEAG Figure 4 grouped bar chart.

Layout: 1×3 panels
(a) FEVER (Type I), (b) APPS Intro (Mixed), (c) APPS Interview (Type D)

For each panel:
- x-axis: entropy bins (4 bins: Low, Med-Low, Med-High, High)
  Bins: [0, Q1), [Q1, Q2), [Q2, Q3), [Q3, max]
  where Q1/Q2/Q3 are quartiles of entropy distribution
- y-axis: SR (%) within that entropy bin

Methods shown (4 bars per bin):
1. base_only (gray)
2. Best fixed-direction baseline (blue)
3. always_trigger (light blue, dashed edge)
4. EAAG (red/crimson)

Annotations:
- On top of each bin group: proportion of steps in that bin
  (like SEAG Figure 4: "0.32", "0.21", etc.)
- Number on top of each bar (SR value)

Key visual patterns to highlight:
- Panel (a) FEVER: At HIGH entropy bin, EAAG >> fixed baseline
  (EAAG doesn't trigger; baseline triggers and gets harmed)
- Panel (b) APPS: All methods similar (mixed direction)
- Panel (c) APPS Intv: At HIGH entropy, EAAG ≈ fixed baseline
  (both correctly trigger), but EAAG more selective at LOW entropy

Style:
- figsize=(14, 4)
- Grouped bar chart
- Consistent colors across panels
- Light grid lines

Data source:
- Need per-step data: (env, step, entropy, trigger, U, method)
- From exploration logs + deployment logs
- Compute: bin by entropy quartile, then compute SR per bin per method
"""
```

---

## Trajectory Case Study (新增)

### Prompt for matplotlib/TikZ

```python
"""
Trajectory-level gate decision visualization.
参考 CoRefine Figure 4 tree visualization, 但用 timeline 形式。

Layout: 2 rows, each is one episode trajectory
(a) Top: HotpotQA episode (Type I)
(b) Bottom: APPS Interview episode (Type D)

For each trajectory:

MAIN ELEMENT: Horizontal timeline of steps (circles on a line)
- Each circle = one step
- Circle color:
  * Green filled: EAAG triggers AND U=1 (beneficial trigger)
  * Green hollow: EAAG triggers AND U=0 (wasted trigger)
  * Gray filled: EAAG doesn't trigger AND correct (no need)
  * Red X overlay: where fixed baseline would trigger AND U=0
    (harmful trigger avoided by EAAG)
- Circle size: proportional to entropy at that step (larger = higher entropy)

BELOW TIMELINE: Small line plot of entropy over steps
- Blue line for Type I, red line for Type D

ABOVE TIMELINE: Annotations at key moments
- "High entropy" label at high-entropy steps
- "EAAG: skip" or "EAAG: trigger" decision labels
- "Baseline: trigger → harm!" for harmful baseline decisions

RIGHT SIDE: Outcome summary
- Episode result: Success/Fail
- EAAG SR / Baseline SR

KEY VISUAL CONTRAST:
- In HotpotQA (Type I): Late steps have HIGH entropy (large circles)
  but EAAG shows gray (skip) while baseline shows red X (harmful trigger)
- In APPS Intv (Type D): High-entropy steps show green (beneficial trigger)
  for both EAAG and baseline

Style:
- figsize=(14, 6)
- Clean, timeline-based (not tree)
- Use matplotlib patches for circles
- Consistent with paper color scheme

Data source:
- Select 1 episode per environment from deployment logs
- Need: step, entropy, eaag_decision, baseline_decision, U
- Choose episodes with clear direction contrast
"""
```

---

## Appendix Figures

### Figure A1: $p_I$ Axis Diagram

```
TikZ diagram: horizontal number line from 0 to 1.

AXIS:
- Left label: "p_I = 0 (Pure Type D)"
- Right label: "p_I = 1 (Pure Type I)"
- Vertical dashed line at p_I* ≈ 0.45, labeled "Reversal threshold p_I*"

REGIONS:
- Left of p_I* (0 to 0.45): light green background, label "ρ > 0"
- Right of p_I* (0.45 to 1): light red background, label "ρ < 0"

ENVIRONMENT DOTS (placed at estimated p_I):
- APPS Intv (p_I ≈ 0.2): green dot, large (|ρ|=0.32), label "ρ=+0.32"
- APPS Intro (p_I ≈ 0.45): gray dot, small (|ρ|≈0), label "ρ≈0"
- WebShop (p_I ≈ 0.5): gray dot, label "ρ≈0"
- CRUXEval (p_I ≈ 0.55): gray dot, label "ρ=-0.05"
- Plancraft (p_I ≈ 0.6): gray dot
- HotpotQA (p_I ≈ 0.7): red dot, label "ρ=-0.04"
- TWExpress (p_I ≈ 0.8): red dot, medium (|ρ|=0.29), label "ρ=-0.29"
- FEVER (p_I ≈ 0.9): red dot, large (|ρ|=0.12), label "ρ=-0.12"

Dot size proportional to |ρ|.

BRACKETS below axis:
- "Type D dominant" spanning 0-0.35
- "Mixed / Weak" spanning 0.35-0.65
- "Type I dominant" spanning 0.65-1.0

STYLE: Clean TikZ, single column width, ~4cm height.
```

### Figure A3: AUC Hierarchy Bar Chart

```python
"""
Grouped bar chart showing AUC hierarchy.

x-axis: 4 environments (HotpotQA, APPS Intro, WebShop, FEVER)
y-axis: AUC (0.4 to 1.0)

3 bars per environment:
1. Single entropy (light gray): ~0.50
2. Multi-signal logistic (blue): ~0.83
3. Hidden-state probe (dark blue): ~0.90

Annotations:
- Dashed horizontal line at AUC=0.5 labeled "chance"
- Bracket between bar 1 and bar 2 labeled
  "Signal combination gain (+0.33)"
- Numbers on top of each bar

Style:
- figsize=(8, 4)
- seaborn whitegrid
- Color: gray → blue → dark blue (progression)

Data: Run AUC computation for each gate type on held-out data
from exploration phase D.
"""
```

### Figure A4: Multi-Backbone Signal Heatmap

```python
"""
Three side-by-side heatmaps showing signal-utility ρ across backbones.

Layout: 1×3, sharing y-axis (environments)
Panel titles: "Qwen3-4B", "Phi-3.5-mini", "Llama-3.1-8B"

Each heatmap:
- Rows: 8 environments
- Columns: 5 key signals (step_count, token_entropy, evidence_count,
  is_finish, claim_length)
- Cell color: diverging RdBu colormap, centered at 0
- Annotate ρ value in each cell (2 decimal places)
- Bold border on cells where sign flips vs Qwen3 panel

Shared colorbar on the right, range [-0.7, +0.7]

figsize=(14, 5)
Style: extends current fig1_signal_heatmap.png to 3 panels

Data: From signal discovery runs on each backbone.
Files: tab_signal_discovery/ extended to all 3 backbones.
"""
```

### Figure A5: Cross-Backbone SR Comparison

```python
"""
Grouped bar chart: EAAG vs best fixed baseline across 3 backbones.

x-axis: 8 environments
Two groups per environment:
  Group 1 (blue shades): Best fixed baseline on Qwen3 / Phi-3.5 / Llama
  Group 2 (red shades): EAAG on Qwen3 / Phi-3.5 / Llama

3 shade levels: light=Qwen3, medium=Phi-3.5, dark=Llama

y-axis: SR (%)

Annotations:
- Arrow or bracket showing Δ between EAAG and baseline for each backbone
- Environments sorted by cross-backbone variance

figsize=(14, 5)

Data: From Table A7 (cross-backbone baseline results).
"""
```

### Figure A6: Controlled Information Manipulation

```python
"""
InfoPoor vs InfoRich signal comparison.

Layout: 1×2 panels

Panel (a): Signal ρ comparison
- x-axis: signals (step_count, token_entropy, evidence_count,
  state_length, action_entropy)
- Two bars per signal: InfoPoor (dark blue), InfoRich (light green)
- y-axis: Spearman ρ
- Horizontal line at ρ=0
- Star/highlight on the "winning" signal in each condition
  (step_count for InfoPoor, entropy for InfoRich)

Panel (b): LASSO coefficient comparison
- Same layout as (a) but y-axis = LASSO weight w_i
- Shows EAAG's automatic signal selection shift

figsize=(12, 4)

Data: From controlled HotpotQA experiments.
Run exploration + LASSO separately for each condition.
Files: fig_controlled_reversal/ CSV files.
"""
```

### Figure A7: Full 8-Environment Pareto Plot

```python
"""
Full version of main-text Pareto plot with all 8 environments.

Layout: 2×4 grid

Same design as main-text Figure (Pareto frontier), but including
APPS Interview and CRUXEval panels.

This is the complete version; main text shows 6 representative envs.

figsize=(16, 8)

Data: Same source as main-text Pareto plot.
"""
```

### Figure A8: Computational Cost Breakdown

```python
"""
Stacked bar chart showing total compute cost per method.

x-axis: methods (sorted by total cost, ascending)
  EAAG, s1, CATTS, CaTS, SEAG, CoRefine, AUQ
y-axis: Total compute (GPU-hours for 500 episodes)

Two stacked components per bar:
1. Dark color: Calibration/exploration overhead
   - EAAG: 50 exploration episodes
   - CaTS/SEAG/CoRefine: calibration data collection
   - CATTS: no overhead (uses runtime signals)
   - s1: no overhead (uses budget)
2. Light color: Deployment compute (rollouts per episode × 500)
   - Depends on trigger rate

Annotations:
- Total hours on top of each bar
- EAAG bar highlighted with red border
- Label "zero per-step overhead" arrow pointing to EAAG

figsize=(10, 5)

Data: From Table A3 (computational cost breakdown).
"""
```

### Figure A2: Hyperparameter Sensitivity

```python
"""
Two-panel line plot for hyperparameter robustness.

Panel (a): SR vs N_explore
- x-axis: N_explore ∈ {10, 20, 30, 50, 100}
- y-axis: SR (%)
- 4 lines: HotpotQA, APPS Intro, FEVER, WebShop
- Shaded green region for N≥30 labeled "stable zone"
- Vertical dashed line at N=50 (our default)
- Error bands (3-seed std)

Panel (b): SR vs threshold τ
- x-axis: τ ∈ {0.3, 0.4, 0.5, 0.6, 0.7}
- y-axis: SR (%)
- Same 4 environments
- Vertical dashed line at τ=0.5 (our default)

Style:
- figsize=(12, 4)
- seaborn style, line plot with markers
- Consistent color per environment across panels
- Shared y-axis range

Data: Run EAAG with each hyperparameter sweep value.
200 episodes × 3 seeds per setting.
"""
```
