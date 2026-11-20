# Authorize an upload session, then verify the owned object

## Inputs and provider boundary

Identify the selected storage provider, bucket/container policy, app domain entity, account scope, accepted types/sizes, integrity requirements and delivery visibility. Preserve an existing provider. An S3-compatible API label does not prove that every AWS policy, conditional header, checksum or expiry behavior works identically on another service.

Define a server-side upload session with stable identity, authenticated owner, intended parent/use, provider object identity, expected constraints and a state/expiry policy. The server chooses the storage key or equivalent safe object identity; a user filename is display metadata, not a trusted path or permission boundary.

## Create a constrained capability

Authorize the user's intent against the domain entity before signing any storage access. A public client must not receive general bucket credentials or a backend signing key. If the provider supports a signed upload URL or temporary scoped credential, constrain method, target object, intended headers/conditions and lifetime using its actual contract.

Treat a signed URL as a bearer capability: possession may grant the allowed operation until it expires or is otherwise invalidated. Do not log it, include it in analytics, attach it to a public issue or store it in a general-purpose crash payload. Keep backend API authorization headers/cookies separate from the storage request; a shared client middleware must not forward them to the object-storage host.

Choose unique object identities or a documented conditional-write mechanism when overwriting an existing object is not intended. Do not describe every signed URL as single-use. Some providers permit repeated use and replacement at the same key until expiry; application session state alone cannot necessarily prevent a direct second storage request.

| Server action | Durable check | Capability boundary |
| --- | --- | --- |
| Create session | Caller owns the intended entity/use | Only the approved object/method/conditions |
| Refresh expired upload access | Session still owned, admissible and incomplete | New bounded capability; no broader storage scope |
| Finalize | Object and constraints match the session | No user-selected arbitrary object association |
| Deliver/download | Current viewer may access the asset | Appropriate visibility and revocation/expiry policy |
| Cleanup abandoned work | Session/object is in the intended expired scope | No blanket bucket or account-wide deletion |

## Finalize from evidence

The client reports completion using the upload-session identity. The backend independently verifies the expected object's existence, size and relevant metadata/integrity conditions through the chosen provider API. Do not trust a client-supplied “uploaded” flag, MIME type or arbitrary object URL as proof.

Treat an ETag or version token according to the provider contract; do not assume it is a content hash. When the product needs a checksum, choose a supported algorithm and verify its documented semantics. Validate exact provider object/version identity so a later replacement cannot silently substitute different bytes after approval.

Commit the asset's domain association and finalized session state atomically where possible. Make duplicate finalization reconcile the same result, with changed intent rejected or repaired under explicit policy. If content must be scanned/transformed, finalization can admit processing while the asset remains quarantined; do not mark it ready before the required checks succeed.

## Expiration and unknown outcomes

Distinguish upload-access expiry, temporary provider-credential expiry, session expiry, local-file lifetime and domain-asset retention. The shortest applicable provider condition may end access before the displayed URL duration. Refresh through the authorized backend flow rather than embedding longer-lived secrets in the app.

After a lost finalization response, reconcile by session/operation identity. Do not create a fresh asset blindly. After an interrupted multipart upload, use the provider's exact resume/abort rules and retain only the intended upload's state. Cleanup can be automated under the product's established retention policy, with ownership/age guards and bounded work.

## Verification

Test an upload for another account/entity, changed object key, reused capability, overwrite attempt, wrong method/header, expired access, size/checksum mismatch and duplicate finalization from different service instances. Crash after object upload, after domain commit and before the response; verify recovery without duplicate assets or exposed quarantined content.

## Evidence and version cautions

`src_backend_extra_s3_presigned` is [AWS presigned URL guidance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html); `src_backend_extra_s3_conditional` covers [conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html). `src_backend_extra_upload_security` identifies the pinned [OWASP upload guidance](https://github.com/OWASP/CheatSheetSeries/blob/a5fbb7f886c02e3418e17f5525874a868cca49e4/cheatsheets/File_Upload_Cheat_Sheet.md). These inform an original provider-neutral flow, not a claim of feature parity across storage services. See [source records](../../research/sources/sources.jsonl) and inspect the actual SDK/provider version.
