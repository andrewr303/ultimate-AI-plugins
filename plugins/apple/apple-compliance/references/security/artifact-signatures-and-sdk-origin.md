# Separate code origin, signed artifacts and distribution approval

## Establish which artifact and channel are being checked

Resolve the app/platform/build, selected scheme/configuration, embedded products, distribution channel and signing arrangement. Mac App Store distribution, iOS App Store distribution, alternative distribution and Mac Developer ID notarization are different lanes. A valid signature establishes a bounded origin/integrity fact; it does not certify privacy declarations, commercial eligibility, legal compliance or App Review acceptance.

Inspect the actual archive rather than only a source entitlement file. Record the bundle identities and relevant resources for app and extensions. Keep signing/profile private material out of plugin packages, source control and shared diagnostic logs. A team/account name may be sufficient for evidence; a certificate alone, a cloud-managed signing arrangement and possession of a local exportable private key have different operational meanings.

## SDK origin and privacy resources

Apple's listed-SDK guidance addresses privacy manifests and signatures in specified submission/distribution circumstances. Identify the exact resolved dependency, whether it is binary or source distributed, its vendor and any repackaged listed components. An app can include a relevant SDK transitively even when it is absent from the top-level dependency file.

For a new binary SDK version, inspect signature continuity and the required privacy resources in the actual selected platform variant. A recognizable vendor signature does not tell you every field the SDK sends, and a manifest's presence does not prove its factual accuracy. Reconcile those facts through the separate privacy and behavior review.

## Workflow

1. Select the intended channel and identify its current signing, packaging and review requirements.
2. Verify artifact bundle/version/platform identities and embedded target consistency.
3. Inspect actual capabilities/resources and the origin evidence for relevant SDKs, using current tool help and documentation.
4. When a repair changes an archive or embedded resource, account for the signature impact and repeat the appropriate final signing/resource checks.
5. For Mac Developer ID notarization, verify the required signing and Hardened Runtime setup, submit only when authorized, inspect returned diagnostics and handle the ticket using supported tooling.
6. For Mac App Store distribution, apply its sandboxing, packaging, update and startup-consent requirements instead of transplanting an external updater/installer lane.

The reviewed notary documentation describes automated malware and code-signing checks and resulting tickets. It explicitly distinguishes direct-distribution notarization from Mac App Store security/review processing. Do not call a notarized binary App Store approved or add broad Hardened Runtime exceptions merely to suppress a diagnostic. Keep any necessary exception tied to the executable's real function and tested need.

## Meaningful evidence

Test a wrong bundle/version, missing embedded resource, stale SDK variant, unexpected signing origin and a signed artifact modified after inspection. Verify that a failed or unavailable validation step is not recorded as a clean result. Where the runtime supports it, inspect the actual tool result/log without exposing profiles, keys or customer data.

Use blocker for a demonstrated mismatch or failed required check, unknown for unavailable artifact/origin/native evidence, not applicable for a reason tied to the selected channel, and satisfied for the exact identity/resource/origin scope established. Source parsers and mocked diagnostics do not establish Gatekeeper behavior, device installation or Apple acceptance.

## Handoff and authority

Report artifact identity, selected lane, observed signing/resource results, repaired components and the next dependent step. Do not revoke shared certificates, replace team credentials, delete user data or upload a product just because a diagnostic guide suggests it. Carry existing authorization through the concrete operation, and ask only when the actual action or required owner fact is outside that scope.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_sdk_requirements` — [Third-party SDK requirements - Support - Apple Developer](https://developer.apple.com/support/third-party-SDK-requirements/)
- `src_policy_adding_manifest` — [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- `src_policy_beta_release` — [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- `src_policy_notarization` — [Notarizing macOS software before distribution](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
- `src_policy_hardened_runtime_current` — [Hardened Runtime](https://developer.apple.com/documentation/security/hardened-runtime)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
