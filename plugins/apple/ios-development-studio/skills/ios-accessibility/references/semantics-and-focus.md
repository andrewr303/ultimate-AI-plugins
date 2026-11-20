# Semantics, actions and focus

## Start with the task

Describe what someone must perceive and do: identify an item, understand its status, select an option, edit a field, resolve an error and complete or cancel the action. Inspect the accessibility representation of that flow, not just its visible labels.

Native controls normally supply useful roles, state and activation. Use buttons for actions, toggles for on/off state, pickers for exclusive choices and text fields for editing. A gesture-only custom surface needs equivalent accessible actions and meaningful focus behavior. An accessibility trait alone may describe a button without implementing the expected action.

## Labels, values and hints

Give an action a concise contextual name. A plus symbol might mean Add account, Add item or Increase quantity; its default symbol name may not explain the task. A visible icon-only button can retain a text label through the supported label style or an explicit accessible name.

Avoid repeating the control type or current state unnecessarily when the system already announces them. Use values for changing state and hints only for non-obvious effects. Localize accessibility text along with visible copy. Keep stable Voice Control input labels where visible content changes frequently or includes volatile numeric data.

Meaningful images need an alternative unless nearby text already conveys the same content and appropriate grouping avoids duplication. Decorative imagery should not become a focus stop. Do not hide an image that is the only way to understand a chart, attachment or status; provide the information through an accessible representation.

## Grouping and reading order

Group related descriptive content when it forms one logical item. Do not combine a row so aggressively that distinct buttons, links or editable fields become unreachable. A custom row with multiple actions may need individual controls or named custom actions; choose the model that keeps the task discoverable.

Traversal should follow the meaningful hierarchy, including right-to-left contexts. Source order, visual position and explicit accessibility sorting can diverge. Use priority/order overrides sparingly; test the result rather than assuming a numeric priority fixes every layout.

When a component is hidden, check visual opacity, hit testing and accessibility exposure separately. An invisible overlay can still capture taps or focus. Disabled controls should communicate their state, and any explanation for why they are disabled must be reachable if the user needs it.

## Focus and updates

After presenting a screen or modal, focus should land somewhere useful and remain within the active presentation as appropriate. After dismissal, returning focus to the invoking control can preserve orientation. Avoid moving focus on every state update or while someone is editing.

Dynamic results and validation errors need a discoverable update. Prefer concise announcements or focus changes only when they help the task. Do not announce every progress percentage, timer tick or streaming token. Expose an understandable stable value and allow the user to inspect details.

For forms, identify field purpose, required state and validation. Associate errors with fields and provide an actionable summary when several failures occur. Preserve entered content after a recoverable error. Ensure custom input controls work with keyboard and assistive activation, not just direct touch.

## Runtime checks

| Task | Observe |
| --- | --- |
| Traverse a list row | Name/status understandable; distinct actions reachable |
| Activate icon action | Correct meaningful action announced and performed |
| Present/dismiss modal | Useful initial focus and coherent return location |
| Submit invalid form | Error discoverable without losing entered data |
| Update async content | Completion understandable without repetitive noise |
| Use Voice Control | Stable recognizable action names where needed |
| Use external keyboard | Focus and activation follow intended interaction |

Automated trees and audits can find missing labels or frames; they cannot establish that the full task makes sense. Test the actual workflow with the relevant mode when possible.

## Provenance

Original synthesis informed by uploaded Paul Hudson `SwiftUI-Agent-Skill-main.zip`, `swiftui-pro/references/accessibility.md`; AvdLee variant, `skills/swiftui-expert-skill/references/accessibility-patterns.md`; and `swiftui-design-principles-main.zip`, `SKILL.md` native-control guidance. Universal gesture bans were replaced with semantic-equivalence checks. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
