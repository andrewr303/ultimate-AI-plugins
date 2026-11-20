# Inventory and place privacy resources per product

## Resolve the product boundary

Start with the build product, not a search for one filename. List the main app, extensions, embedded frameworks, dynamic libraries, static-framework resources and each platform variant in an XCFramework. Record which first-party target or vendor owns each component. A manifest in a repository does not establish that the signed product includes it, and a top-level XCFramework manifest does not establish that every selected variant contains the appropriate resource.

Apple documents `PrivacyInfo.xcprivacy` as a property-list resource with documented keys and values. Its location depends on product and platform. Let the actual build system place the resource according to current documentation; for a package, inspect its explicit resource declaration. Do not copy an iOS path into a macOS bundle without checking the macOS layout. A static library cannot simply carry resources as though it were an ordinary bundle; inspect how its distributor packages the resource-bearing product.

## Required inputs

Collect the selected archive, target/dependency inventory, package resource declarations and manifests for the exact dependency versions. Identify the app's real collection, tracking and required-reason API use separately. Keep business facts such as collection purpose and retention tied to their owner. Inventory records can include relative component paths and hashes; do not capture customer data, account secrets or unrelated app containers.

## Work through the inventory

1. Resolve the scheme, configuration and platforms used to build the artifact. Include app extensions and platform variants that the release actually ships.
2. Find every manifest in source and note its owning target/vendor. Inspect its plist syntax, key spelling and value types against the current documentation.
3. Confirm target membership or package-resource configuration rather than assuming source adjacency makes the file a resource.
4. Inspect the archive's actual bundle tree. Match each manifest to the correct component and platform; report source-only or misplaced files explicitly.
5. Compare the resolved dependency inventory to Apple's current listed-SDK requirements. Binary and source distribution can have different signature evidence, while neither removes the need for accurate data facts.
6. Build an issue list by component. Update the owner-controlled source or dependency through its normal process, then rebuild and inspect the resulting product.

A generated privacy report helps reconcile the included manifests; it does not prove all executable behavior was declared correctly. Keep that limitation in the evidence packet rather than changing a declaration solely to make the report look empty.

## Decide status from evidence

**Satisfied by evidence** means the selected product contains the checked resource at the documented location, its structure is valid, and the specific requirement is met. Name the artifact/configuration and limits. A **blocker** is a concrete missing or invalid required resource in that artifact. **Unknown** covers unresolved SDK ownership, an unbuilt target, unverified collection facts or a product variant not inspected. **Not applicable** needs a reason tied to the component and current rule; “the app has a manifest” is not such a reason for another bundle.

## Failure and verification cases

Check a resource intentionally removed from target membership, an extension built with a different configuration, an XCFramework with only one variant fixed, and a Swift package whose manifest is not declared as a resource. Distinguish a plist parser passing from App Store Connect accepting the archive. Keep source and artifact paths in the finding so a developer can reproduce the mismatch without access to private production content.

The final handoff should identify component, owning party, current requirement, observed path and exact remaining repair. Do not silently edit a vendor bundle, discard a signature or delete a manifest as routine cleanup. Those changes affect the submitted artifact and need an intentional, verified repair path.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_privacy_manifest_current` — [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- `src_policy_adding_manifest` — [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- `src_policy_sdk_requirements` — [Third-party SDK requirements - Support - Apple Developer](https://developer.apple.com/support/third-party-SDK-requirements/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
