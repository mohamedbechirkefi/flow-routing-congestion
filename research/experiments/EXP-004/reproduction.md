<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-004: reproduction

- Revision `8dfc66ca5c9635e160f38526843941716aadacd0`. Results committed in `13d7c64`.
- Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`.
- Run, analysis and figure:

```
.venv/bin/flow run EXP-004
.venv/bin/python scripts/analyse_exp.py EXP-004 results/raw/EXP-004/EXP-004-20261125T002235Z-7a7c2692 --exp003 results/raw/EXP-003/EXP-003-20261124T234531Z-6cbcaa47
```

  The `--exp003` argument is used for the MIX(0) identity check.
- Raw results (committed, 3.5 MB): `results/raw/EXP-004/EXP-004-20261125T002235Z-7a7c2692/`

| File | sha256 |
|---|---|
| `results.json` | `83e5924ef8102ab1b4430c385f9ed8f2e8f9ffba0d88682f1415d21957975525` |
| `metrics.csv` | `ae68e1fc5b26b5cd255553ef8ff008ee3053432018258e805cbf9e1bd2566378` |
| `config.json` | `6d354fb2ae0e28db5d585e67f571c48d09b090f0f5d98d7985c87cbd995388d5` |

- Expected: 2,100 ok records; bootstrap seed 20261124; deterministic.
