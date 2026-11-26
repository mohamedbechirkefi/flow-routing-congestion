// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// Hero illustration: a schematic Braess network drawn as a route map. Travellers
// split over two routes, then link e opens and everyone takes it. It is an
// illustration, not study data: it shows no number and reads no result file.
// Motion: Web Animations API on transform and opacity only; with reduced motion
// the final frame is drawn at once and nothing animates.

const SVGNS = "http://www.w3.org/2000/svg";
const EASE_OUT = "cubic-bezier(0.23, 1, 0.32, 1)";
const EASE_IN_OUT = "cubic-bezier(0.77, 0, 0.175, 1)";

function s(tag, attrs = {}, ...kids) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
  for (const c of kids) el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  return el;
}

// Stations and link geometry, 45-degree schematic. Short links a and d have a
// time that grows with traffic; long links b and c have a fixed time.
const P = { s: [60, 190], A: [240, 70], B: [400, 290], t: [540, 190] };
const LINKS = {
  a: [P.s, [180, 70], P.A],
  c: [P.A, [420, 70], P.t],
  b: [P.s, [160, 290], P.B],
  d: [P.B, [440, 290], P.t],
  // e: down from A, then 45 degrees to B.
  e: [P.A, [240, 130], P.B],
};

const ROUTES = {
  upper: [...LINKS.a, ...LINKS.c.slice(1)],
  lower: [...LINKS.b, ...LINKS.d.slice(1)],
  zig: [...LINKS.a, ...LINKS.e.slice(1), ...LINKS.d.slice(1)],
};

const pathD = (pts) => pts.map(([x, y], i) => `${i ? "L" : "M"}${x},${y}`).join(" ");

function routeKeyframes(pts) {
  const lens = [0];
  for (let i = 1; i < pts.length; i++) lens.push(lens[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const total = lens[lens.length - 1];
  const frames = pts.map(([x, y], i) => ({ transform: `translate(${x}px, ${y}px)`, offset: lens[i] / total }));
  frames[0].opacity = 0; frames[1].opacity = 1;
  frames[frames.length - 1].opacity = 0;
  if (frames.length > 2) frames[frames.length - 2].opacity = 1;
  return frames;
}

export function mountHero(host, replayButton, reduceMotion) {
  const W = 660, H = 340;
  const svg = s("svg", { viewBox: `0 0 ${W} ${H}`, class: "hero-svg", role: "img", "aria-label": "Illustration, not study data: a four-station route map from s to t. Travellers first split over an upper route through A and a lower route through B. Then a new link e from A to B opens, every traveller takes the route s, A, B, t, and the two links whose time grows with traffic jam." });
  const layer = (cls) => { const g = s("g", { class: cls }); svg.append(g); return g; };
  const gLines = layer("h-lines"), gHot = layer("h-hot"), gE = layer("h-e"), gDots = layer("h-dots"), gSt = layer("h-stations"), gLab = layer("h-labels");

  const line = (name, cls) => s("path", { d: pathD(LINKS[name]), class: `h-link ${cls}` });
  const base = { a: line("a", "var"), b: line("b", "fixed"), c: line("c", "fixed"), d: line("d", "var") };
  for (const k of ["a", "b", "c", "d"]) gLines.append(base[k]);
  const hot = { a: line("a", "jam"), d: line("d", "jam") };
  gHot.append(hot.a, hot.d);
  const eLine = line("e", "new");
  gE.append(eLine);
  const plate = s("g", { class: "h-plate" },
    s("rect", { x: 290, y: 100, width: 150, height: 38, rx: 7 }),
    s("text", { x: 365, y: 125, "text-anchor": "middle" }, "New road opens"));
  gE.append(plate);

  const stations = [];
  for (const [name, [x, y]] of Object.entries(P)) {
    const big = name === "s" || name === "t";
    const g = s("g", { class: "h-station", transform: `translate(${x} ${y})` },
      s("circle", { r: big ? 16 : 13, class: big ? "ring big" : "ring" }),
      s("text", { y: 5, "text-anchor": "middle", class: "h-st-name" }, name));
    gSt.append(g);
    stations.push(g);
  }
  const lab = (x, y, t) => gLab.append(s("text", { x, y, class: "h-lab", "text-anchor": "middle" }, t));
  lab(130, 58, "a"); lab(340, 58, "c"); lab(270, 312, "b"); lab(470, 312, "d"); lab(340, 212, "e");
  lab(60, 236, "origin");
  gLab.append(s("text", { x: 562, y: 196, class: "h-lab" }, "destination"));

  host.replaceChildren(svg);

  const all = [];
  const play = (el, frames, opts) => { const a = el.animate(frames, { fill: "both", ...opts }); all.push(a); return a; };
  const dotPool = [];
  for (let i = 0; i < 18; i++) {
    const c = s("circle", { r: 6, class: "h-dot" });
    c.style.opacity = "0";
    gDots.append(c);
    dotPool.push(c);
  }

  // Final frame: link e open, a and d jammed, travellers queued on the jammed links.
  const finalFrame = () => {
    for (const a of all) a.cancel();
    all.length = 0;
    for (const el of [...Object.values(base), ...stations]) el.style.opacity = "1";
    for (const el of [base.b, base.c]) el.style.opacity = "0.35";
    hot.a.style.opacity = "1"; hot.d.style.opacity = "1"; eLine.style.opacity = "1"; plate.style.opacity = "1";
    const spots = [[90, 160], [120, 130], [150, 100], [190, 70], [215, 70], [240, 100], [280, 170], [320, 210], [360, 250], [420, 290], [460, 270], [490, 240], [515, 215]];
    dotPool.forEach((d, i) => {
      if (i < spots.length) { d.style.transform = `translate(${spots[i][0]}px, ${spots[i][1]}px)`; d.style.opacity = "1"; }
      else d.style.opacity = "0";
    });
  };

  const sequence = () => {
    for (const a of all) a.cancel();
    all.length = 0;
    for (const el of [...Object.values(base), ...Object.values(hot), eLine, plate, ...stations]) { el.style.opacity = ""; el.style.transform = ""; }
    for (const d of dotPool) { d.style.opacity = "0"; d.style.transform = ""; }
    // 1. The map draws in: lines, then stations with a short stagger.
    Object.values(base).forEach((el, i) => play(el, [{ opacity: 0 }, { opacity: 1 }], { duration: 420, delay: i * 60, easing: EASE_OUT }));
    stations.forEach((el, i) => play(el, [{ opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1 }], { duration: 360, delay: 240 + i * 50, easing: EASE_OUT }));
    for (const el of [...Object.values(hot), eLine, plate]) el.style.opacity = "0";
    // 2. Before: travellers alternate between the upper and lower routes.
    const t1 = 700, trip1 = 2000, gap = 260, n1 = 9;
    for (let i = 0; i < n1; i++) {
      play(dotPool[i], routeKeyframes(i % 2 ? ROUTES.lower : ROUTES.upper), { duration: trip1, delay: t1 + i * gap, easing: "linear", fill: "none" });
    }
    // 3. The new road opens.
    const t2 = t1 + n1 * gap + trip1 - 600;
    play(plate, [{ opacity: 0, transform: "translateY(8px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 320, delay: t2, easing: EASE_OUT });
    play(eLine, [{ opacity: 0 }, { opacity: 1 }], { duration: 480, delay: t2 + 120, easing: EASE_OUT });
    // 4. After: every traveller takes s, A, B, t; the shared links jam, b and c empty.
    const t3 = t2 + 700, trip2 = 2900, n2 = dotPool.length - n1;
    for (let i = 0; i < n2; i++) play(dotPool[n1 + i], routeKeyframes(ROUTES.zig), { duration: trip2, delay: t3 + i * 200, easing: "linear", fill: "none" });
    play(hot.a, [{ opacity: 0 }, { opacity: 1 }], { duration: 900, delay: t3 + 300, easing: EASE_IN_OUT });
    play(hot.d, [{ opacity: 0 }, { opacity: 1 }], { duration: 900, delay: t3 + 1500, easing: EASE_IN_OUT });
    for (const el of [base.b, base.c]) play(el, [{ opacity: 1 }, { opacity: 0.35 }], { duration: 900, delay: t3 + 600, easing: EASE_IN_OUT, fill: "forwards" });
    const end = t3 + (n2 - 1) * 200 + trip2;
    const last = play(svg, [{ opacity: 1 }, { opacity: 1 }], { duration: end });
    last.finished.then(finalFrame, () => {});
  };

  replayButton.addEventListener("click", () => (reduceMotion() ? finalFrame() : sequence()));
  if (reduceMotion()) finalFrame(); else sequence();
  return { stop: finalFrame };
}
