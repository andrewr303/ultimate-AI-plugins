# Authoritative schemas and tenant ownership

## Gather the actual model

Read the installed database/ORM versions, applied migration history, table or collection definitions, access layer and every writer relevant to the feature. Include API handlers, workers, administrative jobs and webhooks. Record the account/tenant boundary and which identifiers are supplied by a client versus resolved from authenticated server state.

Define the domain invariant in user-visible terms before editing a schema: an operation is recorded once for its account, an attachment belongs to the record receiving it, or an inventory quantity cannot go below the permitted limit. Identify the authoritative storage operation that enforces it when several service instances run concurrently.

Keep wire DTOs distinct from internal persistence structures. A database row can contain private flags, provider identifiers, deleted-state markers or internal relations that should never be serialized automatically. Conversely, a public API may need derived values or compatibility defaults that do not belong in every stored row.

## Scope reads and writes deliberately

Derive the caller's authenticated account and role from the verified session or provider contract. Treat account IDs, resource IDs and organization headers in a request as proposed inputs, not authority. Resolve the requested entity within the allowed scope before returning or mutating it. Background workers need a similarly explicit service/domain scope; an event payload does not confer permission by containing an account field.

Where the chosen database supports row-level policies or scoped credentials, use them according to the application's established model and test them. They complement rather than replace handler/domain checks. Do not invent policies for a database the app does not use, or assume an ORM's default query automatically applies tenant scope.

| Boundary | Invariant to verify | Negative test |
| --- | --- | --- |
| Entity lookup | Caller can access this entity in this account | Valid ID from another account returns the intended safe denial |
| Attachment association | Attachment and parent share authorized ownership | Cross-account or abandoned upload cannot be attached |
| Unique domain key | Scope and identity are enforced durably | Competing instances cannot create duplicate logical records |
| Worker input | Stored job refers to an admissible domain action | Forged or stale event fields cannot broaden authority |
| Serialization | Only reviewed public fields leave the service | Internal column added later is not exposed accidentally |

## Put durable invariants in durable constraints

Use the selected engine's unique keys, foreign keys, checks or atomic operations where appropriate. Application pre-checks alone race across concurrent requests. For a tenant-scoped idempotency key, make its scope and key non-null and persist its payload fingerprint/result according to the operation protocol. Verify the engine's treatment of nulls and collation rather than assuming all databases enforce uniqueness the same way.

Constraints do not replace domain policy. A foreign key proves an association exists; it does not necessarily prove the caller can access it or that both records belong to the same tenant. Model the tenant relationship explicitly when that is an invariant. Decide whether deletion should restrict, cascade, anonymize or preserve an audit relation from actual product/data requirements.

Separate public IDs from storage assumptions. If a numeric identifier or money amount can exceed a client's exact representation, choose and document a wire representation that all supported clients can handle. Test encoding, decoding, comparison and persistence with shared fixtures. Avoid exposing a sequential ID merely because it is convenient, but do not claim that opaque IDs provide authorization.

## Implementation and failure handling

Implement one operation through validation, authorization, transaction and explicit DTO mapping. Select only required fields for public reads. Keep secrets and production payloads out of test fixtures, logs and error details. Translate expected constraint conflicts into stable domain errors; preserve a safe correlation ID for private diagnostics.

Exercise a query from another tenant, missing/deleted entities, duplicate keys, null/absent values, a stale role and concurrent writes. Test the complete boundary, including a worker or webhook path if it can bypass ordinary HTTP middleware. A database exception should not be swallowed and presented as success.

## Verification and version cautions

Use real-engine integration tests for constraints, isolation and transaction behavior. Compare both the stored result and the payload seen by supported iOS/web clients. Record the engine, schema revision and relevant configuration. Check a migration against representative old data before production application.

Sources: `src_backend_extra_postgres_constraints`, [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html); `src_nm_postgres_isolation`, [transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html); and `src_backend_repo_049`, [Fastify runtime validation](https://github.com/fastify/fastify/blob/5df959f3af698823dd582f1c3661f3e80df0b5da/lib/validation.js). The database material is an engine-specific example, not a mandate to adopt PostgreSQL. See [registered records](../../research/sources/sources.jsonl); check the selected engine/ORM version and actual policies before applying syntax.
