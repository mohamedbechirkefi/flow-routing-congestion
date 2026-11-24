<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW roadmap

Target: five focused development days (planning estimate, never a reason to weaken evidence). Status values: not started, in progress, done, blocked. A milestone is done only when its gate is checked and recorded in `progress.md`.

| ID | Milestone | Depends on | Acceptance criteria (gate) | Section 11.6 additions | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | Control files exist; feasibility audit with real command outputs; sources and licences audited; budget zero; scope and fallback explicit; owner can understand question, cost and exclusions | Registry, manuscript skeleton, draft experiment protocols, zero-cost toolchain confirmed | P0 | 0.5 day | done (2026-11-24), pending owner review | none |
| M1 | Research and preregistration | M0 | Reading list of `research/literature_review.md` section 3 completed and levels updated; formal model, baselines and fixture manifest final; protocol and EXP protocols frozen **by the owner** with recorded SHA-256; exploratory work visibly separated | Freeze confirmatory protocols before execution | P0 | 0.5 day | in progress (drafts written) | **Owner freeze (G-FREEZE)**; owner decisions B1-B4 below |
| M2 | Core implementation | M1 drafts (implementation may start before the freeze) | Graph, BPR and linear costs, Dijkstra, FF, UE (Frank-Wolfe), SO, MIX(c), MSA reference; unit, property and golden tests pass (count recorded from a real run): shortest paths vs brute-force enumeration, flow conservation, nonnegative costs, disconnected graphs, convergence tolerances, exact Braess values, MIX(0)=UE, MIX(1)=SO; CLI `flow smoke/run/report`; correctness before UI | Versioned JSON result schema, run manifests and report generators built with the core | P0 | 1 day | not started | none |
| M3 | Experiments | M1 freeze, M2 | Smoke matrix run (exploratory); frozen matrix EXP-001 to EXP-004 (EXP-005 optional) complete or failures documented; raw machine-readable results retained; plots and uncertainty from raw outputs; no silently dropped runs | Each EXP report written as the experiment finishes; failures and deviations recorded at once; provenance captured during runs | P0 | 1 day | not started | Owner freeze |
| M4 | Interpretation | M3 | Confounders and S1-S3 sensitivity analysed; expected versus observed; claims register filled; every numerical claim maps to result id, config and figure; every external claim to a verified source | Experiment reports and evidence audit finished; manuscript synthesised including contradictory results; second review pass challenging the preferred hypothesis | P0 | 0.75 day | not started | none |
| M5 | Interactive experience | M4 (results), M2 (sandbox engine) | Static page: animated network with demand slider, policy comparison, edge congestion, paired before/after charts; offline after first load; keyboard usable; reduced motion; mobile layout; measured vs sandbox vs hypothetical labelled; no runtime service | Demo, paper, reports and articles use identical verified results, labels and scope | P1 | 0.75 day | not started | Owner choice of demo stack (B4) |
| M6 | Release candidate | M4, M5 | Clean clone, `uv sync --frozen`, tests, smoke reproduction, demo build, manifest and link checks, secret and licence scan, all with real outputs | PDFs compiled (pandoc to Typst) and visually inspected; references, cross-links, equations and figures verified; owner review checklist | P1 | 0.5 day | not started | Owner approval for any publication (G-PUBLIC) |

## Cut order if the five-day target is threatened

1. EXP-005 (optional).
2. Demo animation and polish (keep a static results page and small sandbox).
3. The 4x4 size in EXP-003.

Never cut: controls, tests, reports for every registered experiment, the manuscript, truthfulness.

## Owner decisions and blockers

- **B1 (G-FREEZE).** Approve or amend and freeze `research/protocol.md` and EXP-001 to EXP-005 protocols.
- **B2.** Primary contrast: keep the proposal (R relative to SO, primary hypothesis on UE, FF as baseline in every comparison; decision D-004) or make UE versus FF the primary paired contrast as section 10's "simplest baseline as the primary comparator" could be read.
- **B3.** Confirm synthetic-only data (D-003). Any real network (for example TNTP Sioux Falls) would need a rights decision first: the TNTP repository has no licence file and says "academic research purposes only".
- **B4.** Demo stack: TypeScript/React/Vite (master prompt default, needs npm packages and the read-only Node) or a dependency-free single HTML page with vanilla JavaScript (simpler, recommended).
- **B5.** Confirm the licence wording for public texts: the project must be called source-available, not open-source (D-001).
