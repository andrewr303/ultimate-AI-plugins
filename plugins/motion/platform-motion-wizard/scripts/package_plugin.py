#!/usr/bin/env python3
"""Build a deterministic ZIP after local structural and integrity validation."""
from __future__ import annotations

import argparse
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path

from validate_plugin import excluded, validate_archive, validate_directory


def package_plugin(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root):
        raise ValueError("archive must be written outside the plugin directory")
    result = validate_directory(root)
    if not result["ok"]:
        raise ValueError(json.dumps(result))
    manifest = json.loads((root / "plugin.json").read_text())
    wrapper = manifest["name"]
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".platform-motion-", suffix=".zip", dir=output.parent)
    os.close(descriptor)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
                relative = path.relative_to(root)
                if excluded(relative) or path.is_dir():
                    continue
                if path.is_symlink() or not path.is_file():
                    raise ValueError(f"unsafe package file: {relative}")
                entry = zipfile.ZipInfo(f"{wrapper}/{relative.as_posix()}", (2020, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = (stat.S_IFREG | 0o644) << 16
                entry.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        archive_result = validate_archive(temporary)
        if not archive_result["ok"]:
            raise ValueError(json.dumps(archive_result))
        os.replace(temporary, output)
        return {"ok": True, "archive": str(output), "size_bytes": output.stat().st_size,
                "validation_scope": result["scope"], "stats": archive_result["stats"]}
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--output", "--archive", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(package_plugin(args.root, args.output), indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
