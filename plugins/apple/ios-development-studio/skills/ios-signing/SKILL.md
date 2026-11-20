---
name: ios-signing
description: "Use for iOS bundle/team identity, entitlements, certificates, provisioning profiles, archive signing, release-testing packages and signing failures. Do not use to revoke unrelated assets, invite testers, publish an app or package credentials."
---

# Resolve signing and distribution identity

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Establish the app’s bundle identifiers, target/extension identities, team/provider, intended distribution method and actual local signing environment. Reuse existing authorized credentials and profiles before creating or rotating anything.

1. Inspect the project’s signing settings and the exact error. Check identity, entitlements, profile validity/device membership and certificate/private-key availability separately.
2. Select the smallest repair or setup plan. Preserve working team assets and other apps’ profiles.
3. Prepare or export the requested artifact using the established Xcode/CI/asc lane and help-supported flags. Keep private material outside the repository and plugin package.
4. Verify artifact identity, signing/entitlements/profile compatibility and the requested installation/export result.
5. Record exact nonsecret resource IDs, local artifacts and changes. Hand delivery to `ios-release`; an export does not authorize upload, tester notifications or submission.

Use current tool help rather than copying certificate/profile enums. Never request a secret in chat when the host’s credential mechanism or a private local path can supply it.

Read only the references needed for the current step:

- [Identity and profile diagnosis](references/identity-and-profiles.md)
- [Signing artifacts and secret handling](references/exports-and-secrets.md)
- [Signing provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
