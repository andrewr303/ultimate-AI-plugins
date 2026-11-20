# Review rubric

Use this rubric to make findings reproducible and proportionate. Aesthetic preferences become findings only when they conflict with the requested design direction, project standards or reader usability.

| Severity | Reader impact | Typical example |
| --- | --- | --- |
| Critical | Disclosed secret or materially dangerous instruction in the reviewed content | A real credential in a public example; stop reproducing the value in reports |
| High | Core task cannot be completed, or contract is materially wrong | Quickstart invokes a missing command; documented endpoint differs from schema |
| Medium | Reader can proceed with extra work or loses access to important content | Broken next-step route; keyboard-inaccessible navigation; unreadable code contrast |
| Low | Local clarity, consistency or polish issue | Repeated heading with unclear navigation; inconsistent terminology |

Severity follows observed impact. Do not mark every broken link High or every spelling issue Low without considering context.

## Finding record

```text
Severity: High
Location: README.md:42
Observed: The quickstart calls a script absent from the package manifest.
Impact: A new contributor cannot start the example as documented.
Evidence: README.md:42 and package.json scripts; command was not executed.
Fix: Use the supported script after confirming its prerequisites and expected output.
Verification: Run the corrected command in the authorized local environment.
```

This is an illustrative shape, not evidence about the user's repository. In actual findings, cite the exact inspected source and distinguish observation from execution.

## Check ledger

| Check | Scope / command | Status | Evidence or limitation |
| --- | --- | --- | --- |
| Local references | Exact files checked and helper invocation | passed / failed / blocked / not_run | Exit result and findings; note excluded syntax |
| Project renderer | Real configured build command | passed / failed / blocked / not_run | Build output or missing prerequisite |
| External links | Actual checker and configuration | passed / failed / blocked / not_run | Reachability result; auth/timeouts remain inconclusive |
| Snippets | Actual validation procedure | passed / failed / blocked / not_run | Inspected, parsed, compiled or executed |
| Visual review | Renderer, viewport and theme states | passed / failed / blocked / not_run | Inspected screenshot or browser behavior |

Use a single status per actual row. Split a mixed check into separate rows when different parts have different results. An unavailable check is `blocked` when attempted but prevented by a prerequisite; it is `not_run` when no attempt was made.

## Visual procedure

1. Open the landing/README render, a long guide and a dense reference page when they are in scope.
2. Use a desktop viewport and a narrow viewport around 375 CSS pixels. Zoom text to 200% when supported. Confirm the reading column and navigation remain usable.
3. Exercise intended light/dark states. Inspect code tokens, selection, borders, callouts, links and focus rings against their actual backgrounds.
4. Tab through navigation, search, theme controls, tabs and copy buttons. Check focus visibility, meaningful control labels and escape behavior for overlays.
5. Inspect long commands, wide tables and diagrams. Horizontal scrolling may be appropriate inside code/table containers; page-wide overflow needs investigation.
6. Confirm images have useful alternatives and diagrams have a textual explanation of their meaning. A decorative image can have an intentionally empty alternative; do not apply a blanket rule.
7. Request reduced motion and check that optional motion is removed or reduced without hiding content or breaking interaction.

Record only the states actually reviewed. A CSS token calculation or source inspection can support a narrow finding but cannot replace a rendered interaction check.
