#!/usr/bin/env node
// Worst-case text contrast over a rendered glass surface.
//
// Usage (run from the user's project directory, by path):
//   node <plugin-root>/scripts/glass_contrast.mjs --url <url> --selector <css> [options]
//   node <plugin-root>/scripts/glass_contrast.mjs --url <url> [--selector <scope>] --text-selector <css> [options]
//
// <plugin-root> is the folder that holds this scripts/ folder. Relative output
// paths (--screenshot) resolve against the current working directory, and
// missing parent folders are created.
//
// Method:
//   1. Load the page in headless Chromium through Playwright (optional
//      dependency; this script never installs it or its browsers).
//   2. Read the text color from the element's computed style (or --text-color).
//   3. Make the text transparent with an injected style, so the screenshot
//      holds only what sits behind the glyphs: glass tint, blur, refraction,
//      rim light and the page backdrop. Text shadows and outlines stay,
//      because WCAG treats a halo around text as part of its background.
//   4. Screenshot the element and decode the PNG through a canvas
//      (getImageData) in a blank page, so no image library is needed.
//   5. Compute the contrast of the text color against every pixel and report
//      min, 5th percentile, median, and pass/fail at 4.5:1 and 3:1.
//
// Measure text, not containers. With --selector alone, one color (the matched
// element's own) is compared with every pixel of its box, including child
// controls that have their own fills and colors. --text-selector measures each
// matched text element over its own box with its own computed color and
// reports every element plus the worst one.
//
// The ratios follow WCAG 2.x 1.4.3
// (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, checked 2026-11-05).
// WCAG has no rule written for translucent surfaces. Judging the minimum over
// the rendered backdrop is an engineering inference from 1.4.3, not a
// conformance test. Real glyph anti-aliasing, sub-pixel rendering and font
// weight are excluded: the script measures the background the text sits on,
// not the drawn glyph edges. One run covers one scroll position and one moment
// of any animation; move the backdrop and run again for the worst case.
//
// Playwright is looked up in this order: the PLAYWRIGHT_MODULE environment
// variable (path to a playwright package folder), a normal import, the
// current working directory, the plugin root, then the global npm root.
//
// Exit codes: 0 measured (and --require met, if given), 1 --require not met
// (for --text-selector: by any measured element), 2 could not run (bad
// arguments, Playwright missing, page or selector error).

import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { realpathSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { contrastReport, isLargeText, parseColor, pixelContrasts } from './contrast-math.mjs';

const HELP = `Usage: node <plugin-root>/scripts/glass_contrast.mjs --url <url> --selector <css> [options]
       node <plugin-root>/scripts/glass_contrast.mjs --url <url> [--selector <scope>] --text-selector <css> [options]

Run it from your project directory. Relative --screenshot paths resolve against
the current directory; missing folders are created.

Measure text, not containers. --selector alone compares ONE color (the matched
element's own) with every pixel of its box, so a container that holds buttons
or icons with their own fills and colors reports a false result. Point
--selector at the element that carries the text, or use --text-selector.

Options:
  --url <url>             page to load (http, https or file URL)
  --selector <css>        the text element to measure (first match); with
                          --text-selector, the scope to search inside
  --text-selector <css>   measure every match (plain CSS, descendants of
                          --selector, or of the document when --selector is
                          omitted) over its own box with its own color; reports
                          each element and the worst. Example:
                          --selector 'nav.site' --text-selector 'nav.site a, nav.site span'
  --text-color auto|#hex  text color; auto reads each element's computed color (default auto)
  --hide-text             hide the text before capture (default)
  --keep-text             capture with the text visible (debugging only)
  --region element|text   measure the whole element box, or only the text line boxes
                          (default element). Use text for buttons and pills with
                          their own rounded fill: the box corners outside the fill
                          show the surface behind and would count as backdrop.
  --dpr <n>               device pixel ratio for the capture (default 1)
  --viewport <WxH>        viewport size in CSS pixels (default 1280x800)
  --color-scheme light|dark  emulated prefers-color-scheme (default light)
  --wait <ms>             settle time after load and after hiding text (default 300)
  --timeout <ms>          navigation and selector timeout (default 30000)
  --require none|auto|4.5|3  exit 1 when the minimum is below this ratio; with
                          --text-selector, when any element is below (default none)
  --screenshot <file.png> save the captured region for the review record; with
                          --text-selector, one file per element (<name>-1.png, ...)
  --json                  print a JSON report
  -h, --help              show this help

Playwright: found through PLAYWRIGHT_MODULE (path to a playwright package
folder), a normal import, the current directory, the plugin root, or the global
npm root. This script never installs Playwright or browsers.

Exit codes: 0 measured (and --require met), 1 --require not met, 2 could not run.`;

const SCRIPTS_DIR = path.dirname(fileURLToPath(import.meta.url));
const PLUGIN_ROOT = path.resolve(SCRIPTS_DIR, '..');
const PACKAGE_NAMES = ['playwright', 'playwright-core'];
const MAX_TEXT_ELEMENTS = 100;

let globalRootCache;
/** The global npm root from `npm root -g`, cached for the process; null when npm fails. */
export function globalNpmRoot() {
  if (globalRootCache !== undefined) return globalRootCache;
  globalRootCache = null;
  try {
    const win = process.platform === 'win32';
    const out = execFileSync(win ? 'npm.cmd' : 'npm', ['root', '-g'], {
      encoding: 'utf8',
      timeout: 10000,
      stdio: ['ignore', 'pipe', 'ignore'],
      shell: win,
      windowsHide: true,
    }).trim();
    if (out) globalRootCache = out;
  } catch { /* npm missing or failed: skip this route */ }
  return globalRootCache;
}

const requireFrom = (dir, name) => createRequire(path.join(dir, 'noop.js'))(name);

/**
 * Find Playwright without installing it. Routes, in order: PLAYWRIGHT_MODULE
 * (a playwright package folder), a normal import, createRequire from the
 * current directory, from the plugin root, then the global npm root.
 * Returns { module, source, tried } with module null when nothing loads.
 */
export async function resolvePlaywright({
  env = process.env,
  cwd = process.cwd(),
  pluginRoot = PLUGIN_ROOT,
  useImport = true,
  globalRoot = globalNpmRoot,
} = {}) {
  const tried = [];
  const attempt = (source, load) => {
    try {
      const mod = load();
      if (mod) return { module: mod.default ?? mod, source, tried };
    } catch (error) {
      tried.push({ source, error: String(error?.message ?? error).split('\n')[0] });
    }
    return null;
  };
  if (env.PLAYWRIGHT_MODULE) {
    const dir = path.resolve(cwd, env.PLAYWRIGHT_MODULE);
    const found = attempt(`PLAYWRIGHT_MODULE (${dir})`, () => createRequire(path.join(cwd, 'noop.js'))(dir));
    if (found) return found;
  }
  if (useImport) {
    for (const name of PACKAGE_NAMES) {
      try {
        const mod = await import(name);
        return { module: mod.default ?? mod, source: `import ${name}`, tried };
      } catch { /* try the next route */ }
    }
    tried.push({ source: 'import', error: 'not found' });
  }
  const roots = [
    ['current directory', cwd],
    ['plugin root', pluginRoot],
  ];
  for (const [label, dir] of roots) {
    for (const name of PACKAGE_NAMES) {
      const found = attempt(`${label} (${dir})`, () => requireFrom(dir, name));
      if (found) return found;
    }
  }
  const global = typeof globalRoot === 'function' ? globalRoot() : globalRoot;
  if (global) {
    for (const name of PACKAGE_NAMES) {
      const found = attempt(`global npm root (${global})`, () => requireFrom(global, name));
      if (found) return found;
    }
  } else {
    tried.push({ source: 'global npm root', error: 'npm root -g gave no folder' });
  }
  return { module: null, source: null, tried };
}

/** Resolve Playwright without installing it; the module or null. See resolvePlaywright. */
export async function loadPlaywright(options) {
  return (await resolvePlaywright(options)).module;
}

/** The exit 2 message when Playwright cannot be found. */
export function playwrightMissingMessage(tool, browsers = 'chromium') {
  return [
    `${tool}: Playwright is not available. This script never installs Playwright or browsers.`,
    `Searched: PLAYWRIGHT_MODULE, a normal import, the current directory (${process.cwd()}), the plugin root (${PLUGIN_ROOT}), and the global npm root.`,
    "Do not add Playwright to the user's project without asking. Either:",
    '  1. install it in a scratch folder:  npm i playwright --prefix <scratch>',
    '     then run with PLAYWRIGHT_MODULE=<scratch>/node_modules/playwright',
    '  2. or install it globally:          npm i -g playwright',
    `A browser build is needed too (ask first): npx playwright install ${browsers}`,
    '',
  ].join('\n');
}

/** Write a file at a path resolved against the current directory, creating parent folders. */
export async function writeOutput(file, data) {
  const full = path.resolve(file);
  await mkdir(path.dirname(full), { recursive: true });
  await writeFile(full, data);
  return full;
}

/** <name>-<n>.png for per-element screenshots. */
export function numberedPath(file, n) {
  const ext = path.extname(file);
  return `${ext ? file.slice(0, -ext.length) : file}-${n}${ext || '.png'}`;
}

export function parseCliArgs(argv) {
  const { values } = parseArgs({
    args: argv,
    options: {
      url: { type: 'string' },
      selector: { type: 'string' },
      'text-selector': { type: 'string' },
      'text-color': { type: 'string', default: 'auto' },
      'hide-text': { type: 'boolean', default: false },
      'keep-text': { type: 'boolean', default: false },
      region: { type: 'string', default: 'element' },
      dpr: { type: 'string', default: '1' },
      viewport: { type: 'string', default: '1280x800' },
      'color-scheme': { type: 'string', default: 'light' },
      wait: { type: 'string', default: '300' },
      timeout: { type: 'string', default: '30000' },
      require: { type: 'string', default: 'none' },
      screenshot: { type: 'string' },
      json: { type: 'boolean', default: false },
      help: { type: 'boolean', short: 'h', default: false },
    },
    strict: true,
  });
  if (values.help) return { help: true };
  const problems = [];
  if (!values.url) problems.push('--url is required');
  if (!values.selector && !values['text-selector']) problems.push('--selector or --text-selector is required');
  if (values['text-selector'] !== undefined && !values['text-selector'].trim()) problems.push('--text-selector must not be empty');
  if (values['hide-text'] && values['keep-text']) problems.push('--hide-text and --keep-text conflict');
  const dpr = Number(values.dpr);
  if (!(dpr > 0 && dpr <= 4)) problems.push('--dpr must be a number in (0, 4]');
  const viewport = /^(\d+)x(\d+)$/.exec(values.viewport);
  if (!viewport) problems.push('--viewport must look like 1280x800');
  if (!['element', 'text'].includes(values.region)) problems.push('--region must be element or text');
  if (!['light', 'dark'].includes(values['color-scheme'])) problems.push('--color-scheme must be light or dark');
  if (!['none', 'auto', '4.5', '3'].includes(values.require)) problems.push('--require must be none, auto, 4.5 or 3');
  const wait = Number(values.wait);
  const timeout = Number(values.timeout);
  if (!(wait >= 0) || !(timeout > 0)) problems.push('--wait and --timeout must be non-negative numbers');
  let textColor = null;
  if (values['text-color'] !== 'auto') {
    try {
      textColor = parseColor(values['text-color']);
    } catch (error) {
      problems.push(error.message);
    }
  }
  if (problems.length) throw new UsageError(problems.join('; '));
  return {
    url: values.url,
    selector: values.selector ?? null,
    textSelector: values['text-selector'] ?? null,
    textColor,
    textColorArg: values['text-color'],
    hideText: !values['keep-text'],
    region: values.region,
    dpr,
    viewport: { width: Number(viewport[1]), height: Number(viewport[2]) },
    colorScheme: values['color-scheme'],
    wait,
    timeout,
    require: values.require,
    screenshot: values.screenshot,
    json: values.json,
  };
}

class UsageError extends Error {}

// Runs in a blank page: PNG (base64) -> RGBA bytes (base64) through a canvas.
async function decodeInPage(pngBase64) {
  const img = new Image();
  img.src = `data:image/png;base64,${pngBase64}`;
  await img.decode();
  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext('2d', { willReadFrequently: true, colorSpace: 'srgb' });
  ctx.drawImage(img, 0, 0);
  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < data.length; i += chunk) binary += String.fromCharCode.apply(null, data.subarray(i, i + chunk));
  return { width: canvas.width, height: canvas.height, rgba: btoa(binary) };
}

// Runs in the target page: text line boxes relative to the element's border box.
function textRectsInPage(el) {
  const origin = el.getBoundingClientRect();
  const rects = [];
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (!node.textContent.trim()) continue;
    range.selectNodeContents(node);
    for (const r of range.getClientRects()) {
      if (r.width > 0 && r.height > 0) rects.push({ x: r.left - origin.left, y: r.top - origin.top, w: r.width, h: r.height });
    }
  }
  return rects;
}

function maskFromRects(width, height, rects, scaleX, scaleY) {
  const mask = new Uint8Array(width * height);
  for (const r of rects) {
    const x0 = Math.max(0, Math.floor(r.x * scaleX));
    const y0 = Math.max(0, Math.floor(r.y * scaleY));
    const x1 = Math.min(width, Math.ceil((r.x + r.w) * scaleX));
    const y1 = Math.min(height, Math.ceil((r.y + r.h) * scaleY));
    for (let y = y0; y < y1; y += 1) mask.fill(1, y * width + x0, y * width + x1);
  }
  return mask;
}

const cssColor = ({ r, g, b, a }) => `rgba(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)}, ${+a.toFixed(3)})`;

// Runs in the target page: what the measurement needs from one text element.
function elementInfoInPage(el) {
  const cs = getComputedStyle(el);
  const own = cs.color;
  let mixedColors = 0;
  for (const child of el.querySelectorAll('*')) {
    const ccs = getComputedStyle(child);
    const hasText = [...child.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (hasText && ccs.color !== own) mixedColors += 1;
  }
  const id = el.id ? `#${el.id}` : '';
  const cls = typeof el.className === 'string' && el.className.trim() ? `.${el.className.trim().split(/\s+/).slice(0, 3).join('.')}` : '';
  return {
    color: own,
    fontSize: parseFloat(cs.fontSize),
    fontWeight: cs.fontWeight,
    text: el.textContent.replace(/\s+/g, ' ').trim().slice(0, 80),
    label: `${el.tagName.toLowerCase()}${id}${cls}`,
    mixedColors,
  };
}

// Runs in the target page: visible text elements matching textSelector inside scope.
// Element.querySelectorAll matches the selector against the whole document and
// keeps descendants, so 'nav.site a' works with the scope nav.site.
function textElementsInPage(scope, textSelector) {
  return [...scope.querySelectorAll(textSelector)].filter((el) => {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return r.width >= 1 && r.height >= 1 && cs.visibility !== 'hidden' && cs.display !== 'none' && el.textContent.trim();
  });
}

async function settle(page, wait) {
  await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))));
  if (wait) await page.waitForTimeout(wait);
}

async function hideText(page, selector) {
  const sel = `:is(${selector})`;
  await page.addStyleTag({
    content: `${sel}, ${sel} * { color: transparent !important; -webkit-text-fill-color: transparent !important; caret-color: transparent !important; text-decoration-color: transparent !important; }`,
  });
}

/** Capture one element (locator or element handle) and measure its pixels against one text color. */
async function measureElement(handle, decoder, options, textColor, label) {
  await handle.scrollIntoViewIfNeeded();
  const box = await handle.boundingBox();
  if (!box || box.width < 1 || box.height < 1) throw new Error(`element ${label} has no visible box`);
  const rects = options.region === 'text' ? await handle.evaluate(textRectsInPage) : null;
  const png = await handle.screenshot({ type: 'png' });
  const decoded = await decoder.evaluate(decodeInPage, png.toString('base64'));
  const rgba = new Uint8Array(Buffer.from(decoded.rgba, 'base64'));
  let mask;
  if (rects) {
    if (!rects.length) throw new Error(`--region text found no text inside ${label}`);
    mask = maskFromRects(decoded.width, decoded.height, rects, decoded.width / box.width, decoded.height / box.height);
  }
  const ratios = pixelContrasts(rgba, textColor, { mask });
  if (!ratios.length) throw new Error(`no pixels measured for ${label}`);
  return {
    png,
    box: { x: box.x, y: box.y, width: box.width, height: box.height },
    capture: { imageWidth: decoded.width, imageHeight: decoded.height, pixelsMeasured: ratios.length },
    contrast: contrastReport(ratios, [4.5, 3]),
  };
}

/** The ratio an element must meet: the --require number, or its WCAG threshold for none and auto. */
export function requiredRatio(require, wcagThreshold) {
  return require === 'none' || require === 'auto' ? wcagThreshold : Number(require);
}

const METHOD =
  'Per-pixel WCAG 2.x contrast of the text color against the rendered element with its text hidden. ' +
  'Pass is judged at the minimum. Inference: WCAG has no translucency rule; glyph anti-aliasing is excluded.';

export async function measure(options, playwright) {
  const browser = await playwright.chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({
      viewport: options.viewport,
      deviceScaleFactor: options.dpr,
      colorScheme: options.colorScheme,
    });
    const page = await context.newPage();
    await page.goto(options.url, { waitUntil: 'load', timeout: options.timeout });
    const decoder = await context.newPage();
    if (options.textSelector) return await measureTextElements(page, decoder, options);

    const all = page.locator(options.selector);
    const target = all.first();
    await target.waitFor({ state: 'visible', timeout: options.timeout });
    const matched = await all.count();
    const info = await target.evaluate(elementInfoInPage);
    const textColor = options.textColor ?? parseColor(info.color);
    if (textColor.a === 0) throw new Error('text color is fully transparent; pass --text-color #hex');
    if (options.hideText) await hideText(page, options.selector);
    await settle(page, options.wait);
    const result = await measureElement(target, decoder, options, textColor, options.selector);
    let screenshot;
    if (options.screenshot) screenshot = await writeOutput(options.screenshot, result.png);
    const largeText = isLargeText(info.fontSize, info.fontWeight);
    const warnings = [];
    if (info.mixedColors && !options.textColor) {
      warnings.push(
        `${info.mixedColors} descendant element(s) carry text in a different color than ${options.selector}; ` +
          'one color was measured against the whole box. Measure the text elements with --text-selector.',
      );
    }
    return {
      url: options.url,
      selector: options.selector,
      matched,
      sampleText: info.text,
      textColor: { source: options.textColor ? 'argument' : 'computed style', css: cssColor(textColor) },
      font: { sizePx: info.fontSize, weight: info.fontWeight, largeText },
      wcagThreshold: largeText ? 3 : 4.5,
      capture: {
        region: options.region,
        textHidden: options.hideText,
        dpr: options.dpr,
        colorScheme: options.colorScheme,
        ...result.capture,
        ...(screenshot ? { screenshot } : {}),
      },
      contrast: result.contrast,
      warnings,
      method: METHOD,
    };
  } finally {
    await browser.close();
  }
}

async function measureTextElements(page, decoder, options) {
  // Without --selector the scope is the root element, so every match in the document counts.
  const scope = page.locator(options.selector ?? ':root').first();
  await scope.waitFor({ state: options.selector ? 'visible' : 'attached', timeout: options.timeout });
  const listHandle = await scope.evaluateHandle(textElementsInPage, options.textSelector);
  const handles = [];
  for (const prop of (await listHandle.getProperties()).values()) {
    const el = prop.asElement();
    if (el) handles.push(el);
  }
  if (!handles.length) {
    throw new Error(`--text-selector ${options.textSelector} matched no visible text${options.selector ? ` inside ${options.selector}` : ''}`);
  }
  const measuredHandles = handles.slice(0, MAX_TEXT_ELEMENTS);
  const infos = [];
  for (const handle of measuredHandles) infos.push(await handle.evaluate(elementInfoInPage));
  if (options.hideText) await hideText(page, options.textSelector);
  await settle(page, options.wait);

  const elements = [];
  for (const [i, handle] of measuredHandles.entries()) {
    const info = infos[i];
    const index = i + 1;
    const label = `#${index} ${info.label}`;
    const textColor = options.textColor ?? parseColor(info.color);
    if (textColor.a === 0) throw new Error(`text color of ${label} is fully transparent; pass --text-color #hex`);
    const result = await measureElement(handle, decoder, options, textColor, label);
    let screenshot;
    if (options.screenshot) screenshot = await writeOutput(numberedPath(options.screenshot, index), result.png);
    const largeText = isLargeText(info.fontSize, info.fontWeight);
    const wcagThreshold = largeText ? 3 : 4.5;
    const required = requiredRatio(options.require, wcagThreshold);
    elements.push({
      index,
      element: info.label,
      sampleText: info.text,
      textColor: { source: options.textColor ? 'argument' : 'computed style', css: cssColor(textColor) },
      font: { sizePx: info.fontSize, weight: info.fontWeight, largeText },
      wcagThreshold,
      required,
      pass: result.contrast.min >= required,
      box: result.box,
      capture: { ...result.capture, ...(screenshot ? { screenshot } : {}) },
      contrast: result.contrast,
      ...(info.mixedColors && !options.textColor
        ? { warning: `${info.mixedColors} descendant element(s) carry text in another color; narrow --text-selector` }
        : {}),
    });
  }
  const worstElement = elements.reduce((w, e) => (e.contrast.min / e.required < w.contrast.min / w.required ? e : w));
  return {
    url: options.url,
    selector: options.selector,
    textSelector: options.textSelector,
    matched: handles.length,
    measured: elements.length,
    truncated: handles.length > elements.length,
    capture: {
      region: options.region,
      textHidden: options.hideText,
      dpr: options.dpr,
      colorScheme: options.colorScheme,
    },
    elements,
    worst: {
      index: worstElement.index,
      element: worstElement.element,
      sampleText: worstElement.sampleText,
      min: worstElement.contrast.min,
      required: worstElement.required,
      pass: worstElement.pass,
    },
    // The worst element's numbers, so callers that read one report keep working.
    contrast: worstElement.contrast,
    wcagThreshold: worstElement.wcagThreshold,
    pass: elements.every((e) => e.pass),
    method: `${METHOD} Each text element is measured over its own box with its own computed color.`,
  };
}

/** Whether a report meets --require (always true for none). */
export function meetsRequirement(report, require) {
  if (require === 'none') return true;
  if (report.elements) return report.elements.every((e) => e.contrast.min >= requiredRatio(require, e.wcagThreshold));
  return report.contrast.min >= requiredRatio(require, report.wcagThreshold);
}

const fmt = (n) => n.toFixed(2);

function formatText(report) {
  if (report.elements) return formatTextElements(report);
  const c = report.contrast;
  const line = (t) => {
    const r = c.thresholds[t];
    return `  ${t}:1  ${r.passAtMin ? 'PASS' : 'FAIL'} at min, ${(r.fractionBelow * 100).toFixed(1)}% of pixels below`;
  };
  return [
    `${report.url}  ${report.selector}${report.matched > 1 ? `  (first of ${report.matched} matches)` : ''}`,
    `text color ${report.textColor.css} (${report.textColor.source}); font ${report.font.sizePx}px weight ${report.font.weight}` +
      `${report.font.largeText ? ' (large text, 3:1 applies)' : ' (normal text, 4.5:1 applies)'}`,
    `pixels ${report.capture.pixelsMeasured} (${report.capture.region} region, dpr ${report.capture.dpr})`,
    `contrast min ${fmt(c.min)}  p5 ${fmt(c.p5)}  median ${fmt(c.median)}  max ${fmt(c.max)}`,
    line('4.5'),
    line('3'),
    ...report.warnings.map((w) => `warning: ${w}`),
    'note: inference from WCAG 1.4.3; glyph anti-aliasing excluded; one scroll position and frame only.',
  ].join('\n');
}

function formatTextElements(report) {
  const out = [
    `${report.url}  ${report.selector ? `${report.selector} >> ` : ''}${report.textSelector}  (${report.measured} measured` +
      `${report.truncated ? ` of ${report.matched}; capped at ${MAX_TEXT_ELEMENTS}` : ''})`,
  ];
  for (const e of report.elements) {
    const c = e.contrast;
    out.push(
      `  ${e.pass ? 'PASS' : 'FAIL'} #${e.index} ${e.element} "${e.sampleText.slice(0, 32)}"  ${e.textColor.css}  ` +
        `${e.font.sizePx}px ${e.font.weight}  min ${fmt(c.min)} p5 ${fmt(c.p5)} median ${fmt(c.median)}  needs ${e.required}:1`,
    );
    if (e.warning) out.push(`       warning: ${e.warning}`);
  }
  const w = report.worst;
  out.push(
    `worst #${w.index} ${w.element} "${w.sampleText.slice(0, 32)}": min ${fmt(w.min)} against ${w.required}:1, ${w.pass ? 'PASS' : 'FAIL'}`,
    'note: inference from WCAG 1.4.3; glyph anti-aliasing excluded; one scroll position and frame only.',
  );
  return out.join('\n');
}

export async function main(argv = process.argv.slice(2)) {
  let options;
  try {
    options = parseCliArgs(argv);
  } catch (error) {
    process.stderr.write(`glass_contrast: ${error.message}\n\n${HELP}\n`);
    return 2;
  }
  if (options.help) {
    process.stdout.write(`${HELP}\n`);
    return 0;
  }
  const found = await resolvePlaywright();
  const playwright = found.module;
  if (!playwright?.chromium) {
    process.stderr.write(playwrightMissingMessage('glass_contrast', 'chromium'));
    return 2;
  }
  const badOverride = found.tried.find((t) => t.source.startsWith('PLAYWRIGHT_MODULE'));
  if (badOverride) process.stderr.write(`glass_contrast: warning: ${badOverride.source} did not load (${badOverride.error}); used ${found.source}\n`);
  let report;
  try {
    report = await measure(options, playwright);
  } catch (error) {
    process.stderr.write(`glass_contrast: ${error.message.split('\n')[0]}\n`);
    return 2;
  }
  process.stdout.write(`${options.json ? JSON.stringify(report, null, 2) : formatText(report)}\n`);
  return meetsRequirement(report, options.require) ? 0 : 1;
}

const invokedDirectly = (() => {
  try {
    return process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
})();

if (invokedDirectly) {
  main().then((code) => {
    process.exitCode = code;
  });
}
