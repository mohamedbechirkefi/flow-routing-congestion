# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Network and cost model: formulas, validation and explicit error paths."""
import numpy as np
import pytest

from flow.generators import make_grid
from flow.network import Demand, DemandError, FlowError, Network, NetworkError, ODPair
from conftest import make_net


def test_linear_cost_formulas():
    net = make_net([(0, 1), (1, 2)], A=[2, 0], B=[3, 10])
    x = np.array([2.0, 1.5])
    assert np.allclose(net.link_time(x), [8.0, 15.0])
    assert np.allclose(net.marginal_cost(x), [2 + 2 * 3 * 2, 2 * 10 * 1.5])
    assert net.total_travel_time(x) == pytest.approx(2 * 8 + 1.5 * 15)
    assert net.beckmann(x) == pytest.approx(2 * 2 + 3 * 4 / 2 + 10 * 1.5**2 / 2)


def test_bpr_parameterisation_matches_bpr_formula():
    inst = make_grid(3, 9000)
    net = inst.network
    x = np.linspace(0, 2000, net.n_links)
    t0, c = net.A, net.capacity
    bpr = t0 * (1 + 0.15 * (x / c) ** 4)
    assert np.allclose(net.link_time(x), bpr, rtol=1e-12)
    # marginal cost = d/dx [x t(x)] checked by central differences
    h = 1e-3
    num = ((x + h) * net.link_time(x + h) - (x - h) * net.link_time(np.maximum(x - h, 0))) / (2 * h)
    assert np.allclose(net.marginal_cost(x)[1:], num[1:], rtol=1e-6)


@pytest.mark.parametrize(
    "kwargs, msg",
    [
        (dict(A=[-1, 0], B=[1, 1]), "nonnegative"),
        (dict(A=[1, 0], B=[-1, 1]), "nonnegative"),
        (dict(A=[1, np.nan], B=[1, 1]), "finite"),
        (dict(A=[1, 0], B=[1, 1], P=[0.5, 1]), ">= 1"),
        (dict(A=[1, 0], B=[1, 1], capacity=np.array([0.0, 1.0])), "positive"),
    ],
)
def test_invalid_cost_parameters_rejected(kwargs, msg):
    with pytest.raises(NetworkError, match=msg):
        make_net([(0, 1), (1, 2)], **kwargs)


def test_structural_errors():
    with pytest.raises(NetworkError, match="self-loops"):
        make_net([(0, 0), (0, 1)], A=[1, 1], B=[0, 0])
    with pytest.raises(NetworkError, match="parallel"):
        make_net([(0, 1), (0, 1)], A=[1, 1], B=[0, 0])
    with pytest.raises(NetworkError, match="node ids"):
        Network(n_nodes=2, tail=np.array([0]), head=np.array([5]), A=np.ones(1), B=np.ones(1), P=np.ones(1))
    with pytest.raises(NetworkError, match="integer"):
        Network(n_nodes=2, tail=np.array([0.0]), head=np.array([1.0]), A=np.ones(1), B=np.ones(1), P=np.ones(1))


def test_flow_vector_validation():
    net = make_net([(0, 1)], A=[1], B=[1])
    with pytest.raises(FlowError):
        net.link_time(np.array([-1.0]))
    with pytest.raises(FlowError):
        net.link_time(np.array([np.inf]))
    with pytest.raises(FlowError):
        net.link_time(np.array([1.0, 2.0]))


def test_demand_validation():
    with pytest.raises(DemandError):
        Demand(())
    with pytest.raises(DemandError):
        Demand((ODPair(0, 0, 1.0),))
    with pytest.raises(DemandError):
        Demand((ODPair(0, 1, -1.0),))
    with pytest.raises(DemandError):
        Demand((ODPair(0, 1, float("nan")),))
    with pytest.raises(DemandError):
        Demand((ODPair(0, 1, 1.0), ODPair(0, 1, 2.0)))
    net = make_net([(0, 1)], A=[1], B=[1])
    with pytest.raises(DemandError):
        Demand((ODPair(0, 7, 1.0),)).check_against(net)


def test_without_link_and_immutability():
    net = make_net([(0, 1), (1, 2), (0, 2)], A=[1, 1, 3], B=[0, 0, 0])
    sub = net.without_link(2)
    assert sub.n_links == 2 and net.n_links == 3
    with pytest.raises(ValueError):
        net.A[0] = 5.0
