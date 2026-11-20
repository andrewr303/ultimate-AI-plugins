---
name: pds-render
description: "Use when selecting an explicit product-video renderer, producing previews/final exports, compositing real footage, or reproducing a render with source and configuration hashes."
---

# Rendering and adapters

Read [renderer](../../references/renderer.md), [execution](../../references/execution.md) and the render-job contract. Run the doctor.

1. Validate job, assets, revision, storyboard timing, output geometry/fps/duration and hashes. Name proof/result/CTA beats in `reviewPoints`; review also covers caption transitions. For custom HTML, declare content/CTA/caption `data-pds-role` markers or `layoutTargets`, and implement independently seekable configure/seek functions. Their Promises, fonts and images are awaited with bounded readiness. Fail usefully for absent files or unsupported options.
2. Select an explicit supported adapter. `html-playwright` is primary; `footage` preserves recorded sources. Remotion needs its local installed CLI; Hyperframes uses caller-verified argv and is not a presumed installed capability.
3. Run `python scripts/studio.py render --job JOB.json --output OUTPUT --preview` and inspect frames/movement before final encoding.
4. Render selected finals with `python scripts/studio.py render --job JOB.json --output OUTPUT`. Keep variants/hash identities distinct; cache only matching inputs.
5. Inspect with `python scripts/studio.py media inspect VIDEO.mp4 --job OUTPUT/job.resolved.json --output REPORT.json --review-dir REVIEW` and complete encoded-media review. Use the resolved preview job for preview inspection.
6. Retain artifact hash, renderer/version, input snapshot, dimensions, fps, duration, posters/captions and QA. Reject stale evidence after changes.

Report missing dependencies and documented remedies; never silently switch engines, remove narration or change ratio. Respect separate renderer terms.
