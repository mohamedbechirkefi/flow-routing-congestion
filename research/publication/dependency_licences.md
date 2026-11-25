<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# Dependency licences (M6, 2026-11-25)

Source: the installed `.venv` package metadata (`License-Expression`, `License` and licence classifiers, read with `importlib.metadata` after `uv sync --frozen --all-groups --all-extras`), plus the tools used to build and check the release candidate. FLOW's demo has no npm project and no `node_modules` (decision D-018), so there are no npm dependencies to list.

Accepted without a flag: MIT, BSD, ISC, Apache-2.0, PSF, MPL-2.0 and similarly permissive licences.

## Python runtime and build dependencies (`uv.lock`, 19 installed packages)

| Package | Version | Group | Licence (from metadata) | Flag |
|---|---|---|---|---|
| numpy | 2.5.4 | runtime | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | none (all permissive) |
| matplotlib | 3.11.2 | report | Matplotlib licence (PSF-based; classifier "Python Software Foundation License") | none |
| contourpy | 1.4.0 | report (matplotlib) | BSD-3-Clause | none |
| cycler | 0.12.1 | report (matplotlib) | BSD (classifier "BSD License") | none |
| fonttools | 4.68.0 | report (matplotlib) | MIT | none |
| kiwisolver | 1.5.1 | report (matplotlib) | BSD (classifier "BSD License") | none |
| packaging | 26.3 | report, dev | Apache-2.0 OR BSD-2-Clause | none |
| pillow | 13.0.0 | report (matplotlib) | MIT-CMU | none (permissive, HPND family) |
| pyparsing | 3.3.3 | report (matplotlib) | MIT | none |
| python-dateutil | 4.0.0 | report (matplotlib) | BSD-3-Clause | none |
| typst | 0.15.2 | report | Apache-2.0 | none |
| hypothesis | 6.170.15 | dev | MPL-2.0 | none |
| sortedcontainers | 2.4.0 | dev (hypothesis) | Apache 2.0 | none |
| tzdata | 2026.6 | dev (hypothesis) | Apache-2.0 | none |
| pytest | 9.2.0 | dev | MIT | none |
| iniconfig | 2.3.1 | dev (pytest) | MIT | none |
| pluggy | 1.7.0 | dev (pytest) | MIT | none |
| Pygments | 2.21.0 | dev (pytest) | BSD-2-Clause | none |
| flow-routing-congestion | 0.0.1 | this project | LicenseRef-FLOW-NC-Research-1.0 (custom, non-commercial) | the project's own licence; not a dependency |

Build backend: `hatchling>=1.25` (`pyproject.toml`, `[build-system]`) is resolved by uv in an isolated build environment and is not installed in `.venv`, so its licence was not read from installed metadata in this session. **Flag: unverified here.**

## Tools used to build or check, not distributed

| Tool | Version | Use | Licence | Flag |
|---|---|---|---|---|
| pandoc | 3.6.3 | Markdown to Typst and LaTeX | GPL-2.0-or-later | **Flag: copyleft tool.** Used as a converter only; it is not bundled or linked, and its output is not covered by its licence. |
| Typst compiler (inside the `typst` package) | 0.15.1 (PDF creator string) | PDF compilation | Apache-2.0 | none |
| Fonts embedded in the PDFs by Typst (Libertinus Serif regular, italic and bold; DejaVu Sans Mono; listed from the PDF font resources with pypdf) | bundled with Typst | PDF text | Libertinus: SIL Open Font License 1.1; DejaVu: Bitstream Vera derived free font licence (both from general knowledge, not re-checked in this session) | **Flag: font licences, not in the accepted list.** Both permit embedding in documents; recorded for the owner. |
| Node | 22.23.3 | demo tests and the accessibility checker | MIT-style Node licence | none (not distributed) |
| Google Chrome (headless) | installed application | accessibility checker only | proprietary freeware | **Flag: proprietary test tool.** Not distributed; no code or data from it is in the repository. |
| uv | workspace copy | environment management | MIT OR Apache-2.0 | none |

## Data

The TNTP Sioux Falls files are used locally only and are not redistributed ("academic research purposes only"; `data/manifest.json`, owner approval 2026-11-24 round 2). They are not a software dependency and carry no open licence; this is already disclosed in the README and the manuscript.

## Result

No runtime dependency carries a copyleft or non-permissive licence. Flags for the owner: pandoc (GPL-2.0-or-later, build tool only), the OFL-1.1 and DejaVu fonts embedded in the PDFs, headless Chrome (proprietary, test tool only) and the hatchling build backend (licence not read in this session).
