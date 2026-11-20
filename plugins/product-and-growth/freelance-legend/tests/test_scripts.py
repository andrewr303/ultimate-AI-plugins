"""Tests for the freelance-legend standard-library scripts.

Run from the plugin root:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import contact_scan  # noqa: E402
import vet_score  # noqa: E402
import pipeline  # noqa: E402
import price  # noqa: E402
import proposal_lint  # noqa: E402


def run(module, argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = module.main(argv)
    return code, buf.getvalue()


class PriceTests(unittest.TestCase):
    def test_estimate_doubles_and_prices(self):
        tasks = [price.parse_task("Spec:2:3"), price.parse_task("Build:10:12")]
        r = price.estimate(tasks, Decimal("50"), Decimal("2"), price.DEFAULT_FEES, Decimal("1500"), None)
        self.assertEqual(r["raw_likely_hours"], "15")
        self.assertEqual(r["planned_hours"], "30")
        self.assertEqual(r["price_at_rate"], "1500.00")
        self.assertEqual(r["net_after_fee"], {"10%": "1350.00", "15%": "1275.00"})
        self.assertEqual(r["budget"]["effective_rate_on_planned_hours"], "50.00")
        self.assertEqual(r["warnings"], [])

    def test_tight_budget_warns(self):
        r = price.estimate([price.parse_task("Build:20:30")], Decimal("50"), Decimal("2"),
                           price.DEFAULT_FEES, Decimal("1000"), None)
        self.assertTrue(any("rate floor" in w for w in r["warnings"]))

    def test_rate_below_floor_warns(self):
        r = price.estimate([price.parse_task("X:1:1")], Decimal("40"), Decimal("2"), price.DEFAULT_FEES, None, None)
        self.assertTrue(any("below" in w for w in r["warnings"]))

    def test_bad_task_rejected(self):
        with self.assertRaises(ValueError):
            price.parse_task("Build:12:10")
        with self.assertRaises(ValueError):
            price.parse_task("nohours")

    def test_milestones_sum_exactly(self):
        for total in ("2400", "1999", "6750", "333"):
            r = price.milestones(Decimal(total), [Decimal("15"), Decimal("35"), Decimal("50")], [7, 21, 35], None)
            self.assertTrue(r["sums_exactly"], total)
            self.assertEqual(Decimal(r["sum_check"]), Decimal(total))

    def test_milestone_first_share_warning(self):
        r = price.milestones(Decimal("1000"), [Decimal("50"), Decimal("50")], None, None)
        self.assertTrue(r["warnings"])

    def test_milestone_validation(self):
        with self.assertRaises(ValueError):
            price.milestones(Decimal("1000"), [Decimal("60"), Decimal("30")], None, None)
        with self.assertRaises(ValueError):
            price.milestones(Decimal("1000"), [Decimal("20"), Decimal("80")], [10, 5], None)

    def test_hourly_capacity_warning(self):
        r = price.hourly(Decimal("50"), (Decimal("20"), Decimal("30")), Decimal("4"), price.DEFAULT_FEES, Decimal("25"))
        self.assertEqual(r["weekly_billing"], "1000.00-1500.00")
        self.assertEqual(r["net_rate_after_fee"]["10%"], "45.00")
        self.assertTrue(any("capacity" in w for w in r["warnings"]))

    def test_gross_up_never_short(self):
        r = price.gross(Decimal("100"), Decimal("0.10"))
        self.assertEqual(r["gross"], "111.12")
        self.assertGreaterEqual(Decimal(r["net_at_gross"]), Decimal("100"))
        r = price.gross(Decimal("45"), Decimal("0.20"))
        self.assertEqual(r["gross"], "56.25")
        with self.assertRaises(ValueError):
            price.gross(Decimal("45"), Decimal("1"))

    def test_connects_ev(self):
        r = price.connects_ev(10, 4, Decimal("6000"), Decimal("0.10"), Decimal("0.05"))
        self.assertEqual(r["cost_usd"], "2.10")
        self.assertEqual(r["project_net"], "5400.00")
        self.assertEqual(r["expected_value_usd"], "267.90")
        self.assertEqual(r["break_even_win_probability"], "0.00039")

    def test_cli_json(self):
        code, out = run(price, ["--json", "milestones", "--total", "2000", "--split", "20,80"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["sums_exactly"])


class LintTests(unittest.TestCase):
    GOOD = ("Hi, an FP&A tool earns trust when its forecasts reconcile with the spreadsheet the finance team "
            "already uses, so I would start by tracing your current workflow and listing where the numbers "
            "come from before changing any screens.\n\nAndrew")

    def codes(self, text, **kw):
        findings, _ = proposal_lint.lint(text, kw.pop("kind", "cover-letter"), **kw)
        return {(f.level, f.code) for f in findings}

    def test_contact_details_are_errors(self):
        codes = self.codes("Reach me at someone@example.com or 720-555-0100 on WhatsApp.")
        self.assertIn(("ERROR", "contact-email"), codes)
        self.assertIn(("ERROR", "contact-phone"), codes)
        self.assertIn(("ERROR", "off-platform"), codes)

    def test_contact_review_when_contract_active(self):
        codes = self.codes("Email me at someone@example.com", kind="message", contract_active=True)
        self.assertIn(("REVIEW", "contact-email"), codes)
        self.assertNotIn(("ERROR", "contact-email"), codes)

    def test_off_marketplace_contact_is_info(self):
        codes = self.codes("Andrew, 123 Main St. Reply to someone@example.com", kind="outreach", off_marketplace=True)
        self.assertIn(("INFO", "contact-email"), codes)
        self.assertFalse([c for c in codes if c[0] == "ERROR"])

    def test_links_need_approval(self):
        text = "See github.com/example for the code."
        self.assertIn(("ERROR", "unapproved-link"), self.codes(text))
        self.assertNotIn(("ERROR", "unapproved-link"), self.codes(text, allow_links=["github.com/example"]))

    def test_i_led_opening_and_typography(self):
        codes = self.codes("I'm a full-stack developer — the perfect fit.")
        self.assertIn(("REVIEW", "opening"), codes)
        self.assertIn(("REVIEW", "typography"), codes)
        self.assertIn(("REVIEW", "claim"), codes)

    def test_client_instructions(self):
        self.assertIn(("ERROR", "client-instruction"), self.codes(self.GOOD, start_with="spreadsheet"))
        self.assertNotIn(("ERROR", "client-instruction"),
                         self.codes("Spreadsheet first. " + self.GOOD, start_with="spreadsheet"))
        self.assertIn(("ERROR", "client-instruction"), self.codes(self.GOOD, require=["Power BI"]))

    def test_placeholders_error_only_when_final(self):
        text = self.GOOD + " [[CONFIRM: weekly hours]]"
        self.assertIn(("INFO", "placeholder"), self.codes(text))
        self.assertIn(("ERROR", "placeholder"), self.codes(text, final=True))

    def test_clean_letter_has_no_errors(self):
        findings, stats = proposal_lint.lint(self.GOOD, "cover-letter")
        self.assertFalse([f for f in findings if f.level == "ERROR"])
        self.assertNotIn("opening", {f.code for f in findings})
        self.assertGreater(stats["words"], 30)

    def test_char_limit(self):
        self.assertIn(("ERROR", "length"), self.codes("word " * 1200))


class PipelineTests(unittest.TestCase):
    def test_normalize_variants_collapse(self):
        variants = [
            "~022118027855728317369",
            "https://www.upwork.com/nx/proposals/job/~022118027855728317369/apply/",
            "https://www.upwork.com/jobs/AI-FP-Tool_~022118027855728317369?source=email",
            "upwork-nx-proposals-job-022118027855728317369-apply",
            "2118027855728317369",
        ]
        keys = {pipeline.normalize(v) for v in variants}
        self.assertEqual(keys, {"upwork:2118027855728317369"})

    def test_other_platform_keys(self):
        self.assertEqual(pipeline.normalize("https://contra.com/opportunity/abc/?ref=x", "contra"),
                         "contra:contra.com/opportunity/abc")

    def test_ledger_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = str(Path(tmp) / "p.jsonl")
            seeds = Path(tmp) / "seeds.txt"
            seeds.write_text("2110433020008201453\n# comment\n2110676507972041447\n", encoding="utf-8")
            self.assertEqual(run(pipeline, ["--ledger", ledger, "seed", str(seeds)])[0], 0)
            self.assertEqual(run(pipeline, ["--ledger", ledger, "seen", "~012110433020008201453"])[0], 0)
            self.assertEqual(run(pipeline, ["--ledger", ledger, "seen", "~022118027855728317369"])[0], 1)
            for status in ("drafting", "submitted", "viewed", "interviewing"):
                extra = ["--connects", "10"] if status == "submitted" else []
                code, _ = run(pipeline, ["--ledger", ledger, "add", "~022118027855728317369",
                                         "--status", status, "--title", "AI FP&A Tool", *extra])
                self.assertEqual(code, 0)
            code, out = run(pipeline, ["--ledger", ledger, "stats", "--json"])
            stats = json.loads(out)
            self.assertEqual(stats["jobs"], 3)
            self.assertEqual(stats["funnel"]["submitted"], 1)
            self.assertEqual(stats["funnel"]["interviewing"], 1)
            self.assertEqual(stats["funnel"]["hired"], 0)
            self.assertEqual(stats["connects_recorded"], 10)

    def test_bad_status_and_disallowed_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = str(Path(tmp) / "p.jsonl")
            self.assertEqual(run(pipeline, ["--ledger", ledger, "add", "123", "--status", "won"])[0], 2)
            with self.assertRaises(ValueError):
                pipeline.append(Path(ledger), {"key": "x", "status": "seen", "email": "a@b.co"})


class VetScoreTests(unittest.TestCase):
    def test_anchors_hold_their_verdicts(self):
        anchors = json.loads((ROOT / "examples" / "vetting-anchors.json").read_text(encoding="utf-8"))["anchors"]
        for a in anchors:
            self.assertEqual(vet_score.score(a["job"])["verdict"], a["expected"], a["name"])

    def test_unknowns_are_listed_not_penalized_to_zero(self):
        r = vet_score.score({"fit": "strong", "payment_verified": True})
        self.assertIn("proposals", r["unknown"])
        self.assertIsNotNone(r["score"])

    def test_unrecognized_flag_is_surfaced(self):
        r = vet_score.score({"fit": "strong", "payment_verified": True, "red_flags": ["weird_request"]})
        self.assertEqual(r["unrecognized_flags"], ["weird_request"])


class ContactScanTests(unittest.TestCase):
    SAFE = """<html><body><h1>Andrew Rodriguez</h1><img src="/hero@2x.png">
    <a href="https://www.upwork.com/freelancers/~01abc">Continue on Upwork</a>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"Person","name":"Andrew",
    "url":"https://example.dev","knowsAbout":["Next.js","Financial modeling"]}</script></body></html>"""
    UNSAFE = """<html><body><a href="mailto:someone@example.com">Email</a> Call (720) 555-0100
    <form action="/api/contact"></form><a href="https://calendly.com/someone">Book</a>
    <a href="https://www.linkedin.com/in/someone">LinkedIn</a>
    <script type="application/ld+json">{"@type":"Person","name":"A","email":"someone@example.com"}</script>
    </body></html>"""

    def test_safe_build_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "index.html").write_text(self.SAFE, encoding="utf-8")
            self.assertEqual(contact_scan.scan(Path(tmp), ["upwork.com/freelancers/"]), [])
            self.assertEqual(run(contact_scan, [tmp, "--allow", "upwork.com/freelancers/"])[0], 0)

    def test_unsafe_build_flags_each_channel(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "contact").mkdir()
            Path(tmp, "contact", "index.html").write_text(self.UNSAFE, encoding="utf-8")
            kinds = {r["kind"] for r in contact_scan.scan(Path(tmp), [])}
            for kind in ("email", "mailto", "phone", "form", "booking", "social", "jsonld-contact"):
                self.assertIn(kind, kinds)
            self.assertEqual(run(contact_scan, [tmp])[0], 1)



def run_err(module, argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = module.main(argv)
    return code, out.getvalue(), err.getvalue()


class PriceRegressionTests(unittest.TestCase):
    def est(self, *extra):
        return run(price, ["estimate", "--task", "a:16:16", "--task", "b:16:16", "--rate", "50", *extra])

    def test_json_after_subcommand(self):  # S14
        code, out = run(price, ["estimate", "--task", "a:1:2", "--json"])
        self.assertEqual(code, 0)
        self.assertIn("price_at_rate", json.loads(out))

    def test_exact_fee_labels_no_collision(self):  # S12
        r = price.estimate([price.parse_task("a:1:2")], Decimal("50"), Decimal("2"),
                           price.parse_fees("0.105,0.10,0.125"), None, None)
        self.assertEqual(r["net_after_fee"], {"10.5%": "179.00", "10%": "180.00", "12.5%": "175.00"})
        h = price.hourly(Decimal("50"), (Decimal("10"), Decimal("10")), Decimal("1"),
                         price.parse_fees("0.125"), Decimal("25"))
        self.assertIn("12.5%", h["net_rate_after_fee"])

    def test_net_labelled_at_budget_and_bid(self):  # D3
        code, out = self.est("--budget-fixed", "1500", "--bid", "1400")
        self.assertEqual(code, 0)
        self.assertIn("Net of fee on the price $3200.00: 10%: $2880.00", out)
        self.assertIn("Net of fee at the client budget $1500.00: 10%: $1350.00", out)
        self.assertIn("Net of fee at the bid $1400.00: 10%: $1260.00", out)
        self.assertIn("Doubled price / budget: 2.13x", out)
        self.assertIn("net 10%: $42.19/h", out)  # D1: net-at-fee rate on raw hours shown

    def test_recommendation_rule(self):  # D7
        _, out = self.est("--budget-fixed", "1500")  # $46.88/h gross on raw hours >= floor
        self.assertIn("Recommendation: bid within budget with stated scope; note the doubled figure", out)
        _, out = self.est("--budget-fixed", "1000")  # $31.25/h raw, 3.2x
        self.assertIn("Recommendation: offer a narrower first phase or explain the full price", out)

    def test_tax_footer_on_every_subcommand(self):
        cmds = [["estimate", "--task", "a:1:2"], ["milestones", "--total", "1000", "--split", "20,80"],
                ["hourly", "--hours", "10-15", "--weeks", "2"], ["gross", "--net", "45", "--fee", "0.10"],
                ["connects-ev", "--connects", "10", "--project-gross", "1000"]]
        for cmd in cmds:
            code, out = run(price, cmd)
            self.assertEqual(code, 0, cmd)
            self.assertTrue(out.rstrip().endswith("Net figures are before income and self-employment tax."), cmd)

    def test_rejects_non_positive_inputs(self):  # S10
        for argv in (["milestones", "--total", "2400", "--split=-10,60,50"],
                     ["milestones", "--total", "2400", "--split", "0,50,50"],
                     ["milestones", "--total", "2400", "--split=20,-10,90"],
                     ["hourly", "--rate", "-50", "--hours", "15-20", "--weeks", "1"],
                     ["estimate", "--task", "a:1:2", "--rate", "0"],
                     ["estimate", "--task", "a:1:2", "--multiplier", "-2"],
                     ["estimate", "--task", "a:1:2", "--bid", "0"]):
            self.assertEqual(run_err(price, argv)[0], 2, argv)

    def test_milestone_percent_matches_rounded_amount(self):  # S13
        r = price.milestones(Decimal("1250"), [Decimal("15"), Decimal("45"), Decimal("40")], None, None)
        last = r["milestones"][-1]
        self.assertEqual(last["amount"], "499.00")
        self.assertEqual(last["percent"], "39.92")
        self.assertEqual(last["nominal_percent"], "40")
        code, out = run(price, ["milestones", "--total", "2000", "--split", "20,80"])
        self.assertIn("$400.00 (20%)", out)


class LintRegressionTests(unittest.TestCase):
    def find(self, text, **kw):
        findings, _ = proposal_lint.lint(text, kw.pop("kind", "message"), **kw)
        return findings

    def levels(self, text, **kw):
        return {(f.level, f.code, f.excerpt) for f in self.find(text, **kw)}

    def test_technology_words_are_not_errors(self):  # S3, D5
        text = ("I built a Discord bot, a Telegram alert bot, PayPal and crypto reconciliations, Socket.io, "
                "Next.js 14 with react@18.3.1, a LinkedIn scraper, Monday.com and timestamp 1730700000. "
                "Stack: Next.js, TypeScript, Supabase, MongoDB, Trigger.dev, and several LLM providers.")
        findings = self.find(text)
        self.assertEqual([f for f in findings if f.level == "ERROR"], [])
        excerpts = {f.excerpt for f in findings}
        self.assertNotIn("Socket.io", excerpts)
        self.assertNotIn("Trigger.dev", excerpts)
        self.assertIn(("REVIEW", "contact-phone", "1730700000"), self.levels(text))
        self.assertIn(("REVIEW", "unapproved-link", "Monday.com"), self.levels(text))
        self.assertIn(("REVIEW", "off-platform", "Discord"), self.levels(text))

    def test_call_tools_are_review(self):  # C11
        codes = self.levels("Happy to jump on a Zoom call, Microsoft Teams, FaceTime, or Signal here first.")
        for word in ("Zoom", "FaceTime", "Signal"):
            self.assertIn(("REVIEW", "off-platform", word), codes)
        self.assertTrue(any(c[2].endswith("Teams") and c[0] == "REVIEW" for c in codes))
        self.assertNotIn("ERROR", {c[0] for c in codes})

    def test_explicit_contact_phrases_are_errors(self):  # S3, S5
        for text in ("Text me tonight", "Shoot me a text", "message me on Insta", "add me on Discord",
                     "DM me", "Let's continue on Telegram", "you can pay me directly", "My handle is @andrewrod on X"):
            self.assertIn("ERROR", {f.level for f in self.find(text)}, text)

    def test_obfuscated_emails_and_international_phones(self):  # S5
        for text in ("andrew dot rodriguez at proton dot me", "andrew [at] outlook [dot] com",
                     "andrew(at)outlook.com", "Ping +44 20 7946 0958", "Call (720)555-1234."):
            errors = [f for f in self.find(text) if f.level == "ERROR" and f.code.startswith("contact-")]
            self.assertTrue(errors, text)
        self.assertIn(("REVIEW", "contact-phone", "555-1234"), self.levels("or 555-1234 works"))

    def test_links_with_scheme_or_path_are_errors(self):
        self.assertIn(("ERROR", "unapproved-link", "https://example.dev"), self.levels("See https://example.dev."))
        self.assertIn(("ERROR", "unapproved-link", "www.example.dev"), self.levels("See www.example.dev"))
        self.assertIn(("REVIEW", "unapproved-link", "example.dev"), self.levels("See example.dev"))

    def test_allow_link_is_host_plus_path_prefix(self):  # C12
        allow = ["safe.example.dev/work"]
        self.assertEqual(self.find("safe.example.dev/work/a and https://safe.example.dev/work", allow_links=allow), [])
        for bad in ("safe.example.dev/contact", "safe.example.dev/workshop", "evil.com/?x=safe.example.dev/work"):
            self.assertIn("ERROR", {f.level for f in self.find(bad, allow_links=allow)}, bad)

    def test_require_matches_whole_terms(self):  # S15
        miss = lambda text, term: any(f.code == "client-instruction" for f in self.find(text, require=[term]))
        self.assertTrue(miss("PostgreSQL work", "SQL"))
        self.assertFalse(miss("SQL and dbt", "sql"))
        self.assertFalse(miss("Modern C++ code", "C++"))
        self.assertFalse(miss("A .NET service", ".NET"))
        self.assertTrue(miss("bluetooth pairing", "blue"))

    def test_best_only_flags_claim_forms(self):  # D15
        claims = lambda text: [f for f in self.find(text) if f.code == "claim"]
        self.assertEqual(claims("Which works best for you? Whatever is best for you."), [])
        for text in ("I am the best developer", "best-in-class dashboards", "the best choice"):
            self.assertTrue(claims(text), text)


class PipelineRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = str(Path(self.tmp.name) / "p.jsonl")
        self.env = {k: os.environ.pop(k) for k in ("FREELANCE_LEGEND_HOME", "CLAUDE_PLUGIN_DATA",
                                                    "FREELANCE_LEGEND_LEDGER") if k in os.environ}

    def tearDown(self):
        for k in ("FREELANCE_LEGEND_HOME", "CLAUDE_PLUGIN_DATA", "FREELANCE_LEGEND_LEDGER"):
            os.environ.pop(k, None)
        os.environ.update(self.env)
        self.tmp.cleanup()

    def add(self, *argv):
        return run_err(pipeline, ["--ledger", self.ledger, "add", *argv])[0]

    def test_platform_inferred_from_host(self):  # S6
        cases = {
            "https://www.freelancer.com/projects/react/Build-App-123": "freelancer",
            "https://contra.com/opportunity/AbC": "contra",
            "https://news.ycombinator.com/item?id=1": "hn",
            "https://weworkremotely.com/remote-jobs/x": "wwr",
            "https://app.usebraintrust.com/jobs/1": "braintrust",
            "https://arc.dev/remote-jobs/x": "arc",
            "2118027855728317369": "upwork",
            "~022118027855728317369": "upwork",
        }
        for raw, plat in cases.items():
            self.assertEqual(pipeline.normalize(raw).split(":", 1)[0], plat, raw)
        self.assertEqual(pipeline.normalize("https://www.freelancer.com/projects/react/Build-App-123"),
                         "freelancer:freelancer.com/projects/react/build-app-123")
        self.assertTrue(pipeline.normalize("https://example.com/job/1", "contra").startswith("contra:"))

    def test_connects_and_boost_summed_per_event(self):  # S7
        self.assertEqual(self.add("~022118027855728317369", "--status", "submitted", "--connects", "10",
                                  "--boost", "4"), 0)
        self.assertEqual(self.add("~022118027855728317369", "--status", "viewed", "--connects", "0"), 0)
        stats = json.loads(run(pipeline, ["stats", "--json", "--ledger", self.ledger])[1])
        self.assertEqual(stats["connects_recorded"], 10)
        self.assertEqual(stats["boost_recorded"], 4)
        with self.assertRaises(SystemExit):  # --boost is an int now
            run_err(pipeline, ["--ledger", self.ledger, "add", "X", "--status", "seen", "--boost", "four"])

    def test_free_text_contact_details_refused(self):  # S8
        for field in ("--title", "--reason", "--angle", "--url", "--invoice"):
            for value in ("x person@example.com", "call 720-555-1234", "+44 20 7946 0958"):
                self.assertEqual(self.add("123", "--status", "seen", field, value), 2, (field, value))
        self.assertFalse(Path(self.ledger).exists())
        self.assertEqual(self.add("https://www.upwork.com/jobs/~022118027855728317369", "--status", "seen",
                                  "--url", "https://www.upwork.com/jobs/~022118027855728317369"), 0)

    def test_invoices_and_overdue(self):  # K8, C14
        self.assertEqual(self.add("A1", "--status", "invoiced", "--amount", "1200", "--due", "2026-10-01",
                                  "--invoice", "INV-7", "--fee", "0.10", "--met-on", "2026-01-15"), 0)
        self.assertEqual(self.add("B2", "--status", "invoiced", "--amount", "500", "--due", "2026-10-01",
                                  "--invoice", "INV-8"), 0)
        self.assertEqual(self.add("B2", "--status", "paid"), 0)
        self.assertEqual(self.add("C3", "--status", "invoiced", "--due", "2026-12-01", "--invoice", "INV-9"), 0)
        self.assertEqual(self.add("D4", "--status", "invoiced", "--due", "10/01/2026"), 2)
        stats = json.loads(run(pipeline, ["--ledger", self.ledger, "--json", "stats", "--today", "2026-11-04"])[1])
        self.assertEqual([o["invoice"] for o in stats["overdue_invoices"]], ["INV-7"])
        self.assertEqual(stats["overdue_invoices"][0]["days_overdue"], 34)
        row = json.loads(run(pipeline, ["--ledger", self.ledger, "list", "--json", "--status", "invoiced"])[1])
        a1 = [r for r in row if r["key"] == "upwork:a1"][0]
        self.assertEqual((a1["amount"], a1["fee"], a1["met_on"]), (1200.0, 0.1, "2026-01-15"))
        _, out = run(pipeline, ["--ledger", self.ledger, "stats", "--today", "2026-11-04"])
        self.assertIn("OVERDUE: upwork:a1 invoice INV-7 $1200.00 due 2026-10-01", out)

    def test_default_ledger_in_user_data_dir(self):  # K1
        home = Path(self.tmp.name) / "home"
        os.environ["CLAUDE_PLUGIN_DATA"] = str(Path(self.tmp.name) / "plugin-data")
        self.assertEqual(pipeline.ledger_path(None), Path(self.tmp.name) / "plugin-data" / "pipeline.jsonl")
        os.environ["FREELANCE_LEGEND_HOME"] = str(home)
        self.assertEqual(pipeline.ledger_path(None), home / "pipeline.jsonl")
        os.environ["FREELANCE_LEGEND_LEDGER"] = str(Path(self.tmp.name) / "env.jsonl")
        self.assertEqual(pipeline.ledger_path(None), Path(self.tmp.name) / "env.jsonl")
        self.assertEqual(pipeline.ledger_path("x.jsonl"), Path("x.jsonl"))
        os.environ.pop("FREELANCE_LEGEND_LEDGER")
        os.environ.pop("FREELANCE_LEGEND_HOME")
        os.environ.pop("CLAUDE_PLUGIN_DATA")
        self.assertEqual(pipeline.ledger_path(None), Path.home() / ".freelance-legend" / "pipeline.jsonl")

    def test_init_copies_template_and_prints_paths(self):  # K1
        home = Path(self.tmp.name) / "home"
        os.environ["FREELANCE_LEGEND_HOME"] = str(home)
        code, out = run(pipeline, ["init"])
        self.assertEqual(code, 0)
        proof = home / "approved-proof.md"
        self.assertEqual(proof.read_text(encoding="utf-8"),
                         (ROOT / "references" / "approved-proof.md").read_text(encoding="utf-8"))
        self.assertIn(str((home / "pipeline.jsonl").resolve()), out)
        self.assertIn(str(proof.resolve()), out)
        proof.write_text("edited", encoding="utf-8")
        run(pipeline, ["init"])
        self.assertEqual(proof.read_text(encoding="utf-8"), "edited")  # never overwritten

    def test_seed_and_stats_print_absolute_ledger(self):  # K1
        seeds = Path(self.tmp.name) / "s.txt"
        seeds.write_text("2110433020008201453\n", encoding="utf-8")
        abs_path = str(Path(self.ledger).resolve())
        self.assertIn(abs_path, run(pipeline, ["seed", str(seeds), "--ledger", self.ledger])[1])
        self.assertIn(abs_path, run(pipeline, ["stats", "--ledger", self.ledger])[1])

    def test_run_markers(self):  # K10
        self.assertEqual(run(pipeline, ["last-run", "--ledger", self.ledger])[0], 1)
        run(pipeline, ["--ledger", self.ledger, "run-start", "--at", "2026-11-04T10:00:00Z"])
        self.assertEqual(run(pipeline, ["--ledger", self.ledger, "last-run"])[0], 1)
        run(pipeline, ["run-done", "--ledger", self.ledger, "--at", "2026-11-04T10:05:00Z", "--note", "3 new"])
        code, out = run(pipeline, ["last-run", "--ledger", self.ledger])
        self.assertEqual((code, out.strip()), (0, "2026-11-04T10:05:00Z"))
        self.assertTrue((Path(self.tmp.name) / "runs.jsonl").exists())

    def test_ledger_flag_after_subcommand(self):  # S14
        self.assertEqual(run(pipeline, ["add", "X", "--status", "seen", "--ledger", self.ledger])[0], 0)
        self.assertTrue(Path(self.ledger).exists())
        self.assertEqual(json.loads(run(pipeline, ["list", "--ledger", self.ledger, "--json"])[1])[0]["key"],
                         "upwork:x")


class VetRegressionTests(unittest.TestCase):
    STRONG = {"fit": "strong", "budget_type": "hourly", "budget_low": 25, "budget_high": 50,
              "payment_verified": True, "client_spend": 15000, "hires": 6, "hire_rate": 0.6, "rating": 4.9,
              "proposals_low": 5, "posted_hours_ago": 1}

    def test_flags_normalized_and_synonyms(self):  # S2, D2
        for flags in (["off-platform-contact"], ["Telegram"], ["off platform contact"], ["buy laptop"],
                      ["PayPal"], ["free-test"], ["Crypto"], ["overpayment"]):
            self.assertEqual(vet_score.score({**self.STRONG, "red_flags": flags})["verdict"], "Report", flags)
        self.assertEqual(vet_score.normalize_flag("Move-Off Platform"), "off_platform_contact")

    def test_unrecognized_flag_caps_at_hold(self):  # S2, D2
        r = vet_score.score({**self.STRONG, "red_flags": ["equipment"]})
        self.assertEqual(r["verdict"], "Hold")
        self.assertIn("unrecognized red flag: judge by hand", r["reasons"])
        self.assertEqual(r["unrecognized_flags"], ["equipment"])
        r = vet_score.score({"red_flags": ["weird"]})  # panel-missing Hold path also lists it
        self.assertEqual((r["verdict"], r["unrecognized_flags"]), ("Hold", ["weird"]))
        r = vet_score.score({**self.STRONG, "already_hired": True, "red_flags": ["weird"]})
        self.assertEqual((r["verdict"], r["unrecognized_flags"]), ("Skip", ["weird"]))

    def test_bad_input_exits_2(self):  # S2, S11
        with tempfile.TemporaryDirectory() as tmp:
            for i, payload in enumerate(('{"red_flags": "unpaid_test"}', "[1]", '{"budget_fixed": "1,500"}',
                                         '{"hire_rate": true}', '{"red_flags": [1]}')):
                path = Path(tmp, f"{i}.json")
                path.write_text(payload, encoding="utf-8")
                code, _, err = run_err(vet_score, [str(path)])
                self.assertEqual(code, 2, payload)
                self.assertIn("error:", err)

    def test_hire_rate_percent(self):  # S11
        as_pct = vet_score.score({**self.STRONG, "hire_rate": 15})
        as_frac = vet_score.score({**self.STRONG, "hire_rate": 0.15})
        self.assertEqual(as_pct["score"], as_frac["score"])
        self.assertLess(as_pct["score"], vet_score.score(self.STRONG)["score"])

    def test_list_flags(self):
        code, out = run(vet_score, ["--list-flags"])
        self.assertEqual(code, 0)
        for key in vet_score.HARD_FLAGS:
            self.assertIn(key, out)
        self.assertIn("telegram", out)

    def test_net_rate_shown_with_gross_floor(self):  # D1
        r = vet_score.score(self.STRONG)
        self.assertEqual(r["effective_rate_net"], {"10%": 45.0, "15%": 42.5})
        self.assertEqual(r["rate_floor_gross"], 45.0)


class ContactScanRegressionTests(unittest.TestCase):
    def scan(self, files, allow=()):
        with tempfile.TemporaryDirectory() as tmp:
            for name, body in files.items():
                Path(tmp, name).write_text(body, encoding="utf-8")
            return contact_scan.scan(Path(tmp), list(allow))

    def test_allow_applies_to_token_not_context(self):  # S1
        page = ('<a href="https://upwork.com/freelancers/~01a">Hire</a> person@example.com 720-555-1234 '
                'calendly.com/andrew')
        kinds = {r["kind"] for r in self.scan({"c.html": page}, ["upwork.com/freelancers/"])}
        self.assertEqual(kinds, {"email", "phone", "booking"})
        self.assertEqual(self.scan({"c.html": '<a href="https://upwork.com/freelancers/~01a">Hire</a>'},
                                   ["upwork.com/freelancers/"]), [])

    def test_missed_formats_now_caught(self):  # S4
        for line in ("Call 720-555-1234.", "(720)555-1234", "+44 20 7946 0958", "andrew&#64;rodriguez.dev",
                     "andrew [at] gmail [dot] com", "andrew at gmail dot com"):
            self.assertTrue(self.scan({"p.html": f"<p>{line}</p>"}), line)

    def test_vcf_and_pdf_reported(self):  # S4
        found = self.scan({"index.html": "<p>hi</p>", "andrew.vcf": "BEGIN:VCARD", "resume.pdf": "%PDF"})
        self.assertEqual(sorted((Path(r["file"]).name, r["kind"]) for r in found),
                         [("andrew.vcf", "file-review"), ("resume.pdf", "file-review")])


if __name__ == "__main__":
    unittest.main()
