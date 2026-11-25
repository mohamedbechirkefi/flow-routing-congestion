# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""M5 consistency (master prompt 11.6): the demo page shows the manuscript's numbers.

1. The committed demo/public/data/results.json equals a fresh in-memory export.
2. Every display string (display, interval_display, lower_display) appears verbatim in
   research/paper/manuscript.md, unless listed in DOCUMENTED_EXCEPTIONS with a reason.
3. The committed sandbox networks and engine fixture equal a fresh export.
4. No demo source file references a remote host.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = (ROOT / "research" / "paper" / "manuscript.md").read_text()

# display string -> reason. Empty: every printed number is in the manuscript verbatim.
DOCUMENTED_EXCEPTIONS: dict[str, str] = {}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _display_strings(obj) -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("display", "interval_display", "lower_display") and isinstance(v, str):
                out.append(v)
            else:
                out.extend(_display_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_display_strings(v))
    return out


def test_results_json_matches_fresh_export():
    mod = _load("export_demo_data")
    committed = mod.OUT.read_text()
    assert committed == mod.render(mod.build())


def test_every_display_string_is_in_the_manuscript():
    data = json.loads((ROOT / "demo" / "public" / "data" / "results.json").read_text())
    strings = _display_strings(data)
    assert len(strings) > 100
    missing = sorted({s for s in strings if s not in MANUSCRIPT and s not in DOCUMENTED_EXCEPTIONS})
    assert missing == []


def test_every_registered_experiment_is_exported_with_claims():
    data = json.loads((ROOT / "demo" / "public" / "data" / "results.json").read_text())
    ids = [e["id"] for e in data["experiments"]]
    import csv

    registry = [r["experiment_id"] for r in csv.DictReader((ROOT / "research" / "experiment_registry.csv").open())]
    assert set(registry) <= set(ids)
    labels = {e["id"]: e["label"] for e in data["experiments"]}
    assert labels["X-EXP-001-TOL1E-10"] == "exploratory" and labels["X-EXP-002-TOL1E-10"] == "exploratory"
    verdicts = {e["id"]: e["verdict"] for e in data["experiments"]}
    assert verdicts["EXP-001"] == "Contradicted" and verdicts["EXP-002"] == "Contradicted"
    assert all(e["claim_ids"] for e in data["experiments"])


def test_sandbox_files_match_fresh_export():
    mod = _load("export_demo_sandbox")
    assert mod.OUT_NETWORKS.read_text() == mod.render(mod.networks())
    assert mod.OUT_FIXTURE.read_text() == mod.render(mod.fixture())
    seeds = [g["seed"] for g in json.loads(mod.OUT_NETWORKS.read_text())["grids"]]
    assert all(9000 <= s <= 9019 for s in seeds)  # exploratory seeds only


def test_demo_sources_reference_no_remote_host():
    pattern = re.compile(r"(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    for p in (ROOT / "demo" / "site").iterdir():
        hits = {m for m in pattern.findall(p.read_text()) if m != "http://www.w3.org"}
        assert hits == set(), (p.name, hits)
