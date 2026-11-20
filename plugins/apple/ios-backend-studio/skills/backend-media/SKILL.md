---
name: backend-media
description: "Use for authorized media upload/download sessions, signed storage capabilities, validation/processing, native transfer recovery and asset ownership against a Node backend. Preserve the selected storage provider; do not add image generation, public hosting, a media service or broad bucket cleanup without a task need."
---

# Media ownership and transfer lifecycle

First read the [operating contract](../../references/operating-contract.md).

1. Identify the actual storage provider, domain owner, accepted file types/limits, native transfer path and visibility/retention policy. Keep server credentials out of clients.
2. Use [upload sessions](../../references/media/upload-sessions-and-capabilities.md) to authorize intent, constrain storage access and finalize only a verified owned asset.
3. Use [validation and processing](../../references/media/validation-and-processing.md) for quarantined content, bounded parsing/transforms and safe delivery.
4. Use [native transfer lifecycle](../../references/media/native-transfer-and-lifecycle.md) for file persistence, progress, background transfer, expiration and account changes.
5. Verify forged ownership, altered/oversized content, duplicate finalization, lost responses, interrupted transfers, processing failure and signed-URL redaction.

Return the asset/transfer state contract, implementation, selected provider/SDK assumptions, actual checks and pending Apple/device behavior. Successful bytes uploaded is not proof that the domain asset is validated, authorized or ready for public delivery.
