# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Exploratory calibration fits of protocol section 15.2 (C-BPR, C-S3, rho_SF).

No assignment (UE, SO, MIX) and no R is computed: only file columns, generator
draws on exploratory seeds 9000-9019 and free-flow all-or-nothing loading.
Writes aggregate values only to results/exploratory/calibration-2026-11-24.json.

Usage: ``.venv/bin/python scripts/calibrate.py`` (needs scripts/download_tntp.py first).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow.generators import make_grid, reference_demand_absolute, reference_demand_ff, reference_demand_ff_network  # noqa: E402
from flow.runner import load_tntp  # noqa: E402
from flow.tntp import build_demand, parse_net  # noqa: E402


def c_bpr() -> dict:
    tn = load_tntp("siouxfalls", ROOT)  # verifies SHA-256 against data/manifest.json
    cols = parse_net((ROOT / "data/raw/tntp/SiouxFalls/SiouxFalls_net.tntp").read_text())
    out = {}
    for col, key in (("b", "alpha"), ("power", "beta")):
        v = cols[col]
        uniq = sorted(set(float(x) for x in v))
        out[key] = {
            "n_links": int(v.size),
            "distinct_values": uniq,
            "rule": "constant" if len(uniq) == 1 else "median",
            "fitted": uniq[0] if len(uniq) == 1 else float(np.median(v)),
        }
    published = build_demand(list(tn.trips))
    dref = reference_demand_ff_network(tn.network, published)
    out["rho_sf"] = {"total_published_demand": published.total, "d_ref": dref, "rho": published.total / dref,
                     "note": "descriptive; FF all-or-nothing loading only"}
    return out


def c_s3() -> dict:
    seeds = list(range(9000, 9020))
    d_ff, cap = [], []
    for s in seeds:
        inst = make_grid(6, s)
        d_ff.append(2.0 * reference_demand_ff(inst))
        cap.append(reference_demand_absolute(inst, 1.0))  # share 1 -> summed origin capacity
    share = float(np.median(d_ff) / np.median(cap))
    return {
        "seeds": [seeds[0], seeds[-1]],
        "grid": "6x6, grid-v1, alpha 0.15, beta 4",
        "median_rho2_ff_demand": float(np.median(d_ff)),
        "median_origin_capacity": float(np.median(cap)),
        "share_raw": share,
        "fitted_share": float(f"{share:.6g}"),
    }


def main() -> int:
    res = {"journal": "J-0010 (C-BPR, rho_SF) and J-0011 (C-S3)", "label": "exploratory",
           "protocol_section": "15.2", "c_bpr": c_bpr(), "c_s3": c_s3()}
    out = ROOT / "results" / "exploratory" / "calibration-2026-11-24.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
