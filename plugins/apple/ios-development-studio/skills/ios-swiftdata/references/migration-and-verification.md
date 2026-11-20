# Migration, CloudKit compatibility, and verification

## Inspect shipped schema history

Before editing a model used by shipped data, find schema versions, migration plans, container configurations and supported historical app versions. Record whether new fields are optional/defaulted, whether relationships change, and whether existing values need transformation. If the project has no explicit versioning, first establish how its current store was created and which upgrade routes must remain supported.

Select the smallest supported migration strategy for the change. Keep required old schema definitions available. Do not assume that a property rename, model split, inheritance change or altered uniqueness is automatically a harmless lightweight edit. Inspect generated metadata and official migration behavior where uncertainty matters.

Create representative old-store fixtures rather than relying solely on a fresh installation. Include sparse legacy rows, relationship edges, duplicates when historical data can contain them, and volume relevant to migration duration. Exercise direct upgrades from each supported shipped version, not only the immediately preceding schema.

## Protect data during failure

A store failing to open is a diagnostic event, not authorization to destroy it. Preserve the original state, capture a private structured error, and identify incompatible schema/configuration or migration logic. If the product supports recovery/export, implement it explicitly. Do not put an unconditional delete-and-recreate path in production container creation.

Temporary fixtures are disposable only inside a directory the test owns. Clean them predictably and retain a failing fixture only when useful and safe. Backups of a live store need a supported store-consistent method; a copied main file alone may miss journaled changes.

Use a fresh context or reopened container to distinguish current-context cache state from durable state. An insertion visible immediately through an in-memory object graph does not prove data survives process restart.

## CloudKit-backed models

Verify the actual CloudKit mode, entitlements, account state, container/environment and installed framework restrictions. Check uniqueness, optional/defaulted fields, inverses and deletion rules against that configuration. Do not assume a model valid for a local-only store is valid for cloud sync.

Design additive changes that older shipped clients can tolerate. Production schema restrictions do not mean every additive change is impossible; they do mean destructive/type-changing evolution needs particular scrutiny. Verify the exact deployment path and compatibility before remote mutation. A local model migration and a cloud schema deployment are distinct steps.

The UI must tolerate eventual delivery and account/network unavailability. Define conflict and retry behavior in terms of the domain. A successful local save does not prove export; an observed export does not prove import on another device. Use isolated authorized development resources for experiments, not production reset.

## Version-gated optimizations

Indexing, compound uniqueness, model inheritance and newer predicates can have distinct compiler and deployment requirements. Verify the macro/symbol in the installed SDK and target runtime. Add an availability path only when it is usable; silently raising minimum OS support is not a performance fix.

Measure the actual slow fetch/import before indexing or restructuring the model. Record dataset shape, predicate/order and elapsed/resource behavior. Indexes can change write/storage cost; new model features can complicate migration. Keep the optimization tied to a reproducible query or workload.

## Focused acceptance cases

| Scenario | Required check |
| --- | --- |
| Explicit save | Insert/change, save, reopen or refetch independently, assert durable values |
| Save failure | Force a realistic failure through a controlled seam, assert product error and no false success |
| Relationship deletion | Delete each relevant owner/reference, save and refetch graph, assert domain-correct survivors |
| Persistent predicate | Run on realistic store/runtime, include empty/optional/locale-sensitive cases that affect behavior |
| Identifier handoff | Save, transfer stable identity, resolve in destination context; handle a removed record |
| Migration | Open old-version fixture, validate transformed values and relationships, reopen again |
| Cloud compatibility | Check configuration/schema and observe authorized two-instance export/import behavior |
| Performance change | Compare same dataset/query before and after under the same environment |

Test the behavior that prompted the edit. Avoid tests that simply assert annotations, private helper names or implementation layout. Use the project's test framework; no arbitrary sleeps to wait for autosave or sync. Real cloud delivery tests need bounded observation and honest timeout/limitations, not a guaranteed-timing promise.

If the available host lacks Xcode, SwiftData runtime or devices, perform the useful static schema review and report the specific runtime checks still required. Do not call source inspection a successful migration.
