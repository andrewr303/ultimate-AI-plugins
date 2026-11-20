# Match required-reason API use to the owning bundle

## State the reason behind the declaration

Required-reason API review asks what an executable does and why. It is not a hunt for any approved identifier that makes upload feedback disappear. The current Apple documentation describes categories of APIs and associated approved reasons. Those reasons must accurately reflect the app or SDK's actual functionality and handling of derived data. Tracking consent does not authorize fingerprinting.

Maintain a map from an observed API category to the call site or SDK, its user-visible purpose, the executable/bundle containing it, the selected documented reason and the person responsible for confirming that purpose. Keep a candidate found by text search separate from a confirmed call path. Generated code, conditional compilation, binary SDKs and dependency variants can make a simple search incomplete.

## Inputs that matter

Use the real target and SDK versions, first-party source, dependency declarations, framework documentation and the archived component tree. Read the current category/reason definitions before proposing a code. Do not infer an SDK's complete behavior from its marketing name or infer that no covered API exists merely because one source search returned nothing. For opaque binary behavior, ask for vendor evidence and retain unknown status while performing other checks.

## Apply the ownership rule

Apple's article says the app reports its own covered API use and a third-party SDK reports that SDK's use. A third-party SDK cannot rely on another SDK or the app's manifest to substitute for its own declarations. The article also calls out the bundle for each executable or dynamic library using covered APIs. Build this boundary into the inventory instead of flattening every declaration into the main app.

1. Establish the API's actual invocation and data use in the selected build.
2. Read the approved reasons for that exact category and compare the entire definition to the implementation.
3. If a reason fits, record the reason and the implementation evidence. If none fits, identify the need for a product/code change or the current documented process for requesting a reason; do not invent a value.
4. Put the declaration in the owner-controlled resource for the correct product boundary and verify packaging.
5. Rebuild and inspect the archive, then reconcile the required-reason map with the privacy report and any upload feedback.

## Avoid misleading shortcuts

A declaration is not a permission grant to reuse API-derived data for unrelated analytics. It is not enough that a reason appears in another project's manifest. A framework wrapping a call still needs review at the appropriate ownership boundary. An app manifest containing every known reason is not safer than an accurate minimal declaration and may make a false factual assertion.

A proposed manifest with an undocumented reason is a concrete blocker. A documented reason with no implementation evidence stays unknown until confirmed. A confirmed category used only in a build variant not being released may be not applicable to this artifact, with the variant evidence recorded. “Satisfied” should identify which category and component was verified rather than implying an exhaustive semantic audit.

## Verification and handoff

Use fixtures for a covered call in first-party code, one in a dependency, a category declared in the wrong bundle, an unknown reason code and a valid declaration whose file is missing from the archive. Test the stated feature behavior if a code change alters how data is accessed. Preserve the current official definition in a short issue summary with its source URL and observation date; do not copy a stale table into a permanent allowlist and call it current.

When App Store Connect identifies a missing declaration, retain the exact component/path/category from the message in protected diagnostic evidence. Resolve that finding against the same built artifact. Do not relabel the app as compliant merely because a follow-up upload produces no immediate email.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_privacy_required_reasons` — [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- `src_policy_privacy_manifest_current` — [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- `src_policy_adding_manifest` — [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
