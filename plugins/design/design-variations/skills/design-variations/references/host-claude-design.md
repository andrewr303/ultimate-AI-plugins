# Host: Claude Design canvas

Read this when the round goes into a Claude Design canvas (the Design artifact type: live artboards on a
canvas). It covers where the variations go, how to structure the files so all ten are live, how rounds and
choices accumulate, and the format rules that fail silently.

**Precedence:** the Design type ships its own instructions (its SKILL.md and `reference/format.md`,
`craft.md`, `design-system-components.md`). They are the authority on syntax and on how to call the host; read
them when you create or revise a canvas. This file only adds how to lay out a variations exploration on top of
them. Where they differ, follow the type's current instructions and keep this file's structure.

## Contents

1. What a canvas is made of
2. Where the variations go
3. Two ways to make an option live
4. The options document
5. Canvas layout
6. Rounds, choices and promotion on a canvas
7. Format rules that fail silently
8. Checks without rendering
9. Design systems, assets and comments
10. Product facts (as of November 2026)

## 1. What a canvas is made of

- `project/canvas.json`: the index. `boards` maps each artboard file to its frame (`x`, `y`, `w`, `h`, optional
  `title`, `page`, `expand: "fill"` for pages, `is_interactive: true` for working prototypes); `order` lists
  the same files back to front; `notes` holds titles and stickies; `pages` optionally splits the canvas;
  `designSystems` records installed systems.
- `project/<Name>.dc.html`: one file per artboard, a Design Component: `<x-dc>` markup with `{{holes}}`,
  `<sc-if>`, `<sc-for>`, `<dc-import name="Other">` children, plus a `<script type="text/x-dc" data-dc-script
  data-props='…'>` block whose `class Component extends DCLogic` returns the template's values from
  `renderVals()`. `data-props` declares the Tweaks a viewer can change, such as an enum that switches variants.
- Every `.dc.html` outside `project/ds/` shows on the canvas, imported or not, so list each one in `boards`.

## 2. Where the variations go

The original stays untouched. Choose, and say which in your reply:

| Situation | Where |
|---|---|
| The original lives in a canvas you can write to (default) | New files in the same canvas, on a new page named `Variations · <subject>`. Original artboards and their files are never edited. Boards with no `page` belong to the first page, so when the canvas had no pages, add a page for the existing boards first (named after the product) and the variations page second; leave the original board entries otherwise unchanged. |
| The user asked for a separate canvas, or you cannot write to theirs | A new canvas titled `<subject> · Variations`, with copies of the components it needs (and the design system installed the same way) |
| Brand-new design with no canvas yet | A new canvas titled after the subject; the variations are its first page |

File names: segments start with a letter, digit or `_` and continue with letters, digits, `_`, `.` or `-`; no
spaces; stems unique. Suggested names: `Shipments-variations.dc.html` (options document), `Shipments-base.dc.html`
(base copy with the variant switch), `Shipments-1h.dc.html` (a standalone option).

## 3. Two ways to make an option live

**A · Variant switch on a base copy** (refine and evolve bands, and anything that shares most of the surface).
This is how the user's reference canvas works.

1. Copy the original artboard into `<Subject>-base.dc.html` (a faithful copy: same markup, logic, tokens,
   data). The original file is not touched.
2. Add one enum Tweak per round, named for the round's topic in camelCase (`listLayout`, `dayHead`), with the
   options `today` plus the round's IDs (`["today","1a","1b",…]`), default `today`:
   `"listLayout":{"editor":"enum","options":["today","1a","1b","1c"],"default":"today","section":"Variations"}`.
3. In `renderVals()`, read the prop defensively and expose one flag per option:
   `const v = MODES.includes(this.props.listLayout) ? this.props.listLayout : 'today';` then
   `is1a: v === '1a'`, and so on; branch the markup with `<sc-if value="{{ is1a }}" hint-placeholder-val="{{ false }}">`.
   Keep shared parts shared; branch only what the option changes.
4. Every option stays fully interactive: the same state and handlers serve all branches.
   Viewers can flip the base artboard's Tweak themselves; inside the options document each mount passes its
   value explicitly, so there the Tweak is fixed per row. Say this the way the copy needs it ("List layout in
   Tweaks on the base artboard switches between today and 1a–1c").
5. When the round varies a part that lives in an imported child component, copy that child too under a new stem
   (`Slot-card-variations.dc.html`) and point the base copy's `<dc-import>` at the copy. The original child stays
   untouched.

**B · A standalone artboard per option** (rethink and reinvent bands, or when branching would bloat the base).

1. Write `<Subject>-<id>.dc.html` as its own complete component: same fixture data (copied into its logic),
   same contract, its own layout and interaction model.
2. Reuse the original's child components with `<dc-import>` where they still fit, and the installed design
   system's real components through the system's own mounting rules.

A round can mix both: often 1a–1f as switches on the base, 1g–1j as standalone artboards.

## 4. The options document

One artboard, `<Subject>-variations.dc.html`, is the page the user reads: a fluid PAGE (`"expand": "fill"`),
rounds newest first, following output-anatomy.md. For redesigns, the newest round starts with a Now row: a
`Now` chip, "Today", and the base copy mounted with its switch at `today`. assets/canvas/ holds a small worked
example of this document, its base copy and one standalone option.

```html
<section style="display:flex;flex-direction:column;gap:28px;padding:56px 64px 40px;">
  <div style="display:flex;flex-direction:column;gap:10px;max-width:1100px;">
    <span style="…eyebrow…">Turn 1 · Shipments board</span>
    <h1 style="…">Ten ways to spot delayed shipments</h1>
    <p style="…">All ten use the same 24 shipments and keep search, status filters with counts, sorting, bulk
      actions, row actions and the Book shipment drawer. Every frame is live. List layout in Tweaks on
      the Shipments-base artboard switches between today and 1a–1f.</p>
  </div>
  <div style="display:flex;flex-direction:column;gap:64px;">
    <div id="1a" style="display:flex;flex-direction:column;gap:14px;">
      <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;">
        <span style="…chip…">1a</span><span style="…name…">Quieter ledger</span>
        <span style="…desc…">Same table with calmer rules and stronger amounts. About 40px shorter.</span>
      </div>
      <div style="width:1440px;height:900px;border-radius:16px;overflow:hidden;…">
        <dc-import name="Shipments-base" list-layout="1a" style="width:100%;height:100%;" hint-size="1440px,900px"></dc-import>
      </div>
    </div>
    <!-- 1b … 1f the same way; 1g … 1j: <dc-import name="Shipments-1g" …></dc-import> -->
  </div>
</section>
```

- Write each row's copy the way the HTML build would (output-anatomy.md §3 and §4), because nothing assembles it
  for you: the description in one sentence, then the cost; a meta line with Keeps, Changes, Switch back and
  Solves where the option has them, and Inspired by for seed references or Also seen in for corroborating ones;
  in like, combine and refine rounds a small label with the option's role. Put the round's Degraded line under
  its summary.
- Attributes on `<dc-import>` become props (kebab-case to camelCase: `list-layout` → `listLayout`). Never pass a
  prop called `name`.
- Fixed-size frames for app screens (the original's size); the document itself is fluid.
- Copy is literal markup (viewers retype it in place); no Tweaks for copy.
- The document needs the `data-dc-script` block even with no logic:
  `class Component extends DCLogic { renderVals() { return {}; } }`.
- Use the product's fonts and colours for the document's chrome, through the installed design system or the
  same `<helmet>` font and token styles the original uses.
- Keep the number of live mounts manageable. When the document holds more than about thirty live frames, move
  the oldest rounds to their own archive document (`<Subject>-variations-archive.dc.html`) on the same page,
  keeping their rows, so the newest rounds stay fast.

## 5. Canvas layout

- Put the options document first on the variations page at `x: 0, y: 0`, wide enough for one frame plus
  padding (frame width + 128), height = its full content height at that width (over-tall beats clipped).
- Place standalone option artboards and the base copy to the right of the document, in rows: 80 px between
  frames in a row, 120 px between rows, one row per round, newest row on top. Give each a `title` such as
  `1g · Timeline` and `is_interactive: true`.
- Add a `title1` note above each row ("Turn 1 · Ten ways to spot delayed shipments") with `maxW` set to the row
  width and at least 223 px clearance above the row.
- Keep every existing key and entry in `canvas.json` you are not changing; add your boards, order entries,
  notes and the page.

## 6. Rounds, choices and promotion on a canvas

- **A new round:** add its section at the top of the options document, add the new enum options (or a new enum
  for a scoped round) to the base, add new standalone artboards, add a row and a title note. Earlier sections,
  artboards and enum values stay.
- **A choice or merge:** add a Chosen section (output-anatomy.md §6) and set the base's relevant enum default to
  the chosen ID, so every later round starts from it: "Chosen: 2c, now the default on Shipments-base." When
  the chosen option is a standalone artboard, the next round's base is a copy of that artboard.
- **Feedback from comments and edits:** viewers can comment on artboards, edit them by hand, and change Tweaks.
  Treat comments on option frames as feedback for the next round, quoting them in the round's `feedback`. Treat a
  hand edit to an option artboard as a strong signal (read the file again and describe what they changed), and
  never overwrite it.
- **Promotion:** only when the user asks to apply the choice. Describe the change first (which file, what
  changes), then edit the original artboard, keeping its file name, props and the rest of the canvas intact.

## 7. Format rules that fail silently

Read the type's `format.md` before the first artboard. The ones that most often break a variations canvas:

- Keep the head line `<script src="./support.js"></script>` exactly.
- Holes are dotted lookups only: `{{ item.name }}`, `{{ is1a }}`. No expressions (`{{ a + b }}`, `{{ !x }}`);
  compute in `renderVals()`.
- Events bind whole values: `onClick="{{ pick }}"` with `pick` returned from `renderVals()`; per-item handlers
  are attached to each item in `renderVals()`.
- Always give `<sc-if>` and `<sc-for>` their `hint-*` attributes. Never self-close `<dc-import>`; never use
  capitalised tags.
- All UI is markup; never build it in script (`innerHTML`, `appendChild`). No `<iframe>`, `<object>`, `<embed>`.
  No global keydown handlers.
- `data-props` is single-quoted JSON; every prop has an `editor` (`null` for objects and callbacks); include
  `$preview` with the frame's width and height.
- Real `<button>`, `<a href>`, `<input>` with `<label>`; `aria-label` on icon-only buttons; text contrast 4.5:1.
- Icons from the mounted design system by name, else inline stroke SVG; never emoji.
- Follow the type's write order (it may require writing and sending one file at a time, index first).

Behaviour confirmed by running `.dc.html` files in the canvas runtime (November 2026):

- `onKeyDown`, `onInput`, `onChange` and the drag events (`onDragStart`, `onDragOver`, `onDrop`) work as
  whole-value handlers.
- Holes inside an attribute (`style="color: {{ tone }};"`) and next to text (`Pressed {{ count }} times`) work.
- Each `<dc-import>` of the same component keeps its own state.
- Element `id`s are duplicated when a component is imported more than once, so never rely on `id` lookups or
  `for`/`aria-labelledby` pairs that need unique ids inside imported components; wrap inputs in their `<label>`.
- `<helmet>` styles of an imported file apply to the whole importing page. Keep layout and colour inline as the
  format asks. Use helmet classes only for what inline styles cannot express (`:hover`, `:focus-visible`,
  `kbd`, reduced-motion rules), and prefix them with the file's stem (`.shp1h-row:focus-visible`) so they cannot
  leak onto other options.

## 8. Checks without rendering

The Design type may forbid rendering, screenshotting or re-reading the canvas to verify unless the user asks.
Respect that. Instead, before sending files, run the static linter on your local copies:

```bash
python3 <skill>/scripts/dv.py lint-dc <root>/project
```

It checks the head line, the single `<x-dc>`, the logic class, holes, forbidden tags and calls, `data-props`
JSON and editors, `$preview`, unquoted attributes, unclosed tags, `dc-import` targets and the `canvas.json`
boards. Fix every error. Then run the logic check where Node is available:

```bash
node <skill>/scripts/dc-check.mjs <root>/project
```

It runs each artboard's logic outside the canvas (for every value of every enum Tweak), checks that every hole
resolves and fires every handler, so a thrown error or a missing value shows up before the user sees it. Read
its hole warnings: missing optional fields can be fine, missing values in a branch you meant to show are not.
Then reason through each option's handlers against the contract, and do the states pass by reading: for every
`previewState` value, and with a filter applied, check that each total, count and message the branch shows is
true (critique-and-presentation.md §1). Offer the user a check pass ("I can open each frame and click through it
if you want"), and report these checks as reading, not rendering.

## 9. Design systems, assets and comments

- If the canvas has a design system installed, mount its real components in every option rather than look-alikes,
  following the type's `design-system-components.md`. A radical option still uses the system's components; it
  changes composition, not the kit.
- Images and fonts are uploaded as assets and referenced by the URLs the host returns, never as data URIs.
- Keep the ledger as `project/design-variations.json` (a support file) so later rounds can read it. If the host
  will not store it, put it at the end of your reply.

## 10. Product facts (as of November 2026)

- Claude Design runs inside Claude: a new design, design system or slide deck is created as an artifact (the
  Design type is a canvas of live artboards). Designs start private.
- Claude Design has no dedicated variations feature; people ask in chat for alternatives. This skill provides a
  structured ten-option round on top of the canvas.
- Viewers can comment on artboards and adjust Tweaks (the `data-props` controls) without a model round-trip, so
  enum Tweaks are the cheapest way to flip low-rung options in place.
- Exports include standalone HTML, PDF, PPTX and a handoff bundle for Claude Code. Canvases made from a codebase
  can be handed back to Claude Code to implement a chosen option (host-codebase.md §6).

Older guides describe the standalone product's prompt-level "edit mode" markers; follow the Design artifact
type's current instructions instead.
