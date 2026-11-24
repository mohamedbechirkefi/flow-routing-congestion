# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Metric validation on known cases (M3 brief), from an EXPLORATORY smoke run directory.

Checks, from results.json only: the Braess d = 6 cell against the analytic values
(flow.confirmatory.analyse_exp001, same code as EXP-001); TSTT = sum_e x_e t_e(x_e)
recomputed from the recorded link flows; mean trip time = TSTT / demand; for UE
with all paths equal, p95 = max = mean; R(SO) = 0; R(UE) and R(FF) >= 0 within
solver tolerance; flow conservation on every record. Prints a JSON summary.

Usage: .venv/bin/python scripts/validate_metrics.py <smoke run dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow.confirmatory import analyse_exp001  # noqa: E402
from flow.generators import braess_network  # noqa: E402
from flow.schema import load_result  # noqa: E402


def main(run_dir: str) -> int:
    doc = load_result(Path(run_dir) / "results.json")
    recs = doc["records"]
    braess = [r for r in recs if r["cell"] == "braess-d6"]
    out = {"run_id": doc["run_id"], "label": doc["label"], "checks": {}}
    a = analyse_exp001({"records": braess})
    out["checks"]["braess_analytic"] = {"verdict": a["verdict"], "max_abs_diff": a["max_abs_diff"]}
    errs = []
    for r in braess:
        net = braess_network(bool(r["factors"]["with_link"]))
        x = np.array(r["metrics"]["link_flow"])
        tstt = float(np.dot(x, net.link_time(x)))
        errs.append(abs(tstt - r["metrics"]["tstt"]))
        errs.append(abs(r["metrics"]["mean_trip_time"] - r["metrics"]["tstt"] / 6.0))
        if r["arm"] == "UE":
            errs.append(abs(r["metrics"]["p95_trip_time"] - r["metrics"]["mean_trip_time"]))
    out["checks"]["tstt_and_mean_recomputed_max_abs_err"] = max(errs)
    ok = [r for r in recs if r["status"] == "ok"]
    out["checks"]["R_SO_max_abs"] = max(abs(r["metrics"]["R"]) for r in ok if r["arm"] == "SO")
    out["checks"]["R_min_UE_FF"] = min(r["metrics"]["R"] for r in ok if r["arm"] in ("UE", "FF"))
    out["checks"]["max_node_imbalance"] = max(r["metrics"]["max_node_imbalance"] for r in ok)
    out["status_counts"] = {s: sum(r["status"] == s for r in recs) for s in ("ok", "nonconverged", "failed")}
    passed = (a["verdict"] == "reproduced" and out["checks"]["tstt_and_mean_recomputed_max_abs_err"] < 1e-9
              and out["checks"]["R_SO_max_abs"] == 0.0 and out["checks"]["R_min_UE_FF"] > -1e-5
              and out["checks"]["max_node_imbalance"] < 1e-6)
    out["pass"] = passed
    print(json.dumps(out, indent=1))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
