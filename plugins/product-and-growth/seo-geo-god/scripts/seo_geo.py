#!/usr/bin/env python3
"""SEO-GEO-god CLI entry point. Run as: python3 -I scripts/seo_geo.py COMMAND ...

`-I` keeps PYTHONPATH, user site-packages and the current directory off sys.path; this script
adds only its own directory so the bundled seo_geo_lib package is importable.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seo_geo_lib.cli import main  # noqa: E402  (import after the path setup above)

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
