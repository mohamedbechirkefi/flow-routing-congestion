# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Frozen analyses of the confirmatory experiments (protocol v1.0, sections 4, 6, 7, 15).

Written and tested before any confirmatory output existed (M3, 2026-11-25).
Each ``analyse_exp00N`` takes the validated ``results.json`` document(s) of a run
and returns a JSON-serialisable dict with the frozen estimand, interval and
verdict. Interpretation choices that the protocol leaves implicit are fixed
here, before any data, and recorded in decision D-012:

* EXP-001: "differing by more than 1e-6" is read as an absolute difference.
* EXP-002: computed boundaries come from least-squares lines through the sweep
  points strictly inside each predicted regime; a sweep point counts as a
  paradox point when Delta(d) > 1e-6 x TSTT_UE(without e).
* EXP-003 and EXP-004: "95 percent bootstrap lower bound" is the one-sided
  bound (5th percentile of the bootstrap medians), as in the primary rule; the
  two-sided 2.5th percentile is reported alongside.
* EXP-004: the confirmatory monotonicity test uses capacity scale 1.0; the
  other scales are descriptive. No multiplicity correction: H1 needs every
  consecutive step to pass (intersection-union test).
* EXP-005: incidence uses the scan tolerance (item 5); the 1e-8 re-solve of
  flagged links (item 16) is reported as a confirmation count.
"""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from .analysis import BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED, bootstrap_median

DELTA = 0.01
LEVEL = 0.95
EXACT_TOL = 1e-6


# ---------------------------------------------------------------- helpers

def instance_id(rec: dict) -> str:
    """Record id without the trailing arm: identifies the instance (and level) of a record."""
    return rec["record_id"].rsplit("/", 1)[0]


def interval_summary(values, resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED) -> dict:
    """Median with the one-sided 95 percent lower bound and the two-sided 95 percent interval."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return {"n": 0, "median": None, "mean": None, "lower_one_sided_95": None, "ci95": [None, None],
                "q25": None, "q75": None, "min": None, "max": None, "sd": None}
    boots = bootstrap_median(v, resamples=resamples, seed=seed)
    return {
        "n": int(v.size),
        "median": float(np.median(v)),
        "mean": float(np.mean(v)),
        "sd": float(np.std(v, ddof=1)) if v.size > 1 else None,
        "q25": float(np.quantile(v, 0.25)),
        "q75": float(np.quantile(v, 0.75)),
        "min": float(np.min(v)),
        "max": float(np.max(v)),
        "lower_one_sided_95": float(np.quantile(boots, 1 - LEVEL)),
        "ci95": [float(np.quantile(boots, (1 - LEVEL) / 2)), float(np.quantile(boots, 1 - (1 - LEVEL) / 2))],
    }


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def status_counts(recs: list[dict]) -> dict:
    return {s: sum(r["status"] == s for r in recs) for s in ("ok", "nonconverged", "failed")}


def _by(recs, *keys):
    out = defaultdict(list)
    for r in recs:
        out[tuple(r["factors"].get(k) if k != "arm" and k != "cell" else r[k] for k in keys)].append(r)
    return out


def usable_R(recs: list[dict]) -> dict:
    """{(cell, instance) -> {arm: record}} restricted to records whose own solve and SO are ok."""
    inst = defaultdict(dict)
    for r in recs:
        inst[instance_id(r)][r["arm"]] = r
    return inst


def arm_values(inst_map: dict, arm: str, metric: str = "R", need_so: bool = True) -> dict:
    """{instance -> metric} for instances where the arm (and SO, if needed) converged."""
    out = {}
    for key, arms in inst_map.items():
        r = arms.get(arm)
        if r is None or r["status"] != "ok" or not r["metrics"] or r["metrics"].get(metric) is None:
            continue
        if need_so and (arms.get("SO") is None or arms["SO"]["status"] != "ok"):
            continue
        out[key] = float(r["metrics"][metric])
    return out


def paired(a: dict, b: dict) -> list[float]:
    keys = sorted(set(a) & set(b))
    return [a[k] - b[k] for k in keys]


def decision_rule(values) -> dict:
    """Primary rule (protocol section 4): reject H0 if the one-sided 95% lower bound exceeds delta."""
    s = interval_summary(values)
    if s["n"] == 0:
        return {**s, "reject_H0": None, "negligible": None}
    s["reject_H0"] = bool(s["lower_one_sided_95"] > DELTA)
    s["negligible"] = bool(s["ci95"][1] < DELTA)
    return s


# ---------------------------------------------------------------- EXP-001

def braess_expected() -> dict:
    """Analytic values of EXP-001 item 5 (demand 6). Paths are node sequences s=0, A=1, B=2, t=3."""
    return {
        (False, "UE"): {"tstt": 498.0, "time": 83.0, "paths": {(0, 1, 3): 3.0, (0, 2, 3): 3.0}},
        (True, "UE"): {"tstt": 552.0, "time": 92.0, "paths": {(0, 1, 3): 2.0, (0, 2, 3): 2.0, (0, 1, 2, 3): 2.0}},
        (False, "SO"): {"tstt": 498.0, "paths": {(0, 1, 3): 3.0, (0, 2, 3): 3.0}},
        (True, "SO"): {"tstt": 498.0, "link_e": 0.0, "paths": {(0, 1, 3): 3.0, (0, 2, 3): 3.0}},
        (True, "FF"): {"tstt": 816.0, "time": 136.0, "paths": {(0, 1, 2, 3): 6.0}},
        (False, "FF"): {"tstt": 696.0, "time": 116.0, "paths": {(0, 1, 3): 6.0}},
    }


def _paths_of(rec: dict) -> dict:
    out = {}
    for item in rec["metrics"].get("path_flows", [[]])[0]:
        if item["flow"] > 0:
            out[tuple(item["path"])] = item["flow"]
    return out


def analyse_exp001(doc: dict) -> dict:
    exp = braess_expected()
    checks = []
    for r in doc["records"]:
        key = (bool(r["factors"]["with_link"]), r["arm"])
        want = exp[key]
        m = r["metrics"] or {}
        row = {"with_link": key[0], "arm": key[1], "status": r["status"], "iterations": r["solver"]["iterations"],
               "rel_gap": r["solver"]["rel_gap"], "items": []}
        if r["status"] != "ok":
            row["pass"] = False
            checks.append(row)
            continue

        def item(name, got, wanted):
            diff = abs(got - wanted)
            row["items"].append({"quantity": name, "computed": got, "analytic": wanted, "abs_diff": diff,
                                 "rel_diff": diff / abs(wanted) if wanted else None, "pass": diff <= EXACT_TOL})

        item("TSTT", m["tstt"], want["tstt"])
        if "time" in want:
            item("mean trip time", m["mean_trip_time"], want["time"])
            item("max path time", m["max_trip_time"], want["time"])
        if "link_e" in want:
            item("flow on link e", m["link_flow"][4], want["link_e"])
        got_paths = _paths_of(r)
        for p in sorted(set(want["paths"]) | set(got_paths)):
            item("path flow " + "-".join("sABt"[n] for n in p), got_paths.get(p, 0.0), want["paths"].get(p, 0.0))
        row["pass"] = all(i["pass"] for i in row["items"])
        checks.append(row)
    passed = all(c["pass"] for c in checks) and len(checks) == 6
    max_abs = max((i["abs_diff"] for c in checks for i in c["items"]), default=None)
    return {"experiment_id": "EXP-001", "tolerance_abs": EXACT_TOL, "n_records": len(doc["records"]),
            "status_counts": status_counts(doc["records"]), "checks": checks, "max_abs_diff": max_abs,
            "verdict": "reproduced" if passed else "contradicted (at least one value outside tolerance or not converged)"}


# ---------------------------------------------------------------- EXP-002

B_LOW, B_MID, B_HIGH = 80 / 31, 40 / 11, 80 / 9


def braess_ue_time(d: float, with_link: bool) -> float:
    if not with_link or d >= B_HIGH:
        return 5.5 * d + 50
    if d <= B_MID:
        return 21 * d + 10
    return (31 * d + 1010) / 13


def analyse_exp002(doc: dict) -> dict:
    ue = {}
    for r in doc["records"]:
        if r["arm"] == "UE":
            ue[(r["cell"], float(r["factors"]["demand"]), bool(r["factors"]["with_link"]))] = r
    points = []
    for (cell, d, wl), r in sorted(ue.items()):
        if not wl:
            continue
        r0 = ue.get((cell, d, False))
        ok = r["status"] == "ok" and r0 is not None and r0["status"] == "ok"
        row = {"cell": cell, "demand": d, "status_with": r["status"], "status_without": r0["status"] if r0 else None}
        if ok:
            t1, t0 = r["metrics"]["max_trip_time"], r0["metrics"]["max_trip_time"]
            delta = r["metrics"]["tstt"] - r0["metrics"]["tstt"]
            pred_delta = d * (braess_ue_time(d, True) - braess_ue_time(d, False))
            computed_paradox = delta > EXACT_TOL * r0["metrics"]["tstt"]
            predicted_paradox = B_LOW < d < B_HIGH
            pf = _paths_of(r)
            row.update(
                time_with=t1, time_without=t0, analytic_with=braess_ue_time(d, True), analytic_without=braess_ue_time(d, False),
                time_err_with=abs(t1 - braess_ue_time(d, True)), time_err_without=abs(t0 - braess_ue_time(d, False)),
                delta_tstt=delta, analytic_delta_tstt=pred_delta, computed_paradox=computed_paradox,
                predicted_paradox=predicted_paradox, sign_agrees=computed_paradox == predicted_paradox,
                flow_zigzag=pf.get((0, 1, 2, 3), 0.0), flow_outer=pf.get((0, 1, 3), 0.0),
            )
        points.append(row)
    good = [p for p in points if "time_with" in p]
    main = [p for p in good if p["cell"] == "sweep"]

    def fit(xs, ys):
        if len(xs) < 2:
            return None
        a, b = np.polyfit(np.asarray(xs), np.asarray(ys), 1)
        resid = float(np.max(np.abs(np.polyval([a, b], xs) - np.asarray(ys))))
        return float(a), float(b), resid

    low = [p for p in main if p["demand"] < B_MID]
    mid = [p for p in main if B_MID < p["demand"] < B_HIGH]
    f_with_low = fit([p["demand"] for p in low], [p["time_with"] for p in low])
    f_without = fit([p["demand"] for p in main], [p["time_without"] for p in main])
    f_g = fit([p["demand"] for p in mid], [p["flow_zigzag"] for p in mid])
    f_f = fit([p["demand"] for p in mid], [p["flow_outer"] for p in mid])
    bounds = {}
    if f_with_low and f_without and f_with_low[0] != f_without[0]:
        bounds["lower_paradox_boundary"] = (f_without[1] - f_with_low[1]) / (f_with_low[0] - f_without[0])
    if f_g and f_g[0] != 0:
        bounds["upper_boundary_link_e_unused"] = -f_g[1] / f_g[0]
    if f_f and f_f[0] != 0:
        bounds["middle_boundary_outer_paths_used"] = -f_f[1] / f_f[0]
    analytic = {"lower_paradox_boundary": B_LOW, "upper_boundary_link_e_unused": B_HIGH,
                "middle_boundary_outer_paths_used": B_MID}
    bcheck = {k: {"computed": bounds.get(k), "analytic": v,
                  "abs_diff": None if bounds.get(k) is None else abs(bounds[k] - v),
                  "pass": bounds.get(k) is not None and abs(bounds[k] - v) <= EXACT_TOL} for k, v in analytic.items()}
    signs_ok = all(p["sign_agrees"] for p in good)
    all_conv = len(good) == len(points)
    confirmed = all_conv and signs_ok and all(b["pass"] for b in bcheck.values())
    paradox_pts = sorted(p["demand"] for p in main if p["computed_paradox"])
    return {
        "experiment_id": "EXP-002", "tolerance_abs": EXACT_TOL, "n_records": len(doc["records"]),
        "status_counts": status_counts(doc["records"]), "n_points": len(points), "n_points_usable": len(good),
        "boundaries": bcheck,
        "fit_max_residuals": {"with_link_low_regime": f_with_low and f_with_low[2], "without_link": f_without and f_without[2],
                              "zigzag_flow_mid": f_g and f_g[2], "outer_flow_mid": f_f and f_f[2]},
        "sign_agreement_all_points": signs_ok,
        "max_time_err": max((max(p["time_err_with"], p["time_err_without"]) for p in good), default=None),
        "computed_paradox_demands_main_sweep": paradox_pts,
        "points": points,
        "verdict": "derivation confirmed" if confirmed else "contradicted or incomplete (see boundaries and sign agreement)",
    }


# ---------------------------------------------------------------- EXP-003

def analyse_exp003(doc: dict) -> dict:
    recs = doc["records"]
    out = {"experiment_id": "EXP-003", "n_records": len(recs), "status_counts": status_counts(recs),
           "delta": DELTA, "bootstrap": {"resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED}}
    cells = defaultdict(list)
    for r in recs:
        cells[r["cell"]].append(r)
    per_cell = {}
    for cell, crecs in cells.items():
        levels = _by(crecs, "rho")
        per_cell[cell] = {}
        for (rho,), lrecs in sorted(levels.items()):
            imap = usable_R(lrecs)
            arms = sorted({r["arm"] for r in lrecs})
            entry = {"n_instances": len(imap), "status_by_arm": {a: status_counts([r for r in lrecs if r["arm"] == a]) for a in arms}}
            for a in arms:
                if a != "SO":
                    entry[f"R_{a}"] = interval_summary(list(arm_values(imap, a).values()))
            if "FF" in arms and "UE" in arms:
                entry["paired_R_FF_minus_UE"] = interval_summary(paired(arm_values(imap, "FF"), arm_values(imap, "UE")))
                for metric in ("gini_stretch", "p95_trip_time"):
                    vals = {a: arm_values(imap, a, metric) for a in ("FF", "UE", "SO")}
                    entry[f"paired_{metric}_UE_minus_SO"] = interval_summary(paired(vals["UE"], vals["SO"]))
                    entry[f"paired_{metric}_FF_minus_UE"] = interval_summary(paired(vals["FF"], vals["UE"]))
            entry["runtime_s"] = {a: float(np.mean([r["solver"]["runtime_s"] for r in lrecs if r["arm"] == a])) for a in arms}
            per_cell[cell][str(rho)] = entry
    out["per_cell"] = per_cell
    # primary
    prim = [r for r in cells.get("grid6", []) if r["factors"]["rho"] == 2.0]
    imap = usable_R(prim)
    n_inst = len(imap)
    bad = sum(1 for arms in imap.values()
              if any(arms.get(a) is None or arms[a]["status"] != "ok" for a in ("UE", "SO")))
    vals = list(arm_values(imap, "UE").values())
    rule = decision_rule(vals)
    failed = n_inst == 0 or bad / n_inst > 0.10
    out["primary"] = {
        "cell": "grid6, rho = 2, arm UE", "n_instances": n_inst, "n_excluded_nonconverged_or_failed": bad,
        "share_excluded": bad / n_inst if n_inst else None, "analysis_failed_10pct_rule": failed, **rule,
        "verdict": ("failed (more than 10 percent nonconverged)" if failed else
                    "H0 rejected: theta > 0.01" if rule["reject_H0"] else "H0 not rejected"),
    }
    # sensitivity
    sens = {}
    for cell in ("S1-tol1e-4", "S1-tol1e-8", "S2-beta1", "S1-frank-wolfe-reference", "S3-absolute"):
        if cell not in cells:
            continue
        crecs = cells[cell]
        im = usable_R(crecs)
        nb = sum(1 for arms in im.values() if any(arms.get(a) is None or arms[a]["status"] != "ok" for a in ("UE", "SO")))
        r = decision_rule(list(arm_values(im, "UE").values()))
        sens[cell] = {"n_instances": len(im), "n_excluded": nb, **r,
                      "same_decision_as_primary": None if r["reject_H0"] is None or rule["reject_H0"] is None
                      else r["reject_H0"] == rule["reject_H0"]}
        if cell.startswith("S1-tol"):
            pv = {k.split("/")[-1]: v for k, v in arm_values(imap, "UE").items()}
            sv = {k.split("/")[-1]: v for k, v in arm_values(im, "UE").items()}
            sens[cell]["paired_R_minus_primary"] = interval_summary(paired(sv, pv))
    if "S1-frank-wolfe-reference" in sens:
        sens["S1-frank-wolfe-reference"]["note"] = "differential reference, not used in any decision"
    out["sensitivity"] = sens
    robust_s1 = all(sens[c]["same_decision_as_primary"] for c in ("S1-tol1e-4", "S1-tol1e-8") if c in sens)
    out["s1_robust"] = robust_s1
    return out


# ---------------------------------------------------------------- EXP-004

def analyse_exp004(doc: dict, exp003: dict | None = None) -> dict:
    recs = doc["records"]
    cs = [0.0, 0.25, 0.5, 0.75, 1.0]
    out = {"experiment_id": "EXP-004", "n_records": len(recs), "status_counts": status_counts(recs), "per_scale": {}}
    for (scale,), srecs in sorted(_by(recs, "capacity_scale").items()):
        imap = usable_R(srecs)
        arms = [f"MIX({c:g})" for c in cs]
        e = {"n_instances": len(imap), "status_by_arm": {a: status_counts([r for r in srecs if r["arm"] == a]) for a in ["FF", "SO"] + arms}}
        vals = {a: arm_values(imap, a) for a in arms + ["FF"]}
        e["R"] = {a: interval_summary(list(vals[a].values())) for a in arms + ["FF"]}
        steps = []
        for a, b in zip(arms, arms[1:]):
            s = interval_summary(paired(vals[a], vals[b]))
            s["pair"] = f"{a} - {b}"
            s["passes"] = s["lower_one_sided_95"] is not None and s["lower_one_sided_95"] > 0
            s["nonmonotone_evidence"] = s["ci95"][1] is not None and s["ci95"][1] < 0
            steps.append(s)
        e["steps"] = steps
        e["H1_supported"] = all(s["passes"] for s in steps)
        ratio = {}
        for a in arms[1:-1]:
            rv = [r["metrics"]["compliant_to_follower_time_ratio"] for r in srecs
                  if r["arm"] == a and r["status"] == "ok" and r["metrics"].get("compliant_to_follower_time_ratio") is not None]
            ratio[a] = interval_summary(rv)
        e["compliant_to_follower_time_ratio"] = ratio
        mix1 = list(vals["MIX(1)"].values())
        e["identity_MIX1_max_abs_R"] = float(np.max(np.abs(mix1))) if mix1 else None
        out["per_scale"][str(scale)] = e
    conf = out["per_scale"].get("1.0")
    out["confirmatory_scale"] = 1.0
    out["verdict"] = ("H1 supported: median R decreases strictly at every consecutive compliance step"
                      if conf and conf["H1_supported"] else "H0 not rejected: at least one step has a lower bound at or below 0")
    if exp003 is not None:
        ue = {}
        for r in exp003["records"]:
            if r["cell"] == "grid6" and r["factors"]["rho"] == 2.0 and r["arm"] == "UE" and r["status"] == "ok":
                ue[r["seed"]] = r["metrics"]["tstt"]
        m0 = {r["seed"]: r["metrics"]["tstt"] for r in recs
              if r["arm"] == "MIX(0)" and r["factors"]["capacity_scale"] == 1.0 and r["status"] == "ok"}
        common = sorted(set(ue) & set(m0))
        out["identity_MIX0_vs_EXP003_UE"] = {
            "n": len(common),
            "max_rel_tstt_diff": float(max(abs(m0[s] / ue[s] - 1) for s in common)) if common else None,
        }
    return out


# ---------------------------------------------------------------- EXP-005

def analyse_exp005(doc: dict, skipped: list | None = None) -> dict:
    recs = doc["records"]
    by_inst = defaultdict(lambda: {"scan": {}, "recheck": {}})
    for r in recs:
        f = r["factors"]
        by_inst[r["seed"]][f["phase"]][f["removed_link"]] = r
    out = {"experiment_id": "EXP-005", "n_records": len(recs), "status_counts": status_counts(recs),
           "n_skipped_disconnecting": len(skipped or [])}
    per = []
    for seed, ph in sorted(by_inst.items()):
        full = ph["scan"].get(None)
        row = {"seed": seed, "full_status": full["status"] if full else None, "n_removals": len(ph["scan"]) - 1,
               "n_removals_nonconverged": sum(r["status"] != "ok" for k, r in ph["scan"].items() if k is not None)}
        if full is None or full["status"] != "ok":
            row["usable"] = False
            per.append(row)
            continue
        base = full["metrics"]["tstt"]
        eff = {k: (base - r["metrics"]["tstt"]) / base for k, r in ph["scan"].items() if k is not None and r["status"] == "ok"}
        row["usable"] = True
        row["max_rel_decrease"] = max(eff.values()) if eff else None
        for thr, tag in ((1e-4, "1e-4"), (1e-3, "1e-3")):
            row[f"braess_links_{tag}"] = sorted(k for k, v in eff.items() if v > thr)
        rc_full = ph["recheck"].get(None)
        confirmed = []
        if rc_full is not None and rc_full["status"] == "ok":
            b8 = rc_full["metrics"]["tstt"]
            for k in row["braess_links_1e-4"]:
                rr = ph["recheck"].get(k)
                if rr is not None and rr["status"] == "ok" and (b8 - rr["metrics"]["tstt"]) / b8 > 1e-4:
                    confirmed.append(k)
        row["braess_links_confirmed_1e-8"] = confirmed
        row["effects_1e-4"] = {str(k): eff[k] for k in row["braess_links_1e-4"]}
        per.append(row)
    usable = [p for p in per if p["usable"]]
    n = len(usable)
    res = {}
    for tag in ("1e-4", "1e-3", "confirmed_1e-8"):
        key = f"braess_links_{tag}"
        k = sum(1 for p in usable if p[key])
        lo, hi = wilson_interval(k, n)
        res[tag] = {"k": k, "n": n, "incidence": k / n if n else None, "wilson95": [lo, hi],
                    "links_per_instance_median": float(np.median([len(p[key]) for p in usable])) if usable else None,
                    "links_total": int(sum(len(p[key]) for p in usable))}
    out["incidence"] = res
    out["n_instances"] = len(per)
    out["n_usable_instances"] = n
    out["per_instance"] = per
    out["primary_threshold"] = "1e-4"
    k = res["1e-4"]["k"]
    out["verdict"] = ("H1 supported: incidence > 0 (at least one instance with a Braess link)" if k > 0
                      else "contradiction: no Braess link in any instance")
    out["recheck_agrees"] = (res["1e-4"]["k"] > 0) == (res["confirmed_1e-8"]["k"] > 0)
    return out


# ---------------------------------------------------------------- EXP-006

def analyse_exp006(doc: dict) -> dict:
    recs = doc["records"]
    out = {"experiment_id": "EXP-006", "n_records": len(recs), "status_counts": status_counts(recs), "levels": {}}
    for cell in sorted({r["cell"] for r in recs}):
        crecs = [r for r in recs if r["cell"] == cell]
        out["levels"][cell] = {}
        for (lv,), lrecs in _by(crecs, "demand_level").items():
            by = {r["arm"]: r for r in lrecs}
            so_ok = by.get("SO") is not None and by["SO"]["status"] == "ok"
            e = {"rho": lrecs[0]["factors"]["rho"], "total_demand": lrecs[0]["factors"]["total_demand"]}
            for a, r in by.items():
                m = r["metrics"] or {}
                e[a] = {"status": r["status"], "iterations": r["solver"]["iterations"], "rel_gap": r["solver"]["rel_gap"],
                        "tstt": m.get("tstt"), "R": m.get("R") if (so_ok and r["status"] == "ok") else None,
                        "mean_trip_time": m.get("mean_trip_time"), "p95_trip_time": m.get("p95_trip_time"),
                        "gini_stretch": m.get("gini_stretch"), "flow_weighted_vc": m.get("flow_weighted_vc"),
                        "ref_flow_max_abs_diff_rel": m.get("ref_flow_max_abs_diff_rel"), "runtime_s": r["solver"]["runtime_s"]}
            out["levels"][cell][str(lv)] = e
    main = out["levels"].get("siouxfalls", {})
    pub = main.get("published", {}).get("UE", {})
    gate_val = pub.get("ref_flow_max_abs_diff_rel")
    gate = gate_val is not None and pub.get("status") == "ok" and gate_val <= 1e-3
    out["validation_gate"] = {"value": gate_val, "threshold": 1e-3, "pass": gate}
    r2 = main.get("2.0", {})
    rue = r2.get("UE", {}).get("R")
    out["replication"] = {"R_UE_rho2": rue, "replicates": None if rue is None else rue > DELTA}
    if not gate:
        out["verdict"] = "failed: validation gate not met (not reinterpreted)"
    elif rue is None:
        out["verdict"] = "inconclusive: UE or SO at rho = 2 not converged"
    else:
        out["verdict"] = "direction replicates: R(UE) > 0.01 at rho = 2" if rue > DELTA else "contradiction: R(UE) <= 0.01 at rho = 2"
    return out
