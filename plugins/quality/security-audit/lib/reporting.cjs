"use strict";

// Pure exports: callers own bounded file I/O and choose where reports are saved.
const { createHash } = require("node:crypto");
const { validateSignalDocument } = require("./importers.cjs");
const findingsSchema = require("../skills/security-audit/report-schema.json");
const { validateDocument: validateFindings } = require("../skills/security-audit/validate-findings.cjs");

const SCHEMA_VERSION = "1.0.0";
const SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json";
const CONTROLS = /[\p{Cc}\p{Cf}\p{Cs}\p{Zl}\p{Zp}\p{Default_Ignorable_Code_Point}]/gu;
const COMPARISON_WARNING = "Compare reports from the same repository, scope, scanner configuration, and scanner version. Absent signals do not prove a fix.";
const INCOMPLETE_WARNING = "At least one report is incomplete; absent signals are withheld. No clean-scan or remediation conclusion is possible.";
const IDENTITY_WARNING = "Unchanged means the signal identity persists; scanner-reported severity or other metadata may have changed.";

function requireSignals(document) {
  let errors;
  try { errors = validateSignalDocument(document); } catch { throw new Error("Invalid tool-signals document."); }
  if (!Array.isArray(errors) || errors.length !== 0) throw new Error("Invalid tool-signals document.");
  return document;
}

function plain(value, limit = 4096) {
  return String(value).replace(CONTROLS, " ").slice(0, limit);
}

function markdown(value) {
  // Numeric entities keep paths, brackets, HTML, table separators, and Markdown
  // punctuation inert, including values reloaded from a saved comparison.
  return plain(value).replace(/[&<>"'`\\|\[\]()*_!#{}]/g, (c) => `&#${c.codePointAt(0)};`);
}

function fingerprintOrder(left, right) {
  return left.fingerprint < right.fingerprint ? -1 : left.fingerprint > right.fingerprint ? 1 : 0;
}

function cloneSignals(signals) {
  return signals.map((signal) => ({ ...signal })).sort(fingerprintOrder);
}

function compareSignals(current, baseline) {
  requireSignals(current);
  requireSignals(baseline);
  if (current.tool !== baseline.tool || current.schema_version !== baseline.schema_version) {
    throw new Error("Signal reports must use the same tool and schema version.");
  }
  const previousIds = new Set(baseline.signals.map((signal) => signal.fingerprint));
  const currentIds = new Set(current.signals.map((signal) => signal.fingerprint));
  const complete = current.complete && baseline.complete;
  return {
    schema_version: SCHEMA_VERSION,
    kind: "signal-comparison",
    tool: current.tool,
    complete,
    new: cloneSignals(current.signals.filter((signal) => !previousIds.has(signal.fingerprint))),
    unchanged: cloneSignals(current.signals.filter((signal) => previousIds.has(signal.fingerprint))),
    absent: complete ? cloneSignals(baseline.signals.filter((signal) => !currentIds.has(signal.fingerprint))) : [],
    warnings: [...new Set([
      COMPARISON_WARNING,
      IDENTITY_WARNING,
      ...(!complete ? [INCOMPLETE_WARNING] : []),
      ...current.warnings,
      ...baseline.warnings,
    ])],
  };
}

function requireComparison(document) {
  const expectedKeys = ["schema_version", "kind", "tool", "complete", "new", "unchanged", "absent", "warnings"].sort();
  if (!document || typeof document !== "object" || Array.isArray(document) ||
      Object.keys(document).sort().join("|") !== expectedKeys.join("|") ||
      document.schema_version !== SCHEMA_VERSION || document.kind !== "signal-comparison" ||
      typeof document.complete !== "boolean" || !Array.isArray(document.warnings) ||
      document.warnings.length > 1000 || document.warnings.some((warning) =>
        typeof warning !== "string" || warning.length > 4096 || warning.length === 0)) {
    throw new Error("Invalid signal-comparison document.");
  }
  const seen = new Set();
  for (const field of ["new", "unchanged", "absent"]) {
    requireSignals({
      schema_version: SCHEMA_VERSION,
      kind: "tool-signals",
      tool: document.tool,
      complete: document.complete,
      warnings: [],
      signals: document[field],
    });
    for (const signal of document[field]) {
      if (seen.has(signal.fingerprint)) throw new Error("Comparison contains a repeated signal identity.");
      seen.add(signal.fingerprint);
    }
  }
  if (seen.size > 100000 || document.new.length + document.unchanged.length > 50000 ||
      (!document.complete && document.absent.length !== 0)) {
    throw new Error("Invalid comparison coverage or signal count.");
  }
  return document;
}

function validateComparisonDocument(document) {
  try { requireComparison(document); return []; } catch { return ["Invalid signal-comparison document."]; }
}

function signalTable(signals) {
  if (signals.length === 0) return "No signals in this group. This is not a security assurance.\n";
  const rows = ["| Signal | Scanner severity | Location | Package / advisory |", "| --- | --- | --- | --- |"];
  for (const signal of signals) {
    const location = signal.path === null ? "Not available" : `${signal.path}${signal.line === null ? "" : `:${signal.line}`}`;
    const dependency = [signal.package, signal.version, signal.advisory].filter((value) => value !== null).join(" / ") || "—";
    rows.push(`| ${markdown(signal.title)} | ${markdown(signal.severity)} | ${markdown(location)} | ${markdown(dependency)} |`);
  }
  return `${rows.join("\n")}\n`;
}

function renderSignalsMarkdown(document) {
  const comparison = document && document.kind === "signal-comparison";
  if (comparison) requireComparison(document); else requireSignals(document);
  const sections = [
    comparison ? "# Security scanner signal comparison" : "# Security scanner signals",
    "These are unverified external scanner signals. Scanner severity is not a confirmed audit severity. Independent source review and validation are required.",
    `Tool format: ${markdown(document.tool)}. Input processing: ${document.complete ? "complete for the supplied report" : "incomplete"}. This does not establish repository coverage.`,
  ];
  if (comparison) {
    sections.push(COMPARISON_WARNING, IDENTITY_WARNING);
    if (!document.complete) sections.push(INCOMPLETE_WARNING);
    for (const [field, title] of [["new", "New signal identities"], ["unchanged", "Persisting signal identities"], ["absent", "Absent from the current report"]]) {
      sections.push(`## ${title} (${document[field].length})`, signalTable(document[field]));
    }
  } else {
    sections.push(`## Signals (${document.signals.length})`, signalTable(document.signals));
  }
  if (document.warnings.length) {
    sections.push("## Coverage and processing notes", document.warnings.map((warning) => `- ${markdown(warning)}`).join("\n"));
  }
  return `${sections.join("\n\n").trim()}\n`;
}

function uriForPath(sourcePath) {
  return sourcePath.split("/").map((segment) => encodeURIComponent(segment).replace(/[!'()*]/g, (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`)).join("/");
}

function locations(sourcePath, line) {
  if (sourcePath === null) return [];
  return [{ physicalLocation: {
    artifactLocation: { uri: uriForPath(sourcePath) },
    ...(line === null ? {} : { region: { startLine: line } }),
  } }];
}

function sarif(run) {
  return { $schema: SARIF_SCHEMA, version: "2.1.0", runs: [run] };
}

function signalRuleId(signal) {
  return `external.${createHash("sha256").update(JSON.stringify([signal.tool, signal.rule_id])).digest("hex").slice(0, 24)}`;
}

function signalsToSarif(document) {
  requireSignals(document);
  const ruleMap = new Map();
  for (const signal of document.signals) {
    const id = signalRuleId(signal);
    if (!ruleMap.has(id)) ruleMap.set(id, {
      id,
      shortDescription: { text: plain(`Unverified ${signal.tool} rule: ${signal.rule_id}`) },
      defaultConfiguration: { level: "note" },
      properties: { externalTool: signal.tool, externalRuleId: plain(signal.rule_id), reviewStatus: "unverified" },
    });
  }
  const rules = [...ruleMap.values()].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
  const indexes = new Map(rules.map((rule, index) => [rule.id, index]));
  return sarif({
    tool: { driver: { name: "security-audit-signals", rules } },
    invocations: [{ executionSuccessful: document.complete }],
    properties: {
      inputFormat: document.tool,
      inputComplete: document.complete,
      reviewStatus: "unverified",
      coverageNotice: "Only supplied scanner output is represented. No audit confirmation or repository coverage is implied.",
      warnings: document.warnings.map((warning) => plain(warning)),
    },
    results: document.signals.map((signal) => ({
      ruleId: signalRuleId(signal),
      ruleIndex: indexes.get(signalRuleId(signal)),
      kind: "review",
      level: "note",
      message: { text: plain(`Unverified scanner signal requiring independent review: ${signal.title}`) },
      ...(signal.path === null ? {} : { locations: locations(signal.path, signal.line) }),
      partialFingerprints: { "security-audit/signalFingerprint/v1": signal.fingerprint },
      properties: {
        reviewStatus: "unverified",
        scannerSeverity: signal.severity,
        ...(signal.package === null ? {} : { package: plain(signal.package) }),
        ...(signal.version === null ? {} : { packageVersion: plain(signal.version) }),
        ...(signal.advisory === null ? {} : { advisory: plain(signal.advisory) }),
      },
    })),
  });
}

function findingsToSarif(findings) {
  let errors;
  try { errors = validateFindings(findings, findingsSchema); } catch { throw new Error("Invalid audit findings document."); }
  if (errors.length !== 0) throw new Error("Invalid audit findings document; run validate-findings.cjs for details.");
  const confirmed = findings.filter((finding) => finding.verdict === "confirmed");
  const counts = { confirmed: confirmed.length, needs_validation: 0, rejected: 0 };
  for (const finding of findings) if (finding.verdict !== "confirmed") counts[finding.verdict] += 1;
  const level = { critical: "error", high: "error", medium: "warning", low: "warning", informational: "note" };
  return sarif({
    tool: { driver: {
      name: "security-audit",
      rules: [{ id: "security-audit.confirmed", shortDescription: { text: "Independently validated audit finding" } }],
    } },
    invocations: [{ executionSuccessful: true }],
    properties: {
      verdictCounts: counts,
      exportScope: "Only confirmed records are exported as SARIF results. Report validation checks the record contract; it does not establish audit coverage or independently verify source evidence.",
    },
    results: confirmed.map((finding) => {
      const primary = finding.trace.find((entry) => entry.kind === "sink") || finding.evidence[0];
      return {
        ruleId: "security-audit.confirmed",
        ruleIndex: 0,
        kind: "fail",
        level: level[finding.severity.overall_severity],
        message: { text: plain(finding.title) },
        locations: locations(primary.file, primary.line),
        partialFingerprints: { "security-audit/findingFingerprint/v1": finding.fingerprint },
        properties: { verdict: "confirmed", severity: finding.severity.overall_severity },
      };
    }),
  });
}

module.exports = { compareSignals, validateComparisonDocument, renderSignalsMarkdown, signalsToSarif, findingsToSarif };
