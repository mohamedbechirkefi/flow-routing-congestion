<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-001: Analytic Braess example, exact reproduction (report)

## 1. Identification

- Experiment EXP-001. Report date 2026-11-25. Report version 1.1 (M4: exploratory 1e-10 check added beside the frozen verdict; version 1.0 was the M3 report).
- **Status: CONFIRMATORY, complete (6 of 6 records). Verdict under the frozen rule: CONTRADICTED.** One of six arm and network combinations lies outside the 1e-6 tolerance.
- Authorship: Mohamed Bechir Kefi, independent researcher (owner-approved, C3; owner, 2026-11-26, decision sheet, B3). An AI research and development assistant (Claude) is disclosed and is not an author.
- Protocol `research/experiments/EXP-001/protocol.md`, sha256 `c431c303e5d12017b157ec37a722b527492c77a99ab49d6c72029d965bd8d4c7`. Umbrella `research/protocol.md` v1.0, sha256 `9f629b07b4c8e240c41236ff5c0cfd1abfde9681452c9f662f0175f316ecb97d` (frozen 2026-11-24, D-011).
- Config `experiments/EXP-001.json`, file sha256 `605ee995073ff319de450b9aff00bf1125a90ce1ad0849a053f5f8422d537aae`; canonical config hash `846e8c0f758caa6f4993798a0b18087b618054b6da44e727a06381cfeb3be6b4`.
- Provenance revision `8dfc66ca5c9635e160f38526843941716aadacd0`. The manifest records `dirty: false`.
- Report composed under the owner's decision of 2026-11-25 (approvals item 4, D-015), from committed results only.

## 2. Executive summary

**Question.** Does the FLOW engine reproduce the published Braess example at demand 6 exactly, for the FF, UE and SO arms, with and without the added link e?

**Method.** One deterministic run of the frozen config: gradient projection, stopping at relative gap `RG <= 1e-6` or 20,000 sweeps. The results are compared with the analytic values of protocol item 5 at an absolute tolerance of 1e-6 (D-012, fixed before the run).

**Outcome.**

- Five of six combinations match to within 4.4e-16.
- The UE with link e stopped after 6 sweeps at `RG = 7.29e-8`:

| Quantity | Computed | Analytic | Difference |
|---|---|---|---|
| TSTT | 551.99993809 | 552 | 6.19e-5 |
| Mean trip time | 91.99998968 | 92 | 1.03e-5 |
| Zigzag path flow | 1.99999845 | 2 | 1.55e-6 |

The frozen verdict is therefore "contradicted".

**Principal caveat, disclosed.** The protocol text (item 5) states a relative gap of 1e-10 "for this run". The frozen config `experiments/EXP-001.json` uses 1e-6, and the run was made with the frozen config. The 1e-10 run and the item 17 sensitivity (1e-6 versus 1e-10) have no frozen config. The owner decided on 2026-11-25 ("Approve all recommendations, push then next", item 3) that the frozen verdict stands and that a 1e-10 rerun is reported beside it as a labelled exploratory check (section 8, "Exploratory check").

**Exploratory check (M4, J-0022), beside the verdict.** The frozen config rerun with only `solver.tol` changed to 1e-10 and analysed with the frozen analysis code: largest difference 7.53e-9, frozen analysis result "reproduced". This is exploratory and post hoc; it does not change the frozen verdict above.

## 3. Research rationale and literature

- Braess, Nagurney and Wakolbinger (2005), the English translation of Braess (1968), was read. It gives equilibrium path flows of 2, 2 and 2 and a travel time of 92 with link e at total demand 6.
- The supernet Braess page was read. It gives the link costs `10f_a`, `f_b + 50`, `f_c + 50`, `10f_d` and `f_e + 10`, demand 6, and a time of 83 without the link.

This experiment checks the engine on the one network where every arm has a closed form, before the grid experiments rely on it.

## 4. Hypotheses and operational definitions

Predictions (protocol item 5):

| Network | Arm | Path flows | Time | TSTT |
|---|---|---|---|---|
| without e | UE | 3, 3 | 83 | 498 |
| with e | UE | 2, 2, 2 | 92 | 552 |
| without e | SO | 3, 3 | | 498 |
| with e | SO | 3, 3 (link e unused) | | 498 |
| with e | FF | all 6 units on s-A-B-t | 136 | 816 |
| without e | FF | all 6 units on s-A-t | 116 | 696 |

- FF without e has a tie between the two outer paths. It is broken to the lexicographically smallest node sequence, s-A-t.
- `TSTT = sum_e x_e t_e(x_e)`, in the example's abstract units.
- Contradiction: any computed value differing from the analytic value by more than 1e-6. D-012 fixed before the run that this is an absolute difference.

## 5. Methodology

- **Network.** Four nodes (s, A, B, t) with the linear costs above (`flow.generators.braess_network`).
- **UE and SO.** Path-based gradient projection, the solver of record under amendment A1. Stopping rule `RG <= 1e-6` or 20,000 sweeps.
- **FF.** All-or-nothing loading on free-flow times with the lexicographic tie rule.
- **Seeds.** None; the experiment is deterministic.
- **Hardware and software.** Apple M1 Pro, macOS 15.3.1, Python 3.12.1, numpy 2.5.4.
- **Analysis.** `flow.confirmatory.analyse_exp001`, written and tested before the run (commit `5108a16`, D-012). No statistics.

## 6. Implementation verification

- The full test suite passed before the confirmatory runs (138 passed, 2026-11-25).
- The exploratory smoke run J-0013 (same network, same solver) and the metric validation J-0015 showed the same UE-with-link residual before any confirmatory run.
- In J-0015 the other metric checks passed:
  - TSTT and mean trip time recomputed from the link flows: error 0.0.
  - R(SO) = 0.
  - Flow conservation within 2.3e-13.
- No rule was changed after the smoke run.

## 7. Execution record

- Command: `nice -n 10 .venv/bin/flow run EXP-001 --quiet` (log `results/raw/logs/worker-A.log`).
- Run id `EXP-001-20261124T234532Z-846e8c0f`.
- Started 2026-11-24T23:45:32Z and finished 23:45:33Z (UTC). Peak RSS 34 MiB.
- Records: 6 planned and 6 written: 6 ok, 0 nonconverged, 0 failed. No run was dropped or retried.
- Deviations: none in execution. The protocol/config tolerance mismatch is described in section 2. The session-level deviations of D-013 and D-014 do not concern this run.

## 8. Results

| Network | Arm | Sweeps | Final RG | Quantity | Computed | Analytic | Absolute difference | Pass |
|---|---|---|---|---|---|---|---|---|
| without e | UE | 1 | 0 | TSTT; time; flows | 498; 83; 3, 3 | 498; 83; 3, 3 | 0 | yes |
| without e | SO | 1 | 0 | TSTT; flows | 498; 3, 3 | 498; 3, 3 | 0 | yes |
| without e | FF | 0 | n/a | TSTT; time; flow s-A-t | 696; 116; 6 | 696; 116; 6 | 0 | yes |
| with e | SO | 2 | 0 | TSTT; flow on e; flows | 498; 0; 3, 3 | 498; 0; 3, 3 | 4.4e-16 | yes |
| with e | FF | 0 | n/a | TSTT; time; flow s-A-B-t | 816; 136; 6 | 816; 136; 6 | 0 | yes |
| with e | UE | 6 | 7.29e-8 | TSTT | 551.9999380904 | 552 | 6.19e-5 | **no** |
| with e | UE | | | mean trip time | 91.9999896817 | 92 | 1.03e-5 | **no** |
| with e | UE | | | max path time | 91.9999930352 | 92 | 6.96e-6 | **no** |
| with e | UE | | | flow s-A-B-t | 1.9999984523 | 2 | 1.55e-6 | **no** |
| with e | UE | | | flow s-A-t; flow s-B-t | 2.0000007739 each | 2 | 7.74e-7 | yes |

- Source: `research/experiments/EXP-001/analysis.json`, field `max_abs_diff` = 6.19e-5.
- No figure: the six exact comparisons are shown in full in the table, and no interval applies.

**Exploratory check at `RG <= 1e-10` (M4, J-0022; not confirmatory).**

- Authority: owner, 2026-11-25, "Approve all recommendations, push then next", item 3.
- Config `experiments/exploratory/X-EXP-001-TOL1E-10.json`: the frozen config with only `experiment_id`, `label`, `description` and `solver.tol` (1e-10) changed; committed (`01c2b4b`) before the run.
- Run `X-EXP-001-TOL1E-10-20261125T011841Z-ae793d0f`, canonical config hash `ae793d0fe516436cadbfe736ce002825b0be8b2538a7f4bd26522f466f327dbe`; 6 ok. The manifest records `dirty: true` because the analysis script `scripts/analyse_exploratory_tol.py` was untracked at run time; the runner does not import it.
- Analysis: `scripts/analyse_exploratory_tol.py` calls the frozen `flow.confirmatory.analyse_exp001` unchanged. Output `results/exploratory/X-EXP-001-TOL1E-10-20261125T011841Z-ae793d0f/exploratory_analysis.json`.

| Quantity (UE with e) | Confirmatory, RG 1e-6 | Exploratory, RG 1e-10 | Analytic |
|---|---|---|---|
| Sweeps, final RG | 6, 7.29e-8 | 9, 1.77e-11 | |
| TSTT | 551.9999380904 | 552.0000000075 | 552 |
| Largest absolute difference (all six combinations) | 6.19e-5 | 7.53e-9 | |
| Frozen analysis result | contradicted | reproduced | |

The exploratory rerun meets the 1e-6 rule. It was defined after the confirmatory result was seen and **does not replace the frozen verdict**, which stays "contradicted".

**Expected versus observed.**

- Expected: all values within 1e-6.
- Observed: the FF and SO arms and the UE without link e are exact. The UE with link e reproduces the published Braess effect (83 without e, 91.99999 with e) but misses the 1e-6 tolerance by a factor of about 60 in TSTT.

## 9. Interpretation

- **Measured.** Every FF and SO value and the UE without link e are reproduced exactly. The UE with link e is reproduced to a relative TSTT error of 6.19e-5 / 552.
- **Verdict under the frozen rule.** Contradicted. The result is reported as such.
- **Model-dependent reading.** The residual is consistent with the solver stopping rule rather than with an implementation error, for three reasons:
  - the run stopped as soon as `RG` fell below 1e-6;
  - the outer path flows (2.0000008 each) and the zigzag flow (1.9999985) sit on either side of 2 and sum to the demand of 6;
  - the same stopping behaviour appears in EXP-002.
- **What this run cannot exclude.** A small implementation error that shifts the equilibrium cannot be excluded by this run alone. A run at `RG <= 1e-10`, as protocol item 5 intended, would discriminate.
- **Exploratory evidence (M4).** The owner-approved exploratory rerun at `RG <= 1e-10` brings every value within 7.53e-9 of the analytic one. This favours the solver-tolerance reading over an implementation error. It is post hoc evidence and does not change the frozen verdict.

## 10. Threats to validity

- **Internal.** The protocol (1e-10) and its frozen config (1e-6) disagree on the solver tolerance. The absolute reading of the 1e-6 rule (D-012) is strict for a solver that stops at a relative gap.
- **Construct.** The path flows are those maintained by gradient projection, which is one valid decomposition.
- **External.** One textbook network. Nothing transfers to other networks from this experiment.
- **Statistical.** Not applicable (deterministic).

## 11. Conclusion and next experiment

- The registered hypothesis (exact reproduction within 1e-6) is contradicted for the UE with link e, by 6.19e-5 in TSTT, at the frozen tolerance.
- All other combinations are exact, and the published 83 to 92 effect is reproduced to the solver tolerance.
- The owner decided (2026-11-25b, item 3) that the frozen verdict stands and that the 1e-10 rerun is reported as exploratory; it meets the rule (section 8). A confirmatory check at the intended tolerance would need a new registered protocol.

## 12. Reproduction appendix

See `research/experiments/EXP-001/reproduction.md`. References:

- Braess, D., Nagurney, A., Wakolbinger, T. (2005). On a paradox of traffic planning. Transportation Science 39(4), 446-450. doi:10.1287/trsc.1050.0127 (read).
- Supernet Braess paradox page, https://supernet.isenberg.umass.edu/facts/braess.html (read 2026-11-24).
