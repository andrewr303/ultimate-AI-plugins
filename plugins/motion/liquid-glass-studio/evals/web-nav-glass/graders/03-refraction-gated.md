---
type: llm
focus: files
weight: 1
---

If the result uses SVG refraction (`backdrop-filter: url(...)` or `filter: url(#...)` with `feDisplacementMap`), it is applied only on Chromium through an engine or capability check in script, and other engines get a frosted `backdrop-filter: blur(...)` surface (with the `-webkit-backdrop-filter` declaration as well); `@supports (backdrop-filter: url(...))` is not the only gate. If no SVG refraction is used at all, this check passes as long as a frosted tier exists.
