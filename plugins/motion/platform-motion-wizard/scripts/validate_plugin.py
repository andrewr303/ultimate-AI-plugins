#!/usr/bin/env python3
"""Offline package integrity checks; not a host validator or factual research gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import yaml

SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
CATEGORIES = {"Business & Operations", "Communication", "Creativity", "Data & Analytics",
              "Developer Tools", "Education & Research", "Entertainment", "Finance", "Healthcare",
              "Other", "Productivity", "Scientific Research", "Security", "Travel"}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")
NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
HEX = re.compile(r"^[0-9a-f]{64}$")
PRODUCTS = {"CHAT", "CODEX", "HERMES"}
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
EXCLUDE_NAMES = {"__pycache__", ".git", ".DS_Store"}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


class UniqueLoader(yaml.SafeLoader):
    pass


def yaml_mapping(loader, node):
    loader.flatten_mapping(node)
    return unique_pairs(loader.construct_pairs(node))


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping)


def excluded(path):
    return any(part in EXCLUDE_NAMES for part in path.parts) or path.suffix == ".pyc"


def stripped_markdown(value):
    """Ignore fenced examples and inline code when resolving prose links."""
    lines, fence = [], None
    for line in value.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            lines.append("")
        else:
            lines.append("" if fence else re.sub(r"(`+).*?\1", "", line))
    return "\n".join(lines)


def markdown_anchors(value):
    anchors, counts = set(), {}
    for line in stripped_markdown(value).splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match.group(1)).lower()
        heading = "".join(c for c in heading if c in " -_" or unicodedata.category(c)[0] in "LN")
        slug = heading.replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    anchors.update(re.findall(r'\b(?:id|name)=["\']([^"\']+)["\']', value))
    return anchors


class Validator:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.stats = {"skills": 0, "markdown_files": 0, "sources": 0, "claims": 0, "preserved_files": 0}

    def error(self, path, message):
        path = Path(path)
        try:
            label = str(path.relative_to(self.root))
        except ValueError:
            label = str(path)
        self.errors.append({"path": label, "message": message})

    def read(self, path):
        if not Path(path).resolve().is_relative_to(self.root):
            self.error(path, "file resolves outside package")
            return None
        try:
            return Path(path).read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError) as exc:
            self.error(path, f"cannot read UTF-8: {exc}")
            return None

    def json(self, path):
        value = self.read(path)
        if value is None:
            return None
        try:
            return json.loads(value, object_pairs_hook=unique_pairs)
        except (ValueError, TypeError) as exc:
            self.error(path, f"invalid JSON: {exc}")
            return None

    def yaml(self, value, path):
        try:
            return yaml.load(value, Loader=UniqueLoader)
        except (ValueError, TypeError, yaml.YAMLError) as exc:
            self.error(path, f"invalid YAML: {exc}")
            return None

    @staticmethod
    def nonblank(value):
        return isinstance(value, str) and bool(value.strip())

    def local(self, base, reference, owner, anchor=False):
        if not isinstance(reference, str) or not reference.strip():
            self.error(owner, "local file reference must be a nonblank string")
            return
        reference = reference.strip("<>")
        try:
            parsed = urlsplit(reference)
        except ValueError as exc:
            self.error(owner, f"invalid reference: {exc}")
            return
        if parsed.scheme or parsed.netloc:
            if anchor:
                return  # External Markdown destinations are outside this offline check.
            self.error(owner, f"asset must be a contained local path: {reference}")
            return
        decoded = unquote(parsed.path)
        if "\\" in decoded or "\x00" in decoded or Path(decoded).is_absolute():
            self.error(owner, f"unsafe local reference: {reference}")
            return
        target = Path(owner).resolve() if anchor and not decoded else (Path(base) / decoded).resolve()
        if not target.is_relative_to(self.root):
            self.error(owner, f"reference escapes package: {reference}")
        elif not target.is_file():
            self.error(owner, f"missing local file: {reference}")
        elif anchor and parsed.fragment:
            text = self.read(target)
            if text is not None and unquote(parsed.fragment) not in markdown_anchors(text):
                self.error(owner, f"missing local anchor: {reference}")

    def manifest(self):
        path = self.root / "plugin.json"
        data = self.json(path)
        if not isinstance(data, dict):
            self.error(path, "manifest must be an object")
            return
        if data.get("$schema") != SCHEMA:
            self.error(path, "portable schema declaration is missing or incorrect")
        name = data.get("name")
        if not isinstance(name, str) or len(name) > 64 or not NAME.fullmatch(name) or "--" in name or ".." in name:
            self.error(path, "invalid plugin name")
        if not isinstance(data.get("version"), str) or not SEMVER.fullmatch(data["version"]):
            self.error(path, "version must be strict SemVer")
        for key in ("description", "homepage", "repository", "license"):
            if key in data and not isinstance(data[key], str):
                self.error(path, f"{key} must be a string")
        if "author" in data and not isinstance(data["author"], dict):
            self.error(path, "author must be an object")
        if "keywords" in data and (not isinstance(data["keywords"], list) or not all(isinstance(x, str) for x in data["keywords"])):
            self.error(path, "keywords must be an array of strings")
        for key in ("skills", "mcpServers", "apps", "interface"):
            if key in data:
                self.error(path, f"{key} is not a portable root manifest field")
        extensions = data.get("extensions", {})
        if not isinstance(extensions, dict):
            self.error(path, "extensions must be an object")
            extensions = {}
        openai = extensions.get("com.openai", {})
        if not isinstance(openai, dict):
            self.error(path, "extensions.com.openai must be an object")
            openai = {}
        interface = openai.get("interface", {})
        if not isinstance(interface, dict):
            self.error(path, "interface must be an object")
            interface = {}
        for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            if key in interface and not self.nonblank(interface[key]):
                self.error(path, f"interface.{key} must be a nonblank string")
        if isinstance(interface.get("shortDescription"), str) and len(interface["shortDescription"]) > 30:
            self.error(path, "interface.shortDescription exceeds 30 characters")
        if "category" in interface and (not isinstance(interface["category"], str) or interface["category"] not in CATEGORIES):
            self.error(path, "unsupported interface category")
        if "capabilities" in interface and (not isinstance(interface["capabilities"], list) or not all(self.nonblank(x) for x in interface["capabilities"])):
            self.error(path, "interface.capabilities must be an array of nonblank strings")
        if "defaultPrompt" in interface:
            prompt = interface["defaultPrompt"]
            if not (self.nonblank(prompt) or isinstance(prompt, list) and 1 <= len(prompt) <= 3 and all(self.nonblank(x) for x in prompt)):
                self.error(path, "defaultPrompt must be a nonblank string or one to three strings")
        for key in ("brandColor", "brandColorDark"):
            if key in interface and (not isinstance(interface[key], str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", interface[key])):
                self.error(path, f"invalid {key}")
        for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
            if key in interface:
                self.local(self.root, interface[key], path)
        for overlay in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            candidate = self.root / overlay
            if candidate.exists():
                compatibility = self.json(candidate)
                if not isinstance(compatibility, dict):
                    self.error(candidate, "compatibility manifest must be an object")
                else:
                    for key in ("name", "version"):
                        if compatibility.get(key) != data.get(key):
                            self.error(candidate, f"{key} disagrees with portable manifest")

    def agent(self, path, skill_root):
        value = self.read(path)
        data = self.yaml(value, path) if value is not None else None
        if not isinstance(data, dict):
            self.error(path, "agent metadata must be a YAML object")
            return
        interface = data.get("interface")
        if interface is not None:
            if not isinstance(interface, dict):
                self.error(path, "agent interface must be an object")
            else:
                for key in ("display_name", "short_description"):
                    if not self.nonblank(interface.get(key)):
                        self.error(path, f"agent interface.{key} is required")
                if "default_prompt" in interface and not self.nonblank(interface["default_prompt"]):
                    self.error(path, "default_prompt must be one nonblank string")
                if "brand_color" in interface and (not isinstance(interface["brand_color"], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", interface["brand_color"])):
                    self.error(path, "invalid agent brand_color")
                for key in ("icon_small", "icon_large"):
                    if key in interface:
                        self.local(skill_root, interface[key], path)
        policy = data.get("policy", {})
        if not isinstance(policy, dict):
            self.error(path, "policy must be an object")
        else:
            if set(policy) - {"allow_implicit_invocation", "products"}:
                self.error(path, "unknown policy fields")
            implicit = policy.get("allow_implicit_invocation")
            if implicit is not None and not isinstance(implicit, bool):
                self.error(path, "allow_implicit_invocation must be boolean or null")
            products = policy.get("products")
            if products is not None and (not isinstance(products, list) or not all(isinstance(x, str) and x in PRODUCTS for x in products)):
                self.error(path, "products must use CHAT, CODEX, HERMES or be omitted/null")
        if "dependencies" in data and (not isinstance(data["dependencies"], dict) or set(data["dependencies"]) - {"tools"}):
            self.error(path, "dependencies supports only tools")

    def skills(self):
        names = set()
        paths = sorted((self.root / "skills").glob("*/SKILL.md"))
        if not paths:
            self.error(self.root / "skills", "skills-only package contains no usable skills")
        for path in paths:
            if path.parent.name.startswith("."):
                self.error(path, "hidden skill directory is not portable")
            if path.stat().st_size > 1024 * 1024:
                self.error(path, "skill exceeds 1 MiB")
            value = self.read(path)
            if value is None:
                continue
            match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", value, re.S)
            if not match:
                self.error(path, "skill must start with YAML frontmatter")
                continue
            data = self.yaml(match.group(1), path)
            if not isinstance(data, dict):
                self.error(path, "skill frontmatter must be an object")
                continue
            name = data.get("name")
            if not self.nonblank(name) or name != path.parent.name:
                self.error(path, "skill name must match its directory")
            if isinstance(name, str):
                if name in names:
                    self.error(path, "duplicate skill name")
                names.add(name)
            if not self.nonblank(data.get("description")):
                self.error(path, "skill description must be a nonblank string")
            agent = path.parent / "agents/openai.yaml"
            if agent.exists():
                self.agent(agent, path.parent)
            self.stats["skills"] += 1
        for path in (self.root / "skills").rglob("SKILL.md"):
            if path not in paths:
                self.error(path, "skill must be one directory below skills/")

    def markdown(self):
        for path in sorted(self.root.rglob("*.md")):
            value = self.read(path)
            if value is None:
                continue
            value = stripped_markdown(value)
            for match in re.finditer(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", value):
                self.local(path.parent, match.group(1), path, anchor=True)
            definitions = dict(re.findall(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)", value, re.M))
            for reference in definitions.values():
                self.local(path.parent, reference, path, anchor=True)
            self.stats["markdown_files"] += 1

    def provenance(self):
        path = self.root / "provenance/original-files.json"
        data = self.json(path)
        if not isinstance(data, dict) or not isinstance(data.get("files"), list) or not data["files"]:
            self.error(path, "provenance needs a nonempty files array")
            return
        if not isinstance(data.get("archive_sha256"), str) or not HEX.fullmatch(data["archive_sha256"]):
            self.error(path, "archive_sha256 must be a SHA-256 digest")
        seen = set()
        for record in data["files"]:
            if not isinstance(record, dict):
                self.error(path, "invalid preserved-file record")
                continue
            target = record.get("preserved_path")
            if not self.nonblank(record.get("source_path")) or not self.nonblank(target):
                self.error(path, "source_path and preserved_path are required")
                continue
            if target in seen:
                self.error(path, "duplicate preserved_path")
            seen.add(target)
            self.local(self.root, target, path)
            file_path = (self.root / target).resolve()
            if file_path.is_relative_to(self.root) and file_path.is_file():
                raw = file_path.read_bytes()
                if record.get("sha256") != hashlib.sha256(raw).hexdigest():
                    self.error(path, f"preserved bytes changed: {target}")
                if isinstance(record.get("size_bytes"), bool) or record.get("size_bytes") != len(raw):
                    self.error(path, f"preserved size disagrees: {target}")
            self.stats["preserved_files"] += 1

    def jsonl(self, path):
        value = self.read(path)
        result = []
        if value is None:
            return result
        for line_number, line in enumerate(value.splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line, object_pairs_hook=unique_pairs)
                if not isinstance(item, dict):
                    raise ValueError("record is not an object")
                result.append(item)
            except (ValueError, TypeError) as exc:
                self.error(path, f"invalid JSONL at line {line_number}: {exc}")
        return result

    def research(self):
        source_paths = sorted((self.root / "research").rglob("sources.jsonl"))
        claim_paths = sorted((self.root / "research").rglob("claim_ledger.jsonl"))
        if not source_paths or not claim_paths:
            self.error(self.root / "research", "manual research source and claim ledgers are required")
        sources = {}
        for path in source_paths:
            for source in self.jsonl(path):
                identity = source.get("id")
                if not self.nonblank(identity) or identity in sources:
                    self.error(path, "source id missing or duplicated")
                    continue
                sources[identity] = source
                for field in ("url", "org", "type"):
                    if not self.nonblank(source.get(field)):
                        self.error(path, f"source {identity} missing {field}")
                if not isinstance(source.get("quality_rating"), str) or source["quality_rating"] not in {"A", "B", "C", "D", "E"}:
                    self.error(path, f"source {identity} has invalid quality_rating")
        seen = set()
        for path in claim_paths:
            for claim in self.jsonl(path):
                identity = claim.get("claim_id")
                if not self.nonblank(identity) or identity in seen:
                    self.error(path, "claim_id missing or duplicated")
                    continue
                seen.add(identity)
                if not self.nonblank(claim.get("text")):
                    self.error(path, f"claim {identity} missing text")
                if (not isinstance(claim.get("risk"), str) or claim["risk"] not in {"normal", "high"}
                    or not isinstance(claim.get("claim_type"), str) or claim["claim_type"] not in {"descriptive", "numeric", "legal", "causal", "executable"}):
                    self.error(path, f"claim {identity} has invalid risk or claim_type")
                status = claim.get("review_status")
                if not isinstance(status, str) or status not in {"manually_supported", "unresolved", "refuted"}:
                    self.error(path, f"claim {identity} has invalid or missing review_status")
                if claim.get("claim_type") in ("numeric", "legal", "causal") and claim.get("risk") != "high":
                    self.error(path, f"claim {identity} requires high risk for numeric, legal, or causal claims")
                ids = claim.get("source_ids")
                if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x in sources for x in ids):
                    self.error(path, f"claim {identity} has unregistered or missing source_ids")
                    continue
                if claim.get("claim_type") == "executable":
                    proof = claim.get("execution_proof")
                    if not isinstance(proof, dict) or not all(self.nonblank(proof.get(k)) for k in ("script", "output", "env", "verdict")) or proof["verdict"] not in {"confirmed", "refuted", "partial"}:
                        self.error(path, f"claim {identity} needs execution_proof")
                    elif status == "manually_supported" and proof["verdict"] != "confirmed":
                        self.error(path, f"supported executable claim {identity} requires confirmed execution_proof")
                elif status == "manually_supported" and len({sources[x]["org"] for x in ids if isinstance(sources[x].get("org"), str)}) < 2:
                    self.error(path, f"claim {identity} lacks independent source organizations")
                if claim.get("risk") == "high":
                    counter = claim.get("counter_search")
                    urls = {source["url"] for source in sources.values() if isinstance(source.get("url"), str)}
                    if not isinstance(counter, dict) or not all(self.nonblank(counter.get(k)) for k in ("query", "summary")) or not isinstance(counter.get("urls"), list) or not counter["urls"] or not all(isinstance(u, str) and u in urls for u in counter["urls"]):
                        self.error(path, f"high-risk claim {identity} needs registered counter_search")
                    if claim.get("review_status") == "manually_supported":
                        source_types = {sources[x]["type"] for x in ids if isinstance(sources[x].get("type"), str)}
                        primary = {"repository", "api", "official_docs", "standards_document", "official_release"}
                        if len(source_types) < 2 or not source_types.intersection(primary) or not any(sources[x].get("quality_rating") in ("A", "B") for x in ids):
                            self.error(path, f"high-risk claim {identity} lacks primary, strong, or diverse source types")
        for path in self.root.rglob("verified_claims.json"):
            self.error(path, "manual-mode package must not imply an automated verified-claims result")
        self.stats.update(sources=len(sources), claims=len(seen))

    def scenarios(self):
        path = self.root / "tests/skill-scenarios.json"
        data = self.json(path)
        if not isinstance(data, dict):
            self.error(path, "skill scenarios must be an object")
            return
        if data.get("status") != "reviewer fixtures; no agent-host routing execution claimed":
            self.error(path, "scenario status must identify reviewer fixtures without claiming agent-host execution")
        cases = data.get("cases")
        if not isinstance(cases, list) or not cases:
            self.error(path, "skill scenarios need a nonempty cases array")
            return
        skills = {skill.parent.name for skill in (self.root / "skills").glob("*/SKILL.md")}
        seen = set()
        for index, case in enumerate(cases, 1):
            if not isinstance(case, dict):
                self.error(path, f"scenario {index} must be an object")
                continue
            identity = case.get("id")
            if not self.nonblank(identity) or identity in seen:
                self.error(path, f"scenario {index} has missing or duplicate id")
            else:
                seen.add(identity)
            for field in ("prompt", "acceptance"):
                if not self.nonblank(case.get(field)):
                    self.error(path, f"scenario {index} needs nonblank {field}")
            expected = case.get("expected_skills")
            if not isinstance(expected, list) or not all(isinstance(skill, str) and skill in skills for skill in expected):
                self.error(path, f"scenario {index} expected_skills must be an array of existing skill names")
            elif len(set(expected)) != len(expected):
                self.error(path, f"scenario {index} repeats an expected skill")
        self.stats["scenario_cases"] = len(cases)

    def run(self):
        if not self.root.is_dir():
            self.error(self.root, "package directory does not exist")
        else:
            for path in self.root.rglob("*"):
                if path.is_symlink():
                    self.error(path, "symlinks are not permitted")
                elif not path.is_dir() and not path.is_file():
                    self.error(path, "only regular files and directories are permitted")
            if self.errors:
                return {"ok": False, "scope": "offline structural and integrity checks; no host installation or factual research verification", "errors": self.errors, "stats": self.stats}
            self.manifest()
            self.skills()
            self.markdown()
            self.provenance()
            self.research()
            self.scenarios()
        return {"ok": not self.errors, "scope": "offline structural and integrity checks; no host installation or factual research verification", "errors": self.errors, "stats": self.stats}


def validate_directory(root):
    return Validator(root).run()


def validate_archive(archive):
    errors = []
    try:
        with zipfile.ZipFile(archive) as bundle:
            infos = bundle.infolist()
            names, files, total = set(), [], 0
            if len(infos) > 10000:
                errors.append("archive contains too many members")
            for entry in infos:
                name = entry.filename
                parts = PurePosixPath(name).parts
                unsafe = (not name or name.startswith(("/", "\\")) or "\\" in name or "\x00" in name
                          or any(x in {".", ".."} or ":" in x for x in name.rstrip("/").split("/"))
                          or any(not x for x in name.rstrip("/").split("/")))
                if unsafe:
                    errors.append(f"unsafe archive path: {name}")
                if name in names:
                    errors.append(f"duplicate archive member: {name}")
                names.add(name)
                mode = entry.external_attr >> 16
                if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR}:
                    errors.append(f"nonregular archive member: {name}")
                if entry.flag_bits & 1:
                    errors.append(f"encrypted archive member: {name}")
                total += entry.file_size
                if not entry.is_dir():
                    files.append(name)
            if total > MAX_ARCHIVE_BYTES:
                errors.append("uncompressed archive exceeds 128 MiB")
            wrapper = ""
            if "plugin.json" not in files:
                roots = {PurePosixPath(x).parts[0] for x in files if PurePosixPath(x).parts}
                if len(roots) != 1:
                    errors.append("archive must contain one plugin with at most one wrapper")
                else:
                    wrapper = next(iter(roots))
                    if wrapper + "/plugin.json" not in files:
                        errors.append("plugin manifest missing or nested under extra wrappers")
            else:
                # Another wrapped portable plugin cannot coexist with a root plugin.
                if any(re.fullmatch(r"[^/]+/plugin\.json", x) and x.split("/")[0] not in {".claude-plugin", ".codex-plugin"} for x in files):
                    errors.append("archive contains multiple plugin roots")
            if errors:
                return {"ok": False, "scope": "offline archive structure", "errors": [{"path": str(archive), "message": x} for x in errors], "stats": {"members": len(infos)}}
            with tempfile.TemporaryDirectory(prefix="platform-motion-validate-") as directory:
                bundle.extractall(directory)
                result = validate_directory(Path(directory) / wrapper)
                result["stats"]["archive_members"] = len(infos)
                return result
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        return {"ok": False, "scope": "offline archive structure", "errors": [{"path": str(archive), "message": str(exc)}], "stats": {}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--json", action="store_true", help="JSON is also the default output")
    args = parser.parse_args()
    result = validate_archive(args.archive) if args.archive else validate_directory(args.root)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
