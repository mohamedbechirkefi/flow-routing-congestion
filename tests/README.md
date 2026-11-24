<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# tests/

Run with `uv run pytest` (or `uv run flow test`). Pass counts are recorded in `progress.md` from real runs only.

| File | Content |
|---|---|
| `test_network.py` | Cost formulas, BPR parameterisation, invalid inputs |
| `test_paths.py` | Dijkstra against brute-force enumeration (property test with frequent ties), disconnected graphs, negative costs |
| `test_assignment.py` | Pigou and Braess golden values, flow conservation, nonnegativity, path/link consistency, SO lowest, convergence tolerances, Wardrop condition, MIX(0)=UE, MIX(1)=SO, FW versus MSA and gradient projection |
| `test_braess_interval.py` | Exact rational verification of the EXP-002 interval (80/31, 80/9) and engine agreement |
| `test_generators_metrics.py` | Grid generator determinism and structure, calibration, weighted quantile and Gini hand-computed values |
| `test_records.py` | Config to results integration, schema rejection, manifest, determinism, report and PDF, freeze guard |
