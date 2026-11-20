# Signing artifacts and secret handling

## Prepare a concrete export

Use the project’s existing Xcode or CI export lane when understood. If `asc xcode` is available and fits the requested flow, inspect its installed archive/export help; otherwise use supported Xcode export options. Do not force an extra CLI into a project merely because an uploaded skill prefers it.

Choose the actual method accepted by the installed tool and required by the destination. Do not assume old ad-hoc spellings or a copied export plist remain valid. A registered-device artifact needs the right devices/profile; a TestFlight/App Store artifact has a separate contract. A simulator `.app` cannot be substituted for either.

Before export, inspect workspace/project, scheme, Release configuration, archive path and bundle/build identity. Use unique output paths or deliberately scoped overwrites. Separate local export from direct-upload options; some helper flags can upload as well as export. Confirm the chosen lane’s effects through help before execution.

After export, inspect the artifact’s expected format, platform/architectures, bundle/version/build, app/extension entitlements and provisioning relationships. Verify installability on the requested device when authorized and available. Report static inspection separately from actual device installation.

## Minimize credential persistence

Use host-managed auth, OS keychain, protected CI secrets or private files selected by path. Never print P8, P12, PEM, private key, passwords, bearer tokens, recovery codes or session-cookie values. Avoid inline password flags and shell history exposure. Do not infer missing auth solely because no plain token appears in the environment.

If a tool supports an isolated temporary keychain/profile run, inspect its guarantees and preserve the child exit code. An ephemeral wrapper does not authorize access to every local identity. Stop and report cleanup failures affecting private artifacts rather than claiming the environment is restored.

Encrypted team synchronization still moves private material. Use a caller-owned destination, inspect the sync workflow, protect password/key files and establish whether the material includes an actual private identity. Do not invent a signing repository or push credentials to an upstream example. Downloading or decrypting an identity is distinct from importing it into a keychain.

## Cleanup and rotation

Prepare a specific list before deleting profiles or revoking certificates. Reuse session authorization for the approved scope; do not request redundant confirmation solely because a tool has a confirmation flag. Ask when the newly discovered effect would remove unrelated/shared access or otherwise exceed the task.

Scope local cleanup to exact expired or task-created resources and inspect the resolved directory first. Do not delete every profile, reset a keychain or clear web auth to solve an isolated export problem. Keep nonsecret receipts needed for audit and resume.

## Handoff

Provide artifact path/hash when useful, app/platform/team identifiers, version/build, export method, nonsecret certificate/profile IDs, checks performed and pending validation. Mention what was created or changed and whether private temporary files remain. Upload/distribution/review continues in the release workflow under the same task scope.
