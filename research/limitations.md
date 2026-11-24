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
