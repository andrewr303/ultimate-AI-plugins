#!/usr/bin/env python3
"""Offline structural and prose checks for the liquid-glass-studio package.

Checks manifests, skill and brief frontmatter, per-skill openai.yaml metadata,
relative Markdown links and anchors, research JSON/JSONL syntax, and the house
prose gate (no em or en dashes, no banned words) on authored Markdown.
With --archive it first checks ZIP safety, then reruns every check on an
extracted copy.

This is a package integrity checker. It does not install the plugin in a host,
and it does not verify factual claims.

Exit codes: 0 all checks passed (warnings allowed), 1 at least one check
failed, 2 the checks could not run (missing directory, unreadable archive,
missing PyYAML, bad arguments).
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without PyYAML
    yaml = None

SCHEMA_URL = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
PLUGIN_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
CATEGORIES = {
    "Business & Operations", "Communication", "Creativity", "Data & Analytics",
    "Developer Tools", "Education & Research", "Entertainment", "Finance", "Healthcare",
    "Other", "Productivity", "Scientific Research", "Security", "Travel",
}
SHORT_DESCRIPTION_MAX = 30
SKILL_DESCRIPTION_MAX = 1024
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 5000
EXCLUDED_PARTS = {"__pycache__", ".git", ".DS_Store", "node_modules", ".pytest_cache"}

# Prose gate scope: authored Markdown. research/ is exempt (it holds survey
# output and quoted evidence) but its JSON and JSONL files must parse.
PROSE_DIRS = ("skills", "references", "agents", "commands", "templates", "examples", "docs")
PROSE_ROOT_FILES = ("README.md", "NOTICE.md", "VALIDATION.md")

# House banned-word list (PLAN.md). Each entry maps a display word to the
# whole-word forms that count. Matching is case-insensitive.
BANNED_WORDS = {
    "delve": ("delve", "delves", "delved", "delving"),
    "tapestry": ("tapestry", "tapestries"),
    "vibrant": ("vibrant",),
    "pivotal": ("pivotal",),
    "crucial": ("crucial", "crucially"),
    "foster": ("foster", "fosters", "fostered", "fostering"),
    "bolster": ("bolster", "bolsters", "bolstered", "bolstering"),
    "garner": ("garner", "garners", "garnered", "garnering"),
    "underscore": ("underscore", "underscores", "underscored", "underscoring"),
    "nuanced": ("nuanced",),
    "multifaceted": ("multifaceted",),
    "intricate": ("intricate", "intricately"),
    "meticulous": ("meticulous", "meticulously"),
    "harness": ("harness", "harnesses", "harnessed", "harnessing"),
    "illuminate": ("illuminate", "illuminates", "illuminated", "illuminating"),
    "realm": ("realm", "realms"),
    "robust": ("robust", "robustly", "robustness"),
    "holistic": ("holistic", "holistically"),
    "seamless": ("seamless", "seamlessly"),
    "streamlined": ("streamlined",),
    "nestled": ("nestled",),
    "renowned": ("renowned",),
    "groundbreaking": ("groundbreaking",),
    "comprehensive": ("comprehensive", "comprehensively"),
    "moreover": ("moreover",),
    "furthermore": ("furthermore",),
    "encompassing": ("encompassing",),
    "cultivating": ("cultivating",),
    "showcasing": ("showcasing",),
    "embodies": ("embodies",),
    "epitomizes": ("epitomizes",),
    "spearheading": ("spearheading",),
    "interplay": ("interplay",),
    "indelible": ("indelible",),
    "endeavor": ("endeavor", "endeavors", "endeavour", "endeavours"),
    "advent": ("advent",),
}
# Words that are banned only in one sense; the checker cannot tell the sense
# apart, so it reports them as warnings for a person to judge.
WARNING_WORDS = {
    "landscape": ("landscape", "landscapes"),
    "leverage": ("leverage", "leverages", "leveraged", "leveraging"),
}
OPENER_WORDS = ("additionally",)  # banned only when it opens a sentence


def _word_pattern(forms):
    return re.compile(r"(?<![\w-])(" + "|".join(sorted(forms, key=len, reverse=True)) + r")(?![\w-])", re.I)


BANNED_PATTERNS = {word: _word_pattern(forms) for word, forms in BANNED_WORDS.items()}
WARNING_PATTERNS = {word: _word_pattern(forms) for word, forms in WARNING_WORDS.items()}
OPENER_PATTERN = re.compile(
    r"(?:^|[.!?:]\s+|^\s*(?:[-*+]|\d+[.)])\s+|^\s*>\s*|^\s*#+\s+)(" + "|".join(OPENER_WORDS) + r")\b",
    re.I,
)
DASHES = {"\u2014": "em dash", "\u2013": "en dash"}
CURLY_QUOTES = re.compile("[\u2018\u2019\u201c\u201d]")


# --------------------------------------------------------------------------
# YAML helpers
# --------------------------------------------------------------------------

def _make_loader():
    class UniqueKeyLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node, deep=False):
        loader.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key: {key!r}", key_node.start_mark)
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return UniqueKeyLoader


FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


# --------------------------------------------------------------------------
# Markdown helpers
# --------------------------------------------------------------------------

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
HTML_CODE = re.compile(r"<code>.*?</code>", re.I)


def strip_fences(text):
    """Blank out fenced code blocks, keeping line numbers stable."""
    out, fence = [], None
    for line in text.splitlines():
        match = FENCE.match(line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not line.strip()[len(token):].strip():
                fence = None
            out.append("")
        else:
            out.append("" if fence else line)
    return out


def strip_code(text):
    """Return lines with fenced blocks and inline code spans removed."""
    return [HTML_CODE.sub("", INLINE_CODE.sub("", line)) for line in strip_fences(text)]


def heading_slugs(text):
    """GitHub-style anchors for every heading, plus explicit id/name attributes."""
    slugs, counts = set(), {}
    for line in strip_fences(text):
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", match.group(1))  # links keep their text
        heading = re.sub(r"<[^>]+>", "", heading).lower()
        heading = "".join(ch for ch in heading if ch in " -_" or unicodedata.category(ch)[0] in "LN")
        slug = heading.replace(" ", "-")
        seen = counts.get(slug, 0)
        counts[slug] = seen + 1
        slugs.add(slug if seen == 0 else f"{slug}-{seen}")
    slugs.update(re.findall(r"""\b(?:id|name)=["']([^"']+)["']""", text))
    return slugs


INLINE_LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
REFERENCE_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")
URL_TOKEN = re.compile(r"\b(?:https?|ftp|mailto):[^\s)>\]]+|www\.[^\s)>\]]+", re.I)


# --------------------------------------------------------------------------
# Validator
# --------------------------------------------------------------------------

class Validator:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.warnings = []
        self.stats = {"skills": 0, "agents": 0, "commands": 0, "markdown_files": 0,
                      "prose_files": 0, "links": 0, "research_records": 0}
        self.loader = _make_loader()

    # -- reporting ---------------------------------------------------------
    def _label(self, path):
        path = Path(path)
        try:
            return path.resolve().relative_to(self.root).as_posix() or "."
        except ValueError:
            return str(path)

    def error(self, path, message, line=None):
        self.errors.append({"path": self._label(path), "line": line, "message": message})

    def warn(self, path, message, line=None):
        self.warnings.append({"path": self._label(path), "line": line, "message": message})

    # -- readers -----------------------------------------------------------
    def files(self, pattern):
        for path in sorted(self.root.glob(pattern)):
            rel = path.relative_to(self.root)
            if not any(part in EXCLUDED_PARTS for part in rel.parts) and path.is_file():
                yield path

    def read_text(self, path):
        try:
            return Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            self.error(path, f"cannot read as UTF-8: {exc}")
            return None

    def read_json(self, path):
        text = self.read_text(path)
        if text is None:
            return None
        try:
            return json.loads(text, object_pairs_hook=_reject_duplicates)
        except ValueError as exc:
            self.error(path, f"invalid JSON: {exc}")
            return None

    def parse_yaml(self, text, path):
        try:
            return yaml.load(text, Loader=self.loader)
        except yaml.YAMLError as exc:
            self.error(path, f"invalid YAML: {exc}".splitlines()[0])
            return None

    def frontmatter(self, path, kind):
        text = self.read_text(path)
        if text is None:
            return None
        match = FRONTMATTER.match(text)
        if not match:
            self.error(path, f"{kind} must start with YAML frontmatter between --- lines", 1)
            return None
        data = self.parse_yaml(match.group(1), path)
        if not isinstance(data, dict):
            self.error(path, f"{kind} frontmatter must be a mapping", 1)
            return None
        return data

    @staticmethod
    def nonblank(value):
        return isinstance(value, str) and bool(value.strip())

    def contained_file(self, base, reference, owner, what):
        """Check that a manifest asset path is relative, contained, and exists."""
        if not self.nonblank(reference):
            self.error(owner, f"{what} must be a nonblank relative path")
            return
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc or reference.startswith("/") or "\\" in reference:
            self.error(owner, f"{what} must be a relative path inside the package: {reference}")
            return
        target = (Path(base) / unquote(parsed.path)).resolve()
        if not _inside(target, self.root):
            self.error(owner, f"{what} escapes the package: {reference}")
        elif not target.is_file():
            self.error(owner, f"{what} file is missing: {reference}")

    # -- checks ------------------------------------------------------------
    def check_tree(self):
        for path in self.root.rglob("*"):
            rel = path.relative_to(self.root)
            if any(part in EXCLUDED_PARTS for part in rel.parts):
                continue
            if path.is_symlink():
                self.error(path, "symlinks are not allowed in the package")
            elif not (path.is_file() or path.is_dir()):
                self.error(path, "only regular files and directories are allowed")

    def check_manifest(self):
        path = self.root / "plugin.json"
        if not path.is_file():
            self.error(path, "plugin.json is missing")
            return None
        data = self.read_json(path)
        if not isinstance(data, dict):
            if data is not None:
                self.error(path, "plugin.json must be a JSON object")
            return None
        if data.get("$schema") != SCHEMA_URL:
            self.error(path, f"$schema must be {SCHEMA_URL}")
        name = data.get("name")
        if not isinstance(name, str) or len(name) > 64 or not PLUGIN_NAME.fullmatch(name) or "--" in name:
            self.error(path, "name must be lowercase letters, digits and single hyphens (max 64)")
        version = data.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            self.error(path, "version must be strict SemVer (for example 1.0.0)")
        if not self.nonblank(data.get("description")):
            self.error(path, "description must be a nonblank string")
        interface = data.get("extensions", {})
        interface = interface.get("com.openai", {}) if isinstance(interface, dict) else None
        interface = interface.get("interface") if isinstance(interface, dict) else None
        if not isinstance(interface, dict):
            self.error(path, "extensions.com.openai.interface must be an object")
            return data
        for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            if not self.nonblank(interface.get(key)):
                self.error(path, f"interface.{key} must be a nonblank string")
        short = interface.get("shortDescription")
        if isinstance(short, str) and len(short) > SHORT_DESCRIPTION_MAX:
            self.error(path, f"interface.shortDescription is {len(short)} characters; the limit is {SHORT_DESCRIPTION_MAX}")
        if isinstance(interface.get("category"), str) and interface["category"] not in CATEGORIES:
            self.error(path, f"interface.category is not a known category: {interface['category']}")
        prompts = interface.get("defaultPrompt")
        if prompts is not None and not (
            self.nonblank(prompts)
            or (isinstance(prompts, list) and 1 <= len(prompts) <= 3 and all(self.nonblank(p) for p in prompts))
        ):
            self.error(path, "interface.defaultPrompt must be a nonblank string or a list of one to three strings")
        if "capabilities" in interface and not isinstance(interface["capabilities"], list):
            self.error(path, "interface.capabilities must be a list")
        if "logo" not in interface:
            self.error(path, "interface.logo is required")
        for key in ("logo", "composerIcon", "logoDark", "composerIconDark"):
            if key in interface:
                self.contained_file(self.root, interface[key], path, f"interface.{key}")
        return data

    def check_claude_manifest(self, portable):
        path = self.root / ".claude-plugin" / "plugin.json"
        if not path.is_file():
            self.error(path, ".claude-plugin/plugin.json is missing")
            return
        data = self.read_json(path)
        if not isinstance(data, dict):
            if data is not None:
                self.error(path, ".claude-plugin/plugin.json must be a JSON object")
            return
        if portable is None:
            return
        for key in ("name", "version"):
            if data.get(key) != portable.get(key):
                self.error(path, f"{key} {data.get(key)!r} does not match plugin.json {portable.get(key)!r}")
        if data.get("description") != portable.get("description"):
            self.warn(path, "description differs from plugin.json")

    def check_skills(self):
        skills_dir = self.root / "skills"
        paths = list(self.files("skills/*/SKILL.md"))
        if not paths:
            self.error(skills_dir, "no skills/*/SKILL.md found")
        for path in self.files("skills/**/SKILL.md"):
            if path.parent.parent != skills_dir:
                self.error(path, "SKILL.md must sit exactly one directory below skills/")
        for path in paths:
            self.stats["skills"] += 1
            data = self.frontmatter(path, "SKILL.md")
            if data is not None:
                if data.get("name") != path.parent.name:
                    self.error(path, f"frontmatter name {data.get('name')!r} must equal directory name {path.parent.name!r}", 1)
                description = data.get("description")
                if not self.nonblank(description):
                    self.error(path, "frontmatter description must be a nonblank string", 1)
                elif len(description) > SKILL_DESCRIPTION_MAX:
                    self.error(path, f"description is {len(description)} characters; the limit is {SKILL_DESCRIPTION_MAX}", 1)
            self.check_openai_yaml(path.parent / "agents" / "openai.yaml")

    def check_openai_yaml(self, path):
        if not path.is_file():
            self.error(path, "agents/openai.yaml is missing for this skill")
            return
        text = self.read_text(path)
        data = self.parse_yaml(text, path) if text is not None else None
        if not isinstance(data, dict):
            if text is not None:
                self.error(path, "openai.yaml must be a mapping")
            return
        interface = data.get("interface")
        if not isinstance(interface, dict):
            self.error(path, "interface must be a mapping")
        else:
            for key in ("display_name", "short_description", "default_prompt"):
                if not self.nonblank(interface.get(key)):
                    self.error(path, f"interface.{key} must be a nonblank string")
        policy = data.get("policy")
        if not isinstance(policy, dict) or not isinstance(policy.get("allow_implicit_invocation"), bool):
            self.error(path, "policy.allow_implicit_invocation must be true or false")

    def check_briefs(self):
        for path in self.files("agents/*.md"):
            if path.name.lower() == "readme.md":
                # Claude Code loads every agents/*.md file as an agent, so a
                # README there becomes a broken agent named "README".
                self.error(path, "Claude Code loads every agents/*.md file as an agent; "
                                 "move this README out of agents/ (for example to docs/)")
                continue
            self.stats["agents"] += 1
            data = self.frontmatter(path, "agent brief")
            if data is None:
                continue
            if not self.nonblank(data.get("name")):
                self.error(path, "agent frontmatter needs a nonblank name", 1)
            elif data["name"] != path.stem:
                self.error(path, f"agent name {data['name']!r} should equal file name {path.stem!r}", 1)
            if not self.nonblank(data.get("description")):
                self.error(path, "agent frontmatter needs a nonblank description", 1)
        for path in self.files("commands/*.md"):
            if path.name.lower() == "readme.md":
                continue
            self.stats["commands"] += 1
            data = self.frontmatter(path, "command")
            if data is not None and not self.nonblank(data.get("description")):
                self.error(path, "command frontmatter needs a nonblank description", 1)

    def check_links(self):
        for path in self.files("**/*.md"):
            self.stats["markdown_files"] += 1
            text = self.read_text(path)
            if text is None:
                continue
            for number, line in enumerate(strip_code(text), 1):
                targets = [m.group(1) for m in INLINE_LINK.finditer(line)]
                definition = REFERENCE_DEF.match(line)
                if definition:
                    targets.append(definition.group(1))
                for target in targets:
                    self.stats["links"] += 1
                    self.check_link(path, target.strip("<>").strip(), number)

    def check_link(self, owner, target, line):
        if not target:
            self.error(owner, "empty link destination", line)
            return
        try:
            parsed = urlsplit(target)
        except ValueError as exc:
            self.error(owner, f"unparseable link {target!r}: {exc}", line)
            return
        if parsed.scheme or parsed.netloc:
            return  # external links are out of scope for an offline check
        decoded = unquote(parsed.path)
        if decoded.startswith("/") or "\\" in decoded or "\x00" in decoded:
            self.error(owner, f"link must be relative: {target}", line)
            return
        resolved = owner.resolve() if not decoded else (owner.parent / decoded).resolve()
        if not _inside(resolved, self.root):
            self.error(owner, f"link escapes the package: {target}", line)
            return
        if not resolved.exists():
            self.error(owner, f"link target does not exist: {target}", line)
            return
        if parsed.fragment:
            if resolved.is_dir() or resolved.suffix.lower() not in (".md", ".markdown"):
                return  # anchors are only checked inside Markdown files
            text = resolved.read_text(encoding="utf-8", errors="replace")
            if unquote(parsed.fragment).lower() not in {slug.lower() for slug in heading_slugs(text)}:
                self.error(owner, f"anchor not found: {target}", line)

    def prose_paths(self):
        seen = []
        for name in PROSE_ROOT_FILES:
            if (self.root / name).is_file():
                seen.append(self.root / name)
        for directory in PROSE_DIRS:
            seen.extend(self.files(f"{directory}/**/*.md"))
        return seen

    def check_prose(self):
        for path in self.prose_paths():
            self.stats["prose_files"] += 1
            text = self.read_text(path)
            if text is None:
                continue
            for number, raw in enumerate(strip_code(text), 1):
                line = INLINE_LINK.sub(lambda m: m.group(0).split("](", 1)[0], raw)  # keep link text only
                line = URL_TOKEN.sub("", line)
                for char, label in DASHES.items():
                    if char in line:
                        self.error(path, f"{label} (U+{ord(char):04X}) outside code; rewrite with a comma, colon, parentheses, or a new sentence", number)
                if CURLY_QUOTES.search(line):
                    self.warn(path, "curly quote outside code; the house style uses straight quotes", number)
                quoted = [m.span() for m in re.finditer(r'"[^"\n]*"', line)]

                def in_quote(pos):
                    return any(start < pos < end for start, end in quoted)

                for word, pattern in BANNED_PATTERNS.items():
                    for match in pattern.finditer(line):
                        if in_quote(match.start()):
                            self.warn(path, f"banned word {match.group(1)!r} inside a quotation; keep only if it is a verbatim source quote", number)
                        else:
                            self.error(path, f"banned word {match.group(1)!r} (house list entry {word!r})", number)
                for word, pattern in WARNING_PATTERNS.items():
                    for match in pattern.finditer(line):
                        self.warn(path, f"{match.group(1)!r} is banned in its figurative or verb sense; confirm the use is literal", number)
                for match in OPENER_PATTERN.finditer(line):
                    if not in_quote(match.start(1)):
                        self.error(path, f"{match.group(1)!r} as a sentence opener is on the house banned list", number)

    def check_research(self):
        research = self.root / "research"
        if not research.is_dir():
            return
        for path in self.files("research/**/*.jsonl"):
            text = self.read_text(path)
            if text is None:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    json.loads(line, object_pairs_hook=_reject_duplicates)
                    self.stats["research_records"] += 1
                except ValueError as exc:
                    self.error(path, f"invalid JSONL record: {exc}", number)
        for path in self.files("research/**/*.json"):
            self.read_json(path)

    def run(self):
        if not self.root.is_dir():
            raise FileNotFoundError(f"package directory not found: {self.root}")
        self.check_tree()
        portable = self.check_manifest()
        self.check_claude_manifest(portable)
        self.check_skills()
        self.check_briefs()
        self.check_links()
        self.check_prose()
        self.check_research()
        return self.result()

    def result(self):
        return {
            "ok": not self.errors,
            "root": str(self.root),
            "scope": "offline package structure, links, and prose gate; no host install or fact checking",
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }


def _inside(path, root):
    try:
        Path(path).relative_to(root)
        return True
    except ValueError:
        return False


def validate_directory(root):
    if yaml is None:
        raise RuntimeError("PyYAML is required: pip install -r requirements-dev.txt")
    return Validator(root).run()


# --------------------------------------------------------------------------
# Archive mode
# --------------------------------------------------------------------------

def archive_member_problems(info):
    name = info.filename
    problems = []
    parts = name.rstrip("/").split("/")
    if not name or name.startswith("/") or "\\" in name or "\x00" in name or re.match(r"^[A-Za-z]:", name):
        problems.append(f"absolute or non-portable path: {name!r}")
    if any(part in ("", ".", "..") for part in parts):
        problems.append(f"path traversal or empty segment: {name!r}")
    mode = info.external_attr >> 16
    if stat.S_ISLNK(mode):
        problems.append(f"symlink member: {name!r}")
    elif stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
        problems.append(f"special file member: {name!r}")
    if info.flag_bits & 0x1:
        problems.append(f"encrypted member: {name!r}")
    return problems


def validate_archive(archive, max_bytes=MAX_ARCHIVE_BYTES):
    """Check ZIP safety, then validate the extracted package. Raises on unreadable input."""
    archive = Path(archive)
    problems = []
    with zipfile.ZipFile(archive) as bundle:
        infos = bundle.infolist()
        if len(infos) > MAX_ARCHIVE_MEMBERS:
            problems.append(f"archive has {len(infos)} members; the limit is {MAX_ARCHIVE_MEMBERS}")
        names, files, total = set(), [], 0
        for info in infos:
            problems.extend(archive_member_problems(info))
            if info.filename in names:
                problems.append(f"duplicate member: {info.filename!r}")
            names.add(info.filename)
            total += info.file_size
            if not info.is_dir():
                files.append(info.filename)
        if total > max_bytes:
            problems.append(f"uncompressed size {total} bytes exceeds the cap of {max_bytes}")
        wrapper = ""
        if not problems and "plugin.json" not in files:
            roots = {PurePosixPath(name).parts[0] for name in files}
            if len(roots) == 1 and f"{next(iter(roots))}/plugin.json" in files:
                wrapper = next(iter(roots))
            else:
                problems.append("archive must hold plugin.json at its root or inside one wrapper directory")
        if problems:
            return {"ok": False, "root": str(archive), "scope": "archive safety",
                    "errors": [{"path": archive.name, "line": None, "message": p} for p in problems],
                    "warnings": [], "stats": {"archive_members": len(infos)}}
        with tempfile.TemporaryDirectory(prefix="liquid-glass-validate-") as directory:
            for info in infos:  # extract members one by one after the safety pass
                target = Path(directory, info.filename)
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(info) as source, open(target, "wb") as sink:
                    sink.write(source.read(max_bytes + 1))
            result = validate_directory(Path(directory) / wrapper)
    result["root"] = str(archive)
    result["stats"]["archive_members"] = len(infos)
    return result


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def format_text(result):
    lines = []
    status = "PASS" if result["ok"] else "FAIL"
    lines.append(f"{status}: {result['root']} ({len(result['errors'])} errors, {len(result['warnings'])} warnings)")
    for level, items in (("ERROR", result["errors"]), ("WARN", result["warnings"])):
        for item in items:
            where = item["path"] + (f":{item['line']}" if item.get("line") else "")
            lines.append(f"{level} {where}: {item['message']}")
    stats = ", ".join(f"{key}={value}" for key, value in result.get("stats", {}).items())
    lines.append(f"stats: {stats}")
    lines.append(f"scope: {result.get('scope', '')}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline checks for the liquid-glass-studio plugin package.")
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]),
                        help="plugin directory (default: this script's package)")
    parser.add_argument("--archive", type=Path, help="validate a packaged ZIP instead of a directory")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args(argv)
    try:
        result = validate_archive(args.archive) if args.archive else validate_directory(args.root)
    except (OSError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        if args.json:
            print(json.dumps({"ok": False, "fatal": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else format_text(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
