# Store localization and metadata inventory

Read the [operating contract](../operating-contract.md). Keep store copy, app-binary localization and per-platform version metadata aligned without conflating them.

## Establish the inputs

- Primary locale and existing per-locale store metadata.
- App-info versus platform-version fields and editability state.
- Binary localizations and their relationship to store claims.
- Local canonical metadata layout and remote identifiers.
- Requested additions, edits and deletions.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inventory the primary locale, existing localized app-info/version fields and platform-specific content; preserve existing text and identify missing product facts.
2. Preview a local-to-remote diff including deletions and fallback locales. Review factual claims, support/privacy URLs, content rights and actual feature availability.
3. Apply only authorized metadata changes in an editable remote state, then read back the affected fields.

### Keep binary and store localization separate

App Store localizations affect listing names, descriptions, keywords and other store fields. Xcode localization affects the app people run. Inventory both and ensure the listing truthfully describes the actual supported experience. Do not infer that adding a store locale translated the app, or that a localized app binary automatically populated every store field.

Read current platform/app shared-field relationships before bulk editing. Some values belong to app information, others to a selected platform version or asset. A locale may have fallback behavior from the primary language, and adding it can affect shared metadata across platforms. Keep those relationships visible in a preview instead of flattening everything into one untyped folder diff.

### Preview destructive and locked-state changes

Produce a local-to-remote plan with each changed field, locale and target. Explicitly identify deletes and fallback changes. Absence from a local directory is not by itself authority to erase a remote localization. Preserve existing content and resolve missing product facts rather than filling a field with invented claims.

Inspect current remote editability before applying a plan. A submitted version can lock fields that were editable during preparation. On a partial failure, read back the fields that may have changed, then resume only missing authorized work. Keep source content, intended diff and observed remote result distinguishable in the handoff.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| A locale omitted locally must not be silently deleted | Show the deletion separately and preserve the remote locale until matching intent is established. |
| App Store locale present but app binary remains untranslated | Record the mismatch and correct the relevant listing/app work within scope; do not claim a fully localized experience. |
| Fields locked after submission | Stop the locked mutation and select a supported correction lane from the observed status. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Locale/platform inventory and primary-language assumptions.
- Reviewed field-level plan including deletes.
- Exact fields applied and read-back values.
- Unresolved copy, rights or product-fact owner.

Do not invent translations, rights claims, privacy answers or unsupported features merely to fill a required field. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_localization` — [Localize app information - Manage app information - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-app-information/localize-app-information/).
- `src_delivery_fastlane_deliver` — [deliver - fastlane docs](https://docs.fastlane.tools/actions/deliver/).
