"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { LIMITS, readJson, writeExclusive, preflightJson } = require("../lib/io.cjs");

function temp(t) {
  const dir = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "audit-io-")));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}
test("writes private exclusive JSON and reads it back", (t) => {
  const f = path.join(temp(t), "data.json");
  writeExclusive(f, '{"ok":true}');
  assert.deepEqual(readJson(f), { ok: true });
  assert.equal(fs.statSync(f).mode & 0o777, 0o600);
  assert.throws(() => writeExclusive(f, "replacement"), /already exists/);
  assert.deepEqual(readJson(f), { ok: true });
});
test("rejects invalid UTF8 and JSON without disclosing contents", (t) => {
  const dir = temp(t);
  const f = path.join(dir, "bad.json");
  fs.writeFileSync(f, Buffer.from([0xc0, 0x80]));
  assert.throws(() => readJson(f), /UTF-8/);
  fs.writeFileSync(f, 'RAW_SECRET_DO_NOT_ECHO');
  assert.throws(() => readJson(f), (e) => /valid JSON/.test(e.message) && !e.message.includes("RAW_SECRET"));
});
test("enforces bytes, depth and array items before parsing", (t) => {
  const f = path.join(temp(t), "large.json");
  const fd = fs.openSync(f, "w");
  fs.ftruncateSync(fd, LIMITS.bytes + 1); fs.closeSync(fd);
  assert.throws(() => readJson(f), /20 MiB/);
  assert.throws(() => preflightJson("[".repeat(65) + "0" + "]".repeat(65)), /nesting/);
  assert.throws(() => preflightJson(JSON.stringify(Array(50001).fill(0))), /item limit/);
  assert.doesNotThrow(() => preflightJson(JSON.stringify({ text: '"[[[[\\\\' })));
});
test("rejects symlink and hard link inputs and symlink parents", (t) => {
  const dir = temp(t), input = path.join(dir, "input.json");
  fs.writeFileSync(input, "[]");
  const link = path.join(dir, "link.json");
  fs.symlinkSync(input, link);
  assert.throws(() => readJson(link), /safely/);
  assert.throws(() => writeExclusive(link, "[]"), /already exists/);
  const hard = path.join(dir, "hard.json"); fs.linkSync(input, hard);
  assert.throws(() => readJson(hard), /singly linked/);
  const real = path.join(dir, "real"); fs.mkdirSync(real);
  const linked = path.join(dir, "linked"); fs.symlinkSync(real, linked);
  assert.throws(() => writeExclusive(path.join(linked, "out.json"), "[]"), /symlinks/);
  fs.writeFileSync(path.join(real, "in.json"), "[]");
  assert.throws(() => readJson(path.join(linked, "in.json")), /symlinks/);
});
test("rejects FIFO without waiting for a writer", (t) => {
  const f = path.join(temp(t), "pipe.json");
  const made = spawnSync("mkfifo", [f], { timeout: 2000 });
  if (made.error?.code === "ENOENT") return t.skip("mkfifo unavailable");
  assert.equal(made.status, 0);
  assert.throws(() => readJson(f), /regular/);
});
test("does not create missing parent directories or oversized output", (t) => {
  const dir = temp(t);
  assert.throws(() => writeExclusive(path.join(dir, "missing", "x"), "[]"), /Parent/);
  assert.throws(() => writeExclusive(path.join(dir, "big"), "x".repeat(LIMITS.bytes + 1)), /20 MiB/);
});
