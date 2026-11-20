"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { parseArgs, doctor } = require("../scripts/audit-tools.cjs");
const cli = path.resolve(__dirname, "../scripts/audit-tools.cjs");
const invoke = (...args) => spawnSync(process.execPath, [cli, ...args], { encoding: "utf8", timeout: 10000 });
function temp(t) {
  const dir = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "audit-cli-")));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}
test("CLI rejects unsupported, duplicate and missing options", () => {
  for (const args of [["run"], ["doctor", "--execute"], ["import"], ["validate", "--input", "x", "--input", "y"], ["plan", "--target", "--output", "x"]]) {
    assert.throws(() => parseArgs(args));
  }
  assert.equal(invoke("--help").status, 0);
});
test("doctor does not execute a scanner found on PATH", (t) => {
  const dir = temp(t), marker = path.join(dir, "executed");
  fs.writeFileSync(path.join(dir, "gitleaks"), `#!/bin/sh\ntouch '${marker}'\n`, { mode: 0o755 });
  const result = spawnSync(process.execPath, [cli, "doctor"], { encoding: "utf8", env: { PATH: dir }, timeout: 2000 });
  assert.equal(result.status, 0);
  assert.equal(JSON.parse(result.stdout).scanners_on_path.gitleaks, true);
  assert.equal(fs.existsSync(marker), false);
  assert.equal(typeof doctor().safe_file_io, "boolean");
});
test("import, validate, Markdown, SARIF and baseline gate end to end", (t) => {
  const dir = temp(t);
  const input = path.join(dir, "gitleaks.json"), baselineInput = path.join(dir, "baseline-raw.json");
  const signals = path.join(dir, "signals.json"), baseline = path.join(dir, "baseline.json");
  const raw = [{ RuleID: "generic-api-key", File: "src/config.js", StartLine: 4, Secret: "NEVER_RETAIN_TEST_SECRET", Match: "api_key=NEVER_RETAIN_TEST_SECRET" }];
  fs.writeFileSync(input, JSON.stringify(raw));
  fs.writeFileSync(baselineInput, "[]");
  assert.equal(invoke("import", "--format", "gitleaks", "--input", input, "--output", signals).status, 0);
  assert.equal(invoke("import", "--format", "gitleaks", "--input", baselineInput, "--output", baseline).status, 0);
  assert.equal(invoke("validate", "--input", signals).status, 0);
  for (const command of ["report", "sarif"]) {
    const out = path.join(dir, command + ".out");
    const result = invoke(command, "--input", signals, "--output", out);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(fs.readFileSync(out, "utf8").includes("NEVER_RETAIN_TEST_SECRET"), false);
  }
  const comparison = path.join(dir, "compare.json");
  const compared = invoke("compare", "--current", signals, "--baseline", baseline, "--output", comparison, "--fail-on-new");
  assert.equal(compared.status, 3, compared.stderr);
  assert.equal(JSON.parse(fs.readFileSync(comparison, "utf8")).new.length, 1);
  assert.equal(invoke("validate", "--input", comparison).status, 0);
  assert.equal(invoke("report", "--input", comparison, "--output", path.join(dir, "comparison.md")).status, 0);
  assert.equal(invoke("import", "--format", "gitleaks", "--input", input, "--output", signals).status, 1);
});
test("empty malformed report fails, declared scanner errors write incomplete result", (t) => {
  const dir = temp(t), input = path.join(dir, "input.json"), output = path.join(dir, "output.json");
  fs.writeFileSync(input, "{}");
  assert.equal(invoke("import", "--format", "semgrep", "--input", input, "--output", output).status, 1);
  assert.equal(fs.existsSync(output), false);
  fs.writeFileSync(input, JSON.stringify({ results: [], errors: [{ message: "PRIVATE_RAW_SCANNER_ERROR" }] }));
  const result = invoke("import", "--format", "semgrep", "--input", input, "--output", output);
  assert.equal(result.status, 2, result.stderr);
  assert.equal(fs.readFileSync(output, "utf8").includes("PRIVATE_RAW_SCANNER_ERROR"), false);
  assert.equal(invoke("validate", "--input", output).status, 2);
});
test("plan is read only, paths with spaces work", (t) => {
  const dir = temp(t), target = path.join(dir, "target with spaces"); fs.mkdirSync(target);
  fs.writeFileSync(path.join(target, "package.json"), "{}");
  const before = fs.readdirSync(target);
  const result = invoke("plan", "--target", target, "--profile", "quick", "--output", path.join(dir, "plan.json"));
  assert.ok([0, 2].includes(result.status), result.stderr);
  assert.deepEqual(fs.readdirSync(target), before);
  const unsafe = invoke("plan", "--target", target, "--output", path.join(target, "plan.json"));
  assert.equal(unsafe.status, 1);
  assert.deepEqual(fs.readdirSync(target), before);
});
