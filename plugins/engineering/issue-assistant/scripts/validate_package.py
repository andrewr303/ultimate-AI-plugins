#!/usr/bin/env python3
"""Validate local package structure; does not contact providers or validate LLM behavior.

Requires PyYAML in the maintainer environment. The offline workflow helper and its
unit tests continue to use only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


SKILLS = {"issue-assistant", "reconcile-issues", "grill-issue",
          "break-down-issue", "daily-issue-sync"}
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def validate(root: Path, *, archive_ready: bool = False) -> dict:
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("package validation requires PyYAML; helper/tests do not") from exc

    root = root.resolve()

    def read_yaml(text: str):
        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ValueError(f"invalid YAML: {exc}") from exc

    def contained(reference: str, parent: Path = root) -> Path:
        if not isinstance(reference, str) or not reference.strip():
            raise ValueError("package references must be nonempty strings")
        target = (parent / reference).resolve()
        if Path(reference).is_absolute() or not target.is_relative_to(root):
            raise ValueError(f"reference escapes package: {reference}")
        if not target.is_file():
            raise ValueError(f"missing package reference: {reference}")
        return target

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def read_json(path: Path):
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ValueError(f"nonfinite JSON value: {value}")))

    files = []
    for path in sorted(root.rglob("*")):
        cached = "__pycache__" in path.relative_to(root).parts or path.suffix == ".pyc"
        if cached and not archive_ready:
            continue
        files.append(path)
    for path in files:
        if path.is_symlink():
            raise ValueError(f"symlink in package: {path.relative_to(root)}")
        if any(part in {"__pycache__", ".git", "node_modules", ".venv"}
               for part in path.relative_to(root).parts) or path.suffix in {".pyc", ".zip"}:
            raise ValueError(f"build/cache artifact in package: {path.relative_to(root)}")

    manifest = read_json(root / "plugin.json")
    if not isinstance(manifest, dict) or manifest.get("$schema") != SCHEMA:
        raise ValueError("portable manifest schema is missing or invalid")
    if manifest.get("name") != "issue-assistant":
        raise ValueError("plugin identity changed")
    if not re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", manifest.get("version", "")):
        raise ValueError("version must use the existing numeric SemVer scheme")
    claude_manifest = read_json(root / ".claude-plugin" / "plugin.json")
    for key in ("name", "version", "description"):
        if not isinstance(claude_manifest, dict) or claude_manifest.get(key) != manifest.get(key):
            raise ValueError(f".claude-plugin/plugin.json {key} must match plugin.json")
    if any(key in manifest for key in ("skills", "interface", "mcpServers", "apps")):
        raise ValueError("host-specific settings must be under extensions.com.openai")
    host = manifest["extensions"]["com.openai"]
    interface = host["interface"]
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            raise ValueError(f"interface.{key} must be a nonblank string")
    if len(interface["shortDescription"]) > 30:
        raise ValueError("shortDescription exceeds 30 characters")
    if interface["category"] != "Developer Tools":
        raise ValueError("preserve the existing Developer Tools category")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or any(not isinstance(x, str) or not x.strip() for x in capabilities):
        raise ValueError("capabilities must be an array of nonblank strings")
    prompts = interface.get("defaultPrompt")
    if isinstance(prompts, str):
        prompts = [prompts]
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or any(
            not isinstance(x, str) or not x.strip() for x in prompts):
        raise ValueError("defaultPrompt must be a string or up to three strings")
    for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
        if key in interface:
            contained(interface[key])
    bindings = read_json(contained(host["apps"]))["apps"]
    if set(bindings) != {"linear", "github"}:
        raise ValueError("preserve the existing connected-app set")
    for binding in bindings.values():
        if not re.fullmatch(r"(?:asdk_app_|connector_|templated_apps_)[A-Za-z0-9][A-Za-z0-9_-]*", binding.get("id", "")):
            raise ValueError("invalid app binding ID")
        if "optional" in binding and type(binding["optional"]) is not bool:
            raise ValueError("optional app setting must be a boolean")

    discovered = set()
    for skill_file in sorted((root / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        if skill_file.stat().st_size > 1024 * 1024 or not text.startswith("---\n"):
            raise ValueError(f"invalid skill frontmatter: {skill_file}")
        parts = text.split("---", 2)
        if len(parts) != 3:
            raise ValueError(f"unterminated frontmatter: {skill_file}")
        frontmatter = read_yaml(parts[1])
        if not isinstance(frontmatter, dict):
            raise ValueError(f"skill frontmatter must be an object: {skill_file}")
        name = frontmatter.get("name")
        if name != skill_file.parent.name or name in discovered:
            raise ValueError(f"skill name mismatch or duplicate: {skill_file}")
        if not isinstance(frontmatter.get("description"), str) or not frontmatter["description"].strip():
            raise ValueError(f"missing skill description: {name}")
        discovered.add(name)
        agent_file = skill_file.parent / "agents/openai.yaml"
        if agent_file.exists():
            agent = read_yaml(agent_file.read_text(encoding="utf-8"))
            if not isinstance(agent, dict):
                raise ValueError(f"agent metadata must be an object: {name}")
            presentation = agent.get("interface", {})
            for field in ("display_name", "short_description"):
                if not isinstance(presentation.get(field), str) or not presentation[field].strip():
                    raise ValueError(f"invalid agent interface: {name}/{field}")
            policy = agent.get("policy", {})
            if not isinstance(policy, dict) or set(policy) - {"products", "allow_implicit_invocation"}:
                raise ValueError(f"unsupported agent policy: {name}")
            implicit = policy.get("allow_implicit_invocation")
            if implicit is not None and type(implicit) is not bool:
                raise ValueError(f"invocation policy must be a boolean: {name}")
            if name == "daily-issue-sync" and implicit is not False:
                raise ValueError("unattended sync must remain explicitly invoked")
    if discovered != SKILLS:
        raise ValueError(f"expected skill entrypoints differ: {sorted(discovered)}")

    links = 0
    for path in files:
        if not path.is_file():
            continue
        if path.suffix == ".json":
            read_json(path)
        elif path.suffix == ".jsonl":
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    json.loads(line, object_pairs_hook=unique_object)
        elif path.suffix == ".md":
            for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
                if ":" in target or target.startswith("#"):
                    continue
                contained(target.split("#", 1)[0], path.parent)
                links += 1
    return {"valid": True, "version": manifest["version"], "skills": sorted(discovered),
            "connected_apps": sorted(bindings), "relative_links_checked": links}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive-ready", action="store_true", help="also reject generated Python caches")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, archive_ready=args.archive_ready), sort_keys=True))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
