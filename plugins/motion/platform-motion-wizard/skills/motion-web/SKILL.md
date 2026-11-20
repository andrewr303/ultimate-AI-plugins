---
name: motion-web
description: "Implement robust web interaction motion in CSS, WAAPI, React/Next, Vue, or Svelte. Use for animation lifecycle bugs, presence, shared layout, SSR/hydration, live reduced-motion policy, or integration with an existing animation library. Pair with the affected component skill."
---

# Implement motion in a web stack

Read [web implementation](../../references/web-implementation.md), then the selected surface skill. Inspect installed versions, lockfile, existing primitives, SSR strategy, supported browsers, and tests.

## Choose the smallest owner

- CSS transitions for simple stable-state style changes.
- CSS keyframes for finite effects with an explicit lifecycle and reduced alternative.
- WAAPI when imperative playback, cancellation, or retargeting is needed.
- An existing library for shared layout, gestures, presence, or orchestration it already supports.
- View Transitions only as progressive enhancement with an ordinary navigation/update path.

Do not install or upgrade a library for a small transition by default. Check package version and current primary docs before using an uncertain API. Current repository main is not proof the installed release exposes an API.

## Implement the contract

1. Establish stable logical states and IDs. Make the no-animation flow work first.
2. Apply immediate pressed/selected/pending feedback and start work independently.
3. Centralize motion roles and a live preference source, with SSR-safe defaults and subscription cleanup.
4. Attach motion to actual semantic changes, not each render. Preserve keys, input values, focus, and scroll.
5. Retarget active movement from current presentation. Guard generation/request identity so canceled or stale work cannot commit.
6. Coordinate visual presence with primitive-owned focus and dismissal behavior. Never leave a dismissed invisible layer blocking input.
7. Settle or cancel active nonessential motion when the preference changes, including JS animations and programmatic scrolling.
8. Profile required measurement/layout work and verify lifecycle races in the actual browser.

## Lifecycle details that prevent bugs

For a concrete implementation and controllable race fixtures, read [executable recipes](../../references/executable-recipes.md). The bundled scalar controller is a reference for owned effects, not a replacement for the product's framework, presence primitive, focus management, or spring engine.

- A canceled WAAPI finished promise may reject. Handle expected cancellation explicitly; unexpected failures still need visibility.
- Animation finish, cancel, transition cancellation, no-change properties, display:none, unmount, and zero-motion are different paths. No business operation should require an animation event.
- For decorative exits, preserve semantics through the tested overlay primitive; if necessary separate a noninteractive, accessibility-hidden visual layer. Do not hide an ancestor while focus remains inside.
- React effects must clean up under development Strict Mode. Do not create duplicate listeners, timers, observers, or requests.
- During SSR, avoid reading window at module scope. Render useful content before JS and hydrate to a stable state.
- Vue/Svelte transitions and Motion/other presence APIs need the same logical rules. Do not translate lifecycle assumptions blindly across frameworks.
- Do not assume a reduced-motion hook is live because of its name or doc comment. Check implementation/version and exercise a mid-session preference change.
- Avoid competing CSS transform, JS transform, layout projection, and press transforms on one node. Use wrappers or a single motion owner.

## Browser and navigation edges

Feature-detect optional APIs. A missing or skipped View Transition must still apply the update, preserve history/scroll rules, and leave the destination usable. Avoid overlapping transition names and duplicate accessible content.

Respect link semantics, modifier clicks, back/forward, reduced programmatic scroll, safe areas, virtual keyboards, and visual viewport changes. Keep touch-action local to the gesture target; do not disable page scrolling to polish a sheet.

## Acceptance

Run the project's relevant checks and the actual changed flow. Test first-frame interaction, rapid open/close/reopen, current-operation identity, zero-motion cleanup, unmount, keyboard focus, and slow/failing work. Use [review](../motion-review/SKILL.md); report code-only checks separately from browser evidence.
