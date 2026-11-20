# Interaction review

## Scope and evidence

- Product flow, revision, stack/version, viewport/device, input method:
- Source files inspected:
- Runtime/recording/trace actually observed:
- Normal and reduced-motion conditions:
- Limitations:

## Findings

| Severity | Action and reproduction | Observed result | Expected result | Cause/confidence | Fix location | Verification |
| --- | --- | --- | --- | --- | --- | --- |

Severity: Blocker = a demonstrated trap, core-task failure, consequential false outcome, or serious inaccessible state; High = frequent lost input/state or materially blocked input mode; Medium = reproducible impairment with a workable path; Low = local polish. State observed versus inferred for each finding.

## State and interruption checks

| Scenario | Expected endpoint / focus / scroll | Evidence | Result |
| --- | --- | --- | --- |
| Ordinary input | | | |
| Rapid reverse/reopen | | | |
| Obsolete completion delivered after replacement | | | |
| Slow success/failure/cancel | | | |
| Keyboard/touch alternative | | | |
| Reduced motion at start | | | |
| Preference changes after positively observed active effect | | | |
| Navigate/unmount/resize | | | |

## Remaining limitations

Distinguish code checks from runtime evidence. Do not infer measured latency, frame rate, screen-reader behavior, or accessibility compliance from screenshots.
