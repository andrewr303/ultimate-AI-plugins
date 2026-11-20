'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { importReport, fingerprintSignal, validateSignalDocument, isSafeRelativePath, WARNINGS } = require('../lib/importers.cjs');
const clone = x => JSON.parse(JSON.stringify(x));
const semgrep = () => ({ results: [{ check_id: 'javascript.lang.security.eval', path: 'src/handler.js', start: { line: 7 }, extra: { severity: 'ERROR', message: 'secret=DO_NOT_KEEP', lines: 'DO_NOT_KEEP' } }], errors: [] });
const leaks = () => [{ RuleID: 'generic-api-key', File: 'config/app.env', StartLine: 3, Secret: 'DO_NOT_KEEP', Match: 'DO_NOT_KEEP', Description: 'DO_NOT_KEEP', Fingerprint: 'DO_NOT_KEEP' }];
const sarif = () => ({ version: '2.1.0', runs: [{ tool: { driver: { name: 'Example', rules: [{ id: 'TEST001', properties: { 'security-severity': '9.1' }, fullDescription: { text: 'DO_NOT_KEEP' } }] } }, results: [{ ruleId: 'TEST001', level: 'error', message: { text: 'DO_NOT_KEEP' }, locations: [{ physicalLocation: { artifactLocation: { uri: 'src/main.py' }, region: { startLine: 14, snippet: { text: 'DO_NOT_KEEP' } } } }] }] }] });
const osv = () => ({ results: [{ source: { path: '/project/package-lock.json', type: 'lockfile' }, packages: [{ package: { name: '@demo/library', ecosystem: 'npm', version: '1.2.3' }, vulnerabilities: [{ id: 'GHSA-aaaa-bbbb-cccc', summary: 'DO_NOT_KEEP', details: 'DO_NOT_KEEP', severity: [{ type: 'CVSS_V3', score: 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H' }] }], groups: [{ ids: ['GHSA-aaaa-bbbb-cccc'], max_severity: '9.8' }] }] }] });
const trivy = () => ({ SchemaVersion: 2, Results: [{ Target: 'package-lock.json', Type: 'npm', Vulnerabilities: [{ VulnerabilityID: 'CVE-2026-1000', PkgName: 'library', InstalledVersion: '1.0.0', Severity: 'HIGH', Description: 'DO_NOT_KEEP' }] }, { Target: 'Dockerfile', Misconfigurations: [{ ID: 'DS002', Severity: 'MEDIUM', Status: 'FAIL', CauseMetadata: { StartLine: 9, Code: 'DO_NOT_KEEP' } }] }, { Target: 'src/keys.js', Secrets: [{ RuleID: 'generic-key', StartLine: 1, Severity: 'CRITICAL', Match: 'DO_NOT_KEEP', Code: 'DO_NOT_KEEP' }] }] });

for (const [format, fixture, count] of [['semgrep', semgrep, 1], ['gitleaks', leaks, 1], ['sarif', sarif, 1], ['osv', osv, 1], ['trivy', trivy, 3]]) {
  test(`${format}: imports metadata without source prose or secret material`, () => {
    const report = importReport(format, fixture(), { sourceRoot: '/project' });
    assert.equal(report.signals.length, count);
    assert.equal(report.complete, true);
    assert.deepEqual(validateSignalDocument(report), []);
    assert.ok(!JSON.stringify(report).includes('DO_NOT_KEEP'));
    for (const signal of report.signals) {
      assert.equal(signal.tool, format);
      assert.equal(signal.fingerprint, fingerprintSignal(signal));
      assert.ok(!('verdict' in signal));
    }
  });
}

test('legitimate empty reports are accepted; missing required report containers are rejected', () => {
  const empty = { semgrep: { results: [], errors: [] }, gitleaks: [], sarif: { version: '2.1.0', runs: [] }, osv: { results: [] }, trivy: { SchemaVersion: 2, Results: [] } };
  for (const [format, data] of Object.entries(empty)) {
    assert.deepEqual(importReport(format, data).signals, []);
    assert.equal(importReport(format, data).complete, true);
    assert.throws(() => importReport(format, {}), /structure/);
  }
  assert.deepEqual(importReport('trivy', { SchemaVersion: 2, ArtifactName: '.', ArtifactType: 'filesystem' }).signals, []);
  assert.throws(() => importReport('trivy', { SchemaVersion: 2 }), /structure/);
  assert.throws(() => importReport('sarif', { version: '2.1.0', runs: [{ tool: { driver: { name: 'Tool' } } }] }), /structure/);
});

test('stable fingerprints deduplicate repeated input and merge highest reported severity', () => {
  const data = semgrep();
  data.results.push(clone(data.results[0]));
  data.results[0].extra.severity = 'INFO';
  const report = importReport('semgrep', data);
  assert.equal(report.signals.length, 1);
  assert.equal(report.signals[0].severity, 'high');
  assert.deepEqual(report, importReport('semgrep', { ...data, results: [...data.results].reverse() }));
  assert.equal(report.signals[0].fingerprint, importReport('semgrep', semgrep()).signals[0].fingerprint);
  data.results[0].start.line = 8;
  assert.equal(importReport('semgrep', data).signals.length, 2);
});

test('unsafe locations never enter artifacts, diagnostics, or line metadata', () => {
  for (const path of ['/outside/DO_NOT_KEEP', '../DO_NOT_KEEP', 'src/../DO_NOT_KEEP', 'https://host/DO_NOT_KEEP', 'src/%2e%2e/DO_NOT_KEEP', 'C:\\outside\\DO_NOT_KEEP', '//host/DO_NOT_KEEP', 'src/DO_NOT_KEEP\u202e.js']) {
    const data = semgrep(); data.results[0].path = path;
    const result = importReport('semgrep', data, { sourceRoot: '/project' });
    assert.equal(result.signals[0].path, null);
    assert.equal(result.signals[0].line, null);
    assert.equal(result.complete, false);
    assert.deepEqual(result.warnings, [WARNINGS.path]);
    assert.ok(!JSON.stringify(result).includes('DO_NOT_KEEP'));
  }
});

test('explicit source root maps only contained lexical paths and handles Windows separators', () => {
  const data = semgrep(); data.results[0].path = '/project/src/main.js';
  assert.equal(importReport('semgrep', data, { sourceRoot: '/project' }).signals[0].path, 'src/main.js');
  data.results[0].path = '/project-next/main.js';
  assert.equal(importReport('semgrep', data, { sourceRoot: '/project' }).signals[0].path, null);
  data.results[0].path = '/project/src/../../outside.js';
  assert.equal(importReport('semgrep', data, { sourceRoot: '/project' }).signals[0].path, null);
  data.results[0].path = 'C:\\PROJECT\\src\\main.js';
  assert.equal(importReport('semgrep', data, { sourceRoot: 'c:\\project' }).signals[0].path, 'src/main.js');
  assert.throws(() => importReport('semgrep', data, { sourceRoot: 'project' }), /Source root/);
  assert.throws(() => importReport('semgrep', data, { sourceRoot: '/project/../outside' }), /Source root/);
});

test('Semgrep error or skipped analysis cannot become a clean import', () => {
  for (const change of [{ errors: [{ message: 'DO_NOT_KEEP' }] }, { paths: { skipped: [{ path: 'DO_NOT_KEEP' }] } }, { skipped_rules: ['DO_NOT_KEEP'] }]) {
    const result = importReport('semgrep', { ...semgrep(), ...change });
    assert.equal(result.complete, false);
    assert.ok(result.warnings.length);
    assert.ok(!JSON.stringify(result).includes('DO_NOT_KEEP'));
  }
});

test('SARIF handles unsuccessful invocations, suppression, numeric score and indexed locations', () => {
  const data = sarif();
  data.runs[0].invocations = [{ executionSuccessful: false }];
  data.runs[0].results[0].suppressions = [{ kind: 'inSource', justification: 'DO_NOT_KEEP' }];
  data.runs[0].artifacts = [{ location: { uri: 'src/from-index.py' } }];
  data.runs[0].results[0].locations[0].physicalLocation.artifactLocation = { index: 0 };
  let report = importReport('sarif', data);
  assert.equal(report.complete, false);
  assert.equal(report.signals[0].severity, 'critical');
  assert.equal(report.signals[0].rule_id, '7:Example/7:TEST001');
  assert.equal(report.signals[0].path, 'src/from-index.py');
  data.runs[0].tool.driver.rules[0].properties['security-severity'] = '4.0';
  report = importReport('sarif', data);
  assert.equal(report.signals[0].severity, 'medium');
  data.runs[0].results[0].locations[0].physicalLocation.artifactLocation.index = 99;
  assert.throws(() => importReport('sarif', data), /structure/);
});

test('SARIF URI bases require explicit trusted source-root mapping', () => {
  const data = sarif();
  data.runs[0].originalUriBaseIds = { '%SRCROOT%': { uri: 'file:///project/' } };
  data.runs[0].results[0].locations[0].physicalLocation.artifactLocation.uriBaseId = '%SRCROOT%';
  assert.equal(importReport('sarif', data).signals[0].path, null);
  assert.equal(importReport('sarif', data, { sourceRoot: '/project' }).signals[0].path, 'src/main.py');
  data.runs[0].originalUriBaseIds['%SRCROOT%'].uri = 'file:///elsewhere/';
  assert.equal(importReport('sarif', data, { sourceRoot: '/project' }).signals[0].path, null);
});

test('OSV preserves package identity and scores; CVSS vectors are not guessed', () => {
  const data = osv();
  let report = importReport('osv', data, { sourceRoot: '/project' });
  assert.equal(report.signals[0].package, 'npm:@demo/library');
  assert.equal(report.signals[0].version, '1.2.3');
  assert.equal(report.signals[0].severity, 'critical');
  delete data.results[0].packages[0].groups;
  report = importReport('osv', data, { sourceRoot: '/project' });
  assert.equal(report.signals[0].severity, 'unknown');
  data.results[0].packages[0].vulnerabilities[0].database_specific = { severity: 'HIGH' };
  assert.equal(importReport('osv', data, { sourceRoot: '/project' }).signals[0].severity, 'high');
});

test('Trivy and OSV explicitly disclose unsupported finding categories', () => {
  const t = trivy(); t.Results[0].Licenses = [{ Name: 'DO_NOT_KEEP' }];
  assert.equal(importReport('trivy', t).complete, false);
  const o = osv(); o.experimental_generic_findings = [{ message: 'DO_NOT_KEEP' }];
  assert.equal(importReport('osv', o, { sourceRoot: '/project' }).complete, false);
  const lic = osv(); lic.results[0].packages[0].license_violations = ['GPL-3.0'];
  assert.equal(importReport('osv', lic, { sourceRoot: '/project' }).complete, false);
});

test('malformed nested containers and metadata fail instead of silently dropping results', () => {
  const bad = [
    ['gitleaks', [{ RuleID: 'rule', File: 'file', StartLine: -1 }]],
    ['semgrep', { results: [{}] }],
    ['semgrep', { ...semgrep(), errors: 'error' }],
    ['trivy', { SchemaVersion: 2, Results: [{ Target: 'file', Vulnerabilities: {} }] }],
    ['osv', { results: [{ source: { path: 'lock' }, packages: {} }] }],
    ['sarif', { version: '2.0.0', runs: [] }],
  ];
  for (const [format, data] of bad) assert.throws(() => importReport(format, data), /structure/);
  const data = semgrep(); data.results[0].check_id = 'rule\nDO_NOT_KEEP';
  assert.throws(() => importReport('semgrep', data), error => !error.message.includes('DO_NOT_KEEP'));
  assert.throws(() => importReport('unsupported', {}), /Unsupported/);
  const circular = {}; circular.self = circular;
  assert.throws(() => importReport('semgrep', circular), /structure/);
  assert.throws(() => importReport('gitleaks', Array(50001).fill(null)), /structure/);
});

test('stored signal validator rejects tampering and raw-content injection', () => {
  const original = importReport('semgrep', semgrep());
  for (const change of [
    d => { d.signals[0].fingerprint = 'sig:' + '0'.repeat(64); },
    d => { d.signals[0].verdict = 'confirmed'; },
    d => { d.signals[0].title = 'malicious message'; },
    d => { d.signals[0].path = '../secret'; },
    d => { d.signals[0].tool = 'gitleaks'; },
    d => { d.signals[0].severity = 'CONFIRMED'; },
    d => { d.signals.push(clone(d.signals[0])); },
    d => { d.warnings = ['untrusted message']; },
    d => { d.complete = 'yes'; },
  ]) {
    const modified = clone(original); change(modified);
    assert.ok(validateSignalDocument(modified).length);
  }
  assert.ok(isSafeRelativePath('src/app.js'));
  assert.ok(!isSafeRelativePath('src/../app.js'));
});

test('path metadata rejects Unicode hazards and filesystem aliases', () => {
  for (const unsafe of ['src/a\ud800.js', 'src/a\u200f.js', 'src/a\u00ad.js', 'src/a\u2028.js', 'src/con.txt', 'src/COM1', 'src/name.', 'src/name ']) {
    const data = leaks(); data[0].File = unsafe;
    const report = importReport('gitleaks', data);
    assert.equal(report.signals[0].path, null);
    assert.equal(report.complete, false);
    assert.deepEqual(validateSignalDocument(report), []);
  }
});

test('SARIF URI decoding maps contained files and rejects remote, traversal, or double encoding', () => {
  const data = sarif();
  const artifact = data.runs[0].results[0].locations[0].physicalLocation.artifactLocation;
  artifact.uri = 'file:///project/src%20dir/main.py';
  assert.equal(importReport('sarif', data, { sourceRoot: '/project' }).signals[0].path, 'src dir/main.py');
  artifact.uri = 'src%20dir/main.py';
  assert.equal(importReport('sarif', data).signals[0].path, 'src dir/main.py');
  for (const unsafe of ['file://remote/project/main.py', 'file:///project/%2e%2e/out.py', 'file:///project/%252e%252e/out.py', 'https://host/main.py', 'file:///project/main.py?token=DO_NOT_KEEP']) {
    artifact.uri = unsafe;
    const report = importReport('sarif', data, { sourceRoot: '/project' });
    assert.equal(report.signals[0].path, null);
    assert.equal(report.complete, false);
    assert.ok(!JSON.stringify(report).includes('DO_NOT_KEEP'));
  }
});

test('SARIF reports historical and external-result omissions and rejects mismatched rule indices', () => {
  const data = sarif();
  data.runs[0].results[0].baselineState = 'absent';
  const absent = importReport('sarif', data);
  assert.equal(absent.complete, false);
  assert.equal(absent.signals.length, 0);
  delete data.runs[0].results[0].baselineState;
  data.runs[0].externalPropertyFileReferences = { results: [{ location: { uri: 'DO_NOT_KEEP' } }] };
  assert.equal(importReport('sarif', data).complete, false);
  data.runs[0].results[0].ruleIndex = 0;
  data.runs[0].results[0].ruleId = 'another-rule';
  assert.throws(() => importReport('sarif', data), /structure/);
});

test('SARIF namespaces are unambiguous when driver names and rule IDs contain slashes', () => {
  const data = sarif();
  data.runs[0].tool.driver.name = 'a/b';
  data.runs[0].tool.driver.rules[0].id = 'c';
  data.runs[0].results[0].ruleId = 'c';
  const other = clone(data.runs[0]);
  other.tool.driver.name = 'a'; other.tool.driver.rules[0].id = 'b/c'; other.results[0].ruleId = 'b/c';
  data.runs.push(other);
  const report = importReport('sarif', data);
  assert.equal(report.signals.length, 2);
  assert.notEqual(report.signals[0].fingerprint, report.signals[1].fingerprint);
});

test('Trivy OS package target labels are not exposed as source-file locations', () => {
  const data = trivy(); data.Results[0].Class = 'os-pkgs'; data.Results[0].Target = 'alpine 3.20';
  const report = importReport('trivy', data);
  assert.equal(report.signals.find(s => s.advisory).path, null);
  assert.equal(report.complete, false);
});
