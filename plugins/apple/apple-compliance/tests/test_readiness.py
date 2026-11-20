from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('readiness', ROOT / 'scripts/readiness.py')
readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readiness)


def packet():
    # Fictional evidence references exercise the public packet contract, not policy truth.
    checks = ['policy_scope', 'artifact_identity', 'signing', 'privacy_data_map', 'data_declarations',
              'product_flows', 'metadata_assets', 'review_access', 'account_lifecycle', 'commerce',
              'content_age_rights', 'export_compliance', 'backend_access']
    return {'schema_version': 1, 'scope': {'bundle_id': 'com.example.demo', 'platform': 'ios',
            'channel': 'app_store', 'storefronts': ['US', 'GB'], 'requested_stage': 'prepare'},
            'checks': [{'id': item, 'status': 'satisfied', 'evidence': ['fixture:owner-observation/' + item]} for item in checks]}


class ReadinessTests(unittest.TestCase):
    def test_complete_preparation_is_only_ready_for_requested_stage(self):
        result = readiness.evaluate(packet())
        self.assertEqual(result['status'], 'ready_for_requested_stage')
        self.assertEqual(result['requested_stage'], 'prepare')
        self.assertTrue(any('not App Store approval' in limit for limit in result['limits']))

    def test_absent_check_stays_missing(self):
        value = packet()
        value['checks'] = [c for c in value['checks'] if c['id'] != 'export_compliance']
        result = readiness.evaluate(value)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertEqual(result['missing_checks'], ['export_compliance'])

    def test_unknown_is_not_satisfied_or_not_applicable(self):
        value = packet()
        value['checks'][0].update(status='unknown', evidence=[])
        result = readiness.evaluate(value)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertEqual(result['unknown_checks'], ['policy_scope'])

    def test_concrete_blocker_wins_over_unknowns(self):
        value = packet()
        value['checks'][0]['status'] = 'unknown'
        value['checks'][1]['status'] = 'blocked'
        result = readiness.evaluate(value)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['blocked_checks'], ['artifact_identity'])

    def test_not_applicable_requires_reason_and_evidence(self):
        value = packet()
        check = next(c for c in value['checks'] if c['id'] == 'commerce')
        check.update(status='not_applicable', applicability_reason='Fictional app has no commerce features')
        self.assertEqual(readiness.evaluate(value)['status'], 'ready_for_requested_stage')
        del check['applicability_reason']
        with self.assertRaises(ValueError):
            readiness.evaluate(value)
        check['applicability_reason'] = 'Reason supplied'
        check['evidence'] = []
        with self.assertRaises(ValueError):
            readiness.evaluate(value)

    def test_core_checks_cannot_be_waived(self):
        value = packet()
        value['checks'][0].update(status='not_applicable', applicability_reason='Skip source review')
        with self.assertRaises(ValueError):
            readiness.evaluate(value)

    def test_submit_requires_processing_and_items_ready(self):
        value = packet()
        value['scope']['requested_stage'] = 'submit'
        result = readiness.evaluate(value)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertEqual(set(result['missing_checks']), {'build_processed', 'submission_items_ready'})

    def test_release_requires_approval_and_release_scope(self):
        value = packet()
        value['scope']['requested_stage'] = 'release'
        result = readiness.evaluate(value)
        self.assertIn('review_approved', result['missing_checks'])
        self.assertIn('release_scope', result['missing_checks'])

    def test_mac_developer_id_does_not_require_app_store_submission(self):
        value = packet()
        value['scope'].update(platform='macos', channel='developer_id', requested_stage='release')
        value['checks'] = [c for c in value['checks'] if c['id'] in {'policy_scope', 'artifact_identity', 'signing', 'privacy_data_map', 'data_declarations', 'product_flows'}]
        for identity in ['hardened_runtime', 'notarization_plan', 'notary_accepted', 'ticket_verified', 'release_scope']:
            value['checks'].append({'id': identity, 'status': 'satisfied', 'evidence': ['fixture:direct-distribution/' + identity]})
        result = readiness.evaluate(value)
        self.assertEqual(result['status'], 'ready_for_requested_stage')
        self.assertNotIn('review_approved', result['required_checks'])
        self.assertNotIn('build_processed', result['required_checks'])

    def test_notarization_cannot_masquerade_as_ios_review(self):
        value = packet()
        value['scope']['requested_stage'] = 'notarize'
        with self.assertRaises(ValueError):
            readiness.evaluate(value)
        value['scope'].update(channel='developer_id')
        with self.assertRaises(ValueError):
            readiness.evaluate(value)

    def test_no_global_region_assumption(self):
        value = packet()
        value['scope']['storefronts'] = []
        with self.assertRaises(ValueError):
            readiness.evaluate(value)

    def test_duplicate_and_malformed_statuses_are_rejected(self):
        for change in ['duplicate', 'unrecognized', 'boolean_version', 'secret_field', 'empty_evidence']:
            with self.subTest(change=change):
                value = packet()
                if change == 'duplicate': value['checks'].append(copy.deepcopy(value['checks'][0]))
                elif change == 'unrecognized': value['checks'][0]['status'] = 'passed_all_rules'
                elif change == 'boolean_version': value['schema_version'] = True
                elif change == 'secret_field': value['checks'][0]['private_token'] = 'should-never-be-output'
                else: value['checks'][0]['evidence'] = []
                with self.assertRaises(ValueError): readiness.evaluate(value)

    def test_reports_do_not_echo_evidence_or_private_values(self):
        value = packet()
        value['checks'][0]['evidence'] = ['private location or owner notes should stay in the packet']
        rendered = json.dumps(readiness.evaluate(value))
        self.assertNotIn('private location', rendered)

    def test_container_scope_and_status_types_are_rejected_without_echo(self):
        mutations = [('platform', []), ('channel', {}), ('requested_stage', [])]
        with tempfile.TemporaryDirectory() as temporary:
            file = Path(temporary) / 'packet.json'
            for field, replacement in mutations + [('status', {'private': 'private-owner-note'})]:
                with self.subTest(field=field):
                    value = packet()
                    if field == 'status':
                        value['checks'][0]['status'] = replacement
                    else:
                        value['scope'][field] = replacement
                    with self.assertRaises(ValueError):
                        readiness.evaluate(value)
                    file.write_text(json.dumps(value))
                    result = subprocess.run([sys.executable, str(ROOT / 'scripts/readiness.py'), '--evidence', str(file)],
                                            capture_output=True, text=True, timeout=3)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(json.loads(result.stderr)['status'], 'invalid_input')
                    self.assertNotIn('private-owner-note', result.stdout + result.stderr)

    def test_deep_json_is_invalid_input_without_traceback_or_evidence_echo(self):
        with tempfile.TemporaryDirectory() as temporary:
            file = Path(temporary) / 'packet.json'
            prefix = '{"schema_version":1,"scope":' + json.dumps(packet()['scope']) + ',"checks":'
            file.write_text(prefix + '[' * 20000 + '"private-owner-note"' + ']' * 20000 + '}')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/readiness.py'), '--evidence', str(file)],
                                    capture_output=True, text=True, timeout=3)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)['status'], 'invalid_input')
            self.assertNotIn('Traceback', result.stdout + result.stderr)
            self.assertNotIn('private-owner-note', result.stdout + result.stderr)

    def test_cli_exit_codes_and_duplicate_json_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            file = Path(temporary) / 'packet.json'
            for variant, expected in [('ready', 0), ('unknown', 1), ('invalid', 2), ('duplicate', 2)]:
                value = packet()
                if variant == 'unknown': value['checks'][0]['status'] = 'unknown'
                file.write_text('{bad' if variant == 'invalid' else '{"schema_version":1,"schema_version":1}' if variant == 'duplicate' else json.dumps(value))
                result = subprocess.run([sys.executable, str(ROOT / 'scripts/readiness.py'), '--evidence', str(file)], capture_output=True, text=True, timeout=3)
                self.assertEqual(result.returncode, expected)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_plist(self, relative, data):
        file = self.root / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(plistlib.dumps(data))
        return file

    def test_metadata_scan_is_read_only_and_does_not_infer_privacy_truth(self):
        info = self.write_plist('Info.plist', {'CFBundleIdentifier':'com.example.demo', 'CFBundleVersion':'9',
                                'CFBundlePackageType':'APPL', 'NSCameraUsageDescription':'Private wording', 'ITSAppUsesNonExemptEncryption':True})
        before = info.read_bytes()
        observed = readiness.inspect_artifact(self.root)
        self.assertEqual(info.read_bytes(), before)
        self.assertTrue(observed['bundle_metadata'][0]['encryption_declaration_present'])
        self.assertNotIn('Private wording', json.dumps(observed))
        self.assertIn('does not prove', observed['limit'])

    def test_app_and_sdk_manifests_keep_separate_scopes(self):
        self.write_plist('Info.plist', {'CFBundleIdentifier':'com.example.demo', 'CFBundlePackageType':'APPL'})
        self.write_plist('PrivacyInfo.xcprivacy', {'NSPrivacyTracking':False, 'NSPrivacyAccessedAPITypes':[]})
        self.write_plist('Frameworks/SDK.framework/PrivacyInfo.xcprivacy', {'NSPrivacyTracking':False, 'NSPrivacyAccessedAPITypes':[{'NSPrivacyAccessedAPIType':'fixture'}]})
        result = readiness.inspect_artifact(self.root)
        self.assertEqual(len(result['privacy_manifests']), 2)
        self.assertEqual({r['accessed_api_entry_count'] for r in result['privacy_manifests']}, {0, 1})
        self.assertTrue(all(r['separate_bundle_scope'] for r in result['privacy_manifests']))

    def test_observed_wrong_artifact_blocks_owner_assertion(self):
        self.write_plist('Info.plist', {'CFBundleIdentifier':'com.example.other', 'CFBundlePackageType':'APPL'})
        result = readiness.build_report(packet(), self.root)
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('artifact_identity', result['blocked_checks'])

    def test_unreadable_identity_stays_unknown(self):
        (self.root / 'Info.plist').write_text('invalid plist')
        result = readiness.build_report(packet(), self.root)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertIn('artifact_identity', result['unknown_checks'])

    def test_matching_artifact_does_not_claim_signature_verification(self):
        self.write_plist('Info.plist', {'CFBundleIdentifier':'com.example.demo', 'CFBundlePackageType':'APPL'})
        result = readiness.build_report(packet(), self.root)
        self.assertEqual(result['status'], 'ready_for_requested_stage')
        self.assertIn('signing', result['artifact_identity_observation'])

    def test_truncated_matching_scan_needs_evidence_and_keeps_existing_blockers(self):
        self.write_plist('Info.plist', {'CFBundleIdentifier':'com.example.demo', 'CFBundlePackageType':'APPL'})
        (self.root / 'zz.dat').write_text('unobserved fixture')
        inspector = readiness.inspect_artifact
        for blocked in (False, True):
            with self.subTest(blocked=blocked):
                value = packet()
                if blocked:
                    value['checks'][0]['status'] = 'blocked'
                with mock.patch.object(readiness, 'inspect_artifact', side_effect=lambda directory: inspector(directory, max_files=1)):
                    result = readiness.build_report(value, self.root)
                self.assertTrue(result['artifact_observations']['truncated'])
                self.assertEqual(result['status'], 'blocked' if blocked else 'needs_evidence')
                self.assertIn('artifact_scan_completeness', result['unknown_checks'])
                self.assertNotIn('artifact_identity', result['blocked_checks'])

    def test_partial_wrong_identity_does_not_establish_a_complete_mismatch(self):
        self.write_plist('Info.plist', {'CFBundleIdentifier':'com.example.other', 'CFBundlePackageType':'APPL'})
        (self.root / 'zz.dat').write_text('unobserved fixture')
        inspector = readiness.inspect_artifact
        with mock.patch.object(readiness, 'inspect_artifact', side_effect=lambda directory: inspector(directory, max_files=1)):
            result = readiness.build_report(packet(), self.root)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertIn('artifact_identity', result['unknown_checks'])
        self.assertIn('artifact_scan_completeness', result['unknown_checks'])
        self.assertNotIn('artifact_identity', result['blocked_checks'])

    def test_deep_binary_plist_warns_without_a_cli_traceback(self):
        # Valid binary plist object references form a deeply nested array. Build
        # bytes directly so the fixture encoder does not hit Python recursion.
        depth = 2000
        objects = [b'\xa1' + (index + 1).to_bytes(2, 'big') for index in range(depth)]
        objects.append(b'\x5cprivate-note')
        offsets, position = [], 8
        for item in objects:
            offsets.append(position)
            position += len(item)
        table = b''.join(offset.to_bytes(4, 'big') for offset in offsets)
        trailer = b'\x00' * 6 + bytes([4, 2]) + len(objects).to_bytes(8, 'big') + b'\x00' * 8 + position.to_bytes(8, 'big')
        (self.root / 'Info.plist').write_bytes(b'bplist00' + b''.join(objects) + table + trailer)
        file = self.root / 'packet.json'
        file.write_text(json.dumps(packet()))
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/readiness.py'), '--evidence', str(file), '--artifact', str(self.root)],
                                capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'needs_evidence')
        self.assertTrue(any(w['reason'] == 'unreadable_or_invalid_plist' for w in report['artifact_observations']['warnings']))
        self.assertNotIn('Traceback', result.stdout + result.stderr)
        self.assertNotIn('private-note', result.stdout + result.stderr)

    def test_invalid_plist_value_types_stay_observations_without_private_echo(self):
        self.write_plist('Info.plist', {'CFBundleIdentifier':['private-owner-note'], 'CFBundlePackageType':'APPL'})
        self.write_plist('PrivacyInfo.xcprivacy', {'NSPrivacyTracking':'private-owner-note', 'NSPrivacyAccessedAPITypes':{}, 'NSPrivacyCollectedDataTypes':True})
        result = readiness.build_report(packet(), self.root)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertIn('artifact_identity', result['unknown_checks'])
        privacy = result['artifact_observations']['privacy_manifests'][0]
        self.assertFalse(privacy['tracking_boolean_present'])
        self.assertIsNone(privacy['accessed_api_entry_count'])
        self.assertIsNone(privacy['collected_data_entry_count'])
        self.assertNotIn('private-owner-note', json.dumps(result))

    def test_scan_bounds_are_integers_and_oversized_metadata_is_not_a_match(self):
        for bound in (True, 1.5, [], 0, 20001):
            with self.subTest(bound=bound), self.assertRaises(ValueError):
                readiness.inspect_artifact(self.root, max_files=bound)
        (self.root / 'Info.plist').write_bytes(b'x' * (readiness.MAX_INPUT + 1))
        result = readiness.build_report(packet(), self.root)
        self.assertEqual(result['status'], 'needs_evidence')
        self.assertEqual(result['artifact_observations']['bundle_metadata'], [])
        self.assertTrue(any(w['reason'] == 'oversized' for w in result['artifact_observations']['warnings']))

    def test_symlink_and_oversize_are_skipped(self):
        with tempfile.TemporaryDirectory() as outside:
            secret = Path(outside) / 'Info.plist'
            secret.write_bytes(plistlib.dumps({'CFBundleIdentifier':'outside.private'}))
            (self.root / 'Info.plist').symlink_to(secret)
            (self.root / 'PrivacyInfo.xcprivacy').write_bytes(b'x' * (readiness.MAX_INPUT + 1))
            result = readiness.inspect_artifact(self.root)
            self.assertEqual(result['bundle_metadata'], [])
            self.assertNotIn('outside.private', json.dumps(result))
            self.assertTrue(any(x['reason'] == 'oversized' for x in result['warnings']))

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX fixture')
    def test_fifo_packet_and_metadata_do_not_hang(self):
        fifo = self.root / 'evidence.json'
        os.mkfifo(fifo)
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/readiness.py'), '--evidence', str(fifo)], capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 2)
        os.mkfifo(self.root / 'Info.plist')
        result = readiness.inspect_artifact(self.root)
        self.assertTrue(any(w['reason'] == 'nonregular' for w in result['warnings']))


if __name__ == '__main__':
    unittest.main()
