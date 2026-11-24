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
