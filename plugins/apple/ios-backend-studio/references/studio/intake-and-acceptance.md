# Intake that leads to an implementable outcome

## Inputs to resolve

Start with the requested user behavior, the affected app/service paths, supported client versions and the smallest concrete example. Ask what changes only when the repository and request cannot answer a fact that changes correctness. An endpoint may serve the main app, a widget, a web client and an older released app simultaneously; a single successful request from the newest app does not define compatibility.

Read relevant project instructions and current changes before selecting a framework or editing a generated client. Identify the wire-contract authority, server entrypoint, client transport, domain store and release path. Inspect lockfiles and actual target settings. Do not infer an Expo runtime from a Node tooling wrapper, an authenticated account from a named environment variable, or a working deployment from a configuration file.

## Write acceptance in observable terms

Express completion as a trigger, actor, authoritative effect and user-visible result. For example: “An authorized account creates one item; a repeated request with the same operation identity returns the recorded outcome; another account cannot read it; the app shows a recoverable pending state after an uncertain transport failure.” Treat that as an example design, not an assumption that every existing API already supports idempotency.

Capture the smallest applicable acceptance table:

| Case | Observation that settles it |
| --- | --- |
| Valid request | Expected status/body and durable domain invariant |
| Invalid wire data | Stable rejection before unintended side effects |
| Wrong account/entity | Server denial independent of client UI visibility |
| Expired session | Existing refresh or sign-in path without replaying unsafe writes |
| Duplicate/late work | Intended deduplication and current authoritative state |
| Offline/cancellation | Honest local state and later reconciliation |
| Old supported client | Its real decoder and request shape still behave as promised |

Select rows relevant to the task. A text-only contract correction does not require creating a queue or implementing a new auth provider. Conversely, a write path cannot be validated only by confirming that generated source compiles.

## Keep work and authority concrete

Distinguish preparation from an external mutation. A request to implement an API permits ordinary local edits and relevant tests. A plan to deploy needs the intended environment, account-safe target identity, artifact and existing authorization. Finish a reviewable candidate before asking for genuinely missing authority. Preserve unrelated changes, production data and the user's existing service choices.

When a platform is unavailable, split the work by dependency. Wire fixtures, Node tests and source changes can continue while an Xcode/device gate remains pending. State the missing environment and exact check rather than inventing a pass or provisioning an unrequested replacement service.

## Handoff evidence

Retain the accepted trigger/effect, affected owners, contract revision, actual versions and smallest test command. List consequential unknowns with the fact needed to resolve each. Do not copy credentials, user payloads or entire production logs into the handoff. End an implementation task with the changed artifact and observed checks, not only this intake record.

Sources: src_nm_openapi_spec — [OpenAPI definition](https://spec.openapis.org/oas/v3.1.1.html); src_nm_node_test — [Node test runner](https://nodejs.org/api/test.html); src_nm_oauth_native — [OAuth for native apps](https://www.rfc-editor.org/rfc/rfc8252.html). These sources inform contract/test/auth boundaries; the acceptance examples above are original project-adaptable designs.
