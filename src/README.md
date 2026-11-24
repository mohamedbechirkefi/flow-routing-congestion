<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# src/

`src/flow/` is the Python package (M2). Layers are kept separate:

| Module | Role |
|---|---|
| `network.py` | Directed graph, unified polynomial cost model `t(x) = A + B x^P` (linear Braess costs and BPR), OD demand, explicit error types |
| `paths.py` | Dijkstra with the protocol tie-breaking rule, brute-force path enumeration (test reference), all-or-nothing loading |
| `generators.py` | Braess network; seeded grid generator `grid-v1`; FF and absolute demand calibration (ingestion of synthetic inputs) |
| `assignment.py` | Arms: FF (baseline), UE and SO by Frank-Wolfe, MIX(c), MSA reference; candidate path-based gradient projection (not in the draft protocol) |
| `metrics.py` | TSTT, mean and p95 trip time, congestion, Gini of stretch, node balance |
| `analysis.py` | Percentile bootstrap over instances (protocol section 6) |
| `runner.py` | Config validation, freeze guard, exploratory-seed guard, run execution, run manifest, metrics CSV |
| `schema.py`, `schemas/result-1.0.0.json` | Versioned JSON result schema, validated at export and import |
| `report.py` | Tables and figures from `results.json`; PDF via pandoc to Typst |
| `cli.py` | `flow smoke`, `flow run`, `flow report`, `flow test` |
