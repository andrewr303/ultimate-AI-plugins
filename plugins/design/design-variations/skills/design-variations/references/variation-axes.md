# Variation axes

Read this at step 3 when assigning each option its primary axis, and whenever two options look alike. An axis
is a dimension a design can move along. Each option owns one **primary axis position**, plus at most two
secondary axes that follow from it. By default no primary axis leads twice in a round (§3). That way the user
learns what made an option good, and the ten really are ten answers.

## Contents

1. The axes
2. Which axes suit which band
3. Diversity rules for ten
4. Coherent bundles and mood presets
5. Recording axes

## 1. The axes

Sixteen axes, each with the plane it lives on (spectrum-ladder.md, placing an option). The deeper the plane, the
more users relearn when it moves. The first column is the exact ID the ledger records.

Cost tags: **R** relearning (what existing users must relearn; resistance to change), **B** build effort, **A**
accessibility risk, **D** brand or theme drift. Untagged phrases are other costs to state.

| Axis | Plane | What it decides | Positions | Costs |
|---|---|---|---|---|
| `layout-paradigm` | Structure | The arrangement of the whole surface | single column · list–detail · supporting pane · feed or grid · table · board · timeline or calendar · canvas or map · hub or launcher · document · dashboard of panels · wizard | R high (spatial memory) · B high (each paradigm needs its own responsive rules) · content that fits the paradigm badly |
| `information-architecture` | Structure | How content is chunked, ordered, grouped and nested | by object · task · status · time · owner · priority · place; flat ↔ nested (two levels at most); grouped by proximity, shared background, dividers or headings | R high (landmarks, mental model) · A medium (heading order) · findability of moved items |
| `density` | Skeleton | Items and whitespace per view, as one whole ramp | spacious · comfortable · compact · dense | A (touch targets, readability when dense) · fewer items and more scrolling when spacious · harder for novices when compact |
| `visual-hierarchy` | Skeleton and surface | What wins attention, and by how much | subtle · balanced · strong · dramatic; one focal point · distributed · progressive reveal; what leads: the key number, next action, newest item, exception, person | Demoted items get slower to reach · everything loud means nothing is · R low to medium |
| `typography` | Surface | Type voice, scale, weight ramp and line length | productive ↔ expressive; neutral sans · humanist · geometric · grotesk · serif · slab · mono · display; flat ↔ dramatic scale; numeral style | D (brand drift if families change) · B (font loading) · expressive type distracts inside a product |
| `colour-stance` | Surface | How much of the surface colour carries, and in which roles | monochrome · restrained (tinted neutrals, one accent) · tonal · committed (one colour carries a large share) · full palette (three or four roles) · drenched; light or dark from the use scene | A (contrast; meaning carried by colour alone) · D (theme drift) · clashes with status colours |
| `shape-and-depth` | Surface | Corner personality and how surfaces separate, as one set | radius sharp · soft · pill; separation flat or hairline · subtle · layered · lifted; by border, shadow, tone or space | A (fully flat loses signs of what is clickable) · mixed sets read as broken · every card looking alike |
| `imagery-and-icons` | Surface and skeleton | Pictures and the icon system | none · icon with label · icon only · illustration · photography · avatars · data as image; icon fill, weight and style | Removing text labels has measurably hurt usability · B (asset cost) · decoration without information |
| `motion` | Surface | How much things move, and with what character | still · calm (productive) · lively · energetic (expressive); one orchestrated moment or per element | A (reduced-motion users) · performance · distraction |
| `interaction-model` | Structure | How the core task is performed | form and submit · inline edit · direct manipulation (drag) · modal edit · side-panel edit · wizard · command-first · keyboard-first · conversational · batch or instant · suggestions · proactive queue · automated with review | R high (muscle memory) · hidden saves · keyboard parity · trust and control when automated |
| `navigation-model` | Skeleton (structure at app scale) | How people move between areas and subsets | top bar · tabs · bottom tab bar · sidebar · rail · drawer · hub · breadcrumbs and drill-down · command palette · in-content links; where filters and global actions live | R high (habit) · discoverability (drawers, palettes) · width |
| `content-and-voice` | Skeleton | What the words say, and how | formal ↔ casual · serious ↔ funny · respectful ↔ irreverent · matter-of-fact ↔ enthusiastic; terse labels ↔ guided sentences; instructions inline ↔ on demand | Translated length · D (voice drift) · wordiness |
| `progressive-disclosure` | Structure | What is visible up front, what is deferred, and how deep | all visible · primary plus "more" · staged wizard · one thing per page · task-list hub · on-demand overlay (drawer, modal, popover) · inline expansion; two levels at most | Hidden features get used less · extra steps · getting lost · context lost in overlays |
| `data-representation` | Skeleton | The form data takes | table · list · cards · chart chosen by relationship (change over time, ranking, part-to-whole, distribution, deviation, correlation, flow, place) · map · timeline · stat tile · sparkline; lean ↔ annotated | Cards lose comparison · precision or glance · charts that decorate rather than inform |
| `input-and-controls` | Skeleton | Which controls and inputs collect choices | pointer · touch · keyboard · voice · pen; radio · segmented · select · combobox · chips · slider · stepper · calendar · typed with parsing | A (control accessibility) · platform conventions |
| `automation-and-guidance` | Scope | How much the product does or suggests for the user | manual · suggestions · smart defaults · proactive queue ("what needs you") · automated with review | Trust and explainability · R (users must learn what it does for them) · manual control must stay reachable |
| `feedback-and-state` | Skeleton | How the system reports state, least to most interruptive | inline · toast · banner · panel · modal; loading skeleton · spinner · optimistic; empty: text · illustration · starter content | Interruptions · A (focus stolen) · optimistic updates need conflict handling |

## 2. Which axes suit which band

An axis leads at the rungs that match its plane:

| Plane | Axes | Leads at rungs |
|---|---|---|
| Surface | `typography`, `colour-stance`, `shape-and-depth`, `imagery-and-icons`, `motion` (and `visual-hierarchy` by weight, size and colour alone) | 1–3 |
| Skeleton | `density`, `visual-hierarchy`, `content-and-voice`, `navigation-model` (placement), `data-representation`, `input-and-controls`, `feedback-and-state` | 3–5 |
| Structure | `layout-paradigm`, `information-architecture`, `interaction-model`, `progressive-disclosure`, `navigation-model` (at app scale) | 6–8 |
| Scope and strategy | `automation-and-guidance`, or a new metaphor or job framing carried by a structure axis, or by `data-representation` when the idea is a new form (a map, a matrix, a timeline) | 9–10 |

| Band | Primary axes that fit | Avoid as primary |
|---|---|---|
| Refine (1–3) | Surface axes at rungs 1–2; `visual-hierarchy`, `density`, `content-and-voice` at rung 3 | `layout-paradigm`, `interaction-model`, `information-architecture` |
| Evolve (4–6) | `input-and-controls`, `feedback-and-state`, or `data-representation` for one region (rung 4); `navigation-model`, or `visual-hierarchy` when a summary or key action moves to lead (rung 5); `interaction-model`, `progressive-disclosure` (rung 6) | A new paradigm or organising idea |
| Rethink (7–8) | `layout-paradigm` (rung 7); `information-architecture`, `navigation-model` or `progressive-disclosure` at page or app scale (rung 8) | Pure styling |
| Reinvent (9–10) | The axis that carries the new idea: `automation-and-guidance`, `information-architecture`, `interaction-model`, `layout-paradigm`, or `data-representation` for a new form; rung 10 adds secondary axes on two other planes | Anything that only restyles or only moves regions |

For new designs the ladder measures distance from convention, not depth of change, so any axis may lead at any
rung; the plane table is a guide to how unfamiliar a move will feel.

## 3. Diversity rules for ten

- **One axis rule.** By default no primary axis leads twice in a round. When two options must share one (two
  options on one rung in a `bolder` row, or a like round's push and crossover both carrying a pick's
  interaction), they need different paradigms, and a one-line reason goes in the round's `degraded` line and the
  reply. Two options never share both rung and primary axis. `dv.py check` errors on a shared rung and axis in
  explore and more rounds (a warning in other rounds),
  warns when a repeated axis also repeats the paradigm, and notes a repeat with no `degraded` line. Refine
  rounds are exempt: every option varies one pick.
- Never pick a less fitting axis ID to dodge the rule. An honest repeat with its reason beats a stretched label,
  because later rounds read the axis to know what led.
- The rung says how deep a change goes; the axis says what leads it. A rung's name in spectrum-ladder.md describes
  typical moves, not a required axis, so two rung-7 options may lead on different axes.
- One primary axis per option, with a stated position ("density: compact"), and at most two secondary axes.
- No two options share both the same pattern entry (pattern-alternatives.md, recorded in `paradigm`) and the
  same primary axis.
- At least six different primary axes across ten options.
- At least three different layout paradigms across the round (Refine options count as today's paradigm).
- **Shared-traits cap:** two options at rung 7 or above may share at most one of page skeleton, main visual
  device, core interaction and memorable moment. Record them in the option's `traits` (`skeleton`, `device`,
  `interaction`, `moment`), describing the whole option, including the screen after its core choice: a quiz
  whose result is another option's layout shares that option's skeleton. `dv.py check` warns when two options
  share more than one trait with the same wording (ignoring case and spacing), so name each trait plainly and
  use the same phrase for the same thing.
- Secondary changes must follow from the primary ("compact density brings a smaller type step") and never
  become a second, independent idea.
- Shape and depth, and density, move as whole sets. A new radius applies to every surface and control, with
  elevation to match; a density step changes rows, controls, padding and pagination together. Sharp cards with
  pill buttons, or one compact table in a spacious page, read as broken.
- Mood words ("premium", "playful", "calm") are presets over several axes (section 4), never one axis. Record
  the axis that leads, not the mood.
- Expressive positions on `typography` and `motion` get a familiarity check. Expressive styles can help people
  spot key elements faster, but they have hurt usability where they replaced familiar list patterns or removed
  text labels. Keep familiar patterns and labels in place, and keep a calm option elsewhere in the round.
- In an existing product, visual-language axes stay inside the brand's tokens unless the user lifted that.
  What varies most is structure, hierarchy, density and interaction.
- When two options look alike after building, redraw one against an explicit ban ("no cards", "no split view",
  "type only") rather than nudging colours.

## 4. Coherent bundles and mood presets

**Mood presets.** A mood word is shorthand for positions on several axes. Use these when the brief or a steer
word names a mood (iteration.md, steer glossary, uses the same moves). Inside an existing product, apply them
with the brand's own families and tokens.

| Mood | Positions |
|---|---|
| Premium | `density` spacious · `colour-stance` restrained or monochrome · `shape-and-depth` sharp, flat or subtle · `motion` calm · `typography` refined, a high-contrast display face where the brand has one · precise alignment |
| Playful | `shape-and-depth` pill or soft · `colour-stance` committed or full palette · `motion` lively to energetic · `typography` rounded sans · `imagery-and-icons` illustration · `content-and-voice` casual |
| Pro | `density` compact or dense · `typography` productive, tabular figures · `shape-and-depth` sharp with hairlines · `colour-stance` restrained, semantic colour only · `motion` calm and quick · `input-and-controls` keyboard-first |
| Calm | `visual-hierarchy` one focal point, subtle elsewhere · `colour-stance` restrained · `density` comfortable to spacious · `motion` still or calm · `feedback-and-state` inline, rarely interruptive |
| Editorial | `typography` expressive, dramatic scale · `density` spacious · `shape-and-depth` few containers, rules instead of cards · `imagery-and-icons` photography or type only · `visual-hierarchy` dramatic |
| Bold | `visual-hierarchy` dramatic · `colour-stance` committed · `typography` large scale contrast · fewer, larger elements |
| Friendly | `content-and-voice` casual and explanatory · `shape-and-depth` soft · `colour-stance` tonal · `imagery-and-icons` illustration or avatars · `motion` calm to lively |
| Simple | `progressive-disclosure` primary plus "more" · one primary action · fewer visible controls · `content-and-voice` terse |

**Structural bundles.** Bold options often move a structural primary axis and pull a few others with it. These
hang together:

| Bundle | Primary | Pulls along |
|---|---|---|
| Expert cockpit | `density`: compact | Keyboard-first interaction, command palette, inline editing, small type step, hairline separation |
| Calm focus | `progressive-disclosure`: summary first | Spacious density, one focal number, quiet colour, details in a side panel |
| Workbench | `layout-paradigm`: list–detail | Persistent selection, inline actions in the detail, keyboard movement between items |
| Triage inbox | `information-architecture`: by what needs action | Queue ordering, one-key actions, done state, undo, counts per bucket |
| Timeline | `information-architecture`: by time | Date scrubbing, grouping by period, a "today" anchor, forecast area |
| Board | `layout-paradigm`: columns by state | Drag between states with a keyboard alternative, card summaries, counts per column, quick add |
| Conversational | `interaction-model`: ask and answer | Suggested prompts, results as cards with actions, the full list one step away |
| Proactive assistant | `interaction-model`: suggestions | A "do these now" strip, explanations, one-click accept, manual control always present |

Combinations that clash: dramatic editorial type with dense expert layouts; drag-first interaction on a
phone-first surface without a keyboard alternative; colour-blocked regions with an already colour-heavy status
system; sharp containers with pill controls.

## 5. Recording axes

In the plan table and the ledger, every option records:

- `axis`: one ID from section 1, written exactly: `layout-paradigm`, `information-architecture`, `density`,
  `visual-hierarchy`, `typography`, `colour-stance`, `shape-and-depth`, `imagery-and-icons`, `motion`,
  `interaction-model`, `navigation-model`, `content-and-voice`, `progressive-disclosure`,
  `data-representation`, `input-and-controls`, `feedback-and-state`, `automation-and-guidance`;
- its position in words, inside `idea` or `description`;
- `secondary_axes`: up to two more IDs from the same list;
- `paradigm`: the pattern entry from pattern-alternatives.md;
- for redesigns, `plane`: the deepest plane the built option touches (spectrum-ladder.md §2);
- at rung 7 and above, `traits` (§3, shared-traits cap);
- for new designs, `direction` (aesthetic-directions.md).

Later rounds read these to avoid re-offering used corners (iteration.md §4) and to push picked options further
along their own axis. `dv.py check` and `dv.py novelty` compare axis IDs as exact text, so never invent a
synonym.

Ledgers written before these IDs may use older axis names. Read them as: content priority →
`visual-hierarchy`; flow shape → `progressive-disclosure` (or `interaction-model` for a wizard); automation and
guidance → `automation-and-guidance`; navigation and chrome → `navigation-model`; imagery and data form →
`imagery-and-icons` or `data-representation`; motion and feedback → `motion` or `feedback-and-state`; structure
→ `layout-paradigm`; visual language → the surface axis it mainly moved.
