---
name: glass-lab
description: 'Run the bundled Glass Lab, a local page with no network requests that renders the liquid glass style engine over a busy backdrop with live controls for every parameter, to tune glass, compare variants side by side, capture screenshots per tier, and export the chosen settings into the project as engine options and CSS. Use when the user says "let me tune the glass", "show me the refraction live", "compare these two glass looks", "playground for the liquid glass effect", "preview glassmorphism settings", "what does the frost fallback look like", or wants reproducible screenshots for a review. Do not use for production implementation (glass-web), for library selection (glass-library-select), or as evidence that the product page itself is legible (glass-accessibility measures the real page).'
---

# Tune glass in the lab

The lab (`<plugin-root>/examples/glass-lab/index.html`) runs the same engine the project would ship, over a seeded backdrop of colored shapes and text, with a toolbar, a card, a pill button and a switch in glass. Use it to settle parameters one variable at a time, show stakeholders the three tiers, and produce settings and screenshots that can be reproduced from a URL.

## Start here

1. Check what the project renders glass with. The lab tunes the bundled engine; for a library, use it only to explore the look, then map values with the name table in [optics.md section 11](../../references/optics.md#11-parameter-guide).
2. Note the target surface's real size, corner radius and the content it floats over. The lab card is about 360 px wide; a 56 px toolbar needs different values.
3. Start the lab (next section) on a free port that you started yourself.
4. Tune, compare, export, then stop the server you started.

## Run it

The lab ships inside this plugin, not in the user's project. `<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Browsers block ES module imports from `file://`, so serve the folder:

```sh
cd <plugin-root>/examples/glass-lab
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. If port 8000 is taken, pick another free port. Stop the server with Ctrl+C, or by the PID you started if it runs in the background. Never stop a process you did not start.

The tier line at the top of the panel reports the tier and its reason, for example `Tier: frost (url() backdrop refraction is unreliable in engine "webkit")`. Open the lab in Chromium to tune refraction; WebKit and Firefox show the frost tier by design.

## Controls and presets

Every range and select can be preset from the query string, which makes a look shareable and screenshots stable:

| Query key | Engine option or CSS | Example |
| --- | --- | --- |
| `tier` | `tier` override (lowers only) | `?tier=frost`, `?tier=solid` |
| `profile` | `profile` | `?profile=lip` |
| `shape` | `shape` (map only) | `?shape=squircle` |
| `bezelWidth`, `thickness`, `ior`, `strength` | same names | `?thickness=60&ior=1.6` |
| `chromaticAberration`, `blur`, `frostBlur`, `saturation` | same names | `?chromaticAberration=0.2` |
| `specularIntensity`, `lightAngle`, `rimWidth` | same names | `?specularIntensity=0.4` |
| `foldGuard` | `foldGuard` (`0` turns it off) | `?foldGuard=0` |
| `tint` | CSS `--tint` on the glass | `?tint=0.7` |
| `offset` | CSS `--offset`, slides the backdrop under the glass | `?offset=200` |

Values outside a slider's range are clamped. Pointer elasticity is a checkbox only and stays off under reduced motion. The panel readout shows engine, size, map resolution and DPR, max offset, filter scale, neutral bias, fold guard reduction, minimum Jacobian and build time; below it the displacement and specular maps render as images.

## Tuning loop

1. Set the backdrop that matters: drag "Backdrop offset" until the busiest shapes and the white text pass under the card's rim.
2. Pick `profile` first, then `bezelWidth` and `thickness`, then `ior`. Use `strength` last, as a stylistic trim.
3. Watch "Fold guard" in the readout. "amplitude x0.7" means the engine had to reduce the bend to stay fold-free; lower `thickness` or `strength` until it reads "no reduction" if you want the full designed bend.
4. Set `tint`, `blur` and `saturation` for legibility, and read the "Worst-case contrast" note. It is an estimate over flat backdrop colors; it ignores refraction and blur.
5. Check the rim: `specularIntensity`, `lightAngle` and `rimWidth`. On dark content keep the rim thin.
6. Switch `Tier override` to frost and solid. Both must look finished, not broken.
7. Copy the URL. It is the record of the variant.

Diagnosis of anything that looks wrong (tearing, fringes, flat glass) belongs to [glass-optics](../glass-optics/SKILL.md).

## Compare variants side by side

- Open two windows or tabs with different query strings at the same size and offset, for example `?profile=convexCircle&thickness=40&offset=200` and `?profile=lip&thickness=30&offset=200`, and tile them.
- For reviews, capture each variant at the same viewport and DPR with a headless browser you already have. Name the files by variant (`A-convexCircle.png`, `B-lip.png`) and keep them in a scratch or gitignored folder, never a tracked path.
- Change one parameter between variants. If two differ in several, label every difference in the comparison.
- Capture the tier set for each finalist: default (refract in Chromium), `?tier=frost`, `?tier=solid`, and one with emulated `prefers-contrast: more`.

## Export the chosen settings

The lab does not write files. Turn the final URL into project code:

1. Split the query keys into engine options and CSS. Engine options go to `createGlass(element, options)`; `tint` becomes the alpha in the project's tint token per tier; `offset` is lab-only and is dropped.
2. Rescale for the real component. Bezel width and thickness are in CSS px for the lab card. For a smaller surface keep them proportional: the lab itself gives the toolbar, switch row and knob their own `data-glass` values and scales them with the shared sliders. A good start is bezel width at 10% to 30% of the surface's short side.
3. Keep only options that differ from `DEFAULTS` in the engine, so a later engine update can change defaults deliberately.
4. Put the values in one place in the project (a token file or a `glassOptions` constant next to the component) with a comment holding the lab URL that produced them.

```js
// Tuned in Glass Lab: ?profile=convexSquircle&bezelWidth=20&thickness=28&tint=0.62
export const navGlass = { profile: 'convexSquircle', bezelWidth: 20, thickness: 28 };
```

```css
:root { --glass-tint-refract: rgb(255 255 255 / 0.62); --glass-tint: rgb(255 255 255 / 0.70); }
```

5. Re-measure on the product page. Lab legibility does not transfer: the product's backdrop, text and sizes differ.

## Rules

- Serve over http from the lab folder; do not edit the lab to tune a product. Settings live in the project.
- Start only your own server, on a free port, bound to 127.0.0.1; stop only what you started.
- Tune refraction in Chromium; judge frost in WebKit or Firefox, or with `?tier=frost`.
- One variable per comparison; same viewport, DPR and backdrop offset for every capture.
- The lab's contrast note is an estimate. Sign-off needs a measurement on the real page.
- Keep screenshots out of tracked paths unless the user asks for them in the repository.

## Verify

```sh
node --test <plugin-root>/tests/engine.test.mjs     # the lab and the project share this engine
```

- The tier line matches the browser (refract in Chromium, frost in WebKit and Firefox, solid under emulated `forced-colors: active`).
- The browser console shows no errors, and the network panel shows only the local server and `data:` URLs.
- The exported options reproduce the lab look on the product component in Chromium (screenshot both).
- On the product page, from the user's project directory, text element by text element: `node <plugin-root>/scripts/glass_contrast.mjs --url <product url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto`.

## References

- [Glass Lab README](../../examples/glass-lab/README.md): controls, tiers, how the engine works, what was verified
- [liquid-glass.js](../../examples/glass-lab/liquid-glass.js): `DEFAULTS`, `createGlass`, `explainTier`
- [optics.md](../../references/optics.md#11-parameter-guide): ranges and the cross-library name table
- [accessibility.md](../../references/accessibility.md#2-worst-case-backdrop-contrast): the real contrast method
