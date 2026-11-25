// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// Fail-closed loader tests: the shared template's seven vitest cases ported to
// Node's built-in runner, plus the FLOW extensions. Run: node --test demo/tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ResultsError, validateResults, fmtInterval } from "../site/results.js";

const here = dirname(fileURLToPath(import.meta.url));
const good = () => JSON.parse(readFileSync(join(here, "..", "public", "data", "results.json"), "utf8"));
const rejects = (r) => assert.throws(() => validateResults(r), ResultsError);

test("accepts the exported results file", () => {
  const r = validateResults(good());
  assert.ok(r.experiments.length >= 9);
  assert.equal(r.braess_sweep.points.length, 75);
});
test("rejects a wrong schema name", () => rejects({ ...good(), schema: "other" }));
test("rejects an unsupported major version", () => rejects({ ...good(), schema_version: "2.0.0" }));
test("rejects a missing estimate", () => {
  const r = good();
  delete r.experiments[0].estimates[0].estimate;
  rejects(r);
});
test("rejects a non-finite number", () => {
  const r = good();
  r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "", display: "x" }];
  rejects(r);
});
test("rejects a half-open interval", () => {
  const r = good();
  r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "", display: "1", interval_display: "[0, ]" }];
  rejects(r);
});
test("rejects a malformed source hash", () => rejects({ ...good(), sources: [{ path: "a", sha256: "zz" }] }));

test("rejects an estimate without the manuscript's display text", () => {
  const r = good();
  r.experiments[2].estimates[0].display = null;
  rejects(r);
});
test("rejects an interval without display text", () => {
  const r = good();
  r.experiments[2].estimates[0].interval_display = null;
  rejects(r);
});
test("rejects an unknown evidence label", () => {
  const r = good();
  r.experiments[0].label = "sandbox";
  rejects(r);
});
test("rejects a missing Braess sweep", () => {
  const r = good();
  delete r.braess_sweep;
  rejects(r);
});
test("rejects a Braess point with a missing arm or negative flow", () => {
  const r = good();
  delete r.braess_sweep.points[3].with_e.SO;
  rejects(r);
  const q = good();
  q.braess_sweep.points[3].without_e.UE.link_flow[0] = -1;
  rejects(q);
});
test("rejects non-increasing Braess demands", () => {
  const r = good();
  r.braess_sweep.points[5].demand = r.braess_sweep.points[4].demand;
  rejects(r);
});
test("rejects a sensitivity row without an interval", () => {
  const r = good();
  r.sensitivity[0].ci_low = null;
  r.sensitivity[0].ci_high = null;
  rejects(r);
});
test("rejects compliance without exactly one confirmatory scale", () => {
  const r = good();
  r.compliance[0].confirmatory = true;
  rejects(r);
});
test("rejects malformed grid cells", () => {
  const r = good();
  r.grid_cells[0].R_UE.ci_low = 1;
  rejects(r);
});
test("interval text shows the manuscript's interval verbatim", () => {
  const r = validateResults(good());
  const prim = r.experiments.find((e) => e.id === "EXP-003").estimates[0];
  assert.equal(fmtInterval(prim), "95% [0.02075, 0.02559]");
});
