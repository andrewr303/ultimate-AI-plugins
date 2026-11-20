"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const { fingerprintSignal } = require("../lib/importers.cjs");
const {
  compareSignals,
  validateComparisonDocument,
  renderSignalsMarkdown,
  signalsToSarif,
  findingsToSarif,
} = require("../lib/reporting.cjs");

function signal(overrides = {}) {
  const value = {
    tool: "semgrep",
    rule_id: "rule.sample",
    path: "src/handler.js",
    line: 12,
    severity: "high",
    package: null,
    version: null,
    advisory: null,
    ...overrides,
  };
  value.title = `${value.tool} signal: ${value.rule_id}`;
  value.fingerprint = fingerprintSignal(value);
  return value;
}

function envelope(signals = [signal()], overrides = {}) {
  return {
    schema_version: "1.0.0",
    kind: "tool-signals",
    tool: "semgrep",
    complete: true,
    warnings: [],
    signals: [...signals].sort((a, b) => a.fingerprint.localeCompare(b.fingerprint)),
    ...overrides,
  };
}

function source(kind, file, line) {
  return { kind, file, line, scope: "update_record", description: "The user-selected identifier reaches the trusted data store." };
}

function confirmed() {
  return {
    verdict: "confirmed",
    fingerprint: "confirmed-owner-check",
    title: "Missing record ownership check",
    description: "An authenticated user can update a record belonging to a different dummy tenant.",
    root_cause: "The update operation omits the record owner condition.",
    intended_behavior: "Only the owner can update a record.",
    trace: [source("entrypoint", "src/api.js", 5), source("sink", "src/data store.js", 12)],
    evidence: [{ file: "src/data store.js", line: 12, description: "The store update filters by record identifier without owner." }],
    conditions: [],
    execution: {
      attacker_perspective: "An authenticated user in the local dummy fixture.",
      payloads: ["dummy-other-tenant-record"],
      instructions: ["Call the update operation against the local dummy record."],
      observed_result: "The other dummy tenant record changes.",
    },
    remediation: { strategy: "Require the requesting tenant to own the record at the write boundary." },
    severity: {
      likelihood: { score: "medium", reason: "The attacker needs a record identifier." },
      impact: { score: "high", reason: "The operation crosses the tenant boundary." },
      overall_severity: "high",
    },
    confidence: { score: "high", reason: "The local fixture observed the record change." },
  };
}

function unresolved() {
  return {
    verdict: "needs_validation",
    fingerprint: "unresolved-provider-control",
    title: "Provider authorization requires owner validation",
    description: "The local path delegates its last authorization decision to a missing provider.",
    claimed_root_cause: "The provider may not enforce resource ownership.",
    trace: [source("entrypoint", "src/provider.js", 3)],
    evidence: [{ file: "src/provider.js", line: 3, description: "The local code calls an external provider." }],
    blockers: ["The provider policy is absent."],
    validation_plan: { local: "Inspect an owner-supplied policy fixture." },
  };
}

function rejected() {
  return {
    verdict: "rejected",
    fingerprint: "rejected-router-bypass",
    title: "Router bypass refuted",
    description: "The route applies a guard before dispatch.",
    claimed_root_cause: "The route was claimed to bypass its guard.",
    trace: [source("entrypoint", "src/router.js", 8)],
    evidence: [{ file: "src/router.js", line: 8, description: "The guard wraps every handler." }],
    reason: "The mandatory guard rejects requests before dispatch.",
  };
}

test("baseline comparison distinguishes new, persisting, and absent identities", () => {
  const persistent = signal();
  const added = signal({ rule_id: "rule.added" });
  const removed = signal({ rule_id: "rule.removed" });
  const current = envelope([persistent, added]);
  const baseline = envelope([persistent, removed]);
  const comparison = compareSignals(current, baseline);
  assert.deepEqual(comparison.new, [added]);
  assert.deepEqual(comparison.unchanged, [persistent]);
  assert.deepEqual(comparison.absent, [removed]);
  assert.equal(comparison.complete, true);
  assert.match(comparison.warnings.join(" "), /Absent signals do not prove a fix/);
  assert.deepEqual(validateComparisonDocument(comparison), []);
  comparison.unchanged[0].severity = "low";
  assert.equal(current.signals.find((item) => item.fingerprint === persistent.fingerprint).severity, "high");
});

test("incomplete comparisons withhold absence and retain new signals", () => {
  const old = signal();
  const added = signal({ rule_id: "rule.new" });
  for (const [currentComplete, baselineComplete] of [[false, true], [true, false], [false, false]]) {
    const comparison = compareSignals(envelope([added], { complete: currentComplete }), envelope([old], { complete: baselineComplete }));
    assert.equal(comparison.complete, false);
    assert.equal(comparison.new.length, 1);
    assert.deepEqual(comparison.absent, []);
    assert.match(comparison.warnings.join(" "), /absent signals are withheld/);
  }
});

test("same identity with changed scanner severity stays in persisting group", () => {
  const current = signal({ severity: "critical" });
  const baseline = signal({ severity: "low" });
  const comparison = compareSignals(envelope([current]), envelope([baseline]));
  assert.equal(comparison.unchanged.length, 1);
  assert.equal(comparison.unchanged[0].severity, "critical");
  assert.match(comparison.warnings.join(" "), /metadata may have changed/);
});

test("incompatible tool reports and invalid schema versions are rejected", () => {
  const sarif = signal({ tool: "sarif" });
  assert.throws(() => compareSignals(envelope(), envelope([sarif], { tool: "sarif" })), /same tool/);
  assert.throws(() => compareSignals(envelope(), envelope([], { schema_version: "2.0.0" })), /Invalid/);
});

test("forged fingerprints, duplicate identities, unknown fields, and unsafe paths are rejected", () => {
  const forged = signal();
  forged.fingerprint = `sig:${"0".repeat(64)}`;
  for (const value of [
    envelope([forged]),
    envelope([signal(), signal()]),
    envelope([signal({ path: "../outside.js" })]),
    envelope([signal({ path: "https://example.test/file.js" })]),
    envelope([], { Secret: "must-never-leak" }),
  ]) {
    assert.throws(() => renderSignalsMarkdown(value), /Invalid/);
    assert.throws(() => signalsToSarif(value), /Invalid/);
  }
});

test("reloaded comparisons cannot inject repeated identities or false absence", () => {
  const value = compareSignals(envelope(), envelope([]));
  value.absent = [value.new[0]];
  assert.notEqual(validateComparisonDocument(value).length, 0);
  assert.throws(() => renderSignalsMarkdown(value), /repeated/);
  const incomplete = compareSignals(envelope([], { complete: false }), envelope([signal()]));
  incomplete.absent = [signal()];
  assert.notEqual(validateComparisonDocument(incomplete).length, 0);
});

test("Markdown escapes injected markup and describes completeness narrowly", () => {
  const value = compareSignals(envelope(), envelope([]));
  value.warnings.push('<script>alert("x")</script> | [click](https://example.test) `code`\n# heading');
  const markdown = renderSignalsMarkdown(value);
  assert.doesNotMatch(markdown, /<script>|\[click\]|`code`|\n# heading/);
  assert.match(markdown, /&#60;script&#62;/);
  assert.match(markdown, /complete for the supplied report/);
  assert.match(markdown, /does not establish repository coverage/);
  assert.match(markdown, /unverified external scanner signals/);
});

test("empty scanner output never renders an assurance", () => {
  const markdown = renderSignalsMarkdown(envelope([]));
  assert.match(markdown, /No signals in this group/);
  assert.match(markdown, /not a security assurance/);
  assert.doesNotMatch(markdown, /no vulnerabilities|secure repository/i);
});

test("signal SARIF explicitly exports review notes with scanner severity separated", () => {
  const output = signalsToSarif(envelope());
  assert.equal(output.version, "2.1.0");
  const run = output.runs[0];
  const result = run.results[0];
  assert.equal(result.kind, "review");
  assert.equal(result.level, "note");
  assert.equal(result.properties.scannerSeverity, "high");
  assert.equal(result.properties.reviewStatus, "unverified");
  assert.equal(run.tool.driver.rules[result.ruleIndex].id, result.ruleId);
  assert.equal(result.locations[0].physicalLocation.artifactLocation.uri, "src/handler.js");
  assert.equal(result.locations[0].physicalLocation.region.startLine, 12);
  assert.equal(result.partialFingerprints["security-audit/signalFingerprint/v1"], signal().fingerprint);
  assert.ok(!JSON.stringify(output).includes("security-severity"));
});

test("SARIF percent-encodes repository paths and omits unknown locations", () => {
  const withSpaces = signal({ path: "src/a file.js", line: null });
  const withoutLocation = signal({ rule_id: "dependency.rule", path: null, line: null, package: "example-package", version: "1.0.0", advisory: "CVE-2026-12345" });
  const output = signalsToSarif(envelope([withSpaces, withoutLocation]));
  const located = output.runs[0].results.find((item) => item.locations);
  const unlocated = output.runs[0].results.find((item) => !item.locations);
  assert.equal(located.locations[0].physicalLocation.artifactLocation.uri, "src/a%20file.js");
  assert.ok(!("region" in located.locations[0].physicalLocation));
  assert.equal(unlocated.properties.package, "example-package");
  assert.equal(unlocated.properties.advisory, "CVE-2026-12345");
});

test("SARIF includes failed processing state and keeps rule order deterministic", () => {
  const values = [signal({ rule_id: "rule.z" }), signal({ rule_id: "rule.a" })];
  const output = signalsToSarif(envelope(values, { complete: false }));
  assert.equal(output.runs[0].invocations[0].executionSuccessful, false);
  const ids = output.runs[0].tool.driver.rules.map((rule) => rule.id);
  assert.deepEqual(ids, [...ids].sort());
  assert.deepEqual(output, signalsToSarif(envelope(values.reverse(), { complete: false })));
});

test("canonical findings SARIF emits only confirmed records and explicit omitted counts", () => {
  const findings = [confirmed(), rejected(), unresolved()].sort((a, b) => a.fingerprint.localeCompare(b.fingerprint));
  const output = findingsToSarif(findings);
  const run = output.runs[0];
  assert.equal(run.results.length, 1);
  assert.deepEqual(run.properties.verdictCounts, { confirmed: 1, needs_validation: 1, rejected: 1 });
  assert.equal(run.results[0].kind, "fail");
  assert.equal(run.results[0].level, "error");
  assert.equal(run.results[0].properties.severity, "high");
  assert.equal(run.results[0].locations[0].physicalLocation.artifactLocation.uri, "src/data%20store.js");
  assert.ok(!JSON.stringify(output).includes("dummy-other-tenant-record"));
  assert.ok(!JSON.stringify(output).includes("The provider policy is absent"));
  assert.match(run.properties.exportScope, /does not establish audit coverage/);
});

test("findings export validates contracts before writing any SARIF", () => {
  const missingEvidence = confirmed();
  delete missingEvidence.evidence;
  const severityOnUnresolved = unresolved();
  severityOnUnresolved.severity = "high";
  assert.throws(() => findingsToSarif([missingEvidence]), /Invalid audit findings/);
  assert.throws(() => findingsToSarif([severityOnUnresolved]), /Invalid audit findings/);
  assert.throws(() => findingsToSarif([confirmed(), confirmed()]), /Invalid audit findings/);
});

test("valid empty findings export does not imply complete audit coverage", () => {
  const output = findingsToSarif([]);
  assert.deepEqual(output.runs[0].results, []);
  assert.match(output.runs[0].properties.exportScope, /does not establish audit coverage/);
});

test("confirmed findings export bounds title and strips terminal controls", () => {
  const finding = confirmed();
  finding.title = "Observed issue\u001b[31m\nwith context";
  const text = findingsToSarif([finding]).runs[0].results[0].message.text;
  assert.doesNotMatch(text, /\u001b|\n/);
  assert.match(text, /Observed issue/);
});
