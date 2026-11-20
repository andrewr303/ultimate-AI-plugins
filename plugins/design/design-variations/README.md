# Design Variations

Decide on a design direction by looking at ten real, working alternatives at once. Give it a screen, a
component, a flow or a brief. It builds ten fully interactive prototypes, ordered from a careful refinement of
what you have to a radical rethink, in a new variations file. Your original is never touched. Pick, combine or
push back, and the next round builds on what you liked.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`design-variations`](skills/design-variations/SKILL.md). Try this prompt.

> Create six interactive directions for this settings screen, ranging from a small refinement to a new layout. Carry over the existing controls and include an error state in each.

## What you get

- **Ten options per round** (or the number you ask for), each a live, hi-fi prototype of the whole surface with
  realistic content. Every control works, and the key states (empty, loading, error) can be previewed.
- **A deliberate spread.** Options run 1a–1j up a ten-step ladder in four bands: Refine, Evolve, Rethink and
  Reinvent for redesigns, or Proven, Fresh, Novel and Experimental for new designs. Each option changes a
  different thing, and says what it costs.
- **Your product kept intact.** Redesigns keep every function, the data and the brand unless you say
  otherwise, even in the radical options. A "Now" frame shows today's design for comparison.
- **Real inspiration.** When a design-reference library is connected (Gummble, Mobbin, Refero, UXKin, Figma,
  Dembrandt and similar), the skill searches it, looks at the results, and cites what each option borrowed.
  When nothing is connected, it says so and how to connect one.
- **A new file every time.** Rounds go into a separate variations gallery or Claude Design canvas files,
  newest round on top. Like your own options canvases, each option has an ID chip, a short name, a one-line
  difference and cost, and a full-size live frame. Chosen and merged results get their own rounds.
- **Iteration that listens.** In the gallery, shortlist options, mark directions you don't want, and add notes;
  then copy the feedback into the chat. Ask for "more" (ten new directions, never repeats), "like 2c and 2g",
  "combine 2c's header with 2g's list", "refine 4e", "bolder" or "closer to today".

## Use it

> Give me ten interactive variations of our invoices page, from small tweaks to radical redesigns.

> Design ten directions for a new pricing page that fit our product's look.

> I like 1c and 1g. Combine 1c's header with 1g's list and push it bolder.

> None of these. Ten new directions, nothing like the board ideas.

> Let's go with 3e. Apply it to the real component.

The skill picks where the output goes and tells you. In a Claude Design canvas, it adds new files, usually on
a new page, beside your original. In a repository, it writes a self-contained gallery in a new folder. In
chat, it produces an HTML gallery you can open or publish. Applying a choice to the original only happens when
you ask.

## Install

- **Claude Code:** install the plugin from this repository's marketplace (the repository is private, so your
  git credentials need access to it):

  ```bash
  claude plugin marketplace add andrewr303/ultimate-AI-plugins
  ```

  ```bash
  claude plugin install design-variations@ultimate-ai-plugins
  ```

  Or copy `skills/design-variations/` into `~/.claude/skills/` (personal) or a project's `.claude/skills/`. It
  triggers when you ask for design variations, options or directions. You can also call it directly:
  `/design-variations` for a copied skill, or `/design-variations:design-variations` from the plugin.
- **Claude (claude.ai, where Claude Design now lives):** upload `design-variations-skill-<version>.zip`, which
  is in this repository's `artifacts/design-variations/` folder. Go to Customize → Skills, choose "+", then
  "+ Create skill", and upload the ZIP. Claude's skills feature requires code execution to be enabled.
- **Other agent hosts:** `plugin.json` follows the Agent Plugins 1.0 manifest; `agents/openai.yaml` carries the
  listing for hosts that read it.

### Connect an inspiration library (recommended)

The skill is much stronger with a connected design-reference library. Gummble is checked first.

| Library | Connect |
|---|---|
| Gummble | Claude Code: `/mcp` → gummble → Authenticate if the connector is already installed, or add `https://mcp.gummble.com/mcp`. claude.ai: Settings → Connectors. Needs a Gummble plan with MCP access. |
| Mobbin | `claude mcp add --transport http mobbin https://api.mobbin.com/mcp`, then `/mcp` to sign in (Pro, Team or Enterprise). |
| Refero | `claude mcp add --transport http refero https://api.refero.design/mcp`, then sign in (paid plan). |
| UXKin | `claude mcp add --scope user --transport http uxkin https://uxkin.com/mcp`, then sign in (UXKin plan). |
| Figma | `claude mcp add --transport http figma https://mcp.figma.com/mcp` for reading your own frames. |

## What's inside

```
skills/design-variations/
  SKILL.md                 the round workflow, deliverables and hard rules
  references/              18 one-level references: intake, preservation contract, spectrum ladder, variation
                           axes, pattern alternatives, aesthetic directions, inspiration MCPs, references to
                           ideas, prototype standard, output anatomy, three hosts, iteration, critique and
                           presentation, skill routing, anti-patterns, worked examples
  assets/                  gallery template, ledger schema and example, Claude Design canvas templates
  scripts/dv.py            workspace init, next IDs, gallery build (with per-round kits and standalone pages),
                           ledger and quality checks, a boot check of the built gallery, novelty against history
                           and passed directions, Claude Design linter
  scripts/smoke.mjs        optional Playwright pass: dead controls and fake toggles, hidden elements that still
                           show, covered controls, clipped text, phone width, per-state screenshots, one round at a
                           time, and an automated squint test
  scripts/dc-check.mjs     runs Claude Design artboards' logic for every Tweak value without the canvas runtime
  agents/openai.yaml       listing metadata for hosts that read it
  evals/                   six test cases in the `claude plugin eval` layout (excluded from upload ZIPs)
```

No MCP server, API key or background service is required. Python 3.8+ (standard library only) runs `dv.py`;
Node 18+ runs `dc-check.mjs`, and with Playwright, the optional smoke test.

## Review

[EVALUATION.md](EVALUATION.md) records what was checked and how: static validation, the gallery and canvas
runtime tests, and simulated skill runs with adversarial reviews. [PROVENANCE.md](PROVENANCE.md) explains the
research behind the design and what was learned from which sources. No third-party text, prompts or code are
included.
