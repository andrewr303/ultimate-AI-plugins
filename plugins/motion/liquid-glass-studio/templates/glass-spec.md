# Glass spec: {product or feature}

Use this spec before building or changing liquid glass style surfaces. Fill every section; write "not applicable" with a reason rather than deleting a row. Replace each `{placeholder}`. Keep one spec per feature, next to the code it describes.

- **Owner:** {name}
- **Date:** {YYYY-MM-DD}
- **Repository and branch:** {repo}, {branch}
- **Platforms:** {web engines, iOS, macOS, Android, Flutter, React Native}
- **Slowest supported device:** {device, OS, browser, refresh rate}
- **Rendering approach:** {this plugin's engine, a library and version, hand-written CSS, system glass}

## 1. Surface inventory

One row per surface. Only floating controls and navigation should carry glass; content stays opaque or uses a standard material. See `references/design-principles.md` sections 2 and 3.

| ID | Surface | Layer (functional, transient, content) | Variant (regular, clear) | Text and controls on it | Content it can cover | Why glass and not solid |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | {bottom tab bar} | functional | regular | {labels, icons, selected state} | {scrolling feed with photos} | {content must stay visible under navigation} |
| S2 | | | | | | |

**Stacking check:** at most one glass layer over any point of content. List any overlap and how it is resolved: {none, or "S3 menu sits beside S1 after the morph"}.

## 2. Tier plan per engine

Tiers: refract (SVG displacement, Chromium), frost (CSS blur and tint), solid (opaque with a border). Native rows name the system API and its pre-26 fallback.

| Surface | Chromium | Safari and all iOS browsers | Firefox | iOS and macOS 26+ | Older Apple OS | Android | How the tier is chosen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | refract | frost | frost | system glass | `.regularMaterial` | blur at API 31+, scrim below | {engine `detectTier`, `#available`, API level check} |

**Probe expectation:** record what `node <plugin-root>/scripts/glass_probe.mjs --json` should report for each engine, so a review can compare: {chromium: refraction yes, blur yes; firefox: refraction no, blur yes; webkit: refraction no, blur yes}.

## 3. Parameters

Web values per surface (see `references/optics.md`, parameter guide). Native platforms expose no numeric blur or refraction; record the variant, tint and container spacing instead.

| Surface | Radius | Bezel width | Thickness | IOR | Strength | Chromatic aberration | Blur (refract) | Frost blur | Saturation | Tint and opacity | Rim light | Elasticity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | {px or auto} | {px} | {px} | {1.5} | {1} | {0} | {px} | {px} | {1.5} | {token, alpha} | {intensity, angle} | {0 to 1} |

**Tokens used:** {glass tint, solid surface, solid text, border, focus ring colors from the design system}

## 4. Preferences behaviour

| Preference | Signal | Behaviour per surface | Verified how |
| --- | --- | --- | --- |
| Reduced transparency | `prefers-reduced-transparency: reduce`; native Reduce Transparency | solid tier with border | {DevTools emulation, simulator setting} |
| In-product solid toggle | `data-glass-surfaces="solid"` on `<html>`; {setting name and storage key} | solid tier, applied before first paint and live when toggled | {toggle on, toggle off, reload} |
| More contrast | `prefers-contrast: more`; native Increase Contrast | solid or near-solid, stronger border | |
| Forced colors | `forced-colors: active` | system colors, real border, decorative layers hidden | |
| Reduced motion | `prefers-reduced-motion: reduce`; native Reduce Motion | no stretch or travel; morphs become fades | |
| Apple Clear and Tinted (26.1+) | system setting | custom surfaces stay legible under both | |

`prefers-reduced-transparency` is not supported in Safari as of the 2026-11-05 snapshot (MDN browser-compat-data; WebKit bug 175497 still NEW), so the in-product toggle row is required for every web product.

## 5. Motion

| Interaction | Surface | Spring (duration, bounce) | Interruption behaviour | Reduced alternative |
| --- | --- | --- | --- | --- |
| press | S1 | {press 0.24, 0.2} | retarget, keep velocity | {rim brightens, no scale} |
| open menu | {S3} | {morph 0.42, 0.18} | reverses from current point | {appear in place, fade} |

## 6. Performance budget

| Budget | Target | Measured on | Result |
| --- | --- | --- | --- |
| p95 frame time during interaction | {16.7 ms at 60 Hz} | {device} | {pending} |
| Glass script per frame | {4 ms or less} | | |
| Visible refractive surfaces | {count, and the fallback past 12} | | |
| Rendering DPR cap | {2} | | |
| First paint | {frost or solid immediately} | | |

## 7. Acceptance checks

Each check ends as checked, not checked, or not applicable, with evidence. `<plugin-root>` is the liquid-glass-studio plugin folder (two directories above a loaded skill's base directory); run the commands from the project directory.

| # | Check | Command or method | Pass condition |
| --- | --- | --- | --- |
| A1 | Engine tests | `node --test <plugin-root>/tests/engine.test.mjs` | all pass |
| A2 | Engines render what the tier plan expects | `node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --json` | matches section 2 |
| A3 | Worst-case text contrast per surface | `node <plugin-root>/scripts/glass_contrast.mjs --url {url} --selector {glass surface} --text-selector {text elements on it} --require auto --json`, per scroll position, light and dark; text elements, never the container alone | minimum at least 4.5:1, or 3:1 for large text |
| A4 | Boundary and focus ring contrast | sample the ring outside each control | at least 3:1 |
| A5 | Screenshots per tier and preference | real browser, each surface | matches sections 2 and 4 |
| A6 | Keyboard and screen reader | Tab through, VoiceOver or NVDA | every control reachable, named, ring visible and unclipped |
| A7 | Motion interruption and reduced motion | press, reverse, reopen; preference switched mid-animation | section 5 holds |
| A8 | Performance budget | trace and frame pacing on the slowest device | section 6 holds |
| A9 | Native builds | newest SDK and lowest deployment target | builds, fallbacks look designed |

## 8. Open questions

- {question, owner, what it blocks}
