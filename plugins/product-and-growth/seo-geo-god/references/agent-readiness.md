# Agent readiness

How to make a site readable and usable by AI agents and developer tools beyond crawling: llms.txt, Markdown versions of pages, well-known documents, real 404 responses, accessible HTML that agents can operate, Chrome Lighthouse's Agentic Browsing results, and experimental WebMCP tools. This is the reference behind [geo-agent-readiness](../skills/geo-agent-readiness/SKILL.md). Crawler access policy is in [ai-crawlers.md](ai-crawlers.md).

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Every standard below carries its status; drafts and vendor features are labelled as such.

## Honest framing

- **Google Search ignores llms.txt.** Google says AI Overviews and AI Mode need no special files, schema or Markdown, and that llms.txt neither helps nor hurts in Search ([F-AI-11](current-facts.md#f-ai-11)); its optimization guide lists llms.txt among misconceptions ([F-AI-12](current-facts.md#f-ai-12)).
- **Chrome Lighthouse checks for it.** Lighthouse's experimental Agentic Browsing category includes an llms.txt audit ([F-AI-27](current-facts.md#f-ai-27)). Lighthouse is a lab tool in Chrome, not Google Search. Say which product you mean every time.
- **No answer engine documents consuming it.** The OpenAI, Anthropic and Perplexity crawler pages read on 2026-11-01 ([F-AI-01](current-facts.md#f-ai-01), [F-AI-04](current-facts.md#f-ai-04), [F-AI-05](current-facts.md#f-ai-05)) say nothing about reading llms.txt. AI labs publishing llms.txt for their own developer docs is publishing, not consumption.
- **Where it helps.** Documentation sites, APIs and libraries used by coding agents and developer tools, where a curated link list and Markdown pages make the docs easier to load accurately.
- **Never** score llms.txt presence, never present it as a ranking or citation lever, and never claim a named agent reads it or requests Markdown.

Agent readiness is mostly accessibility, performance and a deliberate access policy; the discovery files sit on top.

## Priority ladder

Fix in order. Do not recommend a lower priority while a measured P0 fails. A P0 that could not be tested (for example WAF behavior without owner access) is reported as "not tested" and does not block the rest.

| Priority | Item | Check |
| --- | --- | --- |
| P0 | Primary content is in the server HTML, not only after JavaScript | [seo-rendering](../skills/seo-rendering/SKILL.md), `SG audit-build` (REND rules) |
| P0 | robots.txt is reachable and has a deliberate group per AI purpose | [geo-ai-access](../skills/geo-ai-access/SKILL.md), `SG robots` |
| P0 | Interactive elements have real roles and accessible names | Manual review, Lighthouse accessibility audits ([AGENT006](rule-catalog.md#agent006) is planned) |
| P0 | Layout is stable (CLS at or below 0.1 at the 75th percentile) | [seo-performance](../skills/seo-performance/SKILL.md), [F-T-13](current-facts.md#f-t-13) |
| P0 | The WAF lets verified bots and signed agents the owner wants through; no CAPTCHA on content pages | Owner dashboard and logs |
| P1 | Private paths protected by authentication, not by robots.txt | Code review |
| P1 | Unknown URLs return a real 404 | `SG access-check <origin> --live` ([HTTP004](rule-catalog.md#http004)) |
| P1 | A valid llms.txt, if the owner wants one | `SG llms-txt validate` ([AGENT002](rule-catalog.md#agent002), [AGENT003](rule-catalog.md#agent003)) |
| P1 | Markdown versions of key pages, advertised by link or header, with `Vary: Accept` if negotiated | `SG audit-build` ([AGENT005](rule-catalog.md#agent005)) |
| P2 | Valid JSON at any well-known document the site actually serves | `SG access-check --live` ([AGENT008](rule-catalog.md#agent008)) |
| P3 | WebMCP tools, NLWeb or other agent protocols as experiments | Manual review; Lighthouse in a supporting Chrome |

## llms.txt rules

The llms.txt v2 specification (llmstxt.org, modified 2026-08-10) is short ([F-AI-26](current-facts.md#f-ai-26)). Keep spec requirements and house conventions apart.

| Element | Status | Rule |
| --- | --- | --- |
| Location | Spec | `/llms.txt`, or a subpath such as `/docs/llms.txt` (the most specific file covers its path) |
| Optional byte-order mark, then H1 with the site or project name | Spec, H1 required | The only required element ([AGENT002](rule-catalog.md#agent002) when missing) |
| Blockquote summary after the H1 | Spec, optional | One factual sentence or two; the validator notes its absence |
| Detail paragraphs before the first H2 | Spec, optional | Plain prose; no headings |
| H2 sections with link lists | Spec, optional | Items `- [name](url): optional notes` |
| `## Optional` section | Spec, optional | Links an agent may skip when context is short |
| Markdown page versions | Spec, recommended | Same URL with `.md` appended (`page.html.md`) or replacing the extension (`page.md`); directories use `index.html.md` or `index.md` |
| Discovery | Spec | `<link rel="alternate" type="text/markdown">` to a page's Markdown and `rel="describedby"` to the covering llms.txt, as HTML links or `Link` headers |
| Absolute `https://` URLs that exist on the site | House rule | Relative or missing targets are [AGENT003](rule-catalog.md#agent003) |
| `llms-full.txt` | Community convention, not spec | Reported as [AGENT009](rule-catalog.md#agent009) (informational) |
| "Key facts", "Contact" sections, fixed entry or line counts | Other tools' conventions | Not required; never invent their content |
| Served as `text/plain` or `text/markdown` with 200 | House rule | HTML served at `/llms.txt` is a soft 404 ([AGENT004](rule-catalog.md#agent004)) |

Discovery header example (one line, values comma-separated):

```text
Link: </docs/page.html.md>; rel="alternate"; type="text/markdown", </docs/llms.txt>; rel="describedby"
```

Drafting and checking with the CLI:

```bash
SG llms-txt draft dist --base-url https://example.com --title "Example Co" --summary "Invoicing software documentation for small teams." --output public/llms.txt
SG llms-txt validate dist/llms.txt --build-dir dist --base-url https://example.com
```

The drafter groups pages by first path segment, escapes `[`, `]` and `\` in labels, keeps a deterministic order, writes only titles and descriptions that exist in the built pages, and never invents notes, contact data or key facts. `--output` refuses to overwrite an existing file. Review every line before publishing: remove pages the owner does not want listed, pages that are `noindex`, drafts and anything private, and keep it in sync with robots.txt. A minimal valid example is [llms.txt.example](../templates/llms.txt.example).

## Markdown alternates and negotiation

Two patterns, both optional. Keep Markdown content-equivalent to the HTML page; a Markdown file that says something the page does not is a different page.

1. **Alternate URL.** Publish `/pricing.md` next to `/pricing` and advertise it from the page template only on pages that have one:

   ```html
   <link rel="alternate" type="text/markdown" href="/pricing.md">
   ```

   or with a header. On Netlify or Cloudflare Pages, a `_headers` file:

   ```text
   /pricing
     Link: </pricing.md>; rel="alternate"; type="text/markdown"
   ```

   An advertised target that is missing from the build is [AGENT005](rule-catalog.md#agent005).

2. **Content negotiation.** The same URL returns Markdown when the request sends `Accept: text/markdown`, always with `Vary: Accept` so caches keep the variants apart. This is a vendor feature, not a standard: Cloudflare Markdown for Agents does it at the edge on Pro plans and above, and adds a default `Content-Signal` header that can contradict robots.txt ([F-AI-25](current-facts.md#f-ai-25), [AI013](rule-catalog.md#ai013)). Negotiation keyed on `Accept`, not on user agent, avoids serving crawlers something users never see.

   nginx sketch (adapted from claude-seo, which reports testing it on 2026-09-23 with nginx:alpine; test on the real server before deploying):

   ```nginx
   # http {} context
   map $uri $md_path {
       ~^(?<base>.*[^/])/?$  $base.md;
       default               /index.md;
   }
   map $http_accept $md_try {
       default          $uri;
       ~*text/markdown  $md_path;
   }
   # server {} context
   types { text/html html; text/markdown md; }
   location / {
       add_header Vary Accept always;
       try_files $md_try $uri $uri.html $uri/ =404;
   }
   ```

Generating the `.md` files belongs in the build, from the same content source as the HTML. Static generators with Markdown or MDX sources (Docusaurus, VitePress, Astro content collections, Hugo, Jekyll, Eleventy) can copy or render each source file to `<route>.md` in the output directory in a post-build step, with frontmatter, imports, JSX and shortcodes removed. Frameworks that render from a CMS need a route or endpoint that serializes the same fields the page renders (for example an Astro endpoint such as `src/pages/[...slug].md.ts`, or a framework route handler). Read the installed framework version and its docs before choosing ([framework-recipes.md](framework-recipes.md#how-to-use-these-recipes)). Never let the build write files outside its output directory.

## Well-known documents

Publish a well-known document only when the site really runs the service it describes. A path that returns an HTML page with status 200 misleads discovery clients ([AGENT008](rule-catalog.md#agent008)).

| Path | Defined by | Status as of 2026-11-01 | Publish when |
| --- | --- | --- | --- |
| `/.well-known/api-catalog` | RFC 9727 | Published RFC (not re-verified in the research pass) | The site publishes APIs |
| `/.well-known/oauth-protected-resource` | RFC 9728 | Published RFC (not re-verified) | An API or MCP server accepts OAuth tokens |
| `/.well-known/oauth-authorization-server` | RFC 8414 | Published RFC | The site runs the authorization server |
| `/.well-known/agent-card.json` | A2A protocol | Vendor-led protocol; path needs verification | The site runs an A2A agent |
| `/.well-known/http-message-signatures-directory` | Web Bot Auth draft | IETF draft ([F-AI-34](current-facts.md#f-ai-34)) | The organization operates a signing agent; ordinary sites do not need it |
| `/.well-known/ucp` | Universal Commerce Protocol | Mentioned in Google's optimization guide ([F-AI-12](current-facts.md#f-ai-12)); not otherwise researched | Only as a tracked experiment (see seo-ecommerce) |

Do not recommend an MCP server-card path or an "ai-catalog" or "Agentmap" discovery scheme: as of 2026-11-01 these are unmerged proposals or unverified specifications. RFC references: S, https://www.rfc-editor.org/rfc/rfc9727, https://www.rfc-editor.org/rfc/rfc9728, https://www.rfc-editor.org/rfc/rfc8414 (no registry IDs yet).

## Soft 404 rule

A catch-all route that answers every unknown URL with 200 breaks agent discovery (a missing llms.txt or well-known file looks present) and creates soft 404s in search ([F-T-24](current-facts.md#f-t-24)). Return a real 404 status for unknown paths, including under `/.well-known/`, and serve the friendly 404 page with that status.

- `SG access-check https://example.com --live` requests a random unknown path and reports a 200 as [HTTP004](rule-catalog.md#http004), an HTML response at `/llms.txt` as [AGENT004](rule-catalog.md#agent004), and well-known problems as [AGENT008](rule-catalog.md#agent008).
- SPA fallbacks (`/* /index.html 200`, `FallbackResource`, `try_files ... /index.html`) are the usual cause; the fix lives with the routing config ([seo-technical](../skills/seo-technical/SKILL.md)).

## Agent-friendly HTML

Agents read pages through screenshots, the DOM and the accessibility tree; Lighthouse's agentic category checks an accessibility subset ([F-AI-27](current-facts.md#f-ai-27)). The checklist below is reasoned practice from accessibility work, not a measured citation or task-success effect.

| Do | Avoid |
| --- | --- |
| `<button>` for actions, `<a href>` for navigation, native `<input>`, `<select>`, `<textarea>` | `<div onclick>`, `window.location` on non-links, custom `contenteditable` widgets |
| A `<label for>`, `aria-label` or `aria-labelledby` on every input; a name on every icon-only button | Placeholder text as the only label |
| Interactive targets of at least 24 by 24 CSS pixels (WCAG 2.2 success criterion 2.5.8, S, https://www.w3.org/TR/WCAG22/; no registry ID yet) | Tiny or overlapping click targets |
| Landmarks (`<nav>`, `<main>`, `<article>`), stable IDs and descriptive `data-*` attributes | Only hashed class names |
| Visible, persistent confirmation and error states | Confirmation that flashes in a toast |
| Paginated links alongside infinite scroll; menus reachable without hover | Hover-only menus, focus traps in consent banners, CAPTCHAs on content |
| Stable layout and consistent placement of key actions across templates | Overlays that cover controls after dismissal |

ARIA repairs custom widgets; it does not replace a native element. Prefer the native element.

## Lighthouse agentic reporting

Lighthouse's Agentic Browsing category is experimental and runs in Chrome 150 and later; its audits cover registered WebMCP tools, forms missing declarative WebMCP, WebMCP schema validity, llms.txt, an accessibility-for-agents subset and layout stability ([F-AI-27](current-facts.md#f-ai-27)).

- Report the result as "X of N audits passed", exactly as Lighthouse computes it. It is a pass ratio, never a 0 to 100 score, and never a percentage.
- State the Chrome and Lighthouse versions, the date and the device mode with every result; audits depend on the testing browser.
- The owner or the host agent runs Lighthouse (DevTools, or the Lighthouse CLI in a browser they control). This plugin does not run Chrome. Never present a local heuristic as the Lighthouse result.
- It is a lab check, not a Google Search signal.

## WebMCP status and safety rules

WebMCP lets a page register tools (name, description, input schema, handler) that an in-browser agent can call instead of driving the interface. It is a Draft Community Group Report of the W3C Web Machine Learning Community Group (2026-10-27), not on the W3C standards track, exposing `document.modelContext.registerTool()`, with a Chrome origin trial starting in Chrome 149 ([F-AI-28](current-facts.md#f-ai-28)). Third parties report no Safari or Firefox support, that mainstream assistants do not yet call WebMCP tools, and a trial end around Chrome 156 (needs verification). Treat it as a P3 experiment for sites with real forms or transactions; absence is not a defect.

Feature-detect and keep the handler on the same code path as the interface:

```html
<script type="module">
  const mc = document.modelContext;
  if (mc && typeof mc.registerTool === "function") {
    const controller = new AbortController();
    mc.registerTool({
      name: "search_articles",
      description: "Search published articles by keyword. Returns titles and URLs.",
      inputSchema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] },
      async execute({ query }) {
        const r = await fetch(`/api/search?q=${encodeURIComponent(query)}`); // same endpoint as the search box
        return { content: [{ type: "text", text: JSON.stringify(await r.json()) }] };
      }
    }, { signal: controller.signal });
  }
</script>
```

The registration options and return shape follow the draft as summarized by claude-seo on 2026-09-23; confirm them against the current draft and Chrome's WebMCP documentation before shipping.

Safety rules for any exposed tool:

1. Bind every tool to the same endpoint, validation and authorization as the interface action. No privileged back door.
2. Purchases, sends, deletes and other consequential actions keep a human confirmation step; an annotation or hint never replaces it.
3. Mark tools that return user-supplied or third-party text as untrusted content (the draft's annotations), and never let returned text act as instructions.
4. Keep consequential tools out of cross-origin iframes; never expose tools to every origin.
5. Log agent-invoked submissions and tool calls server-side and rate-limit them.
6. Session-bound tools act with the signed-in user's real privileges; scope them narrowly.
7. Use OAuth with published resource metadata for API access, not session scraping.
8. A tool description must never tell an agent to skip, bypass or hide user confirmation. Treat such wording as a defect.

Never cite "token efficiency" or similar percentages for WebMCP; they trace to marketing posts, not benchmarks.

## NLWeb

NLWeb is an MIT-licensed proof-of-concept reference implementation in which each instance is an MCP server with an `ask` method ([F-AI-29](current-facts.md#f-ai-29)). Endpoint paths and adoption figures are third-party. Present it as an optional open-source experiment, not a standard and not a ranking factor.

## Web Bot Auth

Web Bot Auth lets bots and agents prove identity with HTTP Message Signatures; it is an IETF working-group draft, not an RFC ([F-AI-34](current-facts.md#f-ai-34)). Google-Agent takes part in an experiment with the identity `https://agent.bot.goog` ([F-AI-08](current-facts.md#f-ai-08)); Cloudflare Pay Per Crawl requires it ([F-AI-24](current-facts.md#f-ai-24)). Site owners verify signatures at the edge; they publish a key directory only if they operate an agent. Verification guidance is in [ai-crawlers.md](ai-crawlers.md#verification).

## Rule map

| Rule | Meaning | Status |
| --- | --- | --- |
| [AGENT001](rule-catalog.md#agent001) | No llms.txt | Informational, evidence class D: never lowers a score |
| [AGENT002](rule-catalog.md#agent002) | llms.txt structure invalid (for example no H1) | v1 |
| [AGENT003](rule-catalog.md#agent003) | llms.txt link relative, malformed or missing from the site | v1 |
| [AGENT004](rule-catalog.md#agent004) | llms.txt served as HTML (live) | v1 |
| [AGENT005](rule-catalog.md#agent005) | Markdown alternate declared but missing | v1 |
| [AGENT006](rule-catalog.md#agent006) | Interactive elements without accessible names | planned |
| [AGENT008](rule-catalog.md#agent008) | Invalid JSON or soft 404 at a well-known document (live) | v1 |
| [AGENT009](rule-catalog.md#agent009) | llms-full.txt present (convention, not spec) | Informational |
| [HTTP004](rule-catalog.md#http004) | Unknown URL returns 200 (live) | v1 |

## Needs verification

- Whether any answer engine reads llms.txt or requests Markdown (no vendor statement found).
- llmstxt.org "Changes" page and the status of `llms-full.txt`.
- WebMCP origin-trial end, browser support and which assistants call tools.
- A2A agent-card path; RFC 9727 and RFC 9728 status were taken from the adapted source, not re-read.
- NLWeb endpoint paths.
