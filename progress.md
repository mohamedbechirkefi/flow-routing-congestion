<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Progress journal (append-only)

## 2026-11-24: Session 1 (M0, plus M1 drafts)

**Milestone.** M0 bootstrap and feasibility; M1 drafts (protocols, registry, manuscript skeleton). Nothing frozen. No experiment run.

### Starting state

`git status` before work: `On branch main`, `nothing to commit, working tree clean`. One commit `c92d878` (master prompt and the owner's licence package).

### Commands and actual outputs

- `sysctl -n machdep.cpu.brand_string hw.ncpu hw.memsize` -> `Apple M1 Pro`, `10`, `17179869184`.
- `sysctl -n hw.physicalcpu hw.perflevel0.physicalcpu hw.perflevel1.physicalcpu` -> `10`, `8`, `2`.
- `sw_vers` -> `ProductName: macOS`, `ProductVersion: 15.3.1`, `BuildVersion: 24D70`.
- `df -h /Users/bechir/research/labs` -> `/dev/disk3s1 460Gi 311Gi 128Gi 71%`.
- `/usr/local/bin/python3 --version` -> `Python 3.12.1`.
- `.tools/py/bin/uv --version` -> `uv 0.9.5 (d5f39331a 2025-10-21)`.
- `.tools/py/bin/typst --version` -> `no such file or directory` (there is no typst CLI; the typst **Python package** is installed). `importlib.metadata.version('typst')` -> `0.15.0`. pypdf `6.20.0`, pillow `11.3.0`.
- `.tools/pandoc --version` -> `pandoc 3.6.3`.
- `/Users/bechir/research/helix/.tools/node/bin/node --version` -> `v22.23.3` (read-only use).
- `git --version` -> `git version 2.42.1`.
- `which tex pdflatex xelatex` -> `tex not found`, `pdflatex not found`, `xelatex not found`.
- Toolchain smoke (exploratory, in a scratch directory outside the repository, journal J-0001): pandoc Markdown to Typst exit 0; first `typst.compile` failed with `typst.TypstError: font fallback list must not be empty`; with `-V mainfont="New Computer Modern"` it compiled a 1-page PDF whose extracted text matched the input.
- `uv lock` -> `Using CPython 3.12.1 interpreter at: /Library/Frameworks/Python.framework/Versions/3.12/bin/python3`, `Resolved 20 packages in 300ms`. Locked: numpy 2.5.4, pytest 9.2.0, hypothesis 6.170.15, matplotlib 3.11.2, typst 0.15.2 (with `exclude-newer = 2026-11-10`).
- `pandoc research/paper/manuscript.md -s -t latex` via `scripts/build_manuscript_tex.sh` -> exit 0, `manuscript.tex` written (skeleton only, not compiled; no TeX).
- Literature and data: Crossref API metadata for 12 DOIs; fetched and read the Braess translation PDF (author-hosted), the Roughgarden-Tardos preprint (abstract and introduction), the supernet Braess page, the arXiv abstract of Youn et al.; checked TNTP repository licence (GitHub API `license: null`). Publisher pages for INFORMS and ACM returned HTTP 403. Details in `research/literature_review.md` and `data/manifest.json`.

### Decisions

D-001 licence (owner), D-002 toolchain, D-003 synthetic-only data, D-004 draft primary contrast, D-005 dependency age rule. See `research/decision_log.md`.

### Files created

`CLAUDE.md`, `README.md`, `CITATION.cff`, `roadmap.md`, `progress.md`, `pyproject.toml`, `uv.lock`, `src/flow/__init__.py`, `scripts/build_manuscript_tex.sh`, `research/{decision_log,literature_review,feasibility,protocol,limitations}.md`, `research/{claims_register,experiment_registry}.csv`, `research/experiment_journal.jsonl`, `research/experiments/EXP-001..005/protocol.md`, `research/paper/{manuscript.md,manuscript.tex,references.bib,supplementary.md,figures/README.md}`, `research/publication/{artifact_manifest.json,claims_audit.md,reproducibility_report.md,author_review.md,release_checklist.md}`, `data/manifest.json`, README files in `results/`, `src/`, `tests/`, `experiments/`, `demo/`, `articles/`. Appended section 6 (development commands) to `CONTRIBUTING.md`.

### Not done, and why

- No tests and no engine code: M2 work; the test suite was not run because no tests exist.
- No PDFs of the manuscript or reports: no content to compile yet; the toolchain is only smoke-tested.
- Full texts of Wardrop, Beckmann, Sheffi, Steinberg-Zangwill, Valiant-Roughgarden, Roughgarden 2004 and Harker not read (metadata only). BPR primary source not found.
- The EXP-002 paradox interval `(80/31, 80/9)` is a hand derivation by the assistant, not yet verified by code or a source.

### Outstanding risks

Frank-Wolfe convergence (S1), MIX(c) definition and convergence, demand calibration artefacts (S3), demo scope. See `research/feasibility.md` section 8.

### Next action

Owner: review and decide B1 to B5 in `roadmap.md`. Assistant (allowed before the freeze): M2 implementation and tests, smoke matrix on exploratory seeds 9000-9019 only, M1 reading list.

## 2026-11-24: Session 2 (M2 core implementation; protocol still unfrozen)

**Milestone.** M2. The protocol is not frozen (no FREEZE record); every run this session is EXPLORATORY on seeds 9000-9019. No confirmatory run, no push, no paid service, no download.

### Starting state

`git status`: `On branch main`, `nothing to commit, working tree clean`; HEAD `3407251`.

### Implemented

- `src/flow/`: `network.py` (graph, unified cost model, demand, explicit errors), `paths.py` (Dijkstra with the protocol tie rule, brute-force enumeration, all-or-nothing), `generators.py` (Braess, grid `grid-v1`, FF and absolute calibration), `assignment.py` (FF, UE and SO by Frank-Wolfe with exact line search and path-flow tracking, MIX(c), MSA reference, candidate gradient projection), `metrics.py`, `analysis.py` (bootstrap), `schema.py` with `schemas/result-1.0.0.json`, `runner.py` (config validation, freeze guard, exploratory-seed guard, run manifest, metrics CSV), `report.py` (tables, figures, PDF), `cli.py` (`flow smoke | run | report | test`). Decisions D-006 to D-009.
- `experiments/EXP-001.json` to `EXP-004.json` (confirmatory, refused until freeze; EXP-003 without S3), `experiments/exploratory/*.json` (6 planning configs).
- `scripts/m2_planning_summary.py`; `research/protocol_amendment_proposals.md` (A1-A8, proposals only).
- `pyproject.toml`: console script `flow`; `uv lock` -> `Resolved 20 packages in 4ms` (lockfile unchanged). `.gitignore`: `.hypothesis/`, `.pytest_cache/`.

### Commands and actual outputs

- `uv sync --all-groups` -> installed numpy 2.5.4, pytest 9.2.0, hypothesis 6.170.15, matplotlib 3.11.2, typst 0.15.2 and dependencies.
- Test runs (all real): first run `-x`: `1 failed, 34 passed` (FW-SO versus GP equality too strict; GP had the lower TSTT, FW-SO had not reached 1e-8). Second run: `4 failed, 93 passed in 324.90s` (same FW stalling at tight tolerances on 3x3 and on Braess d = 9 and 11, plus a wrong test assumption that a 2x2 grid has fewer than 12 OD candidates). Tests were corrected to check convexity bounds and explicit nonconvergence flags instead of exact equality; then `1 failed, 96 passed` (Braess d = 8.8, near the corner, also stalls). **Final run after all code changes: `97 passed in 93.38s`, 0 failed.**
- `flow run EXP-003` -> `REFUSED: refusing confirmatory run of EXP-003: no FREEZE record for research/protocol.md in research/decision_log.md (protocol not frozen; G-FREEZE)`, exit 3.
- Exploratory runs (sequential, one process each, log `results/exploratory/session-M2-runs.log`), all exit 0:

| Journal | Run id | Wall s | Records ok / nonconverged / failed |
|---|---|---|---|
| J-0002 | SMOKE-20261124T161549Z-94d06582 | 11.3 | 25 / 1 / 0 |
| J-0003 | X-BRAESS-CONV-20261124T161601Z-8fdc44d6 | 49.8 | 46 / 8 / 0 |
| J-0004 | X-SPREAD-6x6-GP-20261124T161651Z-e2c25681 | 1.5 | 100 / 0 / 0 |
| J-0005 | X-MIX-6x6-20261124T161652Z-702080f8 | 226.7 | 4 / 32 / 0 |
| J-0006 | X-TIMING-4x4-20261124T162039Z-2bce20f0 | 334.0 | 86 / 34 / 0 |
| J-0007 | X-TIMING-6x6-20261124T162613Z-5f27dc7d | 223.9 | 43 / 17 / 0 |
| J-0008 | X-SPREAD-6x6-FW-20261124T162957Z-d64cb70a | 382.5 | 32 / 28 / 0 |

  Peak RSS 32 to 35 MiB per run. Manifests record git revision `3407251` with `dirty: true`: the runs used the uncommitted M2 working tree. The engine files used by the runs (`network.py`, `paths.py`, `assignment.py`, `generators.py`, `metrics.py`, `runner.py`, `schema.py`) were not edited after the runs started and are committed unchanged in the M2 commit; `report.py` was changed afterwards (PDF path bug, R filtering on SO convergence, compact table) and all seven reports were regenerated.
- `flow report` on each run directory: first attempt failed for all seven (`pandoc ... withBinaryFile: does not exist`: relative path combined with `cwd`); fixed by resolving paths; then 7 PDFs built (pandoc to Typst, `mainfont=Libertinus Serif`, `fontsize=9pt`). pypdf check: 2 to 3 pages each, "EXPLORATORY" on page 1. The SMOKE and X-TIMING-6x6 PDFs were inspected visually; the first table layout overflowed and was replaced by a compact 9-column table.
- `scripts/m2_planning_summary.py` -> `results/exploratory/M2-planning-summary.{md,json}` (J-0009).

### Exploratory measurements (not findings)

- Runtime per solve (FW as drafted): Braess below 0.1 s when converged, about 6 s at the cap; 4x4 rho = 2 to 3: 5 to 9 s; 6x6 rho = 2 to 3: 8 to 12 s; uncongested cells about 1 ms. Gradient projection on 6x6 rho = 2: 0.008 to 0.031 s mean.
- Projected full draft matrix with FW: about 27,000 s (7.5 h) single core, of which optional EXP-005 about 12,800 s (S1 at 1e-8, S2, S3 projected from proxies).
- Convergence: FW nonconverged in 27 of 28 SO and 11 of 25 UE solves at 6x6 rho = 2, in every 6x6 rho = 3 solve, and on the Braess SO with link e at d >= 5.1 (including EXP-001's d = 6) and UE at d >= 8.9. This exceeds the 10 percent failure threshold of protocol section 7.
- Seed spread, 6x6 rho = 2, 20 seeds (GP, all converged): SD of R(UE) 0.0169; bootstrap 95 percent width of the median 0.029 at n = 20, about 0.018 projected at n = 50.
- Degenerate cells: rho = 0.5 (FF already the UE in 14 of 15 grid instances); 3x3 rho = 1 smoke cell (UE in 0 iterations).

### Proposed amendments for the owner

A1 solver (Frank-Wolfe would make the primary analysis fail; gradient projection measured as an alternative), A2 seed count (n = 100 per size, cheap with GP), A3 degenerate rho = 0.5, A4 MIX convergence rule, A5 S3 share value, A6 runtime values, A7 EXP-002 interval verified, A8 freeze-record format. See `research/protocol_amendment_proposals.md`. The draft protocol files are unchanged (SHA-256 identical to the registry values; protocol.md `008cf8a1...`).

### Not done, and why

- No confirmatory run and no freeze (G-FREEZE).
- MIX(c) with the gradient-projection solver: only needed if the owner adopts A1.
- EXP-005 link-removal runner and config: optional experiment, not needed before the freeze.
- S3 config: its share parameter is not fixed (A5).
- Per-experiment `report.md`, `config.json` and `run_manifest.json` under `research/experiments/EXP-NNN/` were not created: no registered experiment has run; the smoke run is reported in `results/exploratory/` only.
- No demo (M5).

### Outstanding risks

FW convergence (now measured, A1); bias from the assistant having seen exploratory primary-cell-analogue values (disclosed, D-009); 6x6 FW solves are near the 10-minute single-run guidance only in aggregate (largest single run 382 s).

### Next action

Owner: decide B1-B6, in particular amendment A1, then freeze. Assistant after the freeze: implement the adopted solver option, rerun the smoke, then M3.
