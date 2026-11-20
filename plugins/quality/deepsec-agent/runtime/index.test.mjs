import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { audit } from './index.mjs';

test('combined finding limit applies across built-in and external engines', { skip: process.platform === 'win32' }, async t => {
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-combined-'));
  t.after(() => fs.rm(temporary, { recursive: true, force: true }));
  const root = path.join(temporary, 'repo'); const tools = path.join(temporary, 'tools');
  await fs.mkdir(root); await fs.mkdir(tools);
  await fs.writeFile(path.join(root, 'app.js'), 'export function unsafe(input) { return eval(input); }\n');
  await fs.writeFile(path.join(tools, 'gitleaks'), `#!${process.execPath}\nprocess.stdout.write(JSON.stringify([{RuleID:'fixture-secret',File:process.argv.at(-1)+'/app.js',StartLine:1}]));\n`, { mode: 0o700 });
  const originalPath = process.env.PATH;
  process.env.PATH = tools + path.delimiter + originalPath;
  t.after(() => { process.env.PATH = originalPath; });
  const report = await audit(root, { engines: ['deepsec', 'gitleaks'], maxFindings: 1 });
  assert.equal(report.findings.length, 1);
  assert.equal(report.findings[0].engine, 'gitleaks');
  assert.equal(report.complete, false);
  assert(report.coverage.some(item => item.reason?.includes('Combined report finding limit')));
});

test('external-only audits reject invalid bounds instead of silently replacing them', async () => {
  await assert.rejects(audit('.', { engines: ['gitleaks'], maxFiles: -1 }), TypeError);
  await assert.rejects(audit('.', { engines: ['gitleaks'], allowNetwork: 'yes' }), TypeError);
});
