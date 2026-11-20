// Pure decision functions for scripts/glass_probe.mjs.
//
// Images are { width, height, data } with data as RGBA bytes (Uint8Array or
// Uint8ClampedArray), the shape canvas getImageData returns. Nothing here
// touches a browser, so every rule is unit tested in tests/probe.test.mjs.
//
// Why render and sample: CSS.supports('backdrop-filter', 'url(#f)') and
// @supports answer whether the value parses, not whether the engine paints
// it. A url() backdrop filter can parse and then draw nothing, so the probe
// renders a known filter over a known backdrop and measures the pixels.

export const DEFAULT_THRESHOLDS = Object.freeze({
  // Mean absolute difference (0 to 255) below which two captures count as
  // the same picture. Anti-aliasing and color management stay well under 4.
  minDiff: 8,
  // Blur moves pixels less than a large shift does, so its floor is lower.
  minBlurDiff: 4,
  // Allowed error, in image pixels, between the measured and expected shift.
  shiftTolerance: 1.5,
  // Residual after aligning the shift, as a fraction of the unaligned error.
  maxResidualRatio: 0.25,
  // Edge energy of the blurred pane over the control at or below this means
  // the edges went soft.
  maxSharpnessRatio: 0.6,
  // A blur keeps the average brightness. A larger change means the pane drew
  // something else (blank, opaque, black).
  maxMeanShift: 40,
});

function assertImage(img, label = 'image') {
  if (!img || !Number.isInteger(img.width) || !Number.isInteger(img.height) || !img.data) {
    throw new TypeError(`${label} must be { width, height, data }`);
  }
  if (img.data.length < img.width * img.height * 4) throw new RangeError(`${label} data is shorter than width * height * 4`);
}

function sameSize(a, b) {
  if (a.width !== b.width || a.height !== b.height) {
    throw new RangeError(`image sizes differ: ${a.width}x${a.height} vs ${b.width}x${b.height}`);
  }
}

/** Inner rectangle after trimming `margin` pixels on every side. */
export function interior(img, margin = 0) {
  const m = Math.max(0, Math.floor(margin));
  const x0 = Math.min(m, img.width);
  const y0 = Math.min(m, img.height);
  const x1 = Math.max(x0, img.width - m);
  const y1 = Math.max(y0, img.height - m);
  return { x0, y0, x1, y1 };
}

/** Per-pixel luma (Rec. 709 weights on the stored sRGB bytes), 0 to 255. */
export function luma(img) {
  assertImage(img);
  const n = img.width * img.height;
  const out = new Float32Array(n);
  const d = img.data;
  for (let i = 0; i < n; i += 1) out[i] = 0.2126 * d[i * 4] + 0.7152 * d[i * 4 + 1] + 0.0722 * d[i * 4 + 2];
  return out;
}

/**
 * Crop two images to their shared top-left size. Element screenshots of
 * equal boxes can differ by one row or column when a box sits on a
 * fractional pixel; the crop keeps the comparison aligned.
 */
export function cropToCommon(a, b) {
  assertImage(a, 'a');
  assertImage(b, 'b');
  const width = Math.min(a.width, b.width);
  const height = Math.min(a.height, b.height);
  const crop = (img) => {
    if (img.width === width && img.height === height) return img;
    const data = new Uint8Array(width * height * 4);
    for (let y = 0; y < height; y += 1) data.set(img.data.subarray(y * img.width * 4, (y * img.width + width) * 4), y * width * 4);
    return { width, height, data };
  };
  return [crop(a), crop(b)];
}

/** Mean absolute RGB difference between two same-size images, 0 to 255. */
export function meanAbsDiff(a, b, { margin = 0 } = {}) {
  assertImage(a, 'a');
  assertImage(b, 'b');
  sameSize(a, b);
  const { x0, y0, x1, y1 } = interior(a, margin);
  let sum = 0;
  let count = 0;
  for (let y = y0; y < y1; y += 1) {
    for (let x = x0; x < x1; x += 1) {
      const i = (y * a.width + x) * 4;
      sum += Math.abs(a.data[i] - b.data[i]) + Math.abs(a.data[i + 1] - b.data[i + 1]) + Math.abs(a.data[i + 2] - b.data[i + 2]);
      count += 3;
    }
  }
  return count ? sum / count : 0;
}

/** Mean luma over the interior. */
export function meanLuma(img, { margin = 0 } = {}) {
  const L = luma(img);
  const { x0, y0, x1, y1 } = interior(img, margin);
  let sum = 0;
  let count = 0;
  for (let y = y0; y < y1; y += 1) for (let x = x0; x < x1; x += 1) {
    sum += L[y * img.width + x];
    count += 1;
  }
  return count ? sum / count : 0;
}

/**
 * Edge energy: mean of (dL/dx)^2 + (dL/dy)^2 over the interior. Squared, not
 * absolute: the sum of |dL/dx| across one isolated edge equals the step
 * height however soft the edge is, while the sum of squares falls roughly in
 * proportion to the width the blur spreads the step over.
 */
export function gradientEnergy(img, { margin = 0 } = {}) {
  const L = luma(img);
  const { x0, y0, x1, y1 } = interior(img, margin);
  const w = img.width;
  let sum = 0;
  let count = 0;
  for (let y = y0; y < y1 - 1; y += 1) {
    for (let x = x0; x < x1 - 1; x += 1) {
      const i = y * w + x;
      const dx = L[i + 1] - L[i];
      const dy = L[i + w] - L[i];
      sum += dx * dx + dy * dy;
      count += 1;
    }
  }
  return count ? sum / count : 0;
}

/**
 * Horizontal shift s that best explains test(x, y) = control(x + s, y), found
 * by trying every s in [-maxShift, maxShift] and scoring mean |luma error|.
 * A positive s means the test pane shows content from further right, which
 * is what feDisplacementMap does with a red channel above 0.5.
 * Returns { shift, error, errorAtZero }; ties go to the smaller |s|.
 */
export function estimateShift(test, control, { maxShift = 24, margin = 0 } = {}) {
  assertImage(test, 'test');
  assertImage(control, 'control');
  sameSize(test, control);
  const S = Math.max(0, Math.floor(maxShift));
  const Lt = luma(test);
  const Lc = luma(control);
  const { x0, y0, x1, y1 } = interior(test, margin);
  const xa = x0 + S;
  const xb = x1 - S;
  if (xb <= xa || y1 <= y0) throw new RangeError('image is too small for this maxShift and margin');
  const w = test.width;
  const score = (s) => {
    let sum = 0;
    for (let y = y0; y < y1; y += 1) {
      const row = y * w;
      for (let x = xa; x < xb; x += 1) sum += Math.abs(Lt[row + x] - Lc[row + x + s]);
    }
    return sum / ((xb - xa) * (y1 - y0));
  };
  let best = { shift: 0, error: score(0) };
  const errorAtZero = best.error;
  for (let k = 1; k <= S; k += 1) {
    for (const s of [k, -k]) {
      const e = score(s);
      if (e < best.error) best = { shift: s, error: e };
    }
  }
  return { shift: best.shift, error: best.error, errorAtZero };
}

/**
 * Did the url() backdrop filter render? `shift` and `expectedShift` are in
 * image pixels. Status: 'renders' (the expected shift explains the pane),
 * 'no-effect' (the pane matches the control, so the filter was ignored),
 * 'wrong-output' (the pane changed but not as the filter defines).
 */
export function judgeRefraction({ errorAtZero, shift, error, expectedShift }, thresholds = {}) {
  const t = { ...DEFAULT_THRESHOLDS, ...thresholds };
  if (!(errorAtZero >= t.minDiff)) {
    return { renders: false, status: 'no-effect', reason: 'the pane matches the control, so the url() filter was ignored' };
  }
  const shiftOk = Math.abs(shift - expectedShift) <= t.shiftTolerance;
  const residualOk = error <= t.maxResidualRatio * errorAtZero;
  if (shiftOk && residualOk) {
    return { renders: true, status: 'renders', reason: `the pane equals the control shifted by ${shift} px, as the filter defines` };
  }
  return {
    renders: false,
    status: 'wrong-output',
    reason:
      `the pane differs from the control but is not the expected ${expectedShift} px shift ` +
      `(best shift ${shift} px, residual ${error.toFixed(1)} of ${errorAtZero.toFixed(1)})`,
  };
}

/**
 * Did backdrop-filter: blur() render? Status: 'renders' (edges went soft and
 * brightness held), 'no-effect' (the pane matches the control),
 * 'wrong-output' (the pane changed in some other way).
 */
export function judgeBlur({ meanAbsDiff: mad, sharpnessRatio, meanShift }, thresholds = {}) {
  const t = { ...DEFAULT_THRESHOLDS, ...thresholds };
  if (!(mad >= t.minBlurDiff)) {
    return { renders: false, status: 'no-effect', reason: 'the pane matches the control, so blur() was ignored' };
  }
  if (Math.abs(meanShift) > t.maxMeanShift) {
    return {
      renders: false,
      status: 'wrong-output',
      reason: `average brightness moved by ${meanShift.toFixed(1)}; a blur keeps it, so the pane drew something else`,
    };
  }
  if (sharpnessRatio <= t.maxSharpnessRatio) {
    return { renders: true, status: 'renders', reason: `edge energy fell to ${(sharpnessRatio * 100).toFixed(2)}% of the control` };
  }
  return {
    renders: false,
    status: 'wrong-output',
    reason: `the pane changed but edges stayed sharp (${(sharpnessRatio * 100).toFixed(2)}% of the control)`,
  };
}

/** Measure the refraction pane against the control. `dpr` scales the expected shift. */
export function analyzeRefraction(testImage, controlImage, { expectedShiftCss = 8, dpr = 1, margin = 4, thresholds } = {}) {
  const [test, control] = cropToCommon(testImage, controlImage);
  const expectedShift = Math.round(expectedShiftCss * dpr);
  const maxShift = Math.max(4, Math.ceil(expectedShift * 3));
  const est = estimateShift(test, control, { maxShift, margin: Math.round(margin * dpr) });
  const verdict = judgeRefraction({ ...est, expectedShift }, thresholds);
  return {
    ...verdict,
    meanAbsDiff: round(meanAbsDiff(test, control, { margin: Math.round(margin * dpr) })),
    shiftPx: est.shift,
    shiftCssPx: round(est.shift / dpr),
    expectedShiftPx: expectedShift,
    residual: round(est.error),
    errorAtZero: round(est.errorAtZero),
  };
}

/** Measure the blur pane against the control. */
export function analyzeBlur(testImage, controlImage, { margin = 16, dpr = 1, thresholds } = {}) {
  const [test, control] = cropToCommon(testImage, controlImage);
  const m = Math.round(margin * dpr);
  const mad = meanAbsDiff(test, control, { margin: m });
  const gTest = gradientEnergy(test, { margin: m });
  const gControl = gradientEnergy(control, { margin: m });
  const sharpnessRatio = gControl > 0 ? gTest / gControl : 1;
  const meanShift = meanLuma(test, { margin: m }) - meanLuma(control, { margin: m });
  const verdict = judgeBlur({ meanAbsDiff: mad, sharpnessRatio, meanShift }, thresholds);
  return { ...verdict, meanAbsDiff: round(mad), sharpnessRatio: round(sharpnessRatio, 5), meanShift: round(meanShift) };
}

/**
 * Tier this engine earned by rendering: 'refract' needs the url() filter to
 * draw, 'frost' needs blur(), otherwise 'solid'. User preferences (reduced
 * transparency, more contrast, forced colors) can still lower it at runtime;
 * explainTier in examples/glass-lab/liquid-glass.js applies those.
 */
export function recommendTier({ refraction, blur }) {
  if (refraction && refraction.renders) {
    return { tier: 'refract', reason: 'the url() backdrop filter rendered the expected displacement' };
  }
  if (blur && blur.renders) {
    return { tier: 'frost', reason: 'blur() rendered but the url() backdrop filter did not' };
  }
  return { tier: 'solid', reason: 'neither backdrop filter rendered' };
}

/**
 * Compare the tier the engine picked by sniffing with the tier the pixels
 * support. 'over' means the sniffed tier is richer than what renders, which
 * ships a broken or invisible effect; 'under' means it leaves an effect that
 * works unused.
 */
export function compareTiers(sniffedTier, renderedTier) {
  const rank = { solid: 0, frost: 1, refract: 2 };
  if (!(sniffedTier in rank) || !(renderedTier in rank)) return { agree: null, direction: 'unknown' };
  if (rank[sniffedTier] === rank[renderedTier]) return { agree: true, direction: 'same' };
  return { agree: false, direction: rank[sniffedTier] > rank[renderedTier] ? 'over' : 'under' };
}

/** Cross-engine comparison of two captures of the same element. */
export function compareCaptures(a, b, { margin = 0, minDiff = DEFAULT_THRESHOLDS.minDiff } = {}) {
  if (a.width !== b.width || a.height !== b.height) {
    return { comparable: false, reason: `sizes differ: ${a.width}x${a.height} vs ${b.width}x${b.height}` };
  }
  const mad = meanAbsDiff(a, b, { margin });
  return { comparable: true, meanAbsDiff: round(mad), similar: mad < minDiff };
}

function round(n, places = 2) {
  const f = 10 ** places;
  return Math.round(n * f) / f;
}
