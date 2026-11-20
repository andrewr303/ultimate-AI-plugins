# Ownership across the app, extensions and server

## Make one authority explicit for each concern

Provider neutrality reduces duplicated management when the same domain and wire contract serve several clients. It does not require a monorepo or make all providers interchangeable. Identify the current authority and change it only for a demonstrated requirement. Different processes may read projections of the same domain state without sharing credentials, storage lifetimes or release schedules.

| Concern | Authoritative owner and boundary |
| --- | --- |
| Wire shape | Versioned contract plus the actual server behavior; generated clients are derived consumers |
| Identity/session | Chosen authorization service and server verification; client storage is a separate decision |
| Entity/tenant access | Server/domain authorization after parsing the credential |
| Domain mutation | Durable transaction and constraints in the owning service/store |
| Retry identity | Explicit operation/event key with a defined scope, retention and outcome policy |
| Main-app state | Native lifecycle owner with cancellation and stale-result protection |
| Widget data | Small versioned projection, useful when stale or unavailable |
| Intent action | Validated domain adapter with its execution and authentication context |
| Live Activity | Bounded presentation state and its own update/token lifecycle |
| Background work | Supported system opportunity or durable server worker, not an indefinite client task |

The server holds provider signing keys and performs privileged checks. An extension must not inherit broad server credentials merely because it can access shared app-group data. A bearer token need not be a JWT; preserve the chosen token format and verifier. Client or intent validation improves interaction but does not replace server authorization.

## Preserve native execution boundaries

App groups provide an intentional sharing capability, not universal process memory or automatic concurrent-store safety. Define the format/version, writer, atomic publication method, read fallback and account association of each shared snapshot. Protect credentials according to the actual access group and device-lock needs. Clear or retire prior-account projections deliberately when switching accounts.

Widgets and intents may operate when the main app is absent. Live Activity updates and APNs deliveries do not prove that the app ran or committed a domain action. The system can decline or defer background opportunities. Keep stale timestamps, denied access, offline data and expiration visible in the state model rather than reporting success prematurely.

## Handoff only a distinct concern

Select one primary skill for the user's actual defect or feature. Add a supporting owner when another boundary needs work. A wrong avatar after account switching can involve cache identity and domain authorization; it does not automatically justify a service migration. A widget that shows stale data may need snapshot publication or lifecycle diagnosis before an APNs change.

A useful handoff contains the accepted behavior, exact code/target, current state, known contract version and evidence already collected. State who owns the next mutation and what result will resume the original flow. Carry target identity and existing authorization forward; do not restart discovery or repeat permission questions after every specialist transition.

## Verify ownership failures

Test a request with valid identity but wrong entity ownership, a deleted entity reached from an old widget link, account change during a fetch, duplicate intent execution and a worker crash after a durable effect. Assert current domain state and exposed information, not merely a callback count. Record which native, service and provider paths actually ran.

Sources: src_backend_repo_040 — [Swift client transport seam](https://github.com/apple/swift-openapi-runtime/blob/76720b809fa0d4c68d7518db81c75d9fb371f169/Sources/OpenAPIRuntime/Interface/ClientTransport.swift); src_backend_apple_025 — [App groups](https://developer.apple.com/documentation/xcode/configuring-app-groups); src_backend_apple_007 — [App Intents](https://developer.apple.com/documentation/appintents/appintent); src_backend_apple_011 — [Live Activity presentation](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities).
