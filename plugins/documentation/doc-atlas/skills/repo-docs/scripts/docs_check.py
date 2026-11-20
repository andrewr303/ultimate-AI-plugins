#!/usr/bin/env python3
"""Conservative offline Markdown preflight. JSON output; not a complete Markdown/MDX parser."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import html
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
import unicodedata
from urllib.parse import unquote, urlsplit
from doc_common import InputFailure, MAX_FILES, contained, inventory, read_text, root_path

MARKDOWN = {'.md', '.markdown'}
MAX_TOTAL_BYTES = 16 * 1_048_576
MAX_FINDINGS = 4096
MAX_LINKS_PER_FILE = 2048


def blank(s: str) -> str:
    return ''.join('\n' if c == '\n' else ' ' for c in s)


def frontmatter_span(text: str) -> tuple[int | None, bool]:
    """Recognize only delimiter-paired, mapping-style YAML frontmatter.

    A leading thematic break is ordinary Markdown. This deliberately does not
    parse YAML: a first nonblank mapping line is the conservative discriminator.
    The returned boolean also identifies an unclosed mapping-style region.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, False
    closing = next((i for i in range(1, len(lines))
                    if lines[i].strip() in {'---', '...'}), None)
    body = lines[1:closing] if closing is not None else lines[1:]
    first = next((line for line in body if line.strip()), '')
    mapping_start = bool(re.match(r'^[A-Za-z_][\w.-]*[ \t]*:', first))
    return closing if mapping_start else None, mapping_start


def block_text(text: str) -> tuple[str, int | None]:
    """Mask recognized frontmatter, comments and code, preserving line offsets."""
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    fence = None
    unclosed = None
    frontmatter_end, _ = frontmatter_span(text)
    for n, line in enumerate(lines, 1):
        if frontmatter_end is not None and n <= frontmatter_end + 1:
            output.append(blank(line))
            continue
        m = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            output.append(blank(line))
            if m and m[1][0] == fence[0] and len(m[1]) >= fence[1] and not m[2].strip():
                fence = None
                unclosed = None
            continue
        if m and not (m[1][0] == '`' and '`' in m[2]):
            fence = (m[1][0], len(m[1]))
            unclosed = n
            output.append(blank(line))
        elif line.startswith(('    ', '\t')):
            output.append(blank(line))
        else:
            output.append(line)
    result = ''.join(output)
    result = re.sub(r'<!--[\s\S]*?(?:-->|$)', lambda m: blank(m[0]), result)
    return result, unclosed


def inline_mask(text: str) -> str:
    result = list(text)
    i = 0
    while i < len(text):
        if text[i] != '`' or (i and text[i-1] == '\\'):
            i += 1
            continue
        end = i
        while end < len(text) and text[end] == '`':
            end += 1
        token = text[i:end]
        close = text.find(token, end)
        while close >= 0 and ((close and text[close-1] == '`') or
                                 (close+len(token) < len(text) and text[close+len(token)] == '`')):
            close = text.find(token, close+len(token))
        if close < 0:
            i = end
            continue
        for j in range(i, close+len(token)):
            if result[j] != '\n':
                result[j] = ' '
        i = close+len(token)
    return ''.join(result)


def slug(text: str) -> str:
    # Deliberately a GitHub-style approximation; rendered output remains authoritative.
    text = re.sub(r'!?(\[([^\]]*)\])\([^)]*\)', r'\2', text)
    text = re.sub(r'<[^>]*>', '', text)
    text = html.unescape(text).strip().lower()
    return ''.join(c for c in text if c in '-_ ' or c.isalnum() or unicodedata.category(c).startswith('M')).replace(' ', '-')


def headings(text: str) -> tuple[set[str], list[tuple[int, int, str]]]:
    seen: dict[str, int] = {}
    ids: set[str] = {'top'}
    generated: set[str] = set()
    records = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r'^ {0,3}(#{1,6})(?:[ \t]+(.*)|$)', line)
        if match:
            level, title = len(match[1]), match[2] or ''
            title = re.sub(r'[ \t]+#+[ \t]*$', '', title)
        elif index+1 < len(lines) and line.strip() and re.fullmatch(r' {0,3}(?:=+|-+)[ \t]*', lines[index+1]):
            level, title = (1 if lines[index+1].lstrip().startswith('=') else 2), line.strip()
        else:
            continue
        base = slug(title)
        candidate = base
        suffix = seen.get(base, 0)
        while candidate in generated:
            suffix += 1
            candidate = f'{base}-{suffix}'
        seen[base] = suffix
        ids.add(candidate)
        generated.add(candidate)
        records.append((index+1, level, title))
    return ids, records


def destination(raw: str) -> str | None:
    raw = raw.strip()
    if raw.startswith('<'):
        end = raw.find('>')
        return raw[1:end] if end >= 0 else None
    # Spaces outside angle destinations delimit an optional quoted title.
    match = re.match(r'(\S+?)(?:\s+[\'\"(].*)?$', raw)
    return match[1] if match else None


def reference_key(label: str) -> str:
    return ' '.join(label.split()).casefold()


@dataclass
class Link:
    line: int
    label: str
    target: str | None
    image: bool
    unknown_ref: str | None = None


def links(text: str, original: str | None = None) -> tuple[list[Link], list[int]]:
    references = {}
    masked = text
    for match in re.finditer(r'^ {0,3}\[([^\]\n]+)\]:[ \t]*(.+)$', text, re.M):
        references.setdefault(reference_key(match[1]), destination(match[2]))
        masked = masked[:match.start()] + blank(match[0]) + masked[match.end():]
    found: list[Link] = []
    unsupported: list[int] = []
    stack: list[int] = []
    i = 0
    while i < len(masked):
        char = masked[i]
        if char == '\\':
            i += 2
            continue
        if char == '[':
            stack.append(i)
        elif char == ']' and stack:
            start = stack.pop()
            label = (original if original is not None else masked)[start+1:i]
            image = start > 0 and masked[start-1] == '!'
            line = masked.count('\n', 0, start)+1
            end = i+1
            target = None
            ref = None
            if end < len(masked) and masked[end] == '(':
                cursor, depth = end+1, 1
                while cursor < len(masked) and depth:
                    if masked[cursor] == '\\':
                        cursor += 2
                        continue
                    if masked[cursor] == '(':
                        depth += 1
                    elif masked[cursor] == ')':
                        depth -= 1
                    cursor += 1
                if depth:
                    unsupported.append(line)
                else:
                    target = destination(masked[end+1:cursor-1])
                    found.append(Link(line, label, target, image))
                    i = cursor-1
            elif end < len(masked) and masked[end] == '[':
                close = masked.find(']', end+1)
                if close >= 0:
                    key = reference_key(masked[end+1:close] or label)
                    target = references.get(key)
                    if key not in references:
                        ref = key
                    found.append(Link(line, label, target, image, ref))
                    i = close
            elif reference_key(label) in references:
                found.append(Link(line, label, references[reference_key(label)], image))
            elif image:
                # Unresolved image shortcut reference; a bracketed ordinary word may be prose.
                found.append(Link(line, label, None, image, reference_key(label)))
        i += 1
    return found, unsupported


class Checker:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[dict] = []
        self.unresolved: list[dict] = []
        self.failures: list[dict] = []
        self.cache: dict[Path, tuple[str, set[str]]] = {}
        self.bytes_read = 0

    def relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return '[outside-root]'

    def add(self, path: Path, line: int, code: str, message: str, severity: str = 'error'):
        if len(self.findings) >= MAX_FINDINGS:
            self.pending(path, line, 'finding-limit', 'Finding output capped; remaining content requires review.')
            return
        self.findings.append({'path': self.relative(path), 'line': line,
                              'code': code, 'severity': severity, 'message': message})

    def pending(self, path: Path, line: int, code: str, message: str):
        record = {'path': self.relative(path), 'line': line, 'code': code, 'message': message}
        if record not in self.unresolved and len(self.unresolved) < MAX_FINDINGS:
            self.unresolved.append(record)

    def read(self, path: Path) -> str:
        try:
            size = contained(self.root, path).stat().st_size
        except OSError as exc:
            raise InputFailure('file could not be inspected') from exc
        if self.bytes_read + size > MAX_TOTAL_BYTES:
            raise InputFailure('total document byte budget reached; coverage incomplete')
        body = read_text(self.root, path)
        self.bytes_read += len(body.encode('utf-8'))
        return body

    def load(self, path: Path) -> tuple[str, set[str]]:
        if path not in self.cache:
            body = self.read(path)
            blocks, _ = block_text(body)
            self.cache[path] = (blocks, headings(blocks)[0])
        return self.cache[path]

    def check_target(self, path: Path, link: Link):
        if link.image and not link.label.strip():
            self.add(path, link.line, 'missing-image-alt', 'Markdown image needs descriptive alternate text; review decorative cases manually.')
        if link.unknown_ref is not None:
            self.add(path, link.line, 'unknown-reference', 'Explicit link/image reference has no definition.')
            return
        if link.target is None:
            self.pending(path, link.line, 'unsupported-destination', 'Destination syntax could not be parsed conservatively.')
            return
        target = html.unescape(link.target)
        if re.match(r'^[A-Za-z]:[/\\]', target) or target.startswith('\\\\'):
            self.add(path, link.line, 'outside-root', 'Windows rooted or UNC destination is not repository-local.')
            return
        if re.search(r'%(?![A-Fa-f0-9]{2})', target):
            self.pending(path, link.line, 'invalid-percent-encoding', 'Destination contains malformed percent encoding.')
            return
        try:
            url = urlsplit(target)
        except ValueError:
            self.pending(path, link.line, 'unsupported-destination', 'Destination is not a parseable URI reference.')
            return
        if url.scheme or url.netloc or target.startswith('//'):
            if url.scheme.lower() in {'javascript', 'data', 'vbscript'}:
                self.add(path, link.line, 'unsafe-scheme', 'Executable or embedded-data URI requires removal or explicit manual review.')
            else:
                self.pending(path, link.line, 'remote-or-scheme-link', 'Non-local destination was not fetched or verified.')
            return
        decoded = unquote(url.path)
        if re.match(r'^[A-Za-z]:[/\\]', decoded) or decoded.startswith('\\\\'):
            self.add(path, link.line, 'outside-root', 'Encoded Windows rooted destination is not repository-local.')
            return
        if '\x00' in decoded or '\x00' in unquote(url.fragment):
            self.add(path, link.line, 'invalid-destination', 'Destination contains a null byte.')
            return
        if decoded.startswith('/') or url.query or '\\' in decoded:
            self.pending(path, link.line, 'framework-route-or-query', 'Root routes, query links and backslash paths require renderer-specific review.')
            return
        target_path = path if not decoded else path.parent / decoded
        try:
            target_path = contained(self.root, target_path)
        except InputFailure as exc:
            self.add(path, link.line, 'excluded-destination', str(exc))
            return
        if decoded and not Path(decoded).suffix:
            self.pending(path, link.line, 'extensionless-route', 'Extensionless destination may be a framework route; not verified.')
            return
        if not target_path.is_file():
            self.add(path, link.line, 'missing-local-file', 'Local destination is not an existing regular file.')
            return
        if url.fragment:
            if target_path.suffix.lower() not in MARKDOWN:
                self.pending(path, link.line, 'unsupported-fragment', 'Fragment belongs to a non-Markdown or dynamic target; inspect rendered output.')
                return
            try:
                target_blocks, ids = self.load(target_path)
            except InputFailure as exc:
                self.failures.append({'path': self.relative(target_path), 'reason': str(exc)})
                return
            fragment = unquote(url.fragment)
            if fragment not in ids and (re.search(r'<[^>]+(?:id|name)\s*=|\{#[^}]+\}|<[A-Z]', target_blocks)):
                self.pending(path, link.line, 'custom-renderer-fragment', 'Custom/HTML anchors require rendered validation; the subset cannot decide this fragment.')
            elif fragment not in ids:
                self.add(path, link.line, 'missing-heading-fragment', 'Fragment does not match a heading in the supported GitHub-style subset.')

    def check(self, path: Path):
        if path.suffix.lower() == '.mdx':
            self.pending(path, 1, 'mdx-requires-renderer', 'MDX is executable/component syntax; this preflight does not parse it. Run the existing site build and route checks.')
            return
        if path.suffix.lower() not in MARKDOWN:
            self.pending(path, 1, 'unsupported-filetype', 'Only .md and .markdown files are parsed.')
            return
        try:
            text = self.read(path)
        except InputFailure as exc:
            self.failures.append({'path': self.relative(path), 'reason': str(exc)})
            return
        frontmatter_end, mapping_start = frontmatter_span(text)
        if mapping_start and frontmatter_end is None:
            self.add(path, 1, 'unclosed-frontmatter', 'Mapping-style YAML frontmatter has no closing delimiter; remaining text was checked as Markdown.')
        elif frontmatter_end is not None:
            self.pending(path, 1, 'frontmatter-not-validated', 'Mapping-style frontmatter was excluded from Markdown checks; its YAML and renderer metadata were not validated.')
        blocks, unclosed = block_text(text)
        self.cache[path] = (blocks, headings(blocks)[0])
        if unclosed:
            self.add(path, unclosed, 'unclosed-fence', 'Fenced code block is not closed.')
        _, records = headings(blocks)
        previous = 0
        for line, level, _ in records:
            if previous and level > previous+1:
                self.add(path, line, 'heading-level-jump', 'Heading skips a level; review document hierarchy.', 'warning')
            previous = level
        masked = inline_mask(blocks)
        for match in re.finditer(r'<(?:a|img)\b|<[A-Z][A-Za-z]*\b|^\s*(?:import|export)\s', masked, re.M):
            self.pending(path, masked.count('\n', 0, match.start())+1,
                         'html-or-component-syntax', 'HTML/component/import syntax requires renderer-aware checks.')
        found, unsupported = links(masked, blocks)
        for line in unsupported:
            self.pending(path, line, 'unsupported-link-syntax', 'Unbalanced or unsupported inline link syntax needs manual review.')
        if len(found) > MAX_LINKS_PER_FILE:
            self.pending(path, 1, 'link-limit', 'Per-file link budget reached; remaining links require review.')
        for link in found[:MAX_LINKS_PER_FILE]:
            self.check_target(path, link)


def run(root: Path, requested: list[str] | None, max_files: int) -> tuple[dict, int]:
    checker = Checker(root)
    if requested:
        if len(requested) > max_files:
            raise InputFailure('explicit selection exceeds entry limit')
        files = []
        for value in requested:
            candidate = Path(value)
            if candidate.is_absolute():
                raise InputFailure('--path must be repository-relative')
            candidate = contained(root, root/candidate)
            if not candidate.is_file():
                raise InputFailure('--path must name an existing regular file')
            files.append(candidate)
        limits = {'truncated': False, 'read_failures': 0, 'selection': 'explicit'}
    else:
        all_files, limits = inventory(root, max_files)
        files = [p for p in all_files if p.suffix.lower() in MARKDOWN | {'.mdx'}]
    for path in sorted(set(files)):
        checker.check(path)
    limits['document_bytes_read'] = checker.bytes_read
    limits['max_total_document_bytes'] = MAX_TOTAL_BYTES
    limits['max_links_per_file'] = MAX_LINKS_PER_FILE
    result = {'tool': 'docs_check', 'schema_version': 1,
              'scope': 'Offline bounded GitHub-style Markdown subset; no networking, commands, writes, full parser, factual or visual validation.',
              'limits': limits, 'files_checked': len(set(files)),
              'findings': checker.findings, 'unresolved': checker.unresolved,
              'failures': checker.failures,
              'limitations': ['Heading IDs approximate GitHub; target renderer is authoritative.',
                              'MDX, HTML anchors, custom heading IDs, dynamic routes, autolinks and shortcut references without definitions require renderer/manual review.',
                              'Only paired, mapping-style YAML frontmatter is masked; YAML validity is not evaluated.',
                              'Passing this preflight does not establish complete link coverage, accessibility, content truth or visual quality.']}
    if limits['truncated']:
        result['unresolved'].append({'code': 'traversal-limit', 'message': 'Traversal was capped; coverage is incomplete.'})
    if not files:
        result['unresolved'].append({'code': 'no-markdown', 'message': 'No supported documentation files found.'})
    if checker.failures or limits['read_failures']:
        status = 2
    elif any(f['severity'] == 'error' for f in checker.findings):
        status = 1
    else:
        status = 0
    result['status'] = 'failed-to-read' if status == 2 else ('errors' if status == 1 else 'no-errors-detected')
    return result, status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='Repository directory (never modified).')
    parser.add_argument('--path', action='append', help='Repository-relative file; repeat to select files.')
    parser.add_argument('--max-files', type=int, default=MAX_FILES, help='Scanned entry limit, 1..50000.')
    args = parser.parse_args()
    if not 1 <= args.max_files <= 50000:
        parser.error('--max-files must be between 1 and 50000')
    try:
        result, status = run(root_path(args.root), args.path, args.max_files)
    except InputFailure as exc:
        print(json.dumps({'tool': 'docs_check', 'failure': str(exc)}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return status

if __name__ == '__main__':
    sys.exit(main())
