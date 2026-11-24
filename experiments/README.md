<!-- SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0 -->
# experiments/

- `EXP-001.json` to `EXP-004.json`: confirmatory configs mirroring the DRAFT protocol v0.1. `flow run EXP-00N` refuses them (exit code 3) until the freeze is recorded in `research/decision_log.md` as `FREEZE <path> sha256:<hex>` lines matching the current protocol files. EXP-003 omits S3 because its share parameter is not fixed in the draft. No EXP-005 config yet (optional experiment; link-removal runner not written).
- `exploratory/`: EXPLORATORY M2 planning configs (seeds 9000-9019 only).
