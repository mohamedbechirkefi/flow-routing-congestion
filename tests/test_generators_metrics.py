# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Grid generator, demand calibration and metric formulas (hand-computed examples)."""
import numpy as np
import pytest

from flow.assignment import AssignmentResult, free_flow
from flow.generators import make_grid, reference_demand_absolute, reference_demand_ff
from flow.metrics import evaluate, node_balance, weighted_gini, weighted_quantile
from flow.network import Demand, DemandError, FlowError, NetworkError
from flow.paths import all_or_nothing, enumerate_simple_paths
from conftest import make_net


def test_grid_is_deterministic_and_seed_dependent():
    a, b, c = make_grid(4, 9000), make_grid(4, 9000), make_grid(4, 9001)
    assert np.array_equal(a.network.A, b.network.A) and a.od == b.od and a.weights == b.weights
    assert not np.array_equal(a.network.A, c.network.A)


@pytest.mark.parametrize("n", [3, 4, 6])
def test_grid_structure(n):
    inst = make_grid(n, 9000)
    net = inst.network
    assert net.n_nodes == n * n and net.n_links == 4 * n * (n - 1)
    assert np.all((net.A >= 1) & (net.A <= 3))
    assert np.all((net.capacity >= 600) & (net.capacity <= 1800))
    # both directions of a link share t0 and capacity
    for e in range(0, net.n_links, 2):
        assert net.tail[e] == net.head[e + 1] and net.A[e] == net.A[e + 1]
    assert len(inst.od) == 12 and len(set(inst.od)) == 12
    for o, d in inst.od:
        assert abs(o // n - d // n) + abs(o % n - d % n) >= n - 1
    assert sum(inst.weights) == pytest.approx(1.0)


def test_capacity_scale_keeps_instance_matched():
    a, b = make_grid(4, 9005), make_grid(4, 9005, capacity_scale=0.8)
    assert np.array_equal(a.network.A, b.network.A) and a.od == b.od
    assert np.allclose(b.network.capacity, 0.8 * a.network.capacity)


def test_ff_calibration_saturates_one_link():
    inst = make_grid(4, 9003)
    dref = reference_demand_ff(inst)
    x, _, _ = all_or_nothing(inst.network, inst.network.A, inst.demand(dref))
    assert np.max(x / inst.network.capacity) == pytest.approx(1.0)


def test_absolute_calibration():
    inst = make_grid(3, 9000)
    with pytest.raises(DemandError):
        reference_demand_absolute(inst, 0.0)
    assert reference_demand_absolute(inst, 0.5) > 0


def test_generator_invalid_inputs():
    with pytest.raises(NetworkError):
        make_grid(1, 9000)
    with pytest.raises(NetworkError):
        make_grid(3, 9000, beta=0.5)
    with pytest.raises(DemandError):
        make_grid(2, 9000, k_pairs=13)  # 2x2 has only 12 ordered OD candidates


def test_weighted_quantile_hand_computed():
    assert weighted_quantile([1, 2, 3, 4], [1, 1, 1, 1], 0.5) == 2
    assert weighted_quantile([1, 2, 3, 4], [1, 1, 1, 1], 0.95) == 4
    assert weighted_quantile([10, 1], [9, 1], 0.05) == 1
    assert weighted_quantile([10, 1], [9, 1], 0.95) == 10
    with pytest.raises(FlowError):
        weighted_quantile([], [], 0.5)
    with pytest.raises(FlowError):
        weighted_quantile([1], [0], 0.5)


def test_weighted_gini_hand_computed():
    assert weighted_gini([1, 1, 1], [1, 2, 3]) == 0.0
    # two equal-weight values 0 and 1: G = 2 * 1 * 1 / (2 * 4 * 0.5) = 0.5
    assert weighted_gini([0, 1], [1, 1]) == pytest.approx(0.5)
    # integer weights equal repetition
    assert weighted_gini([1, 3], [2, 1]) == pytest.approx(weighted_gini([1, 1, 3], [1, 1, 1]))
    with pytest.raises(FlowError):
        weighted_gini([-1, 1], [1, 1])


def test_evaluate_hand_computed_braess_ff():
    from flow.generators import braess_demand, braess_network

    net, dem = braess_network(True), braess_demand(6.0)
    m = evaluate(net, dem, free_flow(net, dem))
    assert m["tstt"] == 816.0 and m["mean_trip_time"] == 136.0 and m["p95_trip_time"] == 136.0
    assert m["gini_stretch"] == 0.0 and m["flow_weighted_vc"] is None


def test_node_balance_detects_violation():
    net = make_net([(0, 1), (1, 2)], A=[1, 1], B=[0, 0])
    dem = Demand.from_tuples([(0, 2, 5.0)])
    assert np.allclose(node_balance(net, dem, np.array([5.0, 5.0])), 0)
    assert not np.allclose(node_balance(net, dem, np.array([5.0, 4.0])), 0)
