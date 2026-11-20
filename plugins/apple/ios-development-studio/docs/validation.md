# Verification scope

The package includes a validator and deterministic helper tests. The final [validation result](validation-results.json) records the executed suite and package/archive checks for this release. [Native host evidence](native-host-verification.json) records isolated Claude Code 2.1.310 and Kimi Code 2.3.3 installation/discovery results; each discovered all 26 skills without a model conversation.

## What the checks establish

- Portable manifest syntax, required metadata, semantic version, category and listing constraints used by this package.
- Unique skill entrypoints, matching YAML names, optional agent metadata and contained file links/assets.
- Archive layout, duplicate/traversal/symlink handling, dependency/secret exclusions and known unwanted feedback commands.
- Read-only discovery behavior for synthetic native, Expo, tooling-only EAS, malformed JSON, lockfile and symlink inputs.
- Keyword routing behavior against [routing fixtures](../tests/fixtures/routing.json), including non-iOS negative requests.

Mutation tests verify that broken packages are rejected. Routing fixtures exercise the bundled deterministic aid, not the host's language-model selection. Skill-specific activation fixtures are review scenarios and acceptance checklists; they are not recorded model executions. The validator is defense in depth, not a complete secret scanner or semantic proof of every guide.

## What still needs the target environment

Xcode builds, simulator/physical-device UI behavior, Instruments recordings, real signing/export, live provider delivery, App Store/Expo account mutations and model-driven skill invocation must be verified where those tools and projects are available. Native host installation and skill discovery were exercised separately from model-driven execution. No Swift snippets were compiled as part of this Linux package build. Source-reviewed API fragments are examples for adaptation to a resolved project, not standalone compiled applications.

The private plugin creation result establishes account saving and the host's reported ingestion result. It does not establish that optional tools exist, the user selected the plugin in another task, or an iOS app passed its checks. Inspect ingestion diagnostics and retain exact plugin/release identifiers in the build record.

## Reproduce

From the package root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_plugin.py --expected-skills 26 --json
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_kimi.py --json
```

For archive validation add `--archive` with the built ZIP path. If the official JSON schema and jsonschema are already available, add `--schema` with the local schema file. Rebuild and validate the archive again after any substantive source edit.

The research process used manual source-evidence review because optional local research accelerator projects were absent. [Research decisions](research-decision.md), [live source review](upstream-review.md), source/claim ledgers and input hashes are retained. No automatic research PASS or verified_claims.json is claimed.
