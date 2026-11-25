<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-006: reproduction

- Revision `8dfc66ca5c9635e160f38526843941716aadacd0`. Results committed in `13d7c64`, except `results.json`.
- Data, local only and never committed:

```
.venv/bin/python scripts/download_tntp.py
```

  The script checks each file's SHA-256 against `data/manifest.json` (sha256 `81470760...e104`). Licence: academic research purposes only.
- Run, analysis and figure:

```
.venv/bin/flow run EXP-006
.venv/bin/python scripts/analyse_exp.py EXP-006 results/raw/EXP-006/EXP-006-20261124T234536Z-9a9669c8
```

- Raw results: `results/raw/EXP-006/EXP-006-20261124T234536Z-9a9669c8/`

| File | sha256 | Committed |
|---|---|---|
| `results.json` | `3d2ae0c28a3f9c34edc9887be3f5d86510c931a37cc73a5a3a71a821b6e934d8` | no (TNTP-derived per-link flows) |
| `metrics.csv` | `814b210b2b0619d3a8936a2e570c971abc4ce4d6e61c68c9d542333e3f9f0a58` | yes |
| `config.json` | `8565a0049174f5e8200838f7967fc1a7902498622b2b05234c15ce3d64e9239b` | yes |

- Expected: 16 ok records; gate value 1.28e-4; deterministic.
