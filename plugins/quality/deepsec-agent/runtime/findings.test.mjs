import test from 'node:test';
import assert from 'node:assert/strict';
import { makeFinding, normalizeReport, createBaseline, applyBaseline, redactText } from './findings.mjs';

const finding = (overrides = {}) => makeFinding({
  engine: 'deepsec', ruleId: 'unsafe-exec', title: 'Command execution candidate', path: 'src/server.js',
  line: 8, message: 'A request value may reach a command.', severity: 'high', ...overrides,
});
const report = (findings = [finding()], coverage = [{ engine: 'deepsec', status: 'complete' }]) => ({ schemaVersion: '1.0', createdAt: '2026-10-23T00:00:00Z', findings, coverage });

test('findings redact common credential forms and never retain raw scanner properties', () => {
  const secret = 'ghp_abcdefghijklmnopqrstuvwxyz1234567890';
  const raw = makeFinding({
    ...finding(), title: `Exposed ${secret}`, message: `api_key="super-sensitive-123"; password=hunter2; Bearer abcdefghijklmnop`,
    remediation: '-----BEGIN RSA PRIVATE KEY-----\nsecret body\n-----END RSA PRIVATE KEY-----',
    Secret: 'raw-scanner-secret', snippet: 'another raw secret',
  });
  const serialized = JSON.stringify(raw);
  for (const value of [secret, 'super-sensitive-123', 'hunter2', 'abcdefghijklmnop', 'secret body', 'raw-scanner-secret', 'another raw secret']) assert.equal(serialized.includes(value), false, value);
  assert.match(serialized, /REDACTED/);
  assert.equal('snippet' in raw, false);
  assert.equal('Secret' in raw, false);
  assert.equal(redactText('-----BEGIN PRIVATE KEY-----\ntruncated-body'), '[REDACTED PRIVATE KEY]');
  assert.equal(redactText('access_token: "do-not-leak"'), 'access_token: "[REDACTED]"');
  assert.equal(redactText('password="unterminated-secret'), 'password="[REDACTED]"');
  assert.equal(redactText('password="' + 'x'.repeat(100_000)).includes('xxxxx'), false);
});

test('relative paths normalize Windows separators and reject traversal, URIs, controls and absolutes', () => {
  assert.equal(finding({ path: 'src\\server.js' }).path, 'src/server.js');
  for (const path of ['../secret', 'src/../secret', './server.js', '/etc/passwd', 'C:\\keys', '\\\\server\\share', 'file:///etc/passwd', 'src\u0000.js', 'src//server.js']) {
    assert.throws(() => finding({ path }), TypeError, path);
  }
});

test('evidence fingerprints survive line drift and unrelated whole-file changes', () => {
  const a = finding({ evidenceHash: 'a'.repeat(64), sourceHash: 'b'.repeat(64) });
  const b = finding({ evidenceHash: 'a'.repeat(64), sourceHash: 'c'.repeat(64), line: 22 });
  assert.equal(a.fingerprint, b.fingerprint);
  assert.notEqual(finding({ line: 22 }).fingerprint, finding({ line: 8 }).fingerprint);
  const known = createBaseline(report([a]));
  const applied = applyBaseline(report([b, finding({ ruleId: 'new-rule' })]), known);
  assert.equal(applied.findings.find(f => f.ruleId === 'unsafe-exec').baseline, 'existing');
  assert.equal(applied.summary.existing, 1);
  assert.equal(applied.summary.new, 1);
  assert.equal(applied.summary.total, 2);
});

test('normalization deduplicates and carries explicit partial coverage rather than trusting input summary', () => {
  const normalized = normalizeReport({ ...report([finding(), finding()], [{ engine: 'deepsec', status: 'partial', reason: 'File byte limit reached', skipReasons: { oversized: 1 }, filesVisited: 9, gateMode: 'file-patterns-only' }]), complete: true, summary: { total: 0 }, root: '/private/workspace' });
  assert.equal(normalized.findings.length, 1);
  assert.equal(normalized.summary.total, 1);
  assert.equal(normalized.complete, false);
  assert.equal(normalized.coverage[0].filesVisited, 9);
  assert.deepEqual(normalized.coverage[0].skipReasons, { oversized: 1 });
  assert.equal('root' in normalized, false);
});

test('normalization preserves scanner bounds and snapshot counters but drops raw source data', () => {
  const coverage = {
    engine: 'deepsec', status: 'partial', entriesVisited: 23, directoriesVisited: 4,
    policyExcluded: 6, limits: { maxFiles: 20, maxFileBytes: 262144, timeoutMs: 30000 },
    findings: 3, invalidEntries: 2, scannerErrors: 1, sources: 4,
    snapshotBytes: 128, skippedInputs: 2, snapshotLimited: true, outputBytes: 256,
    scope: 'Bounded snapshot, token=do-not-print',
    stdout: 'raw-source-secret', stderr: 'raw-error-secret', snippet: 'raw-snippet-secret',
    snapshot: { files: ['raw-file-contents'] },
  };
  const normalized = normalizeReport(report([], [coverage])).coverage[0];
  for (const key of ['entriesVisited', 'directoriesVisited', 'policyExcluded', 'findings', 'invalidEntries', 'scannerErrors', 'sources', 'snapshotBytes', 'skippedInputs', 'snapshotLimited', 'outputBytes']) assert.equal(normalized[key], coverage[key], key);
  assert.deepEqual(normalized.limits, coverage.limits);
  assert.equal(normalized.scope, 'Bounded snapshot, token=[REDACTED]');
  for (const key of ['stdout', 'stderr', 'snippet', 'snapshot']) assert.equal(key in normalized, false, key);
  assert.equal(JSON.stringify(normalized).includes('raw-'), false);
  assert.throws(() => normalizeReport(report([], [{ ...coverage, snapshotLimited: 'true' }])), TypeError);
  assert.throws(() => normalizeReport(report([], [{ ...coverage, limits: { maxFiles: -1 } }])), TypeError);
  assert.throws(() => normalizeReport(report([], [{ ...coverage, snapshotBytes: -1 }])), TypeError);
});

test('invalid and oversized report/baseline inputs are rejected', () => {
  assert.throws(() => normalizeReport(report([], [{ engine: 'deepsec', status: 'clean' }])), TypeError);
  assert.throws(() => normalizeReport({ findings: [], coverage: [] , schemaVersion: '0.0' }), TypeError);
  assert.throws(() => normalizeReport(report(Array(10_001).fill(finding()))), TypeError);
  assert.throws(() => applyBaseline(report(), { schemaVersion: '1.0', fingerprints: ['bad'] }), TypeError);
  assert.throws(() => finding({ line: 0 }), TypeError);
  assert.throws(() => finding({ sourceHash: 'not-a-digest' }), TypeError);
  assert.throws(() => finding({ severity: 'urgent' }), TypeError);
  assert.throws(() => finding({ line: 8, endLine: 2 }), TypeError);
  assert.equal(normalizeReport(report([], [])).complete, false);
});

test('user-controlled engine identifiers do not collide with inherited object properties', () => {
  const normalized = normalizeReport(report([finding({ engine: 'constructor' }), finding({ engine: '__proto__' })]));
  assert.equal(normalized.summary.byEngine.constructor, 1);
  assert.equal(normalized.summary.byEngine.__proto__, 1);
  assert.equal(Object.getPrototypeOf(normalized.summary.byEngine), null);
});
