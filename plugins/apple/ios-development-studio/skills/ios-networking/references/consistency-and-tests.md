# Retries, consistency and tests

Reliable networking preserves the meaning of the operation when requests fail, overlap or return late. Model the request's identity, owner and retry policy before adding automatic retry behavior.

## Bounded retry policy

Retry only eligible transient failures and only when the operation can safely repeat. A GET is usually a candidate, but the actual API contract wins. A create, purchase or send operation must not be replayed merely because it timed out: the server may already have committed it. Use server-supported idempotency keys, reusing a key for the same logical operation and changing it for a genuinely new one. Do not invent exactly-once guarantees.

Bound attempts and total elapsed time. Apply backoff with jitter, honor a valid server Retry-After policy where appropriate and make both delays and requests cancellation-aware. Avoid retrying authentication rejection, validation failures, cancellation or incompatible schema indefinitely. Define whether the backend's throttling response is retryable and whether request body streams can be safely recreated.

Inject a clock/sleep abstraction and deterministic random source when policy requires jitter. Tests should advance a fake clock instead of waiting in real time. Assert attempt count, eligibility, same operation identity, deadline and cancellation during backoff. Do not write a test that only repeats the implementation's arithmetic.

## Authentication refresh

Keep credential refresh behind the existing auth provider. Coalesce simultaneous refresh attempts if the contract permits; otherwise expired credentials can trigger a request storm. Use a generation/account check so an old refresh cannot log back in after logout or replace a newer session. Retry a rejected request only within a bounded documented flow, with a freshly constructed authorized request.

Do not embed a confidential OAuth client secret in a mobile app. Token storage and browser-based authorization belong with `ios-security`. A service's configured scopes and redirect URLs are inputs; do not create new ones without a requirement.

## Pagination and stale results

Use the service's cursor, ordering and revision fields. Track loading state per query/direction, prevent repeated triggers from duplicating pages and de-duplicate by stable domain identity. Advance the cursor only after accepting the matching response. Handle empty pages, invalidated cursors and an explicit end-of-history state.

Cancel or supersede requests when search/account/filters change. Cancellation alone does not replace a generation check: work might complete before cancellation is observed. A late response cannot replace a newer accepted result or cross account boundaries. Merge rules should preserve server revisions for updates/deletes instead of blindly appending arrays.

## Offline state

Reachability changes are hints, not permission to skip all requests or proof of a working endpoint. Attempt the operation and handle the actual response. Define cache freshness, stale presentation and manual refresh separately. HTTP URLCache is a cache, not durable domain storage; the system can purge it. A persisted offline store needs explicit migration, retention and synchronization policy.

For writes, decide whether offline behavior is rejection, a draft or an outbox. An outbox needs durable operation IDs, replay eligibility, user/account ownership, expiry and conflict handling. A network retry queue is not sufficient. Do not silently upload user work after account changes or consent revocation.

## Minimal useful test matrix

| Case | Assertion |
| --- | --- |
| Success, including empty success | Correct accepted status/body mapping |
| Rejected HTTP response | Safe domain error; error body handled intentionally |
| Malformed or oversized body | Controlled contract/resource error |
| Cancellation before/during transfer | No retry, no stale UI update |
| Eligible transient failure then success | Bounded retry with expected identity/delay |
| Write timeout without idempotency contract | No automatic unsafe replay |
| Concurrent expired-token requests | Refresh follows selected single-flight policy |
| Logout while refresh/page is in flight | Old response cannot mutate new session |
| Overlapping pages with edits | Stable deduplicated order and revision preservation |

Inject a transport closure/protocol or a supported URLProtocol fixture. Keep fixtures local, deterministic and free of real credentials. Mocks validate client behavior; an authorized staging smoke check is needed for the actual server contract. Report these separately.

Sources: official Apple [URLSession](https://developer.apple.com/documentation/foundation/urlsession) and [URLCache](https://developer.apple.com/documentation/foundation/urlcache); uploaded Chat ordering tests and Nuke request-lifecycle tests informed original consistency fixtures. The retry, outbox and idempotency rules are design guidance to be checked against the user's service, not claims about either uploaded library. See [source map](../../../docs/source-map.md).
