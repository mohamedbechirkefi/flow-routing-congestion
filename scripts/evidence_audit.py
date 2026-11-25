# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Evidence audit (master prompt 11.5): raw-output cross-checks and a number trace.

Part A, raw cross-checks (no solver is run):
  A1  SHA-256 of every file listed in results/M3-raw-manifest.json that is present locally.
  A2  The committed research/experiments/EXP-*/metrics.csv equals the raw run's metrics.csv.
  A3  Record and status counts recounted from each raw metrics.csv equal analysis.json.
  A4  Key estimates recomputed from the raw per-record tables: EXP-003 primary median, mean,
      n; EXP-003 per-cell UE and FF medians; EXP-004 median R(MIX(c)) at each capacity scale;
      EXP-006 R(UE) at each level. Compared with analysis.json at 1e-12.

Part B, number trace: every decimal number (and every integer >= 101 not of the form of a
year) in the given Markdown/CSV documents is looked up among the numeric values stored in the
committed result files (analysis.json, run manifests, exploratory analyses, calibration
output, freeze record), allowing for display rounding at the shown precision and for
percent display. Numbers that only appear in protocol or config text are traced to those
files. Anything left is listed as UNTRACED for manual classification.

Part C, row-by-row semantic check: rows of manuscript Tables 2, 3, 4, 5 and supplementary
Tables S3 and S4 are rebuilt from the named analysis.json fields and must appear verbatim.

Usage: .venv/bin/python scripts/evidence_audit.py [doc ...]
Writes research/publication/evidence_audit.json.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "publication" / "evidence_audit.json"

DEFAULT_DOCS = [
    "research/paper/manuscript.md",
    "research/paper/supplementary.md",
    "research/claims_register.csv",
    *[f"research/experiments/EXP-00{i}/report.md" for i in range(1, 7)],
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_json(p: Path):
    return json.loads(p.read_text())


def numeric_leaves(obj, out: list):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        if math.isfinite(obj):
            out.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            numeric_leaves(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            numeric_leaves(v, out)


NUM = re.compile(r"(?<![\w.#/-])-?\d+(?:,\d{3})*(?:\.\d+)?(?:e-?\d+)?(?![\w])")


def text_numbers(text: str) -> list[str]:
    return NUM.findall(text)


def matches(token: str, values: list[float]) -> bool:
    s = token.replace(",", "")
    x = float(s)
    if "e" in s:
        mant = s.split("e")[0]
        dec = len(mant.split(".")[1]) if "." in mant else 0
        exp = int(s.split("e")[1])
        tol = 0.5 * 10 ** (exp - dec) * 1.000001
    else:
        dec = len(s.split(".")[1]) if "." in s else 0
        tol = 0.5 * 10 ** (-dec) * 1.000001
    for v in values:
        for cand in (v, 100 * v, abs(v)):
            if abs(cand - x) <= tol or abs(abs(cand) - abs(x)) <= tol:
                return True
    return False


def raw_dir(exp: str) -> Path | None:
    d = sorted((ROOT / "results" / "raw" / exp).glob(f"{exp}-*"))
    return d[-1] if d else None


def read_csv(p: Path) -> list[dict]:
    with p.open() as fh:
        return list(csv.DictReader(fh))


def part_a() -> dict:
    res: dict = {"A1_manifest_hashes": [], "A2_metrics_copy": {}, "A3_counts": {}, "A4_recomputed": []}
    man = load_json(ROOT / "results" / "M3-raw-manifest.json")
    for f in man["files"]:
        p = ROOT / f["path"]
        if p.exists():
            res["A1_manifest_hashes"].append({"path": f["path"], "match": sha(p) == f["sha256"]})
        else:
            res["A1_manifest_hashes"].append({"path": f["path"], "match": None, "note": "not present locally"})
    for i in range(1, 7):
        exp = f"EXP-00{i}"
        rd = raw_dir(exp)
        a = load_json(ROOT / "research" / "experiments" / exp / "analysis.json")
        committed = ROOT / "research" / "experiments" / exp / "metrics.csv"
        if rd is None:
            res["A2_metrics_copy"][exp] = None
            continue
        res["A2_metrics_copy"][exp] = sha(committed) == sha(rd / "metrics.csv")
        rows = read_csv(rd / "metrics.csv")
        cnt = Counter(r["status"] for r in rows)
        want = a["status_counts"]
        res["A3_counts"][exp] = {"n_rows": len(rows), "n_records_analysis": a["n_records"],
                                 "status_counts_raw": dict(cnt), "status_counts_analysis": want,
                                 "match": len(rows) == a["n_records"] and all(cnt.get(k, 0) == v for k, v in want.items())}

    def chk(name, got, want):
        ok = want is not None and got is not None and abs(got - want) <= 1e-12 * max(1.0, abs(want))
        res["A4_recomputed"].append({"quantity": name, "recomputed": got, "analysis_json": want, "match": ok})

    # EXP-003
    rd = raw_dir("EXP-003")
    a = load_json(ROOT / "research" / "experiments" / "EXP-003" / "analysis.json")
    rows = read_csv(rd / "metrics.csv")
    by = defaultdict(dict)
    for r in rows:
        by[(r["cell"], r["rho"], r["arm"])][r["seed"]] = r
    prim_ue, prim_so = by[("grid6", "2.0", "UE")], by[("grid6", "2.0", "SO")]
    vals = [float(prim_ue[s]["R"]) for s in prim_ue
            if prim_ue[s]["status"] == "ok" and prim_so.get(s, {}).get("status") == "ok"]
    chk("EXP-003 primary n", float(len(vals)), float(a["primary"]["n"]))
    chk("EXP-003 primary median R(UE)", statistics.median(vals), a["primary"]["median"])
    chk("EXP-003 primary mean R(UE)", statistics.fmean(vals), a["primary"]["mean"])
    for grid, levels in a["per_cell"].items():
        for rho_key, node in levels.items():
            for arm in ("UE", "FF"):
                summ = node.get(f"R_{arm}")
                if not isinstance(summ, dict) or summ.get("median") is None:
                    continue
                rho = f"{float(rho_key):.1f}"
                recs, so = by[(grid, rho, arm)], by[(grid, rho, "SO")]
                v = [float(recs[s]["R"]) for s in recs
                     if recs[s]["status"] == "ok" and so.get(s, {}).get("status") == "ok"]
                chk(f"EXP-003 {grid} rho {rho} median R({arm})", statistics.median(v) if v else None, summ["median"])
    # EXP-004
    rd = raw_dir("EXP-004")
    a = load_json(ROOT / "research" / "experiments" / "EXP-004" / "analysis.json")
    rows = read_csv(rd / "metrics.csv")
    for scale, node in a["per_scale"].items():
        for arm, summ in node["R"].items():
            v = [float(r["R"]) for r in rows if r["arm"] == arm and float(r["capacity_scale"]) == float(scale)
                 and r["status"] == "ok" and r["R"] != ""]
            want = summ.get("median") if isinstance(summ, dict) else None
            if want is not None and v:
                chk(f"EXP-004 scale {scale} median R({arm})", statistics.median(v), want)
    # EXP-006
    rd = raw_dir("EXP-006")
    a = load_json(ROOT / "research" / "experiments" / "EXP-006" / "analysis.json")
    rows = read_csv(rd / "metrics.csv")
    for r in rows:
        if r["arm"] == "UE" and r["R"] != "" and r["cell"] == "siouxfalls" and float(r["rho"] or 0) == 2.0:
            chk("EXP-006 R(UE) rho 2", float(r["R"]), a["replication"]["R_UE_rho2"])
    return res


def source_values() -> dict[str, list[float]]:
    src: dict[str, list[float]] = {}
    files = list((ROOT / "research" / "experiments").glob("EXP-*/analysis.json"))
    files += list((ROOT / "research" / "experiments").glob("EXP-*/run_manifest.json"))
    files += list((ROOT / "results" / "exploratory").glob("X-EXP-00*-TOL1E-10-*/exploratory_analysis.json"))
    files += list((ROOT / "results" / "exploratory").glob("X-EXP-00*-TOL1E-10-*/run_manifest.json"))
    files += [ROOT / "results" / "exploratory" / "M4-confounder-checks.json",
              ROOT / "research" / "freeze.json", ROOT / "data" / "manifest.json"]
    files += list((ROOT / "results" / "exploratory").glob("calibration-*.json"))
    files += list((ROOT / "results" / "exploratory").glob("SMOKE*/metric_validation.json"))
    for f in files:
        if f.exists():
            vals: list[float] = []
            numeric_leaves(load_json(f), vals)
            src[str(f.relative_to(ROOT))] = vals
    # per-record tables of the confirmatory runs (committed copies)
    for f in (ROOT / "research" / "experiments").glob("EXP-*/metrics.csv"):
        vals = []
        for r in read_csv(f):
            for k in ("tstt", "R", "mean_trip_time", "runtime_s", "total_demand", "rel_gap", "iterations"):
                try:
                    vals.append(float(r[k]))
                except (KeyError, ValueError):
                    pass
        src[str(f.relative_to(ROOT))] = vals
    return src


def protocol_values() -> dict[str, list[float]]:
    out = {}
    files = [ROOT / "research" / "protocol.md", *sorted((ROOT / "research" / "experiments").glob("EXP-*/protocol.md")),
             *sorted((ROOT / "experiments").glob("EXP-*.json")), *sorted((ROOT / "experiments" / "exploratory").glob("X-EXP-*.json"))]
    for f in files:
        out[str(f.relative_to(ROOT))] = [float(t.replace(",", "")) for t in text_numbers(f.read_text())]
    return out


def part_b(docs: list[str]) -> dict:
    src, prot = source_values(), protocol_values()
    allsrc = [v for vs in src.values() for v in vs]
    allprot = [v for vs in prot.values() for v in vs]
    report = {}
    for d in docs:
        p = ROOT / d
        if not p.exists():
            report[d] = {"missing": True}
            continue
        text = p.read_text()
        # ignore hashes, run ids, paths, dates and code spans that are identifiers
        text = re.sub(r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,64}\b", " ", text)
        text = re.sub(r"\b(19|20)\d\d-\d\d-\d\d(T[\d:]+Z)?\b", " ", text)
        text = re.sub(r"\b(EXP|J|D|CL|X|S|H|A|B|C|M|DEC)-?\d+\b", " ", text)
        toks = text_numbers(text)
        traced, protocol_only, untraced = 0, 0, []
        for t in toks:
            s = t.replace(",", "")
            isint = "." not in s and "e" not in s
            if isint and (abs(int(s)) <= 100 or 1900 <= int(s) <= 2100):
                continue  # small integers (counts, section numbers, grid sizes) checked by hand
            if matches(t, allsrc):
                traced += 1
            elif matches(t, allprot):
                protocol_only += 1
            else:
                untraced.append(t)
        report[d] = {"n_checked": traced + protocol_only + len(untraced), "traced_to_results": traced,
                     "traced_to_protocol_or_config": protocol_only, "untraced": sorted(set(untraced))}
    return report


def part_c() -> dict:
    """Row-by-row semantic check: rebuild manuscript/supplementary table rows from analysis.json fields."""
    text = (ROOT / "research/paper/manuscript.md").read_text() + (ROOT / "research/paper/supplementary.md").read_text()
    a = load_json(ROOT / "research/experiments/EXP-003/analysis.json")
    f = lambda x, d: f"{x:.{d}f}"  # noqa: E731
    rows, missing = [], []

    def check(s):
        rows.append(s)
        if s not in text:
            missing.append(s)

    for g, lab in (("grid4", "4x4"), ("grid6", "6x6")):
        for r in ("1.0", "2.0", "3.0"):
            c = a["per_cell"][g][r]
            u, ff, p = c["R_UE"], c["R_FF"], c["paired_R_FF_minus_UE"]
            check(f"| {lab} | {r[0]} | {f(u['median'], 5)} [{f(u['ci95'][0], 5)}, {f(u['ci95'][1], 5)}] | "
                  f"{f(ff['median'], 4)} [{f(ff['ci95'][0], 4)}, {f(ff['ci95'][1], 4)}] | "
                  f"{f(p['median'], 4)} [{f(p['ci95'][0], 4)}, {f(p['ci95'][1], 4)}] |")
            gi, p9 = c["paired_gini_stretch_UE_minus_SO"], c["paired_p95_trip_time_UE_minus_SO"]
            check((f"| {lab} | {r[0]} | {f(gi['median'], 5)} [{f(gi['ci95'][0], 5)}, {f(gi['ci95'][1], 5)}] | "
                   f"{f(p9['median'], 4)} [{f(p9['ci95'][0], 4)}, {f(p9['ci95'][1], 4)}] |").replace("-0.0000", "0.0000"))
    for cell, lab in (("S1-tol1e-4", "S1, RG 1e-4"), ("S1-tol1e-8", "S1, RG 1e-8"), ("S2-beta1", "S2, beta = 1"),
                      ("S3-absolute", "S3, absolute calibration")):
        s = a["sensitivity"][cell]
        check(f"| {lab} | {s['n']} ({s['n_excluded']}) | {f(s['median'], 5)} | {f(s['lower_one_sided_95'], 5)} | "
              f"[{f(s['ci95'][0], 5)}, {f(s['ci95'][1], 5)}] |")
    b = load_json(ROOT / "research/experiments/EXP-004/analysis.json")["per_scale"]
    for arm in ("FF", "MIX(0.25)", "MIX(0.5)", "MIX(0.75)"):
        check("| " + arm + " | " + " | ".join(
            f"{f(b[s]['R'][arm]['median'], 5)} [{f(b[s]['R'][arm]['ci95'][0], 5)}, {f(b[s]['R'][arm]['ci95'][1], 5)}]"
            for s in ("0.8", "1.0", "1.2")) + " |")
    for i in range(len(b["1.0"]["steps"])):
        check(" | ".join(
            f"{f(b[s]['steps'][i]['median'], 5)} ({f(b[s]['steps'][i]['lower_one_sided_95'], 5)}; "
            f"[{f(b[s]['steps'][i]['ci95'][0], 5)}, {f(b[s]['steps'][i]['ci95'][1], 5)}])" for s in ("0.8", "1.0", "1.2")))
    e = load_json(ROOT / "research/experiments/EXP-006/analysis.json")["levels"]["siouxfalls"]
    for r in ("1.0", "2.0", "3.0"):
        lv = e[r]
        check(f"{f(lv['UE']['R'], 5)}")
        check(f"{f(lv['FF']['R'], 5)}")
        check(f"{f(lv['UE']['gini_stretch'], 4)} / {f(lv['SO']['gini_stretch'], 4)} / {f(lv['FF']['gini_stretch'], 4)}")
    return {"rows_checked": len(rows), "missing": missing}


def main(argv: list[str]) -> int:
    docs = argv or DEFAULT_DOCS
    out = {"generator": "scripts/evidence_audit.py", "part_a": part_a(), "part_b": part_b(docs), "part_c": part_c()}
    a = out["part_a"]
    summary = {
        "A1_hash_mismatches": [x["path"] for x in a["A1_manifest_hashes"] if x["match"] is False],
        "A1_checked": sum(1 for x in a["A1_manifest_hashes"] if x["match"] is not None),
        "A2_all_equal": all(v for v in a["A2_metrics_copy"].values() if v is not None),
        "A3_all_match": all(v["match"] for v in a["A3_counts"].values()),
        "A4_checked": len(a["A4_recomputed"]),
        "A4_mismatches": [x["quantity"] for x in a["A4_recomputed"] if not x["match"]],
        "C_rows_checked": out["part_c"]["rows_checked"],
        "C_missing": out["part_c"]["missing"],
        "B_untraced": {d: v.get("untraced") for d, v in out["part_b"].items() if v.get("untraced")},
    }
    out["summary"] = summary
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
