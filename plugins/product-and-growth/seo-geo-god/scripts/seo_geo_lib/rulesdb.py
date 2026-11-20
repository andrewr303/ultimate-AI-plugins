"""Rule catalog, data-file loading and data freshness (WP01; public API frozen).

`data/rules.json` is the single source of rule metadata. Modules create findings with
`findings.make(rule_id, ...)`, which reads severity, priority and class from here.
"""
from __future__ import annotations

import copy
import functools
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple, Union

from . import DATA_DIR

RULE_ID_RE = re.compile(r"^[A-Z]{2,6}\d{3}$")
SEVERITIES = ("error", "warning", "info")
PRIORITIES = ("P0", "P1", "P2", "P3")
EVIDENCE_CLASSES = ("A", "B", "C", "D")
STATUSES = ("v1", "planned")
EFFORTS = ("S", "M", "L")
IMPACTS = ("high", "medium", "low")
SCOPES = ("page", "site")
OWNERS = ("robots", "robots.access_check", "llmstxt", "sitescan", "sitemaps", "hreflang", "perf",
          "jsonld", "content", "fidelity", "drift")
REF_RE = re.compile(r"^(fact:F-(?:AI|T)-\d{2}|rule:[A-Z]{2,6}\d{3}|"
                    r"(?:references|templates|skills)/[A-Za-z0-9._/-]+\.md(?:#[a-z0-9-]+)?|https://\S+)$")
_DATA_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_JSON_TOKEN_RE = re.compile(r'"(?:[^"\\]|\\[\s\S])*"?|[\[\]{}]')
MAX_JSON_DEPTH = 256
_RULE_FIELDS = ("id", "title", "category", "severity", "priority", "evidence_class", "effort", "impact",
                "status", "owner", "fix_hint", "refs")


@dataclass(frozen=True)
class Rule:
    """One catalog entry (see data/rules.json)."""
    id: str
    title: str
    category: str
    severity: str
    priority: str
    evidence_class: str
    effort: Optional[str]
    impact: str
    status: str
    owner: str
    fix_hint: str
    refs: Tuple[str, ...]
    scope: str = "page"
    notes: str = ""

    @property
    def family(self) -> str:
        """Alphabetic prefix of the rule ID (e.g. ``CANON``)."""
        return self.id.rstrip("0123456789")

    def to_dict(self) -> Dict[str, Any]:
        """JSON-ready dict in catalog field order."""
        out = {k: getattr(self, k) for k in _RULE_FIELDS}
        out["refs"] = list(self.refs)
        out["scope"] = self.scope
        if self.notes:
            out["notes"] = self.notes
        return out


class RuleCatalog:
    """Loaded rule catalog: rules, categories (weights per profile), penalties, blockers."""

    def __init__(self, data: Dict[str, Any], source: str = "<memory>") -> None:
        if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
            raise ValueError("%s: rules catalog must be an object with a 'rules' list" % source)
        self.source = source
        self.schema = data.get("schema")
        self.rules_version = str(data.get("rules_version", ""))
        self.as_of = str(data.get("as_of", ""))
        self.categories: Dict[str, Dict[str, Any]] = dict(data.get("categories") or {})
        self.penalties: Dict[str, Any] = dict(data.get("penalties") or {})
        self.blockers: FrozenSet[str] = frozenset(data.get("blockers") or ())
        self.checks: Dict[str, List[str]] = {k: list(v) for k, v in (data.get("checks") or {}).items()}
        self.escalations: Dict[str, Any] = dict(data.get("escalations") or {})
        self._rules: Dict[str, Rule] = {}
        for entry in data["rules"]:
            if not isinstance(entry, dict) or any(k not in entry for k in _RULE_FIELDS):
                raise ValueError("%s: rule entry missing required fields: %r" % (source, entry))
            rid = entry["id"]
            if rid in self._rules:
                raise ValueError("%s: duplicate rule id %s" % (source, rid))
            kw = {k: entry[k] for k in _RULE_FIELDS}
            kw["refs"] = tuple(entry["refs"])
            self._rules[rid] = Rule(scope=entry.get("scope", "page"), notes=entry.get("notes", ""), **kw)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "RuleCatalog":
        """Load data/rules.json (or `path`); raises ValueError on a malformed catalog."""
        target = Path(path) if path is not None else DATA_DIR / "rules.json"
        return cls(read_json(target), source=str(target))

    def get(self, rule_id: str) -> Rule:
        """Return the rule; KeyError on an unknown id."""
        try:
            return self._rules[rule_id]
        except KeyError:
            raise KeyError("unknown rule id: %s" % rule_id) from None

    def all(self) -> List[Rule]:
        """All rules in catalog order."""
        return list(self._rules.values())

    def __contains__(self, rule_id: object) -> bool:
        return rule_id in self._rules

    def __len__(self) -> int:
        return len(self._rules)

    def scored_categories(self) -> List[str]:
        """Category ids that take part in scoring, in catalog order."""
        return [c for c, meta in self.categories.items() if meta.get("scored", True)]

    def categories_for_checks(self, checks_run: List[str]) -> List[str]:
        """Categories measured by the given check names (unknown names measure nothing)."""
        found = set()
        for check in checks_run:
            if check in self.categories:
                found.add(check)
            found.update(self.checks.get(check, ()))
        return [c for c in self.categories if c in found]

    def severity_for(self, rule_id: str, *, profile: str = "default", expect_indexable: bool = False) -> str:
        """Catalog severity after documented escalations (§4.5 profiles, §4.9 notes)."""
        sev = self.get(rule_id).severity
        if expect_indexable:
            sev = self.escalations.get("expect_indexable", {}).get(rule_id, sev)
        sev = self.escalations.get("profiles", {}).get(profile, {}).get(rule_id, sev)
        cap = self.escalations.get("caps", {}).get(rule_id)
        if cap and SEVERITIES.index(sev) < SEVERITIES.index(cap):
            sev = cap
        return sev

    def problems(self) -> List[str]:
        """Integrity problems (empty list when the catalog is consistent)."""
        out: List[str] = []
        if self.schema != "seo-geo-god.rules/1":
            out.append("schema must be seo-geo-god.rules/1")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", self.as_of):
            out.append("as_of must be YYYY-MM-DD")
        for cid, meta in self.categories.items():
            weights = meta.get("weights", {})
            if not meta.get("title") or set(weights) != {"seo", "geo"}:
                out.append("category %s needs title and seo/geo weights" % cid)
        for profile in ("seo", "geo"):
            total = sum(m["weights"].get(profile, 0) for m in self.categories.values()
                        if m.get("scored", True) and "weights" in m)
            if total != 100:
                out.append("%s weights sum to %s, expected 100" % (profile, total))
        for name, cats in self.checks.items():
            for cat in cats:
                if cat not in self.categories:
                    out.append("check %s maps to unknown category %s" % (name, cat))
        for rid in sorted(self.blockers):
            if rid not in self._rules:
                out.append("blocker %s is not a rule" % rid)
        for r in self._rules.values():
            out.extend(_rule_problems(r, self.categories))
        return out


def _rule_problems(r: Rule, categories: Dict[str, Any]) -> List[str]:
    checks = [
        (RULE_ID_RE.match(r.id), "id pattern"), (r.category in categories, "category"),
        (r.severity in SEVERITIES, "severity"), (r.priority in PRIORITIES, "priority"),
        (r.evidence_class in EVIDENCE_CLASSES, "evidence_class"), (r.effort in EFFORTS or r.effort is None, "effort"),
        (r.impact in IMPACTS, "impact"), (r.status in STATUSES, "status"), (r.owner in OWNERS, "owner"),
        (r.scope in SCOPES, "scope"), (bool(r.title) and len(r.title) <= 120, "title"),
        (bool(r.fix_hint) and len(r.fix_hint) <= 200, "fix_hint length"),
        (bool(r.refs) and all(REF_RE.match(x) for x in r.refs), "refs format"),
    ]
    return ["%s: invalid %s" % (r.id, label) for ok, label in checks if not ok]


@functools.lru_cache(maxsize=1)
def default_catalog() -> RuleCatalog:
    """Cached catalog loaded from data/rules.json."""
    return RuleCatalog.load()


def json_depth_exceeds(text: str, max_depth: int = MAX_JSON_DEPTH) -> bool:
    """True when JSON nesting exceeds `max_depth` (brackets inside strings are ignored)."""
    depth = 0
    for match in _JSON_TOKEN_RE.finditer(text):
        tok = match.group()
        if tok in "[{":
            depth += 1
            if depth > max_depth:
                return True
        elif tok in "]}":
            depth -= 1
    return False


def _reject_constant(name: str) -> Any:
    raise ValueError("non-finite JSON number %s refused" % name)


def loads_json(data: Union[str, bytes], *, max_depth: int = MAX_JSON_DEPTH) -> Any:
    """json.loads with a nesting pre-check, NaN/Infinity refused; raises ValueError."""
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("JSON is not UTF-8: %s" % exc) from None
    elif data.startswith("\ufeff"):
        data = data[1:]
    if json_depth_exceeds(data, max_depth):
        raise ValueError("JSON nesting deeper than %d refused" % max_depth)
    try:
        return json.loads(data, parse_constant=_reject_constant)
    except RecursionError:
        raise ValueError("JSON nesting too deep") from None


def read_json(path: Union[str, Path], *, max_bytes: int = 5_000_000, max_depth: int = MAX_JSON_DEPTH) -> Any:
    """Read and parse a JSON file with size and depth caps; raises ValueError or OSError."""
    p = Path(path)
    size = p.stat().st_size
    if size > max_bytes:
        raise ValueError("%s is %d bytes; limit is %d" % (p, size, max_bytes))
    with open(p, "rb") as fh:
        raw = fh.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError("%s exceeds %d bytes" % (p, max_bytes))
    return loads_json(raw, max_depth=max_depth)


def load_data(name: str, *, max_bytes: int = 5_000_000) -> Any:
    """Load data/<name>.json (name is a bare file stem) with size and depth guards."""
    if not _DATA_NAME_RE.match(name):
        raise ValueError("invalid data file name: %r" % name)
    return read_json(DATA_DIR / (name + ".json"), max_bytes=max_bytes)


@functools.lru_cache(maxsize=1)
def _thresholds_cached() -> Dict[str, Any]:
    return load_data("thresholds")


def thresholds() -> Dict[str, Any]:
    """Numeric limits from data/thresholds.json (a fresh copy per call)."""
    return copy.deepcopy(_thresholds_cached())


def freshness(today: date, *, aging_days: int = 90, stale_days: int = 180) -> List[Dict[str, Any]]:
    """Per data file: {file, as_of, age_days, status: fresh|aging|stale|unknown}, sorted by file."""
    rows: List[Dict[str, Any]] = []
    if not DATA_DIR.is_dir():
        return rows
    for p in sorted(DATA_DIR.glob("*.json")):
        if p.is_symlink() or not p.is_file():
            continue
        row: Dict[str, Any] = {"file": "data/" + p.name, "as_of": None, "age_days": None, "status": "unknown"}
        try:
            doc = read_json(p, max_bytes=20_000_000)
            as_of = doc.get("as_of") if isinstance(doc, dict) else None
            day = date.fromisoformat(as_of) if isinstance(as_of, str) else None
        except (OSError, ValueError):
            row["error"] = "unreadable or invalid JSON"
            day = None
        if day is not None:
            age = (today - day).days
            row.update(as_of=day.isoformat(), age_days=age,
                       status="stale" if age > stale_days else "aging" if age > aging_days else "fresh")
        rows.append(row)
    return rows
