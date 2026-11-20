---
name: review-account-auth
description: "Review Apple login-service applicability, identity/session boundaries, in-app account deletion and representative App Review access. Use for account/reviewer-flow issues; do not impose a login provider on every app or treat account deletion as automatic Apple subscription cancellation."
---

# Review Account Auth

First read the [operating contract](../../references/operating-contract.md). The actual task and established authorization govern the work.

Resolve the real primary account, providers, account-data graph and reviewer task path.

## Workflow

1. Resolve app, platform, storefront, distribution channel, release/artifact and requested endpoint. Read the actual project and current primary sources for the selected scope.
2. Identify current guideline applicability and exceptions; implement the smallest authorized lifecycle/access fix; test cancellation, revocation, guest/deletion and wrong-account cases; prepare protected synthetic review access; retain exact owner and native-environment gaps.
3. Keep four explicit outcomes: **satisfied by evidence**, **concrete blocker**, **unknown/needs evidence**, and **not applicable with a reason**. A parser/test result proves only its checked scope.
4. Finish independent authorized work while a genuinely missing product, legal or target-environment fact is resolved. A review/preparation task does not authorize remote publication or factual declarations on the owner’s behalf.
5. Return concrete findings or changes, source/date/applicability, exact checks and artifact/account stage, with the next evidence needed. Never report local readiness as review approval.

## Focused references

- [Equivalent login and sessions](../../references/account-auth/equivalent-login-and-sessions.md)
- [Deletion data and subscriptions](../../references/account-auth/deletion-data-and-subscriptions.md)
- [Review access and identity evidence](../../references/account-auth/review-access-and-identity-evidence.md)

Read only the card needed for the current decision. Primary policy statements are contextual source observations, not independent legal clearance. Resolve contradictory, regional or forward-dated conditions before the dependent action; do not freeze them as universal defaults.
