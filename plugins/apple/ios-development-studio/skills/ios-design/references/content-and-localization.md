# Content, formatting and localization

## Inspect the resource contract

Identify String Catalogs or other localization resources, bundle ownership, supported locales, format conventions and existing accessibility strings. A package resource may need its own bundle rather than the app's main bundle. Do not replace established localization keys with dynamic strings during visual cleanup.

Distinguish localizable user-facing text from identifiers. Localize sentences as units with interpolation or supported pluralization; concatenating independently translated fragments constrains word order. A string assembled dynamically can lose its lookup key. Use meaningful translator context for ambiguous labels and preserve placeholders in every locale.

Prefer supported locale-aware format APIs for dates, numbers, currencies, durations and measurements. The user's calendar, locale and time zone may matter differently: a server timestamp, a calendar day and a recurring local reminder are distinct concepts. Confirm the product rule instead of formatting everything with the device's current time zone.

Identifiers such as a model number or year label may require no grouping; monetary or quantity values usually need locale conventions. Do not convert a numeric-looking identifier into a number if leading zeros matter. Test plural zero/one/many cases and unusually long formatted values.

## Interface copy

Use concise labels that explain actions in context. A primary button should describe the result, and an error should state the useful next step without exposing a raw network response. Avoid repeating the same explanation in title, subtitle, footer and button.

Do not remove necessary qualification merely to shorten text. Destructive or paid actions need clear scope and effect consistent with the product's established interaction. Keep implementation detail out of visible copy unless it helps the person make a meaningful choice.

## Layout expansion and direction

Test long translations rather than assuming English lengths. Let text wrap where appropriate and permit controls to grow. An ellipsis is suitable for secondary identifiers in some contexts; it is harmful if it removes the action or information required to decide.

Use leading/trailing semantics for directional layout. Mirror navigation where system conventions require it, but do not mirror inherently directional media, charts or identifiers blindly. Mixed-language text, telephone numbers and URLs may need specific direction handling. Validate with an actual right-to-left locale; forcing only a layout direction cannot reveal every localization issue.

Prefer semantic system symbols and localized assets when suitable. A symbol can mean different things in different locales; pair actions with useful labels. Decorative images should not create redundant announcements. Meaningful images need localized alternatives if their content is not otherwise available.

## Fixtures

- A long action label at a large text size remains actionable.
- A zero-item state uses correct pluralization and a useful next action.
- A right-to-left detail view has coherent reading order and navigation.
- A package-owned view resolves strings from the intended bundle.
- A server time near midnight renders according to the defined product rule.
- An identifier with leading zeros is preserved.

Build or validate localized resources with the available project tooling. A screenshot cannot verify that every locale key resolves; inspect resource coverage as well.

## Provenance

Original guidance informed by both uploaded `SwiftUI-Agent-Skill-main.zip` variants, their respective `references/localization.md`, and `swiftui-design-principles-main.zip`, `SKILL.md` numeric-formatting and content-hierarchy guidance. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
