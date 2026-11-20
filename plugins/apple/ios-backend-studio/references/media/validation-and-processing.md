# Keep untrusted media quarantined until the required checks pass

## Define the accepted product surface

Specify which media the feature needs, who can upload/view it, maximum encoded/decoded resource cost, required metadata and the intended processing/delivery policy. A profile image, chat attachment and user-supplied document have different parser and visibility risks. Do not accept every extension or content type merely because the storage provider can store it.

Separate admission, bytes received, validation, processing, ready, rejected and deleted states. Keep unapproved objects outside public delivery. An upload completing successfully is a transport observation, not proof of safe type, domain ownership or successful transformation.

## Validate in layers

Use an allowlist appropriate to the feature. Treat filename, extension, Content-Type and client-reported dimensions as untrusted input. Apply size and request bounds before expensive parsing, then verify the actual format with a suitable maintained parser under an intentional resource budget. File signatures can support classification but are not a complete security check on their own.

Reject unsafe path usage by choosing server-owned object identities; preserve a sanitized display filename only when needed. Do not pass a user filename into shell text, a local filesystem path or a processor command without the appropriate safe argument/path handling. Keep processor configuration separate from user-supplied options.

| Layer | Question | Example failure to cover |
| --- | --- | --- |
| Admission | Is this account/entity allowed to submit this type? | Valid session with another account's upload ID |
| Transfer bound | Can the request/object exceed the allowed resource budget? | Oversized or truncated upload |
| Format | Do the actual bytes match a supported format? | Spoofed MIME type or polyglot/malformed file |
| Decode/process | Can work exceed CPU, memory, time or output limits? | Extreme dimensions, decompression expansion, corrupt input |
| Domain association | Is the approved object/version still the expected one? | Object replaced after validation |
| Delivery | Does current viewer/content policy allow this result? | Quarantined/private object exposed by a public URL |

## Process with explicit ownership

Queue expensive transforms only when the feature needs them and work must survive the HTTP request. Use a stable asset/version/transform identity and a durable receipt so duplicate jobs do not create conflicting outputs. If the input changes, decide whether old work is cancelled, ignored or retained as a prior version; a late result must not overwrite the current asset.

Bound CPU, memory, decoding, output size, temporary disk and execution time using the actual processing environment. A subprocess or container can help isolate work, but its mere presence is not a complete sandbox or security proof. Avoid fetching arbitrary user-supplied URLs as a shortcut to “import media”; that introduces a separate server-side request/credential/network boundary.

If antivirus, document reconstruction or other content analysis is required, use an actually configured service/tool and retain an explicit unknown/failure state. Do not label content “scanned” because a placeholder function returned true. Keep user content and processor diagnostics out of general logs, and apply the real privacy/retention policy to raw/derived objects.

For thumbnails/previews, derive only the variants the app needs. Decide how orientation, color, animation, metadata and accessibility descriptions are preserved or transformed. If location or other sensitive metadata must be removed, verify the resulting files; do not claim removal merely because a different extension was written.

## Delivery and deletion

Serve only approved variants through the intended account/content boundary. Set actual content type and safe delivery headers according to the feature. A public CDN URL or long-lived signed URL can outlive an account permission change; design expiration/invalidation/revocation around the provider's real behavior instead of promising immediate revocation universally.

Deletion must address the authoritative asset, derived variants, pending jobs, caches and stored references according to the product's actual policy. Use object/version ownership guards so a late cleanup cannot delete a replacement. Do not give a generic bucket-wide delete command as an application repair.

## Verification and evidence

Test malformed/unsupported bytes, misleading filenames/types, resource-limit failures, processing crash/retry, changed input versions, scan unavailable, cross-account delivery, deletion during transformation and late result publication. Assert both database state and object visibility. Use synthetic fixtures rather than customer media or copyrighted demo assets.

Sources: `src_backend_extra_upload_security`, [OWASP File Upload Cheat Sheet at the reviewed commit](https://github.com/OWASP/CheatSheetSeries/blob/a5fbb7f886c02e3418e17f5525874a868cca49e4/cheatsheets/File_Upload_Cheat_Sheet.md); `src_nm_node_security`, [Node security practices](https://nodejs.org/en/learn/getting-started/security-best-practices); and `src_nm_bullmq_idempotent`, [idempotent processing guidance](https://docs.bullmq.io/patterns/idempotent-jobs). See [the catalog](../../research/sources/sources.jsonl). Parser/service safety, policy facts and runtime isolation need actual version/environment checks; this card is not a content or security certification.
