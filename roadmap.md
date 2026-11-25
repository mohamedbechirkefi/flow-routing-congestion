<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW roadmap

Target: five focused development days (planning estimate, never a reason to weaken evidence). Status values: not started, in progress, done, blocked. A milestone is done only when its gate is checked and recorded in `progress.md`.

| ID | Milestone | Depends on | Acceptance criteria (gate) | Section 11.6 additions | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | Control files exist; feasibility audit with real command outputs; sources and licences audited; budget zero; scope and fallback explicit; owner can understand question, cost and exclusions | Registry, manuscript skeleton, draft experiment protocols, zero-cost toolchain confirmed | P0 | 0.5 day | done (2026-11-24), pending owner review | none |
| M1 | Research and preregistration | M0 | Reading list of `research/literature_review.md` section 3 completed and levels updated; formal model, baselines and fixture manifest final; protocol and EXP protocols frozen **by the owner** with recorded SHA-256; exploratory work visibly separated | Freeze confirmatory protocols before execution | P0 | 0.5 day | done (2026-11-24): gate passed, protocol v1.0 frozen by the owner's approval (D-011, `research/freeze.json`); reading list items still metadata-only are recorded in the literature review | none |
| M2 | Core implementation | M1 drafts (implementation may start before the freeze) | Graph, BPR and linear costs, Dijkstra, FF, UE (Frank-Wolfe), SO, MIX(c), MSA reference; unit, property and golden tests pass (count recorded from a real run): shortest paths vs brute-force enumeration, flow conservation, nonnegative costs, disconnected graphs, convergence tolerances, exact Braess values, MIX(0)=UE, MIX(1)=SO; CLI `flow smoke/run/report`; correctness before UI | Versioned JSON result schema, run manifests and report generators built with the core | P0 | 1 day | done (2026-11-24) against the draft protocol: all listed components, 97 tests passing (real run), CLI and records built; exploratory planning runs J-0002 to J-0009. Reopened and closed 2026-11-24 (round 2): gradient projection for the MIX follower, TNTP ingestion, freeze guard on configs; 127 tests passing (real run) | none |
| M3 | Experiments | M1 freeze, M2 | Smoke matrix run (exploratory, done at M2: J-0002); frozen matrix EXP-001 to EXP-004 (EXP-005 optional) complete or failures documented; raw machine-readable results retained; plots and uncertainty from raw outputs; no silently dropped runs | Each EXP report written as the experiment finishes; failures and deviations recorded at once; provenance captured during runs | P0 | 1 day | in progress (2026-11-25): smoke and metric validation done (J-0013 to J-0015); full frozen matrix of EXP-001 to EXP-006 run with no dropped or failed run (J-0016 to J-0021); analyses, figures, raw results and manifests done; the six 11.3 experiment reports are not yet written (D-014), so the 11.6 M3 addition is not met | Experiment reports; owner decision on EXP-001/EXP-002 1e-10 rerun |
| M4 | Interpretation | M3 | Confounders and S1-S3 sensitivity analysed; expected versus observed; claims register filled; every numerical claim maps to result id, config and figure; every external claim to a verified source | Experiment reports and evidence audit finished; manuscript synthesised including contradictory results; second review pass challenging the preferred hypothesis | P0 | 0.75 day | done (2026-11-25, D-016) | none |
| M5 | Interactive experience | M4 (results), M2 (sandbox engine) | Static page: animated network with demand slider, policy comparison, edge congestion, paired before/after charts; offline after first load; keyboard usable; reduced motion; mobile layout; measured vs sandbox vs hypothetical labelled; no runtime service | Demo, paper, reports and articles use identical verified results, labels and scope | P1 | 0.75 day | not started | Owner choice of demo stack (B4) |
| M6 | Release candidate | M4, M5 | Clean clone, `uv sync --frozen`, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan, all with real outputs | PDFs compiled (pandoc to Typst) and visually inspected; references, cross-links, equations and figures verified; owner review checklist | P1 | 0.5 day | not started | Owner approval for any publication (G-PUBLIC) |

## Cut order if the five-day target is threatened

1. EXP-005 (optional).
2. Demo animation and polish (keep a static results page and small sandbox).
3. The 4x4 size in EXP-003.

Never cut: controls, tests, reports for every registered experiment, the manuscript, truthfulness.

## Owner decisions and blockers

Status 2026-11-24 (round 2): B1 (freeze), B2 (UE versus SO stays primary), B3 (real data: TNTP Sioux Falls adopted, local only) and B6 (A1-A5 approved) are resolved (D-010, D-011). B4 and B5 remain open. New: EXP-005 config and runner mode need an owner-approved addendum before it can run.


- **B1 (G-FREEZE).** Approve or amend and freeze `research/protocol.md` and EXP-001 to EXP-005 protocols.
- **B2.** Primary contrast: keep the proposal (R relative to SO, primary hypothesis on UE, FF as baseline in every comparison; decision D-004) or make UE versus FF the primary paired contrast as section 10's "simplest baseline as the primary comparator" could be read.
- **B3.** Confirm synthetic-only data (D-003). Any real network (for example TNTP Sioux Falls) would need a rights decision first: the TNTP repository has no licence file and says "academic research purposes only".
- **B4.** Demo stack: TypeScript/React/Vite (master prompt default, needs npm packages and the read-only Node) or a dependency-free single HTML page with vanilla JavaScript (simpler, recommended). Resolved 2026-11-25 (D-018): the repo's existing stack, static and offline, no npm packages.
- **B6 (new, M2).** Decide amendment proposals A1-A5 in `research/protocol_amendment_proposals.md` before freezing. A1 (solver) is blocking in practice: with Frank-Wolfe as drafted, the exploratory nonconvergence rate in the primary-cell analogue exceeds the 10 percent failure threshold of protocol section 7.
- **B5.** Confirm the licence wording for public texts: the project must be called source-available, not open-source (D-001).
