#!/usr/bin/env node
// design-variations: logic check for Claude Design .dc.html artboards, without the canvas runtime.
//
//   node dc-check.mjs <file.dc.html | folder> [--json]
//
// For every artboard it: reads the data-props defaults; for every value of every enum Tweak (one at a time,
// others at their defaults) it builds the Component with a small DCLogic stand-in, calls renderVals(), checks
// that every {{ hole }} in the template resolves (inside <sc-for> loops against the first item), then fires
// every handler function renderVals() returns (top level and one level inside lists) with a fake event,
// re-rendering after each, and reports any exception. It does not render markup or judge looks; it catches the
// logic errors that break a canvas option silently. Holes that never resolve are warnings, because optional item
// fields and props a parent passes in can legitimately be missing here; read each one. Exit 1 when anything
// threw, 0 otherwise.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';

const args = process.argv.slice(2);
const target = args.find((a) => !a.startsWith('--'));
const asJson = args.includes('--json');
if (!target) { console.error('usage: node dc-check.mjs <file.dc.html | folder> [--json]'); process.exit(2); }

const files = statSync(target).isDirectory()
  ? readdirSync(target, { recursive: true }).map(String).filter((f) => f.endsWith('.dc.html') && !f.split(/[\\/]/).includes('ds')).map((f) => join(target, f))
  : [target];

const decode = (s) => s.replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

class DCLogic {
  constructor(props) { this.props = props || {}; this.state = {}; }
  setState(patch, cb) {
    const next = typeof patch === 'function' ? patch(this.state, this.props) : patch;
    this.state = { ...this.state, ...(next || {}) };
    if (typeof cb === 'function') cb();
  }
  forceUpdate() {}
}

// Minimal stand-ins for what the canvas runtime provides (React 18, a browser window). Timers never fire.
const noop = () => {};
const fakeEl = () => ({ focus: noop, blur: noop, scrollIntoView: noop, scrollTo: noop, getBoundingClientRect: () => ({ top: 0, left: 0, width: 100, height: 40, right: 100, bottom: 40 }), addEventListener: noop, removeEventListener: noop, contains: () => false, closest: () => null, querySelector: () => null, querySelectorAll: () => [], style: {}, classList: { add: noop, remove: noop, toggle: noop, contains: () => false }, dataset: {}, offsetWidth: 100, offsetHeight: 40, scrollHeight: 40, clientHeight: 40, scrollTop: 0 });
const SANDBOX = {
  React: { createRef: () => ({ current: null }), Fragment: 'Fragment', createElement: () => null, Component: DCLogic },
  window: { addEventListener: noop, removeEventListener: noop, innerWidth: 1440, innerHeight: 900, matchMedia: () => ({ matches: false, addEventListener: noop, removeEventListener: noop }), getComputedStyle: () => ({}), requestAnimationFrame: noop, cancelAnimationFrame: noop, scrollTo: noop, location: { hash: '', search: '' } },
  document: { addEventListener: noop, removeEventListener: noop, querySelector: () => null, querySelectorAll: () => [], getElementById: () => null, activeElement: null, body: fakeEl(), documentElement: fakeEl() },
  setTimeout: () => 0, clearTimeout: noop, setInterval: () => 0, clearInterval: noop, requestAnimationFrame: () => 0, cancelAnimationFrame: noop,
  localStorage: { getItem: () => null, setItem: noop, removeItem: noop }, sessionStorage: { getItem: () => null, setItem: noop, removeItem: noop },
  navigator: { clipboard: { writeText: () => Promise.resolve() }, userAgent: 'dc-check' }, queueMicrotask: noop,
};
SANDBOX.window.document = SANDBOX.document;

function fakeEvent() {
  const target = { ...fakeEl(), value: 'Test value', checked: true, files: [], dataset: {} };
  return {
    target, currentTarget: target, key: 'Enter', code: 'Enter', shiftKey: false, metaKey: false, ctrlKey: false, altKey: false,
    clientX: 10, clientY: 10, deltaY: 0, preventDefault() {}, stopPropagation() {},
    dataTransfer: { setData() {}, getData: () => '', effectAllowed: 'move', dropEffect: 'move' },
  };
}

// Hole scopes: track <sc-for list="{{ path }}" as="name"> around each hole.
function holesWithScopes(tpl) {
  const out = [];
  const stack = [];
  const re = /<sc-for\b([^>]*)>|<\/sc-for>|\{\{([\s\S]*?)\}\}/g;
  let m;
  while ((m = re.exec(tpl))) {
    if (m[1] !== undefined) {
      const list = (m[1].match(/list="\{\{\s*([^}]+?)\s*\}\}"/) || [])[1];
      const as = (m[1].match(/\bas="([^"]+)"/) || [])[1] || 'item';
      stack.push({ list, as });
    } else if (m[0] === '</sc-for>') {
      stack.pop();
    } else {
      out.push({ path: m[2].trim(), scopes: stack.slice() });
    }
  }
  return out;
}

const LITERAL = /^(true|false|null|-?\d+(\.\d+)?|'[^']*'|"[^"]*")$/;
function resolve(path, vals, scopes) {
  if (LITERAL.test(path) || path === '$index') return { ok: true };
  const parts = path.split('.');
  let base = vals;
  for (let i = scopes.length - 1; i >= 0; i--) {
    if (scopes[i].as === parts[0]) {
      const listVal = resolve(scopes[i].list, vals, scopes.slice(0, i)).value;
      if (!Array.isArray(listVal)) return { ok: false, why: `loop list ${scopes[i].list} is not an array` };
      if (!listVal.length) return { ok: true, empty: true };
      base = { [parts[0]]: listVal[0] };
      break;
    }
  }
  let cur = base;
  for (const p of parts) {
    if (cur == null || !(p in Object(cur))) return { ok: false, why: `${path} is undefined` };
    cur = cur[p];
  }
  return { ok: true, value: cur };
}

function handlersOf(vals) {
  const hs = [];
  for (const [k, v] of Object.entries(vals || {})) {
    if (typeof v === 'function') hs.push([k, v]);
    else if (Array.isArray(v)) v.slice(0, 3).forEach((item, i) => {
      if (item && typeof item === 'object') for (const [k2, v2] of Object.entries(item)) if (typeof v2 === 'function') hs.push([`${k}[${i}].${k2}`, v2]);
    });
  }
  return hs;
}

const report = [];
let failed = false;
for (const file of files) {
  const raw = readFileSync(file, 'utf8');
  const r = { file: basename(file), states: 0, unresolved: [], errors: [] };
  const sm = raw.match(/<script type="text\/x-dc" data-dc-script([^>]*)>([\s\S]*?)<\/script>/);
  const tpl = (raw.split('<x-dc>')[1] || '').split('</x-dc>')[0];
  if (!sm) { r.errors.push('no data-dc-script block'); report.push(r); failed = true; continue; }
  let props = {};
  const pm = sm[1].match(/data-props='([\s\S]*?)'/) || sm[1].match(/data-props="([\s\S]*?)"/);
  try { props = pm ? JSON.parse(decode(pm[1])) : {}; } catch (e) { r.errors.push('data-props JSON: ' + e.message); }
  let Component;
  try { Component = new Function('DCLogic', ...Object.keys(SANDBOX), sm[2] + '\n;return typeof Component !== "undefined" ? Component : null;')(DCLogic, ...Object.values(SANDBOX)); }
  catch (e) { r.errors.push('logic does not parse: ' + e.message); report.push(r); failed = true; continue; }
  if (!Component) { r.errors.push('no class Component'); report.push(r); failed = true; continue; }

  const defaults = Object.fromEntries(Object.entries(props).filter(([k, v]) => !k.startsWith('$') && v && typeof v === 'object' && 'default' in v).map(([k, v]) => [k, v.default]));
  const variants = [{ label: 'defaults', props: { ...defaults } }];
  for (const [k, v] of Object.entries(props)) {
    if (v && v.editor === 'enum' && Array.isArray(v.options)) for (const o of v.options) if (o !== v.default) variants.push({ label: `${k}=${o}`, props: { ...defaults, [k]: o } });
    if (v && v.editor === 'boolean') variants.push({ label: `${k}=${!v.default}`, props: { ...defaults, [k]: !v.default } });
  }
  const holes = holesWithScopes(tpl);
  const everResolved = new Map(holes.map((h) => [h.path + '|' + h.scopes.map((s) => s.as).join(','), { ok: false, why: '' }]));
  for (const variant of variants) {
    r.states++;
    let inst;
    try { inst = new Component(variant.props); if (!inst.state) inst.state = {}; if (typeof inst.componentDidMount === 'function') inst.componentDidMount(); }
    catch (e) { r.errors.push(`${variant.label}: constructor threw: ${e.message}`); continue; }
    const render = (when) => { try { return inst.renderVals(); } catch (e) { r.errors.push(`${variant.label}: renderVals threw ${when}: ${e.message}`); return null; } };
    let vals = render('on first render');
    if (!vals) continue;
    for (const h of holes) {
      const key = h.path + '|' + h.scopes.map((s) => s.as).join(',');
      const res = resolve(h.path, vals, h.scopes);
      if (res.ok) everResolved.set(key, { ok: true }); else if (!everResolved.get(key).ok) everResolved.set(key, { ok: false, why: res.why });
    }
    for (const [name, fn] of handlersOf(vals)) {
      try { fn(fakeEvent()); } catch (e) { r.errors.push(`${variant.label}: handler ${name} threw: ${e.message}`); }
      const again = render(`after ${name}`);
      if (again) vals = again;
    }
  }
  for (const [key, st] of everResolved) if (!st.ok) r.unresolved.push(`${key.split('|')[0]} (${st.why})`);
  if (r.errors.length) failed = true;
  report.push(r);
}

if (asJson) console.log(JSON.stringify(report, null, 2));
else for (const r of report) {
  console.log(`${r.file}: ${r.states} state(s) checked, ${r.errors.length} error(s), ${r.unresolved.length} hole warning(s)`);
  for (const e of r.errors.slice(0, 12)) console.log(`  ERROR ${e}`);
  for (const u of r.unresolved.slice(0, 12)) console.log(`  WARN  hole ${u}`);
}
process.exit(failed ? 1 : 0);
