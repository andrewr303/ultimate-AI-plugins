# Data, feature and review-access map

Apply the [operating contract](../operating-contract.md). Use the app’s actual facts, selected lane and current authoritative sources.

## Start from behavior rather than declarations

Map the app's actual user tasks, protected resources, account lifecycle, purchases, content and system surfaces. Include widgets, Siri/App Intents, notifications, extensions, web-linked flows and the shared backend. Inventory direct/transitive SDK behavior as well as first-party code. An SDK name, empty privacy manifest or lack of an obvious analytics package does not establish what data is collected or shared.

For each feature, record inputs, on-device processing, network destinations, backend/provider processing, storage/retention, user linkage, purposes, tracking decision and deletion behavior with its owner/evidence. Synthetic runtime observations can reveal a missing flow; source/vendor documentation can explain behavior; neither alone proves all production configurations. Preserve uncertainties and avoid dumping private user payloads to make the map look complete.

## Keep related evidence surfaces separate

Privacy labels, privacy manifests, required-reason API use, SDK signature/origin, usage descriptions, ATT, privacy policy and real collection behavior answer related but different questions. One does not substitute for all others. Required-reason codes must describe actual covered API use; permission consent does not automatically authorize unrelated collection or fingerprinting.

Account deletion, data retention and subscription cancellation are distinct outcomes. Digital goods classification, external offers and storefront/program eligibility need current policy and product facts. A shared Node entitlement service can reduce cross-platform duplication, but it does not establish a universal exception to Apple billing rules.

## Build the map

1. List common user tasks and all roles/states, including signed out, new/returning account, expired purchase, denied permission and review account.
2. Trace each task through app/extension, SDK, backend and external provider. Record safe categories and purpose rather than copying live records or credentials.
3. Map every observed collection/access to responsible declaration/purpose/consent surfaces and evidence owners. Leave contradictory or missing facts unknown until resolved.
4. Add content/age/rights, moderation and child/regulated-category considerations when the actual product calls for them. Do not fabricate certificates, rights or legal assent.
5. Verify review access to representative tasks with synthetic data, usable credentials and required hardware/region instructions through the supported secure review fields.
6. Route concrete repairs to focused specialists and recheck affected declarations/artifacts after SDK or feature changes.

## Failure matrix

| Shortcut | Missing evidence |
| --- | --- |
| Empty manifest means no data collection | First-party/SDK/backend behavior and label interpretation |
| Data hashed, so automatically unlinked | Actual linkage/purpose/provider processing |
| ATT granted, so all practices permitted | Applicable collection, fingerprinting and consent boundaries |
| Login removed, so no account lifecycle | Backend account retention and supported deletion/exit paths |
| Web purchase works, so iOS is eligible | Product/storefront/agreement policy classification |
| Demo screenshot exists | A usable representative review experience and backend access |

## Verification and handoff

Provide a concise feature/data-flow map, owner/evidence per unresolved fact and the affected declaration/review surfaces. Test denied/expired states, account deletion, purchase/restore and review access as relevant on the actual target environment. Static inspection cannot certify complete collection, user consent, content rights or legal compliance. Continue independent technical checks while responsible owners supply genuinely missing facts.

## Sources and checked scope

- [src_policy_app_privacy_details](https://developer.apple.com/app-store/app-privacy-details/)
- [src_policy_user_privacy_data_use](https://developer.apple.com/app-store/user-privacy-and-data-use/)
- [src_policy_review_guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [src_policy_complete_review](https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review)

The [source index](../../research/sources/sources.jsonl) records identity and observation scope. These are original workflow notes, not a full policy mirror or a legal/approval certification. Refresh material applicability before the requested external action.
