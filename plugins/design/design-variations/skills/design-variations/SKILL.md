---
name: design-variations
description: Generates ten distinct, fully interactive design variations, ranging from small refinements to radical redesigns, so the user can pick a direction, then iterate in rounds (more like my picks, combine picks, ten new directions, bolder, closer to today, refine one). Use for brand-new screens, components, pages and flows, and for redesigning or overhauling existing UI from a codebase, a Claude Design canvas, Figma, a screenshot or a live URL while keeping the original's functions and key elements. Pulls inspiration from connected design-reference MCP servers (Gummble, Mobbin, Refero, UXKin, Figma, Dembrandt and similar) and writes every round into a new variations file or canvas, never into the original. Use whenever someone asks for design options, alternatives, variations, directions, explorations, concepts or mockups to choose from, says "show me a few ways" or "what could this look like", wants a redesign, or is iterating on design options, even if they never say ten.
license: MIT
compatibility: Works in Claude Design canvases (the Design artifact type), Claude Code and claude.ai. Python 3.8+ for scripts/dv.py is optional; Node with Playwright is optional for scripts/smoke.mjs.
metadata:
  version: 1.0.0
  default-count: "10"
---

# Design variations

Help the user decide on a design direction by showing them ten real, working alternatives at once, then
narrow or widen in rounds until they choose. The ten are a spread, not ten tints: ordered from the smallest
sensible change to a radical rethink, each a different answer to the same brief, each a live prototype they
can click, type into and judge, all in a new variations file so nothing they already have is touched.

A round is done when the user has a link or file with ten working prototypes, a one-line case and cost for
each, and an easy way to say what they want next. The skill is complete on its own; when better-suited skills
or tools are present it uses them (references/skill-routing.md).

## What every round delivers

1. **Ten options by default.** Honour any count the user names ("give me 4"). IDs are the round number plus a
   letter (`1a` … `1j`), permanent across rounds; never renumber or rename an option once shown.
2. **A deliberate spread** ordered a→j by change level on a 1–10 ladder grouped into four bands
   (references/spectrum-ladder.md). Redesigns: Refine 1–3, Evolve 4–6, Rethink 7–8, Reinvent 9–10. New designs:
   Proven, Fresh, Novel, Experimental. Every band is present unless feedback shifted the spread on purpose. An
   option's rung is earned by what it changes, never by the slot it fills.
3. **Genuinely different answers.** Each option owns one primary axis position (layout paradigm, density,
   interaction model …). By default no primary axis leads twice in a round, and no two options ever share both
   rung and axis (references/variation-axes.md §3). The bold end is visibly bold: Rethink and Reinvent options
   must not look like today, or like the picks a later round builds on, at a glance.
4. **Fully interactive, hi-fi prototypes** of the whole surface with realistic content, every control
   responding and the key states reachable. Not wireframes (references/prototype-standard.md).
5. **The original's essentials kept.** For redesigns every option passes the preservation contract: all
   functions, data and key brand elements survive, even in the radical options, unless the user lifted them
   (references/preservation-contract.md).
6. **The product's look.** Options fit the original's or platform's theme unless the user said otherwise; the
   radical end may push the visual language but stays recognisably the same product.
7. **Inspiration from connected design-reference MCPs**, cited per option (references/inspiration-mcps.md).
8. **A new file or canvas.** Never the original (references/output-anatomy.md and the host file).
9. **A round ledger** (`design-variations.json`) recording the contract, options, lineage, references and
   feedback, so later rounds stay consistent and never repeat themselves.
10. **Today, for comparison.** Redesigns show the current design unchanged as a "Now" frame at the top of the
    newest round. It is not one of the ten.

## The workflow

| Step | Do | Read |
|---|---|---|
| 0 | Pick the mode: Explore, Iterate or Promote; settle subject, host and count | intake-and-modes.md |
| 1 | Ground in the original (or the brief): inventory, theme, preservation contract | preservation-contract.md |
| 2 | Gather inspiration from connected MCPs, user references or captures | inspiration-mcps.md, inspiration-to-ideas.md |
| 3 | Plan the ten: rung, band, primary axis, big idea, references, keeps/changes | spectrum-ladder.md, variation-axes.md, pattern-alternatives.md, aesthetic-directions.md |
| 4 | Build the prototypes into a new variations file | prototype-standard.md, then host-claude-design.md, host-html.md or host-codebase.md; skill-routing.md for specialists |
| 5 | Verify: every option works, passes the contract, and the ten look different | critique-and-presentation.md; skill-routing.md for browser and critic helpers |
| 6 | Present: link, ten one-line cases with costs, how to give feedback | critique-and-presentation.md |
| 7 | Record the round in the ledger | output-anatomy.md (ledger section) |
| Next | Iterate on feedback, or promote the choice | iteration.md |

Read each reference when its step starts, not all up front. References are one level deep; examples.md has
three compact worked rounds.

### Step 0 · Mode, subject, host

- **Explore** is the first round on a subject. **Iterate** is any later round driven by feedback.
  **Promote** applies a chosen option to the real design, only on the user's explicit request. A ledger whose
  newest round was never shown is not iteration: resume that round (intake-and-modes.md §1).
- Name the subject in one sentence: what it is, where it renders, what job it does. One subject per round;
  a later round may zoom into a sub-part ("the day header") while holding the rest constant.
- Decide **redesign** (an original exists: code, canvas, Figma, screenshot, URL) or **new** (nothing to keep
  but maybe a platform theme to fit).
- Pick the host (references/intake-and-modes.md): a Claude Design canvas when the Design artifact type is
  available or the work lives in a canvas; a self-contained HTML gallery otherwise; a codebase harness only
  when real components matter more than a standalone file.
- Take the inspiration inventory now (step 2 explains it), because design-context servers such as Figma or
  Dembrandt help capture the original in step 1.
- Ask at most one round of questions (at most four), and only when two or more open decisions would change
  what you build. Otherwise decide, state the assumptions in one line, and build.

### Step 1 · Ground

Redesign: read the real source before designing. Inventory every screen region, control, action, state,
data field, rule, piece of copy and token; then write the **preservation contract**: must keep, may change,
lifted by the user, and constraints. New design: write a five-line brief (job, audience, platform, content,
tone) and adopt the platform's theme when the new piece lives inside an existing product.

### Step 2 · Inspire

When any inspiration library is connected, use it: this is a required step, not decoration. Take inventory
first: search the available tools for provider names (gummble, mobbin, refero, uxkin, figma, dembrandt …) and
note which are connected, which need sign-in and which are absent; that one line goes in the reply. A sign-in
notice is not proof: when a provider's tools are listed, make one cheap call before believing it, and record
each copy in `inspiration.connections`. Read each provider's tool schemas before the first call. Run the query
recipe, open and actually look at the strongest results, and build a reference board of 8–20 entries, each with
a link, what it does well in abstract terms, and which option it seeds. Borrow patterns, never another product's
identity or copy. Design-context servers such as Figma or Dembrandt serve step 1 and need not yield references.
A library that becomes usable after planning re-seeds named options or is cited as corroborating, never as their
source (inspiration-to-ideas.md §2). When nothing is connected, say so in one line with how to connect Gummble
(or the provider the user names), worded for a local or a remote session (inspiration-mcps.md §7), and use the
fallback ladder in inspiration-to-ideas.md: user references, public page captures, then your own knowledge
labelled as such. A missing connection never blocks the round.

### Step 3 · Plan the ten

Write the plan before any code. Naming the corners of the idea space up front is what stops ten options
collapsing into one safe answer; models left alone drift toward similar ideas. Start with the round's one design
question ("How should dispatchers see what is running late?"), what every option holds constant, and the
criteria the user cares about (the cost lines are judged against them). Every complaint in the brief becomes a
criterion ("feels dated", "slow to find what needs chasing"), and at least one option leads on each. When the
brief complains about the look, keep a rung-2 restyle slot even in a bolder round (spectrum-ladder.md §5).
Sketch about twenty one-line concepts first, then pick the ten that are most spread out across rungs and axes.
Write one table row per option: ID, name (2–4 words that say the idea), rung, band, plane, primary axis and its
position, the big idea in one sentence, reference seeds, keeps, changes and cost.

Then run the checks in spectrum-ladder.md and variation-axes.md:

- options ordered by rung, with every band present;
- no primary axis leading twice unless the options differ in paradigm and the round's `degraded` line says why;
  never two options on the same rung and axis;
- at least six different primary axes and at least three structurally different layouts;
- the pairwise distinctness tests (silhouette, swap, one-sentence difference, shared traits);
- every complaint in the brief led by at least one option;
- rungs 9–10 with a function mapping and a switch-back; fact-led subjects such as pricing that hide the facts
  behind interaction get a one-click way back to them on the first screen (spectrum-ladder.md §6);
- every option passing the contract on paper.

In later rounds, also run `dv.py novelty` (or the manual check in iteration.md) so nothing repeats an earlier
option, or revives one the user passed on, unless it descends from a pick. Check every new first screen against
the `signature` of each passed option, so a dead direction cannot return under a new label. In like, combine
and refine rounds, give each option a `role` and lay the roles onto the round's rung row (iteration.md §3).

When the brief is ambiguous and the user is present, you may show the ten one-line rows first and let them swap
some before you build. Otherwise build, and let the round header carry the plan.

### Step 4 · Build

- One shared kit: product tokens, fonts, realistic data, helpers. Then one prototype per option. Low rungs
  can be cheap deltas on a faithful base; high rungs are full rebuilds of the surface on the same data.
- Every option is the whole surface in context (real chrome, neighbours, data volume), at the frame size the
  product is really used at, with every visible control working (prototype-standard.md).
- Write into a new location only: a new canvas or new canvas files, a new HTML file, or a new scratch folder.
  The original file, component or canvas artboard is never edited during exploration.
- Build in batches so a round never dies half-way: the kit and the Now frame first, then a–e, check them, then
  f–j. Shared components (header, table row, drawer, form fields) live in the kit so options compose them
  instead of re-implementing them. If the turn cannot hold all ten, deliver the finished options with a
  Degraded line naming what is missing, and finish the rest next turn; never ship a broken option.
- In later rounds, new shared helpers go in `kit/round-<n>.html`, which the build adds only to that round's
  frames. `kit/kit.html` and every earlier round's files stay byte-identical, with two disclosed exceptions in
  host-html.md §2: a shared helper that is wrong in every round, and a font-fidelity fix in `variants/today.html`.
- When subagents are available and the host allows parallel writes, split the ten across them after the shared
  kit exists (host-codebase.md §5 defines what each worker gets). Integrate and check centrally; say when
  independent generation was not possible.

### Step 5 · Verify

Before showing anything: load the output, click through every option, confirm the console is clean, every
contract function works, nothing clips at the narrowest supported width, and focus is visible. Then look at
the ten side by side and ask whether a stranger would call them ten different ideas. Fix or replace any that
fail. Then place every built option again by the plane test (spectrum-ladder.md §2) and, for redesigns, record
its `plane`: an
option that landed below its slot is rebuilt or replaced, or the row is left uneven and the `degraded` line says
so; never relabel it to fit. Switch each option into every declared state and read every sentence for truth.
Run `dv.py check` for HTML galleries; for canvas files run `dv.py lint-dc` and `dc-check.mjs`, plus
`dv.py check` on the ledger. On a Claude Design canvas, follow the Design type's own rule about rendering checks
(it may forbid rendering unless the user asks), and rely on these checks there.

### Step 6 · Present

Reply with the link or path, then the ten in order, one line each: `1c · Split ledger: … Costs …`. Give each
an honest case and its main cost, and say which options answer which complaint in the brief. Then, in the
reply only, add one recommendation and a runner-up, each tied to the user's stated goal and each with its cost.
The file stays neutral. Close with how to steer the next round: in a gallery, shortlist, "not this" marks and
notes, then Give feedback; on a canvas, comments on frames; or a reply like "like 1c and 1g, combine 1c's header
with 1g's list, bolder". Keep the reply short; the file carries the detail. When project or host instructions
set a reply format, fit these parts inside it rather than adding a second one.

### Step 7 · Record

Add the round to `design-variations.json` (schema in assets/ledger.schema.json): kind, topic, title, summary,
feedback that drove it, basis options, the inspiration inventory with its `connections`, references (each with
`use`: `seed` or `corroborating`) and every option with rung, band, `plane` (redesigns), axis, paradigm, a
one-sentence description (the cost goes only in `cost`), keeps, changes, its contract mapping, parents and
tags. Rungs 7–10 add `solves` and `traits`, rungs 9–10 add `switch_back`, like, combine and refine rounds add
each option's `role`, and every option the user passes on gets a one-line `signature`. Shown rounds may have
ledger metadata backfilled; their variant files never change.
In a canvas, keep the ledger as a `design-variations.json` file beside the artboards (or in your reply if the
host cannot store it) so later rounds can read it.

## Iterating (references/iteration.md)

Restate your reading of the feedback in one line before building ("Reading this as: evolve 2c and 2g, keep
2c's header, bolder overall"). Feedback maps onto one or more of these:

| They say | Next round |
|---|---|
| "More", "none of these", "something different" | Ten new directions unlike every earlier option; new axes, new references; diagnose what missed |
| "I like 2c and 2g" | Evolve the picks: refinements of each, crossovers, pushes along their axis, and one or two wildcards, each with its `role` |
| "Combine 2c's header with 2g's list" | A Chosen round holding the merge, then ten variations of the merge (skip them only when the user says the merge is final) |
| "Make 3c's header bigger" (one concrete change) | An Edit round: one option, a new ID, 3c as parent; not a decision |
| "Refine 2c" | Ten variations of 2c alone, a local spread from polish to a bold take on 2c |
| "Bolder" / "closer to what we have" | Shift the rung distribution up or down; keep what they liked. With picks, lay the like roles onto the shifted row (iteration.md §3) |
| Steer words ("calmer", "denser", "airier", "more premium") | Translate each into concrete moves on named axes within the brand (iteration.md, steer glossary) |
| "Not this" on some options | Record them as passed, each with a one-line `signature`; never re-offer those directions or their signature device unless asked |
| Specific notes ("no sidebars", "denser") | Add to the contract's constraints and apply to every new option |
| "Now the empty state" / a sub-part | A scoped round: hold the chosen design constant, vary only that part |
| "Let's go with 3e" | Promote flow: Chosen round, then apply to the original only when asked |

New rounds go on top; earlier rounds stay below, unchanged, so the file reads as a history of decisions.
iteration.md holds the recipes behind each row.

## Hard rules

- Never modify the original design, file, artboard or component during exploration; promotion is a separate,
  explicitly requested step that you describe before doing.
- Never drop a contract function to make an option cleaner. A radical option changes how it works, not whether.
- Never pad with lorem ipsum, "John Doe", fake stats or invented features; missing facts become visible
  placeholders such as [YOUR PRICE].
- Never pass off a reference's design, logo, copy or proprietary pattern as an option; borrow the idea.
- Never send a user's private screenshots or code to a third-party service without their yes to that upload.
- Never claim an MCP search, a render check or a test you did not run, and never present a reference found
  after the options were planned as the source of their ideas, unless you rebuilt the option from it.
- When an inspiration library (Gummble, Mobbin, Refero …) is connected, search it every round and seed options
  from what you saw; record the inventory and the references in the ledger.
- Place every option on the rung its changes earn. Never relabel an option to fill a slot.
- Keep the variations file neutral, with no favourite marked. The recommendation and its cost live in the reply.
- Merges take each part whole from a named donor option; never average two directions into a middle neither
  option was.
- Never re-offer a direction the user passed on, unless they ask for it back.

## Calling other skills

This skill is self-sufficient. When a skill or agent below is available, prefer it for its slice and keep
the round's structure here (detail and exact names: references/skill-routing.md):

- the host's own Design-canvas instructions for `.dc.html` syntax and canvas rules (always, when present);
- a brand or token extractor (for example Dembrandt) to capture a live site's exact tokens;
- reference-research skills to drive a connected inspiration library;
- layout, color, typography, writing and accessibility specialists to sharpen one axis;
- a browser or acceptance-testing skill to verify prototypes; a design-critic agent for a second opinion.

## Scripts and assets

`<skill>` below means this skill's folder (`${CLAUDE_SKILL_DIR}` in Claude Code). Run the scripts; do not read them
into context unless one fails.

- `scripts/dv.py init|next|build|check|novelty|lint-dc`: workspace setup, the next round's IDs, gallery build,
  ledger and quality checks, novelty against history, and a static linter for Claude Design files.
  `build <dir> --standalone-dir <folder>` writes one page per option to a folder outside the workspace, for
  click-through tests.
- `scripts/smoke.mjs`: optional Playwright pass that loads the gallery, presses every option's buttons and fails
  dead ones, checks phone width, saves one screenshot per option (and per declared state with `--states`) and
  runs an automated squint test; `--round <n>` tests one round only.
- `scripts/dc-check.mjs`: runs Claude Design artboards' logic without the canvas runtime, for every Tweak value,
  and reports thrown errors and unresolved holes.
- `assets/gallery-template.html`: the gallery shell (rounds newest first, live frames, shortlist, notes,
  compare, focus and copy-feedback). `assets/ledger.schema.json` and `assets/ledger.example.json`: the ledger.
- `assets/canvas/`: an options-document template and a canvas index example for Claude Design.

## Reference map

| File | Use it for |
|---|---|
| intake-and-modes.md | Mode, subject, resuming an unshown round, redesign vs new, host choice, when and how to ask, count overrides |
| preservation-contract.md | Inventorying the original; must keep, may change, lifted; per-option contract check |
| spectrum-ladder.md | The 1–10 ladder, placing options by plane, bands, default slot plan, distribution shifts, new-design ladder |
| variation-axes.md | The axes options vary on, their positions and costs; diversity rules |
| pattern-alternatives.md | Structurally different patterns for common components and screens |
| aesthetic-directions.md | Named visual directions for new work; fitting an existing theme |
| inspiration-mcps.md | Provider cards, detecting connections, query recipes, citing, failures, privacy |
| inspiration-to-ideas.md | Turning references into options; the reference board; fallbacks without MCPs |
| prototype-standard.md | What fully interactive means; build strategy; accessibility and quality floor |
| output-anatomy.md | The variations file's anatomy, copy formulas, IDs and the ledger |
| host-claude-design.md | Writing rounds into a Claude Design canvas |
| host-html.md | The self-contained HTML gallery and its workspace |
| host-codebase.md | Working inside a repository without touching the original |
| iteration.md | Feedback grammar, evolution recipes and roles, novelty, Chosen rounds, convergence, promotion |
| critique-and-presentation.md | Self-review rubric, verification, presenting fairly, the reply |
| skill-routing.md | Which other skills and agents to call, and what to do without them |
| anti-patterns.md | Failure modes and their fixes |
| examples.md | Three worked rounds |
