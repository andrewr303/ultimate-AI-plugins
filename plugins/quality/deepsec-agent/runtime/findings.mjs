import { createHash } from 'node:crypto';

export const SEVERITIES = Object.freeze(['critical', 'high', 'medium', 'low', 'info']);
const COVERAGE_STATUSES = new Set(['complete', 'partial', 'error', 'unavailable', 'skipped']);
const MAX_FINDINGS = 10_000;

/** Defensive redaction, never a guarantee that arbitrary prose contains no secrets. */
export function redactText(value, limit = 8192) {
  if (typeof value !== 'string') return '';
  const outputLimit = Number.isSafeInteger(limit) && limit >= 0 ? Math.min(limit, 65_536) : 8192;
  return value.slice(0, Math.max(outputLimit, 32_768))
    .replace(/-----BEGIN (?:[A-Z0-9 ]* )?PRIVATE KEY-----[\s\S]*?(?:-----END (?:[A-Z0-9 ]* )?PRIVATE KEY-----|$)/g, '[REDACTED PRIVATE KEY]')
    .replace(/\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/g, '[REDACTED AWS KEY]')
    .replace(/\b(?:gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,})\b/g, '[REDACTED GITHUB TOKEN]')
    .replace(/\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{16,}\b/g, '[REDACTED API KEY]')
    .replace(/\b(Bearer|Basic)\s+[A-Za-z0-9._~+\/-]{8,}={0,2}/gi, '$1 [REDACTED]')
    .replace(/\b((?:password|passwd|pwd|secret|client_secret|token|access_token|refresh_token|api[_-]?key|authorization)[\w.-]*\s*[=:]\s*)(["'`])[^\n]*?(?:\2|(?=\n|$))/gi, '$1$2[REDACTED]$2')
    .replace(/\b((?:password|passwd|pwd|secret|client_secret|token|access_token|refresh_token|api[_-]?key|authorization)[\w.-]*\s*[=:]\s*)(?!["'`\s\[])([^\s,;<>]+)/gi, '$1[REDACTED]')
    .replace(/(https?:\/\/)[^\s/@:]+:[^\s/@]+@/gi, '$1[REDACTED]@')
    .replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g, '')
    .slice(0, outputLimit);
}

function boundedText(value, name, fallback, maxLength) {
  if (value === undefined || value === null) return fallback;
  if (typeof value !== 'string') throw new TypeError(`${name} must be a string`);
  return redactText(value, maxLength);
}

export function relativeFindingPath(value) {
  if (typeof value !== 'string' || !value || value.length > 4096) {
    throw new TypeError('Finding path must be a nonempty relative path');
  }
  const path = value.replaceAll('\\', '/');
  if (path.startsWith('/') || /^[A-Za-z][A-Za-z0-9+.-]*:/.test(path)
      || /[\u0000-\u001f\u007f]/.test(path)
      || path.split('/').some(part => part === '..' || part === '.' || part === '')) {
    throw new TypeError('Finding path must remain inside the workspace');
  }
  return path;
}

function hashField(value, name) {
  if (value === undefined) return undefined;
  if (typeof value !== 'string' || !/^[a-f0-9]{8,128}$/i.test(value)) {
    throw new TypeError(`${name} must be a hexadecimal digest`);
  }
  return value.toLowerCase();
}

function lineNumber(value, name, fallback = 1) {
  if (value === undefined) return fallback;
  if (!Number.isSafeInteger(value) || value < 1 || value > 1_000_000_000) {
    throw new TypeError(`${name} must be a positive integer`);
  }
  return value;
}

/** Only explicitly selected fields cross the boundary; raw scanner records do not. */
export function makeFinding(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new TypeError('Finding must be an object');
  const engine = boundedText(input.engine, 'engine', 'deepsec', 64);
  if (!/^[a-zA-Z0-9_.-]{1,64}$/.test(engine)) throw new TypeError('Invalid engine identifier');
  const ruleId = boundedText(input.ruleId, 'ruleId', 'unknown', 256);
  if (!ruleId.trim()) throw new TypeError('ruleId must not be blank');
  const path = relativeFindingPath(input.path);
  const line = lineNumber(input.line, 'line');
  const title = boundedText(input.title, 'title', ruleId, 512);
  const message = boundedText(input.message, 'message', title, 8192);
  const severity = input.severity ?? 'medium';
  if (!SEVERITIES.includes(severity)) throw new TypeError('Unknown finding severity');
  const confidence = input.confidence ?? 'low';
  if (!['low', 'medium', 'high'].includes(confidence)) throw new TypeError('Unknown finding confidence');
  const status = input.status ?? 'candidate';
  if (!['candidate', 'confirmed', 'dismissed'].includes(status)) throw new TypeError('Unknown finding status');
  const sourceHash = hashField(input.sourceHash, 'sourceHash');
  const evidenceHash = hashField(input.evidenceHash, 'evidenceHash');
  const fingerprint = createHash('sha256').update(JSON.stringify([
    engine, ruleId, path, evidenceHash ?? [line, message],
  ])).digest('hex');
  const finding = {
    id: `ds-${fingerprint.slice(0, 20)}`, fingerprint, engine, ruleId, title,
    severity, confidence, status, path, line, message,
    remediation: boundedText(input.remediation, 'remediation', 'Review the data flow and validate a minimal fix with regression tests.', 8192),
  };
  if (input.endLine !== undefined) {
    const endLine = lineNumber(input.endLine, 'endLine');
    if (endLine < line) throw new TypeError('endLine precedes line');
    finding.endLine = endLine;
  }
  if (sourceHash) finding.sourceHash = sourceHash;
  if (evidenceHash) finding.evidenceHash = evidenceHash;
  if (input.baseline !== undefined) {
    if (!['new', 'existing'].includes(input.baseline)) throw new TypeError('Invalid baseline state');
    finding.baseline = input.baseline;
  }
  return finding;
}

function normalizeCoverage(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new TypeError('Coverage must be an object');
  if (!COVERAGE_STATUSES.has(input.status)) throw new TypeError('Unknown coverage status');
  const engine = boundedText(input.engine, 'coverage engine', 'deepsec', 64);
  if (!/^[a-zA-Z0-9_.-]{1,64}$/.test(engine)) throw new TypeError('Invalid coverage engine');
  const coverage = { engine, status: input.status };
  if (input.reason !== undefined) coverage.reason = boundedText(input.reason, 'coverage reason', '', 4096);
  if (input.message !== undefined) coverage.message = boundedText(input.message, 'coverage message', '', 4096);
  if (input.gateMode !== undefined) coverage.gateMode = boundedText(input.gateMode, 'gateMode', '', 128);
  if (input.scope !== undefined) coverage.scope = boundedText(input.scope, 'coverage scope', '', 1024);
  if (input.snapshotLimited !== undefined) {
    if (typeof input.snapshotLimited !== 'boolean') throw new TypeError('snapshotLimited must be a boolean');
    coverage.snapshotLimited = input.snapshotLimited;
  }
  for (const key of ['files', 'filesScanned', 'filesRead', 'filesSkipped', 'filesRequested', 'filesVisited', 'entriesVisited', 'directoriesVisited', 'policyExcluded', 'bytesRead', 'bytesScanned', 'matchedFiles', 'findings', 'findingsCount', 'invalidEntries', 'scannerErrors', 'sources', 'snapshotBytes', 'skippedInputs', 'outputBytes', 'durationMs', 'exitCode', 'requested', 'read', 'skipped', 'totalBytes', 'activeRules', 'skippedNoisyRules']) {
    if (input[key] !== undefined) {
      if (!Number.isFinite(input[key]) || input[key] < 0) throw new TypeError(`Invalid coverage count ${key}`);
      coverage[key] = input[key];
    }
  }
  for (const field of ['counts', 'skipReasons', 'limits']) {
    if (input[field] !== undefined) {
      if (!input[field] || typeof input[field] !== 'object' || Array.isArray(input[field]) || Object.keys(input[field]).length > 32) throw new TypeError('Invalid coverage counts');
      coverage[field] = {};
      for (const [key, value] of Object.entries(input[field])) {
        if (!/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(key) || !Number.isFinite(value) || value < 0) throw new TypeError('Invalid coverage count');
        coverage[field][key] = value;
      }
    }
  }
  return coverage;
}

export function normalizeReport(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new TypeError('Report must be an object');
  if (input.schemaVersion !== undefined && input.schemaVersion !== '1.0') throw new TypeError('Unsupported report schemaVersion');
  if (!Array.isArray(input.findings) || input.findings.length > MAX_FINDINGS) throw new TypeError(`Report findings must be an array of at most ${MAX_FINDINGS}`);
  if (!Array.isArray(input.coverage) || input.coverage.length > 64) throw new TypeError('Report coverage must be an array of at most 64');
  const unique = new Map();
  for (const raw of input.findings) {
    const finding = makeFinding(raw);
    const previous = unique.get(finding.fingerprint);
    if (!previous || SEVERITIES.indexOf(finding.severity) < SEVERITIES.indexOf(previous.severity)) unique.set(finding.fingerprint, finding);
  }
  const findings = [...unique.values()].sort((a, b) => SEVERITIES.indexOf(a.severity) - SEVERITIES.indexOf(b.severity) || a.path.localeCompare(b.path) || a.line - b.line || a.ruleId.localeCompare(b.ruleId));
  const coverage = input.coverage.map(normalizeCoverage);
  if (input.createdAt !== undefined && (typeof input.createdAt !== 'string' || !input.createdAt)) throw new TypeError('Invalid report createdAt');
  const date = input.createdAt === undefined ? new Date() : new Date(input.createdAt);
  if (!Number.isFinite(date.getTime())) throw new TypeError('Invalid report createdAt');
  const bySeverity = Object.fromEntries(SEVERITIES.map(s => [s, 0]));
  const byEngine = Object.create(null);
  for (const f of findings) {
    bySeverity[f.severity] += 1;
    byEngine[f.engine] = (byEngine[f.engine] ?? 0) + 1;
  }
  const report = {
    schemaVersion: '1.0', createdAt: date.toISOString(),
    complete: coverage.length > 0 && coverage.every(c => c.status === 'complete'),
    findings, coverage,
    summary: {
      total: findings.length, new: findings.filter(f => f.baseline !== 'existing').length,
      existing: findings.filter(f => f.baseline === 'existing').length, bySeverity, byEngine,
    },
  };
  if (input.limits !== undefined) {
    if (!input.limits || typeof input.limits !== 'object' || Array.isArray(input.limits) || Object.keys(input.limits).length > 32) throw new TypeError('Invalid limits');
    report.limits = {};
    for (const [key, value] of Object.entries(input.limits)) {
      if (!/^[A-Za-z][A-Za-z0-9_]{0,63}$/.test(key) || !Number.isFinite(value) || value < 0) throw new TypeError('Invalid limit');
      report.limits[key] = value;
    }
  }
  return report;
}

export function createBaseline(report) {
  const normalized = normalizeReport(report);
  return { schemaVersion: '1.0', fingerprints: normalized.findings.map(f => f.fingerprint).sort() };
}

export function applyBaseline(report, baseline) {
  if (!baseline || baseline.schemaVersion !== '1.0' || !Array.isArray(baseline.fingerprints)
      || baseline.fingerprints.length > MAX_FINDINGS || baseline.fingerprints.some(f => typeof f !== 'string' || !/^[a-f0-9]{64}$/.test(f))) {
    throw new TypeError('Invalid baseline: expected schemaVersion 1.0 and SHA-256 fingerprints');
  }
  const known = new Set(baseline.fingerprints);
  const normalized = normalizeReport(report);
  return normalizeReport({ ...normalized, findings: normalized.findings.map(f => ({ ...f, baseline: known.has(f.fingerprint) ? 'existing' : 'new' })) });
}
