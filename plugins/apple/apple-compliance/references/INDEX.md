# Reference library

Choose the specialist that owns the task, then read the focused cards below. Each card records inputs, decisions, implementation/recovery steps, verification and source citations. Check current applicability using the [operating contract](operating-contract.md) and [source index](source-index.md).

## Skill entrypoints

- [app-store-readiness](../skills/app-store-readiness/SKILL.md): Use for a concrete App Store readiness assessment, evidence packet, account/capability check, or changing upload-rule review. Do not treat an audit as approval or infer upload, submission, invitations or release from preparation.
- [apple-compliance](../skills/apple-compliance/SKILL.md): Use for end-to-end Apple app compliance preparation, unfamiliar review/distribution scope, or choosing the correct privacy, commerce, content, signing, submission or Mac specialist. Keep actual evidence and requested stage explicit. Do not certify legal compliance, invent declarations, or infer publication authority from preparation.
- [compliance-discovery](../skills/compliance-discovery/SKILL.md): Use when inventorying the actual Apple app artifact, SDK/data/features, review access, platform/storefront or distribution lane before classification. Route concrete policy/privacy/signing defects to the relevant specialist. A file scan or matched identifier does not establish truthful declarations, eligibility or approval.
- [compliance-policy-watch](../skills/compliance-policy-watch/SKILL.md): Use when verifying a material Apple policy/source, reviewing changed requirements, or distinguishing current and future effective dates for the selected app/lane. Do not create unrequested monitoring, generalize regional exceptions, treat website success as valid content, or replace owner product/legal facts with guesses.
- [compliance-security](../skills/compliance-security/SKILL.md): Review security-relevant Apple submission evidence: account/data authorization, encryption/export determinations, artifact identity/signatures, SDK origin and Mac distribution boundaries. Do not invent exemptions, rotate credentials, mutate team assets or call a signature/notary ticket App Store approval.
- [mac-distribution](../skills/mac-distribution/SKILL.md): Use for Mac App Store versus Developer ID distribution, Hardened Runtime/App Sandbox, notarization diagnostics and stapling. Do not treat a notary ticket as App Store approval, copy Electron entitlements into unrelated apps, or generalize this lane to iOS review.
- [privacy-labels-att](../skills/privacy-labels-att/SKILL.md): Review Apple privacy labels, tracking/ATT, purpose strings and consent/data-use consistency using actual app and SDK behavior. Do not equate every analytics event with tracking or automatically answer data declarations from an SDK name, empty manifest or source search.
- [privacy-manifests](../skills/privacy-manifests/SKILL.md): Review and repair Apple privacy-manifest structure, target/package resource placement, required-reason API ownership and SDK manifest/signature evidence. Use for PrivacyInfo.xcprivacy and archive privacy findings; do not infer privacy labels or legal facts from a valid plist.
- [review-account-auth](../skills/review-account-auth/SKILL.md): Review Apple login-service applicability, identity/session boundaries, in-app account deletion and representative App Review access. Use for account/reviewer-flow issues; do not impose a login provider on every app or treat account deletion as automatic Apple subscription cancellation.
- [review-content-safety](../skills/review-content-safety/SKILL.md): Review Apple user-generated/AI content safeguards, age/Kids Category boundaries, health/regulated-service claims and protected-content evidence. Do not fabricate licenses, consent or ratings, and do not claim that a report button or SDK alone makes a product eligible.
- [review-digital-goods](../skills/review-digital-goods/SKILL.md): Classify Apple digital goods, purchase/restore/subscription behavior, paywall terms and storefront-specific external-offer eligibility. Do not treat a shared web backend as a universal iOS billing exception or accept agreements, change prices or submit purchases from a prepare-only task.
- [review-platform-extensions](../skills/review-platform-extensions/SKILL.md): Review Apple widgets, App Clips, Siri/App Intents, notifications and background features as product, privacy and authorization surfaces. Do not expose sensitive locked-device actions by relying on default intent policy or promise guaranteed background scheduling from a static check.
- [review-rejections](../skills/review-rejections/SKILL.md): Use for a specific App Review/TestFlight rejection, reproduction, repair plan, response draft or authorized resubmission. Do not send messages, appeal, cancel review or promise acceptance merely because a reference describes those actions.
- [review-submission-release](../skills/review-submission-release/SKILL.md): Use for staging review items, actual App Review submission, release policy/availability and recovery after partial completion. Keep preparation, submission, approval and public release distinct; do not duplicate live submissions or change pricing/territories without matching scope.
- [signing-entitlements](../skills/signing-entitlements/SKILL.md): Use for Apple signing identity/profile/entitlement mismatches, exported-artifact verification and controlled CI signing. Do not revoke shared assets, rotate credentials, broaden capabilities or change distribution channels as routine cleanup.
- [store-metadata-assets](../skills/store-metadata-assets/SKILL.md): Use for App Store listing metadata/localizations, Asset Library images/videos, screenshot matrices and review-access information. Keep binary localization and app implementation separate; do not fabricate product declarations or publish from a draft request.
- [testflight-builds](../skills/testflight-builds/SKILL.md): Use for iOS/macOS build upload receipts, Apple processing, TestFlight eligibility/groups and beta feedback. Do not infer tester invitations, notification, production review or public release from an upload-only request.

## Focused guides

### Account Auth

- [Delete accounts and data without confusing billing cancellation](account-auth/deletion-data-and-subscriptions.md)
- [Apply the login-service rule to the real account model](account-auth/equivalent-login-and-sessions.md)
- [Give reviewers representative access with protected test identities](account-auth/review-access-and-identity-evidence.md)

### Content Safety

- [Separate age ratings, Kids Category and parental-consent facts](content-safety/children-age-and-parental-boundaries.md)
- [Prepare genuine health, regulated-service and content-rights evidence](content-safety/health-regulated-and-rights.md)
- [Make content safeguards operational for UGC and generated content](content-safety/ugc-and-ai-moderation.md)

### Digital Goods

- [Present subscription terms and regional lanes truthfully](digital-goods/paywalls-subscriptions-and-regional-gates.md)
- [Classify products before choosing the payment route](digital-goods/product-and-storefront-classification.md)
- [Verify purchase, restore and shared entitlement behavior](digital-goods/purchase-restoration-and-entitlements.md)

### Discovery

- [Artifact inventory and identity reconciliation](discovery/artifact-inventory-and-identity.md)
- [Data, feature and review-access map](discovery/data-and-feature-map.md)
- [Distribution scope, storefronts and eligibility](discovery/distribution-scope-and-eligibility.md)

### Mac Distribution

- [Choose the Mac App Store or direct distribution lane](mac-distribution/choose-distribution-lane.md)
- [Notary submission, wait and diagnostics](mac-distribution/notary-submit-and-diagnostics.md)
- [Staple and verify the actual final distribution artifact](mac-distribution/staple-verify-final-artifact.md)

### Metadata Assets

- [Asset Library and screenshot matrix](metadata-assets/asset-library-and-matrix.md)
- [Store localization and metadata inventory](metadata-assets/localization-inventory.md)
- [Review access and declaration completeness](metadata-assets/review-access-and-declarations.md)

### Platform Extensions

- [Separate notification consent, background work and review behavior](platform-extensions/notifications-background-and-review.md)
- [Verify Siri and App Intent actions at the authentication boundary](platform-extensions/siri-intents-and-locked-device.md)
- [Review widgets, App Clips and shared data as separate surfaces](platform-extensions/widgets-clips-and-shared-data.md)

### Policy Watch

- [Observed dates, effective dates and future requirements](policy-watch/observed-and-effective-dates.md)
- [Policy change review and evidence refresh](policy-watch/policy-change-review-and-refresh.md)
- [Source identity and applicability](policy-watch/source-identity-and-applicability.md)

### Privacy Labels Att

- [Reconcile real data flows with privacy labels](privacy-labels-att/data-flows-and-labels.md)
- [Make purpose strings and privacy explanations match the feature](privacy-labels-att/purpose-consent-and-policy.md)
- [Connect tracking behavior, ATT and declared domains](privacy-labels-att/tracking-att-and-domains.md)

### Privacy Manifests

- [Use archive reports and repair invalid manifests deliberately](privacy-manifests/archive-report-and-repair.md)
- [Inventory and place privacy resources per product](privacy-manifests/inventory-and-placement.md)
- [Match required-reason API use to the owning bundle](privacy-manifests/required-reasons-and-sdk-boundaries.md)

### Readiness

- [Account, app and capability map](readiness/account-and-capability-map.md)
- [Readiness evidence packet](readiness/evidence-packet.md)
- [Tool and rule refresh](readiness/tool-and-rule-refresh.md)

### Rejections

- [Classify and reproduce a review issue](rejections/classify-and-reproduce.md)
- [Draft a clear response and supporting evidence](rejections/reply-evidence-and-appeal.md)
- [Resubmit without losing the original evidence trail](rejections/resubmission-and-regression.md)

### Security

- [Separate code origin, signed artifacts and distribution approval](security/artifact-signatures-and-sdk-origin.md)
- [Review data security at real app and service boundaries](security/data-security-and-authorization.md)
- [Determine encryption/export declarations from product facts](security/encryption-and-owner-declarations.md)

### Signing Entitlements

- [Verify the signed artifact and extension capabilities](signing-entitlements/artifact-entitlement-verification.md)
- [Ephemeral CI signing and secret containment](signing-entitlements/ephemeral-ci-signing.md)
- [Signing identity and provisioning map](signing-entitlements/signing-identity-and-profiles.md)

### Studio

- [Applicability and specialist routing](studio/applicability-and-specialist-router.md)
- [Evidence packet and unknown-preserving readiness](studio/evidence-packet-and-statuses.md)
- [Submission handoff and authorized state transitions](studio/submission-handoff-and-authorization.md)

### Submission Release

- [Recover after partial mutation or timeout](submission-release/recovery-and-checkpoints.md)
- [Approval, release and territorial availability](submission-release/release-and-availability.md)
- [Submission state machine and multi-item review](submission-release/submission-state-machine.md)

### Testflight Builds

- [Beta feedback, crashes and build lifetime](testflight-builds/beta-feedback-and-build-lifetime.md)
- [TestFlight groups, invitations and beta review](testflight-builds/beta-groups-and-scope.md)
- [Build upload, receipts and processing](testflight-builds/build-upload-receipts.md)

## Provenance and evidence

- [Source and claim records](../research/outputs/design-decision.md)
- [Validation](../docs/validation.md)
- [Native host evidence](../docs/native-host-verification.json)
