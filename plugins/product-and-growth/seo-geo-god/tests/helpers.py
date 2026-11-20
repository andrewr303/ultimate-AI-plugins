"""Shared unittest helpers for SEO-GEO-god (WP01; frozen API, standard library only).

Importing this module puts ``scripts/`` on ``sys.path`` so tests can ``import seo_geo_lib``.

Paths
    PLUGIN_ROOT, SCRIPTS_DIR, DATA_DIR, SCHEMAS_DIR, TEMPLATES_DIR, REFERENCES_DIR, SKILLS_DIR, FIXTURES
    fixture(*parts) -> Path; read_fixture(*parts, binary=False) -> str | bytes
Determinism
    NOW ("2026-11-01T00:00:00Z"), TODAY (date(2026, 11, 1)), SEED (20261101), seeded_random(seed=SEED)
Network sentinel (call block_network() in every test module's setUpModule)
    block_network() patches socket connect/create_connection/getaddrinfo/gethostbyname* to raise
    NetworkBlocked (a BaseException, so library ``except Exception`` blocks cannot swallow it);
    network_attempts() lists blocked calls; reset_network_attempts(since=0) drops those recorded from
    index `since` on (only after a test that provokes the sentinel on purpose); restore_network() undoes the patch.
Fakes
    FakeResolver({host: [ip, ...] | Exception}) -- getaddrinfo-compatible; unknown host -> gaierror.
    FakeTransport({url: (status, headers, body)}) -- seo_geo_lib.fetch transport; body is bytes, an
        object with read(n), or an exception instance raised when the request is sent. `.calls`
        holds TransportRequest objects, `.responses` the FakeResponse objects (`bytes_read`).
    FakeClock(start=1000.0, step=0.0) -- callable clock; .sleep(s) records and advances time.
CLI
    run_cli(argv, *, env=None, stdin=None) -> (exit_code, stdout, stderr); imports seo_geo_lib.cli lazily.
Findings and files
    catalog() -> cached RuleCatalog; rule_ids(findings) -> sorted unique rule ids (Finding or dict);
    findings_for(findings, rule_id) -> list; temp_dir() -> context manager yielding a Path;
    write_tree(root, {relpath: str | bytes}) -> Path; gzip_bytes(data) -> bytes.
Validation
    validate_schema(instance, schema_or_file_name) -> list of problems (JSON Schema 2020-12 subset:
        type, enum, const, pattern, min/maxLength, minimum/maximum, required, properties,
        additionalProperties, patternProperties, items, prefixItems, min/maxItems, anyOf, oneOf,
        allOf, not, $ref to "#/$defs/..." or a sibling "*.schema.json" in schemas/).
    parse_py39(path) -> ast.Module (feature_version=(3, 9)); python_files(root=PLUGIN_ROOT) -> [Path].
"""
from __future__ import annotations

import ast
import contextlib
import functools
import gzip
import io
import json
import os
import random
import re
import socket
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple, Union
from unittest import mock

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
DATA_DIR = PLUGIN_ROOT / "data"
SCHEMAS_DIR = PLUGIN_ROOT / "schemas"
TEMPLATES_DIR = PLUGIN_ROOT / "templates"
REFERENCES_DIR = PLUGIN_ROOT / "references"
SKILLS_DIR = PLUGIN_ROOT / "skills"
FIXTURES = PLUGIN_ROOT / "tests" / "fixtures"
NOW = "2026-11-01T00:00:00Z"
TODAY = date(2026, 11, 1)
SEED = 20261101

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def fixture(*parts: str) -> Path:
    """Path under tests/fixtures/."""
    return FIXTURES.joinpath(*parts)


def read_fixture(*parts: str, binary: bool = False) -> Union[str, bytes]:
    """Fixture contents (UTF-8 text unless binary=True)."""
    p = fixture(*parts)
    return p.read_bytes() if binary else p.read_text(encoding="utf-8")


def seeded_random(seed: int = SEED) -> random.Random:
    """Deterministic RNG for property tests."""
    return random.Random(seed)


# ----------------------------------------------------------------------------- network sentinel

class NetworkBlocked(BaseException):
    """Raised by the sentinel; deliberately not an Exception subclass."""


_ATTEMPTS: List[str] = []
_ORIGINALS: Dict[str, Any] = {}


def _blocker(name: str) -> Callable[..., Any]:
    def blocked(*args: Any, **kwargs: Any) -> Any:
        _ATTEMPTS.append("%s%r" % (name, args[1:] if name.startswith("socket.socket.") else args))
        raise NetworkBlocked("network access attempted in a test: %s" % name)
    return blocked


def block_network() -> None:
    """Patch socket entry points so any network use raises NetworkBlocked (idempotent)."""
    if _ORIGINALS:
        return
    targets = [(socket.socket, "connect"), (socket.socket, "connect_ex"), (socket, "create_connection"),
               (socket, "getaddrinfo"), (socket, "gethostbyname"), (socket, "gethostbyname_ex"),
               (socket, "gethostbyaddr")]
    for owner, attr in targets:
        label = ("socket.socket." if owner is socket.socket else "socket.") + attr
        _ORIGINALS[label] = (owner, attr, getattr(owner, attr))
        setattr(owner, attr, _blocker(label))


def restore_network() -> None:
    """Undo block_network()."""
    for owner, attr, original in _ORIGINALS.values():
        setattr(owner, attr, original)
    _ORIGINALS.clear()


def network_attempts() -> List[str]:
    """Blocked network calls recorded since import (copy)."""
    return list(_ATTEMPTS)


def reset_network_attempts(since: int = 0) -> None:
    """Forget attempts recorded at index >= since (for tests that trigger the sentinel on purpose)."""
    del _ATTEMPTS[since:]


# ----------------------------------------------------------------------------- fakes

class FakeResolver:
    """getaddrinfo-compatible resolver backed by a dict; records calls."""

    def __init__(self, mapping: Mapping[str, Any]) -> None:
        self.mapping = {k.lower(): v for k, v in mapping.items()}
        self.calls: List[Tuple[str, int]] = []

    def __call__(self, host: str, port: Any, family: int = 0, type: int = 0, proto: int = 0,
                 flags: int = 0) -> List[Tuple[Any, ...]]:
        self.calls.append((host, port))
        value = self.mapping.get(str(host).lower())
        if value is None:
            raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")
        if isinstance(value, BaseException):
            raise value
        out = []
        for ip in value:
            if ":" in ip:
                out.append((socket.AF_INET6, socket.SOCK_STREAM, 6, "", (ip, int(port or 0), 0, 0)))
            else:
                out.append((socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, int(port or 0))))
        return out


class FakeResponse:
    """Response object for FakeTransport; counts bytes read."""

    def __init__(self, status: int, headers: Any, body: Any) -> None:
        self.status = status
        self.headers = list(headers.items()) if isinstance(headers, Mapping) else list(headers or [])
        self._body = io.BytesIO(body) if isinstance(body, (bytes, bytearray)) else body
        self.bytes_read = 0
        self.closed = False

    def read(self, n: int = -1) -> bytes:
        """Read up to n bytes of the fake body."""
        data = self._body.read(n) if self._body is not None else b""
        self.bytes_read += len(data)
        return data

    def close(self) -> None:
        """Mark the response closed."""
        self.closed = True


class FakeTransport:
    """Transport for seo_geo_lib.fetch: maps absolute URLs to (status, headers, body)."""

    def __init__(self, routes: Optional[Mapping[str, Any]] = None, default: Any = None) -> None:
        self.routes: Dict[str, Any] = dict(routes or {})
        self.default = default
        self.calls: List[Any] = []
        self.responses: List[FakeResponse] = []

    def add(self, url: str, status: int = 200, headers: Any = None, body: Any = b"") -> "FakeTransport":
        """Register a route; returns self for chaining."""
        self.routes[url] = (status, headers or {}, body)
        return self

    @property
    def urls(self) -> List[str]:
        """Requested URLs in order."""
        return [c.url for c in self.calls]

    def __call__(self, req: Any) -> FakeResponse:
        self.calls.append(req)
        route = self.routes.get(req.url, self.default)
        if route is None:
            raise ConnectionRefusedError("no fake route for %s" % req.url)
        if callable(route) and not isinstance(route, tuple):
            route = route(req)
        status, headers, body = route
        if isinstance(body, BaseException):
            raise body
        if callable(body) and not hasattr(body, "read"):
            body = body()
        resp = FakeResponse(status, headers, body)
        self.responses.append(resp)
        return resp


class FakeClock:
    """Monotonic fake clock; `sleep` records durations and advances time (no real sleeping)."""

    def __init__(self, start: float = 1000.0, step: float = 0.0) -> None:
        self.now = start
        self.step = step
        self.sleeps: List[float] = []

    def __call__(self) -> float:
        value = self.now
        self.now += self.step
        return value

    def sleep(self, seconds: float) -> None:
        """Record the requested sleep and advance the clock."""
        self.sleeps.append(seconds)
        self.now += seconds

    def advance(self, seconds: float) -> None:
        """Move the clock forward."""
        self.now += seconds


# ----------------------------------------------------------------------------- CLI and findings

def run_cli(argv: Sequence[str], *, env: Optional[Mapping[str, str]] = None,
            stdin: Optional[str] = None) -> Tuple[int, str, str]:
    """Run seo_geo_lib.cli.main(argv) in-process; returns (exit_code, stdout, stderr)."""
    from seo_geo_lib import cli  # imported lazily: cli.py is written by another package

    out, err = io.StringIO(), io.StringIO()
    patches = [mock.patch.dict(os.environ, dict(env or {}))]
    if stdin is not None:
        patches.append(mock.patch.object(sys, "stdin", io.StringIO(stdin)))
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        stack.enter_context(contextlib.redirect_stdout(out))
        stack.enter_context(contextlib.redirect_stderr(err))
        try:
            code = cli.main(list(argv))
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)
    return int(code or 0), out.getvalue(), err.getvalue()


@functools.lru_cache(maxsize=1)
def catalog() -> Any:
    """Cached RuleCatalog from data/rules.json."""
    from seo_geo_lib.rulesdb import RuleCatalog
    return RuleCatalog.load()


def _rule_of(f: Any) -> str:
    return f["rule"] if isinstance(f, Mapping) else f.rule


def rule_ids(findings: Iterable[Any]) -> List[str]:
    """Sorted unique rule ids from Finding objects or finding dicts."""
    return sorted({_rule_of(f) for f in findings})


def findings_for(findings: Iterable[Any], rule_id: str) -> List[Any]:
    """Findings (objects or dicts) for one rule id."""
    return [f for f in findings if _rule_of(f) == rule_id]


@contextlib.contextmanager
def temp_dir() -> Iterator[Path]:
    """Temporary directory (removed afterwards) as a resolved Path."""
    with tempfile.TemporaryDirectory(prefix="seo-geo-god-test-") as d:
        yield Path(d).resolve()


def write_tree(root: Union[str, Path], files: Mapping[str, Union[str, bytes]]) -> Path:
    """Create files under root from {relative/path: text-or-bytes}; returns root."""
    base = Path(root)
    for rel, content in files.items():
        p = base.joinpath(*rel.split("/"))
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")
    return base


def gzip_bytes(data: bytes) -> bytes:
    """Deterministic gzip (mtime 0)."""
    return gzip.compress(data, mtime=0)


def parse_py39(path: Union[str, Path]) -> ast.Module:
    """Parse a Python file with the 3.9 grammar (raises SyntaxError otherwise)."""
    src = Path(path).read_text(encoding="utf-8")
    return ast.parse(src, filename=str(path), feature_version=(3, 9))


def python_files(root: Union[str, Path] = PLUGIN_ROOT) -> List[Path]:
    """All .py files under root, excluding __pycache__ directories."""
    return sorted(p for p in Path(root).rglob("*.py") if "__pycache__" not in p.parts)


# ----------------------------------------------------------------------------- JSON Schema subset

_TYPES: Dict[str, Callable[[Any], bool]] = {
    "object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str), "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None, "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)}


@functools.lru_cache(maxsize=None)
def _schema_file(name: str) -> Any:
    return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))


def _resolve(ref: str, root: Any) -> Tuple[Any, Any]:
    file_part, _, frag = ref.partition("#")
    doc = _schema_file(os.path.basename(file_part)) if file_part else root
    node = doc
    for token in [t for t in frag.split("/") if t]:
        node = node[token.replace("~1", "/").replace("~0", "~")]
    return node, doc


def validate_schema(instance: Any, schema: Union[str, Mapping[str, Any]]) -> List[str]:
    """Validate against a schema dict or a file name in schemas/; returns problem strings."""
    root = _schema_file(schema) if isinstance(schema, str) else schema
    errors: List[str] = []
    _check(instance, root, root, "$", errors)
    return errors


def _check(v: Any, s: Any, root: Any, path: str, errors: List[str]) -> None:
    if s is True or s is None:
        return
    if s is False:
        errors.append("%s: not allowed" % path)
        return
    if "$ref" in s:
        target, doc = _resolve(s["$ref"], root)
        _check(v, target, doc, path, errors)
    t = s.get("type")
    if t is not None:
        names = t if isinstance(t, list) else [t]
        if not any(_TYPES[n](v) for n in names):
            errors.append("%s: expected type %s" % (path, "/".join(names)))
            return
    if "const" in s and v != s["const"]:
        errors.append("%s: expected const %r" % (path, s["const"]))
    if "enum" in s and v not in s["enum"]:
        errors.append("%s: %r not in enum" % (path, v))
    if isinstance(v, str):
        if "pattern" in s and not re.search(s["pattern"], v):
            errors.append("%s: %r does not match %s" % (path, v, s["pattern"]))
        if len(v) < s.get("minLength", 0) or len(v) > s.get("maxLength", float("inf")):
            errors.append("%s: string length %d out of range" % (path, len(v)))
    if _TYPES["number"](v):
        if v < s.get("minimum", float("-inf")) or v > s.get("maximum", float("inf")):
            errors.append("%s: %r out of range" % (path, v))
        if "exclusiveMinimum" in s and v <= s["exclusiveMinimum"]:
            errors.append("%s: %r <= exclusiveMinimum" % (path, v))
        if "exclusiveMaximum" in s and v >= s["exclusiveMaximum"]:
            errors.append("%s: %r >= exclusiveMaximum" % (path, v))
    if isinstance(v, dict):
        for key in s.get("required", []):
            if key not in v:
                errors.append("%s: missing required %r" % (path, key))
        props = s.get("properties", {})
        patterns = s.get("patternProperties", {})
        for key, val in v.items():
            sub = "%s.%s" % (path, key)
            matched = False
            if key in props:
                matched = True
                _check(val, props[key], root, sub, errors)
            for pat, ps in patterns.items():
                if re.search(pat, key):
                    matched = True
                    _check(val, ps, root, sub, errors)
            if not matched and "additionalProperties" in s:
                _check(val, s["additionalProperties"], root, sub, errors)
        if len(v) < s.get("minProperties", 0):
            errors.append("%s: too few properties" % path)
    if isinstance(v, list):
        prefix = s.get("prefixItems", [])
        for i, item in enumerate(v):
            if i < len(prefix):
                _check(item, prefix[i], root, "%s[%d]" % (path, i), errors)
            elif "items" in s:
                _check(item, s["items"], root, "%s[%d]" % (path, i), errors)
        if len(v) < s.get("minItems", 0) or len(v) > s.get("maxItems", float("inf")):
            errors.append("%s: array length %d out of range" % (path, len(v)))
        if s.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in v}) != len(v):
            errors.append("%s: items not unique" % path)
    for sub in s.get("allOf", []):
        _check(v, sub, root, path, errors)
    for key in ("anyOf", "oneOf"):
        if key in s:
            passing = sum(1 for sub in s[key] if not _sub_errors(v, sub, root, path))
            if (key == "anyOf" and passing == 0) or (key == "oneOf" and passing != 1):
                errors.append("%s: %s matched %d subschemas" % (path, key, passing))
    if "not" in s and not _sub_errors(v, s["not"], root, path):
        errors.append("%s: matched a 'not' schema" % path)


def _sub_errors(v: Any, sub: Any, root: Any, path: str) -> List[str]:
    tmp: List[str] = []
    _check(v, sub, root, path, tmp)
    return tmp
