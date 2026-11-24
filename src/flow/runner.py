# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Experiment runner: config -> solves -> validated results, metrics table and run manifest.

Guards (G-FREEZE, protocol section 5):
* a confirmatory config runs only if the protocol freeze is recorded in
  ``research/decision_log.md`` with SHA-256 values that match the current
  ``research/protocol.md``, the experiment's protocol file and the experiment's
  config ``experiments/<EXP>.json``, and only if the config being run is
  identical to that frozen config file;
* an exploratory config may only use the exploratory seeds 9000-9019 and writes
  under ``results/exploratory/``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import resource
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import __version__
from .assignment import (
    AssignmentResult,
    free_flow,
    frank_wolfe,
    gradient_projection,
    mixed_compliance,
)
from .generators import (
    BPR_ALPHA,
    BPR_BETA,
    GRID_GENERATOR_VERSION,
    braess_demand,
    braess_network,
    make_grid,
    reference_demand_absolute,
    reference_demand_ff,
    reference_demand_ff_network,
)
from .metrics import evaluate, node_balance
from .network import Demand, FlowError, Network
from .schema import SCHEMA_VERSION, clean_json, dump_result
from .tntp import build_demand, ingest

CONFIG_VERSION = "flow.config/1"
MANIFEST_VERSION = "flow.manifest/1"
EXPLORATORY_SEEDS = range(9000, 9020)
ALGORITHMS = ("frank-wolfe", "gradient-projection")
# Real networks (owner approval 2026-11-24, round 2): local files only, never committed.
TNTP_DATASETS = {
    "siouxfalls": {
        "dir": "data/raw/tntp/SiouxFalls",
        "net": "SiouxFalls_net.tntp",
        "trips": "SiouxFalls_trips.tntp",
        "flow": "SiouxFalls_flow.tntp",
        "manifest_id": "tntp-siouxfalls",
    }
}


class ConfigError(FlowError):
    """Invalid experiment configuration."""


class FreezeError(FlowError):
    """A confirmatory run was requested but the protocol freeze is not recorded."""


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "master_prompt.md").exists() and (parent / "research").is_dir():
            return parent
    return Path.cwd()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_hash(config: dict) -> str:
    return hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def freeze_status(root: Path, experiment_id: str | None, cfg: dict | None = None) -> tuple[bool, str]:
    """True only if decision_log records a freeze whose hashes match the current files.

    A freeze record is a line ``FREEZE <relative path> sha256:<hex>`` written by the
    owner (or on the owner's recorded instruction) in ``research/decision_log.md``.
    Required: ``research/protocol.md``, the experiment's protocol and, when an
    experiment id is given, its config ``experiments/<EXP>.json``. If ``cfg`` is
    given it must equal the frozen config file (canonical JSON hash).
    """
    log = root / "research" / "decision_log.md"
    if not log.exists():
        return False, "research/decision_log.md not found"
    text = log.read_text()
    records = dict(re.findall(r"^FREEZE\s+(\S+)\s+sha256:([0-9a-f]{64})\s*$", text, flags=re.M))
    needed = ["research/protocol.md"]
    if experiment_id:
        needed.append(f"research/experiments/{experiment_id}/protocol.md")
        needed.append(f"experiments/{experiment_id}.json")
    for rel in needed:
        f = root / rel
        if not f.exists():
            return False, f"{rel} not found"
        if rel not in records:
            return False, f"no FREEZE record for {rel} in research/decision_log.md (protocol not frozen; G-FREEZE)"
        if records[rel] != sha256_file(f):
            return False, f"{rel} changed since its recorded freeze (hash mismatch)"
    if cfg is not None and experiment_id:
        frozen_cfg = json.loads((root / f"experiments/{experiment_id}.json").read_text())
        if config_hash(cfg) != config_hash(frozen_cfg):
            return False, f"config differs from the frozen experiments/{experiment_id}.json"
    return True, "frozen"


def validate_config(cfg: dict) -> None:
    if cfg.get("config_version") != CONFIG_VERSION:
        raise ConfigError(f"config_version must be {CONFIG_VERSION}")
    if cfg.get("label") not in ("exploratory", "confirmatory"):
        raise ConfigError("label must be 'exploratory' or 'confirmatory'")
    solver = cfg.get("solver", {})
    if solver.get("algorithm", "frank-wolfe") not in ALGORITHMS:
        raise ConfigError(f"solver.algorithm must be one of {ALGORITHMS}")
    validate_bpr(cfg)
    cells = cfg.get("cells")
    if not isinstance(cells, list) or not cells:
        raise ConfigError("config needs a nonempty list of cells")
    names = set()
    for cell in cells:
        name = cell.get("cell")
        if not name or name in names:
            raise ConfigError(f"cell names must be unique and nonempty: {name!r}")
        names.add(name)
        if cell.get("network") not in ("braess", "grid", "tntp"):
            raise ConfigError(f"{name}: network must be 'braess', 'grid' or 'tntp'")
        if cell["network"] == "tntp":
            if cell.get("dataset") not in TNTP_DATASETS:
                raise ConfigError(f"{name}: tntp cells need dataset in {sorted(TNTP_DATASETS)}")
            levels = cell.get("demand_levels")
            if not isinstance(levels, list) or not levels:
                raise ConfigError(f"{name}: tntp cells need a nonempty demand_levels list")
            for lv in levels:
                if lv != "published" and not (isinstance(lv, (int, float)) and lv > 0):
                    raise ConfigError(f"{name}: demand level must be 'published' or a positive rho")
        for arm in cell.get("arms", []):
            parse_arm(arm)
        if cell["network"] == "grid":
            seeds = cell.get("seeds", [])
            if not seeds:
                raise ConfigError(f"{name}: grid cells need seeds")
            if cfg["label"] == "exploratory" and any(s not in EXPLORATORY_SEEDS for s in seeds):
                raise ConfigError(f"{name}: exploratory runs may only use seeds 9000-9019")
            if cell.get("calibration", "ff") not in ("ff", "absolute"):
                raise ConfigError(f"{name}: calibration must be 'ff' or 'absolute'")
            if cell.get("calibration") == "absolute" and "absolute_share" not in cell:
                raise ConfigError(f"{name}: absolute calibration needs absolute_share")


def validate_bpr(cfg: dict) -> tuple[float, float]:
    bpr = cfg.get("bpr", {})
    if not isinstance(bpr, dict) or set(bpr) - {"alpha", "beta", "source"}:
        raise ConfigError("bpr must be an object with keys alpha, beta, source")
    alpha = float(bpr.get("alpha", BPR_ALPHA))
    beta = float(bpr.get("beta", BPR_BETA))
    if not (alpha >= 0 and beta >= 1):
        raise ConfigError("bpr needs alpha >= 0 and beta >= 1")
    return alpha, beta


def parse_arm(arm: str) -> tuple[str, float | None]:
    if arm in ("FF", "UE", "SO"):
        return arm, None
    m = re.fullmatch(r"MIX\(([0-9.]+)\)", arm)
    if m:
        c = float(m.group(1))
        if not 0 <= c <= 1:
            raise ConfigError(f"compliance out of range in {arm}")
        return "MIX", c
    raise ConfigError(f"unknown arm {arm!r}")


@dataclass
class Instance:
    cell: str
    network: Network
    demand: Demand
    seed: int | None
    factors: dict
    key: str
    reference_flow: np.ndarray | None = None


def load_tntp(dataset: str, root: Path):
    """Load a git-ignored TNTP dataset after checking every file's SHA-256 against data/manifest.json."""
    spec = TNTP_DATASETS[dataset]
    d = root / spec["dir"]
    man = json.loads((root / "data" / "manifest.json").read_text())
    want = {x["file"]: x["sha256"] for x in man.get("downloads", []) if x.get("dataset") == spec["manifest_id"]}
    texts = {}
    for key in ("net", "trips", "flow"):
        f = d / spec[key]
        if not f.exists():
            raise ConfigError(f"{f} missing: run scripts/download_tntp.py first")
        if want.get(spec[key]) != sha256_file(f):
            raise ConfigError(f"{f} SHA-256 does not match data/manifest.json")
        texts[key] = f.read_text()
    return ingest(texts["net"], texts["trips"], texts["flow"], name=dataset)


def expand_cell(cell: dict, bpr: tuple[float, float] = (BPR_ALPHA, BPR_BETA), root: Path | None = None) -> list[Instance]:
    out: list[Instance] = []
    if cell["network"] == "tntp":
        tn = load_tntp(cell["dataset"], root or repo_root())
        published = build_demand(list(tn.trips))
        dref = reference_demand_ff_network(tn.network, published)
        for lv in cell["demand_levels"]:
            if lv == "published":
                dem, rho = published, published.total / dref
            else:
                rho = float(lv)
                dem = published.scaled(rho * dref / published.total)
            factors = {
                "dataset": cell["dataset"],
                "demand_level": lv if lv == "published" else float(lv),
                "rho": rho,
                "d_ref": dref,
                "total_demand": dem.total,
            }
            inst = Instance(cell["cell"], tn.network, dem, None, factors, f"{cell['dataset']}-{lv}")
            inst.reference_flow = tn.reference_flow if lv == "published" else None
            out.append(inst)
        return out
    if cell["network"] == "braess":
        for wl in cell.get("with_link", [True]):
            for d in cell["demand"]:
                net = braess_network(bool(wl))
                factors = {"with_link": bool(wl), "demand": float(d)}
                out.append(Instance(cell["cell"], net, braess_demand(float(d)), None, factors, f"braess-wl{int(wl)}-d{d}"))
        return out
    n = int(cell["n"])
    alpha = float(bpr[0])
    beta = float(cell.get("beta", bpr[1]))
    scales = cell.get("capacity_scale", [1.0])
    for seed in cell["seeds"]:
        base = make_grid(n, int(seed), beta=beta, alpha=alpha)
        if cell.get("calibration", "ff") == "ff":
            dref = reference_demand_ff(base)
        else:
            dref = reference_demand_absolute(base, float(cell["absolute_share"]))
        for scale in scales:
            inst = base if float(scale) == 1.0 else make_grid(n, int(seed), beta=beta, alpha=alpha, capacity_scale=float(scale))
            for rho in cell["rho"]:
                factors = {
                    "n": n,
                    "rho": float(rho),
                    "alpha": alpha,
                    "beta": beta,
                    "capacity_scale": float(scale),
                    "calibration": cell.get("calibration", "ff"),
                    "d_ref": dref,
                    "total_demand": float(rho) * dref,
                    "generator": GRID_GENERATOR_VERSION,
                }
                key = f"grid{n}-s{seed}-a{alpha:g}-b{beta:g}-cap{float(scale):g}-rho{float(rho):g}"
                out.append(Instance(cell["cell"], inst.network, inst.demand(float(rho) * dref), int(seed), factors, key))
    return out


def _solve(inst: Instance, arm: str, solver: dict, so_cache: dict) -> AssignmentResult:
    kind, c = parse_arm(arm)
    tol = float(solver.get("tol", 1e-6))
    max_iter = int(solver.get("max_iter", 20_000))
    algo = solver.get("algorithm", "frank-wolfe")

    def solve(obj: str) -> AssignmentResult:
        if algo == "gradient-projection":
            return gradient_projection(inst.network, inst.demand, obj, tol=tol, max_iter=max_iter)
        return frank_wolfe(inst.network, inst.demand, obj, tol=tol, max_iter=max_iter)

    if kind == "FF":
        return free_flow(inst.network, inst.demand)
    if kind == "UE":
        return solve("ue")
    if kind == "SO":
        if inst.key not in so_cache:
            so_cache[inst.key] = solve("so")
        return so_cache[inst.key]
    so = None
    if c and c > 0:
        if inst.key not in so_cache:
            so_cache[inst.key] = solve("so")
        so = so_cache[inst.key]
    return mixed_compliance(inst.network, inst.demand, float(c), so_result=so, tol=tol, max_iter=max_iter, algorithm=algo)


def _mix_extra(inst: Instance, res: AssignmentResult) -> dict:
    t = inst.network.link_time(res.link_flow)
    from .paths import LinkLookup

    lk = LinkLookup(inst.network)

    def mean_time(groups) -> float | None:
        num = den = 0.0
        for pf in groups:
            for path, f in pf.items():
                num += f * float(sum(t[e] for e in lk.links(path)))
                den += f
        return num / den if den > 0 else None

    comp = mean_time(res.extra.get("compliant_path_flows", []))
    fol = mean_time(res.extra.get("follower_path_flows", []))
    return {
        "compliant_mean_time": comp,
        "follower_mean_time": fol,
        "compliant_to_follower_time_ratio": (comp / fol) if comp and fol else None,
    }


def git_info(root: Path) -> dict:
    def run(*args: str) -> str | None:
        try:
            return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    status = run("status", "--porcelain")
    return {"revision": run("rev-parse", "HEAD"), "dirty": bool(status) if status is not None else None}


def environment_info() -> dict:
    cpu = platform.processor()
    try:
        cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, check=True).stdout.strip() or cpu
    except (OSError, subprocess.CalledProcessError):
        pass
    import importlib.metadata as md

    def ver(name: str) -> str | None:
        try:
            return md.version(name)
        except md.PackageNotFoundError:
            return None

    return {
        "os": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "python": sys.version.split()[0],
        "packages": {"flow": __version__, "numpy": ver("numpy"), "matplotlib": ver("matplotlib"), "typst": ver("typst")},
    }


def peak_rss_bytes() -> int:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r if sys.platform == "darwin" else r * 1024)


def run_config(cfg: dict, out_root: Path | None = None, root: Path | None = None, log=None) -> Path:
    """Execute a config. Returns the run directory. Raises FreezeError for unfrozen confirmatory configs."""
    validate_config(cfg)
    root = root or repo_root()
    exp_id = cfg.get("experiment_id")
    if cfg["label"] == "confirmatory":
        ok, reason = freeze_status(root, exp_id, cfg)
        if not ok:
            raise FreezeError(f"refusing confirmatory run of {exp_id}: {reason}")
        out_root = out_root or root / "results" / "raw" / str(exp_id)
    else:
        out_root = out_root or root / "results" / "exploratory"
    chash = config_hash(cfg)
    started = datetime.now(timezone.utc)
    run_id = f"{exp_id or 'run'}-{started.strftime('%Y%m%dT%H%M%SZ')}-{chash[:8]}"
    run_dir = Path(out_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "config.json").write_text(json.dumps(cfg, indent=1, sort_keys=True) + "\n")
    solver = cfg.get("solver", {})
    t0 = time.perf_counter()
    records: list[dict] = []
    for cell in cfg["cells"]:
        cell_solver = {**solver, **cell.get("solver", {})}
        for inst in expand_cell(cell, validate_bpr(cfg), root):
            so_cache: dict = {}
            arms = list(cell["arms"])
            # SO first so that R can be computed for every arm of the instance
            order = sorted(arms, key=lambda a: 0 if a == "SO" else 1)
            so_tstt = None
            for arm in order:
                rec = {
                    "record_id": f"{run_id}/{cell['cell']}/{inst.key}/{arm}",
                    "cell": cell["cell"],
                    "network": inst.network.name,
                    "seed": inst.seed,
                    "factors": inst.factors,
                    "arm": arm,
                    "solver": {
                        "algorithm": "all-or-nothing" if arm == "FF" else cell_solver.get("algorithm", "frank-wolfe"),
                        "tol": None if arm == "FF" else float(cell_solver.get("tol", 1e-6)),
                        "max_iter": None if arm == "FF" else int(cell_solver.get("max_iter", 20_000)),
                        "iterations": None,
                        "rel_gap": None,
                        "converged": False,
                        "runtime_s": 0.0,
                    },
                    "status": "failed",
                    "metrics": None,
                    "error": None,
                }
                ts = time.perf_counter()
                try:
                    res = _solve(inst, arm, cell_solver, so_cache)
                    m = evaluate(inst.network, inst.demand, res)
                    m["max_node_imbalance"] = float(np.max(np.abs(node_balance(inst.network, inst.demand, res.link_flow))))
                    m["min_link_time"] = float(np.min(inst.network.link_time(res.link_flow)))
                    if arm == "SO":
                        so_tstt = m["tstt"]
                    m["R"] = (m["tstt"] / so_tstt - 1.0) if so_tstt else None
                    if arm.startswith("MIX"):
                        m.update(_mix_extra(inst, res))
                        m["follower_converged"] = res.extra.get("follower_converged")
                        m["so_converged"] = res.extra.get("so_converged")
                    if arm == "UE" and inst.reference_flow is not None:
                        ref = inst.reference_flow
                        m["ref_flow_max_abs_diff_rel"] = float(np.max(np.abs(res.link_flow - ref)) / np.max(np.abs(ref)))
                    rec["metrics"] = m
                    rec["solver"].update(
                        iterations=int(res.iterations),
                        rel_gap=None if not np.isfinite(res.rel_gap) else float(res.rel_gap),
                        converged=bool(res.converged),
                    )
                    rec["status"] = "ok" if res.converged else "nonconverged"
                except Exception as exc:  # recorded, never dropped silently
                    rec["error"] = "".join(traceback.format_exception(exc))
                rec["solver"]["runtime_s"] = time.perf_counter() - ts
                records.append(clean_json(rec))
                if log:
                    log(f"{rec['record_id']} {rec['status']} it={rec['solver']['iterations']} rg={rec['solver']['rel_gap']} {rec['solver']['runtime_s']:.2f}s")
    runtime = time.perf_counter() - t0
    doc = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "label": cfg["label"],
        "experiment_id": exp_id,
        "config_hash": chash,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "records": records,
    }
    dump_result(doc, run_dir / "results.json")
    write_metrics_csv(records, run_dir / "metrics.csv")
    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "run_id": run_id,
        "label": cfg["label"],
        "experiment_id": exp_id,
        "config_hash": chash,
        "config_path": "config.json",
        "seeds": sorted({r["seed"] for r in records if r["seed"] is not None}),
        "git": git_info(root),
        "environment": environment_info(),
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_s": runtime,
        "peak_rss_bytes": peak_rss_bytes(),
        "peak_rss_note": "process-wide maximum resident set size from getrusage; includes interpreter and imports",
        "n_records": len(records),
        "status_counts": {s: sum(r["status"] == s for r in records) for s in ("ok", "nonconverged", "failed")},
        "files": {
            name: sha256_file(run_dir / name) for name in ("config.json", "results.json", "metrics.csv")
        },
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(clean_json(manifest), indent=1, sort_keys=True) + "\n")
    return run_dir


METRIC_COLUMNS = [
    "tstt", "R", "mean_trip_time", "p95_trip_time", "gini_stretch", "flow_weighted_vc",
    "share_links_over_capacity", "max_vc", "max_node_imbalance", "compliant_to_follower_time_ratio",
]


def write_metrics_csv(records: list[dict], path: Path) -> None:
    factor_keys = sorted({k for r in records for k in r["factors"]})
    cols = ["record_id", "cell", "network", "seed", "arm", "status"] + factor_keys + [
        "iterations", "rel_gap", "converged", "runtime_s"] + METRIC_COLUMNS
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in records:
            m = r["metrics"] or {}
            row = [r["record_id"], r["cell"], r["network"], r["seed"], r["arm"], r["status"]]
            row += [r["factors"].get(k) for k in factor_keys]
            s = r["solver"]
            row += [s["iterations"], s["rel_gap"], s["converged"], s["runtime_s"]]
            row += [m.get(k) for k in METRIC_COLUMNS]
            w.writerow(row)


def smoke_config() -> dict:
    """Smoke matrix of protocol section 8 (exploratory)."""
    return {
        "config_version": CONFIG_VERSION,
        "experiment_id": "SMOKE",
        "label": "exploratory",
        "description": "Protocol section 8 smoke matrix: pipeline, schemas and timing only. Exploratory.",
        "solver": {"algorithm": "frank-wolfe", "tol": 1e-6, "max_iter": 20000},
        "cells": [
            {"cell": "braess-d6", "network": "braess", "with_link": [False, True], "demand": [6.0], "arms": ["FF", "UE", "SO"]},
            {"cell": "grid3-rho1", "network": "grid", "n": 3, "rho": [1.0], "seeds": [9000, 9001, 9002, 9003, 9004],
             "arms": ["FF", "UE", "SO", "MIX(0.5)"]},
        ],
    }


def load_config(path: Path) -> dict:
    try:
        cfg = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read config {path}: {exc}") from exc
    validate_config(cfg)
    return cfg
