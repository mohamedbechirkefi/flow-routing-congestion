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

## 2026-11-24: Session 3 (real data, approved amendments, freeze)

**Milestone.** M1 gate (freeze) under the owner's round-2 approvals ("Approve all"; amendments "yes for all others"). No confirmatory run, no push, no paid service.

### Starting state

`git status`: clean, HEAD `4227baa`.

### Work and actual outputs

- Licence check: TNTP README "License" section (opened 2026-11-24) says "Data sets are for academic research purposes only"; GitHub API `license: null`. Matches the approval. Recorded in `data/manifest.json` and D-010.
- `scripts/download_tntp.py` (pinned commit `d1639b4e...`): `SiouxFalls_net.tntp 3136 bytes sha256:ace99b24...`, `SiouxFalls_trips.tntp 10859 bytes sha256:56f95668...`, `SiouxFalls_flow.tntp 3523 bytes sha256:5d0b83a2...`. Files in `data/raw/` (git-ignored). Total under 20 KB.
- Ingestion `src/flow/tntp.py` (pure): Sioux Falls 76 links read and kept, no missing fields; 576 OD cells, 24 diagonal and 24 zero cells excluded, 528 pairs kept, total 360,600 equal to the header.
- Protocol section 15 written before fitting; then `scripts/calibrate.py` (J-0010, J-0011): alpha 0.15, beta 4 (all links identical); rho_SF 5.788; S3 share 0.10826. Engine check J-0012 (UE only): objective 42.3133529 versus published 42.31335287; max link-flow difference 1.28e-4 (tol 1e-6), 1.26e-6 (tol 1e-8).
- During code checks the assistant printed one exploratory value outside the primary cell: 3x3 grid, rho = 2, seed 9000, gradient projection: R(UE) 0.0497, R(MIX(0.5)) 0.0264 (not stored; disclosed in `research/freeze.json`). While checking cell expansion the generator's demand values for confirmatory seed 2000 were printed (no solve).
- Code: gradient projection with background flow; MIX with gradient projection and the A4 convergence rule; `tntp` network cells; `bpr` config block; freeze guard now also requires the config file hash and that the config run equals it.
- Configs: all confirmatory configs on gradient projection; EXP-003 seeds 1000-1099 / 2000-2099, rho {1, 2, 3}, S1 Frank-Wolfe reference cell, S3 cell (share 0.10826); EXP-004 seeds 2000-2099; new EXP-006 (Sioux Falls).
- Tests: `.venv/bin/python -m pytest -q` -> `124 passed in 96.53s` before the freeze record; after the freeze record and guard tests: `127 passed in 95.07s`.
- Guard: every frozen config (EXP-001 to EXP-004, EXP-006) returns `(True, 'frozen')`; a changed EXP-003 copy via `flow run` -> `REFUSED: ... config differs from the frozen experiments/EXP-003.json`, exit 3; EXP-005 refused (no config).
- Freeze: `research/freeze.json`, D-011 with FREEZE lines; protocol SHA-256 `9f629b07b4c8e240c41236ff5c0cfd1abfde9681452c9f662f0175f316ecb97d`, frozen revision `ca8b750`.

### Not done, and why

- A7 not applied (not in the approved list). EXP-005 runner mode and config not implemented (optional; needs an owner-approved addendum).
- No confirmatory run (coordinator schedules M3).

### Next action

M3 after scheduling: download TNTP locally, `uv run flow run EXP-001` ... `EXP-006`, reports as each finishes.

## 2026-11-25: Session 4 (M3, confirmatory runs)

**Milestone.** M3 under the owner's "Start next" (2026-11-25) and the coordinator's M3 brief. No push, no paid service, no download.

### Starting state and checks

- `git status`: clean, HEAD `2f049d0`. Every frozen hash in `research/freeze.json` matched the files on disk; `data/manifest.json` hash matched; the three TNTP files were present with matching SHA-256 (no download needed).
- `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` -> `Audited 19 packages`; editable `flow` points at this repository's `src/`.
- `.venv/bin/python -m pytest -q` -> `127 passed in 98.13s`.

### Preparation (before any confirmatory output), commit `5108a16`

- `src/flow/confirmatory.py`, `scripts/analyse_exp.py`: frozen analyses and figures; interpretation rules fixed in D-012.
- Runner: link flows recorded for Braess and Sioux Falls, Braess path flows; link-removal mode for EXP-005.
- `experiments/EXP-005.json` (implements frozen EXP-005, added before any EXP-005 data; FREEZE line in D-012, `research/freeze.json` `added_after_freeze`).
- Tests: `tests/test_confirmatory.py` (new), `tests/test_records.py` updated. While adapting tests, one old test executed the new EXP-005 config into a pytest temp directory; not inspected; disclosed as D-013.
- Full suite: `138 passed in 226.94s`; after the runs and records: `138 passed in 94.64s`.

### Smoke and metric validation (exploratory), commit `8dfc66c`

- `flow run experiments/exploratory/X-SMOKE-GP.json` -> 26 ok (J-0013); `flow smoke` (Frank-Wolfe) -> 25 ok, 1 nonconverged (J-0014).
- `scripts/validate_metrics.py` on both -> metric checks pass; Braess UE with link e differs from 552 by 6.2e-5 at the frozen 1e-6 tolerance (J-0015).

### Confirmatory runs (revision `8dfc66c`), worker logs `results/raw/logs/`

| EXP | Run id | Start to end (UTC) | Records ok / nc / failed | Verdict (frozen rule) |
|---|---|---|---|---|
| EXP-001 | EXP-001-20261124T234532Z-846e8c0f | 23:45:32 to 23:45:33 | 6 / 0 / 0 | contradicted (UE with e: 6.2e-5 > 1e-6) |
| EXP-002 | EXP-002-20261124T234533Z-fcb88932 | 23:45:33 to 23:45:36 | 450 / 0 / 0 | contradicted (upper, middle boundary off by 1.1e-5, 8.8e-6) |
| EXP-006 | EXP-006-20261124T234536Z-9a9669c8 | 23:45:36 to 23:45:54 | 16 / 0 / 0 | gate pass (1.28e-4); R(UE) rho 2 = 0.0145: replicates |
| EXP-005 | EXP-005-20261124T234554Z-4051f409 | 23:45:54 to 23:46:45 | 5154 / 0 / 0 | incidence 77/100, Wilson [0.678, 0.842]: H1 supported |
| EXP-003 | EXP-003-20261124T234531Z-6cbcaa47 | 23:45:31 to 00:22:35 | 2745 / 155 / 0 | median R(UE) 0.0232, one-sided LB 0.0213, CI [0.0208, 0.0256]: H0 rejected |
| EXP-004 | EXP-004-20261125T002235Z-7a7c2692 | 00:22:35 to 00:22:53 | 2100 / 0 / 0 | strict decrease at every step: H1 supported |

Sensitivity: S1 robust (1e-4: 0.0231, 1e-8: 0.0232); S2 beta = 1: 0.0030 (below delta); S3: 0.0214 (same decision); Frank-Wolfe reference nonconverged on 93/100. Analyses in `research/experiments/EXP-*/analysis.json`, figures in `research/experiments/EXP-*/figures/`, raw-file hashes in `results/M3-raw-manifest.json`. Raw results committed (all under 20 MB in total) except EXP-006 `results.json` (TNTP-derived per-link flows; hash recorded only).

### Deviations and gaps (D-013, D-014)

Stray EXP-005 execution by a test (not inspected); `dirty: true` in three manifests from untracked analysis outputs only; one figure fix after EXP-003 output (no analysis change); experiment reports not written (file tool refused; left unwritten on the coordinator's instruction); EXP-001 1e-10 and EXP-004 link-flow sensitivities have no frozen config.

### Next action

Owner: decide on a 1e-10 rerun of EXP-001/EXP-002 and on the EXP-004 sensitivity. Assistant: write the six 11.3 reports when permitted, then M4.

## 2026-11-25: M3 done (coordinator)

The owner approved the experiment reports (owner, 2026-11-25, "approve all recommendations, RIGGED A", item 4). Subagents may not write report files, so the reports were composed by the M3 session from committed results only and written by the coordinator: 6 report(s). The coordinator checked that every decimal number in them appears in a committed file. With the complete matrices (or documented failures) recorded above, the M3 gate holds. M3 is **done**. Next: M4 (interpretation), not started.

## 2026-11-25: Session 5 (M4, interpretation, evidence audit and manuscript)

**Milestone.** M4 under the owner's "Approve all recommendations, push then next" (2026-11-25, `labs/_shared/owner-approvals-2026-11-25b.md`) and the coordinator's M4 brief. No confirmatory rerun, no change to frozen protocols, configs or seeds, no push, no paid service, no large download.

### Starting state

`git status`: clean; HEAD `15e1181` (M3 done).

### Work and actual outputs

- Exploratory 1e-10 configs written from the frozen ones (only id, label, description, `solver.tol` changed) and committed first: `01c2b4b`.
- `nice -n 10 .venv/bin/flow run experiments/exploratory/X-EXP-001-TOL1E-10.json --quiet` -> `results/exploratory/X-EXP-001-TOL1E-10-20261125T011841Z-ae793d0f` (6 ok). Same for EXP-002 -> `X-EXP-002-TOL1E-10-20261125T011841Z-5acef701` (450 ok). Manifests `dirty: true` (untracked analysis script only).
- `.venv/bin/python scripts/analyse_exploratory_tol.py <both run dirs>` (frozen `flow.confirmatory` unchanged): EXP-001 "reproduced", largest difference 7.53e-9; EXP-002 "derivation confirmed", boundaries within 1.3e-15, 7.0e-10 and 1.5e-9, sign 75/75; largest per-point UE time error 3.37e-6 at d = 3.64. Journal J-0022. Frozen verdicts unchanged (contradicted).
- `.venv/bin/python scripts/m4_exploratory_checks.py` -> `results/exploratory/M4-confounder-checks.json`: primary cell 90/100 instances above delta (S2 0/100, S3 86/100, 6x6 rho 1 3/100); Spearman R(UE) vs UE flow-weighted v/c 0.653; EXP-005 17/100 instances with an effect above 1e-2, median link effect 0.0030. Journal J-0023.
- TNTP `SiouxFalls/README.md` fetched at the pinned commit into the session scratchpad (4,581 bytes, sha256 `ebe1f3dc...54c1`) to verify the "not considered as a realistic one" quotation (audit F-3). Not stored in the repository.
- `.venv/bin/python scripts/evidence_audit.py` -> A1 27/27 hashes match; A2 6/6 metrics copies equal; A3 6/6 counts match; A4 40/40 recomputed estimates match; C 33/33 table rows; B untraced numbers only DOIs and the derived sum 10,626. Findings F-1 to F-8 in `research/publication/evidence_audit.md`. Journal J-0024.
- Manuscript and supplementary file synthesised (11.4, 5,757 words before the second-pass edits); second review pass written and six revisions applied; `bash scripts/build_manuscript_tex.sh` -> `wrote .../manuscript.tex`; `references.bib` filled.
- Claims register rebuilt (21 rows, 11 columns); claims audit, artifact manifest (24 entries), limitations 14 to 19, registry statuses, EXP-001 and EXP-002 reports (v1.1), literature review section 4, decision D-016.
- Tests: `nice -n 10 .venv/bin/python -m pytest -q` -> `138 passed in 98.67s`.

### M4 gate

Every numerical claim in the manuscript maps to a claim row with result id, config hash and figure or table, and to a manifest entry; every content-bearing external claim maps to a source read (one abstract-only source labelled as such; six sources cited for attribution only, labelled "metadata verified, text not read"). M4 is **done**.

### Risks and open items

- The EXP-001 and EXP-002 exact checks remain contradicted under their frozen rule; only exploratory evidence supports the tolerance reading.
- No independent solver check on grids (Frank-Wolfe reference failed on 93/100).
- PDFs not compiled (M6).

### Next action

M5 (interactive page) needs the owner's demo-stack choice (B4); M6 after that.

## 2026-11-25: Session 6 (post-M4 owner decisions, items 2 and 6)

**Authority.** Owner, 2026-11-25, "Approve all" (post-M4) (`labs/_shared/owner-approvals-2026-11-25c.md`), applied under the coordinator's post-M4 brief. No change to frozen protocols, configs, seeds or results; no run; no push.

### Starting state

`git status`: clean; HEAD `a4676a8` (M4).

### Work

- Item 2: decision D-017 records that the funding, competing-interest and AI-use wording of the manuscript is owner-approved. No wording changed.
- Item 6: decision D-018 records that the M5 demo uses the repo's existing stack, static and offline; blocker B4 marked resolved in `roadmap.md`. Nothing built.
- Tests: `nice -n 10 .venv/bin/python -m pytest -q` -> `138 passed in 100.09s (0:01:40)`.

### Owner placeholders for M5

1. Repository URL, `research/paper/manuscript.md` section "Data and code availability": "[to be added on owner-approved release]" (and its generated copy in `manuscript.tex`). Needs the owner's release decision (G-PUBLIC).

Not a placeholder, but owner-only: `research/publication/author_review.md` is still to be completed by the owner before any publication.

### Next action

M5: static offline demo page and article drafts from the verified results; then M6.

## 2026-11-25: Session 7 (M5, interactive experience)

**Authority.** Owner, 2026-11-25, "Next" (`labs/_shared/owner-approvals-2026-11-25d.md`); FLOW stack exception per D-018. No change to frozen protocols, configs, seeds or results; no run of any experiment; no push; no paid service.

### Starting state

`git status`: clean; HEAD `7f9ae53`. `../.tools/py/bin/uv sync --frozen --all-groups --all-extras` -> `Audited 19 packages in 4ms`.

### Work

- `scripts/export_demo_data.py` -> `wrote demo/public/data/results.json` (schema `lab-demo-results` 1.0.0; nine entries: EXP-001 to EXP-006 measured, three exploratory; 158 display strings; source sha256 list; no timestamps).
- `scripts/export_demo_sandbox.py` -> `wrote demo/public/data/sandbox.json (60862 bytes)`, `wrote demo/tests/fixtures/sandbox_fixture.json (24095 bytes)`; 0.10 s user time. Grid networks from exploratory seeds 9000 to 9009 only.
- Page in `demo/site/` (plain HTML, CSS, JavaScript): overview with status label and evidence-label legend; animated Braess network (EXP-002 raw records) with demand slider, policy comparison, edge congestion and the paired before and after chart; published results (four charts with intervals and nine experiment panels); assumptions; method and limitations; sandbox in a Web Worker (engine port; network and seed, demand, compliance, run, cancel, reset).
- `scripts/build_demo.py` -> `export check: identical`, `sandbox export check: identical`, `built demo/dist: 8 files`.
- `docs/demo.png` (107,056 bytes) from a headless capture of the Braess explorer.
- Text consistency (D-020): README, CITATION.cff, demo README, articles README, new `articles/medium.md` and `articles/linkedin.md`, `research/publication/author_review.md` status line; CONTRIBUTING section 7 appended.
- Decisions D-019 and D-020. Roadmap M5 marked done.

### Tests and checks (actual outputs)

- `node --test demo/tests/*.test.mjs` (Node 22.23.3) -> `# tests 33`, `# pass 33`, `# fail 0` (16 engine-port and fixture tests, 17 loader tests). Largest port differences against the Python fixture: TSTT 3.7e-16 relative, link flows 2.8e-15 of the largest flow (stated tolerance 1e-9 and 1e-7).
- `.venv/bin/python -m pytest -q tests/test_demo_export.py` -> `5 passed in 0.19s`.
- Full suite: `nice -n 10 .venv/bin/python -m pytest -q` -> `143 passed in 98.67s (0:01:38)`.
- `cd demo && node tools/a11y_check.mjs dist --screenshots <scratchpad>/flow/shots`:

```
PASS results render (no fail-closed panel): 9 experiment panels
PASS text contrast, light scheme (WCAG AA)
PASS text contrast, dark scheme (WCAG AA)
PASS keyboard reaches every focusable element: 32 reached of 32
PASS visible focus indicator
PASS no horizontal page scroll at 360 px: overflow 0px
PASS reduced motion: no running animations: 0 running
PASS no request leaves the local origin
PASS offline after first load: results stay, sandbox runs: Sandbox output (Braess network with link e, demand 6): R(UE) = 0.1084, R(FF) = 0
A11Y-CHECK PASS
```

- Fail-closed check: with one estimate in `dist/data/results.json` corrupted, the checker printed `FAIL results render (no fail-closed panel): 0 experiment panels` and `A11Y-CHECK FAIL (2)`; `dist/` was then rebuilt.
- Motion check (headless, scratch script): 9 running animations with default motion, 0 after the on-page toggle, 0 under reduced motion (checker).
- Screenshots inspected (desktop light and dark, mobile, sandbox after a grid run). Fixed during the session: charts drawn before layout (now drawn on first width), a CSS class clash that enlarged the sandbox tag, overlapping value labels in the interval charts, cramped estimate tables on phones (now stacked), inline styles blocked by the page's CSP (now CSSOM), and duplicate focus keys.
- Scans: no `REPLACE` marker in `demo/`; no em dash, e-mail address or missing SPDX header in the new files.

### M5 gate

Offline after the initial load, responsive at 360 px, usable with the keyboard, no fabricated data (every number exported from committed files and checked against the manuscript), no runtime service: the gate holds. M5 is **done**.

### Owner placeholders and owner items

1. Repository URL and demo URL: "[to be added on owner-approved release]" in the manuscript, README, CITATION.cff, articles, demo README and page footer (G-PUBLIC).
2. The FLOW manuscript title was not in the post-M4 title approval list.
3. Full-text review of the manuscript and articles, and `author_review.md` (no box ticked), belong to M6.

### Next action

M6 (release candidate): PDFs, clean-clone reproduction, owner review checklist.

## 2026-11-25: Session 8 (M6, release candidate)

**Authority.** Owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`), under the coordinator's M6 brief; FLOW keeps its Python and plain static demo stack (D-018). No change to frozen protocols, configs, seeds or results; no confirmatory run; no push, tag or release; no paid service.

### Starting state

`git status`: clean; HEAD `9ce3092` (M5).

### Clean clone (scratch directory outside the repository)

- `git clone -q <repo> $S/clone`; `uv sync --frozen --all-groups --all-extras` -> 19 packages installed; rerun `Audited 19 packages in 3ms`.
- `nice -n 10 .venv/bin/python -m pytest -q` -> `143 passed in 133.80s (0:02:13)`.
- `scripts/analyse_exp.py` on the committed raw results of EXP-001 to EXP-005 (EXP-004 with `--exp003`) -> `git status --short` empty (byte-identical analysis files and figures). EXP-006: `cannot read result file ... results.json` because the TNTP-derived `results.json` is not committed (documented in its reproduction file).
- `.venv/bin/flow run experiments/exploratory/X-EXP-001-TOL1E-10.json --out $S/smoke --quiet` -> 0.33 s; config `cmp` identical; `records 6 max abs diff (excl. runtime) 0 differing fields []`.
- `scripts/build_demo.py` -> `export check: identical`, `sandbox export check: identical`, `built demo/dist: 8 files`; `node --test demo/tests/*.test.mjs` -> `# tests 33`, `# pass 33`, `# fail 0`; `node tools/a11y_check.mjs dist` -> nine PASS lines and `A11Y-CHECK PASS`.
- `scripts/export_demo_data.py` and `scripts/export_demo_sandbox.py` -> `git status --short` empty (deterministic).

### Findings and fixes (working repository)

1. PDF title not set in metadata and printed as plain text: builder strips leading HTML comments and promotes the heading (`src/flow/report.py`).
2. Table captions separated from their tables (unbreakable Typst figures): tables now break across pages.
3. Table cells centred and justified, wrapped numbers spread across cells: left-aligned, unjustified, 8 pt, header rules.
4. 21 bullet lists in the six reports printed as raw "- " text (no blank line before the list): blank lines inserted.
5. Figures only referenced by path: the manuscript now embeds Figures 1 to 6 and each report its own figures (Typst root is the repository root).
6. Absolute home-directory paths in six current files replaced by relative paths; kept in append-only records and committed logs (see the note below).
7. Youn et al. (2008) read in full (arXiv v4); Roughgarden and Tardos (2002) passages checked (pages 1, 3, 17); labels updated; evidence audit section 6 appended.
8. `CITATION.cff`: version `0.1.0-rc1`, `date-released` removed.

### PDFs (built with `flow.report.build_pdf`, inspected as PNG at 60 ppi, page 6 also at 130 ppi)

`manuscript.pdf` 12 pages (520,659 bytes), `supplementary.pdf` 5 (145,996), EXP-001 4 (129,424), EXP-002 4 (184,731), EXP-003 5 (224,322), EXP-004 3 (156,577), EXP-005 3 (127,420), EXP-006 4 (113,612). pypdf: title set in all eight, 0 e-mail addresses, 0 local paths. `bash scripts/build_manuscript_tex.sh` -> `wrote .../manuscript.tex` (6 `includegraphics`).

### Checks (actual outputs)

- `.venv/bin/python scripts/m6_checks.py all` -> `links: 12 relative links checked in 58 tracked Markdown files`, `PASS links`; `numbers: 46 decimal numbers checked in 4 files`, `PASS numbers`; `manifests: 109 artifact-manifest paths checked`, `3 of 3 data-manifest downloads present locally and checked`, `PASS manifests`; `cff: 8 top-level keys checked; version 0.1.0-rc1`, `PASS cff`.
- `research/freeze.json`: 12 of 12 frozen file hashes match.
- `scripts/evidence_audit.py` rerun: A1 27 checked, no mismatch; A2 all equal; A3 all match; A4 40 checked, no mismatch; untraced strings unchanged (DOIs, 128701, 10,626).
- Scan of 275 tracked and new files: 0 e-mail addresses (one false positive, the text `user.email=...` in `CLAUDE.md`), 0 tokens or keys, 0 private-key headers, 0 `.env` files; home-directory paths in 11 files (30 lines) before the fix, 5 files after (append-only or committed logs).
- SPDX: every file added since the initial commit has the header except `results/exploratory/X-SF-UE-CHECK/output.txt` (a result; not edited).
- Licences: `research/publication/dependency_licences.md`; no runtime dependency is copyleft; flags: pandoc (GPL, build tool), embedded fonts (OFL, DejaVu), headless Chrome (test tool), hatchling (not read).

### Note on append-only records (no edit made)

This file (entries of 2026-11-24, lines 17 and 22) and `research/experiment_journal.jsonl` (J-0001) contain absolute home-directory paths of the development machine, as do the committed run logs `results/raw/logs/worker-A.log`, `results/raw/logs/worker-B.log` and `results/exploratory/session-M2-runs.log`. They are not rewritten; the owner decides before publication whether they are acceptable.

### Owner placeholders and open items

Listed with file and line in `research/publication/author_review.md`, section "Prepared for the owner (M6, 2026-11-25)": repository and demo URLs (9 places plus the generated `manuscript.tex`), the manuscript title, the CITATION title, blocker B5, the licence flags, and G-PUBLIC.
