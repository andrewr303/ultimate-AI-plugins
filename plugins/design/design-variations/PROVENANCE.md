# Design provenance

Design Variations is an original instruction package. Its core shape comes from the creator's requirements:
ten options per round from small tweaks to radical redesigns, redesigns that keep their functions, inspiration
from connected libraries such as Gummble, a new design file every time, fully interactive prototypes, a fit with
the product's theme, self-sufficiency with optional calls to other skills, and an iteration loop. Its output
format follows the creator's own Claude Design options canvas: rounds newest first, ID chips, a one-line
difference and cost, full-size live frames, and Chosen merge rounds.

No third-party prompt text, implementation code, templates, images or other assets are included. The research
below informed abstract design decisions only. Research was done read-only on 2026-11-01, following the
research-first-creator plugin's manual review mode. No automated research-verification pass is claimed. The full
source register, claim ledger and decision report are kept with the package evidence in the repository
(`artifacts/design-variations/research/`).

## What the research changed

| Decision | Evidence (abstract ideas only) |
|---|---|
| Write a plan with a name, angle and cost for every option before building; sketch more concepts than needed, then keep a spread-out ten | Variant-round skills such as [Nutlope/variate](https://github.com/Nutlope/variate) (MIT), [bitjaru/styleseed](https://github.com/bitjaru/styleseed) (MIT) and [oil-oil/oil-ui](https://github.com/oil-oil/oil-ui) (MIT); Anthropic's first-party frontend-design skill; Design Galleries (Marks et al., SIGGRAPH 1997) on dispersion; studies showing model-generated ideas homogenise (Doshi & Hauser 2024; Anderson et al. 2024) |
| A ten-rung ladder in four bands, ordered from least to most change | Scope ladders in [educlopez/ui-craft](https://github.com/educlopez/ui-craft) (refresh, reskin, rebuild) and conservative-to-wild ordering in several skills; a choice-overload meta-analysis finding no general overload effect (Scheibehenne et al. 2010), with proposed moderators (Chernev et al. 2015; Mogilner et al. 2008 on category labels) treated as unresolved, so structure is added as a precaution |
| One primary axis per option, with pairwise distinctness tests (silhouette, swap, one-sentence difference) | oil-ui's shared-traits cap and squint test; variate's same-angle check; gstack design-shotgun's headline-swap test; Gourville & Soman 2005 on alignable sets |
| Preservation contract with protected classes (brand equity, information architecture, voice, conversion paths) and "no option worse for accessibility than today" | ui-craft's preservation classes; [superdesign-skill](https://github.com/superdesigndev/superdesign-skill)'s reproduce-first and logo invariants; Google's change-aversion framework (Sedley & Müller, CHI 2013); NN/g on incremental versus radical redesign |
| A "Now" frame showing today's design next to the options, never as one of them | variate (variant 1 is the untouched original); [joshpuckett/dialkit](https://github.com/joshpuckett/dialkit) (V1 holds base values); Tohidi et al. (CHI 2006) on inflated ratings of single designs; status-quo and primacy research |
| Parallel alternatives shown together, then merges rather than winner-takes-all | Dow et al. (TOCHI 2010) on parallel prototyping; one case study reported by NN/g (Nielsen & Faber 1996) in which a merged design outperformed the best single design (single source, unresolved) |
| Merges take whole parts from named donors; dead directions stay dead; taste memory needs two decisions and keeps one or two pattern-breaking slots | variate's merge and narrowing rules; gstack's taste profile; [deepshal99/variantkit](https://github.com/deepshal99/variantkit)'s taste evidence rule (single-source, labelled) |
| Iteration recipes: refine, push, cross over, wildcard; "more" excludes everything seen | Interactive evolutionary computation (Takagi 2001); novelty search (Lehman & Stanley 2011); Picbreeder (Secretan et al. 2011) |
| Feedback grammar in the gallery: shortlist, "not this", notes with like / wish / what if, then a composed message | gstack's comparison board; LMArena and lmring's "all bad" bucket; NN/g on critique; Takagi on low-effort selection |
| Gallery with full-size live frames, an overview mode, compare for two to four, and focus mode | variate, screenshot-to-code and dialkit presentation modes; NN/g on comparison tables (compare few at a time) |
| Required inspiration step with provider detection, a query recipe keyed to bands, look-before-citing and reference locks | Official docs for [Gummble](https://docs.gummble.com/docs/mcp), [Mobbin](https://docs.mobbin.com/mcp/introduction), [Refero](https://doc.refero.design/mcp/getting-started), [UXKin](https://uxkin.com/docs) and [Figma](https://developers.figma.com/docs/figma-mcp-server/); [referodesign/refero_skill](https://github.com/referodesign/refero_skill)'s reference lock (MIT); Siangliulue et al. (CSCW 2015) on diverse examples reducing fixation |
| Claude Design output as an options document plus a base copy with an enum Tweak and standalone artboards | The creator's own options canvas, and the Design artifact type's published format; dialkit and open-codesign show options as parameter values on one component |
| A ten-rung ladder defined by the deepest design plane an option touches (surface, skeleton, structure, scope, strategy), with a test per rung, and a separate convention-to-experimental ladder for new designs | Garrett's planes of user experience (via a secondary review), Google's change-aversion work (change aversion does not apply to a first product), and design-system documentation of named alternatives (IBM Carbon, Twilio Paste, GOV.UK Design System, Android and Apple guidelines) |
| Sixteen variation axes with costs, 21 archetype catalogs and 26 aesthetic directions with watch-outs | Carbon density and motion guidance, Material dynamic-colour schemes, Fluent shape and elevation ramps, Paste and Carbon pattern pages, NN/g articles on cards, tables, disclosure and modals, and design-history sources for named movements. A few directions (soft minimal, organic, quiet luxury) rest on general design vocabulary, not primary literature |
| Routing to other skills, and never starting user-invoked ones | The installed ult-design plugin (MIT) and its declared upstreams (jakubkrehel/skills, mobbin/skills, referodesign/refero_skill, plugin87/ux-ui-agent-skills, dembrandt/dembrandt-skills), read locally. Their templates and the CC BY-SA writing-tell list were not reused |
| An automated squint test, contract mapping per option and an inspiration inventory checked by `dv.py` | Gaps found by an independent cold-read audit and the research completeness review; tests like the squint and silhouette checks come from oil-ui and gstack, automated here |
| SKILL.md as a short router over one-level references, a third-person description, under 500 lines | Anthropic's Agent Skills best practices and the agentskills.io specification |

## Licences

Ideas were taken only from repositories under MIT or Apache-2.0, and only abstractly. The output format follows
the creator's own options canvas; the Claude Design runtime found in that export was used only to test canvas
output locally and is not included. Repositories without a
licence (for example ZeroZ-lab/cc-design and 0xdesign/design-plugin) were read for context and contributed no
specific mechanism. High-star repositories the creator distrusts (for example gstack, screenshot-to-code) are
labelled as outside the preferred star band wherever they are cited. Two colour-strategy names and part of the
cliché list first came from an out-of-band repository (pbakaus/impeccable); the shipped wording rests on Material's
colour schemes and the in-band skills instead. Two repositories were not inspected: huashu-design (out of band)
and Owl-Listener/designer-skills (just above the band). Google Stitch reportedly offers a refine, explore and
reimagine range of up to five variants; that comes from third-party descriptions only.

## Unresolved

- No inspected source generates ten options per round. The ten-option mechanics (bands, ladder, axis rules,
  gallery modes) are an original synthesis from two-to-eight-option practice and decision research.
- No inspiration MCP was signed in during research. Provider tool lists come from official documentation dated
  2026-11-01, and the skill tells agents to read live tool schemas first.
- Claude Design's `.dc.html` format comes from the Design artifact type's instructions as published on
  2026-11-01. The skill defers to the type's live instructions.
- Effect sizes for several studies were read from abstracts rather than full texts; the skill quotes no effect
  sizes.
- What a given host allows (connectors inside the Claude Design flow, script execution, subagents) varies, so the
  skill checks capabilities at run time (intake-and-modes.md §8) instead of assuming them.

## Refuted

- The often-quoted "6 versus 24 jams" result is not used as a rule: meta-analyses show choice overload is
  conditional, not general.
- A "70% versus 18%" comparison circulates as merged design versus best single design. The 18% figure actually
  measures traditional iterative design between two versions, so that reading is refuted and the skill does not
  use it.
