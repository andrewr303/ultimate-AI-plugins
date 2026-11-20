---
name: glass-web
description: 'Implement liquid glass style surfaces on the web in the project stack: vanilla JS, React or Next.js, Vue or Nuxt, Svelte or SvelteKit, web components, and server rendering. Builds the solid, frost and refract tiers in that order, wires the bundled dependency-free engine (or an installed library) with unique filter ids, tier styling, Backdrop Root checks, live preference changes and cleanup. Use when the user asks to "add liquid glass to the navbar", "build a glass button or toolbar in React", "glassmorphism CSS", "frosted glass header", "Apple glass effect on the web", "SVG refraction with backdrop-filter", or reports glass breaking under SSR or hydration. Do not use for picking among libraries (glass-library-select), optical tuning (glass-optics), native apps (glass-native) or a review-only request (glass-review).'
---

# Implement glass on the web

Ship glass that always renders something correct: an opaque surface everywhere, frost where `backdrop-filter` works, and refraction only where it actually renders. Use the project's own framework patterns, the bundled engine or an already chosen library, and leave focus, semantics and content untouched.

## Start here

1. Inspect the project: framework and version, router, SSR or static output, build tool, CSP rules, supported browsers, and any installed glass library with its exact version.
2. Read existing surface, radius, focus and motion tokens. Find the component that should become glass (often a nav bar or toolbar) and what scrolls under it.
3. If the approach is not decided, run [glass-library-select](../glass-library-select/SKILL.md) first. Default: the bundled engine for Chromium refraction with frost elsewhere.
4. Confirm the design decisions in [glass-design](../glass-design/SKILL.md) exist: which surfaces, variant, tint, radius, and the three tier looks.
5. Build the tiers in order (next section), then wire the engine, then verify each tier in a real browser.

## Tier order: solid, then frost, then refract

Write the CSS so the page is correct before any script runs and when every script fails. Define the tokens once on `:root` from the design system's opaque surface, text and border colors; [glass-accessibility](../glass-accessibility/SKILL.md) uses the same names, so do not redefine them on `.glass`.

```css
:root {
  --glass-solid: Canvas;          /* map each to a design-system token */
  --glass-solid-ink: CanvasText;
  --glass-solid-line: color-mix(in srgb, CanvasText 30%, transparent);
}
.glass {                                     /* solid: always valid */
  background: var(--glass-solid);
  border: 1px solid var(--glass-solid-line);
  color: var(--glass-ink, var(--glass-solid-ink));
}
@supports ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass {                                   /* frost: any engine with backdrop-filter */
    background: var(--glass-tint);
    border-color: var(--glass-line);
    -webkit-backdrop-filter: blur(var(--lg-frost-blur, 14px)) saturate(var(--lg-saturation, 1.5));
    backdrop-filter: blur(var(--lg-frost-blur, 14px)) saturate(var(--lg-saturation, 1.5));
  }
}
.glass[data-glass-tier="refract"] { background: var(--glass-tint-refract); }
.glass[data-glass-tier="solid"],
:root[data-glass-surfaces="solid"] .glass {
  background: var(--glass-solid);
  border-color: var(--glass-solid-line);
  color: var(--glass-solid-ink);
  -webkit-backdrop-filter: none;
  backdrop-filter: none;
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more) {
  .glass {
    background: var(--glass-solid); color: var(--glass-solid-ink); border-color: var(--glass-solid-line);
    -webkit-backdrop-filter: none; backdrop-filter: none;
  }
}
@media (forced-colors: active) {
  .glass { background: Canvas; color: CanvasText; border-color: CanvasText; backdrop-filter: none; }
}
```

- Refraction is added by script only, never by CSS: `@supports` proves `backdrop-filter` parses, not that `url()` displacement renders ([research-snapshot.md](../../references/research-snapshot.md) row W8).
- `prefers-reduced-transparency` is not supported in Safari as of the 2026-11-05 snapshot (row W11). Offer an in-app "Solid surfaces" setting that sets `data-glass-surfaces="solid"` on the `<html>` element. That one attribute drives both paths: the `:root[data-glass-surfaces="solid"]` rule above, and the engine, which watches the attribute and switches every instance to `solid` live. Set it before first paint; [glass-accessibility](../glass-accessibility/SKILL.md#build-the-solid-tier-and-the-toggle) has the inline script.
- Never hide surfaces until JavaScript runs. The frost or solid look is the first paint.

## Use the bundled engine

1. Copy `<plugin-root>/examples/glass-lab/liquid-glass.js` into the project (for example `src/vendor/liquid-glass.js`). In a TypeScript project, also copy `liquid-glass.d.ts` from the same folder next to it (`src/vendor/liquid-glass.d.ts`), so the import is typed and a strict typecheck does not fail with TS7016. Keep the attribution header at the top of both files. `<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Add the plugin's MIT notice (copyright line and license text from the plugin `LICENSE`) to the project's third-party notices.
2. Record the source and date in a comment or the notices file, so a later upgrade can diff against the plugin.
3. Do not edit the math in place. If you must, also copy `<plugin-root>/tests/engine.test.mjs`, fix its import path, update the `.d.ts` to match, and keep it passing in the project's test runner.
4. Call it on the client only:

```js
import { createGlass } from './vendor/liquid-glass.js';

const handle = createGlass(navEl, { bezelWidth: 20, thickness: 28, profile: 'convexSquircle' });
// handle.tier            'refract' | 'frost' | 'solid'
// handle.info            size, map scale, fold guard, build time (after first render)
// handle.update({ tier: 'frost' })   per-instance override; it can only lower the tier
//                                   (the page-wide solid setting is the data-glass-surfaces attribute)
// handle.destroy()       removes the filter, listeners and observers; restores inline styles
```

What the engine does for you: picks the tier with `explainTier` (forced colors, the page's `data-glass-surfaces="solid"` setting, reduced transparency and more contrast give solid; no `backdrop-filter` gives solid; non-Chromium gives frost), writes `data-glass-tier` and the `--lg-frost-blur` and `--lg-saturation` custom properties, injects one zero-specificity stylesheet for the frost and solid tiers that any author rule overrides (the inline `backdrop-filter` is used only for the refract tier's per-instance filter), builds DPR-aware PNG maps, caches them, rebuilds on resize in one animation frame, swaps to a new versioned filter id on each rebuild, listens for live preference changes, warns about Backdrop Root ancestors, and never touches `outline`, focus styles or content. Tune options with [glass-optics](../glass-optics/SKILL.md) or [glass-lab](../glass-lab/SKILL.md).

## Framework wiring

Every framework follows the same contract: create after mount, update on option change, destroy on unmount, and never read `window` or `navigator` during render. Details and library-specific traps are in [web-techniques.md section 4](../../references/web-techniques.md#4-framework-integration).

| Stack | Where to create | Where to destroy | Notes |
| --- | --- | --- | --- |
| Vanilla | after the element exists (`DOMContentLoaded` or module end) | when the element is removed | one handle per element |
| React, Next.js | `useEffect` with a ref | the effect cleanup | Strict Mode mounts twice in development; cleanup must fully undo, which `destroy()` does. Mark the module `"use client"` in the App Router |
| Vue, Nuxt | `onMounted`, or a custom directive `mounted` | `onBeforeUnmount` or directive `unmounted` | in Nuxt, keep the import in client-only code |
| Svelte, SvelteKit | an action: `use:glass={options}` returning `{ update, destroy }` | the action's `destroy` | actions run only in the browser |
| Web components | `connectedCallback` | `disconnectedCallback` | call `createGlass` on the host element itself (inference: the engine puts its filter in the document, and fragment references from inside a shadow root may not resolve there) |
| SSR, static | nowhere on the server | | importing the module in Node is safe (no DOM at import); render the solid or frost CSS on the server |

Pass options as a stable object; call `handle.update(next)` when they change rather than destroying and recreating.

## Filter ids

- One filter per instance. Shared ids make every instance use whichever filter the document finds first ([web-techniques.md 4.1](../../references/web-techniques.md#41-rules-for-every-framework)).
- Ids must start with a letter and use only letters, digits, `-` and `_`. `buildFilterMarkup` throws otherwise. React `useId()` values contain colons; strip them before use.
- The engine versions ids (`lgs-<instance>-<version>`) and swaps to a new filter on every rebuild, because Chromium can keep a cached result when a filter's children change under the same id ([gotchas.md G35](../../references/gotchas.md#g35-chromium-does-not-repaint-after-a-filter-graph-edit)).
- The engine's SVG host is zero-size and absolutely positioned, not `display: none`, which would disable the filter in Chromium.

## Backdrop Root

`backdrop-filter` only sees content painted up to the nearest ancestor with `opacity` below 1, a `filter`, `mask`, `clip-path`, `backdrop-filter`, `mix-blend-mode` or a matching `will-change` ([web-techniques.md section 6](../../references/web-techniques.md#6-the-backdrop-root-rule)).

- The engine logs a warning naming the ancestor and property. In a console, `findBackdropRoot(el)` returns `{ element, property }` or `null`.
- Common culprits: a page-transition wrapper fading `opacity`, a layout wrapper with `will-change: opacity`, a `filter: drop-shadow()` on a header container.
- Fix by animating `transform` on the wrapper, moving the fade onto siblings, or moving the glass outside the wrapper.

## Using a library instead

Follow the library's documentation at the installed version, then wrap it behind the same component interface you would give the engine, so the solid and frost CSS and the `data-glass-*` attributes still apply. Each source note lists the library's fallback, accessibility gaps and known bugs: start from [library-matrix.md](../../references/library-matrix.md) and the linked note. Add what the library lacks (usually the solid tier for preferences and a visible focus style).

## Rules

- Solid first, frost second, refraction last. Each tier is a finished look.
- Refraction through `backdrop-filter: url()` is a Chromium-only enhancement; gate it by engine, never by `@supports` alone.
- Never remove or restyle the focus outline to suit the glass. Interactive glass uses real `<button>`, `<a>` or form elements.
- Text and icons are normal DOM above the effect, padded past the bezel.
- Never read `window` or `navigator` during server render or module scope.
- Destroy every handle on unmount; no orphan filters, observers or listeners.
- Do not add a glass library or upgrade one for a small change; check the installed version before using any API.

## Verify

```sh
node --test <plugin-root>/tests/engine.test.mjs   # run from the project; or the copied test in the project's runner
```

- Run the project's own lint, typecheck and tests. A TS7016 "Could not find a declaration file" error means `liquid-glass.d.ts` was not copied next to the `.js` file.
- Open the real page in Chromium and confirm `data-glass-tier="refract"`; in WebKit and Firefox confirm `frost`. Screenshot each.
- Emulate `prefers-contrast: more`, `forced-colors: active` and (Chromium) `prefers-reduced-transparency: reduce` in DevTools Rendering; confirm `solid` and a visible border. Flip one while the page is open; the tier must follow without a reload.
- Tab through the glass controls; the focus ring stays visible over the busiest backdrop.
- Mount and unmount the component repeatedly; the count of `filter[id^="lgs-"]` elements returns to its earlier value.
- Turn on the solid surfaces setting while the page is open; every surface must switch to `solid` without a reload.
- Measure text on glass, element by element, from the project directory: `node <plugin-root>/scripts/glass_contrast.mjs --url <dev url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto --screenshot contrast.png`. Never measure only the container: its one color is compared with every pixel of the box, including controls with their own fills.

## References

- [web-techniques.md](../../references/web-techniques.md): tiers, detection, framework rules, SSR, capture limits, Backdrop Root
- [browser-support.md](../../references/browser-support.md): engine matrix and a detection sketch
- [gotchas.md](../../references/gotchas.md): compositing, engine and framework failure modes
- [accessibility.md](../../references/accessibility.md) and [performance.md](../../references/performance.md)
- Engine and lab: [examples/glass-lab/README.md](../../examples/glass-lab/README.md)
