#!/usr/bin/env python3
"""Build a deterministic ZIP of a validated plugin directory and re-validate the archive.

Usage: python3 -I scripts/package_plugin.py . --output <path outside the plugin>/seo-geo-god-1.0.1.zip
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

# `python3 -I` leaves the script directory off sys.path; add only this directory, and keep
# bytecode caches out of the tree being packaged when run as a command.
if __name__ == "__main__":
    sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_plugin import package_files, validate_archive, validate_directory  # noqa: E402

TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def package_plugin(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root):
        raise ValueError("archive must be written outside the plugin directory")
    result = validate_directory(root)
    if not result["ok"]:
        raise ValueError(json.dumps(result))
    wrapper = json.loads((root / "plugin.json").read_text(encoding="utf-8"))["name"]
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".seo-geo-god-", suffix=".zip", dir=output.parent)
    os.close(descriptor)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for relative in package_files(root):
                path = root / relative
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f"unsafe package file: {relative}")
                entry = zipfile.ZipInfo(f"{wrapper}/{relative}", TIMESTAMP)
                entry.create_system = 3
                entry.external_attr = (stat.S_IFREG | 0o644) << 16
                entry.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        archive_result = validate_archive(temporary)
        if not archive_result["ok"]:
            raise ValueError(json.dumps(archive_result))
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    data = output.read_bytes()
    return {"ok": True, "archive": str(output), "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "validation_scope": result["scope"], "stats": archive_result["stats"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a deterministic, re-validated plugin ZIP.")
    parser.add_argument("root", nargs="?", default=".", help="plugin root directory (default: .)")
    parser.add_argument("--output", "--archive", required=True, type=Path, help="ZIP path outside the plugin directory")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(package_plugin(args.root, args.output), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
