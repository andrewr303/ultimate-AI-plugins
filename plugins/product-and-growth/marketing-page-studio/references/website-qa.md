# Website validation and critique

## Evidence scope

The helper command `python scripts/studio.py web verify --site SITE --output REPORTS` serves the bundled static fixture and records browser assertions plus screenshots. Different projects need their own route/control selectors and expected outcomes. Keep the test's source revision and configuration with its report. No fixture-only test establishes an unrelated site's behavior.

## Responsive pass

Use representative widths of 390, 768, 1024 and 1440px, plus any required target. Inspect the meaningful hero, active demo, result, feature detail and final CTA. Check readable UI, preserved aspect ratios, no page-level horizontal overflow, sensible wrapping, visible focus rings, adequate targets and deliberate mobile order.

Image sharpness needs native-pixel inspection at the largest crop. A clean `naturalWidth` check is useful but cannot detect a screenshot whose bitmap content was soft before capture. Keep full-resolution evidence for important product details.

## Interaction pass

| Behavior | Check |
| --- | --- |
| Tabs | Selected state/panel, Arrow keys, one tab stop, no hidden focusable controls |
| Input/result | Labeled input, valid submit, processing, correct result, sample disclosure |
| Empty/error | Useful message, retained input where useful, retry/clear path |
| Cancel/reset | Pending work stops or is ignored; no stale result arrives later |
| Search/filter | Actual matching, result count, empty recovery, repeat use |
| Reordering | Pointer and keyboard actions update order, announce position, retain focus |
| Editable output | Changes persist in the intended local state; reset behavior is clear |
| Details | Expanded state is exposed; focus/modal escape behavior is appropriate |
| Scroll story | Start/mid/end forward and backward; resize and anchor behavior |
| Replay | Known baseline; no duplicated timers/listeners; deterministic sample |

Use the keyboard from the page's start, not only programmatic `.click()`. Check logical focus order and focus restoration. Native semantic controls are easier to keep usable than divs with ad hoc key handlers.

## Motion and accessibility

Emulate `prefers-reduced-motion: reduce` and verify the full story remains understandable. No essential content should remain at opacity zero waiting for an animation. Test the no-JavaScript path when required. Inspect semantic heading order, landmarks, labels, alt text, status announcements, contrast and color-independent state cues. Automated findings do not replace a screen-reader or device test; record coverage honestly.

## Performance and stability

Collect console/page errors and failed local requests. Reserve dimensions for images/video and for frequently changing demo regions. Observe layout before/after fonts, assets and result states load. Avoid reflow-heavy per-frame work, hidden infinite loops and expensive effects on offscreen surfaces. Prefer responsive images and lazy-load below-the-fold media without delaying the first useful product view.

A performance number from a local fixture is not a production field metric. State network, device and measurement scope if reporting timings.

## Capture planning

Capture initial, input, loading, result and recovery states with stable viewport/motion settings. For recordings, choose actual retained raster dimensions as well as CSS viewport/device scale, and inspect the encoded result. Include lead-in/lead-out around actions; wait for the state that matters rather than a fixed arbitrary delay alone.

Hash delivered images and recordings. Re-recording changes downstream in-points; rebuild dependent edits and reviews. Preserve asset rights and sample labels in the capture manifest.

## Critique and repair

Write concrete observations with route, width, state, evidence and consequence. Prioritize wrong product behavior/claims, unreadable proof, blocked controls and broken mobile layout before subtle spacing. Fix the mechanism and rerun affected checks. Separate technical passes from the editorial question: can a new visitor understand the value and act?
