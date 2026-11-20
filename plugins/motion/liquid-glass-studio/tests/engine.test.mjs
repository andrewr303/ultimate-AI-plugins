// Tests for examples/glass-lab/liquid-glass.js (pure math + filter markup).
// Run: node --test tests/engine.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  PROFILES,
  convexCircle,
  convexSquircle,
  concave,
  lip,
  refractionProfile,
  displacementField,
  specularField,
  roundedRectSDF,
  encodeDisplacement,
  decodeDisplacement,
  NEUTRAL,
  NEUTRAL_BIAS,
  buildFilterMarkup,
  detectTier,
  explainTier,
  detectEngine,
  capabilities,
  createGlass,
  clearGlassCache,
  SOLID_SURFACES_ATTRIBUTE,
  BASE_STYLES,
  BASE_STYLES_ID,
} from '../examples/glass-lab/liquid-glass.js';

const grid = (n = 101) => Array.from({ length: n }, (_, i) => i / (n - 1));

test('module imports in Node without a DOM', () => {
  assert.equal(typeof globalThis.document, 'undefined');
  const caps = capabilities(undefined);
  assert.equal(caps.engine, 'unknown');
  assert.equal(caps.supportsBackdrop, false);
});

test('profiles: range, endpoints and flat inner end', () => {
  for (const [name, h] of Object.entries(PROFILES)) {
    for (const t of grid()) {
      const v = h(t);
      assert.ok(Number.isFinite(v), `${name}(${t}) finite`);
      assert.ok(v >= -1e-12 && v <= 1 + 1e-12, `${name}(${t}) = ${v} in [0,1]`);
    }
    // zero slope where the bezel meets the interior, so no seam
    const e = 1e-4;
    const slope = (h(1) - h(1 - e)) / e;
    assert.ok(Math.abs(slope) < 0.05, `${name} slope at t=1 is ${slope}`);
  }
  assert.equal(convexCircle(0), 0);
  assert.equal(convexCircle(1), 1);
  assert.equal(convexSquircle(0), 0);
  assert.equal(convexSquircle(1), 1);
  assert.equal(concave(0), 1);
  assert.equal(concave(1), 0);
  assert.equal(lip(0), 0);
  assert.ok(Math.abs(lip(1) - 0.5) < 1e-12);
});

test('profiles: convex shapes are monotone increasing, concave decreasing', () => {
  const ts = grid(201);
  for (const [name, h, sign] of [
    ['convexCircle', convexCircle, 1],
    ['convexSquircle', convexSquircle, 1],
    ['concave', concave, -1],
  ]) {
    for (let i = 1; i < ts.length; i++) {
      assert.ok(sign * (h(ts[i]) - h(ts[i - 1])) >= -1e-12, `${name} monotone at ${ts[i]}`);
    }
  }
  // squircle rises faster than the circle near the edge
  assert.ok(convexSquircle(0.1) > convexCircle(0.1));
  // lip is a raised ring: interior max above the plateau
  const peak = Math.max(...ts.map(lip));
  assert.ok(peak > lip(1) + 0.1);
});

test('refraction: zero at the outer edge and at the interior, no NaN', () => {
  for (const profile of Object.keys(PROFILES)) {
    const d = refractionProfile({ profile, samples: 257 });
    assert.equal(d.length, 257);
    for (const v of d) assert.ok(Number.isFinite(v));
    assert.ok(Math.abs(d[0]) < 1e-3, `${profile} edge offset ${d[0]}`); // numeric slope: within 0.001 px
    assert.ok(Math.abs(d[d.length - 1]) < 1e-9, `${profile} interior offset ${d[d.length - 1]}`);
  }
});

test('refraction: convex bends inward, concave outward, ior 1 bends nothing', () => {
  const conv = refractionProfile({ profile: 'convexCircle', samples: 65 });
  const conc = refractionProfile({ profile: 'concave', samples: 65 });
  assert.ok(conv.slice(1, -1).every((v) => v > 0));
  assert.ok(conc.slice(1, -1).every((v) => v <= 0));
  assert.ok(refractionProfile({ ior: 1, samples: 33 }).every((v) => v === 0));
  // more index of refraction = more bending
  const lo = Math.max(...refractionProfile({ ior: 1.2 }));
  const hi = Math.max(...refractionProfile({ ior: 1.8 }));
  assert.ok(hi > lo);
});

test('refraction: convex profiles are unimodal (rise, then fall monotonically to zero)', () => {
  for (const profile of ['convexCircle', 'convexSquircle']) {
    const d = refractionProfile({ profile, samples: 257 });
    let peak = 0;
    for (let i = 1; i < d.length; i++) if (d[i] > d[peak]) peak = i;
    for (let i = peak + 1; i < d.length; i++) assert.ok(d[i] <= d[i - 1] + 1e-9, `${profile} falls after peak at ${i}`);
    for (let i = 1; i <= peak; i++) assert.ok(d[i] >= d[i - 1] - 1e-9, `${profile} rises before peak at ${i}`);
  }
});

test('refraction: steep walls saturate at sqrt(ior^2 - 1) per px of height', () => {
  // A vertical wall bends a vertical ray to the critical direction, so
  // offset / height approaches sqrt(n^2 - 1); it must never exceed it.
  const ior = 1.5;
  const limit = Math.sqrt(ior * ior - 1);
  const thickness = 50;
  const d = refractionProfile({ profile: 'convexCircle', thickness, bezelWidth: 1, ior, samples: 1001 });
  for (let i = 0; i < d.length; i++) {
    const height = thickness * convexCircle(i / (d.length - 1));
    if (height > 0) assert.ok(d[i] / height <= limit + 1e-9);
  }
});

test('encoding: neutral is 128 and round trip is within half a step', () => {
  assert.equal(NEUTRAL, 128);
  assert.ok(Math.abs(NEUTRAL_BIAS - 1 / 510) < 1e-15);
  assert.notEqual(NEUTRAL / 255, 0.5); // the reason the bias exists
  assert.equal(encodeDisplacement(0, 10), 128);
  assert.equal(decodeDisplacement(128, 10), 0);
  assert.equal(encodeDisplacement(10, 10), 255);
  assert.equal(encodeDisplacement(-10, 10), 1);
  const max = 17.3;
  const step = max / 127;
  for (let v = -max; v <= max; v += 0.37) {
    const back = decodeDisplacement(encodeDisplacement(v, max), max);
    assert.ok(Math.abs(back - v) <= step / 2 + 1e-9, `round trip ${v} -> ${back}`);
  }
  // symmetric rounding: encode(-v) - 128 === -(encode(v) - 128)
  for (let v = 0; v <= max; v += 0.5 * step) {
    assert.equal(encodeDisplacement(-v, max) - 128, 0 - (encodeDisplacement(v, max) - 128));
  }
  // without the bias the neutral pixel would move content by scale/510 px
  const scale = (max * 255) / 127;
  assert.ok(Math.abs(scale * (128 / 255 - 0.5) - scale / 510) < 1e-12);
});

test('sdf: sign and corner radius', () => {
  assert.ok(roundedRectSDF(0, 0, 50, 30, 10) < 0);
  assert.ok(Math.abs(roundedRectSDF(50, 0, 50, 30, 10)) < 1e-12);
  assert.ok(roundedRectSDF(60, 0, 50, 30, 10) > 0);
  // corner: distance from the corner circle center minus radius
  const c = roundedRectSDF(50, 30, 50, 30, 10);
  assert.ok(Math.abs(c - (Math.SQRT2 * 10 - 10)) < 1e-9);
  // squircle corner is "fuller" than the circle (point on the diagonal is inside or nearer)
  assert.ok(roundedRectSDF(47.5, 27.5, 50, 30, 10, 'squircle') < roundedRectSDF(47.5, 27.5, 50, 30, 10));
});

function fieldAt(f, i, j) {
  const p = (j * f.width + i) * 4;
  return [f.data[p], f.data[p + 1], f.data[p + 2], f.data[p + 3]];
}

test('displacement field: size, neutral outside and center, no NaN', () => {
  const f = displacementField({ width: 160, height: 100, radius: 24, pixelRatio: 2 });
  assert.equal(f.width, 320);
  assert.equal(f.height, 200);
  assert.equal(f.data.length, 320 * 200 * 4);
  assert.equal(f.neutral, 128);
  assert.ok(Number.isFinite(f.maxDisplacement) && f.maxDisplacement > 0);
  assert.ok(Math.abs(f.filterScale - (f.maxDisplacement * 255) / 127) < 1e-9);
  for (let k = 0; k < f.data.length; k += 4) {
    assert.equal(f.data[k + 2], 128);
    assert.equal(f.data[k + 3], 255);
  }
  // center of the plateau and the very corner pixel (outside the rounded shape) are neutral
  assert.deepEqual(fieldAt(f, 160, 100).slice(0, 2), [128, 128]);
  assert.deepEqual(fieldAt(f, 0, 0).slice(0, 2), [128, 128]);
  // edge midpoint row: left rim samples to the right (R > 128), right rim to the left
  const row = 100;
  const left = Math.max(...Array.from({ length: 40 }, (_, i) => fieldAt(f, i, row)[0]));
  const right = Math.min(...Array.from({ length: 40 }, (_, i) => fieldAt(f, 319 - i, row)[0]));
  assert.ok(left > 128 && right < 128);
});

test('displacement field: mirror symmetry in x and y (corners match)', () => {
  for (const shape of ['rounded', 'squircle']) {
    for (const profile of Object.keys(PROFILES)) {
      const f = displacementField({ width: 97, height: 61, radius: 18, bezelWidth: 20, pixelRatio: 1.5, shape, profile });
      for (let j = 0; j < f.height; j++) {
        for (let i = 0; i < f.width; i++) {
          const [r, g] = fieldAt(f, i, j);
          const [rx, gx] = fieldAt(f, f.width - 1 - i, j);
          const [ry, gy] = fieldAt(f, i, f.height - 1 - j);
          assert.equal(r - 128, 0 - (rx - 128), `${shape}/${profile} x-mirror R at ${i},${j}`);
          assert.equal(g, gx, `${shape}/${profile} x-mirror G at ${i},${j}`);
          assert.equal(g - 128, 0 - (gy - 128), `${shape}/${profile} y-mirror G at ${i},${j}`);
          assert.equal(r, ry, `${shape}/${profile} y-mirror R at ${i},${j}`);
        }
      }
    }
  }
});

test('displacement field: fold guard keeps the Jacobian positive', () => {
  for (const profile of Object.keys(PROFILES)) {
    for (const [bezelWidth, thickness, radius] of [
      [28, 40, 24],
      [12, 80, 0],
      [40, 120, 60],
    ]) {
      const f = displacementField({ width: 200, height: 120, radius, bezelWidth, thickness, profile });
      assert.ok(f.minJacobian >= 0.2 - 1e-6, `${profile} ${bezelWidth}/${thickness} minJ ${f.minJacobian}`);
      assert.ok(f.attenuation > 0 && f.attenuation <= 1);
      assert.ok(Number.isFinite(f.maxDisplacement));
    }
  }
  // turning the guard off keeps full amplitude and may fold
  const wild = displacementField({ width: 200, height: 120, radius: 0, bezelWidth: 12, thickness: 80, minJacobian: -Infinity });
  assert.equal(wild.attenuation, 1);
  // headroom for chromatic aberration lowers amplitude, never raises it
  const a = displacementField({ width: 200, height: 120, thickness: 80 });
  const b = displacementField({ width: 200, height: 120, thickness: 80, foldHeadroom: 1.4 });
  assert.ok(b.maxDisplacement <= a.maxDisplacement + 1e-9);
});

test('displacement field: bezel clamps to the short half side (pill center stays neutral)', () => {
  const f = displacementField({ width: 220, height: 48, radius: 24, bezelWidth: 80, pixelRatio: 1 });
  assert.equal(f.bezelWidth, 24);
  // center row of the straight middle segment is neutral in y
  for (let i = 40; i < 180; i++) assert.equal(fieldAt(f, i, 24)[1] === 128 || fieldAt(f, i, 23)[1] + fieldAt(f, i, 24)[1] === 256, true);
});

test('displacement field: degenerate inputs stay finite', () => {
  for (const o of [
    { width: 1, height: 1 },
    { width: 0, height: 0 },
    { width: 50, height: 50, radius: 999, bezelWidth: 0, thickness: 0 },
    { width: 40, height: 20, ior: 0.5 },
    { width: 40, height: 20, scale: 0 },
  ]) {
    const f = displacementField(o);
    assert.ok(Number.isFinite(f.maxDisplacement));
    assert.ok(Number.isFinite(f.filterScale));
    for (const v of f.data) assert.ok(v >= 0 && v <= 255);
  }
});

test('specular field: lit rim only, brighter on the light side', () => {
  const s = specularField({ width: 120, height: 80, radius: 20, lightAngle: 90, intensity: 1, rimWidth: 3 });
  const alpha = (i, j) => s.data[(j * s.width + i) * 4 + 3];
  assert.equal(alpha(60, 40), 0); // interior
  assert.equal(alpha(0, 0), 0); // outside the rounded corner
  const top = alpha(60, 0);
  const side = alpha(0, 40);
  assert.ok(top > 0 && top > side, `top ${top} side ${side}`);
  const bottom = alpha(60, 79);
  assert.ok(bottom > 0 && bottom < top, `opposite rim weaker: ${bottom} < ${top}`);
  for (const v of s.data) assert.ok(Number.isFinite(v));
});

// Tiny well-formedness check: balanced tags, quoted attributes, no stray text.
function parseTags(xml) {
  const stack = [];
  const nodes = [];
  const re = /<(\/?)([A-Za-z][\w:-]*)((?:\s+[\w:-]+="[^"<]*")*)\s*(\/?)>/gy;
  let pos = 0;
  while (pos < xml.length) {
    re.lastIndex = pos;
    const m = re.exec(xml);
    assert.ok(m, `unparsable markup at ${pos}: ${xml.slice(pos, pos + 40)}`);
    const [all, close, name, attrText, self] = m;
    const attrs = Object.fromEntries([...attrText.matchAll(/([\w:-]+)="([^"]*)"/g)].map((a) => [a[1], a[2]]));
    if (close) assert.equal(stack.pop(), name, `closing ${name}`);
    else {
      nodes.push({ name, attrs });
      if (!self) stack.push(name);
    }
    pos += all.length;
  }
  assert.equal(stack.length, 0, 'all tags closed');
  return nodes;
}

const MAP = 'data:image/png;base64,AAAA';
const SPEC = 'data:image/png;base64,BBBB';

test('filter markup: single pass is well formed and reads x=R, y=G', () => {
  const xml = buildFilterMarkup({ id: 'g1', mapHref: MAP, specularHref: SPEC, width: 200, height: 80, scale: 24 });
  const nodes = parseTags(xml);
  const filter = nodes[0];
  assert.equal(filter.name, 'filter');
  assert.equal(filter.attrs.id, 'g1');
  assert.equal(filter.attrs['color-interpolation-filters'], 'sRGB');
  assert.equal(filter.attrs.filterUnits, 'userSpaceOnUse');
  assert.deepEqual([filter.attrs.x, filter.attrs.y, filter.attrs.width, filter.attrs.height], ['0', '0', '200', '80']);
  const disp = nodes.filter((n) => n.name === 'feDisplacementMap');
  assert.equal(disp.length, 1);
  assert.equal(disp[0].attrs.xChannelSelector, 'R');
  assert.equal(disp[0].attrs.yChannelSelector, 'G');
  assert.equal(disp[0].attrs.in2, 'map');
  assert.equal(disp[0].attrs.scale, '24');
  // neutral correction feeds the displacement
  const corr = nodes.find((n) => n.name === 'feColorMatrix' && n.attrs.result === 'map');
  assert.ok(corr && corr.attrs.in === 'mapRaw');
  const vals = corr.attrs.values.split(/\s+/).map(Number);
  assert.equal(vals.length, 20);
  assert.ok(Math.abs(vals[4] + 1 / 510) < 1e-4 && Math.abs(vals[9] + 1 / 510) < 1e-4);
  // feImage stretched to the box
  for (const img of nodes.filter((n) => n.name === 'feImage')) {
    assert.equal(img.attrs.preserveAspectRatio, 'none');
    assert.equal(img.attrs.width, '200');
  }
  assert.ok(nodes.some((n) => n.name === 'feBlend' && n.attrs.mode === 'screen' && n.attrs.in2 === 'refracted'));
});

test('filter markup: chromatic aberration uses three R/G passes and restores alpha', () => {
  const xml = buildFilterMarkup({ id: 'g2', mapHref: MAP, width: 100, height: 50, scale: 20, chromaticAberration: 0.2, blur: 2, saturation: 1.4 });
  const nodes = parseTags(xml);
  const byResult = Object.fromEntries(nodes.filter((n) => n.attrs.result).map((n) => [n.attrs.result, n]));
  const disp = nodes.filter((n) => n.name === 'feDisplacementMap');
  assert.equal(disp.length, 3);
  for (const d of disp) {
    assert.equal(d.attrs.xChannelSelector, 'R');
    assert.equal(d.attrs.yChannelSelector, 'G'); // never B (see liquid-glass-react src/index.tsx)
    assert.equal(d.attrs.in, 'sat'); // frost and saturation run first
  }
  assert.deepEqual(disp.map((d) => Number(d.attrs.scale)), [16, 20, 24]); // blue bends most
  // each channel image keeps exactly one color channel and forces alpha to 1
  const keepRow = { cR: 0, cG: 1, cB: 2 };
  for (const [name, row] of Object.entries(keepRow)) {
    const m = byResult[name].attrs.values.split(/\s+/).map(Number);
    for (let r = 0; r < 3; r++) {
      const sum = m.slice(r * 5, r * 5 + 5).reduce((a, b) => a + b, 0);
      assert.equal(sum, r === row ? 1 : 0, `${name} row ${r}`);
    }
    assert.deepEqual(m.slice(15), [0, 0, 0, 0, 1]);
  }
  assert.equal(byResult.cRG.attrs.operator, 'arithmetic');
  assert.equal(byResult.cRGB.attrs.operator, 'arithmetic');
  assert.equal(byResult.refracted.attrs.operator, 'in');
  assert.equal(byResult.refracted.attrs.in2, 'dG');
  assert.equal(byResult.frost.attrs.stdDeviation, '2');
  // every `in`/`in2` refers to a defined result or a standard input
  const defined = new Set(['SourceGraphic', 'SourceAlpha']);
  for (const n of nodes) {
    for (const k of ['in', 'in2']) if (n.attrs[k]) assert.ok(defined.has(n.attrs[k]), `${n.name} ${k}=${n.attrs[k]}`);
    if (n.attrs.result) defined.add(n.attrs.result);
  }
});

test('filter markup: rejects unsafe ids and escapes hrefs', () => {
  assert.throws(() => buildFilterMarkup({ id: 'a b', mapHref: MAP }));
  assert.throws(() => buildFilterMarkup({ id: ':r0:', mapHref: MAP }));
  assert.throws(() => buildFilterMarkup({ id: 'ok' }));
  const xml = buildFilterMarkup({ id: 'ok', mapHref: 'x"y<z', width: 10, height: 10, scale: 1 });
  assert.ok(xml.includes('x&quot;y&lt;z'));
  parseTags(xml);
});

test('tier decision table', () => {
  const base = { reducedTransparency: false, contrastMore: false, forcedColors: false, supportsBackdrop: true, engine: 'chromium' };
  const rows = [
    [{}, 'refract'],
    [{ engine: 'webkit' }, 'frost'],
    [{ engine: 'gecko' }, 'frost'],
    [{ engine: 'unknown' }, 'frost'],
    [{ supportsBackdrop: false }, 'solid'],
    [{ supportsBackdrop: false, engine: 'webkit' }, 'solid'],
    [{ reducedTransparency: true }, 'solid'],
    [{ contrastMore: true }, 'solid'],
    [{ forcedColors: true }, 'solid'],
    [{ forcedColors: true, engine: 'gecko' }, 'solid'],
    [{ preferred: 'frost' }, 'frost'],
    [{ preferred: 'solid' }, 'solid'],
    [{ preferred: 'refract', engine: 'webkit' }, 'frost'], // overrides cannot raise
    [{ preferred: 'refract', reducedTransparency: true }, 'solid'],
    [{ preferred: 'auto' }, 'refract'],
    [{ preferred: 'bogus' }, 'refract'],
  ];
  for (const [delta, want] of rows) {
    assert.equal(detectTier({ ...base, ...delta }), want, JSON.stringify(delta));
  }
  assert.equal(detectTier(), 'frost'); // unknown engine by default
  assert.match(explainTier({ ...base, contrastMore: true }).reason, /contrast/);
});

test('engine detection from user agents', () => {
  const ua = {
    chrome: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    edge: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
    safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15',
    iosChrome: 'Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/141.0 Mobile/15E148 Safari/604.1',
    firefox: 'Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0',
  };
  assert.equal(detectEngine({ userAgent: ua.chrome }), 'chromium');
  assert.equal(detectEngine({ userAgent: ua.edge }), 'chromium');
  assert.equal(detectEngine({ userAgent: ua.safari, vendor: 'Apple Computer, Inc.' }), 'webkit');
  assert.equal(detectEngine({ userAgent: ua.iosChrome }), 'webkit');
  assert.equal(detectEngine({ userAgent: ua.firefox }), 'gecko');
  assert.equal(detectEngine({ userAgent: 'x', userAgentData: { brands: [{ brand: 'Chromium', version: '141' }] } }), 'chromium');
  assert.equal(detectEngine(undefined), 'unknown');
  assert.equal(detectEngine({ userAgent: 'curl/8' }), 'unknown');
});

test('displacement field: fixed 1 CSS px edge fade, at least one device pixel, at most half the bezel', () => {
  for (const profile of Object.keys(PROFILES)) {
    for (const pixelRatio of [0.5, 1, 2, 3]) {
      const f = displacementField({ width: 200, height: 120, radius: 24, bezelWidth: 28, profile, pixelRatio });
      assert.equal(f.fadeBand, Math.max(1 / pixelRatio, 1), `${profile} at ${pixelRatio}x`);
    }
  }
  assert.equal(displacementField({ width: 200, height: 120, bezelWidth: 1 }).fadeBand, 0.5);
  // The fade acts: on the left edge midpoint row the outermost map pixel bends less than the next one.
  for (const profile of ['convexCircle', 'convexSquircle', 'lip']) {
    for (const pixelRatio of [1, 2]) {
      const f = displacementField({ width: 200, height: 120, radius: 24, bezelWidth: 28, profile, pixelRatio });
      const row = Math.floor(f.height / 2);
      const off = (i) => Math.abs(fieldAt(f, i, row)[0] - 128);
      assert.ok(off(0) < off(1), `${profile} at ${pixelRatio}x: edge ${off(0)} < next ${off(1)}`);
    }
  }
});

test('tier decision: the page solid surfaces setting forces solid', () => {
  const base = { reducedTransparency: false, contrastMore: false, forcedColors: false, supportsBackdrop: true, engine: 'chromium' };
  assert.deepEqual(explainTier({ ...base, solidSurfaces: true }), { tier: 'solid', reason: 'the user turned on solid surfaces' });
  assert.equal(detectTier({ ...base, solidSurfaces: true, preferred: 'refract' }), 'solid');
  assert.equal(detectTier({ ...base, solidSurfaces: true, engine: 'webkit' }), 'solid');
  assert.match(explainTier({ ...base, solidSurfaces: true, forcedColors: true }).reason, /forced colors/);
  assert.equal(SOLID_SURFACES_ATTRIBUTE, 'data-glass-surfaces');
});

/* ------------------------------------------------------------------------ */
/* createGlass in a small fake DOM                                           */
/* ------------------------------------------------------------------------ */
// Just enough browser surface for createGlass: style declarations,
// attributes, matchMedia with change events, requestAnimationFrame, a
// MutationObserver on <html>, a canvas that encodes nothing, Image.decode,
// DOMParser and importNode. Real rendering is checked in Chromium by the lab
// run documented in examples/glass-lab/README.md.

const UA = {
  chromium: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
  webkit: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15',
};

class FakeStyle {
  constructor() { this.props = new Map(); this.cssText = ''; }
  setProperty(name, value) { if (value === '' || value == null) this.props.delete(name); else this.props.set(name, String(value)); }
  getPropertyValue(name) { return this.props.get(name) ?? ''; }
  removeProperty(name) { const v = this.getPropertyValue(name); this.props.delete(name); return v; }
}

function makeEnv({ engine = 'chromium', dpr = 1 } = {}) {
  const env = { active: true, raf: [], rafId: 0, mqls: [], observers: [], canvasThrows: false, warnings: [] };
  class El {
    constructor(tag) {
      this.tagName = tag;
      this.style = new FakeStyle();
      this.attrs = new Map();
      this.children = [];
      this.parentElement = null;
      this.parentNode = null;
      this.dataset = {};
      this.listeners = new Map();
      this.offsetWidth = 0;
      this.offsetHeight = 0;
      this.textContent = '';
      this.id = '';
    }
    get isConnected() { return env.active; }
    get childNodes() { return this.children; }
    getAttribute(n) { return this.attrs.has(n) ? this.attrs.get(n) : null; }
    hasAttribute(n) { return this.attrs.has(n); }
    setAttribute(n, v) { this.attrs.set(n, String(v)); this.notify(n); }
    removeAttribute(n) { this.attrs.delete(n); this.notify(n); }
    notify(name) {
      for (const o of env.observers) {
        if (o.target === this && (!o.filter || o.filter.includes(name))) queueMicrotask(() => o.cb([{ type: 'attributes', attributeName: name }]));
      }
    }
    addEventListener(t, f) { if (!this.listeners.has(t)) this.listeners.set(t, new Set()); this.listeners.get(t).add(f); }
    removeEventListener(t, f) { this.listeners.get(t)?.delete(f); }
    appendChild(c) { c.parentNode = this; c.parentElement = this; this.children.push(c); return c; }
    removeChild(c) { this.children = this.children.filter((x) => x !== c); c.parentNode = null; c.parentElement = null; return c; }
    remove() { if (this.parentNode) this.parentNode.removeChild(this); }
    getBoundingClientRect() { return { left: 0, top: 0, width: this.offsetWidth, height: this.offsetHeight }; }
  }
  const html = new El('html');
  const head = html.appendChild(new El('head'));
  const body = html.appendChild(new El('body'));
  const find = (node, id) => {
    if (node.id === id) return node;
    for (const c of node.children) { const hit = find(c, id); if (hit) return hit; }
    return null;
  };
  let pngCount = 0;
  const document = {
    documentElement: html,
    head,
    body,
    createElement(tag) {
      const el = new El(tag);
      if (tag === 'canvas') {
        el.getContext = () => {
          if (env.canvasThrows) throw new Error('canvas unavailable');
          return { putImageData() {} };
        };
        el.toDataURL = () => `data:image/png;base64,${++pngCount}`;
      }
      return el;
    },
    createElementNS: (ns, tag) => new El(tag),
    getElementById: (id) => find(html, id),
    importNode: (n) => n,
  };
  const prefs = new Set();
  const win = {
    document,
    navigator: { userAgent: UA[engine], vendor: engine === 'webkit' ? 'Apple Computer, Inc.' : 'Google Inc.' },
    devicePixelRatio: dpr,
    CSS: { supports: () => true },
    matchMedia(q) {
      const m = {
        media: q,
        listeners: new Set(),
        get matches() {
          const r = /resolution: ([\d.]+)dppx/.exec(q);
          return r ? Number(r[1]) === win.devicePixelRatio : prefs.has(q);
        },
        addEventListener(t, f) { if (t === 'change') this.listeners.add(f); },
        removeEventListener(t, f) { if (t === 'change') this.listeners.delete(f); },
        dispatch() { for (const f of [...this.listeners]) f({ matches: this.matches, media: q }); },
      };
      env.mqls.push(m);
      return m;
    },
    requestAnimationFrame(cb) { const id = ++env.rafId; env.raf.push([id, cb]); return id; },
    cancelAnimationFrame(id) { env.raf = env.raf.filter(([i]) => i !== id); },
    MutationObserver: class {
      constructor(cb) { this.cb = cb; }
      observe(target, o) { this.target = target; this.filter = o.attributeFilter; env.observers.push(this); }
      disconnect() { env.observers = env.observers.filter((x) => x !== this); }
    },
  };
  const globals = {
    window: win,
    document,
    getComputedStyle: () => ({ borderTopLeftRadius: '0px', opacity: '1', filter: 'none', backdropFilter: 'none', maskImage: 'none', clipPath: 'none', mixBlendMode: 'normal', willChange: 'auto' }),
    Image: class { decode() { return Promise.resolve(); } },
    ImageData: class { constructor(data, w, h) { Object.assign(this, { data, width: w, height: h }); } },
    DOMParser: class {
      parseFromString(text) {
        const filter = new El('filter');
        filter.id = (/id="([^"]+)"/.exec(text) || [])[1] || '';
        filter.markup = text;
        return { querySelector: () => null, documentElement: { firstElementChild: filter } };
      }
    },
  };
  const saved = {};
  const warn = console.warn;
  env.install = () => {
    for (const [k, v] of Object.entries(globals)) { saved[k] = Object.getOwnPropertyDescriptor(globalThis, k); globalThis[k] = v; }
    console.warn = (...args) => env.warnings.push(args);
    clearGlassCache();
  };
  env.uninstall = () => {
    env.active = false;
    for (const k of Object.keys(globals)) { if (saved[k]) Object.defineProperty(globalThis, k, saved[k]); else delete globalThis[k]; }
    console.warn = warn;
  };
  env.settle = async () => {
    for (let i = 0; i < 12; i++) {
      const q = env.raf.splice(0);
      for (const [, cb] of q) cb(0);
      await new Promise((r) => setImmediate(r));
    }
  };
  env.el = (w, h, parent = body) => {
    const e = new El('div');
    e.offsetWidth = w;
    e.offsetHeight = h;
    parent.appendChild(e);
    return e;
  };
  env.html = html;
  env.head = head;
  env.body = body;
  env.win = win;
  return env;
}

async function withEnv(opts, fn) {
  const env = makeEnv(opts);
  env.install();
  try {
    await fn(env);
  } finally {
    env.uninstall();
  }
}

test('createGlass: info reports CSS px size and map px separately at pixel ratio 2', async () => {
  await withEnv({ engine: 'chromium', dpr: 2 }, async (env) => {
    const el = env.el(40, 24);
    const seen = [];
    const g = createGlass(el, { onRender: (i) => seen.push(i) });
    await env.settle();
    assert.equal(g.tier, 'refract');
    const info = g.info;
    assert.equal(seen.at(-1), info);
    assert.deepEqual([info.width, info.height, info.pixelRatio], [40, 24, 2]);
    assert.deepEqual([info.mapWidth, info.mapHeight], [80, 48]);
    assert.match(el.style.getPropertyValue('backdrop-filter'), /^url\(#lgs-\d+-\d+\)$/);
    assert.equal(el.style.getPropertyValue('-webkit-backdrop-filter'), 'none');
    g.destroy();
    assert.equal(el.style.getPropertyValue('backdrop-filter'), '');
    assert.equal(el.getAttribute('data-glass-tier'), null);
  });
});

test('createGlass: frost tier is styled by the injected :where() sheet, not inline backdrop-filter', async () => {
  await withEnv({ engine: 'webkit' }, async (env) => {
    const el = env.el(120, 60);
    const g = createGlass(el, { frostBlur: 18, saturation: 1.3 });
    await env.settle();
    assert.equal(g.tier, 'frost');
    assert.equal(el.getAttribute('data-glass-tier'), 'frost');
    assert.equal(el.style.getPropertyValue('backdrop-filter'), '');
    assert.equal(el.style.getPropertyValue('-webkit-backdrop-filter'), '');
    assert.equal(el.style.getPropertyValue('--lg-frost-blur'), '18px');
    assert.equal(el.style.getPropertyValue('--lg-saturation'), '1.3');
    const sheet = env.win.document.getElementById(BASE_STYLES_ID);
    assert.ok(sheet && sheet.tagName === 'style', 'one <style id="lgs-base-styles"> is injected');
    assert.equal(sheet.textContent, BASE_STYLES);
    for (const rule of BASE_STYLES.split('}').map((r) => r.trim()).filter(Boolean)) {
      assert.match(rule, /^:where\(/, `zero-specificity rule: ${rule.split('{')[0]}`);
    }
    assert.match(BASE_STYLES, /var\(--lg-frost-blur/);
    assert.match(BASE_STYLES, /var\(--lg-saturation/);
    const second = createGlass(env.el(50, 50));
    await env.settle();
    assert.equal(env.head.children.filter((c) => c.id === BASE_STYLES_ID).length, 1, 'injected once');
    g.update({ frostBlur: 22 });
    await env.settle();
    assert.equal(el.style.getPropertyValue('--lg-frost-blur'), '22px');
    g.destroy();
    assert.equal(el.style.getPropertyValue('--lg-frost-blur'), '');
    assert.ok(env.win.document.getElementById(BASE_STYLES_ID), 'kept while another instance lives');
    second.destroy();
    assert.equal(env.win.document.getElementById(BASE_STYLES_ID), null, 'removed with the last instance');
  });
});

test('createGlass: a page that ships its own #lgs-base-styles gets no second sheet', async () => {
  await withEnv({ engine: 'webkit' }, async (env) => {
    const own = env.win.document.createElement('style');
    own.id = BASE_STYLES_ID;
    env.head.appendChild(own);
    const g = createGlass(env.el(60, 30));
    await env.settle();
    assert.equal(env.head.children.filter((c) => c.id === BASE_STYLES_ID).length, 1);
    g.destroy();
    assert.equal(env.win.document.getElementById(BASE_STYLES_ID), own, 'the page sheet is left alone');
  });
});

test('createGlass: <html data-glass-surfaces="solid"> switches the tier live', async () => {
  await withEnv({ engine: 'chromium' }, async (env) => {
    const el = env.el(80, 40);
    const g = createGlass(el);
    await env.settle();
    assert.equal(g.tier, 'refract');
    env.html.setAttribute(SOLID_SURFACES_ATTRIBUTE, 'solid');
    await env.settle();
    assert.equal(g.tier, 'solid');
    assert.equal(g.info.reason, 'the user turned on solid surfaces');
    assert.equal(el.getAttribute('data-glass-tier'), 'solid');
    assert.equal(el.style.getPropertyValue('backdrop-filter'), '', 'the refract url() is removed');
    assert.equal(capabilities(env.win).solidSurfaces, true);
    env.html.removeAttribute(SOLID_SURFACES_ATTRIBUTE);
    await env.settle();
    assert.equal(g.tier, 'refract');
    g.destroy();
    assert.equal(env.win.MutationObserver && env.observers.length, 0, 'observer disconnected');
  });
});

test('createGlass: custom profile functions do not share cached maps', async () => {
  await withEnv({ engine: 'chromium' }, async (env) => {
    const linear = (t) => t;
    const square = (t) => t * t;
    const a = createGlass(env.el(60, 40), { profile: linear });
    await env.settle();
    const b = createGlass(env.el(60, 40), { profile: square });
    await env.settle();
    const c = createGlass(env.el(60, 40), { profile: linear });
    await env.settle();
    assert.equal(a.info.cacheHit, false);
    assert.equal(b.info.cacheHit, false, 'a different function builds its own map');
    assert.equal(c.info.cacheHit, true, 'the same function reuses the map');
    assert.notEqual(a.info.maxDisplacement, b.info.maxDisplacement);
    for (const g of [a, b, c]) g.destroy();
  });
});

test('createGlass: a pixel ratio change rebuilds the map and re-arms the resolution query', async () => {
  await withEnv({ engine: 'chromium', dpr: 1 }, async (env) => {
    const g = createGlass(env.el(50, 30));
    await env.settle();
    assert.deepEqual([g.info.pixelRatio, g.info.mapWidth], [1, 50]);
    const at1 = env.mqls.find((m) => m.media === '(resolution: 1dppx)');
    assert.ok(at1 && at1.listeners.size === 1, 'listens for a change away from 1dppx');
    env.win.devicePixelRatio = 2;
    at1.dispatch();
    await env.settle();
    assert.deepEqual([g.info.pixelRatio, g.info.mapWidth, g.info.width], [2, 100, 50]);
    assert.equal(at1.listeners.size, 0, 'old query released');
    const at2 = env.mqls.find((m) => m.media === '(resolution: 2dppx)');
    assert.ok(at2 && at2.listeners.size === 1, 'listens for the next change');
    g.destroy();
    assert.equal(at2.listeners.size, 0);
  });
});

test('createGlass: a failed map build settles every field on frost', async () => {
  await withEnv({ engine: 'chromium' }, async (env) => {
    const el = env.el(70, 40);
    const seen = [];
    const g = createGlass(el, { onRender: (i) => seen.push(i.tier) });
    await env.settle();
    assert.equal(g.tier, 'refract');
    const host = env.body.children.find((c) => 'liquidGlassHost' in c.dataset);
    assert.equal(host.children.length, 1);
    env.canvasThrows = true;
    g.update({ thickness: 12 }); // new cache key, so the map is rebuilt and fails
    await env.settle();
    assert.equal(env.warnings.length, 1);
    assert.match(String(env.warnings[0][0]), /map build failed/);
    assert.equal(g.tier, 'frost', 'the tier getter agrees with the attribute');
    assert.equal(g.info.tier, 'frost');
    assert.match(g.info.reason, /could not be built/);
    assert.deepEqual(seen, ['refract', 'frost']);
    assert.equal(el.getAttribute('data-glass-tier'), 'frost');
    assert.equal(el.style.getPropertyValue('backdrop-filter'), '', 'no url() to a removed filter');
    assert.equal(host.children.length, 0, 'the old filter is dropped');
    g.destroy();
  });
});

test('createGlass: an element under 2 px drops the url() filter and reports frost', async () => {
  await withEnv({ engine: 'chromium' }, async (env) => {
    const el = env.el(60, 30);
    const g = createGlass(el);
    await env.settle();
    assert.equal(g.tier, 'refract');
    el.offsetHeight = 1;
    g.refresh();
    await env.settle();
    assert.equal(g.tier, 'frost');
    assert.equal(el.getAttribute('data-glass-tier'), 'frost');
    assert.equal(el.style.getPropertyValue('backdrop-filter'), '');
    assert.match(g.info.reason, /2 CSS px/);
    el.offsetHeight = 30;
    g.refresh();
    await env.settle();
    assert.equal(g.tier, 'refract');
    g.destroy();
  });
});

test('createGlass: glass inside glass warns once, on the inner element', async () => {
  await withEnv({ engine: 'chromium' }, async (env) => {
    const outer = env.el(200, 60);
    const inner = env.el(40, 30, outer);
    const a = createGlass(outer);
    const b = createGlass(inner);
    await env.settle();
    const nested = env.warnings.filter((w) => /inside another glass element/.test(String(w[0])));
    assert.equal(nested.length, 1);
    assert.equal(nested[0][1], inner);
    assert.equal(nested[0][2], outer);
    b.refresh();
    await env.settle();
    assert.equal(env.warnings.length, 1, 'checked on the first render only');
    b.destroy();
    const quiet = createGlass(inner, { warn: false });
    await env.settle();
    assert.equal(env.warnings.length, 1, 'warn: false silences it');
    quiet.destroy();
    a.destroy();
  });
});
