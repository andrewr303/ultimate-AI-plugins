# Route ownership and presentation identity

## Choose the owner

Start from the existing shell. A simple screen with one sheet may need only local optional state. A multi-tab application can need one independent path per tab. Multiple app scenes usually need their own selected record and history. A global router is useful only when its lifetime and responsibilities are truly global.

| State | Typical lifetime | Questions |
| --- | --- | --- |
| Selected tab | Scene or app, per product rule | Should another window change with it? |
| Navigation path | Stack/scene/tab owner | What clears it on logout or context change? |
| Local modal payload | Presenting feature | What happens when its underlying item changes? |
| Editing draft | Editing session | Does Cancel discard or persist changes? |
| Cross-feature intent | App coordinator or existing router | How is it consumed once and acknowledged? |

Store lightweight destination identifiers and route parameters, not live view instances or entire database objects. A stable ID can be resolved by the destination with explicit loading/not-found/unauthorized behavior. Keep serialization formats independent from internal presentation types when long-term restoration matters.

For SwiftUI, map route data to destinations at the appropriate stack boundary using APIs supported by the deployment target. Do not attach destinations deep inside transient lazy rows if lifetime/discovery becomes unreliable. For UIKit, preserve the existing controller/coordinator ownership and synchronize any SwiftUI adapter at a clear boundary.

## Paths and tabs

One path shared across tabs means shared history; that is a product choice, not a default. If histories should be independent, keep separate owners. Switching tabs should not unexpectedly clear a draft or append a detail to the wrong stack.

Define what selecting the active tab again does: no change, scroll to top, or pop to root according to project behavior. Reset or rebuild paths intentionally when account/workspace context changes. Do not leave a path carrying identifiers from a previous account.

Avoid duplicate sources of truth, such as an enum route plus an unrelated selected object plus a Boolean all describing the same presentation. Use a clear conversion at boundaries where multiple frameworks require different representations.

## Payload-driven sheets

When presentation requires an item, make the selected payload drive presentation. A Boolean plus separately managed data can open a sheet before data exists or keep old data after selection changes.

Give presentation identity deliberate meaning. If different payloads should replace the editor, their identity must distinguish them. Reusing a single ID for several cases can retain local state unexpectedly. Conversely, changing identity for every render destroys a draft. Test switching A → B while a modal is visible and closing/reopening the same item.

Define dismissal responsibility. A sheet can own its internal Save/Cancel controls while the presenting feature observes completion through an explicit contract. A parent-controlled workflow may need callbacks or a coordinator; do not ban them categorically. Save should dismiss only after the required result, or clearly show progress/error behavior.

Avoid immediate save-on-change when a Cancel button promises to discard edits. Use a draft or transactional operation as appropriate. Define dismissal by gesture, backgrounding, account change and underlying record deletion. If interactive dismissal is blocked, provide an understandable route to save or discard.

## Nested navigation and synchronization

A modal with its own push flow needs its own appropriate navigation container or coordinator. Ensure environment dependencies reach modal destinations and that dismiss acts on the intended presentation.

When bridging UIKit and SwiftUI, decide who is authoritative for path and dismissal. Reflect completed transitions back once; avoid a callback loop that pushes or dismisses twice. Canceled interactive transitions must not leave model state claiming the destination disappeared.

## Fixtures

1. Open details in tab A, switch to B and back: history follows the product contract.
2. Open two app scenes: changing one scene's path affects the other only if deliberately shared.
3. Present item A then switch to B: title, actions and draft belong to B.
4. Save fails: the modal remains useful and editable with an actionable error.
5. Cancel an interactive pop/dismissal: state matches the visible UI.
6. Log out while detail is active: account-bound state is cleared or safely re-resolved.

## Provenance

Original synthesis informed by `Skills-main.zip`, `swiftui-ui-patterns/references/navigationstack.md`, `sheets.md` and `app-wiring.md`; uploaded Paul Hudson `SwiftUI-Agent-Skill-main.zip`, `swiftui-pro/references/navigation.md`; AvdLee variant, `skills/swiftui-expert-skill/references/sheet-navigation-patterns.md`. Global-router mandates, shared modal IDs from examples and speculative API guidance were generalized or excluded. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
