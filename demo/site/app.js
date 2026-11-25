// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// FLOW lab page. Published numbers come only from data/results.json (validated,
// fail closed) and are printed with the manuscript's own text. Visual readouts on
// the Braess explorer are rounded from the committed EXP-002 raw records. Sandbox
// output comes from the worker and is labelled as such. No request leaves the page's
// own origin and nothing is stored.
import { loadResults, fmtEstimate, fmtInterval, ResultsError } from "./results.js";
import { validateSandbox, EngineError } from "./engine.js";

const SVGNS = "http://www.w3.org/2000/svg";

function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "text") el.textContent = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : String(v));
  }
  for (const c of kids.flat()) if (c !== null && c !== undefined && c !== false) el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return el;
}

function s(tag, attrs = {}, ...kids) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined) continue;
    // CSSOM writes are allowed by the page's CSP; style attributes in markup are not.
    if (k === "css") for (const [p, val] of Object.entries(v)) el.style.setProperty(p, val);
    else el.setAttribute(k, String(v));
  }
  for (const c of kids.flat()) if (c !== null && c !== undefined) el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return el;
}

const tag = (kind) => h("span", { class: `tag ${kind}`, text: { measured: "Measured", exploratory: "Exploratory", sandbox: "Sandbox output", assumption: "Assumption" }[kind] });
const est = (r, id, i) => r.experiments.find((e) => e.id === id).estimates[i];

// Motion: CSS animation only, off under prefers-reduced-motion and with the toggle.
const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
let motionOn = !motionQuery.matches;
const motionButtons = [];
function applyMotion() {
  document.documentElement.classList.toggle("no-motion", !motionOn);
  for (const b of motionButtons) {
    b.setAttribute("aria-pressed", String(motionOn));
    b.textContent = motionOn ? "Animation on" : "Animation off";
  }
}
motionQuery.addEventListener("change", () => { motionOn = !motionQuery.matches; applyMotion(); });
function motionToggle() {
  const b = h("button", { type: "button", id: `motion-${motionButtons.length + 1}`, "aria-pressed": String(motionOn), onclick: () => { motionOn = !motionOn; applyMotion(); } });
  motionButtons.push(b);
  applyMotion();
  return b;
}

function seg(options, current, onPick, label) {
  const wrap = h("div", { class: "seg", role: "group", "aria-label": label });
  const buttons = options.map(([value, text]) => h("button", { type: "button", "aria-pressed": String(value === current), onclick: () => {
    for (const b of buttons) b.setAttribute("aria-pressed", String(b === buttons[options.findIndex((o) => o[0] === value)]));
    onPick(value);
  } }, text));
  wrap.append(...buttons);
  return wrap;
}

// Responsive charts: re-rendered from data when the container width changes.
// A container is drawn once it has a width (after it is attached) and again when its width changes.
function responsive(container, draw) {
  let lastW = 0;
  const run = (force = true) => {
    const w = Math.floor(container.clientWidth);
    if (!w || (!force && w === lastW)) return;
    lastW = w;
    container.replaceChildren(draw(Math.max(260, w)));
  };
  new ResizeObserver(() => run(false)).observe(container);
  return () => run(true);
}

function linear(d0, d1, r0, r1) {
  const k = (r1 - r0) / (d1 - d0 || 1);
  return (v) => r0 + (v - d0) * k;
}

function niceTicks(lo, hi, n = 5) {
  const span = hi - lo || 1;
  const step0 = span / n;
  const mag = 10 ** Math.floor(Math.log10(step0));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((v) => v >= step0) ?? 10 * mag;
  const out = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-12; v += step) out.push(+v.toPrecision(10));
  return out;
}

const tickText = (v) => (Math.abs(v) < 1e-12 ? "0" : String(+v.toPrecision(4)));

// ---------------------------------------------------------------------------
// Dot-and-interval chart (rows stacked; label above each row so it fits phones).

function dotIntervalChart(rows, { ref = null, refLabel = "", width, xLabel }) {
  // Each row: label line, value line (the manuscript's text), then the dot and interval,
  // so no text ever sits on a mark and nothing is clipped at phone width.
  const padL = 12, padR = 16, rowH = 62, top = 28, bottom = 40;
  const vals = rows.flatMap((r) => [r.lo ?? r.est, r.hi ?? r.est, r.est]).concat(ref === null ? [] : [ref]);
  const lo = Math.min(0, ...vals), hi = Math.max(...vals) * 1.05;
  const x = linear(lo, hi, padL + 6, width - padR);
  const height = top + rows.length * rowH + bottom;
  const svg = s("svg", { width, height, viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": `${xLabel}: ` + rows.map((r) => `${r.label} ${r.text}`).join("; ") });
  const ticks = niceTicks(lo, hi, width < 420 ? 3 : 5);
  for (const t of ticks) {
    svg.append(s("line", { class: "gridline", x1: x(t), x2: x(t), y1: top - 6, y2: height - bottom + 4 }));
    svg.append(s("text", { class: "svg-ink2", x: x(t), y: height - bottom + 20, "text-anchor": "middle", "font-size": 12 }, tickText(t)));
  }
  svg.append(s("text", { class: "svg-ink2", x: width / 2, y: height - 6, "text-anchor": "middle", "font-size": 12 }, xLabel));
  if (ref !== null) {
    svg.append(s("line", { class: "refline", x1: x(ref), x2: x(ref), y1: top - 14, y2: height - bottom + 4 }));
    svg.append(s("text", { class: "svg-ink2 halo", x: Math.min(x(ref) + 4, width - padR - 4), y: top - 14, "text-anchor": x(ref) > width * 0.6 ? "end" : "start", "font-size": 12 }, refLabel));
  }
  rows.forEach((r, i) => {
    const y = top + i * rowH + 44;
    svg.append(s("text", { class: "svg-ink2 halo", x: padL, y: y - 28, "font-size": 12 }, r.label));
    svg.append(s("text", { class: "svg-ink halo", x: padL, y: y - 12, "font-size": 12.5, "font-weight": 600 }, r.text));
    const cls = r.series ?? "s1";
    if (r.lo !== null && r.lo !== undefined) svg.append(s("line", { class: `ci ${cls}`, x1: x(r.lo), x2: x(r.hi), y1: y, y2: y }));
    svg.append(s("circle", { class: cls, cx: x(r.est), cy: y, r: 5, css: { stroke: "var(--surface)" }, "stroke-width": 2 }));
  });
  return svg;
}

function dataTable(caption, head, rows) {
  // The scroll region becomes a tab stop only while the table is open.
  const onToggle = (ev) => {
    const region = ev.currentTarget.querySelector(".table-scroll");
    if (ev.currentTarget.open) region.setAttribute("tabindex", "0");
    else region.removeAttribute("tabindex");
  };
  return h("details", { ontoggle: onToggle },
    h("summary", { text: `Data table: ${caption}` }),
    h("div", { class: "table-scroll", role: "region", "aria-label": `${caption} data`, id: `dt-${caption.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}` },
      h("table", {}, h("thead", {}, h("tr", {}, head.map((c) => h("th", { scope: "col", text: c })))),
        h("tbody", {}, rows.map((r) => h("tr", {}, r.map((c, i) => (i === 0 ? h("th", { scope: "row", text: c }) : h("td", { text: c })))))))));
}

// ---------------------------------------------------------------------------
// Network drawings.

const congRamp = ["--cong-0", "--cong-1", "--cong-2", "--cong-3", "--cong-4"];
function congColour(v, max) {
  const t = max > 0 ? Math.min(1, Math.max(0, v / max)) : 0;
  return `var(${congRamp[Math.min(4, Math.floor(t * 4.999))]})`;
}

function rampLegend(label, maxText) {
  return h("div", { class: "ramp" }, h("span", { text: `${label}: 0` }), congRamp.map((c, i) => h("span", { class: `sw c${i}` })), h("span", { text: maxText }));
}

const BRAESS_POS = { s: [0.1, 0.5], A: [0.5, 0.15], B: [0.5, 0.85], t: [0.9, 0.5] };

function drawLink(g, x1, y1, x2, y2, width, colour, moving, offset = 0) {
  const dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy) || 1;
  const ox = (-dy / len) * offset, oy = (dx / len) * offset;
  const shrink = 14 / len;
  const a = [x1 + dx * shrink + ox, y1 + dy * shrink + oy], b = [x2 - dx * shrink + ox, y2 - dy * shrink + oy];
  g.append(s("line", { class: "link-base", x1: a[0], y1: a[1], x2: b[0], y2: b[1], css: { stroke: colour }, "stroke-width": width }));
  if (moving) g.append(s("line", { class: "flowdash moving", x1: a[0], y1: a[1], x2: b[0], y2: b[1] }));
  // arrowhead
  const ux = dx / len, uy = dy / len, bx = b[0], by = b[1];
  g.append(s("path", { d: `M${bx},${by} L${bx - ux * 9 - uy * 5},${by - uy * 9 + ux * 5} L${bx - ux * 9 + uy * 5},${by - uy * 9 - ux * 5} Z`, css: { fill: colour } }));
}

function braessSvg(sweep, point, net, arm, width, maxDelay, maxFlow) {
  const H = Math.round(width * 0.62);
  const svg = s("svg", { width, height: H, viewBox: `0 0 ${width} ${H}`, role: "img" });
  const rec = point[net][arm];
  const names = net === "with_e" ? sweep.links : sweep.links.slice(0, 4);
  const pos = (n) => [BRAESS_POS[n][0] * width, BRAESS_POS[n][1] * H];
  const g = s("g");
  const labels = [];
  names.forEach((name, e) => {
    const [u, v] = sweep.link_ends[e];
    const f = rec.link_flow[e];
    const delay = sweep.cost_B[e] * f;
    const [x1, y1] = pos(u), [x2, y2] = pos(v);
    drawLink(g, x1, y1, x2, y2, 2 + 10 * (f / maxFlow), congColour(delay, maxDelay), f > 1e-9);
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const off = name === "e" ? [16, 4] : [0, my < H / 2 ? -12 : 22];
    labels.push(s("text", { class: "svg-ink halo", x: mx + off[0], y: my + off[1], "text-anchor": name === "e" ? "start" : "middle", "font-size": 12.5 }, `${name}: flow ${f.toFixed(2)}`));
  });
  svg.append(g);
  for (const [n, [px, py]] of Object.entries(BRAESS_POS)) {
    svg.append(s("circle", { class: "node", cx: px * width, cy: py * H, r: 13 }));
    svg.append(s("text", { class: "svg-ink", x: px * width, y: py * H + 4.5, "text-anchor": "middle", "font-size": 13, "font-weight": 600 }, n));
  }
  svg.append(...labels);
  const desc = names.map((n, e) => `link ${n} carries ${rec.link_flow[e].toFixed(2)}`).join(", ");
  svg.setAttribute("aria-label", `Braess network ${net === "with_e" ? "with" : "without"} link e, ${arm} routing at demand ${point.demand}: ${desc}; mean trip time ${rec.mean_trip_time.toFixed(2)}.`);
  return svg;
}

function gridSvg(grid, x, width, maxFlow) {
  const n = grid.n;
  const H = width;
  const pad = 28;
  const svg = s("svg", { width, height: H, viewBox: `0 0 ${width} ${H}`, role: "img" });
  const pos = (i) => [pad + ((i % n) / (n - 1)) * (width - 2 * pad), pad + (Math.floor(i / n) / (n - 1)) * (H - 2 * pad)];
  const g = s("g");
  let maxvc = 0;
  const net = grid.spec;
  for (let e = 0; e < net.tail.length; e++) {
    const vc = x[e] / net.capacity[e];
    maxvc = Math.max(maxvc, vc);
    const [x1, y1] = pos(net.tail[e]), [x2, y2] = pos(net.head[e]);
    drawLink(g, x1, y1, x2, y2, 1.5 + 6 * (x[e] / maxFlow), congColour(vc, 1.5), x[e] > 1e-9, 4);
  }
  svg.append(g);
  for (let i = 0; i < n * n; i++) {
    const [px, py] = pos(i);
    svg.append(s("circle", { class: "node", cx: px, cy: py, r: 6 }));
  }
  svg.setAttribute("aria-label", `Grid seed ${grid.seed}: link colour shows volume over capacity, darkest at 1.5 or more; the most loaded link is at ${maxvc.toFixed(2)} of capacity.`);
  return svg;
}

// ---------------------------------------------------------------------------
// Braess explorer (measured EXP-002 records).

function braessExplorer(r) {
  const sw = r.braess_sweep;
  const pts = sw.points;
  let idx = pts.findIndex((p) => p.demand === 6);
  if (idx < 0) idx = 0;
  let arm = "UE";
  const maxFlow = pts[pts.length - 1].demand;
  let maxDelay = 0;
  for (const p of pts) for (const net of ["with_e", "without_e"]) for (const a of ["FF", "UE", "SO"]) p[net][a].link_flow.forEach((f, e) => { maxDelay = Math.max(maxDelay, sw.cost_B[e] * f); });

  const slider = h("input", { type: "range", min: 0, max: pts.length - 1, step: 1, value: idx, id: "bx-demand" });
  const readout = h("p", { class: "readout", id: "bx-readout" });
  const before = h("div"), after = h("div");
  const chartBox = h("div"), barsBox = h("div");
  const pointText = (p) => `demand ${p.demand}${p.predicted_paradox ? ", inside the predicted paradox interval" : ""}`;

  const update = () => {
    const p = pts[idx];
    slider.setAttribute("aria-valuetext", pointText(p));
    const w = p.without_e[arm].mean_trip_time, wi = p.with_e[arm].mean_trip_time;
    readout.textContent = `At demand ${p.demand} (${p.cell === "sweep" ? "main sweep" : "fine boundary sweep"}), ${arm} mean trip time is ${w.toFixed(2)} without link e and ${wi.toFixed(2)} with it: adding the link ${wi > w + 1e-6 ? "makes the average trip slower" : wi < w - 1e-6 ? "makes the average trip faster" : "leaves the average trip unchanged"}.`;
    drawBefore(); drawAfter(); drawChart(); drawBars();
  };
  const netFigure = (box, net, title) => responsive(box, (W) => h("figure", {},
    h("p", { class: "chart-title", text: title }),
    braessSvg(sw, pts[idx], net, arm, Math.min(W, 520), maxDelay, maxFlow)));
  let drawBefore = () => {}, drawAfter = () => {}, drawChart = () => {}, drawBars = () => {};
  slider.addEventListener("input", () => { idx = Number(slider.value); update(); });

  drawBefore = netFigure(before, "without_e", "Before: without link e");
  drawAfter = netFigure(after, "with_e", "After: with link e");

  drawChart = responsive(chartBox, (W) => {
    const width = W, height = Math.max(240, Math.round(W * 0.42));
    const padL = 48, padR = 14, top = 14, bottom = 42;
    const x = linear(0, 12.25, padL, width - padR);
    const main = pts.filter((p) => p.cell === "sweep");
    const ys = main.flatMap((p) => [p.with_e[arm].mean_trip_time, p.without_e[arm].mean_trip_time]);
    const y = linear(0, Math.max(...ys) * 1.05, height - bottom, top);
    const svg = s("svg", { width, height, viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": `Measured ${arm} mean trip time against demand, with and without link e. The with-link line is above the without-link line between ${sw.paradox_interval.display}.` });
    if (arm === "UE") {
      svg.append(s("rect", { class: "band", x: x(sw.paradox_interval.low), width: x(sw.paradox_interval.high) - x(sw.paradox_interval.low), y: top, height: height - bottom - top }));
    }
    for (const t of niceTicks(0, Math.max(...ys) * 1.05, 4)) {
      svg.append(s("line", { class: "gridline", x1: padL, x2: width - padR, y1: y(t), y2: y(t) }));
      svg.append(s("text", { class: "svg-ink2", x: padL - 6, y: y(t) + 4, "text-anchor": "end", "font-size": 12 }, tickText(t)));
    }
    for (const t of [0, 2, 4, 6, 8, 10, 12]) svg.append(s("text", { class: "svg-ink2", x: x(t), y: height - bottom + 18, "text-anchor": "middle", "font-size": 12 }, String(t)));
    svg.append(s("line", { class: "axisline", x1: padL, x2: width - padR, y1: y(0), y2: y(0) }));
    svg.append(s("text", { class: "svg-ink2", x: (padL + width) / 2, y: height - 6, "text-anchor": "middle", "font-size": 12 }, "Total demand (abstract units)"));
    const path = (net) => main.map((p, i) => `${i ? "L" : "M"}${x(p.demand).toFixed(1)},${y(p[net][arm].mean_trip_time).toFixed(1)}`).join("");
    svg.append(s("path", { class: "line s2", d: path("without_e"), fill: "none" }));
    svg.append(s("path", { class: "line s1", d: path("with_e"), fill: "none" }));
    const p = pts[idx];
    svg.append(s("line", { class: "refline", x1: x(p.demand), x2: x(p.demand), y1: top, y2: height - bottom }));
    for (const [net, cls] of [["without_e", "s2"], ["with_e", "s1"]]) svg.append(s("circle", { class: cls, cx: x(p.demand), cy: y(p[net][arm].mean_trip_time), r: 5, css: { stroke: "var(--surface)" }, "stroke-width": 2 }));
    // pointer selects the nearest measured demand
    const hit = s("rect", { x: padL, y: top, width: width - padL - padR, height: height - bottom - top, fill: "transparent" });
    hit.addEventListener("pointermove", (ev) => {
      const rect = svg.getBoundingClientRect();
      const d = ((ev.clientX - rect.left) / rect.width) * width;
      let best = 0;
      pts.forEach((q, i) => { if (Math.abs(x(q.demand) - d) < Math.abs(x(pts[best].demand) - d)) best = i; });
      if (best !== idx) { idx = best; slider.value = String(idx); update(); }
    });
    svg.append(hit);
    return svg;
  });

  drawBars = responsive(barsBox, (W) => {
    const p = pts[idx];
    const rows = [];
    for (const [net, nm] of [["without_e", "without link e"], ["with_e", "with link e"]]) for (const a of ["FF", "UE", "SO"]) rows.push({ label: `${a}, ${nm}`, v: p[net][a].mean_trip_time, cls: net === "with_e" ? "s1" : "s2" });
    const width = W, rowH = 26, padL = Math.min(150, W * 0.42), padR = 64;
    const height = rows.length * rowH + 10;
    const x = linear(0, Math.max(...rows.map((q) => q.v)) || 1, padL, width - padR);
    const svg = s("svg", { width, height, viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": `Mean trip time at demand ${p.demand} under each routing policy: ` + rows.map((q) => `${q.label} ${q.v.toFixed(2)}`).join("; ") });
    rows.forEach((q, i) => {
      const yy = 6 + i * rowH;
      svg.append(s("text", { class: "svg-ink", x: padL - 8, y: yy + 14, "text-anchor": "end", "font-size": 12.5 }, q.label));
      svg.append(s("rect", { class: q.cls, x: padL, y: yy + 3, width: Math.max(2, x(q.v) - padL), height: 15, rx: 3 }));
      svg.append(s("text", { class: "svg-ink", x: x(q.v) + 6, y: yy + 14, "font-size": 12.5 }, q.v.toFixed(2)));
    });
    return svg;
  });

  const armSeg = seg([["FF", "Free-flow (FF)"], ["UE", "Equilibrium (UE)"], ["SO", "System optimum (SO)"]], arm, (v) => { arm = v; update(); }, "Routing policy");
  const sec = h("section", { id: "explorer", "aria-labelledby": "h-explorer", class: "animate" },
    h("h2", { id: "h-explorer" }, "The Braess network, measured ", tag("measured")),
    h("p", { class: "lede" }, "Four nodes, one origin s and one destination t. Link costs are 10f on a and d, f + 50 on b and c, and f + 10 on the extra link e. Move the demand slider through the 75 demand values of EXP-002 and compare the network before and after adding link e. Every value shown here is read from the committed raw records of the confirmatory run ", h("code", { text: sw.run_id }), "; readouts are rounded to two decimals for display."),
    h("div", { class: "controls" },
      h("label", { class: "grow", for: "bx-demand" }, h("span", { text: "Total demand (EXP-002 sweep points)" }), slider),
      h("div", {}, h("span", { class: "meta", text: "Routing policy " }), armSeg),
      h("div", {}, h("span", { class: "meta", text: "Motion " }), motionToggle())),
    readout,
    h("div", { class: "pair" }, before, after),
    h("div", { class: "key" }, rampLegend("Link congestion delay (flow-dependent part of link time)", `${maxDelay.toFixed(0)} or more`), h("span", { text: "Line width shows link flow; moving dashes show the direction of travel." })),
    h("figure", { class: "chart" },
      h("p", { class: "chart-title", text: "Paired before and after: mean trip time against demand" }),
      h("div", { class: "key" }, h("span", {}, h("i", { class: "k-s2" }), "without link e (before)"), h("span", {}, h("i", { class: "k-s1" }), "with link e (after)"), h("span", {}, h("i", { class: "bandkey" }), `predicted paradox interval ${sw.paradox_interval.display} (UE only)`), h("span", {}, h("i", { class: "dash" }), "selected demand")),
      chartBox,
      h("figcaption", {}, h("strong", { text: "Reading the chart. " }), "Under equilibrium routing the line with link e lies above the line without it exactly inside the shaded interval: there, adding a road makes every traveller slower. The sign agreed with the derivation at 75 of 75 points; the frozen exact check was still contradicted because two estimated boundaries missed by about 1e-5 at the frozen solver tolerance (see EXP-002 below).")),
    h("figure", { class: "chart" },
      h("p", { class: "chart-title", text: "Policy comparison at the selected demand: mean trip time" }),
      barsBox,
      h("figcaption", { text: "Free-flow routing ignores congestion, equilibrium routing lets every traveller minimise their own time, and the system optimum minimises the total. The study's primary metric compares each policy's total travel time with the system optimum on the same network and demand." })),
    dataTable("measured mean trip time by demand", ["Demand", "Cell", "UE without e", "UE with e", "SO without e", "SO with e", "FF without e", "FF with e"],
      pts.map((p) => [String(p.demand), p.cell, ...["UE", "SO", "FF"].flatMap((a) => [p.without_e[a].mean_trip_time.toFixed(2), p.with_e[a].mean_trip_time.toFixed(2)])])));
  update();
  return sec;
}

// ---------------------------------------------------------------------------
// Published results.

function overview(r) {
  const prim = est(r, "EXP-003", 0), lb = est(r, "EXP-003", 1);
  const sf = est(r, "EXP-006", 1);
  const e1 = r.experiments.find((e) => e.id === "EXP-001"), e2 = r.experiments.find((e) => e.id === "EXP-002");
  return h("section", { id: "overview", "aria-labelledby": "h-overview" },
    h("h2", { id: "h-overview", text: "Overview" }),
    h("p", { class: "status-label", text: r.status_label }),
    h("p", { class: "lede", text: r.question }),
    h("div", { class: "tiles" },
      h("div", { class: "tile" }, tag("measured"), h("p", { class: "big", text: fmtEstimate(prim) }),
        h("p", { text: "Median relative excess of equilibrium over system-optimal total travel time, 100 synthetic 6 by 6 grids at twice the saturation demand (primary, EXP-003)." }),
        h("p", { class: "meta", text: `95% bootstrap interval ${prim.interval_display}; one-sided lower bound ${lb.display}, above the 0.01 margin: H0 rejected.` })),
      h("div", { class: "tile" }, tag("measured"), h("p", { class: "big", text: e1.verdict === e2.verdict ? `${e1.verdict}, both` : `${e1.verdict}; ${e2.verdict}` }),
        h("p", { text: "Both exact checks on the Braess network failed their own frozen 1e-6 rule (EXP-001, EXP-002)." }),
        h("p", { class: "meta", text: "Residuals of 1e-5 to 6e-5 at the frozen solver tolerance. An exploratory rerun at 1e-10 met the rule; the frozen verdicts stand." })),
      h("div", { class: "tile" }, tag("measured"), h("p", { class: "big", text: fmtEstimate(sf) }),
        h("p", { text: "Equilibrium excess on one real test network, Sioux Falls, at rho = 2 (EXP-006): the direction replicates, by a small margin." }),
        h("p", { class: "meta", text: "One deterministic network, no interval; its maintainers describe it as not realistic." }))),
    h("ul", { class: "legend-labels", "aria-label": "Evidence labels used on this page" },
      h("li", {}, tag("measured"), h("span", { text: "confirmatory results from the frozen protocol" })),
      h("li", {}, tag("exploratory"), h("span", { text: "defined after results were seen; changes no verdict" })),
      h("li", {}, tag("assumption"), h("span", { text: "modelling choices and conventions, not measurements" })),
      h("li", {}, tag("sandbox"), h("span", { text: "computed in your browser; not a research result" }))));
}

function charts(r) {
  const cells = r.grid_cells;
  const ueBox = h("div"), pairBox = h("div"), sensBox = h("div"), compBox = h("div");
  responsive(ueBox, (W) => dotIntervalChart(cells.map((c) => ({ label: `${c.size}, rho = ${c.rho}`, est: c.R_UE.estimate, lo: c.R_UE.ci_low, hi: c.R_UE.ci_high, text: `${c.R_UE.display} ${c.R_UE.interval_display}` })), { ref: 0.01, refLabel: "margin 0.01", width: W, xLabel: "Median R(UE) with 95% bootstrap interval" }));
  responsive(pairBox, (W) => dotIntervalChart(cells.map((c) => ({ label: `${c.size}, rho = ${c.rho}`, est: c.paired_FF_minus_UE.estimate, lo: c.paired_FF_minus_UE.ci_low, hi: c.paired_FF_minus_UE.ci_high, series: "s2", text: `${c.paired_FF_minus_UE.display} ${c.paired_FF_minus_UE.interval_display}` })), { width: W, xLabel: "Paired median R(FF) - R(UE) with 95% interval" }));
  responsive(sensBox, (W) => dotIntervalChart(r.sensitivity.map((q) => ({ label: `${q.label}, n = ${q.n_used}${q.label.includes(q.decision_role) ? "" : `; ${q.decision_role}`}`, est: q.estimate, lo: q.ci_low, hi: q.ci_high, series: q.decision_role === "different decision" ? "s2" : q.decision_role === "no decision" ? "s3" : "s1", text: `${q.display} ${q.interval_display}` })), { ref: 0.01, refLabel: "margin 0.01", width: W, xLabel: "Median R(UE), 6 by 6, rho = 2, with 95% interval" }));
  responsive(compBox, (W) => {
    const rows = [];
    for (const sc of r.compliance) for (const a of sc.arms) if (a.arm !== "FF") rows.push({ label: `capacity ${sc.capacity_scale}${sc.confirmatory ? " (confirmatory)" : " (descriptive)"}, ${a.arm}`, est: a.estimate, lo: a.ci_low, hi: a.ci_high, series: sc.confirmatory ? "s1" : "s3", text: a.interval_display ? `${a.display} ${a.interval_display}` : `${a.display} (SO by construction)` });
    return dotIntervalChart(rows, { ref: 0.01, refLabel: "margin 0.01", width: W, xLabel: "Median R(MIX(c)) with 95% interval" });
  });
  const ff = r.compliance.map((sc) => sc.arms.find((a) => a.arm === "FF"));
  return h("div", {},
    h("div", { class: "pair" },
      h("figure", { class: "chart" }, h("p", { class: "chart-title" }, "Equilibrium excess by grid size and demand (EXP-003) ", tag("measured")), ueBox,
        h("figcaption", { text: "The excess grows with demand and is below the 0.01 margin at rho = 1 in both sizes; the primary cell is 6x6 at rho = 2. Each row is 100 instances." }),
        dataTable("R(UE) by cell", ["Cell", "Median R(UE)", "95% interval", "Median R(FF)", "95% interval"], cells.map((c) => [`${c.size}, rho = ${c.rho}`, c.R_UE.display, c.R_UE.interval_display, c.R_FF.display, c.R_FF.interval_display]))),
      h("figure", { class: "chart" }, h("p", { class: "chart-title" }, "Free-flow minus equilibrium, paired on the same instances ", tag("measured")), pairBox,
        h("figcaption", { text: "Ignoring congestion costs far more than the equilibrium inefficiency once demand is congested; at rho = 1 the policies are close." }),
        dataTable("paired R(FF) - R(UE)", ["Cell", "Paired median", "95% interval"], cells.map((c) => [`${c.size}, rho = ${c.rho}`, c.paired_FF_minus_UE.display, c.paired_FF_minus_UE.interval_display])))),
    h("div", { class: "pair" },
      h("figure", { class: "chart" }, h("p", { class: "chart-title" }, "Sensitivity of the primary result ", tag("measured")), sensBox,
        h("figcaption", { text: "Solver tolerance and demand calibration leave the decision unchanged. With linear-in-flow costs (S2) the excess falls below the margin, a different decision and a scope limit. The Frank-Wolfe reference converged on only 7 of 100 instances and supports no decision." }),
        dataTable("sensitivity", ["Cell", "n used", "Median", "One-sided lower bound", "95% interval", "Role"], r.sensitivity.map((q) => [q.label, String(q.n_used), q.display, q.lower_display, q.interval_display, q.decision_role]))),
      h("figure", { class: "chart" }, h("p", { class: "chart-title" }, "Partial system-optimal compliance (EXP-004) ", tag("measured")), compBox,
        h("figcaption", { text: "Routing a larger share c of travellers system-optimally lowered the median excess at every step at capacity 1.0 (confirmatory); scales 0.8 and 1.2 are descriptive. MIX(0) is equilibrium and MIX(1) the optimum by construction." }),
        dataTable("compliance", ["Capacity scale", "Arm", "Median R", "95% interval"], r.compliance.flatMap((sc) => sc.arms.map((a) => [String(sc.capacity_scale), a.arm, a.display, a.interval_display ?? "none (identity)"]))),
        h("p", { class: "meta", text: `Free-flow routing on the same instances: median R(FF) ${ff.map((a, i) => `${a.display} ${a.interval_display} at capacity ${r.compliance[i].capacity_scale}`).join("; ")}.` }))));
}

function experimentPanel(e) {
  return h("article", { class: `panel ${e.label}`, "aria-labelledby": `h-${e.id}` },
    h("h3", { id: `h-${e.id}` }, `${e.id}: ${e.title} `, tag(e.label)),
    h("p", {}, h("span", { class: "badge", text: e.verdict }), " ", h("span", { class: "meta", text: e.label === "measured" ? "verdict under the frozen rule" : "not a confirmatory verdict" })),
    h("p", { class: "meta", text: `Status: ${e.status}` }),
    h("div", { class: "table-scroll", role: "region", "aria-label": `${e.id} estimates`, tabindex: 0, id: `est-${e.id}` },
      h("table", { class: "stack" }, h("thead", {}, h("tr", {}, h("th", { scope: "col", text: "Quantity" }), h("th", { scope: "col", text: "Value" }), h("th", { scope: "col", text: "Interval" }))),
        h("tbody", {}, e.estimates.map((x) => h("tr", {}, h("th", { scope: "row", text: x.label }), h("td", { "data-label": "Value", text: fmtEstimate(x) }), h("td", { "data-label": "Interval", text: fmtInterval(x) })))))),
    e.notes.map((n) => h("p", { class: "note", text: n })),
    h("p", { class: "meta" }, "Report: ", h("code", { text: e.report_path }), e.claim_ids.length ? ` · Claims: ${e.claim_ids.join(", ")}` : ""));
}

function published(r) {
  const frag = document.createDocumentFragment();
  frag.append(overview(r), braessExplorer(r));
  frag.append(h("section", { id: "results", "aria-labelledby": "h-results" },
    h("h2", { id: "h-results", text: "Published results" }),
    h("p", { class: "note" }, "Every number below is printed exactly as the manuscript prints it, from the committed results of the confirmatory runs at revision ", h("code", { text: r.code_revision.slice(0, 7) }), " (exploratory runs at ", h("code", { text: r.exploratory_code_revision.slice(0, 7) }), "). Contradicted, null and exploratory results are shown with the same weight as supported ones. Nothing here comes from the sandbox."),
    charts(r),
    h("div", { class: "exp-grid" }, r.experiments.map(experimentPanel))));
  frag.append(h("section", { id: "assumptions", "aria-labelledby": "h-assumptions" },
    h("h2", { id: "h-assumptions" }, "Assumptions ", tag("assumption")),
    h("p", { class: "note", text: "These are modelling choices and conventions of the study. They are inputs, not findings." }),
    h("dl", { class: "assumptions" }, r.assumptions.map((a) => h("div", {}, h("dt", { text: a.name }), h("dd", {}, a.value, " ", h("span", { class: "meta", text: `(${a.source})` })))))));
  frag.append(h("section", { id: "method", "aria-labelledby": "h-method" },
    h("h2", { id: "h-method", text: "Method and limitations" }),
    h("p", { class: "lede", text: "The study protocol and six experiment protocols were frozen by the owner before any confirmatory instance was solved, with SHA-256 hashes recorded. Each grid instance is the independent unit; all policies are solved on the same network and demand, and intervals are percentile bootstrap intervals over instances (10,000 resamples). Everything labelled exploratory was defined after the confirmatory results existed and changes no frozen verdict." }),
    h("h3", { text: "Limitations" }),
    h("ul", {}, r.limitations.map((l) => h("li", { text: l }))),
    h("details", {}, h("summary", { text: "Source files and SHA-256 hashes" }),
      h("ul", { class: "meta" }, r.sources.map((src) => h("li", {}, h("code", { text: src.path }), " ", h("code", { text: src.sha256.slice(0, 16) })))))));
  return frag;
}

// ---------------------------------------------------------------------------
// Sandbox.

function sandbox(sb) {
  const scenario = document.getElementById("sb-scenario");
  const demand = document.getElementById("sb-demand");
  const demandLabel = document.getElementById("sb-demand-label");
  const mix = document.getElementById("sb-mix");
  const run = document.getElementById("sb-run");
  const cancel = document.getElementById("sb-cancel");
  const reset = document.getElementById("sb-reset");
  const out = document.getElementById("sb-out");
  const progress = document.getElementById("sb-progress");
  const detail = document.getElementById("sb-detail");

  const options = [["braess-e", "Braess network, with link e"], ["braess", "Braess network, without link e"], ...sb.grids.map((g) => [`grid-${g.seed}`, `4 by 4 grid, seed ${g.seed}`])];
  scenario.replaceChildren(...options.map(([v, t]) => h("option", { value: v, text: t })));

  const isGrid = () => scenario.value.startsWith("grid");
  const setRange = () => {
    if (isGrid()) { Object.assign(demand, { min: 0.25, max: 3, step: 0.25 }); demand.value = "2"; }
    else { Object.assign(demand, { min: 0.25, max: 12, step: 0.25 }); demand.value = "6"; }
    labelDemand();
  };
  const labelDemand = () => {
    const v = Number(demand.value);
    const t = isGrid() ? `Demand level rho = ${v}` : `Total demand = ${v}`;
    demandLabel.textContent = t;
    demand.setAttribute("aria-valuetext", t);
  };
  scenario.addEventListener("change", setRange);
  demand.addEventListener("input", labelDemand);

  let worker = null;
  let job = 0;
  let last = null;
  let view = "UE";
  const startWorker = () => {
    worker = new Worker(new URL("./sandbox_worker.js", import.meta.url), { type: "module" });
    worker.onmessage = (ev) => {
      const m = ev.data;
      if (m.id !== job) return;
      if (m.type === "progress") { progress.textContent = `Running: ${m.sweeps} solver sweeps so far.`; return; }
      run.disabled = false; cancel.disabled = true;
      if (m.type === "done") { last = { ...pending, arms: m.arms }; progress.textContent = ""; render(); }
      if (m.type === "cancelled") { progress.textContent = ""; out.textContent = "Sandbox run cancelled; no output."; }
      if (m.type === "error") { progress.textContent = ""; out.textContent = `Sandbox run stopped with an error: ${m.message}`; }
    };
  };
  startWorker();

  let pending = null;
  run.addEventListener("click", () => {
    const v = Number(demand.value);
    const c = Number(mix.value);
    let network, dem, label, grid = null;
    if (isGrid()) {
      grid = sb.grids.find((g) => `grid-${g.seed}` === scenario.value);
      network = grid.spec;
      dem = grid.od.map(([o, d], k) => ({ o, d, q: v * grid.d_ref * grid.weights[k] }));
      label = `4 by 4 grid, seed ${grid.seed}, rho = ${v}`;
    } else {
      const withE = scenario.value === "braess-e";
      network = withE ? sb.raw.braess.with_e : sb.raw.braess.without_e;
      dem = [{ o: 0, d: 3, q: v }];
      label = `Braess network ${withE ? "with" : "without"} link e, demand ${v}`;
    }
    job += 1;
    pending = { label, grid, withE: scenario.value === "braess-e", demand: v, c, network };
    out.textContent = "";
    detail.replaceChildren();
    progress.textContent = "Running.";
    run.disabled = true; cancel.disabled = false;
    worker.postMessage({ type: "run", id: job, network, demand: dem, mixC: c });
  });
  cancel.addEventListener("click", () => { worker.postMessage({ type: "cancel" }); });
  reset.addEventListener("click", () => {
    worker.terminate(); job += 1; startWorker();
    scenario.value = "braess-e"; mix.value = "0.5"; setRange();
    out.textContent = ""; progress.textContent = ""; detail.replaceChildren(); last = null; view = "UE";
    run.disabled = false; cancel.disabled = true;
  });
  setRange();

  function render() {
    const L = last;
    const arms = [["FF", "FF"], ["UE", "UE"], ["SO", "SO"], ["MIX", `MIX(${L.c})`]];
    const fmt = (v) => (Math.abs(v) >= 1000 ? v.toFixed(0) : v.toFixed(3));
    const allConv = arms.every(([k]) => L.arms[k].converged);
    out.textContent = `Sandbox output (${L.label}): R(UE) = ${L.arms.UE.R.toFixed(4)}, R(FF) = ${L.arms.FF.R.toFixed(4)}, R(MIX(${L.c})) = ${L.arms.MIX.R.toFixed(4)}${allConv ? "; every solve converged" : "; at least one solve reached the sweep cap and is marked nonconverged"}.`;
    const netBox = h("div");
    const maxFlow = Math.max(...arms.flatMap(([k]) => L.arms[k].x), 1e-9);
    const draw = responsive(netBox, (W) => {
      const width = Math.min(W, 460);
      const x = L.arms[view].x;
      if (L.grid) return gridSvg(L.grid, x, width, maxFlow);
      const names = L.withE ? ["a", "b", "c", "d", "e"] : ["a", "b", "c", "d"];
      const ends = [["s", "A"], ["s", "B"], ["A", "t"], ["B", "t"], ["A", "B"]];
      const Bc = L.network.B;
      const fake = { links: names, link_ends: ends, cost_B: Bc };
      const point = { demand: L.demand, with_e: {}, without_e: {} };
      const key = L.withE ? "with_e" : "without_e";
      point[key][view] = { link_flow: x, mean_trip_time: L.arms[view].tstt / L.demand };
      return braessSvg({ ...fake, links: ["a", "b", "c", "d", "e"] }, point, key, view, width, Math.max(...x.map((f, e) => Bc[e] * f), 1e-9), maxFlow);
    });
    const viewSeg = seg(arms.map(([k, t]) => [k, t]), view, (v) => { view = v; draw(); }, "Policy drawn");
    detail.replaceChildren(h("div", { class: "panel sandbox-out" },
      h("p", {}, tag("sandbox"), " ", h("span", { class: "meta", text: L.label })),
      h("div", { class: "table-scroll", role: "region", "aria-label": "Sandbox output table", tabindex: 0, id: "sb-table" },
        h("table", {}, h("thead", {}, h("tr", {}, ["Policy", "Total travel time", "R (relative to SO)", "Solver sweeps", "Final relative gap", "Converged"].map((c) => h("th", { scope: "col", text: c })))),
          h("tbody", {}, arms.map(([k, t]) => {
            const a = L.arms[k];
            return h("tr", {}, h("th", { scope: "row", text: t }), h("td", { text: fmt(a.tstt) }), h("td", { text: a.R.toFixed(4) }), h("td", { text: String(a.iterations) }), h("td", { text: a.relGap === null ? "not iterative" : a.relGap.toExponential(1) }), h("td", { text: a.converged ? "yes" : "no (sweep cap)" }));
          })))),
      h("div", { class: "controls" }, h("div", {}, h("span", { class: "meta", text: "Draw the network under " }), viewSeg), h("div", {}, h("span", { class: "meta", text: "Motion " }), motionToggle())),
      h("div", { class: "animate" }, netBox),
      L.grid ? rampLegend("Volume over capacity", "1.5 or more") : rampLegend("Congestion delay", "the largest on this drawing"),
      h("p", { class: "note", text: "Solved by the browser port at relative gap 1e-6 with at most 20,000 sweeps, the research solver settings. Units: veh min per hour on grids, abstract units on the Braess network." })));
  }
}

// ---------------------------------------------------------------------------

async function main() {
  const host = document.getElementById("published");
  try {
    const r = await loadResults();
    host.replaceChildren(published(r));
  } catch (e) {
    host.replaceChildren(h("div", { role: "alert", class: "panel error" },
      h("h2", { text: "Results unavailable" }),
      h("p", { text: "The published results file failed validation, so no numbers are shown." }),
      h("p", {}, h("code", { text: e instanceof ResultsError ? e.message : "results could not be loaded" }))));
  }
  try {
    const res = await fetch("./data/sandbox.json", { cache: "no-store" });
    if (!res.ok) throw new EngineError(`sandbox data HTTP ${res.status}`);
    const raw = await res.json();
    const sb = validateSandbox(raw);
    sb.raw = raw;
    sandbox(sb);
  } catch (e) {
    document.getElementById("sb-controls").replaceChildren(h("p", { role: "alert", class: "panel error", text: `The sandbox is unavailable: its network file failed validation (${e instanceof Error ? e.message : "unknown error"}).` }));
  }
}

main();
