# Apple Compliance: manually supported design decision

Build an independent private plugin that prepares Apple-platform apps for the correct review/distribution lane and helps carry authorized submission work through verified states. It includes substantial original references grounded in reviewed primary policy/docs and pinned implementation evidence, source freshness and applicability, unknown-preserving readiness helpers, safe artifact metadata inspection and native host packaging.

The optional local research accelerator is absent. Manual source-evidence review was performed; no automated research PASS or verified_claims.json is asserted. Apple primary policy observations are not mislabeled as independent legal corroboration. Multiple Apple pages and Apple repository code remain one underlying author.

## Manually supported design observations

- **clm_comp_delivery_states**: The inspected Apple, Expo and release-tool sources treat build upload, processing, review submission and public release as separate workflow concerns. Sources: src_delivery_upload_builds, src_delivery_submit_review, src_delivery_release_options, src_delivery_eas_submit_ios, src_comp_delivery_code_004.
- **clm_comp_delivery_recovery**: The inspected release implementations re-resolve target identity and current submission state rather than treating a local checkpoint or retry as proof of completion. Sources: src_comp_delivery_code_012, src_comp_delivery_code_004.
- **clm_comp_delivery_auth**: Apple administration tooling distinguishes credential roles and operation-specific capabilities, so a workflow needs a resolved account and authorization lane. Sources: src_delivery_asc_roles, src_delivery_api_token, src_delivery_fastlane_api, src_comp_delivery_code_039.
- **clm_comp_delivery_mac**: The inspected macOS sources separate direct distribution signing, notarization and ticket stapling from App Store review. Sources: src_delivery_developer_id, src_delivery_notarization, src_delivery_notary_custom, src_comp_delivery_code_059.
- **clm_comp_delivery_metadata**: The inspected metadata sources manage localizations and store assets separately from the compiled application binary. Sources: src_delivery_localization, src_delivery_screenshots, src_delivery_fastlane_deliver.
- **clm_comp_delivery_purchases**: The inspected commerce sources require a purchase-verification and launch-test workflow beyond installing a client SDK. Sources: src_comp_delivery_code_046, src_delivery_revenuecat_launch.

## Original implementation decisions

| Requirement | Source evidence surface | Gap | Notice decision | Original design |
| --- | --- | --- | --- | --- |
| Preparation through release | Pinned Fastlane/ASC/EAS implementations and Apple workflow docs | Upload, processing, stage, submit, approval and release differ | Original workflows; no release-tool implementation vendored | One evidence packet and explicit requested endpoint; clm_comp_delivery_states, clm_comp_delivery_recovery |
| Policy/privacy/auth/commerce classification | Identity-checked Apple review, privacy, SDK, account and StoreKit primary pages | Rule depends on app facts, platform, storefront, agreement and effective date | Original summaries with source citations; no full policy mirror | Dedicated specialists, actual product facts and explicit unknowns; do not infer declarations or universal checkout exceptions |
| Metadata/assets | Apple Help and Fastlane delivery docs | Store content differs from binary localization and assets have state | Original checklists and evidence templates | Source-cited reviewable asset/localization workflow; clm_comp_delivery_metadata |
| Signing and account capabilities | Current Apple roles/API and tool-specific credential docs | Signing identity, team role, profile and private key differ | Source-only ideas | Resolve exact target/account/auth lane and preserve team assets; clm_comp_delivery_auth |
| macOS distribution | Apple Developer ID/notary docs and Electron implementation | Notarization and App Store review are different processes | No tool/runtime source vendored | Separate direct distribution, sandbox/review and ticket evidence; clm_comp_delivery_mac |
| Digital goods testing | Apple signed-data implementation and independent launch checks | An installed SDK cannot establish entitlement/business readiness | Original scope/verification workflow | Product/storefront/restore/server checks tied to current agreement; clm_comp_delivery_purchases |

## Acceptance and manual checklist

The plugin must contain focused skills and a substantial reference library, a current source index with identity/observation metadata, a readiness tool that separates pass/blocker/unknown/not-applicable, safe artifact inspection, meaningful failure-case tests, portable/Codex/Claude/current Kimi metadata and available native-host discovery evidence. No actual submission, certificate mutation, legal assent, purchase, paid service or production deployment is requested by this creation task.

Registered IDs and independent author identities were checked for each narrow supported design claim. Exact source-level finalist matrices and policy research are retained as companion reports. Source code/tests were inspected without running upstream code. Single-primary policy statements are scoped observations requiring live contextual verification; dates, rights and fee/region details are not promoted as blanket independently corroborated legal conclusions. Local executable claims will be added only after real tests.

## Unresolved

Actual app data collection, required-reason API use, consent, content rights, age classification, account deletion behavior, commerce eligibility, publisher agreements, storefronts, signing and remote review state remain product-specific. Forward-dated requirements are not current defaults. Static inspection cannot establish security, legal compliance or App Store approval. Xcode/device behavior, authenticated Apple operations and model-driven skill behavior need the target environment. Source main/tool versions and mixed license surfaces must be checked before adoption.

## Refuted

Rejected inference patterns: a file/scan passing certifies an app; one regional commerce exception applies globally; an upload is a review submission; a notary ticket is App Store approval; a signed client payload eliminates server authorization; source instructions grant authority to publish or supply factual/legal answers for the user.
