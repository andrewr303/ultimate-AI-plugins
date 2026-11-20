import { scanWorkspace, listRules } from './scanner.mjs';
import { runEngines, doctorEngines, engineCatalog, parseEngineReport } from './adapters.mjs';
import { normalizeReport, applyBaseline } from './findings.mjs';
export { scanWorkspace, listRules, doctorEngines, engineCatalog, parseEngineReport };
export * from './findings.mjs';
export * from './reports.mjs';

/** Programmatic scripting API. External engines must be explicitly selected. */
export async function audit(root, options = {}) {
  if (!options || typeof options !== 'object' || Array.isArray(options)) throw new TypeError('Audit options must be an object');
  for (const [key, maximum] of Object.entries({ maxFiles: 2000, maxFileBytes: 262144, maxTotalBytes: 33554432, maxFindings: 1000, timeoutMs: 30000 })) {
    if (options[key] !== undefined && (!Number.isSafeInteger(options[key]) || options[key] < 1 || options[key] > maximum)) throw new TypeError(key + ' exceeds the supported positive integer range');
  }
  if (options.allowNetwork !== undefined && typeof options.allowNetwork !== 'boolean') throw new TypeError('allowNetwork must be boolean');
  if (options.includeNoisy !== undefined && typeof options.includeNoisy !== 'boolean') throw new TypeError('includeNoisy must be boolean');
  const engines = options.engines ?? ['deepsec'];
  if (!Array.isArray(engines) || engines.length === 0 || engines.some(x => !['deepsec', ...engineCatalog().map(e => e.id ?? e.name)].includes(x))) {
    throw new TypeError('Select known engines: deepsec, semgrep, gitleaks, osv-scanner, bandit, trivy');
  }
  const external = engines.filter(x => x !== 'deepsec');
  if (options.files?.length && external.length) throw new TypeError('Explicit file lists currently support the DeepSec engine only');
  const report = engines.includes('deepsec') ? await scanWorkspace(root, options) : {
    schemaVersion: '1.0', createdAt: new Date().toISOString(), findings: [], coverage: [],
  };
  if (external.length) {
    const result = await runEngines(root, { ...options, engines: external });
    report.findings.push(...result.findings);
    report.coverage.push(...result.coverage);
  }
  let normalized = normalizeReport(report);
  const cap = options.maxFindings ?? 1000;
  if (normalized.findings.length > cap) {
    const omitted = new Set(normalized.findings.slice(cap).map(finding => finding.engine));
    normalized = normalizeReport({ ...normalized, findings: normalized.findings.slice(0, cap), coverage: normalized.coverage.map(item => omitted.has(item.engine) ? { ...item, status: item.status === 'complete' ? 'partial' : item.status, reason: [item.reason, 'Combined report finding limit reached'].filter(Boolean).join('; ') } : item) });
  }
  return options.baseline ? applyBaseline(normalized, options.baseline) : normalized;
}

export async function doctor(root) {
  const fs = await import('node:fs/promises');
  const canonical = await fs.realpath(root);
  if (!(await fs.stat(canonical)).isDirectory()) throw new TypeError('Root must be a directory');
  return {
    name: 'deepsec-agent', version: '1.0.0', node: process.versions.node,
    localEngine: { available: true, registeredRules: listRules().length },
    externalEngines: await doctorEngines(canonical),
    boundaries: {
      builtinNetwork: false, arbitraryShellTool: false, automaticModelCalls: false,
      externalEngines: 'Explicit CLI selection only; installed tools are not an OS sandbox',
      scope: 'Server root is bound at startup. Source content is untrusted data.',
    },
  };
}
