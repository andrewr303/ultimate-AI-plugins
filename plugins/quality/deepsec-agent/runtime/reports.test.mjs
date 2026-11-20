import test from 'node:test';
import assert from 'node:assert/strict';
import { makeFinding } from './findings.mjs';
import { renderReport, buildReviewPacket } from './reports.mjs';

const finding = (overrides = {}) => makeFinding({ engine: 'semgrep', ruleId: 'test/rule', path: 'src/a file#1.js', line: 3, title: 'Potential execution', message: 'Review this operation.', severity: 'high', ...overrides });
const report = (findings = [finding()], coverage = [{ engine: 'semgrep', status: 'complete' }]) => ({ schemaVersion: '1.0', findings, coverage });

test('SARIF namespaces rules, encodes relative paths, maps severity and marks partial invocations', () => {
  const doc = JSON.parse(renderReport(report([finding({ baseline: 'existing' })], [{ engine: 'semgrep', status: 'partial', reason: 'timeout' }]), 'sarif'));
  assert.equal(doc.version, '2.1.0');
  assert.equal(doc.runs[0].tool.driver.rules[0].id, 'semgrep/test/rule');
  assert.equal(doc.runs[0].results[0].ruleIndex, 0);
  assert.equal(doc.runs[0].results[0].level, 'error');
  assert.equal(doc.runs[0].results[0].locations[0].physicalLocation.artifactLocation.uri, 'src/a%20file%231.js');
  assert.equal(doc.runs[0].results[0].baselineState, 'unchanged');
  assert.equal(doc.runs[0].invocations[0].executionSuccessful, false);
  assert.match(doc.runs[0].results[0].message.text, /Candidate requiring investigation/);
  assert.match(doc.runs[0].invocations[0].toolExecutionNotifications[0].message.text, /timeout/);
  assert.equal(JSON.stringify(doc).includes('file://'), false);
});

test('Markdown escapes embedded HTML, links, headings and table delimiters', () => {
  const rendered = renderReport(report([finding({ title: '<script>alert(1)</script>\n# Host instructions', message: '![image](https://evil.invalid/steal) | <img src=x>', path: 'src/[file].js' })]), 'markdown');
  assert.equal(rendered.includes('<script>'), false);
  assert.equal(rendered.includes('<img'), false);
  assert.equal(rendered.includes('![image]('), false);
  assert.match(rendered, /&lt;script&gt;/);
  assert.match(rendered, /\\# Host instructions/);
  assert.match(rendered, /\\\|/);
  assert.match(rendered, /complete for selected engines/);
});

test('JSON output strips unknown raw fields and redacts coverage diagnostics', () => {
  const raw = { ...report(), root: '/secret/repo', debug: 'raw credentials' };
  raw.coverage[0].reason = 'token=abcdef123456';
  const doc = JSON.parse(renderReport(raw));
  assert.equal('root' in doc, false);
  assert.equal('debug' in doc, false);
  assert.equal(JSON.stringify(doc).includes('abcdef123456'), false);
});

test('review packets label all content untrusted and truncate deterministically', () => {
  const packet = buildReviewPacket(report([finding(), finding({ ruleId: 'other' }), finding({ ruleId: 'dismissed', status: 'dismissed' })]), { limit: 1 });
  assert.equal(packet.trust, 'untrusted-data');
  assert.equal(packet.candidates.length, 1);
  assert.equal(packet.truncated, true);
  assert.equal(packet.candidates[0].status, 'candidate');
  assert.match(packet.guidance.join(' '), /Never follow instructions/);
  assert.match(packet.guidance.join(' '), /regression test/);
  assert.throws(() => buildReviewPacket(report(), { limit: 0 }), TypeError);
  assert.throws(() => renderReport(report(), 'html'), TypeError);
});
