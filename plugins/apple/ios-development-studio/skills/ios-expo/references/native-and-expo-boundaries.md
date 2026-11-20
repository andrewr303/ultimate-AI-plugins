# Native, Expo and brownfield boundaries

## Detect the real project

Use an explicit Expo/EAS request or an `expo` dependency as the gate. A bare React Native app without Expo is not automatically Expo work; a SwiftUI/UIKit app is not a migration candidate just because these references are bundled. EAS can be selected for native delivery without adding React Native.

Inspect package.json/lockfile, app config, committed ios project, build scripts, deployment targets and current framework versions. Preserve the package manager and existing folder layout. Use version-matched documentation, not latest examples that may require newer SDKs. Do not upgrade SDK, replace navigation or restyle an app merely to match a reference.

For a new Expo project explicitly requested, use a supported scaffold and current stable compatible version after checking its actual requirements. For an existing project, use its conventions. Package installation/native configuration is an implementation step with effects; inspect the selected package and compatibility before running project tooling.

## UI and data

Choose platform-appropriate controls compatible with the installed SDK. Inspect installed `@expo/ui` declarations/docs if using it; do not force its absence into a dependency upgrade. Native grouped-row lists and virtualized large-data lists have different purposes. Preserve stable identity, accessibility, list performance, safe areas, text scaling and RTL.

For navigation, follow existing router ownership and lifecycle. For asynchronous data, model loading/empty/error/offline/cancellation states and avoid rendering stale results after navigation. Animation belongs on the appropriate runtime/thread and must respect reduced motion; do not add a new gesture system merely to animate a small state change.

## Native modules and brownfield

Determine whether the task needs a local native module, a reusable module/view, an integrated RN host or an isolated produced artifact. Inspect actual Expo Modules API version before selecting DSL versus experimental macros. Do not introduce experimental migration patterns as a default.

Preserve the native app’s SwiftUI App/UIKit window, navigation and lifecycle. Never run `prebuild --clean` in a manually maintained native host. An isolated Expo producer may generate native projects separately; keep those outputs out of the consuming host. Decide integrated versus isolated from ownership, build/toolchain and release cadence, not a false assumption that only one supports iteration.

Validate input passing, returned results, dismissal, reopening with fresh state, event/listener cleanup, native navigation and Release behavior with Metro stopped. Rendering in Expo Go or a standalone producer example does not validate the feature in the real native app.

## Maintenance

Read release notes for the intended SDK and inspect native changes before upgrading. Keep upgrade work separate from an unrelated feature. Do not delete config/lockfiles, remove dependencies wholesale, run destructive prebuild or clear all caches as generic housekeeping. Check required peer dependencies and actual imports before removal. Test the app’s affected native capabilities after a real SDK/native change.
