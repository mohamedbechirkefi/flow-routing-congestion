# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""Ingestion of TNTP-format networks (Transportation Networks for Research).

Pure functions: text in, validated tables, a ``Network``, a ``Demand`` and an
ingestion report (schema checks, missingness and exclusion counts) out. No file
is written here. The raw files are never committed (licence "academic research
purposes only"; owner approval 2026-11-24, round 2); tests use a committed
synthetic fixture in the same schema (``tests/fixtures/tntp_synthetic/``).

Cost model: TNTP gives ``t = fft * (1 + b * (x / capacity) ** power)``, which maps
onto the engine's ``A + B x^P`` with ``A = fft``, ``B = fft * b / capacity ** power``,
``P = power`` (network.py). Node ids are 1-based in TNTP and 0-based here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from .network import Demand, DemandError, Network, NetworkError, ODPair

NET_COLUMNS = ("init_node", "term_node", "capacity", "length", "free_flow_time", "b", "power", "speed", "toll", "link_type")


class TNTPError(NetworkError):
    """A TNTP file violates the expected schema."""


@dataclass
class IngestReport:
    """Counts produced by ingestion (aggregate only, safe to commit)."""

    links_read: int = 0
    links_kept: int = 0
    missing_fields: dict[str, int] = field(default_factory=dict)
    od_cells_read: int = 0
    od_pairs_kept: int = 0
    od_excluded_zero: int = 0
    od_excluded_diagonal: int = 0
    total_od_flow_read: float = 0.0
    total_od_flow_header: float | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def _metadata(text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    lines = text.splitlines()
    body_start = None
    for i, line in enumerate(lines):
        m = re.match(r"\s*<([A-Z ]+)>\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1).strip()
        if key == "END OF METADATA":
            body_start = i + 1
            break
        meta[key] = m.group(2).strip()
    if body_start is None:
        raise TNTPError("missing <END OF METADATA>")
    return meta, "\n".join(lines[body_start:])


def _int_meta(meta: dict[str, str], key: str) -> int:
    if key not in meta:
        raise TNTPError(f"missing metadata <{key}>")
    try:
        return int(float(meta[key].split()[0]))
    except (ValueError, IndexError) as exc:
        raise TNTPError(f"metadata <{key}> is not a number: {meta[key]!r}") from exc


def parse_net(text: str, report: IngestReport | None = None) -> dict[str, np.ndarray]:
    """Parse a ``*_net.tntp`` file into column arrays; validates the schema."""
    rep = report if report is not None else IngestReport()
    meta, body = _metadata(text)
    rep.metadata.update({k: v for k, v in meta.items() if k in ("NUMBER OF ZONES", "NUMBER OF NODES", "FIRST THRU NODE", "NUMBER OF LINKS")})
    n_links = _int_meta(meta, "NUMBER OF LINKS")
    n_nodes = _int_meta(meta, "NUMBER OF NODES")
    first_thru = _int_meta(meta, "FIRST THRU NODE")
    if first_thru != 1:
        raise TNTPError("FIRST THRU NODE other than 1 (zones that block through traffic) is not supported")
    rows: list[list[float]] = []
    missing = {c: 0 for c in NET_COLUMNS}
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("~"):
            continue
        s = s.rstrip(";").strip()
        parts = s.split()
        if len(parts) < 7:
            raise TNTPError(f"link row has {len(parts)} fields, need at least 7: {line!r}")
        vals: list[float] = []
        for k, col in enumerate(NET_COLUMNS):
            if k >= len(parts):
                missing[col] += 1
                vals.append(float("nan"))
                continue
            try:
                vals.append(float(parts[k]))
            except ValueError as exc:
                raise TNTPError(f"non-numeric {col} in row {line!r}") from exc
        rows.append(vals)
    rep.links_read = len(rows)
    rep.missing_fields = {k: v for k, v in missing.items() if v}
    if len(rows) != n_links:
        raise TNTPError(f"header says {n_links} links, file has {len(rows)}")
    arr = np.array(rows, dtype=float)
    cols = {c: arr[:, k] for k, c in enumerate(NET_COLUMNS)}
    for c in ("init_node", "term_node", "capacity", "free_flow_time", "b", "power"):
        if np.any(~np.isfinite(cols[c])):
            raise TNTPError(f"column {c} has missing or non-finite values")
    for c in ("init_node", "term_node"):
        if np.any(cols[c] != np.round(cols[c])) or cols[c].min() < 1 or cols[c].max() > n_nodes:
            raise TNTPError(f"{c} must be integer node ids in [1, {n_nodes}]")
    if np.any(cols["capacity"] <= 0):
        raise TNTPError("capacity must be positive")
    if np.any(cols["free_flow_time"] < 0) or np.any(cols["b"] < 0):
        raise TNTPError("free_flow_time and b must be nonnegative")
    if np.any(cols["power"] < 1):
        raise TNTPError("power must be >= 1")
    rep.links_kept = len(rows)
    return cols


def parse_trips(text: str, report: IngestReport | None = None) -> list[tuple[int, int, float]]:
    """Parse a ``*_trips.tntp`` file into (origin, destination, flow) with 1-based zones.

    Zero cells and diagonal cells are excluded and counted.
    """
    rep = report if report is not None else IngestReport()
    meta, body = _metadata(text)
    n_zones = _int_meta(meta, "NUMBER OF ZONES")
    if "TOTAL OD FLOW" in meta:
        rep.total_od_flow_header = float(meta["TOTAL OD FLOW"].split()[0])
    out: list[tuple[int, int, float]] = []
    origin: int | None = None
    seen: set[tuple[int, int]] = set()
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.match(r"Origin\s+(\d+)", s)
        if m:
            origin = int(m.group(1))
            if not 1 <= origin <= n_zones:
                raise TNTPError(f"origin {origin} outside 1..{n_zones}")
            continue
        if origin is None:
            raise TNTPError(f"OD entry before any Origin line: {line!r}")
        for dest_s, flow_s in re.findall(r"(\d+)\s*:\s*([-+0-9.eE]+)\s*;", s):
            dest = int(dest_s)
            flow = float(flow_s)
            rep.od_cells_read += 1
            if not 1 <= dest <= n_zones:
                raise TNTPError(f"destination {dest} outside 1..{n_zones}")
            if not np.isfinite(flow) or flow < 0:
                raise TNTPError(f"OD flow must be finite and nonnegative, got {flow_s}")
            if (origin, dest) in seen:
                raise TNTPError(f"duplicate OD cell {(origin, dest)}")
            seen.add((origin, dest))
            rep.total_od_flow_read += flow
            if origin == dest:
                rep.od_excluded_diagonal += 1
                if flow != 0:
                    raise TNTPError(f"nonzero intrazonal flow at zone {origin}")
                continue
            if flow == 0:
                rep.od_excluded_zero += 1
                continue
            out.append((origin, dest, flow))
    rep.od_pairs_kept = len(out)
    if rep.total_od_flow_header is not None and abs(rep.total_od_flow_read - rep.total_od_flow_header) > 1e-6 * max(1.0, rep.total_od_flow_header):
        raise TNTPError(f"OD total {rep.total_od_flow_read} differs from header {rep.total_od_flow_header}")
    if not out:
        raise TNTPError("no positive OD flow")
    return out


def parse_flow(text: str) -> list[tuple[int, int, float]]:
    """Parse a ``*_flow.tntp`` reference solution into (from, to, volume) with 1-based nodes."""
    out = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 3 or not parts[0].isdigit():
            continue
        out.append((int(parts[0]), int(parts[1]), float(parts[2])))
    if not out:
        raise TNTPError("no flow rows")
    return out


def build_network(cols: dict[str, np.ndarray], n_nodes: int, name: str) -> Network:
    """Engine network from parsed TNTP columns (0-based node ids)."""
    fft = cols["free_flow_time"]
    cap = cols["capacity"]
    return Network(
        n_nodes=int(n_nodes),
        tail=cols["init_node"].astype(np.int64) - 1,
        head=cols["term_node"].astype(np.int64) - 1,
        A=fft,
        B=fft * cols["b"] / cap ** cols["power"],
        P=cols["power"],
        capacity=cap,
        name=name,
    )


def build_demand(trips: list[tuple[int, int, float]], scale: float = 1.0) -> Demand:
    if not (np.isfinite(scale) and scale >= 0):
        raise DemandError("scale must be finite and nonnegative")
    return Demand(tuple(ODPair(o - 1, d - 1, q * scale) for o, d, q in trips))


def reference_link_flow(net: Network, flows: list[tuple[int, int, float]]) -> np.ndarray:
    """Reference link flows aligned with ``net`` link order."""
    x = np.full(net.n_links, np.nan)
    for u, v, q in flows:
        x[net.link_index(u - 1, v - 1)] = q
    if np.any(np.isnan(x)):
        raise TNTPError("reference flow file does not cover every link")
    return x


@dataclass(frozen=True)
class TNTPInstance:
    network: Network
    trips: tuple[tuple[int, int, float], ...]
    reference_flow: np.ndarray | None
    report: dict


def ingest(net_text: str, trips_text: str, flow_text: str | None = None, name: str = "tntp") -> TNTPInstance:
    """Pure ingestion: raw texts to network, positive OD table, reference flow and report."""
    rep = IngestReport()
    cols = parse_net(net_text, rep)
    n_nodes = int(rep.metadata["NUMBER OF NODES"].split()[0])
    trips = parse_trips(trips_text, rep)
    net = build_network(cols, n_nodes, name)
    for o, d, _ in trips:
        if o > n_nodes or d > n_nodes:
            raise TNTPError("zone id beyond node count")
    ref = reference_link_flow(net, parse_flow(flow_text)) if flow_text is not None else None
    return TNTPInstance(net, tuple(trips), ref, rep.as_dict())
