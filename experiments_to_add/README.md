# Experiments to Add — Pre-Submission Reviewer-Risk Mitigation

This folder collects the experiments that, based on three rounds of internal review, are still missing from the current paper draft and represent the highest reviewer-risk attack vectors.

Each `NN_*.md` file is a self-contained experiment spec: motivation (which review concern it addresses), research question, exact protocol, what to look for, integration plan, and estimated cost.

## Priority order (ROI-ranked)

| # | Experiment | Risk addressed | Cost | Must-do? |
|---|---|---|---|---|
| 01 | **Entropy quantile-normalization confound** | "Backbone reversal is a scale artifact, not a real reversal" | LOW (re-analysis of existing data) | **YES** — closes the single biggest attack vector |
| 02 | **Calibration-quality sweep on misaligned envs** | "Better calibration worsens performance" claim is currently inferred, not directly demonstrated | LOW–MED (one new variant, existing infra) | **YES** — turns the headline claim into a controlled experiment |
| 03 | **Sample-complexity sweep ($N_\text{explore}$)** | "Is 50 episodes enough? Does it generalize?" | LOW (sweep over existing pipeline) | **YES** — required to defend the deployment claim |
| 04 | **Alternative-explanation isolation** | "Reversal could be from rollout noise / reward bias / search depth, not two-source mixture" | MED (controlled ablations on rollout settings) | **SHOULD** — directly addresses the most persistent reviewer concern across 3 review rounds |
| 05 | **DIAL with $\Delta U$ regression head** | "DIAL is just logistic regression — where is the method contribution?" | HIGH (re-train + re-evaluate all 6 envs × 3 backbones) | **OPTIONAL** — only if deadline allows; lifts method-side novelty |

## Recommended execution order

1. **Day 1–2**: Run #01 (no new data, just re-analysis). If reversal survives quantile-normalization, the paper's central observation is bulletproofed.
2. **Day 3–5**: Run #02 (calibration sweep). Turns the abstract hook into a directly demonstrated experimental finding.
3. **Day 5–7**: Run #03 (sample complexity). Cheap, defends deployment story.
4. **Day 7–14**: Run #04 (alternative explanations). Most reviewer-defensive of the four.
5. **Optional, week 3+**: Run #05 (VOC regression). Substantive method upgrade if time permits.

## What to add to the paper after running

Each experiment file has an "Integration plan" section specifying which paper section gets the new table/figure and what one-paragraph summary to write. Do not over-expand — the paper is already 24 pages.

## Decision criteria for each experiment

- **#01**: If reversal disappears after quantile-normalization on >50% of cases → re-evaluate framing of backbone-reversal claim. If it persists → defends backbone reversal as substantive.
- **#02**: If "more calibration → worse SR on misaligned envs" is monotone → headline claim is bulletproofed. If non-monotone → soften the hook.
- **#03**: If SR plateaus by $N_\text{explore}{=}30$ → DIAL's deployment story is solid. If still climbing at 200 → rethink the "minimal" framing.
- **#04**: If two-source predictions hold under controlled rollout-noise / reward-bias variation → strengthens causal claim. If they collapse under one of these → must add caveat to §3.2.
- **#05**: If $\Delta U$ regression beats binary classifier by ≥2 pp → adopt as DIAL default. Otherwise drop quietly.

---

**Last updated**: 2026-04-25
**Owner**: zmli6 (liziming033@gmail.com)
