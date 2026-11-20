# Intake and modes

Read this at step 0 of every round: before reading code, before searching for references, before planning.
It settles what the round is about, where its output goes and whether anything must be asked.

## Contents

1. The three modes
2. Naming the subject
3. Redesign or new
4. Choosing the host
5. When to ask, and how
6. Counts, sizes and other overrides
7. Intake checklist
8. Host capabilities to check at run time

## 1. The three modes

| Mode | Trigger | Output |
|---|---|---|
| **Explore** | First request on a subject: "give me options for the shipments page", "design a pricing page", "what could onboarding look like" | Round 1: ten options across the full spread |
| **Iterate** | Any feedback on shown options: picks, "more", "combine", "bolder", notes, a sub-part to explore next | Round n+1 on top of the same variations file (iteration.md) |
| **Promote** | "Go with 3e", "apply 3e", "make 3e real" | A Chosen round marking the decision, then, on the user's explicit go-ahead, applying it to the original (iteration.md, Promotion) |

If a request mixes modes ("I like 2c, now do the header"), do them in order: record the choice as a Chosen
round, then explore the header as a scoped round that holds 2c constant.

If a variations file for this subject already exists (look for `design-variations.json`, a canvas page or
file named "… Variations", or a gallery the user links), you are iterating, or resuming (below): read its ledger
first and continue its round numbers. A built gallery carries a copy of the ledger in
`<script type="application/json" id="dv-ledger">`; when all you have is a published gallery link, read the
ledger from there. Never start a second variations file for the same subject unless asked.

**Resuming an unshown round.** A ledger whose newest round was never presented (an earlier turn ran out before
the reply, the round's `degraded` line names missing options, `dv.py check` reports missing variant files, or the
user says "continue") is not a new round. Finish it:

1. Keep the round number and every option ID already planned. Unshown options may still be fixed or replaced in
   place.
2. Retake the inspiration inventory, because connections change between turns (inspiration-mcps.md §1).
3. Re-verify every option, not only the new ones: the full pass in critique-and-presentation.md §1, including
   each option's own signature interaction ("tap a line to see what's included"), not just the flow the options
   share.
4. Build what is missing, then present the whole round as round n.

## 2. Naming the subject

Write one sentence: **what it is, where it renders, what job it does.**

> The shipments board in Freightline's web app, the page dispatchers keep open all day to spot delays and act on them.

One subject per round. "The dashboard" is a subject only if the user wants the whole dashboard rethought;
"the dashboard's revenue card" is a different, smaller subject. When the brief spans several pieces, pick the
one the others hang off, say so, and offer the others as later scoped rounds.

Frame the subject as the **whole surface the user will judge**, even when only part of it varies: a filter
bar is judged inside the page it filters. Each prototype shows the real chrome and neighbours around the part
that changes, like the user's example, where every option is the full app with only the backlog placement
changing.

## 3. Redesign or new

| Signal | Treat as | Spread | Contract |
|---|---|---|---|
| Code, a canvas artboard, a Figma frame, a screenshot or a URL of the thing exists | **Redesign** | Refine → Evolve → Rethink → Reinvent | Full preservation contract (preservation-contract.md) |
| Nothing exists, but it lives inside an existing product or platform | **New, in a theme** | Proven → Fresh → Novel → Experimental | Theme contract: the product's tokens, components, voice and navigation |
| Nothing exists and no product surrounds it | **New, open** | Proven → Fresh → Novel → Experimental | Brief only; options may explore aesthetic directions (aesthetic-directions.md) |

A "complete overhaul" or "radical redesign" request is still a redesign: keep the contract, shift the
spread toward the radical end (spectrum-ladder.md, distribution shifts). Only the user can lift contract items
("drop the stats row", "ignore our current colors").

## 4. Choosing the host

Pick the first row that applies. Tell the user in one line where the output went and why.

What counts as "a new design file": in Claude Design, new `.dc.html` files (an options document, a base copy,
option artboards) that sit beside the original, normally on their own page; the original files are never
edited. In a repository or chat, a new folder or a new HTML file. Say in the first reply which you used, and
offer a separate new canvas if the user prefers.

| Situation | Host | Read |
|---|---|---|
| The work lives in a Claude Design canvas, or the user asked for a canvas, or you are running inside Claude Design | Claude Design canvas: new files (or a new canvas) beside the original | host-claude-design.md |
| A Design artifact type is available and the user wants something shareable on claude.ai, with no codebase in play | A new Claude Design canvas | host-claude-design.md |
| Working in a repository, and a standalone faithful recreation is enough to choose a direction (most cases) | Self-contained HTML gallery in a new scratch folder | host-codebase.md, then host-html.md |
| Working in a repository whose components are too complex to recreate faithfully, and the app runs locally | Dev-only variations harness: new files only, never imported by production code | host-codebase.md |
| Plain chat with file creation or artifacts, no canvas | Self-contained HTML gallery, published as an artifact when that is how the user opens files there (host-html.md §7) | host-html.md |
| No way to create files at all | The gallery HTML in one code block, plus the ledger as JSON, with a note on how to open it | host-html.md, last section |

The user can always override: "put it in a new canvas", "just give me an HTML file", "make it a Storybook page".

## 5. When to ask, and how

Ask only when **two or more** open decisions would each change what you build, and someone is there to
answer. One round of questions, at most four, through the host's question tool when it has one
(multi-select by default, your recommended option first, concrete options drawn from what you read).
Otherwise decide, state assumptions in one line, and build.

Worth asking (when genuinely open):

- Which surface, when the user named a product but not the screen.
- What may change, when a redesign request is ambiguous about scope ("overhaul" the page, or just the table?).
- Whether to stay in the current visual language or explore new ones, when nothing signals either.
- Platform and frame size, when the product ships on several and the subject differs between them.

Never ask:

- How many options (ten, unless they said otherwise).
- Whether to make them interactive (always).
- Questions the code, canvas or screenshots already answer. Read first.
- Permission to use connected MCPs (they connected them to be used). Do ask before uploading the user's own
  private images or code to any third-party service.

When the brief is a single sentence with nothing to read ("make me a landing page for a ceramics studio"),
do not ask a form's worth of questions: commit to a reading, put the assumptions in one line, and let the ten
options do the asking. A spread is itself a question.

## 6. Counts, sizes and other overrides

- **Count:** honour any explicit number. With fewer than ten, keep the spread across the range the round
  covers, then fill the bands in proportion (spectrum-ladder.md §5). With more than ten, add options to the
  middle bands first. Record `count` in the round.
- **Budget:** ten hi-fi prototypes are a lot of output. Build in batches (SKILL.md step 4) and, if a turn runs
  out, deliver what is finished with a Degraded line and continue next turn.
- **Sparse subjects:** when the surface is too small to hold ten genuinely different answers (a three-field
  form, a single button group), widen the frame to the surrounding screen and let options vary how the part sits
  in it, or include the part's states (empty, error, success) in the variation. If even that would force
  look-alikes, say so in one line and offer a smaller count; never pad with duplicates. On a thin subject the
  Reinvent options must change the job's framing (capture first, a triage queue, time blocking, a review ritual),
  not re-slice the same field in a new layout.
- **Frame size:** use the size the product is actually used at. On a canvas, the original artboard's frame is the
  default; note it if that is not the product's real viewport. Desktop web app: 1440×900 (or the size the
  original's layout targets). Marketing page: 1440 wide and tall enough for the full page. Phone app: 390×844.
  Tablet: 834×1112. A component: its realistic container plus enough page around it to judge it.
- **Responsive:** every web option must also work at the narrowest width the product supports. The gallery's
  width switch lets the user check; you check before presenting.
- **Theme:** dark or light as the product is; both only if the product ships both and the round is about
  visual language.
- **Fidelity:** always hi-fi and interactive. If the user explicitly asks for quick sketches or wireframes,
  honour it, keep the spread, and say what is not wired.

## 7. Intake checklist

Before step 1, you can answer all of these in a line each:

- Mode and round number (and the ledger's location if iterating or resuming).
- Subject sentence.
- Redesign, new in a theme, or new and open.
- Host and output location (a new file or canvas, never the original).
- Count, frame size, platform, theme.
- Assumptions you are making, and any question you asked.

## 8. Host capabilities to check at run time

Hosts differ, and some capabilities cannot be known in advance. Check, then adapt:

| Capability | If present | If absent |
|---|---|---|
| Design-reference MCP tools in the tool list | Use them; test a sign-in notice with one cheap call before believing it (inspiration-mcps.md §2) | Fallback ladder (inspiration-to-ideas.md §6) |
| Code execution (Python, Node) | Run `dv.py` and `smoke.mjs` | Hand-author the gallery (host-html.md §6); run the checks by reading |
| A browser tool | Click through every option | Reason through handlers; say rendering was not checked |
| Subagents | Parallel batches (host-codebase.md §5) | Build sequentially in batches |
| A question tool and a person present | At most one round of questions | Decide and state assumptions |
| The Design artifact type | Canvas output (host-claude-design.md) | HTML gallery |
