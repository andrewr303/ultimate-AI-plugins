# Evolve independently released clients safely

## Establish the compatibility window

List supported app versions, extensions, web clients, service versions and stored snapshots. Mobile and widget code can remain deployed long after a server changes. Record which request/response shapes and domain semantics the backend must continue to accept. A schema version label is useful only when the actual behavior behind it is defined and tested.

For a change, capture the before/after contract: required and optional fields, nullability, enum behavior, pagination, error codes, authentication, authorization and side effects. Identify the rollback direction. Reverting server source may not reverse a database migration, an emitted event, a completed external payment or a new snapshot already written by a client.

## Stage changes as compatible steps

Prefer an expand/adopt/contract sequence when a stored or wire representation changes. Introduce compatible server handling and storage first, verify it with old fixtures, adopt it in clients, measure the remaining old usage where permitted, and retire the compatibility path only under the product's actual support policy. Do not silently invent a retirement deadline or telemetry program.

Keep a single authority for API description and compatibility fixtures. Regenerate language-specific bindings with pinned tooling, review the diff and run semantic checks. A textual generated diff is not a complete breaking-change detector: a default, validation option, authorization rule or ordering guarantee can change without an obvious type change.

| Change | Questions before deployment |
| --- | --- |
| Add response field | Does the oldest supported decoder ignore it? Is sensitive data now serialized? |
| Add required request field | Can old clients still call the route? Is a meaningful server default possible? |
| Add enum value | Do clients have an explicit unknown/fallback path? |
| Change ID/date/number representation | Are sorting, precision, equality and persistence still correct across languages? |
| Change retry/error status | Could a client repeat a write or stop a recoverable sync operation? |
| Change storage or event schema | Can old workers, extensions and snapshots still interpret it? |

## Environments without duplicated secrets

Map each environment to its backend URL, data store, external-provider environment, app bundle identity and test credentials. Use the project's established configuration mechanism to derive non-secret client endpoints. Keep server signing keys and privileged credentials in the server's configured secret store, never in a generated Swift configuration file.

Treat environment selection as an explicit value in the build/release process. Verify the actual built artifact's bundle identity and endpoint behavior rather than relying on an Xcode scheme's name or a dashboard label. A development push token, sandbox purchase event or test webhook must not accidentally be routed into a production account boundary.

For local development, distinguish simulator loopback, a physical device's network path, container networking and remote preview URLs. Use an intentionally trusted local certificate or the app's documented development arrangement; do not solve connectivity by globally disabling TLS verification. Avoid exposing a local backend or forwarding a privileged port to the public internet merely for convenience.

## Deployment and recovery

Define the observable ready state for API, database and background workers. Deploy changes in a compatible order, verify the intended environment and run a bounded smoke operation that does not mutate real customer data. A successful image build or upload is not proof that the new route, worker or client configuration is live.

After a timeout or unclear deployment result, inspect the platform's current state before retrying. Record exact service version, migration status and relevant receipts without secrets. Preserve a recovery path for clients whose operation committed before they lost the response: durable operation lookup is preferable to telling them to submit the same action under a new identity.

## Verification checklist

- Old supported request fixtures still produce the promised semantics.
- New client bindings compile against the selected app targets when Apple tools are available.
- Unknown enum, absent/null, date precision and identifier cases have explicit outcomes.
- API and worker versions can overlap for the expected rollout window.
- Schema changes are tested on a copy of relevant prior data, including repeated startup.
- The selected artifact, backend environment and provider sandbox/production identities agree.
- Recovery and rollback describe data/events as well as source code.

## Evidence and version cautions

`src_nm_openapi_spec` is the [OpenAPI specification](https://spec.openapis.org/oas/v3.1.1.html); `src_nm_prisma_migrate` is the [Prisma development/production migration guide](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production); `src_nm_postgres_alter` is the [PostgreSQL ALTER TABLE reference](https://www.postgresql.org/docs/current/sql-altertable.html). These inform original compatibility and rollout guidance, not a provider-independent migration command. See the [source catalog](../../research/sources/sources.jsonl). Resolve the actual generator, ORM, database and hosting versions before applying a recipe; no deployment was executed by this reference review.
