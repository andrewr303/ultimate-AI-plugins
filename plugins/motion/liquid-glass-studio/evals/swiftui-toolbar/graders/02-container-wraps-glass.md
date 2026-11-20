---
type: llm
focus: files
weight: 1
---

In the edited CanvasView.swift, the palette's glass buttons (views using `.glassEffect(...)`, or `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)`) sit inside a `GlassEffectContainer`, and the two groups (Pen, Highlighter, Eraser; Undo, Redo) are visibly separate: for example two containers, a gap larger than the container spacing, or `glassEffectUnion` with a different id per group.
