# Models, persistent queries, and context ownership

## Establish the actual model contract

Read the complete model graph, container schema/configuration and call sites. A model property can participate in storage, derived presentation, relationships, uniqueness or external binary storage; those roles have different constraints. Verify macros and supported property types in the installed SDK rather than treating an uploaded list as permanent framework law.

Choose identifiers from the product and persistence lifecycles. A newly inserted object's persistent identity may change when saved. Do not infer its stability by parsing a private textual representation. Save before relying on persistent identity across a durable handoff, and handle a refetch that no longer finds the object.

Use a computed property for cheap derived data when appropriate. A transient value is not persisted and is not automatically a supported persistent-query expression. Explicitly decide whether a derived value must be stored, recomputed, or backfilled during migration. Avoid changing storage shape solely to satisfy a convenient UI query without considering upgrade cost.

## Relationships encode ownership

For each relationship, record cardinality, optionality, inverse, ownership and deletion behavior. A parent may own a child exclusively, share it with other parents, or merely reference an independently existing entity. Cascade can be correct for exclusive ownership and destructive for shared records. Nullify can be correct for a reference and invalid for a domain invariant that requires the connection.

Verify inverses and macro expansion if the compiler reports a cycle or an inferred relationship behaves unexpectedly. Do not add duplicate annotations blindly. Check CloudKit restrictions separately when enabled. Test deleting each relevant side and reloading the graph; visual disappearance in the current context is insufficient proof of the resulting persistent relationships.

## Context and actor ownership

ModelContext and live model instances belong to their isolation/lifecycle. Perform operations on their owning context. Cross a boundary with a saved identifier or an immutable Sendable snapshot, then resolve it in the destination context. A general-purpose actor holding an object does not retroactively make that object safe to share.

When using a model actor or background service, inspect how it is constructed and how its context/executor is assigned. Do not assume an actor was offloaded merely because its type is an actor. Separate heavy synchronous work from UI work using APIs supported by the actual compiler and project configuration.

Use @Query for a SwiftUI observation boundary that the framework supports. A service/repository ordinarily performs explicit context fetches; attaching a view-oriented wrapper to an arbitrary class does not establish observation. If using fetched snapshots, define how changes cause refresh and who owns that refresh.

## Query support has two stages

Predicate construction/macro expansion can succeed while a persistent backend rejects the expression. Exercise the expression against a realistic store and supported runtime. Focus on stored fields, supported relationship traversal and actual translation behavior. Computed/transient/opaque Codable structures may not provide the persistent expression the query requires.

Do not treat every source warning about prefix/suffix, empty collections or string normalization as a timeless crash rule. Reproduce the specific expression and alternatives on the affected OS/store. Choose search behavior that matches the product's locale/case/diacritic semantics, then test those cases. A rewrite that merely compiles can change user-visible matching.

Fetch counts when only a count is needed; fetch models when their data is needed. A one-time count does not become live observation automatically. Consider limits, sorting, prefetching and fetched properties based on measured access. Stable pagination requires more than a limit.

## Durability and errors

Autosave policy is not a substitute for a clear durability boundary. When the product promises an edit is committed, explicitly save as needed, handle failure, and verify the persisted result. Decide what happens to UI state if save fails. Do not swallow the error and show success.

Define transaction/partial-progress behavior for imports or multiple related mutations. Cancellation must not accidentally leave a user-visible operation reported as complete while important records are unsaved. Preserve context ownership when reporting errors back to UI.
