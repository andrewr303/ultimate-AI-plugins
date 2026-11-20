# Critique, verification and presentation

Read this at steps 5 and 6: before showing a round, and when writing the reply. A round is only useful if every
option works and tells the truth in every state, the ten are genuinely different, and the user can compare them
fairly and say what they want next.

## Contents

1. Verify every option
2. The side-by-side review
3. Self-review rubric
4. Presenting fairly
5. The reply
6. The recommendation
7. Reporting honestly

## 1. Verify every option

Run what the host allows, in this order:

1. **Static checks:** `dv.py check <dir>` (HTML) or `dv.py lint-dc <root>/project` (canvas). Fix every error.
   For HTML it also confirms that the built `index.html` can boot.
2. **Load and click** (HTML galleries and codebase harnesses): run
   `node <skill>/scripts/smoke.mjs <dir>/index.html --shots <dir>/shots --states`, with `--round <n>` in later
   rounds to test only the new round. It fails options that throw, have no controls, have a button that changes
   nothing (a toggle that flips only its attributes is one) or a `hidden` element that still renders; it warns on
   covered controls and clipped text; it saves a shot per option and per declared state. It does not prove the
   contract: click through each option's contract functions, and its own signature interaction (the thing its
   idea promises, such as "tap a line to see what's included"), yourself or with a browser-testing skill.
   Scripted click-throughs are easier on standalone pages written outside the workspace with
   `dv.py build <dir> --standalone-dir <scratch-dir>`, because a dialog in a scaled gallery frame can fall
   outside the viewport.
3. **States pass (every option):** switch it into each declared state, filter it to one client (or one item)
   and to nothing, and finish its main flow. Read every sentence and number on screen and ask whether it is
   still true there:
   - every group, lane or area total equals the sum of what it shows, or is labelled as the page total;
   - counts and end-of-flow messages match what happened ("All 7 handled" is false while one is Skipped);
   - an empty state hides or disables chrome that assumes items, and offers the way forward
     (prototype-standard.md §3).
   On a canvas, read each `previewState` branch the same way.
4. **Narrow width:** run the smoke test again with `--frame-width 390` (or the narrowest supported width) and fix
   any option that scrolls sideways or clips. Compare those shots with the design-width ones: every control and
   navigation item is still there, at worst in a menu or a scrolling row (prototype-standard.md §5).
5. **Keyboard:** tab through one representative low, middle and high option.
6. **Canvas:** follow the Design type's own rule on rendering. Render only in the real canvas (or in a canvas
   export's own runtime the user provides); never present a hand-built stand-in render as evidence. If it forbids rendering unless asked, rely on the
   static linter and a careful read of each option's handlers against the contract, and offer to check.

An option with a console error, a dead control, a missing contract function, clipped content or a sentence
that is false in one of its states is fixed before showing, or replaced with a different plan row and a note in
the ledger.

## 2. The side-by-side review

Look at all ten together (the Overview layout, or the smoke screenshots in a grid), starting with the three
nearest pairs the smoke report lists whatever their score, and ask:

- **Ten ideas, or ten tints?** Run these pairwise tests on each option's first screen and again on its
  after-the-choice state (the screen after its main interaction: an answered quiz, an opened item, a finished
  queue). Two different first screens can lead to the same result layout. Declaring that screen as a state
  (such as `result`) puts it in the smoke shots.
  - **Silhouette (squint) test:** blur your eyes, or look at the Overview thumbnails. If two options have the same
    arrangement of light and dark masses, they share a skeleton.
  - **Swap test:** if you could swap the headline, data or content between two options and nobody would notice,
    they are too close.
  - **One-sentence test:** you must be able to say how any two differ in one sentence. If you cannot, cut one.
  - **Shared-traits cap:** two options in the Rethink or Reinvent bands may share at most one of layout skeleton,
    main visual device, core interaction and memorable moment. The brand's type and colour do not count: in a
    redesign every option shares them. Check it with the `traits` each option records; `dv.py check` only
    catches phrases that match word for word, so compare near-matches yourself ("circles that grow" and "a pot
    that grows" are one moment).
  - **Against today:** a Rethink or Reinvent option whose first screen has today's silhouette is a
    rearrangement; push it or move it down the ladder. In later rounds, test against the basis picks too, and
    check every first screen against each passed option's `signature` (spectrum-ladder.md §7, iteration.md §4).
  Rebuild the weaker of a too-close pair against an explicit ban ("no card grid", "no split view", "type only"),
  then repeat the tests.
- **Is the spread real?** The first option should feel like a careful polish of today; the last should make
  someone say "I hadn't thought of that". The middle should fill the gap evenly. Place each built option again by
  the plane test (spectrum-ladder.md §2); an uneven row is said, never hidden by relabelling.
- **Is each option the best version of its idea?** A radical option that is half-built loses to a timid one
  and teaches the user nothing. Give the high rungs the most care.
- **Does every option look like the product** (or its committed direction)?
- **Would the user learn something from each one?** An option whose purpose you cannot state in one sentence
  should go.

## 3. Self-review rubric

Score each option 0–2 on each line; anything with a 0 is fixed before showing.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Works | Errors or dead controls | Main flow works, edges rough | Every control and state works |
| Contract | Drops a core function | All kept, one awkward to reach | All kept and easy to find |
| Distinct | Same idea as another option | Differs on one minor axis | A different answer, visible at a glance |
| Faithful to theme | Looks like another product | Mostly on brand | Unmistakably this product (or its direction) |
| Craft | Misaligned, generic, placeholder content | Clean but plain | Considered hierarchy, spacing, copy and detail |
| Accessible | Fails the floor | Passes with minor issues | Passes cleanly |
| Honest copy | Name or description misleads | Accurate but vague | Accurate, specific, states the cost, and still true in every declared state, filtered to one item and filtered to nothing |

## 4. Presenting fairly

- Every option gets an honest case and an honest cost. A set where only one option gets a real argument is a
  rigged vote.
- No favourite marked in the gallery. The recommendation lives only in the reply (§6), after the neutral list.
- Costs are concrete: "takes 56 px of height", "hides bulk actions behind a select mode", "new pattern to
  learn", "fewer rows visible", "harder to scan amounts".
- Order is by change level, not by preference. Because the first option and the middle one get an unearned
  boost (primacy and compromise effects), and the familiar one gets a status-quo boost, show today's design as
  the separate Now frame, never add a weak option to make another look good, and keep your recommendation out of
  the order and the styling.
- Every Rethink and Reinvent option names the user problem it solves and its relearning cost (what moved, what
  was renamed, what now takes an extra step).
- Name options by idea, never by preference words ("Best", "Recommended", "Clean").

## 5. The reply

Short; the gallery carries the detail. Aim for about 350–450 words in later rounds, and up to about 550 in a
first round, which also carries the inventory and the contract in brief. Count before sending, and cut what the
gallery already says.

When project or host instructions set a reply format (a status header, labelled fields, a decision layout, a
word cap), their wrapper wins. Put the parts below inside it once, rather than adding a second reply: for
example, the link and the ten lines under its result field, the recommendation and how to steer under its next
step. Keep this order wherever the wrapper allows.

1. **Where:** the link or path, and in one line what was made ("Ten live variations of the shipments board,
   from a quieter table (1a) to an inbox-style triage flow (1j)."). Name the host and that the original is
   untouched.
2. **What all ten share:** one line (the contract in brief; the dataset; what is simulated; any inherited
   accessibility failure the options fix while the Now frame keeps it).
3. **The ten:** one line each, in order: `1c · Split view: list on the left, the open shipment on the right;
   fewer columns visible.` Group by band with the band word as a small label if it helps scanning. Say which
   options answer which complaint in the brief.
4. **Inspiration:** the inventory line (connected, needs sign-in, absent), how many references were used, and,
   when nothing was connected, how to connect one (inspiration-mcps.md §7). A reference found after planning is
   "also seen in", never the source of an idea.
5. **Degraded:** when the round has a `degraded` line, repeat it word for word under this label, so the reply and
   the gallery say the same thing.
6. **Recommendation:** one sentence naming your pick for the user's stated goal and its cost, plus a runner-up
   and what would make it the better choice (§6).
7. **Next:** how to steer: "Shortlist and add notes in the gallery, then Give feedback, or reply with picks and
   what you liked, e.g. 'like 1c and 1g, keep 1c's header, bolder'. Say 'more' for ten new directions."
8. **Anything not done or not checked**, plainly (§7). Note anything simulated (sending email, payments,
   network). Raise any odd behaviour the contract made every option keep as a question ("Send reminder still
   shows on paid invoices, as it does today; should it?"; preservation-contract.md §5).

## 6. The recommendation

Every round's reply ends its list with one recommendation, because a decision helper that never commits leaves
the user doing all the weighing. Make it in a sentence or two, tied to the user's stated goal and audience, and
give it a cost: "If the main job is catching delays every hour, 1e, because it puts late shipments first
without hiding bulk actions. It costs the at-a-glance totals row." Name the runner-up and what would make it the
better choice. Never change the gallery to favour it, and never preselect it in a canvas Tweak. When you
recommend a Rethink or Reinvent option for production, say what justifies that much change (diminishing returns
from small fixes, outdated technology, tangled structure, very poor results, falling behind competitors) and
how users could switch back during the transition.

## 7. Reporting honestly

- Say which checks ran and which did not ("smoke test passed on all ten; keyboard checked on 1b, 1f and 1j";
  "canvas not rendered, per the canvas's rules; static lint clean").
- Report automated checks as heuristics, with what they test and what they miss: "the automated squint test
  flagged no look-alike pairs (it compares light and dark blocks, first screens only)"; "smoke found no dead
  controls by its change test, which cannot tell whether the change is the right one". Never turn a clean
  heuristic into a claim about the designs, such as "no two options look alike" or "everything works".
- Say when the gallery is not a clean build: a built `index.html` you patched by hand, or a kit fix that changed
  how earlier rounds render (host-html.md §2 and §4).
- Say which inspiration sources were searched, and that model knowledge was used where it was.
- Never claim a render, a test, an MCP call or a reference you did not actually make or open.
