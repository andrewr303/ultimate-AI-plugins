# Make purpose strings and privacy explanations match the feature

## Ask for a resource because the feature needs it

Inventory protected-resource use across first-party code and dependencies. Map camera, microphone, photos, location, contacts, health and notification-related interactions to the actual user task. Different APIs have different permission semantics; do not construct one generic “all permissions accepted” gate. Use a supported picker or narrower access path when it fulfills the feature without unnecessary collection.

Apple's purpose-string guidance asks for a concrete explanation of the app's use, not a restatement of the resource name or a vague promise of a better experience. Supply an honest, specific sentence for each requested protected resource and verify localizations in the system UI. Do not add a fabricated rationale simply because an SDK references an API the product does not need.

## Inputs and preparation

Read the chosen targets' Info.plist settings and localized usage strings, the API call sites, SDK resource requests and the product's user-facing explanation. Compare those with actual collection, retention and sharing. For policy text, obtain real owner facts rather than inventing data practices or legal commitments. Keep a missing product decision distinct from a missing localization or malformed resource key.

## Implementation and verification sequence

1. Identify when and why each permission request occurs. Prefer a relevant feature context over indiscriminate first-launch prompts.
2. Write the smallest truthful purpose explanation and include the required target resources.
3. Exercise fresh-install authorization, denial, restriction, revocation and unavailable hardware/OS paths.
4. Confirm the app still offers the appropriate fallback when a resource is not necessary to its core task. Do not force unrelated access as the price of using another feature.
5. Test the supported languages and the specific permission dialog on a real target where required.
6. Reconcile the app's settings, policy, store answers and actual backend behavior after changes.

For notifications, authorization for user-visible alerts/sounds/badges is not the same as every remote-registration or silent/background operation. Check the API used and current documentation. Repeated authorization calls after denial do not reliably present a new prompt. Provisional notification authorization has its own delivery behavior and is not full alert permission.

For HealthKit, read denial intentionally resembles no data to avoid leaking the user's choice. Do not diagnose an empty read as an explicit denial. Check required health usage descriptions and the actual data types separately, and test when locked-device protection makes data unavailable.

## Four outcomes and evidence

Mark a demonstrated mismatch between requested resource and described feature as a blocker. An unconfirmed SDK request or collection purpose is unknown; do not fill it with boilerplate. A genuinely unused resource is not applicable to that build once its invocation/reference and packaging are verified. Satisfied evidence identifies the specific prompt, localization and denial/fallback behavior tested.

Useful fixtures include a microphone request on a photo-only task, an SDK-triggered location request, a non-English system dialog, a notification request after the first reminder is created and a denied-permission return to settings. A static plist parse is supporting evidence; it does not verify what the dialog says, when it appears, or whether the feature respects the result.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_purpose_strings` — [5.1.1(ii) - Write clear purpose strings - Guideline reference - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/guideline-reference/5-1-1-purpose-strings)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_notification_permission` — [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- `src_policy_health_privacy` — [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
