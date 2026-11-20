# Change record: [REPLACE: page or file] — [REPLACE: YYYY-MM-DD]

One record per page per run. Use it for citability rewrites, entity and metadata edits and any other content change an agent prepares. Rules for what may change: [citability-and-rewrite.md](../references/citability-and-rewrite.md).

| Field | Value |
| --- | --- |
| File | [REPLACE: path in the repository] |
| URL | [REPLACE: production URL] |
| Section ID | [REPLACE: from `SG sections list <file>`, for example s03] |
| Target query | [REPLACE: real query from the user, a Search Console export or a tracker export, with its source] |
| State | [REPLACE: prepared / implemented locally / deployed / measured] |

## Changes

| Element | Before | After | Why | Evidence |
| --- | --- | --- | --- | --- |
| [REPLACE: first sentence of section s03] | [REPLACE: exact original text] | [REPLACE: exact new text] | [REPLACE: for example "direct answer moved to the first sentence"] | [REPLACE: `SG citability` passage score before and after, labelled heuristic; or user-supplied source URL] |
| [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |

## Placeholders still to fill

List every `[needs source]` note left in the draft. Never replace one with a number, quote, author or date that nobody supplied or verified.

| Location | What is missing | Who can supply it |
| --- | --- | --- |
| [REPLACE: section and sentence] | [REPLACE: for example "source for the 2025 adoption figure"] | [REPLACE: owner, product team, public primary source] |

## Fidelity result

Paste the summary of `SG fidelity original.md rewrite.md` (exit code 0 means passed).

| Check | Result |
| --- | --- |
| Command | [REPLACE: exact command] |
| Exit code | [REPLACE: 0 or 1] |
| Violations | [REPLACE: none, or the list with rule IDs FID001 to FID010] |
| Word ratio | [REPLACE: rewrite words / original words] |

A failed fidelity check means the rewrite is rejected or redone. It is never overridden in the record.

## Re-measure list

| Query | Surface | Read-back date | Ledger entry |
| --- | --- | --- | --- |
| [REPLACE] | [REPLACE: for example perplexity] | [REPLACE: YYYY-MM-DD] | [REPLACE: observation or experiment ID] |

A citability improvement is a readiness proxy. Whether engines cite the page is known only after the read-back, and only for the surfaces that were measured.
