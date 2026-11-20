"""WP01 stack detection tests: fixtures under tests/fixtures/stack/ plus synthetic temp repos."""
from __future__ import annotations

import builtins
import json
import os
import re
import shutil
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_stack
import helpers  # noqa: E402
from seo_geo_lib import stack  # noqa: E402
from seo_geo_lib.stack import detect_stack  # noqa: E402


def setUpModule() -> None:
    helpers.block_network()


CANARIES = ("leak-canary", "fixture-canary", "DO_NOT_LEAK")
KEYS = {"frameworks", "package_manager", "lockfiles", "build_script", "rendering_hints", "build_output_candidates",
        "site_url_candidates", "site_url_env_vars", "seo_surfaces", "recipe_anchors", "skipped", "notes"}


def names(result):
    return [fw["name"] for fw in result["frameworks"]]


def detect_fixture(name):
    return detect_stack(str(helpers.fixture("stack", name)))


def github_slug(heading: str) -> str:
    text = re.sub(r"<[^>]+>", "", heading).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


class FixtureTest(unittest.TestCase):
    def test_next_app_router_static_export(self) -> None:
        r = detect_fixture("next")
        self.assertEqual(set(r), KEYS)
        self.assertEqual(names(r), ["next"])
        fw = r["frameworks"][0]
        self.assertEqual((fw["version"], fw["label"]), ("^15.0.3", "Next.js (app router)"))
        self.assertEqual(fw["evidence"], ["package.json", "next.config.mjs", "app/"])
        self.assertEqual((r["package_manager"], r["lockfiles"], r["build_script"]),
                         ("pnpm", ["pnpm-lock.yaml"], "next build"))
        self.assertEqual(r["build_output_candidates"], ["out"])
        self.assertTrue(any("output 'export'" in h for h in r["rendering_hints"]))
        self.assertTrue(any("trailingSlash" in h for h in r["rendering_hints"]))
        self.assertEqual(r["site_url_candidates"], [{"value": "https://www.example.com/", "source": "package.json: homepage"}])
        self.assertEqual(r["site_url_env_vars"], ["NEXT_PUBLIC_SITE_URL"])
        self.assertEqual(r["seo_surfaces"]["metadata"], ["app/layout.tsx"])
        self.assertEqual(r["seo_surfaces"]["sitemap"], ["app/sitemap.ts"])
        self.assertEqual(r["seo_surfaces"]["robots"], ["app/robots.ts"])
        self.assertEqual(r["recipe_anchors"], ["framework-recipes.md#nextjs-app-router"])

    def test_astro_site(self) -> None:
        r = detect_fixture("astro")
        self.assertEqual(names(r), ["astro"])
        self.assertEqual(r["frameworks"][0]["version"], "^5.1.0")
        self.assertEqual(r["site_url_candidates"], [{"value": "https://docs.example.org/", "source": "astro.config.mjs: site"}])
        self.assertEqual((r["package_manager"], r["build_output_candidates"]), ("npm", ["dist"]))
        self.assertEqual(r["seo_surfaces"]["sitemap"], ["astro.config.mjs"])
        self.assertEqual(r["seo_surfaces"]["robots"], ["public/robots.txt"])
        self.assertEqual(r["seo_surfaces"]["headers"], ["public/_headers"])
        self.assertEqual(r["recipe_anchors"], ["framework-recipes.md#astro"])
        self.assertFalse(any("no site configured" in h for h in r["rendering_hints"]))

    def test_hugo_base_url(self) -> None:
        r = detect_fixture("hugo")
        self.assertEqual(names(r), ["hugo"])
        self.assertEqual(r["site_url_candidates"], [{"value": "https://example.org/", "source": "hugo.toml: baseURL"}])
        self.assertEqual((r["package_manager"], r["build_output_candidates"]), (None, ["public"]))
        self.assertEqual(r["seo_surfaces"]["metadata"], ["layouts/_default/baseof.html"])
        self.assertFalse(any("baseURL missing" in h for h in r["rendering_hints"]))

    def test_vite_spa(self) -> None:
        r = detect_fixture("spa-vite")
        self.assertEqual(names(r), ["vite"])
        self.assertEqual(r["frameworks"][0]["label"], "Vite SPA (react)")
        self.assertEqual((r["package_manager"], r["build_output_candidates"]), ("yarn", ["dist"]))
        self.assertTrue(any("REND001" in h for h in r["rendering_hints"]))
        self.assertEqual(r["recipe_anchors"], ["framework-recipes.md#vite-spa"])
        self.assertEqual(r["site_url_candidates"], [])

    def test_wordpress_theme(self) -> None:
        r = detect_fixture("wordpress-theme")
        self.assertEqual(names(r), ["wordpress-theme"])
        fw = r["frameworks"][0]
        self.assertEqual((fw["label"], fw["version"]), ("WordPress theme: Example Starter", "1.2.0"))
        self.assertEqual(fw["evidence"], ["style.css", "functions.php"])
        self.assertEqual(r["seo_surfaces"]["metadata"], ["functions.php", "header.php"])
        self.assertTrue(any("audit-url --allow-local" in h for h in r["rendering_hints"]))

    def test_deterministic(self) -> None:
        for name in ("next", "astro", "hugo", "spa-vite", "wordpress-theme"):
            self.assertEqual(json.dumps(detect_fixture(name), sort_keys=True),
                             json.dumps(detect_fixture(name), sort_keys=True))


class SecretSafetyTest(unittest.TestCase):
    def test_env_files_never_opened_or_echoed(self) -> None:
        fixture_root = helpers.fixture("stack", "next")
        with helpers.temp_dir() as d:
            copy = d / "repo"
            shutil.copytree(str(fixture_root), str(copy))
            helpers.write_tree(copy, {".env": "NEXT_PUBLIC_SITE_URL=https://leak-canary.example.net\n"
                                              "DO_NOT_LEAK_TOKEN=fixture-canary-0d6f1c9a\n"})
            for root in (fixture_root, copy):  # the copy guarantees the canary even if dotfiles were not shipped
                opened = []
                real_open = builtins.open

                def spy(file, *args, **kwargs):
                    opened.append(os.path.basename(str(file)))
                    return real_open(file, *args, **kwargs)
                with mock.patch("builtins.open", spy):
                    result = detect_stack(str(root))
                self.assertIn("package.json", opened)
                self.assertFalse([n for n in opened if n.lower().startswith(".env")], opened)
                blob = json.dumps(result)
                for canary in CANARIES:
                    self.assertNotIn(canary, blob)
                self.assertEqual(result["site_url_env_vars"], ["NEXT_PUBLIC_SITE_URL"])

    def test_env_only_repo_and_copied_canary(self) -> None:
        with helpers.temp_dir() as d:
            shutil.copytree(str(helpers.fixture("stack", "next")), str(d / "repo"))
            helpers.write_tree(d / "repo", {".env.production": "SITE_URL=https://leak-canary.example.net\n",
                                            ".envrc": "export DO_NOT_LEAK=1\n"})
            blob = json.dumps(detect_stack(str(d / "repo")))
            empty = detect_stack(str(helpers.write_tree(d / "bare", {".env": "SITE_URL=https://leak-canary.example.net\n"})))
        for canary in CANARIES:
            self.assertNotIn(canary, blob)
        self.assertEqual((empty["frameworks"], empty["site_url_candidates"]), ([], []))

    def test_symlinks_and_size_limits(self) -> None:
        with helpers.temp_dir() as d:
            outside = helpers.write_tree(d / "outside", {"package.json": json.dumps({"dependencies": {"next": "1"}})})
            repo = helpers.write_tree(d / "repo", {"hugo.toml": "baseURL = 'https://example.org/'\n" + "#" * 1_048_577})
            os.symlink(outside / "package.json", repo / "package.json")
            os.symlink(outside, repo / "app")
            r = detect_stack(str(repo))
        self.assertEqual(names(r), ["hugo"])  # config present but unread: no next from the symlink, no baseURL claim
        self.assertFalse(any("baseURL" in h for h in r["rendering_hints"]))
        self.assertEqual(r["site_url_candidates"], [])
        reasons = {s["file"]: s["reason"] for s in r["skipped"]}
        self.assertEqual(reasons["package.json"], "symlink or outside root")
        self.assertIn("larger than", reasons["hugo.toml"])
        self.assertEqual(len(r["skipped"]), len({(s["file"], s["reason"]) for s in r["skipped"]}))

    def test_invalid_inputs(self) -> None:
        with helpers.temp_dir() as d:
            helpers.write_tree(d, {"package.json": "{not json", "angular.json": "[1, 2]", "file.txt": "x"})
            r = detect_stack(str(d))
            self.assertIn({"file": "package.json", "reason": "invalid JSON"}, r["skipped"])
            self.assertEqual(names(r), ["angular"])
            with self.assertRaises(ValueError):
                detect_stack(str(d / "file.txt"))
            with self.assertRaises(ValueError):
                detect_stack(str(d / "missing"))


def pkg(deps=None, dev=None, **extra):
    doc = {"name": "fixture", "dependencies": deps or {}, "devDependencies": dev or {}}
    doc.update(extra)
    return json.dumps(doc)


SYNTHETIC = {
    "next-pages-ssr": ({"package.json": pkg({"next": "^14.2.0"}), "next.config.js": "module.exports = { distDir: 'build',"
                        " async redirects() { return []; }, async headers() { return []; } };\n",
                        "pages/index.tsx": "x", "pages/_app.tsx": "x"},
                       ["next"], "nextjs-pages-router", ["build"]),
    "nuxt": ({"package.json": pkg({"nuxt": "^3.13.0"}), "nuxt.config.ts": "export default { ssr: false }\n"},
             ["nuxt"], "nuxt", [".output/public"]),
    "sveltekit-static": ({"package.json": pkg(dev={"@sveltejs/kit": "^2.0.0", "@sveltejs/adapter-static": "^3.0.0",
                                                   "vite": "^5.0.0"}),
                          "svelte.config.js": "import adapter from '@sveltejs/adapter-static';\n"},
                         ["sveltekit"], "sveltekit", ["build"]),
    "remix": ({"package.json": pkg({"@remix-run/react": "^2.0.0"}, {"@remix-run/dev": "^2.0.0", "vite": "^5.0.0"})},
              ["remix"], "remix", ["build/client", "public/build"]),
    "react-router-spa": ({"package.json": pkg(dev={"@react-router/dev": "^7.0.0", "vite": "^6.0.0"}),
                          "react-router.config.ts": "export default { ssr: false };\n"},
                         ["react-router"], "react-router", ["build/client"]),
    "gatsby": ({"package.json": pkg({"gatsby": "^5.0.0"}),
                "gatsby-config.js": "module.exports = { siteMetadata: { siteUrl: 'https://www.example.net' } };\n"},
               ["gatsby"], "gatsby", ["public"]),
    "docusaurus": ({"package.json": pkg({"@docusaurus/core": "^3.0.0"}),
                    "docusaurus.config.js": "module.exports = { url: 'https://docs.example.com', baseUrl: '/' };\n"},
                   ["docusaurus"], "docusaurus", ["build"]),
    "vitepress": ({"package.json": pkg(dev={"vitepress": "^1.0.0", "vite": "^5.0.0"}),
                   "docs/.vitepress/config.mts": "export default { sitemap: { hostname: 'https://example.com' } }\n"},
                  ["vitepress"], "vitepress", ["docs/.vitepress/dist"]),
    "angular": ({"angular.json": json.dumps({"projects": {"shop": {"architect": {"build": {"options": {
                 "outputPath": "dist/shop"}}}}}}), "package.json": pkg({"@angular/core": "^18.0.0", "@angular/ssr": "^18"})},
                ["angular"], "angular-ssr", ["dist/shop/browser", "dist/shop"]),
    "cra": ({"package.json": pkg({"react": "^18.0.0", "react-scripts": "5.0.1"})}, ["create-react-app"],
            "create-react-app", ["build"]),
    "jekyll": ({"_config.yml": "title: Example\nurl: \"https://example.org\"\nbaseurl: \"\"\n",
                "Gemfile": "source 'https://rubygems.org'\ngem \"jekyll\", \"~> 4.3\"\n"},
               ["jekyll"], "jekyll", ["_site"]),
    "eleventy": ({"package.json": pkg(dev={"@11ty/eleventy": "^3.0.0"}), "eleventy.config.js": "export default {};\n"},
                 ["eleventy"], "eleventy", ["_site"]),
    "hugo-config-toml": ({"config.toml": "baseURL = \"https://example.net/\"\ntitle = \"x\"\n"}, ["hugo"], "hugo",
                         ["public"]),
    "shopify": ({"layout/theme.liquid": "<html>{{ content_for_header }}</html>",
                 "templates/robots.txt.liquid": "{{ robots }}"}, ["shopify-theme"], "shopify-liquid-themes", []),
    "django": ({"manage.py": "import os\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site.settings')\n"
                             "from django.core.management import execute_from_command_line\n"},
               ["django"], "django", []),
    "rails": ({"Gemfile": "gem 'rails', '~> 7.1'\n", "public/robots.txt": "User-agent: *\n"}, ["rails"], "rails", []),
    "laravel": ({"artisan": "#!/usr/bin/env php\n", "composer.json": json.dumps({"require": {"laravel/framework": "^11.0"}})},
                ["laravel"], "laravel", []),
    "static": ({"index.html": "<!doctype html><title>x</title>", "CNAME": "www.example.com\n", "_redirects": "/a /b 301\n"},
               ["static-html"], "plain-static-html", ["."]),
}


class SyntheticRepoTest(unittest.TestCase):
    def test_each_detector(self) -> None:
        with helpers.temp_dir() as d:
            for name, (files, expected, anchor, outputs) in SYNTHETIC.items():
                with self.subTest(repo=name):
                    r = detect_stack(str(helpers.write_tree(d / name, files)))
                    self.assertEqual(names(r), expected)
                    self.assertIn("framework-recipes.md#" + anchor, r["recipe_anchors"])
                    self.assertEqual(r["build_output_candidates"], outputs)

    def test_details(self) -> None:
        with helpers.temp_dir() as d:
            def run(name):
                return detect_stack(str(helpers.write_tree(d / name, SYNTHETIC[name][0])))
            nxt = run("next-pages-ssr")
            self.assertTrue(any("audit-url --live --allow-local" in h for h in nxt["rendering_hints"]))
            self.assertEqual(nxt["seo_surfaces"]["redirects"], ["next.config.js"])
            self.assertEqual(nxt["seo_surfaces"]["headers"], ["next.config.js"])
            self.assertIn("pages/_app.tsx", nxt["seo_surfaces"]["metadata"])
            self.assertTrue(any("ssr false" in h for h in run("nuxt")["rendering_hints"]))
            self.assertTrue(any("SPA mode" in h for h in run("react-router-spa")["rendering_hints"]))
            self.assertEqual(run("gatsby")["site_url_candidates"],
                             [{"value": "https://www.example.net/", "source": "gatsby-config.js: siteUrl"}])
            self.assertEqual(run("docusaurus")["site_url_candidates"][0]["value"], "https://docs.example.com/")
            self.assertEqual(run("vitepress")["site_url_candidates"][0]["source"], "docs/.vitepress/config.mts: hostname")
            self.assertEqual(run("jekyll")["site_url_candidates"], [{"value": "https://example.org/",
                                                                     "source": "_config.yml: url"}])
            static = run("static")
            self.assertEqual(static["site_url_candidates"], [{"value": "https://www.example.com/",
                                                              "source": "CNAME (https assumed)"}])
            self.assertEqual(static["seo_surfaces"]["redirects"], ["_redirects"])
            self.assertEqual(run("shopify")["seo_surfaces"]["robots"], ["templates/robots.txt.liquid"])
            both = detect_stack(str(helpers.write_tree(d / "both", {"package.json": pkg({"next": "15.0.0"}),
                                                                    "app/page.tsx": "x", "src/pages/a.tsx": "x"})))
            self.assertEqual(both["frameworks"][0]["label"], "Next.js (app router + pages router)")
            self.assertEqual(both["recipe_anchors"], ["framework-recipes.md#nextjs-app-router",
                                                      "framework-recipes.md#nextjs-pages-router"])
            self.assertEqual(both["build_output_candidates"], [".next"])
            astro_ssr = detect_stack(str(helpers.write_tree(d / "astro-ssr", {
                "package.json": pkg({"astro": "^5.0.0", "@astrojs/node": "^9.0.0"}),
                "astro.config.mjs": "export default { output: 'server' };\n"})))
            self.assertEqual(astro_ssr["build_output_candidates"], ["dist/client", "dist"])
            self.assertTrue(any("no site configured" in h for h in astro_ssr["rendering_hints"]))
            hugo_no_base = detect_stack(str(helpers.write_tree(d / "hugo-nobase", {"hugo.toml": "title = 'x'\n"})))
            self.assertTrue(any("baseURL missing" in h for h in hugo_no_base["rendering_hints"]))
            declared = detect_stack(str(helpers.write_tree(d / "pm", {
                "package.json": pkg({"vite": "^5"}, packageManager="bun@1.1.0"), "package-lock.json": "{}"})))
            self.assertEqual((declared["package_manager"], declared["lockfiles"]), ("bun", ["package-lock.json"]))
            plain_toml = detect_stack(str(helpers.write_tree(d / "zola", {"config.toml": "base_url = 'https://x.test'\n"})))
            self.assertEqual(plain_toml["frameworks"], [])
            bad_cname = detect_stack(str(helpers.write_tree(d / "cname", {"index.html": "x", "CNAME": "not a domain\n"})))
            self.assertEqual(bad_cname["site_url_candidates"], [])

    def test_recipe_anchor_inventory(self) -> None:
        self.assertEqual(len(stack.RECIPE_ANCHORS), len(set(stack.RECIPE_ANCHORS)))
        recipes = helpers.REFERENCES_DIR / "framework-recipes.md"
        if not recipes.is_file():
            self.skipTest("references/framework-recipes.md not present (written by another package)")
        text = recipes.read_text(encoding="utf-8")
        anchors = {github_slug(m) for m in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*#*\s*$", text)}
        anchors |= set(re.findall(r'<a\s+id="([^"]+)"', text))
        missing = [a for a in stack.RECIPE_ANCHORS if a not in anchors]
        self.assertEqual(missing, [], "stack.py recipe anchors missing from framework-recipes.md")


class NoNetworkTest(unittest.TestCase):
    def test_no_network_attempts(self) -> None:
        self.assertEqual(helpers.network_attempts(), [])


if __name__ == "__main__":
    unittest.main()
