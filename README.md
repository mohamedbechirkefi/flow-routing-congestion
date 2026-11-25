<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW: navigation and collective congestion

**Question.** Can individually optimal routing worsen collective travel time?

**Status (2026-11-25).** Preregistered simulation study. Protocol v1.0 was frozen by the owner on 2026-11-24; all six confirmatory experiments are complete and reported; the manuscript is a draft, not peer-reviewed. The owner approved the funding, competing-interest and AI-use statements on 2026-11-25; the owner's full-text review of the manuscript is pending (M6). Nothing has been published.

## Why it matters

When every traveller takes the route that is best for them, the result need not be best for everyone. The classic illustration is Braess's paradox, where adding a road makes every driver slower. FLOW measures this gap in small, controlled, fully reproducible simulations.

## What FLOW is and is not

- A small offline simulation study on synthetic networks (the Braess network and seeded grids), with one second test on the TNTP Sioux Falls network, used locally and not redistributed.
- Compares free-flow shortest-path routing (FF, baseline), user equilibrium (UE, individually optimal under congestion) and the system optimum (SO), plus partial system-optimal compliance MIX(c).
- **Not** a reconstruction of Google Maps or any navigation product, and **not** a prediction for any real city.

## Interactive page (M5)

![The Braess network explorer of the FLOW demo page: the network before and after adding link e at demand 6, with measured link flows, and below it the measured equilibrium mean trip time against demand with and without link e, the predicted paradox interval shaded.](docs/demo.png)

A static, offline page in `demo/`: an animated Braess network with a demand slider over the measured EXP-002 points, a routing-policy comparison, edge congestion, paired before and after charts, every published result with its interval, the assumptions, the method and limitations, and a sandbox that runs a port of the engine in a Web Worker. Measured results, exploratory checks, assumptions and sandbox output are labelled separately. Demo URL: [to be added on owner-approved release].

Demo quick start (FLOW uses plain static files and the repository's Python, no npm project):

```sh
.venv/bin/python scripts/build_demo.py                                       # checks the exports, writes demo/dist/
.venv/bin/python -m http.server --bind 127.0.0.1 --directory demo/dist 8000  # then open http://127.0.0.1:8000/
```

## Key findings (verified against committed results)

Every number below is printed as in `research/paper/manuscript.md`; each maps to a claim in `research/claims_register.csv`.

- **Primary (EXP-003).** On 100 seeded 6 by 6 grids with quartic (BPR) link costs, at twice the demand at which free-flow routing first saturates a link, the median excess of equilibrium over system-optimal total travel time was 0.02317 (95 percent bootstrap interval [0.02075, 0.02559]; one-sided lower bound 0.02134). The preregistered null hypothesis of an excess of at most 0.01 is rejected.
- **Scope limits.** The decision held at solver tolerances 1e-4 and 1e-8 and under an alternative demand calibration, but not with linear-in-flow costs (S2: median 0.00304, below the margin) or at light demand (rho = 1).
- **Baseline.** Free-flow routing was far worse than equilibrium routing under congestion (paired median R(FF) - R(UE) 0.2007, interval [0.1782, 0.2202]).
- **Compliance (EXP-004).** Routing more travellers system-optimally lowered the median excess at every step (H1 supported), in one operationalisation of partial compliance.
- **Braess links (EXP-005, optional).** 77 of 100 4 by 4 grid instances contain a link whose removal lowers equilibrium total travel time (Wilson 95 percent [0.678, 0.842]); most effects are small.
- **Real test network (EXP-006).** On Sioux Falls, which its maintainers do not consider realistic, the excess was 0.01453 at rho = 2, just above the margin.
- **Exact checks (EXP-001, EXP-002): contradicted.** Both failed their frozen 1e-6 rule, with residuals of 1e-5 to 6e-5 at the frozen solver tolerance. An exploratory rerun at relative gap 1e-10 met the rule (largest difference 7.53e-9); it is labelled exploratory and does not change the frozen verdicts.

## Research navigation

| Item | Path |
|---|---|
| Manuscript (canonical source) | `research/paper/manuscript.md` |
| Supplementary appendix | `research/paper/supplementary.md` |
| Frozen protocol | `research/protocol.md` (freeze record `research/freeze.json`) |
| Experiment registry | `research/experiment_registry.csv` |
| Experiment reports | `research/experiments/EXP-001/report.md` to `EXP-006/report.md` |
| Claims register | `research/claims_register.csv` |
| Artifact manifest and evidence audit | `research/publication/artifact_manifest.json`, `research/publication/evidence_audit.md` |
| Decisions | `research/decision_log.md` |
| Limitations | `research/limitations.md` |
| Demo page | `demo/` |

| Experiment | Title | Status | Verdict (frozen rule) |
|---|---|---|---|
| EXP-001 | Analytic Braess example | complete, confirmatory | Contradicted |
| EXP-002 | Braess demand sweep | complete, confirmatory | Contradicted |
| EXP-003 | Grid collective excess (primary) | complete, confirmatory | H0 rejected |
| EXP-004 | Compliance and capacity sweep | complete, confirmatory | H1 supported |
| EXP-005 | Single-link removal scan (optional) | complete, confirmatory | H1 supported |
| EXP-006 | Real-network second test (Sioux Falls) | complete, confirmatory | Gate passed; direction replicates |
| X-EXP-001/002-TOL1E-10 | Exact checks rerun at 1e-10 | exploratory | no verdict; frozen verdicts stand |

## Quick start (development)

Requires Python 3.12 and uv.

```sh
uv sync --frozen --all-groups   # install locked dependencies from uv.lock
uv run pytest                   # full test suite (synthetic fixtures only)
```

Demo tests use Node's built-in runner (no npm packages): `node --test demo/tests/*.test.mjs`.

## Full reproduction

Each experiment's `research/experiments/EXP-NNN/reproduction.md` gives its commands (`flow run EXP-NNN`, then `scripts/analyse_exp.py`). The demo data are regenerated from committed results by `scripts/export_demo_data.py` and `scripts/export_demo_sandbox.py`.

## Architecture

`src/flow/`: network and cost model, shortest paths, assignment (free flow, gradient projection, Frank-Wolfe reference, MIX(c)), generators, metrics, runner, records and CLI. `scripts/`: analyses, audits and exports. `demo/site/`: the static page (plain JavaScript; `engine.js` is a port of the solver, tested against a Python fixture).

## Data

The primary study uses synthetic networks only. One real network, the TNTP Sioux Falls network (Transportation Networks for Research, https://github.com/bstabler/TransportationNetworks; "academic research purposes only"), is used locally for calibration and a second test. It is not included in this repository and is never redistributed: run `.venv/bin/python scripts/download_tntp.py` to fetch it from a pinned commit; the script checks the SHA-256 values in `data/manifest.json`. The demo page contains no Sioux Falls data beyond published summary numbers.

## Limitations

Synthetic networks with 12 OD pairs; static deterministic assignment; quartic costs only (the effect falls below the margin with linear costs); congested demand only; a single solver implementation on grids; contradicted exact checks; exploratory values seen before the freeze (disclosed). Full list: `research/limitations.md`.

## Licence

FLOW Source-Available Non-Commercial Research License v1.0 (`LicenseRef-FLOW-NC-Research-1.0`); see `LICENSE` and `NOTICE.md`. This is a custom source-available licence, not an OSI-approved open-source licence. Third-party dependencies keep their own licences.

## Citation

See `CITATION.cff`. Cite as an independent research manuscript draft, not peer-reviewed. Repository URL: [to be added on owner-approved release].
