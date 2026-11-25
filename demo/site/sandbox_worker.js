// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// Visitor sandbox worker: runs the engine port on one small network, bounded and
// cancellable. Its output is sandbox output, never a published result.
import { makeNetwork, solveArms, EngineError } from "./engine.js";

const MAX_SWEEPS = 20000; // the research solver's cap (protocol section 7)
const MAX_LINKS = 200; // the sandbox only ships the Braess network and 4 by 4 grids
let cancelled = false;
let running = 0;

self.onmessage = async (ev) => {
  const m = ev.data;
  if (m.type === "cancel") {
    cancelled = true;
    return;
  }
  if (m.type !== "run") return;
  cancelled = false;
  const job = ++running;
  try {
    const net = makeNetwork(m.network);
    if (net.m > MAX_LINKS) throw new EngineError("network too large for the sandbox");
    if (!Array.isArray(m.demand) || m.demand.length === 0 || m.demand.some((od) => !(od.q >= 0) || !Number.isFinite(od.q))) throw new EngineError("bad demand");
    const mixC = m.mixC === null ? null : Number(m.mixC);
    const gen = solveArms(net, m.demand, { mixC, tol: 1e-6, maxIter: MAX_SWEEPS });
    let sweeps = 0;
    let last = Date.now();
    let r;
    for (;;) {
      r = gen.next();
      if (r.done) break;
      sweeps++;
      if (Date.now() - last > 30) {
        await new Promise((res) => setTimeout(res, 0)); // let a cancel message in
        last = Date.now();
        if (cancelled || job !== running) {
          self.postMessage({ type: "cancelled", id: m.id });
          return;
        }
        self.postMessage({ type: "progress", id: m.id, sweeps });
      }
    }
    const out = {};
    for (const [k, v] of Object.entries(r.value)) {
      out[k] = { tstt: v.tstt, R: v.R, x: v.x, iterations: v.iterations, relGap: v.relGap, converged: v.converged };
    }
    self.postMessage({ type: "done", id: m.id, arms: out });
  } catch (e) {
    self.postMessage({ type: "error", id: m.id, message: e instanceof Error ? e.message : String(e) });
  }
};
