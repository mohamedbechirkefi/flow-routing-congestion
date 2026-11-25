<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Second review pass: arguing against the preferred hypothesis

**Date.** 2026-11-25 (M4). **Reviewer.** The AI research assistant, as internal quality control. This is not external peer review.

**Object.** `research/paper/manuscript.md` (M4 draft), `research/paper/supplementary.md`, the six experiment reports and the claims register.

**Preferred hypothesis under challenge.** Individually optimal (equilibrium) routing worsens collective travel time by a practically meaningful margin (EXP-003 H1), supported by the compliance, Braess-link and real-network results; the two failed exact checks are tolerance artefacts.

Each challenge below states the strongest opposing reading, what the evidence says, whether the challenge holds, and what was changed.

## 1. Strongest alternative readings

| # | Challenge | Evidence | Holds? | Change made |
|---|---|---|---|---|
| 1.1 | **The effect is a product of the chosen congestion level.** The primary cell (rho = 2) is a congested regime chosen by the study; at rho = 1 the median excess is 0.00305 (6x6) and 0.00409 (4x4), both below delta, and only 3 of 100 6x6 instances exceed delta (J-0023). "Individually optimal routing worsens collective travel time" is true only under congestion. | Table 2; S4.2 | **Yes.** The primary cell and delta were fixed before any run (commit `91ecb92`), so this is not a forking-paths problem, but the abstract mentioned the linear-cost limit and not the light-demand limit. | Abstract and conclusion now state that the excess is below the margin at light demand (rho = 1). |
| 1.2 | **The effect is a product of the quartic cost convention.** With beta = 1 the median is 0.00304 and no instance exceeds delta. The "calibration" from Sioux Falls only confirms the conventional 0.15 and 4, which the TNTP README says are assumed. | Table 3; CL-005; TNTP README | **Yes,** already disclosed (abstract, Table 6, Section 7). | None beyond 1.1. |
| 1.3 | **The 1 percent margin is not a practical threshold.** delta = 0.01 was set by the assistant at M0 without an external source. Calling a 2.3 percent excess "practically meaningful" borrows authority from a convention. | Protocol section 4 | **Yes.** | Section 6.4 now says "by more than the preregistered 1 percent margin" and states that the margin is a study convention, not an externally grounded threshold. |
| 1.4 | **OD sampling drives the result.** 12 OD pairs at Manhattan distance at least n - 1 load the grid centre; a different OD rule might give a smaller gap. | 90 of 100 instances exceed delta individually; 4x4 grids also exceed delta; OD count and distance rule never varied | **Partly.** Instance-to-instance variation is covered; the OD rule is a fixed design choice. | Already in Table 6 and Section 7; no further change. |
| 1.5 | **A solver bias, shared by all arms, creates the gap.** Every grid number comes from one gradient-projection implementation; the Frank-Wolfe reference failed on 93 of 100 instances. | S1 tolerances agree (paired shifts below 1e-5); engine matches Braess (exactly, at 1e-10) and Sioux Falls UE (1.28e-4); SO never validated against an external grid solution | **Partly.** An incompletely optimised SO would lower R(UE), not raise it; an unconverged UE is excluded by S1. No independent SO check exists on grids. | Section 7 already states it; Section 4.3 now discloses that the solver was changed before the freeze because Frank-Wolfe did not converge in exploratory runs (amendment A1). |
| 1.6 | **The compliance result is close to true by construction.** MIX(0) = UE and MIX(1) = SO, so an overall decline is built in. | Table 4 | **Partly.** The step-wise test is informative (re-equilibration could have offset a step), but the result is weaker than "H1 supported" suggests. | Abstract now qualifies the compliance result as holding "in one operationalisation of partial compliance"; Section 6.3 already discusses it. |
| 1.7 | **Braess links are common but immaterial.** 77 of 100 instances have one at 1e-4, but the median effect is 0.0030 and only 17 of 100 instances have one above 1e-2. | CL-008, CL-012 | **Yes,** already reported in 5.5 and 6.3. | None. |
| 1.8 | **The real-network replication is weak.** 0.01453 against 0.01 on one network the maintainers call unrealistic, at a demand level defined by the study's calibration. | Table 5 | **Yes.** | Abstract now gives the small margin and the network's status. |
| 1.9 | **The exact-check contradictions might not be tolerance artefacts.** The preferred reading (solver tolerance) is supported only by a post hoc exploratory rerun. | J-0022; residual 3.37e-6 at d = 3.64 remains at 1e-10 | **Partly.** The rerun meets the frozen rule with the frozen analysis code, which is strong evidence; it remains exploratory, and a per-point residual remains near the regime change. | The manuscript keeps both verdicts as "contradicted", reports the residual, and uses "consistent with", not "shows". No change needed. |

## 2. Overgeneralisation check

- Title, abstract and conclusion restrict the claim to static deterministic assignment on synthetic grids, with the real network as one weak test. No sentence refers to a real city, real drivers or any navigation product. **Holds as written.**
- Section 6.1 attributes the excess to the protocol's mechanism (travellers ignore the marginal delay they impose). The supporting evidence is an exploratory correlation (Spearman 0.653). **Challenge holds in part:** the text now labels the correlation as exploratory and correlational.
- Section 1 opens with "a classical result" about Braess. The source read (Braess et al. 2005) supports the example; the general "need not minimise" statement is the paradox itself. **Holds as written.**

## 3. Stale figures and numbers

- All figures referenced by the manuscript are the M3 figures in `research/experiments/EXP-*/figures/`, generated by `scripts/analyse_exp.py` from the confirmatory runs. No figure shows exploratory data. The EXP-003 sensitivity figure was regenerated after a cosmetic fix (D-014); its numbers equal `analysis.json`. **No stale figure found.**
- One aggregate in the draft ("the whole confirmatory matrix ran in under 40 minutes") was derived from run timestamps, not stored as a number. **Challenge holds:** replaced by stored per-experiment runtimes.
- "About nine times" (Section 6.1) is the ratio 0.2007 / 0.02317 of two stored medians; it is recorded as a derived value in the evidence audit.
- The claims register said "within 4.5e-16" where the stored value is 4.44e-16; corrected (evidence audit finding F-1).

## 4. Leakage

- **Sioux Falls into the grids.** Only the BPR parameters were taken from Sioux Falls, by a rule fixed before the fit, and they equal the conventional values. No R, UE or SO on Sioux Falls was computed before the freeze except the UE engine check (J-0012). **No leakage.**
- **Exploratory into confirmatory.** Exploratory seeds 9000-9019 are disjoint from the confirmatory seeds. The primary-cell analogue was seen before the freeze (C4) and informed only n. **Disclosed; no leakage into the rule.**
- **Shared instances.** EXP-004 and EXP-005 reuse EXP-003 instances. This is by design (matched comparison) and means they are not independent replications. Stated in Section 7.

## 5. Missing failed runs

- 155 nonconverged Frank-Wolfe records: reported (Tables 3, S1).
- The stray EXP-005 execution by a test (D-013): reported (S6).
- Exploratory pre-freeze runs in which Frank-Wolfe failed to converge (journal J-0002 to J-0008), the reason for the solver amendment: **not mentioned in the draft manuscript.** Challenge holds: Section 4.3 now discloses them.
- No confirmatory record failed and none was dropped (A3 of the evidence audit recounted every status from the raw tables).

## 6. Summary of changes made to the manuscript

1. Abstract: light-demand limit added; compliance result qualified to one operationalisation; real-network margin and status given.
2. Section 4.3: pre-freeze Frank-Wolfe nonconvergence and the solver amendment disclosed.
3. Section 5.7: underived aggregate runtime removed.
4. Section 6.1: exploratory correlational nature of the mechanism evidence stated.
5. Section 6.4: "practically meaningful" replaced by the preregistered-margin wording, with the margin's status stated.
6. Section 9: light-demand limit added to the conclusion.

No verdict, number or claim strength was increased by this pass.
