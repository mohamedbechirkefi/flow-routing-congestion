# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Report generator: tables and figures built only from a validated results file.

PDF route (decision D-002 and the M0 workaround): pandoc Markdown -> Typst with
``-V mainfont="Libertinus Serif"``, compiled by the ``typst`` Python package.
"""

from __future__ import annotations

import os
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

from .schema import load_result

PANDOC = os.environ.get("FLOW_PANDOC", "/Users/bechir/research/labs/.tools/pandoc")
MAINFONT = "Libertinus Serif"


def _fmt(v, digits: int = 4) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if abs(v) >= 1e4 or (0 < abs(v) < 1e-3):
        return f"{v:.3e}"
    return f"{v:.{digits}f}"


def summarise(doc: dict) -> list[dict]:
    """One row per (cell, factor level without seed, arm): counts and distribution of R and runtime."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in doc["records"]:
        f = {k: v for k, v in r["factors"].items() if k not in ("d_ref", "total_demand")}
        key = (r["cell"], tuple(sorted(f.items())), r["arm"])
        groups[key].append(r)
    so_ok = {r["record_id"].rsplit("/", 1)[0]: r["status"] == "ok" for r in doc["records"] if r["arm"] == "SO"}

    def usable(r: dict) -> bool:
        # R needs a converged arm AND a converged SO reference on the same instance
        return (r["status"] == "ok" and bool(r["metrics"]) and r["metrics"].get("R") is not None
                and so_ok.get(r["record_id"].rsplit("/", 1)[0], False))

    rows = []
    for (cell, fitems, arm), recs in groups.items():
        R = [r["metrics"]["R"] for r in recs if usable(r)]
        rt = [r["solver"]["runtime_s"] for r in recs]
        its = [r["solver"]["iterations"] for r in recs if r["solver"]["iterations"] is not None]
        row = {
            "cell": cell,
            "factors": dict(fitems),
            "arm": arm,
            "n": len(recs),
            "n_ok": sum(r["status"] == "ok" for r in recs),
            "n_nonconverged": sum(r["status"] == "nonconverged" for r in recs),
            "n_failed": sum(r["status"] == "failed" for r in recs),
            "n_R": len(R),
            "R_median": float(np.median(R)) if R else None,
            "R_q25": float(np.quantile(R, 0.25)) if R else None,
            "R_q75": float(np.quantile(R, 0.75)) if R else None,
            "R_min": float(np.min(R)) if R else None,
            "R_max": float(np.max(R)) if R else None,
            "R_sd": float(np.std(R, ddof=1)) if len(R) > 1 else None,
            "runtime_mean_s": float(np.mean(rt)),
            "runtime_max_s": float(np.max(rt)),
            "iterations_median": float(np.median(its)) if its else None,
        }
        rows.append(row)
    return rows


def markdown_table(rows: list[dict]) -> str:
    """Compact table (fits a portrait page): status counts and R distribution per group."""
    head = "| Cell | Factors | Arm | n (ok/nc/fail) | n for R | R median [IQR] | R min to max | mean s | med. iter. |"
    sep = "|---|---|---|---|---|---|---|---|---|"
    lines = [head, sep]
    for r in rows:
        fac = ", ".join(f"{k}={v}" for k, v in r["factors"].items() if k not in ("generator", "calibration", "beta", "n")
                        and not (k == "capacity_scale" and v == 1.0))
        lines.append(
            f"| {r['cell']} | {fac} | {r['arm']} | {r['n']} ({r['n_ok']}/{r['n_nonconverged']}/{r['n_failed']}) | {r['n_R']} | "
            f"{_fmt(r['R_median'])} [{_fmt(r['R_q25'])}, {_fmt(r['R_q75'])}] | {_fmt(r['R_min'])} to {_fmt(r['R_max'])} | "
            f"{_fmt(r['runtime_mean_s'], 3)} | {_fmt(r['iterations_median'], 0)} |"
        )
    return "\n".join(lines)


def make_figures(doc: dict, fig_dir: Path) -> list[tuple[str, str, str]]:
    """Per-instance R by arm and cell (strip plot). Returns (file, caption, alt text)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir.mkdir(parents=True, exist_ok=True)
    out = []
    by_cell: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    so_ok = {r["record_id"].rsplit("/", 1)[0]: r["status"] == "ok" for r in doc["records"] if r["arm"] == "SO"}
    for r in doc["records"]:
        if (r["status"] == "ok" and r["metrics"] and r["metrics"].get("R") is not None and r["seed"] is not None
                and so_ok.get(r["record_id"].rsplit("/", 1)[0], False)):
            label = f"{r['arm']} rho={r['factors'].get('rho')}"
            by_cell[r["cell"]][label].append(r["metrics"]["R"])
    for cell, series in sorted(by_cell.items()):
        labels = sorted(series)
        fig, ax = plt.subplots(figsize=(max(4.0, 0.9 * len(labels) + 1.5), 3.2))
        for i, lab in enumerate(labels):
            ys = series[lab]
            xs = np.full(len(ys), i) + np.linspace(-0.12, 0.12, len(ys)) if len(ys) > 1 else [i]
            ax.scatter(xs, ys, s=14, color="#33475b")
            ax.hlines(np.median(ys), i - 0.25, i + 0.25, color="#b5452b", lw=1.5)
        ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right", fontsize=8)
        ax.set_ylabel("R (dimensionless)")
        ax.set_title(f"{cell}: per-instance R (EXPLORATORY)", fontsize=9)
        ax.axhline(0, color="#999999", lw=0.6)
        fig.tight_layout()
        name = f"R_{cell}.png"
        fig.savefig(fig_dir / name, dpi=150)
        plt.close(fig)
        n = len(next(iter(series.values())))
        out.append((
            name,
            f"Per-instance relative excess R over the system optimum, cell {cell}; dots are instances whose arm and SO reference both converged, red bars medians. Exploratory, about {n} instances per arm.",
            f"Strip plot of R by arm for cell {cell}.",
        ))
    return out


def write_report(run_dir: Path, pdf: bool = True) -> dict:
    run_dir = Path(run_dir).resolve()
    doc = load_result(run_dir / "results.json")  # fail closed on malformed results
    rows = summarise(doc)
    figs = make_figures(doc, run_dir / "figures")
    label = doc["label"].upper()
    lines = [
        f"<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->",
        f"# Run report {doc['run_id']}",
        "",
        f"**Label: {label}.** " + (
            "Exploratory run on exploratory seeds; not a finding and not evidence for any registered hypothesis."
            if doc["label"] == "exploratory" else "Confirmatory run under a recorded freeze."
        ),
        "",
        f"- Experiment id: {doc['experiment_id']}",
        f"- Config hash: `{doc['config_hash']}`",
        f"- Schema: {doc['schema_version']}; records: {len(doc['records'])}",
        "",
        "Generated by `flow report` from `results.json` only.",
        "",
        "## Summary by cell, factor level and arm",
        "",
        "R = TSTT / TSTT(SO) - 1 is the relative excess total system travel time over the system optimum of the same instance (dimensionless). Status counts: ok / nonconverged / failed. R statistics use only records whose own solve and whose SO reference both converged ('n for R'). Nonconverged and failed runs are counted, not dropped.",
        "",
        markdown_table(rows),
        "",
    ]
    for name, cap, alt in figs:
        lines += [f"![{cap}](figures/{name} \"{alt}\")", ""]
    failed = [r for r in doc["records"] if r["status"] == "failed"]
    if failed:
        lines += ["## Failed records", ""] + [f"- {r['record_id']}: {r['error'].splitlines()[-1]}" for r in failed] + [""]
    md = "\n".join(lines)
    (run_dir / "report.md").write_text(md)
    result = {"report_md": str(run_dir / "report.md"), "figures": [f[0] for f in figs], "pdf": None}
    if pdf:
        result["pdf"] = build_pdf(run_dir / "report.md")
    return result


def build_pdf(md_path: Path) -> str:
    """pandoc -> Typst -> PDF. Raises on failure (never claims a PDF that was not built)."""
    md_path = Path(md_path).resolve()
    typ = md_path.with_suffix(".typ")
    pdf = md_path.with_suffix(".pdf")
    subprocess.run(
        [PANDOC, str(md_path), "-s", "-t", "typst", "-V", f"mainfont={MAINFONT}", "-V", "fontsize=9pt", "-o", str(typ)],
        check=True, cwd=md_path.parent,
    )
    import typst

    typst.compile(str(typ), output=str(pdf), root=str(md_path.parent))
    typ.unlink()
    return str(pdf)
