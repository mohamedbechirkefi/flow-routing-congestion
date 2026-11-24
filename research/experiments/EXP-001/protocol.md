<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-001: Analytic Braess example, exact reproduction

**Status: protocol v1.0, FROZEN (owner-approved 2026-11-24, round 2), not yet run.** Amendments before the freeze: umbrella `research/protocol.md` section 15. Umbrella protocol: `research/protocol.md`.

1. **Question.** Does the FLOW engine reproduce the published Braess example exactly for the FF, UE and SO arms, with and without the added link?
2. **Mechanism.** Under UE, each traveller ignores the delay they impose on others. The added link offers a privately cheaper path that loads the two congestible links `a` and `d`, raising every traveller's time.
3. **Rationale (verified sources).** Braess, Nagurney and Wakolbinger (2005), read: equilibrium path flows 2, 2, 2 and time 92 with the link at total flow 6. Supernet Braess page, read: link costs `10f_a`, `f_b + 50`, `f_c + 50`, `10f_d`, `f_e + 10`, demand 6, time 83 without the link.
4. **Competing explanations for a mismatch.** Implementation bug; solver not converged; wrong tie-breaking for FF; numeric tolerance.
5. **Hypotheses (deterministic).** Predictions (from the sources, and hand-derived by the assistant for SO and FF, to be checked by exact rational tests):
   - UE without link: path flows 3, 3; path time 83; TSTT 498.
   - UE with link: path flows 2, 2, 2; path time 92; TSTT 552.
   - SO with link: link e unused, path flows 3, 3; TSTT 498. SO without link: TSTT 498.
   - FF with link: all 6 units on path a-e-d (free-flow time 10); path time 136; TSTT 816.
   - FF without link: both paths have free-flow time 50; tie broken to the lexicographically smallest node sequence; path time 116; TSTT 696 (depends on the tie rule, stated as such).
   - Contradiction: any computed value differing from these by more than `1e-6` (relative gap `1e-10` for this run).
6. **Estimand.** Exact equality of computed and analytic values within tolerance.
7. **Unit and scope.** One deterministic network; no seeds.
8. **Variables.** Independent: arm (FF, UE, SO), link e present or absent. Dependent: path flows, path times, TSTT, R.
9. **Treatment and control.** Treatment: network with link e. Control: network without e.
10. **Baseline.** FF.
11. **Seeds and sample size.** None (deterministic). Sample size not applicable.
12. **Compute budget.** Under one minute in total (planning estimate).
13. **Metrics.** As in `research/protocol.md` section 3; time units are the example's abstract units.
14. **Uncertainty.** None reported; exact comparison with tolerance.
15. **Exclusion and stopping.** None. Nonconvergence is a failure of the experiment. Solver: gradient projection (umbrella 15.3 item 1).
16. **Failure modes.** Solver stalling near the boundary of the feasible set (Frank-Wolfe did so in exploratory runs, J-0003, hence the gradient-projection solver); floating point.
17. **Sensitivity.** Tolerance `1e-6` versus `1e-10`.
18. **Reproduction (planned).** `uv run flow run EXP-001`; outputs `results/EXP-001/`.
