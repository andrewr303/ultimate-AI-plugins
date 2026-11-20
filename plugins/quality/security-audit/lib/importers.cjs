'use strict';

// Report adapters deliberately copy metadata only. Scanner prose, source snippets,
// secret matches, tokens, and scanner-generated fingerprints are never retained.
const { createHash } = require('node:crypto');
const { isSafeRelativeSourcePath, PATH_FORBIDDEN_CHARACTER } = require('../skills/security-audit/validate-findings.cjs');
const FORMATS = Object.freeze(['sarif', 'semgrep', 'gitleaks', 'trivy', 'osv']);
const SEVERITIES = Object.freeze(['unknown', 'info', 'low', 'medium', 'high', 'critical']);
const MAX_SIGNALS = 50000;
const MAX_ENTRIES = 250000;
const MAX_DEPTH = 64;
const ROOT_KEYS = ['schema_version', 'kind', 'tool', 'complete', 'warnings', 'signals'];
const SIGNAL_KEYS = ['fingerprint', 'tool', 'rule_id', 'title', 'path', 'line', 'severity', 'package', 'version', 'advisory'];
const WARNINGS = Object.freeze({
  errors: 'The report contains scanner errors or unsuccessful invocations; coverage is incomplete.',
  skipped: 'The report records skipped analysis; coverage is incomplete.',
  path: 'A location was omitted because it could not be mapped to a safe repository-relative path.',
  unsupported: 'The report contains result categories that this adapter does not import.',
  suppression: 'The report contains suppressed or excluded results; coverage is incomplete.',
});
const CONTROL = PATH_FORBIDDEN_CHARACTER;
const METADATA = /^[\p{L}\p{N}][\p{L}\p{N}._:/@+~()#=!*,\- ]*$/u;
const VALUE_METADATA = /^[\p{L}\p{N}@~^<>=][\p{L}\p{N}._:/@+~()#=!*,%<>^\- ]*$/u;
const OWN = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
function invalid() { throw new Error('Invalid or unsupported scanner report structure.'); }
function object(value) { if (!value || typeof value !== 'object' || Array.isArray(value)) invalid(); return value; }
function array(value) { if (!Array.isArray(value) || value.length > MAX_SIGNALS) invalid(); return value; }
function metadata(value, max = 256, flexible = false) {
  if (typeof value !== 'string' || !value.length || value.length > max || value !== value.trim() || CONTROL.test(value) || !(flexible ? VALUE_METADATA : METADATA).test(value) || /:\/\//.test(value)) invalid();
  return value;
}
function optionalMetadata(value, max) { return value == null || value === '' ? null : metadata(value, max, true); }
function positiveLine(value) { if (value == null) return null; if (!Number.isSafeInteger(value) || value < 1) invalid(); return value; }
function optionalArray(value) { return value == null ? [] : array(value); }
function exactKeys(value, allowed) { return Object.keys(value).every(k => allowed.includes(k)); }
function normalizeSeverity(value) {
  if (value == null || value === '') return 'unknown';
  if (typeof value !== 'string') invalid();
  const key = value.toLowerCase();
  return ({ error: 'high', warning: 'medium', warn: 'medium', note: 'info', informational: 'info', none: 'info', moderate: 'medium' })[key] || (SEVERITIES.includes(key) ? key : 'unknown');
}
function numericSeverity(value) {
  if (typeof value === 'string' && /^\d{1,2}(?:\.\d+)?$/.test(value)) value = Number(value);
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 10) return 'unknown';
  return value >= 9 ? 'critical' : value >= 7 ? 'high' : value >= 4 ? 'medium' : value > 0 ? 'low' : 'info';
}
function higher(a, b) { return SEVERITIES.indexOf(a) >= SEVERITIES.indexOf(b) ? a : b; }
function boundedData(root) {
  const stack = [[root, 0]];
  const seen = new Set();
  let entries = 0;
  while (stack.length) {
    const [value, depth] = stack.pop();
    if (++entries > MAX_ENTRIES || depth > MAX_DEPTH) invalid();
    if (value && typeof value === 'object') {
      if (seen.has(value)) invalid();
      seen.add(value);
      if (Array.isArray(value) && value.length > MAX_SIGNALS) invalid();
      for (const child of Object.values(value)) stack.push([child, depth + 1]);
    } else if (typeof value === 'string' && value.length > 5 * 1024 * 1024) invalid();
    else if (!['string', 'number', 'boolean'].includes(typeof value) && value !== null) invalid();
  }
}
function normalizedSlashes(value) { return value.replace(/\\/g, '/'); }
function safePathParts(value) {
  return typeof value === 'string' && value.length > 0 && value.length <= 4096 && !CONTROL.test(value) && !/[<>"|?*%]/.test(value) && !value.split('/').some(p => p === '..' || p === '.' || p === '');
}
function isSafeRelativePath(value) {
  return safePathParts(value) && isSafeRelativeSourcePath(value);
}
function validateSourceRoot(root) {
  if (root == null) return null;
  if (typeof root !== 'string') throw new Error('Source root must be an absolute path without traversal or URI syntax.');
  const value = normalizedSlashes(root).replace(/\/$/, '');
  const absolute = value.startsWith('/') || /^[A-Za-z]:\//.test(value);
  const parts = value.startsWith('/') ? value.slice(1) : value.slice(3);
  if (!absolute || !parts || !safePathParts(parts) || parts.includes(':')) throw new Error('Source root must be an absolute path without traversal or URI syntax.');
  return value;
}
function relativeLocation(raw, sourceRoot, warning) {
  if (raw == null || raw === '') return null;
  if (typeof raw !== 'string') invalid();
  let value = normalizedSlashes(raw);
  if (value.startsWith('./')) value = value.slice(2);
  if (isSafeRelativePath(value)) return value;
  if (sourceRoot) {
    const windows = /^[A-Za-z]:\//.test(sourceRoot);
    const prefix = sourceRoot + '/';
    const matches = windows ? value.toLowerCase().startsWith(prefix.toLowerCase()) : value.startsWith(prefix);
    if (matches) {
      const relative = value.slice(prefix.length);
      if (isSafeRelativePath(relative)) return relative;
    }
  }
  warning('path');
  return null;
}
function fingerprintSignal(signal) {
  const identity = [signal.tool, signal.rule_id, signal.path, signal.line, signal.package, signal.version, signal.advisory];
  return 'sig:' + createHash('sha256').update(JSON.stringify(identity)).digest('hex');
}
function sarifRule(driver, rule) { const id = metadata(rule, 256); return `${driver.length}:${driver}/${id.length}:${id}`; }
function titleFor(tool, rule) { return `${tool} signal: ${rule}`; }
function validateSignalDocument(doc) {
  const errors = [];
  const fail = text => { if (!errors.includes(text)) errors.push(text); };
  try {
    boundedData(doc);
    if (!doc || typeof doc !== 'object' || Array.isArray(doc) || !exactKeys(doc, ROOT_KEYS) || ROOT_KEYS.some(k => !OWN(doc, k))) return ['Invalid tool-signals envelope.'];
    if (doc.schema_version !== '1.0.0' || doc.kind !== 'tool-signals' || !FORMATS.includes(doc.tool) || typeof doc.complete !== 'boolean') fail('Invalid tool-signals envelope.');
    if (!Array.isArray(doc.warnings) || doc.warnings.length > Object.keys(WARNINGS).length || doc.warnings.some(w => !Object.values(WARNINGS).includes(w)) || new Set(doc.warnings).size !== doc.warnings.length) fail('Invalid warnings.');
    if (Array.isArray(doc.warnings) && doc.warnings.length && doc.complete !== false) fail('Incomplete imports must not claim completeness.');
    if (!Array.isArray(doc.signals) || doc.signals.length > MAX_SIGNALS) return [...errors, 'Invalid signals array.'];
    const seen = new Set();
    let previous = '';
    for (const signal of doc.signals) {
      if (!signal || typeof signal !== 'object' || Array.isArray(signal) || !exactKeys(signal, SIGNAL_KEYS) || SIGNAL_KEYS.some(k => !OWN(signal, k))) { fail('Invalid signal structure.'); continue; }
      if (signal.tool !== doc.tool || !SEVERITIES.includes(signal.severity)) fail('Invalid signal tool or severity.');
      try {
        metadata(signal.rule_id, 512);
        if (signal.title !== titleFor(signal.tool, signal.rule_id)) fail('Signal title must contain only generated metadata.');
        for (const key of ['package', 'version', 'advisory']) if (signal[key] !== null) metadata(signal[key], 512, true);
        if (signal.path !== null && !isSafeRelativePath(signal.path)) fail('Invalid signal location.');
        positiveLine(signal.line);
        if (signal.path === null && signal.line !== null) fail('A line requires a safe path.');
      } catch { fail('Invalid signal metadata.'); }
      if (typeof signal.fingerprint !== 'string' || !/^sig:[a-f0-9]{64}$/.test(signal.fingerprint) || signal.fingerprint !== fingerprintSignal(signal)) fail('Invalid signal fingerprint.');
      if (seen.has(signal.fingerprint)) fail('Duplicate signal fingerprints.');
      if (previous && previous > signal.fingerprint) fail('Signals must be sorted by fingerprint.');
      seen.add(signal.fingerprint); previous = signal.fingerprint;
    }
  } catch { fail('Invalid tool-signals document.'); }
  return errors;
}
function importReport(format, data, options = {}) {
  if (!FORMATS.includes(format)) throw new Error('Unsupported report format. Use sarif, semgrep, gitleaks, trivy, or osv.');
  object(options);
  if (!exactKeys(options, ['sourceRoot'])) throw new Error('Unsupported importer option.');
  const sourceRoot = validateSourceRoot(options.sourceRoot);
  boundedData(data);
  const warnings = new Set();
  const found = new Map();
  const warn = key => warnings.add(WARNINGS[key]);
  const location = value => relativeLocation(value, sourceRoot, warn);
  function add({ rule, path: rawPath = null, line = null, severity = 'unknown', package: pkg = null, version = null, advisory = null, mapped = false }) {
    const ruleId = metadata(rule, 512);
    const relative = mapped ? rawPath : location(rawPath);
    const normalizedLine = positiveLine(line);
    const signal = { fingerprint: '', tool: format, rule_id: ruleId, title: titleFor(format, ruleId), path: relative, line: relative === null ? null : normalizedLine, severity, package: optionalMetadata(pkg, 512), version: optionalMetadata(version, 512), advisory: optionalMetadata(advisory, 512) };
    if (!SEVERITIES.includes(severity)) invalid();
    signal.fingerprint = fingerprintSignal(signal);
    const prior = found.get(signal.fingerprint);
    if (prior) prior.severity = higher(prior.severity, severity);
    else found.set(signal.fingerprint, signal);
    if (found.size > MAX_SIGNALS) invalid();
  }
  if (format === 'semgrep') {
    object(data);
    const results = array(data.results);
    if (optionalArray(data.errors).length) warn('errors');
    if (optionalArray(data.skipped_rules).length) warn('skipped');
    if (data.paths != null) { object(data.paths); if (optionalArray(data.paths.skipped).length) warn('skipped'); }
    for (const result of results) {
      object(result); object(result.extra); object(result.start);
      if (typeof result.path !== 'string' || !result.path.length) invalid();
      if (result.extra.is_ignored === true) warn('suppression');
      add({ rule: result.check_id, path: result.path, line: positiveLine(result.start.line), severity: normalizeSeverity(result.extra.severity) });
    }
  } else if (format === 'gitleaks') {
    for (const result of array(data)) {
      object(result);
      if (typeof result.File !== 'string' || !result.File.length) invalid();
      add({ rule: result.RuleID, path: result.File, line: positiveLine(result.StartLine), severity: 'unknown' });
    }
  } else if (format === 'sarif') {
    object(data);
    if (data.version !== '2.1.0') invalid();
    for (const run of array(data.runs)) {
      object(run); object(run.tool); object(run.tool.driver);
      const driver = metadata(run.tool.driver.name, 200);
      const rules = optionalArray(run.tool.driver.rules).map(object);
      const artifacts = optionalArray(run.artifacts).map(object);
      if (run.externalPropertyFileReferences != null) {
        const external = object(run.externalPropertyFileReferences);
        if (optionalArray(external.results).length) warn('unsupported');
      }
      for (const invocation of optionalArray(run.invocations)) {
        object(invocation);
        if (invocation.executionSuccessful != null && typeof invocation.executionSuccessful !== 'boolean') invalid();
        if (invocation.executionSuccessful === false) warn('errors');
        for (const note of optionalArray(invocation.toolExecutionNotifications)) { object(note); if (note.level === 'error') warn('errors'); }
      }
      for (const result of array(run.results)) {
        object(result);
        let rule = null;
        if (result.ruleIndex != null) { if (!Number.isSafeInteger(result.ruleIndex) || result.ruleIndex < 0 || result.ruleIndex >= rules.length) invalid(); rule = rules[result.ruleIndex]; }
        if (rule && result.ruleId != null && rule.id !== result.ruleId) invalid();
        if (!rule && typeof result.ruleId === 'string') rule = rules.find(r => r.id === result.ruleId) || null;
        const ruleId = result.ruleId == null ? (rule && rule.id) : result.ruleId;
        if (optionalArray(result.suppressions).length) warn('suppression');
        if (result.baselineState != null && !['new', 'unchanged', 'updated', 'absent'].includes(result.baselineState)) invalid();
        if (result.baselineState === 'absent') { warn('suppression'); continue; }
        if (result.kind != null && !['fail', 'pass', 'open', 'review', 'notApplicable', 'informational'].includes(result.kind)) invalid();
        if (result.kind === 'pass' || result.kind === 'notApplicable') continue;
        let severity = normalizeSeverity(result.level || (rule && rule.defaultConfiguration && object(rule.defaultConfiguration).level));
        if (rule && rule.properties != null) { object(rule.properties); const score = numericSeverity(rule.properties['security-severity']); if (score !== 'unknown') severity = score; }
        if (result.properties != null) { object(result.properties); const score = numericSeverity(result.properties['security-severity']); if (score !== 'unknown') severity = score; }
        const locations = optionalArray(result.locations);
        if (!locations.length) add({ rule: sarifRule(driver, ruleId), severity });
        for (const loc of locations) {
          object(loc);
          if (loc.physicalLocation == null) { add({ rule: sarifRule(driver, ruleId), severity }); continue; }
          const physical = object(loc.physicalLocation);
          let artifact = object(physical.artifactLocation);
          if (artifact.index != null) {
            if (!Number.isSafeInteger(artifact.index) || artifact.index < 0 || artifact.index >= artifacts.length) invalid();
            artifact = { ...object(artifacts[artifact.index].location), ...artifact };
          }
          let relative;
          function decodeUri(value, localBase = false) {
            if (typeof value !== 'string' || !value || /[?#]/.test(value)) { warn('path'); return null; }
            let decoded;
            try { decoded = decodeURIComponent(value); } catch { warn('path'); return null; }
            if (/^file:\/\/\//i.test(decoded)) {
              if (!sourceRoot) { warn('path'); return null; }
              decoded = decoded.slice(7);
              if (/^[A-Za-z]:\//.test(sourceRoot) && /^\/[A-Za-z]:\//.test(decoded)) decoded = decoded.slice(1);
              return decoded;
            }
            if (localBase || /^[A-Za-z][A-Za-z0-9+.-]*:/.test(decoded)) { warn('path'); return null; }
            return decoded;
          }
          const decodedUri = artifact.uri == null ? null : decodeUri(artifact.uri);
          if (artifact.uriBaseId != null && decodedUri != null && !decodedUri.startsWith('/') && !/^[A-Za-z]:\//.test(decodedUri)) {
            // Base references are not assumed to denote the repository root.
            if (typeof artifact.uriBaseId !== 'string') invalid();
            metadata(artifact.uriBaseId.replaceAll('%', ''), 256);
            const base = run.originalUriBaseIds && object(run.originalUriBaseIds)[artifact.uriBaseId];
            if (!sourceRoot || !base || base.uriBaseId != null) { warn('path'); relative = null; }
            else {
              object(base);
              const basePath = decodeUri(base.uri, true);
              relative = basePath ? location(basePath.replace(/\/$/, '') + '/' + decodedUri) : null;
            }
          } else relative = decodedUri == null ? null : location(decodedUri);
          const region = physical.region == null ? {} : object(physical.region);
          add({ rule: sarifRule(driver, ruleId), path: relative, mapped: true, line: positiveLine(region.startLine), severity });
        }
      }
    }
  } else if (format === 'trivy') {
    object(data);
    if (data.SchemaVersion !== 2) invalid();
    // Trivy omits Results for an empty scan. Require identifying report
    // metadata before accepting that documented encoding as an empty result.
    if (!OWN(data, 'Results') && (typeof data.ArtifactName !== 'string' || !data.ArtifactName || typeof data.ArtifactType !== 'string' || !data.ArtifactType)) invalid();
    for (const result of OWN(data, 'Results') ? array(data.Results) : []) {
      object(result);
      if (typeof result.Target !== 'string' || !result.Target.length) invalid();
      if (optionalArray(result.Licenses).length || optionalArray(result.CustomResources).length || optionalArray(result.CryptoFindings).length || optionalArray(result.CryptoAssets).length) warn('unsupported');
      if (optionalArray(result.ExperimentalModifiedFindings).length) warn('suppression');
      for (const vuln of optionalArray(result.Vulnerabilities)) {
        object(vuln);
        const pkg = metadata(vuln.PkgName, 256, true);
        if (result.Class === 'os-pkgs') warn('path');
        add({ rule: vuln.VulnerabilityID, advisory: vuln.VulnerabilityID, path: result.Class === 'os-pkgs' ? null : result.Target, severity: normalizeSeverity(vuln.Severity), package: result.Type ? `${metadata(result.Type, 128)}:${pkg}` : pkg, version: vuln.InstalledVersion });
      }
      for (const mis of optionalArray(result.Misconfigurations)) {
        object(mis);
        if (mis.Status && !['FAIL', 'PASS', 'EXCEPTION'].includes(mis.Status)) invalid();
        if (mis.Status === 'PASS') continue;
        if (mis.Status === 'EXCEPTION') warn('suppression');
        const cause = mis.CauseMetadata == null ? {} : object(mis.CauseMetadata);
        add({ rule: mis.ID || mis.AVDID, path: result.Target, line: positiveLine(cause.StartLine || null), severity: normalizeSeverity(mis.Severity) });
      }
      for (const secret of optionalArray(result.Secrets)) {
        object(secret);
        add({ rule: secret.RuleID, path: result.Target, line: positiveLine(secret.StartLine), severity: normalizeSeverity(secret.Severity) });
      }
    }
  } else if (format === 'osv') {
    object(data);
    if (optionalArray(data.experimental_generic_findings).length) warn('unsupported');
    for (const result of array(data.results)) {
      object(result); object(result.source);
      if (typeof result.source.path !== 'string') invalid();
      for (const entry of array(result.packages)) {
        object(entry); object(entry.package);
        const pkg = metadata(entry.package.name || entry.package.purl || (entry.package.commit ? 'git-commit' : ''), 256, true);
        const ecosystem = optionalMetadata(entry.package.ecosystem, 128);
        if (optionalArray(entry.license_violations).length || entry.package.deprecated === true) warn('unsupported');
        const groups = optionalArray(entry.groups).map(object);
        for (const vuln of optionalArray(entry.vulnerabilities)) {
          object(vuln);
          const id = metadata(vuln.id, 256);
          let severity = 'unknown';
          if (vuln.database_specific != null) { object(vuln.database_specific); severity = normalizeSeverity(vuln.database_specific.severity); }
          for (const score of optionalArray(vuln.severity)) { object(score); severity = higher(severity, numericSeverity(score.score)); }
          for (const group of groups) {
            const ids = array(group.ids);
            if (ids.some(x => typeof x !== 'string')) invalid();
            if (ids.includes(id)) severity = higher(severity, numericSeverity(group.max_severity));
          }
          add({ rule: id, advisory: id, path: result.source.path, severity, package: ecosystem ? `${ecosystem}:${pkg}` : pkg, version: entry.package.version || (entry.package.commit ? `commit:${metadata(entry.package.commit, 256)}` : null) });
        }
      }
    }
  }
  const report = { schema_version: '1.0.0', kind: 'tool-signals', tool: format, complete: warnings.size === 0, warnings: [...warnings].sort(), signals: [...found.values()].sort((a, b) => a.fingerprint.localeCompare(b.fingerprint, 'en')) };
  if (validateSignalDocument(report).length) throw new Error('Scanner report could not be normalized safely.');
  return report;
}
module.exports = { FORMATS, SEVERITIES, MAX_SIGNALS, WARNINGS, importReport, fingerprintSignal, validateSignalDocument, isSafeRelativePath };
