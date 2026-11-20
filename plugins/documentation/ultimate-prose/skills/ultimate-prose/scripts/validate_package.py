#!/usr/bin/env python3
"""Validate this skill package: routes, budgets, eval cases, scripts, manifests.

Adapted from Clarity's validate_package.py (MIT License, Copyright (c) 2026
Addy Osmani; see NOTICE.md). Standard library only; read-only.

Checks that can fail:
  - SKILL.md frontmatter has a name and a semantic metadata.version;
  - every references/, scripts/, or tests/ path named in SKILL.md or README.md exists;
  - SKILL.md, and SKILL.md plus every references/*.md it routes to, stay within
    word budgets (a growth alarm: a task loads only the references it needs);
  - the eval file parses, ids are unique, each case states its expectations,
    and categorized cases cover the required behavior categories;
  - every Python file compiles; with --release, no caches, symlinks, or OS litter;
  - plugin manifests, when present two levels up, carry the skill's version.

Usage: python scripts/validate_package.py [--release] [--max-skill-words N] [--max-runtime-words N]
Exit: 0 all checks passed; 1 a check failed.
"""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_CATEGORIES = {
    "factual_fidelity", "medium_fit", "false_positive", "authorship",
    "mode_boundary", "instruction_integrity",
}
EVAL_FILES = ("references/test-cases.json", "references/evaluation-cases.json")
LITTER = {"__pycache__", ".DS_Store", "Thumbs.db", ".pytest_cache"}


def words(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max-skill-words", type=int, default=2500)
    parser.add_argument("--max-runtime-words", type=int, default=18000,
                        help="SKILL.md plus every references/*.md file it names")
    parser.add_argument("--release", action="store_true",
                        help="also fail on caches, symlinks, and OS files (run before packaging)")
    args = parser.parse_args(argv)
    failures = []

    def check(ok, message):
        print(("PASS  " if ok else "FAIL  ") + message)
        if not ok:
            failures.append(message)

    skill_path = ROOT / "SKILL.md"
    if not skill_path.is_file():
        check(False, "SKILL.md exists")
        return 1
    skill = skill_path.read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---\n", skill, re.S)
    name = re.search(r"^name:\s*(\S+)\s*$", front.group(1), re.M) if front else None
    version = re.search(r'^\s+version:\s*["\']?(\d+\.\d+\.\d+)["\']?\s*$', front.group(1), re.M) if front else None
    check(bool(name and version), "SKILL.md frontmatter has name and semantic metadata.version")

    readme = ROOT / "README.md"
    sources = [skill] + ([readme.read_text(encoding="utf-8")] if readme.is_file() else [])
    named = sorted({p for text in sources
                    for p in re.findall(r"\b((?:references|scripts|tests)/[\w./-]+\.(?:md|json|py))", text)})
    missing = [p for p in named if not (ROOT / p).is_file()]
    check(not missing, f"{len(named)} paths named in SKILL.md/README.md exist"
          + (f" (missing: {', '.join(missing)})" if missing else ""))

    skill_words = words(skill)
    check(skill_words <= args.max_skill_words,
          f"SKILL.md is {skill_words} words (budget {args.max_skill_words})")
    routed = sorted({ROOT / p for p in re.findall(r"\b(references/[\w./-]+\.md)", skill)})
    sizes = {p: words(p.read_text(encoding="utf-8")) for p in routed if p.is_file()}
    runtime = skill_words + sum(sizes.values())
    largest = max(sizes, key=sizes.get) if sizes else None
    check(runtime <= args.max_runtime_words,
          f"SKILL.md plus {len(sizes)} routed references is {runtime} words (budget {args.max_runtime_words}"
          + (f"; largest {largest.relative_to(ROOT)} at {sizes[largest]})" if largest else ")"))
    unrouted = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "references").glob("*.md")
                      if str(p.relative_to(ROOT)) not in named)
    if unrouted:
        print("INFO  references not named in SKILL.md or README.md: " + ", ".join(unrouted))

    eval_path = next((ROOT / p for p in EVAL_FILES if (ROOT / p).is_file()), None)
    if eval_path is None:
        check(False, "an eval case file exists")
    else:
        try:
            cases = json.loads(eval_path.read_text(encoding="utf-8"))["cases"]
            ids = [c.get("id") for c in cases]
            malformed = [c.get("id", f"#{i}") for i, c in enumerate(cases)
                         if not c.get("id") or not c.get("prompt")
                         or not (c.get("expectations") or c.get("expect"))]
            categories = {c.get("category") for c in cases if c.get("category")}
            check(len(ids) == len(set(ids)), f"{len(cases)} eval case ids are unique")
            check(not malformed, "every eval case has id, prompt, and expectations"
                  + (f" (malformed: {', '.join(map(str, malformed))})" if malformed else ""))
            gaps = sorted(REQUIRED_CATEGORIES - categories)
            check(not gaps, "categorized eval cases cover required behavior categories"
                  + (f" (missing: {', '.join(gaps)})" if gaps else ""))
            no_prohibition = [c["id"] for c in cases if c.get("category") and not (
                c.get("prohibitions") or (c.get("expect") or {}).get("prohibit"))]
            check(not no_prohibition, "categorized cases state prohibitions"
                  + (f" (missing: {', '.join(no_prohibition)})" if no_prohibition else ""))
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            check(False, f"{eval_path.name} parses ({exc})")

    bad_python = []
    for path in sorted(ROOT.rglob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (SyntaxError, UnicodeError) as exc:
            bad_python.append(f"{path.relative_to(ROOT)}: {exc}")
    check(not bad_python, "Python files compile" + (f" ({'; '.join(bad_python)})" if bad_python else ""))

    litter = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
              if p.name in LITTER or p.is_symlink() or p.suffix == ".pyc"]
    if args.release:
        check(not litter, "no caches, symlinks, or OS files" + (f" ({', '.join(litter)})" if litter else ""))
    elif litter:
        print(f"INFO  {len(litter)} cache or OS file(s) present; --release fails on them")

    plugin_root = ROOT.parent.parent
    manifests = [plugin_root / p for p in ("plugin.json", ".claude-plugin/plugin.json",
                                           ".codex-plugin/plugin.json")]
    manifests = [p for p in manifests if p.is_file()] if ROOT.parent.name == "skills" else []
    if manifests and version:
        stale = []
        for manifest in manifests:
            try:
                if json.loads(manifest.read_text(encoding="utf-8")).get("version") != version.group(1):
                    stale.append(str(manifest.relative_to(plugin_root)))
            except ValueError:
                stale.append(str(manifest.relative_to(plugin_root)) + " (invalid JSON)")
        check(not stale, f"{len(manifests)} plugin manifests carry version {version.group(1)}"
              + (f" (mismatch: {', '.join(stale)})" if stale else ""))

    print(f"\n{len(failures)} failure(s)" if failures else "\nPackage validation passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
