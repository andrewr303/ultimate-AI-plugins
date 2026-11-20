---
name: motion-native
description: "Design, implement, or review native app motion in SwiftUI/UIKit, React Native, Jetpack Compose, Flutter, or WinUI while preserving platform navigation, interruption, accessibility preferences, and lifecycle behavior. Use for native app polish; use web-specific skills for DOM interfaces."
---

# Native platform motion

Improve responsiveness and continuity using the platform's own controls and navigation first. Apple-like means clear feedback, spatial logic, restrained movement, and user control; it does not mean transplanting iOS behavior into every platform.

Read [native adapters and evidence](../../references/native-platforms.md). Pair with [motion-accessibility](../motion-accessibility/SKILL.md) for reduced motion and assistive interaction. The original [polish-platform-motion](../polish-platform-motion/SKILL.md) supplies the shared design baseline.

## Inspect before choosing APIs

Record the framework and installed release, language, minimum deployment target, supported devices, navigation owner, existing animation system, and platform accessibility adapter. Read project instructions and lockfiles. Check SDK symbols locally or in matching-version primary documentation before writing framework code.

Locate the actual friction: deferred press feedback, an interrupted sheet snapping, an entrance replaying after scrolling, duplicated back navigation, inaccessible disappearance, keyboard-induced jumps, or expensive layout work.

Choose one real flow and its shared components. Preserve brand, native controls, system scrolling, safe areas, focus behavior, and the platform's back affordance. Do not install a new animation engine just to tune a basic state transition.

## Specify a platform-aware interaction

For each interaction, define trigger, immediate semantic update, visual origin and endpoint, interruption/cancel policy, reduced path, focus or accessibility destination, and resource lifetime.

Use native duration or spring configuration only after checking the installed API's units. Do not copy web cubic-bezier values into a physical spring or reuse stiffness values across engines. Tune movement in context with restrained overshoot.

- Press feedback acknowledges input immediately; network work begins independently.
- Direct manipulation tracks the finger; settling begins after release. Use bounds, cancellation, and a non-gesture control.
- Navigation follows the real hierarchy and reading direction. Preserve interactive back and platform predictive-back behavior where supported.
- Shared elements require stable identity and a true relationship. An ordinary transition is a valid fallback when measurement or lifecycle ownership is uncertain.
- Separate the logical endpoint from animator completion. Cancellation, navigation, backgrounding, and zero-duration modes must release resources safely.

## Select the matching adapter

### SwiftUI and UIKit

Prefer standard buttons, sheets, navigation containers, and transitions. Scope custom animation to the intended state change; inspect implicit animation propagation so an unrelated layout update does not animate.

In SwiftUI, inspect the accessibility Reduce Motion environment value and choose a reduced presentation. In UIKit, inspect `UIAccessibility.isReduceMotionEnabled` and the corresponding status-change notification. Verify availability and observer ownership in the project's SDK.

Keep navigation, presentation, and dismissal under one owner. If using an interruptible UIKit animator, distinguish completion from cancellation and settle from the current presentation. Do not infer dismissal from a visual alpha alone.

Test dynamic type, safe-area changes, device rotation, keyboard appearance, VoiceOver, and interruption by system navigation. Haptics and sound remain outside scope unless separately requested.

### React Native and Reanimated

Reuse the installed navigation and gesture stack. Confirm compatibility among React Native, Reanimated, gesture handling, and any architecture-specific setup before choosing APIs.

Use the platform accessibility query plus live change event where the product must react within the current session. In inspected Reanimated source, `useReducedMotion` is a startup snapshot; do not use it as proof that preference changes rerender the UI. Check the installed version and explicitly bridge live changes when needed.

Retain system-respecting reduced-motion configuration on animations, including delayed, repeated, layout, and gesture-settling paths. Do not force an “always animate” option to retain a visual flourish.

Keep per-frame movement in the animation/gesture runtime the project already uses; avoid unnecessary React state updates per frame. Treat crossings into application state as semantic events. Verify cancellation before running a completion callback that commits state.

Test touch cancellation, keyboard avoidance, hardware back, app background/foreground, and VoiceOver/TalkBack on supported devices. A JavaScript unit test alone does not validate native thread or gesture behavior.

### Jetpack Compose

Prefer Material and navigation primitives already in use. Choose appearance, content, size, or value animation APIs by the state being represented. Check installed Compose/navigation versions before using shared transitions or newer back APIs.

Respect system duration scale through supported framework behavior and verify a zero-animation path. Do not substitute developer animation scale for a complete accessibility review.

Opacity alone leaves a composable's existence and semantics unchanged. Coordinate interactive removal with the semantic tree and focus, including during an exit. Keep lazy-list item identity stable and hoist state that should survive recycling.

Profile recomposition, layout, and draw separately when motion stutters. Preserve nested scroll, IME insets, gesture navigation, and TalkBack behavior.

### Flutter

Use the existing route, implicit animation, or controller system. Check the installed SDK's preference model: current inspected source distinguishes `disableAnimations` from `reduceMotion`. Do not assume one flag covers both iOS and Android in every release.

Check how framework controllers consume preferences separately from custom widget policy. A test-only `MediaQuery` override may not change framework animation behavior in the inspected current implementation; verify the installed release and test the real system preference too.

Cancel and dispose controllers, listeners, and tickers. Invisible widget content may remain interactive or semantic; explicitly coordinate exclusion, focus, and state preservation. Test route pop, gesture interruption, text scaling, keyboard insets, and screen-reader navigation.

### WinUI and other native stacks

Reuse existing platform transitions and controls. Verify the installed Windows App SDK / framework APIs for animation preference, change notifications, dispatching, and cancellation. `UISettings.AnimationsEnabled` is a source to investigate for the supported Windows target, not a universal cross-framework subscription API.

Keep keyboard focus, Narrator semantics, window resizing, DPI changes, and system navigation coherent. For an unfamiliar stack, produce the platform contract and inspect matching documentation before inventing adapter code.

## Verify and deliver

Run the project's relevant compile/build checks and concrete state-risk tests. Exercise normal speed on a representative device or simulator, then repeat with reduced motion enabled before launch and changed mid-session.

Rapidly reverse presentation, navigate back while moving, background the app during settling, change text size, and test slow/failing operations. Confirm endpoint, cleanup, focus, retained input, and one committed operation.

Deliver the implementation and a concise record of framework/SDK target, chosen native owner, reduced path, tests and devices used, and any unavailable GUI or assistive-technology checks. Do not report smoothness or native behavior as tested when only source inspection or compilation ran.
