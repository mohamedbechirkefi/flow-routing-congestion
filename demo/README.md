<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# demo/

Static interactive research page (M5). It runs offline after the first load, has no backend, collects nothing about visitors and makes no request beyond its own files. Plain HTML, CSS and JavaScript (FLOW decision D-018: the repository's existing Python plus static files, no npm project). Design, fail-closed loader and Web Worker pattern follow the shared lab demo template, ported to plain JavaScript.

## What it shows

- **Overview** with the status label: preregistered simulation study, protocol v1.0 frozen by the owner on 2026-11-24, all six confirmatory experiments complete, manuscript draft not peer-reviewed, the owner's full-text review pending (M6).
- **Braess network, measured:** an animated network with a demand slider over the 75 EXP-002 demand points, before (without link e) and after (with link e), a routing-policy comparison (FF, UE, SO), edge congestion, and the paired before and after chart of mean trip time against demand. Values come from the committed raw records of the confirmatory EXP-002 run; readouts are rounded to two decimals.
- **Published results:** every registered experiment (EXP-001 to EXP-006) and the exploratory checks (the 1e-10 reruns and the M4 confounder checks), each with its status, its verdict under the frozen rule (EXP-001 and EXP-002: Contradicted), its claim ids and its numbers printed exactly as the manuscript prints them, with intervals where they exist. Charts: R(UE) by cell, paired R(FF) - R(UE), sensitivity, compliance.
- **Assumptions**, **method and limitations**, and the hashes of every source file.
- **Sandbox:** a port of the engine (free-flow loading, gradient projection for UE and SO, MIX(c)) runs in a Web Worker on the Braess network or on 4 by 4 grid-v1 networks from exploratory seeds 9000 to 9009, with network and seed, demand, compliance, run, cancel and reset. It is labelled sandbox output and is never mixed with published results.

Brand: "Flow", a transit-map and road-signage direction (`DESIGN.md`). The hero shows a route-map illustration of the Braess mechanism, labelled "Illustration, not study data"; it shows no number and reads no result file.

Labels: **Measured** (confirmatory), **Exploratory** (defined after results were seen; changes no verdict), **Assumption** (modelling inputs) and **Sandbox output** (computed in the browser), each with its own text tag and border style. Reduced motion (system setting or the on-page toggle) stops the animation.

## Files

| Path | Content |
|---|---|
| `site/` | `index.html`, `style.css`, `app.js` (page), `hero.js` (hero illustration, not study data), `results.js` (fail-closed loader), `engine.js` (engine port), `sandbox_worker.js` (Web Worker) |
| `DESIGN.md` | the brand and UI plan (owner request 2026-11-26) and its review |
| `public/brand/` | logo mark, small-size mark, one-colour mark, wordmark, lockups, favicon (SVG and 32 px PNG), Open Graph image (1200 by 630) |
| `public/fonts/` | self-hosted WOFF2 fonts and their OFL licence texts |
| `public/data/results.json` | written by `scripts/export_demo_data.py` from committed results (schema `lab-demo-results` 1.0.0) |
| `public/data/sandbox.json` | sandbox network definitions, written by `scripts/export_demo_sandbox.py` (not results) |
| `tests/` | Node built-in test runner: loader tests and the engine port against `tests/fixtures/sandbox_fixture.json` (Python engine output) |
| `tools/a11y_check.mjs` | offline and accessibility smoke check (Chrome DevTools Protocol) |
| `dist/` | build output, not committed |
| `wrangler.jsonc` | Cloudflare Workers static-assets configuration (assets only, directory `./dist`) |

## Commands

From the repository root, with Node 22 on the path (on the development machine, the workspace's read-only copy in `../../helix/.tools/node/bin`) for the tests and the checker:

    .venv/bin/python scripts/export_demo_data.py && .venv/bin/python scripts/export_demo_sandbox.py
    .venv/bin/python scripts/build_demo.py
    .venv/bin/python -m http.server --bind 127.0.0.1 --directory demo/dist 8000
    node --test demo/tests/*.test.mjs
    cd demo && node tools/a11y_check.mjs dist --screenshots <dir>

Demo: <https://flow-routing-congestion.kefimohamedbechir.workers.dev>. The page is hosted as Cloudflare Workers static assets on the free plan (owner, 2026-11-26, decision sheet, B2). `demo/wrangler.jsonc` names the built folder `./dist` as the assets directory; there is no Worker script. The deploy is made by the coordinator, not by any script of this repository. Source: <https://github.com/mohamedbechirkefi/flow-routing-congestion>.

## Third-party notes

Fonts are installed with npm into a scratch folder (`npm_config_before=2026-11-12`, exact versions) and only the WOFF2 files for the weights used are copied into `public/fonts/`, with their licence texts. Nothing is loaded from a font service.

| Family | Package and version | Files used | Licence |
|---|---|---|---|
| Overpass (The Overpass Project Authors) | `@fontsource/overpass` 5.3.0 | latin 400, 600, 800 normal | SIL Open Font License 1.1 (`public/fonts/OFL-overpass.txt`) |
| PT Serif (ParaType) | `@fontsource/pt-serif` 5.3.0 | latin 400 normal, 400 italic, 700 normal | SIL Open Font License 1.1 (`public/fonts/OFL-pt-serif.txt`) |

The wordmark "Flow" in the logo files is built from Overpass 800 outlines (converted to paths with fontTools), which the OFL permits.
