# Consolidated TODO — All 6 Reviews

> Merged from: review_1 (6/10), review_2 (5/10), review_3 (6/10), review_4 (4/10), review_5 (7/10), review_6 (6.5/10)
> Average score: **5.75/10** (borderline)
> Generated: 2026-03-23

---

## Score Summary

| Reviewer | Persona | Score | Key Concern |
|----------|---------|:-----:|-------------|
| R1 | General | 6 | Single backbone; post-hoc theory |
| R2 | Theory | 5 | Proposition trivial; model unfalsifiable |
| R3 | Agent Systems | 6 | Optimizer-environment confound |
| R4 | Skeptical Empiricist | 4 | 34W/2L overclaimed; stats weak |
| R5 | Applied ML | 7 | Minor issues only |
| R6 | Senior AC | 6.5 | Multi-backbone is the decision point |

---

## P0: MUST DO (all reviewers agree)

### P0-1. Multi-backbone direction reversal verification
- **Raised by**: R1(M3), R2(cross-ref), R3(P1-2), R4(P2-1), R5(C1), R6(T1.1) — **6/6 reviewers**
- **What**: Run at least 1 additional backbone (e.g., Llama 3 8B) on 4 core environments (HotpotQA, APPS Intro, WebShop, FEVER). Compute ρ(entropy, U) and ρ(step_count, U). Show direction reversal persists.
- **Why**: Paper claims reversal is an environment property, not model-specific. Untested with one backbone = fatal weakness.
- **Decision gate**: If reversal persists → accept probability +15-20%. If not → major pivot needed.
- **Effort**: 1-2 weeks GPU time + 1 day analysis
- **Files**: `experiment/tab_signal_discovery/`, `experiment/tab_main_results/`
- **Paper sections**: §3.1 (add multi-backbone ρ table), §6 Limitations (remove/weaken single-backbone caveat)
- **Score impact**: 5.75 → **6.5-7.0**

### P0-2. Qualify 34W/2L with statistical significance
- **Raised by**: R1(m2), R3(P3-4), R4(P0-1), R5(C3), R6(T1.3) — **5/6 reviewers**
- **What**: Report "34 wins (18 statistically significant) vs 2 losses" instead of bare 34W/2L. Add mean SR improvement per baseline. Include bootstrap CIs in main table or appendix.
- **Why**: 12/30 "wins" have CIs including zero. Bare count is misleading.
- **Effort**: 2-3 hours (data already in `experiment/tab_significance/data.csv`)
- **Paper sections**: Abstract, §1 P5, §5.2
- **Score impact**: +0.3-0.5 across reviewers

### P0-3. Replace "emergent adaptive behavior"
- **Raised by**: R1(m5), R3(P3-2), R4(m3), R5(C4), R6(T1.4) — **5/6 reviewers**
- **What**: Replace "emergent" with "environment-adaptive gating patterns" or "learned adaptive behavior" throughout.
- **Why**: Logistic regression responding to different feature distributions is not "emergent." Term has specific connotations post-Schaeffer et al.
- **Effort**: 30 min (5 occurrences in writing guide: Abstract, §1 P5, §5.2, §5.3, §7)
- **Files**: `VOC_PAPER_WRITING_GUIDE.md`
- **Score impact**: +0.2-0.3 (removes easy attack surface)

---

## P1: HIGH PRIORITY (3+ reviewers agree)

### P1-1. Strengthen Proposition 1
- **Raised by**: R1(M2), R2(P1), R3(P2-3), R6(T2.1) — **4/6 reviewers**
- **What**: Either (A) prove quantitative bound: SR degradation ≥ f(|ρ|) when direction is wrong (BSW data supports this), or (B) prove sample complexity: N_explore ≥ O(1/|ρ|²) episodes suffice for correct direction recovery with prob ≥ 1-δ. Minimal fix: add Remark acknowledging the proposition's structural nature and supplement with the quantitative empirical relationship.
- **Why**: Current proposition is trivially true ("two opposite directions can't both be right"). Reviewer 2 calls it a "tautology."
- **Effort**: 1-2 days (formal proof or empirical bound)
- **Paper sections**: §3.2, Appendix C
- **Score impact**: +0.5-1.0

### P1-2. Make Two-Source Model falsifiable / reframe
- **Raised by**: R1(M1), R2(P2), R6(T1.2) — **3/6 reviewers**
- **What**: Two options:
  - (A) **A priori prediction test**: Given a NEW environment description, predict Type I/D before running experiments. Use held-out environments (e.g., AlfWorld, ScienceQA).
  - (B) **Reframe as explanatory framework**: Explicitly state the model is a post-hoc explanatory tool (like the epistemic/aleatoric distinction), not a predictive theory. Remove "provably" language. Add falsification criteria.
- **Why**: p_I is unobservable, α/β are free parameters. Model can explain any ρ value post-hoc = unfalsifiable.
- **Effort**: Option A: 1-2 weeks (new experiments). Option B: 1 day (rewriting).
- **Paper sections**: §3.2, §5.4
- **Score impact**: +0.5-1.0

### P1-3. Add ρ confidence intervals
- **Raised by**: R2(P5), R4(P0-2), R5(implicit) — **3/6 reviewers**
- **What**: Report bootstrap 95% CIs for all Spearman ρ values in Table 1 (signal discovery). Flag which correlations are significant at p<0.05.
- **Why**: 5/8 environments have |entropy ρ| < 0.05. Without CIs, readers can't assess whether these are noise. Direction reversal story depends heavily on FEVER vs APPS Interview contrast.
- **Effort**: 3-4 hours
- **Paper sections**: §3.1 Table 1, Appendix
- **Score impact**: +0.3-0.5

### P1-4. CATTS cost footnote
- **Raised by**: R1(m1), R3(P4), R4(P1-3), R5(P2) — **4/6 reviewers**
- **What**: Add table footnote: "CATTS additionally incurs K=5 forward passes per step for voting (not reflected in deployment cost column)."
- **Effort**: 10 min
- **Paper sections**: Table 1 / main results table footnote
- **Score impact**: +0.1-0.2

---

## P2: MEDIUM PRIORITY (2+ reviewers agree)

### P2-1. Disentangle optimizer type from environment
- **Raised by**: R3(P1-1) — **1/6 reviewers but critical**
- **What**: Run a cross-optimizer experiment — e.g., use K-variant sampling on HotpotQA (normally per-action eval) or per-action eval on APPS (normally K-variant). If direction reversal persists under a different optimizer, it's truly an environment property.
- **Why**: Per-action eval maps to Type I envs, K-variant maps to Type D envs. The confound means reversal might be an optimizer-environment interaction, not pure environment effect.
- **Effort**: 1 week GPU time
- **Paper sections**: §5.4 or Appendix
- **Score impact**: +0.3-0.5 (eliminates a strong potential objection)

### P2-2. Coverage proxy → appendix
- **Raised by**: R1(m4), R4(P2-2), R5(P2), R6(T2.3) — **4/6 reviewers**
- **What**: Move §5.7 (observable proxy for p_I, r=+0.75 on 6 points, p=0.086) from main text to Appendix D.
- **Why**: Not statistically significant. Weakens rather than strengthens the main text.
- **Effort**: 30 min
- **Score impact**: +0.2 (removes attack surface, saves ~0.3 pages)

### P2-3. APPS Intro ρ=+0.012 framing
- **Raised by**: R1(m3), R4(P3-2) — **2/6 reviewers**
- **What**: Rephrase as "not statistically significant (ρ=+0.012, p=0.63)" rather than "near-zero signal." Clarify: absence of evidence ≠ evidence of absence.
- **Effort**: 15 min
- **Paper sections**: Abstract, §3.1

### P2-4. Exploration budget sensitivity
- **Raised by**: R1(P4), R3(P2-2), R6(T2.4) — **3/6 reviewers**
- **What**: Run EAAG with N_explore ∈ {10, 20, 30, 50, 100} on 2-3 environments. Show stability. Report in appendix.
- **Effort**: 2-3 days
- **Paper sections**: Appendix E

### P2-5. RL baseline comparison or discussion
- **Raised by**: R1(P4), R3(P2-1), R6(T3) — **3/6 reviewers**
- **What**: Either (A) run AdaptThink/Thinkless on 2-3 environments, or (B) add substantive discussion in §2 explaining why they're not directly comparable (different training paradigm, per-environment RL training).
- **Effort**: Option A: 1-2 weeks. Option B: 1 hour.
- **Paper sections**: §2.1, §5.2

### P2-6. Formalize LLM Reason step
- **Raised by**: R1(M4), R3(P4), R6(T3) — **3/6 reviewers**
- **What**: Include exact prompt template in appendix. Run sensitivity analysis (3-5 prompt variations). Note that ablation shows <1pp impact in 4/6 envs → present as optional enhancement.
- **Effort**: 1-2 days
- **Paper sections**: §4 Step 2, Appendix B

---

## P3: LOW PRIORITY (1-2 reviewers, nice to have)

### P3-1. Environment selection justification
- **Raised by**: R4(P1-2)
- **What**: Add paragraph justifying the 8 environments were chosen for diversity (not to demonstrate reversal). Note that paper roles (Main, Diagnostic, Appendix) were assigned based on data availability, not cherry-picked for narrative.
- **Paper sections**: §5.1

### P3-2. LLM ablation Plancraft discussion
- **Raised by**: R1(m6), R5(implicit)
- **What**: Explicitly discuss that removing LLM improves Plancraft by +3.9pp — LLM features can be harmful in rollout-harmful environments, mirroring the paper's core insight.
- **Paper sections**: §5.3 (already partially fixed)

### P3-3. Simpson's paradox formal DAG
- **Raised by**: R2(P3)
- **What**: Add a causal DAG showing the structure (environment type Z → entropy H, Z → utility U) that produces Simpson's paradox. Strengthen the connection from analogy to formal correspondence.
- **Paper sections**: §3.2

### P3-4. Fix "provably incomplete" language
- **Raised by**: R2(P5)
- **What**: Soften "provably incomplete" to "cannot guarantee non-negative VOC" or "theoretically limited." The proof only covers the fixed-direction linear gate class.
- **Paper sections**: §3.3, §7

### P3-5. Detail the 2 losses
- **Raised by**: R1(Q6), R4(implicit)
- **What**: Identify which environment/baseline pairs. Report if within noise (bootstrap CI includes 0).
- **Data**: `experiment/tab_winloss/data.csv`, `experiment/tab_significance/data.csv`

### P3-6. Page budget management
- **Raised by**: R5(P4), R6(page budget)
- **What**: Current draft ~10.25 pages. NeurIPS limit 9 pages. Need to cut ~1.25 pages.
  - Move coverage proxy to appendix (-0.3p)
  - Compress §2 Related Work (-0.2p)
  - Tighten §5.5 Extreme Environments (-0.2p)
  - Compress design notes (not in final submission) (-0.3p)
  - Condense §3.3 Design Implications (-0.2p)

---

## Execution Plan

### Week 1: Experiments (P0-1, P2-1)
- [ ] Launch multi-backbone experiments (Llama 3 8B on HotpotQA, APPS Intro, WebShop, FEVER)
- [ ] Launch cross-optimizer experiment (K-variant on HotpotQA)
- [ ] Launch exploration sensitivity (N ∈ {10,20,30,50,100})

### Week 2: Analysis + Writing (P0-2, P0-3, P1-1 through P1-4, P2-2 through P2-6)
- [ ] Analyze multi-backbone results → **DECISION GATE**: if reversal confirmed, proceed; if not, pivot
- [ ] Qualify 34W/2L with significance
- [ ] Replace "emergent" (5 occurrences)
- [ ] Add ρ confidence intervals
- [ ] CATTS cost footnote
- [ ] Strengthen Proposition 1 (quantitative bound or sample complexity)
- [ ] Reframe Two-Source Model
- [ ] Move coverage proxy to appendix
- [ ] Fix APPS Intro framing
- [ ] Formalize LLM Reason step

### Week 3: Polish (P3-*, page budget)
- [ ] All P3 items
- [ ] Page budget cuts to reach 9 pages
- [ ] Final proofreading pass

---

## Estimated Score Impact

| Action Set | Current → Expected | Acceptance Prob |
|------------|:------------------:|:---------------:|
| Nothing | 5.75 | ~30% |
| P0 only (multi-backbone + qualify W/L + drop "emergent") | 5.75 → **6.5** | ~50% |
| P0 + P1 (+ Proposition + ρ CIs + CATTS) | 5.75 → **7.0** | ~65% |
| P0 + P1 + P2 (+ optimizer confound + appendix cleanup) | 5.75 → **7.5** | ~75% |
| All P0-P3 | 5.75 → **7.5-8.0** | ~80% |

**Bottom line**: Multi-backbone (P0-1) alone drives ~50% of the score improvement. It is non-negotiable.
