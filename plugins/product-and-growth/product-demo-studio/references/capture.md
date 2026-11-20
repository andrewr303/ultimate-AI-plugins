# Product capture and faithful replay

## Inspect before shooting

Read the relevant product routes, components, visible labels, sample-data modules and actual running states. Select the smallest causal workflow that proves the campaign promise. The source fixture itself is the evidence for synthetic Tandem behavior; it is not evidence of customer adoption or performance.

Plan entry, input, initiating action, processing, complete result, review/edit boundary and CTA. Preserve lead-in/out around important events. Use seeded nonproduction data, documented test authentication and source-side redaction. Keep browser auth state outside deliverables. Inspect images/canvases/PDFs separately; a DOM text replacement cannot redact their pixels.

## Native density and readable framing

Choose logical viewport, device scale and retained recording dimensions deliberately. Verify the encoded raster with ffprobe; increasing DPR alone does not prove the recorder retained more pixels. Preserve that density through normalization. Capture high enough for the largest crop, then inspect native strokes and target-size readability separately.

A complete selected request, status card or reply can communicate more than an entire tiny dashboard. Keep qualifiers, units, consequences and source labels visible. Source sharpness cannot cure excessive information density at phone size.

## Capture execution

Use `python scripts/studio.py capture --job JOB.json --output CAPTURES` where the bundled capture command is provided; inspect `--help` and the capture-job example for its supported actions. The video example includes a real-workflow capture job and footage adapter contract; use their exact paths from [renderer guidance](renderer.md). Do not guess a browser MCP name or use a command advertised by an upstream skill without its implementation.

After recording, inspect the actual frames, confirm events against source time and create a manifest with IDs, relative paths, dimensions, product revision, visual mode, hashes and rights. A new recording changes downstream in-points: update storyboard excerpts and render binding. A file named redacted or approved is not proof that its content is safe or current.

## Wait for the demonstrated result

An element can already be visible while its result is stale or processing. A `wait-for` action can declare a bounded condition before taking proof screenshots or continuing a recording:

```json
{
  "id": "result-ready",
  "action": "wait-for",
  "selector": "#result",
  "condition": {"type": "text", "value": "Ready for review"},
  "timeoutMs": 15000,
  "holdMs": 1000
}
```

Supported condition objects have exactly these fields:

| Condition | Shape and meaning |
| --- | --- |
| Element state | `{"type":"state","state":"visible"}`; also `hidden`, `attached`, or `detached`. Hidden also succeeds when the element is absent. |
| Whole text | `{"type":"text","value":"Ready for review"}`; Playwright retries whole-text equality with whitespace normalization. |
| Attribute value | `{"type":"attribute","name":"data-state","value":"complete"}`; retries equality for the named attribute. |

Absent `condition` preserves the existing visible-element wait. Text and attribute checks do not also require visibility; add a separate visible-state wait if the next shot needs both facts. Attribute names must use letters, digits, `_`, `:`, `.`, or `-` and start with a letter, `_`, or `:`. Names are limited to 200 characters; text/attribute values to 10,000. String values are literal, including an empty string; regular expressions and job-supplied JavaScript are unsupported. Conditions are accepted only on `wait-for` actions. `timeoutMs` bounds each readiness check from 100 through 120,000 milliseconds. Optional `holdMs` adds a settled reading hold after the condition succeeds, from zero through 10,000 milliseconds.

Capture reports record the condition type and passed/failed outcome alongside the step ID. They omit selectors, expected/observed text, attribute names and values; screenshots and the product itself still need private-data review. A failed condition exits unsuccessfully, writes a failed `capture-report.json` for diagnosis, and does not publish a new capture manifest. Use a fresh output directory when retrying. A condition proves only the authored DOM observation; it does not verify the product claim or the source of the result.

## Reconstructing UI

Reuse native components and frozen sample states when practical. Otherwise reproduce verified geometry, typography, labels, data and states in an isolated composition. Declare replay mode and source revision; label the reconstruction where it might otherwise appear to be a new live run. Record a source-state/capture mapping per shot.

Do not infer unseen behavior from a still image. If screenshots are the only material, animate their presentation or build a labeled illustrative prototype within verified bounds. An illustrative concept does not prove shipped capability. A deterministic sample must not imply a live AI call.

## Real-footage editing

Use the `footage` adapter for actual recordings. Preserve the initiating action and visible result; compress only identified idle/navigation time and disclose relevant timing treatment. Do not insert a result from another case or conceal an exception that changes the claim. Keep recorded authority boundaries. Source excerpt ranges must exist and be long enough for narration/reading holds.

## Imported handoffs

Marketing-page captures arrive as files, not a runtime dependency. Validate the brand/evidence/capture/rights objects, resolve only safe relative paths and verify hashes after copying. Reject stale revision mismatches or explicitly document them before production.
