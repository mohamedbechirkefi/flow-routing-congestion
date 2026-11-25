<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
<!-- Supplementary material to research/paper/manuscript.md. Status: independent research manuscript / preprint draft, not peer-reviewed. M4, 2026-11-25. Numbers come only from committed result files (research/publication/artifact_manifest.json). -->

# Supplementary material

## S1. Complete experimental matrix

| EXP | Status | Networks | Factors | Arms | Instances | Records (ok / nonconverged / failed) | Run id |
|---|---|---|---|---|---|---|---|
| EXP-001 | confirmatory, contradicted | Braess, with and without link e | demand 6 | FF, UE, SO | 1 (deterministic) | 6 / 0 / 0 | EXP-001-20261124T234532Z-846e8c0f |
| EXP-002 | confirmatory, contradicted | Braess, with and without link e | 48 demands 0.25 to 12.0, plus 27 fine-cell demands | FF, UE, SO | deterministic | 450 / 0 / 0 | EXP-002-20261124T234533Z-fcb88932 |
| EXP-003 | confirmatory, H0 rejected | grid 4x4 (seeds 1000-1099), 6x6 (2000-2099) | rho in {1, 2, 3}; S1 (1e-4, 1e-8, Frank-Wolfe), S2 (beta 1), S3 (absolute, share 0.10826) | FF, UE, SO | 100 per size | 2,745 / 155 / 0 | EXP-003-20261124T234531Z-6cbcaa47 |
| EXP-004 | confirmatory, H1 supported | grid 6x6 (2000-2099), rho 2 | c in {0, 0.25, 0.5, 0.75, 1} x capacity {0.8, 1.0, 1.2} | MIX(c), FF, SO | 100 | 2,100 / 0 / 0 | EXP-004-20261125T002235Z-7a7c2692 |
| EXP-005 | confirmatory (optional), H1 supported | grid 4x4 (1000-1099), rho 2 | each of 48 directed links removed | UE | 100 | 5,154 / 0 / 0 | EXP-005-20261124T234554Z-4051f409 |
| EXP-006 | confirmatory, gate passed, direction replicates | TNTP Sioux Falls | published demand, rho in {1, 2, 3}; S1 at 1e-8 | FF, UE, SO | 1 (deterministic) | 16 / 0 / 0 | EXP-006-20261124T234536Z-9a9669c8 |
| X-EXP-001-TOL1E-10 | **exploratory** (M4) | as EXP-001 | RG 1e-10 | FF, UE, SO | 1 | 6 / 0 / 0 | X-EXP-001-TOL1E-10-20261125T011841Z-ae793d0f |
| X-EXP-002-TOL1E-10 | **exploratory** (M4) | as EXP-002 | RG 1e-10 | FF, UE, SO | deterministic | 450 / 0 / 0 | X-EXP-002-TOL1E-10-20261125T011841Z-5acef701 |

All 155 nonconverged EXP-003 records are in the Frank-Wolfe reference cell (SO 93, UE 62). No record failed and no run was dropped or retried.

## S2. Extended tables

**Table S2.** EXP-003 primary cell (6x6, rho = 2, UE), from `research/experiments/EXP-003/analysis.json` (`primary`).

| Statistic | Value |
|---|---|
| Instances, excluded | 100, 0 |
| Median R(UE) | 0.02317 |
| Mean | 0.02575 |
| Quartiles | 0.01732 to 0.03160 |
| Range | 0.00386 to 0.06667 |
| One-sided 95% lower bound | 0.02134 |
| Two-sided 95% CI | [0.02075, 0.02559] |

**Table S3.** EXP-003 paired UE minus SO differences in fairness and p95 trip time (median [95% CI]; descriptive, not multiplicity-controlled).

| Size | rho | Gini of stretch | p95 trip time (min) |
|---|---|---|---|
| 4x4 | 1 | 0.00081 [0.00037, 0.00146] | -0.0004 [-0.0040, 0.0000] |
| 4x4 | 2 | 0.00472 [0.00314, 0.00635] | -0.0273 [-0.0561, 0.0002] |
| 4x4 | 3 | 0.00183 [0.00042, 0.00654] | -0.1296 [-0.2089, -0.0143] |
| 6x6 | 1 | 0.00055 [0.00034, 0.00119] | 0.0000 [-0.0002, 0.0002] |
| 6x6 | 2 | 0.00408 [0.00279, 0.00488] | 0.0000 [-0.0171, 0.0263] |
| 6x6 | 3 | 0.00472 [0.00181, 0.00595] | 0.0360 [-0.0223, 0.0954] |

**Table S4.** EXP-004 consecutive paired median differences (one-sided 95% lower bound; two-sided 95% CI).

| Step | Capacity 0.8 | Capacity 1.0 (confirmatory) | Capacity 1.2 |
|---|---|---|---|
| MIX(0) - MIX(0.25) | 0.00510 (0.00460; [0.00447, 0.00581]) | 0.00415 (0.00343; [0.00322, 0.00489]) | 0.00295 (0.00204; [0.00194, 0.00367]) |
| MIX(0.25) - MIX(0.5) | 0.00684 (0.00592; [0.00581, 0.00770]) | 0.00539 (0.00442; [0.00425, 0.00656]) | 0.00386 (0.00342; [0.00333, 0.00493]) |
| MIX(0.5) - MIX(0.75) | 0.00964 (0.00840; [0.00828, 0.01077]) | 0.00725 (0.00652; [0.00636, 0.00821]) | 0.00571 (0.00470; [0.00447, 0.00667]) |
| MIX(0.75) - MIX(1) | 0.00868 (0.00816; [0.00809, 0.00950]) | 0.00496 (0.00445; [0.00432, 0.00600]) | 0.00294 (0.00255; [0.00251, 0.00338]) |

**Table S5.** EXP-004 compliant to non-compliant mean trip-time ratio (median [95% CI]).

| Arm | Capacity 0.8 | Capacity 1.0 | Capacity 1.2 |
|---|---|---|---|
| MIX(0.25) | 1.0058 [1.0050, 1.0071] | 1.0051 [1.0043, 1.0055] | 1.0037 [1.0033, 1.0046] |
| MIX(0.5) | 1.0091 [1.0080, 1.0103] | 1.0076 [1.0066, 1.0088] | 1.0062 [1.0052, 1.0076] |
| MIX(0.75) | 1.0164 [1.0141, 1.0178] | 1.0132 [1.0120, 1.0144] | 1.0109 [1.0093, 1.0116] |

**Table S6.** EXP-005 incidence of Braess links (n = 100 instances).

| Threshold | Instances | Wilson 95% | Links in total | Median links per instance |
|---|---|---|---|---|
| 1e-4 (primary) | 77 | [0.678, 0.842] | 177 | 1.5 |
| 1e-4, confirmed at RG 1e-8 | 77 | [0.678, 0.842] | 177 | 1.5 |
| 1e-3 (sensitivity) | 67 | [0.573, 0.754] | 128 | 1.0 |

**Table S7.** EXP-006 sweeps (final RG) per arm and mean trip time (0.01 h).

| Level | Total demand | UE sweeps (RG) | SO sweeps (RG) | Mean trip time UE / SO / FF |
|---|---|---|---|---|
| rho = 1 | 62,301.9 | 2 (8.3e-7) | 4 (5e-8) | 8.953 / 8.911 / 8.966 |
| rho = 2 | 124,603.8 | 4 (2.4e-7) | 40 (9.5e-7) | 9.452 / 9.317 / 11.345 |
| rho = 3 | 186,905.7 | 43 (9.3e-7) | 29 (8.7e-7) | 10.507 / 10.199 / 21.652 |
| published (rho 5.788) | 360,600 | 83 (1e-6) | 54 (9e-7) | 20.743 / 19.951 / 186.765 |

## S3. Configurations and hashes

| EXP | Config file | Canonical config hash (run id suffix) | Protocol SHA-256 | Code revision | Manifest dirty flag |
|---|---|---|---|---|---|
| EXP-001 | `experiments/EXP-001.json` | `846e8c0f758caa6f...` | `c431c303...d4c7` | `8dfc66c` | false |
| EXP-002 | `experiments/EXP-002.json` | `fcb88932cbe551ae...` | `262a029d...7963` | `8dfc66c` | false |
| EXP-003 | `experiments/EXP-003.json` | `6cbcaa47d6d0bfb8...` | `b047a0b1...3eba` | `8dfc66c` | true (D-014) |
| EXP-004 | `experiments/EXP-004.json` | `7a7c26921a0225fc...` | `37e8e328...de22` | `8dfc66c` | true (D-014) |
| EXP-005 | `experiments/EXP-005.json` | `4051f409dd967b2a...` | `e8cb9380...9359` | `8dfc66c` | true (D-014) |
| EXP-006 | `experiments/EXP-006.json` | `9a9669c8d4189347...` | `efbca04a...37f2` | `8dfc66c` | false |
| X-EXP-001-TOL1E-10 (exploratory) | `experiments/exploratory/X-EXP-001-TOL1E-10.json` | `ae793d0fe516436c...` | n/a | `01c2b4b` | true (untracked analysis script only) |
| X-EXP-002-TOL1E-10 (exploratory) | `experiments/exploratory/X-EXP-002-TOL1E-10.json` | `5acef70144c3e63e...` | n/a | `01c2b4b` | true (untracked analysis script only) |

Full hashes: `research/freeze.json`, decision D-011 and D-012 FREEZE lines, and each run's `run_manifest.json`. Umbrella protocol SHA-256 `9f629b07b4c8e240c41236ff5c0cfd1abfde9681452c9f662f0175f316ecb97d`.

## S4. Robustness and exploratory results

Confirmatory sensitivity results are in manuscript Table 3 (EXP-003 S1 to S3) and Section 5.6 (EXP-006 S1). The following are **exploratory**, defined at M4 after the confirmatory results were seen, and change no frozen verdict.

**S4.1 Braess exact checks at RG <= 1e-10** (J-0022; `results/exploratory/X-EXP-00{1,2}-TOL1E-10-*/exploratory_analysis.json`).

| Quantity | Confirmatory (RG 1e-6) | Exploratory (RG 1e-10) | Analytic |
|---|---|---|---|
| EXP-001 UE with e: TSTT | 551.9999380904 | 552.0000000075 | 552 |
| EXP-001 largest absolute difference | 6.19e-5 | 7.53e-9 | |
| EXP-001 UE with e: sweeps, final RG | 6, 7.29e-8 | 9, 1.77e-11 | |
| EXP-002 lower boundary | 2.580645161290321 | 2.580645161290321 | 80/31 |
| EXP-002 middle boundary | 3.6363548780120354 | 3.63636363566172 | 40/11 |
| EXP-002 upper boundary | 8.888899966300295 | 8.888888890418269 | 80/9 |
| EXP-002 sign agreement | 75 of 75 | 75 of 75 | |
| EXP-002 largest per-point UE time error | 1.06e-3 (d = 3.64) | 3.37e-6 (d = 3.64) | |
| Frozen analysis verdict | contradicted | reproduced / derivation confirmed | |

**S4.2 Confounder checks from committed tables** (J-0023; `results/exploratory/M4-confounder-checks.json`).

| Check | Result |
|---|---|
| Instances with R(UE) > 0.01, 6x6 rho = 2 (primary) | 90 of 100 |
| Same, S1 RG 1e-4 / 1e-8 | 90 / 90 of 100 |
| Same, S2 beta = 1 | 0 of 100 |
| Same, S3 absolute calibration | 86 of 100 |
| Same, 4x4 rho = 1 / 2 / 3 | 17 / 94 / 97 of 100 |
| Same, 6x6 rho = 1 / 3 | 3 / 99 of 100 |
| Spearman, R(UE) vs UE flow-weighted v/c (primary cell, n = 100) | 0.653 |
| Spearman, R(UE) vs UE share of links over capacity | 0.674 |
| Spearman, R(UE) vs UE max v/c | 0.638 |
| EXP-005 instances with a removal lowering TSTT_UE by > 1e-2 / > 1e-3 | 17 / 67 of 100 |
| EXP-005 median relative effect over the 177 flagged links | 0.0030 |
| EXP-005 flagged links with effect > 1e-2 | 25 of 177 |

## S5. Experiment reports

| EXP | Report | Reproduction |
|---|---|---|
| EXP-001 | `research/experiments/EXP-001/report.md` | `research/experiments/EXP-001/reproduction.md` |
| EXP-002 | `research/experiments/EXP-002/report.md` | `research/experiments/EXP-002/reproduction.md` |
| EXP-003 | `research/experiments/EXP-003/report.md` | `research/experiments/EXP-003/reproduction.md` |
| EXP-004 | `research/experiments/EXP-004/report.md` | `research/experiments/EXP-004/reproduction.md` |
| EXP-005 | `research/experiments/EXP-005/report.md` | `research/experiments/EXP-005/reproduction.md` |
| EXP-006 | `research/experiments/EXP-006/report.md` | `research/experiments/EXP-006/reproduction.md` |

Report PDFs are generated locally at M6 and are not claimed to exist before then.

## S6. Deviations and owner decisions

| Id | Date | What | Effect on results |
|---|---|---|---|
| C4 (freeze record) | 2026-11-24 | Exploratory primary-cell analogue values seen before the freeze (median 0.02349, n = 20, disjoint seeds) | Disclosed; delta, primary cell and rule were fixed earlier (commit `91ecb92`) |
| D-012 | 2026-11-25 | Interpretation rules fixed before confirmatory output; EXP-005 config added before EXP-005 data | None; rules applied as fixed |
| D-013 | 2026-11-25 | A test ran the EXP-005 config once into a temporary directory before the official run; output not inspected | None; solves are deterministic |
| D-014 | 2026-11-25 | Dirty flag on three manifests (untracked outputs only); sensitivity-figure code fixed after EXP-003 output; reports not written at run time | No estimand, interval or table changed |
| D-015 | 2026-11-25 | Owner approved the experiment reports, written from committed results only | None |
| Protocol/config mismatch | 2026-11-24 freeze | EXP-001 protocol states RG 1e-10; frozen EXP-001 and EXP-002 configs use 1e-6 | Both exact checks contradicted under the frozen rule |
| Owner decision (2026-11-25b, item 3) | 2026-11-25 | Frozen EXP-001/EXP-002 verdicts stand; 1e-10 rerun reported as exploratory; EXP-004 link-flow sensitivity not added | Exploratory S4.1 added beside the verdicts |
| D-016 | 2026-11-25 | M4 records: exploratory checks, evidence audit, second review pass | See `research/decision_log.md` |
