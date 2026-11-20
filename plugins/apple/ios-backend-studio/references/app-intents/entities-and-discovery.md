# Siri, Apple Intelligence and controlled entity exposure

## Decision to make

Decide which real app actions/content should be discoverable, which domain schema actually fits and what information may leave the app’s ordinary view context. A backend integration does not justify indexing every record or inventing a generic schema match.

## Workflow

1. Separate the stable App Intent command layer from optional newer schema adoption. Inventory the actual SDK, app domain and supported system experiences.
2. Adopt a system schema only when its meaning matches the app action/entity. If a use-case group requires related schemas, use Xcode diagnostics and the actual domain documentation to implement the complete supported set.
3. Make entity identity stable across refreshes. Keep lookup permission-aware and remove or invalidate suggestions/index entries when the account or access changes.
4. Annotate only content that the current interface actually represents. Use an entity identifier or supported view-entity mechanism rather than sending unrelated backend records as context.
5. Where transfer representations are appropriate, expose the minimum structured value needed for interoperability. A file/image representation and a structured location/contact value are different contracts.
6. Preserve existing shortcuts when newer schema requirements change property shapes. Add a compatible intent or staged transition rather than silently breaking saved user workflows.

## Privacy and backend boundary

Display names, shortcut phrases, indexed entities and onscreen context can expose information beyond the app’s ordinary UI. Use deliberate data selection, no secrets and the actual account’s authorized records. Backend endpoints must still enforce current access when an action or query arrives; discovery metadata is not an access grant.

## Failure cases and tests

Check unsupported SDK/runtime, mismatched domain, missing required schema member, duplicate old/new actions, stale entity identifiers, revoked sharing and multiple accounts. Verify that the app remains useful with basic App Intents even when an optional Apple Intelligence integration is unavailable. Do not claim Siri AI behavior from a passing schema or build check.

## Entity freshness and privacy decisions

Define how entity suggestions/index entries are refreshed after edits, deletion, permission changes and account transitions. Keep exported display values sufficient for the user's task but avoid private backend payloads, secret links or tokens in names, phrases and descriptions. System discovery and search have a different exposure surface from the app's authenticated detail view.

Choose stable IDs that the backend can resolve safely. An entity object or indexed identifier is a pointer to revalidate, not a capability granting permanent access. If the app already has an intent used by saved shortcuts, preserve the old contract during a compatible staged migration rather than replacing required parameters silently.

## Acceptance matrix

| Fixture | Observe |
| --- | --- |
| Account signs out after suggestions were indexed | No unauthorized result/action from old metadata |
| User loses access to a shared item | Query/perform rechecks current access |
| Schema macro unavailable in selected SDK | Baseline supported intent path remains usable |
| Existing shortcut payload uses an old parameter | Intent remains compatible or provides intentional migration |
| Onscreen entity differs from selected context | Only the actually represented entity is exposed |

Treat current platform schema examples as evidence to inspect, not instructions to adopt every domain or raise deployment targets.

## Platform and verification boundary

The contextual-cues article’s metadata lists iOS/iPadOS 18.2, macOS 15.2 and Xcode 16.2 introductions for that article/sample scope. The schema overview has no platform-introduction metadata. Check each selected API, runtime capability and current official feature availability independently.

## Primary evidence

- `src_backend_apple_009` — [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- `src_backend_apple_031` — [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- `src_backend_apple_032` — [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
