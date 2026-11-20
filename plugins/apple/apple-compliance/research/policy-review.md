# Apple Compliance: primary policy research

## Scope and method

This is research only, not plugin implementation or legal clearance. The corpus contains **35 identity-checked Apple primary sources**, fetched and read in the task-relevant sections on **2026-10-26 UTC**. Exact URLs, observed titles, snapshot hashes, platform metadata where present, and review scope are in `reviewed-sources.jsonl`. Raw fetches stay in this scratch research area; do not ship complete Apple pages as plugin reference text. Use original focused synthesis and source links instead.

No upstream code, installer, model provider or account mutation was executed. Old/guessed URLs were not silently treated as sources: HTTP200 PageNotFound, empty page shells and topic-specific redirects are recorded in `retrieval-log.json`. The optional local research accelerator was not used. There is no automated factual PASS or verified_claims.json.

Apple is the authority for its own review rules. Multiple Apple pages are still one author organization, so these direct policy observations are not mislabeled as independent legal corroboration under the Research-first Creator checklist. Parent synthesis can combine independent repository/implementation evidence for workflow design; it must not turn a policy snapshot into a blanket legal or approval conclusion.

## Important design decisions

1. Use a tri-state evidence model: observed/satisfied, concrete blocker, unknown, and not-applicable; a file or scan passing cannot approve an app or infer product declarations.
2. Resolve platform, storefront, distribution channel, app/build/submission and requested endpoint before routing rules. Keep prepare, upload, stage, submit, approval and release distinct.
3. Link privacy labels, bundled manifests, approved reasons, SDK signatures, usage descriptions, account deletion and real data behavior without treating any one artifact as proof of all the others.
4. Treat commerce as product classification plus region/agreement eligibility. Shared backend entitlements can reduce cross-platform maintenance; one checkout provider cannot bypass Apple purchase rules.
5. Keep accessibility claims tied to real common-task evidence per device; retain exact voluntary/effective status from current sources.
6. Treat Siri, widgets, App Clips and notifications as product/privacy surfaces, including locked-device actions and separate executable resources.
7. Keep Apple Store review, iOS alternative-distribution notarization and macOS Developer ID notarization separate.
8. Keep precise source sections and dates in focused reference cards so rules can be refreshed without rewriting every workflow.

## Suggested source-backed reference cards

### Scope a compliance review before classifying rules

**Proposed reference:** `scope-and-evidence.md`

**Primary observation:** Apple review covers more than the main binary: app changes, metadata, purchases, events and other submission items can be evaluated. App Store review, alternative-distribution review and Mac Developer ID notarization are distinct lanes.

**Inputs:** App identity and publisher; Supported platforms and deployment targets; Storefronts/distribution channels; Selected build/version/submission IDs; Requested endpoint: diagnose, prepare, upload, submit, appeal or release.

**Workflow outline:**

1. Create an evidence inventory and identify the selected lane.
2. Record each finding as satisfied, blocked, unknown or not applicable with the evidence and owner.
3. Finish independent technical checks while missing product/legal facts are resolved.
4. Separate local structural checks, native tests, review submission and approval in the final report.

**Failure cases to cover:** A valid archive is reported as approved.; A US storefront exception is applied globally.; An uploaded build is confused with a submitted review item..

**Sources:** `src_policy_review_guidelines`, `src_policy_submitting`, `src_policy_app_review_overview`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Make the submitted experience reviewable

**Proposed reference:** `submission-completeness.md`

**Primary observation:** Guideline 2.1 asks for final, functional submissions; review requires working access to backend/account features and complete IAP information. A demo mode for security/legal restrictions has its own approval conditions.

**Inputs:** Release build and core task list; Backend availability and feature flags; Review account access; Review notes and required hardware/region conditions.

**Workflow outline:**

1. Run the actual supported-device and fresh-install tasks.
2. Remove placeholders and dead URLs; make paid features discoverable to review.
3. Verify review credentials remain usable and the backend stays available.
4. Describe significant changes, special setup, tested devices and region differences in review information.

**Failure cases to cover:** Expired OTP/demo account; Backend disabled outside developer office hours; Feature hidden by remote flag or unavailable test subscription; Hardware feature demonstrated only with an unrelated screen recording.

**Sources:** `src_policy_review_guidelines`, `src_policy_submitting`, `src_policy_complete_review`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Validate the artifact that is actually uploaded

**Proposed reference:** `archive-and-platform.md`

**Primary observation:** Xcode archives and distribution configuration identify the uploaded product. Privacy resources and SDK metadata need to exist in the built product, not merely in the source tree.

**Inputs:** Selected scheme/configuration; Archive and artifact bundle identifiers; Build/version/platform values; Embedded targets, SDKs and resources.

**Workflow outline:**

1. Archive the selected app and every affected extension.
2. Inspect resolved artifact identity and resource placement.
3. Use Xcode Validate App for preparation without claiming it submits the build.
4. Compare currently effective upload requirements with announced future deadlines.

**Failure cases to cover:** Simulator artifact supplied as device build; Wrong extension version or bundle ID; Manifest copied to source but absent from archive; Future SDK deadline treated as current deployment minimum.

**Sources:** `src_policy_beta_release`, `src_policy_submitting`, `src_policy_adding_manifest`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Supply review access without exposing production data

**Proposed reference:** `review-access.md`

**Primary observation:** Apple requests review instructions, usable demo accounts, external service information and regulated-field documentation. Sensitive or regulated apps may use a demonstration mode when appropriate and subject to the review guidance.

**Inputs:** Account roles and expired/active purchase states; Hardware integrations; Service availability; Region restrictions; Documentation ownership.

**Workflow outline:**

1. Prepare synthetic but representative review data and task instructions.
2. Provide the required account types, purchase states and additional authentication mechanism through the secure App Store Connect review fields.
3. Explain hardware, services and feature flags.
4. Keep demo secrets out of source control, plugin archives and ordinary research logs.

**Failure cases to cover:** Only admin flow can be reviewed; Credentials expire during queue time; Production customer data used as screenshot/demo content; A sample legal certificate is fabricated.

**Sources:** `src_policy_complete_review`, `src_policy_review_guidelines`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Reconcile data flows with Privacy Nutrition Labels

**Proposed reference:** `privacy-data-inventory.md`

**Primary observation:** The label includes relevant app and third-party collection, including data used only for app functionality. Apple defines collection and narrow optional-disclosure conditions; declarations must match actual behavior.

**Inputs:** Data-flow map by feature and SDK; Network destinations and retention; Purposes, identity linkage and tracking; Privacy policy and deletion behavior.

**Workflow outline:**

1. Inventory first-party and SDK data sent off device.
2. For each type record purpose, linkage, tracking and retention rather than inferring them from an SDK name.
3. Evaluate every optional-disclosure criterion when claiming an exception.
4. Reconcile source code, runtime observations, manifests, policy text and App Store Connect responses.

**Failure cases to cover:** Empty manifest is treated as proof no data is collected; Analytics is declared but functional account data omitted; Hashing or pseudonymization automatically marked unlinked; Optional one-time feedback exception applied to ongoing collection.

**Sources:** `src_policy_app_privacy_details`, `src_policy_user_privacy_data_use`, `src_policy_privacy_data`, `src_policy_review_guidelines`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Package valid privacy manifests per product

**Proposed reference:** `privacy-manifest-packaging.md`

**Primary observation:** PrivacyInfo.xcprivacy is a resource plist using documented keys/values. Xcode placement varies by product/platform; Swift packages need explicit resource handling. Invalid bundled manifests can block submission.

**Inputs:** All executable/framework/extension targets; Manifest source paths; Package resources; Archived bundle tree; Actual data/reason declarations.

**Workflow outline:**

1. Validate plist syntax and documented value types.
2. Verify each relevant target packages its manifest in the correct product location.
3. Inspect every platform variant of an XCFramework.
4. Generate and review the archive privacy report, then reconcile it with product facts.

**Failure cases to cover:** Valid source file omitted from Swift package resources; Manifest located only in top XCFramework wrapper; Unknown collected-data identifiers; Blindly deleting a required SDK manifest to remove a validation error.

**Sources:** `src_policy_privacy_manifest_current`, `src_policy_adding_manifest`, `src_policy_privacy_data`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Map covered APIs to accurate approved reasons

**Proposed reference:** `required-reason-api.md`

**Primary observation:** Required-reason API declarations belong to the bundle using the covered API, including a third-party SDK’s own use. Reasons must accurately match behavior; fingerprinting remains prohibited even after tracking consent.

**Inputs:** API usage by first-party code and each SDK; Current covered-category list; Current approved reasons; Affected executable/dynamic library bundles.

**Workflow outline:**

1. Find actual covered API calls and intended use.
2. Choose only documented reasons that accurately describe that use.
3. Keep SDK and app responsibilities separate; do not use the app manifest to substitute for missing SDK declarations.
4. Inspect the archived resources and test the feature against the stated purpose.

**Failure cases to cover:** Selecting any reason to silence upload feedback; Treating ATT permission as permission to fingerprint; One app manifest assumed to cover all linked SDKs; Static grep success claimed as complete semantic API audit.

**Sources:** `src_policy_privacy_required_reasons`, `src_policy_adding_manifest`, `src_policy_privacy_manifest_current`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Review listed SDK requirements and origin

**Proposed reference:** `sdk-supply-chain.md`

**Primary observation:** Apple’s listed commonly used SDKs require privacy manifests in specified submission circumstances, and binary dependencies have signature requirements. App developers remain responsible for included SDK behavior.

**Inputs:** Resolved direct/transitive dependencies; Binary vs source distribution; SDK versions and origin signatures; Built product SDK manifests; Vendor collection documentation.

**Workflow outline:**

1. Compare actual dependency inventory to the current Apple SDK list.
2. Verify required manifests and inspect signature continuity when adopting new binary SDK versions.
3. Use vendor updates and documented repair paths before mutating an archive.
4. Recheck the final Xcode report and labels after SDK changes.

**Failure cases to cover:** Transitive SDK ignored because not a direct package; Repackaged listed SDK assumed exempt; SDK signature treated as privacy/rights clearance; Known listed loader such as Kingfisher assumed irrelevant to compliance.

**Sources:** `src_policy_sdk_requirements`, `src_policy_adding_manifest`, `src_policy_app_privacy_details`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Make resource requests truthful and usable when denied

**Proposed reference:** `purpose-and-permission.md`

**Primary observation:** Purpose strings must explain the concrete feature use and be localized where supported. Permission requirements depend on the actual resource; denial should not trigger unrelated access demands.

**Inputs:** Protected API calls; Info.plist and localized usage text; Feature-level access purpose; Permission denied/restricted/unavailable paths.

**Workflow outline:**

1. Ask only when the feature needs the protected resource.
2. Write one specific use description for each actual resource.
3. Test the localized system prompt and denied/revoked paths.
4. Remove unnecessary protected API references instead of inventing a purpose to justify them.

**Failure cases to cover:** Generic benefit-only purpose text; Mic permission required merely to upload a photo; Repeated system prompts expected after denial; A third-party permission request ignored in app review.

**Sources:** `src_policy_purpose_strings`, `src_policy_review_guidelines`, `src_policy_notification_permission`, `src_policy_health_privacy`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Separate tracking, privacy disclosures and fingerprinting

**Proposed reference:** `tracking-and-att.md`

**Primary observation:** ATT concerns tracking across other companies’ properties and access to the advertising identifier, not every analytics event. Tracking permission, manifest domains, app labels and the actual SDK behavior must agree.

**Inputs:** Actual cross-company data linkage/sharing; Tracking domains; Authorization state; SDK configuration before/after consent; Relevant region/OS behavior.

**Workflow outline:**

1. Classify the real data use against Apple’s definition.
2. Request authorization with a truthful purpose when applicable.
3. Respect denied/restricted/not-determined states and test that tracking is not performed.
4. Treat announced region-specific prompts or reprompt rules as dated capabilities requiring SDK/live-policy verification.

**Failure cases to cover:** Payment/content gated on tracking consent; Fingerprinting used instead of an identifier; Vendor-domain name assumed to mean tracking; Future EU prompt behavior applied on unsupported OS versions.

**Sources:** `src_policy_user_privacy_data_use`, `src_policy_att`, `src_policy_privacy_manifest_current`, `src_policy_privacy_required_reasons`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Apply login-service rules to the actual account model

**Proposed reference:** `identity-and-login.md`

**Primary observation:** Guideline 4.8 describes a privacy-preserving equivalent login option for covered social/third-party primary account login, with listed exceptions. This is more precise than an unconditional instruction to add Apple login to every app.

**Inputs:** Primary account flow; Login providers and collected claims; Exception evidence; Token verification and revocation design; No-account access requirements.

**Workflow outline:**

1. Determine whether the covered login rule applies.
2. Document the equivalent option or exact applicable exception.
3. Implement identity verification and account linking against the actual service contracts.
4. Test private email, cancellation, existing accounts, revocation and deletion without logging credentials.

**Failure cases to cover:** Company-only enterprise login incorrectly forced into consumer flow; Demo sample password-display code copied into production; Two identities merged solely because an email matches; Login required for an app with no meaningful account-based feature.

**Sources:** `src_policy_review_guidelines`, `src_policy_siwa_implementation`, `src_policy_account_deletion`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Delete accounts without confusing subscription management

**Proposed reference:** `deletion-and-billing.md`

**Primary observation:** Apps supporting account creation must support in-app initiation of account deletion, including automatically created/guest accounts. Deactivation alone is insufficient; deletion and cancellation of an Apple-billed subscription are separate operations.

**Inputs:** Created/guest account types; Personal/UGC data graph; Legal retention facts; Sign in with Apple revocation; Subscription status and management path.

**Workflow outline:**

1. Provide an easy-to-find deletion entry with proportionate identity confirmation.
2. Delete associated personal/UGC data or disclose exact lawful retention determined by the product owner.
3. Explain duration and completion when deletion is asynchronous.
4. Explain continuing billing and provide the supported subscription management path without blocking deletion contrary to the applicable guidance.

**Failure cases to cover:** Support email required for an ordinary app; Only temporary deactivation offered; Guest accounts excluded; Account deletion reported as automatically cancelling Apple billing.

**Sources:** `src_policy_account_deletion`, `src_policy_review_guidelines`, `src_policy_subscriptions`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Classify what is sold before selecting a payment lane

**Proposed reference:** `purchase-classification.md`

**Primary observation:** Guidelines distinguish digital functionality, physical goods/services, enterprise services, one-to-one services, reader apps and narrow companion-app cases. Cross-platform access does not make a web checkout universally valid within iOS.

**Inputs:** Item/service consumed and where; Consumer vs organization sale; App/storefront/platform; Current exception/entitlement terms; Equivalent IAP availability where required.

**Workflow outline:**

1. Map each product to the current applicable rule and exception.
2. Select a supported storefront-aware purchase presentation.
3. Separate backend entitlement reconciliation from payment collection.
4. Record agreement and entitlement evidence before changing external purchase links.

**Failure cases to cover:** One global Stripe flow chosen for all digital products; Physical goods routed through IAP; Free companion exception applied despite in-app purchase calls to action; US exception treated as permission in every storefront.

**Sources:** `src_policy_review_guidelines`, `src_policy_storekit_selection`, `src_policy_reader_apps`, `src_policy_dma`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Present actual subscription terms clearly

**Proposed reference:** `paywall-and-product-metadata.md`

**Primary observation:** The purchase screen needs the subscription identity/duration, service, clear renewal price and an existing-customer restore/sign-in route; the amount actually billed must be prominent. Trial terms and post-trial price must be clear.

**Inputs:** Store-provided localized product data; Billing/commitment periods; Trial eligibility and transition; Terms/Privacy URLs; Current subscription state.

**Workflow outline:**

1. Render pricing from the actual StoreKit product rather than manually formatted assumptions.
2. Show the total billed amount more prominently than an equivalent monthly breakdown.
3. State trial duration, renewal amount and actual commitment terms.
4. Test purchase, existing subscriber, restore, pending, cancellation and error states.

**Failure cases to cover:** Annual bill hidden behind a monthly-equivalent headline; Trial advertised to ineligible customers; 12-month commitment described as freely cancellable monthly billing; Terms or privacy link missing or unrelated.

**Sources:** `src_policy_subscriptions`, `src_policy_review_guidelines`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Make entitlements survive lifecycle changes

**Proposed reference:** `subscription-lifecycle.md`

**Primary observation:** StoreKit API choice depends on deployment support; the current purchase/restoration article is a legacy SKPaymentQueue sample. Subscription status, renewal, restore and server events require deliberate reconciliation.

**Inputs:** Resolved StoreKit API and target OS; Subscription groups/levels; Server notification and status evidence; Entitlement state machine; Restore/manage UI.

**Workflow outline:**

1. Choose modern or legacy implementation according to actual supported targets.
2. Verify transactions and avoid granting duplicate entitlements from repeated events.
3. Test upgrade/downgrade, expired subscription, billing issue, refund/revocation and restored ownership.
4. Keep source-of-truth and customer-visible access consistent across supported devices.

**Failure cases to cover:** Legacy sample called StoreKit2; Finish/acknowledgment performed before durable fulfillment without recovery design; Duplicate subscriptions for the same benefit; Previously paid primary functionality removed during a subscription migration.

**Sources:** `src_policy_subscriptions`, `src_policy_storekit_selection`, `src_policy_storekit_purchase`, `src_policy_review_guidelines`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Keep regional eligibility and agreements explicit

**Proposed reference:** `regional-commerce.md`

**Primary observation:** Current primary pages have storefront-, platform-, age- and agreement-specific purchase rules. The EU support page describes recently effective unified terms; the Netherlands dating-app page and reader-app entitlement have narrower scopes.

**Inputs:** Storefront rather than only device language/IP; Platform/OS; Developer agreement/enrollment; Required approved entitlements; Age/parental-consent facts; Payment reporting/support obligations.

**Workflow outline:**

1. Build an eligibility matrix from current primary agreements and sources.
2. Keep fees, enrollment and legal acceptances as owner decisions, not automated defaults.
3. Gate the purchase experience using the supported storefront/capability APIs.
4. Test every supported lane and a denied/ineligible case before release.

**Failure cases to cover:** Old CTF/fee tables copied as current; Locale mistaken for storefront; Dating-app Netherlands entitlement used by another product; Read-only policy review silently accepts new business terms.

**Sources:** `src_policy_review_guidelines`, `src_policy_dma`, `src_policy_reader_apps`, `src_policy_external_link_entitlement`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Treat reader-app account links as a narrow lane

**Proposed reference:** `reader-app-entitlement.md`

**Primary observation:** Eligibility is based on primary reader content functionality, not merely the presence of video/audio. Account-link entitlement conditions and more recent US/EU exceptions must be read together for the selected storefront.

**Inputs:** Primary content type; Current IAP offering; Approved per-bundle entitlement; Destination domain/URL; Supported OS/storefront.

**Workflow outline:**

1. Document why the app qualifies as a reader app.
2. Verify entitlement approval and required link/API presentation for the applicable lane.
3. Keep the submitted destination and binary metadata aligned.
4. Test ineligible storefront and access to previously purchased content separately from checkout.

**Failure cases to cover:** Social media app with videos assumed to be a reader; Entitlement mixed with disallowed IAP configuration; Redirect or changed URL not reflected in review; An old global account-link rule overrides a current regional exception.

**Sources:** `src_policy_reader_apps`, `src_policy_review_guidelines`, `src_policy_dma`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Make moderation controls match the actual content surface

**Proposed reference:** `ugc-and-ai-content.md`

**Primary observation:** Guideline 1.2 explicitly includes AI content creation as well as social/user-generated platforms. Filtering, reporting, blocking and reachable support must function; content/age/payment responsibilities do not disappear when content is generated elsewhere.

**Inputs:** Posting/generation/sharing surfaces; Abuse and copyright reporting; Moderation response ownership; Blocking behavior; Age restrictions and support contact.

**Workflow outline:**

1. Map where objectionable content can enter or be exposed.
2. Provide the required reporting/blocking/filtering and operational response path.
3. Test abuse cases and child/age restrictions using safe synthetic fixtures.
4. Explain moderation and external AI/service behavior accurately to review.

**Failure cases to cover:** Report button with no operational recipient; Anonymous/random chat treated as safe solely because it has a block button; AI-generated content excluded from UGC policy; Private user data sent to third-party AI without required disclosure/permission.

**Sources:** `src_policy_review_guidelines`, `src_policy_kids_apps`, `src_policy_complete_review`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Separate age ratings, Kids Category and legal consent

**Proposed reference:** `kids-and-age.md`

**Primary observation:** Age ratings derive from the app’s real content/capabilities and can differ by region/OS. Kids Category commitments and parental gates are not interchangeable with legal consent to collect child data.

**Inputs:** Audience and actual content frequency; Chat/advertising/web access features; Kids Category selection history; Regional legal/parental-consent facts; SDK behavior.

**Workflow outline:**

1. Answer the current questionnaire from product evidence.
2. Use the applicable higher-rating override and retain region-specific documentation when required.
3. Review third-party analytics/ads against the stricter Kids guidance.
4. Test parental-gated links/purchases and handle uncertainty in age/consent without inventing it.

**Failure cases to cover:** Age inferred automatically from UI colors; A parental gate claimed to satisfy all privacy law consent; Changing category assumed to erase historic Kids commitments; Marketing-page consent shorthand used to bypass stricter guideline1.3 language.

**Sources:** `src_policy_review_guidelines`, `src_policy_kids_apps`, `src_policy_age_rating`, `src_policy_dma`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Collect the actual authorization and review evidence

**Proposed reference:** `health-and-regulated.md`

**Primary observation:** Health data has special permissions and use limitations; read denial can appear as absence of data. Regulated service and rights claims require the actual entity/region documentation requested by the relevant review lane.

**Inputs:** Health data types and uses; Permission usage descriptions; Clinical/research claims; Provider legal entity and jurisdiction; Research consent/ethics or rights documents.

**Workflow outline:**

1. Separate technical HealthKit access from authorization to provide a regulated service.
2. Request only relevant types and handle unavailable/empty data without inferring a denied permission.
3. Keep prohibited health-derived advertising/mining paths out of the product.
4. Provide real documentation through the secure review channel and identify missing owner facts.

**Failure cases to cover:** Empty HealthKit read interpreted as explicit denial; Medical efficacy/clearance claimed from a code test; Fabricated license or research approval; Personal health data placed in an unsuitable cloud store.

**Sources:** `src_policy_health_privacy`, `src_policy_review_guidelines`, `src_policy_complete_review`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Classify the asset before applying its rules

**Proposed reference:** `metadata-and-assets.md`

**Primary observation:** Screenshots, preview videos, icons and newer Creative Assets have different content constraints while sharing accurate-metadata responsibilities. Guideline2.3.14 separately recognizes Creative Assets; not every product-page asset must be an app screenshot.

**Inputs:** Asset type and target platform/device; Actual app behavior/build; Rights and synthetic account data; Localized names/descriptions/events; Privacy and purchase claims.

**Workflow outline:**

1. Choose the correct asset category and current specification.
2. Show genuine app use for screenshots/previews as required; classify Creative Assets separately.
3. Remove misleading claims, unsupported prices and third-party rights issues.
4. Verify descriptions, paid-feature disclosure, privacy details and significant-update notes against the built experience.

**Failure cases to cover:** Creative asset rules confused with screenshot-only rules; Real customer data appears in review media; External content rights assumed from public availability; Device/platform claim not supported by the submitted build.

**Sources:** `src_policy_review_guidelines`, `src_policy_submitting`, `src_policy_app_privacy_details`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Claim accessibility support only after common-task evaluation

**Proposed reference:** `accessibility-label-evidence.md`

**Primary observation:** Accessibility Nutrition Labels have per-device criteria and ask whether people can complete all common tasks using the claimed feature. The retrieved overview says voluntary-to-start; current submission requirements must be checked before declaring it mandatory.

**Inputs:** Common task list including onboarding/login/purchase/settings; Supported device/platform matrix; Assistive-feature evaluations; Known limitations and accessibility URL.

**Workflow outline:**

1. Evaluate actual common tasks with the relevant assistive features on each claimed device type.
2. Record evidence and unresolved blockers before indicating support.
3. Use the current evaluation criteria and platform-specific available labels.
4. Update claims when product behavior changes; keep screenshots/static audits distinct from usability proof.

**Failure cases to cover:** AX tree lint treated as VoiceOver certification; Only the happy-path main screen tested; Mac claimed to support an unavailable Larger Text label; Voluntary-to-start page described as an immediately mandatory requirement.

**Sources:** `src_policy_accessibility_nutrition`, `src_policy_review_guidelines`, `src_policy_submitting`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Review extensions as real product and privacy surfaces

**Proposed reference:** `widgets-siri-notifications.md`

**Primary observation:** Widgets/extensions/notifications must relate to the app; advertising placement and Siri/Shortcuts expectations are constrained. AppIntent authentication defaults can allow locked-device execution, so sensitive actions need deliberate authentication and backend access checks.

**Inputs:** Extension targets and manifests; Intent actions and lock-state behavior; Shared app-group data; Notification permissions/content; Deep-link and server authorization.

**Workflow outline:**

1. Map the main-app purpose to each extension/intent action.
2. Keep secrets and sensitive content out of inappropriate lock-screen/notification surfaces.
3. Set and test the supported intent authentication policy for sensitive actions.
4. Test denied permissions, signed-out accounts, duplicate delivery and invalid/deleted linked entities.

**Failure cases to cover:** Ads inserted between a Siri request and fulfillment; Unrelated intents registered for keyword capture; Locked intent relies on main-app UI authentication only; Extension manifest/resource omitted from the submitted product.

**Sources:** `src_policy_review_guidelines`, `src_policy_appintent_authentication`, `src_policy_notification_permission`, `src_policy_adding_manifest`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Answer export declarations from real implementation facts

**Proposed reference:** `encryption-export.md`

**Primary observation:** Apple asks developers to determine export compliance for encryption use, including OS-provided cryptography. Documentation/exception answers depend on actual app use and distribution, not a universal Info.plist boolean.

**Inputs:** Encryption features/libraries; OS crypto usage; Distribution regions; Existing approved documentation/key; Owner’s classification determination.

**Workflow outline:**

1. Inventory encryption use without exporting keys.
2. Answer the current App Store Connect determination questions using owner-confirmed facts.
3. Upload/attach actual required documentation before dependent review actions.
4. Set the corresponding Info.plist declaration only when supported by the determination.

**Failure cases to cover:** ITSAppUsesNonExemptEncryption blindly set false; Expected review duration promised as a guarantee; French/US obligations inferred from TLS use alone; Placeholder regulatory document packaged as real evidence.

**Sources:** `src_policy_export_overview`, `src_policy_encryption_docs`, `src_policy_beta_release`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Recover the existing submission before retrying

**Proposed reference:** `submission-recovery-and-appeal.md`

**Primary observation:** Add for Review is not the final Submit for Review step. All submitted items need acceptance; unresolved-item recovery and appeals have different procedures. An appeal is not a status/expedite request or a substitute for supplying missing information.

**Inputs:** Current version/build/item/submission IDs; Reviewer messages and cited guideline; Accepted/rejected item states; Whether code was fixed or decision is disputed.

**Workflow outline:**

1. Read current remote state before mutation or retry.
2. Prepare the evidence or repair for each cited issue.
3. Edit/resubmit or remove rejected items only within the intended release scope and supported state rules.
4. For a genuine dispute, clarify first, then prepare one focused appeal addressing all cited issues; send only when authorized.

**Failure cases to cover:** Creating a duplicate submission after a timeout; An accepted-only subset released unintentionally; Removed item assumed re-addable to the same submission; Appeal filed after fixing/resubmitting instead of resolving the current lane.

**Sources:** `src_policy_submit_app`, `src_policy_unresolved_review`, `src_policy_appeal`, `src_policy_app_review_overview`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Keep Mac App Store and Developer ID lanes distinct

**Proposed reference:** `mac-distribution.md`

**Primary observation:** Mac App Store review and Developer ID notarization are different distribution lanes. The notary service checks malware/signing and issues a ticket; it does not confer App Store review approval.

**Inputs:** Distribution channel; Signing certificate type; Executable targets and necessary entitlements; Archive/package format; Notarization ticket/log.

**Workflow outline:**

1. Select the intended Mac distribution lane before signing/export.
2. For Developer ID notarization, verify required signing and Hardened Runtime configuration.
3. Use currently supported notary tooling and inspect the returned log; staple/verify tickets as applicable.
4. For Mac App Store, check its sandboxing, packaging, update and startup-consent rules instead of applying external-distribution assumptions.

**Failure cases to cover:** Notarization called App Store acceptance; Broad Hardened Runtime exceptions added to silence a failure; Developer ID and Mac Distribution certificate confused; Installer or updater lane contradicts the selected store channel.

**Sources:** `src_policy_notarization`, `src_policy_hardened_runtime_current`, `src_policy_review_guidelines`, `src_policy_beta_release`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

### Track policy facts as dated, conditional evidence

**Proposed reference:** `policy-watch.md`

**Primary observation:** Primary pages can mix effective rules, announced future requirements, regional agreements, SDK support and voluntary programs. The plugin should refresh applicability rather than freeze dates/fees/exception lists in an evergreen checklist.

**Inputs:** Last reviewed source URLs/content hashes; Current date and submission date; OS/storefront/agreement/channel; Owner decisions and unresolved conflicts.

**Workflow outline:**

1. Record observed source title, section, retrieval date and relevant effective date separately.
2. Check whether a change is already effective for this submission.
3. When primary surfaces differ, preserve the conflict and resolve it through the more specific current rule/agreement or Apple clarification.
4. Update focused references and fixtures with the reason; do not silently change user policy answers or accept legal terms.

**Failure cases to cover:** Future April2027 SDK deadline applied in Oct2026; EU payment terms copied from a stale fee chart; Many Apple pages counted as independent organizations; Fetched HTTP200 PageNotFound or topic redirect treated as proof.

**Sources:** `src_policy_submitting`, `src_policy_dma`, `src_policy_user_privacy_data_use`, `src_policy_reader_apps`, `src_policy_accessibility_nutrition`.

**Freshness gate:** Recheck live primary sources for the selected platform, storefront, build and submission date before an external action.

## Observed conditions requiring special care

- The live submitting page announces minimum-upload SDK requirements for April 2027. An announced future upload requirement is not an automatic current compiler or deployment-target default.
- The current EU support page describes agreement/business-term changes and an October 2026 effective date; older fee tables, eligibility assumptions and entitlement guidance in repositories can be stale. Do not hardcode a commission or accept revised terms on the user's behalf.
- The live user-privacy page describes newer regional ATT prompt behavior tied to future/newer OS versions. Current tracking definitions remain distinct from API availability.
- Guideline 4.8 describes an equivalent privacy-preserving login option with exceptions. Avoid the shorthand that every login must add Sign in with Apple.
- Guideline 2.3.14 specifically covers Creative Assets, distinct from app-in-use screenshots and preview-video rules.
- The privacy manifest documentation distinguishes each app/SDK/executable bundle's actual use. A parent app manifest is not a substitute for a missing SDK required-reason declaration.
- The StoreKit purchase/restoration sample reviewed here uses legacy SKPaymentQueue. The API selection article states the original API is deprecated and identifies modern-API deployment support; do not label the sample StoreKit2.
- HealthKit read denial deliberately looks like no data; an empty read does not reveal permission denial.
- AppIntent authenticationPolicy defaults can allow execution when locked. Sensitive actions need an explicit supported policy plus domain/backend authorization.

## Unresolved

These are direct primary observations, not independently corroborated legal findings. Current legal classification, content rights, child consent, regulated-field authorization, export exemptions, fee obligations, agreement acceptance and App Store approval remain decisions/results requiring real owner evidence or the applicable review process. This research did not inspect the user's app or assert those facts.

A notable primary-surface conflict: the child-safety marketing page describes third-party data sharing with parent-consent language, while App Review Guideline1.3 states a stricter Kids Category restriction. Do not use the marketing wording as an automatic loophole; verify the current specific rule/agreement and intended data flow. Another contextual difference is accessibility labels' voluntary-to-start status versus future submission expectations; check the effective requirement at action time.

The official manifest-repair article describes deleting/fixing an invalid SDK manifest in an archive and Xcode re-signing. That is not blanket permission to remove a required listed SDK manifest or mutate an archive without scope. Prefer a valid vendor update, preserve the exact validation issue, and verify the final signed artifact and applicable requirement.

The App Review overview publishes typical review-time statistics, not an SLA. Do not promise approval time. No current hosted/account review, Xcode build, device test, signing or legal clearance was performed.

## Refuted

- HTTP success alone does not establish source identity: several guessed Apple URLs return a PageNotFound title with status200, and a generic-looking external-entitlement URL is specifically Netherlands dating-app guidance.
- Native package validation, notarization or an automated checklist is not App Store review approval.
- A parental gate is not automatically legal consent to collect a child's data.
- Account deletion is not automatically cancellation of an Apple-billed subscription.
- Many files from the same Apple organization are not independent corroboration.

## Source inventory

| ID | Reviewed source | Human URL | Review scope/identity caveat |
| --- | --- | --- | --- |
| `src_policy_submitting` | Submitting - App Store - Apple Developer | https://developer.apple.com/app-store/submitting/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_app_privacy_details` | App Privacy Details - App Store - Apple Developer | https://developer.apple.com/app-store/app-privacy-details/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_sdk_requirements` | Third-party SDK requirements - Support - Apple Developer | https://developer.apple.com/support/third-party-SDK-requirements/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_account_deletion` | 5.1.1(v) - Offering account deletion in your app - Guideline reference - App Review - Help - Apple Developer | https://developer.apple.com/support/offering-account-deletion-in-your-app/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_user_privacy_data_use` | User Privacy and Data Use - App Store - Apple Developer | https://developer.apple.com/app-store/user-privacy-and-data-use/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_kids_apps` | Design safe and age-appropriate experiences - Apple Developer | https://developer.apple.com/app-store/kids-apps/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_export_overview` | Overview of export compliance - Manage app information - App Store Connect - Help - Apple Developer | https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_encryption_docs` | Determine and upload app encryption documentation - Manage app information - App Store Connect - Help - Apple Developer | https://developer.apple.com/help/app-store-connect/manage-app-information/determine-and-upload-app-encryption-documentation/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_age_rating` | Set an app age rating - Manage app information - App Store Connect - Help - Apple Developer | https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_privacy_data` | Describing data use in privacy manifests | https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_privacy_required_reasons` | Describing use of required reason API | https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_adding_manifest` | Adding a privacy manifest to your app or third-party SDK | https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_att` | App Tracking Transparency | https://developer.apple.com/documentation/apptrackingtransparency | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_siwa_implementation` | Implementing User Authentication with Sign in with Apple | https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_storekit_selection` | Choosing a StoreKit API for Apple In-App Purchases | https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_storekit_purchase` | Offering, completing, and restoring Apple In-App Purchases | https://developer.apple.com/documentation/storekit/offering-completing-and-restoring-in-app-purchases | This article is a legacy SKPaymentQueue sample, not a StoreKit 2 sample. Read with choosing-a-storekit-api source. |
| `src_policy_notification_permission` | Asking permission to use notifications | https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_health_privacy` | Protecting user privacy | https://developer.apple.com/documentation/healthkit/protecting-user-privacy | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_beta_release` | Distributing your app for beta testing and releases | https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_notarization` | Notarizing macOS software before distribution | https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_hardened_runtime_current` | Hardened Runtime | https://developer.apple.com/documentation/security/hardened-runtime | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_privacy_manifest_current` | Privacy manifest files | https://developer.apple.com/documentation/bundleresources/privacy-manifest-files | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_appintent_authentication` | authenticationPolicy | https://developer.apple.com/documentation/appintents/appintent/authenticationpolicy | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_submit_app` | Submit an app - Manage submissions to App Review - App Store Connect - Help - Apple Developer | https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_unresolved_review` | Manage a submission with unresolved issues - Manage submissions to App Review - App Store Connect - Help - Apple Developer | https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/manage-a-submission-with-unresolved-issues | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_accessibility_nutrition` | Overview of Accessibility Nutrition Labels - Manage App Accessibility - App Store Connect - Help - Apple Developer | https://developer.apple.com/help/app-store-connect/manage-app-accessibility/overview-of-accessibility-nutrition-labels | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_purpose_strings` | 5.1.1(ii) - Write clear purpose strings - Guideline reference - App Review - Help - Apple Developer | https://developer.apple.com/help/app-review/guideline-reference/5-1-1-purpose-strings | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_complete_review` | Provide information for a complete review - Before submitting for review - App Review - Help - Apple Developer | https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_appeal` | Appeal to the App Review Board - After submitting for review - App Review - Help - Apple Developer | https://developer.apple.com/help/app-review/after-submitting-for-review/appeal-to-the-app-review-board | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_dma` | Changes for apps in the European Union - Support - Apple Developer | https://developer.apple.com/support/dma-and-apps-in-the-eu/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_external_link_entitlement` | Distributing dating apps in the Netherlands - Support - Apple Developer | https://developer.apple.com/support/storekit-external-entitlement/ | This legacy-looking URL is specifically Netherlands dating-app distribution. It is not generic worldwide external-link entitlement guidance. |
| `src_policy_reader_apps` | Distributing “reader” apps with a link to your website - Support - Apple Developer | https://developer.apple.com/support/reader-apps/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_subscriptions` | Auto-renewable Subscriptions - App Store - Apple Developer | https://developer.apple.com/app-store/subscriptions/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_app_review_overview` | App Review - Distribute - Apple Developer | https://developer.apple.com/distribute/app-review/ | Primary article discussion and task-relevant sections, as recorded in reference-card outlines; long pages were not represented as exhaustively audited. |
| `src_policy_review_guidelines` | App Review Guidelines - Apple Developer | https://developer.apple.com/app-store/review/guidelines/ | Sections 1.2, 1.3, 2.1, 2.3, 2.4.5, selected 2.5 clauses, 3.1.1, 3.1.1(a), 3.1.2(a-b), 3.1.3(a-f), 4.2, 4.8, and 5.1.1–5.1.4. |
