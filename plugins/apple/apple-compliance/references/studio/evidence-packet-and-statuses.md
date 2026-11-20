# Evidence packet and unknown-preserving readiness

Apply the [operating contract](../operating-contract.md). Use the app’s actual facts, selected lane and current authoritative sources.

## What the helper actually evaluates

The bundled scripts/readiness.py evaluates an owner-supplied evidence packet. It does not authenticate the truth or content of evidence references, contact Apple, sign an app, inspect every API or make declarations. A ready result means only that the declared supported profile/stage has no recorded missing, blocked or unknown checks. Treat it as a disciplined handoff, not a compliance certificate.

Use schema_version integer 1, a scope object and checks list. Scope names bundle_id, platform, channel, storefronts and requested_stage. Supported channels are app_store and macOS developer_id; unsupported distribution lanes require a separate manual profile. Storefront code shape is structural validation, not proof that an app or agreement is eligible there.

## Preserve four check states

| Packet status | Meaning and evidence requirement |
| --- | --- |
| satisfied | A concrete observed artifact/test/source/product fact supports this check; supply evidence references |
| blocked | A demonstrated issue prevents the requested dependent action |
| unknown | The necessary fact or verification is not available yet; name the evidence owner outside the packet |
| not_applicable | Give a bounded reason and supporting references for this selected scope; never use it to hide missing facts |

The helper refuses not_applicable for core checks. Even an offline app needs an evidenced data map and product-flow review; a finding of no relevant collection is an observed conclusion, not a reason to omit review. Extra declared blocked or unknown checks also keep the report from ready. Do not remove a valid concern merely to obtain a green result.

## Profile and stage dependencies

Every profile requires policy_scope, artifact_identity, signing, privacy_data_map, data_declarations and product_flows. App Store adds metadata_assets, review_access, account_lifecycle, commerce, content_age_rights, export_compliance and backend_access. Developer ID adds hardened_runtime and notarization_plan instead of those store checks.

App Store submit/release also require build_processed and submission_items_ready. App Store release additionally needs review_approved and release_scope. Developer ID release needs notary_accepted, ticket_verified and release_scope. These are helper dependencies, not a complete universal statement of Apple requirements; evaluate actual app facts and current rules separately.

## Run and interpret

Use `python3 scripts/readiness.py --evidence /path/packet.json` from the plugin root, optionally adding `--artifact /path/to/App.app` or a real archive directory. The artifact scanner observes bounded Info.plist/privacy-file metadata; direct IPA extraction is outside this command. Observed app-identifier contradiction blocks the packet, while absent interpretable identity remains unknown. Matching identity does not validate signing or the App Store record.

The report omits evidence-reference contents and reports counts/IDs/statuses. Exit 0 means ready for the requested profile/stage, 1 means blocked or needs evidence, and 2 means invalid input. Keep protected references in the packet's controlled storage; a syntactically valid reference may still be stale, inaccessible or false.

## Verification and handoff

Review each asserted fact against its real owner/source and artifact revision. Test missing evidence, wrong identity, unknown checks and unsupported profiles rather than only a fabricated all-satisfied packet. Record source freshness, real native tests, exact stage and remaining facts alongside the structural report. A green JSON result must never be used to invent approval, consent or truthful policy answers.

## Sources and checked scope

- [src_policy_complete_review](https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review)
- [src_policy_app_privacy_details](https://developer.apple.com/app-store/app-privacy-details/)
- [src_policy_adding_manifest](https://developer.apple.com/tutorials/data/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk.json)
- [src_delivery_choose_build](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit/)

The [source index](../../research/sources/sources.jsonl) records identity and observation scope. These are original workflow notes, not a full policy mirror or a legal/approval certification. Refresh material applicability before the requested external action.

Helper behavior is defined by the local [readiness implementation](../../scripts/readiness.py); its structural assertions and artifact observations do not authenticate product facts.
