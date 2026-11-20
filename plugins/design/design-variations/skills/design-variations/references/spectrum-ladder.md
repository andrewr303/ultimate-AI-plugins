# The spectrum ladder

Read this at step 3 of every round. It turns "ten outputs from smaller tweaks to radical redesigns and
everything in between" into a ladder with ten rungs, four bands and a default slot plan, so the spread is built
on purpose instead of hoped for. Each rung has a test, so two people would place the same option on the same
rung.

## Contents

1. Why a ladder
2. The ten rungs for redesigns
3. The four bands
4. The default slot plan
5. Distribution shifts
6. The ladder for new designs
7. Rungs in later rounds
8. Checks

## 1. Why a ladder

Designing several alternatives in parallel, then comparing them together, produces better and more varied
results than refining one idea at a time. Showing alternatives also makes people's ratings more honest: a single
design gets inflated praise. A deliberate spread stops the options drifting into one safe middle, which is where
model-generated ideas tend to go when nothing pushes them apart.

Ten options are more than people usually compare at once. Research on whether large choice sets overwhelm people
is mixed: a meta-analysis found no general overload effect, and the conditions under which it appears are
debated. So the ladder adds structure as a precaution. The order
runs from least to most change, four labelled bands group the options, and each option differs from today on one
named axis. The round header restates the goal and must-keeps. The user can read the round like a map: "these
three are polish, those two are new paradigms".

Rungs are defined by how deep a change goes, because what users must relearn grows with depth. A restyle costs
almost nothing; a moved region breaks spatial memory; a new way to do the task breaks muscle memory; a new
organising idea breaks the mental model. People feel that loss even when the new design is better, so each rung
says what it may change, what it must keep, and what it asks users to relearn.

## 2. The ten rungs for redesigns

**Placing an option.** Find the deepest plane the option touches, then judge its breadth. The four planes, from
concrete to abstract:

| Deepest plane touched | What it covers | Rungs |
|---|---|---|
| Surface | How it looks: colour, type, shape, icons, motion | 1–3 |
| Skeleton | Where things sit and which controls and components do the job | 3–5 |
| Structure | How content is organised and how the core task flows | 6–8 |
| Scope or strategy | What features exist, and what the surface is for | 9–10 |

Within that range, pick the rung whose test the option passes. When two pass, the broader change (more of the
surface, more planes at once) takes the higher rung. Never place an option by how different it looks: a loud
restyle is still rung 2, and a quiet-looking new organising idea is still rung 9. Each rung allows everything
the rungs below it allow.

**Place it again after building.** Plans drift: an option planned as a paradigm shift often ships as today's
table with a new band on top. Once it is built, judge the prototype, not the plan row, and record the plane in
the option's `plane` (`surface`, `skeleton`, `structure` or `scope`; redesigns only). If the option landed below
its slot, rebuild it to earn the slot or replace it with another plan row. If neither fits the turn, keep the
honest rung and say in the round's `degraded` line that the row is uneven. Never relabel an option to fill a
slot. `dv.py check` errors when a rung sits outside its recorded plane's range, but only you can see whether the
plane itself is right. Common misplacements:

| Built option | Is really | Not |
|---|---|---|
| A chart or summary band added above today's unchanged table | 5: a region added | 7 |
| Expandable rows or an accordion on today's list | 4: a component swap | 7 |
| Today's table made denser, plus keyboard shortcuts and a command palette | 3 to 6: density, then interaction | 8 |
| A typographic restyle that also turns the table into a list | 4 at most | 6 |
| The same records regrouped into panels by a new object (by client) | 8: a new organising object | 9 |

| Rung | Name | May change | Must preserve | Test | Relearning risk |
|---|---|---|---|---|---|
| 1 | Polish | Values within today's styles: spacing, alignment, weights, hover, focus and disabled states, copy fixes | Every element, position, component, palette role, flow and label meaning | Laid over today, nothing is added, removed or moved to another region | Negligible: nothing to relearn |
| 2 | Restyle in system | One surface axis applied differently with the product's own tokens: colour application, the shape and depth set, icon style, calm motion | Layout, regions, components, copy, flows, palette roles | Same regions and components; the difference is styling only | Low; brand drift if overdone |
| 3 | Hierarchy and density | What leads and by how much; one density step for the whole surface; the grouping device; label wording | The same elements in the same regions; task order; navigation | Every element is still in its region; at least one emphasis or density change is visible | Low to moderate: habitual scanners may miss demoted items |
| 4 | Component swap | Components replaced by others doing the same job: a control, a feedback pattern, how one region shows its data | Page skeleton, data, every function in the same place, navigation, flows | Regions unchanged; at least one component type changed; every function still where it was | Moderate but local: one learned interaction changes |
| 5 | Region re-layout | Where regions sit and how big they are; column count; sticky areas; where navigation, filters and actions live | Most components, the information structure, the navigation model, flows | At least one region moved; the information structure is unchanged | Moderate: spatial memory breaks ("where did X go?") |
| 6 | Interaction model change | How the core task is done: inline editing, drag, command-first, batch or instant, staged or single page | Information structure, data, features, outcomes, navigation model | The core task's steps differ; the outcome and the data are the same | Moderate to high: muscle memory; needs clear affordances and keyboard parity |
| 7 | Layout paradigm shift | The whole surface's paradigm, with the data form and interaction that follow from it | All objects, fields, functions, permissions, the brand and theme, navigation entry points | The paradigm has a different name; every function is present | High: dropping familiar list patterns has measurably cut usability |
| 8 | IA and navigation restructure | Grouping, the organising object, the navigation model and disclosure depth, at page or app scale | Functions, data, brand; every old entry point still leads somewhere | The navigation tree or screen count differs; every old entry point maps to a new one | High: landmarks are lost; worth it when today's structure is tangled |
| 9 | Reconceived experience | A new organising metaphor or modality; features may be folded together or added | The user's goal, every must-keep function (possibly reached differently), data truth, unlifted brand anchors | The primary metaphor differs; a mapping gives each original function its new place | Very high: needs a switch-back path |
| 10 | Radical reinvention | Structure, interaction and, when the theme is lifted or new, the visual world at once; the job itself reframed | The contract minimum: goals, required functions, data truth, accessibility floor, unlifted brand anchors | Differs from today on at least three planes; the contract checklist passes | Highest: in a real launch it needs a reason beyond looks; in a round it is a probe to borrow from |

Typical moves:

| Rung | Typical moves |
|---|---|
| 1 | Fix rhythm, tighten table padding, add visible focus, align baselines, clearer numerals |
| 2 | Flat to layered surfaces; outlined to filled icons; accent moved from borders to fills |
| 3 | Primary action enlarged and secondary demoted; comfortable to compact; borders replaced by whitespace groups |
| 4 | Dropdown to segmented control; modal to side panel; tabs to accordion; one table region to a card list |
| 5 | Filter sidebar to a top bar; detail page to a side panel; summary made sticky; bulk actions to a sticky bar |
| 6 | Edit page to inline editing; form to drag-to-schedule; wizard to one page; batch Apply to instant |
| 7 | List to board; table to calendar or timeline; list–detail to feed; page to canvas |
| 8 | Organised by object to organised by task; hub to sidebar; two screens merged; settings split |
| 9 | Assistant-led flow; spatial canvas; automation first ("it plans for you"); timeline as home |
| 10 | Designed today from first principles for this audience; a different first question, everything still offered |

**Rungs 9 and 10 carry two extra notes**, in the plan row and inside the prototype:

- **Function mapping:** each original function and its new place ("role change → the person's cells and row
  menu"). Nothing on the contract may be missing from it. In the ledger it goes in the option's `keeps`.
- **Switch-back:** how a user gets back to the familiar way inside the prototype (a list toggle, the full
  roster one tab away), built and working, and recorded in the option's `switch_back`. `dv.py check` errors on
  a redesign option at rung 9–10 without one. An option whose own cost says the familiar view is gone has no
  switch-back yet: build one. When the option is recommended for production, add how the change would be
  introduced: a preview, a way to switch between old and new for a while, and a clear note of what improved.

Visual boldness never raises a rung on its own. A bolder use of the brand pairs with a deeper move (a region
re-layout that also sets the key number large is rung 5), or comes from the steer words (iteration.md, steer
glossary). Rung 10 is radical but never a different product. The contract (preservation-contract.md) holds at
every rung.

## 3. The four bands

| Band | Rungs | The user should feel | Risk to state |
|---|---|---|---|
| **Refine** | 1–3 | "Ours, but better" | Little to relearn; may not solve deeper problems; demoted items can be missed |
| **Evolve** | 4–6 | "Ours, reorganised" | One learned control, location or habit changes; worth it when the reason is clear |
| **Rethink** | 7–8 | "A new way to do the same job" | Landmarks and familiar patterns are lost; must show its payoff fast |
| **Reinvent** | 9–10 | "I hadn't thought of that" | Highest change aversion; needs a mapping and a switch-back; best as a direction to borrow from, or for new audiences |

People resist change to familiar tools even when the new version is better. That resistance fades when the
benefit is clear and controls are easy to find. So every Rethink and Reinvent option makes its payoff obvious
inside the prototype and keeps every function easy to find.

Recommending a high rung for production needs a reason beyond looks or boredom: improvements to today's design
have stopped paying off, the technology is outdated, the structure is tangled, results are very poor, or
competitors are clearly ahead. Name the reason when you recommend a Rethink or Reinvent option
(critique-and-presentation.md, the recommendation).

## 4. The default slot plan

Ten options, one per rung, ordered a→j:

| Slot | Rung | Band | Rung name | Aim |
|---|---|---|---|---|
| a | 1 | Refine | Polish | Today's design on its best day |
| b | 2 | Refine | Restyle in system | One surface axis used better, with the product's own tokens |
| c | 3 | Refine | Hierarchy and density | A clear re-weighting of what leads, or one density step |
| d | 4 | Evolve | Component swap | One component replaced to fix a real friction |
| e | 5 | Evolve | Region re-layout | Regions rearranged around the main job |
| f | 6 | Evolve | Interaction model change | The core task done a different way |
| g | 7 | Rethink | Layout paradigm shift | A new paradigm for the whole surface |
| h | 8 | Rethink | IA and navigation restructure | A new organising object or navigation model |
| i | 9 | Reinvent | Reconceived experience | A new organising metaphor, with a mapping and a switch-back |
| j | 10 | Reinvent | Radical reinvention | The job reframed from first principles, contract intact |

Each slot still gets its own primary axis, and the axis should fit the rung (variation-axes.md §2). By default no
primary axis leads twice in a round, and two slots never share both rung and axis (variation-axes.md §3). The
slot plan is a target: the rung each option ends on comes from placing the built option (§2), and an honest
uneven row beats a relabelled even one.

## 5. Distribution shifts

When feedback or the brief asks for a different centre of gravity, change the rung list. Keep the order, and keep
the spread across the whole of the shifted range: every row below runs from its own low end to its own high end.
Record the row in the round's `distribution` so `dv.py check` applies the matching rules.

| Signal | `distribution` | Rungs for a→j |
|---|---|---|
| Default | default | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 |
| "Closer to what we have", "safer", "small tweaks" | closer | 1, 1, 2, 2, 3, 3, 4, 4, 5, 6 |
| "Bolder", "push it", "overhaul", "complete redesign", "radical redesign" | bolder | 3, 4, 5, 6, 7, 7, 8, 8, 9, 10 |
| "Only radical" (explicit) | only-radical | 7, 7, 8, 8, 8, 9, 9, 9, 10, 10 |
| "Only small changes" (explicit) | only-small | 1, 1, 1, 2, 2, 2, 3, 3, 3, 4 |
| Daily-use expert tool (when nothing else is said) | default | Default, but make 7–10 especially careful about findability |

With a different count, scale the row and keep its two ends: default with five options → 1, 3, 5, 7, 10; with
four → 1, 4, 7, 10; with three → 1, 5, 10.

- **A brief that complains about the look** ("feels dated", "looks cheap") keeps a rung-2 restyle-in-system
  slot in every row, because that is where a look complaint is answered best. The exception is an explicit
  only-radical request: there one bold option leads on the look, and the `degraded` line says so. Under bolder the first slot drops
  from 3 to 2: 2, 4, 5, 6, 7, 7, 8, 8, 9, 10. The bold options may also refresh the look, but one option leads on
  it.
- **Like, combine and refine rounds** lay their roles (refine, push, crossover, secondary, wildcard) onto the
  shifted row; iteration.md §3 has the table.

## 6. The ladder for new designs

With no original there is nothing to relearn: resistance to change is about losing something familiar, and a
first-time product has nothing familiar to lose. What new designs risk instead is novelty and learnability.
People bring expectations from similar products, so the further an option strays from the category's convention,
the more it has to teach itself. The ladder therefore measures distance from convention: the patterns and visual
norms people already know for this kind of thing on this platform (or inside this product's theme).

| Rung | Band | Step | Novelty and learnability risk |
|---|---|---|---|
| 1 | **Proven** | The category's convention played straight, executed exceptionally | None beyond execution |
| 2 | **Proven** | The convention plus one signature detail | Low |
| 3 | **Proven** | The convention in a distinct aesthetic direction | Low; the direction must suit the audience |
| 4 | **Fresh** | An alternative proven pattern for the core task | Low to moderate: known pattern, unexpected here |
| 5 | **Fresh** | A paradigm common in an adjacent category | Moderate: familiar elsewhere, new here |
| 6 | **Fresh** | A hybrid of two proven paradigms | Moderate: two models to read at once |
| 7 | **Novel** | An uncommon but documented pattern (command-first, canvas, guided questions) | High: must be usable at first sight |
| 8 | **Novel** | A strong aesthetic stance plus an uncommon structure | High: style and structure are both unfamiliar |
| 9 | **Experimental** | A new metaphor borrowed from another domain | Very high: the metaphor has to explain itself |
| 10 | **Experimental** | An experimental, unproven interaction | Highest: a direction to borrow from as much as to ship |

Every option, however experimental, lets a first-time visitor complete the core task without instructions. New
designs inside an existing product keep the product's theme at every rung (theme contract); open new designs may
also vary the aesthetic direction across options (aesthetic-directions.md).

**Fact-led subjects.** On a pricing page, a timetable, a menu, a spec sheet or a comparison, the core facts are
the first-five-seconds payoff: a visitor expects to see every price or plan at once. An option that hides them
behind interaction (a quiz, a dial, a configurator) puts a one-click way to the plain facts on its first screen,
records it in `switch_back`, and names what is hidden in its cost. At rungs 9–10 every new design records a
`switch_back` (`dv.py check` warns without one).

## 7. Rungs in later rounds

A later round's ladder measures change from that round's starting point, named in its summary (iteration.md §2).
In a `like` round built on 2c, rung 1 is a polish of 2c and rung 10 is a radical take that keeps 2c's core idea.
Record the starting point in the round's `basis`.

**Test against the basis, not only today.** In like, refine and combine rounds, run the "against today" test
(critique-and-presentation.md §2) and the shared-traits cap against the basis picks too. A Rethink or Reinvent
option that keeps a pick's skeleton is a rearrangement of that pick: push it or move it down the ladder.
Expandable rows or an accordion added to a pick's table are rung 4, not 7. A crossover's rung is measured from
its closest parent: lay it over each parent and take the smaller change. Each option records its `role`
(iteration.md §3).

## 8. Checks

Before building, and again after:

- [ ] Options ordered by rung, a→j.
- [ ] Each option's rung matches the deepest plane its built prototype touches, recorded in `plane`, and passes
      that rung's test; none relabelled to fill a slot, and an uneven row is said in the `degraded` line.
- [ ] Every band present (unless a shift or the user's words removed one on purpose, and the summary says so).
- [ ] At least one option at rung 3 or below and one at rung 9 or above (default rounds).
- [ ] No two options share a rung and a primary axis; a primary axis leading twice has a reason in the
      `degraded` line (variation-axes.md §3).
- [ ] A brief that complains about the look has a rung-2 restyle among the options.
- [ ] Each option's cost line names what users must relearn (rungs 4 and up) or what they lose (rungs 1–3:
      emphasis, density, height). New designs name what a first-time user must learn instead.
- [ ] Rungs 9 and 10 carry a function mapping and a working switch-back, recorded in `switch_back`.
- [ ] Fact-led new designs show the core facts, or one click to them, on the first screen.
- [ ] In default and closer rounds the lowest option looks like today on its best day; in every round the highest
  makes someone stop and think.
- [ ] In later rounds, no Rethink or Reinvent option keeps a basis pick's skeleton.
- [ ] Every option passes the contract, whatever its rung.
- [ ] Each Rethink and Reinvent option shows its payoff in the first five seconds of using it.

`dv.py check` enforces ordering, band coverage and the rung–axis rule for explore and more rounds. It errors when
a rung sits outside its recorded `plane` and, in the newest round, when a redesign option at rung 9–10 has no
`switch_back`; it notes a primary axis that leads twice with no `degraded` line. Whether the plane is right is
your call.
