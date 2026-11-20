# Release evaluation — 1.0.0

Reviewed 2026-11-01 and 2026-11-02. This records what was checked, how, and what was not. Evidence files and recheck commands
are in [artifacts/design-variations/validation/](../../artifacts/design-variations/validation/README.md).

## Structural checks

| Check | Result |
|---|---|
| `claude plugin validate plugins/design-variations` | Passed with nothing to report |
| `claude plugin validate .claude-plugin/marketplace.json` | Passed |
| skill-creator `quick_validate.py` on `skills/design-variations` | "Skill is valid!" |
| `artifacts/design-variations/validate.py` (manifests against the Agent Plugins 1.0 schema, frontmatter, every relative link, ledger example against its schema, script syntax, ZIP contents against the source tree, checksums) | Passed |
| `dv.py check` on `assets/ledger.example.json` | Every ledger rule passes; the only errors are the 17 prototype files (16 options and the Now frame) the example deliberately does not ship |
| `dv.py lint-dc` and `dc-check.mjs` on `assets/canvas/` | 0 errors, 0 warnings; six Tweak states run |
| Ledger example against `assets/ledger.schema.json` (jsonschema, Draft 2020-12) | 0 errors |

## Runtime tests

- **Gallery.** Run A's gallery, rebuilt with the final `dv.py build`, passes `smoke.mjs` 11 of 11 at design width
  and 11 of 11 at 390 wide (131 and 130 button presses, each changed the page), and 11 of 11 with every declared
  state shot (33 shots, no errors). Run B's passes 9 of 10 at both widths: 1c fails for toggles that show
  nothing, the defect its review found. Run D's second round passes 10 of 10. Every warning (a clipped
  placeholder, amounts cut off at 390, a cut name and amount in 2j) matches a defect a reviewer found by hand.
  No look-alike pairs, no Rethink or Reinvent option close to today, no gallery errors.
- **Script fixtures.** The verifiers built fixtures for every new check: a working and a fake toggle, a hidden
  element overridden by CSS, a covered button, clipped text with and without an ellipsis, a carousel peek,
  checkbox, image and stepper toggles, wrongly typed ledger fields, round-kit names, signatures and the
  inspiration inventory. Each fails or passes as it should with the final scripts.
- **Claude Design canvas.** Artboards were rendered with the canvas runtime file from the user's own Claude
  Design export, locally and not redistributed. Verified: key and drag handlers, partial attribute holes and
  text holes, and separate state per imported copy. Two runtime behaviours found here are now documented in
  `references/host-claude-design.md`: element ids repeat across imports, and an artboard's head styles apply to
  the page that imports it.
- **Canvas logic without the runtime.** `dc-check.mjs` ran dry run C's ten canvas files: 21 Tweak states,
  0 errors, 0 unresolved holes. `dv.py lint-dc`: 0 errors, 0 warnings.
- **Gummble, live.** Pattern search, two screen searches and a batch detail call with images, run by the author
  on 2026-11-01. A query in the domain's own nouns returned only unrelated filler; the same need phrased as a UI
  pattern returned real matches, and looking at the images showed two of three were not true matches. The
  Gummble card and the round recipe in `references/inspiration-mcps.md` now say both things.

## Simulated skill runs

Each run was a separate agent that read the skill and carried out a realistic request on a synthetic fixture.
A different agent then reviewed the output adversarially: it ran the checks, looked at screenshots and graded
against the eval case's graders.

| Run | Request | Output | Review |
|---|---|---|---|
| A | Ten variations of a repository's invoices page | HTML gallery in a new `design-variations/invoices/` folder; the page and its tokens kept their hashes | 7 of 9 graders passed; partial on card copy (the cost said twice) and on rung labels stretched to fill slots. Six medium and six low defects |
| B | Ten directions for a new pricing page | HTML gallery in a new folder: three plain cards (1a) to a wheel you turn (1j); Gummble used live (11 searches, 15 screens viewed, 10 cited) | 4 of 6 graders passed; partial on interaction truth and on distinctness. One high defect (row toggles in 1c that show nothing), four medium, seven low |
| C | Ten variations of a Claude Design canvas's task list | New page with a base copy (layout Tweak), seven standalone artboards and an options document with a Now row; the original artboard's hash unchanged | Graders 01–04 passed; one high, four medium and five low defects |
| D | Iteration on A: shortlist 1c and 1g, pass on 1b, bolder, no left sidebar | Round 2 above round 1 in the same gallery; round 1's option files kept their hashes; Gummble used live (14 calls, 8 cited) | 2 of 6 graders passed; partial on keeping round 1 byte-identical (the shared kit gained round-2 code), the like-round recipe (roles and wildcards not recorded), and novelty (one option re-used the passed 1b's lead device). Four medium and seven low defects |

A fresh reader also audited the skill text cold and reported 31 issues. Most were applied (see below).

## What changed because of the evaluation

- **Gallery build bug.** The ledger was injected at the first `</body>`, which sat inside the gallery's own
  script, so the gallery failed to start while `dv.py check` still passed. Fixed, and the smoke test now
  reports a dead gallery instead of crashing.
- **Fixed-size canvas frames** clipped content that grew past the frame (run C's high defect). Artboards now give
  their main region its own scroll area, and the checks add several items and confirm the feedback stays visible.
- **Sparse fixtures** made options look alike. Rounds now share stress rows (long values, a busy day, empty
  fields) while the Now frame keeps the original data.
- **Budget.** A round's ten whole prototypes can exceed one turn. The skill now builds in batches from a shared
  kit of components and, when a turn runs out, delivers the finished options with a Degraded line and finishes
  the rest next turn, never shipping a broken option.
- **Inspiration enforcement.** `dv.py check` fails a round where a connected provider supplied no reference,
  and requires a Degraded line when none was connected.
- **Contract mapping.** Evolve-or-higher redesign options map every must-keep item to where it lives, and
  `dv.py check` fails unmapped items.
- **Examples.** The worked examples had mirrored an eval fixture, and runs copied them. They now use an
  unrelated domain, and the canvas example is a correct miniature round.
- **Smoke test.** First screens are captured before any clicks, and the overview sheet paints every frame.

Runs B and D and the three reviews led to a second set of changes. Four writers applied them, each owning
separate files, and two independent verifiers then checked completeness, consistency and the scripts. The
verifiers' 26 problems were fixed and their test fixtures re-run.

- **Fake toggles.** The smoke test now fails a toggle whose press changes nothing visible, and any element with
  the `hidden` attribute that still shows (run B's 1c). New kits hide `[hidden]` elements whatever a component's
  CSS says.
- **Honest placement.** After building, each option is placed again by the ladder's plane test and records its
  `plane`; `dv.py check` errors when a rung sits outside its plane. An uneven row is recorded, never relabelled
  (run A's middle rungs).
- **Ways back.** Redesign options at rungs 9 and 10 must build and record a `switch_back` (run A's 1i had none).
- **States and filtered views.** A states pass reads every sentence in each declared state and in a view filtered
  to one item; a total either matches what is shown or is labelled as the page total. `smoke.mjs --states`
  shoots every state (runs A and D showed totals and copy that were untrue there).
- **Second rounds.** Each option records its role (refine, push, crossover, secondary or wildcard), shown on its
  card; a like round needs a wildcard; a table shows how a like round combines with "bolder" or "closer"; a
  crossover's rung is measured from its closest parent; and the ladder's tests run against the picks (run D).
- **Directions the user passed on.** A passed option's `signature` is recorded, new first screens must not
  reproduce it, and `dv.py novelty` warns on wording that does (run D's 2g).
- **Distinct beyond the first screen.** Rethink and Reinvent options record `traits` (skeleton, device,
  interaction, moment) and share at most one; the swap and silhouette tests also run on each option's state
  after the main choice (run B's 1e and 1g, 1h and 1j).
- **New designs' looks.** Directions differ in at least two of ground colour, type and imagery, and when the brand
  is open at least half draw on the subject's own world (run B).
- **Narrow widths.** Controls and navigation are never hidden to fit; they collapse into a menu (run B).
- **The kit in later rounds.** New shared code goes in `kit/round-<n>.html`, which only that round's frames load;
  `kit/kit.html` and earlier rounds' files stay unchanged, apart from two disclosed exceptions (run D).
- **Inspiration.** One cheap call before trusting a sign-in notice; one record per copy of a provider; references
  found after planning are marked corroborating and shown as "Also seen in"; when to stop after weak matches;
  design-context servers such as Figma do not count as inspiration libraries (runs B and D).
- **The reply.** A word budget, heuristic checks reported as heuristics, the Degraded line repeated word for word,
  and odd behaviour the contract keeps raised as a question.
- **Scripts.** `dv.py check` confirms the built gallery can start, gives older rounds one note instead of a list
  of warnings, recognises handlers wired by kit helpers, flags multi-sentence descriptions in any script and
  checks new fields' types; `dv.py build` drops only the parts of a cost the description already says and adds
  `--standalone-dir`. `smoke.mjs` adds `--round`, `--states`, covered controls, clipped text and placeholders,
  blank first screens and each round's three nearest pairs.

## Not tested

- **Installed-host triggering.** No test of whether the description triggers the skill in an installed host,
  and no billed `claude plugin eval` run. The six cases in `skills/design-variations/evals/` are ready for one.
- **Claude Design itself.** Output was not loaded into claude.ai. The runtime file and the logic checker stand
  in for it; `dc-check.mjs` is a shim, not the product.
- **Independence.** The runs and reviews used the same model family as the author. They are simulated
  invocations, not a review by a different model.
- **Other inspiration providers.** Gummble was used live in runs B and D; Dembrandt answered contrast checks.
  Mobbin, Refero, UXKin and Figma were not exercised; their cards follow each provider's documentation as
  checked on 2026-11-01. Runs A and C ran without any inspiration library and exercised the Degraded path.
- **Browsers.** The gallery was tested in Chromium only.
- **Squint test.** The automated look-alike check compares coarse light and dark blocks of first screens. It is
  a prompt to look, not a verdict, and it does not compare the screens after a choice.
- **Layout checks not automated.** Text that spills past a card's border or overlaps other text (run D's 2h
  and 2i), controls hidden at narrow widths, and filter rows cut inside a scroller with no sign that more exist are
  rules in the skill, not checks in `smoke.mjs`.
- **Matching by wording.** Shared traits and passed signatures are compared by their words, so a reworded repeat
  (run D's 2g) still needs the planner's judgement.
