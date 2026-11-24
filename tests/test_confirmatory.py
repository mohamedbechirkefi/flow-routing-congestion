# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Frozen confirmatory analyses (flow.confirmatory) on synthetic records with known answers,
and the EXP-005 link-removal runner mode on exploratory seeds."""
import copy
import json

import numpy as np
import pytest

from flow import confirmatory as C
from flow.runner import ConfigError, freeze_status, load_config, repo_root, run_config
from flow.schema import load_result

ROOT = repo_root()


def rec(cell, key, arm, factors, metrics, status="ok", seed=None, run="RUN"):
    return {"record_id": f"{run}/{cell}/{key}/{arm}", "cell": cell, "network": "n", "seed": seed, "factors": factors,
            "arm": arm, "solver": {"algorithm": "gp", "tol": 1e-6, "max_iter": 1, "iterations": 1, "rel_gap": 0.0,
                                   "converged": status == "ok", "runtime_s": 0.01},
            "status": status, "metrics": metrics, "error": None}


def pf(paths):
    return [[{"path": list(p), "flow": f} for p, f in paths.items()]]


def braess_doc(perturb=0.0):
    exp = C.braess_expected()
    recs = []
    for (wl, arm), v in exp.items():
        t = v.get("time", 0.0)
        m = {"tstt": v["tstt"] + perturb, "mean_trip_time": t, "max_trip_time": t,
             "link_flow": [0, 0, 0, 0, v.get("link_e", 0.0)], "path_flows": pf(v["paths"])}
        recs.append(rec("braess-d6", f"wl{int(wl)}", arm, {"with_link": wl, "demand": 6.0}, m))
    return {"records": recs}


def test_exp001_exact_and_contradiction():
    assert C.analyse_exp001(braess_doc())["verdict"] == "reproduced"
    assert C.analyse_exp001(braess_doc(perturb=1e-5))["verdict"].startswith("contradicted")


def test_exp002_analytic_records_confirm_derivation():
    recs = []
    for d in [0.25 * k for k in range(1, 49)]:
        for wl in (False, True):
            t = C.braess_ue_time(d, wl)
            if wl and C.B_MID < d < C.B_HIGH:
                g, f = (80 - 9 * d) / 13, (11 * d - 40) / 13
            elif wl and d <= C.B_MID:
                g, f = d, 0.0
            else:
                g, f = 0.0, d / 2
            paths = {(0, 1, 3): f, (0, 2, 3): f, (0, 1, 2, 3): g} if wl else {(0, 1, 3): d / 2, (0, 2, 3): d / 2}
            m = {"tstt": d * t, "max_trip_time": t, "path_flows": pf(paths)}
            recs.append(rec("sweep", f"wl{int(wl)}-d{d}", "UE", {"with_link": wl, "demand": d}, m))
    a = C.analyse_exp002({"records": recs})
    assert a["verdict"] == "derivation confirmed", a["boundaries"]
    assert all(b["pass"] for b in a["boundaries"].values())
    assert a["computed_paradox_demands_main_sweep"] == [2.75 + 0.25 * k for k in range(25)]
    # wrong physics: no paradox at all -> contradiction
    for r in recs:
        if r["factors"]["with_link"]:
            r["metrics"]["tstt"] = r["factors"]["demand"] * C.braess_ue_time(r["factors"]["demand"], False)
    assert C.analyse_exp002({"records": recs})["verdict"].startswith("contradicted")


def grid_doc(r_ue, cell="grid6", rho=2.0, status_ue=None, extra_cells=()):
    recs = []
    for i, r in enumerate(r_ue):
        key = f"grid6-s{2000 + i}-rho{rho:g}"
        f = {"rho": rho}
        recs.append(rec(cell, key, "SO", f, {"R": 0.0, "tstt": 1.0, "gini_stretch": 0.1, "p95_trip_time": 1.0}, seed=2000 + i))
        st = (status_ue or {}).get(i, "ok")
        recs.append(rec(cell, key, "UE", f, {"R": r, "tstt": 1 + r, "gini_stretch": 0.1, "p95_trip_time": 1.0}, status=st, seed=2000 + i))
        recs.append(rec(cell, key, "FF", f, {"R": r + 0.2, "tstt": 1.2 + r, "gini_stretch": 0.2, "p95_trip_time": 2.0}, seed=2000 + i))
    return recs


def test_exp003_primary_rule():
    rng = np.random.default_rng(1)
    big = list(0.03 + 0.005 * rng.standard_normal(100))
    a = C.analyse_exp003({"records": grid_doc(big)})
    assert a["primary"]["reject_H0"] is True and a["primary"]["n"] == 100
    assert a["primary"]["lower_one_sided_95"] > 0.01
    assert a["per_cell"]["grid6"]["2.0"]["paired_R_FF_minus_UE"]["median"] == pytest.approx(0.2)
    small = list(0.005 + 0.001 * rng.standard_normal(100))
    b = C.analyse_exp003({"records": grid_doc(small)})
    assert b["primary"]["reject_H0"] is False and b["primary"]["negligible"] is True
    # more than 10 percent nonconverged -> failed analysis
    c = C.analyse_exp003({"records": grid_doc(big, status_ue={i: "nonconverged" for i in range(11)})})
    assert c["primary"]["analysis_failed_10pct_rule"] is True and c["primary"]["verdict"].startswith("failed")
    d = C.analyse_exp003({"records": grid_doc(big, status_ue={i: "nonconverged" for i in range(10)})})
    assert d["primary"]["analysis_failed_10pct_rule"] is False and d["primary"]["n"] == 90


def test_exp003_sensitivity_pairs_with_primary():
    rng = np.random.default_rng(2)
    v = list(0.03 + 0.005 * rng.standard_normal(50))
    recs = grid_doc(v) + grid_doc([x + 0.001 for x in v], cell="S1-tol1e-8")
    a = C.analyse_exp003({"records": recs})
    s = a["sensitivity"]["S1-tol1e-8"]
    assert s["same_decision_as_primary"] is True
    assert s["paired_R_minus_primary"]["median"] == pytest.approx(0.001)
    assert a["s1_robust"] is True


def mix_doc(medians_by_c, n=60, scale=1.0, noise=0.002):
    rng = np.random.default_rng(3)
    recs = []
    for i in range(n):
        key = f"grid6-s{2000 + i}-cap{scale:g}"
        f = {"capacity_scale": scale, "rho": 2.0}
        recs.append(rec("mix", key, "SO", f, {"R": 0.0, "tstt": 1.0}, seed=2000 + i))
        recs.append(rec("mix", key, "FF", f, {"R": 0.3, "tstt": 1.3}, seed=2000 + i))
        base = noise * rng.standard_normal()
        for c, m in medians_by_c.items():
            r = 0.0 if c == 1 else m + base
            recs.append(rec("mix", key, f"MIX({c:g})", f, {"R": r, "tstt": 1 + r, "compliant_to_follower_time_ratio": 1.1},
                            seed=2000 + i))
    return recs


def test_exp004_monotone_and_not():
    a = C.analyse_exp004({"records": mix_doc({0: 0.04, 0.25: 0.03, 0.5: 0.02, 0.75: 0.01, 1: 0.0})})
    assert a["per_scale"]["1.0"]["H1_supported"] is True and a["verdict"].startswith("H1 supported")
    assert a["per_scale"]["1.0"]["identity_MIX1_max_abs_R"] == 0.0
    b = C.analyse_exp004({"records": mix_doc({0: 0.04, 0.25: 0.03, 0.5: 0.035, 0.75: 0.01, 1: 0.0})})
    st = b["per_scale"]["1.0"]["steps"]
    assert b["per_scale"]["1.0"]["H1_supported"] is False and st[1]["nonmonotone_evidence"] is True
    assert b["verdict"].startswith("H0 not rejected")


def test_wilson_known_values():
    lo, hi = C.wilson_interval(0, 100)
    assert lo == pytest.approx(0.0, abs=1e-12) and hi == pytest.approx(0.03699, abs=1e-4)
    lo, hi = C.wilson_interval(5, 100)
    assert lo == pytest.approx(0.02154, abs=1e-4) and hi == pytest.approx(0.11175, abs=1e-4)


def removal_cfg(seeds=(9000, 9001)):
    return {"config_version": "flow.config/1", "experiment_id": "TEST-RM", "label": "exploratory",
            "solver": {"algorithm": "gradient-projection", "tol": 1e-6, "max_iter": 20000},
            "cells": [{"cell": "removal", "network": "grid", "n": 3, "rho": [2.0], "seeds": list(seeds), "arms": ["UE"],
                       "mode": "link-removal", "recheck": {"tol": 1e-8, "flag_threshold": 1e-4}}]}


def test_link_removal_mode_runs_and_is_analysed(tmp_path):
    run = run_config(removal_cfg(), out_root=tmp_path, root=ROOT)
    doc = load_result(run / "results.json")
    skipped = json.loads((run / "skipped_removals.json").read_text())
    scan = [r for r in doc["records"] if r["factors"]["phase"] == "scan"]
    assert len(scan) + len(skipped) == 2 * (1 + 24)  # 3x3 grid: 24 directed links
    assert all(r["metrics"]["max_node_imbalance"] < 1e-6 for r in doc["records"] if r["status"] == "ok")
    man = json.loads((run / "run_manifest.json").read_text())
    assert "skipped_removals.json" in man["files"]
    a = C.analyse_exp005(doc, skipped)
    assert a["n_instances"] == 2 and a["incidence"]["1e-4"]["n"] <= 2
    for p in a["per_instance"]:
        assert set(p["braess_links_1e-3"]) <= set(p["braess_links_1e-4"])
        assert set(p["braess_links_confirmed_1e-8"]) <= set(p["braess_links_1e-4"])
    # every flagged link was re-solved at 1e-8 together with the full network
    for seed in (9000, 9001):
        flagged = next(p for p in a["per_instance"] if p["seed"] == seed)["braess_links_1e-4"]
        rech = [r for r in doc["records"] if r["seed"] == seed and r["factors"]["phase"] == "recheck"]
        assert len(rech) == (len(flagged) + 1 if flagged else 0)


def test_link_removal_skips_disconnecting_removal(tmp_path):
    from flow.generators import braess_demand, braess_network
    from flow.runner import Instance, run_link_removal

    net = braess_network(False)  # links a, b, c, d: removing any one leaves the other route
    inst = Instance("c", net, braess_demand(6.0), 1, {"rho": 1.0}, "k")
    cell = {"cell": "c", "recheck": {"tol": 1e-8, "flag_threshold": 1e-4}}
    recs, skipped = run_link_removal(inst, cell, {"algorithm": "gradient-projection", "tol": 1e-6}, "R")
    assert skipped == [] and len(recs) == 5
    from flow.network import Network

    chain = Network(n_nodes=3, tail=np.array([0, 1]), head=np.array([1, 2]), A=np.ones(2), B=np.ones(2), P=np.ones(2))
    from flow.network import Demand

    inst2 = Instance("c", chain, Demand.from_tuples([(0, 2, 1.0)]), 1, {}, "k2")
    recs, skipped = run_link_removal(inst2, cell, {"algorithm": "gradient-projection", "tol": 1e-6}, "R")
    assert len(recs) == 1 and len(skipped) == 2


def test_link_removal_config_validation():
    for mutate in (
        lambda c: c.update(arms=["UE", "SO"]),
        lambda c: c.update(network="braess"),
        lambda c: c.update(recheck={"tol": 1e-8}),
        lambda c: c.update(mode="other"),
        lambda c: c.update(rho=[1.0, 2.0]),
    ):
        cfg = removal_cfg()
        mutate(cfg["cells"][0])
        with pytest.raises(ConfigError):
            run_config(cfg, out_root=ROOT / "nonexistent", root=ROOT)


def test_exp005_config_implements_frozen_protocol():
    cfg = load_config(ROOT / "experiments" / "EXP-005.json")
    cell = cfg["cells"][0]
    assert cfg["label"] == "confirmatory" and cfg["solver"] == {"algorithm": "gradient-projection", "tol": 1e-6, "max_iter": 20000}
    assert cell["n"] == 4 and cell["rho"] == [2.0] and cell["seeds"] == list(range(1000, 1100))
    assert cell["recheck"] == {"tol": 1e-8, "flag_threshold": 1e-4}
    assert cfg["bpr"]["alpha"] == 0.15 and cfg["bpr"]["beta"] == 4.0
    assert freeze_status(ROOT, "EXP-005", cfg) == (True, "frozen")
    changed = copy.deepcopy(cfg)
    changed["cells"][0]["recheck"]["flag_threshold"] = 1e-3
    assert not freeze_status(ROOT, "EXP-005", changed)[0]


def test_exp006_gate_and_rule():
    def doc(gate, r2):
        recs = []
        for lv, rho in (("published", 5.8), (2.0, 2.0)):
            f = {"demand_level": lv, "rho": rho, "total_demand": 1.0}
            recs.append(rec("siouxfalls", f"sf-{lv}", "SO", f, {"R": 0.0, "tstt": 1.0}))
            m = {"R": r2 if lv == 2.0 else 0.1, "tstt": 1.1}
            if lv == "published":
                m["ref_flow_max_abs_diff_rel"] = gate
            recs.append(rec("siouxfalls", f"sf-{lv}", "UE", f, m))
        return {"records": recs}

    assert C.analyse_exp006(doc(1e-4, 0.05))["verdict"].startswith("direction replicates")
    assert C.analyse_exp006(doc(1e-4, 0.005))["verdict"].startswith("contradiction")
    assert C.analyse_exp006(doc(2e-3, 0.05))["verdict"].startswith("failed")
