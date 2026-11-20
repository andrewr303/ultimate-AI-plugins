# Pipeline integration

Inspect the resolved package before selecting APIs. The uploaded Nuke README labels `main` as Nuke 14 in development. Its Package.swift declares tools 6.0 and platform floors including iOS 16, while README's WIP table lists a newer compiler requirement. These describe different layers, and the main snapshot does not prove a released compatibility contract. Check the pinned release, its manifest/source and the project's compiler/deployment target together.

## Choose the smallest fitting component

Reuse the existing image solution if it meets the requirement. System AsyncImage may suffice for simple remote display; an established Nuke pipeline adds explicit caching, processing, prefetching and lifecycle controls. Do not replace Kingfisher, a custom authenticated loader or a proven cache merely because Nuke was uploaded as reference material.

The uploaded package exposes Nuke, NukeUI, NukeVideo and NukeExtensions. Add only the products the app needs. NukeUI supplies LazyImage and reexports Nuke in the inspected source. NukeExtensions is described as soft-deprecated in README; use installed release guidance when updating an old app rather than mixing API generations.

## SwiftUI surface

`Sources/NukeUI/LazyImage.swift` declares an @MainActor LazyImage with URL and ImageRequest initializers and a custom content closure. The closure receives a state object, not AsyncImagePhase. Read `state.image`, `state.error`, loading and progress as required. Default image presentation is natural size; resizing belongs in the image content, with layout dimensions set outside it.

This is a project fragment, source-reviewed against the uploaded initializer and not compiled here; `imageURL` is supplied by the surrounding app:

```swift
import NukeUI
import SwiftUI

LazyImage(url: imageURL) { state in
    if let image = state.image {
        image.resizable().scaledToFill()
    } else if state.error != nil {
        Image(systemName: "photo")
    } else {
        ProgressView()
    }
}
.frame(width: 160, height: 120)
.clipped()
```

For decorative images, hide redundant accessibility content; for meaningful content supply the actual label from the product model. A broken-image placeholder must not imply the network is still loading forever. Provide retry only through a real state transition or request mechanism supported by the pinned version.

## Pipeline ownership and caching

Use an intentionally scoped shared pipeline or inject one per account/content domain. `.pipeline(customPipeline)` selects an instance in the inspected API. Establish configuration during app/service setup, not per cell render. Avoid mutating global shared configuration while existing screens are loading.

Distinguish processed-image memory cache, HTTP URLCache and the optional Nuke DataCache disk layer. URLCache follows HTTP semantics; DataCache has different persistence behavior. Enabling both indiscriminately may duplicate disk data. Prefer a deliberate built-in configuration where it fits, then confirm the actual initialized cache and backend cache-control headers.

Authenticated images need an explicit cache identity and logout policy. User-specific content at identical paths must not leak through shared keys or reused state. Decide whether credentials change request identity and how expiring signed URLs affect cache hit rate without stripping authorization-relevant components. Do not record signed URLs or Authorization headers in logs.

## Processing and snapshot conflicts

Decode/process near the needed destination size, accounting for display scale and cropping. A small frame alone does not prove a full-resolution decode is avoided. Match processor identity to the rendered variant so avatar and full-screen variants do not collide.

In uploaded `LazyImage.swift`, `.processors(...)` overrides processors from the request; nil restores request values, and the last view override wins. `Documentation/Nuke.docc/Essentials/swiftui.md` contains stale prose saying view processors apply only if the request has none. Use the installed implementation as authority and do not repeat that prose as a universal rule. Similar-looking FetchImage/LazyImageView APIs may intentionally differ.

Source evidence: uploaded `Nuke-main.zip`, Package.swift, README, Sources/NukeUI/LazyImage.swift, Sources/Nuke/Pipeline/ImagePipeline+Configuration.swift, and Documentation/Nuke.docc/Performance/Caching/cache-layers.md. See [source map](../../../docs/source-map.md) and preserved MIT notice.
