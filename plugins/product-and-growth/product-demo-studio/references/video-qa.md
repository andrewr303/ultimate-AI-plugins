# Encoded-media QA and editorial repair

Bind review to the exact delivered hash and current source/configuration. A changed render invalidates previous QA. Run `python scripts/studio.py media inspect VIDEO.mp4 --job JOB.json --review-dir REVIEW --output REPORT.json` for implemented inspection against the authored job; consult renderer guidance for supported checks. Do not mark unimplemented checks passed.

## Authored review frames

Add optional named times to the render job so proof, transitions and CTA holds are reviewed where this product's story actually occurs:

```json
"reviewPoints": [
  {"time": 2.25, "label": "Action submitted"},
  {"time": 5.6, "label": "Result settled"},
  {"time": 10.5, "label": "CTA reading hold"}
]
```

Each time must be inside the video (`0 <= time < duration`), and each nonblank label can contain at most 80 characters. A job permits at most 32 named points and 100 captions. Authored times select the frame presented at that time: `floor(time * fps)`, bounded to the last encoded frame. Review also includes opening, ending, quarter/midpoint/three-quarter positions, and caption midpoints plus the encoded frames immediately before, at and after each caption boundary. For a boundary between frame times, the first frame at or after it is used; unavailable neighbours outside the clip are skipped.

Samples merge when they select the same frame, retaining all labels. `reviewFrames` records the exact frame index, its grid time (`frame / fps`), labels, PNG path and hash. The frame index is authoritative for the renderer's constant-frame-rate output. A selected-frame FFmpeg decode extracts all samples in one pass. This selects exact frames; it does not infer scene meaning or recognize text.

The first contact sheet is `contact-sheet.jpg`; additional pages are named `contact-sheet-002.jpg`, and so on. Each page contains at most 24 frames. `reviewSheets` records their paths and hashes. Contact-sheet label previews are shortened for space; full labels remain in the QA report. Review fails with an explicit error above 512 unique samples instead of silently dropping required frames. Split an unusually dense job or narrow its caption/review plan before retrying.

| Area | Evidence |
| --- | --- |
| Geometry | Encoded dimensions, ratio and pixel format |
| Time | fps, duration, frame count and expected tolerance |
| Decode | Full FFmpeg decode and errors |
| Picture | Black/blank scan plus inspected relevant frames |
| Product | Native sharpness, complete UI units, qualifiers |
| Captions | Timing, longest lines, safe areas, rendered bounds |
| Cursor | Target alignment, press hold, no clipping |
| Sources | Hashes, revision, native density under maximum crop |
| Audio | Requested stream, duration, peaks/clipping, loudness target |
| Sync | Spoken phrase/cue and corresponding action |

Interpret scans: a deliberate dark opening can be valid; bright emptiness evades black detection. Frame-difference spikes may be intentional cuts. Findings require inspection, not automatic taste judgments.

Extract opening, action, processing/result, transition boundaries, caption-heavy state, CTA and ending from the actual encoded file. Inspect native pixels and target size including 320/390px. Sharp dashboards can still be too small. Recompose complete units instead of severing fragments. Check cursor in transformed output.

Watch normal-speed motion when available: causality, settled reading, camera arrival, continuity, captions and CTA. Repeat loop boundaries. Stills cannot prove pacing, shimmer or velocity. Listen when available; separate that from audio measurements.

Editorial questions: does the intended viewer understand product/action/benefit/next step? Does visible proof support the promise? Does the opening give a reason to watch? Is the story understandable muted? Can sample states be mistaken for customer activity?

Record concrete defects by time/frame, evidence, consequence and repair. Missing proof needs capture or a narrower claim; unreadable UI needs recomposition; rushed results need time; bad cursor targeting needs coordinate correction. Render selective previews and rerun affected checks. Preserve useful comparisons. Keep technical, editorial and intended-host routing status distinct; encoder/model success cannot prove persuasion or campaign performance.
