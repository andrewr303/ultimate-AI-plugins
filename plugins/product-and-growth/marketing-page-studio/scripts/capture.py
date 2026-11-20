#!/usr/bin/env python3
"""Run bounded local browser captures using the bundled capture-job contract."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import urljoin, urlsplit, urlunsplit

SCHEMA_VERSION = "1.0.0"
ACTIONS = {"goto", "click", "fill", "select", "press", "wait-for", "screenshot", "start-recording", "stop-recording"}


class CaptureError(ValueError):
    """An actionable capture input or execution error."""


def _slug(value, field):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9._-]{0,99}", value):
        raise CaptureError(f"{field} must be a stable lowercase id containing letters, digits, '.', '_' or '-'")
    return value


def _integer(value, field, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise CaptureError(f"{field} must be an integer from {minimum} through {maximum}")
    return value


def safe_asset_path(value, suffix=None):
    """Reject parent traversal, Windows drives, absolute paths and ambiguous paths."""
    if not isinstance(value, str) or not value.strip() or "\\" in value or ":" in value:
        raise CaptureError("asset path must be a portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ("..", ".", "") for p in value.split("/")):
        raise CaptureError("asset path must stay inside the production project")
    if suffix and path.suffix.lower() != suffix:
        raise CaptureError(f"asset path must end with {suffix}")
    if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", p) for p in path.parts):
        raise CaptureError("asset path components must use letters, digits, '.', '_' or '-'")
    return path.as_posix()


def project_path(root, relative):
    candidate = (root / safe_asset_path(relative)).resolve()
    if not candidate.is_relative_to(root):
        raise CaptureError("asset path resolves outside the production project (possibly through a symlink)")
    return candidate


def check_url(value, base=None):
    if not isinstance(value, str):
        raise CaptureError("URL must be a string")
    url = urljoin(base, value) if base else value
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise CaptureError("capture URLs must use http:// or https://; serve local files first")
    if parts.username or parts.password:
        raise CaptureError("do not put credentials in capture URLs; use --storage-state with a private local file")
    return url


def display_url(value):
    """Exclude query values and fragments from persisted provenance."""
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def validate_job(job):
    if not isinstance(job, dict):
        raise CaptureError("job must be a JSON object")
    if job.get("schemaVersion") != SCHEMA_VERSION:
        raise CaptureError(f"schemaVersion must equal {SCHEMA_VERSION}")
    _slug(job.get("id"), "id")
    if not isinstance(job.get("productRevision"), str) or not job["productRevision"].strip():
        raise CaptureError("productRevision must identify the revision being captured")
    check_url(job.get("baseUrl"))
    vp = job.get("viewport")
    if not isinstance(vp, dict):
        raise CaptureError("viewport must be an object")
    width = _integer(vp.get("width"), "viewport.width", 240, 7680)
    height = _integer(vp.get("height"), "viewport.height", 240, 4320)
    scale = vp.get("deviceScaleFactor")
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not 1 <= scale <= 4:
        raise CaptureError("viewport.deviceScaleFactor must be between 1 and 4")
    if width * height * scale * scale > 36_000_000:
        raise CaptureError("capture size exceeds 36 megapixels; reduce viewport or scale")
    output_dir = safe_asset_path(job.get("outputDir"))
    if job.get("mode") not in {"actual", "replay", "illustrative"}:
        raise CaptureError("mode must be actual, replay or illustrative")
    if type(job.get("syntheticData")) is not bool:
        raise CaptureError("syntheticData must be a boolean")
    if not isinstance(job.get("claims"), list) or any(not isinstance(x, str) for x in job["claims"]):
        raise CaptureError("claims must be an array of claim ids")
    steps = job.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        raise CaptureError("steps must contain 1 through 100 bounded actions")
    used_paths, used_ids = set(), set()
    has_record_start = False
    has_record_stop = False
    for number, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            raise CaptureError(f"step {number} must be an object")
        ident = _slug(step.get("id"), f"step {number}.id")
        if ident in used_ids:
            raise CaptureError(f"step {number}: duplicate step id")
        used_ids.add(ident)
        action = step.get("action")
        if action not in ACTIONS:
            raise CaptureError(f"step {number}: unsupported action {action!r}; allowed: {', '.join(sorted(ACTIONS))}")
        if "timeoutMs" in step:
            _integer(step["timeoutMs"], f"step {number}.timeoutMs", 100, 120000)
        if "holdMs" in step:
            _integer(step["holdMs"], f"step {number}.holdMs", 0, 10000)
            if action != "wait-for":
                raise CaptureError(f"step {number}: holdMs is only supported on wait-for")
        if action in {"click", "fill", "select", "press", "wait-for"}:
            selector = step.get("selector")
            if not isinstance(selector, str) or not selector.strip() or len(selector) > 1000:
                raise CaptureError(f"step {number}: selector must be a nonempty string of at most 1000 characters")
        if action in {"fill", "select", "press"}:
            if not isinstance(step.get("value"), str) or len(step["value"]) > 100000:
                raise CaptureError(f"step {number}: value must be a string of at most 100000 characters")
        if action == "goto":
            check_url(step.get("value"), job["baseUrl"])
        if action == "screenshot":
            path = safe_asset_path(step.get("path"), ".png")
            if not PurePosixPath(path).is_relative_to(PurePosixPath(output_dir)):
                raise CaptureError(f"step {number}: screenshot path must be inside outputDir")
            if path in used_paths:
                raise CaptureError(f"step {number}: duplicate screenshot path {path}")
            used_paths.add(path)
        if action == "start-recording":
            if has_record_start:
                raise CaptureError("one recording segment is supported per capture job; split additional segments into separate jobs")
            has_record_start = True
        if action == "stop-recording":
            if not has_record_start or has_record_stop:
                raise CaptureError("stop-recording must follow one start-recording")
            has_record_stop = True
    if has_record_start != has_record_stop:
        raise CaptureError("pair start-recording with stop-recording to make the intended footage boundaries explicit")
    if not used_paths and not has_record_start:
        raise CaptureError("job must capture at least one screenshot or recording")
    # Validate the actual packaged JSON Schema too when available. No network resolution.
    schema = Path(__file__).resolve().parents[1] / "contracts" / "schemas" / "capture-job.schema.json"
    if schema.exists():
        if importlib.util.find_spec("jsonschema") is None:
            raise CaptureError("jsonschema is unavailable; install the plugin's Python requirements")
        import jsonschema
        try:
            jsonschema.Draft202012Validator(json.loads(schema.read_text(encoding="utf-8"))).validate(job)
        except jsonschema.ValidationError as exc:
            raise CaptureError(f"capture-job schema: {exc.message}") from exc
    return job


def choose_browser(requested=None):
    candidate = requested or os.environ.get("STUDIO_BROWSER") or os.environ.get("BROWSER_EXECUTABLE")
    if candidate:
        path = shutil.which(candidate) or (str(Path(candidate).resolve()) if Path(candidate).is_file() else None)
        if not path:
            raise CaptureError("requested browser executable was not found; set STUDIO_BROWSER (or BROWSER_EXECUTABLE) or install Chromium")
        return path
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge"):
        path = shutil.which(name)
        if path:
            return path
    return None  # Playwright uses its installed Chromium, or reports an actionable launch failure.


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _asset(path, root, job, ident, kind, rights_id, source_url, dimensions=None):
    if len(ident) > 100:
        ident = ident[:83] + "-" + hashlib.sha256(ident.encode()).hexdigest()[:16]
    data = {"id": ident, "path": path.relative_to(root).as_posix(), "sha256": file_hash(path),
            "kind": kind, "mode": job["mode"], "source": {"type": "capture", "url": display_url(source_url),
            "revision": job["productRevision"], "note": "Synthetic data" if job["syntheticData"] else "Review for private data"},
            "rightsId": rights_id, "claims": job["claims"], "capturedAt": datetime.now(timezone.utc).isoformat()}
    if dimensions:
        data.update(dimensions)
    return data


def canonical_manifest_path(root, job):
    """Reserve one unambiguous root handoff; never replace another capture job."""
    path = root / "capture-manifest.json"
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CaptureError("existing root capture-manifest.json is unreadable; choose a new production root or resolve the conflict") from exc
        if not isinstance(existing, dict) or existing.get("id") != job["id"]:
            raise CaptureError("root capture-manifest.json belongs to a different job; choose a new production root or explicitly move the existing handoff")
    return path


def run_capture(job, output, browser=None, storage_state=None, rights_id="capture-rights-review", reduced_motion=False):
    job = validate_job(job)
    _slug(rights_id, "rights-id")
    if importlib.util.find_spec("playwright") is None:
        raise CaptureError("Playwright is unavailable. Run python -m pip install playwright; python -m playwright install chromium")
    from playwright.sync_api import sync_playwright, Error as BrowserError
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = canonical_manifest_path(root, job)
    artifact_dir = project_path(root, job["outputDir"])
    if artifact_dir.exists() and any(artifact_dir.iterdir()):
        raise CaptureError("outputDir is not empty; choose a new outputDir to avoid stale provenance")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    assets, action_log, console_errors = [], [], []
    vp = job["viewport"]
    context_options = {"viewport": {"width": vp["width"], "height": vp["height"]},
                       "device_scale_factor": vp["deviceScaleFactor"], "reduced_motion": "reduce" if reduced_motion else "no-preference"}
    if storage_state:
        state = Path(storage_state).resolve()
        if not state.is_file():
            raise CaptureError("storage-state file does not exist")
        context_options["storage_state"] = str(state)
    recording = any(s["action"] == "start-recording" for s in job["steps"])
    if recording:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise CaptureError("ffmpeg and ffprobe are required for start/stop recording boundaries; install FFmpeg or request screenshots only")
        context_options["record_video_dir"] = str(artifact_dir / "raw-recording")
        context_options["record_video_size"] = {"width": vp["width"], "height": vp["height"]}
    current_step, initial_time = "initial navigation", 0.0
    rec_start = rec_end = None
    try:
        with sync_playwright() as playwright:
            options = {"headless": True}
            executable = choose_browser(browser)
            if executable:
                options["executable_path"] = executable
            br = playwright.chromium.launch(**options)
            context = br.new_context(**context_options)
            initial_time = time.monotonic()
            page = context.new_page()
            page.set_default_timeout(15000)
            page.on("pageerror", lambda err: console_errors.append(str(err)[:500]))
            response = page.goto(job["baseUrl"], wait_until="domcontentloaded")
            if response and response.status >= 400:
                raise CaptureError(f"initial navigation returned HTTP {response.status}")
            page.evaluate("document.fonts.ready")
            for number, step in enumerate(job["steps"], 1):
                current_step = f"step {number} ({step['action']})"
                action = step["action"]
                timeout = step.get("timeoutMs", 15000)
                if action == "goto":
                    response = page.goto(check_url(step["value"], job["baseUrl"]), wait_until="domcontentloaded", timeout=timeout)
                    if response and response.status >= 400:
                        raise CaptureError(f"{current_step}: HTTP {response.status}")
                elif action == "click":
                    page.locator(step["selector"]).click(timeout=timeout)
                elif action == "fill":
                    page.locator(step["selector"]).fill(step["value"], timeout=timeout)
                elif action == "select":
                    page.locator(step["selector"]).select_option(step["value"], timeout=timeout)
                elif action == "press":
                    page.locator(step["selector"]).press(step["value"], timeout=timeout)
                elif action == "wait-for":
                    page.locator(step["selector"]).wait_for(state="visible", timeout=timeout)
                    if step.get("holdMs", 0):
                        page.wait_for_timeout(step["holdMs"])
                elif action == "start-recording":
                    rec_start = time.monotonic() - initial_time
                elif action == "stop-recording":
                    page.wait_for_timeout(350)
                    rec_end = time.monotonic() - initial_time
                elif action == "screenshot":
                    target = project_path(root, step["path"])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if "selector" in step:
                        page.locator(step["selector"]).screenshot(path=str(target), animations="disabled", timeout=timeout)
                    else:
                        page.screenshot(path=str(target), full_page=True, animations="disabled", timeout=timeout)
                    from PIL import Image
                    with Image.open(target) as im:
                        size = {"width": im.width, "height": im.height}
                    assets.append(_asset(target, root, job, f"{job['id']}-{step['id']}", "image", rights_id, page.url, size))
                # Persist action kinds/IDs, never typed input or keyboard contents.
                action_log.append({"id": step["id"], "action": action, "status": "passed"})
            video = page.video if recording else None
            video_url = page.url
            context.close()
            if video:
                original = Path(video.path())
                target = artifact_dir / f"{job['id']}.webm"
                duration = max(0.05, rec_end - rec_start)
                command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(original), "-ss", f"{rec_start:.3f}",
                           "-t", f"{duration:.3f}", "-an", "-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-y", str(target)]
                result = subprocess.run(command, capture_output=True, text=True, timeout=300)
                if result.returncode:
                    raise CaptureError("FFmpeg could not trim recorded footage; raw recording retained for diagnosis")
                probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height:format=duration", "-of", "json", str(target)], capture_output=True, text=True, timeout=30)
                if probe.returncode:
                    raise CaptureError("ffprobe could not inspect recorded footage; inspect the retained recording")
                info = json.loads(probe.stdout)
                stream = info["streams"][0]
                assets.append(_asset(target, root, job, f"{job['id']}-recording", "video", rights_id, video_url,
                                     {"width": stream["width"], "height": stream["height"], "duration": float(info["format"]["duration"])}))
                original.unlink()
                original.parent.rmdir()
            br.close()
    except BrowserError as exc:
        if "ffmpeg-" in str(exc) or "Video rendering requires ffmpeg" in str(exc):
            raise CaptureError("Playwright recording FFmpeg is unavailable (separate from system ffmpeg). Run python -m playwright install ffmpeg using the same PLAYWRIGHT_BROWSERS_PATH as capture.") from exc
        if "Executable doesn\'t exist" in str(exc):
            raise CaptureError("Playwright Chromium is unavailable. Run python -m playwright install chromium, set STUDIO_BROWSER, or pass --browser.") from exc
        raise CaptureError(f"{current_step} failed ({type(exc).__name__}). Check selector, browser installation and app readiness. No fallback was produced.") from exc
    manifest = {"schemaVersion": SCHEMA_VERSION, "id": job["id"], "productRevision": job["productRevision"],
                "captureJobId": job["id"], "assets": assets}
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    manifest_path.write_text(manifest_text, encoding="utf-8")
    (artifact_dir / "capture-manifest.json").write_text(manifest_text, encoding="utf-8")
    report = {"status": "completed", "jobSha256": hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest(),
              "manifestSha256": file_hash(manifest_path), "actions": action_log, "consoleErrors": console_errors,
              "mode": job["mode"], "syntheticData": job["syntheticData"], "rightsId": rights_id,
              "reviewRequired": "Check accuracy, readable UI, sensitive data and rights. Recorded clip boundaries use browser wall-clock timing."}
    (artifact_dir / "capture-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return manifest, manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path, help="Version 1.0.0 capture-job JSON")
    parser.add_argument("--output", required=True, type=Path, help="Production project root; job.outputDir and step.path resolve beneath it")
    parser.add_argument("--browser", help="Chromium-compatible executable (or STUDIO_BROWSER, then BROWSER_EXECUTABLE)")
    parser.add_argument("--storage-state", type=Path, help="Private local Playwright storage state; never copied to deliverables")
    parser.add_argument("--rights-id", default="capture-rights-review", help="ID in your asset rights manifest; default requires rights review")
    parser.add_argument("--reduced-motion", action="store_true", help="Capture with reduced-motion media preference")
    args = parser.parse_args(argv)
    try:
        job = json.loads(args.job.read_text(encoding="utf-8"))
        manifest, path = run_capture(job, args.output, args.browser, args.storage_state, args.rights_id, args.reduced_motion)
        print(json.dumps({"status": "completed", "manifest": str(path), "assets": len(manifest["assets"])}))
        return 0
    except (CaptureError, OSError, json.JSONDecodeError, ImportError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
