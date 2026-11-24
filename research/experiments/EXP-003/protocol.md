<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-003: Grid networks, collective excess of individually optimal routing (primary)

**Status: protocol v1.0, FROZEN (owner-approved 2026-11-24, round 2), not yet run.** Amendments before the freeze: umbrella `research/protocol.md` section 15. Depends on EXP-001 and the M2 test suite. Primary experiment of the study.

1. **Question.** On seeded BPR grids at matched demand levels, by how much does the total system travel time of individually optimal routing (UE, and the FF baseline) exceed the system optimum?
2. **Mechanism.** Selfish routing ignores the marginal delay imposed on others; the gap grows with congestion and cost curvature.
3. **Rationale.** Roughgarden and Tardos (2002, preprint read): ratio at most 4/3 for linear latencies, unbounded for general nondecreasing latencies. Youn et al. (2008, abstract read): city networks show a measurable gap. FLOW measures the gap in a controlled synthetic family with paired uncertainty.
4. **Competing explanations.** Solver nonconvergence inflating or shrinking the gap (S1); dependence on cost curvature (S2); artefact of the demand calibration (S3); OD sampling.
5. **Hypotheses.** Primary: `theta` = median over 6x6 instances of `R(UE)` at `rho = 2`. H0: `theta <= 0.01`; H1: `theta > 0.01`. Reject H0 if the one-sided 95 percent bootstrap lower bound exceeds 0.01. Contradiction: lower bound at or below 0.01. Secondary (descriptive): `R(FF) - R(UE)` at each level, `R(UE)` by size and level, fairness and p95 differences.
6. **Estimand.** Median of the per-instance `R(UE)` over the instance population defined by the generator.
7. **Unit and scope.** Instance = seeded grid plus seeded OD sample. Sizes 4x4 (seeds 1000-1099) and 6x6 (seeds 2000-2099).
8. **Variables.** Independent: arm (FF, UE, SO), `rho in {1, 2, 3}` (rho = 0.5 dropped, umbrella 15.3 item 3), grid size. Dependent: R, TSTT, mean and p95 trip time, congestion, fairness, convergence.
9. **Treatment and control.** Treatments FF and UE; control and normalising reference SO on the same instance and level.
10. **Baseline.** FF (simplest individually optimal rule).
11. **Seeds and sample size.** 100 instances per size, fixed (umbrella section 5 and 15.3 item 2).
12. **Compute budget.** Gradient projection, cap 20,000 sweeps per solve; exploratory solves took about 0.01 to 0.03 s on 6x6, rho = 2. The S1 Frank-Wolfe reference takes about 8 to 12 s per solve (exploratory), about 40 minutes in total.
13. **Metrics.** Umbrella section 3.
14. **Uncertainty.** Paired percentile bootstrap over instances, 10,000 resamples, seed 20261124.
15. **Exclusion and stopping.** Umbrella section 7 (nonconverged runs flagged and counted; primary analysis fails if more than 10 percent of the primary cell is nonconverged).
16. **Failure modes.** Slow convergence at `rho = 3` (measured for FW in exploratory runs; GP converged there); numerical overflow of `(x/c)^4` under FF at high demand (use float64, check finiteness).
17. **Sensitivity.** S1 tolerance (`1e-4`, `1e-8`) plus a Frank-Wolfe differential reference at `1e-6`, S2 `beta = 1`, S3 absolute demand calibration with share `s = 0.10826` (rule C-S3, umbrella 15.2 and 15.6), all on the 6x6 primary cell (seeds 2000-2099).
18. **Reproduction (planned).** `uv run flow run EXP-003`; raw outputs in `results/raw/EXP-003/` (not committed), summary `research/experiments/EXP-003/metrics.csv`.
