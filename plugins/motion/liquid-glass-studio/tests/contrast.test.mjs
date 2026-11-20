// Tests for scripts/contrast-math.mjs and scripts/glass_contrast.mjs.
// Run: node --test tests/contrast.test.mjs
// The end-to-end tests run only when Playwright and a Chromium build are
// already installed; otherwise they are skipped with a reason.
import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  compositeOver,
  contrastRatio,
  contrastReport,
  glassOver,
  isLargeText,
  minOf,
  parseColor,
  percentile,
  pixelContrasts,
  relativeLuminance,
  summarize,
} from '../scripts/contrast-math.mjs';
import {
  loadPlaywright,
  meetsRequirement,
  numberedPath,
  parseCliArgs,
  playwrightMissingMessage,
  requiredRatio,
  resolvePlaywright,
} from '../scripts/glass_contrast.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT = path.join(here, '..', 'scripts', 'glass_contrast.mjs');
const close = (actual, expected, tolerance, label) =>
  assert.ok(Math.abs(actual - expected) <= tolerance, `${label ?? ''} expected ${expected} +/- ${tolerance}, got ${actual}`);

describe('color parsing', () => {
  test('hex forms', () => {
    assert.deepEqual(parseColor('#fff'), { r: 255, g: 255, b: 255, a: 1 });
    assert.deepEqual(parseColor('#00000080'), { r: 0, g: 0, b: 0, a: 128 / 255 });
    assert.deepEqual(parseColor('#777777'), { r: 119, g: 119, b: 119, a: 1 });
  });
  test('computed style forms', () => {
    assert.deepEqual(parseColor('rgb(17, 17, 19)'), { r: 17, g: 17, b: 19, a: 1 });
    assert.deepEqual(parseColor('rgba(0, 0, 0, 0.5)'), { r: 0, g: 0, b: 0, a: 0.5 });
    assert.deepEqual(parseColor('rgb(255 0 0 / 50%)'), { r: 255, g: 0, b: 0, a: 0.5 });
    assert.deepEqual(parseColor('color(srgb 1 0 0)'), { r: 255, g: 0, b: 0, a: 1 });
    assert.equal(parseColor('transparent').a, 0);
  });
  test('unsupported forms throw', () => {
    assert.throws(() => parseColor('oklch(0.5 0.1 200)'), /Unsupported color/);
    assert.throws(() => parseColor('#12'), /Unsupported color/);
  });
});

describe('WCAG luminance and contrast', () => {
  test('black on white is 21:1', () => {
    assert.equal(relativeLuminance(parseColor('#000')), 0);
    close(relativeLuminance(parseColor('#fff')), 1, 1e-12);
    close(contrastRatio('#000000', '#ffffff'), 21, 1e-9);
    close(contrastRatio('#ffffff', '#000000'), 21, 1e-9, 'order independent');
  });
  test('#777 on white is about 4.48 and fails 4.5', () => {
    const ratio = contrastRatio('#777777', '#ffffff');
    close(ratio, 4.48, 0.01);
    assert.ok(ratio < 4.5);
  });
  test('other reference pairs', () => {
    close(contrastRatio('#767676', '#ffffff'), 4.54, 0.01, '#767676 is the lightest gray that passes');
    close(contrastRatio('#959595', '#ffffff'), 2.99, 0.01);
    close(contrastRatio('#ff0000', '#ffffff'), 4.0, 0.01);
    assert.equal(contrastRatio('#123456', '#123456'), 1);
  });
  test('translucent text is composited over the background', () => {
    close(contrastRatio({ r: 0, g: 0, b: 0, a: 0.5 }, '#ffffff'), contrastRatio('rgb(127.5,127.5,127.5)', '#fff'), 1e-9);
    assert.throws(() => contrastRatio('#000', 'rgba(0,0,0,0.5)'), /opaque background/);
  });
});

describe('compositing', () => {
  test('half black over white is mid gray', () => {
    const out = compositeOver({ r: 0, g: 0, b: 0, a: 0.5 }, { r: 255, g: 255, b: 255, a: 1 });
    assert.deepEqual(out, { r: 127.5, g: 127.5, b: 127.5, a: 1 });
  });
  test('opaque top wins, transparent top is a no-op', () => {
    const bg = { r: 10, g: 20, b: 30, a: 1 };
    assert.deepEqual(compositeOver({ r: 200, g: 100, b: 0, a: 1 }, bg), { r: 200, g: 100, b: 0, a: 1 });
    assert.deepEqual(compositeOver({ r: 200, g: 100, b: 0, a: 0 }, bg), bg);
  });
  test('translucent over translucent accumulates alpha', () => {
    const out = compositeOver({ r: 255, g: 255, b: 255, a: 0.5 }, { r: 0, g: 0, b: 0, a: 0.5 });
    close(out.a, 0.75, 1e-12);
    close(out.r, 170, 1e-9);
  });
  test('glassOver stacks tint layers bottom to top', () => {
    const black = { r: 0, g: 0, b: 0, a: 1 };
    const out = glassOver(black, { r: 255, g: 255, b: 255, a: 0.6 });
    close(out.r, 153, 1e-9);
    close(contrastRatio('#000', out), 7.37, 0.02, 'white 60% tint over black, black text');
  });
});

describe('statistics', () => {
  test('percentile interpolates between ranks', () => {
    const values = [5, 1, 4, 2, 3];
    assert.equal(percentile(values, 0), 1);
    assert.equal(percentile(values, 50), 3);
    assert.equal(percentile(values, 100), 5);
    close(percentile(values, 5), 1.2, 1e-12);
    assert.deepEqual(values, [5, 1, 4, 2, 3], 'input not mutated');
    assert.ok(Number.isNaN(percentile([], 50)));
  });
  test('minOf and summarize', () => {
    assert.equal(minOf(Float64Array.from([3, -1, 2])), -1);
    assert.deepEqual(summarize([4, 2, 8, 6]), { count: 4, min: 2, p5: 2.3, median: 5, max: 8 });
  });
});

describe('pixel sets', () => {
  const pixels = (list) => Uint8ClampedArray.from(list.flat());
  test('per-pixel contrast with mask and matte', () => {
    const data = pixels([[255, 255, 255, 255], [0, 0, 0, 255], [0, 0, 0, 0]]);
    const all = pixelContrasts(data, '#000');
    assert.equal(all.length, 3);
    close(all[0], 21, 1e-9);
    close(all[1], 1, 1e-9);
    close(all[2], 21, 1e-9, 'transparent pixel composited over white matte');
    const masked = pixelContrasts(data, '#000', { mask: Uint8Array.from([0, 1, 0]) });
    assert.deepEqual(Array.from(masked), [1]);
  });
  test('report judges pass at the minimum and counts the failing fraction', () => {
    const data = pixels([[255, 255, 255, 255], [255, 255, 255, 255], [255, 255, 255, 255], [119, 119, 119, 255]]);
    const report = contrastReport(pixelContrasts(data, '#000'), [4.5, 3]);
    assert.equal(report.count, 4);
    assert.equal(report.thresholds['4.5'].passAtMin, true);
    const gray = contrastReport(pixelContrasts(pixels([[255, 255, 255, 255], [119, 119, 119, 255]]), '#fff'));
    assert.equal(gray.thresholds['4.5'].passAtMin, false);
    assert.equal(gray.thresholds['4.5'].fractionBelow, 1);
    assert.equal(gray.thresholds['3'].passAtMin, false, 'white on white is 1:1');
    assert.equal(gray.thresholds['3'].fractionBelow, 0.5);
  });
  test('large text rule', () => {
    assert.equal(isLargeText(24, '400'), true);
    assert.equal(isLargeText(19, '700'), true);
    assert.equal(isLargeText(19, '400'), false);
    assert.equal(isLargeText(16, 'bold'), false);
  });
});

describe('CLI arguments', () => {
  test('defaults and validation', () => {
    const opts = parseCliArgs(['--url', 'http://x', '--selector', '.g']);
    assert.equal(opts.hideText, true);
    assert.equal(opts.dpr, 1);
    assert.equal(opts.textColor, null);
    assert.deepEqual(opts.viewport, { width: 1280, height: 800 });
    assert.deepEqual(parseCliArgs(['--url', 'u', '--selector', 's', '--text-color', '#fff']).textColor, { r: 255, g: 255, b: 255, a: 1 });
    assert.throws(() => parseCliArgs(['--selector', 's']), /--url is required/);
    assert.throws(() => parseCliArgs(['--url', 'u', '--selector', 's', '--dpr', '0']), /--dpr/);
    assert.throws(() => parseCliArgs(['--url', 'u', '--selector', 's', '--hide-text', '--keep-text']), /conflict/);
    assert.throws(() => parseCliArgs(['--url', 'u', '--selector', 's', '--bogus']));
  });
  test('--text-selector makes --selector optional', () => {
    const scoped = parseCliArgs(['--url', 'u', '--selector', 'nav', '--text-selector', 'nav a']);
    assert.equal(scoped.selector, 'nav');
    assert.equal(scoped.textSelector, 'nav a');
    const whole = parseCliArgs(['--url', 'u', '--text-selector', 'a']);
    assert.equal(whole.selector, null);
    assert.throws(() => parseCliArgs(['--url', 'u']), /--selector or --text-selector is required/);
    assert.throws(() => parseCliArgs(['--url', 'u', '--text-selector', ' ']), /must not be empty/);
  });
  test('per-element requirement and numbered screenshot names', () => {
    assert.equal(requiredRatio('auto', 3), 3);
    assert.equal(requiredRatio('none', 4.5), 4.5);
    assert.equal(requiredRatio('3', 4.5), 3);
    const report = { elements: [{ wcagThreshold: 4.5, contrast: { min: 5 } }, { wcagThreshold: 4.5, contrast: { min: 4.4 } }] };
    assert.equal(meetsRequirement(report, 'auto'), false, 'one element below its threshold fails the run');
    assert.equal(meetsRequirement(report, '3'), true);
    assert.equal(meetsRequirement(report, 'none'), true);
    assert.equal(meetsRequirement({ wcagThreshold: 3, contrast: { min: 3.2 } }, 'auto'), true);
    assert.equal(numberedPath('out/shot.png', 2), 'out/shot-2.png');
    assert.equal(numberedPath('shot', 1), 'shot-1.png');
  });
});

// ---------------------------------------------------------------------------
// Playwright resolution (no browser needed: stub packages).
// ---------------------------------------------------------------------------

function stubPackage(dir, marker) {
  mkdirSync(dir, { recursive: true });
  writeFileSync(path.join(dir, 'package.json'), JSON.stringify({ name: 'playwright', version: '0.0.0-stub', main: 'index.js' }));
  writeFileSync(
    path.join(dir, 'index.js'),
    `module.exports = { marker: ${JSON.stringify(marker)}, chromium: { launch: async () => { throw new Error('stub launch: ${marker}'); } } };\n`,
  );
  return dir;
}

describe('Playwright resolution', () => {
  let scratch;
  before(() => {
    scratch = mkdtempSync(path.join(tmpdir(), 'lgs-pw-'));
  });
  after(() => {
    if (scratch && existsSync(scratch)) rmSync(scratch, { recursive: true, force: true });
  });

  test('PLAYWRIGHT_MODULE wins over every other route', async () => {
    const dir = stubPackage(path.join(scratch, 'override', 'node_modules', 'playwright'), 'override');
    const found = await resolvePlaywright({ env: { PLAYWRIGHT_MODULE: dir }, cwd: scratch, globalRoot: null });
    assert.equal(found.module.marker, 'override');
    assert.match(found.source, /^PLAYWRIGHT_MODULE/);
    const relative = await resolvePlaywright({ env: { PLAYWRIGHT_MODULE: 'override/node_modules/playwright' }, cwd: scratch, globalRoot: null });
    assert.equal(relative.module.marker, 'override', 'a relative PLAYWRIGHT_MODULE resolves against the current directory');
  });

  test('a project install in the current directory is found', async () => {
    const project = path.join(scratch, 'project');
    stubPackage(path.join(project, 'node_modules', 'playwright'), 'project');
    const found = await resolvePlaywright({ env: {}, cwd: project, useImport: false, globalRoot: null });
    assert.equal(found.module.marker, 'project');
    assert.match(found.source, /^current directory/);
  });

  test('a broken PLAYWRIGHT_MODULE is recorded and the next route is used', async () => {
    const project = path.join(scratch, 'project2');
    stubPackage(path.join(project, 'node_modules', 'playwright'), 'project2');
    const found = await resolvePlaywright({
      env: { PLAYWRIGHT_MODULE: path.join(scratch, 'missing') },
      cwd: project,
      useImport: false,
      globalRoot: null,
    });
    assert.equal(found.module.marker, 'project2');
    assert.ok(found.tried.some((t) => t.source.startsWith('PLAYWRIGHT_MODULE')));
  });

  test('the CLI loads PLAYWRIGHT_MODULE (stub launch error, exit 2)', async () => {
    const dir = stubPackage(path.join(scratch, 'cli', 'playwright'), 'cli-stub');
    const { code, stderr } = await run(['--url', 'http://127.0.0.1:9/', '--selector', 'p'], {
      env: { ...process.env, PLAYWRIGHT_MODULE: dir },
    });
    assert.equal(code, 2);
    assert.match(stderr, /stub launch: cli-stub/);
  });

  test('the missing message says not to touch the project and how to provide it', async (t) => {
    const message = playwrightMissingMessage('glass_contrast');
    assert.match(message, /Do not add Playwright to the user's project without asking/);
    assert.match(message, /npm i playwright --prefix <scratch>/);
    assert.match(message, /PLAYWRIGHT_MODULE=<scratch>\/node_modules\/playwright/);
    assert.match(message, /npm i -g playwright/);
    try {
      await import('playwright');
      return t.skip('playwright is importable next to the plugin, so the CLI cannot be made to miss it');
    } catch { /* expected */ }
    const empty = mkdtempSync(path.join(scratch, 'empty-'));
    const env = { ...process.env, PATH: '', NODE_PATH: '' };
    delete env.PLAYWRIGHT_MODULE;
    const { code, stderr } = await run(['--url', 'http://127.0.0.1:9/', '--selector', 'p'], { cwd: empty, env });
    if (code !== 2 || !/not available/.test(stderr)) return t.skip('Playwright was still found through another route');
    assert.match(stderr, /Do not add Playwright to the user's project without asking/);
  });
});

// ---------------------------------------------------------------------------
// End to end: a static page served by python http.server, measured in Chromium.
// ---------------------------------------------------------------------------

const PAGE = `<!doctype html>
<html><head><meta charset="utf-8"><title>contrast fixture</title>
<style>
  body { margin: 0; background: #fff; font: 16px/1.2 sans-serif; }
  .split { position: absolute; left: 0; top: 200px; width: 100%; height: 120px;
           background: linear-gradient(to right, #000 50%, #fff 50%); }
  .glass { position: absolute; padding: 8px; }
  #dark-tint { left: 20px; top: 20px; width: 200px; height: 60px; background: rgba(0, 0, 0, 0.5); color: #fff; }
  #light-tint { left: 540px; top: 220px; width: 200px; height: 60px; background: rgba(255, 255, 255, 0.6); color: #000; }
  /* A nav over a backdrop that is black on the left and white on the right:
     a white link sits on the black half, a gray label on the white half. */
  .nav-backdrop { position: absolute; left: 0; top: 400px; width: 600px; height: 60px;
                  background: linear-gradient(to right, #000 300px, #fff 300px); }
  nav.site { position: absolute; left: 0; top: 400px; width: 600px; height: 60px; color: #777; }
  nav.site a, nav.site span { position: absolute; top: 20px; width: 100px; height: 20px; display: block; text-decoration: none; }
  #home { left: 20px; color: #fff; }
  #label { left: 420px; }
</style></head>
<body>
  <div id="dark-tint" class="glass">Hello glass</div>
  <div class="split"></div>
  <div id="light-tint" class="glass">Over a split backdrop</div>
  <div class="nav-backdrop"></div>
  <nav class="site"><a id="home" href="#">Home</a><span id="label">Saturday</span></nav>
</body></html>`;

let skipReason = false;
let server;
let baseUrl;
let workdir;

function run(args, { cwd, env } = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [SCRIPT, ...args], { stdio: ['ignore', 'pipe', 'pipe'], cwd, env });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

describe('glass_contrast.mjs end to end', () => {
  before(async () => {
    const playwright = await loadPlaywright();
    if (!playwright?.chromium) {
      skipReason = 'Playwright is not installed';
      return;
    }
    try {
      const browser = await playwright.chromium.launch({ headless: true });
      await browser.close();
    } catch (error) {
      skipReason = `Chromium could not launch: ${error.message.split('\n')[0]}`;
      return;
    }
    workdir = mkdtempSync(path.join(tmpdir(), 'lgs-contrast-'));
    writeFileSync(path.join(workdir, 'index.html'), PAGE);
    server = spawn('python3', ['-u', '-m', 'http.server', '0', '--bind', '127.0.0.1', '--directory', workdir], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    const port = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('http.server did not report a port')), 10000);
      let buffer = '';
      server.stdout.on('data', (chunk) => {
        buffer += chunk;
        const match = buffer.match(/port (\d+)/);
        if (match) {
          clearTimeout(timer);
          resolve(Number(match[1]));
        }
      });
      server.on('exit', (code) => reject(new Error(`http.server exited with ${code}`)));
    }).catch((error) => {
      skipReason = `local server failed: ${error.message}`;
      return null;
    });
    if (port) baseUrl = `http://127.0.0.1:${port}/index.html`;
  });

  after(() => {
    if (server && server.exitCode === null) process.kill(server.pid); // only the server this test started
    if (workdir && existsSync(workdir)) rmSync(workdir, { recursive: true, force: true });
  });

  test('half black tint over white: white text measures about 4:1 with text hidden', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run(['--url', baseUrl, '--selector', '#dark-tint', '--json', '--wait', '0']);
    assert.equal(code, 0, stderr);
    const report = JSON.parse(stdout);
    assert.equal(report.textColor.source, 'computed style');
    assert.equal(report.textColor.css, 'rgba(255, 255, 255, 1)');
    assert.equal(report.capture.textHidden, true);
    close(report.contrast.min, 4.0, 0.08, 'min');
    close(report.contrast.max, 4.0, 0.08, 'max (uniform tint, glyphs hidden)');
    assert.equal(report.contrast.thresholds['4.5'].passAtMin, false);
    assert.equal(report.contrast.thresholds['3'].passAtMin, true);
    assert.equal(report.contrast.thresholds['4.5'].fractionBelow, 1);
  });

  test('keeping the text visible pulls the minimum toward 1:1 (glyphs vs themselves)', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run(['--url', baseUrl, '--selector', '#dark-tint', '--json', '--keep-text', '--wait', '0']);
    assert.equal(code, 0, stderr);
    assert.ok(JSON.parse(stdout).contrast.min < 1.5);
  });

  test('light tint over a split backdrop: min comes from the dark half', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run(['--url', baseUrl, '--selector', '#light-tint', '--json', '--dpr', '2', '--wait', '0']);
    assert.equal(code, 0, stderr);
    const report = JSON.parse(stdout);
    assert.equal(report.capture.imageWidth, 2 * 216, 'dpr 2 doubles the capture width (200px + padding)');
    close(report.contrast.min, 7.37, 0.15, 'white 60% over black');
    close(report.contrast.max, 21, 0.01, 'white 60% over white');
    assert.equal(report.contrast.thresholds['4.5'].passAtMin, true);
  });

  test('--require and --text-color drive the exit code; text region shrinks the sample', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const failing = await run(['--url', baseUrl, '--selector', '#dark-tint', '--require', 'auto', '--wait', '0']);
    assert.equal(failing.code, 1, failing.stderr);
    assert.match(failing.stdout, /4\.5:1 {2}FAIL at min/);
    const passing = await run(['--url', baseUrl, '--selector', '#dark-tint', '--text-color', '#000', '--require', '3', '--region', 'text', '--json', '--wait', '0']);
    assert.equal(passing.code, 0, passing.stderr);
    const report = JSON.parse(passing.stdout);
    assert.equal(report.textColor.source, 'argument');
    assert.ok(report.capture.pixelsMeasured < 200 * 60, 'text line boxes are smaller than the element');
  });

  test('missing selector is a usage error (exit 2)', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stderr } = await run(['--url', baseUrl, '--selector', '#nope', '--timeout', '1500', '--wait', '0']);
    assert.equal(code, 2);
    assert.match(stderr, /glass_contrast:/);
  });

  test('a container measured as one element gives a false result and a warning', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run(['--url', baseUrl, '--selector', 'nav.site', '--json', '--require', 'auto', '--wait', '0']);
    assert.equal(code, 1, stderr);
    const report = JSON.parse(stdout);
    assert.equal(report.textColor.css, 'rgba(119, 119, 119, 1)', 'the container color stands in for every text');
    assert.ok(report.contrast.min < 4.5);
    assert.equal(report.warnings.length, 1);
    assert.match(report.warnings[0], /--text-selector/);
  });

  test('--text-selector measures each text element with its own color over its own box', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run([
      '--url', baseUrl, '--selector', 'nav.site', '--text-selector', 'nav.site a, nav.site span', '--json', '--wait', '0',
    ]);
    assert.equal(code, 0, stderr);
    const report = JSON.parse(stdout);
    assert.equal(report.textSelector, 'nav.site a, nav.site span');
    assert.equal(report.measured, 2);
    const [home, label] = report.elements;
    assert.equal(home.element, 'a#home');
    assert.equal(home.textColor.css, 'rgba(255, 255, 255, 1)');
    close(home.contrast.min, 21, 0.01, 'white link over the black half');
    assert.equal(home.pass, true);
    assert.equal(label.element, 'span#label');
    assert.equal(label.textColor.css, 'rgba(119, 119, 119, 1)');
    close(label.contrast.min, 4.48, 0.01, '#777 over the white half');
    assert.equal(label.pass, false);
    assert.equal(report.worst.index, 2, 'the gray label is the worst element');
    assert.equal(report.worst.element, 'span#label');
    assert.equal(report.pass, false);
    close(report.contrast.min, 4.48, 0.01, 'top-level contrast is the worst element');
  });

  test('--text-selector exit codes follow every element; the document is the default scope', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const strict = await run(['--url', baseUrl, '--selector', 'nav.site', '--text-selector', 'nav.site a, nav.site span', '--require', 'auto', '--wait', '0']);
    assert.equal(strict.code, 1, strict.stderr);
    assert.match(strict.stdout, /FAIL #2 span#label/);
    assert.match(strict.stdout, /worst #2 span#label/);
    const loose = await run(['--url', baseUrl, '--selector', 'nav.site', '--text-selector', 'nav.site a, nav.site span', '--require', '3', '--wait', '0']);
    assert.equal(loose.code, 0, loose.stderr);
    const whole = await run(['--url', baseUrl, '--text-selector', '#home', '--json', '--require', 'auto', '--wait', '0']);
    assert.equal(whole.code, 0, whole.stderr);
    const report = JSON.parse(whole.stdout);
    assert.equal(report.selector, null);
    assert.equal(report.measured, 1);
    const none = await run(['--url', baseUrl, '--selector', 'nav.site', '--text-selector', 'nav.site h1', '--wait', '0', '--timeout', '3000']);
    assert.equal(none.code, 2);
    assert.match(none.stderr, /matched no visible text/);
  });

  test('--screenshot resolves against the current directory and creates folders', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const cwd = mkdtempSync(path.join(workdir, 'cwd-'));
    const single = await run(['--url', baseUrl, '--selector', '#dark-tint', '--screenshot', 'review/deep/dark.png', '--json', '--wait', '0'], { cwd });
    assert.equal(single.code, 0, single.stderr);
    const expected = path.join(cwd, 'review', 'deep', 'dark.png');
    assert.ok(existsSync(expected), 'screenshot written under the current directory');
    assert.equal(JSON.parse(single.stdout).capture.screenshot, expected);
    const many = await run([
      '--url', baseUrl, '--text-selector', 'nav.site a, nav.site span', '--screenshot', 'per/element/nav.png', '--wait', '0',
    ], { cwd });
    assert.equal(many.code, 0, many.stderr);
    for (const n of [1, 2]) assert.ok(existsSync(path.join(cwd, 'per', 'element', `nav-${n}.png`)), `element ${n} screenshot`);
  });
});
