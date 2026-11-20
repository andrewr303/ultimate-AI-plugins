import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { engineCatalog, parseEngineReport, runBounded, runEngines, doctorEngines } from './adapters.mjs';

test('the five parser contracts produce candidates without raw source or secrets', () => {
  const root = path.join(os.tmpdir(), 'deepsec-parser-root');
  const fixtures = {
    semgrep: { results: [{ check_id: 'eval', path: 'src/main.js', start: { line: 2 }, extra: { message: 'Review eval', severity: 'WARNING', lines: 'secret source' } }], errors: [] },
    gitleaks: [{ RuleID: 'generic-api-key', File: 'src/main.js', StartLine: 2, Secret: 'unrecognized-secret-value', Match: 'secret source', Description: 'unrecognized-secret-value' }],
    'osv-scanner': { results: [{ source: { path: 'package-lock.json' }, packages: [{ package: { name: 'example', version: '1.0' }, vulnerabilities: [{ id: 'OSV-EXAMPLE', summary: 'Example advisory' }] }] }] },
    bandit: { results: [{ test_id: 'B602', test_name: 'subprocess_popen_with_shell_equals_true', filename: 'main.py', line_number: 2, issue_text: 'Review shell execution', issue_severity: 'HIGH', issue_confidence: 'MEDIUM', code: 'secret source' }], errors: [] },
    trivy: { SchemaVersion: 2, Results: [{ Target: 'package-lock.json', Vulnerabilities: [{ VulnerabilityID: 'CVE-EXAMPLE', PkgName: 'example', InstalledVersion: '1.0', Severity: 'HIGH', Title: 'Example advisory' }] }] },
  };
  assert.equal(engineCatalog().length, 5);
  for (const [engine, fixture] of Object.entries(fixtures)) {
    const result = parseEngineReport(engine, fixture, root);
    assert.equal(result.findings.length, 1, engine);
    assert.equal(result.findings[0].status, 'candidate', engine);
    assert.equal(result.coverage[0].status, 'complete', engine);
    assert.ok(!JSON.stringify(result).includes('secret source'), engine);
    assert.ok(!JSON.stringify(result).includes('unrecognized-secret-value'), engine);
    assert.ok(!JSON.stringify(result).includes(root), engine);
  }
});

test('absolute in-root paths normalize but traversal, foreign paths and URIs are omitted', () => {
  const root = path.join(os.tmpdir(), 'deepsec-parser-root');
  const reports = ['../outside.js', '/etc/passwd', 'C:\\private\\secret.txt', 'file:///etc/passwd', 'safe/../../outside.js'].map(File => ({ RuleID: 'secret', File, StartLine: 1 }));
  const result = parseEngineReport('gitleaks', reports, root);
  assert.equal(result.findings.length, 0);
  assert.equal(result.coverage[0].status, 'partial');
  const valid = parseEngineReport('gitleaks', [{ RuleID: 'secret', File: path.join(root, 'src/main.js'), StartLine: 1 }], root);
  assert.equal(valid.findings[0].path, 'src/main.js');
});

test('malformed reports, scanner errors and absent sources cannot appear clean', () => {
  for (const engine of engineCatalog()) {
    assert.equal(parseEngineReport(engine.id, {}, '/tmp/project').coverage[0].status, 'error', engine.id);
  }
  assert.equal(parseEngineReport('semgrep', { results: [], errors: [{}] }, '/tmp/project').coverage[0].status, 'partial');
  assert.equal(parseEngineReport('bandit', { results: [], errors: [{}] }, '/tmp/project').coverage[0].status, 'partial');
  assert.equal(parseEngineReport('osv-scanner', { results: [] }, '/tmp/project').coverage[0].status, 'partial');
  assert.equal(parseEngineReport('trivy', { Results: [] }, '/tmp/project').coverage[0].status, 'partial');
  assert.equal(parseEngineReport('gitleaks', [], '/tmp/project').coverage[0].status, 'complete');
});

test('Trivy infrastructure positions and severity are retained', () => {
  const parsed = parseEngineReport('trivy', { Results: [{ Target: 'deployment.yaml', Misconfigurations: [{ ID: 'AVD-EXAMPLE', Title: 'Privileged container', Severity: 'CRITICAL', Message: 'Review privileges', CauseMetadata: { StartLine: 8 } }] }] }, '/tmp/project');
  assert.equal(parsed.findings[0].line, 8);
  assert.equal(parsed.findings[0].severity, 'critical');
});

test('bounded runner enforces deadlines, output caps and captures process exit codes', async () => {
  const timeout = await runBounded(process.execPath, ['-e', 'setInterval(()=>{},1000)'], { timeoutMs: 50 });
  assert.equal(timeout.ok, false);
  assert.equal(timeout.reason, 'timeout');
  const huge = await runBounded(process.execPath, ['-e', "process.stdout.write('x'.repeat(1000000))"], { maxOutputBytes: 1024 });
  assert.equal(huge.ok, false);
  assert.equal(huge.reason, 'output-limit');
  assert.equal(huge.stdout, '');
  const failure = await runBounded(process.execPath, ['-e', "process.stderr.write('private scanner diagnostic'); process.exit(7)"]);
  assert.equal(failure.exitCode, 7);
  assert.ok(!JSON.stringify(failure).includes('private scanner diagnostic'));
});

test('network-dependent scanners require explicit opt-in even when absent', async () => {
  const result = await runEngines('/tmp', { engines: ['osv-scanner', 'trivy'] });
  assert.equal(result.findings.length, 0);
  assert.deepEqual(result.coverage.map(item => item.status), ['skipped', 'skipped']);
  await assert.rejects(runEngines('/tmp', { engines: ['osv-scanner'], allowNetwork: 'false' }), /boolean/);
});

test('OSV omitted empty vulnerability lists remain valid but empty package sources are partial', () => {
  const clean = parseEngineReport('osv-scanner', { results: [{ source: { path: 'package-lock.json' }, packages: [{ package: { name: 'example', version: '1.0' } }] }] }, '/tmp/project');
  assert.equal(clean.coverage[0].status, 'complete');
  assert.equal(clean.findings.length, 0);
  assert.equal(parseEngineReport('osv-scanner', { results: [{ source: { path: 'package-lock.json' }, packages: [] }] }, '/tmp/project').coverage[0].status, 'partial');
});

test('workspace-shadowed executables are never considered installed', async () => {
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-adapter-test-'));
  const previousPath = process.env.PATH;
  try {
    await fs.writeFile(path.join(temporary, 'semgrep'), '#!/bin/sh\nexit 0\n', { mode: 0o700 });
    process.env.PATH = `${temporary}${path.delimiter}.`;
    const engines = await doctorEngines(temporary);
    assert.equal(engines.find(item => item.id === 'semgrep').available, false);
  } finally {
    process.env.PATH = previousPath;
    await fs.rm(temporary, { recursive: true, force: true });
  }
});

test('external nonzero exit is reported without trusting valid-looking stdout', async () => {
  if (process.platform === 'win32') return;
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-adapter-test-'));
  const root = path.join(temporary, 'project');
  const bin = path.join(temporary, 'bin');
  const previousPath = process.env.PATH;
  try {
    await fs.mkdir(root);
    await fs.mkdir(bin);
    await fs.writeFile(path.join(root, 'main.py'), 'print("safe fixture")\n');
    await fs.writeFile(path.join(bin, 'bandit'), `#!${process.execPath}\nconsole.log(JSON.stringify({results:[],errors:[]}));process.exit(2);\n`, { mode: 0o700 });
    process.env.PATH = `${bin}${path.delimiter}${previousPath}`;
    const result = await runEngines(root, { engines: ['bandit'] });
    assert.equal(result.coverage[0].status, 'error');
    assert.match(result.coverage[0].reason, /exit code 2/);
  } finally {
    process.env.PATH = previousPath;
    await fs.rm(temporary, { recursive: true, force: true });
  }
});

test('snapshot caps and symlinks remain visible in adapter coverage', async () => {
  if (process.platform === 'win32') return;
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-adapter-test-'));
  const root = path.join(temporary, 'project');
  const bin = path.join(temporary, 'bin');
  const previousPath = process.env.PATH;
  try {
    await fs.mkdir(root);
    await fs.mkdir(bin);
    await fs.writeFile(path.join(root, 'main.py'), 'print("safe fixture")\n');
    await fs.symlink('/etc/passwd', path.join(root, 'outside.py'));
    await fs.writeFile(path.join(root, 'oversized.py'), 'a'.repeat(262145));
    await fs.writeFile(path.join(bin, 'bandit'), `#!${process.execPath}\nconsole.log(JSON.stringify({results:[],errors:[]}));\n`, { mode: 0o700 });
    process.env.PATH = `${bin}${path.delimiter}${previousPath}`;
    const result = await runEngines(root, { engines: ['bandit'] });
    assert.equal(result.coverage[0].status, 'partial');
    assert.equal(result.coverage[0].files, 1);
    assert.equal(result.coverage[0].filesSkipped, 2);
  } finally {
    process.env.PATH = previousPath;
    await fs.rm(temporary, { recursive: true, force: true });
  }
});

test('caller snapshot limits are enforced and project scanner controls cannot suppress scans', async () => {
  if (process.platform === 'win32') return;
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-adapter-test-'));
  const root = path.join(temporary, 'project');
  const bin = path.join(temporary, 'bin');
  const previousPath = process.env.PATH;
  try {
    await fs.mkdir(root);
    await fs.mkdir(bin);
    await fs.writeFile(path.join(root, '.semgrepignore'), '*\n');
    await fs.writeFile(path.join(root, '.gitignore'), '*\n');
    await fs.writeFile(path.join(root, 'main.js'), 'eval(input);\n');
    await fs.writeFile(path.join(bin, 'semgrep'), `#!${process.execPath}\nconst fs=require('node:fs'),path=require('node:path');const target=process.argv.at(-1);if(fs.existsSync(path.join(target,'.semgrepignore'))||fs.existsSync(path.join(target,'.gitignore'))||!process.argv.includes('--no-git-ignore'))process.exit(2);console.log(JSON.stringify({results:[],errors:[]}));\n`, { mode: 0o700 });
    process.env.PATH = `${bin}${path.delimiter}${previousPath}`;
    const complete = await runEngines(root, { engines: ['semgrep'] });
    assert.equal(complete.coverage[0].status, 'complete');
    assert.equal(complete.coverage[0].counts.sourceControlFilesExcluded, 2);
    const limited = await runEngines(root, { engines: ['semgrep'], maxFileBytes: 2 });
    assert.equal(limited.coverage[0].status, 'partial');
    assert.equal(limited.coverage[0].files, 0);
  } finally {
    process.env.PATH = previousPath;
    await fs.rm(temporary, { recursive: true, force: true });
  }
});
