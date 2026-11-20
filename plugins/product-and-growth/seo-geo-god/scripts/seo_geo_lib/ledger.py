"""Append-only observation ledger: panel samples, metrics and experiments (WP06).

Layout of a ledger directory: ``ledger.json`` (meta) and ``observations.jsonl`` (one JSON
object per line, never rewritten). Validation mirrors ``schemas/ledger.schema.json``.
Rates use valid samples only: empty and error samples never enter a denominator.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .rulesdb import loads_json

LEDGER_SCHEMA = "seo-geo-god.ledger/1"
OBS_FILE = "observations.jsonl"
META_FILE = "ledger.json"
MAX_LEDGER_BYTES = 52_428_800
RECORD_VERSION = 1
KINDS = ("panel", "metric", "experiment")
STATUSES = ("valid_present", "valid_absent", "empty", "error")
METRIC_SOURCES = ("gsc", "bing", "ga4", "crux", "log", "manual")
DECISIONS = ("promote", "keep_testing", "rollback", "unproven")
QUERY_CLASSES = ("branded", "generic", "commercial", "informational", "navigational", "technical", "comparison",
                 "other")
DEVICES = ("desktop", "mobile", "tablet")
DEFAULT_READBACK_DAYS = (7, 14, 28, 56)
SUMMARY_FIELDS = ("surface", "query_class", "holdout", "locale", "device", "logged_in", "model_label", "query_id",
                  "query")
STORED_FIELDS = ("id", "recorded_at", "v")
PII_KEY_RE = re.compile(r"(?i)(e-?mail|phone|ip_?addr|^ip$|user_?agent|full_?name|first_?name|last_?name|"
                        r"address|cookie|session_?id|user_?id|person)")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2}))?$")
_URL = re.compile(r"^https?://[^\s/@]+(/\S*)?$")
_LOCALE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")

# field -> (kind of value, required, extra constraint); kinds: str:N, enum:NAME, bool, int, num, urls, days, date,
# stamp, window, locale. A trailing "?" in the kind allows null.
_SPECS: Dict[str, Dict[str, Tuple[str, bool]]] = {
    "panel": {"surface": ("str:80", True), "query": ("str:500", True), "query_class": ("enum:QUERY_CLASSES", True),
              "status": ("enum:STATUSES", True), "holdout": ("bool", False), "cited_urls": ("urls", False),
              "cited_statement": ("str:300?", False), "locale": ("locale?", False), "device": ("enum:DEVICES?", False),
              "logged_in": ("bool?", False), "model_label": ("str:80?", False), "observed_at": ("stamp?", False),
              "sample": ("int?", False), "query_id": ("str:80?", False), "note": ("str:500?", False)},
    "metric": {"source": ("enum:METRIC_SOURCES", True), "metric": ("str:120", True), "value": ("num", True),
               "window": ("window", True), "segment": ("str:200?", False), "unit": ("str:40?", False),
               "observed_at": ("stamp?", False), "note": ("str:500?", False)},
    "experiment": {"hypothesis": ("str:1000", True), "change": ("str:1000", True), "target_urls": ("urls", True),
                   "deployed_at": ("date", True), "metric": ("str:120", True), "control_urls": ("urls", False),
                   "baseline_ref": ("str:500?", False), "readback_days": ("days", False),
                   "decision": ("enum:DECISIONS?", False), "experiment_id": ("str:80?", False),
                   "note": ("str:1000?", False)},
}
_ENUMS = {"QUERY_CLASSES": QUERY_CLASSES, "STATUSES": STATUSES, "DEVICES": DEVICES, "METRIC_SOURCES": METRIC_SOURCES,
          "DECISIONS": DECISIONS}


def _valid_date(text: str) -> bool:
    try:
        date.fromisoformat(text[:10])
        return True
    except ValueError:
        return False


def _check_value(name: str, value: Any, kind: str) -> Optional[str]:
    nullable = kind.endswith("?")
    kind = kind.rstrip("?")
    if value is None:
        return None if nullable else "%s must not be null" % name
    if kind.startswith("str:"):
        limit = int(kind[4:])
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            return "%s must be a non-empty string of at most %d characters" % (name, limit)
    elif kind.startswith("enum:"):
        allowed = _ENUMS[kind[5:]]
        if value not in allowed:
            return "%s must be one of %s" % (name, ", ".join(allowed))
    elif kind == "bool":
        if not isinstance(value, bool):
            return "%s must be true or false" % name
    elif kind == "int":
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            return "%s must be an integer >= 1" % name
    elif kind == "num":
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return "%s must be a finite number" % name
    elif kind == "urls":
        if not isinstance(value, list) or len(value) > 50 or not all(
                isinstance(u, str) and len(u) <= 2048 and _URL.match(u) for u in value):
            return "%s must be a list of at most 50 absolute http(s) URLs without userinfo" % name
    elif kind == "days":
        if not isinstance(value, list) or not value or len(set(value)) != len(value) or not all(
                isinstance(d, int) and not isinstance(d, bool) and 1 <= d <= 365 for d in value):
            return "%s must be a non-empty list of distinct integers from 1 to 365" % name
    elif kind == "date":
        if not isinstance(value, str) or not _DATE.match(value) or not _valid_date(value):
            return "%s must be a date YYYY-MM-DD" % name
    elif kind == "stamp":
        if not isinstance(value, str) or not _STAMP.match(value) or not _valid_date(value):
            return "%s must be an ISO 8601 date or UTC timestamp" % name
    elif kind == "window":
        parts = value.split(":") if isinstance(value, str) else []
        if len(parts) != 2 or not all(_DATE.match(p) and _valid_date(p) for p in parts) or parts[0] > parts[1]:
            return "%s must be START:END dates (YYYY-MM-DD:YYYY-MM-DD, start <= end)" % name
    elif kind == "locale":
        if not isinstance(value, str) or len(value) > 35 or not _LOCALE.match(value):
            return "%s must be a BCP 47 language tag such as en-US" % name
    return None


def validate_observation(obs: Any) -> List[str]:
    """Problems with one observation as supplied by the user (empty list = valid)."""
    if not isinstance(obs, dict):
        return ["observation must be a JSON object"]
    kind = obs.get("kind")
    if kind not in KINDS:
        return ["kind must be one of %s" % ", ".join(KINDS)]
    spec = _SPECS[kind]
    problems = []
    for key in sorted(obs):
        if key == "kind" or key in spec:
            continue
        if key in STORED_FIELDS:
            problems.append("%s is set by the ledger; remove it" % key)
        elif PII_KEY_RE.search(key):
            problems.append("field %r looks like personal data; the ledger stores no personal data" % key)
        else:
            problems.append("unknown field %r for kind %s" % (key, kind))
    for key, (vkind, required) in spec.items():
        if key not in obs:
            if required:
                problems.append("missing required field %s" % key)
            continue
        problem = _check_value(key, obs[key], vkind)
        if problem:
            problems.append(problem)
    if kind == "panel" and obs.get("status") in ("empty", "error") and obs.get("cited_urls"):
        problems.append("an empty or error sample cannot have cited_urls")
    return problems


def identity(obs: Dict[str, Any]) -> str:
    """Stable id: sha256 of the canonical JSON of the user-supplied fields, first 16 hex characters."""
    core = {k: v for k, v in obs.items() if k not in STORED_FIELDS}
    raw = json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _paths(dir_: str) -> Tuple[str, str]:
    return os.path.join(dir_, META_FILE), os.path.join(dir_, OBS_FILE)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _check_stamp(now: str) -> str:
    if not isinstance(now, str) or not _STAMP.match(now) or not _valid_date(now):
        raise ValueError("now must be an ISO 8601 timestamp")
    return now


def _regular(path: str, label: str) -> None:
    if os.path.islink(path) or not os.path.isfile(path):
        raise ValueError("%s is missing, a symlink or not a regular file: %s" % (label, path))


def init(dir_: str, *, now: Optional[str] = None) -> Dict[str, Any]:
    """Create the ledger directory files; refuses to touch an existing ledger (FileExistsError)."""
    created = _check_stamp(now or _now_iso())
    if os.path.islink(dir_):
        raise ValueError("ledger directory must not be a symlink")
    if os.path.exists(dir_) and not os.path.isdir(dir_):
        raise NotADirectoryError("not a directory: %s" % dir_)
    os.makedirs(dir_, exist_ok=True)
    meta_path, obs_path = _paths(dir_)
    meta = {"schema": LEDGER_SCHEMA, "created": created, "observations": OBS_FILE,
            "note": "Append-only. Corrections are new records; never edit or delete lines."}
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(obs_path, flags, 0o644)
    os.close(fd)
    try:
        fd = os.open(meta_path, flags, 0o644)
    except FileExistsError:
        os.unlink(obs_path)
        raise
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    return meta


def load(dir_: str) -> List[Dict[str, Any]]:
    """All stored observations in file order; ValueError on a malformed line or an uninitialized ledger."""
    meta_path, obs_path = _paths(dir_)
    _regular(meta_path, "ledger meta file")
    _regular(obs_path, "ledger observations file")
    if os.path.getsize(obs_path) > MAX_LEDGER_BYTES:
        raise ValueError("ledger exceeds %d bytes" % MAX_LEDGER_BYTES)
    out = []
    with open(obs_path, "r", encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rec = loads_json(line)
            except ValueError as exc:
                raise ValueError("%s line %d: invalid JSON (%s)" % (OBS_FILE, number, exc)) from None
            if not isinstance(rec, dict) or not rec.get("id") or rec.get("kind") not in KINDS:
                raise ValueError("%s line %d: not a ledger observation" % (OBS_FILE, number))
            out.append(rec)
    return out


def record_many(dir_: str, items: Iterable[Dict[str, Any]], *, now: str) -> List[Dict[str, Any]]:
    """Validate every observation first, then append all of them (all or nothing)."""
    stamp = _check_stamp(now)
    seen = {o["id"] for o in load(dir_)}
    stored: List[Dict[str, Any]] = []
    for index, obs in enumerate(list(items)):
        problems = validate_observation(obs)
        if problems:
            raise ValueError("observation %d is invalid: %s" % (index + 1, "; ".join(problems)))
        oid = identity(obs)
        if oid in seen:
            raise ValueError("observation %d duplicates %s; add observed_at or sample to record a repeated sample"
                             % (index + 1, oid))
        seen.add(oid)
        rec = dict(obs)
        rec.update(id=oid, recorded_at=stamp, v=RECORD_VERSION)
        stored.append(rec)
    _, obs_path = _paths(dir_)
    _regular(obs_path, "ledger observations file")
    fd = os.open(obs_path, os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "a", encoding="utf-8") as fh:
        for rec in stored:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n")
    return stored


def record(dir_: str, obs: Dict[str, Any], *, now: str) -> Dict[str, Any]:
    """Validate and append one observation; ValueError when invalid or a duplicate."""
    return record_many(dir_, [obs], now=now)[0]


def _day(obs: Dict[str, Any]) -> str:
    return str(obs.get("observed_at") or obs.get("recorded_at") or "")[:10]


def wilson(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Wilson score interval for k successes in n trials (n >= 1)."""
    if n < 1 or k < 0 or k > n:
        raise ValueError("wilson needs 0 <= k <= n and n >= 1")
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> Dict[str, float]:
    """Pooled two-proportion z test (two-sided). Observational evidence only, not causation."""
    if n1 < 1 or n2 < 1 or not (0 <= k1 <= n1) or not (0 <= k2 <= n2):
        raise ValueError("two_proportion_z needs 0 <= k <= n and n >= 1 for both groups")
    p1, p2 = k1 / n1, k2 / n2
    pooled = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se else 0.0
    return {"p1": p1, "p2": p2, "diff": p1 - p2, "z": z, "p_value": math.erfc(abs(z) / math.sqrt(2))}


def _rates(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {s: sum(1 for r in rows if r.get("status") == s) for s in STATUSES}
    k, n = counts["valid_present"], counts["valid_present"] + counts["valid_absent"]
    out: Dict[str, Any] = {"samples": len(rows), **counts, "n": n}
    if n:
        lo, hi = wilson(k, n)
        out.update(rate=round(k / n, 4), ci95=[round(lo, 4), round(hi, 4)], result="computed")
    else:
        out.update(rate=None, ci95=None, result="no computable result")
    if rows and (counts["empty"] + counts["error"]) * 2 > len(rows):
        out["warning"] = "more than half of the samples were empty or errors; treat this read as a failed measurement"
    return out


def summary(observations: Iterable[Dict[str, Any]], *, by: Sequence[str] = ("surface", "query_class"),
            window: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
    """Citation rates per group with Wilson 95% intervals; empty/error samples excluded from denominators."""
    fields = list(by)
    bad = [f for f in fields if f not in SUMMARY_FIELDS]
    if bad:
        raise ValueError("cannot group by %s; allowed: %s" % (", ".join(bad), ", ".join(SUMMARY_FIELDS)))
    if window is not None:
        if len(window) != 2 or not all(_DATE.match(str(w)) for w in window) or window[0] > window[1]:
            raise ValueError("window must be (START, END) dates YYYY-MM-DD with START <= END")
    rows = [o for o in observations if not window or window[0] <= _day(o) <= window[1]]
    panel = [o for o in rows if o.get("kind") == "panel"]
    groups: Dict[Tuple[str, ...], List[Dict[str, Any]]] = {}
    for obs in panel:
        groups.setdefault(tuple(json.dumps(obs.get(f)) for f in fields), []).append(obs)
    out_groups = []
    for key in sorted(groups):
        entry = {"group": {f: json.loads(v) for f, v in zip(fields, key)}}
        entry.update(_rates(groups[key]))
        out_groups.append(entry)
    metrics: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
    for obs in rows:
        if obs.get("kind") == "metric":
            metrics.setdefault((obs["source"], obs["metric"], obs.get("segment") or ""), []).append(obs)
    metric_rows = []
    for (source, metric, segment), items in sorted(metrics.items()):
        items = sorted(items, key=lambda o: (o["window"], o.get("recorded_at", ""), o["id"]))
        metric_rows.append({"source": source, "metric": metric, "segment": segment or None, "observations": len(items),
                            "series": [{"window": o["window"], "value": o["value"]} for o in items[-20:]]})
    return {"by": fields, "window": list(window) if window else None, "groups": out_groups, "totals": _rates(panel),
            "metrics": metric_rows, "experiments": sum(1 for o in rows if o.get("kind") == "experiment"),
            "note": "Rate = valid_present / (valid_present + valid_absent); empty and error samples are excluded "
                    "from every denominator. Intervals are Wilson 95%. Differences are observational, not causal."}


def _experiment_key(obs: Dict[str, Any]) -> str:
    if obs.get("experiment_id"):
        return str(obs["experiment_id"])
    raw = "\n".join(str(obs.get(k, "")) for k in ("hypothesis", "change", "deployed_at"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def experiments_status(observations: Iterable[Dict[str, Any]], *, today: date) -> List[Dict[str, Any]]:
    """Registered experiments with read-back dates and the latest recorded decision."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for obs in observations:
        if obs.get("kind") == "experiment":
            groups.setdefault(_experiment_key(obs), []).append(obs)
    out = []
    for key, items in groups.items():
        items = sorted(items, key=lambda o: (str(o.get("recorded_at", "")), str(o.get("id", ""))))
        first = items[0]
        deployed = date.fromisoformat(first["deployed_at"])
        days = sorted(set(first.get("readback_days") or DEFAULT_READBACK_DAYS))
        readbacks = []
        for d in days:
            due = deployed + timedelta(days=d)
            status = "passed" if due < today else "due" if due == today else "upcoming"
            readbacks.append({"days": d, "date": due.isoformat(), "status": status})
        decided = [o for o in items if o.get("decision")]
        decision = decided[-1]["decision"] if decided else None
        upcoming = [r["date"] for r in readbacks if r["status"] != "passed"]
        if decision:
            state = "decided"
        elif deployed > today:
            state = "not_deployed_yet"
        elif upcoming:
            state = "reading"
        else:
            state = "decision_due"
        out.append({"key": key, "hypothesis": first["hypothesis"], "change": first["change"],
                    "metric": first["metric"], "target_urls": list(first.get("target_urls") or []),
                    "control_urls": list(first.get("control_urls") or []), "deployed_at": first["deployed_at"],
                    "readbacks": readbacks, "next_readback": upcoming[0] if upcoming else None,
                    "decision": decision, "state": state, "records": len(items)})
    return sorted(out, key=lambda e: (e["deployed_at"], e["key"]))
