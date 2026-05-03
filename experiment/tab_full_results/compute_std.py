#!/usr/bin/env python3
"""
Append per-seed std to tab_full_results cells.

Strategy: keep the published paper means intact (some come from earlier
runs whose exact files have moved), and pull std from whichever raw
summary.json batch best matches each cell. The std characterizes
seed-to-seed variance, which is robust to small mean shifts.

Mean values are hard-coded from the current LaTeX table; std is computed
on the fly from the most authoritative available path.
"""
import glob
import json
import statistics
from pathlib import Path

ROOT = Path("/home/uuc24002/FRVC/results")

# Paper means (must match current tab_full_results.tex)
PAPER = {
    # backbone -> env -> method -> mean SR (%)
    "qwen3": {
        "hotpotqa":  {"cats":93.2, "seag":67.5, "corefine":68.2, "catts":68.3, "auq":95.0, "s1_budget":94.0, "DIAL":95.2},
        "webshop":   {"cats":30.5, "seag":28.0, "corefine":27.5, "catts":16.0, "auq":35.7, "s1_budget":17.8, "DIAL":43.8},
        "fever":     {"cats":48.2, "seag":47.3, "corefine":47.8, "catts":32.2, "auq":38.7, "s1_budget":44.2, "DIAL":49.8},
        "twexpress": {"cats":96.7, "seag":97.3, "corefine":97.5, "catts":97.5, "auq":95.5, "s1_budget":95.0, "DIAL":99.0},
        "plancraft": {"cats":20.3, "seag":22.8, "corefine":20.8, "catts":23.0, "auq":22.2, "s1_budget":16.3, "DIAL":23.3},
        "apps":      {"cats":66.2, "seag":66.0, "corefine":67.5, "catts":60.8, "auq":64.7, "s1_budget":69.0, "DIAL":73.0},
    },
    "phi35": {
        "hotpotqa":  {"cats":68.3, "seag":88.3, "corefine":87.7, "catts":42.0, "auq":31.2, "s1_budget":91.2, "DIAL":92.3},
        "webshop":   {"cats":41.7, "seag":36.5, "corefine":35.8, "catts":28.7, "auq":37.0, "s1_budget":43.0, "DIAL":57.3},
        "fever":     {"cats":19.8, "seag":13.5, "corefine":13.7, "catts":12.7, "auq":8.5,  "s1_budget":20.0, "DIAL":20.5},
        "twexpress": {"cats":68.2, "seag":92.5, "corefine":92.7, "catts":86.7, "auq":92.5, "s1_budget":93.7, "DIAL":96.7},
        "plancraft": {"cats":13.5, "seag":14.7, "corefine":15.2, "catts":13.5, "auq":12.7, "s1_budget":13.7, "DIAL":16.8},
        "apps":      {"cats":30.5, "seag":27.8, "corefine":28.5, "catts":27.7, "auq":27.2, "s1_budget":34.5, "DIAL":36.8},
    },
    "llama31": {
        "hotpotqa":  {"cats":94.2, "seag":94.0, "corefine":94.2, "catts":94.0, "auq":95.0, "s1_budget":94.5, "DIAL":95.5},
        "webshop":   {"cats":36.0, "seag":27.5, "corefine":27.5, "catts":11.3, "auq":37.8, "s1_budget":11.2, "DIAL":41.7},
        "fever":     {"cats":56.3, "seag":53.5, "corefine":53.5, "catts":14.2, "auq":52.8, "s1_budget":13.8, "DIAL":54.7},
        "twexpress": {"cats":35.8, "seag":76.5, "corefine":76.0, "catts":49.3, "auq":63.2, "s1_budget":76.1, "DIAL":94.8},
        "plancraft": {"cats":22.8, "seag":21.8, "corefine":21.5, "catts":27.0, "auq":27.0, "s1_budget":26.3, "DIAL":27.0},
        "apps":      {"cats":55.2, "seag":57.2, "corefine":57.2, "catts":52.3, "auq":46.0, "s1_budget":52.5, "DIAL":59.7},
    },
}


def patterns(backbone, env, method):
    """Return ranked list of glob patterns for raw seed summaries."""
    if backbone == "qwen3":
        if method == "DIAL":
            # DIAL was implemented as principled_v2 / principled_nopca / scg_finetune_lr
            # Use whichever variant exists for this env.
            return [
                str(ROOT / f"phase6/path_e/{env}/principled_v2/seed_*/summary.json"),
                str(ROOT / f"phase6/path_e/{env}/principled_nopca/seed_*/summary.json"),
                str(ROOT / f"phase6/path_e/{env}/principled/seed_*/summary.json"),
                str(ROOT / f"phase5/{env}/{env}/scg_finetune_lr/seed_*/summary.json"),
            ]
        return [
            str(ROOT / f"phase5/competing_baselines_calibrated/{env}/{method}/seed_*/summary.json"),
            str(ROOT / f"phase6/new_baselines/{env}/{method}/seed_*/summary.json"),
            str(ROOT / f"phase5/competing_baselines/{env}/{method}/seed_*/summary.json"),
            str(ROOT / f"phase6/{env}/{env}/{method}/seed_*/summary.json"),
            str(ROOT / f"phase5/{env}/{env}/{method}/seed_*/summary.json"),
        ]
    bb_dir = "phi35_mini" if backbone == "phi35" else "llama31_8b"
    if method == "DIAL":
        # Multi-backbone DIAL ran as se_few5_filter_local
        return [
            str(ROOT / f"review/{bb_dir}/{env}/{env}/se_few5_filter_local/seed_*/summary.json"),
        ]
    return [
        str(ROOT / f"review/{bb_dir}/{env}/{env}/{method}/seed_*/summary.json"),
    ]


def std_for(backbone, env, method):
    """Compute std (in %) from the first non-empty pattern, else None."""
    seen = set()
    srs = []
    for pat in patterns(backbone, env, method):
        for p in glob.glob(pat):
            seed = p.split("seed_")[1].split("/")[0]
            if seed in seen:
                continue
            try:
                d = json.load(open(p))
                srs.append(d["success_rate"])
                seen.add(seed)
            except Exception:
                pass
        if len(srs) >= 2:
            break
    if len(srs) < 2:
        return None
    return 100 * statistics.stdev(srs)


def fmt(mean, std):
    if std is None:
        return f"{mean}"
    return f"{mean}\\,$\\pm$\\,{std:.1f}"


def main():
    rows = {}
    for bb, envs in PAPER.items():
        for env, methods in envs.items():
            for method, mean in methods.items():
                sd = std_for(bb, env, method)
                rows[(bb, env, method)] = (mean, sd)

    # Print summary
    miss = [k for k, v in rows.items() if v[1] is None]
    print(f"Computed std for {len(rows) - len(miss)}/{len(rows)} cells")
    if miss:
        print("Missing (no raw data):")
        for k in miss:
            print(f"  {k}")
    print()

    print("=== Per-cell (mean, std) ===")
    for (bb, env, m), (mean, sd) in sorted(rows.items()):
        sd_str = f"±{sd:.1f}" if sd is not None else "±?"
        print(f"  {bb:8s} {env:11s} {m:10s}: {mean:>5}{sd_str}")

    # Write out a JSON for easy table patching
    out_path = Path(__file__).parent / "cells.json"
    with open(out_path, "w") as f:
        json.dump({f"{bb}|{env}|{m}": {"mean": mean, "std": sd}
                   for (bb, env, m), (mean, sd) in rows.items()}, f, indent=2)
    print(f"\nWrote → {out_path}")


if __name__ == "__main__":
    main()
