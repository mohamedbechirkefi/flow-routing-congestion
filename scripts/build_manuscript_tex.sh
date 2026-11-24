#!/bin/sh
# SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
# Regenerate research/paper/manuscript.tex from the canonical Markdown (decision D-002).
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PANDOC="${PANDOC:-/Users/bechir/research/labs/.tools/pandoc}"
OUT="$ROOT/research/paper/manuscript.tex"
TMP="$OUT.tmp"
"$PANDOC" "$ROOT/research/paper/manuscript.md" -s -t latex -o "$TMP"
{ echo "% SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0"; echo "% Generated from manuscript.md by scripts/build_manuscript_tex.sh. Do not edit by hand."; cat "$TMP"; } > "$OUT"
rm "$TMP"
echo "wrote $OUT"
