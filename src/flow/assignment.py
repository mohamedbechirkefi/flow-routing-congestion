# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Traffic assignment arms: FF (baseline), UE and SO (Frank-Wolfe), MIX(c), MSA reference.

All solvers are deterministic given their inputs. Path flows are tracked by
storing the all-or-nothing path of each iteration with its convex weight
(protocol section 3), so path-level metrics (p95, fairness) are available.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from .network import Demand, FlowError, ODPair, Network
from .paths import LinkLookup, Path, all_or_nothing

DEFAULT_TOL = 1e-6
DEFAULT_MAX_ITER = 20_000


@dataclass
class AssignmentResult:
    """Outcome of one assignment solve.

    ``path_flows[k]`` maps node sequences to flow for OD pair ``k``.
    ``rel_gap`` is the relative gap at the returned flow (protocol section 2).
    """

    arm: str
    link_flow: np.ndarray
    path_flows: list[dict[Path, float]]
    iterations: int
    rel_gap: float
    converged: bool
    runtime_s: float
    gap_trace: list[tuple[int, float]] = field(default_factory=list)
    extra: dict = field(default_factory=dict)


def _cost_fn(net: Network, objective: str, background: np.ndarray):
    if objective == "ue":
        return lambda x: net.link_time(x + background)
    if objective == "so":
        if np.any(background != 0):
            raise FlowError("system-optimal solve with background flow is not defined")
        return net.marginal_cost
    raise FlowError(f"unknown objective {objective!r}")


def relative_gap(x: np.ndarray, costs: np.ndarray, demand: Demand, kappa: list[float]) -> float:
    """RG = (sum_e x_e c_e - sum_w d_w kappa_w) / sum_e x_e c_e (0 when demand is zero)."""
    num = float(np.dot(x, costs))
    if num <= 0.0:
        return 0.0
    shortest = sum(p.demand * k for p, k in zip(demand.pairs, kappa))
    return (num - shortest) / num


def _line_search(cost_fn, x: np.ndarray, direction: np.ndarray, tol: float = 1e-14, max_steps: int = 200) -> float:
    """Exact line search on the convex objective by bisection of its derivative.

    phi'(lam) = sum_e direction_e * c_e(x + lam * direction), nondecreasing in lam.
    """

    def deriv(lam: float) -> float:
        return float(np.dot(direction, cost_fn(np.maximum(x + lam * direction, 0.0))))

    if deriv(1.0) <= 0.0:
        return 1.0
    if deriv(0.0) >= 0.0:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(max_steps):
        mid = 0.5 * (lo + hi)
        if deriv(mid) > 0.0:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def free_flow(net: Network, demand: Demand) -> AssignmentResult:
    """FF baseline: all demand on free-flow shortest paths (all-or-nothing on A)."""
    t = time.perf_counter()
    x, chosen, _ = all_or_nothing(net, net.free_flow_time(), demand)
    paths = [({path: p.demand} if p.demand > 0 else {}) for p, path in zip(demand.pairs, chosen)]
    return AssignmentResult("FF", x, paths, 0, float("nan"), True, time.perf_counter() - t)


def frank_wolfe(
    net: Network,
    demand: Demand,
    objective: str = "ue",
    background: np.ndarray | None = None,
    tol: float = DEFAULT_TOL,
    max_iter: int = DEFAULT_MAX_ITER,
    trace_every: int = 0,
) -> AssignmentResult:
    """Frank-Wolfe for UE (Beckmann objective) or SO (total travel time).

    Stops when RG <= tol (converged) or after ``max_iter`` line-search updates
    (flagged nonconverged). ``background`` is a fixed link flow added before costs
    are evaluated (used by MIX); it does not count in the returned link flow.
    """
    if not (np.isfinite(tol) and tol > 0):
        raise FlowError("tol must be positive")
    if max_iter < 0:
        raise FlowError("max_iter must be >= 0")
    start = time.perf_counter()
    bg = np.zeros(net.n_links) if background is None else np.asarray(background, dtype=float)
    if bg.shape != (net.n_links,) or np.any(bg < 0) or not np.all(np.isfinite(bg)):
        raise FlowError("background flow must be a finite nonnegative link vector")
    cost_fn = _cost_fn(net, objective, bg)
    arm = "UE" if objective == "ue" else "SO"
    lookup = LinkLookup(net)
    x, chosen, _ = all_or_nothing(net, cost_fn(np.zeros(net.n_links)), demand, lookup)
    paths: list[dict[Path, float]] = [({c: p.demand} if p.demand > 0 else {}) for p, c in zip(demand.pairs, chosen)]
    trace: list[tuple[int, float]] = []
    it = 0
    while True:
        costs = cost_fn(x)
        y, chosen, kappa = all_or_nothing(net, costs, demand, lookup)
        rg = relative_gap(x, costs, demand, kappa)
        if trace_every and it % trace_every == 0:
            trace.append((it, rg))
        if rg <= tol:
            converged = True
            break
        if it >= max_iter:
            converged = False
            break
        d = y - x
        lam = _line_search(cost_fn, x, d)
        if lam <= 0.0:
            # no descent possible along the FW direction at machine precision
            converged = rg <= tol
            break
        x = np.maximum(x + lam * d, 0.0)
        for k, (p, c) in enumerate(zip(demand.pairs, chosen)):
            if p.demand <= 0:
                continue
            pf = paths[k]
            for key in pf:
                pf[key] *= 1.0 - lam
            pf[c] = pf.get(c, 0.0) + lam * p.demand
        it += 1
    for pf in paths:
        for key in [k for k, v in pf.items() if v <= 1e-12 * max(1.0, demand.total)]:
            del pf[key]
    if trace_every:
        trace.append((it, rg))
    return AssignmentResult(arm, x, paths, it, rg, converged, time.perf_counter() - start, trace)


def user_equilibrium(net: Network, demand: Demand, **kw) -> AssignmentResult:
    return frank_wolfe(net, demand, "ue", **kw)


def system_optimum(net: Network, demand: Demand, **kw) -> AssignmentResult:
    return frank_wolfe(net, demand, "so", **kw)


def msa(net: Network, demand: Demand, iterations: int = 2000) -> AssignmentResult:
    """Method of successive averages for UE (step 1/(k+1)); differential reference only."""
    start = time.perf_counter()
    lookup = LinkLookup(net)
    x, _, _ = all_or_nothing(net, net.link_time(np.zeros(net.n_links)), demand, lookup)
    rg = float("nan")
    for k in range(1, iterations + 1):
        costs = net.link_time(x)
        y, _, kappa = all_or_nothing(net, costs, demand, lookup)
        rg = relative_gap(x, costs, demand, kappa)
        x = x + (y - x) / (k + 1)
    return AssignmentResult("MSA", x, [], iterations, rg, False, time.perf_counter() - start)


def mixed_compliance(
    net: Network,
    demand: Demand,
    c: float,
    so_result: AssignmentResult | None = None,
    tol: float = DEFAULT_TOL,
    max_iter: int = DEFAULT_MAX_ITER,
) -> AssignmentResult:
    """MIX(c): share c follows the SO path flows (scaled by c); the rest reaches UE
    with the compliant flow as fixed background flow (protocol section 2)."""
    if not (0.0 <= c <= 1.0) or not np.isfinite(c):
        raise FlowError("compliance c must lie in [0, 1]")
    start = time.perf_counter()
    if so_result is None and c > 0:
        so_result = system_optimum(net, demand, tol=tol, max_iter=max_iter)
    if c > 0:
        assert so_result is not None
        comp_x = c * so_result.link_flow
        comp_paths = [{k: c * v for k, v in pf.items()} for pf in so_result.path_flows]
    else:
        comp_x = np.zeros(net.n_links)
        comp_paths = [{} for _ in demand.pairs]
    follow_demand = Demand(tuple(ODPair(p.origin, p.destination, (1.0 - c) * p.demand) for p in demand.pairs))
    fol = frank_wolfe(net, follow_demand, "ue", background=comp_x, tol=tol, max_iter=max_iter)
    total_paths: list[dict[Path, float]] = []
    for cp, fp in zip(comp_paths, fol.path_flows):
        merged = dict(cp)
        for k, v in fp.items():
            merged[k] = merged.get(k, 0.0) + v
        total_paths.append(merged)
    so_ok = True if c == 0 else bool(so_result.converged)  # type: ignore[union-attr]
    res = AssignmentResult(
        f"MIX({c:g})",
        comp_x + fol.link_flow,
        total_paths,
        fol.iterations,
        fol.rel_gap,
        fol.converged and so_ok,
        time.perf_counter() - start,
    )
    res.extra = {
        "compliance": c,
        "compliant_path_flows": comp_paths,
        "follower_path_flows": fol.path_flows,
        "so_converged": so_ok,
        "so_rel_gap": None if c == 0 else so_result.rel_gap,  # type: ignore[union-attr]
    }
    return res


def _cost_derivative(net: Network, objective: str, x: np.ndarray) -> np.ndarray:
    """d c_e / d x_e for the UE (link time) or SO (marginal cost) objective."""
    x = np.maximum(x, 0.0)
    pm1 = net.P - 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        base = np.where(pm1 == 0, 1.0, x**pm1)
    d = net.B * net.P * base
    return d if objective == "ue" else d * (1.0 + net.P)


def gradient_projection(
    net: Network,
    demand: Demand,
    objective: str = "ue",
    tol: float = DEFAULT_TOL,
    max_iter: int = 2_000,
) -> AssignmentResult:
    """Path-based gradient projection (Jayakrishnan et al. 1994 style, unit step).

    CANDIDATE SOLVER, NOT PART OF THE DRAFT PROTOCOL (which specifies Frank-Wolfe).
    Implemented at M2 as a differential reference and as the basis of a proposed
    amendment, because Frank-Wolfe did not reach RG <= 1e-6 within 20,000
    iterations on several exploratory instances. Same RG definition and stopping
    rule as ``frank_wolfe``; one iteration is one Gauss-Seidel sweep over OD pairs.
    """
    if not (np.isfinite(tol) and tol > 0):
        raise FlowError("tol must be positive")
    start = time.perf_counter()
    cost_fn = _cost_fn(net, objective, np.zeros(net.n_links))
    lookup = LinkLookup(net)
    x, chosen, _ = all_or_nothing(net, cost_fn(np.zeros(net.n_links)), demand, lookup)
    paths: list[dict[Path, float]] = [({c: p.demand} if p.demand > 0 else {}) for p, c in zip(demand.pairs, chosen)]
    it = 0
    arm = ("UE" if objective == "ue" else "SO") + "-GP"
    while True:
        costs = cost_fn(x)
        _, _, kappa = all_or_nothing(net, costs, demand, lookup)
        rg = relative_gap(x, costs, demand, kappa)
        if rg <= tol:
            converged = True
            break
        if it >= max_iter:
            converged = False
            break
        for k, p in enumerate(demand.pairs):
            if p.demand <= 0:
                continue
            costs = cost_fn(x)
            from .paths import shortest_path  # local import keeps module graph simple

            _, best = shortest_path(net, costs, p.origin, p.destination)
            pf = paths[k]
            pf.setdefault(best, 0.0)
            best_links = set(lookup.links(best))
            for path in list(pf):
                if path == best or pf[path] <= 0:
                    continue
                costs = cost_fn(x)
                deriv = _cost_derivative(net, objective, x)
                links = set(lookup.links(path))
                gap = float(sum(costs[e] for e in links) - sum(costs[e] for e in best_links))
                if gap <= 0:
                    continue
                s = float(sum(deriv[e] for e in links ^ best_links))
                delta = pf[path] if s <= 0 else min(pf[path], gap / s)
                pf[path] -= delta
                pf[best] += delta
                for e in links:
                    x[e] -= delta
                for e in best_links:
                    x[e] += delta
                x = np.maximum(x, 0.0)
            for path in [q for q, v in pf.items() if v <= 1e-14 * max(1.0, p.demand)]:
                if path != best:
                    del pf[path]
        it += 1
    return AssignmentResult(arm, x, paths, it, rg, converged, time.perf_counter() - start)
