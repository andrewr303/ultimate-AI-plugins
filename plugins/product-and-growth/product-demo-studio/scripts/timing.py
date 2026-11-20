#!/usr/bin/env python3
"""Measure local audio and validate supplied caption/word timing. No APIs or alignment guesses."""
from __future__ import annotations

import argparse
from array import array
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import wave

SCHEMA_VERSION = "1.0.0"
ANALYSIS_RATE = 22050
ANALYSIS_STEP = 0.02
FRAME_EPSILON = Fraction(1, 100_000_000)


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def numeric(value, name: str, *, positive: bool = False) -> Fraction:
    """Parse numbers without binary-float drift; bool is not a timestamp."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Fraction)):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if number < 0 or (positive and number == 0):
        qualifier = "positive" if positive else "non-negative"
        raise ValueError(f"{name} must be {qualifier}")
    return number


def frame_rate(value) -> int:
    rate = numeric(value, "fps", positive=True)
    if rate.denominator != 1 or not 1 <= rate <= 120:
        raise ValueError("fps must be an integer between 1 and 120, matching render-job v1")
    return int(rate)


def frame_boundary(seconds, fps: int) -> int:
    """First frame timestamp at/after seconds. Snap only sub-nanosecond float noise."""
    scaled = numeric(seconds, "timestamp") * frame_rate(fps)
    floor = scaled.numerator // scaled.denominator
    if scaled - floor <= FRAME_EPSILON:
        return floor
    return floor + 1


def _intervals(entries, duration, fps, *, words=False):
    """Validate source order, preserving original seconds and separate frame maps."""
    duration = numeric(duration, "duration", positive=True)
    fps = frame_rate(fps)
    if not isinstance(entries, list) or not entries:
        raise ValueError("timing input must contain a non-empty list")
    normalized, maps = [], []
    previous_end = Fraction(0)
    for index, entry in enumerate(entries):
        label = f"{'word' if words else 'caption'} {index + 1}"
        if not isinstance(entry, dict):
            raise ValueError(f"{label} must be an object")
        if "start" not in entry or "end" not in entry:
            raise ValueError(f"{label} requires start and end in seconds")
        # JSON timestamp fields must be numbers, not string-formatted timestamps.
        if any(isinstance(entry[k], (str, bool)) for k in ("start", "end")):
            raise ValueError(f"{label} start/end must be numeric seconds")
        start = numeric(entry["start"], f"{label} start")
        end = numeric(entry["end"], f"{label} end")
        if end <= start:
            raise ValueError(f"{label} end must be after start")
        if start < previous_end:
            raise ValueError(f"{label} is unordered or overlaps the preceding item")
        if end > duration:
            raise ValueError(f"{label} ends after the declared duration")
        text = entry.get("text", entry.get("word") if words else None)
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"{label} requires nonblank text")
        if words and "text" in entry and "word" in entry and entry["text"] != entry["word"]:
            raise ValueError(f"{label} has conflicting text and word fields")
        first = frame_boundary(start, fps)
        exclusive = frame_boundary(end, fps)
        if not words and first == exclusive:
            raise ValueError(f"{label} is shorter than its available frame interval at {fps} fps")
        normalized.append({"start": float(start), "end": float(end), "text": text.strip()})
        maps.append({"index": index, "firstFrame": first, "endFrameExclusive": exclusive,
                     "frameCount": exclusive - first, "subframe": first == exclusive})
        previous_end = end
    return normalized, maps


SRT_TIME = r"(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})"
SRT_LINE = re.compile(rf"^\s*{SRT_TIME}\s*-->\s*{SRT_TIME}\s*$")


def _srt_time(groups, cue):
    hours, minutes, seconds, milliseconds = map(int, groups)
    if minutes > 59 or seconds > 59:
        raise ValueError(f"SRT cue {cue} has an invalid minute or second field")
    return Fraction(((hours * 60 + minutes) * 60 + seconds) * 1000 + milliseconds, 1000)


def parse_srt(text: str):
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        raise ValueError("SRT is empty")
    entries, identifiers = [], []
    previous_id = 0
    for block in re.split(r"\n[ \t]*\n", text):
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            raise ValueError("each SRT cue requires an increasing numeric index, timestamp line, and text")
        identifier = int(lines[0].strip())
        if identifier <= previous_id:
            raise ValueError(f"SRT cue indices must increase; found {identifier} after {previous_id}")
        match = SRT_LINE.fullmatch(lines[1])
        if not match:
            raise ValueError(f"SRT cue {identifier} requires HH:MM:SS,mmm --> HH:MM:SS,mmm; placement settings are unsupported")
        groups = match.groups()
        start = _srt_time(groups[:4], identifier)
        end = _srt_time(groups[4:], identifier)
        body = "\n".join(lines[2:]).strip()
        entries.append({"start": start, "end": end, "text": body})
        identifiers.append(identifier)
        previous_id = identifier
    return entries, identifiers


def caption_report(text: str, duration, fps=24):
    entries, identifiers = parse_srt(text)
    captions, maps = _intervals(entries, duration, fps)
    for entry, identifier in zip(maps, identifiers):
        entry["sourceCueId"] = identifier
    warnings = []
    if any(re.search(r"<[^>]+>|\{\\", cue["text"]) for cue in captions):
        warnings.append("SRT styling is preserved as literal text; remove markup or adapt the chosen renderer explicitly.")
    return {"schemaVersion": SCHEMA_VERSION, "kind": "caption-timing", "timingAuthority": "supplied-srt",
            "duration": float(numeric(duration, "duration", positive=True)), "fps": frame_rate(fps),
            "totalFramesCoveringDuration": frame_boundary(duration, fps),
            "framePolicy": "frame f is active when start <= f/fps < end; ceil boundaries; end exclusive",
            "captions": captions, "frameMap": maps, "warnings": warnings,
            "limits": ["Caption timing is supplied, not speech-verified.",
                       "No word timing, translation, transcription, or narration alignment is inferred."]}


def word_report(payload, duration, fps=24):
    source = None
    if isinstance(payload, dict):
        entries = payload.get("words")
        source = payload.get("source")
        if source is not None and not isinstance(source, dict):
            raise ValueError("source metadata, when supplied, must be an object")
    elif isinstance(payload, list):
        entries = payload
    else:
        raise ValueError("word input must be an array or an object containing words")
    words, maps = _intervals(entries, duration, fps, words=True)
    pauses = []
    for previous, following in zip(words, words[1:]):
        if following["start"] > previous["end"]:
            pauses.append({"start": previous["end"], "end": following["start"],
                           "duration": round(following["start"] - previous["end"], 9),
                           "firstFrame": frame_boundary(previous["end"], fps),
                           "endFrameExclusive": frame_boundary(following["start"], fps)})
    warnings = ["Supplied timestamps were validated for structure and bounds; their speech alignment was not independently verified."]
    if any(item["subframe"] for item in maps):
        warnings.append("Some words have no sampled frame at this fps; source timestamps were retained without stretching or dropping them.")
    result = {"schemaVersion": SCHEMA_VERSION, "kind": "word-timing", "timingAuthority": "supplied-word-timestamps",
              "duration": float(numeric(duration, "duration", positive=True)), "fps": frame_rate(fps),
              "totalFramesCoveringDuration": frame_boundary(duration, fps),
              "framePolicy": "frame f is active when start <= f/fps < end; ceil boundaries; end exclusive",
              "words": words, "frameMap": maps, "pauseWindows": pauses, "warnings": warnings,
              "limits": ["Pause windows are observed timestamp gaps, not verified sentence or thought boundaries.",
                         "No forced alignment, speech-speed changes, or estimated word timings are performed."]}
    if source is not None:
        result["declaredSource"] = source
    return result


def tool(name):
    executable = shutil.which(name)
    if not executable:
        raise RuntimeError(f"{name} was not found on PATH; install FFmpeg with ffprobe and rerun")
    return executable


def run(args):
    result = subprocess.run([str(item) for item in args], stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"{Path(str(args[0])).name} failed ({result.returncode}): {result.stderr[-2000:]}")
    return result


def _finite_measurement(value):
    number = float(value)
    return number if math.isfinite(number) else None


def loudness_report(stderr: str):
    summary = stderr.rsplit("Summary:", 1)[-1]
    number = r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)|-?inf|nan)"
    integrated = re.search(rf"\bI:\s*{number}\s*LUFS", summary, re.I)
    peak = re.search(rf"\bPeak:\s*{number}\s*dBFS", summary, re.I)
    if integrated is None or peak is None:
        raise RuntimeError("FFmpeg ebur128 did not produce integrated loudness and true-peak measurements")
    return {"integratedLufs": _finite_measurement(integrated.group(1)),
            "truePeakDbtp": _finite_measurement(peak.group(1)), "method": "FFmpeg ebur128=peak=true on original first audio stream"}


def _dbfs(value):
    return round(20 * math.log10(value), 4) if value > 0 else None


def transient_candidates(bins, maximum_rms):
    strengths = [entry["transient"] for entry in bins]
    if not strengths:
        return [], 0.012
    median = statistics.median(strengths)
    deviation = statistics.median(abs(value - median) for value in strengths)
    threshold = max(0.012, maximum_rms * 0.15, median + 3 * deviation)
    candidates = []
    for index, entry in enumerate(bins):
        value = entry["transient"]
        left = strengths[index - 1] if index else -1
        right = strengths[index + 1] if index + 1 < len(strengths) else -1
        if value < threshold or value < left or value < right:
            continue
        candidate = {"time": round(entry["time"], 6), "strength": round(value, 6)}
        if candidates and candidate["time"] - candidates[-1]["time"] < 0.18:
            if value > candidates[-1]["strength"]:
                candidates[-1] = candidate
        else:
            candidates.append(candidate)
    return candidates, threshold


def estimate_beats(candidates, duration):
    # A simple onset-interval estimator, not a spectral/musical beat tracker.
    if len(candidates) < 4:
        return {"candidateBpm": None, "confidence": 0.0, "beatCandidates": [],
                "reason": "Fewer than four sufficiently distinct onset candidates."}
    intervals = [b["time"] - a["time"] for a, b in zip(candidates, candidates[1:])]
    plausible = [value for value in intervals if 0.25 <= value <= 2.0]
    if len(plausible) < 3:
        return {"candidateBpm": None, "confidence": 0.0, "beatCandidates": [],
                "reason": "Onset spacing does not support a 30–240 BPM candidate."}
    period = statistics.median(plausible)
    errors = [abs(value - period) / period for value in plausible]
    inlier_fraction = sum(error <= 0.12 for error in errors) / len(intervals)
    consistency = max(0.0, 1 - statistics.median(errors) * 4)
    count_weight = min(1.0, len(plausible) / 6)
    confidence = round(inlier_fraction * consistency * count_weight, 3)
    bpm = round(60 / period, 3)
    # Only show a grid with a minimally consistent cadence; never silently impose one.
    beats = []
    if confidence >= 0.6:
        anchor = candidates[0]["time"]
        beats = [round(anchor + step * period, 6)
                 for step in range(max(0, math.ceil((duration - anchor) / period)))
                 if anchor + step * period < duration]
    return {"candidateBpm": bpm, "confidence": confidence, "candidatePeriodSeconds": round(period, 6),
            "beatCandidates": beats, "reason": "Median spacing of detected positive RMS changes; grid anchored to first onset.",
            "confidenceMeaning": "Cadence consistency heuristic, not a calibrated probability of correct tempo."}


def analyze_audio(path: Path, fps=24):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("input must be an existing local file")
    fps = frame_rate(fps)
    before = digest(path)
    ffmpeg, ffprobe = tool("ffmpeg"), tool("ffprobe")
    probe = json.loads(run([ffprobe, "-v", "error", "-protocol_whitelist", "file,pipe",
                            "-select_streams", "a:0", "-show_entries",
                            "stream=index,duration,sample_rate,channels:format=duration", "-of", "json", path]).stdout)
    streams = probe.get("streams", [])
    if not streams:
        raise ValueError("input has no audio stream")
    raw_duration = streams[0].get("duration", probe.get("format", {}).get("duration"))
    try:
        probed_duration = float(numeric(raw_duration, "probed duration", positive=True)) if raw_duration is not None else None
    except ValueError:
        probed_duration = None  # Some codecs expose N/A; decoded PCM is measured below.
    with tempfile.TemporaryDirectory(prefix="product-demo-timing-") as temp:
        pcm = Path(temp) / "analysis.wav"
        run([ffmpeg, "-hide_banner", "-nostdin", "-v", "error", "-xerror", "-protocol_whitelist", "file,pipe",
             "-i", path, "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(ANALYSIS_RATE),
             "-c:a", "pcm_s16le", "-y", pcm])
        bins, sample_count, energy, peak, previous_rms = [], 0, 0.0, 0.0, 0.0
        with wave.open(str(pcm), "rb") as source:
            if source.getnchannels() != 1 or source.getsampwidth() != 2:
                raise RuntimeError("unexpected analysis PCM format")
            rate = source.getframerate()
            hop = round(rate * ANALYSIS_STEP)
            while True:
                raw = source.readframes(hop)
                if not raw:
                    break
                samples = array("h")
                samples.frombytes(raw)
                if sys.byteorder != "little":
                    samples.byteswap()
                count = len(samples)
                block_energy = sum((sample / 32768.0) ** 2 for sample in samples)
                block_peak = max(abs(sample) for sample in samples) / 32768.0
                rms = math.sqrt(block_energy / count)
                bins.append({"time": sample_count / rate, "duration": count / rate,
                             "rms": rms, "peak": block_peak, "transient": max(0.0, rms - previous_rms)})
                energy += block_energy
                sample_count += count
                peak = max(peak, block_peak)
                previous_rms = rms
        if sample_count == 0:
            raise ValueError("audio decoded to zero samples")
        duration = sample_count / rate
    loudness = loudness_report(run([ffmpeg, "-hide_banner", "-nostdin", "-nostats", "-xerror",
                                    "-protocol_whitelist", "file,pipe", "-i", path, "-map", "0:a:0", "-vn",
                                    "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr)
    loudness["measurementMeaningful"] = peak > 0
    onsets, threshold = transient_candidates(bins, max(item["rms"] for item in bins))
    for item in onsets:
        item["frame"] = frame_boundary(item["time"], fps)
    beats = estimate_beats(onsets, duration)
    # Compact output envelope: five 20ms analysis bins per reported 100ms bin.
    envelope = []
    for offset in range(0, len(bins), 5):
        group = bins[offset:offset + 5]
        span = sum(item["duration"] for item in group)
        envelope.append({"start": round(group[0]["time"], 6), "end": round(group[-1]["time"] + group[-1]["duration"], 6),
                         "rms": round(math.sqrt(sum(item["rms"] ** 2 * item["duration"] for item in group) / span), 6),
                         "peak": round(max(item["peak"] for item in group), 6),
                         "transient": round(max(item["transient"] for item in group), 6)})
    if digest(path) != before:
        raise RuntimeError("input changed during analysis; no stable timing report can be issued")
    return {"schemaVersion": SCHEMA_VERSION, "kind": "audio-timing-analysis", "status": "measured",
            "source": {"file": path.name, "sha256": before, "audioStream": streams[0].get("index"),
                       "sampleRate": streams[0].get("sample_rate"), "channels": streams[0].get("channels")},
            "duration": round(duration, 9), "probedDuration": probed_duration, "fps": fps,
            "totalFramesCoveringDuration": frame_boundary(duration, fps), "loudness": loudness,
            "decodedMono": {"sampleRate": rate, "samples": sample_count, "peakDbfs": _dbfs(peak),
                            "rmsDbfs": _dbfs(math.sqrt(energy / sample_count)),
                            "note": "Downmixed/resampled analysis proxy; original-stream true peak is measured separately."},
            "envelope": envelope, "analysisStepSeconds": ANALYSIS_STEP, "envelopeStepSeconds": 0.1,
            "onsetThreshold": round(threshold, 6), "onsetCandidates": onsets, "beatAnalysis": beats,
            "limits": ["Onsets and tempo are amplitude-envelope heuristics, not verified musical beats.",
                       "Half/double tempo, syncopation, compression, speech and sustained music can mislead the estimator.",
                       "Verify candidate events against listening and picture before placing cues.",
                       "No word or character alignment, audio edits, uploads or paid operations were performed."]}


def _reject_constant(value):
    raise ValueError(f"non-finite JSON number is not supported: {value}")


def write_report(path: Path, report, source: Path):
    path, source = Path(path).resolve(), Path(source).resolve()
    if path == source or (path.exists() and os.path.samefile(path, source)):
        raise ValueError("output must differ from input; source files are never overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".timing-", suffix=".json", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("analyze", "captions", "words"):
        child = commands.add_parser(command)
        child.add_argument("--input", required=True, type=Path, help="Existing local source file")
        child.add_argument("--output", required=True, type=Path, help="JSON report, distinct from input")
        child.add_argument("--fps", default=24, type=int)
        if command != "analyze":
            child.add_argument("--duration", required=True, help="Positive final picture duration in seconds")
    args = parser.parse_args(argv)
    if not args.input.is_file():
        raise ValueError("input must be an existing local file")
    if args.input.resolve() == args.output.resolve():
        raise ValueError("output must differ from input; source files are never overwritten")
    if args.command == "analyze":
        report = analyze_audio(args.input, args.fps)
    else:
        raw = args.input.read_text(encoding="utf-8-sig")
        report = caption_report(raw, args.duration, args.fps) if args.command == "captions" else word_report(
            json.loads(raw, parse_constant=_reject_constant), args.duration, args.fps)
        report["source"] = {"file": args.input.name, "sha256": digest(args.input)}
    write_report(args.output, report, args.input)
    print(json.dumps({"status": "passed", "command": args.command, "output": args.output.name,
                      "duration": report["duration"], "fps": report["fps"]}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, wave.Error) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        sys.exit(2)
