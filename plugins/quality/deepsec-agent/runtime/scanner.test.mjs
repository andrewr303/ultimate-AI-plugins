import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { listRules, scanWorkspace, SCAN_LIMITS } from './scanner.mjs';

function fixture(t, files = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'deepsec-scan-test-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  for (const [name, value] of Object.entries(files)) {
    fs.mkdirSync(path.dirname(path.join(root, name)), { recursive: true });
    fs.writeFileSync(path.join(root, name), value);
  }
  return root;
}

test('catalog contains the broad upstream registry without snippets/examples', () => {
  const rules = listRules();
  assert.ok(rules.length > 150);
  assert.ok(rules.some(rule => rule.ruleId === 'rce'));
  assert.ok(rules.every(rule => !('examples' in rule) && !('snippet' in rule)));
});

test('vulnerable source yields hashed static candidates without source snippets or root paths', async t => {
  const secret = 'DO_NOT_EXPORT_PRIVATE_SOURCE_391731';
  const root = fixture(t, { 'src/unsafe.js': `execSync(request.query.command); // ${secret}\n` });
  const report = await scanWorkspace(root);
  const finding = report.findings.find(item => item.ruleId === 'rce');
  assert.ok(finding);
  assert.equal(finding.status, 'candidate');
  assert.equal(finding.path, 'src/unsafe.js');
  assert.equal(finding.line, 1);
  assert.match(finding.sourceHash, /^[a-f0-9]{64}$/);
  assert.match(finding.evidenceHash, /^[a-f0-9]{64}$/);
  assert.equal(report.coverage[0].gateMode, 'file-patterns-only');
  assert.equal(report.coverage[0].status, 'complete');
  assert.equal(JSON.stringify(report).includes(secret), false);
  assert.equal(JSON.stringify(report).includes(root), false);
  assert.equal(JSON.stringify(report).includes('request.query.command'), false);
});

test('simple safe fixture produces no findings', async t => {
  const root = fixture(t, { 'safe.js': 'export const add = (a, b) => a + b;\n' });
  const report = await scanWorkspace(root);
  assert.equal(report.findings.length, 0);
  assert.equal(report.complete, true);
  assert.equal(report.coverage[0].filesRead, 1);
});

test('rejects traversal, absolute, Windows absolute and invalid paths before scanning', async t => {
  const root = fixture(t);
  for (const name of ['../escape.js', '/etc/passwd', 'C:\\secrets.js', 'a/../../b.js', 'a/./b.js', '//host/a.js', '.', 'https:abc.js', 'a\0b.js']) {
    await assert.rejects(scanWorkspace(root, { files: [name] }));
  }
  await assert.rejects(scanWorkspace(root, { files: 'unsafe.js' }));
});

test('explicit file scans reject symlink escapes and report incomplete coverage', async t => {
  const root = fixture(t);
  const outside = fixture(t, { 'outside.js': 'execSync(command);\n' });
  fs.symlinkSync(path.join(outside, 'outside.js'), path.join(root, 'link.js'));
  const report = await scanWorkspace(root, { files: ['link.js'] });
  assert.equal(report.findings.length, 0);
  assert.equal(report.complete, false);
  assert.equal(report.coverage[0].skipReasons.symlink, 1);
  assert.equal(report.coverage[0].filesRead, 0);
});

test('does not recurse through a symlink directory', async t => {
  const root = fixture(t);
  const outside = fixture(t, { 'outside.js': 'eval(command);\n' });
  fs.symlinkSync(outside, path.join(root, 'linked'));
  const report = await scanWorkspace(root);
  assert.equal(report.findings.length, 0);
  assert.equal(report.coverage[0].skipReasons.symlink, 1);
});

test('excludes build/dependency/state/credential content by policy', async t => {
  const root = fixture(t, {
    'node_modules/bad/index.js': 'eval(input);\n',
    '.deepsec/data/code.js': 'eval(input);\n',
    'build/code.js': 'eval(input);\n',
    '.env': 'SECRET=not-for-the-agent\n',
    'good.js': 'export const answer = 42;\n',
  });
  const report = await scanWorkspace(root);
  assert.equal(report.findings.length, 0);
  assert.equal(report.coverage[0].filesRead, 1);
  assert.ok(report.coverage[0].policyExcluded >= 4);
  assert.equal(report.complete, true);
});

test('file byte cap skips oversized content and marks partial', async t => {
  const root = fixture(t, { 'big.js': `eval(input);${' '.repeat(100)}` });
  const report = await scanWorkspace(root, { maxFileBytes: 32 });
  assert.equal(report.coverage[0].skipReasons['file-byte-limit'], 1);
  assert.equal(report.findings.length, 0);
  assert.equal(report.complete, false);
});

test('total byte cap and file count cap are explicit partial results', async t => {
  const root = fixture(t, { 'one.js': 'eval(input);\n', 'two.js': 'eval(other);\n' });
  const total = await scanWorkspace(root, { files: ['one.js', 'two.js'], maxTotalBytes: 15 });
  assert.equal(total.coverage[0].skipReasons['total-byte-limit'], 1);
  assert.ok(total.coverage[0].bytesRead <= 15);
  assert.equal(total.complete, false);
  const files = await scanWorkspace(root, { files: ['one.js', 'two.js'], maxFiles: 1 });
  assert.equal(files.coverage[0].filesVisited, 1);
  assert.match(files.coverage[0].reason, /File count limit/);
});

test('finding cap bounds result length and marks partial', async t => {
  const root = fixture(t, { 'unsafe.js': 'eval(input);\nexecSync(other);\n' });
  const report = await scanWorkspace(root, { maxFindings: 1 });
  assert.equal(report.findings.length, 1);
  assert.equal(report.complete, false);
  assert.match(report.coverage[0].reason, /Finding count limit/);
});

test('binary, malformed UTF-8 and missing inputs are reported as skipped', async t => {
  const root = fixture(t, { 'binary.js': Buffer.from([0, 1, 2]), 'invalid.js': Buffer.from([0xff, 0xfe]) });
  const report = await scanWorkspace(root, { files: ['binary.js', 'invalid.js', 'missing.js'] });
  assert.equal(report.complete, false);
  assert.equal(report.coverage[0].filesSkipped, 3);
  assert.equal(report.coverage[0].skipReasons['binary-file'], 1);
  assert.equal(report.coverage[0].skipReasons['invalid-utf8'], 1);
  assert.equal(report.coverage[0].skipReasons['unreadable-or-missing'], 1);
});

test('FIFO inputs cannot block worker reads', { skip: process.platform === 'win32' }, async t => {
  const root = fixture(t);
  execFileSync('mkfifo', [path.join(root, 'pipe.js')]);
  const report = await scanWorkspace(root, { files: ['pipe.js'] });
  assert.equal(report.coverage[0].skipReasons['special-file'], 1);
  assert.equal(report.coverage[0].filesRead, 0);
});

test('deadline remains enforced outside worker regex execution', async t => {
  const root = fixture(t, { 'unsafe.js': 'eval(input);\n' });
  const report = await scanWorkspace(root, { timeoutMs: 1 });
  assert.equal(report.complete, false);
  assert.match(report.coverage[0].reason, /deadline/);
});

test('limits cannot exceed hard ceilings or contain invalid numbers', async t => {
  const root = fixture(t);
  for (const [name, maximum] of Object.entries(SCAN_LIMITS)) {
    for (const value of [maximum + 1, 0, -1, 1.5, '1', Infinity]) {
      await assert.rejects(scanWorkspace(root, { [name]: value }));
    }
  }
  await assert.rejects(scanWorkspace(root, { includeNoisy: 'true' }));
});


test('stdin module API invocation does not pass input-type to file-backed workers', async t => {
  const root = fixture(t, { 'unsafe.js': 'eval(input);\n' });
  const scannerUrl = new URL('./scanner.mjs', import.meta.url).href;
  const script = `import { scanWorkspace } from ${JSON.stringify(scannerUrl)};\nconst report = await scanWorkspace(${JSON.stringify(root)});\nconsole.log(JSON.stringify(report));`;
  for (const inputType of [['--input-type=module'], ['--input-type', 'module']]) {
    const stdout = execFileSync(process.execPath, [...inputType, '--no-warnings', '-'], {
      input: script, encoding: 'utf8', timeout: 5000,
    });
    const report = JSON.parse(stdout);
    assert.equal(report.coverage[0].status, 'complete');
    assert.ok(report.findings.some(finding => finding.ruleId === 'rce'));
  }
});
