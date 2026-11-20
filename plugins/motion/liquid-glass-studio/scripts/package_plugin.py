#!/usr/bin/env python3
"""Build a deterministic ZIP of the liquid-glass-studio package and print its SHA-256.

The package directory is validated first; the finished archive is validated
again in --archive mode before it replaces the output path. Entries are sorted,
timestamps are fixed, and file modes are normalized, so the same tree always
produces the same bytes. Cache and dependency folders are left out; research/
is included.

Exit codes: 0 archive written, 1 validation failed, 2 the build could not run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_plugin import EXCLUDED_PARTS, validate_archive, validate_directory  # noqa: E402

FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


class ValidationFailed(Exception):
    def __init__(self, result):
        super().__init__("validation failed")
        self.result = result


def package_files(root):
    """Sorted (relative POSIX path, absolute path) pairs that belong in the archive."""
    root = Path(root).resolve()
    entries = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts) or path.suffix in EXCLUDED_SUFFIXES:
            continue
        if relative.parts[:2] == ("evals", "results"):
            continue  # local eval run output, never shipped

        if path.is_symlink():
            raise ValueError(f"symlink in package: {relative.as_posix()}")
        if path.is_file():
            entries.append((relative.as_posix(), path))
    return sorted(entries)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_plugin(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError("write the archive outside the plugin directory")
    result = validate_directory(root)
    if not result["ok"]:
        raise ValidationFailed(result)
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    wrapper = manifest["name"]
    entries = package_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".liquid-glass-", suffix=".zip", dir=output.parent)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for relative, path in entries:
                info = zipfile.ZipInfo(f"{wrapper}/{relative}", FIXED_TIMESTAMP)
                info.create_system = 3  # Unix, so the mode bits below are honored
                executable = path.stat().st_mode & 0o111
                info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(info, path.read_bytes(), compresslevel=9)
        archive_result = validate_archive(temporary)
        if not archive_result["ok"]:
            raise ValidationFailed(archive_result)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {
        "ok": True,
        "archive": str(output),
        "sha256": sha256_file(output),
        "size_bytes": output.stat().st_size,
        "files": len(entries),
        "warnings": len(result["warnings"]),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a deterministic ZIP of the plugin and print its SHA-256.")
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]),
                        help="plugin directory (default: this script's package)")
    parser.add_argument("--output", "-o", required=True, type=Path, help="ZIP path outside the plugin directory")
    parser.add_argument("--json", action="store_true", help="print a JSON report instead of 'sha256  path'")
    args = parser.parse_args(argv)
    try:
        report = package_plugin(args.root, args.output)
    except ValidationFailed as failure:
        print(json.dumps({"ok": False, "validation": failure.result}, indent=2))
        return 1
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else f"{report['sha256']}  {report['archive']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
