# Chat integration boundaries

Read the resolved package and the app's current adapter before borrowing APIs. The upload is a `main` archive without Git history. It is evidence of those files, not proof of the latest released SDK. `Chat-main/Package.swift` declares the `ExyteChat` product, an iOS 17 floor, Swift tools 6.1 and Swift language mode 5 with strict concurrency enabled. A toolchain version and language mode are different settings; never raise the deployment target solely to match this archive.

## Framework and backend responsibilities

The source `Sources/ExyteChat/Views/ChatView.swift` declares `ChatView(messages:chatType:replyMode:didSendMessage:...)`. Its `didSendMessage` value is a `(DraftMessage) -> Void` callback. The app owns storage, authorization, uploads, acknowledgment, failure recovery and remote event delivery. Build a thin mapping layer from the domain message into `ExyteChat.Message` rather than letting UI-specific types become the backend schema by accident.

The upload's `Message.swift` declares a stable String `id`, user, creation date, attributed text, attachments and optional delivery status. Status cases include sending, sent, delivered, readBy and error. Define the meaning of each state against your backend. A successful HTTP upload is not a read receipt. Use a separate durable client operation identifier when the backend needs it; reconcile its result with the server message identifier without briefly displaying two copies.

## API inspection rules

- `Sources/ExyteChat/Views/ChatBuilderParameters.swift` provides `MessageBuilderParameters.message`, `messageActionClosure`, `showAttachmentClosure` and `defaultMessageView()`. Selective custom cards can keep the default row for ordinary messages.
- `InputViewBuilderParameters.text` is a Binding of String in the upload. Some README prose calls it `textBinding`; read the actual installed declaration.
- The model has `staticLocation`, not the `location` field named in one README passage. Inspect both Message and DraftMessage before mapping location data.
- `Sources/ExyteChat/Views/PublicAPI.swift` contains the offset-based `enableLoadMore` plus async older/newer history APIs in this snapshot. An older installed release may expose a different interface.

The following is a project fragment, source-reviewed against the uploaded initializer and not compiled here. `messages` and `send` are app-owned values, and the fragment is not a standalone app:

```swift
import ExyteChat
import SwiftUI

ChatView(messages: messages) { draft in
    send(draft)
}
```

Create a structured task or store-owned operation in the application's send implementation when work is asynchronous. Track cancellation and lifetime. Avoid launching detached work from each render or assuming navigation cancellation should discard an already accepted user send.

## Media and integrations

Chat's Package.swift already depends on Kingfisher, Exyte MediaPicker, Giphy and AnchoredPopup. Adding Nuke to the app does not change Chat's internal image loading. Evaluate whether a custom message builder needs a second loader and whether it would duplicate memory/disk caches. Never silently replace transitive dependencies.

Enable only requested composer inputs. Inspect the app's chosen camera, microphone, photo library and location paths; add truthful localized purpose strings only for APIs actually used. Test denial and limited access. A picker integration does not authorize uploading every selected file indefinitely. Validate supported media types, size limits and backend permissions, and scope temporary files and security-scoped access correctly. Keep signed URLs and local paths out of analytics and logs.

Giphy needs a real configured key and applicable attribution. Do not insert example credentials into a production target. Live location needs explicit product behavior for its duration, stopping and sharing; the UI library does not distribute updates to other users. Background location is a separate capability decision with device verification, not a requirement for displaying a static map.

## Source provenance

This is original guidance based on the uploaded `Chat-main.zip`: `Package.swift`, `Sources/ExyteChat/Model/Message.swift`, `Sources/ExyteChat/Views/ChatView.swift`, `Views/ChatBuilderParameters.swift`, `Views/PublicAPI.swift`, README and tests. Library copyright/permission notices remain in the plugin's license records. See [source map](../../../docs/source-map.md). Consult the installed release before applying any snapshot-specific name.
