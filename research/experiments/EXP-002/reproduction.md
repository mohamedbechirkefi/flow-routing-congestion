<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-002: reproduction

- Revision `8dfc66ca5c9635e160f38526843941716aadacd0`. Results committed in `13d7c64`.
- Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`. Versions: Python 3.12.1, numpy 2.5.4, matplotlib 3.11.2.
- Run, analysis and figure:

```
.venv/bin/flow run EXP-002
.venv/bin/python scripts/analyse_exp.py EXP-002 results/raw/EXP-002/EXP-002-20261124T234533Z-fcb88932
```

  The second command writes `analysis.json` and `figures/exp002_sweep.png`.
- Raw results (committed, 624 KB): `results/raw/EXP-002/EXP-002-20261124T234533Z-fcb88932/`

| File | sha256 |
|---|---|
| `results.json` | `697f1a954b73abbdf410473ee8bc7bce93477746851dd36c613221a3c645836c` |
| `metrics.csv` | `97c143c1fb60c424ed90a8103a2e6a57e94b2eb496b9401a6c018cc230e00fe6` |
| `config.json` | `79b8ea46587cad131ce41fcc89e0510d94c8be727e1f1aba85c9e3981a186bb7` |

- Expected: 450 records, schema `flow.result/1.0.0`, deterministic values.
