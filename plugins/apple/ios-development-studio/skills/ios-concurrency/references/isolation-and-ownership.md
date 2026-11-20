# Isolation and task ownership

## Read settings before annotations

The compiler version, Swift language mode, deployment availability, default actor isolation, and enabled upcoming features answer different questions. Inspect the selected target's resolved settings where tools permit. Two targets can compile the same-looking code under different isolation assumptions. A dependency's behavior does not follow from the app target's settings.

For recent nonisolated async behavior, verify the relevant language feature and generated interface. Do not assume every plain async helper leaves the caller's actor, or that a compiler version alone opts every module into caller-isolation semantics. Use explicit API contracts supported by the actual compiler. Treat newer attributes and task APIs as conditional until verified in the installed toolchain.

An async URLSession operation can suspend without blocking the main actor. A large synchronous decode/transform after that suspension can still monopolize the actor on which it executes. Trace the expensive segment rather than moving the entire function to a detached task by habit.

## Make a boundary map

For a problematic call, identify:

- the caller's isolation and the callee's declared/inferred isolation;
- each captured argument and returned value, including mutable reference internals;
- the owner of mutable state and every path that accesses it;
- whether the operation is structured under its caller or has an independent owner;
- what can change while an await is suspended;
- whether cancellation, invalidation or a new intent makes the result obsolete.

Compiler diagnostics are evidence of a boundary the compiler cannot prove safe. Read the full message and notes. Resolve whether the intended contract is actor-local work, immutable transfer, ownership transfer, or synchronized shared access. Do not add a Sendable conformance merely because a type crosses an API.

## Select the protection mechanism

| Requirement | Candidate mechanism | Review question |
| --- | --- | --- |
| UI state belongs to the UI executor | Main-actor isolation | Are callers and lifecycle operations consistently isolated? |
| Independent mutable service state needs serialized access | Actor | What assumptions must be revalidated after suspension? |
| Data is a snapshot passed between tasks | Immutable Sendable value | Are nested values and references safe, not merely declared safe? |
| Legacy synchronous state is already protected | Reviewed lock/queue | Are all paths covered, with no lock held across await? |
| Persistence object belongs to its context | Identifier or snapshot transfer | Is the identifier stable and refetched in the destination context? |

Actors serialize isolated execution, not whole async methods. For a cache, two callers may both observe a miss before a download completes. An in-flight operation map can coalesce work, but must define who cancels a shared request and what invalidation does to late results. A force unwrap deserves review, but do not invent an actor interleaving between two synchronous statements with no suspension.

## Choose task structure from lifetime

Prefer an awaited async function, async let, or task group when the caller owns the work. Bound concurrency according to the resource: launching one child per item can overwhelm memory, network or a service even when structurally correct. Make child error/partial-result policy explicit.

An unstructured Task is appropriate when an identified owner must start work from a synchronous boundary. Store its handle when later cancellation/completion matters. Define replacement and teardown. A Task created inside another task does not become a structured child merely because it appears lexically inside it.

Task.detached discards inherited task context and changes isolation/capture requirements. Use it only when independent execution is the intended contract and captured values/results are safe. It is not a general Sendable-diagnostic escape hatch. Use a verified offloading API or dedicated service boundary when CPU-heavy work must leave UI isolation.

## Unsafe and legacy boundaries

Keep existing queues, locks and callbacks when they are the correct framework contract. Migrate only the required seam. Never block a cooperative executor with a semaphore waiting for async work. Never hold a synchronous lock across suspension.

An unchecked conformance requires a documented synchronization invariant and review of every mutable access; it cannot repair a context-confined managed object. A preconcurrency import changes checking of a legacy boundary rather than proving safety. Record any deliberately unresolved legacy limitation and test the behavior it can affect.
