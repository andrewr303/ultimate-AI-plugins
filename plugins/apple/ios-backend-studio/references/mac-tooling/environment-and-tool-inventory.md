# Mac environment inventory, runtime pins and local services

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inventory before changing the workstation

Read project instructions and tool files, selected Xcode, Node/package-manager versions, Ruby/Bundler settings, simulator runtimes, container engine/context and local services. Discover executable presence/version without dumping environment values or credential stores. An available binary does not prove a healthy installation, selected account, valid license or successful build.

Preserve the user's chosen tools and running applications. A reference to Homebrew, mise, Colima or Docker is an optional supported lane, not permission to install it. A task that needs setup should identify the smallest missing prerequisite and its concrete consequence. Do not switch a global Xcode path, stop a user's VM or rewrite shell startup files as routine diagnosis.

## Inventory is not exact pinning

Homebrew Bundle documents tools in a Brewfile and explicitly does not provide a Brewfile lockfile. Its install operation can upgrade existing packages. Inspect what a proposed command changes and use supported no-upgrade behavior where that matches the task. Treat the Brewfile as onboarding inventory rather than a complete reproducibility claim.

Pin language/runtime and package dependencies through the project's established mechanisms: actual runtime-version/task configuration, Node lockfiles, Ruby lockfiles and selected Apple toolchain. Inspect version resolution in CI as well as local shells. Avoid stacking multiple competing runtime managers just because each appears in the reference library.

## Implementation sequence

1. Produce a small nonsecret inventory: project roots, selected toolchain, required executables, configured runtime versions and observed versions. Keep unknowns explicit.
2. Compare local and CI resolution. Resolve a mismatch at its actual source rather than adding unexplained PATH overrides or deleting dependency directories.
3. Expose a few stable project tasks for contract checks, backend tests and native build/test. Read the task definitions as code before execution.
4. Check task ordering: mise prerequisites may run in parallel, so their listed order is not a sequencing guarantee. Use explicit ordered steps when generation must precede compilation or migrations must precede a dependent release action.
5. If local containers are required, reuse the selected engine/context and inspect ports, volumes and data ownership. Colima startup manages a VM/runtime and needs appropriate client tools; do not silently provision or resize it.
6. Start and clean up only the processes/services created for the task, with captured identity. Keep disposable development data separate from persistent customer or production data.

## Failure matrix

| Symptom | Check |
| --- | --- |
| Different Node version in CI | Actual version-manager resolution and deployment image, not shell aliases alone |
| Brewfile satisfied but app differs | Runtime/package locks and selected Xcode remain separate |
| Build races generated files | Task dependency semantics and explicit ordered steps |
| Docker points at wrong data | Current context, socket, volume and project namespace |
| Signing works only in one shell | Selected identity/keychain access and build process context |
| Setup asks for broad privileges | Confirm the exact necessary operation; prepare independent work first |

## Verification and handoff

Run only relevant read-only discovery and the authorized setup/check commands. Record before/after tool selection and actual tests. A completed install is not a passing app build or backend deployment. Do not log tokens, private key material, full environment dumps or user-specific container contents.

The goal is a small shared task interface across Mac and backend CI, with native platform steps kept explicit. It does not require identical operating systems or pretending a Linux backend host can execute Xcode.

## Sources and applicability

- [Homebrew Documentation: Homebrew Bundle, brew bundle and Brewfile](https://docs.brew.sh/Brew-Bundle-and-Brewfile) — `src_nm_brew_bundle`.
- [Tasks | mise-en-place](https://mise.jdx.dev/tasks/) — `src_nm_mise_tasks`.
- [colima](https://raw.githubusercontent.com/abiosoft/colima/main/README.md) — `src_nm_colima`.
- [Process | Node.js v26.12.1 Documentation](https://nodejs.org/api/process.html) — `src_nm_node_process`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
