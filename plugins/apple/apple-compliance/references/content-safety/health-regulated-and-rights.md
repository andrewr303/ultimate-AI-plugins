# Prepare genuine health, regulated-service and content-rights evidence

## Separate implementation from authority to offer the service

Identify the actual claims the app makes, the service provider, supported jurisdictions and the data used. A HealthKit integration does not establish medical efficacy, regulatory clearance or authorization to provide healthcare. A payment or location SDK does not establish a gambling, financial, travel or other regulated-service license. Determine which specific review/documentation lane applies to the real product.

Apple's complete-review guidance calls for relevant documentation in regulated fields and evidence of rights for protected content. Use the publisher's actual documents and confirmations. Do not invent a regulatory identifier, rights license, institutional approval or “compliant” medical claim to complete a submission checklist.

## Health data boundary

Map requested HealthKit data types, permissions, actual uses, downstream recipients and storage. Apple describes fine-grained authorization and explains that a denied read can look like no data to protect privacy. Do not infer the user's permission choice from an empty result or request unrelated types to discover it.

Check required usage descriptions and the app's clear health/fitness purpose. The reviewed health guidance restricts health-derived advertising, selling and sharing; general consent is not a universal exception to every restriction. The App Review health section also describes research-consent/ethics evidence and limits on personal health information in iCloud. Classify the actual data and use rather than asserting that all fitness content has the same legal status.

## Review preparation workflow

1. Inventory diagnostic, treatment, financial, gambling, research or other material claims in the app and metadata.
2. Resolve the actual entity providing the service and the storefronts where it is offered.
3. Identify the current source section and document type relevant to each claim/jurisdiction. Ask for a specific missing fact, not an open-ended assurance that the business is compliant.
4. Verify the release behavior against the claims, including limited/denied permissions and unavailable/locked data.
5. Prepare representative synthetic review access and attach actual sensitive documents only through the appropriate protected review channel.
6. Reconcile content licenses, provider partnerships, privacy statements and marketing text with the same product/version.

For human-subject research, do not equate a system permission prompt with research consent or independent ethics review. For third-party media, public availability and a successful download do not establish a license to redistribute or enable downloads. A source repository's code license does not automatically license its example photos, logos or external content.

## Failure cases

Test unsupported claims left in store text, a denied HealthKit type, background reads while protected data is unavailable, a real provider document missing for one region, an expired partnership and media accessible through a service without a redistribution right. Use safe synthetic records, not actual patient/customer data, in screenshots and ordinary logs.

A demonstrated prohibited use or a required missing document is a concrete blocker for that lane. Unresolved qualification, legal scope or rights facts are unknown; avoid both a fabricated pass and an unsupported legal accusation. Not applicable needs an explanation grounded in the actual features and claims. Satisfied evidence names what was reviewed and remains separate from regulatory or App Store acceptance.

## Handoff

Deliver a claim-to-evidence matrix, implementation/privacy findings, owner-confirmed documents and precise pending items. Continue authorized technical fixes while the right owner supplies missing facts. Preparing or reviewing this evidence does not authorize sending a regulator appeal, accepting terms, uploading private documents or submitting the app; execute the actual requested external stage only within the established scope.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_health_privacy` — [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_complete_review` — [Provide information for a complete review - Before submitting for review - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
