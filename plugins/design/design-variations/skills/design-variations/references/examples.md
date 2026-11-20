# Worked examples

Read this when you want to see a whole round end to end: the plan, the reply and an iteration. The examples
are compact; real rounds also carry the reference board, the contract and the built prototypes.

## Contents

1. Redesign: the Members page of a settings area (round 1)
2. New design: a booking page for a bike repair shop (round 1)
3. Iteration: evolving picks and a merge (rounds 2 and 3)

## 1. Redesign: the Members page of a settings area (round 1)

**Intake line:** "Redesign of Fieldnote's Members settings page (src/settings/Members.tsx). Output: a new HTML
gallery in design-variations/team-members/, original untouched. Ten options at 1280×800, light theme."

**Inventory line:** "Inspiration: Gummble · Design context: none (read from code) · Not connected: Mobbin."

**Contract (short):** see every member with name, email, role and last active date; search; filter by role;
invite by email with role; change role (last owner protected); remove with confirmation; resend or revoke
invites; seat usage; Fieldnote brand.

**Round question:** How should admins see and manage who has access?

**Plan:**

| ID | Name | Rung · band · plane | Primary axis | Big idea | Cost |
|---|---|---|---|---|---|
| 1a | Calmer roster | 1 Polish · Refine · surface | `visual-hierarchy` | Quieter borders, stronger name column | Fixes little beyond scanning |
| 1b | Tinted role labels | 2 Restyle in system · Refine · surface | `colour-stance` | Roles as quiet tinted labels; indigo kept for Invite only | More colour on a calm page, and the words, not the colour, must tell roles apart |
| 1c | Role-first rows | 3 Hierarchy and density · Refine · skeleton | `density` | Name and role on one line, email beneath; more people per screen | Long emails truncate sooner |
| 1d | Inline role picker | 4 Component swap · Evolve · skeleton | `input-and-controls` | Change roles in the row, with undo, instead of the Edit dialog | Admins relearn where roles change |
| 1e | Filter rail | 5 Region re-layout · Evolve · skeleton | `navigation-model` | Search, role filters with counts and seat usage move to a left rail | Filters move from above the table to the left; the table loses width |
| 1f | Keyboard roster | 6 Interaction model change · Evolve · structure | `interaction-model` | A command bar handles invite, role change and removal | A new habit to learn; gains mostly for frequent admins |
| 1g | People and detail | 7 Layout paradigm shift · Rethink · structure | `layout-paradigm` | List left, selected person's access right | Editing moves from the row to the panel; needs width |
| 1h | Roles first | 8 IA and navigation restructure · Rethink · structure | `information-architecture` | Opens on four role cards: what each role can do, and its people | People are found by role or search; the flat list moves to an All people view |
| 1i | Access map | 9 Reconceived experience · Reinvent · scope | `data-representation` | People × workspaces matrix, edit in cells | A new mental model; wide teams scroll sideways |
| 1j | Access review queue | 10 Radical reinvention · Reinvent · scope | `automation-and-guidance` | Leads with what needs attention, one-click fixes | Browsing the roster takes one more step |

**Traits (rungs 7–10, recorded in `traits` for the shared-traits cap):**

| ID | Skeleton | Device | Interaction | Moment |
|---|---|---|---|---|
| 1g | Narrow list beside a detail panel | A person's access and activity panel | Select a person, then edit in the panel | One person's whole access on one screen |
| 1h | Four role cards over an All people tab | Cards that say what each role can do | Browse by role, then act on a person | Seeing who holds Admin at a glance |
| 1i | People-by-workspace grid | Editable access cells | Click a cell to change access | The whole team's access in one picture |
| 1j | Attention queue over a Roster tab | Fix cards with one-click actions | Work down the queue | The queue reaching zero |

**Mappings and switch-back (rungs 9–10):** 1i: search and role filter → the map's row filter; invite → a new
row at the foot of the map; role change and removal → the person's cells and row menu; resend and revoke →
the pending rows; seat count → the map header. A List toggle switches back to today's table. 1j: every action
→ the Roster tab, which is today's table; the queue's fixes are shortcuts to the same actions. The Roster tab
is one click away, and the prototype remembers the last tab used. Each way back goes in the option's
`switch_back`.

**Checks:** ordered by rung; four bands; ten distinct primary axes; four structures beyond today's table
(master–detail, role cards, matrix, queue); after building, every option placed again by the plane test and
none moved; no two of 1g–1j share a trait; the costs of 1d–1j say what admins relearn; every option keeps all
contract items; every option read through in its declared states and filtered to one member; 1i leads with a
Gummble access-matrix reference, and 1j borrows its review-queue idea from security tools.

**Reply:**

> Ten live variations of the Members page are in `design-variations/team-members/index.html` (your original
> file is untouched). All ten use the same 24 members and 3 pending invites, and keep search, role filters,
> inviting, role changes, removal and the seat count. Emails are simulated.
>
> - 1a · Calmer roster: quieter table, names lead. Fixes little beyond scanning.
> - 1b · Tinted role labels: …
> - …
> - 1j · Access review queue: opens on what needs attention, with one-click fixes. The plain roster is one tab
>   away.
>
> Inspiration: Gummble (9 references; cited under each option). Mobbin is not connected.
>
> I'd start from 1h if admins mostly manage roles in bulk: each role's count and what it allows are obvious.
> It costs some name-finding speed. Runner-up: 1g, if admins usually work on one person at a time.
>
> Shortlist, mark "not this" and add notes in the gallery, then use Give feedback. Or reply with something
> like "like 1g and 1h, keep 1e's rail".
>
> Checked: the smoke test passed all ten at 1280 and 390, with a shot of every declared state; its squint
> heuristic flagged no look-alikes, though it compares first screens only. I read each option filtered to one
> member and to nothing, and tabbed through 1b, 1f and 1j.

## 2. New design: a booking page for a bike repair shop (round 1)

**Intake line:** "New design, open: a booking page for Spoke & Chain, a two-mechanic bike repair shop. Ten
options at 1440 wide, also checked at 390. Prices from the brief; opening hours shown as a placeholder."

**Brief:** let riders pick a service (safety check £25, full service £85, wheel true £20), see the next free
slots, and book with name, phone and bike type. Audience: commuters and weekend riders. Tone: practical,
friendly.

**Plan (directions vary because nothing exists yet; rungs measure distance from the usual booking page):**

| ID | Name | Rung · band | Primary axis | Direction: ground, type, imagery | Big idea |
|---|---|---|---|---|---|
| 1a | Service list, slots below | 1 · Proven | `visual-hierarchy` | Flat 2.0 / system-native: light grey, platform sans, line icons | The conventional three-step page played straight, done exceptionally |
| 1b | Price cards | 2 · Proven | `typography` | Swiss / International: workshop near-black, neo-grotesk, photos of each job on the bench | The convention plus one signature detail: prices set large on three service cards |
| 1c | Repair ticket | 3 · Proven | `colour-stance` | Paper and print: ticket buff, book serif with small caps, the shop's own job-ticket form | The convention laid out as the shop's own job ticket: black ink, one spot colour |
| 1d | Slots first | 4 · Fresh | `information-architecture` | Data-ink minimal: workshop-manual paper, sans with tabular figures, free slots as a bar timeline | Next free times lead; the service is chosen second |
| 1e | Workshop board | 5 · Fresh | `layout-paradigm` | Skeuomorphic tactile: pegboard brown, humanist sans on card tags, tags hung on pegs | Today and tomorrow as a pegboard of slot tags per mechanic, borrowed from staff schedulers |
| 1f | Stepper with summary | 6 · Fresh | `progressive-disclosure` | Editorial serif: white, text serif with a grotesk for controls, rules and a summary column | A wizard and a single page combined: sections open in turn beside a live booking summary |
| 1g | Diagnose first | 7 · Novel | `automation-and-guidance` | Illustrated narrative: soft green, humanist sans, drawings of worn brakes, chains and tyres | "What's wrong?" questions pick the service for you |
| 1h | Booking sentence | 8 · Novel | `content-and-voice` | Kinetic type: ink blue, variable display face, type only | The booking reads as one large sentence; each blank is a picker |
| 1i | Bike map | 9 · Experimental | `input-and-controls` | Bauhaus geometric: white with primaries, geometric sans, a bike drawn from circles and bars | Tap the part of a bike diagram that needs work |
| 1j | Drop-off planner | 10 · Experimental | `interaction-model` | Neo-brutalist: signal orange, quirky display over a clean body face, bold tool icons | Say when you can leave the bike and when you need it back; the shop fits the work in |

**Notes:** every option books a real slot (in the prototype's state), validates the phone number and shows a
confirmation. No reviews or ratings are invented, and the address is a visible [YOUR ADDRESS] placeholder. 1g,
1i and 1j each keep a plain "choose a service" link with all three prices, recorded in `switch_back`, so a
first-time visitor can always finish without learning the new idea. Any two directions differ in at least two
of ground, type and imagery; only 1a pairs a plain light ground with a neutral sans, and six (1b, 1c, 1d, 1e, 1g,
1i) draw on the workshop's own world.

## 3. Iteration: evolving picks and a merge (rounds 2 and 3)

**User:** "1g and 1h are closest. I like the role groups in 1h but want 1g's detail panel. No command bars."

**Reading line:** "Reading this as: evolve 1g and 1h, keep 1h's role groups with 1g's detail panel in mind,
and add 'no command bar' as a constraint. 1f's idea is set aside."

**Recorded:** "no command bar" joins the constraints, and 1f goes into round 2's `passed` with its `signature`:
"a command bar at the top that invites, changes roles and removes people by typing, with the list following the
keyboard".

**Round 2 (kind `like`, basis 1g and 1h), ten options ordered by distance from the picks:**

| ID | Name | From | `role` | Move |
|---|---|---|---|---|
| 2a | Tidier groups | 1h | `refine` | Sharpen 1h's role groups |
| 2b | Groups with avatars | 1h | `refine` | 1h's groups with a face for each person |
| 2c | Detail with tabs | 1g | `refine` | 1g's panel split into tabs |
| 2d | Detail as timeline | 1g | `refine` | 1g's panel as a history of access changes |
| 2e | Collapsible groups | 1h | `push` | 1h's axis further: groups fold to their counts |
| 2f | Wide detail | 1g | `push` | 1g's axis further: the panel takes most of the width |
| 2g | Groups beside detail | 1g + 1h | `crossover` | 1h's role groups as 1g's list |
| 2h | Detail drawer on groups | 1g + 1h | `crossover` | 1g's detail as a drawer over 1h |
| 2i | Person cards by role | 1g + 1h | `crossover` | 1h's role groups hold person cards that open 1g's detail in place |
| 2j | Access by workspace | none | `wildcard` | Grouping plus detail, by workspace instead of role: it breaks the recorded liking for role groups on purpose, and its `idea` says so |

The gallery shows each role on its card. `dv.py novelty` flags nothing: 2j's paradigm differs from 1i's matrix,
and no new idea or description repeats 1f's signature.

**User:** "2g, but use 2b's avatars. That's the one."

**Round 3 (kind `chosen`):** one option, 3a "Grouped people with detail", parents 2g and 2b. The summary reads
"2g's layout with 2b's avatar rows. Chosen." The reply asks whether to apply it to src/settings/Members.tsx,
and lists the files that would change.
