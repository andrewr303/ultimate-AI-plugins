# Pattern alternatives by archetype

Read this at step 3 when filling the Evolve, Rethink and Reinvent slots, and in `more` rounds when you need
directions not yet shown. Each archetype lists ten to twelve structurally different ways to do the same job,
roughly from familiar to unusual, each with its trade-off. They are starting points to adapt to the product, not
recipes to paste; every one must still pass the contract. "Using this catalog" at the end says how to choose.

## Contents

1. Data tables and lists
2. Cards
3. Dashboards and overviews
4. Forms and data entry
5. Navigation and app shell
6. Search and filtering
7. Pickers and selectors
8. Dialogs, sheets and overlays
9. Empty, loading and error states
10. Onboarding and first run
11. Pricing and plans
12. Landing page hero and marketing sections
13. Settings and preferences
14. Calendar and scheduling
15. Chat and assistant panels
16. Detail, profile and record pages
17. Checkout and payment
18. Notifications, inbox and activity
19. File upload and media
20. Editors, canvases and toolbars
21. People, roles and permissions

## 1. Data tables and lists

- **Refined dense table** (sticky header, frozen first column, aligned numerals): best for comparison; weak on narrow screens and at showing what matters.
- **Table with a side detail panel** (list–detail): rows stay visible while editing; halves the table's width.
- **Expandable rows**: detail in place; open rows pile up and lengthen the page.
- **Grouped sections with totals** (by status, date or owner), collapsible: structure at a glance; one grouping at a time, collapsed items hidden.
- **Two-line compact rows** (title, then a metadata line): scans well on phones; fewer attributes, weaker sorting.
- **List with full-page detail** (drill in): simplest; loses the list's context.
- **Editable grid** (spreadsheet-style): fastest bulk edits; save behaviour and validation need care, and undo.
- **Card grid**: browsing mixed items; poor for scanning and comparing, fewer per screen.
- **Board by status, drag to move**: flow and bottlenecks visible; few fields per card.
- **Timeline or Gantt rows**: time relations obvious; every row needs dates.
- **Summary first** (aggregates and outliers on top, drill down to records): shows what matters; an extra step to the records.
- **Triage queue** (one item at a time, keyboard actions): fast processing; poor overview.
- *Sub-choices:* paging (pages, load more, endless scroll); bulk actions through checkbox selection, not a menu on every row.

## 2. Cards

- **Vertical media card** (image on top): visual browsing; tall.
- **Horizontal card** (thumbnail left): denser lists; smaller image.
- **Text-only tile**: scannable; weak visual hook.
- **Stat tile**: glanceable; a cliché when it decorates rather than informs.
- **Card with inline quick actions**: fast; clutter and mis-taps.
- **Expandable card** (details in place): no navigation; layout shifts.
- **Selectable choice card** (visual picker): big targets; space.
- **Bento mosaic** (mixed sizes): hierarchy by size; uneven scanning.
- **Swipeable stack** (one at a time): focus; no overview.
- **No card at all** (a plain list row): better scanning; weaker grouping.

## 3. Dashboards and overviews

- **KPI strip plus chart grid**: glance, then detail; the most generic, often everything shouts equally.
- **Single hero metric or one-question chart with annotations**: clear focus; other metrics demoted.
- **Comparison view** (this period against last, segment against segment): shows change; needs two baselines.
- **Table first with inline sparklines**: dense comparison; tiny charts.
- **"What needs you" action list first, metrics second**: drives action; less analytical.
- **Goals and pacing** (targets, progress): motivating; needs targets to exist.
- **Exception-only view** (only anomalies shown): quiet when healthy; needs trusted rules.
- **Operational status wall** (live, with thresholds): time-critical monitoring; little depth.
- **Analytical workspace** (filters and linked views): exploration; complex.
- **Narrative report** (sentences with live numbers): readable for non-experts; slower to scan precisely.
- **User-arranged widget board**: personal; empty or messy by default.
- **Assistant summary with drill-down to the evidence**: fast insight; verification must be easy.
- *Charts:* choose by the relationship shown (change over time, ranking, part-to-whole …); position and length read more accurately than angle or area, so avoid gauges and 3D.

## 4. Forms and data entry

- **One long page, grouped sections**: full overview; intimidating when long.
- **Accordion sections on one page**: progressive; people treat sections as steps and expect Back to work.
- **Multi-step wizard with progress**: chunks the work; poor when steps depend on each other, harder to review.
- **One question per page** (a common public-service default): focused and accessible; more steps.
- **Task-list hub** (sections in any order, across sessions): long or multi-session work; overhead for short forms.
- **Side sheet beside the list**: context kept; cramped.
- **Modal form**: short, focused tasks; hides the information people refer to.
- **Read view with inline editing**: edit in context; save behaviour must be visible; weak for creating records.
- **Progressive form** (fields appear as earlier answers make them relevant): short for most people; can surprise.
- **Smart defaults, then a review page with Change links**: fastest when defaults are right; unchecked errors slip through.
- **Natural-language entry parsed into fields** ("£480 to Atlas, due Friday"): very fast for experts; needs clear parse feedback.
- **Conversational, one prompt at a time**: friendly; slow for experts, hard to review.

## 5. Navigation and app shell

- **Labelled left sidebar with groups**: scales; costs width.
- **Top bar with tabs**: familiar; few items.
- **Bottom tab bar** (phones): always visible; five items at most.
- **Icon rail that expands to labels**: saves width; icons are ambiguous.
- **Top sections plus a contextual left sub-navigation**: deep structures; two systems to learn.
- **Drawer behind a menu button**: many items in little space; less discoverable.
- **Mega menu**: exposes a wide structure; hover and touch pitfalls.
- **Hub or launcher home with tiles**: clear start; an extra hop to everything.
- **Breadcrumbs and drill-down only**: strong hierarchy; slow sideways moves.
- **Workspace switcher plus open-item tabs** (browser-like): multitasking; tab management.
- **Search-first shell** (one search box leads): reaches everything; heavy on empty states.
- **Command palette as primary navigation**: keyboard speed; must be learned, low discoverability.

## 6. Search and filtering

- **Filter bar of chips or popovers**: the familiar default; crowds with many filters.
- **Segmented control for the main dimension**: instant; one dimension only.
- **Left facet rail with counts**: powerful; costs width.
- **Filter bar plus a "More filters" side panel**: common filters fast; rare ones hidden.
- **Filter sheet with a batch Apply** (phones): saves space; filters hidden, results update late.
- **Saved views or smart lists** ("Late by more than a day"): fast repeat questions; setup cost.
- **"Add filter" builder**: precise combinations; more clicks for simple cases.
- **Search first, with query, scope and rich suggestions**: fast for known items; weak for browsing.
- **Filter by example** (click a value to filter by it): discoverable in context; hard to combine.
- **Token query bar** ("status:delayed carrier:north"): precise and shareable; learning curve.
- **Natural-language search showing how it was read**: approachable; precision and trust.
- *Sub-choice:* apply filters instantly, or in a batch with an Apply button.

## 7. Pickers and selectors

- **Radio group or radio cards**: all options visible; few options only.
- **Segmented control**: two to five compact choices; short labels only.
- **Native select**: reliable on phones and in long forms; hides options, no filtering.
- **Combobox with typeahead and recent items**: long or open lists; people must know the names.
- **Multi-select with chips**: several values; chips overflow.
- **Anchored popover with a ranked list and preview**: keeps context; small area.
- **Visual tiles or swatches**: rich or visual options; space, poor for text.
- **Tree or cascading menu**: hierarchical options; depth.
- **Full-screen sheet** (phones): big targets; context lost.
- **Slider or stepper**: continuous values; imprecise.
- **Typed entry with parsing** (dates, amounts): fastest for distant or exact values; needs clear feedback.
- **Best-fit suggestions first, then the rest**: saves time; must explain why.

## 8. Dialogs, sheets and overlays

- **Centred modal**: critical decisions; blocks context; one at a time.
- **Alert or confirmation**: irreversible actions; fatigue when overused.
- **Non-modal side panel**: keeps context visible; narrow.
- **Anchored popover**: small contextual edits; tiny.
- **Inline expansion in the page**: no overlay; layout shifts.
- **Bottom sheet with drag heights** (phones): peek and expand; gesture conflicts.
- **Separate page or route**: room for substantial work; context lost.
- **Full-screen takeover**: distinct multi-step tasks; context lost.
- **Floating non-modal window** (compose-style): work alongside; window management.
- **Undo toast instead of a confirmation**: no friction; the action must be truly reversible.

## 9. Empty, loading and error states

- **Short title and one primary action**: clear; can feel bare.
- **Illustration and action**: warmth; upkeep, and decoration if it says nothing.
- **Inline explanation of the feature**: helps first use; takes space.
- **Starter or sample content**: explore without risk; must be removable.
- **Import or connect prompt**: gets real data in fast; integration work.
- **Setup checklist**: momentum; nags.
- **Ghost preview of the filled state**: sets expectations; can look broken.
- **No-results repair** (suggest terms, clear filters): recovers searches; needs good suggestions.
- **Error or permission state with the cause in plain words and a way out**: recoverable; needs precise errors, and no jokes.
- **Skeleton loading that matches the final layout**: feels faster; must match exactly.
- **Optimistic display with background sync**: feels instant; needs conflict handling.
- **Partial content with the failed part isolated**: keeps working; more states to design.

## 10. Onboarding and first run

- **No tour: a usable interface with contextual tips**: the preferred default; relies on clear design.
- **Single most important action first, the rest later**: focus; slower full setup.
- **Coach marks over the interface**: quick hints; dismissed and forgotten.
- **Interactive walkthrough** (learn by doing in the real product): suits complex workflows; hints can annoy.
- **Persistent setup checklist**: progress visible; clutter.
- **Personalisation questions that shape the defaults**: relevant start; more questions.
- **Sample workspace with realistic data**: immediate understanding; cleanup needed.
- **Empty-state-led onboarding** (each empty screen teaches its feature): learning at the point of need; slower full picture.
- **Multi-step setup wizard**: thorough; drop-off risk.
- **Intro card carousel**: often skipped and strains memory; rarely the right choice.
- **Assistant-guided first run**: friendly; depends on the assistant.

## 11. Pricing and plans

- **Three or four plan cards, one recommended**: familiar; anchoring can feel pushy.
- **Billing-period toggle above the plans**: compact; hides one view, easy to make manipulative.
- **Comparison grid** (many plans or heavy comparison): precise; heavy.
- **Cards per audience** ("for individuals", "for studios"): self-identification; overlap.
- **Single plan with add-ons**: simple; little tiering.
- **Price-first minimal list**: fast; little persuasion.
- **Usage calculator or slider**: honest for variable use; effort.
- **"Which plan fits" questions**: personal; extra steps.
- **FAQ-led** (objections answered beside the plans): reassuring; long.
- **Story-led long page with plans woven in**: persuasive; slower to the price.
- **Self-serve plans beside "talk to sales"**: suits high-touch deals; opaque.
- **In-product upgrade moments instead of a pricing page**: contextual; scattered.

## 12. Landing page hero and marketing sections

- **Headline, subhead, call to action and product image**: clear; the most generic.
- **Proof first** (real customers, real usage): trust; the proof must be real.
- **Full-bleed photo or video with overlay copy**: emotion; contrast and page weight.
- **Product interface as the hero, scroll-driven**: tangible; performance.
- **Live interactive demo as the hero**: proves value; build effort and weight.
- **Input-first hero** (start the task right there): action; less story.
- **Use-case selector** ("I'm a…") that changes the page: relevant; more content to write.
- **Long-form typographic opening**: voice; slower to the call to action.
- **Editorial magazine layout**: distinctive; content-heavy.
- **Comparison against the old way**: persuasive; can feel negative.
- **Kinetic type hero**: memorable; needs a reduced-motion version.
- **The most characteristic thing of the subject's world first**: distinctive; needs real material.

## 13. Settings and preferences

- **Two-pane category list and detail**: familiar on large screens; deep trees.
- **Single scroll with section anchors**: everything findable; long.
- **Top tabs per category**: suits few categories; overflows.
- **Overview with subscreens** (long lists split into subscreens): scales; extra taps.
- **Category card hub with summaries and Edit**: overview; extra click.
- **Searchable settings with deep links**: fast for known settings; poor browsing.
- **Contextual settings beside the feature they affect**: discoverable; scattered.
- **Inline toggles with immediate save and undo**: fast; risky for sensitive settings.
- **Profiles or presets** ("Focus", "Detailed"): quick switching; less control.
- **Setup wizard for complex configuration**: guided the first time; slow to change one thing later.
- **Natural-language or command settings**: speed; trust.
- *Sub-choice:* save automatically, or through an explicit save bar.

## 14. Calendar and scheduling

- **Month grid**: overview; little detail.
- **Week time-grid**: precise scheduling; dense.
- **Agenda list**: compact chronology; gaps invisible.
- **Day timeline**: focus; no overview.
- **Week strip plus a focused day**: overview and detail; two zones.
- **Day columns stacking items in order** (a board by day): planning; weak time precision.
- **Resource timeline** (people or rooms as rows): shows capacity and overlaps; wide.
- **Available-slot list**: quick booking among a few valid choices; little context.
- **Capacity view** (filled against available): planning; abstract.
- **Backlog tray, drag onto days**: direct planning; needs a keyboard alternative.
- **Natural-language quick add**: speed; parse errors.
- **Suggested schedule to accept or adjust**: fast; must explain its choices.
- *Date entry:* a calendar for near dates, typed entry for distant ones; avoid separate day, month and year dropdowns.

## 15. Chat and assistant panels

- **Side panel docked beside the work**: keeps context; narrow.
- **Full-page assistant**: focus; context lost.
- **Floating launcher bubble**: unobtrusive; covers content, easy to ignore.
- **Suggestion chips and quick actions**: guided; limited.
- **Embedded on one item** (select, then act): contextual; one item at a time.
- **Assistant inside the command bar** ("ask or do"): fast; low discoverability.
- **Inline suggestions as ghost text**: fast to accept; easy to accept blindly.
- **Results as structured cards with actions**: actionable; less conversational.
- **Chat beside an output canvas** (inputs, outputs and history together): iterative work; width.
- **Proposal and diff** (assistant proposes, user approves): trust and control; extra review.
- **Task interface with knobs and presets, no chat**: precise and repeatable; less open-ended.
- **Proactive contextual nudges**: timely; interruptive when wrong.

## 16. Detail, profile and record pages

- **Header summary plus tabs**: familiar; tab content hidden.
- **Main column plus a metadata sidebar**: dense; width.
- **Single scroll with sticky section navigation**: everything visible; long.
- **Summary with expand-all**: short by default; detail hidden.
- **Side panel over the list**: context kept; narrow.
- **Action-led** (next steps on top, facts below): drives work; less reference value.
- **Editable in place with change history**: efficient; needs undo and an audit trail.
- **Activity-centred** (history is the page): the record's story; facts buried.
- **Profile as a dashboard** (tiles and charts): glanceable; shallow, easily decorative.
- **Reorderable section cards** (bento): visual overview; generic, uneven density.
- **Comparison with peers or the previous version**: insight; extra data.

## 17. Checkout and payment

- **Multi-step** (details, delivery, payment, review): clear; more clicks.
- **One page**: quick to scan; not a cure-all, can feel long.
- **Accordion sections**: read as steps; Back must work.
- **Side summary that updates live**: confidence; space.
- **Guest checkout first, account optional**: fewer drop-offs; weaker retention.
- **Express payment first, form as fallback**: quick for most; less for the rest.
- **Review then pay** (summary with Change links): fewer mistakes; an extra screen.
- **One field group per screen** (phones): focus; more taps.
- **Slide-over cart checkout**: keeps context; cramped.
- **Buy on the product page**: fastest; a complex page.
- **Saved details, one-click confirm**: fastest for returning customers; only for them, and needs trust.

## 18. Notifications, inbox and activity

- **Inline message where it happened**: relevant, non-disruptive; scattered.
- **Badges and counters on navigation**: ambient; can cause anxiety.
- **Toast**: light confirmation; easily missed, never the only copy of something important.
- **Page or system banner**: persistent; takes space.
- **Notification panel behind a bell**: opened when wanted; easy to ignore.
- **Chronological list with read and unread**: familiar; noisy.
- **Grouped by source or type, or a digest by object and time**: less noise; recency and speed suffer.
- **Priority lane** (important first): focus; needs good rules.
- **Full inbox with triage** (done, snooze, archive): inbox-zero control; effort.
- **Activity feed with filters**: awareness; passive, noisy.
- **Actionable notification** (approve in place): fast; risky for big decisions.
- **Modal for critical alerts only**: cannot be missed; most interruptive.

## 19. File upload and media

- **Button plus a file list**: suits forms; static.
- **Drop zone with a browse button**: familiar; takes space.
- **Inline upload inside the list** (the row appears immediately): context; less guidance.
- **Thumbnail grid with per-file progress**: suits media; busy.
- **Background queue tray with retry**: robust; busy.
- **Drop anywhere** (full-page overlay): fast once known; hidden.
- **Paste from the clipboard or a link**: fast for power users; hidden.
- **Connected-service picker**: fast for cloud users; integrations to build.
- **Camera or scan first** (phones): natural on phones; weak on desktop.
- **Single-file replace with crop** (avatars): focused; one file only.
- **Gallery first, drag to reorder**: visual; poor for documents.
- *Avoid* multi-file uploads inside a modal.

## 20. Editors, canvases and toolbars

- **Fixed top toolbar, three groups at most**: discoverable; costs space.
- **Tool palette left, inspector right**: the design-tool standard; width.
- **Floating toolbar on selection**: in place; covers content, hidden until something is selected.
- **Right-click menu**: power; hidden.
- **Slash or insert menu in the content**: fast; must be learned.
- **Command palette**: keyboard speed; discoverability.
- **Keyboard-first with a cheat sheet**: expert speed; a barrier for novices.
- **Bottom floating dock**: content first; covers the canvas edge.
- **Mode-based tool sets** (edit, preview, comment): clarity; mode errors and switching cost.
- **Focus mode** (toolbars hidden, reliable restore): concentration; tools out of sight.
- **Radial menu**: quick once learned; unusual.

## 21. People, roles and permissions

- **Members table with a role column**: familiar; what a role allows stays hidden.
- **Grouped by role with counts**: structure; finding a person relies on search.
- **People list plus person detail**: rich per-person view; width.
- **Invite-first flow with seat usage**: growth focus; less management.
- **Bulk edit through a select mode**: fast for many changes; risky without preview and undo.
- **Role cards that say what each role can do, members inside**: understandable; less dense.
- **Permission editor on each resource** (a share dialog on the item): contextual; no overall view.
- **Teams or groups as the unit** (people inherit access): scales; "why does she have access?" gets harder.
- **Access matrix** (people against resources): the full picture; wide.
- **Access review queue** (what needs attention): security focus; browsing one step away.
- **Audit timeline of changes**: accountability; secondary for daily work.

## Using this catalog

- Pick one entry per option as its primary move, adapted to the product's tokens, copy and data; the entry's
  trade-off seeds the option's cost line. Decide an archetype's sub-choices on purpose and say which one it uses.
- Low rungs (1–6) stay close to today's entry in the same archetype: a dense table becomes a table with a side
  panel or grouped sections, not a board. Rungs 7 and above may cross to a different paradigm (a table becomes a
  board or a calendar); Reinvent slots may also look one archetype over: a shipments list can borrow from an
  inbox (18), a calendar (14) or a triage queue (1).
- Record the entry's name in the option's `paradigm`, so later rounds can see what has been shown and no two
  options share both an entry and a primary axis (variation-axes.md, diversity rules).
