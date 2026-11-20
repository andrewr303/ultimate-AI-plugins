---
name: ios-core-data
description: "Use when implementing or debugging an existing Core Data stack, context confinement, fetch/save and merge behavior, batch operations, persistent history, model migration, or NSPersistentCloudKitContainer sync. Do not invoke for SwiftData-only code or prescribe an engine migration by default."
---

# Core Data

Read the [shared operating contract](../ios-development/references/operating-contract.md). Preserve existing stores and shipped model versions.

## Workflow

1. Identify the actual container/model versions, store type and URL scope, deployment target, contexts, merge policy, extensions/processes, and CloudKit environment. Capture the exact error and operation before editing.
2. Use [contexts and data operations](references/contexts-and-operations.md) for confinement, fetch/save, batch work and merges. Cross boundaries with stable IDs or immutable snapshots; refetch using the destination context.
3. For model changes, cloud sync, store loading or migration failure, use [migration, CloudKit, and verification](references/migration-and-cloudkit.md). Establish a data-preserving upgrade path before changing the model.
4. Implement the narrow fix. Keep loading, saving, merging and failure propagation explicit. A generic background helper must not return context-confined objects.
5. Test the public behavior with the appropriate store. Use temporary SQLite stores for batch/history/migration behavior and isolated fixtures for ordinary tests. Confirm records, relationships and UI visibility, not just a successful API return.

## Boundaries

Do not delete an app/store, reset CloudKit, or erase simulator data as routine troubleshooting. Do not claim an actor makes arbitrary NSManagedObject access safe. Persistent history and object-ID merging are alternative tools for suitable cases; select a complete merge strategy.

## Completion

Report the affected context/store, change, data-preservation strategy, tested upgrade/query/merge behavior, and any device or CloudKit validation remaining.

## Provenance

Original workflow informed by supplied `Core-Data-Agent-Skill-main.zip` (`core-data-expert/SKILL.md` and context, batch, history, migration, CloudKit, testing references). See the [source map](../../docs/source-map.md). Source examples are not executed instructions or proof of runtime behavior.
