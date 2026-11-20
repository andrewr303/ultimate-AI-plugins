# Data-preserving migration, CloudKit, and verification

## Store loading is a multi-result contract

Read the framework's actual callback contract. Loading can report separately for multiple store descriptions. If the project adds an async wrapper, coordinate expected per-store completion and resolve the aggregate exactly once, including errors. A checked continuation resumed unconditionally in each callback is unsafe for multiple stores.

Do not mark the whole stack ready because the first store loaded. Decide whether partial loading is a supported product state; if it is not, fail the initialization path coherently and preserve recoverable diagnostics. Test a failed secondary store as well as the single-store happy path.

## Plan migrations before modifying a shipped model

Identify every supported shipped model version, store configuration and upgrade path. Keep source models required for inference or mappings. List intended transformations: rename, optional/default change, relationship change, entity split/merge, or data-derived backfill. Use renaming identifiers when applicable rather than accidentally creating unrelated fields.

Choose a lightweight, staged, mapping/custom or other supported migration strategy based on the actual change and available OS/SDK. Do not assume that every schema edit is inferable. Do not raise the deployment target merely to use a newer migration convenience without a product requirement.

Establish a realistic fixture for each supported upgrade route. Include null/missing legacy values, relationship edges, duplicate/conflicting data, and a sufficiently representative data volume. Record whether the migration is transactional, restartable, and able to report failure without discarding the original store. Keep recovery/export plans scoped to user-authorized data access.

Never implement “on load failure, delete database and try again” as a silent production repair. Development fixtures can be recreated only when they are explicitly disposable and confined to the test directory. If a migration needs a backup/copy, use a supported store-safe method; copying only a live SQLite main file can omit journal state.

## CloudKit is an additional compatibility boundary

Identify the actual iCloud container, entitlement, account availability, environment and persistent-store configuration. Development and production are separate states. A working local store does not prove cloud export/import works.

Inspect the installed framework's schema limitations before changing constraints, optionality, inverses or deletion behavior. Preserve additive compatibility with older shipped clients. Production schema evolution is restricted; do not describe every production change as impossible, and do not assume destructive field/type changes can be deployed. Verify the specific allowed additive change through the relevant Apple tooling/documentation.

Do not reset an existing cloud container or delete/reinstall a user's app to diagnose mismatch. Capture the failing event/error and compare model configuration, deployed schema and environment. Use a separate disposable development container or fixture when an experiment genuinely needs reset.

Model sync as eventual and failure-prone. The UI should cope with account unavailable, offline, delayed imports, retries and partial records according to product needs. Export success is not proof another device imported the expected state. Notification callbacks need lifetime management and should not be assumed to arrive on UI isolation.

## Verification matrix

| Change | Small meaningful check | Integration evidence |
| --- | --- | --- |
| Fetch/predicate | Seed known records, assert correct results/order/limits | UI observes intended records |
| Save/merge policy | Simulate conflicting edits in distinct contexts | Expected durable value and visible resolution |
| Object-ID handoff | Save, transfer ID, resolve in destination; handle deletion | No context-confined instance escapes |
| Batch update/delete | Temporary SQLite fixture, inspect affected IDs/rows | Destination context/list sees update without restart |
| Persistent history | Generate relevant transaction, consume and persist token | No missed/duplicated effects after restart |
| Migration | Open an old SQLite fixture with new model/strategy | Data and relationships survive reopen/restart |
| Multi-store load | Arrange two store outcomes, including failure | Readiness and error resolve once with correct state |
| Cloud sync | Controlled authorized account/container and two instances/devices | Export and import observed with intended conflict behavior |

Use in-memory stores for ordinary object behavior when appropriate; they do not prove SQLite-specific migration, batching or history behavior. Await store readiness in setup. Isolate tests by fixture directory and clean only files the test owns. Preserve a failed migration fixture for diagnosis when appropriate without exposing user data.

When macOS, devices or authorized cloud resources are absent, report the checks still required. A static model review is useful evidence but cannot certify migration or CloudKit runtime success.
