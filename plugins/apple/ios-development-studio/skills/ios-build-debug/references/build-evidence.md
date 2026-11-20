# Build and test evidence

## Discover before building

Read repository build instructions as project context within the shared operating contract. Inspect Xcode project/workspace names, shared schemes, test plans, package resolution and CI configuration. Prefer the project’s established script when its implementation is understood. A package manifest does not prove the entire iOS app can be checked with `swift test`; separate platform-independent packages from Apple-framework targets.

On macOS, harmless discovery includes checking the installed Xcode selection, tool versions and help. Do not change the selected Xcode or install a toolchain as routine diagnosis. Example discovery commands, used only when these tools exist:

```sh
xcode-select -p
xcodebuild -version
xcodebuild -help
xcrun simctl help
```

Inspect installed help for project/scheme/destination listing and supported result-bundle options. Choose exactly one project or workspace selector. If multiple schemes or destinations fit, use CI configuration and the user’s goal to resolve them; ask only when that choice materially changes the result. Record the target simulator UDID or device destination rather than assuming the newest runtime is installed.

## Reproducible execution

Keep derived data and result artifacts in the project’s accepted output location, outside source inputs. Use a fresh result bundle path for every run; an old bundle must not be mistaken for the new result. Preserve stdout, stderr and actual process status when introducing a log formatter or pipe.

The following is a template, not a command to run with unresolved placeholders. Confirm each flag with installed help and replace the variables with resolved values:

```sh
xcodebuild -workspace "$IOS_WORKSPACE" -scheme "$IOS_SCHEME" \
  -configuration Debug -destination "platform=iOS Simulator,id=$IOS_SIMULATOR_UDID" \
  -resultBundlePath "$IOS_RESULT_BUNDLE" test
```

Use `-project` instead of `-workspace` for a project-only build. Choose a focused test selection only after discovering the actual test identifiers and test-plan configuration. Preserve user-selected test environments, launch arguments and locale. Do not disable signing, sanitizers or tests merely to turn a failed check green. A simulator build can reasonably use the project’s existing unsigned simulator lane; a device archive has different signing requirements.

## Interpret the artifact

Read both exit status and result contents. Inspect the installed `xcresulttool` help before choosing its current subcommands; never assume a copied JSON schema or old command spelling. Distinguish build diagnostics, test discovery, test execution, assertion failures, launch failures and infrastructure failures. Name skipped tests and their reason. Keep screenshots/logs from a failed UI test associated with the exact run.

Do not silently retry mutating prebuild hooks or remote dependency resolution without understanding their side effects. Cache deletion and full clean builds are diagnostic experiments, not a default first step. If a clean build is necessary, scope it to the task’s derived artifacts and preserve project files.

## Archive versus simulator proof

An `.xcarchive`, exported `.ipa` and simulator `.app` are distinct artifacts. A simulator app is not a signed device package. Inspect the installed `xcodebuild` or `asc xcode` archive/export help and the repository’s export options before producing an artifact. Validate bundle identity, version/build number, platform, architecture and expected executable. Read entitlements and provisioning when delivery needs them; avoid printing private signing material.

If the user requested only local preparation, artifact creation does not authorize upload, tester notification or review submission. Move to the release workflow with a clear handoff containing artifact path, build identity and checks.
