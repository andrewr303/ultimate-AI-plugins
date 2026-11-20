#!/usr/bin/env node
// design-variations smoke test (optional). Needs Node 18+ and Playwright with a Chromium build.
//
//   node smoke.mjs <gallery index.html> [--shots <dir>] [--frame-width 390] [--round <n>] [--states]
//                  [--clicks 12] [--squint 0.92] [--timeout 20000]
//
// Loads the gallery, mounts every prototype, then inside each frame:
// - saves the first screen, before any interaction and once entry animations finish, as <id>.png (with --shots);
// - looks over the whole page for layout faults: an element with the hidden attribute that still renders (fails the
//   option); a visible button, link or field whose centre point is covered by an unrelated element (under a fixed or
//   sticky bar it counts only when scrolling cannot bring it out from under the bar), and text or a
//   placeholder cut off by an overflow:hidden box with no ellipsis, or a line lost just below a fixed-height box
//   (both warnings; a card cut at the edge of a carousel or scrolling track is a peek and is not reported). A first
//   screen with almost no light/dark variation is reported as blank (a warning). Only the centre is tested, so a
//   decoration painted beneath a control is not caught;
// - records load errors, types into the first text field, presses up to --clicks visible buttons (Escape after each)
//   and counts which controls visibly changed something. A press that changes nothing fails its option unless the
//   button carries data-dv-inert="reason". A button with aria-expanded or aria-controls whose press flips its state
//   (its ARIA state, or the hidden, class or style of the region it controls) must also change what is on screen
//   outside itself; one that only flips attributes is dead ("toggle changes nothing visible"). Pressing the tab that
//   is already selected flips nothing, so it is judged like any other button.
// --round N tests only round N's options. Today's first screen is still captured, untested, for the squint test.
// --states then resets each option and posts every value of its State menu (data-states with two or more values)
//   into the frame, the way the menu does. It saves <id>--<state>.png (with --shots; the state in lower case, letters
//   and digits in any script kept, other characters as dashes, and a number added when two states share a name; the
//   exact file is in results[].states[state].shot) and records, per state, errors, hidden elements that render and (with --frame-width) sideways
//   overflow, which fail the option, and covered controls and cut-off text (warnings). Faults already reported for
//   the first screen are not repeated per state.
// --frame-width W reloads every prototype at W pixels wide (the gallery's width switch) and fails options whose page
//   scrolls sideways.
// Squint test: each first screen is reduced to a coarse grid of light and dark blocks. Same-round pairs that correlate
// above --squint (default 0.92) are look-alikes; Rethink and Reinvent options above it against today are close to
// today; the three nearest pairs in each round are listed whatever their score. Pairs of Refine options (rungs 1-3)
// are skipped because they share today's skeleton by design.
// With --shots it also saves _overview.png, a contact sheet taken from a fresh page. A failed capture or a blank tile
// is reported as overviewError instead of being ignored.
// Prints a JSON report. Exit 0 when every tested option loaded without errors, has no dead controls, no hidden
// element that renders and (with --frame-width) no sideways overflow; warnings never change it. 1 otherwise; 2 on
// setup problems. It cannot judge looks, copy or the contract: look at the shots.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const USAGE = 'usage: node smoke.mjs <index.html> [--shots dir] [--frame-width 390] [--round n] [--states] [--clicks 12] [--squint 0.92] [--timeout 20000]';
const VALUED = ['shots', 'frame-width', 'round', 'clicks', 'squint', 'timeout'];
const FLAGS = ['states'];
const opts = {};
let file = null;
{
  const argv = process.argv.slice(2);
  const bad = (m) => { console.error(m + '\n' + USAGE); process.exit(2); };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) { if (file) bad('unexpected argument ' + a); file = a; continue; }
    const eq = a.indexOf('=');
    const k = a.slice(2, eq > 0 ? eq : undefined);
    if (FLAGS.includes(k)) opts[k] = true;
    else if (VALUED.includes(k)) {
      const v = eq > 0 ? a.slice(eq + 1) : argv[++i];
      if (v == null || v === '' || v.startsWith('--')) bad('--' + k + ' needs a value');
      opts[k] = v;
    } else bad('unknown option ' + a);
  }
  if (!file) bad('no gallery given');
}

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  try { return require('playwright'); } catch (e) { /* try the global install */ }
  try { const root = execSync('npm root -g', { encoding: 'utf8' }).trim(); return require(join(root, 'playwright')); } catch (e) { return null; }
}
const pw = loadPlaywright();
if (!pw) { console.error('Playwright is not available. Install it in the project (npm i -D playwright) or skip the smoke test and click through the gallery by hand.'); process.exit(2); }

const started = Date.now();
const shots = opts.shots || null;
const frameWidth = opts['frame-width'] || '';
const onlyRound = opts.round ? String(opts.round) : '';
const withStates = !!opts.states;
const maxClicks = +(opts.clicks || 12);
const timeout = +(opts.timeout || 20000);
const squintLimit = +(opts.squint || 0.92);
if (shots) mkdirSync(shots, { recursive: true });

const browser = await pw.chromium.launch(process.env.DV_CHROMIUM ? { executablePath: process.env.DV_CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
const helper = await browser.newPage(); // decodes screenshots for the squint test and the overview check
const consoleErrors = [];
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push({ frame: m.location()?.url?.slice(0, 40) || '', text: m.text().slice(0, 240) }); });
page.on('pageerror', (e) => consoleErrors.push({ frame: 'gallery', text: String(e).slice(0, 240) }));

const url = pathToFileURL(resolve(file)).href + (frameWidth ? `?w=${encodeURIComponent(frameWidth)}` : '');
await page.goto(url);
await page.evaluate(() => {
  document.querySelectorAll('.dv-round.dv-collapsed').forEach((r) => r.classList.remove('dv-collapsed'));
  const top = document.querySelector('.dv-top'); if (top) top.style.position = 'static'; // keep the sticky bar out of frame screenshots
});
try {
  await page.waitForFunction(() => !!window.DV_GALLERY, null, { timeout });
} catch (e) {
  console.log(JSON.stringify({ gallery: file, options: 0, passed: 0, failing: ['gallery'], error: 'The gallery runtime did not start; fix these page errors first.', galleryConsoleErrors: consoleErrors.slice(0, 20) }, null, 2));
  await browser.close();
  process.exit(1);
}
await page.evaluate(() => window.DV_GALLERY.mountAll());
const info = await page.$$eval('.dv-option[id]', (as) => as.map((a) => {
  const sec = a.closest('.dv-round');
  return {
    id: a.id,
    rung: +(a.dataset.rung || 0),
    baseline: a.classList.contains('dv-baseline') || a.id === 'today',
    round: (sec && sec.dataset.round) || (a.id.match(/^(\d+)/) || [])[1] || '',
    states: (a.dataset.states || '').split(',').map((s) => s.trim()).filter(Boolean),
  };
}));
const byId = Object.fromEntries(info.map((o) => [o.id, o]));
const rungs = Object.fromEntries(info.map((o) => [o.id, o.rung]));
const roundOf = (id) => (byId[id] && !byId[id].baseline ? byId[id].round : 'today');
const tested = info.filter((o) => !onlyRound || (!o.baseline && o.round === onlyRound)).map((o) => o.id);
if (!tested.length) {
  const rounds = [...new Set(info.filter((o) => !o.baseline).map((o) => o.round))].sort((a, b) => a - b).join(', ');
  console.error(`No options in round ${onlyRound}. This gallery has rounds: ${rounds || 'none'}.`);
  await browser.close();
  process.exit(2);
}
// With --round, today is captured for the squint comparison but not tested.
const compareOnly = new Set(onlyRound && byId.today ? ['today'] : []);
const visit = [...compareOnly, ...tested];
const deadline = Date.now() + timeout;
while (Date.now() < deadline) {
  const pending = await page.$$eval('.dv-option[id]', (as, want) => as.filter((a) => want.includes(a.id) && !a.dataset.dvStatus).length, visit);
  if (!pending) break;
  await page.waitForTimeout(250);
}

// ---- Functions that run inside a prototype frame (serialised by Playwright: no outside references) ----

// Wait for fonts and finite entry animations (capped), then two frames, so shots and checks see the settled page.
async function settleFrame(cap) {
  const t0 = performance.now();
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  try { await Promise.race([document.fonts ? document.fonts.ready : null, sleep(cap)]); } catch (e) { /* no font API */ }
  const running = () => document.getAnimations().filter((a) => {
    if (a.playState !== 'running') return false;
    try { return Number.isFinite(a.effect.getComputedTiming().endTime); } catch (e) { return false; }
  }).length;
  while (running() && performance.now() - t0 < cap) await sleep(50);
  await Promise.race([new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))), sleep(200)]);
}

// Layout faults on the whole page. Scrolls to reach controls below the fold, then puts every scroll back.
function layoutScan(opt) {
  const CAP = 12;
  const out = { hidden: [], covered: [], clipped: [], clippedCount: 0, coveredCount: 0 };
  const add = (list, s) => { if (list.length < CAP && !list.includes(s)) list.push(s); };
  const name = (el, withText) => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    else if (typeof el.className === 'string' && el.className.trim()) s += '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.');
    if (!withText) return s;
    const t = (el.getAttribute('aria-label') || ('innerText' in el ? el.innerText : el.textContent) || el.getAttribute('placeholder') || '').replace(/\s+/g, ' ').trim().slice(0, 32);
    return t ? s + ' "' + t + '"' : s;
  };
  const shown = (el) => (el.checkVisibility ? el.checkVisibility({ opacityProperty: true, visibilityProperty: true }) : el.getClientRects().length > 0);

  // 1. The hidden attribute must hide: a component that sets display overrides it unless the kit guards [hidden].
  for (const el of document.querySelectorAll('[hidden]')) {
    if (!(el instanceof HTMLElement) || el.getAttribute('hidden') === 'until-found') continue;
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) add(out.hidden, name(el, true) + ' has the hidden attribute but renders (display: ' + getComputedStyle(el).display + ')');
  }
  if (opt.hiddenOnly) return out;

  // 2. Covered controls: the centre of a visible control must hit the control itself (or its label).
  const H = window.innerHeight, W = window.innerWidth, sx = window.scrollX, sy = window.scrollY;
  const scrolled = new Map(); // element -> [left, top] before the scan moved it
  const pinned = (el) => { for (let p = el; p && p !== document.body; p = p.parentElement) { const pos = getComputedStyle(p).position; if (pos === 'fixed' || pos === 'sticky') return true; } return false; };
  const inClip = (el, x, y) => {
    for (let p = el.parentElement; p && p !== document.body && p !== document.documentElement; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (cs.overflowX !== 'visible' || cs.overflowY !== 'visible') { const r = p.getBoundingClientRect(); if (x < r.left || x > r.right || y < r.top || y > r.bottom) return false; }
    }
    return true;
  };
  const related = (el, hit) => hit === el || el.contains(hit) || hit.contains(el) || (el.labels && Array.from(el.labels).some((l) => l.contains(hit)));
  const testable = (el) => { const r = el.getBoundingClientRect(); const x = r.left + r.width / 2, y = r.top + r.height / 2; return x >= 0 && y >= 0 && x < W && y < H && inClip(el, x, y) ? [x, y] : null; };
  const coveredBy = (el, pt) => { const hit = document.elementFromPoint(pt[0], pt[1]); return hit && !related(el, hit) ? hit : null; };
  const report = (el, hit) => { out.coveredCount++; add(out.covered, name(el, true) + ' is under ' + name(hit, true)); };
  const controls = Array.from(document.querySelectorAll('button, a[href], input:not([type="hidden"]), select, textarea'))
    .filter((el) => { const r = el.getBoundingClientRect(); return r.width >= 6 && r.height >= 6 && shown(el); }).slice(0, 600);
  const later = [];
  const retry = new Set(); // under a fixed or sticky bar: content scrolls out from under it, so look again once centred
  for (const el of controls) {
    const pt = testable(el);
    if (!pt) { if (!pinned(el)) later.push(el); continue; }
    const hit = coveredBy(el, pt);
    if (!hit) continue;
    if (pinned(hit) && !pinned(el)) { later.push(el); retry.add(el); } else report(el, hit);
  }
  for (const el of later) {
    let pt = testable(el);
    if (!pt || retry.has(el) || pt[1] < H * 0.2 || pt[1] > H * 0.8) {
      for (let p = el.parentElement; p; p = p.parentElement) if (!scrolled.has(p) && (p.scrollTop || p.scrollLeft || p.scrollHeight > p.clientHeight || p.scrollWidth > p.clientWidth)) scrolled.set(p, [p.scrollLeft, p.scrollTop]);
      el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'instant' });
      pt = testable(el);
    }
    const hit = pt && coveredBy(el, pt);
    if (hit) report(el, hit);
  }
  for (const [p, [l, t]] of scrolled) { p.scrollLeft = l; p.scrollTop = t; }
  window.scrollTo({ left: sx, top: sy, behavior: 'instant' });

  // 3. Clipped text: text cut by the nearest overflow:hidden/clip box, with no ellipsis or line clamp.
  const clipCache = new Map();
  const clipperOf = (start, axis) => {
    let entry = clipCache.get(start); if (!entry) { entry = {}; clipCache.set(start, entry); }
    if (axis in entry) return entry[axis];
    let needPositioned = false, found = null;
    for (let p = start; p && p !== document.documentElement; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (needPositioned && cs.position !== 'static') needPositioned = false; // the containing block of an absolute box clips it
      const ov = axis === 'x' ? cs.overflowX : cs.overflowY;
      if (!needPositioned) {
        if (ov === 'hidden' || ov === 'clip') { found = p; break; }
        if (ov === 'auto' || ov === 'scroll') break; // a scroller: the text can be scrolled to
      }
      if (cs.position === 'fixed') break;
      if (cs.position === 'absolute') needPositioned = true;
    }
    entry[axis] = found;
    return found;
  };
  const boxOf = (c) => {
    const cs = getComputedStyle(c);
    if (cs.clip !== 'auto' || cs.clipPath !== 'none') return null; // visually hidden on purpose
    const r = c.getBoundingClientRect();
    if (Math.abs(r.width - c.offsetWidth) > 1 || Math.abs(r.height - c.offsetHeight) > 1) return null; // transformed
    const left = r.left + c.clientLeft, top = r.top + c.clientTop;
    if (c.clientWidth < 4 || c.clientHeight < 4) return null; // collapsed or screen-reader only
    return { left, top, right: left + c.clientWidth, bottom: top + c.clientHeight, cs };
  };
  const moved = (from, to) => { for (let p = from; p && p !== to; p = p.parentElement) if (getComputedStyle(p).transform !== 'none') return true; return false; };
  // A flex or grid track wider than its clipping box is a carousel or a scrolling row: a card cut at its edge is a peek.
  const track = (from, to) => {
    const w = to.getBoundingClientRect().width;
    for (let p = from.parentElement; p && p !== to; p = p.parentElement) {
      const d = getComputedStyle(p).display;
      if (/flex|grid/.test(d) && p.getBoundingClientRect().width > w + 1) return true;
    }
    return false;
  };
  const range = document.createRange();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let seen = 0;
  for (let t = walker.nextNode(); t && seen < 5000; t = walker.nextNode()) {
    const s = t.data; const a = s.search(/\S/); if (a < 0) continue;
    const pe = t.parentElement;
    if (!pe || pe.closest('script, style, template, noscript, svg, textarea, select')) continue;
    seen++;
    if (!shown(pe)) continue;
    const b = s.length - (s.match(/\s*$/)[0].length);
    range.setStart(t, a); range.setEnd(t, b);
    const rects = Array.from(range.getClientRects()).filter((r) => r.width > 0.5 && r.height > 0.5);
    if (!rects.length) continue;
    for (const axis of ['x', 'y']) {
      const c = clipperOf(pe, axis); if (!c) continue;
      const box = boxOf(c); if (!box) continue;
      if (axis === 'x' && (box.cs.textOverflow === 'ellipsis' || moved(pe, c) || track(pe, c))) continue;
      if (axis === 'y' && box.cs.webkitLineClamp && box.cs.webkitLineClamp !== 'none') continue;
      for (const r of rects) {
        const outside = r.right <= box.left || r.left >= box.right || r.bottom <= box.top || r.top >= box.bottom;
        // A line that starts just below a fixed-height box is lost too, unless something between them is moved on
        // purpose (a carousel track or a reveal mask). Other text wholly outside the box is not a visible cut.
        const lost = outside && axis === 'y' && r.top >= box.bottom - 0.5 && r.top - box.bottom < r.height && r.right > box.left && r.left < box.right && !moved(pe, c);
        if (outside && !lost) continue;
        const over = lost ? r.height : axis === 'x' ? Math.max(r.right - box.right, box.left - r.left) : Math.max(r.bottom - box.bottom, box.top - r.top);
        if (over > (axis === 'x' ? 2 : Math.max(3, r.height * 0.3))) {
          const edge = axis === 'x' ? (r.right > box.right ? 'right' : 'left') : (r.bottom > box.bottom ? 'bottom' : 'top');
          out.clippedCount++;
          add(out.clipped, '"' + s.slice(a, b).replace(/\s+/g, ' ').slice(0, 32) + '" ' + (lost ? 'hidden below the bottom edge of ' : 'cut at the ' + edge + ' edge of ') + name(c, false));
          break;
        }
      }
    }
  }
  // Placeholders wider than their field.
  const ctx = document.createElement('canvas').getContext('2d');
  for (const el of document.querySelectorAll('input[placeholder]')) {
    const type = (el.getAttribute('type') || 'text').toLowerCase();
    if (el.value || !el.placeholder || !/^(text|search|email|url|tel|password|number)$/.test(type) || !shown(el)) continue;
    const cs = getComputedStyle(el);
    let ps = cs; try { ps = getComputedStyle(el, '::placeholder'); } catch (e) { /* no pseudo styles */ }
    if (cs.textOverflow === 'ellipsis' || ps.textOverflow === 'ellipsis') continue;
    const widthIn = (st) => {
      ctx.font = [st.fontStyle, st.fontWeight, st.fontSize, st.fontFamily].join(' ');
      try { ctx.letterSpacing = st.letterSpacing === 'normal' ? '0px' : st.letterSpacing; } catch (e) { /* older canvas */ }
      return ctx.measureText(el.placeholder).width;
    };
    const need = widthIn(ps);
    let cut = false;
    if (type !== 'number' && type !== 'password') {
      // Let the browser lay the words out as a value for a moment (no events fire): this counts the room a search
      // field keeps for its clear button. Then allow for a placeholder font that differs from the value font.
      el.value = el.placeholder; const over = el.scrollWidth - el.clientWidth; el.value = '';
      if (over > 0) cut = over + need - widthIn(cs) > 1;
    }
    if (!cut) { const room = el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight); cut = room > 0 && need > room + 2; }
    if (cut) { out.clippedCount++; add(out.clipped, 'placeholder "' + el.placeholder.slice(0, 32) + '" is wider than ' + name(el, false)); }
  }
  return out;
}

// A toggle's own state: its ARIA state attributes and the hidden, class, style and open attributes of the regions it
// names in aria-controls. A press flipped the toggle when this changes. null when the toggle was replaced without an id.
function toggleState(el) {
  const live = el.isConnected ? el : (el.id && document.getElementById(el.id)) || null;
  if (!live) return null;
  const s = ['aria-expanded', 'aria-pressed', 'aria-selected', 'aria-checked'].map((a) => live.getAttribute(a));
  for (const id of (live.getAttribute('aria-controls') || '').split(/\s+/).filter(Boolean)) {
    const t = document.getElementById(id);
    s.push(t ? [t.hidden, t.getAttribute('class'), t.getAttribute('style'), t.hasAttribute('open'), t.getAttribute('aria-hidden'), t.hasAttribute('inert')].join('|') : '-');
  }
  return JSON.stringify(s);
}

// A fingerprint of what is on screen outside the pressed toggle: every rendered element's box, colours, opacity and
// transform, plus the rendered text. The toggle itself is left out (its icon turns and its label may change), and so
// are elements that are animating on their own. A toggle that leaves this unchanged changed nothing visible.
function visibleSignature(btn) {
  let h = 2166136261 >>> 0;
  const mix = (s) => { for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } };
  const self = btn && (btn.isConnected ? btn : (btn.id && document.getElementById(btn.id))); // a re-rendered toggle keeps its id
  const inBtn = (el) => !!self && (self === el || self.contains(el));
  const moving = new Set();
  for (const a of document.getAnimations()) if (a.playState === 'running' && a.effect && a.effect.target) moving.add(a.effect.target);
  const animated = (el) => { for (let p = el; p; p = p.parentElement) if (moving.has(p)) return true; return false; };
  const on = (el) => (el.checkVisibility ? el.checkVisibility({ opacityProperty: true, visibilityProperty: true }) : el.getClientRects().length > 0);
  let n = 0;
  for (const el of document.body.querySelectorAll('*')) {
    if (inBtn(el) || !on(el) || (moving.size && animated(el))) continue;
    const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); n++;
    // Native state that paints without changing boxes or colours: ticks, field values, the selected option, image sources.
    const st = (el.tagName === 'INPUT' ? (el.checked ? 'x' : 'o') + el.value : '') + (el.tagName === 'SELECT' ? el.selectedIndex : '')
      + (el.tagName === 'TEXTAREA' || el.tagName === 'OUTPUT' ? el.value : '') + (el.tagName === 'IMG' ? el.currentSrc : '');
    mix(el.tagName + Math.round(r.left) + ',' + Math.round(r.top) + ',' + Math.round(r.width) + ',' + Math.round(r.height) + cs.color + cs.backgroundColor + cs.borderTopColor + cs.opacity + cs.transform + st + ';');
  }
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let t = walker.nextNode(); t; t = walker.nextNode()) {
    const pe = t.parentElement;
    if (pe && t.data.trim() && !inBtn(pe) && on(pe)) mix(t.data);
  }
  return h + ':' + n;
}

// ---- Helpers that run in Node ----
const settle = (frame, cap = 1500) => frame.evaluate(settleFrame, cap).catch(() => {});
async function blockMass(png) { return (await gridsOf(png, null))[0]; }
// Reduce a screenshot (or regions of it) to 24x16 luminance grids.
async function gridsOf(png, regions) {
  return helper.evaluate(async ([b64, regions]) => {
    const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
    const c = document.createElement('canvas'); c.width = 24; c.height = 16;
    const g = c.getContext('2d');
    return (regions || [{ x: 0, y: 0, w: img.naturalWidth, h: img.naturalHeight }]).map((r) => {
      g.clearRect(0, 0, 24, 16); g.drawImage(img, r.x, r.y, r.w, r.h, 0, 0, 24, 16);
      const d = g.getImageData(0, 0, 24, 16).data; const out = [];
      for (let i = 0; i < d.length; i += 4) out.push(0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]);
      return out;
    });
  }, [png.toString('base64'), regions]);
}
const spread = (a) => { const m = a.reduce((s, x) => s + x, 0) / a.length; return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / a.length); };
// State shot names: lower case, letters and digits in any script kept, everything else a dash; a number is added
// when two states of one option would get the same name.
const slug = (s, used) => {
  const base = String(s).normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || 'state';
  let name = base; for (let k = 2; used && used.has(name); k++) name = `${base}-${k}`;
  if (used) used.add(name);
  return name;
};
const trim = (list, count) => (count > list.length ? [...list, `+${count - list.length} more`] : list);
async function frameOf(art) { const h = await art.locator('.dv-frame iframe').elementHandle({ timeout: 2000 }).catch(() => null); return h ? h.contentFrame() : null; }

const results = [];
const masses = {};
for (const id of visit) {
  const art = page.locator(`[id="${id}"]`);
  const status = await art.getAttribute('data-dv-status');
  const errText = status === 'error' ? (await art.locator('.dv-error').textContent().catch(() => '')) : '';
  let frame = await frameOf(art);
  // First screen, before any interaction: this is what the screenshots and the squint test compare.
  await art.locator('.dv-frame').scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {});
  await page.mouse.move(0, 0); // no hover left over from the previous option's clicks
  await page.waitForTimeout(300);
  if (frame) await settle(frame);
  try {
    const png = await art.locator('.dv-frame').screenshot(shots && !compareOnly.has(id) ? { path: join(shots, `${id}.png`) } : {});
    masses[id] = await blockMass(png);
  } catch (e) { /* frame not visible: no squint data */ }
  if (compareOnly.has(id)) continue;
  const r = { id, round: roundOf(id), loaded: status === 'loaded' || status === 'error', error: errText || null, controls: 0, clicked: 0, responsive: 0, typed: false, dead: [], overflow: false, hiddenRenders: [], covered: [], clipped: [] };
  // A first screen with almost no light/dark variation is blank (often content waiting on an entrance animation).
  if (masses[id] && spread(masses[id]) < 1.5) r.blankFirstScreen = true;
  if (!frame) { r.error = r.error || 'no frame'; results.push(r); continue; }
  const scan = await frame.evaluate(layoutScan, {}).catch((e) => ({ hidden: [], covered: [], clipped: [], coveredCount: 0, clippedCount: 0, failed: String(e.message || e).slice(0, 120) }));
  r.hiddenRenders = scan.hidden;
  r.covered = trim(scan.covered, scan.coveredCount);
  r.clipped = trim(scan.clipped, scan.clippedCount);
  if (scan.failed) r.scanError = scan.failed;
  await page.waitForTimeout(150); // let scroll events from the scan land before counting mutations
  await frame.evaluate(() => {
    window.__dvMut = 0;
    new MutationObserver((m) => { window.__dvMut += m.length; }).observe(document.documentElement, { subtree: true, childList: true, attributes: true, characterData: true });
  });
  r.controls = await frame.$$eval('button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"]), summary, [role="button"], [role="tab"], [role="slider"]', (els) => els.length);
  const field = frame.locator('input[type="search"], input[type="text"], input:not([type]), textarea').first();
  if (await field.count()) {
    try { await field.fill('a', { timeout: 1500 }); r.typed = true; await field.fill('', { timeout: 1500 }); } catch (e) { /* not typeable */ }
  }
  if (frameWidth) r.overflow = await frame.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1).catch(() => false);
  const buttons = frame.locator('button:visible:not([disabled]):not([aria-disabled="true"]):not([data-dv-inert])');
  const n = Math.min(await buttons.count(), maxClicks);
  for (let i = 0; i < n; i++) {
    const b = buttons.nth(i);
    let label = '';
    try {
      label = ((await b.getAttribute('aria-label')) || (await b.innerText({ timeout: 1500 })) || '').replace(/\s+/g, ' ').trim().slice(0, 40);
      // A press responds when the DOM changes, focus moves or anything scrolls. Look twice before calling it dead:
      // a busy machine can delay the first reading.
      const probe = () => frame.evaluate(() => {
        const a = document.activeElement;
        let scroll = window.scrollX + window.scrollY;
        for (const el of document.querySelectorAll('*')) if (el.scrollTop || el.scrollLeft) scroll += el.scrollTop + el.scrollLeft;
        // Field values and ticks change as properties, not DOM mutations (a stepper's + button, Select all).
        let fields = '';
        for (const f of document.querySelectorAll('input, select, textarea')) fields += (f.checked ? 'x' : 'o') + f.value + (f.selectedIndex ?? '') + '|';
        return { mut: window.__dvMut, focus: a ? (a.id || a.tagName) + ':' + (a.textContent || '').slice(0, 20) : '', scroll, fields };
      });
      const changed = (x, y) => y.mut > x.mut || y.focus !== x.focus || y.scroll !== x.scroll || y.fields !== x.fields;
      // A toggle (aria-expanded or aria-controls) whose press flips its state must change what is on screen, not only
      // attributes. Pressing the tab that is already selected flips nothing and is judged like any other button.
      // Hover first so hover styles are already in the "before" picture.
      const el = await b.elementHandle({ timeout: 1500 });
      const toggle = await el.evaluate((x) => x.hasAttribute('aria-expanded') || x.hasAttribute('aria-controls'));
      if (toggle) { await b.hover({ timeout: 1500 }); await page.waitForTimeout(150); }
      await b.focus({ timeout: 1500 }); // clicking focuses the button itself; that alone is not a response
      const before = await probe();
      const stateBefore = toggle ? await el.evaluate(toggleState) : null;
      const sigBefore = toggle ? await el.evaluate(visibleSignature) : null;
      await b.click({ timeout: 1500 });
      await page.waitForTimeout(120);
      let after = await probe();
      if (!changed(before, after)) { await page.waitForTimeout(500); after = await probe(); }
      r.clicked++;
      let why = changed(before, after) ? '' : 'dead';
      if (!why && toggle && stateBefore && after.focus === before.focus && after.scroll === before.scroll) {
        const stateAfter = await el.evaluate(toggleState).catch(() => null);
        if (stateAfter && stateAfter !== stateBefore) {
          let sig = await el.evaluate(visibleSignature);
          if (sig === sigBefore) { await page.waitForTimeout(500); sig = await el.evaluate(visibleSignature); }
          if (sig === sigBefore) why = 'toggle';
        }
      }
      await el.dispose().catch(() => {});
      if (!why) r.responsive++;
      else r.dead.push((label || `button ${i + 1}`) + (why === 'toggle' ? ' (toggle changes nothing visible)' : ''));
      await frame.locator('body').press('Escape').catch(() => {});
    } catch (e) { /* hidden, detached or covered: skip */ }
  }
  // Interactions can hide things too: check the hidden attribute again on the clicked-through page.
  const lateHidden = await frame.evaluate(layoutScan, { hiddenOnly: true }).catch(() => ({ hidden: [] }));
  for (const h of lateHidden.hidden) if (!r.hiddenRenders.includes(h)) r.hiddenRenders.push(h);
  const lateStatus = await art.getAttribute('data-dv-status');
  if (lateStatus === 'error' && !r.error) r.error = (await art.locator('.dv-error').textContent().catch(() => 'error during interaction'));

  const states = byId[id].states;
  if (withStates && states.length > 1) {
    // Start from a fresh copy of the prototype, then switch states the way the gallery's State menu does.
    r.states = {};
    const usedSlugs = new Set();
    await page.evaluate((x) => { const b = document.getElementById(x)?.querySelector('.dv-reset'); if (b) b.click(); }, id);
    await art.locator('.dv-frame').scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {});
    const until = Date.now() + timeout;
    while (Date.now() < until && !(await art.getAttribute('data-dv-status'))) await page.waitForTimeout(100);
    frame = await frameOf(art);
    const resetStatus = await art.getAttribute('data-dv-status');
    if (frame) {
      await settle(frame);
      await frame.evaluate(() => {
        window.__dvErrs = [];
        window.addEventListener('error', (e) => window.__dvErrs.push(String(e.message || 'Script error').slice(0, 200)));
        window.addEventListener('unhandledrejection', (e) => window.__dvErrs.push(String((e.reason && e.reason.message) || e.reason).slice(0, 200)));
      }).catch(() => {});
    }
    for (const s of states) {
      const st = { errors: [] };
      if (!frame) { st.errors.push('no frame after reset'); r.states[s] = st; continue; }
      if (resetStatus === 'error' && s === states[0]) st.errors.push((await art.locator('.dv-error').textContent().catch(() => 'error after reset')) || 'error after reset');
      await page.evaluate(([x, v]) => {
        const a = document.getElementById(x); if (!a) return;
        const sel = a.querySelector('.dv-state'); if (sel) sel.value = v;
        const f = a.querySelector('.dv-frame iframe'); if (f && f.contentWindow) f.contentWindow.postMessage({ dvState: v }, '*');
      }, [id, s]);
      await page.mouse.move(0, 0);
      await page.waitForTimeout(250);
      await settle(frame);
      if (shots) {
        const name = `${id}--${slug(s, usedSlugs)}.png`;
        try { await art.locator('.dv-frame').screenshot({ path: join(shots, name) }); st.shot = name; } catch (e) { st.errors.push('screenshot failed'); }
      }
      st.errors.push(...(await frame.evaluate(() => (window.__dvErrs || []).splice(0)).catch(() => [])));
      const ss = await frame.evaluate(layoutScan, {}).catch(() => null);
      if (ss) {
        const hid = ss.hidden.filter((x) => !r.hiddenRenders.includes(x)); if (hid.length) st.hiddenRenders = hid;
        const cov = ss.covered.filter((x) => !scan.covered.includes(x)); if (cov.length) st.covered = cov;
        const clip = ss.clipped.filter((x) => !scan.clipped.includes(x)); if (clip.length) st.clipped = clip;
      }
      if (frameWidth) st.overflow = await frame.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1).catch(() => false);
      if (!st.errors.length) delete st.errors;
      r.states[s] = st;
    }
  }
  results.push(r);
}

// Automated squint test: correlate coarse light/dark block patterns of options within the same round.
function corr(a, b) {
  const n = a.length, ma = a.reduce((s, x) => s + x, 0) / n, mb = b.reduce((s, x) => s + x, 0) / n;
  let num = 0, da = 0, db = 0;
  for (let i = 0; i < n; i++) { num += (a[i] - ma) * (b[i] - mb); da += (a[i] - ma) ** 2; db += (b[i] - mb) ** 2; }
  return da && db ? num / Math.sqrt(da * db) : 1;
}
const lookalikes = [];
const closeToToday = [];
const pairsByRound = {};
if (masses.today) for (const id of tested) {
  if (id === 'today' || !masses[id] || (rungs[id] || 0) < 7) continue;
  const c = corr(masses.today, masses[id]);
  if (c >= squintLimit) closeToToday.push({ id, correlation: +c.toFixed(3) });
}
const scored = tested.filter((id) => masses[id] && roundOf(id) !== 'today');
for (let i = 0; i < scored.length; i++) for (let j = i + 1; j < scored.length; j++) {
  const a = scored[i], b = scored[j];
  if (roundOf(a) !== roundOf(b)) continue;
  if (Math.max(rungs[a] || 0, rungs[b] || 0) < 4) continue; // Refine options share today's skeleton by design
  const c = +corr(masses[a], masses[b]).toFixed(3);
  (pairsByRound[roundOf(a)] ||= []).push({ pair: [a, b], correlation: c });
  if (c >= squintLimit) lookalikes.push({ pair: [a, b], correlation: c });
}
const nearest = Object.fromEntries(Object.entries(pairsByRound).map(([k, v]) => [k, v.sort((x, y) => y.correlation - x.correlation).slice(0, 3)]));

let overview = null;
let overviewError = null;
if (shots) {
  // Overview contact sheet from a fresh page, so frames show first screens rather than the clicked-through state.
  // Chromium neither loads lazy frames nor paints sandboxed frames outside the viewport, so the viewport is grown to
  // the page height and every frame is waited for before the capture. Blank tiles are reported, not ignored.
  const sheet = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  try {
    await sheet.goto(url);
    await sheet.waitForFunction(() => !!window.DV_GALLERY, null, { timeout });
    await sheet.evaluate((round) => {
      document.querySelectorAll('.dv-round').forEach((r) => r.classList.toggle('dv-collapsed', !!round && r.dataset.round !== round));
      document.querySelector('[data-dv-view="grid"]')?.click();
      window.DV_GALLERY.mountAll();
    }, onlyRound);
    await sheet.waitForTimeout(100);
    const h = await sheet.evaluate(() => document.documentElement.scrollHeight);
    if (h > 16000) overviewError = `the page is ${h}px tall; the overview stops at 16000px`;
    await sheet.setViewportSize({ width: 1600, height: Math.min(h, 16000) });
    const want = await sheet.$$eval('.dv-option[id]', (as) => as.filter((a) => a.checkVisibility()).map((a) => a.id));
    const until = Date.now() + timeout;
    const late = [];
    for (const id of want) {
      const fr = await frameOf(sheet.locator(`[id="${id}"]`));
      const ok = fr && await fr.waitForFunction(() => document.readyState === 'complete' && 'DV_STATE' in window, null, { timeout: Math.max(1, until - Date.now()) }).then(() => true, () => false);
      if (ok) await settle(fr); else late.push(id);
    }
    await sheet.waitForTimeout(300);
    const path = join(shots, '_overview.png');
    const png = await sheet.screenshot({ path, fullPage: true });
    overview = path;
    const tiles = await sheet.$$eval('.dv-option[id]', (as, want) => as.filter((a) => want.includes(a.id)).map((a) => {
      const r = a.querySelector('.dv-frame').getBoundingClientRect();
      return { id: a.id, x: Math.round(r.left + window.scrollX), y: Math.round(r.top + window.scrollY), w: Math.round(r.width), h: Math.round(r.height) };
    }).filter((t) => t.w > 8 && t.h > 8 && t.y + t.h <= 16000), want);
    const grids = tiles.length ? await gridsOf(png, tiles) : [];
    const blank = tiles.filter((t, i) => spread(grids[i]) < 1.5 && (!masses[t.id] || spread(masses[t.id]) >= 1.5)).map((t) => t.id);
    const problems = [];
    if (late.length) problems.push(`frames that did not finish loading: ${late.join(', ')}`);
    if (blank.length) problems.push(`blank tiles: ${blank.join(', ')}`);
    if (problems.length) overviewError = [overviewError, problems.join('; ') + '. Use the per-option shots for these.'].filter(Boolean).join('; ');
  } catch (e) {
    overviewError = 'overview not saved: ' + String((e && e.message) || e).split('\n')[0].slice(0, 200);
  }
  await sheet.close().catch(() => {});
  if (overviewError) console.error('smoke: ' + overviewError);
}
await browser.close();

const failing = results.filter((r) => r.error || !r.loaded || r.controls === 0 || r.dead.length > 0 || r.overflow || r.hiddenRenders.length > 0
  || Object.values(r.states || {}).some((s) => (s.errors && s.errors.length) || s.hiddenRenders || s.overflow));
const warned = results.filter((r) => r.blankFirstScreen || r.covered.length || r.clipped.length || Object.values(r.states || {}).some((s) => s.covered || s.clipped));
const report = {
  gallery: file,
  frameWidth: frameWidth || 'design size',
  round: onlyRound || 'all',
  states: withStates,
  options: results.length,
  passed: results.length - failing.length,
  failing: failing.map((r) => r.id),
  warned: warned.map((r) => r.id),
  seconds: Math.round((Date.now() - started) / 1000),
  galleryConsoleErrors: consoleErrors.slice(0, 20),
  squint: { limit: squintLimit, lookalikes, closeToToday, nearest, note: 'lookalikes: Evolve-or-higher pairs whose first screens share a light/dark block pattern. closeToToday: Rethink and Reinvent options whose first screen looks like today. nearest: the three closest pairs in each round, whatever their score. A heuristic on first screens only: check pairs side by side; redraw one against an explicit ban if it is the same idea.' },
  overview,
  overviewError,
  checks: 'Fails: load errors, no controls, dead buttons (including toggles whose press flips their state but changes nothing visible), hidden elements that still render, sideways overflow with --frame-width, and errors in a state with --states. Warns (exit code unchanged): a blank first screen, controls whose centre is covered, and cut-off text or placeholders. All are heuristics: report them as what the smoke test found, not as proof.',
  results,
};
console.log(JSON.stringify(report, null, 2));
process.exit(failing.length || !results.length ? 1 : 0);
