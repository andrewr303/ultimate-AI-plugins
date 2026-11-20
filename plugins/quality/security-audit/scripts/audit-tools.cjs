#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { readJson, writeExclusive, safeIoAvailable } = require("../lib/io.cjs");

const HELP = `Security Audit — local planning and result utilities
Usage: node scripts/audit-tools.cjs <command> [options]

  plan --target DIR [--profile quick|standard|deep] --output FILE
  import --format sarif|semgrep|gitleaks|trivy|osv --input FILE --output FILE
         [--source-root DIR]
  compare --current FILE --baseline FILE --output FILE [--fail-on-new]
  report --input FILE --output FILE.md
  sarif --input FILE --output FILE.sarif
  export-findings --input FILE --output FILE.sarif
  validate --input FILE
  doctor

Creates new files only; output parent directories must already exist.
No command executes scanners, target code, installs, or network requests.
Imported tool signals remain unverified. Absence is not proof of remediation.
Exit: 0 success; 1 invalid input/I/O; 2 known incomplete data;
      3 new signals with compare --fail-on-new (only if complete).
`;

const OPTIONS = {
  plan: { required: ["target", "output"], optional: ["profile"] },
  import: { required: ["format", "input", "output"], optional: ["source-root"] },
  compare: { required: ["current", "baseline", "output"], optional: ["fail-on-new"] },
  report: { required: ["input", "output"], optional: [] },
  sarif: { required: ["input", "output"], optional: [] },
  "export-findings": { required: ["input", "output"], optional: [] },
  validate: { required: ["input"], optional: [] },
  doctor: { required: [], optional: [] },
};

function parseArgs(argv) {
  const command = argv[0];
  if (argv.length === 0 || (argv.length === 1 && ["--help", "-h", "help"].includes(command))) return { command: "help", options: {} };
  if (!Object.hasOwn(OPTIONS, command)) throw new Error("Unknown command. Use --help.");
  const spec = OPTIONS[command];
  const allowed = new Set([...spec.required, ...spec.optional]);
  const options = Object.create(null);
  for (let i = 1; i < argv.length; i++) {
    const flag = argv[i];
    if (!flag.startsWith("--") || !allowed.has(flag.slice(2))) throw new Error("Unknown option. Use --help.");
    const key = flag.slice(2);
    if (Object.hasOwn(options, key)) throw new Error("Duplicate option.");
    if (key === "fail-on-new") options[key] = true;
    else {
      const value = argv[++i];
      if (!value || value.startsWith("--")) throw new Error("Option requires a value.");
      options[key] = value;
    }
  }
  if (spec.required.some((key) => !Object.hasOwn(options, key))) throw new Error("Missing required option. Use --help.");
  return { command, options };
}

function doctor() {
  const names = ["semgrep", "gitleaks", "trivy", "osv-scanner", "zizmor", "syft"];
  const dirs = (process.env.PATH || "").split(path.delimiter).filter((p) => p && path.isAbsolute(p));
  const presence = Object.fromEntries(names.map((name) => [name, dirs.some((dir) => {
    try {
      const p = path.join(dir, name);
      if (!fs.statSync(p).isFile()) return false;
      fs.accessSync(p, fs.constants.X_OK);
      return true;
    } catch { return false; }
  })]));
  return { node: process.versions.node, node_supported: Number(process.versions.node.split(".")[0]) >= 20,
    safe_file_io: safeIoAvailable(), scanners_on_path: presence,
    note: "Presence only; binaries were not executed. Versions, authenticity, rules, databases and sandbox readiness are unverified." };
}

function run(argv = process.argv.slice(2)) {
  const { command, options: o } = parseArgs(argv);
  if (command === "help") { process.stdout.write(HELP); return 0; }
  if (command === "doctor") { process.stdout.write(JSON.stringify(doctor(), null, 2) + "\n"); return 0; }
  if (Number(process.versions.node.split(".")[0]) < 20) throw new Error("Node.js 20 or newer is required.");
  let result;
  let content;
  let incomplete = false;
  if (command === "plan") {
    const target = path.resolve(o.target);
    const output = path.resolve(o.output);
    const withinTarget = path.relative(target, output);
    if (withinTarget === "" || (!withinTarget.startsWith(`..${path.sep}`) && withinTarget !== ".." && !path.isAbsolute(withinTarget))) {
      throw new Error("Plan output must be outside the target repository.");
    }
    result = require("../lib/planner.cjs").planRepository(o.target, { profile: o.profile || "standard" });
    incomplete = result.complete === false;
  } else if (command === "import") {
    result = require("../lib/importers.cjs").importReport(o.format, readJson(o.input), { sourceRoot: o["source-root"] });
    incomplete = !result.complete;
  } else if (command === "compare") {
    result = require("../lib/reporting.cjs").compareSignals(readJson(o.current), readJson(o.baseline));
    incomplete = !result.complete;
  } else if (command === "validate") {
    const doc = readJson(o.input);
    const comparison = doc?.kind === "signal-comparison";
    const validate = comparison ? require("../lib/reporting.cjs").validateComparisonDocument : require("../lib/importers.cjs").validateSignalDocument;
    const errors = validate(doc);
    if (errors.length) throw new Error("Invalid signals or comparison document.");
    process.stdout.write(`VALID: ${comparison ? "signal comparison" : `${doc.signals.length} unverified tool signals`}; input processing ${doc.complete ? "complete" : "incomplete"}.\n`);
    return doc.complete ? 0 : 2;
  } else {
    const reporting = require("../lib/reporting.cjs");
    const doc = readJson(o.input);
    if (command === "report") content = reporting.renderSignalsMarkdown(doc);
    else if (command === "sarif") result = reporting.signalsToSarif(doc);
    else result = reporting.findingsToSarif(doc);
    incomplete = command !== "export-findings" && doc.complete === false;
  }
  writeExclusive(o.output, content ?? JSON.stringify(result, null, 2) + "\n");
  process.stdout.write(incomplete ? "WROTE: incomplete data; inspect warnings and coverage gaps.\n" : "WROTE: output created.\n");
  if (incomplete) return 2;
  if (command === "compare" && o["fail-on-new"] && result.new.length > 0) return 3;
  return 0;
}

if (require.main === module) {
  try { process.exitCode = run(); }
  catch (error) {
    // Library messages contain no report payloads. Strip controls defensively.
    const message = String(error.message || "Operation failed.").replace(/[\p{Cc}\p{Cf}\p{Cs}]/gu, " ").slice(0, 240);
    process.stderr.write(`ERROR: ${message}\n`);
    process.exitCode = 1;
  }
}
module.exports = { parseArgs, doctor, run };
