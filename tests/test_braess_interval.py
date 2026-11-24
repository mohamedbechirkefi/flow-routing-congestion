# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""EXP-002 pre-run verification: the hand-derived paradox interval (80/31, 80/9)
checked by exact rational arithmetic and then against the numerical engine."""
from fractions import Fraction as F

import pytest

from flow.assignment import gradient_projection, user_equilibrium
from flow.generators import braess_demand, braess_network


def exact_ue_time_with_link(d: F) -> F:
    """Solve the symmetric UE exactly, checking Wardrop conditions in each regime."""
    # regime 1: all on a-e-d
    t3 = 21 * d + 10
    t1 = 10 * d + 50  # unused outer path cost when f = 0, g = d
    if t3 <= t1:
        return t3
    # regime 3: link e unused
    f = d / 2
    t_outer = 10 * f + f + 50
    t_mid = 10 * f + 10 + 10 * f
    if t_outer <= t_mid:
        return t_outer
    # regime 2: interior
    f = (11 * d - 40) / 13
    g = (80 - 9 * d) / 13
    assert f >= 0 and g >= 0 and 2 * f + g == d
    p1 = 10 * (f + g) + f + 50
    p3 = 10 * (f + g) + g + 10 + 10 * (f + g)
    assert p1 == p3
    assert p1 == (31 * d + 1010) / 13
    return p1


def exact_ue_time_without_link(d: F) -> F:
    return F(11, 2) * d + 50


def test_regime_boundaries_exact():
    assert exact_ue_time_with_link(F(40, 11)) == 21 * F(40, 11) + 10
    assert exact_ue_time_with_link(F(80, 9)) == F(11, 2) * F(80, 9) + 50


def test_paradox_interval_exact():
    lo, hi = F(80, 31), F(80, 9)
    assert exact_ue_time_with_link(lo) == exact_ue_time_without_link(lo)
    assert exact_ue_time_with_link(hi) == exact_ue_time_without_link(hi)
    grid = [F(k, 100) for k in range(1, 1501)]
    for d in grid:
        diff = exact_ue_time_with_link(d) - exact_ue_time_without_link(d)
        if lo < d < hi:
            assert diff > 0, d
        else:
            assert diff <= 0, d
    assert exact_ue_time_with_link(F(6)) == 92 and exact_ue_time_without_link(F(6)) == 83


@pytest.mark.parametrize("d", [0.5, 2.0, 2.6, 3.0, 3.6363, 5.0, 6.0, 8.0, 8.8, 9.0, 11.0])
def test_engine_matches_exact_ue(d):
    for with_link, exact in ((True, exact_ue_time_with_link), (False, exact_ue_time_without_link)):
        net, dem = braess_network(with_link), braess_demand(d)
        res = gradient_projection(net, dem, "ue", tol=1e-12, max_iter=5000)
        expected = float(exact(F(d).limit_denominator(10**6)))
        assert net.total_travel_time(res.link_flow) / d == pytest.approx(expected, rel=1e-6)
        fw = user_equilibrium(net, dem, tol=1e-8, max_iter=20_000)
        if fw.converged:
            assert net.total_travel_time(fw.link_flow) / d == pytest.approx(expected, rel=1e-5)
        else:
            # M2 finding: at or near the corner equilibrium (link e unused, d >= 80/9) FW stalls; it must
            # then be flagged, and its error stays small but above the 1e-6 check of EXP-002
            assert fw.rel_gap > 1e-8 and with_link and d >= 8.0
            assert net.total_travel_time(fw.link_flow) / d == pytest.approx(expected, rel=1e-3)
