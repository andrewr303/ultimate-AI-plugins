import fs from 'node:fs/promises';
import { constants as fsConstants, realpathSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { makeFinding } from './findings.mjs';

const RULES = fileURLToPath(new URL('../rules/', import.meta.url));
const CATALOG = Object.freeze([
  { id: 'semgrep', binary: 'semgrep', scope: 'Bundled original JavaScript and Python structural rules', networkRequired: false },
  { id: 'gitleaks', binary: 'gitleaks', scope: 'Directory secrets; installed built-in rules; full redaction', networkRequired: false, freshness: 'Mature optional exception; inspected code activity exceeded the research freshness screen' },
  { id: 'osv-scanner', binary: 'osv-scanner', scope: 'Dependency sources and advisory matches', networkRequired: true },
  { id: 'bandit', binary: 'bandit', scope: 'Python security analysis using installed plugins', networkRequired: false, freshness: 'Mature optional exception; inspected code activity exceeded the research freshness screen' },
  { id: 'trivy', binary: 'trivy', scope: 'Filesystem dependencies and infrastructure misconfiguration', networkRequired: true },
]);
const EXCLUDED = new Set(['.git', '.hg', '.svn', 'node_modules', '.deepsec', '.deepsec-agent', 'dist', 'build', 'target', '.next', 'coverage', '.venv', 'venv', '__pycache__']);
const SCANNER_CONTROLS = new Set(['.gitignore', '.semgrepignore', '.gitleaks.toml', '.gitleaksignore', '.bandit', 'bandit.yaml', 'bandit.yml', '.trivyignore', '.trivyignore.yaml', 'trivy.yaml', 'trivy.yml', 'osv-scanner.toml', 'osv-scanner.yaml', 'osv-scanner.yml', '.osv-scanner.toml']);
const MAX_FINDINGS = 1000;
const boundedLimit = (value, fallback, maximum) => Number.isSafeInteger(value) && value > 0 ? Math.min(value, maximum) : fallback;
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = (value, fallback = '') => typeof value === 'string' ? value.slice(0, 4000) : fallback;
const safeLine = value => Number.isInteger(value) && value > 0 && value < 100000000 ? value : 1;
const severity = value => ({ CRITICAL: 'critical', HIGH: 'high', ERROR: 'high', MEDIUM: 'medium', WARNING: 'medium', LOW: 'low', INFO: 'info', UNKNOWN: 'info' })[String(value).toUpperCase()] || 'medium';

export function engineCatalog() { return CATALOG.map(engine => ({ ...engine })); }

function within(root, candidate) {
  const rel = path.relative(root, candidate);
  return rel === '' || (!rel.startsWith(`..${path.sep}`) && rel !== '..' && !path.isAbsolute(rel));
}

function resultPath(value, root) {
  if (typeof value !== 'string' || !value || value.length > 4096 || /[\x00-\x1f]/.test(value)) throw new Error('Invalid source path');
  const normalized = value.replaceAll('\\', '/').replace(/ \([^/]*\)$/, '');
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(normalized)) throw new Error('Source URI or foreign absolute path rejected');
  if (normalized.split('/').includes('..')) throw new Error('Path traversal rejected');
  const absolute = path.resolve(root, normalized);
  if (!within(path.resolve(root), absolute)) throw new Error('Source path outside root');
  const relative = path.relative(root, absolute).split(path.sep).join('/');
  if (!relative || relative === '.') throw new Error('A source file path is required');
  return relative;
}

/** Normalize allowlisted fields only. Raw snippets, secret values and scanner stderr never escape. */
export function parseEngineReport(engine, data, root) {
  if (!CATALOG.some(item => item.id === engine)) throw new Error('Unknown scanner engine');
  const findings = [];
  let invalid = 0;
  let scannerErrors = 0;
  let sources = 0;
  let packages = 0;
  let malformed = false;
  const add = fields => {
    if (findings.length >= MAX_FINDINGS) { invalid += 1; return; }
    try {
      if (!isObject(fields) || !fields.ruleId) throw new Error('Missing rule');
      findings.push(makeFinding({ engine, status: 'candidate', confidence: 'medium', ...fields, path: resultPath(fields.path, root), line: safeLine(fields.line) }));
    } catch { invalid += 1; }
  };
  const each = (items, callback) => {
    if (!Array.isArray(items)) { malformed = true; return; }
    if (items.length > 10000) invalid += items.length - 10000;
    for (const item of items.slice(0, 10000)) {
      if (!isObject(item)) { invalid += 1; continue; }
      try { callback(item); } catch { invalid += 1; }
    }
  };
  if (engine === 'gitleaks') {
    each(data, finding => add({ ruleId: text(finding.RuleID), title: 'Potential hardcoded credential', severity: 'high', path: finding.File, line: finding.StartLine,
      message: 'A secret-detection rule matched this location. Secret values and matched source text are intentionally omitted.',
      remediation: 'Verify the credential, revoke or rotate it if exposed, and remove it from source and affected history.' }));
  } else if (engine === 'semgrep') {
    if (!isObject(data) || !Array.isArray(data.results) || !Array.isArray(data.errors)) malformed = true;
    else {
      scannerErrors = data.errors.length;
      each(data.results, finding => {
        if (!isObject(finding.extra) || !isObject(finding.start)) { invalid += 1; return; }
        add({ ruleId: text(finding.check_id), title: text(finding.check_id, 'Structural security candidate'), severity: severity(finding.extra.severity), path: finding.path, line: finding.start.line,
          message: text(finding.extra.message, 'Structural rule matched; investigate the data flow.'), remediation: 'Trace untrusted inputs to this operation, verify protections, and add a regression test before changing code.' });
      });
    }
  } else if (engine === 'bandit') {
    if (!isObject(data) || !Array.isArray(data.results) || !Array.isArray(data.errors)) malformed = true;
    else {
      scannerErrors = data.errors.length;
      each(data.results, finding => add({ ruleId: text(finding.test_id), title: text(finding.test_name, 'Python security candidate'), severity: severity(finding.issue_severity), confidence: ['LOW', 'MEDIUM', 'HIGH'].includes(finding.issue_confidence) ? finding.issue_confidence.toLowerCase() : 'low',
        path: finding.filename, line: finding.line_number, message: text(finding.issue_text, 'Python security rule matched.'), remediation: 'Review the Python operation in context and replace unsafe behavior with an appropriate API; verify with a regression test.' }));
    }
  } else if (engine === 'osv-scanner') {
    if (!isObject(data) || !Array.isArray(data.results)) malformed = true;
    else {
      if (Array.isArray(data.errors)) scannerErrors += data.errors.length;
      each(data.results, source => {
        if (!isObject(source.source) || !Array.isArray(source.packages)) { invalid += 1; return; }
        resultPath(source.source.path, root);
        sources += 1;
        each(source.packages, item => {
          if (!isObject(item.package) || (item.vulnerabilities !== undefined && !Array.isArray(item.vulnerabilities))) { invalid += 1; return; }
          packages += 1;
          each(item.vulnerabilities || [], advisory => add({ ruleId: text(advisory.id), title: text(advisory.summary, 'Dependency advisory match'), severity: severity(advisory.database_specific?.severity), confidence: 'medium', path: source.source.path, line: 1,
            message: `File-level advisory match for ${text(item.package.name, 'dependency')} ${text(item.package.version)}; line 1 is a file anchor. Reachability and exploitability have not been verified.`,
            remediation: 'Check the advisory and available fixed versions, update the dependency and lockfile, and run the project tests.' }));
        });
      });
    }
  } else if (engine === 'trivy') {
    if (!isObject(data) || !Array.isArray(data.Results)) malformed = true;
    else {
      each(data.Results, result => {
        resultPath(result.Target, root);
        sources += 1;
        if (result.Vulnerabilities !== undefined) each(result.Vulnerabilities, advisory => add({ ruleId: text(advisory.VulnerabilityID), title: text(advisory.Title, 'Dependency advisory match'), severity: severity(advisory.Severity), path: result.Target, line: 1,
          message: `File-level advisory match for ${text(advisory.PkgName, 'dependency')} ${text(advisory.InstalledVersion)}; line 1 is a file anchor. Reachability and exploitability have not been verified.`,
          remediation: advisory.FixedVersion ? `Review and update to an appropriate fixed version: ${text(advisory.FixedVersion)}; run the project tests.` : 'Review the advisory, mitigations and available upgrades; run the project tests.' }));
        if (result.Misconfigurations !== undefined) each(result.Misconfigurations, issue => add({ ruleId: text(issue.ID || issue.AVDID), title: text(issue.Title, 'Infrastructure configuration candidate'), severity: severity(issue.Severity), path: result.Target,
          line: issue.CauseMetadata?.StartLine, message: text(issue.Message, 'Infrastructure configuration rule matched.'), remediation: 'Review the configuration against its deployment context, apply the least-privilege setting, and validate the deployment.' }));
      });
    }
  }
  const noSources = (['osv-scanner', 'trivy'].includes(engine) && sources === 0) || (engine === 'osv-scanner' && packages === 0);
  const partial = malformed || invalid > 0 || scannerErrors > 0 || noSources;
  const reasons = [malformed && 'Malformed or unsupported scanner report', invalid > 0 && `${invalid} invalid or excess report entries omitted`, scannerErrors > 0 && `${scannerErrors} scanner errors`, noSources && 'No supported dependency or infrastructure sources reported'].filter(Boolean);
  return { findings, coverage: [{ engine, status: malformed ? 'error' : partial ? 'partial' : 'complete', findings: findings.length, invalidEntries: invalid, scannerErrors, ...(sources ? { sources } : {}), ...(reasons.length ? { reason: reasons.join('; ') } : {}) }] };
}

async function resolveExecutable(binary, root) {
  const forbiddenRoot = root ? await fs.realpath(root).catch(() => path.resolve(root)) : path.resolve(process.cwd());
  const directories = (process.env.PATH || '').split(path.delimiter).filter(entry => entry && path.isAbsolute(entry));
  const suffixes = process.platform === 'win32' ? ['.exe', '.com'] : [''];
  for (const directory of directories) {
    if (within(forbiddenRoot, path.resolve(directory))) continue;
    for (const suffix of suffixes) {
      const candidate = path.join(directory, binary + suffix);
      try {
        const actual = await fs.realpath(candidate);
        if (within(forbiddenRoot, actual)) continue;
        const stat = await fs.stat(actual);
        if (!stat.isFile()) continue;
        await fs.access(actual, fsConstants.X_OK);
        return actual;
      } catch { /* Try the next trusted PATH entry. */ }
    }
  }
  return null;
}

export async function doctorEngines(root) {
  return Promise.all(CATALOG.map(async engine => ({ ...engine, available: Boolean(await resolveExecutable(engine.binary, root)) })));
}

function scannerEnvironment(root) {
  const env = {};
  const allowed = ['PATH', 'SystemRoot', 'WINDIR', 'LANG', 'LC_ALL', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE', 'NODE_EXTRA_CA_CERTS'];
  for (const key of allowed) if (typeof process.env[key] === 'string') env[key] = process.env[key];
  env.PATH = (env.PATH || '').split(path.delimiter).filter(directory => {
    if (!directory || !path.isAbsolute(directory)) return false;
    try { return !within(path.resolve(root || process.cwd()), realpathSync(directory)); } catch { return false; }
  }).join(path.delimiter);
  env.PYTHONNOUSERSITE = '1';
  env.SEMGREP_SEND_METRICS = 'off';
  return env;
}

/** Low-level testable runner; raw stdout is internal and must never be put in reports. */
export function runBounded(executable, args, { cwd, env = scannerEnvironment(), timeoutMs = 30000, maxOutputBytes = 4194304 } = {}) {
  timeoutMs = Math.min(30000, Math.max(20, Number(timeoutMs) || 30000));
  maxOutputBytes = Math.min(4194304, Math.max(128, Number(maxOutputBytes) || 4194304));
  return new Promise(resolve => {
    let child;
    let settled = false;
    let reason;
    let outputBytes = 0;
    const stdout = [];
    const finish = (exitCode, signal) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({ ok: !reason, exitCode, signal, reason, stdout: reason ? '' : Buffer.concat(stdout).toString('utf8'), outputBytes });
    };
    const kill = why => {
      if (reason) return;
      reason = why;
      try { if (process.platform !== 'win32' && child?.pid) process.kill(-child.pid, 'SIGKILL'); else child?.kill('SIGKILL'); } catch { child?.kill('SIGKILL'); }
    };
    const timer = setTimeout(() => kill('timeout'), timeoutMs);
    try {
      child = spawn(executable, args, { cwd, env, shell: false, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true, detached: process.platform !== 'win32' });
      child.on('error', () => { reason = 'process-error'; finish(null, null); });
      child.stdout.on('data', chunk => { outputBytes += chunk.length; if (outputBytes > maxOutputBytes) kill('output-limit'); else stdout.push(chunk); });
      child.stderr.on('data', chunk => { outputBytes += chunk.length; if (outputBytes > maxOutputBytes) kill('output-limit'); });
      child.on('close', finish);
    } catch { reason = 'process-error'; finish(null, null); }
  });
}

async function snapshotWorkspace(root, destination, limits) {
  const actualRoot = await fs.realpath(root);
  const state = { files: 0, bytes: 0, skipped: 0, policyExcluded: 0, visited: 0, limited: false, timedOut: false };
  const deadline = Date.now() + limits.timeoutMs;
  const expired = () => {
    if (Date.now() < deadline) return false;
    state.limited = true;
    state.timedOut = true;
    return true;
  };
  const walk = async (directory, relative = '') => {
    if (state.limited || expired()) return;
    const actualDirectory = await fs.realpath(directory);
    if (!within(actualRoot, actualDirectory)) { state.skipped += 1; return; }
    const stream = await fs.opendir(directory);
    for await (const entry of stream) {
      if (expired()) break;
      if (++state.visited > 10000 || state.files >= limits.maxFiles) { state.limited = true; break; }
      if (EXCLUDED.has(entry.name)) continue;
      if (SCANNER_CONTROLS.has(entry.name)) { state.policyExcluded += 1; continue; }
      const rel = path.join(relative, entry.name);
      const source = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) { state.skipped += 1; continue; }
      if (entry.isDirectory()) { try { await walk(source, rel); } catch { state.skipped += 1; } continue; }
      if (!entry.isFile()) { state.skipped += 1; continue; }
      let handle;
      try {
        const before = await fs.lstat(source);
        if (!before.isFile()) throw new Error('Not a regular file');
        const actual = await fs.realpath(source);
        if (!within(actualRoot, actual)) throw new Error('Outside root');
        const flags = fsConstants.O_RDONLY | (fsConstants.O_NOFOLLOW || 0) | (fsConstants.O_NONBLOCK || 0);
        handle = await fs.open(source, flags);
        const stat = await handle.stat();
        if (!stat.isFile() || stat.dev !== before.dev || stat.ino !== before.ino) throw new Error('Changed file');
        if (process.platform === 'linux' && !within(actualRoot, await fs.realpath(`/proc/self/fd/${handle.fd}`))) throw new Error('Opened file outside root');
        if (stat.size > limits.maxFileBytes || state.bytes + stat.size > limits.maxTotalBytes) { state.skipped += 1; continue; }
        const remaining = Math.min(limits.maxFileBytes, limits.maxTotalBytes - state.bytes);
        const buffer = Buffer.alloc(remaining + 1);
        let length = 0;
        while (length < buffer.length && !expired()) {
          const read = await handle.read(buffer, length, buffer.length - length, length);
          if (read.bytesRead === 0) break;
          length += read.bytesRead;
        }
        if (state.timedOut || length > remaining) { state.skipped += 1; continue; }
        const after = await handle.stat();
        if (after.size !== length || after.mtimeMs !== stat.mtimeMs) { state.skipped += 1; continue; }
        if (buffer.subarray(0, length).includes(0)) continue;
        const target = path.join(destination, rel);
        await fs.mkdir(path.dirname(target), { recursive: true, mode: 0o700 });
        await fs.writeFile(target, buffer.subarray(0, length), { mode: 0o600 });
        state.files += 1;
        state.bytes += length;
      } catch { state.skipped += 1; }
      finally { await handle?.close(); }
    }
  };
  await walk(actualRoot);
  return state;
}

function scannerArgs(engine, target) {
  if (engine === 'semgrep') return ['scan', '--json', '--metrics', 'off', '--disable-version-check', '--no-git-ignore', '--disable-nosem', '--config', path.join(RULES, 'semgrep.yml'), target];
  if (engine === 'gitleaks') return ['dir', '--no-banner', '--redact=100', '--report-format', 'json', '--report-path', '-', '--exit-code', '0', '--config', path.join(RULES, 'gitleaks.toml'), '--ignore-gitleaks-allow', target];
  if (engine === 'osv-scanner') return ['scan', 'source', '--format', 'json', '--recursive', target];
  if (engine === 'bandit') return ['--recursive', '--format', 'json', '--quiet', '--ini', path.join(RULES, 'bandit.ini'), '--configfile', path.join(RULES, 'bandit.yml'), '--ignore-nosec', target];
  if (engine === 'trivy') return ['--config', path.join(RULES, 'trivy.yml'), 'filesystem', '--format', 'json', '--scanners', 'vuln,misconfig', '--exit-code', '0', '--ignorefile', '', target];
  throw new Error('Unknown scanner engine');
}

/** Explicitly requested external scanners only. There is no installation or arbitrary command facility. */
export async function runEngines(root, { engines = [], allowNetwork = false, timeoutMs = 30000, maxOutputBytes = 4194304, maxFiles, maxFileBytes, maxTotalBytes, maxFindings } = {}) {
  if (!Array.isArray(engines) || engines.length > CATALOG.length || engines.some(engine => !CATALOG.some(item => item.id === engine))) throw new Error('Unknown or invalid engine selection');
  if (typeof allowNetwork !== 'boolean') throw new Error('allowNetwork must be a boolean');
  const findings = [];
  const coverage = [];
  const selected = [...new Set(engines)];
  const limits = { maxFiles: boundedLimit(maxFiles, 2000, 2000), maxFileBytes: boundedLimit(maxFileBytes, 262144, 262144), maxTotalBytes: boundedLimit(maxTotalBytes, 33554432, 33554432), maxFindings: boundedLimit(maxFindings, MAX_FINDINGS, MAX_FINDINGS), timeoutMs: boundedLimit(timeoutMs, 30000, 30000) };
  if (!selected.length) return { findings, coverage };
  let temporary;
  let snapshot;
  try {
    for (const engine of selected) {
      const metadata = CATALOG.find(item => item.id === engine);
      if (metadata.networkRequired && allowNetwork !== true) { coverage.push({ engine, status: 'skipped', reason: 'Requires explicit --allow-network for vulnerability databases and advisory services' }); continue; }
      const executable = await resolveExecutable(metadata.binary, root);
      if (!executable) { coverage.push({ engine, status: 'unavailable', reason: 'Scanner is not installed on a trusted absolute PATH entry' }); continue; }
      if (!temporary) {
        temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-agent-'));
        await fs.chmod(temporary, 0o700);
        const target = path.join(temporary, 'workspace');
        await fs.mkdir(target, { mode: 0o700 });
        snapshot = await snapshotWorkspace(root, target, limits);
      }
      if (snapshot.timedOut) { coverage.push({ engine, status: 'error', reason: 'Bounded source snapshot exceeded its deadline', files: snapshot.files }); continue; }
      const target = path.join(temporary, 'workspace');
      const result = await runBounded(executable, scannerArgs(engine, target), { cwd: temporary, env: scannerEnvironment(await fs.realpath(root)), timeoutMs: limits.timeoutMs, maxOutputBytes });
      if (!result.ok) { coverage.push({ engine, status: 'error', reason: `Scanner stopped: ${result.reason}`, files: snapshot.files }); continue; }
      const allowedCodes = engine === 'bandit' || engine === 'osv-scanner' ? [0, 1] : [0];
      if (!allowedCodes.includes(result.exitCode)) { coverage.push({ engine, status: 'error', reason: `Scanner failed with exit code ${result.exitCode ?? 'unknown'}`, files: snapshot.files }); continue; }
      let parsed;
      try { parsed = parseEngineReport(engine, JSON.parse(result.stdout), target); }
      catch { coverage.push({ engine, status: 'error', reason: 'Scanner returned invalid JSON', files: snapshot.files }); continue; }
      const remaining = Math.max(0, limits.maxFindings - findings.length);
      const truncated = parsed.findings.length > remaining;
      findings.push(...parsed.findings.slice(0, remaining));
      for (const item of parsed.coverage) {
        if (truncated) {
          if (item.status === 'complete') item.status = 'partial';
          item.reason = [item.reason, 'Finding count limit reached'].filter(Boolean).join('; ');
        }
        if ((snapshot.skipped || snapshot.limited || snapshot.files === 0) && item.status === 'complete') item.status = 'partial';
        if (snapshot.skipped || snapshot.limited || snapshot.files === 0) item.reason = [item.reason, 'Bounded snapshot omitted inputs or had no supported text files'].filter(Boolean).join('; ');
        coverage.push({ ...item, files: snapshot.files, bytesRead: snapshot.bytes, filesSkipped: snapshot.skipped, counts: { sourceControlFilesExcluded: snapshot.policyExcluded }, scope: metadata.scope });
      }
    }
  } finally { if (temporary) await fs.rm(temporary, { recursive: true, force: true }); }
  return { findings, coverage };
}
