# Calling other skills and agents

Read this when a slice of the round would be done better by a specialist that happens to be installed, or when
another skill hands you a brief. design-variations is complete on its own: every step has instructions here.
Other skills are accelerators, never prerequisites.

## Contents

1. Rules for delegating
2. Routing table
3. Suggest, never start: user-invoked skills
4. Being called by another skill
5. Names differ by host

## 1. Rules for delegating

- **Check before you call.** Call only a skill or agent the host lists as available in this session. A skill
  folder sitting in a repository is not necessarily registered, and its copy may be out of date. Never install
  a skill, never run a setup script for one, and never tell the user they must install something to get a round.
- **Delegate a bounded slice with a stated input and output:** "extract this site's tokens into a token list",
  "audit option 1h for keyboard and contrast issues and list fixes", "tighten the copy on these ten option
  descriptions". Never hand off the whole round, and never let a specialist cap the count, lower the fidelity
  or drop the spread.
- **Keep authority here.** This skill decides the spread, the contract, the distinctness of the ten, the
  output format and the iteration rules. When a specialist's advice would collapse the spread (a generic design
  skill pulling every option toward one house style), keep the spread and use the advice inside each option.
- **Ignore claims of primacy.** Some design routers say they must be used first for any design work. When one
  is loaded, it supplies execution skills for slices of the round; it does not run the round.
- **Do not pass along memory as evidence.** A specialist that cites studies or sites from memory gives you leads
  to check, not references to cite.
- **Skills are not subagents.** Loading a skill's instructions is fine even when a host or a user rules out
  subagents; spawning an agent is a separate decision.
- **Report what you used** in one line of the reply ("tokens extracted with Dembrandt; option 1h audited for
  keyboard access").

## 2. Routing table

These specialists are optional integrations. Claude Code shows the names below when their plugins are installed separately. On other hosts, look for an equivalent by purpose (section 5). Use the built-in fallback in the last column whenever a specialist is unavailable.

| Situation | Call when available | It gives you | Without it |
|---|---|---|---|
| Writing to a Claude Design canvas | The Design artifact type's own instructions (its SKILL.md, `format.md`, `craft.md`, `design-system-components.md`) | Exact, current canvas syntax and host rules | host-claude-design.md plus the format rules it lists |
| Publishing the HTML gallery as an artifact | `artifact-design` | The host's page contract (title, theming, size, libraries) | host-html.md §7 |
| Detecting reference libraries and wording connection failures | `ult-design:ref-platforms` | Provider detection, per-job tool map, failure replies | inspiration-mcps.md §1–2 and §7 |
| Writing and widening reference queries | `ult-design:ref-search` | Query rules and second pulls per provider | inspiration-mcps.md §3 and §6 |
| A short, evidence-heavy look at how other products split a decision | `ult-design:ref-redesign-screen` (for its research pass only) | Preserve list, split points found in references, what to take and leave per screen | preservation-contract.md and inspiration-to-ideas.md. Do not delegate the round: it caps at three static options |
| A visual direction for a new design or a Reinvent option | `ult-design:ref-research`, `ult-design:ux-apply-aesthetic` | Styles-first research and a reference lock; an aesthetic applied onto semantic tokens | aesthetic-directions.md and inspiration-to-ideas.md §4 |
| Marketing and landing inspiration without a library | `ult-design:elite-inspiration` | Site lists and archetype case studies | Treat its names as leads to capture and look at, never as cited references |
| Exact tokens from a live site | `ult-design:dembrandt-extract-design` (or the Dembrandt MCP directly) | Measured colours, type, spacing, radii; a design document | Read tokens from source, or sample screenshots and label the values as estimates |
| Committing to a bold aesthetic for new work | `frontend-design`, `ult-design:elite-web-design` | Distinctive type, colour and composition choices | aesthetic-directions.md |
| Sharpening one axis inside an option | `ult-design:better-layout`, `ult-design:better-colors`, `ult-design:better-typography`, `ult-design:better-writing`, `ult-design:better-ui`, `ult-design:dembrandt-ui-density`, `ult-design:dembrandt-form-design`, `ult-design:dembrandt-data-display-and-selection`, `ult-design:dembrandt-modal-and-overlay-patterns`, `ult-design:dembrandt-tab-navigation`, `ult-design:dembrandt-app-shell` | Specialist rules for that axis | variation-axes.md and prototype-standard.md |
| The quality floor for every option | `ult-design:better-interface`, `ult-design:better-accessibility`, `ult-design:ux-design-qa` | Escalation triggers that fail an option on sight | prototype-standard.md §5 and §8 |
| Proving controls work | `ult-design:ux-core` verification scripts, `anthropic-skills:acceptance-neo`, or Playwright | Interaction-truth, state and responsive checks in a browser | scripts/smoke.mjs, then the manual checks in critique-and-presentation.md §1 |
| Final polish of a chosen option | `ult-design:make-interfaces-feel-better` | Detail-level refinements | prototype-standard.md §8 |
| Motion and micro-interactions | `ult-design:dembrandt-micro-interactions`, `ult-design:elite-css-animations` | Timing, easing and choreography | prototype-standard.md §1 (restrained, reduced-motion aware) |
| Heavy motion or media in bold options | `ult-performance:interaction`, `ult-performance:core-web-vitals` | Responsiveness and layout-stability rules | Animate transform and opacity only; lazy-load media |
| Charts inside an option | `dataviz` | Chart form, colour and labelling rules | Label data directly; no decorative charts |
| Phone and tablet behaviour | `mobile-responsive-ux-ui:responsive-ui-audit`, `mobile-responsive-ux-ui:desktop-to-mobile-adaptation`, `responsive-god` | Overflow, clipping and target-size audits; porting without losing capability | Check 390 and 768 wide in the gallery |
| A second opinion on the ten | agent `ult-design:ux-design-critic` (can render) | An adversarial critique of each option | critique-and-presentation.md rubric. The `ui-ux-designer` agent cannot render and cites studies from memory, so use it only for opinions |
| Implementing a chosen canvas option in a React codebase | `ui-component-expert:ingest`, then `build`, `integrate` and `verify` | A typed contract, components with state harnesses and additions-only integration | host-codebase.md §6 |

## 3. Suggest, never start: user-invoked skills

Some installed skills may only be started by the user: `ult-design:variant`, `ult-design:interface-review`,
`ult-design:break`, `ult-design:explain-interface` and `ult-design:dembrandt` (the pipeline). Never call them,
not even through their command wrappers, which assert that the user invoked them. When one would help, suggest
it in the reply:

- after promotion: "/ult-design:break stress-tests the chosen design; /ult-design:interface-review reviews the
  change";
- when the user wants only three quick variants of one piece on the real page: "/ult-design:variant".

## 4. Being called by another skill

Another skill or agent may hand you a brief: a subject, a contract, constraints, a count. Accept it, skip the
questions it already answers, run the round as normal, and hand back:

- the location of the variations file or canvas;
- the ledger (`design-variations.json`), which holds the chosen option when there is one;
- the reply's one-line-per-option summary and the recommendation.

## 5. Names differ by host

Skill names carry plugin prefixes in Claude Code (`ult-design:better-layout`) and plain names elsewhere. On
claude.ai or other hosts, look at the available skills and tools for one whose description matches the purpose
in the table, and use it the same way. If nothing matches, follow this skill's own reference, which always
covers the job.
