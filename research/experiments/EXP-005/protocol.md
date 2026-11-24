<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-005 (optional): Single-link removal scan on grids

**Status: protocol v1.0, FROZEN, optional (owner-approved 2026-11-24, round 2), not yet run.** Amendments before the freeze: umbrella `research/protocol.md` section 15. First item to cut if the five-day target is threatened.

1. **Question.** In 4x4 BPR grids at `rho = 2`, does removing a single directed link ever reduce UE total travel time (a Braess link)?
2. **Mechanism.** As in EXP-002, on a generic network.
3. **Rationale.** Prevalence literature (Steinberg and Zangwill 1983; Valiant and Roughgarden 2010), metadata verified only; Youn et al. (2008, abstract read) report street closures that reduce travel time on city networks.
4. **Competing explanations.** Apparent reductions within solver tolerance (false positives).
5. **Hypotheses.** Descriptive with one test: H1 incidence `> 0`, where incidence is the share of instances with at least one removable link (all OD pairs stay connected) whose removal lowers `TSTT_UE` by more than 1e-4 relative (100 times the relative-gap tolerance). H0: incidence = 0. Contradiction: no such link in any instance. Also reported: number of Braess links per instance, their size of effect.
6. **Estimand.** Incidence share and its Wilson 95 percent interval over 100 instances.
7. **Unit and scope.** 4x4 instances, seeds 1000-1099 (same as EXP-003).
8. **Variables.** Independent: removed link. Dependent: `TSTT_UE` change.
9. **Treatment and control.** Network minus one link versus full network.
10. **Baseline.** Full network UE.
11. **Seeds and sample size.** 100 instances, 48 removals each.
12. **Compute budget.** About 4,800 UE solves, gradient projection (planning estimate under one hour). Runner mode and config are not implemented at the freeze: `flow run EXP-005` is refused until a config is added and its hash recorded with the owner's approval.
13. **Metrics.** Relative change in `TSTT_UE`.
14. **Uncertainty.** Wilson interval for the incidence; per-link effects with tolerance band.
15. **Exclusion and stopping.** Removals that disconnect any OD pair are skipped and counted.
16. **Failure modes.** False positives from tolerance; mitigated by the 1e-4 threshold and a re-solve at `1e-8` of every flagged link.
17. **Sensitivity.** Threshold 1e-3.
18. **Reproduction (planned).** `uv run flow run EXP-005`.
