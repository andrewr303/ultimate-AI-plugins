import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PassThrough } from 'node:stream';
import { startServer } from './mcp.mjs';

const server = fileURLToPath(new URL('./mcp.mjs', import.meta.url));
test('MCP handshake, tools, scoped scan, review packet and errors over real stdio', async t => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-mcp-'));
  await fs.writeFile(path.join(root, 'app.js'), 'export function unsafe(input) { return eval(input); }\n');
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const child = spawn(process.execPath, [server, '--root', root], { stdio: ['pipe', 'pipe', 'pipe'] });
  t.after(() => child.kill());
  const waiting = new Map(); let buffer = ''; let next = 0; let stderr = '';
  child.stderr.on('data', b => stderr += b);
  child.stdout.on('data', b => {
    buffer += b;
    for (;;) {
      const end = buffer.indexOf('\n'); if (end < 0) break;
      const line = buffer.slice(0, end); buffer = buffer.slice(end + 1);
      const response = JSON.parse(line);
      waiting.get(response.id)?.(response); waiting.delete(response.id);
    }
  });
  async function call(method, params = {}) {
    const id = ++next;
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('MCP response timed out')), 5000);
      waiting.set(id, value => { clearTimeout(timeout); resolve(value); });
      child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    });
  }
  const init = await call('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'test', version: '1.0' } });
  assert.equal(init.result.protocolVersion, '2025-06-18');
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
  const list = await call('tools/list');
  assert.deepEqual(list.result.tools.map(x => x.name).sort(), ['deepsec_doctor', 'deepsec_review_packet', 'deepsec_rules', 'deepsec_scan']);
  assert(list.result.tools.every(x => x.annotations.readOnlyHint));
  const bad = await call('tools/call', { name: 'deepsec_scan', arguments: { root: '/' } });
  assert.equal(bad.result.isError, true);
  const escaped = await call('tools/call', { name: 'deepsec_scan', arguments: { files: ['../outside.js'] } });
  assert.equal(escaped.result.isError, true);
  const scan = await call('tools/call', { name: 'deepsec_scan', arguments: {} });
  const report = JSON.parse(scan.result.content[0].text);
  assert.equal(report.complete, true); assert(report.findings.length > 0);
  assert(report.findings.every(f => f.path === 'app.js' && f.status === 'candidate'));
  assert(!JSON.stringify(report).includes('eval(input)'));
  const packet = await call('tools/call', { name: 'deepsec_review_packet', arguments: { limit: 1 } });
  assert.equal(JSON.parse(packet.result.content[0].text).trust, 'untrusted-data');
  const rules = await call('tools/call', { name: 'deepsec_rules', arguments: { limit: 2 } });
  assert.equal(JSON.parse(rules.result.content[0].text).rules.length, 2);
  const unknown = await call('unrecognized'); assert.equal(unknown.error.code, -32601);
  assert.equal(stderr, '');
});

test('MCP rejects a startup root replaced with an outside symlink', async t => {
  const temporary = await fs.mkdtemp(path.join(os.tmpdir(), 'deepsec-root-binding-'));
  t.after(() => fs.rm(temporary, { recursive: true, force: true }));
  const root = path.join(temporary, 'repository');
  const outside = path.join(temporary, 'outside');
  await fs.mkdir(root); await fs.mkdir(outside);
  await fs.writeFile(path.join(outside, 'outside.js'), 'export const value = eval(attackerInput);\n');
  const input = new PassThrough();
  const output = new PassThrough();
  t.after(() => { input.destroy(); output.destroy(); });
  const waiting = new Map(); let buffer = ''; let next = 0;
  output.on('data', bytes => {
    buffer += bytes;
    for (;;) {
      const end = buffer.indexOf('\n'); if (end < 0) break;
      const response = JSON.parse(buffer.slice(0, end)); buffer = buffer.slice(end + 1);
      waiting.get(response.id)?.(response); waiting.delete(response.id);
    }
  });
  await startServer(root, input, output);
  const call = (method, params) => new Promise((resolve, reject) => {
    const id = ++next;
    const timer = setTimeout(() => reject(new Error('MCP response timed out')), 5000);
    waiting.set(id, value => { clearTimeout(timer); resolve(value); });
    input.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
  });
  await call('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'binding-test', version: '1' } });
  await fs.rename(root, root + '-original');
  await fs.symlink(outside, root, process.platform === 'win32' ? 'junction' : 'dir');
  const response = await call('tools/call', { name: 'deepsec_scan', arguments: {} });
  assert.equal(response.result.isError, true);
  assert.match(response.result.content[0].text, /bound workspace root changed/);
  assert(!JSON.stringify(response).includes('outside.js'));
});
