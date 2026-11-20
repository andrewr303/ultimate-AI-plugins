# Accessible interaction reference

This is an implementation aid for the plugin's focused motion pass. It is not a certification checklist. Read the applicable normative standard and evaluate the actual product scope before making conformance claims.

## Preference and presentation policy

Use a single product policy with explicit presentations for ordinary and reduced motion. Observe the system preference and any further-reducing user preference. The reduced path preserves information, controls, and logical outcomes while omitting nonessential travel, scaling, parallax, and repetition. Prefer an immediate endpoint; a brief fade may be appropriate after checking context and comfort.

Audit every motion owner. A CSS media query cannot govern an imperative scroll, animation library, canvas loop, or native gesture runtime by itself. Live preference changes need cancellation and cleanup as well as a different value for future animations.

Use explicit lifecycle states such as closed/opening/open/closing only when useful. Keep logical state separate from presentation progress. A removed animation must not remove the only completion callback that releases a lock or pending flag.

## Closing surfaces

| Responsibility | Question to resolve |
| --- | --- |
| Interaction | When does the dismissed content stop receiving input? |
| Semantics | When does it leave accessible navigation? |
| Focus | Where does focus go if the trigger disappeared? |
| Ownership | Can an older completion affect a newer opening? |
| Modality | Which primitive owns nested locks, inertness, and focus containment? |
| Cleanup | Does the same release path work after cancel, unmount, or zero motion? |

Do not hide an ancestor of the active focus. Avoid duplicate interactive transition clones. Preserve the accessible component primitive's lifecycle hooks instead of installing a competing focus trap.

## Relevant standards, with scope

The following are prompts for a focused review, not a complete list of requirements:

| Criterion or pattern | Relevance |
| --- | --- |
| [WCAG Animation from Interactions, 2.3.3, AAA](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | Nonessential interaction-triggered movement can be disabled. “Essential” is a narrow exception, not a synonym for intended visual design. |
| [WCAG Dragging Movements, 2.5.7, AA](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html) | A single-pointer method without dragging is evaluated separately from keyboard access. A move menu or adjacent tap controls can support both. |
| [WCAG Keyboard, 2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) | Review operability of the actual custom interaction. |
| [WCAG Focus Order, 2.4.3](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html) | Review meaningful progression as content opens, closes, or moves. |
| [WCAG Pause, Stop, Hide, 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | Check applicability to automatically moving or updating content; it differs from interaction-triggered movement. |
| [WCAG Status Messages, 4.1.3](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | Review meaningful asynchronous status without unnecessary focus changes. |
| APG modal dialog pattern | A reference for contained tab order, Escape dismissal, naming, initial focus, and logical focus return; APG is guidance, not a conformance certificate. |

For any cited failure, record the trigger, affected users, observed behavior, relevant requirement, expected result, and reproduction steps. Do not turn a preferred easing curve into a standards violation.

## Platform-specific traps

- Browser: CSS reduction and JavaScript state can disagree; listen where needed and guard SSR. An invisible overlay may still block clicks or receive focus.
- React Native: a synchronous startup preference hook is not necessarily a subscription. The inspected Reanimated hook returns a captured startup value; use the live platform change event when required.
- Compose: alpha changes do not remove the composable from composition or accessible semantics. Model removal intentionally.
- Flutter: inspect both platform preference flags in the installed SDK and separate the app's custom motion policy from framework controller behavior.

## Source notes

Read on 2026-10-21. Standards and long-lived platform guidance are retained for authority; they are not claimed to be newly published this month.

- [W3C: Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html): explains interaction motion, essential movement, and preference-based disabling.
- [W3C: Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html): explains pointer alternatives and their distinction from keyboard operation.
- [W3C APG: Modal Dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/): semantic and focus pattern.
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion): browser preference semantics and examples.
- [React Native AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo): query and change-event documentation; select the project's matching version.
- [Reanimated useReducedMotion](https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion/): documents startup capture and lack of rerender on setting changes.
- [Android Compose animation guide](https://developer.android.com/develop/ui/compose/animation/quick-guide): distinguishes visual alpha from removal.

The reference's engineering procedures are original plugin guidance informed by these sources and the preserved baseline skill; no source implementation is bundled here.
