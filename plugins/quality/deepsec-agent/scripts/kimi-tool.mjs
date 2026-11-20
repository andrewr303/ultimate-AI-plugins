#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { readFileSync, realpathSync, statSync } from 'node:fs';
import { isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

try {
  const action = process.argv[2];
  if (!['scan', 'doctor', 'rules'].includes(action) || process.argv.length !== 3) throw new Error('unsupported native tool');
  const chunks = [];
  let inputBytes = 0;
  for await (const chunk of process.stdin) {
    inputBytes += chunk.length;
    if (inputBytes > 1048576) throw new Error('tool input is too large');
    chunks.push(chunk);
  }
  const input = Buffer.concat(chunks).toString('utf8');
  const params = input.trim() ? JSON.parse(input) : {};
  if (!params || typeof params !== 'object' || Array.isArray(params) || Object.keys(params).length) {
    throw new Error('this tool takes no parameters; its repository root is bound during configuration');
  }
  const config = JSON.parse(readFileSync(new URL('../.deepsec-host.json', import.meta.url), 'utf8'));
  if (!isAbsolute(config.workspaceRoot ?? '')) throw new Error('missing absolute workspace root binding');
  const root = realpathSync(config.workspaceRoot);
  if (!statSync(root).isDirectory()) throw new Error('workspace root must be a directory');
  const cli = fileURLToPath(new URL('../bin/deepsec-agent.mjs', import.meta.url));
  const args = [cli, action, '--root', root];
  if (action === 'scan') args.push('--format', 'json');
  const result = spawnSync(process.execPath, args, {
    encoding: 'utf8', shell: false, timeout: 110000, maxBuffer: 16 * 1024 * 1024,
    windowsHide: true,
  });
  if (result.error) throw result.error;
  let output;
  try { output = JSON.parse(result.stdout); } catch { /* The error below retains bounded CLI diagnostics. */ }
  const scanReport = action === 'scan' && output && typeof output === 'object' && typeof output.schemaVersion === 'string' && Array.isArray(output.findings) && Array.isArray(output.coverage) && typeof output.complete === 'boolean';
  if (result.status !== 0 && !(scanReport && [1, 2].includes(result.status))) {
    throw new Error(result.stderr.trim() || `DeepSec exited with code ${result.status}`);
  }
  // Findings and partial coverage are useful evidence, not transport errors.
  // Preserve the report's explicit complete=false status on a partial scan.
  // Command failures and malformed output remain tool errors.
  if (output === undefined) throw new Error('DeepSec returned invalid JSON');
  process.stdout.write(`${JSON.stringify(output)}\n`);
} catch (error) {
  process.stderr.write(`DeepSec Kimi tool: ${error.message}\n`);
  process.exitCode = 2;
}
