<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Evidence audit (master prompt 11.5), M4

**Date.** 2026-11-25. **Auditor.** The AI research assistant (internal quality control, not peer review). **Generator.** `scripts/evidence_audit.py`; machine-readable output `research/publication/evidence_audit.json`. **Manifest.** `research/publication/artifact_manifest.json` (24 artifact entries).

**Scope.** `research/paper/manuscript.md`, `research/paper/supplementary.md`, the six experiment reports, `research/claims_register.csv`, against the committed results of the six confirmatory runs (revision `8dfc66c`) and the M4 exploratory outputs.

## 1. Raw-output cross-checks (Part A)

| Check | What was compared | Result |
|---|---|---|
| A1 | SHA-256 of every file listed in `results/M3-raw-manifest.json` against the files on disk | 27 of 27 match |
| A2 | Committed `research/experiments/EXP-*/metrics.csv` against the raw run's `metrics.csv` | 6 of 6 identical |
| A3 | Record count and status counts recounted from each raw `metrics.csv` against `analysis.json` | 6 of 6 match (6; 450; 2,900 with 155 nonconverged; 2,100; 5,154; 16) |
| A4 | 40 key estimates recomputed from the raw per-record tables, compared at 1e-12: EXP-003 primary n, median and mean; median R(UE) and R(FF) for every main and sensitivity cell; EXP-004 median R for every arm and capacity scale; EXP-006 R(UE) at rho = 2 | 40 of 40 match |

**Denominators and sample counts** (checked by hand against `analysis.json`): every EXP-003 main cell n = 100 with no exclusion; Frank-Wolfe reference n = 7 (SO 93 and UE 62 nonconverged; R needs both); EXP-004 n = 100 per arm and scale; EXP-005 n = 100 instances, 48 removals each, 0 disconnecting removals, 177 flagged links; EXP-006 one network, 16 records. The manuscript's 10,626 records is the sum of the six stored record counts.

**Units** (checked against protocol section 3 and the TNTP README): grid TSTT in veh min per hour and trip times in minutes; Braess values in the example's abstract units; Sioux Falls times in 0.01 hours (stated in Tables 5 and S7); R, Gini and incidence dimensionless.

**Uncertainty** (checked against `analysis.json`): grid intervals are 95 percent percentile bootstrap intervals over instances (10,000 resamples, seed 20261124), one-sided bounds are 5th percentiles; EXP-005 intervals are Wilson intervals; EXP-001, EXP-002 and EXP-006 report no interval (deterministic). No interval in the manuscript is described with another method.

**Precision.** Displayed values are rounded from stored values; the number trace allows half a unit in the last displayed digit. No value is displayed with more precision than stored.

## 2. Number trace (Part B)

Every decimal number, and every integer above 100 that is not a year, in the documents listed was looked up among the numeric values stored in the committed result files (analysis files, run manifests, per-record tables, exploratory outputs, calibration output, freeze record, data manifest), allowing for display rounding and percent display.

| Document | Number occurrences checked | Traced to results | Traced to protocol or config only | Untraced occurrences |
|---|---|---|---|---|
| manuscript.md | 367 | 357 | 0 | 10 |
| supplementary.md | 236 | 236 | 0 | 0 |
| claims_register.csv | 116 | 114 | 0 | 2 |
| EXP-001 report | 100 | 99 | 0 | 1 |
| EXP-002 report | 102 | 102 | 0 | 0 |
| EXP-003 report | 185 | 184 | 0 | 1 |
| EXP-004 report | 176 | 176 | 0 | 0 |
| EXP-005 report | 63 | 63 | 0 | 0 |
| EXP-006 report | 82 | 81 | 1 | 0 |

**Untraced numbers, classified by hand.** DOI prefixes and article numbers (10.1002, 10.1016, 10.1103, 10.1145, 10.1287, 10.1680, 128701, 90030): bibliographic, not results. 10,626 (manuscript and CL-015): derived sum, listed under `DERIVED` in the manifest. Other derived values (about nine times; the 0.0045 margin; 2.3 percent; relative 1.1e-7) are traced to their stored operands in the manifest's `DERIVED` entry.

**Limit of the method.** The trace confirms that each displayed number equals some stored value at its precision; it does not by itself prove that the number is attached to the right quantity. For that, A4 recomputes the main estimates from raw tables, and Part C rebuilds 33 table rows (manuscript Tables 2 to 5, supplementary Tables S3 and S4) from the named `analysis.json` fields: 33 of 33 appear verbatim. The remaining tables (Table 1, S2, S5 to S7, S4.1, S4.2) were compared by hand with the fields named in the manifest. Small integers (100 or less: counts, grid sizes, section numbers) were checked by hand in the denominator check above.

## 3. External claims

| Claim | Source | Level | Finding |
|---|---|---|---|
| CL-E01 Braess example (flows 2, 2, 2; times 92 and 83; link costs) | Braess, Nagurney and Wakolbinger (2005); supernet page | read | Matches the literature review notes. |
| CL-E02 4/3 bound and unboundedness | Roughgarden and Tardos (2002), author preprint | read (abstract and introduction) | Labelled as preprint in the manuscript; journal wording not checked. |
| CL-E03 price of anarchy on city networks; closing streets | Youn et al. (2008) | **abstract only** | Labelled "abstract read" in the manuscript and EXP-003 report; nothing beyond the abstract is used. |
| CL-E04 Sioux Falls "not considered as a realistic one"; B = 0.15 assumed; 0.01 h units; academic-use terms | TNTP root README (2026-11-24); SiouxFalls/README.md (2026-11-25) | read | See finding F-3. |
| CL-E05 Wardrop, Beckmann et al., Frank and Wolfe, LeBlanc et al., Roughgarden (2004), Harker | Crossref or publisher metadata | metadata only | Cited for attribution only and labelled "metadata verified, text not read". No content statement rests on them. |

## 4. Findings and fixes

| Id | Finding | Fix |
|---|---|---|
| F-1 | CL-001 said "within 4.5e-16"; the stored largest difference is 4.44e-16 (reports say 4.4e-16). | Corrected to 4.4e-16. |
| F-2 | Row CL-008 of `research/claims_register.csv` had an unquoted comma in its limitations field, giving 8 fields instead of 7, so CSV readers misassigned it. | Field quoted; the register was rebuilt with the M4 columns (run id, config hash, figure or table, manuscript section). |
| F-3 | The quotation "not considered as a realistic one" (limitations item 1, EXP-006 report) had no recorded access entry; only the root README had been recorded as read. | SiouxFalls/README.md fetched at the pinned commit on 2026-11-25 (SHA-256 recorded in the literature review); the wording is exact. |
| F-4 | The registry still said "report pending" for all six experiments, and the EXP-001 and EXP-002 reports and limitations items 9 and 12 said that the owner had not decided on a 1e-10 rerun. Both were stale after D-015 and the owner's decision of 2026-11-25b. | Registry statuses, reports (version 1.1) and limitations updated. |
| F-5 | The draft manuscript stated an aggregate runtime ("under 40 minutes") that is not a stored number. | Replaced by stored per-experiment runtimes (second review pass). |
| F-6 | `research/publication/artifact_manifest.json` was still the M0 placeholder with no artifacts. | Built (24 entries). |
| F-7 | The two exploratory 1e-10 run manifests record `dirty: true`. The only uncommitted file at run time was the untracked analysis script, which the runner does not import; the configs were committed first (`01c2b4b`). | Disclosed in the reports, supplementary S3 and J-0022. |
| F-8 | No mismatch between any reported number and the raw outputs was found (A1 to A4). | None needed. |

## 5. Strength and scope of each conclusion

| Conclusion | Strength | Scope |
|---|---|---|
| EXP-003 primary (H0 rejected) | Confirmatory, preregistered, 100 instances, robust to S1 and S3 | 6x6 grid-v1 family, beta = 4, rho = 2; fails under beta = 1; below delta at rho = 1 |
| EXP-003 secondary (FF versus UE) | Descriptive | Both grid sizes, congested levels |
| EXP-004 compliance (H1 supported) | Confirmatory, but partly implied by the MIX construction | One compliance definition; capacity 1.0 confirmatory |
| EXP-005 incidence (H1 supported) | Confirmatory (optional); effects mostly small | 4x4 grids, rho = 2 |
| EXP-006 replication | Deterministic single comparison, small margin | One unrealistic test network |
| EXP-001, EXP-002 (contradicted) | Confirmatory verdicts; exploratory evidence points to solver tolerance | Braess network |
