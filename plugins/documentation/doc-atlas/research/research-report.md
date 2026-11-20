# Doc Atlas research decision report

Status: manually supported design synthesis. The local research accelerator was not configured; no automated research PASS or verified_claims.json is claimed. Public code was read as data; no candidate was cloned, installed, or executed.

The deliverable is a skills-only agent plugin for repository documentation: README composition, documentation architecture, framework integration, API reference, diagrams, review, and maintenance. It uses original instructions and local preflight helpers, without a hosted server.

## Supported findings and original design

Documentation implementations model navigation separately from page prose [clm_navigation]. Keep a source inventory and a task-based page map before writing. Evidence: src_004, src_013.

Rendered documentation checks complement source checks, including accessibility behavior [clm_render_checks]. Require a real framework build and browser review when those capabilities exist; mark unavailable checks untested. Evidence: src_041, src_033.

Documentation tooling distinguishes markup semantics when evaluating content [clm_markup]. Keep the bundled offline helper deliberately limited, identify unsupported syntax, and use the repo's actual parser for MDX and framework routes. Evidence: src_051, src_071.

Search implementations account for loading and empty or error states [clm_search_states]. Include these states in the site review checklist. Evidence: src_033, src_025.

## Original implementation choices

Use the existing docs framework and package manager. For a new site, choose from requirements and installed ecosystem; do not prescribe an evergreen version. Keep GitHub README output valid without custom CSS or JavaScript. Treat a site as a separate rendering surface. Pair visuals with useful text, light and dark treatment, responsive behavior and keyboard access. Trace commands and feature statements to repository evidence. Never generate fictional badges, performance numbers, endpoints or screenshots.

Runtime helpers will use the Python standard library and will not fetch URLs or execute repository commands. They inspect selected repository metadata and perform a conservative Markdown preflight. Complete external link, MDX, API schema, accessibility and runtime validation belongs to the actual project tooling.

## Provenance map

| Requirement | Adopted idea | Evidence | Original component |
| --- | --- | --- | --- |
| Discoverable docs | Separate navigation model | clm_navigation | Architecture skill and page-map template |
| Useful visual polish | Review rendered behavior | clm_render_checks | Visual direction guide and site review checklist |
| Honest quality checks | Respect syntax boundaries | clm_markup | Read-only inventory and conservative preflight helper |
| Search usability | Review loading and empty/error states | clm_search_states | Browser acceptance scenarios |

## Unresolved

The following table records directly observed finalist snapshots. Individual repository metadata and license observations have not been independently corroborated under the research skill's strict claim rule. They are comparison inputs, not affirmative claims of legal clearance, full accessibility, reliability, or maintenance quality. All reuse decisions are **ideas only; original prose/code; no upstream source bundled**. Dependency integration in a target repo still requires checking its exact installed release and license. Star counts are observations, not quality scores.

| Requirement / finalist | Pinned implementation evidence | Gap / fit judgment | Observed license / reuse decision | Original design choice |
| --- | --- | --- | --- | --- |
| Structured/versioned docs: `facebook/docusaurus` | `facebook/docusaurus@4e6fe61666a521d35d328ec0561d84eb96609017:packages/docusaurus-plugin-content-docs/src/sidebars/generator.ts` (src_004) | React docs stack; avoid adding migration cost | MIT; ideas only | Existing-stack adapter |
| Composable React docs: `fuma-nama/fumadocs` | `fuma-nama/fumadocs@da4ca7b86ad97fa98ae648ed35403559f89d7c74:apps/docs/lib/source/navigation.ts` (src_013) | Fast-moving package layout; inspect installed exports | MIT; ideas only | Version-aware adapter rather than copied snippets |
| Next.js docs incumbent: `shuding/nextra` | `shuding/nextra@d6e80e1dd627b781429a6ee989b15ebba688c8ea:packages/nextra/src/client/components/search.tsx` (src_025) | Older default branch; relaxed-screen reference only | MIT; ideas only | Test search against built output |
| Markdown-centric docs: `vuejs/vitepress` | `vuejs/vitepress@415a6a39507af37e282c02eb57ca50594f1bc237:src/client/theme-default/styles/vars.css` (src_032) | Vue/Vite fit; rich components require its renderer | MIT; ideas only | Semantic theme and code-block guidance |
| Documentation-focused site: `withastro/starlight` | `withastro/starlight@982a22f2c83b1926f0db7eaa9d557fb488957acb:docs/__a11y__/docs.test.ts` (src_041) | Astro integration; verify project package version | MIT; ideas only | Accessibility and navigation acceptance criteria |
| Markdown consistency: `DavidAnson/markdownlint` | `DavidAnson/markdownlint@5dd44fe44481cfbc8c6fee955719773fa17dc5d5:lib/md045.mjs` (src_051) | Does not establish command correctness or full visual quality | MIT; ideas only | Separate source lint from rendered review |
| Schema-driven API docs: `Redocly/redoc` | `Redocly/redoc@1bc09cd8c6edf414311da8ae4bb8d8ea29dc05f8:src/components/Security/SecuritySection.tsx` (src_063) | Do not infer runtime auth or endpoint behavior from UI | MIT; ideas only | Schema-first reference and safe example policy |
| Technical prose: `vale-cli/vale` | `vale-cli/vale@8b9bfb97700a707140fff9f444048439df5bc9b1:internal/lint/mdx.go` (src_071) | Style configuration and MDX parser version matter | MIT; ideas only | Optional repo-owned prose rules |
| Link integrity: `lycheeverse/lychee` | `lycheeverse/lychee@d9d97b51e395bd72c6498e0c6c4943dcae7b410a:lychee-bin/tests/cli.rs` (src_076) | External reachability can be transient or authenticated | Apache-2.0; ideas only | Distinguish offline paths from remote checks |
| Diagrams as code: `mermaid-js/mermaid` | `mermaid-js/mermaid@f61bea59f3e091cd7a7958aa79dfb96a0102e997:README.md` (src_083) | Renderer support differs across platforms | MIT; ideas only | Caption, text explanation, renderer verification |
| Interactive API reference: `scalar/scalar` | `scalar/scalar@862997c4fc8fe96a529c2dd0be15711c40a31ae2:README.md` (src_092) | Hosted/client/server surfaces differ; do not invent integrations | MIT; ideas only | Version-aware OpenAPI adapter |

### Activity and discovery observations

Observation date: 2026-10-27. Query ladder and candidate grades live in discovery/queries.json and discovery/candidates.json. Directory triage had no matching curated page; filtered and unfiltered searches were used, then named lookup/get evidence. Incorrect-category results were discarded. GitHub API and pinned source were used independently of the directory. No exhaustive claim that all GitHub repositories were found is made.

- `facebook/docusaurus`: `4e6fe61666a521d35d328ec0561d84eb96609017`; default-branch commit `2026-10-23T20:43:28Z`; changed files observed: 5; stars observed: 66588; snapshot `frameworks/facebook--docusaurus/evidence.json`.
- `fuma-nama/fumadocs`: `da4ca7b86ad97fa98ae648ed35403559f89d7c74`; default-branch commit `2026-10-26T14:22:25Z`; changed files observed: 7; stars observed: 13483; snapshot `frameworks/fuma-nama--fumadocs/evidence.json`.
- `shuding/nextra`: `d6e80e1dd627b781429a6ee989b15ebba688c8ea`; default-branch commit `2026-06-23T16:02:07Z`; changed files observed: 3; stars observed: 13944; snapshot `frameworks/shuding--nextra/evidence.json`.
- `vuejs/vitepress`: `415a6a39507af37e282c02eb57ca50594f1bc237`; default-branch commit `2026-10-26T21:58:29Z`; changed files observed: 5; stars observed: 18441; snapshot `frameworks/vuejs--vitepress/evidence.json`.
- `withastro/starlight`: `982a22f2c83b1926f0db7eaa9d557fb488957acb`; default-branch commit `2026-10-26T21:48:55Z`; changed files observed: 1; stars observed: 9475; snapshot `frameworks/withastro--starlight/evidence.json`.
- `DavidAnson/markdownlint`: `5dd44fe44481cfbc8c6fee955719773fa17dc5d5`; default-branch commit `2026-10-20T02:28:05Z`; changed files observed: 1; stars observed: 6399; snapshot `quality/DavidAnson__markdownlint/evidence.json`.
- `Redocly/redoc`: `1bc09cd8c6edf414311da8ae4bb8d8ea29dc05f8`; default-branch commit `2026-10-21T12:32:25Z`; changed files observed: 1; stars observed: 25979; snapshot `quality/Redocly__redoc/evidence.json`.
- `vale-cli/vale`: `8b9bfb97700a707140fff9f444048439df5bc9b1`; default-branch commit `2026-10-24T15:57:41Z`; changed files observed: 3; stars observed: 6290; snapshot `quality/errata-ai__vale/evidence.json`.
- `lycheeverse/lychee`: `d9d97b51e395bd72c6498e0c6c4943dcae7b410a`; default-branch commit `2026-10-26T12:49:59Z`; changed files observed: 3; stars observed: 4051; snapshot `quality/lycheeverse__lychee/evidence.json`.
- `mermaid-js/mermaid`: `f61bea59f3e091cd7a7958aa79dfb96a0102e997`; default-branch commit `2026-10-26T15:57:27Z`; changed files observed: 34; stars observed: 90887; snapshot `quality/mermaid-js__mermaid/evidence.json`.
- `scalar/scalar`: `862997c4fc8fe96a529c2dd0be15711c40a31ae2`; default-branch commit `2026-10-27T05:19:14Z`; changed files observed: 1; stars observed: 16325; snapshot `quality/scalar__scalar/evidence.json`.

Nextra is outside the primary activity screen and retained only as a labeled relaxed incumbent. README template directories and inactive generators were not adopted as defaults. Recent commits containing only dependency/lockfile changes prove activity, not substantive feature development. API errors or missing paths were not interpreted as successful checks.

License text and package dependencies were inspected as source evidence. Docusaurus has a separate documentation license file; Lychee has MIT and Apache alternatives despite singular API metadata. Those source observations do not resolve an independent legal conclusion. No third-party implementation, branding, templates or artwork is copied into the plugin.

## Refuted

No supported design claim was contradicted by the inspected evidence. Rejected source assumptions include treating Nextra's default branch as changed within the preferred window, assuming historical Fumadocs source paths remain current, treating a successful HEAD request as proof of fragment existence, and assuming one GitHub-style slugger validates every framework's anchors. The pinned source records contradict those assumptions. They are not used as affirmative recommendations.
