// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// The browser engine port against the Python engine (fixture written by
// scripts/export_demo_sandbox.py). Stated tolerance: TSTT within 1e-9 relative,
// every link flow within 1e-7 of the largest link flow, the same number of sweeps
// and the same convergence flag. Run: node --test demo/tests/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { makeNetwork, referenceDemandFF, runSync, solveArms, validateSandbox, gradientProjection, EngineError } from "../site/engine.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixture = JSON.parse(readFileSync(join(here, "fixtures", "sandbox_fixture.json"), "utf8"));
const sandbox = validateSandbox(JSON.parse(readFileSync(join(here, "..", "public", "data", "sandbox.json"), "utf8")));

const TSTT_REL = 1e-9;
const FLOW_REL = 1e-7;

function compare(label, js, py) {
  const rel = Math.abs(js.tstt - py.tstt) / Math.max(1, Math.abs(py.tstt));
  assert.ok(rel <= TSTT_REL, `${label}: TSTT ${js.tstt} vs ${py.tstt} (rel ${rel})`);
  const scale = Math.max(1, ...py.link_flow);
  py.link_flow.forEach((f, e) => {
    assert.ok(Math.abs(js.x[e] - f) <= FLOW_REL * scale, `${label}: link ${e} flow ${js.x[e]} vs ${f}`);
  });
  assert.equal(js.iterations, py.iterations, `${label}: sweeps`);
  assert.equal(js.converged, py.converged, `${label}: converged`);
}

test("fixture covers Braess and grid cases", () => {
  assert.equal(fixture.schema, "flow-demo-sandbox-fixture");
  assert.ok(fixture.cases.filter((c) => c.scenario === "braess").length >= 4);
  assert.ok(fixture.cases.filter((c) => c.scenario === "grid").length >= 2);
});

for (const c of fixture.cases) {
  const name = c.scenario === "braess" ? `Braess d=${c.demand} ${c.with_e ? "with" : "without"} e` : `grid seed ${c.seed} rho=${c.rho}`;
  test(`port matches Python engine: ${name}`, () => {
    let net, demand, mixC = null;
    if (c.scenario === "braess") {
      net = c.with_e ? sandbox.braess.with_e : sandbox.braess.without_e;
      demand = [{ o: 0, d: 3, q: c.demand }];
    } else {
      const g = sandbox.grids.find((x) => x.seed === c.seed);
      net = g.net;
      demand = g.od.map(([o, d], k) => ({ o, d, q: c.rho * g.d_ref * g.weights[k] }));
      mixC = 0.5;
    }
    const r = runSync(solveArms(net, demand, { mixC }));
    for (const arm of ["FF", "UE", "SO"]) compare(`${name} ${arm}`, r[arm], c.arms[arm]);
    if (mixC !== null) compare(`${name} MIX(0.5)`, r.MIX, c.arms["MIX(0.5)"]);
  });
}

test("free-flow reference demand matches the Python D_ref", () => {
  for (const g of sandbox.grids) {
    const d = referenceDemandFF(g.net, g.od, g.weights);
    assert.ok(Math.abs(d - g.d_ref) <= 1e-9 * g.d_ref, `seed ${g.seed}: ${d} vs ${g.d_ref}`);
  }
});

test("engine fails closed on invalid input", () => {
  assert.throws(() => makeNetwork({ n_nodes: 2, tail: [0], head: [0], A: [1], B: [1], P: [1] }), EngineError);
  assert.throws(() => makeNetwork({ n_nodes: 2, tail: [0], head: [1], A: [-1], B: [1], P: [1] }), EngineError);
  assert.throws(() => validateSandbox({ schema: "other" }), EngineError);
  const net = makeNetwork({ n_nodes: 3, tail: [0], head: [1], A: [1], B: [1], P: [1] });
  assert.throws(() => runSync(gradientProjection(net, [{ o: 0, d: 2, q: 1 }])), EngineError);
});

test("sweep cap is honoured and reported as nonconverged", () => {
  const g = sandbox.grids[0];
  const demand = g.od.map(([o, d], k) => ({ o, d, q: 3 * g.d_ref * g.weights[k] }));
  const r = runSync(gradientProjection(g.net, demand, "so", { tol: 1e-14, maxIter: 2 }));
  assert.equal(r.iterations, 2);
  assert.equal(r.converged, false);
});
