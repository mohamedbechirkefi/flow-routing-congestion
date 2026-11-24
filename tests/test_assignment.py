# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Assignment arms: golden values, invariants, convergence tolerances, differential checks."""
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from flow.assignment import (
    frank_wolfe,
    free_flow,
    gradient_projection,
    mixed_compliance,
    msa,
    system_optimum,
    user_equilibrium,
)
from flow.generators import braess_demand, braess_network, make_grid, reference_demand_ff
from flow.metrics import evaluate, node_balance
from flow.network import Demand, FlowError
from flow.paths import LinkLookup


# --- golden: Pigou example (hand computed) --------------------------------
def test_pigou_golden(pigou):
    dem = Demand.from_tuples([(0, 1, 1.0)])
    ue = user_equilibrium(pigou, dem)
    so = system_optimum(pigou, dem)
    assert pigou.total_travel_time(ue.link_flow) == pytest.approx(1.0, abs=1e-5)
    assert pigou.total_travel_time(so.link_flow) == pytest.approx(0.75, abs=1e-6)
    assert so.link_flow[2] == pytest.approx(0.5, abs=1e-4)
    # price of anarchy 4/3 for linear latencies is attained here
    ratio = pigou.total_travel_time(ue.link_flow) / pigou.total_travel_time(so.link_flow)
    assert ratio == pytest.approx(4 / 3, abs=1e-4)


# --- golden: Braess example (EXP-001 values) -------------------------------
@pytest.mark.parametrize(
    "with_link, arm, tstt, path_time",
    [
        (False, "FF", 696.0, 116.0),
        (False, "UE", 498.0, 83.0),
        (False, "SO", 498.0, 83.0),
        (True, "FF", 816.0, 136.0),
        (True, "UE", 552.0, 92.0),
    ],
)
def test_braess_golden_frank_wolfe(with_link, arm, tstt, path_time):
    net = braess_network(with_link)
    dem = braess_demand(6.0)
    res = {"FF": free_flow, "UE": user_equilibrium, "SO": system_optimum}[arm](net, dem)
    m = evaluate(net, dem, res)
    # FW stops at RG <= 1e-6, so TSTT is exact up to about RG * TSTT
    assert res.converged
    assert m["tstt"] == pytest.approx(tstt, rel=2e-6)
    assert m["mean_trip_time"] == pytest.approx(path_time, rel=2e-6)


def test_braess_so_with_link_frank_wolfe_slow_known_limitation():
    """SO with link e at d=6 is a corner solution (e unused). FW zigzags and does not
    reach RG <= 1e-6 in 20,000 iterations (M2 finding); its TSTT is within 0.01 of 498.
    The path-based candidate solver reaches it exactly."""
    net, dem = braess_network(True), braess_demand(6.0)
    fw = system_optimum(net, dem, max_iter=2000)
    assert not fw.converged
    assert net.total_travel_time(fw.link_flow) == pytest.approx(498.0, abs=0.1)
    gp = gradient_projection(net, dem, "so")
    assert gp.converged and net.total_travel_time(gp.link_flow) == pytest.approx(498.0, abs=1e-9)


def test_braess_ue_path_times_equal_92():
    net, dem = braess_network(True), braess_demand(6.0)
    res = user_equilibrium(net, dem, tol=1e-10, max_iter=100_000)
    t = net.link_time(res.link_flow)
    lk = LinkLookup(net)
    for path, f in res.path_flows[0].items():
        assert f == pytest.approx(2.0, abs=1e-3)
        assert sum(t[e] for e in lk.links(path)) == pytest.approx(92.0, abs=1e-3)


# --- invariants on seeded grids --------------------------------------------
CAP = 5_000  # test-suite cap; the protocol cap is 20,000
GRID_CASES = [(3, 9000, 1.0), (3, 9001, 2.0), (4, 9002, 2.0), (4, 9003, 3.0)]


@pytest.fixture(scope="module")
def grid_solutions():
    out = {}
    for n, seed, rho in GRID_CASES:
        inst = make_grid(n, seed)
        dem = inst.demand(rho * reference_demand_ff(inst))
        net = inst.network
        out[(n, seed, rho)] = (
            net, dem,
            free_flow(net, dem),
            user_equilibrium(net, dem, tol=1e-6, max_iter=CAP),
            system_optimum(net, dem, tol=1e-6, max_iter=CAP),
        )
    return out


@pytest.mark.parametrize("case", GRID_CASES)
def test_flow_conservation_and_nonnegativity(grid_solutions, case):
    net, dem, ff, ue, so = grid_solutions[case]
    for res in (ff, ue, so):
        assert np.all(res.link_flow >= 0)
        assert np.max(np.abs(node_balance(net, dem, res.link_flow))) < 1e-8 * dem.total
        assert np.all(net.link_time(res.link_flow) >= 0)
        for p, pf in zip(dem.pairs, res.path_flows):
            assert sum(pf.values()) == pytest.approx(p.demand, rel=1e-9)
            assert all(v >= 0 for v in pf.values())
            for path in pf:
                assert path[0] == p.origin and path[-1] == p.destination


@pytest.mark.parametrize("case", GRID_CASES)
def test_path_flows_reproduce_link_flows(grid_solutions, case):
    net, dem, ff, ue, so = grid_solutions[case]
    lk = LinkLookup(net)
    for res in (ff, ue, so):
        x = np.zeros(net.n_links)
        for pf in res.path_flows:
            for path, f in pf.items():
                for e in lk.links(path):
                    x[e] += f
        assert np.allclose(x, res.link_flow, rtol=1e-8, atol=1e-8 * dem.total)


@pytest.mark.parametrize("case", GRID_CASES)
def test_system_optimum_is_lowest(grid_solutions, case):
    net, dem, ff, ue, so = grid_solutions[case]
    t_so = net.total_travel_time(so.link_flow)
    # SO is computed to a tolerance; allow its residual optimality gap
    slack = 1 + 2 * max(so.rel_gap, 1e-6)
    assert t_so <= net.total_travel_time(ue.link_flow) * slack
    assert t_so <= net.total_travel_time(ff.link_flow) * slack


@pytest.mark.parametrize("case", GRID_CASES)
def test_convergence_tolerance_respected(grid_solutions, case):
    _, _, _, ue, so = grid_solutions[case]
    for res in (ue, so):
        if res.converged:
            assert res.rel_gap <= 1e-6
        else:
            assert res.iterations == CAP and res.rel_gap > 1e-6


@pytest.mark.parametrize("case", GRID_CASES)
def test_wardrop_condition_at_ue(grid_solutions, case):
    net, dem, _, ue, _ = grid_solutions[case]
    t = net.link_time(ue.link_flow)
    lk = LinkLookup(net)
    from flow.paths import shortest_path

    for p, pf in zip(dem.pairs, ue.path_flows):
        best, _ = shortest_path(net, t, p.origin, p.destination)
        # flow-weighted excess cost of used paths is bounded by the gap
        excess = sum(f * (sum(t[e] for e in lk.links(path)) - best) for path, f in pf.items())
        assert excess >= -1e-9
        assert excess <= max(ue.rel_gap, 1e-6) * net.total_travel_time(ue.link_flow) + 1e-9


def test_tighter_tolerance_gives_smaller_gap():
    inst = make_grid(3, 9001)
    dem = inst.demand(2 * reference_demand_ff(inst))
    loose = user_equilibrium(inst.network, dem, tol=1e-3)
    tight = user_equilibrium(inst.network, dem, tol=1e-7, max_iter=50_000)
    assert loose.rel_gap <= 1e-3 and tight.rel_gap <= max(1e-7, loose.rel_gap)
    assert tight.iterations >= loose.iterations


def test_iteration_cap_flags_nonconvergence():
    inst = make_grid(4, 9003)
    dem = inst.demand(3 * reference_demand_ff(inst))
    res = user_equilibrium(inst.network, dem, tol=1e-12, max_iter=5)
    assert not res.converged and res.iterations == 5 and res.rel_gap > 1e-12


def test_beckmann_objective_does_not_increase():
    inst = make_grid(4, 9002)
    dem = inst.demand(2 * reference_demand_ff(inst))
    vals = [inst.network.beckmann(user_equilibrium(inst.network, dem, tol=1e-12, max_iter=k).link_flow) for k in (0, 1, 2, 5, 20, 100)]
    assert all(b <= a + 1e-9 * abs(a) for a, b in zip(vals, vals[1:]))


# --- MIX(c) ----------------------------------------------------------------
@pytest.mark.parametrize("seed", [9000, 9004])
def test_mix_endpoints(seed):
    inst = make_grid(3, seed)
    net = inst.network
    dem = inst.demand(2 * reference_demand_ff(inst))
    ue = user_equilibrium(net, dem)
    so = system_optimum(net, dem)
    m0 = mixed_compliance(net, dem, 0.0)
    m1 = mixed_compliance(net, dem, 1.0, so_result=so)
    assert np.allclose(m0.link_flow, ue.link_flow, rtol=1e-12, atol=1e-9)
    assert np.allclose(m1.link_flow, so.link_flow, rtol=1e-12, atol=1e-9)
    mh = mixed_compliance(net, dem, 0.5, so_result=so)
    assert np.max(np.abs(node_balance(net, dem, mh.link_flow))) < 1e-8 * dem.total


def test_mix_invalid_compliance():
    net, dem = braess_network(True), braess_demand(6.0)
    for c in (-0.1, 1.5, float("nan")):
        with pytest.raises(FlowError):
            mixed_compliance(net, dem, c)


# --- differential references -------------------------------------------------
@pytest.mark.parametrize("seed", [9000, 9001, 9002])
def test_frank_wolfe_matches_msa_and_gradient_projection(seed):
    inst = make_grid(3, seed)
    net = inst.network
    dem = inst.demand(2 * reference_demand_ff(inst))
    fw = user_equilibrium(net, dem, tol=1e-8, max_iter=20_000)
    ms = msa(net, dem, iterations=3000)
    gp = gradient_projection(net, dem, "ue", tol=1e-10)
    t_fw = net.total_travel_time(fw.link_flow)
    assert net.total_travel_time(ms.link_flow) == pytest.approx(t_fw, rel=1e-3)
    assert net.total_travel_time(gp.link_flow) == pytest.approx(t_fw, rel=1e-5)
    # convexity bound: Beckmann(x) - Beckmann* <= RG * sum_e x_e t_e(x)
    b_gp, b_fw = net.beckmann(gp.link_flow), net.beckmann(fw.link_flow)
    assert b_gp <= b_fw * (1 + 1e-12)
    assert b_fw - b_gp <= max(fw.rel_gap, 1e-8) * t_fw + 1e-9
    so_fw = system_optimum(net, dem, tol=1e-8, max_iter=20_000)
    so_gp = gradient_projection(net, dem, "so", tol=1e-10)
    t_gp, t_sofw = net.total_travel_time(so_gp.link_flow), net.total_travel_time(so_fw.link_flow)
    # convexity bound: TSTT(x) - TSTT* <= RG * sum_e x_e m_e(x) <= RG * (1 + beta) * TSTT(x)
    assert t_gp <= t_sofw * (1 + 1e-9)
    assert (t_sofw - t_gp) / t_sofw <= (1 + 4.0) * max(so_fw.rel_gap, 1e-8) + 1e-9


# --- edge cases ---------------------------------------------------------------
def test_zero_demand_is_trivially_converged():
    net = braess_network(True)
    dem = braess_demand(0.0)
    for f in (user_equilibrium, system_optimum):
        r = f(net, dem)
        assert r.converged and np.all(r.link_flow == 0)


def test_invalid_solver_arguments():
    net, dem = braess_network(True), braess_demand(6.0)
    with pytest.raises(FlowError):
        frank_wolfe(net, dem, "xx")
    with pytest.raises(FlowError):
        frank_wolfe(net, dem, tol=0)
    with pytest.raises(FlowError):
        frank_wolfe(net, dem, background=-np.ones(net.n_links))
    with pytest.raises(FlowError):
        frank_wolfe(net, dem, "so", background=np.ones(net.n_links))


def test_extreme_demand_stays_finite():
    inst = make_grid(3, 9002)
    dem = inst.demand(1e3 * reference_demand_ff(inst))
    ff = free_flow(inst.network, dem)
    m = evaluate(inst.network, dem, ff)
    assert np.isfinite(m["tstt"])
    ue = user_equilibrium(inst.network, dem, max_iter=200)
    assert np.all(np.isfinite(ue.link_flow))


@settings(max_examples=40, deadline=None)
@given(st.floats(0.1, 12.0))
def test_braess_ue_is_deterministic(d):
    net, dem = braess_network(True), braess_demand(d)
    a = user_equilibrium(net, dem, max_iter=500)
    b = user_equilibrium(net, dem, max_iter=500)
    assert np.array_equal(a.link_flow, b.link_flow)
