"""Drift snapshots, DRIFT001-DRIFT020 comparison and audit-history diff (WP06).

A snapshot stores one record per page (shape of ``sitescan.page_record``) keyed by
``normalize_url``. ``compare`` refuses to compute deltas when the snapshots are not
comparable (schema, tool major version, source type or base URL differ) and emits DRIFT020
instead. ``compare_findings`` diffs two result envelopes by finding id.
"""
from __future__ import annotations

import difflib
import functools
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .findings import Finding, make, truncate
from .rulesdb import RuleCatalog, default_catalog, load_data, thresholds

SNAPSHOT_SCHEMA = "seo-geo-god.snapshot/1"
RECORD_FIELDS = ("url", "status", "title", "meta_description", "canonical", "robots", "x_robots", "h1", "h2",
                 "hreflang", "jsonld_types", "og", "word_count", "internal_links", "content_hash", "noindex")
# Heuristic defaults (catalog titles DRIFT007/015/016); data/thresholds.json "drift" overrides them when present.
DEFAULT_LIMITS = {"h1_similarity_min": 0.5, "word_drop_pct": 50.0, "link_drop_pct": 50.0}
ROBOTS_MAX_CHARS = 512_000
_DEFAULT_PORTS = {"http": 80, "https": 443}
_DEFAULT_DIRECTIVES = {"all", "index", "follow"}
_SCHEMA_PREFIX = re.compile(r"^(?:https?://)?schema\.org/", re.I)
_WS = re.compile(r"\s+")


def normalize_url(url: str) -> str:
    """Lowercase scheme/host, drop default ports, userinfo, fragment and utm_* parameters,
    sort the query, strip a trailing slash except on the root. Path-only URLs stay path-only."""
    parts = urlsplit(str(url or "").strip())
    scheme = parts.scheme.lower()
    netloc = ""
    if parts.netloc:
        host = (parts.hostname or "").lower()
        netloc = "[%s]" % host if ":" in host else host
        try:
            port = parts.port
        except ValueError:
            port = None
        if port is not None and port != _DEFAULT_PORTS.get(scheme):
            netloc += ":%d" % port
    path = parts.path or "/"
    if len(path) > 1:
        path = path.rstrip("/") or "/"
    query = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                   if not k.lower().startswith("utm_"))
    return urlunsplit((scheme, netloc, path, urlencode(query), ""))


def _light(url: Optional[str]) -> Optional[str]:
    """Case-insensitive scheme/host and default-port comparison form; path and query kept exactly."""
    if not url:
        return None
    parts = urlsplit(str(url).strip())
    netloc = parts.netloc.lower()
    port = _DEFAULT_PORTS.get(parts.scheme.lower())
    if port and netloc.endswith(":%d" % port):
        netloc = netloc[: -len(":%d" % port)]
    return urlunsplit((parts.scheme.lower(), netloc, parts.path or "/", parts.query, ""))


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str))


def snapshot(records: List[Dict[str, Any]], *, source: Dict[str, Any], tool_version: str, now: str,
             robots_txt: Optional[str] = None) -> Dict[str, Any]:
    """Build a snapshot document from page records; the first record wins on a URL collision."""
    if not isinstance(source, dict) or not source.get("type"):
        raise ValueError("snapshot source needs a type (for example build-dir or live)")
    pages: Dict[str, Dict[str, Any]] = {}
    collisions: List[str] = []
    for rec in records:
        if not isinstance(rec, dict) or not rec.get("url"):
            raise ValueError("every snapshot record needs a url")
        key = normalize_url(rec["url"])
        if key in pages:
            collisions.append(str(rec["url"]))
            continue
        pages[key] = {f: _jsonable(rec.get(f)) for f in RECORD_FIELDS}
    out: Dict[str, Any] = {
        "schema": SNAPSHOT_SCHEMA, "created": now, "tool_version": str(tool_version),
        "source": {k: source[k] for k in ("type", "path", "url", "base_url", "profile") if source.get(k) is not None},
        "pages": dict(sorted(pages.items())), "robots_sha256": None, "robots_txt": None,
    }
    if robots_txt is not None:
        text = robots_txt.replace("\r\n", "\n").replace("\r", "\n")[:ROBOTS_MAX_CHARS]
        out["robots_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        out["robots_txt"] = text
    if collisions:
        out["url_collisions"] = sorted(collisions)
    return out


def _check_snapshot(doc: Any, label: str) -> None:
    if not isinstance(doc, dict) or not isinstance(doc.get("pages"), dict) or not isinstance(doc.get("source"), dict):
        raise ValueError("%s is not a seo-geo-god snapshot (needs source and pages objects)" % label)
    for key, rec in doc["pages"].items():
        if not isinstance(rec, dict):
            raise ValueError("%s page %r is not an object" % (label, key))


def _major(version: Any) -> str:
    return str(version or "").split(".")[0]


def _base(doc: Dict[str, Any]) -> Optional[str]:
    src = doc.get("source", {})
    base = src.get("base_url") or (src.get("url") if src.get("type") == "live" else None)
    return normalize_url(base) if base else None


def comparability(baseline: Dict[str, Any], current: Dict[str, Any]) -> List[str]:
    """Reasons the two snapshots cannot be compared (empty list = comparable)."""
    reasons = []
    if baseline.get("schema") != current.get("schema") or baseline.get("schema") != SNAPSHOT_SCHEMA:
        reasons.append("snapshot schema differs (%s vs %s)" % (baseline.get("schema"), current.get("schema")))
    if _major(baseline.get("tool_version")) != _major(current.get("tool_version")):
        reasons.append("tool major version differs (%s vs %s)" % (baseline.get("tool_version"),
                                                                 current.get("tool_version")))
    b_type, c_type = baseline["source"].get("type"), current["source"].get("type")
    if b_type != c_type:
        reasons.append("source type differs (%s vs %s)" % (b_type, c_type))
    if _base(baseline) != _base(current):
        reasons.append("base URL differs (%s vs %s)" % (_base(baseline), _base(current)))
    return reasons


def _limits() -> Dict[str, float]:
    out = dict(DEFAULT_LIMITS)
    extra = thresholds().get("drift")
    if isinstance(extra, dict):
        out.update({k: float(v) for k, v in extra.items() if k in DEFAULT_LIMITS and isinstance(v, (int, float))})
    return out


@functools.lru_cache(maxsize=1)
def retired_types() -> frozenset:
    """Types whose Google rich result is retired or phasing out (data/structured-data.json, whole-type rows)."""
    try:
        rows = load_data("structured-data").get("no_rich_result", [])
    except (OSError, ValueError, AttributeError):
        return frozenset()
    return frozenset(r["type"] for r in rows if isinstance(r, dict) and r.get("type") and not r.get("property"))


def _text(value: Any) -> str:
    return _WS.sub(" ", str(value or "")).strip()


def _noindex(rec: Dict[str, Any]) -> bool:
    if isinstance(rec.get("noindex"), bool):
        return rec["noindex"]
    return bool({"noindex", "none"} & _tokens(rec.get("robots"))) or any(
        {"noindex", "none"} & _tokens(v) for v in (rec.get("x_robots") or {}).values())


def _tokens(values: Any) -> Set[str]:
    return {str(v).strip().lower() for v in (values or []) if str(v).strip()}


def _directives(values: Any) -> List[str]:
    """Directive tokens other than noindex and defaults; `none` counts as nofollow here."""
    toks = _tokens(values)
    if "none" in toks:
        toks = (toks - {"none"}) | {"nofollow"}
    return sorted(toks - {"noindex"} - _DEFAULT_DIRECTIVES)


def _types(values: Any) -> Set[str]:
    return {_SCHEMA_PREFIX.sub("", str(v)) for v in (values or []) if str(v).strip()}


def _hreflang(values: Any) -> Set[Tuple[str, str]]:
    out = set()
    for pair in values or []:
        if isinstance(pair, (list, tuple)) and len(pair) == 2:
            out.add((str(pair[0]).lower(), _light(str(pair[1])) or ""))
    return out


def _drop_pct(before: Any, after: Any) -> Optional[float]:
    if not isinstance(before, (int, float)) or not isinstance(after, (int, float)) or before <= 0:
        return None
    return round((before - after) * 100.0 / before, 9)


class _Page:
    """Collects findings and field deltas for one page pair."""

    def __init__(self, key: str, base: Dict[str, Any], cur: Dict[str, Any], cat: RuleCatalog) -> None:
        self.key, self.base, self.cur, self.cat = key, base, cur, cat
        self.url = str(cur.get("url") or base.get("url") or key)
        self.findings: List[Finding] = []
        self.changes: Dict[str, Any] = {}

    def delta(self, field: str, before: Any, after: Any) -> None:
        self.changes[field] = {"before": truncate(before), "after": truncate(after)}

    def emit(self, rule: str, message: str, evidence: Dict[str, Any], severity: Optional[str] = None) -> None:
        self.findings.append(make(rule, message, catalog=self.cat, severity=severity, url=self.url,
                                  key=self.key, evidence=evidence))


def _compare_page(p: _Page, limits: Dict[str, float]) -> None:
    b, c = p.base, p.cur
    bs, cs = b.get("status"), c.get("status")
    if bs != cs:
        p.delta("status", bs, cs)
        if isinstance(bs, int) and isinstance(cs, int) and 200 <= bs < 300 and cs >= 400:
            p.emit("DRIFT001", "Status changed from %d to %d." % (bs, cs), {"before": bs, "after": cs})
    if _noindex(b) != _noindex(c):
        p.delta("noindex", _noindex(b), _noindex(c))
        if _noindex(c):
            p.emit("DRIFT002", "noindex added: the page was indexable in the baseline and now asks not to be indexed.",
                   {"robots": c.get("robots"), "x_robots": c.get("x_robots")})
    bc, cc = b.get("canonical"), c.get("canonical")
    if _light(bc) != _light(cc):
        p.delta("canonical", bc, cc)
        if bc and not cc:
            p.emit("DRIFT004", "Canonical link removed.", {"before": bc})
        elif bc and cc:
            p.emit("DRIFT003", "Canonical changed.", {"before": bc, "after": cc})
    _compare_text(p, "title", "DRIFT005", "DRIFT008", "Title removed.", "Title changed.")
    bh, ch = _text(b.get("h1")), _text(c.get("h1"))
    if bh != ch:
        p.delta("h1", b.get("h1"), c.get("h1"))
        if bh and not ch:
            p.emit("DRIFT006", "H1 removed.", {"before": bh})
        elif bh and ch:
            ratio = difflib.SequenceMatcher(None, bh.casefold(), ch.casefold()).ratio()
            if ratio < limits["h1_similarity_min"]:
                p.emit("DRIFT007", "H1 changed substantially (similarity %.2f)." % ratio,
                       {"before": bh, "after": ch, "similarity": round(ratio, 3),
                        "threshold": limits["h1_similarity_min"]})
    bd, cd = _text(b.get("meta_description")), _text(c.get("meta_description"))
    if bd != cd:
        p.delta("meta_description", b.get("meta_description"), c.get("meta_description"))
        if bd:
            p.emit("DRIFT009", "Meta description %s." % ("changed" if cd else "removed"), {"before": bd, "after": cd})
    _compare_types(p)
    bl, cl = _hreflang(b.get("hreflang")), _hreflang(c.get("hreflang"))
    if bl != cl:
        p.delta("hreflang", sorted(bl), sorted(cl))
        p.emit("DRIFT012", "hreflang set changed (%d removed, %d added)." % (len(bl - cl), len(cl - bl)),
               {"removed": sorted("%s %s" % x for x in bl - cl), "added": sorted("%s %s" % x for x in cl - bl)})
    _compare_directives(p)
    if b.get("og") and not c.get("og"):
        p.delta("og", sorted(b["og"]), [])
        p.emit("DRIFT014", "All Open Graph tags removed.", {"before": sorted(b["og"])})
    for field, rule, limit, label in (("word_count", "DRIFT015", limits["word_drop_pct"], "Word count"),
                                      ("internal_links", "DRIFT016", limits["link_drop_pct"], "Internal outlinks")):
        if b.get(field) != c.get(field):
            p.delta(field, b.get(field), c.get(field))
        drop = _drop_pct(b.get(field), c.get(field))
        if drop is not None and drop > limit:
            p.emit(rule, "%s dropped by %.0f%% (%s to %s)." % (label, drop, b.get(field), c.get(field)),
                   {"before": b.get(field), "after": c.get(field), "drop_pct": round(drop, 1), "threshold_pct": limit})
    if b.get("content_hash") and c.get("content_hash") and b["content_hash"] != c["content_hash"]:
        p.delta("content_hash", b["content_hash"], c["content_hash"])
        p.emit("DRIFT017", "Content hash changed (title, description, JSON-LD types or main text).",
               {"before": b["content_hash"][:16], "after": c["content_hash"][:16]})
    if [_text(x) for x in b.get("h2") or []] != [_text(x) for x in c.get("h2") or []]:
        p.delta("h2", b.get("h2"), c.get("h2"))


def _compare_text(p: _Page, field: str, removed_rule: str, changed_rule: str, removed: str, changed: str) -> None:
    before, after = _text(p.base.get(field)), _text(p.cur.get(field))
    if before == after:
        return
    p.delta(field, p.base.get(field), p.cur.get(field))
    if before and not after:
        p.emit(removed_rule, removed, {"before": before})
    elif before and after:
        p.emit(changed_rule, changed, {"before": before, "after": after})


def _compare_types(p: _Page) -> None:
    bt, ct = _types(p.base.get("jsonld_types")), _types(p.cur.get("jsonld_types"))
    if bt == ct:
        return
    p.delta("jsonld_types", sorted(bt), sorted(ct))
    gone, new = sorted(bt - ct), sorted(ct - bt)
    if gone:
        retired = sorted(set(gone) & retired_types())
        all_retired = len(retired) == len(gone)
        p.emit("DRIFT010", "JSON-LD types removed: %s%s." % (", ".join(gone),
                                                             " (no Google rich result for these types)" if all_retired else ""),
               {"removed": gone, "retired_types": retired}, severity="info" if all_retired else None)
    if new:
        p.emit("DRIFT011", "JSON-LD types added: %s." % ", ".join(new), {"added": new})


def _compare_directives(p: _Page) -> None:
    b, c = p.base, p.cur
    bm, cm = _directives(b.get("robots")), _directives(c.get("robots"))
    bx = {a: _directives(v) for a, v in (b.get("x_robots") or {}).items()}
    cx = {a: _directives(v) for a, v in (c.get("x_robots") or {}).items()}
    bx, cx = {a: v for a, v in bx.items() if v}, {a: v for a, v in cx.items() if v}
    if bm != cm or bx != cx:
        p.delta("directives", {"meta": bm, "x_robots": bx}, {"meta": cm, "x_robots": cx})
        p.emit("DRIFT013", "Robots meta or X-Robots-Tag directives changed (noindex aside).",
               {"meta_before": bm, "meta_after": cm, "x_robots_before": bx, "x_robots_after": cx})


def _meta(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {"created": doc.get("created"), "tool_version": doc.get("tool_version"),
            "source": dict(doc.get("source") or {}), "pages": len(doc.get("pages") or {})}


def compare(baseline: Dict[str, Any], current: Dict[str, Any],
            catalog: Optional[RuleCatalog] = None) -> Tuple[Dict[str, Any], List[Finding]]:
    """DRIFT001-DRIFT020. Returns (data, findings); data["deltas"] is None when not comparable."""
    cat = catalog or default_catalog()
    _check_snapshot(baseline, "baseline")
    _check_snapshot(current, "current")
    data: Dict[str, Any] = {"baseline": _meta(baseline), "current": _meta(current)}
    site_url = current["source"].get("base_url") or current["source"].get("url")
    affected = max(len(baseline["pages"]), len(current["pages"]), 1)
    reasons = comparability(baseline, current)
    if reasons:
        data.update(comparable=False, reasons=reasons, deltas=None)
        return data, [make("DRIFT020", "Snapshots are not comparable; deltas withheld: %s." % "; ".join(reasons),
                           catalog=cat, url=site_url, key="not-comparable", affected=affected,
                           evidence={"reasons": reasons})]
    limits = _limits()
    findings: List[Finding] = []
    pages: List[Dict[str, Any]] = []
    b_pages, c_pages = baseline["pages"], current["pages"]
    for key in sorted(set(b_pages) | set(c_pages)):
        if key not in c_pages:
            url = str(b_pages[key].get("url") or key)
            findings.append(make("DRIFT001", "Page removed: present in the baseline, missing now.", catalog=cat,
                                 url=url, key=key, evidence={"baseline_status": b_pages[key].get("status")}))
            pages.append({"url": key, "state": "removed"})
        elif key not in b_pages:
            url = str(c_pages[key].get("url") or key)
            findings.append(make("DRIFT018", "New page added.", catalog=cat, url=url, key=key,
                                 evidence={"status": c_pages[key].get("status")}))
            pages.append({"url": key, "state": "added"})
        else:
            page = _Page(key, b_pages[key], c_pages[key], cat)
            _compare_page(page, limits)
            findings.extend(page.findings)
            if page.changes:
                pages.append({"url": key, "state": "changed", "changes": page.changes})
    robots = {"changed": baseline.get("robots_sha256") != current.get("robots_sha256"),
              "before_sha256": baseline.get("robots_sha256"), "after_sha256": current.get("robots_sha256")}
    if robots["changed"]:
        diff = list(difflib.unified_diff((baseline.get("robots_txt") or "").splitlines(),
                                         (current.get("robots_txt") or "").splitlines(), "baseline", "current",
                                         n=0, lineterm=""))[2:]
        robots["diff"] = [truncate(line) for line in diff[:40]]
        state = "added" if not baseline.get("robots_sha256") else "removed" if not current.get("robots_sha256") \
            else "changed"
        findings.append(make("DRIFT019", "robots.txt %s since the baseline." % state, catalog=cat, url=site_url,
                             key="robots.txt", affected=affected, evidence={"state": state, "diff": diff[:10]}))
    counts = {s: sum(1 for p in pages if p["state"] == s) for s in ("added", "removed", "changed")}
    counts["unchanged"] = len(set(b_pages) & set(c_pages)) - counts["changed"]
    data.update(comparable=True, reasons=[], deltas={"summary": counts, "pages": pages, "robots": robots,
                                                     "limits": limits})
    return data, findings


def _target_id(env: Dict[str, Any]) -> Tuple[Any, ...]:
    t = env.get("target") or {}
    where = t.get("base_url") or t.get("url") or t.get("path")
    return (t.get("type"), normalize_url(where) if where else None, t.get("profile") or "default")


def compare_findings(old_env: Dict[str, Any], new_env: Dict[str, Any],
                     catalog: Optional[RuleCatalog] = None) -> Dict[str, Any]:
    """Diff two result envelopes by finding id; ValueError when they are not comparable."""
    cat = catalog or default_catalog()
    for env, label in ((old_env, "old"), (new_env, "new")):
        if not isinstance(env, dict) or env.get("tool") != "seo-geo-god" or not isinstance(env.get("findings"), list):
            raise ValueError("%s report is not a seo-geo-god result envelope" % label)
        if env.get("error"):
            raise ValueError("%s report recorded an error; refusing to compare" % label)
    problems = []
    if old_env.get("command") != new_env.get("command"):
        problems.append("command differs (%s vs %s)" % (old_env.get("command"), new_env.get("command")))
    if _target_id(old_env) != _target_id(new_env):
        problems.append("target differs")
    if _major(old_env.get("rules_version")) != _major(new_env.get("rules_version")):
        problems.append("rules major version differs (%s vs %s)" % (old_env.get("rules_version"),
                                                                   new_env.get("rules_version")))
    if problems:
        raise ValueError("reports are not comparable: " + "; ".join(problems))
    old = {f["id"]: f for f in old_env["findings"] if isinstance(f, dict) and f.get("id")}
    new = {f["id"]: f for f in new_env["findings"] if isinstance(f, dict) and f.get("id")}
    measured = set(cat.categories_for_checks(list((new_env.get("coverage") or {}).get("checks_run") or [])))

    def item(f: Dict[str, Any]) -> Dict[str, Any]:
        return {k: f.get(k) for k in ("id", "rule", "title", "severity", "priority", "category", "url", "file")}

    def order(ids: Set[str], src: Dict[str, Dict[str, Any]]) -> List[str]:
        return sorted(ids, key=lambda i: (str(src[i].get("rule")), i))

    persisting = []
    for fid in order(set(old) & set(new), new):
        row = item(new[fid])
        if old[fid].get("severity") != new[fid].get("severity"):
            row["severity_before"] = old[fid].get("severity")
        persisting.append(row)
    gone = []
    for fid in order(set(old) - set(new), old):
        row = item(old[fid])
        row["check_not_run"] = old[fid].get("category") not in measured
        gone.append(row)
    added = [item(new[f]) for f in order(set(new) - set(old), new)]
    return {"old": {"generated_at": old_env.get("generated_at"), "rules_version": old_env.get("rules_version"),
                    "findings": len(old)},
            "new": {"generated_at": new_env.get("generated_at"), "rules_version": new_env.get("rules_version"),
                    "findings": len(new)},
            "counts": {"added": len(added), "no_longer_observed": len(gone), "persisting": len(persisting)},
            "added": added, "no_longer_observed": gone, "persisting": persisting,
            "note": "'No longer observed' means the finding is absent from the newer report. It is not proof of a "
                    "fix when check_not_run is true or when the inputs changed."}
