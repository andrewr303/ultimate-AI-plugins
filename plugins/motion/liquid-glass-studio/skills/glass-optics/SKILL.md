---
name: glass-optics
description: 'Tune and debug the optics of liquid glass style refraction: bezel profile, thickness, index of refraction, strength, bezel width, chromatic aberration, blur, saturation, rim light and tint, plus displacement map encoding (sRGB, neutral 128, channel selectors, filter scale, DPR). Use when the user says the glass "looks flat", "looks like frosted plastic", "edges tear", "corners fold", "rainbow fringes", "content shifts or shimmers", "refraction is too strong", "make the refraction more realistic", or asks how feDisplacementMap maps work. Do not use for choosing a rendering tier or library (glass-library-select), framework wiring (glass-web), native SwiftUI glass, which has no optics knobs (glass-native), or contrast sign-off (glass-accessibility).'
---

# Tune and debug glass optics

Make refraction read as thick glass instead of a blurred card, without tearing, folding, drifting or color fringes the user did not ask for. This skill covers the parameters of the bundled engine and the equivalent knobs in the five studied libraries, the map encoding rules that break most hand-rolled filters, and a symptom table for diagnosis.

## Start here

1. Find out what renders the glass: the bundled engine (`liquid-glass.js` copied from `<plugin-root>/examples/glass-lab/`), one of the studied libraries (check the installed version in the lockfile), or hand-written SVG or shader code.
2. Confirm the active tier before tuning. With the engine, read `data-glass-tier` on the element or `handle.info.tier`. Tuning refraction on a frost or solid tier changes nothing visible.
3. Capture the current look over a busy backdrop with high-contrast edges (stripes, text, a grid). Smooth gradients hide every optical bug.
4. Reproduce the settings in the lab ([glass-lab](../glass-lab/SKILL.md)) when the project uses the engine, so each change is one variable at a time.
5. Change one parameter, compare against the capture, keep or revert.

## The model in one paragraph

Refraction lives in a bezel band along the outline; the flat interior shows the backdrop almost unchanged. A height profile `h(t)` across the bezel gives a surface slope; the engine refracts a straight-down ray through that slope with vector Snell's law and reports how far sideways it lands on the backdrop. The offset is zero at the outer edge and at the interior, peaks inside the band, and saturates at steep walls instead of growing without bound. Corners follow the gradient of a rounded-rectangle distance field. Derivation and the comparison with each library are in [optics.md section 4](../../references/optics.md#4-refraction-models) and the engine header comments.

## Parameters (bundled engine)

Defaults come from `DEFAULTS` in `examples/glass-lab/liquid-glass.js`; typical ranges from [optics.md section 11](../../references/optics.md#11-parameter-guide).

| Option | Default | Start range | Turn it up for | Watch out for |
| --- | --- | --- | --- | --- |
| `profile` | `convexCircle` | see below | shape of the bend | concave samples outward |
| `bezelWidth` | 28 | 8 to 40 px, 10% to 30% of the short side | a thicker-looking rim | clamped to half the short side; text must sit inside it |
| `thickness` | 40 | 10 to 80 px | more bend at the same width | strong values trigger the fold guard |
| `ior` | 1.5 | 1.2 to 1.8 | stronger bend at steep slopes | 1 bends nothing |
| `strength` | 1 | 0.3 to 1.5 | a stylized boost on top of physics | above about 1.5 corners fold |
| `chromaticAberration` | 0 | 0 to 0.3 | color fringes at the rim | three filter passes instead of one |
| `blur` | 3 | 0 to 8 px | frost inside the refract tier | legibility versus clarity |
| `frostBlur` | 14 | 8 to 24 px | the frost tier only | cost grows with radius and area |
| `saturation` | 1.5 | 1.0 to 1.8 | color that blur washes out | below 1 gives a milky veil |
| `specularIntensity`, `lightAngle`, `rimWidth` | 0.7, 135, 3 | 0 to 1, any, 1 to 6 px | edge definition | a bright rim on dark content reads as an outline |
| `shape` | `rounded` | `rounded` or `squircle` | continuous corners | `squircle` changes only the map; clip the element to match |
| `foldGuard` | true | keep on | | off allows mirrored, folded rims |
| `maxPixelRatio` | 2 | 1 to 2 | sharper maps | map memory grows with the square |

Tint is CSS, not an engine option: style `[data-glass-tier="refract"]`, `[data-glass-tier="frost"]` and `[data-glass-tier="solid"]` separately. Tint is the main legibility control and belongs to [glass-accessibility](../glass-accessibility/SKILL.md) as much as to optics.

## Choosing a profile

| Profile | Look | Use for |
| --- | --- | --- |
| `convexCircle` | quarter circle; vertical wall at the edge | default for controls and bars |
| `convexSquircle` | rises faster, settles flatter; bending close to the rim, calm interior | toolbars with text near the edge, large panels |
| `concave` | bowl; samples move outward, level rim with no seam | deliberate lens or inset wells; rarely for chrome |
| `lip` | raised ring then a lower plateau; inward at the rim, slightly outward inside | buttons and knobs that should read as molded |

For library code, [optics.md section 3.6](../../references/optics.md#36-choosing-a-profile) maps the same goals to glasshq, samasante, ybouane and liquidGL settings. Name mapping between libraries is in the second table of optics.md section 11.

## Diagnose by symptom

| Symptom | Likely cause | Fix | Reference |
| --- | --- | --- | --- |
| Looks flat, like frosted plastic | frost tier active; or bezel too thin, thickness or strength too low; or a smooth backdrop | confirm tier; raise `thickness` before `strength`; test over stripes | [web-techniques.md](../../references/web-techniques.md#2-when-to-pick-each-tier) |
| Flat in Safari or Firefox only | `backdrop-filter: url()` does not render there | expected; give frost a rim and top-lit gradient, or change approach in glass-library-select | [research-snapshot.md](../../references/research-snapshot.md) rows W3, W4 |
| Blurs nothing at all | a Backdrop Root ancestor (`opacity` below 1, `filter`, `mask`, `clip-path`, `will-change`) | `findBackdropRoot(el)`; animate `transform` on wrappers instead | [gotchas.md G1](../../references/gotchas.md#g1-glass-blurs-nothing-while-a-wrapper-fades-in) |
| Corners tear or fold, mirrored slivers | displacement no longer one-to-one; bezel wider than corner radius | keep `foldGuard` on; lower `strength`; widen the radius; read "Fold guard: amplitude" in `info.attenuation` | [gotchas.md G22](../../references/gotchas.md#g22-content-folds-or-tears-at-corners-under-strong-refraction) |
| Whole surface shimmers or sits a fraction of a pixel off | 128 is not 0.5; no neutral bias correction | subtract `1/510` from R and G with `feColorMatrix` (the engine does this) | [optics.md 5.2](../../references/optics.md#52-the-128-neutral-pitfall) |
| Constant vertical shift, no vertical bend | `yChannelSelector` reads a channel the map does not fill | read x from R and y from G, as the engine does | [gotchas.md G19](../../references/gotchas.md#g19-vertical-refraction-missing-content-shifted-up-or-down) |
| Bending plateaus abruptly | encoding maps the range past [0, 1] and clips | `byte = 128 + round(127 * d / max)`, `scale = max * 255 / 127` | [gotchas.md G21](../../references/gotchas.md#g21-half-the-displacement-range-saturates) |
| Wide pill refracts like a strip | `preserveAspectRatio="xMidYMid slice"` crops the map | `preserveAspectRatio="none"` and a map at the element's aspect | [gotchas.md G20](../../references/gotchas.md#g20-corners-and-vertical-bending-disappear-on-wide-pills) |
| Rim bend does not follow the rounded corner | map radius differs from CSS radius | one radius for both; the engine reads `border-top-left-radius` when `radius: 'auto'` | [gotchas.md G24](../../references/gotchas.md#g24-refraction-ignores-the-corner-radius) |
| Rainbow fringes nobody asked for | `chromaticAberration` above 0, or a library default | set it to 0; if wanted, keep it under 0.3 | [optics.md section 8](../../references/optics.md#8-chromatic-aberration) |
| Fringes look wrong (red bends most, alpha brightens) | dispersion order or recombination wrong | blue gets the largest scale; take alpha from one pass, not a screen blend | [optics.md section 8](../../references/optics.md#8-chromatic-aberration) |
| Blocky noise or a non-neutral center | JPEG or resampled map | PNG data URLs or runtime maps only | [gotchas.md G18](../../references/gotchas.md#g18-blocky-noise-or-a-constant-offset-from-jpeg-maps) |
| Map values look shifted, refraction weaker than set | linearRGB filter space converts the map | `color-interpolation-filters="sRGB"` on the filter | [optics.md 5.3](../../references/optics.md#53-precision-and-color-space) |
| Soft or blocky edges on a 2x screen | map built at 1x | build at `devicePixelRatio`, capped at 2 | [gotchas.md G25](../../references/gotchas.md#g25-blur-looks-weaker-on-high-dpr-screens) |
| Streaks or clipped content at the rim | reach exceeds the filter region or pad | pad by maximum reach plus blur | [gotchas.md G23](../../references/gotchas.md#g23-edge-pixels-smear-or-clip-at-the-rim) |

## Map encoding rules

1. R holds x, G holds y, B is neutral, A is 255. Always `xChannelSelector="R" yChannelSelector="G"`.
2. `byte = 128 + round(127 * offset / maxDisplacement)`; subtract `128/255 - 0.5` (that is `1/510`) from R and G before displacing; then `scale = maxDisplacement * 255 / 127` so byte 255 means exactly the maximum offset. `encodeDisplacement`, `decodeDisplacement`, `NEUTRAL` and `NEUTRAL_BIAS` in the engine implement this.
3. `color-interpolation-filters="sRGB"` on the `<filter>`.
4. Lossless maps, stretched with `preserveAspectRatio="none"`, generated at the element's size and DPR.
5. Chromatic aberration as three passes with scales `S(1 - ca)`, `S`, `S(1 + ca)` for R, G, B, each reading x from R and y from G, channels kept disjoint, summed, then alpha restored from the green pass.

When writing your own generator, reuse `displacementField`, `specularField` and `buildFilterMarkup` from the engine rather than re-deriving them; they are covered by tests.

## Rules

- Fix the tier and the Backdrop Root before touching optics.
- Raise physical parameters (`thickness`, `ior`, `bezelWidth`) before the stylized `strength` multiplier.
- Keep text out of the bezel band: pad content by at least `bezelWidth`.
- Keep the fold guard on in shipped code.
- Do not ship animated light; static or interaction-driven only.
- Any optics change that touches tint, blur or saturation invalidates the last contrast measurement. Re-measure.
- Cite library behavior with the library and file, as in [optics.md](../../references/optics.md); never from memory.

## Verify

`<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Run plugin scripts from the user's project directory by path; output paths resolve against the current directory.

```sh
node --test <plugin-root>/tests/engine.test.mjs    # profiles, Snell limits, encoding round trip, Jacobian, filter channels
```

- If you changed engine math, add a numeric test next to the existing ones (for example the offset at a known slope or a fold-free field at the new limit), not a source-text assertion.
- Compare before and after screenshots over a striped backdrop in Chromium at DPR 1 and 2. Lab presets help: `?strength=0`, `?chromaticAberration=0.3`, `?foldGuard=0`, `?offset=200`.
- Inspect the generated map: the lab shows it under "Displacement map"; the center and outside must read neutral gray.
- After tint, blur or saturation changes, measure each text element: `node <plugin-root>/scripts/glass_contrast.mjs --url <url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto`.

## References

- [optics.md](../../references/optics.md): model, profiles, Snell, encoding, scale, light, dispersion, blur, tint, parameter guide
- [gotchas.md](../../references/gotchas.md#optics-and-map-encoding): G17 to G26 with sources
- [web-techniques.md](../../references/web-techniques.md): which tier implements which part of the model
- Engine and lab: [examples/glass-lab/README.md](../../examples/glass-lab/README.md), [liquid-glass.js](../../examples/glass-lab/liquid-glass.js)
- Per-library knobs: source notes for [glasshq-liquid-glass](../../references/sources/glasshq-liquid-glass.md), [simple-liquid-glass](../../references/sources/simple-liquid-glass.md), [liquidGL](../../references/sources/liquidgl.md), [ybouane-liquidglass](../../references/sources/ybouane-liquidglass.md) and [liquid-glass-react](../../references/sources/liquid-glass-react.md)
