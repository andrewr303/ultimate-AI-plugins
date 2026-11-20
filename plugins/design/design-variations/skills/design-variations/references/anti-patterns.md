# Anti-patterns

Read this when reviewing a plan (step 3) or a built round (step 5), or when a round feels weak. Each row is a
failure seen in design-option work, how to spot it and what to do instead.

| Failure | How it shows | Fix |
|---|---|---|
| Ten tints | Options differ in accent colour, radius or copy; screenshots look alike | Give each option a different primary axis position or paradigm (variation-axes.md); cut duplicates |
| Everything varies at once | An option changes layout, colour, type and interaction together, so nobody can tell what made it good | One primary axis per option; secondary changes follow from it |
| Timid spread | No option a stranger would call radical; the top rungs are rearrangements | Rebuild 9–10 around a new metaphor, job framing or interaction model (pattern-alternatives.md) |
| Wild spread | Low rungs already restructure the page; nothing is a safe improvement | Rebuild 1–3 as polish on the faithful base |
| Radical means broken | A reinvented option drops search, bulk actions or totals | Contract check (preservation-contract.md §5); find another way or replace the option |
| Wireframes | Grey boxes, placeholder copy, unstyled controls | Hi-fi with the product's tokens and real content (prototype-standard.md) |
| Fake interactivity | Buttons that do nothing, menus that never open, filters that do not filter, a toggle whose icon flips while its region stays put | Every visible control responds; keep the kit's `[hidden]` guard; test before showing (prototype-standard.md §1) |
| Copy that lies in other states | Group totals that ignore the filter, "All 7 handled" with one skipped, a dock that invites drags in an empty list | The states pass: every declared state, one item, nothing (critique-and-presentation.md §1) |
| Relabelled rungs | Rung chips fill the slots, but the built option is today's table with a band on top | Place each built option by the plane test; rebuild, replace or record an uneven row (spectrum-ladder.md §2) |
| Same idea after the click | First screens differ, but two options land on the same result layout | Swap and silhouette tests on the after-the-choice state too (critique-and-presentation.md §2) |
| Blank first paint | Frames and screenshots come up empty while an entrance animation runs | Never start main content from `opacity: 0` (prototype-standard.md §1) |
| Theme drift | Options look like a different product, or like each other's template | Start from the product's tokens and components; push the visual language only within the brand (from rung 2 up), and beyond it only when the user lifts the theme |
| Timid top rungs | Rethink and Reinvent options are rearrangements in identical styling | Change scale, composition, imagery or motion visibly within the brand; the squint test against today must fail |
| Budget overrun | The round stops half-built, or the last options are thin | Build in batches; shared components in the kit; deliver finished options with a Degraded line |
| Generic AI look | Gradient washes, glass everywhere, left-border cards, emoji icons, the same centred hero | Use the product's language or a committed direction; remove tropes |
| Neutral collapse | In a new design, several options are a white ground, near-black ink and a neutral grotesk under different direction names | Directions differ in at least two of ground, type genre and imagery; half draw on the subject's own world (aesthetic-directions.md §2) |
| Lorem and fake data | "John Doe", "Item 1", invented stats | Real or realistic data; visible placeholders for missing facts |
| Copied reference | An option is a recognisable clone of another product's screen | Borrow the abstract move (inspiration-to-ideas.md); change composition, style and copy |
| Inspiration theatre | References listed but no option actually uses them, references never opened, or references found after building cited as the source | Seed specific options from specific references and say what was borrowed; late finds are `corroborating` (inspiration-to-ideas.md §2) |
| Skipped MCPs | A design-reference MCP was connected but not searched | Inspiration is a required step when one is connected (inspiration-mcps.md) |
| Overwrote the original | Edits landed in the real component, canvas artboard or page | New files only; promotion is separate and explicit |
| Renumbered options | Round 2 reuses `1c` or renames shown options | IDs and names are permanent; new options get new IDs and list parents |
| Rewritten history | Round 2 helpers appended to the shared kit, so round 1 frames load new code | New helpers go in `kit/round-<n>.html`; earlier files stay byte-identical, apart from the two disclosed exceptions in host-html.md §2 |
| Repeats across rounds | A "more" round shows the same paradigm again | Novelty check against the ledger (iteration.md §4) |
| Converging too fast | Every option in a `like` round is a near copy of one pick, or keeps a pick's skeleton at Rethink rungs | Keep crossovers, pushes and at least one wildcard, each with its `role`; test bold options against the basis (iteration.md §3, spectrum-ladder.md §7) |
| Averaged merge | "Combine 2c and 2g" yields a grey middle with neither option's strength | Take each part whole from a named donor (iteration.md §3) |
| Zombie directions | A direction the user passed on comes back as "new", or its signature device leads a new option under another name | Ledger `passed`, a `signature` for each passed option and the dead-direction rule (iteration.md §4) |
| Notes in the design | "Demo data", "not wired" or a state switcher printed inside the prototype | States through the gallery State menu or a canvas Tweak; simulation noted in the summary |
| Rigged vote | One option is polished and argued for; others are half-built | Equal care and honest costs for all; no favourite marked |
| Wall of text | A long essay before the link; ten paragraphs of rationale; a reply near a thousand words | Link first, one line per option, about 350–450 words in later rounds; the gallery holds the detail (critique-and-presentation.md §5) |
| Asking instead of showing | A questionnaire before any design | At most one round of questions, only when decisions are truly open; otherwise let the ten options ask |
| Unverified claims | "All tested" without running anything; "no two options look alike" because a heuristic flagged nothing | Report exactly what ran, and heuristics as heuristics with their limits (critique-and-presentation.md §7) |
| Isolation | Options judged on a blank page, missing the real chrome and data | Show the whole surface in context, with realistic data volume |
| Mobile afterthought | Options break at phone width, or navigation vanishes to pass the overflow check | Check the narrowest supported width for every option; collapse controls into a menu or a scrolling row, never hide them (prototype-standard.md §5) |
