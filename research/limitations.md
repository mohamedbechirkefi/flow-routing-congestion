<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Limitations (living document)

Items 1 to 8 were written at M0, before any result, as limitations known by design. Items 9 to 13 were added at M3 and items 14 to 19 at M4 (2026-11-25); items 9 and 12 were updated at M4.

1. **Mostly synthetic networks.** The primary hypothesis rests on the Braess network and seeded grids. One real network (TNTP Sioux Falls, local use only) calibrates the BPR parameters and gives a single deterministic second test (EXP-006). Sioux Falls is a small 1970s test network that its maintainers describe as "not considered as a realistic one"; one network supports no population claim and no prediction for any real city.
2. **Static deterministic assignment.** No time dynamics, queue spillback, departure-time choice, signals or stochastic route choice. Real congestion is dynamic.
3. **Behavioural model.** "Individually optimal" is modelled as free-flow shortest paths or Wardrop user equilibrium with perfect information. Synthetic agents are not human participants; nothing is inferred about real driver behaviour.
4. **Cost function.** BPR parameters (0.15, 4) are conventional. They were fitted from the Sioux Falls file (J-0010), where they are themselves the "traditional" assumed values (TNTP README), so the calibration confirms convention rather than measuring real roads.
5. **Not a navigation product study.** No claim about Google Maps, Waze or any proprietary routing system, their internals or their effects.
6. **Solver error.** Gradient-projection (solver of record) and Frank-Wolfe (S1 reference) results are approximate within the relative-gap tolerance; small differences near the tolerance are not interpretable (sensitivity S1).
7. **Compliance arm.** MIX(c) is one specific operationalisation (scaled system-optimal flow plus equilibrium of the rest). Other definitions of partial compliance could give different results.
8. **Grid family.** Conclusions do not transfer to other topologies or sizes without new experiments.

## Added at M3 (2026-11-25, from confirmatory results)

9. **Exact checks limited by the frozen tolerance.** EXP-001 and EXP-002 ran at the frozen `RG <= 1e-6`; their residuals (up to 6.2e-5 in TSTT, about 1e-5 in the Braess regime boundaries) exceed the frozen absolute 1e-6 tolerance, so both are contradicted under their own rule even though signs, the lower paradox boundary and the published 83/92 values are reproduced. Owner decision 2026-11-25b (item 3): the frozen verdicts stand; an exploratory rerun at `1e-10` (J-0022) meets the rule (largest EXP-001 difference 7.53e-9; boundaries within 1.5e-9), is reported beside the verdicts and never replaces them. The protocol (1e-10) and config (1e-6) mismatch is a design error of the frozen record.
10. **Cost curvature.** With `beta = 1` (S2) the median excess falls to 0.0030, below delta; the primary finding holds for the BPR curvature `beta = 4` only.
11. **Frank-Wolfe reference.** The S1 Frank-Wolfe reference did not converge on 93 of 100 primary-cell instances; it gives no independent check of the gradient-projection values.
12. **Untested sensitivities.** EXP-004 item 17 (link-flow instead of path-flow compliant scaling) has no frozen config and is not added (owner, 2026-11-25b, item 3). EXP-001 item 17 (`1e-10`) exists only as the exploratory check J-0022, not as a confirmatory sensitivity.
13. **Small effects in EXP-005.** Braess links are common (77 of 100 instances) but their effects are small (relative decreases between 1.2e-4 and 0.035).

## Added at M4 (2026-11-25, interpretation and second review pass)

14. **Light demand.** At rho = 1 the median excess is below delta at both grid sizes (0.00409 and 0.00305), and only 3 of 100 6x6 instances exceed delta (exploratory J-0023). The primary finding is a statement about congested demand.
15. **The margin is a convention.** delta = 0.01 was fixed by the study at M0, before any run, without an external source for its practical importance.
16. **No independent solver check on grids.** Every grid number comes from one gradient-projection implementation. The Frank-Wolfe reference failed on 93 of 100 instances, and no published system-optimal solution was used to validate SO on any network except the Braess example.
17. **OD rule fixed.** The OD count (12) and the distance rule (at least n - 1) were never varied; the excess may depend on them.
18. **Compliance by construction.** MIX(0) = UE and MIX(1) = SO by definition, so an overall decline in EXP-004 is built in; only the step-wise decline is informative.
19. **Weak real-network replication.** EXP-006 exceeds delta by 0.0045 at rho = 2 on one network that its maintainers describe as "not considered as a realistic one" (TNTP SiouxFalls README, read 2026-11-25).
