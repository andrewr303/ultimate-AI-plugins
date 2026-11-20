# Motion for liquid glass style UI

Motion is half of what makes glass read as "liquid": it gives under a finger, swells on press, stretches when dragged, and grows out of the control that opened it. Done badly, it is lag, jank and "motion for motion's sake" (Nielsen Norman Group, https://www.nngroup.com/articles/liquid-glass/, checked 2026-11-05). This reference covers elasticity models from the studied libraries, morphing on the web and in SwiftUI, interruption, reduced-motion alternatives, and pointer handling that does not re-render on every move.

## Source keys

Library claims cite `<library> <path>`: glasshq (paths under `packages/liquid-glass/`), simple-liquid-glass, liquidGL (`scripts/liquidGL.js`), ybouane, liquid-glass-react. Platform facts cite a URL and "checked 2026-11-05". Formulas are quoted briefly with attribution; code samples here are original. **Inference** marks reasoning not observed in a running build.

## 1. Principles

1. **Small things give, big things are heavy.** glasshq: "Controls give a little under the finger; surfaces only at their edges" and "Larger glass is heavier" (glasshq `src/dom/interaction.ts`).
2. **Every animation can be interrupted and reversed from where it is.** Springs that keep velocity on retarget make this free (glasshq `src/core/spring.ts`).
3. **Content waits for room.** A morphing menu shows its items only once the glass is big enough to hold them (glasshq `src/core/morph-path.ts`).
4. **Time is real time.** Use the actual frame delta, so 120 Hz screens and dropped frames do not change the speed (section 6).
5. **Reduced motion removes travel and stretch, not feedback** (section 7).
6. **One motion vocabulary.** glasshq names six springs and reuses them everywhere "so motion reads as one material" (glasshq `src/core/spring.ts`).

## 2. Elasticity models compared

| Library | Press | Hover and pointer | Drag | Engine | Source |
| --- | --- | --- | --- | --- | --- |
| liquid-glass-react | `scale(0.96)` while pressed | stretch toward the cursor within 200 px of the edge, translate toward it | none | CSS transitions, 0.2 s | liquid-glass-react `src/index.tsx` |
| glasshq | grow up to 16%, spring | pointer-positioned glow (fine pointers only) | rubber-banded follow with volume-preserving stretch | analytic springs | glasshq `src/dom/interaction.ts`, `src/core/spring.ts` |
| liquidGL | none built in | shape deforms toward pointer velocity, exponential smoothing | 1:1 translate, no inertia | per-frame smoothing | liquidGL `scripts/liquidGL.js` |
| simple-liquid-glass | turbulence animation toggle | spring lean toward the cursor | none | per-frame Euler spring | simple-liquid-glass `src/interactive/spring.ts`, `src/interactive/index.tsx` |
| ybouane | `zRadius x 0.8`, shadow spread x 1.2, instant | brightness + 0.2, instant | 1:1 translate | none | ybouane `src/LiquidGlass.ts` |

### 2.1 liquid-glass-react: edge-distance stretch

From liquid-glass-react `src/index.tsx` (quoted in short):

- Distance is measured from the pill's **edge**, not its center: `edgeDistance = hypot(max(0, |dx| - w/2), max(0, |dy| - h/2))`.
- Activation zone 200 px; `fade = 1 - edgeDistance / 200`, zero beyond.
- `stretchIntensity = min(centerDistance / 300, 1) * elasticity * fade`.
- `scaleX = 1 + |nx| * I * 0.3 - |ny| * I * 0.15`, and the mirror for `scaleY`, each floored at 0.8: stretch along the pointer axis, squash across it.
- Translation toward the cursor: `(mouse - center) * elasticity * 0.1 * fade` px.
- Reference presets: button `elasticity 0.35`, card `elasticity 0` (liquid-glass-react `README.md`, example page).

What to keep: the edge-distance zone and the stretch-across-squash shape. What to fix: it sets React state on every `mousemove` and reads layout in render, has no leave reset (the glass stays stretched), treats a coordinate of 0 as "no pointer", and listens to mouse events only (liquid-glass-react `src/index.tsx`; see [gotchas.md](gotchas.md#g46-pointer-movement-re-renders-every-layer)).

### 2.2 glasshq: springs and volume-preserving stretch

Named springs, parameterized by perceptual duration (s) and bounce (glasshq `src/core/spring.ts`):

| Spring | Duration | Bounce | Use |
| --- | --- | --- | --- |
| press | 0.24 | 0.2 | the material catching a finger or pointer |
| release | 0.5 | 0.42 | gel-like overshoot back to rest |
| glow | 0.42 | 0 | light settling in and out |
| morph | 0.42 | 0.18 | growing out of or into another shape |
| layout | 0.4 | 0.16 | layout changes, tab indicator |
| track | 0.18 | 0 | a selection lens following a drag |

Mapping to physics: `omega = 2 * PI / duration`, stiffness `k = omega^2`, damping `c = 4 * PI * (1 - bounce) / duration` for bounce >= 0 (glasshq `src/core/spring.ts`). The step uses the closed-form damped oscillator, so a long frame does not destabilize it, and settles when `|x| < 1e-4 * scale` and `|v| < 1e-3 * scale`.

Interaction formulas (glasshq `src/dom/interaction.ts`):

- **Grow on press:** `min(0.16, 8 / max(w, h)) * press`. Small controls grow up to 16%; a 400 px panel grows 2%.
- **Rubber band:** `sign(o) * L * (1 - 1 / (|o| * 0.55 / L + 1))` (glasshq `src/core/spring.ts`), with limit `L = 4 + 0.15 * max` for controls up to 72 px and `min(10, 3 + 0.04 * max)` for surfaces. Small controls measure drag from the press origin; large ones only past their edges.
- **Stretch:** `ex = min(cap, 0.5 * |tx| / w + 0.00007 * |vx| + 0.00005 * |carried|)`, cap 0.2 for small controls and 0.12 for large. Scale is volume-preserving: `sx = (1 + grow)(1 + ex) / sqrt(1 + ey)`, `sy = (1 + grow)(1 + ey) / sqrt(1 + ex)`.
- **Heavier when larger:** drag-follow spring duration `0.18 + 0.0005 * max(w, h)`.
- **Glow:** 1 on press, 0.35 on hover, hover only under `(hover: hover) and (pointer: fine)`; size `clamp(0.9 * max, 36, 180)` px.
- **Keyboard:** Space and Enter press with a centered glow.
- **Writes only `translate`, `scale` and custom properties**, so an author's `transform` still composes.
- The innermost interactive surface claims a press; ancestors see the event but do not react.

### 2.3 liquidGL: smoothing toward pointer velocity

liquidGL deforms the lens shape itself rather than scaling the element (liquidGL `scripts/liquidGL.js`): `follow = 1 - exp(-dt / (25 + viscosity * 180))`, `settle = 1 - exp(-dt / (80 + viscosity * 620))`, displacement `min(size * 0.12, speed * 45) * strength * exp(-(now - lastMove) / 70)` along the velocity. Exponential smoothing with real `dt` is frame-rate independent and cheap, but it has no overshoot, so it reads as viscous rather than springy.

### 2.4 simple-liquid-glass: a lesson in frame dependence

Its pointer spring steps `v = (v + (target - x) * stiffness) * damping; x += v` once per frame (simple-liquid-glass `src/interactive/spring.ts`). Inference: on a 120 Hz display it runs twice as fast as on 60 Hz. Its changelog also records a feedback loop where the spring chased itself because the transformed rect was measured; the fix subtracts the current translation before computing the center (simple-liquid-glass `CHANGELOG.md`, `src/interactive/index.tsx`).

## 3. A press and stretch recipe

An original sketch that applies the lessons above: pointer events, one `requestAnimationFrame` loop that sleeps when settled, springs with real `dt`, measurement on press rather than per frame, writes to `scale` and `translate` only, keyboard parity, and reduced motion.

```js
// Spring parameterization from glasshq src/core/spring.ts:
// k = (2*PI/duration)^2, c = 4*PI*(1 - bounce)/duration.
function spring(value, opts) {
  const s = { value, target: value, velocity: 0, k: 0, c: 0 };
  s.configure = ({ duration, bounce }) => {
    s.k = (2 * Math.PI / duration) ** 2;
    s.c = (4 * Math.PI * (1 - Math.max(0, bounce))) / duration;
    return s;
  };
  s.step = (dt) => {
    let left = Math.min(dt, 0.064);              // a tab switch should not fling the glass
    while (left > 0) {
      const h = Math.min(left, 1 / 240);           // substeps keep explicit integration stable
      s.velocity += (-s.k * (s.value - s.target) - s.c * s.velocity) * h;
      s.value += s.velocity * h;
      left -= h;
    }
    const done = Math.abs(s.value - s.target) < 1e-4 && Math.abs(s.velocity) < 1e-3;
    if (done) { s.value = s.target; s.velocity = 0; }
    return !done;
  };
  return s.configure(opts);
}

const PRESS = { duration: 0.24, bounce: 0.2 };     // glasshq springs.press
const RELEASE = { duration: 0.5, bounce: 0.42 };   // glasshq springs.release

export function attachGlassPress(el) {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const press = spring(0, PRESS);
  let size = 1, raf = 0, last = 0;

  const frame = (now) => {
    const dt = last ? (now - last) / 1000 : 1 / 60;
    last = now;
    const moving = press.step(dt);
    const grow = reduced.matches ? 0 : Math.min(0.16, 8 / size) * press.value;
    el.style.scale = grow ? String(1 + grow) : '';
    el.style.setProperty('--glass-press', press.value.toFixed(3));   // drives glow or tint in CSS
    raf = moving ? requestAnimationFrame(frame) : 0;
    if (!raf) last = 0;
  };
  const go = (target, opts) => {
    press.configure(opts).target = target;
    if (!raf) raf = requestAnimationFrame(frame);
  };
  const down = () => {
    size = Math.max(el.offsetWidth, el.offsetHeight) || 1;   // layout size, unaffected by scale
    go(1, PRESS);
  };
  const up = () => go(0, RELEASE);

  el.addEventListener('pointerdown', down);
  el.addEventListener('pointerup', up);
  el.addEventListener('pointercancel', up);
  el.addEventListener('pointerleave', up);
  el.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && !e.repeat) down(); });
  el.addEventListener('keyup', (e) => { if (e.key === ' ' || e.key === 'Enter') up(); });
  return () => cancelAnimationFrame(raf);
}
```

Attach it to a real `<button>`. Under reduced motion the scale stays at 1, while `--glass-press` still drives a visible state change (a brighter rim or a stronger tint) in CSS. For drag stretch, add `tx` and `ty` springs that follow the pointer through a rubber band, and compute `scale` with the volume-preserving formula in section 2.2.

## 4. Morphing shapes

The open-source reference for web glass morphing is glasshq; the other four libraries have no shape-morph API (liquidGL and simple-liquid-glass follow live geometry, so a host animation can drive them; liquid-glass-react and ybouane have none).

### 4.1 glasshq: a planned path of prepared shapes

Refraction maps are baked per shape, so a morph cannot regenerate maps every frame. glasshq plans the path ahead (glasshq `src/core/morph-path.ts`, `src/dom/morph.ts`):

1. **Shape over progress.** The axis the popup opens along leads with `1 - (1 - t)^1.6`; the cross axis follows with `t^1.4`. Past 1, the spring's overshoot swells the shape evenly. In flight the corners become drop-like (at least `0.34 * min(w, h)`), blended in by a bulge that fades between progress 0.35 and 0.8, so the shape only takes its final corners near arrival.
2. **Stops.** Sample 240 fine shapes and place stops evenly by a shape distance `|ln(w1/w2)| + |ln(h1/h2)| + |r1 - r2| / max(4, min/2)`. Use 14 stops with a liquid neck, 10 without; WebKit halves the count (minimum 4) because it decodes every map a filter switches to during an already slow frame.
3. **Resolution.** The two endpoints are resting shapes at full DPR and persist in the map cache; in-between stops use 1x maps (glasshq `src/dom/index.ts`).
4. **Cross-fade.** Each frame draws the two stops around the current progress and blends their maps with `feComposite operator="arithmetic" k2=1-mix k3=mix` (glasshq `src/dom/map-blend.ts`). Arithmetic blends quantize displacement at low alpha, so blended placements keep the full sampling reach (glasshq `src/dom/index.ts`, `src/dom/sampling-bounds.ts`).
5. **Late maps.** If a stop's maps are not ready, the nearest prepared plain map is stretched as a stand-in. An entrance waits at most 140 ms for its path maps without spending animation time (glasshq `src/dom/morph.ts`, `src/dom/index.ts`).
6. **Content.** Content is clipped to the live outline each frame, so the glass opens to reveal it rather than scaling it. Content reveal is `smoothstep(0.4, 0.9, p)` and the source's own content withdraws with `smoothstep(0.02, 0.3, p)`; CSS turns these into opacity and a small blur (`blur((1 - m) * 6px)` in, `blur(m * 3px)` on the source) (glasshq `src/core/morph-path.ts`, `src/styles.css`).
7. **Placement first.** Popups settle a frame after mount, so the entrance waits for two stable frames (at most 8) before drawing glass (glasshq `src/dom/morph.ts`).

### 4.2 Become versus detach, and the liquid neck

- **become:** the popup replaces its source glass; the source's material and content hide during the morph (glasshq `src/dom/morph.ts`). Use it for a button that turns into its menu.
- **detach:** a drop leaves its source glass and pinches off. While the drop is within `neckWidth(p) = neck * (1 - smoothstep(0.3, 0.95, p))` of the source (default `neck` 18 px), frames use a smooth union of the two rounded rectangles, so a liquid bridge connects them and thins until it breaks (glasshq `src/core/morph-path.ts`).
- **The union:** signed distances of both rounded rectangles combined with a polynomial smooth minimum, quoted from glasshq `src/core/union.ts`:

```ts
const h = Math.max(k - Math.abs(a - b), 0) / k;
return Math.min(a, b) - h * h * k * 0.25;
```

  The zero contour is traced with marching squares at 1.5 px and simplified to at most 700 edges; plans are cached (16) in source-local coordinates so fractional scrolling does not change map keys (glasshq `src/core/union.ts`, `src/core/morph-path.ts`).
- **Submenus** do not travel from their row; they fade in place in 0.22 s with no bounce, and siblings hand the panel off by morphing the outgoing panel's box (glasshq `src/dom/morph.ts`, `src/dom/exit-handoff.ts`).
- **Toolbar spacers** split a cluster that grows out of its neighbor with `detach`; removed clusters stay as inert, `aria-hidden` ghosts until their exit finishes (glasshq `src/react/toolbar.tsx`).

### 4.3 Morphing on cheaper tiers

On frosted CSS (no maps), morph with FLIP: measure the source and target boxes, animate `clip-path: inset(... round r)` or `border-radius` plus `transform` with the Web Animations API, and fade content in after about 40% of the progress (the glasshq reveal window above is a good default). Inference: animating `clip-path` on a backdrop-filtered element repaints the blur each frame; keep morphing surfaces small.

## 5. SwiftUI `glassEffectID` morphing

SwiftUI does the planning for you inside a `GlassEffectContainer`. Pair views across states with `glassEffectID(_:in:)` and change state inside an animation (https://developer.apple.com/documentation/swiftui/view/glasseffectid(_:in:), checked 2026-11-05):

```swift
struct ShareCluster: View {
    @State private var open = false
    @Namespace private var glass

    var body: some View {
        GlassEffectContainer(spacing: 16) {
            HStack(spacing: 16) {
                if open {
                    Button("Copy link", systemImage: "link") { }
                        .labelStyle(.iconOnly)
                        .padding(12)
                        .glassEffect()
                        .glassEffectID("copy", in: glass)
                }
                Button(open ? "Close" : "Share",
                       systemImage: open ? "xmark" : "square.and.arrow.up") {
                    withAnimation(.spring(duration: 0.42, bounce: 0.18)) { open.toggle() }
                }
                .labelStyle(.iconOnly)
                .padding(12)
                .glassEffect(.regular.interactive())
                .glassEffectID("share", in: glass)
            }
        }
    }
}
```

- `glassEffectID` and `glassEffectTransition` only act during view hierarchy transitions or animations. Without `withAnimation`, the change is instant.
- `.matchedGeometry` (the default within the container's spacing) morphs nearby shapes; `.materialize` fades content and animates the material for shapes that appear far from a partner; `.identity` disables the transition (https://developer.apple.com/documentation/swiftui/glasseffecttransition, checked 2026-11-05).
- Larger container spacing makes shapes start blending sooner (https://developer.apple.com/documentation/swiftui/glasseffectcontainer, checked 2026-11-05).
- `.spring(duration:bounce:)` uses the same perceptual parameters as glasshq's springs, so a web and native implementation can share one motion spec (the value 0.42 / 0.18 above is glasshq's `morph` spring, not an Apple constant).
- System morphs (menus, toolbars, sheets) already have Apple's motion. Do not rebuild them with custom glass to change timing.

## 6. Interruption and retargeting

- **Retarget, do not restart.** Set a new target on the running spring and keep its velocity. glasshq's `Spring` documents this: "Retargeting keeps the current velocity, so every animation built on it can be interrupted and reversed mid-flight" (glasshq `src/core/spring.ts`).
- **Reverse from the current point.** Reopening a menu mid-exit runs the same path forward from where it is, with a fresh bounded wait if the maps were interrupted (glasshq `src/dom/morph.ts`).
- **Keep exiting elements mounted until the spring settles.** glasshq holds Base UI's exit with a dummy `element.animate([{}, {}], { duration })` until the spring is within 1% of rest, then emits `glass:exited` (glasshq `src/dom/morph.ts`).
- **Real `dt`, stable integration.** Analytic springs (glasshq) or substepped integration (section 3) with the real frame delta. Reset the previous timestamp after idle so the first frame after a pause is not a giant step (glasshq `src/dom/morph.ts`; tests in `src/dom/morph.test.ts`, `src/dom/interaction.test.ts`).
- **Avoid CSS transitions for interruptible glass physics.** A CSS transition retargeted mid-flight restarts its easing curve from the current value with zero velocity (inference from how transitions work); liquid-glass-react's `transition: all ease-out 0.2s` shows the resulting stiffness. Use springs in script for anything the user can reverse.
- **Freeze while waiting.** If assets are not ready, hold the animation still rather than spending its time, as glasshq's "quiet" mode does (glasshq `src/dom/interaction.ts`).

## 7. Reduced-motion alternatives

| Motion | Full | Reduced alternative |
| --- | --- | --- |
| Press grow or shrink | spring scale | no scale; brighter rim, stronger tint, or inset border |
| Hover lean and stretch | elastic follow | none; optional static highlight |
| Drag stretch | volume-preserving stretch | position follows the pointer 1:1 with no stretch |
| Popup morph from source | planned shape path | appear in place; fade content in (glasshq: "materialize in place") |
| SwiftUI morph | `glassEffectID` with `.matchedGeometry` | `.glassEffectTransition(.materialize)` or `.identity` under `accessibilityReduceMotion` |
| Tab indicator travel | layout spring | jump to the new tab; short crossfade |
| Animated turbulence, specular sweep, tilt | continuous | off |
| Click ripple | expanding ring | off, or a static pressed state |

glasshq: system reduced motion always overrides `motion="full"`; `"reduced"` removes stretch and travel; `"none"` also removes transitions (glasshq `src/dom/interaction.ts`, `README.md`). simple-liquid-glass stops its turbulence, pointer spring and ripples and reacts to live preference changes (simple-liquid-glass `src/index.tsx`, `src/interactive/index.tsx`). liquidGL, ybouane and liquid-glass-react do nothing.

```css
@media (prefers-reduced-motion: reduce) {
  .glass, .glass * { transition-duration: 0.01ms !important; animation: none !important; }
  .glass[data-pressed] { box-shadow: inset 0 0 0 2px currentColor; }   /* feedback without movement */
}
```

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion
// ...
.glassEffectTransition(reduceMotion ? .materialize : .matchedGeometry)
```

Listen for live changes on the web (`matchMedia(...).addEventListener('change', ...)`) so a user who turns the setting on mid-session gets the reduced version immediately.

## 8. Pointer handling without re-renders

The most common motion bug in glass components is re-rendering a component tree on every pointer move (liquid-glass-react sets two React states per `mousemove` and calls `getBoundingClientRect()` several times per render, liquid-glass-react `src/index.tsx`).

Rules:

1. **Use pointer events, passive, and coalesce into one frame.** Store the latest event; apply it in `requestAnimationFrame`.
2. **Write styles directly**, not framework state: individual transform properties (`translate`, `scale`) and CSS custom properties for light position. glasshq writes only these (glasshq `src/dom/interaction.ts`); simple-liquid-glass writes the transform imperatively and causes React renders only for consumed state changes (simple-liquid-glass `src/interactive/index.tsx`).
3. **Measure rarely.** Measure on `pointerenter` and on `ResizeObserver`, using layout size (`offsetWidth`) or a rect taken while the springs are at rest. If you must measure while moving, subtract your own translation first (simple-liquid-glass `CHANGELOG.md`).
4. **Reset on leave and cancel.** Return springs to rest on `pointerleave` and `pointercancel`.
5. **Hover effects only for fine pointers:** gate with `matchMedia('(hover: hover) and (pointer: fine)')` (glasshq `src/dom/interaction.ts`).
6. **Do not compare coordinates to 0 as "unset".** Use `null` (liquid-glass-react bug, `src/index.tsx`).
7. **Prevent native drag of links and images inside pressed glass**, or the browser cancels the press with `pointercancel` (glasshq `src/dom/interaction.ts`).

```js
export function trackGlassLight(el) {
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  let rect = null, pending = null, raf = 0;

  const apply = () => {
    raf = 0;
    if (!pending || !rect) return;
    el.style.setProperty('--glass-light-x', `${pending.clientX - rect.left}px`);
    el.style.setProperty('--glass-light-y', `${pending.clientY - rect.top}px`);
    el.style.setProperty('--glass-light', '0.35');
  };
  el.addEventListener('pointerenter', () => { if (fine.matches) rect = el.getBoundingClientRect(); });
  el.addEventListener('pointermove', (e) => {
    if (!rect) return;
    pending = e;
    if (!raf) raf = requestAnimationFrame(apply);
  }, { passive: true });
  el.addEventListener('pointerleave', () => {
    rect = pending = null;
    el.style.setProperty('--glass-light', '0');
  });
  addEventListener('scroll', () => { rect = null; }, { passive: true, capture: true });  // re-measure on next enter
}
```

```css
.glass::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: radial-gradient(120px circle at var(--glass-light-x, 50%) var(--glass-light-y, 0%),
              rgb(255 255 255 / calc(var(--glass-light, 0) * 0.6)), transparent 70%);
}
```

This sketch drops the light on scroll until the next `pointerenter`; for a light that must follow during scroll, re-measure inside `apply` instead, once per frame.

## Related references

- [accessibility.md](accessibility.md#7-reduced-motion) for the reduced-motion requirement
- [performance.md](performance.md#6-frame-scheduling-and-skipping) for loop scheduling
- [native.md](native.md#13-swiftui-recipes) for more SwiftUI glass code
- [gotchas.md](gotchas.md#interaction-and-framework-integration) for interaction failure modes
