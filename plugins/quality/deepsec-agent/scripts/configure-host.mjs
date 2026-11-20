#!/usr/bin/env node
import { cp, lstat, mkdir, readFile, readdir, realpath, stat, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('../', import.meta.url));
const usage = 'Usage: node scripts/configure-host.mjs --host codex|claude|kimi|mcp --root /absolute/repository --out /new/destination';

function options(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i += 2) {
    if (!['--host', '--root', '--out'].includes(argv[i]) || !argv[i + 1] || argv[i + 1].startsWith('--')) throw new Error(usage);
    const key = argv[i].slice(2);
    if (key in result) throw new Error(`duplicate --${key}`);
    result[key] = argv[i + 1];
  }
  if (!['codex', 'claude', 'kimi', 'mcp'].includes(result.host) || !result.root || !result.out) throw new Error(usage);
  if (!isAbsolute(result.root) || !isAbsolute(result.out)) throw new Error('--root and --out must be absolute paths');
  return result;
}

async function json(path, value) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
}

async function assertNoLinks(path) {
  const info = await lstat(path);
  if (info.isSymbolicLink()) throw new Error(`refusing to package a symlink: ${path}`);
  if (info.isDirectory()) for (const item of await readdir(path)) await assertNoLinks(join(path, item));
}

async function copyCommon(destination) {
  for (const item of ['bin', 'runtime', 'skills', 'scripts']) {
    const path = join(source, item);
    await assertNoLinks(path);
    await cp(path, join(destination, item), { recursive: true, errorOnExist: true, force: false });
  }
  // Optional data/metadata directories differ between source and release bundles.
  for (const item of ['rules', 'docs', 'licenses', 'vendor', 'research', 'examples', 'LICENSE', 'NOTICE', 'README.md', 'package.json', 'package-lock.json']) {
    const path = join(source, item);
    try { await lstat(path); } catch (error) { if (error.code === 'ENOENT') continue; throw error; }
    await assertNoLinks(path);
    await cp(path, join(destination, item), { recursive: true, errorOnExist: true, force: false });
  }
}

const noParameters = { type: 'object', properties: {}, additionalProperties: false };

try {
  if (process.argv.includes('--help')) { process.stdout.write(`${usage}\nWrites destination files only; does not install or update host settings.\n`); process.exit(0); }
  const args = options(process.argv.slice(2));
  const root = await realpath(args.root);
  if (!(await stat(root)).isDirectory()) throw new Error('--root must identify a directory');
  const output = resolve(args.out);
  const sourceRoot = await realpath(source);
  const rel = relative(sourceRoot, output);
  if (rel === '' || (!rel.startsWith(`..${sep}`) && rel !== '..' && !isAbsolute(rel))) throw new Error('--out must be outside the source plugin directory');
  // Validate destination ancestors before writing. Existing output is always
  // refused, so reruns cannot replace a config or package that somebody edited.
  let ancestor = dirname(output);
  while (true) {
    try {
      const info = await lstat(ancestor);
      if (info.isSymbolicLink()) throw new Error('destination ancestors must not be symbolic links');
      if (!info.isDirectory()) throw new Error('destination parent must be a directory');
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    const next = dirname(ancestor);
    if (next === ancestor) break;
    ancestor = next;
  }
  try { await lstat(output); throw new Error('--out already exists; choose a new destination'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  await mkdir(dirname(output), { recursive: true });
  await mkdir(output);

  if (args.host === 'mcp') {
    const cli = join(sourceRoot, 'bin', 'deepsec-agent.mjs');
    const server = { command: 'node', args: [cli, 'serve', '--root', root] };
    await json(join(output, 'mcp.json'), { mcpServers: { 'deepsec-agent': server } });
    await writeFile(join(output, 'codex.toml'), `[mcp_servers.deepsec-agent]\ncommand = "node"\nargs = ${JSON.stringify(server.args)}\n`, { flag: 'wx' });
    await json(join(output, 'binding.json'), { host: args.host, workspaceRoot: root, runtime: cli });
  } else {
    const bundle = args.host === 'codex' ? join(output, 'plugins', 'deepsec-agent') : output;
    if (bundle !== output) await mkdir(bundle, { recursive: true });
    await copyCommon(bundle);
    await json(join(bundle, '.deepsec-host.json'), { host: args.host, workspaceRoot: root, version: '1.0.0' });
    if (args.host === 'kimi') {
      const kimiManifest = JSON.parse(await readFile(join(sourceRoot, 'kimi.plugin.json'), 'utf8'));
      kimiManifest.mcpServers['deepsec-agent'].args = ['./bin/deepsec-agent.mjs', 'serve', '--root', root];
      await json(join(bundle, 'kimi.plugin.json'), kimiManifest);
      // Keep the command-tool manifest for installations of the older Kimi CLI.
      await json(join(bundle, 'plugin.json'), {
        name: 'deepsec-agent', version: '1.0.0', description: 'Bound local source security tools for DeepSec Agent.',
        tools: [
          ['scan', 'Scan the bound authorized repository with built-in local security rules. Returns findings as JSON.'],
          ['doctor', 'Inspect local runtime and scanner availability for the bound repository.'],
          ['rules', 'List the built-in local security rules and coverage.'],
        ].map(([action, description]) => ({ name: `deepsec_${action}`, description, command: ['node', 'scripts/kimi-tool.mjs', action], parameters: noParameters })),
      });
    } else {
      const manifest = JSON.parse(await readFile(join(sourceRoot, 'plugin.json'), 'utf8'));
      await json(join(bundle, 'plugin.json'), manifest);
      const portableServer = { type: 'stdio', command: 'node', args: ['${PLUGIN_ROOT}/bin/deepsec-agent.mjs', 'serve', '--root', root], cwd: '${PLUGIN_ROOT}' };
      await json(join(bundle, 'mcp.json'), { $schema: 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json', mcpServers: { 'deepsec-agent': portableServer } });
      if (args.host === 'claude') {
        const claudeManifest = JSON.parse(await readFile(join(sourceRoot, '.claude-plugin', 'plugin.json'), 'utf8'));
        await json(join(bundle, '.claude-plugin', 'plugin.json'), claudeManifest);
        await json(join(bundle, '.mcp.json'), { mcpServers: { 'deepsec-agent': { type: 'stdio', command: 'node', args: ['${CLAUDE_PLUGIN_ROOT}/bin/deepsec-agent.mjs', 'serve', '--root', root] } } });
      }
      if (args.host === 'codex') {
        await json(join(output, '.agents', 'plugins', 'marketplace.json'), {
          name: 'deepsec-local', plugins: [{ name: 'deepsec-agent', source: './plugins/deepsec-agent' }],
        });
      }
    }
  }
  process.stdout.write(`${JSON.stringify({ host: args.host, workspaceRoot: root, output, installed: false }, null, 2)}\n`);
} catch (error) {
  process.stderr.write(`DeepSec configure: ${error.message}\n`);
  process.exitCode = 2;
}
