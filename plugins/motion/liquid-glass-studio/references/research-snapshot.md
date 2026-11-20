# Research snapshot: platform facts

Primary-source facts about Apple's Liquid Glass material, the web platform features that liquid glass style UIs depend on, Android and Flutter primitives, accessibility criteria and published critique. Other references cite rows here by ID (for example "row W3").

"Liquid Glass" is Apple's name for its material. This plugin is not affiliated with Apple; it describes "liquid glass style" interfaces.

## How to use this snapshot

- **Checked date.** Every row was checked on **2026-11-05** unless the row says otherwise.
- **Re-check moving facts before relying on them.** Rows marked "moving" in the Volatility column change with browser releases, OS updates, bug triage or library releases. Before you quote one to a user, put it in a recommendation, or gate code on it, open the URL and confirm it still holds. If it changed, say so and use the new fact; if you cannot reach the source, state the check date and that the fact is unconfirmed.
- **Stable rows** (spec text, API signatures already shipped, WCAG thresholds) rarely change, but still re-check when a new major OS or spec version appears.
- **Confidence.** High = primary source read on the check date. Medium = indirect primary source, or a reputable secondary source consistent with primary evidence. Low = single secondary source or inference. Items that could not be confirmed are in [Unverified](#unverified); never state them as fact.
- **Method.** Apple DocC JSON for exact signatures and HIG text; MDN browser-compat-data for browser versions; WebKit and Mozilla bug trackers for live bug status; W3C WAI Understanding documents; Android reference docs. Secondary press only where no primary source exists, and flagged.

## 1. Apple guidance

| ID | Claim | Source URL | Checked | Confidence | Volatility |
| --- | --- | --- | --- | --- | --- |
| A1 | Liquid Glass was announced June 9, 2025 and ships in iOS 26, iPadOS 26, macOS Tahoe 26, watchOS 26 and tvOS 26 | https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/ | 2026-11-05 | High | stable |
| A2 | WWDC25 sessions: 219 "Meet Liquid Glass", 356 "Get to know the new design system", 323 "Build a SwiftUI app with the new design", 284 "Build a UIKit app with the new design", 310 "Build an AppKit app with the new design" | https://developer.apple.com/videos/play/wwdc2025/219/ (and /356/, /323/, /284/, /310/) | 2026-11-05 | High | stable |
| A3 | HIG: Liquid Glass forms a functional layer for controls and navigation that floats above content; "Don't use Liquid Glass in the content layer" (transient controls such as sliders and toggles may take the look while active) | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving (HIG updates) |
| A4 | HIG: "Use Liquid Glass effects sparingly"; limit custom glass to the most important functional elements | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving |
| A5 | HIG: regular variant blurs and adjusts luminosity for legibility (text-heavy UI such as alerts, sidebars, popovers); clear variant is highly translucent and only for components over visually rich backgrounds such as media | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving |
| A6 | HIG: under clear glass over bright content, "consider adding a dark dimming layer of 35% opacity" | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving |
| A7 | HIG Materials change log: added 2025-06-09, updated 2025-09-09 | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving |
| A8 | HIG: variant appearance can change with the user's preferred Liquid Glass look and with Reduce Transparency or Increase Contrast | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving |
| A9 | HIG: iOS and iPadOS standard materials are ultraThin, thin, regular, thick; avoid `quaternaryLabel` on thin and ultraThin | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | stable |
| A10 | Adopting guide: standard components adopt the look with the latest SDKs; reduce custom backgrounds in bars; test with accessibility settings; avoid layering glass on glass; give custom colors light, dark and increased-contrast variants; combine custom effects in `GlassEffectContainer` for performance | https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass | 2026-11-05 | High | moving |
| A11 | tvOS: Liquid Glass effects need Apple TV 4K (2nd generation) or newer; older devices keep the previous look | https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass | 2026-11-05 | High | stable |
| A12 | visionOS windows use an unmodifiable system glass; SwiftUI `glassEffect`, `Glass` and `GlassEffectContainer` do not list visionOS availability | https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:) | 2026-11-05 | High | moving |
| A13 | `UIDesignRequiresCompatibility` is ignored when an app links against the iOS 27 SDK; apps linked with the iOS 26 SDK keep the opt-out on iOS 27 devices (Apple DTS forum answer) | https://developer.apple.com/forums/thread/832543 | 2026-11-05 | High | moving |
| A14 | iOS, iPadOS and macOS 26.1 add a Liquid Glass setting with Clear (default) or Tinted: Settings > Display & Brightness on iOS and iPadOS, System Settings > Appearance on the Mac | https://www.macrumors.com/2025/10/20/ios-26-1-liquid-glass-toggle/ | 2026-11-05 | Medium (secondary) | stable |
| A15 | iOS 26.1 released November 3, 2025 | https://9to5mac.com/2025/11/03/apple-releases-ios-26-1-for-iphone-with-these-changes/ | 2026-11-05 | Medium (secondary) | stable |
| A16 | iOS 26.2 adds a transparency slider for the Lock Screen clock glass style only | https://techcrunch.com/2025/12/12/with-ios-26-2-apple-lets-you-roll-back-liquid-glass-again-this-time-on-the-lock-screen/ | 2026-11-05 | Medium (secondary) | stable |
| A17 | iOS 27 (WWDC26): reported transparency slider from "ultra clear" to "fully tinted", darker edges, brighter specular highlights, better diffusion, uniform top toolbar; existing apps get changes without recompiling | https://macrumors.com/2026/06/10/how-liquid-glass-is-changing-in-ios-27 | 2026-11-05 | Medium (secondary only) | moving |
| A18 | Apple's public `Glass` docs still list only `regular`, `clear`, `identity`, `tint(_:)`, `interactive(_:)` | https://developer.apple.com/documentation/swiftui/glass | 2026-11-05 | High | moving |

## 2. Apple API list (exact signatures from DocC, checked 2026-11-05)

Availability: SwiftUI glass APIs list iOS, iPadOS, Mac Catalyst, macOS, tvOS and watchOS 26.0 (not visionOS), except where a line below notes a later version. UIKit `UIGlassEffect` and `UIGlassContainerEffect` list iOS, iPadOS, Mac Catalyst and tvOS 26.0. AppKit `NSGlassEffectView` lists macOS 26.0; its `effectIsInteractive` property lists macOS 27.0. On visionOS, custom glass uses `glassBackgroundEffect(displayMode:)` (visionOS 1.0) instead.

### SwiftUI

```swift
func glassEffect(_ glass: Glass = .regular,
                 in shape: some Shape = DefaultGlassEffectShape()) -> some View   // default shape: Capsule
struct Glass {
  static var regular: Glass
  static var clear: Glass
  static var identity: Glass
  func tint(_ color: Color?) -> Glass
  func interactive(_ isEnabled: Bool = true) -> Glass
}
struct GlassEffectContainer<Content: View> { init(spacing: CGFloat? = nil, content: () -> Content) }
func glassEffectID(_ id: (some Hashable & Sendable)?, in namespace: Namespace.ID) -> some View
func glassEffectUnion(id: (some Hashable & Sendable)?, namespace: Namespace.ID) -> some View
func glassEffectTransition(_ transition: GlassEffectTransition) -> some View   // .identity, .matchedGeometry, .materialize
static var glass: GlassButtonStyle
static func glass(_ glass: Glass) -> Self     // 26.0, for example .glass(.clear)
// GlassButtonStyle: init() is 26.0; init(_ glass: Glass) is 26.1
static var glassProminent: GlassProminentButtonStyle
func backgroundExtensionEffect() -> some View
struct ToolbarSpacer { init(_ sizing: SpacerSizing = .flexible, placement: ToolbarItemPlacement = .automatic) }
func tabBarMinimizeBehavior(_ behavior: TabBarMinimizeBehavior) -> some View   // .automatic, .never, .onScrollDown, .onScrollUp
func tabViewBottomAccessory<Content>(content: () -> Content) -> some View
func scrollEdgeEffectStyle(_ style: ScrollEdgeEffectStyle?, for edges: Edge.Set) -> some View   // .automatic, .hard, .soft
func scrollEdgeEffectHidden(_ hidden: Bool = true, for edges: Edge.Set = .all) -> some View
func safeAreaBar(edge: VerticalEdge, alignment: HorizontalAlignment = .center,
                 spacing: CGFloat? = nil, content: () -> some View) -> some View   // .top, .bottom
func safeAreaBar(edge: HorizontalEdge, alignment: VerticalAlignment = .center,
                 spacing: CGFloat? = nil, content: () -> some View) -> some View   // .leading, .trailing
func glassBackgroundEffect(displayMode: GlassBackgroundDisplayMode = .always) -> some View   // visionOS 1.0 only
```

Attributes such as `nonisolated`, `@MainActor` and `@ContentBuilder` are omitted for brevity; read the DocC page for the full declaration.

### UIKit

```swift
class UIGlassEffect            // init(style: UIGlassEffect.Style), .regular / .clear; isInteractive; tintColor
class UIGlassContainerEffect   // spacing: CGFloat (distance at which elements begin to merge)
UIButton.Configuration.glass(), .prominentGlass(), .clearGlass(), .prominentClearGlass()
class UIScrollEdgeEffect       // isHidden, style
class UIScrollEdgeElementContainerInteraction
class UIBackgroundExtensionView
```

Host `UIGlassEffect` in `UIVisualEffectView(effect:)`; for groups, nest glass effect views inside the `contentView` of a view using `UIGlassContainerEffect`. Existing `UIVisualEffectView` rules apply: add subviews to `contentView`, avoid alpha below 1 on the effect view or its superviews, and snapshot the window rather than the effect view.

### AppKit

```swift
class NSGlassEffectView            // contentView, cornerRadius, style (.regular / .clear), tintColor
                                   // var effectIsInteractive: Bool { get set }  (macOS 27.0, needs the macOS 27 SDK)
class NSGlassEffectContainerView   // contentView, spacing
NSButton.BezelStyle.glass
```

### API claims

| ID | Claim | Source URL | Checked | Confidence | Volatility |
| --- | --- | --- | --- | --- | --- |
| S1 | `glassEffect(_:in:)` signature and Capsule default; apply it after other appearance modifiers | https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:) | 2026-11-05 | High | stable |
| S2 | `Glass` members as listed | https://developer.apple.com/documentation/swiftui/glass | 2026-11-05 | High | moving (new members possible) |
| S3 | `GlassEffectContainer(spacing:content:)` renders contained effects together for performance and morphing; container spacing larger than stack spacing blends shapes at rest | https://developer.apple.com/documentation/swiftui/glasseffectcontainer ; https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views | 2026-11-05 | High | stable |
| S4 | `glassEffectID`, `glassEffectUnion`, `glassEffectTransition` signatures; transitions `.identity`, `.matchedGeometry`, `.materialize` | https://developer.apple.com/documentation/swiftui/view/glasseffectid(_:in:) ; https://developer.apple.com/documentation/swiftui/glasseffecttransition | 2026-11-05 | High | stable |
| S5 | `.glass` and `.glassProminent` button styles and `.glass(_ glass: Glass)` are 26.0; `GlassButtonStyle(_ glass: Glass)` is 26.1 | https://developer.apple.com/documentation/swiftui/primitivebuttonstyle/glass ; https://developer.apple.com/documentation/swiftui/primitivebuttonstyle/glass(_:) ; https://developer.apple.com/documentation/swiftui/glassbuttonstyle/init(_:) | 2026-11-05 | High | stable |
| S6 | `backgroundExtensionEffect()` mirrors and blurs the view into safe areas; use with discretion | https://developer.apple.com/documentation/swiftui/view/backgroundextensioneffect() | 2026-11-05 | High | stable |
| S7 | `ToolbarSpacer` initializer as listed | https://developer.apple.com/documentation/swiftui/toolbarspacer | 2026-11-05 | High | stable |
| S8 | `tabBarMinimizeBehavior` values; minimizing is iPhone only | https://developer.apple.com/documentation/swiftui/tabbarminimizebehavior | 2026-11-05 | High | stable |
| S9 | `scrollEdgeEffectStyle` with `.automatic`, `.hard`, `.soft` (the modifier does not list visionOS); `safeAreaBar` has a `VerticalEdge` and a `HorizontalEdge` overload and extends scroll edge effects to custom bars | https://developer.apple.com/documentation/swiftui/scrolledgeeffectstyle ; https://developer.apple.com/documentation/swiftui/view/safeareabar(edge:alignment:spacing:content:) | 2026-11-05 | High | stable |
| S10 | `glassBackgroundEffect(displayMode:)` is the visionOS API for custom glass panels and ornaments; visionOS 1.0 only | https://developer.apple.com/documentation/swiftui/view/glassbackgroundeffect(displaymode:) | 2026-11-05 | High | stable |
| U1 | `UIGlassEffect(style:)` with `.regular` and `.clear`, `isInteractive`, `tintColor` | https://developer.apple.com/documentation/uikit/uiglasseffect | 2026-11-05 | High | stable |
| U2 | `UIGlassContainerEffect.spacing`; nest glass effect views in its `contentView` | https://developer.apple.com/documentation/uikit/uiglasscontainereffect | 2026-11-05 | High | stable |
| U3 | `UIButton.Configuration` glass factories as listed | https://developer.apple.com/documentation/uikit/uibutton/configuration-swift.struct/glass() | 2026-11-05 | High | stable |
| U4 | `UIVisualEffectView` rules: no alpha below 1, subviews in `contentView`, snapshot the window | https://developer.apple.com/documentation/uikit/uivisualeffectview | 2026-11-05 | High | stable |
| K1 | `NSGlassEffectView`, `NSGlassEffectContainerView.spacing`, `NSButton.BezelStyle.glass` | https://developer.apple.com/documentation/appkit/nsglasseffectview | 2026-11-05 | High | stable |
| K2 | Accessibility hooks: SwiftUI `accessibilityReduceTransparency`, `colorSchemeContrast`, `accessibilityReduceMotion`; UIKit `UIAccessibility.isReduceTransparencyEnabled` | https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency | 2026-11-05 | High | stable |
| K3 | `NSGlassEffectView.effectIsInteractive` lists macOS 27.0 only; gate it with `if #available(macOS 27.0, *)` and build with the macOS 27 SDK | https://developer.apple.com/documentation/appkit/nsglasseffectview/effectisinteractive | 2026-11-05 | High | stable |

## 3. Web platform

| ID | Claim | Source URL | Checked | Confidence | Volatility |
| --- | --- | --- | --- | --- | --- |
| W1 | `backdrop-filter`: Chrome 76, Edge 79, Firefox 103, Safari 18 unprefixed (Safari 9 to 17 need `-webkit-backdrop-filter`) | https://github.com/mdn/browser-compat-data/blob/main/css/properties/backdrop-filter.json | 2026-11-05 | High | stable |
| W2 | Firefox before 123 did not support `backdrop-filter` on systems with an unknown GPU vendor | https://bugzil.la/1868737 (via MDN BCD note) | 2026-11-05 | High | stable |
| W3 | Safari has not shipped `backdrop-filter: url(#svg)` with filters such as `feDisplacementMap`: WebKit bug 245510 is NEW, last change 2026-09-06, community patches pending | https://bugs.webkit.org/show_bug.cgi?id=245510 | 2026-11-05 | High | **moving** |
| W4 | Firefox ignores some url() backdrop filters when they would fall back to a blob image: bug 1961378 is NEW | https://bugzilla.mozilla.org/show_bug.cgi?id=1961378 | 2026-11-05 | High (status) / Medium (practical impact) | **moving** |
| W5 | Firefox regression of backdrop SVG filters in 120 was fixed (bug 1868479) | https://bugzilla.mozilla.org/show_bug.cgi?id=1868479 | 2026-11-05 | High | stable |
| W6 | Chromium renders `backdrop-filter: url(#svg)` including `feDisplacementMap` | https://bugs.webkit.org/show_bug.cgi?id=245510 ; https://kube.io/blog/liquid-glass-css-svg/ | 2026-11-05 | Medium | moving |
| W7 | WebKit bug 297770 "filter: url() ignored when backdrop-filter applied" is REOPENED | https://bugs.webkit.org/show_bug.cgi?id=297770 | 2026-11-05 | High | **moving** |
| W8 | `@supports` cannot tell whether a url() backdrop filter actually renders; engine gating or a frosted baseline is required | https://kube.io/blog/liquid-glass-css-svg/ | 2026-11-05 | Medium | moving |
| W9 | `feDisplacementMap` as a normal SVG filter is supported everywhere (Chrome 5, Firefox 3, Safari 6, Edge 12) | https://github.com/mdn/browser-compat-data/blob/main/svg/elements/feDisplacementMap.json | 2026-11-05 | High | stable |
| W10 | Filter Effects Level 2 Editor's Draft (2 Oct 2026) defines a Backdrop Root formed by `filter`, `opacity` below 1, mask, clip-path, `backdrop-filter`, `mix-blend-mode` or a matching `will-change`; the draft lacks Working Group consensus | https://drafts.csswg.org/filter-effects-2/ | 2026-11-05 | High (spec text) | **moving** |
| W11 | `prefers-reduced-transparency`: Chrome 118 (BCD) or 119 (web-features); Firefox 113 behind a pref; not in Safari | https://web-platform-dx.github.io/web-features-explorer/features/prefers-reduced-transparency | 2026-11-05 | High (support) / Medium (exact Chrome version) | **moving** |
| W12 | Firefox enable bug 1822176 NEW (last change 2026-06-12); WebKit bug 175497 NEW (last change 2026-07-01, privacy concerns cited) | https://bugzilla.mozilla.org/show_bug.cgi?id=1822176 ; https://bugs.webkit.org/show_bug.cgi?id=175497 | 2026-11-05 | High | **moving** |
| W13 | `prefers-reduced-motion`: Chrome 74, Firefox 63, Safari 10.1 | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json | 2026-11-05 | High | stable |
| W14 | `prefers-contrast`: Chrome 96, Firefox 101, Safari 14.1 | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json | 2026-11-05 | High | stable |
| W15 | `forced-colors`: Chrome 89, Firefox 89, Safari 16 (always `none` on Apple platforms) | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json | 2026-11-05 | High | stable |
| W16 | `color-mix()`: Chrome 111, Firefox 113, Safari 16.2 | https://github.com/mdn/browser-compat-data/blob/main/css/types/color.json | 2026-11-05 | High | stable |
| W17 | `@property`: Chrome 85, Firefox 128, Safari 16.4 | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/property.json | 2026-11-05 | High | stable |
| W18 | `anchor-name`: Chrome 125, Firefox 147, Safari 26 | https://github.com/mdn/browser-compat-data/blob/main/css/properties/anchor-name.json | 2026-11-05 | High | stable |
| W19 | html2canvas 1.4.1 (published 2022-01-22) does not support box-shadow, filter, mix-blend-mode and several other features; images must be same origin | https://html2canvas.hertzen.com/features ; https://html2canvas.hertzen.com/documentation | 2026-11-05 | High | moving (releases) |
| W20 | html-to-image 1.11.13 (2025-02-14) renders through SVG `foreignObject`; tainted canvases fail; large DOMs hit data-URI limits; WebKit can draw a large embedded image blank on first rasterization | https://github.com/bubkoo/html-to-image | 2026-11-05 | High | moving (releases) |
| W21 | modern-screenshot 4.7.0 (2026-04-16) is a foreignObject-based alternative (version only) | npm registry entry for `modern-screenshot` (exact URL not recorded at check time) | 2026-11-05 | Medium | moving |
| W22 | Cross-origin iframe content cannot be read by any DOM serialization approach (same-origin policy) | (general web security rule) | 2026-11-05 | Medium | stable |
| W23 | Uploading a cross-origin image without CORS approval to a WebGL texture is blocked or taints the canvas | (long-standing HTML and WebGL rule; MDN page not re-fetched) | 2026-11-05 | Medium | stable |
| W24 | HTML-in-Canvas (`drawElementImage`) is a Chrome origin trial, 148 extended to 154; Chrome 155 renames `layoutsubtree` to `content="drawable"` | https://groups.google.com/a/chromium.org/g/blink-dev/c/BpWbzJ9P22s ; https://developer.chrome.com/blog/html-in-canvas-ot-changes | 2026-11-05 | Medium | **moving** |

Engine versions for WebGL, WebGPU, CSS `filter` and `-moz-element()` are tabulated in [browser-support.md](browser-support.md).

## 4. Android and Flutter

| ID | Claim | Source URL | Checked | Confidence | Volatility |
| --- | --- | --- | --- | --- | --- |
| D1 | `RenderEffect` (blur, chain, color filter, shader, blend, offset) is API 31; `createRuntimeShaderEffect` is API 33 | https://developer.android.com/reference/android/graphics/RenderEffect | 2026-11-05 | High | stable |
| D2 | `RuntimeShader` (AGSL) is API 33; `setInputColorFilter` and `setInputXfermode` API 36; `setWorkingColorSpace` API 37; AGSL outputs premultiplied alpha | https://developer.android.com/reference/android/graphics/RuntimeShader | 2026-11-05 | High | stable |
| D3 | Compose `Modifier.blur` works only on Android 12 and later (ignored before) and blurs the composable's own content, not what is behind it | https://developer.android.com/develop/ui/compose/graphics/images/customize | 2026-11-05 | High | stable |
| D4 | Android 12 window blurs (`setBackgroundBlurRadius`, `FLAG_BLUR_BEHIND`); the system may disable blurs at runtime; check `isCrossWindowBlurEnabled` and listen for changes | https://source.android.com/docs/core/display/window-blurs | 2026-11-05 | High | stable |
| D5 | No official Material 3 or Compose glass or refraction component found; press reports Material 3 Expressive system UI uses blur and a user toggle to disable blur is coming | https://www.androidauthority.com/android-getting-option-disable-background-blur-3590124 | 2026-11-05 | Medium-Low | **moving** |
| D6 | Haze (Compose Multiplatform backdrop blur): Android API 23+, scrim fallback at API 30 and below, full features at API 33+ | https://chrisbanes.github.io/haze/latest/blur/platforms/ | 2026-11-05 | High | moving |
| D7 | Haze 1.7.2 stable (2026-02-10); 2.0.0 alphas add an experimental `haze-liquidglass` module | https://chrisbanes.github.io/haze/latest/changelog/ | 2026-11-05 | Medium | **moving** |
| D8 | Kyant0 "Backdrop" (`io.github.kyant0:backdrop`) is a Compose Multiplatform liquid glass library without high-level components | https://github.com/Kyant0/AndroidLiquidGlass | 2026-11-05 | High (README) | moving |
| D9 | Flutter `liquid_glass_renderer` requires Impeller; no Web, Windows or Linux; 1.0.0-dev needs Flutter 3.47 and Flutter GPU (preview) with a `FakeGlass` fallback | https://pub.dev/documentation/liquid_glass_renderer/latest/ | 2026-11-05 | Medium | **moving** |
| D10 | Flutter core `BackdropFilter` with `ImageFilter.blur` gives frosted glass | (well established; not re-fetched) | 2026-11-05 | Medium | stable |

## 5. Accessibility

| ID | Claim | Source URL | Checked | Confidence | Volatility |
| --- | --- | --- | --- | --- | --- |
| X1 | WCAG 1.4.3 Contrast (Minimum), AA: 4.5:1 normal text, 3:1 large text (18pt, or 14pt bold); ratios are not rounded; failure F83 covers background images without enough contrast | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 2026-11-05 | High | stable |
| X2 | WCAG 1.4.11 Non-text Contrast, AA: 3:1 for visuals that identify components and states; gradient guidance differs between central color and least-contrasting area | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | 2026-11-05 | High | stable |
| X3 | WCAG 2.2 adds 2.4.11 Focus Not Obscured (Minimum), AA, relevant to floating glass bars over scrolling content | https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html | 2026-11-05 | High (existence; page not re-fetched) | stable |
| X4 | Apple system glass adapts to Reduce Transparency and Increase Contrast automatically; custom glass must be tested under them | https://developer.apple.com/design/human-interface-guidelines/materials | 2026-11-05 | High | moving |
| X5 | Safari cannot detect Reduce Transparency from CSS (see W11), so web glass needs an in-app "solid surfaces" option and should treat `prefers-contrast: more` and `forced-colors: active` as "go solid" | derived from W11, W14, W15 | 2026-11-05 | Low (inference) | moving |
| X6 | Contrast method for glass: composite the glass over the worst-case backdrop (brightest for dark text, darkest for light text, busiest region) and require the WCAG ratio at that minimum. This is an engineering inference from X1 and X2, not a W3C rule | derived from X1, X2 | 2026-11-05 | Low (inference) | stable |

## 6. Published critique

| ID | Claim | Source URL | Checked | Confidence | Volatility |
| --- | --- | --- | --- | --- | --- |
| N1 | Nielsen Norman Group, Raluca Budiu, "Liquid Glass Is Cracked, and Usability Suffers in iOS 26" (Oct 10, 2025): text-to-background contrast "is often too low"; overlapping text; floating controls blend into content; context-dependent controls are "harder to learn and less predictable"; "Motion for motion's sake is not usability" | https://www.nngroup.com/articles/liquid-glass/ | 2026-11-05 | High | stable |
| N2 | Apple's later user controls (26.1 Tinted option, 26.2 clock slider, reported iOS 27 slider) are consistent with legibility being a recognized problem. Interpretation, not an Apple statement | derived from A14, A16, A17 | 2026-11-05 | Low (inference) | moving |

## Unverified

Do not state these as fact. Re-check, or say they are unconfirmed.

| Item | Status | Where it came from |
| --- | --- | --- |
| iOS 27 Liquid Glass control lives at Settings > Appearance > Liquid Glass | UNVERIFIED; single secondary source (technobezz) | 2026-11-05 search |
| iOS 26.4 changed Liquid Glass or "Reduce Bright Effects" behavior | UNVERIFIED; forum claim only | https://discussions.apple.com/docs/DOC-250010041 |
| WWDC25 State of the Union said the compatibility opt-out is intended to be removed in the next major release | UNVERIFIED wording; quoted by a forum poster, transcript not re-read | developer forum thread linked in A13 |
| html2canvas renders `backdrop-filter` | Not listed as supported or unsupported; treat as unsupported (Low, inference) | https://html2canvas.hertzen.com/features |
| Video frame capture behavior in html2canvas and html-to-image | UNVERIFIED | none found |
| Licenses of Haze and Kyant0 Backdrop | UNVERIFIED this session (GitHub API blocked); Haze believed Apache-2.0 from prior knowledge | D6, D8 |
| Kyant0 Backdrop lens refraction requires API 33+ | Low; from a port's compatibility table | D8 |
| Material 3 Expressive blur toggle timing | Medium-Low; press only | D5 |

## Re-check checklist for moving facts

1. Safari url() backdrop filters: open WebKit bug 245510 and 297770 (W3, W7). If either is RESOLVED FIXED, find the Safari release that ships it and update [browser-support.md](browser-support.md) and the tier logic.
2. Firefox url() backdrop filters: open bug 1961378 (W4).
3. `prefers-reduced-transparency`: check web-features and bugs 1822176 and 175497 (W11, W12).
4. Backdrop Root: check the Filter Effects Level 2 draft status (W10).
5. Apple: re-read the HIG Materials change log (A7) and the `Glass` DocC page (A18); check whether iOS 27 changes (A17) now have an Apple primary source.
6. `UIDesignRequiresCompatibility`: check Apple's upcoming-requirements page (https://developer.apple.com/news/upcoming-requirements/) for the iOS 27 SDK deadline (A13).
7. HTML-in-Canvas origin trial status (W24).
8. Library versions: Haze, Kyant0 Backdrop, `liquid_glass_renderer`, html-to-image, and the five web libraries in [library-matrix.md](library-matrix.md).
