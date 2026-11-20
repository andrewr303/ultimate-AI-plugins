# Chat state and verification

Start with a small state contract rather than a set of independent callback mutations. The app should know the active conversation/account, message map/order, pagination cursor, request generation, in-flight sends and per-item failure state. Keep mutable UI state on its intended actor and send immutable values through transport boundaries.

## Ordering and identity

The uploaded `Tests/ExyteChatTests/WrappingMessagesTest.swift` explicitly checks that input order determines displayed message order; creation timestamps do not automatically sort it. Define your backend ordering field and tiebreaker. Normalize incoming pages and live events into one stable domain sequence. Replies in answer mode and quote mode group differently, so verify against the actual UI mode rather than compensating with arbitrary array reversal.

A retry must preserve the logical operation identity. If the server supports idempotency keys, persist and reuse one key for the same send. If it does not, do not promise exactly-once delivery. Reconcile optimistic rows by the acknowledged identifier and show uncertainty when a network failure leaves acceptance unknown. The adapter should never create a fresh UUID every time it maps an already stored message.

## Pagination and remote events

Record the cursor from the accepted page, whether more history exists and which request owns the loading indicator. Allow at most the intended concurrent request per direction. Repeated scroll callbacks must not create duplicate pages. Filter duplicate identifiers while preserving edits and deletion events. An empty page with a valid next cursor has different meaning from the end of history; use the service contract.

A conversation switch must invalidate or cancel old requests. Check account/conversation identity and generation when responses arrive, including cache hits. A canceled request can still have completed side effects remotely; canceling a send does not prove it was never sent. Preserve enough metadata to recover on reopen when the product requires durable outbox behavior.

Use server revisions or sequence information where available for edit/delete ordering. Avoid allowing a late snapshot page to resurrect a deleted message or replace a more recent edit. Decide what happens to a reply when its parent is outside the loaded window. Keep loading states separate for initial history, pagination and outgoing attachments so one completion does not clear another's progress.

## Attachments and drafts

Treat a draft as user work. Define when it is cleared, whether navigation preserves it and how retry retains media access. A sensible send pipeline validates locally, creates the operation, uploads media with progress, submits the message and reconciles acknowledgment. On partial failure, retain the draft or retryable operation according to the product design; do not display delivered while uploads remain incomplete.

Do not assume a temporary asset URL survives relaunch. Copy only necessary authorized content to an app-owned location, record ownership and delete it when no longer needed. Handle canceled picker selection and revoked library access. Use backend limits for type/size/content processing; frontend filtering is not an authorization boundary.

## Verification matrix

| Case | Observable result |
| --- | --- |
| Same live event delivered twice | One logical row, latest valid state retained |
| Page overlaps existing rows | Stable order without duplicates or scroll jump |
| Send times out after remote acceptance | Uncertainty is recoverable; retry follows server idempotency contract |
| Attachment fails after optimistic row | Visible retry/error state; draft media is recoverable |
| Switch account during history request | Old response cannot appear under the new account |
| Edit arrives before stale page | Old page cannot overwrite newer revision |
| Keyboard, long text and Dynamic Type | Composer and newest content remain reachable |
| Screen reader and denied permissions | Controls have useful labels; accessible recovery exists |

Use fake transport events and an injected clock for deterministic timeouts, ordering and retry tests. Use the actual framework in previews/simulator for row grouping, keyboard and menu behavior. Device checks are needed for camera/audio/location, background transitions and real accessibility behavior. Report exactly which were run. The uploaded tests were inspected, not executed by this plugin build.

See [source map](../../../docs/source-map.md) for the uploaded Chat snapshot. Network policy and retry implementation are owned by the app; use `ios-networking` for shared transport and `ios-security` for credential/media privacy boundaries.
