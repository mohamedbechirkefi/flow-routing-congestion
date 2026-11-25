# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Frozen analysis and figures for one confirmatory experiment, from its raw run directory.

Usage:
  .venv/bin/python scripts/analyse_exp.py EXP-003 results/raw/EXP-003/<run_id>
  .venv/bin/python scripts/analyse_exp.py EXP-004 results/raw/EXP-004/<run_id> --exp003 results/raw/EXP-003/<run_id>

Writes into research/experiments/<EXP>/: analysis.json (estimands, intervals,
verdicts), config.json and run_manifest.json (copies of the run's files),
metrics.csv (the run's per-record table) and figures/*.png. Nothing is computed
here that is not in flow.confirmatory (written before any confirmatory output).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flow import confirmatory as C  # noqa: E402
from flow.schema import clean_json, load_result  # noqa: E402


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


INK, ACCENT, GREY = "#33475b", "#b5452b", "#999999"


def fig_exp002(a: dict, d: Path) -> list[str]:
    plt = _plt()
    pts = [p for p in a["points"] if "time_with" in p and p["cell"] == "sweep"]
    xs = np.array([p["demand"] for p in pts])
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    grid = np.linspace(0.01, 12.2, 600)
    ax[0].plot(grid, [C.braess_ue_time(g, True) for g in grid], color=ACCENT, lw=1, label="analytic, with e")
    ax[0].plot(grid, [C.braess_ue_time(g, False) for g in grid], color=GREY, lw=1, label="analytic, without e")
    ax[0].scatter(xs, [p["time_with"] for p in pts], s=10, color=ACCENT, label="computed, with e")
    ax[0].scatter(xs, [p["time_without"] for p in pts], s=10, color=INK, marker="x", label="computed, without e")
    ax[0].set_xlabel("total demand d (abstract units)")
    ax[0].set_ylabel("UE path time (abstract units)")
    ax[0].legend(fontsize=7)
    ax[1].axvspan(C.B_LOW, C.B_HIGH, color="#f3d9d2", label="predicted paradox interval (80/31, 80/9)")
    ax[1].scatter(xs, [p["delta_tstt"] for p in pts], s=10, color=INK, label="computed Delta(d)")
    ax[1].axhline(0, color=GREY, lw=0.6)
    ax[1].set_xlabel("total demand d")
    ax[1].set_ylabel("TSTT_UE(with e) - TSTT_UE(without e)")
    ax[1].legend(fontsize=7)
    fig.suptitle("EXP-002 (confirmatory): Braess demand sweep, deterministic (no intervals)", fontsize=9)
    fig.tight_layout()
    fig.savefig(d / "exp002_sweep.png", dpi=150)
    plt.close(fig)
    return ["exp002_sweep.png"]


def _ci_plot(ax, labels, summaries, title, ref=None):
    for i, s in enumerate(summaries):
        if s["median"] is None:
            continue
        lo, hi = s["ci95"]
        ax.errorbar([i], [s["median"]], yerr=[[s["median"] - lo], [hi - s["median"]]], fmt="o", color=INK, capsize=3)
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right", fontsize=7)
    if ref is not None:
        ax.axhline(ref, color=ACCENT, lw=0.8, ls="--")
    ax.axhline(0, color=GREY, lw=0.5)
    ax.set_title(title, fontsize=8)


def fig_exp003(a: dict, doc: dict, d: Path) -> list[str]:
    plt = _plt()
    out = []
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=False)
    for ax, cell in zip(axes, ("grid4", "grid6")):
        k = 0
        labels = []
        for rho in ("1.0", "2.0", "3.0"):
            for arm in ("UE", "FF"):
                vals = sorted(C.arm_values(C.usable_R([r for r in doc["records"] if r["cell"] == cell and str(r["factors"]["rho"]) == rho]), arm).values())
                s = a["per_cell"][cell][rho][f"R_{arm}"]
                jitter = np.linspace(-0.15, 0.15, len(vals)) if vals else []
                ax.scatter(np.full(len(vals), k) + jitter, vals, s=4, color=GREY, alpha=0.6)
                if s["median"] is not None:
                    ax.errorbar([k], [s["median"]], yerr=[[s["median"] - s["ci95"][0]], [s["ci95"][1] - s["median"]]],
                                fmt="o", color=ACCENT, capsize=3, ms=4)
                labels.append(f"{arm} rho={rho[0]}")
                k += 1
        ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right", fontsize=7)
        ax.set_yscale("symlog", linthresh=1e-3)
        ax.axhline(C.DELTA, color=ACCENT, lw=0.8, ls="--")
        ax.set_ylabel("R = TSTT/TSTT(SO) - 1 (dimensionless)")
        ax.set_title(f"{cell}: per-instance R (grey), median and 95% bootstrap CI (red)", fontsize=8)
    fig.tight_layout()
    fig.savefig(d / "exp003_R_by_cell.png", dpi=150)
    plt.close(fig)
    out.append("exp003_R_by_cell.png")
    fig, ax = plt.subplots(figsize=(6, 3.4))
    labels = ["primary (GP 1e-6)"]
    sums = [a["primary"]]
    for c, s in a["sensitivity"].items():
        labels.append(c)
        sums.append(s)
    _ci_plot(ax, labels, sums, "EXP-003: median R(UE), 6x6 rho=2, 95% bootstrap CI\n(FW reference: converged instances only); dashed: delta = 0.01", ref=C.DELTA)
    ax.set_ylabel("median R(UE)")
    fig.tight_layout()
    fig.savefig(d / "exp003_sensitivity.png", dpi=150)
    plt.close(fig)
    out.append("exp003_sensitivity.png")
    return out


def fig_exp004(a: dict, d: Path) -> list[str]:
    plt = _plt()
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    cs = [0, 0.25, 0.5, 0.75, 1]
    for off, (scale, e) in zip((-0.02, 0, 0.02), sorted(a["per_scale"].items())):
        med = [e["R"][f"MIX({c:g})"]["median"] for c in cs]
        lo = [e["R"][f"MIX({c:g})"]["ci95"][0] for c in cs]
        hi = [e["R"][f"MIX({c:g})"]["ci95"][1] for c in cs]
        x = np.array(cs) + off
        ax[0].errorbar(x, med, yerr=[np.array(med) - lo, np.array(hi) - med], fmt="o-", capsize=3, ms=3,
                       label=f"capacity scale {scale}")
    ax[0].set_xlabel("compliance c")
    ax[0].set_ylabel("median R(MIX(c))")
    ax[0].legend(fontsize=7)
    ax[0].set_title("Median R with 95% bootstrap CI (n = 100 instances)", fontsize=8)
    e = a["per_scale"]["1.0"]
    _ci_plot(ax[1], [s["pair"] for s in e["steps"]], e["steps"], "Capacity 1.0: paired median differences, 95% CI")
    fig.tight_layout()
    fig.savefig(d / "exp004_compliance.png", dpi=150)
    plt.close(fig)
    return ["exp004_compliance.png"]


def fig_exp005(a: dict, d: Path) -> list[str]:
    plt = _plt()
    usable = [p for p in a["per_instance"] if p["usable"]]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    counts = [len(p["braess_links_1e-4"]) for p in usable]
    ax[0].hist(counts, bins=np.arange(-0.5, max(counts + [1]) + 1.5, 1), color=INK)
    ax[0].set_xlabel("Braess links per instance (threshold 1e-4)")
    ax[0].set_ylabel("instances")
    eff = [v for p in usable for v in p["effects_1e-4"].values()]
    if eff:
        ax[1].hist(np.log10(eff), bins=20, color=INK)
    ax[1].axvline(-4, color=ACCENT, ls="--", lw=0.8)
    ax[1].axvline(-3, color=GREY, ls="--", lw=0.8)
    ax[1].set_xlabel("log10 relative decrease of TSTT_UE after removal")
    ax[1].set_ylabel("links")
    inc = a["incidence"]["1e-4"]
    fig.suptitle(f"EXP-005 (confirmatory, optional): incidence {inc['k']}/{inc['n']}, Wilson 95% "
                 f"[{inc['wilson95'][0]:.3f}, {inc['wilson95'][1]:.3f}]", fontsize=9)
    fig.tight_layout()
    fig.savefig(d / "exp005_removals.png", dpi=150)
    plt.close(fig)
    return ["exp005_removals.png"]


def fig_exp006(a: dict, d: Path) -> list[str]:
    plt = _plt()
    lv = a["levels"]["siouxfalls"]
    order = sorted(lv, key=lambda k: lv[k]["rho"])
    fig, ax = plt.subplots(figsize=(6, 3.2))
    x = np.arange(len(order))
    for off, arm, col in ((-0.18, "UE", ACCENT), (0.18, "FF", INK)):
        ax.bar(x + off, [lv[k][arm]["R"] or 0 for k in order], width=0.34, color=col, label=arm)
    ax.set_xticks(x, [f"{k}\n(rho={lv[k]['rho']:.2f})" for k in order], fontsize=7)
    ax.set_yscale("symlog", linthresh=1e-3)
    ax.axhline(C.DELTA, color=GREY, ls="--", lw=0.8)
    ax.set_ylabel("R (dimensionless)")
    ax.set_title("EXP-006: Sioux Falls, R by demand level (deterministic, one network, no interval)", fontsize=8)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(d / "exp006_R.png", dpi=150)
    plt.close(fig)
    return ["exp006_R.png"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exp")
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--exp003", type=Path, default=None)
    args = ap.parse_args(argv)
    run = args.run_dir.resolve()
    doc = load_result(run / "results.json")
    if doc["experiment_id"] != args.exp or doc["label"] != "confirmatory":
        raise SystemExit("run does not belong to this confirmatory experiment")
    dest = ROOT / "research" / "experiments" / args.exp
    figs = dest / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    if args.exp == "EXP-001":
        a, f = C.analyse_exp001(doc), []
    elif args.exp == "EXP-002":
        a = C.analyse_exp002(doc)
        f = fig_exp002(a, figs)
    elif args.exp == "EXP-003":
        a = C.analyse_exp003(doc)
        f = fig_exp003(a, doc, figs)
    elif args.exp == "EXP-004":
        e3 = load_result(args.exp003.resolve() / "results.json") if args.exp003 else None
        a = C.analyse_exp004(doc, e3)
        f = fig_exp004(a, figs)
    elif args.exp == "EXP-005":
        skipped = json.loads((run / "skipped_removals.json").read_text())
        a = C.analyse_exp005(doc, skipped)
        f = fig_exp005(a, figs)
    elif args.exp == "EXP-006":
        a = C.analyse_exp006(doc)
        f = fig_exp006(a, figs)
    else:
        raise SystemExit(f"unknown experiment {args.exp}")
    a["source_run"] = {"run_id": doc["run_id"], "path": str(run.relative_to(ROOT)), "config_hash": doc["config_hash"],
                       "results_sha256": hashlib.sha256((run / "results.json").read_bytes()).hexdigest()}
    a["figures"] = f
    (dest / "analysis.json").write_text(json.dumps(clean_json(a), indent=1, sort_keys=True) + "\n")
    for name in ("config.json", "run_manifest.json", "metrics.csv"):
        shutil.copyfile(run / name, dest / name)
    print(json.dumps({k: a[k] for k in a if k in ("verdict", "primary", "validation_gate", "replication", "incidence", "boundaries")}, indent=1, default=str)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
