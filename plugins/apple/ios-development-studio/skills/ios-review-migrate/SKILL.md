---
name: ios-review-migrate
description: Use for scoped iOS/Swift code reviews, SDK or language/API upgrades, persistence migrations, and incremental architecture refactors. Do not expand a local bug fix into a repository rewrite or apply migration instructions solely because an uploaded guide calls them latest.
---

# iOS review and migration

Read [the operating contract](../ios-development/references/operating-contract.md). Preserve the user's requested mode: review produces findings; an authorized fix/migration includes implementation and verification.

1. Resolve the requested diff/files/feature, current baseline, relevant target/configuration and acceptance behavior. Inspect existing uncommitted changes before modifying files.
2. For review, use [the evidence checklist](references/review-checklist.md). Read surrounding ownership and call sites, then report concrete regressions or risks with location, trigger, impact and confidence. Avoid generic preference findings.
3. For migration, establish before/after contracts and a staged [migration plan](references/migration-playbook.md). Verify compiler/SDK/API semantics and supported fallbacks. Route persistence work to the engine already in use.
4. Keep edits additive or narrow where possible. Preserve external interfaces, release identity, data and lockfiles unless the change actually needs them. Complete independent authorized steps while a platform prerequisite is unavailable.
5. Verify the changed behavior and required project checks. Record unavailable Apple runtime validation explicitly. Do not label static inspection a successful migration.

Return prioritized findings or the completed change with before/after behavior, test evidence, remaining risk and any genuinely unresolved decision. A clean review means no actionable defect found in scope; it is not a correctness guarantee.

Sources: scoped review/refactor skills from `Skills-main.zip`, architecture benchmarks and concurrency/persistence source audits. See [the source map](../../docs/source-map.md).
