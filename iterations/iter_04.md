# Iteration 4: Discussion & Conclusion

## Targeted Section
- `sections/discussion.tex`

## Changes Made

### Future Directions
1. **Added multi-agent coordination future direction** (guide lines 1349-1358): New paragraph on signal semantics implications for multi-agent systems where mismatched semantics between agents in different sub-environments could produce coordination failures. This is a compelling extension that broadens the paper's relevance.
2. **Expanded taxonomy future direction** (guide lines 1334-1336): Added concluding sentence about theory-guided prediction potentially replacing empirical direction discovery.
3. **Enriched adaptive exploration paragraph** (guide lines 1344-1347): Added concrete example ("search-based QA tasks have early-step critical windows") and explicit mention of maintaining direction discovery while reducing the budget.

### Limitations
4. **Strengthened backbone diversity limitation** (guide lines 1366-1377): Reframed as "stronger" finding, added explicit statement that fixed-direction methods fail across backbones too, and positioned EAAG as the only approach that can handle this unpredictability.
5. **Clarified model value description** (guide lines 1382-1383): Changed "explanatory and prescriptive" to include parenthetical explanations of each.
6. **Expanded exploration cost limitation** (guide line 1393-1394): Added note that re-exploration is also needed when the model backbone changes, connecting to multi-backbone findings.

### Broader Impact
7. **Added failure mode consequence** (guide lines 1404-1406): Added "a failure mode that wastes compute while degrading user experience" to make the practical impact more vivid.

## Rationale
The guide's design notes (lines 1288-1291) emphasize that Discussion should zoom out to community-level insights and present honest-but-not-self-defeating limitations. The multi-agent extension broadens appeal. The strengthened limitations convert potential weaknesses into reinforcement of the core argument (direction is unpredictable → adaptive learning is necessary).
