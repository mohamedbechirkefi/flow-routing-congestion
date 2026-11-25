<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Claims audit

Each row of `research/claims_register.csv` was checked on 2026-11-25 (M4) against its raw result or verified source: number, denominator, unit, precision, uncertainty, sample count and scope. Method and full findings: `research/publication/evidence_audit.md`. Every claim in the manuscript has a row; claims without a row were removed or qualified during M4 (none of the M4 manuscript statements needed removal; the aggregate runtime of the draft was replaced, see `review_pass_2.md` section 3).

| claim_id | Checked against | Result | Checked on |
|---|---|---|---|
| CL-001 | EXP-001 `analysis.json` (`checks`, `max_abs_diff`); raw `metrics.csv` | Pass after fix F-1 (4.5e-16 corrected to 4.4e-16); 6 records; absolute tolerance 1e-6 | 2026-11-25 |
| CL-002 | EXP-002 `analysis.json` (`boundaries`, `sign_agreement_all_points`, `max_time_err`); 450 records, 75 points | Pass | 2026-11-25 |
| CL-003 | EXP-003 `analysis.json` (`primary`); median, mean and n recomputed from raw (A4) | Pass; n = 100, 0 excluded; percentile bootstrap, 10,000 resamples | 2026-11-25 |
| CL-004 | EXP-003 `analysis.json` (`sensitivity`); S1 and S3 medians recomputed from raw (A4) | Pass; Frank-Wolfe n = 7 stated | 2026-11-25 |
| CL-005 | EXP-003 `analysis.json` (`sensitivity.S2-beta1`); recomputed (A4) | Pass | 2026-11-25 |
| CL-006 | EXP-003 `analysis.json` (`per_cell`); R(FF) medians recomputed (A4) | Pass; descriptive, no test | 2026-11-25 |
| CL-007 | EXP-004 `analysis.json` (`per_scale.1.0`); medians recomputed (A4) | Pass; one-sided lower bounds as fixed in D-012 | 2026-11-25 |
| CL-008 | EXP-005 `analysis.json` (`incidence`, `per_instance`) | Pass after fix F-2 (CSV row malformed); n = 100 instances, 177 links | 2026-11-25 |
| CL-009 | EXP-006 `analysis.json` (`validation_gate`, `replication`, `levels`); R(UE) at rho 2 recomputed (A4) | Pass; deterministic, no interval; units 0.01 h | 2026-11-25 |
| CL-010 | `results/exploratory/X-EXP-00{1,2}-TOL1E-10-*/exploratory_analysis.json` | Pass; labelled exploratory | 2026-11-25 |
| CL-011 | `results/exploratory/M4-confounder-checks.json` | Pass; labelled exploratory and correlational | 2026-11-25 |
| CL-012 | `results/exploratory/M4-confounder-checks.json` (`exp005_materiality`) | Pass; labelled exploratory | 2026-11-25 |
| CL-013 | EXP-006 `analysis.json` (`levels.S1-tol1e-8`) | Pass | 2026-11-25 |
| CL-014 | EXP-004 `analysis.json` (`compliant_to_follower_time_ratio`, `identity_MIX0_vs_EXP003_UE`) | Pass | 2026-11-25 |
| CL-015 | Six `analysis.json` (`n_records`, `status_counts`); EXP-003 `run_manifest.json`; A3 recount | Pass; 10,626 is a derived sum | 2026-11-25 |
| CL-016 | EXP-003 `analysis.json` (`per_cell` paired Gini and p95); Part C row check | Pass; descriptive | 2026-11-25 |
| CL-E01 | Braess et al. (2005) and supernet page (read 2026-11-24) | Pass | 2026-11-25 |
| CL-E02 | Roughgarden and Tardos (2002) author preprint (abstract and introduction read) | Pass; preprint level stated | 2026-11-25 |
| CL-E03 | Youn et al. (2008) arXiv abstract | Pass; marked abstract-only | 2026-11-25 |
| CL-E04 | TNTP root README (2026-11-24) and SiouxFalls/README.md (2026-11-25) | Pass after fix F-3 (access now recorded) | 2026-11-25 |
| CL-E05 | Crossref and publisher metadata | Attribution only; no content claim | 2026-11-25 |
