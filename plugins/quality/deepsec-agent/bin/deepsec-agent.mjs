#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import { parseArgs } from 'node:util';
import { pathToFileURL } from 'node:url';
import { audit, doctor, listRules, normalizeReport, createBaseline, applyBaseline, renderReport, buildReviewPacket, parseEngineReport } from '../runtime/index.mjs';
import { startServer } from '../runtime/mcp.mjs';

const HELP = `DeepSec Agent 1.0.0 — Node 22+; no runtime installation required

  scan      --root DIR [--engines deepsec,gitleaks] [--allow-network]
            [--format json|markdown|sarif] [--out FILE] [--baseline FILE]
            [--files RELATIVE,PATHS] [--max-files N] [--max-file-bytes N]
            [--max-total-bytes N] [--max-findings N] [--timeout-ms N]
            [--include-noisy] [--fail-on critical|high|medium|low|info]
  doctor    [--root DIR]
  rules     [--root DIR]
  serve     --root DIR
  report    --input REPORT.json [--format markdown|json|sarif] [--out FILE]
  baseline  --input REPORT.json [--out BASELINE.json]
  plan      --input REPORT.json [--limit N] [--out FILE]
  import    --engine NAME --input NATIVE.json --root DIR [--out FILE]
  workflow  --config WORKFLOW.json

Engines: deepsec, semgrep, gitleaks, osv-scanner, bandit, trivy.
Only deepsec runs by default. OSV/Trivy require --allow-network.
Exit: 0 complete; 1 new finding meets --fail-on; 2 error/incomplete coverage.
Findings are candidates requiring investigation. No automatic model calls.
`;

async function readJson(file) {
  if (!file) throw new TypeError('An input file is required');
  const handle = await fs.open(file, 'r');
  try {
    const stat = await handle.stat();
    if (!stat.isFile() || stat.size > 8 * 1024 * 1024) throw new TypeError('Input must be a regular JSON file no larger than 8 MiB');
    return JSON.parse(await handle.readFile('utf8'));
  } finally { await handle.close(); }
}
export async function writeOutput(content, file) {
  if (!file) { process.stdout.write(content.endsWith('\n') ? content : content + '\n'); return; }
  const destination = path.resolve(file);
  await fs.mkdir(path.dirname(destination), { recursive: true });
  const temporary = destination + '.tmp-' + process.pid + '-' + Math.random().toString(16).slice(2);
  try { await fs.writeFile(temporary, content.endsWith('\n') ? content : content + '\n', { mode: 0o600, flag: 'wx' }); await fs.rename(temporary, destination); }
  finally { await fs.rm(temporary, { force: true }); }
}
function number(value) {
  if (value === undefined) return undefined;
  if (!/^\d+$/.test(value)) throw new TypeError('Limits must be positive integers');
  return Number(value);
}
function exitFor(report, threshold) {
  if (!report.complete) return 2;
  if (!threshold) return 0;
  const order = ['info', 'low', 'medium', 'high', 'critical'];
  if (!order.includes(threshold)) throw new TypeError('Invalid severity threshold');
  return report.findings.some(f => f.baseline !== 'existing' && order.indexOf(f.severity) >= order.indexOf(threshold)) ? 1 : 0;
}
export async function main(argv = process.argv.slice(2)) {
  const { values, positionals } = parseArgs({ args: argv, allowPositionals: true, strict: true, options: {
    root: { type: 'string' }, engines: { type: 'string' }, engine: { type: 'string' }, format: { type: 'string' }, out: { type: 'string' }, input: { type: 'string' }, baseline: { type: 'string' }, files: { type: 'string' }, config: { type: 'string' }, limit: { type: 'string' },
    'max-files': { type: 'string' }, 'max-file-bytes': { type: 'string' }, 'max-total-bytes': { type: 'string' }, 'max-findings': { type: 'string' }, 'timeout-ms': { type: 'string' }, 'fail-on': { type: 'string' },
    'allow-network': { type: 'boolean' }, 'include-noisy': { type: 'boolean' }, help: { type: 'boolean', short: 'h' }, version: { type: 'boolean' },
  } });
  const command = positionals[0];
  if (values.version) { process.stdout.write('1.0.0\n'); return 0; }
  if (values.help || !command) { process.stdout.write(HELP); return 0; }
  if (positionals.length !== 1) throw new TypeError('Use one command and named options');
  const root = values.root ?? process.cwd();
  const format = values.format ?? 'json';
  if (command === 'serve') {
    if (!values.root && !process.env.DEEPSEC_WORKSPACE_ROOT) throw new TypeError('serve requires --root or DEEPSEC_WORKSPACE_ROOT');
    await startServer(values.root ?? process.env.DEEPSEC_WORKSPACE_ROOT); return null;
  }
  if (command === 'doctor') { await writeOutput(JSON.stringify(await doctor(root), null, 2), values.out); return 0; }
  if (command === 'rules') { await writeOutput(JSON.stringify({ rules: listRules() }, null, 2), values.out); return 0; }
  if (command === 'scan') {
    const options = {
      engines: values.engines?.split(',') ?? ['deepsec'], allowNetwork: values['allow-network'] ?? false, includeNoisy: values['include-noisy'] ?? false,
      maxFiles: number(values['max-files']), maxFileBytes: number(values['max-file-bytes']), maxTotalBytes: number(values['max-total-bytes']), maxFindings: number(values['max-findings']), timeoutMs: number(values['timeout-ms']),
      files: values.files?.split(','), baseline: values.baseline ? await readJson(values.baseline) : undefined,
    };
    for (const key of Object.keys(options)) if (options[key] === undefined) delete options[key];
    const report = await audit(root, options);
    await writeOutput(renderReport(report, format), values.out);
    return exitFor(report, values['fail-on']);
  }
  if (command === 'workflow') {
    const config = await readJson(values.config);
    const allowed = ['root', 'engines', 'allowNetwork', 'includeNoisy', 'maxFiles', 'maxFileBytes', 'maxTotalBytes', 'maxFindings', 'timeoutMs', 'outputDir', 'formats', 'baseline', 'failOn'];
    if (!config || Array.isArray(config) || Object.keys(config).some(k => !allowed.includes(k))) throw new TypeError('Unknown workflow field');
    if (!config.root || !config.outputDir) throw new TypeError('Workflow requires root and outputDir');
    const base = path.dirname(path.resolve(values.config));
    const workflowRoot = path.resolve(base, config.root);
    const outputDir = path.resolve(base, config.outputDir);
    const options = { ...config, baseline: config.baseline ? await readJson(path.resolve(base, config.baseline)) : undefined };
    const report = await audit(workflowRoot, options);
    for (const target of config.formats ?? ['json', 'markdown', 'sarif']) {
      const ext = { json: 'json', markdown: 'md', sarif: 'sarif' }[target];
      if (!ext) throw new TypeError('Unknown report format');
      await writeOutput(renderReport(report, target), path.join(outputDir, 'deepsec-report.' + ext));
    }
    process.stdout.write(JSON.stringify({ outputDir, complete: report.complete, summary: report.summary }) + '\n');
    return exitFor(report, config.failOn);
  }
  if (command === 'import') {
    if (!values.engine) throw new TypeError('import requires --engine');
    const imported = parseEngineReport(values.engine, await readJson(values.input), await fs.realpath(root));
    const report = normalizeReport({ schemaVersion: '1.0', createdAt: new Date().toISOString(), ...imported });
    await writeOutput(renderReport(report, format), values.out); return report.complete ? 0 : 2;
  }
  if (['report', 'baseline', 'plan'].includes(command)) {
    let report = normalizeReport(await readJson(values.input));
    if (values.baseline) report = applyBaseline(report, await readJson(values.baseline));
    const text = command === 'report' ? renderReport(report, format) : JSON.stringify(command === 'baseline' ? createBaseline(report) : buildReviewPacket(report, { limit: number(values.limit) ?? 20 }), null, 2);
    await writeOutput(text, values.out); return command === 'report' && !report.complete ? 2 : 0;
  }
  throw new TypeError('Unknown command; use --help');
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().then(code => { if (code !== null) process.exitCode = code; }).catch(error => {
    process.stderr.write(error instanceof TypeError ? 'DeepSec: ' + error.message.slice(0, 240) + '\n' : 'DeepSec operation failed. Check paths, JSON inputs, and permissions.\n');
    process.exitCode = 2;
  });
}
