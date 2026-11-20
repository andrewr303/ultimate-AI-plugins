/**
 * Baseline-aware outlier lift and a transparent creator score.
 *
 * TypeScript port of scripts/creator_score.py, which stays the reference. Both must return the same result for every
 * vector in vectors/creator-score.vectors.json. Inputs and outputs use the same snake_case JSON shape as the Python
 * command line, so one wire contract serves the skills, this module and the vectors.
 *
 * Pure: no I/O, no clock, no Node built-ins, ES2020 library only. Invalid values throw TypeError or RangeError; they
 * are never coerced. Unknown stays unknown: a missing dimension is renormalised away and lowers confidence, a post
 * with no metric value or no age is left out of the baseline and counted.
 *
 * This score is not HypeStake's Match Score and must not be shown as one. It describes one Creator against one brief
 * from public data, explains a shortlist and never recommends accepting a deal. Weights, thresholds and cutoffs are
 * judgment defaults until calibrated against deal outcomes (references/scoring-rubric.md).
 */

export const CREATOR_SCORE_VERSION = "creator-score-v2";

export type Confidence = "low" | "medium" | "high";
export type DimensionName =
  | "niche_fit"
  | "audience_fit"
  | "engagement_quality"
  | "authenticity"
  | "reach"
  | "brand_safety"
  | "sponsor_readiness"
  | "contactability";
export type GateCode = "G1" | "G2" | "G3" | "G4" | "G5";
export type LiftLabel = "huge" | "strong" | "mild";

export const WEIGHTS: Readonly<Record<DimensionName, number>> = Object.freeze({
  niche_fit: 20, audience_fit: 15, engagement_quality: 15, authenticity: 15,
  reach: 10, brand_safety: 10, sponsor_readiness: 10, contactability: 5,
});
export const GATES: Readonly<Record<GateCode, string>> = Object.freeze({
  G1: "brand-safety floor hit",
  G2: "strong evidence of inauthentic audience or engagement",
  G3: "insufficient public data to score",
  G4: "identity unverifiable (profile, site and handle do not agree)",
  G5: "persistent undisclosed sponsored content",
});
export const CONFIDENCE_RANK: Readonly<Record<Confidence, number>> = Object.freeze({ low: 0, medium: 1, high: 2 });
export const BAND: Readonly<Record<Confidence, number>> = Object.freeze({ high: 5, medium: 10, low: 20 });
/** Younger posts have not finished accruing views. YouTube: pass 336. */
export const MIN_POST_AGE_HOURS = 72;
export const FLOORS: ReadonlyArray<readonly [DimensionName, number]> = Object.freeze([["authenticity", 40], ["brand_safety", 50]] as const);
export const FLOOR_CAP = 60;
/** Output keys, and object-prototype keys, cannot be a metric name. */
const RESERVED_POST_KEYS: ReadonlySet<string> = new Set(["id", "lift", "label", "__proto__", "constructor", "prototype"]);
/** roundHalfEven1 is exact only within this bound; scores, bands and weights stay within 0 to 100. */
export const ROUND_BOUND = 1e9;

const has = (o: object, k: string): boolean => Object.prototype.hasOwnProperty.call(o, k);
const isNumber = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const isPlainObject = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);

/**
 * Python's round(x, 1) for |x| <= ROUND_BOUND (throws RangeError outside it): the nearest one-decimal value, ties to
 * even on the exact binary value. A tie at one decimal place is exactly representable only when 4x is an odd integer
 * (x = j/4); toFixed rounds those up, so they are handled here, where 10x is exact within the bound. Otherwise
 * toFixed's correctly rounded result is used.
 */
export function roundHalfEven1(x: number): number {
  if (!isNumber(x) || Math.abs(x) > ROUND_BOUND) throw new RangeError(`roundHalfEven1 needs a finite number with |x| <= ${ROUND_BOUND}`);
  const q = x * 4;
  if (Math.floor(q) === q && Math.abs(q % 2) === 1) {
    const lo = Math.floor(x * 10);
    return (lo % 2 === 0 ? lo : lo + 1) / 10;
  }
  return Number(x.toFixed(1));
}

/** A 10-post median can be off by roughly 1.5-1.8x (simulation, independence assumed). */
export function baselineConfidence(n: number): Confidence {
  if (!isNumber(n) || Math.floor(n) !== n || n < 0) throw new RangeError("n must be a whole number >= 0");
  return n >= 20 ? "high" : n >= 12 ? "medium" : "low";
}

/** A string, a safe integer (|id| <= 2**53 - 1) or null. Pass larger platform ids as strings. */
export type PostId = string | number | null;
export interface PostInput {
  id?: PostId;
  age_hours?: number | null;
  [metric: string]: unknown;
}
export interface OutlierPost {
  readonly id: PostId;
  readonly lift: number | null;
  readonly label: LiftLabel | null;
  /** The metric value, under the metric's own name (for example `views`). */
  readonly [metric: string]: PostId | number | null;
}
export interface OutlierReport {
  baseline: number | null;
  n: number;
  confidence: Confidence;
  excluded_too_young: number;
  excluded_unknown_age: number;
  excluded_missing_metric: number;
  posts: OutlierPost[];
}
export interface OutlierInput {
  posts: ReadonlyArray<PostInput>;
  metric?: string;
  min_age_hours?: number;
}

function median(values: number[]): number {
  const s = values.slice().sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 === 1 ? (s[mid] as number) : ((s[mid - 1] as number) + (s[mid] as number)) / 2;
}

/** Baseline is the median of settled posts. Score one platform and one format at a time; never pool platforms. */
export function outlierReport(input: OutlierInput): OutlierReport {
  if (!isPlainObject(input)) throw new TypeError("input must be an object");
  const posts: unknown = input.posts;
  const metric: unknown = input.metric === undefined ? "views" : input.metric;
  const minAge: unknown = input.min_age_hours === undefined ? MIN_POST_AGE_HOURS : input.min_age_hours;
  if (!Array.isArray(posts)) throw new TypeError("posts must be an array");
  if (typeof metric !== "string" || !metric || RESERVED_POST_KEYS.has(metric)) throw new RangeError("metric must be a non-empty name other than id, lift, label, __proto__, constructor or prototype");
  if (!isNumber(minAge) || minAge < 0) throw new RangeError("min_age_hours must be a number >= 0");
  const settled: Array<{ id: PostId; value: number }> = [];
  let missingMetric = 0;
  let unknownAge = 0;
  let tooYoung = 0;
  posts.forEach((post: unknown, i: number) => {
    if (!isPlainObject(post)) throw new TypeError(`posts[${i}] must be an object`);
    const id = has(post, "id") ? post.id : null;
    if (id !== null && id !== undefined && typeof id !== "string" && !Number.isSafeInteger(id)) throw new TypeError(`posts[${i}].id must be a string, a safe integer or null`);
    const value = has(post, metric) ? post[metric] : null;
    const age = has(post, "age_hours") ? post.age_hours : null;
    if (value !== null && value !== undefined && (!isNumber(value) || value < 0)) throw new RangeError(`posts[${i}].${metric} must be a number >= 0 or null`);
    if (age !== null && age !== undefined && (!isNumber(age) || age < 0)) throw new RangeError(`posts[${i}].age_hours must be a number >= 0 or null`);
    if (value === null || value === undefined) missingMetric++;
    else if (age === null || age === undefined) unknownAge++;
    else if (age < minAge) tooYoung++;
    else settled.push({ id: id === undefined ? null : (id as PostId), value });
  });
  const counts = { excluded_too_young: tooYoung, excluded_unknown_age: unknownAge, excluded_missing_metric: missingMetric };
  if (settled.length === 0) return { baseline: null, n: 0, confidence: "low", ...counts, posts: [] };
  const baseline = median(settled.map((p) => p.value));
  const scored: OutlierPost[] = settled.map(({ id, value }) => {
    const lift = baseline ? value / baseline : null;
    const label: LiftLabel | null = lift === null ? null : lift >= 5 ? "huge" : lift >= 2 ? "strong" : lift >= 1.5 ? "mild" : null;
    const out: Record<string, PostId | number | null> = { id };
    out[metric] = value;
    out.lift = lift;
    out.label = label;
    return out as OutlierPost;
  });
  const key = (p: OutlierPost): number => -((p.lift as number | null) || 0);
  scored.sort((a, b) => Number(a.lift === null) - Number(b.lift === null) || key(a) - key(b));
  return { baseline, n: settled.length, confidence: baselineConfidence(settled.length), ...counts, posts: scored };
}

export interface DimensionInput {
  /** 0 to 100, or null when public data cannot support a score. Never 0 or 50 as a stand-in. */
  score: number | null;
  confidence?: Confidence;
  evidence?: string;
}
export interface ScoreInput {
  dimensions: Partial<Record<DimensionName, DimensionInput>>;
  gates?: ReadonlyArray<GateCode> | null;
}
export type ScoreResult =
  | { verdict: "reject"; gates: Partial<Record<GateCode, string>>; score: null }
  | {
      verdict: "score";
      score: number;
      /** Fixed width by confidence (plus or minus 5, 10 or 20), not a statistical interval. */
      band: [number, number];
      confidence: Confidence;
      missing: DimensionName[];
      floor_capped_by: DimensionName[];
      weights_used: Partial<Record<DimensionName, number>>;
    };

/** Gates first, then the renormalised weighted mean with floors and a confidence-width band. */
export function scoreCreator(input: ScoreInput): ScoreResult {
  if (!isPlainObject(input)) throw new TypeError("input must be an object");
  const dims: unknown = input.dimensions;
  if (!isPlainObject(dims)) throw new TypeError("dimensions must be an object");
  const names = Object.keys(dims);
  const unknownNames = names.filter((k) => !has(WEIGHTS, k)).sort();
  if (unknownNames.length) throw new RangeError(`unknown dimensions: ${unknownNames.join(", ")}`);
  const present: Array<[DimensionName, number, Confidence]> = [];
  for (const name of names) {
    const d: unknown = dims[name];
    if (!isPlainObject(d) || !has(d, "score") || Object.keys(d).some((k) => k !== "score" && k !== "confidence" && k !== "evidence")) {
      throw new TypeError(`${name} must be an object with score and optional confidence and evidence`);
    }
    const score: unknown = d.score;
    const confidence: unknown = has(d, "confidence") ? d.confidence : "low";
    const evidence: unknown = has(d, "evidence") ? d.evidence : "";
    if (score !== null && (!isNumber(score) || score < 0 || score > 100)) throw new RangeError(`${name} score out of range`);
    if (typeof confidence !== "string" || !has(CONFIDENCE_RANK, confidence)) throw new RangeError(`${name} confidence must be low, medium or high`);
    if (typeof evidence !== "string") throw new TypeError(`${name} evidence must be a string`);
    if (score !== null) present.push([name as DimensionName, score, confidence as Confidence]);
  }
  const gates: unknown = input.gates === undefined ? null : input.gates;
  if (gates !== null && (!Array.isArray(gates) || !gates.every((g) => typeof g === "string"))) throw new TypeError("gates must be an array of gate codes");
  const triggered = Array.from(new Set((gates ?? []) as string[])).sort();
  const bad = triggered.filter((g) => !has(GATES, g));
  if (bad.length) throw new RangeError(`unknown gates: ${bad.join(", ")}`);
  if (triggered.length) {
    const out: Partial<Record<GateCode, string>> = {};
    for (const g of triggered) out[g as GateCode] = GATES[g as GateCode];
    return { verdict: "reject", gates: out, score: null };
  }
  if (present.length === 0) return { verdict: "reject", gates: { G3: GATES.G3 }, score: null };

  const presentNames = new Set(present.map(([k]) => k));
  const missing = (Object.keys(WEIGHTS) as DimensionName[]).filter((k) => !presentNames.has(k)).sort();
  let weightSum = 0;
  let weighted = 0;
  for (const [k, score] of present) {
    weightSum += WEIGHTS[k];
    weighted += score * WEIGHTS[k];
  }
  let total = weighted / weightSum;
  const cappedBy = FLOORS.filter(([k, floor]) => present.some(([n, s]) => n === k && s < floor)).map(([k]) => k);
  if (cappedBy.length && total > FLOOR_CAP) total = FLOOR_CAP;
  let confidence: Confidence = present[0]![2];
  for (const [, , c] of present) if (CONFIDENCE_RANK[c] < CONFIDENCE_RANK[confidence]) confidence = c;
  if (missing.length) confidence = "low";
  const band = BAND[confidence];
  const weightsUsed: Partial<Record<DimensionName, number>> = {};
  for (const [k] of present) weightsUsed[k] = roundHalfEven1((WEIGHTS[k] / weightSum) * 100);
  return {
    verdict: "score",
    score: roundHalfEven1(total),
    band: [Math.max(0, roundHalfEven1(total - band)), Math.min(100, roundHalfEven1(total + band))],
    confidence,
    missing,
    floor_capped_by: cappedBy,
    weights_used: weightsUsed,
  };
}
