#!/usr/bin/env node
import assert from 'node:assert/strict';
import { access, readFile, readdir } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultRoot = fileURLToPath(new URL('../', import.meta.url));
const args = process.argv.slice(2);
if (args.length && (args.length !== 2 || args[0] !== '--dir')) {
  process.stderr.write('Usage: node scripts/validate-plugin.mjs [--dir /plugin/path]\n'); process.exit(2);
}
const root = resolve(args[1] ?? defaultRoot);
const readJSON = async path => JSON.parse(await readFile(join(root, path), 'utf8'));
const exists = async path => { await access(join(root, path)); };
const namePattern = /^[a-z0-9]+(?:[.-][a-z0-9]+)*$/;
const versionPattern = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;

try {
  const manifest = await readJSON('plugin.json');
  assert.equal(manifest.name, 'deepsec-agent');
  assert.match(manifest.name, namePattern);
  assert.match(manifest.version, versionPattern);
  assert.equal(typeof manifest.description, 'string');
  await exists('bin/deepsec-agent.mjs');
  const native = Array.isArray(manifest.tools);
  if (native) {
    const binding = await readJSON('.deepsec-host.json');
    assert.equal(binding.host, 'kimi');
    assert.equal(typeof binding.workspaceRoot, 'string');
    assert.deepEqual(manifest.tools.map(tool => tool.name).sort(), ['deepsec_doctor', 'deepsec_rules', 'deepsec_scan']);
    for (const tool of manifest.tools) {
      assert.deepEqual(tool.command.slice(0, 2), ['node', 'scripts/kimi-tool.mjs']);
      assert.deepEqual(tool.parameters, { type: 'object', properties: {}, additionalProperties: false });
    }
    await exists('scripts/kimi-tool.mjs');
  } else {
    assert.equal(manifest.$schema, 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json');
    const mcp = await readJSON('mcp.json');
    assert.equal(mcp.$schema, 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json');
    assert.deepEqual(Object.keys(mcp.mcpServers), ['deepsec-agent']);
    const server = mcp.mcpServers['deepsec-agent'];
    assert.equal(server.type, 'stdio');
    assert.equal(server.command, 'node');
    assert.ok(server.args.every(value => typeof value === 'string'));
    assert.ok(server.args[0].startsWith('${PLUGIN_ROOT}/'));
    await exists(server.args[0].replace('${PLUGIN_ROOT}/', ''));
    const entries = await readdir(root);
    if (entries.includes('.claude-plugin')) {
      const claude = await readJSON('.claude-plugin/plugin.json');
      assert.equal(claude.name, manifest.name);
      assert.equal(claude.version, manifest.version);
      const claudeMcp = await readJSON('.mcp.json');
      const claudeServer = claudeMcp.mcpServers['deepsec-agent'];
      assert.equal(claudeServer.command, 'node');
      assert.ok(claudeServer.args[0].startsWith('${CLAUDE_PLUGIN_ROOT}/'));
      await exists(claudeServer.args[0].replace('${CLAUDE_PLUGIN_ROOT}/', ''));
    }
    const interfaceMetadata = manifest.extensions?.['com.openai']?.interface;
    if (interfaceMetadata) {
      assert.equal(typeof interfaceMetadata.displayName, 'string');
      assert.equal(typeof interfaceMetadata.shortDescription, 'string');
      assert.ok(Array.isArray(interfaceMetadata.capabilities));
    }
  }
  const skills = await readdir(join(root, 'skills'), { withFileTypes: true });
  const seen = new Set();
  for (const skill of skills.filter(entry => entry.isDirectory() && !entry.name.startsWith('.'))) {
    const content = await readFile(join(root, 'skills', skill.name, 'SKILL.md'), 'utf8');
    const frontmatter = content.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)?.[1];
    assert.ok(frontmatter, `missing skill frontmatter: ${skill.name}`);
    // The authored package intentionally uses simple YAML scalars. Validate
    // their concrete syntax; this is not a general-purpose YAML parser.
    const name = frontmatter.match(/^name: ([a-z0-9-]+)$/m)?.[1];
    const descriptionLiteral = frontmatter.match(/^description: (".*")$/m)?.[1];
    assert.ok(name && !seen.has(name)); seen.add(name);
    assert.ok(JSON.parse(descriptionLiteral).trim());
    const metadata = JSON.parse(await readFile(join(root, 'skills', skill.name, 'agents', 'openai.yaml'), 'utf8'));
    assert.equal(typeof metadata.interface.display_name, 'string');
    assert.equal(typeof metadata.interface.short_description, 'string');
    assert.equal(typeof metadata.policy.allow_implicit_invocation, 'boolean');
  }
  assert.ok(seen.size > 0);
  process.stdout.write(`${JSON.stringify({ valid: true, root, format: native ? 'kimi-native' : 'portable', skills: [...seen], hostLoaderVerified: false })}\n`);
} catch (error) {
  process.stderr.write(`DeepSec package validation failed: ${error.message}\n`);
  process.exitCode = 1;
}
