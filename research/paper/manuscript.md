<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
<!-- Status: independent research manuscript / preprint draft, not peer-reviewed. M4 synthesis, 2026-11-25. Every number below comes from a committed result file; the mapping is research/publication/artifact_manifest.json. -->

# Individually optimal routing and total travel time on synthetic grid networks: a preregistered simulation study

**Status.** Independent research manuscript / preprint draft, not peer-reviewed. Version M4 (2026-11-25).

## Author and affiliation metadata

Mohamed Bechir Kefi (no affiliation; owner-approved metadata, freeze record C3). An AI system (Claude, Anthropic) was used as a research and development assistant; it is not an author (see the AI assistance statement).

## Abstract

When every traveller picks the route that is fastest for themselves, total travel time can exceed what a coordinated assignment would achieve. We measured this gap in a small, fully offline simulation study whose confirmatory protocol was frozen before any confirmatory instance was solved. On 100 seeded 6 by 6 lattice networks with quartic (BPR) link costs, at twice the demand at which free-flow routing first saturates a link, the median excess of user-equilibrium total travel time over the system optimum was 0.0232 (one-sided 95 percent bootstrap lower bound 0.0213), rejecting the preregistered null hypothesis of an excess of at most 1 percent. The decision held at solver tolerances of 1e-4 and 1e-8 and under an alternative demand calibration, but not with linear-in-flow costs (median 0.0030) or at light demand. Free-flow shortest-path routing was far worse than equilibrium routing under congestion (paired median difference 0.201). In one operationalisation of partial compliance, routing more travellers system-optimally lowered the excess at every step. On one real test network (Sioux Falls), which its maintainers do not consider realistic, the excess was 0.0145, just above the margin. Two exact checks on the Braess network were contradicted under their frozen 1e-6 rule, with residuals of 1e-5 to 6e-5 at the frozen solver tolerance; an exploratory rerun at a tighter tolerance met the rule. The results concern static deterministic assignment on synthetic networks and say nothing about any real city or navigation product.

## Keywords

traffic assignment; user equilibrium; system optimum; price of anarchy; Braess paradox; preregistration

## 1. Introduction

Route-guidance tools and individual drivers usually seek the route that is fastest for the traveller. A classical result of transport economics is that a population of such choices, at equilibrium, need not minimise the total time spent travelling by everyone, and that adding a road can even make every traveller slower (Braess, Nagurney and Wakolbinger 2005). How large the gap is in a given family of networks is an empirical question about that family.

This study asks one question: **can individually optimal routing worsen collective travel time, and by how much, in a controlled family of synthetic congestible networks?** It is a simulation study. It does not model any commercial navigation product, makes no prediction for any real city and says nothing about how real drivers behave.

Hypotheses were fixed before any confirmatory instance was solved (Section 4.1):

- **Primary (EXP-003).** H0: the median over 6 by 6 grid instances of the relative excess `R(UE)` of user-equilibrium (UE) over system-optimal (SO) total travel time, at demand level rho = 2, is at most delta = 0.01. H1: it exceeds 0.01.
- **Exact checks (EXP-001, EXP-002).** The engine reproduces the published Braess example and a hand-derived demand interval in which the extra link raises equilibrium travel time.
- **Compliance (EXP-004).** The median excess decreases strictly as the share of travellers routed system-optimally rises.
- **Braess links (EXP-005, optional).** Some 4 by 4 grid instances contain a link whose removal lowers equilibrium total travel time.
- **Real network (EXP-006).** The primary direction also holds on the Sioux Falls test network.

**Contributions,** stated narrowly:

1. a small tested engine that reproduces the Braess example and the published Sioux Falls equilibrium;
2. a preregistered, 100-instance measurement of the UE-to-SO gap and of the free-flow baseline gap on seeded BPR grids, with paired bootstrap intervals and sensitivity analyses that could have exposed the gap as an artefact of solver tolerance, cost curvature or demand calibration;
3. a compliance sweep and a single-link removal scan on the same instances;
4. a complete public record of every result, including two exact checks that failed their own frozen rule.

No novelty is claimed for any theoretical statement.

## 2. Related work

Only sources actually opened are used for content statements. Their reading level is given in brackets; sources whose text was not opened are cited for attribution only.

- **The paradox.** Braess's 1968 paper, read in the English translation of Braess, Nagurney and Wakolbinger (2005) [read], gives a four-node network in which, at total flow 6, the equilibrium with an added link has path flows 2, 2 and 2 and travel time 92, while eliminating the link makes the equilibrium coincide with the optimal flow. The Supernetworks Center page (Nagurney, n.d.) [read] gives the link costs `10f_a`, `f_b + 50`, `f_c + 50`, `10f_d`, `f_e + 10` and the travel time 83 without the added link. EXP-001 reproduces this example.
- **Price of anarchy.** Roughgarden and Tardos (2002) [author preprint; abstract, Section 1 and Theorem 4.5 checked] show that with linear latencies the total latency of selfish routing is at most 4/3 of the minimum, and that with general continuous nondecreasing latencies it can be arbitrarily worse. Our primary metric `R(UE) + 1` is this ratio, measured instead of bounded.
- **Empirical gaps.** Youn, Gastner and Jeong (2008) [arXiv version 4 read in full] study the price of anarchy on city road networks and report that closing certain streets can reduce travel time. We make no city claim; EXP-005 asks the analogous question on synthetic grids.
- **Formulations and methods.** The user-equilibrium and system-optimum principles are commonly attributed to Wardrop (1952), the convex equilibrium formulation to Beckmann, McGuire and Winsten (1955), and the Frank-Wolfe method to Frank and Wolfe (1956) and, for traffic assignment, LeBlanc, Morlok and Pierskalla (1975) [all four: metadata verified, text not read; attribution only]. Partial central control and mixed behaviour classes, related to our compliance arm, are studied by Roughgarden (2004) and Harker (1988) [metadata verified, text not read]; we do not claim that our MIX(c) arm matches either formulation.
- **Data.** The Sioux Falls network of the Transportation Networks for Research collection [README files read] is described by its maintainers as "not considered as a realistic one", useful "for code debugging", and as carrying the "traditional" BPR value B = 0.15.

Relation to prior work: EXP-001 is a replication of a published example; EXP-002 extends it to a demand interval derived by the assistant (not taken from a source); EXP-003 to EXP-005 are measurements on a synthetic family that, to our knowledge from a non-systematic search, has not been reported in this form, which is not evidence that it has not been.

## 3. Background and formal model

A directed graph `G = (V, E)` carries, on each link `e`, a nondecreasing nonnegative travel-time function `t_e(x_e)` of the link flow `x_e`. Grid links use the BPR form

`t_e(x) = t0_e (1 + alpha (x / c_e)^beta)`, with `alpha = 0.15`, `beta = 4`,

where `t0_e` is the free-flow time (minutes) and `c_e` the capacity (veh/h). The Braess network uses the linear costs above in abstract units. Origin-destination (OD) pairs `w` have demand `d_w`; path flows `h_p >= 0` satisfy `sum_{p in P_w} h_p = d_w`, and `x_e = sum_p delta_{ep} h_p`.

- **Total system travel time** `TSTT(x) = sum_e x_e t_e(x_e)` (veh min per hour).
- **Primary metric** `R(arm) = TSTT(arm) / TSTT(SO) - 1`, dimensionless, on the same instance and demand level.
- **FF (baseline).** All demand of each OD pair on its free-flow shortest path, ties broken to the lexicographically smallest node sequence.
- **UE.** No traveller can lower their own time by switching path (minimises the Beckmann objective `sum_e integral_0^{x_e} t_e(s) ds`).
- **SO.** Minimises TSTT (the same solver on marginal costs `t_e(x) + x t_e'(x)`).
- **MIX(c).** A fraction `c` of every OD demand follows `c` times the SO path flows; the rest reaches UE with that flow as fixed background. MIX(0) = UE and MIX(1) = SO by construction.
- **Relative gap** `RG = (sum_e x_e t_e(x_e) - sum_w d_w kappa_w) / sum_e x_e t_e(x_e)`, where `kappa_w` is the current shortest-path time of OD `w` (marginal costs for SO).
- **Demand level rho.** For each grid instance, `D_ref` is the total demand at which free-flow all-or-nothing loading first brings a link to `x / c = 1`. Total demand is `rho * D_ref`, split over OD pairs by the instance's Dirichlet weights.

Two analytic facts frame the results. In the Braess network at demand 6 the UE path time is 83 without the extra link and 92 with it. For the same network the assistant derived, and exact rational tests confirmed before the freeze, that the link raises UE time exactly for `d in (80/31, 80/9)`, with a regime change at `d = 40/11` where the outer paths start to carry flow.

## 4. Methods

### 4.1 Design and protocol registration

The study protocol (`research/protocol.md`, v1.0) and six experiment protocols were frozen by the owner on 2026-11-24 at revision `ca8b750`, with SHA-256 hashes of every protocol and confirmatory config recorded in `research/freeze.json` and decision D-011. A freeze guard in the runner refuses any confirmatory config whose hash differs from the recorded one. The primary estimand, primary cell (6 by 6, rho = 2) and margin delta = 0.01 were written in the first draft of the protocol (commit `91ecb92`), before any exploratory run. Amendments made before the freeze (solver of record, sample size, dropped demand level, real-data calibration) are listed in protocol section 15.

**Disclosure (C4).** Before the freeze the assistant saw exploratory values from the analogue of the primary cell on disjoint exploratory seeds (median `R(UE)` 0.02349, n = 20; listed in `research/freeze.json`). These informed the sample-size choice only; delta, the primary cell and the decision rule were not changed after they were seen.

Confirmatory work is EXP-001 to EXP-006 as frozen. Everything labelled **exploratory** in this paper was defined after confirmatory results existed and changes no frozen verdict.

### 4.2 Networks and demand

- **Braess network** (EXP-001, EXP-002): four nodes, the five published links, demand 6 (EXP-001) or 75 demand values from 0.25 to 12.0 (EXP-002).
- **Grid generator** (grid-v1): `n` by `n` lattice with bidirectional links between 4-neighbours; per undirected pair `t0 ~ U[1, 3]` minutes and `c ~ U[600, 1800]` veh/h; 12 OD pairs drawn without replacement among node pairs at Manhattan distance at least `n - 1`, weights Dirichlet(1, ..., 1). Confirmatory seeds 1000-1099 (4 by 4) and 2000-2099 (6 by 6).
- **Sioux Falls** (EXP-006): the TNTP files at a pinned commit, checked against SHA-256 values before every use, used locally and not redistributed. All 76 links carry `B = 0.15` and power 4, which set the grid's BPR parameters (rule fixed before the fit; the fitted values equal the conventional ones). The published OD table corresponds to rho_SF = 5.788.

### 4.3 Routing policies and solvers

UE, SO and the MIX follower are solved by a path-based gradient-projection method implemented for this study (unit step; one iteration is one Gauss-Seidel sweep over OD pairs), stopping at `RG <= 1e-6` or 20,000 sweeps. Frank-Wolfe with exact line search was the solver of the draft protocol; in pre-freeze exploratory runs (journal J-0002 to J-0008) it failed to reach `RG <= 1e-6` within 20,000 iterations on most congested grid solves and on corner Braess solutions, so the owner adopted gradient projection before the freeze (amendment A1) and Frank-Wolfe was kept only as a differential reference in sensitivity S1. A MIX(c) record counts as converged only if both its SO reference and its follower UE converged.

### 4.4 Metrics

Primary: `R`. Secondary: TSTT, mean trip time (`TSTT / sum_w d_w`), demand-weighted p95 path time, flow-weighted `x/c` and share of links over capacity, the demand-weighted Gini coefficient of the stretch `time_p / FFmin_w`, and convergence (sweeps, final RG, wall-clock). The Braess effect is `Delta(d) = TSTT_UE(with e) - TSTT_UE(without e)`.

### 4.5 Statistical analysis

The independent unit is the instance; all arms and levels of an instance are solved on the same network and OD sample (matched comparison). Intervals are percentile bootstrap intervals over instances (10,000 resamples, seed 20261124), resampling instance ids for paired contrasts. EXP-003 rejects H0 if the one-sided 95 percent lower bound of the median exceeds 0.01. EXP-004 supports H1 if every consecutive paired median difference has a one-sided 95 percent lower bound above 0 at capacity scale 1.0 (no multiplicity correction; every step must pass). EXP-005 reports a Wilson 95 percent interval for the incidence. EXP-001, EXP-002 and EXP-006 are deterministic and report exact values against tolerances, without intervals. Instances with a nonconverged UE or SO solve are excluded and counted; if more than 10 percent of the primary cell were excluded the primary analysis would be reported as failed. Interpretation rules that the protocol left implicit (absolute reading of the 1e-6 tolerance; boundary estimation by line fits; one-sided EXP-004 bounds) were fixed in decision D-012 before any confirmatory output.

### 4.6 Implementation and reproducibility

Python 3.12.1 and numpy 2.5.4 on one Apple M1 Pro machine, single process per experiment. Every run records its config hash, git revision, environment and per-record status. Confirmatory runs used clean revision `8dfc66c`; the analysis code (`src/flow/confirmatory.py`) was committed before any confirmatory output (`5108a16`). The test suite (shortest paths against brute-force enumeration, flow conservation, nonnegative costs, disconnected OD pairs, convergence tolerances, MIX identities, exact Braess values) passed before the runs. Reproduction commands are in each experiment's `reproduction.md`.

## 5. Results

Every number in this section is read from the committed `analysis.json` of the experiment named, or from the exploratory output named; the mapping is in `research/publication/artifact_manifest.json`. All six confirmatory matrices completed: 10,626 records, of which 155 were nonconverged (all in the Frank-Wolfe reference cell of EXP-003) and none failed.

### 5.1 Expected versus observed

**Table 1.** Predictions, observations and verdicts under the frozen rules.

| EXP | Prediction (frozen) | Observation | Verdict (frozen rule) |
|---|---|---|---|
| EXP-001 | All Braess values within 1e-6 (absolute) of the analytic ones | 5 of 6 arm-network combinations exact (difference at most 4.4e-16); UE with link e: TSTT 551.99993809 against 552 (difference 6.19e-5) | **Contradicted** |
| EXP-002 | Paradox exactly on (80/31, 80/9); boundaries within 1e-6 | Sign of `Delta` agrees at 75 of 75 points; lower boundary within 1.3e-15; upper and middle boundaries off by 1.11e-5 and 8.76e-6 | **Contradicted** |
| EXP-003 | Median `R(UE)` (6 by 6, rho = 2) > 0.01 by its one-sided lower bound | Median 0.02317; one-sided lower bound 0.02134; n = 100, none excluded | **H0 rejected** |
| EXP-004 | Median `R(MIX(c))` strictly decreasing in c | Medians 0.02317, 0.01824, 0.01254, 0.00496, 0; all four lower bounds above 0 | **H1 supported** |
| EXP-005 | Incidence of Braess links > 0 | 77 of 100 instances (Wilson 95% 0.678 to 0.842) | **H1 supported** |
| EXP-006 | Engine gate <= 1e-3; `R(UE)` at rho = 2 > 0.01 | Gate 1.28e-4; `R(UE)` 0.01453 | **Gate passed; direction replicates** |

### 5.2 Exact checks on the Braess network (EXP-001, EXP-002)

**EXP-001.** Free-flow and system-optimal values, and the UE without the extra link, matched the analytic values exactly (largest difference 4.4e-16). The UE with the link stopped after 6 sweeps at RG 7.29e-8 with TSTT 551.99993809, mean trip time 91.99998968 and zigzag path flow 1.99999845 against 552, 92 and 2. The 6.19e-5 TSTT difference exceeds the frozen absolute tolerance of 1e-6, so EXP-001 is **contradicted** under its frozen rule. The published effect (83 without the link, 92 with it) is reproduced to the solver's tolerance.

**EXP-002.** Over 75 demand values, adding the link raised UE travel time at exactly the predicted points (main sweep: 2.75 to 8.75) and at none outside. The lower paradox boundary was recovered as 2.580645161290321 (80/31 within 1.3e-15). The two boundaries estimated from the middle regime, where UE uses three paths, were 8.888899966 (80/9, difference 1.11e-5) and 3.636354878 (40/11, difference 8.76e-6). EXP-002 is **contradicted** under its frozen rule. The largest per-point UE time error was 1.06e-3, at d = 3.64 just above the regime change (Figure 1).

![EXP-002 (confirmatory): equilibrium path time against total demand with and without link e, analytic and computed (left), and the difference in equilibrium total travel time with the predicted paradox interval shaded (right). Deterministic; no intervals. Source: `research/experiments/EXP-002/figures/exp002_sweep.png`.](../experiments/EXP-002/figures/exp002_sweep.png){width=100%}

**Protocol and config mismatch (disclosed).** EXP-001 protocol item 5 states a relative gap of 1e-10 "for this run" and item 17 a 1e-6 versus 1e-10 sensitivity, but the frozen config runs at 1e-6, and EXP-002's frozen config also uses 1e-6 while its contradiction threshold is 1e-6. The confirmatory runs used the frozen configs. The owner decided on 2026-11-25 that the frozen verdicts stand and that a 1e-10 rerun be reported beside them as an exploratory check.

**Exploratory check at RG <= 1e-10 (J-0022).** The frozen configs were rerun with only the tolerance changed and analysed with the frozen analysis code unchanged:

| Run (exploratory) | Records | Largest final RG | Result of the frozen analysis |
|---|---|---|---|
| X-EXP-001-TOL1E-10 | 6 ok | 1.77e-11 | "reproduced"; largest difference 7.53e-9 (TSTT 552.0000000075) |
| X-EXP-002-TOL1E-10 | 450 ok | 9.59e-11 | "derivation confirmed"; boundaries within 1.3e-15 (80/31), 7.0e-10 (40/11), 1.5e-9 (80/9); sign agrees at 75 of 75 points |

The largest per-point UE time error in the exploratory EXP-002 run was still 3.37e-6, at d = 3.64; per-point time agreement is not a criterion of the frozen rule. This check is consistent with the reading that the confirmatory contradictions come from the frozen solver tolerance rather than from the engine or the derivation. It was defined after the confirmatory results were seen and does not change either frozen verdict.

### 5.3 Primary result: equilibrium excess on grids (EXP-003)

In the primary cell (6 by 6, rho = 2, n = 100, none excluded) the median `R(UE)` was **0.02317** (mean 0.02575; quartiles 0.01732 to 0.03160; range 0.00386 to 0.06667). The one-sided 95 percent lower bound was 0.02134 and the two-sided 95 percent interval [0.02075, 0.02559]. **H0 is rejected.** The upper bound is above 0.01, so the loss is not "practically negligible" in the protocol's sense.

**Table 2.** Median `R` and 95 percent bootstrap interval by grid size and demand level (n = 100 per cell; every arm converged in every cell). Source: `research/experiments/EXP-003/analysis.json` (`per_cell`).

| Size | rho | R(UE) | R(FF) | Paired R(FF) - R(UE) |
|---|---|---|---|---|
| 4x4 | 1 | 0.00409 [0.00253, 0.00553] | 0.0081 [0.0063, 0.0098] | 0.0008 [0.0000, 0.0025] |
| 4x4 | 2 | 0.03479 [0.02785, 0.03803] | 0.3324 [0.3054, 0.3436] | 0.2951 [0.2654, 0.3210] |
| 4x4 | 3 | 0.04538 [0.04082, 0.05448] | 1.6884 [1.5706, 1.8056] | 1.6332 [1.5038, 1.7480] |
| 6x6 | 1 | 0.00305 [0.00223, 0.00361] | 0.0053 [0.0044, 0.0066] | 0.0005 [0.0000, 0.0015] |
| 6x6 | 2 | 0.02317 [0.02075, 0.02559] | 0.2275 [0.2078, 0.2498] | 0.2007 [0.1782, 0.2202] |
| 6x6 | 3 | 0.03744 [0.03295, 0.04152] | 1.2372 [1.1569, 1.3924] | 1.2101 [1.1188, 1.3400] |

The equilibrium excess grows with demand at both sizes and is below delta at rho = 1. The free-flow baseline is close to UE at rho = 1 and far worse once demand is congested. Equilibrium routing raised the Gini coefficient of the stretch slightly over SO in every cell (6 by 6, rho = 2: paired median 0.00408, interval [0.00279, 0.00488]); p95 trip-time differences were small and of both signs (supplementary Table S3). See Figure 2.

![EXP-003 (confirmatory): per-instance R for UE and FF by demand level on 4 by 4 and 6 by 6 grids (grey), with medians and 95 percent bootstrap intervals (red); the dashed line is delta = 0.01; symmetric logarithmic vertical axis. Source: `research/experiments/EXP-003/figures/exp003_R_by_cell.png`.](../experiments/EXP-003/figures/exp003_R_by_cell.png){width=100%}

**Table 3.** Sensitivity analyses on the primary cell (6 by 6, rho = 2). Source: `analysis.json` (`sensitivity`).

| Cell | n used (excluded) | Median R(UE) | One-sided LB | Two-sided 95% CI | Same decision as primary |
|---|---|---|---|---|---|
| Primary (RG 1e-6) | 100 (0) | 0.02317 | 0.02134 | [0.02075, 0.02559] | n/a |
| S1, RG 1e-4 | 100 (0) | 0.02305 | 0.02131 | [0.02057, 0.02552] | yes |
| S1, RG 1e-8 | 100 (0) | 0.02317 | 0.02134 | [0.02075, 0.02559] | yes |
| S2, beta = 1 | 100 (0) | 0.00304 | 0.00274 | [0.00264, 0.00360] | **no** |
| S3, absolute calibration | 100 (0) | 0.02136 | 0.01847 | [0.01781, 0.02369] | yes |
| S1, Frank-Wolfe reference (no decision) | 7 (93) | 0.01407 | 0.00981 | [0.00981, 0.02904] | n/a |

Against the primary values, the paired median change was -9.9e-6 at RG 1e-4 and 5.3e-12 at RG 1e-8. The Frank-Wolfe reference converged on only 7 of 100 instances (SO) and provides no independent check. See Figure 3.

![EXP-003 sensitivity analyses: median R(UE) on 6 by 6 grids at rho = 2 with 95 percent bootstrap intervals, for the primary analysis, the two solver tolerances, linear costs (S2), the Frank-Wolfe reference (converged instances only) and the alternative calibration (S3); the dashed line is delta = 0.01. Source: `research/experiments/EXP-003/figures/exp003_sensitivity.png`.](../experiments/EXP-003/figures/exp003_sensitivity.png){width=100%}

### 5.4 Compliance and capacity (EXP-004)

**Table 4.** Median `R(MIX(c))` with 95 percent bootstrap intervals on the 100 EXP-003 6 by 6 instances at rho = 2. Capacity scale 1.0 is confirmatory; 0.8 and 1.2 are descriptive.

| Arm | Capacity 0.8 | Capacity 1.0 | Capacity 1.2 |
|---|---|---|---|
| FF | 0.59239 [0.55147, 0.65693] | 0.22745 [0.20778, 0.24982] | 0.09698 [0.08765, 0.10728] |
| MIX(0) = UE | 0.03058 [0.02698, 0.03411] | 0.02317 [0.02075, 0.02559] | 0.01651 [0.01426, 0.01935] |
| MIX(0.25) | 0.02542 [0.02237, 0.02746] | 0.01824 [0.01605, 0.02124] | 0.01372 [0.01184, 0.01556] |
| MIX(0.5) | 0.01758 [0.01643, 0.01963] | 0.01254 [0.01116, 0.01400] | 0.00907 [0.00715, 0.01043] |
| MIX(0.75) | 0.00868 [0.00809, 0.00950] | 0.00496 [0.00432, 0.00600] | 0.00294 [0.00251, 0.00338] |
| MIX(1) = SO | 0 | 0 | 0 |

At capacity 1.0 the four consecutive paired median differences were 0.00415, 0.00539, 0.00725 and 0.00496, with one-sided lower bounds 0.00343, 0.00442, 0.00652 and 0.00445, all above 0: **H1 is supported**. Every step also passed at scales 0.8 and 1.2 (descriptive). The identity checks held: MIX(0) reproduced the EXP-003 UE TSTT on all 100 instances (largest relative difference 0.0) and MIX(1) gave `R = 0`. Compliant travellers' mean trip time exceeded that of the others by a median factor of 1.0051 at c = 0.25 and 1.0132 at c = 0.75 (capacity 1.0). See Figure 4.

![EXP-004 (confirmatory): median R of MIX(c) against compliance c at three capacity scales (left) and paired median differences between consecutive compliance levels at capacity 1.0 (right), with 95 percent bootstrap intervals. Source: `research/experiments/EXP-004/figures/exp004_compliance.png`.](../experiments/EXP-004/figures/exp004_compliance.png){width=100%}

### 5.5 Braess links in 4 by 4 grids (EXP-005, optional)

On the 100 EXP-003 4 by 4 instances at rho = 2, each of the 48 directed links was removed in turn (5,154 solves, no disconnecting removal). **77 of 100 instances** contained at least one link whose removal lowered TSTT_UE by more than 1e-4 relative (Wilson 95 percent [0.678, 0.842]); all 177 such links were confirmed at RG 1e-8. At the 1e-3 threshold the incidence was 67 of 100 ([0.573, 0.754]). The largest relative decrease was 0.0354 and the smallest flagged one 1.16e-4. **H1 is supported.** An exploratory materiality check (J-0023) found that 17 of 100 instances have a removal lowering TSTT_UE by more than 1e-2, and that the median effect over the 177 flagged links was 0.0030. See Figure 5.

![EXP-005 (confirmatory, optional): number of Braess links per instance at the 1e-4 threshold (left) and distribution of the relative decrease of TSTT_UE after removal, on a log10 scale (right). Source: `research/experiments/EXP-005/figures/exp005_removals.png`.](../experiments/EXP-005/figures/exp005_removals.png){width=100%}

### 5.6 One real test network (EXP-006)

The engine's UE link flows at the published Sioux Falls demand matched the TNTP best-known solution within 1.28e-4 of the largest reference flow (gate threshold 1e-3): the gate passed.

**Table 5.** Sioux Falls, deterministic, one network (no interval). Source: `research/experiments/EXP-006/analysis.json`.

| Demand level | R(UE) | R(FF) | Gini of stretch UE / SO / FF |
|---|---|---|---|
| rho = 1 | 0.00463 | 0.00614 | 0.0144 / 0.0094 / 0.0153 |
| rho = 2 | **0.01453** | 0.21769 | 0.0424 / 0.0305 / 0.1866 |
| rho = 3 | 0.03012 | 1.12283 | 0.0786 / 0.0557 / 0.4639 |
| published (rho 5.788) | 0.03973 | 8.36129 | 0.1950 / 0.1774 / 0.7022 |

At RG 1e-8, `R(UE)` was 0.01452 at rho = 2 and 0.03975 at the published level. The direction replicates at rho = 2 by a margin of 0.0045 above delta. See Figure 6.

![EXP-006 (confirmatory): R for UE and FF on the Sioux Falls network by demand level, including the published demand; one deterministic network, no interval; the dashed line is delta = 0.01. Source: `research/experiments/EXP-006/figures/exp006_R.png`.](../experiments/EXP-006/figures/exp006_R.png){width=100%}

### 5.7 Runtime

EXP-003, which includes the Frank-Wolfe reference, took 2,222.8 s on one machine; every other confirmatory experiment took under one minute (EXP-005: 48.6 s). Mean gradient-projection time per solve in the primary cell was 0.022 s (UE) and 0.049 s (SO).

## 6. Discussion

### 6.1 What the evidence supports

In this synthetic family, with quartic BPR costs and demand at twice the free-flow saturation level, equilibrium routing costs a median of about 2.3 percent more total travel time than the system optimum. The excess is not carried by a few instances: in the exploratory check J-0023, 90 of the 100 primary-cell instances individually exceeded delta. It grows with demand (Table 2) and, in the same exploratory and purely correlational check, tracks congestion within the primary cell (Spearman correlation 0.653 between `R(UE)` and the UE flow-weighted volume-to-capacity ratio, n = 100). This is consistent with, but does not establish, the mechanism named in the protocol: equilibrium travellers ignore the marginal delay they impose on others, and that delay matters only where links are loaded into the steep part of the cost curve.

The free-flow baseline matters more than the equilibrium inefficiency. At rho = 2 ignoring congestion altogether costs about nine times the equilibrium excess (paired median `R(FF) - R(UE)` 0.201 on 6 by 6 grids). At rho = 1 all three policies are within 1 percent of each other. A reader who equates "individually optimal" with "shortest path on an empty network" would therefore overstate what congestion-aware individual routing loses.

### 6.2 Competing explanations

**Table 6.** Competing explanations named in the protocols and what the results say about them.

| Conclusion | Competing explanation (protocol) | Addressed by | Status |
|---|---|---|---|
| EXP-003 primary | Solver nonconvergence inflating or shrinking the gap | S1: decision unchanged at RG 1e-4 and 1e-8; paired shifts below 1e-5 | Addressed for gradient projection. No independent solver check: the Frank-Wolfe reference failed to converge on 93 of 100 instances. |
| EXP-003 primary | Dependence on cost curvature | S2 (beta = 1): median 0.00304, below delta; 0 of 100 instances above delta (J-0023) | **Confirmed as a scope limit.** The result holds for beta = 4 only. |
| EXP-003 primary | Artefact of the demand calibration | S3 (absolute calibration): median 0.02136, same decision; 86 of 100 instances above delta (J-0023) | Addressed for the two calibrations tested. The result does depend on the demand level: below delta at rho = 1. |
| EXP-003 primary | OD sampling | 100 independent instances; 90 of 100 above delta individually (J-0023); 4 by 4 grids at rho = 2, with different draws, also exceed delta (median 0.03479) | Partly addressed. The OD count (12) and distance rule were never varied. |
| EXP-001, EXP-002 | Implementation bug, nonconvergence, tie-breaking, tolerance | FF tie rule exact; exact rational tests of the derivation; exploratory 1e-10 rerun meets the rule (J-0022) | The exploratory evidence favours the frozen solver tolerance. A small implementation error cannot be excluded by the confirmatory run alone. |
| EXP-004 | Re-equilibration of non-compliant users cancelling the benefit; nonmonotone effects; follower nonconvergence | Every step positive at every capacity scale; all MIX records converged | Addressed within this MIX definition. The link-flow scaling sensitivity (protocol item 17) was not run (owner decision, 2026-11-25). |
| EXP-005 | Apparent reductions within solver tolerance | All 177 flagged links confirmed at RG 1e-8 | Addressed. Materiality is a separate question (Section 5.5). |
| EXP-006 | Ingestion error; nonconvergence; demand scaling; single network | Engine gate 1.28e-4; S1 at 1e-8 unchanged; R reported at four levels | Ingestion and convergence addressed. One network supports no population claim. |

### 6.3 Contradictory and weak results

The two exact checks failed their own frozen rule. The reason is visible in the records: the frozen configs stop the solver at a relative gap of 1e-6 while the contradiction threshold is an absolute 1e-6 on quantities of order 500, which a solver stopping at that gap need not meet. This is a design error in the frozen protocol and config, not a property of the network; it is reported as a contradiction because that is what the frozen rule gives. The exploratory 1e-10 rerun shows that the engine meets the rule when the solver is run to the tolerance the EXP-001 protocol text intended.

The real-network replication is weak: 0.01453 against a margin of 0.01, on one network that its maintainers do not consider realistic, at a demand level defined by our own calibration. The compliance result (EXP-004) is close to what the MIX construction implies: MIX(0) is UE and MIX(1) is SO, so an overall decline is expected; the informative part is that every intermediate step declined despite re-equilibration. Most Braess links found by EXP-005 are small: the median effect is 0.0030 of TSTT_UE, below the study's own practical margin.

### 6.4 Practical significance

The excess measured here is modest: about 2 percent at the primary level, a median below 5 percent in every grid cell, and below 1 percent with linear costs or light demand. With linear costs (S2) it is far below the worst-case ratio of 4/3 that Roughgarden and Tardos (2002) prove for linear latencies. The margin delta = 0.01 is a convention fixed by the study before any run, not an externally grounded threshold of practical importance. The study supports the statement that equilibrium routing can worsen collective travel time by more than this preregistered 1 percent margin in congested synthetic networks with conventional quartic costs; it does not support any statement about the size of the effect on real roads.

## 7. Limitations and threats to validity

- **Synthetic networks.** The primary hypothesis rests on seeded lattices with 12 OD pairs. Sioux Falls is one small test network. No transfer to other topologies, sizes or real cities is implied.
- **Static deterministic assignment.** No time dynamics, queues, departure-time choice, signals or stochastic route choice.
- **Behavioural model.** "Individually optimal" means free-flow shortest paths or Wardrop equilibrium with perfect information. Synthetic agents are not people; nothing is inferred about real drivers or any navigation product.
- **Cost curvature.** The effect falls below delta at beta = 1 (S2). The BPR parameters were "fitted" from a file that itself assumes the traditional values, so the calibration confirms convention rather than measuring roads.
- **Demand definition.** rho is relative to free-flow saturation; at rho = 1 the effect is below delta.
- **Solver.** All arms use one solver implementation; the Frank-Wolfe reference did not converge on most instances, so there is no independent solver check on grids. The engine is externally validated on the Braess network and on Sioux Falls (UE only; no published SO was used).
- **Exact checks.** EXP-001 and EXP-002 are contradicted under their frozen rule; the 1e-10 evidence is exploratory and post hoc.
- **Pre-freeze exposure.** Exploratory values of the primary-cell analogue were seen before the freeze (C4).
- **Shared instances.** EXP-004 and EXP-005 reuse EXP-003 instances; they are not independent replications.
- **Untested sensitivities.** EXP-004 link-flow scaling (item 17) was not run, by owner decision.
- **Provenance flags.** Three confirmatory manifests record `dirty: true` because untracked analysis outputs existed during the runs; no tracked file differed (D-014). One test executed the EXP-005 config once before the official run; its output was not inspected (D-013).
- **Statistical.** Secondary contrasts are descriptive and not corrected for multiplicity. Nonrejection at rho = 1 is not evidence of equivalence.

## 8. Ethics and responsible research

The study uses synthetic data and one public research network (TNTP Sioux Falls, "for academic research purposes only"), used locally and not redistributed; its source is cited. No personal data, human participants or behavioural data were involved, so no ethics review was required and none is claimed. The results must not be presented as evidence about real drivers, real cities or any commercial routing product.

## 9. Conclusion and future work

On congested synthetic grids with quartic BPR costs, individually optimal (equilibrium) routing increased total travel time over the system optimum by a median of 2.3 percent, above the preregistered 1 percent margin, robustly to solver tolerance and demand calibration but not to linear costs, and not at light demand (rho = 1), where all policies were within 1 percent of the optimum in median. Free-flow routing was far worse; partial system-optimal compliance reduced the excess at every step; small Braess links were common; one real test network showed the same direction at a small margin. Two exact checks failed their frozen rule because of a protocol and config tolerance mismatch.

Feasible extensions, each needing a new registered protocol: an independent second solver that converges on grids; varied OD counts and topologies; the link-flow compliance sensitivity; further TNTP networks; and a registered rerun of the exact checks at the intended tolerance.

## Data and code availability

All code, configs, frozen protocols, analyses, figures and confirmatory per-record tables are in this repository (paths given in each experiment report). The Sioux Falls files are not redistributed; `scripts/download_tntp.py` fetches them from the pinned commit and checks their SHA-256 values; the EXP-006 per-link results are kept local for the same reason. Repository URL: [to be added on owner-approved release].

## Funding, competing interests and AI assistance

No funding. No competing interests. An AI system (Claude, Anthropic) acted as research and development assistant: it drafted protocols, implemented the engine and tests, ran the experiments and drafted the reports and this manuscript. The owner approved the protocol freeze, the amendments and every decision recorded as an owner decision. Numbers were checked by an automated trace against committed result files (`research/publication/evidence_audit.md`) and an internal second review pass (`research/publication/review_pass_2.md`). These are internal quality controls, not peer review.

## References

- Beckmann, M. J., McGuire, C. B., Winsten, C. B. (1955). *Studies in the Economics of Transportation*. RAND Corporation, RM-1488. https://www.rand.org/pubs/research_memoranda/RM1488.html [metadata verified; text not read].
- Braess, D., Nagurney, A., Wakolbinger, T. (2005). On a paradox of traffic planning. *Transportation Science* 39(4), 446-450. doi:10.1287/trsc.1050.0127 [read].
- Frank, M., Wolfe, P. (1956). An algorithm for quadratic programming. *Naval Research Logistics Quarterly* 3(1-2), 95-110. doi:10.1002/nav.3800030109 [metadata verified; text not read].
- Harker, P. T. (1988). Multiple equilibrium behaviors on networks. *Transportation Science* 22(1), 39-46. doi:10.1287/trsc.22.1.39 [metadata verified; text not read].
- LeBlanc, L. J., Morlok, E. K., Pierskalla, W. P. (1975). An efficient approach to solving the road network equilibrium traffic assignment problem. *Transportation Research* 9(5), 309-318. doi:10.1016/0041-1647(75)90030-1 [metadata verified; text not read].
- Nagurney, A. (n.d.). The Braess Paradox. Virtual Center for Supernetworks, UMass Amherst. https://supernet.isenberg.umass.edu/facts/braess.html [read 2026-11-24].
- Roughgarden, T. (2004). Stackelberg scheduling strategies. *SIAM Journal on Computing* 33(2), 332-350. doi:10.1137/S0097539701397059 [metadata verified; text not read].
- Roughgarden, T., Tardos, E. (2002). How bad is selfish routing? *Journal of the ACM* 49(2), 236-259. doi:10.1145/506147.506153 [author preprint of 5 December 2001; abstract (page 1), Section 1 "Our Results" (page 3) and Theorem 4.5 (page 17) checked; journal version not checked].
- Transportation Networks for Research Core Team. Transportation Networks for Research (TNTP), repository README and SiouxFalls/README.md at commit d1639b4ef218c17928ba573e806ddf8ba5e7ae6d. https://github.com/bstabler/TransportationNetworks [read 2026-11-24 and 2026-11-25].
- Wardrop, J. G. (1952). Some theoretical aspects of road traffic research. *Proceedings of the Institution of Civil Engineers* 1(3), 325-362. doi:10.1680/ipeds.1952.11259 [metadata verified; text not read].
- Youn, H., Gastner, M. T., Jeong, H. (2008). Price of anarchy in transportation networks: efficiency and optimality control. *Physical Review Letters* 101(12), 128701. doi:10.1103/PhysRevLett.101.128701 [arXiv:0712.1598 version 4 of 7 August 2008 read in full, pages 1 to 4; journal version not checked].

## Supplementary appendix

See `research/paper/supplementary.md`: complete experimental matrix (S1), extended tables (S2, S3), configurations (S4), robustness and exploratory results (S5), experiment reports (S6) and deviations and owner decisions (S7).
