---
type: llm
focus: files
weight: 1
---

Keyboard focus on the nav links and the nav button stays visible: the existing `:focus-visible` outline rules are not removed, weakened to `outline: none` or `outline: 0`, or replaced by a background tint only, and the glass element does not clip the outline (no `overflow: hidden` or `clip-path` on the focusable element itself). A `:focus:not(:focus-visible) { outline: none }` rule alongside a visible `:focus-visible` ring is acceptable.
