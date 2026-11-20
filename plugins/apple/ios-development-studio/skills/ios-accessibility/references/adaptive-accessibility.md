# Text, contrast, motion and direction

## Dynamic Type and content expansion

Use semantic text styles or a custom typography system that scales through supported mechanisms. Inspect fixed frames, truncation, line limits and minimum-scale shortcuts around essential content. A large-text layout can reflow horizontally arranged controls into vertical groups or use scrolling; it need not preserve every small-text coordinate.

Do not shrink important text until it fits or hide an action to preserve a screenshot. Keep primary actions reachable at the largest intended categories. A deliberately compact visualization can provide a separate readable summary. Scaled spacing and symbols should remain proportional without making the interface unnecessarily sparse.

Test long translations and large text together. English-only large text is not enough to reveal every clipping case. A format such as a currency, duration or long person's name may expand differently from a simple placeholder.

## Contrast and non-color information

Use semantic colors and tested theme variants. Semantic color selection helps adaptation but does not guarantee contrast for custom combinations, overlays or images. Check text, icons, borders, focus indicators, selected states and disabled states against their actual backgrounds.

When color communicates meaning, add text, shape, pattern, icon or another distinguishable cue. A red/green status pair should remain understandable without color discrimination. Increased-contrast settings and differentiate-without-color settings can require additional treatment in custom components.

Hit regions must be usable without requiring precision. Follow the supported platform's guidance and the project's design system, checking actual interactive frames rather than visual icon size alone. Overlapping expanded regions can make the wrong control activate; verify adjacent controls at compact widths.

## Motion and transparency

Read the user's reduced-motion preference where custom animations are introduced. Replace large spatial movement, parallax or repeated morphing with a calmer transition while retaining the information the transition communicated. Do not simply remove a necessary state change. Some subtle motion may remain appropriate; judge the effect and product need.

Avoid flashing or rapidly alternating effects. Auto-playing or continuous motion needs a way to remain comfortable and usable according to the app's supported interaction. A loading indicator should have a stable accessible description rather than repeated announcements.

Reduced transparency and contrast settings matter for custom blur/material/glass surfaces. Provide a readable solid or less translucent treatment when needed. Check the actual dynamic background; a text label readable over a blank preview can disappear over a photo. Glass adoption remains opt-in through [design guidance](../../ios-design/references/materials-and-glass.md).

## Direction and localized semantics

Use leading/trailing layout semantics for normal directional UI. Test with a genuine right-to-left locale and mixed-direction content. Keep intentionally directional content such as media timelines or literal identifiers correct rather than mirroring everything indiscriminately.

VoiceOver reading order should match the localized task hierarchy. A visually mirrored row can still announce elements in a confusing order. Dates, numbers and accessibility values need appropriate locale formatting; identifiers may follow a product-specific representation.

## Matrix and evidence

| Configuration | Primary task to verify |
| --- | --- |
| Largest supported Dynamic Type | Read full essential content and complete action |
| Narrow/short window with keyboard | Reach focused field, validation and completion |
| Light/dark plus contrast preferences | Distinguish content and interactive states |
| Differentiate without color | Interpret status/selection without hue |
| Reduced motion | Follow state changes without large unnecessary movement |
| Reduced transparency | Read controls over real content |
| Right-to-left locale | Navigate, read and activate in coherent order |

Record the actual device/runtime, setting and outcome. A source-level audit should identify risk locations and proposed checks; a screenshot can show clipping or contrast concerns but cannot prove assistive navigation works. Automated findings are evidence inputs, not certification.

## Provenance

Original guidance informed by both uploaded `SwiftUI-Agent-Skill-main.zip` variants, their accessibility/localization references; and `swiftui-design-principles-main.zip`, `SKILL.md` semantic-color and widget/layout guidance. Fixed-size style prescriptions were replaced with adaptive behavior checks. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
