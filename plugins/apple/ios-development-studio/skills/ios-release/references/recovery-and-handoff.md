# Release recovery and handoff

## Recover from partial completion

Retain nonsecret receipts from each mutation: app/version/build/submission IDs, operation, timestamp, artifact reference and observed result. A failed batch may contain completed items. Inspect them before retrying; do not rerun the entire release blindly.

Classify the interruption:

- Local artifact/build failed: repair locally; no remote stage should be inferred complete.
- Upload returned uncertain status: query the exact app/version/build number and available upload/build receipts.
- Build processing failed: preserve diagnostic evidence and decide whether a new binary is needed.
- Staging applied some metadata/assets: compare the remote state and canonical files before resuming.
- Review draft or active submission exists: inspect ownership/state/items; reuse a suitable draft and avoid a second submission.
- Review rejected or blocked: read the rejection/readiness evidence and repair the specific cause.

Cancellation is not a routine retry technique. A long review duration alone does not justify withdrawing the app. Resolve the exact active submission and the user’s intended outcome before cancellation. Once authorized repairs pass, resume the chosen lane using preserved IDs.

## TestFlight distinctions

A build can be uploaded but still processing, processed but unavailable to a group, or available but awaiting external beta review. Tester/group membership and notifications have independent effects. “Upload only” should not silently create groups, invite people, change test notes or submit beta review.

Resolve groups and testers deterministically. An account-wide tester list is sensitive; use only needed records, keep exports local and redact emails in summaries. Sending invitations or notifications requires scope that includes them; general preparation is insufficient.

Verify the actual group/build relationship and observed status after distribution. Do not claim a tester received an email or installed the app solely because an API request succeeded.

## Workflow files and secrets

A release workflow may execute arbitrary shell hooks and mutate multiple services. Inspect trusted definitions before running, particularly in a PR or downloaded archive. Prefer the project’s existing secrets mechanism and keep credentials out of version control, logs and artifacts. Validate syntax and tool-specific semantics; a YAML parse does not validate remote profile names or account access.

Retries should be limited and tied to evidence. Automatic retries of a non-idempotent publishing step can duplicate remote objects or notifications. On uncertainty, query state rather than infer failure. Preserve actual child exit status through wrappers and parse partial receipts even when the command exits nonzero.

## Report the real endpoint

A useful handoff contains app/platform/version/build identifiers, artifact path, lane used, checks completed, remote mutations, resulting status and next observation command derived from installed help. List blocking findings with evidence and exact pending actions. Label suggested commands as unexecuted.

Use phrases that match evidence: “archive exported”, “upload accepted”, “build processed”, “available to selected beta group”, “submitted”, “approved” and “released” are different statements. Preserve any public availability uncertainty, storefront delay or missing account check. Keep runtime validation limitations visible.
