// Liquid Glass Studio engine: liquid glass style refraction for the web.
// Original, dependency-free ES module. MIT License (see the plugin LICENSE).
// Not affiliated with Apple. "Liquid Glass" is Apple's name for its material.
//
// Two layers:
//   1. Pure math (safe to import in Node; touches no DOM at import time):
//      surface profiles, a Snell refraction profile, displacement and
//      specular maps, SVG filter markup, and the tier decision.
//   2. A browser API (capabilities(), createGlass()) that measures the
//      environment, renders maps to PNG data URLs and wires them to
//      `backdrop-filter: url(#id)`.
//
// Sources studied (MIT, not copied): glasshq-liquid-glass, simple-liquid-glass
// (which vendors samasante's map generator), liquidGL, ybouane-liquidglass and
// liquid-glass-react. Each comparison below names the library and file.

/* ------------------------------------------------------------------------ */
/* Small helpers                                                             */
/* ------------------------------------------------------------------------ */

const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);
const clamp01 = (v) => clamp(v, 0, 1);

/** Hermite smoothstep on [e0, e1]. */
export function smoothstep(e0, e1, x) {
  if (e0 === e1) return x < e0 ? 0 : 1;
  const t = clamp01((x - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
}

/** Quintic smootherstep on [0, 1]: zero first and second derivative at both ends. */
export function smootherstep(t) {
  t = clamp01(t);
  return t * t * t * (t * (t * 6 - 15) + 10);
}

/** Round half away from zero, so encode(-v) === -encode(v) exactly (mirror symmetry). */
const symRound = (v) => (v < 0 ? -Math.round(-v) : Math.round(v));

const fmt = (n) => {
  const v = Number(n);
  if (!Number.isFinite(v)) return '0';
  return String(Math.round(v * 10000) / 10000);
};

const escapeAttr = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/* ------------------------------------------------------------------------ */
/* 1. Surface profiles                                                       */
/* ------------------------------------------------------------------------ */
//
// A profile is a height function h(t) on t in [0, 1], where t is the
// normalized distance from the outer edge across the bezel:
//   t = 0 at the outer edge, t = 1 where the bezel meets the flat interior.
// Heights are normalized to [0, 1]; the physical height is thickness * h(t).
// Beyond the bezel (t > 1) the surface is flat, so refraction there is zero.
//
//   convexCircle(t)   = sqrt(1 - (1 - t)^2)
//                       Quarter circle. Vertical wall at the edge, flat at t = 1.
//   convexSquircle(t) = (1 - (1 - t)^4)^(1/4)
//                       Superellipse (n = 4) quarter. Rises faster and settles
//                       flatter than the circle, which concentrates bending
//                       close to the rim and keeps the interior calm.
//   concave(t)        = 1 - smootherstep(t)
//                       A bowl: thick at the rim with a level top edge, dipping
//                       smoothly toward the interior. The slope is negative,
//                       so light bends outward (samples move out). The level
//                       rim keeps the offset zero at the edge, so no hard
//                       seam appears where the glass meets the page.
//   lip(t)            = convexCircle(t) * (1 - 0.5 * smootherstep(t))
//                       A raised ring: rises like the circle near the edge,
//                       then settles to a lower plateau at half height. Bends
//                       inward at the rim and slightly outward on the inner
//                       slope.
//
// Every profile has zero slope at t = 1, so displacement reaches zero
// continuously where the bezel meets the interior (no seam).

export function convexCircle(t) {
  const u = 1 - clamp01(t);
  return Math.sqrt(Math.max(0, 1 - u * u));
}

export function convexSquircle(t) {
  const u = 1 - clamp01(t);
  return Math.pow(Math.max(0, 1 - u * u * u * u), 0.25);
}

export function concave(t) {
  return 1 - smootherstep(t);
}

export function lip(t) {
  return convexCircle(t) * (1 - 0.5 * smootherstep(t));
}

export const PROFILES = Object.freeze({ convexCircle, convexSquircle, concave, lip });

function resolveProfile(profile) {
  if (typeof profile === 'function') return profile;
  const fn = PROFILES[profile || 'convexCircle'];
  if (!fn) throw new Error(`Unknown profile "${profile}". Use one of: ${Object.keys(PROFILES).join(', ')}`);
  return fn;
}

/** Numerical slope dh/dt with one-sided differences at the ends. */
function profileSlope(h, t) {
  const e = 1e-4;
  const a = Math.max(0, t - e);
  const b = Math.min(1, t + e);
  return (h(b) - h(a)) / (b - a);
}

/* ------------------------------------------------------------------------ */
/* 2. Refraction profile (Snell's law on the height field)                   */
/* ------------------------------------------------------------------------ */
//
// Model (a deliberate approximation, documented so it can be tuned honestly):
//   - Work in a 2D cross section perpendicular to the edge: u = inward
//     distance in px, z = height above the backdrop plane.
//   - The glass top surface is z(u) = thickness * h(u / bezelWidth); the
//     glass bottom sits on the backdrop plane (z = 0).
//   - The viewer looks straight down: incident direction I = (0, -1).
//   - Surface normal from the height derivative: m = dz/du,
//     N = (-m, 1) / sqrt(1 + m^2).
//   - Vector Snell refraction with eta = 1 / ior:
//       cos_i = -I.N,  k = 1 - eta^2 (1 - cos_i^2)
//       T = eta I + (eta cos_i - sqrt(k)) N
//   - The refracted ray travels from the surface down to the backdrop, so
//     the lateral offset is  D(u) = z(u) * T.u / (-T.z).
//   - Positive D means the pixel shows backdrop from further inward
//     (a converging, magnifying edge); negative D samples outward.
// Ignored on purpose: the second refraction at the flat bottom (a flat
// interface parallel to the backdrop only shifts the ray, and we already
// stop at the backdrop), Fresnel loss, dispersion (handled separately as an
// artistic per-channel scale), and the 2D curvature of corners (handled by
// following the distance-field gradient, see displacementField).
//
// How this compares with the sources:
//   - glasshq-liquid-glass packages/liquid-glass/src/gpu/maps.wgsl and
//     src/core/optics.ts use a circular-arc falloff with no Snell or IOR term:
//       "edge = 1.0 - sat(sqrt((2.0 - depth) * depth))"
//     with depth = clamp(-d * 0.05), so displacement is maximal AT the rim
//     and fades to zero over a fixed 20 px band. It is a heuristic lens.
//   - ybouane-liquidglass src/shaders.ts uses a quarter-circle bevel height
//     "sqrt(d * (2.0 * zR - d))", finite-difference normals, and scales the
//     height gradient by (1 - 1/ior) with ior = 1.5: a linear small-angle
//     stand-in for Snell's law, plus a center pull term.
//   - simple-liquid-glass src/vendor/samasante/displacement.ts builds a
//     spherical-cap dome slope normalized to a mean of 0.5, feathered with an
//     erf edge, plus a "bend" bump 6.75 s^2 (1 - s); no IOR.
// This engine keeps the full vector Snell expression, so large slopes
// saturate physically (at a vertical wall the offset factor is
// sqrt(ior^2 - 1)) instead of growing without bound, and the offset is zero
// where the glass has zero height.

function lateralOffset(h, t, bezelWidth, thickness, ior) {
  if (t >= 1) return 0; // flat interior by definition (every profile has zero slope at t = 1)
  const height = thickness * h(t);
  if (height === 0 || ior <= 1) return 0;
  const m = (thickness / bezelWidth) * profileSlope(h, t);
  if (m === 0) return 0;
  const inv = 1 / Math.sqrt(1 + m * m);
  const nx = -m * inv;
  const nz = inv;
  const eta = 1 / ior;
  const cosi = nz;
  const k = 1 - eta * eta * (1 - cosi * cosi);
  if (k < 0) return 0; // total internal reflection cannot happen entering a denser medium; guard anyway
  const f = eta * cosi - Math.sqrt(k);
  const tx = f * nx;
  const tz = -eta + f * nz;
  return (height * tx) / -tz;
}

/**
 * Signed lateral displacement (px) sampled across the bezel.
 * Index i corresponds to t = i / (samples - 1). Positive = sample inward.
 * @returns {Float64Array}
 */
export function refractionProfile({
  bezelWidth = 28,
  thickness = 40,
  ior = 1.5,
  profile = 'convexCircle',
  samples = 128,
  strength = 1,
} = {}) {
  const h = resolveProfile(profile);
  const n = Math.max(2, Math.floor(samples));
  const bw = Math.max(1e-3, bezelWidth);
  const th = Math.max(0, thickness);
  const n1 = Math.max(1, ior);
  const out = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    out[i] = lateralOffset(h, i / (n - 1), bw, th, n1) * strength;
  }
  return out;
}

function sampleLut(lut, t) {
  if (t <= 0) return lut[0];
  if (t >= 1) return lut[lut.length - 1];
  const x = t * (lut.length - 1);
  const i = Math.floor(x);
  const f = x - i;
  return lut[i] * (1 - f) + lut[i + 1] * f;
}

/* ------------------------------------------------------------------------ */
/* 3. Shape distance field                                                   */
/* ------------------------------------------------------------------------ */
//
// Signed distance (px, negative inside) to a centered rounded rectangle with
// half sizes hw, hh and corner radius r. shape 'rounded' uses circular
// corners (matches CSS border-radius). shape 'squircle' replaces the corner
// circle with an L4-norm superellipse corner: continuous and monotone, but
// only an approximation of true Euclidean distance inside the corner
// (within a factor of 2^(-1/4) ~ 0.84). It will not match a CSS
// border-radius clip exactly; clip the element with a matching shape.

export function roundedRectSDF(x, y, hw, hh, r, shape = 'rounded') {
  const qx = Math.abs(x) - hw + r;
  const qy = Math.abs(y) - hh + r;
  const ox = qx > 0 ? qx : 0;
  const oy = qy > 0 ? qy : 0;
  let outside;
  if (shape === 'squircle') {
    const a = ox * ox;
    const b = oy * oy;
    outside = Math.sqrt(Math.sqrt(a * a + b * b));
  } else {
    outside = Math.sqrt(ox * ox + oy * oy);
  }
  const inside = Math.min(Math.max(qx, qy), 0);
  return outside + inside - r;
}

function gradientAt(x, y, hw, hh, r, shape) {
  const e = 0.25;
  const gx = (roundedRectSDF(x + e, y, hw, hh, r, shape) - roundedRectSDF(x - e, y, hw, hh, r, shape)) / (2 * e);
  const gy = (roundedRectSDF(x, y + e, hw, hh, r, shape) - roundedRectSDF(x, y - e, hw, hh, r, shape)) / (2 * e);
  const len = Math.sqrt(gx * gx + gy * gy);
  return len > 1e-9 ? [gx / len, gy / len] : [0, 0];
}

/** Pixel-center coordinate, exactly antisymmetric: coord(n-1-i) === -coord(i). */
const centerCoord = (i, n, size) => (i + 0.5 - n / 2) * (size / n);

/* ------------------------------------------------------------------------ */
/* 4. Displacement map                                                       */
/* ------------------------------------------------------------------------ */
//
// Encoding (RGBA, Uint8ClampedArray, opaque):
//   R = x offset, G = y offset, B = neutral, A = 255.
//   byte = NEUTRAL + round(127 * offset / maxDisplacement), NEUTRAL = 128.
// SVG feDisplacementMap samples P(x + S (C - 0.5), y + ...) with C = byte/255.
// 128/255 is not 0.5: an uncorrected neutral pixel still moves content by
// S/510 px. buildFilterMarkup therefore subtracts neutralBias = 128/255 - 0.5
// (= 1/510) from R and G with an feColorMatrix before displacing, the same
// correction simple-liquid-glass applies (src/core/DisplacementFilter.tsx and
// src/core/LiquidGLSvgFilter.tsx use a -1/510 intercept). After correction
// the offset is S * (byte - 128) / 255, so S = maxDisplacement * 255 / 127
// maps byte 255 to exactly +maxDisplacement. That S is returned as
// filterScale so the filter and the map always agree.
//
// Corners and folds:
//   - Direction is the inward normal of the distance field (-grad sdf).
//     The field shape uses corner radius max(radius, bezelWidth), so inside
//     the bezel band the normal turns smoothly around corners instead of
//     snapping across the diagonal crease (the tear seen when the bezel is
//     wider than the corner radius). The visible clip keeps the authored
//     radius; near the edge displacement fades to zero, so the mismatch is
//     not visible.
//   - bezelWidth is clamped to the short half side so a pill's center line
//     (where the normal flips) always has zero displacement.
//   - The outer edge fades to neutral over a fixed band of 1 CSS px (never
//     less than one device pixel, never more than half the bezel), returned
//     as fadeBand. simple-liquid-glass src/core/displacementField.ts widens
//     its neutral band with the displacement; that was tried here and
//     rejected. Every built-in profile has zero offset at t = 0, so the band
//     has to be sized from the offset a few px in, and at 360 x 200, bezel
//     28, thickness 40 a band of twice that offset cut the peak offset from
//     6.9 to 4.7 px (convexSquircle) and from 3.9 to 2.6 px (lip): the fold
//     guard reduced less, but the wide fade removed the rim where those
//     profiles bend most. A 1 CSS px band gives the same result at every
//     pixel ratio.
//   - Fold check: the warp p -> p + a * d(p) must stay locally injective, so
//     the Jacobian determinant must stay positive. The minimum determinant
//     is measured on the float field (central differences); if it falls
//     below minJacobian, the amplitude a is reduced by bisection.
//     simple-liquid-glass uses the same criterion (jacobianMinDet in
//     src/core/displacementField.ts); this implementation is independent.

export const NEUTRAL = 128;
export const NEUTRAL_BIAS = NEUTRAL / 255 - 0.5; // 1/510
const EDGE_FADE_CSS_PX = 1;

/** Encode a signed offset (px) to a byte given the map's max displacement. */
export function encodeDisplacement(offset, maxDisplacement) {
  if (!(maxDisplacement > 0)) return NEUTRAL;
  const u = clamp(offset / maxDisplacement, -1, 1);
  return NEUTRAL + symRound(127 * u);
}

/**
 * Decode a byte back to the px offset the corrected filter will apply.
 * filterScale defaults to maxDisplacement * 255 / 127.
 */
export function decodeDisplacement(byte, maxDisplacement, filterScale = (maxDisplacement * 255) / 127) {
  // Filter math after the neutral correction: S * (byte / 255 - NEUTRAL_BIAS - 0.5)
  return filterScale * (byte / 255 - NEUTRAL_BIAS - 0.5);
}

/**
 * Build the displacement map for a rounded rectangle.
 * @param {object} o
 * @param {number} o.width   CSS px
 * @param {number} o.height  CSS px
 * @param {number} [o.radius] corner radius, CSS px (clamped to half the short side)
 * @param {number} [o.bezelWidth] refracting band width, CSS px
 * @param {string|function} [o.profile]
 * @param {number} [o.ior]
 * @param {number} [o.thickness] glass height at the plateau, CSS px
 * @param {number} [o.scale] strength multiplier on the physical offset (alias: strength)
 * @param {number} [o.pixelRatio] map pixels per CSS px (use devicePixelRatio)
 * @param {'rounded'|'squircle'} [o.shape]
 * @param {number} [o.foldHeadroom] fold check runs at amplitude * headroom (use 1 + chromaticAberration)
 * @param {number} [o.minJacobian] smallest allowed Jacobian determinant; pass -Infinity
 *   to allow folds. Inference from the numbers: glasshq-liquid-glass defaults to a 60 px offset
 *   (src/core/materials.ts) over a 20 px band (src/gpu/maps.wgsl), which folds the rim into a
 *   mirrored, compressed image; this guard trades that look for an unfolded one.
 */
export function displacementField({
  width,
  height,
  radius = 16,
  bezelWidth = 28,
  profile = 'convexCircle',
  ior = 1.5,
  thickness = 40,
  scale,
  strength,
  pixelRatio = 1,
  shape = 'rounded',
  foldHeadroom = 1,
  minJacobian = 0.2,
} = {}) {
  const W = Math.max(1, Number(width) || 1);
  const H = Math.max(1, Number(height) || 1);
  const pr = clamp(Number(pixelRatio) || 1, 0.25, 4);
  const mw = Math.max(1, Math.round(W * pr));
  const mh = Math.max(1, Math.round(H * pr));
  const hw = W / 2;
  const hh = H / 2;
  const minHalf = Math.min(hw, hh);
  const r = clamp(Number(radius) || 0, 0, minHalf);
  const bezel = clamp(Number(bezelWidth) || 1, 0.5, minHalf);
  const fieldRadius = clamp(Math.max(r, bezel), 0, minHalf);
  const amp = Number.isFinite(scale) ? scale : Number.isFinite(strength) ? strength : 1;

  const lut = refractionProfile({ bezelWidth: bezel, thickness, ior, profile, samples: 512, strength: amp });
  const fadeBand = Math.min(0.5 * bezel, Math.max(1 / pr, EDGE_FADE_CSS_PX));

  const n = mw * mh;
  const fx = new Float32Array(n);
  const fy = new Float32Array(n);
  for (let j = 0; j < mh; j++) {
    const y = centerCoord(j, mh, H);
    for (let i = 0; i < mw; i++) {
      const x = centerCoord(i, mw, W);
      const d = roundedRectSDF(x, y, hw, hh, fieldRadius, shape);
      const depth = -d;
      if (depth <= 0 || depth >= bezel) continue;
      const D = sampleLut(lut, depth / bezel) * smoothstep(0, fadeBand, depth);
      if (D === 0) continue;
      const g = gradientAt(x, y, hw, hh, fieldRadius, shape);
      const k = j * mw + i;
      fx[k] = -g[0] * D; // inward = -outward normal
      fy[k] = -g[1] * D;
    }
  }

  // Partial derivatives of the offset field (px per px).
  const sx = W / mw;
  const sy = H / mh;
  const ax = new Float32Array(n); // d(fx)/dx
  const ay = new Float32Array(n); // d(fx)/dy
  const bx = new Float32Array(n); // d(fy)/dx
  const by = new Float32Array(n); // d(fy)/dy
  for (let j = 1; j < mh - 1; j++) {
    for (let i = 1; i < mw - 1; i++) {
      const k = j * mw + i;
      ax[k] = (fx[k + 1] - fx[k - 1]) / (2 * sx);
      ay[k] = (fx[k + mw] - fx[k - mw]) / (2 * sy);
      bx[k] = (fy[k + 1] - fy[k - 1]) / (2 * sx);
      by[k] = (fy[k + mw] - fy[k - mw]) / (2 * sy);
    }
  }
  const minDetAt = (a) => {
    let m = Infinity;
    for (let k = 0; k < n; k++) {
      const det = (1 + a * ax[k]) * (1 + a * by[k]) - a * a * ay[k] * bx[k];
      if (det < m) m = det;
    }
    return m === Infinity ? 1 : m;
  };
  const head = Math.max(1, Number(foldHeadroom) || 1);
  let attenuation = 1;
  if (minDetAt(head) < minJacobian) {
    let lo = 0;
    let hi = 1;
    for (let it = 0; it < 24; it++) {
      const mid = (lo + hi) / 2;
      if (minDetAt(mid * head) >= minJacobian) lo = mid;
      else hi = mid;
    }
    attenuation = lo;
  }
  const finalMinDet = minDetAt(attenuation);

  let maxAbs = 0;
  for (let k = 0; k < n; k++) {
    fx[k] *= attenuation;
    fy[k] *= attenuation;
    const m = Math.max(Math.abs(fx[k]), Math.abs(fy[k]));
    if (m > maxAbs) maxAbs = m;
  }

  const data = new Uint8ClampedArray(n * 4);
  for (let k = 0; k < n; k++) {
    const p = k * 4;
    data[p] = encodeDisplacement(fx[k], maxAbs);
    data[p + 1] = encodeDisplacement(fy[k], maxAbs);
    data[p + 2] = NEUTRAL;
    data[p + 3] = 255;
  }

  return {
    width: mw,
    height: mh,
    cssWidth: W,
    cssHeight: H,
    pixelRatio: pr,
    data,
    neutral: NEUTRAL,
    neutralBias: NEUTRAL_BIAS,
    maxDisplacement: maxAbs,
    filterScale: (maxAbs * 255) / 127,
    attenuation,
    minJacobian: finalMinDet,
    bezelWidth: bezel,
    radius: r,
    fieldRadius,
    fadeBand,
  };
}

/* ------------------------------------------------------------------------ */
/* 5. Specular rim map                                                       */
/* ------------------------------------------------------------------------ */
//
// White RGB with alpha = intensity * coverage * rim(depth) * direction(n).
//   coverage: anti-aliased inside test, 1 device px wide.
//   rim: (1 - smoothstep(0, rimWidth, depth))^1.5, a thin band at the edge.
//   direction: n is the outward normal; L points toward the light in screen
//     space, lightAngle in degrees (0 = from the right, 90 = from the top).
//     A primary highlight faces the light; a weaker one sits on the opposite
//     rim (light leaving through the far edge), with a small floor so the
//     whole outline reads.
// glasshq-liquid-glass src/gpu/maps.wgsl lights top and bottom symmetrically
// and adds a dark side shade; ybouane-liquidglass src/shaders.ts uses
// Blinn-Phong lights plus a Fresnel term. This map is a single cheap 2D
// approximation meant to be composited with a screen blend.

export function specularField({
  width,
  height,
  radius = 16,
  shape = 'rounded',
  pixelRatio = 1,
  lightAngle = 135,
  intensity = 0.6,
  rimWidth = 3,
} = {}) {
  const W = Math.max(1, Number(width) || 1);
  const H = Math.max(1, Number(height) || 1);
  const pr = clamp(Number(pixelRatio) || 1, 0.25, 4);
  const mw = Math.max(1, Math.round(W * pr));
  const mh = Math.max(1, Math.round(H * pr));
  const hw = W / 2;
  const hh = H / 2;
  const r = clamp(Number(radius) || 0, 0, Math.min(hw, hh));
  const rw = Math.max(0.25, Number(rimWidth) || 1);
  const amt = clamp01(Number(intensity) || 0);
  const a = (lightAngle * Math.PI) / 180;
  const lx = Math.cos(a);
  const ly = -Math.sin(a); // screen y grows downward
  const data = new Uint8ClampedArray(mw * mh * 4);
  for (let j = 0; j < mh; j++) {
    const y = centerCoord(j, mh, H);
    for (let i = 0; i < mw; i++) {
      const x = centerCoord(i, mw, W);
      const p = (j * mw + i) * 4;
      data[p] = 255;
      data[p + 1] = 255;
      data[p + 2] = 255;
      const d = roundedRectSDF(x, y, hw, hh, r, shape);
      const coverage = clamp01(0.5 - d * pr);
      if (coverage === 0 || amt === 0) continue;
      const depth = Math.max(0, -d);
      if (depth >= rw) continue;
      const rim = Math.pow(1 - smoothstep(0, rw, depth), 1.5);
      const g = gradientAt(x, y, hw, hh, r, shape);
      const dot = g[0] * lx + g[1] * ly;
      const front = Math.pow(Math.max(0, dot), 2);
      const back = 0.55 * Math.pow(Math.max(0, -dot), 2);
      const dir = 0.18 + 0.82 * Math.max(front, back);
      data[p + 3] = Math.round(255 * clamp01(amt * coverage * rim * dir));
    }
  }
  return { width: mw, height: mh, cssWidth: W, cssHeight: H, pixelRatio: pr, data };
}

/* ------------------------------------------------------------------------ */
/* 6. SVG filter markup                                                      */
/* ------------------------------------------------------------------------ */
//
// Graph (all in sRGB so map bytes are not converted to linear light):
//   [blur]  feGaussianBlur on SourceGraphic            -> frost   (optional)
//   [sat]   feColorMatrix saturate                     -> sat     (optional)
//   map     feImage (displacement PNG, stretched to the box)
//   mapN    feColorMatrix subtracting neutralBias from R and G
//   one pass:  feDisplacementMap x=R y=G               -> refracted
//   three passes (chromaticAberration > 0):
//     dR, dG, dB  feDisplacementMap, scales S(1-ca), S, S(1+ca); always x=R y=G
//     cR, cG, cB  feColorMatrix keeping one channel, alpha forced to 1
//     sum         arithmetic add (channels are disjoint, so the sum is exact)
//     refracted   feComposite "in" with dG, restoring the center pass alpha
//   [spec]  feImage (specular PNG) screen-blended over refracted
//
// Why the recombination looks like this: liquid-glass-react src/index.tsx
// reads Y from the B channel (yChannelSelector="B") while one of its baked
// maps has B = 0 everywhere, which turns vertical refraction into a constant
// shift; its channel images are merged with screen blends, which also merge
// alpha. Here every pass reads x from R and y from G, and alpha comes from a
// single pass so semi-transparent backdrops are not brightened.
// Blue gets the largest scale because shorter wavelengths see a higher
// index of refraction in common glasses; the size of the split is an
// artistic control, not a dispersion model.

export function buildFilterMarkup({
  id,
  mapHref,
  specularHref = '',
  width,
  height,
  scale,
  chromaticAberration = 0,
  blur = 0,
  saturation = 1,
  neutralBias = NEUTRAL_BIAS,
  specularOpacity = 1,
} = {}) {
  if (!/^[A-Za-z][A-Za-z0-9_-]*$/.test(String(id || ''))) {
    throw new Error('buildFilterMarkup: id must start with a letter and use only letters, digits, "-" or "_"');
  }
  if (!mapHref) throw new Error('buildFilterMarkup: mapHref is required');
  const W = Math.max(1, Number(width) || 1);
  const H = Math.max(1, Number(height) || 1);
  const S = Number(scale) || 0;
  const ca = clamp(Number(chromaticAberration) || 0, 0, 1);
  const b = Math.max(0, Number(blur) || 0);
  const sat = Math.max(0, Number.isFinite(Number(saturation)) ? Number(saturation) : 1);
  const bias = fmt(neutralBias);
  const box = `x="0" y="0" width="${fmt(W)}" height="${fmt(H)}"`;
  const parts = [];
  parts.push(
    `<filter id="${id}" ${box} filterUnits="userSpaceOnUse" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">`,
  );
  let src = 'SourceGraphic';
  if (b > 0) {
    parts.push(`<feGaussianBlur in="${src}" stdDeviation="${fmt(b)}" edgeMode="duplicate" result="frost"/>`);
    src = 'frost';
  }
  if (sat !== 1) {
    parts.push(`<feColorMatrix in="${src}" type="saturate" values="${fmt(sat)}" result="sat"/>`);
    src = 'sat';
  }
  parts.push(`<feImage href="${escapeAttr(mapHref)}" ${box} preserveAspectRatio="none" result="mapRaw"/>`);
  parts.push(
    `<feColorMatrix in="mapRaw" type="matrix" values="1 0 0 0 -${bias} 0 1 0 0 -${bias} 0 0 1 0 0 0 0 0 1 0" result="map"/>`,
  );
  if (ca > 0) {
    const scales = { R: S * (1 - ca), G: S, B: S * (1 + ca) };
    const keep = {
      R: '1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1',
      G: '0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 1',
      B: '0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 1',
    };
    for (const c of ['R', 'G', 'B']) {
      parts.push(
        `<feDisplacementMap in="${src}" in2="map" scale="${fmt(scales[c])}" xChannelSelector="R" yChannelSelector="G" result="d${c}"/>`,
      );
      parts.push(`<feColorMatrix in="d${c}" type="matrix" values="${keep[c]}" result="c${c}"/>`);
    }
    parts.push(`<feComposite in="cR" in2="cG" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="cRG"/>`);
    parts.push(`<feComposite in="cRG" in2="cB" operator="arithmetic" k1="0" k2="1" k3="1" k4="0" result="cRGB"/>`);
    parts.push(`<feComposite in="cRGB" in2="dG" operator="in" result="refracted"/>`);
  } else {
    parts.push(
      `<feDisplacementMap in="${src}" in2="map" scale="${fmt(S)}" xChannelSelector="R" yChannelSelector="G" result="refracted"/>`,
    );
  }
  if (specularHref) {
    parts.push(`<feImage href="${escapeAttr(specularHref)}" ${box} preserveAspectRatio="none" result="specRaw"/>`);
    let spec = 'specRaw';
    const so = clamp01(Number(specularOpacity));
    if (so < 1) {
      parts.push(
        `<feColorMatrix in="specRaw" type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 ${fmt(so)} 0" result="spec"/>`,
      );
      spec = 'spec';
    }
    parts.push(`<feBlend in="${spec}" in2="refracted" mode="screen" result="lit"/>`);
  }
  parts.push('</filter>');
  return parts.join('');
}

/* ------------------------------------------------------------------------ */
/* 7. Tier decision                                                          */
/* ------------------------------------------------------------------------ */
//
// Tiers, from richest to plainest:
//   'refract' SVG displacement through backdrop-filter: url(#id)
//   'frost'   CSS backdrop-filter blur + saturate + tint
//   'solid'   opaque surface, no backdrop effects
// Rules (first match wins):
//   forced colors active      -> solid (the system palette replaces backgrounds)
//   solid surfaces turned on  -> solid (the page's own setting:
//                                 <html data-glass-surfaces="solid">)
//   reduced transparency      -> solid (the user asked for opaque surfaces)
//   increased contrast        -> solid (legibility first; also the only
//                                 signal Safari offers, because Safari does
//                                 not expose prefers-reduced-transparency)
//   no backdrop-filter        -> solid
//   engine is not Chromium    -> frost (url() backdrop filters do not render
//                                 reliably outside Chromium, see below)
//   otherwise                 -> refract
// `preferred` (an author or user override) can lower the tier, never raise
// it: forcing 'refract' on a Reduce Transparency user returns 'solid'.
//
// Platform facts (checked 2026-11-05):
//   - backdrop-filter: url() with feDisplacementMap renders in Chromium;
//     WebKit bug 245510 is open (https://bugs.webkit.org/show_bug.cgi?id=245510);
//     Firefox bug 1961378 is open (https://bugzilla.mozilla.org/show_bug.cgi?id=1961378).
//   - @supports cannot detect whether a url() backdrop filter renders, so an
//     engine check is required (https://kube.io/blog/liquid-glass-css-svg/).
//   - prefers-reduced-transparency: Chrome only; Firefox behind a pref; not in
//     Safari (https://web-platform-dx.github.io/web-features-explorer/features/prefers-reduced-transparency).

const TIER_RANK = { solid: 0, frost: 1, refract: 2 };

export function explainTier({
  reducedTransparency = false,
  contrastMore = false,
  forcedColors = false,
  solidSurfaces = false,
  supportsBackdrop = true,
  engine = 'unknown',
  preferred = 'auto',
} = {}) {
  let tier;
  let reason;
  if (forcedColors) [tier, reason] = ['solid', 'forced colors are active'];
  else if (solidSurfaces) [tier, reason] = ['solid', 'the user turned on solid surfaces'];
  else if (reducedTransparency) [tier, reason] = ['solid', 'the user prefers reduced transparency'];
  else if (contrastMore) [tier, reason] = ['solid', 'the user prefers more contrast'];
  else if (!supportsBackdrop) [tier, reason] = ['solid', 'backdrop-filter is not supported'];
  else if (engine !== 'chromium') [tier, reason] = ['frost', `url() backdrop refraction is unreliable in engine "${engine}"`];
  else [tier, reason] = ['refract', 'Chromium with backdrop-filter support'];
  if (preferred && preferred !== 'auto' && preferred in TIER_RANK && TIER_RANK[preferred] < TIER_RANK[tier]) {
    tier = preferred;
    reason = `override lowered the tier to ${preferred}`;
  }
  return { tier, reason };
}

/** Pure tier decision: 'refract' | 'frost' | 'solid'. */
export function detectTier(input = {}) {
  return explainTier(input).tier;
}

/**
 * Engine from a navigator-like object. User-agent parsing is brittle (UA
 * strings can be frozen, spoofed or reduced) but it is the only way to
 * learn whether url() backdrop filters render. Risks: a new engine or a
 * spoofed UA gets the wrong tier, so unknown engines fall back to 'frost',
 * which is safe everywhere backdrop-filter exists. Prefer
 * navigator.userAgentData brands when present. iOS browsers (CriOS, FxiOS,
 * EdgiOS) all use WebKit. glasshq-liquid-glass src/dom/engine.ts sniffs the
 * UA the same way.
 */
export function detectEngine(nav) {
  if (!nav) return 'unknown';
  const brands = nav.userAgentData && Array.isArray(nav.userAgentData.brands) ? nav.userAgentData.brands : null;
  const ua = String(nav.userAgent || '');
  if (/\b(CriOS|FxiOS|EdgiOS)\//.test(ua)) return 'webkit';
  if (brands && brands.some((b) => /Chromium/i.test(b.brand))) return 'chromium';
  if (/Gecko\/\d/.test(ua) && !/like Gecko/.test(ua)) return 'gecko';
  if (/(Chrome|Chromium|Edg|OPR|SamsungBrowser)\//.test(ua)) return 'chromium';
  if (/AppleWebKit\//.test(ua) || nav.vendor === 'Apple Computer, Inc.') return 'webkit';
  return 'unknown';
}

/* ------------------------------------------------------------------------ */
/* 8. Browser API                                                            */
/* ------------------------------------------------------------------------ */

/**
 * The page-level "solid surfaces" setting: <html data-glass-surfaces="solid">.
 * createGlass() watches this attribute live and forces the 'solid' tier while
 * it is set. CSS outside the engine can follow the same setting with
 * :root[data-glass-surfaces="solid"] selectors.
 */
export const SOLID_SURFACES_ATTRIBUTE = 'data-glass-surfaces';

export const MEDIA_QUERIES = Object.freeze({
  reducedTransparency: '(prefers-reduced-transparency: reduce)',
  contrastMore: '(prefers-contrast: more)',
  forcedColors: '(forced-colors: active)',
  reducedMotion: '(prefers-reduced-motion: reduce)',
});

function solidSurfacesOn(doc) {
  try {
    const root = doc && doc.documentElement;
    return Boolean(root && root.getAttribute(SOLID_SURFACES_ATTRIBUTE) === 'solid');
  } catch {
    return false;
  }
}

/** Measure the current environment (browser only). */
export function capabilities(win = globalThis.window) {
  if (!win || !win.document) {
    return { reducedTransparency: false, contrastMore: false, forcedColors: false, reducedMotion: false, solidSurfaces: false, supportsBackdrop: false, engine: 'unknown' };
  }
  const mm = (q) => {
    try {
      return Boolean(win.matchMedia && win.matchMedia(q).matches);
    } catch {
      return false;
    }
  };
  const sup = (p, v) => {
    try {
      return Boolean(win.CSS && win.CSS.supports && win.CSS.supports(p, v));
    } catch {
      return false;
    }
  };
  return {
    reducedTransparency: mm(MEDIA_QUERIES.reducedTransparency),
    contrastMore: mm(MEDIA_QUERIES.contrastMore),
    forcedColors: mm(MEDIA_QUERIES.forcedColors),
    reducedMotion: mm(MEDIA_QUERIES.reducedMotion),
    solidSurfaces: solidSurfacesOn(win.document),
    supportsBackdrop: sup('backdrop-filter', 'blur(1px)') || sup('-webkit-backdrop-filter', 'blur(1px)'),
    engine: detectEngine(win.navigator),
  };
}

/**
 * Find the nearest ancestor that starts a new Backdrop Root, so the glass
 * would only "see" content inside that ancestor. Filter Effects Level 2
 * (https://drafts.csswg.org/filter-effects-2/, checked 2026-11-05) lists
 * filter, opacity < 1, mask, clip-path, backdrop-filter, mix-blend-mode and
 * a matching will-change. Returns { element, property } or null.
 */
export function findBackdropRoot(element) {
  if (typeof getComputedStyle !== 'function' || !element) return null;
  for (let el = element.parentElement; el && el !== document.documentElement; el = el.parentElement) {
    const cs = getComputedStyle(el);
    const checks = [
      ['opacity', parseFloat(cs.opacity) < 1],
      ['filter', cs.filter && cs.filter !== 'none'],
      ['backdrop-filter', (cs.backdropFilter || cs.webkitBackdropFilter || 'none') !== 'none'],
      ['mask', (cs.maskImage || cs.webkitMaskImage || 'none') !== 'none'],
      ['clip-path', cs.clipPath && cs.clipPath !== 'none'],
      ['mix-blend-mode', cs.mixBlendMode && cs.mixBlendMode !== 'normal'],
      ['will-change', /\b(opacity|filter|backdrop-filter|mask|clip-path|mix-blend-mode)\b/.test(cs.willChange || '')],
    ];
    for (const [property, hit] of checks) if (hit) return { element: el, property };
  }
  return null;
}

export const DEFAULTS = Object.freeze({
  tier: 'auto',
  radius: 'auto',
  bezelWidth: 28,
  thickness: 40,
  ior: 1.5,
  profile: 'convexCircle',
  shape: 'rounded',
  strength: 1,
  chromaticAberration: 0,
  blur: 3,
  saturation: 1.5,
  frostBlur: 14,
  specularIntensity: 0.7,
  lightAngle: 135,
  rimWidth: 3,
  elasticity: 0,
  foldGuard: true,
  maxPixelRatio: 2,
  warn: true,
  onRender: null,
});


/**
 * Id of the one stylesheet createGlass() injects. If the page already has an
 * element with this id (a <style> you ship with a CSP nonce, or a <link>),
 * the engine uses it and injects nothing.
 */
export const BASE_STYLES_ID = 'lgs-base-styles';

/**
 * The frost and solid tier rules. Every selector is wrapped in :where(), so
 * the rules have zero specificity and any author CSS wins: style
 * [data-glass-tier="frost"] yourself to replace the default frost. The engine
 * feeds the frost values through --lg-frost-blur and --lg-saturation, which
 * it sets on each element from the frostBlur and saturation options.
 */
export const BASE_STYLES = [
  ':where([data-glass-tier="frost"]) {',
  '  -webkit-backdrop-filter: blur(var(--lg-frost-blur, 14px)) saturate(var(--lg-saturation, 1.5));',
  '  backdrop-filter: blur(var(--lg-frost-blur, 14px)) saturate(var(--lg-saturation, 1.5));',
  '}',
  ':where([data-glass-tier="solid"]) {',
  '  -webkit-backdrop-filter: none;',
  '  backdrop-filter: none;',
  '}',
].join('\n');

const CACHE_LIMIT = 24;
const mapCache = new Map(); // key -> Promise<{ mapUrl, specUrl, field }>
let instanceCount = 0;
let liveCount = 0;
let host = null;
let ownBaseStyle = null; // the <style> this module injected, if any
const glassElements = new WeakSet(); // elements with a live createGlass instance

function svgHost() {
  if (host && host.isConnected) return host;
  const NS = 'http://www.w3.org/2000/svg';
  host = document.createElementNS(NS, 'svg');
  host.setAttribute('aria-hidden', 'true');
  host.setAttribute('focusable', 'false');
  host.setAttribute('width', '0');
  host.setAttribute('height', '0');
  // Not display:none: Chromium skips filters inside undisplayed SVG.
  host.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;pointer-events:none';
  host.dataset.liquidGlassHost = '';
  document.body.appendChild(host);
  return host;
}

function ensureBaseStyles(doc) {
  if (!doc || typeof doc.createElement !== 'function') return;
  if (doc.getElementById(BASE_STYLES_ID)) return;
  const el = doc.createElement('style');
  el.id = BASE_STYLES_ID;
  el.textContent = BASE_STYLES;
  (doc.head || doc.documentElement).appendChild(el);
  ownBaseStyle = el;
}

function toDataURL({ width, height, data }) {
  const c = document.createElement('canvas');
  c.width = width;
  c.height = height;
  c.getContext('2d').putImageData(new ImageData(data, width, height), 0, 0);
  return c.toDataURL('image/png'); // lossless; never JPEG for vector data
}

async function decoded(url) {
  const img = new Image();
  img.src = url;
  try {
    await img.decode();
  } catch {
    /* decode can reject for detached images; the filter still loads it */
  }
  return url;
}

// Custom profile functions get a stable per-function id in the cache key:
// JSON.stringify drops function values, so without this two different
// functions would share one cached map.
const profileIds = new WeakMap();
let profileCount = 0;
function cacheKey(fieldOpts, specOpts) {
  const p = fieldOpts.profile;
  let profile = p;
  if (typeof p === 'function') {
    if (!profileIds.has(p)) profileIds.set(p, ++profileCount);
    profile = `function#${profileIds.get(p)}`;
  }
  return JSON.stringify([{ ...fieldOpts, profile }, specOpts]);
}

function cachedMaps(key, build) {
  if (mapCache.has(key)) {
    const hit = mapCache.get(key);
    mapCache.delete(key); // refresh LRU order
    mapCache.set(key, hit);
    return { promise: hit, hit: true };
  }
  const promise = build();
  mapCache.set(key, promise);
  promise.catch(() => mapCache.delete(key));
  while (mapCache.size > CACHE_LIMIT) mapCache.delete(mapCache.keys().next().value);
  return { promise, hit: false };
}

function parseFilter(markup) {
  const doc = new DOMParser().parseFromString(
    `<svg xmlns="http://www.w3.org/2000/svg">${markup}</svg>`,
    'image/svg+xml',
  );
  const err = doc.querySelector('parsererror');
  if (err) throw new Error('liquid-glass: generated filter markup did not parse');
  return document.importNode(doc.documentElement.firstElementChild, true);
}

function resolveRadius(element, option, w, h) {
  const limit = Math.min(w, h) / 2;
  if (typeof option === 'number') return clamp(option, 0, limit);
  const raw = getComputedStyle(element).borderTopLeftRadius || '0';
  const first = raw.split(' ')[0];
  const v = parseFloat(first) || 0;
  return clamp(first.endsWith('%') ? (v / 100) * Math.min(w, h) : v, 0, limit);
}

function glassAncestor(element) {
  for (let el = element.parentElement; el; el = el.parentElement) if (glassElements.has(el)) return el;
  return null;
}

/**
 * Turn an element into liquid glass style.
 * The engine never touches outline, focus styles or content. It sets:
 *   - data-glass-tier="refract|frost|solid" (style the tint per tier with it);
 *   - --lg-frost-blur and --lg-saturation (from frostBlur and saturation);
 *   - an inline backdrop-filter: url(#id) in the refract tier only, because
 *     each instance needs its own filter id;
 *   - translate and scale while pointer elasticity is on.
 * The frost and solid backdrops come from BASE_STYLES, injected once as
 * <style id="lgs-base-styles"> with zero-specificity :where() rules, so any
 * author CSS for those tiers wins.
 * The page-level setting <html data-glass-surfaces="solid"> forces the solid
 * tier, live.
 */
export function createGlass(element, options = {}) {
  if (typeof window === 'undefined' || !element) throw new Error('createGlass needs a browser and an element');
  const win = window;
  const doc = win.document;
  const uid = ++instanceCount;
  liveCount++;
  glassElements.add(element);
  ensureBaseStyles(doc);
  let opts = { ...DEFAULTS, ...options };
  let version = 0;
  let renderToken = 0;
  let rafId = 0;
  let destroyed = false;
  let checkedRoot = false;
  let current = null; // active <filter>
  let state = { tier: null, reason: '' };
  let info = {};
  const style = element.style;
  const saved = {
    backdrop: style.getPropertyValue('backdrop-filter'),
    webkit: style.getPropertyValue('-webkit-backdrop-filter'),
    frostBlur: style.getPropertyValue('--lg-frost-blur'),
    saturation: style.getPropertyValue('--lg-saturation'),
    translate: style.getPropertyValue('translate'),
    scale: style.getPropertyValue('scale'),
    tier: element.getAttribute('data-glass-tier'),
  };

  const schedule = () => {
    if (rafId || destroyed) return;
    rafId = win.requestAnimationFrame(() => {
      rafId = 0;
      render();
    });
  };

  // Preference changes and the page's solid-surfaces setting.
  const mqls = Object.values(MEDIA_QUERIES).map((q) => win.matchMedia(q));
  const onMedia = () => {
    resetElastic();
    schedule();
  };
  mqls.forEach((m) => m.addEventListener('change', onMedia));
  const MO = win.MutationObserver || (typeof MutationObserver === 'function' ? MutationObserver : null);
  const mo = MO && doc && doc.documentElement ? new MO(onMedia) : null;
  if (mo) mo.observe(doc.documentElement, { attributes: true, attributeFilter: [SOLID_SURFACES_ATTRIBUTE] });

  // Size changes, and pixel ratio changes (zoom, moving to another display)
  // that leave the CSS size alone. The resolution query only matches the
  // ratio it was created for, so it is re-armed after every change.
  const ro = typeof ResizeObserver === 'function' ? new ResizeObserver(schedule) : null;
  if (ro) ro.observe(element);
  let dprMql = null;
  function watchPixelRatio() {
    if (dprMql) dprMql.removeEventListener('change', onPixelRatio);
    dprMql = null;
    try {
      dprMql = win.matchMedia(`(resolution: ${win.devicePixelRatio || 1}dppx)`);
      dprMql.addEventListener('change', onPixelRatio);
    } catch {
      dprMql = null;
    }
  }
  function onPixelRatio() {
    watchPixelRatio();
    schedule();
  }
  watchPixelRatio();

  function setInline(prop, value) {
    if (value) style.setProperty(prop, value);
    else style.removeProperty(prop);
  }

  function restoreBackdrop() {
    setInline('backdrop-filter', saved.backdrop);
    setInline('-webkit-backdrop-filter', saved.webkit);
  }

  function dropFilter(node) {
    if (node && node.parentNode) node.parentNode.removeChild(node);
  }

  // Glass inside glass is the most common Backdrop Root, and the outer
  // element only gets its backdrop-filter when it renders, so this runs on
  // the first render, after every instance created in the same task exists.
  function checkBackdropRoot() {
    if (checkedRoot || !opts.warn) return;
    checkedRoot = true;
    const outer = glassAncestor(element);
    if (outer) {
      console.warn(
        'liquid-glass: this glass element sits inside another glass element. The outer backdrop-filter starts a Backdrop Root, so the inner glass refracts the outer glass instead of the page. Keep one glass layer, or give the inner one blur 0 and a smaller bezel and thickness (pass warn: false once it follows that rule).',
        element,
        outer,
      );
      return;
    }
    const root = findBackdropRoot(element);
    if (root) {
      console.warn(
        `liquid-glass: an ancestor has ${root.property} set, which starts a Backdrop Root; the glass will only refract content inside that ancestor.`,
        root.element,
      );
    }
  }

  // Every outcome other than a working refract filter ends here, so the
  // attribute, the tier getter, info and onRender always agree.
  function settle(decision, base) {
    state = decision;
    element.setAttribute('data-glass-tier', decision.tier);
    restoreBackdrop();
    dropFilter(current);
    current = null;
    info = { ...base, tier: decision.tier, reason: decision.reason };
    if (typeof opts.onRender === 'function') opts.onRender(info);
  }

  async function render() {
    if (destroyed) return;
    const token = ++renderToken;
    checkBackdropRoot();
    const caps = capabilities(win);
    let decision = explainTier({ ...caps, preferred: opts.tier });
    const w = Math.round(element.offsetWidth);
    const h = Math.round(element.offsetHeight);
    const pr = Math.min(win.devicePixelRatio || 1, opts.maxPixelRatio);
    const base = { tier: decision.tier, reason: decision.reason, engine: caps.engine, width: w, height: h, pixelRatio: pr };
    style.setProperty('--lg-frost-blur', `${fmt(opts.frostBlur)}px`);
    style.setProperty('--lg-saturation', fmt(opts.saturation));

    if (decision.tier === 'refract' && (w < 2 || h < 2)) {
      decision = { tier: 'frost', reason: 'the element is under 2 CSS px, too small to refract' };
    }
    if (decision.tier !== 'refract') {
      settle(decision, base);
      return;
    }

    const radius = resolveRadius(element, opts.radius, w, h);
    const ca = clamp(Number(opts.chromaticAberration) || 0, 0, 1);
    const fieldOpts = {
      width: w,
      height: h,
      radius,
      bezelWidth: opts.bezelWidth,
      profile: opts.profile,
      ior: opts.ior,
      thickness: opts.thickness,
      scale: opts.strength,
      pixelRatio: pr,
      shape: opts.shape,
      foldHeadroom: 1 + ca,
      minJacobian: opts.foldGuard === false ? -Infinity : 0.2,
    };
    const specOpts = {
      width: w,
      height: h,
      radius,
      shape: opts.shape,
      pixelRatio: pr,
      lightAngle: opts.lightAngle,
      intensity: opts.specularIntensity,
      rimWidth: opts.rimWidth,
    };
    const t0 = performance.now();
    const { promise, hit } = cachedMaps(cacheKey(fieldOpts, specOpts), async () => {
      const field = displacementField(fieldOpts);
      const spec = specularField(specOpts);
      const [mapUrl, specUrl] = await Promise.all([decoded(toDataURL(field)), decoded(toDataURL(spec))]);
      const { data, ...meta } = field; // keep the cache light: drop raw bytes
      return { mapUrl, specUrl, field: meta };
    });
    let maps;
    try {
      maps = await promise;
    } catch (e) {
      if (destroyed || token !== renderToken) return;
      console.warn('liquid-glass: map build failed, falling back to frost', e);
      settle({ tier: 'frost', reason: 'the displacement map could not be built' }, base);
      return;
    }
    if (destroyed || token !== renderToken) return;

    // Versioned ids: Chromium may keep a cached result when a filter's
    // children change under the same id, so swap to a new filter instead.
    const fid = `lgs-${uid}-${++version}`;
    const node = parseFilter(
      buildFilterMarkup({
        id: fid,
        mapHref: maps.mapUrl,
        specularHref: opts.specularIntensity > 0 ? maps.specUrl : '',
        width: w,
        height: h,
        scale: maps.field.filterScale,
        chromaticAberration: ca,
        blur: opts.blur,
        saturation: opts.saturation,
        neutralBias: maps.field.neutralBias,
      }),
    );
    svgHost().appendChild(node);
    style.setProperty('backdrop-filter', `url(#${fid})`);
    style.setProperty('-webkit-backdrop-filter', 'none');
    element.setAttribute('data-glass-tier', 'refract');
    state = decision;
    const old = current;
    current = node;
    win.requestAnimationFrame(() => win.requestAnimationFrame(() => dropFilter(old)));
    // The map's own size is in map pixels (CSS px times the pixel ratio), so
    // it is reported as mapWidth and mapHeight; width and height stay CSS px.
    const { width: mapWidth, height: mapHeight, cssWidth, cssHeight, pixelRatio: mapRatio, ...field } = maps.field;
    info = {
      ...field,
      mapWidth,
      mapHeight,
      radius,
      filterId: fid,
      cacheHit: hit,
      buildMs: Math.round((performance.now() - t0) * 10) / 10,
      mapUrl: maps.mapUrl,
      specularUrl: maps.specUrl,
      ...base,
    };
    if (typeof opts.onRender === 'function') opts.onRender(info);
  }

  // Pointer elasticity: a small pull toward the pointer and a slight stretch.
  // Uses the individual translate/scale properties so author transforms
  // survive, and layout size (offsetWidth) is unchanged, so ResizeObserver
  // does not loop. Off when prefers-reduced-motion is set.
  let pointerRaf = 0;
  let pending = null;
  function reducedMotion() {
    try {
      return win.matchMedia(MEDIA_QUERIES.reducedMotion).matches;
    } catch {
      return false;
    }
  }
  function resetElastic() {
    setInline('translate', saved.translate);
    setInline('scale', saved.scale);
  }
  function onPointerMove(ev) {
    const e = clamp(Number(opts.elasticity) || 0, 0, 1);
    if (e === 0 || reducedMotion()) return;
    pending = ev;
    if (pointerRaf) return;
    pointerRaf = win.requestAnimationFrame(() => {
      pointerRaf = 0;
      if (!pending || destroyed) return;
      const r = element.getBoundingClientRect();
      const nx = clamp((pending.clientX - (r.left + r.width / 2)) / (r.width / 2), -1, 1);
      const ny = clamp((pending.clientY - (r.top + r.height / 2)) / (r.height / 2), -1, 1);
      const pull = 6 * e;
      style.setProperty('translate', `${fmt(nx * pull)}px ${fmt(ny * pull)}px`);
      style.setProperty('scale', `${fmt(1 + 0.035 * e * Math.abs(nx))} ${fmt(1 + 0.035 * e * Math.abs(ny))}`);
    });
  }
  function onPointerLeave() {
    pending = null;
    resetElastic();
  }
  element.addEventListener('pointermove', onPointerMove);
  element.addEventListener('pointerleave', onPointerLeave);
  element.addEventListener('pointercancel', onPointerLeave);

  schedule();

  return {
    element,
    get tier() {
      return state.tier;
    },
    get info() {
      return info;
    },
    update(next = {}) {
      opts = { ...opts, ...next };
      if (!opts.elasticity) resetElastic();
      schedule();
    },
    refresh: schedule,
    destroy() {
      if (destroyed) return;
      destroyed = true;
      liveCount--;
      glassElements.delete(element);
      if (rafId) win.cancelAnimationFrame(rafId);
      if (pointerRaf) win.cancelAnimationFrame(pointerRaf);
      if (ro) ro.disconnect();
      if (mo) mo.disconnect();
      mqls.forEach((m) => m.removeEventListener('change', onMedia));
      if (dprMql) dprMql.removeEventListener('change', onPixelRatio);
      element.removeEventListener('pointermove', onPointerMove);
      element.removeEventListener('pointerleave', onPointerLeave);
      element.removeEventListener('pointercancel', onPointerLeave);
      dropFilter(current);
      current = null;
      restoreBackdrop();
      setInline('--lg-frost-blur', saved.frostBlur);
      setInline('--lg-saturation', saved.saturation);
      resetElastic();
      if (saved.tier === null) element.removeAttribute('data-glass-tier');
      else element.setAttribute('data-glass-tier', saved.tier);
      if (host && host.childNodes.length === 0) {
        host.remove();
        host = null;
      }
      if (liveCount === 0 && ownBaseStyle) {
        ownBaseStyle.remove();
        ownBaseStyle = null;
      }
    },
  };
}

/** Clear the shared map cache (for tests or memory pressure). */
export function clearGlassCache() {
  mapCache.clear();
}
