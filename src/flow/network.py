# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Directed network, link cost model and origin-destination demand.

Every link cost has the unified polynomial form

    t_e(x) = A_e + B_e * x ** P_e      (time units per traveller)

with ``A_e >= 0``, ``B_e >= 0`` and ``P_e >= 1``. This covers both models used by
the study:

* linear costs of the Braess example: ``A = a``, ``B = b``, ``P = 1``;
* BPR costs: ``t0 * (1 + alpha * (x / c) ** beta)`` gives ``A = t0``,
  ``B = t0 * alpha / c ** beta`` and ``P = beta``.

Units: flows in vehicles per hour (veh/h) for grids, abstract demand units for the
Braess network; times in minutes for grids, abstract time units for Braess.
All functions are pure: inputs are not mutated.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


class FlowError(ValueError):
    """Base class of every explicit error raised by the FLOW engine."""


class NetworkError(FlowError):
    """The network definition is invalid."""


class DemandError(FlowError):
    """The demand definition is invalid."""


class DisconnectedError(FlowError):
    """An origin-destination pair has no path."""


class NegativeCostError(FlowError):
    """A link cost is negative or not finite."""


def _as_float_array(values, name: str, n: int) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.shape != (n,):
        raise NetworkError(f"{name} must have shape ({n},), got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise NetworkError(f"{name} must be finite")
    arr = arr.copy()
    arr.setflags(write=False)
    return arr


@dataclass(frozen=True)
class Network:
    """Directed graph with polynomial link costs.

    ``capacity`` (veh/h) is optional; it is used only by congestion metrics.
    """

    n_nodes: int
    tail: np.ndarray
    head: np.ndarray
    A: np.ndarray
    B: np.ndarray
    P: np.ndarray
    capacity: np.ndarray | None = None
    link_names: tuple[str, ...] | None = None
    name: str = "network"
    out_links: tuple[tuple[int, ...], ...] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.n_nodes, (int, np.integer)) or self.n_nodes < 2:
            raise NetworkError("n_nodes must be an integer >= 2")
        tail = np.asarray(self.tail)
        head = np.asarray(self.head)
        if tail.ndim != 1 or tail.shape != head.shape or tail.size == 0:
            raise NetworkError("tail and head must be nonempty 1-D arrays of equal length")
        if not (np.issubdtype(tail.dtype, np.integer) and np.issubdtype(head.dtype, np.integer)):
            raise NetworkError("tail and head must be integer arrays")
        m = tail.size
        if tail.min() < 0 or head.min() < 0 or tail.max() >= self.n_nodes or head.max() >= self.n_nodes:
            raise NetworkError("link endpoints must be node ids in [0, n_nodes)")
        if np.any(tail == head):
            raise NetworkError("self-loops are not allowed")
        pairs = set(zip(tail.tolist(), head.tolist()))
        if len(pairs) != m:
            raise NetworkError("parallel links (same tail and head) are not allowed")
        A = _as_float_array(self.A, "A", m)
        B = _as_float_array(self.B, "B", m)
        P = _as_float_array(self.P, "P", m)
        if np.any(A < 0) or np.any(B < 0):
            raise NetworkError("cost coefficients A and B must be nonnegative")
        if np.any(P < 1):
            raise NetworkError("cost exponent P must be >= 1")
        cap = None
        if self.capacity is not None:
            cap = _as_float_array(self.capacity, "capacity", m)
            if np.any(cap <= 0):
                raise NetworkError("capacity must be strictly positive")
        if self.link_names is not None and len(self.link_names) != m:
            raise NetworkError("link_names must have one name per link")
        t = tail.astype(np.int64).copy()
        h = head.astype(np.int64).copy()
        t.setflags(write=False)
        h.setflags(write=False)
        object.__setattr__(self, "tail", t)
        object.__setattr__(self, "head", h)
        object.__setattr__(self, "A", A)
        object.__setattr__(self, "B", B)
        object.__setattr__(self, "P", P)
        object.__setattr__(self, "capacity", cap)
        out: list[list[int]] = [[] for _ in range(self.n_nodes)]
        for e in range(m):
            out[int(t[e])].append(e)
        # deterministic order: by head node id
        object.__setattr__(
            self, "out_links", tuple(tuple(sorted(lst, key=lambda e: int(h[e]))) for lst in out)
        )

    @property
    def n_links(self) -> int:
        return int(self.tail.size)

    def link_index(self, u: int, v: int) -> int:
        idx = np.nonzero((self.tail == u) & (self.head == v))[0]
        if idx.size == 0:
            raise NetworkError(f"no link {u}->{v}")
        return int(idx[0])

    # cost model -----------------------------------------------------------
    def _check_flow(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        if x.shape != (self.n_links,):
            raise FlowError(f"flow vector must have shape ({self.n_links},)")
        if not np.all(np.isfinite(x)):
            raise FlowError("flow vector must be finite")
        if np.any(x < -1e-9):
            raise FlowError("link flows must be nonnegative")
        return np.maximum(x, 0.0)

    def link_time(self, x) -> np.ndarray:
        """Travel time per traveller on every link at flow ``x``."""
        x = self._check_flow(x)
        return self.A + self.B * x ** self.P

    def marginal_cost(self, x) -> np.ndarray:
        """d/dx [x t(x)] = A + B (1 + P) x^P (system-optimal link cost)."""
        x = self._check_flow(x)
        return self.A + self.B * (1.0 + self.P) * x ** self.P

    def beckmann(self, x) -> float:
        """Beckmann objective sum_e integral_0^{x_e} t_e(s) ds."""
        x = self._check_flow(x)
        return float(np.sum(self.A * x + self.B * x ** (self.P + 1.0) / (self.P + 1.0)))

    def total_travel_time(self, x) -> float:
        """TSTT = sum_e x_e t_e(x_e)."""
        x = self._check_flow(x)
        return float(np.dot(x, self.link_time(x)))

    def free_flow_time(self) -> np.ndarray:
        return self.A.copy()

    def without_link(self, e: int) -> "Network":
        """Copy of the network with link ``e`` removed (link ids above ``e`` shift down)."""
        if not 0 <= e < self.n_links:
            raise NetworkError(f"link index {e} out of range")
        keep = np.array([i for i in range(self.n_links) if i != e], dtype=np.int64)
        return Network(
            n_nodes=self.n_nodes,
            tail=self.tail[keep],
            head=self.head[keep],
            A=self.A[keep],
            B=self.B[keep],
            P=self.P[keep],
            capacity=None if self.capacity is None else self.capacity[keep],
            link_names=None if self.link_names is None else tuple(self.link_names[i] for i in keep),
            name=f"{self.name}-without-{e}",
        )


@dataclass(frozen=True)
class ODPair:
    origin: int
    destination: int
    demand: float


@dataclass(frozen=True)
class Demand:
    """Validated set of OD pairs. Demand values are nonnegative and finite."""

    pairs: tuple[ODPair, ...]

    def __post_init__(self) -> None:
        if len(self.pairs) == 0:
            raise DemandError("demand needs at least one OD pair")
        seen = set()
        for p in self.pairs:
            if not isinstance(p, ODPair):
                raise DemandError("pairs must be ODPair instances")
            if p.origin == p.destination:
                raise DemandError("origin and destination must differ")
            if not np.isfinite(p.demand) or p.demand < 0:
                raise DemandError("demand must be finite and nonnegative")
            key = (p.origin, p.destination)
            if key in seen:
                raise DemandError(f"duplicate OD pair {key}")
            seen.add(key)

    def check_against(self, net: Network) -> None:
        for p in self.pairs:
            for node in (p.origin, p.destination):
                if not 0 <= node < net.n_nodes:
                    raise DemandError(f"OD node {node} not in network")

    @property
    def total(self) -> float:
        return float(sum(p.demand for p in self.pairs))

    def scaled(self, factor: float) -> "Demand":
        if not np.isfinite(factor) or factor < 0:
            raise DemandError("scale factor must be finite and nonnegative")
        return Demand(tuple(ODPair(p.origin, p.destination, p.demand * factor) for p in self.pairs))

    @staticmethod
    def from_tuples(items) -> "Demand":
        return Demand(tuple(ODPair(int(o), int(d), float(q)) for o, d, q in items))
