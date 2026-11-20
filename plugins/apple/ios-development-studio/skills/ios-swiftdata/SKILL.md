---
name: ios-swiftdata
description: "Use when implementing or debugging SwiftData models, containers and contexts, @Query or FetchDescriptor behavior, relationships, persistence durability, schema migration, indexing, or SwiftData CloudKit compatibility. Do not choose SwiftData for an existing Core Data app unless migration is requested."
---

# SwiftData

Read the [shared operating contract](../ios-development/references/operating-contract.md). Choose the persistence engine and API availability from the project, not source-author preferences.

## Workflow

1. Inspect model types, schema/versioning, ModelContainer configuration, context ownership, CloudKit use, target OS and installed SDK. Capture the failing predicate/save/migration and a minimal representative dataset.
2. Use [models, queries, and ownership](references/models-queries-and-ownership.md) to define relationship semantics, stable identity, query support and isolation. Preserve existing domain behavior.
3. For schema changes or cloud-backed stores, use [migration and verification](references/migration-and-verification.md). Establish supported upgrade paths and additive cloud compatibility before editing.
4. Implement the smallest fix with explicit durability/error behavior. Treat successful compilation and successful persistent-store execution as separate checks.
5. Verify inserts/updates/deletions through a fresh context or reopen where durability matters. Add runtime predicate, relationship and migration checks on the supported OS/store. Measure before adding indexes or changing fetch shape.

## Boundaries

Do not pass ModelContext or live model instances across arbitrary isolation boundaries. Do not fix a load/migration failure by deleting the user's store. New macros, model inheritance and query expressions require SDK/deployment verification. Choose delete rules from ownership rather than defaulting to cascade.

## Completion

Report model/query changes, save/isolation and migration implications, executed checks and unresolved runtime availability. Preserve shipped data and versioned schemas.

## Provenance

Original workflow informed by supplied `SwiftData-Agent-Skill-main.zip` (`swiftdata-pro` core rules, predicates, CloudKit, indexing and inheritance references), plus persistence/concurrency audits. See the [source map](../../docs/source-map.md). The original author's claimed user preferences are excluded.
