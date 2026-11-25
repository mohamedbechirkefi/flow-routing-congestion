# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""EXPLORATORY M4 confounder checks computed from committed confirmatory tables only.

No solver is run. Reads research/experiments/EXP-003/metrics.csv (committed copy of the
EXP-003 run's per-record table) and writes results/exploratory/M4-confounder-checks.json.
None of these numbers changes or replaces a frozen verdict; they were defined after the
confirmatory results were seen (M4, 2026-11-25) and are labelled exploratory.

Checks:
  1. Share of primary-cell instances (6x6, rho = 2) whose own R(UE) exceeds delta = 0.01,
     and the same in S2 (beta = 1) and S3 (absolute calibration): is the median driven by a
     subset of instances (OD sampling explanation)?
  2. Spearman rank correlation, in the primary cell, between per-instance R(UE) and the
     UE flow-weighted volume-to-capacity ratio and the UE share of links over capacity
     (does the excess track congestion, the mechanism named in the protocol?).
  3. The same share as in 1 for every grid size and demand level of the main matrix.
  4. EXP-005 (from the committed research/experiments/EXP-005/analysis.json, per_instance):
     how many instances have a single-link removal lowering TSTT_UE by more than 1e-2 and
     1e-3 relative, and the median relative effect over all flagged (1e-4) Braess links
     (are the Braess links practically material, judged against the study's delta?).

Usage: .venv/bin/python scripts/m4_exploratory_checks.py
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "research" / "experiments" / "EXP-003" / "metrics.csv"
OUT = ROOT / "results" / "exploratory" / "M4-confounder-checks.json"
DELTA = 0.01


def ranks(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    # average ties
    for v in np.unique(x):
        idx = np.where(x == v)[0]
        if len(idx) > 1:
            r[idx] = r[idx].mean()
    return r


def spearman(a, b) -> float:
    ra, rb = ranks(np.asarray(a, float)), ranks(np.asarray(b, float))
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> int:
    rows = list(csv.DictReader(SRC.open()))
    ue = defaultdict(dict)
    for r in rows:
        if r["arm"] != "UE" or r["status"] != "ok" or r["R"] == "":
            continue
        ue[(r["cell"], float(r["rho"]))][int(r["seed"])] = r
    out = {
        "label": "EXPLORATORY (M4, defined after the confirmatory results were seen; never changes a frozen verdict)",
        "source": str(SRC.relative_to(ROOT)),
        "source_run": rows[0]["record_id"].split("/")[0],
        "delta": DELTA,
        "share_instances_R_UE_above_delta": {},
    }
    for (cell, rho), recs in sorted(ue.items()):
        vals = np.array([float(r["R"]) for r in recs.values()])
        out["share_instances_R_UE_above_delta"][f"{cell} rho={rho:g}"] = {
            "n": int(len(vals)), "k_above": int((vals > DELTA).sum()), "min": float(vals.min()), "max": float(vals.max())}
    prim = ue[("grid6", 2.0)]
    seeds = sorted(prim)
    R = [float(prim[s]["R"]) for s in seeds]
    out["primary_cell_spearman"] = {
        "n": len(seeds),
        "R_UE_vs_flow_weighted_vc_UE": spearman(R, [float(prim[s]["flow_weighted_vc"]) for s in seeds]),
        "R_UE_vs_share_links_over_capacity_UE": spearman(R, [float(prim[s]["share_links_over_capacity"]) for s in seeds]),
        "R_UE_vs_max_vc_UE": spearman(R, [float(prim[s]["max_vc"]) for s in seeds]),
    }
    e5 = json.loads((ROOT / "research" / "experiments" / "EXP-005" / "analysis.json").read_text())
    usable = [p for p in e5["per_instance"] if p["usable"]]
    mx = [p["max_rel_decrease"] for p in usable]
    eff = [x for p in usable for x in p["effects_1e-4"].values()]
    out["exp005_materiality"] = {
        "source": "research/experiments/EXP-005/analysis.json (per_instance)",
        "n_instances": len(usable),
        "k_instances_max_rel_decrease_above_1e-2": int(sum(x > 1e-2 for x in mx)),
        "k_instances_max_rel_decrease_above_1e-3": int(sum(x > 1e-3 for x in mx)),
        "n_braess_links_1e-4": len(eff),
        "median_rel_effect_braess_links_1e-4": float(np.median(eff)),
        "k_braess_links_above_1e-2": int(sum(x > 1e-2 for x in eff)),
    }
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
