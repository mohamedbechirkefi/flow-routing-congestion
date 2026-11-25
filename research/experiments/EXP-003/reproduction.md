<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-003: reproduction

- Revision `8dfc66ca5c9635e160f38526843941716aadacd0`. Results committed in `13d7c64`.
- Environment: `../.tools/py/bin/uv sync --frozen --all-groups --all-extras`. Versions: Python 3.12.1, numpy 2.5.4, matplotlib 3.11.2.
- Run, analysis and figures:

```
nice -n 10 .venv/bin/flow run EXP-003
.venv/bin/python scripts/analyse_exp.py EXP-003 results/raw/EXP-003/EXP-003-20261124T234531Z-6cbcaa47
```

  About 37 minutes in total; the Frank-Wolfe reference cell takes most of it.
- Raw results (committed, 4.4 MB): `results/raw/EXP-003/EXP-003-20261124T234531Z-6cbcaa47/`

| File | sha256 |
|---|---|
| `results.json` | `8b05b53be300205d26eff747f8adb9e42c0e5eb664ea040e52f8dbd3a069e7c4` |
| `metrics.csv` | `df97b4902a3c06cff25fe9a6951be852ae77e810dd035a5876f516580e0fde46` |
| `config.json` | `18a93abeb9fc10211b68bf177f47a167f596b79586bfb17b3f299cb0561ee740` |

- Expected:
  - 2,900 records: 2,745 ok and 155 nonconverged, all in the Frank-Wolfe reference cell.
  - Bootstrap: 10,000 resamples, seed 20261124. Values are deterministic, so they reproduce exactly.
