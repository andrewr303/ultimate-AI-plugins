#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { realpath, stat } from 'node:fs/promises';
import { isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

// Read the binding inside the process: portable Codex manifests only expand
// PLUGIN_ROOT/PLUGIN_DATA, whereas Claude also expands environment variables.
// Inferring a scan root from a plugin's working directory would scan the wrong tree.
const requestedRoot = process.env.DEEPSEC_WORKSPACE_ROOT;
if (!requestedRoot || !isAbsolute(requestedRoot)) {
  process.stderr.write('DeepSec: set DEEPSEC_WORKSPACE_ROOT to an absolute authorized repository path, or generate a bound host package with scripts/configure-host.mjs.\n');
  process.exit(2);
}

try {
  const root = await realpath(requestedRoot);
  if (!(await stat(root)).isDirectory()) throw new Error('workspace root must be a directory');
  const cli = fileURLToPath(new URL('../bin/deepsec-agent.mjs', import.meta.url));
  const child = spawn(process.execPath, [cli, 'serve', '--root', root], { stdio: 'inherit', shell: false });
  child.on('error', error => { process.stderr.write(`DeepSec: ${error.message}\n`); process.exitCode = 2; });
  child.on('exit', (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    else process.exitCode = code ?? 2;
  });
  for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
} catch (error) {
  process.stderr.write(`DeepSec: ${error.message}\n`);
  process.exitCode = 2;
}
