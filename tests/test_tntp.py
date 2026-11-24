# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""TNTP ingestion (pure functions) and the tntp runner path, on a committed synthetic fixture.

The real Sioux Falls files are git-ignored and never used by the test suite.
"""
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from flow.assignment import gradient_projection
from flow.generators import reference_demand_ff_network
from flow.runner import ConfigError, load_tntp, run_config
from flow.schema import load_result
from flow.tntp import TNTPError, build_demand, ingest, parse_net, parse_trips

FIX = Path(__file__).parent / "fixtures" / "tntp_synthetic"
NET = (FIX / "synth_net.tntp").read_text()
TRIPS = (FIX / "synth_trips.tntp").read_text()
FLOW = (FIX / "synth_flow.tntp").read_text()


def test_ingest_counts_and_mapping():
    inst = ingest(NET, TRIPS, FLOW, name="synth")
    rep = inst.report
    assert rep["links_read"] == rep["links_kept"] == 5
    assert rep["missing_fields"] == {}
    assert rep["od_cells_read"] == 9 and rep["od_excluded_diagonal"] == 3 and rep["od_excluded_zero"] == 4
    assert rep["od_pairs_kept"] == 2 and rep["total_od_flow_read"] == rep["total_od_flow_header"] == 300.0
    net = inst.network
    assert net.n_nodes == 4 and net.n_links == 5
    e = net.link_index(0, 1)  # TNTP 1->2, 0-based
    # t = fft (1 + b (x/c)^power) at x = c gives fft * 1.15
    x = np.zeros(5)
    x[e] = 100.0
    assert net.link_time(x)[e] == pytest.approx(2.0 * 1.15)
    assert inst.trips == ((1, 2, 100.0), (1, 3, 200.0))
    assert inst.reference_flow[net.link_index(1, 2)] == 50.0


def test_ingest_is_pure_and_deterministic():
    a = ingest(NET, TRIPS, FLOW)
    b = ingest(NET, TRIPS, FLOW)
    assert a.report == b.report and np.array_equal(a.reference_flow, b.reference_flow)


@pytest.mark.parametrize(
    "mutate, match",
    [
        (lambda t: t.replace("<NUMBER OF LINKS> 5", "<NUMBER OF LINKS> 6"), "header says"),
        (lambda t: t.replace("<FIRST THRU NODE> 1", "<FIRST THRU NODE> 2"), "FIRST THRU NODE"),
        (lambda t: t.replace("<END OF METADATA>", ""), "END OF METADATA"),
        (lambda t: t.replace("\t1\t2\t100\t", "\t1\t2\tabc\t"), "non-numeric"),
        (lambda t: t.replace("\t1\t2\t100\t", "\t1\t2\t-100\t"), "capacity"),
        (lambda t: t.replace("\t1\t2\t100\t2\t2\t0.15\t4", "\t1\t2\t100\t2\t2\t0.15\t0.5"), "power"),
        (lambda t: t.replace("\t3\t4\t100\t", "\t3\t9\t100\t"), "node ids"),
    ],
)
def test_net_schema_errors(mutate, match):
    with pytest.raises(TNTPError, match=match):
        parse_net(mutate(NET))


def test_net_missing_optional_fields_are_counted():
    short = NET.replace("\t1\t2\t100\t2\t2\t0.15\t4\t0\t0\t1\t;", "\t1\t2\t100\t2\t2\t0.15\t4\t;")
    from flow.tntp import IngestReport

    rep = IngestReport()
    parse_net(short, rep)
    assert rep.missing_fields == {"speed": 1, "toll": 1, "link_type": 1}


@pytest.mark.parametrize(
    "mutate, match",
    [
        (lambda t: t.replace("<TOTAL OD FLOW> 300.0", "<TOTAL OD FLOW> 301.0"), "differs from header"),
        (lambda t: t.replace("3 :    200.0;", "3 :   -200.0;"), "nonnegative"),
        (lambda t: t.replace("1 :      0.0;     2 :    100.0;", "1 :      5.0;     2 :    100.0;"), "intrazonal|differs"),
        (lambda t: t.replace("Origin \t1 ", "Origin \t7 "), "outside"),
    ],
)
def test_trips_schema_errors(mutate, match):
    with pytest.raises(TNTPError, match=match):
        parse_trips(mutate(TRIPS))


def test_reference_flow_must_cover_every_link():
    with pytest.raises(TNTPError, match="cover every link"):
        ingest(NET, TRIPS, "From To Volume Cost\n1 2 1.0 1.0\n")


def test_reference_demand_ff_network_matches_definition():
    inst = ingest(NET, TRIPS)
    dem = build_demand(list(inst.trips))
    dref = reference_demand_ff_network(inst.network, dem)
    from flow.assignment import free_flow

    x = free_flow(inst.network, dem.scaled(dref / dem.total)).link_flow
    assert float(np.max(x / inst.network.capacity)) == pytest.approx(1.0)


def test_gradient_projection_on_fixture_converges():
    inst = ingest(NET, TRIPS)
    r = gradient_projection(inst.network, build_demand(list(inst.trips)), "ue", tol=1e-8, max_iter=5000)
    assert r.converged and r.rel_gap <= 1e-8


def _fake_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    d = root / "data" / "raw" / "tntp" / "SiouxFalls"
    d.mkdir(parents=True)
    (root / "research").mkdir()
    (root / "master_prompt.md").write_text("x\n")
    downloads = []
    for src, dst in (("synth_net.tntp", "SiouxFalls_net.tntp"), ("synth_trips.tntp", "SiouxFalls_trips.tntp"),
                     ("synth_flow.tntp", "SiouxFalls_flow.tntp")):
        shutil.copy(FIX / src, d / dst)
        downloads.append({"dataset": "tntp-siouxfalls", "file": dst, "sha256": hashlib.sha256((d / dst).read_bytes()).hexdigest()})
    (root / "data" / "manifest.json").write_text(json.dumps({"downloads": downloads}))
    return root


def tntp_config():
    return {
        "config_version": "flow.config/1", "experiment_id": "TEST", "label": "exploratory",
        "solver": {"algorithm": "gradient-projection", "tol": 1e-8, "max_iter": 5000},
        "cells": [{"cell": "t", "network": "tntp", "dataset": "siouxfalls", "demand_levels": ["published", 2.0],
                   "arms": ["FF", "UE", "SO"]}],
    }


def test_runner_tntp_cell(tmp_path):
    root = _fake_root(tmp_path)
    run = run_config(tntp_config(), out_root=tmp_path / "out", root=root)
    recs = load_result(run / "results.json")["records"]
    assert len(recs) == 6 and all(r["status"] == "ok" for r in recs)
    pub = [r for r in recs if r["factors"]["demand_level"] == "published"]
    assert {r["factors"]["total_demand"] for r in pub} == {300.0}
    ue = [r for r in pub if r["arm"] == "UE"][0]
    assert "ref_flow_max_abs_diff_rel" in ue["metrics"]
    rho2 = [r for r in recs if r["factors"]["demand_level"] == 2.0]
    assert all(r["factors"]["rho"] == 2.0 for r in rho2)
    assert all(r["metrics"]["R"] >= -1e-9 for r in recs)


def test_runner_refuses_tampered_data(tmp_path):
    root = _fake_root(tmp_path)
    f = root / "data" / "raw" / "tntp" / "SiouxFalls" / "SiouxFalls_trips.tntp"
    f.write_text(f.read_text().replace("100.0", "101.0"))
    with pytest.raises(ConfigError, match="SHA-256"):
        load_tntp("siouxfalls", root)


def test_runner_refuses_missing_data(tmp_path):
    root = _fake_root(tmp_path)
    (root / "data" / "raw" / "tntp" / "SiouxFalls" / "SiouxFalls_net.tntp").unlink()
    with pytest.raises(ConfigError, match="download_tntp"):
        load_tntp("siouxfalls", root)


def test_tntp_config_validation():
    for mutate in (
        lambda c: c["cells"][0].update(dataset="chicago"),
        lambda c: c["cells"][0].update(demand_levels=[]),
        lambda c: c["cells"][0].update(demand_levels=[-1.0]),
        lambda c: c.update(bpr={"alpha": 0.15, "beta": 0.5}),
        lambda c: c.update(bpr={"gamma": 1}),
    ):
        cfg = tntp_config()
        mutate(cfg)
        with pytest.raises(ConfigError):
            run_config(cfg, out_root=Path("/nonexistent"))
