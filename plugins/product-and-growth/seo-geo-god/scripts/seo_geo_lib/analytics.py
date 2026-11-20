"""Offline analyses of user-supplied exports: Search Console, GA4, access logs, trackers (WP06).

Inputs are untrusted data. Nothing here fetches anything. Defaults come from
``data/thresholds.json`` (block ``gsc``); every number they produce is a heuristic reading of
the user's own export, never a forecast. Bot counts are labelled "claimed (unverified)"
because a user-agent string is only a claim.
"""
from __future__ import annotations

import csv
import io
import math
import os
import re
from datetime import date
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple
from urllib.parse import parse_qsl, urlsplit

from .rulesdb import load_data, loads_json, thresholds

MAX_EXPORT_BYTES = 52_428_800
MAX_TRACKER_BYTES = 10_485_760
CLAIMED = "claimed (unverified)"
GSC_DIMENSIONS = ("query", "page", "country", "device", "date", "search_appearance", "hour")
UPDATE_KINDS = ("core", "spam", "discover", "policy", "documentation", "structured-data", "ai-control", "crawling")
# Heuristic fallbacks used until data/thresholds.json carries them (gsc.movers_min_impressions,
# gsc.site_curve_min_impressions, gsc.aio.min_impressions, gsc.serp_domination); SERP-domination rule adapted
# from the notfair-plugin GSC analysis (MIT).
FALLBACKS = {"movers_min_impressions": 10, "site_curve_min_impressions": 100, "aio_min_impressions": 100,
             "serp_domination": {"max_position": 5.0, "max_spread": 2.0}}
_INT_FIELDS = ("clicks", "impressions", "sessions", "users")
# Best-effort header aliases (compacted: casefolded, letters and digits only). Unknown columns are ignored.
_ALIASES = {
    "query": ("topqueries", "query", "queries", "searchquery", "häufigstesuchanfragen", "suchanfrage",
              "suchanfragen", "consultasprincipales", "consulta", "consultas", "requêteslesplusfréquentes",
              "requête", "requêtes"),
    "page": ("toppages", "page", "pages", "url", "seite", "seiten", "páginasprincipales", "página", "páginas"),
    "country": ("country", "countries", "land", "länder", "país", "países", "pays"),
    "device": ("device", "devices", "gerät", "geräte", "dispositivo", "dispositivos", "appareil", "appareils"),
    "date": ("date", "dates", "datum", "fecha"),
    "search_appearance": ("searchappearance",),
    "hour": ("hour",),
    "clicks": ("clicks", "klicks", "clics"),
    "impressions": ("impressions", "impressionen", "impresiones"),
    "ctr": ("ctr", "clickthroughrate", "klickrate"),
    "position": ("position", "averageposition", "avgposition", "durchschnittlicheposition", "posición",
                 "posiciónmedia", "positionmoyenne"),
    "source": ("sessionsource", "source"),
    "medium": ("sessionmedium", "medium"),
    "source_medium": ("sessionsourcemedium", "sourcemedium"),
    "landing_page": ("landingpage", "landingpagequerystring", "landingpageplusquerystring"),
    "sessions": ("sessions",),
    "users": ("totalusers", "users", "activeusers"),
    "channel_group": ("sessiondefaultchannelgroup", "defaultchannelgroup", "sessionprimarychannelgroup",
                      "primarychannelgroup", "channelgroup"),
    "referrer": ("pagereferrer", "referrer", "referer"),
}
_HEADER = {alias: name for name, aliases in _ALIASES.items() for alias in aliases}
_LOG_RE = re.compile(r'^\S+ \S+ \S+ \[[^\]]*\] "((?:[^"\\]|\\.)*)" (\d{3}|-) \S+'
                     r'(?: "((?:[^"\\]|\\.)*)" "((?:[^"\\]|\\.)*)")?')
_TRACKER_FALSEY = {"false", "0", "no", "n", ""}
_SECRET_KEY = re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|credential|private[_-]?key|oauth|bearer|"
                         r"session[_-]?id)")
_SECRET_VALUE = re.compile(r"(AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|"
                           r"xox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
_QUERY_CLASSES = ("branded", "generic", "commercial", "informational", "navigational", "other")
_GUARDRAILS = ("no_duplicate_query_owners", "no_auto_publish_visible_copy", "no_fabricated_proof",
               "require_fresh_crawl_before_verdict")


# ----------------------------------------------------------------------------- reading

def _read_text(path: str, max_bytes: int) -> str:
    """Read a user-supplied export: regular file, size-capped, never a .env file."""
    name = os.path.basename(str(path))
    if name.startswith(".env"):
        raise ValueError("refusing to read environment files")
    if not os.path.isfile(path):
        raise ValueError("not a regular file: %s" % path)
    size = os.path.getsize(path)
    if size > max_bytes:
        raise ValueError("%s is %d bytes; limit is %d" % (path, size, max_bytes))
    with open(path, "rb") as fh:
        raw = fh.read(max_bytes + 1)
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8-sig", errors="replace")


def _lines(path: str, max_bytes: int) -> Iterator[str]:
    yield from _read_text(path, max_bytes).splitlines()


def _compact(header: str) -> str:
    return "".join(ch for ch in str(header).casefold() if ch.isalnum())


def _canonical(header: str) -> Optional[str]:
    return _HEADER.get(_compact(header))


def _to_int(text: Any, where: str) -> int:
    if isinstance(text, bool):
        raise ValueError("%s: not a number" % where)
    if isinstance(text, (int, float)):
        return int(text)
    s = re.sub(r"[\s\u00a0',]", "", str(text))
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    if s in ("", "-"):
        return 0
    try:
        return int(float(s))
    except ValueError:
        raise ValueError("%s: %r is not a number" % (where, text)) from None


def _to_float(text: Any, where: str) -> Optional[float]:
    if isinstance(text, (int, float)) and not isinstance(text, bool):
        return float(text)
    s = str(text).strip().replace("\u00a0", "").replace(" ", "")
    if s in ("", "-"):
        return None
    if re.fullmatch(r"-?\d+,\d+", s):
        s = s.replace(",", ".")
    s = s.replace(",", "")
    try:
        value = float(s)
    except ValueError:
        raise ValueError("%s: %r is not a number" % (where, text)) from None
    if not math.isfinite(value):
        raise ValueError("%s: %r is not finite" % (where, text))
    return value


def _to_ctr(text: Any, where: str) -> Optional[float]:
    if isinstance(text, str) and "%" in text:
        value = _to_float(text.replace("%", ""), where)
        return None if value is None else round(value / 100.0, 6)
    value = _to_float(text, where)
    return round(value / 100.0, 6) if value is not None and value > 1 else value


def _convert(name: str, value: Any, where: str) -> Any:
    if name in _INT_FIELDS:
        return _to_int(value, where)
    if name == "position":
        return _to_float(value, where)
    if name == "ctr":
        return _to_ctr(value, where)
    return str(value).strip() if value is not None else None


def _finish(row: Dict[str, Any]) -> Dict[str, Any]:
    if row.get("source_medium") and not row.get("source"):
        source, _, medium = str(row["source_medium"]).partition(" / ")
        row["source"] = source.strip()
        row.setdefault("medium", medium.strip())
    if "clicks" in row and "impressions" in row and row.get("ctr") is None:
        row["ctr"] = row["clicks"] / row["impressions"] if row["impressions"] else 0.0
    return row


def _rows_from_csv(text: str) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    start = 0
    while start < len(lines) and (not lines[start].strip() or lines[start].lstrip().startswith("#")):
        start += 1
    if start >= len(lines):
        raise ValueError("export is empty")
    block = [lines[start]]
    for line in lines[start + 1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            break
        block.append(line)
    delimiter = max((",", ";", "\t"), key=lambda d: lines[start].count(d))
    reader = csv.reader(io.StringIO("\n".join(block)), delimiter=delimiter)
    names = [_canonical(h) for h in next(reader)]
    if not any(names):
        raise ValueError("no recognised columns in the export header")
    rows = []
    for number, cells in enumerate(reader, start=start + 2):
        if not any(c.strip() for c in cells) or (cells and cells[0].strip().casefold() == "grand total"):
            continue
        row: Dict[str, Any] = {}
        for name, cell in zip(names, cells):
            if name and name not in row:
                row[name] = _convert(name, cell, "line %d %s" % (number, name))
        rows.append(_finish(row))
    return rows


def _dimension_names(dimensions: Sequence[str]) -> List[str]:
    out = []
    for d in dimensions:
        name = "search_appearance" if d in ("searchAppearance", "search_appearance") else str(d).strip()
        if name not in GSC_DIMENSIONS:
            raise ValueError("unknown dimension %r; use %s" % (d, ", ".join(GSC_DIMENSIONS)))
        out.append(name)
    return out


def _rows_from_json(doc: Any, dimensions: Optional[Sequence[str]]) -> List[Dict[str, Any]]:
    if isinstance(doc, dict) and isinstance(doc.get("rows"), list):
        items = doc["rows"]
    elif isinstance(doc, list):
        items = doc
    elif isinstance(doc, dict) and not doc.get("rows"):
        return []
    else:
        raise ValueError("JSON export must be a Search Analytics response {\"rows\": [...]} or a list of rows")
    dims = _dimension_names(dimensions) if dimensions else None
    rows = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ValueError("row %d is not an object" % index)
        row: Dict[str, Any] = {}
        if "keys" in item:
            keys = item["keys"] if isinstance(item["keys"], list) else []
            if not dims or len(dims) != len(keys):
                raise ValueError("Search Analytics rows carry %d keys; pass matching --dimensions (for example "
                                 "query,page)" % len(keys))
            row.update({d: str(k) for d, k in zip(dims, keys)})
        for key, value in item.items():
            name = _canonical(key)
            if name and name not in row and value is not None:
                row[name] = _convert(name, value, "row %d %s" % (index, name))
        rows.append(_finish(row))
    return rows


def load_rows(path: str, *, dimensions: Optional[Sequence[str]] = None,
              max_bytes: int = MAX_EXPORT_BYTES) -> List[Dict[str, Any]]:
    """Rows with canonical keys (query, page, clicks, impressions, ctr as a 0-1 fraction, position,
    source, medium, landing_page, sessions, ...) from a CSV export or Search Analytics API JSON."""
    text = _read_text(path, max_bytes)
    if text.lstrip().startswith(("{", "[")):
        rows = _rows_from_json(loads_json(text), dimensions)
    else:
        rows = _rows_from_csv(text)
        if dimensions:
            missing = [d for d in _dimension_names(dimensions) if rows and d not in rows[0]]
            if missing:
                raise ValueError("export has no %s column" % ", ".join(missing))
    return rows


# ----------------------------------------------------------------------------- Search Console analyses

def _gsc() -> Dict[str, Any]:
    return thresholds()["gsc"]


def _require(rows: Sequence[Dict[str, Any]], fields: Sequence[str], what: str) -> None:
    missing = [f for f in fields if rows and any(f not in r for r in rows)]
    if missing:
        raise ValueError("%s needs a %s column in every row" % (what, " and ".join(missing)))


def _aggregate(rows: Iterable[Dict[str, Any]], keys: Sequence[str]) -> Dict[Tuple[str, ...], Dict[str, Any]]:
    """Sum clicks/impressions per key; position is impression-weighted, CTR recomputed."""
    acc: Dict[Tuple[str, ...], List[float]] = {}
    for r in rows:
        k = tuple(str(r.get(f) or "") for f in keys)
        a = acc.setdefault(k, [0, 0, 0.0, 0.0, 0])
        imp = int(r.get("impressions") or 0)
        pos = r.get("position")
        a[0] += int(r.get("clicks") or 0)
        a[1] += imp
        if pos is not None:
            a[2] += pos * imp
            a[3] += pos
            a[4] += 1
    out = {}
    for k, (clicks, imp, weighted, plain, count) in acc.items():
        position = weighted / imp if imp else (plain / count if count else None)
        out[k] = {"clicks": int(clicks), "impressions": int(imp), "ctr": clicks / imp if imp else 0.0,
                  "position": position}
    return out


def _view(keys: Sequence[str], k: Tuple[str, ...], m: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = dict(zip(keys, k))
    row.update(clicks=m["clicks"], impressions=m["impressions"], ctr=round(m["ctr"], 4),
               position=None if m["position"] is None else round(m["position"], 2))
    return row


def _dims_present(rows: Sequence[Dict[str, Any]]) -> List[str]:
    dims = [d for d in ("query", "page") if rows and all(d in r for r in rows)]
    if not dims:
        raise ValueError("export needs a query or page column")
    return dims


def _bucket(position: float) -> int:
    return max(1, int(math.floor(position + 0.5)))


def default_ctr_curve() -> Dict[Any, float]:
    """The heuristic default curve from data/thresholds.json (positions 1-10 and "11-20")."""
    raw = _gsc()["default_ctr_curve"]
    return {(int(k) if k.isdigit() else k): float(v) for k, v in raw.items() if k != "source"}


def _expected(curve: Dict[Any, float], position: Optional[float]) -> Optional[float]:
    if position is None:
        return None
    b = _bucket(position)
    if b <= 10:
        value = curve.get(b, curve.get(str(b)))
    elif b <= 20:
        value = curve.get("11-20")
    else:
        value = None
    return None if value is None else float(value)


def movers(cur: Sequence[Dict[str, Any]], prev: Sequence[Dict[str, Any]], *, key: str = "query",
           min_delta: Optional[float] = None, min_impressions: Optional[int] = None) -> Dict[str, Any]:
    """Position winners/losers (>= min_delta positions, both periods >= min_impressions), new and lost keys."""
    cfg = _gsc()
    min_delta = float(cfg["movers_min_delta"] if min_delta is None else min_delta)
    if min_impressions is None:
        min_impressions = int(cfg.get("movers_min_impressions", FALLBACKS["movers_min_impressions"]))
    _require(cur, [key], "movers")
    _require(prev, [key], "movers")
    a, b = _aggregate(cur, [key]), _aggregate(prev, [key])
    out: Dict[str, Any] = {"key": key, "min_delta": min_delta, "min_impressions": min_impressions,
                           "winners": [], "losers": [], "new": [], "lost": []}
    for k in sorted(set(a) | set(b)):
        c, p = a.get(k), b.get(k)
        if c and p:
            if c["impressions"] < min_impressions or p["impressions"] < min_impressions:
                continue
            if c["position"] is None or p["position"] is None:
                continue
            change = round(p["position"] - c["position"], 6)
            row = {key: k[0], "clicks_cur": c["clicks"], "clicks_prev": p["clicks"],
                   "clicks_change": c["clicks"] - p["clicks"], "impressions_cur": c["impressions"],
                   "impressions_prev": p["impressions"], "position_cur": round(c["position"], 2),
                   "position_prev": round(p["position"], 2), "position_change": round(change, 2)}
            if change >= min_delta:
                out["winners"].append(row)
            elif change <= -min_delta:
                out["losers"].append(row)
        elif c and c["impressions"] >= min_impressions:
            out["new"].append(_view([key], k, c))
        elif p and p["impressions"] >= min_impressions:
            out["lost"].append(_view([key], k, p))
    out["winners"].sort(key=lambda r: (-r["clicks_change"], -r["position_change"], r[key]))
    out["losers"].sort(key=lambda r: (r["clicks_change"], r["position_change"], r[key]))
    out["new"].sort(key=lambda r: (-r["impressions"], r[key]))
    out["lost"].sort(key=lambda r: (-r["clicks"], -r["impressions"], r[key]))
    return out


def decay(cur: Sequence[Dict[str, Any]], prev: Sequence[Dict[str, Any]], *, key: str = "page",
          drop_pct: Optional[float] = None, min_prev_clicks: Optional[int] = None) -> List[Dict[str, Any]]:
    """Keys whose clicks fell by more than drop_pct from a previous period with >= min_prev_clicks."""
    cfg = _gsc()
    drop_pct = float(cfg["decay_pct"] if drop_pct is None else drop_pct)
    min_prev_clicks = int(cfg["min_prev_clicks"] if min_prev_clicks is None else min_prev_clicks)
    _require(cur, [key], "decay")
    _require(prev, [key], "decay")
    a, b = _aggregate(cur, [key]), _aggregate(prev, [key])
    out = []
    for k, p in b.items():
        if p["clicks"] < min_prev_clicks or p["clicks"] <= 0:
            continue
        c = a.get(k)
        now_clicks = c["clicks"] if c else 0
        drop = round((p["clicks"] - now_clicks) * 100.0 / p["clicks"], 9)
        if drop > drop_pct:
            out.append({key: k[0], "clicks_prev": p["clicks"], "clicks_cur": now_clicks,
                        "clicks_lost": p["clicks"] - now_clicks, "drop_pct": round(drop, 1),
                        "impressions_prev": p["impressions"], "impressions_cur": c["impressions"] if c else 0,
                        "missing_in_current": c is None})
    return sorted(out, key=lambda r: (-r["clicks_lost"], r[key]))


def site_ctr_curve(rows: Sequence[Dict[str, Any]], *, min_impressions: Optional[int] = None) -> Dict[Any, float]:
    """Site-calibrated CTR by rounded position 1-10 and "11-20"; buckets below min_impressions are omitted."""
    if min_impressions is None:
        min_impressions = int(_gsc().get("site_curve_min_impressions", FALLBACKS["site_curve_min_impressions"]))
    acc: Dict[Any, List[int]] = {}
    for r in rows:
        pos, imp = r.get("position"), int(r.get("impressions") or 0)
        if pos is None or imp <= 0:
            continue
        b = _bucket(pos)
        label = b if b <= 10 else "11-20" if b <= 20 else None
        if label is not None:
            a = acc.setdefault(label, [0, 0])
            a[0] += int(r.get("clicks") or 0)
            a[1] += imp
    order = [b for b in range(1, 11) if b in acc] + (["11-20"] if "11-20" in acc else [])
    return {b: round(acc[b][0] / acc[b][1], 4) for b in order if acc[b][1] >= min_impressions}


def ctr_anomalies(rows: Sequence[Dict[str, Any]], *, max_position: Optional[float] = None,
                  max_ctr: Optional[float] = None, min_impressions: Optional[int] = None,
                  curve: Optional[Dict[Any, float]] = None, max_ratio: Optional[float] = None) -> List[Dict[str, Any]]:
    """High-impression, top-position rows with low CTR: below max_ctr, or below max_ratio x the curve CTR."""
    cfg = _gsc()
    anomaly = cfg["ctr_anomaly"]
    max_position = float(anomaly["max_position"] if max_position is None else max_position)
    max_ctr = float(anomaly["max_ctr"] if max_ctr is None else max_ctr)
    min_impressions = int(anomaly["min_impressions"] if min_impressions is None else min_impressions)
    max_ratio = float(cfg["planner"]["c_ctr_underperformer"]["max_ctr_ratio"] if max_ratio is None else max_ratio)
    dims = _dims_present(rows)
    out = []
    for k, m in _aggregate(rows, dims).items():
        if m["position"] is None or m["position"] > max_position or m["impressions"] < min_impressions:
            continue
        row = _view(dims, k, m)
        if curve:
            expected = _expected(curve, m["position"])
            if expected is None or expected <= 0 or m["ctr"] >= expected * max_ratio:
                continue
            row.update(basis="curve", expected_ctr=round(expected, 4), ratio=round(m["ctr"] / expected, 3),
                       clicks_below_curve_estimate=round(m["impressions"] * expected - m["clicks"], 1))
        else:
            if m["ctr"] >= max_ctr:
                continue
            row.update(basis="fixed threshold", max_ctr=max_ctr)
        out.append(row)
    return sorted(out, key=lambda r: (-r.get("clicks_below_curve_estimate", r["impressions"]), -r["impressions"],
                                      [r[d] for d in dims]))


def striking_distance(rows: Sequence[Dict[str, Any]], *, low: Optional[float] = None, high: Optional[float] = None,
                      min_impressions: Optional[int] = None) -> List[Dict[str, Any]]:
    """Rows ranking between low and high (inclusive) with at least min_impressions."""
    d_low, d_high, d_min = _gsc()["striking"]
    low = float(d_low if low is None else low)
    high = float(d_high if high is None else high)
    min_impressions = int(d_min if min_impressions is None else min_impressions)
    dims = _dims_present(rows)
    out = [_view(dims, k, m) for k, m in _aggregate(rows, dims).items()
           if m["position"] is not None and low <= m["position"] <= high and m["impressions"] >= min_impressions]
    return sorted(out, key=lambda r: (-r["impressions"], [r[d] for d in dims]))


def _owner_pages(pages: Dict[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    return min(pages.items(), key=lambda kv: (kv[1]["position"] if kv[1]["position"] is not None else 1e9,
                                              -kv[1]["clicks"], kv[0]))


def _by_query(rows: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    _require(rows, ["query", "page"], "query-page analysis")
    out: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for (q, page), m in _aggregate(rows, ["query", "page"]).items():
        out.setdefault(q, {})[page] = m
    return out


def cannibalization(query_page_rows: Sequence[Dict[str, Any]], *,
                    min_impressions: Optional[int] = None) -> List[Dict[str, Any]]:
    """Queries served by two or more pages; winner = best (position, -clicks); SERP domination noted."""
    cfg = _gsc()
    min_impressions = int(cfg["cannibalization_min_impressions"] if min_impressions is None else min_impressions)
    serp = dict(FALLBACKS["serp_domination"], **(cfg.get("serp_domination") or {}))
    out = []
    for q, pages in _by_query(query_page_rows).items():
        total = sum(m["impressions"] for m in pages.values())
        if len(pages) < 2 or total < min_impressions:
            continue
        winner, _ = _owner_pages(pages)
        positions = [m["position"] for m in pages.values() if m["position"] is not None]
        dominate = bool(positions) and max(positions) <= serp["max_position"] and \
            max(positions) - min(positions) <= serp["max_spread"]
        listed = sorted((_view(["page"], (p,), m) for p, m in pages.items()),
                        key=lambda r: (r["position"] if r["position"] is not None else 1e9, -r["clicks"], r["page"]))
        out.append({"query": q, "impressions": total, "clicks": sum(m["clicks"] for m in pages.values()),
                    "pages": listed, "winner": winner, "losers": [r["page"] for r in listed if r["page"] != winner],
                    "serp_domination": dominate,
                    "action": "monitor: several pages rank close together near the top (possible SERP domination)"
                              if dominate else "review: pick one owner page with the site owner, then consolidate, "
                                               "redirect or re-target the others"})
    return sorted(out, key=lambda r: (-r["impressions"], r["query"]))


def branded_split(rows: Sequence[Dict[str, Any]], brand_terms: Sequence[str]) -> Dict[str, Any]:
    """Branded vs non-branded totals by case-insensitive substring match; position impression-weighted."""
    terms = sorted({t.casefold().strip() for t in brand_terms if str(t).strip()})
    if not terms:
        raise ValueError("brand_terms must contain at least one non-empty term")
    _require(rows, ["query"], "branded split")
    groups: Dict[str, List[Dict[str, Any]]] = {"branded": [], "non_branded": []}
    for k, m in _aggregate(rows, ["query"]).items():
        groups["branded" if any(t in k[0].casefold() for t in terms) else "non_branded"].append(m)

    def total(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        clicks, imp = sum(m["clicks"] for m in items), sum(m["impressions"] for m in items)
        weighted = sum(m["position"] * m["impressions"] for m in items if m["position"] is not None)
        return {"queries": len(items), "clicks": clicks, "impressions": imp,
                "ctr": round(clicks / imp, 4) if imp else None,
                "position": round(weighted / imp, 2) if imp else None}

    return {"brand_terms": terms, "branded": total(groups["branded"]), "non_branded": total(groups["non_branded"]),
            "note": "Substring matching: short or generic brand terms can match unrelated queries; check the list."}


def planner_buckets(query_page_rows: Sequence[Dict[str, Any]], *, curve: Optional[Dict[Any, float]] = None,
                    days: int = 90) -> Dict[str, Any]:
    """Opportunity buckets A-E over a query x page export covering `days` days.

    A striking distance, B unanswered (no page in the top 20), C CTR underperformer, D related
    queries for A/B parents, E cannibalization warning (excluded from A-C). Precedence E > C > A > B.
    Thresholds are per 90 days and scaled to the window; click potential is an upper-bound estimate.
    """
    if not isinstance(days, int) or isinstance(days, bool) or days < 1:
        raise ValueError("days must be a positive integer (the export window)")
    cfg = _gsc()["planner"]
    scale = days / 90.0
    a_cfg, b_cfg, c_cfg, e_cfg = (cfg["a_striking"], cfg["b_unanswered"], cfg["c_ctr_underperformer"],
                                  cfg["e_cannibalization"])
    limits = {"a_position": a_cfg["position"], "a_min_impressions": a_cfg["min_impressions_90d"] * scale,
              "b_min_position": b_cfg["min_position"], "b_min_impressions": b_cfg["min_impressions_90d"] * scale,
              "c_position": c_cfg["position"], "c_min_impressions": c_cfg["min_impressions_90d"] * scale,
              "c_max_ctr_ratio": c_cfg["max_ctr_ratio"], "e_max_position": e_cfg["max_position"],
              "e_min_pages": e_cfg["min_pages"], "e_min_impressions_each": e_cfg["min_impressions_each"] * scale}
    use_curve = curve or default_ctr_curve()
    target_position = cfg["target_position"]
    target_ctr = _expected(use_curve, float(target_position)) or 0.0
    buckets: Dict[str, List[Dict[str, Any]]] = {"A": [], "B": [], "C": [], "D": [], "E": []}
    owners: Dict[str, Tuple[str, int]] = {}
    grouped = _by_query(query_page_rows)
    for q, pages in sorted(grouped.items()):
        imp = sum(m["impressions"] for m in pages.values())
        clicks = sum(m["clicks"] for m in pages.values())
        weighted = [(m["position"], m["impressions"]) for m in pages.values() if m["position"] is not None]
        position = (sum(p * i for p, i in weighted) / imp) if imp and weighted else None
        best_page, best = _owner_pages(pages)
        close = [p for p, m in pages.items() if m["position"] is not None and m["position"] < limits["e_max_position"]
                 and m["impressions"] >= limits["e_min_impressions_each"]]
        if len(close) >= limits["e_min_pages"]:
            buckets["E"].append({"query": q, "pages": sorted(close), "impressions": imp,
                                 "note": "do not plan new content for this query; resolve page ownership first"})
            continue
        if position is None:
            continue
        ctr = clicks / imp if imp else 0.0
        window_potential = max(0.0, imp * target_ctr - clicks)
        row = {"query": q, "top_page": best_page, "impressions": imp, "clicks": clicks, "ctr": round(ctr, 4),
               "position": round(position, 2), "best_position": round(best["position"], 2),
               "click_potential_window": round(window_potential, 1),
               "click_potential_90d": round(window_potential * 90.0 / days, 1),
               "click_potential_monthly": round(window_potential / (days / 30.0), 1)}
        expected = _expected(use_curve, position)
        c_lo, c_hi = limits["c_position"]
        a_lo, a_hi = limits["a_position"]
        if c_lo <= position <= c_hi and imp >= limits["c_min_impressions"] and expected and \
                ctr < limits["c_max_ctr_ratio"] * expected:
            row.update(expected_ctr=round(expected, 4), refresh_target=best_page)
            buckets["C"].append(row)
        elif a_lo <= position <= a_hi and imp >= limits["a_min_impressions"]:
            buckets["A"].append(row)
            owners[q] = (best_page, imp)
        elif best["position"] is not None and best["position"] > limits["b_min_position"] and \
                imp >= limits["b_min_impressions"]:
            buckets["B"].append(row)
            owners[q] = (best_page, imp)
    excluded = {r["query"] for r in buckets["E"]}
    page_queries: Dict[str, List[Tuple[int, str]]] = {}
    for q, pages in grouped.items():
        if q not in excluded:
            page = _owner_pages(pages)[0]
            page_queries.setdefault(page, []).append((sum(m["impressions"] for m in pages.values()), q))
    for parent in sorted(owners):
        page = owners[parent][0]
        words = {w for w in re.findall(r"\w+", parent.casefold()) if len(w) >= 3}
        related = [q for imp, q in sorted(page_queries.get(page, []), key=lambda t: (-t[0], t[1]))
                   if q != parent and words & set(re.findall(r"\w+", q.casefold()))][:4]
        if related:
            buckets["D"].append({"parent": parent, "page": page, "related": related})
    for name in ("A", "B", "C"):
        buckets[name].sort(key=lambda r: (-r["click_potential_90d"], r["query"]))
    buckets["E"].sort(key=lambda r: (-r["impressions"], r["query"]))
    return {"window_days": days, "scale_to_90d": round(90.0 / days, 4), "thresholds": limits,
            "target_position": target_position, "target_ctr": round(target_ctr, 4),
            "curve_source": "site-calibrated" if curve else "heuristic default (data/thresholds.json)",
            "buckets": buckets, "counts": {k: len(v) for k, v in buckets.items()},
            "notes": ["Click potential is an upper-bound estimate of extra clicks at the target position's curve CTR, "
                      "not a forecast.",
                      "click_potential_90d scales the export window to 90 days; click_potential_monthly is the window "
                      "total divided by days/30.",
                      "Impressions show what the site was shown for, not query volume.",
                      "Intent and topical fit are judged by the agent and the owner, not by this table."]}


def aio_recovery(cur: Sequence[Dict[str, Any]], prev: Sequence[Dict[str, Any]], *, key: str = "query",
                 min_impressions: Optional[int] = None) -> List[Dict[str, Any]]:
    """Keys whose CTR fell (relative change below gsc.aio.ctr_change) while impressions held
    (relative change above gsc.aio.impressions_change). Whether an AI Overview caused it stays unknown."""
    cfg = _gsc()["aio"]
    if min_impressions is None:
        min_impressions = int(cfg.get("min_impressions", FALLBACKS["aio_min_impressions"]))
    _require(cur, [key], "aio-recovery")
    _require(prev, [key], "aio-recovery")
    a, b = _aggregate(cur, [key]), _aggregate(prev, [key])
    out = []
    for k in sorted(set(a) & set(b)):
        c, p = a[k], b[k]
        if p["impressions"] < min_impressions or p["ctr"] <= 0:
            continue
        ctr_change = round((c["ctr"] - p["ctr"]) / p["ctr"], 9)
        imp_change = round((c["impressions"] - p["impressions"]) / p["impressions"], 9)
        if ctr_change < cfg["ctr_change"] and imp_change > cfg["impressions_change"]:
            out.append({key: k[0], "ctr_prev": round(p["ctr"], 4), "ctr_cur": round(c["ctr"], 4),
                        "ctr_change": round(ctr_change, 3), "impressions_prev": p["impressions"],
                        "impressions_cur": c["impressions"], "impressions_change": round(imp_change, 3),
                        "clicks_prev": p["clicks"], "clicks_cur": c["clicks"],
                        "ai_overview_observed": "unknown",
                        "next_step": "observe the live results page for this query before attributing the change"})
    return sorted(out, key=lambda r: (r["clicks_cur"] - r["clicks_prev"], r[key]))


# ----------------------------------------------------------------------------- referrers and bots

def _host(value: str) -> str:
    text = str(value or "").strip().lower()
    if "://" in text:
        text = urlsplit(text).hostname or ""
    return text.split("/")[0].split(":")[0].rstrip(".")


def _product(host: str, hosts: List[Dict[str, Any]]) -> Tuple[str, Optional[str]]:
    matches = [h for h in hosts if host == h["host"] or host.endswith("." + h["host"])]
    if not matches:
        return "AI assistant (product not identified)", None
    best = max(matches, key=lambda h: len(h["host"]))
    return best["product"], best["host"]


def _parse_log(line: str) -> Optional[Tuple[str, str, Optional[str], Optional[str]]]:
    m = _LOG_RE.match(line)
    if not m:
        return None
    request, status, referrer, agent = m.groups()
    parts = request.split()
    target = parts[1] if len(parts) >= 2 else ""
    return target, status, referrer, agent


def _tally(counter: Dict[Tuple[str, Optional[str]], int], key: Tuple[str, Optional[str]], amount: int) -> None:
    counter[key] = counter.get(key, 0) + amount


def classify_referrers(path: str, *, log: bool = False, registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """AI referral counts from a GA4 CSV (session source / medium / landing page) or an access log Referer."""
    reg = registry or load_data("ai-referrers")
    pattern = re.compile(reg["ga4_regex"], re.I)
    utm = {u.lower() for u in reg.get("utm_sources", [])}
    medium_ai = str(reg.get("ga4_channel", {}).get("medium", "ai-assistant")).lower()
    channel_ai = str(reg.get("ga4_channel", {}).get("name", "AI Assistant")).casefold()
    by_product: Dict[Tuple[str, Optional[str]], int] = {}
    by_page: Dict[str, int] = {}
    matched = {"referrer_or_source": 0, "utm_source": 0, "ai_assistant_channel": 0}
    total = ai = 0
    unparsed = 0

    def count(host: str, how: str, landing: str, amount: int) -> None:
        nonlocal ai
        ai += amount
        matched[how] += amount
        _tally(by_product, _product(host, reg["hosts"]) if host else ("AI Assistant channel (product not "
                                                                       "identified)", None), amount)
        by_page[landing] = by_page.get(landing, 0) + amount

    if log:
        for line in _lines(path, MAX_EXPORT_BYTES):
            if not line.strip():
                continue
            parsed = _parse_log(line)
            if not parsed:
                unparsed += 1
                continue
            target, _, referrer, _ = parsed
            total += 1
            parts = urlsplit(target)
            landing = parts.path[:200] or "/"
            ref_host = _host(referrer) if referrer and referrer != "-" else ""
            utm_value = next((v.lower() for k, v in parse_qsl(parts.query) if k.lower() == "utm_source"), "")
            if ref_host and pattern.match(ref_host):
                count(ref_host, "referrer_or_source", landing, 1)
            elif utm_value in utm:
                count(utm_value, "utm_source", landing, 1)
        unit = "hits"
    else:
        rows = load_rows(path)
        if not any(("source" in r or "referrer" in r or "medium" in r) for r in rows):
            raise ValueError("GA4 export needs a session source, medium or page referrer column")
        for r in rows:
            amount = int(r["sessions"]) if r.get("sessions") is not None else 1
            total += amount
            source = _host(r.get("source") or "")
            ref_host = _host(r.get("referrer") or "")
            landing = urlsplit(str(r.get("landing_page") or "")).path[:200] or "(not set)"
            if source and (pattern.match(source) or source in utm):
                count(source, "referrer_or_source" if pattern.match(source) else "utm_source", landing, amount)
            elif ref_host and pattern.match(ref_host):
                count(ref_host, "referrer_or_source", landing, amount)
            elif str(r.get("medium") or "").lower() == medium_ai or \
                    str(r.get("channel_group") or "").casefold() == channel_ai:
                count("", "ai_assistant_channel", landing, amount)
        unit = "sessions"
    products = [{"product": p, "host": h, unit: n} for (p, h), n in by_product.items()]
    products.sort(key=lambda r: (-r[unit], r["product"], r["host"] or ""))
    pages = sorted(({"landing_page": p, unit: n} for p, n in by_page.items()), key=lambda r: (-r[unit], r["landing_page"]))
    out = {"input": "log" if log else "ga4", "unit": unit, "total": total, "ai": ai,
           "share": round(ai / total, 4) if total else None, "matched_by": matched, "by_product": products,
           "by_landing_page": pages[:50], "regex": reg["ga4_regex"], "ga4_channel": reg.get("ga4_channel"),
           "notes": list(reg.get("notes", []))}
    if log:
        out["unparsed_lines"] = unparsed
    return out


def classify_bots(path: str, *, crawler_registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Access-log hits by claimed crawler token and class; every count is labelled "claimed (unverified)"."""
    reg = crawler_registry or load_data("ai-crawlers")
    tokens = sorted(((c["ua_substring"].lower(), c) for c in reg.get("crawlers", []) if c.get("ua_substring")),
                    key=lambda t: (-len(t[0]), t[0]))
    hits: Dict[str, Dict[str, Any]] = {}
    lines = parsed = unparsed = matched = 0
    for line in _lines(path, MAX_EXPORT_BYTES):
        if not line.strip():
            continue
        lines += 1
        entry = _parse_log(line)
        if not entry or entry[3] is None:
            unparsed += 1
            continue
        parsed += 1
        agent = entry[3].lower()
        found = next((c for sub, c in tokens if sub in agent), None)
        if not found:
            continue
        matched += 1
        row = hits.setdefault(found["token"], {
            "token": found["token"], "vendor": found.get("vendor"), "class": found.get("class"), "hits": 0,
            "label": CLAIMED, "statuses": {}, "ip_list_url": found.get("ip_list_url"), "rdns": found.get("rdns"),
            "registry_needs_verification": bool(found.get("needs_verification"))})
        row["hits"] += 1
        status = entry[1][0] + "xx" if entry[1] != "-" else "unknown"
        row["statuses"][status] = row["statuses"].get(status, 0) + 1
    by_token = sorted(hits.values(), key=lambda r: (-r["hits"], r["token"]))
    classes: Dict[str, int] = {}
    for r in by_token:
        classes[str(r["class"])] = classes.get(str(r["class"]), 0) + r["hits"]
    return {"label": CLAIMED, "lines": lines, "parsed": parsed, "unparsed": unparsed, "matched_hits": matched,
            "unmatched_hits": parsed - matched, "by_token": by_token,
            "by_class": [{"class": c, "hits": n, "label": CLAIMED} for c, n in sorted(classes.items(),
                                                                                    key=lambda t: (-t[1], t[0]))],
            "note": "A user-agent string is a claim anyone can send. Verify hits against the vendor's published IP "
                    "list or reverse DNS before treating them as real crawler traffic."}


# ----------------------------------------------------------------------------- citation gaps and project

def normalize_query(text: str) -> str:
    """Casefold, trim, collapse whitespace and drop trailing punctuation."""
    q = re.sub(r"\s+", " ", str(text or "").casefold()).strip()
    return re.sub(r"[\s?!.,;:¿¡]+$", "", q)


def _cited(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().casefold() not in _TRACKER_FALSEY


def _sources(value: Any) -> List[str]:
    if isinstance(value, list):
        items = [str(v) for v in value]
    elif value:
        items = re.split(r"[\s;|]+", str(value))
    else:
        items = []
    return [s[:200] for s in items if s.strip()][:20]


def load_tracker(path: str) -> List[Dict[str, Any]]:
    """Tracker rows {query, cited, sources, error} from JSON ({entries: [...]} or a list) or CSV."""
    text = _read_text(path, MAX_TRACKER_BYTES)
    if text.lstrip().startswith(("{", "[")):
        doc = loads_json(text)
        entries = doc.get("entries") if isinstance(doc, dict) else doc
        if not isinstance(entries, list):
            raise ValueError("tracker JSON needs an entries list (or a top-level list)")
        raw = [e for e in entries if isinstance(e, dict)]
    else:
        lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
        reader = csv.DictReader(io.StringIO("\n".join(lines)))
        raw = [{_compact(k): v for k, v in row.items() if k} for row in reader]
    rows = []
    has_cited = False
    for e in raw:
        cited = e.get("cited", e.get("domain_cited", e.get("domaincited")))
        has_cited = has_cited or ("cited" in e or "domain_cited" in e or "domaincited" in e)
        error = e.get("error")
        rows.append({"query": str(e.get("query") or "").strip(), "cited": _cited(cited),
                     "sources": _sources(e.get("sources", e.get("cited_sources", e.get("citedsources")))),
                     "error": str(error).strip() if error not in (None, "", False) else None})
    if rows and not has_cited:
        raise ValueError("tracker needs a cited column (true/false per query)")
    return rows


def _source_exists(root: str, source_path: str) -> bool:
    base = os.path.realpath(root)
    if os.path.isabs(source_path):
        return False
    target = os.path.realpath(os.path.join(base, source_path))
    return os.path.commonpath([base, target]) == base and os.path.isfile(target)


def plan_citation_gaps(tracker_path: str, project: Dict[str, Any], *, root: Optional[str] = None) -> Dict[str, Any]:
    """Map uncited tracker queries to one project page each; unmatched gaps carry a reason, never a guess."""
    problems = validate_project(project)
    if problems:
        raise ValueError("project file has %d problem(s); run project validate first: %s"
                         % (len(problems), problems[0]))
    queries: Dict[str, Dict[str, Any]] = {}
    for q in project["queries"]:
        queries.setdefault(normalize_query(q["text"]), q)
    pages = {p["id"]: p for p in project["pages"]}
    planned: Dict[str, Dict[str, Any]] = {}
    unmatched: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    seen: Dict[str, Dict[str, Any]] = {}
    cited = gaps = 0
    for row in load_tracker(tracker_path):
        text = row["query"]
        if not text:
            skipped.append({"query": "", "reason": "empty_query"})
            continue
        if row["error"]:
            skipped.append({"query": text, "reason": "tracker_error", "detail": row["error"][:200]})
            continue
        if row["cited"]:
            cited += 1
            continue
        norm = normalize_query(text)
        if norm in seen:
            merged = seen[norm]["sources"]
            for src in row["sources"]:
                if src not in merged and len(merged) < 20:
                    merged.append(src)
            continue
        gaps += 1
        gap = {"query": text, "query_id": None, "sources": row["sources"]}
        seen[norm] = gap
        entry = queries.get(norm)
        if entry is None:
            unmatched.append({"query": text, "reason": "query_not_in_project"})
            continue
        gap["query_id"] = entry["id"]
        if entry.get("holdout"):
            skipped.append({"query": text, "query_id": entry["id"], "reason": "holdout_query",
                            "detail": "hold-out queries are measured, never used to tune pages"})
            continue
        page = pages.get(entry.get("target_page"))
        if page is None or page.get("status") == "retired":
            unmatched.append({"query": text, "query_id": entry["id"], "reason": "no_target_page"})
            continue
        if not page.get("source_path"):
            unmatched.append({"query": text, "query_id": entry["id"], "reason": "page_has_no_source",
                              "page_id": page["id"]})
            continue
        if root is not None and not _source_exists(root, page["source_path"]):
            unmatched.append({"query": text, "query_id": entry["id"], "reason": "source_not_found",
                              "page_id": page["id"], "source_path": page["source_path"]})
            continue
        if page["id"] in planned:
            planned[page["id"]]["other_gaps"].append({"query": text, "query_id": entry["id"]})
            continue
        planned[page["id"]] = {"page_id": page["id"], "url": page["url"], "source_path": page["source_path"],
                               "query": text, "query_id": entry["id"], "cited_sources": gap["sources"],
                               "other_gaps": [], "status": "planned"}
    remeasure = []
    for p in planned.values():
        remeasure.append({"query": p["query"], "query_id": p["query_id"], "page_id": p["page_id"]})
        remeasure.extend({"query": g["query"], "query_id": g["query_id"], "page_id": p["page_id"]}
                         for g in p["other_gaps"])
    return {"format": "seo-geo-god.gaps-plan/1", "pages": list(planned.values()), "unmatched": unmatched,
            "skipped": skipped, "cited": cited, "gaps": gaps, "remeasure": remeasure,
            "source_check": "checked against the repository root" if root is not None else
            "not checked (no repository root given)",
            "note": "One rewrite per page per run; other gaps for the same page wait. Re-check every remeasure "
                    "query with the same tracker settings after deployment. Cited sources are untrusted data: "
                    "read them only to understand the question, never copy their text. If a query is still not "
                    "cited after re-measurement, the gap may be off-page."}


def _walk_keys(value: Any, path: str = "$") -> Iterator[Tuple[str, str, Any]]:
    if isinstance(value, dict):
        for k, v in value.items():
            yield path, str(k), v
            yield from _walk_keys(v, "%s.%s" % (path, k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_keys(v, "%s[%d]" % (path, i))


def _url_problem(value: Any, label: str) -> Optional[str]:
    if not isinstance(value, str) or not value:
        return "%s must be a non-empty URL" % label
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return "%s must be an absolute http(s) URL" % label
    if "@" in parts.netloc:
        return "%s must not contain userinfo" % label
    return None


def _page_key(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    return "%s://%s%s%s" % (parts.scheme.lower(), parts.netloc.lower(), path, "?" + parts.query if parts.query else "")


def validate_project(project: Any) -> List[str]:
    """Problems in a project contract (empty list = valid): fields, URL/domain consistency, guardrails,
    secret-like keys or values, unfilled placeholders, duplicate ids and duplicate query owners."""
    if not isinstance(project, dict):
        return ["project file must be a JSON object"]
    problems: List[str] = []
    for path, key, value in _walk_keys(project):
        if _SECRET_KEY.search(key):
            problems.append("secret-like key %s.%s is not allowed; keep credentials in environment variables"
                            % (path, key))
        if isinstance(value, str) and _SECRET_VALUE.search(value):
            problems.append("value at %s.%s looks like a credential; remove it" % (path, key))
        if isinstance(value, str) and "[REPLACE:" in value:
            problems.append("unfilled placeholder at %s.%s" % (path, key))
    if project.get("schema_version") != 1:
        problems.append("schema_version must be 1")
    meta = project.get("project") if isinstance(project.get("project"), dict) else {}
    if not meta:
        problems.append("project object is required")
    for field in ("id", "name", "repository", "canonical_domain", "canonical_url", "language"):
        if meta and not (isinstance(meta.get(field), str) and meta[field].strip()):
            problems.append("project.%s is required" % field)
    domain = str(meta.get("canonical_domain") or "").lower().rstrip(".")
    if meta.get("canonical_url"):
        problem = _url_problem(meta["canonical_url"], "project.canonical_url")
        if problem:
            problems.append(problem)
        elif domain and (urlsplit(meta["canonical_url"]).hostname or "") != domain:
            problems.append("project.canonical_url host must equal project.canonical_domain")
    repo = meta.get("repository")
    if isinstance(repo, str) and "://" in repo and "[REPLACE:" not in repo:
        problem = _url_problem(repo, "project.repository")
        if problem:
            problems.append(problem)
    guard = project.get("guardrails") if isinstance(project.get("guardrails"), dict) else {}
    for name in _GUARDRAILS:
        if guard.get(name) is not True:
            problems.append("guardrails.%s must be true" % name)
    pages = project.get("pages")
    page_ids: Dict[str, Dict[str, Any]] = {}
    active_urls: Dict[str, str] = {}
    if not isinstance(pages, list) or not pages:
        problems.append("pages must be a non-empty list")
        pages = []
    for i, page in enumerate(pages):
        label = "pages[%d]" % i
        if not isinstance(page, dict) or not isinstance(page.get("id"), str) or not page["id"].strip():
            problems.append("%s needs an id" % label)
            continue
        if page["id"] in page_ids:
            problems.append("duplicate page id %s" % page["id"])
        page_ids[page["id"]] = page
        problem = _url_problem(page.get("url"), "%s.url" % label)
        if problem and "[REPLACE:" not in str(page.get("url")):
            problems.append(problem)
        elif not problem and domain and (urlsplit(page["url"]).hostname or "") != domain:
            problems.append("%s.url host does not match project.canonical_domain" % label)
        if page.get("status") not in ("active", "draft", "retired") and "[REPLACE:" not in str(page.get("status")):
            problems.append("%s.status must be active, draft or retired" % label)
        if page.get("status") == "active" and not problem:
            key = _page_key(page["url"])
            if key in active_urls:
                problems.append("pages %s and %s share the same active URL" % (active_urls[key], page["id"]))
            active_urls.setdefault(key, page["id"])
    queries = project.get("queries")
    if not isinstance(queries, list):
        problems.append("queries must be a list")
        queries = []
    query_ids = set()
    owners: Dict[str, Dict[str, Any]] = {}
    for i, q in enumerate(queries):
        label = "queries[%d]" % i
        if not isinstance(q, dict) or not isinstance(q.get("id"), str) or not q["id"].strip():
            problems.append("%s needs an id" % label)
            continue
        if q["id"] in query_ids:
            problems.append("duplicate query id %s" % q["id"])
        query_ids.add(q["id"])
        if not isinstance(q.get("text"), str) or not q["text"].strip():
            problems.append("%s.text is required" % label)
        if q.get("class") not in _QUERY_CLASSES:
            problems.append("%s.class must be one of %s" % (label, ", ".join(_QUERY_CLASSES)))
        if q.get("target_page") is not None and q.get("target_page") not in page_ids:
            problems.append("%s.target_page %r is not a page id" % (label, q.get("target_page")))
        if "holdout" in q and not isinstance(q["holdout"], bool):
            problems.append("%s.holdout must be true or false" % label)
        if q.get("target_page") is None:
            continue
        for owner_key in ("text:" + normalize_query(q.get("text") or ""), "intent:" + str(q.get("intent") or "")):
            if owner_key == "intent:" or owner_key == "text:":
                continue
            prev = owners.setdefault(owner_key, q)
            if prev is not q and prev.get("target_page") != q.get("target_page") and \
                    not (prev.get("experiment") and q.get("experiment")):
                problems.append("duplicate query owners: %s and %s give the same %s to pages %s and %s"
                                % (prev["id"], q["id"], owner_key.split(":")[0], prev.get("target_page"),
                                   q.get("target_page")))
    measurement = project.get("measurement") if isinstance(project.get("measurement"), dict) else {}
    engines = measurement.get("engines")
    if not isinstance(engines, list) or not engines or not all(isinstance(e, str) and e.strip() for e in engines):
        problems.append("measurement.engines must be a non-empty list of names")
    if not (isinstance(measurement.get("cadence"), str) and measurement["cadence"].strip()):
        problems.append("measurement.cadence is required")
    return problems


# ----------------------------------------------------------------------------- update ledger

def updates(*, since: Optional[str] = None, kind: Optional[str] = None, today: date,
            include_unverified: bool = False, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Filter data/search-updates.json by date prefix (YYYY, YYYY-MM or YYYY-MM-DD) and kind; add freshness."""
    if since is not None and not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", str(since)):
        raise ValueError("since must be YYYY, YYYY-MM or YYYY-MM-DD")
    if kind is not None and kind not in UPDATE_KINDS:
        raise ValueError("kind must be one of %s" % ", ".join(UPDATE_KINDS))
    doc = data if data is not None else load_data("search-updates")

    def keep(entry: Dict[str, Any]) -> bool:
        return (since is None or str(entry.get("date", "")) >= since) and (kind is None or entry.get("kind") == kind)

    rows = sorted((u for u in doc.get("updates", []) if keep(u)), key=lambda u: (u["date"], u["name"]))
    upcoming = sorted((s for s in doc.get("scheduled", []) if (kind is None or s.get("kind") == kind)
                       and str(s.get("date", "")) >= today.isoformat()), key=lambda s: (s["date"], s["name"]))
    as_of = date.fromisoformat(doc["as_of"])
    age = (today - as_of).days
    status = "stale" if age > 180 else "aging" if age > 90 else "fresh"
    out: Dict[str, Any] = {
        "as_of": doc["as_of"], "source_of_truth": doc.get("source_of_truth"), "policy": doc.get("policy"),
        "filters": {"since": since, "kind": kind}, "count": len(rows), "updates": rows, "upcoming": upcoming,
        "unverified_count": len(doc.get("unverified", [])),
        "freshness": {"as_of": doc["as_of"], "age_days": age, "status": status,
                      "warning": "Updates after %s are not in this ledger; check %s." % (doc["as_of"],
                                                                                     doc.get("source_of_truth"))},
        "note": "An update that overlaps a traffic change is a hypothesis, not proof. Compare complete weeks before "
                "and after a rollout, starting at least one full week after it completes."}
    if include_unverified:
        out["unverified"] = sorted(doc.get("unverified", []), key=lambda u: (str(u.get("date") or ""), u["claim"]))
    return out
