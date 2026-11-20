#!/usr/bin/env python3
"""Build and check host catalogs, or register one skill in a local project."""

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = "ultimate-ai-plugins"
TITLE = "Ultimate AI Plugins"
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
ENTRY_SKILLS = {
    "anti-slop-and-design-quality": "antislop",
    "apple-swift-ios-and-macos": "apple-platform-router",
    "creator-intelligence": "creator-research",
    "deepsec-agent": "deepsec-review",
    "doc-atlas": "repo-docs",
    "image-prompt-director": "image-prompts",
    "ios-development-studio": "ios-development",
    "ultimate-sdd": "orchestrator",
    "video-prompt-director": "video-prompts",
    "web-design-and-ui-systems": "web-design-router",
}
MANIFESTS = {
    "Claude Code": ".claude-plugin/plugin.json",
    "Codex": ".codex-plugin/plugin.json",
    "Kimi Code": "kimi.plugin.json",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def relative_path(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.exists():
        raise ValueError(f"{root.relative_to(ROOT)}: invalid path {value}")
    return path


def entry_file(root):
    skill = ENTRY_SKILLS.get(root.name, root.name)
    return relative_path(root, f"skills/{skill}/SKILL.md")


def check_manifest_paths(root, manifest):
    for key in ("skills", "commands", "agents", "hooks", "mcpServers", "apps",
                "systemPromptPath", "onboardingSkill"):
        values = manifest.get(key, [])
        if isinstance(values, str):
            values = [values]
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str):
                    relative_path(root, value)
    interface = manifest.get("interface", {})
    for key in ("logo", "composerIcon"):
        value = interface.get(key, "")
        if value.startswith("./"):
            relative_path(root, value)


def catalog():
    plugins = {}
    for root in sorted(path for path in (ROOT / "plugins").glob("*/*") if path.is_dir()):
        name = root.name
        data = read_json(root / "plugin.json")
        if name in plugins or data["name"] != name or data.get("$schema") != SCHEMA:
            raise ValueError(f"{root.relative_to(ROOT)}: invalid or duplicate plugin identity")
        entry_file(root)
        openai = data["extensions"]["com.openai"]
        check_manifest_paths(root, openai)
        for host, manifest_path in MANIFESTS.items():
            native = read_json(root / manifest_path)
            if (native["name"], native["version"]) != (name, data["version"]):
                raise ValueError(f"{name}: {host} manifest name or version differs")
            check_manifest_paths(root, native)
        for skill in sorted(root.glob("skills/*/SKILL.md")):
            header = skill.read_text(encoding="utf-8").split("---", 2)
            if (len(header) != 3 or header[0].strip()
                or not re.search(r"(?m)^description:", header[1])):
                raise ValueError(f"{skill.relative_to(ROOT)}: missing skill frontmatter")
        plugins[name] = (root, data)
    if not plugins:
        raise ValueError("catalog is empty")
    return plugins


def marketplace_files(plugins):
    codex = {
        "name": MARKETPLACE,
        "interface": {"displayName": TITLE},
        "plugins": [],
    }
    claude = {
        "name": MARKETPLACE,
        "owner": {"name": "Andrew Rodriguez"},
        "metadata": {"description": "Reusable skills and plugins for coding agents."},
        "plugins": [],
    }
    kimi = {"version": "2", "plugins": []}
    for name, (root, data) in plugins.items():
        source = "./" + root.relative_to(ROOT).as_posix()
        display = data["extensions"]["com.openai"]["interface"]["displayName"]
        category = root.parent.name.replace("-and-", " & ").replace("-", " ").title()
        codex["plugins"].append({
            "name": name,
            "source": {"source": "local", "path": source},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": category,
        })
        claude["plugins"].append({
            "name": name,
            "source": source,
            "description": data["description"],
            "category": category,
        })
        kimi["plugins"].append({"id": name, "displayName": display, "source": source})
    return {
        ".agents/plugins/marketplace.json": codex,
        ".claude-plugin/marketplace.json": claude,
        "kimi.marketplace.json": kimi,
    }


def register_skill(root, data, project):
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    route = f"ucp-{root.name}"
    destination = project / ".agents" / "skills" / route / "SKILL.md"
    if not destination.resolve().is_relative_to(project):
        raise ValueError(f"skill registration path leaves the project: {destination}")
    entry = entry_file(root)
    description = json.dumps(data["description"], ensure_ascii=False)
    body = (
        f"---\nname: {route}\ndescription: {description}\n---\n\n"
        f"Read the workflow at `{entry.as_posix()}` and follow it for this project. "
        f"Resolve its resources from the plugin root `{root.as_posix()}` and keep "
        "the project as the target for any changes. Use available host tools and "
        "report any missing connector or runtime needed by the workflow.\n"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.read_text(encoding="utf-8") == body:
        return destination
    with destination.open("x", encoding="utf-8", newline="\n") as output:
        output.write(body)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="regenerate the three marketplace indexes")
    commands.add_parser("check", help="check manifests, entry skills and catalog drift")
    register = commands.add_parser("register-skill", help="add an Agent Skills entry to a project")
    register.add_argument("plugin")
    register.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    try:
        plugins = catalog()
        if args.command == "register-skill":
            if args.plugin not in plugins:
                raise ValueError(f"unknown plugin: {args.plugin}")
            root, data = plugins[args.plugin]
            print(register_skill(root, data, args.project.resolve()))
            return
        for path, data in marketplace_files(plugins).items():
            file = ROOT / path
            contents = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            if args.command == "sync":
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(contents, encoding="utf-8")
            elif not file.is_file() or file.read_text(encoding="utf-8") != contents:
                raise ValueError(f"{path} is stale. Run python3 scripts/plugin_catalog.py sync")
        print(f"Catalog checks passed for {len(plugins)} plugins and three marketplaces")
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
