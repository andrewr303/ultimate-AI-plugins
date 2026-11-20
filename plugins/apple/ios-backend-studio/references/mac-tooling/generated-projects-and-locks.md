# Generated project ownership and reproducible dependency inputs

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Identify the authority artifact

Determine whether Xcode project files are hand-maintained, generated from a spec/Swift manifest or derived by an existing package workflow. Read the actual project instructions and generation task. Generated-project tools can reduce conflict and duplicated configuration, but introducing one is a migration with product/team tradeoffs, not a universal first step for backend integration.

For each output, document its owning input: API description to generated client, project manifest to Xcode project, package manifest/lock to resolved dependency graph, runtime file to local/CI executable selection. Do not maintain a second hand-edited representation that silently diverges. Preserve unrelated user changes and inspect the diff before regeneration.

## Choose a proportional workflow

The inspected XcodeGen implementation composes PBX project, workspace and scheme outputs from a project description. The inspected Tuist service checks whether the configured project is a generated project or Swift package before generation. Use these as evidence to respect existing ownership. Do not run a tool's generation command over an arbitrary native host or add its cloud/cache service merely because local generation exists.

Keep dependency locking distinct from tool inventory. A Brewfile does not lock exact formula versions, a selected Xcode installation does not pin Swift packages, and a Node lockfile does not select the deployed Node runtime. Record the actual authority for each layer and align it with CI. Avoid uncontrolled remote schema/config inputs in a supposedly deterministic generator task.

## Change sequence

1. Map existing generated artifacts and determine whether they are checked in or build outputs. Verify the local project's expected convention before deleting or committing anything.
2. Make the requested change in the owning manifest/spec/schema. Keep target identifiers, signing, build phases, resources, extension membership and package products deliberate.
3. Run the pinned existing generation task in the intended root. Inspect generated changes for unexpected defaults, target removal, secret paths or machine-specific absolute values.
4. Build affected targets/configurations and run relevant payload/target tests. A clean generated diff is not evidence that app or extension code compiles.
5. Compare a second controlled generation from the same inputs if nondeterminism is the actual concern. Do not repeat broad generation solely to create reassuring output.
6. Document how a developer and CI resolve the same inputs, and what legitimate environment-specific settings remain external.

## Failure cases

| Problem | Correct repair direction |
| --- | --- |
| Regeneration removes a manual fix | Move the fix to the owned input or intentionally change ownership |
| Schemes disappear | Compare generator settings and shared-scheme definitions |
| Extension loses dependency/resource | Check target membership in the source manifest and generated output |
| Fresh checkout resolves differently | Inspect runtime/generator/dependency pins and remote inputs |
| Cache hides a missing dependency | Validate the declared build graph with relevant cache assumptions visible |
| Tool source has mixed licensing | Use the selected tool's actual distribution/terms; do not vendor a monorepo under a blanket license claim |

## Verification and provenance

Report input revisions, resolved tool versions, command, generated diff and actual target checks. Main-branch code/tests inspected during research are evidence of mechanisms, not proof the user's pinned release behaves identically. Tuist's root notice contains mixed-license statements; the plugin does not copy or redistribute that implementation.

A low-maintenance setup has one clear source per generated artifact and small deterministic tasks. It preserves existing project choices rather than forcing every app into a shared UI framework or new build system.

## Sources and applicability

- [Projects · Features · Guides · Tuist](https://docs.tuist.dev/en/guides/develop/projects) — `src_nm_tuist_projects`.
- [Swift Package Manager](https://docs.swift.org/latest/data/documentation/packagemanagerdocs.json) — `src_nm_swift_package_json`.
- [Tasks | mise-en-place](https://mise.jdx.dev/tasks/) — `src_nm_mise_tasks`.
- [Homebrew Documentation: Homebrew Bundle, brew bundle and Brewfile](https://docs.brew.sh/Brew-Bundle-and-Brewfile) — `src_nm_brew_bundle`.
- [yonaskolb/XcodeGen:Sources/XcodeGenKit/ProjectGenerator.swift](https://github.com/yonaskolb/XcodeGen/blob/783a19e863ff906e042d061aa0a1d569d3c52ffa/Sources/XcodeGenKit/ProjectGenerator.swift) — `src_nm_repo_yonaskolb_xcodegen_3`.
- [tuist/tuist:cli/Sources/TuistKit/Services/GenerateService.swift](https://github.com/tuist/tuist/blob/5c73f508f6367877751be4d730715e3a1ed82d8c/cli/Sources/TuistKit/Services/GenerateService.swift) — `src_nm_repo_tuist_tuist_3`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
