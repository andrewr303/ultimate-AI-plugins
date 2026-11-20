---
type: llm
focus: files
weight: 1
---

The iOS 26 glass APIs are only reached behind an `if #available(iOS 26..., *)` branch or inside a declaration marked `@available(iOS 26..., *)` that is itself only called behind such a check, so the package (which targets iOS 17) still compiles. The older-system path still shows the palette, using a standard material such as `.regularMaterial`, `.ultraThinMaterial` or `.bar`, or a plain opaque background.
