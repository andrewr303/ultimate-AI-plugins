# CI recipes

How to run the SEO-GEO-god checks as deterministic regression gates in a repository's build and CI: which rules to block on, how to make the CLI available, package-script and CI configurations, baselines and drift comparisons, a guard for layout edits, optional local hooks and their risks, and how to keep outputs reproducible. Used by [seo-ci-guard](../skills/seo-ci-guard/SKILL.md). Every command and flag is listed in [cli-reference.md](cli-reference.md); rule details are in [rule-catalog.md](rule-catalog.md).

As of 2026-11-01. Nothing in this file is enabled by installing the plugin; every recipe is a file the user copies on purpose.

## Principles

- **Advisory by default.** The CLI exits 0 unless `--fail-on` is given. A gate exists only where someone chose it.
- **Report first, then fail.** The full report is written to stdout or `--output` before a gate exits 1, with a one-line reason on stderr.
- **Offline checks.** Gates run on build output and source files. The only network use in CI is an optional, explicitly configured smoke test against the owner's own preview URL.
- **Least privilege.** `permissions: contents: read`, `persist-credentials: false`, no secrets, inputs through environment variables (never `${{ }}` expansions inside shell scripts).
- **Pinned dependencies.** Third-party actions are pinned to full commit SHAs that the user verifies; templates show `<FULL_COMMIT_SHA>` placeholders and never contain invented SHAs. Container images are pinned by digest.
- **Deterministic.** Same input, same report bytes: set the timestamp with `--now` or `SEO_GEO_GOD_NOW`.

## Exit codes

| Code | Meaning | CI reaction |
| --- | --- | --- |
| 0 | Completed; no gate tripped | pass |
| 1 | Gate tripped (`--fail-on` threshold, `fidelity` failed, `drift compare --fail-on` reached) | fail with the report attached |
| 2 | Usage or input error (bad flag, unreadable or oversized input, invalid JSON or CSV) | fail; fix the job |
| 3 | Refused by safety policy (network without `--live`, blocked target, output inside the audited directory) | fail; fix the job |
| 4 | Internal error (a JSON envelope with `error` is still printed) | fail; report the bug |

## Gate selection

Default blocking set: findings that ship broken indexing, broken markup or staging artifacts. Everything else stays advisory until the team decides otherwise.

| Rule | Why it blocks |
| --- | --- |
| [SD001](rule-catalog.md#sd001), [SD002](rule-catalog.md#sd002) | JSON-LD that cannot be parsed or has the wrong shape |
| [SD006](rule-catalog.md#sd006) | Placeholder values shipped in structured data |
| [SD012](rule-catalog.md#sd012) | `</script` or unescaped `<` inside JSON-LD (markup breakout) |
| [CANON002](rule-catalog.md#canon002), [CANON003](rule-catalog.md#canon003) | Several canonicals, or a relative or malformed canonical |
| [CRAWL004](rule-catalog.md#crawl004) | robots.txt disallows the whole site for all crawlers |
| [AI004](rule-catalog.md#ai004) | Googlebot or Bingbot blocked, which removes the site from Search and its AI features |
| [LAUNCH003](rule-catalog.md#launch003) | localhost, staging or preview URLs in canonical, `og:url`, hreflang, sitemap or JSON-LD |
| [LAUNCH004](rule-catalog.md#launch004) | Site-wide noindex or a staging robots.txt shipped |
| [IDX001](rule-catalog.md#idx001) | A page is noindex (error with `--expect-indexable`) |

Two ways to gate:

1. **Rule set** (default in the templates): run with `--fail-on never`, then fail when the JSON report contains a finding whose `rule` is in `SEO_BLOCKING_RULES`. Teams can start strict on these and leave the rest advisory.
2. **Severity**: `--fail-on error` (or `warning`) trips on any finding at that severity. Use it once existing errors are fixed, or on new projects.

Choose `--expect-indexable` only for builds meant to be indexed (production artifacts). Preview builds that intentionally carry noindex should be audited without it.

## Making the CLI available in CI

The CLI is plain Python 3.9+ standard library; there is nothing to install. CI needs a copy of the plugin directory:

- **Committed copy** (simplest): copy the whole `seo-geo-god` plugin directory into the repository, for example at `tools/seo-geo-god/`, and record the plugin version in the commit message. Updates are deliberate commits that reviewers can read.
- **Pinned checkout**: check out the repository that hosts the plugin at a full commit SHA you verified (the templates show this as a commented alternative). Never track a branch.

Invoke it as `python3 -I tools/seo-geo-god/scripts/seo_geo.py …`. The `-I` flag keeps `PYTHONPATH`, user site-packages and the current directory out of the import path.

Add `.seo-geo-god/` to `.gitignore`, except for baselines the team decides to commit (for example `!.seo-geo-god/baselines/`).

## Package scripts

Add an explicit script instead of hiding the check inside `build`:

```json
{
  "scripts": {
    "build": "astro build",
    "seo:check": "python3 -I tools/seo-geo-god/scripts/seo_geo.py audit-build dist --base-url https://www.example.com --expect-indexable --fail-on error --format text"
  }
}
```

- npm runs a `postbuild` script automatically after `npm run build`. That works as a local gate, but it surprises people who only wanted a build; prefer `npm run build && npm run seo:check` in CI.
- pnpm does not run `pre` and `post` scripts for custom scripts unless `enable-pre-post-scripts` is set (verify for the installed pnpm version); call `pnpm run seo:check` explicitly.
- Build output directories differ by framework (`dist/` for Astro and Vite, `out/` for Next.js static export, `public/` for Hugo, `_site/` for Eleventy and Jekyll, `build/` for Docusaurus). `SG stack` reports the detected one; server-rendered apps have no static output and are checked against a local production server instead (see the last section).

## GitHub Actions

Template: [github-actions.example.yml](../templates/ci/github-actions.example.yml). Copy it to `.github/workflows/seo-geo.yml` and edit the `env` block.

What the template does, in order:

1. Checks out the repository with `persist-credentials: false`; workflow-level `permissions: contents: read`; triggers on `pull_request`, pushes to `main` and manual runs (never `pull_request_target`).
2. Sets up Python and Node.js with actions pinned to `<FULL_COMMIT_SHA>` placeholders, then runs the project's build.
3. Validates every input (origin must be `https://`, known profile and gate values, relative paths without `..`, rule IDs only) and stops with exit 2 on bad input.
4. Sets `SEO_GEO_GOD_NOW` from the commit time, so a rerun of the same commit produces the same reports.
5. Runs `audit-build` three times on the same input to produce Markdown (added to the job summary), SARIF and JSON reports under `.seo-geo-god/ci/`; optionally lints source templates with `jsonld --recursive` and compares against a committed drift baseline.
6. Applies the gates in a small Python step that reads the JSON report: blocking-rule findings become `::error` annotations (file and line when known) with workflow-command characters escaped, because messages contain text from the audited pages.
7. Uploads `.seo-geo-god/ci/` as an artifact even when the gate fails.

SARIF upload to code scanning is optional and commented out: it needs `security-events: write` on the job (a write permission), code scanning must be available for the repository, and pull requests from forks do not receive that permission. Results without a file location carry only a page URL, and code-scanning views may not display those; the Markdown summary and artifact still contain them.

Pinning: replace each `<FULL_COMMIT_SHA>` with the 40-character SHA of a release you checked on the action's repository and keep the version comment (`# v4.2.0`). Update pins deliberately, for example through a dependency-update tool that proposes SHA bumps for review.

## GitLab CI

Template: [gitlab-ci.example.yml](../templates/ci/gitlab-ci.example.yml). Merge it into `.gitlab-ci.yml`.

- Two stages: `build-site` produces `dist/` as a short-lived artifact; `seo-geo-checks` audits it.
- Images are pinned by digest (`<FULL_IMAGE_DIGEST>` placeholders). No tokens or CI/CD secrets are used; the build output reaches the audit job as an artifact through `needs`.
- `SEO_GEO_GOD_NOW` comes from `CI_COMMIT_TIMESTAMP`, so reruns of a commit are reproducible.
- The Markdown report is printed to the job log; JSON, Markdown and SARIF files are kept as artifacts with `when: always`. GitLab's security reports use GitLab's own formats, so keep the SARIF file for download or for a converter the team trusts (check the current GitLab documentation before relying on any SARIF import).
- The same rule-set gate runs as an inline Python step and prints one `BLOCKING <rule> <where> <message>` line per finding.

## Other CI systems

Any runner with Python 3.9+ works. The essential sequence:

```sh
set -eu
python3 -I tools/seo-geo-god/scripts/seo_geo.py audit-build dist --base-url https://www.example.com --expect-indexable --format md --output .seo-geo-god/ci/seo-geo.md
python3 -I tools/seo-geo-god/scripts/seo_geo.py audit-build dist --base-url https://www.example.com --expect-indexable --format json --output .seo-geo-god/ci/seo-geo.json --fail-on error
```

The second command writes its report before exiting 1 when the gate trips. `--output` refuses to overwrite an existing file unless `--force` is given, and refuses paths inside the audited directory.

## Baselines and comparability

A baseline is a snapshot of page-level SEO signals (status, title, description, canonical, robots, H1, hreflang, JSON-LD types, word count, internal link count, content hash) used to catch regressions such as a removed H1 or a new noindex.

- Create it on the main branch from a known-good build: `SG drift snapshot dist --base-url https://www.example.com --output .seo-geo-god/baselines/main.json`. Commit it only if the team wants PR comparisons; regenerate it deliberately when intended changes land (a new snapshot is a reviewed commit, not an automatic job).
- In pull requests: `SG drift compare .seo-geo-god/baselines/main.json dist --base-url https://www.example.com --fail-on error`. Error-level drift includes a page removed or erroring ([DRIFT001](rule-catalog.md#drift001)), noindex added ([DRIFT002](rule-catalog.md#drift002)), canonical changed or removed ([DRIFT003](rule-catalog.md#drift003), [DRIFT004](rule-catalog.md#drift004)), title or H1 removed ([DRIFT005](rule-catalog.md#drift005), [DRIFT006](rule-catalog.md#drift006)) and JSON-LD types removed ([DRIFT010](rule-catalog.md#drift010)).
- Comparability: deltas are withheld when snapshots come from different tool major versions, different source types (build directory against live crawl) or different base URLs ([DRIFT020](rule-catalog.md#drift020)). Regenerate the baseline after upgrading the plugin's major version.
- For repeated audits, compare finding sets with `SG drift findings old.json new.json`: added, no longer observed and persisting. A finding that disappears is not proof of a fix; the check may not have run.
- Reports and baselines are only valid for the content and rules version that produced them; rerun rather than reusing old results after either changes.

## Layout edit regression guard

Before an agent or a developer changes shared layouts, head components or theme templates:

1. Build and snapshot: `SG drift snapshot dist --base-url https://www.example.com --output .seo-geo-god/baselines/pre-edit.json`.
2. Make the change, rebuild.
3. Compare: `SG drift compare .seo-geo-god/baselines/pre-edit.json dist --base-url https://www.example.com --fail-on error`.
4. Every reported change to titles, canonicals, robots directives, hreflang or JSON-LD types is either intended (say so in the PR) or fixed before merging.

Restyling work should never remove or alter head tags or JSON-LD output as a side effect.

## Proving a gate works

A gate that never fails proves nothing. Seed a defect in a scratch copy of the build output, outside the repository and outside the audited directory:

```sh
tmp="$(mktemp -d)"
cp -R dist "$tmp/dist"
sed -i.bak 's#<head>#<head><meta name="robots" content="noindex">#' "$tmp/dist/index.html"
python3 -I tools/seo-geo-god/scripts/seo_geo.py audit-build "$tmp/dist" --base-url https://www.example.com --expect-indexable --fail-on error --format text; echo "exit $?"
```

Expect exit 1 with [IDX001](rule-catalog.md#idx001) (and possibly [LAUNCH004](rule-catalog.md#launch004)). The unmodified `dist` should exit 0 for the same gate. Delete the scratch directory afterwards.

## Optional live smoke test

Only when the owner explicitly asks and owns the target: a small consented crawl of a preview deployment, for example `SG audit-url https://preview.example.com --live --max-pages 20`. Preview hosts often send noindex on purpose, so do not combine this with `--expect-indexable` unless the preview is meant to be indexable. Keep it in a separate, manually triggered job; never crawl third-party sites from CI.

## Opt-in pre-commit and agent hooks

Two inert examples ship in `templates/opt-in/`. Neither is active until a person copies it into place; agents install them only on an explicit request, and never edit `.git/hooks` directly.

| File | What it runs | Risks |
| --- | --- | --- |
| [pre-commit-config.example.yaml](../templates/opt-in/pre-commit-config.example.yaml) | `jsonld` on staged HTML and component templates, `content-lint` on staged Markdown, MDX and HTML; blocks the commit only on error-level findings | Requires the third-party pre-commit tool; adds time to each commit; bypassed by `git commit --no-verify`; template blocks with expressions are skipped in source |
| [claude-code-hook.example.json](../templates/opt-in/claude-code-hook.example.json) | A Claude Code `PostToolUse` hook that runs `jsonld` on the one file just edited and returns error findings to the agent | Runs a process after every matching edit with the user's permissions; hook semantics can change between Claude Code versions, so check the installed version's documentation first |

Each file explains how to enable it, how to verify it fails on a seeded defect, and how to disable it.

## Determinism

- `--now 2026-11-01T00:00:00Z` (or `SEO_GEO_GOD_NOW`) fixes the report timestamp; `--today 2026-11-01` fixes date-based heuristics such as stale-year checks.
- Use the commit time in CI (`git log -1 --format=%cI` on GitHub, `CI_COMMIT_TIMESTAMP` on GitLab) so reruns of one commit produce identical reports.
- Findings are sorted and their IDs are stable fingerprints, so `drift findings` and code-scanning deduplication work across runs.
- Keep the plugin version fixed per commit (committed copy or pinned SHA); a different rules version can change findings.

## Server-rendered apps

When a framework renders on request (Next.js without static export, Nuxt, SvelteKit, Remix, Angular SSR, Django, Rails, Laravel, WordPress), build it, start the production server on the runner and crawl it locally:

```sh
npm run build
npm run start -- --port 3000 &
server_pid=$!
# wait until the server answers, then:
python3 -I tools/seo-geo-god/scripts/seo_geo.py audit-url http://localhost:3000 --live --allow-local localhost:3000 --max-pages 200 --expect-indexable --format json --output .seo-geo-god/ci/seo-geo.json
kill "$server_pid"
```

`--allow-local` permits exactly that host and port; it never extends to redirects to other ports or hosts. The start command and readiness check depend on the framework; use the project's documented production start command.
