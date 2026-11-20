# Native platform adapters

Check the installed SDK, deployment targets, and matching primary documentation before writing adapter code. Web durations, spring stiffness, damping, friction, mass, and gesture velocity do not share one interchangeable unit system. Preserve platform navigation and gesture conventions.

## Adapter decision record

Record: platform and release → system motion preference → live update mechanism → animation owner → cancel/settle behavior → focus and semantics owner → runtime checks performed.

| Stack | Inspect | Common implementation risk | Acceptance exercise |
| --- | --- | --- | --- |
| SwiftUI | Reduce Motion environment, scoped animation, navigation/presentation ownership | An inherited animation affects unrelated state or a new API exceeds deployment target | Change motion setting, reverse presentation, test VoiceOver and dynamic type |
| UIKit | Accessibility motion query and notification, installed animator lifecycle | Cancellation calls a completion that assumes dismissal | Interrupt animator, reopen surface, verify latest state and focus |
| React Native | AccessibilityInfo query/events, navigation and gesture integration | Startup preference snapshot mistaken for live subscription | Toggle setting during settling, background app, test hardware back |
| Reanimated | Installed major/version, reduced-motion config, UI/application state boundary | Delayed or nested animation overrides the system preference | Check layout, repeating, delay, and gesture paths separately |
| Compose | Installed animation/navigation APIs, system motion scale, semantics | Alpha zero remains in composition; lazy item effects replay | Recycle list rows, disable animation, test TalkBack and back |
| Flutter | Installed SDK's disableAnimations and reduceMotion behavior, controllers | One platform flag or a test MediaQuery override is assumed universal | Test real iOS and Android preferences and controller cleanup |
| WinUI | Windows target, supported UISettings APIs, dispatcher and notification ownership | A UWP property is treated as a complete WinUI lifecycle implementation | Toggle system animation, resize, inspect Narrator and keyboard |

## Important inspected details

These are version-specific source observations, not blanket promises about all releases:

- Reanimated's [pinned useReducedMotion implementation](https://github.com/software-mansion/react-native-reanimated/blob/8381986bc254a0652543dac545cc08e37d90a6e6/packages/react-native-reanimated/src/hook/useReducedMotion.ts) captures the system value outside the hook. Its [official documentation](https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion/) describes a startup value rather than reactive updates. For live UI policy, inspect `AccessibilityInfo.reduceMotionChanged` in the project's React Native release and remove the listener at teardown.
- Flutter's [pinned media_query.dart](https://github.com/flutter/flutter/blob/7e5619891ad4ad6e66a65a414e20ebdbd8c46cea/packages/flutter/lib/src/widgets/media_query.dart#L667) distinguishes Android-oriented `disableAnimations` from iOS-oriented `reduceMotion`. The [disableAnimations API page](https://api.flutter.dev/flutter/widgets/MediaQueryData/disableAnimations.html) also distinguishes framework consumption from custom widget overrides. Check the project's installed SDK before choosing flags or writing tests.
- Compose's [official animation guide](https://developer.android.com/develop/ui/compose/animation/quick-guide) warns that alpha-only disappearance leaves a composable present. Coordinate semantics and removal explicitly; do not infer operability from pixels.

## Primary documentation entrypoints

- [SwiftUI accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [UIKit isReduceMotionEnabled](https://developer.apple.com/documentation/uikit/uiaccessibility/isreducemotionenabled)
- [UIKit reduceMotionStatusDidChangeNotification](https://developer.apple.com/documentation/uikit/uiaccessibility/reducemotionstatusdidchangenotification)
- [Apple Human Interface Guidelines: Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [React Native AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo)
- [Reanimated accessibility configuration](https://docs.swmansion.com/react-native-reanimated/docs/guides/accessibility/)
- [Compose MotionDurationScale](https://developer.android.com/reference/kotlin/androidx/compose/ui/MotionDurationScale)
- [Flutter MediaQueryData.disableAnimations](https://api.flutter.dev/flutter/widgets/MediaQueryData/disableAnimations.html)
- [Windows UISettings.AnimationsEnabled](https://learn.microsoft.com/en-us/uwp/api/windows.ui.viewmanagement.uisettings.animationsenabled)

Documentation was inspected where readable on 2026-10-21. Apple documentation pages required JavaScript in the retrieval tool; search-index extracts confirmed the named entrypoints, but full SDK availability and implementation behavior remain checks for the target project. The Compose API page exceeded retrieval size; its exact API contract was not fully reviewed. These limitations do not establish a runtime failure or prevent using the qualified adapter workflow.

Use native controls first. Add shared-element or custom interactive motion only when the task benefits and lifecycle ownership is clear. Keep sound and haptics outside scope unless separately requested. Do not claim any native device, screen reader, performance profile, or SDK build was exercised by this package's source research.
