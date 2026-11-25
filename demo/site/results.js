// SPDX-License-Identifier: LicenseRef-FLOW-NC-Research-1.0
// Published results: loaded from data/results.json, which scripts/export_demo_data.py
// writes from committed results only. Plain-JavaScript port of the shared template's
// fail-closed loader: any missing or malformed field means no numbers are shown.
// The FLOW extensions (braess_sweep, grid_cells, sensitivity, compliance) are validated
// with the same rule.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;
export const LABELS = ["measured", "exploratory"];

export class ResultsError extends Error {}

function obj(v, where) {
  if (typeof v !== "object" || v === null || Array.isArray(v)) throw new ResultsError(`${where}: expected an object`);
  return v;
}

function str(o, k, where) {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  return v;
}

function num(o, k, where, nullable = false) {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) throw new ResultsError(`${where}.${k}: expected a finite number`);
  return v;
}

function bool(o, k, where) {
  if (typeof o[k] !== "boolean") throw new ResultsError(`${where}.${k}: expected a boolean`);
  return o[k];
}

function arr(o, k, where) {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o, k, where) {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function numArr(o, k, where, len) {
  const a = arr(o, k, where);
  if (len !== undefined && a.length !== len) throw new ResultsError(`${where}.${k}: expected ${len} values`);
  return a.map((v, i) => {
    if (typeof v !== "number" || !Number.isFinite(v)) throw new ResultsError(`${where}.${k}[${i}]: expected a finite number`);
    return v;
  });
}

function optStr(o, k, where) {
  const v = o[k];
  if (v === undefined || v === null) return null;
  if (typeof v !== "string" || v.length === 0) throw new ResultsError(`${where}.${k}: expected a string or null`);
  return v;
}

export function estimate(v, where) {
  const o = obj(v, where);
  const e = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where),
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: optStr(o, "display", where),
    interval_display: optStr(o, "interval_display", where),
    interval_note: optStr(o, "interval_note", where),
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) throw new ResultsError(`${where}: interval must have both bounds or neither`);
  if (e.ci_low !== null && e.ci_low > e.ci_high) throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  if (e.ci_low !== null && (e.ci_level === null || e.ci_level <= 0 || e.ci_level >= 1)) throw new ResultsError(`${where}: interval needs a level in (0, 1)`);
  if (e.ci_low !== null && e.interval_display === null) throw new ResultsError(`${where}: interval without display text`);
  // FLOW rule: every published number is shown as the manuscript prints it.
  if (e.display === null) throw new ResultsError(`${where}.display: required for FLOW estimates`);
  return e;
}

function braessSweep(v) {
  const w = "braess_sweep";
  const o = obj(v, w);
  const links = strArr(o, "links", w);
  if (links.join() !== "a,b,c,d,e") throw new ResultsError(`${w}.links: expected the five Braess links`);
  const cost_A = numArr(o, "cost_A", w, 5);
  const cost_B = numArr(o, "cost_B", w, 5);
  const ends = arr(o, "link_ends", w);
  if (ends.length !== 5) throw new ResultsError(`${w}.link_ends: expected 5 pairs`);
  const pi = obj(o.paradox_interval, `${w}.paradox_interval`);
  const interval = { low: num(pi, "low", w), high: num(pi, "high", w), display: str(pi, "display", w) };
  if (!(interval.low < interval.high)) throw new ResultsError(`${w}.paradox_interval: low must be below high`);
  const points = arr(o, "points", w).map((p, i) => {
    const wp = `${w}.points[${i}]`;
    const q = obj(p, wp);
    const net = (key, n) => {
      const m = obj(q[key], `${wp}.${key}`);
      const out = {};
      for (const arm of ["FF", "UE", "SO"]) {
        const r = obj(m[arm], `${wp}.${key}.${arm}`);
        const flows = numArr(r, "link_flow", `${wp}.${key}.${arm}`, n);
        if (flows.some((f) => f < -1e-9)) throw new ResultsError(`${wp}.${key}.${arm}: negative link flow`);
        out[arm] = { tstt: num(r, "tstt", wp), mean_trip_time: num(r, "mean_trip_time", wp), link_flow: flows };
      }
      return out;
    };
    const demand = num(q, "demand", wp);
    if (demand <= 0) throw new ResultsError(`${wp}.demand: must be positive`);
    return { demand, cell: str(q, "cell", wp), predicted_paradox: bool(q, "predicted_paradox", wp), with_e: net("with_e", 5), without_e: net("without_e", 4) };
  });
  if (points.length < 2) throw new ResultsError(`${w}.points: too few points`);
  for (let i = 1; i < points.length; i++) {
    if (!(points[i].demand > points[i - 1].demand)) throw new ResultsError(`${w}.points: demands must increase`);
  }
  return {
    experiment_id: str(o, "experiment_id", w),
    run_id: str(o, "run_id", w),
    label: str(o, "label", w),
    links,
    link_ends: ends.map((p, i) => {
      if (!Array.isArray(p) || p.length !== 2 || p.some((s) => typeof s !== "string")) throw new ResultsError(`${w}.link_ends[${i}]: expected two node names`);
      return p;
    }),
    cost_A,
    cost_B,
    paradox_interval: interval,
    points,
  };
}

function gridCells(v) {
  if (!Array.isArray(v) || v.length === 0) throw new ResultsError("grid_cells: expected a nonempty array");
  return v.map((c, i) => {
    const w = `grid_cells[${i}]`;
    const o = obj(c, w);
    return {
      size: str(o, "size", w),
      rho: num(o, "rho", w),
      n: num(o, "n", w),
      R_UE: estimate(o.R_UE, `${w}.R_UE`),
      R_FF: estimate(o.R_FF, `${w}.R_FF`),
      paired_FF_minus_UE: estimate(o.paired_FF_minus_UE, `${w}.paired_FF_minus_UE`),
    };
  });
}

function sensitivity(v) {
  if (!Array.isArray(v) || v.length === 0) throw new ResultsError("sensitivity: expected a nonempty array");
  return v.map((s, i) => {
    const w = `sensitivity[${i}]`;
    const o = obj(s, w);
    const e = estimate(o, w);
    if (e.ci_low === null) throw new ResultsError(`${w}: sensitivity rows need an interval`);
    return { ...e, n_used: num(o, "n_used", w), lower_one_sided_95: num(o, "lower_one_sided_95", w), lower_display: str(o, "lower_display", w), decision_role: str(o, "decision_role", w) };
  });
}

function compliance(v) {
  if (!Array.isArray(v) || v.length === 0) throw new ResultsError("compliance: expected a nonempty array");
  const out = v.map((s, i) => {
    const w = `compliance[${i}]`;
    const o = obj(s, w);
    const arms = arr(o, "arms", w).map((a, j) => {
      const wa = `${w}.arms[${j}]`;
      const e = estimate(a, wa);
      const ao = obj(a, wa);
      return { ...e, arm: str(ao, "arm", wa), c: num(ao, "c", wa, true) };
    });
    if (arms.length === 0) throw new ResultsError(`${w}.arms: empty`);
    return { capacity_scale: num(o, "capacity_scale", w), confirmatory: bool(o, "confirmatory", w), H1_supported: bool(o, "H1_supported", w), arms };
  });
  if (out.filter((s) => s.confirmatory).length !== 1) throw new ResultsError("compliance: expected exactly one confirmatory capacity scale");
  return out;
}

export function validateResults(raw) {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    const label = str(e, "label", w);
    if (!LABELS.includes(label)) throw new ResultsError(`${w}.label: expected one of ${LABELS.join(", ")}`);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      label,
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  const ids = new Set(experiments.map((e) => e.id));
  if (ids.size !== experiments.length) throw new ResultsError("results.experiments: duplicate id");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    exploratory_code_revision: str(o, "exploratory_code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return { name: str(a, "name", `assumptions[${i}]`), value: str(a, "value", `assumptions[${i}]`), source: str(a, "source", `assumptions[${i}]`) };
    }),
    limitations: strArr(o, "limitations", "results"),
    braess_sweep: braessSweep(o.braess_sweep),
    grid_cells: gridCells(o.grid_cells),
    sensitivity: sensitivity(o.sensitivity),
    compliance: compliance(o.compliance),
  };
}

export async function loadResults(url = "./data/results.json") {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

export function fmtEstimate(e) {
  return e.display;
}

export function fmtInterval(e) {
  if (e.interval_display !== null) return `${Math.round((e.ci_level ?? 0.95) * 100)}% ${e.interval_display}`;
  return e.interval_note ?? "no interval reported";
}
