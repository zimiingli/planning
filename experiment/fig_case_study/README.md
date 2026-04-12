# fig_case_study

## Paper Location
experiments.tex, line ~442. Section 5.4 Robustness, after gate complexity ablation.

## Writing Prompt
> **[FIGURE NEEDED: Figure fig:case-study]**
> Trajectory-level gate decision visualization (ref: CoRefine Figure 4).
> Layout: Two horizontal trajectory strips: (a) HotpotQA (Type I), (b) APPS Interview (Type D).
> Each step = colored circle on timeline. Green = correct trigger, Gray = correct skip, Red = baseline harmful trigger.
> Circle size proportional to entropy. Entropy curve below, annotations above.
> Key message: Same high entropy -> opposite gate decisions -> EAAG adapts correctly in both cases.

## Data Status
- Qwen3-4B: **needs generate.py** — decision logs exist but need join with phase1_signal_data for per-step entropy
- Phi-3.5-mini: optional
- Llama-3.1-8B: optional

**Blocker:** Decision log has gate prob/decision per step, but NOT per-step entropy.
Need to reconstruct by joining decision_log.json (step, prob, decision) with
phase1_signal_data.json (step, token_entropy, utility). Complex join — needs generate.py.

## Raw Data Source
- Decision logs: `results/phase6/path_e/{env}/se_few5_filter_local/seed_*/scg_se_*_decision_log.json`
- Episodes: same path, `episodes.json`
- Need per-step: step_index, gate_decision, entropy, U_t, fixed_baseline_decision

## Files
- `data.csv` — TODO (selected episodes)
- `generate.py` — TODO
- `output.pdf` — TODO
