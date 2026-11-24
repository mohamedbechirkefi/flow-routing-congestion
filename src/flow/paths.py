# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Shortest paths, reference path enumeration and all-or-nothing loading.

Tie-breaking rule (protocol section 2): among paths of equal computed cost the
lexicographically smallest node sequence wins. Labels are ordered by the pair
(cost, node sequence) with exact floating-point comparison; near-ties that differ
by rounding are decided by the computed cost. With nonnegative link costs every
extension of a label is strictly larger than the label itself (a longer tuple with
the same prefix is larger), so label setting returns, for each node, the minimal
(cost, path) label over all simple paths.
"""

from __future__ import annotations

import heapq

import numpy as np

from .network import Demand, DisconnectedError, Network, NegativeCostError

Path = tuple[int, ...]  # node sequence


def check_costs(net: Network, costs) -> list[float]:
    c = np.asarray(costs, dtype=float)
    if c.shape != (net.n_links,):
        raise NegativeCostError(f"cost vector must have shape ({net.n_links},)")
    if not np.all(np.isfinite(c)):
        raise NegativeCostError("link costs must be finite")
    if np.any(c < 0):
        raise NegativeCostError("link costs must be nonnegative")
    return c.tolist()


def shortest_path_tree(net: Network, costs, origin: int) -> tuple[list[float], list[Path | None]]:
    """Dijkstra from ``origin``. Returns (distance, path) per node; unreachable nodes get inf/None."""
    if not 0 <= origin < net.n_nodes:
        raise DisconnectedError(f"origin {origin} not in network")
    c = check_costs(net, costs)
    head = net.head.tolist()
    n = net.n_nodes
    dist = [float("inf")] * n
    path: list[Path | None] = [None] * n
    done = [False] * n
    heap: list[tuple[float, Path, int]] = [(0.0, (origin,), origin)]
    while heap:
        d, p, u = heapq.heappop(heap)
        if done[u]:
            continue
        done[u] = True
        dist[u] = d
        path[u] = p
        for e in net.out_links[u]:
            v = head[e]
            if done[v]:
                continue
            heapq.heappush(heap, (d + c[e], p + (v,), v))
    return dist, path


def shortest_path(net: Network, costs, origin: int, destination: int) -> tuple[float, Path]:
    dist, path = shortest_path_tree(net, costs, origin)
    if not 0 <= destination < net.n_nodes or path[destination] is None:
        raise DisconnectedError(f"no path from {origin} to {destination}")
    return dist[destination], path[destination]  # type: ignore[return-value]


def path_links(net: Network, path: Path) -> list[int]:
    """Link ids along a node sequence."""
    lookup = {(int(t), int(h)): e for e, (t, h) in enumerate(zip(net.tail, net.head))}
    try:
        return [lookup[(path[i], path[i + 1])] for i in range(len(path) - 1)]
    except KeyError as exc:
        raise DisconnectedError(f"node sequence {path} is not a path of the network") from exc


def path_cost(net: Network, costs, path: Path) -> float:
    c = np.asarray(costs, dtype=float)
    return float(sum(c[e] for e in path_links(net, path)))


def enumerate_simple_paths(net: Network, origin: int, destination: int, limit: int = 100_000) -> list[Path]:
    """Reference: every simple path from origin to destination (small graphs only)."""
    head = net.head.tolist()
    out: list[Path] = []

    def dfs(u: int, p: Path) -> None:
        if len(out) > limit:
            raise RuntimeError("path enumeration limit exceeded")
        if u == destination:
            out.append(p)
            return
        for e in net.out_links[u]:
            v = head[e]
            if v not in p:
                dfs(v, p + (v,))

    dfs(origin, (origin,))
    return out


def brute_force_shortest(net: Network, costs, origin: int, destination: int) -> tuple[float, Path]:
    """Reference shortest path by enumeration with the same (cost, sequence) order."""
    paths = enumerate_simple_paths(net, origin, destination)
    if not paths:
        raise DisconnectedError(f"no path from {origin} to {destination}")
    c = check_costs(net, costs)
    lookup = {(int(t), int(h)): e for e, (t, h) in enumerate(zip(net.tail, net.head))}
    best = None
    for p in paths:
        cost = 0.0
        for i in range(len(p) - 1):
            cost += c[lookup[(p[i], p[i + 1])]]
        label = (cost, p)
        if best is None or label < best:
            best = label
    return best  # type: ignore[return-value]


class LinkLookup:
    """Cached (tail, head) -> link id map for path-to-link conversion."""

    def __init__(self, net: Network):
        self.map = {(int(t), int(h)): e for e, (t, h) in enumerate(zip(net.tail, net.head))}
        self.cache: dict[Path, list[int]] = {}

    def links(self, path: Path) -> list[int]:
        got = self.cache.get(path)
        if got is None:
            got = [self.map[(path[i], path[i + 1])] for i in range(len(path) - 1)]
            self.cache[path] = got
        return got


def all_or_nothing(
    net: Network, costs, demand: Demand, lookup: LinkLookup | None = None
) -> tuple[np.ndarray, list[Path], list[float]]:
    """Assign each OD demand to its shortest path under fixed ``costs``.

    Returns (link flows, chosen path per OD pair, shortest cost per OD pair).
    Raises DisconnectedError for an OD pair without a path, whatever its demand.
    """
    demand.check_against(net)
    lookup = lookup or LinkLookup(net)
    x = np.zeros(net.n_links)
    chosen: list[Path] = []
    kappa: list[float] = []
    trees: dict[int, tuple[list[float], list[Path | None]]] = {}
    for p in demand.pairs:
        if p.origin not in trees:
            trees[p.origin] = shortest_path_tree(net, costs, p.origin)
        dist, paths = trees[p.origin]
        path = paths[p.destination]
        if path is None:
            raise DisconnectedError(f"no path from {p.origin} to {p.destination}")
        chosen.append(path)
        kappa.append(dist[p.destination])
        if p.demand > 0:
            for e in lookup.links(path):
                x[e] += p.demand
    return x, chosen, kappa
