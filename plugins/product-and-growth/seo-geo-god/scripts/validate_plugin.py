#!/usr/bin/env python3
"""Offline structural and integrity checks for the SEO-GEO-god plugin package.

Standard library only (no PyYAML): skill and agent frontmatter and agents/openai.yaml are read
with a deliberately restricted YAML subset. This is not a host installation test and not a
factual review of the content.

Usage: python3 -I scripts/validate_plugin.py [ROOT] [--archive ZIP]
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import os
import re
import stat
import tempfile
import unicodedata
import zipfile
import zlib
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

SCOPE = "offline structural and integrity checks; no host installation or factual verification"
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
CATEGORIES = {"Business & Operations", "Communication", "Creativity", "Data & Analytics",
              "Developer Tools", "Education & Research", "Entertainment", "Finance", "Healthcare",
              "Other", "Productivity", "Scientific Research", "Security", "Travel"}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")
PLUGIN_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOOL = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\([^()]*\))?$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
MAX_MEMBERS = 10000
MAX_DESCRIPTION = 1024
MAX_MANIFEST_DESCRIPTION = 300
EXCLUDE_NAMES = {"__pycache__", ".git", ".DS_Store", ".seo-geo-god", ".pytest_cache"}
FORBIDDEN_PATHS = ("hooks", ".mcp.json", "bin")
FORBIDDEN_KEYS = ("hooks", "mcpServers", "apps")
OVERLAYS = (".claude-plugin/plugin.json", ".codex-plugin/plugin.json")
REQUIRED_FILES = ("plugin.json",) + OVERLAYS + ("LICENSE", "NOTICE.md", "README.md", "CHANGELOG.md", "VALIDATION.md")
LICENSE_FILES = {
    "licenses/claude-seo-MIT.txt": "MIT License",
    "licenses/geo-seo-claude-MIT.txt": "MIT License",
    "licenses/open-seo-mcp-skills-MIT.txt": "MIT License",
    "licenses/eGEOagents-MIT.txt": "MIT License",
    "licenses/notfair-plugin-MIT.txt": "MIT License",
    "licenses/geoptimize-MIT.txt": "MIT License",
    "licenses/aaron-marketing-skills-Apache-2.0.txt": "Apache License",
}
# Analyzer fixtures are deliberately defective inputs, not package documentation.
LINK_EXEMPT_DIRS = ("tests/fixtures",)
LINK_SCHEMES = {"http", "https", "mailto"}
SKILL_KEYS = {"name", "description"}
AGENT_KEYS = {"name", "description", "tools"}
OPENAI_KEYS = {"interface": {"display_name", "short_description", "default_prompt", "icon_small", "icon_large", "brand_color"},
               "policy": {"allow_implicit_invocation", "products"}}
PRODUCTS = {"CHAT", "CODEX", "HERMES"}
SCENARIO_STATUS = "reviewer fixtures; no agent-host routing execution claimed"


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def excluded(path):
    path = PurePosixPath(Path(path).as_posix())
    return any(part in EXCLUDE_NAMES for part in path.parts) or path.suffix == ".pyc"


def valid_date(value):
    if not isinstance(value, str) or not ISO_DATE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


# ---------------------------------------------------------------- restricted YAML subset

class YamlSubsetError(ValueError):
    """Input is outside the restricted YAML subset this validator accepts."""


KEY_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]+(.*))?$")
DOUBLE = re.compile(r'"((?:[^"\\]|\\.)*)"(?:[ \t]+#.*)?')
SINGLE = re.compile(r"'((?:[^']|'')*)'(?:[ \t]+#.*)?")
FLOW_SEQUENCE = re.compile(r"\[(.*)\](?:[ \t]+#.*)?")
INTEGER = re.compile(r"[-+]?[0-9]+")
FLOAT = re.compile(r"[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?")


def scalar(text, in_sequence=False):
    """Parse one restricted YAML value; return (value, quoted)."""
    text = text.strip()
    if not text or text.startswith("#"):
        return None, False
    if text[0] in "|>":
        raise YamlSubsetError("block scalars (| or >) are not supported; use a one-line quoted string")
    if text[0] == '"':
        match = DOUBLE.fullmatch(text)
        if not match:
            raise YamlSubsetError("unterminated or malformed double-quoted string")
        try:
            return json.loads('"' + match.group(1) + '"'), True
        except ValueError:
            raise YamlSubsetError("unsupported escape or control character in double-quoted string") from None
    if text[0] == "'":
        match = SINGLE.fullmatch(text)
        if not match:
            raise YamlSubsetError("unterminated or malformed single-quoted string")
        return match.group(1).replace("''", "'"), True
    if text[0] == "[" and not in_sequence:
        match = FLOW_SEQUENCE.fullmatch(text)
        if not match:
            raise YamlSubsetError("malformed flow sequence")
        inner = match.group(1).strip()
        return ([scalar(item, True)[0] for item in inner.split(",")] if inner else []), False
    if text[0] in "[]{}&*!%@`,#" or text[:2] in ("- ", "? ", ": ") or text in ("-", "?"):
        raise YamlSubsetError(f"unsupported YAML syntax: {text[:40]}")
    if " #" in text or "\t#" in text:
        text = re.split(r"[ \t]#", text, maxsplit=1)[0].rstrip()
    if ": " in text or text.endswith(":") or "\t" in text:
        raise YamlSubsetError("plain value contains ': ' or a tab; quote the value")
    if text in ("true", "True", "TRUE", "false", "False", "FALSE"):
        return text.lower() == "true", False
    if text in ("null", "Null", "NULL", "~"):
        return None, False
    if INTEGER.fullmatch(text):
        return int(text), False
    if FLOAT.fullmatch(text):
        return float(text), False
    return text, False


def parse_mapping(text, depth):
    """Parse `key: value` lines (depth 1) or one level of nested mappings (depth 2).

    Returns (data, quoted) where quoted maps top-level scalar keys to whether the value was quoted.
    """
    data, quoted, current, indent = {}, {}, None, None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw[:-1] if raw.endswith("\r") else raw
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        width = len(line) - len(line.lstrip(" \t"))
        if "\t" in line[:width]:
            raise YamlSubsetError(f"line {number}: tab indentation is not allowed")
        if width and (depth == 1 or current is None):
            raise YamlSubsetError(f"line {number}: unexpected indentation (multi-line and nested values are not supported)")
        match = KEY_LINE.match(line[width:].rstrip())
        if not match:
            raise YamlSubsetError(f"line {number}: expected 'key: value'")
        key, rest = match.group(1), (match.group(2) or "").strip()
        if width == 0:
            if key in data:
                raise YamlSubsetError(f"line {number}: duplicate key {key}")
            if depth == 2 and (not rest or rest.startswith("#")):
                data[key], current, indent = {}, key, None
                continue
            data[key], quoted[key] = scalar(rest)
            current = None
            continue
        if indent is None:
            indent = width
        elif width != indent:
            raise YamlSubsetError(f"line {number}: inconsistent indentation")
        if key in data[current]:
            raise YamlSubsetError(f"line {number}: duplicate key {current}.{key}")
        if not rest or rest.startswith("#"):
            raise YamlSubsetError(f"line {number}: nesting deeper than two levels is not supported")
        data[current][key] = scalar(rest)[0]
    return data, quoted


def split_frontmatter(text):
    """Return (frontmatter_text or None, body) for a leading `---` block."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r \t") == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    return None, text


# ---------------------------------------------------------------- Markdown links and anchors

FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
CODE_SPAN = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
INLINE_LINK = re.compile(r"(?<!\\)!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(\s*(<[^<>\n]*>|[^\s()<>]*(?:\([^\s()]*\)[^\s()<>]*)*)"
                         r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
REFERENCE_DEF = re.compile(r"^ {0,3}\[([^\]^\n][^\]\n]*)\]:[ \t]*(<[^<>\n]*>|\S+)", re.M)
HTML_ID = re.compile(r"<[A-Za-z][^>]*?\s(?:id|name)\s*=\s*[\"']([^\"']+)[\"']")


def block_text(text):
    """Blank frontmatter, fenced code and HTML comments; keep line positions."""
    lines = text.split("\n")
    start = 0
    if split_frontmatter(text)[0] is not None:
        start = next(i for i in range(1, len(lines)) if lines[i].rstrip("\r \t") == "---") + 1
    out, fence = [""] * start, None
    for line in lines[start:]:
        line = line.rstrip("\r")
        match = FENCE.match(line)
        if fence is None:
            if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
                fence = match.group(1)
                out.append("")
            else:
                out.append(line)
            continue
        if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
            fence = None
        out.append("")
    joined = "\n".join(out)
    return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), joined, flags=re.S)


def prose_text(text):
    return CODE_SPAN.sub("", block_text(text))


def _plain_heading(value):
    value = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"(?<![^\W_])_+|_+(?![^\W_])", "", value)  # emphasis underscores, not snake_case
    return html.unescape(value)


def github_slug(heading, strip=True):
    """GitHub-style heading slug: rendered text, lowercased, punctuation removed, spaces to '-'."""
    pieces, position = [], 0
    for match in CODE_SPAN.finditer(heading):
        code = match.group(2)
        if len(code) > 1 and code[0] == code[-1] == " " and code.strip():
            code = code[1:-1]
        pieces += [_plain_heading(heading[position:match.start()]), code]
        position = match.end()
    pieces.append(_plain_heading(heading[position:]))
    text = "".join(pieces)
    text = (text.strip() if strip else text).lower()
    kept = (c for c in text if c in " -" or unicodedata.category(c)[0] in "LMN" or unicodedata.category(c) == "Pc")
    return "".join(kept).replace(" ", "-")


def markdown_anchors(text):
    """Heading slugs (with GitHub's -1, -2 suffixes) plus explicit id/name attributes."""
    anchors, occurrences, previous = set(), {}, ""

    def add(raw):
        for variant in dict.fromkeys((github_slug(raw), github_slug(raw, strip=False))):
            slug = variant
            while slug in occurrences:
                occurrences[variant] += 1
                slug = f"{variant}-{occurrences[variant]}"
            occurrences[slug] = 0
            anchors.add(slug)

    for line in block_text(text).split("\n"):
        match = ATX.match(line)
        if match:
            add(re.sub(r"(?:^|[ \t]+)#+$", "", match.group(2) or ""))
            previous = ""
            continue
        if (SETEXT.match(line) and previous.strip() and not previous.startswith("    ")
                and not re.match(r"^\s*(?:[-*+>|#]|\d+[.)])", previous)):
            add(previous.strip())
            previous = ""
            continue
        previous = line
    anchors.update(HTML_ID.findall(prose_text(text)))
    return anchors


# ---------------------------------------------------------------- tree walk

def scan_tree(root):
    """Return (files, problems): sorted POSIX paths of package files and (path, message) issues."""
    root, files, problems = Path(root), [], []
    for current, dirs, names in os.walk(root, followlinks=False):
        base = Path(current)
        kept = []
        for name in sorted(dirs):
            if name in EXCLUDE_NAMES:
                continue
            if (base / name).is_symlink():
                problems.append((base / name, "symlinks are not permitted"))
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(names):
            path = base / name
            if name in EXCLUDE_NAMES or name.endswith(".pyc"):
                continue
            info = os.lstat(path)
            if stat.S_ISLNK(info.st_mode):
                problems.append((path, "symlinks are not permitted"))
            elif not stat.S_ISREG(info.st_mode):
                problems.append((path, "only regular files and directories are permitted"))
            else:
                if info.st_size > MAX_FILE_BYTES:
                    problems.append((path, "file exceeds the 2 MiB size cap"))
                files.append(path.relative_to(root).as_posix())
    return sorted(files), problems


def package_files(root):
    return scan_tree(Path(root).resolve())[0]


class Validator:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.files = []
        self.skill_names = set()
        self.anchor_cache = {}
        self.stats = {"files": 0, "bytes": 0, "skills": 0, "agent_briefs": 0, "markdown_files": 0,
                      "links_checked": 0, "data_files": 0, "schema_files": 0, "scenario_cases": 0}

    def error(self, path, message):
        path = Path(path)
        try:
            label = path.relative_to(self.root).as_posix()
        except ValueError:
            label = str(path)
        self.errors.append({"path": label or ".", "message": message})

    def contained(self, path):
        return Path(path).resolve().is_relative_to(self.root)

    def read(self, path):
        path = Path(path)
        if not self.contained(path):
            self.error(path, "file resolves outside package")
            return None
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                self.error(path, "file exceeds the 2 MiB size cap")
                return None
            return path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError) as exc:
            self.error(path, f"cannot read UTF-8: {exc}")
            return None

    def load_json(self, path):
        value = self.read(path)
        if value is None:
            return None
        try:
            return json.loads(value, object_pairs_hook=unique_pairs)
        except (ValueError, TypeError, RecursionError) as exc:
            self.error(path, f"invalid JSON: {exc}")
            return None

    @staticmethod
    def nonblank(value):
        return isinstance(value, str) and bool(value.strip())

    def asset(self, owner, base, reference, directory=False):
        """A manifest/metadata path that must stay inside the package and exist."""
        if not self.nonblank(reference):
            self.error(owner, "local path must be a nonblank string")
            return
        try:
            parsed = urlsplit(reference)
        except ValueError:
            self.error(owner, f"invalid local path: {reference}")
            return
        decoded = unquote(parsed.path)
        if (parsed.scheme or parsed.netloc or parsed.fragment or "\\" in decoded or "\x00" in decoded
                or Path(decoded).is_absolute()):
            self.error(owner, f"path must be a contained relative local path: {reference}")
            return
        target = (Path(base) / decoded).resolve()
        if not target.is_relative_to(self.root):
            self.error(owner, f"path escapes package: {reference}")
        elif not (target.is_dir() if directory else target.is_file()):
            self.error(owner, f"missing local {'directory' if directory else 'file'}: {reference}")

    # ---------------------------------------------------------------- package-level checks

    def walk(self):
        self.files, problems = scan_tree(self.root)
        for path, message in problems:
            self.error(path, message)
        self.stats["files"] = len(self.files)
        self.stats["bytes"] = sum((self.root / rel).stat().st_size for rel in self.files)

    def forbidden(self):
        for name in FORBIDDEN_PATHS:
            path = self.root / name
            if path.exists() or path.is_symlink():
                self.error(path, "forbidden path: the package ships no hooks, MCP server config or bin/ executables")

    def required(self):
        for rel in REQUIRED_FILES + tuple(LICENSE_FILES):
            if not (self.root / rel).is_file():
                self.error(self.root / rel, "required file is missing")
        for rel, marker in LICENSE_FILES.items():
            text = self.read(self.root / rel) if (self.root / rel).is_file() else None
            if text is not None and marker not in text:
                self.error(self.root / rel, f"license text does not contain '{marker}'")
        text = self.read(self.root / "LICENSE") if (self.root / "LICENSE").is_file() else None
        if text is not None and ("MIT License" not in text or "Permission is hereby granted" not in text):
            self.error(self.root / "LICENSE", "LICENSE must contain the MIT license text")

    def interface(self, path, interface, label):
        if not isinstance(interface, dict):
            self.error(path, f"{label} must be an object")
            return
        for key in ("displayName", "shortDescription"):
            if not self.nonblank(interface.get(key)):
                self.error(path, f"{label}.{key} must be a nonblank string")
        for key in ("longDescription", "developerName"):
            if key in interface and not self.nonblank(interface[key]):
                self.error(path, f"{label}.{key} must be a nonblank string")
        if isinstance(interface.get("shortDescription"), str) and len(interface["shortDescription"]) > 30:
            self.error(path, f"{label}.shortDescription exceeds 30 characters")
        if "category" in interface and not (isinstance(interface["category"], str) and interface["category"] in CATEGORIES):
            self.error(path, f"unsupported {label}.category")
        capabilities = interface.get("capabilities", [])
        if not isinstance(capabilities, list) or not all(self.nonblank(x) for x in capabilities):
            self.error(path, f"{label}.capabilities must be an array of nonblank strings")
        if "defaultPrompt" in interface:
            prompt = interface["defaultPrompt"]
            if not (self.nonblank(prompt) or isinstance(prompt, list) and 1 <= len(prompt) <= 3
                    and all(self.nonblank(x) for x in prompt)):
                self.error(path, f"{label}.defaultPrompt must be a nonblank string or one to three strings")
        for key in ("brandColor", "brandColorDark"):
            if key in interface and not (isinstance(interface[key], str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", interface[key])):
                self.error(path, f"invalid {label}.{key}")
        for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
            if key in interface:
                self.asset(path, self.root, interface[key])

    def common_fields(self, path, data):
        for key in FORBIDDEN_KEYS:
            if key in data:
                self.error(path, f"forbidden manifest key: {key}")
        for key in ("description", "homepage", "repository", "license"):
            if key in data and not self.nonblank(data[key]):
                self.error(path, f"{key} must be a nonblank string")
        if "author" in data and not isinstance(data["author"], dict):
            self.error(path, "author must be an object")
        keywords = data.get("keywords", [])
        if not isinstance(keywords, list) or not all(self.nonblank(x) for x in keywords):
            self.error(path, "keywords must be an array of nonblank strings")

    def manifest(self):
        path = self.root / "plugin.json"
        data = self.load_json(path) if path.is_file() else None
        if not isinstance(data, dict):
            self.error(path, "portable manifest must be a JSON object")
            return
        if data.get("$schema") != SCHEMA:
            self.error(path, "portable schema declaration is missing or incorrect")
        name = data.get("name")
        if not isinstance(name, str) or len(name) > 64 or not PLUGIN_NAME.fullmatch(name) or "--" in name or ".." in name:
            self.error(path, "invalid plugin name")
        if not isinstance(data.get("version"), str) or not SEMVER.fullmatch(data["version"]):
            self.error(path, "version must be strict SemVer")
        if not self.nonblank(data.get("description")):
            self.error(path, "description must be a nonblank string")
        elif len(data["description"]) > MAX_MANIFEST_DESCRIPTION:
            self.error(path, f"description exceeds {MAX_MANIFEST_DESCRIPTION} characters")
        self.common_fields(path, data)
        for key in ("skills", "interface"):
            if key in data:
                self.error(path, f"{key} is not a portable root manifest field")
        extensions = data.get("extensions", {})
        openai = extensions.get("com.openai", {}) if isinstance(extensions, dict) else None
        portable_interface = openai.get("interface") if isinstance(openai, dict) else None
        if not isinstance(openai, dict):
            self.error(path, "extensions and extensions.com.openai must be objects")
        elif portable_interface is not None:
            self.interface(path, portable_interface, "extensions.com.openai.interface")
        for overlay in OVERLAYS:
            candidate = self.root / overlay
            other = self.load_json(candidate) if candidate.is_file() else None
            if not isinstance(other, dict):
                self.error(candidate, "compatibility manifest must be a JSON object")
                continue
            for key in ("name", "version"):
                if other.get(key) != data.get(key):
                    self.error(candidate, f"{key} disagrees with portable manifest")
            if "license" in other and other["license"] != data.get("license"):
                self.error(candidate, "license disagrees with portable manifest")
            self.common_fields(candidate, other)
            if overlay.startswith(".codex-plugin"):
                skills = other.get("skills")
                if not isinstance(skills, str) or "\x00" in skills or (self.root / skills).resolve() != self.root / "skills":
                    self.error(candidate, "skills must point to ./skills")
                self.interface(candidate, other.get("interface"), "interface")
                if portable_interface is not None and other.get("interface") != portable_interface:
                    self.error(candidate, "interface disagrees with plugin.json extensions.com.openai.interface")

    # ---------------------------------------------------------------- skills, agents, docs, data

    def frontmatter(self, path):
        text = self.read(path)
        if text is None:
            return None, None
        raw, _ = split_frontmatter(text)
        if raw is None:
            self.error(path, "file must start with a --- frontmatter block")
            return None, None
        try:
            return parse_mapping(raw, depth=1)
        except YamlSubsetError as exc:
            self.error(path, f"frontmatter: {exc}")
            return None, None

    def described(self, path, data, expected_name):
        name = data.get("name")
        if not self.nonblank(name) or name != expected_name:
            self.error(path, "name must match its directory or file name")
        elif len(name) > 64 or not KEBAB.fullmatch(name):
            self.error(path, "name must be kebab-case and at most 64 characters")
        description = data.get("description")
        if not self.nonblank(description):
            self.error(path, "description must be a nonblank string")
        elif len(description) > MAX_DESCRIPTION:
            self.error(path, f"description exceeds {MAX_DESCRIPTION} characters")

    def skills(self):
        skills_dir = self.root / "skills"
        paths = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []
        if not paths:
            self.error(skills_dir, "package contains no skills")
        for path in paths:
            if path.parent.name.startswith("."):
                self.error(path, "hidden skill directory is not portable")
            data, quoted = self.frontmatter(path)
            if data is None:
                continue
            if set(data) != SKILL_KEYS:
                self.error(path, "skill frontmatter keys must be exactly name and description; found "
                           + ", ".join(sorted(data)))
            self.described(path, data, path.parent.name)
            if "description" in data and not quoted.get("description"):
                self.error(path, "skill description must be a one-line quoted string")
            if isinstance(data.get("name"), str):
                self.skill_names.add(data["name"])
            metadata = path.parent / "agents/openai.yaml"
            if metadata.is_file():
                self.openai_yaml(metadata, path.parent)
            else:
                self.error(metadata, "skill is missing agents/openai.yaml")
            self.stats["skills"] += 1
        for rel in self.files:
            parts = rel.split("/")
            if parts[-1] == "SKILL.md" and parts[0] == "skills" and len(parts) != 3:
                self.error(self.root / rel, "skill must be one directory below skills/")

    def openai_yaml(self, path, skill_dir):
        text = self.read(path)
        if text is None:
            return
        try:
            data = parse_mapping(text, depth=2)[0]
        except YamlSubsetError as exc:
            self.error(path, f"agents/openai.yaml: {exc}")
            return
        for key in sorted(set(data) - set(OPENAI_KEYS)):
            self.error(path, f"unsupported top-level key: {key}")
        interface, policy = data.get("interface"), data.get("policy", {})
        if not isinstance(interface, dict):
            self.error(path, "interface must be a mapping")
            interface = {}
        for key in sorted(set(interface) - OPENAI_KEYS["interface"]):
            self.error(path, f"unsupported interface key: {key}")
        for key in ("display_name", "short_description"):
            if not self.nonblank(interface.get(key)):
                self.error(path, f"interface.{key} is required")
        if "default_prompt" in interface and not self.nonblank(interface["default_prompt"]):
            self.error(path, "interface.default_prompt must be one nonblank string")
        if "brand_color" in interface and not (isinstance(interface["brand_color"], str)
                                               and re.fullmatch(r"#[0-9A-Fa-f]{6}", interface["brand_color"])):
            self.error(path, "invalid interface.brand_color")
        for key in ("icon_small", "icon_large"):
            if key in interface:
                self.asset(path, skill_dir, interface[key])
        if not isinstance(policy, dict):
            self.error(path, "policy must be a mapping")
            return
        for key in sorted(set(policy) - OPENAI_KEYS["policy"]):
            self.error(path, f"unsupported policy key: {key}")
        if policy.get("allow_implicit_invocation") is not None and not isinstance(policy["allow_implicit_invocation"], bool):
            self.error(path, "policy.allow_implicit_invocation must be boolean")
        products = policy.get("products")
        if products is not None and not (isinstance(products, list) and all(isinstance(x, str) and x in PRODUCTS for x in products)):
            self.error(path, "policy.products must list CHAT, CODEX or HERMES")

    def agents(self):
        agents_dir = self.root / "agents"
        for path in sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []:
            if path.name == "README.md":
                continue
            data, _ = self.frontmatter(path)
            if data is None:
                continue
            for key in sorted(set(data) - AGENT_KEYS):
                self.error(path, f"unsupported agent frontmatter key: {key}")
            self.described(path, data, path.stem)
            if "tools" in data:
                tools = data["tools"]
                items = tools if isinstance(tools, list) else tools.split(",") if isinstance(tools, str) else None
                if not items or not all(isinstance(x, str) and TOOL.fullmatch(x.strip()) for x in items):
                    self.error(path, "tools must be a comma-separated list of tool names")
            self.stats["agent_briefs"] += 1

    def anchors_of(self, path):
        key = Path(path).resolve()
        if key not in self.anchor_cache:
            text = self.read(key)
            self.anchor_cache[key] = markdown_anchors(text) if text is not None else set()
        return self.anchor_cache[key]

    def link(self, owner, reference, line):
        self.stats["links_checked"] += 1
        where = f"line {line}: "
        if reference.startswith("<") and reference.endswith(">"):
            reference = reference[1:-1]
        if not reference.strip():
            self.error(owner, where + "empty link destination")
            return
        try:
            parsed = urlsplit(reference)
        except ValueError as exc:
            self.error(owner, where + f"invalid link: {exc}")
            return
        if parsed.scheme:
            if parsed.scheme.lower() not in LINK_SCHEMES:
                self.error(owner, where + f"unsupported link scheme: {reference}")
            return
        if parsed.netloc:
            return  # protocol-relative external link
        decoded, fragment = unquote(parsed.path), unquote(parsed.fragment)
        if "\\" in decoded or "\x00" in decoded or Path(decoded).is_absolute():
            self.error(owner, where + f"unsafe local link: {reference}")
            return
        target = (Path(owner).parent / decoded).resolve() if decoded else Path(owner).resolve()
        if not target.is_relative_to(self.root):
            self.error(owner, where + f"link escapes package: {reference}")
        elif target.is_dir() and not fragment:
            return
        elif not target.is_file():
            self.error(owner, where + f"missing local file: {reference}")
        elif fragment and target.suffix.lower() in (".md", ".markdown") and fragment not in self.anchors_of(target):
            self.error(owner, where + f"missing local anchor: {reference}")

    def markdown(self):
        for rel in self.files:
            if not rel.endswith(".md") or any(rel.startswith(d + "/") for d in LINK_EXEMPT_DIRS):
                continue
            path = self.root / rel
            text = self.read(path)
            if text is None:
                continue
            prose = prose_text(text)
            for pattern, group in ((INLINE_LINK, 1), (REFERENCE_DEF, 2)):
                for match in pattern.finditer(prose):
                    self.link(path, match.group(group), prose.count("\n", 0, match.start()) + 1)
            self.stats["markdown_files"] += 1

    def data(self):
        for path in sorted((self.root / "data").glob("*.json")):
            value = self.load_json(path)
            if not isinstance(value, dict):
                if value is not None:
                    self.error(path, "data file must be a JSON object")
            elif not valid_date(value.get("as_of")):
                self.error(path, "as_of must be an ISO date (YYYY-MM-DD)")
            self.stats["data_files"] += 1
        for path in sorted((self.root / "schemas").glob("*.json")):
            value = self.load_json(path)
            if not isinstance(value, dict):
                if value is not None:
                    self.error(path, "schema file must be a JSON object")
            elif not self.nonblank(value.get("$schema")):
                self.error(path, "schema file must declare $schema")
            elif "as_of" in value and not valid_date(value["as_of"]):
                self.error(path, "as_of must be an ISO date (YYYY-MM-DD)")
            self.stats["schema_files"] += 1
        for rel in self.files:
            if rel.endswith(".json") and rel.split("/")[0] in ("templates", "examples"):
                self.load_json(self.root / rel)

    def scenarios(self):
        path = self.root / "tests/skill-scenarios.json"
        data = self.load_json(path) if path.is_file() else None
        if not isinstance(data, dict):
            self.error(path, "skill scenarios must be a JSON object")
            return
        if data.get("status") != SCENARIO_STATUS:
            self.error(path, "scenario status must identify reviewer fixtures without claiming agent-host execution")
        cases = data.get("cases")
        if not isinstance(cases, list) or not cases:
            self.error(path, "skill scenarios need a nonempty cases array")
            return
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
            if not isinstance(expected, list) or not all(isinstance(x, str) and x in self.skill_names for x in expected):
                self.error(path, f"scenario {index} expected_skills must be an array of existing skill names")
            elif len(set(expected)) != len(expected):
                self.error(path, f"scenario {index} repeats an expected skill")
        self.stats["scenario_cases"] = len(cases)

    def result(self):
        return {"ok": not self.errors, "scope": SCOPE, "errors": self.errors, "stats": self.stats}

    def run(self):
        if not self.root.is_dir():
            self.error(self.root, "package directory does not exist")
            return self.result()
        self.walk()
        if self.errors:  # unsafe tree: do not read further
            return self.result()
        for check in (self.forbidden, self.required, self.manifest, self.skills, self.agents,
                      self.markdown, self.data, self.scenarios):
            check()
        return self.result()


def validate_directory(root):
    return Validator(root).run()


def validate_archive(archive):
    archive = Path(archive)

    def failed(messages, stats):
        return {"ok": False, "scope": SCOPE, "errors": [{"path": str(archive), "message": m} for m in messages], "stats": stats}

    try:
        with zipfile.ZipFile(archive) as bundle:
            infos = bundle.infolist()
            errors, names, folded, files, total = [], set(), set(), [], 0
            if len(infos) > MAX_MEMBERS:
                errors.append("archive contains too many members")
            for entry in infos:
                name = entry.filename
                parts = name.rstrip("/").split("/")
                if (not name or name.startswith(("/", "\\")) or "\\" in name or "\x00" in name
                        or any(part in ("", ".", "..") or ":" in part for part in parts)):
                    errors.append(f"unsafe archive path: {name}")
                if name in names:
                    errors.append(f"duplicate archive member: {name}")
                elif name.casefold() in folded:
                    errors.append(f"case-insensitive duplicate archive member: {name}")
                names.add(name)
                folded.add(name.casefold())
                if any(part in EXCLUDE_NAMES for part in parts) or name.endswith(".pyc"):
                    errors.append(f"excluded path in archive: {name}")
                mode = entry.external_attr >> 16
                if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                    errors.append(f"nonregular archive member: {name}")
                if entry.flag_bits & 1:
                    errors.append(f"encrypted archive member: {name}")
                total += entry.file_size
                if not entry.is_dir():
                    files.append(name)
            if total > MAX_ARCHIVE_BYTES:
                errors.append("uncompressed archive exceeds 128 MiB")
            wrapper = ""
            if "plugin.json" in files:
                if any(re.fullmatch(r"[^/]+/plugin\.json", x) and x.split("/")[0] not in (".claude-plugin", ".codex-plugin") for x in files):
                    errors.append("archive contains multiple plugin roots")
            else:
                roots = {x.split("/")[0] for x in files}
                if len(roots) != 1:
                    errors.append("archive must contain one plugin with at most one wrapper directory")
                else:
                    wrapper = next(iter(roots))
                    if wrapper + "/plugin.json" not in files:
                        errors.append("plugin manifest missing or nested under extra wrapper directories")
            if errors:
                return failed(errors, {"archive_members": len(infos)})
            with tempfile.TemporaryDirectory(prefix="seo-geo-god-validate-") as directory:
                bundle.extractall(directory)
                root = Path(directory) / wrapper
                result = validate_directory(root)
                result["stats"]["archive_members"] = len(infos)
                if wrapper:
                    try:
                        name = json.loads((root / "plugin.json").read_text(encoding="utf-8")).get("name")
                    except (OSError, ValueError, AttributeError):
                        name = None
                    if name is not None and wrapper != name:
                        result["errors"].append({"path": str(archive), "message": f"archive wrapper directory {wrapper!r} must equal the plugin name"})
                        result["ok"] = False
                return result
    except (OSError, ValueError, EOFError, RuntimeError, zipfile.BadZipFile, zlib.error) as exc:
        return failed([f"cannot read archive: {exc}"], {})


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline structural and integrity checks for this plugin package.")
    parser.add_argument("root", nargs="?", default=".", help="plugin root directory (default: .)")
    parser.add_argument("--archive", type=Path, help="validate a packaged ZIP instead of a directory")
    args = parser.parse_args(argv)
    result = validate_archive(args.archive) if args.archive else validate_directory(args.root)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
