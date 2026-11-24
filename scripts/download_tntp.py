# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Download the TNTP Sioux Falls files into data/raw/tntp/SiouxFalls/ (never committed).

Deterministic: the files are fetched from a pinned commit of the Transportation
Networks for Research repository, so the bytes cannot change. Each file's SHA-256
is checked against the value recorded in ``data/manifest.json`` (``downloads``);
a mismatch is an error. A local record with URL, size, SHA-256 and access time is
written to ``data/raw/tntp/download_record.json`` (git-ignored, like the data).

Licence (README of the source repository, opened 2026-11-24): "All data is
currently donated. Data sets are for academic research purposes only." Local use
only; the files are never redistributed (owner approval 2026-11-24, round 2).

Usage: ``.venv/bin/python scripts/download_tntp.py [--record-hashes]``.
``--record-hashes`` prints the observed hashes instead of failing when the
manifest has none yet (used once, at the first download).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "d1639b4ef218c17928ba573e806ddf8ba5e7ae6d"
BASE = f"https://raw.githubusercontent.com/bstabler/TransportationNetworks/{COMMIT}/SiouxFalls"
FILES = ("SiouxFalls_net.tntp", "SiouxFalls_trips.tntp", "SiouxFalls_flow.tntp")
DEST = ROOT / "data" / "raw" / "tntp" / "SiouxFalls"
MAX_BYTES = 1_000_000  # each file is a few kilobytes; anything larger is refused


def expected_hashes() -> dict[str, str]:
    man = json.loads((ROOT / "data" / "manifest.json").read_text())
    return {d["file"]: d["sha256"] for d in man.get("downloads", []) if d.get("dataset") == "tntp-siouxfalls"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record-hashes", action="store_true")
    args = ap.parse_args(argv)
    expected = expected_hashes()
    DEST.mkdir(parents=True, exist_ok=True)
    record = {"source_commit": COMMIT, "accessed_utc": datetime.now(timezone.utc).isoformat(), "files": []}
    ok = True
    for name in FILES:
        url = f"{BASE}/{name}"
        with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (fixed https URL)
            data = resp.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            print(f"ERROR: {name} larger than {MAX_BYTES} bytes; refusing", file=sys.stderr)
            return 2
        digest = hashlib.sha256(data).hexdigest()
        want = expected.get(name)
        if want is None and not args.record_hashes:
            print(f"ERROR: no recorded SHA-256 for {name} in data/manifest.json", file=sys.stderr)
            return 2
        if want is not None and want != digest:
            print(f"ERROR: SHA-256 mismatch for {name}: got {digest}, expected {want}", file=sys.stderr)
            ok = False
            continue
        (DEST / name).write_bytes(data)
        record["files"].append({"file": name, "url": url, "bytes": len(data), "sha256": digest})
        print(f"{name} {len(data)} bytes sha256:{digest}")
    (DEST.parent / "download_record.json").write_text(json.dumps(record, indent=1) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
