<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Limitations (living document)

Status at M0: no results exist. These are limitations known by design.

1. **Mostly synthetic networks.** The primary hypothesis rests on the Braess network and seeded grids. One real network (TNTP Sioux Falls, local use only) calibrates the BPR parameters and gives a single deterministic second test (EXP-006). Sioux Falls is a small 1970s test network that its maintainers describe as "not considered as a realistic one"; one network supports no population claim and no prediction for any real city.
2. **Static deterministic assignment.** No time dynamics, queue spillback, departure-time choice, signals or stochastic route choice. Real congestion is dynamic.
3. **Behavioural model.** "Individually optimal" is modelled as free-flow shortest paths or Wardrop user equilibrium with perfect information. Synthetic agents are not human participants; nothing is inferred about real driver behaviour.
4. **Cost function.** BPR parameters (0.15, 4) are conventional. They were fitted from the Sioux Falls file (J-0010), where they are themselves the "traditional" assumed values (TNTP README), so the calibration confirms convention rather than measuring real roads.
5. **Not a navigation product study.** No claim about Google Maps, Waze or any proprietary routing system, their internals or their effects.
6. **Solver error.** Gradient-projection (solver of record) and Frank-Wolfe (S1 reference) results are approximate within the relative-gap tolerance; small differences near the tolerance are not interpretable (sensitivity S1).
7. **Compliance arm.** MIX(c) is one specific operationalisation (scaled system-optimal flow plus equilibrium of the rest). Other definitions of partial compliance could give different results.
8. **Grid family.** Conclusions do not transfer to other topologies or sizes without new experiments.

## Added at M3 (2026-11-25, from confirmatory results)

9. **Exact checks limited by the frozen tolerance.** EXP-001 and EXP-002 ran at the frozen `RG <= 1e-6`; their residuals (up to 6.2e-5 in TSTT, about 1e-5 in the Braess regime boundaries) exceed the frozen absolute 1e-6 tolerance, so both are contradicted under their own rule even though signs, the lower paradox boundary and the published 83/92 values are reproduced. A `1e-10` rerun needs the owner's decision.
10. **Cost curvature.** With `beta = 1` (S2) the median excess falls to 0.0030, below delta; the primary finding holds for the BPR curvature `beta = 4` only.
11. **Frank-Wolfe reference.** The S1 Frank-Wolfe reference did not converge on 93 of 100 primary-cell instances; it gives no independent check of the gradient-projection values.
12. **Untested sensitivities.** EXP-004 item 17 (link-flow instead of path-flow compliant scaling) and EXP-001 item 17 (`1e-10`) have no frozen config and were not run.
13. **Small effects in EXP-005.** Braess links are common (77 of 100 instances) but their effects are small (relative decreases between 1.2e-4 and 0.035).
