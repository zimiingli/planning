# TODO: Addressing Review 4 (Skeptical Empiricist)

**Review Score**: 4/10 (Borderline Reject)
**Reviewer Focus**: Experimental methodology, statistical rigor, overclaiming
**Date**: 2026-03-23

---

## Priority Classification

- **P0 (Must Fix -- blocks acceptance)**: Issues the reviewer explicitly calls "Critical" or "High severity"
- **P1 (Should Fix -- significantly strengthens paper)**: "Major" severity issues
- **P2 (Nice to Fix -- improves but not essential)**: "Medium" severity issues
- **P3 (Optional -- minor polish)**: Minor concerns

---

## P0: Critical Issues (Must Fix Before Resubmission)

### P0-1: Replace misleading 34W/2L headline with significance-adjusted counts
**Review ref**: M1
**Problem**: 12 of 34 "wins" have 95% CIs including zero. Current headline inflates evidence.
**Action items**:
- [ ] Recount wins using only statistically significant comparisons (current: 18 significant wins / 0 significant losses out of 30 comparisons)
- [ ] Run significance tests for the missing environments (FEVER, APPS Intv, CRUXEval are absent from tab_significance -- the "APPS" row appears to be APPS Intro only)
- [ ] Replace "34W/2L" throughout paper (abstract, intro P5, Section 5.2, conclusion) with honest formulation, e.g.: "18 statistically significant wins and 0 significant losses out of 30 head-to-head comparisons (12 indeterminate)"
- [ ] Alternatively, keep the 34W/2L but always immediately qualify: "of which 18 are statistically significant at the 95% level"
- [ ] Consider reframing from win-counting to mean SR improvement + effect sizes
**Files to edit**: Abstract, Section 1 P5, Section 3.1 Obs 4, Section 5.2, Section 7 Conclusion
**Estimated effort**: 2 hours (reanalysis + rewrite)

### P0-2: Add confidence intervals for ALL Spearman rho values
**Review ref**: M2
**Problem**: Core argument rests on rho signs/magnitudes but no CIs reported. Many rho values (5 of 8 entropy correlations) have |rho| < 0.05.
**Action items**:
- [ ] Compute 95% bootstrap CIs for every rho in Table 2 (tab_signal_discovery)
- [ ] Add CI columns to Table 2 or report inline
- [ ] Flag which rho values have CIs that include zero (expected: HotpotQA entropy, APPS Intro entropy, WebShop entropy, CRUXEval entropy, Plancraft entropy)
- [ ] Revise "direction reversal" narrative to restrict to environments where CI excludes zero: FEVER (-0.119), APPS Interview (+0.317), TWExpress (-0.290)
- [ ] Acknowledge that in 5/8 environments, entropy carries no statistically detectable signal -- the "reversal" is primarily between FEVER/TWExpress (negative) and APPS Interview (positive)
- [ ] Reframe Observation 1 from "direction reverses across 8 environments" to something more precise, e.g.: "direction is significantly negative in 2 environments, significantly positive in 1, and indistinguishable from zero in 5 -- but the strongest non-entropy signal also varies"
**Files to edit**: Table 2, Section 3.1 (Obs 1), Abstract, Intro P3
**Estimated effort**: 4 hours (bootstrap computation + rewriting narrative)

---

## P1: Major Issues (Should Fix)

### P1-1: Increase statistical power or temper claims
**Review ref**: M3
**Problem**: 3 seeds x 200 episodes = 600 total. SE ~ 2pp at p=0.5. Many comparisons have delta < 4pp.
**Action items**:
- [ ] Option A (preferred): Run 5 seeds instead of 3, ideally with 300+ episodes per seed
- [ ] Option B (faster): Keep 3 seeds but restrict claims to comparisons where |delta| > 2*SE
- [ ] Option C (narrative): Explicitly state power limitations, e.g.: "Our evaluation protocol detects effects > ~5pp with 80% power. Comparisons with smaller deltas should be interpreted as 'EAAG is competitive' rather than 'EAAG wins.'"
- [ ] Report per-comparison power analysis in appendix
**Files to edit**: Section 5.1 Setup, Section 5.2 Main Results, Appendix
**Estimated effort**: Option A: 1-2 weeks (GPU time). Option B/C: 3 hours.

### P1-2: Justify or acknowledge environment selection
**Review ref**: M4
**Problem**: Environments chosen to span the Two-Source Model spectrum = selection bias.
**Action items**:
- [ ] Disclose total number of environments screened and selection criteria
- [ ] If environments were selected post-hoc, acknowledge this honestly in Section 5.1
- [ ] Consider adding 2-3 "unseen" environments as a held-out test of the Two-Source Model (predict rho direction BEFORE running, then verify)
- [ ] Remove or demote the "paper_role" designations (Main, Diagnostic, Appendix) from the data that could leak into the paper
- [ ] Add a sentence in Section 5.1 such as: "We selected environments to maximize task diversity rather than to demonstrate any particular phenomenon"
**Files to edit**: Section 5.1, tab_env_setup
**Estimated effort**: 2-4 days for new environments, 1 hour for disclosure

### P1-3: Fix cost metric to include total lifecycle cost
**Review ref**: M5
**Problem**: Deployment-only cost systematically favors EAAG by hiding exploration overhead and baseline calibration costs.
**Action items**:
- [ ] Add a "Total Cost" column or a separate table (Appendix B.5) showing:
  - Phase 1 / exploration cost (in equivalent rollout-episodes)
  - Per-step overhead (CATTS K=5 forward passes)
  - Deployment cost (current metric)
  - Total lifecycle cost for a 500-episode deployment scenario
- [ ] Add footnote to main results table noting CATTS per-step overhead not captured by rollout count
- [ ] Consider presenting deployment cost AND total cost in main table
- [ ] Rewrite Section 5.1 cost definition to acknowledge the limitation
**Files to edit**: Section 5.1, Table (main results), Appendix B.5
**Estimated effort**: 4 hours

### P1-4: Temper ablation hierarchy claims
**Review ref**: M6
**Problem**: "Direction >> signals >> complexity" is overclaimed. Multi-signal is worse than best_single in APPS. LLM hurts in Plancraft.
**Action items**:
- [ ] Add per-environment breakdown to the hierarchy claim
- [ ] Acknowledge that multi-signal < best_single in APPS (0.761 vs 0.778)
- [ ] Acknowledge that LLM is harmful in Plancraft (-3.9pp)
- [ ] Revise "LLM provides robustness, not accuracy" to: "LLM provides task-specific features that help in some environments (FEVER: +9.1pp) but can introduce noise in others (Plancraft: -3.9pp)"
- [ ] State hierarchy with proper caveats: "Direction is consistently the dominant factor. Multi-signal features generally help but not universally. LLM features are environment-specific."
**Files to edit**: Section 5.3 Ablation
**Estimated effort**: 2 hours

---

## P2: Medium Priority Issues

### P2-1: Add a second backbone experiment
**Review ref**: M3 from review_1, M4 (implicit)
**Problem**: Single backbone (Qwen3-4B) limits generalizability.
**Action items**:
- [ ] Run EAAG + 2-3 baselines on 3-4 core environments (HotpotQA, FEVER, APPS Interview, WebShop) with a second backbone (e.g., Llama 3 8B or Qwen3-8B)
- [ ] Show whether rho direction reversal persists with different backbone
- [ ] This would address both the reviewer's backbone concern AND strengthen the environment-dependence claim
**Estimated effort**: 1-2 weeks (significant GPU time)

### P2-2: Remove or substantially revise the coverage proxy analysis
**Review ref**: m4
**Problem**: r = +0.75 on 6 points (p=0.086) after excluding outlier. r = +0.27 on 7 points (p=0.56) with outlier. Ad hoc operationalizations.
**Action items**:
- [ ] Option A: Remove entirely from main text, move to appendix as "preliminary"
- [ ] Option B: Strengthen with more environments or better proxy operationalization
- [ ] If keeping, must present both with and without TWExpress, and acknowledge p > 0.05
**Files to edit**: Section 5.7 / Appendix D
**Estimated effort**: 1 hour (removal) or 1-2 days (strengthening)

### P2-3: Fix stratified reversal inconsistencies
**Review ref**: m6
**Problem**: Stratified data does not consistently support claims. WebShop shows no clear pattern. FEVER all strata non-significant. APPS non-monotonic.
**Action items**:
- [ ] Review all stratified results and only claim reversal "persists" for environments where strata data actually supports this (HotpotQA clearly, TWExpress partially)
- [ ] For WebShop/FEVER/APPS: either explain the discrepancy or remove from the "reversal persists" claim
- [ ] Consider whether the stratification is too fine-grained for the available sample sizes (FEVER late stratum: n=18)
**Files to edit**: Section 5.6
**Estimated effort**: 3 hours

### P2-4: Apply multiple comparison correction
**Review ref**: m5
**Problem**: 30 comparisons at alpha=0.05 expects 1.5 false positives. Holm-Bonferroni mentioned in guide but not applied.
**Action items**:
- [ ] Apply Holm-Bonferroni correction to all 30 pairwise comparisons
- [ ] Report both corrected and uncorrected significance
- [ ] Update the significant win count accordingly (may drop from 18)
**Files to edit**: tab_significance, Section 5.6 statistical significance paragraph
**Estimated effort**: 2 hours

---

## P3: Minor Issues (Optional Polish)

### P3-1: Replace "emergent adaptive behavior" terminology
**Review ref**: m1
- [ ] Replace "emergent" with "adaptive" or "learned" throughout
- [ ] Remove "emergent" from abstract and conclusion

### P3-2: Address Proposition 1 triviality
**Review ref**: m3
- [ ] Either strengthen to a non-trivial result (e.g., sample complexity bound for direction discovery) or explicitly acknowledge it as a "formalization of the observation" rather than a novel theoretical result
- [ ] Consider adding a proposition about convergence guarantees for the LASSO direction learner

### P3-3: Fix trigger rate description for Plancraft
**Review ref**: m8
- [ ] Replace "decays from 49% to <20%" with accurate description acknowledging non-monotonicity
- [ ] Consider showing a smoothed trend line rather than raw per-step data

### P3-4: Clarify Two-Source Model circularity
**Review ref**: m2
- [ ] Add explicit disclosure that environment-type mapping is descriptive, not predictive
- [ ] The controlled reversal (InfoPoor/InfoRich) is the strongest defense -- emphasize this more
- [ ] Acknowledge the InfoPoor anomaly (rho = +0.119 positive, contradicting Type I prediction) more prominently

### P3-5: Add held-out environment prediction
**Review ref**: m7
- [ ] If feasible: choose 1-2 new environments, predict rho direction from task description alone using the Two-Source Model, then run the experiment
- [ ] This would transform the model from "post-hoc explanation" to "predictive framework"

---

## Implementation Priority Order

1. **P0-1** (34W/2L fix) -- 2 hours -- highest impact on reviewer perception
2. **P0-2** (rho CIs) -- 4 hours -- addresses the core statistical criticism
3. **P1-3** (cost metric) -- 4 hours -- easy to add, removes a clean attack vector
4. **P1-4** (ablation caveats) -- 2 hours -- easy rewrite, shows intellectual honesty
5. **P1-2** (environment justification) -- 1 hour disclosure, 2-4 days for new envs
6. **P2-4** (multiple comparison correction) -- 2 hours
7. **P1-1** (statistical power) -- depends on approach chosen
8. **P2-3** (stratified analysis fix) -- 3 hours
9. **P2-2** (coverage proxy) -- 1 hour
10. **P2-1** (second backbone) -- 1-2 weeks
11. **P3-*** (minor polish) -- 2-3 hours total

**Total estimated effort for P0+P1**: ~16 hours of writing/analysis + potential 1-2 weeks GPU time
**Total estimated effort for all items**: ~24 hours of writing/analysis + 2-3 weeks GPU time

---

## Cross-References to Other Reviews

- **Review 1 (M3)**: Also flags single backbone limitation -- P2-1 addresses both
- **Review 1 (m2)**: Also flags win/loss coarseness -- P0-1 addresses both
- **Review 1 (m1)**: Also flags CATTS cost misleading -- P1-3 addresses both
- **Review 1 (m5)**: Also flags "emergent" terminology -- P3-1 addresses both
- **Review 1 (m4)**: Also flags coverage proxy weakness -- P2-2 addresses both
