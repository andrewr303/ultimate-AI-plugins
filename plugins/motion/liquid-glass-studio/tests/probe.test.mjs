// Tests for scripts/probe-math.mjs and scripts/glass_probe.mjs.
// Run: node --test tests/probe.test.mjs
// The end-to-end test runs only when Playwright and a Chromium build are
// already installed; otherwise it is skipped with a reason.
import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  analyzeBlur,
  analyzeRefraction,
  compareCaptures,
  compareTiers,
  cropToCommon,
  estimateShift,
  gradientEnergy,
  interior,
  judgeBlur,
  judgeRefraction,
  luma,
  meanAbsDiff,
  meanLuma,
  recommendTier,
} from '../scripts/probe-math.mjs';
import {
  FIXTURE_PATH,
  PLUGIN_ROOT,
  formatTable,
  parseCliArgs,
  resolveUnderRoot,
  startServer,
  strictFailure,
  targetUrl,
} from '../scripts/glass_probe.mjs';
import { loadPlaywright } from '../scripts/glass_contrast.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT = path.join(here, '..', 'scripts', 'glass_probe.mjs');

/* Synthetic images ------------------------------------------------------- */

// Bar widths from scripts/fixtures/probe.html (aperiodic, 3 to 15 px).
const BARS = [14, 14, 14, 6, 5, 13, 13, 12, 12, 9, 3, 8, 13, 8, 5, 15, 13, 7, 5, 3, 3, 10, 4, 15, 6, 8, 4, 7, 11, 4, 13, 6, 5];

function barcodeRow(width, scale = 1) {
  const row = new Uint8Array(width);
  let x = 0;
  let dark = true;
  let i = 0;
  while (x < width) {
    const w = BARS[i % BARS.length] * scale;
    row.fill(dark ? 0 : 255, x, Math.min(width, x + w));
    x += w;
    dark = !dark;
    i += 1;
  }
  return row;
}

function fromRow(row, height) {
  const width = row.length;
  const data = new Uint8Array(width * height * 4);
  for (let y = 0; y < height; y += 1) for (let x = 0; x < width; x += 1) {
    const i = (y * width + x) * 4;
    data[i] = data[i + 1] = data[i + 2] = row[x];
    data[i + 3] = 255;
  }
  return { width, height, data };
}

function barcode(width = 240, height = 48, scale = 1) {
  return fromRow(barcodeRow(width + 64 * scale, scale).subarray(0, width), height);
}

// test(x) = source(x + s): what feDisplacementMap does with red above 0.5.
function shifted(width, height, s, scale = 1) {
  const full = barcodeRow(width + 64 * scale, scale);
  const row = new Uint8Array(width);
  for (let x = 0; x < width; x += 1) row[x] = full[Math.min(full.length - 1, Math.max(0, x + s))];
  return fromRow(row, height);
}

function boxBlur(img, radius) {
  const { width, height } = img;
  const L = luma(img);
  const row = new Uint8Array(width);
  for (let x = 0; x < width; x += 1) {
    let sum = 0;
    let n = 0;
    for (let k = -radius; k <= radius; k += 1) {
      const xx = Math.min(width - 1, Math.max(0, x + k));
      sum += L[xx];
      n += 1;
    }
    row[x] = Math.round(sum / n);
  }
  return fromRow(row, height);
}

function flat(width, height, value) {
  return fromRow(new Uint8Array(width).fill(value), height);
}

function invert(img) {
  const data = img.data.map((v, i) => (i % 4 === 3 ? v : 255 - v));
  return { ...img, data };
}

/* Pure math -------------------------------------------------------------- */

describe('image measures', () => {
  test('interior trims margins and never inverts', () => {
    assert.deepEqual(interior({ width: 10, height: 6 }, 2), { x0: 2, y0: 2, x1: 8, y1: 4 });
    assert.deepEqual(interior({ width: 4, height: 4 }, 9), { x0: 4, y0: 4, x1: 4, y1: 4 });
  });
  test('meanAbsDiff is 0 for equal images and 255 for black vs white', () => {
    const a = barcode();
    assert.equal(meanAbsDiff(a, barcode()), 0);
    assert.equal(meanAbsDiff(flat(8, 8, 0), flat(8, 8, 255)), 255);
    assert.throws(() => meanAbsDiff(flat(8, 8, 0), flat(9, 8, 0)), /sizes differ/);
  });
  test('cropToCommon aligns a one-row size mismatch', () => {
    const [a, b] = cropToCommon(barcode(240, 49), barcode(240, 48));
    assert.equal(a.height, 48);
    assert.equal(b.height, 48);
    assert.equal(meanAbsDiff(a, b), 0);
  });
  test('gradient energy falls under blur; mean luma holds', () => {
    const sharp = barcode();
    const soft = boxBlur(sharp, 6);
    assert.ok(gradientEnergy(soft, { margin: 8 }) < 0.3 * gradientEnergy(sharp, { margin: 8 }));
    assert.ok(Math.abs(meanLuma(soft, { margin: 8 }) - meanLuma(sharp, { margin: 8 })) < 10);
  });
});

describe('shift estimation', () => {
  test('recovers positive and negative shifts on the aperiodic barcode', () => {
    const control = barcode();
    for (const s of [8, -5, 13]) {
      const est = estimateShift(shifted(240, 48, s), control, { maxShift: 24 });
      assert.equal(est.shift, s, `shift ${s}`);
      assert.equal(est.error, 0);
      assert.ok(est.errorAtZero > 50);
    }
  });
  test('identical images report shift 0', () => {
    const est = estimateShift(barcode(), barcode(), { maxShift: 24 });
    assert.deepEqual(est, { shift: 0, error: 0, errorAtZero: 0 });
  });
  test('rejects images too small for the search', () => {
    assert.throws(() => estimateShift(barcode(40, 4), barcode(40, 4), { maxShift: 24 }), /too small/);
  });
});

describe('refraction verdict', () => {
  const control = barcode();
  test('expected shift renders', () => {
    const r = analyzeRefraction(shifted(240, 48, 8), control, { expectedShiftCss: 8 });
    assert.equal(r.renders, true);
    assert.equal(r.status, 'renders');
    assert.equal(r.shiftCssPx, 8);
  });
  test('pane equal to the control is no-effect (filter ignored)', () => {
    const r = analyzeRefraction(barcode(), control, { expectedShiftCss: 8 });
    assert.equal(r.renders, false);
    assert.equal(r.status, 'no-effect');
  });
  test('blank or wrong-shift panes are wrong-output', () => {
    assert.equal(analyzeRefraction(flat(240, 48, 255), control).status, 'wrong-output');
    assert.equal(analyzeRefraction(flat(240, 48, 0), control).status, 'wrong-output');
    const wrong = analyzeRefraction(shifted(240, 48, 3), control, { expectedShiftCss: 8 });
    assert.equal(wrong.renders, false);
    assert.equal(wrong.status, 'wrong-output');
    assert.match(wrong.reason, /best shift 3 px/);
  });
  test('device pixel ratio 2 doubles the expected shift in image pixels', () => {
    const control2 = barcode(480, 48, 2);
    const r = analyzeRefraction(shifted(480, 48, 16, 2), control2, { expectedShiftCss: 8, dpr: 2 });
    assert.equal(r.renders, true);
    assert.equal(r.shiftPx, 16);
    assert.equal(r.shiftCssPx, 8);
  });
  test('judgeRefraction honours custom thresholds', () => {
    const input = { errorAtZero: 100, shift: 8, error: 30, expectedShift: 8 };
    assert.equal(judgeRefraction(input).renders, false, 'residual 30% is above the 25% default');
    assert.equal(judgeRefraction(input, { maxResidualRatio: 0.5 }).renders, true);
  });
});

describe('blur verdict', () => {
  const control = barcode();
  test('box blur renders', () => {
    const r = analyzeBlur(boxBlur(control, 6), control);
    assert.equal(r.renders, true);
    assert.ok(r.sharpnessRatio < 0.3);
  });
  test('unchanged pane is no-effect', () => {
    assert.equal(analyzeBlur(barcode(), control).status, 'no-effect');
  });
  test('blank pane moves brightness and is wrong-output', () => {
    const r = analyzeBlur(flat(240, 48, 255), control);
    assert.equal(r.status, 'wrong-output');
    assert.match(r.reason, /brightness/);
  });
  test('a changed but still sharp pane is wrong-output', () => {
    const r = analyzeBlur(invert(control), control);
    assert.equal(r.renders, false);
    assert.match(r.reason, /edges stayed sharp/);
  });
  test('judgeBlur thresholds', () => {
    assert.equal(judgeBlur({ meanAbsDiff: 20, sharpnessRatio: 0.59, meanShift: 0 }).renders, true);
    assert.equal(judgeBlur({ meanAbsDiff: 20, sharpnessRatio: 0.61, meanShift: 0 }).renders, false);
    assert.equal(judgeBlur({ meanAbsDiff: 3, sharpnessRatio: 0.1, meanShift: 0 }).status, 'no-effect');
  });
});

describe('tier decisions', () => {
  test('recommendTier follows what rendered', () => {
    assert.equal(recommendTier({ refraction: { renders: true }, blur: { renders: true } }).tier, 'refract');
    assert.equal(recommendTier({ refraction: { renders: false }, blur: { renders: true } }).tier, 'frost');
    assert.equal(recommendTier({ refraction: { renders: false }, blur: { renders: false } }).tier, 'solid');
    assert.equal(recommendTier({}).tier, 'solid');
  });
  test('compareTiers names over and under shoots', () => {
    assert.deepEqual(compareTiers('refract', 'refract'), { agree: true, direction: 'same' });
    assert.deepEqual(compareTiers('refract', 'frost'), { agree: false, direction: 'over' });
    assert.deepEqual(compareTiers('frost', 'refract'), { agree: false, direction: 'under' });
    assert.equal(compareTiers('glass', 'frost').agree, null);
  });
  test('compareCaptures flags size mismatch and similarity', () => {
    assert.equal(compareCaptures(barcode(), barcode(240, 40)).comparable, false);
    assert.deepEqual(compareCaptures(barcode(), barcode()), { comparable: true, meanAbsDiff: 0, similar: true });
    assert.equal(compareCaptures(barcode(), invert(barcode())).similar, false);
  });
});

/* CLI helpers ------------------------------------------------------------ */

describe('glass_probe.mjs arguments and helpers', () => {
  test('defaults probe all three engines', () => {
    const o = parseCliArgs([]);
    assert.deepEqual(o.browsers, ['chromium', 'firefox', 'webkit']);
    assert.equal(o.fixture, true);
    assert.equal(o.dpr, 1);
    assert.equal(o.root, PLUGIN_ROOT);
  });
  test('usage errors', () => {
    assert.throws(() => parseCliArgs(['--browsers', 'safari']), /unknown engine "safari"/);
    assert.throws(() => parseCliArgs(['--url', 'x.html']), /--url and --selector go together/);
    assert.throws(() => parseCliArgs(['--skip-fixture']), /--skip-fixture needs --url/);
    assert.throws(() => parseCliArgs(['--dpr', '0']), /--dpr/);
    assert.throws(() => parseCliArgs(['--bogus']), /Unknown option/);
    assert.deepEqual(parseCliArgs(['-h']), { help: true });
  });
  test('resolveUnderRoot blocks traversal', () => {
    const root = '/srv/site';
    assert.equal(resolveUnderRoot(root, '/scripts/a.html?x=1'), path.join(root, 'scripts/a.html'));
    assert.equal(resolveUnderRoot(root, '/../etc/passwd'), path.join(root, 'etc/passwd'));
    assert.equal(resolveUnderRoot(root, '/%2e%2e/%2e%2e/etc/passwd'), path.join(root, 'etc/passwd'));
    assert.equal(resolveUnderRoot(root, '/%zz'), null);
    assert.equal(resolveUnderRoot(root, '/a%00b'), null);
  });
  test('targetUrl keeps schemes and serves bare paths', () => {
    assert.equal(targetUrl('https://example.test/p', 'http://127.0.0.1:9'), 'https://example.test/p');
    assert.equal(targetUrl('examples/glass-lab/index.html', 'http://127.0.0.1:9'), 'http://127.0.0.1:9/examples/glass-lab/index.html');
  });
  test('--strict fails on an unavailable engine or a failed target capture', () => {
    const ok = { engines: [{ engine: 'chromium', status: 'ok', target: { info: {} } }] };
    const targetFailed = { engines: [{ engine: 'chromium', status: 'ok', target: { error: 'locator.waitFor: Timeout' } }] };
    const unavailable = { engines: [{ engine: 'webkit', status: 'unavailable' }] };
    assert.equal(strictFailure({ strict: true }, ok), false);
    assert.equal(strictFailure({ strict: true }, targetFailed), true);
    assert.equal(strictFailure({ strict: true }, unavailable), true);
    assert.equal(strictFailure({ strict: false }, targetFailed), false);
  });
  test('relative --out resolves against the current directory', () => {
    const o = parseCliArgs(['--out', 'review/probe']);
    assert.equal(o.out, path.resolve('review/probe'));
  });
  test('formatTable reports unavailable engines with their error', () => {
    const text = formatTable({ engines: [{ engine: 'webkit', status: 'unavailable', error: 'Executable does not exist' }] });
    assert.match(text, /webkit\s+unavailable/);
    assert.match(text, /webkit: Executable does not exist/);
  });
  test('static server serves the fixture and refuses escapes', async () => {
    const { server, origin } = await startServer(PLUGIN_ROOT);
    try {
      const ok = await fetch(`${origin}${FIXTURE_PATH}`);
      assert.equal(ok.status, 200);
      assert.match(ok.headers.get('content-type'), /text\/html/);
      assert.match(await ok.text(), /id="probeFilter"/);
      const js = await fetch(`${origin}/examples/glass-lab/liquid-glass.js`);
      assert.match(js.headers.get('content-type'), /javascript/);
      await js.arrayBuffer();
      const missing = await fetch(`${origin}/nope.html`);
      assert.equal(missing.status, 404);
      await missing.arrayBuffer();
    } finally {
      await new Promise((done) => server.close(done));
    }
  });
});

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

test('CLI exits 2 on a usage error', async () => {
  const { code, stderr } = await run(['--browsers', 'netscape']);
  assert.equal(code, 2);
  assert.match(stderr, /unknown engine/);
});

test('CLI loads Playwright from PLAYWRIGHT_MODULE', async () => {
  const scratch = mkdtempSync(path.join(tmpdir(), 'lgs-probe-pw-'));
  try {
    const dir = path.join(scratch, 'playwright');
    mkdirSync(dir);
    writeFileSync(path.join(dir, 'package.json'), JSON.stringify({ name: 'playwright', main: 'index.js' }));
    writeFileSync(
      path.join(dir, 'index.js'),
      "module.exports = { chromium: { launch: async () => { throw new Error('probe stub launch'); } } };\n",
    );
    const { code, stdout, stderr } = await run(['--browsers', 'chromium', '--json'], { env: { ...process.env, PLAYWRIGHT_MODULE: dir } });
    assert.equal(code, 0, stderr);
    const [engine] = JSON.parse(stdout).engines;
    assert.equal(engine.status, 'unavailable');
    assert.match(engine.error, /probe stub launch/);
  } finally {
    rmSync(scratch, { recursive: true, force: true });
  }
});

/* End to end ------------------------------------------------------------- */

describe('glass_probe.mjs end to end', () => {
  let skipReason = false;
  let workdir;

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
    workdir = mkdtempSync(path.join(tmpdir(), 'lgs-probe-'));
  });

  after(() => {
    if (workdir && existsSync(workdir)) rmSync(workdir, { recursive: true, force: true });
  });

  test('chromium renders both url() refraction and blur; other engines are reported honestly', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run(['--browsers', 'chromium,webkit', '--json', '--out', workdir, '--wait', '0']);
    assert.equal(code, 0, stderr);
    const report = JSON.parse(stdout);
    const chromium = report.engines.find((e) => e.engine === 'chromium');
    assert.equal(chromium.status, 'ok');
    assert.equal(chromium.refraction_renders, true, chromium.refraction.reason);
    assert.equal(chromium.blur_renders, true, chromium.blur.reason);
    assert.equal(chromium.refraction.shiftCssPx, 8);
    assert.equal(chromium.recommended.tier, 'refract');
    assert.equal(chromium.engineCard.tier, 'refract', 'the engine card picked refract in Chromium');
    assert.equal(chromium.sniffVsRender.agree, true);
    for (const name of ['pane-refract', 'pane-blur', 'pane-control', 'engine-card', 'fixture']) {
      assert.ok(existsSync(path.join(workdir, `chromium-${name}.png`)), `${name} capture written`);
    }
    const saved = JSON.parse(readFileSync(path.join(workdir, 'report.json'), 'utf8'));
    assert.equal(saved.engines[0].refraction_renders, true);
    const webkit = report.engines.find((e) => e.engine === 'webkit');
    assert.ok(['ok', 'unavailable'].includes(webkit.status), `webkit status ${webkit.status}`);
    if (webkit.status === 'unavailable') assert.ok(webkit.error, 'unavailable carries the launch error');
  });

  test('--url captures a page element per engine', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const { code, stdout, stderr } = await run([
      '--browsers', 'chromium', '--skip-fixture', '--json', '--wait', '0',
      '--url', 'scripts/fixtures/probe.html', '--selector', '#pane-blur',
    ]);
    assert.equal(code, 0, stderr);
    const report = JSON.parse(stdout);
    assert.equal(report.fixture, null);
    const [capture] = report.target.captures;
    assert.equal(capture.engine, 'chromium');
    assert.equal(capture.imageWidth, 240);
    assert.match(capture.backdropFilter, /blur\(12px\)/);
  });

  test('--strict exits 1 when the --url/--selector capture fails', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const args = [
      '--browsers', 'chromium', '--skip-fixture', '--json', '--wait', '0', '--timeout', '2000',
      '--url', 'scripts/fixtures/probe.html', '--selector', '#does-not-exist',
    ];
    const lenient = await run(args);
    assert.equal(lenient.code, 0, lenient.stderr);
    assert.ok(JSON.parse(lenient.stdout).engines[0].target.error, 'the failed capture is in the report');
    const strict = await run([...args, '--strict']);
    assert.equal(strict.code, 1, strict.stderr);
  });

  test('--out is created under the current directory', async (t) => {
    if (skipReason) return t.skip(skipReason);
    const cwd = mkdtempSync(path.join(workdir, 'cwd-'));
    const { code, stderr } = await run([
      '--browsers', 'chromium', '--skip-fixture', '--wait', '0', '--out', 'review/probe/run1',
      '--url', 'scripts/fixtures/probe.html', '--selector', '#pane-blur',
    ], { cwd });
    assert.equal(code, 0, stderr);
    const out = path.join(cwd, 'review', 'probe', 'run1');
    assert.ok(existsSync(path.join(out, 'report.json')), 'report.json written');
    assert.ok(existsSync(path.join(out, 'chromium-target.png')), 'target capture written');
  });
});
