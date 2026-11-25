<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-001: reproduction

- Revision: `8dfc66ca5c9635e160f38526843941716aadacd0`. Results committed in `13d7c64`.
- Environment:

```
../.tools/py/bin/uv sync --frozen --all-groups --all-extras
.venv/bin/python -m pytest -q    # 138 passed at 2026-11-25
```

  Versions: Python 3.12.1, numpy 2.5.4, matplotlib 3.11.2, typst 0.15.2.
- Run and analysis:

```
.venv/bin/flow run EXP-001
.venv/bin/python scripts/analyse_exp.py EXP-001 results/raw/EXP-001/EXP-001-20261124T234532Z-846e8c0f
```

- Raw results (committed): `results/raw/EXP-001/EXP-001-20261124T234532Z-846e8c0f/`

| File | sha256 |
|---|---|
| `results.json` | `4d0d2731e8c3b6d126d31bf77755f212b9a51699e951c071be90691b40d60351` |
| `metrics.csv` | `a61e64e1517fb7a2c7782ae71a2161185e09fb2849592a2d57fc0a2636cdc84a` |
| `config.json` | `2d370c89c9775c921125dd9bc2eb29ba7c5b7d30514b15b75ae5d9de9766359a` |

  All raw-file hashes are also in `results/M3-raw-manifest.json`.
- Copies in this folder: `config.json`, `run_manifest.json`, `metrics.csv`, `analysis.json`.
- Expected: schema `flow.result/1.0.0`; 6 records; tolerance 1e-6 absolute (D-012). The run is deterministic, so a rerun gives identical values.
