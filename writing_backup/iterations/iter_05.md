# Iteration 5: Appendix + Final Polish & Compile

## Targeted Sections
- `sections/appendix.tex`
- `main.tex`
- Build system fixes

## Changes Made

### Appendix A: Extended Related Work
1. **Added "Adaptive Compute: From Reasoning to Agent Settings" subsection** (guide lines 1456-1468): New opening subsection framing the two settings (reasoning vs agent) and positioning our work as first to question fixed-direction assumption in either.
2. **Added "Concurrent Work Statement (Extended)" subsection** (guide lines 1486-1494): Timeline-based concurrent work statement with specific submission dates (Feb 2026, May 2025, Oct 2025) and explicit statement of our distinct contribution.
3. **Reorganized Detailed Method Comparison** with proper subsection label.

### Appendix C: Proofs
4. **Added "Wrong-Direction Damage Quantification" subsection** (guide lines 1637-1656): New table with Correct SR, Wrong SR, ΔSR, and |ρ| for 4 environments. Includes analysis that damage scales with signal strength (R² > 0.5) and the key finding that MLP with wrong direction is worse than logistic with wrong direction.

### Appendix D: Two-Source Model
5. **Expanded section title** to "Full Derivation and Verification" (guide line 1689).

### Build System
6. **Fixed double bibliographystyle conflict**: Removed explicit `\bibliographystyle{template/acl_natbib}` from main.tex since acl.sty already sets it internally.
7. **Fixed bst file path**: Copied acl_natbib.bst to working directory for bibtex discovery.
8. **Full 3-pass compilation verified**: pdflatex → bibtex → pdflatex × 2 = 15 pages, no errors.

### Remaining Warnings (Expected)
- Undefined references for `fig:method`, `fig:feature-heatmap`, `fig:auc-hierarchy`, `tab:main`, `tab:winloss` — these require actual experimental figures/tables to be inserted.

## Rationale
The appendix is the reviewer's depth resource. Adding the wrong-direction damage table provides quantitative evidence for Proposition 1. The concurrent work timeline preempts "lack of novelty" concerns. Build fixes ensure the paper compiles cleanly with the official ACL/EMNLP template.
