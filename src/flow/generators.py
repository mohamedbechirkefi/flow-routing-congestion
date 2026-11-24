# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Synthetic networks: the Braess example and seeded BPR grids (protocol sections 2, 10, 11)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .network import Demand, DemandError, Network, NetworkError, ODPair
from .paths import all_or_nothing

GRID_GENERATOR_VERSION = "grid-v1"
BPR_ALPHA = 0.15
BPR_BETA = 4.0

# Braess example (Braess, Nagurney and Wakolbinger 2005 translation): nodes s=0, A=1, B=2, t=3.
BRAESS_NODES = ("s", "A", "B", "t")


def braess_network(with_link: bool = True) -> Network:
    """Links a: s->A 10x, b: s->B x+50, c: A->t x+50, d: B->t 10x, e: A->B x+10."""
    tail = [0, 0, 1, 2]
    head = [1, 2, 3, 3]
    A = [0.0, 50.0, 50.0, 0.0]
    B = [10.0, 1.0, 1.0, 10.0]
    names = ["a", "b", "c", "d"]
    if with_link:
        tail.append(1)
        head.append(2)
        A.append(10.0)
        B.append(1.0)
        names.append("e")
    return Network(
        n_nodes=4,
        tail=np.array(tail),
        head=np.array(head),
        A=np.array(A),
        B=np.array(B),
        P=np.ones(len(tail)),
        capacity=None,
        link_names=tuple(names),
        name="braess" if with_link else "braess-without-e",
    )


def braess_demand(d: float) -> Demand:
    return Demand((ODPair(0, 3, float(d)),))


@dataclass(frozen=True)
class GridInstance:
    """A seeded grid plus its seeded OD sample with Dirichlet weights summing to 1."""

    network: Network
    od: tuple[tuple[int, int], ...]
    weights: tuple[float, ...]
    n: int
    seed: int
    generator_version: str = GRID_GENERATOR_VERSION

    def demand(self, total: float) -> Demand:
        if not np.isfinite(total) or total < 0:
            raise DemandError("total demand must be finite and nonnegative")
        return Demand(tuple(ODPair(o, d, total * w) for (o, d), w in zip(self.od, self.weights)))


def make_grid(
    n: int,
    seed: int,
    beta: float = BPR_BETA,
    alpha: float = BPR_ALPHA,
    k_pairs: int = 12,
    capacity_scale: float = 1.0,
) -> GridInstance:
    """n x n lattice with bidirectional 4-neighbour links (protocol section 11).

    Draw order (part of generator version grid-v1): t0 ~ U[1,3] min for every
    undirected pair, then c ~ U[600,1800] veh/h for every undirected pair, then
    K OD pairs without replacement among ordered pairs at Manhattan distance
    >= n - 1, then Dirichlet(1,...,1) weights. Undirected pairs are ordered by
    node id, right neighbour before lower neighbour. Capacity scaling (EXP-004)
    multiplies capacities after the draws, so instances stay matched.
    """
    if not isinstance(n, int) or n < 2:
        raise NetworkError("grid size n must be an integer >= 2")
    if not (beta >= 1 and np.isfinite(beta)) or not (alpha >= 0 and np.isfinite(alpha)):
        raise NetworkError("need beta >= 1 and alpha >= 0")
    if not (capacity_scale > 0 and np.isfinite(capacity_scale)):
        raise NetworkError("capacity_scale must be positive")
    rng = np.random.Generator(np.random.PCG64(seed))
    und: list[tuple[int, int]] = []
    for r in range(n):
        for c in range(n):
            u = r * n + c
            if c + 1 < n:
                und.append((u, u + 1))
            if r + 1 < n:
                und.append((u, u + n))
    m = len(und)
    t0 = rng.uniform(1.0, 3.0, size=m)
    cap = rng.uniform(600.0, 1800.0, size=m)
    tail, head, tt, cc = [], [], [], []
    for k, (u, v) in enumerate(und):
        for a, b in ((u, v), (v, u)):
            tail.append(a)
            head.append(b)
            tt.append(t0[k])
            cc.append(cap[k] * capacity_scale)
    tt_a = np.array(tt)
    cc_a = np.array(cc)
    candidates = [
        (i, j)
        for i in range(n * n)
        for j in range(n * n)
        if i != j and abs(i // n - j // n) + abs(i % n - j % n) >= n - 1
    ]
    if len(candidates) < k_pairs:
        raise DemandError(f"only {len(candidates)} OD candidates for K={k_pairs}")
    pick = rng.choice(len(candidates), size=k_pairs, replace=False)
    od = tuple(candidates[int(i)] for i in pick)
    weights = rng.dirichlet(np.ones(k_pairs))
    net = Network(
        n_nodes=n * n,
        tail=np.array(tail),
        head=np.array(head),
        A=tt_a,
        B=tt_a * alpha / cc_a**beta,
        P=np.full(len(tail), float(beta)),
        capacity=cc_a,
        name=f"grid{n}x{n}-seed{seed}",
    )
    return GridInstance(net, od, tuple(float(w) for w in weights), n, seed)


def reference_demand_ff(inst: GridInstance) -> float:
    """D_ref: total demand at which FF all-or-nothing loading brings the most loaded link to x/c = 1."""
    x, _, _ = all_or_nothing(inst.network, inst.network.free_flow_time(), inst.demand(1.0))
    assert inst.network.capacity is not None
    peak = float(np.max(x / inst.network.capacity))
    if peak <= 0:
        raise DemandError("FF loading is zero; cannot calibrate demand")
    return 1.0 / peak


def reference_demand_absolute(inst: GridInstance, share: float) -> float:
    """S3 calibration: share of the summed capacity of links leaving the OD origins."""
    if not (share > 0 and np.isfinite(share)):
        raise DemandError("share must be positive")
    net = inst.network
    assert net.capacity is not None
    origins = sorted({o for o, _ in inst.od})
    total_cap = sum(float(net.capacity[e]) for o in origins for e in net.out_links[o])
    return share * total_cap
