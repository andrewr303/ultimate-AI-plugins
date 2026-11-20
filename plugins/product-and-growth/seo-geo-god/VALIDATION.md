# Validation

Results of the checks run against version 1.0.1 on 2026-11-10. Host loading (installing the plugin in Codex, Claude Code or another host) was not part of these checks beyond the Claude Code manifest validator below.

| Check | Command (run from the repository root) | Result |
| --- | --- | --- |
| Unit and contract tests | `cd plugins/seo-geo-god && python3 -m unittest discover -s tests` | 937 tests, OK |
| Package validator | `python3 -I -B plugins/seo-geo-god/scripts/validate_plugin.py plugins/seo-geo-god` | Passed (exit 0, 46 routing scenarios, 7 data files, 4 schemas); the ZIP built by `package_plugin.py` also passed `--archive` validation (362 members) |
| Claude Code manifest validator | `claude plugin validate --strict plugins/seo-geo-god` | Validation passed (an advisory about a marketplace install line in this README does not change the result) |
| Repository plugin lint | `python3 -I docs/research/plugin-improvement-2026-11-10/tools/plugin_lint.py plugins/seo-geo-god` | 0 errors, 0 warnings |

The tests install a network sentinel and make no network requests. What each part of the suite covers is described in the README section on tests.

Earlier release: 1.0.0 (2026-11-03) shipped without this file, and `validate_plugin.py` reported the missing file. No results were recorded for 1.0.0.
