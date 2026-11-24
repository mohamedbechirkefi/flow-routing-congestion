# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Command line: ``flow smoke | run | report | test``."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .network import FlowError
from .runner import FreezeError, load_config, repo_root, run_config, smoke_config


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def resolve_config(target: str) -> Path:
    p = Path(target)
    if p.exists():
        return p
    cand = repo_root() / "experiments" / f"{target}.json"
    if cand.exists():
        return cand
    raise FlowError(f"no config file {target!r} and no experiments/{target}.json")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="flow", description="FLOW simulation study (synthetic networks only).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("smoke", help="run the exploratory smoke matrix (protocol section 8)")
    s.add_argument("--out", type=Path, default=None)
    s.add_argument("--no-report", action="store_true")
    s.add_argument("--quiet", action="store_true")
    r = sub.add_parser("run", help="run an experiment config (EXP id or path); confirmatory configs need a recorded freeze")
    r.add_argument("target")
    r.add_argument("--out", type=Path, default=None)
    r.add_argument("--quiet", action="store_true")
    rp = sub.add_parser("report", help="build report.md, figures and PDF from a run directory")
    rp.add_argument("run_dir", type=Path)
    rp.add_argument("--no-pdf", action="store_true")
    t = sub.add_parser("test", help="run the test suite (pytest)")
    t.add_argument("pytest_args", nargs="*")
    args = ap.parse_args(argv)
    log = None if getattr(args, "quiet", False) else _log
    try:
        if args.cmd == "smoke":
            run_dir = run_config(smoke_config(), out_root=args.out, log=log)
            print(run_dir)
            if not args.no_report:
                print(json.dumps(__import__("flow.report", fromlist=["write_report"]).write_report(run_dir), indent=1))
            return 0
        if args.cmd == "run":
            cfg = load_config(resolve_config(args.target))
            run_dir = run_config(cfg, out_root=args.out, log=log)
            print(run_dir)
            return 0
        if args.cmd == "report":
            from .report import write_report

            print(json.dumps(write_report(args.run_dir, pdf=not args.no_pdf), indent=1))
            return 0
        if args.cmd == "test":
            return subprocess.call([sys.executable, "-m", "pytest", *args.pytest_args], cwd=repo_root())
    except FreezeError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 3
    except FlowError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
