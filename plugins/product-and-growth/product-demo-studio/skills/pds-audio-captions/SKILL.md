---
name: pds-audio-captions
description: "Use when aligning supplied narration and exact captions, planning optional licensed music or sound cues, measuring audio, and preserving muted comprehension in product video."
---

# Narration, captions and sound

Read [audio](../../references/audio.md). Providers are optional; keys being present do not authorize spending.

1. Confirm silence, supplied narration, licensed music, original effects or a combination from the brief. Do not silently remove requested audio.
2. Inspect rights, duration, sample rate, channels and hashes. Preserve a locked narration master and derive picture/caption timing from speech.
3. Use word/character alignment when available; otherwise inspect authored timings against the recording. Subtitles match spoken words exactly; marketing callouts are distinct.
4. Keep captions inside safe areas, clear of essential UI, with readable contrast/time. Deliver editable captions and verify rendered bounds.
5. Align cues to measured picture events. Analyze beats when music-led timing serves the story; keep proof understandable muted.
6. Measure clipping, peak, integrated loudness and chosen tolerance in the final file. Listen when available and report that separately.

Missing narration or alignment needs an explicit useful failure or deliberate revised plan, never silent fallback. Clearly identify any silent alternate/loop.
