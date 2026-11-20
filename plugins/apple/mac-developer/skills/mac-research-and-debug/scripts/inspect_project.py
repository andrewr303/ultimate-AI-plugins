#!/usr/bin/env python3
"""Bounded, read-only project evidence collector. Never executes project code."""
import argparse
import json
import os
from pathlib import Path

SKIP = {"node_modules", "vendor", "build", "dist", "out", "DerivedData", "Pods", "Carthage", "target", "coverage", "__pycache__"}
MARKERS = {"Package.swift": "swift-package", "Cargo.toml": "rust", "tauri.conf.json": "tauri", "tauri.conf.json5": "tauri", "electron-builder.yml": "electron-builder", "electron-builder.yaml": "electron-builder", "project.yml": "xcodegen", "Info.plist": "apple-bundle", "project.pbxproj": "xcode"}
INTERESTING = set(MARKERS) | {"package.json", "manifest.json"}


def inspect(root: Path, budget: int = 12000) -> dict:
    if not root.is_dir():
        raise ValueError("project path must be an existing directory")
    report = {"root": str(root), "evidence": [], "warnings": [], "visited_entries": 0, "complete": True}
    stack = [(root, 0)]
    while stack:
        folder, depth = stack.pop()
        try:
            with os.scandir(folder) as iterator:
                for entry in iterator:
                    report["visited_entries"] += 1
                    if report["visited_entries"] > budget:
                        report["complete"] = False
                        report["warnings"].append("entry budget reached; inspect remaining directories manually")
                        return report
                    if entry.is_symlink() or entry.name.startswith("."):
                        continue
                    path = Path(entry.path)
                    if entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith((".xcodeproj", ".xcworkspace")):
                            report["evidence"].append({"path": str(path.relative_to(root)), "kind": "xcode-project"})
                        if entry.name in SKIP:
                            continue
                        if depth >= 8:
                            report["complete"] = False
                            continue
                        stack.append((path, depth + 1))
                        continue
                    if not entry.is_file(follow_symlinks=False) or entry.name not in INTERESTING:
                        continue
                    rel = str(path.relative_to(root))
                    if entry.name in MARKERS:
                        report["evidence"].append({"path": rel, "kind": MARKERS[entry.name]})
                        continue
                    # Opening without following a final symlink also guards against a changed entry.
                    try:
                        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
                        with os.fdopen(fd, "rb") as source:
                            raw = source.read(512 * 1024 + 1)
                        if len(raw) > 512 * 1024:
                            report["warnings"].append(f"{rel}: JSON exceeds size limit")
                            continue
                        obj = json.loads(raw)
                        if not isinstance(obj, dict):
                            raise ValueError("expected JSON object")
                        if entry.name == "package.json":
                            scripts = obj.get("scripts", {})
                            deps = {}
                            for field in ("dependencies", "devDependencies", "optionalDependencies"):
                                if isinstance(obj.get(field), dict):
                                    deps.update(obj[field])
                            report["evidence"].append({"path": rel, "kind": "node-package", "script_names": sorted(scripts) if isinstance(scripts, dict) else [], "frameworks": sorted(k for k in deps if k in {"electron", "electron-builder", "electron-forge", "@electron-forge/cli", "@tauri-apps/cli", "@tauri-apps/api", "react", "next", "vue", "svelte"}), "has_workspaces": bool(obj.get("workspaces"))})
                        elif "manifest_version" in obj and ("name" in obj or "version" in obj):
                            permissions = obj.get("permissions", [])
                            report["evidence"].append({"path": rel, "kind": "browser-extension", "manifest_version": obj.get("manifest_version"), "has_background": bool(obj.get("background")), "native_messaging": isinstance(permissions, list) and "nativeMessaging" in permissions})
                    except (OSError, ValueError, UnicodeError, RecursionError) as err:
                        report["warnings"].append(f"{rel}: {type(err).__name__}; inspect manually")
        except OSError as err:
            report["complete"] = False
            report["warnings"].append(f"{folder.relative_to(root)}: {type(err).__name__}")
    report["evidence"].sort(key=lambda item: (item["path"], item["kind"]))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.project.resolve())
    except ValueError as err:
        parser.error(str(err))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
