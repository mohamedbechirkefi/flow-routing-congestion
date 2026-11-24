<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-004: Compliance and capacity sweep

**Status: protocol v1.0, FROZEN (owner-approved 2026-11-24, round 2), not yet run.** Amendments before the freeze: umbrella `research/protocol.md` section 15. Depends on EXP-003 infrastructure (same instances).

1. **Question.** How does the collective excess change when a fraction `c` of travellers follows system-optimal routing, and when all capacities are scaled?
2. **Mechanism.** Compliant travellers take routes that account for the marginal delay they cause; the rest re-equilibrate around them, which may offset part of the benefit.
3. **Rationale.** Partial central control is studied in the Stackelberg routing literature (Roughgarden 2004, metadata verified only) and mixed behaviour classes (Harker 1988, metadata verified only). Both to be read at M1 before freezing.
4. **Competing explanations.** Re-equilibration of non-compliant users cancelling the benefit; nonmonotone effects; solver nonconvergence of the follower equilibrium.
5. **Hypotheses.** H1: median `R(MIX(c))` decreases strictly with `c`. H0: at least one consecutive pair has a paired median difference whose 95 percent bootstrap lower bound is at or below 0. Capacity scale is descriptive (no confirmatory hypothesis). Contradiction: any nonmonotone step.
6. **Estimand.** Paired median differences of R between consecutive compliance levels.
7. **Unit and scope.** 6x6 instances, seeds 2000-2099, `rho = 2` with total demand fixed at the capacity-scale-1.0 calibration.
8. **Variables.** Independent: `c in {0, 0.25, 0.5, 0.75, 1}`, capacity scale `{0.8, 1.0, 1.2}`. Dependent: R (relative to SO at the same capacity scale), TSTT, fairness, mean time of compliant versus non-compliant travellers.
9. **Treatment and control.** Control `c = 0` (equals UE).
10. **Baseline.** FF reported at each capacity scale.
11. **Seeds and sample size.** 100 instances, same as EXP-003 6x6.
12. **Compute budget.** About 1,500 MIX solves plus SO references, gradient projection; minutes (planning estimate from exploratory GP timings).
13. **Metrics.** Umbrella section 3, plus the time ratio of compliant to non-compliant travellers (an agency and fairness indicator).
14. **Uncertainty.** Paired bootstrap over instances.
15. **Exclusion and stopping.** Umbrella section 7. MIX(c) is converged only if the SO reference and the follower UE both converged; MIX(0) and MIX(1) are identity checks (umbrella 15.3 item 5).
16. **Failure modes.** The SO path decomposition is not unique; the compliant flow uses the path flows produced by the deterministic gradient-projection SO run (stated as an operational choice).
17. **Sensitivity.** Alternative compliant assignment: link-flow scaling instead of path-flow scaling (if path decomposition matters, the result is definition-dependent).
18. **Reproduction (planned).** `uv run flow run EXP-004`.
