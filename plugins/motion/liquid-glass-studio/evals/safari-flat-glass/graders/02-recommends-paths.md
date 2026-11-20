---
type: llm
focus: last_message
weight: 1
---

The answer recommends a designed frosted fallback (blur, saturation, tint, rim or highlight) for Safari, and for the case where Safari must refract it points to a different rendering path that does not depend on `backdrop-filter: url()`: a WebGL (or WebGPU) capture of the backdrop, or an SVG filter applied to an explicit content layer the app owns (for example via a library such as simple-liquid-glass or glasshq-liquid-glass). It mentions at least one cost or limit of that path (for example performance, recapture on scroll, or content it cannot capture).
