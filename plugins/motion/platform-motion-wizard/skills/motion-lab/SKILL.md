---
name: motion-lab
description: "Use when an interaction needs a runnable isolated preview, side-by-side motion comparison, or quick tuning feedback before integration. Build a small local lab in the existing stack and validate the real product afterward. Excludes shipping a demo into production without a request."
---

# Motion lab

Make uncertain interaction decisions observable. A runnable comparison should
answer a specific question about feedback, continuity, interruption, or control.
Read the [original interaction baseline](../polish-platform-motion/SKILL.md), then
use only the component skills relevant to the experiment.

## Choose the question

1. Inspect the real component, framework, primitives, tokens, and target devices.
   Name the exact uncertainty: does the menu feel delayed, does a dialog steal
   focus on reopen, or does a transition lose the user's place?
2. Use an existing story, component playground, preview route, or test fixture
   before creating another environment. Keep it outside production navigation.
3. Compare the current interaction and one restrained candidate with identical
   content, geometry, input, and logical states. Add a no-motion path.
4. Record what would decide the comparison before tuning. Prefer observable
   outcomes such as immediate acknowledgment and correct reversal over vague
   scores for being “premium.”

## Build the smallest useful experiment

- Reuse the actual component and accessible primitive when feasible. A mock's
  correctness cannot establish the real component's behavior.
- Keep durations and easing editable through the existing token owner. Show
  units and current values; label sample values as authored starting points.
- Never let controls override the operating system's reduced-motion preference.
  A local comparison can further reduce movement; it must not force movement.
- Read preferences initially and subscribe to changes. Settle or cancel active
  nonessential motion without losing state, focus, or pending operations.
- Keep state changes independent from transition completion. No semantic action
  may require an animation event or a tuning delay to finish.
- Give async examples deterministic success, failure, cancellation, and repeated
  input. Label simulations visibly. Do not imply that a simulated result saved
  data or completed a real request.
- Provide controls to deliver obsolete responses after replacement or cancellation.
  Count actual deliveries and ignored results; timer cancellation alone does not
  establish stale-result protection. Assert an animation is active before
  testing its interruption. See [executable recipes](../../references/executable-recipes.md).
- Use generation identity or equivalent ownership so old animation and async
  callbacks cannot overwrite a new instance. Clear owned work on disposal.
- Expose keyboard and pointer controls for replay and reset. Keep target geometry
  stable and focus visible. Native links, scrolling, and dismissal stay usable.
- Use the [dependency-free example](../../examples/motion-lab/index.html) only as
  a starting surface when no product playground exists. Its native dialog and
  simulated response do not replace stack-specific implementation or testing.

## Observe and integrate

1. Test at normal speed first. Exercise first-frame input, rapid close/reopen,
   selection changes, canceled input, and failed requests.
2. Repeat with reduced motion enabled before load and changed during the effect.
   Check live updates in the actual installed animation hooks, not just CSS.
3. Use keyboard and the supported touch/pointer environment. Check focus entry,
   return, scroll, dialog background inertness, and state announcements.
4. Capture short temporal evidence if available. A screenshot records stable
   appearance; it cannot prove interruption safety or smoothness.
5. Integrate the selected change through shared tokens and the existing component
   owner. Recheck the real application: routing, portals, network behavior,
   theme, viewport, and framework lifecycle can change the result.

## Deliver

Return the runnable lab location and launch command, the question compared, the
chosen parameters and reason, real observed checks, and remaining limitations.
For an implementation request, complete the production component change and its
appropriate verification; the playground is supporting evidence. Do not install
new tooling, expose a server publicly, or add a demo to production navigation
merely to present a comparison.
