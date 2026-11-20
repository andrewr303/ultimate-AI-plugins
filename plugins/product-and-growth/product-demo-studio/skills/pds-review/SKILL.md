---
name: pds-review
description: "Use when checking and repairing an encoded product demo's technical quality, evidence timing, UI readability, motion, captions, audio or editorial effectiveness before delivery."
---

# Product video review and repair

Read [video QA](../../references/video-qa.md). Technical and creative checks have separate scopes.

1. Bind review to actual encoded hash and current source/configuration. Verify geometry, fps, duration/frame count, codec/pixel format and full decode.
2. Author named `reviewPoints` for action, settled result, transitions and CTA. Run `python scripts/studio.py media inspect VIDEO.mp4 --job JOB.json --review-dir REVIEW --output REPORT.json`; the review includes exact encoded frame indices, authored points and caption boundaries/midpoints. Inspect every contact-sheet page, blank regions, clipping, native sharpness, safe areas and cursor alignment. Preserve the `reviewFrames` and `reviewSheets` hashes; a label is an authored instruction, not proof of what a frame shows.
3. Review at intended size and a 320/390px-wide player. More pixels cannot fix excessive information density; retain complete meaningful units.
4. Watch normal-speed motion when available: causality, pacing, arrival/holds, continuity and muted understanding. Stills cannot prove timing.
5. Measure requested audio/caption timing and bounds. Listen if available; do not describe measurement as listening or absent alignment as passed.
6. Record defects with time/frame, evidence, consequence and repair. Fix source/story/framing/timing, rerun affected checks and preserve useful comparisons.

External model opinions are optional and advisory. Mechanical passes cannot certify persuasion or performance. Record exact blocked/untested checks.
