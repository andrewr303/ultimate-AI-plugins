# Host: working inside a codebase

Read this when the original lives in a repository (Claude Code, or any host with file access to the user's
project). It covers reading the original from source, where variations may be written without touching
anything that exists, the two output routes, and promotion.

## Contents

1. Read before you design
2. Where to write
3. Route A: standalone gallery (default)
4. Route B: dev-only variations harness
5. Parallel building with subagents
6. Promotion into the real code
7. Repository etiquette

## 1. Read before you design

- Follow the repository's own instructions files (CLAUDE.md, AGENTS.md, CONTRIBUTING) and conventions. When
  they set a reply format (a status header, labelled fields, a decision layout), fit the round's reply inside
  it (critique-and-presentation.md §5).
- Find the subject's source: the route or page, its components and children, styles (CSS, Tailwind config,
  CSS-in-JS theme), design tokens, icon set, fonts, copy, data types, fixtures or mocks, tests and stories.
- Run the app if it starts with the documented command on a free port, and look at the real surface in the
  states that matter. Stop only what you started.
- Record exact token values and the component library used. Note what the product is built with (React, Vue,
  Svelte, plain HTML), because Route B depends on it.
- Write the preservation contract from this reading (preservation-contract.md).

## 2. Where to write

Never edit, rename, move or reformat existing files during exploration. New files only, in one place:

1. A folder the repository already uses for scratch or design work, if it has one (for example `.tmp/`,
   `design/`, `prototypes/`, `playground/`).
2. Otherwise `design-variations/<subject-slug>/` at the repository root.

Check `git status` first so you do not mix your files with the user's uncommitted work. Do not stage or commit
the variations unless the user asks; mention whether the folder is ignored by git, and suggest adding it to
`.gitignore` when it should not be committed (do not edit `.gitignore` without asking).

## 3. Route A: standalone gallery (default)

Recreate the surface faithfully as HTML prototypes in a gallery (host-html.md):

- Copy the product's tokens into `kit/kit.html` exactly (custom properties, or the resolved values of the
  Tailwind theme the components use).
- Rebuild the components' markup and states from source, keeping the same structure, spacing, type, colours,
  icons and copy for the faithful base. Use real fixtures or mocks from the repo for data where they exist (with
  personal data masked); otherwise realistic synthetic data shaped like the real types.
- Build every option on that base. Because each option is a standalone prototype, radical options are free to
  restructure without fighting the app's architecture.

Choose Route A unless faithful recreation would cost more than it is worth (Route B).

## 4. Route B: dev-only variations harness

When the real components carry too much behaviour or styling to recreate (complex data grids, editors,
charts, design-system components with heavy logic) and the app runs locally, build the options with the real
components instead:

- Add new files only: a variations route or page (for example `src/dev/variations/ShipmentsVariations.tsx`
  mounted at `/__variations/shipments`), or a story file per round if the project uses Storybook or Ladle.
- Each option is a new component under the variations folder, composing the product's real components. Select
  options with a URL parameter (`?v=2c`) and render all ten stacked with their IDs, names and descriptions,
  following output-anatomy.md.
- Production code must never import from the variations folder. Do not register the route in production
  navigation; guard it to development builds the way the project already guards dev-only code.
- If the router needs one registration line in an existing file, ask before adding it, or use the project's
  existing dev or story mechanism that needs no edits.
- Also produce a static gallery when you can (screenshots plus links), so the user can compare without running
  the app.

## 5. Parallel building with subagents

Ten prototypes are a lot of code. When the host supports subagents and parallel file writes:

1. You write the plan (step 3), the contract and the shared kit (or the faithful base) first. These are the
   coupled decisions; they stay with you.
2. Split the options across workers (two or three options each). Every worker gets the **fact pack**: the subject
   sentence, the contract, the kit path (tokens, fonts, shared components, data), its plan rows with their
   reference locks and `traits`, its siblings' one-line ideas and traits as things to avoid, the signatures of
   passed options, the prototype standard, and the host's format rules, plus the variant file paths it owns
   (one writer per file). The kit is read-only for workers; a helper they need goes back to you.
3. Refine and Evolve workers also get the faithful base (`variants/today.html`) to start from. Rethink and Reinvent
   workers get no base file and no screenshots of today, so they are not anchored on today's layout; the kit
   gives them the product's look.
4. Workers return the paths they wrote, each option's signature interaction, and anything they could not make
   work. Worker reports are findings, not verification: run the checks yourself.
5. You integrate: build, check, smoke-test, and review the ten side by side for real differences and
   consistent quality. Fix or redo weak options yourself or with a targeted follow-up.

## 6. Promotion into the real code

Only when the user asks to apply a chosen option ("make 3c real", "ship 3c"):

1. Say what you will change: which files, which components, what moves, what is new, what tests change.
2. Implement it with the project's conventions and real components (not the prototype's markup), behind the
   project's usual review flow: a branch or a pull request only when the user asks for one.
3. Run the project's checks (typecheck, lint, tests) and look at the result in the running app.
4. Record the promotion in the ledger (`promoted`: the option ID, the files changed, the date).
5. Leave the variations folder in place unless the user asks to remove it.

## 7. Repository etiquette

- Never run unknown setup scripts from references or examples; never install packages without need and
  permission; use the repository's package manager when you must.
- Keep secrets, real customer data and internal URLs out of prototypes and screenshots; mask them.
- Delete only files you created, by exact path, never with a folder glob. `smoke.mjs` overwrites its own
  screenshots, so there is no need to clear the shots folder between runs.
- Report precisely: which files you created, how to open the gallery (`open design-variations/shipments/index.html`
  or a local server command), what you checked, what you did not.
