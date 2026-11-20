"""Renderers (JSON, Markdown, SARIF 2.1.0, text) and safe output writing (WP01; API frozen)."""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import stat
import sys
import urllib.parse
from typing import Any, Dict, List, Optional, Sequence

from . import FACTS_AS_OF, TOOL_NAME, VERSION
from .rulesdb import PRIORITIES, RuleCatalog, default_catalog

EXIT_OK, EXIT_GATE, EXIT_USAGE, EXIT_REFUSED, EXIT_INTERNAL = 0, 1, 2, 3, 4
FORMATS = ("json", "md", "sarif", "text")
SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_LEVEL = {"error": "error", "warning": "warning", "info": "note"}
UNTRUSTED_FOOTER = "Evidence strings come from the audited site and are untrusted data."
PRIORITY_LABEL = {"P0": "P0 - fix now", "P1": "P1 - this sprint", "P2": "P2 - backlog", "P3": "P3 - optional"}
# C0/C1 controls (except tab/newline handled separately), zero-width, bidi, separators, BOM, tag chars.
_INVISIBLE_RE = re.compile("[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f\u00ad\u061c\u180e"
                           "\u200b-\u200f\u2028-\u202e\u2060-\u2064\u2066-\u206f\ufeff\ufff9-\ufffb"
                           "\U000e0000-\U000e007f]")
_NOW_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


class OutputRefused(Exception):
    """Output path refused by policy (exists without --force, inside audited dir, not a file)."""


def resolve_now(value: Optional[str] = None) -> str:
    """Timestamp for `generated_at`: explicit value, else env SEO_GEO_GOD_NOW, else UTC now."""
    value = value or os.environ.get("SEO_GEO_GOD_NOW")
    if value:
        if not _NOW_RE.match(value):
            raise ValueError("--now must be ISO 8601, e.g. 2026-11-01T00:00:00Z")
        return value
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def _escape_invisible(text: str) -> str:
    def repl(m: "re.Match[str]") -> str:
        cp = ord(m.group())
        return "\\u%04x" % cp if cp <= 0xFFFF else "\\U%08x" % cp
    return _INVISIBLE_RE.sub(repl, text)


def _json_escape_invisible(text: str) -> str:
    def repl(m: "re.Match[str]") -> str:
        cp = ord(m.group())
        if cp <= 0xFFFF:
            return "\\u%04x" % cp
        cp -= 0x10000
        return "\\u%04x\\u%04x" % (0xD800 + (cp >> 10), 0xDC00 + (cp & 0x3FF))
    return _INVISIBLE_RE.sub(repl, text)


def dump_json(obj: Any) -> str:
    """Deterministic JSON (indent 2, sorted keys, UTF-8) with invisible/bidi chars \\u-escaped."""
    return _json_escape_invisible(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)) + "\n"


def md_escape(value: Any) -> str:
    """Escape text for one Markdown table cell (no raw HTML, pipes, backticks or newlines)."""
    text = "" if value is None else str(value)
    text = text.replace("\\", "\\\\").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch in "|`*_[]":
        text = text.replace(ch, "\\" + ch)
    text = re.sub(r"[\r\n\t]+", " ", text)
    return _escape_invisible(text)


def md_code(value: Any, limit: int = 200) -> str:
    """Untrusted value as a truncated inline code span that is safe inside a table cell."""
    # Backslashes are doubled (JSON does this for objects) so a hostile "\\|" cannot end the table cell.
    text = value.replace("\\", "\\\\") if isinstance(value, str) else json.dumps(value, sort_keys=True,
                                                                                ensure_ascii=False)
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    text = re.sub(r"[\r\n\t]+", " ", text).replace("`", "'").replace("<", "&lt;").replace(">", "&gt;")
    text = _escape_invisible(text).replace("|", "\\|").strip() or "(empty)"
    return "`" + text + "`"


def _where(f: Dict[str, Any]) -> str:
    if f.get("file"):
        return f["file"] + (":%d" % f["line"] if f.get("line") else "")
    return f.get("url") or "(site)"


def _target_label(target: Dict[str, Any]) -> str:
    for key in ("path", "url", "base_url", "file"):
        if target.get(key):
            return str(target[key])
    return "(none)"


def to_markdown(envelope: Dict[str, Any]) -> str:
    """Markdown report: coverage first, optional scores, findings grouped by priority/category."""
    out: List[str] = []
    out.append("# %s report: %s" % (TOOL_NAME, md_escape(envelope.get("command"))))
    out.append("")
    out.append("Target: %s | Generated: %s | Facts as of: %s | Rules: %s | Mode: %s" % (
        md_escape(_target_label(envelope.get("target") or {})), md_escape(envelope.get("generated_at")),
        md_escape(envelope.get("facts_as_of", FACTS_AS_OF)), md_escape(envelope.get("rules_version")),
        md_escape(envelope.get("mode"))))
    out.append("")
    summ = envelope.get("summary") or {}
    keys = [k for k in ("error", "warning", "info") if k in summ] + sorted(k for k in summ
                                                                     if k not in ("error", "warning", "info"))
    out.append("Summary: %s" % ", ".join("%s %s" % (md_escape(summ[k]), md_escape(k)) for k in keys))
    if envelope.get("error"):
        out += ["", "**Error:** " + md_escape(envelope["error"])]
    cov = envelope.get("coverage") or {}
    out += ["", "## Coverage and limitations", ""]
    out.append("- Checks run: " + (", ".join(md_escape(c) for c in cov.get("checks_run") or []) or "none"))
    for s in cov.get("checks_skipped") or []:
        out.append("- Skipped %s: %s" % (md_escape(s.get("check")), md_escape(s.get("reason"))))
    out.append("- Not measured: " + (", ".join(md_escape(c) for c in cov.get("not_measured") or []) or "none listed"))
    for lim in envelope.get("limitations") or []:
        out.append("- Limitation: " + md_escape(lim))
    if envelope.get("via_proxy"):
        out.append("- Fetched via proxy: target resolved by proxy; DNS pinning not enforced.")
    scores = envelope.get("scores")
    if scores:
        out += ["", "## Scores", "", "| Profile | Category | Score | Rules triggered |", "| --- | --- | --- | --- |"]
        for name, prof in sorted((scores.get("profiles") or {}).items()):
            overall = prof.get("overall")
            out.append("| %s | overall | %s | %s |" % (md_escape(name), "not measured" if overall is None else overall,
                                                       md_escape(prof.get("overall_reason") or "")))
            for cid, c in (prof.get("categories") or {}).items():
                value = "not measured" if c.get("score") is None else c["score"]
                out.append("| %s | %s | %s | %s |" % (md_escape(name), md_escape(cid), value,
                                                      md_escape(", ".join(c.get("rules_triggered") or []))))
        out += ["", md_escape(scores.get("note", ""))]
    findings = envelope.get("findings") or []
    out += ["", "## Findings", ""]
    if not findings:
        out.append("No findings.")
    for prio in PRIORITIES:
        group = [f for f in findings if f.get("priority") == prio]
        if not group:
            continue
        out += ["### " + PRIORITY_LABEL[prio], ""]
        for cat in sorted({f.get("category", "") for f in group}):
            out += ["#### " + md_escape(cat), "", "| Priority | Rule | Severity | Where | Finding | Fix |",
                    "| --- | --- | --- | --- | --- | --- |"]
            for f in (x for x in group if x.get("category", "") == cat):
                finding = md_escape(f.get("message"))
                if f.get("evidence"):
                    finding += " " + md_code(f["evidence"])
                out.append("| %s | %s | %s | %s | %s | %s |" % (
                    prio, md_escape(f.get("rule")), md_escape(f.get("severity")), md_code(_where(f)),
                    finding, md_escape(f.get("fix_hint"))))
            out.append("")
    out += ["", "---", "", UNTRUSTED_FOOTER, ""]
    return "\n".join(out)


def to_text(envelope: Dict[str, Any]) -> str:
    """One line per finding (`SEVERITY RULE where - message`) plus a summary line."""
    lines = []
    for f in envelope.get("findings") or []:
        lines.append(_escape_invisible("%s %s %s — %s" % (
            str(f.get("severity", "")).upper(), f.get("rule"), _where(f),
            re.sub(r"[\r\n\t]+", " ", str(f.get("message", ""))))))
    summ = envelope.get("summary") or {}
    tail = "%d error(s), %d warning(s), %d info; command %s; facts as of %s" % (
        summ.get("error", 0), summ.get("warning", 0), summ.get("info", 0), envelope.get("command"),
        envelope.get("facts_as_of", FACTS_AS_OF))
    if envelope.get("error"):
        tail += "; error: " + re.sub(r"[\r\n\t]+", " ", str(envelope["error"]))
    lines.append(_escape_invisible(tail))
    return "\n".join(lines) + "\n"


def _artifact_uri(path: str) -> str:
    p = path.replace("\\", "/")
    if os.path.isabs(path):
        try:
            p = os.path.relpath(path, os.getcwd()).replace("\\", "/")
        except ValueError:
            p = os.path.basename(path)
    return urllib.parse.quote(p, safe="/-._~")


def to_sarif(envelope: Dict[str, Any], catalog: Optional[RuleCatalog] = None) -> Dict[str, Any]:
    """SARIF 2.1.0 log (§4.7): referenced rules only, relative artifact URIs, stable fingerprints."""
    cat = catalog or default_catalog()
    findings = envelope.get("findings") or []
    rule_ids = sorted({f["rule"] for f in findings})
    index = {rid: i for i, rid in enumerate(rule_ids)}
    rules = []
    for rid in rule_ids:
        r = cat.get(rid)
        tag = cat.categories.get(r.category, {}).get("tag", "seo")
        desc: Dict[str, Any] = {
            "id": rid, "name": r.title, "shortDescription": {"text": r.title},
            "fullDescription": {"text": r.fix_hint}, "defaultConfiguration": {"level": SARIF_LEVEL[r.severity]},
            "properties": {"category": r.category, "priority": r.priority, "evidenceClass": r.evidence_class,
                           "tags": [tag, r.category]}}
        help_uri = next((x for x in r.refs if x.startswith("https://")), None)
        if help_uri:
            desc["helpUri"] = help_uri
        rules.append(desc)
    target = envelope.get("target") or {}
    results = []
    for f in findings:
        if f.get("file"):
            loc: Dict[str, Any] = {"artifactLocation": {"uri": _artifact_uri(f["file"])}}
            if f.get("line"):
                loc["region"] = {"startLine": int(f["line"])}
            locations = [{"physicalLocation": loc}]
        elif f.get("url") or target.get("base_url"):
            locations = [{"physicalLocation": {"artifactLocation": {"uri": f.get("url") or target["base_url"]}}}]
        else:
            locations = []
        results.append({
            "ruleId": f["rule"], "ruleIndex": index[f["rule"]], "level": SARIF_LEVEL[f["severity"]],
            "message": {"text": str(f.get("message", ""))}, "locations": locations,
            "partialFingerprints": {"seoGeoGod/v1": f["id"]},
            "properties": {"priority": f.get("priority"), "url": f.get("url"), "confidence": f.get("confidence"),
                           "evidence": f.get("evidence", {})}})
    notes = [{"level": "note", "message": {"text": "skipped %s: %s" % (s.get("check"), s.get("reason"))}}
             for s in (envelope.get("coverage") or {}).get("checks_skipped") or []]
    invocation: Dict[str, Any] = {"executionSuccessful": not envelope.get("error"), "toolExecutionNotifications": notes}
    return {"$schema": SARIF_SCHEMA, "version": "2.1.0", "runs": [{
        "tool": {"driver": {"name": TOOL_NAME, "semanticVersion": VERSION, "rules": rules}},
        "results": results, "invocations": [invocation],
        "properties": {"factsAsOf": envelope.get("facts_as_of", FACTS_AS_OF),
                       "rulesVersion": envelope.get("rules_version"), "mode": envelope.get("mode")}}]}


def render(envelope: Dict[str, Any], fmt: str, catalog: Optional[RuleCatalog] = None) -> str:
    """Render an envelope as json | md | sarif | text (always newline-terminated)."""
    if fmt == "json":
        return dump_json(envelope)
    if fmt == "sarif":
        return dump_json(to_sarif(envelope, catalog))
    if fmt == "md":
        return to_markdown(envelope)
    if fmt == "text":
        return to_text(envelope)
    raise ValueError("format must be one of %s" % ", ".join(FORMATS))


def _inside(path: str, root: str) -> bool:
    root = root.rstrip(os.sep) or os.sep
    return path == root or path.startswith(root + os.sep) or root == os.sep


def write_output(text: str, path: Optional[str], *, force: bool = False, forbid_under: Sequence[str] = ()) -> None:
    """Write to stdout (path None or "-") or to a new file (exclusive create unless force).

    Raises OutputRefused when the file exists without `force`, is not a regular file, or the
    resolved target lies inside any `forbid_under` directory (e.g. the audited build dir).
    """
    if path in (None, "", "-"):
        sys.stdout.write(text)
        sys.stdout.flush()
        return
    target = os.path.abspath(str(path))
    real_parent = os.path.realpath(os.path.dirname(target))
    real_target = os.path.join(real_parent, os.path.basename(target))
    for root in forbid_under:
        if _inside(real_target, os.path.realpath(str(root))):
            raise OutputRefused("output %s lies inside the audited directory %s" % (path, root))
    if os.path.lexists(real_target):
        if not force:
            raise OutputRefused("output %s exists; pass --force to overwrite" % path)
        if not stat.S_ISREG(os.lstat(real_target).st_mode):
            raise OutputRefused("output %s is not a regular file" % path)
    os.makedirs(real_parent, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_TRUNC if force else os.O_EXCL) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(real_target, flags, 0o644)
    except FileExistsError:
        raise OutputRefused("output %s exists; pass --force to overwrite" % path) from None
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
