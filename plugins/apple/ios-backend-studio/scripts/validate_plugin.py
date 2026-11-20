#!/usr/bin/env python3
"""Validate this skills-only plugin or its ZIP without network access.

Core checks use the standard library. PyYAML is used when installed; otherwise
the package's simple mapping/scalar YAML subset is parsed conservatively.
An explicit --schema uses the optional jsonschema package and a local schema.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import stat
import struct
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
CATEGORIES = {
    "Business & Operations", "Communication", "Creativity", "Data & Analytics",
    "Developer Tools", "Education & Research", "Entertainment", "Finance",
    "Healthcare", "Other", "Productivity", "Scientific Research", "Security", "Travel",
}
FORBIDDEN_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "Pods", "Carthage", "DerivedData",
    ".build", ".venv", "venv", "__pycache__",
}
FORBIDDEN_NAMES = {
    "AGENTS.md", "CLAUDE.md", ".DS_Store", "credentials.json",
    ".npmrc", ".netrc", ".pypirc",
}
SECRET_SUFFIXES = {".p8", ".p12", ".pfx", ".pem", ".key", ".mobileprovision", ".keychain"}
NAME = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME = re.compile(r"^(?!.*--)[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
MAX_FILE = 10 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024
MAX_ENTRIES = 10000


def _nonblank(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _pairs_no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_duplicates)


def _yaml(text: str) -> object:
    try:
        import yaml
    except ImportError:
        yaml = None
    if yaml is not None:
        class UniqueLoader(yaml.SafeLoader):
            pass

        def mapping(loader, node, deep=False):
            return _pairs_no_duplicates([
                (loader.construct_object(key, deep=deep), loader.construct_object(value, deep=deep))
                for key, value in node.value
            ])

        UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        return yaml.load(text, Loader=UniqueLoader)
    # This deliberately supports only the simple YAML authored in this package.
    # Reject richer YAML instead of silently giving it another interpretation.
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line or not re.match(r"^ *[A-Za-z_][A-Za-z0-9_-]*:", line):
            raise ValueError(f"YAML line {number} needs PyYAML for this syntax")
        indent = len(line) - len(line.lstrip())
        key, raw = line.strip().split(":", 1)
        raw = raw.strip()
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if key in parent:
            raise ValueError(f"duplicate YAML key {key!r}")
        if not raw:
            value: object = {}
        elif raw in {"true", "false", "null", "~"}:
            value = {"true": True, "false": False, "null": None, "~": None}[raw]
        elif raw.startswith('"'):
            value = json.loads(raw)
        elif raw.startswith("'") and raw.endswith("'"):
            value = raw[1:-1].replace("''", "'")
        elif raw.startswith(("[", "{")):
            value = json.loads(raw)
        elif raw.startswith(("|", ">", "&", "*", "!")) or ": " in raw or " #" in raw:
            raise ValueError(f"YAML line {number} needs PyYAML for this syntax")
        else:
            value = raw
        parent[key] = value
        if isinstance(value, dict):
            stack.append((indent, value))
    return root


def _contained(root: Path, origin: Path, target: str) -> Path:
    parsed = urlsplit(target)
    relative = unquote(parsed.path)
    if not relative:
        return origin
    path = (origin.parent / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes plugin: {target}")
    return path


def _https(value: object) -> bool:
    if not _nonblank(value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and parsed.username is None and parsed.password is None
    except ValueError:
        return False


def _raster_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        if data[12:16] == b"VP8X" and len(data) >= 30:
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
        if data[12:16] == b"VP8L" and len(data) >= 25 and data[20] == 47:
            bits = int.from_bytes(data[21:25], "little")
            return (bits & 16383) + 1, ((bits >> 14) & 16383) + 1
        if data[12:16] == b"VP8 " and data[23:26] == b"\x9d\x01\x2a" and len(data) >= 30:
            width, height = struct.unpack("<HH", data[26:30])
            return width & 16383, height & 16383
    if data.startswith(b"\xff\xd8"):
        offset = 2
        while offset + 4 <= len(data):
            if data[offset] != 255:
                break
            while offset < len(data) and data[offset] == 255:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in {216, 217}:
                continue
            length = int.from_bytes(data[offset:offset + 2], "big")
            if length < 2:
                break
            if marker in {192, 193, 194, 195, 197, 198, 199, 201, 202, 203, 205, 206, 207} and offset + 7 <= len(data):
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return width, height
            offset += length
    raise ValueError("unrecognized or truncated raster image")


def _check_icon(path: Path, errors: list[str], label: str) -> None:
    if path.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
        errors.append(f"{label}: unsupported icon type")
    if path.stat().st_size > 5 * 1024 * 1024:
        errors.append(f"{label}: icon exceeds 5 MiB")
    if path.suffix.lower() == ".svg":
        try:
            svg = ElementTree.fromstring(path.read_text(encoding="utf-8"))
            viewbox = svg.get("viewBox", "").split()
            if len(viewbox) == 4:
                width, height = float(viewbox[2]), float(viewbox[3])
            else:
                width = float(svg.get("width", "0").removesuffix("px"))
                height = float(svg.get("height", "0").removesuffix("px"))
            if width != height or width < 48:
                errors.append(f"{label}: icon must be square and at least 48 pixels")
            if any(el.tag.split("}")[-1] in {"script", "foreignObject"} for el in svg.iter()):
                errors.append(f"{label}: active SVG content is forbidden")
            for el in svg.iter():
                for key, value in el.attrib.items():
                    if key.lower().startswith("on") or (key.split("}")[-1] == "href" and not value.startswith("#")):
                        errors.append(f"{label}: SVG external reference or event handler is forbidden")
        except (ValueError, ElementTree.ParseError) as exc:
            errors.append(f"{label}: invalid SVG: {exc}")
    else:
        try:
            width, height = _raster_size(path)
            if width != height or not 48 <= width <= 4096:
                errors.append(f"{label}: raster icon must be square, 48–4096 pixels")
        except ValueError as exc:
            errors.append(f"{label}: {exc}")


def _manifest(root: Path, errors: list[str], schema_path: Path | None) -> dict:
    path = root / "plugin.json"
    try:
        data = _json(path)
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(f"plugin.json: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append("plugin.json: must be an object")
        return {}
    if data.get("$schema") != SCHEMA:
        errors.append("plugin.json: missing or incorrect portable $schema")
    name = data.get("name")
    if not _nonblank(name) or len(name) > 64 or not NAME.fullmatch(name):
        errors.append("plugin.json: invalid name")
    allowed = {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}
    for key in data.keys() - allowed:
        errors.append(f"plugin.json: unsupported root field {key}")
    version = data.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        errors.append("plugin.json: version must be strict SemVer")
    for field in ("description", "homepage", "repository", "license"):
        if field in data and not _nonblank(data[field]):
            errors.append(f"plugin.json: {field} must be a nonblank string")
    if "author" in data and not isinstance(data["author"], dict):
        errors.append("plugin.json: author must be an object")
    elif isinstance(data.get("author"), dict):
        author = data["author"]
        if author.keys() - {"name", "email", "url"} or any(not isinstance(value, str) for value in author.values()):
            errors.append("plugin.json: author accepts name, email and url string fields only")
    if "keywords" in data and (not isinstance(data["keywords"], list) or not all(_nonblank(v) for v in data["keywords"])):
        errors.append("plugin.json: keywords must be strings")
    extensions = data.get("extensions", {})
    if not isinstance(extensions, dict) or any(not isinstance(v, dict) for v in extensions.values()):
        errors.append("plugin.json: extensions must map namespaces to objects")
        return data
    openai = extensions.get("com.openai", {})
    interface = openai.get("interface", {})
    if not isinstance(interface, dict):
        errors.append("plugin.json: OpenAI interface must be an object")
        return data
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if field in interface and not _nonblank(interface[field]):
            errors.append(f"plugin.json: interface.{field} must be nonblank")
    subtitle = interface.get("shortDescription")
    if isinstance(subtitle, str) and len(subtitle) > 30:
        errors.append("plugin.json: shortDescription exceeds 30 characters")
    if "category" in interface and (not isinstance(interface["category"], str) or interface["category"] not in CATEGORIES):
        errors.append("plugin.json: category is not a supported exact title")
    if "capabilities" in interface and (not isinstance(interface["capabilities"], list) or not all(_nonblank(v) for v in interface["capabilities"])):
        errors.append("plugin.json: capabilities must be an array of nonblank strings")
    if "defaultPrompt" in interface:
        prompts = interface["defaultPrompt"]
        prompts = [prompts] if isinstance(prompts, str) else prompts
        if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or not all(_nonblank(p) for p in prompts):
            errors.append("plugin.json: defaultPrompt requires one to three nonblank strings")
    for field, value in interface.items():
        if field.endswith("URL") and not _https(value):
            errors.append(f"plugin.json: {field} requires an absolute HTTPS URL without credentials")
        if field in {"brandColor", "brandColorDark"} and (not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value)):
            errors.append(f"plugin.json: {field} requires a six-digit color")
    for field in ("logo", "composerIcon", "logoDark", "composerIconDark"):
        if field not in interface:
            continue
        value = interface[field]
        if not _nonblank(value) or value.startswith("/"):
            errors.append(f"plugin.json: {field} requires a contained relative path")
            continue
        try:
            if urlsplit(value).scheme:
                raise ValueError("asset requires a relative path")
            asset = _contained(root, path, value)
            if not asset.is_file():
                errors.append(f"plugin.json: missing asset {value}")
            else:
                _check_icon(asset, errors, field)
        except (OSError, ValueError) as exc:
            errors.append(f"plugin.json: {field}: {exc}")
    if schema_path is not None:
        try:
            import jsonschema
            schema = _json(schema_path)
            validator = jsonschema.Draft202012Validator(schema)
            errors.extend("plugin.json schema: " + e.message for e in validator.iter_errors(data))
        except ImportError:
            errors.append("--schema requires the optional jsonschema package")
        except (OSError, ValueError) as exc:
            errors.append(f"local schema: {exc}")
    return data


def _agent(path: Path, errors: list[str]) -> None:
    try:
        data = _yaml(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("must be a YAML object")
        interface = data.get("interface")
        if interface is not None:
            if not isinstance(interface, dict):
                raise ValueError("interface must be an object")
            if not all(_nonblank(interface.get(k)) for k in ("display_name", "short_description")):
                raise ValueError("interface requires display_name and short_description")
            if "default_prompt" in interface and not _nonblank(interface["default_prompt"]):
                raise ValueError("default_prompt must be one string")
            if "brand_color" in interface and not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(interface["brand_color"])):
                raise ValueError("invalid brand_color")
        policy = data.get("policy", {})
        if not isinstance(policy, dict) or policy.keys() - {"products", "allow_implicit_invocation"}:
            raise ValueError("unsupported policy field or type")
        implicit = policy.get("allow_implicit_invocation")
        if implicit is not None and not isinstance(implicit, bool):
            raise ValueError("allow_implicit_invocation must be a boolean")
        products = policy.get("products")
        if products is not None and (not isinstance(products, list) or any(p not in {"CHAT", "CODEX", "HERMES"} for p in products)):
            raise ValueError("unsupported products")
        dependencies = data.get("dependencies", {})
        if not isinstance(dependencies, dict) or dependencies.keys() - {"tools"}:
            raise ValueError("dependencies accepts tools only")
    except Exception as exc:
        errors.append(f"{path.parent.parent.name}/agents/openai.yaml: {exc}")


def _links(root: Path, path: Path, text: str, errors: list[str]) -> None:
    targets = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+[^)]*)?\)", text)
    targets += re.findall(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]*>|\S+)", text, re.M)
    targets += re.findall(r"(?:src|href)=[\"']([^\"']+)[\"']", text)
    for target in targets:
        target = target.removeprefix("<").removesuffix(">")
        if not target or target.startswith("#"):
            continue
        try:
            parsed = urlsplit(target)
            if parsed.scheme == "file" or target.startswith("/") and not target.startswith("//"):
                raise ValueError(f"nonportable absolute local link {target}")
            if parsed.scheme or target.startswith("//"):
                continue
            linked = _contained(root, path, target)
            if not linked.exists():
                errors.append(f"{path.relative_to(root)}: broken local link {target}")
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")


def _feedback_instructions(text: str) -> bool:
    """Detect actionable upstream reporting hooks, not prose documenting exclusions."""
    feedback_section = False
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s+", line):
            feedback_section = bool(re.match(r"^#{1,6}\s+Feedback\b", line, re.I))
        if re.search(r"\b(?:do not|never|exclude[ds]?|omit(?:ted)?|removed?|prohibit(?:ed)?|not included)\b", line, re.I):
            continue
        expo = re.search(r"(?:npx|bunx)\s+@expo/agent-cli\b[^\n]*\bfeedback\b", line, re.I)
        actionable = re.match(r"^\s*(?:[$>]\s*)?(?:npx|bunx|curl|requests\.post|POST\s+https?://)\b", line, re.I)
        imperative = re.search(r"\b(?:run|execute|send|transmit|upload)\b[^\n]*(?:npx|bunx|curl|requests\.post|POST\s+https?://)", line, re.I)
        if expo and (actionable or imperative):
            return True
        if feedback_section and (actionable or imperative):
            return True
    return False


def _compatibility_overlay(path: Path, portable: dict, errors: list[str], host: str = "codex") -> None:
    """Accept a synchronized metadata projection for a known host only."""
    label = f".{host}-plugin/plugin.json"
    try:
        overlay = _json(path)
        if not isinstance(overlay, dict):
            raise ValueError("must be an object")
        metadata = {"name", "version", "description", "author", "keywords", "license", "homepage", "repository"}
        host_fields = {"skills", "interface"} if host == "codex" else set()
        unknown = overlay.keys() - metadata - host_fields
        if unknown:
            raise ValueError("unsupported fields: " + ", ".join(sorted(unknown)))
        for key in ("name", "version"):
            if not _nonblank(overlay.get(key)) or overlay[key] != portable.get(key):
                raise ValueError(f"{key} must match portable manifest")
        if host == "claude" and not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", overlay["name"]):
            raise ValueError("name must use Claude Code kebab-case format")
        for key in metadata - {"name", "version"}:
            if (key in overlay or key in portable) and overlay.get(key) != portable.get(key):
                raise ValueError(f"{key} must match portable manifest")
        if host == "codex" and overlay.get("skills") != "./skills":
            raise ValueError("skills must be './skills'")
        if "interface" in overlay:
            extensions = portable.get("extensions", {})
            openai = extensions.get("com.openai", {}) if isinstance(extensions, dict) else {}
            interface = openai.get("interface", {}) if isinstance(openai, dict) else {}
            if not isinstance(overlay["interface"], dict) or overlay["interface"] != interface:
                raise ValueError("interface must match portable OpenAI interface")
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(f"{label}: invalid compatibility overlay: {exc}")


def _kimi_profile(root: Path, expected_skills: int | None, errors: list[str]) -> None:
    """Use trusted sibling validation code, never a candidate archive's script."""
    if not (root / "kimi.plugin.json").exists():
        return
    trusted = Path(__file__).resolve().with_name("validate_kimi.py")
    try:
        spec = importlib.util.spec_from_file_location("ios_trusted_kimi_validator", trusted)
        if spec is None or spec.loader is None:
            raise ImportError("cannot load installed Kimi compatibility checks")
        module = importlib.util.module_from_spec(spec)
        # Compile the trusted file directly so validation does not create a
        # __pycache__ directory inside the plugin being checked.
        exec(compile(trusted.read_text(encoding="utf-8"), str(trusted), "exec"), module.__dict__)
        errors.extend(f"kimi.plugin.json: {error}" for error in module.validate_kimi(root, expected_skills))
    except (ImportError, OSError, SyntaxError) as exc:
        errors.append(f"kimi.plugin.json: trusted compatibility validation unavailable: {exc}")


def _reference_profile(root: Path, errors: list[str]) -> None:
    """Check registered citations using installed code, not archive contents."""
    if not any((root / name).exists() for name in ("research/sources/sources.jsonl", "research/artifacts/claim_ledger.jsonl")):
        return
    trusted = Path(__file__).resolve().with_name("validate_references.py")
    try:
        spec = importlib.util.spec_from_file_location("trusted_reference_integrity", trusted)
        if spec is None or spec.loader is None:
            raise ImportError("cannot load installed reference integrity checks")
        module = importlib.util.module_from_spec(spec)
        exec(compile(trusted.read_text(encoding="utf-8"), str(trusted), "exec"), module.__dict__)
        errors.extend(f"references: {error}" for error in module.validate_references(root))
    except (ImportError, OSError, SyntaxError) as exc:
        errors.append(f"references: trusted integrity validation unavailable: {exc}")


def validate_plugin(root: Path, expected_skills: int | None = None, schema_path: Path | None = None) -> list[str]:
    """Return diagnostics; a successful validation returns an empty list."""
    errors: list[str] = []
    root = Path(root).absolute()
    if root.is_symlink():
        return ["plugin directory must not be a symlink"]
    if not root.is_dir():
        return [f"plugin directory does not exist: {root}"]
    data = _manifest(root, errors, schema_path)
    total = 0
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"{rel}: symlinks are forbidden")
            continue
        if any(part in FORBIDDEN_DIRS for part in rel.parts):
            errors.append(f"{rel}: dependency/cache/source-control directory is forbidden")
            continue
        if path.is_dir():
            continue
        if not stat.S_ISREG(path.stat().st_mode):
            errors.append(f"{rel}: nonregular files are forbidden")
            continue
        # These exact root overlays project one plugin into host metadata.
        # A manifest anywhere else represents an unrelated nested package.
        if path.name.casefold() == "plugin.json" and path != root / "plugin.json":
            if rel.parts == (".codex-plugin", "plugin.json"):
                _compatibility_overlay(path, data, errors, "codex")
            elif rel.parts == (".claude-plugin", "plugin.json"):
                _compatibility_overlay(path, data, errors, "claude")
            else:
                errors.append(f"{rel}: nested plugin manifest is forbidden")
        if path.name in {"mcp.json", ".mcp.json", ".app.json"}:
            errors.append(f"{rel}: skills-only package contains an unvalidated MCP/app connection")
        if rel.parts[0] in {"hooks", "commands", "agents"} or rel.parts == ("settings.json",):
            errors.append(f"{rel}: skills-only package contains an undeclared host component")
        if path.name in FORBIDDEN_NAMES or path.name == ".env" or path.name.startswith(".env.") or path.suffix.lower() in SECRET_SUFFIXES:
            errors.append(f"{rel}: secret, host instruction, or unrelated file is forbidden")
        size = path.stat().st_size
        total += size
        if size > MAX_FILE:
            errors.append(f"{rel}: file exceeds {MAX_FILE} bytes")
            continue
        if path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".svg", ".txt"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeError:
                errors.append(f"{rel}: text must be UTF-8")
                continue
            if re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", text):
                errors.append(f"{rel}: private key material is forbidden")
            if re.search(r"gh[pousr]_[A-Za-z0-9]{20,}", text):
                errors.append(f"{rel}: credential-like token is forbidden")
            if path.suffix.lower() == ".md":
                _links(root, path, text, errors)
                if _feedback_instructions(text):
                    errors.append(f"{rel}: upstream Feedback transmission instructions are forbidden")
    if total > MAX_TOTAL:
        errors.append(f"plugin exceeds {MAX_TOTAL} uncompressed bytes")
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("skills: at least one usable skill is required")
    if expected_skills is not None and len(skills) != expected_skills:
        errors.append(f"skills: expected {expected_skills}, found {len(skills)}")
    discovered = set()
    if (root / "skills").is_dir():
        for child in (root / "skills").iterdir():
            if child.is_dir() and not (child / "SKILL.md").is_file():
                errors.append(f"skills/{child.name}: missing SKILL.md entrypoint")
    for path in skills:
        try:
            if path.stat().st_size > 1024 * 1024:
                raise ValueError("SKILL.md exceeds 1 MiB")
            text = path.read_text(encoding="utf-8")
            match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
            if not match:
                raise ValueError("missing opening YAML frontmatter")
            frontmatter = _yaml(match.group(1))
            if not isinstance(frontmatter, dict) or not _nonblank(frontmatter.get("name")) or not _nonblank(frontmatter.get("description")):
                raise ValueError("name and description must be nonblank strings")
            name = frontmatter["name"]
            if len(name) > 64 or not SKILL_NAME.fullmatch(name) or name != path.parent.name:
                raise ValueError("name must match its kebab-case skill directory")
            if name in discovered:
                raise ValueError("duplicate skill name")
            discovered.add(name)
            if not text[match.end():].strip():
                raise ValueError("skill instructions must not be empty")
        except Exception as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
        agent = path.parent / "agents" / "openai.yaml"
        if agent.exists():
            _agent(agent, errors)
    for path in (root / "skills").rglob("SKILL.md"):
        if path not in skills:
            errors.append(f"{path.relative_to(root)}: skill is not at portable skills/<name>/SKILL.md depth")
    # This package is skills-only: silently ignoring another connection type is unsafe.
    if (root / "mcp.json").exists() or (root / ".mcp.json").exists() or (root / ".app.json").exists():
        errors.append("skills-only package must not include an unvalidated MCP/app connection")
    extensions = data.get("extensions")
    openai = extensions.get("com.openai") if isinstance(extensions, dict) else None
    if isinstance(openai, dict) and openai.get("apps") is not None:
        errors.append("skills-only package must not declare app dependencies")
    _kimi_profile(root, expected_skills, errors)
    _reference_profile(root, errors)
    return sorted(set(errors))


def validate_archive(archive: Path, expected_skills: int | None = None, schema_path: Path | None = None) -> list[str]:
    """Validate paths and sizes before extracting into a private temporary directory."""
    errors: list[str] = []
    try:
        with zipfile.ZipFile(archive) as zipped:
            items = zipped.infolist()
            if len(items) > MAX_ENTRIES:
                return ["archive: too many entries"]
            total = 0
            names = set()
            folded = set()
            for item in items:
                name = item.filename
                parts = PurePosixPath(name).parts
                if name in names:
                    errors.append(f"archive: duplicate entry {name}")
                names.add(name)
                folded_name = name.rstrip("/").casefold()
                if folded_name in folded:
                    errors.append(f"archive: colliding entry {name}")
                folded.add(folded_name)
                if not name or name.startswith(("/", "\\")) or "\\" in name or ".." in parts or ":" in (parts[0] if parts else ""):
                    errors.append(f"archive: unsafe path {name}")
                if str(PurePosixPath(name)) != name.rstrip("/"):
                    errors.append(f"archive: noncanonical path {name}")
                if stat.S_ISLNK(item.external_attr >> 16):
                    errors.append(f"archive: symlink {name}")
                entry_type = stat.S_IFMT(item.external_attr >> 16)
                if entry_type not in {0, stat.S_IFREG, stat.S_IFDIR, stat.S_IFLNK}:
                    errors.append(f"archive: nonregular entry {name}")
                if item.flag_bits & 1:
                    errors.append(f"archive: encrypted entry {name}")
                if item.file_size > MAX_FILE:
                    errors.append(f"archive: oversized entry {name}")
                total += item.file_size
            if total > MAX_TOTAL:
                errors.append("archive: uncompressed size exceeds bound")
            if errors:
                return sorted(set(errors))
            files = [i for i in items if not i.is_dir()]
            manifests = [i.filename for i in files if PurePosixPath(i.filename).name == "plugin.json" and len(PurePosixPath(i.filename).parts) <= 2]
            if "plugin.json" in manifests:
                prefix = ""
            elif len(manifests) == 1:
                prefix = str(PurePosixPath(manifests[0]).parent) + "/"
            else:
                return ["archive: expected one root manifest or one enclosing plugin directory"]
            if prefix and any(not i.filename.startswith(prefix) for i in files):
                return ["archive: unrelated siblings outside enclosing plugin directory"]
            with tempfile.TemporaryDirectory(prefix="ios-plugin-validate-") as temporary:
                extraction = Path(temporary)
                for item in files:
                    target = extraction.joinpath(*PurePosixPath(item.filename).parts)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zipped.read(item))
                plugin = extraction / prefix if prefix else extraction
                errors.extend(validate_plugin(plugin, expected_skills, schema_path))
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError) as exc:
        errors.append(f"archive: {exc}")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive", type=Path, help="Validate a ZIP instead of a directory")
    parser.add_argument("--expected-skills", type=int, help="Check an expected count, when the desired count is known")
    parser.add_argument("--schema", type=Path, help="Optional pinned local JSON schema; needs jsonschema")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable result")
    args = parser.parse_args(argv)
    if args.expected_skills is not None and args.expected_skills < 1:
        parser.error("--expected-skills must be positive")
    errors = validate_archive(args.archive, args.expected_skills, args.schema) if args.archive else validate_plugin(args.root, args.expected_skills, args.schema)
    if args.json:
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    elif errors:
        print("Plugin validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("Plugin validation passed.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
