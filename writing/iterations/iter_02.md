# Iteration 2: Method Section

## Targeted Section
- `sections/method.tex`

## Changes Made

### "Why simplicity" paragraph expansion
1. **Extended the "Why the method is intentionally simple" paragraph** (guide lines 726-732): Added 4 sentences explaining the discovery-gate division of labor. The guide's version explicitly frames the architecture as "rich discovery + simple gate" and explains *why* training is fast (the gate doesn't need to compensate for missing direction information). This directly addresses potential reviewer concerns about method simplicity being a weakness.

## Rationale
The guide's design notes (lines 677-681) emphasize that this paper's contribution hierarchy is Finding > Theory > Method, following the pattern of NeurIPS best papers like "Are Emergent Abilities a Mirage?" where the method is deliberately simple because the insight is what matters. The expanded paragraph makes this explicit, preventing reviewers from perceiving simplicity as laziness rather than principled design.
