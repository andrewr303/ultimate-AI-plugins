#!/usr/bin/env python3
"""Evaluate an explicit evidence packet; never submit an app or certify compliance."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import plistlib
import re
import stat
import sys

MAX_INPUT = 2 * 1024 * 1024
BASE = {'policy_scope', 'artifact_identity', 'signing', 'privacy_data_map', 'data_declarations', 'product_flows'}
STORE = {'metadata_assets', 'review_access', 'account_lifecycle', 'commerce', 'content_age_rights', 'export_compliance', 'backend_access'}
DIRECT = {'hardened_runtime', 'notarization_plan'}
STAGES = {'prepare', 'upload', 'distribute', 'submit', 'release', 'notarize'}
STATUSES = {'satisfied', 'blocked', 'unknown', 'not_applicable'}
IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]{0,79}$')


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def load_packet(path: Path):
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('Evidence packet must be a regular file')
        data = stream.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise ValueError('Evidence packet exceeds size bound')
    try:
        return json.loads(data, object_pairs_hook=_pairs)
    except RecursionError:
        raise ValueError('Evidence packet nesting exceeds supported depth') from None


def evaluate(packet: dict) -> dict:
    if not isinstance(packet, dict) or set(packet) - {'schema_version', 'scope', 'checks'}:
        raise ValueError('Packet must contain only schema_version, scope and checks')
    if type(packet.get('schema_version')) is not int or packet['schema_version'] != 1:
        raise ValueError('schema_version must be integer 1')
    scope = packet.get('scope')
    if not isinstance(scope, dict) or set(scope) - {'bundle_id', 'platform', 'channel', 'storefronts', 'requested_stage'}:
        raise ValueError('Scope has missing or unsupported structure')
    bundle = scope.get('bundle_id')
    if not isinstance(bundle, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{1,249}', bundle):
        raise ValueError('Provide a nonblank bundle identifier')
    if not isinstance(scope.get('platform'), str) or scope['platform'] not in {'ios', 'ipados', 'macos', 'watchos', 'tvos', 'visionos'}:
        raise ValueError('Unsupported or unknown platform')
    channel, stage = scope.get('channel'), scope.get('requested_stage')
    if not isinstance(channel, str) or channel not in {'app_store', 'developer_id'} or not isinstance(stage, str) or stage not in STAGES:
        raise ValueError('Choose a supported channel and requested stage; other lanes need a manual profile')
    if channel == 'developer_id' and (scope['platform'] != 'macos' or stage not in {'prepare', 'notarize', 'release'}):
        raise ValueError('Developer ID profile is for macOS direct distribution')
    if stage == 'notarize' and channel != 'developer_id':
        raise ValueError('Notarization is a separate Developer ID profile here')
    storefronts = scope.get('storefronts')
    if not isinstance(storefronts, list) or not storefronts or not all(isinstance(s, str) and re.fullmatch(r'[A-Z]{2}', s) for s in storefronts):
        raise ValueError('Provide explicit storefront/region codes for applicability review')
    if len(storefronts) != len(set(storefronts)):
        raise ValueError('Duplicate storefront/region codes')
    required = BASE | (STORE if channel == 'app_store' else DIRECT)
    if channel == 'app_store' and stage in {'submit', 'release'}:
        required |= {'build_processed', 'submission_items_ready'}
    if stage == 'release' and channel == 'app_store':
        required |= {'review_approved', 'release_scope'}
    if stage == 'release' and channel == 'developer_id':
        required |= {'notary_accepted', 'ticket_verified', 'release_scope'}
    mandatory = BASE | ({'metadata_assets', 'content_age_rights', 'export_compliance'} if channel == 'app_store' else DIRECT)
    checks = packet.get('checks')
    if not isinstance(checks, list) or len(checks) > 200:
        raise ValueError('checks must be a bounded list')
    indexed = {}
    for check in checks:
        if not isinstance(check, dict) or set(check) - {'id', 'status', 'evidence', 'applicability_reason'}:
            raise ValueError('Check has unsupported structure')
        identity = check.get('id')
        if not isinstance(identity, str) or not IDENTIFIER.fullmatch(identity) or identity in indexed:
            raise ValueError('Check IDs must be unique safe identifiers')
        status = check.get('status')
        evidence = check.get('evidence')
        if not isinstance(status, str) or status not in STATUSES or not isinstance(evidence, list) or len(evidence) > 20 or not all(isinstance(v, str) and 0 < len(v.strip()) <= 2000 for v in evidence):
            raise ValueError('Check status/evidence has unsupported structure')
        if status in {'satisfied', 'not_applicable'} and not evidence:
            raise ValueError('Satisfied and not-applicable checks require evidence references')
        if status == 'not_applicable':
            reason = check.get('applicability_reason')
            if not isinstance(reason, str) or not reason.strip() or len(reason) > 2000:
                raise ValueError('Not-applicable checks require a bounded reason')
            if identity in mandatory:
                raise ValueError('A core profile check cannot be not applicable')
        indexed[identity] = check
    missing = sorted(required - indexed.keys())
    blocked = sorted(k for k, v in indexed.items() if v['status'] == 'blocked')
    unknown = sorted(k for k, v in indexed.items() if v['status'] == 'unknown')
    status = 'blocked' if blocked else 'needs_evidence' if missing or unknown else 'ready_for_requested_stage'
    return {'schema_version': 1, 'status': status, 'requested_stage': stage, 'channel': channel,
            'missing_checks': missing, 'blocked_checks': blocked, 'unknown_checks': unknown,
            'required_checks': sorted(required), 'observed_check_count': len(indexed),
            'evidence_reference_count': sum(len(v['evidence']) for v in indexed.values()),
            'limits': ['Evidence assertions are supplied by the owner; content and truth are not authenticated by this tool.',
                       'Readiness is only for the requested profile/stage; it is not App Store approval, legal or security certification.',
                       'No Apple API, signing identity, app artifact or device behavior is changed or remotely checked.']}


def inspect_artifact(directory: Path, max_files: int = 20000) -> dict:
    """Extract bounded plist observations, never infer policy answers or modify a bundle."""
    root = directory.resolve()
    if not root.is_dir() or directory.is_symlink():
        raise ValueError('Artifact must be a real app/archive directory; IPA extraction is a separate operation')
    if type(max_files) is not int or not 1 <= max_files <= 20000:
        raise ValueError('Invalid artifact scan bound')
    result = {'files_seen': 0, 'truncated': False, 'bundle_metadata': [], 'privacy_manifests': [], 'warnings': [],
              'limit': 'Observed metadata only. Presence or syntax does not prove correct declarations, API use, signing or policy compliance.'}
    for current, dirs, files in os.walk(root, followlinks=False):
        here = Path(current)
        dirs[:] = sorted(d for d in dirs if not (here / d).is_symlink() and d not in {'.git', 'node_modules', 'Pods', '.build'})
        for name in sorted(files):
            if result['files_seen'] >= max_files:
                result['truncated'] = True
                break
            result['files_seen'] += 1
            if name not in {'Info.plist', 'PrivacyInfo.xcprivacy'}:
                continue
            file = here / name
            rel = str(file.relative_to(root))
            if file.is_symlink() or not file.resolve().is_relative_to(root):
                result['warnings'].append({'path': rel, 'reason': 'link_or_outside_root'})
                continue
            try:
                flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
                with os.fdopen(os.open(file, flags), 'rb') as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        result['warnings'].append({'path': rel, 'reason': 'nonregular'})
                        continue
                    data = stream.read(MAX_INPUT + 1)
                if len(data) > MAX_INPUT:
                    result['warnings'].append({'path': rel, 'reason': 'oversized'})
                    continue
                obj = plistlib.loads(data)
                if not isinstance(obj, dict):
                    raise ValueError('Expected a plist dictionary')
                if name == 'Info.plist':
                    values = {}
                    for key in ('CFBundleIdentifier', 'CFBundleShortVersionString', 'CFBundleVersion', 'CFBundlePackageType'):
                        value = obj.get(key)
                        values[key] = value if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9.+_-]{1,250}', value) else None
                    result['bundle_metadata'].append({'path': rel, 'values': values,
                                                     'usage_description_keys': sorted(k for k in obj if isinstance(k, str) and re.fullmatch(r'NS[A-Za-z]+UsageDescription', k)),
                                                     'encryption_declaration_present': 'ITSAppUsesNonExemptEncryption' in obj})
                else:
                    tracking = obj.get('NSPrivacyTracking')
                    accessed = obj.get('NSPrivacyAccessedAPITypes')
                    collected = obj.get('NSPrivacyCollectedDataTypes')
                    result['privacy_manifests'].append({'path': rel, 'tracking_boolean_present': type(tracking) is bool,
                                                        'accessed_api_entry_count': len(accessed) if isinstance(accessed, list) else None,
                                                        'collected_data_entry_count': len(collected) if isinstance(collected, list) else None,
                                                        'separate_bundle_scope': True})
            except (OSError, ValueError, plistlib.InvalidFileException, TypeError, OverflowError, RecursionError):
                result['warnings'].append({'path': rel, 'reason': 'unreadable_or_invalid_plist'})
        if result['truncated']:
            break
    if not result['bundle_metadata']:
        result['warnings'].append({'reason': 'no_bundle_metadata_observed'})
    return result


def build_report(packet: dict, artifact: Path | None = None) -> dict:
    report = evaluate(packet)
    if artifact is None:
        return report
    observed = inspect_artifact(artifact)
    report['artifact_observations'] = observed
    candidates = {row['values']['CFBundleIdentifier'] for row in observed['bundle_metadata']
                  if row['values']['CFBundlePackageType'] == 'APPL' and row['values']['CFBundleIdentifier']}
    expected = packet['scope']['bundle_id']
    if candidates and expected not in candidates and not observed['truncated']:
        report['status'] = 'blocked'
        report['blocked_checks'] = sorted(set(report['blocked_checks']) | {'artifact_identity'})
        report['artifact_identity_observation'] = 'Expected app identifier was not found in observed application bundles'
    elif expected not in candidates:
        if report['status'] != 'blocked':
            report['status'] = 'needs_evidence'
        report['unknown_checks'] = sorted(set(report['unknown_checks']) | {'artifact_identity'})
        report['artifact_identity_observation'] = ('Expected application identifier was not found in the partial scan'
                                                   if observed['truncated'] else 'No interpretable application-bundle identity was observed')
    else:
        report['artifact_identity_observation'] = 'Expected identifier observed; signing and App Store identity remain separate checks'
    if observed['truncated']:
        if report['status'] != 'blocked':
            report['status'] = 'needs_evidence'
        report['unknown_checks'] = sorted(set(report['unknown_checks']) | {'artifact_scan_completeness'})
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--artifact', type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(load_packet(args.evidence), args.artifact)
        print(json.dumps(report, indent=2))
        return 0 if report['status'] == 'ready_for_requested_stage' else 1
    except (ValueError, OSError, TypeError, UnicodeError) as error:
        print(json.dumps({'status': 'invalid_input', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
