<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: per-surface control table, cross-surface principles, query-type structures and entity-signal categories rewritten in our own words against 2026-11-01 vendor documentation, with fact IDs, measurement notes and explicit gaps added. See NOTICE.md. -->
# AI answer surfaces

What each AI answer surface documents about eligibility, publisher controls and measurement, and what it does not document. Use it to answer "how do we appear in X" or "how do we keep out of X" without inventing rules. Crawler tokens and their verification are in [ai-crawlers.md](ai-crawlers.md); measurement method is in [measurement-protocol.md](measurement-protocol.md).

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Name the surface exactly in every report: Google AI Overviews, Google AI Mode, the Gemini app, ChatGPT search, Perplexity, Microsoft Copilot and Bing, Claude, Meta AI, Apple, Amazon, DuckDuckGo and Mistral are different products with different controls. Chrome Lighthouse is a lab tool, not a search surface.

## How to use this reference

- Eligibility is never selection. Meeting every documented requirement makes a page usable; it does not make an engine cite it, and no vendor promises citations.
- If a provider publishes no crawler, index or publisher-control contract for a behavior, record the gap. Do not reverse-engineer a durable rule from one answer, one referral or one screenshot.
- Separate three questions for every surface: can it fetch the page (access), may it use the page (controls), and does it cite the page (measured outcome).
- Third-party citation-share and click studies are vendor research; see [geo-research-evidence.md](geo-research-evidence.md) for how to label them.

## Summary table

| Surface | Fetch and index | Publisher controls | Measurement available to the site owner |
| --- | --- | --- | --- |
| Google AI Overviews and AI Mode | Googlebot (Google Search index) | `noindex`, `nosnippet`, `max-snippet`, `data-nosnippet`, Search Console "Search generative AI" setting | Search Console totals and generative-AI reports; GA4 Organic Search |
| Gemini app | Google systems; grounding governed by Google-Extended | `Google-Extended` (and `__usage_ai-training` from early 2027) | GA4 AI Assistant channel; referrers |
| ChatGPT search | OAI-SearchBot; ChatGPT-User for user visits | robots.txt per token | `utm_source=chatgpt.com` (needs verification); GA4; referrers; prompt panels |
| Perplexity | PerplexityBot; Perplexity-User for user fetches | robots.txt for PerplexityBot; WAF for Perplexity-User | Referrers; prompt panels |
| Microsoft Copilot and Bing | bingbot | Bingbot `ai-training` and `ai-grounding` directives (from 2027-02-01), `data-nosnippet` | Bing Webmaster Tools AI Performance; GA4 |
| Claude | Claude-SearchBot; Claude-User; ClaudeBot for training | robots.txt per token | Referrers; prompt panels |
| Meta AI | meta-webindexer; meta-externalfetcher; meta-externalagent for training | robots.txt per token | Referrers; prompt panels |
| Apple (Siri, Spotlight, Safari) | Applebot | `Applebot` and `Applebot-Extended` groups | None documented for AI answers |
| Amazon (Alexa and Amazon AI) | Amazonbot, Amzn-SearchBot, Amzn-User | robots.txt per token; `noarchive` as no-training for Amazonbot | None documented |
| DuckDuckGo AI answers | DuckAssistBot | robots.txt | Referrers |
| Mistral | MistralAI-Index, MistralAI-User, MistralAI-Training | robots.txt per token | Referrers |

## Google AI Overviews and AI Mode

- **Eligibility.** A page must be indexed and eligible to show with a snippet; there are no additional technical requirements, special files, schema or Markdown ([F-AI-11](current-facts.md#f-ai-11)). The site must also be included through the Search Console "Search generative AI" setting, which defaults to Include ([F-AI-09](current-facts.md#f-ai-09)).
- **Controls.** Googlebot access and indexability; `noindex`; `nosnippet` (no direct AI input); `max-snippet` (limits AI input); `data-nosnippet` on elements ([F-AI-10](current-facts.md#f-ai-10)); the Search Console setting set to Exclude for the whole property ([F-AI-09](current-facts.md#f-ai-09)). Google-Extended does not control these features ([F-AI-06](current-facts.md#f-ai-06)).
- **Measurement.** AI Mode traffic counts in Search Console Performance totals under the "Web" search type ([F-T-50](current-facts.md#f-t-50)). The generative-AI performance reports show impressions by page, country, device and date, with no API mentioned ([F-AI-13](current-facts.md#f-ai-13)); reports that they lack clicks and queries are third-party. In GA4, AI Overviews and AI Mode visits stay in Organic Search ([F-AI-30](current-facts.md#f-ai-30)). Independent research found fewer result clicks when an AI summary appears ([F-AI-33](current-facts.md#f-ai-33)).
- **Documented guidance.** Google's generative-AI optimization guide says optimizing for generative AI search is still SEO and lists misconceptions: llms.txt, chunking, rewriting for AI, inauthentic mentions, over-focus on structured data and AEO/GEO hacks; mass pages for query variants can be scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)). Spam policies cover manipulating generative AI responses ([F-T-32](current-facts.md#f-t-32)). Helpful, people-first content is part of core ranking ([F-T-35](current-facts.md#f-t-35)). Preferred-source badges appear in AI Mode and AI Overviews for users who chose the site ([F-AI-14](current-facts.md#f-ai-14)).
- **Not documented.** How sources are chosen among eligible pages, how often a page is cited, and click-through from links inside AI answers in Search Console. Do not infer these from rankings or a handful of answers.

## Gemini app

- **Controls.** Google-Extended governs Gemini training and grounding in Gemini Apps and Vertex AI ([F-AI-06](current-facts.md#f-ai-06)). The Search Console generative-AI setting does not cover the Gemini app ([F-AI-09](current-facts.md#f-ai-09)). From early 2027 an opt-out through `__usage_ai-training` counts as a Google-Extended disallow when no Google-Extended rule exists ([F-AI-07](current-facts.md#f-ai-07)).
- **Measurement.** GA4's AI Assistant channel names Gemini among its examples ([F-AI-30](current-facts.md#f-ai-30)); `gemini.google.com` referrers are third-party reports to confirm in your own data.
- **Not documented.** How the Gemini app selects or ranks sources. Measure it as its own surface, separate from AI Overviews and AI Mode.

## ChatGPT search

- **Eligibility and controls.** OAI-SearchBot decides inclusion in ChatGPT search answers; a site that disallows it is not shown in answers, though it can still appear as a navigational link ([F-AI-02](current-facts.md#f-ai-02)). GPTBot (training) is independent, and ChatGPT-User visits do not decide search eligibility; robots.txt changes take about 24 hours ([F-AI-01](current-facts.md#f-ai-01)).
- **Measurement.** ChatGPT is reported to append `utm_source=chatgpt.com` to referral URLs ([F-AI-03](current-facts.md#f-ai-03), needs verification). GA4's AI Assistant channel names ChatGPT ([F-AI-30](current-facts.md#f-ai-30)). In-app and copied links can arrive without a referrer, so counts are a floor. No OpenAI publisher citation report was found.
- **Not documented here.** Which search providers or indexes ChatGPT search combines; OpenAI's publisher help pages could not be read in the research pass. Do not tell users that Bing indexation decides ChatGPT visibility.

## Perplexity

- **Controls.** PerplexityBot crawls for Perplexity search and is not used for foundation-model training; Perplexity-User fetches for a user's question and generally ignores robots.txt ([F-AI-05](current-facts.md#f-ai-05)). Use WAF rules based on Perplexity's published IP lists if Perplexity-User must be blocked.
- **Measurement.** `perplexity.ai` referrers (verify in your own data); prompt panels. GA4's AI Assistant channel page does not name Perplexity (needs verification).
- **Not documented.** A publisher program or citation report. Reports about undeclared crawling are a disputed third-party matter; do not assert either side.

## Microsoft Copilot and Bing

- **Controls.** bingbot crawls for Bing search and for grounding Copilot answers. From 2027-02-01 Bing honors `ai-training` and `ai-grounding` page preferences and the shared training token; after 2027-03-01 NOARCHIVE and NOCACHE stop being AI signals ([F-AI-19](current-facts.md#f-ai-19)). `data-nosnippet` keeps marked text out of Bing snippets and Copilot answers ([F-T-51](current-facts.md#f-t-51)).
- **Discovery.** Bing treats sitemap `lastmod` as a key signal and pairs sitemaps with IndexNow ([F-T-52](current-facts.md#f-t-52)); IndexNow is supported by Bing and other engines, not Google ([F-AI-21](current-facts.md#f-ai-21)).
- **Measurement.** Bing Webmaster Tools AI Performance (public preview) shows citations, cited pages and sampled grounding queries for Copilot, Bing AI summaries and select partners ([F-AI-20](current-facts.md#f-ai-20)); the Bing Webmaster API has no AI Performance method, so use UI exports ([F-T-53](current-facts.md#f-t-53)). GA4's AI Assistant channel names Copilot ([F-AI-30](current-facts.md#f-ai-30)).
- **Needs verification.** Third-party reports say Bing's February 2026 guideline rewrite names GEO, says it does not guarantee citations, adds a prompt-injection section and expands keyword stuffing to "artificially engineered language". Treat as unconfirmed until the guideline page is read.

## Claude

- **Controls.** Claude-SearchBot (search indexing), Claude-User (fetches for a user's request) and ClaudeBot (training) are separate and all honor robots.txt and Crawl-delay ([F-AI-04](current-facts.md#f-ai-04)). Allowing ClaudeBot alone is not a search-visibility control, and blocking Claude-User stops retrieval for user requests.
- **Measurement.** `claude.ai` referrers (verify in your own data); prompt panels. GA4's AI Assistant channel page does not name Claude (needs verification).
- **Not documented.** Which search index backs Claude's web search, and any Claude-specific publisher program. Do not assume a fixed backend.

## Meta AI

- **Controls.** meta-webindexer (Meta AI search citations), meta-externalagent (training or product indexing), meta-externalfetcher (user fetches that may bypass robots.txt) ([F-AI-36](current-facts.md#f-ai-36)). Meta publishes no IP ranges for them.
- **Measurement.** `meta.ai` referrers (third-party; verify). No publisher report found.

## Apple

- **Controls.** Applebot powers Spotlight, Siri and Safari search and its data may also train Apple models; Applebot-Extended controls training use only and does not crawl; Applebot follows Googlebot rules when no Applebot group exists ([F-AI-35](current-facts.md#f-ai-35)). Disallowing Applebot-Extended does not remove the site from Siri or Spotlight.
- **Measurement.** None documented for AI features.

## Amazon

- **Controls.** Amazonbot (mixed use; honors `noarchive` as "no model training"), Amzn-SearchBot (search experiences such as Alexa; not training) and Amzn-User (user fetches) ([F-AI-37](current-facts.md#f-ai-37)). To opt out of Amazon training while staying in Amazon features, prefer the documented `noarchive` signal or the specific tokens over blocking Amazonbot outright.
- **Measurement.** None documented.

## DuckDuckGo

- **Controls.** DuckAssistBot fetches in real time for DuckDuckGo AI answers, is not used for training, and opting out does not affect DuckDuckGo rankings ([F-AI-38](current-facts.md#f-ai-38)).
- **Measurement.** Referrers only.

## Mistral

- **Controls.** MistralAI-User (user fetches, governed by robots.txt), MistralAI-Index (index, not training), MistralAI-Training (training) ([F-AI-39](current-facts.md#f-ai-39)).
- **Measurement.** `chat.mistral.ai` referrers (third-party; verify).

## Other surfaces (needs verification)

These rows come from the adapted source's 2026-07-30 review and were not re-verified in the 2026-11-01 research pass. Read the URL before quoting them.

| Surface | Reported behavior | Source |
| --- | --- | --- |
| Brave Search | Independent index; crawler has no distinct user agent; does not crawl pages Googlebot may not crawl; delists on `noindex` after re-fetch | https://search.brave.com/help/brave-search-crawler |
| Gemini API grounding with Google Search | A developer API whose responses carry citation annotations; separate from Google Search eligibility | https://ai.google.dev/gemini-api/docs/google-search |
| Copilot Studio public-web grounding | Uses Bing Custom Search for configured sources; scoped to Copilot Studio, not every Copilot product | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites |

## Cross-surface principles

Defensible practices that help readers on every surface. No principle here is a documented ranking or citation factor, and no format guarantees selection.

| Principle | In practice |
| --- | --- |
| Correctness and provenance | Material claims link named, dated primary sources; measured facts are distinguished from estimates and opinion |
| Original value | First-hand evidence, real examples, expert analysis or a genuinely useful synthesis instead of restated commodity text |
| Retrievability | Important content is server-rendered text; robots.txt, snippet controls, authentication, CDN and WAF match the intended surfaces ([seo-rendering](../skills/seo-rendering/SKILL.md), [ai-crawlers.md](ai-crawlers.md)) |
| Reader-first structure | Headings, lists, tables, definitions and steps where they help comprehension, not to meet a quota |
| Freshness with substance | Visible dates when time matters; update the evidence, not only the timestamp |
| Surface-specific measurement | Record query, locale, account state, device, date, cited URL and cited statement, repeated over time ([measurement-protocol.md](measurement-protocol.md)) |

## Reader-first structures by query type

| Query type | What the reader needs | Structure that serves it |
| --- | --- | --- |
| Definition ("what is", "what does") | Correct scope and meaning | One-sentence definition naming the subject and its category, then mechanism, examples and limits |
| Comparison ("X vs Y", "best for") | Consistent criteria | Comparable table with units and visible unknowns, trade-offs, "choose X when" conditions, sourced facts |
| How-to ("how to", "steps") | Safe completion | Prerequisites, ordered steps, verification, troubleshooting, version notes |
| Statistical ("how much", "how many") | Traceable numbers | The figure with its source, date, denominator and method, then caveats |
| Troubleshooting | A fix for a specific symptom | Symptom, cause, fix, how to confirm, what not to do |

Answer at the length the question needs. There is no documented universal word count for citation; any word band in this plugin is a house heuristic ([citability-and-rewrite.md](citability-and-rewrite.md)).

## Entity signals across surfaces

AI answers that describe an organization wrongly usually reflect weak or inconsistent identity signals, not a missing file. Work through these categories in order; keep "unknown" distinct from "partial" and "missing".

| Category | What to check | Owner of the fix |
| --- | --- | --- |
| On-site identity | Organization (or Person) JSON-LD on the home page with one stable `@id`, `name`, `url`, `logo`; an About page and a contact page that match; author pages for real authors | [geo-entity-authority](../skills/geo-entity-authority/SKILL.md), mechanics in [structured-data-matrix.md](structured-data-matrix.md#entity-graph-pattern) |
| Consistent definition | One factual sentence describing the entity, reused unchanged on the home page, About page, README, app store and directory listings | geo-entity-authority |
| Verified profiles | `sameAs` only to profiles the owner confirms they control or that verifiably describe the entity | geo-entity-authority |
| Knowledge bases | An existing Wikidata item verified to describe the entity; notability rests on independent reliable sources; editing about yourself follows conflict-of-interest rules | owner, with disclosure |
| Third-party corroboration | Independent coverage, reviews on third-party platforms, citations by sources the surfaces already cite | owner and communications, never fabricated |
| Recognition checks | How each surface describes the entity today, recorded per surface and date in the ledger; unobserved is unknown | [seo-geo-measurement](../skills/seo-geo-measurement/SKILL.md) |

Rules: never merge two identities because names, logos or domains look alike; never guess `sameAs`; populate markup only from values the owner confirmed, and ask for missing required values instead of guessing.

## Needs verification

- Whether GA4's internal AI assistant list includes Perplexity and Claude.
- Which referrer each AI app, mobile app and AI browser sends.
- Search Console generative-AI report limits (clicks, queries, start date).
- Bing's February 2026 guideline rewrite.
- The three "other surfaces" rows above.
