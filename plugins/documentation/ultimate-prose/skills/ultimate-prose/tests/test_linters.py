"""Regression coverage for source boundaries, advisory behavior and public CLIs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import lint
import lint_andrew


class BoundaryTests(unittest.TestCase):
    def test_short_authored_lines_are_not_signatures(self):
        self.assertEqual(lint.split_sentences('Approved'), ['Approved'])
        self.assertEqual(lint.split_sentences('Ship it'), ['Ship it'])
        self.assertEqual(lint.split_sentences('DO NOT'), ['DO NOT'])

    def test_real_greeting_and_signature_do_not_skew_cadence(self):
        text = 'Hi Dana,\n\nThe report is ready.\n\nBest,\nAndrew Rodriguez'
        self.assertEqual(lint.split_sentences(text), ['The report is ready.'])

    def test_abbreviations_decimals_versions_addresses(self):
        text = ('Dr. Smith checked v1.2. The rate was 2.5 percent. '
                'Email a.b@example.com for the report. '
                'See https://example.com/v1.2. Then confirm the $2.50 price.')
        parts = lint.split_sentences(text)
        self.assertEqual(len(parts), 5)
        self.assertEqual(parts[0], 'Dr. Smith checked v1.2.')
        self.assertIn('2.5 percent.', parts[1])
        self.assertIn('a.b@example.com', parts[2])
        self.assertIn('https://example.com/v1.2.', parts[3])

    def test_mask_length_newlines_and_original_finding_offsets(self):
        text = ('> great question\n\n```markdown\n# This Is Source Code\n'
                '- **Owner:** robust\n```\n\n"great question"\n\n'
                'At its core, the remaining work is contract review.')
        masked = lint.mask_sources(text)
        self.assertEqual(len(masked), len(text))
        self.assertEqual([i for i, ch in enumerate(masked) if ch == '\n'],
                         [i for i, ch in enumerate(text) if ch == '\n'])
        findings, _ = lint.check(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 10)
        self.assertEqual(findings[0].offset_start, text.index('At its core'))
        self.assertEqual(findings[0].evidence, text.splitlines()[9])

    def test_quoted_code_and_citations_are_excluded(self):
        text = ('The source says "at its core, great question."\n'
                '“This changes everything.\nGreat question.”\n'
                '`great question`\n'
                'The estimate is uncertain (Smith et al., 2024) [1, 2–3].\n'
                'https://example.com/great-question a.b@example.com')
        findings, _ = lint.check(text, strict=True)
        self.assertFalse(findings)
        masked = lint.mask_sources(text)
        self.assertNotIn('Smith', masked)
        self.assertNotIn('example.com', masked)

    def test_include_quotes_does_not_include_code(self):
        text = '"great question"\n`at its core`\n'
        findings, _ = lint.check(text, include_quotes=True)
        self.assertEqual(len(findings), 1)
        self.assertIn('great question', findings[0].rule)

    def test_unclosed_fence_is_source_material(self):
        self.assertFalse(lint.check('```python\ngreat question\n')[0])

    def test_author_parenthetical_with_year_is_not_a_citation(self):
        text = 'The contract is ready (We shipped it in 2024, and support is still limited).'
        self.assertIn('We shipped it in 2024', lint.mask_sources(text))
        self.assertEqual(lint.mask_sources('(Smith, 2024)'), ' ' * len('(Smith, 2024)'))

    def test_personalized_findings_preserve_source_evidence(self):
        text = '> fuck this\n\nThe fucking approval process failed.'
        findings, _ = lint_andrew.check_andrew(text, genre='email')
        casual = [f for f in findings if f.category == 'andrew-casual-residue']
        self.assertEqual(len(casual), 1)
        self.assertEqual(casual[0].line, 3)
        self.assertEqual(casual[0].evidence, text.splitlines()[2])
        self.assertEqual(casual[0].offset_start, text.index('fucking'))


class AdvisoryTests(unittest.TestCase):
    def test_genuine_question_is_not_assumed_rhetorical(self):
        findings, _ = lint.check('Can you meet on Thursday?')
        self.assertFalse([f for f in findings if f.category == 'opening'])

    def test_real_support_questions_have_no_arbitrary_question_budget(self):
        text = ('Which version failed? What did the log say? '
                'Did the retry succeed? Can you share the reproduction steps?')
        findings, _ = lint_andrew.check_andrew(text, genre='email', formality='executive')
        self.assertFalse([f for f in findings if 'question-budget' in f.category])
        requirements, _ = lint_andrew.check_andrew('You must be logged in to view invoices.', genre='email')
        self.assertFalse([f for f in requirements if f.category == 'andrew-confrontation'])

    def test_explicit_numeric_range_is_not_reported_as_false_range(self):
        findings, _ = lint.check('Revenue rose from 10 million to 20 million in two years.')
        self.assertFalse([f for f in findings if f.category == 'false-range'])

    def test_technical_vocabulary_and_range_cannot_fail_strict_scan(self):
        text = ('The report uses robust standard errors. Our leverage ratio rose '
                'from 10 percent to 20 percent because borrowing increased.')
        findings, _ = lint.check(text, strict=True)
        self.assertTrue(findings)
        self.assertTrue(all(f.severity == lint.WARNING for f in findings))
        self.assertEqual(lint.strict_exit(findings), 0)

    def test_typography_strict_and_override(self):
        text = 'The draft is ready — the contract remains unsigned.'
        default, _ = lint.check(text)
        self.assertTrue(all(f.severity == lint.WARNING for f in default))
        strict, _ = lint.check(text, strict=True)
        self.assertEqual(lint.strict_exit(strict), 1)
        override, _ = lint.check(text, strict=True, allow_em_dash=True)
        self.assertEqual(lint.strict_exit(override), 0)
        self.assertFalse(override)

    def test_profanity_convention_is_register_and_channel_specific(self):
        text = 'The fucking approval process failed.'
        business, _ = lint_andrew.check_andrew(text, genre='email', strict=True)
        natural, _ = lint_andrew.check_andrew(text, genre='reddit', formality='natural', strict=True)
        internal, _ = lint_andrew.check_andrew(text, genre='internal', strict=True)
        self.assertEqual(lint.strict_exit(business), 1)
        self.assertEqual(lint.strict_exit(natural), 0)
        self.assertFalse(internal)

    def test_short_and_micro_cadence_is_not_judged(self):
        text = 'Approved. Ship it. Thanks. I agree. You decide. Send it.'
        findings, cadence = lint.check(text, genre='email')
        self.assertEqual(cadence.status, 'insufficient_sample')
        self.assertFalse([f for f in findings if f.category in {'cadence', 'texture', 'fragment', 'anaphora'}])
        _, tweet = lint.check(text, genre='x')
        self.assertEqual(tweet.status, 'exempt')

    def test_sufficient_sample_cadence_is_still_advisory(self):
        text = ' '.join(['The approval process will require further legal review before the new contract can be sent to the customer.'] * 7)
        findings, cadence = lint.check(text, genre='email', strict=True)
        self.assertEqual(cadence.status, 'review')
        self.assertEqual(cadence.connector_cue_share, 1.0)
        self.assertTrue(all(f.severity == lint.WARNING for f in findings))
        self.assertEqual(lint.strict_exit(findings), 0)

    def test_connector_cues_do_not_pretend_to_parse_clauses(self):
        self.assertFalse(lint.has_connector_cue('I ordered copper, zinc and tin.'))
        self.assertTrue(lint.has_connector_cue('I will approve the order if the price stays below the agreed ceiling.'))
        text = ' '.join(['The customer approval process remains the primary constraint on the scheduled contract review and final signature date.'] * 7)
        findings, cadence = lint_andrew.check_andrew(text, genre='email')
        self.assertEqual(cadence.status, 'review')
        self.assertEqual(cadence.connector_cue_share, 0.0)
        self.assertTrue(any(f.category == 'texture' and 'connector cue' in f.rule for f in findings))
        self.assertIn('not a clause parser', cadence.method)

    def test_overlapping_phrase_reported_once(self):
        findings, _ = lint.check('First and foremost, the report is ready.')
        matching = [f for f in findings if f.offset_start == 0]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].rule_id, 'prose.banned-phrase')


class RedundantAcronymTests(unittest.TestCase):
    def candidates(self, text, **kwargs):
        findings, _ = lint.check(text, **kwargs)
        return [f for f in findings if f.rule_id == 'prose.redundant-acronym']

    def test_uppercase_acronyms_accept_noun_case_and_plural(self):
        for phrase in ['PIN number', 'PIN numbers', 'PIN Number', 'PIN NUMBERS',
                       'ATM machine', 'ATM machines', 'ATM Machine', 'ATM MACHINES']:
            with self.subTest(phrase=phrase):
                findings = self.candidates('Check the ' + phrase + '.')
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].snippet, phrase)

    def test_ordinary_case_standalone_acronyms_and_definitions_are_preserved(self):
        text = ('The pin number identifies a connector. Pin Number is the field label. '
                'The atm machine and Atm Machine are test labels. '
                'Enter your PIN beside the ATM. '
                'PIN (personal identification number) means personal identification number (PIN). '
                'ATM (automated teller machine) means automated teller machine (ATM). '
                'An automatic teller machine (ATM) is available. '
                'VIN number and GUI interface are outside this check.')
        self.assertFalse(self.candidates(text))

    def test_source_masks_do_not_create_acronym_candidates(self):
        text = ('> PIN number\n"ATM machine" and “PIN numbers”\n'
                '`ATM machines`\n```text\nPIN number\n```\n'
                'PIN contact@example.com number. ATM https://example.com machine. '
                'PIN `source` number. ATM "quoted source" machine.')
        self.assertFalse(self.candidates(text))

    def test_include_quotes_includes_quotations_but_keeps_code_excluded(self):
        text = ('"PIN number"\n> ATM machines\n`PIN number`\n'
                '```text\nATM machine\n```\n')
        self.assertFalse(self.candidates(text))
        findings = self.candidates(text, include_quotes=True)
        self.assertEqual([f.snippet for f in findings], ['PIN number', 'ATM machines'])
        self.assertEqual([f.line for f in findings], [1, 2])

    def test_strict_and_personalized_overlay_keep_unique_advisories(self):
        text = 'Use the PIN number at either ATM machine.'
        generic, _ = lint.check(text, strict=True)
        personalized, _ = lint_andrew.check_andrew(text, genre='email', strict=True)
        for findings in [generic, personalized]:
            candidates = [f for f in findings if f.rule_id == 'prose.redundant-acronym']
            self.assertEqual(len(candidates), 2)
            self.assertTrue(all(f.severity == lint.WARNING and not f.convention
                                and f.origin == 'heuristic' for f in candidates))
            self.assertEqual(lint.strict_exit(findings), 0)
        self.assertEqual([(f.rule_id, f.offset_start, f.offset_end) for f in generic],
                         [(f.rule_id, f.offset_start, f.offset_end) for f in personalized])

    def test_original_line_evidence_and_exact_offsets_survive_masking(self):
        text = ('"ATM machine"\r\n'
                'Café review: PIN\tNUMBERS; PIN number; PIN number.\r\n')
        findings = self.candidates(text)
        phrases = ['PIN\tNUMBERS', 'PIN number', 'PIN number']
        self.assertEqual(len(findings), len(phrases))
        previous_end = 0
        for finding, phrase in zip(findings, phrases):
            start = text.index(phrase, previous_end)
            self.assertEqual((finding.offset_start, finding.offset_end),
                             (start, start + len(phrase)))
            self.assertEqual(text[finding.offset_start:finding.offset_end], phrase)
            self.assertEqual(finding.snippet, phrase)
            self.assertEqual(finding.line, 2)
            self.assertEqual(finding.evidence, text.split('\n')[1])
            previous_end = finding.offset_end

    def test_compounds_and_partial_words_are_preserved(self):
        for text in ['ATM machine-learning', 'PIN number-one', 'ATM machine‑learning',
                     'PIN number‐one', 'SPIN number', 'XPIN number', 'ATM machineshop',
                     'PIN numbered', 'ATM machines2', 'PIN numbers_field', '_PIN number',
                     "ATM machine's", 'PIN number’s', 'ATM machinery']:
            with self.subTest(text=text):
                self.assertFalse(self.candidates(text))


class ClarityDerivedRuleTests(unittest.TestCase):
    """Rules adapted from Clarity's edit guide and the supplied tells catalog."""

    def categories(self, text, **kwargs):
        findings, _ = lint.check(text, **kwargs)
        return [f.category for f in findings]

    def test_vague_attribution_needs_a_named_source(self):
        self.assertIn('vague-attribution', self.categories('Studies show that founders sleep less.'))
        self.assertIn('vague-attribution', self.categories('Experts warn the market will cool.'))
        self.assertNotIn('vague-attribution',
                         self.categories("The 2025 Acme survey shows renewals took longer to close."))

    def test_importance_without_mechanism(self):
        self.assertIn('importance-claim', self.categories('This release is transformative for creators.'))
        self.assertNotIn('importance-claim', self.categories(
            'This release is important because payouts now settle in two days.'))
        self.assertNotIn('importance-claim', self.categories(
            'The effect was statistically significant in the pilot cohort.'))
        noted, _ = lint.check("It's important to note the export is late.")
        self.assertEqual([f.category for f in noted], ['banned-phrase'])

    def test_abstract_actor_but_not_measured_result(self):
        self.assertIn('abstract-actor', self.categories('The data tells us to slow down.'))
        self.assertIn('abstract-actor', self.categories('The market rewards speed.'))
        self.assertNotIn('abstract-actor', self.categories('The data shows a 12% drop in churn.'))

    def test_plain_word_suggests_an_alternative(self):
        findings, _ = lint.check('Send the deck prior to the call.')
        plain = [f for f in findings if f.category == 'plain-word']
        self.assertEqual(len(plain), 1)
        self.assertIn('before', plain[0].rule)

    def test_demonstrative_kicker_and_its_exceptions(self):
        text = ('Teams want to reuse the approval flow they already run for every vendor. '
                'That instinct backfires.')
        kicker = [f for f in lint.check(text)[0] if f.category == 'kicker']
        self.assertEqual(len(kicker), 1)
        self.assertEqual(kicker[0].snippet, 'That instinct backfires.')
        self.assertNotIn('kicker', self.categories(
            'Thanks for moving the review to Thursday afternoon. That works for me.'))
        self.assertNotIn('kicker', self.categories('This matters.'))

    def test_metaphor_flourish_and_false_balance(self):
        self.assertIn('flourish', self.categories(
            'It was an authorization bug wearing the costume of a performance fix.'))
        self.assertIn('false-balance', self.categories(
            'On one hand, the round is small. On the other hand, the terms are clean.'))
        self.assertNotIn('false-balance', self.categories('On the other hand, the terms are clean.'))

    def test_stock_vocab_names_a_plainer_choice(self):
        findings, _ = lint.check('We leverage the existing queue.')
        vocab = [f for f in findings if f.category == 'stock-vocab']
        self.assertEqual(len(vocab), 1)
        self.assertIn('plainer: use', vocab[0].rule)

    def test_earned_patterns_produce_no_findings(self):
        self.assertFalse(lint.check(
            'Before reopening traffic, verify the certificate, the DNS record, and the health check.')[0])
        self.assertFalse(lint.check(
            "At dusk, the blue pigment almost disappears. Step sideways and the silver ground "
            "catches the room's light, returning the river a piece at a time.")[0])

    def test_new_rules_never_affect_strict_exit(self):
        text = ('Studies show this is transformative. The data tells us to move. '
                'Prior to launch, That instinct backfires.')
        findings, _ = lint.check(text, strict=True)
        self.assertTrue(findings)
        self.assertEqual(lint.strict_exit(findings), 0)


class LocationTests(unittest.TestCase):
    def test_heading_patterns_do_not_swallow_the_previous_blank_line(self):
        text = 'Intro paragraph here.\n\n## Next Section Title Here\n\nBody paragraph here.'
        self.assertEqual(lint.split_paragraphs(text), ['Intro paragraph here.', 'Body paragraph here.'])
        findings, _ = lint.check(text)
        heading = [f for f in findings if f.category == 'formatting-header']
        self.assertEqual(heading[0].line, 3)
        self.assertEqual(heading[0].evidence, '## Next Section Title Here')

    def test_sentence_findings_point_at_their_sentence(self):
        intro = ('The pilot covered nine creator partnerships across two quarters, and the '
                 'payout ledger matched the bank statements every week of the test. ')
        text = intro * 5 + '\nIt broke. We fixed it. Then it broke. We gave up.'
        findings, _ = lint.check(text, genre='email')
        staccato = [f for f in findings if 'staccato' in f.rule]
        self.assertTrue(staccato)
        self.assertEqual(staccato[0].line, 2)
        self.assertTrue(staccato[0].evidence.startswith('It broke.'))
        documentwide = [f for f in findings if f.offset_start < 0]
        self.assertTrue(all(f.evidence == '(document-level measurement)' or f.snippet for f in documentwide))

    def test_document_level_findings_are_labelled_in_reports(self):
        text = ' '.join(['The approval process will require further legal review before the new contract can be sent to the customer.'] * 8)
        result = subprocess.run([sys.executable, str(SCRIPTS / 'lint.py'), '--genre', 'email'],
                                input=text, text=True, capture_output=True, check=False)
        self.assertIn('document: (document-level measurement)', result.stdout)


class CliTests(unittest.TestCase):
    def run_cli(self, script='lint.py', args=(), text='The report is ready.'):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                              input=text, text=True, capture_output=True, check=False)

    def test_alias_and_json_schema(self):
        result = self.run_cli(args=['--genre', 'x', '--json'], text='At its core, the report is ready.')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['genre'], 'tweet')
        self.assertEqual(data['schema_version'], 2)
        self.assertEqual(data['violations'], [])
        finding = data['findings'][0]
        self.assertTrue({'rule_id', 'severity', 'line', 'evidence', 'origin', 'convention'} <= finding.keys())
        self.assertEqual(finding['line'], 1)
        self.assertEqual(finding['evidence'], 'At its core, the report is ready.')

    def test_overlay_cli_parity_and_strict_exit(self):
        result = self.run_cli('lint_andrew.py', ['--genre', 'email', '--strict', '--json'],
                              'The draft is ready — review the contract.')
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertEqual(data['formality'], 'business')
        self.assertTrue(data['violations'])
        result = self.run_cli('lint_andrew.py', ['--genre', 'internal', '--json'])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_detect_is_findings_only_and_does_not_guess_authorship(self):
        result = self.run_cli(args=['--detect'], text='At its core, the report is ready.')
        self.assertEqual(result.returncode, 0)
        self.assertIn('Pattern candidate', result.stdout)
        self.assertIn('contextual review candidates', result.stdout)
        self.assertNotIn('machine output', result.stdout)
        self.assertNotIn('human prose', result.stdout)

    def test_acronym_detect_reports_contextual_hint_and_preserves_file_bytes(self):
        data = 'Café review\r\nUse the PIN number beside the ATM machines.\r\n'.encode('utf-8')
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'draft.txt'
            source.write_bytes(data)
            for script in ['lint.py', 'lint_andrew.py']:
                with self.subTest(script=script):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPTS / script), str(source), '--strict', '--detect'],
                        text=True, capture_output=True, check=False)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.count('[prose.redundant-acronym]'), 1)
                    self.assertIn('Use the PIN number beside the ATM machines.', result.stdout)
                    self.assertIn('Check the intended meaning', result.stdout)
                    self.assertIn('acronym alone or its full expansion', result.stdout)
                    self.assertEqual(source.read_bytes(), data)

    def test_usage_read_and_empty_errors(self):
        for args, text in [([], ''), (['--max-examples', '-1'], 'The report is ready.'),
                           (['/a/file/that/does/not/exist'], 'unused')]:
            with self.subTest(args=args):
                self.assertEqual(self.run_cli(args=args, text=text).returncode, 2)

    def test_file_bytes_and_specific_qualifiers_preserved(self):
        data = (b'Hi Dana,\r\n\r\nThe spread fell from 40% to 18%, but I still do not trust '
                b'the tail. Legal approval remains pending.\r\n\r\nBest,\r\nAndrew\r\n')
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'draft.txt'
            source.write_bytes(data)
            before = hashlib.sha256(data).hexdigest()
            for script in ['lint.py', 'lint_andrew.py']:
                result = subprocess.run([sys.executable, str(SCRIPTS / script), str(source), '--genre', 'email', '--json'],
                                        text=True, capture_output=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
                self.assertEqual(source.read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
