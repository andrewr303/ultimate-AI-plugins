---
name: ios-store-metadata
description: "Use for App Store listing metadata, localization, screenshots, ASO review and evidence-based release notes. Do not use to invent product claims, publish prepared content, change prices or infer privacy/legal declarations."
---

# Prepare and maintain App Store content

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Resolve the app/version/platform/locales and canonical metadata/assets location. Preserve existing formats and approved brand terminology. Derive release notes from actual changes and build screenshot plans from real app states.

1. Pull or inspect current content read-only when authorized and available; retain a baseline.
2. Prepare localized copy, release notes and screenshots with explicit sources and reviewable diffs.
3. Validate schema, lengths/placeholders, locale completeness and current screenshot requirements using installed tooling/current official specifications.
4. Apply content only when the task includes that remote update, using a scoped plan/dry-run and preserving unrelated locales/assets.
5. Read back the changed fields and report validation, publication state and unresolved translation/product facts.

Use `ios-simulator` for capture, `ios-release` for attaching/submitting a release and `ios-commerce` for product/price changes. External ASO services are optional integrations whose availability must be verified.

Read only the references needed for the current step:

- [Content, localization and change notes](references/content-and-localization.md)
- [Screenshots and asset validation](references/screenshots.md)
- [Store content provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
