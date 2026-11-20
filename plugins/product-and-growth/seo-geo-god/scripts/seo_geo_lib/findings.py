"""Findings, result envelope, coverage-aware scores and gates (WP01; public API frozen).

Typical module use::

    from .findings import make
    make("CANON002", "Page declares 2 canonical links.", file=rel, url=url, line=14,
         evidence={"observed": hrefs}, key="canonical-count")

`key` is the module-chosen stable evidence key: it feeds the fingerprint, so it must never
contain timestamps or line numbers. Findings with the same rule/file/url/key are merged by
`dedupe` (scope counts merge, samples union).
"""
from __future__ import annotations

import dataclasses
import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import FACTS_AS_OF, SCHEMA_VERSION, TOOL_NAME, VERSION
from .rulesdb import PRIORITIES, RuleCatalog, default_catalog

SEVERITY_ORDER = {"error": 3, "warning": 2, "info": 1}
CONFIDENCES = ("high", "medium", "low")
FAIL_ON = ("error", "warning", "info", "never")
SAMPLE_LIMIT = 10
TEXT_LIMIT = 200
MESSAGE_LIMIT = 300
LIST_LIMIT = 20
SCORE_NOTE = ("Readiness heuristics from deterministic checks; not a ranking, traffic or citation "
              "prediction. Weights are opinionated.")
DEFAULT_UNTRUSTED = ["data.*", "findings[].evidence", "findings[].message", "findings[].scope.sample",
                     "findings[].url"]


@dataclass(frozen=True)
class Finding:
    """One issue instance. Catalog metadata (title, class, fix hint) is joined at output time."""
    rule: str
    severity: str
    message: str
    file: Optional[str] = None
    url: Optional[str] = None
    line: Optional[int] = None
    evidence: Mapping[str, Any] = field(default_factory=dict)
    key: str = ""
    confidence: str = "high"
    affected: int = 1
    sample: Tuple[str, ...] = ()
    priority: Optional[str] = None  # None = catalog default; set only via escalate()

    def __hash__(self) -> int:
        return hash((self.rule, self.severity, self.message, self.file, self.url, self.line, self.key))

    def fingerprint(self) -> str:
        """Stable id: "SG-" + sha1(rule|file|url|key)[:12]."""
        raw = "|".join([self.rule, self.file or "", self.url or "", self.key])
        return "SG-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]

    def effective_priority(self, catalog: RuleCatalog) -> str:
        """Override priority if set, else the catalog default."""
        return self.priority or catalog.get(self.rule).priority

    def to_dict(self, catalog: RuleCatalog) -> Dict[str, Any]:
        """Finding JSON object per schemas/finding.schema.json."""
        rule = catalog.get(self.rule)
        return {
            "id": self.fingerprint(), "rule": self.rule, "title": rule.title, "category": rule.category,
            "severity": self.severity, "priority": self.effective_priority(catalog),
            "confidence": self.confidence, "evidence_class": rule.evidence_class, "file": self.file,
            "url": self.url, "line": self.line, "evidence": truncate(dict(self.evidence)),
            "message": truncate(self.message, MESSAGE_LIMIT), "fix_hint": rule.fix_hint,
            "refs": list(rule.refs), "scope": {"affected": self.affected, "sample": list(self.sample)},
            "as_of": FACTS_AS_OF,
        }


def truncate(value: Any, limit: int = TEXT_LIMIT) -> Any:
    """Recursively bound strings to `limit` chars, lists to 20 items; non-JSON types become strings."""
    return _truncate(value, limit, 0)


def _truncate(value: Any, limit: int, depth: int) -> Any:
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, str):
        return value if len(value) <= limit else value[: max(limit - 1, 0)] + "…"
    if depth >= 8:
        return "…"
    if isinstance(value, Mapping):
        return {_truncate(str(k), limit, depth): _truncate(v, limit, depth + 1) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        value = sorted(value, key=str)
    if isinstance(value, (list, tuple)):
        items = [_truncate(v, limit, depth + 1) for v in list(value)[:LIST_LIMIT]]
        if len(value) > LIST_LIMIT:
            items.append("… (+%d more)" % (len(value) - LIST_LIMIT))
        return items
    return _truncate(str(value), limit, depth)


def make(rule_id: str, message: str, *, catalog: Optional[RuleCatalog] = None, severity: Optional[str] = None,
         **kw: Any) -> Finding:
    """Build a Finding; severity defaults from the catalog, evidence and sample are truncated.

    Accepted keywords: file, url, line, evidence, key, confidence, affected, sample, priority.
    Raises KeyError for an unknown rule and ValueError for invalid values.
    """
    cat = catalog or default_catalog()
    rule = cat.get(rule_id)
    sev = severity or rule.severity
    if sev not in SEVERITY_ORDER:
        raise ValueError("invalid severity %r" % sev)
    conf = kw.pop("confidence", "high")
    if conf not in CONFIDENCES:
        raise ValueError("invalid confidence %r" % conf)
    prio = kw.pop("priority", None)
    if prio is not None and prio not in PRIORITIES:
        raise ValueError("invalid priority %r" % prio)
    file = kw.pop("file", None)
    if file is not None:
        file = str(file).replace("\\", "/")
    line = kw.pop("line", None)
    line = int(line) if line is not None and int(line) >= 1 else None
    distinct = tuple(dict.fromkeys(str(truncate(str(s))) for s in kw.pop("sample", ()) or ()))
    sample = distinct[:SAMPLE_LIMIT]
    affected = max(int(kw.pop("affected", 1) or 1), 1, len(distinct))
    evidence = truncate(dict(kw.pop("evidence", None) or {}))
    key = str(kw.pop("key", ""))[:500]
    url = kw.pop("url", None)
    if kw:
        raise TypeError("unexpected keyword(s) for make(): %s" % ", ".join(sorted(kw)))
    return Finding(rule=rule_id, severity=sev, message=str(message), file=file,
                   url=None if url is None else str(url), line=line, evidence=evidence, key=key,
                   confidence=conf, affected=affected, sample=sample, priority=prio)


def escalate(finding: Finding, catalog: Optional[RuleCatalog] = None) -> Finding:
    """Return the finding at P0 when its rule is in the blocker set (cli decides when to call)."""
    cat = catalog or default_catalog()
    if finding.rule in cat.blockers:
        return dataclasses.replace(finding, priority="P0")
    return finding


def dedupe(findings: Iterable[Finding]) -> List[Finding]:
    """Merge findings with equal fingerprints (first wins; max severity; samples union)."""
    merged: Dict[str, Finding] = {}
    for f in findings:
        fp = f.fingerprint()
        prev = merged.get(fp)
        if prev is None:
            merged[fp] = f
            continue
        sample = tuple(dict.fromkeys(prev.sample + f.sample))
        sev = max(prev.severity, f.severity, key=lambda s: SEVERITY_ORDER[s])
        prio = min((p for p in (prev.priority, f.priority) if p), default=None)
        merged[fp] = dataclasses.replace(prev, severity=sev, priority=prio, sample=sample[:SAMPLE_LIMIT],
                                         affected=max(prev.affected, f.affected, len(sample)))
    return list(merged.values())


def sort_findings(findings: Iterable[Finding], catalog: Optional[RuleCatalog] = None) -> List[Finding]:
    """Deterministic order: priority, severity (desc), rule, file, url, line, fingerprint."""
    cat = catalog or default_catalog()
    return sorted(findings, key=lambda f: (
        PRIORITIES.index(f.effective_priority(cat)), -SEVERITY_ORDER[f.severity], f.rule, f.file or "",
        f.url or "", f.line or 0, f.fingerprint()))


def gate_tripped(findings: Iterable[Finding], fail_on: str) -> bool:
    """True when any finding is at or above `fail_on` (error|warning|info); never → False."""
    if fail_on not in FAIL_ON:
        raise ValueError("fail_on must be one of %s" % ", ".join(FAIL_ON))
    if fail_on == "never":
        return False
    floor = SEVERITY_ORDER[fail_on]
    return any(SEVERITY_ORDER[f.severity] >= floor for f in findings)


def _scope_multiplier(catalog: RuleCatalog, scope: str, affected: int) -> float:
    steps = catalog.penalties.get("scope") or [[1, 1.0], [2, 1.5], [10, 2.0]]
    if scope == "site":
        return float(steps[-1][1])
    mult = float(steps[0][1])
    for threshold, value in steps:
        if affected >= threshold:
            mult = float(value)
    return mult


def compute_scores(findings: Iterable[Finding], checks_run: Sequence[str], catalog: Optional[RuleCatalog] = None,
                   profile: str = "seo") -> Dict[str, Any]:
    """Coverage-aware 0-100 scores for one weight profile (seo|geo), §4.8.

    A category is measured when a mapped check ran. Each triggered rule is penalized once
    (max severity), x class factor (C half, D zero), x scope multiplier. Overall is null when
    measured weight < 70%.
    """
    cat = catalog or default_catalog()
    if profile not in ("seo", "geo"):
        raise ValueError("profile must be seo or geo")
    measured = set(cat.categories_for_checks(list(checks_run)))
    pen = cat.penalties
    base = {"error": float(pen.get("error", 12)), "warning": float(pen.get("warning", 4)),
            "info": float(pen.get("info", 0))}
    factor = {k: float(v) for k, v in (pen.get("class_factor") or {"A": 1, "B": 1, "C": 0.5, "D": 0}).items()}
    by_rule: Dict[str, List[Finding]] = {}
    for f in findings:
        by_rule.setdefault(f.rule, []).append(f)
    categories: Dict[str, Any] = {}
    total_w = measured_w = weighted = 0.0
    for cid in cat.scored_categories():
        weight = float(cat.categories[cid]["weights"][profile])
        total_w += weight
        if cid not in measured:
            categories[cid] = {"score": None, "measured": False}
            continue
        triggered = sorted(r for r in by_rule if cat.get(r).category == cid)
        penalty = 0.0
        for rid in triggered:
            rule, group = cat.get(rid), by_rule[rid]
            sev = max((f.severity for f in group), key=lambda s: SEVERITY_ORDER[s])
            affected = sum(f.affected for f in group)
            penalty += base[sev] * factor.get(rule.evidence_class, 1.0) * _scope_multiplier(cat, rule.scope, affected)
        score = int(round(max(0.0, 100.0 - penalty)))
        categories[cid] = {"score": score, "measured": True, "penalty": round(penalty, 2),
                           "rules_triggered": triggered}
        measured_w += weight
        weighted += weight * score
    share = measured_w / total_w if total_w else 0.0
    out: Dict[str, Any] = {"overall": None, "overall_reason": None, "measured_weight": round(share, 2),
                           "categories": categories}
    if share >= 0.7 and measured_w > 0:
        out["overall"] = int(round(weighted / measured_w))
    else:
        out["overall_reason"] = "measured weight %d%% < 70%%" % int(round(share * 100))
    return out


@dataclass
class Result:
    """Everything a command produced; `to_envelope` renders the §4.2 JSON envelope."""
    command: str
    target: Dict[str, Any]
    mode: str = "offline"
    findings: List[Finding] = field(default_factory=list)
    checks_run: List[str] = field(default_factory=list)
    checks_skipped: List[Dict[str, str]] = field(default_factory=list)
    not_measured: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    summary: Dict[str, Any] = field(default_factory=dict)  # extra counters, e.g. pages, files_skipped
    via_proxy: bool = False
    untrusted_fields: List[str] = field(default_factory=lambda: list(DEFAULT_UNTRUSTED))

    def final_findings(self, catalog: Optional[RuleCatalog] = None) -> List[Finding]:
        """Deduplicated, sorted findings (what the envelope and gates see)."""
        return sort_findings(dedupe(self.findings), catalog)

    def to_envelope(self, catalog: Optional[RuleCatalog] = None, *, now: str,
                    scores: Optional[str] = None) -> Dict[str, Any]:
        """Build the result envelope; `scores` in {None, none, seo, geo, both}."""
        cat = catalog or default_catalog()
        final = self.final_findings(cat)
        counts = {"error": 0, "warning": 0, "info": 0}
        for f in final:
            counts[f.severity] += 1
        summary = dict(self.summary)
        summary.update(counts)
        env: Dict[str, Any] = {
            "tool": TOOL_NAME, "version": VERSION, "schema_version": SCHEMA_VERSION, "command": self.command,
            "generated_at": now, "facts_as_of": FACTS_AS_OF, "rules_version": cat.rules_version,
            "mode": self.mode, "target": dict(self.target), "summary": summary,
            "coverage": {"checks_run": list(self.checks_run), "checks_skipped": [dict(x) for x in self.checks_skipped],
                         "not_measured": list(self.not_measured)},
            "scores": None, "findings": [f.to_dict(cat) for f in final], "data": self.data,
            "limitations": list(self.limitations), "untrusted_fields": sorted(set(self.untrusted_fields)),
            "error": self.error,
        }
        if self.via_proxy:
            env["via_proxy"] = True
        if scores not in (None, "none"):
            if scores not in ("seo", "geo", "both"):
                raise ValueError("scores must be none, seo, geo or both")
            names = ("seo", "geo") if scores == "both" else (scores,)
            env["scores"] = {"profiles": {p: compute_scores(final, self.checks_run, cat, p) for p in names},
                             "note": SCORE_NOTE}
        return env
