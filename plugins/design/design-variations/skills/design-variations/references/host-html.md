# Host: the self-contained HTML gallery

Read this when the round's output is an HTML file: in a codebase (after host-codebase.md), in claude.ai chat,
or anywhere without a Claude Design canvas. The result is one HTML file that opens offline in any modern
browser, holds every round, and runs each option as an isolated live prototype.

## Contents

1. Workspace layout
2. The shared kit
3. Variant files
4. Building and checking
5. What the gallery gives the user
6. Writing the gallery by hand (no scripts)
7. Publishing and sharing
8. Limits and fallbacks

## 1. Workspace layout

```
design-variations/<subject-slug>/
  design-variations.json   the ledger (output-anatomy.md §9)
  kit/kit.html             shared tokens, fonts, base styles, data and helpers for every prototype
  kit/round-<n>.html       optional: helpers and CSS added in round n, loaded by round n's frames only
  variants/today.html      the current design, unchanged (redesigns): the Now frame
  variants/1a.html … 1j.html  one prototype per option
  index.html               the built gallery: the file the user opens
  shots/                   optional screenshots from scripts/smoke.mjs
```

Create it with `python3 <skill>/scripts/dv.py init <dir> --title "Shipments board" --mode redesign --w 1440 --h 900 --theme light`
(theme = the product's).
`init` refuses to write into a non-empty folder that is not already a variations workspace, so it cannot
overwrite anything. Get the next IDs with `dv.py next <dir>`.

## 2. The shared kit

`kit/kit.html` is injected at the top of every prototype's `<head>`. Put here, once:

- **Tokens** copied exactly from the product (`:root { --… }`), or the committed direction's tokens for new work.
- **Fonts:** load exactly what the product loads. If the product loads a Google Font, use the same `<link>`; if
  it names a family without loading it (so users see a system fallback), do the same, so the Now frame matches the
  real page. Otherwise use the product's own font files only if they are small and licensed for this use.
- **Base styles:** resets, body type, focus ring, scrollbar, selection colour, and
  `[hidden] { display: none !important; }`, so a component's own `display` rule cannot keep a hidden region on
  screen. New workspaces' kit stub includes it; keep it.
- **Data:** realistic fixtures as `window.KIT.data` (names, amounts, dates, statuses, long and short values,
  enough rows to scroll: usually 15–60). Same data for every option, so differences come from design alone.
- **Helpers:** formatters (`KIT.fmt.money`, `KIT.fmt.date`), a tiny store or event helper, a toast, an icon
  set as inline SVG strings. Keep helpers small; prototypes must stay readable. A helper that sums or counts
  takes the rows on screen, so a filtered view shows filtered totals.

Every prototype gets its own fresh copy of the kit, so state never leaks between options.

**Extending the kit in a later round.** Once a round is shown, `kit/kit.html` and that round's variant files
stay byte-identical. New helpers and CSS for round n go in `kit/round-<n>.html`, which `dv.py build` injects
after `kit/kit.html` into round n's frames only. Prefix what it adds with the round (`.r2-dock`, `KIT.r2`) so
it cannot collide with the shared kit. When a fix truly has to change `kit/kit.html` (a shared helper that is
wrong in every round), make it, and say in the reply which earlier frames now render differently and how.

**Fixing font fidelity mid-exploration.** If a later round finds that the kit loads fonts differently from the
product, load the right fonts in that round's `kit/round-<n>.html`, and in `variants/today.html` too: the Now
frame shows only in the newest round, so the new round then compares like with like. Earlier rounds keep the
fonts they were shown with; say so in the reply.

## 3. Variant files

`variants/<id>.html` is a fragment: no `<!doctype>`, `<html>`, `<head>` or `<body>` (the gallery adds them).

```html
<style>
  /* only this option's CSS; kit tokens are available */
</style>
<div class="app">
  <!-- the whole surface: shell, navigation, content, overlays -->
</div>
<script>
  // this option's behaviour, reading KIT.data and using KIT helpers
</script>
```

Rules:

- The fragment renders the whole surface at the frame size and adapts down to the narrowest supported width.
- All behaviour is in this file's `<script>` (plain JS, or a framework from an allowed CDN when the product is
  built with it and the prototype genuinely needs it). Keep it working offline whenever possible.
- Do not reach outside the frame (`parent`, `top`, `document.write`). Links that would navigate away are
  blocked by the gallery; use buttons and in-page state for navigation inside the prototype.
- Never include `</template>` in a fragment or the kit.
- Downloads work (an Export button may save a real file). Keep all state in memory. Frames are sandboxed without same-origin access, so `localStorage`,
  `sessionStorage`, cookies and the clipboard API throw inside a prototype.
- Mark a control that is deliberately inert (a disabled-looking "Coming soon" is not allowed, but a decorative
  avatar button might be) with `data-dv-inert="reason"`; the smoke test fails any other button that changes
  nothing. A press that scrolls, moves focus or changes the page counts as a response, so scroll-to-section
  navigation needs no mark.
- Never give a component a `display` rule that overrides the `hidden` attribute, and start entrance motion
  from a visible state, never `opacity: 0` (prototype-standard.md §1).
- Low-rung options may start from a copy of a faithful base fragment and change only what the option changes.
  Build the base first as `variants/today.html` (declare `"baseline": {"name": "Today"}` in the ledger), then
  copy it per option.
- States that cannot be reached naturally are declared in the option's `states` and switched by the gallery.
  Listen for them with `window.addEventListener('dv:state', (e) => render(e.detail))`
  (prototype-standard.md §3).

## 4. Building and checking

```bash
python3 <skill>/scripts/dv.py build <dir>
python3 <skill>/scripts/dv.py check <dir>
node <skill>/scripts/smoke.mjs <dir>/index.html --shots <dir>/shots --states
```

- `build` assembles `index.html` from the template, the ledger, the kit (plus each round's
  `kit/round-<n>.html`) and every variant, newest round first, and fills the gallery chrome tokens and title.
  Rebuild after every change; never hand-edit `index.html` when the workspace exists. If a build bug ever forces
  you to patch the built file, say so in the reply: the gallery is not a clean build, and the next `build`
  overwrites the patch.
- `check` validates the ledger, IDs, spread rules, names, descriptions, contract notes and each prototype
  (interactive elements, handlers, placeholder text, emoji, external hosts), and confirms the built
  `index.html` can boot. Calls into kit helpers that wire events (`KIT.r2.wire(`, `bind`, `on…`, or any kit
  function that calls `addEventListener`) count as handlers, so options wired through the kit pass. Errors must be fixed; read the warnings.
- `smoke.mjs` (optional, needs Node and Playwright) loads every frame, records errors, types into the first
  text field and presses up to twelve visible buttons per option. It fails an option when a press changes
  nothing (a toggle that flips only attributes counts) or a `hidden` element still renders, and warns on a
  blank first screen, on controls covered by another element and on text cut off with no ellipsis. It saves a screenshot per option
  and runs an automated squint test that flags Evolve-or-higher look-alikes and Rethink or Reinvent options
  that look like today, listing each round's three nearest pairs whatever their score. `--states` also shoots
  every declared state of options with two or more states as `<id>--<state>.png` (the state in lower case, other
  characters as dashes; the exact name is in `results[].states[state].shot`); `--round <n>` tests one round only. Run it again with
  `--frame-width 390` to catch sideways scrolling at phone width. Its checks are heuristics: it cannot judge
  looks, copy, the truth of a total or the contract, so look at the screenshots and click the contract
  functions yourself.
- `build --standalone` also writes `variants-standalone/<id>.html`, one full page per option, for hosts that block
  embedded frames or for sharing a single option. `build <dir> --standalone-dir <scratch-dir>` writes only
  those pages, to a folder outside the workspace (relative to the current folder): use it for scripts that click through contract flows, because
  Playwright clicks into scaled gallery frames can time out and dialogs can fall outside the viewport.
- The build embeds the ledger in `index.html` (`<script type="application/json" id="dv-ledger">`), so a published
  gallery still carries its memory.

## 5. What the gallery gives the user

The template (`assets/gallery-template.html`) provides, with no extra work:

- rounds newest first, each with a spectrum strip showing where its options sit on the 1–10 ladder;
- full-size live frames that scale to the window, lazy-loaded, each in a sandboxed iframe;
- Full size and Overview layouts; a width switch (design size, desktop, laptop, tablet, phone);
- per option: shortlist, "not this", note, open full size (with previous and next), reset, and a State menu when
  the option declares states;
- a band filter (All, Refine, Evolve, Rethink, Reinvent, or the new-design bands) to cut the ten down while
  comparing;
- Compare: two to four shortlisted options side by side;
- Give feedback: composes a message from the shortlist, notes and a chosen next step, ready to paste back;
- keyboard: J/K next and previous, S shortlist, X not this, F full size, N note, R reset, Esc close;
- deep links (`#2c`, `?w=390`), an error badge on any prototype that throws, and storage-free fallback when the
  browser blocks local storage.

Do not restyle the gallery runtime beyond the chrome tokens; it should stay quietly out of the way of the
options.

## 6. Writing the gallery by hand (no scripts)

When Python cannot run, write `index.html` directly from the template:

1. Copy `assets/gallery-template.html`.
2. Replace `__DV_TITLE__` and `__DV_KEY__`; set `data-theme`; add chrome token overrides inside the
   `DV:TOKENS` region.
3. Replace the content between `<!-- DV:ROUNDS:START -->` and `<!-- DV:ROUNDS:END -->` with your round
   sections, newest first, using the same markup as the demo round (`section.dv-round` with `data-round`,
   `data-kind`, `data-w`, `data-h`; `article.dv-option` with `id`, `data-rung`, `data-band`, `data-axis`; the
   head row, the meta line, an empty `div.dv-frame`).
4. Replace the `DV:KIT` region with `<template id="dv-kit">…your kit…</template>`.
5. Replace the `DV:VARIANTS` region with one `<template id="variant-<id>">…fragment…</template>` per option.
6. Keep the ledger as JSON beside the file, or at the end of your reply.

In a later round, add the new section at the top of the rounds region and the new templates to the variants
region; leave earlier rounds and the kit template untouched. Round n's additions go in their own
`<template id="dv-kit-round-<n>">` after `dv-kit`; the gallery loads it into round n's frames only.

## 7. Publishing and sharing

One rule, decided by how the user opens files in this host:

- **The user opens files from disk** (a codebase, Claude Code, a desktop session): the gallery stays in the
  scratch folder (host-codebase.md); give the path and how to open it, and when an artifact tool is available,
  offer in one line to publish it as a private artifact for sharing. Publish without asking only when the user
  asked for a link and the gallery holds no private data.
- **An artifact is how the user sees files** (claude.ai chat with no file viewer): publish the built
  `index.html` as a private artifact; that link is the delivery, not an extra. It is self-contained and runs
  offline.
- Either way, follow the host's artifact rules (size limit, allowed CDNs, theming, when to publish); where they
  are stricter than this section, they win. Updating the same artifact keeps one link across rounds.
- Never publish a gallery that contains the user's private data or unreleased product details to a public
  location without asking.

## 8. Limits and fallbacks

- Size: ten rich prototypes are usually 150–600 KB. Hosts cap single pages around 16 MB; keep images as small
  inline SVG or compressed data only where needed. Older rounds open collapsed to their headers, so only the
  newest round's prototypes load until the user expands one.
- Offline: the gallery runs offline except for web fonts loaded from Google Fonts, which fall back to the system
  stack without a connection.
- If a host blocks embedded frames, each option shows "did not report loading" after a few seconds. Build with
  `--standalone` and point the user to `variants-standalone/<id>.html`.
- If nothing can be written to disk, output the full `index.html` in one fenced code block and the ledger in a
  second, with one line telling the user to save it as `.html` and open it.
