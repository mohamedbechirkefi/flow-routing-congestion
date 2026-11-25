<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-005: reproduction

- Revision `8dfc66ca5c9635e160f38526843941716aadacd0`. Results committed in `13d7c64`.
- Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`.
- Run, analysis and figure:

```
.venv/bin/flow run EXP-005
.venv/bin/python scripts/analyse_exp.py EXP-005 results/raw/EXP-005/EXP-005-20261124T234554Z-4051f409
```

- Raw results (committed, 8.7 MB): `results/raw/EXP-005/EXP-005-20261124T234554Z-4051f409/`

| File | sha256 |
|---|---|
| `results.json` | `ff47676a3cbd54dad23e69962acab3c19b258ecd54b1cfdbfa795c04ee0032da` |
| `metrics.csv` | `3461c5510d0691b8be8d797ff7092785c2da80af34ed4949763b47ddcc39a1e6` |
| `config.json` | `d2dc655102b64c0834a7b46eec84d1c18cde85fd5f24703764b279e930f7a73c` |
| `skipped_removals.json` | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |

- Expected: 5,154 ok records; 0 skipped; deterministic.
