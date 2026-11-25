# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Integration: config -> runner -> schema-validated results, manifest, report; freeze guard."""
import copy
import json
import shutil
from pathlib import Path

import pytest

from flow import cli
from flow.analysis import bootstrap_median, paired_differences, percentile_interval
from flow.network import FlowError
from flow.report import write_report
from flow.runner import (
    ConfigError,
    FreezeError,
    config_hash,
    freeze_status,
    load_config,
    repo_root,
    run_config,
    sha256_file,
    smoke_config,
)
from flow.schema import SchemaError, load_result, validate_result

ROOT = repo_root()


def tiny_config(label="exploratory", seeds=(9000,)):
    return {
        "config_version": "flow.config/1",
        "experiment_id": "TEST",
        "label": label,
        "solver": {"algorithm": "frank-wolfe", "tol": 1e-6, "max_iter": 2000},
        "cells": [
            {"cell": "b", "network": "braess", "with_link": [True], "demand": [6.0], "arms": ["FF", "UE"]},
            {"cell": "g", "network": "grid", "n": 3, "rho": [1.0, 2.0], "seeds": list(seeds), "arms": ["FF", "UE", "SO", "MIX(0.5)"]},
        ],
    }


@pytest.fixture(scope="module")
def run_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("runs")
    return run_config(tiny_config(), out_root=out, root=ROOT)


def test_run_outputs_validate(run_dir):
    doc = load_result(run_dir / "results.json")
    assert doc["label"] == "exploratory" and doc["schema_version"] == "flow.result/1.0.0"
    assert len(doc["records"]) == 2 + 2 * 4
    for r in doc["records"]:
        assert r["status"] in ("ok", "nonconverged")
        assert r["metrics"]["max_node_imbalance"] < 1e-6
    so = [r for r in doc["records"] if r["arm"] == "SO"]
    assert all(r["metrics"]["R"] == 0.0 for r in so)
    ue = [r for r in doc["records"] if r["arm"] == "UE" and r["cell"] == "g"]
    assert all(r["metrics"]["R"] >= -1e-6 for r in ue)


def test_manifest_fields(run_dir):
    man = json.loads((run_dir / "run_manifest.json").read_text())
    for key in ("config_hash", "seeds", "git", "environment", "runtime_s", "peak_rss_bytes", "files", "status_counts"):
        assert key in man
    assert man["seeds"] == [9000]
    assert man["config_hash"] == config_hash(json.loads((run_dir / "config.json").read_text()))
    assert man["files"]["results.json"] == sha256_file(run_dir / "results.json")
    assert man["environment"]["python"].startswith("3.12")


def test_rerun_is_deterministic(run_dir, tmp_path):
    other = run_config(tiny_config(), out_root=tmp_path, root=ROOT)
    a = load_result(run_dir / "results.json")["records"]
    b = load_result(other / "results.json")["records"]
    strip = lambda recs: [(r["cell"], r["seed"], r["arm"], r["metrics"], r["solver"]["iterations"]) for r in recs]
    assert strip(a) == strip(b)


def test_report_generation(run_dir):
    res = write_report(run_dir, pdf=False)
    md = (run_dir / "report.md").read_text()
    assert "EXPLORATORY" in md and "| g |" in md
    assert res["figures"] and all((run_dir / "figures" / f).exists() for f in res["figures"])


@pytest.mark.skipif(not Path(__import__("flow.report", fromlist=["PANDOC"]).PANDOC).exists(), reason="pandoc not available")
def test_report_pdf(run_dir, tmp_path):
    d = tmp_path / "copy"
    shutil.copytree(run_dir, d)
    res = write_report(d, pdf=True)
    pdf = Path(res["pdf"])
    assert pdf.exists() and pdf.read_bytes()[:5] == b"%PDF-"


def test_schema_rejects_malformed(run_dir):
    doc = json.loads((run_dir / "results.json").read_text())
    for mutate in (
        lambda d: d.pop("records"),
        lambda d: d.update(label="final"),
        lambda d: d.update(extra=1),
        lambda d: d["records"][0].update(status="maybe"),
        lambda d: d["records"][0]["solver"].update(runtime_s=-1.0),
        lambda d: d["records"][0]["metrics"].update(tstt=float("nan")),
        lambda d: d.update(schema_version="flow.result/0.9"),
    ):
        bad = copy.deepcopy(doc)
        mutate(bad)
        with pytest.raises(SchemaError):
            validate_result(bad)
    p = run_dir / "broken.json"
    p.write_text("{not json")
    with pytest.raises(SchemaError):
        load_result(p)


def test_confirmatory_refused_without_freeze(tmp_path):
    cfg = tiny_config(label="confirmatory", seeds=(2000,))
    cfg["experiment_id"] = "EXP-003"
    with pytest.raises(FreezeError):  # differs from the frozen EXP-003 config
        run_config(cfg, out_root=tmp_path, root=ROOT)
    cfg["experiment_id"] = "EXP-099"  # no freeze record at all
    with pytest.raises(FreezeError):
        run_config(cfg, out_root=tmp_path, root=ROOT)
    assert not any(tmp_path.iterdir())  # nothing written
    assert cli.main(["run", "EXP-098", "--out", str(tmp_path), "--quiet"]) == 2  # no config file


def test_freeze_status_requires_matching_hashes(tmp_path):
    root = tmp_path / "repo"
    (root / "research" / "experiments" / "EXP-001").mkdir(parents=True)
    (root / "research" / "protocol.md").write_text("protocol v1\n")
    (root / "research" / "experiments" / "EXP-001" / "protocol.md").write_text("exp v1\n")
    log = root / "research" / "decision_log.md"
    log.write_text("# log\n")
    assert freeze_status(root, "EXP-001")[0] is False
    h1 = sha256_file(root / "research" / "protocol.md")
    h2 = sha256_file(root / "research" / "experiments" / "EXP-001" / "protocol.md")
    (root / "experiments").mkdir()
    cfg = tiny_config(label="confirmatory", seeds=(2000,))
    cfg["experiment_id"] = "EXP-001"
    (root / "experiments" / "EXP-001.json").write_text(json.dumps(cfg))
    log.write_text(f"# log\nFREEZE research/protocol.md sha256:{h1}\nFREEZE research/experiments/EXP-001/protocol.md sha256:{h2}\n")
    ok, reason = freeze_status(root, "EXP-001")
    assert not ok and "experiments/EXP-001.json" in reason  # config hash is required too
    h3 = sha256_file(root / "experiments" / "EXP-001.json")
    log.write_text(log.read_text() + f"FREEZE experiments/EXP-001.json sha256:{h3}\n")
    assert freeze_status(root, "EXP-001") == (True, "frozen")
    assert freeze_status(root, "EXP-001", cfg) == (True, "frozen")
    changed = copy.deepcopy(cfg)
    changed["cells"][1]["rho"] = [2.0]
    ok, reason = freeze_status(root, "EXP-001", changed)
    assert not ok and "differs" in reason
    (root / "experiments" / "EXP-001.json").write_text(json.dumps(changed))
    ok, reason = freeze_status(root, "EXP-001")
    assert not ok and "changed" in reason
    (root / "experiments" / "EXP-001.json").write_text(json.dumps(cfg))
    (root / "research" / "protocol.md").write_text("protocol v2\n")
    ok, reason = freeze_status(root, "EXP-001")
    assert not ok and "changed" in reason


FROZEN = ("EXP-001", "EXP-002", "EXP-003", "EXP-004", "EXP-005", "EXP-006")


class _Stop(Exception):
    pass


def _no_solves(monkeypatch):
    """Make any accidental confirmatory execution impossible: expanding a cell raises."""
    import flow.runner as runner

    def stop(*a, **k):
        raise _Stop("guard passed; execution blocked by the test")

    monkeypatch.setattr(runner, "expand_cell", stop)


def test_real_repository_is_frozen_and_guard_accepts_frozen_configs(monkeypatch, tmp_path):
    _no_solves(monkeypatch)
    for eid in FROZEN:
        cfg = load_config(ROOT / "experiments" / f"{eid}.json")
        assert freeze_status(ROOT, eid, cfg) == (True, "frozen"), eid
        with pytest.raises(_Stop):  # the guard lets the frozen config through
            run_config(cfg, out_root=tmp_path / eid, root=ROOT)


def test_guard_refuses_changed_configs(monkeypatch, tmp_path):
    _no_solves(monkeypatch)
    for eid in FROZEN:
        cfg = load_config(ROOT / "experiments" / f"{eid}.json")
        changed = copy.deepcopy(cfg)
        changed["solver"]["tol"] = 1e-5
        with pytest.raises(FreezeError, match="differs"):
            run_config(changed, out_root=tmp_path / eid, root=ROOT)
    assert not any(tmp_path.iterdir())


def test_guard_refuses_edited_frozen_files(tmp_path):
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "research", root / "research")
    shutil.copytree(ROOT / "experiments", root / "experiments")
    assert freeze_status(root, "EXP-003")[0]
    f = root / "experiments" / "EXP-003.json"
    f.write_text(f.read_text().replace("0.10826", "0.2"))
    ok, reason = freeze_status(root, "EXP-003")
    assert not ok and "changed" in reason
    p = root / "research" / "protocol.md"
    p.write_text(p.read_text() + "edit\n")
    assert not freeze_status(root, "EXP-001")[0]


def test_exp005_config_added_before_data_is_accepted(tmp_path):
    # M3 (2026-11-25): config implementing the frozen EXP-005 protocol, hash recorded in D-012
    assert freeze_status(ROOT, "EXP-005") == (True, "frozen")
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "research", root / "research")
    shutil.copytree(ROOT / "experiments", root / "experiments")
    (root / "experiments" / "EXP-005.json").unlink()
    ok, reason = freeze_status(root, "EXP-005")
    assert not ok and "EXP-005.json" in reason


def test_config_validation():
    bad_seed = tiny_config(seeds=(2000,))
    with pytest.raises(ConfigError, match="9000-9019"):
        run_config(bad_seed, out_root=Path("/nonexistent"), root=ROOT)
    for mutate in (
        lambda c: c.update(config_version="x"),
        lambda c: c.update(label="final"),
        lambda c: c["cells"][0].update(arms=["XX"]),
        lambda c: c["cells"][1].update(calibration="absolute"),
        lambda c: c["cells"].append(dict(c["cells"][0])),
        lambda c: c["solver"].update(algorithm="newton"),
    ):
        cfg = tiny_config()
        mutate(cfg)
        with pytest.raises(ConfigError):
            run_config(cfg, out_root=Path("/nonexistent"), root=ROOT)


def test_failed_record_is_kept(tmp_path, monkeypatch):
    import flow.runner as runner

    def boom(*a, **k):
        raise RuntimeError("injected failure")

    monkeypatch.setattr(runner, "free_flow", boom)
    cfg = tiny_config()
    cfg["cells"] = [{"cell": "g", "network": "grid", "n": 3, "rho": [1.0], "seeds": [9000], "arms": ["SO", "FF"],
                     "solver": {"algorithm": "gradient-projection"}}]
    run = run_config(cfg, out_root=tmp_path, root=ROOT)
    recs = load_result(run / "results.json")["records"]
    assert [r["status"] for r in recs] == ["ok", "failed"]
    assert "injected failure" in recs[1]["error"]


def test_mix_runs_with_gradient_projection(tmp_path):
    cfg = tiny_config()
    cfg["solver"] = {"algorithm": "gradient-projection", "tol": 1e-6, "max_iter": 20000}
    cfg["cells"] = [{"cell": "g", "network": "grid", "n": 3, "rho": [2.0], "seeds": [9000],
                     "arms": ["SO", "UE", "MIX(0)", "MIX(0.5)", "MIX(1)"]}]
    recs = load_result(run_config(cfg, out_root=tmp_path, root=ROOT) / "results.json")["records"]
    by = {r["arm"]: r for r in recs}
    assert all(r["status"] == "ok" for r in recs)
    assert by["MIX(1)"]["metrics"]["R"] == pytest.approx(0.0, abs=1e-12)
    assert by["MIX(0)"]["metrics"]["tstt"] == pytest.approx(by["UE"]["metrics"]["tstt"], rel=1e-9)
    assert by["MIX(0.5)"]["metrics"]["follower_converged"] is True


def test_shipped_experiment_configs_are_valid_and_confirmatory():
    for eid in ("EXP-001", "EXP-002", "EXP-003", "EXP-004", "EXP-006"):
        cfg = load_config(ROOT / "experiments" / f"{eid}.json")
        assert cfg["label"] == "confirmatory" and cfg["experiment_id"] == eid
        assert cfg["solver"]["algorithm"] == "gradient-projection"  # amendment A1


def test_frozen_configs_carry_the_approved_amendments():
    c3 = load_config(ROOT / "experiments" / "EXP-003.json")
    cells = {c["cell"]: c for c in c3["cells"]}
    assert cells["grid4"]["seeds"] == list(range(1000, 1100))  # A2
    assert cells["grid6"]["seeds"] == list(range(2000, 2100))
    assert cells["grid6"]["rho"] == [1.0, 2.0, 3.0]  # A3
    assert cells["S3-absolute"]["absolute_share"] == 0.10826  # A5, fitted J-0011
    assert cells["S1-frank-wolfe-reference"]["solver"]["algorithm"] == "frank-wolfe"
    assert c3["bpr"]["alpha"] == 0.15 and c3["bpr"]["beta"] == 4.0  # C-BPR, fitted J-0010
    c4 = load_config(ROOT / "experiments" / "EXP-004.json")
    assert c4["cells"][0]["seeds"] == list(range(2000, 2100))
    smoke = smoke_config()
    assert smoke["label"] == "exploratory"


def test_bootstrap_helpers():
    v = [0.01, 0.02, 0.03, 0.04, 0.05]
    a = bootstrap_median(v, resamples=500)
    b = bootstrap_median(v, resamples=500)
    assert (a == b).all() and a.min() >= 0.01 and a.max() <= 0.05
    lo, hi = percentile_interval(v, resamples=2000)
    assert 0.01 <= lo <= 0.03 <= hi <= 0.05
    lo1, inf = percentile_interval(v, one_sided_lower=True, resamples=2000)
    assert inf == float("inf") and lo1 >= lo
    assert list(paired_differences({"a": 2, "b": 3}, {"b": 1, "a": 1, "c": 9})) == [1, 2]
    with pytest.raises(FlowError):
        bootstrap_median([])
    with pytest.raises(FlowError):
        paired_differences({"a": 1}, {"b": 1})
