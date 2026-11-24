<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# EXP-006: Second test on a real road network (TNTP Sioux Falls)

**Status: protocol v1.0, FROZEN (owner-approved 2026-11-24, round 2), not yet run.** Added by umbrella `research/protocol.md` section 15.4 under the owner's real-data approval. Depends on EXP-001 (engine) and the ingestion tests.

1. **Question.** Does the direction of the primary hypothesis (equilibrium routing exceeds the system optimum by more than `delta = 0.01`) hold on one real road network?
2. **Mechanism.** As in EXP-003: selfish routing ignores the marginal delay imposed on others; the gap depends on congestion and on network structure, which a real network supplies instead of a lattice.
3. **Rationale.** Sioux Falls (LeBlanc, Morlok and Pierskalla 1975, via the TNTP repository, README read 2026-11-24) is the standard small test network of the assignment literature; its best-known UE solution is published with the data, which lets the engine be validated on a real network. The TNTP README warns that the network "is not considered as a realistic one"; this limits the external claim.
4. **Competing explanations.** Ingestion error (link order, units, node indexing); solver nonconvergence; dependence on the demand scaling (published level versus FF-calibrated levels); a single network is not a population.
5. **Hypotheses.** Deterministic replication check: the direction replicates if `R(UE) > 0.01` at `rho = 2`. Contradiction: `R(UE) <= 0.01` at `rho = 2`. Descriptive: R(UE) and R(FF) at the published demand (`rho_SF = 5.788`, J-0010) and at `rho = 1, 3`.
6. **Estimand.** `R(UE)` and `R(FF)` on the single network at each demand level.
7. **Unit and scope.** One real network, 24 nodes, 76 links, 528 positive OD pairs. No seeds.
8. **Variables.** Independent: arm (FF, UE, SO), demand level (published; `rho in {1, 2, 3}` with the published OD shares scaled by the section 10 calibration). Dependent: R, TSTT, mean and p95 trip time, congestion, fairness, convergence.
9. **Treatment and control.** Treatments FF and UE; reference SO on the same network and demand.
10. **Baseline.** FF.
11. **Seeds and sample size.** None; deterministic, one network. No population inference.
12. **Compute budget.** 18 solves; exploratory UE solve at the published demand took 1.1 s (`1e-6`) and 2.5 s (`1e-8`), J-0012.
13. **Metrics.** Umbrella section 3. Times in 0.01 hours (TNTP units); R is dimensionless.
14. **Uncertainty.** None (deterministic). Solver tolerance sensitivity only (item 17).
15. **Exclusion and stopping.** Validation gate first: at the published demand the UE link flows must satisfy `max_e |x_e - x_ref_e| / max_e x_ref_e <= 1e-3` against `SiouxFalls_flow.tntp` (recorded per UE record as `ref_flow_max_abs_diff_rel`). If the gate fails, EXP-006 is reported as failed and not reinterpreted. Nonconverged solves are flagged and reported; the replication check needs converged UE and SO at `rho = 2`.
16. **Failure modes.** Data file changed upstream (prevented: pinned commit and SHA-256 check before every load); zones used as through nodes (supported, FIRST THRU NODE = 1).
17. **Sensitivity.** Published level and `rho = 2` re-solved at `RG <= 1e-8`.
18. **Reproduction.** `.venv/bin/python scripts/download_tntp.py`, then `uv run flow run EXP-006`. The data are never committed; licence "academic research purposes only", cite the TNTP repository.
