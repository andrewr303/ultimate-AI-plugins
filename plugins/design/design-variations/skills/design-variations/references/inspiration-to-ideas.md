# From references to options

Read this at step 2, after searching (inspiration-mcps.md) or when the user brings their own references. It
covers how to look at references, turn them into abstract moves, assign them to options without copying, and
what to do when no reference library is connected.

## Contents

1. Look before you cite
2. The reference board
3. Abstract moves, not screens
4. One lead reference per bold option
5. Matching references to bands, and evidence strength
6. When no library is connected
7. Rights, privacy and honesty

## 1. Look before you cite

- Open every reference you will use and look at the actual image (a detail call, a full-size screenshot, the
  page itself). Search-result text and thumbnails are not enough to cite.
- Record what you saw, not what the product is known for. If you could not open the image, the reference is
  "not seen": you may mention it as an idea from your own knowledge, labelled so, but never cite it as evidence.
- Do not infer motion, hover, responsive or multi-step behaviour from a single static screen. Use a flow (an
  ordered set of screens) when behaviour matters.

## 2. The reference board

Collect 8–20 references you actually looked at for an explore round (fewer for a scoped round, and as many as
the fallback yields when no library is connected). Model-knowledge entries may sit on the board, labelled, but do
not count toward the number. Give each an ID and a short entry:

| ID | Source | What it is | What it does well (abstract) | Role | Seeds |
|---|---|---|---|---|---|
| r1 | Gummble · [app] · [screen] (link) | Shipment list | Late shipments lead each group; one-key notify | Interaction reference | 1h |
| r2 | Mobbin · [app] · [flow] (link) | Payment reminder flow | Reminder preview before sending | Flow reference | 1d |
| r3 | Refero style · [site] (link) | Editorial finance site | Large tabular numerals, restrained colour | Visual reference | 1f |

Kinds of role, so each reference has a bounded job:

- **Structure:** how the surface is organised (layout paradigm, grouping, information architecture).
- **Interaction:** how actions happen (inline editing, drag, keyboard, bulk actions).
- **Flow:** how multi-step journeys run (onboarding, checkout, invite).
- **Copy:** microcopy for empty states, errors and calls to action.
- **Visual:** type, colour roles, density, imagery (mostly for new designs; for redesigns only within the brand).

Classify each observed trait as one of:

- **baseline:** what the category expects, which you should keep;
- **cliché:** what everyone does, which at least one option should break;
- **signature:** what makes that product itself, which you must never copy.

**Seeds and late references.** A reference seeds an option only when you saw it before the option was planned, or
rebuilt the option from it. A reference found later (a library that came online after planning, a search run
after building) gets `use: "corroborating"` in the ledger: the gallery lists it under "Also seen in", never
"Inspired by", and the reply never calls it the source of the idea. To make a late library a real seed, re-plan
and rebuild the named options from what you saw before showing them, and say which ones. `dv.py check` does not
count corroborating references as seeds. Keep the board to 20 entries; drop any that neither seeds nor
corroborates an option.

## 3. Abstract moves, not screens

Turn each reference into one or two moves that could apply to the user's product:

- "Group the list by what needs doing next, with a count per group" (not "make it look like App X").
- "Put the single most important number in the page title area at display size."
- "Let rows expand in place to show detail instead of opening a drawer."
- "Preview the reminder email before sending, inside the same panel."

A move is good when you can explain it without naming the source and it still makes sense in the user's
product and theme.

## 4. One lead reference per bold option

- Each Rethink and Reinvent option gets one **lead reference** for its main move and may borrow one or two
  details from others.
- Never average several references into a safe middle. When two references disagree, pick one for this
  option and give the other its own option, or drop it.
- Write a short **reference lock** for each bold option in the plan:
  - **lead:** the reference and its main move;
  - **borrow:** one or two details from others;
  - **reject:** the traits you are deliberately not taking (often the source's signature look);
  - **keep:** which of the user's brand and contract elements anchor it.
- Refine options usually need no references; their source is the product itself and the craft rules.

## 5. Matching references to bands, and evidence strength

| Band | Most useful reference kinds | Typical queries |
|---|---|---|
| Refine | Microcopy, states, detail treatments of the same pattern | "shipment table empty state", "status badge table" |
| Evolve | The same archetype done differently by strong products | "shipment list with filters web", "fleet dashboard summary" |
| Rethink | Other paradigms for the same job; flows | "accounts receivable board", "master detail finance app" |
| Reinvent | Adjacent domains that solved a similar problem differently | "email triage inbox", "task queue one-key actions", "timeline of payments" |

Searching adjacent domains for the top rungs is how radical options stay grounded: they borrow a proven idea from
elsewhere instead of inventing an unproven one.

Label each option's evidence in its "Inspired by" line (and each reference's `strength` in the ledger):

| Strength | Means |
|---|---|
| precedent | Two or more products you actually looked at do this |
| example | One product you looked at does this |
| craft judgement | A move from the product itself and craft rules (most Refine options) |
| exploratory | No precedent found; the idea is new. Allowed, especially at the top rungs, but say so |

Never claim precedent you did not look at.

## 6. When no library is connected

The round still happens. Use this ladder and say which rung you used:

1. **The user's references:** images, links, saved collections or files they shared. Treat a set they name as a
   collection, and count products rather than files.
2. **Public page captures:** with a browser tool, capture public pages the user names, or well-known public
   pages in the category, as any visitor would see them. Marketing home pages often hide the product, so go to
   feature pages, help-centre and documentation screenshots, and changelogs, which show real UI. A page that shows
   only copy is not a visual reference. Never use logged-in, paywalled or personal pages unless the user is
   signed in and asks.
3. **Your own knowledge:** patterns you know from the category and adjacent domains, labelled "from model
   knowledge, not a live reference". No links, no claims about a specific product's current screens.

Tell the user in one line that no reference library was connected and how to connect one (inspiration-mcps.md
has the setup line for each provider). Never stop the round to wait for a connection.

## 7. Rights, privacy and honesty

- Borrow patterns and principles, not identity. No logos, illustrations, photography, proprietary icon sets,
  distinctive copy or a recognisable clone of another product's screen. If an option starts to look like its
  lead reference, change composition, type treatment and copy until it reads as the user's product.
- Ask before uploading the user's private screenshots or files to any third-party service (for example a
  visual-similarity search).
- Cite every reference you used, in the gallery's "Inspired by" line (with its link; corroborating ones under
  "Also seen in") and in the ledger. Cite only references you actually opened.
