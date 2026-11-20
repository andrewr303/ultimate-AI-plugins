# Asset Library and screenshot matrix

Read the [operating contract](../operating-contract.md). Prepare accurate image/video assets using the current Apple matrix for the actual supported app.

## Establish the inputs

- App platform, supported devices and SDK of the intended build.
- Current Apple display/asset requirements and observation date.
- Locale, orientation, appearance and app state represented.
- Source captures, file hashes/types/dimensions and transparency.
- Remote asset processing/review/attachment state.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Discover current required device/display sets, platform, localization and app SDK; capture an as-of requirement matrix rather than embedding permanent device dimensions.
2. Use representative app states with synthetic or approved data. Check file type, dimensions, alpha/transparency, orientation, text legibility and localization before upload.
3. Track upload, processing, asset review, attachment and reuse as distinct states. Preserve an asset-to-source-capture mapping and inspect the remote attachment.

### Build a current matrix, not a permanent device table

Resolve the app's actual platform, supported device families, SDK and intended storefront presentation. Read current Apple screenshot and preview requirements for that scope. A source may announce a device or SDK requirement with a future start date; do not silently apply it to every current release. Record which matrix was used and when it was checked.

Use representative captures from the relevant app build and supported states. Synthetic or approved demo data protects user information, but it must not depict features that do not exist. Check crop, orientation, locale, legibility, file type, dimensions and alpha/transparency against the current asset specification. Pixel validity alone does not establish truthful marketing.

### Track assets through their own lifecycle

Current App Store Connect guidance uses Asset Library for images/videos, including screenshots, previews and reusable creative assets. Upload, processing, review/approval, attachment and reuse are separate observations. A successfully uploaded image may be unapproved or attached to the wrong locale or platform. Preserve an asset-to-capture mapping so a reviewer can trace a published image back to the source state.

Before replacing or archiving assets, inspect the current selected set and affected placements. Avoid deleting useful approved assets as cleanup. After an authorized change, read back the association/order and preserve any remaining processing or review state as a named dependency.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| HTTP200 not-found documentation rejected as evidence | Reject the page as a source, retain the failed attempt as context, and locate the correct current official page. |
| Future device screenshot requirement treated as currently active | Keep the future requirement in the watch list and apply the currently effective matrix to this release. |
| Approved asset accidentally attached to wrong localization | Correct the scoped relationship after inspecting current state; do not reupload or delete the entire library blindly. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Time-scoped requirement matrix with source URLs.
- Capture/build/locale mapping and local file validation.
- Remote asset identifiers, state, order and target association.
- Actual gaps in truthful content or supported display coverage.

Do not fabricate screenshots of unavailable features; a valid image file does not establish accurate App Store marketing. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_screenshots` — [Manage your App Store assets - Manage app information - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-your-app-store-assets/).
- `src_delivery_screenshot_specs` — [Screenshot specifications - App information - Reference - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/).
- `src_delivery_fastlane_deliver` — [deliver - fastlane docs](https://docs.fastlane.tools/actions/deliver/).
