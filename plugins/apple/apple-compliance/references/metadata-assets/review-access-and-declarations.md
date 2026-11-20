# Review access and declaration completeness

Read the [operating contract](../operating-contract.md). Make the reviewer able to exercise real features while protecting access details.

## Establish the inputs

- Selected build and reviewer-visible feature paths.
- Demo access/hardware/backend prerequisites.
- Actual data, content, encryption and commerce behavior.
- Current editable review-note/declaration fields.
- Owner and secure destination for sensitive review information.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Identify app review notes, demo-account/feature access, backend availability, hardware dependencies and content paths needed for the selected build.
2. Gather age/content, encryption and other declarations from observed implementation and authorized product facts; do not copy a sample false-valued encryption answer.
3. Keep sensitive demo credentials in the intended secure review channel, not Git, generic logs or the public listing. Re-test access with the exact release configuration.

### Make the submitted experience reachable

Exercise the app with the same release configuration intended for review. Identify sign-in, feature flags, subscription/account access, network dependencies, special hardware and content needed to reach meaningful functionality. A working development account is not proof that the reviewer can use the submitted app. Confirm that backend endpoints and demonstration data remain available for the planned review window.

Prepare short, factual reviewer steps that identify the relevant screen/action and expected result. Keep sensitive credentials in the intended secure review information channel rather than a public listing, repository or generic report. Do not create or transmit new accounts or messages unless that action is within the user's scope.

### Preserve factual uncertainty

Encryption, age/content, rights and similar declarations describe the actual product. Sample Boolean values in an automation guide are not facts about this app. Inspect implementation, bundled SDK behavior and the responsible owner's evidence. If a fact is genuinely missing, preserve it as unknown and keep independent technical preparation moving.

Bind any changed review note or declaration to the intended version/platform/build. An artifact change can invalidate an access instruction or feature description. A metadata-only correction may not require a new binary, but choose that lane from the actual review message and current state rather than assuming every rejection is metadata-only.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Demo account disabled after review notes were written | Mark reviewer access blocked and repair/test the intended demonstration path before relying on the notes. |
| Feature hidden behind undocumented hardware or account requirements | Document the real prerequisites and usable steps; do not hide the dependency or invent supported access. |
| Metadata-only rejection that does not need a new binary | Resolve the reported metadata issue and confirm the same build remains eligible for the chosen resubmission lane. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Tested reviewer path and release configuration.
- Prepared notes/attachments and their secure destination.
- Declaration facts with evidence/owner, including unknowns.
- Version/build binding and observed field editability.

Preparing review information is separate from transmitting messages or changing product/legal declarations. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_submit_review` — [Submit an app - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/).
- `src_delivery_review_messages` — [Reply to App Review messages - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/reply-to-app-review-messages/).
- `src_delivery_fastlane_deliver` — [deliver - fastlane docs](https://docs.fastlane.tools/actions/deliver/).
