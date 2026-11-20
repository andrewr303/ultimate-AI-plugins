// Docs drift tests: the prose must not describe an engine that does not exist.
// Run: node --test tests/docs_drift.test.mjs
//
// The engine (examples/glass-lab/liquid-glass.js) is the source of truth. These
// tests import it, build its vocabulary (exports, createGlass options, function
// parameters, result fields, handle members, tiers, emitted SVG primitives) and
// check the documentation against it:
//   1. every export is documented in examples/glass-lab/README.md;
//   2. on any doc line that names liquid-glass.js, every backticked identifier
//      is part of the engine vocabulary;
//   3. `import { ... } from '.../liquid-glass.js'` names real exports;
//   4. object literals passed to engine functions (and to a createGlass handle's
//      update()) use real option names, and handle members exist;
//   5. tables with an "Engine option" column name real options;
//   6. the tier table in the README matches what explainTier can return;
//   7. filter primitives the docs attribute to the engine are emitted by
//      buildFilterMarkup, and every emitted primitive is named in the README;
//   8. examples/glass-lab/liquid-glass.d.ts declares exactly the engine's
//      exports, and its GlassOptions and Capabilities interfaces list exactly
//      the keys of DEFAULTS and capabilities().
// Doc files are discovered at run time, so new skills, agents or references
// are checked as soon as they are added.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as engine from '../examples/glass-lab/liquid-glass.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ENGINE_SOURCE = readFileSync(path.join(ROOT, 'examples/glass-lab/liquid-glass.js'), 'utf8');
const README = 'examples/glass-lab/README.md';
const DTS = 'examples/glass-lab/liquid-glass.d.ts';
const DTS_SOURCE = readFileSync(path.join(ROOT, DTS), 'utf8');
// Type names the declaration file exports (GlassOptions, GlassInfo, ...).
const DTS_TYPES = [...DTS_SOURCE.matchAll(/^export\s+(?:interface|type)\s+([A-Za-z_$][\w$]*)/gm)].map((m) => m[1]);

/* ------------------------------------------------------------------------ */
/* Doc discovery                                                            */
/* ------------------------------------------------------------------------ */

function walk(dir, keep, out = []) {
  const abs = path.join(ROOT, dir);
  if (!existsSync(abs)) return out;
  for (const name of readdirSync(abs).sort()) {
    if (name === 'node_modules' || name.startsWith('.')) continue;
    const rel = path.join(dir, name);
    if (statSync(path.join(ROOT, rel)).isDirectory()) walk(rel, keep, out);
    else if (keep(rel)) out.push(rel);
  }
  return out;
}

const isMd = (p) => p.endsWith('.md');
const DOCS = [
  ...walk('references', isMd),
  ...walk('skills', (p) => path.basename(p) === 'SKILL.md'),
  ...walk('agents', isMd),
  ...walk('commands', isMd),
  ...walk('templates', isMd),
  ...(existsSync(path.join(ROOT, README)) ? [README] : []),
  ...(existsSync(path.join(ROOT, 'README.md')) ? ['README.md'] : []),
];

/** Lines with their fence state. */
function docLines(rel) {
  const lines = readFileSync(path.join(ROOT, rel), 'utf8').split(/\r?\n/);
  const out = [];
  let fence = null;
  lines.forEach((text, i) => {
    const m = text.match(/^\s{0,3}(`{3,}|~{3,})/);
    if (m) {
      if (fence === null) fence = m[1][0];
      else if (m[1][0] === fence) fence = null;
      out.push({ rel, n: i + 1, text, fenced: true });
      return;
    }
    out.push({ rel, n: i + 1, text, fenced: fence !== null });
  });
  return out;
}

/** Fenced code blocks as arrays of lines. */
function fencedBlocks(rel) {
  const blocks = [];
  let cur = null;
  for (const l of docLines(rel)) {
    if (/^\s{0,3}(`{3,}|~{3,})/.test(l.text)) {
      if (cur) {
        blocks.push(cur);
        cur = null;
      } else cur = [];
      continue;
    }
    if (cur) cur.push(l);
  }
  return blocks;
}

const inlineCode = (text) => [...text.matchAll(/`([^`\n]+)`/g)].map((m) => m[1].trim());

/* ------------------------------------------------------------------------ */
/* Engine vocabulary                                                        */
/* ------------------------------------------------------------------------ */

const EXPORTS = new Set(Object.keys(engine));
const OPTIONS = new Set(Object.keys(engine.DEFAULTS));

/** Split a parameter list at top-level commas. */
function splitTop(s) {
  const parts = [];
  let depth = 0;
  let quote = null;
  let start = 0;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (quote) {
      if (c === quote && s[i - 1] !== '\\') quote = null;
      continue;
    }
    if (c === "'" || c === '"' || c === '`') quote = c;
    else if ('([{'.includes(c)) depth++;
    else if (')]}'.includes(c)) depth--;
    else if (c === ',' && depth === 0) {
      parts.push(s.slice(start, i));
      start = i + 1;
    }
  }
  parts.push(s.slice(start));
  return parts.map((p) => p.trim()).filter(Boolean);
}

/** Index of the bracket that closes the one at `open`. */
function matching(s, open) {
  const pairs = { '(': ')', '{': '}', '[': ']' };
  const want = pairs[s[open]];
  let depth = 0;
  let quote = null;
  for (let i = open; i < s.length; i++) {
    const c = s[i];
    if (quote) {
      if (c === quote && s[i - 1] !== '\\') quote = null;
      continue;
    }
    if (c === "'" || c === '"' || c === '`') quote = c;
    else if (c === s[open]) depth++;
    else if (c === want && --depth === 0) return i;
  }
  return -1;
}

/** Parameter names of a function, including names destructured from an object parameter. */
function paramNames(fn) {
  const src = fn.toString();
  const open = src.indexOf('(');
  const close = matching(src, open);
  const names = new Set();
  for (const part of splitTop(src.slice(open + 1, close))) {
    if (part.startsWith('{')) {
      const inner = part.slice(1, matching(part, 0));
      for (const p of splitTop(inner)) {
        const m = p.match(/^([A-Za-z_$][\w$]*)/);
        if (m) names.add(m[1]);
      }
    } else {
      const m = part.match(/^([A-Za-z_$][\w$]*)/);
      if (m) names.add(m[1]);
    }
  }
  return names;
}

const PARAMS = new Map(
  [...EXPORTS].filter((k) => typeof engine[k] === 'function').map((k) => [k, paramNames(engine[k])]),
);

/** Members of the handle createGlass returns, read from its final `return {` block. */
function handleMembers() {
  const src = engine.createGlass.toString();
  const at = src.lastIndexOf('return {');
  assert.ok(at > 0, 'createGlass source has a final "return {" block');
  const open = src.indexOf('{', at);
  const body = src.slice(open + 1, matching(src, open));
  const members = new Set();
  let depth = 0;
  for (const line of body.split('\n')) {
    if (depth === 0) {
      const m = line.match(/^\s*(?:get\s+|set\s+|async\s+)?([A-Za-z_$][\w$]*)\s*(?:[:(,]|$)/);
      if (m) members.add(m[1]);
    }
    for (const c of line) {
      if (c === '{') depth++;
      else if (c === '}') depth--;
    }
  }
  return members;
}
const HANDLE = handleMembers();

const FIELD = engine.displacementField({ width: 40, height: 24, radius: 8, bezelWidth: 8 });
const SPECULAR = engine.specularField({ width: 40, height: 24, radius: 8 });
const RESULT_FIELDS = new Set([
  ...Object.keys(FIELD),
  ...Object.keys(SPECULAR),
  ...Object.keys(engine.explainTier()),
  ...Object.keys(engine.capabilities(undefined)),
]);

const TIERS = new Set(['auto', 'refract', 'frost', 'solid']);

/** Every tier explainTier can return, by enumerating its boolean inputs. */
function reachableTiers() {
  const seen = new Set();
  const flags = ['reducedTransparency', 'contrastMore', 'forcedColors', 'supportsBackdrop'];
  for (let mask = 0; mask < 1 << flags.length; mask++) {
    for (const engineName of ['chromium', 'webkit', 'gecko', 'unknown']) {
      for (const preferred of TIERS) {
        const input = { engine: engineName, preferred };
        flags.forEach((f, i) => (input[f] = Boolean(mask & (1 << i))));
        seen.add(engine.explainTier(input).tier);
      }
    }
  }
  return seen;
}

/** Union of everything buildFilterMarkup can emit, over its option switches. */
function filterMarkupMatrix() {
  const out = [];
  for (const blur of [0, 3]) {
    for (const saturation of [1, 1.5]) {
      for (const chromaticAberration of [0, 0.3]) {
        for (const specularHref of ['', 'data:image/png;base64,AA==']) {
          for (const specularOpacity of [1, 0.5]) {
            out.push(
              engine.buildFilterMarkup({
                id: 'drift',
                mapHref: 'data:image/png;base64,AA==',
                specularHref,
                width: 40,
                height: 24,
                scale: FIELD.filterScale,
                chromaticAberration,
                blur,
                saturation,
                specularOpacity,
              }),
            );
          }
        }
      }
    }
  }
  return out;
}
const MARKUP = filterMarkupMatrix();
const PRIMITIVES = new Set(MARKUP.flatMap((m) => [...m.matchAll(/<(fe[A-Z]\w*)/g)].map((x) => x[1])));

const VOCAB = new Set([
  ...EXPORTS,
  ...OPTIONS,
  ...[...PARAMS.values()].flatMap((s) => [...s]),
  ...RESULT_FIELDS,
  ...HANDLE,
  ...Object.keys(engine.PROFILES),
  ...Object.keys(engine.MEDIA_QUERIES),
  ...TIERS,
  ...PRIMITIVES,
  ...DTS_TYPES,
  'true',
  'false',
  'null',
]);

/** Check one backticked token; returns an error string or null. */
function checkToken(token) {
  const m = token.match(/^([A-Za-z_$][\w$]*)((?:\.[A-Za-z_$][\w$]*)*)(\(.*)?$/);
  if (!m) return null; // not an identifier reference (paths, CSS, prose)
  if (!m[3] && existsSync(path.join(ROOT, token))) return null; // a plugin file such as LICENSE
  const head = m[1];
  const rest = m[2] ? m[2].slice(1).split('.') : [];
  if (rest.length === 0) return VOCAB.has(head) ? null : `\`${token}\`: "${head}" is not an engine export, option, parameter or field`;
  if (!EXPORTS.has(head)) return null; // dotted names on other objects (handle.x, navigator.y) are not checked here
  const value = engine[head];
  if (value && typeof value === 'object' && !(rest[0] in value)) {
    return `\`${token}\`: ${head} has no key "${rest[0]}"`;
  }
  return null;
}

const fmtHit = (l, msg) => `${l.rel}:${l.n}: ${msg}`;

/* ------------------------------------------------------------------------ */
/* Tests                                                                    */
/* ------------------------------------------------------------------------ */

test('the doc set is discovered and the engine vocabulary is not empty', () => {
  assert.ok(DOCS.includes(README), 'glass-lab README found');
  assert.ok(DOCS.some((d) => d.startsWith('references/')), 'references found');
  assert.ok(EXPORTS.has('createGlass') && EXPORTS.has('buildFilterMarkup'), 'engine exports read');
  assert.ok(OPTIONS.size >= 10, 'DEFAULTS lists the createGlass options');
  for (const m of ['update', 'refresh', 'destroy', 'tier', 'info']) assert.ok(HANDLE.has(m), `handle member ${m} parsed`);
  for (const p of ['pixelRatio', 'minJacobian', 'foldHeadroom']) {
    assert.ok(PARAMS.get('displacementField').has(p), `displacementField parameter ${p} parsed`);
  }
  for (const f of ['filterScale', 'attenuation', 'maxDisplacement', 'neutralBias']) {
    assert.ok(RESULT_FIELDS.has(f), `displacementField result field ${f} read`);
  }
});

test('every engine export is documented in the glass-lab README', () => {
  const text = readFileSync(path.join(ROOT, README), 'utf8');
  const documented = new Set(
    inlineCode(text)
      .map((t) => t.match(/^([A-Za-z_$][\w$]*)/))
      .filter(Boolean)
      .map((m) => m[1]),
  );
  const missing = [...EXPORTS].filter((name) => !documented.has(name));
  assert.deepEqual(missing, [], `exports missing from ${README} (write each in backticks): ${missing.join(', ')}`);
});

test('backticked identifiers on lines that name liquid-glass.js exist in the engine', () => {
  const problems = [];
  for (const rel of DOCS) {
    for (const l of docLines(rel)) {
      if (!l.text.includes('liquid-glass.js')) continue;
      for (const token of inlineCode(l.text)) {
        const err = checkToken(token);
        if (err) problems.push(fmtHit(l, err));
      }
    }
  }
  assert.deepEqual(problems, []);
});

test('imports from liquid-glass.js name real exports', () => {
  const problems = [];
  for (const rel of DOCS) {
    const text = readFileSync(path.join(ROOT, rel), 'utf8');
    for (const m of text.matchAll(/import\s*\{([^}]*)\}\s*from\s*['"][^'"]*liquid-glass\.js['"]/g)) {
      for (const part of splitTop(m[1])) {
        const name = part.split(/\s+as\s+/)[0].trim();
        if (!EXPORTS.has(name)) problems.push(`${rel}: imports "${name}", which liquid-glass.js does not export`);
      }
    }
  }
  assert.deepEqual(problems, []);
});

test('option objects passed to engine functions use real names', () => {
  const problems = [];
  const keysOf = (obj) =>
    splitTop(obj)
      .map((p) => p.match(/^([A-Za-z_$][\w$]*)\s*:/) || p.match(/^([A-Za-z_$][\w$]*)$/))
      .filter(Boolean)
      .map((m) => m[1]);
  const scan = (rel, text, where) => {
    for (const name of PARAMS.keys()) {
      const re = new RegExp(`\\b${name}\\(`, 'g');
      for (const m of text.matchAll(re)) {
        const open = m.index + m[0].length - 1;
        const close = matching(text, open);
        if (close < 0) continue;
        const args = splitTop(text.slice(open + 1, close));
        // createGlass(element, options): options are DEFAULTS keys. Other exports take one object.
        const objArg = name === 'createGlass' ? args[1] : args[0];
        if (!objArg || !objArg.startsWith('{')) continue;
        const allowed = name === 'createGlass' ? OPTIONS : PARAMS.get(name);
        for (const key of keysOf(objArg.slice(1, matching(objArg, 0)))) {
          if (!allowed.has(key)) problems.push(`${rel}${where}: ${name}() has no option "${key}"`);
        }
      }
    }
  };
  for (const rel of DOCS) {
    for (const l of docLines(rel)) {
      if (l.fenced) continue;
      for (const token of inlineCode(l.text)) scan(rel, token, `:${l.n}`);
    }
    for (const block of fencedBlocks(rel)) {
      const code = block.map((l) => l.text).join('\n');
      const where = block.length ? `:${block[0].n}` : '';
      scan(rel, code, where);
      if (!/liquid-glass\.js/.test(code)) continue;
      // Handles returned by createGlass in a block that imports the engine.
      for (const h of code.matchAll(/\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*createGlass\(/g)) {
        const v = h[1];
        for (const use of code.matchAll(new RegExp(`\\b${v}\\.([A-Za-z_$][\\w$]*)`, 'g'))) {
          if (!HANDLE.has(use[1])) problems.push(`${rel}${where}: createGlass handle has no member "${use[1]}"`);
        }
        for (const up of code.matchAll(new RegExp(`\\b${v}\\.update\\(`, 'g'))) {
          const open = up.index + up[0].length - 1;
          const arg = code.slice(open + 1, matching(code, open)).trim();
          if (!arg.startsWith('{')) continue;
          for (const key of keysOf(arg.slice(1, matching(arg, 0)))) {
            if (!OPTIONS.has(key)) problems.push(`${rel}${where}: handle.update() has no option "${key}"`);
          }
        }
      }
    }
  }
  assert.deepEqual(problems, []);
});

test('"Engine option" table columns name real createGlass options', () => {
  const problems = [];
  let columns = 0;
  for (const rel of DOCS) {
    const lines = docLines(rel);
    for (let i = 0; i < lines.length - 1; i++) {
      const head = lines[i].text;
      if (lines[i].fenced || !/^\s*\|/.test(head) || !/^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1].text)) continue;
      const cells = head.split('|').slice(1, -1).map((c) => c.trim());
      const col = cells.findIndex((c) => /engine option/i.test(c));
      if (col < 0) continue;
      columns++;
      for (let j = i + 2; j < lines.length && /^\s*\|/.test(lines[j].text); j++) {
        const cell = (lines[j].text.split('|').slice(1, -1)[col] || '').trim();
        if (/^CSS\b/.test(cell)) continue; // CSS custom properties, not engine options
        for (const token of inlineCode(cell)) {
          const m = token.match(/^([A-Za-z_$][\w$]*)$/);
          if (m && !OPTIONS.has(m[1]) && !TIERS.has(m[1])) {
            problems.push(fmtHit(lines[j], `"${m[1]}" is not a key of DEFAULTS (createGlass options)`));
          }
        }
      }
    }
  }
  assert.ok(columns >= 1, 'at least one "Engine option" column exists (glass-lab README Controls table)');
  assert.deepEqual(problems, []);
});

test('README tier table matches the tiers explainTier returns', () => {
  const reachable = reachableTiers();
  assert.deepEqual([...reachable].sort(), ['frost', 'refract', 'solid']);
  const lines = docLines(README);
  const start = lines.findIndex((l) => /^\|\s*Tier\s*\|/.test(l.text));
  assert.ok(start >= 0, 'README has a tier table');
  const documented = new Set();
  for (let j = start + 2; j < lines.length && /^\|/.test(lines[j].text); j++) {
    const first = lines[j].text.split('|')[1];
    for (const t of inlineCode(first)) documented.add(t);
  }
  assert.deepEqual([...documented].sort(), [...reachable].sort());
});

test('filter primitives the docs attribute to the engine are emitted by buildFilterMarkup', () => {
  for (const core of ['feImage', 'feColorMatrix', 'feDisplacementMap', 'feGaussianBlur', 'feComposite', 'feBlend']) {
    assert.ok(PRIMITIVES.has(core), `buildFilterMarkup emits ${core} for some options`);
  }
  // Lines that talk about this engine's filter, minus lines that describe a studied library.
  const OTHER_LIBRARY = /glasshq|simple-liquid-glass|liquidGL|liquid-gl\b|ybouane|liquid-glass-react|samasante/i;
  const problems = [];
  for (const rel of DOCS) {
    for (const l of docLines(rel)) {
      const aboutEngine = rel === README || /liquid-glass\.js|buildFilterMarkup/.test(l.text);
      if (!aboutEngine || OTHER_LIBRARY.test(l.text)) continue;
      for (const m of l.text.matchAll(/\b(fe[A-Z][A-Za-z]+)\b/g)) {
        if (!PRIMITIVES.has(m[1])) problems.push(fmtHit(l, `${m[1]} is not emitted by buildFilterMarkup`));
      }
    }
  }
  assert.deepEqual(problems, []);
});

test('every primitive buildFilterMarkup emits is named in the README', () => {
  const text = readFileSync(path.join(ROOT, README), 'utf8');
  const missing = [...PRIMITIVES].filter((p) => !text.includes(p));
  assert.deepEqual(missing, [], `README does not name: ${missing.join(', ')}`);
});

test('README filter claims hold: sRGB, x from R, y from G, PNG maps', () => {
  for (const m of MARKUP) {
    assert.match(m, /color-interpolation-filters="sRGB"/);
    for (const d of m.matchAll(/<feDisplacementMap[^>]*>/g)) {
      assert.match(d[0], /xChannelSelector="R"/);
      assert.match(d[0], /yChannelSelector="G"/);
    }
  }
  assert.match(ENGINE_SOURCE, /toDataURL\('image\/png'\)/, 'maps are encoded as PNG');
  const readme = readFileSync(path.join(ROOT, README), 'utf8');
  assert.match(readme, /color-interpolation-filters="sRGB"/);
  assert.match(readme, /xChannelSelector="R"/);
  assert.match(readme, /yChannelSelector="G"/);
});

/* ------------------------------------------------------------------------ */
/* TypeScript declarations                                                   */
/* ------------------------------------------------------------------------ */

/** Keys of `export interface Name { ... }` in the declaration file. */
function interfaceKeys(name) {
  const m = DTS_SOURCE.match(new RegExp(`export interface ${name}\\s*\\{`));
  assert.ok(m, `${DTS} declares interface ${name}`);
  const open = m.index + m[0].length - 1;
  const body = DTS_SOURCE.slice(open + 1, matching(DTS_SOURCE, open));
  return [...body.matchAll(/^\s*(?:readonly\s+)?([A-Za-z_$][\w$]*)\??\s*:/gm)].map((k) => k[1]).sort();
}

test('liquid-glass.d.ts declares exactly the exports of liquid-glass.js', () => {
  const declared = [
    ...DTS_SOURCE.matchAll(/^export\s+declare\s+(?:function|const|let|var|class)\s+([A-Za-z_$][\w$]*)/gm),
  ].map((m) => m[1]);
  const dupes = declared.filter((n, i) => declared.indexOf(n) !== i);
  assert.deepEqual(dupes, [], 'no export is declared twice');
  const missing = [...EXPORTS].filter((n) => !declared.includes(n)).sort();
  const extra = declared.filter((n) => !EXPORTS.has(n)).sort();
  assert.deepEqual({ missing, extra }, { missing: [], extra: [] });
});

test('liquid-glass.d.ts option and capability interfaces match the engine', () => {
  assert.deepEqual(interfaceKeys('GlassOptions'), [...OPTIONS].sort());
  assert.deepEqual(interfaceKeys('Capabilities'), Object.keys(engine.capabilities(undefined)).sort());
  assert.deepEqual(interfaceKeys('TierInput'), [...PARAMS.get('explainTier')].sort());
  assert.deepEqual(
    interfaceKeys('DisplacementField').filter((k) => k !== 'data'),
    Object.keys(FIELD).filter((k) => k !== 'data').sort(),
  );
  const handle = interfaceKeys('GlassHandle');
  const methods = [...DTS_SOURCE.slice(DTS_SOURCE.indexOf('export interface GlassHandle')).split('}')[0].matchAll(/^\s*([A-Za-z_$][\w$]*)\(/gm)].map((m) => m[1]);
  assert.deepEqual([...handle, ...methods].sort(), [...HANDLE].sort());
});

test('liquid-glass.d.ts carries the attribution header', () => {
  const head = DTS_SOURCE.split('\n').slice(0, 4).join('\n');
  assert.match(head, /Liquid Glass Studio engine/);
  assert.match(head, /MIT License/);
  assert.match(head, /Not affiliated with Apple/);
});
