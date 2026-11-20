# Release states and execution

## Define the endpoint

“Prepare” means a concrete reviewable result: build/export artifact, metadata/assets, readiness findings and an execution plan. “Upload” moves a build to processing; it does not inherently distribute it to groups. “TestFlight” can include upload, beta review, selected group access and notification, but the exact requested scope decides which. “Submit for review” is distinct from approval and release. Public release may be manual, automatic or phased according to existing configuration.

Resolve app bundle identifier and App Store app ID, platform, marketing version, build number/ID, team/provider and any existing version/submission IDs. Do not use a global default app without verifying it. Keep one selected binary through the flow; immediately after upload a “latest” query may still return a previous build.

## Select a lane

Use the repository’s established fastlane, asc, EAS or CI lane when it is trusted and fits the task. Do not mix two mutation orchestrators for the same version. For an existing asc installation, discover the available release surface:

```sh
asc --help
asc release --help
asc review --help
asc publish --help
asc testflight --help
```

Inspect leaf help before constructing commands. Typical logical lanes are stage an existing build, submit an already prepared version, upload/build then publish, or assemble a lower-level multi-item review. The actual commands and fields come from installed help. If one lane created a draft or active review, inspect it before continuing with another lane.

Prepare-only work must not invoke an upload/publish operation disguised as an export helper. Read options that combine export and upload. Local output generation and read-only remote validation can proceed within scope; no placeholder release or test submission should be created to check connectivity.

## Readiness dependencies

Check intended build processing/validity, version/platform correspondence, signing, localizations, screenshots, review contact/demo access, encryption/content-rights/age/privacy declarations, availability and any required digital goods. Require truthful user-provided business/legal facts; never fill a declaration merely to make validation pass.

If the lane stages an existing build, attach that build before treating “no build attached” as a readiness blocker. Other blockers should be repaired and verified before submission. Versioned IAP, subscription or Game Center items may need coordinated preparation; inspect current API/CLI support and exact related IDs.

## Execute and observe

Dry-run or plan first when supported, then compare the exact app/version/build/assets and mutation list with scope. Existing user authorization covers the stages they asked for; confirmation flags implement the selected command and do not require asking the same question again. If a necessary action expands scope, complete independent preparation and ask only for that new effect.

Wait using bounded polls when subsequent stages depend on processing. A process timeout is not proof of remote failure. Read back the resource, status and attachments after a mutation, record receipts and proceed only from verified state. Avoid sending tester invitations/notifications as an incidental side effect of artifact upload.
