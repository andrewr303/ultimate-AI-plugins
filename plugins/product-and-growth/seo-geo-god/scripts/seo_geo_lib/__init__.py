"""SEO-GEO-god offline-first audit library (Python 3.9+, standard library only).

Submodules are imported explicitly by callers; this package imports nothing else.
"""
from __future__ import annotations

from pathlib import Path

TOOL_NAME = "seo-geo-god"
VERSION = "1.0.1"
SCHEMA_VERSION = "1.0"
FACTS_AS_OF = "2026-11-01"
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PLUGIN_ROOT / "data"
SCHEMAS_DIR = PLUGIN_ROOT / "schemas"
