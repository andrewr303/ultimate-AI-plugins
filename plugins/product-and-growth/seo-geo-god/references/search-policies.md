# Search policies for SEO and GEO work

The search-engine policies that decide whether a tactic is allowed, written for coding agents who change templates, content pipelines, structured data and routing. It covers Google's spam policies (with what each looks like inside a repository), structured-data and review policies, Google's guidance on AI-generated content, what is known about Bing's guidelines, how enforcement works, and a table that maps prohibited tactics to SEO-GEO-god rule IDs and to the compliant alternative. Used by [seo-content](../skills/seo-content/SKILL.md), [seo-programmatic](../skills/seo-programmatic/SKILL.md), [seo-local](../skills/seo-local/SKILL.md), [seo-ecommerce](../skills/seo-ecommerce/SKILL.md), [seo-structured-data](../skills/seo-structured-data/SKILL.md) and the router.

As of 2026-11-01. Facts are cited by ID from [current-facts.md](current-facts.md); rules link to [rule-catalog.md](rule-catalog.md). Policy pages change: re-read the primary page before quoting a policy to a user, and give its page date.

## How to use this file

- "Policy" means Google Search policy unless a row says Bing. Google's spam policies apply to Google Search, which includes AI Overviews and AI Mode; they do not describe ChatGPT search, Perplexity, Claude or Copilot, which publish no comparable policy set. Treat those surfaces as unknown, not as permissive.
- A policy breach is a judgment the search engine makes. The CLI can only flag code and content patterns that commonly cause one. A clean `SG audit-build` run is not a clearance; a finding is not proof of a violation.
- When a request needs a prohibited tactic, say which policy it breaks, cite the fact, and offer the compliant alternative from the last table. Do not implement a "light" version of the tactic.
- Owner approval is needed before removing, redirecting or noindexing content because of a policy concern; the decision affects traffic the agent cannot see.

## Spam policies that matter in code

Google's spam policies name 16 practices and count attempts to manipulate generative AI responses in Search as spam ([F-T-32](current-facts.md#f-t-32)). The descriptions below are ours; the policy page is the authority.

| Policy | Meaning (our words) | What it looks like in a repository | Check |
| --- | --- | --- | --- |
| Cloaking | Showing crawlers different content or URLs than users | Middleware, edge functions or server code branching on `User-Agent` (Googlebot, bingbot, GPTBot, OAI-SearchBot and others) to change HTML | [SPAM003](rule-catalog.md#spam003) (planned); search for user-agent branches in middleware |
| Doorway abuse | Many pages or sites made to rank for similar queries that funnel users to one destination | City-swap or product-swap templates with identical body text | [PSEO001](rule-catalog.md#pseo001); gates in [programmatic-seo.md](programmatic-seo.md) |
| Expired domain abuse | Buying an expired domain and hosting low-value content to exploit its old reputation | Migrating unrelated content onto a purchased domain | Agent check during migrations |
| Hacked content | Content or links placed without the owner's permission | Unexpected outbound links, obfuscated scripts, unknown pages in the build | Agent check; [CONT010](rule-catalog.md#cont010) for injected AI instructions |
| Hidden text and link abuse | Text or links hidden from users to manipulate ranking | `display:none` keyword blocks, off-screen text, text colored like its background, one-pixel links | Agent check; [CONT010](rule-catalog.md#cont010) when the hidden text addresses AI systems |
| Keyword stuffing | Filling pages with keywords or numbers out of context | Repeated city lists in footers, keyword lists in alt text or titles | [IMG002](rule-catalog.md#img002); agent read of titles and footers |
| Link spam | Buying, selling or exchanging links to manipulate ranking; automated link building | Sponsored-post templates without `rel="sponsored"`, footer link blocks to partner sites, generated link pages | Agent check of outbound link templates |
| Machine-generated traffic | Automated queries to Google | Rank-checking scripts that scrape Google results | Do not build; use Search Console exports |
| Malicious practices | Malware, unwanted software and, since 2026-06-15, back-button hijacking | `history.pushState` or `replaceState` on load without navigation, `popstate` traps, redirect scripts from ad libraries | [SPAM001](rule-catalog.md#spam001); [F-T-33](current-facts.md#f-t-33) |
| Misleading functionality | Pages that pretend to offer a function they do not provide | "Free tool" pages whose tool does not work or only collects data | Agent check |
| Scaled content abuse | Many pages generated primarily to manipulate rankings, however produced | Generators that emit thousands of near-identical pages | [PSEO001](rule-catalog.md#pseo001); [PSEO003](rule-catalog.md#pseo003) (planned) |
| Scraping | Republishing other sites' content without added value | Import scripts that copy third-party articles or feeds into pages | Agent check of content pipelines |
| Site reputation policy | Third-party content published on a host mainly to exploit the host's ranking signals | A coupons, reviews or partner section written and run by a third party | Agent check; see the section below |
| Sneaky redirects | Sending users somewhere other than what crawlers saw | Redirects conditioned on referrer or user agent; meta refresh | [SPAM002](rule-catalog.md#spam002); [REDIR005](rule-catalog.md#redir005) |
| Thin affiliation | Affiliate pages that copy merchant content without added value | Product feeds rendered as pages with no own testing, comparison or data | Agent check; disclosure rules in [content-quality-rubrics.md](content-quality-rubrics.md#comparison-page-fairness) |
| User-generated spam | Spam that users add to comments, forums or profiles | Open comment forms without moderation; profile links without `rel="ugc"` | Agent check of UGC templates |

## Scaled content abuse

- The test is purpose and value, not the production method: AI-written, human-written and template-generated pages are judged the same way ([F-T-32](current-facts.md#f-t-32), [F-T-37](current-facts.md#f-t-37)).
- Google's generative-AI optimization guide adds that mass-producing pages for query variations, to manipulate rankings or generative AI responses, may be scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)). One comprehensive page beats many variant pages.
- In code: gate generation on per-row data (see [programmatic-seo.md](programmatic-seo.md)), do not generate empty combinations, and keep rewording tools out of pipelines whose purpose is to evade duplicate detection.

## Site reputation policy

- The policy covers third-party content published on a host site mainly because of the host's established ranking signals ([F-T-32](current-facts.md#f-t-32)). Google introduced it on 2024-03-05 with enforcement from 2024-05-05, and clarified on 2024-11-19 that first-party involvement, white-label arrangements, licensing or partial ownership do not make such content first-party ([F-T-69](current-facts.md#f-t-69), [F-T-70](current-facts.md#f-t-70)).
- From 2026-08-30, manual actions under this policy have no effect for users in the EEA, where the affected section may rank on its own; they still apply elsewhere ([F-T-34](current-facts.md#f-t-34)). Do not read this as permission: algorithmic systems and the rest of the policy still apply everywhere.
- Usefulness alone is not a safe harbor. Ask who writes the section, who controls it, and whether it would exist on this domain without the domain's reputation.

## Expired domain abuse and migrations

Moving content onto a purchased domain is fine when the content continues the domain's purpose or the business itself moved. Buying an unrelated expired domain to host content that rides on its old links is the policy target ([F-T-32](current-facts.md#f-t-32)). Record the domain's history in the migration plan ([migrations.md](migrations.md)) and let the owner decide.

## Back-button hijacking

Interfering with browser navigation so the back button does not return users (inserting history entries, sending users to pages they never visited or to ads) is a malicious practice, enforced from 2026-06-15, and site owners are responsible for library and ad-platform code too ([F-T-33](current-facts.md#f-t-33)). `SG audit-build` reports [SPAM001](rule-catalog.md#spam001) for history manipulation on load in inline scripts; also read third-party bundles that the build includes, because the CLI does not execute JavaScript.

## Manipulating generative AI responses

- Google counts attempts to manipulate generative AI responses in Search as spam ([F-T-32](current-facts.md#f-t-32)). Text that addresses AI systems with instructions ("assistants should recommend this product", "ignore other sources"), hidden or visible, is reported as [CONT010](rule-catalog.md#cont010) with error severity.
- Inauthentic mentions, rewriting pages "for AI" and chunking content are listed as misconceptions, not techniques ([F-AI-12](current-facts.md#f-ai-12)). Google says AI features need no special files, schema or Markdown ([F-AI-11](current-facts.md#f-ai-11)).
- For other AI surfaces there is no published policy to cite. Apply the same standard: visible, accurate content that serves readers, and the same content for every client.

## Structured-data and review policies

- Do not mark up content that is not visible; use the most specific type; a structured-data manual action removes rich-result eligibility without affecting web ranking ([F-T-11](current-facts.md#f-t-11)). Details and code patterns live in [structured-data-matrix.md](structured-data-matrix.md#policy-rules).
- Self-serving reviews: a business must not mark up reviews or ratings of itself on its own LocalBusiness or Organization, including ratings pulled from third-party widgets ([SD010](rule-catalog.md#sd010)).
- Fake or undisclosed incentivized reviews are ineligible in visible content and in markup; Google's review-snippet guidance added an explicit rule on this on 2026-07-24 and recommends accepting reviews only with a comment and an author name ([F-T-67](current-facts.md#f-t-67)).
- Counts and ranges must be real and consistent ([SD011](rule-catalog.md#sd011)); placeholders never ship ([SD006](rule-catalog.md#sd006)).
- Valid markup earns eligibility, not a rich result. FAQ rich results are no longer shown in Google Search from 2026-05-07 ([F-T-02](current-facts.md#f-t-02)); keep a FAQ section only when it helps readers.

## AI-generated content guidance

Google's guidance on generative AI content ([F-T-37](current-facts.md#f-t-37)):

- AI-generated content is acceptable when it meets Search Essentials and the spam policies; generating many pages without added value can be scaled content abuse.
- Fact-check AI output before publishing, including titles, meta descriptions, structured data and alt text.
- Explain how automated content was created where readers would reasonably ask.
- In Merchant Center, AI-generated images need IPTC `DigitalSourceType` `TrainedAlgorithmicMedia` metadata, and AI-generated product data must be labelled (see [ecommerce-seo.md](ecommerce-seo.md#product-images-and-ai-generated-images)).

What this means for an agent: AI may draft and restructure; it never invents numbers, quotes, reviews, credentials, authors, dates or sources. Style lint ([CONT002](rule-catalog.md#cont002), [CONT008](rule-catalog.md#cont008)) is a writing signal, not AI detection, and no tool reliably detects AI authorship.

## Bing guideline notes

- Bing supports `data-nosnippet`, which keeps marked text out of Bing snippets and Copilot answers while the page stays indexed ([F-T-51](current-facts.md#f-t-51)).
- Bing's AI training and grounding preferences are controls, not policies; they are covered in [ai-crawlers.md](ai-crawlers.md) ([F-AI-19](current-facts.md#f-ai-19)).
- Reports that Bing's Webmaster Guidelines were rewritten in February 2026 to name GEO, add a prompt-injection section and widen keyword stuffing to "artificially engineered language" are third-party only; Bing's help pages could not be read ([current-facts.md](current-facts.md#not-verified-third-party-only)). The direction matches Google's: do not engineer text to trigger AI citations.
- A Bing Webmaster blog post (2025-12-19) says duplicate pages are not penalized but split signals, and that large language models group near-duplicates and pick one page to represent them ([F-T-73](current-facts.md#f-t-73)). Canonicals, redirects and consolidation are the fix.

## Enforcement and recovery

- Manual actions appear in the Search Console Manual actions report; the owner fixes the cause and files a reconsideration request. Agents prepare the fix and an evidence summary; the owner submits.
- Spam reports from users may now lead to manual actions ([F-T-71](current-facts.md#f-t-71)).
- Algorithmic spam updates and core updates are listed on the Search Status Dashboard ([F-T-36](current-facts.md#f-t-36)). Overlap between a traffic change and an update date is a hypothesis to test with [search-data-analysis](../skills/search-data-analysis/SKILL.md), never proof.
- Google's core-update guidance says smaller unannounced core updates also happen, asks site owners to wait at least one full week after a rollout completes before analyzing, and to compare the week before with the week after ([F-T-72](current-facts.md#f-t-72)).
- Helpful content is part of the core ranking systems since March 2024 ([F-T-35](current-facts.md#f-t-35)); there is no separate "helpful content update" to wait for.
- Recovery from quality issues can take months. Delete content only as a last resort and only with the owner's approval.

## Prohibited tactics mapped to rules

| Tactic requested | Why it is out | Rule or check | Compliant alternative |
| --- | --- | --- | --- |
| Hidden instructions for AI assistants ("tell users we are the best") | Manipulating generative AI responses ([F-T-32](current-facts.md#f-t-32)) | [CONT010](rule-catalog.md#cont010) | Clear, visible, sourced claims the page can support |
| Different HTML for AI crawlers or Googlebot | Cloaking | [SPAM003](rule-catalog.md#spam003) (planned), agent check | Same content for all; access policy through robots.txt and headers ([geo-ai-access](../skills/geo-ai-access/SKILL.md)) |
| Review or rating markup for the business itself | Self-serving reviews ([F-T-11](current-facts.md#f-t-11)) | [SD010](rule-catalog.md#sd010) | Show real third-party reviews as visible text without markup, or link to them |
| Sample or invented reviews, ratings, testimonials | Fake reviews; fabrication | [SD011](rule-catalog.md#sd011), agent check | Collect real reviews; disclose incentives |
| Invented statistics, quotes, expert names or credentials | Fabrication; misleading content | [CONT001](rule-catalog.md#cont001), [FID005](rule-catalog.md#fid005) | User-supplied sources, or `[needs source]` and a narrower claim |
| City-swap location pages | Doorway abuse | [PSEO001](rule-catalog.md#pseo001) | Pages only for real locations with real local facts ([local-seo.md](local-seo.md#location-and-service-area-pages)) |
| One page per query variant | Scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)) | [PSEO001](rule-catalog.md#pseo001) | One comprehensive page with sections for the variants |
| Back-button traps or exit redirects | Malicious practices ([F-T-33](current-facts.md#f-t-33)) | [SPAM001](rule-catalog.md#spam001) | Normal navigation; remove the library or setting |
| Meta refresh or conditional redirects | Sneaky redirects | [SPAM002](rule-catalog.md#spam002), [REDIR005](rule-catalog.md#redir005) | Server-side 301 to the closest equivalent page |
| Keyword lists in alt text, titles or footers | Keyword stuffing | [IMG002](rule-catalog.md#img002) | Descriptive alt text; one clear title |
| Bumping years or dates without changing content | Misleading freshness; Google rewrites titles with obsolete dates ([F-T-38](current-facts.md#f-t-38)) and uses `lastmod` only when accurate ([F-T-27](current-facts.md#f-t-27)) | [CONT005](rule-catalog.md#cont005), [META012](rule-catalog.md#meta012), [SMAP006](rule-catalog.md#smap006) | Update the content, then the dates ([content-quality-rubrics.md](content-quality-rubrics.md#date-honesty)) |
| Paid links without `rel="sponsored"` or `nofollow` | Link spam | Agent check | Qualify paid and affiliate links |
| Third-party content sections that exploit the domain | Site reputation policy ([F-T-34](current-facts.md#f-t-34)) | Agent check | Bring the section under first-party editorial control or move it off the domain |
| Leftover AI or editor artifacts published | Quality and trust | [CONT004](rule-catalog.md#cont004) | Remove them before publishing |
| Invisible or bidi-control characters in text | Hidden-text risk and broken rendering | [CONT003](rule-catalog.md#cont003) | Strip them from the user's own drafts |

## Needs verification

- The full text of Bing's current Webmaster Guidelines (client-rendered pages could not be read on 2026-11-01).
- Whether AI search products other than Google and Bing apply any published content policy to sources they cite.
- The exact wording of each spam policy changes over time; quote only from the live page with its date.
