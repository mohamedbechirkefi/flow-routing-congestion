<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW: how every session works in this repository

FLOW asks one question: can individually optimal routing worsen collective travel time? It is a small, offline, zero-cost simulation study on synthetic networks (a Braess network and grids). It is not a reconstruction of any commercial navigation product and makes no prediction for any real city.

`master_prompt.md` is the authority. It is never edited. If this file and the master prompt conflict, the master prompt wins; record the conflict in `progress.md`.

## 1. Reading order (before modifying anything)

1. `master_prompt.md`
2. `roadmap.md`
3. `progress.md` (latest entry first, then the open risks)
4. `research/protocol.md`
5. `research/claims_register.csv`

Then also read, when relevant: `research/decision_log.md`, `research/experiment_registry.csv`, the `research/experiments/EXP-NNN/protocol.md` you are working on, `research/limitations.md`, `data/manifest.json`.

At session start: run `git status`, state the current milestone and the next bounded task. Never overwrite changes made by the owner.

## 2. Mandatory requirements (master prompt section 11, made binding for every milestone)

- **Registry.** Every experiment is registered in `research/experiment_registry.csv` before confirmatory execution, with purpose, dependency, primary outcome, protocol hash, status, report location and planned analysis. A seed is a run inside an experiment, not a new experiment. A new question or a materially different protocol gets a new EXP id.
- **Per-experiment folder** `research/experiments/EXP-NNN/` holds `protocol.md`, `report.md`, `report.pdf` (generated locally only), `config.json`, `run_manifest.json`, `metrics.csv`, `figures/`, `reproduction.md`. Never create placeholder results, placeholder PDFs or mock data to fill the tree.
- **Protocol before runs (11.2).** The protocol states question, mechanism, verified rationale, competing explanations, falsifiable hypotheses, estimand, unit, scope, variables, treatment and control, baseline, seeds, sample-size rationale, compute budget, metric formulas and units, uncertainty method, exclusion and stopping rules, failure modes, sensitivity tests, reproduction commands and what would contradict the hypothesis.
- **Report for every registered experiment (11.3),** in the twelve-section structure, including failed, null, abandoned and exploratory ones, each visibly labelled.
- **One integrated manuscript (11.4)** at `research/paper/manuscript.md` (canonical source), with `manuscript.tex` and `manuscript.pdf` generated locally by free tools.
- **Evidence pipeline (11.5).** Tables and figures are generated once from versioned results and reused everywhere. A manifest maps every number, figure and claim to experiment id, run ids, metric definition, result path, generator script, config or protocol hash and code revision. A second review pass must challenge the preferred hypothesis.
- **Milestone additions (11.6).** M0/M1: registry, manuscript skeleton, experiment protocols, zero-cost toolchain confirmed, protocols frozen by the owner before execution. M2: versioned output schemas, reproducibility manifests and report generators built with the core. M3: reports written as experiments finish; failures and deviations recorded at once. M4: reports and evidence audit finished, manuscript synthesised, contradictory results and sensitivity included. M5: demo, paper, reports and articles use identical verified results, labels and scope. M6: PDFs compiled and visually inspected where tooling permits; clean-clone smoke reproduction; owner review checklist.
- **Publication gate.** Satisfied only when every registered experiment has a truthful standalone report, the manuscript is complete, artifacts are traceable and blockers are disclosed.

## 3. Toolchain (zero cost, recorded in decision D-002)

- Python 3.12.1 at `/usr/local/bin/python3`; project environment managed by uv at `../.tools/py/bin/uv` (paths in this section are relative to the repository).
- PDFs: Markdown is canonical. `pandoc` (`../.tools/pandoc`) converts Markdown to Typst; the `typst` Python package (0.15.0, in `../.tools/py/`) compiles the PDF. `manuscript.tex` is generated from Markdown with pandoc. There is no TeX distribution on this machine; never claim a LaTeX-compiled PDF.
- Node 22.23.3 at `../../helix/.tools/node/bin` may be used read-only for the demo build. Never modify that folder.

## 4. Rules (all sessions)

### Gates
- Never push, add a remote, create a GitHub repository or publish anything (G-PUBLIC).
- No paid service of any kind. No paid API, inference, cloud compute, hosting or data.
- Never freeze a protocol yourself. Freezing is the owner's decision (G-FREEZE). Until the owner freezes a protocol, every run is exploratory and labelled so.
- No confirmatory experiment before the owner's recorded freeze. A tiny exploratory smoke check of the toolchain is allowed when labelled exploratory.

### Scope
- Work only inside this repository, except for read-only use of the tools listed in section 3.
- Do not touch any other folder of the parent research workspace `../..` (hive, helix, cogkt, trading, the other labs).
- Never kill processes you did not start. Never delete anything you did not create in the current session.

### Truthfulness
- Never fabricate results, citations, test counts or PDFs.
- Record the commands you ran and their actual outputs in `progress.md`.
- A source not actually opened is labelled unverified and is not cited as read.
- Never mark incomplete work done.

### Files and style
- New text and code files start with `SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0` as a comment where the format allows. JSON and CSV files are covered by `NOTICE.md`.
- The licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `.github/`) are the owner's and are not changed. Development commands may be appended to `CONTRIBUTING.md`.
- English. No em dashes. Plain, formal register.
- No e-mail address, personal identifier or secret in any committed file (git author metadata excepted).
- Refer to the owner as "the owner"; use they/them if a pronoun is needed.
- Large generated files stay out of git (`results/raw/`); provide deterministic regeneration scripts and small fixtures.

### Commits
- Local commits only, with the owner's git identity passed on the command line (`git -c user.name=... -c user.email=... commit`, values from the owner's session brief, never written into a file), message ending with a blank line and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Run `git status` before and after.

## 5. Session end

Update `progress.md` (dated, append-only: decisions, commands, actual outputs, failures, changed files, risks, next action) and `roadmap.md` statuses. Append decisions to `research/decision_log.md`. Run the test suite if code changed, or say why not.
