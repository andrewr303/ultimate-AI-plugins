# Iteration

Read this whenever the user responds to a round. Iteration is where the user's taste turns into a direction:
they react to what they see, and each new round moves toward what they liked while still offering real
choice. The rules here keep rounds consistent (same IDs, same contract), make every new round build on what
was learned, and stop the skill from showing the same idea twice.

## Contents

1. Reading feedback
2. Where the ladder starts in a later round
3. Round recipes
4. Novelty: never repeat yourself
5. Chosen rounds and merges
6. Scoped rounds
7. Convergence, stopping and promotion
8. Recording feedback and taste
9. Steer glossary

## 1. Reading feedback

Feedback arrives as chat text, the gallery's composed feedback message, comments on canvas artboards, or
annotated screenshots. Parse it into:

- **Picks:** option IDs or names they liked ("2c", "the timeline one" → resolve names to IDs from the ledger).
- **Passes:** options marked "not this" in the gallery, or named as disliked. They become dead directions.
- **Parts:** which part of a pick they liked ("2c's header", "the colours in 2g").
- **Rejections:** what they disliked, explicitly or by silence across a whole band.
- **Direction words:** more, different, bolder, wilder, simpler, closer, calmer, denser, more like X.
- **Constraints and lifts:** "no sidebars" (constraint), "we can drop the stats" (lift).
- **Next scope:** "now the empty state", "let's do the mobile version".
- **A decision:** "go with 3e", "this is it".

Treat notes as problem reports. Users are good at saying what bothers them and bad at prescribing fixes, so
turn each note into design moves yourself ("hard to see what's late" → late shipments lead each group).

Start your reply by saying how you read it, in one line: "Reading this as: evolve 2c and 2g, keep 2c's
header, bolder overall, no sidebars from now on." If two readings would produce very different rounds and the
user is present, ask one short question instead; otherwise take the more useful reading and say so.

## 2. Where the ladder starts in a later round

Every round's 1–10 ladder measures change **from that round's starting point**, which the summary names:

- Explore and "more" rounds start from the original (or, for new designs, from the conventional baseline).
- "Like", "combine" and "refine" rounds start from the picks or the merge.
- Scoped rounds start from the chosen design, varying only the scoped part.

Record the starting point in the round's `basis` field (`[]` means the original). In like, refine and combine
rounds, the "against today" and shared-traits tests run against the basis picks as well (spectrum-ladder.md §7):
an option that keeps a pick's skeleton is not a Rethink, whatever its slot.

## 3. Round recipes

### "More" / "none of these" / "something different" (kind `more`)

1. Diagnose the miss from the ledger and their words. Were the ten too timid (no picks in Rethink or
   Reinvent), too wild (no picks anywhere, or only from Refine), or simply wrong in kind (wrong axes)?
2. List every (axis, paradigm) pair and every aesthetic direction already shown; plan ten that use none of them
   unless a pair is clearly needed. Reach for unused rows in pattern-alternatives.md and variation-axes.md.
3. Run new inspiration queries (new terms, other providers, `exclude_ids` of everything seen).
4. Keep the full spread unless the diagnosis says shift it.
5. Run the novelty check strictly: in a `more` round any resemblance to an earlier option is an error.

### "I like 2c and 2g" (kind `like`)

Evolve toward the picks while keeping some exploration. Allocation for ten:

| Picks | Refine each pick | Push each along its axis | Crossovers | Change a secondary axis | Wildcards |
|---|---|---|---|---|---|
| 1 | 3 | 2 | 2 (with the best idea from an unpicked option or the original) | 2 | 1 |
| 2 | 2 each (4) | 1 each (2) | 3 (A's structure + B's header, B's structure + A's interaction, A with B's data presentation) | 0 | 1 |
| 3 | 1 each (3) | 1 for the strongest | 4 across the most compatible pairs | 1 | 1 |
| 4+ | Treat as a theme: name what the picks share, then run the 1-pick recipe on that shared idea | | | | |

- **Refine** keeps the pick's big idea and sharpens it (hierarchy, density, copy, states). It has one parent; an
  option that takes parts from two picks is a crossover.
- **Push** takes the pick's primary axis further than it went (denser, more editorial, more direct manipulation).
- **Crossover** takes each part whole from one named donor ("2c's layout with 2g's day header") and lists both in
  `parents`. Never average two directions: a midpoint between two picks is usually the option neither of them was.
- **Secondary** keeps a pick's primary axis and changes one of its secondary axes.
- **Wildcard** is a new idea informed by what the picks share, to avoid converging too early. When the ledger
  holds a taste profile (§8), seed most options toward it and make the wildcard deliberately break at least one
  recorded preference; say which in its `idea`.

Record each option's job in `role` (`refine`, `push`, `crossover`, `secondary` or `wildcard`); the gallery shows
it on the card, so the user can tell the wildcards apart. A like round of five or more options holds at least one
wildcard (`dv.py check` errors without one in the newest round). "Keep what they liked" means each liked part survives in the
options descended from its pick, not that every option carries both picks' parts: crossovers carry both, refines
and pushes carry one.

Order the ten by distance from the picks. Name each option fresh; list parents.

**With a distribution shift** ("I like 2c and 2g, bolder"): run this recipe as a `like` round, record the
shifted row in `distribution` (spectrum-ladder.md §5), and lay the roles onto it in order: refines take the
lowest slots, then pushes, then crossovers, and the wildcard takes the top. For two picks:

| Row | Rungs a→j | Refine (one parent) | Push | Crossover | Wildcard |
|---|---|---|---|---|---|
| default | 1–10 | 4 at 1–4 | 2 at 5–6 | 3 at 7–9 | 1 at 10 |
| bolder | 3, 4, 5, 6, 7, 7, 8, 8, 9, 10 | 2 at 3–4 | 2 at 5–6 | 5: four at 7–8, one at 9 or 10 | 1 at 9 or 10 |
| closer | 1, 1, 2, 2, 3, 3, 4, 4, 5, 6 | 4 at 1–2 | 2 at 3 | 3 at 4–5 | 1 at 6 |

With one or three picks, keep the allocation's proportions and fill the row in the same order. A crossover's rung
is measured from its closest parent (spectrum-ladder.md §7), so a crossover in a rung 7–8 slot must change the
structure even against that parent; one that only swaps a header into the other pick sits at 4 or 5.

### "Combine 2c and 2g" (kind `combine` or `chosen`)

- **Specified merge** ("2c's header with 2g's list"): build it as a Chosen round with one option, parents
  `[2c, 2g]`. Then, in the same turn, run a `like` round of ten variations of the merge, ordered from polish to a
  bold take on it, so the user again has ten to react to. Skip the ten only when the user says the merge is
  final ("just combine them", "that's the one").
- **Unspecified merge** ("combine 2c and 2g"): a `combine` round of ten different blends ordered from "2c with
  one idea from 2g" to "2g with one idea from 2c", with balanced hybrids and two or three novel syntheses in
  between. Each description says what came from which parent. Blends take the role `crossover`; the novel
  syntheses take `wildcard`.

### "Refine 2c" (kind `refine`)

Ten variations of 2c alone, a local spread from polish (spacing, type, emphasis, copy, states) through
structural tweaks within 2c's idea to a bold reinterpretation that is still recognisably 2c. Keep 2c's big idea
in every option. Late in an exploration there may not be ten truly different refinements. Say so, label the
smallest ones as micro-variants, and never pad with duplicates. Roles: polish and sharpening are `refine`, takes
further along 2c's axis are `push`, changes to one of its secondary axes are `secondary`.

### A small fix to one option ("make 3c's header bigger") (kind `edit`)

A concrete, single change is an edit, not an exploration. Make it as a one-option round of kind `edit` (new ID,
`parents: ["3c"]`), so 3c itself stays as shown. It is not a decision, so it never sets `chosen`. Open-ended
notes about one option ("3c feels cramped") get a `refine` round instead. Defects you find in your own options
before showing them are simply fixed in place; after showing, fix them with an edit round.

### "Bolder" / "wilder" or "closer to what we have" / "safer" (kind `feedback`)

Shift the rung distribution (spectrum-ladder.md, distribution shifts) and keep anything they liked. Bolder
moves options up the ladder and increases structural and interaction-model change; closer moves down and keeps
the layout recognisable, improving within it. When the same message names picks, it is a `like` round with the
shifted row (the like recipe's table above).

### Specific notes ("denser", "no sidebars", "the drawer feels slow") (kind `feedback`)

Turn each note into a contract constraint, a lift or a targeted change, apply it to every new option, and say
how each option answers it. If the notes target one option, run a `refine` round on it with the notes applied.

## 4. Novelty: never repeat yourself

- Keep a coverage map from the ledger: primary axes and positions, paradigms (split view, board, timeline,
  command palette, inline editing …), aesthetic directions, and references used.
- A new option must differ from every earlier option that is not its parent in at least one of: paradigm,
  primary axis position, interaction model, or aesthetic direction, and the difference must be visible in a
  screenshot.
- With scripts: `python3 <skill>/scripts/dv.py novelty <dir>` compares the latest round with every earlier one
  (same paradigm and axis, name and idea overlap, tag overlap). Fix every error; read every warning.
- Without scripts: list the earlier options' paradigms and axes next to your plan and strike any match.
- Re-showing an earlier option on purpose (as a reference point) is allowed only when labelled as such.
- **Dead directions stay dead.** A direction the user marked "not this" or rejected in words is recorded in the
  round's `passed` and is not offered again as a fresh idea; `dv.py novelty` treats resemblance to a passed option
  as an error in every round. Bring it back only when the user asks ("show me 1d again"). Options that were
  simply not picked are not dead; they just do not seed the next round.
- **Passed options get a signature.** Labels miss a device that returns under a new name, so give every passed
  option a one-line `signature` naming its signature device ("a chase band leading the page with the three
  most-overdue invoices and a primary Send reminders button"). At the plan step, and again on the built options,
  check every new first screen against each signature. A new option that leads with the same device is the dead
  direction again: drop the device, or, when a pick genuinely needs part of it, say so in the reply. If the
  reply promises to leave a device out, the built options keep that promise. `dv.py novelty` warns when a new
  option's idea, description or signature shares at least 60% of a passed signature's content words.
- If two options in the new round came out alike, redraw the weaker one against an explicit ban ("no card grid",
  "type only", "no split view"), with at most two retries; then replace it with a different plan row.

## 5. Chosen rounds and merges

When the user picks a winner or specifies a merge:

- Add a round of kind `chosen` (output-anatomy.md §6) with the result as its one option and `parents` set.
- Set `chosen` on the source round, so its summary reads "Chosen: 2c".
- In a canvas, set the base's variant switch default to the chosen value (host-claude-design.md §6).
- The next exploration round builds on the chosen design and says so.

## 6. Scoped rounds

After a whole-surface direction is chosen, users often explore one part at a time, as in the user's example
(filters, then calendar layout, then day header, then the idea picker):

- Hold everything else constant at the chosen design; vary only the scoped part.
- The spread still runs from a small tweak to a radical take on that part.
- Frames may crop to the part plus enough context to judge it (for example the top 560 px of a 1440-wide app),
  noted in the round's `h`.
- The contract may gain part-specific must-keeps (what that part must still let users do).

## 7. Convergence, stopping and promotion

- Signals of convergence: picks cluster in one band or idea; notes get smaller; the user names a winner. Offer
  a scoped round or promotion instead of another broad round.
- When the user has two or more favourites, offer a merge (a Chosen round that takes named parts from each). A
  reported parallel-design case study found a merged design outperformed the best single design; a merge is cheap
  to offer, so offer it.
- Signals of divergence: no picks, contradictory picks, "none of these". Run a `more` round and ask one sharp
  question if the miss is unclear.
- There is no fixed number of rounds. Never declare the design done for the user.
- **Promotion** happens only when asked ("apply 3e", "make it real"): describe the change, then apply it to the
  original in the host's way (host-claude-design.md §6, host-codebase.md §6), and record `promoted` in the ledger.

## 8. Recording feedback and taste

In the new round's ledger entry: `feedback` (their words, verbatim), `basis` (starting IDs), `kind`, `passed`
(options marked "not this", each given a `signature` in its own round), and, in each option, `parents` and, in
like, combine and refine rounds, `role`. Add constraints and lifts to the contract with the round number. This
record is what lets round 6 know why round 2's stats row disappeared.

**Shown rounds stay as shown.** Rules added after a round was shown can leave it short of fields (`plane`,
`traits`, `role`, `signature`, `solves`, a `degraded` line). `dv.py check` applies those field warnings to the
newest round only and gives each older round one note. You may backfill an older round's ledger metadata, such
as a passed option's `signature`, but never change its variant files. New shared helpers go in
`kit/round-<n>.html`, which the build injects only into that round's frames, after `kit/kit.html`; `kit/kit.html`
stays byte-identical once a round that uses it is shown. Two exceptions are allowed and disclosed in the reply
(host-html.md §2): a shared helper that is wrong in every round, fixed in `kit/kit.html`; and a kit-level
fidelity fix found later (a font the product loads differently), which goes in the new round's kit file and in
`variants/today.html`, because the Now frame loads no round kit. Earlier rounds keep the rendering they were
shown with.

Keep a small taste profile in the ledger's `preferences`. Each entry is a like, a dislike or a constraint, plus
the trait ("dense tables", "no illustrations", "bold numerals"), why, and the decisions it comes from. Record a
like or dislike only when at least two decisions support it, or when the user said it outright. A one-off pick
is not a taste. Constraints never override the accessibility floor. When a new request contradicts a recorded
preference, follow the request and update the profile.

## 9. Steer glossary

Steer words are vague on purpose. Translate each into concrete moves on named axes, inside the brand, and say
the translation in the reading line.

| Word | Usually means | Moves |
|---|---|---|
| Calmer, quieter | Less competing for attention | Fewer accents, softer contrast on secondary elements, fewer borders and badges, more whitespace, one focal point |
| Bolder, louder | More conviction | Larger type contrast, stronger use of the brand colour, bigger key numbers, more decisive layout, fewer equal-weight elements |
| Airier | More room | Larger spacing steps, longer line length limits, fewer items per row, larger hit areas |
| Denser | More at a glance | Smaller spacing steps, compact rows, inline metadata, more columns, progressive disclosure for detail |
| Simpler | Fewer decisions | Fewer visible controls, defaults instead of options, one primary action, secondary actions in menus |
| More premium | Considered, expensive-feeling | Refined type scale and tracking, restrained use of the palette, precise alignment, subtle motion, quality imagery. In a redesign, stay inside the brand's type families and colour roles; a new serif display only when the theme is lifted |
| More playful | Warmth and delight | Rounder shapes, livelier motion, illustration or character where the brand allows, friendlier copy |
| More like [product] | That product's specific moves | Name the two or three moves meant (layout, density, type) and borrow those, never the identity |
| Closer to today | Less change | Lower rungs, keep the layout and component patterns, improve within them |
| Totally different | Leave the explored space | A `more` round that excludes every prior paradigm and axis position |

