---
name: privacy-manifests
description: "Review and repair Apple privacy-manifest structure, target/package resource placement, required-reason API ownership and SDK manifest/signature evidence. Use for PrivacyInfo.xcprivacy and archive privacy findings; do not infer privacy labels or legal facts from a valid plist."
---

# Privacy Manifests

First read the [operating contract](../../references/operating-contract.md). The actual task and established authorization govern the work.

Resolve the selected artifact and component inventory, then reconcile manifest structure, actual API/data use and packaging.

## Workflow

1. Resolve app, platform, storefront, distribution channel, release/artifact and requested endpoint. Read the actual project and current primary sources for the selected scope.
2. Inspect target/dependency ownership; check the current documented categories/values; make the concrete owner-controlled resource/dependency fix; rebuild and inspect the actual product; report structure, placement and factual limits separately.
3. Keep four explicit outcomes: **satisfied by evidence**, **concrete blocker**, **unknown/needs evidence**, and **not applicable with a reason**. A parser/test result proves only its checked scope.
4. Finish independent authorized work while a genuinely missing product, legal or target-environment fact is resolved. A review/preparation task does not authorize remote publication or factual declarations on the owner’s behalf.
5. Return concrete findings or changes, source/date/applicability, exact checks and artifact/account stage, with the next evidence needed. Never report local readiness as review approval.

## Focused references

- [Inventory and placement](../../references/privacy-manifests/inventory-and-placement.md)
- [Required reasons and sdk boundaries](../../references/privacy-manifests/required-reasons-and-sdk-boundaries.md)
- [Archive report and repair](../../references/privacy-manifests/archive-report-and-repair.md)

Read only the card needed for the current decision. Primary policy statements are contextual source observations, not independent legal clearance. Resolve contradictory, regional or forward-dated conditions before the dependent action; do not freeze them as universal defaults.
