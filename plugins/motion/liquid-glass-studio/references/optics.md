# Optics of liquid glass style surfaces

This reference describes the visual model behind refractive glass UI and how each studied library approximates it. Use it to pick a surface profile, set refraction strength, encode displacement maps correctly, and tune light, color and shadow without guesswork.

"Liquid Glass" is Apple's name for its system material. This plugin describes a "liquid glass style" and is not affiliated with Apple.

## Source keys

Every claim about a library cites `<library> <path>`. Paths are relative to each library's root as studied.

| Key | Library | Path prefix used below |
| --- | --- | --- |
| glasshq | `@glass-sdk/liquid-glass` 0.0.2 (MIT, Glass HQ) | `packages/liquid-glass/` |
| simple-liquid-glass | `simple-liquid-glass` 5.7.0 (MIT, lucaperullo); vendors code from samasante/liquid-glass, @ybouane/liquidglass and liquidGL | repository root |
| liquidGL | `liquid-gl` 3.0.0 (MIT, NaughtyDuk) | repository root |
| ybouane | `@ybouane/liquidglass` 1.0.3 (MIT per package.json) | repository root |
| liquid-glass-react | `liquid-glass-react` 1.1.1 (MIT, Max Rovensky) | repository root |

Statements marked **inference** are reasoned from the code or from general optics. They were not observed in a browser.

## 1. The visual model

A glass surface in this style is a stack of effects applied to whatever sits behind it, with the foreground content drawn on top, untouched.

```text
backdrop pixels
  -> optional frost (blur, saturation, tone)
  -> refraction (sample the backdrop at an offset that depends on the surface shape)
  -> optional chromatic split (offset differs per color channel)
  -> tint (color the transmitted light)
  -> light (rim stroke, specular, Fresnel brightening)
  -> coverage mask (the shape, antialiased)
  -> shadow outside the shape
foreground content (text, icons) drawn above, not filtered
```

Three observations hold across all five libraries:

- **Refraction lives near the edge.** The flat middle of a panel shows the backdrop almost unchanged. Displacement concentrates in a bezel band along the outline. This is what makes the surface read as thick glass instead of a blurred card.
- **The shape drives everything.** One signed distance field (SDF) for the outline feeds the coverage mask, the bezel profile, the refraction direction, the rim light and the shadow. When the clip shape and the optical shape come from different formulas, corners tear or rims float (see [gotchas.md](gotchas.md)).
- **Text stays live.** Every library keeps foreground content as normal DOM above the effect, so it stays selectable and readable by assistive technology (glasshq `src/dom/compose-layers.ts`; ybouane `src/LiquidGlass.ts`; liquid-glass-react `src/index.tsx`).

## 2. Shape: distance fields and normals

Most libraries drive the optics from a signed distance `d(p)` to the outline: negative inside, zero on the edge, positive outside. ybouane, liquidGL and simple-liquid-glass use the closed-form rounded-box distance popularized by Inigo Quilez (ybouane `src/shaders.ts`; liquidGL `scripts/liquidGL.js`; simple-liquid-glass `src/vendor/samasante/displacement.ts`). glasshq uses a signed distance to a tessellated continuous-corner (squircle) outline (glasshq `src/gpu/maps.wgsl`, `shape`). liquid-glass-react uses a rounded-rectangle SDF only in shader mode and baked map images otherwise (liquid-glass-react `src/shader-utils.ts`, `src/index.tsx`).

Differences that matter:

| Concern | Approach | Source |
| --- | --- | --- |
| Corner curve | Continuous corners (squircle, smoothing 0.8125) from `@lisse/core`, tessellated into the distance field and reused as the CSS `clip-path` | glasshq `src/core/shape.ts` |
| Corner curve | Circular-arc rounded rectangle, radius clamped to half the short side | ybouane `src/shaders.ts`; simple-liquid-glass `src/index.tsx` |
| Normal direction | Gradient of the SDF (outward edge normal) | glasshq `src/gpu/maps.wgsl` |
| Normal direction | Radial direction from the center, blended toward the corner-arc normal with a smoothstep weight near corners | liquidGL `scripts/liquidGL.js` (`cornerNormal`) |
| Normal direction | Central finite differences of a height field (step 2 device px) | ybouane `src/shaders.ts` |
| Radius source | Only `borderTopLeftRadius` is read, so per-corner and elliptical radii are ignored | liquidGL `scripts/liquidGL.js` (`updateMetrics`) |

Recommendation: generate the clip path and the optical field from the same outline. glasshq states this as a design rule ("not a second corner formula", glasshq `src/core/shape.ts`).

## 3. Surface and height functions

A height function `h(x)` gives glass thickness at inset distance `x = -d` from the edge. The bezel profile decides where light bends and how sharp the rim looks. The five sources use five different profiles.

### 3.1 glasshq: circular-arc edge with a fixed bezel

```wgsl
let depth = sat(-d * 0.05);
let edge = 1.0 - sat(sqrt((2.0 - depth) * depth));
```

Quoted from glasshq `src/gpu/maps.wgsl` (also `src/core/optics.ts`, `edgeDisplacement`).

- `depth = clamp(x / 20)`: the bezel is a fixed 20 CSS px band whatever the panel size.
- `edge = 1 - sqrt((2 - depth) * depth) = 1 - sqrt(1 - (1 - depth)^2)`. This is one minus a quarter circle: 1 at the rim, 0 at 20 px inset, with a steep fall just inside the rim.
- Displacement magnitude is `edge * refraction` (default 60 px) and its direction is the inward normal `-n` (glasshq `src/core/materials.ts`, `src/dom/index.ts`).

**Inference.** A quarter-circle bevel of radius `R` has normalized height `h/R = sqrt(t(2 - t))` with `t = x/R`. glasshq's `edge` equals `1 - h/R` with `R = 20 px`. So glasshq displaces in proportion to how far the surface sits below its plateau, not in proportion to its slope. The slope of a quarter circle is unbounded at the rim; this choice keeps the maximum displacement finite and equal to `refraction`.

### 3.2 samasante lens map (vendored in simple-liquid-glass): spherical cap plus lip

simple-liquid-glass `src/vendor/samasante/displacement.ts` builds the lens map from three terms.

1. **Spherical-cap dome.** Cap height `h = curvature * min(halfW, halfH)`. Sphere radius from chord and cap, `R = (a^2 + h^2) / 2h`. The dome slope `x / sqrt(R^2 - x^2)` is rescaled so its mean over the half extent is 0.5, using the closed form `mean = (R - sqrt(R^2 - H^2)) / H`.
2. **Erf feather.** An inner rounded rectangle inset by `depthPx = min(depth * minHalf, minHalf - 1)` gates displacement with `edgeOpacity = 0.5 * (1 + erf(innerSdf * SQRT1_2 / depthPx))`, with `erf(x)` approximated by `tanh(sqrt(pi) * x)`.
3. **Lip (meniscus) bump.** In a band of width `bendWidth * min(halfW, halfH)` inside the rim, an extra inward push shaped as

   ```ts
   const m = 6.75 * s * s * (1 - s);
   ```

   Quoted from simple-liquid-glass `src/vendor/samasante/displacement.ts`. `m` is 0 at both ends of the band, peaks at `s = 2/3`, and the constant 6.75 normalizes the peak to exactly 1.

Profiles tune these per use: `player` (default, controls) uses strength 0.16, depth 0.2, curvature 0.55, bend 0.25; `loupe` (magnifier) uses depth 0.95; `track` (slider tracks) uses strength 0.03 (simple-liquid-glass `src/core/nativeOptics.ts`). The source comments advise pairing bend with a gentler curvature so the body stays slightly magnified and the rim reads as the glass thickness (paraphrase of simple-liquid-glass `src/vendor/samasante/displacement.ts`).

### 3.3 ybouane: circular bevel height field

In our notation, with inset distance `x` and bevel radius `zR`:

```text
h(x) = 0                      for x <= 0
h(x) = sqrt(x * (2 zR - x))   for 0 < x < zR
h(x) = zR                     for x >= zR
```

This is a circular arc that plateaus at `zR`, written here from the behavior of ybouane `src/shaders.ts` (`bevelHeight`); no code is reproduced. `zR = zRadius * DPR` (default 40 CSS px).

- The height rises with infinite slope at the edge and plateaus at `zR` inset.
- Normals come from central differences of `h` with a 2 device px step: five SDF evaluations per fragment.
- On the plateau the normal points straight up, so gradient refraction vanishes. A separate center pull `-p / half * refraction * 4 * depth` adds mild global magnification (ybouane `src/shaders.ts`).
- `bevelMode: 1` switches to a dome magnifier: sample position scaled toward the center by `1 - 0.35 * refraction * depth`. With the default `refraction = 0.69` that is about 1.32x magnification (derived from the formula). Pair `cornerRadius === zRadius` for a half-sphere (ybouane `src/defaults.ts`).

### 3.4 liquid-glass-react: smoothstep corner map

Shader mode generates a displacement PNG on a CPU canvas (liquid-glass-react `src/shader-utils.ts`, adapted from shuding/liquid-glass per its header comment). In our notation, for a point `p` centered on the element in normalized units:

```text
dist  = sdf_roundrect(p; half extents 0.3 x 0.2, radius 0.6)
s     = smoothstep(0, 1, smoothstep(0.8, 0, dist - 0.15))
sample position = p * s + 0.5
```

This paraphrases the fragment in liquid-glass-react `src/shader-utils.ts`; no code is reproduced, because the upstream license of that file is unverified. The result is a "pull toward center" whose strength `1 - s` is near zero over most of the surface. The radius 0.6 exceeds both half extents (0.3, 0.2), so the SDF degenerates to a corner-weighted circular falloff. **Inference** from re-implementing the formula: `s` is about 0.98 at edge midpoints and about 0.35 at corners, so the map bends strongly only near corners.

The default `standard`, `polar` and `prominent` modes use fixed 256 px baked images instead of a height function (liquid-glass-react `src/utils.ts`).

### 3.5 liquidGL: two-term bevel without a height function

```glsl
float offsetAmt = (edge * u_refraction + pow(edge, 10.0) * u_bevelDepth);
float centreBlend = smoothstep(0.15, 0.45, length(p));
```

Quoted from liquidGL `scripts/liquidGL.js` (lens fragment shader). `edge = 1 - smoothstep(0, bevelWidth * min(w, h), inset)`.

- `refraction` is a linear-ish ramp across the bevel band; `bevelDepth` is an `edge^10` term confined to the last few pixels of the rim, which gives a razor rim.
- `centreBlend` zeroes the offset near the center, where the radial direction is undefined.
- Offset units are snapshot UV (a fraction of the captured document texture), so the same `refraction` value produces more pixels of travel on a taller page (liquidGL `scripts/liquidGL.js`, `_renderLens`).

### 3.6 Choosing a profile

| Goal | Profile | Why |
| --- | --- | --- |
| UI chrome (toolbars, tabs, buttons) | Fixed-width circular arc (glasshq) or low-depth cap with lip (samasante `player`/`track`) | Refraction stays in a thin rim; the center stays legible |
| Magnifier or hero lens | Dome magnifier (ybouane `bevelMode: 1`) or high-depth cap (samasante `loupe`) | Uniform zoom across the plateau |
| Razor-sharp rim highlight | `edge^10` rim term (liquidGL `bevelDepth`) | Concentrates bending in a few pixels |
| Physically motivated shading | Height field plus finite-difference normals (ybouane) | One normal drives refraction, dispersion, Fresnel and specular |

## 4. Refraction models

### 4.1 What feDisplacementMap does

The SVG filter primitive used by glasshq, simple-liquid-glass and liquid-glass-react computes

```text
out(x, y) = in(x + scale * (XC(x, y) - 0.5), y + scale * (YC(x, y) - 0.5))
```

where `XC` and `YC` are the map channels picked by `xChannelSelector` and `yChannelSelector`, as fractions in [0, 1]. It samples; it never pushes pixels. A map value above 0.5 makes a pixel show content from further right or down.

### 4.2 Three families

| Family | Formula shape | Used by |
| --- | --- | --- |
| Fixed directional sampling | `offset = -n * f(inset) * strength` with a hand-shaped `f` | glasshq (inward), liquidGL (outward horizontally, inward vertically; inference, see below), samasante map (dome direction times feather) |
| Thin-lens approximation | `offset ~ k * (1 - 1/n) * grad(h)` | ybouane (`refrPow = 1 - 1/ior`, `ior = 1.5`) |
| Vector Snell's law | refract a view ray through the surface normal, march it through the glass thickness | Our engine, `examples/glass-lab/liquid-glass.js` |

**Vector Snell (general optics).** For a unit incident direction `I`, unit normal `N` facing the viewer, and ratio `eta = n1 / n2` (air to glass `1 / 1.5`):

```text
cosi = -dot(N, I)
k    = 1 - eta^2 * (1 - cosi^2)
T    = eta * I + (eta * cosi - sqrt(k)) * N      (total internal reflection if k < 0)
offset = T.xy / abs(T.z) * thickness
```

**Small-angle link (inference).** With the view straight down and a surface tilt `theta`, the transmitted ray deviates by `theta - asin(sin(theta) / n)`, which is about `theta * (1 - 1/n)` for small tilts. Since `tan(theta) = |grad(h)|`, the lateral offset is about `thickness * (1 - 1/n) * |grad(h)|`. ybouane's formula has this shape with an artistic gain (`* 30 * refraction`, entry and exit terms equal), so it is a heuristic scaling of the gradient, not exact Snell (ybouane `src/shaders.ts`).

**Direction convention.** For convex glass the normal tilts outward at the rim, so the transmitted ray bends inward and the rim shows backdrop from inside the shape (inference from Snell's law). glasshq samples inward and matches this. liquid-glass-react's baked maps with negative scale sample from beyond the rim on both axes (liquid-glass-react `src/index.tsx`). liquidGL is mixed: it builds its offset in a y-up frame (`v_uv` from clip space) and adds it unflipped to y-down snapshot UVs, so it samples outward horizontally and inward vertically (inference from code, not observed in a browser; liquidGL `scripts/liquidGL.js`, `flippedUV` and `UNPACK_FLIP_Y_WEBGL`). Both conventions read as glass; outward sampling pulls content from outside the outline into the rim, which compresses it.

### 4.3 Our engine

[`examples/glass-lab/liquid-glass.js`](../examples/glass-lab/liquid-glass.js) is original code. It belongs to the vector Snell family, not to the hand-shaped offset family. The engine source and [`examples/glass-lab/README.md`](../examples/glass-lab/README.md) remain the authority; `tests/docs_drift.test.mjs` fails when option names written here drift from `DEFAULTS` in the engine.

**Cross section.** The engine works in a 2D slice perpendicular to the edge. `u` is the inward distance in px and `t = u / bezelWidth`. The top surface is `z(u) = thickness * h(t)`, where `h` is one of the four `PROFILES` (`convexCircle`, `convexSquircle`, `concave`, `lip`). The bottom of the glass sits on the backdrop plane.

**Vector Snell.** The viewer looks straight down, `I = (0, -1)`. The slope is `m = (thickness / bezelWidth) * h'(t)`, the normal is `N = (-m, 1) / sqrt(1 + m^2)`, and `eta = 1 / ior`. The refracted direction `T` comes from the formula in 4.2, and the ray travels from the surface to the backdrop, so the sideways offset is

```text
D(u) = z(u) * T.u / (-T.z)        (positive: sample from further inward)
```

This has two useful properties. The offset is zero wherever the glass has zero height, so the outer edge never shows a seam. At a vertical wall the factor `T.u / (-T.z)` tops out at `sqrt(ior^2 - 1)` (about 1.12 at `ior = 1.5`), so steep profiles saturate instead of growing without bound. Ignored on purpose: the second interface at the flat bottom, Fresnel loss, and true dispersion. `refractionProfile()` samples `D` across the bezel; `displacementField()` uses a 512-sample table of it.

**From profile to map.** Each map pixel takes `D` at its depth inside a rounded-rectangle distance field and points it along the inward normal (minus the field gradient). The field uses a corner radius of at least `bezelWidth`, so the normal turns smoothly around corners; `bezelWidth` is clamped to half the short side so a pill's center line stays at zero. The outer edge fades to neutral over a band that widens with the rim offset. The map is built at `pixelRatio = min(devicePixelRatio, maxPixelRatio)`.

**Fold guard.** The warp `p -> p + a * d(p)` must stay one-to-one, so the engine measures the smallest Jacobian determinant of the offset field. When it falls below 0.2, the engine bisects for the largest amplitude `a` that keeps it at 0.2 or above. The check runs at `1 + chromaticAberration` times the amplitude, so the blue pass, which bends most, also stays unfolded. The result reports the factor as `attenuation` and the final determinant as `minJacobian`. `foldGuard: false` disables the check for the mirrored-rim look. simple-liquid-glass checks the same criterion (`src/core/displacementField.ts`); the engine's implementation is independent.

**Encoding and neutral bias correction.** After the fold guard, `maxDisplacement` is the largest remaining offset component. Each component is stored as `128 + round(127 * offset / maxDisplacement)` in R (x) and G (y); B stays 128. Because 128/255 is not 0.5 (see 5.2), the filter subtracts `NEUTRAL_BIAS` (1/510) from R and G with an `feColorMatrix` before `feDisplacementMap` reads them.

**filterScale.** After that correction the filter moves a pixel by `S * (byte - 128) / 255`. The engine returns `filterScale = maxDisplacement * 255 / 127` with every map and passes it as the `feDisplacementMap` scale, so byte 255 means exactly `+maxDisplacement` and `decodeDisplacement()` inverts `encodeDisplacement()` through the real filter math. With `chromaticAberration` set to `ca`, the red, green and blue passes use `filterScale * (1 - ca)`, `filterScale` and `filterScale * (1 + ca)`: blue bends most.

## 5. Displacement encoding

A displacement map stores a signed 2D offset in unsigned 8-bit channels.

| Library | X | Y | Other channels | Source |
| --- | --- | --- | --- | --- |
| glasshq | R | G | B = 0.5, A = coverage; separate overlay image for light | glasshq `src/gpu/maps.wgsl` |
| samasante lens map | R | G | B = specular mask (128 none, 255 full) | simple-liquid-glass `src/vendor/samasante/displacement.ts` |
| simple-liquid-glass classic | R | B | gradient-built SVG map | simple-liquid-glass `src/index.tsx`, `src/core/displacementMap.ts` |
| liquid-glass-react | R | B | shader mode copies G into B "for SVG filter compatibility" | liquid-glass-react `src/index.tsx`, `src/shader-utils.ts` |

### 5.1 Encoding rule

For an offset field with maximum magnitude `M` px:

```text
channel = 0.5 + offset / (2 * M)      (in [0, 1])
scale   = 2 * M                       (feDisplacementMap attribute)
```

glasshq follows this exactly: `R,G = 0.5 - n * edge * 0.5` with `scale = 2 * refraction` (glasshq `src/gpu/maps.wgsl`, `src/dom/index.ts`). liquid-glass-react's shader mode writes `dx / maxScale + 0.5`, which maps [-M, M] to [-0.5, 1.5] and clips the stronger half of the range into a plateau (liquid-glass-react `src/shader-utils.ts`).

### 5.2 The 128 neutral pitfall

8-bit channels cannot store 0.5. Byte 128 decodes to 128/255 = 0.50196, so "no displacement" still moves every pixel by `scale * 0.00196` px. At `scale = 320` that is about 0.6 px of drift across the whole surface, enough to shimmer text edges under motion.

Fixes seen in the sources:

- Subtract `1/510` with a `feComponentTransfer` linear intercept on the X and Y channels (simple-liquid-glass `src/core/DisplacementFilter.tsx`).
- Chromium re-quantizes component-transfer lookup tables, so the liquidGL SVG path applies the `-1/510` offset with `feColorMatrix` instead (simple-liquid-glass `src/core/LiquidGLSvgFilter.tsx`).
- Fill outside the map with an exact neutral flood (`rgb(128,128,128)`) composited under the map so out-of-image samples do not read as black (simple-liquid-glass `src/core/materialFilter.ts`).
- Never store maps as JPEG. liquid-glass-react's JPEG maps have centers at R 124 / B 132 and green noise up to 18, which is about 1 px of offset at the default scale of 70 (liquid-glass-react `src/utils.ts`, pixel measurement in the dossier).

### 5.3 Precision and color space

- One 8-bit step equals `scale / 255` px. At `scale = 120`, a step is about 0.47 px. Keep `scale` no larger than the travel you need.
- Set `color-interpolation-filters="sRGB"` on the filter. The SVG default is linearRGB, which converts map values before displacement (liquid-glass-react `src/index.tsx` sets sRGB; the default is general SVG knowledge, inference for this plugin's purpose).
- Use `preserveAspectRatio="none"` on `feImage` so the map stretches to the element box (glasshq `src/dom/map-image.ts`; simple-liquid-glass `src/core/materialFilter.ts`). liquid-glass-react's `xMidYMid slice` crops a square map on a wide pill and drops the vertical gradient (liquid-glass-react `src/index.tsx`).

### 5.4 Map resolution and fold-free fields

- simple-liquid-glass sizes SVG maps at `clamp(64, ceil(max(w, h) * 0.75), 512)` because Chromium resends `feImage` bytes to the GPU process every frame the glass or its backdrop moves (simple-liquid-glass `src/core/nativeMapGeometry.ts`).
- glasshq caps map DPR at 2 and uses 1x maps while shapes move (glasshq `src/gpu/geometry.ts`, `src/dom/index.ts`).
- A displacement `p -> p + scale * field(p)` must stay locally injective, or content folds over itself at corners. simple-liquid-glass checks that the Jacobian determinant stays positive on an N x N grid and widens the neutral edge band as scale grows, attenuating amplitude past a ceiling (simple-liquid-glass `src/core/displacementField.ts`).

## 6. Scale selection

Refraction travel is the single most visible knob. Too little reads as frosted plastic; too much tears corners and smears edges.

Travel here means the largest pixel offset. An `feDisplacementMap` moves a pixel by `scale * (C - 0.5)`, so its travel is at most `scale / 2` (section 4.1). Libraries that expose the filter scale are listed with that scale and the travel it gives; do not copy a scale value into a library whose knob is travel, or the bend doubles.

| Source | Default travel | Notes | Source path |
| --- | --- | --- | --- |
| glasshq | 60 px at the rim over a 20 px bezel | Nested glass: `clamp(0.6 * inset, 0, 8)` px | glasshq `src/core/materials.ts`, `src/dom/index.ts` |
| simple-liquid-glass lens | Filter scale `scale / 160 * strength * hypot(w, h) / sqrt(2)`; the `player` profile uses a fixed norm of 500, giving scale 80 at defaults, so about 40 px of travel | Clamped to +/-320 before normalization; padding uses `scale / 2` as the reach | simple-liquid-glass `src/index.tsx`, `src/core/materialFilter.ts` |
| simple-liquid-glass classic | Filter scale capped at 10% of the short side (travel is half that) | "to prevent extreme tearing" | simple-liquid-glass `README.md`, `src/index.tsx` |
| liquid-glass-react | About 35 px at most: `displacementScale` 70 is the `feDisplacementMap` scale and travel is scale / 2. Button preset 64 and card 100 are scales too; halved over light | Example slider 0 to 200 | liquid-glass-react `src/index.tsx`, `liquid-glass-example/src/pages/index.tsx` |
| liquidGL | `refraction` 0.006 to 0.01 for UI chrome, 0.07 to 0.15 for lenses | Snapshot UV units | liquidGL demos `demos/frost-specular.html`, `demos/true-refraction.html` |
| ybouane | about 60 device px at the outermost rim pixels, about 8 px at 20 px inset (derived) | Can exceed the 20 px sampling pad | ybouane `src/shaders.ts`, `src/defaults.ts` |

Rules of thumb (synthesized from the table; inference):

1. Express travel relative to the short side. 5% to 15% of the short side suits controls; up to 30% suits a deliberate lens.
2. Pad the sampled region by the maximum reach. simple-liquid-glass pads its filter region by `ceil(|scale| * (1 + 0.22 * dispersion) / 2 + 3 * blur + 2)` (simple-liquid-glass `src/core/materialFilter.ts`). ybouane's fixed 20 px pad is smaller than its rim offset, so rim samples clamp to the crop edge.
3. Reduce travel for nested glass and over bright, busy backdrops (glasshq nested clamp; liquid-glass-react `overLight` halves displacement).

## 7. Light: rim, specular and Fresnel

| Library | Model | Key constants | Source |
| --- | --- | --- | --- |
| glasshq | Baked overlay image: a 0.9 px antialiased rim stroke weighted by how vertical the normal is (top and bottom lit), an 18% diffuse glow within about 4.5 px, a dark side shade weighted by horizontal normals | Light 1.0 and dark 0.82 specular; side shade 0.48 light, 0.60 dark | glasshq `src/gpu/maps.wgsl` |
| samasante map | Specular stored in the map's B channel: a sheen band along a diagonal axis with a 16% floor around the whole rim, plus a soft inner glow | `0.16 + 0.84 * axis^1.6`; default sheen angle 50 degrees (`player`) | simple-liquid-glass `src/vendor/samasante/displacement.ts`, `src/core/nativeOptics.ts` |
| ybouane | Fresnel `pow(1 - abs(N.z), 4)` mixed toward white by 0.2; four fixed lights (Blinn-Phong exponents 90, 50, 120 plus a Lambert power 6 bloom); 1.5 px inner stroke biased to the top | `fresnel` default 1.0, `specular` default 0 | ybouane `src/shaders.ts`, `src/defaults.ts` |
| liquidGL | Two time-animated soft blobs added to RGB; no Fresnel or rim term | Peak about +0.18 brightness | liquidGL `scripts/liquidGL.js` |
| liquid-glass-react | CSS gradient ring (1.5 px) cut with `mask-composite: exclude`, angle `135 + 1.2 * mouseX` degrees, drawn twice in `screen` and `overlay` blends so the rim picks up backdrop color | Opacity 0.2 (screen layer) | liquid-glass-react `src/index.tsx` |

Notes:

- **Schlick's approximation (general optics).** `F = F0 + (1 - F0) * (1 - cos(theta))^5`, with `F0 = ((n - 1) / (n + 1))^2 = 0.04` for `n = 1.5`. ybouane's exponent-4 term without `F0` is a stylized variant that whitens rims even when `specular` is 0.
- **Light direction.** ybouane's shader frame is y-down, so its lights with positive y favor the bottom rim while its inner stroke favors the top (inference from ybouane `src/shaders.ts`). Re-check light vectors when porting any shader between y-up and y-down frames.
- **Animated light costs frames.** liquidGL's time-based specular forces continuous rendering while a lens is on screen (liquidGL `scripts/liquidGL.js`, `_needsFrame`). Prefer static or pointer-driven light.

## 8. Chromatic aberration

Real glass refracts short wavelengths more, so blue bends further than red (general optics). Libraries fake this by sampling each channel at a slightly different offset.

| Method | Formula | Source |
| --- | --- | --- |
| Per-channel scale, additive recombine | `scale_c = scale * (1 + 0.22 * dispersion * (1 - c * 0.5))` for c = 0, 1, 2: red +22%, green +11%, blue +0% at `dispersion = 1`; channels isolated with `feColorMatrix` and summed with `feComposite arithmetic k2=1 k3=1` | simple-liquid-glass `src/core/materialFilter.ts`, `src/vendor/samasante/displacement.ts` (`DISPERSION_SPREAD = 0.22`) |
| Three passes, screen blend | Scales `-70`, `-77`, `-84` for R, G, B at defaults (blue displaced 20% more); recombined with two `feBlend mode="screen"`; then a small blur `max(0.1, 0.5 - 0.1 * aberration)` | liquid-glass-react `src/index.tsx` |
| Shader fringe along the normal | `offset_c = +/- chroma * 36 * (0.3 + 0.7 * edge)` device px along `N.xy`, red one way, blue the other | ybouane `src/shaders.ts` |
| Shader fringe proportional to displacement | `chroma = offset * aberration`; red at `-chroma`, blue at `+chroma` | liquidGL `scripts/liquidGL.js` |
| None | No per-channel displacement | glasshq `src/dom/material-graph.ts` |

Notes:

- Tie dispersion to displacement (liquidGL, ybouane) so fringes vanish on the flat center. Constant splits tint the whole panel.
- simple-liquid-glass displaces red the most, the reverse of physical dispersion; liquid-glass-react's baked modes displace blue the most, and its shader mode flips the order (liquid-glass-react `src/index.tsx`). Either reads as glass at small values; pick one order and keep it.
- liquidGL's README says blue moves further than red, but its shader splits red and blue symmetrically (liquidGL `README.md` vs `scripts/liquidGL.js`).
- Every extra channel pass is another full displacement primitive or two more texture fetches. simple-liquid-glass disables dispersion at `quality='low'` (simple-liquid-glass `src/index.tsx`).

## 9. Blur, saturation, tone and tint

### 9.1 Order of blur and refraction

| Order | Effect | Source |
| --- | --- | --- |
| Blur, then refract | The frosted backdrop is bent; rims keep a soft look | glasshq `src/dom/index.ts`; simple-liquid-glass lens path (`README.md`); liquid-glass-react (blur in `backdrop-filter`, displacement in `filter`) |
| Sample sharp and blurred, mix with a rim mask | Rim stays slightly sharper: `col = mix(sharp, blur, 1 - 0.15 * edge)` | ybouane `src/shaders.ts` |

### 9.2 Blur recipes

| Source | Recipe | Source path |
| --- | --- | --- |
| glasshq Regular | `blur(sigma 7.33)` plus a fill blur (sigma 23 light, 21.8 dark) blended with `lighten`/`darken`, mixed at 0.34 light / 0.65 dark; Clear has no blur | glasshq `src/dom/material-graph.ts`, `src/core/materials.ts` |
| liquid-glass-react | `blur((overLight ? 12 : 4) + 32 * blurAmount px)`; default 6 px | liquid-glass-react `src/index.tsx` |
| ybouane | Six H+V passes of a 9-tap Gaussian, step `2.5 * blurAmount` texels; total sigma about `10.3 * blurAmount` device px, not scaled by DPR | ybouane `src/GlassRenderer.ts`, `src/shaders.ts` |
| liquidGL | 16 random-disc taps of radius `frost * 4` texels (noisy, not separable) | liquidGL `scripts/liquidGL.js` |
| simple-liquid-glass fallback | `blur(8 to 11 px) saturate(>= 180%)` plus a top-lit white gradient | simple-liquid-glass `src/index.tsx` |

Normalize blur radius by DPR; ybouane's undivided step halves the visible blur on a 2x display.

### 9.3 Saturation and tone

- Saturation above 100% restores color that blur washes out. Defaults: 140% (liquid-glass-react, simple-liquid-glass), 110% to 115% for simple-liquid-glass `frosted`/`clear` presets (simple-liquid-glass `src/materials.ts`), 1.10 light / 1.06 dark in glasshq Regular (glasshq `src/dom/material-graph.ts`).
- Saturation below 100% gives the milky "veil" look (simple-liquid-glass `src/vendor/samasante/displacement.ts` comments).
- glasshq applies a quadratic tone curve `a + b*v + q*v^2` blended at 0.80 light / 0.90 dark for Regular, and a shadow-lift / highlight-rolloff curve for Clear, so stacked layers stay distinct (glasshq `src/dom/material-graph.ts`).
- Luma weights differ: Rec.709 in simple-liquid-glass's shader, Rec.601 in ybouane (simple-liquid-glass `src/core/webgl/optics.ts`; ybouane `src/shaders.ts`). Either works for saturation; use Rec.709 or WCAG relative luminance for contrast math.

### 9.4 Tint

| Model | Formula | Source |
| --- | --- | --- |
| Luminance-transmitting | Desaturate to luminance `L`; `out_c = tint_c * (body + (1 - body) * L)`; `alpha = body + (1 - body) * A`; `body = 0.78` Regular, `0.68` Clear; rim light recolored by slope `(0.45 + 0.55 * tint_c)` | glasshq `src/dom/material-graph.ts` |
| Multiplicative dye | `rgb = mix(rgb, rgb * tint.rgb, tint.a)` | liquidGL `scripts/liquidGL.js` |
| Fixed cool cast | `mix(col, col * (0.92, 0.95, 1.05), tintStrength)` | ybouane `src/shaders.ts` |
| Translucent background layer | semi-transparent `glassColor` behind content; opaque values rejected | simple-liquid-glass `src/index.tsx`, `src/core/background.ts` |
| Darkening layers | black layer at 20% plus black `overlay` blend layer when `overLight` | liquid-glass-react `src/index.tsx` |

glasshq's comment states the reason: "Colored glass transmits luminance" so a pale backdrop brightens the pigment without removing its chroma and dark detail stays visible (glasshq `src/dom/material-graph.ts`). A multiplicative dye darkens everything and mutes backdrop colors far from the tint hue (inference). Tint the glass, not the text (glasshq `README.md`).

## 10. Shadows

| Library | Shadow | Source |
| --- | --- | --- |
| glasshq | None on surfaces; resting slider and switch faces use a small CSS `box-shadow` | glasshq `src/styles.css` |
| simple-liquid-glass | CSS: inset top and bottom rims plus `0 6px 18px #00000018` (lens path) | simple-liquid-glass `src/index.tsx` |
| liquidGL | Static CSS `box-shadow` on a sibling div; in fluid mode a GPU SDF shadow (two 31-tap Gaussian passes at half resolution), drawn at 10% strength with interleaved-gradient-noise dithering to avoid 8-bit banding | liquidGL `scripts/liquidGL.js` |
| ybouane | In-shader SDF shadow outside the shape: 65% Gaussian plus 35% exponential contact term, offset in y, inside the 20 px pad | ybouane `src/shaders.ts` |
| liquid-glass-react | `0 12px 40px rgba(0,0,0,.25)`, heavier when `overLight` | liquid-glass-react `src/index.tsx` |

Keep shadows soft and low: glass is light, and a heavy shadow reads as an opaque card. Size any shader pad to the shadow spread, or the shadow clips at the canvas edge (ybouane `src/defaults.ts` `SHADOW_PAD = 20`).

## 11. Parameter guide

Typical ranges are synthesized from the defaults and presets cited above; treat them as starting points (inference).

The "Engine option" column gives the `createGlass()` option in [`examples/glass-lab/liquid-glass.js`](../examples/glass-lab/liquid-glass.js) and its default from `DEFAULTS`. "None" means the engine leaves that look to your CSS or does not model it.

| Parameter | Typical range | Visual effect | Cost | Engine option (default) |
| --- | --- | --- | --- | --- |
| Refraction travel | 4 to 24 px for controls; 40 to 100 px for lenses (or 5% to 30% of the short side) | How far rim content bends | Free in shaders; in SVG it widens the filter region and the sampled area | Derived, not set: `thickness` (40), `ior` (1.5) and `strength` (1) give the travel (see 4.3 for the resulting filter scale) |
| Bezel width | 8 to 40 px, or 10% to 30% of the short side | Width of the bending band; wider reads thicker | Map regeneration on change | `bezelWidth` (28) |
| Bezel profile | circle, squircle, bowl or raised ring | Where in the band the bending sits | Map regeneration on change | `profile` (`'convexCircle'`), `shape` (`'rounded'`) |
| Lip or rim term | 0 to 0.5 | Extra push just inside the rim | Negligible | `profile` set to `'lip'` (a profile, not a separate amount) |
| Magnify | 1.0 to 1.35 | Uniform zoom of the plateau | Negligible | None: the interior is flat by design |
| Frost blur | 0 to 24 px (CSS) | Legibility versus clarity | High; grows with radius and area | `blur` (3) inside the refract filter; `frostBlur` (14) for the frost tier |
| Saturation | 100% to 180% | Restores or boosts color under blur | Low | `saturation` (1.5) |
| Dispersion | 0 to 0.3 of travel | Colored fringes at the rim | Two extra passes or fetches | `chromaticAberration` (0, range 0 to 1) |
| Specular / rim light | 0 to 1 | Edge definition and gloss | Low if static; continuous frames if animated | `specularIntensity` (0.7), `lightAngle` (135), `rimWidth` (3) |
| Fresnel | 0 to 1 | Rim whitening at grazing angles | Low | None |
| Tint strength | 0 to 0.6 alpha | Color identity; contrast support | Low | None: style the tint per `data-glass-tier` in CSS |
| Shadow | blur 8 to 40 px, alpha 0.1 to 0.3 | Lift off the backdrop | Low in CSS; pad cost in shaders | None: CSS `box-shadow` |
| Fold guard | on for UI | Keeps the rim from mirroring | One pass over the map, about 25 when it has to lower the amplitude | `foldGuard` (true) |
| Map resolution | 1 to 2 map pixels per CSS px | Sharpness of the bent edge | Map size grows with the square | `maxPixelRatio` (2) |
| Pointer pull | 0 to 0.3 | Small stretch toward the pointer | A transform per pointer frame | `elasticity` (0) |

Name mapping across libraries:

| Concept | glasshq | simple-liquid-glass | liquidGL | ybouane | liquid-glass-react | Engine option |
| --- | --- | --- | --- | --- | --- | --- |
| Refraction travel | `refraction` (px of travel; filter scale is 2x) | `scale`, `displacementScale` (filter scale, travel is half), `lensOptions.strength` | `refraction` (UV) | `refraction` | `displacementScale` (filter scale, travel is half) | derived from `thickness`, `ior`, `strength` |
| Bezel width | fixed 20 px | `lensOptions.depth`, `bendWidth` | `bevelWidth` | `zRadius` | n/a (baked maps) | `bezelWidth` |
| Rim term | n/a | `lensOptions.bend` | `bevelDepth` | n/a | n/a | `profile` `'lip'` |
| Magnify | n/a | `lensProfile="loupe"` | `magnify` | `bevelMode: 1` | n/a | n/a |
| Blur | `material="regular"` | `blur` | `frost` | `blurAmount` | `blurAmount` | `blur`, `frostBlur` |
| Saturation | built into Regular | `saturation` | n/a | `saturation` | `saturation` | `saturation` |
| Dispersion | n/a | `dispersion` x `aberrationIntensity` | `aberration` | `chromAberration` | `aberrationIntensity` | `chromaticAberration` |
| Specular | baked overlay | `lensOptions.specular`, `sheen`, `glow` | `specular` (bool) | `specular`, `edgeHighlight` | rim gradient layers | `specularIntensity`, `lightAngle`, `rimWidth` |
| Fresnel | n/a | n/a | n/a | `fresnel` | n/a | n/a |
| Tint | `tint` (`#rrggbb`) | `glassColor` | `tint` (CSS color) | `tintStrength` | `overLight` | CSS per tier |
| Shadow | n/a | built-in CSS | `shadow` | `shadowOpacity`, `shadowSpread`, `shadowOffsetY` | built-in CSS | CSS |
| Corner radius | `radius` | `radius` | element `border-radius` | `cornerRadius` | `cornerRadius` | `radius` (`'auto'` reads `border-radius`) |

Sources for the mapping: engine `DEFAULTS` in `examples/glass-lab/liquid-glass.js`; glasshq `src/core/materials.ts`, `src/react/surface.tsx`; simple-liquid-glass `src/index.tsx`, `src/core/nativeOptics.ts`; liquidGL `scripts/liquidGL.js` (defaults block); ybouane `src/defaults.ts`; liquid-glass-react `src/index.tsx`.

## Related references

- [web-techniques.md](web-techniques.md): how each rendering tier implements this model in a browser.
- [browser-support.md](browser-support.md): which engines render which tier.
- [gotchas.md](gotchas.md): numbered failure modes, many of them optical.
