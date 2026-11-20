# A durable local outbox with an explicit acknowledgement contract

## Inputs and authority

Inspect the app's existing local store, pending-operation representation, backend endpoint, account/session lifecycle and refresh process. Determine whether a user action is optimistic, must wait for a server decision, or is prohibited offline. Do not promise offline acceptance for operations whose domain requires current server authorization or availability.

Define an operation envelope with stable operation identity, account scope, operation kind, payload version and the fields needed for a domain precondition. The server derives actual authority from authenticated state; a stored account identifier only helps prevent accidental cross-account replay. Keep secrets out of the envelope unless the existing storage and lifecycle explicitly require them.

## Persist intent before sending

When the product uses optimistic local state, commit that local change and its outbox record in one local transaction. Otherwise a crash can display an edit with no pending intent or enqueue an edit the UI never committed. Use the selected persistence engine's actual transaction/confinement mechanisms; wrapping a managed object in an actor does not make it a cross-context snapshot.

Represent states such as pending, in-flight, unknown outcome, acknowledged and rejected/needs repair. “Unknown” is essential after a timeout: the server may already have committed. Persist attempt/recovery metadata intentionally, but do not treat attempt count or a random request tracing ID as the operation's domain identity.

| Event | Durable local outcome | Next action |
| --- | --- | --- |
| User commits offline edit | Local state and pending operation agree | Send when an appropriate authorized opportunity occurs |
| Network fails before result is known | Operation remains recoverable | Retry/reconcile with the same identity |
| Server confirms committed result | Authoritative result recorded and pending intent acknowledged | Reconcile local projection and advance safe progress |
| Server only admits async work | Admission receipt stored | Query/reconcile according to the explicit completion contract |
| Permanent domain/auth rejection | Intent retained or transformed under product policy | Present repair/re-auth/conflict behavior; no infinite blind retry |

## Server admission and commit

Bind duplicate handling to authenticated account, operation kind and stable operation ID. Persist a canonical request fingerprint so reuse with different intent is detected. Protect the authoritative mutation and its recorded operation result with a suitable database transaction/constraint. A process-local map or single worker lock cannot provide this boundary across restarts and replicas.

If the operation creates external work, record a durable outbox/job admission alongside the domain change. The worker applies its own durable side-effect identity. Do not hold the database transaction open while waiting for a remote provider and call that an atomic distributed commit.

Return a stable result or operation receipt that the client can look up safely after a lost response. A duplicate of a completed operation should reconcile the existing logical result according to the contract. A duplicate still being processed needs a defined pending outcome. An altered payload under the same identity must not silently become a new write.

## Acknowledge only the promised outcome

Remove or mark a local pending operation complete only after the server outcome required by the protocol is known. A `200` response may mean committed work or just an adapter's own envelope; a `202` commonly represents admission rather than completion. Read the actual endpoint contract instead of using status alone as a universal rule.

Apply acknowledgement and local projection/cursor changes together when the store supports it. After a crash, reconcile by operation identity before sending under a new identity. Never clear the entire outbox because one request succeeds. Preserve order where domain preconditions require it, but avoid making an unrelated poisoned operation block every account/entity forever.

## Verification matrix

Test crash after local commit, crash before send, lost response after server commit, server restart, duplicate admission from another instance, altered duplicate payload and interruption during local acknowledgement. Assert both the authoritative domain result and the remaining outbox state. Use controlled completion points so each failure occurs at the intended boundary.

Also test sign-out/account switch while work is in flight. An old account's request or response must not modify a new account's local projection. Decide the retention/recovery policy for unsent edits explicitly; do not delete them merely to simplify logout handling.

## Evidence and version cautions

Sources `src_backend_repo_073` and `src_backend_repo_074` expose [PowerSync connector responsibilities](https://github.com/powersync-ja/powersync-swift/blob/b77dc2f00366db9540f2ecd3903cfefb63fc29e8/Sources/PowerSync/Protocol/PowerSyncBackendConnector.swift) and [CRUD completion](https://github.com/powersync-ja/powersync-swift/blob/b77dc2f00366db9540f2ecd3903cfefb63fc29e8/Sources/PowerSync/Protocol/db/CrudTransaction.swift). `src_nm_bullmq_idempotent` is the [idempotent job guide](https://docs.bullmq.io/patterns/idempotent-jobs). This card is original provider-neutral protocol guidance, not a requirement to adopt either product. See the [source catalog](../../research/sources/sources.jsonl) and verify the actual adapter's acknowledgement semantics.
