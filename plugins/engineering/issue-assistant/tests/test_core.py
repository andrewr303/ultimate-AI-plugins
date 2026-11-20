"""Behavioral boundary tests for the optional offline helpers (stdlib only)."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "reconcile-issues" / "scripts" / "core.py"
SPEC = importlib.util.spec_from_file_location("issue_assistant_core", SCRIPT)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)
SCOPE = {"provider": "linear", "workspace_id": "ws-1", "team_id": "team-1"}


def completed_record():
    return {
        "explicit_link": True,
        "pr_merged": True,
        "current_head_verified": True,
        "contradiction": False,
        "reverted": False,
        "coverage": {"complete": True, "required": ["code", "tests", "docs"],
                     "reviewed": ["code", "tests", "docs"], "inaccessible": []},
        "criteria": [{"id": "AC1", "met": True, "evidence_refs": ["code-1", "test-1"]}],
        "evidence": [
            {"id": "code-1", "kind": "code", "ref": "repo@abc:src/service.py#L20",
             "accessible": True, "verified": True},
            {"id": "test-1", "kind": "test", "ref": "check/123@abc",
             "accessible": True, "verified": True},
        ],
        "deploy_required": False,
        "manual_acceptance_required": False,
    }


def covered_record():
    return json.loads((Path(__file__).parent / "fixtures" / "coverage-complete.json").read_text())


class CoverageTests(unittest.TestCase):
    def test_complete_fixed_window_with_partitioned_sources(self):
        record = covered_record()
        original = copy.deepcopy(record)
        self.assertEqual(core.coverage_gate(record), {"complete": True, "reasons": []})
        self.assertEqual(record, original)
        record["sources"].reverse()
        record["sources"][1]["partitions"].reverse()
        self.assertEqual(core.coverage_gate(record), {"complete": True, "reasons": []})

    def test_empty_page_with_continuation_requires_another_page(self):
        record = covered_record()
        pages = record["sources"][0]["partitions"][0]["pages"]
        pages[:] = [{"item_count": 0, "has_next_page": True}]
        self.assertFalse(core.coverage_gate(record)["complete"])
        pages.append({"item_count": 0, "has_next_page": False})
        self.assertTrue(core.coverage_gate(record)["complete"])

    def test_pages_after_explicit_exhaustion_are_inconsistent(self):
        record = covered_record()
        record["sources"][0]["partitions"][0]["pages"] = [
            {"item_count": 4, "has_next_page": False},
            {"item_count": 0, "has_next_page": False},
        ]
        self.assertFalse(core.coverage_gate(record)["complete"])

    def test_missing_source_or_partition_and_middle_gap_block_coverage(self):
        for mutation in (
            lambda r: r["sources"].pop(),
            lambda r: r["sources"][0]["partitions"].pop(),
            lambda r: r["sources"][0]["partitions"][1].update(start="2026-10-16T00:00:01Z"),
        ):
            record = covered_record()
            mutation(record)
            self.assertFalse(core.coverage_gate(record)["complete"])

    def test_overlapping_partitions_cover_the_union(self):
        record = covered_record()
        record["sources"][0]["partitions"][1]["start"] = "2026-10-15T23:59:00Z"
        self.assertTrue(core.coverage_gate(record)["complete"])

    def test_capped_truncated_and_inaccessible_collections_are_incomplete(self):
        for field, value in (("capped", True), ("truncated", True), ("accessible", False)):
            record = covered_record()
            record["sources"][0]["partitions"][0][field] = value
            self.assertFalse(core.coverage_gate(record)["complete"])
        record = covered_record()
        record["sources"][0]["accessible"] = False
        self.assertFalse(core.coverage_gate(record)["complete"])

    def test_missing_or_truthy_flags_do_not_establish_coverage(self):
        for field, value in (("capped", 0), ("truncated", None), ("accessible", 1)):
            record = covered_record()
            record["sources"][0]["partitions"][0][field] = value
            self.assertFalse(core.coverage_gate(record)["complete"])
        record = covered_record()
        del record["sources"][0]["partitions"][0]["capped"]
        self.assertFalse(core.coverage_gate(record)["complete"])

    def test_fixed_window_and_partitions_require_aware_valid_timestamps(self):
        for value in ("2026-10-01T00:00:00", "not-a-date", None):
            record = covered_record()
            record["window"]["start"] = value
            self.assertFalse(core.coverage_gate(record)["complete"])
        for value in ("2026-09-01T00:00:00Z", "2026-10-17T00:00:00", None):
            record = covered_record()
            record["sources"][0]["partitions"][0]["start"] = value
            self.assertFalse(core.coverage_gate(record)["complete"])
        record = covered_record()
        record["window"]["start"] = record["window"]["end"]
        self.assertFalse(core.coverage_gate(record)["complete"])

    def test_equivalent_offsets_are_compared_as_utc(self):
        record = covered_record()
        record["sources"][0]["partitions"][1]["start"] = "2026-10-15T18:00:00-06:00"
        self.assertTrue(core.coverage_gate(record)["complete"])

    def test_duplicate_source_ids_cannot_hide_inaccessible_source(self):
        record = covered_record()
        record["sources"].append({**record["sources"][0], "accessible": False})
        self.assertFalse(core.coverage_gate(record)["complete"])

    def test_malformed_records_and_pages_fail_closed(self):
        for record in (None, [], {}, {"window": []}):
            self.assertFalse(core.coverage_gate(record)["complete"])
        for page in (None, {}, {"item_count": True, "has_next_page": False},
                     {"item_count": -1, "has_next_page": False},
                     {"item_count": 0, "has_next_page": 0}):
            record = covered_record()
            record["sources"][0]["partitions"][0]["pages"] = [page]
            self.assertFalse(core.coverage_gate(record)["complete"])


class WindowTests(unittest.TestCase):
    def test_default_rolls_28_days(self):
        self.assertEqual(core.scan_window("2026-10-19T12:00:00Z"), {
            "start": "2026-09-21T12:00:00Z", "end": "2026-10-19T12:00:00Z"})

    def test_converts_offsets_to_utc(self):
        self.assertEqual(core.scan_window("2026-10-19T06:00:00-06:00", days=14)["end"],
                         "2026-10-19T12:00:00Z")

    def test_naive_now_and_checkpoint_rejected(self):
        for kwargs in ({"now": "2026-10-19T12:00:00"},
                       {"now": "2026-10-19T12:00:00Z", "checkpoint": "2026-10-18T12:00:00"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                core.scan_window(**kwargs)

    def test_downtime_expands_window_without_a_gap(self):
        result = core.scan_window("2026-10-19T12:00:00Z", "2026-06-01T10:00:00Z")
        self.assertEqual(result["start"], "2026-05-30T10:00:00Z")

    def test_recent_checkpoint_keeps_deep_rolling_context(self):
        self.assertEqual(core.scan_window("2026-10-19T12:00:00Z", "2026-10-18T12:00:00Z")["start"],
                         "2026-09-21T12:00:00Z")

    def test_future_checkpoint_and_invalid_durations_rejected(self):
        with self.assertRaises(ValueError):
            core.scan_window("2026-10-19T12:00:00Z", "2026-10-19T12:00:01Z")
        for kwargs in ({"days": 0}, {"days": True}, {"overlap_hours": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                core.scan_window("2026-10-19T12:00:00Z", **kwargs)


class IdentityTests(unittest.TestCase):
    def test_scope_key_order_unicode_and_concern_spacing_are_stable(self):
        first = core.fingerprint({"a": "é", "b": 2}, "  fix   schema ")
        second = core.fingerprint({"b": 2, "a": "e\u0301"}, "fix schema")
        self.assertEqual(first, second)

    def test_provider_namespace_prevents_cross_tracker_collision(self):
        self.assertNotEqual(core.fingerprint(SCOPE, "fix schema"),
                            core.fingerprint({**SCOPE, "provider": "github"}, "fix schema"))

    def test_operation_uses_desired_content_not_mapping_order(self):
        self.assertEqual(core.operation_key(SCOPE, "a", "UPDATE", {"body": "abc", "title": "x"}),
                         core.operation_key(SCOPE, "a", "update", {"title": "x", "body": "abc"}))
        self.assertNotEqual(core.operation_key(SCOPE, "a", "update", {"body": " abc"}),
                            core.operation_key(SCOPE, "a", "update", {"body": "abc"}))

    def test_empty_identity_and_non_json_values_rejected(self):
        for scope, concern in (({}, "a"), (SCOPE, " ")):
            with self.subTest(scope=scope, concern=concern), self.assertRaises(ValueError):
                core.fingerprint(scope, concern)
        with self.assertRaises(ValueError):
            core.operation_key(SCOPE, "a", "update", {"confidence": float("nan")})


class CompletionTests(unittest.TestCase):
    def test_complete_record_passes(self):
        self.assertEqual(core.completion_gate(completed_record()), {"eligible": True, "reasons": []})

    def test_all_explicit_flags_are_required_without_truthy_coercion(self):
        for field in ("explicit_link", "pr_merged", "current_head_verified"):
            record = completed_record()
            record[field] = 1
            with self.subTest(field=field):
                self.assertFalse(core.completion_gate(record)["eligible"])

    def test_partial_scope_and_unreviewed_sources_block_closure(self):
        for mutation in (lambda c: c.update(complete=False),
                         lambda c: c.update(reviewed=["code", "tests"]),
                         lambda c: c.update(inaccessible=["docs/private"])):
            record = completed_record()
            mutation(record["coverage"])
            self.assertFalse(core.completion_gate(record)["eligible"])

    def test_absent_access_assessment_blocks_closure(self):
        record = completed_record()
        del record["coverage"]["inaccessible"]
        self.assertFalse(core.completion_gate(record)["eligible"])

    def test_unmet_or_empty_criteria_block_closure(self):
        record = completed_record()
        record["criteria"].append({"id": "AC2", "met": False, "evidence_refs": ["test-1"]})
        self.assertFalse(core.completion_gate(record)["eligible"])
        record["criteria"] = []
        self.assertFalse(core.completion_gate(record)["eligible"])

    def test_unknown_or_duplicate_evidence_references_block_closure(self):
        for refs in (["missing"], ["code-1", "code-1"]):
            record = completed_record()
            record["criteria"][0]["evidence_refs"] = refs
            self.assertFalse(core.completion_gate(record)["eligible"])

    def test_session_and_pr_prose_alone_cannot_complete_issue(self):
        for kind in ("session", "pr_prose"):
            record = completed_record()
            record["evidence"] = [{"id": "claim", "kind": kind, "ref": "session/123",
                                   "accessible": True, "verified": True}]
            record["criteria"][0]["evidence_refs"] = ["claim"]
            self.assertFalse(core.completion_gate(record)["eligible"])

    def test_session_may_corroborate_direct_proof(self):
        record = completed_record()
        record["evidence"].append({"id": "session", "kind": "session", "ref": "session/123",
                                   "accessible": True, "verified": True})
        record["criteria"][0]["evidence_refs"].append("session")
        self.assertTrue(core.completion_gate(record)["eligible"])

    def test_reverted_or_contradicted_work_stays_open(self):
        for field in ("reverted", "contradiction"):
            record = completed_record()
            record[field] = True
            self.assertFalse(core.completion_gate(record)["eligible"])

    def test_deployment_requires_actual_verified_evidence(self):
        record = completed_record()
        record.update(deploy_required=True, deployment_verified=True)
        self.assertFalse(core.completion_gate(record)["eligible"])
        record["evidence"].append({"id": "deploy", "kind": "deployment", "ref": "deployment/123@abc",
                                   "accessible": True, "verified": True})
        self.assertTrue(core.completion_gate(record)["eligible"])
        record["deployment_verified"] = False
        self.assertFalse(core.completion_gate(record)["eligible"])

    def test_code_and_tests_are_both_required_for_automatic_completion(self):
        for kind in ("code", "test"):
            record = completed_record()
            record["evidence"] = [item for item in record["evidence"] if item["kind"] == kind]
            record["criteria"][0]["evidence_refs"] = [record["evidence"][0]["id"]]
            self.assertFalse(core.completion_gate(record)["eligible"])

    def test_required_manual_acceptance_needs_verified_acceptance_proof(self):
        record = completed_record()
        record.update(manual_acceptance_required=True, manual_acceptance_verified=True)
        self.assertFalse(core.completion_gate(record)["eligible"])
        record["evidence"].append({"id": "acceptance", "kind": "acceptance", "ref": "issue/42#approval",
                                   "accessible": True, "verified": True})
        self.assertTrue(core.completion_gate(record)["eligible"])
        record["manual_acceptance_verified"] = False
        self.assertFalse(core.completion_gate(record)["eligible"])

    def test_manual_acceptance_requirement_must_be_explicitly_assessed(self):
        record = completed_record()
        del record["manual_acceptance_required"]
        self.assertFalse(core.completion_gate(record)["eligible"])

    def test_inaccessible_or_failed_verification_blocks_completion(self):
        for field in ("accessible", "verified"):
            record = completed_record()
            record["evidence"][0][field] = False
            self.assertFalse(core.completion_gate(record)["eligible"])

    def test_duplicate_proof_ids_cannot_smuggle_conflicting_proof(self):
        record = completed_record()
        record["evidence"].append({**record["evidence"][0], "verified": False})
        self.assertFalse(core.completion_gate(record)["eligible"])

    def test_malformed_evidence_kind_and_record_fail_closed(self):
        record = completed_record()
        record["criteria"][0]["evidence_refs"] = ["code-1"]
        record["evidence"][0]["kind"] = ["code"]
        self.assertFalse(core.completion_gate(record)["eligible"])
        self.assertFalse(core.completion_gate(None)["eligible"])


class RankingTests(unittest.TestCase):
    def test_priority_zero_is_unspecified_and_last(self):
        ranked = core.rank_issues([{"id": str(p), "priority": p} for p in (0, 4, 2, 1, 3)])
        self.assertEqual([issue["priority"] for issue in ranked], [1, 2, 3, 4, 0])

    def test_completed_and_deferred_skipped_but_deferred_dependency_unresolved(self):
        ranked = core.rank_issues([{"id": "done", "state": "completed"},
                                   {"id": "later", "state": "deferred"},
                                   {"id": "a", "blocked_by": ["done", "later", "unknown"]}])
        self.assertEqual(len(ranked), 1)
        self.assertFalse(ranked[0]["ready"])
        self.assertEqual(ranked[0]["unresolved_blockers"], ["later", "unknown"])

    def test_blocker_precedes_peer_at_same_priority_and_explains_dependency(self):
        issues = [{"id": "A", "priority": 2}, {"id": "Z", "priority": 2},
                  {"id": "B", "priority": 2, "blocked_by": ["Z"]}]
        result = core.rank_issues(issues)
        self.assertEqual([issue["id"] for issue in result], ["Z", "A", "B"])
        self.assertIn("unblocks B", result[0]["rank_reason"])
        self.assertNotIn("ready", issues[0])

    def test_dependency_cycles_remain_not_ready(self):
        result = core.rank_issues([{"id": "A", "blocked_by": ["B"]},
                                   {"id": "B", "blocked_by": ["A"]}])
        self.assertTrue(all(not issue["ready"] for issue in result))

    def test_canceled_and_duplicate_dependencies_are_not_delivered_outcomes(self):
        for state in ("canceled", "cancelled", "duplicate"):
            result = core.rank_issues([{"id": "prerequisite", "state": state},
                                       {"id": "task", "blocked_by": ["prerequisite"]}])
            self.assertEqual(len(result), 1)
            self.assertFalse(result[0]["ready"])
            self.assertEqual(result[0]["unresolved_blockers"], ["prerequisite"])

    def test_closed_not_planned_does_not_satisfy_a_dependency(self):
        result = core.rank_issues([{"id": "prerequisite", "state": "closed", "state_reason": "not_planned"},
                                   {"id": "task", "blocked_by": ["prerequisite"]}])
        self.assertFalse(result[0]["ready"])

    def test_closed_completed_and_legacy_closed_dependencies_still_resolve(self):
        for reason in ("completed", ""):
            result = core.rank_issues([{"id": "prerequisite", "state": "closed", "state_reason": reason},
                                       {"id": "task", "blocked_by": ["prerequisite"]}])
            self.assertTrue(result[0]["ready"])

    def test_blockers_inherit_highest_priority_through_dependency_chain(self):
        result = core.rank_issues([
            {"id": "urgent", "priority": 1, "blocked_by": ["middle"]},
            {"id": "middle", "priority": 4, "blocked_by": ["first"]},
            {"id": "first", "priority": 0}, {"id": "other", "priority": 2}])
        self.assertEqual(result[0]["id"], "first")
        self.assertEqual(result[0]["priority"], 0)
        self.assertEqual(result[0]["effective_priority"], 1)
        self.assertTrue(result[0]["ready"])

    def test_duplicate_ids_or_invalid_priorities_rejected(self):
        for issues in ([{"id": "x"}, {"id": "x"}], [{"id": "x", "priority": -1}]):
            with self.subTest(issues=issues), self.assertRaises(ValueError):
                core.rank_issues(issues)


class PlanningTests(unittest.TestCase):
    def finding(self, **kwargs):
        return {"concern_key": "auth:refresh-token", "kind": "create", "desired": {"title": "Fix refresh"},
                "duplicate_search_complete": True, **kwargs}

    def test_existing_canonical_prevents_duplicate_create(self):
        result = core.plan_findings(SCOPE, [self.finding()], {"auth:refresh-token": "LIN-42"})[0]
        self.assertEqual(result["kind"], "review_existing")
        self.assertEqual(result["target_id"], "LIN-42")
        self.assertFalse(result["write_candidate"])

    def test_duplicate_proof_findings_make_one_stable_plan(self):
        first = self.finding(evidence_refs=["pr/1"], observed_at="2026-10-18")
        second = self.finding(evidence_refs=["pr/2"], observed_at="2026-10-19")
        result = core.plan_findings(SCOPE, [first, second], {})
        self.assertEqual(len(result), 1)
        self.assertEqual(result, core.plan_findings(SCOPE, [second, first], {}))
        self.assertEqual(result[0]["kind"], "create")

    def test_conflicting_findings_require_review(self):
        result = core.plan_findings(SCOPE, [self.finding(), self.finding(desired={"title": "Other fix"})], {})[0]
        self.assertEqual(result["kind"], "review_conflict")
        self.assertFalse(result["write_candidate"])

    def test_incomplete_duplicate_search_prevents_create(self):
        result = core.plan_findings(SCOPE, [self.finding(duplicate_search_complete=False)], {})[0]
        self.assertEqual(result["kind"], "review")

    def test_missing_canonical_prevents_an_update(self):
        result = core.plan_findings(SCOPE, [self.finding(kind="update")], {})[0]
        self.assertFalse(result["write_candidate"])

    def test_partial_completion_is_not_a_close_candidate(self):
        record = completed_record()
        record["coverage"]["complete"] = False
        result = core.plan_findings(SCOPE, [self.finding(kind="complete", completion=record)],
                                    {"auth:refresh-token": "LIN-42"})[0]
        self.assertEqual(result["kind"], "review")
        self.assertFalse(result["write_candidate"])

    def test_conflicting_completion_evidence_fails_closed_in_any_order(self):
        good = self.finding(kind="complete", completion=completed_record())
        bad = copy.deepcopy(good)
        bad["completion"]["reverted"] = True
        one = core.plan_findings(SCOPE, [good, bad], {"auth:refresh-token": "LIN-42"})
        two = core.plan_findings(SCOPE, [bad, good], {"auth:refresh-token": "LIN-42"})
        self.assertEqual(one, two)
        self.assertFalse(one[0]["write_candidate"])

    def test_valid_completion_becomes_candidate_for_agent_review(self):
        result = core.plan_findings(SCOPE, [self.finding(kind="complete", completion=completed_record())],
                                    {"auth:refresh-token": {"id": "LIN-42"}})[0]
        self.assertEqual(result["kind"], "complete")
        self.assertTrue(result["write_candidate"])

    def test_merged_and_conflicting_findings_preserve_sorted_source_provenance(self):
        first = self.finding(evidence_refs=["pr/2", "pr/1"])
        second = self.finding(evidence_refs=["pr/3", "pr/2"])
        result = core.plan_findings(SCOPE, [first, second], {})[0]
        self.assertEqual(result["evidence_refs"], ["pr/1", "pr/2", "pr/3"])
        self.assertEqual(result, core.plan_findings(SCOPE, [second, first], {})[0])
        second["desired"] = {"title": "Conflict"}
        conflict = core.plan_findings(SCOPE, [first, second], {})[0]
        self.assertEqual(conflict["evidence_refs"], result["evidence_refs"])
        self.assertFalse(conflict["write_candidate"])

    def test_malformed_source_references_are_not_silently_discarded(self):
        for refs in (None, "pr/1", [""], ["pr/1", "pr/1"], [42]):
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                core.plan_findings(SCOPE, [self.finding(evidence_refs=refs)], {})

    def test_evidence_changes_do_not_change_operation_identity(self):
        first = core.plan_findings(SCOPE, [self.finding(evidence_refs=["pr/1"])], {})[0]
        second = core.plan_findings(SCOPE, [self.finding(evidence_refs=["pr/2"])], {})[0]
        self.assertEqual(first["operation_key"], second["operation_key"])
        self.assertEqual(first["fingerprint"], second["fingerprint"])


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "journal.jsonl"

    def test_timeout_after_create_requires_recovery_without_blind_retry(self):
        journal = core.Journal(self.path)
        self.assertTrue(journal.begin("create:1"))
        journal.record("create:1", "uncertain", {"reason": "create request timed out"})
        restored = core.Journal(self.path)
        self.assertFalse(restored.begin("create:1"))
        self.assertEqual(restored.latest("create:1")["status"], "uncertain")
        with self.assertRaises(ValueError):
            restored.record("create:1", "applied")

    def test_failed_readback_does_not_become_verified(self):
        journal = core.Journal(self.path)
        journal.begin("update:1")
        journal.record("update:1", "applied", {"remote_id": "LIN-42"})
        journal.record("update:1", "uncertain", {"reason": "readback differs"})
        self.assertFalse(core.Journal(self.path).begin("update:1"))

    def test_crash_after_planning_is_also_recovery_required(self):
        core.Journal(self.path).begin("create:1")
        self.assertFalse(core.Journal(self.path).begin("create:1"))

    def test_verified_operation_cannot_be_reapplied(self):
        journal = core.Journal(self.path)
        journal.begin("update:1")
        journal.record("update:1", "applied")
        journal.record("update:1", "verified", {"readback": "matches"})
        self.assertFalse(core.Journal(self.path).begin("update:1"))
        with self.assertRaises(ValueError):
            journal.record("update:1", "planned")

    def test_corrupt_log_requires_recovery_instead_of_silent_reset(self):
        self.path.write_text('{"operation_key":"x","status":"planned"}\n{truncated', encoding="utf-8")
        with self.assertRaises(ValueError):
            core.Journal(self.path)

    def test_replay_rejects_impossible_transition_history(self):
        for states in (("verified",), ("applied",), ("planned", "verified", "planned"),
                       ("planned", "uncertain", "applied"), ("planned", "planned")):
            entries = [{"operation_key": "x", "status": state, "detail": {}} for state in states]
            self.path.write_text("".join(json.dumps(entry) + "\n" for entry in entries))
            with self.subTest(states=states), self.assertRaises(ValueError):
                core.Journal(self.path)

    def test_unterminated_json_line_cannot_be_concatenated_with_a_later_append(self):
        original = json.dumps({"operation_key": "x", "status": "planned", "detail": {}})
        self.path.write_text(original)
        with self.assertRaises(ValueError):
            core.Journal(self.path)
        self.assertEqual(self.path.read_text(), original)

    def test_replay_accepts_interleaved_valid_operation_histories(self):
        journal = core.Journal(self.path)
        journal.begin("a")
        journal.begin("b")
        journal.record("a", "applied")
        journal.record("b", "uncertain")
        journal.record("a", "verified")
        journal.record("b", "verified")
        restored = core.Journal(self.path)
        self.assertEqual(restored.latest("a")["status"], "verified")
        self.assertEqual(restored.latest("b")["status"], "verified")

    def test_record_and_replay_reject_nonobject_details(self):
        for detail in ([], "text", 0, False):
            with self.subTest(detail=detail), self.assertRaises(ValueError):
                core.Journal(self.path).begin("x", detail)
            self.assertFalse(self.path.exists())
        for detail in (None, [], "text", 0, False):
            self.path.write_text(json.dumps({"operation_key": "x", "status": "planned", "detail": detail}) + "\n")
            with self.subTest(detail=detail), self.assertRaises(ValueError):
                core.Journal(self.path)

    def test_mutating_input_or_latest_snapshot_cannot_change_recorded_intent(self):
        journal = core.Journal(self.path)
        detail = {"expected": {"title": "original"}, "sources": ["pr/1"]}
        journal.begin("x", detail)
        detail["expected"]["title"] = "changed"
        detail["sources"].append("pr/2")
        snapshot = journal.latest("x")
        snapshot["detail"]["expected"]["title"] = "also changed"
        self.assertEqual(journal.latest("x"), core.Journal(self.path).latest("x"))
        self.assertEqual(journal.latest("x")["detail"],
                         {"expected": {"title": "original"}, "sources": ["pr/1"]})


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                              text=True, capture_output=True, check=False)

    def test_window_cli_outputs_json_and_bad_timestamp_exits_nonzero(self):
        result = self.run_cli("window", "--now", "2026-10-19T12:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["start"], "2026-09-21T12:00:00Z")
        invalid = self.run_cli("window", "--now", "2026-10-19")
        self.assertEqual(invalid.returncode, 2)

    def test_gate_cli_distinguishes_evaluation_from_eligibility(self):
        result = self.run_cli("gate", "-", stdin=json.dumps({}))
        self.assertEqual(result.returncode, 0)
        self.assertFalse(json.loads(result.stdout)["eligible"])

    def test_coverage_cli_reports_structural_results_without_fetching(self):
        complete = self.run_cli("coverage", "-", stdin=json.dumps(covered_record()))
        self.assertEqual(complete.returncode, 0, complete.stderr)
        self.assertEqual(json.loads(complete.stdout), {"complete": True, "reasons": []})
        incomplete = self.run_cli("coverage", "-", stdin="{}")
        self.assertEqual(incomplete.returncode, 0)
        self.assertFalse(json.loads(incomplete.stdout)["complete"])
        malformed = self.run_cli("coverage", "-", stdin="{")
        self.assertEqual(malformed.returncode, 2)

    def test_rank_and_fingerprint_json_input(self):
        rank = self.run_cli("rank", "-", stdin='[{"id":"x","priority":0}]')
        self.assertEqual(json.loads(rank.stdout)[0]["id"], "x")
        identity = self.run_cli("fingerprint", "-", stdin=json.dumps({
            "scope": SCOPE, "concern_key": "a", "kind": "update", "desired": {"title": "A"}}))
        self.assertEqual(json.loads(identity.stdout)["fingerprint"], core.fingerprint(SCOPE, "a"))
        self.assertIn("operation_key", json.loads(identity.stdout))


if __name__ == "__main__":
    unittest.main()
