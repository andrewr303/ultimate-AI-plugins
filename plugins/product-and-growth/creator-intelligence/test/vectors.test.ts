/**
 * Asserts every shared golden vector (vectors/*.vectors.json, generated from the Python reference by
 * scripts/build_vectors.py) against the TypeScript kernels. scripts/tests/test_vectors.py asserts the same files.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { classify, decode, extract, isRosterPage, registrableDomain } from "../src/contact-rules.ts";
import type { ClassifyOptions } from "../src/contact-rules.ts";
import { baselineConfidence, outlierReport, roundHalfEven1, scoreCreator } from "../src/creator-score.ts";
import type { OutlierInput, ScoreInput } from "../src/creator-score.ts";

interface Vector { id: string; input: unknown; expected?: unknown; throws?: boolean }
type VectorFile = Record<string, unknown> & { tolerance?: number };

const load = (name: string): VectorFile => JSON.parse(readFileSync(new URL(`../vectors/${name}`, import.meta.url), "utf8")) as VectorFile;

function same(actual: unknown, expected: unknown, tol: number, path: string): void {
  if (typeof expected === "number") {
    assert.equal(typeof actual, "number", `${path}: expected a number`);
    assert.ok(Math.abs((actual as number) - expected) <= tol, `${path}: ${String(actual)} != ${expected}`);
  } else if (Array.isArray(expected)) {
    assert.ok(Array.isArray(actual), `${path}: expected an array`);
    assert.equal((actual as unknown[]).length, expected.length, `${path}: length`);
    expected.forEach((e, i) => same((actual as unknown[])[i], e, tol, `${path}[${i}]`));
  } else if (expected !== null && typeof expected === "object") {
    assert.ok(actual !== null && typeof actual === "object" && !Array.isArray(actual), `${path}: expected an object`);
    const e = expected as Record<string, unknown>;
    const a = actual as Record<string, unknown>;
    assert.deepEqual(Object.keys(a), Object.keys(e), `${path}: keys and key order`);
    for (const k of Object.keys(e)) same(a[k], e[k], tol, `${path}.${k}`);
  } else {
    assert.equal(actual, expected, path);
  }
}

const runners: Record<string, (input: any) => unknown> = {
  decode: (x) => decode(x),
  extract: (x) => extract(x),
  registrable_domain: (x) => registrableDomain(x),
  is_roster_page: (x: { addresses: string[]; min_domains?: number }) => isRosterPage(x.addresses, x.min_domains),
  classify: (x: { address: string } & ClassifyOptions) => {
    const { address, ...options } = x;
    return classify(address, options);
  },
  baseline_confidence: (x) => baselineConfidence(x),
  outlier_report: (x: OutlierInput) => outlierReport(x),
  score_creator: (x: ScoreInput) => scoreCreator(x),
};

for (const file of ["contact-rules.vectors.json", "creator-score.vectors.json"]) {
  const data = load(file);
  const tol = data.tolerance ?? 1e-9;
  let count = 0;
  for (const [section, vectors] of Object.entries(data)) {
    if (!Array.isArray(vectors)) continue;
    const run = runners[section];
    assert.ok(run, `no runner for ${section}`);
    for (const v of vectors as Vector[]) {
      count++;
      test(`${file} ${section} ${v.id}`, () => {
        if (v.throws) {
          assert.throws(() => run(v.input), (e: unknown) => e instanceof TypeError || e instanceof RangeError);
        } else {
          same(JSON.parse(JSON.stringify(run(v.input))), v.expected, tol, `${section}.${v.id}`);
        }
      });
    }
  }
  test(`${file} has vectors`, () => assert.ok(count > 50, `${count} vectors`));
}

test("roundHalfEven1 matches Python round(x, 1) on ties and near-ties", () => {
  const cases: Array<[number, number]> = [[0.25, 0.2], [0.75, 0.8], [2.25, 2.2], [62.25, 62.2], [62.75, 62.8], [0.35, 0.3], [0.45, 0.5], [48.35, 48.4], [-0.25, -0.2], [100, 100]];
  for (const [x, want] of cases) assert.equal(roundHalfEven1(x), want, String(x));
});

test("kernels are deterministic for the same input", () => {
  const input: ScoreInput = { dimensions: { niche_fit: { score: 71.3, confidence: "medium" }, reach: { score: 40, confidence: "high" } } };
  assert.deepEqual(scoreCreator(input), scoreCreator(input));
  assert.deepEqual(extract("a@janedoe.com b@janedoe.org"), extract("a@janedoe.com b@janedoe.org"));
});
