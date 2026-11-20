import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contact_rules import (  # noqa: E402
    RFC2142_ROLES,
    RULES,
    classify,
    decode,
    extract,
    is_roster_page,
    registrable_domain,
)

SITE = "tessaquill.com"


class ExtractTests(unittest.TestCase):
    def test_literal_escape_sequences_do_not_glue_to_the_local_part(self):
        # A JSON-style dump writes a tab or newline as backslash plus a letter, and that
        # letter is a word character, so it would stick to the next name.
        cases = {
            "tab": r"Rates and availability:\tOlu.Adeyemi@adeyemi-studio.net",
            "carriage return": r"Studio line\rOlu.Adeyemi@adeyemi-studio.net",
            "newline": r"Talk to me about shoots\nOlu.Adeyemi@adeyemi-studio.net",
        }
        for label, raw in cases.items():
            with self.subTest(label):
                self.assertEqual(extract(raw), ["olu.adeyemi@adeyemi-studio.net"])

    def test_html_entities_and_unicode_escapes_are_decoded_first(self):
        self.assertEqual(extract("hello&#64;tessaquill.com"), ["hello@tessaquill.com"])
        self.assertEqual(extract(r"tessa@tessaquill.com"), ["tessa@tessaquill.com"])

    def test_trailing_punctuation_is_stripped(self):
        self.assertEqual(extract("mail tessa@tessaquill.com."), ["tessa@tessaquill.com"])
        self.assertEqual(extract("(tessa@tessaquill.com)"), ["tessa@tessaquill.com"])

    def test_duplicates_collapse_and_case_is_folded(self):
        self.assertEqual(extract("Tessa@tessaquill.com, tessa@TessaQuill.com"), ["tessa@tessaquill.com"])

    def test_decode_leaves_plain_text_alone(self):
        self.assertEqual(decode("plain"), "plain")


class ClassifyTests(unittest.TestCase):
    def test_asset_filenames_are_not_emails(self):
        self.assertEqual(classify("banner@3x.png", SITE).kind, "reject_junk")
        self.assertEqual(classify("sprite@bundle.css", SITE).kind, "reject_junk")

    def test_placeholders_rejected(self):
        self.assertEqual(classify("you@example.org").kind, "reject_placeholder")
        self.assertEqual(classify("tessa@yourcompany.com", SITE).kind, "reject_placeholder")
        self.assertEqual(classify("tessa@mail.test", SITE).kind, "reject_placeholder")

    def test_role_inboxes_rejected_even_with_plus_tag_or_digits(self):
        for address in (f"info@{SITE}", f"support+vip@{SITE}", f"sales7@{SITE}", f"customer-service@{SITE}"):
            self.assertEqual(classify(address, SITE).kind, "reject_role", address)

    def test_every_rfc2142_role_is_refused(self):
        for local in sorted(RFC2142_ROLES | {"abuse", "security"}):
            self.assertFalse(classify(f"{local}@{SITE}", SITE).keep, local)

    def test_legal_and_purpose_bound_rejected(self):
        self.assertEqual(classify(f"legal@{SITE}", SITE).kind, "reject_legal")
        self.assertEqual(classify(f"dpo-uk@{SITE}", SITE).kind, "reject_legal")
        self.assertEqual(classify(f"abuse@{SITE}", SITE).kind, "reject_purpose_bound")
        self.assertEqual(classify(f"do-not-reply@{SITE}", SITE).kind, "reject_purpose_bound")

    def test_deal_inbox_kept_only_on_creators_own_domain(self):
        kept = classify(f"collabs@{SITE}", f"www.{SITE}", page="sponsor")
        self.assertTrue(kept.keep)
        self.assertEqual(kept.kind, "business_inbox")
        other = classify("collabs@northbridge-agency.com", SITE, page="contact")
        self.assertFalse(other.keep)
        self.assertEqual(other.kind, "reject_role")

    def test_deal_inbox_needs_a_site_to_compare_against(self):
        self.assertFalse(classify(f"business@{SITE}", None).keep)

    def test_generic_inbox_on_own_domain_is_still_rejected(self):
        self.assertFalse(classify(f"info@{SITE}", SITE, page="sponsor").keep)

    def test_personal_address_on_contact_page_kept(self):
        verdict = classify(f"tessa@{SITE}", SITE, page="contact")
        self.assertTrue(verdict.keep)
        self.assertEqual(verdict.kind, "personal")

    def test_legal_page_and_roster_page_are_incidental(self):
        self.assertFalse(classify(f"tessa@{SITE}", SITE, page="legal").keep)
        self.assertFalse(classify(f"tessa@{SITE}", SITE, page="roster").keep)

    def test_address_repeated_across_three_pages_is_a_footer_entry(self):
        verdict = classify(f"tessa@{SITE}", SITE, page="homepage", pages_seen_on=3)
        self.assertFalse(verdict.keep)
        self.assertEqual(verdict.kind, "reject_footer")

    def test_platform_domain_address_rejected(self):
        verdict = classify("tessa@ghost.io", SITE, platform_domains=frozenset({"ghost.io"}))
        self.assertEqual(verdict.kind, "reject_platform")

    def test_free_mail_provider_is_a_valid_personal_address(self):
        self.assertTrue(classify("tessa.quill@gmail.com", SITE, page="bio").keep)

    def test_malformed_address_is_junk(self):
        self.assertEqual(classify("@tessaquill.com", SITE).kind, "reject_junk")
        self.assertEqual(classify("tessa@localhost", SITE).kind, "reject_junk")

    def test_rule_table_ends_with_a_catch_all(self):
        self.assertTrue(RULES[-1][0](None))
        self.assertEqual(RULES[-1][1], "personal")


class RosterTests(unittest.TestCase):
    def test_five_distinct_registered_domains_is_a_roster(self):
        addresses = [f"x@studio{i}.net" for i in range(5)]
        self.assertTrue(is_roster_page(addresses))

    def test_four_domains_is_not_a_roster(self):
        self.assertFalse(is_roster_page([f"x@studio{i}.net" for i in range(4)]))

    def test_many_addresses_on_one_domain_is_not_a_roster(self):
        self.assertFalse(is_roster_page([f"writer{i}@tessaquill.com" for i in range(9)]))


class DomainTests(unittest.TestCase):
    def test_registrable_domain_handles_country_second_level_labels(self):
        self.assertEqual(registrable_domain("tessa@mail.tessaquill.co.uk"), "tessaquill.co.uk")
        self.assertEqual(registrable_domain("blog.tessaquill.com.au"), "tessaquill.com.au")
        self.assertEqual(registrable_domain("www.tessaquill.com"), "tessaquill.com")

    def test_two_letter_tld_without_a_generic_label_keeps_two_labels(self):
        self.assertEqual(registrable_domain("www.tessaquill.io"), "tessaquill.io")

    def test_unusable_hosts_return_none(self):
        self.assertIsNone(registrable_domain("localhost"))
        self.assertIsNone(registrable_domain("a..b.com"))


class IterableArgumentTests(unittest.TestCase):
    def test_generator_platform_domains_is_not_consumed_by_validation(self):
        verdict = classify("jane@youtube.com", SITE, platform_domains=(d for d in ["youtube.com"]))
        self.assertEqual(verdict.kind, "reject_platform")

    def test_generator_addresses_is_not_consumed_by_validation(self):
        self.assertTrue(is_roster_page((a for a in ["a@one.com", "b@two.com"]), 2))

    def test_non_iterable_arguments_raise_type_error(self):
        with self.assertRaises(TypeError):
            classify("jane@janedoe.com", SITE, platform_domains=5)
        with self.assertRaises(TypeError):
            is_roster_page(5)

    def test_huge_integer_count_raises_value_error(self):
        with self.assertRaises(ValueError):
            classify("jane@janedoe.com", SITE, pages_seen_on=10**400)


class LinearTimeTests(unittest.TestCase):
    """Adversarial page text must not make extract() slow: every quantifier is bounded."""

    INPUTS = {
        "a% run": lambda n: "a%" * (n // 2),
        "a. run": lambda n: "a." * (n // 2),
        "@ run": lambda n: "@" * n,
        "_ run": lambda n: "_" * n,
        "a@ run": lambda n: "a@" * (n // 2),
        "label run after @": lambda n: "x@" + "a." * (n // 2),
    }

    def test_200k_adversarial_inputs_finish_well_under_a_second(self):
        import time
        for label, make in self.INPUTS.items():
            text = make(200_000)
            start = time.perf_counter()
            extract(text)
            elapsed = time.perf_counter() - start
            with self.subTest(label=label):
                self.assertLess(elapsed, 1.0, f"{label}: {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main()
