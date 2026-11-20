---
tags: [liquid-glass-studio, web, debug]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

I built a liquid glass header with an SVG displacement filter. In Chrome the edges bend the page behind them beautifully, but in Safari 26 on my Mac and iPhone the header just looks flat and frosted, with no bending at all. What am I doing wrong, and how do I get the same refraction in Safari? This is the CSS:

```css
.header {
  backdrop-filter: url(#lens) blur(6px) saturate(160%);
  -webkit-backdrop-filter: url(#lens) blur(6px) saturate(160%);
}
@supports (backdrop-filter: url(#lens)) {
  .header { background: rgb(255 255 255 / 0.08); }
}
```
