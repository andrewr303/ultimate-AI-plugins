"use strict";

// Trusted parent-side JSON I/O. This is not the original audit workflow's
// race-safe sandbox artifact promoter: callers must own stable parent dirs.
const fs = require("node:fs");
const path = require("node:path");
const { TextDecoder } = require("node:util");
const LIMITS = Object.freeze({ bytes: 20 * 1024 * 1024, depth: 64, arrayItems: 50000 });
const fail = (message) => { throw new Error(message); };

function safeIoAvailable() {
  return ["O_NOFOLLOW", "O_NONBLOCK"].every((k) => Number.isInteger(fs.constants[k]) && fs.constants[k] !== 0);
}

function checkParents(file) {
  if (typeof file !== "string" || !file || /[\p{Cc}\p{Cf}\p{Cs}\p{Zl}\p{Zp}\p{Default_Ignorable_Code_Point}]/u.test(file)) fail("Invalid file path.");
  const absolute = path.resolve(file);
  const parent = path.dirname(absolute);
  let current = path.parse(parent).root;
  for (const component of parent.slice(current.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, component);
    let stat;
    try { stat = fs.lstatSync(current); } catch { fail("Parent directory is unavailable; create a trusted output directory first."); }
    if (stat.isSymbolicLink() || !stat.isDirectory()) fail("Parent paths must be real directories, without symlinks.");
  }
  return absolute;
}

function preflightJson(text) {
  const containers = [];
  let inString = false;
  let escaped = false;
  function item() {
    const top = containers.at(-1);
    if (top?.type === "[" && top.pending) {
      top.pending = false;
      if (++top.items > LIMITS.arrayItems) fail("JSON array exceeds the item limit.");
    }
  }
  for (const c of text) {
    if (inString) {
      if (escaped) escaped = false;
      else if (c === "\\") escaped = true;
      else if (c === '"') inString = false;
      continue;
    }
    if (c === '"') { item(); inString = true; }
    else if (c === "[" || c === "{") {
      item();
      if (containers.length >= LIMITS.depth) fail("JSON exceeds the nesting limit.");
      containers.push({ type: c, pending: c === "[", items: 0 });
    } else if (c === "]" || c === "}") containers.pop();
    else if (c === ",") { if (containers.at(-1)?.type === "[") containers.at(-1).pending = true; }
    else if (!/\s/.test(c)) item();
  }
}

function readJson(file) {
  if (!safeIoAvailable()) fail("Safe file I/O requires POSIX O_NOFOLLOW and O_NONBLOCK support.");
  const absolute = checkParents(file);
  let fd;
  try {
    fd = fs.openSync(absolute, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
    const before = fs.fstatSync(fd);
    if (!before.isFile() || before.nlink !== 1 || before.size > LIMITS.bytes) fail("Input must be a regular, singly linked file of at most 20 MiB.");
    const buffer = Buffer.alloc(before.size + 1);
    let offset = 0;
    while (offset < buffer.length) {
      const count = fs.readSync(fd, buffer, offset, buffer.length - offset, null);
      if (count === 0) break;
      offset += count;
    }
    const after = fs.fstatSync(fd);
    if (offset !== before.size || after.size !== before.size || after.mtimeMs !== before.mtimeMs || after.ctimeMs !== before.ctimeMs || after.nlink !== 1) fail("Input changed while it was being read.");
    let text;
    try { text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(buffer.subarray(0, offset)); }
    catch { fail("Input must contain valid UTF-8."); }
    preflightJson(text);
    try { return JSON.parse(text); } catch { fail("Input must contain valid JSON."); }
  } catch (error) {
    if (error.code) fail("Input could not be read safely (missing, linked, or inaccessible file).");
    throw error;
  } finally { if (fd !== undefined) fs.closeSync(fd); }
}

function writeExclusive(file, content) {
  if (!safeIoAvailable()) fail("Safe file I/O requires POSIX O_NOFOLLOW and O_NONBLOCK support.");
  const absolute = checkParents(file);
  if (typeof content !== "string" || Buffer.byteLength(content) > LIMITS.bytes) fail("Output exceeds the 20 MiB file limit.");
  let fd;
  try {
    fd = fs.openSync(absolute, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_NOFOLLOW, 0o600);
    fs.writeFileSync(fd, content, { encoding: "utf8" });
    fs.fsyncSync(fd);
  } catch (error) {
    if (error.code === "EEXIST") fail("Output already exists; choose a new output path.");
    fail("Output could not be written safely; any partial output must be discarded.");
  } finally { if (fd !== undefined) fs.closeSync(fd); }
}

module.exports = { LIMITS, safeIoAvailable, readJson, writeExclusive, preflightJson };
