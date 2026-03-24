# Review Response TODO

> Generated from: `review/review_5.md` (NeurIPS 2026 review, applied ML researcher perspective)
> Overall score: Accept (7/10)
> Reviewer focus: Practical utility, adoption feasibility, "finding paper" positioning

---

## Priority 1: High-Impact Improvements (would solidify acceptance)

- [ ] **C1: Multi-backbone validation (2-3 environments)**
  - Run a second backbone (e.g., Llama 3 8B or Qwen2.5-7B) on FEVER, APPS Interview, and HotpotQA
  - Goal: show that the SIGN of rho is preserved (magnitude may differ)
  - Even a short table (3 environments x 2 backbones) showing consistent direction would address this concern
  - Reviewer explicitly says "even showing that the sign of rho is preserved would substantially strengthen the paper"
  - Paper sections: Section 3.1 (add row to Table 1 or supplementary table), Section 6 Limitations
  - Estimated effort: Medium (need to set up second backbone, run exploration on 3 environments)

- [ ] **C2: Strengthen controlled reversal experiment (InfoPoor/InfoRich)**
  - Current issue: InfoPoor shows entropy rho = +0.119 (weakly positive), contradicting Two-Source Model prediction of negative rho
  - Options: (a) increase sample size to get tighter CI, (b) use a more extreme InfoPoor manipulation (e.g., no search at all, just the question), (c) provide a clearer theoretical explanation for why the prediction fails in this controlled setting
  - The caveat is currently buried in parenthetical text -- make it a prominent acknowledgment
  - Paper sections: Section 5.4, Appendix D
  - Estimated effort: Low-Medium

---

## Priority 2: Straightforward Fixes (reviewer explicitly flagged)

- [ ] **C3: Refine 34W/2L reporting**
  - Change to: "EAAG achieves statistically significant SR improvements in 18/30 head-to-head comparisons, with no statistically significant losses"
  - Keep 34W/2L as secondary metric but qualify it
  - Paper sections: Abstract, Section 1 P5, Section 5.2, Section 7
  - Estimated effort: Low (text edits only)

- [ ] **C4: Replace "emergent adaptive behavior" terminology**
  - Change to "environment-adaptive gating patterns" throughout
  - Locations: Abstract, Section 1 P5, Section 5.2, Section 5.3, Section 7
  - Reviewer specifically cites Schaeffer et al. (the paper's own reference) as reason this term is misleading
  - Estimated effort: Low (find-and-replace with care)

- [ ] **CATTS cost footnote in Table 1**
  - Add: "CATTS additionally incurs K=5 forward passes per step for vote computation, not reflected in the deployment cost column"
  - Paper sections: Table 1 footnote
  - Estimated effort: Trivial

- [ ] **Coverage proxy section (Section 5.7) move to appendix**
  - r = +0.75 on 6 data points with p = 0.086 is not strong enough for main text
  - Reviewer says it "weakens rather than strengthens the theory"
  - Move entirely to Appendix D as supplementary evidence
  - Paper sections: Section 5.7 -> Appendix D
  - Estimated effort: Low (restructure only)

---

## Priority 3: Strengthening Arguments (would push toward strong accept)

- [ ] **Operationalize the prescriptive framework**
  - Reviewer says the framework is "directionally useful but needs more operationalization"
  - Create a concrete decision tree or checklist:
    - "Does the task require external information retrieval?" -> likely Type I
    - "Are there multiple valid solution strategies?" -> likely Type D
    - "Is information self-contained in the problem statement?" -> likely Type D
    - "Does success depend on finding specific external evidence?" -> likely Type I
  - Could be a small figure or table in Section 6 Discussion
  - Paper sections: Section 6 (prescriptive framework paragraph)
  - Estimated effort: Low (conceptual work, small addition)

- [ ] **Exploration budget convergence diagnostic**
  - Reviewer asks: "Is there a principled way to determine when sufficient exploration data has been collected?"
  - Propose monitoring LASSO coefficient sign stability across bootstrap resamples of exploration data
  - If coefficient signs are stable across 90%+ of resamples, exploration is sufficient
  - Paper sections: Section 4 Step 1 or Appendix B
  - Estimated effort: Low-Medium (run bootstrap analysis on existing data)

- [ ] **FEVER curriculum exploration experiment**
  - Reviewer suggests: always-trigger for first 10 episodes, then random exploration for remaining 40
  - If this closes the FEVER gap (49.8% -> closer to 90%+), it both validates the exploration-bias explanation and provides a practical fix
  - Paper sections: Section 6 (FEVER and exploration bias), possibly Section 5.5
  - Estimated effort: Medium (needs new experiment run)

- [ ] **Online adaptation evidence**
  - Reviewer asks whether the learned direction ever changes during deployment
  - Track LASSO coefficient signs over deployment episodes (after initial exploration)
  - If signs are stable, report this as evidence that 50-episode exploration is sufficient
  - If signs shift, this motivates the online adaptation mechanism
  - Paper sections: Section 4.4 (Online Adaptation), Appendix E
  - Estimated effort: Low (analyze existing deployment logs)

---

## Priority 4: Page Budget (must do before submission)

- [ ] **Trim approximately 1.25 pages to meet 9-page NeurIPS limit**
  - Current estimate: approximately 10.25 pages
  - Recommended cuts (in priority order):
    1. Section 5.2 per-environment analysis: move HotpotQA and APPS Intro bullet points to appendix (~0.3 pages)
    2. Section 5.7 coverage proxy: move to Appendix D (~0.2 pages, already flagged above)
    3. Section 2.1 Related Work: tighten signal-based and vote-based paragraphs (~0.2 pages)
    4. Section 4 "Why Simplicity" paragraph: condense to 3 sentences (~0.15 pages)
    5. Section 6 Future Directions: move "multi-agent coordination" paragraph to appendix (~0.15 pages)
    6. Section 1 P2: reduce mechanism enumeration, consolidate citations (~0.1 pages)
    7. Section 6 Broader Impact: condense to 2 sentences (~0.1 pages)
  - Total savings: approximately 1.2 pages
  - Paper sections: Multiple (see above)
  - Estimated effort: Medium (careful editing to preserve narrative flow)

---

## Reviewer-Specific Notes

This reviewer is leaning positive (7/10 Accept) and values:
- **Practical utility above all** -- the "Monday morning test" is the key criterion
- **Simplicity as a feature** -- explicitly appreciates EAAG's adoption advantage over RL-based methods
- **Honest limitations** -- FEVER discussion is cited as a strength, not a weakness
- **"Finding paper" positioning** -- accepts the Finding > Theory > Method hierarchy

The reviewer's remaining concerns are primarily about confidence in generality (single backbone) and operationalization (making the prescriptive framework more concrete). These are addressable without major new experiments.

Key insight from this review: **The prescriptive framework is the most underrated contribution.** The reviewer explicitly identifies "characterize information structure first" as potentially the paper's most durable impact. Consider elevating this in the presentation -- perhaps adding a concrete decision tree figure that practitioners can reference.

---

## Cross-Reference with Review 1

| Issue | Review 1 (6/10) | Review 5 (7/10) | Consensus |
|-------|:---:|:---:|-----------|
| Multi-backbone | M3 (Critical) | C1 (High-Impact) | Both flag as top priority |
| Two-Source Model | M1 (Post-hoc, hard to falsify) | C2 (Useful simplification) | Review 5 more charitable; strengthen controlled experiment either way |
| Proposition 1 trivial | M2 (Medium) | Not flagged | Review 5 implicitly accepts it as sufficient |
| Method novelty | M4 (Technically thin) | S3 (Simplicity is adoption advantage) | Opposite reads; Review 5's framing is more aligned with "finding paper" positioning |
| "Emergent" overclaim | m5 (Minor) | C4 (Minor) | Both flag; easy fix |
| CATTS cost | m1 (Minor) | Mentioned | Both flag; easy fix |
| 34W/2L granularity | m2 (Minor) | C3 (Minor) | Both flag; easy fix |
| Coverage proxy weak | m4 (Minor) | Mentioned | Both say move to appendix |
| FEVER gap | Noted as honest | C5 (Minor, suggest curriculum fix) | Both accept explanation; curriculum experiment would help |
| Prescriptive framework | Not discussed | S4 (Most underrated contribution) | New insight from Review 5 |

**Highest-consensus actions:**
1. Multi-backbone validation (both reviewers' top priority)
2. Replace "emergent" terminology (both flag)
3. CATTS cost footnote (both flag)
4. Move coverage proxy to appendix (both flag)
5. Refine 34W/2L reporting (both flag)

---

## Progress Tracking

| Priority | Total | Done | Remaining |
|----------|:-----:|:----:|:---------:|
| P1 High-Impact | 2 | 0 | 2 |
| P2 Straightforward | 4 | 0 | 4 |
| P3 Strengthening | 4 | 0 | 4 |
| P4 Page Budget | 1 | 0 | 1 |
| **Total** | **11** | **0** | **11** |

---

## Estimated Impact on Score

| Action | Current -> Expected (this reviewer) |
|--------|------|
| C1 multi-backbone done | 7 -> **7-8** |
| C1 + C2 controlled reversal fix | 7 -> **8** |
| All P1+P2 done | 7 -> **7-8** |
| All P1+P2+P3 done | 7 -> **8** (strong accept territory) |
| Page budget met (P4) | Required for submission regardless of score |
