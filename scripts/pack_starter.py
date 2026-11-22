#!/usr/bin/env python3
"""Build the Doc Atlas starter ZIP and checksum from a committed Git tree."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "plugins/documentation/doc-atlas"
MARKETPLACE = ".agents/plugins/marketplace.json"
PREFIX = "doc-atlas-starter/"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="existing output directory")
    parser.add_argument("--ref", default="HEAD", help="committed release ref")
    args = parser.parse_args()
    commit = git("rev-parse", "--verify", f"{args.ref}^{{commit}}").decode().strip()
    version = json.loads(git("show", f"{commit}:{PLUGIN}/plugin.json"))["version"]
    catalog = json.loads(git("show", f"{commit}:{MARKETPLACE}"))
    catalog["name"] = "ultimate-ai-plugins-starter"
    catalog["interface"]["displayName"] = "Ultimate AI Plugins Starter"
    catalog["plugins"] = [entry for entry in catalog["plugins"] if entry["name"] == "doc-atlas"]
    if len(catalog["plugins"]) != 1:
        parser.error("expected one Doc Atlas entry in the source catalog")

    archive_path = args.output / f"doc-atlas-starter-v{version}.zip"
    checksum_path = args.output / "SHA256SUMS"
    if archive_path.exists() or checksum_path.exists():
        parser.error("use an output directory without an existing starter or checksum")
    content = io.BytesIO(git("archive", "--format=zip", f"--prefix={PREFIX}", commit, "LICENSE", PLUGIN))
    with ZipFile(content, "a", ZIP_DEFLATED) as archive:
        entry = ZipInfo(PREFIX + MARKETPLACE, date_time=(2026, 1, 1, 0, 0, 0))
        archive.writestr(entry, json.dumps(catalog, indent=2) + "\n", compress_type=ZIP_DEFLATED)
        failed = archive.testzip()
        if failed:
            parser.error(f"archive integrity check failed for {failed}")

    data = content.getvalue()
    with archive_path.open("xb") as archive:
        archive.write(data)
    with checksum_path.open("x", encoding="utf-8") as checksum:
        checksum.write(f"{hashlib.sha256(data).hexdigest()}  {archive_path.name}\n")
    print(archive_path)


if __name__ == "__main__":
    main()
