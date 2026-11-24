<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# FLOW study protocol

**Status: v1.0, FROZEN (owner-approved 2026-11-24, round 2).** Freeze record: `research/freeze.json` and the `FREEZE` lines of decision D-011 in `research/decision_log.md` (SHA-256 of this file, of each `research/experiments/EXP-NNN/protocol.md` and of each confirmatory config). Amendments applied before the freeze are listed in section 15; any later change is a deviation (section 14).

## 1. Research question

Can individually optimal routing worsen collective travel time?

Operationally: on synthetic congestible networks, how much larger is the total system travel time when every traveller takes a route that is individually optimal (free-flow shortest path, or user equilibrium) than when routes are chosen to minimise total travel time (system optimum), and can adding a link make individually optimal routing worse for everyone (Braess)?

Claims boundary: synthetic networks carry the primary hypothesis; one real network (TNTP Sioux Falls) is used for calibration and a second test only (section 15). Not a reconstruction of Google Maps or any navigation product, not a prediction for any real city, and no claim about real driver behaviour.

## 2. Formal model

- Directed graph `G = (V, E)`. Each link `e` has free-flow time `t0_e` (minutes), capacity `c_e` (vehicles per hour, veh/h) and cost function `t_e(x_e)` (minutes), nondecreasing and nonnegative in the link flow `x_e` (veh/h).
- Grid links use the BPR form `t_e(x) = t0_e (1 + alpha (x / c_e)^beta)`, `alpha = 0.15`, `beta = 4` (parameter source unverified, see literature review). The Braess network uses the linear costs of the published example: `10x`, `x + 50`, `x + 50`, `10x`, and added link `x + 10` (units: the example's abstract time units; demand 6 abstract units).
- Origin-destination (OD) pairs `w in W` with demand `d_w` (veh/h). Path flows `h_p >= 0` with `sum_{p in P_w} h_p = d_w`; link flows `x_e = sum_p delta_{ep} h_p`.
- **Total system travel time** `TSTT(x) = sum_e x_e t_e(x_e)` (veh min per hour).
- **Free-flow shortest path (FF), baseline.** All demand of each OD pair is assigned to its shortest path under `t0` (all-or-nothing). Ties are broken deterministically (lexicographically smallest node sequence). This is the simplest individually optimal rule: each traveller takes the route that is fastest on an empty network.
- **User equilibrium (UE).** Wardrop's first principle: no traveller can lower their own time by switching path. Minimises the Beckmann objective `sum_e integral_0^{x_e} t_e(s) ds`. Solver of record: path-based gradient projection (amendment 15.3 item 1); Frank-Wolfe with exact line search is a differential reference in S1.
- **System optimum (SO).** Minimises `TSTT`, same solvers on marginal costs `t_e(x) + x t_e'(x)`.
- **Mixed compliance MIX(c).** A fraction `c` of every OD demand follows the path flows of the SO solution for the full demand scaled by `c`; the remaining `(1 - c)` reaches user equilibrium given the compliant flow as fixed background flow. `MIX(0) = UE` and `MIX(1) = SO` by construction (both are tests, reported as identity checks; convergence rule in section 15.3 item 5). Related to the partial-control literature (Roughgarden 2004; Harker 1988), relation to be confirmed at M1.
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

Path flows for p95 and fairness are the path flows maintained by gradient projection (for the Frank-Wolfe reference: the all-or-nothing path of each iteration with its convex weight).

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
- **Seeds.** Exploratory and smoke seeds 9000-9019 only. Confirmatory seeds (amended, section 15.3 item 2): 1000-1099 (4 by 4 grids), 2000-2099 (6 by 6 grids). Confirmatory seeds are not run before the freeze. At least 5 seeds per stochastic arm is exceeded (100).
- **Sample size rationale.** All variance is between instances. Exploratory planning runs (seeds 9000-9019, journal J-0004) gave a between-instance SD of R(UE) of about 0.017 in the 6 by 6, rho = 2 analogue; the projected 95 percent bootstrap interval width of the median is about 0.018 at n = 50 and about 0.013 at n = 100. n = 100 is fixed on these precision grounds only and is not increased after seeing results. Cost is low with gradient projection (about 0.01 to 0.03 s per solve, exploratory).

## 6. Uncertainty method

Percentile bootstrap over instances (the independent unit), 10,000 resamples, fixed bootstrap seed. Paired contrasts resample instance ids, keeping all arms of an instance together. Report medians, means, interquartile ranges, full per-instance distributions and effect sizes (median paired difference). Deterministic experiments (EXP-001, EXP-002) report exact values and tolerances, not confidence intervals.

## 7. Exclusion and stopping rules

- **Generator validity.** An instance is valid if every OD pair is connected. The generator draws OD pairs only among connected pairs; disconnected networks are an error path covered by tests, not a silent exclusion.
- **Convergence.** UE, SO and MIX stop at `RG <= 1e-6` or at 20,000 iterations (gradient-projection sweeps). MIX(c) counts as converged only if the SO reference and the follower UE both converged (section 15.3 item 5). A run that ends above tolerance is flagged `nonconverged`, kept in raw results, excluded from the primary analysis and included in sensitivity S1. Every exclusion is counted and reported. If more than 10 percent of primary-cell instances are nonconverged, the primary analysis is reported as failed and not reinterpreted.
- **Stopping.** Fixed matrix, no optional stopping, no interim looks at confirmatory results.
- **Failures.** Exceptions are written to the run record with traceback; no run is dropped silently.

## 8. Matrices

**Smoke matrix (exploratory, run at M2/M3 before confirmatory runs).** Braess network at demand 6, with and without link e, arms FF, UE, SO. Grid 3 by 3, `rho = 1`, seeds 9000-9004, arms FF, UE, SO, MIX(0.5). Purpose: pipeline, schemas and timing only.

**Full matrix (confirmatory after freeze).**

| EXP | Networks | Factors | Arms | Instances | Solves (approx.) |
|---|---|---|---|---|---|
| EXP-001 | Braess, with/without link | demand 6 | FF, UE, SO | 1 (deterministic) | 6 |
| EXP-002 | Braess, with/without link | demand 0.25 to 12.0 step 0.25 (48 values) | FF, UE, SO | deterministic | 288 |
| EXP-003 | grid 4x4, 6x6 | `rho in {1, 2, 3}` | FF, UE, SO | 100 per size | 1,200 (FF excluded, trivial) |
| EXP-003 S1-S3 | grid 6x6 | `rho = 2`; tol (plus Frank-Wolfe reference), beta, calibration | UE, SO (S3 also FF) | 100 | 1,000 |
| EXP-004 | grid 6x6 | `c in {0,0.25,0.5,0.75,1}` x capacity scale `{0.8, 1.0, 1.2}` | MIX(c) | 100 | 1,500 plus SO references |
| EXP-005 (optional) | grid 4x4 | single directed-link removal | UE | 100 | about 4,800 |
| EXP-006 | TNTP Sioux Falls (real) | published demand and `rho in {1, 2, 3}`; S1 at `1e-8` | FF, UE, SO | 1 (deterministic) | 18 |

## 9. Sensitivity analyses (could invalidate the main interpretation)

- **S1 Solver tolerance.** Re-solve the primary cell with `RG <= 1e-4` and `RG <= 1e-8` (gradient projection), and once with Frank-Wolfe at `RG <= 1e-6` as a differential reference (reported, not used in a decision; section 15.3 item 1). If the primary decision flips between tolerances, the measured UE-SO gap is a convergence artefact and the primary result is reported as not robust.
- **S2 Cost curvature.** `beta = 1` instead of 4. Theory bounds the ratio by 4/3 for linear costs; a large change shows dependence on the cost model, limiting scope.
- **S3 Demand calibration.** Replace the free-flow-based calibration (`rho` relative to the demand at which FF loading first saturates a link) by an absolute calibration (total demand as a fixed share `s` of the summed capacity of the links leaving origins; `s` fitted by rule C-S3 of section 15.2, see 15.6; compared with the rho = 2 primary cell). If the effect is present only under one calibration, it is an artefact of the demand definition.

## 10. Demand calibration (grids)

For each instance, `D_ref` is the total demand at which free-flow all-or-nothing loading brings the most loaded link to `x / c = 1` (closed form because FF loading is linear in demand). Total demand is `rho * D_ref`, split over OD pairs by the instance's Dirichlet weights.

## 11. Grid generator (proposal)

`n` by `n` lattice, bidirectional links between 4-neighbours. BPR `alpha` and `beta` as fitted in section 15.6 (C-BPR). Per undirected pair: `t0 ~ Uniform[1, 3]` minutes, `c ~ Uniform[600, 1800]` veh/h, same values in both directions. `K = 12` OD pairs drawn without replacement among node pairs at Manhattan distance at least `n - 1`, weights `Dirichlet(1, ..., 1)`. NumPy `Generator(PCG64(seed))`. Generator version recorded in every run manifest.

## 12. Compute budget and reproducibility

Single CPU core, fixed iteration caps above, wall-clock and peak memory recorded per run (feasibility section 4 gives the planning estimate). Every run records config hash, git revision, OS, CPU, Python and package versions. Commands (to be implemented at M2): `uv run flow smoke`, `uv run flow run EXP-003`, `uv run flow report`, `uv run pytest`.

## 13. Verification before any run (master prompt section 10)

Shortest paths against brute-force path enumeration on small graphs; flow conservation at every node; nonnegative costs and flows; explicit errors for disconnected OD pairs; convergence to tolerance; `MIX(0) = UE`, `MIX(1) = SO`; `TSTT(SO) <= TSTT(UE)` and `TSTT(SO) <= TSTT(FF)` on every instance; exact Braess values from EXP-001; MSA as a differential reference for UE.

## 14. Deviations

None yet (amendments before the freeze are in section 15). Any change after a freeze is dated, justified, logged in `research/decision_log.md` and analysed separately as exploratory.

## 15. Amendments before freeze (owner-approved 2026-11-24, round 2)

Authority: the owner's second-round approvals of 2026-11-24 ("Approve all"), sections 1 and 7 for FLOW, and the earlier approval of the amendment list ("yes for all others"). Where this section and an earlier section disagree, this section wins; the earlier sections were edited to match and carry a pointer here.

### 15.1 How the real data enters the study

- **Dataset.** TNTP Sioux Falls network (Transportation Networks for Research, `SiouxFalls_net.tntp`, `SiouxFalls_trips.tntp`, `SiouxFalls_flow.tntp`, pinned commit `d1639b4ef218c17928ba573e806ddf8ba5e7ae6d`). Licence: "Data sets are for academic research purposes only"; the source must be cited. Local use only: the files live in `data/raw/` (git-ignored), are fetched by `scripts/download_tntp.py` and checked against the SHA-256 values in `data/manifest.json` before every use. Nothing derived at row level is committed.
- **Role.** The synthetic grids stay the controlled part of the study and carry the primary hypothesis. Sioux Falls enters in two ways: (a) **calibration** of the BPR cost parameters of the grid generator (15.2); (b) a **second test** on a real network, the new experiment EXP-006 (15.4).
- **What is not done with the real data.** The primary estimand, the primary cell, the margin `delta`, the decision rule and the seeds are not changed by, and are not computed from, the real data.

### 15.2 Calibration method (written before any fit)

- **C-BPR (real data).** Parameters: the BPR `alpha` and `beta` of the grid cost function (section 2; planning values 0.15 and 4, previously "parameter source unverified"). Data: the `b` and `power` columns of `SiouxFalls_net.tntp`, all 76 links (the whole file is the calibration split; no part of the data involves the primary contrast, which is defined on synthetic grids only). Method: if every link carries the same value, that value is adopted; otherwise the median over links is adopted and the spread is reported. Nothing is solved: no assignment, UE, SO or R is computed for the fit. The fitted values replace the planning values in the configs (`bpr` block). S2 keeps `beta = 1` as its alternative.
- **C-S3 share (synthetic, amendment A5).** Parameter: the share `s` of the absolute calibration of S3 (section 9). Method: on the exploratory seeds 9000-9019 of the 6 by 6 generator (never the confirmatory seeds), compute for each seed `D_ff(seed) = 2 * D_ref` (the rho = 2 FF-calibrated total demand, section 10) and `C(seed)` = summed capacity of the links leaving the OD origins; set `s = median(D_ff) / median(C)`, so that the median absolute-calibrated total demand equals the median rho = 2 FF-calibrated demand. Only generator draws and free-flow loading are used; no assignment and no R is computed. The value is rounded to 6 significant digits and written into the EXP-003 S3 cell.
- **Descriptive (no parameter set).** The FF-calibrated demand level of the published Sioux Falls OD table, `rho_SF = total published demand / D_ref(Sioux Falls)`, using the section 10 definition with the published OD shares; FF loading only.
- Both fits are journaled as exploratory entries with their scripts (`scripts/calibrate.py`), and the fitted values are recorded in 15.6 after the fit.

### 15.3 Approved amendments of section 7 of the approvals (FLOW)

1. **Gradient-projection solver (A1, option a).** UE, SO and the MIX follower are solved by the path-based gradient projection of `flow.assignment.gradient_projection` (unit step, Gauss-Seidel sweep over OD pairs; one iteration is one sweep), same relative-gap definition and the same stopping rule `RG <= 1e-6` or 20,000 iterations. Frank-Wolfe as drafted is kept only as a differential reference: sensitivity S1 adds a Frank-Wolfe re-solve of the primary cell (`RG <= 1e-6`, 20,000 iterations), reported alongside and not used in any decision. The MIX compliant flow uses the SO path flows produced by the deterministic gradient-projection run (the operational choice of EXP-004 item 16, now with this solver).
2. **n = 100 per grid size (A2).** Confirmatory seeds 1000-1099 (4 by 4) and 2000-2099 (6 by 6). EXP-004 and EXP-005 use the same instances as EXP-003 (2000-2099 and 1000-1099). Decided on precision grounds only (section 5); `delta`, the primary cell and the decision rule are unchanged.
3. **Drop rho = 0.5 (A3).** EXP-003 demand levels are `rho in {1, 2, 3}`. The level was degenerate in exploratory runs (FF already the UE in most instances).
4. **UE versus SO stays primary (B2).** The primary estimand remains the median of `R(UE) = TSTT(UE) / TSTT(SO) - 1` in the 6 by 6, rho = 2 cell; FF remains the baseline in every comparison.
5. **MIX convergence (A4).** MIX(c) is converged only if both the SO reference (for `c > 0`) and the follower UE meet the tolerance; otherwise it is flagged nonconverged and handled by section 7. MIX(0) and MIX(1) are reported as identity checks (MIX(0) = UE, MIX(1) = SO), not as independent solves.
6. **S3 share (A5).** Set by the C-S3 rule of 15.2.

### 15.4 Second test on a real network: EXP-006

- **Question.** Does the primary direction (equilibrium routing exceeds the system optimum by more than `delta = 0.01`) also hold on one real road network?
- **Design.** Sioux Falls, arms FF, UE, SO, gradient projection at `RG <= 1e-6`. Demand levels: the published OD table (`rho_SF`, descriptive), and the published OD shares scaled to `rho in {1, 2, 3}` by the section 10 calibration. S1 analogue: the published level and rho = 2 re-solved at `RG <= 1e-8`.
- **Engine validation gate.** Before interpreting EXP-006, the UE link flows at the published demand must match the TNTP best-known solution (`SiouxFalls_flow.tntp`): `max_e |x_e - x_ref_e| / max_e x_ref_e <= 1e-3`. If the gate fails, EXP-006 is reported as failed (ingestion or engine mismatch) and not reinterpreted.
- **Test.** Deterministic, one network: the direction replicates if `R(UE) > 0.01` at rho = 2. Contradiction: `R(UE) <= 0.01` at rho = 2. One network supports no population claim; no interval is reported. The published level is descriptive.
- **Units.** Sioux Falls times are in 0.01 hours (TNTP README); R is dimensionless and unaffected.

### 15.5 Not changed

The primary hypothesis, `delta`, the decision rule, the bootstrap method and seed, EXP-001 and EXP-002 (beyond the solver), the S1 tolerances, S2 and the 10 percent nonconvergence rule.

### 15.6 Fitted values (recorded after the fit; exploratory journal entries)

- **C-BPR** (J-0010, `scripts/calibrate.py`, `results/exploratory/calibration-2026-11-24.json`): all 76 Sioux Falls links carry `b = 0.15` and `power = 4`; rule "constant" applies. Fitted `alpha = 0.15`, `beta = 4`. The fitted values equal the planning values, which are now sourced (TNTP README: "the traditional BPR value of B=0.15 is assumed").
- **rho_SF** (J-0010, descriptive): published total demand 360,600; `D_ref = 62,301.9`; `rho_SF = 5.788`.
- **C-S3** (J-0011): over seeds 9000-9019 (6 by 6), median rho = 2 FF-calibrated demand 4,161.76 veh/h, median summed origin capacity 38,442.5 veh/h; fitted `s = 0.10826`. In the S3 cell total demand is `s` times the summed origin capacity (multiplier 1).
- **Engine check before the freeze** (J-0012, exploratory, UE only, no SO and no R computed): gradient-projection UE on Sioux Falls at the published demand reproduces the TNTP best-known solution (objective 42.313353 versus 42.313353 in units of 1e5; maximum link-flow difference 1.3e-4 of the largest reference flow at `RG <= 1e-6`, 1.3e-6 at `1e-8`). The EXP-006 validation gate is still evaluated in the confirmatory run.
