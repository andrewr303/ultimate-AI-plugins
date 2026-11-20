# Native liquid glass: Apple, Android, Flutter, React Native

This reference maps liquid glass style UI onto native toolkits. On Apple platforms the material is a system API, so the job is to call it correctly and stay out of its way. On Android, Flutter and React Native there is no system material; you assemble blur, tint and (optionally) a refraction shader yourself, with honest fallbacks.

"Liquid Glass" is Apple's name for its system material. This plugin describes a "liquid glass style" and is not affiliated with Apple.

## Source keys

Platform facts cite a URL and "checked 2026-11-05" (from the platform snapshot, see [research-snapshot.md](research-snapshot.md)). Library claims cite `<library> <path>`; glasshq paths for the SwiftUI comparison app are under `apps/native-reference/`. **Inference** marks reasoning not confirmed by a primary source. **UNVERIFIED** marks a claim we could not confirm; do not repeat it as fact.

## 1. Apple platforms

### 1.1 Availability

| API family | Platforms (26.0 unless noted) | Not available | Source (checked 2026-11-05) |
| --- | --- | --- | --- |
| SwiftUI `glassEffect(_:in:)`, `Glass`, `GlassEffectContainer`, `glassEffectID`, `glassEffectUnion`, `glassEffectTransition`, `.glass`, `.glassProminent` | iOS, iPadOS, Mac Catalyst, macOS, tvOS, watchOS | visionOS | https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:) |
| SwiftUI `backgroundExtensionEffect()`, `ScrollEdgeEffectStyle` (the type), `TabBarMinimizeBehavior`, `safeAreaBar` | also list visionOS 26.0 | The `scrollEdgeEffectStyle(_:for:)` modifier does not list visionOS | https://developer.apple.com/documentation/swiftui/scrolledgeeffectstyle ; https://developer.apple.com/documentation/swiftui/view/scrolledgeeffectstyle(_:for:) |
| SwiftUI `ToolbarSpacer` | iOS, iPadOS, Mac Catalyst, macOS | | https://developer.apple.com/documentation/swiftui/toolbarspacer |
| UIKit `UIGlassEffect`, `UIGlassContainerEffect` | iOS, iPadOS, Mac Catalyst, tvOS | macOS, watchOS, visionOS | https://developer.apple.com/documentation/uikit/uiglasseffect |
| AppKit `NSGlassEffectView`, `NSGlassEffectContainerView`, `NSButton.BezelStyle.glass` | macOS (`NSGlassEffectView.effectIsInteractive` is macOS 27.0) | | https://developer.apple.com/documentation/appkit/nsglasseffectview |
| SwiftUI `GlassButtonStyle.init(_ glass: Glass)` | 26.1 on iOS, iPadOS, Mac Catalyst, macOS, tvOS, watchOS | visionOS | https://developer.apple.com/documentation/swiftui/glassbuttonstyle/init(_:) |
| SwiftUI `glassBackgroundEffect(displayMode:)` | visionOS 1.0 | other platforms | https://developer.apple.com/documentation/swiftui/view/glassbackgroundeffect(displaymode:) |

Platform notes (all from https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass, checked 2026-11-05):

- **visionOS** windows use a separate system glass that apps cannot modify (HIG Materials, https://developer.apple.com/design/human-interface-guidelines/materials, checked 2026-11-05). Do not try to reproduce the 26 material there. For a custom panel or ornament on visionOS, use `.glassBackgroundEffect()` (`nonisolated func glassBackgroundEffect(displayMode: GlassBackgroundDisplayMode = .always) -> some View`, visionOS 1.0, https://developer.apple.com/documentation/swiftui/view/glassbackgroundeffect(displaymode:), checked 2026-11-05).
- **tvOS:** Apple TV 4K (2nd generation) and newer render the effects; older devices keep the previous appearance.
- **watchOS:** changes are minimal; adopt the standard toolbar APIs and button styles.
- Standard components (bars, sheets, menus, toolbars, sidebars) adopt the material automatically when built with the 26 SDK. Most apps need less custom glass than they expect.

Gate custom glass with `if #available(iOS 26.0, macOS 26.0, *)` and keep a pre-26 path (a standard material such as `.regularMaterial`) for older OS versions you still support.

### 1.2 SwiftUI signatures

Exact declarations from Apple's DocC (checked 2026-11-05):

```swift
nonisolated func glassEffect(_ glass: Glass = .regular,
                             in shape: some Shape = DefaultGlassEffectShape()) -> some View

struct Glass {
  static var regular: Glass
  static var clear: Glass
  static var identity: Glass
  func tint(_ color: Color?) -> Glass
  func interactive(_ isEnabled: Bool = true) -> Glass
}

@MainActor @preconcurrency init(spacing: CGFloat? = nil, @ContentBuilder content: () -> Content) // GlassEffectContainer

nonisolated func glassEffectID(_ id: (some Hashable & Sendable)?, in namespace: Namespace.ID) -> some View
@MainActor @preconcurrency func glassEffectUnion(id: (some Hashable & Sendable)?, namespace: Namespace.ID) -> some View
@MainActor @preconcurrency func glassEffectTransition(_ transition: GlassEffectTransition) -> some View
// GlassEffectTransition: .identity, .matchedGeometry, .materialize

nonisolated static var glass: GlassButtonStyle { get }
nonisolated static func glass(_ glass: Glass) -> Self            // 26.0, for example .glass(.clear)
@MainActor static var glassProminent: GlassProminentButtonStyle { get }
// GlassButtonStyle: init() (26.0), init(_ glass: Glass) (26.1 only)

@MainActor @preconcurrency func backgroundExtensionEffect() -> some View
nonisolated init(_ sizing: SpacerSizing = .flexible, placement: ToolbarItemPlacement = .automatic) // ToolbarSpacer
nonisolated func tabBarMinimizeBehavior(_ behavior: TabBarMinimizeBehavior) -> some View
nonisolated func scrollEdgeEffectStyle(_ style: ScrollEdgeEffectStyle?, for edges: Edge.Set) -> some View
nonisolated func scrollEdgeEffectHidden(_ hidden: Bool = true, for edges: Edge.Set = .all) -> some View
nonisolated func safeAreaBar(edge: VerticalEdge, alignment: HorizontalAlignment = .center,
                             spacing: CGFloat? = nil, @ContentBuilder content: () -> some View) -> some View   // .top, .bottom
nonisolated func safeAreaBar(edge: HorizontalEdge, alignment: VerticalAlignment = .center,
                             spacing: CGFloat? = nil, @ContentBuilder content: () -> some View) -> some View   // .leading, .trailing
```

The default shape is a capsule (`DefaultGlassEffectShape`). `Glass.regular` blurs and adjusts luminosity for legibility; `Glass.clear` is highly translucent; `Glass.identity` leaves content as if no glass were applied, which is useful for toggling glass off without changing the view tree (https://developer.apple.com/documentation/swiftui/glass, checked 2026-11-05).

### 1.3 SwiftUI recipes

**One custom surface.** Apply `glassEffect` after the modifiers that set size and padding, because the glass is anchored to the view's bounds including padding (https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views, checked 2026-11-05).

```swift
import SwiftUI

struct NowPlayingPill: View {
    var body: some View {
        Label("Now playing", systemImage: "music.note")
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .glassEffect()   // regular glass in a capsule
    }
}
```

**Shape, tint and interaction.** Tint only to mark prominence (see [design-principles.md](design-principles.md#6-tint-signals-prominence-not-brand)). `interactive()` lets the material react to touch and pointer.

```swift
Text("Record")
    .padding(20)
    .glassEffect(.regular.tint(.red).interactive(), in: .rect(cornerRadius: 16))
```

**Clear glass over media, with a dimming layer.** Apple's own example for `Glass.clear` puts a dark layer underneath (https://developer.apple.com/documentation/swiftui/glass, checked 2026-11-05); the HIG suggests 35% opacity when the content beneath is bright.

```swift
PlayerControls()
    .padding()
    .glassEffect(.clear)
    .background(.black.opacity(0.35), in: .capsule)
```

**Several surfaces: always use a container.** `GlassEffectContainer` renders its effects together, which Apple says improves rendering performance and lets shapes blend. When the container spacing is larger than the stack spacing, the shapes merge while at rest (https://developer.apple.com/documentation/swiftui/glasseffectcontainer, checked 2026-11-05).

```swift
GlassEffectContainer(spacing: 20) {
    HStack(spacing: 12) {          // 12 < 20: the two buttons read as one blended shape
        Label("Draw", systemImage: "pencil")
            .labelStyle(.iconOnly)
            .frame(width: 44, height: 44)
            .glassEffect()
        Label("Erase", systemImage: "eraser")
            .labelStyle(.iconOnly)
            .frame(width: 44, height: 44)
            .glassEffect()
    }
}
```

**Morphing between states.** `glassEffectID(_:in:)` pairs shapes across a state change inside one container. It only acts during view hierarchy transitions or animations, so drive the change with `withAnimation` (https://developer.apple.com/documentation/swiftui/view/glasseffectid(_:in:), checked 2026-11-05).

```swift
struct ToolPalette: View {
    @State private var expanded = false
    @Namespace private var glass

    var body: some View {
        GlassEffectContainer(spacing: 24) {
            HStack(spacing: 24) {
                Button {
                    withAnimation(.bouncy) { expanded.toggle() }
                } label: {
                    Label(expanded ? "Close tools" : "Open tools",
                          systemImage: expanded ? "xmark" : "paintbrush")
                        .labelStyle(.iconOnly)
                        .frame(width: 44, height: 44)
                }
                .glassEffect(.regular.interactive())
                .glassEffectID("toggle", in: glass)

                if expanded {
                    Label("Eraser", systemImage: "eraser")
                        .labelStyle(.iconOnly)
                        .frame(width: 44, height: 44)
                        .glassEffect()
                        .glassEffectID("eraser", in: glass)
                }
            }
        }
    }
}
```

Use `.glassEffectTransition(.matchedGeometry)` (the default within container spacing) for nearby shapes and `.materialize` for shapes that appear far from any partner; `materialize` fades the content and animates the material without matching geometry (https://developer.apple.com/documentation/swiftui/glasseffecttransition, checked 2026-11-05). More on morph timing in [motion.md](motion.md#5-swiftui-glasseffectid-morphing).

**Union shapes that are not adjacent in the view tree.** All effects with the same union ID, shape and variant become one shape:

```swift
@Namespace private var group
let symbols = ["bold", "italic", "underline", "strikethrough"]

GlassEffectContainer(spacing: 8) {
    HStack(spacing: 8) {
        ForEach(symbols.indices, id: \.self) { index in
            Image(systemName: symbols[index])
                .frame(width: 40, height: 40)
                .glassEffect()
                .glassEffectUnion(id: index < 2 ? "weight" : "line", namespace: group)
                .accessibilityLabel(symbols[index])
        }
    }
}
```

**Buttons.** Prefer the system styles over a hand-built glass button; they bring the press response, focus handling and accessibility adaptations.

```swift
Button("Share", systemImage: "square.and.arrow.up") { share() }
    .buttonStyle(.glass)

Button("Done") { finish() }
    .buttonStyle(.glassProminent)   // the glass counterpart of .borderedProminent

Button("Skip") { skip() }
    .buttonStyle(.glass(.clear))   // 26.0; GlassButtonStyle(.clear) needs 26.1
```

On tvOS, `.glass` and `.glassProminent` apply glass whether or not the button has focus (https://developer.apple.com/documentation/swiftui/primitivebuttonstyle/glass, checked 2026-11-05).

**Bars, edges and tabs.**

```swift
TabView {
    Tab("Library", systemImage: "books.vertical") { LibraryView() }
    Tab("Search", systemImage: "magnifyingglass") { SearchView() }
}
.tabBarMinimizeBehavior(.onScrollDown)   // minimizing is iPhone only

ScrollView { ArticleBody() }
    .scrollEdgeEffectStyle(.hard, for: .top)   // .automatic, .hard (nearly opaque), .soft (blurred)
    .safeAreaBar(edge: .bottom) { CommentComposer() }

ContentView()
    .toolbar {
        ToolbarItemGroup {
            Button("Play", systemImage: "play") { }
            Button("Volume", systemImage: "speaker.wave.3") { }
        }
        ToolbarSpacer(.fixed)                  // splits the bar into two glass groups
        ToolbarItem {
            Button("Favorite", systemImage: "heart") { }
        }
    }
```

`backgroundExtensionEffect()` mirrors a view into the safe area around it, blurs the copies and clips the original, so a hero image appears to continue under a floating sidebar. Apple asks for discretion and a single instance (https://developer.apple.com/documentation/swiftui/view/backgroundextensioneffect(), checked 2026-11-05).

```swift
NavigationSplitView {
    Sidebar()
} detail: {
    Image("hero").resizable().scaledToFill()
        .backgroundExtensionEffect()
}
```

Apple's adoption guide also asks you to remove custom backgrounds from navigation bars, tab bars, toolbars and split views, because they interfere with the material and the scroll edge effect, and to avoid mixing text and icons in items that share one glass background (https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass, checked 2026-11-05).

### 1.4 UIKit

`UIGlassEffect` is a visual effect hosted in `UIVisualEffectView`. Group several with a `UIVisualEffectView` whose effect is `UIGlassContainerEffect` and whose `contentView` holds the glass views (https://developer.apple.com/documentation/uikit/uiglasscontainereffect, checked 2026-11-05).

```swift
import UIKit

func makeGlassChip(title: String) -> UIVisualEffectView {
    let effect = UIGlassEffect(style: .regular)   // or .clear
    effect.isInteractive = true
    effect.tintColor = nil                        // set a color only for prominence
    let view = UIVisualEffectView(effect: effect)
    let label = UILabel()
    label.text = title
    label.translatesAutoresizingMaskIntoConstraints = false
    view.contentView.addSubview(label)            // never add subviews to the effect view itself
    NSLayoutConstraint.activate([
        label.leadingAnchor.constraint(equalTo: view.contentView.leadingAnchor, constant: 16),
        label.trailingAnchor.constraint(equalTo: view.contentView.trailingAnchor, constant: -16),
        label.topAnchor.constraint(equalTo: view.contentView.topAnchor, constant: 10),
        label.bottomAnchor.constraint(equalTo: view.contentView.bottomAnchor, constant: -10),
    ])
    return view
}

let containerEffect = UIGlassContainerEffect()
containerEffect.spacing = 20                      // distance at which children begin to merge
let container = UIVisualEffectView(effect: containerEffect)
container.contentView.addSubview(makeGlassChip(title: "Draw"))
container.contentView.addSubview(makeGlassChip(title: "Erase"))
```

Buttons use configurations: `UIButton.Configuration.glass()`, `.prominentGlass()`, `.clearGlass()`, and `.prominentClearGlass()` (listed on the adoption page) (https://developer.apple.com/documentation/uikit/uibutton/configuration-swift.struct/glass(), checked 2026-11-05).

```swift
var config = UIButton.Configuration.glass()
config.title = "Share"
config.image = UIImage(systemName: "square.and.arrow.up")
let share = UIButton(configuration: config)
```

Shape the glass with the corner configuration API (`cornerConfiguration`, `UICornerConfiguration`) named in the adoption guide; check its factory methods in Apple's docs, as our snapshot did not capture them. Custom bars over scrolling content use `UIScrollEdgeElementContainerInteraction`; scroll edges are tuned through `UIScrollEdgeEffect` (`isHidden`, `style`).

`UIVisualEffectView` rules still apply (https://developer.apple.com/documentation/uikit/uivisualeffectview, checked 2026-11-05):

- Do not set `alpha` below 1 on the effect view or any superview; the effect can render wrong or disappear. Fade by animating the `effect` or the content, not the container alpha.
- Masking a superview of an effect view throws.
- A snapshot of only the effect view does not contain the effect. Snapshot the window for tests and screenshots.

Reduce Transparency: `UIAccessibility.isReduceTransparencyEnabled` (iOS 8+) and its change notification. System glass adapts on its own; see [accessibility.md](accessibility.md#10-apple-platform-settings).

### 1.5 AppKit

```swift
import AppKit

let glass = NSGlassEffectView()
glass.style = .regular            // or .clear
glass.cornerRadius = 16
glass.tintColor = nil
glass.contentView = NSTextField(labelWithString: "Inspector")

let row = NSStackView(views: [glass /*, more NSGlassEffectViews */])
row.spacing = 8

let container = NSGlassEffectContainerView()
container.spacing = 12            // merges descendant glass views within this distance
container.contentView = row

let button = NSButton(title: "Share", target: nil, action: nil)
button.bezelStyle = .glass
```

`NSGlassEffectView.effectIsInteractive` (`var effectIsInteractive: Bool { get set }`) is macOS 27.0, not 26.0: it needs the macOS 27 SDK and an `if #available(macOS 27.0, *)` gate (https://developer.apple.com/documentation/appkit/nsglasseffectview/effectisinteractive, checked 2026-11-05). The container renders its descendants with fewer passes (https://developer.apple.com/documentation/appkit/nsglasseffectview, checked 2026-11-05).

### 1.6 Opting out: `UIDesignRequiresCompatibility`

Setting the Info.plist key `UIDesignRequiresCompatibility` to `YES` keeps the pre-26 look while building with the 26 SDK (https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass, checked 2026-11-05). An Apple DTS answer in June 2026 says the key is **ignored when the app links against the iOS 27 SDK or later**; apps linked with the iOS 26 SDK keep the opt-out on iOS 27 devices (https://developer.apple.com/forums/thread/832543, checked 2026-11-05). The App Store deadline for building with the iOS 27 SDK had not been announced at that time; watch https://developer.apple.com/news/upcoming-requirements/. Treat the key as a short bridge, not a plan.

### 1.7 User settings that change the material

- iOS, iPadOS and macOS 26.1 add a Liquid Glass setting with Clear and Tinted (more opaque) options. On iOS and iPadOS it is in Settings > Display & Brightness; on the Mac it is in System Settings > Appearance (https://www.macrumors.com/2025/10/20/ios-26-1-liquid-glass-toggle/, checked 2026-11-05, Medium: secondary source).
- Reports of iOS 27 changes (a transparency slider, darker edges, better diffusion) come from secondary press only (https://macrumors.com/2026/06/10/how-liquid-glass-is-changing-in-ios-27, checked 2026-11-05, Medium). The claim that the iOS control moved to Settings > Appearance is **UNVERIFIED**.
- Apple's public `Glass` docs still list only `regular`, `clear`, `identity`, `tint(_:)` and `interactive(_:)` as of 2026-11-05.

Custom glass must look acceptable under every setting: Clear, Tinted, Reduce Transparency, Increase Contrast, and Reduce Motion.

### 1.8 Web components mapped to native (glasshq comparison app)

glasshq ships a macOS 26+ SwiftUI app that renders each web component next to its closest Apple equivalent. It is explicitly "not a native port" (glasshq `apps/native-reference/README.md`). Use the table when porting a web glass design to Apple platforms: replace the custom web control with the system one rather than recreating the web material.

| Web component or option (glasshq) | Native equivalent used | Source |
| --- | --- | --- |
| `material="clear"` / `"regular"` plus `tint` | `Glass.clear` / `Glass.regular` with `.tint(_:)` | glasshq `apps/native-reference/Sources/NativeReference.swift` |
| `GlassSurface interactive` | `.glassEffect(material.interactive(), in: .rect(cornerRadius: 38))` | glasshq `Sources/NativeReference.swift`, `Sources/NativeUsage.swift` |
| `GlassScene` (grouping) | `GlassEffectContainer(spacing: 0)` | glasshq `Sources/NativeReference.swift` |
| `GlassButton` | `.buttonStyle(.glass)`, `.buttonBorderShape(.capsule)` or `.circle`, `.controlSize(.large)` | glasshq `Sources/NativeReference.swift` |
| `GlassToolbar` with spacers | window `.toolbar { ToolbarItemGroup ... ToolbarSpacer(.fixed) }` | glasshq `Sources/NativeUsage.swift` |
| `GlassTabs` | `NSSegmentedControl` with `borderShape = .capsule`; glasshq also sets a macOS 27 `role = .tabs` (not checked against Apple docs here) | glasshq `Sources/NativeUsage.swift` |
| `GlassMenu` and submenus | SwiftUI `Menu`; the system owns material, placement and animation | glasshq `Sources/NativeUsage.swift` |
| `GlassSlider`, `GlassSwitch` | `Slider`, `Toggle(.switch)`, or `NSSlider`, `NSSwitch`; thumbs use the system material, so Clear or Regular cannot be chosen | glasshq `Sources/NativeUsage.swift`, `Sources/NativeValueControls.swift` |
| `GlassScrollEdges` | `.scrollEdgeEffectStyle(.soft or .hard, for:)`, `.scrollEdgeEffectHidden()`, `.safeAreaBar(edge:)` | glasshq `Sources/NativeProgressiveScenes.swift`, `Sources/NativeUsage.swift` |
| `GlassProgressiveBlur` over an image | `NSVisualEffectView` with a `CAGradientLayer` mask: a material fade, not a variable blur | glasshq `Sources/NativeProgressiveScenes.swift` |

Gaps the app records: Apple exposes no numeric blur radius or refraction amount, and no drag-stretch parameters (glasshq `apps/native-reference/README.md`, `Sources/NativeUsage.swift`). Web tuning values such as `refraction: 60` have no native counterpart; do not try to fake them with overlays.

## 2. Android

There is no system glass material in Android or in Material 3 primary docs as of 2026-11-05. Press coverage says Android 16's Material 3 Expressive system UI uses background blur and that Google is adding a setting to turn blur off (https://www.androidauthority.com/android-getting-option-disable-background-blur-3590124, checked 2026-11-05, Medium-Low).

### 2.1 Platform primitives

| Primitive | API level | What it does | Source (checked 2026-11-05) |
| --- | --- | --- | --- |
| `RenderEffect.createBlurEffect(radiusX, radiusY, Shader.TileMode)` | 31 | blurs the view or `RenderNode` it is set on | https://developer.android.com/reference/android/graphics/RenderEffect |
| `RenderEffect.createChainEffect`, `createColorFilterEffect`, `createShaderEffect`, `createOffsetEffect`, `createBlendModeEffect` | 31 | compose effects, tint, color adjust | same |
| `RenderEffect.createRuntimeShaderEffect(RuntimeShader, String)` | 33 | runs an AGSL shader over the content; this is the refraction path | same |
| `RuntimeShader` (AGSL) | 33; `setInputColorFilter`, `setInputXfermode` 36; `setWorkingColorSpace` 37 | shader uniforms, input shaders | https://developer.android.com/reference/android/graphics/RuntimeShader |
| Compose `Modifier.blur` | 31; ignored on older versions | blurs the composable's own content, not what is behind it | https://developer.android.com/develop/ui/compose/graphics/images/customize |
| Window blur: `Window#setBackgroundBlurRadius`, `FLAG_BLUR_BEHIND` | 31 | blurs what is behind a translucent window (dialogs, sheets) | https://source.android.com/docs/core/display/window-blurs |

The system can disable window blurs at runtime (battery saver, some video paths, low-end GPUs, a developer option). Check `WindowManager#isCrossWindowBlurEnabled` and listen with `addCrossWindowBlurEnabledListener`, then switch to a scrim (https://source.android.com/docs/core/display/window-blurs, checked 2026-11-05).

The core difficulty: `RenderEffect` filters the view it is attached to. To blur or refract what sits **behind** a panel, you render the background content again into a node or layer that the panel can filter. That is what the libraries below do.

### 2.2 Refraction sketch with AGSL (API 33+)

An original, minimal lens: it pulls samples inward near the rim of a rounded rectangle. It assumes the view draws (a copy of) the backdrop it should refract.

```kotlin
import android.graphics.RenderEffect
import android.graphics.RuntimeShader
import android.os.Build
import android.view.View
import androidx.annotation.RequiresApi

private const val LENS_AGSL = """
uniform shader content;
uniform float2 size;
uniform float radius;
uniform float bezel;      // px band where bending happens
uniform float strength;   // max pull in px at the rim

half4 main(float2 p) {
    float2 c = size * 0.5;
    float2 q = abs(p - c) - (c - radius);
    float d = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - radius; // < 0 inside
    float depth = clamp(-d / bezel, 0.0, 1.0);
    float edge = 1.0 - sqrt((2.0 - depth) * depth);                    // 1 at rim, 0 past the bezel
    float2 n = normalize(p - c + float2(1e-4));
    return content.eval(p - n * edge * strength);
}
"""

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
fun View.applyLens(radiusPx: Float, bezelPx: Float = 20f, strengthPx: Float = 24f) {
    val shader = RuntimeShader(LENS_AGSL)
    shader.setFloatUniform("size", width.toFloat(), height.toFloat())
    shader.setFloatUniform("radius", radiusPx)
    shader.setFloatUniform("bezel", bezelPx)
    shader.setFloatUniform("strength", strengthPx)
    setRenderEffect(RenderEffect.createRuntimeShaderEffect(shader, "content"))
}
```

The edge profile follows the circular-arc bezel described for glasshq (`packages/liquid-glass/src/core/optics.ts`); the radial normal is a simplification (inference: acceptable for capsules, visibly wrong near long straight edges; use the SDF gradient for production). Reapply when the size changes. In Compose, convert with `asComposeRenderEffect()` and set it in `Modifier.graphicsLayer { renderEffect = ... }`.

Fallback ladder: API 33+ shader lens, API 31-32 blur plus tint, API 30 and below a translucent scrim with a hairline border.

### 2.3 Libraries

| Library | What it offers | Maturity (our label) | License | Source (checked 2026-11-05) |
| --- | --- | --- | --- | --- |
| Haze (chrisbanes) | Compose Multiplatform backdrop blur. Android API 23+, iOS, macOS arm64, desktop JVM, Web. Full features on API 33+; API 31-32 blur with extra cost for progressive effects; API 30 and below blur off by default with a scrim (`fallbackColorEffect`) | Stable: 1.7.2 released 2026-02-10 per the changelog mirror. A 2.0.0 alpha adds an experimental `haze-liquidglass` module whose publishing was disabled until stable | Apache-2.0 per prior knowledge, **UNVERIFIED** | https://chrisbanes.github.io/haze/latest/blur/platforms/ ; https://chrisbanes.github.io/haze/latest/changelog/ |
| Kyant0 AndroidLiquidGlass ("Backdrop") | "A customizable Liquid Glass effect library for Compose Multiplatform", Maven `io.github.kyant0:backdrop`; samples (button, toggle, slider, tabs) but no high-level components | Young; lens refraction relies on AGSL, so API 33+ (Low confidence, from a port's compatibility table) | **UNVERIFIED** | https://github.com/Kyant0/AndroidLiquidGlass |

Check both licenses in the repositories before adopting; our snapshot could not reach the GitHub API.

## 3. Flutter

- **Frosted glass, every renderer:** `BackdropFilter` with `ImageFilter.blur` clipped by `ClipRRect`. Well established; not re-fetched for this snapshot (Medium).

```dart
import 'dart:ui';
import 'package:flutter/material.dart';

class FrostedPanel extends StatelessWidget {
  const FrostedPanel({super.key, required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: const Color(0x33FFFFFF),                       // 20% white tint
            border: Border.all(color: const Color(0x66FFFFFF)),   // rim
            borderRadius: BorderRadius.circular(24),
          ),
          child: Padding(padding: const EdgeInsets.all(16), child: child),
        ),
      ),
    );
  }
}
```

- **Refraction:** `liquid_glass_renderer` (whynotmake-it) requires the Impeller renderer (Skia is unsupported) and does not support Web, Windows or Linux. Its 1.0.0-dev.1 rewrite needs Flutter 3.47+ and Flutter GPU (a preview feature) and falls back to `FakeGlass` automatically (https://pub.dev/documentation/liquid_glass_renderer/latest/, checked 2026-11-05, Medium). Label it **experimental**; ship the `BackdropFilter` path as the default and opt in per platform.
- On iOS 26, an app that wants the real system material inside Flutter needs a platform view or plugin that hosts `UIGlassEffect`. We found no primary source for a maintained plugin (**UNVERIFIED**).

## 4. React Native

Nothing in our snapshot was checked against primary sources for React Native, so every row is **UNVERIFIED** and the labels are cautious.

| Option | What it would give | Maturity label |
| --- | --- | --- |
| A blur view package (for example the community blur view or Expo's blur module) | frosted blur on iOS and Android, no refraction | Commonly used; versions and Android behavior **UNVERIFIED** |
| A package that wraps `UIGlassEffect` on iOS 26 (Expo and third parties have published such views) | the real system material on iOS 26 only; a fallback elsewhere | New; API and maintenance **UNVERIFIED** |
| Your own native module: `UIVisualEffectView(effect: UIGlassEffect(...))` on iOS 26, `RenderEffect` on Android 31+, a scrim otherwise | full control, matches sections 1.4 and 2 | Depends on your team; the safest long-term option |
| Skia-based shaders in React Native | custom refraction on both platforms | Possible in principle; performance and backdrop access **UNVERIFIED** |

Whatever you choose, keep content in normal React Native views above the effect so it stays accessible, and keep the fallback path tested.

## 5. Porting checklist

1. On Apple platforms, use system components first, then `glassEffect` or `UIGlassEffect` or `NSGlassEffectView`, always inside a container when there are two or more.
2. Never add glass in the content layer (cards, list rows, backgrounds). See [design-principles.md](design-principles.md#2-two-layers-controls-float-content-does-not).
3. Remove custom bar backgrounds that fight the material.
4. Test Clear, Tinted, Reduce Transparency, Increase Contrast and Reduce Motion.
5. On Android, branch by API level (33 shader, 31 blur, older scrim) and listen for cross-window blur changes.
6. On Flutter and React Native, ship the blur or scrim path first; treat refraction packages as opt-in.

## APIs that do not exist

Agents and published agent skills produce glass API names that look right and do not compile, or that apply a real name in the wrong place. Check generated code against this list before running it. Each row is backed by Apple's DocC (checked 2026-11-05, from the platform snapshot in [research-snapshot.md](research-snapshot.md)), by the tables above, or by the survey of existing liquid glass skills ([research decision report, per-finalist notes](../research/skills-survey/outputs/research-decision-report.md#per-finalist-notes)), which cites each skill as `owner/repo@commit:path:line`.

| Name you may see | Status | Use instead | Evidence |
| --- | --- | --- | --- |
| `Glass.thin`, `Glass.thick`, `Glass.ultraThin`, `Glass.prominent` | No such variants. `Glass` has `regular`, `clear` and `identity`, plus `tint(_:)` and `interactive(_:)` | `.glassEffect(.regular)` or `.glassEffect(.clear)`; color with `.regular.tint(color)`; a prominent button with `.buttonStyle(.glassProminent)`. `.ultraThinMaterial` and `.regularMaterial` are the older `Material` blurs, useful for the pre-26 path, not `Glass` values | https://developer.apple.com/documentation/swiftui/glass |
| `.glassEffectTransition(.matchedGeometry \| .materialize)` | Not valid Swift. `GlassEffectTransition` is a struct with three static values, not an option set | Pass one value: `.glassEffectTransition(.matchedGeometry)` for shapes within the container spacing, `.materialize` for shapes farther apart, `.identity` for none | https://developer.apple.com/documentation/swiftui/glasseffecttransition; seen in `Tsdsj/Apple-Style@103385529843:skills/Apple-Style-Liquid-Glass/SKILL.md:53` |
| `.scrollEdgeEffectStyle(.soft \| .hard, for: .top)` | Not valid Swift; the style is a single optional value | One of `.automatic`, `.soft` or `.hard`: `.scrollEdgeEffectStyle(.soft, for: .top)`; hide it with `.scrollEdgeEffectHidden()` | https://developer.apple.com/documentation/swiftui/scrolledgeeffectstyle; seen in `Tsdsj/Apple-Style@103385529843:skills/Apple-Style-Liquid-Glass/SKILL.md:53` |
| `.buttonShape(.capsule)` | Not a SwiftUI modifier | `.buttonStyle(.glass)` with `.buttonBorderShape(.capsule)` or `.circle`, as in section 1.8 | glasshq `apps/native-reference/Sources/NativeReference.swift`; seen in `WAIS-CLOUD-SORTER/liquid-glass@11f18a25:references/swiftui.md:46` |
| `glassEffectWithFallback(_:)` | Not an Apple API. It is a helper one surveyed skill defines, and its version names `Glass` without `@available` | Write the branch yourself: `if #available(iOS 26.0, macOS 26.0, *) { content.glassEffect(.regular, in: shape) } else { content.background(.regularMaterial, in: shape) }`. Mark any helper that takes `Glass` with `@available(iOS 26.0, macOS 26.0, *)` | `AvdLee/SwiftUI-Agent-Skill@204dba7:skills/swiftui-expert-skill/references/liquid-glass.md:377-390` |
| `UIGlassEffect.Style.prominent` | `UIGlassEffect` styles are `.regular` and `.clear` | Prominence is a button configuration: `UIButton.Configuration.prominentGlass()` or `.prominentClearGlass()` | https://developer.apple.com/documentation/uikit/uiglasseffect; https://developer.apple.com/documentation/uikit/uibutton/configuration-swift.struct/glass() |
| `UIGlassEffect` in an AppKit app, `NSGlassEffectView` on iOS | Wrong framework. UIKit glass covers iOS, iPadOS, Mac Catalyst and tvOS; AppKit glass is macOS only | `NSGlassEffectView` and `NSGlassEffectContainerView` in AppKit; `UIGlassEffect` in `UIVisualEffectView` in UIKit and Mac Catalyst | Section 1.1; https://developer.apple.com/documentation/appkit/nsglasseffectview |
| `glassEffect(_:in:)` on visionOS | Not available on visionOS. The system draws its own window glass, which apps cannot modify | Use standard visionOS windows and controls; for a custom panel or ornament use `.glassBackgroundEffect()` (visionOS 1.0) | Section 1.1; https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:); https://developer.apple.com/documentation/swiftui/view/glassbackgroundeffect(displaymode:) |
| A numeric blur radius or refraction amount on `Glass` (for example a value copied from web tuning such as `refraction: 60`) | Apple exposes no such parameter | Choose `regular` or `clear`, tint, and interactivity; leave the optics to the system | glasshq `apps/native-reference/README.md` (section 1.8) |
| Any Android system or Material 3 "glass" material, modifier or component | None exists in the Android or Material 3 primary docs as of 2026-11-05 | `RenderEffect` blur on API 31+, an AGSL `RuntimeShader` lens on API 33+, a scrim below; or a library such as Haze (sections 2.1 to 2.3) | Section 2 |
| `@media (prefers-reduced-rendering: reduce)` in a web view or React Native web build | Not a CSS media feature | `prefers-reduced-transparency`, `prefers-contrast: more`, `forced-colors: active` and `prefers-reduced-motion`, plus an in-app "solid surfaces" setting because Safari does not expose reduced transparency | [accessibility.md](accessibility.md#4-reduced-transparency); seen in `WAIS-CLOUD-SORTER/liquid-glass@11f18a25:references/refraction-advanced.md:152` |

Real names that agents misuse:

- **`UIDesignRequiresCompatibility`** exists, but it is a bridge, not a permanent opt-out: Apple DTS says it is ignored once the app links against the iOS 27 SDK (section 1.6).
- **Compose `Modifier.blur`** blurs the composable's own content, not what is behind it, so it cannot make a frosted panel by itself (section 2.1).
- **`UIVisualEffectView.alpha`** below 1 on the effect view or a superview makes the effect render wrong or vanish; fade the `effect` or the content instead (section 1.4).

Not settled here: one surveyed skill uses `navigationZoomTransition` and `navigationTransitionSource` for sheet morphing while another file in the same skill uses `matchedTransitionSource` with `.navigationTransition(.zoom)` (`AvdLee/SwiftUI-Agent-Skill@204dba7`, survey claim clm_017). This snapshot did not check either set against Apple's docs; look them up before using any of them.

## Related references

- [design-principles.md](design-principles.md) for where glass belongs
- [accessibility.md](accessibility.md) for settings and contrast checks
- [motion.md](motion.md) for morph and press behavior
- [library-matrix.md](library-matrix.md) for web libraries
