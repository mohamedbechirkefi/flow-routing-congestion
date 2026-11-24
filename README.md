<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW: navigation and collective congestion

**Question.** Can individually optimal routing worsen collective travel time?

**Status: M0 (bootstrap and feasibility), 2026-11-24. No experiment has run and there are no findings.** The study protocol is a draft awaiting the owner's freeze.

## Why it matters

When every traveller takes the route that is best for them, the result need not be best for everyone. The classic illustration is Braess's paradox, where adding a road makes every driver slower. FLOW measures this gap in small, controlled, fully reproducible simulations.

## What FLOW is and is not

- A small offline simulation study on synthetic networks: the Braess network and seeded grids with congestion-dependent travel times.
- Compares three routing rules: free-flow shortest paths (baseline), user equilibrium (individually optimal under congestion) and system optimum, plus partial compliance.
- **Not** a reconstruction of Google Maps or any navigation product, and **not** a prediction for any real city.

## What is implemented

Nothing yet beyond the control files, the draft protocol and the build scaffolding (M0). See `roadmap.md`.

## Research navigation

| Item | Path |
|---|---|
| Draft protocol | `research/protocol.md` |
| Feasibility audit | `research/feasibility.md` |
| Experiment registry | `research/experiment_registry.csv` |
| Experiment protocols | `research/experiments/EXP-001` to `EXP-005` |
| Literature notes | `research/literature_review.md` |
| Decisions | `research/decision_log.md` |
| Limitations | `research/limitations.md` |
| Manuscript (skeleton) | `research/paper/manuscript.md` |

| Experiment | Title | Status |
|---|---|---|
| EXP-001 | Analytic Braess example | planned (draft protocol) |
| EXP-002 | Braess demand sweep | planned (draft protocol) |
| EXP-003 | Grid collective excess (primary) | planned (draft protocol) |
| EXP-004 | Compliance and capacity sweep | planned (draft protocol) |
| EXP-005 | Single-link removal scan (optional) | planned (draft protocol) |

## Quick start (development)

Requires Python 3.12 and uv.

```sh
uv sync            # install locked dependencies from uv.lock
uv run pytest      # full test suite (synthetic fixtures only)
```

## Data

The primary study uses synthetic networks only. One real network, the TNTP Sioux Falls network (Transportation Networks for Research, https://github.com/bstabler/TransportationNetworks; "academic research purposes only"), is used locally for calibration and a second test. It is not included in this repository and is never redistributed: run `.venv/bin/python scripts/download_tntp.py` to fetch it from a pinned commit; the script checks the SHA-256 values in `data/manifest.json`.

## Licence

FLOW Source-Available Non-Commercial Research License v1.0 (`LicenseRef-FLOW-NC-Research-1.0`); see `LICENSE` and `NOTICE.md`. This is a custom source-available licence, not an OSI-approved open-source licence. Third-party dependencies keep their own licences.

## Citation

See `CITATION.cff`. Cite as an independent research project in progress; there is no paper yet.
