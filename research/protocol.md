<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW study protocol

**Status: DRAFT v0.1 (2026-11-24). Not frozen.** Freezing is the owner's decision (G-FREEZE). Until the owner records a freeze in `research/decision_log.md` with the SHA-256 of this file and of each `research/experiments/EXP-NNN/protocol.md`, every run is exploratory and labelled so. All numerical settings below are planning proposals, not measured values.

## 1. Research question

Can individually optimal routing worsen collective travel time?

Operationally: on synthetic congestible networks, how much larger is the total system travel time when every traveller takes a route that is individually optimal (free-flow shortest path, or user equilibrium) than when routes are chosen to minimise total travel time (system optimum), and can adding a link make individually optimal routing worse for everyone (Braess)?

Claims boundary: synthetic networks only. Not a reconstruction of Google Maps or any navigation product, not a prediction for any real city, and no claim about real driver behaviour.

## 2. Formal model

- Directed graph `G = (V, E)`. Each link `e` has free-flow time `t0_e` (minutes), capacity `c_e` (vehicles per hour, veh/h) and cost function `t_e(x_e)` (minutes), nondecreasing and nonnegative in the link flow `x_e` (veh/h).
- Grid links use the BPR form `t_e(x) = t0_e (1 + alpha (x / c_e)^beta)`, `alpha = 0.15`, `beta = 4` (parameter source unverified, see literature review). The Braess network uses the linear costs of the published example: `10x`, `x + 50`, `x + 50`, `10x`, and added link `x + 10` (units: the example's abstract time units; demand 6 abstract units).
- Origin-destination (OD) pairs `w in W` with demand `d_w` (veh/h). Path flows `h_p >= 0` with `sum_{p in P_w} h_p = d_w`; link flows `x_e = sum_p delta_{ep} h_p`.
- **Total system travel time** `TSTT(x) = sum_e x_e t_e(x_e)` (veh min per hour).
- **Free-flow shortest path (FF), baseline.** All demand of each OD pair is assigned to its shortest path under `t0` (all-or-nothing). Ties are broken deterministically (lexicographically smallest node sequence). This is the simplest individually optimal rule: each traveller takes the route that is fastest on an empty network.
- **User equilibrium (UE).** Wardrop's first principle: no traveller can lower their own time by switching path. Computed by Frank-Wolfe on the Beckmann objective `sum_e integral_0^{x_e} t_e(s) ds`, exact line search by bisection.
- **System optimum (SO).** Minimises `TSTT`. Frank-Wolfe on marginal costs `t_e(x) + x t_e'(x)`.
- **Mixed compliance MIX(c).** A fraction `c` of every OD demand follows the path flows of the SO solution for the full demand scaled by `c`; the remaining `(1 - c)` reaches user equilibrium given the compliant flow as fixed background flow. `MIX(0) = UE` and `MIX(1) = SO` by construction (both are tests). Related to the partial-control literature (Roughgarden 2004; Harker 1988), relation to be confirmed at M1.
- **Relative gap** (convergence): `RG = (sum_e x_e t_e(x_e) - sum_w d_w kappa_w) / sum_e x_e t_e(x_e)`, where `kappa_w` is the current shortest-path time of OD `w`. For SO the same formula with marginal costs.

## 3. Metrics

| Metric | Formula | Unit | Role |
|---|---|---|---|
| **R (primary)** | `R(arm) = TSTT(arm) / TSTT(SO) - 1` on the same instance | dimensionless | Collective excess over the system optimum; `R(UE) + 1` is the price of anarchy |
| TSTT | as above | veh min/h | Secondary (absolute) |
| Mean trip time | `TSTT / sum_w d_w` | min | Secondary |
| p95 trip time | demand-weighted 95th percentile of path times over used paths | min | Secondary |
| Congestion | flow-weighted mean `x_e / c_e`; share of links with `x_e / c_e > 1` | ratio, share | Secondary |
| Fairness | demand-weighted Gini coefficient of the stretch `time_p / FFmin_w` over travellers | dimensionless in [0, 1) | Secondary |
| Convergence | iterations to `RG <= tol`, final `RG`, wall-clock seconds | count, ratio, s | Secondary and quality control |
| Braess effect | `TSTT_UE(with link) - TSTT_UE(without link)` | veh min/h | EXP-002 and EXP-005 |

Path flows for p95 and fairness are tracked by storing the all-or-nothing path of each Frank-Wolfe iteration with its convex weight.

## 4. Hypotheses (falsifiable)

**Primary (EXP-003).** Estimand `theta` = median over instances of `R(UE)` on 6 by 6 grids at demand level `rho = 2` (pre-specified primary cell). Practical margin `delta = 0.01` (1 percent of system-optimal travel time).

- H0: `theta <= 0.01`. Individually optimal (equilibrium) routing does not worsen collective travel time by a practically meaningful margin in this family.
- H1 (directional): `theta > 0.01`.
- Decision rule: reject H0 if the lower bound of the one-sided 95 percent percentile bootstrap interval for the median (10,000 resamples of instances, bootstrap seed 20261124) exceeds 0.01.
- Contradicting result: lower bound at or below 0.01. If in addition the upper bound of the two-sided 95 percent interval is below 0.01, report evidence that the loss is practically negligible in this family. Nonrejection alone is not evidence of equivalence.

**Baseline contrast (secondary, EXP-003).** Paired difference `R(FF) - R(UE)` per instance at each demand level; reported with paired bootstrap intervals, no confirmatory test. Expectation (not a hypothesis test): FF is worse than UE once demand is congested.

**Analytic Braess checks (EXP-001, EXP-002).** Deterministic. EXP-001: UE path cost 83 without the extra link and 92 with it at demand 6 (Braess et al. 2005; supernet page). EXP-002: hand derivation (assistant, this session, to be verified by exact rational unit tests before any run) predicts that adding the link raises UE travel time exactly for demand in the open interval `(80/31, 80/9)`, about `(2.581, 8.889)`. Contradiction: any computed boundary differing from these values by more than `1e-6`, or the paradox at a demand outside the interval.

**Compliance (EXP-004).** H1: median `R(MIX(c))` decreases strictly with `c` over `c in {0, 0.25, 0.5, 0.75, 1}`. H0: for at least one consecutive pair, the paired median difference `R(MIX(c_k)) - R(MIX(c_{k+1}))` has a 95 percent bootstrap lower bound at or below 0.

## 5. Experimental unit, seeds and sample size

- **Unit.** One network-demand instance: a seeded grid (link times, capacities) plus a seeded OD sample. All arms and demand levels are evaluated on the same instance (matched comparison, common random numbers). Arms are deterministic given the instance, so seeds index instances, not solver noise.
- **Seeds.** Exploratory and smoke seeds 9000-9019 only. Confirmatory seeds: 1000-1049 (4 by 4 grids), 2000-2049 (6 by 6 grids). Confirmatory seeds are not run before the freeze. At least 5 seeds per stochastic arm is exceeded (50).
- **Sample size rationale.** All variance is between instances. With n = 50, the distribution-free 95 percent interval for a median spans roughly the 18th to the 33rd order statistic, which is precise enough to separate a median of 0.01 from medians of a few percent if the between-instance spread is of that order. The spread is unknown before running; n is fixed now and is not increased after seeing results. Cost is low (feasibility section 4).

## 6. Uncertainty method

Percentile bootstrap over instances (the independent unit), 10,000 resamples, fixed bootstrap seed. Paired contrasts resample instance ids, keeping all arms of an instance together. Report medians, means, interquartile ranges, full per-instance distributions and effect sizes (median paired difference). Deterministic experiments (EXP-001, EXP-002) report exact values and tolerances, not confidence intervals.

## 7. Exclusion and stopping rules

- **Generator validity.** An instance is valid if every OD pair is connected. The generator draws OD pairs only among connected pairs; disconnected networks are an error path covered by tests, not a silent exclusion.
- **Convergence.** UE, SO and MIX stop at `RG <= 1e-6` or at 20,000 iterations. A run that ends above tolerance is flagged `nonconverged`, kept in raw results, excluded from the primary analysis and included in sensitivity S1. Every exclusion is counted and reported. If more than 10 percent of primary-cell instances are nonconverged, the primary analysis is reported as failed and not reinterpreted.
- **Stopping.** Fixed matrix, no optional stopping, no interim looks at confirmatory results.
- **Failures.** Exceptions are written to the run record with traceback; no run is dropped silently.

## 8. Matrices

**Smoke matrix (exploratory, run at M2/M3 before confirmatory runs).** Braess network at demand 6, with and without link e, arms FF, UE, SO. Grid 3 by 3, `rho = 1`, seeds 9000-9004, arms FF, UE, SO, MIX(0.5). Purpose: pipeline, schemas and timing only.

**Full matrix (confirmatory after freeze).**

| EXP | Networks | Factors | Arms | Instances | Solves (approx.) |
|---|---|---|---|---|---|
| EXP-001 | Braess, with/without link | demand 6 | FF, UE, SO | 1 (deterministic) | 6 |
| EXP-002 | Braess, with/without link | demand 0.25 to 12.0 step 0.25 (48 values) | FF, UE, SO | deterministic | 288 |
| EXP-003 | grid 4x4, 6x6 | `rho in {0.5, 1, 2, 3}` | FF, UE, SO | 50 per size | 1,200 (FF excluded, trivial) |
| EXP-003 S1-S3 | grid 6x6 | `rho = 2`; tol, beta, calibration | UE, SO | 50 | 600 |
| EXP-004 | grid 6x6 | `c in {0,0.25,0.5,0.75,1}` x capacity scale `{0.8, 1.0, 1.2}` | MIX(c) | 50 | 750 plus SO references |
| EXP-005 (optional) | grid 4x4 | single directed-link removal | UE | 50 | about 2,400 |

## 9. Sensitivity analyses (could invalidate the main interpretation)

- **S1 Solver tolerance.** Re-solve the primary cell with `RG <= 1e-4` and `RG <= 1e-8`. If the primary decision flips between tolerances, the measured UE-SO gap is a convergence artefact and the primary result is reported as not robust.
- **S2 Cost curvature.** `beta = 1` instead of 4. Theory bounds the ratio by 4/3 for linear costs; a large change shows dependence on the cost model, limiting scope.
- **S3 Demand calibration.** Replace the free-flow-based calibration (`rho` relative to the demand at which FF loading first saturates a link) by an absolute calibration (total demand as a fixed share of the summed capacity of the links leaving origins). If the effect is present only under one calibration, it is an artefact of the demand definition.

## 10. Demand calibration (grids)

For each instance, `D_ref` is the total demand at which free-flow all-or-nothing loading brings the most loaded link to `x / c = 1` (closed form because FF loading is linear in demand). Total demand is `rho * D_ref`, split over OD pairs by the instance's Dirichlet weights.

## 11. Grid generator (proposal)

`n` by `n` lattice, bidirectional links between 4-neighbours. Per undirected pair: `t0 ~ Uniform[1, 3]` minutes, `c ~ Uniform[600, 1800]` veh/h, same values in both directions. `K = 12` OD pairs drawn without replacement among node pairs at Manhattan distance at least `n - 1`, weights `Dirichlet(1, ..., 1)`. NumPy `Generator(PCG64(seed))`. Generator version recorded in every run manifest.

## 12. Compute budget and reproducibility

Single CPU core, fixed iteration caps above, wall-clock and peak memory recorded per run (feasibility section 4 gives the planning estimate). Every run records config hash, git revision, OS, CPU, Python and package versions. Commands (to be implemented at M2): `uv run flow smoke`, `uv run flow run EXP-003`, `uv run flow report`, `uv run pytest`.

## 13. Verification before any run (master prompt section 10)

Shortest paths against brute-force path enumeration on small graphs; flow conservation at every node; nonnegative costs and flows; explicit errors for disconnected OD pairs; convergence to tolerance; `MIX(0) = UE`, `MIX(1) = SO`; `TSTT(SO) <= TSTT(UE)` and `TSTT(SO) <= TSTT(FF)` on every instance; exact Braess values from EXP-001; MSA as a differential reference for UE.

## 14. Deviations

None yet. Any change after a freeze is dated, justified, logged in `research/decision_log.md` and analysed separately as exploratory.
