"""Mutation tests for the independent package validator, using disposable fixtures."""
from __future__ import annotations

import importlib.util
import json
import os
import stat
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_plugin.py"
SPEC = importlib.util.spec_from_file_location("ios_package_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "example-plugin"
        self.root.mkdir()
        self.manifest = {
            "$schema": validator.SCHEMA, "name": "example-plugin", "version": "1.0.0",
            "extensions": {"com.openai": {"interface": {
                "displayName": "Example", "shortDescription": "Test iOS workflows",
                "category": "Developer Tools", "capabilities": [],
                "defaultPrompt": "Inspect this project.", "logo": "assets/icon.svg",
            }}},
        }
        self.write_manifest()
        (self.root / "assets").mkdir()
        (self.root / "assets/icon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64"/></svg>')
        self.skill = self.root / "skills/example-skill/SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text('---\nname: example-skill\ndescription: "Use for an example."\n---\n\nRead [guidance](../../docs/guide.md).\n')
        (self.root / "docs").mkdir()
        (self.root / "docs/guide.md").write_text("Example guidance.\n")

    def write_manifest(self):
        (self.root / "plugin.json").write_text(json.dumps(self.manifest))

    def errors(self):
        return validator.validate_plugin(self.root)

    def archive(self, wrapper=True):
        archive = self.base / "package.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            for path in self.root.rglob("*"):
                if path.is_file():
                    name = path.relative_to(self.root)
                    zipped.write(path, (Path(self.root.name) / name).as_posix() if wrapper else name.as_posix())
        return archive

    def test_valid_minimal_package_and_both_zip_layouts(self):
        self.assertEqual(self.errors(), [])
        self.assertEqual(validator.validate_archive(self.archive()), [])
        self.assertEqual(validator.validate_archive(self.archive(wrapper=False)), [])

    def test_optional_expected_count_does_not_hardcode_production_count(self):
        self.assertEqual(validator.validate_plugin(self.root, expected_skills=1), [])
        self.assertTrue(any("expected 7" in e for e in validator.validate_plugin(self.root, expected_skills=7)))

    def test_missing_skill_is_not_a_usable_package(self):
        self.skill.unlink()
        self.assertTrue(any("at least one usable skill" in e for e in self.errors()))

    def test_missing_entrypoint_is_reported_alongside_existing_skill(self):
        (self.root / "skills/empty-skill").mkdir()
        self.assertIn("missing SKILL.md entrypoint", "\n".join(self.errors()))

    def test_invalid_manifest_metadata(self):
        interface = self.manifest["extensions"]["com.openai"]["interface"]
        interface.update(shortDescription="x" * 31, category="developer-tools", capabilities="tools")
        self.manifest["version"] = "1.0"
        self.manifest["skills"] = "./skills"
        self.write_manifest()
        errors = "\n".join(self.errors())
        for expected in ("30 characters", "category", "capabilities", "SemVer", "root field skills"):
            self.assertIn(expected, errors)

    def test_duplicate_json_keys_are_rejected(self):
        (self.root / "plugin.json").write_text('{"name":"first","name":"second"}')
        self.assertIn("duplicate key", "\n".join(self.errors()))

    def test_malformed_manifest_types_return_errors_instead_of_crashing(self):
        for extensions in ([], "invalid", {"com.openai": []}):
            self.manifest["extensions"] = extensions
            self.write_manifest()
            self.assertTrue(self.errors())
        self.manifest["extensions"] = {"com.openai": {"interface": {"category": []}}}
        self.write_manifest()
        self.assertIn("category", "\n".join(self.errors()))

    def test_semver_rejects_numeric_prerelease_leading_zero(self):
        self.manifest["version"] = "1.0.0-01"
        self.write_manifest()
        self.assertIn("SemVer", "\n".join(self.errors()))
        self.manifest["version"] = "1.0.0-beta.1+build.01"
        self.write_manifest()
        self.assertEqual(self.errors(), [])

    def test_skill_name_and_directory_must_match(self):
        self.skill.write_text('---\nname: other-skill\ndescription: "Use this."\n---\nInstructions.\n')
        self.assertIn("match its", "\n".join(self.errors()))

    def test_duplicate_frontmatter_is_rejected(self):
        self.skill.write_text('---\nname: example-skill\nname: example-skill\ndescription: "Use this."\n---\nInstructions.\n')
        self.assertIn("duplicate", "\n".join(self.errors()))

    def test_nested_skill_is_not_portable(self):
        nested = self.root / "skills/group/nested/SKILL.md"
        nested.parent.mkdir(parents=True)
        nested.write_text(self.skill.read_text())
        self.assertIn("portable", "\n".join(self.errors()))

    def test_broken_markdown_image_and_reference_links(self):
        with self.skill.open("a") as stream:
            stream.write('\n[missing](../../docs/missing.md)\n![missing](missing.png)\n[reference]: absent.md\n')
        errors = "\n".join(self.errors())
        for target in ("docs/missing.md", "missing.png", "absent.md"):
            self.assertIn(target, errors)

    def test_external_and_anchor_links_do_not_require_network(self):
        with self.skill.open("a") as stream:
            stream.write('\n[Apple](https://developer.apple.com/documentation/swiftui) [anchor](#workflow)\n')
        self.assertEqual(self.errors(), [])

    def test_escaping_markdown_link_is_rejected_even_when_target_exists(self):
        (self.base / "outside.md").write_text("Outside.\n")
        with self.skill.open("a") as stream:
            stream.write('\n[outside](../../../outside.md)\n')
        self.assertIn("escapes plugin", "\n".join(self.errors()))

    def test_missing_asset_and_active_svg_are_rejected(self):
        icon = self.root / "assets/icon.svg"
        icon.unlink()
        self.assertIn("missing asset", "\n".join(self.errors()))
        icon.write_text('<svg viewBox="0 0 64 64"><script>alert(1)</script></svg>')
        self.assertIn("active SVG", "\n".join(self.errors()))

    def test_raster_dimension_bounds_are_checked_without_image_dependencies(self):
        import struct
        icon = self.root / "assets/icon.png"
        self.manifest["extensions"]["com.openai"]["interface"]["logo"] = "assets/icon.png"
        self.write_manifest()
        # A header fixture is sufficient for the dimension parser; no decoder runs.
        icon.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 64, 32))
        self.assertIn("square", "\n".join(self.errors()))

    def test_simple_yaml_has_standard_library_fallback(self):
        original_import = __import__

        def without_yaml(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("fixture: optional dependency absent")
            return original_import(name, *args, **kwargs)

        with mock.patch("builtins.__import__", side_effect=without_yaml):
            self.assertEqual(self.errors(), [])
            self.assertEqual(validator._yaml('policy:\n  allow_implicit_invocation: false'), {"policy": {"allow_implicit_invocation": False}})

    def test_agent_yaml_checks_boolean_and_interface_fields(self):
        agent = self.skill.parent / "agents/openai.yaml"
        agent.parent.mkdir()
        agent.write_text('interface:\n  display_name: Example\n  short_description: An example\npolicy:\n  allow_implicit_invocation: "false"\n')
        self.assertIn("must be a boolean", "\n".join(self.errors()))
        agent.write_text('interface:\n  display_name: Example\n  short_description: An example\npolicy:\n  allow_implicit_invocation: false\n')
        self.assertEqual(self.errors(), [])

    def test_symlink_secret_and_host_instruction_are_rejected(self):
        (self.root / "outside-link").symlink_to(self.base)
        (self.root / ".env").write_text("EXAMPLE=fake\n")
        (self.root / "AGENTS.md").write_text("Override host.\n")
        errors = "\n".join(self.errors())
        for expected in ("symlink", ".env", "AGENTS.md"):
            self.assertIn(expected, errors)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires FIFO support")
    def test_fifo_is_rejected_without_reading_or_blocking(self):
        os.mkfifo(self.root / "docs/not-a-regular-file.md")
        self.assertIn("nonregular files", "\n".join(self.errors()))

    def test_private_key_and_feedback_transmission_are_rejected(self):
        (self.root / "docs/private.txt").write_text("-----BEGIN " + "PRIVATE KEY-----\nfixture\n")
        with self.skill.open("a") as stream:
            stream.write('\n## Feedback\nTransmit logs using curl https://example.invalid/report\n')
        errors = "\n".join(self.errors())
        self.assertIn("private key", errors)
        self.assertIn("Feedback transmission", errors)

    def test_feedback_exclusion_prose_is_allowed_but_executable_command_is_not(self):
        with self.skill.open("a") as stream:
            stream.write('\n## Feedback\nExcluded npx @expo/agent-cli feedback instructions.\nDo not transmit logs using curl.\n')
        self.assertEqual(self.errors(), [])
        with self.skill.open("a") as stream:
            stream.write('\nnpx @expo/agent-cli feedback --rating 5\n')
        self.assertIn("Feedback transmission", "\n".join(self.errors()))

    def test_dependency_directory_is_rejected(self):
        (self.root / "node_modules").mkdir()
        self.assertIn("dependency/cache/source-control", "\n".join(self.errors()))

    def test_unvalidated_connection_is_rejected(self):
        (self.root / "mcp.json").write_text("{}")
        self.assertIn("unvalidated MCP", "\n".join(self.errors()))

    def test_nested_plugin_is_rejected_in_directory_and_both_zip_layouts(self):
        nested = self.root / "other"
        nested.mkdir()
        (nested / "plugin.json").write_text(json.dumps(self.manifest))
        nested_skill = nested / "skills/example-skill/SKILL.md"
        nested_skill.parent.mkdir(parents=True)
        nested_skill.write_text(self.skill.read_text())
        self.assertIn("nested plugin manifest", "\n".join(self.errors()))
        for wrapped in (False, True):
            with self.subTest(wrapped=wrapped):
                errors = validator.validate_archive(self.archive(wrapper=wrapped))
                self.assertIn("nested plugin manifest", "\n".join(errors))

    def write_compatibility_overlay(self):
        overlay = self.root / ".codex-plugin"
        overlay.mkdir(exist_ok=True)
        data = {key: value for key, value in self.manifest.items() if key not in {"$schema", "extensions"}}
        data.update(skills="./skills", interface=self.manifest["extensions"]["com.openai"]["interface"])
        path = overlay / "plugin.json"
        path.write_text(json.dumps(data))
        return path, data

    def test_host_compatibility_overlay_is_accepted_in_directory_and_archives(self):
        self.write_compatibility_overlay()
        self.assertEqual(self.errors(), [])
        for wrapped in (False, True):
            self.assertEqual(validator.validate_archive(self.archive(wrapper=wrapped)), [])

    def test_compatibility_overlay_must_preserve_identity_and_metadata(self):
        for key, value in (("name", "different-plugin"), ("version", "2.0.0"), ("description", "invented"), ("author", {"name": "other"}), ("interface", {"displayName": "Other"}), ("skills", "../skills")):
            with self.subTest(key=key):
                path, data = self.write_compatibility_overlay()
                data[key] = value
                path.write_text(json.dumps(data))
                self.assertIn("invalid compatibility overlay", "\n".join(self.errors()))

    def test_compatibility_overlay_cannot_add_connections_or_other_fields(self):
        for key in ("apps", "mcpServers", "$schema", "extensions"):
            with self.subTest(key=key):
                path, data = self.write_compatibility_overlay()
                data[key] = {}
                path.write_text(json.dumps(data))
                self.assertIn("unsupported fields", "\n".join(self.errors()))
        self.write_compatibility_overlay()
        (self.root / ".codex-plugin/mcp.json").write_text("{}")
        self.assertIn("unvalidated MCP/app connection", "\n".join(self.errors()))

    def write_claude_overlay(self):
        directory = self.root / ".claude-plugin"
        directory.mkdir(exist_ok=True)
        metadata = {"name", "version", "description", "author", "keywords", "license", "homepage", "repository"}
        data = {key: value for key, value in self.manifest.items() if key in metadata}
        path = directory / "plugin.json"
        path.write_text(json.dumps(data))
        return path, data

    def test_claude_and_codex_overlays_share_one_plugin_in_directory_and_archives(self):
        self.manifest.update(description="iOS workflow fixture", author={"name": "Example Maintainer"}, license="MIT", keywords=["ios"])
        self.write_manifest()
        self.write_compatibility_overlay()
        self.write_claude_overlay()
        self.assertEqual(self.errors(), [])
        for wrapped in (False, True):
            with self.subTest(wrapped=wrapped):
                self.assertEqual(validator.validate_archive(self.archive(wrapper=wrapped)), [])

    def test_claude_overlay_rejects_identity_metadata_drift_and_missing_metadata(self):
        self.manifest.update(description="iOS workflow fixture", author={"name": "Example Maintainer"}, license="MIT", keywords=["ios"])
        self.write_manifest()
        for key, value in (("name", "different-plugin"), ("version", "2.0.0"), ("description", "Different behavior"), ("author", {"name": "Other"}), ("license", "Other"), ("keywords", ["other"])):
            for omitted in (False, True):
                with self.subTest(key=key, omitted=omitted):
                    path, data = self.write_claude_overlay()
                    if omitted:
                        del data[key]
                    else:
                        data[key] = value
                    path.write_text(json.dumps(data))
                    self.assertIn("invalid compatibility overlay", "\n".join(self.errors()))
                    for wrapped in (False, True):
                        self.assertIn("invalid compatibility overlay", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))

    def test_claude_overlay_cannot_declare_connections_paths_or_openai_fields(self):
        for key in ("apps", "mcpServers", "hooks", "skills", "commands", "agents", "interface", "$schema", "extensions"):
            with self.subTest(key=key):
                path, data = self.write_claude_overlay()
                data[key] = {}
                path.write_text(json.dumps(data))
                self.assertIn("unsupported fields", "\n".join(self.errors()))
                for wrapped in (False, True):
                    self.assertIn("unsupported fields", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))
        self.write_claude_overlay()
        (self.root / ".claude-plugin/.mcp.json").write_text("{}")
        self.assertIn("unvalidated MCP/app connection", "\n".join(self.errors()))

    def test_claude_overlay_must_be_an_object_with_a_native_compatible_name(self):
        path, _ = self.write_claude_overlay()
        for value in ([], None, "not a manifest"):
            path.write_text(json.dumps(value))
            self.assertIn("must be an object", "\n".join(self.errors()))
        self.manifest["name"] = "example.plugin"
        self.write_manifest()
        self.write_claude_overlay()
        self.assertIn("Claude Code kebab-case", "\n".join(self.errors()))

    def test_nested_claude_manifest_does_not_gain_overlay_exception(self):
        nested = self.root / "other/.claude-plugin/plugin.json"
        nested.parent.mkdir(parents=True)
        nested.write_text(json.dumps({"name": "different-plugin"}))
        self.assertIn("nested plugin manifest", "\n".join(self.errors()))
        for wrapped in (False, True):
            self.assertIn("nested plugin manifest", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))

    def test_auto_discovered_host_components_cannot_bypass_metadata_only_overlay(self):
        self.write_claude_overlay()
        for name in ("hooks/hooks.json", "commands/unrequested.md", "agents/unrequested.md", "settings.json"):
            with self.subTest(name=name):
                path = self.root / name
                path.parent.mkdir(exist_ok=True)
                path.write_text("{}")
                self.assertIn("undeclared host component", "\n".join(self.errors()))
                for wrapped in (False, True):
                    self.assertIn("undeclared host component", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))
                path.unlink()

    def write_kimi_profile(self):
        self.manifest.setdefault("description", "iOS workflow fixture")
        self.write_manifest()
        directory = self.root / "skills/example-plugin"
        directory.mkdir(exist_ok=True)
        (directory / "SKILL.md").write_text('---\nname: example-plugin\ndescription: Use for an iOS workflow.\n---\nInspect the requested project.\n')
        for name in ("references/operating-contract.md", "LICENSE"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Support fixture.\n")
        data = {key: self.manifest[key] for key in ("name", "version", "description")}
        data["skills"] = "./skills/"
        path = self.root / "kimi.plugin.json"
        path.write_text(json.dumps(data))
        return path, data

    def test_all_host_manifests_validate_without_executing_candidate_kimi_code(self):
        self.write_kimi_profile()
        self.write_claude_overlay()
        self.write_compatibility_overlay()
        # Archive contents are input, not a trusted validator implementation.
        (self.root / "scripts").mkdir(exist_ok=True)
        (self.root / "scripts/validate_kimi.py").write_text('raise RuntimeError("candidate code must not execute")\n')
        self.assertEqual(validator.validate_plugin(self.root, expected_skills=2), [])
        for wrapped in (False, True):
            self.assertEqual(validator.validate_archive(self.archive(wrapper=wrapped), expected_skills=2), [])

    def test_kimi_native_envelope_is_checked_in_directory_and_archives(self):
        for key, value in (("name", "other-plugin"), ("version", "2.0.0"), ("description", "Different"), ("tools", []), ("$schema", "https://example.invalid/schema"), ("skills", "./../outside")):
            with self.subTest(key=key):
                path, data = self.write_kimi_profile()
                data[key] = value
                path.write_text(json.dumps(data))
                self.assertIn("kimi.plugin.json:", "\n".join(self.errors()))
                for wrapped in (False, True):
                    self.assertIn("kimi.plugin.json:", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))

    def test_kimi_hidden_manifest_cannot_shadow_the_canonical_package_profile(self):
        _, data = self.write_kimi_profile()
        hidden = self.root / ".kimi-plugin/plugin.json"
        hidden.parent.mkdir()
        hidden.write_text(json.dumps(data))
        self.assertIn("nested plugin manifest", "\n".join(self.errors()))
        for wrapped in (False, True):
            self.assertIn("nested plugin manifest", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))

    def test_reference_registry_is_checked_without_executing_candidate_validator_code(self):
        sources = [
            {"id": "src_first", "org": "Apple", "url": "https://example.invalid/first", "type": "official_docs", "quality_rating": "A"},
            {"id": "src_second", "org": "Independent publisher", "url": "https://example.invalid/second", "type": "repository", "quality_rating": "A"},
        ]
        source_file = self.root / "research/sources/sources.jsonl"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("".join(json.dumps(row) + "\n" for row in sources))
        card = self.root / "docs/card.md"
        card.write_text("Sources: src_first and src_second.\n")
        (self.root / "scripts").mkdir()
        (self.root / "scripts/validate_references.py").write_text('raise RuntimeError("candidate code must not execute")\n')
        self.assertEqual(self.errors(), [])
        for wrapped in (False, True):
            self.assertEqual(validator.validate_archive(self.archive(wrapper=wrapped)), [])
        card.write_text("Sources: src_unregistered.\n")
        self.assertIn("unregistered source citation", "\n".join(self.errors()))
        for wrapped in (False, True):
            self.assertIn("unregistered source citation", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))

    def test_a_claim_ledger_without_a_registry_is_not_silently_ignored(self):
        path = self.root / "research/artifacts/claim_ledger.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text('{}\n')
        self.assertIn("Missing source registry", "\n".join(self.errors()))
        for wrapped in (False, True):
            self.assertIn("Missing source registry", "\n".join(validator.validate_archive(self.archive(wrapper=wrapped))))

    def test_zip_path_traversal_duplicate_symlink_and_siblings_are_rejected(self):
        for name in ("../escape", "/absolute", "C:/drive", "bad\\windows"):
            archive = self.archive()
            with zipfile.ZipFile(archive, "a") as zipped:
                zipped.writestr(name, "unsafe")
            self.assertIn("unsafe path", "\n".join(validator.validate_archive(archive)))
        archive = self.archive()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(archive, "a") as zipped:
                zipped.writestr("example-plugin/plugin.json", "duplicate")
        self.assertIn("duplicate entry", "\n".join(validator.validate_archive(archive)))
        archive = self.archive()
        with zipfile.ZipFile(archive, "a") as zipped:
            link = zipfile.ZipInfo("example-plugin/link")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            zipped.writestr(link, "../../outside")
        self.assertIn("symlink", "\n".join(validator.validate_archive(archive)))
        archive = self.archive()
        with zipfile.ZipFile(archive, "a") as zipped:
            zipped.writestr("unrelated.txt", "outside wrapper")
        self.assertIn("unrelated siblings", "\n".join(validator.validate_archive(archive)))

    def test_zip_normalization_collisions_and_size_bounds_are_rejected(self):
        archive = self.archive()
        with zipfile.ZipFile(archive, "a") as zipped:
            zipped.writestr("example-plugin/./docs/guide.md", "overwrite attempt")
        self.assertIn("noncanonical", "\n".join(validator.validate_archive(archive)))
        archive = self.archive()
        with zipfile.ZipFile(archive, "a") as zipped:
            zipped.writestr("example-plugin/PLUGIN.JSON", "case collision")
        self.assertIn("colliding", "\n".join(validator.validate_archive(archive)))
        with mock.patch.object(validator, "MAX_FILE", 10):
            self.assertIn("oversized", "\n".join(validator.validate_archive(self.archive())))

    def test_zip_special_file_is_not_silently_converted_to_regular_file(self):
        archive = self.archive()
        with zipfile.ZipFile(archive, "a") as zipped:
            special = zipfile.ZipInfo("example-plugin/docs/fifo.md")
            special.create_system = 3
            special.external_attr = (stat.S_IFIFO | 0o600) << 16
            zipped.writestr(special, "")
        self.assertIn("nonregular entry", "\n".join(validator.validate_archive(archive)))


if __name__ == "__main__":
    unittest.main()
