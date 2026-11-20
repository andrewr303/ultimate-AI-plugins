/** Adversarial page text must not make extract() slow: every quantifier in the pattern is bounded. */
import assert from "node:assert/strict";
import { test } from "node:test";
import { extract } from "../src/contact-rules.ts";

const INPUTS: Array<[string, (n: number) => string]> = [
  ["a% run", (n) => "a%".repeat(n / 2)],
  ["a. run", (n) => "a.".repeat(n / 2)],
  ["@ run", (n) => "@".repeat(n)],
  ["_ run", (n) => "_".repeat(n)],
  ["a@ run", (n) => "a@".repeat(n / 2)],
  ["label run after @", (n) => "x@" + "a.".repeat(n / 2)],
];

test("200k-character adversarial inputs finish well under a second", () => {
  for (const [label, make] of INPUTS) {
    const text = make(200_000);
    const start = performance.now();
    extract(text);
    const ms = performance.now() - start;
    assert.ok(ms < 1000, `${label}: ${ms.toFixed(1)} ms`);
  }
});
