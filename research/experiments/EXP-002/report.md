<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-002: Braess demand sweep, when does the added link hurt? (report)

## 1. Identification

- Experiment EXP-002. Report date 2026-11-25. Report version 1.0.
- **Status: CONFIRMATORY, complete (450 of 450 records, 75 demand points). Verdict under the frozen rule: CONTRADICTED.** Two of three computed regime boundaries lie outside 1e-6; the lower paradox boundary and the paradox sign at all 75 points agree with the derivation.
- Authorship: Mohamed Bechir Kefi (owner-approved). An AI assistant (Claude) is disclosed and is not an author.
- Protocol sha256 `262a029df24996f1a82d8a2b517572af2765bec0a6551a3b911d00914a567963`. Umbrella protocol v1.0, sha256 `9f629b07...b97d`.
- Config `experiments/EXP-002.json`, file sha256 `7b046213b1f1b2de7971b2b2740bf3c79526518c8cebae8d670a91aa91a4d877`; canonical hash `fcb88932cbe551ae87741488096fab36a2a071684088c075a47c887bb4fef3be`.
- Provenance revision `8dfc66ca5c9635e160f38526843941716aadacd0`. The manifest records `dirty: false`.
- Composed under owner approvals item 4 (D-015) from committed results only.

## 2. Executive summary

**Question.** For which total demands d does adding link e raise UE travel time in the Braess network?

**Method.** Frozen sweep: 48 demands from 0.25 to 12.0 in steps of 0.25, plus a fine cell of 27 demands at a 0.05 step around the predicted boundaries. Each point is solved with and without link e for the FF, UE and SO arms by gradient projection at `RG <= 1e-6`. Boundaries are computed from least-squares lines through the points strictly inside each predicted regime, with tolerance 1e-6 (D-012).

**Outcome.**
- At all 75 points the sign of `Delta(d) = TSTT_UE(with e) - TSTT_UE(without e)` agrees with the predicted interval (80/31, 80/9).
- Computed paradox points of the main sweep: 2.75 to 8.75.
- Boundaries:

| Boundary | Computed | Analytic | Difference | Within 1e-6 |
|---|---|---|---|---|
| Lower paradox boundary | 2.580645161290321 | 80/31 | 1.3e-15 | yes |
| Upper boundary | 8.888899966 | 80/9 | 1.1e-5 | no |
| Middle boundary | 3.636354878 | 40/11 | 8.8e-6 | no |

The frozen verdict is therefore "contradicted".

**Principal caveat.** The failing residuals are of the size the frozen solver tolerance (`RG <= 1e-6`) allows. The same protocol/config tolerance issue affects EXP-001: the EXP-001 protocol states a relative gap of 1e-10 and its frozen config uses 1e-6. EXP-002's frozen config also uses 1e-6, while its contradiction threshold is 1e-6. A tighter rerun is an owner decision that has not been made.

## 3. Research rationale and literature

Braess et al. (2005) and the supernet page (both read) give only the point d = 6. The interval was derived by the assistant on 2026-11-24 and is not taken from a source. It was checked by exact rational unit tests before the freeze (`tests/test_braess_interval.py`).

## 4. Hypotheses and operational definitions

UE path time with link e, by regime:

| Regime | UE time with e |
|---|---|
| d <= 40/11 | 21d + 10 |
| 40/11 <= d <= 80/9 | (31d + 1010)/13 |
| d >= 80/9 | 5.5d + 50 |

- Without link e the UE time is 5.5d + 50.
- Prediction: the link raises UE time exactly for d in (80/31, 80/9), about (2.581, 8.889).
- Estimand: `Delta(d)` over the grid, and the set where `Delta > 0`.
- Contradiction: computed boundaries or paradox interval deviating by more than 1e-6.
- Operationalisation fixed in D-012 before the run:
  - boundaries come from straight-line fits;
  - a point is a paradox point when `Delta(d) > 1e-6 x TSTT_UE(without e)`.

## 5. Methodology

- Network as in EXP-001, the solver of record, deterministic, no seeds.
- Main sweep: 48 values. Fine cell: 27 values at 2.38 to 2.78, 3.44 to 3.84 and 8.69 to 9.09 in steps of 0.05. The fine cell is the protocol's item 17 sensitivity.
- Hardware: Apple M1 Pro.
- Analysis: `flow.confirmatory.analyse_exp002`, written before the run.
- Boundaries:
  - lower: intersection of the fitted lines through UE time with e (points d < 40/11) and UE time without e (all points);
  - upper: root of the fitted zigzag-path flow over 40/11 < d < 80/9;
  - middle: root of the fitted outer-path flow over the same range.

## 6. Implementation verification

- The test suite passed before the runs (138 passed).
- Exact rational tests of the derivation were in place before the freeze.
- The smoke and metric validation (J-0013, J-0015) passed the metric checks.

## 7. Execution record

- Command: `nice -n 10 .venv/bin/flow run EXP-002 --quiet`.
- Run id `EXP-002-20261124T234533Z-fcb88932`.
- Started 2026-11-24T23:45:33Z and finished 23:45:36Z (UTC). Peak RSS 36 MiB.
- Records: 450 planned (75 demands x 2 networks x 3 arms) and 450 written: 450 ok, 0 nonconverged, 0 failed. No run was dropped or retried.
- Deviations in execution: none. Gap: no run at a tighter tolerance exists, because there is no frozen config for one.

## 8. Results

| Check | Computed | Analytic | Absolute difference | Pass |
|---|---|---|---|---|
| Lower paradox boundary | 2.580645161290321 | 80/31 = 2.5806451612903225 | 1.3e-15 | yes |
| Upper boundary (link e falls unused) | 8.888899966300295 | 80/9 = 8.88888888888889 | 1.11e-5 | **no** |
| Middle boundary (outer paths used) | 3.6363548780120354 | 40/11 = 3.6363636363636362 | 8.76e-6 | **no** |
| Paradox sign, all 75 points | agrees at 75 of 75 | | | yes |

- Fit residuals (largest absolute):

| Fit | Residual |
|---|---|
| UE time with e, low regime | 1.8e-14 |
| UE time without e | 2.8e-14 |
| Zigzag flow, middle regime | 5.96e-5 |
| Outer flow, middle regime | 3.07e-5 |

- Largest per-point UE time error: 1.06e-3, at d = 3.64 in the fine cell, just above 40/11. There, computed `Delta = 59.5130` against an analytic 59.5224. At d = 4.0 the time error is 3.37e-4.
- Figure: `figures/exp002_sweep.png`.
  - Caption: "UE path time with and without link e against total demand (left; lines analytic, markers computed) and Delta(d) = TSTT_UE(with e) - TSTT_UE(without e) (right), with the predicted paradox interval (80/31, 80/9) shaded. Deterministic: no intervals."
  - Alt text: "Two panels; computed points lie on the analytic curves; Delta is positive exactly inside the shaded band."
- Full per-point values: `analysis.json` (`points`).

**Expected versus observed.**
- Expected: all three boundaries within 1e-6, and the sign agreeing everywhere.
- Observed: the sign agrees everywhere and the lower boundary is exact. The two boundaries that come from the middle regime, where UE uses three paths, are off by about 1e-5.

## 9. Interpretation

- **Measured.** The direction and location of the paradox agree with the derivation at every sweep point. The lower boundary, where the solver finds an exact corner solution, is reproduced to machine precision.
- **Frozen verdict.** Contradicted, because two boundaries miss 1e-6. The result is reported as such.
- **Model-dependent reading.** In the middle regime the solver stops at `RG <= 1e-6` with path-flow residuals of order 1e-5 (fit residuals of 3e-5 to 6e-5). The boundary errors are of that size, and the error grows near the regime change at 40/11 (d = 3.64). This pattern fits solver tolerance rather than a wrong derivation, but this run cannot prove that. A tighter-tolerance rerun would decide, and it is the owner's call.

## 10. Threats to validity

- **Internal.** The frozen tolerance is of the same order as the contradiction threshold, so the verdict partly measures the solver tolerance. Boundary estimates depend on the fitted points chosen in D-012.
- **Construct.** Regime boundaries are inferred from a discrete sweep and fitted lines, not solved exactly.
- **External.** One textbook network.
- **Statistical.** Not applicable (deterministic).

## 11. Conclusion and next experiment

- Adding link e raises UE travel time at exactly the predicted sweep points (2.75 to 8.75 in the main sweep) and at none outside.
- The lower paradox boundary 80/31 is reproduced to 1.3e-15.
- Under the frozen rule the registered hypothesis is contradicted, because the upper (80/9) and middle (40/11) boundaries miss 1e-6 by about 1e-5.
- Follow-up, for the owner: rerun at `RG <= 1e-10`, together with EXP-001.

## 12. Reproduction appendix

See `reproduction.md`. References as in EXP-001.
