# Context confinement, operations, and visibility

## Map the store before the object graph

Inspect the selected model/configuration and every persistent-store description. The app can use multiple stores with different options. Determine when loading finishes, where failures surface, and whether any fetch/save can run before the necessary store is ready. Do not print store contents or production account data during discovery.

The persistent container, coordinator, contexts and managed objects have distinct roles. Identify each context's queue/confinement and intended workload. A view context commonly serves UI; an import/background context owns heavy work. Use the framework's context execution API for the actual context rather than assuming the current task happens to be on the correct executor.

## Pass identity or snapshots

Managed objects belong to their context. Do not pass them to another context or independently executing task as a shortcut. A Sendable annotation cannot change that ownership.

For a destination that must mutate/refetch, pass a permanent saved object ID and resolve it inside the destination context. Handle deletion or unavailable objects explicitly; a fault-returning lookup is not proof the row still exists. Temporary IDs are not an inter-context persistence contract. If the destination needs display-only information, build an immutable snapshot while executing in the source context.

Background helpers need a constrained return contract. A generic method returning arbitrary T can accidentally leak a managed object even when its closure is Sendable. Prefer narrow operations returning IDs, counts, domain values or snapshots. Verify the actual SDK's sendability annotations and compiler mode rather than assuming every reference wrapper is transferable.

An actor wrapping Core Data does not replace context confinement. An ordinary actor executor and a context queue are different mechanisms. Use context.perform at the seam unless a reviewed custom-executor design is already part of the project and its complexity is justified.

## Save and conflict semantics

Define what “saved” means for the affected context hierarchy and store. A child context save can push changes to a parent without durably committing them to disk. Ensure the required parent save occurs at the product's durability boundary.

Inspect validation, uniqueness and merge policy before changing them. An object-trump policy may hide a business conflict; a store-trump policy may discard an edit the UI still shows. Resolve conflicts according to ownership and user expectations. Surface a meaningful error or recoverable state while keeping private diagnostics available.

Do not swallow save errors with try? or replace them with an unconditional success UI. For cancellation during import, decide whether partial progress is committed, rolled back or resumable. A context reset invalidates objects; use it only within an intentionally owned lifecycle.

## Fetch according to the question

Choose predicate, sort, limit, batching, prefetch and selected properties based on actual access. Use counts/aggregates when rows are unnecessary. Identify accidental relationship faulting or repeated fetches before optimizing blindly. A fetch limit does not replace a stable pagination policy when the product needs paging.

For UI lists, check the fetched-results/query observation path as well as the database operation. An operation can succeed while another context retains stale registered objects. Test what the user sees after merge, including deletions.

## Batch operations and merges

Batch operations can bypass ordinary object graph validation, callbacks and change tracking. Confirm store support and relationship implications. A batch delete is not equivalent to deleting every managed object through context APIs.

Select one proven visibility path appropriate to the operation and processes:

- returned affected object IDs merged into the relevant contexts, when the operation provides sufficient IDs and the app owns those contexts;
- persistent history consumption with durable tokens and transaction handling, useful for changes from extensions/processes, batch work and cloud integration;
- an established project pipeline that demonstrably provides equivalent visibility.

Automatic parent merges do not imply every SQL-level batch change will appear. Conversely, persistent history is not mandatory for every valid ID-merge design. Verify the selected path end to end. With history, identify the token owner, store identity, transaction authors to exclude, cleanup policy, and how readers recover when history expires or a store is replaced.

## Diagnostic order

Wrong-context exceptions: inspect object provenance and execution seam. Stale lists: inspect merge/observation path. Constraint errors: inspect model and merge policy. Memory growth: measure fetch volume, registered objects, faults and retained snapshots. Do not begin each investigation with a store reset or a new architecture.
