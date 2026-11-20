# Anti-Slop & Design Quality Guardrails

Version 3.4.0. Eight skills that stop and audit generic AI output in UI design, copy, responsive layout, accessibility and code comments. It is a filter, not a style guide: it holds each choice to a written purpose and does not prescribe an aesthetic.

Start with the `antislop` skill. It resolves a usage mode, then routes to the one or two skills that fit the task.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`antislop`](skills/antislop/SKILL.md). Try this prompt.

> Review this landing page for generic copy and repeated layout patterns. Point to specific sections and propose edits in the existing visual style.

## Install

```sh
/plugin marketplace add andrewr303/ultimate-AI-plugins
/plugin install anti-slop-and-design-quality@ultimate-ai-plugins
```

Skills load when a session starts, so open a new session after installing.

## What runs

Nothing runs automatically. The plugin declares no hooks, no MCP servers and no commands, and it makes no network calls.

Two optional scripts exist in the contrast skill and only run when you or an agent start them:

| Script | What it does | Run |
| :--- | :--- | :--- |
| `skills/antislop-human/contrast-check.py` | WCAG 2.x contrast ratio for two hex colors, pass or fail for normal and large text. Python 3 standard library only. `--selftest` recomputes the reference table in that skill's `SKILL.md`. | `python3 skills/antislop-human/contrast-check.py "#FFFFFF" "#777777"` |
| `scripts/contrast-mcp-launcher.mjs` | Opt-in. Starts the same checker as a local stdio MCP server (`contrast-mcp.py`, tool `check_contrast`). Needs Node and Python 3. Not registered by default. | `claude mcp add antislop-contrast -- node <plugin folder>/scripts/contrast-mcp-launcher.mjs` |

The MCP path is WCAG only. There is no APCA support.

## Skills

| Skill | Use it for |
| :--- | :--- |
| [`antislop`](skills/antislop/SKILL.md) | Core filter and router. Usage modes (during or after), the purpose test, the Delivery Gate, and the rules in [`references/RULES.md`](skills/antislop/references/RULES.md) (R-01 to R-40). |
| [`antislop-ui`](skills/antislop-ui/SKILL.md) | Building or editing an interface: color, layout, components, motion, page performance. |
| [`antislop-copywriting`](skills/antislop-copywriting/SKILL.md) | Headlines, CTAs, tone and AI-sounding prose. |
| [`antislop-layoutmobile`](skills/antislop-layoutmobile/SKILL.md) | Layouts that reflow from phone to desktop: grids, overflow, tap targets. |
| [`antislop-human`](skills/antislop-human/SKILL.md) | Contrast, keyboard, focus, states and affordances, with the contrast checker. |
| [`antislop-code`](skills/antislop-code/SKILL.md) | Removing generic AI comments from code while keeping the useful ones. Never edits code. |
| [`no-ai-design-slop`](skills/no-ai-design-slop/SKILL.md) | A passive gate while creating or revising UI, with a pattern library in [`ARTICLE.md`](skills/no-ai-design-slop/ARTICLE.md). Keeps the product's chosen direction. |
| [`audit-ai-design-slop`](skills/audit-ai-design-slop/SKILL.md) | An evidence-backed audit of a site, screenshot, mockup or design code, with a removal-first plan. |

Which to pick: build with `antislop-ui` plus `no-ai-design-slop`; review something that exists with `audit-ai-design-slop`; the core `antislop` skill applies in both.

## Related plugins

- The writing and content plugins in this repository produce prose. `antislop-copywriting` here only filters AI tells from copy that already exists or is being written, and it does not set voice or strategy.

## Provenance

License: the upstream code and skills are MIT (see `LICENSE`). Two skills, `no-ai-design-slop` and `audit-ai-design-slop`, carry no license in their files, so their terms are unconfirmed. See NOTICE.md before redistributing them.

Upstream sources, licenses and what this integration changed are in [NOTICE.md](NOTICE.md). Release notes are in [CHANGELOG.md](CHANGELOG.md).
