# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""EXPLORATORY: apply the frozen EXP-001 / EXP-002 analyses unchanged to the 1e-10 reruns.

Owner, 2026-11-25, "Approve all recommendations, push then next" (item 3): EXP-001 and
EXP-002 are rerun at relative gap 1e-10 as a clearly labelled exploratory check that never
replaces the confirmatory verdict. This script calls flow.confirmatory.analyse_exp001 and
analyse_exp002 (frozen analysis code, unchanged since commit 5108a16) on the exploratory run
directories and writes exploratory_analysis.json into each. It computes nothing else.

Usage:
  .venv/bin/python scripts/analyse_exploratory_tol.py results/exploratory/X-EXP-001-TOL1E-10-<...> \
      results/exploratory/X-EXP-002-TOL1E-10-<...>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow import confirmatory as C  # noqa: E402
from flow.schema import clean_json, load_result  # noqa: E402

LABEL = ("EXPLORATORY (M4, owner item 3 of 2026-11-25b): frozen analysis applied to a rerun at "
         "relative gap 1e-10. Not a confirmatory result; the frozen verdict of the confirmatory run stands.")


def main(argv: list[str]) -> int:
    for arg in argv:
        run_dir = Path(arg)
        doc = load_result(run_dir / "results.json")
        exp = doc.get("experiment_id") or json.loads((run_dir / "config.json").read_text())["experiment_id"]
        if exp.startswith("X-EXP-001"):
            a = C.analyse_exp001(doc)
        elif exp.startswith("X-EXP-002"):
            a = C.analyse_exp002(doc)
        else:
            print(f"skip {run_dir}: not an EXP-001/EXP-002 tolerance rerun", file=sys.stderr)
            continue
        a["label"] = LABEL
        a["analysed_as"] = a["experiment_id"]
        a["experiment_id"] = exp
        a["run_dir"] = str(run_dir.relative_to(ROOT)) if run_dir.is_absolute() else str(run_dir)
        a["solver_rel_gap_max"] = max(r["solver"]["rel_gap"] for r in doc["records"] if r["solver"]["rel_gap"] is not None)
        a["solver_iterations_max"] = max(r["solver"]["iterations"] for r in doc["records"])
        out = run_dir / "exploratory_analysis.json"
        out.write_text(json.dumps(clean_json(a), indent=1, sort_keys=True) + "\n")
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
