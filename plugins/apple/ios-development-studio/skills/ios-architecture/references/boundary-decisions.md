# Choose boundaries from the problem

## Establish the current contract

Trace one real user action from view/controller through state, effects, persistence or networking, then back to rendering. Record the types actually involved. Identify the owner of each mutable value and the lifetime of each task or subscription. Read the injected dependency at its construction site, not just its protocol. A view model with a protocol is not automatically isolated from a singleton used behind that protocol.

Ask only for facts that cannot be discovered and materially change the design. State an assumption when a bounded local implementation is possible. Do not require a comprehensive architecture questionnaire to fix one screen.

The first decision is the boundary to repair:

| Observed problem | Useful boundary | First small change |
| --- | --- | --- |
| A simple screen cannot express loading, empty, content and failure coherently | Presentation state | Make the valid states explicit in the current screen/model |
| Several overlapping intents can write conflicting state | Effect ownership/state transition | Identify intents, cancellation policy and accepted result identity |
| Business rules depend directly on transport/database APIs | Domain/infrastructure | Extract the behavior-bearing dependency needed by this feature |
| Screens repeat push/present/deep-link decisions | Navigation flow | Give the flow one route owner and explicit destinations |
| Stream ordering, debounce or switching behavior is the issue | Event pipeline | Repair the existing Combine/Rx/async pipeline and test its ordering |
| A large module has unclear team or dependency ownership | Module boundary | Separate the smallest coherent capability before changing all patterns |

## Fit existing patterns deliberately

These options express trade-offs, not an order of superiority:

- **Screen model/MVVM:** useful for ordinary screen state and bindings. Keep business effects behind injected boundaries when the feature needs them. A separate view model for a stateless view is optional.
- **Reducer/MVI:** useful when explicit state transitions and effect outcomes simplify overlapping intents. Enumerate actions and effect identities; a single giant reducer can still hide poor ownership.
- **TCA:** use the resolved library's API when the project already uses it or the task explicitly adopts it. TestStore, dependency and cancellation APIs vary by version. Do not add the dependency for an unrelated cleanup.
- **Clean/layered boundaries:** useful when business behavior must outlive or replace infrastructure. Keep domain types free of storage/transport concerns when that separation earns its cost. Avoid pass-through use-case/protocol layers that add no behavior or substitution need.
- **MVP/VIPER:** preserve these in working UIKit modules. Give rendering, interaction, business rules and routing explicit owners. Do not apply SwiftUI observation wrappers to UIKit presenters by habit.
- **Coordinator/router:** useful for a distinct flow concern in SwiftUI or UIKit. A route contains navigation state; the owner handles presentation and completion. It should not become the owner of every business rule.
- **Reactive composition:** use the project's existing stream tools when the behavior is a stream. Define subscription lifetime, scheduler/isolation and error/retry behavior. Reactive composition can live inside a presentation or domain boundary.

If the user names a pattern, start there. Explain a concrete mismatch only when it conflicts with required behavior, deployment support or existing dependencies. A disagreement over style does not justify a migration.

## State and observation

Choose ownership before choosing a wrapper. For SwiftUI, determine whether a view creates a model, borrows it, receives a binding, or reads an environment dependency. Use Observation or ObservableObject according to deployment support and the project's interoperation needs. Keep a single authoritative value; a copied local state that drifts from the model needs a documented edit/commit policy.

In UIKit, identify how rendering receives changes and how observations/subscriptions end. In mixed code, inspect hosting/controller lifetime and ensure the same model instance crosses the adapter when shared state is intended.

Navigation state should support the actual user behavior: selection, pushed path, sheet, authentication prerequisite, deep link or restored destination. Do not force every app to serialize its entire navigation graph. Do test invalid or unauthorized destinations and completion of child flows.

## Decision record

For a meaningful structural change, leave a compact record: observed problem; affected boundary; selected pattern and existing convention; alternative rejected and its specific cost; state/effect/dependency ownership; migration step; behavioral verification. For a small repair, a few sentences in the change description suffice. Keep this record connected to the shipped implementation.
