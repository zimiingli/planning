# Iteration 1: Related Work & Signal-Utility Landscape

## Targeted Sections
- `sections/related_work.tex`
- `sections/signal_utility_landscape.tex`

## Changes Made

### Related Work
1. **Added missing "fair comparison" sentence** for RL-based methods (guide line 265-267): "A fair comparison would require retraining each RL method per environment in our agent setting---a substantial engineering effort orthogonal to our contribution."

### Signal-Utility Landscape
2. **Added ecological fallacy reference** in theoretical grounding (guide line 551-553): Connected Simpson's paradox to the ecological fallacy in statistics for stronger theoretical framing.
3. **Expanded env-type-mapping table** with Rationale column (guide lines 518-535): Added a 5th column explaining the reasoning behind each environment's dominant type classification, matching the guide's richer table format.
4. **Enhanced Testable Prediction P1** wording (guide lines 620-625): Added parenthetical explanation "(the agent lacks information *but also faces many open paths*)" and "after information-gathering attempts" for richer intuition.
5. **Updated Design Implications table** column headers and content (guide lines 648-662): Changed abbreviated headers (Gran. -> Granularity, Env. -> Env-Aware, Prob. -> Problem) and added "(hand)"/"(auto)" qualifiers to Multi-signal rows.

## Rationale
These changes align the draft with the guide's recommendations for stronger theoretical framing and more informative tables. The ecological fallacy connection strengthens the paper's intellectual positioning, and the expanded table columns give reviewers immediate access to the reasoning behind each classification.
