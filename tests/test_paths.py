# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Shortest paths against reference enumeration; disconnected graphs; nonnegative costs."""
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from flow.generators import braess_network, make_grid
from flow.network import Demand, DisconnectedError, NegativeCostError, Network
from flow.paths import (
    all_or_nothing,
    brute_force_shortest,
    enumerate_simple_paths,
    path_cost,
    shortest_path,
    shortest_path_tree,
)
from conftest import make_net


@st.composite
def small_graphs(draw):
    n = draw(st.integers(3, 6))
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    mask = draw(st.lists(st.booleans(), min_size=len(pairs), max_size=len(pairs)))
    edges = [p for p, keep in zip(pairs, mask) if keep]
    if not edges:
        edges = [(0, 1)]
    # integer costs make exact ties frequent, which exercises the tie-breaking rule
    costs = draw(st.lists(st.integers(0, 4), min_size=len(edges), max_size=len(edges)))
    net = make_net(edges, A=costs, B=[0] * len(edges), n=n)
    return net, np.array(costs, dtype=float)


@settings(max_examples=300, deadline=None)
@given(small_graphs())
def test_dijkstra_matches_bruteforce_enumeration(g):
    net, c = g
    for o in range(net.n_nodes):
        dist, paths = shortest_path_tree(net, c, o)
        for d in range(net.n_nodes):
            if d == o:
                continue
            ref = enumerate_simple_paths(net, o, d)
            if not ref:
                assert paths[d] is None and dist[d] == float("inf")
                with pytest.raises(DisconnectedError):
                    shortest_path(net, c, o, d)
                continue
            bcost, bpath = brute_force_shortest(net, c, o, d)
            assert dist[d] == pytest.approx(bcost)
            assert paths[d] == bpath  # identical tie-breaking: lexicographically smallest sequence
            assert path_cost(net, c, paths[d]) == pytest.approx(dist[d])


def test_hand_computed_shortest_path():
    #   0 -> 1 (1), 1 -> 3 (1), 0 -> 2 (1), 2 -> 3 (1), 0 -> 3 (3)
    net = make_net([(0, 1), (1, 3), (0, 2), (2, 3), (0, 3)], A=[1, 1, 1, 1, 3], B=[0] * 5)
    cost, path = shortest_path(net, net.A, 0, 3)
    assert cost == 2.0 and path == (0, 1, 3)  # tie with (0, 2, 3) broken lexicographically


def test_braess_free_flow_paths():
    net = braess_network(True)
    assert shortest_path(net, net.A, 0, 3) == (10.0, (0, 1, 2, 3))
    net0 = braess_network(False)
    assert shortest_path(net0, net0.A, 0, 3) == (50.0, (0, 1, 3))


def test_grid_dijkstra_matches_enumeration_3x3():
    inst = make_grid(3, 9001)
    net = inst.network
    for o, d in inst.od:
        assert shortest_path(net, net.A, o, d) == brute_force_shortest(net, net.A, o, d)


def test_disconnected_graph_errors():
    net = make_net([(0, 1), (2, 3)], A=[1, 1], B=[0, 0])
    with pytest.raises(DisconnectedError):
        shortest_path(net, net.A, 0, 3)
    with pytest.raises(DisconnectedError):
        all_or_nothing(net, net.A, Demand.from_tuples([(0, 3, 1.0)]))
    # zero demand on a disconnected pair is still an explicit error (no silent exclusion)
    with pytest.raises(DisconnectedError):
        all_or_nothing(net, net.A, Demand.from_tuples([(0, 3, 0.0)]))
    # one-way link: reverse direction unreachable
    with pytest.raises(DisconnectedError):
        shortest_path(net, net.A, 1, 0)


def test_negative_or_nonfinite_costs_rejected():
    net = make_net([(0, 1), (1, 2)], A=[1, 1], B=[0, 0])
    with pytest.raises(NegativeCostError):
        shortest_path_tree(net, np.array([1.0, -0.5]), 0)
    with pytest.raises(NegativeCostError):
        shortest_path_tree(net, np.array([1.0, np.nan]), 0)
    with pytest.raises(NegativeCostError):
        shortest_path_tree(net, np.array([1.0]), 0)


def test_all_or_nothing_loads_demand_on_chosen_paths():
    net = braess_network(True)
    x, chosen, kappa = all_or_nothing(net, net.A, Demand.from_tuples([(0, 3, 6.0)]))
    assert chosen == [(0, 1, 2, 3)] and kappa == [10.0]
    assert np.allclose(x, [6, 0, 0, 6, 6])
