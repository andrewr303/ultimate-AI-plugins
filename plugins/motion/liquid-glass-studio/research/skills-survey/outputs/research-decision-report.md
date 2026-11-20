# Liquid glass agent skills: research decision report

Date: 2026-11-05. Mode: manual review. The automated gates (repo-hunt-plus, insane-research-main) are not installed in this environment, so no automated PASS is claimed and no verified_claims.json exists. Every per-finalist weakness line and every Refuted row carries a claim ID from `artifacts/claim_ledger.jsonl`, as do the gap statements that criticise a named project and every Unresolved row except the last, which records a data-access gap. Each ledger entry names its source IDs in `sources/sources.jsonl`. Strength bullets and adoption-map evidence cite pinned `repo@sha:path:line` locations recorded in the inspection objects of `artifacts/candidates.json`, and rejection reasons come from the triage records there; those do not all have ledger entries. Inspectors read named files at pinned SHAs. Repository trees could not be listed (GitHub `/contents` and `/git/trees` returned HTTP 403 for every candidate), so a statement that something is absent means it was not found in the files read, not that it is absent from the repository.

## Question and method

**Question.** Which existing agent skills, plugins, rule packs, llms.txt files and MCP servers help a coding agent design, build and review liquid glass interfaces, and what can our original plugin (liquid-glass-studio) learn from them or do that none of them do?

**Discovery arms.**

1. awesome-repositories MCP directory (src_057). Curated-search triage, tag taxonomy, six tag searches, filtered and unfiltered repository search, and name-recall lookups. Result: no dedicated liquid glass skill in the directory; the liquid-glass-effects tag subtree holds 2 repos, both libraries (clm_004, unresolved).
2. GitHub search ladder (src_059). 11 repository queries (for example `"liquid glass" skill`, `topic:agent-skills glass`, `liquid glass mcp`), 10 code queries plus path lookups (for example `"liquid glass" filename:SKILL.md` with 9056 hits, `feDisplacementMap filename:SKILL.md` with 527 hits, `"liquid glass" extension:mdc` with 132 hits, `"liquid glass" filename:llms.txt` with 160 hits), and commit search to date default branches.
3. Web and marketplace sweep. 9 web searches (skills.sh, claudskills, smithery, mcp.so, cursor.directory, llms.txt), about 14 more repository searches, and README checks of anthropics/skills, obra/superpowers, travisvn/awesome-claude-skills, ComposioHQ/awesome-claude-skills and VoltAgent/awesome-agent-skills (src_055).

**Tool availability.** GitHub search endpoints (`search/repositories`, `search/code`, `search/commits`) and raw.githubusercontent.com worked. Per-repo REST (`repos/OWNER/REPO`, `/commits/SHA`), GraphQL and the GitHub MCP were refused for repositories outside this session (HTTP 403). No repository was attached, cloned for execution, installed or run. Inspectors read files at pinned SHAs through raw fetches; two inspectors (anubhavaanand, Zettersten) used a blobless bare fetch of commit metadata only. One WebFetch to cursor.directory returned HTTP 429. Armitanemati/liquid-glass-claude-skill could not be read at all.

**Counter searches run for this record (2026-11-05).** `gh api search/repositories` with batched `repo:` qualifiers for the 10 finalists and 8 notable rejects (stars, license, pushed_at, archived, fork), and `gh api search/commits` with `hash:` for 8 inspected HEAD SHAs plus `glass` commit searches for Zettersten and Dimillian. Results are recorded in clm_003, clm_009, clm_011 and clm_012.

**Libraries seen but out of scope.** The directory arm also surfaced glass libraries that ship no agent skill, for example rdev/liquid-glass-react (src_060, pushed 2025-06-13, stale) and callstack/liquid-glass (src_061, React Native wrapper for native glass). They are not ranked here.

**Grading.** Inspectors graded each finalist strong / match / adjacent and scored it out of 10 on eight coverage areas. "Activity verified" means a default-branch commit dated within 75 days with a confirmed changed-file count.

## Ranked findings

Ties at 8.0 are ordered by breadth across web and native.

| Rank | Repo | Format | Grade | Score | Activity (HEAD, date, verified) | License | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | Tsdsj/Apple-Style | 4 SKILL.md family plus JS runtime, CSS, Playwright script | strong | 8.0 | 103385529843, 2026-10-20, unverified files | none (cite only) | Only finalist with real web and native coverage, plus the best reviewer evidence model |
| 2 | gentpan/liquidglass | library with skill, references, scripts | strong | 8.0 | 068ad226f53e, 2026-09-19, unverified files | MIT | Best web engine and per-engine quirk table; no native, weak contrast handling |
| 3 | xenitV1/liquid-glass-skill | skill with tokens.css and refraction.js | strong | 8.0 | 8cf508b2e547, 2026-10-12, unverified files | MIT | Most direct competitor; honest gaps section; thin perf and verification |
| 4 | WAIS-CLOUD-SORTER/liquid-glass | skill, references, static checker, evals | strong | 7.8 | 11f18a25f066, 2026-10-04, unverified files | MIT | Clearest fidelity-tier model and a lint checker; weak optics; CI claim not borne out |
| 5 | CharlesWiltgen/Axiom | multi-host plugin with glass auditor | match | 7.0 | b185447110ba, 2026-11-04, verified (18 files) | MIT | Best audit procedure; Apple only; examples contradict its own auditor |
| 6 | the-Ashkanian/ashi-liquid-glass | single-file skill with embedded engine | match | 6.5 | 1dc795bcceb8, 2026-10-08, unverified files | MIT | Physically motivated Snell map and good runtime hygiene; weak a11y; tests not observed |
| 7 | anubhavaanand/glass-of-web | skill, engine, node tests | match | 5.5 | 9c65bcce5145, 2026-11-01, verified (3 files) | none (cite only) | Portable content-refraction model; skill text drifted from the engine |
| 8 | AvdLee/SwiftUI-Agent-Skill | multi-host SwiftUI plugin | match | 5.5 | 204dba7c6725, 2026-10-06, unverified files | MIT | Reach and packaging model; references contradict each other; no glass a11y guidance in files read |
| 9 | Zettersten/skills | skill with references, generator, templates | match | 5.0 | glass skill e9e39fe1040f, 2026-08-13, stale | MIT | Closest folder layout to ours; dispersion order and sign conventions conflict; fallback claim contradicted by its own template |
| 10 | Armitanemati/liquid-glass-claude-skill | skill (per triage) | unverified | 0 | pushed 2026-09-17 | MIT per API only | Not gradable: no file could be read |

Stars at 2026-11-05 (clm_003): AvdLee 3829, Axiom 1247, gentpan 23, xenitV1 12, Tsdsj 11, Ashkanian 8, Zettersten 7, Armitanemati 3, anubhavaanand 2, WAIS 0. The high-star glass skills are SwiftUI native; every web-refraction finalist has 23 stars or fewer.

## Coverage matrix

Cells come from each inspection's coverage object and rate only the files each inspector read. "none" means nothing for that area was found in those files; because repository trees could not be listed, it does not establish that the repository lacks the area. The Armitanemati column is "none" because nothing was read at all.

| Area | Tsdsj | gentpan | xenitV1 | WAIS | Axiom | Ashkanian | anubhavaanand | AvdLee | Zettersten | Armitanemati |
|---|---|---|---|---|---|---|---|---|---|---|
| Design guidance | strong | solid | strong | strong | strong | thin | thin | thin | thin | none |
| Web implementation | strong | strong | strong | strong | none | strong | solid | none | solid | none |
| Optics math | thin | strong | solid | thin | none | solid | solid | none | solid | none |
| Native SwiftUI | solid | none | solid | solid | strong | none | none | solid | none | none |
| Accessibility | solid | thin | solid | strong | solid | thin | none | none | none | none |
| Performance | solid | solid | thin | solid | thin | strong | thin | thin | thin | none |
| Verification | strong | solid | thin | solid | solid | none | thin | thin | none | none |
| Browser support | solid | strong | solid | solid | none | solid | thin | none | thin | none |

## Per-finalist notes

### 1. Tsdsj/Apple-Style (src_005)

- Anatomy table maps each material layer to a web mechanism: `Tsdsj/Apple-Style@103385529843:skills/Apple-Style-Liquid-Glass/SKILL.md:12-26`.
- Lens gate combines `CSS.supports` with a UA check and skips lensing under reduced transparency, more contrast and a lite flag: `@103385529843:skills/Apple-Style/web/liquid-glass.js:59-64,214` (clm_018).
- Full preference set including forced-colors: `@103385529843:skills/Apple-Style/web/css/preferences.css:15-53` (clm_007).
- Reviewer uses checked / not checked / not applicable with Blocker, Major and Minor: `@103385529843:skills/Apple-Style-Review/SKILL.md:12-34`.
- Weaknesses: heuristic smoothstep map with no Snell term (`liquid-glass.js:150-152`, clm_026); recorded browser evidence is Chromium only (`docs/validation.md:72,175`, clm_026); no LICENSE file (`docs/license-decision.md:3`, clm_009). Whether the native recipe at `SKILL.md:53` is valid Swift is in Unresolved (clm_035); self-reported test counts are in Unresolved (clm_020).

### 2. gentpan/liquidglass (src_004)

- Situation-to-pattern table (wrap, overlay copy, backdrop copy, Chromium-only backdrop, WebGL): `gentpan/liquidglass@068ad226:skill/liquid-glass-web/SKILL.md:21-31` (clm_002).
- Engine-breaking rules including sRGB and WebKit filter-id caching: `@068ad226:skill/liquid-glass-web/SKILL.md:78-84` (clm_022).
- Full optics (SDF, superellipse height, Snell offset, RGBA encoding): `@068ad226:skill/liquid-glass-web/references/optics.md:23-55`.
- Weaknesses: claims 4.5:1 contrast is "guaranteed by the tint layer" (`SKILL.md:93`, clm_027); WebGL renderer has no context-lost handling or offscreen pause (`assets/glass-webgl.js:56,143,162`, clm_027); no prefers-contrast or forced-colors in `assets/components.js` (clm_007); verification is macOS-only and manual (`scripts/shoot.sh:1-38`, clm_005). Per-engine scale measurements are author-only (clm_019, Unresolved). tfdmendes/liquidglass (src_011) is a declared copy with newer commits (clm_023).

### 3. xenitV1/liquid-glass-skill (src_001)

- Two-layer content-vs-chrome model with quoted HIG rules: `xenitV1/liquid-glass-skill@8cf508b2e547:SKILL.md:43-61`.
- Engine with Chromium backdrop mode and a sanitised mirror mode elsewhere: `@8cf508b2e547:assets/refraction.js:20-33,269-283` (clm_001, clm_002).
- Honest gaps section: `@8cf508b2e547:SKILL.md:369-381`.
- Weaknesses (clm_028 unless noted): rAF mirror sync with no offscreen pause (`refraction.js:306-335`); no devicePixelRatio (`refraction.js:121-122`); HIG contrast thresholds given for web text with no WCAG reference in the files read (`SKILL.md:251-252`); no prefers-contrast block (`assets/tokens.css:525-546`, clm_007); Playwright verification is claimed (`references/materials.md:142-146`), none of the fetched files are tests, and the repository tree could not be listed.

### 4. WAIS-CLOUD-SORTER/liquid-glass (src_008)

- Floating-vs-reading sort with a 0.85 fill floor, enforced by a lint rule: `WAIS-CLOUD-SORTER/liquid-glass@11f18a25:SKILL.md:30-38`, `scripts/check-glass.mjs:227-397`.
- Fidelity tiers A/B/C: `@11f18a25:SKILL.md:42-50`.
- Weaknesses: separable linear ramps that do not use the corner radius (`assets/refraction-map.svg:17-34`, clm_029); no numeric contrast measurement in the files read (clm_029); claimed CI workflow is absent and the HEAD commit says it was deferred (clm_013). Inspectors also questioned two API names (`references/refraction-advanced.md:152`, `references/swiftui.md:46`); that check was not made against primary documentation and is in Unresolved (clm_035). Safari support for prefers-reduced-transparency conflicts with other sources (clm_008, Unresolved).

### 5. CharlesWiltgen/Axiom (src_006)

- Phased auditor with 8 detection patterns, false-positive list and health score: `CharlesWiltgen/Axiom@b185447:axiom-codex/skills/axiom-audit-liquid-glass/SKILL.md:14-20,112,254-329` (clm_016).
- Single-source generation for several hosts: `@b185447:.claude-plugin/plugins/axiom/skills/axiom-design/SKILL.md:11-17`.
- Weaknesses: Apple only (clm_006); its "correct" toolbar sample applies `.glassEffect()` inside a ToolbarItem (`skills/liquid-glass.md:441-444`) and its reference pins bars by hand (`skills/liquid-glass-ref.md:473-495`), two patterns its own auditor flags (clm_030); "Developer Action Required: None" for accessibility settings (`skills/liquid-glass.md:190`) while the auditor asks for a contrast re-check (clm_030).

### 6. the-Ashkanian/ashi-liquid-glass (src_002)

- Snell refraction over an exponent-4 superellipse bezel: `the-Ashkanian/ashi-liquid-glass@1dc795b:SKILL.md:206-211`.
- Runtime hygiene: geometry-keyed map cache, IntersectionObserver gating, filter GC: `@1dc795b:SKILL.md:231-313`.
- Weaknesses (clm_031): UA regex detection (`SKILL.md:201`); hover-only tooltip and modal without dialog semantics (`SKILL.md:172,344-345`); hard-coded right alignment (`SKILL.md:122`); no destroy API (`SKILL.md:308-313`); no demo at the probed paths (index.html, demo.html, examples/, package.json returned 404); tests not observed (only SKILL.md, README.md and LICENSE were read, and the tree listing was blocked).

### 7. anubhavaanand/glass-of-web (src_003)

- "Refract the content, not the backdrop" model: `anubhavaanand/glass-of-web@9c65bcc:SKILL.md:20-30` (clm_002).
- Hole-punch composite keeps outside pixels unchanged: `@9c65bcc:glass-engine.js:374-401`.
- Weaknesses: SKILL.md describes a 17-primitive chain while the engine emits 13 or 14 (clm_014); no `color-interpolation-filters` on the filter (`glass-engine.js:298-305`, clm_022); WebGL multi-lens overwrite and texture leak (`glass-engine.js:557-558,672-676`, clm_032); no license (clm_009).

### 8. AvdLee/SwiftUI-Agent-Skill (src_009)

- Router SKILL.md plus on-demand references; "APIs that do not exist" list: `AvdLee/SwiftUI-Agent-Skill@204dba7:skills/swiftui-expert-skill/references/liquid-glass.md:75-83`.
- Self-update skill with a scan manifest: `@204dba7:.agents/skills/update-swiftui-apis/SKILL.md:8`.
- Weaknesses: sheet morphing names contradict between references (clm_017); no Reduce Transparency, Increase Contrast or Reduce Motion guidance for glass in the two files searched (clm_033). Whether the `glassEffectWithFallback` helper (`liquid-glass.md:376-390`) compiles below iOS 26 was not checked by compiling and is in Unresolved (clm_035).

### 9. Zettersten/skills (src_010)

- Router plus physics and filter-pipeline references, generator and templates: `Zettersten/skills@567c013:skills/liquid-glass/SKILL.md:98-147`.
- Displacement decode formula and sRGB rule: `@567c013:skills/liquid-glass/references/physics.md:19-21,48` (clm_022).
- Weaknesses: says Firefox and Safari "ignore the url() part automatically, keeping the blur" (`SKILL.md:130-136`), while its own TSX template strips url() outside Chrome (`assets/templates/LiquidGlass.tsx:249-254`, clm_034); what those browsers do is unverified here (clm_036, Unresolved); dispersion order puts green highest (clm_015); generator sign convention conflicts with the docs (`scripts/generate-displacement-map.py:152-167,366`, clm_034); stale since 2026-08-13 (clm_012).

### 10. Armitanemati/liquid-glass-claude-skill (src_007)

All four read paths were refused. Triage describes a 538-line design-reasoning skill (clm_025), but none of it was confirmed. The GitHub API license field says MIT (clm_010).

## Gaps no existing skill covers

These are the openings for liquid-glass-studio. Each is stated against the files the inspectors read, not against whole repositories or the whole ecosystem.

1. **Automated cross-engine visual verification.** No finalist ships pixel or screenshot assertions that run in Chromium, Firefox and WebKit on Linux or CI (clm_005). gentpan's three-engine script is macOS-only and manual; Tsdsj's recorded checks are Chromium only (clm_026).
2. **Measured legibility over the refracted backdrop.** No finalist's files read measure text contrast against the worst-case region behind the glass. gentpan claims the tint guarantees 4.5:1 (clm_027); xenitV1 gives HIG thresholds for web text (clm_028); the WAIS inspection found no numeric contrast measurement (clm_029).
3. **Render-level capability detection.** Every engine decides the Chromium-only path by UA sniffing, a parse-level `CSS.supports` or `@supports`, or both (clm_018). None renders and samples a probe.
4. **Web and native in one place with a reviewer.** No finalist combines deep web refraction, SwiftUI / UIKit / AppKit glass, design reasoning and an evidence-based reviewer (clm_006).
5. **Docs that cannot drift from code.** anubhavaanand's skill text describes a filter the engine no longer builds (clm_014); Axiom's and AvdLee's own examples contradict their other files (clm_030, clm_017). WAIS has a doc-vs-stylesheet drift check and gentpan's bundled engine is byte-identical to its library copy; no other drift guard was found in the files read.
6. **Accessibility preferences with documented browser support.** Most web finalists skip prefers-contrast and forced-colors (clm_007), and the sources disagree on where prefers-reduced-transparency works (clm_008). WAIS pairs the media query with a user-facing solid toggle (`material.md:139-159`), and xenitV1's engine has a manual `data-rt` hook (`refraction.js:69-72`).
7. **Correct optics conventions under test.** Dispersion order (clm_015), displacement sign conventions (clm_034) and the sRGB neutral point (clm_022) are wrong or untested in several skills. None of the files read include numeric tests on a map generator.
8. **WebGL path without lifecycle bugs.** anubhavaanand's WebGL path overwrites lenses and leaks textures (clm_032); gentpan's has no context-lost handling or offscreen pause (clm_027).
9. **Freshness for web compat data.** AvdLee refreshes SwiftUI API notes through a scan manifest; nothing does the same for browser support of backdrop-filter, SVG filters and the accessibility media queries.

## Adoption map

"Our implementation" names the file in this plugin that carries the idea. Ideas are re-implemented in original code and prose; nothing is copied. Attribution is listed where an idea is specific enough to credit.

| Idea | Evidence | How liquid-glass-studio implements it | Attribution |
|---|---|---|---|
| Content vs chrome layer rule, glass only on chrome | src_001 `SKILL.md:43-61`; src_005 cheatsheet `:12-17`; src_008 `SKILL.md:30-38` | `references/design-principles.md` states the rule; the reviewer treats glass on reading surfaces as a finding | Credit the HIG; idea is common across 3 orgs |
| Fidelity tiers with a guaranteed baseline | src_008 `SKILL.md:42-50`; src_044 (tiering, stale) | Engine `explainTier` / `detectTier` in `examples/glass-lab/liquid-glass.js`; tiers documented in `references/web-techniques.md` | Credit WAIS for the clearest framing |
| Portable refraction on the element's own pixels | src_003 `SKILL.md:20-30`; src_004 `SKILL.md:21-31` | Described in `references/web-techniques.md` as the cross-engine path; Chromium backdrop path stays an enhancement | Credit Aave Labs article via gentpan and anubhavaanand |
| SDF map from the real border radius, selectable surface profile | src_001 `refraction.js:100-218`; src_002 `SKILL.md:206-211`; src_004 `optics.md:23-36` | `roundedRectSDF`, `PROFILES` (convexCircle, convexSquircle, concave, lip) and `refractionProfile` in the engine; derivation in `references/optics.md` | General technique; credit kube.io-derived profiles where Zettersten cites them |
| sRGB filter space and neutral 128 encoding | src_010 `physics.md:19-21,48`; src_004 `SKILL.md:78-84` | `buildFilterMarkup` sets `color-interpolation-filters="sRGB"`; `encodeDisplacement` / `decodeDisplacement` with `NEUTRAL` and a bias correction, covered by `tests/engine.test.mjs` | Spec behaviour, no credit needed |
| Dispersion as per-channel passes | src_002 `SKILL.md:257`; src_005 `SKILL.md:16` | Engine uses scales R < G < B and takes alpha from one pass, avoiding the order in src_010 (clm_015) and the alpha sum in src_001 and src_003 (clm_028, clm_032) | Technique is common |
| DPR-aware maps | gap in src_001 `refraction.js:121-122` (clm_028) and src_002 `SKILL.md:247` (clm_031) | `displacementField` takes `pixelRatio` | Not needed |
| Backdrop Root diagnosis | src_008 `material.md:186`; gap in src_002 `SKILL.md:78-79` (clm_031) | `findBackdropRoot` in the engine; listed in `references/gotchas.md` | Credit WAIS for the review-checklist framing |
| Full preference set: reduced transparency, more contrast, forced colors, reduced motion | src_005 `preferences.css:15-53`; src_008 `SKILL.md:175-197` | `MEDIA_QUERIES` in the engine, with an engine comment that prefers-reduced-transparency is Chrome only and absent in Safari; `references/accessibility.md` | Common; support data is still Unresolved (clm_008) |
| Worst-case contrast measurement | gap (2 above) | `scripts/glass_contrast.mjs` and `scripts/contrast-math.mjs` hide the text and measure the rendered backdrop; `tests/contrast.test.mjs` | Original |
| Phased auditor with false-positive list and evidence states | src_006 auditor `SKILL.md:14-329`; src_005 Review `SKILL.md:12-34` | Review workflow should record checked / not checked / not applicable and run named detection patterns with a false-positive section | Credit Axiom and Apple-Style for the pattern |
| Symptom to cause to fix tables | src_004 `browser-quirks.md:7-25`; src_003 `SKILL.md:186-198`; src_005 `SKILL.md:38-50` | `references/gotchas.md` | Common pattern |
| "APIs that do not exist" list | src_009 `liquid-glass.md:75-83` | `references/native.md` should carry a short list, adding names questioned in src_008 and src_009 only after they are checked against Apple documentation (clm_035) | Credit AvdLee for the pattern |
| Engine lifecycle: destroy, observers | gap in src_002 `SKILL.md:308-313` (clm_031) | `createGlass` returns a handle with destroy and uses ResizeObserver | Not needed |
| Multi-host packaging from one source | src_006 `axiom-design/SKILL.md:11-17`; src_009 `README.md:11` | `plugin.json` plus `.claude-plugin/` manifest | Common |

## Rejected candidates

| Repo | Reason |
|---|---|
| Dimillian/Skills (src_012) | SwiftUI only, glass skill last touched 2026-03-06 (clm_012), mirrored near-verbatim by src_014 and src_015 |
| nextlevelbuilder/ui-ux-pro-max-skill (src_013) | Adjacent; glass appears only as style-database rows (clm_024) |
| huozhi/vaso (src_019) | Thin 51-line skill; useful only for its Safari flashing fix |
| EVEDensity/Liquid-Glass-Skill (src_029) | Mainly an editor app; 34-line SKILL.md |
| agent-skills-hub/agent-skills-hub (src_030) | Likely mirror of src_031 |
| woodfishhhh/glass-material-skills (src_031) | 47 and 42 line skills, stale |
| jpoindexter/liquid-glass-web (src_032) | Stale; same technique covered by src_003 and src_004 |
| pedronauck/skills (src_033) | 65-line skill, shallow |
| csuyincs-creator/fluidglass-ui (src_034) | Less depth than web finalists |
| deepika-builds/liquid-glass (src_035) | 38-line skill, stale |
| imMamdouhaboammar/motion-graphics-skills (src_036) | Motion graphics, adjacent |
| openai/plugins (src_014) | First-party benchmark, but glass skills stale (2026-05-27) and SwiftUI only |
| steipete/agent-scripts (src_015) | Near-duplicate of the Dimillian skill |
| rshankras/claude-code-apple-skills (src_016) | Strong API depth, glass skill stale (2026-07-13); secondary citation |
| dickwu/apple-design-skill (src_017) | General HIG reviewer, glass is minor |
| Prisma-Labs-Dev/apple-skills (src_026) | Overlaps Apple finalists |
| dpearson2699/swift-ios-skills (src_025) | Stale |
| conorluddy/LiquidGlassReference (src_024) | Reference doc, not a skill; stale |
| aka-kika/hig-mcp (src_020) | MCP with glass as one facet; packaging idea only |
| sxhxliang/gpui-liquid-glass (src_037) | Rust GPUI niche |
| podo/design-agent-skills (src_038) | 79-line skill, shallow |
| tfdmendes/liquidglass (src_011) | Copy of gentpan, covered under the gentpan entry |
| iart-ai/web-animation-skills (src_022) | Stale (2026-06-22) |
| jiuyang5354/skills (src_023) | Overlaps gentpan and anubhavaanand; much content Chinese-only |
| yichen08092025/liquid-glass (src_039) | Overlaps WAIS tiering with less depth |
| sridhar-raj/blur-craft (src_040) | Frosted blur only, no refraction |
| lucaperullo/simple-liquid-glass (src_027) | Library slot went to gentpan; secondary llms.txt reference |
| liquefy-ui/liquefy-ui (src_041) | No SKILL.md; llms.txt 404 |
| moekoelueker/open-glass-ui (src_042) | llms.txt is usage docs only |
| meniscus-site/meniscus-mcp (src_021) | Thin skill; hosted OAuth MCP would send code to a third party |
| IntelliHelper/agent-skills (src_043) | No glass SKILL.md verified |
| radustefandumitru/overdrive (src_044) | Stale; tiering better covered by WAIS |
| dabit3/liquid-glass-web-skill (src_045) | Stale; no displacement refraction |
| bowen31337/apple-design (src_046) | Stale; broader than glass |
| jcm-developer/liquid-glass-components (src_047) | Claimed rule files 404 or stub |
| Na2H2P2O7/liquid-glass-skill (src_048) | Desktop-window niche, stale |
| affaan-m/ECC (src_018) | Huge reach but narrow SwiftUI skill, glass content reportedly stale |
| expo/skills (src_028) | Glass is one section of a React Native reference |
| sickn33/agentic-awesome-skills (src_049) | Mirror list |
| aiskillstore/marketplace (src_050) | Mirror list |
| heyparsadev/liquid-glass-skill (src_051) | SwiftUI only, overlaps Axiom and AvdLee |
| 2dubu/liquid-glass (src_052) | 43-line SKILL.md, iOS only |
| haider-nawaz/liquid-glass-skill (src_053) | Stale; skill path unconfirmed |
| anthropics/skills (src_054), PatrickJS/awesome-cursorrules (src_056) | No glass content; format references only |
| skills.sh listings (src_058) | Aggregator; listings map to repos above |

## Unresolved

| Claim | Why unresolved | What would settle it |
|---|---|---|
| clm_004: directory has no dedicated glass skill; liquid-glass tag subtree has 2 repos | Single origin (one MCP session); not re-queried | Re-run `explore_tag` on the liquid-glass-effects path |
| clm_008: Safari does not support prefers-reduced-transparency | Inspectors assert it from prior knowledge; WAIS `material.md:132` says Safari supports it. Our engine comment cites web-features-explorer, which was not fetched in this research step | Fetch MDN browser-compat-data or web-features for the feature |
| clm_010: Armitanemati is MIT | API license field only; LICENSE file never read | Read LICENSE at a pinned SHA |
| clm_019: gentpan per-engine feDisplacementMap scale formulas | Author-measured; no reproducible page committed | Render a probe page in Chromium, Firefox and WebKit |
| clm_020: Tsdsj test counts; WAIS 89.0% vs 51.3% benchmark | Self-reported in each repo | Run each suite at the pinned SHA |
| clm_021: headless Chromium under-renders blur of 20px or more | Single org | Compare headless and GPU-backed screenshots |
| clm_025: Armitanemati content (538 lines, layer model) | No file readable this session | Grant read access and inspect |
| Engine behaviour behind clm_018: `CSS.supports('backdrop-filter','url(#x)')` returns true in engines that do not render it | Stated by xenitV1, inferred by inspectors for WAIS and Zettersten | Run the probe in Safari and Firefox |
| SwiftUI API existence behind clm_017 (navigationZoomTransition, navigationTransitionSource) and other SDK 27 names | Beyond what the inspectors could check against Apple docs | Check current Apple documentation |
| clm_035: API and spec names questioned by inspectors (WAIS `prefers-reduced-rendering` and `buttonShape`; AvdLee `glassEffectWithFallback` availability; Tsdsj `.glassEffectTransition(.matchedGeometry \| .materialize)`) | Inspectors judged these from their own knowledge; no specification or Apple documentation was fetched and nothing was compiled | Check Media Queries Level 5 and current Apple documentation, or compile the snippets against the current SDK |
| clm_036: Firefox and Safari keep the blur when url() is in backdrop-filter (Zettersten `SKILL.md:130-136`) | No browser was run; only Chromium is installed here. The same repo's template strips url() outside Chrome (clm_034), and `references/browser-support.md` treats loss of blur as an inference from WebKit bug 245510 and Gecko bug 1961378 | Run `scripts/glass_probe.mjs` in WebKit and Firefox once those browsers are installed |
| Changed-file counts for xenitV1, Ashkanian, gentpan, Tsdsj, WAIS, AvdLee HEADs | `commits/SHA` endpoint refused (403) | Read each commit's file list |

## Refuted

| Claim | Source | Refuting evidence |
|---|---|---|
| "Exact 17-primitive" filter chain in glass-of-web | src_003 `SKILL.md:47-70` | Engine emits 13 or 14 primitives and its own test asserts 5 composites (`glass-engine.js:313-401`, `test/filter.test.js:214`), clm_014 |
| CI runs `.github/workflows/check.yml` in WAIS | src_008 `BENCHMARK.md:76`, `README.md:113` | Path 404 at HEAD; HEAD commit message "defer CI workflow: token lacks workflow scope" (clm_013) |
| "Green disperses more" | src_010 `LiquidGlass.tsx:174` | Normal dispersion rises toward shorter wavelengths, so blue should get the largest scale (clm_015) |
| "Text on glass: at least 4.5:1, guaranteed by the tint layer" | src_004 `SKILL.md:93` | A fixed 8-20% tint cannot bound contrast over an arbitrary backdrop (a backdrop matching the text colour gives a ratio near 1:1); the inspector found no measurement in the files read (clm_027) |
| Triage SHAs as the current HEADs for xenitV1, Ashkanian and WAIS | triage in `candidates.json` | Commit search on 2026-11-05 shows the inspected HEADs (8cf508b2e547, 1dc795bcceb8, 11f18a25f066) carry the same push-day dates (clm_011) |
