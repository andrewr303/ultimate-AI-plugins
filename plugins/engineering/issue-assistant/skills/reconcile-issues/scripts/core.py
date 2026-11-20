#!/usr/bin/env python3
"""Optional, offline planning helpers. No network calls or provider mutations.

These helpers validate structured assertions supplied by the coding agent. They
cannot establish that an assertion is true or replace semantic evidence review.
See README.md beside this module for contracts and JSON examples.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Any


PRIORITY_ORDER = {1: 0, 2: 1, 3: 2, 4: 3, 0: 4}
FINISHED_STATES = {"done", "completed", "closed", "canceled", "cancelled", "duplicate"}
SATISFIED_STATES = {"done", "completed", "closed"}
UNDELIVERED_REASONS = {"not_planned", "canceled", "cancelled", "duplicate"}
DEFERRED_STATES = {"deferred", "snoozed"}
PROOF_KINDS = {"code", "test", "docs", "deployment", "check", "acceptance"}
JOURNAL_STATES = {"planned", "applied", "verified", "uncertain"}
JOURNAL_TRANSITIONS = {
    None: {"planned"}, "planned": {"applied", "verified", "uncertain"},
    "applied": {"verified", "uncertain"}, "uncertain": {"verified"}, "verified": set(),
}


def _aware(value: str | datetime, label: str) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{label} must be an ISO 8601 datetime") from exc
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def scan_window(
    now: str | datetime,
    checkpoint: str | datetime | None = None,
    days: int = 28,
    overlap_hours: int = 48,
) -> dict[str, str]:
    """Return the rolling window, extended to recover any checkpoint gap."""
    if type(days) is not int or days <= 0:
        raise ValueError("days must be a positive integer")
    if type(overlap_hours) is not int or overlap_hours < 0:
        raise ValueError("overlap_hours must be a nonnegative integer")
    end = _aware(now, "now")
    start = end - timedelta(days=days)
    if checkpoint is not None:
        previous = _aware(checkpoint, "checkpoint")
        if previous > end:
            raise ValueError("checkpoint must not be later than now")
        start = min(start, previous - timedelta(hours=overlap_hours))
    return {"start": _iso(start), "end": _iso(end)}


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("JSON object keys must be strings")
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            key = unicodedata.normalize("NFC", key)
            if key in normalized:
                raise ValueError("object keys collide after normalization")
            normalized[key] = _normalize(item)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if value is None or type(value) in (bool, int, float):
        return value
    raise ValueError("identity and desired values must be JSON compatible")


def _canonical(value: Any) -> str:
    return json.dumps(_normalize(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _identity(scope: Any, concern_key: str) -> tuple[Any, str]:
    normalized_scope = _normalize(scope)
    if isinstance(normalized_scope, str):
        normalized_scope = normalized_scope.strip()
    if not isinstance(normalized_scope, (dict, str)) or not normalized_scope:
        raise ValueError("scope must be a nonempty provider namespace string or object")
    if not isinstance(concern_key, str) or not concern_key.strip():
        raise ValueError("concern_key must be a nonempty stable semantic key")
    return normalized_scope, " ".join(unicodedata.normalize("NFC", concern_key).split())


def fingerprint(scope: Any, concern_key: str) -> str:
    """Identify a concern, independently of runs, observations, or evidence order."""
    namespace, concern = _identity(scope, concern_key)
    return "ia1:" + hashlib.sha256(_canonical([namespace, concern]).encode()).hexdigest()


def operation_key(scope: Any, concern_key: str, kind: str, desired: Any) -> str:
    """Identify one desired change; desired contains changed fields only."""
    namespace, concern = _identity(scope, concern_key)
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("kind must be a nonempty operation name")
    payload = [namespace, concern, kind.strip().lower(), desired]
    return "iao1:" + hashlib.sha256(_canonical(payload).encode()).hexdigest()


def _strings(value: Any, *, nonempty: bool = False) -> bool:
    return (isinstance(value, list) and (bool(value) or not nonempty)
            and all(isinstance(item, str) and bool(item.strip()) for item in value)
            and len(value) == len(set(value)))


def coverage_gate(record: Any) -> dict[str, Any]:
    """Evaluate supplied collection coverage, without fetching or verifying it."""
    reasons: list[str] = []

    def result() -> dict[str, Any]:
        return {"complete": not reasons, "reasons": list(dict.fromkeys(reasons))}

    if not isinstance(record, dict):
        reasons.append("coverage record must be an object")
        return result()
    window = record.get("window")
    try:
        if not isinstance(window, dict):
            raise ValueError("window must be an object")
        start, end = _aware(window.get("start"), "window start"), _aware(window.get("end"), "window end")
        if start >= end:
            raise ValueError("window start must be earlier than end")
    except (ValueError, TypeError, OverflowError) as exc:
        reasons.append(f"invalid fixed window: {exc}")
        return result()

    required = record.get("required_sources")
    if not _strings(required, nonempty=True):
        reasons.append("required_sources must contain distinct nonempty source IDs")
        required = []
    sources = record.get("sources")
    if not isinstance(sources, list):
        reasons.append("sources must be a list")
        sources = []
    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source["id"].strip():
            reasons.append("source IDs must be nonempty strings")
            continue
        identifier = source["id"]
        if identifier in seen:
            reasons.append(f"source {identifier} is duplicated")
            continue
        seen.add(identifier)
        if source.get("accessible") is not True:
            reasons.append(f"source {identifier} is inaccessible or access was not checked")
        partitions = source.get("partitions")
        if not isinstance(partitions, list) or not partitions:
            reasons.append(f"source {identifier} has no covered partitions")
            continue
        intervals: list[tuple[datetime, datetime]] = []
        for index, partition in enumerate(partitions, 1):
            label = f"source {identifier} partition {index}"
            if not isinstance(partition, dict):
                reasons.append(f"{label} must be an object")
                continue
            if partition.get("accessible") is not True:
                reasons.append(f"{label} is inaccessible or access was not checked")
            for flag in ("capped", "truncated"):
                if partition.get(flag) is not False:
                    reasons.append(f"{label} is {flag} or {flag} status was not checked")
            try:
                left = _aware(partition.get("start"), f"{label} start")
                right = _aware(partition.get("end"), f"{label} end")
                if not start <= left < right <= end:
                    raise ValueError("partition must lie inside the fixed window with start before end")
                intervals.append((left, right))
            except (ValueError, TypeError, OverflowError) as exc:
                reasons.append(f"{label} has an invalid interval: {exc}")
            pages = partition.get("pages")
            if not isinstance(pages, list) or not pages:
                reasons.append(f"{label} has no page exhaustion evidence")
                continue
            for page_index, page in enumerate(pages):
                if (not isinstance(page, dict) or type(page.get("item_count")) is not int
                        or page["item_count"] < 0 or type(page.get("has_next_page")) is not bool):
                    reasons.append(f"{label} page {page_index + 1} is malformed")
                    continue
                # Empty pages may still carry a continuation. Only the final
                # page may explicitly end this partition's ordered collection.
                expected_next = page_index < len(pages) - 1
                if page["has_next_page"] is not expected_next:
                    reasons.append(f"{label} page chain is incomplete or continues after exhaustion")
        covered_through = start
        for left, right in sorted(intervals):
            if left > covered_through:
                reasons.append(f"source {identifier} has an interval gap")
            covered_through = max(covered_through, right)
        if covered_through < end:
            reasons.append(f"source {identifier} does not cover the window through its end")
    for identifier in required:
        if identifier not in seen:
            reasons.append(f"required source {identifier} is missing")
    return result()


def completion_gate(record: Any) -> dict[str, Any]:
    """Fail closed when structured completion evidence is absent or inconsistent."""
    if not isinstance(record, dict):
        return {"eligible": False, "reasons": ["completion record must be an object"]}
    reasons: list[str] = []
    for field, expected, reason in (
        ("explicit_link", True, "no explicit issue-to-PR link"),
        ("pr_merged", True, "PR is not verified merged"),
        ("current_head_verified", True, "current head has not been verified"),
        ("contradiction", False, "contradictions are present or not checked"),
        ("reverted", False, "revert status is present or not checked"),
    ):
        if record.get(field) is not expected:
            reasons.append(reason)

    coverage = record.get("coverage")
    if not isinstance(coverage, dict):
        reasons.append("relevant evidence coverage is missing")
    else:
        required, reviewed = coverage.get("required"), coverage.get("reviewed")
        if (coverage.get("complete") is not True
                or not _strings(required, nonempty=True)
                or not _strings(reviewed, nonempty=True)
                or not set(required).issubset(reviewed)):
            reasons.append("relevant evidence coverage is incomplete")
        if coverage.get("inaccessible") != []:
            reasons.append("relevant evidence is inaccessible or access was not checked")

    evidence = record.get("evidence")
    evidence_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(evidence, list) or not evidence:
        reasons.append("verified evidence is missing")
    else:
        for item in evidence:
            if (not isinstance(item, dict) or not isinstance(item.get("id"), str)
                    or not item["id"].strip() or item["id"] in evidence_by_id):
                reasons.append("evidence IDs must be nonempty and unique")
                continue
            evidence_by_id[item["id"]] = item
            if (item.get("accessible") is not True or item.get("verified") is not True
                    or not isinstance(item.get("ref"), str) or not item["ref"].strip()):
                reasons.append(f"evidence {item['id']} is inaccessible, unverified, or lacks a reference")

    def verified_kind(kinds: set[str]) -> bool:
        return any(isinstance(item.get("kind"), str) and item["kind"] in kinds
                   and item.get("accessible") is True and item.get("verified") is True
                   and isinstance(item.get("ref"), str) and bool(item["ref"].strip())
                   for item in evidence_by_id.values())

    if not verified_kind({"code"}):
        reasons.append("verified code evidence is missing")
    if not verified_kind({"test", "check"}):
        reasons.append("verified test or check evidence is missing")

    criteria = record.get("criteria")
    seen_criteria: set[str] = set()
    if not isinstance(criteria, list) or not criteria:
        reasons.append("acceptance criteria are missing")
    else:
        for index, criterion in enumerate(criteria):
            if not isinstance(criterion, dict):
                reasons.append(f"criterion {index + 1} is malformed")
                continue
            identifier = criterion.get("id")
            if not isinstance(identifier, str) or not identifier.strip() or identifier in seen_criteria:
                reasons.append("acceptance criterion IDs must be nonempty and unique")
            else:
                seen_criteria.add(identifier)
            label = identifier if isinstance(identifier, str) else str(index + 1)
            if criterion.get("met") is not True:
                reasons.append(f"criterion {label} is not met")
            refs = criterion.get("evidence_refs")
            if not _strings(refs, nonempty=True):
                reasons.append(f"criterion {label} lacks distinct evidence references")
                continue
            linked = [evidence_by_id.get(ref) for ref in refs]
            if any(item is None for item in linked):
                reasons.append(f"criterion {label} references unknown evidence")
            if not any(item is not None and isinstance(item.get("kind"), str)
                       and item["kind"] in PROOF_KINDS
                       and item.get("accessible") is True and item.get("verified") is True
                       and bool(item.get("ref")) for item in linked):
                reasons.append(f"criterion {label} lacks direct proof; sessions or PR prose alone are insufficient")

    if type(record.get("deploy_required")) is not bool:
        reasons.append("deployment requirement was not assessed")
    elif record["deploy_required"]:
        if record.get("deployment_verified") is not True:
            reasons.append("required deployment has not been verified")
        if not verified_kind({"deployment"}):
            reasons.append("required deployment lacks verified deployment evidence")
    if type(record.get("manual_acceptance_required")) is not bool:
        reasons.append("manual acceptance requirement was not assessed")
    elif record["manual_acceptance_required"]:
        if record.get("manual_acceptance_verified") is not True:
            reasons.append("required manual acceptance has not been verified")
        if not verified_kind({"acceptance"}):
            reasons.append("required manual acceptance lacks verified acceptance evidence")
    return {"eligible": not reasons, "reasons": list(dict.fromkeys(reasons))}


def _state(issue: dict[str, Any]) -> str:
    return str(issue.get("state", "open")).strip().lower()


def _satisfies_dependency(issue: dict[str, Any]) -> bool:
    reason = str(issue.get("state_reason", "")).strip().lower()
    return _state(issue) in SATISFIED_STATES and reason not in UNDELIVERED_REASONS


def rank_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by inherited explicit priority, readiness, blocker role, and ID."""
    if not isinstance(issues, list) or any(not isinstance(issue, dict) for issue in issues):
        raise ValueError("issues must be a list of objects")
    by_id: dict[str, dict[str, Any]] = {}
    for issue in issues:
        identifier = issue.get("id")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in by_id:
            raise ValueError("issue IDs must be nonempty, unique strings")
        priority = issue.get("priority", 0)
        if type(priority) is not int or priority not in PRIORITY_ORDER:
            raise ValueError(f"{identifier}: priority must be 0, 1, 2, 3, or 4")
        if not _strings(issue.get("blocked_by", [])):
            raise ValueError(f"{identifier}: blocked_by must contain distinct issue IDs")
        by_id[identifier] = issue
    active = {key: value for key, value in by_id.items()
              if _state(value) not in FINISHED_STATES | DEFERRED_STATES}
    blockers: dict[str, list[str]] = {}
    for identifier, issue in active.items():
        blockers[identifier] = sorted(
            key for key in issue.get("blocked_by", [])
            if key not in by_id or not _satisfies_dependency(by_id[key])
        )
    # Propagate only actual provider priority levels through prerequisites. This
    # finite fixed point terminates even for cycles, without invented scores.
    effective = {key: value.get("priority", 0) for key, value in active.items()}
    changed = True
    while changed:
        changed = False
        for dependent, prerequisites in blockers.items():
            for prerequisite in prerequisites:
                if prerequisite in effective and PRIORITY_ORDER[effective[dependent]] < PRIORITY_ORDER[effective[prerequisite]]:
                    effective[prerequisite] = effective[dependent]
                    changed = True
    result: list[dict[str, Any]] = []
    for identifier, issue in active.items():
        blocks_active = sorted(key for key, blocked in blockers.items() if identifier in blocked)
        unresolved = blockers[identifier]
        ready = not unresolved
        reason = ("blocked by " + ", ".join(unresolved) if unresolved else "ready")
        if blocks_active:
            reason += "; unblocks " + ", ".join(blocks_active)
        if effective[identifier] != issue.get("priority", 0):
            reason += f"; inherits priority {effective[identifier]} from blocked dependent work"
        result.append({**issue, "priority": issue.get("priority", 0), "ready": ready,
                       "effective_priority": effective[identifier],
                       "unresolved_blockers": unresolved, "blocks_active": blocks_active,
                       "rank_reason": reason})
    result.sort(key=lambda issue: (PRIORITY_ORDER[issue["effective_priority"]],
                                   not issue["ready"], not bool(issue["blocks_active"]),
                                   issue["id"]))
    return result


def plan_findings(scope: Any, findings: list[dict[str, Any]],
                  existing: dict[str, Any]) -> list[dict[str, Any]]:
    """Return candidate operations or explicit nonwriting reviews, never write."""
    if not isinstance(findings, list) or not isinstance(existing, dict):
        raise ValueError("findings must be a list and existing must be an object")
    canonical: dict[str, str] = {}
    for concern, issue in existing.items():
        key = fingerprint(scope, concern)
        identifier = issue.get("id") if isinstance(issue, dict) else issue
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("canonical issue IDs must be nonempty strings")
        if key in canonical and canonical[key] != identifier:
            raise ValueError("normalized concern has conflicting canonical issue IDs")
        canonical[key] = identifier
    groups: dict[str, list[dict[str, Any]]] = {}
    for finding in findings:
        if not isinstance(finding, dict):
            raise ValueError("each finding must be an object")
        if "evidence_refs" in finding and not _strings(finding["evidence_refs"]):
            raise ValueError("finding evidence_refs must contain distinct nonempty strings")
        concern = finding.get("concern_key")
        identity = fingerprint(scope, concern)
        kind, desired = finding.get("kind"), finding.get("desired", {})
        if not isinstance(kind, str) or kind not in {"create", "update", "complete"} or not isinstance(desired, dict):
            raise ValueError("finding kind must be create/update/complete and desired must be an object")
        groups.setdefault(identity, []).append({**finding, "concern_key": _identity(scope, concern)[1],
                                               "operation_key": operation_key(scope, concern, kind, desired)})
    plans: list[dict[str, Any]] = []
    for identity, group in sorted(groups.items()):
        keys = sorted({item["operation_key"] for item in group})
        first = group[0]
        target = canonical.get(identity)
        plan: dict[str, Any] = {"fingerprint": identity, "concern_key": first["concern_key"],
                                "target_id": target, "write_candidate": False,
                                "evidence_refs": sorted({ref for item in group
                                                         for ref in item.get("evidence_refs", [])})}
        if len(keys) != 1:
            plan.update(kind="review_conflict", reasons=["findings propose conflicting changes"],
                        candidate_operation_keys=keys)
        else:
            kind = first["kind"]
            reasons: list[str] = []
            output_kind = kind
            if kind == "create" and target:
                output_kind, reasons = "review_existing", ["a canonical issue already represents this concern"]
            elif kind == "create" and not all(item.get("duplicate_search_complete") is True for item in group):
                output_kind, reasons = "review", ["duplicate search is incomplete or inaccessible"]
            elif kind in {"update", "complete"} and not target:
                output_kind, reasons = "review", ["canonical issue target is missing"]
            elif kind == "complete":
                for item in group:
                    gate = completion_gate(item.get("completion"))
                    reasons.extend(gate["reasons"])
                if reasons:
                    output_kind = "review"
            plan.update(kind=output_kind, operation_key=keys[0], desired=_normalize(first.get("desired", {})),
                        reasons=sorted(set(reasons)),
                        write_candidate=output_kind in {"create", "update", "complete"})
        plans.append(plan)
    return plans


class Journal:
    """Single-process local intent log; no provider CAS or exactly-once guarantee.

    A persisted planned/applied/uncertain operation must be recovered by remote
    lookup and verification before a new attempt. This class performs no lookup.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.entries: list[dict[str, Any]] = []
        if self.path.exists():
            content = self.path.read_text(encoding="utf-8")
            if content and not content.endswith("\n"):
                raise ValueError("unterminated journal line; recover manually before writing")
            for number, line in enumerate(content.splitlines(), 1):
                try:
                    entry = json.loads(line)
                    if (not isinstance(entry, dict) or not isinstance(entry.get("status"), str)
                            or entry["status"] not in JOURNAL_STATES
                            or not isinstance(entry.get("operation_key"), str)
                            or not entry["operation_key"].strip()
                            or not isinstance(entry.get("detail", {}), dict)):
                        raise ValueError("invalid journal entry")
                    previous = self.latest(entry["operation_key"])
                    before = previous["status"] if previous else None
                    if entry["status"] not in JOURNAL_TRANSITIONS[before]:
                        raise ValueError("unsafe journal transition")
                    entry = json.loads(_canonical(entry))
                except (ValueError, TypeError) as exc:
                    raise ValueError(f"invalid journal line {number}; recover manually before writing") from exc
                self.entries.append(entry)

    def latest(self, key: str) -> dict[str, Any] | None:
        return next((copy.deepcopy(entry) for entry in reversed(self.entries)
                     if entry["operation_key"] == key), None)

    def begin(self, key: str, detail: dict[str, Any] | None = None) -> bool:
        """Reserve a new local intent; false means recover/skip, never blindly retry."""
        if self.latest(key) is not None:
            return False
        self.record(key, "planned", detail)
        return True

    def record(self, key: str, status: str, detail: dict[str, Any] | None = None) -> None:
        if (not isinstance(key, str) or not key.strip() or not isinstance(status, str)
                or status not in JOURNAL_STATES):
            raise ValueError("nonempty operation_key and supported status are required")
        previous = self.latest(key)
        before = previous["status"] if previous else None
        if status not in JOURNAL_TRANSITIONS[before]:
            raise ValueError(f"unsafe journal transition {before!r} -> {status!r}")
        if detail is not None and not isinstance(detail, dict):
            raise ValueError("journal detail must be an object")
        serialized = _canonical({"operation_key": key, "status": status,
                                 "detail": detail if detail is not None else {}}) + "\n"
        entry = json.loads(serialized)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        self.entries.append(entry)


def _read_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    window = commands.add_parser("window", help="compute UTC rolling/catch-up window")
    window.add_argument("--now", required=True)
    window.add_argument("--checkpoint")
    window.add_argument("--days", type=int, default=28)
    window.add_argument("--overlap-hours", type=int, default=48)
    for name in ("gate", "coverage", "rank", "fingerprint", "plan"):
        command = commands.add_parser(name)
        command.add_argument("file", help="JSON file or - for stdin")
    args = parser.parse_args(argv)
    try:
        if args.command == "window":
            result = scan_window(args.now, args.checkpoint, args.days, args.overlap_hours)
        else:
            payload = _read_json(args.file)
            if args.command == "gate":
                result = completion_gate(payload)
            elif args.command == "coverage":
                result = coverage_gate(payload)
            elif args.command == "rank":
                result = rank_issues(payload)
            elif args.command == "fingerprint":
                result = {"fingerprint": fingerprint(payload["scope"], payload["concern_key"])}
                if "kind" in payload and "desired" in payload:
                    result["operation_key"] = operation_key(payload["scope"], payload["concern_key"],
                                                            payload["kind"], payload["desired"])
            else:
                result = plan_findings(payload["scope"], payload["findings"], payload.get("existing", {}))
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
