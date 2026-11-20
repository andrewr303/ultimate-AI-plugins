# Narration, captions, music and sound

Choose silence, supplied narration, licensed music, original local effects or a combination. Silence is valid for a muted loop, not a fallback for missing narration. External generation/transcription is optional and follows host authorization and cost estimates.

Record rights, file hash, duration, sample rate and channels. Code licenses do not automatically license sample tracks. Preserve locked narration hash/duration; retiming/replacement needs a deliberate revised decision.

## Alignment and captions

Use supplied trusted word/character timings where available; otherwise author and inspect against actual speech. Keep complete thoughts around cuts and show proof near its relevant phrase. Text-estimated sentence lengths are not final alignment.

Subtitles match speech, including qualifiers. Correct transcription against the recording. Keep marketing callouts visually distinct. Cues must be ordered, nonnegative and within duration. Avoid unreadable rapid changes, excessive lines, clipped descenders and essential UI overlap. Reserve space per placement. Deliver editable SRT/VTT or the supported timing contract and inspect longest/last caption frames from the encoded output.

Muted comprehension needs visible context/action/result. Do not duplicate all dense UI labels as giant captions. A narration-led tour may use concise visual summaries plus exact caption files.

## Music and effects

Use supplied/licensed tracks selected for story and brand. Analyze actual onsets/tempo for music-led timing; BPM alone says little about energy. Preserve reading time. Align audible cue peaks to picture events, not blindly to file starts. Effects clarify presses/results/transitions without a mandatory sound for every element.

Set documented loudness/peak targets appropriate to the destination; local defaults are choices, not universal upload rules. Measure integrated loudness, true/sample peak, clipping and relevant silence in the final encoded file. Record actual tools/results. Recheck duration/channels/sync after audio processing.

Listen when available and state that separately from measurements. If playback is unavailable, complete measurements and report listening blocked. Missing requested narration, invalid alignment or unsupported mixing must produce a useful error rather than silent removal or an unsolicited paid-provider substitution.

## Local timing tools

Read [timing](timing.md) only when measuring supplied audio or importing captions/word timings. Commands run from the installed plugin root:

```text
python scripts/timing.py analyze --input AUDIO.wav --output audio-analysis.json --fps 24
python scripts/timing.py captions --input captions.srt --duration 12 --output caption-timing.json --fps 24
python scripts/timing.py words --input words.json --duration 12 --output word-timing.json --fps 24
```

Onset/tempo candidates are heuristic analysis, not speech alignment or a verified musical beat grid. Supplied word timestamps are validated rather than fabricated from text.
