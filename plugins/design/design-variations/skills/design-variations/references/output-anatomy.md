# Output anatomy

Read this before building the first round, and whenever you write round copy. It defines what the variations
file looks like in every host, the copy formulas, the IDs and the ledger.

The format comes from real Claude Design options canvases this skill was designed around: a separate options
document beside the real component; turns stacked newest first under eyebrows like "TURN 7 · ADD IDEA PICKER"
and titles like "Five ways to pick an idea for a day"; a paragraph saying what all options share, how to switch
between them in Tweaks, and "Chosen: 7c, now the default"; rows with a violet ID chip (7a), a two-to-three word
name and one sentence such as "Opens under the Add idea button with a search field and a ranked list. The
calendar stays visible and nothing dims."; each row followed by the live, full-size prototype; and Chosen turns
that record merges ("4a layout with the 5c header, on the 3a filters"). This skill keeps that shape, raises the
count to ten, and adds a cost to every row, a Now frame, and the ledger.

## Contents

1. The file is new and separate
2. Page structure
3. Round header copy
4. Option row copy
5. The live frame
6. Chosen and merge rounds
7. IDs and names
8. Gallery chrome and theming
9. The ledger

## 1. The file is new and separate

Every round goes into a variations file that is not the original: a new canvas file or canvas, a new HTML file,
a new scratch folder. Name it after the subject: `Shipments board · Variations`, `design-variations/shipments-board/`.
The original stays exactly as it was until the user promotes a choice. Later rounds go into the same variations
file, on top.

## 2. Page structure

```
Top bar: subject · Variations | round jump | Full size / Overview | width | Compare (n) | Give feedback | ?
Round 3 · Day header                      ← newest round first
  Ten ways to head each day
  What is held constant… how to compare… Chosen: 3c (once chosen)
  Spectrum strip: positions of 3a–3j on the 1–10 ladder, bands under it
  3a  One line      Day, date and posts against the daily max on a single line. About 20px shorter than today.
      Keeps … · Changes … · Inspired by …
      [ live prototype, full size ]
  3b  …
  …
Round 2 · Chosen
  Day columns with date tiles
  1d layout with the 1g header, on the original filters.
  2a  1d with 1g dates
      [ live prototype ]
Round 1 · Calendar layouts
  …
```

Rounds are never deleted or rewritten. A correction to a shown option becomes a new option in a new round.

**The "Now" frame.** For redesigns, the newest round starts with the current design, unchanged and live, chipped
`Now` and labelled Today. It is the control the ten are judged against, and it is not one of the ten. In HTML it
is `variants/today.html`, declared by the ledger's `baseline`. On a canvas it is the base copy with its variant
switch set to `today`.

## 3. Round header copy

- **Eyebrow:** `TURN n · TOPIC` (the word comes from the ledger's `round_label`, default Turn; use the user's
  own word if their files have one). Topic is the subject or the sub-part this round varies ("Day header",
  "Shipments board", "Empty state"). Chosen rounds use `TURN n · CHOSEN`, edit rounds `TURN n · EDIT`.
- **Degraded line** (whenever something fell short, including when references came from the fallback ladder
  or the rung row is uneven): one plain sentence after the summary, e.g. "No reference library was connected;
  references are public pages captured today." or "Only nine options: a tenth Reinvent idea did not survive the
  contract check." The reply repeats it word for word under a "Degraded:" label (critique-and-presentation.md
  §5).
- **Title:** `Ten ways to <verb phrase>`, naming the user's job, not the component: "Ten ways to spot delayed
  shipments", "Ten ways to pick an idea for a day". With another count, use the number in words.
  Iterations can say what they do: "Ten takes on 2c and 2g", "Ten new directions", "Ten refinements of 4e".
- **Question** (optional, recorded in the ledger): the one design question the round answers, such as "How
  should dispatchers see what is running late?". Use it to write the title.
- **Summary paragraph** (two to four sentences):
  1. What every option shares: the same data, the same rules, the contract in one clause.
  2. What varies, in plain words.
  3. How to interact: "Every frame is live: filter, select, open the drawer."
  4. After a choice: "Chosen: 3c, now the base for round 4."
- When the round came from feedback, start the summary with the feedback in a clause: "From your picks 2c and
  2g: …".

## 4. Option row copy

- **Chip:** the ID, e.g. `3c`.
- **Name:** two to four words that say the idea ("Split ledger", "Command palette", "Inside the day"). Never
  "Option C", "Variant 3", "Modern", "Clean".
- **Description:** one plain sentence saying what the option is and what the user will see differently: "Opens
  under the Add idea button with a search field and a ranked list; the calendar stays visible and nothing
  dims." The cost lives only in `cost`; `dv.py check` warns on a second sentence, or when the description and
  the cost share most of their words.
- **Cost:** a short clause in the `cost` field, which the build adds after the description: "Takes 56px of
  height." For rungs 4 and above, name what users must relearn ("Bulk actions move into a select mode.").
- **Solves** (rungs 7–10): the user problem the bold option is for, in the `solves` field: "Late shipments are
  buried among on-time ones." The build shows it in the meta line, so every Rethink and Reinvent row reads
  "Solves … · Relearn …".
- **Switch back** (rungs 9–10, and fact-led new designs that hide the facts): how the user returns to the
  familiar view inside the prototype, in `switch_back`: "A List toggle at the top switches back to today's
  table." The build shows it in the meta line.
- **Meta line:** `Keeps …` (compact contract summary), `Changes …` (what moved), `Switch back …`, `Solves …`,
  `From 2c, 2g` (lineage), `Inspired by …` (seed references, each with its evidence strength: precedent,
  example, craft judgement or exploratory; inspiration-to-ideas.md §5) and `Also seen in …` (references with
  `use: "corroborating"`, found after the option was planned; never shown as its source).
- **Role chip** (like, combine and refine rounds): the option's `role` (Refine, Push, Crossover, Secondary
  axis, Wildcard), so the user can tell the wildcards apart.
- **Level badge:** band word and rung, e.g. `Evolve · 5`, added by the gallery from the data.

Write for someone deciding, not for a designer reading a spec: no token names, hex codes or component names
in the copy; name things as the user sees them.

## 5. The live frame

- Full size by default (the size from intake: 1440×900 desktop, 390×844 phone …), scaled down only to fit the
  window. The gallery's Overview mode shows them smaller in a grid for scanning.
- The whole surface, in its real chrome, with realistic data volume.
- Every frame is independent: interacting with one never changes another.
- Each frame can be reset, opened full size, shortlisted and annotated.

## 6. Chosen and merge rounds

When the user picks or merges, record it as a round of kind `chosen`:

- Eyebrow `ROUND n · CHOSEN`, a title naming the result ("Day columns with date tiles"), and a summary naming
  the parents by ID ("1d layout with the 1g header, on the original filters").
- One option (or a few, when the merge has a real open question), with `parents` listing the source IDs.
- `chosen` means one thing per round type: in a source round it lists the IDs the user picked or used as
  donors (the gallery shows "Chosen: 1d, 1g" there); in the Chosen round it lists that round's result. Never
  rewrite an earlier summary; the build renders the Chosen line from the field.
- **Edit rounds** are different: a single concrete change to one option ("make 3c's header bigger") becomes a
  one-option round of kind `edit` with a new ID and the source as parent. It never sets `chosen`.
- The next exploration round builds on the chosen option and says so.

## 7. IDs and names

- ID = round number + letter in order: `4a`, `4b` … `4j`. The 27th option in a round (rare) would need a second
  round; keep rounds to 26 or fewer.
- IDs and names never change once shown. A later variation of `2c` gets a new ID and lists `2c` as a parent.
- In canvases, IDs appear in artboard titles and the options document; in HTML, as element IDs (use
  `getElementById` or `[id="2c"]`; `#2c` is not a valid CSS selector).
- Deep links: `#2c` opens the gallery at that option; `?w=390` starts at phone width.

## 8. Gallery chrome and theming

- Redesigns: the gallery chrome (background, text, accent chip, fonts) uses the product's own tokens, so the
  page feels like part of the product. Map them in the ledger's `chrome.tokens`
  (`--dv-bg`, `--dv-surface`, `--dv-text`, `--dv-text-2`, `--dv-text-3`, `--dv-accent`, `--dv-on-accent`,
  `--dv-accent-text`, `--dv-font`, `--dv-font-display`, `--dv-font-mono`) and set `chrome.theme` to `dark` or
  `light`.
- New designs: neutral chrome (the template's grey light and dark defaults), so it does not bias the options.
  Controls that sit on top of a live prototype (focus and compare toolbars) always stay neutral.
- Chrome text must meet contrast (4.5:1 for text, 3:1 for large text and controls) against `--dv-bg`.
- No emoji in chrome; inline stroke icons only.

## 9. The ledger

`design-variations.json` sits beside the gallery (or as a file in the canvas, or in the reply when nothing can
be stored). It is the memory that keeps rounds consistent. Schema: `assets/ledger.schema.json`; a filled
example: `assets/ledger.example.json`.

Top level: `schema` (`design-variations/1`), `title`, `slug`, `mode` (`redesign` or `new`), `host`, `subject`,
`theme`, `chrome`, `contract`, `frame`, `rounds`.

Each round: `n`, `kind` (`explore`, `more`, `like`, `combine`, `refine`, `feedback`, `scope`, `chosen`,
`edit`), `topic`, `question`, `title`, `summary`, `degraded`, `feedback` (the user's words, verbatim, when a round
came from feedback), `basis` (IDs it builds on), `scope` (what varies, for scoped rounds), `distribution`,
`inspiration` (the inventory: connected, needs_signin, absent, failed, queries, fallback, and `connections`,
one `{provider, via, status}` per copy of a provider reached; inspiration-mcps.md §1), `chosen`, `passed`
(options marked "not this"), `count` (when not ten), `references`, `options`.

Top level also holds `baseline` (the Now frame: `name`, `description`, optional `w`, `h`, `states`) and
`preferences` (the taste profile, iteration.md §8).

Each option: `id`, `name`, `rung` (1–10), `band`, `plane` (redesigns: `surface`, `skeleton`, `structure` or
`scope`, the deepest plane it touches; spectrum-ladder.md §2), `axis` (primary), `secondary_axes`, `paradigm`
(the structural pattern, such as "split view" or "kanban"), `direction` (new designs), `idea` (one sentence),
`description` (the row copy, one sentence), `cost`, `keeps`, `changes`, `contract` (must-keep mapping),
`parents`, `refs` (reference IDs), `tags`, `states` (preview states the prototype supports, default first),
`file` (when the prototype lives outside `variants/`), and optional `w`/`h` frame overrides. Some fields depend
on the rung, the round or the user's verdict:

- `solves` and `traits` (rungs 7–10): `traits` is `{skeleton, device, interaction, moment}`, short phrases for
  the page skeleton, main visual device, core interaction and memorable moment, so the shared-traits cap can be
  checked (critique-and-presentation.md §2);
- `switch_back` (rungs 9–10): how the user gets back to the familiar view inside the prototype;
- `role` (like, combine and refine rounds): `refine`, `push`, `crossover`, `secondary` or `wildcard`
  (iteration.md §3);
- `signature` (every option the user passes on): one line naming its signature device, so a dead direction
  cannot return under a new label (iteration.md §4).

```json
{"id": "1j", "name": "Access review queue", "rung": 10, "band": "reinvent", "plane": "scope",
 "axis": "interaction-model",
 "description": "Opens on what needs attention, with one-click fixes; the full roster is one tab away.",
 "cost": "Browsing the roster takes one more step.",
 "solves": "Risky access goes unnoticed until it causes trouble.",
 "traits": {"skeleton": "attention queue over a Roster tab", "device": "fix cards with one-click actions",
            "interaction": "work down the queue", "moment": "the queue reaching zero"},
 "switch_back": "The Roster tab is today's table, with search, the role filter and every row action."}
```

Each reference: `id`, `provider` (`gummble`, `mobbin`, `refero`, `uxkin`, `figma`, `user`, `capture`,
`knowledge` …), `title`, `url` (never for `knowledge`), `borrowed` (the abstract idea taken), `strength`, and
`use`: `seed` (seen before the option was planned, or the option was rebuilt from it) or `corroborating` (found
later; inspiration-to-ideas.md §2).

Update the ledger in the same step that writes the round, and run `dv.py check` when scripts can run. Shown
rounds may get ledger metadata backfilled (a `signature`, a `plane`); their variant files never change. Field
warnings apply to the newest round only; `dv.py check` gives older rounds one note each.
