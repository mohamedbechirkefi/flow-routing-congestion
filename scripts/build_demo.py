# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Assemble the static M5 demo into demo/dist/ (FLOW D-018: plain static files, no npm).

Copies demo/site/* and demo/public/data/*.json into demo/dist/, after three fail-closed
checks: the exported data files equal a fresh export (scripts/export_demo_data.py and
scripts/export_demo_sandbox.py, --check), no site file references a remote host, and
no REPLACE template marker is left. demo/dist/ is not committed (.gitignore).

Usage: .venv/bin/python scripts/build_demo.py
Preview: .venv/bin/python -m http.server --bind 127.0.0.1 --directory demo/dist 8000
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "demo" / "site"
DATA = ROOT / "demo" / "public" / "data"
DIST = ROOT / "demo" / "dist"

# The SVG namespace string is an identifier, not a request.
ALLOWED_URLS = {"http://www.w3.org/2000/svg"}
URL = re.compile(r"(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}[^\s\"'`)]*")


def main() -> int:
    for script in ("export_demo_data.py", "export_demo_sandbox.py"):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--check"], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode != 0:
            print(f"build refused: {script} --check failed; rerun the export", file=sys.stderr)
            return 1
    files = sorted(p for p in SITE.iterdir() if p.is_file())
    for p in files:
        text = p.read_text()
        remote = sorted({u for u in URL.findall(text) if u not in ALLOWED_URLS})
        if remote:
            print(f"build refused: {p.name} references remote locations {remote}", file=sys.stderr)
            return 1
        if "REPLACE" in text:
            print(f"build refused: template marker left in {p.name}", file=sys.stderr)
            return 1
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "data").mkdir(parents=True)
    for p in files:
        shutil.copy2(p, DIST / p.name)
    for p in sorted(DATA.glob("*.json")):
        shutil.copy2(p, DIST / "data" / p.name)
    n = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"built {DIST.relative_to(ROOT)}: {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
