# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Export the published results for the M5 demo page (schema lab-demo-results 1.0.0).

Reads committed result files only (the six confirmatory analysis.json files, the two
exploratory 1e-10 analyses, the M4 exploratory confounder checks and the committed raw
EXP-002 records), plus the claims register, the experiment registry and the artifact
manifest. No solver is run and nothing is recomputed beyond selecting and formatting
stored values.

Every displayed string is produced by formatting the stored value with the rounding the
manuscript uses; ``tests/test_demo_export.py`` checks that every display string appears
verbatim in ``research/paper/manuscript.md`` and that the committed JSON equals a fresh
export. The output is deterministic (sorted keys, no timestamps).

Usage: .venv/bin/python scripts/export_demo_data.py [--check]
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"

SCHEMA = "lab-demo-results"
SCHEMA_VERSION = "1.0.0"

A = {f"EXP-00{i}": f"research/experiments/EXP-00{i}/analysis.json" for i in range(1, 7)}
X1 = "results/exploratory/X-EXP-001-TOL1E-10-20261125T011841Z-ae793d0f/exploratory_analysis.json"
X2 = "results/exploratory/X-EXP-002-TOL1E-10-20261125T011841Z-5acef701/exploratory_analysis.json"
X1_MANIFEST = "results/exploratory/X-EXP-001-TOL1E-10-20261125T011841Z-ae793d0f/run_manifest.json"
M4 = "results/exploratory/M4-confounder-checks.json"
RAW_002 = "results/raw/EXP-002/EXP-002-20261124T234533Z-fcb88932/results.json"
CLAIMS = "research/claims_register.csv"
REGISTRY = "research/experiment_registry.csv"
MANIFEST = "research/publication/artifact_manifest.json"
LIMITATIONS = "research/limitations.md"

RUN_MANIFESTS = {
    "EXP-001": "results/raw/EXP-001/EXP-001-20261124T234532Z-846e8c0f/run_manifest.json",
    "EXP-002": "results/raw/EXP-002/EXP-002-20261124T234533Z-fcb88932/run_manifest.json",
    "EXP-003": "results/raw/EXP-003/EXP-003-20261124T234531Z-6cbcaa47/run_manifest.json",
    "EXP-004": "results/raw/EXP-004/EXP-004-20261125T002235Z-7a7c2692/run_manifest.json",
    "EXP-005": "results/raw/EXP-005/EXP-005-20261124T234554Z-4051f409/run_manifest.json",
    "EXP-006": "results/raw/EXP-006/EXP-006-20261124T234536Z-9a9669c8/run_manifest.json",
}

SOURCES = [*A.values(), *RUN_MANIFESTS.values(), X1, X2, X1_MANIFEST, M4, RAW_002, CLAIMS, REGISTRY, MANIFEST, LIMITATIONS]


class ExportError(RuntimeError):
    """A committed file does not contain what the export expects."""


# formatting ---------------------------------------------------------------------------


def fixed(v: float, n: int) -> str:
    return f"{v:.{n}f}"


def sci(v: float, n: int) -> str:
    """Scientific notation as the manuscript prints it: 6.19e-5, not 6.19e-05."""
    mant, exp = f"{v:.{n}e}".split("e")
    return f"{mant}e{int(exp)}"


def interval(lo: float, hi: float, n: int) -> str:
    return f"[{fixed(lo, n)}, {fixed(hi, n)}]"


def est(label, value, display, unit="", ci=None, ci_display=None, level=0.95, note=None):
    if ci is not None and ci_display is None:
        raise ExportError(f"{label}: interval without display text")
    return {
        "label": label,
        "estimate": float(value),
        "ci_low": None if ci is None else float(ci[0]),
        "ci_high": None if ci is None else float(ci[1]),
        "ci_level": None if ci is None else level,
        "unit": unit,
        "display": display,
        "interval_display": ci_display,
        "interval_note": note,
    }


def median_est(label, stats: dict, n: int, unit="dimensionless") -> dict:
    return est(label, stats["median"], fixed(stats["median"], n), unit, stats["ci95"], interval(*stats["ci95"], n))


# inputs -------------------------------------------------------------------------------


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def claims_by_evidence() -> dict[str, list[str]]:
    rows = list(csv.DictReader((ROOT / CLAIMS).open(newline="")))
    out: dict[str, list[str]] = {}
    for r in rows:
        ev = r["evidence_path_or_source"]
        keys = []
        for e in A:
            if f"experiments/{e}/" in ev:
                keys.append(e)
        if "EXP-00*" in ev:
            keys.extend(A.keys())
        if "X-EXP-001-TOL1E-10" in ev:
            keys.append("X-EXP-001-TOL1E-10")
        if "X-EXP-002-TOL1E-10" in ev:
            keys.append("X-EXP-002-TOL1E-10")
        if "M4-confounder-checks" in ev:
            keys.append("X-M4-CHECKS")
        for k in keys:
            out.setdefault(k, []).append(r["claim_id"])
    return {k: sorted(set(v)) for k, v in out.items()}


def registry_status() -> dict[str, str]:
    return {r["experiment_id"]: r["status"] for r in csv.DictReader((ROOT / REGISTRY).open(newline=""))}


def counts_text(sc: dict, n: int) -> str:
    return f"{sc['ok']} ok, {sc['nonconverged']} nonconverged, {sc['failed']} failed of {n} records"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ExportError(msg)


# experiments --------------------------------------------------------------------------


def exp001(d: dict) -> dict:
    ue_e = next(c for c in d["checks"] if c["arm"] == "UE" and c["with_link"])
    tstt = next(i for i in ue_e["items"] if i["quantity"] == "TSTT")
    others = max(i["abs_diff"] for c in d["checks"] if c is not ue_e for i in c["items"])
    require(d["verdict"].startswith("contradicted"), "EXP-001 verdict changed")
    return {
        "verdict": "Contradicted",
        "estimates": [
            est("TSTT, UE with link e (analytic value 552)", tstt["computed"], fixed(tstt["computed"], 8), "abstract time units"),
            est("Largest absolute difference from the analytic values (frozen tolerance 1e-6)", d["max_abs_diff"], sci(d["max_abs_diff"], 2), "abstract time units"),
            est("Largest difference, the other five arm and network combinations", others, sci(others, 1), "abstract time units"),
        ],
        "notes": [
            "Deterministic exact check: no interval applies.",
            "The published effect (83 without the link, 92 with it) is reproduced to the solver's tolerance; the frozen rule nevertheless gives a contradiction because the frozen config stops the solver at relative gap 1e-6.",
            f"Analysis verdict string: {d['verdict']}.",
        ],
    }


def exp002(d: dict) -> dict:
    b = d["boundaries"]
    lo, mid, up = b["lower_paradox_boundary"], b["middle_boundary_outer_paths_used"], b["upper_boundary_link_e_unused"]
    agree = sum(1 for p in d["points"] if p["sign_agrees"])
    require(d["verdict"].startswith("contradicted"), "EXP-002 verdict changed")
    return {
        "verdict": "Contradicted",
        "estimates": [
            est("Lower paradox boundary (analytic 80/31)", lo["computed"], repr(lo["computed"]), "demand units"),
            est("Upper boundary, link e unused (analytic 80/9)", up["computed"], fixed(up["computed"], 9), "demand units"),
            est("Middle boundary, outer paths used (analytic 40/11)", mid["computed"], fixed(mid["computed"], 9), "demand units"),
            est("Upper boundary difference from 80/9", up["abs_diff"], sci(up["abs_diff"], 2), "demand units"),
            est("Middle boundary difference from 40/11", mid["abs_diff"], sci(mid["abs_diff"], 2), "demand units"),
            est("Demand points where the sign of Delta agrees with the derivation", agree, f"{agree} of {d['n_points']}", "points"),
            est("Largest per-point UE time error", d["max_time_err"], sci(d["max_time_err"], 2), "abstract time units"),
        ],
        "notes": [
            "Deterministic sweep: no interval applies.",
            f"Analysis verdict string: {d['verdict']}.",
        ],
    }


def exp003(d: dict) -> dict:
    p = d["primary"]
    s = d["sensitivity"]
    cell = d["per_cell"]["grid6"]["2.0"]
    require(p["reject_H0"] is True and p["n"] == 100, "EXP-003 primary changed")
    return {
        "verdict": "H0 rejected",
        "estimates": [
            median_est("Median R(UE), 6 by 6 grids, rho = 2 (primary)", p, 5),
            est("One-sided 95 percent bootstrap lower bound of the primary median", p["lower_one_sided_95"], fixed(p["lower_one_sided_95"], 5), "dimensionless", note="this row is the uncertainty bound"),
            median_est("S1, solver tolerance RG 1e-4", s["S1-tol1e-4"], 5),
            median_est("S1, solver tolerance RG 1e-8", s["S1-tol1e-8"], 5),
            median_est("S2, linear-in-flow costs (beta = 1): below the margin", s["S2-beta1"], 5),
            median_est("S3, absolute demand calibration", s["S3-absolute"], 5),
            median_est("S1, Frank-Wolfe reference (7 of 100 converged; no decision)", s["S1-frank-wolfe-reference"], 5),
            median_est("Paired median R(FF) - R(UE), 6 by 6, rho = 2", cell["paired_R_FF_minus_UE"], 4),
            median_est("Paired median Gini of stretch, UE - SO, 6 by 6, rho = 2", cell["paired_gini_stretch_UE_minus_SO"], 5),
        ],
        "notes": [
            "Intervals are 95 percent percentile bootstrap intervals over the 100 instances (10,000 resamples).",
            "S2 does not give the same decision as the primary analysis: the result holds for quartic costs (beta = 4) only.",
            f"Analysis verdict string: {p['verdict']}.",
        ],
    }


def exp004(d: dict) -> dict:
    sc = d["per_scale"]["1.0"]
    require(sc["H1_supported"] is True, "EXP-004 verdict changed")
    ests = [median_est(f"Median R({arm}), capacity scale 1.0", sc["R"][arm], 5) for arm in ("MIX(0.25)", "MIX(0.5)", "MIX(0.75)")]
    for st in sc["steps"]:
        ests.append(est(f"Paired median step {st['pair']}", st["median"], fixed(st["median"], 5), "dimensionless", note="one-sided lower bound in the next row"))
        ests.append(est(f"One-sided 95 percent lower bound, step {st['pair']}", st["lower_one_sided_95"], fixed(st["lower_one_sided_95"], 5), "dimensionless", note="this row is the uncertainty bound"))
    for arm in ("MIX(0.25)", "MIX(0.75)"):
        r = sc["compliant_to_follower_time_ratio"][arm]["median"]
        ests.append(est(f"Median ratio of compliant to other travellers' mean trip time, {arm} (descriptive)", r, fixed(r, 4), "ratio"))
    return {
        "verdict": "H1 supported",
        "estimates": ests,
        "notes": [
            "Capacity scale 1.0 is confirmatory; scales 0.8 and 1.2 are descriptive (chart below).",
            "MIX(0) = UE and MIX(1) = SO by construction, so an overall decline is built in; only the step-wise decline is informative.",
            "The link-flow scaling sensitivity (protocol item 17) was not run, by owner decision.",
        ],
    }


def exp005(d: dict) -> dict:
    i4, i3, ic = d["incidence"]["1e-4"], d["incidence"]["1e-3"], d["incidence"]["confirmed_1e-8"]
    largest = max(p["max_rel_decrease"] for p in d["per_instance"])
    require(d["verdict"].startswith("H1 supported"), "EXP-005 verdict changed")
    return {
        "verdict": "H1 supported",
        "estimates": [
            est("Instances with a Braess link (threshold 1e-4 relative)", i4["incidence"], f"{i4['k']} of {i4['n']}", "share", i4["wilson95"], interval(*i4["wilson95"], 3)),
            est("Instances with a Braess link (threshold 1e-3 relative)", i3["incidence"], f"{i3['k']} of {i3['n']}", "share", i3["wilson95"], interval(*i3["wilson95"], 3)),
            est("Flagged links confirmed at RG 1e-8", ic["links_total"], str(ic["links_total"]), "links"),
            est("Largest relative decrease of TSTT_UE from one removal", largest, fixed(largest, 4), "relative"),
        ],
        "notes": [
            "Optional experiment. Intervals are Wilson 95 percent intervals for the incidence.",
            "Most effects are small; see the exploratory materiality check (J-0023) below.",
        ],
    }


def exp006(d: dict) -> dict:
    lv = d["levels"]["siouxfalls"]
    s1 = d["levels"]["S1-tol1e-8"]
    g = d["validation_gate"]
    require(g["pass"] is True and d["replication"]["replicates"] is True, "EXP-006 verdict changed")
    ests = [est("Engine gate: largest UE link-flow difference from the TNTP solution, relative (threshold 1e-3)", g["value"], sci(g["value"], 2), "relative")]
    for key, name in (("2.0", "rho = 2"), ("1.0", "rho = 1"), ("3.0", "rho = 3"), ("published", "published demand")):
        r = lv[key]["UE"]["R"]
        ests.append(est(f"R(UE), {name}", r, fixed(r, 5), "dimensionless"))
    ests.append(est("R(FF), rho = 2", lv["2.0"]["FF"]["R"], fixed(lv["2.0"]["FF"]["R"], 5), "dimensionless"))
    ests.append(est("R(UE), rho = 2, S1 at RG 1e-8", s1["2.0"]["UE"]["R"], fixed(s1["2.0"]["UE"]["R"], 5), "dimensionless"))
    return {
        "verdict": "Gate passed; direction replicates",
        "estimates": ests,
        "notes": [
            "One deterministic network: no interval applies, and one network supports no population claim.",
            "The maintainers describe Sioux Falls as \"not considered as a realistic one\". The network files are used locally and are not redistributed.",
        ],
    }


def x001(d: dict) -> dict:
    require(d["verdict"] == "reproduced", "X-EXP-001 verdict changed")
    return {
        "verdict": "Frozen analysis returns \"reproduced\" (exploratory; the frozen EXP-001 verdict stays Contradicted)",
        "estimates": [
            est("Largest absolute difference from the analytic values", d["max_abs_diff"], sci(d["max_abs_diff"], 2), "abstract time units"),
            est("Largest final relative gap", d["solver_rel_gap_max"], sci(d["solver_rel_gap_max"], 2), "dimensionless"),
        ],
        "notes": [
            "EXPLORATORY (J-0022): the frozen EXP-001 config rerun with only the solver tolerance changed to 1e-10, defined after the confirmatory results were seen. It is reported beside the frozen verdict and never replaces it (owner decision, 2026-11-25).",
        ],
    }


def x002(d: dict) -> dict:
    b = d["boundaries"]
    agree = sum(1 for p in d["points"] if p["sign_agrees"])
    require(d["verdict"] == "derivation confirmed", "X-EXP-002 verdict changed")
    return {
        "verdict": "Frozen analysis returns \"derivation confirmed\" (exploratory; the frozen EXP-002 verdict stays Contradicted)",
        "estimates": [
            est("Lower boundary difference from 80/31", b["lower_paradox_boundary"]["abs_diff"], sci(b["lower_paradox_boundary"]["abs_diff"], 1), "demand units"),
            est("Middle boundary difference from 40/11", b["middle_boundary_outer_paths_used"]["abs_diff"], sci(b["middle_boundary_outer_paths_used"]["abs_diff"], 1), "demand units"),
            est("Upper boundary difference from 80/9", b["upper_boundary_link_e_unused"]["abs_diff"], sci(b["upper_boundary_link_e_unused"]["abs_diff"], 1), "demand units"),
            est("Demand points where the sign of Delta agrees", agree, f"{agree} of {d['n_points']}", "points"),
            est("Largest per-point UE time error (not a criterion of the frozen rule)", d["max_time_err"], sci(d["max_time_err"], 2), "abstract time units"),
            est("Largest final relative gap", d["solver_rel_gap_max"], sci(d["solver_rel_gap_max"], 2), "dimensionless"),
        ],
        "notes": [
            "EXPLORATORY (J-0022): the frozen EXP-002 config rerun at relative gap 1e-10, analysed with the frozen analysis code unchanged. It does not change the frozen verdict.",
        ],
    }


def xm4(d: dict) -> dict:
    sh = d["share_instances_R_UE_above_delta"]
    m = d["exp005_materiality"]

    names = {"grid6 rho=2": "primary cell (6 by 6, rho = 2)", "S2-beta1 rho=2": "S2 cell (beta = 1)", "S3-absolute rho=1": "S3 cell (absolute calibration)"}

    def k_of(key):
        return est(f"Instances with R(UE) above 0.01, {names[key]}", sh[key]["k_above"] / sh[key]["n"], f"{sh[key]['k_above']} of {sh[key]['n']}", "instances")

    rho = d["primary_cell_spearman"]["R_UE_vs_flow_weighted_vc_UE"]
    return {
        "verdict": "Exploratory, no verdict (defined after the confirmatory results were seen)",
        "estimates": [
            k_of("grid6 rho=2"),
            k_of("S2-beta1 rho=2"),
            k_of("S3-absolute rho=1"),
            est("Spearman correlation of R(UE) with UE flow-weighted v/c, primary cell", rho, fixed(rho, 3), "dimensionless"),
            est("EXP-005 instances with a removal lowering TSTT_UE by more than 1e-2", m["k_instances_max_rel_decrease_above_1e-2"] / m["n_instances"], f"{m['k_instances_max_rel_decrease_above_1e-2']} of {m['n_instances']}", "instances"),
            est("EXP-005 median relative effect over the flagged Braess links", m["median_rel_effect_braess_links_1e-4"], fixed(m["median_rel_effect_braess_links_1e-4"], 4), "relative"),
        ],
        "notes": [
            "EXPLORATORY (J-0023): computed from committed tables without a solver. The correlation is not causal evidence.",
        ],
    }


# extensions ---------------------------------------------------------------------------


def grid_cells(d: dict) -> list[dict]:
    out = []
    for size, key in (("4x4", "grid4"), ("6x6", "grid6")):
        for rho in ("1.0", "2.0", "3.0"):
            c = d["per_cell"][key][rho]
            out.append({
                "size": size,
                "rho": float(rho),
                "n": c["n_instances"],
                "R_UE": median_est("Median R(UE)", c["R_UE"], 5),
                "R_FF": median_est("Median R(FF)", c["R_FF"], 4),
                "paired_FF_minus_UE": median_est("Paired median R(FF) - R(UE)", c["paired_R_FF_minus_UE"], 4),
            })
    return out


def sensitivity(d: dict) -> list[dict]:
    p, s = d["primary"], d["sensitivity"]
    rows = [("Primary (RG 1e-6)", p, True, "n/a")]
    for key, name in (("S1-tol1e-4", "S1, RG 1e-4"), ("S1-tol1e-8", "S1, RG 1e-8"), ("S2-beta1", "S2, beta = 1"),
                      ("S3-absolute", "S3, absolute calibration"), ("S1-frank-wolfe-reference", "S1, Frank-Wolfe reference (no decision)")):
        rows.append((name, s[key], s[key].get("same_decision_as_primary"), None))
    out = []
    for name, st, same, _ in rows:
        e = median_est(name, st, 5)
        e["n_used"] = st["n"]
        e["lower_one_sided_95"] = float(st["lower_one_sided_95"])
        e["lower_display"] = fixed(st["lower_one_sided_95"], 5)
        e["decision_role"] = "no decision" if "Frank-Wolfe" in name else ("primary" if name.startswith("Primary") else ("same decision" if same else "different decision"))
        out.append(e)
    return out


def compliance(d: dict) -> list[dict]:
    out = []
    for scale in ("0.8", "1.0", "1.2"):
        sc = d["per_scale"][scale]
        arms = []
        for arm, c in (("FF", None), ("MIX(0)", 0.0), ("MIX(0.25)", 0.25), ("MIX(0.5)", 0.5), ("MIX(0.75)", 0.75), ("MIX(1)", 1.0)):
            st = sc["R"][arm]
            if arm == "MIX(1)":
                require(st["median"] == 0.0 and st["max"] == 0.0, "MIX(1) identity changed")
                e = est("Median R(MIX(1)) = SO by construction", 0.0, "0", "dimensionless", note="identity by construction, no interval")
            else:
                e = median_est(f"Median R({arm})", st, 5)
            e["arm"] = arm
            e["c"] = c
            arms.append(e)
        out.append({"capacity_scale": float(scale), "confirmatory": scale == "1.0", "H1_supported": bool(sc["H1_supported"]), "arms": arms})
    return out


def braess_sweep(d002: dict, raw: dict) -> dict:
    links = ["a", "b", "c", "d", "e"]
    pts: dict[float, dict] = {}
    for r in raw["records"]:
        require(r["status"] == "ok", f"raw record {r['record_id']} not ok")
        dem = float(r["factors"]["demand"])
        net = "with_e" if r["factors"]["with_link"] else "without_e"
        p = pts.setdefault(dem, {"demand": dem, "cell": r["cell"], "with_e": {}, "without_e": {}})
        p[net][r["arm"]] = {
            "tstt": float(r["metrics"]["tstt"]),
            "mean_trip_time": float(r["metrics"]["mean_trip_time"]),
            "link_flow": [float(v) for v in r["metrics"]["link_flow"]],
        }
    for p in pts.values():
        for net, n in (("with_e", 5), ("without_e", 4)):
            require(set(p[net]) == {"FF", "UE", "SO"}, "missing Braess arm")
            require(all(len(v["link_flow"]) == n for v in p[net].values()), "Braess link count")
    predicted = {float(p["demand"]): bool(p["predicted_paradox"]) for p in d002["points"]}
    points = []
    for dem in sorted(pts):
        p = pts[dem]
        p["predicted_paradox"] = predicted[dem]
        points.append(p)
    return {
        "experiment_id": "EXP-002",
        "run_id": raw["run_id"],
        "label": "measured (confirmatory run, committed raw records)",
        "links": links,
        "link_ends": [["s", "A"], ["s", "B"], ["A", "t"], ["B", "t"], ["A", "B"]],
        "cost_A": [0.0, 50.0, 50.0, 0.0, 10.0],
        "cost_B": [10.0, 1.0, 1.0, 10.0, 1.0],
        "paradox_interval": {"low": 80 / 31, "high": 80 / 9, "display": "(80/31, 80/9)"},
        "points": points,
    }


STATUS_LABEL = (
    "Preregistered simulation study. Protocol v1.0 frozen by the owner on 2026-11-24; all six confirmatory "
    "experiments complete; manuscript draft, not peer-reviewed; the owner's full-text review is pending (M6)."
)
QUESTION = (
    "Can individually optimal routing worsen collective travel time? FLOW measures the gap between "
    "user-equilibrium and system-optimal total travel time on a Braess network, seeded synthetic grids and one "
    "test network (Sioux Falls). It is not a reconstruction of any navigation product and makes no prediction "
    "for any real city."
)
TITLES = {
    "EXP-001": "Analytic Braess example (exact check)",
    "EXP-002": "Braess demand sweep (exact check)",
    "EXP-003": "Grid collective excess (primary)",
    "EXP-004": "Compliance and capacity sweep",
    "EXP-005": "Single-link removal scan (optional)",
    "EXP-006": "Real-network second test (TNTP Sioux Falls)",
    "X-EXP-001-TOL1E-10": "EXP-001 rerun at relative gap 1e-10 (exploratory)",
    "X-EXP-002-TOL1E-10": "EXP-002 rerun at relative gap 1e-10 (exploratory)",
    "X-M4-CHECKS": "Confounder and materiality checks (exploratory)",
}
REPORTS = {
    **{e: f"research/experiments/{e}/report.md" for e in A},
    "X-EXP-001-TOL1E-10": "research/paper/manuscript.md section 5.2 (journal J-0022)",
    "X-EXP-002-TOL1E-10": "research/paper/manuscript.md section 5.2 (journal J-0022)",
    "X-M4-CHECKS": "research/paper/manuscript.md sections 6.1 to 6.3 (journal J-0023)",
}
ASSUMPTIONS = [
    ("BPR cost curve", "t(x) = t0 (1 + 0.15 (x / c)^4) on grid links; the conventional values, also the values the Sioux Falls file assumes", "protocol section 2; limitation 4"),
    ("Practical margin delta", "0.01 relative excess, a convention fixed by the study before any run, not an externally grounded threshold", "protocol; limitation 15"),
    ("Demand level rho", "multiple of the total demand at which free-flow loading first brings a link to capacity", "manuscript section 3"),
    ("Grid family grid-v1", "n by n lattice, t0 uniform on [1, 3] minutes, capacity uniform on [600, 1800] veh/h, 12 OD pairs with Dirichlet weights", "manuscript section 4.2"),
    ("Behaviour", "static deterministic assignment with perfect information; synthetic travellers are not people", "limitations 2 and 3"),
    ("Solver of record", "path-based gradient projection, stopping at relative gap 1e-6 or 20,000 sweeps", "manuscript section 4.3"),
    ("Partial compliance MIX(c)", "a share c follows the scaled system-optimal path flows; the rest reaches equilibrium around them", "manuscript section 3; limitation 7"),
]
LIMITATIONS_TEXT = [
    "Synthetic networks: the primary result rests on seeded lattices with 12 OD pairs; Sioux Falls is one small test network. Nothing transfers to real cities or navigation products.",
    "Static deterministic assignment: no time dynamics, queues, departure-time choice, signals or stochastic route choice.",
    "Cost curvature: with linear-in-flow costs (S2) the excess falls below the margin; the result holds for quartic costs only.",
    "Light demand: at rho = 1 the median excess is below the margin at both grid sizes.",
    "One solver: the Frank-Wolfe reference failed to converge on most instances, so there is no independent solver check on grids.",
    "Exact checks: EXP-001 and EXP-002 are contradicted under their frozen rule; the 1e-10 evidence is exploratory and post hoc.",
    "Pre-freeze exposure: exploratory values of the primary-cell analogue were seen before the freeze (disclosure C4).",
    "Shared instances: EXP-004 and EXP-005 reuse EXP-003 instances and are not independent replications.",
    "The margin delta = 0.01 is a study convention; the OD count and distance rule were never varied.",
]


def build() -> dict:
    data = {k: load(v) for k, v in A.items()}
    x1, x2, m4, raw = load(X1), load(X2), load(M4), load(RAW_002)
    claims = claims_by_evidence()
    reg = registry_status()
    revs = set()
    for e, d in data.items():
        require(d["source_run"]["path"] + "/run_manifest.json" == RUN_MANIFESTS[e], f"{e} source run changed")
        revs.add(load(RUN_MANIFESTS[e])["git"]["revision"])
    require(len(revs) == 1, f"confirmatory runs at several revisions: {revs}")
    revision = revs.pop()
    x_rev = load(X1_MANIFEST)["git"]["revision"]

    builders = {"EXP-001": exp001, "EXP-002": exp002, "EXP-003": exp003, "EXP-004": exp004, "EXP-005": exp005, "EXP-006": exp006}
    experiments = []
    for e, fn in builders.items():
        d = data[e]
        part = fn(d)
        experiments.append({
            "id": e,
            "title": TITLES[e],
            "status": f"confirmatory; complete ({counts_text(d['status_counts'], d['n_records'])})",
            "verdict": part["verdict"],
            "estimates": part["estimates"],
            "claim_ids": claims.get(e, []),
            "report_path": REPORTS[e],
            "notes": part["notes"] + [f"Registry status: {reg[e]}."],
            "label": "measured",
        })
    for e, fn, d in (("X-EXP-001-TOL1E-10", x001, x1), ("X-EXP-002-TOL1E-10", x002, x2), ("X-M4-CHECKS", xm4, m4)):
        part = fn(d)
        sc = d.get("status_counts")
        status = "exploratory; complete" + (f" ({counts_text(sc, d['n_records'])})" if sc else " (no solver run)")
        experiments.append({
            "id": e,
            "title": TITLES[e],
            "status": status,
            "verdict": part["verdict"],
            "estimates": part["estimates"],
            "claim_ids": claims.get(e, []),
            "report_path": REPORTS[e],
            "notes": part["notes"],
            "label": "exploratory",
        })
    default_note = {
        "EXP-001": "deterministic, no interval",
        "EXP-002": "deterministic, no interval",
        "EXP-003": "no interval reported",
        "EXP-004": "descriptive, no interval reported",
        "EXP-005": "count or maximum, no interval",
        "EXP-006": "deterministic, no interval",
        "X-EXP-001-TOL1E-10": "deterministic, no interval",
        "X-EXP-002-TOL1E-10": "deterministic, no interval",
        "X-M4-CHECKS": "exploratory, no interval computed",
    }
    for x in experiments:
        require(len(x["claim_ids"]) > 0, f"{x['id']} has no claim in the register")
        for e in x["estimates"]:
            if e["ci_low"] is None and e["interval_note"] is None:
                e["interval_note"] = default_note[x["id"]]
    manifest = load(MANIFEST)
    require(manifest.get("artifacts"), "artifact manifest has no artifacts")

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "project": "FLOW",
        "question": QUESTION,
        "status_label": STATUS_LABEL,
        "code_revision": revision,
        "exploratory_code_revision": x_rev,
        "sources": [{"path": p, "sha256": sha256(p)} for p in SOURCES],
        "experiments": experiments,
        "assumptions": [{"name": n, "value": v, "source": s} for n, v, s in ASSUMPTIONS],
        "limitations": LIMITATIONS_TEXT,
        "braess_sweep": braess_sweep(data["EXP-002"], raw),
        "grid_cells": grid_cells(data["EXP-003"]),
        "sensitivity": sensitivity(data["EXP-003"]),
        "compliance": compliance(data["EXP-004"]),
        "artifact_manifest_entries": len(manifest["artifacts"]),
    }


def render(obj: dict) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        same = OUT.exists() and OUT.read_text() == text
        print("export check:", "identical" if same else "DIFFERS")
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
