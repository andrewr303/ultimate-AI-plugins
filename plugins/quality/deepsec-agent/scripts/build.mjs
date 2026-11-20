#!/usr/bin/env node
import { build } from 'esbuild';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const vendor = path.join(root, 'vendor/deepsec-scanner/matchers/index.ts');
await build({ entryPoints: [vendor], outfile: path.join(root, 'runtime/upstream-matchers.mjs'), bundle: true, platform: 'node', format: 'esm', target: 'node22', legalComments: 'inline', banner: { js: '// Generated from uploaded DeepSec sources. See LICENSE and NOTICE. Matcher logic unchanged.' } });
await build({ entryPoints: [path.join(root, 'node_modules/minimatch/dist/esm/index.js')], outfile: path.join(root, 'runtime/glob.mjs'), bundle: true, platform: 'node', format: 'esm', target: 'node22', legalComments: 'inline', banner: { js: '// Bundled minimatch 10.2.6. See licenses/minimatch-LICENSE and transitive notices.' } });
for (const [from, to] of [['minimatch/LICENSE.md','minimatch-LICENSE'], ['brace-expansion/LICENSE','brace-expansion-LICENSE'], ['balanced-match/LICENSE.md','balanced-match-LICENSE']]) {
  await fs.copyFile(path.join(root, 'node_modules', from), path.join(root, 'licenses', to));
}
process.stdout.write('Rebuilt DeepSec matcher registry and glob dependency.\n');
