"""Static performance risk signals and Lighthouse / PSI / CrUX readers (WP02).

Static checks (PERF001-007) read built HTML only; they are risk signals, not measurements.
Field Core Web Vitals come only from user-supplied CrUX (or PSI field) JSON; lab data from
Lighthouse never stands in for field data (PERF009). Thresholds: data/thresholds.json `cwv`
(fact F-T-13). FID is not read: INP replaced it on 2024-03-12.
"""
from __future__ import annotations

import functools
import re
from typing import Any, Dict, List, Optional

from .findings import Finding, make
from .rulesdb import RuleCatalog, default_catalog, thresholds

_METRIC_ALIASES = {
    "lcp": "lcp_ms", "lcp_ms": "lcp_ms", "largest_contentful_paint": "lcp_ms",
    "inp": "inp_ms", "inp_ms": "inp_ms", "interaction_to_next_paint": "inp_ms",
    "cls": "cls", "cumulative_layout_shift": "cls",
    "fcp": "fcp_ms", "fcp_ms": "fcp_ms", "first_contentful_paint": "fcp_ms",
    "ttfb": "ttfb_ms", "ttfb_ms": "ttfb_ms", "time_to_first_byte": "ttfb_ms",
    "experimental_time_to_first_byte": "ttfb_ms",
}
CWV = ("lcp_ms", "inp_ms", "cls")
_LAB_AUDITS = {"largest-contentful-paint": "lcp_ms", "cumulative-layout-shift": "cls",
               "first-contentful-paint": "fcp_ms", "total-blocking-time": "tbt_ms", "speed-index": "si_ms",
               "interactive": "tti_ms", "server-response-time": "ttfb_ms"}
_PSI_FIELD = {"LARGEST_CONTENTFUL_PAINT_MS": "lcp_ms", "INTERACTION_TO_NEXT_PAINT": "inp_ms",
              "CUMULATIVE_LAYOUT_SHIFT_SCORE": "cls", "FIRST_CONTENTFUL_PAINT_MS": "fcp_ms",
              "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "ttfb_ms"}
_UNLOAD = re.compile(r"addEventListener\s*\(\s*['\"](?:before)?unload['\"]|\bon(?:before)?unload\s*=", re.I)
_BLOCKING_TYPES = ("", "text/javascript", "application/javascript", "application/ecmascript", "text/ecmascript")
LAB_NOTE = "Lighthouse lab data is a diagnostic; Core Web Vitals assessment needs field data (CrUX)."
AGENTIC_NOTE = ("Experimental Chrome Lighthouse category (not Google Search); pass ratio of counted audits, "
                "score >= 0.9 passes.")


@functools.lru_cache(maxsize=1)
def _cwv() -> Dict[str, Any]:
    block = thresholds().get("cwv")
    return block if isinstance(block, dict) else {}


def rate(metric: str, value: float) -> str:
    """good | needs-improvement | poor at the documented thresholds (value <= good is good)."""
    name = _METRIC_ALIASES.get(str(metric).lower())
    limits = _cwv().get(name) if name else None
    if not limits or len(limits) != 2:
        raise ValueError("unknown metric %r" % metric)
    v = float(value)
    return "good" if v <= limits[0] else "needs-improvement" if v <= limits[1] else "poor"


def _number(value: Any) -> Optional[float]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return v if v == v and v not in (float("inf"), float("-inf")) else None


# ---------------------------------------------------------------------------------------- static

def _sized(img: Dict[str, Any]) -> bool:
    style = (img.get("style") or "").lower().replace(" ", "")
    if "aspect-ratio" in style:
        return True
    if (img.get("width") or "").strip() and (img.get("height") or "").strip():
        return True
    return bool(re.search(r"(?:^|;)width:", style) and re.search(r"(?:^|;)height:", style))


def check_static(page: Any, catalog: Optional[RuleCatalog] = None, *, url: Optional[str] = None,
                 file: Optional[str] = None) -> List[Finding]:
    """PERF001-007 for one PageDoc (risk signals from built HTML; not field measurements)."""
    cat = catalog or default_catalog()
    out: List[Finding] = []
    loc = {"url": url if url is not None else getattr(page, "url", None),
           "file": file if file is not None else getattr(page, "path", None)}

    def emit(rule: str, message: str, **kw: Any) -> None:
        if cat.get(rule).status == "v1":
            out.append(make(rule, message, catalog=cat, **dict(loc, **kw)))

    images = [i for i in getattr(page, "images", []) or [] if i.get("src") and not str(i["src"]).startswith("data:")]
    unsized = [i for i in images if not _sized(i)]
    if unsized:
        emit("PERF001", "%d images lack width/height or aspect-ratio." % len(unsized), key="unsized",
             line=unsized[0].get("line"), evidence={"observed": [i["src"] for i in unsized][:10],
                                                    "count": len(unsized)})
    lcp = next((i for i in images if i.get("in_first_viewport_guess")), None)
    if lcp is not None:
        if lcp.get("lazy"):
            emit("PERF002", "Likely LCP image %s is lazy-loaded (%s)." % (lcp["src"], lcp["lazy"]), key="lcp-lazy",
                 line=lcp.get("line"), confidence="medium", evidence={"observed": lcp["src"], "lazy": lcp["lazy"]})
        preloaded = any("preload" in (t.get("rel") or []) and t.get("as") == "image" and (
            t.get("href") == lcp["src"] or (t.get("imagesrcset") and lcp["src"] in t["imagesrcset"]))
            for t in getattr(page, "link_tags", []) or [])
        if (lcp.get("fetchpriority") or "").strip().lower() != "high" and not preloaded:
            emit("PERF003", "Likely LCP image %s has neither fetchpriority=high nor a preload." % lcp["src"],
                 key="lcp-priority", line=lcp.get("line"), confidence="low", evidence={"observed": lcp["src"]})
    blocking = [s for s in getattr(page, "scripts", []) or [] if s.get("in_head") and s.get("src")
                and not s.get("async") and not s.get("defer") and not s.get("module")
                and (s.get("type") or "") in _BLOCKING_TYPES]
    if blocking:
        emit("PERF004", "%d render-blocking scripts in the head." % len(blocking), key="blocking",
             line=blocking[0].get("line"), evidence={"observed": [s["src"] for s in blocking][:10]})
    body = getattr(page, "body_attrs", {}) or {}
    unload = [k for k in ("onunload", "onbeforeunload") if k in body]
    unload += ["inline script line %s" % s.get("line") for s in getattr(page, "scripts", []) or []
               if not s.get("src") and _UNLOAD.search(s.get("inline_text") or "")]
    if unload:
        emit("PERF005", "unload/beforeunload handler found (%s)." % ", ".join(unload[:3]), key="unload",
             evidence={"observed": unload[:5]})
    prerender = [t for t in getattr(page, "link_tags", []) or [] if "prerender" in (t.get("rel") or [])]
    if prerender:
        emit("PERF006", "%d deprecated rel=prerender links." % len(prerender), key="prerender",
             line=prerender[0].get("line"), evidence={"observed": [t.get("href") for t in prerender][:5]})
    heavy = int(thresholds().get("heavy_html_bytes", 1048576))
    size = int(getattr(page, "raw_size", 0) or 0)
    if size > heavy:
        emit("PERF007", "HTML document is %d bytes (heavy above %d)." % (size, heavy), key="heavy",
             evidence={"observed": size, "threshold": heavy})
    return out


# ---------------------------------------------------------------------------------------- readers

def _ratings(metrics: Dict[str, Any]) -> Dict[str, str]:
    out = {}
    for name, value in metrics.items():
        if name in ("lcp_ms", "inp_ms", "cls", "fcp_ms", "ttfb_ms") and value is not None:
            out[name] = rate(name, value)
    return out


def _agentic(lhr: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    categories = lhr.get("categories") if isinstance(lhr.get("categories"), dict) else {}
    cat_id = next((c for c in sorted(categories) if "agentic" in c), None)
    if cat_id is None or not isinstance(categories[cat_id], dict):
        return None
    audits = lhr.get("audits") if isinstance(lhr.get("audits"), dict) else {}
    passed = counted = 0
    for ref in categories[cat_id].get("auditRefs") or []:
        if not isinstance(ref, dict) or ref.get("group") == "hidden":
            continue
        audit = audits.get(ref.get("id")) if isinstance(audits.get(ref.get("id")), dict) else {}
        mode = audit.get("scoreDisplayMode")
        if mode in ("manual", "notApplicable", "informative"):
            continue
        counted += 1
        score = _number(audit.get("score"))
        if mode != "error" and score is not None and score >= 0.9:
            passed += 1
    return {"category": cat_id, "passed": passed, "counted": counted, "display": "%d/%d" % (passed, counted),
            "note": AGENTIC_NOTE}


def _psi_field(block: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(block, dict) or not isinstance(block.get("metrics"), dict):
        return None
    metrics: Dict[str, Any] = {}
    for key, name in _PSI_FIELD.items():
        entry = block["metrics"].get(key)
        value = _number(entry.get("percentile")) if isinstance(entry, dict) else None
        if value is not None:
            metrics[name] = round(value / 100.0, 4) if name == "cls" else value   # PSI reports CLS x 100
    if not metrics:
        return None
    return {"source": "psi-field", "kind": "field", "url": block.get("id"), "metrics": metrics,
            "ratings": _ratings(metrics), "overall": block.get("overall_category")}


def read_lighthouse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize a PageSpeed Insights v5 response or a raw Lighthouse result (LHR); ValueError otherwise."""
    if not isinstance(data, dict):
        raise ValueError("Lighthouse JSON must be an object")
    lhr = data.get("lighthouseResult") if isinstance(data.get("lighthouseResult"), dict) else data
    if not isinstance(lhr.get("audits"), dict) and not isinstance(lhr.get("categories"), dict):
        raise ValueError("not a Lighthouse result or PageSpeed Insights response")
    categories, nulls = {}, []
    for cid, cat in sorted((lhr.get("categories") or {}).items()):
        score = _number(cat.get("score")) if isinstance(cat, dict) else None
        if score is None:
            nulls.append(cid)   # null scores are skipped, never treated as 0
        else:
            categories[cid] = int(round(score * 100))
    metrics: Dict[str, Any] = {}
    audits = lhr.get("audits") if isinstance(lhr.get("audits"), dict) else {}
    for audit_id, name in _LAB_AUDITS.items():
        audit = audits.get(audit_id)
        value = _number(audit.get("numericValue")) if isinstance(audit, dict) else None
        if value is not None:
            metrics[name] = round(value, 4) if name == "cls" else int(round(value))
    settings = lhr.get("configSettings") if isinstance(lhr.get("configSettings"), dict) else {}
    return {"source": "psi" if "lighthouseResult" in data else "lighthouse", "kind": "lab",
            "lighthouse_version": lhr.get("lighthouseVersion"), "requested_url": lhr.get("requestedUrl"),
            "final_url": lhr.get("finalDisplayedUrl") or lhr.get("finalUrl"), "fetch_time": lhr.get("fetchTime"),
            "form_factor": settings.get("formFactor"), "categories": categories, "null_categories": nulls,
            "metrics": metrics, "ratings": _ratings(metrics), "agentic": _agentic(lhr),
            "field": _psi_field(data.get("loadingExperience")) or _psi_field(data.get("originLoadingExperience")),
            "note": LAB_NOTE}


def read_crux(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize a CrUX API (or CrUX History API) record: p75 per metric, CLS strings handled."""
    if not isinstance(data, dict):
        raise ValueError("CrUX JSON must be an object")
    record = data.get("record") if isinstance(data.get("record"), dict) else data
    raw = record.get("metrics")
    if not isinstance(raw, dict):
        raise ValueError("not a CrUX record (no metrics)")
    metrics: Dict[str, Any] = {}
    histograms: Dict[str, Dict[str, float]] = {}
    unrated = []
    for key, entry in sorted(raw.items()):
        if not isinstance(entry, dict):
            continue
        name = _METRIC_ALIASES.get(key)
        if name is None:
            unrated.append(key)
            continue
        p75 = None
        if isinstance(entry.get("percentiles"), dict):
            p75 = _number(entry["percentiles"].get("p75"))
        elif isinstance(entry.get("percentilesTimeseries"), dict):
            series = [_number(v) for v in entry["percentilesTimeseries"].get("p75s") or []]
            p75 = next((v for v in reversed(series) if v is not None), None)
        if p75 is not None:
            metrics[name] = round(p75, 4) if name == "cls" else p75
        bins = entry.get("histogram")
        if isinstance(bins, list) and len(bins) == 3:
            histograms[name] = {label: round(_number(b.get("density")) or 0.0, 4)
                                for label, b in zip(("good", "needs-improvement", "poor"), bins) if isinstance(b, dict)}
    key = record.get("key") if isinstance(record.get("key"), dict) else {}
    return {"source": "crux", "kind": "field", "url": key.get("url") or key.get("origin"),
            "form_factor": key.get("formFactor"), "collection_period": record.get("collectionPeriod")
            or record.get("collectionPeriods"), "metrics": metrics, "ratings": _ratings(metrics),
            "histograms": histograms, "unrated": unrated,
            "experimental": [k for k in unrated if re.search(r"experimental|soft_nav|(?:^|_)ad_", k)]}


def check_field(summary: Dict[str, Any], catalog: Optional[RuleCatalog] = None) -> List[Finding]:
    """PERF008 per Core Web Vital rated needs-improvement or poor; PERF009 when only lab data exists.

    `summary` is a read_crux() or read_lighthouse() result, or {"field": ..., "lab": ...}.
    """
    cat = catalog or default_catalog()
    if summary.get("kind") == "field":
        field, lab = summary, None
    elif summary.get("kind") == "lab":
        field, lab = summary.get("field"), summary
    else:
        field, lab = summary.get("field"), summary.get("lab")
    out: List[Finding] = []
    metrics = (field or {}).get("metrics") or {}
    if any(m in metrics for m in CWV):
        limits = _cwv()
        for m in CWV:
            if m in metrics and rate(m, metrics[m]) != "good":
                rating = rate(m, metrics[m])
                out.append(make("PERF008", "Field %s p75 is %s (%s)." % (m.split("_")[0].upper(), metrics[m], rating),
                                catalog=cat, url=field.get("url"), key="field:" + m,
                                evidence={"metric": m, "p75": metrics[m], "rating": rating,
                                          "thresholds": limits.get(m), "source": field.get("source")}))
    elif lab is not None:
        out.append(make("PERF009", "Only Lighthouse lab data was supplied; no field data.", catalog=cat,
                        url=lab.get("final_url") or lab.get("requested_url"), key="lab-only",
                        evidence={"source": lab.get("source"), "note": LAB_NOTE}))
    return out
