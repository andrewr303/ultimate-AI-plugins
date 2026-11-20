"""WP11 CLI tests: the section 4.6 surface, end-to-end audits, formats, gates, exit codes, safety refusals,
generated rule catalog, examples, doctor, robots templates and live commands with fakes (no sockets)."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import runpy
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_cli
import helpers  # noqa: E402
from helpers import FIXTURES, NOW, PLUGIN_ROOT  # noqa: E402
from seo_geo_lib import cli, ledger, robots, rulesdb  # noqa: E402

_CWD: List[str] = []


def setUpModule() -> None:
    helpers.block_network()
    _CWD.append(os.getcwd())
    os.chdir(str(PLUGIN_ROOT))   # finding paths and examples are relative to the plugin root


def tearDownModule() -> None:
    os.chdir(_CWD.pop())


TOP_COMMANDS = {"stack", "audit-build", "audit-page", "audit-url", "access-check", "robots", "jsonld", "sitemap",
                "hreflang", "links", "redirects", "perf", "llms-txt", "indexnow", "citability", "content-lint",
                "sections", "fidelity", "drift", "ledger", "gsc", "referrers", "gaps", "project", "updates",
                "crawlers", "rules", "doctor"}
LEAVES = sorted(
    (TOP_COMMANDS - {"llms-txt", "sections", "drift", "ledger", "gsc", "gaps", "project"})
    | {"llms-txt validate", "llms-txt draft", "sections list", "sections show", "sections replace",
       "drift snapshot", "drift compare", "drift findings", "ledger init", "ledger record", "ledger summary",
       "ledger status", "gaps plan", "project validate"}
    | {"gsc " + s for s in ("movers", "decay", "ctr", "striking", "cannibalization", "brand", "buckets",
                            "aio-recovery")})
GLOBAL_FLAGS = {"--format", "--output", "--force", "--fail-on", "--scores", "--now", "--today", "--quiet"}
GOOD = "tests/fixtures/site-good"
BAD = "tests/fixtures/site-bad"
BASE = ["--base-url", "https://example.com"]
EXAMPLE_ARGS = ["audit-build", BAD, "--base-url", "https://example.com", "--scores", "both", "--now", NOW]
CAT = rulesdb.RuleCatalog.load()


def run(*argv: str, env: Optional[Dict[str, str]] = None, stdin: Optional[str] = None) -> Tuple[int, str, str]:
    """run_cli with --now pinned unless the test passes its own."""
    args = list(argv)
    if "--now" not in args and not (env and "SEO_GEO_GOD_NOW" in env) and args and args[0] not in ("--help",
                                                                                                 "--version"):
        args += ["--now", NOW]
    return helpers.run_cli(args, env=env, stdin=stdin)


def run_json(*argv: str, code: int = 0, **kw: Any) -> Dict[str, Any]:
    rc, out, err = run(*argv, **kw)
    if rc != code:
        raise AssertionError("exit %d (expected %d) for %r\nstderr: %s\nstdout: %s" % (rc, code, argv, err, out[:2000]))
    return json.loads(out)


def rules_of(env: Dict[str, Any]) -> List[str]:
    return helpers.rule_ids(env["findings"])


@contextlib.contextmanager
def no_network() -> Iterator[None]:
    """Assert that the block does not even attempt a socket call."""
    before = len(helpers.network_attempts())
    yield
    attempts = helpers.network_attempts()[before:]
    if attempts:
        helpers.reset_network_attempts(before)
        raise AssertionError("network attempted: %r" % attempts)


@contextlib.contextmanager
def live_fakes(routes: Dict[str, Any], *, hosts: Optional[Dict[str, List[str]]] = None,
               default: Any = (404, {"content-type": "text/html"}, b"<html><body>Not found</body></html>")
               ) -> Iterator[Tuple[helpers.FakeTransport, helpers.FakeClock]]:
    transport = helpers.FakeTransport(routes, default=default)
    clock = helpers.FakeClock()
    resolver = helpers.FakeResolver(hosts or {"example.com": ["93.184.215.14"]})
    with mock.patch.dict(cli.HOOKS, {"transport": transport, "resolver": resolver, "sleep": clock.sleep,
                                     "clock": clock}), no_network():
        yield transport, clock


def html(title: str, body: str, *, head: str = "", canonical: Optional[str] = None) -> bytes:
    canon = '<link rel="canonical" href="%s">' % canonical if canonical else ""
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title>'
            '<meta name="viewport" content="width=device-width, initial-scale=1">%s%s</head><body>%s</body></html>'
            % (title, canon, head, body)).encode("utf-8")


# ----------------------------------------------------------------------------- parser surface

class ParserTests(unittest.TestCase):
    def test_help_lists_exactly_the_section_4_6_commands(self) -> None:
        code, out, _ = run("--help")
        self.assertEqual(code, 0)
        listed = set(re.findall(r"^    ([a-z][a-z-]*)(?=\s)", out, re.M))
        self.assertEqual(listed, TOP_COMMANDS)

    def test_command_names_are_the_sorted_leaf_commands(self) -> None:
        self.assertEqual(cli.command_names(), LEAVES)
        self.assertEqual({n.split()[0] for n in cli.command_names()}, TOP_COMMANDS)

    def test_group_help_lists_subcommands(self) -> None:
        for group, subs in (("llms-txt", {"validate", "draft"}), ("sections", {"list", "show", "replace"}),
                            ("drift", {"snapshot", "compare", "findings"}),
                            ("ledger", {"init", "record", "summary", "status"}), ("gaps", {"plan"}),
                            ("project", {"validate"})):
            with self.subTest(group=group):
                code, out, _ = helpers.run_cli([group, "--help"])
                self.assertEqual(code, 0)
                self.assertEqual(set(re.findall(r"^    ([a-z][a-z-]*)(?=\s)", out, re.M)), subs)

    def test_every_leaf_accepts_the_global_options(self) -> None:
        parser = cli.build_parser()

        def leaves(p: Any, prefix: str = "") -> Iterator[Tuple[str, Any]]:
            for action in p._actions:
                if action.__class__.__name__ == "_SubParsersAction":
                    for name, child in action.choices.items():
                        full = (prefix + " " + name).strip()
                        if any(a.__class__.__name__ == "_SubParsersAction" for a in child._actions):
                            yield from leaves(child, full)
                        else:
                            yield full, child

        seen = 0
        for name, child in leaves(parser):
            flags = {s for a in child._actions for s in a.option_strings}
            self.assertTrue(GLOBAL_FLAGS <= flags, (name, GLOBAL_FLAGS - flags))
            seen += 1
        self.assertEqual(seen, len(LEAVES))

    def test_section_4_6_flags_exist(self) -> None:
        cases = {
            "audit-build": ["x", "--base-url", "https://example.com", "--url-style", "clean", "--expect-indexable",
                            "--profile", "launch", "--max-pages", "5", "--max-file-bytes", "100"],
            "audit-url": ["https://example.com", "--live", "--max-pages", "3", "--delay", "0", "--allow-local",
                          "localhost:3000", "--ignore-robots", "--via-proxy", "--expect-indexable", "--profile", "geo"],
            "robots": ["--url", "https://example.com", "--live", "--bots", "training", "--path", "/", "--path", "/a"],
            "llms-txt": ["draft", "d", "--base-url", "https://example.com", "--title", "T", "--summary", "S",
                         "--optional-prefix", "/x/"],
            "indexnow": ["--build-dir", "d", "--base-url", "https://example.com", "--key-file", "k",
                         "--key-location", "https://example.com/k.txt"],
            "gsc": ["ctr", "c.csv", "--dimensions", "query,page", "--calibrate", "--brand-terms", "a", "b"],
            "ledger": ["summary", "d", "--by", "surface", "--window", "2026-11-01:2026-11-30"],
        }
        parser = cli.build_parser()
        for cmd, rest in cases.items():
            with self.subTest(cmd=cmd):
                args = parser.parse_args([cmd] + rest)
                self.assertTrue(callable(args.handler))

    def test_usage_errors_exit_2(self) -> None:
        for argv in ([], ["no-such-command"], ["hreflang", GOOD], ["llms-txt"], ["llms-txt", "draft", GOOD],
                     ["gaps", "plan", "t.csv"], ["audit-build"], ["audit-build", GOOD, "--profile", "nope"],
                     ["audit-build", GOOD, "--format", "pdf"], ["audit-build", GOOD, "--max-pages", "x"]):
            with self.subTest(argv=argv):
                code, _, err = helpers.run_cli(argv)
                self.assertEqual(code, 2)
                self.assertIn("usage", err.lower())

    def test_input_errors_exit_2_with_error_envelope(self) -> None:
        cases = [["audit-build", "tests/fixtures/no-such-dir"], ["audit-page", "tests/fixtures/missing.html"],
                 ["audit-build", GOOD, "--now", "yesterday"], ["audit-build", GOOD, "--today", "2026-13-01"],
                 ["perf"], ["perf", "--crux", "tests/fixtures/content/guide.md"],
                 ["drift", "findings", "tests/fixtures/content/guide.md", "tests/fixtures/content/guide.md"],
                 ["rules", "--category", "nope"], ["doctor", "--scores", "seo"],
                 ["gsc", "movers", "tests/fixtures/analytics/gsc/queries-cur.csv"],
                 ["gsc", "brand", "tests/fixtures/analytics/gsc/queries-cur.csv"],
                 ["citability", "tests/fixtures/content/guide.md", "--top", "0"]]
        for argv in cases:
            with self.subTest(argv=argv):
                code, out, err = helpers.run_cli(argv + ([] if "--now" in argv else ["--now", NOW]))
                self.assertEqual(code, 2, err)
                env = json.loads(out)
                self.assertTrue(env["error"])
                self.assertEqual(env["tool"], "seo-geo-god")
                self.assertIn("error:", err)

    def test_version_and_internal_error(self) -> None:
        code, out, _ = helpers.run_cli(["--version"])
        self.assertEqual((code, out.strip()), (0, "seo-geo-god 1.0.1"))
        with mock.patch.object(cli, "cmd_doctor", side_effect=RuntimeError("boom")):
            code, out, err = run("doctor")
        self.assertEqual(code, 4)
        self.assertIn("internal error: RuntimeError: boom", json.loads(out)["error"])
        self.assertIn("internal error", err)


# ----------------------------------------------------------------------------- audit-build end to end

class AuditBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bad = run_json("audit-build", BAD, *BASE)
        cls.expected = json.loads(helpers.read_fixture("site-bad", "EXPECTED_RULES.json"))
        opts = cls.expected["options"]
        cls.bad_launch = run_json("audit-build", BAD, "--base-url", opts["base_url"], "--url-style", opts["url_style"],
                                  "--expect-indexable", "--profile", opts["profile"], "--today", opts["today"])

    def test_site_good_has_no_errors_or_warnings(self) -> None:
        env = run_json("audit-build", GOOD, *BASE, "--expect-indexable", "--fail-on", "warning")
        self.assertEqual((env["summary"]["error"], env["summary"]["warning"]), (0, 0), [
            (f["rule"], f["message"]) for f in env["findings"] if f["severity"] != "info"])
        self.assertEqual(env["summary"]["pages"], 5)
        self.assertEqual(env["command"], "audit-build")
        self.assertEqual(env["target"], {"type": "build-dir", "path": GOOD, "base_url": "https://example.com",
                                         "profile": "default"})

    def test_site_bad_emits_every_integration_rule(self) -> None:
        got = set(rules_of(self.bad_launch))
        self.assertEqual(sorted(set(self.expected["integration_rules"]) - got), [])
        allowed = set(self.expected["integration_rules"]) | set(self.expected["integration_possible"])
        self.assertEqual(sorted(got - allowed), [])
        self.assertIn("launch", self.bad_launch["coverage"]["checks_run"])

    def test_launch_only_rules_need_the_launch_profile(self) -> None:
        got = set(rules_of(self.bad))
        self.assertFalse(got & set(self.expected["launch_profile_only"]))
        self.assertIn("launch", {s["check"] for s in self.bad["coverage"]["checks_skipped"]})

    def test_check_order_and_coverage(self) -> None:
        self.assertEqual(self.bad["coverage"]["checks_run"],
                         ["pages", "duplicates", "links", "robots", "ai-directives", "sitemaps", "hreflang", "jsonld",
                          "content", "perf", "llms"])
        skipped = {s["check"]: s["reason"] for s in self.bad["coverage"]["checks_skipped"]}
        self.assertIn("HTTP status", skipped["http"])
        self.assertIn("pseo", skipped)
        self.assertIn("field Core Web Vitals", self.bad["coverage"]["not_measured"])
        self.assertTrue(self.bad["limitations"])
        prog = run_json("audit-build", BAD, *BASE, "--profile", "programmatic")
        self.assertIn("pseo", prog["coverage"]["checks_run"])
        geo = run_json("audit-build", GOOD, *BASE, "--profile", "geo")
        self.assertIn("citability", geo["coverage"]["checks_run"])
        self.assertEqual(sorted(geo["scores"]["profiles"]), ["geo"])
        self.assertTrue(geo["data"]["citability"])

    def test_only_v1_rules_and_paths_relative_to_the_working_directory(self) -> None:
        for f in self.bad["findings"]:
            self.assertEqual(CAT.get(f["rule"]).status, "v1", f["rule"])
            if f["file"]:
                self.assertTrue(f["file"].startswith(BAD + "/"), f["file"])
                self.assertTrue((PLUGIN_ROOT / f["file"].split(":")[0]).exists(), f["file"])
        self.assertEqual(helpers.validate_schema(self.bad, "result.schema.json"), [])

    def test_summary_counts_match_findings(self) -> None:
        for sev in ("error", "warning", "info"):
            self.assertEqual(self.bad["summary"][sev], sum(1 for f in self.bad["findings"] if f["severity"] == sev))
        self.assertEqual(self.bad["summary"]["pages"], 31)
        self.assertEqual(len({f["id"] for f in self.bad["findings"]}), len(self.bad["findings"]))

    def test_expect_indexable_escalates_idx001(self) -> None:
        idx_default = helpers.findings_for(self.bad["findings"], "IDX001")
        idx_strict = helpers.findings_for(self.bad_launch["findings"], "IDX001")
        self.assertTrue(idx_default and idx_strict)
        self.assertEqual({f["severity"] for f in idx_default}, {"warning"})
        self.assertEqual({f["severity"] for f in idx_strict}, {"error"})
        self.assertEqual({f["priority"] for f in idx_strict}, {"P0"})

    def test_gate_writes_the_report_before_exiting_1(self) -> None:
        code, out, err = run("audit-build", BAD, *BASE, "--fail-on", "error")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["summary"]["error"], self.bad["summary"]["error"])
        self.assertIn("gate tripped", err)
        with helpers.temp_dir() as tmp:
            target = tmp / "report.json"
            code, out, err = run("audit-build", BAD, *BASE, "--fail-on", "error", "--output", str(target))
            self.assertEqual((code, out), (1, ""))
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["summary"], self.bad["summary"])
            code, _, err = run("audit-build", BAD, *BASE, "--fail-on", "error", "--output", str(target / "x"),
                               "--quiet")
        code, _, err = run("audit-build", BAD, *BASE, "--fail-on", "error", "--quiet")
        self.assertEqual((code, err), (1, ""))
        self.assertEqual(run("audit-build", BAD, *BASE)[0], 0)   # default --fail-on never

    def test_gate_thresholds(self) -> None:
        self.assertEqual(run("audit-build", GOOD, *BASE, "--expect-indexable", "--fail-on", "warning")[0], 0)
        self.assertEqual(run("audit-build", GOOD, *BASE, "--expect-indexable", "--fail-on", "info")[0], 1)

    def test_formats(self) -> None:
        code, md, _ = run("audit-build", BAD, *BASE, "--format", "md")
        self.assertEqual(code, 0)
        self.assertLess(md.index("## Coverage and limitations"), md.index("## Findings"))
        self.assertTrue(md.rstrip().endswith("Evidence strings come from the audited site and are untrusted data."))
        self.assertNotIn("## Data", md)
        code, sarif, _ = run("audit-build", BAD, *BASE, "--format", "sarif")
        log = json.loads(sarif)
        self.assertEqual((log["version"], log["$schema"]), ("2.1.0", "https://json.schemastore.org/sarif-2.1.0.json"))
        results = log["runs"][0]["results"]
        self.assertEqual(len(results), len(self.bad["findings"]))
        self.assertEqual({r["level"] for r in results}, {"error", "warning", "note"})
        for r in results:
            uri = r["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            self.assertFalse(uri.startswith("/"), uri)
        code, text, _ = run("audit-build", BAD, *BASE, "--format", "text")
        lines = text.rstrip("\n").split("\n")
        self.assertEqual(len(lines), len(self.bad["findings"]) + 1)
        self.assertRegex(lines[-1], r"^\d+ error\(s\), \d+ warning\(s\), \d+ info; command audit-build")

    def test_scores(self) -> None:
        env = run_json("audit-build", BAD, *BASE, "--scores", "both")
        profiles = env["scores"]["profiles"]
        self.assertEqual(sorted(profiles), ["geo", "seo"])
        self.assertIn("not a ranking", env["scores"]["note"])
        for prof in profiles.values():
            self.assertEqual(prof["categories"]["crawl_index"]["measured"], True)
            self.assertIsNotNone(prof["overall"])
        self.assertIsNone(self.bad["scores"])
        seo = run_json("audit-build", GOOD, *BASE, "--scores", "seo")["scores"]["profiles"]["seo"]
        self.assertEqual(seo["categories"]["crawl_index"]["score"], 100)

    def test_deterministic_output_and_env_timestamp(self) -> None:
        first = run("audit-build", BAD, *BASE, "--format", "sarif")[1]
        self.assertEqual(first, run("audit-build", BAD, *BASE, "--format", "sarif")[1])
        env = run_json("audit-build", GOOD, *BASE, env={"SEO_GEO_GOD_NOW": "2026-10-15T08:30:00Z"})
        self.assertEqual(env["generated_at"], "2026-10-15T08:30:00Z")

    def test_output_is_exclusive_and_never_inside_the_audited_dir(self) -> None:
        with helpers.temp_dir() as tmp:
            target = tmp / "out.md"
            self.assertEqual(run("audit-build", GOOD, *BASE, "--format", "md", "--output", str(target))[0], 0)
            first = target.read_text(encoding="utf-8")
            code, out, err = run("audit-build", GOOD, *BASE, "--output", str(target))
            self.assertEqual(code, 3)
            self.assertIn("exists", json.loads(out)["error"])
            self.assertEqual(target.read_text(encoding="utf-8"), first)
            self.assertEqual(run("audit-build", GOOD, *BASE, "--output", str(target), "--force")[0], 0)
            self.assertTrue(target.read_text(encoding="utf-8").startswith("{"))
            build = helpers.write_tree(tmp / "dist", {"index.html": html("Home page title", "<h1>Home</h1>")})
            code, _, err = run("audit-build", str(build), "--output", str(build / "report.json"))
            self.assertEqual(code, 3)
            self.assertIn("inside the audited directory", err)
            self.assertFalse((build / "report.json").exists())

    def test_hostile_page_text_cannot_inject_markdown(self) -> None:
        with helpers.temp_dir() as tmp:
            build = helpers.write_tree(tmp / "dist", {
                "index.html": html("<script>alert(1)</script> | Home", '<h1>x</h1><img src="a.png"><a href="'
                                   'javascript:alert(1)" onclick="x()">`|` bad</a>')})
            code, md, _ = run("audit-build", str(build), *BASE, "--format", "md")
        self.assertEqual(code, 0)
        self.assertNotIn("<script", md)
        self.assertNotIn("onclick=", md)
        for line in md.splitlines():
            if line.startswith("| P"):
                self.assertEqual(len(re.findall(r"(?<!\\)\|", line)), 7, line)

    def test_examples_regenerate_byte_identical(self) -> None:
        for fmt, ext in (("json", "json"), ("md", "md"), ("sarif", "sarif")):
            with self.subTest(fmt=fmt):
                code, out, _ = helpers.run_cli(EXAMPLE_ARGS + ["--format", fmt])
                self.assertEqual(code, 0)
                expected = (PLUGIN_ROOT / "examples" / ("audit-site-bad." + ext)).read_text(encoding="utf-8")
                self.assertEqual(out, expected, "regenerate examples/ (see examples/README.md)")
        readme = (PLUGIN_ROOT / "examples" / "README.md").read_text(encoding="utf-8")
        self.assertIn("synthetic", readme.lower())
        self.assertIn("--now 2026-11-01T00:00:00Z", readme)


class AuditPageTests(unittest.TestCase):
    def test_html_page_with_url(self) -> None:
        env = run_json("audit-page", BAD + "/schema/index.html", "--url", "https://example.com/schema/")
        self.assertTrue({"SD001", "SD006", "SD012"} <= set(rules_of(env)))
        self.assertEqual(env["target"]["path"], BAD + "/schema/index.html")
        self.assertEqual(env["coverage"]["checks_run"], ["pages", "ai-directives", "jsonld", "content", "perf"])
        for f in env["findings"]:
            self.assertEqual(f["url"], "https://example.com/schema/")

    def test_markdown_source_skips_layout_rules(self) -> None:
        env = run_json("audit-page", GOOD + "/about/index.md")
        self.assertEqual(env["data"]["kind"], "markdown")
        self.assertFalse(set(rules_of(env)) & (cli.MARKDOWN_LAYOUT_RULES | cli.PAGE_BUILD_RULES))
        self.assertEqual((env["summary"]["error"], env["summary"]["warning"]), (0, 0))
        self.assertIn("layout", {s["check"] for s in env["coverage"]["checks_skipped"]})

    def test_stdin_and_expect_indexable(self) -> None:
        page = html("Noindex page title", "<h1>Hidden</h1><p>Text.</p>", head='<meta name="robots" content="noindex">')
        env = run_json("audit-page", "-", "--expect-indexable", stdin=page.decode("utf-8"))
        idx = helpers.findings_for(env["findings"], "IDX001")
        self.assertEqual([f["severity"] for f in idx], ["error"])
        self.assertEqual(env["target"]["path"], "stdin")
        self.assertIsNone(idx[0]["url"])

    def test_env_files_are_never_read(self) -> None:
        with helpers.temp_dir() as tmp:
            secret = helpers.write_tree(tmp, {".env": "API_KEY=synthetic-canary-value\n"}) / ".env"
            code, out, _ = run("audit-page", str(secret))
        self.assertEqual(code, 3)
        self.assertNotIn("synthetic-canary-value", out)


# ----------------------------------------------------------------------------- network policy

class LiveRefusalTests(unittest.TestCase):
    def test_live_commands_without_live_exit_3_without_sockets(self) -> None:
        cases = [["audit-url", "https://example.com/"], ["access-check", "https://example.com"],
                 ["robots", "--url", "https://example.com/"],
                 ["drift", "snapshot", "--url", "https://example.com/", "--output", "/nonexistent/x.json"]]
        for argv in cases:
            with self.subTest(argv=argv), no_network():
                code, out, err = run(*argv)
                self.assertEqual(code, 3)
                self.assertIn("network disabled: pass --live", json.loads(out)["error"])
                self.assertIn("--live", err)

    def test_ignore_robots_needs_allow_local(self) -> None:
        with no_network():
            code, out, _ = run("audit-url", "https://example.com/", "--live", "--ignore-robots")
        self.assertEqual(code, 3)
        self.assertIn("--allow-local", json.loads(out)["error"])

    def test_ssrf_targets_are_refused_before_any_socket(self) -> None:
        for url in ("http://127.0.0.1/", "http://169.254.169.254/latest/", "http://[::1]/", "http://2130706433/",
                    "http://metadata.google.internal/", "https://user:pass@example.com/", "file:///etc/passwd"):
            for argv in (["audit-url", url, "--live"], ["access-check", url, "--live"]):
                with self.subTest(argv=argv), no_network():
                    code, out, _ = run(*argv)
                    self.assertIn(code, (2, 3))
                    if url.startswith("http"):
                        self.assertEqual(code, 3, out)

    def test_bad_allow_local_is_a_usage_error(self) -> None:
        with no_network():
            self.assertEqual(run("audit-url", "http://localhost:3000/", "--live", "--allow-local", "nonsense")[0], 2)
            self.assertEqual(run("audit-url", "https://example.com/", "--live", "--max-pages", "501")[0], 2)

    def test_offline_commands_never_touch_the_network(self) -> None:
        with no_network():
            run("audit-build", BAD, *BASE)
            run("indexnow", "--build-dir", GOOD, *BASE, "--key", "abcdef123456")
            run("robots", BAD + "/robots.txt")


class LiveFakeTests(unittest.TestCase):
    ROUTES = {
        "https://example.com/robots.txt": (200, {"content-type": "text/plain"},
                                           b"User-agent: *\nDisallow: /private/\n\nUser-agent: GPTBot\nDisallow: /\n\n"
                                           b"Sitemap: https://example.com/sitemap.xml\n"),
        "https://example.com/": (200, {"content-type": "text/html; charset=utf-8"},
                                 html("Example home page", '<h1>Home</h1><p>Welcome to the example site.</p>'
                                      '<a href="/about/">About</a> <a href="/private/x">Private</a> '
                                      '<a href="/gone/">Gone</a> <a href="https://example.org/">Elsewhere</a>',
                                      canonical="https://example.com/")),
        "https://example.com/about/": (200, {"content-type": "text/html"},
                                       html("About Example", '<h1>About</h1><p>About text.</p><a href="/">Home</a>',
                                            canonical="https://example.com/about/")),
        "https://example.com/gone/": (404, {"content-type": "text/html"}, b"<html><body>Missing</body></html>"),
        "https://example.com/sitemap.xml": (200, {"content-type": "application/xml"},
                                            b'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.'
                                            b'org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url>'
                                            b'<loc>https://example.com/about/</loc></url></urlset>'),
    }

    def test_audit_url_crawls_with_robots_and_reports_http_rules(self) -> None:
        with live_fakes(self.ROUTES) as (transport, clock):
            env = run_json("audit-url", "https://example.com/", "--live")
        self.assertEqual(env["mode"], "live")
        self.assertNotIn("https://example.com/private/x", transport.urls)
        self.assertNotIn("https://example.org/", transport.urls)
        self.assertEqual(transport.urls[0], "https://example.com/robots.txt")
        self.assertIn("HTTP001", rules_of(env))
        self.assertIn("http", env["coverage"]["checks_run"])
        self.assertEqual(env["summary"]["pages"], 2)
        self.assertIn("https://example.com/private/x", env["data"]["crawl"]["skipped_robots"])
        self.assertEqual(env["data"]["sitemaps"][0]["urls"], 2)
        self.assertTrue(clock.sleeps and all(s == 1.0 for s in clock.sleeps))
        self.assertIn("ai_access", {CAT.get(r).category for r in rules_of(env)} | {"ai_access"})
        self.assertTrue(any("GPTBot" == row["token"] and not row["allowed"]["/"]
                            for row in env["data"]["robots"]["access"]))

    def test_audit_url_on_an_allowlisted_dev_server(self) -> None:
        routes = {"http://localhost:3000/": (200, {"content-type": "text/html"},
                                             html("Local dev home", "<h1>Dev</h1><p>Local.</p>"))}
        with live_fakes(routes, hosts={"localhost": ["127.0.0.1"]}) as (transport, clock):
            env = run_json("audit-url", "http://localhost:3000/", "--live", "--allow-local", "localhost:3000",
                           "--ignore-robots", "--max-pages", "5")
        self.assertEqual(transport.urls[0], "http://localhost:3000/")
        self.assertEqual(env["summary"]["pages"], 1)
        self.assertTrue(all(s == 0.2 for s in clock.sleeps))

    def test_dns_to_private_address_is_refused(self) -> None:
        with live_fakes({}, hosts={"example.com": ["10.0.0.7"]}) as (transport, _):
            code, out, _ = run("audit-url", "https://example.com/", "--live")
        self.assertEqual(code, 3)
        self.assertEqual(transport.urls, [])

    def test_via_proxy_is_flagged_in_the_envelope(self) -> None:
        with live_fakes(self.ROUTES) as _:
            env = run_json("audit-url", "https://example.com/", "--live", "--via-proxy", "--max-pages", "1",
                           env={"HTTPS_PROXY": "http://10.0.0.5:3128"})
        self.assertTrue(env["via_proxy"])
        self.assertIn("target resolved by proxy; DNS pinning not enforced", env["limitations"])

    def test_robots_url_live(self) -> None:
        with live_fakes(self.ROUTES) as (transport, _):
            env = run_json("robots", "--url", "https://example.com/blog/", "--live", "--bots", "training")
        self.assertEqual(transport.urls, ["https://example.com/robots.txt"])
        self.assertEqual(env["mode"], "live")
        gpt = [r for r in env["data"]["rows"] if r["token"] == "GPTBot"]
        self.assertEqual(gpt[0]["allowed"], {"/": False})

    def test_access_check_live(self) -> None:
        routes = dict(self.ROUTES)
        routes["https://example.com/llms.txt"] = (200, {"content-type": "text/html"},
                                                  b"<!doctype html><html><body>Home</body></html>")
        with live_fakes(routes) as (transport, _):
            env = run_json("access-check", "https://example.com", "--live")
        self.assertIn("AGENT004", rules_of(env))
        self.assertEqual(env["data"]["robots"]["outcome"], "parsed")
        self.assertEqual(env["coverage"]["checks_run"], ["access", "robots", "llms"])
        self.assertTrue(all(u.startswith("https://example.com/") for u in transport.urls))

    def test_drift_snapshot_live(self) -> None:
        with helpers.temp_dir() as tmp, live_fakes(self.ROUTES):
            target = tmp / "snap.json"
            env = run_json("drift", "snapshot", "--url", "https://example.com/", "--live", "--output", str(target))
            snap = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(snap["source"]["type"], "live")
        self.assertEqual(env["data"]["pages"], len(snap["pages"]))
        self.assertGreaterEqual(len(snap["pages"]), 2)


# ----------------------------------------------------------------------------- other commands

class CommandTests(unittest.TestCase):
    def test_stack(self) -> None:
        env = run_json("stack", "tests/fixtures/stack/next")
        self.assertEqual(env["data"]["frameworks"][0]["name"], "next")
        self.assertEqual(run("stack", "tests/fixtures/nope")[0], 2)

    def test_robots_file_table(self) -> None:
        env = run_json("robots", BAD + "/robots.txt", "--bots", "ai", "--path", "/", "--path", "/blog/")
        self.assertEqual(env["data"]["paths"], ["/", "/blog/"])
        self.assertTrue(env["data"]["rows"])
        self.assertTrue({"AI001", "CRAWL004"} & set(rules_of(env)))
        self.assertTrue(all(f["file"] == BAD + "/robots.txt" for f in env["findings"]))

    def test_jsonld(self) -> None:
        env = run_json("jsonld", "tests/fixtures/jsonld", "--recursive")
        paths = [r["path"] for r in env["data"]["files"]]
        self.assertIn("tests/fixtures/jsonld/Seo.tsx", paths)
        self.assertIn("SD018", rules_of(env))
        self.assertEqual(run("jsonld", "tests/fixtures/jsonld", "--recursive", "--fail-on", "error")[0], 1)
        flat = run_json("jsonld", "tests/fixtures/jsonld")
        self.assertTrue(all("/site/" not in r["path"] for r in flat["data"]["files"]))

    def test_sitemap_and_parity(self) -> None:
        env = run_json("sitemap", BAD, "--build-dir", BAD, *BASE)
        self.assertTrue(env["data"]["sitemaps"])
        self.assertTrue(any(r.startswith("SMAP") for r in rules_of(env)))
        one = run_json("sitemap", "tests/fixtures/sitemaps/urlset.xml")
        self.assertEqual(one["data"]["sitemaps"][0]["kind"], "urlset")
        self.assertIn("parity", {s["check"] for s in one["coverage"]["checks_skipped"]})

    def test_hreflang_and_links(self) -> None:
        env = run_json("hreflang", BAD, *BASE)
        self.assertTrue(env["data"]["cluster_count"] >= 1)
        self.assertTrue(any(r.startswith("HREF") for r in rules_of(env)))
        with helpers.temp_dir() as tmp:
            graph = tmp / "graph.json"
            env = run_json("links", BAD, *BASE, "--graph-out", str(graph))
            self.assertIn("edges", json.loads(graph.read_text(encoding="utf-8")))
            self.assertEqual(run("links", BAD, *BASE, "--graph-out", str(graph))[0], 3)
        self.assertIn("LINK001", rules_of(env))
        self.assertEqual(run("links", BAD, *BASE, "--graph-out", BAD + "/graph.json")[0], 3)

    def test_redirects(self) -> None:
        env = run_json("redirects", "tests/fixtures/redirects/map-bad.csv", "--old-build",
                       "tests/fixtures/redirects/old-build", "--new-build", "tests/fixtures/redirects/new-build", *BASE)
        self.assertTrue({"REDIR001", "REDIR002", "REDIR007"} <= set(rules_of(env)))
        self.assertTrue(any(c["loop"] for c in env["data"]["chains"]))
        good = run_json("redirects", "tests/fixtures/redirects/map-good.csv")
        self.assertIn("coverage", {s["check"] for s in good["coverage"]["checks_skipped"]})

    def test_perf(self) -> None:
        env = run_json("perf", BAD, "--lighthouse", "tests/fixtures/lighthouse/lhr-mobile.json", "--crux",
                       "tests/fixtures/lighthouse/crux-record.json")
        self.assertIn("PERF008", rules_of(env))
        self.assertEqual(sorted(env["data"]), ["field", "lab", "static"])
        lab = run_json("perf", "--lighthouse", "tests/fixtures/lighthouse/lhr-mobile.json")
        self.assertEqual(rules_of(lab), ["PERF009"])
        self.assertIn("field Core Web Vitals", lab["coverage"]["not_measured"])

    def test_llms_txt_validate_and_draft(self) -> None:
        env = run_json("llms-txt", "validate", "tests/fixtures/llms/no-h1.txt")
        self.assertEqual(rules_of(env), ["AGENT002"])
        good = run_json("llms-txt", "validate", GOOD + "/llms.txt", "--build-dir", GOOD, *BASE)
        self.assertEqual(good["findings"], [])
        draft = run_json("llms-txt", "draft", GOOD, *BASE, "--title", "Example Widgets")
        self.assertTrue(draft["data"]["text"].startswith("# Example Widgets\n"))
        code, text, _ = run("llms-txt", "draft", GOOD, *BASE, "--title", "Example Widgets", "--format", "text")
        self.assertEqual((code, text), (0, draft["data"]["text"]))
        with helpers.temp_dir() as tmp:
            target = tmp / "llms.txt"
            env = run_json("llms-txt", "draft", GOOD, *BASE, "--title", "Example Widgets", "--output", str(target))
            self.assertEqual(target.read_text(encoding="utf-8"), draft["data"]["text"])
            self.assertEqual(env["data"]["written"], str(target).replace(os.sep, "/"))
        self.assertEqual(run("llms-txt", "draft", GOOD, *BASE, "--title", "T", "--output", GOOD + "/llms2.txt")[0], 3)

    def test_indexnow_prepares_but_never_sends(self) -> None:
        env = run_json("indexnow", "--build-dir", GOOD, *BASE, "--key", "abcdef123456")
        payload = env["data"]["payload"]
        self.assertEqual((payload["host"], payload["key"]), ("example.com", "abcdef123456"))
        self.assertIn("https://example.com/", payload["urlList"])
        self.assertFalse(env["data"]["sent"])
        self.assertEqual(env["data"]["key_file"]["present"], False)
        with helpers.temp_dir() as tmp:
            urls = helpers.write_tree(tmp, {"urls.txt": "# list\nhttps://example.com/a\nhttps://example.com/b\n"})
            env = run_json("indexnow", "--urls-file", str(urls / "urls.txt"), "--key", "abcdef123456")
            self.assertEqual(env["data"]["urls"], 2)
        self.assertEqual(run("indexnow", "--build-dir", GOOD, *BASE, "--key", "short")[0], 2)
        self.assertEqual(run("indexnow", "--key", "abcdef123456")[0], 2)

    def test_citability_and_content_lint(self) -> None:
        env = run_json("citability", "tests/fixtures/content/guide.md", "--query", "widget care", "--top", "3")
        self.assertIn("mean_top5", env["data"])
        self.assertEqual(env["findings"], [])
        lint = run_json("content-lint", "tests/fixtures/content", "--recursive")
        paths = {r["path"] for r in lint["data"]["files"]}
        self.assertIn("tests/fixtures/content/lint-dirty.html", paths)
        self.assertTrue({"CONT004", "CONT009"} & set(rules_of(lint)))
        clean = run_json("content-lint", "tests/fixtures/content/lint-clean.md")
        self.assertEqual(clean["summary"]["error"], 0)

    def test_sections_list_show_replace(self) -> None:
        guide = "tests/fixtures/content/guide.md"
        listing = run_json("sections", "list", guide)
        ids = [s["id"] for s in listing["data"]["sections"]]
        self.assertEqual(ids[0], "s00")
        sid = ids[1]
        with helpers.temp_dir() as tmp:
            original = tmp / "orig.md"
            shown = run_json("sections", "show", guide, "--id", sid, "--output", str(original))
            self.assertEqual(original.read_text(encoding="utf-8"), shown["data"]["text"])
            code, raw, _ = run("sections", "show", guide, "--id", sid, "--format", "text")
            self.assertEqual(raw, shown["data"]["text"])
            new = helpers.write_tree(tmp, {"new.md": shown["data"]["text"].replace("Widget", "Example widget", 1)})
            diff = run_json("sections", "replace", guide, "--id", sid, "--with", str(new / "new.md"))
            self.assertTrue(diff["data"]["diff"].startswith("--- a/" + guide))
            out = tmp / "guide.new.md"
            run_json("sections", "replace", guide, "--id", sid, "--with", str(new / "new.md"), "--output", str(out))
            self.assertIn("Example widget", out.read_text(encoding="utf-8"))
            copy = helpers.write_tree(tmp, {"copy.md": helpers.read_fixture("content", "guide.md")}) / "copy.md"
            code, _, err = run("sections", "replace", str(copy), "--id", sid, "--with", str(new / "new.md"),
                               "--output", str(copy), "--force")
            self.assertEqual(code, 3)
            self.assertIn("in place", err)
        self.assertEqual(run("sections", "show", guide, "--id", "s99")[0], 2)

    def test_fidelity_gate(self) -> None:
        base = "tests/fixtures/content/fidelity/"
        ok = run_json("fidelity", base + "original.md", base + "rewrite-faithful.md")
        self.assertTrue(ok["data"]["passed"])
        code, out, err = run("fidelity", base + "original.md", base + "page-rewrite-drops-source.md")
        self.assertEqual(code, 1)
        env = json.loads(out)
        self.assertFalse(env["data"]["passed"])
        self.assertTrue(all(r.startswith("FID") for r in rules_of(env)) and env["findings"])
        self.assertIn("fidelity", err)
        self.assertEqual(run("fidelity", base + "original.md", base + "original.md", "--min-ratio", "0.9")[0], 0)

    def test_drift_snapshot_compare_and_findings(self) -> None:
        with helpers.temp_dir() as tmp:
            snap = tmp / "base.json"
            env = run_json("drift", "snapshot", GOOD, *BASE, "--output", str(snap))
            self.assertEqual(env["data"]["pages"], 5)
            same = run_json("drift", "compare", str(snap), GOOD, *BASE)
            self.assertEqual(same["findings"], [])
            self.assertTrue(same["data"]["comparable"])
            self.assertEqual(run("drift", "snapshot", GOOD, *BASE)[0], 2)
            self.assertEqual(run("drift", "snapshot", GOOD, *BASE, "--output", GOOD + "/snap.json")[0], 3)
            old = tmp / "old.json"
            new = tmp / "new.json"
            run("audit-build", GOOD, *BASE, "--output", str(old))
            run("audit-build", GOOD, *BASE, "--output", str(new), "--now", "2026-11-02T00:00:00Z")
            diff = run_json("drift", "findings", str(old), str(new))
            self.assertEqual(diff["data"]["counts"]["added"], 0)
        expected = json.loads(helpers.read_fixture("drift", "EXPECTED.json"))
        pair = run_json("drift", "compare", "tests/fixtures/drift/baseline.json", "tests/fixtures/drift/current.json")
        want = {v for v in expected["pages"].values() if v} | set(expected["site_rules"])
        self.assertEqual(sorted(want - set(rules_of(pair))), [])
        self.assertEqual(run("drift", "compare", "tests/fixtures/drift/baseline.json",
                             "tests/fixtures/drift/current.json", "--fail-on", "error")[0], 1)
        other = run_json("drift", "compare", "tests/fixtures/drift/baseline.json",
                         "tests/fixtures/drift/current-other-origin.json")
        self.assertEqual(rules_of(other), [expected["not_comparable_rule"]])
        self.assertIsNone(other["data"]["deltas"])

    def test_ledger_lifecycle(self) -> None:
        panel = {"kind": "panel", "surface": "perplexity", "query": "how to send a recurring invoice",
                 "query_class": "informational", "holdout": False, "status": "valid_present",
                 "cited_urls": ["https://example.com/guides/recurring-invoices/"], "locale": "en-US",
                 "device": "mobile", "logged_in": False}
        with helpers.temp_dir() as tmp:
            d = str(tmp / "ledger")
            self.assertEqual(run_json("ledger", "init", d)["data"]["schema"], ledger.LEDGER_SCHEMA)
            self.assertEqual(run("ledger", "init", d)[0], 3)
            obs = helpers.write_tree(tmp, {"obs.json": json.dumps(panel)}) / "obs.json"
            self.assertEqual(run_json("ledger", "record", d, "--json", str(obs))["data"]["recorded"], 1)
            self.assertEqual(run("ledger", "record", d, "--json", str(obs))[0], 2)
            second = dict(panel, surface="chatgpt", status="valid_absent", cited_urls=[])
            self.assertEqual(run_json("ledger", "record", d, "--json", "-", stdin=json.dumps([second]))
                             ["data"]["recorded"], 1)
            summary = run_json("ledger", "summary", d, "--by", "surface")
            self.assertTrue(summary["data"])
            self.assertEqual(run("ledger", "summary", d, "--window", "2026-11-01")[0], 2)
            status = run_json("ledger", "status", d)
            self.assertEqual(status["data"]["experiments"], [])

    def test_gsc_subcommands(self) -> None:
        g = "tests/fixtures/analytics/gsc/"
        cases = {"movers": [g + "queries-cur.csv", g + "queries-prev.csv"],
                 "decay": [g + "pages-cur.csv", g + "pages-prev.csv"],
                 "ctr": [g + "queries-cur.csv", "--calibrate"], "striking": [g + "queries-cur.csv"],
                 "cannibalization": [g + "query-page.json", "--dimensions", "query,page"],
                 "brand": [g + "queries-cur.csv", "--brand-terms", "example"],
                 "buckets": [g + "planner.json", "--dimensions", "query,page"],
                 "aio-recovery": [g + "queries-cur.csv", g + "queries-prev.csv"]}
        for sub, rest in cases.items():
            with self.subTest(sub=sub):
                env = run_json("gsc", sub, *rest)
                self.assertEqual(env["command"], "gsc " + sub)
                self.assertTrue(env["data"])
                self.assertIn("not forecasts", env["limitations"][0])
        self.assertIn("calibrated_curve", run_json("gsc", "ctr", g + "queries-cur.csv", "--calibrate")["data"])
        code, md, _ = run("gsc", "striking", g + "queries-cur.csv", "--format", "md")
        self.assertIn("## Data", md)
        self.assertTrue(md.rstrip().endswith("untrusted data."))

    def test_referrers_gaps_project(self) -> None:
        ref = run_json("referrers", "tests/fixtures/analytics/ga4/sessions.csv")
        self.assertIn("ai", ref["data"])
        bots = run_json("referrers", "tests/fixtures/analytics/logs/access.log", "--log", "--bots")
        self.assertIn("claimed", json.dumps(bots["data"]))
        t = "tests/fixtures/analytics/tracker/"
        plan = run_json("gaps", "plan", t + "tracker.csv", "--project", t + "project.json")
        self.assertIn("gaps", plan["data"])
        valid = run_json("project", "validate", t + "project.json")
        self.assertEqual(valid["data"], {"valid": True, "problems": []})
        with helpers.temp_dir() as tmp:
            bad = helpers.write_tree(tmp, {"p.json": json.dumps({"schema_version": 1, "api_key": "x"})})
            self.assertFalse(run_json("project", "validate", str(bad / "p.json"))["data"]["valid"])

    def test_updates_and_crawlers(self) -> None:
        env = run_json("updates", "--since", "2026", "--kind", "core")
        self.assertIn("freshness", env["data"])
        crawlers = run_json("crawlers", "--class", "TRAIN")
        rows = crawlers["data"]["crawlers"]
        self.assertTrue(rows and all(r["class"] == "TRAIN" for r in rows))
        self.assertIn("GPTBot", {r["token"] for r in rows})
        self.assertNotIn("policy_tokens", crawlers["data"])
        self.assertIn("policy_tokens", run_json("crawlers")["data"])


class DeterminismTests(unittest.TestCase):
    def test_json_ld_syntax_errors_read_the_same_on_every_python(self) -> None:
        from seo_geo_lib import jsonld
        cases = {'{"a": 1,}': "Illegal trailing comma before end of object at line 1 column 8",
                 '[1, 2,\n ]': "Illegal trailing comma before end of array at line 1 column 6",
                 '{"a": [1,]}': "Illegal trailing comma before end of array at line 1 column 9",
                 '{"a" 1}': "Expecting ':' delimiter at line 1 column 6"}
        for raw, message in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(jsonld.parse_block(raw), (None, "malformed JSON (%s)" % message))


class RulesAndDoctorTests(unittest.TestCase):
    def test_rules_md_equals_the_reference_catalog(self) -> None:
        code, out, _ = helpers.run_cli(["rules", "--format", "md"])
        self.assertEqual(code, 0)
        reference = (PLUGIN_ROOT / "references" / "rule-catalog.md").read_text(encoding="utf-8")
        self.assertEqual(out, reference, "regenerate with: python3 -I scripts/seo_geo.py rules --format md")
        for rule in CAT.all():
            self.assertIn('<a id="%s"></a>' % rule.id.lower(), out)
        self.assertNotIn("## Data", out)

    def test_rules_json_filters(self) -> None:
        env = run_json("rules")
        self.assertEqual(env["data"]["count"], len(CAT))
        planned = run_json("rules", "--status", "planned")["data"]["rules"]
        self.assertTrue(planned and all(r["status"] == "planned" for r in planned))
        sd = run_json("rules", "--category", "structured_data")["data"]["rules"]
        self.assertTrue(sd and all(r["category"] == "structured_data" for r in sd))

    def test_doctor(self) -> None:
        code, out, err = run("doctor", "--today", "2026-11-01")
        self.assertEqual((code, err), (0, ""))
        data = json.loads(out)["data"]
        self.assertTrue(data["ok"])
        self.assertTrue(data["python"]["ok"])
        self.assertEqual(data["catalog"]["problems"], [])
        self.assertEqual({r["status"] for r in data["data"]}, {"fresh"})
        self.assertEqual(data["catalog"]["rules"], len(CAT))
        code, out, err = run("doctor", "--today", "2027-03-01")
        self.assertEqual(code, 0)
        self.assertIn("aging", err)
        self.assertTrue(json.loads(out)["data"]["ok"])
        code, out, err = run("doctor", "--today", "2027-09-01", "--quiet")
        self.assertEqual(err, "")
        self.assertFalse(json.loads(out)["data"]["ok"])


class RobotsTemplateTests(unittest.TestCase):
    TEMPLATES = PLUGIN_ROOT / "templates" / "robots"

    def _rows(self, name: str) -> Dict[str, Dict[str, Any]]:
        path = self.TEMPLATES / name
        if not path.is_file():
            self.skipTest("templates/robots/%s is written by another package and does not exist yet" % name)
        env = run_json("robots", str(path.relative_to(PLUGIN_ROOT)), "--bots", "all")
        self.assertEqual(env["data"]["summary"]["errors"], [])
        return {r["token"]: r for r in env["data"]["rows"]}

    def test_templates_parse_cleanly(self) -> None:
        if not self.TEMPLATES.is_dir():
            self.skipTest("templates/robots/ is written by another package and does not exist yet")
        for path in sorted(self.TEMPLATES.glob("*.txt")):
            with self.subTest(path=path.name):
                parsed = robots.parse_robots(path.read_text(encoding="utf-8"))
                self.assertEqual((parsed.errors, parsed.orphans, parsed.truncated), ([], [], False))
                self.assertTrue(parsed.groups)

    def test_search_only_keeps_search_and_user_fetchers(self) -> None:
        rows = self._rows("search-only-no-training.txt")
        for token in ("OAI-SearchBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Googlebot", "bingbot"):
            self.assertTrue(rows[token]["allowed"]["/"], token)
        for token in ("GPTBot", "ClaudeBot", "Google-Extended", "CCBot", "__usage_ai-training"):
            self.assertFalse(rows[token]["allowed"]["/"], token)

    def test_open_and_closed_templates(self) -> None:
        open_rows = self._rows("search-and-ai-open.txt")
        self.assertTrue(all(open_rows[t]["allowed"]["/"] for t in ("GPTBot", "OAI-SearchBot", "Googlebot")))
        closed = self._rows("closed-to-ai.txt")
        self.assertFalse(closed["GPTBot"]["allowed"]["/"])
        self.assertTrue(closed["Googlebot"]["allowed"]["/"])


class EntryPointTests(unittest.TestCase):
    def test_entry_script_is_small_and_python39(self) -> None:
        src = (PLUGIN_ROOT / "scripts" / "seo_geo.py").read_text(encoding="utf-8")
        self.assertLessEqual(len(src.splitlines()), 25)
        self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parent))", src)
        for path in (PLUGIN_ROOT / "scripts" / "seo_geo.py", PLUGIN_ROOT / "scripts" / "seo_geo_lib" / "cli.py",
                     Path(__file__)):
            ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))

    def test_entry_script_runs_main(self) -> None:
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["seo_geo.py", "rules", "--status", "planned", "--now", NOW]), \
                contextlib.redirect_stdout(out):
            with self.assertRaises(SystemExit) as caught:
                runpy.run_path(str(PLUGIN_ROOT / "scripts" / "seo_geo.py"), run_name="__main__")
        self.assertEqual(caught.exception.code, 0)
        self.assertEqual(json.loads(out.getvalue())["command"], "rules")

    def test_cli_imports_only_stdlib_and_the_package(self) -> None:
        tree = ast.parse((PLUGIN_ROOT / "scripts" / "seo_geo_lib" / "cli.py").read_text(encoding="utf-8"))
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names.add((node.module or "").split(".")[0])
        self.assertFalse(names & {"subprocess", "requests", "pickle", "importlib", "socket"})
        stdlib = getattr(sys, "stdlib_module_names", None)
        if stdlib:
            self.assertEqual(sorted(n for n in names if n not in stdlib and n != "__future__"), [])


if __name__ == "__main__":
    unittest.main()
