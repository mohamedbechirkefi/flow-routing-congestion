# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""EXPLORATORY planning summary for the owner before the freeze (M2).

Reads exploratory run directories (validated results.json only) and writes
results/exploratory/M2-planning-summary.{json,md}: runtime per solve, projected
full-matrix runtime, nonconvergence shares, seed spread of R in the 6x6 rho=2
cell, and FW versus gradient-projection differences. Not a finding.

Usage: uv run python scripts/m2_planning_summary.py <run_dir> [<run_dir> ...]
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from flow.analysis import percentile_interval
from flow.schema import load_result

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "exploratory"


def main(run_dirs: list[str]) -> None:
    docs = [load_result(Path(d) / "results.json") for d in run_dirs]
    for d in docs:
        assert d["label"] == "exploratory", "planning summary reads exploratory runs only"
    recs = [r for d in docs for r in d["records"]]

    # 1. runtime and convergence per (network size, rho, arm, algorithm)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in recs:
        f = r["factors"]
        size = f"grid{f['n']}" if "n" in f else ("braess+e" if f.get("with_link") else "braess")
        key = (size, f.get("rho", f.get("demand")), f.get("capacity_scale", 1.0), r["arm"], r["solver"]["algorithm"], r["solver"]["tol"])
        groups[key].append(r)
    timing = []
    for key, rs in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        rt = np.array([r["solver"]["runtime_s"] for r in rs])
        timing.append({
            "size": key[0], "level": key[1], "capacity_scale": key[2], "arm": key[3], "algorithm": key[4], "tol": key[5],
            "n": len(rs), "nonconverged": sum(r["status"] == "nonconverged" for r in rs),
            "failed": sum(r["status"] == "failed" for r in rs),
            "runtime_mean_s": float(rt.mean()), "runtime_max_s": float(rt.max()),
            "iterations_median": float(np.median([r["solver"]["iterations"] or 0 for r in rs])),
        })

    def mean_rt(size, arm, algo="frank-wolfe", level=None, tol=1e-6):
        sel = [t for t in timing if t["size"] == size and t["arm"] == arm and t["algorithm"] == algo and t["tol"] == tol
               and (level is None or t["level"] == level) and t["capacity_scale"] == 1.0]
        if not sel:
            return None
        return float(np.average([t["runtime_mean_s"] for t in sel], weights=[t["n"] for t in sel]))

    # 2. projection of the draft full matrix (protocol section 8) with the draft FW solver
    proj = []

    def add(name, count, per, basis):
        proj.append({"block": name, "solves": count, "mean_s_per_solve": per, "projected_s": None if per is None else count * per, "basis": basis})

    for n in (4, 6):
        for rho in (0.5, 1.0, 2.0, 3.0):
            for arm in ("UE", "SO"):
                add(f"EXP-003 grid{n} rho={rho} {arm}", 50, mean_rt(f"grid{n}", arm, level=rho), f"measured mean, X-TIMING-{n}x{n}")
    cap_rt = max(t["runtime_max_s"] for t in timing if t["size"] == "grid6" and t["algorithm"] == "frank-wolfe")
    add("EXP-003 S1 tol 1e-4 (UE, SO)", 100, mean_rt("grid6", "UE", level=2.0), "upper bound: 6x6 rho=2 mean at tol 1e-6")
    add("EXP-003 S1 tol 1e-8 (UE, SO)", 100, cap_rt, "assumption: every solve hits the 20,000 cap (max measured 6x6 FW runtime)")
    add("EXP-003 S2 beta=1 (UE, SO)", 100, mean_rt("grid6", "SO", level=2.0), "proxy: 6x6 rho=2 SO mean at beta=4 (not measured)")
    add("EXP-003 S3 absolute calibration (UE, SO)", 100, mean_rt("grid6", "SO", level=2.0), "proxy: 6x6 rho=2 SO mean (share not fixed)")
    mix = [t for t in timing if t["size"] == "grid6" and t["arm"].startswith("MIX") and t["arm"] not in ("MIX(1)",)]
    so_cap = [t for t in timing if t["size"] == "grid6" and t["arm"] == "SO" and t["level"] == 2.0 and t["algorithm"] == "frank-wolfe"]
    mix_rt = float(np.mean([t["runtime_mean_s"] for t in mix])) if mix else None
    so_rt = float(np.mean([t["runtime_mean_s"] for t in so_cap])) if so_cap else None
    add("EXP-004 MIX(c<1) follower solves", 50 * 3 * 4, mix_rt, "measured mean of MIX(0) and MIX(0.5), X-MIX-6x6")
    add("EXP-004 SO references", 50 * 3, so_rt, "measured 6x6 rho=2 SO mean")
    br = [t for t in timing if t["size"].startswith("braess") and t["algorithm"] == "frank-wolfe" and t["arm"] != "FF"]
    br_rt = float(np.mean([t["runtime_mean_s"] for t in br])) if br else None
    add("EXP-001/002 Braess UE+SO (about 2 x 2 x 66 demand values)", 264, br_rt, "measured mean, X-BRAESS-CONV (off-grid demands)")
    add("EXP-005 (optional) 4x4 UE, 48 removals + base", 50 * 49, mean_rt("grid4", "UE", level=2.0), "measured 4x4 rho=2 UE mean")
    total = sum(p["projected_s"] for p in proj if p["projected_s"] is not None)

    # 3. seed spread in the primary-cell analogue (6x6, rho=2, exploratory seeds)
    spread = {}
    for cell in sorted({r["cell"] for r in recs if r["factors"].get("n") == 6 and r["factors"].get("rho") == 2.0
                        and r["factors"].get("capacity_scale", 1.0) == 1.0 and not r["arm"].startswith("MIX")}):
        for arm in ("UE", "FF"):
            rs = [r for r in recs if r["cell"] == cell and r["arm"] == arm and r["factors"].get("rho") == 2.0]
            allR = [r["metrics"]["R"] for r in rs if r["metrics"] and r["metrics"].get("R") is not None]
            okR = [r["metrics"]["R"] for r in rs if r["status"] == "ok" and r["metrics"].get("R") is not None]
            if len(allR) < 3:
                continue
            v = np.array(allR)
            lo, hi = percentile_interval(v, resamples=10_000)
            spread[f"{cell}/{arm}"] = {
                "algorithm": rs[0]["solver"]["algorithm"], "tol": rs[0]["solver"]["tol"],
                "n_instances": len(v), "n_converged_own_arm": len(okR),
                "n_so_nonconverged": sum(1 for r in recs if r["cell"] == cell and r["arm"] == "SO" and r["factors"].get("rho") == 2.0 and r["status"] != "ok"),
                "median": float(np.median(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
                "q25": float(np.quantile(v, 0.25)), "q75": float(np.quantile(v, 0.75)), "min": float(v.min()), "max": float(v.max()),
                "boot95_median_width_at_n": float(hi - lo),
                "projected_width_at_n50": float((hi - lo) * np.sqrt(len(v) / 50)),
                "note": "all instances incl. nonconverged, for spread only",
            }

    # 4. FW versus GP on the same instances (R(UE) differences)
    def r_by_seed(cell, arm):
        return {r["seed"]: r["metrics"]["R"] for r in recs if r["cell"] == cell and r["arm"] == arm and r["metrics"] and r["metrics"].get("R") is not None}

    fw, gp = r_by_seed("grid6-rho2", "UE"), r_by_seed("grid6-rho2-gp-1e-8", "UE")
    common = sorted(set(fw) & set(gp))
    diff = {"n": len(common)}
    if common:
        d = np.array([fw[s] - gp[s] for s in common])
        diff.update(max_abs=float(np.abs(d).max()), median=float(np.median(d)))

    summary = {"label": "exploratory", "run_ids": [d["run_id"] for d in docs], "timing": timing, "projection": proj,
               "projected_total_s_single_core": total, "seed_spread": spread, "fw_minus_gp_R_UE": diff}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "M2-planning-summary.json").write_text(json.dumps(summary, indent=1) + "\n")

    L = ["<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->",
         "# M2 planning summary (EXPLORATORY, not a finding)", "",
         "Generated by `scripts/m2_planning_summary.py` from the exploratory runs: " + ", ".join(f"`{d['run_id']}`" for d in docs) + ".",
         "Exploratory seeds 9000-9019 only. Purpose: runtime, convergence, seed spread and degenerate cells for the owner's freeze decision.", "",
         "## Runtime and convergence per solve", "",
         "| Network | Level | Cap. scale | Arm | Algorithm | tol | n | nonconv. | failed | mean s | max s | median iter. |", "|" + "---|" * 12]
    for t in timing:
        L.append(f"| {t['size']} | {t['level']} | {t['capacity_scale']} | {t['arm']} | {t['algorithm']} | {t['tol']} | {t['n']} | {t['nonconverged']} | {t['failed']} | {t['runtime_mean_s']:.3f} | {t['runtime_max_s']:.3f} | {t['iterations_median']:.0f} |")
    L += ["", "## Projected runtime of the draft full matrix (single core, Frank-Wolfe as drafted)", "",
          "| Block | Solves | mean s per solve | projected s | basis |", "|---|---|---|---|---|"]
    for p in proj:
        ps = "n/a" if p["projected_s"] is None else f"{p['projected_s']:.0f}"
        ms = "n/a" if p["mean_s_per_solve"] is None else f"{p['mean_s_per_solve']:.3f}"
        L.append(f"| {p['block']} | {p['solves']} | {ms} | {ps} | {p['basis']} |")
    L += ["", f"Projected total: {total:.0f} s ({total / 3600:.2f} h) on one core.", "",
          "## Seed spread of R, 6x6 grids at rho = 2 (exploratory seeds)", "",
          "| Cell/arm | algorithm | tol | n | SO nonconv. | median | mean | SD | IQR | min to max | 95% bootstrap width of median at n | projected width at n=50 |", "|" + "---|" * 12]
    for k, s in spread.items():
        L.append(f"| {k} | {s['algorithm']} | {s['tol']} | {s['n_instances']} | {s['n_so_nonconverged']} | {s['median']:.5f} | {s['mean']:.5f} | {s['sd']:.5f} | {s['q25']:.5f} to {s['q75']:.5f} | {s['min']:.5f} to {s['max']:.5f} | {s['boot95_median_width_at_n']:.5f} | {s['projected_width_at_n50']:.5f} |")
    L += ["", f"FW (tol 1e-6) minus GP (tol 1e-8) in R(UE), same instances: {json.dumps(diff)}.", ""]
    (OUT / "M2-planning-summary.md").write_text("\n".join(L))
    print(OUT / "M2-planning-summary.md")


if __name__ == "__main__":
    main(sys.argv[1:])
