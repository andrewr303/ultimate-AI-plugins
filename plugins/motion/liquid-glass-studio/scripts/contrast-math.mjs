// Pure contrast math for text over glass. No DOM, no dependencies.
//
// Relative luminance and contrast ratio follow the WCAG 2.x definitions
// (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, checked 2026-11-05):
//   L = 0.2126 R + 0.7152 G + 0.0722 B, with each channel linearized from sRGB;
//   ratio = (L1 + 0.05) / (L2 + 0.05), L1 the lighter.
// The linearization cutoff is 0.04045 (the sRGB standard value). Older WCAG
// text says 0.03928; no 8-bit channel value falls between the two, so the
// results are identical for 8-bit colors.
//
// Compositing is source-over in gamma-encoded sRGB, which is how browsers
// blend translucent layers by default. A glass surface is more than a tint
// (blur, refraction, rim light), so for real pages measure the rendered pixels
// (see glass_contrast.mjs) and use compositeOver only for flat tint estimates.

/** @typedef {{r:number,g:number,b:number,a?:number}} RGBA  channels 0..255, a 0..1 */

const clamp = (value, lo, hi) => Math.min(hi, Math.max(lo, value));

/**
 * Parse a CSS color string as returned by getComputedStyle, or a hex literal.
 * Supports #rgb, #rgba, #rrggbb, #rrggbbaa, rgb()/rgba() (comma or space
 * syntax, numbers or percentages), color(srgb ...) and "transparent".
 * Throws on anything else (for example oklch()), so callers can ask the user
 * for an explicit --text-color.
 * @param {string} input
 * @returns {Required<RGBA>}
 */
export function parseColor(input) {
  const text = String(input).trim().toLowerCase();
  if (text === 'transparent') return { r: 0, g: 0, b: 0, a: 0 };
  let match = text.match(/^#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$/);
  if (match) {
    let hex = match[1];
    if (hex.length <= 4) hex = [...hex].map((ch) => ch + ch).join('');
    const n = (i) => parseInt(hex.slice(i, i + 2), 16);
    return { r: n(0), g: n(2), b: n(4), a: hex.length === 8 ? n(6) / 255 : 1 };
  }
  match = text.match(/^rgba?\((.*)\)$/);
  if (match) {
    const parts = match[1].split(/[\s,/]+/).filter(Boolean);
    if (parts.length < 3 || parts.length > 4) throw new Error(`Unsupported color: ${input}`);
    const channel = (p) => (p.endsWith('%') ? (parseFloat(p) / 100) * 255 : parseFloat(p));
    const alpha = parts[3] === undefined ? 1 : parts[3].endsWith('%') ? parseFloat(parts[3]) / 100 : parseFloat(parts[3]);
    const out = { r: channel(parts[0]), g: channel(parts[1]), b: channel(parts[2]), a: alpha };
    if (Object.values(out).some((v) => !Number.isFinite(v))) throw new Error(`Unsupported color: ${input}`);
    return { r: clamp(out.r, 0, 255), g: clamp(out.g, 0, 255), b: clamp(out.b, 0, 255), a: clamp(out.a, 0, 1) };
  }
  match = text.match(/^color\(srgb\s+([^)]*)\)$/);
  if (match) {
    const [rgb, alphaPart] = match[1].split('/');
    const values = rgb.trim().split(/\s+/).map((p) => (p.endsWith('%') ? parseFloat(p) / 100 : parseFloat(p)));
    const a = alphaPart === undefined ? 1 : parseFloat(alphaPart) / (alphaPart.includes('%') ? 100 : 1);
    if (values.length !== 3 || [...values, a].some((v) => !Number.isFinite(v))) throw new Error(`Unsupported color: ${input}`);
    return { r: clamp(values[0] * 255, 0, 255), g: clamp(values[1] * 255, 0, 255), b: clamp(values[2] * 255, 0, 255), a: clamp(a, 0, 1) };
  }
  throw new Error(`Unsupported color: ${input} (pass an explicit #hex text color)`);
}

/** Linearize one 8-bit sRGB channel (0..255) to 0..1. */
export function srgbToLinear(channel) {
  const c = clamp(channel, 0, 255) / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/**
 * WCAG relative luminance of an opaque sRGB color.
 * @param {RGBA} color
 */
export function relativeLuminance({ r, g, b }) {
  return 0.2126 * srgbToLinear(r) + 0.7152 * srgbToLinear(g) + 0.0722 * srgbToLinear(b);
}

/** Contrast ratio between two luminances, 1..21. */
export function contrastFromLuminance(l1, l2) {
  const hi = Math.max(l1, l2);
  const lo = Math.min(l1, l2);
  return (hi + 0.05) / (lo + 0.05);
}

/**
 * Contrast ratio between two colors. A translucent foreground is composited
 * over the background first; the background must be opaque.
 * @param {RGBA|string} foreground
 * @param {RGBA|string} background
 */
export function contrastRatio(foreground, background) {
  const bg = typeof background === 'string' ? parseColor(background) : background;
  let fg = typeof foreground === 'string' ? parseColor(foreground) : foreground;
  if ((bg.a ?? 1) < 1) throw new Error('contrastRatio needs an opaque background; composite it first');
  if ((fg.a ?? 1) < 1) fg = compositeOver(fg, bg);
  return contrastFromLuminance(relativeLuminance(fg), relativeLuminance(bg));
}

/**
 * Source-over compositing of a translucent layer (for example a glass tint)
 * onto a backdrop pixel, in gamma-encoded sRGB.
 * @param {RGBA} top     layer above, alpha 0..1
 * @param {RGBA} bottom  backdrop, alpha 0..1 (default opaque)
 * @returns {Required<RGBA>}
 */
export function compositeOver(top, bottom) {
  const ta = clamp(top.a ?? 1, 0, 1);
  const ba = clamp(bottom.a ?? 1, 0, 1);
  const a = ta + ba * (1 - ta);
  if (a === 0) return { r: 0, g: 0, b: 0, a: 0 };
  const mix = (t, b) => (t * ta + b * ba * (1 - ta)) / a;
  return { r: mix(top.r, bottom.r), g: mix(top.g, bottom.g), b: mix(top.b, bottom.b), a };
}

/**
 * Estimate the color seen through a flat glass tint: composite the tint over
 * the backdrop, then any extra translucent layers (highlights, veils) in order.
 * @param {RGBA} backdrop opaque backdrop pixel
 * @param {...RGBA} layers bottom-to-top translucent layers
 */
export function glassOver(backdrop, ...layers) {
  return layers.reduce((acc, layer) => compositeOver(layer, acc), { ...backdrop, a: backdrop.a ?? 1 });
}

/**
 * Percentile of a numeric set with linear interpolation between closest ranks
 * (p in 0..100). Accepts any array-like; does not mutate a plain array.
 * Pass sorted=true when the input is already ascending.
 */
export function percentile(values, p, sorted = false) {
  const n = values.length;
  if (n === 0) return NaN;
  const data = sorted ? values : Float64Array.from(values).sort();
  const rank = (clamp(p, 0, 100) / 100) * (n - 1);
  const lo = Math.floor(rank);
  const hi = Math.ceil(rank);
  return data[lo] + (data[hi] - data[lo]) * (rank - lo);
}

/** Minimum of an array-like without spreading (safe for millions of values). */
export function minOf(values) {
  let min = Infinity;
  for (let i = 0; i < values.length; i += 1) if (values[i] < min) min = values[i];
  return values.length ? min : NaN;
}

/** Summary statistics used by the contrast report. */
export function summarize(values) {
  const sorted = Float64Array.from(values).sort();
  return {
    count: sorted.length,
    min: sorted.length ? sorted[0] : NaN,
    p5: percentile(sorted, 5, true),
    median: percentile(sorted, 50, true),
    max: sorted.length ? sorted[sorted.length - 1] : NaN,
  };
}

/**
 * Per-pixel contrast of a text color against RGBA pixel data (for example
 * ImageData.data). Pixels whose mask entry is 0 are skipped. Pixels that are
 * not fully opaque are composited over `matte` (white by default, the
 * browser's canvas default). A translucent text color is composited over each
 * pixel before the ratio is taken.
 * @param {Uint8Array|Uint8ClampedArray|number[]} rgba  4 bytes per pixel
 * @param {RGBA|string} textColor
 * @param {{mask?: Uint8Array, matte?: RGBA}} [options]
 * @returns {Float64Array} one ratio per measured pixel
 */
export function pixelContrasts(rgba, textColor, { mask, matte = { r: 255, g: 255, b: 255, a: 1 } } = {}) {
  const text = typeof textColor === 'string' ? parseColor(textColor) : { a: 1, ...textColor };
  const pixels = Math.floor(rgba.length / 4);
  const out = new Float64Array(pixels);
  const opaqueText = text.a >= 1;
  const textLum = opaqueText ? relativeLuminance(text) : 0;
  let n = 0;
  for (let i = 0; i < pixels; i += 1) {
    if (mask && !mask[i]) continue;
    let px = { r: rgba[i * 4], g: rgba[i * 4 + 1], b: rgba[i * 4 + 2], a: rgba[i * 4 + 3] / 255 };
    if (px.a < 1) px = compositeOver(px, matte);
    const bgLum = relativeLuminance(px);
    const fgLum = opaqueText ? textLum : relativeLuminance(compositeOver(text, px));
    out[n] = contrastFromLuminance(fgLum, bgLum);
    n += 1;
  }
  return out.subarray(0, n);
}

/**
 * Worst-case style report over a set of per-pixel ratios.
 * pass is judged at the minimum (every measured pixel meets the threshold);
 * fractionBelow shows how much of the area fails.
 * @param {ArrayLike<number>} ratios
 * @param {number[]} [thresholds]
 */
export function contrastReport(ratios, thresholds = [4.5, 3]) {
  const stats = summarize(ratios);
  const result = { ...stats, thresholds: {} };
  for (const threshold of thresholds) {
    let below = 0;
    for (let i = 0; i < ratios.length; i += 1) if (ratios[i] < threshold) below += 1;
    result.thresholds[String(threshold)] = {
      passAtMin: stats.count > 0 && stats.min >= threshold,
      passAtP5: stats.count > 0 && stats.p5 >= threshold,
      fractionBelow: stats.count ? below / stats.count : NaN,
    };
  }
  return result;
}

/**
 * WCAG "large text" test: at least 18pt (24px), or 14pt (about 18.66px) and bold.
 * Source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, checked 2026-11-05.
 */
export function isLargeText(fontSizePx, fontWeight) {
  const weight = Number(fontWeight) || (String(fontWeight) === 'bold' ? 700 : 400);
  return fontSizePx >= 24 || (fontSizePx >= 18.66 && weight >= 700);
}
