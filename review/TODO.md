# Review Response TODO

> Generated from: `review/review_1.md` (NeurIPS 2026 self-review, 2026-03-23)
> Overall score: Weak Accept (6/10)

---

## Priority 1: Critical (must fix before submission)

- [ ] **M3: Multi-backbone validation** — Run Llama 3 8B (or similar) on 4 core environments (HotpotQA, APPS Intro, WebShop, FEVER). Show direction reversal persists. This is the single highest-impact improvement.
  - File to update: `experiment/tab_signal_discovery/`, `experiment/tab_main_results/`
  - Paper sections: §3.1 (add multi-backbone ρ comparison), §6 Limitations (remove or weaken single-backbone caveat)

- [ ] **M1: Two-Source Model falsifiability** — Add a priori prediction experiment: given a NEW environment's task description, predict Type I/D *before* running experiments. Candidate new environments: AlfWorld (navigation), ScienceQA (visual QA), or InterCode (bash).
  - Alternative (lighter): formalize the mapping criteria (information sufficiency, action reversibility) into a decision tree that can be applied without seeing ρ values first.
  - Paper sections: §3.2 (strengthen environment mapping), §5.4 (add prediction test)

## Priority 2: Important (strongly recommended)

- [ ] **M2: Strengthen Proposition 1** — Either (a) prove a quantitative bound: SR degradation scales with |ρ| (the BSW data already supports this empirically, formalize it), or (b) prove exploration convergence: with N≥N_min episodes, LASSO recovers correct direction sign with probability ≥1-δ.
  - Paper sections: §3.2, Appendix C

- [ ] **M4: Formalize LLM Reason step** — Include exact prompt template in appendix. Run sensitivity analysis (3-5 prompt variations). If <1pp impact in most envs, present as optional with a clear statement on when it matters (WebShop-like environments).
  - Paper sections: §4 Step 2, Appendix B

- [ ] **m1: CATTS cost footnote** — Add table footnote: "CATTS additionally incurs K=5 forward passes per step for voting, not reflected in deployment cost."
  - Paper sections: Table 1 footnote

- [ ] **m5: Replace "emergent"** — Change "emergent adaptive behavior" to "environment-adaptive gating patterns" throughout (Abstract, §1 P5, §5.2, §5.3, §7).
  - Files: `VOC_PAPER_WRITING_GUIDE.md` (5 occurrences)

## Priority 3: Recommended improvements

- [ ] **m2: Win/loss granularity** — Add mean SR improvement per baseline alongside W/L count. Note that 18/30 comparisons are statistically significant; qualify the 34W/2L claim with "18 of which reach statistical significance."
  - Paper sections: §5.2, `experiment/tab_significance/`

- [ ] **m3: APPS Intro framing** — Rephrase "near-zero signal" to "not statistically significant (ρ=+0.012, p=0.63, n=1567)" — emphasize it's absence of evidence, not evidence of absence.
  - Paper sections: Abstract, §3.1 Obs 1

- [ ] **m4: Coverage proxy → appendix** — Move §5.7 (observable proxy for p_I) entirely to Appendix D. The r=+0.75 on 6 points with p=0.086 is not strong enough for main text.
  - Paper sections: §5.4/5.7 → Appendix D

- [ ] **m6: LLM ablation Plancraft** — Explicitly discuss that LLM features can be harmful in rollout-harmful environments (Plancraft -3.9pp). Frame as: "the LLM's value is environment-dependent, mirroring the paper's core finding."
  - Paper sections: §5.3 (already partially fixed, verify framing)

## Priority 4: Nice to have

- [ ] **Exploration sensitivity** — Run EAAG with N_explore ∈ {10, 20, 30, 50, 100} on 2-3 environments. Show stability.
  - Paper sections: Appendix E

- [ ] **RL baseline comparison** — If feasible, compare against AdaptThink or Thinkless on 2-3 environments to address reviewer Q4.
  - Paper sections: §5.2 or Appendix

- [ ] **Q6: Detail the 2 losses** — Identify which specific environment/baseline pairs account for the 2 losses. Report if they're within noise (bootstrap CI includes 0).
  - Data source: `experiment/tab_winloss/data.csv`, `experiment/tab_significance/data.csv`

---

## Progress Tracking

| Priority | Total | Done | Remaining |
|----------|:-----:|:----:|:---------:|
| P1 Critical | 2 | 0 | 2 |
| P2 Important | 4 | 0 | 4 |
| P3 Recommended | 4 | 0 | 4 |
| P4 Nice to have | 3 | 0 | 3 |
| **Total** | **13** | **0** | **13** |

---

## Estimated Impact on Score

| Action | Current → Expected |
|--------|-------------------|
| M3 multi-backbone done | 6 → **7** |
| M3 + M1 a priori prediction | 6 → **7-8** |
| All P1+P2 done | 6 → **7** |
| All P1+P2+P3 done | 6 → **7-8** |
