---
type: llm
focus: files
weight: 1
---

Every `id` attribute on SVG `<filter>` elements in the final index.html (and any filter ids created by script) is unique. The new glass filter does not reuse the id `glass`, which the page already uses for the logo's emboss filter, and the logo still references its own filter. If no SVG filter was added for the nav, this passes as long as the existing logo filter is untouched.
