# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Outcome metrics (protocol section 3). Pure functions of a network, demand and assignment."""

from __future__ import annotations

import numpy as np

from .assignment import AssignmentResult
from .network import Demand, FlowError, Network
from .paths import LinkLookup, shortest_path_tree


def weighted_quantile(values, weights, q: float) -> float:
    """Smallest value v such that the weight share of values <= v is at least q."""
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if v.size == 0 or v.shape != w.shape:
        raise FlowError("weighted_quantile needs equal nonempty arrays")
    if np.any(w < 0) or w.sum() <= 0:
        raise FlowError("weights must be nonnegative with a positive sum")
    if not 0 <= q <= 1:
        raise FlowError("q must lie in [0, 1]")
    order = np.argsort(v, kind="stable")
    cw = np.cumsum(w[order]) / w.sum()
    idx = int(np.searchsorted(cw, q - 1e-12, side="left"))
    return float(v[order][min(idx, v.size - 1)])


def weighted_gini(values, weights) -> float:
    """G = sum_i sum_j w_i w_j |v_i - v_j| / (2 W^2 mean). Values must be nonnegative."""
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if v.size == 0 or v.shape != w.shape:
        raise FlowError("weighted_gini needs equal nonempty arrays")
    if np.any(v < 0) or np.any(w < 0) or w.sum() <= 0:
        raise FlowError("values and weights must be nonnegative, weights with positive sum")
    W = w.sum()
    mean = float(np.dot(w, v) / W)
    if mean == 0:
        return 0.0
    diff = np.abs(v[:, None] - v[None, :])
    return float((w[:, None] * w[None, :] * diff).sum() / (2.0 * W * W * mean))


def node_balance(net: Network, demand: Demand, x: np.ndarray) -> np.ndarray:
    """Inflow - outflow + net supply per node; zero for a feasible flow (conservation)."""
    bal = np.zeros(net.n_nodes)
    np.add.at(bal, net.head, x)
    np.subtract.at(bal, net.tail, x)
    for p in demand.pairs:
        bal[p.origin] += p.demand
        bal[p.destination] -= p.demand
    return bal


def evaluate(net: Network, demand: Demand, res: AssignmentResult) -> dict:
    """Metrics of an assignment: TSTT, mean and p95 trip time, congestion, fairness."""
    x = res.link_flow
    t = net.link_time(x)
    tstt = float(np.dot(x, t))
    total = demand.total
    lookup = LinkLookup(net)
    ff = net.free_flow_time()
    trees: dict[int, list[float]] = {}
    times, weights, stretch = [], [], []
    for p, pf in zip(demand.pairs, res.path_flows):
        if p.origin not in trees:
            trees[p.origin] = shortest_path_tree(net, ff, p.origin)[0]
        ffmin = trees[p.origin][p.destination]
        for path, f in pf.items():
            if f <= 0:
                continue
            tp = float(sum(t[e] for e in lookup.links(path)))
            times.append(tp)
            weights.append(f)
            stretch.append(tp / ffmin if ffmin > 0 else float("nan"))
    out: dict = {
        "tstt": tstt,
        "total_demand": total,
        "mean_trip_time": tstt / total if total > 0 else None,
        "p95_trip_time": weighted_quantile(times, weights, 0.95) if times else None,
        "max_trip_time": max(times) if times else None,
        "gini_stretch": None,
        "flow_weighted_vc": None,
        "share_links_over_capacity": None,
        "max_vc": None,
        "n_used_paths": len(times),
    }
    st = np.asarray(stretch)
    if times and np.all(np.isfinite(st)):
        out["gini_stretch"] = weighted_gini(st, weights)
    if net.capacity is not None:
        vc = x / net.capacity
        out["flow_weighted_vc"] = float(np.dot(x, vc) / x.sum()) if x.sum() > 0 else 0.0
        out["share_links_over_capacity"] = float(np.mean(vc > 1.0))
        out["max_vc"] = float(vc.max())
    return out
