<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: crawler matrix, policy modes, search-only starter and edge-override check rewritten against 2026-11-01 vendor documentation, merged with MIT-licensed material and extended with the shared training token, Content Signals and Bing directives. See NOTICE.md. -->
# AI crawlers, agents and training controls

Which bots fetch a site for AI search answers, model training, user-requested retrieval or agent actions; which robots.txt token, page directive, header or dashboard setting controls each use; what blocking each one costs in visibility; and how to verify who actually visited. This is the reference behind [geo-ai-access](../skills/geo-ai-access/SKILL.md) and the AI rules in the CLI (AI001 to AI015). Search-crawler mechanics for Googlebot and Bingbot (grouping, longest match, status codes) live in [robots-and-directives.md](robots-and-directives.md).

As of 2026-11-01. Every vendor statement cites a fact in [current-facts.md](current-facts.md); rows labelled 3P or "needs verification" are not confirmed by the vendor. The machine-readable copy of the token table is `data/ai-crawlers.json`, printed by `SG crawlers` (`SG` is `python3 -I <plugin-root>/scripts/seo_geo.py`).

## Purpose classes

Report every decision per class. Visibility impact and training impact are separate lines in every report; never merge them.

| Class | What the bot does | Disallowing it | Honors robots.txt |
| --- | --- | --- | --- |
| TRAIN | Collects content to train or fine-tune models | Affects training use only, not search or answer inclusion | Yes for the documented vendors |
| INDEX | Builds a search or answer index that an AI product cites | Removes or reduces the site in that product's answers | Yes for the documented vendors |
| USER | Fetches a URL because a person asked an assistant to | Stops that live retrieval where it is honored; some vendors say robots.txt may not apply | Often no or partial |
| AGENT | A browser agent that navigates and acts for a person | Usually not honored; use server or WAF rules | Generally no |
| ADS | Reviews ad landing pages | Can break ad review for that vendor | Not stated |
| PREVIEW | Fetches link previews for shared URLs | Breaks link cards in chat and social apps | Partial |
| MIXED | One crawler serves classic search and AI features | Removes the site from that vendor's search as well as its AI features | Yes |
| CONTROL | A robots.txt token with no crawler of its own (training controls, legacy names, the shared policy token) | Expresses a preference to crawlers that read the token | Token only |
| CORPUS | Builds an open web corpus that third parties reuse, including for training | Removes the site from future corpus snapshots | Yes |

## Token table

Tokens are matched case-insensitively. "Verify" lists the vendor's published IP list or reverse-DNS pattern; a user-agent string alone proves nothing.

| Token | Vendor | Class | Purpose | robots.txt | Verify | Fact |
| --- | --- | --- | --- | --- | --- | --- |
| GPTBot | OpenAI | TRAIN | Content for training foundation models | Honored; about 24 hours to take effect | https://openai.com/gptbot.json | [F-AI-01](current-facts.md#f-ai-01) |
| OAI-SearchBot | OpenAI | INDEX | Inclusion in ChatGPT search answers | Honored; about 24 hours | https://openai.com/searchbot.json | [F-AI-01](current-facts.md#f-ai-01), [F-AI-02](current-facts.md#f-ai-02) |
| ChatGPT-User | OpenAI | USER | Visits for ChatGPT users, custom GPTs and actions; not used for search eligibility | "May not apply" | https://openai.com/chatgpt-user.json | [F-AI-01](current-facts.md#f-ai-01) |
| OAI-AdsBot | OpenAI | ADS | Ad landing-page review; not used for training | Not stated | https://openai.com/adsbot.json | [F-AI-01](current-facts.md#f-ai-01) |
| ClaudeBot | Anthropic | TRAIN | Training data | Honored, including Crawl-delay | https://claude.com/crawling/bots.json | [F-AI-04](current-facts.md#f-ai-04) |
| Claude-SearchBot | Anthropic | INDEX | Search indexing for Claude answers | Honored | https://claude.com/crawling/bots.json | [F-AI-04](current-facts.md#f-ai-04) |
| Claude-User | Anthropic | USER | Fetches for a Claude user's request; blocking it stops that retrieval | Honored | https://claude.com/crawling/bots.json | [F-AI-04](current-facts.md#f-ai-04) |
| PerplexityBot | Perplexity | INDEX | Perplexity search results; not used for foundation-model training | Honored | https://www.perplexity.ai/perplexitybot.json | [F-AI-05](current-facts.md#f-ai-05) |
| Perplexity-User | Perplexity | USER | Fetches for a user's question | Generally ignored | https://www.perplexity.ai/perplexity-user.json | [F-AI-05](current-facts.md#f-ai-05) |
| Googlebot | Google | MIXED | Google Search, including the index that AI Overviews and AI Mode draw on | Honored | Google's published IP ranges and reverse DNS | [F-AI-11](current-facts.md#f-ai-11), [F-T-18](current-facts.md#f-t-18) |
| Google-Extended | Google | CONTROL | Gemini model training and grounding in Gemini Apps and Vertex AI; no effect on Google Search inclusion or ranking | Token only | n/a (no crawler) | [F-AI-06](current-facts.md#f-ai-06) |
| GoogleOther | Google | MIXED | Generic crawler for Google product teams and research; no Search effect (also `GoogleOther-Image`, `GoogleOther-Video`) | Honored | Google IP ranges | [F-AI-41](current-facts.md#f-ai-41) |
| Google-CloudVertexBot | Google | INDEX | Crawls that a site owner requests for Vertex AI Agents; no Search effect | Honored | Google IP ranges | [F-AI-41](current-facts.md#f-ai-41) |
| Google-Agent | Google | AGENT | Agents on Google infrastructure that browse and act on a user's request; Web Bot Auth experiment as `https://agent.bot.goog` | Generally ignored | user-triggered-agents IP file | [F-AI-08](current-facts.md#f-ai-08) |
| Google-GeminiNotebook | Google | USER | Fetches sources a user adds (formerly `Google-NotebookLM`; also `Google-Pinpoint`, `Google-Read-Aloud` among Google's user-triggered fetchers) | Generally ignored | user-triggered-fetchers IP files | [F-AI-42](current-facts.md#f-ai-42) |
| Applebot | Apple | MIXED | Spotlight, Siri and Safari search; data may also train Apple models; follows Googlebot rules when it has no group | Honored; Crawl-delay ignored | Reverse DNS `*.applebot.apple.com` | [F-AI-35](current-facts.md#f-ai-35) |
| Applebot-Extended | Apple | CONTROL | Training-use control for content Applebot already fetched; does not crawl | Token only | n/a | [F-AI-35](current-facts.md#f-ai-35) |
| bingbot | Microsoft | MIXED | Bing search and grounding for Copilot answers | Honored; page-level AI preferences from 2027-02-01 | Bing verification (method not re-checked) | [F-AI-19](current-facts.md#f-ai-19) |
| meta-externalagent | Meta | TRAIN | Training or product indexing | Can be disallowed | No IP ranges published | [F-AI-36](current-facts.md#f-ai-36) |
| meta-webindexer | Meta | INDEX | Meta AI search citations | Honored | No IP ranges published | [F-AI-36](current-facts.md#f-ai-36) |
| meta-externalfetcher | Meta | USER | Fetches for a user | May bypass robots.txt | No IP ranges published | [F-AI-36](current-facts.md#f-ai-36) |
| meta-externalads | Meta | ADS | Ad review | Partial | No IP ranges published | [F-AI-43](current-facts.md#f-ai-43) |
| facebookexternalhit | Meta | PREVIEW | Link previews; may bypass robots.txt for integrity checks | Partial | No IP ranges published | [F-AI-43](current-facts.md#f-ai-43) |
| Amazonbot | Amazon | MIXED | Amazon products and services; may train Amazon AI; honors `noarchive` as "no model training" | Honored; Crawl-delay ignored | developer.amazon.com/amazonbot/ip-addresses/ | [F-AI-37](current-facts.md#f-ai-37) |
| Amzn-SearchBot | Amazon | INDEX | Search experiences such as Alexa; not training | Honored | developer.amazon.com/amazonbot/searchbot-ip-addresses/ | [F-AI-37](current-facts.md#f-ai-37) |
| Amzn-User | Amazon | USER | Fetches for a user; not training | Partial | developer.amazon.com/amazonbot/live-ip-addresses/ | [F-AI-37](current-facts.md#f-ai-37) |
| DuckAssistBot | DuckDuckGo | USER | Real-time fetches for DuckDuckGo AI answers; not used for training; opting out does not affect DuckDuckGo rankings | Honored | https://duckduckgo.com/duckassistbot.json | [F-AI-38](current-facts.md#f-ai-38) |
| MistralAI-User | Mistral | USER | Fetches for Mistral users | Honored ("robots.txt governs") | https://mistral.ai/mistralai-user-ips.json | [F-AI-39](current-facts.md#f-ai-39) |
| MistralAI-Index | Mistral | INDEX | Index for Mistral answers; not training | Not described | https://mistral.ai/mistralai-index-ips.json | [F-AI-39](current-facts.md#f-ai-39) |
| MistralAI-Training | Mistral | TRAIN | Training | Can be disallowed | Not listed | [F-AI-39](current-facts.md#f-ai-39) |
| CCBot | Common Crawl | CORPUS | Open web corpus that third parties widely reuse for training | Honored | Reverse DNS `*.crawl.commoncrawl.org`; https://index.commoncrawl.org/ccbot.json | [F-AI-40](current-facts.md#f-ai-40) |
| Bytespider | ByteDance | TRAIN | ByteDance products (3P) | Compliance disputed (3P) | None found | 3P, [needs verification](current-facts.md#not-verified-third-party-only) |
| cohere-ai | Cohere | TRAIN | Unclear; sources conflict (3P) | Unclear | None found | 3P, [needs verification](current-facts.md#not-verified-third-party-only) |
| cohere-training-data-crawler | Cohere | TRAIN | Unclear; sources conflict (3P) | Unclear | None found | 3P, [needs verification](current-facts.md#not-verified-third-party-only) |
| anthropic-ai | Anthropic | CONTROL | Legacy token (3P); not listed on Anthropic's current page | Keep only if already present | n/a | 3P, needs verification |
| Claude-Web | Anthropic | CONTROL | Legacy token (3P); not listed on Anthropic's current page | Keep only if already present | n/a | 3P, needs verification |
| `__usage_ai-training` | Policy token | CONTROL | Shared AI-training preference; not a crawler | Preference; `User-agent: *` never matches it | n/a | [F-AI-17](current-facts.md#f-ai-17), [F-AI-18](current-facts.md#f-ai-18) |

ChatGPT agent reportedly signs requests with `Signature-Agent: "https://chatgpt.com"`; that comes from third parties, not OpenAI's bots page (needs verification). No crawler documentation was reviewed for xAI, DeepSeek, You.com, Yandex or Baidu AI products; report them as "not researched", not as safe.

Vendor timing and fallback details: Amazonbot caches robots.txt for up to 30 days and Amzn-SearchBot follows other search bots' rules when not named ([F-AI-44](current-facts.md#f-ai-44)); Perplexity robots.txt changes take up to 24 hours ([F-AI-45](current-facts.md#f-ai-45)); a DuckAssistBot opt-out takes up to 72 hours ([F-AI-46](current-facts.md#f-ai-46)).

## Claim to token table

Check the token that governs the claim, and report it by name.

| Claim to make or check | Token to check | Token that does not support it | Fact |
| --- | --- | --- | --- |
| "Pages can be cited in ChatGPT search" | `OAI-SearchBot` | `GPTBot` (not a search crawler) | [F-AI-01](current-facts.md#f-ai-01), [F-AI-02](current-facts.md#f-ai-02) |
| "Content is available for OpenAI training" | `GPTBot` | `OAI-SearchBot` | [F-AI-01](current-facts.md#f-ai-01) |
| "Pages can appear in Google AI Overviews or AI Mode" | `Googlebot`, plus snippet controls and the Search Console setting | `Google-Extended` (does not control AI Overviews or AI Mode) | [F-AI-06](current-facts.md#f-ai-06), [F-AI-09](current-facts.md#f-ai-09), [F-AI-10](current-facts.md#f-ai-10) |
| "Content may train Gemini or ground Gemini app answers" | `Google-Extended` | `Googlebot` | [F-AI-06](current-facts.md#f-ai-06) |
| "Pages can be cited in Claude's search" | `Claude-SearchBot` | `ClaudeBot` | [F-AI-04](current-facts.md#f-ai-04) |
| "Content is available for Anthropic training" | `ClaudeBot` | `Claude-SearchBot` | [F-AI-04](current-facts.md#f-ai-04) |
| "Pages can appear in Perplexity answers" | `PerplexityBot` (Perplexity-User may fetch regardless) | `Perplexity-User` alone | [F-AI-05](current-facts.md#f-ai-05) |
| "Pages can appear in Siri, Spotlight or Safari search" | `Applebot` | `Applebot-Extended` | [F-AI-35](current-facts.md#f-ai-35) |
| "Content is out of Apple model training" | `Applebot-Extended` | `Applebot` | [F-AI-35](current-facts.md#f-ai-35) |
| "Pages can ground Copilot answers" | `bingbot` plus the `ai-grounding` page preference | robots.txt alone (no grounding control there) | [F-AI-19](current-facts.md#f-ai-19) |
| "Pages can be cited by Meta AI search" | `meta-webindexer` | `meta-externalagent` | [F-AI-36](current-facts.md#f-ai-36) |

## Visibility and training impact

- Disallowing OAI-SearchBot, Claude-SearchBot, PerplexityBot, Amzn-SearchBot, MistralAI-Index, meta-webindexer, DuckAssistBot, Googlebot or bingbot reduces AI-answer visibility ([AI001](rule-catalog.md#ai001); Googlebot and bingbot also remove the site from classic search, [AI004](rule-catalog.md#ai004)).
- Disallowing GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, meta-externalagent, MistralAI-Training or CCBot affects training use only, not search inclusion ([AI002](rule-catalog.md#ai002)). CCBot feeds a third-party corpus that many parties reuse.
- Google-Extended is the one exception worth spelling out: disallowing it also stops grounding in the Gemini app and Vertex AI, and it does not affect Google Search, AI Overviews or AI Mode ([F-AI-06](current-facts.md#f-ai-06)).
- User-triggered fetchers (ChatGPT-User, Perplexity-User, Google-Agent and Google's other user-triggered fetchers, meta-externalfetcher, Amzn-User) are documented as not, or not reliably, bound by robots.txt ([AI003](rule-catalog.md#ai003)). Blocking them needs server or WAF rules and also removes the site from live answers that fetch it.
- Leaving an AI search indexer blocked only through `User-agent: *` is not a decision anyone made ([AI014](rule-catalog.md#ai014)); name each indexer and record the owner's choice.
- Crawl-delay is honored by Anthropic, ignored by Apple and Amazon ([F-AI-04](current-facts.md#f-ai-04), [F-AI-35](current-facts.md#f-ai-35), [F-AI-37](current-facts.md#f-ai-37)) and unsupported by Google ([F-T-18](current-facts.md#f-t-18)).
- Do not IP-block a crawler whose robots.txt preferences you want honored: a blocked crawler cannot read robots.txt.

## Policy modes

The owner chooses the mode. Explain the visibility impact and the training impact separately before any edit, and show the exact diff for approval.

| Mode | AI search and answer indexers | User fetchers | Training crawlers and tokens | Classic search | Template |
| --- | --- | --- | --- | --- | --- |
| `open` | Allowed, named explicitly | Allowed | Allowed, named explicitly | Allowed | [search-and-ai-open.txt](../templates/robots/search-and-ai-open.txt) |
| `search-only-no-training` | Allowed, named explicitly | Allowed | Disallowed, plus `__usage_ai-training` | Allowed | [search-only-no-training.txt](../templates/robots/search-only-no-training.txt) |
| `closed-to-ai` | Disallowed | Disallowed (and WAF rules where they ignore robots.txt) | Disallowed, plus `__usage_ai-training` | Allowed | [closed-to-ai.txt](../templates/robots/closed-to-ai.txt) |
| `custom` | Per token | Per token | Per token | Allowed unless the owner says otherwise | start from the closest template |

Questions to put to the owner before choosing:

1. Should the site appear in AI answers (ChatGPT search, Claude, Perplexity, Copilot, Google AI features)? Which ones?
2. May vendors train models on the content? Is any content licensed, paywalled or rights-reserved?
3. Should Google AI Overviews and AI Mode be excluded while classic Google Search stays? (That is the Search Console setting or snippet controls, not robots.txt.)
4. Is a CDN or WAF in front of the site, and who controls its bot settings?

The search-only pattern must keep `Claude-SearchBot` and `Claude-User` allowed while blocking `ClaudeBot`, and the same split for every vendor; otherwise a training opt-out silently removes the site from that vendor's answers. Every template parses with the bundled robots parser; check the adapted file with `SG robots public/robots.txt --bots all`.

## AIPREF training token

The individual IETF draft draft-kelley-aipref-training-preference-signal-00 (2026-10-30) defines `__usage_ai-training` as a robots.txt policy token with no new grammar ([F-AI-17](current-facts.md#f-ai-17)):

```text
User-agent: __usage_ai-training
Disallow: /
Allow: /press-kit/
```

- `Disallow` expresses a preference against training; `Allow` expresses a preference in favor; no group means no preference. RFC 9309 longest match applies to paths ([F-AI-52](current-facts.md#f-ai-52)).
- `User-agent: *` must never be read as matching the token ([AI008](rule-catalog.md#ai008)). A `Disallow: /` under `*` says nothing about training.
- It is not a crawling directive and not access control. Crawler-specific groups stay independent, so keep GPTBot, ClaudeBot, Google-Extended and similar groups alongside it.
- Commitments as of 2026-11-01 ([F-AI-18](current-facts.md#f-ai-18)): Anthropic has started implementing; Google plans early 2027 and treats an opt-out through the token as a Google-Extended disallow when the site sets no Google-Extended rule ([F-AI-07](current-facts.md#f-ai-07)); Bing honors it from 2027-02-01 ([F-AI-19](current-facts.md#f-ai-19)); OpenAI has announced support without a confirmed date (snippet only). No statement was found from Perplexity, Meta, Apple, Amazon, ByteDance or Common Crawl.
- The CLI reports the token's presence with its scope and dates ([AI007](rule-catalog.md#ai007)).

The AIPREF working group's vocabulary draft (draft-ietf-aipref-vocab-08) defines `train-ai`, `ai-use` and `search` with `y` or `n`; it is a draft, not an RFC ([F-AI-16](current-facts.md#f-ai-16)). Its HTTP attachment draft, draft-ietf-aipref-attach-05 ([F-AI-51](current-facts.md#f-ai-51)), is also a draft. Do not ship either as if it were a standard.

## Content Signals

Cloudflare's Content Signals Policy (CC0) adds a `Content-Signal:` line to robots.txt ([F-AI-22](current-facts.md#f-ai-22)):

```text
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=no
Allow: /
```

| Key | Meaning | Values |
| --- | --- | --- |
| `search` | Build a search index and show links and short excerpts (not AI summaries) | `yes`, `no` |
| `ai-input` | Use content as real-time input to AI answers (retrieval, grounding) | `yes`, `no` |
| `ai-train` | Train or fine-tune models | `yes`, `no` |
| `use` | Cloudflare test parameter (`immediate`, `reference` default, `full`) | testing |

- A signal is a stated preference, not access control; RFC 9309 parsers, including Google's, ignore the line. An absent signal means no preference. (Key definitions: [F-AI-48](current-facts.md#f-ai-48).)
- Signals sit inside a group. A crawler that matches a named group never reads the `*` group, so repeat the line in every named group ([AI006](rule-catalog.md#ai006)). Malformed lines or unknown keys are [AI005](rule-catalog.md#ai005).
- Cloudflare's managed robots.txt now emits `Content-signal: search=yes, ai-train=no, use=reference` ([F-AI-22](current-facts.md#f-ai-22)).
- Cloudflare Markdown for Agents adds `Content-Signal: ai-train=yes, search=yes, ai-input=yes` to Markdown responses when the origin sets none ([F-AI-25](current-facts.md#f-ai-25)). That can contradict a robots.txt `ai-train=no`; `SG access-check <origin> --live` reports it as [AI013](rule-catalog.md#ai013). Fix it by setting the header at the origin or in the Cloudflare configuration the owner controls.

## Bing directives

Bing separates training (changing model parameters) from grounding (using content as input to AI answers); both default to allow and are independent ([F-AI-19](current-facts.md#f-ai-19)).

| Goal | Page-level syntax (from 2027-02-01) | Header equivalent |
| --- | --- | --- |
| No training | `<meta name="Bingbot" content="ai-training:disallow">` | `X-Robots-Tag: Bingbot: ai-training:disallow` |
| No grounding in any Bing AI experience | `<meta name="Bingbot" content="ai-grounding:disallow">` | `X-Robots-Tag: Bingbot: ai-grounding:disallow` |
| No grounding in Microsoft-operated experiences | `<meta name="Bingbot" content="ai-grounding:disallowextended">` | `X-Robots-Tag: Bingbot: ai-grounding:disallowextended` |

- Training can also be expressed site-wide with `__usage_ai-training` in robots.txt; there is no robots.txt grounding control. Page-level training preferences override robots.txt.
- `disallowextended` covers only Microsoft-operated experiences including Copilot; the exclusion of Web IQ and the Foundry grounding API is stated in the same Bing post (V, 2026-10-30, no registry ID yet).
- Timeline: 2026-12-15 temporary grounding preferences open in Bing Webmaster Tools for sites using NOARCHIVE or NOCACHE; 2027-02-01 the new preferences take effect; after 2027-03-01 NOARCHIVE and NOCACHE are no longer read as AI signals; 2027-09-30 the temporary preferences expire ([F-AI-19](current-facts.md#f-ai-19)). Until 2027-03-01, third-party reports say NOARCHIVE keeps content out of Copilot grounding (needs verification). Google ignores both directives ([F-AI-10](current-facts.md#f-ai-10)); the CLI reports their use as [AI011](rule-catalog.md#ai011) and the new Bingbot directives as [AI012](rule-catalog.md#ai012).
- Disallowing grounding reduces Copilot visibility; Bing search eligibility is unaffected.
- Bing supports `data-nosnippet`, which keeps marked text out of Bing snippets and Copilot answers ([F-T-51](current-facts.md#f-t-51)).

## Google AI controls

| Lever | Scope | Effect | Fact |
| --- | --- | --- | --- |
| Googlebot allowed and page indexable | Site and page | Required for Google Search and therefore for AI Overviews and AI Mode; no special file or markup is needed | [F-AI-11](current-facts.md#f-ai-11) |
| `noindex` | Page | Removes the page from Google Search entirely | [F-T-20](current-facts.md#f-t-20) |
| `nosnippet` | Page | No snippet and no use as direct input for AI Overviews and AI Mode | [F-AI-10](current-facts.md#f-ai-10) |
| `max-snippet:[n]` | Page | Limits snippet length and the amount used as direct AI input | [F-AI-10](current-facts.md#f-ai-10) |
| `data-nosnippet` | Element | Excludes the marked text; structured data inside stays usable | [F-AI-10](current-facts.md#f-ai-10) |
| Search Console > Settings > "Search generative AI" | Property | Include, Exclude or Inherit for AI Overviews, AI Mode and Discover generative AI; not a ranking signal for the rest of Search; no training effect; worldwide since 2026-08-31 | [F-AI-09](current-facts.md#f-ai-09) |
| `Google-Extended` | Site (robots.txt) | Gemini training and grounding in Gemini Apps and Vertex AI only | [F-AI-06](current-facts.md#f-ai-06) |
| `__usage_ai-training` | Site (robots.txt) | Honored from early 2027; acts as a Google-Extended disallow when Google-Extended is not set | [F-AI-07](current-facts.md#f-ai-07) |

```html
<!-- Page-level: keep the page in Search but out of AI Overviews and AI Mode input -->
<meta name="robots" content="nosnippet">
<!-- Element-level: keep one block out of snippets and AI input -->
<div data-nosnippet>Member-only pricing details</div>
```

```text
X-Robots-Tag: max-snippet:50
```

- Snippet controls also reduce classic snippets ([AI010](rule-catalog.md#ai010)); they are an owner decision.
- The Search Console setting takes effect after it goes live and child properties can override parents ([F-AI-47](current-facts.md#f-ai-47)). It is an owner action in Search Console; nothing in the repository replaces it.
- Preferred sources badges in AI Mode and AI Overviews require the site to be included through that setting ([F-AI-14](current-facts.md#f-ai-14)).
- The UK CMA requires Google to provide effective publisher opt-outs from AI search features within nine months of 2026-06-03 ([F-AI-15](current-facts.md#f-ai-15)); finer-grained controls reported for 2026 and 2027 are third-party only.

## Verification

- A user-agent string is a claim, not an identity. Count claimed hits with `SG referrers access.log --log --bots`; every count is labelled "claimed (unverified)".
- Verify with the vendor's published IP list (token table) or reverse DNS followed by a forward lookup (Apple `*.applebot.apple.com`, Common Crawl `*.crawl.commoncrawl.org`, Google's documented crawler hostnames). Meta publishes no IP ranges for its crawlers ([F-AI-36](current-facts.md#f-ai-36)).
- Web Bot Auth lets agents sign requests with HTTP Message Signatures; it is an IETF working-group draft, not an RFC ([F-AI-34](current-facts.md#f-ai-34)). Google-Agent takes part in an experiment with the identity `https://agent.bot.goog` ([F-AI-08](current-facts.md#f-ai-08)). Verification happens at the edge (CDN or WAF), not in robots.txt.
- Allowlist verified bots by IP list or signature, never by user-agent string. A WAF that challenges an unverified request claiming to be GPTBot is behaving correctly.
- This plugin never sends requests that impersonate AI crawlers. A manual owner-run check of how the WAF treats a crawler is out of scope for the CLI.

## CDN and WAF overrides

What the repository contains is not always what crawlers receive.

- Cloudflare changed its default to block AI crawlers on 2025-07-01, and for new domains onboarding from 2026-09-15 blocks the Training and Agent categories on pages that display ads; mixed-use crawlers such as Googlebot, Applebot and Bingbot get the strictest applicable rule ([F-AI-23](current-facts.md#f-ai-23)). An owner who blocks "Training" there can block Googlebot.
- Cloudflare's managed robots.txt can inject rules at the edge that never appear in the origin file; its documented example disallows Amazonbot, Applebot-Extended, Bytespider, CCBot, ClaudeBot, Google-Extended, GPTBot and meta-externalagent ([F-AI-49](current-facts.md#f-ai-49)). `SG access-check <origin> --live` reports a managed block as [AI009](rule-catalog.md#ai009).
- Pay Per Crawl is still a private beta using HTTP 402 and Web Bot Auth ([F-AI-24](current-facts.md#f-ai-24)).
- Other edge layers (WAF bot rules, Workers, transform rules, cache variants, other CDNs) can block a user agent before it reaches robots.txt or serve different files per host. Compare the served `/robots.txt` with the repository copy, check the bot settings with the owner, and confirm behavior in logs before concluding the published file is the effective policy.
- A robots.txt that returns 5xx or is unreachable is treated as a full disallow by compliant crawlers ([AI015](rule-catalog.md#ai015)).
- Keep CAPTCHAs and challenge pages off content pages for verified crawlers the owner wants to allow.

Dashboard changes are user-operated: write numbered steps naming the service, the zone and the setting as the owner sees it, and say that labels change over time.

## Rule map

| Rule | Meaning | Usual fix |
| --- | --- | --- |
| [AI001](rule-catalog.md#ai001) | AI search or answer indexer blocked by a named group | Confirm with the owner; allow it if visibility is wanted |
| [AI002](rule-catalog.md#ai002) | Training-only crawler blocked | Informational: no search impact |
| [AI003](rule-catalog.md#ai003) | Rule targets a user fetcher that may ignore robots.txt | Use authentication or WAF rules for anything that must stay private |
| [AI004](rule-catalog.md#ai004) | Googlebot or bingbot blocked | Unblock unless the owner wants the site out of search |
| [AI005](rule-catalog.md#ai005) | Malformed Content-Signal or unknown key | Use `search`, `ai-input`, `ai-train` with `yes` or `no` |
| [AI006](rule-catalog.md#ai006) | Named group lacks the `*` group's Content-Signal | Repeat the line in every group |
| [AI007](rule-catalog.md#ai007) | Shared training token present | Informational: explain scope and dates |
| [AI008](rule-catalog.md#ai008) | `*` rule assumed to express a training preference | Add an explicit `__usage_ai-training` group and vendor groups |
| [AI009](rule-catalog.md#ai009) | Cloudflare-managed block detected | Owner reviews the Cloudflare setting |
| [AI010](rule-catalog.md#ai010) | Snippet controls limit AI Overviews and AI Mode input | Confirm it is intended |
| [AI011](rule-catalog.md#ai011) | noarchive or nocache used as an AI control | Move to the Bingbot directives or the Search Console setting |
| [AI012](rule-catalog.md#ai012) | Bingbot ai-training or ai-grounding directive | Informational: honored from 2027-02-01 |
| [AI013](rule-catalog.md#ai013) | Edge Content-Signal header contradicts robots.txt | Align the header with the owner's policy |
| [AI014](rule-catalog.md#ai014) | AI search indexer blocked only through `*` | Name the indexer and record the decision |
| [AI015](rule-catalog.md#ai015) | robots.txt returns 5xx or is unreachable | Fix the server or CDN response |
| [CRAWL004](rule-catalog.md#crawl004) | All crawlers disallowed from the whole site | Remove unless the site must be hidden from everything |
| [CRAWL008](rule-catalog.md#crawl008) | Page is noindex but disallowed | Allow crawling so the noindex can be seen |

## Re-check dates

| Date | What changes | Facts |
| --- | --- | --- |
| 2026-12-15 | Bing temporary grounding preferences open in Bing Webmaster Tools | [F-AI-19](current-facts.md#f-ai-19) |
| 2027-02-01 | Bing honors `ai-training`, `ai-grounding` and `__usage_ai-training` | [F-AI-18](current-facts.md#f-ai-18), [F-AI-19](current-facts.md#f-ai-19) |
| 2027-03-01 | Bing stops reading NOARCHIVE and NOCACHE as AI signals | [F-AI-19](current-facts.md#f-ai-19) |
| Early 2027 | Google honors `__usage_ai-training` | [F-AI-07](current-facts.md#f-ai-07) |
| About March 2027 | UK CMA deadline for Google's publisher AI controls | [F-AI-15](current-facts.md#f-ai-15) |
| 2027-09-30 | Bing temporary preferences expire | [F-AI-19](current-facts.md#f-ai-19) |

Reports that depend on these facts print the relevant dates. Re-verify every row against the vendor URL before relying on it after a re-check date.

## Needs verification

- OpenAI's support for `__usage_ai-training` and its timing (snippet only), and ChatGPT agent's request signatures.
- Bytespider, `cohere-ai` and `cohere-training-data-crawler`: purposes and robots.txt compliance are third-party and conflicting.
- Legacy Anthropic tokens `anthropic-ai` and `Claude-Web`.
- Bingbot verification method and Bing's crawl-delay handling.
- The Cloudflare managed-block marker text and current dashboard labels.
- Perplexity "stealth crawling" claims: third-party coverage of a dispute; do not assert either side.
- Which referrer each AI app sends (see [measurement-protocol.md](measurement-protocol.md)).
