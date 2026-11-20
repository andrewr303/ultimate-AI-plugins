# The preservation contract

Read this at step 1 of a redesign (and of any new design that lives inside an existing product). It explains
how to capture the original faithfully and how to write the contract every option must pass, from the smallest
refinement to the most radical reinvention.

The user's rule: a redesign "can be radical, but it should maintain important elements and functionality".
The contract makes that rule checkable. Radical options change **how** something is done or shown; they do not
silently remove **what** can be done.

## Contents

1. Capture the original from the best source available
2. The inventory
3. Writing the contract
4. Theme contract for new designs inside a product
5. Checking each option against the contract
6. When the user lifts or adds items
7. Contract format

## 1. Capture the original from the best source available

Build from the real source, never from memory of what an app "usually" looks like. Prefer the highest row you
can reach, and use lower rows only to fill gaps.

| Source | How to read it | What you get exactly |
|---|---|---|
| Codebase | Read the component, its children, styles, tokens, data types, handlers, routes, tests and copy files. Run the app if it runs, and look. | Exact tokens, spacing, radii, type, states, behaviours, copy, data shape |
| Claude Design canvas | Read `project/canvas.json`, then the artboard files; note design-system installs and Tweak props | Exact markup, tokens, props, states |
| Figma (when an MCP is connected) | Fetch the frame's design context, variables and a screenshot | Exact tokens and structure |
| Live URL | Capture screenshots at real widths; extract tokens with a brand extractor when connected (Dembrandt) | Close tokens, real layout and copy |
| Screenshots only | Study every image; ask for missing states if they matter | Approximate values: say they are estimates |

Copy exact numeric values (paddings, radii, font sizes, line heights, colours) from source. Do not round them
to a 4/8 grid or a framework default; the refinement options depend on starting from the true values.

Reading code well:

- **Read the real render branch.** Components often branch on breakpoint, feature flag, role or data state. The
  branch your user actually sees is the one to inventory. Reading the wrong branch is the most common cause of
  an unfaithful baseline.
- **Scale the reading to the codebase.** In a small project, read the whole surface. In a large one, read the
  subject's route, its components and their children, the token files and two or three representative shared
  components (button, input, card), then stop. Ask for focus only when the subject is genuinely unclear.
- **Say the system out loud.** Before designing, write a five-line summary of the system in use: colour roles,
  type families and scale, spacing rhythm, radii and elevation, and component vocabulary. It goes in the ledger's
  `theme.summary`, and keeps every option speaking the same language.
- **Screenshots are estimates.** Sample colours from pixels rather than guessing by eye. Label every value taken
  from an image as estimated, and never infer motion, hover or responsive behaviour from a static image.

## 2. The inventory

Walk the surface region by region and write down everything that a user could notice is gone:

- **Purpose and audience:** the job the surface does, who uses it, how often (daily tools tolerate less churn).
- **Regions:** header, navigation, toolbars, main content, panels, footers, overlays; their order and roles.
- **Actions:** every button, link, menu item, shortcut, drag, bulk action and form submission, with what it does.
- **Data:** every field shown, its format and units, sort and filter options, counts and totals, data volume.
- **States:** empty, loading, partial, error, success, disabled, selected, hover, focus, overflow, long text,
  permission-limited, first-run.
- **Rules:** validation, limits, ordering, business constraints ("deliverables stay inside their window").
- **Content and voice:** headings, labels, microcopy, tone, terminology the users know.
- **Brand and theme:** logo use, colours and their roles, type families and scale, radii, elevation, iconography,
  motion, imagery, density.
- **Accessibility facts:** keyboard paths, focus order, labels, contrast already achieved, and the failures
  today has (every option fixes them, §5).
- **Oddities:** behaviour that looks unintended but users can reach (an action offered where it makes no sense).
  Keep it and ask about it (§5).
- **Mental-model anchors:** things users rely on finding in a known place (primary action position, navigation,
  totals), which raise the cost of moving them.

Mark each item with how important it looks: **core** (the job fails without it), **expected** (users would
complain), **incidental** (could change freely).

Four classes are wrong to change unless the user explicitly asks, whatever the band:

- **Brand equity:** the logo (the real mark, never initials, emoji or an invented glyph in its place), the
  product name, and the committed palette and type families.
- **Information architecture and addressability:** routes, navigation destinations, heading semantics and
  anything search or bookmarks depend on.
- **Content and voice:** restructure freely, but keep terminology users know, and reword the voice only with
  permission.
- **Conversion and critical paths:** primary calls to action, forms, checkout and sign-up steps. They may be
  relocated or restyled, but never silently dropped.

## 3. Writing the contract

Turn the inventory into four lists. Keep them short and concrete; each line is something you can test.

- **Must keep:** every core function and data item, plus brand elements that make it recognisably the same
  product. Phrase as capabilities, not layouts: "Filter by status (All, Booked, In transit, Delayed, Delivered) with counts",
  not "status tabs above the table".
- **May change:** layout, component patterns, visual hierarchy, density, navigation placement, interaction
  model, copy wording (not terminology), illustration, motion. Name anything the user invited change on.
- **Lifted:** items the user said may go ("drop the stats row"). Only the user can lift items.
- **Constraints:** standing rules for every option: platform, frame size, accessibility level, "no sidebars",
  "must work on phones", "keep our teal". By default options add no new capabilities beyond what the original
  does. A small affordance a new interaction model needs (undo, skip, a "move later" in a board) is allowed
  when it is listed under the option's `changes` and nothing depends on it.

A good contract has 8–20 must-keep lines. Fewer usually means the inventory was shallow; many more usually
means layouts were written as requirements.

What the contract is not: a list of today's positions and component choices. If "table" or "tabs" appears in
must-keep, rewrite it as the capability, unless the user said the pattern itself must stay.

## 4. Theme contract for new designs inside a product

When the subject is new but lives in an existing product (a new settings page in an app that exists), write a
theme contract instead of a function contract:

- the product's tokens (colour roles, type scale, spacing, radii, elevation, motion);
- the component library and patterns to reuse (buttons, inputs, tables, navigation shell);
- voice and terminology;
- navigation placement and the page shell;
- constraints (platform, accessibility, density).

Options vary inside the theme by default. The Experimental band may stretch it (a new layout paradigm or a
bolder use of the brand) but never replaces it with a different product's look unless the user asks.

## 5. Checking each option against the contract

At plan time (step 3) and again after building (step 5), every option gets a contract check. In the plan
table and the ledger, record for each option (options at rung 4 and above also get a full mapping in
`contract`: one entry per must-keep item saying where it lives, e.g. `{"item": "3", "how": "sort menu in the
list header"}`; `{"item": "*", "how": "unchanged"}` covers every item not listed; `dv.py check` fails an
Evolve-or-higher redesign option with an unmapped item):

- **Keeps:** a compact summary, e.g. "all 9 actions, status filters with counts, totals, bulk send".
- **Changes:** what moved or became different, e.g. "table → grouped cards; filters → left rail".
- **How each core function is reached** when it moved, e.g. "bulk reminders: select mode in the toolbar".

A radical option that cannot keep a core function has three honest choices, in this order: find another way to
offer it; ask whether the user wants to lift it; or drop the option and plan a different one. Never ship it
quietly broken.

After building, test the contract inside the prototype: click each core action, check each data item shows,
reach each state the contract names. A function that exists only as a dead button fails the contract.

Accessibility is part of the contract too: no option may ship with more accessibility problems than the
original had, and none may keep a failure the original has. Inherited failures (a status pill below 4.5:1, an
unlabelled icon button) are fixed in every option, while the Now frame stays exactly as today; the reply says
so (prototype-standard.md §5). Keep an inherited failure only when the user says to.

**Odd behaviour the contract keeps.** Sometimes the original does something that looks wrong, such as offering
Send reminder on invoices that are already paid. Keep it in every option, because the contract cannot tell a bug
from a rule, and raise it in the reply as a question ("Send reminder still shows on paid invoices, as it does
today; should it?"). If the user answers, record a lifted item or a constraint (§6).

## 6. When the user lifts or adds items

- Feedback such as "we don't need the stats" lifts an item: move it to **Lifted** with the round it happened in.
- Feedback such as "never use a sidebar" or "keep the teal" adds a **Constraint** that applies to all later rounds.
- Picks imply nothing about the contract by themselves. If a pick dropped something by accident, it is still in
  the contract; fix it in the next round.
- Record every change in the ledger with the round number, so a later round can explain why something is gone.

## 7. Contract format

In the ledger (`design-variations.json`):

```json
"contract": {
  "must_keep": [
    "Find a shipment by reference or customer",
    "Filter by status: All, Booked, In transit, Delayed, Delivered, each with a count",
    "Sort by reference, customer, pickup date, ETA and weight",
    "Select several shipments and notify customers or reassign a carrier",
    "Per-shipment actions: view, notify customer, reassign carrier, duplicate, cancel",
    "Book a shipment with customer, route and pickup date, validated, as draft or confirmed",
    "Totals: in transit, delayed, delivered this week, drafts",
    "Freightline brand: indigo accent, IBM Plex Sans, light theme, plain operational tone"
  ],
  "may_change": ["layout and grouping", "filter and search placement", "table vs other list forms", "density", "visual hierarchy", "how creation opens"],
  "lifted": [],
  "constraints": ["Desktop web at 1440×900, usable down to 390 wide", "WCAG 2.2 AA contrast and keyboard access"]
}
```

In the gallery, the round summary names what all options keep in one sentence, and each option's meta line shows
its own Keeps and Changes.
