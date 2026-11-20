---
name: glass-native
description: "Adopts liquid glass style material in native apps: SwiftUI, UIKit and AppKit on the 26 SDKs with availability checks and pre-26 fallbacks, GlassEffectContainer grouping, glassEffectID morphs, glass button styles, toolbar spacers, and Reduce Transparency or Increase Contrast behaviour; plus Android (RenderEffect, AGSL, Compose libraries), Flutter and React Native options with maturity labels. Use when the user says \"liquid glass in SwiftUI\", \"Apple glass\", \"glassEffect\", \"adopt iOS 26 design\", \"glass effect on Android\", \"frosted glass in Compose or Flutter\", \"refraction in React Native\", or asks why native glass looks wrong or crashes on older OS versions. Do not use for web pages or CSS (use glass-web), for choosing a web library (use glass-library-select), or for visual design decisions alone (use glass-design)."
---

# Native glass adoption

Put liquid glass style material into a native app the way each platform intends. On Apple platforms the material is a system API, so most of the work is calling it correctly, grouping it, gating it by OS version and removing custom chrome that fights it. Android, Flutter and React Native have no system material, so you assemble blur, tint and an optional refraction shader with honest fallbacks and label how mature each option is. This plugin is not affiliated with Apple; "Liquid Glass" is Apple's name for its material.

## Start here

1. **Read the project before writing code.** Record the UI frameworks in use, the minimum deployment target per platform, and the SDK the app builds with:
   - Apple: `IPHONEOS_DEPLOYMENT_TARGET` and `MACOSX_DEPLOYMENT_TARGET` in `project.pbxproj`, `platforms:` in `Package.swift`, `xcodebuild -version`, `xcrun --sdk iphoneos --show-sdk-version`. Check `Info.plist` for `UIDesignRequiresCompatibility`.
   - Android: `minSdk`, `compileSdk` and the Compose BOM in `build.gradle(.kts)`.
   - Flutter: `flutter --version`, the renderer (Impeller or Skia) per platform, and `pubspec.yaml`.
   - React Native: `react-native` and Expo SDK versions in `package.json`, plus the iOS deployment target.
2. **Find existing design tokens**: asset catalog colors, `Color` extensions, Material theme, Flutter `ThemeData`. Glass tints and the solid fallback must come from these, not new literals.
3. **List the surfaces** that would carry glass and sort them with [design-principles.md](../../references/design-principles.md#2-two-layers-controls-float-content-does-not): floating controls and navigation get glass; cards, rows and backgrounds do not.
4. **Prefer system components.** Bars, sheets, menus, toolbars and sidebars adopt the material on their own when built with the 26 SDK ([native.md](../../references/native.md#11-availability)). Remove custom bar backgrounds first, then add custom glass only to the few controls left.
5. **Check every API name** against [native.md](../../references/native.md) before using it, including its section "APIs that do not exist". Do not write an API from memory.
6. Record the plan in a copy of [glass-spec.md](../../templates/glass-spec.md) when more than two surfaces change.

## SwiftUI

**Availability.** `glassEffect`, `Glass`, `GlassEffectContainer`, `glassEffectID`, `glassEffectUnion`, `glassEffectTransition` and the `.glass` button styles are 26.0 APIs on iOS, iPadOS, Mac Catalyst, macOS, tvOS and watchOS, and not on visionOS. `ToolbarSpacer` lists iOS, iPadOS, Mac Catalyst and macOS only. Name every platform the target supports in each `#available` check, because the `*` wildcard means "the deployment target" on the platforms you leave out.

A wrapper keeps call sites clean. Its signature must not mention `Glass` or any other 26-only type unless the wrapper itself carries `@available`:

```swift
import SwiftUI

extension View {
    /// Glass on 26+, a standard material on 15 to 18. Below iOS 15, use a solid token color.
    @ViewBuilder
    func floatingSurface(cornerRadius: CGFloat) -> some View {
        let shape = RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
        if #available(iOS 26.0, macOS 26.0, *) {
            self.glassEffect(.regular, in: shape)
        } else {
            self.background(.regularMaterial, in: shape)
        }
    }
}

struct GlassGroup<Content: View>: View {
    var spacing: CGFloat
    @ViewBuilder var content: Content

    var body: some View {
        if #available(iOS 26.0, macOS 26.0, *) {
            GlassEffectContainer(spacing: spacing) { content }
        } else {
            content
        }
    }
}
```

**Order and grouping.** Apply `glassEffect` after the modifiers that set size and padding. Two or more glass views go inside one `GlassEffectContainer`; when the container spacing is larger than the stack spacing, the shapes blend while at rest. Use `glassEffectUnion(id:namespace:)` for shapes that should read as one but are not adjacent in the view tree. Recipes: [native.md](../../references/native.md#13-swiftui-recipes).

**Morphs.** Give each paired view a `glassEffectID(_:in:)` with a shared `@Namespace`, keep both inside the same container, and change state inside `withAnimation`; without an animation the change is instant. Choose `glassEffectTransition(.matchedGeometry)` for nearby shapes, `.materialize` for shapes that appear far from a partner, and `.identity` to turn the transition off. Timing and reduced motion: the `glass-motion` skill and [motion.md](../../references/motion.md#5-swiftui-glasseffectid-morphing).

**Buttons and bars.** Use `.buttonStyle(.glass)`, `.buttonStyle(.glassProminent)` or `.buttonStyle(.glass(.clear))` instead of a hand-built glass button; on older OS versions fall back to `.bordered` and `.borderedProminent`. Split a toolbar into glass groups with `ToolbarSpacer(.fixed)` or `ToolbarSpacer(.flexible)` behind the same availability check. Tint only to mark prominence. The `GlassButtonStyle(_:)` initializer (for example `GlassButtonStyle(.clear)`) is 26.1 and later, so it needs its own `26.1` availability check; see [native.md](../../references/native.md).

**Clear glass over media** needs a dimming layer under it; Apple's example uses a dark layer, and the HIG suggests 35% when the content is bright ([native.md](../../references/native.md#13-swiftui-recipes)).

## UIKit and AppKit

- UIKit: host `UIGlassEffect(style:)` in a `UIVisualEffectView`; add subviews to `contentView`, never to the effect view. Group several with a `UIVisualEffectView` whose effect is `UIGlassContainerEffect` and set its `spacing`. Buttons use `UIButton.Configuration.glass()`, `.prominentGlass()`, `.clearGlass()` or `.prominentClearGlass()`.
- Never set `alpha` below 1 on an effect view or any superview, and never mask its superview: the effect breaks or the app throws. Fade the content or animate the `effect` instead.
- AppKit: `NSGlassEffectView` with `contentView`, `style`, `cornerRadius` and `tintColor`; group with `NSGlassEffectContainerView` and its `spacing`; buttons use `bezelStyle = .glass`.
- Gate each framework with its own platforms, because `*` stands for the deployment target on every platform you leave out. UIKit: `if #available(iOS 26.0, tvOS 26.0, *)` (Mac Catalyst follows the iOS entry; drop `tvOS` if you do not ship it). AppKit: `if #available(macOS 26.0, *)`; an iOS-only check does not guard `NSGlassEffectView`, `NSGlassEffectContainerView` or `.glass` on a pre-26 macOS target. Or put `@available` with the same platforms on the type. Keep a `UIBlurEffect` or `NSVisualEffectView` path for older systems.

Code for both: [native.md](../../references/native.md#14-uikit) and [native.md](../../references/native.md#15-appkit).

## Settings that change the material

| Setting | System glass | What your code must do |
| --- | --- | --- |
| Reduce Transparency | adapts on its own | anything you draw (overlays, custom blurs, `.clear` over media) switches to opaque; read `\.accessibilityReduceTransparency` or `UIAccessibility.isReduceTransparencyEnabled` |
| Increase Contrast | adapts on its own | supply increased contrast color variants; read `\.colorSchemeContrast` |
| Reduce Motion | may remove or modify effects | gate custom springs and morphs with `\.accessibilityReduceMotion` |
| Clear or Tinted (26.1+, secondary source) | Tinted is more opaque | check custom surfaces under both |

`Glass.identity` turns glass off without changing the view tree, which keeps identity and animation stable when a setting flips. Branch only when testing shows the system adaptation is not enough ([accessibility.md](../../references/accessibility.md#10-apple-platform-settings)).

**Opt-out key.** `UIDesignRequiresCompatibility = YES` keeps the pre-26 look while building with the 26 SDK. An Apple DTS forum answer says the key is ignored once an app links against the iOS 27 SDK ([native.md](../../references/native.md#16-opting-out-uidesignrequirescompatibility)). Treat it as a short bridge and plan the adoption anyway.

## Android, Flutter and React Native

No system glass material exists on these platforms as of the 2026-11-05 snapshot. Ship the blur or scrim path first and make refraction opt-in.

| Platform | Option | Maturity label | Fallback |
| --- | --- | --- | --- |
| Android 33+ | `RenderEffect.createRuntimeShaderEffect` with an AGSL lens | platform API, stable; the lens is your code | blur at 31 to 32, scrim at 30 and below |
| Android 31+ | `RenderEffect.createBlurEffect`, window blur | platform API, stable; can be disabled at runtime, listen with `addCrossWindowBlurEnabledListener` | translucent scrim with a hairline border |
| Compose | Haze (backdrop blur, multiplatform) | stable library (1.7.2); its liquid glass module is experimental | Haze's own scrim below API 31 |
| Compose | Kyant0 AndroidLiquidGlass ("Backdrop") | young; license unverified | Haze or `RenderEffect` blur |
| Flutter | `BackdropFilter` with `ImageFilter.blur` in `ClipRRect` | framework, established | tinted container |
| Flutter | `liquid_glass_renderer` | experimental: Impeller only, no Web, Windows or Linux | `BackdropFilter` |
| React Native | blur view packages; packages that wrap `UIGlassEffect` on iOS 26 | unverified in our snapshot | your own native module or a scrim |

`RenderEffect` filters the view it is attached to, so blurring what sits behind a panel means drawing a copy of the backdrop into a layer the panel can filter. The AGSL lens sketch, library versions and sources are in [native.md](../../references/native.md#2-android).

## Rules

- System components first; custom glass only on floating controls, never on content.
- Two or more glass views always share one container (`GlassEffectContainer`, `UIGlassContainerEffect`, `NSGlassEffectContainerView`).
- Every 26-only symbol sits behind `#available` or `@available` covering every supported platform, with a fallback that still looks designed.
- Never invent API names, modifier parameters or numeric blur or refraction controls; Apple exposes none of the latter. Check [native.md](../../references/native.md) and its "APIs that do not exist" section first.
- No glass on glass: one glass layer over any point of content.
- Do not port web tuning values (`refraction: 60`, bezel widths) into native code.
- Label every non-Apple option with its maturity and keep its fallback tested.
- Content stays in normal accessible views above the effect; icon-only glass buttons get accessibility labels.

## Verify

1. Build for the newest SDK and for the lowest deployment target: `xcodebuild -scheme <Scheme> -destination 'platform=iOS Simulator,name=<device>' build`, once on a 26+ simulator and once on the oldest simulator runtime you support. A missing `#available` fails at compile time; a weak fallback only shows at run time.
2. Screenshot each surface on both runtimes with `xcrun simctl io booted screenshot <name>.png`, in light and dark.
3. Repeat with Reduce Transparency, Increase Contrast and Reduce Motion on (Simulator Settings > Accessibility, or Xcode's Environment Overrides), and with Clear and Tinted on 26.1+. Pass: text stays readable, custom overlays turn opaque, morphs become fades.
4. Measure contrast on the region behind each label, never the whole screen (a whole-screen run compares the label color with every pixel on screen):
   1. Make a debug build with the label colors set to clear, so the screenshot holds only what sits behind the text, and take the screenshot.
   2. Find the label's rectangle in screenshot pixels: its frame in window coordinates (from the view debugger, Accessibility Inspector, or a debug log of `label.convert(label.bounds, to: nil)`) times the screen scale (`UIScreen.main.scale` or `NSScreen.backingScaleFactor`, usually 2 or 3).
   3. Crop to that rectangle in a local HTML page next to the PNG, with no image tool needed: `<div id="behind-label" style="width:Wpx;height:Hpx;background:url(shot.png) -Xpx -Ypx no-repeat"></div>`, where X, Y, W and H are that rectangle in screenshot pixels.
   4. From the project directory, run `node <plugin-root>/scripts/glass_contrast.mjs --url file:///path/page.html --selector '#behind-label' --text-color '#hex' --dpr 1 --require auto`, with the real label color for `--text-color`. On the crop, `--require auto` sees the page's default font size and applies 4.5:1; use `--require 3` only for a label that is large text. `<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads).
   5. Repeat per label and per screenshot state, and record each crop rectangle in the report next to its ratio.
5. Android: run on API 33, 31 and 30 (or lower) emulators, toggle battery saver to check the blur listener, and capture `adb exec-out screencap -p > <name>.png`. Flutter and React Native: test the fallback path on every platform you ship.
6. Report what ran on which runtime and device; list paths you could not test (real device, VoiceOver, TalkBack) as not checked.

## References

- [native.md](../../references/native.md): signatures, recipes, UIKit, AppKit, Android, Flutter, React Native, "APIs that do not exist"
- [accessibility.md](../../references/accessibility.md#10-apple-platform-settings): Apple settings and custom glass
- [design-principles.md](../../references/design-principles.md): layers, stacking, tint
- [motion.md](../../references/motion.md#5-swiftui-glasseffectid-morphing): morph timing
- [performance.md](../../references/performance.md): cost of many surfaces
- [research-snapshot.md](../../references/research-snapshot.md): check dates and confidence
- [glass-spec.md](../../templates/glass-spec.md): surface inventory and acceptance checks
