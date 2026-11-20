/** Original bounded host bridge for the bundled DeepSec matcher registry. */
import fs from 'node:fs';
import path from 'node:path';
import { Worker } from 'node:worker_threads';
import { createDefaultRegistry } from './upstream-matchers.mjs';

export const SCAN_LIMITS = Object.freeze({
  maxFiles: 2000,
  maxFileBytes: 262144,
  maxTotalBytes: 33554432,
  maxFindings: 1000,
  timeoutMs: 30000,
});

/** Metadata only: upstream examples can contain credentials or source snippets. */
export function listRules() {
  return createDefaultRegistry().getAll().map(matcher => ({
    ruleId: matcher.slug,
    title: matcher.slug.replaceAll('-', ' '),
    description: matcher.description,
    filePatterns: [...matcher.filePatterns],
    noiseTier: matcher.noiseTier,
    gated: Boolean(matcher.requires),
  }));
}

function boundedOptions(options) {
  if (!options || typeof options !== 'object' || Array.isArray(options)) throw new TypeError('Scan options must be an object');
  const result = {};
  for (const [name, maximum] of Object.entries(SCAN_LIMITS)) {
    const value = options[name] ?? maximum;
    if (!Number.isSafeInteger(value) || value < 1 || value > maximum) {
      throw new RangeError(`${name} must be an integer between 1 and ${maximum}`);
    }
    result[name] = value;
  }
  if (options.includeNoisy !== undefined && typeof options.includeNoisy !== 'boolean') throw new TypeError('includeNoisy must be a boolean');
  result.includeNoisy = options.includeNoisy === true;
  if (options.files !== undefined) {
    if (!Array.isArray(options.files) || options.files.length > SCAN_LIMITS.maxFiles) throw new TypeError('files must be an array with at most 2000 relative paths');
    result.files = [...new Set(options.files.map(value => {
      if (typeof value !== 'string' || value.length === 0 || value.length > 4096 || /[\x00-\x1f\x7f]/.test(value)) throw new TypeError('Each file must be a nonempty relative path');
      const normalized = value.replaceAll('\\', '/');
      if (normalized.startsWith('/') || /^[a-z]:/i.test(normalized) || normalized.split('/').some(part => part === '..' || part === '')) throw new Error('File path escapes workspace or is invalid');
      const relative = normalized.replace(/^\.\//, '');
      if (relative.split('/').includes('.') || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(relative) || relative === '') throw new Error('Each file must name a file under the workspace');
      return relative;
    }))];
  }
  return result;
}

function emptyReport(options) {
  return {
    schemaVersion: '1.0',
    createdAt: new Date().toISOString(),
    findings: [],
    coverage: [{ engine: 'deepsec', status: 'partial', reason: 'Scan did not finish', gateMode: 'file-patterns-only', filesVisited: 0, filesRead: 0, filesSkipped: 0, bytesRead: 0, limits: Object.fromEntries(Object.entries(options).filter(([, value]) => Number.isSafeInteger(value))) }],
    summary: { total: 0, candidates: 0, bySeverity: { critical: 0, high: 0, medium: 0, low: 0, info: 0 }, partial: true },
    complete: false,
  };
}

/**
 * Local static scan only. No source, lifecycle scripts, plugins, git config or
 * uploaded instructions are executed. A worker deadline also bounds regex work.
 */
export async function scanWorkspace(root, options = {}) {
  if (typeof root !== 'string' || root.length === 0 || root.includes('\0')) throw new TypeError('Workspace root must be a path');
  const limits = boundedOptions(options);
  const rootReal = fs.realpathSync(path.resolve(root));
  if (!fs.statSync(rootReal).isDirectory()) throw new Error('Workspace root must be a directory');
  return new Promise(resolve => {
    let report = emptyReport(limits);
    let settled = false;
    const worker = new Worker(new URL('./scanner-worker.mjs', import.meta.url), {
      workerData: { root: rootReal, options: limits },
      // The bundled ES worker needs no host loaders or CLI mode flags.
      // Replaying process.execArgv can include stdin-only --input-type and
      // process-global options rejected by Worker (including test runners).
      execArgv: [],
      resourceLimits: { maxOldGenerationSizeMb: 256, stackSizeMb: 8 },
      // Inherit the runtime's proxy/CA configuration, but never stream logs into
      // the JSON-RPC protocol. This worker contains only the bundled matchers.
      stdout: true,
      stderr: true,
    });
    worker.stdout.resume();
    worker.stderr.resume();
    const finish = (reason, failed = false) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (reason) {
        report.coverage[0] = { ...report.coverage[0], status: failed ? 'error' : 'partial', reason };
        report.complete = false;
        report.summary.partial = true;
      }
      resolve(report);
    };
    const timer = setTimeout(() => {
      // Resolve immediately after requesting termination: no synchronous matcher
      // in the worker can prevent the parent from enforcing this deadline.
      void worker.terminate();
      finish('Worker deadline reached; results may be incomplete');
    }, limits.timeoutMs);
    worker.on('message', message => {
      if (message?.type === 'progress' || message?.type === 'result') report = message.report;
      if (message?.type === 'result') finish();
    });
    worker.on('error', () => finish('Scanner worker failed; coverage is incomplete', true));
    worker.on('exit', code => {
      if (!settled) finish(code === 0 ? 'Scanner worker exited without a result' : 'Scanner worker terminated; coverage is incomplete', code !== 0);
    });
  });
}
