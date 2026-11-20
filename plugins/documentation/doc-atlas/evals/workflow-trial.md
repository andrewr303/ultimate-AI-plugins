# Doc Atlas instruction trial

Completed one real, bounded workflow exercise using the actual packaged `repo-docs` and `docs-readme` instructions. This was manual agent execution against an original synthetic fixture, not a host-trigger test or a broad model benchmark.

## Fixture and inspection

Created `repo/pyproject.toml`, a standard-library Python CLI under `repo/src/tinyroute/`, and three unittest cases under `repo/tests/`. The public source contract accepts `--name NAME`, prints `Hello, NAME!`, and exposes argparse's `--help`. The manifest specifies Python 3.10 or newer. No license file was created.

The initial README deliberately advertised a nonexistent `--fast` flag, made an unsupported speed claim, displayed an MIT license badge without evidence, and linked to a missing manual. Before editing, inspected the manifest, CLI parser, module entrypoint, tests, README, and absence of a license file. Read the packaged main router, README skill, evidence/safety reference, quality bar, and deliverable contract.

## Applied workflow

Rewrote only the fixture README after source inspection. The result has a short factual opening, the real source-checkout command with its working-directory and shell prerequisite, observed expected output, help, and test instructions. It uses descriptive links to the actual parser and tests. Removed the unsupported flag, speed claim, fake badge, and nonexistent manual link. No screenshot, decorative image, framework migration, or new dependency was needed for this tiny CLI.

The documentation repair did not change the source, manifest, or tests: their SHA-256 hashes match before and after the README edit.

## Actual checks

From the isolated fixture repository with `PYTHONPATH=src`:

| Check | Result |
| --- | --- |
| `python -m tinyroute --name Ada --fast` | Exit 2; argparse rejects the invented option |
| `python -m tinyroute --name Ada` | Exit 0; stdout is exactly `Hello, Ada!` followed by a newline |
| `python -m tinyroute --help` | Exit 0; lists required `--name NAME` and built-in help |
| `python -m unittest discover -s tests -v` | Exit 0; three meaningful contract tests passed |
| Bundled `docs_check.py --root . --path README.md` before repair | Exit 1; missing manual link detected; remote badge and extensionless license destination unresolved |
| Same checker after repair | Exit 0; one file checked, no findings, no unresolved destinations |

The checker did not detect the invented flag or prove the license badge false; those repairs required source inspection. This distinction is part of the exercise.

## Criterion verdicts

All seven bounded criteria passed: unsupported flag removed, fake license badge removed, documented commands work, expected output matches, useful next navigation, local links/preflight clean, and source unchanged by the documentation repair.

Exact command arguments, stdout/stderr, exit codes, before/after README contents, evidence, hashes and limitations are recorded in `result.json`. The repaired reader-facing artifact is `repo/README.md`.

## Limits

No host installation, automatic skill triggering, GitHub browser rendering, mobile/light/dark review, external-link checking, live API request, or accessibility certification was exercised. This one fixture establishes only the recorded workflow outcome. The offline preflight remains a conservative Markdown subset check. No plugin files were modified by this trial.
