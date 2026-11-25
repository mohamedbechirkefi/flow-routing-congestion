# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
"""M6 release-candidate checks (master prompt 11.6, M6): links, numbers, manifests, CITATION.cff.

Usage: .venv/bin/python scripts/m6_checks.py [links|numbers|manifests|cff|all]

- links: every relative link and anchor in tracked Markdown files resolves.
- numbers: every decimal number in README.md and articles/*.md appears verbatim in the manuscript.
- manifests: every path in research/publication/artifact_manifest.json exists; the SHA-256 values in
  data/manifest.json match the local (git-ignored) TNTP files when they are present.
- cff: CITATION.cff is structurally valid CFF 1.2.0 (keys and types) and has no date-released.

Each check prints a PASS or FAIL line and the script exits non-zero on any failure.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "research" / "paper" / "manuscript.md"

LINK_RE = re.compile(r"(?<!\\)!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^(```|~~~)")


def tracked_markdown() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [ROOT / p for p in out.split() if p and not p.startswith("master_prompt")]


def slug(heading: str) -> str:
    """GitHub-style anchor: lower case, punctuation removed, spaces to hyphens."""
    h = re.sub(r"[`*_]", "", heading.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found: set[str] = set()
    seen: dict[str, int] = {}
    in_fence = False
    for line in path.read_text().splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m and not in_fence:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            found.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
    found.update(re.findall(r"<a\s+(?:id|name)=\"([^\"]+)\"", path.read_text()))
    return found


def links_in(path: Path) -> list[str]:
    targets: list[str] = []
    in_fence = False
    for line in path.read_text().splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)  # inline code is not a link
        targets.extend(LINK_RE.findall(line))
    return targets


def check_links() -> list[str]:
    errors: list[str] = []
    n = 0
    for md in tracked_markdown():
        for target in links_in(md):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):  # http:, https:, mailto: and similar
                continue
            n += 1
            file_part, _, anchor = target.partition("#")
            dest = md if not file_part else (md.parent / file_part).resolve()
            rel = md.relative_to(ROOT)
            if not dest.exists():
                errors.append(f"{rel}: missing target {target}")
                continue
            if anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                errors.append(f"{rel}: missing anchor {target}")
    print(f"links: {n} relative links checked in {len(tracked_markdown())} tracked Markdown files")
    return errors


NUM_RE = re.compile(r"(?<![\w.])\d+(?:,\d{3})*\.\d+(?:e-?\d+)?(?![\w.]*\.\d)|(?<![\w.])\d+e-\d+")
# Strings that look like numbers but are not results: a local address and tool versions.
NOT_RESULTS = {"127.0.0.1"}


def check_numbers() -> list[str]:
    text = MANUSCRIPT.read_text()
    errors: list[str] = []
    files = [ROOT / "README.md", *sorted((ROOT / "articles").glob("*.md"))]
    n = 0
    for f in files:
        body = f.read_text()
        body = re.sub(r"```.*?```", "", body, flags=re.S)  # commands, not results
        body = re.sub(r"https?://\S+", "", body)
        for num in NUM_RE.findall(body):
            if num in NOT_RESULTS:
                continue
            n += 1
            if num not in text:
                errors.append(f"{f.relative_to(ROOT)}: {num} not in manuscript")
    print(f"numbers: {n} decimal numbers checked in {len(files)} files")
    return errors


def _expand(p: str) -> list[str]:
    m = re.search(r"\{(\d+)\.\.(\d+)\}", p)
    if not m:
        return [p]
    return [x for i in range(int(m.group(1)), int(m.group(2)) + 1) for x in _expand(p[: m.start()] + str(i) + p[m.end():])]


def manifest_paths() -> list[str]:
    doc = json.loads((ROOT / "research" / "publication" / "artifact_manifest.json").read_text())
    paths: list[str] = []
    for a in doc["artifacts"]:
        for key in ("result_path", "raw_path", "config_path", "generator_script", "path"):
            v = a.get(key)
            if not v:
                continue
            for part in str(v).split(";"):
                part = part.strip().split(" (")[0].strip()
                if part:
                    paths.extend(_expand(part))
    return paths


def check_manifests() -> list[str]:
    errors = [f"artifact_manifest.json: missing {p}" for p in manifest_paths() if not (ROOT / p).exists()]
    print(f"manifests: {len(manifest_paths())} artifact-manifest paths checked")
    data = json.loads((ROOT / "data" / "manifest.json").read_text())
    local = ROOT / "data" / "raw" / "tntp" / "SiouxFalls"
    checked = 0
    for d in data.get("downloads", []):
        f = local / d["file"]
        if not f.exists():
            continue
        checked += 1
        b = f.read_bytes()
        if hashlib.sha256(b).hexdigest() != d["sha256"] or len(b) != d["bytes"]:
            errors.append(f"data/manifest.json: {d['file']} hash or size mismatch")
    print(f"manifests: {checked} of {len(data.get('downloads', []))} data-manifest downloads present locally and checked")
    return errors


CFF_TOP = {"abstract": str, "authors": list, "cff-version": str, "commit": str, "contact": list, "date-released": str,
           "doi": str, "identifiers": list, "keywords": list, "license": (str, list), "license-url": str, "message": str,
           "preferred-citation": dict, "references": list, "repository": str, "repository-artifact": str,
           "repository-code": str, "title": str, "type": str, "url": str, "version": str}
CFF_REQUIRED = ("authors", "cff-version", "message", "title")


def parse_cff(text: str) -> dict:
    """Minimal parser for the flat subset of YAML used by this repository's CITATION.cff."""
    doc: dict = {}
    key = None
    for raw in text.splitlines():
        line = raw.split(" #")[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        if not line.startswith(" "):
            k, _, v = line.partition(":")
            key = k.strip()
            v = v.strip()
            doc[key] = json.loads(v) if v.startswith('"') else (v if v else [])
        elif line.lstrip().startswith("- "):
            item = line.lstrip()[2:]
            if ":" in item and not item.startswith('"'):
                k, _, v = item.partition(":")
                doc[key].append({k.strip(): json.loads(v.strip())})
            else:
                doc[key].append(json.loads(item) if item.startswith('"') else item.strip())
        else:
            k, _, v = line.strip().partition(":")
            doc[key][-1][k.strip()] = json.loads(v.strip())
    return doc


def check_cff() -> list[str]:
    doc = parse_cff((ROOT / "CITATION.cff").read_text())
    errors = [f"CITATION.cff: missing required key {k}" for k in CFF_REQUIRED if k not in doc]
    for k, v in doc.items():
        if k not in CFF_TOP:
            errors.append(f"CITATION.cff: unknown key {k}")
        elif not isinstance(v, CFF_TOP[k]):
            errors.append(f"CITATION.cff: key {k} has type {type(v).__name__}")
    if doc.get("cff-version") != "1.2.0":
        errors.append("CITATION.cff: cff-version is not 1.2.0")
    if "date-released" in doc:
        errors.append("CITATION.cff: date-released present although no release exists")
    for a in doc.get("authors", []):
        if not isinstance(a, dict) or not ({"family-names", "name"} & set(a)):
            errors.append("CITATION.cff: author without family-names or name")
    if not re.fullmatch(r"\d+\.\d+\.\d+-rc\d+", str(doc.get("version", ""))):
        errors.append("CITATION.cff: version is not a release candidate (x.y.z-rcN)")
    print(f"cff: {len(doc)} top-level keys checked; version {doc.get('version')}")
    return errors


CHECKS = {"links": check_links, "numbers": check_numbers, "manifests": check_manifests, "cff": check_cff}


def main(argv: list[str] | None = None) -> int:
    names = (argv or sys.argv[1:]) or ["all"]
    if names == ["all"]:
        names = list(CHECKS)
    failed = 0
    for name in names:
        errs = CHECKS[name]()
        for e in errs:
            print(f"  {e}")
        print(f"{'PASS' if not errs else 'FAIL'} {name}" + (f" ({len(errs)})" if errs else ""))
        failed += bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
