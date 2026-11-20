# Supplied audio, captions, and word timing

Use [timing.py](../scripts/timing.py) when a production already has audio, SRT captions, or measured word timestamps. Python 3.10+ is sufficient for caption/word validation. Audio analysis also requires `ffmpeg` and `ffprobe` on PATH, including the `ebur128` filter. The command works through Python on Windows 11, macOS, and Linux without a shell-specific script. Windows execution was not exercised in this environment.

All input is local. No provider key, upload, transcription, paid synthesis, or model call is involved. The tool writes a JSON report to a distinct output path and never edits, normalizes, stretches, overwrites, or replaces source audio. Reports identify the source by filename and SHA-256, so they remain portable without development paths. A tool failure exits 2 and does not write a success report.

## Measure supplied audio

Run from the installed plugin directory, quoting paths containing spaces:

```text
python scripts/timing.py analyze --input "project/audio/narration.wav" --output "project/reports/audio-timing.json" --fps 24
```

The output includes:

- `duration`: measured length of the decoded first audio stream; `probedDuration` is the container/stream declaration for comparison.
- `loudness.integratedLufs` and `loudness.truePeakDbtp`: FFmpeg EBU R128 measurements on the original first audio stream. Silence has no finite true peak and is marked `measurementMeaningful: false`.
- `decodedMono`: sample count, peak, and RMS of a temporary mono 22,050 Hz PCM analysis proxy. These proxy levels are separate from original-stream true peak.
- `envelope`: compact 100 ms RMS/peak/transient bins, derived from 20 ms analysis windows.
- `onsetCandidates`: positive RMS changes above an adaptive threshold, with candidate seconds and frame boundaries.
- `beatAnalysis.candidateBpm`, `confidence`, and `beatCandidates`: an onset-spacing hypothesis, if sufficient regular events exist. The confidence describes cadence consistency; it is not a calibrated probability of musical accuracy. A beat grid is withheld below 0.6 confidence.

Treat events as candidates. Speech, compressed music, sustained tones, syncopation, missing attacks, and half/double tempo can defeat this simple amplitude-envelope method. A steady sine wave should not acquire an invented rhythmic grid. The analyzed file is not classified as narration or music automatically. Listen when possible and compare candidate events with the intended picture before assigning sounds or cuts. Audio measurements alone cannot prove that a cue feels synchronized or a mix sounds good.

For multiple audio streams, prepare a deliberate single-stream source first. Analysis always measures `a:0` and reports its stream index. FFmpeg's input protocols are restricted to local files and pipes. Source rights must still be recorded in the project's asset manifest; local analysis grants no redistribution rights.

## Import SRT captions

```text
python scripts/timing.py captions --input "project/captions.srt" --duration 12 --output "project/reports/caption-timing.json" --fps 24
```

The importer accepts UTF-8/BOM, CRLF or LF, multiline text, increasing positive numeric cue IDs, and `HH:MM:SS,mmm` timestamps (a decimal dot also works). It rejects blank input, malformed times, non-increasing cue IDs, unordered/overlapping intervals, zero/negative lengths, captions beyond picture duration, and intervals containing no sampled video frame. Adjacent intervals are allowed. SRT placement settings are rejected explicitly. Styling is preserved as literal text with a warning, so remove styling tags or explicitly support them in the chosen renderer.

`report.captions` contains only `{start, end, text}` and can be assigned directly to a render-job v1 `captions` field. `report.frameMap` carries cue IDs and frame metadata separately, preserving the render schema. Do not put the whole report or its frame metadata inside `job.captions`.

Timing validation does not prove that captions match spoken words, fit the placement's caption safe zone, remain readable, or avoid covering important UI. Inspect the encoded output at its intended viewing size. Nothing in this command creates or estimates word alignment.

## Validate supplied word timestamps

```text
python scripts/timing.py words --input "project/word-timestamps.json" --duration 12 --output "project/reports/word-timing.json" --fps 24
```

Accepted input:

```json
{
  "source": {
    "kind": "human-marked",
    "audioSha256": "replace-with-the-actual-narration-hash"
  },
  "words": [
    {"start": 0.12, "end": 0.42, "text": "Open"},
    {"start": 0.48, "end": 0.94, "text": "Tandem."}
  ]
}
```

A bare word array also works. Each item needs numeric seconds and nonblank `text`; common provider field `word` is accepted as an alias. Conflicting `text`/`word` values are rejected. The tool rejects negative, nonfinite, unordered, overlapping, empty, or out-of-duration intervals. `source` is optional declared provenance, retained under `declaredSource`; its claims and audio hash are not independently verified.

The output preserves source seconds and supplies `frameMap` plus `pauseWindows` for actual gaps between words. A word shorter than the sampled frame interval is retained and marked `subframe`; its timing is never stretched or invented. Pause windows indicate only timestamp gaps. They do not establish sentence, thought, breath, or safe editorial cut boundaries. Verify those against the actual narration.

## Frame boundaries and production planning

All commands accept integer 1–120 fps, matching render-job v1. A frame numbered `f` displays an interval when `start <= f/fps < end`. Therefore its active frame range is `[ceil(start × fps), ceil(end × fps))`, with an exclusive end. Exact decimal/rational arithmetic avoids ordinary float rounding; a tolerance of 1e-8 frame removes numerical noise at a mathematically equal boundary. At 24 fps, 0.100–0.500 s maps to frames 3–11 (`firstFrame: 3`, `endFrameExclusive: 12`).

`totalFramesCoveringDuration` is the ceiling needed to cover the source duration. A renderer may require an integer-frame final duration: decide that explicitly, then validate captions against the actual encoded duration. These utilities do not rewrite the render job or change approved narration to make a film fit.

For narration-led work, measure the locked audio first, bind its hash, and build picture around complete spoken thoughts. Use supplied word timing when available. If it is absent, plan coarse sections from listening and author verified boundaries; do not claim word-locked synchronization from waveform peaks. Preserve a purposeful reading hold after a visible action and its result. Transition overlap extends picture, not speech; never replay or stretch narration to fill it. A musical onset or a timestamp gap is not sufficient evidence that cutting there preserves meaning.

The measured-duration, explicit-overlap, source-binding, and separate-review practices are adapted from Product Launch Motion and Product Demo Director's inspected timing/production guidance. Implementation here is independent local Python. Preserved source notices are distributed in the plugin's license materials. No upstream soundtrack or third-party audio is bundled by this utility.

## Verification

```text
python -m unittest discover -s tests -p test_timing.py -v
```

Tests cover SRT encoding/multiline handling, invalid ordering/overlap/bounds, exclusive frame rounding, subframe word preservation, invalid JSON numbers, source overwrite prevention, portable output, and generated sine/silence/transient fixtures. Tests requiring FFmpeg report a skip when dependencies are absent; a skip is not an audio-analysis pass. Synthetic fixture audio is generated during tests and contains no copied music.
