# Materials and opt-in Glass

Read this for explicitly requested adoption or for fixing an existing material implementation. Ordinary feature work does not require a new material style.

## Verify support

Inspect the selected SDK's actual declarations and availability before choosing any effect, container, shape or transition. Record the project's deployment target. Compiler/SDK recognition and runtime availability are separate: an availability branch does not teach an old SDK a missing declaration. Keep a supported material or opaque fallback when the app supports earlier runtimes.

Do not import device names, version defaults or symbols from source guides without this verification. If tooling cannot establish support, describe the proposal as unverified or use the project's existing supported treatment.

## Composition questions

- Which surfaces are controls/navigation chrome, and which are content?
- What background lies behind the material during real use?
- Does tint or transparency reduce legibility in any supported appearance?
- Do neighboring effects need the native grouping/container mechanism?
- Are shape, spacing and effect identity stable as controls appear or move?
- Is an interactive treatment attached to a real interactive control?

Use native controls and effects when appropriate. Apply modifiers in the order required by the verified API, with layout and shape decisions made explicitly. Do not simulate every native effect through stacked blur, opacity and custom shadows. Avoid treating an entire scrolling content surface as chrome merely to show the effect.

When animating grouped material controls, use supported identity/container mechanisms deliberately. A transition should correspond to a meaningful hierarchy change. Measure complex effect compositions when they stutter; the presence of a native API does not guarantee a particular frame rate.

## Accessibility and fallback

Check reduced transparency, increased contrast, light/dark backgrounds and reduced motion. The fallback must preserve labels, affordance, focus indication and hit targets. A disabled or selected control needs more than a subtle translucency difference. Give motion-sensitive users a calmer transition when the effect includes large movement or morphing.

Test the actual content and scrolling background, not only a blank preview. A material that looks readable over a solid color may fail over an image. Route semantic checks to [accessibility](../../ios-accessibility/SKILL.md).

## Evidence

Record the SDK/runtime support checked, tested appearances and settings, fallback behavior, and any actual visual/runtime capture. Do not call a source-level modifier review a tested effect. Keep unrelated screens unchanged unless the requested scope includes broader adoption.

## Provenance

Original synthesis informed by `Skills-main.zip`, `swiftui-liquid-glass/SKILL.md` and `references/liquid-glass.md`; uploaded AvdLee `SwiftUI-Agent-Skill-main.zip`, `skills/swiftui-expert-skill/references/liquid-glass.md`. No source-supplied future release/API claims are asserted. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
