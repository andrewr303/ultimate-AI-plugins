#!/usr/bin/env python3
"""Explain deterministic skill suggestions; does not execute agent skills or actions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROUTES = Path(__file__).resolve().parents[1] / 'skills/ios-development/references/routes.json'


def suggest(request: str, stack: str = 'auto') -> dict:
    if stack not in {'auto', 'native', 'expo', 'react-native'}:
        raise ValueError('Unknown stack')
    if not isinstance(request, str) or not request.strip():
        raise ValueError('Request must contain text')
    if len(request) > 20000:
        raise ValueError('Request is too long for the routing aid')
    text = request.casefold()
    # Honor the explicit native/React Native boundary in common negative cases.
    # This small aid is deliberately not a general natural-language parser.
    if stack != 'expo':
        text = re.sub(r'\b(?:without|no|not)\s+expo\b', '', text)
    rules = json.loads(ROUTES.read_text(encoding='utf-8'))
    explicit_context = bool(re.search(r'\b(ios|iphone|ipad|swift|swiftui|uikit|xcode|expo|testflight|app store|core data|coredata|swiftdata|nuke|exytechat|exyte chat|eas)\b', text))
    applicable = stack != 'auto' or explicit_context
    found = []
    for rule in rules:
        matches = [p for p in rule['patterns'] if re.search(p, text)]
        if matches and (applicable or rule.get('establishes_context', False)):
            found.append({'skill': rule['skill'], 'score': rule['priority'], 'matched_patterns': matches, 'purpose': rule['purpose']})
            applicable = True
    if stack == 'expo' or (stack == 'auto' and re.search(r'\b(expo|eas)\b', text)):
        # Native Swift diagnostics still get a specialist; Expo owns general app work.
        for item in found:
            if item['skill'] == 'ios-expo':
                item['score'] = max(item['score'], 85)
        if not any(x['skill'] == 'ios-expo' for x in found):
            found.append({'skill': 'ios-expo', 'score': 85, 'matched_patterns': ['explicit expo stack'], 'purpose': 'Expo app or authorized EAS workflow'})
        applicable = True
    found.sort(key=lambda x: (-x['score'], x['skill']))
    primary = found[0]['skill'] if found else ('ios-development' if applicable else None)
    return {'format_version': 1, 'applicable': applicable, 'primary': primary,
            'supporting': [x['skill'] for x in found[1:4]], 'matches': found,
            'limitation': 'Keyword-based suggestions only. The agent must read project evidence and skill descriptions. This does not test host model invocation or authorize any action.'}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request')
    parser.add_argument('--stack', choices=('auto', 'native', 'expo', 'react-native'), default='auto')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(suggest(args.request, args.stack), indent=2))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'route: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
