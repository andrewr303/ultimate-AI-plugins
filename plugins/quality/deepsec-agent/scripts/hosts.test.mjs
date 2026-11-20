import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('../', import.meta.url));
const configure = path.join(source, 'scripts', 'configure-host.mjs');
const validate = path.join(source, 'scripts', 'validate-plugin.mjs');
const run = (script, args = [], options = {}) => spawnSync(process.execPath, [script, ...args], {
  encoding: 'utf8', timeout: 30000, maxBuffer: 8 * 1024 * 1024, ...options,
});
function fixture(t) {
  const base = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'deepsec-host-test-'));
  t.after(() => fs.rmSync(base, { recursive: true, force: true }));
  const repo = path.join(base, 'repository with spaces');
  fs.mkdirSync(repo);
  fs.writeFileSync(path.join(repo, 'safe.js'), 'export const answer = 42;\n');
  return { base, repo };
}

function assertSourceBundle(bundle) {
  for (const item of ['licenses/minimatch-LICENSE', 'licenses/brace-expansion-LICENSE', 'licenses/balanced-match-LICENSE', 'vendor', 'research', 'examples', 'package-lock.json', 'scripts/build.mjs']) {
    assert.ok(fs.existsSync(path.join(bundle, item)), `missing bundled source or notice: ${item}`);
  }
  assert.equal(fs.existsSync(path.join(bundle, 'node_modules')), false);
}

test('source host manifests and skill metadata validate', () => {
  const result = run(validate);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).hostLoaderVerified, false);
});

test('default launcher refuses an implicit repository root', () => {
  const env = { ...process.env };
  delete env.DEEPSEC_WORKSPACE_ROOT;
  const result = run(path.join(source, 'scripts/start-server.mjs'), [], { env });
  assert.equal(result.status, 2);
  assert.equal(result.stdout, '');
  assert.match(result.stderr, /DEEPSEC_WORKSPACE_ROOT/);
});

test('generator rejects relative roots, overwrite, and output within source', t => {
  const { base, repo } = fixture(t);
  let result = run(configure, ['--host', 'kimi', '--root', '.', '--out', path.join(base, 'relative')]);
  assert.equal(result.status, 2);
  assert.equal(fs.existsSync(path.join(base, 'relative')), false);
  result = run(configure, ['--host', 'kimi', '--root', repo, '--out', source]);
  assert.equal(result.status, 2);
  result = run(configure, ['--host', 'mcp', '--root', repo, '--out', path.join(base, 'out')]);
  assert.equal(result.status, 0, result.stderr);
  const original = fs.readFileSync(path.join(base, 'out', 'mcp.json'), 'utf8');
  result = run(configure, ['--host', 'mcp', '--root', repo, '--out', path.join(base, 'out')]);
  assert.equal(result.status, 2);
  assert.equal(fs.readFileSync(path.join(base, 'out', 'mcp.json'), 'utf8'), original);
});

test('generated Codex marketplace and Claude package bind exact roots', t => {
  const { base, repo } = fixture(t);
  for (const host of ['codex', 'claude']) {
    const out = path.join(base, host);
    const result = run(configure, ['--host', host, '--root', repo, '--out', out]);
    assert.equal(result.status, 0, result.stderr);
    const bundle = host === 'codex' ? path.join(out, 'plugins/deepsec-agent') : out;
    const valid = run(validate, ['--dir', bundle]);
    assert.equal(valid.status, 0, valid.stderr);
    const config = JSON.parse(fs.readFileSync(path.join(bundle, host === 'codex' ? 'mcp.json' : '.mcp.json'), 'utf8'));
    assert.deepEqual(config.mcpServers['deepsec-agent'].args.slice(-2), ['--root', fs.realpathSync(repo)]);
    assertSourceBundle(bundle);
    assert.equal(fs.existsSync(path.join(bundle, '.agents/plugins/marketplace.json')), false);
    if (host === 'codex') {
      const market = JSON.parse(fs.readFileSync(path.join(out, '.agents/plugins/marketplace.json'), 'utf8'));
      assert.equal(market.plugins[0].source, './plugins/deepsec-agent');
    }
  }
});

test('generated Kimi bundle runs copied runtime and rejects root override', t => {
  const { base, repo } = fixture(t);
  const out = path.join(base, 'kimi');
  const result = run(configure, ['--host', 'kimi', '--root', repo, '--out', out]);
  assert.equal(result.status, 0, result.stderr);
  const valid = run(validate, ['--dir', out]);
  assert.equal(valid.status, 0, valid.stderr);
  assertSourceBundle(out);
  const manifest = JSON.parse(fs.readFileSync(path.join(out, 'kimi.plugin.json'), 'utf8'));
  assert.deepEqual(manifest.mcpServers['deepsec-agent'], {
    type: 'stdio',
    command: 'node',
    args: ['./bin/deepsec-agent.mjs', 'serve', '--root', fs.realpathSync(repo)],
    cwd: './',
  });
  const wrapper = path.join(out, 'scripts/kimi-tool.mjs');
  let call = run(wrapper, ['scan'], { input: '{}', cwd: base });
  assert.equal(call.status, 0, call.stderr);
  const report = JSON.parse(call.stdout);
  assert.equal(report.complete, true);
  assert.equal(report.findings.length, 0);
  call = run(wrapper, ['rules'], { input: '{}', cwd: base });
  assert.equal(call.status, 0, call.stderr);
  assert.ok(JSON.parse(call.stdout).rules.length > 0);
  fs.symlinkSync(path.join(repo, 'safe.js'), path.join(repo, 'linked.js'));
  call = run(wrapper, ['scan'], { input: '{}', cwd: base });
  assert.equal(call.status, 0, call.stderr);
  const partial = JSON.parse(call.stdout);
  assert.equal(partial.complete, false);
  assert.equal(partial.coverage[0].status, 'partial');
  assert.equal(partial.coverage[0].skipReasons.symlink, 1);
  call = run(wrapper, ['scan'], { input: JSON.stringify({ root: base }) });
  assert.equal(call.status, 2);
  assert.equal(call.stdout, '');
  assert.match(call.stderr, /takes no parameters/);
  call = run(wrapper, ['unknown'], { input: '{}' });
  assert.equal(call.status, 2);
});

test('MCP config generation preserves spaces and does not install anything', t => {
  const { base, repo } = fixture(t);
  const out = path.join(base, 'mcp');
  const result = run(configure, ['--host', 'mcp', '--root', repo, '--out', out]);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).installed, false);
  const config = JSON.parse(fs.readFileSync(path.join(out, 'mcp.json'), 'utf8'));
  assert.deepEqual(config.mcpServers['deepsec-agent'].args.slice(-2), ['--root', fs.realpathSync(repo)]);
  assert.equal(fs.readdirSync(out).length, 3);
});
