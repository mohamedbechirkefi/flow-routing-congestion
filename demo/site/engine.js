// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// Browser port of the FLOW engine (src/flow/network.py, paths.py, assignment.py),
// reduced to what the sandbox needs: polynomial link costs t(x) = A + B x^P,
// Dijkstra with the (cost, node sequence) tie rule, all-or-nothing loading,
// free-flow routing (FF), path-based gradient projection for UE and SO (the solver
// of record, unit step, one iteration = one Gauss-Seidel sweep over OD pairs),
// MIX(c) and the free-flow reference demand D_ref. Checked against a Python fixture
// by tests/engine.test.mjs. Bounded: sweeps are capped and solves are generators,
// so the worker can yield and honour a cancel request between sweeps.

export class EngineError extends Error {}

export function makeNetwork(spec) {
  const n = spec.n_nodes;
  const { tail, head, A, B, P } = spec;
  if (!Number.isInteger(n) || n < 2) throw new EngineError("n_nodes must be an integer >= 2");
  const m = tail.length;
  for (const [name, a] of Object.entries({ head, A, B, P })) {
    if (!Array.isArray(a) || a.length !== m) throw new EngineError(`${name} must have ${m} entries`);
  }
  const pairs = new Set();
  for (let e = 0; e < m; e++) {
    if (!Number.isInteger(tail[e]) || !Number.isInteger(head[e]) || tail[e] < 0 || head[e] < 0 || tail[e] >= n || head[e] >= n) throw new EngineError("bad link endpoint");
    if (tail[e] === head[e]) throw new EngineError("self-loops are not allowed");
    const key = `${tail[e]},${head[e]}`;
    if (pairs.has(key)) throw new EngineError("parallel links are not allowed");
    pairs.add(key);
    if (!(A[e] >= 0) || !(B[e] >= 0) || !(P[e] >= 1) || ![A[e], B[e], P[e]].every(Number.isFinite)) throw new EngineError("bad cost coefficients");
  }
  const cap = spec.capacity ?? null;
  if (cap !== null && (cap.length !== m || cap.some((c) => !(c > 0) || !Number.isFinite(c)))) throw new EngineError("bad capacity");
  const out = Array.from({ length: n }, () => []);
  for (let e = 0; e < m; e++) out[tail[e]].push(e);
  for (const lst of out) lst.sort((a, b) => head[a] - head[b]);
  const lookup = new Map();
  for (let e = 0; e < m; e++) lookup.set(`${tail[e]},${head[e]}`, e);
  return { n, m, tail, head, A, B, P, capacity: cap, out, lookup };
}

export function linkTime(net, x) {
  const t = new Array(net.m);
  for (let e = 0; e < net.m; e++) t[e] = net.A[e] + net.B[e] * Math.max(x[e], 0) ** net.P[e];
  return t;
}

function marginalCost(net, x) {
  const t = new Array(net.m);
  for (let e = 0; e < net.m; e++) t[e] = net.A[e] + net.B[e] * (1 + net.P[e]) * Math.max(x[e], 0) ** net.P[e];
  return t;
}

function costDerivative(net, objective, x) {
  const d = new Array(net.m);
  for (let e = 0; e < net.m; e++) {
    const pm1 = net.P[e] - 1;
    const base = pm1 === 0 ? 1 : Math.max(x[e], 0) ** pm1;
    d[e] = net.B[e] * net.P[e] * base * (objective === "ue" ? 1 : 1 + net.P[e]);
  }
  return d;
}

export function tstt(net, x) {
  const t = linkTime(net, x);
  let s = 0;
  for (let e = 0; e < net.m; e++) s += x[e] * t[e];
  return s;
}

function lexLess(p, q) {
  const k = Math.min(p.length, q.length);
  for (let i = 0; i < k; i++) if (p[i] !== q[i]) return p[i] < q[i];
  return p.length < q.length;
}

function labelLess(a, b) {
  if (a[0] !== b[0]) return a[0] < b[0];
  return lexLess(a[1], b[1]);
}

class Heap {
  constructor() { this.h = []; }
  get size() { return this.h.length; }
  push(v) {
    const h = this.h;
    h.push(v);
    let i = h.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (!labelLess(h[i], h[p])) break;
      [h[i], h[p]] = [h[p], h[i]];
      i = p;
    }
  }
  pop() {
    const h = this.h;
    const top = h[0];
    const last = h.pop();
    if (h.length > 0) {
      h[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1, r = l + 1;
        let s = i;
        if (l < h.length && labelLess(h[l], h[s])) s = l;
        if (r < h.length && labelLess(h[r], h[s])) s = r;
        if (s === i) break;
        [h[i], h[s]] = [h[s], h[i]];
        i = s;
      }
    }
    return top;
  }
}

export function shortestPathTree(net, costs, origin) {
  for (const c of costs) if (!Number.isFinite(c) || c < 0) throw new EngineError("link costs must be finite and nonnegative");
  const dist = new Array(net.n).fill(Infinity);
  const path = new Array(net.n).fill(null);
  const done = new Array(net.n).fill(false);
  const heap = new Heap();
  heap.push([0, [origin], origin]);
  while (heap.size) {
    const [d, p, u] = heap.pop();
    if (done[u]) continue;
    done[u] = true;
    dist[u] = d;
    path[u] = p;
    for (const e of net.out[u]) {
      const v = net.head[e];
      if (done[v]) continue;
      heap.push([d + costs[e], [...p, v], v]);
    }
  }
  return { dist, path };
}

export function pathLinks(net, p) {
  const out = [];
  for (let i = 0; i + 1 < p.length; i++) out.push(net.lookup.get(`${p[i]},${p[i + 1]}`));
  return out;
}

export function allOrNothing(net, costs, demand) {
  const x = new Array(net.m).fill(0);
  const chosen = [];
  const kappa = [];
  const trees = new Map();
  for (const od of demand) {
    if (!trees.has(od.o)) trees.set(od.o, shortestPathTree(net, costs, od.o));
    const { dist, path } = trees.get(od.o);
    const p = path[od.d];
    if (p === null) throw new EngineError(`no path from ${od.o} to ${od.d}`);
    chosen.push(p);
    kappa.push(dist[od.d]);
    if (od.q > 0) for (const e of pathLinks(net, p)) x[e] += od.q;
  }
  return { x, chosen, kappa };
}

function relativeGap(x, costs, demand, kappa) {
  let num = 0;
  for (let e = 0; e < x.length; e++) num += x[e] * costs[e];
  if (num <= 0) return 0;
  let sp = 0;
  demand.forEach((od, k) => { sp += od.q * kappa[k]; });
  return (num - sp) / num;
}

export function freeFlow(net, demand) {
  const { x } = allOrNothing(net, net.A, demand);
  return { arm: "FF", x, iterations: 0, relGap: null, converged: true };
}

/** Gradient projection as in flow.assignment.gradient_projection; a generator that yields after every sweep. */
export function* gradientProjection(net, demand, objective = "ue", { tol = 1e-6, maxIter = 20000, background = null } = {}) {
  if (!(tol > 0)) throw new EngineError("tol must be positive");
  const bg = background ?? new Array(net.m).fill(0);
  if (objective === "so" && bg.some((v) => v !== 0)) throw new EngineError("system-optimal solve with background flow is not defined");
  const plus = (x) => x.map((v, e) => v + bg[e]);
  const cost = objective === "ue" ? (x) => linkTime(net, plus(x)) : (x) => marginalCost(net, x);
  let { x, chosen } = allOrNothing(net, cost(new Array(net.m).fill(0)), demand);
  const paths = demand.map((od, k) => {
    const pf = new Map();
    if (od.q > 0) pf.set(chosen[k].join(), od.q);
    return pf;
  });
  const linksOf = new Map();
  const links = (key) => {
    let l = linksOf.get(key);
    if (!l) { l = pathLinks(net, key.split(",").map(Number)); linksOf.set(key, l); }
    return l;
  };
  let it = 0;
  let rg;
  let converged;
  for (;;) {
    const costs = cost(x);
    const { kappa } = allOrNothing(net, costs, demand);
    rg = relativeGap(x, costs, demand, kappa);
    if (rg <= tol) { converged = true; break; }
    if (it >= maxIter) { converged = false; break; }
    demand.forEach((od, k) => {
      if (od.q <= 0) return;
      const c0 = cost(x);
      const { path } = shortestPathTree(net, c0, od.o);
      if (path[od.d] === null) throw new EngineError(`no path from ${od.o} to ${od.d}`);
      const best = path[od.d].join();
      const pf = paths[k];
      if (!pf.has(best)) pf.set(best, 0);
      const bestLinks = new Set(links(best));
      for (const key of [...pf.keys()]) {
        if (key === best || pf.get(key) <= 0) continue;
        const costs2 = cost(x);
        const deriv = costDerivative(net, objective, plus(x));
        const lk = new Set(links(key));
        let gap = 0;
        for (const e of lk) gap += costs2[e];
        let gb = 0;
        for (const e of bestLinks) gb += costs2[e];
        gap -= gb;
        if (gap <= 0) continue;
        let s = 0;
        for (const e of lk) if (!bestLinks.has(e)) s += deriv[e];
        for (const e of bestLinks) if (!lk.has(e)) s += deriv[e];
        const cur = pf.get(key);
        const delta = s <= 0 ? cur : Math.min(cur, gap / s);
        pf.set(key, cur - delta);
        pf.set(best, pf.get(best) + delta);
        for (const e of lk) x[e] -= delta;
        for (const e of bestLinks) x[e] += delta;
        x = x.map((v) => Math.max(v, 0));
      }
      for (const key of [...pf.keys()]) {
        if (key !== best && pf.get(key) <= 1e-14 * Math.max(1, od.q)) pf.delete(key);
      }
    });
    it += 1;
    yield it;
  }
  return { arm: objective === "ue" ? "UE" : "SO", x, iterations: it, relGap: rg, converged };
}

/** MIX(c) as in flow.assignment.mixed_compliance (gradient projection). */
export function* mixedCompliance(net, demand, c, soResult, opts = {}) {
  if (!(c >= 0 && c <= 1)) throw new EngineError("compliance c must lie in [0, 1]");
  const compX = c > 0 ? soResult.x.map((v) => c * v) : new Array(net.m).fill(0);
  const follow = demand.map((od) => ({ o: od.o, d: od.d, q: (1 - c) * od.q }));
  const fol = yield* gradientProjection(net, follow, "ue", { ...opts, background: compX });
  return {
    arm: `MIX(${c})`,
    x: compX.map((v, e) => v + fol.x[e]),
    iterations: fol.iterations,
    relGap: fol.relGap,
    converged: fol.converged && (c === 0 || soResult.converged),
  };
}

export function referenceDemandFF(net, od, weights) {
  const demand = od.map(([o, d], k) => ({ o, d, q: weights[k] }));
  const { x } = allOrNothing(net, net.A, demand);
  let peak = 0;
  for (let e = 0; e < net.m; e++) peak = Math.max(peak, x[e] / net.capacity[e]);
  if (!(peak > 0)) throw new EngineError("FF loading is zero; cannot calibrate demand");
  return 1 / peak;
}

/** Runs a generator to completion (tests and small synchronous use). */
export function runSync(gen) {
  for (;;) {
    const r = gen.next();
    if (r.done) return r.value;
  }
}

/** Solves FF, UE, SO and optionally MIX(c) on one network and demand. */
export function* solveArms(net, demand, { mixC = null, tol = 1e-6, maxIter = 20000 } = {}) {
  const ff = freeFlow(net, demand);
  const ue = yield* gradientProjection(net, demand, "ue", { tol, maxIter });
  const so = yield* gradientProjection(net, demand, "so", { tol, maxIter });
  const out = { FF: ff, UE: ue, SO: so };
  if (mixC !== null) out.MIX = yield* mixedCompliance(net, demand, mixC, so, { tol, maxIter });
  const base = tstt(net, so.x);
  for (const r of Object.values(out)) {
    r.tstt = tstt(net, r.x);
    r.R = base > 0 ? r.tstt / base - 1 : 0;
  }
  return out;
}

/** Validates the sandbox network file (fail closed) and returns ready networks. */
export function validateSandbox(raw) {
  if (typeof raw !== "object" || raw === null) throw new EngineError("sandbox: expected an object");
  if (raw.schema !== "flow-demo-sandbox" || String(raw.schema_version).split(".")[0] !== "1") throw new EngineError("sandbox: wrong schema");
  const br = raw.braess;
  if (!br || !br.with_e || !br.without_e) throw new EngineError("sandbox.braess: missing networks");
  if (!Array.isArray(raw.grids) || raw.grids.length === 0) throw new EngineError("sandbox.grids: empty");
  const grids = raw.grids.map((g, i) => {
    if (!Number.isInteger(g.seed) || !Number.isInteger(g.n)) throw new EngineError(`sandbox.grids[${i}]: bad seed or size`);
    const net = makeNetwork(g.network);
    if (net.capacity === null) throw new EngineError(`sandbox.grids[${i}]: capacities required`);
    if (!Array.isArray(g.od) || g.od.length !== g.weights.length || g.od.length === 0) throw new EngineError(`sandbox.grids[${i}]: bad OD sample`);
    const wsum = g.weights.reduce((a, b) => a + b, 0);
    if (Math.abs(wsum - 1) > 1e-9 || g.weights.some((w) => !(w >= 0))) throw new EngineError(`sandbox.grids[${i}]: weights must sum to 1`);
    if (!(g.d_ref > 0)) throw new EngineError(`sandbox.grids[${i}]: bad D_ref`);
    return { seed: g.seed, n: g.n, net, spec: g.network, od: g.od, weights: g.weights, d_ref: g.d_ref };
  });
  return {
    braess: { with_e: makeNetwork(br.with_e), without_e: makeNetwork(br.without_e), origin: br.origin, destination: br.destination, names: br.with_e.link_names },
    grids,
    solver: raw.solver,
  };
}
