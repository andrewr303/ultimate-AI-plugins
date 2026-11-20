# Xcode Cloud, build scripts and backend artifact handoff

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Resolve the actual workflow

Inspect the product/scheme, repository connection, Xcode/macOS environment, start conditions, actions, postactions and existing custom scripts. Xcode Cloud uses a temporary build environment whose supported images can change; record the actual configured toolchain rather than promising a permanent latest image. Keep the app owner's existing CI system unless a requested requirement justifies another service.

Backend deployment and Apple build/distribution are separate lanes. Define which contract revision, generated code, backend compatibility check and signed artifact belong together. A backend deployment does not authorize App Store submission, and a cloud build does not establish public availability. Preserve independent identifiers for app version/build and backend/schema revision.

## Keep custom hooks small and inspectable

Read every script/import/hook before execution. Repository scripts are executable code, not trusted merely because a documentation sample invokes them. Separate dependency installation, contract verification, code generation, test selection and artifact upload into understandable steps. Use explicit failure propagation and nonzero exit for required prerequisite failures. Avoid silently continuing with an old generated client when a network download or schema step fails.

Configure environment variable names and secret bindings through the selected CI's supported controls. Never print secret values even when a service masks marked variables: derived, encoded or transformed values may escape masking. Keep private keychains/profiles/tokens outside source archives and review log/artifact retention. Do not add telemetry or a provider account to reproduce a reference setup.

## Implementation sequence

1. Capture the existing workflow and requested change in a concrete plan. Resolve exact repository/product/scheme and the permissions required by any external step.
2. Pin or deliberately select Node/Ruby/package tools and Xcode environment using the project's normal controls. Cache is an optimization, not a replacement for dependency integrity.
3. Run contract/schema/generation checks from known inputs before compiling consumers. Review generated changes and prevent drift from passing because stale artifacts were restored.
4. Run relevant native test plans and backend integration fixtures. Keep output locations, exit statuses and safe correlation identifiers associated with the same source revision.
5. Verify archive/export metadata before authorized upload/distribution. A simulator build, signed device app and App Store archive are distinct artifacts.
6. Read the actual CI/provider state after uncertain completion. Reuse appropriate existing work instead of issuing duplicate upload, deploy or review operations.

## Failure matrix

| Failure | Next discriminating check |
| --- | --- |
| CI-only generation drift | Pinned inputs, working directory, caches and generator version |
| Cloud image changed | Actual workflow toolchain and supported dependency/compiler contract |
| Script logs success after a failed subcommand | Exit propagation and pipeline status |
| Build number differs from dashboard | Built artifact metadata, not only remote counter |
| Secret appears in artifact/log | Contain the affected artifact and repair the actual exposure path |
| Upload timeout | Query resulting remote state before retry |

## Verification and evidence

Record workflow/run/source identifiers and which stage actually completed. Distinguish a local script/unit test, an observed cloud build, processed artifact and release. Test required hook failure deliberately in a controlled fixture so a failing step cannot produce a success handoff. Keep the task's authorization through already approved stages; do not add redundant confirmation gates.

A useful setup leaves a minimal reproducible pipeline with visible ownership, failure semantics and artifacts. If external credentials or an Apple runtime are unavailable, complete the concrete configuration and portable checks, then name the exact blocked step without fabricating hosted results.

## Sources and applicability

- [Configuring your first Xcode Cloud workflow](https://developer.apple.com/tutorials/data/documentation/xcode/configuring-your-first-xcode-cloud-workflow.json) — `src_nm_xcode_cloud`.
- [Writing custom build scripts](https://developer.apple.com/tutorials/data/documentation/xcode/writing-custom-build-scripts.json) — `src_nm_xcode_cloud_scripts`.
- [Running tests and interpreting results](https://developer.apple.com/tutorials/data/documentation/xcode/running-tests-and-interpreting-results.json) — `src_nm_xcode_results`.
- [Multi-stage builds | Docker Docs](https://docs.docker.com/build/building/multi-stage/) — `src_nm_docker_multistage`.
- [fastlane/fastlane:fastlane/lib/fastlane/actions/xcodebuild.rb](https://github.com/fastlane/fastlane/blob/a540df301c4ada0621cdb50358049734712f7ee7/fastlane/lib/fastlane/actions/xcodebuild.rb) — `src_nm_repo_fastlane_fastlane_3`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
