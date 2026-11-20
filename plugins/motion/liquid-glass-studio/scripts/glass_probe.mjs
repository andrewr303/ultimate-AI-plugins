#!/usr/bin/env node
// Render-level glass capability probe, per browser engine.
//
// Usage (run from the user's project directory, by path):
//   node <plugin-root>/scripts/glass_probe.mjs [--browsers chromium,firefox,webkit] [--out dir] [--json]
//                                              [--url <page> --selector <css>] [options]
//
// <plugin-root> is the folder that holds this scripts/ folder. --out resolves
// against the current working directory and is created when missing.
// Playwright is found the same way as glass_contrast.mjs: PLAYWRIGHT_MODULE,
// a normal import, the current directory, the plugin root, the global npm root.
//
// Method:
//   1. Serve a folder (default: the plugin root) from a local node:http server
//      on a free port. No network access is needed.
//   2. For each requested engine, launch the Playwright build that is already
//      installed. A missing package or browser is recorded as "unavailable"
//      with the error; nothing is installed.
//   3. Load scripts/fixtures/probe.html: one pane with a url() backdrop filter
//      that shifts the backdrop by a constant 8 CSS px, one pane with
//      backdrop-filter: blur(12px), one control pane with no filter, and one
//      real createGlass card from examples/glass-lab/liquid-glass.js.
//   4. Screenshot each pane, decode the PNGs through a canvas in a blank page
//      of the same browser (no image library), and compare with the control:
//        refraction renders  when the pane equals the control shifted by the
//                            expected amount (shift search over luma);
//        blur renders        when the pane differs, edge energy falls and the
//                            average brightness holds.
//   5. Report the tier each engine earned by rendering next to the tier the
//      engine picked by sniffing and the parse-level CSS.supports answers.
//   6. With --url and --selector, also screenshot that element in every
//      engine and compare each capture with the first engine's capture.
//
// Exit codes: 0 the run completed (a browser build that is not installed is
// reported as "unavailable"; read the report), 1 --strict was given and an
// engine was unavailable or failed, or the --url/--selector capture failed in
// any engine, 2 could not run (usage error, Playwright package missing, local
// server could not start).

import { createServer } from 'node:http';
import { createReadStream, realpathSync } from 'node:fs';
import { mkdir, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { playwrightMissingMessage, resolvePlaywright } from './glass_contrast.mjs';
import { analyzeBlur, analyzeRefraction, compareCaptures, compareTiers, recommendTier } from './probe-math.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
export const PLUGIN_ROOT = path.resolve(here, '..');
export const FIXTURE_PATH = '/scripts/fixtures/probe.html';
export const ENGINES = Object.freeze(['chromium', 'firefox', 'webkit']);
const EXPECTED_SHIFT_CSS = 8; // probe.html: feDisplacementMap scale 16 with red 1.0

const HELP = `Usage: node <plugin-root>/scripts/glass_probe.mjs [options]

Renders known backdrop filters in each installed Playwright engine and
measures the pixels, instead of trusting user agent strings or CSS.supports.
Run it from your project directory. --out resolves against the current
directory and is created when missing.

Options:
  --browsers <list>     comma list of chromium, firefox, webkit (default all three)
  --out <dir>           write PNG captures and report.json to this folder
                        (relative to the current directory; created if missing)
  --json                print the JSON report instead of the table
  --url <page>          also capture a page of yours in every engine: an http,
                        https or file URL, or a path under --root
  --selector <css>      element to capture on --url (first match)
  --root <dir>          folder the local server serves (default: plugin root;
                        pass --root . to serve your project for a bare --url path)
  --skip-fixture        with --url, skip the capability probe
  --dpr <n>             device pixel ratio (default 1)
  --viewport <WxH>      viewport in CSS pixels (default 1024x900)
  --wait <ms>           settle time after load (default 300)
  --timeout <ms>        launch, navigation and selector timeout (default 30000)
  --strict              exit 1 when a requested engine is unavailable or fails,
                        or when the --url/--selector capture fails in any engine
  -h, --help            show this help

Playwright: found through PLAYWRIGHT_MODULE (path to a playwright package
folder), a normal import, the current directory, the plugin root, or the global
npm root. This script never installs Playwright or browsers.

Exit codes: 0 completed, 1 --strict and an engine or target capture failed,
2 could not run.`;

export class UsageError extends Error {}

export function parseCliArgs(argv) {
  let values;
  try {
    ({ values } = parseArgs({
      args: argv,
      options: {
        browsers: { type: 'string', default: ENGINES.join(',') },
        out: { type: 'string' },
        json: { type: 'boolean', default: false },
        url: { type: 'string' },
        selector: { type: 'string' },
        root: { type: 'string' },
        'skip-fixture': { type: 'boolean', default: false },
        dpr: { type: 'string', default: '1' },
        viewport: { type: 'string', default: '1024x900' },
        wait: { type: 'string', default: '300' },
        timeout: { type: 'string', default: '30000' },
        strict: { type: 'boolean', default: false },
        help: { type: 'boolean', short: 'h', default: false },
      },
      strict: true,
    }));
  } catch (error) {
    throw new UsageError(error.message);
  }
  if (values.help) return { help: true };
  const problems = [];
  const browsers = [...new Set(values.browsers.split(',').map((s) => s.trim().toLowerCase()).filter(Boolean))];
  if (!browsers.length) problems.push('--browsers needs at least one engine');
  for (const b of browsers) if (!ENGINES.includes(b)) problems.push(`unknown engine "${b}" (use ${ENGINES.join(', ')})`);
  if (Boolean(values.url) !== Boolean(values.selector)) problems.push('--url and --selector go together');
  if (values['skip-fixture'] && !values.url) problems.push('--skip-fixture needs --url');
  const dpr = Number(values.dpr);
  if (!(dpr > 0 && dpr <= 4)) problems.push('--dpr must be a number in (0, 4]');
  const viewport = /^(\d+)x(\d+)$/.exec(values.viewport);
  if (!viewport) problems.push('--viewport must look like 1024x900');
  const wait = Number(values.wait);
  const timeout = Number(values.timeout);
  if (!(wait >= 0) || !(timeout > 0)) problems.push('--wait and --timeout must be non-negative numbers');
  if (problems.length) throw new UsageError(problems.join('; '));
  return {
    browsers,
    out: values.out ? path.resolve(values.out) : null,
    json: values.json,
    url: values.url ?? null,
    selector: values.selector ?? null,
    root: path.resolve(values.root ?? PLUGIN_ROOT),
    fixture: !values['skip-fixture'],
    dpr,
    viewport: { width: Number(viewport[1]), height: Number(viewport[2]) },
    wait,
    timeout,
    strict: values.strict,
  };
}

/* ------------------------------------------------------------------------ */
/* Static server                                                             */
/* ------------------------------------------------------------------------ */

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.gif': 'image/gif',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
};

/** Map a request path onto a file under root, or null when it escapes root. */
export function resolveUnderRoot(root, urlPath) {
  let decoded;
  try {
    decoded = decodeURIComponent(String(urlPath).split('?')[0].split('#')[0]);
  } catch {
    return null;
  }
  if (decoded.includes('\0')) return null;
  const full = path.resolve(root, `.${path.posix.normalize(`/${decoded}`)}`);
  const base = path.resolve(root);
  return full === base || full.startsWith(base + path.sep) ? full : null;
}

export function startServer(root) {
  const server = createServer(async (req, res) => {
    const send = (code, text) => {
      res.writeHead(code, { 'content-type': 'text/plain; charset=utf-8' });
      res.end(text);
    };
    if (req.method !== 'GET' && req.method !== 'HEAD') return send(405, 'method not allowed');
    let file = resolveUnderRoot(root, req.url);
    if (!file) return send(403, 'forbidden');
    try {
      let info = await stat(file);
      if (info.isDirectory()) {
        file = path.join(file, 'index.html');
        info = await stat(file);
      }
      res.writeHead(200, {
        'content-type': TYPES[path.extname(file).toLowerCase()] ?? 'application/octet-stream',
        'content-length': info.size,
        'cache-control': 'no-store',
      });
      if (req.method === 'HEAD') return res.end();
      createReadStream(file).pipe(res);
    } catch {
      send(404, 'not found');
    }
  });
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ server, origin: `http://127.0.0.1:${port}` });
    });
  });
}

/** Absolute URL for --url: kept as is with a scheme, otherwise a path under the served root. */
export function targetUrl(value, origin) {
  if (/^[a-z][a-z0-9+.-]*:/i.test(value)) return value;
  return new URL(value.startsWith('/') ? value : `/${value}`, origin).href;
}

/* ------------------------------------------------------------------------ */
/* Browser work                                                              */
/* ------------------------------------------------------------------------ */

// Runs in a blank page: PNG (base64) -> RGBA bytes (base64) through a canvas.
async function decodeInPage(pngBase64) {
  const img = new Image();
  img.src = `data:image/png;base64,${pngBase64}`;
  await img.decode();
  const canvas = document.createElement('canvas');
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(img, 0, 0);
  const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < data.length; i += chunk) binary += String.fromCharCode.apply(null, data.subarray(i, i + chunk));
  return { width: canvas.width, height: canvas.height, rgba: btoa(binary) };
}

async function decodePng(decoder, png) {
  const d = await decoder.evaluate(decodeInPage, png.toString('base64'));
  return { width: d.width, height: d.height, data: new Uint8Array(Buffer.from(d.rgba, 'base64')) };
}

const twoFrames = () => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done)));
const firstLine = (error) => String(error?.message ?? error).split('\n')[0];

async function saveCapture(options, name, png, files) {
  if (!options.out) return;
  const file = path.join(options.out, name);
  await writeFile(file, png);
  files.push(file);
}

async function probeFixture(page, decoder, options, origin, engine, files) {
  await page.goto(`${origin}${FIXTURE_PATH}`, { waitUntil: 'load', timeout: options.timeout });
  await page.waitForFunction(() => window.__probe && window.__probe.done, null, { timeout: options.timeout });
  await page.evaluate(twoFrames);
  if (options.wait) await page.waitForTimeout(options.wait);
  const shots = {};
  for (const id of ['pane-refract', 'pane-blur', 'pane-control', 'engine-card']) {
    const png = await page.locator(`#${id}`).screenshot({ type: 'png', animations: 'disabled' });
    shots[id] = png;
    await saveCapture(options, `${engine}-${id}.png`, png, files);
  }
  await saveCapture(options, `${engine}-fixture.png`, await page.locator('main').screenshot({ type: 'png' }), files);
  const [refract, blur, control] = await Promise.all(
    ['pane-refract', 'pane-blur', 'pane-control'].map((id) => decodePng(decoder, shots[id])),
  );
  const refraction = analyzeRefraction(refract, control, { expectedShiftCss: EXPECTED_SHIFT_CSS, dpr: options.dpr });
  const blurResult = analyzeBlur(blur, control, { dpr: options.dpr });
  const state = await page.evaluate(() => window.__probe);
  const recommended = recommendTier({ refraction, blur: blurResult });
  const card = state.engineCard ?? { error: 'no engine card result' };
  const sniffed = card.tier ?? null;
  return {
    refraction,
    blur: blurResult,
    recommended,
    parseLevel: state.parse,
    engineCard: card,
    sniffVsRender: sniffed ? { sniffedTier: sniffed, renderedTier: recommended.tier, ...compareTiers(sniffed, recommended.tier) } : null,
    userAgent: state.userAgent,
  };
}

async function captureTarget(page, decoder, options, url, engine, files) {
  await page.goto(url, { waitUntil: 'load', timeout: options.timeout });
  const target = page.locator(options.selector).first();
  await target.waitFor({ state: 'visible', timeout: options.timeout });
  await page.evaluate(twoFrames);
  if (options.wait) await page.waitForTimeout(options.wait);
  await target.scrollIntoViewIfNeeded();
  const info = await target.evaluate((el) => {
    const cs = getComputedStyle(el);
    return {
      backdropFilter: cs.backdropFilter || 'unsupported',
      webkitBackdropFilter: cs.webkitBackdropFilter || 'unsupported',
      glassTier: el.getAttribute('data-glass-tier'),
      width: el.getBoundingClientRect().width,
      height: el.getBoundingClientRect().height,
    };
  });
  const png = await target.screenshot({ type: 'png', animations: 'disabled' });
  await saveCapture(options, `${engine}-target.png`, png, files);
  return { info, image: await decodePng(decoder, png) };
}

async function runEngine(playwright, engine, options, origin) {
  const result = { engine, status: 'ok' };
  const type = playwright?.[engine];
  if (!type) {
    return { engine, status: 'unavailable', error: 'Playwright is not installed (this script does not install it)' };
  }
  let browser;
  try {
    browser = await type.launch({ headless: true, timeout: options.timeout });
  } catch (error) {
    return { engine, status: 'unavailable', error: firstLine(error) };
  }
  const files = [];
  try {
    result.version = browser.version();
    const context = await browser.newContext({
      viewport: options.viewport,
      deviceScaleFactor: options.dpr,
      colorScheme: 'light',
      reducedMotion: 'no-preference',
    });
    const page = await context.newPage();
    const decoder = await context.newPage();
    await decoder.goto('about:blank');
    if (options.fixture) {
      Object.assign(result, await probeFixture(page, decoder, options, origin, engine, files));
      result.refraction_renders = result.refraction.renders;
      result.blur_renders = result.blur.renders;
    }
    if (options.url) {
      try {
        result.target = await captureTarget(page, decoder, options, targetUrl(options.url, origin), engine, files);
      } catch (error) {
        result.target = { error: firstLine(error) };
      }
    }
  } catch (error) {
    result.status = 'error';
    result.error = firstLine(error);
  } finally {
    await browser.close().catch(() => {});
  }
  if (files.length) result.files = files;
  return result;
}

export async function probe(options, playwright) {
  if (options.out) await mkdir(options.out, { recursive: true });
  const { server, origin } = await startServer(options.root);
  try {
    const engines = [];
    for (const engine of options.browsers) engines.push(await runEngine(playwright, engine, options, origin));
    const report = {
      tool: 'glass_probe',
      fixture: options.fixture ? `${origin}${FIXTURE_PATH}` : null,
      dpr: options.dpr,
      viewport: options.viewport,
      engines,
      method:
        'Rendered a constant 8 CSS px url() displacement, a 12px blur and a control pane over the same aperiodic ' +
        'barcode, then compared pixels. Refraction counts as rendered only when the pane equals the control at the ' +
        'expected shift; blur only when edges soften and brightness holds.',
    };
    if (options.url) report.target = summarizeTargets(options, engines);
    return report;
  } finally {
    await new Promise((done) => server.close(done));
  }
}

function summarizeTargets(options, engines) {
  const captured = engines.filter((e) => e.target && e.target.image);
  const base = captured[0];
  const rows = engines
    .filter((e) => e.target)
    .map((e) => {
      if (e.target.error) return { engine: e.engine, error: e.target.error };
      const row = { engine: e.engine, ...e.target.info, imageWidth: e.target.image.width, imageHeight: e.target.image.height };
      if (base && e !== base) row.versus = { engine: base.engine, ...compareCaptures(e.target.image, base.target.image) };
      return row;
    });
  for (const e of engines) if (e.target && e.target.image) delete e.target.image;
  return { url: options.url, selector: options.selector, captures: rows };
}

/* ------------------------------------------------------------------------ */
/* Output                                                                    */
/* ------------------------------------------------------------------------ */

const yesNo = (v) => (v === true ? 'yes' : v === false ? 'no' : '-');

export function formatTable(report) {
  const head = ['engine', 'status', 'refraction', 'blur', 'shift', 'blur edges', 'sniffed', 'rendered tier'];
  const rows = report.engines.map((e) => {
    if (e.status !== 'ok' || !e.refraction) return [e.engine, e.status, '-', '-', '-', '-', '-', '-'];
    const card = e.engineCard?.tier ?? 'n/a';
    return [
      e.engine,
      `ok ${e.version ?? ''}`.trim(),
      `${yesNo(e.refraction.renders)} (${e.refraction.status})`,
      `${yesNo(e.blur.renders)} (${e.blur.status})`,
      `${e.refraction.shiftCssPx}px/${EXPECTED_SHIFT_CSS}`,
      `${(e.blur.sharpnessRatio * 100).toFixed(2)}%`,
      card,
      e.recommended.tier,
    ];
  });
  const widths = head.map((h, i) => Math.max(h.length, ...rows.map((r) => String(r[i]).length)));
  const line = (r) => r.map((c, i) => String(c).padEnd(widths[i])).join('  ').trimEnd();
  const out = [line(head), line(widths.map((w) => '-'.repeat(w))), ...rows.map(line)];
  for (const e of report.engines) {
    if (e.error) out.push(`${e.engine}: ${e.error}`);
    if (e.sniffVsRender && e.sniffVsRender.agree === false) {
      out.push(
        `${e.engine}: the engine sniff picked "${e.sniffVsRender.sniffedTier}" but pixels support "${e.sniffVsRender.renderedTier}" (${e.sniffVsRender.direction})`,
      );
    }
    if (e.parseLevel && e.refraction && e.parseLevel.backdropUrl && !e.refraction.renders) {
      out.push(`${e.engine}: CSS.supports accepts backdrop-filter: url() but it did not render`);
    }
    if (e.engineCard?.error) out.push(`${e.engine}: engine card: ${e.engineCard.error}`);
  }
  if (report.target) {
    out.push('', `target ${report.target.url}  ${report.target.selector}`);
    for (const c of report.target.captures) {
      if (c.error) {
        out.push(`  ${c.engine}: ${c.error}`);
        continue;
      }
      const vs = c.versus
        ? c.versus.comparable
          ? `, vs ${c.versus.engine}: mean diff ${c.versus.meanAbsDiff}${c.versus.similar ? ' (similar)' : ' (differs)'}`
          : `, vs ${c.versus.engine}: ${c.versus.reason}`
        : '';
      out.push(`  ${c.engine}: ${c.imageWidth}x${c.imageHeight}, backdrop-filter ${c.backdropFilter}, tier ${c.glassTier ?? 'n/a'}${vs}`);
    }
  }
  const files = report.engines.flatMap((e) => e.files ?? []);
  if (files.length) out.push('', `captures: ${files.length} PNG files${report.out ? ` in ${report.out}` : ''}`);
  out.push(
    '',
    'rendered tier = what the pixels support; user preferences (reduced transparency, more contrast,',
    'forced colors) still lower it at runtime. One frame, one DPR, headless; confirm on real devices.',
  );
  return out.join('\n');
}

/** Under --strict: an engine that is not ok, or a --url/--selector capture that failed. */
export function strictFailure(options, report) {
  if (!options.strict) return false;
  return report.engines.some((e) => e.status !== 'ok' || Boolean(e.target?.error));
}

export async function main(argv = process.argv.slice(2)) {
  let options;
  try {
    options = parseCliArgs(argv);
  } catch (error) {
    process.stderr.write(`glass_probe: ${error.message}\n\n${HELP}\n`);
    return 2;
  }
  if (options.help) {
    process.stdout.write(`${HELP}\n`);
    return 0;
  }
  try {
    const info = await stat(options.root);
    if (!info.isDirectory()) throw new Error('not a directory');
  } catch (error) {
    process.stderr.write(`glass_probe: --root ${options.root}: ${error.message}\n`);
    return 2;
  }
  const found = await resolvePlaywright();
  const playwright = found.module;
  if (!playwright) {
    process.stderr.write(playwrightMissingMessage('glass_probe', options.browsers.join(' ')));
    return 2;
  }
  const badOverride = found.tried.find((t) => t.source.startsWith('PLAYWRIGHT_MODULE'));
  if (badOverride) process.stderr.write(`glass_probe: warning: ${badOverride.source} did not load (${badOverride.error}); used ${found.source}\n`);
  let report;
  try {
    report = await probe(options, playwright);
  } catch (error) {
    process.stderr.write(`glass_probe: ${firstLine(error)}\n`);
    return 2;
  }
  if (options.out) {
    report.out = options.out;
    await writeFile(path.join(options.out, 'report.json'), `${JSON.stringify(report, null, 2)}\n`);
  }
  process.stdout.write(`${options.json ? JSON.stringify(report, null, 2) : formatTable(report)}\n`);
  return strictFailure(options, report) ? 1 : 0;
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
