/** Original scanner I/O boundary. The matcher implementation remains upstream. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { parentPort, workerData } from 'node:worker_threads';
import { createDefaultRegistry } from './upstream-matchers.mjs';
import { minimatch } from './glob.mjs';
import { makeFinding } from './findings.mjs';

const { root, options } = workerData;
const EXCLUDED_DIRS = new Set(['.git', 'node_modules', '.deepsec', '.deepsec-agent', 'dist', 'build', 'target', '.next', 'coverage', '.turbo', '.cache', '.venv', 'venv']);
const MAX_ENTRIES = 20000;
const MAX_DIRS = 2000;
const skipReasons = {};
const limits = Object.fromEntries(Object.entries(options).filter(([, value]) => Number.isSafeInteger(value)));
const allRules = createDefaultRegistry().getAll();
const matchers = allRules.filter(matcher => options.includeNoisy || matcher.noiseTier !== 'noisy');
const findings = [];
const fingerprints = new Set();
const coverage = {
  engine: 'deepsec', status: 'complete',
  reason: 'Static candidates only; vulnerability confirmation requires source review',
  gateMode: 'file-patterns-only', activeRules: matchers.length,
  skippedNoisyRules: allRules.length - matchers.length,
  filesVisited: 0, filesRead: 0, filesSkipped: 0, bytesRead: 0,
  entriesVisited: 0, directoriesVisited: 0, policyExcluded: 0,
  skipReasons, limits,
};
let halted = false;

function report() {
  const bySeverity = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
  for (const finding of findings) bySeverity[finding.severity] = (bySeverity[finding.severity] ?? 0) + 1;
  return { schemaVersion: '1.0', createdAt: new Date().toISOString(), findings,
    coverage: [coverage], complete: coverage.status === 'complete',
    summary: { total: findings.length, candidates: findings.length, bySeverity, partial: coverage.status !== 'complete' } };
}

function partial(reason) {
  coverage.status = 'partial';
  coverage.reason = reason;
}
function skip(reason, incomplete = true) {
  coverage.filesSkipped++;
  skipReasons[reason] = (skipReasons[reason] ?? 0) + 1;
  if (incomplete) partial('Some inputs were skipped; inspect skipReasons');
}
function inside(candidate) {
  const relative = path.relative(root, candidate);
  return relative === '' || (!relative.startsWith(`..${path.sep}`) && relative !== '..' && !path.isAbsolute(relative));
}
function policyExcluded(relative) {
  const parts = relative.split('/');
  if (parts.some(part => EXCLUDED_DIRS.has(part))) return true;
  const name = parts.at(-1);
  // Environment/credential contents are deliberately not exposed to this host
  // scanner. A separately selected secret engine has its own redacted adapter.
  return /^(?:\.env(?:\..*)?|\.npmrc|\.pypirc|credentials|id_rsa|id_ed25519)$/i.test(name) || /\.(?:pem|key|p12|pfx)$/i.test(name);
}
function safeFile(relative) {
  const absolute = path.resolve(root, relative);
  if (!inside(absolute)) { skip('outside-root'); return null; }
  let cursor = root;
  try {
    for (const part of relative.split('/')) {
      if (part === '.' || part === '') continue;
      cursor = path.join(cursor, part);
      if (fs.lstatSync(cursor).isSymbolicLink()) { skip('symlink'); return null; }
    }
    const canonical = fs.realpathSync(absolute);
    if (!inside(canonical)) { skip('outside-root'); return null; }
    const stat = fs.lstatSync(absolute);
    if (!stat.isFile()) { skip('special-file'); return null; }
    if (stat.size > options.maxFileBytes) { skip('file-byte-limit'); return null; }
    if (coverage.bytesRead + stat.size > options.maxTotalBytes) {
      skip('total-byte-limit'); halted = true; return null;
    }
    const flags = fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0) | (fs.constants.O_NONBLOCK ?? 0);
    const fd = fs.openSync(absolute, flags);
    try {
      const opened = fs.fstatSync(fd);
      if (!opened.isFile() || opened.dev !== stat.dev || opened.ino !== stat.ino) { skip('changed-file'); return null; }
      // Linux can check the opened descriptor itself, including a directory
      // swapped between validation and open. Other systems retain inode checks.
      if (process.platform === 'linux' && !inside(fs.realpathSync(`/proc/self/fd/${fd}`))) { skip('outside-root'); return null; }
      const remaining = Math.min(options.maxFileBytes, options.maxTotalBytes - coverage.bytesRead);
      const buffer = Buffer.alloc(Math.max(0, remaining) + 1);
      let length = 0;
      while (length < buffer.length) {
        const count = fs.readSync(fd, buffer, length, buffer.length - length, null);
        if (count === 0) break;
        length += count;
      }
      if (length > remaining) { skip('file-grew-or-byte-limit'); return null; }
      coverage.bytesRead += length;
      const bytes = buffer.subarray(0, length);
      if (bytes.includes(0)) { skip('binary-file'); return null; }
      let content;
      try { content = new TextDecoder('utf-8', { fatal: true }).decode(bytes).replaceAll('\r\n', '\n'); }
      catch { skip('invalid-utf8'); return null; }
      coverage.filesRead++;
      return content;
    } finally { fs.closeSync(fd); }
  } catch { skip('unreadable-or-missing'); return null; }
}
function hash(text) { return crypto.createHash('sha256').update(text).digest('hex'); }
function scanFile(relative) {
  if (halted) return;
  if (relative.length > 4096 || /[\x00-\x1f\x7f]/.test(relative) || /^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(relative)) { skip('invalid-file-path'); return; }
  if (coverage.filesVisited >= options.maxFiles) { partial('File count limit reached'); halted = true; return; }
  coverage.filesVisited++;
  if (policyExcluded(relative)) { coverage.policyExcluded++; return; }
  const applicable = matchers.filter(matcher => matcher.filePatterns.some(pattern => minimatch(relative, pattern, { dot: true, nocase: false })));
  if (applicable.length === 0) { skip('unsupported-file-type', false); return; }
  const content = safeFile(relative);
  if (content === null) return;
  const sourceHash = hash(content);
  const lines = content.split('\n');
  for (const matcher of applicable) {
    let matches;
    try { matches = matcher.match(content, relative); }
    catch { skipReasons['matcher-error'] = (skipReasons['matcher-error'] ?? 0) + 1; partial('A matcher failed; coverage is incomplete'); continue; }
    if (!Array.isArray(matches)) { partial('A matcher returned invalid candidates'); continue; }
    for (const candidate of matches) {
      const hitLines = Array.isArray(candidate.lineNumbers) ? candidate.lineNumbers : [1];
      for (const hit of hitLines) {
        const line = Number.isSafeInteger(hit) && hit > 0 && hit <= lines.length ? hit : 1;
        const finding = makeFinding({
          engine: 'deepsec', ruleId: matcher.slug,
          title: matcher.slug.replaceAll('-', ' '), severity: 'medium',
          confidence: matcher.requires || matcher.noiseTier === 'noisy' ? 'low' : 'medium',
          status: 'candidate', path: relative, line, sourceHash,
          evidenceHash: hash(lines[line - 1].trim()),
          message: `${matcher.description}. This is a static candidate, not a confirmed vulnerability.`,
          remediation: 'Trace attacker-controlled input, validation, authorization and the sensitive operation. Confirm reachability, propose the smallest safe patch, and rerun relevant tests and this scan.',
        });
        if (fingerprints.has(finding.fingerprint)) continue;
        if (findings.length >= options.maxFindings) { partial('Finding count limit reached'); halted = true; return; }
        fingerprints.add(finding.fingerprint);
        findings.push(finding);
      }
    }
  }
  if (coverage.filesRead % 10 === 0) parentPort.postMessage({ type: 'progress', report: report() });
}

function walk(directory, prefix = '') {
  if (halted) return;
  if (++coverage.directoriesVisited > MAX_DIRS) { partial('Directory count limit reached'); halted = true; return; }
  let handle;
  try { handle = fs.opendirSync(directory); }
  catch { skip('unreadable-directory'); return; }
  try {
    for (let entry = handle.readSync(); entry && !halted; entry = handle.readSync()) {
      if (++coverage.entriesVisited > MAX_ENTRIES) { partial('Directory entry limit reached'); halted = true; break; }
      const relative = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isSymbolicLink()) { skip('symlink'); continue; }
      if (entry.isDirectory()) {
        if (EXCLUDED_DIRS.has(entry.name)) { coverage.policyExcluded++; continue; }
        // Do not follow a directory changed into a symlink between enumeration
        // and recursion, including internal links (all symlinks are excluded).
        try {
          const actual = fs.lstatSync(path.join(directory, entry.name));
          if (actual.isSymbolicLink() || !actual.isDirectory() || !inside(fs.realpathSync(path.join(directory, entry.name)))) { skip('changed-directory'); continue; }
        } catch { skip('unreadable-directory'); continue; }
        walk(path.join(directory, entry.name), relative);
      } else if (entry.isFile()) scanFile(relative);
      else skip('special-file');
    }
  } finally { handle.closeSync(); }
}

try {
  if (options.files) for (const relative of options.files) scanFile(relative);
  else walk(root);
  parentPort.postMessage({ type: 'result', report: report() });
} catch {
  coverage.status = 'error';
  coverage.reason = 'Scanner failed; coverage is incomplete';
  parentPort.postMessage({ type: 'result', report: report() });
}
