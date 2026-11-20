# Prototype standard

Read this before building (step 4) and again while verifying (step 5). The user asked for prototypes that are
"fully interactive, not basic wireframes". This file turns that into a bar every option clears, plus a build
strategy that makes ten such prototypes affordable.

## Contents

1. The bar: what fully interactive means
2. Content and data
3. States
4. Fidelity and theme fit
5. Accessibility and responsive floor
6. Build strategy for ten
7. Interaction recipes
8. Before an option counts as done

## 1. The bar: what fully interactive means

A user can sit in front of any option and do the subject's real job with it:

- **Every visible control responds.** Buttons do something visible, inputs accept and validate input, menus
  open and close, tabs switch, toggles toggle, sort and filter re-order and narrow the real data, selection
  works, drawers and dialogs open, submit and close. No dead buttons, no "coming soon", and nothing that is
  not a control drawn like one (a bordered label that looks like a disabled button).
- **Every contract function is reachable and works,** in the option's own way (preservation-contract.md).
- **State persists within the frame:** adding an item shows it in the list and the totals; deleting removes
  it; marking paid moves it between filters and updates the counts.
- **Feedback for every action:** a toast, an inline confirmation, a state change. Destructive actions offer
  undo or confirmation as the product does.
- **Keyboard works:** Tab reaches every control in a sensible order, Enter and Space activate, Escape closes
  overlays, arrow keys move within composite widgets the option introduces (menus, grids, listboxes, sliders).
- **Motion is real and restrained:** transitions where the product has them, honouring
  `prefers-reduced-motion`. Entrance motion never starts the main content from `opacity: 0` on first paint: a
  frame caught early (a screenshot, a slow load, a script error) shows a blank page. Animate from a visible
  state, or animate only secondary decoration.
- **Interaction truth:** a control that declares a state (`aria-pressed`, `aria-expanded`, `aria-selected`,
  `aria-checked`, a sort direction, a selected tab) must change something the user can see when it flips. A
  state that changes only in an attribute is a fake. A component rule that sets `display`
  (`.more { display: grid }`) beats the `hidden` attribute, so the region never hides: keep the kit's
  `[hidden] { display: none !important; }` guard and never write a rule that overrides it.
- **Interaction choices are deliberate:** a dialog only when it clearly helps, one at a time; at most two
  levels of disclosure; filters apply instantly or with an Apply button on purpose, not by accident; inline
  editing makes its save behaviour visible. Feedback sits on the lightest step that works (inline, then toast,
  banner, panel, dialog); an option that moves feedback up that ladder says why.

What may be simulated: network (instant or a short fake delay to show loading), authentication, payments,
file systems, emails sent. Simulate them believably and say so in the round summary if it matters.

## 2. Content and data

- Real copy from the product for redesigns; for new work, specific copy written for this product and audience.
  Never lorem ipsum, "John Doe", "Acme" (unless it is the user's fixture), "Item 1, Item 2".
- Realistic data volume: as many rows, cards or messages as the real surface carries on a normal day, plus the
  long and awkward values (a 40-character client name, a seven-figure amount, an empty optional field).
- The same dataset in every option of a round, so differences come from design. When the original's data is
  sparse (fewer than about eight items, or no long values), add stress rows to the shared kit that every option
  and the Now frame use: a very long name, ten to fifteen items, a crowded group, an empty optional field.
- Missing facts become visible placeholders ([YOUR PRICE]), never invented numbers or claims.
- Mask any real personal data you read from the codebase or screenshots.

## 3. States

Make the states the contract names reachable in every option, with a control in the prototype rather than
only in code. Common ones:

- empty (first use, filtered to nothing), loading (skeleton or progress), error (failed action with recovery),
  success, partial data, long content and overflow, disabled and permission-limited, selected, focus, hover;
- for forms: pristine, invalid with messages, submitting, saved;
- for collections: one item, many items, a huge number.

Every state tells the truth. Totals, counts and summaries are computed from what the state shows, or labelled
as page totals; end-of-flow messages count what actually happened. An empty state hides or disables chrome that
assumes items (docks, drag hints, bulk bars, "0 of 0 handled" counters) and offers the next step, such as the
product's create action. Calm states stay calm: zero overdue is not painted in alarm red.

When a state cannot be reached naturally (loading, a server error, a first-run empty account), do not put a
"preview state" control inside the design. Declare the states in the option's ledger entry (`"states":
["default", "empty", "loading", "error"]`). The gallery then shows a State menu beside the option and posts the
choice into the frame. The prototype listens with `window.addEventListener('dv:state', e => …)` (and can read
`window.DV_STATE`). On a canvas, use one enum Tweak named `previewState` instead.

Never print "sample", "demo" or "not wired" inside the design. Note anything simulated in the round summary or
the reply.

## 4. Fidelity and theme fit

- Hi-fi: final type, colour, spacing, icons, imagery treatment and microcopy. A sketchy look is wrong unless the
  user asked for sketches.
- Redesigns use the product's exact tokens and components as the starting point. Refine and Evolve options look
  like the product on its best day; Rethink options keep the product's visual language around a new structure;
  Reinvent options may push the visual language (scale, contrast, imagery, motion) but keep the brand's colours,
  type families and voice unless the user lifted them.
- New designs commit to one coherent direction per option (aesthetic-directions.md); new designs inside a
  product follow the theme contract.
- Avoid generic AI-made tropes: purple-to-blue gradient washes, glassmorphism on everything, rounded cards
  with a coloured left border, emoji as icons, centred hero plus three feature cards by default, identical
  rounded corners on every element, decorative charts with fake numbers.

## 5. Accessibility and responsive floor

The floor is the same for all ten options and never trades against boldness:

- Real elements: `<button>`, `<a href>`, `<input>` with `<label>`, `<select>`, `<dialog>` or an accessible
  equivalent. No clickable `<div>`s.
- Accessible names on every control, including icon-only buttons.
- Visible focus on everything focusable.
- Text contrast at least 4.5:1 (3:1 for large text and for control boundaries and icons that carry meaning).
- Meaning never by colour alone (status pills carry text; charts carry labels or patterns).
- Touch targets at least 44 by 44 px on touch platforms (24 px minimum with spacing on dense desktop tools).
- No clipping or overlap at the design size or the narrowest width the product supports (usually 390 px for
  web), including decoration over a control and a field too narrow for its placeholder. No horizontal page
  scroll; wide tables scroll inside their own container, with the identifying column and the main figure kept
  in view.
- Never hide controls or navigation to fit a narrow width. Collapse them into a menu (a button with
  `aria-expanded`) or a scrolling row with a visible affordance (a cut-off last item, a fade or scroll buttons),
  so the user can see that more exists.
- Content that grows stays reachable. In a fixed-size frame (canvas artboards especially) set the root to the
  frame's height and give the main region its own scroll area; then add several items and confirm the status
  line, the last row and the composer are still visible or scrollable.

Failures the original already has (a status pill at 4.4:1, a missing label) are fixed in every option, because
the floor is absolute; the Now frame keeps them, because it shows today. Say so in the reply. The user can ask
for them to stay.

An option that can only work by breaking the floor is not a candidate: change it or replace it.

## 6. Build strategy for ten

Ten hi-fi prototypes are affordable when the expensive parts are shared:

1. **Kit first:** tokens, fonts, base styles (including the `[hidden]` guard, §1), fixtures, formatters, icons
   and small helpers (a store, a toast, a focus-trap for dialogs). Every option reads the same kit. Later rounds
   add helpers in a per-round kit file and leave the shown kit unchanged (host-html.md §2).
2. **Faithful base next (redesigns):** a prototype that recreates today's design and behaviour. It is always
   shown as the Now frame and never counted among the ten; low-rung options start as copies of it.
3. **Low rungs as deltas:** Refine options change CSS, hierarchy, copy and a component or two on the base.
4. **Mid rungs on the base:** Evolve options swap components, move regions or change one interaction, on the
   base's data and most of its behaviour.
5. **High rungs as rebuilds:** Rethink and Reinvent options rebuild the surface on the same kit and data with a
   new structure and interaction model. Budget the most effort here: these are the options people remember.
6. **Parallelise when you can** (host-codebase.md §5), and integrate centrally.
7. **Batch and check:** build a–e, run the checks, then f–j. An option that still fails after two fix
   attempts is replaced by a new idea in the same band, never shipped broken and never silently dropped.
8. **Bold means visibly bold:** every Rethink and Reinvent option changes at least one of scale, composition,
   imagery or motion in a way a glance can see, inside the brand. If its first screen looks like today, it is a
   rearrangement, not a rethink.

Keep each prototype readable: one style block, one markup block, one script; small functions; no framework
unless the product uses it and the option needs it.

## 7. Interaction recipes

Patterns that keep prototypes honest without much code (plain JS):

- **Render from state:** keep one `state` object; every handler changes state and calls `render()`, which
  rebuilds the affected region. Keep focus where the user was after re-render (restore by element id).
- **Filtering and search:** derive the visible list from state on every render; show counts per filter; show an
  empty state with a way out ("Clear filters").
- **Selection and bulk actions:** a `Set` of selected IDs; a bulk bar appears with the count; actions update the
  data and clear the selection; a toast confirms.
- **Dialogs and drawers:** use `<dialog>` with `showModal()` (focus is trapped and Escape closes); return focus to
  the trigger on close.
- **Menus:** a button with `aria-expanded` controlling a list of buttons; close on outside click and Escape;
  arrow keys move between items.
- **Disclosure:** a button with `aria-expanded` and `aria-controls` that sets `hidden` on its region; check that
  the region really disappears (§1).
- **Drag and drop:** pointer events with a keyboard alternative (move up and down buttons, or a "Move to" menu).
- **Forms:** validate on submit and on blur after the first error; messages next to fields, linked with
  `aria-describedby`; disable the submit button only while submitting. A stepper that limits a typed value says
  so ("Up to 24 classes") instead of changing it silently.
- **Undo:** keep the last removed item; a toast with Undo restores it.
- **Loading:** a short `setTimeout` showing a skeleton the first time a view opens, skippable.

## 8. Before an option counts as done

- [ ] Every visible control does something you can see; every contract function works.
- [ ] The key states are reachable inside the frame, and every sentence and total is true in each of them.
- [ ] Same dataset as the other options; realistic, specific copy; no placeholder text.
- [ ] Looks like the product (or its committed direction); no generic tropes.
- [ ] Keyboard path complete; focus visible; contrast passes; nothing clips at the design size or the
      narrowest width, and no control disappears there.
- [ ] The first paint shows the content, not a blank frame waiting for an animation.
- [ ] No console errors on load or during the main flow.
- [ ] Its plan row (name, rung, plane, axis, keeps, changes, traits) still describes what was built; update the
      row if not, and never relabel the option to keep its slot.
